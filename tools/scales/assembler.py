"""
Assembler — LayerIR/EventIR → MusicXML via music21.

Refactored from tools/v3/wmn_v3_assembler.py.
Handles: key signatures, time signatures, tempo, dynamics, articulations,
         ornaments (trill/mordent/turn), ties, expression text, and — via a
         second spanner pass — slurs and hairpins, plus multi-staff piano
         layout.
"""

from __future__ import annotations

import logging
import re
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .duration import (
    DURATION_VALUES,
    GRACE_ORNAMENTS,
    bar_duration,
    dur_to_beats,
    largest_dur_at_most,
)
from .models import EventIR, is_keyboard, is_string_ensemble, is_vocal
from .music_io import layer_ir_to_event_ir
from .piece_graph import PieceGraph


def scoped_basename(piece_id: str, scope: str) -> str:
    """Output basename for a piece rendered at ``scope``.

    Both writers named their file after the PIECE alone, so rendering section
    m1_b overwrote the file a reviewer of m1_a had just been handed — same path,
    contents silently changed from 14 bars to 9. Reviews are per section and can
    run one after another or in parallel, so a fresh-ears critic could open its
    own path and read a section it was never asked about, with nothing to
    indicate it.

    "full" keeps the bare piece id, so the deliverable path is unchanged.
    """
    tag = str(scope or "full").strip()
    if not tag or tag == "full":
        return str(piece_id)
    return f"{piece_id}__{re.sub(r'[^A-Za-z0-9_.-]+', '-', tag)}"


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
    _apply_metadata(score, piece_graph, contract)

    # Determine instrumentation (handle dict or dataclass target)
    target = contract.target if hasattr(contract, "target") else {}
    if isinstance(target, dict):
        instrumentation = target.get("instrumentation", "solo_piano")
    else:
        instrumentation = getattr(target, "instrumentation", "solo_piano")
    # Normalize free-text forms ("solo piano", "Solo-Piano") so the piano grand
    # staff path is taken — the ensemble path can't render the two-voice
    # pedal-under-figuration overlap and spills it past the barline.
    instrumentation = str(instrumentation).strip().lower().replace(" ", "_").replace("-", "_")
    if instrumentation not in ("solo_piano", "piano") and "piano" in instrumentation.split("_"):
        instrumentation = "solo_piano"

    # Build per-bar metadata (key/meter/tempo) from PieceGraph phrases. METER is
    # per bar, not global: taking the first phrase's meter for the whole score
    # mis-barred every piece with a meter change (a minuet + trio, a 6/8 finale,
    # any multi-movement work).
    bar_meta = {}
    for phrase_id, phrase_state in piece_graph.phrases.items():
        s = phrase_state.slot
        if not s or not _in_scope(phrase_state, scope) or not phrase_state.realized:
            continue
        s_meter = tuple(s.meter) if s.meter else meter
        pickup = float(getattr(phrase_state.realized, "pickup_beats", 0) or 0)
        for b in range(s.bar_start, s.bar_start + s.bar_count):
            bar_meta[b] = {"key": s.key, "tempo": s.tempo_bpm, "meter": s_meter}
        if pickup:
            bar_meta[s.bar_start]["pickup_beats"] = pickup
    # Partial scopes re-base bar numbers in _collect_events — mirror the shift so
    # per-bar key/meter still line up with the events.
    if bar_meta and scope != "full":
        shift = min(bar_meta) - 1
        if shift > 0:
            bar_meta = {b - shift: m for b, m in bar_meta.items()}
    # The opening key/meter come from the first sounding bar, not from whichever
    # phrase happens to be first in dict order.
    if bar_meta:
        first = bar_meta[min(bar_meta)]
        key_str, meter, tempo_bpm = first["key"], first["meter"], first["tempo"]

    # A note that runs past its barline becomes real tied fragments. This must
    # happen AFTER bar_meta exists (it needs each bar's capacity) and BEFORE the
    # performance marks are placed (so a mark can't land on an event that is
    # about to be split and lose its first fragment).
    all_events = _split_events_over_barlines(all_events, bar_meta, meter)
    _resolve_cross_phrase_ties(all_events)
    _dedupe_cross_staff_marks(all_events)

    # Performance indications (rit. / a tempo / con pedale): attach text
    # expressions to existing events so they flow through measure building
    if performance_marks:
        _apply_performance_marks(piece_graph, scope, all_events)

    # One decider (models.is_keyboard): this whitelist missed `piano_solo` and
    # `solo piano`, both of which real saved graphs carry — and routing a piano
    # piece down the ensemble path is the documented cause of the voice-overlap
    # bar overflow that desynced the hands in every render.
    # The CONTRACT says which path to take; the NOTES say whether it can work.
    # `_build_piano_score` reads the treble/bass staves that the piano branch of
    # `layer_ir_to_event_ir` produces. Phrases realized into ORCHESTRAL layers
    # emit orchestral staff names instead, so if the contract says solo_piano
    # while the phrases hold orchestral material, the piano path matches nothing
    # and writes a score with one empty part — silently, with no error and a
    # valid file on disk.
    #
    # An empty score is never the right answer when there are notes. Route by
    # the evidence in that one case, and say so.
    keyboard = is_keyboard(instrumentation)
    if keyboard and all_events and not any(e.staff in _PIANO_STAVES for e in all_events):
        keyboard = False
        _LOG.warning(
            "%s: contract says %r but no phrase has piano-staff material; "
            "assembling as an ensemble so the notes survive.",
            getattr(piece_graph, "piece_id", "?"),
            instrumentation,
        )

    if keyboard:
        score = _build_piano_score(score, all_events, key_str, meter, tempo_bpm, bar_meta=bar_meta)
    else:
        score = _build_ensemble_score(
            score,
            all_events,
            key_str,
            meter,
            tempo_bpm,
            bar_meta=bar_meta,
            instrumentation=instrumentation,
        )

    # Structural barlines: a double bar where a section ends, a final barline at
    # the end. Every engraved score has these and their absence is one of the
    # first things that makes a printout look machine-generated.
    _apply_structural_barlines(score, piece_graph, scope)

    # Write to file
    if output_dir is None:
        output_dir = f"workspace/{piece_graph.piece_id}/output"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{scoped_basename(piece_graph.piece_id, scope)}.musicxml"
    filepath = output_path / filename
    try:
        score.write("musicxml", fp=str(filepath))
    except Exception as exc:
        # Name the bar. A bare music21 export exception loses the whole score and
        # says nothing actionable about which bar is malformed.
        raise ValueError(
            f"MusicXML export failed for '{piece_graph.piece_id}': {exc}. "
            f"This means a bar's content cannot be notated as written — check the "
            f"reported measure with the meter gate (self_evaluate's ear reports "
            f"bar_length errors)."
        ) from exc

    # Record where it went, and PERSIST that. Setting the field on an object the
    # caller is about to discard is why four of twelve pieces in workspace/ have
    # an output_paths entry despite all of them having been assembled.
    from .piece_graph import record_output

    record_output(piece_graph, "musicxml", filepath)

    return str(filepath)


def _dedupe_cross_staff_marks(events: List[EventIR]) -> None:
    """One dynamic per moment, not one per staff.

    ``dyn`` on a bar dict lands on the first event of BOTH hands, so a piano
    score came out with the same marking printed twice at every dynamic change —
    once under each staff. On a grand staff a dynamic belongs between the staves,
    once. The same goes for a text expression ("rit.", "con pedale"): duplicated,
    it reads as two instructions.

    Keeps the mark on the upper staff (where a pianist reads it) and clears the
    duplicate below.
    """
    seen: Dict[tuple, str] = {}
    order = {"treble": 0, "melody": 0, "bass": 1}
    for e in sorted(events, key=lambda x: (x.bar, x.beat, order.get(x.staff, 2), x.voice)):
        for field in ("dynamic", "expression"):
            value = getattr(e, field, None)
            if not value:
                continue
            key = (e.bar, round(float(e.beat), 4), field, value)
            if key in seen:
                setattr(e, field, None)
            else:
                seen[key] = e.staff


