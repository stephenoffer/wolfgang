"""The tool surface is called by hand, so it must fail loudly, not quietly.

Every function in `scales.scales` is invoked by an agent writing a Python
snippet, which means the arguments arrive hand-typed and a plausible-looking
mistake is the normal case rather than the exceptional one. The worst of those
mistakes is passing a bare string where a list is expected, because Python
iterates a string as **characters** and nothing raises:

    compile_style(piece_id, composers="mozart")

compiled six one-letter "composers" — a, m, o, r, t, z, the letters of the name
— wrote `tools/compiled_packs/{a,m,o,r,t,z}/` to disk, and then resolved the
piece's entire style against the composer "m": tier D, zero fingerprints, zero
cadence rules, zero left-hand textures. The piece generated anyway. It just had
no style at all, and no message anywhere said so.

These tests pin the coercion so that regression cannot come back through any of
the entry points an agent actually types.
"""

from __future__ import annotations

import ast
import inspect

import pytest

from scales import scales

# ─── The normaliser itself ───────────────────────────────────────────────────


def test_a_bare_string_becomes_a_single_item_not_its_characters():
    assert scales._as_list("mozart", "composers") == ["mozart"]


def test_a_lone_dict_becomes_a_single_item():
    """`allow=[{...}]` typed as `allow={...}` is the other common slip."""
    waiver = {"check": "density", "reason": "deliberately sparse"}
    assert scales._as_list(waiver, "allow") == [waiver]


def test_none_becomes_empty():
    assert scales._as_list(None, "sections") == []


def test_a_list_passes_through_unchanged():
    assert scales._as_list(["a", "b"], "x") == ["a", "b"]
    assert scales._as_list(("a",), "x") == ["a"]


def test_something_that_is_not_a_sequence_raises_with_the_argument_named():
    with pytest.raises(TypeError) as exc:
        scales._as_list(7, "motif_ids")
    assert "motif_ids" in str(exc.value)


def test_compile_style_accepts_a_bare_composer_name(function_source):
    """The original bug, at its original call site."""
    # By NAME, not by line offset — see `function_source` in conftest.
    src = function_source(scales, "compile_style")
    assert "isinstance(composers, str)" in src, (
        "compile_style must still guard against a bare string — this is the "
        "call that wrote six one-letter composer packs to disk"
    )


# ─── Every list-typed tool argument is guarded ───────────────────────────────

# Entry points an agent calls directly, per CLAUDE.md and the skill files.
_TOOL_SURFACE = {
    "build_form_graph",
    "resolve_motifs",
    "save_narrative",
    "apply_revision",
    "commit_agent_phrase_layer_ir",
    "commit_agent_phrase_direct_bars",
    "commit_candidate_phrase",
    "orchestrate_section",
    "compile_style",
}


def test_every_list_argument_on_the_tool_surface_is_normalised():
    """A new list-typed tool argument must be guarded when it is added.

    Checked structurally rather than by calling each function, because most of
    them need a workspace on disk. The rule is simple enough to read off the
    parse tree: if a public entry point declares a `List[...]` parameter, its
    body must pass that parameter through `_as_list` (or guard it by hand, as
    `compile_style` does).
    """
    tree = ast.parse(inspect.getsource(scales))
    unguarded = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        if fn.name not in _TOOL_SURFACE:
            continue
        body = ast.unparse(fn)
        for arg in fn.args.args + fn.args.kwonlyargs:
            if arg.annotation is None:
                continue
            hint = ast.unparse(arg.annotation)
            if "List[" not in hint:
                continue
            guarded = f"_as_list({arg.arg}," in body or f"isinstance({arg.arg}, str)" in body
            if not guarded:
                unguarded.append(f"{fn.name}({arg.arg}: {hint})")
    assert not unguarded, (
        "list-typed tool argument(s) with no bare-string guard; a string passed "
        "to any of these is iterated as characters and nothing raises:\n  " + "\n  ".join(unguarded)
    )


def test_normalising_none_did_not_break_a_default_branch(tmp_path):
    """`_as_list(None)` returns `[]`, so `is None` checks stop working.

    Two call sites branched on `is None` to mean "the caller did not supply
    this": `orchestrate_section` chose its default ensemble that way, and
    `commit_candidate_phrase` chose between the shorthand and the LayerIR path.
    Both would have silently taken the wrong branch.

    Tested by CALLING them with None and seeing which branch they take. The
    previous version parsed `inspect.getsource` for `is None` comparisons, which
    finds a function by the line number recorded when the module was IMPORTED —
    once the file changes on disk it parses whatever now occupies those lines,
    and the test became intermittent rather than wrong.
    """
    from scales.scales import _WORKSPACE, commit_candidate_phrase, orchestrate_section

    piece = "mozart-andante-fmaj-v2-20260826"
    if not (_WORKSPACE / piece / "piece_graph.json").exists():
        pytest.skip("no probe piece in the workspace")

    # No ensemble given: the default must be chosen, not an empty one used.
    result = orchestrate_section(piece, "m1_a", target_ensemble=None)
    assert result.get("ok"), result
    assert result.get("ensemble"), "an omitted ensemble produced an empty one"
    assert result.get("part_event_counts"), "no parts were written"

    # No bars and no layer_ir: it must complain about the MISSING INPUT rather
    # than take the shorthand path with an empty bar list.
    empty = commit_candidate_phrase(piece, "m1_a_p1", lens="probe", bars=None, layer_ir=None)
    assert not empty.get("ok"), empty
    assert empty.get("error"), "a candidate with no content must say what is missing"
