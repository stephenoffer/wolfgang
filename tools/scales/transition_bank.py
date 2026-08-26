"""
TransitionBank — phrase-to-phrase transition retrieval and scoring.

Wraps: Adjacent phrase pairs from phrase_catalog,
       transition matrices from pattern_library/transitions/.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import TransitionQuery, TransitionResult
from .pitch import pitch_to_midi

_BASE = Path(__file__).parent.parent
REFERENCE_INDEX = _BASE / "reference_index"
PATTERN_LIBRARY = _BASE / "pattern_library"

# Dynamic level mapping for distance computation
_DYNAMIC_LEVELS = {"pp": 0, "p": 1, "mp": 2, "mf": 3, "f": 4, "ff": 5, "fff": 6}


class TransitionBank:
    """Phrase-to-phrase transition retrieval and scoring.

    Retrieves actual transition examples from corpus and scores them
    for register continuity, harmonic plausibility, dynamic flow,
    texture contrast, and motivic logic.
    """

    def __init__(self, composer: str = "mozart"):
        self.composer = composer
        self._adjacency_pairs: list[dict] | None = None
        self._transition_matrix: dict | None = None

    def _load_adjacency_pairs(self) -> list[dict]:
        """Build adjacency index from phrase catalog."""
        if self._adjacency_pairs is not None:
            return self._adjacency_pairs

        catalog_path = REFERENCE_INDEX / self.composer / "phrase_catalog.json"
        if not catalog_path.exists():
            self._adjacency_pairs = []
            return []

        with open(catalog_path) as f:
            catalog = json.load(f)

        phrases = catalog.get("phrases", [])

        # Group by source movement
        by_source: dict[str, list[dict]] = {}
        for p in phrases:
            src = p.get("source", "")
            by_source.setdefault(src, []).append(p)

        # Build consecutive pairs
        pairs = []
        for source, source_phrases in by_source.items():
            source_phrases.sort(key=lambda x: x.get("bar_range", [0])[0])
            for i in range(len(source_phrases) - 1):
                pairs.append(
                    {
                        "from": source_phrases[i],
                        "to": source_phrases[i + 1],
                        "source": source,
                    }
                )

        self._adjacency_pairs = pairs
        return pairs

    def _load_transition_matrix(self) -> dict:
        """Delegates to the single canonical loader.

        This method existed twice, byte-identical, in this class and in
        `TransitionBank`, and both fell back to the *classical* genre matrix for
        every composer — so a Bach or a ``style__romantic`` piece was handed
        Classical texture-transition odds while `by_genre/baroque.json` and
        `by_genre/romantic.json` sat unread next to it.
        """
        if self._transition_matrix is None:
            from .style_registry import load_transition_matrix

            self._transition_matrix = load_transition_matrix(self.composer, PATTERN_LIBRARY)
        return self._transition_matrix

    def score_transition(
        self, from_state: dict, to_state: dict, query: TransitionQuery
    ) -> TransitionResult:
        """Score a transition between two phrase states."""
        # Register continuity
        from_reg = from_state.get("register_center", query.exit_register_center)
        to_reg = to_state.get("register_center", from_reg)
        reg_dist = abs(from_reg - to_reg)
        register_continuity = max(0, 1.0 - reg_dist / 24.0)

        # Harmonic plausibility
        from_cad = query.exit_cadence_type or ""
        to_fn = to_state.get("function", query.target_function or "")
        harmonic_plausibility = _harmonic_plausibility_score(from_cad, to_fn)

        # Dynamic continuity
        from_dyn = query.exit_dynamic or "mf"
        to_dyn = to_state.get("dynamic", "mf")
        dyn_dist = abs(_DYNAMIC_LEVELS.get(from_dyn, 3) - _DYNAMIC_LEVELS.get(to_dyn, 3))
        dynamic_continuity = max(0, 1.0 - dyn_dist / 4.0)

        # Texture contrast
        matrix = self._load_transition_matrix()
        from_tex = query.exit_texture_lh
        to_tex = to_state.get("lh_texture", "")
        if from_tex and to_tex:
            counts = matrix.get("counts", {}).get(from_tex, {})
            total = sum(counts.values()) if counts else 1
            prob = counts.get(to_tex, 0) / max(total, 1)
            actual_contrast = 1.0 - prob
            texture_contrast = 1.0 - abs(actual_contrast - query.texture_contrast_preference)
        else:
            texture_contrast = 0.5

        # Motivic logic (basic: same source gets a bonus)
        motivic_logic = 0.5

        composite = (
            0.25 * register_continuity
            + 0.20 * harmonic_plausibility
            + 0.15 * dynamic_continuity
            + 0.25 * texture_contrast
            + 0.15 * motivic_logic
        )

        return TransitionResult(
            register_continuity=register_continuity,
            harmonic_plausibility=harmonic_plausibility,
            dynamic_continuity=dynamic_continuity,
            texture_contrast=texture_contrast,
            motivic_logic=motivic_logic,
            composite_score=composite,
            entry_state=to_state,
        )

    def retrieve(self, query: TransitionQuery) -> list[TransitionResult]:
        """Retrieve transition examples matching the query."""
        pairs = self._load_adjacency_pairs()
        results = []

        for pair in pairs:
            from_phrase = pair["from"]
            to_phrase = pair["to"]

            # Extract states
            from_state = {
                "register_center": from_phrase.get("register_curve", [0.5])[-1] * 48 + 48,
                "density": from_phrase.get("density_curve", [1.0])[-1] * 16,
                "rh_texture": from_phrase.get("rh_textures", [""])[-1]
                if from_phrase.get("rh_textures")
                else "",
                "lh_texture": from_phrase.get("lh_textures", [""])[-1]
                if from_phrase.get("lh_textures")
                else "",
                "cadence_type": from_phrase.get("cadence_type", "none"),
            }
            to_state = {
                "register_center": to_phrase.get("register_curve", [0.5])[0] * 48 + 48
                if to_phrase.get("register_curve")
                else 72,
                "function": to_phrase.get("role", ""),
                "lh_texture": to_phrase.get("lh_textures", [""])[0]
                if to_phrase.get("lh_textures")
                else "",
                "dynamic": "mf",
            }

            result = self.score_transition(from_state, to_state, query)
            result.from_phrase_id = from_phrase.get("phrase_id", "")
            result.to_phrase_id = to_phrase.get("phrase_id", "")

            if result.composite_score > 0.2:
                results.append(result)

        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results[: query.n]

    def score_candidate_transition(
        self, prev_surface, curr_surface, query: TransitionQuery
    ) -> float:
        """Score the transition between two realized LayerIR surfaces."""
        # Extract states from LayerIR
        from_state = _extract_exit_state(prev_surface)
        to_state = _extract_entry_state(curr_surface)
        result = self.score_transition(from_state, to_state, query)
        return result.composite_score


def _harmonic_plausibility_score(from_cadence: str, to_function: str) -> float:
    """Score harmonic plausibility of a cadence → next phrase function transition."""
    # Strong transitions
    strong = {
        ("PAC", "presentation"): 1.0,
        ("PAC", "contrasting_theme"): 0.9,
        ("PAC", "closing"): 0.9,
        ("HC", "continuation"): 1.0,
        ("HC", "cadential"): 0.9,
        ("DC", "continuation"): 0.8,
        ("DC", "transition"): 0.8,
        ("evaded", "cadential"): 0.9,
        ("evaded", "continuation"): 0.8,
        ("none", ""): 0.7,
    }
    return strong.get((from_cadence, to_function), 0.5)


def _extract_exit_state(surface) -> dict:
    """Extract exit state from a LayerIR."""
    if surface is None:
        return {}
    last_melody = surface.principal_line[-1] if surface.principal_line else None
    surface.bass_foundation[-1] if surface.bass_foundation else None
    return {
        "register_center": pitch_to_midi(last_melody.pitch) if last_melody else 72,
        "density": len(surface.principal_line),
        "dynamic": last_melody.dynamic if last_melody else "mf",
    }


def _extract_entry_state(surface) -> dict:
    """Extract entry state from a LayerIR."""
    if surface is None:
        return {}
    first_melody = surface.principal_line[0] if surface.principal_line else None
    return {
        "register_center": pitch_to_midi(first_melody.pitch) if first_melody else 72,
        "function": "",
        "dynamic": first_melody.dynamic if first_melody else "mf",
    }