def _apply_metadata(score, piece_graph, contract) -> None:
    """Title, composer and movement on the score.

    A score whose title is the first fifty characters of the request prompt and
    whose composer field reads "Wolfgang SCALES (mozart)" announces what it is
    before a note is read. Use the piece's own description as a title and name
    the style as a subtitle instead of impersonating the composer.
    """
    md = score.metadata
    desc = (getattr(contract, "description", "") or "").strip()
    title = desc.split(".")[0].split(",")[0].strip() if desc else ""
    title = (title[:60] or piece_graph.piece_id.replace("-", " ")).strip()
    # Assign from the local string, never by reading md.title back: music21
    # processes a title on read (it strips a leading article for sorting and
    # title-cases the rest), so round-tripping turned "Andante grazioso in F
    # major" into "Ndante Grazioso In F Major".
    md.title = title
    try:
        md.movementName = title
    except Exception:
        pass
    style_ref = ""
    dna = getattr(piece_graph, "style_dna", None)
    if dna is not None:
        style_ref = getattr(dna, "composer_id", "") or getattr(dna, "active_period", "") or ""
    # Not "composer: Mozart" — this is not by Mozart. Name the model honestly.
    md.composer = f"after {style_ref}" if style_ref else ""


def _apply_structural_barlines(score, piece_graph, scope: str) -> None:
    """A double bar where a section ends, a final barline at the end.

    Every engraved score has these; their absence is one of the first things that
    makes a printout look machine-generated.
    """
    import music21

    section_ends = set()
    by_section: Dict[str, List[int]] = {}
    for _pid, ps in piece_graph.phrases.items():
        slot = getattr(ps, "slot", None)
        if slot is None or not _in_scope(ps, scope) or not ps.realized:
            continue
        by_section.setdefault(slot.section_id, []).append(slot.bar_start + slot.bar_count - 1)
    for ends in by_section.values():
        section_ends.add(max(ends))

    shift = 0
    if scope != "full" and section_ends:
        shift = (
            min(
                slot.bar_start
                for ps in piece_graph.phrases.values()
                if (slot := getattr(ps, "slot", None)) and _in_scope(ps, scope) and ps.realized
            )
            - 1
        )
        if shift > 0:
            section_ends = {b - shift for b in section_ends}
        else:
            shift = 0

    # Where each movement ENDS and where the next one begins. A movement close
    # takes a final barline, not a double bar, and the next movement starts on
    # a new page under its own heading — a three-movement sonata engraved as one
    # unbroken run of bars is not a sonata, it is a spreadsheet.
    movement_ends, movement_starts = _movement_bounds(piece_graph, scope, shift)

    last_bar = max(section_ends) if section_ends else None
    for part in score.parts:
        for measure in part.getElementsByClass("Measure"):
            if measure.number in movement_ends or measure.number == last_bar:
                style = "final"
            elif measure.number in section_ends:
                style = "double"
            else:
                continue
            try:
                measure.rightBarline = music21.bar.Barline(type=style)
            except Exception:
                continue

    if len(movement_starts) > 1:
        _apply_movement_headings(score, piece_graph, movement_starts)


def _movement_bounds(piece_graph, scope: str, shift: int):
    """(bars where a movement ends, {bar: movement_id} where one begins)."""
    spans: Dict[str, List[int]] = {}
    for ps in piece_graph.phrases.values():
        slot = getattr(ps, "slot", None)
        if slot is None or not ps.realized or not _in_scope(ps, scope):
            continue
        section = slot.section_id or ""
        # The `m<N>_` section-id convention is what identifies a movement; see
        # CLAUDE.md's Section IDs note.
        mv = section.split("_", 1)[0] if "_" in section else ""
        if not mv:
            continue
        start = (slot.bar_start or 1) - shift
        end = start + (slot.bar_count or 1) - 1
        span = spans.setdefault(mv, [start, end])
        span[0], span[1] = min(span[0], start), max(span[1], end)
    ends = {v[1] for v in spans.values()}
    starts = {v[0]: k for k, v in spans.items()}
    return ends, starts


# Roman numerals for movement headings, the way a score prints them.
_ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII")


def _apply_movement_headings(score, piece_graph, movement_starts: Dict[int, str]) -> None:
    """A page break and a heading ("II. Andante") at each movement's first bar."""
    import music21

    by_id = {getattr(m, "id", ""): m for m in (getattr(piece_graph.form, "movements", None) or [])}
    ordered = sorted(movement_starts)
    try:
        top = score.parts[0]
    except (AttributeError, IndexError):
        return
    for n, bar in enumerate(ordered):
        mv_id = movement_starts[bar]
        contract = by_id.get(mv_id)
        numeral = _ROMAN[n] if n < len(_ROMAN) else str(n + 1)
        marking = (getattr(contract, "tempo_marking", "") or "").strip()
        if not marking:
            marking = tempo_word(getattr(contract, "tempo_bpm", 0) or 120)
        measure = next((m for m in top.getElementsByClass("Measure") if m.number == bar), None)
        if measure is None:
            continue
        try:
            heading = music21.expressions.TextExpression(f"{numeral}. {marking}")
            heading.style.fontWeight = "bold"
            heading.style.fontSize = 14
            measure.insert(0, heading)
            # The heading now carries the tempo WORD, so the metronome mark
            # beside it should print only the number — otherwise the first
            # movement reads "I. Allegro   Allegro ♩=120".
            for mm_mark in measure.getElementsByClass("MetronomeMark"):
                if (mm_mark.text or "").strip().lower() == marking.strip().lower():
                    mm_mark.text = None
        except Exception:
            pass
        if n == 0:
            continue  # the first movement does not need a break before it
        for part in score.parts:
            m = next((x for x in part.getElementsByClass("Measure") if x.number == bar), None)
            if m is None:
                continue
            try:
                m.insert(0, music21.layout.PageLayout(isNew=True))
            except Exception:
                pass


def _in_scope(phrase_state, scope: str) -> bool:
    """Is this phrase included by ``scope``?

    "full" takes everything; "section-<id>" one section; "movement-<id>" one
    movement (matched on the slot's movement, falling back to the ``m<N>_``
    prefix convention of section ids) — that used to silently include the whole
    piece, so asking for one movement assembled all of them.
    """
    if not scope or scope == "full":
        return True
    slot = getattr(phrase_state, "slot", None)
    if slot is None:
        return False
    if scope.startswith("section-"):
        return slot.section_id == scope[len("section-") :]
    if scope.startswith("movement-"):
        want = scope[len("movement-") :]
        mv = getattr(slot, "movement_id", "") or ""
        if mv:
            return mv == want or mv == f"m{want}"
        sec = slot.section_id or ""
        return sec.startswith(f"m{want}_") or sec.startswith(f"{want}_")
    # A BARE section id. `self_evaluate` takes one ("m1_a") while this took a
    # prefixed scope ("section-m1_a"), and the two conventions met at a final
    # `return True`: passing the natural argument, or a typo, silently included
    # the WHOLE PIECE. The critic then reviewed — and heard — music from
    # sections it was not reviewing, with nothing to say so.
    #
    # Anything matching no phrase now yields an empty collection, and the
    # caller's existing "No realized phrases found for scope" error fires
    # instead of a wrong score being returned confidently.
    return (slot.section_id or "") == scope


_LOG = logging.getLogger(__name__)

#: Staff names the piano branch of `layer_ir_to_event_ir` emits.
_PIANO_STAVES = frozenset({"treble", "bass"})


def _collect_events(piece_graph: PieceGraph, scope: str) -> List[EventIR]:
    """Collect all EventIR from realized phrases matching scope."""
    events = []

    for phrase_id, phrase_state in piece_graph.phrases.items():
        if not _in_scope(phrase_state, scope):
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

    # Drop exact duplicates. The same pitch, at the same instant, in the same
    # voice, for the same duration is not a unison — it is a double-commit or a
    # merge artifact, and music21 turns the resulting zero-length gaps into
    # unnotatable durations that abort the whole export.
    seen: set = set()
    unique = []
    for e in events:
        key = (e.staff, e.voice, e.bar, round(float(e.beat), 4), str(e.pitch), e.duration)
        if key in seen:
            continue
        seen.add(key)
        unique.append(e)
    events = unique

    # Sort by bar, beat
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))
    return events


