"""Every tool must fail in a way an agent can read.

These functions are called by an agent writing a Python snippet, so what a
failure LOOKS like is part of the interface. Two ways it was failing badly:

**Ten tools raised a bare `FileNotFoundError`** on a piece that does not exist —
a traceback with a path in it and no indication that the piece id was the
problem, from `apply_revision`, `build_form_graph`, both commit entry points,
`get_composition_brief`, `compare_to_corpus` and more.

**Eight others silently succeeded.** `load_workspace('ghost')` returned a
plausible status dict for nothing; `save_reference_study` returned
`{"saved": True}` after writing state for a piece nobody had created;
`list_phrase_candidates` returned an empty candidate list, which is
indistinguishable from "this phrase has no candidates yet". A wrong piece id is
a typo, and a typo that returns a success dict is a bug that surfaces much
later somewhere else.
"""

from __future__ import annotations

import inspect
import json

import pytest

from scales import scales as scales_mod

_GHOST = "no-such-piece-x9k2"

# Tools whose job is to CREATE the piece, so a missing one is the normal case.
_CREATORS = {"init_workspace"}


def _tools_taking_a_piece_id():
    for name in sorted(dir(scales_mod)):
        if name.startswith("_"):
            continue
        fn = getattr(scales_mod, name)
        if not callable(fn) or getattr(fn, "__module__", "") != "scales.scales":
            continue
        try:
            sig = inspect.signature(fn)
        except (TypeError, ValueError):
            continue
        if "piece_id" in sig.parameters and name not in _CREATORS:
            yield name, fn, sig


def _call_with_ghost(fn, sig):
    args = {}
    for p in sig.parameters.values():
        if p.default is not inspect.Parameter.empty:
            continue
        if p.name == "piece_id":
            args[p.name] = _GHOST
        elif p.annotation in (str, "str"):
            args[p.name] = "x"
        else:
            args[p.name] = []
    return fn(**args)


@pytest.mark.parametrize("name,fn,sig", list(_tools_taking_a_piece_id()), ids=lambda v: str(v)[:40])
def test_a_missing_piece_returns_a_result_not_a_traceback(name, fn, sig):
    try:
        result = _call_with_ghost(fn, sig)
    except (TypeError, ValueError) as exc:
        # An argument error raised BEFORE the piece is looked at is correct —
        # compile_style with no composers, say. A file error is not.
        assert "piece" not in str(exc).lower() or "workspace" not in str(exc).lower()
        return
    except Exception as exc:  # noqa: BLE001 — the whole point is that this must not happen
        pytest.fail(f"{name} raised {type(exc).__name__} instead of returning a result: {exc}")

    assert isinstance(result, dict), f"{name} returned {type(result).__name__}"
    said_no = "error" in result or result.get("ready") is False
    assert said_no, f"{name} silently succeeded on a piece that does not exist: {result}"


@pytest.mark.parametrize("name,fn,sig", list(_tools_taking_a_piece_id()), ids=lambda v: str(v)[:40])
def test_the_failure_names_the_piece_and_says_what_to_do(name, fn, sig):
    try:
        result = _call_with_ghost(fn, sig)
    except (TypeError, ValueError):
        return
    except Exception:
        return  # covered by the test above
    if not isinstance(result, dict):
        return
    # Not every tool reports trouble under an "error" key: `plan_readiness`
    # answers `{"ready": False, "missing": ["no workspace for '<id>'"]}`, which
    # is a perfectly good report — and the old `"error" not in result: return`
    # skipped it, so two of these parametrised cases asserted nothing at all.
    # What matters is that the reply NAMES the piece, whatever shape it takes.
    reported = json.dumps(result, default=str)
    if _GHOST not in reported and not any(
        k in result for k in ("error", "missing", "hint", "warning")
    ):
        return  # this tool answered normally; nothing to report on a ghost piece
    assert _GHOST in reported, f"{name}'s failure does not name the piece: {result}"


def test_an_empty_result_never_doubles_as_a_missing_piece(tmp_path, monkeypatch):
    """`list_phrase_candidates` returned an empty list for a piece that does not
    exist — the same answer it gives for a real phrase that simply has no
    candidates yet. Three different situations must give three answers: no such
    piece, no such phrase, and no candidates."""
    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    assert "error" in scales_mod.list_phrase_candidates(_GHOST, "p1")

    scales_mod.init_workspace("real", mode="compose_from_text", description="a piece in C major")
    scales_mod.build_form_graph("real", form="ternary", key="C major")
    assert "error" in scales_mod.list_phrase_candidates("real", "no-such-phrase")

    real = scales_mod.list_phrase_candidates("real", "m1_a_p1")
    assert "error" not in real and real["candidates"] == [], real


