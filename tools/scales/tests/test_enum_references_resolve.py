"""Every `Enum.MEMBER` written in this package must exist.

`surface_composer` referenced `NoteJustification.MOTIVE`. The member is `MOTIF`,
so that line raised `AttributeError` — and it sits on the branch that runs only
when a phrase actually carries a motif transform. As `resolve_motifs`'s own
comment records, across the twelve pieces in the workspace not one had an
elected principal theme or a single placement on any of its 113 phrases, so the
theme system had never been active in a real run. The line had therefore never
executed, and the first piece to be given a theme crashed on it.

An unresolvable attribute on an Enum is a hard error at the moment it is
reached, which makes it invisible for exactly as long as its branch is dead.
That is a static fact, so it can be checked statically rather than waited for.
"""

from __future__ import annotations

import ast
import pathlib
from enum import Enum

import scales.enums as enums_module

_ROOT = pathlib.Path(enums_module.__file__).resolve().parent

_ENUMS = {
    name: obj
    for name, obj in vars(enums_module).items()
    if isinstance(obj, type) and issubclass(obj, Enum)
}


def test_enums_were_found():
    """Guard the guard: an empty set would make the test below vacuous."""
    assert len(_ENUMS) >= 5, sorted(_ENUMS)
    assert "NoteJustification" in _ENUMS


def test_every_enum_member_referenced_in_the_package_exists():
    bad = []
    for path in sorted(_ROOT.rglob("*.py")):
        if "tests" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:  # pragma: no cover
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            owner = node.value
            if not isinstance(owner, ast.Name) or owner.id not in _ENUMS:
                continue
            member = node.attr
            if not member.isupper():
                continue  # `.value`, `.name`, a method
            if not hasattr(_ENUMS[owner.id], member):
                bad.append(f"{path.relative_to(_ROOT.parent)}:{node.lineno} {owner.id}.{member}")
    assert not bad, (
        "reference(s) to enum members that do not exist — each raises "
        "AttributeError the moment its branch is reached, and stays invisible "
        "for as long as that branch is dead:\n  " + "\n  ".join(bad)
    )


def test_the_motif_branch_uses_the_member_that_exists():
    """The specific line, named, because it took a whole feature down with it."""
    src = (_ROOT / "surface_composer.py").read_text()
    assert "NoteJustification.MOTIVE" not in src
    assert "NoteJustification.MOTIF" in src