def _pad_measure_to_meter(measure, music21, capacity) -> None:
    """Fill a short measure with a rest for exactly the time it is missing.

    A bar whose events do not reach the barline was left short and music21's
    export padded it — with a rest of a WHOLE BAR rather than the remainder. A
    6/4 measure holding a single two-beat chord came back holding 8.0 of 6.0:

        off=0  ql=2  Chord
        off=2  ql=6  Rest      <- a full bar appended to a bar with content

    The underfull bar upstream is a separate matter and is reported by the
    meter check. What must not happen is an engraver's convenience turning it
    into an OVERFULL one, which is unreadable rather than merely thin.

    Voices are padded individually: each is an independent line and each has to
    reach the barline on its own.
    """
    from fractions import Fraction

    cap = Fraction(capacity).limit_denominator(1680)
    if cap <= 0:
        return
    containers = list(measure.voices) or [measure]
    for container in containers:
        held = Fraction(str(round(float(container.highestTime), 6))).limit_denominator(1680)
        missing = cap - held
        # Below a 128th is float residue from the six-decimal rounding upstream,
        # not a gap: two triplet-eighths at 6.666667 end at 6.000000333 against
        # a capacity of 6, three parts in ten million. A tolerance narrower than
        # the rounding that produced the number reports a clean bar as broken.
        if missing <= Fraction(1, 32):
            continue
        # NEVER a bare whole rest for a PARTIAL bar. A `<rest/>` of
        # `<type>whole</type>` is the MusicXML convention for a whole-measure
        # rest, and a reader that follows it inflates the rest to the bar's
        # length: a correct 4-quarter rest written into a 6/4 bar came back as
        # a dotted whole, and the measure read 8.0 of 6.0. The file was right
        # and every reader of it was wrong, which is worse than a file that is
        # wrong — so the remainder goes in as half-bar pieces, which is also
        # how a rest of that length is engraved.
        position = held
        left = missing
        while left > Fraction(1, 32):
            take = min(left, Fraction(2))
            rest = music21.note.Rest()
            rest.duration = music21.duration.Duration(float(take))
            container.insert(float(position), rest)
            position += take
            left -= take


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

    # Build measures. Key, meter and tempo are all per bar — compared by their
    # NORMALIZED value so "a minor" and "Am" (two spellings of the same key used
    # by different phrase slots) don't re-print a key signature at every phrase.
    current_key_sig = None
    current_meter = None
    current_tempo = None

    for bar_num in range(1, max_bar + 1):
        meta = bar_meta.get(bar_num, {})
        new_key = meta.get("key", key_str)
        new_tempo = meta.get("tempo", tempo_bpm)
        bar_meter = tuple(meta.get("meter", meter))
        beats_per_bar = bar_duration(bar_meter)

        key_obj = _parse_key(new_key)
        key_changed = current_key_sig is None or key_obj.sharps != current_key_sig.sharps
        meter_changed = bar_meter != current_meter
        tempo_changed = new_tempo != current_tempo

        for part, bars_by_num, is_treble in (
            (treble, treble_bars, True),
            (bass, bass_bars, False),
        ):
            measure = music21.stream.Measure(number=bar_num)
            if key_changed:
                measure.insert(0, _parse_key(new_key))
            if meter_changed:
                measure.insert(0, music21.meter.TimeSignature(f"{bar_meter[0]}/{bar_meter[1]}"))
            if tempo_changed and is_treble:
                # Carry the tempo WORD, not just the number. A metronome mark
                # alone ("quarter = 76") with no "Andante" over it is how a data
                # export looks, not how a score looks.
                mm = music21.tempo.MetronomeMark(
                    number=new_tempo, text=tempo_word(new_tempo) if current_tempo is None else None
                )
                measure.insert(0, mm)

            pickup = meta.get("pickup_beats")
            shift = Fraction(0)
            if pickup:
                # An anacrusis is a PARTIAL measure: tell music21 how much of the
                # bar is missing so it exports an implicit measure rather than a
                # bar that looks short by mistake.
                shift = beats_per_bar - Fraction(pickup).limit_denominator(96)
                measure.paddingLeft = float(shift)

            evts = bars_by_num.get(bar_num, [])
            if evts:
                _add_events_voiced(measure, evts, bar_meter, note_map, offset_shift=shift)
                _pad_measure_to_meter(measure, music21, beats_per_bar - shift)
            elif not pickup:
                r = music21.note.Rest()
                r.duration = music21.duration.Duration(beats_per_bar)
                measure.append(r)
            part.append(measure)

        if key_changed:
            current_key_sig = key_obj
        current_meter = bar_meter
        current_tempo = new_tempo

    # Set clefs
    treble.insert(0, music21.clef.TrebleClef())
    bass.insert(0, music21.clef.BassClef())

    # Second pass: slurs and hairpins span notes, so they can only be
    # attached once the notes exist
    _apply_spanners(treble, [e for e in events if e.staff == "treble"], note_map)
    _apply_spanners(bass, [e for e in events if e.staff == "bass"], note_map)

    score.insert(0, treble)
    score.insert(0, bass)
    # A real braced grand staff. Without this, MuseScore imports two unrelated
    # single-staff parts that both happen to be called "Piano".
    group = music21.layout.StaffGroup(
        [treble, bass], name="Piano", abbreviation="Pno.", symbol="brace"
    )
    group.barTogether = True
    score.insert(0, group)

    return score


# Orchestral layer name → the instrument an engraver would put on that staff.
# Without an Instrument object every part exports with no MIDI program, so an
# orchestrated score plays back as a room full of pianos.
_LAYER_INSTRUMENTS = {
    "melody": "Violin",
    "foreground": "Flute",
    "counter": "Viola",
    "counter_reply": "Clarinet",
    "harmony": "Horn",
    "response": "Bassoon",
    "motor": "Violin",
    "color": "Oboe",
    "punctuation": "Trumpet",
    "ornament": "Flute",
    "bass": "Violoncello",
    "treble": "Piano",
}


# Real instrument names, as an orchestration plan writes them. The layer map
# above covers the abstract roles the piano-core path produces; a planned
# orchestration names actual instruments, and without these every part of a
# ten-instrument score exported with the piano's MIDI program — so an
# orchestrated piece played back as a room full of pianos even after each part
# was given an Instrument object.
_NAMED_INSTRUMENTS = {
    "piccolo": "Piccolo",
    "flute": "Flute",
    "alto_flute": "Flute",
    "oboe": "Oboe",
    "english_horn": "EnglishHorn",
    "clarinet": "Clarinet",
    "bass_clarinet": "BassClarinet",
    "bassoon": "Bassoon",
    "contrabassoon": "Contrabassoon",
    "horn": "Horn",
    "trumpet": "Trumpet",
    "trombone": "Trombone",
    "bass_trombone": "BassTrombone",
    "tuba": "Tuba",
    "timpani": "Timpani",
    "percussion": "Percussion",
    "harp": "Harp",
    "violin": "Violin",
    "violin_1": "Violin",
    "violin_2": "Violin",
    "viola": "Viola",
    "cello": "Violoncello",
    "violoncello": "Violoncello",
    "contrabass": "Contrabass",
    "double_bass": "Contrabass",
    "soprano": "Soprano",
    "alto": "Alto",
    "tenor": "Tenor",
    "baritone": "Baritone",
    "organ": "Organ",
    "harpsichord": "Harpsichord",
    "fortepiano": "Piano",
    "piano": "Piano",
}


# A CHOIR is not a small orchestra. `_build_ensemble_score` was given no
# instrumentation at all, so it built a vocal piece exactly like an orchestral
# one and resolved the layer roles through `_LAYER_INSTRUMENTS`: the upper staff
# became a Piano and the lower a Violoncello. "A sacred motet for four voices"
# exported as a piano and a cello — with the wrong MIDI programs, the wrong part
# names, and no way for a singer to read their own line.
_VOCAL_ROLES = {
    "treble": "Soprano",
    "melody": "Soprano",
    "foreground": "Soprano",
    "soprano": "Soprano",
    "cantus": "Soprano",
    "counter": "Alto",
    "counter_reply": "Alto",
    "alto": "Alto",
    "altus": "Alto",
    "harmony": "Tenor",
    "response": "Tenor",
    "tenor": "Tenor",
    "tenore": "Tenor",
    "bass": "Bass",
    "bassus": "Bass",
    "baritone": "Baritone",
}


