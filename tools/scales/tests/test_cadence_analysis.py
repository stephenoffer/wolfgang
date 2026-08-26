"""Cadence reading.

Falsified against real scores: the final bar of all 15 real movements tested
reads as an authentic or plagal cadence and none as "no cadence" (the corpus
harness in ``test_corpus_cadence.py`` pins that). Four bugs were found and fixed
by that exercise, each of which silently mislabelled every cadence in the piece:

* ``harmony_analysis.candidates`` takes a 12-slot vector indexed by pitch class;
  passing a dict made ``sum()`` add the keys, so every reading came back empty.
* Passing pitch classes instead of MIDI made the *lowest pitch class* the bass,
  so a root-position F major tonic containing a C read as I64.
* Timing the cadence at the bar's final attack reported every cadence in a 3/4
  piece as landing on beat 3.
* The analyzer drops any beat with fewer than two sounding pitch classes, so a
  final tonic whose bass is struck alone on the downbeat lost its bass and read
  as a first-inversion chord.
"""

import pytest

from scales.cadence_analysis import (
    analyze_cadences,
    cadence_summary_lines,
    check_against_plan,
    read_cadence,
    scale_degree,
)
from scales.models import LayerEvent, LayerIR


def _ev(bar, beat, pitch, dur="q"):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur)


def _cadence_phrase(kind="PAC", key="C major", meter=(4, 4)):
    """Two bars: a dominant, then the goal chord that ``kind`` implies."""
    ir = LayerIR(key=key, meter=meter, bar_count=2)
    # Bar 1: G major in ROOT POSITION (the dominant of C). The bass has to be
    # held under the upper voices, not replaced by them — a PAC requires both
    # chords in root position, and a fixture whose "dominant" bar ends with B in
    # the bass is a V6 and correctly downgrades the cadence to imperfect.
    ir.principal_line += [_ev(1, 1.0, "D5", "h"), _ev(1, 3.0, "B4", "h")]
    ir.bass_foundation += [_ev(1, 1.0, "G2", "w"), _ev(1, 3.0, ["B3", "D4"], "h")]
    goals = {
        "PAC": (["C5"], "C3", ["E3", "G3"]),
        "IAC": (["E5"], "C3", ["E3", "G3"]),
        "DC": (["C5"], "A2", ["C3", "E3"]),
        "HC": (["D5"], "G2", ["B3", "D4"]),
    }
    mel, bass, chord = goals[kind]
    ir.principal_line.append(_ev(2, 1.0, mel[0], "w"))
    ir.bass_foundation.append(_ev(2, 1.0, bass, "w"))
    ir.bass_foundation.append(_ev(2, 3.0, chord, "h"))
    return ir


# ─── Classification ──────────────────────────────────────────────────────────


def test_a_perfect_authentic_cadence_is_read_as_one():
    c = read_cadence(_cadence_phrase("PAC"), cadence_bar=2, key="C major", is_final=True)
    assert c is not None
    assert c.kind == "PAC"
    assert c.soprano_degree == 1
    assert c.root_position


def test_the_same_cadence_with_the_third_on_top_is_imperfect():
    """PAC vs IAC is the distinction that decides whether a piece sounds closed."""
    c = read_cadence(_cadence_phrase("IAC"), cadence_bar=2, key="C major", is_final=True)
    assert c.kind == "IAC"
    assert c.soprano_degree == 3


def test_a_deceptive_cadence_is_read_as_one():
    c = read_cadence(_cadence_phrase("DC"), cadence_bar=2, key="C major")
    assert c.kind == "DC"


def test_a_phrase_ending_on_the_dominant_is_a_half_cadence():
    c = read_cadence(_cadence_phrase("HC"), cadence_bar=2, key="C major")
    assert c.kind == "HC"


# ─── The four bugs, pinned ───────────────────────────────────────────────────


def test_a_root_position_tonic_is_not_read_as_a_six_four():
    """Pitch classes as bass made any chord containing a C read over C."""
    ir = LayerIR(key="F major", meter=(3, 4), bar_count=2)
    ir.principal_line = [_ev(1, 1.0, "E5", "dh"), _ev(2, 1.0, "F5", "dh")]
    ir.bass_foundation = [
        _ev(1, 1.0, "C3", "q"),
        _ev(1, 2.0, ["E3", "G3"], "h"),
        _ev(2, 1.0, "F2", "q"),
        _ev(2, 2.0, ["A2", "C3", "F3"], "h"),
    ]
    c = read_cadence(ir, cadence_bar=2, key="F major", is_final=True)
    assert c.goal_roman.rstrip("6432") in ("I", "i"), c.goal_roman
    assert c.root_position, "the bass F2 makes this root position"


