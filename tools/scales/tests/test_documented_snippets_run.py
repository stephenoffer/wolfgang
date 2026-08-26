"""The snippets in the skill files must actually be runnable.

Every skill, agent and workflow file teaches the agent to call this package by
pasting a shell snippet. Those snippets are the interface, so a wrong
interpreter in one of them is a production bug, not a typo — and there were 37
of them.

`python3` on a developer machine is whatever is first on PATH (here, Homebrew's
3.14), which has neither `music21` nor the `scales` package installed. Because
`assembler.py` imports music21 lazily, the failure did not surface at import
time: `from scales.assembler import assemble` succeeded and the call then raised
`ImportError: music21 is required for assembly`. So assembly, MIDI preview and
`self_evaluate` — the entire back half of the pipeline — failed for an agent
that followed the documentation exactly, and failed late.

The project venv is the only interpreter that has the dependencies (CLAUDE.md:
"Use `.venv/bin/python` for anything that assembles/parses scores").
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_CLAUDE = _REPO / ".claude"

_DOC_FILES = sorted(
    list(_CLAUDE.glob("skills/*/SKILL.md"))
    + list(_CLAUDE.glob("skills/*/references/*.md"))
    + list(_CLAUDE.glob("agents/*.md"))
    + list(_CLAUDE.glob("workflows/*.js"))
)


def _docs():
    if not _DOC_FILES:
        pytest.skip("no .claude documentation found")
    return _DOC_FILES


@pytest.mark.parametrize("path", _docs(), ids=lambda p: str(p.relative_to(_CLAUDE)))
def test_snippet_uses_an_interpreter_that_has_the_dependencies(path):
    """No snippet may invoke a bare `python3` / `python`."""
    # Strip fenced-block language tags (```python) — those name a syntax
    # highlighter, not an interpreter.
    text = re.sub(r"```[a-zA-Z]*", "```", path.read_text())
    bad = re.findall(r"(?<![\w/.-])python3?(?![\w.-])", text)
    assert not bad, (
        f"{path.relative_to(_REPO)} invokes a bare `{bad[0]}` in {len(bad)} place(s). "
        "That interpreter has no music21 and no `scales` package, so every "
        "assemble / render_midi / self_evaluate call in this file fails at "
        "runtime. Use `.venv/bin/python`."
    )


@pytest.mark.parametrize("path", _docs(), ids=lambda p: str(p.relative_to(_CLAUDE)))
def test_no_snippet_teaches_the_sys_path_shim(path):
    """`sys.path.insert(0, 'tools')` contradicts the packaging.

    The package is installed editable (CLAUDE.md, "Packaging": "no `sys.path`
    shims"), so the shim is redundant when the working directory happens to be
    the repo root and silently does nothing when it is not — while shadowing
    the installed package with whatever `./tools` contains.
    """
    text = path.read_text()
    assert "sys.path.insert" not in text, (
        f"{path.relative_to(_REPO)} still teaches the sys.path shim; the "
        "`scales` package is installed editable and does not need it"
    )


def test_the_venv_interpreter_can_actually_assemble():
    """Assert the recommended interpreter really does have the dependencies.

    Recommending `.venv/bin/python` is only right for as long as the venv has
    music21 in it; this fails loudly rather than sending the agent to a second
    broken interpreter.
    """
    venv = _REPO / ".venv" / "bin" / "python"
    if not venv.exists():
        pytest.skip("project venv not present")
    import subprocess

    r = subprocess.run(
        [str(venv), "-c", "import music21, scales.assembler; print('ok')"],
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )
    assert "ok" in r.stdout, (
        f"the interpreter the docs point at cannot import music21/scales:\n{r.stderr[-500:]}"
    )


# ─── The craft reference is navigated by section number ──────────────────────

_CRAFT = _CLAUDE / "skills" / "w-compose" / "references" / "note-writing-craft.md"


def _craft_text():
    if not _CRAFT.exists():
        pytest.skip("craft reference not found")
    return _CRAFT.read_text()


def _section_key(label: str):
    """'4b' -> (4, 'b') so §4b sorts after §4 and before §5."""
    m = re.match(r"(\d+)([a-z]*)", label)
    return (int(m.group(1)), m.group(2)) if m else (0, "")


def test_craft_reference_sections_are_in_order():
    """Every agent that composes reads this file top to bottom.

    §6b was written between §4b and §5 — before both §5 and §6 — while covering
    the same subject as §6. Out-of-order numbering makes the cross-references
    other files use ("see §8 for the grammar") unreliable, and a topic split
    across two non-adjacent sections is how two versions of one rule drift apart.
    """
    headings = re.findall(r"^#{2,3} §(\d+[a-z]*)", _craft_text(), re.M)
    keys = [_section_key(h) for h in headings]
    assert keys == sorted(keys), "craft-reference sections are out of order: " + " ".join(
        f"§{h}" for h in headings
    )


def test_every_craft_section_number_is_unique():
    headings = re.findall(r"^#{2,3} §(\d+[a-z]*)", _craft_text(), re.M)
    dupes = {h for h in headings if headings.count(h) > 1}
    assert not dupes, f"duplicate craft-reference section number(s): {sorted(dupes)}"


@pytest.mark.parametrize("path", _docs(), ids=lambda p: str(p.relative_to(_CLAUDE)))
def test_craft_section_cross_references_resolve(path):
    """A pointer to a section that does not exist sends the agent nowhere."""
    known = set(re.findall(r"^#{2,3} §(\d+[a-z]*)", _craft_text(), re.M))
    if not known:
        pytest.skip("no craft sections found")
    referenced = set(re.findall(r"§(\d+[a-z]*)", path.read_text()))
    if path == _CRAFT:
        referenced -= known  # its own headings
    missing = sorted(referenced - known, key=_section_key)
    assert not missing, (
        f"{path.relative_to(_REPO)} points at craft-reference section(s) that do "
        f"not exist: {['§' + m for m in missing]}"
    )
