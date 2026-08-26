"""Falsification harness: the craft checklist must not fail real music.

Before calibration, over 126 real 8-bar phrases (Mozart, Beethoven, Chopin):
``has_memorable_detail`` passed **0 of 126**, ``accompaniment_responds_to_melody``
31%, ``harmony_is_voiced`` 56%. A checklist canonical music cannot satisfy does
not raise standards — it teaches the composer to write toward whatever artefact
the check is really measuring, which in three of these four cases was "which
layer did the shorthand happen to file this note under".

Marked ``calibration``: needs the score corpus and music21.
"""

import collections
import glob

import pytest

from scales.craft_checker import CraftChecker
from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR

pytestmark = pytest.mark.calibration

# Every check must pass the large majority of real phrases. The two set at 0.85
# are genuinely variable in the repertoire (a phrase can legitimately have no
# rest, and a melody can legitimately sit inside a third), so they are not held
# to the same bar as the structural checks.
_MIN_PASS_RATE = {
    "melodic_claim_clear": 0.85,
    "rhythm_has_identity": 0.85,
    "bass_has_purpose": 0.90,
    "harmony_is_voiced": 0.90,
    "has_breath_point": 0.85,
    "accompaniment_responds_to_melody": 0.90,
    "entry_exit_earned": 0.90,
    "has_memorable_detail": 0.90,
}

_PHRASE_BARS = 8
_MAX_BARS = 64


def _real_phrases():
    import music21 as m21

    paths = (
        sorted(glob.glob("tools/reference_scores/mozart-piano-sonatas/kern/sonata0[1-6]-*.krn"))[:8]
        + sorted(glob.glob("tools/reference_scores/beethoven-piano-sonatas/**/*.krn", recursive=True))[:4]
        + sorted(glob.glob("tools/reference_scores/chopin-mazurkas/**/*.krn", recursive=True))[:4]
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
        by_bar = {}
        for pi, pt in enumerate(parts[:2]):
            for m in pt.getElementsByClass("Measure"):
                if m.number is None or m.number > _MAX_BARS:
                    continue
                for vi, v in enumerate(list(m.voices) or [m]):
                    layer = (
                        ("principal_line" if vi == 0 else "counter_reply")
                        if pi == 0
                        else ("bass_foundation" if vi == 0 else "response_layer")
                    )
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
                        by_bar.setdefault(m.number, []).append(
                            (
                                layer,
                                LayerEvent(
                                    bar=m.number,
                                    beat=1.0 + float(n.offset),
                                    pitch=pitch,
                                    duration=d,
                                ),
                            )
                        )
        bars = sorted(by_bar)
        for i in range(0, len(bars), _PHRASE_BARS):
            chunk = bars[i : i + _PHRASE_BARS]
            if len(chunk) < _PHRASE_BARS:
                break
            ir = LayerIR(key="C", meter=meter, bar_count=len(chunk))
            for b in chunk:
                for layer, ev in by_bar[b]:
                    getattr(ir, layer).append(ev)
            for layer in (
                "principal_line",
                "bass_foundation",
                "response_layer",
                "counter_reply",
            ):
                getattr(ir, layer).sort(key=lambda e: (e.bar, e.beat))
            out.append(ir)
    if len(out) < 40:
        pytest.skip("not enough real phrases parsed")
    return out


def test_the_craft_checklist_passes_real_music():
    phrases = _real_phrases()
    checker = CraftChecker()
    passes = collections.Counter()
    for ir in phrases:
        chk = checker.check(ir)
        for name, value in vars(chk).items():
            if isinstance(value, bool) and value:
                passes[name] += 1

    n = len(phrases)
    offenders = []
    for name, floor in _MIN_PASS_RATE.items():
        rate = passes[name] / n
        if rate < floor:
            offenders.append(
                f"{name}: passes only {rate:.1%} of {n} real phrases (floor {floor:.0%})"
            )
    assert not offenders, (
        "these craft checks reject canonical music:\n" + "\n".join(offenders)
    )


def test_the_checklist_still_rejects_empty_music():
    """Loosening a check must not turn it into a rubber stamp."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=4)
    for b in range(1, 5):
        for i in range(4):
            ir.principal_line.append(
                LayerEvent(bar=b, beat=1 + i, pitch="C5", duration="q")
            )
    chk = CraftChecker().check(ir)
    failed = [k for k, v in vars(chk).items() if isinstance(v, bool) and not v]
    assert len(failed) >= 5, f"a one-note phrase failed only {failed}"
