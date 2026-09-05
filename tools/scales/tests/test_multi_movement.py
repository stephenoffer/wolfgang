"""A multi-movement work must give each movement its own phrase namespace.

Every form spec hardcodes an `m1_` prefix. `build_form_graph` had no
`movement_id` parameter at all, so a second movement built into the same piece
produced ids that COLLIDED with the first and silently replaced them — a
sonata's `m1_a_p1` overwritten by a ternary's, 17 + 9 phrases arriving as 25.
CLAUDE.md documents `m2_a` as the convention; nothing could produce it.

`init_work` and `plan_movement` existed and recorded movements the whole time.
Only the realisation step could not tell them apart.
"""

from scales.models import StyleDNA
from scales.scales import _build_sonata, _build_ternary


def test_the_default_movement_is_unchanged():
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    assert all(s.section_id.startswith("m1_") for s in slots)


def test_a_second_movement_gets_its_own_namespace():
    slots = _build_ternary("C major", 60, (3, 4), StyleDNA(), movement_id="m2")
    assert slots
    assert all(s.section_id.startswith("m2_") for s in slots)
    assert all(s.phrase_id.startswith("m2_") for s in slots)


def test_two_movements_do_not_collide():
    m1 = _build_sonata("G major", 132, (4, 4), StyleDNA(), movement_id="m1")
    m2 = _build_ternary("C major", 60, (3, 4), StyleDNA(), movement_id="m2")
    ids = [s.phrase_id for s in m1] + [s.phrase_id for s in m2]
    assert len(ids) == len(set(ids)), "movement phrase ids collide"


def test_each_movement_keeps_its_own_meter_and_key():
    m2 = _build_ternary("C major", 60, (3, 4), StyleDNA(), movement_id="m2")
    assert all(tuple(s.meter) == (3, 4) for s in m2)
    assert any("C" in (s.key or "") for s in m2)


def test_the_work_home_key_is_the_first_movements_key():
    """`init_work` runs before any movement or phrase exists, so it can only
    default — a three-movement sonatina in G major recorded a home key of "C"."""
    import shutil

    from scales.piece_graph import PieceGraph
    from scales.scales import compile_style, init_work, init_workspace, plan_movement

    pid = "_test_work_home_key"
    shutil.rmtree(f"workspace/{pid}", ignore_errors=True)
    init_workspace(pid, mode="compose_from_text", description="A sonatina in G major for piano")
    compile_style(pid, composers=["haydn"])
    init_work(pid, movement_count=2, description="x")
    plan_movement(pid, movement_id="m1", form="sonata", key="G major")
    plan_movement(pid, movement_id="m2", form="ternary", key="C major")
    wg = PieceGraph.load(f"workspace/{pid}/piece_graph.json").work_graph
    assert wg.tonal_itinerary.home_key == "G major", wg.tonal_itinerary.home_key
    shutil.rmtree(f"workspace/{pid}", ignore_errors=True)
