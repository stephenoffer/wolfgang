"""The notation layer must be able to write down the music being asked for.

Each test here pins a defect that silently mangled the score: triplets parsed as
32nds, 32nds quantized on top of each other, ties bound to the wrong note,
one-note slurs left dangling, and a meter check that was dead for every phrase
after the first.
"""

from fractions import Fraction
from pathlib import Path

import pytest

from scales.direct_compose import compose_phrase
from scales.duration import bar_duration, beats_to_dur, dur_to_beats, is_tuplet_code
from scales.models import LayerEvent
from scales.validator import validate_meter

# ─── Tuplets ────────────────────────────────────────────────────────────────


def test_triplet_codes_parse_as_triplets_not_32nds():
    """`C5trip_e` is a triplet eighth. A short-first duration scan matched the
    trailing 'e' and left 'trip_' on the pitch, which the salvage path then read
    as 't' — a 32nd. Three of them filled 3/8 of a beat instead of one beat."""
    layer = compose_phrase(
        [{"rh": "C5trip_e D5trip_e E5trip_e F5q G5q", "lh": "C3dh"}],
        key="C",
        meter=(3, 4),
    )
    durs = [e.duration for e in layer.principal_line]
    assert durs[:3] == ["trip_e"] * 3
    assert all(is_tuplet_code(d) for d in durs[:3])


def test_triplet_bar_sums_exactly_to_the_meter():
    """Exact Fractions, so a triplet bar is not one float-epsilon short of the
    meter (which read as a meter violation)."""
    layer = compose_phrase(
        [{"rh": "C5trip_e D5trip_e E5trip_e F5q G5q", "lh": "C3dh"}],
        key="C",
        meter=(3, 4),
    )
    total = sum(dur_to_beats(e.duration) for e in layer.principal_line)
    assert total == Fraction(3)
    assert not validate_meter(layer.principal_line, (3, 4), 1)


def test_triplet_onsets_are_exact_thirds():
    layer = compose_phrase(
        [{"rh": "C5trip_e D5trip_e E5trip_e F5q G5q", "lh": "C3dh"}],
        key="C",
        meter=(3, 4),
    )
    from scales.assembler import _exact_offset

    offsets = [_exact_offset(e.beat) for e in layer.principal_line]
    assert offsets[:4] == [Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1)]


def test_rest_with_tuplet_duration_is_not_zero_length():
    """`rest_trip_e` split on the first '_' only; splitting on every '_' gave
    dur='trip', which mapped to zero beats and silently ate the rest."""
    layer = compose_phrase(
        [{"rh": "rest_trip_e C5trip_e D5trip_e E5q F5q", "lh": "C3dh"}],
        key="C",
        meter=(3, 4),
    )
    first = layer.principal_line[0]
    assert first.pitch == "rest"
    assert dur_to_beats(first.duration) == Fraction(1, 3)


def test_tuplet_marker_written_as_a_suffix_is_normalized():
    layer = compose_phrase(
        [{"rh": "C5e_trip D5e_trip E5e_trip F5q G5q", "lh": "C3dh"}], key="C", meter=(3, 4)
    )
    assert [e.duration for e in layer.principal_line][:3] == ["trip_e"] * 3


def test_beats_to_dur_prefers_plain_codes_over_tuplets():
    assert beats_to_dur(0.25) == "s"
    assert beats_to_dur(Fraction(1, 3)) == "trip_e"


def test_bar_duration_is_exact():
    assert bar_duration((6, 8)) == Fraction(3)
    assert bar_duration((4, 2)) == Fraction(8)


# ─── Fine subdivisions ──────────────────────────────────────────────────────


def test_32nd_notes_get_distinct_onsets():
    """The assembler snapped onsets to a 16th grid, so beats 1.0 and 1.125 both
    became offset 0.0 — two notes on top of each other, one of them lost."""
    from scales.assembler import _exact_offset

    layer = compose_phrase(
        [{"rh": "C5t D5t E5t F5t G5e A5q B5q", "lh": "C3w"}], key="C", meter=(4, 4)
    )
    offsets = [_exact_offset(e.beat) for e in layer.principal_line]
    assert len(set(offsets)) == len(offsets)
    assert offsets[:4] == [Fraction(0), Fraction(1, 8), Fraction(1, 4), Fraction(3, 8)]


def test_64th_note_is_representable():
    assert dur_to_beats("x") == Fraction(1, 16)


def test_tuplets_and_32nds_survive_to_musicxml(tmp_path):
    music21 = pytest.importorskip("music21")
    from scales.assembler import _add_events_voiced
    from scales.music_io import layer_ir_to_event_ir

    layer = compose_phrase(
        [
            {"rh": "C5trip_e D5trip_e E5trip_e F5q G5q", "lh": "C3dh"},
            {"rh": "C5t D5t E5t F5t G5e A5q B5q", "lh": "C3q G3q E3q"},
        ],
        key="C",
        meter=(3, 4),
    )
    events = layer_ir_to_event_ir(layer)
    part = music21.stream.Part()
    for bar in (1, 2):
        measure = music21.stream.Measure(number=bar)
        if bar == 1:
            measure.insert(0, music21.meter.TimeSignature("3/4"))
        _add_events_voiced(
            measure, [e for e in events if e.bar == bar and e.staff == "treble"], (3, 4), {}
        )
        part.append(measure)
    score = music21.stream.Score()
    score.insert(0, part)
    out = tmp_path / "t.musicxml"
    score.write("musicxml", fp=str(out))

    assert "<time-modification>" in out.read_text()  # real tuplet brackets
    reparsed = music21.converter.parse(str(out))
    measures = list(reparsed.recurse().getElementsByClass("Measure"))
    assert [float(m.duration.quarterLength) for m in measures] == [3.0, 3.0]
    thirds = [n for n in measures[0].recurse().notes if n.quarterLength == Fraction(1, 3)]
    assert len(thirds) == 3
    assert len(list(measures[1].recurse().notes)) == 7  # no 32nd collapsed away


# ─── Ties and slurs ─────────────────────────────────────────────────────────


def test_tie_binds_only_to_the_adjacent_same_pitch():
    layer = compose_phrase([{"rh": "C5q~ C5q D5q E5q", "lh": "C3w"}], key="C", meter=(4, 4))
    assert [e.tie for e in layer.principal_line] == ["start", "stop", None, None]


def test_tie_over_an_intervening_note_is_dropped_not_mis_bound():
    """`C5q~ D5q C5q` used to tie across the D5 — unrepresentable in MusicXML."""
    layer = compose_phrase([{"rh": "C5q~ D5q C5q E5q", "lh": "C3w"}], key="C", meter=(4, 4))
    assert [e.tie for e in layer.principal_line] == [None, None, None, None]


def test_one_note_slur_does_not_leave_a_dangling_start():
    layer = compose_phrase([{"rh": "(C5q) D5q E5q F5q", "lh": "C3w"}], key="C", meter=(4, 4))
    assert [e.slur for e in layer.principal_line] == [None, None, None, None]


def test_multi_note_slur_still_starts_and_stops():
    layer = compose_phrase([{"rh": "(C5q D5q E5q) F5q", "lh": "C3w"}], key="C", meter=(4, 4))
    assert [e.slur for e in layer.principal_line] == ["start", None, "stop", None]


# ─── Meter validation ───────────────────────────────────────────────────────


def _bar(bar, durs):
    return [LayerEvent(bar=bar, beat=1.0 + i, pitch="C5", duration=d) for i, d in enumerate(durs)]


