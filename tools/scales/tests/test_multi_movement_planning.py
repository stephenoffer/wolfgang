"""Planning a movement twice made every brief in the work count wrong.

Found by planning a two-movement sonatina end to end. Three defects, all on the
multi-movement entry path, all of the shape "a tool quietly accepted or did
something other than what the caller meant":

1. `init_work(piece_id, movement_count)` declares `movement_count: int` and never
   checked it. Called the way every neighbouring tool is called —
   `init_work(pid, "compose_from_text")`, with the MODE second, which is what
   `init_workspace` takes — it stored the string as the movement count and
   echoed it back without complaint.

2. `plan_movement` takes `form`, `key`, `tempo_bpm` and `meter` — every argument
   `build_form_graph` needs — and creates NO phrases. A caller who stops there
   has a work with two planned movements and nothing to compose, and the return
   said nothing about it.

3. `plan_movement` APPENDED. Planning a movement twice — which is what revising
   one looks like, and what happens the moment a call is corrected and rerun —
   left `['m1', 'm2', 'm1']`, and every brief in the piece then opened
   "MOVEMENT 1 of 3" for a two-movement work, because the count is the length of
   that list.
"""

from __future__ import annotations

import pytest

from scales import scales as S


@pytest.fixture
def work(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "_WORKSPACE", tmp_path)
    pid = "mm-probe"
    S.init_workspace(pid, "compose_from_text", description="a two-movement sonatina")
    return pid


def test_the_mode_in_the_count_position_is_refused(work):
    got = S.init_work(work, "compose_from_text")
    assert "error" in got
    assert "movement_count" in got["error"] and "init_workspace" in got["error"]


def test_a_count_below_one_is_refused(work):
    assert "error" in S.init_work(work, 0)


def test_a_numeric_string_is_accepted(work):
    assert S.init_work(work, "3").get("movement_count") == 3


def test_plan_movement_says_it_created_no_phrases(work):
    S.init_work(work, 2)
    got = S.plan_movement(work, "m1", "binary", "A minor", tempo_bpm=132, meter=(2, 4))
    assert got["phrases_created"] == 0
    assert "build_form_graph" in got["next"]


def test_replanning_a_movement_revises_it_rather_than_duplicating(work):
    S.init_work(work, 2)
    S.plan_movement(work, "m1", "binary", "A minor", character="terse")
    S.plan_movement(work, "m2", "ternary", "C major", character="consoling")
    S.plan_movement(work, "m1", "binary", "A minor", character="terse and driven")

    graph = S._load_graph(work)
    assert [m.id for m in graph.work_graph.movements] == ["m1", "m2"]
    assert graph.work_graph.movements[0].character == "terse and driven"


def test_a_list_already_duplicated_by_an_earlier_run_is_healed(work):
    """Existing workspaces carry the duplicate; stopping new ones is not enough."""
    from scales.models import MovementContract

    S.init_work(work, 2)
    graph = S._load_graph(work)
    graph.work_graph.movements = [
        MovementContract(id="m1", form="binary", key="A minor"),
        MovementContract(id="m2", form="ternary", key="C major"),
        MovementContract(id="m1", form="binary", key="A minor"),
    ]
    graph.save(str(S._WORKSPACE / work / "piece_graph.json"))

    S.plan_movement(work, "m2", "ternary", "C major", character="consoling")
    healed = S._load_graph(work)
    assert [m.id for m in healed.work_graph.movements] == ["m1", "m2"]


def test_the_first_movements_key_is_the_works_home_key(work):
    """Guards the neighbouring rule: replacing rather than appending must not
    break the `len(movements) == 1` test that records the home key."""
    S.init_work(work, 2)
    S.plan_movement(work, "m1", "binary", "A minor")
    S.plan_movement(work, "m2", "ternary", "C major")
    graph = S._load_graph(work)
    assert graph.work_graph.tonal_itinerary.home_key == "A minor"
