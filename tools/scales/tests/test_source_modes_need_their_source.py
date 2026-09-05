"""A mode that transforms an existing score must have that score.

Five of the six composition modes — variation, style_transfer, continue_piece,
orchestrate, reduce_to_piano — are defined by what they PRESERVE from a source.
`load_source_score` is what reads the source in and what applies the lock
policy, and the orchestrator skill says so plainly: "Without it the mode has no
material: the path alone is not the music."

Nothing enforced it. `build_form_graph` on a `variation` with no source loaded
returned ten phrase slots with `contract.source` empty and `contract.locks`
**entirely unset** — an original piece, called a variation, with the lock policy
that is the mode's whole definition never applied. Passing `source_path` to
`init_workspace` did not help: it records a path, and a path is not a score.

Both halves are pinned: the refusal, and that a properly loaded source is still
allowed straight through.
"""

import pytest

from scales.scales import (
    _MODE_LOCKS,
    _WORKSPACE,
    build_form_graph,
    compile_style,
    init_workspace,
    load_source_score,
)

SOURCE_MODES = sorted(_MODE_LOCKS)


@pytest.fixture(scope="module")
def a_real_score(tmp_path_factory):
    """Compose the smallest real score, so the happy path uses actual notes."""
    from pathlib import Path

    for candidate in sorted(Path("workspace").glob("*/output/*.musicxml")):
        return str(candidate)
    pytest.skip("no assembled score in the workspace to use as a source")


@pytest.mark.parametrize("mode", SOURCE_MODES)
def test_planning_without_a_source_is_refused(mode, tmp_path):
    pid = f"t-nosrc-{mode.replace('_', '-')}"
    init_workspace(piece_id=pid, mode=mode, description="a piece for solo piano in C major")
    compile_style(pid, composers=["mozart"])
    result = build_form_graph(pid, form="ternary", key="C major")

    assert not isinstance(result, list), f"{mode} planned a form with nothing to transform"
    assert pid in result["error"], "a failure must name the piece"
    assert mode in result["error"]
    assert "load_source_score" in result["hint"]
    # the hint must name what the mode would actually have preserved
    for lock in _MODE_LOCKS[mode]:
        assert lock in result["hint"]


def test_compose_from_text_needs_no_source():
    """The one mode that invents from nothing must not be caught by the guard."""
    pid = "t-nosrc-compose-from-text"
    init_workspace(piece_id=pid, mode="compose_from_text", description="a piece for solo piano in C major")
    compile_style(pid, composers=["mozart"])
    assert isinstance(build_form_graph(pid, form="ternary", key="C major"), list)


def test_a_loaded_source_is_allowed_through(a_real_score):
    """The half that matters most: the guard must not block the real flow."""
    pid = "t-src-variation"
    init_workspace(
        piece_id=pid,
        mode="variation",
        description="variations on a theme, for solo piano",
        params={"source_path": a_real_score},
    )
    loaded = load_source_score(pid)
    assert loaded.get("locks_applied"), "loading a source must apply the mode's locks"

    plan = build_form_graph(pid, form="theme_variations", key="F major")
    assert isinstance(plan, list) and plan, "a variation WITH a source must plan normally"

    from scales.piece_graph import PieceGraph

    graph = PieceGraph.load(str(_WORKSPACE / pid / "piece_graph.json"))
    assert any(getattr(p, "salience", "") == "source" for p in graph.phrases.values())
    assert any(vars(graph.contract.locks).values()), "the mode's lock policy must survive planning"
