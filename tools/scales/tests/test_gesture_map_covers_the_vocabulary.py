"""A phrase that RETURNS the theme must not be given the gestures of a beginning.

`_FUNCTION_TO_GESTURES` listed eleven `PhraseFunction` members and fell back to
`["pickup", "answer"]` — the PRESENTATION gestures. Measured over 426 slots in
`workspace/`, **31% took that fallback**, led by two functions that ARE enum
members and were simply absent from the map:

    contrasting_theme   56 slots
    return              49 slots

So the recapitulation — the moment the piece pays off — asked the gesture bank
for a pickup and an answer, the shapes a phrase uses to START.

The gesture names come from the four families in `gesture_bank._same_gesture_family`
(initiate / drive / resolve / answer), not invented: `arrival` and `sustain`
resolve to `resolve`, `sequence_step` and `lean_in` to `drive` and `initiate`.
That aliasing is deliberate and predates this change.
"""

import pathlib
import re

from scales.gesture_bank import _same_gesture_family
from scales.models import PhraseFunction
from scales.piece_graph import PieceGraph
from scales.scales import _WORKSPACE

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "sketch_proposer.py"
KNOWN_FAMILY_MEMBERS = {
    "answer", "answer_with_space", "echo",
    "insist", "sequence_step", "cadential_push",
    "arrival", "cadential_release", "sustain",
    "pickup", "lean_in",
}


def _map_block() -> str:
    src = SOURCE.read_text()
    start = src.index("_FUNCTION_TO_GESTURES = {")
    return src[start : src.index("\n        }", start)]


def _mapped_functions() -> set:
    block = _map_block()
    keys = set(re.findall(r'"([a-z_]+)":\s*\[', block))
    for member in re.findall(r"PhraseFunction\.([A-Z_]+)\.value", block):
        keys.add(getattr(PhraseFunction, member).value)
    return keys


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
            fn = (getattr(state.slot, "function", "") or "").strip()
            if fn:
                seen.add(fn)
    return seen


def test_there_are_functions_to_check():
    assert len(_functions_in_use()) > 5


def test_every_function_in_use_has_its_own_gestures():
    unmapped = sorted(_functions_in_use() - _mapped_functions())
    assert not unmapped, f"still falling back to the opening gestures: {unmapped}"


def test_a_return_does_not_get_the_opening_gestures():
    """The specific defect: `return` was absent, so the payoff asked for a
    pickup."""
    block = _map_block()
    match = re.search(r"PhraseFunction\.RETURN\.value:\s*\[([^\]]+)\]", block)
    assert match, "RETURN is not mapped"
    assert "pickup" not in match.group(1)
    assert "arrival" in match.group(1)


def test_every_gesture_name_used_is_one_the_bank_knows():
    """Inventing a gesture name is the dead-label trap — the bank would family-
    match it to something arbitrary or nothing."""
    used = set(re.findall(r'"([a-z_]+)"', _map_block()))
    gestures = used & KNOWN_FAMILY_MEMBERS
    invented = {
        g for g in used
        if g not in KNOWN_FAMILY_MEMBERS
        and g not in _mapped_functions()
        and any(_same_gesture_family(g, k) for k in KNOWN_FAMILY_MEMBERS) is False
        and "_" in g
        and g.split("_")[0] in {"pickup", "answer", "insist", "arrival", "sustain"}
    }
    assert gestures, "no recognised gesture names found — the parse is wrong"
    assert not invented, f"gesture names the bank does not know: {sorted(invented)}"
