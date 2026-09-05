"""A score must be engraved the right way up.

The generic staff names `treble` and `bass` sat at ranks 29 and 30 in
`_SCORE_ORDER`, so `_score_order` put the BASS staff on top. A four-voice motet
engraved upside down, carried no clefs at all, and every analysis that indexes
`melody_staff=0` — voicing poverty, register stasis, scalar overuse, melody
buried — read the bass line as the melody. `detect_melody_buried` reported the
top voice as covered in 100% of bars, which was true of the file and false of
the music.

Piano pieces were unaffected: that path builds its two staves explicitly.
"""

import pytest

from scales.assembler import _SCORE_ORDER, _score_order


def test_the_treble_staff_ranks_above_the_bass():
    order = list(_SCORE_ORDER)
    assert order.index("treble") < order.index("bass")


def test_score_order_puts_treble_first():
    assert _score_order({"bass": [], "treble": []}) == ["treble", "bass"]


def test_an_explicit_ensemble_order_still_wins():
    """A named ensemble supplies its own score order and must not be reordered."""
    got = _score_order({"cello": [], "violin": []}, ensemble=["cello", "violin"])
    assert got == ["cello", "violin"]


def test_orchestral_ranking_is_unchanged():
    order = list(_SCORE_ORDER)
    for higher, lower in (("flute", "oboe"), ("oboe", "clarinet"), ("violin", "cello")):
        assert order.index(higher) < order.index(lower), (higher, lower)


def test_a_choral_score_engraves_treble_first_with_clefs():
    """End to end, because the ordering bug was only visible in the file."""
    from music21 import converter, note

    from scales.assembler import assemble
    from scales.piece_graph import PieceGraph

    path = "workspace/palestrina-motet-dorian-20260826/piece_graph.json"
    import os

    if not os.path.exists(path):
        pytest.skip("motet workspace not present")
    s = converter.parse(assemble(PieceGraph.load(path)))
    assert len(s.parts) >= 2
    tops = []
    for p in s.parts:
        clefs = {type(c).__name__ for c in p.recurse().getElementsByClass("Clef")}
        assert clefs, f"part {p.partName!r} carries no clef"
        pitches = [
            n.pitch.midi if isinstance(n, note.Note) else max(x.midi for x in n.pitches)
            for n in p.recurse().notes
        ]
        tops.append(max(pitches))
    assert tops[0] > tops[-1], "the first part must be the highest-sounding staff"
