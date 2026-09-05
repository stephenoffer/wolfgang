"""A chromatic chord over a tonic bass is not that chord.

`_roman_to_bass_degree` was a hand-written dict of ~20 spellings ending in
`return "^1"`, so every numeral it did not list put the TONIC in the bass:

    bVI -> ^1    V/V -> ^1    viio7 -> ^1    #ivo -> ^1

Same shape as the harmonic-function table (Addendum 73): an exact-match table
whose fallback is the most stable answer available, which is the most damaging
one to be wrong with. Now derived from `harmony_analysis` — parse the numeral,
take the chord template, pick the member the inversion puts in the bass.

Fixing it surfaced a second defect. The new derivation emits ALTERED degrees
(`bVI` -> `^#5`), and both anchor resolvers did `int(p[1:])`, returning None for
anything with an accidental — so the expressive degrees (the borrowed flat
sixth, the raised fourth) resolved to no pitch at all. One shared
`pitch.parse_scale_degree` now serves both.
"""

import pytest

from scales.models import Anchor
from scales.pitch import parse_scale_degree
from scales.realizer import Realizer
from scales.sketch_proposer import _roman_to_bass_degree as bass_degree

BASS = {
    "I": "^1", "I6": "^3", "I64": "^5",
    "ii6": "^4", "IV": "^4", "vi": "^6", "iii": "^3",
    "V": "^5", "V7": "^5", "V65": "^7", "V43": "^2",
    "viio": "^7",
}


@pytest.mark.parametrize("roman,expected", sorted(BASS.items()))
def test_the_inversion_decides_the_bass(roman, expected):
    assert bass_degree(roman) == expected


def test_a_chromatic_chord_does_not_get_a_tonic_bass():
    """The defect: four different chromatic chords all returned ^1."""
    for roman in ("bVI", "V/V", "viio7", "#ivo"):
        assert bass_degree(roman) != "^1", roman


def test_an_unparseable_numeral_still_falls_back():
    """A fallback is correct when there is genuinely nothing to derive from."""
    assert bass_degree("not-a-numeral") == "^1"
    assert bass_degree("") == "^1"


def test_altered_degrees_parse():
    assert parse_scale_degree("^5") == (5, 0)
    assert parse_scale_degree("^b6") == (6, -1)
    assert parse_scale_degree("^#4") == (4, 1)


def test_a_pitch_name_is_not_a_degree():
    for name in ("C4", "Bb2", "", None, "^"):
        assert parse_scale_degree(name) is None


@pytest.mark.parametrize("degree,expected", [("^1", 60), ("^5", 67), ("^7", 71),
                                             ("^b6", 68), ("^#4", 66)])
def test_the_realizer_resolves_altered_degrees(degree, expected):
    """`^b6` and `^#4` used to resolve to None — the anchor silently vanished."""
    rz = Realizer.__new__(Realizer)
    anchor = Anchor(bar=1, beat=1.0, pitch_or_degree=degree)
    assert rz._resolve_anchor_pitch(anchor, "C major", [0, 2, 4, 5, 7, 9, 11]) == expected


def test_a_pitch_anchor_still_resolves():
    rz = Realizer.__new__(Realizer)
    anchor = Anchor(bar=1, beat=1.0, pitch_or_degree="C4")
    assert rz._resolve_anchor_pitch(anchor, "C major", [0, 2, 4, 5, 7, 9, 11]) == 60


# ─── The same derivation, from the realizer's side ───────────────────────────

OFFSETS = {
    "I": 0, "I6": 4, "I64": 7,
    "ii": 2, "ii6": 5, "ii65": 5,
    "IV": 5, "IV6": 9, "vi": 9, "iii": 4,
    "V": 7, "V7": 7, "V65": 11, "V43": 2,
    "viio": 11, "viio6": 2, "bVI": 8, "V/V": 2,
}


@pytest.mark.parametrize("roman,expected", sorted(OFFSETS.items()))
def test_the_realizer_bass_offset(roman, expected):
    """A 24-entry dict ending in `mapping.get(roman, 0)` returned 0 — the TONIC
    — for seven of these, including every inversion but the two someone had
    hand-added (`ii6`, `I64`)."""
    from scales.realizer import _roman_to_bass_offset

    assert _roman_to_bass_offset(roman) == expected


def test_the_two_bass_views_agree():
    """`realizer` wants semitones and `sketch_proposer` wants a scale degree.
    They are the same fact, and were two hand-written tables that disagreed with
    each other and with the music."""
    from scales.harmony_analysis import roman_bass_offset
    from scales.realizer import _roman_to_bass_offset

    for roman in OFFSETS:
        assert _roman_to_bass_offset(roman) == roman_bass_offset(roman)


def test_there_is_one_bass_derivation(function_source):
    """The guard: a third table must not appear. Both callers delegate."""


    from scales import realizer, sketch_proposer

    for module, name in (
        (realizer, "_roman_to_bass_offset"),
        (sketch_proposer, "_roman_to_bass_degree"),
    ):
        src = function_source(module, name)
        assert "roman_bass_offset" in src
        assert "mapping = {" not in src and "CHORD_TEMPLATES" not in src


def test_an_unparseable_numeral_falls_back_to_the_tonic_offset():
    from scales.realizer import _roman_to_bass_offset

    assert _roman_to_bass_offset("not-a-numeral") == 0