# ── The second dimension: a real piece, a bad section or phrase id ──────────


@pytest.fixture()
def planned_piece(tmp_path, monkeypatch):
    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    scales_mod.init_workspace("real", mode="compose_from_text", description="a piece in C major")
    scales_mod.build_form_graph("real", form="ternary", key="C major")
    return "real"


def _tools_taking_a_section_or_phrase():
    for name, fn, sig in _tools_taking_a_piece_id():
        if {"section_id", "phrase_id"} & set(sig.parameters):
            yield name, fn, sig


@pytest.mark.parametrize(
    "name,fn,sig", list(_tools_taking_a_section_or_phrase()), ids=lambda v: str(v)[:40]
)
def test_a_bad_section_or_phrase_id_is_reported(planned_piece, name, fn, sig):
    args = {}
    for p in sig.parameters.values():
        if p.default is not inspect.Parameter.empty:
            continue
        if p.name == "piece_id":
            args[p.name] = planned_piece
        elif p.name in ("section_id", "phrase_id"):
            args[p.name] = "no-such-id"
        elif p.annotation in (str, "str"):
            args[p.name] = "x"
        else:
            args[p.name] = []
    try:
        result = fn(**args)
    except (TypeError, ValueError):
        return
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"{name} raised {type(exc).__name__} for a bad id: {exc}")
    assert isinstance(result, dict) and "error" in result, (
        f"{name} accepted a nonexistent section/phrase and returned: {result}"
    )


def test_a_revision_that_applies_to_nothing_is_an_error(planned_piece):
    """A revision that silently applies to nothing looks exactly like one that
    worked: the result carried an empty `affected_phrases` and no error, so a
    mistyped id read as 'the critic's fix landed'."""
    out = scales_mod.apply_revision(planned_piece, "no-such-section", [])
    assert "error" in out and out.get("sections")

    out = scales_mod.apply_revision(
        planned_piece, "m1_a", [{"target_phrase": "ghost", "operation": "re_realize"}]
    )
    assert "error" in out and "ghost" in out["error"]


def test_an_unrecognised_revision_operation_is_an_error(planned_piece):
    """The patch engine logs and skips an operation it does not know, so a typo
    in a critic's revision script came back as a successful revision that
    changed nothing."""
    out = scales_mod.apply_revision(
        planned_piece, "m1_a", [{"target_phrase": "m1_a_p1", "operation": "make_it_nicer"}]
    )
    assert "error" in out
    assert "set_articulation" in out.get("operations", []), out


def test_a_valid_revision_reports_how_many_ops_it_applied(planned_piece):
    out = scales_mod.apply_revision(
        planned_piece, "m1_a", [{"target_phrase": "m1_a_p1", "operation": "re_realize"}]
    )
    assert "error" not in out
    assert out["ops_applied"] == 1
    assert out["affected_phrases"] == ["m1_a_p1"]


def test_the_documented_operations_are_the_implemented_ones():
    """The critic is handed a table of operations in music-critic.md. If the
    table and the engine disagree, the critic writes ops that do nothing."""
    from pathlib import Path

    from scales.scales import _REVISION_OPS

    doc = Path(".claude/agents/music-critic.md")
    if not doc.exists():
        pytest.skip("critic guidance not present")
    text = doc.read_text()
    for op in _REVISION_OPS:
        assert f"`{op}`" in text, f"{op} is implemented but not offered to the critic"


def test_every_tool_that_takes_a_piece_id_is_decorated():
    """`_load_graph` reports a missing piece by RAISING `_MissingPiece`, and the
    docstring says why: "Raised rather than returned so `_load_graph` can be a
    one-line call at the top of a tool without every caller needing a two-value
    unpack." That only holds if the tool carries `@_tool`, which turns the
    exception back into the tool's normal error result.

    `run_scales_section` — the SCALES engine's own entry point — was the one
    public tool taking a `piece_id` without it, so a mistyped piece id came back
    as a FileNotFoundError traceback with a path in it while every neighbouring
    tool returned `{"error": "No workspace for '<id>'", "hint": ...}`.

    Parsed from the source rather than read off the objects: `functools.wraps`
    makes a decorated function indistinguishable from an undecorated one at
    runtime, so asking the object cannot answer this.
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("tools/scales/scales.py").read_text())
    undecorated = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        args = [a.arg for a in node.args.args]
        if not args or args[0] != "piece_id":
            continue
        if "_tool" not in {ast.unparse(d) for d in node.decorator_list}:
            undecorated.append(node.name)
    assert not undecorated, (
        f"these tools take a piece_id and would raise a traceback on a missing "
        f"piece instead of returning a structured error: {undecorated}"
    )
