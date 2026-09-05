"""Falsification harness: the texture floors must not reject ensemble writing.

Every threshold in `voicing.py` was measured on PIANO corpora — Mozart sonatas,
Beethoven sonatas, Chopin mazurkas, all keyboard. Ensemble writing has different
texture statistics by nature rather than by quality, and the piano floors
rejected it badly. Measured over 59 real multi-part (4+ voice) movements in
`reference_scores/_fetch_*`:

    the hand-span check fired at all      — there are no hands in an ensemble
    "only N registers are used"      23%  — each instrument covers a narrow one
    "the left hand averages 1.0/bar" 14%  — a cello plays one line; that is what it is
    simultaneity CV below the floor  47%  — sustained scoring holds a part count

The last is the sharpest: the measured 5th percentile of ensemble simultaneity CV
is **0.000**, so no floor above zero exists that does not reject real music. A
first attempt set it to 0.06 by eye and still rejected a quarter of them —
setting a threshold by judgement and measuring afterwards is the error this
harness exists to prevent.

After: **47% → 2%**, with keyboard behaviour unchanged.

Marked ``calibration``: needs the acquired sources and music21.
"""

import glob

import pytest

from scales.counterpoint import analyze_counterpoint
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR
from scales.voicing import analyze_voicing

pytestmark = pytest.mark.calibration

_MIN_PARTS = 4
_MAX_COMPLAINT_RATE = 0.15


def _ensemble_movements(max_bars=48, limit=40):
    import music21 as m21

    paths = sorted(glob.glob("tools/reference_scores/_fetch_*/*.mid"))
    if not paths:
        pytest.skip("acquired sources not present")
    out = []
    for path in paths:
        if len(out) >= limit:
            break
        try:
            score = m21.converter.parse(path)
        except Exception:
            continue
        parts = list(score.parts)
        if len(parts) < _MIN_PARTS:
            continue
        ts = score.recurse().getElementsByClass(m21.meter.TimeSignature)
        meter = (ts[0].numerator, ts[0].denominator) if ts else (4, 4)
        key = score.analyze("key")
        ir = LayerIR(
            key=f"{key.tonic.name} {key.mode}",
            meter=meter,
            instrumentation="ensemble",
        )
        targets = [ir.principal_line, ir.counter_reply, ir.response_layer, ir.bass_foundation]
        for pi, part in enumerate(parts):
            tgt = (
                targets[0]
                if pi == 0
                else targets[3]
                if pi == len(parts) - 1
                else targets[1 + (pi % 2)]
            )
            for m in part.getElementsByClass("Measure"):
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
        for t in targets:
            t.sort(key=lambda e: (e.bar, e.beat))
        ir.bar_count = len({e.bar for e in ir.principal_line}) or 1
        if ir.principal_line and ir.bar_count >= 8:
            out.append((path, ir))
    if len(out) < 8:
        pytest.skip("not enough multi-part movements parsed")
    return out


def test_ensemble_writing_draws_almost_no_texture_complaints():
    movements = _ensemble_movements()
    complained, offenders = 0, []
    for path, ir in movements:
        suggestions = analyze_voicing(ir, style="romantic").suggestions
        if suggestions:
            complained += 1
            offenders.append((path.split("/")[-1][:28], suggestions[0][:60]))
    rate = complained / len(movements)
    assert rate <= _MAX_COMPLAINT_RATE, (
        f"{complained} of {len(movements)} real multi-part movements draw a "
        f"texture complaint ({rate:.0%}) — the floors are piano-specific. "
        f"Examples: {offenders[:3]}"
    )


def test_the_hand_span_check_does_not_run_on_an_ensemble():
    """Two "hands" in an ensemble are two players; a wide gap is scoring."""
    for _path, ir in _ensemble_movements(limit=12):
        assert analyze_voicing(ir).unplayable_spans == [], _path


def test_part_writing_finds_no_errors_in_real_ensemble_music():
    """The counterpoint detectors were calibrated on keyboard too."""
    errors = sum(
        analyze_counterpoint(ir, key=ir.key).error_count
        for _path, ir in _ensemble_movements(limit=20)
    )
    assert errors == 0, f"{errors} part-writing errors reported in real ensemble writing"


def test_keyboard_floors_are_still_the_strict_ones():
    """Relaxing for ensembles must not relax the keyboard case."""
    from scales.voicing import floors_for

    piano = LayerIR(instrumentation="solo_piano")
    ensemble = LayerIR(instrumentation="ensemble")
    strict = floors_for("mozart", piano)
    loose = floors_for("mozart", ensemble)
    assert strict["simultaneity_cv"] > loose["simultaneity_cv"]
    assert strict["registers_used"] > loose["registers_used"]
    assert strict["register_span"] > loose["register_span"]
