"""The score being transformed is not part of the score that comes out.

`load_source_score` reads a source in as phrases marked `salience='source'` so
the composer can see what must survive. `_collect_events` had no salience
filter, so it engraved them as if they were the piece.

Assembling a `reduce_to_piano` of a real string quartet put the 11 source
phrases (608 events, bars 1-41) AND the reduction (312 events, bars 1-41) onto
the same two staves: **40 of the 41 right-hand bars held 6.0 beats in a 3/4
bar**, every bar of the source printed on top of every bar of the reduction.

The LayerIR was correct the whole time — 41 bars, none over 3.0 beats — so no
gate, validator or ear check could see it. It was only visible in the exported
file, which is the lesson recorded in [[project_assembler_voice_bug]]: read the
assembled score back.

All five source-based modes were affected (variation, style_transfer,
continue_piece, orchestrate, reduce_to_piano).
"""

import pytest
from music21 import converter

from scales.assembler import assemble
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _phrase(pid, bar, pitches, salience):
    layer = LayerIR(phrase_id=pid, instrumentation="solo_piano", key="C major", meter=(3, 4))
    for i, p in enumerate(pitches):
        layer.principal_line.append(LayerEvent(bar=bar, beat=1.0 + i, pitch=p, duration="q"))
        layer.bass_foundation.append(LayerEvent(bar=bar, beat=1.0 + i, pitch="C3", duration="q"))
    layer.bar_count = 1
    return PhraseState(
        slot=PhraseSlot(
            phrase_id=pid, section_id="m1_a", bar_start=bar, bar_count=1,
            key="C major", meter=(3, 4), tempo_bpm=100,
        ),
        realized=layer,
        agent_authored=(salience != "source"),
        salience=salience,
    )


def _graph():
    g = PieceGraph.create("t-source-not-engraved", "reduce_to_piano", "a reduction")
    g.contract.target.instrumentation = "solo_piano"
    # both cover bar 1, exactly as a real source and its reduction do
    g.phrases["src_p1"] = _phrase("src_p1", 1, ["G4", "A4", "B4"], "source")
    g.phrases["red_p1"] = _phrase("red_p1", 1, ["C5", "D5", "E5"], "normal")
    return g


def _bar_lengths(path):
    score = converter.parse(path)
    out = []
    for part in score.parts:
        ts = None
        for m in part.getElementsByClass("Measure"):
            ts = m.timeSignature or ts
            if ts:
                out.append((float(m.duration.quarterLength), float(ts.barDuration.quarterLength)))
    return out


def test_a_source_phrase_is_not_printed_over_the_composed_one(tmp_path):
    path = assemble(_graph(), output_dir=str(tmp_path))
    lengths = _bar_lengths(path)
    assert lengths, "nothing was engraved"
    for got, want in lengths:
        assert abs(got - want) < 0.01, f"bar holds {got} beats in a {want}-beat meter"

    pitches = {
        str(p) for part in converter.parse(path).parts for n in part.recurse().notes for p in n.pitches
    }
    assert {"C5", "D5", "E5"} <= pitches, "the composed music must be engraved"
    assert not ({"G4", "A4", "B4"} & pitches), "the source must not be engraved"


def test_the_source_can_still_be_asked_for_explicitly(tmp_path):
    path = assemble(_graph(), output_dir=str(tmp_path), include_source=True)
    pitches = {
        str(p) for part in converter.parse(path).parts for n in part.recurse().notes for p in n.pitches
    }
    assert {"G4", "A4", "B4"} <= pitches


def test_a_graph_holding_only_source_says_so(tmp_path):
    """Assembling right after loading a source is a real mistake to make, and
    'No realized phrases found' would be a lie — there are eleven."""
    g = PieceGraph.create("t-only-source", "variation", "a variation")
    g.contract.target.instrumentation = "solo_piano"
    g.phrases["src_p1"] = _phrase("src_p1", 1, ["G4", "A4", "B4"], "source")
    with pytest.raises(ValueError, match="SOURCE phrase"):
        assemble(g, output_dir=str(tmp_path))


def test_an_ordinary_piece_is_unaffected(tmp_path):
    """The filter must not touch a piece that has no source at all."""
    g = PieceGraph.create("t-no-source", "compose_from_text", "a piece")
    g.contract.target.instrumentation = "solo_piano"
    g.phrases["p1"] = _phrase("p1", 1, ["C5", "D5", "E5"], "normal")
    path = assemble(g, output_dir=str(tmp_path))
    for got, want in _bar_lengths(path):
        assert abs(got - want) < 0.01
