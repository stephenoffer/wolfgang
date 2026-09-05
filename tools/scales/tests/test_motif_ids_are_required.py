"""A motif with no id is inert, and used to be stored anyway.

`resolve_motifs` is documented "Validate and store motif definitions" and
validated nothing: `mdef.get("motif_id", "")` put a nameless motif in the bank
under the empty string. An empty id can never be elected — `elect_principal_theme`
returns it and `_place_principal_theme` rejects it with `if not
graph.principal_theme_id` — and no `MotifTransform` can refer to it.

If it is the only motif, the theme system goes inert and reports
`sections_given_a_theme_statement: 0` with no reason given. The commonest way to
produce one is writing `"id"` instead of `"motif_id"`, which is exactly how this
was found.

The theme mechanism itself works: with a well-formed motif, five sections of a
ternary form receive a placement.
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.piece_graph import PieceGraph
from scales.scales import build_form_graph, compile_style, init_workspace, resolve_motifs

PID = "_motif_validation_probe"
GOOD = {
    "motif_id": "A",
    "character": "the opening idea",
    "interval_contour": [0, 2, 2, -2],
    "rhythm_cell": ["q", "e", "e", "h"],
}


@pytest.fixture
def piece():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="An andante in F major for piano")
    compile_style(PID, composers=["mozart"])
    build_form_graph(PID, form="ternary", key="F major", tempo_bpm=72, meter=(4, 4))
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _bank(pid):
    path = scales_mod._WORKSPACE / pid / "piece_graph.json"
    return PieceGraph.load(str(path))


def test_a_definition_with_no_id_is_refused(piece):
    result = resolve_motifs(piece, [{"id": "A", "interval_contour": [0, 2]}])
    assert "error" in result
    assert "motif_id" in result["error"]


def test_the_refusal_names_the_likely_mistake(piece):
    """`"id"` instead of `"motif_id"` is how this is produced."""
    result = resolve_motifs(piece, [{"id": "A"}])
    assert "not `id`" in result.get("hint", "")


def test_nothing_is_stored_when_a_definition_is_refused(piece):
    resolve_motifs(piece, [{"id": "A", "interval_contour": [0, 2]}])
    assert not _bank(piece).motif_bank, "a refused batch must not half-apply"


def test_a_well_formed_motif_is_elected_and_placed(piece):
    result = resolve_motifs(piece, [GOOD])
    assert result["principal_theme_id"] == "A"
    assert result["sections_given_a_theme_statement"] >= 1
    graph = _bank(piece)
    placed = [pid for pid, ps in graph.phrases.items() if ps.slot.motif_transforms]
    assert placed, "the theme mechanism must reach the phrase slots"


def test_the_placement_names_the_motif(piece):
    resolve_motifs(piece, [GOOD])
    graph = _bank(piece)
    slot = next(ps.slot for ps in graph.phrases.values() if ps.slot.motif_transforms)
    assert slot.motif_transforms[0].params.get("motif_id") == "A"
