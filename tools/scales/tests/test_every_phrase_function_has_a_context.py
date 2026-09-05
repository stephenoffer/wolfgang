"""A phrase function the planner writes must reach the ornament router.

`_resolve_ornaments` maps `slot.function` to an ornament context. Its table was
keyed on `PhraseFunction` members and covered seven, and the planner writes a
much wider vocabulary — `development`, `transition`, `climactic`, `sequence`,
`standing_on_dominant`, `resolution`, `extension`, `recapitulation`,
`retransition` are not enum members at all.

Two of the misses were NEAR MISSES on the enum's own spellings: the data says
`contrasting` and `varied_return` where the enum says `contrasting_theme` and
`return_varied`, so functions that WERE meant to be mapped fell through on a
naming difference — the dead-label shape from `project_dead_label_vocabulary`.

Measured over 426 slots in `workspace/`: **39% had no function-based ornament
context**, and chose ornaments from energy alone. Unlike the tonic-fallback
family (Addenda 73-77) this fails to silence rather than to a wrong value, which
is why nothing ever flagged it.
"""

import pathlib
import re

import pytest

from scales.piece_graph import PieceGraph
from scales.scales import _WORKSPACE

ROUTER = pathlib.Path(__file__).resolve().parents[1] / "context_router.py"


def _mapped_keys() -> set:
    src = ROUTER.read_text()
    start = src.index("context_map = {")
    end = src.index("}", start)
    block = src[start:end]
    literal = set(re.findall(r'"([a-z_]+)":', block))
    enum_keys = {"presentation", "cadential", "contrasting_theme", "return",
                 "return_varied", "closing", "coda"}
    return literal | enum_keys


def _functions_in_use() -> set:
    seen = set()
    for path in sorted(_WORKSPACE.glob("*/piece_graph.json")):
        if path.parent.name.startswith("_"):
            continue
        try:
            graph = PieceGraph.load(str(path))
        except Exception:
            continue
        for state in graph.phrases.values():
            fn = (getattr(state.slot, "function", "") or "").strip().lower()
            if fn:
                seen.add(fn)
    return seen


def test_there_are_functions_to_check():
    """A workspace with no pieces would make the assertion below vacuous."""
    assert len(_functions_in_use()) > 5


def test_every_function_the_planner_writes_is_mapped():
    unmapped = sorted(_functions_in_use() - _mapped_keys())
    assert not unmapped, f"no ornament context for: {unmapped}"


@pytest.mark.parametrize("near_miss,enum_spelling", [
    ("contrasting", "contrasting_theme"),
    ("varied_return", "return_varied"),
])
def test_the_near_miss_spellings_are_both_mapped(near_miss, enum_spelling):
    """Both spellings occur in real graphs; mapping only one is how a function
    that was meant to be handled silently is not."""
    keys = _mapped_keys()
    assert near_miss in keys and enum_spelling in keys


def test_an_unknown_function_still_yields_no_context():
    """Falsification: the fix must not invent a context for anything at all —
    the empty default is correct for a genuinely unknown function."""
    assert "not_a_real_function" not in _mapped_keys()
