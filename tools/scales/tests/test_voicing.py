"""Texture and voicing measurement.

The thresholds these tests pin were set by measuring 22 real movements, not by
judgement. Two assumptions died in that measurement and the tests below record
both, because both were about to drive work in the wrong direction:

* A generated piece at 1.13 RH notes per attack was assumed "thin". Real
  Mozart's median is 1.15. It was not thin.
* Its texture-change rate of 0.62 was assumed restless. Mozart's range is
  0.37-0.67. It was not restless.

What the measurement *did* find is that its simultaneity never varies — CV 0.19
against a Mozart floor of 0.22. That is the finding the numbers support, and the
style-aware floor is what makes it visible.
"""

import pytest

from scales.models import LayerEvent, LayerIR
from scales.voicing import (
    CORPUS_TEXTURE,
    analyze_voicing,
    floors_for,
    measure_bars,
    register_of,
    suggest_thickening_points,
    texture_label,
    texture_runs,
)


def _ev(bar, beat, pitch, dur="q", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _single_line(bars=12):
    """One bare line over one repeating bass note — the thin case."""
    ir = LayerIR(meter=(4, 4), key="C")
    tune = ["C5", "D5", "E5", "F5"]
    for b in range(1, bars + 1):
        for i in range(4):
            ir.principal_line.append(_ev(b, 1 + i, tune[i]))
        ir.bass_foundation.append(_ev(b, 1.0, "C3", "w"))
    return ir


def _varied(bars=12):
    """A texture that thickens and thins the way a real one does."""
    ir = LayerIR(meter=(4, 4), key="C")
    for b in range(1, bars + 1):
        thick = b % 4 == 0
        for i in range(4):
            p = ["C5", "E5", "G5"] if thick else ["C5", "D5", "E5", "F5"][i]
            ir.principal_line.append(_ev(b, 1 + i, p))
        for i in range(4):
            ir.bass_foundation.append(_ev(b, 1 + i, ["C3", "G3"] if thick else "C3", "q"))
    return ir


# ─── Measurement ─────────────────────────────────────────────────────────────


def test_simultaneity_counts_sustained_notes_not_just_attacks():
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1.0, "C5", "w")]
    ir.bass_foundation = [_ev(1, 1 + i, "C3", "q") for i in range(4)]
    bars = measure_bars(ir)
    assert bars[0].mean_simultaneity == 2.0, "the held C5 sounds under every bass note"


def test_a_chord_counts_as_several_notes_not_one():
    """``melody_density`` counting a chord as one event is why block-chordal and
    single-line bars were indistinguishable in every density statistic."""
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1.0, ["C5", "E5", "G5"], "w")]
    assert measure_bars(ir)[0].max_simultaneity == 3


def test_registers_are_named_by_sound():
    assert register_of(60) == "tenor"  # middle C
    assert register_of(72) == "soprano"
    assert register_of(36) == "sub_bass"
    assert register_of(200) == "brilliant"  # out of range, does not crash


def test_texture_labels_describe_what_is_heard():
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1.0, "C5", "w")]
    assert texture_label(measure_bars(ir)[0]) == "monophonic"

    ir2 = LayerIR(meter=(4, 4))
    ir2.principal_line = [_ev(1, 1 + i, "C5") for i in range(4)]
    ir2.bass_foundation = [_ev(1, 1 + i, ["C3", "G3"]) for i in range(4)]
    assert texture_label(measure_bars(ir2)[0]) == "melody_and_accompaniment"

    ir3 = LayerIR(meter=(4, 4))
    ir3.principal_line = [_ev(1, 1 + i, ["C5", "E5", "G5"]) for i in range(4)]
    ir3.bass_foundation = [_ev(1, 1.0, "C3", "w")]
    assert texture_label(measure_bars(ir3)[0]) == "chordal"


def test_texture_runs_expose_a_long_unchanging_stretch():
    """The '12 bars of identical arpeggios' finding, made visible."""
    runs = texture_runs(_single_line(12))
    assert len(runs) == 1
    label, first, last = runs[0]
    assert (first, last) == (1, 12)


def test_a_varied_texture_produces_several_runs():
    assert len(texture_runs(_varied(12))) > 1


def test_thirds_and_sixths_are_detected():
    ir = LayerIR(meter=(4, 4))
    for i in range(4):
        ir.principal_line.append(_ev(1, 1 + i, ["C5", "E5"]))  # a third
    assert analyze_voicing(ir).thirds_sixths_pct == 1.0


