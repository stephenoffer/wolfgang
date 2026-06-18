"""
CraftChecker — enforces the phrase sanctity checklist.

Every phrase must pass before acceptance:
- melodic claim is clear
- rhythm has identity
- bass has purpose
- harmony is voiced, not just labeled
- there is a breath point
- accompaniment responds to melody
- entry and exit feel earned
- at least one memorable detail (encouraged, not blocking)
"""

from __future__ import annotations

from typing import List, Optional

from .models import (
    LayerIR,
    OnsetBundle,
    PhraseControlIR,
    PhraseCraftCheck,
)
from .pitch import pitch_to_midi


class CraftChecker:
    """Enforces the phrase sanctity checklist."""

    def check(
        self,
        layer_ir: LayerIR,
        control: Optional[PhraseControlIR] = None,
        bundles: Optional[List[OnsetBundle]] = None,
    ) -> PhraseCraftCheck:
        """Run all craft checks on a realized phrase."""
        return PhraseCraftCheck(
            melodic_claim_clear=self._check_melodic_claim(layer_ir),
            rhythm_has_identity=self._check_rhythmic_identity(layer_ir),
            bass_has_purpose=self._check_bass_purpose(layer_ir),
            harmony_is_voiced=self._check_harmony_voiced(layer_ir),
            has_breath_point=self._check_breathing(layer_ir),
            accompaniment_responds_to_melody=self._check_accomp_response(layer_ir),
            entry_exit_earned=self._check_entry_exit(layer_ir, control),
            has_memorable_detail=self._check_memorable_detail(layer_ir),
            all_notes_justified=self._check_justifications(bundles),
        )

    def _check_melodic_claim(self, layer: LayerIR) -> bool:
        """Melody exists and has directional movement."""
        melody = layer.principal_line
        if len(melody) < 3:
            return False

        midis = []
        for evt in melody:
            if evt.pitch != "rest" and not isinstance(evt.pitch, list):
                try:
                    midis.append(pitch_to_midi(evt.pitch))
                except (ValueError, KeyError):
                    pass

        if len(midis) < 3:
            return False

        # Check that melody has directional movement (not all same pitch)
        pitch_range = max(midis) - min(midis)
        return pitch_range >= 3  # at least a minor third

    def _check_rhythmic_identity(self, layer: LayerIR) -> bool:
        """Rhythm has variety — not all same duration."""
        all_events = layer.principal_line + layer.response_layer
        if len(all_events) < 4:
            return False

        durations = [evt.duration for evt in all_events if evt.pitch != "rest"]
        unique = set(durations)
        return len(unique) >= 2

    def _check_bass_purpose(self, layer: LayerIR) -> bool:
        """Bass exists and provides harmonic foundation."""
        bass = layer.bass_foundation
        if len(bass) < 2:
            return False

        # Bass should have at least one note per 2 bars
        bars_with_bass = set(evt.bar for evt in bass if evt.pitch != "rest")
        expected_bars = max(1, layer.bar_count // 2)
        return len(bars_with_bass) >= expected_bars

    def _check_harmony_voiced(self, layer: LayerIR) -> bool:
        """Harmony is not just bass root — has inner voices or chords."""
        total_events = len(layer.response_layer) + len(layer.counter_reply)
        return total_events >= 2

    def _check_breathing(self, layer: LayerIR) -> bool:
        """Has at least one rest or breath point."""
        all_events = layer.principal_line + layer.bass_foundation + layer.response_layer
        rests = sum(1 for evt in all_events if evt.pitch == "rest")
        return rests >= 1 or layer.bar_count <= 2

    def _check_accomp_response(self, layer: LayerIR) -> bool:
        """Accompaniment exists and has enough density."""
        return len(layer.response_layer) >= 4

    def _check_entry_exit(self, layer: LayerIR, control: Optional[PhraseControlIR]) -> bool:
        """Entry and exit are defined (melody starts and ends)."""
        melody = layer.principal_line
        if not melody:
            return False
        first = melody[0]
        last = melody[-1]
        return first.pitch != "rest" and last.pitch != "rest"

    def _check_memorable_detail(self, layer: LayerIR) -> bool:
        """Has at least one non-obvious moment (ornament, dynamic change, etc.)."""
        ornaments = len(layer.ornamental_surface)
        dynamic_changes = len(set(evt.dynamic for evt in layer.principal_line if evt.dynamic))
        articulation_variety = len(
            set(evt.articulation for evt in layer.principal_line if evt.articulation)
        )
        return ornaments > 0 or dynamic_changes > 1 or articulation_variety > 0

    def _check_justifications(self, bundles: Optional[List[OnsetBundle]]) -> bool:
        """Every note has at least one structural + one local reason."""
        if not bundles:
            return True  # skip if no bundles (backward compat)

        for bundle in bundles:
            for onset in bundle.events:
                if onset.pitch == "rest":
                    continue
                j = onset.justification
                if not j.structural_reasons or not j.local_reasons:
                    return False
        return True
