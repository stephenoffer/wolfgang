"""The engine path must take the steps the agent path takes at commit.

`_gated_commit` (agent) and `run_scales_section` (engine fallback) both end with
a phrase going into the graph, but the engine path skipped work the agent path
does. Diffing the two found five such steps; three mattered:

  * `_engrave_phrase`  — engine output reached the page with 0 slurs and 0
    articulations (see test_engine_output_is_engraved.py)
  * `_capture_theme_if_first_statement` — the PRINCIPAL THEME is captured from
    the phrase that first states it. With the engine realizing the opening
    section — the usual case for a fallback — nothing captured it, so
    `principal_theme_phrase()` returned "" and the piece had no theme to bring
    back, develop or recognise. A piece cannot have a memorable theme if
    nothing ever recorded what the theme was.
  * `_settle_expectations` — promises recorded at plan time and never
    discharged leave every debt open for the whole piece.

These are call-site tests. The helpers are covered elsewhere; what was broken
here was that one of the two paths never called them.
"""


from scales import scales

REQUIRED_AT_COMMIT = (
    "_engrave_phrase",
    "_capture_theme_if_first_statement",
    "_settle_expectations",
)


def _by_name(module, name: str) -> str:
    """Located by NAME, not by the line numbers `inspect.getsource` recorded when
    the module was imported — those go stale the moment the file is edited, and
    it then returns a different function's text."""
    import ast
    import inspect as _inspect
    from pathlib import Path

    text = Path(_inspect.getfile(module)).read_text()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(f"{module.__name__} has no {name!r}")


def _engine_source() -> str:
    return _by_name(scales, "run_scales_section")


def _agent_source() -> str:
    return _by_name(scales, "_gated_commit")


def test_the_engine_path_takes_every_step_the_agent_path_takes():
    src = _engine_source()
    missing = [name for name in REQUIRED_AT_COMMIT if f"{name}(" not in src]
    assert not missing, f"engine commit loop skips: {missing}"


def test_the_agent_path_still_takes_them_too():
    """Parity is symmetric — this is the half that was already right, pinned so
    a later change cannot quietly drop it."""
    src = _agent_source()
    missing = [name for name in REQUIRED_AT_COMMIT if f"{name}(" not in src]
    assert not missing, f"agent commit skips: {missing}"


def test_theme_capture_runs_before_nothing_can_undo_it():
    """Capture reads the phrase's realized surface, so it has to come after the
    surface is committed, not before."""
    src = _engine_source()
    assert src.index("commit_phrase(") < src.index("_capture_theme_if_first_statement(")
