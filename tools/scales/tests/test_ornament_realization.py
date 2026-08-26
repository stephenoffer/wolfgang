"""Ornaments have to be audible or they do not exist.

The music-critic judges by listening to the MIDI preview. Measured on the test
piece: 12 written ornaments and 17 grace notes across 41 bars — 0.29 ornaments
per bar, **0.00 audible per bar**. A trill engraved a ``tr`` and played one plain
note, and appoggiatura and acciaccatura rendered identically, so the leaning
dissonance that carries most of the expression in a Classical slow movement
sounded exactly like the ornament that deliberately takes no time.
"""

from fractions import Fraction

import pytest

from scales.models import LayerEvent
from scales.ornament_realization import (
    lower_neighbour,
    ornament_summary,
    realize,
    realize_acciaccatura,
    realize_appoggiatura,
    realize_event,
    realize_mordent,
    realize_trill,
    realize_turn,
    realizes,
    upper_neighbour,
)

C5 = 72  # middle-C octave 5 in this project's numbering
G4 = 67


# ─── Scale-correct neighbours ────────────────────────────────────────────────


def test_the_upper_neighbour_follows_the_key_not_a_fixed_interval():
    """A trill on the leading tone is a semitone; on the mediant it is a tone."""
    b_natural = 71  # leading tone of C major
    assert upper_neighbour(b_natural, "C major") == 72  # semitone to C
    e_natural = 64  # mediant of C major
    assert upper_neighbour(e_natural, "C major") == 65  # semitone to F
    c = 60
    assert upper_neighbour(c, "C major") == 62  # whole tone to D


def test_the_lower_neighbour_follows_the_key():
    assert lower_neighbour(60, "C major") == 59  # C down to B
    assert lower_neighbour(65, "C major") == 64  # F down to E


def test_minor_keys_use_the_raised_leading_tone():
    """A trill on the dominant of A minor turns to G#, not G natural."""
    assert upper_neighbour(67, "a minor") == 68  # G -> G#


# ─── Trill ───────────────────────────────────────────────────────────────────


def test_a_trill_actually_alternates():
    notes = realize_trill(C5, Fraction(2), "C major", tempo_bpm=90)
    assert len(notes) > 3
    pitches = {n.midi for n in notes}
    assert len(pitches) >= 2, "a trill that plays one pitch is not a trill"


def test_a_classical_trill_starts_on_the_upper_note():
    """The commonest misreading of Classical ornamentation there is."""
    notes = realize_trill(C5, Fraction(2), "C major", start_upper=True)
    assert notes[0].midi == upper_neighbour(C5, "C major")


def test_a_romantic_trill_starts_on_the_principal():
    notes = realize("trill", C5, Fraction(2), key="C major", tempo_bpm=90, period="romantic")
    assert notes[0].midi == C5


def test_a_trill_fills_exactly_its_written_duration():
    dur = Fraction(2)
    notes = realize_trill(C5, dur, "C major", tempo_bpm=90)
    end = max(n.offset_beats + n.duration_beats for n in notes)
    assert end == dur, f"trill ran to {end}, not {dur}"


def test_a_trill_ends_with_a_closing_turn():
    """A trill that simply runs out sounds like a mistake."""
    notes = realize_trill(C5, Fraction(4), "C major", tempo_bpm=60, termination=True)
    assert notes[-1].midi == C5
    assert notes[-2].midi == lower_neighbour(C5, "C major")


def test_a_faster_tempo_gives_a_trill_fewer_notes():
    slow = realize_trill(C5, Fraction(2), "C major", tempo_bpm=50)
    fast = realize_trill(C5, Fraction(2), "C major", tempo_bpm=180)
    assert len(fast) < len(slow)


def test_a_note_too_short_to_trill_is_left_alone():
    assert realize_trill(C5, Fraction(1, 32), "C major") == []


# ─── Mordents and turns ──────────────────────────────────────────────────────


def test_a_mordent_dips_below_and_an_inverted_one_rises():
    """Only one of the two was spellable, so every prall came out inverted."""
    down = realize_mordent(C5, Fraction(1), "C major", inverted=False)
    up = realize_mordent(C5, Fraction(1), "C major", inverted=True)
    assert down[1].midi < C5
    assert up[1].midi > C5


def test_a_mordent_returns_to_its_principal():
    notes = realize_mordent(C5, Fraction(1), "C major")
    assert notes[0].midi == C5 and notes[-1].midi == C5


