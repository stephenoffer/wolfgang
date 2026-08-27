"""Every `python -c` command in a skill or agent file must be runnable.

An agent copies these verbatim. Three of them in `/w-plan` had their FIRST line
indented one level deeper than the rest — a markdown list item's indentation
leaking into the program — and `python -c` refuses a program whose first line is
indented:

      .venv/bin/python -c "
         from scales.scales import list_reference_scores
      import json; print(...)
      "
      IndentationError: unexpected indent

The three were `list_reference_scores`, `get_reference_score` and
`save_reference_study` — the whole-score reference study that CLAUDE.md calls
central to v6 ("Study scores like a human, then compose freely"). An agent
following `/w-plan` hit the error on its first study command, whichever way it
handled the surrounding indentation: strip the common prefix and the first line
still has three spaces the second does not; keep it and the mismatch remains.

This is the same class as the `python3` defect recorded in
`project_docs_snippets_must_run` — the documented call did not run, and nothing
tested the documentation because it is prose.
"""

from __future__ import annotations

import ast
import pathlib
import re
import textwrap

_ROOT = pathlib.Path(__file__).resolve().parents[3]
_DOCS = [
    f
    for d in (_ROOT / ".claude" / "skills", _ROOT / ".claude" / "agents")
    if d.is_dir()
    for f in d.rglob("*.md")
]

_PROGRAM = re.compile(r'python\s+-c\s+"\n(.*?)^\s*"\s*$', re.S | re.M)


def _programs():
    """(file, program text) for every `python -c "…"` in the skill docs."""
    for doc in _DOCS:
        for match in _PROGRAM.finditer(doc.read_text()):
            yield doc, match.group(1)


def test_the_docs_were_found():
    """Guard the guard: an empty corpus makes every test below vacuous."""
    assert len(_DOCS) >= 10, [d.name for d in _DOCS]
    assert len(list(_programs())) >= 15, "the `python -c` extraction found almost nothing"


def test_no_program_starts_with_an_indented_line():
    """The exact failure, checked without dedenting anything first."""
    offenders = []
    for doc, code in _programs():
        lines = [ln for ln in code.splitlines() if ln.strip()]
        if not lines:
            continue
        indents = [len(ln) - len(ln.lstrip()) for ln in lines]
        if indents[0] > min(indents):
            offenders.append(f"{doc.relative_to(_ROOT)}: {lines[0].strip()[:60]}")
    assert not offenders, (
        "program(s) whose first line is indented deeper than the rest — "
        "`python -c` raises IndentationError before running a statement:\n  "
        + "\n  ".join(offenders)
    )


def test_every_program_parses_once_its_common_indent_is_removed():
    """Placeholders like `<tempo>` are templates and are skipped by design."""
    broken = []
    for doc, code in _programs():
        body = textwrap.dedent(code)
        # A template has placeholders the reader fills in. A QUOTED one
        # (`'<piece-id>'`) is still valid Python and must parse; a bare one
        # (`tempo_bpm=<tempo>`) is not, and that snippet is a form to complete
        # rather than a command to run. Testing for "has a placeholder at all"
        # is not enough — one snippet has both, and checking the quoted kind
        # first let it through to fail as though the doc were broken.
        without_quoted = re.sub(r"""(['"])<[^<>]+>\1""", "'x'", body)
        if re.search(r"<[^<>]+>", without_quoted):
            continue
        try:
            ast.parse(body)
        except SyntaxError as exc:
            broken.append(f"{doc.relative_to(_ROOT)}: {exc}")
    assert not broken, "documented program(s) that do not parse:\n  " + "\n  ".join(broken)


def test_every_documented_import_names_something_that_exists():
    """A snippet importing a function that was renamed fails at the first line."""
    import importlib

    missing = []
    for doc, code in _programs():
        try:
            tree = ast.parse(textwrap.dedent(code))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom) or not (node.module or "").startswith("scales"):
                continue
            try:
                module = importlib.import_module(node.module)
            except ImportError:
                missing.append(f"{doc.relative_to(_ROOT)}: no module {node.module}")
                continue
            for alias in node.names:
                if not hasattr(module, alias.name):
                    missing.append(f"{doc.relative_to(_ROOT)}: {node.module}.{alias.name}")
    assert not missing, "documented import(s) of names that do not exist:\n  " + "\n  ".join(
        missing
    )


def test_the_interpreter_is_the_one_with_music21():
    """`python3` is the system interpreter and has no music21, so every
    assembly, MIDI and self_evaluate snippet failed for any agent following the
    docs — recorded in `project_docs_snippets_must_run`."""
    offenders = []
    for doc in _DOCS:
        for line_no, line in enumerate(doc.read_text().splitlines(), 1):
            if re.search(r"(?<![\w./])python3?\s+-c\s+\"", line) and ".venv/bin/python" not in line:
                offenders.append(f"{doc.relative_to(_ROOT)}:{line_no}: {line.strip()[:70]}")
    assert not offenders, (
        "documented command(s) not using the project interpreter:\n  " + "\n  ".join(offenders)
    )
