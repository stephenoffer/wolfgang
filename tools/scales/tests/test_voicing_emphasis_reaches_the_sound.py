"""The plan said "the bass carries the line here" and nothing listened.

`performance_renderer.apply_voicing_priorities` exists so a phrase can name which
voice is brought out — its docstring: *"Emphasise the voices the plan names,
instead of always the melody. A plan that says the bass carries the line, or that
an inner voice should be brought out, had no way to say so."* It writes
`PerformanceIR.voicing_emphasis` per bar.

**Nothing read it.** Grepping every consumer, `voicing_emphasis` was referenced
only by `performance_renderer` itself (to filter its own list) and by tests. The
MIDI renderer — which turns velocity into the sound the `music-critic` judges —
never applied it, while its own module docstring claims the dynamic curve comes
"with melody voicing emphasis". A phrase planned around a singing bass rendered
identically to one planned around a singing melody.

That is [[project_correct_analysis_wired_to_nothing]], and the tests made it
harder to see rather than easier: they asserted the emphasis list was correctly
BUILT, which was true, and never that it changed a note.
"""

from __future__ import annotations

import tempfile

import pytest

from scales.midi_renderer import _emphasis_by_bar, render_midi
from scales.models import (
    LayerEvent,
    LayerIR,
    PhraseSlot,
    PhraseState,
    StyleDNA,
    VoicingEmphasis,
)
from scales.piece_graph import PieceGraph

music21 = pytest.importorskip("music21")


def _graph() -> PieceGraph:
    # `source_layer` is what the renderer keys voicing on, and `direct_compose`
    # sets it on every event it writes — a fixture that omits it is testing a
    # shape production never has.
    melody = [
        LayerEvent(
            bar=1, beat=float(i + 1), pitch=p, duration="q",
            role="structural", source_layer="principal_line",
        )
        for i, p in enumerate(["C5", "E5", "G5", "C6"])
    ]
    bass = [
        LayerEvent(
            bar=1, beat=float(i + 1), pitch=p, duration="q",
            role="structural", source_layer="bass_foundation",
        )
        for i, p in enumerate(["C3", "G2", "E3", "C3"])
    ]
    layer = LayerIR(
        principal_line=melody, bass_foundation=bass, meter=(4, 4), key="C major", phrase_id="p1"
    )
    graph = PieceGraph()
    graph.style_dna = StyleDNA(composer_id="chopin")
    graph.phrases["p1"] = PhraseState(
        slot=PhraseSlot(
            phrase_id="p1",
            section_id="m1_a",
            bar_start=1,
            bar_count=1,
            key="C major",
            meter=(4, 4),
            tempo_bpm=90,
        ),
        realized=layer,
        agent_authored=True,
    )
    return graph


def _bass_velocities(path: str) -> list[int]:
    score = music21.converter.parse(path)
    out = []
    for note in score.recurse().notes:
        if any(p.midi < 55 for p in note.pitches):
            out.append(note.volume.velocity or 64)
    return out


def _render_with(emphasis) -> list[int]:
    import scales.performance_renderer as PR

    real = PR.build_performance_ir
    if emphasis is not None:

        def patched(*args, **kwargs):
            perf = real(*args, **kwargs)
            perf.voicing_emphasis = emphasis
            return perf

        PR.build_performance_ir = patched
    try:
        with tempfile.TemporaryDirectory() as d:
            return _bass_velocities(render_midi(_graph(), output_dir=d))
    finally:
        PR.build_performance_ir = real


def test_a_bass_led_plan_makes_the_bass_louder():
    """The failure this fixes: identical renders."""
    default = _render_with(None)
    bass_led = _render_with(
        [VoicingEmphasis(bar=1, beat=1.0, voice="bass", boost=0.30)]
    )
    assert default and bass_led
    assert sum(bass_led) / len(bass_led) > sum(default) / len(default)


def test_emphasising_the_melody_does_not_lift_the_bass():
    """The emphasis has to be selective, or it is just a volume knob."""
    default = _render_with(None)
    melody_led = _render_with(
        [VoicingEmphasis(bar=1, beat=1.0, voice="melody", boost=0.30)]
    )
    assert sum(melody_led) / len(melody_led) == pytest.approx(
        sum(default) / len(default), abs=1.0
    )


def test_the_plans_voice_names_map_onto_real_layers():
    by_bar = _emphasis_by_bar(
        type("P", (), {"voicing_emphasis": [
            VoicingEmphasis(bar=3, beat=1.0, voice="bass", boost=0.2),
            VoicingEmphasis(bar=3, beat=1.0, voice="inner", boost=0.1),
        ]})()
    )
    assert by_bar[3]["bass_foundation"] == 0.2
    assert by_bar[3]["counter_reply"] == 0.1
    assert by_bar[3]["response_layer"] == 0.1


def test_a_layer_named_directly_still_works():
    """A plan may name a layer rather than a role word."""
    by_bar = _emphasis_by_bar(
        type("P", (), {"voicing_emphasis": [
            VoicingEmphasis(bar=1, beat=1.0, voice="ornamental_surface", boost=0.2)
        ]})()
    )
    assert by_bar[1]["ornamental_surface"] == 0.2


def test_no_performance_ir_is_not_an_error():
    assert _emphasis_by_bar(None) == {}


def test_a_graph_with_no_piece_id_still_writes_a_readable_file():
    """`scoped_basename("")` returned "", so the writers produced a file named
    ".mid" — hidden on Unix, and music21 refuses to parse it back. Silent until
    something tries to read its own output, which is how this was found."""
    from scales.assembler import scoped_basename

    assert scoped_basename("", "full") == "piece"
    assert scoped_basename(None, "full") == "piece"
    assert scoped_basename("", "section-m1_a") == "piece__section-m1_a"
    assert scoped_basename("real-piece", "full") == "real-piece"
