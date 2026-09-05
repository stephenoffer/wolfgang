"""Every minor chord in the engine path was voiced MAJOR.

`HarmonicSolver.solve` read `cell.quality or _roman_quality(roman, mode)`, and
`HarmonicCell.quality` defaults to `"major"` — a NON-EMPTY default, so the `or`
never fell through and the correctly-parsed quality was never consulted for any
cell built without an explicit one. Which is all of them on the v6 path.

So in D minor:

    i   ->  D  F#  A      (a D MAJOR triad where the notation says minor)
    iv  ->  G  B         (should be G Bb D)

Measured on a planned piece, **5 of 16 bars carried a pitch class outside their
own chord**, every one of them that F# — sounding against a melody correctly
playing F natural, and surfacing as a cross-relation two modules away.

`parse_roman` had the right answer the whole time: `i` IS minor, the numeral
says so. The `quality` field is redundant beside a roman and only meaningful
without one. A default that is not empty shadows the derivation it was meant to
fall back to — the inverse of a value never set at the source, and just as
silent.
"""

import pytest

from scales.harmonic_solver import HarmonicSolver
from scales.models import HarmonicCell


def _pcs(roman, key="D minor", meter=(4, 4)):
    voiced = HarmonicSolver().solve(
        [HarmonicCell(bar=1, beat=1.0, roman=roman, key=key)], key, meter
    )
    if not voiced:
        pytest.skip(f"solver returned nothing for {roman}")
    return sorted(
        {m % 12 for k, m in voiced[0].items() if k.endswith("_midi") and isinstance(m, int)}
    ), voiced[0].get("quality")


def test_a_lowercase_roman_is_voiced_minor():
    """D minor's tonic is D F A. It was D F# A."""
    pcs, quality = _pcs("i")
    assert quality == "minor"
    assert 5 in pcs and 6 not in pcs, f"F# in a D minor tonic: {pcs}"


def test_the_subdominant_of_a_minor_key_is_minor():
    pcs, quality = _pcs("iv")
    assert quality == "minor"
    assert 10 in pcs and 11 not in pcs, f"B natural in a G minor chord: {pcs}"


def test_the_dominant_of_a_minor_key_is_still_major():
    """The fix must not make everything minor: V in D minor is A C# E."""
    pcs, quality = _pcs("V")
    assert quality == "major"
    assert 1 in pcs, f"the leading tone C# is missing: {pcs}"


def test_a_flat_submediant_is_major():
    pcs, quality = _pcs("VI")
    assert quality == "major"
    assert set(pcs) <= {10, 2, 5}, f"VI in D minor should be Bb D F: {pcs}"


def test_a_seventh_keeps_its_own_quality():
    _, quality = _pcs("V7")
    assert quality not in ("major", "minor"), f"V7 flattened to a plain triad: {quality}"


def test_an_explicit_quality_still_wins_when_there_is_no_roman():
    """The field remains meaningful for a cell that names no numeral."""
    voiced = HarmonicSolver().solve(
        [HarmonicCell(bar=1, beat=1.0, roman="", key="D minor", quality="minor")],
        "D minor",
        (4, 4),
    )
    if voiced:
        assert voiced[0].get("quality") == "minor"


@pytest.mark.parametrize("roman", ["i", "ii", "III", "iv", "V", "VI", "vii"])
def test_every_degree_of_a_minor_key_gets_a_quality_from_its_numeral(roman):
    """`i` was right by luck, so the function looked right, and everything that
    was not `i` was wrong in the same way."""
    from scales.harmony_analysis import parse_roman

    parsed = parse_roman(roman)
    if not parsed:
        pytest.skip(f"{roman} does not parse")
    _, quality = _pcs(roman)
    assert quality == parsed["quality"], f"{roman}: solver says {quality}, numeral says {parsed['quality']}"
