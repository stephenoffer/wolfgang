"""A phrase in the slow movement should know it is in the slow movement.

`plan_movement` stores `role_in_work`, `character` and `tempo_marking` on a
`MovementContract`. **Nothing has ever read any of them.** `composition_brief`
contains no reference to `work_graph` or `MovementContract` at all, so a phrase
in the second movement of a symphony got a brief indistinguishable in kind from
one in the opening allegro:

    m1 (opening allegro)   mentions its role: False | its character: False
    m2 (slow movement)     mentions its role: False | its character: False

For a multi-movement work that is the largest single piece of context there is,
and it was sitting on the graph unused — the same "written, never read" shape as
`forward_context` (Addendum 60) and the section goals (Addendum 62).
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.composition_brief import _movement_brief
from scales.models import MovementContract, PhraseSlot
from scales.piece_graph import PieceGraph
from scales.scales import (
    build_form_graph,
    compile_style,
    get_composition_brief,
    init_work,
    init_workspace,
    plan_movement,
)

PID = "_movement_identity_probe"


@pytest.fixture
def work():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="A sonatina in G major")
    compile_style(PID, composers=["haydn"])
    init_work(PID, movement_count=2, emotional_narrative="bright then songful",
              finale_payoff="the opening idea returns transformed")
    plan_movement(PID, "m1", form="sonata", key="G major", tempo_bpm=132,
                  character="bright and athletic", role_in_work="opening allegro",
                  tempo_marking="Allegro")
    plan_movement(PID, "m2", form="ternary", key="C major", tempo_bpm=60,
                  character="a songful lament", role_in_work="slow movement",
                  tempo_marking="Adagio")
    build_form_graph(PID, form="sonata", key="G major", tempo_bpm=132, meter=(4, 4), movement_id="m1")
    build_form_graph(PID, form="ternary", key="C major", tempo_bpm=60, meter=(3, 4), movement_id="m2")
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_the_slow_movement_says_so(work):
    text = get_composition_brief(work, "m2_a_p1", composer="haydn")
    assert "slow movement" in text
    assert "songful lament" in text
    assert "MOVEMENT 2 of 2" in text


def test_the_two_movements_are_told_different_things(work):
    graph = PieceGraph.load(str(scales_mod._WORKSPACE / work / "piece_graph.json"))
    first_m1 = next(
        pid for pid, ps in graph.phrases.items()
        if ps.slot and ps.slot.section_id.startswith("m1_")
    )
    a = get_composition_brief(work, first_m1, composer="haydn")
    b = get_composition_brief(work, "m2_a_p1", composer="haydn")
    assert "opening allegro" in a and "opening allegro" not in b
    assert "slow movement" in b and "slow movement" not in a


def test_a_single_movement_piece_gets_no_orientation():
    """Falsification: "MOVEMENT 1 of 1" is noise, not context."""
    graph = PieceGraph()
    slot = PhraseSlot(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=4,
                      key="C major", meter=(4, 4), tempo_bpm=90)
    assert _movement_brief(graph, slot) == []


def test_a_movement_with_nothing_planned_says_nothing():
    """An id alone is not context — without a role, character or marking there
    is nothing worth a line."""
    graph = PieceGraph()

    class _Work:
        movements = [MovementContract(id="m1"), MovementContract(id="m2")]

    graph.work_graph = _Work()
    slot = PhraseSlot(phrase_id="p1", section_id="m2_a", bar_start=1, bar_count=4,
                      key="C major", meter=(4, 4), tempo_bpm=90)
    assert _movement_brief(graph, slot) == []


def test_the_works_narrative_reaches_every_movement(work):
    """`init_work` stores `emotional_narrative` and nothing read it. A movement
    composed without the work's arc is a piece that happens to be third in a
    folder."""
    graph = PieceGraph.load(str(scales_mod._WORKSPACE / work / "piece_graph.json"))
    for mid in ("m1", "m2"):
        pid = next(
            p for p, ps in graph.phrases.items()
            if ps.slot and ps.slot.section_id.startswith(mid + "_")
        )
        assert "THE WHOLE WORK" in get_composition_brief(work, pid, composer="haydn")


def test_only_the_last_movement_is_told_what_it_must_pay_off(work):
    """A payoff handed to the opening allegro is an instruction to spend the
    ending early."""
    graph = PieceGraph.load(str(scales_mod._WORKSPACE / work / "piece_graph.json"))

    def brief_for(mid):
        pid = next(
            p for p, ps in graph.phrases.items()
            if ps.slot and ps.slot.section_id.startswith(mid + "_")
        )
        return get_composition_brief(work, pid, composer="haydn")

    assert "MUST PAY OFF" not in brief_for("m1")
    assert "MUST PAY OFF" in brief_for("m2")


def test_a_movement_away_from_home_is_told_the_distance(work):
    """The home key is written by `plan_movement` with a comment about the bug
    where a G major sonatina recorded "C" — and had no reader at all, so the
    "later question about where the work lives" was never asked."""
    graph = PieceGraph.load(str(scales_mod._WORKSPACE / work / "piece_graph.json"))
    pid = next(
        p for p, ps in graph.phrases.items()
        if ps.slot and ps.slot.section_id.startswith("m2_")
    )
    text = get_composition_brief(work, pid, composer="haydn")
    assert "home key is G major" in text
    assert "this movement is in C major" in text


def test_a_movement_at_home_is_not_told_a_distance(work):
    """Falsification: the first movement IS the home key, so there is no
    distance to report and reporting one would be noise."""
    graph = PieceGraph.load(str(scales_mod._WORKSPACE / work / "piece_graph.json"))
    pid = next(
        p for p, ps in graph.phrases.items()
        if ps.slot and ps.slot.section_id.startswith("m1_")
    )
    assert "home key is" not in get_composition_brief(work, pid, composer="haydn")
