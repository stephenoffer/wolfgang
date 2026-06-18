"""
Reducer — reduce a realized surface back to a skeleton for round-trip comparison.

This is THE key quality mechanism in SCALES. Every realized surface is
reduced back to structural tones and compared to the intended sketch.
If the ornate output no longer says the same musical thing, it gets
penalized heavily.
"""

from __future__ import annotations

from typing import Dict, List

from .enums import NoteRole
from .models import (
    Anchor,
    CadenceApproach,
    EntryExitState,
    HarmonyEvent,
    LayerEvent,
    LayerIR,
    SketchIR,
    TextureIntent,
)
from .pitch import pitch_to_midi


class Reducer:
    """Reduces LayerIR back to SketchIR for round-trip verification."""

    def reduce(self, surface: LayerIR) -> SketchIR:
        """Strip realized surface to structural skeleton."""
        sketch = SketchIR(phrase_id=surface.phrase_id)

        # 1. Extract melody anchors from principal_line
        sketch.melody_anchors = self._extract_melody_anchors(surface.principal_line)

        # 2. Extract bass anchors from bass_foundation
        sketch.bass_anchors = self._extract_bass_anchors(surface.bass_foundation)

        # 3. Infer harmonic rhythm from structural tones
        sketch.harmonic_rhythm = self._infer_harmony(surface)

        # 4. Extract texture plan from response layer
        sketch.texture_plan = self._extract_texture_plan(surface)

        # 5. Extract entry/exit signatures
        sketch.entry_signature = self._extract_entry(surface)
        sketch.exit_signature = self._extract_exit(surface)

        return sketch

    def compare(self, original: SketchIR, reduced: SketchIR) -> float:
        """Compare original sketch to reduced skeleton. Returns 0-1 fidelity."""
        scores = []

        # Melody anchor similarity (0.25)
        scores.append(
            (0.25, self._anchor_similarity(original.melody_anchors, reduced.melody_anchors))
        )

        # Bass anchor similarity (0.20)
        scores.append((0.20, self._anchor_similarity(original.bass_anchors, reduced.bass_anchors)))

        # Harmonic grid similarity (0.20)
        scores.append(
            (0.20, self._harmony_similarity(original.harmonic_rhythm, reduced.harmonic_rhythm))
        )

        # Cadence fidelity (0.20)
        scores.append((0.20, self._cadence_fidelity(original.cadence, reduced)))

        # Motif placement fidelity (0.15)
        scores.append(
            (0.15, self._motif_fidelity(original.motif_placements, reduced.melody_anchors))
        )

        total_weight = sum(w for w, _ in scores)
        total_score = sum(w * s for w, s in scores)
        return total_score / total_weight if total_weight > 0 else 0.0

    # ─── Extraction ───────────────────────────────────────────────────────

    def _extract_melody_anchors(self, events: List[LayerEvent]) -> List[Anchor]:
        """Extract structural melody anchors from principal line."""
        anchors = []
        for event in events:
            if event.pitch == "rest":
                continue
            if event.role in (
                NoteRole.STRUCTURAL.value,
                "structural",
                "peak",
                "cadence",
                "entry",
                "exit",
            ):
                anchors.append(
                    Anchor(
                        bar=event.bar,
                        beat=event.beat,
                        pitch_or_degree=event.pitch
                        if isinstance(event.pitch, str)
                        else str(event.pitch),
                        weight=1.0,
                        role=event.role,
                    )
                )
        return anchors

    def _extract_bass_anchors(self, events: List[LayerEvent]) -> List[Anchor]:
        """Extract structural bass anchors."""
        anchors = []
        seen_bars = set()
        for event in events:
            if event.pitch == "rest":
                continue
            # Take first structural event per bar
            if event.bar not in seen_bars and event.role in (
                NoteRole.STRUCTURAL.value,
                "structural",
            ):
                seen_bars.add(event.bar)
                anchors.append(
                    Anchor(
                        bar=event.bar,
                        beat=event.beat,
                        pitch_or_degree=event.pitch
                        if isinstance(event.pitch, str)
                        else str(event.pitch),
                        weight=0.8,
                        role="structural",
                    )
                )
        return anchors

    def _infer_harmony(self, surface: LayerIR) -> List[HarmonyEvent]:
        """Infer harmonic rhythm from all structural tones."""
        events = []
        # Group all structural tones by bar
        bar_tones: Dict[int, List[int]] = {}
        for layer_events in [
            surface.principal_line,
            surface.bass_foundation,
            surface.response_layer,
            surface.counter_reply,
        ]:
            for event in layer_events:
                if event.pitch == "rest" or event.role == NoteRole.PASSING.value:
                    continue
                midi = pitch_to_midi(event.pitch)
                if midi is not None:
                    bar_tones.setdefault(event.bar, []).append(midi)

        for bar, tones in sorted(bar_tones.items()):
            # Simple: use lowest tone as root indicator
            if tones:
                events.append(
                    HarmonyEvent(
                        bar=bar,
                        beat=1.0,
                        roman="?",  # We don't need exact Roman numeral for comparison
                        key=surface.key,
                    )
                )
        return events

    def _extract_texture_plan(self, surface: LayerIR) -> List[TextureIntent]:
        """Infer texture type from response layer density."""
        plan = []
        # Group response events by bar and count
        bar_counts: Dict[int, int] = {}
        for event in surface.response_layer:
            bar_counts[event.bar] = bar_counts.get(event.bar, 0) + 1

        for bar, count in sorted(bar_counts.items()):
            # Heuristic texture classification from density
            if count >= 12:
                lh_type = "alberti"
            elif count >= 6:
                lh_type = "broken_chord_wave"
            elif count >= 3:
                lh_type = "bass_melody"
            elif count >= 1:
                lh_type = "block_chord_sparse"
            else:
                lh_type = "silence"

            plan.append(
                TextureIntent(
                    bar=bar,
                    rh_type="",
                    lh_type=lh_type,
                    density_target=count,
                )
            )
        return plan

    def _extract_entry(self, surface: LayerIR) -> EntryExitState:
        """Extract entry state from first events."""
        first_melody = surface.principal_line[0] if surface.principal_line else None
        surface.bass_foundation[0] if surface.bass_foundation else None
        return EntryExitState(
            pitch=first_melody.pitch if first_melody else None,
            dynamic=first_melody.dynamic if first_melody else None,
        )

    def _extract_exit(self, surface: LayerIR) -> EntryExitState:
        """Extract exit state from last events."""
        last_melody = surface.principal_line[-1] if surface.principal_line else None
        surface.bass_foundation[-1] if surface.bass_foundation else None
        return EntryExitState(
            pitch=last_melody.pitch if last_melody else None,
            dynamic=last_melody.dynamic if last_melody else None,
        )

    # ─── Comparison ───────────────────────────────────────────────────────

    def _anchor_similarity(self, original: List[Anchor], reduced: List[Anchor]) -> float:
        """Compare two sets of anchors. Returns 0-1."""
        if not original:
            return 1.0 if not reduced else 0.5
        if not reduced:
            return 0.0

        # Match anchors by bar proximity
        matched = 0
        used = set()
        for orig in original:
            best_match = None
            best_dist = float("inf")
            for j, red in enumerate(reduced):
                if j in used:
                    continue
                bar_dist = abs(orig.bar - red.bar)
                if bar_dist < best_dist:
                    best_dist = bar_dist
                    best_match = j
            if best_match is not None and best_dist <= 1:
                used.add(best_match)
                # Check pitch proximity
                orig_midi = pitch_to_midi(orig.pitch_or_degree)
                red_midi = pitch_to_midi(reduced[best_match].pitch_or_degree)
                if orig_midi and red_midi:
                    pitch_dist = abs(orig_midi - red_midi)
                    if pitch_dist <= 2:
                        matched += 1.0
                    elif pitch_dist <= 5:
                        matched += 0.5
                else:
                    matched += 0.5  # Can't compare degrees vs pitches directly

        return matched / len(original)

    def _harmony_similarity(
        self, original: List[HarmonyEvent], reduced: List[HarmonyEvent]
    ) -> float:
        """Compare harmonic grids by attack count alignment."""
        if not original:
            return 1.0 if not reduced else 0.5
        if not reduced:
            return 0.0

        orig_bars = {h.bar for h in original}
        red_bars = {h.bar for h in reduced}
        if not orig_bars:
            return 0.5

        overlap = len(orig_bars & red_bars)
        return overlap / len(orig_bars)

    def _cadence_fidelity(self, original_cadence: CadenceApproach, reduced: SketchIR) -> float:
        """Check if the cadence survived realization."""
        if not original_cadence or original_cadence.type == "none":
            return 1.0

        # Check if there's a structural melody anchor at the cadence bar
        for anchor in reduced.melody_anchors:
            if anchor.bar == original_cadence.arrival_bar:
                return 1.0
            if abs(anchor.bar - original_cadence.arrival_bar) <= 1:
                return 0.7
        return 0.3

    def _motif_fidelity(self, original_placements, reduced_anchors) -> float:
        """Check if motif placements are reflected in the reduced anchors."""
        if not original_placements:
            return 1.0

        found = 0
        for placement in original_placements:
            for anchor in reduced_anchors:
                if abs(anchor.bar - placement.bar) <= 1:
                    found += 1
                    break

        return found / len(original_placements) if original_placements else 1.0
