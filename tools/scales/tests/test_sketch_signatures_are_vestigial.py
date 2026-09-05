"""`entry_signature` is written by nobody who reads it, and read by nobody.

Measured across `workspace/`: 426 phrases, ten with a sketch at all, and **zero**
carrying either signature. Only `sketch_proposer` (the engine fallback) and
`reducer` write them, and neither runs on the default agent path.

`exit_signature` at least has a reader — `composition_brief` renders it — so that
block is merely unreachable. `entry_signature` has no reader anywhere in the
package.

Continuity is carried instead by `_derive_continuation`, off the previous
phrase's REALIZED notes rather than its plan. That is the live mechanism and the
right one: it describes what was actually written, not what was intended.

This test exists so the next person to find the field does not wire it up
expecting data — the failure mode that made two complete modules dead code in
this repo before.
"""

import pathlib

import scales.composition_brief as cb
from scales.models import SketchIR

PACKAGE = pathlib.Path(cb.__file__).parent


def _sources():
    return {
        p.name: p.read_text()
        for p in PACKAGE.rglob("*.py")
        if "test" not in str(p) and p.name != "models.py"
    }


def test_the_fields_still_exist():
    assert "entry_signature" in SketchIR.__dataclass_fields__
    assert "exit_signature" in SketchIR.__dataclass_fields__


def test_entry_signature_has_no_reader():
    """If this fails someone gave it one — check they also gave it a writer that
    runs on the agent path, or the reader gets an empty object.

    Parsed, not grepped: the first version matched a line of PROSE in
    `piece_graph.py`'s docstring describing the bug this field once had, and
    reported the documentation as a reader.
    """
    import ast

    reads = []
    for name, src in _sources().items():
        try:
            tree = ast.parse(src)
        except SyntaxError:  # pragma: no cover - a file mid-edit
            continue
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "entry_signature"
                and isinstance(node.ctx, ast.Load)
            ):
                reads.append(f"{name}:{node.lineno}")
    assert not reads, f"entry_signature now has readers: {reads}"


def test_the_live_continuity_path_is_the_realized_one():
    """`_derive_continuation` is what actually carries phrase-to-phrase state."""
    assert hasattr(cb, "_derive_continuation")


def test_the_field_is_marked_as_superseded():
    """The comment is the deliverable here — the code change is nil."""
    src = (PACKAGE / "models.py").read_text()
    idx = src.index("entry_signature: EntryExitState")
    assert "SUPERSEDED" in src[max(0, idx - 1200) : idx]
