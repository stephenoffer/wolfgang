"""
PhraseBank — phrase-level retrieval from corpus data.

Wraps:
  - tools/reference_index/<composer>/phrase_catalog.json
  - tools/reference_index/<composer>/window_index_*.json
  - tools/pattern_library/ (transition matrices, canonical patterns)

Replaces: exemplar_retriever.py, window_retriever.py, corpus_analyzer.py,
          pattern_library.py, texture_retriever.py, texture_sequencer.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from .models import PhraseQuery, PhraseResult

# ─── Corpus Paths ────────────────────────────────────────────────────────────

_BASE = Path(__file__).parent.parent
REFERENCE_INDEX = _BASE / "reference_index"
PATTERN_LIBRARY = _BASE / "pattern_library"


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors. Returns 0 if either is empty."""
    if not a or not b:
        return 0.0
    min_len = min(len(a), len(b))
    a, b = a[:min_len], b[:min_len]
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


class PhraseBank:
    """Phrase-level corpus retrieval.

    Retrieves 2-16 bar phrases (not individual bars) with rich metadata
    for style-grounded composition.
    """

    def __init__(self, composer: str = "mozart"):
        self.composer = composer
        self._phrase_catalog: dict | None = None
        self._window_shards: dict[int, list[dict]] = {}
        self._transition_matrix: dict | None = None

    def _load_phrase_catalog(self) -> dict:
        if self._phrase_catalog is not None:
            return self._phrase_catalog

        catalog_path = REFERENCE_INDEX / self.composer / "phrase_catalog.json"
        if not catalog_path.exists():
            self._phrase_catalog = {"phrases": [], "total_phrases": 0}
            return self._phrase_catalog

        with open(catalog_path) as f:
            self._phrase_catalog = json.load(f)
        return self._phrase_catalog

    def _load_window_shard(self, shard_idx: int) -> list[dict]:
        if shard_idx in self._window_shards:
            return self._window_shards[shard_idx]

        shard_path = REFERENCE_INDEX / self.composer / f"window_index_{shard_idx:02d}.json"
        if not shard_path.exists():
            self._window_shards[shard_idx] = []
            return []

        with open(shard_path) as f:
            data = json.load(f)
        windows = data if isinstance(data, list) else data.get("windows", [])
        self._window_shards[shard_idx] = windows
        return windows

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

    # ─── Scoring ──────────────────────────────────────────────────────────

    def _score_phrase(self, phrase: dict, query: PhraseQuery) -> tuple[float, dict[str, float]]:
        """Score a phrase against a query. Returns (total, breakdown)."""
        breakdown = {}

        # Formal function (0.20)
        if query.formal_function:
            role = phrase.get("role", "")
            if role == query.formal_function:
                breakdown["function"] = 1.0
            elif _same_function_family(role, query.formal_function):
                breakdown["function"] = 0.5
            else:
                breakdown["function"] = 0.0
        else:
            breakdown["function"] = 0.5

        # Cadence type (0.15)
        if query.cadence_type:
            breakdown["cadence"] = 1.0 if phrase.get("cadence_type") == query.cadence_type else 0.0
        else:
            breakdown["cadence"] = 0.5

        # Cadence distance (0.10)
        if query.cadence_distance is not None:
            actual = phrase.get("length", 4)
            breakdown["cadence_dist"] = max(
                0, 1.0 - abs(actual - query.cadence_distance) / max(query.cadence_distance, 1)
            )
        else:
            breakdown["cadence_dist"] = 0.5

        # Density curve similarity (0.15)
        if query.density_curve and phrase.get("density_curve"):
            breakdown["density"] = max(
                0, _cosine_similarity(query.density_curve, phrase["density_curve"])
            )
        else:
            breakdown["density"] = 0.5

        # Texture match (0.10)
        tex_score = 0.0
        if query.rh_texture_family:
            rh_textures = phrase.get("rh_textures", [])
            tex_score += 0.5 if query.rh_texture_family in rh_textures else 0.0
        else:
            tex_score += 0.25
        if query.lh_texture_family:
            lh_textures = phrase.get("lh_textures", [])
            tex_score += 0.5 if query.lh_texture_family in lh_textures else 0.0
        else:
            tex_score += 0.25
        breakdown["texture"] = tex_score

        # Key mode (0.05)
        if query.key_mode:
            breakdown["key_mode"] = 1.0 if phrase.get("key_mode") == query.key_mode else 0.0
        else:
            breakdown["key_mode"] = 0.5

        # Contour class (0.05)
        if query.contour_class:
            # Check melody_directions or bass_contour
            contours = phrase.get("melody_directions", []) or []
            breakdown["contour"] = 1.0 if query.contour_class in contours else 0.0
        else:
            breakdown["contour"] = 0.5

        # Entry/exit texture compatibility (0.05)
        entry_score = 0.5
        if query.entry_texture:
            first_rh = phrase.get("rh_textures", [""])[0] if phrase.get("rh_textures") else ""
            entry_score = 1.0 if first_rh == query.entry_texture else 0.0
        breakdown["entry_exit"] = entry_score

        # Length fit (0.05)
        length = phrase.get("length", 4)
        if query.length_range[0] <= length <= query.length_range[1]:
            breakdown["length"] = 1.0
        else:
            overshoot = max(0, length - query.length_range[1]) + max(
                0, query.length_range[0] - length
            )
            breakdown["length"] = max(0, 1.0 - overshoot * 0.2)

        # Harmony path (0.10)
        if query.harmony_path_class:
            phrase.get("harmony_path", [])
            breakdown["harmony"] = 0.5  # basic default; could classify paths
        else:
            breakdown["harmony"] = 0.5

        # Weighted total
        weights = {
            "function": 0.20,
            "cadence": 0.15,
            "cadence_dist": 0.10,
            "density": 0.15,
            "texture": 0.10,
            "key_mode": 0.05,
            "contour": 0.05,
            "entry_exit": 0.05,
            "length": 0.05,
            "harmony": 0.10,
        }
        total = sum(weights[k] * breakdown.get(k, 0.5) for k in weights)
        return total, breakdown

    # ─── Retrieval ────────────────────────────────────────────────────────

    def retrieve(self, query: PhraseQuery) -> list[PhraseResult]:
        """Retrieve phrases matching the query, ranked by score."""
        catalog = self._load_phrase_catalog()
        phrases = catalog.get("phrases", [])

        scored = []
        for phrase in phrases:
            score, breakdown = self._score_phrase(phrase, query)
            if score > 0.1:
                scored.append((score, breakdown, phrase))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate by source if requested
        if query.deduplicate_by_source:
            seen_sources = set()
            deduped = []
            for score, breakdown, phrase in scored:
                source = phrase.get("source", "")
                if source not in seen_sources:
                    seen_sources.add(source)
                    deduped.append((score, breakdown, phrase))
            scored = deduped

        # Limit to n
        results = []
        for score, breakdown, phrase in scored[: query.n]:
            bar_range = tuple(phrase.get("bar_range", [1, 4]))
            results.append(
                PhraseResult(
                    phrase_id=phrase.get("phrase_id", ""),
                    source=phrase.get("source", ""),
                    bar_range=bar_range,
                    length=phrase.get("length", bar_range[1] - bar_range[0] + 1),
                    role=phrase.get("role", ""),
                    cadence_type=phrase.get("cadence_type", ""),
                    key=phrase.get("key", ""),
                    key_mode=phrase.get("key_mode", ""),
                    density_curve=phrase.get("density_curve", []),
                    register_curve=phrase.get("register_curve", []),
                    rh_textures=phrase.get("rh_textures", []),
                    lh_textures=phrase.get("lh_textures", []),
                    match_score=score,
                    match_breakdown=breakdown,
                    entry_state=phrase.get("entry_state", {}),
                    exit_state=phrase.get("exit_state", {}),
                )
            )

        return results

    def get_transition_probability(self, from_texture: str, to_texture: str) -> float:
        """Get transition probability from one texture to another."""
        matrix = self._load_transition_matrix()
        counts = matrix.get("counts", {})
        from_counts = counts.get(from_texture, {})
        if not from_counts:
            return 0.0
        total = sum(from_counts.values())
        if total == 0:
            return 0.0
        return from_counts.get(to_texture, 0) / total

    def get_texture_distribution(self) -> dict[str, float]:
        """Get the overall texture distribution for this composer."""
        catalog = self._load_phrase_catalog()
        phrases = catalog.get("phrases", [])
        if not phrases:
            return {}

        counts: dict[str, int] = {}
        total = 0
        for phrase in phrases:
            for tex in phrase.get("rh_textures", []):
                counts[tex] = counts.get(tex, 0) + 1
                total += 1

        if total == 0:
            return {}
        return {k: v / total for k, v in counts.items()}


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _same_function_family(a: str, b: str) -> bool:
    """Check if two phrase functions are in the same family."""
    families = {
        "opening": {"opening", "presentation", "statement"},
        "middle": {"middle", "continuation", "sequence", "development"},
        "closing": {"closing", "cadential", "codetta", "coda"},
    }
    for family in families.values():
        if a in family and b in family:
            return True
    return False
