"""Shared pytest setup for the SCALES test suite.

Makes the top-level ``scales`` package importable when the suite is run without
an editable install (``pip install -e .``) — pytest auto-loads this file before
collecting tests, so individual test modules need no ``sys.path`` manipulation.
"""

import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2]  # repo's tools/ directory
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))


@pytest.fixture
def tmp_workspace(tmp_path, monkeypatch):
    """Isolated workspace dir with ``scales._WORKSPACE`` pointed at it.

    Mirrors the manual setup in each gate test's ``__main__`` runner so the same
    test functions work under both ``pytest`` and direct execution.
    """
    from scales import scales

    monkeypatch.setattr(scales, "_WORKSPACE", tmp_path)
    return tmp_path


@pytest.fixture(autouse=True)
def _workspace_is_not_leaked():
    """Fail the test that repoints ``scales._WORKSPACE`` and does not put it back.

    One test assigned it directly (`scales._WORKSPACE = tmp_path`) instead of
    using `monkeypatch`, so from that point on the ENTIRE REST OF THE SUITE ran
    against a temp directory containing a single piece. Nothing failed loudly:
    tests that build their own fixtures still passed, and the damage landed on
    any test holding a module-level ``from scales.scales import _WORKSPACE`` —
    an import-time copy that then pointed somewhere different from the attribute
    the code under test reads. Those passed alone and failed in the suite, which
    is the most expensive way for a test to be wrong.

    Guarding it here rather than trusting review: the failure mode is invisible
    at the call site and only shows up in an unrelated file.
    """
    from scales import scales

    before = scales._WORKSPACE
    yield
    assert scales._WORKSPACE == before, (
        "this test repointed scales._WORKSPACE and did not restore it — use the "
        "`monkeypatch` fixture (or the shared `tmp_workspace` fixture) so it is "
        "put back; leaving it set corrupts every test that runs afterwards"
    )


def _function_source(module, name: str) -> str:
    """The source of one function, located by NAME rather than line number.

    `inspect.getsource(fn)` finds a function by the line number recorded on its
    code object when the module was IMPORTED. If the file changes on disk after
    that — which it does constantly while anyone is editing, and constantly
    while two sessions share a checkout — it returns whatever now occupies those
    lines. Four tests here failed that way, one of them asserting a notice
    appeared in the string `'        ):'`.

    Reading the file and finding the definition in its AST is immune to that.

    Prefer testing BEHAVIOUR. Reach for this only where the claim is genuinely
    about the code — "no function in this module does X" — and not where the
    property can be observed by calling something.
    """
    import ast
    import inspect
    from pathlib import Path

    text = Path(inspect.getfile(module)).read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(text, node) or ""
    raise AssertionError(f"{module.__name__} has no function named {name!r}")


@pytest.fixture
def function_source():
    """Fixture form, so tests can take it as an argument."""
    return _function_source
