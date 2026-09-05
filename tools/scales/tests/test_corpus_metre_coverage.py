"""Falsification harness: the musicality bands across METRES, not just 4/4.

`test_corpus_musicality_bands` falsified these bands against Mozart sonatas,
Beethoven sonatas and Chopin mazurkas. That corpus is keyboard, and it is 4/4
and 3/4. Measuring what the armed corpus actually holds shows how narrow a
sample that was:

    palestrina   5,766 of 6,000 sampled bars in 4/2 — NOT ONE in 4/4
    beethoven    top three metres are 3/4, 2/4, 2/2 — no 4/4 among them
    chopin       82% 3/4
    brahms       3/4, 6/8, 2/4 — no 4/4
    bruckner     2/2 only        mussorgsky  2/2 only
    dvorak       6/8 only        bartok      2/4 only

Any threshold expressed PER BAR is metre-dependent by construction: a 2/4 bar
is half the length of a 4/4 bar and holds half the events, and a 4/2 bar holds
twice as many. A band calibrated on 4/4 keyboard music and then applied to a
Palestrina motet or a Brahms 6/8 intermezzo is measuring the metre as much as
the music.

So this harness asks the falsification question for each metre SEPARATELY: does
this band score real music written in this metre differently from real music
written in any other? A band fine in aggregate can still reject one metre
whole, and the aggregate median hides it.

**The hypothesis that prompted this test was refuted, and the measurement is
worth keeping for that reason.** Median score by metre, over 78 real movements:

                                 2/2      3/2      3/4      4/4
    rest_ratio                  1.00     1.00     1.00     1.00
    direction_changes_per_bar   1.00     0.99     1.00     0.96
    rhythmic_variety            0.52     0.56     0.59     0.55
    melodic_smoothness          0.60     0.68     0.48     0.62

`rest_ratio` and `direction_changes_per_bar` are flat across every metre — the
per-bar normalisation these use is doing its job, and the concern was
unfounded. `rhythmic_variety` sits near 0.55 in EVERY metre **including 4/4**,
so that is not metre-dependence either: these movements come from MIDI, which
quantises durations and genuinely lowers rhythmic entropy. Lowering the band to
chase it would be calibrating to the source format rather than to music.

What the tests below pin is therefore the SPREAD across metres, not an absolute
floor. A band that tracks the metre shows a large gap between metres; one that
measures the writing does not. That is the sharper question, and an absolute
floor would have failed here for a reason that has nothing to do with metre.

Marked ``calibration``: needs the acquired sources and music21.
"""

import collections
import glob
import statistics

import pytest

from scales import musicality as M
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR

pytestmark = pytest.mark.calibration

#: The largest permitted gap between the best-scoring metre and the worst.
#: Observed spreads: rest_ratio 0.00, direction_changes 0.04, rhythmic_variety
#: 0.07, melodic_smoothness 0.20. Set above the observed maximum, so this fires
#: on a band that genuinely tracks bar length rather than on sampling noise.
_MAX_SPREAD_ACROSS_METRES = 0.30
#: Below the observed minimum (0.48) — a floor low enough that only a band
#: rejecting a metre outright trips it.
_MIN_MEDIAN_PER_METRE = 0.40
#: A band may not put more than this share of one metre's real movements at the
#: bottom of its range.
_MAX_POOR_SHARE = 0.5
_POOR = 0.3


def _movements_by_metre(max_bars=64, limit=90):
    """Real movements grouped by their own time signature."""
    import music21 as m21

    paths = sorted(glob.glob("tools/reference_scores/_fetch_*/*.mid"))
    if not paths:
        pytest.skip("acquired sources not present")
    by_metre = collections.defaultdict(list)
    seen = 0
    for path in paths:
        if seen >= limit:
            break
        try:
            score = m21.converter.parse(path)
        except Exception:
            continue
        parts = list(score.parts)
        if not parts:
            continue
        ts = score.recurse().getElementsByClass(m21.meter.TimeSignature)
        if not ts:
            continue
        meter = (ts[0].numerator, ts[0].denominator)
        ir = LayerIR(key="C", meter=meter)
        for pi, pt in enumerate(parts[:2]):
            tgt = ir.principal_line if pi == 0 else ir.bass_foundation
            for m in pt.getElementsByClass("Measure"):
                if m.number is None or m.number > max_bars:
                    continue
                for v in list(m.voices) or [m]:
                    for n in v.notesAndRests:
                        try:
                            d = beats_to_dur(n.duration.quarterLength)
                        except Exception:
                            d = "q"
                        pitch = (
                            "rest"
                            if n.isRest
                            else [x.nameWithOctave for x in n.pitches]
                            if n.isChord
                            else n.nameWithOctave
                        )
                        tgt.append(
                            LayerEvent(
                                bar=m.number, beat=1.0 + float(n.offset), pitch=pitch, duration=d
                            )
                        )
        ir.bar_count = len({e.bar for e in ir.principal_line}) or 1
        if len(ir.principal_line) > 40 and ir.bar_count >= 8:
            by_metre[meter].append(ir)
            seen += 1
    live = {k: v for k, v in by_metre.items() if len(v) >= 5}
    if len(live) < 3:
        pytest.skip("not enough metres represented")
    return live


