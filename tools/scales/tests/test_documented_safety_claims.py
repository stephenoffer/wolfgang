"""CLAUDE.md makes safety claims. They are checked here.

Two of them protect the composer's work, and a violation of either would be
silent and expensive:

  · "expression_enricher ... never changes a pitch or a duration"
  · "run_scales_section ... never overwrites `agent_authored` phrases"

Both hold. Verifying them found a third thing: the engine reported
`phrases_realized: 3` for a section whose three phrases it had correctly left
alone, so an orchestrator reading the result would believe work had been done.
"""

import copy
import os
import shutil

import pytest

_LAYERS = (
    "principal_line",
    "bass_foundation",
    "response_layer",
    "counter_reply",
    "ornamental_surface",
)


def _notes(layer):
    return [
        (n, e.bar, float(e.beat), str(e.pitch), e.duration)
        for n in _LAYERS
        for e in (getattr(layer, n, None) or [])
    ]


@pytest.mark.parametrize(
    "piece,style",
    [
        ("mozart-andante-bb-20260826", "classical"),
        ("bach-fugue-amin-20260826", "baroque"),
        ("palestrina-motet-dorian-20260826", "renaissance"),
    ],
)
def test_the_engraver_never_changes_a_pitch_or_a_duration(piece, style):
    from scales.expression_enricher import enrich_layer_ir
    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE

    p = _WORKSPACE / piece / "piece_graph.json"
    if not os.path.exists(p):
        pytest.skip(f"{piece} not present")
    g = PieceGraph.load(str(p))
    checked = 0
    for ps in g.phrases.values():
        if not ps.realized:
            continue
        before = _notes(ps.realized)
        after_ir = copy.deepcopy(ps.realized)
        enrich_layer_ir(after_ir, style=style)
        assert _notes(after_ir) == before, "the engraver altered the notes"
        checked += 1
    assert checked, "no realized phrases to check"


@pytest.fixture()
def copied_piece():
    from scales.scales import _WORKSPACE

    src = _WORKSPACE / "mozart-andante-bb-20260826"
    if not os.path.exists(src / "piece_graph.json"):
        pytest.skip("source piece not present")
    pid = "_test_engine_overwrite"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    shutil.copytree(src, _WORKSPACE / pid)
    yield pid
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)


def test_the_engine_never_overwrites_agent_work(copied_piece):
    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE, run_scales_section

    path = str(_WORKSPACE / copied_piece / "piece_graph.json")
    before = {
        k: _notes(ps.realized) for k, ps in PieceGraph.load(path).phrases.items() if ps.realized
    }
    assert before, "fixture has no realized phrases"
    run_scales_section(copied_piece, "m1_a")
    after = {
        k: _notes(ps.realized) for k, ps in PieceGraph.load(path).phrases.items() if ps.realized
    }
    assert set(before) <= set(after), "phrases disappeared"
    for k, notes in before.items():
        assert after[k] == notes, f"{k} was rewritten by the engine"


def test_the_engine_reports_what_it_actually_wrote(copied_piece):
    """`phrases_realized` counted the whole path, so a section the engine
    correctly skipped still reported three phrases realized."""
    from scales.scales import run_scales_section

    r = run_scales_section(copied_piece, "m1_a")
    assert r.get("phrases_realized") == 0, r
    assert r.get("phrases_kept_agent_authored", 0) >= 1, r
    assert r.get("phrases_in_path", 0) >= 1, r


# ─── the gate's documented scope ────────────────────────────────────────────


def test_there_is_no_skip_gate():
    """CLAUDE.md: "There is no `skip_gate`." A way to bypass the physical checks
    would make every guarantee here conditional."""
    import glob

    for f in glob.glob("tools/**/*.py", recursive=True):
        if f.endswith(os.path.basename(__file__)):
            continue  # this file names it in order to forbid it
        src = open(f, errors="ignore").read()
        for line in src.splitlines():
            if "skip_gate" in line and "no `skip_gate`" not in line and "removed" not in line:
                raise AssertionError(f"{f}: {line.strip()}")


def test_only_physical_violations_block_in_the_gate():
    """CLAUDE.md: the commit gate blocks ONLY physical violations. Everything
    artistic — density, figuration, composed_blind, anti-patterns — is advisory,
    because the agent is allowed to invent away from the corpus and the
    fresh-ears critic judges the result."""
    import inspect
    import re

    from scales import commit_gate as CG

    src = inspect.getsource(CG)
    blocking = set(re.findall(r'blocking\.append\(\s*GateDiagnostic\(\s*check="([a-z_]+)"', src))
    assert blocking <= {"meter"}, f"non-physical checks now block: {sorted(blocking - {'meter'})}"


@pytest.fixture()
def scratch_piece():
    from scales.piece_graph import PieceGraph
    from scales.scales import _WORKSPACE, build_form_graph, compile_style, init_workspace

    pid = "_test_gate_scope"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    init_workspace(pid, mode="compose_from_text", description="A study for solo piano")
    compile_style(pid, composers=["mozart"])
    build_form_graph(pid, form="ternary", key="C major", tempo_bpm=90, meter=(4, 4))
    g = PieceGraph.load(str(_WORKSPACE / pid / "piece_graph.json"))
    first = sorted(g.phrases, key=lambda k: g.phrases[k].slot.bar_start)[0]
    yield pid, first, g.phrases[first].slot.bar_count
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)


def test_a_commit_without_a_brief_is_refused(scratch_piece):
    """ "Studying references is required" — the brief receipt is the one
    non-physical requirement the gate still enforces."""
    from scales.scales import commit_agent_phrase_direct_bars

    pid, phrase, nbars = scratch_piece
    bars = [{"rh": "C5q D5q E5q F5q", "lh": "C3q G3q E3q G3q"}] * nbars
    r = commit_agent_phrase_direct_bars(pid, phrase, bars, composer="mozart")
    assert r.get("ok") is False
    assert r.get("error") == "brief_not_fetched", r


def test_a_note_outside_the_instrument_is_refused(scratch_piece):
    """Range is physical and never waivable."""
    from scales.scales import commit_agent_phrase_direct_bars, get_composition_brief

    pid, phrase, nbars = scratch_piece
    get_composition_brief(pid, phrase, composer="mozart")
    bars = [{"rh": "C9q D5q E5q F5q", "lh": "C3q G3q E3q G3q"}] * nbars
    r = commit_agent_phrase_direct_bars(pid, phrase, bars, composer="mozart")
    assert r.get("ok") is False
    assert any("out of range" in str(i) for i in (r.get("issues") or [])), r