def test_a_bass_note_held_under_a_higher_chord_is_not_a_stretch():
    """A pedal point is held by the PEDAL, not by the fingers.

    An earlier version of this test asserted the opposite, on the reasoning that
    a note sustained under a later one is the commonest way a stretch appears.
    Real music settled it: counting everything *sounding* together produced 211
    "unplayable" stretches across 1,027 bars of Mozart, Beethoven and Chopin,
    with a median widest span of 28 semitones — an octave and a half, which no
    hand spans and every pianist plays.
    """
    ir = LayerIR(meter=(4, 4))
    ir.bass_foundation = [_ev(1, 1.0, "C2", "w"), _ev(1, 3.0, "E3", "h")]
    rep = analyze_voicing(ir)
    assert rep.unplayable_spans == []


def test_a_simultaneous_attack_beyond_a_hands_reach_is_reported():
    ir = LayerIR(meter=(4, 4))
    ir.bass_foundation = [_ev(1, 1.0, ["C2", "A3"], "w")]  # 21 semitones, struck together
    rep = analyze_voicing(ir)
    assert rep.unplayable_spans
    assert rep.widest_hand_span == 21


def test_a_tenth_struck_together_is_not_reported():
    """Real writing is full of tenths; the threshold is set above them."""
    ir = LayerIR(meter=(4, 4))
    ir.bass_foundation = [_ev(1, 1.0, ["C3", "E4"], "w")]  # a tenth
    assert analyze_voicing(ir).unplayable_spans == []


def test_an_overlapping_strand_of_the_melody_stays_in_the_right_hand():
    """Stripping only '#' left 'principal_line@1' unmatched, so a melody note
    held under its own continuation was counted as an accompaniment note."""
    ir = LayerIR(meter=(4, 4))
    ir.principal_line = [_ev(1, 1.0, "G5", "w"), _ev(1, 2.0, "C5", "h")]
    rep = analyze_voicing(ir)
    assert rep.rh_notes_per_attack > 0
    assert rep.lh_notes_per_attack == 0, "no left hand was written"


# ─── Suggestions ─────────────────────────────────────────────────────────────


def test_a_genuinely_thin_texture_is_called_out():
    rep = analyze_voicing(_single_line(16), style="mozart")
    joined = " ".join(rep.suggestions)
    assert rep.suggestions
    assert "single line" in joined or "notes per attack" in joined


def test_a_varied_texture_draws_no_thinness_complaint():
    rep = analyze_voicing(_varied(16), style="mozart")
    assert not any("bare single line" in s for s in rep.suggestions)


def test_style_floors_are_tighter_for_classical_than_the_union():
    """Mozart's simultaneity never drops below 0.22; Chopin's reaches 0.16."""
    assert floors_for("mozart")["simultaneity_cv"] > floors_for(None)["simultaneity_cv"]
    assert floors_for("chopin")["simultaneity_cv"] == floors_for(None)["simultaneity_cv"]


def test_a_short_phrase_draws_no_texture_conclusions():
    """Four bars is not enough evidence to say anything about texture over time."""
    assert analyze_voicing(_single_line(4)).suggestions == []


def test_corpus_baselines_are_present_and_plausible():
    for period, vals in CORPUS_TEXTURE.items():
        assert 1.0 <= vals["rh_notes_per_attack"] <= 3.0, period
        assert 0.0 <= vals["single_line_rh_pct"] <= 1.0, period
        assert 30 <= vals["register_span"] <= 80, period


# ─── Thickening advice ───────────────────────────────────────────────────────


def test_the_most_exposed_melody_note_is_ranked_first():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [
        _ev(1, 1.0, "C5", "q"),
        _ev(1, 2.0, "G5", "h"),  # long, high, alone — the exposed one
        _ev(1, 4.0, "E5", "q"),
    ]
    pts = suggest_thickening_points(ir)
    assert pts and pts[0]["pitch_midi"] == 79


def test_a_note_already_supported_is_not_suggested():
    ir = LayerIR(meter=(4, 4), key="C")
    ir.principal_line = [_ev(1, 1.0, "G5", "w")]
    ir.counter_reply = [_ev(1, 1.0, "C5", "w")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "w")]
    assert suggest_thickening_points(ir) == []


# ─── Contract ────────────────────────────────────────────────────────────────


def test_empty_input_is_safe():
    rep = analyze_voicing(LayerIR())
    assert rep.bars == []
    assert "no sounding notes" in rep.observations


def test_metadata_is_never_iterated_as_notes():
    ir = LayerIR(meter=(3, 4), key="a minor", bar_count=4)
    ir.principal_line = [_ev(1, 1.0, "A4")]
    analyze_voicing(ir)  # must not raise
    assert ir.meter == (3, 4)


@pytest.mark.parametrize("meter", [(4, 4), (3, 4), (6, 8), (2, 2), (12, 8)])
def test_every_meter_measures_without_error(meter):
    ir = LayerIR(meter=meter, key="C")
    for b in range(1, 9):
        ir.principal_line.append(_ev(b, 1.0, "C5", "q"))
        ir.bass_foundation.append(_ev(b, 1.0, "C3", "q"))
    rep = analyze_voicing(ir)
    assert len(rep.bars) == 8
