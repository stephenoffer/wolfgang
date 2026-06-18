"""
PatchEngine — scope-aware revision at any compositional scale.

Supports natural-language edits at work, movement, section, phrase,
and bar levels. Identifies affected scope, preserves constraints above
and below, re-runs only necessary pipeline stages, and validates
cross-scale obligations.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from .enums import PhraseStatus
from .models import (
    PhraseState,
    RevisionOp,
    RevisionScript,
)

logger = logging.getLogger(__name__)


class PatchEngine:
    """Scope-aware revision engine.

    Each edit:
    1. Identifies affected scope (which phrases need re-composing)
    2. Preserves constraints above and below
    3. Re-runs only the necessary pipeline stages
    4. Validates that the edit didn't break cross-scale obligations
    """

    def identify_affected_phrases(
        self, revision: RevisionScript, all_phrase_ids: List[str]
    ) -> List[str]:
        """Determine which phrases are affected by a revision script."""
        affected: set = set()
        for op in revision.ops:
            if op.target_phrase:
                affected.add(op.target_phrase)
            elif op.target_bars:
                # Find phrases that overlap these bars
                # (simplified — would need bar-to-phrase mapping)
                affected.add(op.target_phrase or revision.section_id)
        return sorted(affected)

    def apply_revision_op(self, op: RevisionOp, phrase_state: PhraseState) -> PhraseState:
        """Apply a single revision operation to a phrase state.

        Returns the modified phrase state with status reset for
        re-composition at the appropriate stage.
        """
        operation = op.operation

        if operation == "re_sketch":
            phrase_state.sketch = None
            phrase_state.onset_bundles = None
            phrase_state.realized = None
            phrase_state.agent_authored = False
            phrase_state.review = None
            phrase_state.craft_check = None
            phrase_state.status = PhraseStatus.PLANNED.value

        elif operation == "re_realize":
            phrase_state.onset_bundles = None
            phrase_state.realized = None
            phrase_state.agent_authored = False
            phrase_state.review = None
            phrase_state.craft_check = None
            phrase_state.status = PhraseStatus.SKETCHED.value

        elif operation == "transpose_region":
            # Apply transposition to realized LayerIR
            if phrase_state.realized:
                interval = op.params.get("interval", 0)
                target_bars = op.target_bars
                self._transpose_events(phrase_state.realized.principal_line, interval, target_bars)
                self._transpose_events(phrase_state.realized.bass_foundation, interval, target_bars)
                phrase_state.review = None
                phrase_state.craft_check = None
                phrase_state.status = PhraseStatus.REALIZED.value

        elif operation == "change_texture":
            new_texture = op.params.get("lh_texture", "")
            if new_texture and phrase_state.slot.texture_plan:
                target_bars = op.target_bars
                for bar_plan in phrase_state.slot.texture_plan:
                    if target_bars is None or True:  # simplified
                        bar_plan.lh_texture = new_texture
                # Needs re-realization
                phrase_state.onset_bundles = None
                phrase_state.realized = None
                phrase_state.agent_authored = False
                phrase_state.status = PhraseStatus.SKETCHED.value

        elif operation == "change_dynamic":
            new_dynamic = op.params.get("dynamic", "")
            if new_dynamic and phrase_state.realized:
                target_bars = op.target_bars
                for evt in phrase_state.realized.principal_line:
                    if target_bars is None or (target_bars[0] <= evt.bar <= target_bars[1]):
                        evt.dynamic = new_dynamic
                phrase_state.status = PhraseStatus.REALIZED.value

        else:
            logger.warning("Unknown revision operation: %s", operation)

        return phrase_state

    def validate_edit_coherence(
        self, edited_phrases: List[str], all_phrase_ids: List[str]
    ) -> List[str]:
        """Check that edits didn't break cross-scale obligations.

        Returns list of warning messages. Empty = no issues.
        """
        warnings: List[str] = []

        # Check continuity: edited phrases should still connect
        for phrase_id in edited_phrases:
            idx = all_phrase_ids.index(phrase_id) if phrase_id in all_phrase_ids else -1
            if idx > 0:
                prev = all_phrase_ids[idx - 1]
                if prev not in edited_phrases:
                    warnings.append(
                        f"Phrase {phrase_id} was edited but previous phrase "
                        f"{prev} was not — check continuity"
                    )

        return warnings

    def _transpose_events(self, events: List, interval: int, target_bars: Optional[tuple]) -> None:
        """Transpose events by a chromatic interval."""
        from .pitch import midi_to_pitch, pitch_to_midi

        for evt in events:
            if target_bars and not (target_bars[0] <= evt.bar <= target_bars[1]):
                continue
            if evt.pitch == "rest" or isinstance(evt.pitch, list):
                continue
            try:
                midi = pitch_to_midi(evt.pitch)
                new_midi = max(21, min(108, midi + interval))
                evt.pitch = midi_to_pitch(new_midi, "C")
            except (ValueError, KeyError):
                pass
