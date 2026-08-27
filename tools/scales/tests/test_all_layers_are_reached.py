"""Hand-enumerated layer lists cover the five PIANO layers; LayerIR has eleven.

That shape has now produced the same silent failure three times in this
codebase — a check that runs, computes, and reads an empty drawer, which is
indistinguishable from a clean result. These pin the derived accessors that
replaced the enumerations.

Honest scope, measured rather than assumed: the six ORCHESTRAL LayerIR layers
are currently written by nothing in production. `plan_orchestration` returns a
plain ``dict[str, list[dict]]`` of instrument -> events and writes it to
``orchestration/<section>.json``; it never builds a LayerIR from those fields.
So the range hole these close is a hole nothing currently walks through — the
fix is defensive, and the coverage matters the day something does populate
them. The live orchestration path is range-safe by construction instead, which
`test_orchestration_clamps_every_part_into_its_range` pins.
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


def test_orchestration_clamps_every_part_into_its_range():
    """The live orchestration path never goes through `validate_layer_ir` — it
    returns a plain dict of instrument -> events — so its range safety rests
    entirely on the planner clamping as it assigns.

    Falsified with deliberately extreme piano writing (C8 melody, C0 bass)
    across a ten-instrument ensemble: every assigned note lands inside its own
    instrument's practical range.
    """
    from scales.orchestration_planner import plan_orchestration, practical_range
    from scales.pitch import pitch_to_midi

    ir = LayerIR(phrase_id="p", instrumentation="orchestra", key="C", meter=(4, 4), bar_count=4)
    ir.principal_line = [
        _note(p, "principal_line", bar=b, duration="q")
        for b, p in enumerate(["C7", "G7", "C8", "A7"], 1)
    ]
    ir.bass_foundation = [
        _note(p, "bass_foundation", bar=b, duration="q")
        for b, p in enumerate(["A0", "C1", "E1", "C0"], 1)
    ]

    ensemble = [
        "flute",
        "oboe",
        "clarinet",
        "bassoon",
        "violin",
        "viola",
        "cello",
        "contrabass",
        "horn",
        "trumpet",
    ]
    parts = plan_orchestration(ir, ensemble, key="C")
    assert parts, "the planner assigned nothing"

    for instrument, events in parts.items():
        lo, hi = practical_range(instrument)
        for event in events:
            pitch = event.get("pitch")
            if not pitch or pitch == "rest":
                continue
            for one in pitch if isinstance(pitch, list) else [pitch]:
                midi = pitch_to_midi(one)
                if midi is None:
                    continue
                assert lo <= midi <= hi, (
                    f"{instrument} given {one} (midi {midi}), range [{lo},{hi}]"
                )


def test_every_spelling_of_piano_gets_the_playability_check():
    """The hand-span gate was a whitelist of two spellings, and the graphs on
    disk carry four: 'piano', 'piano_solo', 'solo piano', 'solo_piano'.

    A piece saved under two of them got NO playability check — not a relaxed
    one, none — and hand span is a strict physical constraint. Reproduced: an
    unplayable two-octave stretch in one hand yielded zero findings for
    `piano_solo` before this.
    """
    from scales.validator import validate_layer_ir

    def span_findings(instrumentation):
        ir = LayerIR(phrase_id="p", instrumentation=instrumentation, meter=(4, 4), bar_count=1)
        ir.principal_line = [
            LayerEvent(
                bar=1,
                beat=1.0,
                pitch=["C4", "C6"],  # a two-octave stretch in one hand
                duration="w",
                role="structural",
                source_layer="principal_line",
            )
        ]
        report = validate_layer_ir(ir)
        return [i for i in getattr(report, "issues", []) if i.category == "playability"]

    for spelling in ("solo_piano", "piano", "piano_solo", "solo piano", "fortepiano", "Solo Piano"):
        assert span_findings(spelling), f"{spelling!r} got no playability check"
    # An ensemble has no hands. `piano_trio` contains "piano" and is still one.
    for spelling in ("ensemble", "string_quartet", "piano_trio", "choir"):
        assert not span_findings(spelling), f"{spelling!r} was given a hand-span check"


def test_a_layer_knows_what_the_piece_is_scored_for():
    """Every LayerIR was constructed claiming `solo_piano`, whatever the piece
    was written for — six sites hardcoded it and nothing read the contract.

    So every physical check asking "is this a keyboard?" answered yes for a
    motet, the HAND-SPAN limit among them: a Tenor and a Bassus a nineteenth
    apart is ordinary vocal writing and an impossible reach for one hand. That
    is the exact failure the forces-inference work exists to prevent, arriving
    by a different route — the forces were inferred correctly and then not
    carried to the check that reads them.
    """
    from scales.direct_compose import compose_phrase
    from scales.validator import validate_layer_ir

    bars = [{"rh": "C6w", "lh": "[C3,G4]w"}] * 2  # a 19-semitone reach in one hand

    def span_findings(instrumentation):
        ir = compose_phrase(
            bars, key="C", phrase_id="p", meter=(4, 4), instrumentation=instrumentation
        )
        assert ir.instrumentation == instrumentation, "the layer dropped its forces"
        report = validate_layer_ir(ir)
        return [i for i in getattr(report, "issues", []) if i.category == "playability"]

    for keyboard in ("solo_piano", "piano_solo", "harpsichord"):
        assert span_findings(keyboard), f"{keyboard} must still be held to a hand's reach"
    for ensemble in ("choir", "string_quartet", "orchestra"):
        assert not span_findings(ensemble), f"{ensemble} has no hands to span"

    # The default is unchanged for callers that do not say.
    assert compose_phrase(bars, key="C", phrase_id="p").instrumentation == "solo_piano"
