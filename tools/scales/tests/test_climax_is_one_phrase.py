"""Only one phrase may be told it is the climax.

`PhraseSlot.climax_distance` defaults to 0, and 0 MEANS "this phrase is the
climax", so any phrase the dramatic planner never touched claimed the peak of
the whole piece. Measured across `workspace/`: **nine pieces in which every
phrase was told it was the climax** — 9 of 9 in the F major andante, 56 of 56 in
the seasons sonata, and two of the nine were created the same day.

The brief tells such a phrase it "must be the highest, densest, most
harmonically charged moment ... write the peak". A piece where every phrase is
written that way has no arc at all, which is the exact failure the dramatic
planner was built to fix.
"""

from scales.composition_brief import _dramatic_brief
from scales.models import PhraseSlot, StyleDNA
from scales.scales import _build_ternary


def _slot(**kw):
    base = dict(
        phrase_id="p1",
        section_id="m1_a",
        bar_start=1,
        bar_count=4,
        key="C major",
        meter=(4, 4),
        tempo_bpm=90,
    )
    base.update(kw)
    return PhraseSlot(**base)


def test_an_unplanned_phrase_is_not_told_it_is_the_climax():
    text = " ".join(_dramatic_brief(_slot()))
    assert "CLIMAX of the whole piece" not in text


def test_an_unplanned_phrase_is_told_that_it_has_no_plan():
    """Silence would let the composer assume; the honest thing is to say the
    plan is missing."""
    text = " ".join(_dramatic_brief(_slot())).lower()
    assert "no dramatic plan" in text
    assert "do not assume this is the climax" in text


def test_a_planned_climax_still_gets_the_full_instruction():
    text = " ".join(_dramatic_brief(_slot(dramatic_role="intensify", climax_distance=0)))
    assert "CLIMAX of the whole piece" in text


def test_a_planned_phrase_before_the_peak_is_told_to_hold_back():
    text = " ".join(_dramatic_brief(_slot(dramatic_role="establish", climax_distance=-3)))
    assert "before the piece's climax" in text
    assert "CLIMAX of the whole piece" not in text


def test_a_real_plan_names_exactly_one_climax():
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    from scales import dramatic_plan

    dramatic_plan.build(slots)
    peaks = [s for s in slots if " ".join(_dramatic_brief(s)).count("CLIMAX of the whole piece")]
    assert len(peaks) == 1


def _work_graph(n_movements: int):
    """A graph whose work has `n` movements, for scoping the climax claim."""
    from scales.models import MovementContract
    from scales.piece_graph import PieceGraph

    graph = PieceGraph()

    class _Work:
        movements = [MovementContract(id=f"m{i}") for i in range(1, n_movements + 1)]

    if n_movements:
        graph.work_graph = _Work()
    return graph


def test_a_single_movement_piece_still_says_whole_piece():
    text = " ".join(
        _dramatic_brief(_slot(dramatic_role="intensify", climax_distance=0), _work_graph(0))
    )
    assert "CLIMAX of the whole piece" in text


def test_a_multi_movement_work_scopes_the_claim_to_the_movement():
    """The dramatic plan runs PER MOVEMENT, so a three-movement work produced
    three phrases each told they were the peak of everything — with two whole
    movements still to come after the first of them. "Everything after subsides
    from it" is simply false there."""
    text = " ".join(
        _dramatic_brief(_slot(dramatic_role="intensify", climax_distance=0), _work_graph(3))
    )
    assert "CLIMAX of the MOVEMENT" in text
    assert "CLIMAX of the whole piece" not in text


def test_it_says_the_works_apex_is_undecided():
    """`WorkGraph.climax_reservations` exists and nothing fills it, so the brief
    must not imply the question has been answered somewhere."""
    text = " ".join(
        _dramatic_brief(_slot(dramatic_role="intensify", climax_distance=0), _work_graph(3))
    )
    assert "not recorded anywhere" in text


def test_the_approach_lines_are_scoped_too():
    text = " ".join(
        _dramatic_brief(_slot(dramatic_role="establish", climax_distance=-3), _work_graph(3))
    )
    assert "before this movement's climax" in text
