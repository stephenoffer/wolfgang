"""
CadenceBank — cadential realization retrieval.

Wraps: phrase_catalog.json (phrases with cadence_type != none),
       harmony grammar cadence patterns.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import CadenceQuery, CadenceResult

_BASE = Path(__file__).parent.parent
REFERENCE_INDEX = _BASE / "reference_index"


# ─── Built-in cadence patterns (harmony grammar) ─────────────────────────────

_CADENCE_PATTERNS = {
    "PAC": [
        {"chords": ["ii6", "V", "I"], "soprano": "2-7-1", "bass": "4-5-1", "strength": 5},
        {"chords": ["IV", "V", "I"], "soprano": "4-7-1", "bass": "4-5-1", "strength": 4},
        {"chords": ["ii", "V7", "I"], "soprano": "2-7-1", "bass": "2-5-1", "strength": 5},
        {"chords": ["vi", "ii6", "V", "I"], "soprano": "1-2-7-1", "bass": "6-4-5-1", "strength": 5},
        {"chords": ["I64", "V", "I"], "soprano": "1-7-1", "bass": "5-5-1", "strength": 4},
    ],
    "IAC": [
        {"chords": ["ii6", "V", "I"], "soprano": "2-2-3", "bass": "4-5-1", "strength": 3},
        {"chords": ["IV", "V", "I"], "soprano": "4-5-3", "bass": "4-5-1", "strength": 3},
    ],
    "HC": [
        {"chords": ["I", "IV", "V"], "soprano": "1-4-5", "bass": "1-4-5", "strength": 3},
        {"chords": ["ii6", "V"], "soprano": "2-5", "bass": "4-5", "strength": 3},
        {"chords": ["I", "ii", "V"], "soprano": "1-2-5", "bass": "1-2-5", "strength": 3},
    ],
    "DC": [
        {"chords": ["V", "vi"], "soprano": "7-1", "bass": "5-6", "strength": 2},
        {"chords": ["V7", "vi"], "soprano": "2-1", "bass": "5-6", "strength": 2},
    ],
    "plagal": [
        {"chords": ["IV", "I"], "soprano": "4-3", "bass": "4-1", "strength": 2},
        {"chords": ["iv", "I"], "soprano": "b6-5", "bass": "4-1", "strength": 3},
    ],
    "evaded": [
        {"chords": ["V", "I6"], "soprano": "7-1", "bass": "5-3", "strength": 1},
        {"chords": ["V7", "vi"], "soprano": "4-3", "bass": "5-6", "strength": 1},
    ],
}


class CadenceBank:
    """Cadential realization retrieval.

    Combines built-in harmony patterns with real cadential phrases
    from the corpus.
    """

    def __init__(self, composer: str = "mozart"):
        self.composer = composer
        self._cadence_phrases: Optional[List[Dict]] = None

    def _load_cadence_phrases(self) -> List[Dict]:
        """Load phrases with cadences from corpus."""
        if self._cadence_phrases is not None:
            return self._cadence_phrases

        catalog_path = REFERENCE_INDEX / self.composer / "phrase_catalog.json"
        if not catalog_path.exists():
            self._cadence_phrases = []
            return []

        with open(catalog_path) as f:
            catalog = json.load(f)

        self._cadence_phrases = [
            p for p in catalog.get("phrases", []) if p.get("cadence_type", "none") != "none"
        ]
        return self._cadence_phrases

    def _score_pattern(self, pattern: Dict, query: CadenceQuery) -> float:
        """Score a built-in cadence pattern."""
        score = 0.0

        # Cadence type match (0.40) — already filtered
        score += 0.40

        # Soprano arrival (0.15)
        if query.soprano_arrival_degree:
            soprano = pattern.get("soprano", "")
            arrival = soprano.split("-")[-1] if soprano else ""
            if arrival == str(query.soprano_arrival_degree):
                score += 0.15

        # Strength (0.10)
        strength = pattern.get("strength", 3)
        score += 0.10 * (strength / 5.0)

        # Approach length (0.10)
        n_chords = len(pattern.get("chords", []))
        if n_chords <= query.approach_length_bars:
            score += 0.10

        return score

    def _score_corpus_phrase(self, phrase: Dict, query: CadenceQuery) -> float:
        """Score a corpus phrase for cadence retrieval."""
        score = 0.0

        # Type match (0.40) — already filtered
        score += 0.40

        # Key mode match (0.15)
        if phrase.get("key_mode") == query.mode:
            score += 0.15

        # Texture match (0.15)
        if query.texture_family:
            rh_textures = phrase.get("rh_textures", [])
            if query.texture_family in rh_textures:
                score += 0.15

        # Length proximity (0.10)
        length = phrase.get("length", 4)
        if length >= query.approach_length_bars:
            score += 0.10

        return score

    def retrieve(self, query: CadenceQuery) -> List[CadenceResult]:
        """Retrieve cadential realizations matching the query."""
        results = []

        # 1. Built-in patterns
        patterns = _CADENCE_PATTERNS.get(query.cadence_type, [])
        for pattern in patterns:
            score = self._score_pattern(pattern, query)
            results.append(
                CadenceResult(
                    cadence_id=f"pattern_{query.cadence_type}_{patterns.index(pattern)}",
                    cadence_type=query.cadence_type,
                    source="harmony_grammar",
                    chord_sequence=pattern.get("chords", []),
                    soprano_arrival=pattern.get("soprano", "").split("-")[-1],
                    bass_motion=pattern.get("bass", ""),
                    texture_at_cadence="",
                    density_at_cadence=8,
                    dynamic_at_cadence="mf",
                    approach_bars=None,
                    strength=pattern.get("strength", 3),
                    match_score=score,
                )
            )

        # 2. Corpus phrases with matching cadence
        cadence_phrases = self._load_cadence_phrases()
        for phrase in cadence_phrases:
            if phrase.get("cadence_type") != query.cadence_type:
                continue
            score = self._score_corpus_phrase(phrase, query)
            last_rh = phrase.get("rh_textures", [""])[-1] if phrase.get("rh_textures") else ""
            results.append(
                CadenceResult(
                    cadence_id=phrase.get("phrase_id", ""),
                    cadence_type=query.cadence_type,
                    source=phrase.get("source", ""),
                    chord_sequence=[],  # Would need bar-level data to extract
                    soprano_arrival="",
                    bass_motion="",
                    texture_at_cadence=last_rh,
                    density_at_cadence=int(phrase.get("avg_melody_density", 8)),
                    dynamic_at_cadence="mf",
                    approach_bars=None,
                    strength=3,
                    match_score=score,
                )
            )

        # Sort and limit
        results.sort(key=lambda r: r.match_score, reverse=True)
        return results[: query.n]
