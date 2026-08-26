"""Falsification harness: the cadence reader must read real cadences.

A cadence detector that reports "no cadence" at the end of a real sonata
movement is not detecting cadences, it is detecting nothing. Measured on 15 real
movements (Mozart, Beethoven, Chopin), every final bar reads as an authentic or
plagal cadence and none as NONE.

Marked ``calibration`` because it needs the score corpus. Run with
``pytest -m calibration``.
"""

import glob

import pytest

from scales.cadence_analysis import read_cadence
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR

pytestmark = pytest.mark.calibration

_CLOSING = {"PAC", "IAC", "PLAGAL", "DC"}


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


def _load(path):
    import music21 as m21

    s = m21.converter.parse(path)
    parts = list(s.parts)
    if len(parts) < 2:
        return None, None
    k = s.analyze("key")
    keystr = f"{k.tonic.name} {k.mode}"
    ts = s.recurse().getElementsByClass(m21.meter.TimeSignature)
    meter = (ts[0].numerator, ts[0].denominator) if ts else (4, 4)
    ir = LayerIR(key=keystr, meter=meter)
    for pi, pt in enumerate(parts[:2]):
        main = ir.principal_line if pi == 0 else ir.bass_foundation
        second = ir.counter_reply if pi == 0 else ir.response_layer
        for m in pt.getElementsByClass("Measure"):
            if m.number is None:
                continue
            for vi, v in enumerate(list(m.voices) or [m]):
                tgt = main if vi == 0 else second
                for n in v.notes:
                    try:
                        d = beats_to_dur(n.duration.quarterLength)
                    except Exception:
                        d = "q"
                    p = [x.nameWithOctave for x in n.pitches] if n.isChord else n.nameWithOctave
                    tgt.append(
                        LayerEvent(bar=m.number, beat=1.0 + float(n.offset), pitch=p, duration=d)
                    )
    return ir, keystr


def test_every_real_movement_ends_with_a_readable_cadence():
    missed, read = [], 0
    for path in _real_scores():
        ir, key = _load(path)
        if ir is None or not ir.principal_line:
            continue
        last = max(e.bar for e in ir.principal_line)
        cad = read_cadence(ir, cadence_bar=last, key=key, is_final=True)
        read += 1
        if cad is None or cad.kind not in _CLOSING:
            missed.append(f"{path.split('/')[-1]}: {cad.kind if cad else 'unreadable'}")
    assert read >= 10, "not enough real movements loaded to draw a conclusion"
    assert not missed, "these real endings did not read as cadences:\n" + "\n".join(missed)


def test_real_cadences_are_not_all_the_same_kind():
    """A reader that answers PAC for everything would also pass the test above."""
    kinds = set()
    for path in _real_scores():
        ir, key = _load(path)
        if ir is None or not ir.principal_line:
            continue
        last = max(e.bar for e in ir.principal_line)
        cad = read_cadence(ir, cadence_bar=last, key=key, is_final=True)
        if cad:
            kinds.add(cad.kind)
    assert len(kinds) >= 2, f"every real ending read the same: {kinds}"