_SCORERS = {
    "rest_ratio": M.rest_ratio,
    "direction_changes_per_bar": M.direction_changes_per_bar,
    "rhythmic_variety": M.rhythmic_variety,
    "melodic_smoothness": M.melodic_smoothness,
}


def test_no_band_scores_one_metre_differently_from_another():
    """The real question. A band that tracks bar length is measuring the metre.

    This is the assertion the absolute floor should have been: `rhythmic_variety`
    sits at 0.55 in every metre including 4/4, so a floor of 0.6 flagged it for
    a reason that has nothing to do with metre, while its spread of 0.07 says
    plainly that the band is metre-independent.
    """
    by_metre = _movements_by_metre()
    offenders = []
    for name, fn in _SCORERS.items():
        meds = {
            meter: statistics.median([fn(ir)[0] for ir in layers])
            for meter, layers in by_metre.items()
        }
        spread = max(meds.values()) - min(meds.values())
        if spread > _MAX_SPREAD_ACROSS_METRES:
            hi = max(meds, key=meds.get)
            lo = min(meds, key=meds.get)
            offenders.append(
                f"{name} spans {spread:.2f} across metres — {hi[0]}/{hi[1]} scores "
                f"{meds[hi]:.2f} and {lo[0]}/{lo[1]} scores {meds[lo]:.2f}"
            )
    assert not offenders, (
        "a band scores real music differently depending only on its metre:\n  "
        + "\n  ".join(offenders)
    )


def test_no_band_rejects_an_entire_metre():
    """The aggregate median can be healthy while one metre is rejected whole."""
    by_metre = _movements_by_metre()
    offenders = []
    for name, fn in _SCORERS.items():
        for meter, layers in sorted(by_metre.items()):
            scores = [fn(ir)[0] for ir in layers]
            med = statistics.median(scores)
            if med < _MIN_MEDIAN_PER_METRE:
                offenders.append(
                    f"{name} scores real {meter[0]}/{meter[1]} music at a median of "
                    f"{med:.2f} over {len(scores)} movements"
                )
    assert not offenders, "a band rejects a whole metre of real music:\n  " + "\n  ".join(offenders)


def test_no_band_puts_half_of_one_metre_at_the_bottom_of_its_range():
    by_metre = _movements_by_metre()
    offenders = []
    for name, fn in _SCORERS.items():
        for meter, layers in sorted(by_metre.items()):
            scores = [fn(ir)[0] for ir in layers]
            poor = sum(1 for s in scores if s < _POOR) / len(scores)
            if poor > _MAX_POOR_SHARE:
                offenders.append(
                    f"{name}: {poor:.0%} of real {meter[0]}/{meter[1]} movements score below {_POOR}"
                )
    assert not offenders, "\n  ".join(offenders)


def test_the_corpus_really_does_span_metres():
    """Guards the harness itself: a sample that is all 4/4 proves nothing.

    Two harnesses earlier in this session returned degenerate results that
    looked like findings — a monotone drone from wrong key names, and a metric
    saturated at exactly 1.00 in every metre. A harness gets its own assertion.
    """
    by_metre = _movements_by_metre()
    assert len(by_metre) >= 3, f"only {len(by_metre)} metres represented"
    assert any(m != (4, 4) for m in by_metre), "every sampled movement is in 4/4"
    for meter, layers in by_metre.items():
        assert all(ir.meter == meter for ir in layers)
        assert all(len(ir.principal_line) > 40 for ir in layers)
