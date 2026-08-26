"""
PerformanceBank — expressive rendering pattern retrieval.

Provides performance templates for rubato, dynamics, pedaling, and
articulation by phrase type. Built from heuristic classification of
corpus data (grace notes, rest patterns, density changes).
"""

from __future__ import annotations

from .models import PerformanceQuery, PerformanceResult

# ─── Built-in performance patterns ───────────────────────────────────────────
# These are heuristic templates derived from common-practice performance,
# not extracted from MIDI performance data (which we don't have).

_PATTERNS = [
    # Cadence approaches
    {
        "pattern_id": "cadence_rit",
        "phrase_type": "cadence_approach",
        "tempo_modification": "slight_rit",
        "dynamic_curve": [0.6, 0.7, 0.8, 0.65],
        "pedal_pattern": "sustain_through",
        "source": "common_practice",
    },
    {
        "pattern_id": "cadence_spread",
        "phrase_type": "cadence_approach",
        "tempo_modification": "broadening",
        "dynamic_curve": [0.7, 0.8, 0.9, 0.6],
        "pedal_pattern": "sustain_through",
        "source": "common_practice",
    },
    # Post-appoggiatura
    {
        "pattern_id": "appoggiatura_lean",
        "phrase_type": "post_appoggiatura",
        "tempo_modification": "slight_delay",
        "dynamic_curve": [0.8, 0.5],
        "pedal_pattern": "finger_legato",
        "source": "common_practice",
    },
    # Rubato peaks
    {
        "pattern_id": "rubato_peak_stretch",
        "phrase_type": "rubato_peak",
        "tempo_modification": "stretch_peak",
        "dynamic_curve": [0.6, 0.7, 0.9, 0.8, 0.7],
        "pedal_pattern": "sustain_through",
        "source": "common_practice",
    },
    # Subito dynamic
    {
        "pattern_id": "subito_piano",
        "phrase_type": "subito_dynamic",
        "tempo_modification": None,
        "dynamic_curve": [0.9, 0.3, 0.4, 0.5],
        "pedal_pattern": "half_pedal",
        "source": "common_practice",
    },
    {
        "pattern_id": "subito_forte",
        "phrase_type": "subito_dynamic",
        "tempo_modification": None,
        "dynamic_curve": [0.3, 0.9, 0.85, 0.8],
        "pedal_pattern": "sustain_through",
        "source": "common_practice",
    },
    # Opening
    {
        "pattern_id": "gentle_opening",
        "phrase_type": "opening",
        "tempo_modification": "slight_rit_first_beat",
        "dynamic_curve": [0.5, 0.55, 0.6, 0.65],
        "pedal_pattern": "finger_legato",
        "source": "common_practice",
    },
    # Crescendo buildup
    {
        "pattern_id": "crescendo_buildup",
        "phrase_type": "crescendo_buildup",
        "tempo_modification": "slight_accel",
        "dynamic_curve": [0.4, 0.5, 0.6, 0.7, 0.8],
        "pedal_pattern": "sustain_through",
        "source": "common_practice",
    },
    # Post-climax breathing
    {
        "pattern_id": "post_climax_breath",
        "phrase_type": "post_climax",
        "tempo_modification": "rit_then_a_tempo",
        "dynamic_curve": [0.9, 0.6, 0.4, 0.45],
        "pedal_pattern": "release_then_half",
        "source": "common_practice",
    },
    # Thinning/emptying
    {
        "pattern_id": "thinning_release",
        "phrase_type": "thinning",
        "tempo_modification": "slight_rit",
        "dynamic_curve": [0.6, 0.5, 0.4, 0.3],
        "pedal_pattern": "gradual_release",
        "source": "common_practice",
    },
]


class PerformanceBank:
    """Expressive performance pattern retrieval.

    Provides heuristic performance templates (rubato, dynamics, pedaling)
    since the corpus data is purely symbolic (no MIDI performance data).
    """

    def __init__(self, composer: str = "mozart"):
        self.composer = composer

    def retrieve(self, query: PerformanceQuery) -> list[PerformanceResult]:
        """Retrieve performance patterns matching the query."""
        results = []

        for pattern in _PATTERNS:
            score = self._score_pattern(pattern, query)
            if score > 0.1:
                results.append(
                    PerformanceResult(
                        pattern_id=pattern["pattern_id"],
                        phrase_type=pattern["phrase_type"],
                        tempo_modification=pattern.get("tempo_modification"),
                        dynamic_curve=pattern.get("dynamic_curve", []),
                        pedal_pattern=pattern.get("pedal_pattern"),
                        source=pattern.get("source", ""),
                        match_score=score,
                    )
                )

        results.sort(key=lambda r: r.match_score, reverse=True)
        return results[: query.n]

    def _score_pattern(self, pattern: dict, query: PerformanceQuery) -> float:
        """Score a pattern against a query."""
        score = 0.0

        # Phrase type match (0.50)
        if pattern["phrase_type"] == query.phrase_type:
            score += 0.50
        elif _similar_phrase_type(pattern["phrase_type"], query.phrase_type):
            score += 0.25

        # Dynamic context (0.25)
        if query.dynamic_context:
            curve = pattern.get("dynamic_curve", [])
            if curve:
                if query.dynamic_context == "pp_to_ff" and curve[-1] > curve[0]:
                    score += 0.25
                elif query.dynamic_context == "ff_to_pp" and curve[-1] < curve[0]:
                    score += 0.25
                elif query.dynamic_context == "steady_mf":
                    variance = sum((x - 0.5) ** 2 for x in curve) / len(curve)
                    if variance < 0.05:
                        score += 0.25
        else:
            score += 0.125

        # Texture (0.25) — light matching
        if query.texture:
            score += 0.125  # baseline
        else:
            score += 0.125

        return score


def _similar_phrase_type(a: str, b: str) -> bool:
    """Check if two phrase types are similar."""
    families = {
        "cadence": {"cadence_approach", "cadence_spread"},
        "expression": {"post_appoggiatura", "rubato_peak"},
        "dynamic": {"subito_dynamic", "crescendo_buildup"},
        "ending": {"post_climax", "thinning"},
    }
    for family in families.values():
        if a in family and b in family:
            return True
    return False