# A STRING QUARTET is not a mixed chamber group. With no roles table of its own,
# the abstract layer names resolved through `_LAYER_INSTRUMENTS`: melody became a
# Violin, but counter_reply became a CLARINET and response a BASSOON — so "a
# quartet in Haydn's style", written from a corpus that IS string quartets, came
# out scored for violin, clarinet, bassoon and cello, with the parts named
# "Melody", "Counter Reply", "Response" and "Bass". Same defect as the choir
# above, one genre over.
#
# Two violins share an instrument class, so the display name is carried here
# rather than derived from it.
_STRING_ROLES = {
    "treble": ("Violin", "Violin I"),
    "melody": ("Violin", "Violin I"),
    "foreground": ("Violin", "Violin I"),
    "counter": ("Violin", "Violin II"),
    "counter_reply": ("Violin", "Violin II"),
    "harmony": ("Viola", "Viola"),
    "response": ("Viola", "Viola"),
    "bass": ("Violoncello", "Violoncello"),
}


#: Generic STAFF names — the two halves of a keyboard, or an abstract layer
#: role. None of them names an instrument, so what they resolve to depends
#: entirely on what the piece is scored for.
_GENERIC_STAFVES = {
    "treble",
    "bass",
    "melody",
    "foreground",
    "counter",
    "counter_reply",
    "harmony",
    "response",
    "motor",
    "color",
    "punctuation",
    "ornament",
}


def _keyboard_instrument(instrumentation: str) -> str:
    """Which keyboard — a harpsichord piece must not play back as a piano."""
    inst = str(instrumentation or "").lower()
    for word, cls in (
        ("harpsichord", "Harpsichord"),
        ("clavichord", "Clavichord"),
        ("organ", "Organ"),
        ("celesta", "Celesta"),
        ("fortepiano", "Piano"),
    ):
        if word in inst:
            return cls
    return "Piano"


def string_part_name(staff_name: str) -> Optional[str]:
    """The display name a bowed part reads under — "Violin II", not "Counter Reply"."""
    key = str(staff_name or "").strip().lower().replace(" ", "_").replace("-", "_")
    entry = _STRING_ROLES.get(key) or _STRING_ROLES.get(key.rsplit("_", 1)[0])
    return entry[1] if entry else None


def _instrument_for(
    staff_name: str, vocal: bool = False, keyboard: str = "", strings: bool = False
):
    """A music21 Instrument for a part name — a real instrument first, then the
    abstract layer role, then the piano.

    ``vocal`` routes the abstract layer roles to voice types instead, so a choir
    part is a Soprano rather than a Piano. A staff that names a REAL instrument
    still wins, since a cantata genuinely has an orchestra in it.
    """
    import music21

    key = str(staff_name or "").strip().lower().replace(" ", "_").replace("-", "_")
    named = _NAMED_INSTRUMENTS.get(key)
    # A KEYBOARD's staves are both the same instrument. "bass" is an orchestral
    # layer role that resolves to a Violoncello, which is right for an ensemble
    # and wrong for the left hand of a piano — a solo piano preview played back
    # as a piano and a cello.
    if keyboard and named is None and key in _GENERIC_STAFVES:
        try:
            return getattr(music21.instrument, _keyboard_instrument(keyboard))()
        except Exception:
            return music21.instrument.Piano()
    if strings and named is None:
        entry = _STRING_ROLES.get(key) or _STRING_ROLES.get(key.rsplit("_", 1)[0])
        cls_name = (
            entry[0] if entry else (_NAMED_INSTRUMENTS.get(key.rsplit("_", 1)[0]) or "Violin")
        )
    elif vocal and named is None:
        cls_name = _VOCAL_ROLES.get(key) or _VOCAL_ROLES.get(key.rsplit("_", 1)[0])
        if cls_name is None:
            cls_name = _NAMED_INSTRUMENTS.get(key.rsplit("_", 1)[0]) or "Vocalist"
    else:
        cls_name = named or _LAYER_INSTRUMENTS.get(key)
        if cls_name is None:
            # "violin_1" style suffixes, and anything the plan spelled loosely.
            stem = key.rsplit("_", 1)[0]
            cls_name = _NAMED_INSTRUMENTS.get(stem) or _LAYER_INSTRUMENTS.get(stem) or "Piano"
    try:
        return getattr(music21.instrument, cls_name)()
    except Exception:
        return music21.instrument.Piano()


# Conventional score order, top to bottom. A score whose parts come out in
# whatever order a dict happened to iterate is not readable as a score.
_SCORE_ORDER = (
    "melody",
    "foreground",
    "piccolo",
    "flute",
    "oboe",
    "clarinet",
    "bassoon",
    "horn",
    "trumpet",
    "trombone",
    "tuba",
    "timpani",
    "percussion",
    "harp",
    "counter",
    "counter_reply",
    "harmony",
    "response",
    "motor",
    "color",
    "punctuation",
    "ornament",
    "violin_1",
    "violin_2",
    "violin",
    "viola",
    "cello",
    "violoncello",
    "contrabass",
    # The GENERIC staff names, and they must sit in staff order: a piece whose
    # parts are named "treble"/"bass" had them ranked 30 and 29, so `_score_order`
    # put the bass staff on TOP. It engraved upside down, and every analysis that
    # indexes `melody_staff=0` read the bass line as the melody.
    "treble",
    "bass",
)


def _score_order(staff_events: Dict[str, List], ensemble=None) -> List[str]:
    """Part names in score order: the ensemble's own order if given, else the
    conventional one, with anything unrecognised kept at the end."""
    names = list(staff_events)
    if ensemble:
        preferred = [str(n) for n in ensemble if str(n) in staff_events]
        return preferred + [n for n in names if n not in preferred]
    rank = {n: i for i, n in enumerate(_SCORE_ORDER)}
    return sorted(names, key=lambda n: (rank.get(n, len(_SCORE_ORDER)), n))


