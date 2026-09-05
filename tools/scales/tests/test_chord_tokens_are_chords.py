"""A chord token must not repeat a pitch.

Two voices doubling one pitch arrive from the extractor as a two-note "chord" —
`['G5','G5']` — and 1,471 of the corpus's 139,923 chords (1.05%) are like that.
The brief printed them straight into the exemplars a composer is told to adapt:

    RH: C5e Bb4e D6e C6e Bb5s Ab5s G5s [Ab5,Ab5]s C5s D5s Eb5h D5e

`[Ab5,Ab5]` is a real unison in Chopin's score and a nonsense chord in shorthand.
The duplicate is removed at RENDERING; the bar records keep what they measured,
because the doubling is a true fact about the voice leading.

The same duplicate also counted as thickness in `voicing_profile`. That effect is
small — schubert 0.196 to 0.195 chord share, rachmaninoff 2.71 to 2.69 notes per
chord — and is fixed for correctness, not because the numbers were misleading.
"""

from scales.composition_brief import _distinct_pitches, _pitch_token


def test_a_doubled_unison_renders_as_one_note():
    assert _pitch_token(["Ab5", "Ab5"]) == "Ab5"


def test_a_real_chord_is_untouched():
    assert _pitch_token(["C3", "E3", "G3"]) == "[C3,E3,G3]"


def test_a_partial_doubling_keeps_the_other_voices():
    assert _pitch_token(["C4", "E4", "C4", "G4"]) == "[C4,E4,G4]"


def test_order_is_preserved():
    """Chord members are printed as the score spells them, not sorted — this
    only removes repeats."""
    assert _distinct_pitches(["G3", "C4", "E4"]) == ["G3", "C4", "E4"]


def test_rests_and_blanks_are_dropped():
    assert _distinct_pitches(["C4", "rest", "", None, "C4"]) == ["C4"]


def test_an_empty_chord_renders_as_nothing():
    assert _pitch_token([]) == ""
    assert _pitch_token(["rest"]) == ""
