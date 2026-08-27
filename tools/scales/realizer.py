"""
Realizer — style-conditioned realization: SketchIR → LayerIR.

Takes an abstract sketch (melody/bass anchors, harmonic rhythm, texture intent)
and realizes it into a full LayerIR with note-level detail using corpus
retrieval and idiomatic gesture expansion.

The realizer is NOT an LLM — it is a programmatic engine that uses
retrieved gestures and patterns to fill in surface detail.
"""

from __future__ import annotations

from fractions import Fraction

from .cadence_bank import CadenceBank
from .duration import bar_duration, dur_to_beats, largest_dur_at_most
from .enums import AccompType, CadenceTarget, NoteRole
from .gesture_bank import GestureBank
from .models import (
    Anchor,
    CadenceQuery,
    GestureQuery,
    HarmonyEvent,
    LayerEvent,
    LayerIR,
    MotifObject,
    PhraseSlot,
    SketchIR,
    StyleDNA,
    TextureIntent,
)
from .motif_realization import emit_motif_melody_events, first_scale_degree_midi
from .pitch import (
    build_scale,
    chord_tones,
    is_minor_key,
    key_to_root_midi,
    midi_to_pitch,
    pitch_to_midi,
    snap_to_scale,
)


class Realizer:
    """Style-conditioned realization engine.

    Transforms SketchIR into LayerIR by:
    1. Realizing melody anchors into a principal line
    2. Realizing bass anchors into a bass foundation
    3. Filling response layer (accompaniment patterns) from gestures
    4. Optionally adding counter reply and ornamental surface
    """

    def __init__(
        self,
        gesture_bank: GestureBank,
        cadence_bank: CadenceBank,
        motif_bank: dict[str, MotifObject] | None = None,
    ):
        self.gesture_bank = gesture_bank
        self.cadence_bank = cadence_bank
        self.motif_bank = motif_bank or {}

    def realize(
        self,
        sketch: SketchIR,
        slot: PhraseSlot,
        style_dna: StyleDNA,
        n: int = 4,
        motif_bank: dict[str, MotifObject] | None = None,
    ) -> list[LayerIR]:
        """Generate N realization candidates from a sketch."""
        candidates = []
        mb = motif_bank if motif_bank is not None else self.motif_bank
        for realization_idx in range(n):
            layer = self._realize_one(sketch, slot, style_dna, realization_idx, mb)
            candidates.append(layer)
        return candidates

    def _realize_one(
        self,
        sketch: SketchIR,
        slot: PhraseSlot,
        style_dna: StyleDNA,
        realization_idx: int,
        motif_bank: dict[str, MotifObject],
    ) -> LayerIR:
        """Generate one realization variant."""
        layer = LayerIR(
            phrase_id=sketch.phrase_id,
            instrumentation="solo_piano",
            key=slot.key,
            meter=slot.meter,
            bar_count=slot.bar_count,
        )

        # Build scale for this key
        root = key_to_root_midi(slot.key)
        mode = "minor" if is_minor_key(slot.key) else "major"
        scale = build_scale(root + 60, mode)  # centered around C4

        # 1. Principal line (from melody anchors + motif placements)
        layer.principal_line = self._realize_principal_line(
            sketch,
            slot,
            scale,
            realization_idx,
            motif_bank,
        )

        # 2. Bass foundation (from bass anchors + harmony)
        layer.bass_foundation = self._realize_bass_foundation(sketch, slot, scale, realization_idx)

        # 3. Response layer (accompaniment from texture intent)
        layer.response_layer = self._realize_response_layer(
            sketch, slot, scale, style_dna, realization_idx
        )

        # 4. Counter reply (inner voice on every realization)
        if slot.bar_count >= 4:
            layer.counter_reply = self._realize_counter_reply(sketch, slot, scale, realization_idx)

        # 5. Ornamental surface (always include for complex pieces)
        layer.ornamental_surface = self._realize_ornamental(sketch, slot, scale)

        return layer

    # ─── Principal Line ───────────────────────────────────────────────────

    def _realize_principal_line(
        self,
        sketch: SketchIR,
        slot: PhraseSlot,
        scale: list[int],
        variant: int,
        motif_bank: dict[str, MotifObject],
    ) -> list[LayerEvent]:
        """Realize melody from anchors into a full melodic line."""
        events = []
        anchors = sorted(sketch.melody_anchors, key=lambda a: (a.bar, a.beat))

        if not anchors:
            return self._motif_only_principal_line(sketch, slot, scale, motif_bank)

        beats_per_bar = bar_duration(slot.meter)

        for i, anchor in enumerate(anchors):
            # Resolve pitch
            pitch = self._resolve_anchor_pitch(anchor, slot.key, scale)
            if pitch is None:
                continue

            # Determine duration based on distance to next anchor
            if i < len(anchors) - 1:
                next_anchor = anchors[i + 1]
                beats_to_next = (next_anchor.bar - anchor.bar) * beats_per_bar + (
                    next_anchor.beat - anchor.beat
                )
                dur = _choose_melody_duration(beats_to_next, variant)
            else:
                # The LAST note of the phrase, with nothing after it to bound
                # its length — so it runs to the end of its bar. A hardcoded
                # half note left every cadence bar exactly half empty: two
                # beats of a 4/4, then two beats of silence in both hands,
                # in every phrase.
                #
                # Falsified against the corpus rather than guessed. Cadential
                # bars in real music are a median 100% sounding (Chopin,
                # Beethoven, Bach, Haydn) and 75% in Mozart, with only 16-33%
                # at or below half full — against 50%, uniformly, here.
                # This IS the cadence — it is the final anchor of the phrase,
                # by construction, with nothing after it to bound its length.
                #
                # The test was `anchor.role == "cadence"`, and `sketch_proposer`
                # emits only "passing" and "structural". That branch had never
                # once executed: every phrase ended on a QUARTER NOTE and left
                # its bar three-quarters empty, while the code read as though
                # cadences were being given long notes.
                remaining = beats_per_bar - (anchor.beat - 1)
                dur = largest_dur_at_most(remaining) if remaining > 0 else "q"

            events.append(
                LayerEvent(
                    bar=anchor.bar,
                    beat=anchor.beat,
                    pitch=midi_to_pitch(pitch, slot.key),
                    duration=dur,
                    role=NoteRole.STRUCTURAL.value,
                    dynamic=self._dynamic_at(sketch, anchor.bar, anchor.beat),
                    source_layer="principal_line",
                )
            )

            # Add passing tones between anchors
            if i < len(anchors) - 1 and variant >= 1:
                next_pitch = self._resolve_anchor_pitch(anchors[i + 1], slot.key, scale)
                if next_pitch and abs(next_pitch - pitch) > 2:
                    passing = self._generate_passing_tones(
                        pitch,
                        next_pitch,
                        anchor.bar,
                        anchor.beat,
                        beats_to_next,
                        scale,
                        slot.key,
                        slot.meter,
                    )
                    events.extend(passing)

        self._inject_motif_placements(
            events,
            sketch,
            slot,
            scale,
            motif_bank,
            beats_per_bar,
            anchors,
        )
        events.sort(key=lambda e: (e.bar, e.beat))
        return events

    def _motif_only_principal_line(
        self,
        sketch: SketchIR,
        slot: PhraseSlot,
        scale: list[int],
        motif_bank: dict[str, MotifObject],
    ) -> list[LayerEvent]:
        """When there are no anchors, still realize motif placements if any."""
        out: list[LayerEvent] = []
        bpb = bar_duration(slot.meter)
        for mp in sketch.motif_placements or []:
            if mp.voice not in ("melody", "soprano", ""):
                continue
            motif = motif_bank.get(mp.motif_id)
            if not motif or not motif.rhythm_cell:
                continue
            sm = key_to_root_midi(slot.key) + 60
            fsd = first_scale_degree_midi(motif, scale)
            if fsd is not None:
                sm = fsd
            for r in emit_motif_melody_events(
                motif,
                mp,
                slot.key,
                scale,
                int(sm),
                bpb,
            ):
                out.append(
                    LayerEvent(
                        bar=r["bar"],
                        beat=r["beat"],
                        pitch=r["pitch"],
                        duration=r["duration"],
                        role=r["role"],
                        dynamic=self._dynamic_at(sketch, r["bar"], r["beat"]),
                        source_layer="principal_line",
                    )
                )
        return out

    def _inject_motif_placements(
        self,
        events: list[LayerEvent],
        sketch: SketchIR,
        slot: PhraseSlot,
        scale: list[int],
        motif_bank: dict[str, MotifObject],
        beats_per_bar: float,
        anchors: list[Anchor],
    ) -> None:
        """Append LayerEvents from motif_placements (mutates events)."""
        for mp in sketch.motif_placements or []:
            if mp.voice not in ("melody", "soprano", ""):
                continue
            motif = motif_bank.get(mp.motif_id)
            if not motif or not motif.rhythm_cell:
                continue
            anchor = next((a for a in anchors if a.bar == mp.bar), None)
            start_m = self._resolve_anchor_pitch(anchor, slot.key, scale) if anchor else None
            if start_m is None:
                start_m = key_to_root_midi(slot.key) + 60
            fsd = first_scale_degree_midi(motif, scale)
            if fsd is not None:
                start_m = fsd
            for r in emit_motif_melody_events(
                motif,
                mp,
                slot.key,
                scale,
                int(start_m),
                beats_per_bar,
            ):
                events.append(
                    LayerEvent(
                        bar=r["bar"],
                        beat=r["beat"],
                        pitch=r["pitch"],
                        duration=r["duration"],
                        role=r["role"],
                        dynamic=self._dynamic_at(sketch, r["bar"], r["beat"]),
                        source_layer="principal_line",
                    )
                )

    # ─── Bass Foundation ──────────────────────────────────────────────────

    def _realize_bass_foundation(
        self, sketch: SketchIR, slot: PhraseSlot, scale: list[int], variant: int
    ) -> list[LayerEvent]:
        """Realize bass from anchors and harmony."""
        events = []
        bass_register = scale[: len(scale) // 3]  # lower third of scale

        for harmony in sketch.harmonic_rhythm:
            # Get bass pitch from harmony
            bass_pitch = self._harmony_to_bass(harmony, bass_register, slot.key)
            if bass_pitch is None:
                continue

            # Duration varies by variant
            dur = ["h", "q", "dq"][variant % 3]

            events.append(
                LayerEvent(
                    bar=harmony.bar,
                    beat=harmony.beat,
                    pitch=midi_to_pitch(bass_pitch, slot.key),
                    duration=dur,
                    role=NoteRole.STRUCTURAL.value,
                    source_layer="bass_foundation",
                )
            )

        return events

    # ─── Response Layer ───────────────────────────────────────────────────

    def _realize_response_layer(
        self,
        sketch: SketchIR,
        slot: PhraseSlot,
        scale: list[int],
        style_dna: StyleDNA,
        variant: int,
    ) -> list[LayerEvent]:
        """Realize accompaniment pattern from texture intent.

        Tries gesture-based accompaniment first via GestureBank; falls
        back to hardcoded pattern generation if no gesture is found.
        At cadence zones, overlays CadenceBank chord sequences on the
        last 1-2 bars.
        """
        events = []
        beats_per_bar = bar_duration(slot.meter)

        for tex_intent in sketch.texture_plan:
            bar = tex_intent.bar
            lh_type = tex_intent.lh_type

            # Get harmony for this bar
            harmony = self._get_harmony_at(sketch, bar)
            if harmony is None:
                continue

            # Build chord for this bar
            root = key_to_root_midi(harmony.key) + 36  # bass octave
            # Determine quality from Roman numeral
            quality = _roman_to_quality(harmony.roman)
            tones = chord_tones(root, quality)

            # --- Try gesture-based accompaniment first ---
            gesture_events = self._try_gesture_accompaniment(
                tex_intent, bar, beats_per_bar, tones, slot.key, variant
            )
            if gesture_events:
                events.extend(gesture_events)
                continue

            # --- Fallback: hardcoded pattern generation ---
            bar_events = self._generate_lh_pattern(
                lh_type, tones, bar, beats_per_bar, scale, slot.key, variant
            )
            events.extend(bar_events)

        # --- CadenceBank overlay at cadence zones ---
        cadence_events = self._apply_cadence_bank(sketch, slot, scale)
        if cadence_events:
            events.extend(cadence_events)

        return events

    def _try_gesture_accompaniment(
        self,
        tex_intent: TextureIntent,
        bar: int,
        beats_per_bar: float,
        tones: list[int],
        key: str,
        variant: int,
    ) -> list[LayerEvent]:
        """Try to retrieve a gesture for this bar's texture and convert to events.

        Returns events if a gesture is found, empty list otherwise.
        """
        try:
            query = GestureQuery(
                texture_lh=tex_intent.lh_type,
                texture_rh=tex_intent.rh_type,
                min_span_beats=beats_per_bar,
                max_span_beats=beats_per_bar * 2,
                n=1,
            )
            results = self.gesture_bank.retrieve(query)
            if not results:
                return []

            gesture = results[0]
            events = []
            # Use the gesture's dur_profile to generate events
            if gesture.dur_profile and tones:
                # Exact, because a gesture profile can contain tuplets: a float
                # cursor advanced by 1/3 drifts, and the drift arrives
                # downstream as an onset the notation cannot express.
                beat = Fraction(1)
                for j, dur_str in enumerate(gesture.dur_profile):
                    if beat > beats_per_bar:
                        break
                    tone = tones[j % len(tones)]
                    role = NoteRole.ARPEGGIATED_FILL.value if j > 0 else NoteRole.STRUCTURAL.value
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=float(beat),
                            pitch=midi_to_pitch(tone, key),
                            duration=dur_str,
                            role=role,
                            source_layer="response_layer",
                        )
                    )
                    beat += dur_to_beats(dur_str)
            return events
        except Exception:
            return []

    def _apply_cadence_bank(
        self, sketch: SketchIR, slot: PhraseSlot, scale: list[int]
    ) -> list[LayerEvent]:
        """If the phrase has a cadence target, query CadenceBank and override
        the last 1-2 bars of the response layer with the cadence chord sequence.
        """
        if not slot.cadence_target or slot.cadence_target == CadenceTarget.NONE.value:
            return []

        try:
            key_mode = "minor" if is_minor_key(slot.key) else "major"
            query = CadenceQuery(
                cadence_type=slot.cadence_target,
                key=slot.key,
                mode=key_mode,
                approach_length_bars=2,
                n=1,
            )
            results = self.cadence_bank.retrieve(query)
            if not results:
                return []

            cadence = results[0]
            if not cadence.chord_sequence:
                return []

            events = []
            arrival_bar = slot.cadence_bar or (slot.bar_start + slot.bar_count - 1)
            approach_bars = len(cadence.chord_sequence)
            start_bar = max(slot.bar_start, arrival_bar - approach_bars + 1)

            root_midi = key_to_root_midi(slot.key) + 36  # bass octave

            for i, roman in enumerate(cadence.chord_sequence):
                bar = start_bar + i
                if bar > arrival_bar:
                    break
                quality = _roman_to_quality(roman)
                degree_offset = _roman_to_bass_offset(roman)
                bass_pitch = root_midi + degree_offset
                tones = chord_tones(bass_pitch, quality)
                if not tones:
                    continue
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=1.0,
                        pitch=midi_to_pitch(tones[0], slot.key),
                        duration="h",
                        role=NoteRole.STRUCTURAL.value,
                        source_layer="response_layer",
                    )
                )
            return events
        except Exception:
            return []

    # ─── Counter Reply ────────────────────────────────────────────────────

    def _realize_counter_reply(
        self, sketch: SketchIR, slot: PhraseSlot, scale: list[int], variant: int
    ) -> list[LayerEvent]:
        """Inner counter-melody — chord tones in middle register, every bar."""
        events = []
        for bar_offset in range(slot.bar_count):
            bar = slot.bar_start + bar_offset
            harmony = self._get_harmony_at(sketch, bar)
            if not harmony:
                continue

            root = key_to_root_midi(harmony.key) + 60  # middle register
            quality = _roman_to_quality(harmony.roman)
            tones = chord_tones(root, quality)
            if len(tones) < 2:
                continue

            # Choose inner voice pitch (3rd or 5th of chord)
            tone_idx = 1 if bar_offset % 2 == 0 else min(2, len(tones) - 1)
            pitch = tones[tone_idx]

            # Rhythmic variety: half notes with occasional quarters
            if bar_offset % 3 == 0 and variant % 2 == 0:
                # Two quarter notes
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=1.0,
                        pitch=midi_to_pitch(pitch, slot.key),
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        source_layer="counter_reply",
                    )
                )
                if len(tones) >= 3:
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=3.0,
                            pitch=midi_to_pitch(tones[2 if tone_idx != 2 else 1], slot.key),
                            duration="q",
                            role=NoteRole.STRUCTURAL.value,
                            source_layer="counter_reply",
                        )
                    )
            else:
                # Held half note
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=1.0,
                        pitch=midi_to_pitch(pitch, slot.key),
                        duration="h",
                        role=NoteRole.STRUCTURAL.value,
                        source_layer="counter_reply",
                    )
                )

        return events

    # ─── Ornamental Surface ──────────────────────────────────────────────

    def _realize_ornamental(
        self, sketch: SketchIR, slot: PhraseSlot, scale: list[int]
    ) -> list[LayerEvent]:
        """Ornamental figuration — turns, neighbor tones, arpeggiated fills."""
        events = []
        bar_duration(slot.meter)

        for bar_offset in range(slot.bar_count):
            bar = slot.bar_start + bar_offset
            harmony = self._get_harmony_at(sketch, bar)
            if not harmony:
                continue

            root = key_to_root_midi(harmony.key) + 72  # high register
            quality = _roman_to_quality(harmony.roman)
            tones = chord_tones(root, quality)

            # Every other bar: add sixteenth-note figuration on beat 2 or 4
            if bar_offset % 2 == 0 and tones:
                beat = 2.0 if bar_offset % 4 == 0 else 4.0
                for j, t in enumerate(tones[:3]):
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=beat + j * 0.25,
                            pitch=midi_to_pitch(t, slot.key),
                            duration="s",
                            role=NoteRole.ORNAMENTAL.value,
                            source_layer="ornamental_surface",
                        )
                    )

            # Neighbor tone figure at phrase midpoints and cadence approach
            if bar_offset == slot.bar_count // 2 - 1 or bar_offset == slot.bar_count - 2:
                if tones:
                    main = tones[0]
                    upper = snap_to_scale(main + 1, scale) if scale else main + 1
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=3.5,
                            pitch=midi_to_pitch(upper, slot.key),
                            duration="s",
                            role=NoteRole.NEIGHBOR.value,
                            ornament="turn",
                            source_layer="ornamental_surface",
                        )
                    )
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=3.75,
                            pitch=midi_to_pitch(main, slot.key),
                            duration="s",
                            role=NoteRole.ORNAMENTAL.value,
                            source_layer="ornamental_surface",
                        )
                    )

        return events

    # ─── Pattern Generators ───────────────────────────────────────────────

    def _generate_lh_pattern(
        self,
        lh_type: str,
        tones: list[int],
        bar: int,
        beats: float,
        scale: list[int],
        key: str,
        variant: int,
    ) -> list[LayerEvent]:
        """Generate LH accompaniment events for one bar."""
        events = []

        if lh_type == AccompType.ALBERTI.value and len(tones) >= 3:
            # Root-5th-3rd-5th pattern in sixteenths
            pattern = [tones[0], tones[2], tones[1], tones[2]]
            beat = 1.0
            for _ in range(int(beats)):
                for p in pattern:
                    events.append(
                        LayerEvent(
                            bar=bar,
                            beat=beat,
                            pitch=midi_to_pitch(p, key),
                            duration="s",
                            role=NoteRole.ARPEGGIATED_FILL.value,
                            source_layer="response_layer",
                        )
                    )
                    beat += 0.25

        elif lh_type == AccompType.BASS_MELODY.value:
            # Contrapuntal bass — quarter notes on chord tones
            beat = 1.0
            for i in range(int(beats)):
                p = tones[i % len(tones)]
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=beat,
                        pitch=midi_to_pitch(p, key),
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        source_layer="response_layer",
                    )
                )
                beat += 1.0

        elif lh_type == AccompType.BLOCK_CHORD_SPARSE.value:
            # Block chord on beat 1
            chord_pitches = [midi_to_pitch(t, key) for t in tones[:3]]
            events.append(
                LayerEvent(
                    bar=bar,
                    beat=1.0,
                    pitch=chord_pitches,
                    duration="h",
                    role=NoteRole.STRUCTURAL.value,
                    source_layer="response_layer",
                )
            )

        elif lh_type == AccompType.BROKEN_CHORD_WAVE.value and tones:
            # Ascending broken chord
            beat = 1.0
            for t in tones[: int(beats * 2)]:
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=beat,
                        pitch=midi_to_pitch(t, key),
                        duration="e",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        source_layer="response_layer",
                    )
                )
                beat += 0.5

        elif lh_type == AccompType.PEDAL_POINT.value and tones:
            # Held bass note
            events.append(
                LayerEvent(
                    bar=bar,
                    beat=1.0,
                    pitch=midi_to_pitch(tones[0], key),
                    duration="w",
                    role=NoteRole.PEDAL_SUPPORT.value,
                    source_layer="response_layer",
                )
            )

        elif lh_type == AccompType.WALKING_BASS.value:
            # Quarter-note walking bass on scale tones
            beat = 1.0
            base = tones[0] if tones else 48
            for i in range(int(beats)):
                p = snap_to_scale(base + i, scale) if scale else base + i
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=beat,
                        pitch=midi_to_pitch(p, key),
                        duration="q",
                        role=NoteRole.PASSING.value,
                        source_layer="response_layer",
                    )
                )
                beat += 1.0

        elif lh_type == AccompType.SILENCE.value:
            events.append(
                LayerEvent(
                    bar=bar,
                    beat=1.0,
                    pitch="rest",
                    duration="w",
                    role=NoteRole.STRUCTURAL.value,
                    source_layer="response_layer",
                )
            )

        else:
            # Default: simple chord on beat 1
            if tones:
                events.append(
                    LayerEvent(
                        bar=bar,
                        beat=1.0,
                        pitch=midi_to_pitch(tones[0], key),
                        duration="h",
                        role=NoteRole.STRUCTURAL.value,
                        source_layer="response_layer",
                    )
                )

        return events

    def _generate_passing_tones(
        self,
        from_midi: int,
        to_midi: int,
        bar: int,
        beat: float,
        beats_available: float,
        scale: list[int],
        key: str,
        meter: tuple[int, int],
    ) -> list[LayerEvent]:
        """Generate passing tones between two melody anchors."""
        events = []
        direction = 1 if to_midi > from_midi else -1
        current = from_midi + direction

        beat_pos = beat + dur_to_beats("q")
        remaining = beats_available - dur_to_beats("q") * 2  # leave room for arrival

        while remaining > 0.25 and abs(current - to_midi) > 1:
            snapped = snap_to_scale(current, scale)
            events.append(
                LayerEvent(
                    bar=bar,
                    beat=beat_pos,
                    pitch=midi_to_pitch(snapped, key),
                    duration="e",
                    role=NoteRole.PASSING.value,
                    source_layer="principal_line",
                )
            )
            current += direction * 2
            beat_pos += 0.5
            remaining -= 0.5

            # Wrap to next bar if needed
            beats_per_bar = bar_duration(meter)
            if beat_pos > beats_per_bar:
                bar += 1
                beat_pos -= beats_per_bar

        return events

    # ─── Helpers ──────────────────────────────────────────────────────────

    def _resolve_anchor_pitch(self, anchor: Anchor, key: str, scale: list[int]) -> int | None:
        """Resolve an anchor's pitch_or_degree to a MIDI value."""
        p = anchor.pitch_or_degree
        if not p:
            return None

        # If it's a concrete pitch like "C5"
        midi = pitch_to_midi(p)
        if midi is not None:
            return midi

        # If it's a scale degree like "^5"
        if p.startswith("^"):
            try:
                degree = int(p[1:])
                root = key_to_root_midi(key) + 60  # octave 4
                mode = "minor" if is_minor_key(key) else "major"
                intervals = {
                    1: 0,
                    2: 2,
                    3: 4 if mode == "major" else 3,
                    4: 5,
                    5: 7,
                    6: 9 if mode == "major" else 8,
                    7: 11,
                }
                return root + intervals.get(degree, 0)
            except ValueError:
                return None

        return None

    def _harmony_to_bass(
        self, harmony: HarmonyEvent, bass_register: list[int], key: str
    ) -> int | None:
        """The bass note of this harmony — the chord tone the INVERSION puts there.

        This kept its own Roman-numeral table: nineteen entries mapping a symbol
        to a scale degree, with everything unlisted falling through to `0`, the
        root. So every first and second inversion was silently played in root
        position — `i6` in G minor put G in the bass where the notation says B
        flat, and then a scale snap moved it to B NATURAL, a note outside the
        key, sounding against the melody's B flat.

        `harmony_analysis` is this project's one Roman parser and already covers
        every degree, quality and inversion; `roman_pitches` returns the pitch
        classes BASS FIRST. There is no second table to maintain.
        """
        from .harmony_analysis import roman_pitches
        from .pitch import is_minor_key

        roman = harmony.roman.strip()
        tonic_pc = key_to_root_midi(key) % 12
        mode = "minor" if is_minor_key(key) else "major"
        pcs = roman_pitches(roman, tonic_pc, mode)
        if not pcs:
            # An unparseable symbol is the tonic, as before — but now that is a
            # deliberate fallback rather than the answer for two thirds of the
            # inversions in common use.
            pcs = [tonic_pc]

        # Place that pitch class in the bass octave, then keep it: snapping a
        # chord tone to a scale is what turned the B flat into a B natural.
        #
        # The floor is the tonic in the octave this always used (`root + 36`, so
        # G2 in G minor), and the chord tone is taken AT OR ABOVE it — a bass
        # that drops below the tonic for an inversion is a different register,
        # not a different note.
        bass_pc = pcs[0]
        octave_floor = key_to_root_midi(key) + 36
        target = octave_floor + ((bass_pc - octave_floor) % 12)
        if bass_register:
            lo, hi = min(bass_register), max(bass_register)
            while target < lo - 12:
                target += 12
            while target > hi + 12:
                target -= 12
        return target

    def _get_harmony_at(self, sketch: SketchIR, bar: int) -> HarmonyEvent | None:
        """Get the harmony event at or before a given bar."""
        result = None
        for h in sketch.harmonic_rhythm:
            if h.bar <= bar:
                result = h
            elif h.bar > bar:
                break
        return result

    def _dynamic_at(self, sketch: SketchIR, bar: int, beat: float) -> str | None:
        """Get dynamic level at a position."""
        for d in reversed(sketch.dynamic_shape):
            if d.bar < bar or (d.bar == bar and d.beat <= beat):
                return d.level
        return None


