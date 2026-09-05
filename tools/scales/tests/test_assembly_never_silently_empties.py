"""An empty score is never the right answer when there are notes.

`assemble` routes on the CONTRACT's instrumentation, and `_build_piano_score`
reads the treble/bass staves that the PIANO branch of `layer_ir_to_event_ir`
produces. Phrases realized into ORCHESTRAL layers emit orchestral staff names
instead — `foreground`, `harmony`, `punctuation`.

So when the contract says `solo_piano` while the phrases hold orchestral
material, the piano path matches nothing and writes a score with one empty part.
Not an error, not a warning: a valid MusicXML file on disk with no music in it.

    contract says choir        -> 2 parts, 10 notes
    contract wrong or unset    -> 1 part,   0 notes     <- 10 events in, 0 out

The contract says which path to take; the notes say whether it can work. Where
the piano path would produce nothing and orchestral material exists, the
evidence wins and the assembler logs that it overrode.

This is the last stage in the pipeline, so anything lost here is lost for good —
and it is the stage where a defect is hardest to notice, because the file
opens.
"""

import shutil
import tempfile

import music21
import pytest

from scales.assembler import _PIANO_STAVES, assemble
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _graph(contract_instrumentation, layer_instrumentation, orchestral=True):
    graph = PieceGraph()
    graph.piece_id = "_t_assembly"
    if contract_instrumentation:
        graph.contract.target.instrumentation = contract_instrumentation
    slot = PhraseSlot(
        phrase_id="m1_a_p1",
        section_id="m1_a",
        bar_start=1,
        bar_count=2,
        key="D minor",
        meter=(4, 4),
        cadence_bar=2,
        cadence_target="PAC",
    )
    ir = LayerIR(
        phrase_id="m1_a_p1",
        key="D minor",
        meter=(4, 4),
        instrumentation=layer_instrumentation,
        bar_count=2,
    )
    for bar in (1, 2):
        for i, pitch in enumerate(["D5", "E5", "F5", "E5"]):
            target = "foreground" if orchestral else "principal_line"
            ir.ensure_layer(target).append(
                LayerEvent(bar=bar, beat=1.0 + i, pitch=pitch, duration="q")
            )
        target = "harmonic_mass" if orchestral else "bass_foundation"
        ir.ensure_layer(target).append(LayerEvent(bar=bar, beat=1.0, pitch="F4", duration="w"))
    graph.phrases["m1_a_p1"] = PhraseState(slot=slot, realized=ir, status="realized")
    return graph


def _assemble(graph):
    out = tempfile.mkdtemp()
    try:
        score = music21.converter.parse(assemble(graph, scope="full", output_dir=out))
        parts = list(score.parts)
        return len(parts), sum(1 for p in parts for _ in p.recurse().notes)
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_a_correct_contract_assembles_everything():
    assert _assemble(_graph("choir", "choir")) == (2, 10)


def test_a_wrong_contract_does_not_empty_the_score():
    """The regression this exists for: 10 events in, 0 notes out, no error."""
    parts, notes = _assemble(_graph(None, "choir"))
    assert notes == 10, "orchestral material was dropped by the piano path"
    assert parts >= 2


def test_a_real_piano_piece_still_takes_the_piano_path():
    """The override must fire ONLY where the piano path would find nothing.
    Two staves named Piano is the signature of the keyboard route."""
    graph = _graph("solo_piano", "solo_piano", orchestral=False)
    parts, notes = _assemble(graph)
    assert notes == 10
    out = tempfile.mkdtemp()
    try:
        score = music21.converter.parse(assemble(graph, scope="full", output_dir=out))
        assert [p.partName for p in score.parts] == ["Piano", "Piano"]
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_the_piano_staff_names_are_the_ones_the_converter_emits():
    """If the piano branch ever renames its staves, the override would fire on
    every piece. Pin the two names it actually produces."""
    from scales.music_io import layer_ir_to_event_ir

    ir = LayerIR(key="C", meter=(4, 4), instrumentation="solo_piano", bar_count=1)
    ir.principal_line.append(LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"))
    ir.bass_foundation.append(LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q"))
    assert {e.staff for e in layer_ir_to_event_ir(ir)} <= _PIANO_STAVES


def test_an_empty_piece_is_left_alone():
    """No events means nothing to rescue; the override must not fire."""
    graph = PieceGraph()
    graph.piece_id = "_t_empty"
    with pytest.raises(Exception):
        _assemble(graph)
