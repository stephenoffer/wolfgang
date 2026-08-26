"""
SurfaceComposer — phrase-level, context-driven composition.

Replaces the bar-by-bar fallback approach with a phrase-level composer that:
1. Retrieves phrase prototypes from PhraseBank
2. Plans gesture slots between melody anchors
3. Co-composes melody + accompaniment per gesture slot
4. Uses gesture families from GestureBank for melodic fill
5. Adapts patterns to harmony via chord-tone slot roles
6. Integrates cadences as specialized gesture slots
7. Falls back constructively with style-specific figuration

Every bar is shaped by corpus-derived, hand-made musical material.
Procedural filler is a last-resort repair path, not a normal path.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from .cadence_bank import CadenceBank
from .corpus_bar_retriever import CorpusBarRetriever
from .duration import DURATION_VALUES, bar_duration
from .enums import AccompType, NoteJustification, NoteRole
from .gesture_bank import GestureBank
from .models import (
    Anchor,
    CadenceQuery,
    ContextTrace,
    GestureQuery,
    GestureResult,
    HarmonicCell,
    LayerEvent,
    LayerIR,
    MotifPlacement,
    OnsetBundle,
    OnsetEvent,
    OnsetJustification,
    PhraseBoundaryState,
    PhraseContext,
    PhraseControlIR,
    PhraseQuery,
    PhraseResult,
    StyleProgram,
)
from .motif_realization import (
    emit_motif_melody_events,
    first_scale_degree_midi,
    pick_motif_slot_for_bar,
)
from .pattern_retriever import PatternRetriever
from .phrase_bank import PhraseBank
from .pitch import (
    SCALE_INTERVALS,
    build_scale,
    chord_tones,
    clamp_to_range,
    is_minor_key,
    key_to_root_midi,
    midi_to_pitch,
    pitch_to_midi,
    snap_to_scale,
)

logger = logging.getLogger(__name__)


# ─── Internal dataclasses ─────────────────────────────────────────────────────


@dataclass
class GestureSlot:
    """A time span within a phrase where one gesture family operates."""

    bar_start: int = 1
    beat_start: float = 1.0
    bar_end: int = 1
    beat_end: float = 1.0
    span_beats: float = 4.0
    function: str = "continuation"  # pickup, answer, sequence, insist, cadential, arrival
    rh_texture: str = "singing_melody"
    lh_texture: str = "alberti"
    anchor_start: Optional[Anchor] = None
    anchor_end: Optional[Anchor] = None
    bass_anchors: List[Anchor] = field(default_factory=list)
    harmonic_cells: List[HarmonicCell] = field(default_factory=list)
    density_target: int = 8
    is_cadence_zone: bool = False


@dataclass
class SlotExitState:
    """Exit state from one gesture slot, feeds into the next."""

    last_melody_midi: Optional[int] = None
    last_bass_midi: Optional[int] = None
    last_beat: float = 1.0
    last_dynamic: Optional[str] = None
    contour: str = ""  # ascending / descending / static


# ─── SurfaceComposer ──────────────────────────────────────────────────────────


class SurfaceComposer:
    """Phrase-level, context-driven onset bundle composer.

    Composes melody and accompaniment together per gesture slot,
    using retrieved phrase prototypes, gesture families, and
    pattern families from corpus data.
    """

    def __init__(
        self,
        pattern_retriever: PatternRetriever,
        phrase_bank: Optional[PhraseBank] = None,
        gesture_bank: Optional[GestureBank] = None,
        corpus_bar_retriever: Optional[CorpusBarRetriever] = None,
        cadence_bank: Optional[CadenceBank] = None,
        motif_bank: Optional[Dict[str, Any]] = None,
    ):
        self.pattern_retriever = pattern_retriever
        self.phrase_bank = phrase_bank
        self.gesture_bank = gesture_bank
        self.corpus_bar_retriever = corpus_bar_retriever
        self.cadence_bank = cadence_bank
        self.motif_bank = motif_bank or {}

    # ─── Public API ───────────────────────────────────────────────────────

    def compose(
        self,
        control: PhraseControlIR,
        phrase_context: PhraseContext,
        harmonic_voicings: List[Dict],
        style_program: StyleProgram,
        continuation: Optional[PhraseBoundaryState] = None,
        variant: int = 0,
    ) -> Tuple[List[OnsetBundle], ContextTrace]:
        """Compose a phrase as coordinated onset bundles.

        Pipeline:
        1. Select phrase prototype from PhraseBank
        2. Plan gesture slots between melody anchors
        3. Co-compose melody + accompaniment per slot
        4. Integrate cadences
        5. Apply dynamics, breathing, boundary states
        """
        trace = ContextTrace(
            phrase_id=control.phrase_id,
            total_bar_count=control.bars,
        )
        voicing_map = self._index_voicings(harmonic_voicings)
        key = control.local_key
        mode = "minor" if is_minor_key(key) else "major"
        root = key_to_root_midi(key)
        scale = build_scale(root + 60, mode)
        bar_dur = bar_duration(control.meter)

        # Stage 1: Phrase prototype
        prototype = self._select_prototype(control, phrase_context, style_program, trace)

        # Stage 2: Gesture slot planning
        slots = self._plan_gesture_slots(control, voicing_map, prototype)

        # Stage 3: Co-composed realization per slot
        all_bundles: List[OnsetBundle] = []
        prev_exit = SlotExitState()
        if continuation and continuation.pitch:
            prev_exit.last_melody_midi = pitch_to_midi(continuation.pitch)
            prev_exit.last_dynamic = getattr(continuation, "dynamic", None)

        for slot in slots:
            slot_bundles, prev_exit = self._realize_slot(
                slot,
                control,
                phrase_context,
                voicing_map,
                style_program,
                scale,
                key,
                mode,
                root,
                bar_dur,
                variant,
                prev_exit,
                trace,
            )
            all_bundles.extend(slot_bundles)

        # Stage 5: Dynamics from sketch
        self._apply_dynamics(all_bundles, control)

        # Stage 5b: Breathing
        if phrase_context.breathing_plan:
            self._apply_breathing(all_bundles, phrase_context.breathing_plan, control, trace)

        all_bundles.sort(key=lambda b: (b.bar, b.beat))
        return all_bundles, trace

    def bundles_to_layer_ir(
        self,
        bundles: List[OnsetBundle],
        phrase_id: str,
        key: str,
        meter: Tuple[int, int],
        bar_count: int,
    ) -> LayerIR:
        """Convert onset bundles to LayerIR for backward compatibility."""
        layer = LayerIR(
            phrase_id=phrase_id,
            instrumentation="solo_piano",
            key=key,
            meter=meter,
            bar_count=bar_count,
        )
        voice_to_layer = {
            "soprano": "principal_line",
            "melody": "principal_line",
            "bass": "bass_foundation",
            "accomp": "response_layer",
            "inner": "response_layer",
            "inner_1": "response_layer",
            "inner_2": "response_layer",
            "alto": "counter_reply",
            "tenor": "counter_reply",
            "counter": "counter_reply",
            "ornament": "ornamental_surface",
        }
        for bundle in bundles:
            for onset in bundle.events:
                layer_name = voice_to_layer.get(onset.voice, "response_layer")
                layer_list = getattr(layer, layer_name)

                pitch = onset.pitch
                if isinstance(pitch, list):
                    valid = [p for p in pitch if p != "rest"]
                    if not valid:
                        continue
                    midis = [(p, pitch_to_midi(p)) for p, _ in [(p, None) for p in valid]]
                    midis = [(p, pitch_to_midi(p)) for p in valid]
                    midis = [(p, m) for p, m in midis if m is not None]
                    if not midis:
                        continue
                    pitch = (
                        min(midis, key=lambda x: x[1])[0]
                        if layer_name == "bass_foundation"
                        else max(midis, key=lambda x: x[1])[0]
                    )

                if layer_name == "bass_foundation" and pitch != "rest":
                    m = pitch_to_midi(pitch)
                    if m is not None:
                        pitch = midi_to_pitch(clamp_to_range(m, 36, 60), key)
                if layer_name == "principal_line" and pitch != "rest":
                    m = pitch_to_midi(pitch)
                    if m is not None:
                        pitch = midi_to_pitch(clamp_to_range(m, 60, 84), key)

                layer_list.append(
                    LayerEvent(
                        bar=bundle.bar,
                        beat=bundle.beat,
                        pitch=pitch,
                        duration=onset.duration,
                        role=onset.role,
                        dynamic=onset.dynamic,
                        articulation=onset.articulation,
                        ornament=onset.ornament,
                        tie=onset.tie,
                        expression=onset.expression,
                        source_layer=layer_name,
                    )
                )
        return layer

    # ─── Stage 1: Prototype Selection ─────────────────────────────────────

    def _select_prototype(
        self, control: PhraseControlIR, ctx: PhraseContext, sp: StyleProgram, trace: ContextTrace
    ) -> Optional[PhraseResult]:
        """Find a phrase prototype from corpus matching this phrase's role."""
        if not self.phrase_bank:
            return None
        try:
            mode = "minor" if is_minor_key(control.local_key) else "major"
            tex0 = control.texture_program.bars[0] if control.texture_program.bars else None
            query = PhraseQuery(
                formal_function=control.phrase_function,
                cadence_type=control.cadence_target,
                length_range=(max(2, control.bars - 2), control.bars + 2),
                key_mode=mode,
                rh_texture_family=tex0.rh_texture if tex0 else None,
                lh_texture_family=tex0.lh_texture if tex0 else None,
                n=3,
            )
            results = self.phrase_bank.retrieve(query)
            if results:
                proto = results[0]
                trace.corpus_patterns_used.append(f"prototype:{proto.phrase_id}")
                return proto
        except Exception:
            pass
        return None

    # ─── Stage 2: Gesture Slot Planning ───────────────────────────────────

    def _plan_gesture_slots(
        self,
        control: PhraseControlIR,
        voicing_map: Dict[int, Dict],
        prototype: Optional[PhraseResult],
    ) -> List[GestureSlot]:
        """Divide the phrase into gesture slots between consecutive melody anchors."""
        anchors = sorted(control.melody_anchors, key=lambda a: (a.bar, a.beat))
        bass_anchors = sorted(control.bass_anchors, key=lambda a: (a.bar, a.beat))
        bar_dur = bar_duration(control.meter)
        cadence_bar = control.cadence_bar or (control.bar_start + control.bars - 1)
        slots: List[GestureSlot] = []

        if not anchors:
            # No melody anchors — make one slot per bar
            for bar_off in range(control.bars):
                bar = control.bar_start + bar_off
                tex = self._get_texture_for_bar(control, bar_off)
                slots.append(
                    GestureSlot(
                        bar_start=bar,
                        beat_start=1.0,
                        bar_end=bar,
                        beat_end=bar_dur,
                        span_beats=bar_dur,
                        function="continuation",
                        rh_texture=tex[0],
                        lh_texture=tex[1],
                        harmonic_cells=self._cells_for_range(control, bar, 1.0, bar, bar_dur),
                        bass_anchors=[a for a in bass_anchors if a.bar == bar],
                        density_target=tex[2],
                        is_cadence_zone=abs(cadence_bar - bar) <= 1,
                    )
                )
            return slots

        # Build slots between consecutive anchors
        for i in range(len(anchors)):
            a_start = anchors[i]
            a_end = anchors[i + 1] if i + 1 < len(anchors) else None

            bar_s, beat_s = a_start.bar, a_start.beat
            if a_end:
                bar_e, beat_e = a_end.bar, a_end.beat
            else:
                # Last anchor to end of phrase
                bar_e = control.bar_start + control.bars - 1
                beat_e = bar_dur

            span = (bar_e - bar_s) * bar_dur + (beat_e - beat_s)
            if span <= 0:
                span = bar_dur

            # Infer function
            fn = self._infer_slot_function(
                i, len(anchors), a_start, a_end, cadence_bar, bar_dur, control
            )

            # Texture from plan
            bar_off = bar_s - control.bar_start
            tex = self._get_texture_for_bar(control, bar_off)

            # Is this near the cadence?
            is_cad = abs(cadence_bar - bar_e) <= 1 or abs(cadence_bar - bar_s) <= 1

            slots.append(
                GestureSlot(
                    bar_start=bar_s,
                    beat_start=beat_s,
                    bar_end=bar_e,
                    beat_end=beat_e,
                    span_beats=span,
                    function=fn,
                    rh_texture=tex[0],
                    lh_texture=tex[1],
                    anchor_start=a_start,
                    anchor_end=a_end,
                    harmonic_cells=self._cells_for_range(control, bar_s, beat_s, bar_e, beat_e),
                    bass_anchors=[a for a in bass_anchors if bar_s <= a.bar <= bar_e],
                    density_target=tex[2],
                    is_cadence_zone=is_cad,
                )
            )

        return slots

    def _infer_slot_function(
        self,
        idx: int,
        total: int,
        anchor_start: Anchor,
        anchor_end: Optional[Anchor],
        cadence_bar: int,
        bar_dur: float,
        control: PhraseControlIR,
    ) -> str:
        """Infer the rhetorical function of a gesture slot."""
        if idx == 0:
            return "entry"
        if anchor_end is None or idx == total - 1:
            return "arrival"
        if anchor_end and abs(cadence_bar - anchor_end.bar) <= 1:
            return "cadential"
        if anchor_start.role == "peak":
            return "peak_response"
        if anchor_start.role == "motif":
            return "motif_statement"

        # Determine contour direction
        start_midi = (
            pitch_to_midi(anchor_start.pitch_or_degree)
            if not anchor_start.pitch_or_degree.startswith("^")
            else None
        )
        end_midi = (
            pitch_to_midi(anchor_end.pitch_or_degree)
            if anchor_end and not anchor_end.pitch_or_degree.startswith("^")
            else None
        )
        if start_midi and end_midi:
            if end_midi > start_midi + 2:
                return "rising_continuation"
            elif end_midi < start_midi - 2:
                return "falling_continuation"

        if idx < total // 2:
            return "continuation"
        return "winding_down"

    # ─── Stage 3: Co-Composed Realization ─────────────────────────────────

    def _realize_slot(
        self,
        slot: GestureSlot,
        control: PhraseControlIR,
        ctx: PhraseContext,
        voicing_map: Dict[int, Dict],
        sp: StyleProgram,
        scale: List[int],
        key: str,
        mode: str,
        root: int,
        bar_dur: float,
        variant: int,
        prev_exit: SlotExitState,
        trace: ContextTrace,
    ) -> Tuple[List[OnsetBundle], SlotExitState]:
        """Co-compose melody + accompaniment for one gesture slot."""
        bundles: List[OnsetBundle] = []

        # 3a: Resolve melody anchor pitches
        start_midi = (
            self._resolve_pitch(slot.anchor_start, key, mode, root, prev_exit.last_melody_midi)
            if slot.anchor_start
            else prev_exit.last_melody_midi
        )
        end_midi = (
            self._resolve_pitch(slot.anchor_end, key, mode, root, start_midi)
            if slot.anchor_end
            else start_midi
        )

        # 3b: Retrieve gesture for melodic fill between anchors
        gesture = self._retrieve_gesture(slot, ctx, key, mode, trace)

        # 3c: Generate melody events (anchor + gesture fill)
        melody_events = self._construct_melody(
            slot,
            start_midi,
            end_midi,
            gesture,
            scale,
            key,
            bar_dur,
            trace,
            control,
        )

        # 3d: Generate accompaniment events (pattern-adapted + harmony-aware)
        accomp_events = self._construct_accompaniment(
            slot,
            melody_events,
            voicing_map,
            control,
            ctx,
            sp,
            key,
            mode,
            root,
            scale,
            bar_dur,
            variant,
            trace,
        )

        # 3e: Merge into bundles
        all_events = melody_events + accomp_events

        # Deduplicate: remove events with same (bar, beat, voice, pitch)
        seen = set()
        deduped = []
        for evt in all_events:
            p = str(evt.pitch) if isinstance(evt.pitch, list) else evt.pitch
            sig = (evt._bar, round(evt._beat, 2), evt.voice, p)
            if sig not in seen:
                seen.add(sig)
                deduped.append(evt)
        all_events = deduped

        # Group by (bar, beat)
        time_groups: Dict[Tuple[int, float], List[OnsetEvent]] = {}
        for evt in all_events:
            k = (evt._bar, round(evt._beat, 2))
            time_groups.setdefault(k, []).append(evt)

        for (bar, beat), evts in sorted(time_groups.items()):
            b = OnsetBundle(bar=bar, beat=beat)
            # Find harmonic cell for this position
            for cell in slot.harmonic_cells:
                if cell.bar == bar:
                    b.harmonic_cell = cell
                    break
            for e in evts:
                b.events.append(
                    OnsetEvent(
                        voice=e.voice,
                        pitch=e.pitch,
                        duration=e.duration,
                        role=e.role,
                        dynamic=e.dynamic,
                        articulation=e.articulation,
                        ornament=e.ornament,
                        tie=e.tie,
                        expression=e.expression,
                        justification=e.justification,
                    )
                )
            bundles.append(b)

        # Update exit state
        exit_state = SlotExitState(
            last_melody_midi=end_midi or start_midi,
            last_bass_midi=self._last_bass_midi(accomp_events),
            last_beat=slot.beat_end,
            last_dynamic=prev_exit.last_dynamic,
        )
        return bundles, exit_state

    # ─── Melody Construction ──────────────────────────────────────────────

    def _construct_melody(
        self,
        slot: GestureSlot,
        start_midi: Optional[int],
        end_midi: Optional[int],
        gesture: Optional[GestureResult],
        scale: List[int],
        key: str,
        bar_dur: float,
        trace: ContextTrace,
        control: PhraseControlIR,
    ) -> List["_TaggedEvent"]:
        """Build melody events for a gesture slot using anchor interpolation.

        Uses gesture dur_profile for rhythm and scale-walking for pitch.
        When motif_slots + motif_bank supply material for a bar in this slot,
        emits motif rhythm/intervals instead of generic interpolation.
        """
        events: List[_TaggedEvent] = []
        if start_midi is None:
            return events

        effective_end = end_midi if end_midi is not None else start_midi

        # Motif-driven realization for any bar in this slot with a MotifSlot
        if self.motif_bank and getattr(control, "motif_slots", None):
            motif_events: List[_TaggedEvent] = []
            for bar in range(int(slot.bar_start), int(slot.bar_end) + 1):
                ms = pick_motif_slot_for_bar(control.motif_slots, bar)
                if not ms:
                    continue
                motif = self.motif_bank.get(ms.motif_id)
                if not motif or not motif.rhythm_cell:
                    continue
                sm = start_midi
                fsd = first_scale_degree_midi(motif, scale)
                if fsd is not None:
                    sm = fsd
                placement = MotifPlacement(
                    bar=ms.bar,
                    beat=ms.beat,
                    motif_id=ms.motif_id,
                    transform=ms.transform,
                    voice=ms.voice,
                    params=dict(ms.params or {}),
                )
                raw = emit_motif_melody_events(
                    motif,
                    placement,
                    key,
                    scale,
                    int(sm),
                    bar_dur,
                )
                for r in raw:
                    if slot.bar_start <= r["bar"] <= slot.bar_end:
                        motif_events.append(
                            _TaggedEvent(
                                bar=r["bar"],
                                beat=r["beat"],
                                voice="soprano",
                                pitch=r["pitch"],
                                duration=r["duration"],
                                role=r["role"],
                                justification=OnsetJustification(
                                    structural_reasons=[NoteJustification.MOTIVE.value],
                                ),
                            )
                        )
                trace.gestures_applied.append(f"motif:{ms.motif_id}")
            if motif_events:
                return motif_events

        # Place the start anchor
        events.append(
            _TaggedEvent(
                bar=slot.bar_start,
                beat=slot.beat_start,
                voice="soprano",
                pitch=midi_to_pitch(clamp_to_range(start_midi, 60, 84), key),
                duration="q",
                role=NoteRole.STRUCTURAL.value,
                justification=OnsetJustification(
                    structural_reasons=[NoteJustification.FORM.value],
                ),
            )
        )

        # If there's a gesture dur_profile, use it for rhythmic skeleton
        if gesture and gesture.dur_profile:
            pitches = self._interpolate_melody_pitches(
                start_midi, effective_end, len(gesture.dur_profile), scale, key
            )
            # An EXACT cursor, and emit-then-advance.
            #
            # Two faults here, both silent. The cursor was a float advanced by
            # durations and then rounded to two decimals, so a position of
            # 1.5625 — a legitimate 64th-note offset — was emitted as `1.56`,
            # which is not a position in any bar and which no notation can
            # express. Downstream that arrived as an off-grid onset and a bar
            # that did not sum to its meter.
            #
            # And the cursor advanced BEFORE the note was emitted, so every
            # gesture started one note-value late and its last note ran past the
            # end of the slot. A four-note figure beginning on beat 1 was written
            # beginning on beat 1.5.
            beat_cursor = Fraction(str(slot.beat_start)).limit_denominator(96)
            bar_len = Fraction(str(bar_dur)).limit_denominator(96)
            bar_cursor = slot.bar_start
            for i, dur_code in enumerate(gesture.dur_profile):
                dur_beats = DURATION_VALUES.get(dur_code, Fraction(1, 2))
                if not isinstance(dur_beats, Fraction):
                    dur_beats = Fraction(str(dur_beats)).limit_denominator(96)
                while beat_cursor > bar_len:
                    beat_cursor -= bar_len
                    bar_cursor += 1
                if bar_cursor > slot.bar_end:
                    break
                if i < len(pitches):
                    midi_val = clamp_to_range(pitches[i], 60, 84)
                    events.append(
                        _TaggedEvent(
                            bar=bar_cursor,
                            beat=float(beat_cursor),
                            voice="soprano",
                            pitch=midi_to_pitch(midi_val, key),
                            duration=dur_code,
                            role=NoteRole.PASSING.value if i > 0 else NoteRole.STRUCTURAL.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.REGISTER_SHAPING.value],
                                local_reasons=[NoteJustification.VOICE_LEADING.value],
                                context_trace=f"gesture:{gesture.cell_id}" if gesture else "",
                            ),
                        )
                    )
                # Advance AFTER emitting, so the first note lands on the
                # slot's own start beat rather than one value past it.
                beat_cursor += dur_beats
        else:
            # No gesture — generate scale-walk between anchors
            bars_in_slot = max(1, slot.bar_end - slot.bar_start)
            if bars_in_slot > 1 and start_midi != effective_end:
                steps = self._interpolate_melody_pitches(
                    start_midi, effective_end, bars_in_slot, scale, key
                )
                for i, midi_val in enumerate(steps):
                    bar = slot.bar_start + i + 1
                    if bar > slot.bar_end:
                        break
                    midi_val = clamp_to_range(midi_val, 60, 84)
                    # Alternate q and e for rhythmic variety
                    dur = "q" if i % 2 == 0 else "e"
                    events.append(
                        _TaggedEvent(
                            bar=bar,
                            beat=1.0,
                            voice="soprano",
                            pitch=midi_to_pitch(midi_val, key),
                            duration=dur,
                            role=NoteRole.PASSING.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.REGISTER_SHAPING.value],
                            ),
                        )
                    )

        # Place end anchor if it exists and is different from start
        if slot.anchor_end and end_midi is not None and slot.anchor_end.bar != slot.bar_start:
            events.append(
                _TaggedEvent(
                    bar=slot.anchor_end.bar,
                    beat=slot.anchor_end.beat,
                    voice="soprano",
                    pitch=midi_to_pitch(clamp_to_range(end_midi, 60, 84), key),
                    duration="q" if slot.anchor_end.role != "cadence" else "h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.FORM.value],
                    ),
                )
            )

        return events

    def _interpolate_melody_pitches(
        self, start_midi: int, end_midi: int, n_steps: int, scale: List[int], key: str
    ) -> List[int]:
        """Generate n_steps pitches walking from start_midi toward end_midi through the scale."""
        if n_steps <= 0:
            return []
        if n_steps == 1:
            return [(start_midi + end_midi) // 2]

        # Find scale indices closest to start and end
        start_idx = min(range(len(scale)), key=lambda i: abs(scale[i] - start_midi))
        end_idx = min(range(len(scale)), key=lambda i: abs(scale[i] - end_midi))

        result = []
        for step in range(1, n_steps + 1):
            # Linear interpolation through scale indices
            t = step / (n_steps + 1)
            idx = int(start_idx + (end_idx - start_idx) * t)
            idx = max(0, min(len(scale) - 1, idx))
            result.append(scale[idx])

        return result

    # ─── Accompaniment Construction ───────────────────────────────────────

    def _construct_accompaniment(
        self,
        slot: GestureSlot,
        melody_events: List["_TaggedEvent"],
        voicing_map: Dict[int, Dict],
        control: PhraseControlIR,
        ctx: PhraseContext,
        sp: StyleProgram,
        key: str,
        mode: str,
        root: int,
        scale: List[int],
        bar_dur: float,
        variant: int,
        trace: ContextTrace,
    ) -> List["_TaggedEvent"]:
        """Generate accompaniment events aware of melody occupancy.

        Retrieval hierarchy:
        1. Pattern retrieval adapted to harmony
        2. Corpus bar retrieval
        3. Style-specific constructive fallback
        """
        events: List[_TaggedEvent] = []

        # Melody occupancy map: which beats have melody?
        mel_beats: Dict[int, List[float]] = {}
        for me in melody_events:
            mel_beats.setdefault(me._bar, []).append(me._beat)

        # Process bar by bar within the slot
        for bar in range(slot.bar_start, slot.bar_end + 1):
            bar_off = bar - control.bar_start
            voicing = voicing_map.get(bar)
            mel_active = mel_beats.get(bar, [])
            tex = self._get_texture_for_bar(control, bar_off)
            lh_texture = tex[1]

            # Get the harmonic cell for this bar
            cell = None
            for c in slot.harmonic_cells:
                if c.bar == bar:
                    cell = c
                    break

            # Bass anchor for this bar
            bass_anchor = None
            for ba in slot.bass_anchors:
                if ba.bar == bar:
                    bass_anchor = ba
                    break

            # Determine bass pitch
            bass_midi = self._resolve_bass_pitch(bass_anchor, voicing, key, mode, root)

            # Determine chord tones for this bar
            bar_chord_tones = self._get_chord_tones_for_bar(cell, voicing, root, mode)

            # --- Retrieval hierarchy ---
            bar_events = None

            # 1. Try pattern retrieval
            if lh_texture in ctx.active_patterns:
                patterns = ctx.active_patterns[lh_texture]
                if patterns:
                    pattern = patterns[(variant + bar_off) % len(patterns)]
                    bar_events = self._adapt_pattern_to_harmony(
                        pattern,
                        bar,
                        bar_chord_tones,
                        bass_midi,
                        key,
                        mode,
                        scale,
                        mel_active,
                        trace,
                    )

            # 2. Try corpus bar retrieval
            if bar_events is None and self.corpus_bar_retriever:
                bar_events = self._retrieve_corpus_bar(
                    bar, control, lh_texture, tex[0], mode, key, trace
                )

            # 3. Cadence-specialized treatment
            if bar_events is None and slot.is_cadence_zone and self.cadence_bank:
                bar_events = self._cadence_bar_events(bar, control, key, mode, voicing, trace)

            # 4. Style-specific constructive fallback
            if bar_events is None:
                bar_events = self._constructive_fallback(
                    bar,
                    lh_texture,
                    bass_midi,
                    bar_chord_tones,
                    key,
                    mode,
                    scale,
                    mel_active,
                    bar_dur,
                    sp,
                    trace,
                )

            if bar_events:
                events.extend(bar_events)

        return events

    def _adapt_pattern_to_harmony(
        self,
        pattern: Dict,
        bar: int,
        chord_tones_midi: List[int],
        bass_midi: int,
        key: str,
        mode: str,
        scale: List[int],
        mel_active: List[float],
        trace: ContextTrace,
    ) -> Optional[List["_TaggedEvent"]]:
        """Adapt a retrieved pattern to the current harmony by re-mapping chord slots."""
        try:
            lh_events = self.pattern_retriever.pattern_to_events(
                pattern,
                bar,
                target_key=key,
            )
        except Exception:
            return None

        if not lh_events:
            return None

        events: List[_TaggedEvent] = []
        for evt in lh_events:
            # Snap each pattern pitch to nearest chord tone
            evt_midi = pitch_to_midi(evt.pitch)
            if evt_midi is not None and chord_tones_midi:
                snapped = min(chord_tones_midi, key=lambda ct: abs(ct - evt_midi))
                # Keep in LH register
                snapped = clamp_to_range(snapped, 36, 60)
                pitch = midi_to_pitch(snapped, key)
            else:
                pitch = evt.pitch

            voice = "bass" if evt.beat <= 1.01 else "accomp"
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=evt.beat,
                    voice=voice,
                    pitch=pitch,
                    duration=evt.duration,
                    role=evt.role or NoteRole.ARPEGGIATED_FILL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.HARMONY.value],
                        context_trace=f"pattern:{pattern.get('hash', '')}",
                    ),
                )
            )

        trace.corpus_patterns_used.append(pattern.get("hash", ""))
        return events

    def _retrieve_corpus_bar(
        self,
        bar: int,
        control: PhraseControlIR,
        lh_texture: str,
        rh_texture: str,
        mode: str,
        key: str,
        trace: ContextTrace,
    ) -> Optional[List["_TaggedEvent"]]:
        """Retrieve a corpus bar and convert to tagged events."""
        try:
            corpus_bar = self.corpus_bar_retriever.retrieve_bar(
                time_sig=control.meter,
                key_mode=mode,
                rh_texture=rh_texture,
                lh_texture=lh_texture,
            )
            if corpus_bar:
                _rh, lh = self.corpus_bar_retriever.bar_to_events(
                    corpus_bar,
                    bar,
                    key,
                )
                events = []
                for evt in lh:
                    events.append(
                        _TaggedEvent(
                            bar=bar,
                            beat=evt.beat,
                            voice="bass" if evt.beat <= 1.01 else "accomp",
                            pitch=evt.pitch,
                            duration=evt.duration,
                            role=evt.role or NoteRole.ARPEGGIATED_FILL.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.HARMONY.value],
                                context_trace=f"corpus_bar:{corpus_bar.get('source', '')}",
                            ),
                        )
                    )
                trace.corpus_bars_used.append(corpus_bar.get("source", ""))
                return events
        except Exception:
            pass
        return None

    def _cadence_bar_events(
        self,
        bar: int,
        control: PhraseControlIR,
        key: str,
        mode: str,
        voicing: Optional[Dict],
        trace: ContextTrace,
    ) -> Optional[List["_TaggedEvent"]]:
        """Generate cadence-specialized accompaniment."""
        try:
            query = CadenceQuery(
                cadence_type=control.cadence_target,
                key=key,
                mode=mode,
                approach_length_bars=2,
                n=1,
            )
            results = self.cadence_bank.retrieve(query)
            if results and results[0].chord_sequence:
                cad = results[0]
                cad_bar = control.cadence_bar or (control.bar_start + control.bars - 1)
                idx = len(cad.chord_sequence) - 1 - (cad_bar - bar)
                if 0 <= idx < len(cad.chord_sequence):
                    root_midi = key_to_root_midi(key) + 36
                    tones = chord_tones(root_midi, "major")
                    if tones:
                        events = []
                        # Bass note
                        events.append(
                            _TaggedEvent(
                                bar=bar,
                                beat=1.0,
                                voice="bass",
                                pitch=midi_to_pitch(clamp_to_range(tones[0], 36, 60), key),
                                duration="h",
                                role=NoteRole.STRUCTURAL.value,
                                justification=OnsetJustification(
                                    structural_reasons=[NoteJustification.HARMONY.value],
                                    context_trace=f"cadence:{cad.cadence_id}",
                                ),
                            )
                        )
                        # Inner voice on beat 3
                        if len(tones) > 1:
                            events.append(
                                _TaggedEvent(
                                    bar=bar,
                                    beat=3.0,
                                    voice="accomp",
                                    pitch=midi_to_pitch(clamp_to_range(tones[1], 48, 67), key),
                                    duration="q",
                                    role=NoteRole.STRUCTURAL.value,
                                    justification=OnsetJustification(
                                        structural_reasons=[NoteJustification.HARMONY.value],
                                        context_trace=f"cadence:{cad.cadence_id}",
                                    ),
                                )
                            )
                        trace.corpus_patterns_used.append(f"cadence:{cad.cadence_id}")
                        return events
        except Exception:
            pass
        return None

    # ─── Constructive Fallback ────────────────────────────────────────────

    def _constructive_fallback(
        self,
        bar: int,
        lh_texture: str,
        bass_midi: int,
        chord_tones_midi: List[int],
        key: str,
        mode: str,
        scale: List[int],
        mel_active: List[float],
        bar_dur: float,
        sp: StyleProgram,
        trace: ContextTrace,
    ) -> List["_TaggedEvent"]:
        """Style-specific constructive fallback — never dead silence.

        Generates idiomatic LH patterns from chord tones based on
        the requested texture type. Every bar sounds musical.
        """
        events: List[_TaggedEvent] = []
        bass_pitch = midi_to_pitch(clamp_to_range(bass_midi, 36, 55), key)

        # Ensure we have chord tones in LH range
        ct = (
            [clamp_to_range(t, 48, 67) for t in chord_tones_midi]
            if chord_tones_midi
            else [bass_midi + 12, bass_midi + 7]
        )
        ct_pitches = [midi_to_pitch(m, key) for m in ct]

        # Melody busy on beat 1? Thin the accompaniment
        mel_on_1 = 1.0 in mel_active

        just = OnsetJustification(
            structural_reasons=[NoteJustification.HARMONY.value],
            local_reasons=[NoteJustification.VOICE_LEADING.value],
            context_trace=f"constructive_fallback:{lh_texture}",
        )

        if lh_texture in ("alberti", AccompType.ALBERTI.value):
            # Alberti: root-fifth-third-fifth as eighths
            pattern = [
                bass_pitch,
                ct_pitches[0] if ct_pitches else bass_pitch,
                ct_pitches[1]
                if len(ct_pitches) > 1
                else ct_pitches[0]
                if ct_pitches
                else bass_pitch,
                ct_pitches[0] if ct_pitches else bass_pitch,
            ]
            beats = (
                [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5] if bar_dur >= 4 else [1.0, 1.5, 2.0, 2.5]
            )
            for i, beat in enumerate(beats):
                if beat > bar_dur:
                    break
                p = pattern[i % len(pattern)]
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass" if beat == 1.0 else "accomp",
                        pitch=p,
                        duration="e",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("broken_chord_wave", AccompType.BROKEN_CHORD_WAVE.value):
            # Broken chord ascending then descending
            up = [bass_pitch] + ct_pitches[:2]
            down = list(reversed(ct_pitches[:2])) + [bass_pitch]
            seq = up + down
            beats = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            for i, beat in enumerate(beats):
                if beat > bar_dur:
                    break
                p = seq[i % len(seq)]
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass" if beat == 1.0 else "accomp",
                        pitch=p,
                        duration="e",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("walking_bass", AccompType.WALKING_BASS.value):
            # Quarter-note scale walk from bass toward next chord tone
            walk = [bass_midi]
            for s in range(1, 4):
                next_tone = bass_midi + s * (2 if mode == "major" else (2 if s != 2 else 1))
                snapped = snap_to_scale(next_tone, scale, "above")
                walk.append(snapped if snapped else next_tone)
            for i, beat in enumerate([1.0, 2.0, 3.0, 4.0]):
                if beat > bar_dur or i >= len(walk):
                    break
                p = midi_to_pitch(clamp_to_range(walk[i], 36, 55), key)
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass",
                        pitch=p,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("bass_melody", AccompType.BASS_MELODY.value):
            # Contrapuntal bass: quarters on chord tones
            all_tones = [bass_midi] + ct[:2]
            for i, beat in enumerate([1.0, 2.0, 3.0, 4.0]):
                if beat > bar_dur:
                    break
                m = all_tones[i % len(all_tones)]
                p = midi_to_pitch(clamp_to_range(m, 36, 60), key)
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass",
                        pitch=p,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("block_chord_sparse", AccompType.BLOCK_CHORD_SPARSE.value):
            # Block chord on beats 1 and 3
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=just,
                )
            )
            if ct_pitches and bar_dur >= 3:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=3.0,
                        voice="accomp",
                        pitch=ct_pitches[0],
                        duration="h" if bar_dur >= 4 else "q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("pedal_point", AccompType.PEDAL_POINT.value):
            # Sustained bass
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="w" if bar_dur >= 4 else "h",
                    role=NoteRole.PEDAL_SUPPORT.value,
                    justification=just,
                )
            )

        elif lh_texture in ("sparse_punctuation", AccompType.SPARSE_PUNCTUATION.value):
            # Light touch — just beat 1 bass, short
            if not mel_on_1:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=1.0,
                        voice="bass",
                        pitch=bass_pitch,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        else:
            # Generic: bass + one inner voice
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=just,
                )
            )
            if ct_pitches and not mel_on_1:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=2.0,
                        voice="accomp",
                        pitch=ct_pitches[0],
                        duration="q",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )
            if len(ct_pitches) > 1 and bar_dur >= 3:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=3.0,
                        voice="accomp",
                        pitch=ct_pitches[1],
                        duration="q",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        trace.fallback_bar_count += 1
        return events

    # ─── Gesture Retrieval ────────────────────────────────────────────────

    def _retrieve_gesture(
        self, slot: GestureSlot, ctx: PhraseContext, key: str, mode: str, trace: ContextTrace
    ) -> Optional[GestureResult]:
        """Retrieve a gesture from GestureBank matching the slot's function."""
        if not self.gesture_bank:
            return None
        try:
            query = GestureQuery(
                function=slot.function,
                texture_rh=slot.rh_texture,
                texture_lh=slot.lh_texture,
                min_span_beats=max(1.0, slot.span_beats - 4),
                max_span_beats=slot.span_beats + 4,
                key_mode=mode,
                n=3,
            )
            results = self.gesture_bank.retrieve(query)
            if results:
                g = results[0]
                trace.gestures_applied.append(g.cell_id)
                return g
        except Exception:
            pass
        return None

    # ─── Pitch Resolution Helpers ─────────────────────────────────────────

    def _resolve_pitch(
        self, anchor: Optional[Anchor], key: str, mode: str, root: int, prev_midi: Optional[int]
    ) -> Optional[int]:
        """Resolve an anchor's pitch_or_degree to a MIDI value."""
        if anchor is None:
            return None

        pitch_str = anchor.pitch_or_degree
        if pitch_str.startswith("^"):
            intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
            degree = int(pitch_str[1:])
            idx = (degree - 1) % len(intervals)
            midi = 5 * 12 + root + intervals[idx]  # octave 4
            if degree > 7:
                midi += 12
        else:
            midi = pitch_to_midi(pitch_str)
            if midi is None:
                return prev_midi

        # Voice-leading: keep within a 5th of previous
        if prev_midi is not None:
            while midi - prev_midi > 7:
                midi -= 12
            while prev_midi - midi > 7:
                midi += 12

        return clamp_to_range(midi, 60, 84)

    def _resolve_bass_pitch(
        self, bass_anchor: Optional[Anchor], voicing: Optional[Dict], key: str, mode: str, root: int
    ) -> int:
        """Resolve bass pitch from anchor or voicing."""
        if bass_anchor:
            p = bass_anchor.pitch_or_degree
            if p.startswith("^"):
                intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
                degree = int(p[1:])
                idx = (degree - 1) % len(intervals)
                return clamp_to_range(3 * 12 + root + intervals[idx], 36, 55)
            m = pitch_to_midi(p)
            if m is not None:
                return clamp_to_range(m, 36, 55)

        if voicing and "bass_midi" in voicing:
            return clamp_to_range(voicing["bass_midi"], 36, 55)
        if voicing and "bass" in voicing:
            m = pitch_to_midi(voicing["bass"])
            if m is not None:
                return clamp_to_range(m, 36, 55)

        # Default to root in bass register
        return clamp_to_range(root + 36, 36, 55)

    def _get_chord_tones_for_bar(
        self, cell: Optional[HarmonicCell], voicing: Optional[Dict], root: int, mode: str
    ) -> List[int]:
        """Get MIDI chord tones for a bar from voicing or harmonic cell."""
        tones = []
        if voicing:
            for vk in ["soprano_midi", "alto_midi", "tenor_midi", "bass_midi"]:
                if vk in voicing:
                    tones.append(voicing[vk])
        if not tones:
            # Build from root + quality
            quality = "minor" if mode == "minor" else "major"
            tones = chord_tones(root + 48, quality)
        return tones

    def _last_bass_midi(self, events: List["_TaggedEvent"]) -> Optional[int]:
        """Get the last bass MIDI from accompaniment events."""
        for e in reversed(events):
            if e.voice == "bass" and e.pitch != "rest":
                m = pitch_to_midi(e.pitch)
                if m is not None:
                    return m
        return None

    # ─── Utilities ────────────────────────────────────────────────────────

    def _get_texture_for_bar(
        self, control: PhraseControlIR, bar_offset: int
    ) -> Tuple[str, str, int]:
        """Get (rh_texture, lh_texture, density_target) for a bar offset."""
        if control.texture_program.bars and bar_offset < len(control.texture_program.bars):
            tp = control.texture_program.bars[bar_offset]
            return (tp.rh_texture, tp.lh_texture, tp.rh_density_target)
        return ("singing_melody", "alberti", 8)

    def _cells_for_range(
        self, control: PhraseControlIR, bar_s: int, beat_s: float, bar_e: int, beat_e: float
    ) -> List[HarmonicCell]:
        """Get harmonic cells active in a bar range."""
        result = []
        for cell in control.harmonic_cells:
            if bar_s <= cell.bar <= bar_e:
                result.append(cell)
        return result

    def _apply_dynamics(self, bundles: List[OnsetBundle], control: PhraseControlIR) -> None:
        """Apply dynamics from dynamic_shape DynamicEvent list."""
        if not control.dynamic_shape:
            return
        bar_dynamics: Dict[int, str] = {}
        for de in control.dynamic_shape:
            if hasattr(de, "bar") and hasattr(de, "level"):
                bar_dynamics[de.bar] = de.level
        for bundle in bundles:
            dyn = bar_dynamics.get(bundle.bar)
            if dyn and bundle.beat <= 1.5:
                for event in bundle.events:
                    if event.dynamic is None:
                        event.dynamic = dyn

    def _apply_breathing(
        self,
        bundles: List[OnsetBundle],
        breathing_rules: List,
        control: PhraseControlIR,
        trace: ContextTrace,
    ) -> None:
        """Apply breathing rules by inserting rest bundles."""
        for rule in breathing_rules:
            placement = getattr(rule, "placement", "")
            if "before" in placement.lower():
                mid_bar = control.bar_start + control.bars // 2
                mid_beat = bar_duration(control.meter) + 0.5
            elif "after" in placement.lower():
                mid_bar = control.bar_start + control.bars - 1
                mid_beat = bar_duration(control.meter)
            else:
                mid_bar = control.bar_start + control.bars // 2
                mid_beat = 1.0
            rest_bundle = OnsetBundle(bar=mid_bar, beat=mid_beat)
            rest_bundle.events.append(
                OnsetEvent(
                    voice="soprano",
                    pitch="rest",
                    duration="e",
                    role=NoteRole.STRUCTURAL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.FORM.value],
                    ),
                )
            )
            bundles.append(rest_bundle)
            trace.breathing_rules_applied.append(getattr(rule, "type", ""))

    def _index_voicings(self, voicings: List[Dict]) -> Dict[int, Dict]:
        """Index voicings by bar number."""
        result: Dict[int, Dict] = {}
        for v in voicings:
            bar = v.get("bar", 0)
            if bar not in result:
                result[bar] = v
        return result


# ─── Internal tagged event (carries bar/beat for grouping) ────────────────


@dataclass
class _TaggedEvent:
    """Internal event carrying bar/beat position + voice + pitch + metadata."""

    _bar: int = 1
    _beat: float = 1.0
    voice: str = "soprano"
    pitch: str = "C4"
    duration: str = "q"
    role: str = NoteRole.STRUCTURAL.value
    dynamic: Optional[str] = None
    articulation: Optional[str] = None
    ornament: Optional[str] = None
    tie: Optional[str] = None
    expression: Optional[str] = None
    justification: OnsetJustification = field(default_factory=OnsetJustification)

    def __init__(self, bar: int = 1, beat: float = 1.0, **kwargs):
        self._bar = bar
        self._beat = beat
        for k, v in kwargs.items():
            if k == "justification" and v is None:
                v = OnsetJustification()
            setattr(self, k, v)
        if not hasattr(self, "justification") or self.justification is None:
            self.justification = OnsetJustification()
