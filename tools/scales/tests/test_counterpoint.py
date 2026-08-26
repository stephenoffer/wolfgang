"""Part-writing detectors, and the falsification that shaped them.

Every threshold in ``counterpoint.py`` was set by running the detectors over 770
bars of real Mozart, Beethoven and Chopin and tightening until canonical music
came back clean. The first version reported 41 errors and 292 warnings on that
material — a detector that rejects the repertoire is worse than none, because it
teaches the composer to write blander music.

The falsification run itself lives in ``test_corpus_counterpoint.py`` (marked
``calibration``, needs the score corpus). These are the unit-level pins.
"""

from fractions import Fraction

from scales.counterpoint import (
    analyze_counterpoint,
    attack_times,
    extract_voices,
    find_doubled_pairs,
    sounding_at,
    summarize_for_critic,
    voice_independence,
)
from scales.models import LayerEvent, LayerIR


def _ev(bar, beat, pitch, dur="q", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


# ─── Simultaneity ────────────────────────────────────────────────────────────


def test_a_sustained_note_still_sounds_under_a_later_attack():
    """The whole point: a suspension is invisible to onset-matching."""
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1.0, "C5", "w")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "q"), _ev(1, 2.0, "G3", "q")]
    spans = extract_voices(ir)
    at_beat_2 = sounding_at(spans, Fraction(1))
    assert len(at_beat_2) == 2, "the held C5 must still be sounding on beat 2"


def test_a_chord_becomes_ordered_voices_low_to_high():
    ir = LayerIR()
    ir.bass_foundation = [_ev(1, 1.0, ["C3", "E3", "G3"])]
    spans = extract_voices(ir)
    names = [s.voice for s in sorted(spans, key=lambda s: s.midi)]
    assert names == ["bass_foundation#0", "bass_foundation#1", "bass_foundation#2"]


def test_grace_notes_are_excluded_from_the_harmony():
    ir = LayerIR()
    ir.principal_line = [
        _ev(1, 1.0, "B4", "s", ornament="grace"),
        _ev(1, 1.0, "C5", "q"),
    ]
    spans = extract_voices(ir)
    assert len(spans) == 1


# ─── Doubling exemption ──────────────────────────────────────────────────────


def test_a_melody_doubled_in_octaves_is_recognised_as_one_line():
    ir = LayerIR(meter=(4, 4))
    tune = ["C5", "D5", "E5", "F5"]
    for i, p in enumerate(tune):
        ir.principal_line.append(_ev(1, 1 + i, p))
        ir.counter_reply.append(_ev(1, 1 + i, p.replace("5", "4")))
    pairs = find_doubled_pairs(extract_voices(ir))
    assert frozenset(("principal_line", "counter_reply")) in pairs


def test_octave_doubling_does_not_report_parallel_octaves():
    """This is the case that fired 217 times on real music."""
    ir = LayerIR(meter=(4, 4), key="C")
    for i, p in enumerate(["C5", "D5", "E5", "F5"]):
        ir.principal_line.append(_ev(1, 1 + i, p))
        ir.counter_reply.append(_ev(1, 1 + i, p.replace("5", "4")))
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("parallel_octaves", 0) == 0


def test_genuine_parallel_octaves_between_melody_and_bass_are_reported():
    ir = LayerIR(meter=(4, 4), key="C")
    # Two independent lines that only now collapse into octaves.
    ir.principal_line = [_ev(1, 1.0, "E5"), _ev(1, 2.0, "C5"), _ev(1, 3.0, "D5")]
    ir.bass_foundation = [_ev(1, 1.0, "G3"), _ev(1, 2.0, "C3"), _ev(1, 3.0, "D3")]
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("parallel_octaves", 0) >= 1


def test_parallel_fifths_between_outer_voices_are_reported():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "G4"), _ev(1, 2.0, "A4")]
    ir.bass_foundation = [_ev(1, 1.0, "C3"), _ev(1, 2.0, "D3")]
    rep = analyze_counterpoint(ir)
    assert "parallel_fifths" in rep.by_kind()


# ─── Leading tone ────────────────────────────────────────────────────────────


def test_a_descending_scale_through_the_leading_tone_is_not_flagged():
    """A descending scale contains a falling leading tone by definition."""
    ir = LayerIR(meter=(4, 4), key="C major")
    for i, p in enumerate(["C6", "B5", "A5", "G5"]):
        ir.principal_line.append(_ev(1, 1 + i, p))
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("leading_tone_falls", 0) == 0


