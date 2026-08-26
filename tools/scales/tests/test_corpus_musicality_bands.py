"""Falsification harness: musicality scores must not penalize real music.

``musicality.py`` returns 0-1 scores that feed ``self_evaluate``, which the
fresh-ears critic reads. A band that real music sits outside teaches the
composer to write something no one has written. Three bands did exactly that
before this test existed, measured over 20 real movements on 2026-08-26:

* ``rest_ratio`` scored 1.0 only inside 3-15% rest time. Real music's **median
  is 16.3%** — outside the band — so typical writing was marked down for
  breathing a normal amount.
* ``direction_changes_per_bar`` scored 1.0 only inside 1.0-2.0 per bar. Real
  music's **median is 2.05**, right at the edge, and the most active movement
  measured (6.97) scored **0.3**.
* ``rhythmic_variety`` normalized entropy by 3 bits when the richest real
  movement reaches **2.69**, so a full score was literally unreachable and the
  median real movement scored 0.65.

Marked ``calibration``: needs the score corpus and music21.
"""

import glob
import statistics

import pytest

from scales import musicality as M
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR

pytestmark = pytest.mark.calibration

# Real music should score well on a well-calibrated band. These floors are
# deliberately below the measured medians so a band may be *stricter* than the
# median without failing — but not so strict that the repertoire scores badly.
_MIN_MEDIAN_SCORE = {
    "rest_ratio": 0.9,
    "direction_changes_per_bar": 0.9,
    "rhythmic_variety": 0.6,
    "melodic_smoothness": 0.4,
}


def _real_layers():
    import music21 as m21

    paths = (
        sorted(glob.glob("tools/reference_scores/mozart-piano-sonatas/kern/sonata0[1-9]-*.krn"))[:10]
        + sorted(glob.glob("tools/reference_scores/beethoven-piano-sonatas/**/*.krn", recursive=True))[:5]
        + sorted(glob.glob("tools/reference_scores/chopin-mazurkas/**/*.krn", recursive=True))[:5]
    )
    if not paths:
        pytest.skip("score corpus not present")
    out = []
    for path in paths:
        try:
            s = m21.converter.parse(path)
        except Exception:
            continue
        parts = list(s.parts)
        if len(parts) < 2:
            continue
        ts = s.recurse().getElementsByClass(m21.meter.TimeSignature)
        meter = (ts[0].numerator, ts[0].denominator) if ts else (4, 4)
        ir = LayerIR(key="C", meter=meter)
        for pi, pt in enumerate(parts[:2]):
            main = ir.principal_line if pi == 0 else ir.bass_foundation
            second = ir.counter_reply if pi == 0 else ir.response_layer
            for m in pt.getElementsByClass("Measure"):
                if m.number is None or m.number > 64:
                    continue
                for vi, v in enumerate(list(m.voices) or [m]):
                    tgt = main if vi == 0 else second
                    for n in v.notesAndRests:
                        try:
                            d = beats_to_dur(n.duration.quarterLength)
                        except Exception:
                            d = "q"
                        if n.isRest:
                            pitch = "rest"
                        else:
                            pitch = (
                                [x.nameWithOctave for x in n.pitches]
                                if n.isChord
                                else n.nameWithOctave
                            )
                        tgt.append(
                            LayerEvent(
                                bar=m.number, beat=1.0 + float(n.offset), pitch=pitch, duration=d
                            )
                        )
        ir.bar_count = len({e.bar for e in ir.principal_line}) or 1
        if ir.principal_line:
            out.append(ir)
    if len(out) < 8:
        pytest.skip("not enough real movements parsed")
    return out


def test_real_music_scores_well_on_every_calibrated_band():
    layers = _real_layers()
    scorers = {
        "rest_ratio": M.rest_ratio,
        "direction_changes_per_bar": M.direction_changes_per_bar,
        "rhythmic_variety": M.rhythmic_variety,
        "melodic_smoothness": M.melodic_smoothness,
    }
    offenders = []
    for name, fn in scorers.items():
        scores = sorted(fn(ir)[0] for ir in layers)
        med = statistics.median(scores)
        floor = _MIN_MEDIAN_SCORE[name]
        if med < floor:
            offenders.append(
                f"{name}: real music's median score is {med:.2f} (floor {floor}) — "
                f"the band excludes the repertoire, range {min(scores):.2f}-{max(scores):.2f}"
            )
    assert not offenders, "\n".join(offenders)


def test_a_full_score_is_reachable_by_real_music():
    """A ceiling no real movement can reach is a mis-set normalizer."""
    layers = _real_layers()
    best = max(M.rhythmic_variety(ir)[0] for ir in layers)
    assert best > 0.95, (
        f"the richest real movement scores only {best:.2f} for rhythmic variety — "
        f"the entropy normalizer is set above the repertoire's own ceiling"
    )


def test_the_density_fallback_is_not_busier_than_real_music():
    layers = _real_layers()
    rh = statistics.median(M.events_per_bar(ir, "rh") for ir in layers)
    _score, detail = M.figuration_richness(layers[0], hand="rh")
    assert detail["corpus_median"] <= rh * 1.25, (
        f"fallback median {detail['corpus_median']} is well above the real "
        f"right-hand median of {rh:.2f} events per bar"
    )


def test_the_interval_priors_match_the_repertoire():
    """These were 65/25/10 by guess and measured 65/24/11 — left as they were."""
    layers = _real_layers()
    got = {"stepwise": [], "small_leap": [], "large_leap": []}
    for ir in layers:
        _s, d = M.melodic_interval_profile(ir)
        for k, v in (d.get("actual") or {}).items():
            got[k].append(v)
    for k, vals in got.items():
        if not vals:
            continue
        med = statistics.median(vals)
        prior = M.melodic_interval_profile(layers[0])[1]["priors"][k]
        assert abs(med - prior) < 0.15, (
            f"interval prior for {k} is {prior} but real music measures {med:.3f}"
        )