def _build_ensemble_score(
    score,
    events: List[EventIR],
    key_str: str,
    meter: Tuple[int, int],
    tempo_bpm: int,
    bar_meta: Optional[Dict[int, Dict]] = None,
    ensemble: Optional[List[str]] = None,
    instrumentation: str = "",
):
    """Build an ensemble score with multiple parts.

    Brought to parity with the piano path, which had quietly accumulated four
    capabilities this one lacked: per-bar key/meter/tempo changes (so an
    orchestral piece with a meter change was mis-barred), voice containers (so
    two simultaneous voices in one part spilled past the barline — the exact bug
    that was fixed for piano and left here), a real Instrument on each part, and
    a tempo mark at all.
    """
    import music21

    # A choir is not a small orchestra: its parts are voices, not a piano and a
    # cello. Nothing told this function which it was building.
    #
    # This was a second, shorter copy of the word list — it knew "choir" and
    # "satb" but not "motet", "madrigal" or "mass", so "a motet for four parts"
    # still came out as a piano and a cello. One predicate now, shared with the
    # validator that gives those same parts a singer's range.
    vocal = is_vocal(instrumentation)
    strings = is_string_ensemble(instrumentation)

    if bar_meta is None:
        bar_meta = {}

    # Group by staff
    staff_events: Dict[str, List[EventIR]] = {}
    for event in events:
        staff_events.setdefault(event.staff, []).append(event)

    # Every requested part, in score order, INCLUDING the ones that never play
    # in this section. A score for a named ensemble whose silent instruments are
    # simply absent is not a score for that ensemble — the player counting rests
    # has nothing to count, and a section where the flute is tacet reads as a
    # section scored without a flute.
    for name in ensemble or ():
        staff_events.setdefault(str(name), [])
    ordered = _score_order(staff_events, ensemble)

    for idx, staff_name in enumerate(ordered):
        staff_evts = staff_events[staff_name]
        is_top_part = idx == 0
        part = music21.stream.Part()
        instrument = _instrument_for(staff_name, vocal=vocal, strings=strings)
        # A singer reads their own line by its NAME. Naming a choir part
        # "Treble" because that is the staff it happened to be written on leaves
        # nobody able to find the alto. Take the resolved voice type instead; an
        # instrumental part keeps its staff name, which is already how an
        # orchestration plan spells it ("violin_1" -> "Violin 1").
        bowed_name = string_part_name(staff_name) if strings else None
        part.partName = bowed_name or (
            instrument.instrumentName
            if vocal and getattr(instrument, "instrumentName", None)
            else staff_name.replace("_", " ").title()
        )
        part.id = staff_name
        note_map: Dict[int, Any] = {}
        part.insert(0, instrument)
        # A generic staff carries no instrument to imply its clef, and the score
        # came out with none at all — unreadable, and `detect_melody_buried`
        # looks for a treble clef to decide which part carries the tune.
        if staff_name in ("treble", "melody", "foreground"):
            part.insert(0, music21.clef.TrebleClef())
        elif staff_name == "bass":
            part.insert(0, music21.clef.BassClef())

        max_bar = max((e.bar for e in events), default=1)
        bars: Dict[int, List[EventIR]] = {}
        for event in staff_evts:
            bars.setdefault(event.bar, []).append(event)

        current_key_sig = None
        current_meter = None
        current_tempo = None
        for bar_num in range(1, max_bar + 1):
            m_meta = bar_meta.get(bar_num, {})
            new_key = m_meta.get("key", key_str)
            new_tempo = m_meta.get("tempo", tempo_bpm)
            bar_meter = tuple(m_meta.get("meter", meter))
            beats_per_bar = bar_duration(bar_meter)

            key_obj = _parse_key(new_key)
            measure = music21.stream.Measure(number=bar_num)
            # A fresh key/meter object per measure: music21 streams take
            # ownership of inserted elements, so sharing one object across every
            # part gives it conflicting sites and can drop it on export.
            if current_key_sig is None or key_obj.sharps != current_key_sig.sharps:
                measure.insert(0, _parse_key(new_key))
                current_key_sig = key_obj
            if bar_meter != current_meter:
                measure.insert(0, music21.meter.TimeSignature(f"{bar_meter[0]}/{bar_meter[1]}"))
                current_meter = bar_meter
            if new_tempo != current_tempo:
                # A tempo mark goes above the SCORE, not above every player's
                # part. Printing it on all of them gave a seven-part score seven
                # "Allegro"s stacked down the page.
                if is_top_part:
                    measure.insert(
                        0,
                        music21.tempo.MetronomeMark(
                            number=new_tempo,
                            text=tempo_word(new_tempo) if current_tempo is None else None,
                        ),
                    )
                current_tempo = new_tempo

            evts = bars.get(bar_num, [])
            if evts:
                _add_events_voiced(measure, evts, bar_meter, note_map)
            else:
                r = music21.note.Rest()
                r.duration = music21.duration.Duration(beats_per_bar)
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

    # Which phrases actually END at a structural cadence? A rit. is a rare,
    # deliberate mark: it belongs at the approach to a real sectional close, not
    # at every phrase, and certainly not at a phrase's FIRST bar.
    #
    # The old code appended `w.bar_start` for every rubato window and a window
    # was built for essentially every phrase, so a 41-bar andante came out with
    # nine "rit." marks alternating with nine "a tempo" marks — a mark on almost
    # every other bar. No engraved score in history looks like that, and the
    # MIDI preview slowed down and sped up continuously as a result.
    _STRONG_CADENCES = {"PAC", "IAC", "authentic", "perfect_authentic", "imperfect_authentic"}
    last_by_section: Dict[str, Any] = {}
    for ps in phrases:
        sec = getattr(ps.slot, "section_id", "") or ""
        prev = last_by_section.get(sec)
        if prev is None or (ps.slot.bar_start or 0) > (prev.slot.bar_start or 0):
            last_by_section[sec] = ps
    section_final_phrases = set(id(p) for p in last_by_section.values())

    rit_bars: List[int] = []
    any_pedal = False
    for ps in phrases:
        try:
            perf = build_performance_ir(ps.realized, ps.slot)
        except Exception:
            continue
        if pedal_bars(perf):
            any_pedal = True
        if id(ps) not in section_final_phrases:
            continue
        cadence = str(getattr(ps.slot, "cadence_target", "") or "")
        if cadence not in _STRONG_CADENCES:
            continue
        # The broadening lands on the phrase's LAST bar — the cadence itself.
        for w in perf.rubato_windows:
            rit_bars.append(w.bar_end - shift)

    # Keep them sparse even so: a rit. within eight bars of the previous one is
    # not a structural broadening, it is noise.
    rit_bars = sorted(set(rit_bars))
    spaced: List[int] = []
    for b in rit_bars:
        if not spaced or b - spaced[-1] >= 8:
            spaced.append(b)

    last_bar = max((e.bar for e in events), default=0)
    for rit_bar in spaced:
        # No "rit." on the final cadence of the piece — that is what the closing
        # fermata/final barline says, and "a tempo" would have nothing to restore.
        if rit_bar >= last_bar:
            continue
        _mark(rit_bar, "rit.")
        following = [e.bar for e in events if e.bar > rit_bar]
        if following:
            _mark(min(following), "a tempo")

    if any_pedal and events:
        first_bar = min(e.bar for e in events)
        _mark(first_bar, "con pedale", prefer_treble=False)


# Metronome ranges → the Italian tempo word an engraver would actually print.
# A score with a bare "quarter = 76" and no tempo heading reads as a data dump.
_TEMPO_WORDS = (
    (44, "Adagio"),
    (54, "Larghetto"),
    (64, "Andante"),
    (76, "Andantino"),
    (88, "Moderato"),
    (108, "Allegretto"),
    (132, "Allegro"),
    (160, "Vivace"),
    (10**6, "Presto"),
)


def tempo_word(bpm: float) -> str:
    """The conventional tempo word for a metronome value."""
    for ceiling, word in _TEMPO_WORDS:
        if bpm <= ceiling:
            return word
    return "Allegro"


def _resolve_cross_phrase_ties(events: List[EventIR]) -> None:
    """Bind a tie left open at the end of a phrase to the next phrase's entry.

    `direct_compose` resolves ties within one phrase, because one phrase is all
    it can see. A tie-start on a phrase's LAST note therefore had nothing to
    bind to and was dropped — so the one place a tie matters most, an **elided
    cadence** where the resolution is held into the next phrase's downbeat, was
    the one place it could not be written.

    This runs over the assembled event stream, the first point at which both
    sides of the join exist. Same staff, same voice, same pitch, and the very
    next event in that voice: anything else is not a tie, and a start that
    cannot resolve is cleared rather than left dangling.
    """
    from collections import defaultdict

    by_voice = defaultdict(list)
    for e in events:
        if e.pitch == "rest" or e.ornament in _GRACE_ORNAMENTS:
            continue
        by_voice[(e.staff, getattr(e, "voice", 1) or 1)].append(e)

    for evs in by_voice.values():
        evs.sort(key=lambda e: (e.bar, e.beat))
        for cur, nxt in zip(evs, evs[1:]):
            if cur.tie != "start":
                continue
            if nxt.tie in ("stop", "continue"):
                continue  # already bound inside its own phrase
            if nxt.pitch != cur.pitch:
                cur.tie = None
                continue
            nxt.tie = "stop"
            # Only the marks that describe HOW A NOTE IS STRUCK. A dynamic, a
            # text expression and a pedal change mark a MOMENT IN TIME, and the
            # moment happens whether or not a note is re-articulated there:
            # "mp" on the far side of a tie means "from here, mp".
            #
            # Clearing the whole attack set deleted exactly the dynamics a
            # composer cares most about — the ones that open a phrase. In the
            # B-flat andante, two phrases elide into the next bar over a tie,
            # and both of their opening dynamics (bar 9 mp, bar 32 p) vanished
            # between the LayerIR and the score, silently.
            for f in _REARTICULATION_FIELDS:
                setattr(nxt, f, None)
        if evs and evs[-1].tie == "start":
            evs[-1].tie = None


