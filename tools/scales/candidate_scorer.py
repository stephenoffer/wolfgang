"""
CandidateScorer — multi-dimensional scoring for realization candidates.

Replaces: critic_stack.py, style_critic.py, mechanicality_critic.py,
          novelty_guard.py, contract_fidelity_scorer.py

Scores candidates on:
  - style_fidelity: how well it matches StyleDNA
  - sketch_fidelity: round-trip reduction similarity
  - expectation_score: ledger satisfaction
  - novelty_score: not plagiarized, not repetitive
  - continuity_score: smooth transition from previous phrase
  - lock_compliance: preservation of locked source elements
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .enums import NoteRole
from .expectation_ledger import ExpectationLedger
from .models import (
    AntiPatternRule,
    CandidateNode,
    CandidateScores,
    ContextTrace,
    LayerIR,
    LockPolicy,
    PhraseSlot,
    StyleDNA,
)
from .pitch import pitch_to_midi
from .reducer import Reducer
from .validator import validate_layer_ir

# Fallback budgets per tier
_FALLBACK_BUDGETS = {"A": 0.10, "B": 0.20, "C": 0.35, "D": 1.00}


class CandidateScorer:
    """Scores realization candidates across multiple dimensions."""

    def __init__(self, reducer: Optional[Reducer] = None):
        self.reducer = reducer or Reducer()

    def score(
        self,
        candidate: CandidateNode,
        slot: PhraseSlot,
        style_dna: StyleDNA,
        ledger: ExpectationLedger,
        phrase_order: List[str],
        prev_surface: Optional[LayerIR] = None,
        locks: Optional[LockPolicy] = None,
        mode: str = "compose_from_text",
        context_trace: Optional[ContextTrace] = None,
        anti_patterns: Optional[List[AntiPatternRule]] = None,
        tier: str = "D",
    ) -> CandidateScores:
        """Score a single candidate across all dimensions."""
        surface = candidate.surface
        sketch = candidate.sketch
        if surface is None or sketch is None:
            return CandidateScores(hard_pass=False)

        scores = CandidateScores()

        # Hard constraint check (meter, range, playability)
        report = validate_layer_ir(surface)
        scores.hard_pass = report.passed

        # 1. Style fidelity
        scores.style_fidelity = self._score_style(surface, style_dna)

        # 2. Sketch fidelity (round-trip)
        if candidate.reduced is None:
            candidate.reduced = self.reducer.reduce(surface)
        scores.sketch_fidelity = self.reducer.compare(sketch, candidate.reduced)

        # 3. Expectation satisfaction
        scores.expectation_score = ledger.score_phrase_resolution(slot.phrase_id, phrase_order)

        # 4. Novelty
        scores.novelty_score = self._score_novelty(surface, prev_surface)

        # 5. Continuity
        scores.continuity_score = self._score_continuity(surface, prev_surface)

        # 6. Lock compliance
        scores.lock_compliance = self._score_locks(surface, locks)

        # 7. Context fidelity (v6)
        scores.context_fidelity = self._score_context(context_trace, tier)

        # 8. Anti-pattern risk (v6)
        scores.anti_pattern_risk = self._score_anti_patterns(surface, anti_patterns, prev_surface)

        return scores

    def score_all(
        self,
        candidates: List[CandidateNode],
        slot: PhraseSlot,
        style_dna: StyleDNA,
        ledger: ExpectationLedger,
        phrase_order: List[str],
        prev_surface: Optional[LayerIR] = None,
        locks: Optional[LockPolicy] = None,
        mode: str = "compose_from_text",
        context_traces: Optional[Dict[int, ContextTrace]] = None,
        anti_patterns: Optional[List[AntiPatternRule]] = None,
        tier: str = "D",
    ) -> List[CandidateNode]:
        """Score all candidates and attach scores."""
        for i, cand in enumerate(candidates):
            trace = context_traces.get(i) if context_traces else None
            cand.scores = self.score(
                cand,
                slot,
                style_dna,
                ledger,
                phrase_order,
                prev_surface,
                locks,
                mode,
                context_trace=trace,
                anti_patterns=anti_patterns,
                tier=tier,
            )
        # Sort by total score
        candidates.sort(key=lambda c: c.scores.total(mode), reverse=True)
        return candidates

    # ─── Style Fidelity ──────────────────────────────────────────────────

    def _score_style(self, surface: LayerIR, style_dna: StyleDNA) -> float:
        """Score how well the surface matches the target style."""
        scores = []

        # Density match
        if style_dna.density_targets:
            target = style_dna.density_targets.get("moderate")
            if target:
                actual_density = len(surface.principal_line) / max(surface.bar_count, 1)
                expected = target.rh_mean
                density_score = max(0, 1.0 - abs(actual_density - expected) / max(expected, 1))
                scores.append(density_score)

        # Texture distribution match
        if style_dna.lh_distribution and surface.response_layer:
            # Classify actual LH texture
            lh_density = len(surface.response_layer) / max(surface.bar_count, 1)
            if lh_density >= 12:
                actual_tex = "alberti"
            elif lh_density >= 6:
                actual_tex = "broken_chord_wave"
            elif lh_density >= 3:
                actual_tex = "bass_melody"
            else:
                actual_tex = "block_chord_sparse"

            tex_prob = style_dna.lh_distribution.get(actual_tex, 0.1)
            scores.append(min(tex_prob * 5, 1.0))  # Scale probability to 0-1

        # Role tag distribution — penalize too many passing tones
        if surface.principal_line:
            structural = sum(
                1 for e in surface.principal_line if e.role == NoteRole.STRUCTURAL.value
            )
            total = len(surface.principal_line)
            structural_ratio = structural / max(total, 1)
            # Good: 30-60% structural
            if 0.3 <= structural_ratio <= 0.6:
                scores.append(1.0)
            else:
                scores.append(max(0, 1.0 - abs(structural_ratio - 0.45) * 3))

        return sum(scores) / max(len(scores), 1)

    # ─── Novelty ─────────────────────────────────────────────────────────

    def _score_novelty(self, surface: LayerIR, prev_surface: Optional[LayerIR]) -> float:
        """Score novelty — not too repetitive of previous phrase."""
        if prev_surface is None:
            return 0.8  # No comparison available

        # Check if melody contour is different from previous
        curr_midis = [
            pitch_to_midi(e.pitch)
            for e in surface.principal_line
            if e.pitch != "rest" and not isinstance(e.pitch, list)
        ]
        prev_midis = [
            pitch_to_midi(e.pitch)
            for e in prev_surface.principal_line
            if e.pitch != "rest" and not isinstance(e.pitch, list)
        ]

        curr_midis = [m for m in curr_midis if m is not None]
        prev_midis = [m for m in prev_midis if m is not None]

        if not curr_midis or not prev_midis:
            return 0.7

        # Compute contour similarity
        curr_contour = _to_contour(curr_midis)
        prev_contour = _to_contour(prev_midis)
        similarity = _contour_similarity(curr_contour, prev_contour)

        # We want some similarity (coherence) but not too much (repetition)
        # Sweet spot: 0.3-0.6 similarity
        if 0.3 <= similarity <= 0.6:
            return 1.0
        elif similarity < 0.3:
            return 0.6  # Too different — might break coherence
        else:
            return max(0, 1.0 - (similarity - 0.6) * 2.5)  # Too similar

    # ─── Continuity ──────────────────────────────────────────────────────

    def _score_continuity(self, surface: LayerIR, prev_surface: Optional[LayerIR]) -> float:
        """Score transition smoothness from previous phrase."""
        if prev_surface is None:
            return 0.8

        scores = []

        # Register continuity
        last_melody = prev_surface.principal_line[-1] if prev_surface.principal_line else None
        first_melody = surface.principal_line[0] if surface.principal_line else None

        if last_melody and first_melody:
            last_midi = pitch_to_midi(last_melody.pitch)
            first_midi = pitch_to_midi(first_melody.pitch)
            if last_midi and first_midi:
                leap = abs(last_midi - first_midi)
                if leap <= 5:
                    scores.append(1.0)
                elif leap <= 12:
                    scores.append(0.6)
                else:
                    scores.append(max(0, 1.0 - leap / 24.0))

        # Dynamic continuity
        last_dyn = last_melody.dynamic if last_melody else "mf"
        first_dyn = first_melody.dynamic if first_melody else "mf"
        dyn_levels = {"pp": 0, "p": 1, "mp": 2, "mf": 3, "f": 4, "ff": 5}
        dyn_dist = abs(dyn_levels.get(last_dyn, 3) - dyn_levels.get(first_dyn, 3))
        scores.append(max(0, 1.0 - dyn_dist / 3.0))

        return sum(scores) / max(len(scores), 1)

    # ─── Lock Compliance ─────────────────────────────────────────────────

    def _score_locks(self, surface: LayerIR, locks: Optional[LockPolicy]) -> float:
        """Score preservation of locked source elements."""
        if locks is None:
            return 1.0  # No locks — everything compliant

        # Handle dict (from JSON deserialization) or LockPolicy object
        if isinstance(locks, dict):
            total_lock = sum(locks.values())
        else:
            total_lock = (
                locks.principal_melody
                + locks.bass_foundation
                + locks.cadence_hits
                + locks.counterline
                + locks.form_layout
                + locks.key_scheme
            )
        if total_lock == 0:
            return 1.0

        # For score-to-score modes, would compare surface against source
        # (requires source reference, handled in SABRE mode)
        return 0.8  # Default for non-zero locks without source comparison

    # ─── Context Fidelity (v6) ──────────────────────────────────────────

    def _score_context(self, trace: Optional[ContextTrace], tier: str) -> float:
        """Score based on how much context was actually used.

        Higher for candidates that used corpus patterns, gesture templates,
        and breathing rules. Lower for excessive hardcoded fallback.
        """
        if trace is None:
            return 0.5  # No trace → neutral score

        total = trace.total_bar_count
        if total == 0:
            return 0.5

        corpus_ratio = (len(trace.corpus_patterns_used) + len(trace.corpus_bars_used)) / total
        gesture_bonus = min(len(trace.gestures_applied) * 0.1, 0.3)
        breathing_bonus = min(len(trace.breathing_rules_applied) * 0.05, 0.15)

        fallback_ratio = trace.fallback_bar_count / total
        budget = _FALLBACK_BUDGETS.get(tier, 1.0)
        fallback_penalty = 0.0
        if fallback_ratio > budget:
            over = (fallback_ratio - budget) / max(1.0 - budget, 0.01)
            fallback_penalty = 0.55 * min(over, 1.2)

        return min(1.0, max(0.0, corpus_ratio + gesture_bonus + breathing_bonus - fallback_penalty))

    # ─── Anti-Pattern Risk (v6) ─────────────────────────────────────────

    def _score_anti_patterns(
        self,
        surface: LayerIR,
        anti_patterns: Optional[List[AntiPatternRule]],
        prev_surface: Optional[LayerIR],
    ) -> float:
        """Score anti-pattern risk. 0.0 = clean, 1.0 = many violations.

        The CandidateScores.total() uses (1.0 - anti_pattern_risk) so
        that lower risk → higher total.
        """
        if anti_patterns is None:
            return 0.0  # No rules → no risk

        from .anti_pattern_detector import run_all_detectors

        results = run_all_detectors(surface, anti_patterns, prev_surface)
        if not results:
            return 0.0

        violations = sum(1 for r in results if r["detected"])
        return min(1.0, violations / max(len(results), 1))


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _to_contour(midis: List[int]) -> List[int]:
    """Convert pitch sequence to contour (up/down/same)."""
    if len(midis) < 2:
        return []
    contour = []
    for i in range(1, len(midis)):
        diff = midis[i] - midis[i - 1]
        if diff > 0:
            contour.append(1)
        elif diff < 0:
            contour.append(-1)
        else:
            contour.append(0)
    return contour


def _contour_similarity(a: List[int], b: List[int]) -> float:
    """Compare two contour sequences. Returns 0-1."""
    if not a or not b:
        return 0.0
    min_len = min(len(a), len(b))
    matches = sum(1 for i in range(min_len) if a[i] == b[i])
    return matches / min_len
