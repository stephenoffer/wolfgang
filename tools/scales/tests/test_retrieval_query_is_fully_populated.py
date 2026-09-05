"""A fifth of the exemplar relevance model was a constant.

`PhraseQuery` scores retrieval on `contour_class`, `entry_texture` and
`cadence_distance` — 0.20 of the ranking between them. **No caller set any of
them.** All three callers (the brief, the sketch proposer, the surface composer)
pass function, cadence, length and key mode and stop. Unset, each dimension
scores a flat 0.5 for every candidate, so it could not change which exemplar was
retrieved — and the exemplars are what the agent adapts when it writes notes.

The planner knows all three; it just never said so.

Also pinned here: the two rules for `contour_class` I tried BEFORE this one, each
of which returned a single value for all 26 planned slots. A discriminator with
one value discriminates nothing, and looks like it is working
([[feedback_two_kinds_of_detector_falsification]] — a detector that FINDS needs
"would it find what is definitely there?").
"""

from __future__ import annotations

from collections import Counter

from scales import dramatic_plan as DP
from scales.composition_brief import _slot_contour_class, _slot_entry_texture
from scales.models import StyleDNA
from scales.scales import _build_sonata, _build_ternary

#: Measured over 9,569 indexed corpus phrases, `melody_directions` contains
#: exactly these and nothing else. A value outside the set scores every
#: candidate 0.0 rather than a neutral 0.5.
CORPUS_CONTOURS = {"static", "descending", "ascending"}


def _planned(build):
    slots = build("F major", 90, (4, 4), StyleDNA())
    DP.build(slots)
    return slots


def test_the_contour_vocabulary_matches_the_corpus():
    for build in (_build_ternary, _build_sonata):
        for slot in _planned(build):
            value = _slot_contour_class(slot)
            assert value is None or value in CORPUS_CONTOURS, value


def test_the_contour_actually_varies():
    """The failing condition: one value for every phrase. Two earlier rules,
    both read off the register curve, did exactly that — every planned register
    curve is the same arch."""
    for build in (_build_ternary, _build_sonata):
        spread = Counter(_slot_contour_class(s) for s in _planned(build))
        assert len(spread) >= 3, spread


def test_the_contour_follows_the_drama():
    """A phrase that intensifies rises; one that retreats falls."""
    slots = _planned(_build_sonata)
    by_role = {s.dramatic_role: _slot_contour_class(s) for s in slots}
    for role in ("intensify", "crisis", "depart"):
        if role in by_role:
            assert by_role[role] == "ascending", role
    for role in ("retreat", "close"):
        if role in by_role:
            assert by_role[role] == "descending", role


def test_every_phrase_knows_the_texture_it_enters_in():
    for build in (_build_ternary, _build_sonata):
        slots = _planned(build)
        assert all(_slot_entry_texture(s) for s in slots)


def test_the_query_the_brief_builds_carries_all_three():
    """The point of the fix: the retrieval that feeds the agent's exemplars.

    Located through the AST rather than `inspect.getsource`, which reads the file
    at line numbers recorded when the module was imported — so anything editing
    the file mid-run makes it return a different function's text. This very test
    failed that way once and passed in isolation.
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("tools/scales/composition_brief.py").read_text())
    node = next(
        (
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "_phrase_shape"
        ),
        None,
    )
    assert node is not None
    found = {
        kw.arg
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "PhraseQuery"
        for kw in call.keywords
        if kw.arg
    }
    assert {"cadence_distance", "contour_class", "entry_texture"} <= found, sorted(found)


def test_all_three_query_sites_were_updated():
    """There are three `PhraseQuery` constructors and all three were blind. A
    fix to one of them leaves the engine paths retrieving on a constant."""
    import ast
    import pathlib

    expected = {
        "composition_brief.py": {"cadence_distance", "contour_class", "entry_texture"},
        "sketch_proposer.py": {"cadence_distance", "contour_class", "entry_texture"},
        # A PhraseControlIR carries no dramatic role, and every rule read off a
        # register curve returns one value for every phrase — so `contour_class`
        # is deliberately left unset there. Unset scores a neutral 0.5; a wrong
        # word scores 0.0 for every candidate.
        "surface_composer.py": {"cadence_distance", "entry_texture"},
    }
    for filename, wanted in expected.items():
        tree = ast.parse((pathlib.Path("tools/scales") / filename).read_text())
        found: set[str] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "PhraseQuery"
            ):
                found |= {kw.arg for kw in node.keywords if kw.arg}
        assert wanted <= found, f"{filename} is missing {sorted(wanted - found)}"
