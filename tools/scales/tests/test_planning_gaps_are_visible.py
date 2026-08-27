"""Composing an unplanned piece is legal, silent, and quietly much worse.

`build_form_graph` → `run_scales_section` is a legal call sequence that skips
planning entirely, and every planning input has a fallback that produces
plausible-looking output. A peer session measured texture, ties, cadences and
register all session on pieces with NO thematic material, because its harness
took exactly that route and nothing objected. Those numbers were valid for what
they measured; they were never measuring the whole system.

Reported, never blocking — composing an unplanned piece deliberately while
testing something else is reasonable; doing it by accident and believing the
result is not.
"""

from __future__ import annotations

import shutil

import pytest

from scales.scales import (
    _WORKSPACE,
    _load_graph,
    build_form_graph,
    compile_style,
    get_composition_brief,
    init_workspace,
    planning_gaps,
    resolve_motifs,
    save_narrative,
)

_PIECE = "test-planning-gaps-20260827"


@pytest.fixture
def bare():
    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)
    init_workspace(
        _PIECE, "compose_from_text", "probe", {"target": {"instrumentation": "solo_piano"}}
    )
    build_form_graph(_PIECE, "binary", "C major", tempo_bpm=120, meter=(4, 4))
    yield _PIECE
    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)


def _missing(piece):
    return {g["missing"] for g in planning_gaps(_load_graph(piece))}


def test_an_unplanned_piece_names_every_missing_input(bare):
    assert _missing(bare) == {"style", "motifs", "narrative", "reference_study"}


def test_each_gap_says_what_it_costs_and_how_to_fix_it(bare):
    for gap in planning_gaps(_load_graph(bare)):
        assert gap["costs"].strip(), gap
        assert "(" in gap["fix"] or "/" in gap["fix"], gap


def test_compiling_a_style_closes_the_style_gap(bare):
    compile_style(bare, composers=["mozart"])
    assert "style" not in _missing(bare)


def test_resolving_motifs_closes_the_motif_gap(bare):
    resolve_motifs(
        bare,
        [
            {
                "motif_id": "head",
                "interval_contour": [0, 2, 2, -1],
                "rhythm_cell": ["e", "e", "e", "q"],
            }
        ],
    )
    assert "motifs" not in _missing(bare)


def test_the_narrative_gap_distinguishes_authored_prose_from_the_role_table(bare):
    """A gap that cannot fire is worse than no gap.

    `_narrative_from_slots` fills `character` for every section from
    `ROLE_INTENT`, so "is character non-empty" is true on every piece ever built
    and would never report anything. And splitting the text on ";" to compare
    the parts does not work either — the table's own entries contain semicolons,
    so splitting shreds them and every derived section looks authored. That
    version passed its test for the wrong reason.
    """
    assert "narrative" in _missing(bare), "role-table prose was taken for authored prose"
    save_narrative(
        bare,
        sections=[
            {
                "id": "m1_a",
                "label": "A",
                "bar_start": 1,
                "bar_end": 8,
                "character": "a held breath before dawn; the room already knows",
            }
        ],
    )
    assert "narrative" not in _missing(bare)


def test_a_derived_section_is_not_mistaken_for_authored_even_when_it_is_long():
    """Directly, on the table's own text — the case the split version got wrong."""
    from types import SimpleNamespace

    from scales.dramatic_plan import ROLE_INTENT

    entries = list(ROLE_INTENT.values())[:3]
    graph = SimpleNamespace(
        style_dna=None,
        motif_bank={},
        reference_studies={},
        narrative=SimpleNamespace(sections=[SimpleNamespace(character="; ".join(entries))]),
    )
    assert "narrative" in {g["missing"] for g in planning_gaps(graph)}


def test_the_brief_itself_carries_the_warning(bare):
    """The composing agent reads the brief and nothing else.

    A brief built on an uncompiled style still renders — generic bands, no
    fingerprints — and reads exactly like one that was armed.
    """
    text = get_composition_brief(bare, "m1_a_p1")
    assert "PLANNING NEVER SUPPLIED" in text, text[:400]
    assert "compile_style" in text
