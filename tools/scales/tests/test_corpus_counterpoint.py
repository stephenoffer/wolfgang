"""Falsification harness: the part-writing detectors must not reject the canon.

Marked ``calibration`` because it needs the score corpus and takes a minute. Run
it with ``pytest -m calibration``.

The standing rule in this project is that no check may block or warn at scale
until someone has asked "would this reject real canonical music?" and tested it.
When these detectors were first written the answer was an emphatic yes: 41
errors and 292 warnings across 770 bars of Mozart, Beethoven and Chopin, almost
all of them octave doublings read as parallel octaves and descending scales read
as unresolved leading tones. This test is what keeps that from coming back.
"""

import glob

import pytest

from scales.counterpoint import analyze_counterpoint
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR

pytestmark = pytest.mark.calibration

_MAX_BARS = 48
# Ceilings measured after calibration: 0 errors, 17 warnings over 770 bars.
# Headroom is deliberate — a detector drifting past these is a regression.
_MAX_ERRORS_PER_MOVEMENT = 0
_MAX_WARNS_PER_BAR = 0.05


def _real_scores():
    paths = (
        sorted(glob.glob("tools/reference_scores/mozart-piano-sonatas/kern/sonata0[1-6]-*.krn"))[:8]
        + sorted(
            glob.glob("tools/reference_scores/beethoven-piano-sonatas/**/*.krn", recursive=True)
        )[:4]
        + sorted(glob.glob("tools/reference_scores/chopin-mazurkas/**/*.krn", recursive=True))[:4]
    )
    if not paths:
        pytest.skip("score corpus not present")
    return paths


def _score_to_layer_ir(path):
    import music21 as m21

    s = m21.converter.parse(path)
    parts = list(s.parts)
    if len(parts) < 2:
        return None, None
    key = s.analyze("key")
    keystr = f"{key.tonic.name} {key.mode}"
    ts = s.recurse().getElementsByClass(m21.meter.TimeSignature)
    meter = (ts[0].numerator, ts[0].denominator) if ts else (4, 4)
    ir = LayerIR(phrase_id=path, key=keystr, meter=meter)
    for pi, pt in enumerate(parts[:2]):
        main = ir.principal_line if pi == 0 else ir.bass_foundation
        second = ir.counter_reply if pi == 0 else ir.response_layer
        for m in pt.getElementsByClass("Measure"):
            if m.number is None or m.number > _MAX_BARS:
                continue
            for vi, v in enumerate(list(m.voices) or [m]):
                tgt = main if vi == 0 else second
                for n in v.notes:
                    try:
                        dur = beats_to_dur(n.duration.quarterLength)
                    except Exception:
                        dur = "q"
                    p = [x.nameWithOctave for x in n.pitches] if n.isChord else n.nameWithOctave
                    tgt.append(
                        LayerEvent(bar=m.number, beat=1.0 + float(n.offset), pitch=p, duration=dur)
                    )
    return ir, keystr


def test_real_scores_produce_no_part_writing_errors():
    offenders = []
    total_bars = total_warns = 0
    for path in _real_scores():
        ir, key = _score_to_layer_ir(path)
        if ir is None:
            continue
        rep = analyze_counterpoint(ir, key=key)
        bars = len({e.bar for e in ir.principal_line}) or 1
        total_bars += bars
        total_warns += rep.warn_count
        if rep.error_count > _MAX_ERRORS_PER_MOVEMENT:
            offenders.append(f"{path.split('/')[-1]}: {rep.error_count} errors — {rep.by_kind()}")
    assert not offenders, "these detectors reject real music:\n" + "\n".join(offenders)
    assert total_bars > 0
    per_bar = total_warns / total_bars
    assert per_bar <= _MAX_WARNS_PER_BAR, (
        f"{total_warns} warnings over {total_bars} canonical bars "
        f"({per_bar:.3f}/bar) — the detectors have drifted back into "
        f"flagging normal writing"
    )
