"""A parameter that does nothing must not do it silently.

`build_form_graph(sections=..., motif_ids=...)` accepted both, normalised them
with `_as_list`, and never read either again. A caller handing over a custom
section layout got the canned form for `form` and no indication their layout had
been discarded — malformed sections, well-formed sections and no sections at all
produced byte-identical results:

    no sections arg   -> 9 phrases, m1_a m1_a2 m1_b m1_coda m1_retr
    wrong key names   -> 9 phrases, identical
    empty dict        -> 9 phrases, identical

Nothing in the repo passes either, and `/w-plan` documents the call without
them — but the signature advertised them, and a silent no-op on a public tool
surface is worse than an unimplemented one. An agent reading the signature would
have no way to find out.
"""

import ast
import inspect
import logging
import shutil

import pytest

from scales import scales as scales_mod
from scales.scales import build_form_graph, compile_style, init_workspace

PID = "_unimplemented_param_probe"


@pytest.fixture
def piece():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="An andante in F major for piano")
    compile_style(PID, composers=["mozart"])
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_supplying_sections_says_it_was_ignored(piece, caplog):
    with caplog.at_level(logging.WARNING, logger="scales.scales"):
        build_form_graph(piece, form="ternary", key="F major", sections=[{"id": "m1_a"}])
    assert "not implemented" in caplog.text
    assert "sections" in caplog.text


def test_supplying_motif_ids_says_it_was_ignored(piece, caplog):
    with caplog.at_level(logging.WARNING, logger="scales.scales"):
        build_form_graph(piece, form="ternary", key="F major", motif_ids=["A"])
    assert "not implemented" in caplog.text
    assert "motif_ids" in caplog.text


def test_the_normal_call_is_silent(piece, caplog):
    """Falsification: the warning must not fire on the documented call."""
    with caplog.at_level(logging.WARNING, logger="scales.scales"):
        build_form_graph(piece, form="ternary", key="F major")
    assert "not implemented" not in caplog.text


def test_the_form_is_still_built(piece):
    """A warning, not a refusal — the form the caller asked for still appears."""
    assert build_form_graph(piece, form="ternary", key="F major", sections=[{"id": "x"}])


def test_the_parameters_really_are_unread():
    """If either is ever implemented this test should fail and be deleted —
    it exists to stop the no-op being re-introduced quietly."""
    fn = next(
        n
        for n in ast.parse(inspect.getsource(scales_mod)).body
        if isinstance(n, ast.FunctionDef) and n.name == "build_form_graph"
    )
    for name in ("sections", "motif_ids"):
        uses = [
            node
            for node in ast.walk(fn)
            if isinstance(node, ast.Name) and node.id == name and isinstance(node.ctx, ast.Load)
        ]
        # one Load: the `_as_list(...)` normalisation, plus the warning loop
        assert len(uses) <= 2, f"{name} now has real uses — implement it or update this test"


def test_init_work_says_the_description_is_not_stored(piece, caplog):
    """`WorkGraph` has no `description` field, so the argument was accepted and
    dropped. The piece description belongs on `init_workspace`, which is where
    the brief reads it from when no narrative prose was authored."""
    from scales.scales import init_work

    with caplog.at_level(logging.WARNING, logger="scales.scales"):
        init_work(piece, movement_count=3, description="a symphony about winter")
    assert "not stored" in caplog.text
    assert "init_workspace" in caplog.text


def test_init_work_is_silent_without_a_description(piece, caplog):
    from scales.scales import init_work

    with caplog.at_level(logging.WARNING, logger="scales.scales"):
        init_work(piece, movement_count=3, emotional_narrative="winter into spring")
    assert "not stored" not in caplog.text


def test_no_public_tool_parameter_is_silently_unread():
    """The sweep that found `build_form_graph(sections=, motif_ids=)` and
    `init_work(description=)`, kept as a guard. A parameter that is accepted and
    discarded invites a caller to supply something and throws it away looking
    like it worked — dead code moved onto the call surface, where it is worse.

    If a new parameter is added and not yet used, log that it is ignored (as
    those three now do) rather than leaving it silent.
    """
    from scales import scales as S

    normalisers = {"_as_list", "_as_dict", "_as_bool"}
    tree = ast.parse(inspect.getsource(S))
    unread = []
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]:
        params = [a.arg for a in fn.args.args] + [a.arg for a in fn.args.kwonlyargs]
        norm_args = {
            id(a)
            for node in ast.walk(fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in normalisers
            for a in node.args
            if isinstance(a, ast.Name)
        }
        for p in params:
            if p in ("self", "piece_id"):
                continue
            loads = [
                n
                for n in ast.walk(fn)
                if isinstance(n, ast.Name) and n.id == p and isinstance(n.ctx, ast.Load)
            ]
            if not [n for n in loads if id(n) not in norm_args]:
                unread.append(f"{fn.name}({p}=)")
    assert not unread, f"accepted and never read: {unread}"
