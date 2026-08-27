"""A rest carries no sound, so it must never cost a note its length.

The engine's surface repair read a rest as "the next onset", found the note
before it running past that point, and CLAMPED THE NOTE. A half note with a rest
under its second beat came out a quarter:

    before: (1.0, 'C3', 'h')  (2.0, 'rest', 'q')  (3.0, 'G3', 'h')
    after:  (1.0, 'C3', 'q')  (2.0, 'rest', 'q')  (3.0, 'G3', 'h')
    report: {'overlaps_trimmed': 1}

and "overlaps_trimmed: 1" reads as housekeeping rather than as a bass note
losing half its value.

The rests are the corpus's, legitimately: a retrieved left-hand pattern contains
them, `pitch_to_midi("rest")` returns None so the chord-tone snap falls through
to `pitch = evt.pitch`, and the rest passes into `bass_foundation` unchanged —
under a bass note another generator has already placed there.
"""

from __future__ import annotations

from scales.models import LayerEvent, LayerIR
from scales.scales import _repair_engine_surface


def _bass(*events):
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=1)
    ir.bass_foundation = [
        LayerEvent(bar=1, beat=beat, pitch=pitch, duration=dur, source_layer="bass_foundation")
        for beat, pitch, dur in events
    ]
    return ir


def test_a_covered_rest_is_dropped_and_the_note_keeps_its_length():
    ir = _bass((1.0, "C3", "h"), (2.0, "rest", "q"), (3.0, "G3", "h"))
    report = _repair_engine_surface(ir, (4, 4))
    kept = [(e.beat, e.pitch, e.duration) for e in ir.bass_foundation]
    assert kept == [(1.0, "C3", "h"), (3.0, "G3", "h")], kept
    assert report.get("rest_over_note_dropped") == 1, report
    assert "overlaps_trimmed" not in report, report


def test_a_rest_sharing_a_notes_onset_goes_too():
    """The narrower case, which the group pass has always caught."""
    ir = _bass((2.0, "B2", "q"), (2.0, "rest", "q"), (3.0, "B2", "q"))
    _repair_engine_surface(ir, (4, 4))
    assert [(e.beat, e.pitch) for e in ir.bass_foundation] == [(2.0, "B2"), (3.0, "B2")]


def test_a_rest_in_a_gap_survives():
    """Would this reject real music? A rest where nothing sounds is real notation."""
    ir = _bass((1.0, "C3", "q"), (2.0, "rest", "q"), (3.0, "G3", "h"))
    report = _repair_engine_surface(ir, (4, 4))
    kept = [(e.beat, e.pitch, e.duration) for e in ir.bass_foundation]
    assert kept == [(1.0, "C3", "q"), (2.0, "rest", "q"), (3.0, "G3", "h")], kept
    assert not report, report


def test_a_bar_of_rest_survives():
    """A silent bar in one layer is how a texture drops out; nothing covers it."""
    ir = _bass((1.0, "rest", "w"))
    report = _repair_engine_surface(ir, (4, 4))
    assert [e.pitch for e in ir.bass_foundation] == ["rest"]
    assert not report, report


def test_the_repair_report_separates_a_lost_rest_from_a_lost_note():
    """Five different things reported as `overlaps_trimmed`.

    A rest discarded is noise the repair absorbs completely; two simultaneous
    notes in one orchestral part means a note the composer wrote is GONE. Both
    printed "overlaps_trimmed: 1". A counter that merges opposite diagnoses
    hides the one that matters.
    """
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=1)
    ir.bass_foundation = [
        LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q", source_layer="bass_foundation"),
        LayerEvent(bar=1, beat=1.0, pitch="E3", duration="q", source_layer="bass_foundation"),
    ]
    report = _repair_engine_surface(ir, (4, 4), allow_chords=False)
    assert report.get("simultaneous_notes_dropped") == 1, report
    assert "rest_over_note_dropped" not in report, report
