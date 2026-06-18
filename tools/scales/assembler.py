"""
Assembler — LayerIR/EventIR → MusicXML via music21.

Refactored from tools/v3/wmn_v3_assembler.py.
Handles: key signatures, time signatures, tempo, dynamics, articulations,
         ornaments (trill/mordent/turn), ties, expression text, and — via a
         second spanner pass — slurs and hairpins, plus multi-staff piano
         layout.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .duration import DURATION_VALUES
from .models import EventIR
from .music_io import layer_ir_to_event_ir
from .piece_graph import PieceGraph


def assemble(
    piece_graph: PieceGraph,
    scope: str = "full",
    output_dir: Optional[str] = None,
    performance_marks: bool = True,
) -> str:
    """Assemble all realized phrases into MusicXML.

    Args:
        piece_graph: The PieceGraph with realized phrases
        scope: "full" | "movement-1" | "section-m1_expo_pt"
        output_dir: Where to write the file (default: workspace/<piece_id>/output/)
        performance_marks: insert notational performance indications
            derived from PerformanceIR — "rit." at cadential phrase
            endings (with "a tempo" at the next phrase), "con pedale"
            at the opening of pedaled piano textures

    Returns:
        Path to the generated MusicXML file
    """
    try:
        import music21
    except ImportError:
        raise ImportError("music21 is required for assembly. Install with: pip install music21")

    # Collect all EventIR from realized phrases
    all_events = _collect_events(piece_graph, scope)
    if not all_events:
        raise ValueError(f"No realized phrases found for scope '{scope}'")

    # Performance indications (rit. / a tempo / con pedale): attach text
    # expressions to existing events so they flow through measure building
    if performance_marks:
        _apply_performance_marks(piece_graph, scope, all_events)

    # Get metadata
    contract = piece_graph.contract
    key_str = "C"
    meter = (4, 4)
    tempo_bpm = 120

    # Try to get from first phrase slot
    for phrase_id, phrase_state in piece_graph.phrases.items():
        if phrase_state.slot:
            key_str = phrase_state.slot.key
            meter = phrase_state.slot.meter
            tempo_bpm = phrase_state.slot.tempo_bpm
            break

    # Build music21 score
    score = music21.stream.Score()
    score.metadata = music21.metadata.Metadata()
    desc = contract.description if hasattr(contract, "description") else ""
    score.metadata.title = desc[:50] if desc else "Composition"
    composer_id = (
        piece_graph.style_dna.composer_id if hasattr(piece_graph.style_dna, "composer_id") else ""
    )
    score.metadata.composer = f"Wolfgang SCALES ({composer_id})"

    # Determine instrumentation (handle dict or dataclass target)
    target = contract.target if hasattr(contract, "target") else {}
    if isinstance(target, dict):
        instrumentation = target.get("instrumentation", "solo_piano")
    else:
        instrumentation = getattr(target, "instrumentation", "solo_piano")

    # Build per-bar metadata (key/tempo) from PieceGraph phrases
    bar_meta = {}
    for phrase_id, phrase_state in piece_graph.phrases.items():
        if phrase_state.slot:
            s = phrase_state.slot
            for b in range(s.bar_start, s.bar_start + s.bar_count):
                bar_meta[b] = {"key": s.key, "tempo": s.tempo_bpm}

    if instrumentation in ("solo_piano", "piano"):
        score = _build_piano_score(score, all_events, key_str, meter, tempo_bpm, bar_meta=bar_meta)
    else:
        score = _build_ensemble_score(score, all_events, key_str, meter, tempo_bpm)

    # Write to file
    if output_dir is None:
        output_dir = f"workspace/{piece_graph.piece_id}/output"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{piece_graph.piece_id}.musicxml"
    filepath = output_path / filename
    score.write("musicxml", fp=str(filepath))

    # Update piece graph
    piece_graph.output_paths["musicxml"] = str(filepath)

    return str(filepath)


def _collect_events(piece_graph: PieceGraph, scope: str) -> List[EventIR]:
    """Collect all EventIR from realized phrases matching scope."""
    events = []

    for phrase_id, phrase_state in piece_graph.phrases.items():
        # Check scope
        if scope != "full":
            if scope.startswith("movement-"):
                # Would filter by movement — for now include all
                pass
            elif scope.startswith("section-"):
                section_id = scope.replace("section-", "")
                if phrase_state.slot.section_id != section_id:
                    continue

        if phrase_state.realized:
            phrase_events = layer_ir_to_event_ir(phrase_state.realized)
            events.extend(phrase_events)

    # Re-base bar numbers for partial scopes so the score doesn't open
    # with hundreds of empty padding bars (which also poisons metrics)
    if events and scope != "full":
        min_bar = min(e.bar for e in events)
        if min_bar > 1:
            shift = min_bar - 1
            for e in events:
                e.bar -= shift

    # Sort by bar, beat
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))
    return events


def _build_piano_score(
    score,
    events: List[EventIR],
    key_str: str,
    meter: Tuple[int, int],
    tempo_bpm: int,
    bar_meta: Optional[Dict[int, Dict]] = None,
):
    """Build a piano score with treble and bass staves.

    Handles multi-movement pieces by inserting tempo/key changes
    based on bar_meta from PieceGraph phrase data.
    """
    if bar_meta is None:
        bar_meta = {}
    import music21

    # Maps id(EventIR) → created music21 note, for the spanner pass
    note_map: Dict[int, Any] = {}

    treble = music21.stream.Part()
    treble.partName = "Piano"
    treble.partAbbreviation = "Pno."
    bass = music21.stream.Part()
    bass.partName = "Piano"
    bass.partAbbreviation = "Pno."

    # Group events by bar
    treble_bars: Dict[int, List[EventIR]] = {}
    bass_bars: Dict[int, List[EventIR]] = {}

    for event in events:
        if event.staff == "treble":
            treble_bars.setdefault(event.bar, []).append(event)
        elif event.staff == "bass":
            bass_bars.setdefault(event.bar, []).append(event)

    if not treble_bars and not bass_bars:
        return score

    max_bar = max(
        max(treble_bars.keys(), default=0),
        max(bass_bars.keys(), default=0),
    )

    beats_per_bar = meter[0] * 4.0 / meter[1]

    # Build measures
    current_key = key_str
    current_tempo = tempo_bpm

    for bar_num in range(1, max_bar + 1):
        meta = bar_meta.get(bar_num, {})
        new_key = meta.get("key", current_key)
        new_tempo = meta.get("tempo", current_tempo)

        # Treble measure
        t_measure = music21.stream.Measure(number=bar_num)
        if bar_num == 1 or new_key != current_key:
            t_measure.insert(0, _parse_key(new_key))
            t_measure.insert(0, music21.meter.TimeSignature(f"{meter[0]}/{meter[1]}"))
        if bar_num == 1 or new_tempo != current_tempo:
            t_measure.insert(0, music21.tempo.MetronomeMark(number=new_tempo))

        treble_evts = treble_bars.get(bar_num, [])
        if treble_evts:
            # Clip events to bar boundaries and add
            _add_events_voiced(t_measure, treble_evts, meter, note_map)
        else:
            r = music21.note.Rest()
            r.duration = music21.duration.Duration(beats_per_bar)
            t_measure.append(r)

        treble.append(t_measure)

        # Bass measure
        b_measure = music21.stream.Measure(number=bar_num)
        if bar_num == 1 or new_key != current_key:
            b_measure.insert(0, _parse_key(new_key))
            b_measure.insert(0, music21.meter.TimeSignature(f"{meter[0]}/{meter[1]}"))

        bass_evts = bass_bars.get(bar_num, [])
        if bass_evts:
            _add_events_voiced(b_measure, bass_evts, meter, note_map)
        else:
            r = music21.note.Rest()
            r.duration = music21.duration.Duration(beats_per_bar)
            b_measure.append(r)

        bass.append(b_measure)

        current_key = new_key
        current_tempo = new_tempo

    # Set clefs
    treble.insert(0, music21.clef.TrebleClef())
    bass.insert(0, music21.clef.BassClef())

    # Second pass: slurs and hairpins span notes, so they can only be
    # attached once the notes exist
    _apply_spanners(treble, [e for e in events if e.staff == "treble"], note_map)
    _apply_spanners(bass, [e for e in events if e.staff == "bass"], note_map)

    # Create a StaffGroup for piano grand staff
    score.insert(0, treble)
    score.insert(0, bass)

    return score


def _build_ensemble_score(
    score, events: List[EventIR], key_str: str, meter: Tuple[int, int], tempo_bpm: int
):
    """Build an ensemble score with multiple parts."""
    import music21

    # Group by staff
    staff_events: Dict[str, List[EventIR]] = {}
    for event in events:
        staff_events.setdefault(event.staff, []).append(event)

    ks = _parse_key(key_str)
    ts = music21.meter.TimeSignature(f"{meter[0]}/{meter[1]}")

    for staff_name, staff_evts in staff_events.items():
        part = music21.stream.Part()
        part.partName = staff_name
        note_map: Dict[int, Any] = {}

        max_bar = max((e.bar for e in staff_evts), default=1)
        bars: Dict[int, List[EventIR]] = {}
        for event in staff_evts:
            bars.setdefault(event.bar, []).append(event)

        for bar_num in range(1, max_bar + 1):
            measure = music21.stream.Measure(number=bar_num)
            if bar_num == 1:
                measure.insert(0, ks)
                measure.insert(0, ts)

            for event in bars.get(bar_num, []):
                _add_event_to_measure(measure, event, meter, note_map=note_map)

            if not bars.get(bar_num):
                r = music21.note.Rest()
                r.duration = music21.duration.Duration(meter[0] * 4 / meter[1])
                measure.append(r)

            part.append(measure)

        _apply_spanners(part, staff_evts, note_map)
        score.insert(0, part)

    return score


def _apply_performance_marks(piece_graph: PieceGraph, scope: str, events: List[EventIR]) -> None:
    """Attach notational performance indications from PerformanceIR.

    Discrete marks only — "rit." where a cadential phrase ends (with
    "a tempo" at the following phrase entry) and "con pedale" at the
    opening when the piano texture is pedaled. Continuous humanization
    (velocity curves, microtiming) stays in the MIDI preview.
    """
    from .performance_renderer import build_performance_ir, pedal_bars

    # Included phrases under this scope, in bar order
    phrases = []
    for phrase_id, ps in piece_graph.phrases.items():
        if scope.startswith("section-"):
            if not ps.slot or ps.slot.section_id != scope.replace("section-", ""):
                continue
        if ps.realized:
            phrases.append(ps)
    if not phrases:
        return
    phrases.sort(key=lambda ps: ps.slot.bar_start if ps.slot else 0)

    # Partial scopes were re-based in _collect_events — mirror the shift
    orig_min = min(
        min(
            (e.bar for e in (ps.realized.principal_line + ps.realized.bass_foundation)),
            default=10**9,
        )
        for ps in phrases
    )
    shift = (orig_min - 1) if (scope != "full" and orig_min < 10**9) else 0

    def _mark(bar: int, text: str, prefer_treble: bool = True) -> None:
        candidates = [e for e in events if e.bar == bar and e.pitch != "rest" and not e.expression]
        if prefer_treble:
            treble = [e for e in candidates if e.staff == "treble"]
            candidates = treble or candidates
        if candidates:
            target = min(candidates, key=lambda e: e.beat)
            target.expression = text

    rit_bars = []
    any_pedal = False
    for ps in phrases:
        try:
            perf = build_performance_ir(ps.realized, ps.slot)
        except Exception:
            continue
        if pedal_bars(perf):
            any_pedal = True
        for w in perf.rubato_windows:
            rit_bars.append(w.bar_start - shift)

    for rit_bar in rit_bars:
        _mark(rit_bar, "rit.")
        # restore at the next phrase entry, if there is one
        following = [e.bar for e in events if e.bar > rit_bar]
        if following:
            _mark(min(following), "a tempo")

    if any_pedal and events:
        first_bar = min(e.bar for e in events)
        _mark(first_bar, "con pedale", prefer_treble=False)


def _quantize_beat(beat: float, grid: float = 0.25) -> float:
    """Snap a beat to the nearest grid position (default: sixteenth note)."""
    return round(beat / grid) * grid


def _expressible_duration(dur_beats: float) -> float:
    """Snap duration to nearest expressible value in standard notation."""
    expressible = [0.125, 0.25, 0.375, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
    best = min(expressible, key=lambda x: abs(x - dur_beats))
    return best


def _add_events_voiced(
    measure, evts, meter: Tuple[int, int], note_map: Optional[Dict[int, Any]] = None
) -> None:
    """Add a staff's events to a measure, grouping by voice.

    Pedal-under-figuration (a full-bar bass note in voice 1 sounding under
    figuration in voice 2 — both starting at beat 1) must be written as
    distinct music21 ``Voice`` containers, otherwise the MusicXML exporter
    serializes the overlap WITHOUT ``<backup>`` and the figuration spills
    past the barline (an 8-beat bar in 4/4). When a staff/bar uses a single
    voice we add events flat (the common, simplest case).
    """
    from collections import defaultdict

    import music21

    by_voice: Dict[int, list] = defaultdict(list)
    for e in evts:
        by_voice[getattr(e, "voice", 1) or 1].append(e)

    if len(by_voice) <= 1:
        for event in evts:
            _add_event_to_measure(measure, event, meter, note_map=note_map)
        return

    for vid in sorted(by_voice):
        voice = music21.stream.Voice(id=str(vid))
        for event in by_voice[vid]:
            _add_event_to_measure(voice, event, meter, note_map=note_map)
        measure.insert(0, voice)


def _add_event_to_measure(
    measure, event: EventIR, meter: Tuple[int, int], note_map: Optional[Dict[int, Any]] = None
) -> None:
    """Add an EventIR to a music21 Measure.

    Registers the created note/chord in ``note_map`` (keyed by
    ``id(event)``) so the spanner pass can attach slurs/hairpins.
    """
    import music21

    beats_per_bar = meter[0] * 4.0 / meter[1]
    offset = _quantize_beat(event.beat - 1.0)  # music21 uses 0-based offsets
    dur_beats = DURATION_VALUES.get(event.duration, 1.0)

    # Clamp duration so note doesn't exceed measure boundary
    remaining = beats_per_bar - offset
    if dur_beats > remaining and remaining > 0:
        dur_beats = remaining

    # Snap to expressible duration
    dur_beats = _expressible_duration(dur_beats)

    if event.pitch == "rest":
        n = music21.note.Rest()
        n.duration = music21.duration.Duration(dur_beats)
        measure.insert(offset, n)
        return

    if isinstance(event.pitch, list):
        pitches = [music21.pitch.Pitch(p) for p in event.pitch if p != "rest"]
        if not pitches:
            return
        n = music21.chord.Chord(pitches)
    else:
        try:
            n = music21.note.Note(event.pitch)
        except Exception:
            return  # Skip unparseable pitches

    n.duration = music21.duration.Duration(dur_beats)
    _apply_markings(n, event)

    # Dynamics and text expressions are measure-level objects in music21,
    # not note attributes — inserting into the note silently fails (and
    # used to drop the note entirely)
    if event.dynamic:
        try:
            measure.insert(offset, music21.dynamics.Dynamic(event.dynamic))
        except Exception:
            pass
    if event.expression:
        try:
            te = music21.expressions.TextExpression(event.expression)
            te.style.fontStyle = "italic"
            measure.insert(offset, te)
        except Exception:
            pass

    measure.insert(offset, n)
    if note_map is not None:
        note_map[id(event)] = n


def _apply_markings(note_obj, event: EventIR) -> None:
    """Apply articulations, ornaments, ties, and expression text to a note.

    Dynamics and spanners (slurs, hairpins) are handled by the caller —
    they live on the measure/part, not the note.
    """
    import music21

    if event.articulation:
        art_map = {
            "staccato": music21.articulations.Staccato,
            "accent": music21.articulations.Accent,
            "tenuto": music21.articulations.Tenuto,
            "legato": music21.articulations.Tenuto,  # closest
            "marcato": music21.articulations.StrongAccent,
        }
        art_class = art_map.get(event.articulation)
        if art_class:
            note_obj.articulations.append(art_class())

    if event.ornament:
        orn_map = {
            "trill": music21.expressions.Trill,
            "tr": music21.expressions.Trill,
            "mordent": music21.expressions.Mordent,
            "mord": music21.expressions.Mordent,
            "inverted_mordent": music21.expressions.InvertedMordent,
            "turn": music21.expressions.Turn,
            "fermata": music21.expressions.Fermata,
        }
        orn_class = orn_map.get(event.ornament)
        if orn_class:
            note_obj.expressions.append(orn_class())
        elif event.ornament in ("grace", "appoggiatura", "acciaccatura"):
            # Grace notes change the note itself rather than decorating it
            try:
                note_obj.getGrace(inPlace=True)
            except Exception:
                pass

    if event.tie in ("start", "stop", "continue"):
        import music21.tie

        note_obj.tie = music21.tie.Tie(event.tie)


def _apply_spanners(part, events: List[EventIR], note_map: Dict[int, Any]) -> None:
    """Attach slurs and hairpins (crescendo/diminuendo wedges) to a part.

    Spanners reference the actual Note objects created in the first pass,
    so this must run after all measures are built. Events are walked in
    time order; ``slur``/``hairpin`` use start/stop markers. Dangling
    starts are closed at the last spanned note so export stays valid.
    """
    import music21

    ordered = sorted(
        (e for e in events if id(e) in note_map),
        key=lambda e: (e.bar, e.beat, e.voice),
    )

    open_slur: List[Any] = []
    open_hairpin: Optional[Tuple[str, List[Any]]] = None

    def _close_slur():
        nonlocal open_slur
        if len(open_slur) >= 2:
            try:
                part.insert(0, music21.spanner.Slur(open_slur))
            except Exception:
                pass
        open_slur = []

    def _close_hairpin():
        nonlocal open_hairpin
        if open_hairpin and len(open_hairpin[1]) >= 2:
            kind, notes = open_hairpin
            cls = (
                music21.dynamics.Crescendo
                if kind.startswith("cresc")
                else music21.dynamics.Diminuendo
            )
            try:
                part.insert(0, cls(notes))
            except Exception:
                pass
        open_hairpin = None

    for event in ordered:
        n = note_map[id(event)]

        if open_slur:
            open_slur.append(n)
        if open_hairpin:
            open_hairpin[1].append(n)

        if event.slur == "start":
            if open_slur:
                _close_slur()
            open_slur = [n]
        elif event.slur == "stop" and open_slur:
            _close_slur()

        hp = event.hairpin or ""
        if hp in ("cresc_start", "dim_start", "cresc", "dim", "<", ">"):
            if open_hairpin:
                _close_hairpin()
            kind = "cresc" if hp in ("cresc_start", "cresc", "<") else "dim"
            open_hairpin = (kind, [n])
        elif hp in ("stop", "cresc_stop", "dim_stop", "!") and open_hairpin:
            _close_hairpin()

    # Close any dangling spanners at the final note
    _close_slur()
    _close_hairpin()


def _parse_key(key_str: str):
    """Parse a key string like 'C', 'Dm', 'F#m', 'g_minor', 'bb_major' to music21 Key."""
    import music21

    # Normalize space-separated form ('d minor') to underscore form ('d_minor')
    key_str = key_str.strip().replace(" ", "_")

    # Handle underscore format: g_minor, bb_major, eb_major, etc.
    if "_" in key_str:
        parts = key_str.split("_")
        # Handle modulation arrows like "g_minor->bb_major" — use first key
        if "->" in key_str:
            return _parse_key(key_str.split("->")[0])
        tonic = parts[0].upper()
        # Handle flats: bb -> B-, eb -> E-
        if len(tonic) == 2 and tonic[1] == "B":
            tonic = tonic[0] + "-"
        mode = parts[1] if len(parts) > 1 else "major"
        return music21.key.Key(tonic, mode)

    if key_str.endswith("m"):
        tonic = key_str[:-1]
        return music21.key.Key(tonic, "minor")
    return music21.key.Key(key_str, "major")