def test_the_cadence_lands_where_the_chord_arrives_not_at_the_last_note():
    """Timing it at the bar's last attack read every 3/4 cadence as beat 3."""
    ir = LayerIR(key="F major", meter=(3, 4), bar_count=2)
    ir.principal_line = [_ev(1, 1.0, "G4", "dh"), _ev(2, 1.0, "F5", "dh")]
    ir.bass_foundation = [
        _ev(1, 1.0, "C3", "dh"),
        _ev(2, 1.0, "F2", "q"),
        _ev(2, 2.0, ["A2", "C3"], "q"),
        _ev(2, 3.0, ["A2", "C3"], "q"),
    ]
    c = read_cadence(ir, cadence_bar=2, key="F major", is_final=True)
    assert c.beat == 1.0
    assert c.metric_strength == "downbeat"


def test_roman_numerals_are_actually_produced():
    """A dict passed where a 12-slot vector was expected returned nothing at all."""
    c = read_cadence(_cadence_phrase("PAC"), cadence_bar=2, key="C major", is_final=True)
    assert c.approach_roman, "approach chord was not named"
    assert c.goal_roman, "goal chord was not named"


def test_a_bass_struck_alone_on_the_downbeat_still_counts_as_the_bass():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [_ev(1, 1.0, "B4", "w"), _ev(2, 1.0, "C5", "w")]
    ir.bass_foundation = [
        _ev(1, 1.0, "G2", "w"),
        _ev(2, 1.0, "C3", "q"),  # struck alone under the melody
        _ev(2, 2.0, ["E3", "G3"], "dh"),
    ]
    c = read_cadence(ir, cadence_bar=2, key="C major", is_final=True)
    assert c.root_position
    assert c.kind == "PAC"


# ─── Plan comparison ─────────────────────────────────────────────────────────


def test_a_written_cadence_is_checked_against_the_planned_one():
    c = read_cadence(_cadence_phrase("HC"), cadence_bar=2, key="C major")
    assert check_against_plan(c, "HC") is True
    assert check_against_plan(c, "PAC") is False


def test_aliases_are_accepted():
    c = read_cadence(_cadence_phrase("PAC"), cadence_bar=2, key="C major", is_final=True)
    assert check_against_plan(c, "authentic") is True
    assert check_against_plan(c, "perfect") is True


def test_no_plan_means_no_verdict():
    c = read_cadence(_cadence_phrase("PAC"), cadence_bar=2, key="C major")
    assert check_against_plan(c, None) is None
    assert check_against_plan(None, "PAC") is None


# ─── Repetition — the finding this module exists for ─────────────────────────


def test_the_same_cadence_every_time_is_reported():
    phrases = [(_cadence_phrase("PAC"), 2, "C major", "PAC") for _ in range(6)]
    rep = analyze_cadences(phrases)
    assert rep.variety < 0.4
    assert rep.repeated_formulas and rep.repeated_formulas[0][1] == 6
    assert any("same cadence formula" in s for s in rep.suggestions)


def test_varied_cadences_draw_no_repetition_complaint():
    phrases = [(_cadence_phrase(k), 2, "C major", None) for k in ("HC", "PAC", "DC", "IAC", "HC")]
    rep = analyze_cadences(phrases)
    assert not any("same cadence formula" in s for s in rep.suggestions)


def test_all_authentic_cadences_is_called_out():
    phrases = [(_cadence_phrase(k), 2, "C major", None) for k in ("PAC", "IAC", "PAC")]
    rep = analyze_cadences(phrases)
    assert any("no forward momentum" in s for s in rep.suggestions)


# ─── Contract ────────────────────────────────────────────────────────────────


def test_scale_degrees_are_mode_aware():
    assert scale_degree(60, 0, "major") == 1
    assert scale_degree(64, 0, "major") == 3
    assert scale_degree(63, 0, "minor") == 3  # minor third
    assert scale_degree(63, 0, "major") is None  # not in the major scale


def test_empty_input_is_safe():
    assert read_cadence(LayerIR()) is None
    rep = analyze_cadences([])
    assert rep.cadences == []
    assert "no cadences readable" in rep.observations


def test_summary_lines_are_readable():
    phrases = [(_cadence_phrase("PAC"), 2, "C major", "PAC")]
    lines = cadence_summary_lines(analyze_cadences(phrases))
    assert lines and "perfect authentic cadence" in lines[0]


@pytest.mark.parametrize("meter", [(4, 4), (3, 4), (6, 8), (2, 4)])
def test_every_meter_reads_without_error(meter):
    c = read_cadence(_cadence_phrase("PAC", meter=meter), cadence_bar=2, key="C major")
    assert c is not None


def test_metadata_is_never_iterated_as_notes():
    ir = _cadence_phrase("PAC", key="a minor", meter=(3, 4))
    read_cadence(ir, cadence_bar=2, key="a minor")  # must not raise
    assert ir.meter == (3, 4)
