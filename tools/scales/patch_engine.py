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
            # EVERY layer, or the ones left behind stay in the old key and the
            # "revision" produces instant dissonance. This transposed only
            # principal_line and bass_foundation, so the inner voices, the
            # accompaniment figuration and the ornamental surface were all left
            # a fifth (or whatever) away from the music around them.
            if phrase_state.realized:
                interval = op.params.get("interval", 0)
                key = op.params.get("key") or getattr(phrase_state.slot, "key", "C")
                for events in self._all_layers(phrase_state.realized):
                    self._transpose_events(events, interval, op.target_bars, key)
                phrase_state.review = None
                phrase_state.craft_check = None
                phrase_state.status = PhraseStatus.REALIZED.value

        elif operation == "change_texture":
            new_texture = op.params.get("lh_texture", "")
            if new_texture and phrase_state.slot.texture_plan:
                target_bars = op.target_bars
                bar_start = getattr(phrase_state.slot, "bar_start", 1) or 1
                for offset, bar_plan in enumerate(phrase_state.slot.texture_plan):
                    # `if target_bars is None or True` ignored target_bars
                    # entirely, so an op asking to change the texture of two
                    # bars rewrote every bar of the phrase.
                    bar = getattr(bar_plan, "bar", None) or (bar_start + offset)
                    if target_bars and not (target_bars[0] <= bar <= target_bars[1]):
                        continue
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

        elif operation == "set_articulation":
            # The critic's commonest finding by far is an unarticulated page.
            # Without an op for it the only way to act was `re_realize`, which
            # throws away the notes to change a marking.
            art = op.params.get("articulation")
            layer_name = op.target_layer or "principal_line"
            if art and phrase_state.realized:
                for evt in getattr(phrase_state.realized, layer_name, None) or []:
                    if op.target_bars and not (op.target_bars[0] <= evt.bar <= op.target_bars[1]):
                        continue
                    if evt.pitch != "rest" and evt.tie not in ("stop", "continue"):
                        evt.articulation = art
                phrase_state.review = None
                phrase_state.status = PhraseStatus.REALIZED.value

        elif operation == "set_hairpin":
            # A crescendo across a span: start on the first note in range, stop
            # on the last. Shaping within a phrase was otherwise unreachable.
            kind = op.params.get("kind", "cresc")
            if phrase_state.realized:
                events = [
                    e
                    for e in (phrase_state.realized.principal_line or [])
                    if e.pitch != "rest"
                    and (
                        not op.target_bars
                        or op.target_bars[0] <= e.bar <= op.target_bars[1]
                    )
                ]
                if len(events) >= 2:
                    for e in events:
                        e.hairpin = None
                    events[0].hairpin = f"{kind}_start"
                    events[-1].hairpin = "stop"
                    phrase_state.review = None
                    phrase_state.status = PhraseStatus.REALIZED.value

        elif operation == "set_expression":
            text = op.params.get("text")
            if text and phrase_state.realized:
                for evt in phrase_state.realized.principal_line or []:
                    if op.target_bars and evt.bar != op.target_bars[0]:
                        continue
                    if evt.pitch != "rest":
                        evt.expression = text
                        break
                phrase_state.status = PhraseStatus.REALIZED.value

        elif operation == "thin_texture":
            # Drop the off-beat notes of the accompaniment in a range, leaving
            # the harmony intact. This is what "the texture never thins" asks
            # for, and it is a change no re-realization can be asked to make.
            if phrase_state.realized:
                for name in ("response_layer", "bass_foundation"):
                    events = getattr(phrase_state.realized, name, None) or []
                    keep = []
                    for evt in events:
                        in_range = not op.target_bars or (
                            op.target_bars[0] <= evt.bar <= op.target_bars[1]
                        )
                        on_beat = abs(evt.beat - round(evt.beat)) < 0.01
                        if not in_range or on_beat or evt.pitch == "rest":
                            keep.append(evt)
                    if keep:
                        setattr(phrase_state.realized, name, keep)
                phrase_state.review = None
                phrase_state.craft_check = None
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

    @staticmethod
    def _all_layers(layer_ir) -> List[List]:
        """Every event list in a LayerIR — piano layers, orchestral layers, and
        the numbered inner voices. A transform that touches only some of them
        leaves the rest behind."""
        names = (
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
        )
        out = [getattr(layer_ir, n, None) or [] for n in names]
        out.extend((getattr(layer_ir, "inner_voices", None) or {}).values())
        return [e for e in out if e]

    def _transpose_events(
        self,
        events: List,
        interval: int,
        target_bars: Optional[tuple],
        key: str = "C",
    ) -> None:
        """Transpose events by a chromatic interval.

        Chords transpose too — skipping them left the harmony in the old key
        while the melody moved, which is worse than not transposing at all. And
        the spelling follows the phrase's own KEY: always spelling in C turned a
        transposition into D-flat major into a page of sharps.
        """
        from .pitch import midi_to_pitch, pitch_to_midi

        def _shift(name: str) -> str:
            midi = pitch_to_midi(name)
            return midi_to_pitch(max(21, min(108, midi + interval)), key)

        for evt in events:
            if target_bars and not (target_bars[0] <= evt.bar <= target_bars[1]):
                continue
            if evt.pitch == "rest":
                continue
            try:
                if isinstance(evt.pitch, list):
                    evt.pitch = [_shift(p) for p in evt.pitch if p != "rest"]
                else:
                    evt.pitch = _shift(evt.pitch)
            except (ValueError, KeyError, TypeError):
                pass
