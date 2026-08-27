"""Every movement of a work occupies its own bars.

`_build_from_spec` started its bar cursor at 1 for every movement, so a
three-movement work laid all three on top of one another. The assembler collects
events by absolute bar number, so movement I's bar 1, movement II's bar 1 and
movement III's bar 1 all became bar 1 of the score. Measured on a real
three-movement graph: **34 of 41 bars overfull**, a 2/4 bar carrying 8 beats, the
metre flip-flopping 2/4, 3/4, 4/4, 2/4 down the page, and three final barlines
inside the score.

The movement-heading and movement-barline machinery in the assembler was written
assuming bar numbers are globally unique — which they were, right up until a
second movement existed. This is the shape catalogued as "an assumption true
when written that stops being true because the system grew".
"""

from __future__ import annotations

import shutil

import pytest

from scales.scales import _WORKSPACE, build_form_graph, init_workspace

_PLAN = [
    ("m1", "binary", "C major", (4, 4), 120),
    ("m2", "ternary", "F major", (3, 4), 66),
    ("m3", "theme_variations", "C major", (2, 4), 138),
]


@pytest.fixture
def three_movements():
    piece = "test-movements-20260827"
    shutil.rmtree(_WORKSPACE / piece, ignore_errors=True)
    init_workspace(
        piece,
        "compose_from_text",
        "movement layout probe",
        {"target": {"instrumentation": "solo_piano"}},
    )
    spans = {}
    for mid, form, key, meter, tempo in _PLAN:
        rows = build_form_graph(piece, form, key, tempo_bpm=tempo, meter=meter, movement_id=mid)
        bars = [r["bars"] for r in rows if "bars" in r]
        spans[mid] = (
            min(int(b.split("-")[0]) for b in bars),
            max(int(b.split("-")[1]) for b in bars),
        )
    yield piece, spans
    shutil.rmtree(_WORKSPACE / piece, ignore_errors=True)


def test_movements_are_laid_out_end_to_end(three_movements):
    _, spans = three_movements
    assert spans["m1"][0] == 1
    assert spans["m2"][0] == spans["m1"][1] + 1, spans
    assert spans["m3"][0] == spans["m2"][1] + 1, spans


def test_no_bar_is_claimed_by_two_phrases(three_movements):
    """The direct statement of the defect: a bar belongs to exactly one phrase."""
    import collections

    from scales.piece_graph import PieceGraph

    piece, _ = three_movements
    graph = PieceGraph.load(str(_WORKSPACE / piece / "piece_graph.json"))
    occupied = collections.Counter()
    for ps in graph.phrases.values():
        for bar in range(ps.slot.bar_start, ps.slot.bar_start + ps.slot.bar_count):
            occupied[bar] += 1
    shared = {bar: n for bar, n in occupied.items() if n > 1}
    assert not shared, f"bars claimed by more than one phrase: {sorted(shared.items())[:10]}"


def test_a_variations_movement_gets_its_own_section_namespace(three_movements):
    """`_build_theme_variations` alone never passed `movement_id` down.

    So a variations movement placed second or third built `m1_theme` and
    `m1_var1` section ids — colliding with movement I's namespace, which is
    exactly the collision `_build_from_spec`'s prefix rewrite exists to prevent.
    """
    from scales.piece_graph import PieceGraph

    piece, _ = three_movements
    graph = PieceGraph.load(str(_WORKSPACE / piece / "piece_graph.json"))
    sections = {ps.slot.section_id for ps in graph.phrases.values()}
    assert "m3_theme" in sections, sorted(sections)
    assert not any(s.startswith("m1_var") or s == "m1_theme" for s in sections), sorted(sections)


def test_rebuilding_a_middle_movement_puts_it_back_where_it_was(three_movements):
    """Not after the finale — the offset counts LOWER-numbered movements only."""
    piece, spans = three_movements
    rows = build_form_graph(
        piece, "ternary", "F major", tempo_bpm=66, meter=(3, 4), movement_id="m2"
    )
    bars = [r["bars"] for r in rows if "bars" in r]
    assert min(int(b.split("-")[0]) for b in bars) == spans["m2"][0]


def test_a_rebuild_that_changes_length_says_so(three_movements):
    """Two things go stale and neither is visible downstream."""
    piece, _ = three_movements
    rows = build_form_graph(
        piece, "sonata", "F major", tempo_bpm=66, meter=(3, 4), movement_id="m2"
    )
    warnings = {r["warning"]: r for r in rows if "warning" in r}
    assert "stale_phrases_from_previous_layout" in warnings, sorted(warnings)
    assert warnings["stale_phrases_from_previous_layout"]["phrase_ids"], "named nothing"
    assert "later_movements_now_overlap" in warnings, sorted(warnings)
    assert warnings["later_movements_now_overlap"]["overlapping"] == ["m3"]


def test_a_rebuilt_movement_appears_once_in_the_form_graph(three_movements):
    """`form.movements.append` grew a duplicate MovementSpec on every replan."""
    from scales.piece_graph import PieceGraph

    piece, _ = three_movements
    build_form_graph(piece, "ternary", "F major", tempo_bpm=66, meter=(3, 4), movement_id="m2")
    graph = PieceGraph.load(str(_WORKSPACE / piece / "piece_graph.json"))
    ids = [m.id for m in graph.form.movements]
    assert ids == sorted(set(ids), key=ids.index), ids
    assert ids.count("m2") == 1, ids
