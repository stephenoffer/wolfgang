"""The brief must not assert frozen claims about the piece in front of it.

Its most emphatic section was headed "the five things this system has measurably
never done" and stated, with numbers, that the last generated score had ZERO
articulation marks, ZERO ties, and had never used `:arp` or `:ped`.

Measured against the very piece whose brief said it:

    articulation 19 · ties 2 · pedal 82 · arpeggiate 4

Four falsehoods, with numbers, in the section the composer is most likely to act
on. A brief that is wrong about the piece in front of it spends the credibility
of everything true around it — and ":ped never used" actively discourages the
pedal in a nocturne that is pedalled throughout.

The corpus ranges those claims were bundled with are real and stay. What is gone
is every assertion about generated output that a constant cannot know.
"""

from scales.composition_brief import _MINDSET, marks_so_far, render_marks_so_far
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph

FOSSILS = ("last generated score", "never yet used", "measurably never done")


def _graph(**marks) -> PieceGraph:
    ev = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural", **marks)
    layer = LayerIR(principal_line=[ev], bass_foundation=[], meter=(4, 4), key="C major")
    g = PieceGraph()
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(
            phrase_id="p1",
            section_id="m1_a",
            bar_start=1,
            bar_count=4,
            key="C major",
            meter=(4, 4),
            tempo_bpm=90,
        ),
        realized=layer,
        agent_authored=True,
    )
    return g


def test_the_brief_makes_no_frozen_claim_about_generated_output():
    for fossil in FOSSILS:
        assert fossil not in _MINDSET, f"{fossil!r} is a claim a constant cannot know"


def test_the_corpus_ranges_survive():
    """The numbers that ARE measurable stay — they were never the problem."""
    assert "0.11-5.71" in _MINDSET
    assert "24-49 semitones" in _MINDSET


def test_marks_are_counted_from_the_piece():
    counts = marks_so_far(_graph(articulation="staccato", pedal="down"))
    assert counts["articulation"] == 1
    assert counts["pedal"] == 1
    assert counts["tie"] == 0


def test_an_unused_mark_is_named_rather_than_assumed():
    line = " ".join(render_marks_so_far(_graph(articulation="staccato")))
    assert "arpeggio" in line and "Nothing in this piece has used" in line


def test_a_mark_in_use_is_not_reported_as_missing():
    line = " ".join(render_marks_so_far(_graph(technique="arpeggio")))
    assert "arpeggio 1" in line
    missing = line.split("has used:")[-1] if "has used:" in line else ""
    assert "arpeggio" not in missing


def test_the_first_phrase_says_so_instead_of_reporting_zeros():
    line = " ".join(render_marks_so_far(PieceGraph()))
    assert "first phrase" in line
