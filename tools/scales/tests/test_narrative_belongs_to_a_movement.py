"""A narrative section must belong to a movement, because bars restart.

`NarrativeSection` carried a bar range and no movement. Bar numbers restart per
movement, so a phrase at bar 1 of movement two matched a section covering bars
1-8 of movement ONE and was handed the wrong movement's CREATIVE INTENT — the
one line the phrase-composer is told to start from:

    m2 phrase m2_a_p1 (bar 1)
    inherits movement 1's narrative: True

`movement_id` is empty by default, which is what every single-movement piece
wants and what every graph already on disk holds. For those, matching is
unchanged.
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.composition_brief import _narrative_section_for
from scales.models import NarrativeArc, NarrativeSection, PhraseSlot
from scales.piece_graph import PieceGraph
from scales.scales import (
    build_form_graph,
    compile_style,
    init_work,
    init_workspace,
    plan_movement,
    save_narrative,
)

PID = "_narrative_movement_probe"


def _graph_with(sections):
    g = PieceGraph()
    g.narrative = NarrativeArc(sections=sections)
    return g


def _slot(section_id, bar):
    return PhraseSlot(phrase_id=f"{section_id}_p1", section_id=section_id, bar_start=bar,
                      bar_count=4, key="C major", meter=(4, 4), tempo_bpm=90)


def test_a_section_naming_its_movement_matches_only_that_one():
    g = _graph_with([
        NarrativeSection(id="a", movement_id="m1", bar_start=1, bar_end=8, character="ONE"),
        NarrativeSection(id="b", movement_id="m2", bar_start=1, bar_end=8, character="TWO"),
    ])
    assert _narrative_section_for(g, _slot("m1_a", 1)).character == "ONE"
    assert _narrative_section_for(g, _slot("m2_a", 1)).character == "TWO"


def test_an_unattributed_section_still_matches_anything():
    """Every graph already on disk has no movement_id, and every
    single-movement piece never will."""
    g = _graph_with([NarrativeSection(id="a", bar_start=1, bar_end=8, character="ONE")])
    assert _narrative_section_for(g, _slot("m1_a", 1)).character == "ONE"


def test_an_id_prefix_is_honoured_when_the_field_is_unset():
    """Narratives written before the field existed often named the movement in
    the id — `"m2_open"` — and that should still resolve."""
    g = _graph_with([
        NarrativeSection(id="m1_open", bar_start=1, bar_end=8, character="ONE"),
        NarrativeSection(id="m2_open", bar_start=1, bar_end=8, character="TWO"),
    ])
    assert _narrative_section_for(g, _slot("m2_a", 1)).character == "TWO"


def test_a_phrase_outside_every_range_matches_nothing():
    g = _graph_with([NarrativeSection(id="a", movement_id="m1", bar_start=1, bar_end=8)])
    assert _narrative_section_for(g, _slot("m1_a", 99)) is None


@pytest.fixture
def work():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="A sonatina in G major")
    compile_style(PID, composers=["haydn"])
    init_work(PID, movement_count=2, emotional_narrative="x")
    plan_movement(PID, "m1", form="ternary", key="G major")
    plan_movement(PID, "m2", form="ternary", key="C major")
    build_form_graph(PID, form="ternary", key="G major", tempo_bpm=132, meter=(4, 4), movement_id="m1")
    build_form_graph(PID, form="ternary", key="C major", tempo_bpm=60, meter=(3, 4), movement_id="m2")
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_saving_an_unattributed_section_warns_in_a_multi_movement_work(work):
    result = save_narrative(work, sections=[{"id": "open", "bar_start": 1, "bar_end": 8,
                                             "character": "x"}])
    assert result["sections_with_no_movement_id"]
    assert "bar numbers restart" in result["warning"]


def test_attributed_sections_do_not_warn(work):
    """Falsification — the warning must be silent on a correct narrative."""
    result = save_narrative(work, sections=[
        {"id": "a", "movement_id": "m1", "bar_start": 1, "bar_end": 8, "character": "one"},
        {"id": "b", "movement_id": "m2", "bar_start": 1, "bar_end": 8, "character": "two"},
    ])
    assert not result["warning"]


def test_the_curve_mapper_uses_the_right_movements_section():
    """`_apply_narrative_curves` maps a section's energy/tension/density/
    brightness onto a slot — the curves that drive dynamics, density targets and
    the tempo arc. It matched by bar range alone, so a movement-two slot could
    be shaped by movement one's arc."""
    from scales.scales import _apply_narrative_curves

    nar = NarrativeArc(sections=[
        NarrativeSection(id="a", movement_id="m1", bar_start=1, bar_end=8, energy_curve=[1.0, 1.0]),
        NarrativeSection(id="b", movement_id="m2", bar_start=1, bar_end=8, energy_curve=[0.1, 0.1]),
    ])
    for mid, expect in (("m1", 1.0), ("m2", 0.1)):
        slot = _slot(f"{mid}_a", 1)
        assert _apply_narrative_curves(slot, nar)
        assert abs(slot.curves.energy[0] - expect) < 0.01


def test_there_is_exactly_one_movement_predicate():
    """Two copies of this rule drifting apart is the failure
    `project_one_parser_one_loader` records as this repo's most expensive, and
    it had two consumers before one existed at all."""
    import ast
    import pathlib

    from scales import models

    root = pathlib.Path(models.__file__).parent
    definitions = []
    for path in root.rglob("*.py"):
        if "test" in str(path):
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and "is_in_movement" in node.name:
                definitions.append(f"{path.name}:{node.name}")
    assert definitions == ["models.py:narrative_section_is_in_movement"], definitions
    # Callable rather than `inspect.getsource`, which resolves line numbers
    # recorded at import time and returns another function's text once the file
    # is edited. The claim here is that the one definition WORKS, and calling it
    # is a better check of that than reading its source at all.
    assert callable(models.narrative_section_is_in_movement)
