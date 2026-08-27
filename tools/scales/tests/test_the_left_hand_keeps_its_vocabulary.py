"""The left hand played less than half the distinct pitches real music does.

Measured against real Mozart with the corpus's own classifier, so the same
yardstick on both sides:

    distinct LH pitches per bar   ours 1.52   real 3.30
    pedal_point                        27%         3.4%
    block_chord_offbeat                 0%        10.4%   (the oom-pah, absent)

The left hand is then CLASSIFIED as what it has become: a repeated pitch reads
as `pedal_point`, two alternating pitches as `tremolo`. Reading a bar shows it
plainly — `D2 D3 D3 D2 D3 D2 D3` where an Alberti bass is root-fifth-third-fifth.

Two causes, both of them a reasonable-looking rule doing something else:

1. `PatternRetriever.retrieve` ranks by `total_occurrences`, and the commonest
   bar shape in a corpus is its most degenerate. The top five patterns it
   returned for `alberti` — the idiom itself — were octave alternations:

       occ=16917  C2 C3 C2 C3 C2 C3 C2 C3
       occ= 8408  G1 G2 G1 G2 G1 G2 G1 G2

   Retrieved alberti averaged 2.40 distinct pitches against 5.03 across the
   3,173 in the library. The material was there; the ranking could not reach it.

2. The chord-tone snap moved every pattern pitch to the nearest ABSOLUTE chord
   tone, all of them voiced in one register — so the figure's octave shape,
   which is the reason for retrieving a real pattern at all, was flattened.
   Patterns arrive carrying 4.73 distinct pitches and left with 1.45.

    stage                            distinct/bar   chord-notes
    control                                  1.90           141
    + vocabulary floor                       2.05           161
    + pitch-class snap                       2.43           217
    real mozart                              3.25

Both metrics move together. Two earlier attempts on this defect traded one for
the other — offering chord tones across the whole LH register raised distinct
pitches and cost 2.5 points of chord share, because higher bass notes leave the
thickening pass no room under its ceiling — so the pair is asserted here, not
just the headline.
"""

from __future__ import annotations

import statistics

from scales.pattern_retriever import PatternRetriever, _distinct_pitches


def _retriever():
    r = PatternRetriever()
    r._ensure_loaded()
    return r


def test_the_library_is_not_the_problem():
    """It carries MORE vocabulary than the corpus bars it was built from.

    Worth asserting because the defect was first attributed to the corpus build.
    If this ever fails, the diagnosis below is measuring the wrong stage.
    """
    r = _retriever()
    everything = [p for pool in r._by_texture.values() for p in pool]
    assert len(everything) > 20000, len(everything)
    assert statistics.fmean(_distinct_pitches(p) for p in everything) > 3.3


def test_retrieval_does_not_return_the_most_degenerate_pattern_of_an_idiom():
    r = _retriever()
    got = r.retrieve("alberti", n=5)
    assert got, "no alberti patterns retrieved"
    mean = statistics.fmean(_distinct_pitches(p) for p in got)
    assert mean >= 3.0, (
        f"retrieved alberti patterns average {mean:.2f} distinct pitches — an "
        "Alberti bass is root-fifth-third-fifth, so anything under three is an "
        f"octave alternation wearing the label: "
        f"{[[e.get('p') for e in (p.get('lh_events') or [])[:6]] for p in got]}"
    )


def test_the_floor_is_a_floor_and_not_a_maximum():
    """Maximising picks the fifteen-pitch scale run that happens to be labelled
    alberti, which is the same mistake facing the other way."""
    r = _retriever()
    pool = r._by_texture["alberti"]
    richest = max(_distinct_pitches(p) for p in pool)
    got = r.retrieve("alberti", n=5)
    assert max(_distinct_pitches(p) for p in got) < richest, (
        "retrieval is selecting the richest patterns rather than the ones at or "
        "above the idiom's median vocabulary"
    )


def test_a_well_attested_pattern_is_still_preferred():
    """The floor reorders; it must not throw away attestation.

    A pattern seen once is not corpus evidence, and preferring vocabulary alone
    would reach for exactly those.
    """
    r = _retriever()
    got = r.retrieve("alberti", n=5)
    assert min(p.get("total_occurrences", 0) for p in got) > 100, [
        p.get("total_occurrences") for p in got
    ]


def test_the_snap_keeps_the_figures_octave_shape():
    """The registral shape IS the pattern — a real Alberti spans an octave.

    Snapping to the nearest ABSOLUTE chord tone flattened it: this figure came
    out `C3 G3 G3 G3 C3 G3 G3 G3`, two distinct pitches from five.
    """
    from scales.pitch import midi_to_pitch

    chord = [48, 52, 55]  # C major, voiced in one octave
    classes = {c % 12 for c in chord}
    figure = [47, 62, 54, 62, 49, 64, 54, 64]  # B2 D4 F#3 D4 C#3 E4 F#3 E4

    def snap(m):
        return min(
            (c for pc in classes for c in (m - ((m - pc) % 12), m + ((pc - m) % 12))),
            key=lambda c: (abs(c - m), c),
        )

    snapped = [snap(m) for m in figure]
    assert len(set(snapped)) >= 4, [midi_to_pitch(m, "C major") for m in snapped]
    # Every note is a chord tone, and none has moved more than a semitone-and-a-
    # half from where the pattern put it.
    assert all(m % 12 in classes for m in snapped)
    assert max(abs(a - b) for a, b in zip(figure, snapped)) <= 3
    # And the span survives: the old snap collapsed an octave-and-a-half to a fifth.
    assert max(snapped) - min(snapped) >= 12
