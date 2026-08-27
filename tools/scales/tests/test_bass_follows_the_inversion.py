"""The bass note of a chord is the one its INVERSION puts there.

`Realizer._harmony_to_bass` kept its own Roman-numeral table — nineteen entries
mapping a symbol to a scale degree, with everything unlisted falling through to
`0`, the root. Only `ii6` and `I64` of all the inversions in common use were in
it, so `i6`, `I6`, `V6`, `V65`, `V43` and the rest were silently played in root
position: the notation says one thing and the bass plays another.

In G minor that put G under an `i6` where the notation says B flat, and a
subsequent scale snap moved it to B NATURAL — a note outside the key, sounding
against the melody's B flat and reported as a cross-relation.

`harmony_analysis` is this project's one Roman parser and already covered every
degree, quality and inversion.
"""

from __future__ import annotations

import pytest

from scales.models import HarmonyEvent
from scales.pitch import midi_to_pitch
from scales.realizer import Realizer


def _bass(roman: str, key: str) -> str:
    realizer = Realizer.__new__(Realizer)
    midi = realizer._harmony_to_bass(HarmonyEvent(bar=1, beat=1.0, roman=roman), [], key)
    return midi_to_pitch(midi, key)


@pytest.mark.parametrize(
    "roman,expected",
    [
        ("i", "G"),  # root position
        ("i6", "Bb"),  # the third — was G, then B natural
        ("V", "D"),
        ("V6", "F#"),  # the leading tone, raised in minor
        ("V43", "A"),  # the seventh's second inversion puts the fifth in the bass
        ("I64", "D"),  # a cadential six-four IS the fifth in the bass
        ("iv", "C"),
        ("VI", "Eb"),
    ],
)
def test_the_bass_is_the_note_the_inversion_names(roman, expected):
    assert _bass(roman, "g minor").rstrip("0123456789") == expected


def test_the_same_holds_in_major():
    assert _bass("I", "C major").rstrip("0123456789") == "C"
    assert _bass("I6", "C major").rstrip("0123456789") == "E"
    assert _bass("V65", "C major").rstrip("0123456789") == "B"
    assert _bass("ii6", "C major").rstrip("0123456789") == "F"


def test_the_bass_stays_in_the_bass():
    """An inversion is a different NOTE, not a different register."""
    realizer = Realizer.__new__(Realizer)
    for roman in ("i", "i6", "V", "V6", "V43", "I64", "iv", "VI"):
        midi = realizer._harmony_to_bass(HarmonyEvent(bar=1, beat=1.0, roman=roman), [], "g minor")
        assert 36 <= midi <= 60, f"{roman} put the bass at midi {midi}"


def test_an_unparseable_symbol_falls_back_to_the_tonic():
    """Deliberate, and no longer the answer for most inversions in common use."""
    assert _bass("not-a-roman", "g minor").rstrip("0123456789") == "G"


def test_no_second_roman_table_is_maintained_here(function_source):
    """The table is what was wrong; a new one would be the same bug again."""
    from scales import realizer

    src = function_source(realizer, "_harmony_to_bass")
    assert "roman_pitches" in src, "the bass must come from the one Roman parser"
    assert "degree_offsets" not in src, "a second Roman-numeral table has come back"
