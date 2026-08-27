"""How many notes sound together, across every voice stream.

"Does this staff notate a chord" is a KEYBOARD question. `avg_chord_size` asked
it by reading a `type` field off two staves — so for four independent voices it
found chords in 39 of Bach's 470 movements and reported 0.171 for the rest,
which is not a size. It reported 0.000 for Palestrina: zero chords, for music
that is nothing but vertical sonorities.

More than half of Bach's notes and 55% of Palestrina's live in the INNER
streams, which that measure never read at all.

A chorale's chords are alignments ACROSS streams. Reconstructing each stream's
onsets and asking how many pitches sound at each attack has the same meaning for
a piano chord and for four voices arriving together, which is the point.
"""

from __future__ import annotations

import itertools

import pytest

from scales.corpus_metrics import sonority_metrics


def _bar(**streams):
    return {name: list(events) for name, events in streams.items()}


def _n(pitch, dur):
    return {"type": "note", "pitch": pitch, "dur": dur}


def test_four_voices_arriving_together_are_a_four_note_sonority():
    """The case the old measure scored as zero."""
    bar = _bar(
        rh_display=[_n("G5", 1.0)],
        rh_inner_display=[_n("D5", 1.0)],
        lh_inner_display=[_n("B4", 1.0)],
        lh_display=[_n("G3", 1.0)],
    )
    result = sonority_metrics([bar])
    assert result["mean_sonority"] == 4.0, result
    assert result["chorded_attack_pct"] == 100.0, result


def test_a_notated_chord_and_four_voices_measure_the_same():
    """The whole point: one question, both kinds of writing."""
    voices = _bar(
        rh_display=[_n("G5", 1.0)],
        rh_inner_display=[_n("D5", 1.0)],
        lh_display=[_n("B3", 1.0)],
    )
    chord = _bar(
        rh_display=[{"type": "chord", "pitches": ["G5", "D5", "B3"], "dur": 1.0}],
    )
    assert sonority_metrics([voices])["mean_sonority"] == 3.0
    assert sonority_metrics([chord])["mean_sonority"] == 3.0


def test_a_single_line_is_a_sonority_of_one():
    bar = _bar(rh_display=[_n("C5", 1.0), _n("D5", 1.0), _n("E5", 1.0)])
    result = sonority_metrics([bar])
    assert result["mean_sonority"] == 1.0
    assert result["chorded_attack_pct"] == 0.0
    assert result["attacks"] == 3


def test_rests_and_graces_take_no_part():
    """A grace takes no metric time, and a rest is not a pitch."""
    bar = _bar(
        rh_display=[{"type": "rest", "dur": 1.0}, _n("C5", 1.0)],
        lh_display=[
            {"type": "note", "pitch": "B2", "dur": 0.0, "is_grace": True},
            {"type": "note", "pitch": "C3", "dur": 2.0},
        ],
    )
    result = sonority_metrics([bar])
    # The C3 spans the bar; only the C5 attack coincides with it.
    assert result["mean_sonority"] > 1.0
    assert result["attacks"] >= 2


def test_an_empty_bar_measures_nothing_rather_than_zero():
    assert sonority_metrics([])["attacks"] == 0
    assert sonority_metrics([_bar(rh_display=[{"type": "rest", "dur": 4.0}])])["attacks"] == 0


@pytest.mark.parametrize(
    "composer,floor",
    [("bach", 3.0), ("palestrina", 2.8), ("monteverdi", 2.5)],
)
def test_the_contrapuntal_composers_measure_as_polyphony(composer, floor):
    """Bach's chorales are in four parts and Palestrina's masses in four or
    five. Anything near 1 means the inner streams are being missed again."""
    from scales.composition_brief import _iter_corpus_bars

    bars = list(itertools.islice(_iter_corpus_bars(composer), 2000))
    if not bars:
        pytest.skip(f"no corpus for {composer}")
    result = sonority_metrics(bars)
    assert result["mean_sonority"] >= floor, (
        f"{composer} measures {result['mean_sonority']} voices — the old "
        f"`avg_chord_size` read {composer} as ~0 by looking at two staves only"
    )
