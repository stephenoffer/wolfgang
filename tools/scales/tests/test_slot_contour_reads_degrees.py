"""A rising melody must not be labelled "winding down" because of its notation.

`_infer_slot_function` decides a gesture slot's rhetorical role, and its contour
test called `pitch_to_midi` on the anchors. An anchor may be written as a SCALE
DEGREE (`^5`) rather than a pitch, and `pitch_to_midi` returns None for those —
so the test was skipped and the slot fell through to the chain's final
`return "winding_down"`:

    pitches  C4 -> G4  ->  rising_continuation
    degrees  ^1 -> ^5  ->  winding_down          the same melody

A rising slot and a falling slot got the identical label, and "winding down" is
the one that tells the composer to release rather than build.

This is the same shape as the harmonic-function table (Addendum 73): a chain of
exact matches ending in a fallback that is a real, consequential value rather
than "unknown".
"""

import pytest

from scales.models import Anchor, PhraseControlIR
from scales.surface_composer import SurfaceComposer, _degree_number


def _function(start: str, end: str, idx: int = 2, total: int = 4) -> str:
    sc = SurfaceComposer.__new__(SurfaceComposer)
    return sc._infer_slot_function(
        idx, total,
        Anchor(bar=1, beat=1.0, pitch_or_degree=start),
        Anchor(bar=2, beat=1.0, pitch_or_degree=end),
        cadence_bar=99, bar_dur=4.0, control=PhraseControlIR(phrase_id="p"),
    )


@pytest.mark.parametrize("start,end", [("C4", "G4"), ("^1", "^5")])
def test_a_rising_slot_reads_as_rising(start, end):
    assert _function(start, end) == "rising_continuation"


@pytest.mark.parametrize("start,end", [("G4", "C4"), ("^5", "^1")])
def test_a_falling_slot_reads_as_falling(start, end):
    assert _function(start, end) == "falling_continuation"


def test_the_two_notations_agree():
    """The property: notation must not change the reading."""
    assert _function("C4", "G4") == _function("^1", "^5")
    assert _function("G4", "C4") == _function("^5", "^1")


def test_a_flat_slot_is_not_called_rising():
    """Falsification — the fix must not turn every degree pair into motion."""
    assert _function("^3", "^3") == "winding_down"


def test_degree_numbers_are_read_through_accidentals():
    assert _degree_number("^5") == 5
    assert _degree_number("^b6") == 6
    assert _degree_number("^#4") == 4


def test_a_pitch_name_is_not_mistaken_for_a_degree():
    """`_degree_number` must return None for a pitch, or the caller would read
    the octave digit as a scale degree — `C4` would be degree 4."""
    for name in ("C4", "Bb2", "F#5", "", None):
        assert _degree_number(name) is None
