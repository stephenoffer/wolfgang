"""The dominant seventh lost its seventh.

`chord_tones` looked its intervals up as `CHORD_INTERVALS.get(quality, [0,4,7])`.
The table is keyed `7` and `hdim7`. The CORPUS — and `analyze_score_bars`, which
writes it — spells them **`dom7`** and **`halfdim7`**. Both missed, and the
fallback is a major triad:

    chord_tones(60, "dom7")     -> [60, 64, 67]   the seventh, gone
    chord_tones(60, "halfdim7") -> [60, 64, 67]   a MAJOR triad

`dom7` covers 734 bars of Mozart alone. Every caller is on the engine
realization path — `harmonic_solver`, `realizer` (four sites), `surface_composer`
(three) — so every dominant seventh the engine realized came out a plain triad,
and every half-diminished chord came out major, which is not a thinner version
of the chord but a different one.

This is the session's recurring shape: the fallback was *musically plausible*,
so nothing sounded broken enough to investigate.
"""

from __future__ import annotations

import pytest

from scales.pitch import chord_tones

#: Every `chord_quality` value the corpus actually contains, with the interval
#: count that proves the quality survived.
CORPUS_QUALITIES = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dom7": [0, 4, 7, 10],
    "dim": [0, 3, 6],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "maj7": [0, 4, 7, 11],
    "halfdim7": [0, 3, 6, 10],
    "aug": [0, 4, 8],
}


@pytest.mark.parametrize("quality,intervals", sorted(CORPUS_QUALITIES.items()))
def test_every_corpus_chord_quality_spells_its_own_chord(quality, intervals):
    assert chord_tones(60, quality) == [60 + i for i in intervals]


def test_a_seventh_chord_has_four_notes():
    """The specific failure: a triad came back where a seventh was asked for."""
    for quality in ("dom7", "min7", "maj7", "dim7", "halfdim7"):
        assert len(chord_tones(60, quality)) == 4, quality


def test_a_half_diminished_chord_is_not_major():
    """Not a smaller error than the missing seventh — a different chord."""
    assert chord_tones(60, "halfdim7") != chord_tones(60, "major")
    assert 63 in chord_tones(60, "halfdim7")  # minor third


def test_the_spelling_is_case_insensitive():
    assert chord_tones(60, "Minor") == chord_tones(60, "minor")
    assert chord_tones(60, "M7") == chord_tones(60, "maj7")


def test_an_unknown_quality_still_yields_a_usable_triad():
    """Every caller is building notes and none can use nothing back."""
    assert chord_tones(60, "nonsense") == [60, 64, 67]


def test_the_corpus_vocabulary_is_covered_with_no_gaps_left():
    """Guards against the corpus growing a spelling the table does not know —
    which is exactly how `dom7` got in."""
    from scales.pitch import CHORD_INTERVALS, CHORD_QUALITY_ALIASES

    known = set(CHORD_INTERVALS) | set(CHORD_QUALITY_ALIASES)
    missing = sorted(q for q in CORPUS_QUALITIES if q not in known)
    assert not missing, f"corpus qualities with no interval spelling: {missing}"