def test_a_held_leading_tone_that_falls_is_noticed():
    ir = LayerIR(meter=(4, 4), key="C major")
    ir.principal_line = [
        _ev(1, 1.0, "G5", "q"),
        _ev(1, 2.0, "B5", "h"),  # leapt to and held — a structural dominant third
        _ev(1, 4.0, "A5", "q"),
    ]
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("leading_tone_falls", 0) == 1


def test_a_leading_tone_resolving_up_is_clean():
    ir = LayerIR(meter=(4, 4), key="C major")
    ir.principal_line = [_ev(1, 1.0, "G5"), _ev(1, 2.0, "B5", "h"), _ev(1, 4.0, "C6")]
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("leading_tone_falls", 0) == 0


# ─── Sevenths ────────────────────────────────────────────────────────────────


def test_a_passing_note_forming_a_seventh_is_not_an_unresolved_seventh():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "B-4", "q", role="passing"), _ev(1, 2.0, "C5")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "h")]
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("unresolved_seventh", 0) == 0


def test_a_real_chordal_seventh_that_leaps_away_is_reported():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "B-4", "h"), _ev(1, 3.0, "F5", "h")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "h"), _ev(1, 3.0, "F3", "h")]
    ir.counter_reply = [_ev(1, 1.0, "E4", "h"), _ev(1, 3.0, "A4", "h")]
    rep = analyze_counterpoint(ir)
    assert rep.by_kind().get("unresolved_seventh", 0) == 1


# ─── Texture descriptors ─────────────────────────────────────────────────────


def test_lockstep_voices_score_zero_independence():
    ir = LayerIR(meter=(4, 4))
    for i, p in enumerate(["C5", "D5", "E5", "F5"]):
        ir.principal_line.append(_ev(1, 1 + i, p))
        ir.bass_foundation.append(_ev(1, 1 + i, p.replace("5", "3")))
    assert voice_independence(extract_voices(ir)) == 0.0


def test_contrary_motion_scores_full_independence():
    ir = LayerIR(meter=(4, 4))
    for i, (a, b) in enumerate(zip(["C5", "D5", "E5"], ["E3", "D3", "C3"])):
        ir.principal_line.append(_ev(1, 1 + i, a))
        ir.bass_foundation.append(_ev(1, 1 + i, b))
    assert voice_independence(extract_voices(ir)) == 1.0


def test_a_stuck_inner_voice_is_reported():
    ir = LayerIR(meter=(4, 4), key="C")
    for b in (1, 2):
        for i in range(4):
            ir.response_layer.append(_ev(b, 1 + i, "G3"))
    rep = analyze_counterpoint(ir)
    assert "static_voice" in rep.by_kind()


def test_melody_buried_under_the_accompaniment_is_reported():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "C4", "h")]
    ir.bass_foundation = [_ev(1, 1.0, "G4", "h")]
    rep = analyze_counterpoint(ir)
    assert "voice_crossing" in rep.by_kind()


# ─── Contract ────────────────────────────────────────────────────────────────


def test_info_findings_are_kept_out_of_the_critics_summary():
    """A diagnostic must not become a revision target."""
    ir = LayerIR(meter=(4, 4), key="C")
    for b in (1, 2):
        for i in range(4):
            ir.response_layer.append(_ev(b, 1 + i, "G3"))
    rep = analyze_counterpoint(ir)
    assert any(f.severity == "info" for f in rep.findings)
    assert not any("static voice" in line for line in summarize_for_critic(rep))


def test_empty_input_is_safe():
    rep = analyze_counterpoint(LayerIR())
    assert rep.findings == []
    assert rep.attack_points == 0


def test_metadata_is_never_iterated_as_notes():
    ir = LayerIR(meter=(3, 4), key="a minor", bar_count=4)
    ir.principal_line = [_ev(1, 1.0, "A4")]
    analyze_counterpoint(ir)  # must not raise
    assert ir.meter == (3, 4)


def test_detectors_can_be_switched_off_individually():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "G4"), _ev(1, 2.0, "A4")]
    ir.bass_foundation = [_ev(1, 1.0, "C3"), _ev(1, 2.0, "D3")]
    rep = analyze_counterpoint(ir, enable={"parallels": False})
    assert "parallel_fifths" not in rep.by_kind()


def test_attack_times_are_exact_under_triplets():
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1 + i / 3, "C5", "trip_e") for i in range(3)]
    ts = attack_times(extract_voices(ir))
    assert ts[-1] + Fraction(1, 3) == Fraction(1), "three triplets must fill exactly one beat"