def test_a_turn_is_four_notes_around_the_principal():
    notes = realize_turn(C5, Fraction(2), "C major")
    assert [n.midi for n in notes[:4]] == [
        upper_neighbour(C5, "C major"),
        C5,
        lower_neighbour(C5, "C major"),
        C5,
    ]


def test_an_inverted_turn_goes_the_other_way():
    notes = realize_turn(C5, Fraction(2), "C major", inverted=True)
    assert notes[0].midi == lower_neighbour(C5, "C major")


def test_a_turn_written_after_the_note_holds_the_principal_first():
    notes = realize_turn(C5, Fraction(4), "C major", after=True)
    assert notes[0].midi == C5
    assert notes[0].duration_beats == Fraction(2)


# ─── Appoggiatura vs acciaccatura — the distinction that was lost ────────────


def test_an_appoggiatura_takes_half_the_principals_time():
    notes = realize_appoggiatura(74, C5, Fraction(2))
    assert notes[0].duration_beats == Fraction(1)
    assert notes[1].duration_beats == Fraction(1)
    assert notes[0].offset_beats == 0, "an appoggiatura is ON the beat"


def test_an_appoggiatura_is_accented_and_its_resolution_is_not():
    notes = realize_appoggiatura(74, C5, Fraction(2))
    assert notes[0].velocity_scale > notes[1].velocity_scale


def test_an_appoggiatura_on_a_dotted_note_takes_two_thirds():
    notes = realize_appoggiatura(74, C5, Fraction(3), dotted=True)
    assert notes[0].duration_beats == Fraction(2)


def test_an_acciaccatura_takes_no_time_and_comes_before_the_beat():
    notes = realize_acciaccatura(74, C5, Fraction(2))
    assert notes[0].offset_beats < 0, "an acciaccatura is crushed BEFORE the beat"
    assert notes[-1].duration_beats == Fraction(2), "the principal keeps its full value"


def test_the_two_grace_notes_do_not_sound_the_same():
    """They rendered identically, which is the bug."""
    app = realize_appoggiatura(74, C5, Fraction(2))
    acc = realize_acciaccatura(74, C5, Fraction(2))
    assert [n.as_tuple() for n in app] != [n.as_tuple() for n in acc]


# ─── Entry point ─────────────────────────────────────────────────────────────


def test_unknown_and_non_sounding_ornaments_realize_to_nothing():
    assert realize("fermata", C5, Fraction(2)) == []
    assert realize(None, C5, Fraction(2)) == []
    assert realize("something-invented", C5, Fraction(2)) == []
    assert realize("trill", C5, Fraction(0)) == []


def test_realizes_reports_what_is_audible():
    assert realizes("trill")
    assert realizes("turn")
    assert not realizes("fermata")
    assert not realizes(None)


def test_realize_event_reads_the_events_own_fields():
    e = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="h", ornament="trill")
    notes = realize_event(e, key="C major", tempo_bpm=90)
    assert len(notes) > 3


def test_realize_event_ignores_a_rest_and_an_unornamented_note():
    assert realize_event(LayerEvent(pitch="rest", ornament="trill")) == []
    assert realize_event(LayerEvent(pitch="C5", duration="h")) == []


def test_the_summary_exposes_silent_ornaments():
    events = [
        LayerEvent(bar=1, beat=1.0, pitch="C5", ornament="trill"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", ornament="fermata"),
        LayerEvent(bar=2, beat=1.0, pitch="E5"),
    ]
    s = ornament_summary(events)
    assert s["ornaments"] == 2
    assert s["audible"] == 1, "a fermata is not an audible ornament realization"
    assert s["by_kind"]["trill"] == 1


@pytest.mark.parametrize(
    "name", ["trill", "mordent", "inverted_mordent", "turn", "inverted_turn", "schleifer"]
)
def test_every_realization_stays_inside_its_written_duration(name):
    dur = Fraction(2)
    notes = realize(name, C5, dur, key="C major", tempo_bpm=90)
    assert notes, name
    end = max(n.offset_beats + n.duration_beats for n in notes)
    assert end == dur, f"{name} ran to {end}, not {dur}"
    assert all(n.offset_beats >= 0 for n in notes), f"{name} started before its beat"


@pytest.mark.parametrize("key", ["C major", "a minor", "F# major", "Eb major", "bb minor"])
def test_every_key_yields_sane_neighbours(key):
    for midi in (60, 63, 67, 71):
        up, dn = upper_neighbour(midi, key), lower_neighbour(midi, key)
        assert 0 < up - midi <= 2, f"{key}: upper neighbour of {midi} was {up}"
        assert 0 < midi - dn <= 2, f"{key}: lower neighbour of {midi} was {dn}"
