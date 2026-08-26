"""The ExpectationLedger, which had never held a single entry.

CLAUDE.md describes it as one of the system's core design principles — "the
system's working memory of unfinished musical business", carrying promises,
debts, cooldowns and locks across time so a piece can cohere at long range.

Measured on 2026-08-26: **no piece in the workspace contained a single ledger
entry.** Not one, across twelve pieces spanning five months.

The 2026-08-18 audit filed this as C21, "ledger population failures are
invisible" because of a bare `except Exception: pass`. That was a misdiagnosis
and worth stating plainly: nothing ever raised. Planning guards every write with
``if _cross_ledger is not None`` / ``elif _ledger is not None``, and a PieceGraph
has ``cross_scale_ledger = None`` and no ``expectation_ledger`` attribute at
all — so both guards are False for every section and nothing is ever recorded.
There was no ledger to populate.

A second defect sat behind it: even once a ledger exists, ``PieceGraph`` stores
the field as a **dict**, so a live object attached there is not what ``save``
expects. Promises recorded during planning would have been gone before
composition read them — which for a subsystem whose whole purpose is carrying
expectations across time is the same as not having one.
"""

import pytest

from scales.cross_scale_ledger import (
    CrossScaleLedger,
    ensure_ledger,
    ledger_is_empty,
    ledger_summary,
    persist_ledger,
)
from scales.enums import ExpectationDomain, ExpectationType
from scales.piece_graph import PieceGraph


def _promise(ledger, ref="theme_recap_after_m1_dev"):
    ledger.add_movement_expectation(
        exp_type=ExpectationType.PROMISE.value,
        domain=ExpectationDomain.MOTIF_THEME.value,
        object_ref=ref,
        introduced_at="m1_dev",
        expected_form="theme recapitulation",
        urgency=0.7,
        details={},
    )


# ─── The root cause ──────────────────────────────────────────────────────────


def test_a_fresh_graph_has_no_ledger_to_populate():
    """This is why nothing was ever recorded — both guards are False."""
    g = PieceGraph()
    assert getattr(g, "cross_scale_ledger", None) is None
    assert not hasattr(g, "expectation_ledger")
    assert ledger_is_empty(g)


def test_ensure_ledger_makes_one_exist():
    g = PieceGraph()
    ledger = ensure_ledger(g)
    assert isinstance(ledger, CrossScaleLedger)
    _promise(ledger)
    assert not ledger_is_empty(g)


def test_ensure_ledger_is_idempotent():
    g = PieceGraph()
    assert ensure_ledger(g) is ensure_ledger(g)


# ─── It has to survive the save ──────────────────────────────────────────────


def test_expectations_survive_a_save_and_load(tmp_path):
    g = PieceGraph()
    g.piece_id = "ledger-roundtrip"
    ledger = ensure_ledger(g)
    _promise(ledger)
    ledger.add_section_expectation(
        exp_type=ExpectationType.DEBT.value,
        domain=ExpectationDomain.CADENCE.value,
        object_ref="cadence_resolution_m1_a",
        introduced_at="m1_a",
        must_resolve_by="m1_a_p2",
        urgency=0.6,
        details={},
    )
    persist_ledger(g, ledger)

    path = tmp_path / "graph.json"
    g.save(str(path))
    loaded = PieceGraph.load(str(path))

    assert not ledger_is_empty(loaded)
    refs = {e.object_ref for e in ensure_ledger(loaded).get_all_open()}
    assert refs == {"theme_recap_after_m1_dev", "cadence_resolution_m1_a"}


def test_without_persist_the_ledger_does_not_reach_disk(tmp_path):
    """Pinning the reason `persist_ledger` has to be called before save."""
    g = PieceGraph()
    g.piece_id = "no-persist"
    _promise(ensure_ledger(g))
    # ensure_ledger seeds the field with an EMPTY dict at creation time, so
    # anything recorded afterwards is only in memory until persist runs.
    path = tmp_path / "graph.json"
    g.save(str(path))
    assert ledger_is_empty(PieceGraph.load(str(path)))


def test_the_graphs_field_stays_a_dict():
    """The field is typed as the serialized form; an object there breaks save."""
    g = PieceGraph()
    ensure_ledger(g)
    assert isinstance(g.cross_scale_ledger, dict)


def test_an_object_left_on_the_dict_field_is_recovered():
    """A caller that attached the object directly should still work."""
    g = PieceGraph()
    stray = CrossScaleLedger()
    _promise(stray)
    g.cross_scale_ledger = stray
    ledger = ensure_ledger(g)
    assert {e.object_ref for e in ledger.get_all_open()} == {"theme_recap_after_m1_dev"}
    assert isinstance(g.cross_scale_ledger, dict)


# ─── Reading it back ─────────────────────────────────────────────────────────


def test_the_summary_reads_a_freshly_loaded_graph(tmp_path):
    """Reading only the live object reported "no ledger" on a graph whose
    expectations had in fact survived."""
    g = PieceGraph()
    g.piece_id = "summary"
    ledger = ensure_ledger(g)
    _promise(ledger)
    persist_ledger(g, ledger)
    path = tmp_path / "graph.json"
    g.save(str(path))

    summary = ledger_summary(PieceGraph.load(str(path)))
    assert summary["attached"] is True
    assert summary["open"] == 1
    assert summary["by_scale"] == {"movement": 1}


def test_the_summary_of_a_graph_with_no_ledger_says_so():
    summary = ledger_summary(PieceGraph())
    assert summary["attached"] is False
    assert summary["open"] == 0
    assert "no ledger" in summary["note"]


def test_a_corrupt_stored_ledger_does_not_crash():
    g = PieceGraph()
    g.cross_scale_ledger = {"expectations": "not a list at all"}
    assert isinstance(ensure_ledger(g), CrossScaleLedger)
    ledger_summary(g)  # must not raise


@pytest.mark.parametrize(
    "scale_call",
    ["add_movement_expectation", "add_section_expectation", "add_work_expectation"],
)
def test_every_scale_records_and_survives(tmp_path, scale_call):
    g = PieceGraph()
    g.piece_id = f"scale-{scale_call}"
    ledger = ensure_ledger(g)
    getattr(ledger, scale_call)(
        exp_type=ExpectationType.PROMISE.value,
        domain=ExpectationDomain.MOTIF_THEME.value,
        object_ref=f"ref_{scale_call}",
        introduced_at="m1_a",
        urgency=0.5,
        details={},
    )
    persist_ledger(g, ledger)
    path = tmp_path / "g.json"
    g.save(str(path))
    refs = {e.object_ref for e in ensure_ledger(PieceGraph.load(str(path))).get_all_open()}
    assert f"ref_{scale_call}" in refs
