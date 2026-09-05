"""The critic must hear the piece, not the piece plus its source.

Companion to `test_source_is_not_engraved`. Fixing `_collect_events` fixed the
printed score; three other passes read `piece_graph.phrases` on their own and
were still counting SOURCE phrases as the composition:

  * `render_midi` — the preview, which is what the music-critic listens to and
    the sole driver of artistic revision. A variation's preview played G4-A4-B4
    (the source) and C5-D5-E5 (the piece) in the same bar.
  * `_section_barlines` and `_movement_bounds` — double barlines and movement
    headings taken from the source's own `m1_source` span.

`_apply_performance_marks` had a second, unrelated defect found on the way: its
own private scope matcher, understanding only "section-<id>" and falling
through to include everything else — so assembling one movement of a
multi-movement work took its rit./a tempo/con pedale from ALL movements. The
same defect is recorded against the MIDI renderer's private copy; there is one
`_in_scope`, and it is now the only matcher in the file.
"""

import tempfile

from music21 import converter

from scales.assembler import assemble
from scales.midi_renderer import render_midi
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph

SOURCE_PITCHES = ["G4", "A4", "B4"]
PIECE_PITCHES = ["C5", "D5", "E5"]


def _phrase(pid, section, bar, pitches, salience="normal"):
    layer = LayerIR(phrase_id=pid, instrumentation="solo_piano", key="C major", meter=(4, 4))
    for i, p in enumerate(pitches):
        layer.principal_line.append(LayerEvent(bar=bar, beat=1.0 + i, pitch=p, duration="q"))
        layer.bass_foundation.append(LayerEvent(bar=bar, beat=1.0 + i, pitch="C3", duration="q"))
    layer.bar_count = 1
    return PhraseState(
        slot=PhraseSlot(
            phrase_id=pid, section_id=section, bar_start=bar, bar_count=1,
            key="C major", meter=(4, 4), tempo_bpm=100,
        ),
        realized=layer,
        agent_authored=(salience != "source"),
        salience=salience,
    )


def _variation_graph():
    g = PieceGraph.create("t-preview-source", "variation", "a variation")
    g.contract.target.instrumentation = "solo_piano"
    g.phrases["src_p1"] = _phrase("src_p1", "m1_source", 1, SOURCE_PITCHES, "source")
    g.phrases["new_p1"] = _phrase("new_p1", "m1_a", 1, PIECE_PITCHES)
    return g


def _heard(path):
    return {str(p) for n in converter.parse(path).recurse().notes for p in n.pitches}


def test_the_preview_does_not_play_the_source():
    path = render_midi(_variation_graph(), output_dir=tempfile.mkdtemp())
    heard = _heard(path)
    assert set(PIECE_PITCHES) <= heard, "the composed music must be audible"
    assert not (set(SOURCE_PITCHES) & heard), "the source must not be audible"


def test_the_source_can_still_be_previewed_on_request():
    path = render_midi(_variation_graph(), output_dir=tempfile.mkdtemp(), include_source=True)
    assert set(SOURCE_PITCHES) <= _heard(path)


def test_assembling_one_movement_takes_marks_only_from_it():
    """`_apply_performance_marks` had its own scope matcher that understood only
    'section-<id>' and included everything else, so one movement of a
    multi-movement work was marked from all of them."""
    g = PieceGraph.create("t-preview-scope", "compose_from_text", "two movements")
    g.contract.target.instrumentation = "solo_piano"
    for i, (section, bar) in enumerate([("m1_a", 1), ("m1_a", 2), ("m2_a", 3), ("m2_a", 4)]):
        g.phrases[f"p{i}"] = _phrase(f"p{i}", section, bar, PIECE_PITCHES)

    path = assemble(g, scope="movement-1", output_dir=tempfile.mkdtemp())
    score = converter.parse(path)
    bars = {m.number for part in score.parts for m in part.getElementsByClass("Measure")}
    assert len(bars) == 2, f"movement 1 is two bars, got {sorted(bars)}"
    # every mark must sit inside the two bars that were actually engraved
    for part in score.parts:
        for m in part.getElementsByClass("Measure"):
            assert m.number in bars