def test_meter_check_sees_phrases_that_do_not_start_at_bar_1():
    """The loop ran over range(1, bar_count+1) while events carry ABSOLUTE bar
    numbers, so every phrase after the first was unchecked."""
    overfull = _bar(17, ["q", "q", "q", "q", "q"])  # five quarters in 3/4
    issues = validate_meter(overfull, (3, 4), 1)
    assert [i.severity for i in issues] == ["error"]
    assert issues[0].bar == 17


def test_underfull_bar_warns_but_does_not_error():
    issues = validate_meter(_bar(9, ["q", "q"]), (3, 4), 1)
    assert [i.severity for i in issues] == ["warning"]


def test_exact_bar_passes():
    assert not validate_meter(_bar(33, ["q", "q", "q"]), (3, 4), 1)


# ─── Layer completeness ─────────────────────────────────────────────────────


def test_orchestral_layers_are_not_dropped_at_engraving():
    from scales.models import LayerIR
    from scales.music_io import layer_ir_to_event_ir

    layer = LayerIR(instrumentation="orchestra", bar_count=1)
    layer.principal_line = [LayerEvent(pitch="C5")]
    layer.rhythmic_motor = [LayerEvent(pitch="G3")]
    layer.color_layer = [LayerEvent(pitch="E6")]
    layer.punctuation = [LayerEvent(pitch="C2")]
    staves = {e.staff for e in layer_ir_to_event_ir(layer)}
    assert {"motor", "color", "punctuation"} <= staves


def test_merge_phrases_keeps_orchestral_layers():
    from scales.direct_compose import merge_phrases
    from scales.models import LayerIR

    a = LayerIR(bar_count=1, instrumentation="orchestra")
    a.rhythmic_motor = [LayerEvent(pitch="G3")]
    b = LayerIR(bar_count=1, instrumentation="orchestra")
    b.rhythmic_motor = [LayerEvent(pitch="A3")]
    merged = merge_phrases([a, b])
    assert len(merged.rhythmic_motor) == 2


# ─── Anacrusis ──────────────────────────────────────────────────────────────


def test_pickup_bar_right_aligns_to_the_barline():
    """A phrase may begin with an upbeat. Before this, every phrase in every
    piece had to start on beat 1 of a full bar."""
    layer = compose_phrase(
        [
            {"rh": "G4q", "lh": "rest_q", "pickup": True},
            {"rh": "C5q E5q G5q C6q", "lh": "C3q G3q E3q G3q"},
        ],
        key="C",
        meter=(4, 4),
    )
    assert layer.pickup_beats == 1.0
    assert layer.principal_line[0].beat == 4.0  # a one-beat pickup sits on beat 4
    assert layer.principal_line[1].beat == 1.0  # the downbeat follows


def test_three_beat_pickup_starts_on_beat_two():
    layer = compose_phrase(
        [
            {"rh": "G4q A4q B4q", "lh": "rest_dh", "pickup": True},
            {"rh": "C5w", "lh": "C3w"},
        ],
        key="C",
        meter=(4, 4),
    )
    assert layer.pickup_beats == 3.0
    assert layer.principal_line[0].beat == 2.0


def test_pickup_bar_is_not_a_meter_violation():
    from scales.validator import validate_layer_ir

    layer = compose_phrase(
        [
            {"rh": "G4q", "lh": "rest_q", "pickup": True},
            {"rh": "C5q E5q G5q C6q", "lh": "C3q G3q E3q G3q"},
        ],
        key="C",
        meter=(4, 4),
    )
    report = validate_layer_ir(layer)
    assert report.passed
    assert not [i for i in report.issues if i.category == "meter" and i.bar == 1]


# ─── Dotted-duration spelling ───────────────────────────────────────────────


def test_trailing_dot_duration_is_a_dotted_note():
    """`C5h.` is the spelling used by the brief's and the craft doc's own
    examples; it used to parse as a plain half, so every bar written from the
    documented example came out a beat short."""
    layer = compose_phrase([{"rh": "B4h. rest_q", "lh": "C3w"}], key="C", meter=(4, 4))
    assert layer.principal_line[0].duration == "dh"
    assert sum(dur_to_beats(e.duration) for e in layer.principal_line) == Fraction(4)


def test_double_trailing_dot():
    layer = compose_phrase([{"rh": "C5h.. C5t C5t C5t C5t", "lh": "C3w"}], key="C", meter=(4, 4))
    assert layer.principal_line[0].duration == "ddh"
    assert sum(dur_to_beats(e.duration) for e in layer.principal_line) == Fraction(4)


# ─── Export robustness ──────────────────────────────────────────────────────


def test_offset_snapping_recovers_coarsely_rounded_positions():
    """A legacy beat stored as 1.33 means 4/3. Snapping AFTER the 0-based shift
    resolved it to 31/94, and the resulting sliver gaps made music21 emit a
    2048th-note rest and abort the export of the whole score."""
    from scales.assembler import _exact_offset

    assert _exact_offset(1.33) == Fraction(1, 3)
    assert _exact_offset(1.67) == Fraction(2, 3)
    assert _exact_offset(2.33) == Fraction(4, 3)


def test_offset_snapping_still_exact_for_fine_subdivisions():
    from scales.assembler import _exact_offset

    assert _exact_offset(1.125) == Fraction(1, 8)  # 32nd
    assert _exact_offset(1.0625) == Fraction(1, 16)  # 64th
    assert _exact_offset(1.083333) == Fraction(1, 12)  # triplet 32nd
    assert _exact_offset(1.2) == Fraction(1, 5)  # quintuplet


def test_durations_are_snapped_to_notatable_values():
    from scales.assembler import _notatable

    assert _notatable(Fraction(1, 512)) == Fraction(1, 16)
    assert _notatable(Fraction(1, 3)) == Fraction(1, 3)
    assert _notatable(Fraction(3, 4)) == Fraction(3, 4)