def _split_events_over_barlines(
    events: List[EventIR],
    bar_meta: Dict[int, Dict],
    default_meter: Tuple[int, int],
) -> List[EventIR]:
    """Split any event that runs past its barline into tied fragments.

    A note held across a barline is completely ordinary music — a melody that
    leans into the next bar, a pedal bass under a phrase joint, a suspension
    resolving late. The engraving path had no way to represent one: an event
    longer than the space left in its bar was silently CLAMPED to the barline,
    so the score contained no ties at all and every bar was a sealed box. The
    fix belongs here rather than in the shorthand, because the shorthand's
    per-bar contract (each voice sums to the meter) is what makes the meter
    check possible.

    Fragments chain with real ties; attack marks (articulation, ornament,
    dynamic, text) stay on the first, release marks (slur/hairpin stop) move to
    the last, and a pre-existing tie on the source event is preserved.
    """
    import copy

    def _capacity(bar: int) -> Fraction:
        meta = bar_meta.get(bar) or {}
        # `bar_duration` guards a malformed meter; `tuple(None)` does not, and a
        # partially-initialised slot reaches here.
        raw = meta.get("meter", default_meter)
        cap = bar_duration(tuple(raw) if isinstance(raw, (list, tuple)) else raw)
        pickup = meta.get("pickup_beats")
        if pickup:
            cap = Fraction(pickup).limit_denominator(96)
        return cap

    out: List[EventIR] = []
    for e in events:
        if e.ornament in _GRACE_ORNAMENTS or e.pitch == "rest":
            out.append(e)
            continue
        offset = _exact_offset(e.beat)
        remaining = dur_to_beats(e.duration)
        cap = _capacity(e.bar)
        if offset < 0 or remaining <= 0 or offset + remaining <= cap:
            out.append(e)
            continue

        original_tie = e.tie
        bar = e.bar
        beat = e.beat
        first = True
        pieces: List[EventIR] = []
        # Guard the loop: a corrupt duration should not spawn thousands of bars.
        while remaining > 0 and len(pieces) < 64:
            space = _capacity(bar) - (offset if first else Fraction(0))
            if space <= 0:
                break
            take = min(remaining, space)
            frag = copy.copy(e)
            frag.bar = bar
            frag.beat = float(beat) if first else 1.0
            # The LONGEST value that fits, never the nearest: `beats_to_dur` of
            # a 1.4375 remainder is a dotted quarter at 1.5, and of a 0.3125
            # remainder a triplet eighth at 0.3333 — both LONGER than the space
            # they were clamped to. A note split to fix an overflow would
            # re-create one, compounding across each barline it crosses. It
            # bites hardest exactly where the split is most needed: a clean
            # remainder converts fine, and only an awkward one — the whole
            # reason the note is being split — lands on a longer neighbour.
            frag.duration = largest_dur_at_most(take)
            take = dur_to_beats(frag.duration)
            pieces.append(frag)
            remaining -= take
            bar += 1
            first = False
        if not pieces:
            out.append(e)
            continue
        for i, frag in enumerate(pieces):
            is_first, is_last = i == 0, i == len(pieces) - 1
            if not is_first:
                for f in _ATTACK_FIELDS:
                    setattr(frag, f, None)
            if not is_last:
                for f in _RELEASE_FIELDS:
                    setattr(frag, f, None)
            if is_last:
                # The tail carries whatever tie the source event already had, so
                # a chain of held notes across several bars still joins up.
                frag.tie = "continue" if original_tie in ("start", "continue") else "stop"
            else:
                frag.tie = "start" if is_first and original_tie != "stop" else "continue"
        out.extend(pieces)
    out.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))
    return out


# Shortest value the engraver can notate (a 64th note).
_MIN_NOTATABLE = Fraction(1, 16)

# The durations this system can write, taken straight from the duration table
# rather than re-listed here. Hand-listing them was a mistake that snapped 1/5 to
# 3/16 and 1/7 to 1/8 — silently corrupting the quintuplets and septuplets the
# grammar had just been extended to support. The table IS the definition of what
# is notatable; anything else is a computed remainder that has to land on one of
# these values.
_NOTATABLE = sorted(set(DURATION_VALUES.values()))

# Largest denominator a metric position can have. 48 covers everything the
# shorthand can express (64ths = 1/16, triplet-32nds = 1/12, sextuplet-32nds =
# 1/24, quintuplets = 1/5, septuplets = 1/7) while still snapping a sloppily
# rounded legacy value like 1.33 onto the 4/3 it means. A larger bound does NOT
# help: at 96, 1.33 resolves to 125/94, and the resulting sliver-sized gaps make
# music21 emit a 2048th-note rest and abort the export of the entire score.
_MAX_POSITION_DENOM = 48

# Ornaments that take no metric time, so a note carrying one is never split
# across a barline. The canonical set lives in duration.py — a schleifer/slide
# is deliberately NOT one of them: it is a sign printed on an ordinary,
# full-length note.
_GRACE_ORNAMENTS = GRACE_ORNAMENTS

# When one note is split across a barline, its ATTACK markings belong only to the
# first fragment and its RELEASE markings only to the last — otherwise a single
# tied note re-articulates its dynamic, accent and ornament in every bar it
# crosses, which is both wrong and audible.
_ATTACK_FIELDS = ("dynamic", "articulation", "ornament", "expression", "technique", "pedal")
# The subset that describes how a note is STRUCK, as opposed to what happens at a
# moment. Only these are dropped on the far side of a tie between two written
# notes; see `_resolve_ties`.
_REARTICULATION_FIELDS = ("articulation", "ornament", "technique")
_RELEASE_FIELDS = ("slur", "hairpin")


def _notatable(dur: Fraction) -> Fraction:
    """Snap a duration to the nearest value the shorthand can actually express.

    A clamped remainder or a corrupt stored duration can be an arbitrary
    fraction; handing music21 a 1/512 makes it raise
    ``Cannot convert "2048th" duration to MusicXML`` and lose the whole score.
    """
    if dur in _NOTATABLE:
        return dur
    if dur <= _MIN_NOTATABLE:
        return _MIN_NOTATABLE
    return min(_NOTATABLE, key=lambda v: (abs(v - dur), v))


def _exact_offset(beat: float) -> Fraction:
    """Recover the exact metric position from a stored (float) beat.

    The IR stores beats as JSON floats, so a triplet position arrives as
    1.333333 and must map back to exactly 4/3. Snapping happens BEFORE the
    0-based shift — subtracting first turns the float error into a much worse
    approximation.

    This replaces a 16th-note rounding grid that made 32nd notes COLLIDE: beats
    1.0 and 1.125 both snapped to offset 0.0, so half the notes of any 32nd-note
    figuration landed on top of each other and vanished from the score.
    """
    return Fraction(beat).limit_denominator(_MAX_POSITION_DENOM) - 1


