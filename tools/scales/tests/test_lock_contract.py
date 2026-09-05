"""The modes whose whole contract is a lock policy must state it.

CLAUDE.md describes the six composition modes as "all one algorithm, different
contracts", and the contract IS the lock policy. `load_source_score` computes
it, stores it on the graph, and it was read only by the engine's candidate
scorer — never spoken to the agent, who writes every note on the default path.

A `variation` brief did not contain the word "lock". The mode was decorative:
the melody it exists to preserve could be discarded entirely and nothing in the
system would notice or say so.
"""

import shutil

import pytest

_SRC = "workspace/mozart-andante-bb-20260826/output/mozart-andante-bb-20260826.musicxml"
_PID = "_test_lock_contract"


@pytest.fixture(scope="module")
def varied():
    import os

    from scales.scales import _WORKSPACE, compile_style, init_workspace, load_source_score

    if not os.path.exists(_SRC):
        pytest.skip("source score not present")
    shutil.rmtree(_WORKSPACE / _PID, ignore_errors=True)
    init_workspace(_PID, mode="variation", description="Variations", params={"source_path": _SRC})
    compile_style(_PID, composers=["mozart"])
    r = load_source_score(_PID)
    if not r.get("ok"):
        pytest.skip(f"source would not load: {r}")
    yield _PID
    shutil.rmtree(_WORKSPACE / _PID, ignore_errors=True)


def _brief(pid):
    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE, get_composition_brief

    g = PieceGraph.load(str(_WORKSPACE / pid / "piece_graph.json"))
    first = sorted(g.phrases, key=lambda k: g.phrases[k].slot.bar_start)[0]
    return str(get_composition_brief(pid, first, composer="mozart"))


def test_a_variation_brief_states_what_must_survive(varied):
    t = _brief(varied)
    assert "WHAT MUST SURVIVE" in t
    assert "principal_melody" in t


def test_the_locks_are_explained_not_just_numbered(varied):
    """A number a composer cannot interpret is not a contract."""
    t = _brief(varied)
    i = t.index("WHAT MUST SURVIVE")
    window = t[i : i + 900]
    assert "the tune itself" in window
    assert "leave it alone" in window


def test_the_source_material_is_shown(varied):
    """ "Keep the melody" is only actionable beside the melody."""
    t = _brief(varied)
    assert "THE SOURCE" in t


def test_a_plain_composition_is_not_given_a_contract():
    """`compose_from_text` locks nothing; the section must not appear."""
    import os

    if not os.path.exists("workspace/mozart-andante-bb-20260826/piece_graph.json"):
        pytest.skip("piece not present")
    t = _brief("mozart-andante-bb-20260826")
    assert "WHAT MUST SURVIVE" not in t


def test_only_real_locks_are_listed(varied):
    """Dimensions the mode leaves free must not be presented as constraints."""
    t = _brief(varied)
    i = t.index("WHAT MUST SURVIVE")
    window = t[i : i + 900]
    # variation leaves the bass and the colour events free (0.0)
    assert "bass_foundation" not in window
    assert "color_events" not in window


# ─── continue_piece: the ledger is the mode's whole differentiator ───────────


def _continue_from(src_piece):
    import os
    import shutil

    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE, compile_style, init_workspace, load_source_score

    src = _WORKSPACE / src_piece / "output" / f"{src_piece}.musicxml"
    if not os.path.exists(src):
        pytest.skip("source score not present")
    pid = "_test_continue_piece"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    init_workspace(
        pid, mode="continue_piece", description="continue", params={"source_path": str(src)}
    )
    compile_style(pid, composers=["mozart"])
    r = load_source_score(pid)
    g = PieceGraph.load(str(_WORKSPACE / pid / "piece_graph.json"))
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    return r, g


def test_continue_piece_carries_the_ledger_forward():
    """CLAUDE.md's entry for this mode is literally "Ledger carries forward".
    `load_source_score` reads a SCORE FILE, which has no ledger, so nothing was
    carried and the mode's whole differentiator did not happen."""
    r, g = _continue_from("mozart-andante-bb-20260826")
    assert r.get("ok")
    assert r.get("ledger_expectations_carried", 0) >= 1, r
    stored = getattr(g, "cross_scale_ledger", None) or {}
    assert len(stored.get("expectations") or []) >= 1


def test_the_carried_expectations_are_the_sources_own():
    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE

    _, g = _continue_from("mozart-andante-bb-20260826")
    src = PieceGraph.load(str(_WORKSPACE / "mozart-andante-bb-20260826" / "piece_graph.json"))
    mine = {
        e["object_ref"]
        for e in (getattr(g, "cross_scale_ledger", {}) or {}).get("expectations", [])
    }
    theirs = {
        e["object_ref"]
        for e in (getattr(src, "cross_scale_ledger", {}) or {}).get("expectations", [])
    }
    assert mine and mine <= theirs, mine - theirs


def test_other_modes_do_not_inherit_a_ledger():
    """Only `continue_piece` continues; a variation starts its own book."""
    import os
    import shutil

    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE, compile_style, init_workspace, load_source_score

    src = (
        _WORKSPACE / "mozart-andante-bb-20260826" / "output" / "mozart-andante-bb-20260826.musicxml"
    )
    if not os.path.exists(src):
        pytest.skip("source score not present")
    pid = "_test_variation_no_ledger"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    init_workspace(pid, mode="variation", description="v", params={"source_path": str(src)})
    compile_style(pid, composers=["mozart"])
    r = load_source_score(pid)
    g = PieceGraph.load(str(_WORKSPACE / pid / "piece_graph.json"))
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    assert "ledger_expectations_carried" not in r
    assert not (getattr(g, "cross_scale_ledger", None) or {}).get("expectations")
