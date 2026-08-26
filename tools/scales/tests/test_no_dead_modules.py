"""A module documented as part of the pipeline must actually be called.

This is the single most expensive failure mode this project has had. Two
modules — `expression_enricher.py` (1,049 lines, 29 passing tests) and
`score_realism.py` (16 detectors) — were complete, were described in
`CLAUDE.md`, in the craft reference and in the music-critic's prompt as though
they were running, and were **imported by nothing**. Every score the system
produced therefore carried zero articulation marks and zero ties, and the
measurement layer reported "0 errors, 0 warnings" on an obviously machine-made
score, for as long as that was true.

Passing tests are not evidence that a feature works. A module can be perfectly
tested in isolation and never run once in production, and nothing in a green
test suite says otherwise. This file is the check that was missing: if
`CLAUDE.md` lists a module, either something imports it, or the entry says
plainly that nothing does.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_SCALES = _REPO / "tools" / "scales"
_CLAUDE_MD = _REPO / "CLAUDE.md"

# Phrases an entry uses to say, honestly, that nothing calls it.
_DECLARED_UNUSED = ("called by nothing", "currently unused", "not currently wired")


def _importers() -> dict:
    """module name -> set of modules that import it."""
    out: dict = {}
    roots = [_SCALES, _SCALES / "feedback", _REPO / "tools" / "scripts"]
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("*.py"):
            if path.parent.name == "tests":
                continue
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        out.setdefault(node.module.rsplit(".", 1)[-1], set()).add(path.name)
                    else:
                        # `from . import musicality` — the module names are the
                        # aliases, not node.module (which is None here).
                        for alias in node.names:
                            out.setdefault(alias.name, set()).add(path.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        out.setdefault(alias.name.rsplit(".", 1)[-1], set()).add(path.name)

    # The skills, agents and workflows under `.claude` are call sites too — the
    # tool surface (`scales.py`) and the MIDI preview are invoked from there and
    # from nowhere in Python, so a scan of imports alone calls them dead.
    claude = _REPO / ".claude"
    if claude.is_dir():
        for path in list(claude.rglob("*.md")) + list(claude.rglob("*.js")):
            text = path.read_text()
            for m in re.finditer(r"scales\.([a-z_0-9]+)", text):
                out.setdefault(m.group(1), set()).add(str(path.relative_to(_REPO)))
    return out


def _documented_modules() -> dict:
    """module filename -> its CLAUDE.md table description."""
    if not _CLAUDE_MD.exists():
        pytest.skip("CLAUDE.md not found")
    out = {}
    for line in _CLAUDE_MD.read_text().splitlines():
        m = re.match(r"\|\s*`([a-z_0-9]+\.py)`\s*\|(.*)\|\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def test_every_documented_module_is_imported_or_declared_unused():
    documented = _documented_modules()
    if not documented:
        pytest.skip("no module table found in CLAUDE.md")
    importers = _importers()

    dead = []
    for filename, description in sorted(documented.items()):
        name = filename[:-3]
        if not (_SCALES / filename).exists() and not (_SCALES / "feedback" / filename).exists():
            continue  # covered by the existence test below
        if importers.get(name):
            continue
        if any(p in description.lower() for p in _DECLARED_UNUSED):
            continue
        dead.append(
            f"{filename} — documented as active, imported by nothing, and the entry does not say so"
        )
    assert not dead, (
        "module(s) documented as part of the pipeline that nothing calls:\n  "
        + "\n  ".join(dead)
        + "\n\nEither wire it in, or say in its CLAUDE.md entry that nothing "
        "calls it. A module described as running while it does not is how this "
        "project shipped scores with no articulation in them."
    )


def test_every_documented_module_exists():
    """A table entry for a deleted file sends a reader looking for nothing."""
    missing = [
        f
        for f in _documented_modules()
        if not (_SCALES / f).exists() and not (_SCALES / "feedback" / f).exists()
    ]
    assert not missing, f"CLAUDE.md documents module(s) that do not exist: {sorted(missing)}"


def test_the_two_that_caused_this_are_wired():
    """Named explicitly, because they are the reason this file exists."""
    importers = _importers()
    for name in ("expression_enricher", "score_realism"):
        assert importers.get(name), (
            f"{name} is imported by nothing again — this module being dead code "
            "is why generated scores had zero articulations and the audit "
            "reported zero findings on obviously machine-made music"
        )