def _add_events_voiced(
    measure,
    evts,
    meter: Tuple[int, int],
    note_map: Optional[Dict[int, Any]] = None,
    offset_shift: Fraction = Fraction(0),
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

    evts, _chord_aliases = _merge_simultaneous_into_chords(list(evts))

    by_voice: Dict[int, list] = defaultdict(list)
    for e in evts:
        by_voice[getattr(e, "voice", 1) or 1].append(e)

    if len(by_voice) <= 1:
        for event in evts:
            _add_event_to_measure(
                measure, event, meter, note_map=note_map, offset_shift=offset_shift
            )
        _apply_chord_aliases(note_map, _chord_aliases)
        return

    for vid in sorted(by_voice):
        voice = music21.stream.Voice(id=str(vid))
        for event in by_voice[vid]:
            # Notes go into the voice; dynamics / text / pedal go on the MEASURE.
            _add_event_to_measure(
                voice,
                event,
                meter,
                note_map=note_map,
                offset_shift=offset_shift,
                marks_target=measure,
            )
        measure.insert(0, voice)
    _apply_chord_aliases(note_map, _chord_aliases)


def _apply_chord_aliases(note_map, aliases) -> None:
    """Let a merged chord answer to the id of the note that carried its marks."""
    if not note_map or not aliases:
        return
    for chord_id, original_id in aliases.items():
        if chord_id in note_map:
            note_map[original_id] = note_map[chord_id]


def _merge_simultaneous_into_chords(evts: list) -> list:
    """Two notes at one instant in one voice are a CHORD, not two notes.

    `_add_event_to_measure` has always built a `music21.chord.Chord` when an
    event's pitch is a list — but nothing upstream ever produced that list, so
    coincident events in one voice were inserted as separate `Note`s at the same
    offset. MusicXML has no way to express that: without a `<chord/>` marker the
    exporter serializes them one after the other, which is how a 4/4 bar ends up
    holding more beats than it has. It is the same class of defect as the
    pedal-under-figuration overlap, and it silently capped every melody at one
    note per attack.

    Only events sharing an onset AND a duration merge. Different durations at
    one onset are genuinely two voices, which is what `_add_staff_events`
    separates into `Voice` containers.

    **Call this per bar, never across one.** The key is `(beat, duration,
    voice)` with NO bar in it, which is correct inside `_add_staff_events` —
    it is handed one measure at a time — and wrong anywhere else: across a
    section it would merge beat 1 of bar 3 into beat 1 of bar 1.

    A list-pitched event routes to its own `("solo", id(e))` key, so two chords
    at one instant are never merged into a bigger one. That is right for a
    keyboard staff, where a second chord at one onset is a second voice. It is
    also why the orchestral path cannot use this: a viola part carrying a
    melodic line AND an accompaniment needs voice separation, not chording.
    """
    from collections import defaultdict

    groups: Dict[Any, list] = defaultdict(list)
    order: list = []
    for e in evts:
        if e.pitch == "rest" or isinstance(e.pitch, list):
            key = ("solo", id(e))
        else:
            key = (round(float(e.beat), 6), str(e.duration), getattr(e, "voice", 1) or 1)
        if key not in groups:
            order.append(key)
        groups[key].append(e)

    merged = []
    aliases: Dict[int, int] = {}
    for key in order:
        members = groups[key]
        if len(members) == 1:
            merged.append(members[0])
            continue
        # COPY, never mutate. Setting `top.pitch = [...]` in place wrote the
        # merged chord back into the PieceGraph's own events — assembling a
        # piece silently rewrote it, and a second assembly saw a bass note
        # spelled `"['A2', 'C3']"`. Assembly reads the piece; it does not
        # compose it.
        top = max(members, key=lambda e: _pitch_sort_key(e.pitch))
        seen = []
        for e in members:
            if isinstance(e.pitch, str) and e.pitch not in seen:
                seen.append(e.pitch)
        chord = replace(top, pitch=seen)
        # The spanner pass keys slurs and hairpins on `id(event)`, and it is the
        # top note that carries them — so the copy answers to the original's id.
        aliases[id(chord)] = id(top)
        merged.append(chord)
    return merged, aliases


def _pitch_sort_key(pitch) -> int:
    from .pitch import pitch_to_midi

    if isinstance(pitch, str):
        return pitch_to_midi(pitch) or 0
    return 0


def _add_event_to_measure(
    measure,
    event: EventIR,
    meter: Tuple[int, int],
    note_map: Optional[Dict[int, Any]] = None,
    offset_shift: Fraction = Fraction(0),
    marks_target=None,
) -> None:
    """Add an EventIR to a music21 Measure.

    Registers the created note/chord in ``note_map`` (keyed by
    ``id(event)``) so the spanner pass can attach slurs/hairpins.

    Offsets and durations stay exact (``Fraction``), so music21 builds the right
    tuplet bracket for a 1/3 and the right 64th for a 1/16 instead of receiving
    a value already rounded onto a 16th-note grid.
    """
    import music21

    beats_per_bar = bar_duration(meter)
    # music21 uses 0-based offsets. In an anacrusis the IR keeps the metrically
    # TRUE beat (a one-beat pickup in 4/4 sits on beat 4), while music21 wants the
    # content at offset 0 of a measure declared short via paddingLeft — so shift.
    offset = _exact_offset(event.beat) - offset_shift
    if offset_shift:
        beats_per_bar -= offset_shift
    if offset < 0:
        offset = Fraction(0)
    dur_beats = dur_to_beats(event.duration)
    if dur_beats <= 0:
        dur_beats = Fraction(1)

    # An event that starts past the barline is corrupt input (the meter check at
    # commit is what should catch it). Pull it back to the last position inside
    # the bar rather than silently lengthening the measure, which used to produce
    # 5-beat bars in a 4/4 score.
    if offset >= beats_per_bar:
        offset = max(Fraction(0), beats_per_bar - dur_beats)
    # Clamp duration so the note doesn't cross the barline. The remainder must
    # still be a notatable value: clamping to whatever was left over could yield
    # a 1/512 note, which music21 refuses to export ("cannot convert 2048th
    # duration") and which no engraver could render anyway.
    remaining = beats_per_bar - offset
    if dur_beats > remaining:
        if remaining < _MIN_NOTATABLE:
            return  # no room left in the bar — the meter check flags the cause
        # The LONGEST value that fits, not the nearest: `_notatable` rounds to
        # whichever is closest, which for a remainder of 1.4375 is a dotted
        # quarter at 1.5 — back past the barline the clamp just pulled it inside.
        dur_beats = dur_to_beats(largest_dur_at_most(remaining))
    else:
        dur_beats = _notatable(dur_beats)

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

    # Dynamics and text expressions are MEASURE-level objects in music21, not
    # note attributes and not voice contents: a Dynamic inserted into a Voice
    # exports inside that voice's backup/forward block, where engravers place it
    # inconsistently. ``marks_target`` is the enclosing measure when this event
    # is being added to a voice container.
    target = marks_target if marks_target is not None else measure
    seen = _marks_seen(target)

    if event.dynamic:
        # One dynamic per position. A bar-level dynamic used to be written onto
        # the first note of BOTH staves, so every dynamic in the score was
        # printed twice, once above each staff.
        key = ("dyn", float(offset))
        if key not in seen:
            seen.add(key)
            try:
                target.insert(offset, music21.dynamics.Dynamic(event.dynamic))
            except Exception:
                pass
    if event.expression:
        key = ("text", float(offset), event.expression)
        if key not in seen:
            seen.add(key)
            try:
                te = music21.expressions.TextExpression(event.expression)
                te.style.fontStyle = "italic"
                target.insert(offset, te)
            except Exception:
                pass
    # Pedal is emitted by `_apply_spanners` as a real MusicXML <pedal> line,
    # which is what makes MuseScore draw the bracket and sustain on playback.
    # It used to be written here as the literal text "Ped." / "*", on the
    # grounds that "music21 has no PedalMark in this version" — music21 9.9.1
    # has `expressions.PedalMark`, a Spanner that exports
    # `<pedal type="start"/>` … `<pedal type="stop"/>`. A text glyph looks
    # right on the page and does nothing at all.

    measure.insert(offset, n)
    if note_map is not None:
        note_map[id(event)] = n


def _marks_seen(measure) -> set:
    """Per-measure set of already-emitted (kind, offset) marks.

    Stashed on the measure so the dedupe survives across the two staves and the
    several voices that all insert into the same measure.
    """
    got = getattr(measure, "_wolfgang_marks", None)
    if got is None:
        got = set()
        try:
            measure._wolfgang_marks = got
        except Exception:
            return set()
    return got


def _articulation_classes() -> Dict[str, Any]:
    """Name → music21 articulation class.

    Kept as a function so the module imports without music21 present. The map
    used to cover five names, so a staccatissimo wedge, a portato, a breath mark
    and a caesura were all silently discarded on the way to the page.
    """
    import music21

    a = music21.articulations
    return {
        "staccato": a.Staccato,
        "staccatissimo": a.Staccatissimo,
        "portato": a.DetachedLegato,
        "detached_legato": a.DetachedLegato,
        "spiccato": a.Spiccato,
        "accent": a.Accent,
        "tenuto": a.Tenuto,
        "marcato": a.StrongAccent,
        "strong_accent": a.StrongAccent,
        "breath": a.BreathMark,
        "caesura": a.Caesura,
        "stress": a.Stress,
        "unstress": a.Unstress,
        # "legato" is a SLUR, not a note-attached mark. Rendering it as a tenuto
        # printed a dash on every note of a legato passage — the opposite of the
        # smooth line intended.
        "legato": None,
    }


def _ornament_classes() -> Dict[str, Any]:
    """Name → music21 ornament class (None = handled specially by the caller)."""
    import music21

    e = music21.expressions
    return {
        "trill": e.Trill,
        "tr": e.Trill,
        "mordent": e.Mordent,
        "mord": e.Mordent,
        "inverted_mordent": e.InvertedMordent,
        "prall": e.InvertedMordent,
        "turn": e.Turn,
        "inverted_turn": e.InvertedTurn,
        "schleifer": e.Schleifer,
        "fermata": e.Fermata,
    }


def _apply_markings(note_obj, event: EventIR) -> None:
    """Apply articulations, ornaments, ties, techniques and fingering to a note.

    Dynamics, text expressions and spanners (slurs, hairpins, glissandi, ottava)
    are handled by the caller — they live on the measure/part, not the note.
    """
    import music21

    if event.articulation:
        art_class = _articulation_classes().get(event.articulation)
        if art_class:
            note_obj.articulations.append(art_class())

    if event.ornament:
        orn_class = _ornament_classes().get(event.ornament)
        if orn_class:
            note_obj.expressions.append(orn_class())
        elif event.ornament in ("grace", "appoggiatura", "acciaccatura"):
            # Grace notes change the note itself rather than decorating it. An
            # acciaccatura is the SLASHED (crushed) form and an appoggiatura the
            # unslashed one — engravers and players read them differently, and
            # collapsing both onto a plain grace lost that distinction.
            try:
                if event.ornament == "acciaccatura":
                    note_obj.getGrace(appoggiatura=False, inPlace=True)
                    try:
                        note_obj.duration.slash = True
                    except Exception:
                        pass
                elif event.ornament == "appoggiatura":
                    note_obj.getGrace(appoggiatura=True, inPlace=True)
                else:
                    note_obj.getGrace(inPlace=True)
            except Exception:
                pass

    technique = getattr(event, "technique", None)
    if technique:
        try:
            if technique in ("arpeggio", "arpeggio_up", "arpeggio_down"):
                # A rolled chord. Only meaningful on a chord, and the direction
                # is part of the notation ('up' is the default an engraver
                # assumes, so a downward roll must actually say so).
                if isinstance(note_obj, music21.chord.Chord):
                    kind = {
                        "arpeggio": "normal",
                        "arpeggio_up": "up",
                        "arpeggio_down": "down",
                    }[technique]
                    note_obj.expressions.append(music21.expressions.ArpeggioMark(kind))
            elif technique == "tremolo":
                note_obj.expressions.append(music21.expressions.Tremolo())
        except Exception:
            pass

    fingering = getattr(event, "fingering", None)
    if fingering:
        try:
            fg = music21.articulations.Fingering(str(fingering))
            note_obj.articulations.append(fg)
        except Exception:
            pass

    if event.tie in ("start", "stop", "continue"):
        import music21.tie

        note_obj.tie = music21.tie.Tie(event.tie)


# A spanner left open by the composer is a mistake, not an instruction to slur
# the rest of the piece. An unclosed span reaches at most this many bars from
# where it started, then closes.
_MAX_SPANNER_BARS = 4


def _apply_spanners(part, events: List[EventIR], note_map: Dict[int, Any]) -> None:
    """Attach slurs, hairpins, glissandi and ottava lines to a part.

    Spanners reference the actual Note objects created in the first pass, so
    this must run after all measures are built. Events are walked in time order;
    ``slur`` / ``hairpin`` / ``technique`` use start/stop markers.

    A dangling start used to be closed at the FINAL note of the part, so one
    unclosed ``(`` produced a single slur arcing across the entire piece. Now an
    unclosed span is cut off after ``_MAX_SPANNER_BARS`` bars, which is what an
    engraver reading the same passage would do.

    Slurs are tracked PER VOICE. A single cursor meant a slur opened in the
    melody was closed by the next 'stop' in the inner voice, tying two
    independent lines into one spanner.
    """
    import music21

    ordered = sorted(
        (e for e in events if id(e) in note_map),
        key=lambda e: (e.bar, e.beat, e.voice),
    )
    if not ordered:
        return

    # voice → (start_bar, [notes])
    open_slurs: Dict[int, Tuple[int, List[Any]]] = {}
    open_hairpin: Optional[Tuple[str, int, List[Any]]] = None
    open_gliss: Optional[Tuple[int, List[Any]]] = None
    open_ottava: Optional[Tuple[str, int, List[Any]]] = None
    open_pedal: Optional[Tuple[int, List[Any]]] = None

    def _emit(spanner_obj):
        try:
            part.insert(0, spanner_obj)
        except Exception:
            pass

    def _close_slur(voice: int):
        entry = open_slurs.pop(voice, None)
        if entry and len(entry[1]) >= 2:
            _emit(music21.spanner.Slur(entry[1]))

    def _close_hairpin():
        nonlocal open_hairpin
        if open_hairpin and len(open_hairpin[2]) >= 2:
            kind, _b, notes = open_hairpin
            cls = (
                music21.dynamics.Crescendo
                if kind.startswith("cresc")
                else music21.dynamics.Diminuendo
            )
            _emit(cls(notes))
        open_hairpin = None

    def _close_gliss():
        nonlocal open_gliss
        if open_gliss and len(open_gliss[1]) >= 2:
            _emit(music21.spanner.Glissando(open_gliss[1]))
        open_gliss = None

    def _close_ottava():
        nonlocal open_ottava
        if open_ottava and open_ottava[2]:
            kind, _b, notes = open_ottava
            try:
                _emit(music21.spanner.Ottava(notes, type=kind))
            except Exception:
                pass
        open_ottava = None

    def _close_pedal():
        nonlocal open_pedal
        if open_pedal and len(open_pedal[1]) >= 2:
            try:
                _emit(music21.expressions.PedalMark(open_pedal[1]))
            except Exception:
                pass
        open_pedal = None

    for event in ordered:
        n = note_map[id(event)]
        vid = getattr(event, "voice", 1) or 1
        bar = event.bar

        # Extend every open span this note falls inside, then time it out.
        for v, (b0, notes) in list(open_slurs.items()):
            if v != vid:
                continue
            notes.append(n)
            if bar - b0 >= _MAX_SPANNER_BARS:
                _close_slur(v)
        if open_hairpin:
            open_hairpin[2].append(n)
            if bar - open_hairpin[1] >= _MAX_SPANNER_BARS:
                _close_hairpin()
        if open_gliss:
            open_gliss[1].append(n)
            if bar - open_gliss[0] > 1:
                _close_gliss()
        if open_ottava:
            open_ottava[2].append(n)
            if bar - open_ottava[1] >= _MAX_SPANNER_BARS * 2:
                _close_ottava()
        if open_pedal:
            open_pedal[1].append(n)
            if bar - open_pedal[0] >= _MAX_SPANNER_BARS:
                _close_pedal()

        if event.slur == "start":
            if vid in open_slurs:
                _close_slur(vid)
            open_slurs[vid] = (bar, [n])
        elif event.slur == "stop" and vid in open_slurs:
            _close_slur(vid)

        hp = event.hairpin or ""
        if hp in ("cresc_start", "dim_start", "cresc", "dim", "<", ">"):
            if open_hairpin:
                _close_hairpin()
            kind = "cresc" if hp in ("cresc_start", "cresc", "<") else "dim"
            open_hairpin = (kind, bar, [n])
        elif hp in ("stop", "cresc_stop", "dim_stop", "!") and open_hairpin:
            _close_hairpin()

        tech = getattr(event, "technique", None)
        if tech == "gliss_start":
            _close_gliss()
            open_gliss = (bar, [n])
        elif tech == "gliss_stop":
            _close_gliss()
        elif tech in ("8va", "8vb"):
            _close_ottava()
            open_ottava = ("8va" if tech == "8va" else "8vb", bar, [n])
        elif tech == "octave_stop":
            _close_ottava()

        ped = getattr(event, "pedal", None)
        if ped in ("down", "change"):
            # "change" is a lift-and-retake: close the span and open the next.
            _close_pedal()
            open_pedal = (bar, [n])
        elif ped == "up":
            _close_pedal()

    for v in list(open_slurs):
        _close_slur(v)
    _close_hairpin()
    _close_gliss()
    _close_ottava()
    _close_pedal()


def _parse_key(key_str: str):
    """Delegates to the single canonical parser (pitch.parse_key)."""
    from .pitch import parse_key

    return parse_key(key_str)
