"""Falsification harness: the texture measurements must describe real music.

Two faults this harness exists to prevent, both found by running the checks over
the repertoire rather than by reasoning about them:

* **The hand-span check counted everything *sounding* together.** A bass note
  held under a chord the hand plays higher up is the ordinary pedal-point idiom,
  released by the fingers and held by the pedal. Counting it as a reach produced
  **211 "unplayable" stretches across 1,027 real bars**, with a median widest
  span of 28 semitones — an octave and a half, which no hand spans and every
  pianist plays.
* **`_hand_of` stripped only the `#` suffix, not `@`.** The voice namer produces
  both `principal_line#1` (a chord member) and `principal_line@1` (an
  overlapping strand), so every strand of a melody overlapping itself — most
  sustained melodic writing — was counted as a left-hand note.

Marked ``calibration``: needs the score corpus and music21.
"""

import glob
import statistics

import pytest

from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR
from scales.voicing import analyze_voicing

pytestmark = pytest.mark.calibration

# The suggestion floors are set outside the repertoire's range, so real music
# should draw essentially no texture complaints.
_MAX_SUGGESTION_RATE = 0.25
# Simultaneous attacks beyond a hand's reach, per bar, in real music. A two-staff
# score cannot say which hand plays a cross-staff note and a rolled chord is
# notated as a simultaneity, so this is never zero — but it must stay rare.
_MAX_STRETCH_RATE = 0.02  # measured: 15 stretches over 1,027 real bars


def _real_layers():
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
        ir = LayerIR(key="C", meter=meter)
        for pi, pt in enumerate(parts[:2]):
            main = ir.principal_line if pi == 0 else ir.bass_foundation
            second = ir.counter_reply if pi == 0 else ir.response_layer
            for m in pt.getElementsByClass("Measure"):
                if m.number is None or m.number > 64:
                    continue
                for vi, v in enumerate(list(m.voices) or [m]):
                    tgt = main if vi == 0 else second
                    for n in v.notes:
                        try:
                            d = beats_to_dur(n.duration.quarterLength)
                        except Exception:
                            d = "q"
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
        if ir.principal_line:
            # Judge each movement against ITS OWN period. Applying the Classical
            # floor to a Chopin mazurka is the mistake the style-aware floors
            # exist to prevent, and doing it in the test made the test wrong
            # rather than the code — Chopin's simultaneity CV reaches 0.17 and
            # Mozart's never drops below 0.21, so one floor cannot serve both.
            style = (
                "chopin"
                if "chopin" in path
                else ("beethoven" if "beethoven" in path else "mozart")
            )
            out.append((path, ir, style))
    if len(out) < 8:
        pytest.skip("not enough real movements parsed")
    return out


def test_real_music_is_not_told_its_hands_cannot_reach():
    total_bars = total_flagged = 0
    worst = []
    for path, ir, style in _real_layers():
        rep = analyze_voicing(ir, style=style)
        total_bars += len(rep.bars)
        total_flagged += len(rep.unplayable_spans)
        if rep.unplayable_spans:
            worst.append((path.split("/")[-1], len(rep.unplayable_spans)))
    rate = total_flagged / max(1, total_bars)
    assert rate <= _MAX_STRETCH_RATE, (
        f"{total_flagged} stretches flagged across {total_bars} real bars "
        f"({rate:.3f}/bar). Worst: {sorted(worst, key=lambda x: -x[1])[:3]}"
    )


def test_real_music_draws_almost_no_texture_complaints():
    complained = 0
    layers = _real_layers()
    offenders = []
    for path, ir, style in layers:
        sugg = analyze_voicing(ir, style=style).suggestions
        # Cross-staff writing and rolled chords are indistinguishable from a
        # stretch in a two-staff score, so that one complaint is expected on
        # real music and is excluded here; the texture floors are not.
        sugg = [x for x in sugg if "exceed a hand" not in x]
        if sugg:
            complained += 1
            offenders.append((path.split("/")[-1], sugg[0][:80]))
    rate = complained / len(layers)
    assert rate <= _MAX_SUGGESTION_RATE, (
        f"{complained} of {len(layers)} real movements draw a texture complaint "
        f"({rate:.0%}) — the floors have drifted inside the repertoire. "
        f"Examples: {offenders[:3]}"
    )


def test_the_corpus_baselines_still_match_the_corpus():
    """`CORPUS_TEXTURE` is quoted to the composer; it has to stay true."""
    from scales.voicing import CORPUS_TEXTURE

    rh = statistics.median(
        analyze_voicing(ir).rh_notes_per_attack for _p, ir, _s in _real_layers()
    )
    classical = CORPUS_TEXTURE["classical"]["rh_notes_per_attack"]
    romantic = CORPUS_TEXTURE["romantic"]["rh_notes_per_attack"]
    assert min(classical, romantic) <= rh <= max(classical, romantic) * 1.3, (
        f"measured right-hand density {rh:.2f} is outside the range the "
        f"documented baselines describe ({classical}-{romantic})"
    )


def test_hands_are_assigned_correctly_in_real_scores():
    """A melody overlapping itself must not be counted as accompaniment."""
    for _path, ir, _style in _real_layers():
        rep = analyze_voicing(ir)
        assert rep.rh_notes_per_attack >= 1.0
        # Every real piano movement has both hands doing something.
        assert rep.lh_notes_per_attack >= 1.0
