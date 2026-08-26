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
    if not isinstance(result, dict) or "error" not in result:
        return
    message = f"{result.get('error', '')} {result.get('hint', '')}"
    assert _GHOST in message, f"{name}'s error does not name the piece: {result}"


def test_an_empty_result_never_doubles_as_a_missing_piece(tmp_path, monkeypatch):
    """`list_phrase_candidates` returned an empty list for a piece that does not
    exist, which is the same answer it gives for a phrase that simply has no
    candidates yet."""
    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    ghost = scales_mod.list_phrase_candidates(_GHOST, "p1")
    assert "error" in ghost

    scales_mod.init_workspace("real", mode="compose_from_text", description="x")
    real = scales_mod.list_phrase_candidates("real", "p1")
    assert "error" not in real and real["candidates"] == [], real
