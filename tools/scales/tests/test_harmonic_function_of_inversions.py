"""An inversion has the same function as its root position.

`sketch_proposer._classify_harmonic_function` was an exact-match table over
eleven spellings with a fallback of `return TONIC`. Everything it did not
literally list came back tonic — and what it did not list is the inversions and
sevenths that make up most of real music:

    ii65  IV6  iv6        -> tonic, should be predominant
    V65   V43  V42        -> tonic, should be DOMINANT
    viio6 viio7           -> tonic, should be DOMINANT

Nine of twenty-two common numerals wrong, six of them dominants read as tonic —
which inverts the tension of every cadence built on one, and `V65` is the
commonest dominant inversion in tonal music.

Now delegates to `harmony_analysis.parse_roman` + `classify_function`, the pair
that already round-trips 9,216 combinations of degree, quality and inversion.
"""

import pytest

from scales.sketch_proposer import _classify_harmonic_function as classify

TONIC = ["I", "i", "I6", "i6", "I64", "vi", "iii"]
PREDOMINANT = ["ii", "ii6", "ii65", "IV", "IV6", "iv", "iv6"]
DOMINANT = ["V", "V7", "V65", "V43", "V42", "viio", "viio6", "viio7"]


@pytest.mark.parametrize("roman", TONIC)
def test_tonic_function(roman):
    assert classify(roman) == "tonic"


@pytest.mark.parametrize("roman", PREDOMINANT)
def test_predominant_function(roman):
    assert classify(roman) == "predominant"


@pytest.mark.parametrize("roman", DOMINANT)
def test_dominant_function(roman):
    """The six that used to come back "tonic" are in here."""
    assert classify(roman) == "dominant"


def test_an_inversion_keeps_its_root_positions_function():
    """The property the exact-match table could not express."""
    for root, inversions in (("V", ["V6", "V65", "V43", "V42"]),
                             ("ii", ["ii6", "ii65"]),
                             ("IV", ["IV6", "IV64"])):
        for inv in inversions:
            assert classify(inv) == classify(root), f"{inv} vs {root}"


def test_genuinely_chromatic_chords_are_chromatic():
    """Falsification: the fix must not simply classify everything as diatonic.
    These are the real spellings the corpus produces, in descending frequency."""
    for roman in ("viio7/V", "#ivo", "#IV", "bIII"):
        assert classify(roman) == "chromatic", roman


def test_a_borrowed_chord_gets_its_FUNCTION_not_just_chromatic():
    """`bVI` comes back "predominant", and that is the better answer: the flat
    submediant is a borrowed chord that behaves as a predominant, characteristically
    moving to V. Reading it by degree and quality says something useful where
    "chromatic" only says "not diatonic".

    Recorded because my first version of the test above expected "chromatic" and
    was wrong about the music, not about the code."""
    assert classify("bVI") == "predominant"


def test_junk_is_chromatic_not_tonic():
    """The old fallback made an unparseable symbol TONIC — the most consequential
    wrong answer available. Unknown must not mean "stable"."""
    for junk in ("", "not-a-numeral", "???"):
        assert classify(junk) == "chromatic"