def test_exact_duplicate_events_are_dropped(tmp_path):
    """Triple-committed events at one instant produce zero-length gaps that
    abort the export."""
    from scales.assembler import _collect_events
    from scales.models import LayerIR, PhraseSlot, PhraseState
    from scales.piece_graph import PieceGraph

    layer = LayerIR(bar_count=1)
    layer.principal_line = [LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q")] * 3
    graph = PieceGraph()
    graph.piece_id = "dup"
    graph.phrases["p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="p1", bar_start=1, bar_count=1), realized=layer
    )
    assert len(_collect_events(graph, "full")) == 1


def test_every_writable_duration_survives_the_notatable_snap():
    """The snap that protects the exporter must not corrupt values the grammar
    supports. Hand-listing the notatable set broke quintuplets and septuplets
    (1/5 → 3/16, 1/7 → 1/8) the moment they were added to the grammar."""
    from scales.assembler import _notatable
    from scales.duration import DURATION_VALUES

    for code, value in DURATION_VALUES.items():
        assert _notatable(value) == value, f"{code} ({value}) was altered by the snap"


def test_every_writable_duration_is_exportable():
    music21 = pytest.importorskip("music21")
    from scales.duration import DURATION_VALUES

    for code, value in DURATION_VALUES.items():
        assert music21.duration.Duration(value).type != "complex", f"{code} is unnotatable"


# ─── Voice leading ──────────────────────────────────────────────────────────


def test_voice_leading_samples_sounding_voices_not_exact_onsets():
    """The old check paired notes at IDENTICAL (bar, beat), which is a handful of
    moments per piece once the hands have independent rhythms. Sampling the
    highest and lowest SOUNDING pitches at each attack finds real parallels."""
    from scales.validator import validate_voice_leading

    # outer voices moving in parallel octaves, on different rhythms
    sop = [
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q"),
    ]
    bass = [
        LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q"),
        LayerEvent(bar=1, beat=2.0, pitch="D3", duration="q"),
    ]
    found = validate_voice_leading(sop, bass, all_layers=[sop, bass])
    assert found and "octaves" in found[0].message
    assert all(i.severity == "warning" for i in found), "must never block"


def test_voice_leading_ignores_contrary_motion():
    from scales.validator import validate_voice_leading

    sop = [
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q"),
    ]
    bass = [
        LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q"),
        LayerEvent(bar=1, beat=2.0, pitch="B2", duration="q"),
    ]
    assert not validate_voice_leading(sop, bass, all_layers=[sop, bass])


def test_voice_leading_ignores_a_static_voice():
    """One voice holding while the other moves is oblique motion, not parallel."""
    from scales.validator import validate_voice_leading

    sop = [
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q"),
    ]
    bass = [LayerEvent(bar=1, beat=1.0, pitch="C3", duration="h")]
    assert not validate_voice_leading(sop, bass, all_layers=[sop, bass])


# ─── Multi-voice writing ────────────────────────────────────────────────────


def test_three_voices_in_one_hand_get_three_staff_voices():
    """`//` was capped at two voices per hand, so genuine counterpoint required
    hand-written LayerIR and therefore never got written."""
    from scales.music_io import layer_ir_to_event_ir

    layer = compose_phrase(
        [{"rh": "C5h B4h // G4h G4h // E4h D4h", "lh": "C3w"}], key="C", meter=(4, 4)
    )
    assert [e.pitch for e in layer.inner_voices["treble3"]] == ["E4", "D4"]
    pairs = {(e.staff, e.voice) for e in layer_ir_to_event_ir(layer)}
    assert ("treble", 3) in pairs


def test_four_voice_chorale_two_per_hand():
    from scales.music_io import layer_ir_to_event_ir

    layer = compose_phrase(
        [{"rh": "C5h B4h // G4h G4h", "lh": "E3h D3h // C3h G2h"}], key="C", meter=(4, 4)
    )
    pairs = {(e.staff, e.voice) for e in layer_ir_to_event_ir(layer)}
    assert pairs == {("treble", 1), ("treble", 2), ("bass", 1), ("bass", 2)}


def test_every_extra_voice_must_fill_its_own_bar():
    from scales.validator import validate_layer_ir

    short = compose_phrase([{"rh": "C5w // G4w // E4h", "lh": "C3w"}], key="C", meter=(4, 4))
    meter_issues = [i for i in validate_layer_ir(short).issues if i.category == "meter"]
    assert any("treble3" in i.message for i in meter_issues)

    full = compose_phrase([{"rh": "C5w // G4w // E4w", "lh": "C3w"}], key="C", meter=(4, 4))
    assert not [i for i in validate_layer_ir(full).issues if i.category == "meter"]


def test_extra_voices_survive_merge():
    from scales.direct_compose import merge_phrases

    a = compose_phrase([{"rh": "C5w // G4w // E4w", "lh": "C3w"}], key="C", meter=(4, 4))
    b = compose_phrase([{"rh": "D5w // A4w // F4w", "lh": "D3w"}], key="C", meter=(4, 4))
    merged = merge_phrases([a, b])
    assert len(merged.inner_voices["treble3"]) == 2


# ── The 2026-08-25 notation-poverty pass ────────────────────────────────────
#
# Each test below reproduces a defect that shipped in
# workspace/mozart-andante-fmaj-20260825 — a 41-bar score that passed every
# gate the system had. They are written against the ORIGINAL failure, not
# against the shape of the fix.


def _piano_graph(bars, meter=(4, 4), bar_count=None, cadence="PAC", n_phrases=1):
    """A minimal PieceGraph carrying one or more agent-authored phrases."""
    from scales.models import PhraseSlot, PhraseState, PieceContract, TargetSpec
    from scales.piece_graph import PieceGraph

    graph = PieceGraph()
    graph.piece_id = "notation-test"
    graph.contract = PieceContract(
        piece_id="notation-test",
        description="a test",
        target=TargetSpec(instrumentation="solo_piano"),
    )
    per = bar_count or len(bars)
    for i in range(n_phrases):
        pid = f"p{i + 1}"
        start = 1 + i * per
        graph.phrases[pid] = PhraseState(
            slot=PhraseSlot(
                phrase_id=pid,
                section_id="s1",
                bar_start=start,
                bar_count=per,
                key="C",
                meter=meter,
                tempo_bpm=76,
                cadence_target=cadence,
            ),
            realized=compose_phrase(bars, key="C", bar_start=start, phrase_id=pid, meter=meter),
        )
    return graph


def test_note_running_past_the_barline_is_tied_not_truncated():
    """The original score contained ZERO ties in 41 bars because an event
    longer than the space left in its bar was silently clamped to the barline."""
    from scales.assembler import _split_events_over_barlines
    from scales.models import EventIR

    # A whole note starting on beat 3 of a 4/4 bar: 2 beats fit, 2 spill over.
    ev = EventIR(staff="treble", bar=1, beat=3.0, pitch="C5", duration="w", voice=1)
    out = _split_events_over_barlines([ev], {}, (4, 4))

    assert len(out) == 2, "the note should become two tied fragments"
    first, second = out
    assert (first.bar, first.beat, first.duration, first.tie) == (1, 3.0, "h", "start")
    assert (second.bar, second.beat, second.duration, second.tie) == (2, 1.0, "h", "stop")
    total = dur_to_beats(first.duration) + dur_to_beats(second.duration)
    assert total == dur_to_beats("w"), "no duration may be lost in the split"


def test_split_fragments_do_not_re_articulate_the_attack():
    from scales.assembler import _split_events_over_barlines
    from scales.models import EventIR

    ev = EventIR(
        staff="treble",
        bar=1,
        beat=3.0,
        pitch="C5",
        duration="w",
        voice=1,
        articulation="accent",
        dynamic="f",
        ornament="trill",
        expression="dolce",
    )
    first, second = _split_events_over_barlines([ev], {}, (4, 4))
    assert first.articulation == "accent" and first.dynamic == "f"
    assert second.articulation is None, "a tied continuation is not a new attack"
    assert second.dynamic is None and second.ornament is None and second.expression is None


def test_bar_level_dynamic_is_printed_once_not_once_per_staff():
    """Every dynamic in the original score was engraved twice, once above each
    staff, because the bar dynamic was written onto the first note of BOTH hands."""
    layer = compose_phrase(
        [{"rh": "C5w", "lh": "C3w", "dyn": "p"}],
        key="C",
        bar_start=1,
        phrase_id="p",
        meter=(4, 4),
    )
    marked = [
        e
        for e in (layer.principal_line + layer.bass_foundation + layer.response_layer)
        if e.dynamic
    ]
    assert len(marked) == 1, f"expected one dynamic mark, got {len(marked)}"
    assert marked[0].source_layer == "principal_line"


def test_rit_is_not_marked_on_every_phrase():
    """The original score had nine `rit.` marks alternating with nine `a tempo`
    marks across 41 bars — one on almost every other bar — because the mark was
    placed at each phrase's FIRST bar for every phrase that had a rubato window."""
    from scales.assembler import _apply_performance_marks
    from scales.music_io import layer_ir_to_event_ir

    bars = [{"rh": "C5q D5q E5q F5q", "lh": "C3w"}] * 4
    graph = _piano_graph(bars, n_phrases=6)  # 24 bars, 6 phrases
    events = []
    for ps in graph.phrases.values():
        events.extend(layer_ir_to_event_ir(ps.realized))
    _apply_performance_marks(graph, "full", events)

    rits = [e.bar for e in events if e.expression == "rit."]
    assert len(rits) <= 2, f"a 24-bar piece should not carry {len(rits)} rit. marks"
    for bar in rits:
        # A rit. belongs at a phrase ENDING, never at a phrase's first bar.
        assert bar % 4 == 0, f"rit. at bar {bar} is not a phrase ending"


def test_new_notation_survives_all_the_way_to_musicxml(tmp_path):
    """Rolled chords, pedal, fingering, character text, staccatissimo and the
    acciaccatura/appoggiatura distinction were all inexpressible; each one now
    has to reach the file."""
    from scales.assembler import assemble

    bars = [
        {"rh": "[C5,E5,G5]h:arp [D5,F5,A5]h:arpd", "lh": "C3h:ped G2h", "text": "dolce"},
        {"rh": "C5q:stacciss D5q:port E5q:spicc F5q:3", "lh": "C3w:pedup", "art": "ten"},
        {"rh": "B4e:acci C5q G5e:appo A5q rest_h", "lh": "C3q:imord E3q G3q:iturn C4q"},
        {"rh": "[C5,E5,G5,C6]w:arp:ferm", "lh": "C2w:trem"},
    ]
    graph = _piano_graph(bars)
    xml = Path(assemble(graph, output_dir=str(tmp_path))).read_text()

    for tag, label in (
        ("<arpeggiate", "rolled chord"),
        ("<staccatissimo", "staccatissimo"),
        ("<detached-legato", "portato"),
        ("<spiccato", "spiccato"),
        ("<tenuto", "bar-level tenuto"),
        ("<fingering", "fingering"),
        ("<grace", "grace note"),
        ("<inverted-mordent", "inverted mordent"),
        ("<inverted-turn", "inverted turn"),
        ("<fermata", "fermata"),
        ("dolce", "character text"),
        # A real <pedal> line, not the literal text "Ped.". The assembler used
        # to write the glyph as a TextExpression because "music21 has no
        # PedalMark in this version"; music21 9.9.1 has one, and only the real
        # element makes MuseScore draw the bracket and sustain on playback.
        ("<pedal", "pedal line"),
    ):
        assert tag in xml, f"{label} ({tag}) did not survive to MusicXML"


def test_dotted_forms_that_used_to_collapse_to_a_quarter():
    """`dh.` and `trip_e.` both normalized to nothing, fell through to the
    parser's fallback, and silently became QUARTER notes."""
    from scales.duration import DURATION_VALUES, normalize_dot_suffix

    assert normalize_dot_suffix("dh.") == "ddh"
    assert DURATION_VALUES[normalize_dot_suffix("dh.")] == Fraction(7, 2)
    assert normalize_dot_suffix("dq.") == "ddq"
    # A dotted triplet eighth is exactly an eighth; it must not become a quarter.
    assert DURATION_VALUES[normalize_dot_suffix("trip_e.")] == Fraction(1, 2)


def test_layer_ir_notation_survives_a_piece_graph_round_trip(tmp_path):
    """inner_voices and pickup_beats were dropped by the LayerIR loader, so
    three-voice counterpoint and every anacrusis vanished on reload."""
    from scales.piece_graph import PieceGraph

    bars = [{"rh": "C5h B4h // G4h G4h // E4h D4h", "lh": "C3w"}]
    graph = _piano_graph(bars)
    graph.phrases["p1"].realized.pickup_beats = 1.0
    graph.phrases["p1"].realized.principal_line[0].technique = "arpeggio"
    graph.phrases["p1"].realized.principal_line[0].pedal = "down"
    graph.phrases["p1"].realized.principal_line[0].fingering = "3"

    path = tmp_path / "piece_graph.json"
    graph.save(str(path))
    back = PieceGraph.load(str(path)).phrases["p1"].realized

    assert back.inner_voices, "the third voice was dropped on load"
    assert back.pickup_beats == 1.0, "the anacrusis marker was dropped on load"
    assert back.principal_line[0].technique == "arpeggio"
    assert back.principal_line[0].pedal == "down"
    assert back.principal_line[0].fingering == "3"


def test_slur_left_open_does_not_span_the_whole_piece():
    """An unclosed '(' used to be closed at the FINAL note of the part,
    producing one slur arcing over every note in the score."""
    import music21

    from scales.assembler import _MAX_SPANNER_BARS, assemble

    bars = [{"rh": "(C5q D5q E5q F5q", "lh": "C3w"}] + [{"rh": "C5q D5q E5q F5q", "lh": "C3w"}] * 11
    graph = _piano_graph(bars)
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        score = music21.converter.parse(assemble(graph, output_dir=d))
    slurs = list(score.recurse().getElementsByClass(music21.spanner.Slur))
    assert slurs, "the slur should still be emitted"
    for sl in slurs:
        notes = sl.getSpannedElements()
        span = notes[-1].measureNumber - notes[0].measureNumber
        assert span <= _MAX_SPANNER_BARS, f"slur spans {span} bars"


def test_tied_notes_sound_as_one_note_in_the_preview():
    """A tie is one note held. The MIDI renderer read no tie field at all, so
    every tied note re-articulated — invisible only because the engraving path
    could not produce a tie in the first place."""
    from scales.midi_renderer import _tied_extensions
    from scales.models import EventIR

    evs = [
        EventIR(staff="treble", bar=1, beat=3.0, pitch="C5", duration="h", voice=1, tie="start"),
        EventIR(staff="treble", bar=2, beat=1.0, pitch="C5", duration="h", voice=1, tie="continue"),
        EventIR(staff="treble", bar=3, beat=1.0, pitch="C5", duration="h", voice=1, tie="stop"),
    ]
    extra = _tied_extensions(evs)
    assert extra[id(evs[0])] == 4.0, "the tie start must absorb both continuations"
    assert id(evs[1]) not in extra and id(evs[2]) not in extra


def test_tie_does_not_bind_across_a_pitch_change():
    from scales.midi_renderer import _tied_extensions
    from scales.models import EventIR

    evs = [
        EventIR(staff="treble", bar=1, beat=1.0, pitch="C5", duration="h", voice=1, tie="start"),
        EventIR(staff="treble", bar=1, beat=3.0, pitch="D5", duration="h", voice=1, tie="stop"),
    ]
    assert _tied_extensions(evs) == {}


def test_tie_does_not_bind_across_voices():
    from scales.midi_renderer import _tied_extensions
    from scales.models import EventIR

    evs = [
        EventIR(staff="bass", bar=1, beat=1.0, pitch="C3", duration="h", voice=1, tie="start"),
        EventIR(staff="bass", bar=1, beat=3.0, pitch="C3", duration="h", voice=2, tie="stop"),
    ]
    assert _tied_extensions(evs) == {}


def test_rolled_chord_actually_rolls_in_the_preview(tmp_path):
    """`:arp` engraved an arpeggiate mark and then played as a block chord."""
    import music21

    from scales.midi_renderer import render_midi

    graph = _piano_graph([{"rh": "[C5,E5,G5,C6]w:arp", "lh": "C3w"}])
    path = render_midi(graph, output_dir=str(tmp_path))
    # quantizePost=False: music21's MIDI reader snaps to a 16th grid by default,
    # which would erase a roll spaced at 32nds — exactly the detail under test.
    score = music21.converter.parse(path, quantizePost=False)
    onsets = sorted(
        {round(float(n.offset), 3) for n in score.recurse().notes if n.pitches[0].midi >= 60}
    )
    assert len(onsets) >= 4, f"a rolled chord should have staggered entries, got {onsets}"
    gaps = [b - a for a, b in zip(onsets, onsets[1:])]
    assert all(0 < g < 0.4 for g in gaps), f"a roll is a gesture, not a broken chord: {gaps}"


def test_candidates_rejects_a_dict_instead_of_failing_silently():
    """`sum()` over a dict adds its KEYS, so a dict produced a non-zero total,
    walked the keys as weights, and returned nonsense with no exception."""
    import pytest as _pytest

    from scales.harmony_analysis import candidates

    with _pytest.raises(TypeError, match="12-slot"):
        candidates({0: 1.0, 4: 1.0, 7: 1.0}, 0, 0, "major")
    with _pytest.raises(ValueError, match="exactly 12"):
        candidates([1.0, 0.0, 0.0], 0, 0, "major")


def test_pc_weights_rejects_pitch_classes_where_midi_is_required():
    """Pitch classes make the lowest CLASS the bass, so a root-position F major
    triad containing a C reads as I64 — plausible-looking and wrong."""
    import pytest as _pytest

    from scales.harmony_analysis import pc_weights

    with _pytest.raises(ValueError, match="pitch classes"):
        pc_weights([(0.0, 1.0, [5, 9, 0])], 0.0, 1.0)
    # Real MIDI for the same chord is accepted and reads F as the bass.
    weights, bass = pc_weights([(0.0, 1.0, [41, 57, 60])], 0.0, 1.0)
    assert bass == 5, "F (MIDI 41) is the lowest sounding pitch"
    assert len(weights) == 12


def test_brief_reports_how_earlier_phrases_already_closed():
    """Each phrase is composed in an isolated context with no idea how the
    others ended, so the same locally-reasonable close got chosen every time —
    seven of nine phrase endings shared one cadential rhythm."""
    from scales.composition_brief import _cadences_already_used

    graph = _piano_graph(
        [{"rh": "C5q D5q E5q F5q", "lh": "C3w"}] * 3 + [{"rh": "C5h rest_h", "lh": "C3h rest_h"}],
        n_phrases=4,
    )
    last = sorted(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)[-1]
    hist = _cadences_already_used(graph, last)

    assert hist["closes_so_far"], "the brief must see the earlier closes"
    assert len(hist["closes_so_far"]) == 3, "only phrases that come BEFORE this one"
    assert hist["most_repeated"] == 3, "three identical closes must be reported as three"
    assert hist["warn"] is True
    for close in hist["closes_so_far"]:
        assert close["ends_with_rest"] is True
        assert close["bar"] < graph.phrases[last].slot.bar_start


def test_cadence_history_excludes_phrases_that_come_after():
    from scales.composition_brief import _cadences_already_used

    graph = _piano_graph([{"rh": "C5w", "lh": "C3w"}], n_phrases=3)
    first = sorted(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)[0]
    assert _cadences_already_used(graph, first) == {}, "the opening phrase has no history"


# ── The orchestral path, which had quietly diverged from the piano one ──────


def _orch_graph():
    from scales.models import (
        LayerEvent,
        LayerIR,
        PhraseSlot,
        PhraseState,
        PieceContract,
        TargetSpec,
    )
    from scales.piece_graph import PieceGraph

    def ev(b, t, p, d, **k):
        return LayerEvent(bar=b, beat=t, pitch=p, duration=d, **k)

    lir = LayerIR(phrase_id="o1", instrumentation="orchestra", key="C", meter=(4, 4), bar_count=2)
    lir.principal_line = [
        ev(1, 1.0, "C6", "h", articulation="tenuto"),
        ev(1, 3.0, "E6", "h"),
        ev(2, 1.0, "G6", "w"),
    ]
    lir.foreground = [ev(1, 1.0, "G5", "w"), ev(2, 1.0, "C6", "w")]
    lir.harmonic_mass = [ev(1, 1.0, ["C4", "E4", "G4"], "w"), ev(2, 1.0, ["C4", "F4", "A4"], "w")]
    lir.bass_foundation = [ev(1, 1.0, "C2", "w"), ev(2, 1.0, "C2", "w", dynamic="p")]
    lir.punctuation = [ev(2, 1.0, "C4", "q", articulation="accent")]
    g = PieceGraph()
    g.piece_id = "orch-test"
    g.contract = PieceContract(
        piece_id="orch-test",
        description="An orchestral test",
        target=TargetSpec(instrumentation="orchestra"),
    )
    g.phrases["o1"] = PhraseState(
        slot=PhraseSlot(
            phrase_id="o1",
            section_id="s1",
            bar_start=1,
            bar_count=2,
            key="C",
            meter=(4, 4),
            tempo_bpm=100,
            cadence_target="PAC",
        ),
        realized=lir,
    )
    return g


def test_orchestral_parts_get_real_instruments(tmp_path):
    """Without an Instrument object every part exports with no MIDI program, so
    an orchestrated score plays back as a room full of pianos."""
    import music21

    from scales.assembler import assemble

    score = music21.converter.parse(assemble(_orch_graph(), output_dir=str(tmp_path)))
    instruments = {type(p.getInstrument()).__name__ for p in score.parts}
    assert len(instruments) > 1, f"every part got the same instrument: {instruments}"
    assert "Piano" not in instruments or len(instruments) > 2


def test_orchestral_bars_do_not_overflow_the_meter(tmp_path):
    """The voice-container fix that stopped the piano path spilling past the
    barline was never applied to the ensemble path."""
    import music21

    from scales.assembler import assemble

    score = music21.converter.parse(assemble(_orch_graph(), output_dir=str(tmp_path)))
    for part in score.parts:
        for m in part.getElementsByClass("Measure"):
            total = sum(float(n.quarterLength) for n in m.flatten().notesAndRests)
            assert abs(total - 4.0) < 0.01, f"{part.partName} m{m.number} holds {total} beats"


def test_orchestral_notation_reaches_the_page(tmp_path):
    from scales.assembler import assemble

    xml = Path(assemble(_orch_graph(), output_dir=str(tmp_path))).read_text()
    assert "<tenuto" in xml and "<accent" in xml
    assert "<dynamics" in xml
    assert xml.count("midi-program") >= 2


def test_realism_audit_finds_the_melody_in_an_orchestral_score(tmp_path):
    """music21 hands parts back in the exporter's order, which for a generated
    orchestral score is alphabetical — so staff 0 was 'Bass' and every melody
    detector was analysing the double basses as the tune."""
    import music21

    from scales.assembler import assemble
    from scales.score_realism import _bar_table, identify_staves

    score = music21.converter.parse(assemble(_orch_graph(), output_dir=str(tmp_path)))
    names = [str(p.partName or "") for p in score.parts]
    melody, accomp = identify_staves(score, _bar_table(score))
    assert "melody" in names[melody].lower(), f"melody resolved to {names[melody]}"
    assert melody != accomp


def test_piano_staves_are_still_treble_then_bass(tmp_path):
    import music21

    from scales.assembler import assemble
    from scales.score_realism import _bar_table, identify_staves

    graph = _piano_graph([{"rh": "C5w", "lh": "C3w"}])
    score = music21.converter.parse(assemble(graph, output_dir=str(tmp_path)))
    assert identify_staves(score, _bar_table(score)) == (0, 1)


def test_expectation_ledger_is_populated_and_reaches_the_brief(tmp_path, monkeypatch):
    """The ExpectationLedger held no entries in any piece, ever. Every write was
    guarded by `if ledger is not None` and a fresh graph had no ledger, so the
    population block ran to completion and recorded nothing — and then the brief
    read only the PHRASE scale, which is the one scale nothing is filed at."""
    import shutil

    from scales import scales as scales_mod
    from scales.composition_brief import _ledger_lines, _reconstruct_ledger
    from scales.cross_scale_ledger import ledger_summary
    from scales.piece_graph import PieceGraph

    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    pid = "ledger-test"
    scales_mod.init_workspace(pid, description="a sonata in C major", mode="compose_from_text")
    scales_mod.build_form_graph(pid, form="sonata", key="C major")

    graph = PieceGraph.load(str(tmp_path / pid / "piece_graph.json"))
    summary = ledger_summary(graph)
    assert summary["open"] > 0, "the ledger recorded nothing"
    assert summary["by_scale"], "expectations must carry the scale they belong to"

    # And they must survive the save/load, or a promise made at plan time is
    # gone before composition ever reads it.
    view = _reconstruct_ledger(graph)
    assert view is not None and len(view.entries) == summary["open"]

    first = min(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)
    lines = _ledger_lines(graph, first)
    assert lines, "the composer cannot pay a debt it cannot see"
    shutil.rmtree(tmp_path / pid, ignore_errors=True)


def test_ledger_view_exposes_the_expectation_ledger_api():
    """The brief's ledger view must answer the ExpectationLedger's questions
    (prohibitions, cooldowns, locks), not the container's."""
    from scales.composition_brief import _reconstruct_ledger
    from scales.cross_scale_ledger import CrossScaleLedger
    from scales.piece_graph import PieceGraph

    csl = CrossScaleLedger()
    csl.add_section_expectation(
        exp_type="debt",
        domain="cadence",
        object_ref="x",
        introduced_at="s1",
        expected_form="resolution",
        urgency=0.5,
    )
    graph = PieceGraph()
    graph.cross_scale_ledger = csl.to_dict()
    view = _reconstruct_ledger(graph)
    assert view is not None and view.entries
    assert hasattr(view, "get_active_prohibitions")


# ── Style composition, which was silently degraded to templates ────────────


def test_style_ids_resolve_to_their_members():
    """`normalize_style` replaced '_' with '-' BEFORE stripping the `style__`
    prefix, so the system's own canonical id became 'style--classical', failed
    the prefix test, and matched nothing. Every style resolved to zero members."""
    from scales.style_registry import normalize_style, style_members

    for style_id, expected in (
        ("style__classical", "classical"),
        ("style__baroque", "baroque"),
        ("style__romantic", "romantic"),
        ("style__renaissance", "renaissance"),
    ):
        assert normalize_style(style_id) == expected
        assert style_members(style_id, armed_only=True), f"{style_id} has no armed members"
    # Free text and hyphenated names must keep working.
    assert normalize_style("Classical") == "classical"
    assert normalize_style("late romantic") == "late-romantic"
    assert normalize_style("style__late-romantic") == "late-romantic"
    assert normalize_style("not-a-style") is None


@pytest.mark.parametrize(
    "style", ["style__classical", "style__baroque", "style__romantic", "style__renaissance"]
)
def test_every_armed_style_has_corpus_harmony(style):
    """Composing "in the Classical style" rather than "as Mozart" is a
    first-class mode, and every style fell back to hard-coded I-IV-V templates
    because the progression-model builder could not read a style's bars."""
    from scales.progression_model import corpus_harmony_plan, load_progression_model

    model = load_progression_model(style)
    assert model, f"{style} has no progression model"
    assert model["total_transitions"] > 500

    plans = [corpus_harmony_plan(style, "", "PAC", 4, "C major", seed=s) for s in range(6)]
    assert all(p and p[0] == "I" and p[-1] == "I" for p in plans)
    # A template would give the same handful of chords every time.
    assert len({tuple(p) for p in plans}) >= 4, f"{style} harmony looks templated: {plans}"


def test_authentic_cadences_are_approached_by_a_dominant():
    """Sampling the corpus's "what precedes a final tonic" table freely returned
    IV64, making IV64-I — a plagal cadence where a perfect authentic one was
    planned. A piece whose structural cadences never resolve V-I never sounds
    finished, and the same defect was found by hand in generated output."""
    from scales.progression_model import _is_dominant_function, corpus_harmony_plan

    styles = [
        "mozart",
        "beethoven",
        "chopin",
        "bach",
        "haydn",
        "style__classical",
        "style__baroque",
        "style__romantic",
    ]
    checked = 0
    for style in styles:
        for seed in range(20):
            for key in ("C major", "A minor"):
                plan = corpus_harmony_plan(style, "", "PAC", 4, key, seed=seed)
                if not plan:
                    continue
                checked += 1
                assert _is_dominant_function(plan[-2]), (
                    f"{style} approached a PAC with {plan[-2]} in {plan}"
                )
    assert checked > 100, "the sample never actually exercised the samplers"


def test_dominant_function_distinguishes_the_degrees_that_matter():
    from scales.progression_model import _is_dominant_function as is_dom

    for symbol in (
        "V",
        "V7",
        "V6",
        "V65",
        "V43",
        "V42",
        "v",
        "v6",
        "viio",
        "viio7",
        "vii",
        "viiø43",
        "#viio7",
        "V7/V",
    ):
        assert is_dom(symbol), f"{symbol} carries dominant function"
    for symbol in (
        "I",
        "i",
        "IV",
        "IV64",
        "iv",
        "ii",
        "ii6",
        "vi",
        "vi6",
        "vi7",
        "III",
        "VI",
        "VII",
        "bVII",
        "bII6",
    ):
        # vi is not v; VII (uppercase) is the subtonic, not the leading-tone
        # chord; bVII less so.
        assert not is_dom(symbol), f"{symbol} does not resolve as a dominant"


def test_phrase_state_keeps_every_field_across_a_save_load(tmp_path):
    """The PhraseState loader named five of thirteen fields, so `craft_check`
    (the craft checklist) and `review` (the fresh-ears critic's own verdict)
    were written on save and dropped on load — the reviewer's judgement did not
    survive to the revision pass that was supposed to act on it."""
    from scales.piece_graph import PieceGraph

    graph = _piano_graph([{"rh": "C5w", "lh": "C3w"}])
    ps = graph.phrases["p1"]
    from scales.craft_checker import CraftChecker
    from scales.models import ReviewResult

    ps.craft_check = CraftChecker().check(ps.realized)
    ps.review = ReviewResult(passed=False, musical_issues=["bar 1 is bare"])
    ps.agent_authored = True

    path = tmp_path / "piece_graph.json"
    graph.save(str(path))
    back = PieceGraph.load(str(path)).phrases["p1"]

    # Both come back TYPED, not as raw dicts: the revision pass reads
    # `review.passed` and `craft_check.has_breath_point` as attributes.
    assert back.craft_check is not None, "the craft checklist was dropped"
    assert back.craft_check.has_breath_point == ps.craft_check.has_breath_point
    assert back.review is not None, "the critic's verdict was dropped"
    assert back.review.passed is False
    assert back.review.musical_issues == ["bar 1 is bare"]
    assert back.agent_authored is True
    assert back.realized is not None and back.slot is not None


# ── Multi-movement works ────────────────────────────────────────────────────


def _sonata_graph():
    from scales.models import (
        MovementContract,
        PhraseSlot,
        PhraseState,
        PieceContract,
        SectionSpec,
        TargetSpec,
    )
    from scales.piece_graph import PieceGraph

    graph = PieceGraph()
    graph.piece_id = "sonata-test"
    graph.contract = PieceContract(
        piece_id="sonata-test",
        description="A sonata in three movements",
        target=TargetSpec(instrumentation="solo_piano", movements=3),
    )
    plan = [
        ("m1", "C major", (4, 4), 120, 1, "Allegro"),
        ("m2", "F major", (3, 4), 60, 5, ""),
        ("m3", "C major", (6, 8), 160, 9, "Presto"),
    ]
    rh = {(4, 4): "C5q D5q E5q F5q", (3, 4): "C5q D5q E5q", (6, 8): "C5e D5e E5e F5e G5e A5e"}
    lh = {(4, 4): "C3w", (3, 4): "C3h.", (6, 8): "C3h."}
    for mid, key, meter, tempo, start, marking in plan:
        graph.form.movements.append(
            MovementContract(
                id=mid,
                key=key,
                tempo_bpm=tempo,
                meter=meter,
                tempo_marking=marking,
                sections=[f"{mid}_a"],
            )
        )
        graph.form.sections[f"{mid}_a"] = SectionSpec(
            id=f"{mid}_a", movement_id=mid, key=key, bar_start=start, bar_end=start + 3
        )
        for i in range(4):
            pid = f"{mid}_a_p{i + 1}"
            graph.phrases[pid] = PhraseState(
                slot=PhraseSlot(
                    phrase_id=pid,
                    section_id=f"{mid}_a",
                    bar_start=start + i,
                    bar_count=1,
                    key=key,
                    meter=meter,
                    tempo_bpm=tempo,
                ),
                realized=compose_phrase(
                    [{"rh": rh[meter], "lh": lh[meter]}],
                    key=key,
                    bar_start=start + i,
                    phrase_id=pid,
                    meter=meter,
                ),
            )
    return graph


def test_each_movement_keeps_its_own_meter_key_and_tempo(tmp_path):
    import music21

    from scales.assembler import assemble

    score = music21.converter.parse(assemble(_sonata_graph(), output_dir=str(tmp_path)))
    expected = {**{i: 4.0 for i in range(1, 5)}, **{i: 3.0 for i in range(5, 13)}}
    for part in score.parts:
        for m in part.getElementsByClass("Measure"):
            total = sum(float(n.quarterLength) for n in m.flatten().notesAndRests)
            assert abs(total - expected[m.number]) < 0.01, f"m{m.number} holds {total} beats"
    changes = [
        (m.number, m.timeSignature.ratioString)
        for m in score.parts[0].getElementsByClass("Measure")
        if m.timeSignature
    ]
    assert changes == [(1, "4/4"), (5, "3/4"), (9, "6/8")]


def test_movements_are_separated_on_the_page(tmp_path):
    """A three-movement sonata engraved as one unbroken run of bars is not a
    sonata. Each movement takes a final barline, a heading and a new page."""
    import music21

    from scales.assembler import assemble

    path = assemble(_sonata_graph(), output_dir=str(tmp_path))
    xml = Path(path).read_text()
    score = music21.converter.parse(path)

    headings = [
        str(e.content)
        for e in score.recurse().getElementsByClass("TextExpression")
        if str(e.content)[:1].isupper() and "." in str(e.content)
    ]
    assert headings[:3] == ["I. Allegro", "II. Andante", "III. Presto"], headings
    # "II. Andante" is derived from the metronome value where no marking was given.
    assert 'new-page="yes"' in xml
    barlines = {
        m.number: m.rightBarline.type
        for m in score.parts[0].getElementsByClass("Measure")
        if m.rightBarline
    }
    assert barlines == {4: "final", 8: "final", 12: "final"}


def test_the_tempo_word_is_not_printed_twice(tmp_path):
    import music21

    from scales.assembler import assemble

    score = music21.converter.parse(assemble(_sonata_graph(), output_dir=str(tmp_path)))
    texts = [str(e.content) for e in score.recurse().getElementsByClass("TextExpression")]
    assert texts.count("Allegro") == 0, f"the heading already says it: {texts}"


@pytest.mark.parametrize("movement", ["m1", "m2", "m3"])
def test_a_single_movement_can_be_assembled_on_its_own(tmp_path, movement):
    import music21

    from scales.assembler import assemble

    score = music21.converter.parse(
        assemble(_sonata_graph(), scope=f"movement-{movement}", output_dir=str(tmp_path))
    )
    bars = list(score.parts[0].getElementsByClass("Measure"))
    assert len(bars) == 4, f"movement-{movement} assembled {len(bars)} bars"


def test_continuation_is_recorded_for_the_next_phrase(tmp_path, monkeypatch):
    """`ContinuationContext` declares thirteen fields and NOTHING in the system
    ever set one, so every phrase slot carried the default and the brief's
    continuation block never rendered for any piece."""
    import shutil

    from scales import scales as scales_mod
    from scales.piece_graph import PieceGraph

    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    pid = "continuation-test"
    scales_mod.init_workspace(pid, description="a piece in C major", mode="compose_from_text")
    scales_mod.build_form_graph(pid, form="ternary", key="C major")

    graph = PieceGraph.load(str(tmp_path / pid / "piece_graph.json"))
    order = sorted(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)
    first, second = order[0], order[1]
    slot = graph.phrases[first].slot
    graph.phrases[first].slot.cadence_target = "HC"
    graph.phrases[first].realized = compose_phrase(
        [{"rh": "C5q D5q E5q F5q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e", "dyn": "mf"}]
        * slot.bar_count,
        key="C major",
        bar_start=slot.bar_start,
        phrase_id=first,
        meter=(4, 4),
    )
    scales_mod._record_continuation(graph, first)

    cont = graph.phrases[second].slot.continuation
    assert cont is not None
    assert cont.last_soprano_pitch == "F5"
    assert cont.last_soprano_contour == "rising", "the melody arrives rising"
    assert cont.last_bass_pitch, "the bass under the close is part of the continuation"
    assert cont.last_rh_density == 4.0 and cont.last_lh_density == 8.0
    assert cont.last_key == "C major"
    assert cont.last_dynamic == "mf"
    # Something is owed, and it is described in terms of the SOUNDING harmony
    # rather than the planned cadence label — the label says what was intended,
    # not what was written.
    assert cont.pending_resolution, "a half cadence leaves the dominant hanging"
    assert isinstance(cont.pending_resolution, str) and cont.pending_resolution.strip()
    shutil.rmtree(tmp_path / pid, ignore_errors=True)


def test_the_brief_carries_every_continuation_fact(tmp_path, monkeypatch):
    """The brief exported five of thirteen continuation fields. The contour the
    melody arrives on, how dense the last bar was, what the accompaniment was
    doing and what is left hanging are exactly what a phrase composed in an
    isolated context cannot otherwise know."""
    import shutil

    from scales import scales as scales_mod
    from scales.composition_brief import _transition_context
    from scales.piece_graph import PieceGraph

    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    pid = "continuation-brief"
    scales_mod.init_workspace(pid, description="a piece in C major", mode="compose_from_text")
    scales_mod.build_form_graph(pid, form="ternary", key="C major")
    graph = PieceGraph.load(str(tmp_path / pid / "piece_graph.json"))
    order = sorted(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)
    first, second = order[0], order[1]

    slot = graph.phrases[first].slot
    # Close on F5 over G3: a seventh above the bass, left sounding.
    graph.phrases[first].realized = compose_phrase(
        [{"rh": "C5q D5q E5q F5q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e", "dyn": "mf"}]
        * slot.bar_count,
        key="C major", bar_start=slot.bar_start, phrase_id=first, meter=(4, 4),
    )

    cont = (_transition_context(graph, second) or {}).get("continuation") or {}
    assert cont.get("last_soprano_pitch") == "F5"
    assert cont.get("last_soprano_contour") == "rising"
    assert cont.get("last_rh_density") == 4.0
    assert cont.get("last_lh_density") == 8.0
    assert cont.get("last_dynamic") == "mf"
    # Read from the SOUNDING harmony, not from the planned cadence label.
    assert cont.get("pending_resolution"), "a hanging seventh must be carried across"
    shutil.rmtree(tmp_path / pid, ignore_errors=True)


def test_continuation_has_one_implementation(tmp_path, monkeypatch):
    """`_record_continuation` writes the model field and the brief derives the
    same facts on read. Two answers to one question is how this project ends up
    with two of everything, so they must agree."""
    import shutil
    from dataclasses import fields as dc_fields

    from scales import scales as scales_mod
    from scales.composition_brief import _derive_continuation
    from scales.models import ContinuationContext
    from scales.piece_graph import PieceGraph

    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    pid = "continuation-single"
    scales_mod.init_workspace(pid, description="a piece in C major", mode="compose_from_text")
    scales_mod.build_form_graph(pid, form="ternary", key="C major")
    graph = PieceGraph.load(str(tmp_path / pid / "piece_graph.json"))
    order = sorted(graph.phrases, key=lambda p: graph.phrases[p].slot.bar_start)
    first, second = order[0], order[1]
    slot = graph.phrases[first].slot
    graph.phrases[first].realized = compose_phrase(
        [{"rh": "C5q D5q E5q F5q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e", "dyn": "mf"}]
        * slot.bar_count,
        key="C major", bar_start=slot.bar_start, phrase_id=first, meter=(4, 4),
    )
    scales_mod._record_continuation(graph, first)

    written = graph.phrases[second].slot.continuation
    derived = _derive_continuation(graph, first)
    assert isinstance(written, ContinuationContext)
    known = {f.name for f in dc_fields(ContinuationContext)}
    for key, value in derived.items():
        if key in known:
            assert getattr(written, key) == value, f"{key} disagrees between the two paths"
    shutil.rmtree(tmp_path / pid, ignore_errors=True)



def test_the_brief_states_what_the_planned_cadence_requires():
    """The compiled packs declare a `soprano_line` for this and it is EMPTY in
    all 169 places it occurs, because the source doctrine's cadence tables have
    no soprano column. It does not need extracting: a perfect authentic cadence
    has the tonic in the soprano by definition. The regenerated andante's
    structural arrival closed V7-I correctly and still read as imperfect,
    because the melody landed on the fifth."""
    from scales.composition_brief import cadence_requirement

    assert "TONIC in the soprano" in cadence_requirement("PAC")
    assert "third or fifth" in cadence_requirement("IAC")
    assert "stop ON the dominant" in cadence_requirement("HC")
    assert "next phrase's downbeat" in cadence_requirement("elided")
    assert "vi" in cadence_requirement("deceptive")
    assert cadence_requirement("") == ""
    assert cadence_requirement("not-a-cadence") == ""


@pytest.mark.parametrize(
    "bpm,expect",
    [(76, None), (40, None), (200, None), (22, "warning"), (260, "warning"), (0, "error")],
)
def test_tempo_must_be_a_speed_a_player_can_take(bpm, expect):
    """min_tempo_bpm and max_tempo_bpm have sat on PhysicalConstraints since the
    model was written and nothing has ever read either."""
    from scales.validator import validate_tempo

    issues = validate_tempo(bpm)
    if expect is None:
        assert not issues, [i.message for i in issues]
    else:
        assert issues and issues[0].severity == expect
        # The message must say how to fix it, not just that it is wrong.
        if expect == "warning":
            assert "mark it in a" in issues[0].message


def test_a_missing_or_unparseable_tempo_is_not_an_error():
    from scales.validator import validate_tempo

    assert validate_tempo(None) == []
    assert validate_tempo("presto") == []


# ── Orchestration, which had never been assembled and audited ──────────────


def _orchestrated(tmp_path, monkeypatch):
    """Orchestrate a real piano section and assemble it."""
    import shutil

    from scales import scales as scales_mod
    from scales.piece_graph import PieceGraph

    src = Path("workspace/mozart-andante-fmaj-v2-20260826")
    if not (src / "piece_graph.json").exists():
        pytest.skip("reference piece not present")
    dst = tmp_path / src.name
    shutil.copytree(src, dst)
    monkeypatch.setattr(scales_mod, "_WORKSPACE", tmp_path)
    scales_mod.orchestrate_section(src.name, "m1_a")
    result = scales_mod.assemble_orchestration(src.name, "m1_a")
    assert result.get("ok"), result
    return result["path"], PieceGraph.load(str(dst / "piece_graph.json"))


def test_every_ensemble_part_appears_even_when_it_is_tacet(tmp_path, monkeypatch):
    """A score for a named ensemble whose silent instruments are simply absent
    is not a score for that ensemble — the player counting rests has nothing to
    count. Four of ten parts had zero events and vanished from the file."""
    import music21

    path, _ = _orchestrated(tmp_path, monkeypatch)
    score = music21.converter.parse(path)
    names = [str(p.partName).lower().replace(" ", "_") for p in score.parts]
    for expected in ("flute", "oboe", "clarinet", "bassoon", "horn",
                     "violin_1", "violin_2", "viola", "cello", "contrabass"):
        assert expected in names, f"{expected} is missing from the score: {names}"


def test_orchestral_parts_are_in_score_order(tmp_path, monkeypatch):
    import music21

    path, _ = _orchestrated(tmp_path, monkeypatch)
    names = [str(p.partName).lower().replace(" ", "_") for p in music21.converter.parse(path).parts]
    assert names.index("flute") < names.index("bassoon") < names.index("violin_1")
    assert names.index("violin_1") < names.index("viola") < names.index("contrabass")


def test_each_orchestral_part_sounds_like_its_own_instrument(tmp_path, monkeypatch):
    """Every part exported with the piano's MIDI program, so an orchestrated
    piece played back as a room full of pianos."""
    import music21

    path, _ = _orchestrated(tmp_path, monkeypatch)
    score = music21.converter.parse(path)
    by_name = {
        str(p.partName).lower().replace(" ", "_"): type(p.getInstrument()).__name__
        for p in score.parts
    }
    assert by_name["flute"] == "Flute"
    assert by_name["cello"] == "Violoncello"
    assert by_name["violin_1"] == "Violin", "a numbered part must resolve to its instrument"
    assert len(set(by_name.values())) >= 6, f"too many parts share an instrument: {by_name}"


def test_the_tempo_mark_is_printed_once_not_once_per_player(tmp_path, monkeypatch):
    import collections

    import music21

    path, _ = _orchestrated(tmp_path, monkeypatch)
    score = music21.converter.parse(path)
    texts = collections.Counter(
        str(e.content) for e in score.recurse().getElementsByClass("TextExpression")
    )
    for word, count in texts.items():
        if word in ("Allegro", "Andante", "Andantino", "Adagio", "Presto", "Moderato"):
            assert count == 1, f"'{word}' printed {count} times — once per part"


def test_orchestral_bars_hold_their_meter(tmp_path, monkeypatch):
    """The orchestration JSON dropped `ornament`, so an appoggiatura arrived as
    a plain eighth, took real time, collided with the note it decorates and left
    the bar summing to 3.5 beats of a 3/4."""
    import music21

    path, _ = _orchestrated(tmp_path, monkeypatch)
    score = music21.converter.parse(path)
    for part in score.parts:
        for m in part.getElementsByClass("Measure"):
            total = sum(float(n.quarterLength) for n in m.flatten().notesAndRests)
            if total > 0:
                assert abs(total - 3.0) < 0.01, f"{part.partName} m{m.number} holds {total}"