# ─── Module Helpers ──────────────────────────────────────────────────────────


def _roman_to_quality(roman: str) -> str:
    """Determine chord quality from Roman numeral."""
    r = roman.strip()
    if r in ("I", "IV", "V", "V7", "II", "III", "VI", "VII", "I64"):
        return "major"
    if r in ("i", "ii", "iii", "iv", "v", "vi"):
        return "minor"
    if "dim" in r or "o" in r:
        return "dim"
    if r[0].isupper():
        return "major"
    return "minor"


def _roman_to_bass_offset(roman: str) -> int:
    """Map Roman numeral to semitone offset from key root for bass note."""
    mapping = {
        "I": 0,
        "i": 0,
        "II": 2,
        "ii": 2,
        "ii6": 5,
        "III": 4,
        "iii": 4,
        "IV": 5,
        "iv": 5,
        "V": 7,
        "v": 7,
        "V7": 7,
        "VI": 9,
        "vi": 9,
        "VII": 11,
        "vii": 11,
        "viio": 11,
        "I64": 7,
        "bII": 1,
        "bII6": 1,
        "bIII": 3,
        "bVI": 8,
        "bVII": 10,
        "It6": 8,
    }
    return mapping.get(roman.strip(), 0)


def _choose_melody_duration(beats_to_next: float, variant: int) -> str:
    """Choose a melodic note duration based on available space."""
    if beats_to_next >= 4.0:
        return ["h", "dq", "q"][variant % 3]
    if beats_to_next >= 2.0:
        return ["q", "dq", "h"][variant % 3]
    if beats_to_next >= 1.0:
        return "q"
    return "e"
