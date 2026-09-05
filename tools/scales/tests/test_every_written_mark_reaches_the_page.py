"""Every notation field a composer can write must survive to the MusicXML.

`music_io._layer_to_event` calls itself "the single choke point between what the
agent wrote and what gets engraved: a field missing from this list is a mark that
vanishes with no error anywhere, which is how `expression` used to be lost."

That choke point is one of three hops — LayerEvent → EventIR → music21 →
MusicXML — and a mark can die at any of them. This test drives the real
`assemble` and greps the written file, so it fails if any hop drops a field.

The technique vocabulary is checked against `direct_compose._TECHNIQUES`, the
table the shorthand actually produces, rather than against a list written here:
the assembler handles `arpeggio`/`tremolo` in one branch and
`gliss`/`8va`/`8vb` in the spanner pass, and a value in neither would be
discarded silently ([[project_dead_label_vocabulary]]).
"""

from __future__ import annotations

import tempfile

import pytest

from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState, StyleDNA
from scales.piece_graph import PieceGraph

music21 = pytest.importorskip("music21")

#: field value -> a substring that must appear in the engraved MusicXML.
CASES = [
    ({"articulation": "staccato"}, "staccato"),
    ({"dynamic": "ff"}, "<ff"),
    ({"expression": "dolce"}, "dolce"),
    ({"ornament": "trill"}, "trill-mark"),
    ({"slur": "start"}, "<slur"),
    ({"hairpin": "cresc"}, "wedge"),

    ({"pedal": "down"}, "pedal"),
    ({"fingering": "3"}, "fingering"),
    ({"technique": "tremolo"}, "tremolo"),
    ({"technique": "8va"}, "octave-shift"),
]


def _engrave(fields: dict, pitch="C5", second: dict | None = None, second_pitch="D5") -> str:
    events = [
        LayerEvent(
            bar=1, beat=1.0, pitch=pitch, duration="h",
            role="structural", source_layer="principal_line", **fields,
        ),
        LayerEvent(
            bar=1, beat=3.0, pitch=second_pitch, duration="h",
            role="structural", source_layer="principal_line", **(second or {}),
        ),
    ]
    layer = LayerIR(
        principal_line=events,
        bass_foundation=[
            LayerEvent(bar=1, beat=1.0, pitch="C3", duration="w",
                       role="structural", source_layer="bass_foundation")
        ],
        meter=(4, 4), key="C major", phrase_id="p1",
    )
    graph = PieceGraph()
    graph.piece_id = "notation-probe"
    graph.style_dna = StyleDNA(composer_id="chopin")
    graph.phrases["p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=1,
                        key="C major", meter=(4, 4), tempo_bpm=90),
        realized=layer, agent_authored=True,
    )
    from scales.assembler import assemble

    with tempfile.TemporaryDirectory() as d:
        return open(str(assemble(graph, scope="full", output_dir=d))).read()


@pytest.mark.parametrize("fields,needle", CASES, ids=[list(f)[0] + ":" + str(list(f.values())[0]) for f, _ in CASES])
def test_the_mark_survives_to_the_musicxml(fields, needle):
    assert needle in _engrave(fields), f"{fields} never reached the page"


def test_a_tie_survives():
    """A tie needs something to tie TO — the same pitch, next attack. Engraving
    one against a different pitch is not a defect, it is not a tie."""
    xml = _engrave({"tie": "start"}, second={"tie": "stop"}, second_pitch="C5")
    assert "<tie" in xml


def test_a_glissando_survives():
    """A spanner needs both endpoints; one open end is not a glissando."""
    xml = _engrave({"technique": "gliss_start"}, second={"technique": "gliss_stop"})
    assert "slide" in xml or "glissando" in xml


def test_a_rolled_chord_survives():
    """`:arp` is only meaningful on a chord, so it needs its own case."""
    assert "arpeggiate" in _engrave({"technique": "arpeggio"}, pitch=["C5", "E5", "G5"])


def test_every_technique_the_shorthand_emits_is_handled_somewhere():
    """The shorthand's `_TECHNIQUES` table is the vocabulary that actually
    reaches an event. A value the assembler handles in neither its notation
    branch nor its spanner pass is discarded with no error."""
    import ast
    import pathlib

    from scales.direct_compose import _TECHNIQUES

    source = pathlib.Path("tools/scales/assembler.py").read_text()
    handled = {
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    missing = sorted(v for v in set(_TECHNIQUES.values()) if v not in handled)
    assert not missing, f"the shorthand emits techniques the assembler never reads: {missing}"


def test_every_layerevent_field_exists_on_eventir():
    """The choke point: a notation field on LayerEvent with nowhere to go in
    EventIR cannot reach the engraver at all."""
    import dataclasses

    from scales.models import EventIR

    layer_fields = {f.name for f in dataclasses.fields(LayerEvent)}
    event_fields = {f.name for f in dataclasses.fields(EventIR)}
    assert not (layer_fields - event_fields)
