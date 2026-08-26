"""Hand-enumerated layer lists cover the five PIANO layers; LayerIR has eleven.

That shape has now produced the same silent failure three times in this
codebase — a check that runs, computes, and reads an empty drawer, which is
indistinguishable from a clean result. These pin the derived accessors that
replaced the enumerations.
"""

from scales.models import LayerEvent, LayerIR
from scales.validator import validate_layer_ir


def _note(pitch, layer, bar=1, beat=1.0, duration="w"):
    return LayerEvent(
        bar=bar, beat=beat, pitch=pitch, duration=duration, role="structural", source_layer=layer
    )


def test_every_layer_holding_notes_is_enumerated():
    """Derived from the dataclass, so a layer added tomorrow is covered."""
    names = LayerIR.event_layer_names()
    for expected in (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    ):
        assert expected in names, f"{expected} is not reached"


def test_all_events_reaches_orchestral_layers_and_inner_voices():
    ir = LayerIR(phrase_id="p", instrumentation="orchestra")
    ir.principal_line = [_note("C5", "principal_line")]
    ir.harmonic_mass = [_note("C3", "harmonic_mass")]
    ir.inner_voices = {"vln2": [_note("E4", "vln2", beat=2.0)]}
    assert len(ir.all_events()) == 3
    assert {n for n, _ in ir.event_layers()} == {"principal_line", "harmonic_mass", "vln2"}


def test_an_out_of_range_note_in_an_orchestral_layer_is_an_error():
    """RANGE is one of the strict physical constraints — the only kind that
    blocks a commit. It enumerated the five piano layers, so a note anywhere in
    the six orchestral ones was never checked at all: MIDI 120 in
    `harmonic_mass` produced zero findings.
    """
    ir = LayerIR(phrase_id="p", instrumentation="orchestra", meter=(4, 4), bar_count=1)
    ir.harmonic_mass = [_note("C9", "harmonic_mass")]
    report = validate_layer_ir(ir)
    issues = [i for i in getattr(report, "issues", []) if i.category == "range"]
    assert issues, "an out-of-range note in an orchestral layer must be an error"
    assert issues[0].severity == "error"


def test_melody_line_finds_the_tune_in_either_kind_of_piece():
    """An orchestral LayerIR carries its tune in `foreground` and leaves
    `principal_line` empty, so every detector reading `principal_line` and
    calling it "the melody" reported nothing wrong for orchestral pieces."""
    piano = LayerIR(phrase_id="p")
    piano.principal_line = [_note("C5", "principal_line")]
    orch = LayerIR(phrase_id="o", instrumentation="orchestra")
    orch.foreground = [_note("G5", "foreground")]

    assert [e.pitch for e in piano.melody_line()] == ["C5"]
    assert [e.pitch for e in orch.melody_line()] == ["G5"]
    assert LayerIR(phrase_id="x").melody_line() == []


def test_ensure_layer_handles_the_two_different_defaults():
    """The five piano layers default to `[]` and the six orchestral ones to
    `None`, so a bare `getattr(ir, name).extend(...)` works for one kind and
    raises for the other — which is exactly why the piano-only enumerations
    never crashed while covering half the model."""
    ir = LayerIR(phrase_id="p")
    assert ir.color_layer is None
    ir.ensure_layer("color_layer").append(_note("C4", "color_layer"))
    assert len(ir.color_layer) == 1
    ir.ensure_layer("principal_line").append(_note("D4", "principal_line"))
    assert len(ir.principal_line) == 1
