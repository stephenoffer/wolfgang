"""
GestureBank — idiomatic gesture retrieval from corpus.

Wraps: tools/reference_index/<composer>/gesture_bank_*.json
Replaces: gesture_retriever.py, unified_gesture.py
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import GestureQuery, GestureResult

_BASE = Path(__file__).parent.parent
REFERENCE_INDEX = _BASE / "reference_index"


# ─── Composer-qualified role decomposition ────────────────────────────────────

_ROLE_DECOMPOSITIONS = {
    "mozart_light_response": {
        "function": "answer_with_space",
        "contour": "descending",
        "density_range": (3, 7),
    },
    "mozart_singing_line": {
        "function": "pickup",
        "texture_rh": "singing_melody",
    },
    "beethoven_insistence": {
        "function": "insist",
        "contour": "pedal",
    },
    "beethoven_hammer_stroke": {
        "function": "arrival",
        "texture_rh": "chordal",
    },
    "liszt_octave_blaze": {
        "function": "sequence_step",
        "density_range": (12, 20),
    },
    "rachmaninoff_bell_tolling": {
        "function": "sustain",
        "texture_lh": "block_chord_sparse",
    },
}


class GestureBank:
    """Gesture-level corpus retrieval.

    Gestures are 1-4 bar cells with function labels (pickup, answer, insist,
    arrival, etc.) that become the actual generation units in realization.
    """

    def __init__(self, composer: str = "mozart"):
        self.composer = composer
        self._index: dict | None = None
        self._shards: dict[int, list[dict]] = {}

    def _load_index(self) -> dict:
        if self._index is not None:
            return self._index

        index_path = REFERENCE_INDEX / self.composer / "gesture_bank.json"
        if not index_path.exists():
            self._index = {"total_cells": 0, "shards": []}
            return self._index

        with open(index_path) as f:
            self._index = json.load(f)
        return self._index

    def _load_shard(self, shard_idx: int) -> list[dict]:
        if shard_idx in self._shards:
            return self._shards[shard_idx]

        shard_path = REFERENCE_INDEX / self.composer / f"gesture_bank_{shard_idx:02d}.json"
        if not shard_path.exists():
            self._shards[shard_idx] = []
            return []

        with open(shard_path) as f:
            data = json.load(f)
        cells = data if isinstance(data, list) else data.get("cells", [])
        self._shards[shard_idx] = cells
        return cells

    def _load_all_cells(self) -> list[dict]:
        """Load all gesture cells — inline or sharded."""
        index = self._load_index()

        # Check for inline gestures first (common format)
        inline = index.get("gestures", [])
        if isinstance(inline, list) and inline:
            return inline

        # Fall back to sharded files
        all_cells = []
        shards = index.get("shards", [])
        for i, _shard_info in enumerate(shards):
            cells = self._load_shard(i)
            all_cells.extend(cells)
        # If no shard info but files exist, try loading sequentially
        if not all_cells:
            for i in range(10):
                cells = self._load_shard(i)
                if not cells:
                    break
                all_cells.extend(cells)
        return all_cells

    def _score_cell(self, cell: dict, query: GestureQuery) -> float:
        """Score a gesture cell against a query."""
        score = 0.0
        weights_total = 0.0

        # Function match (0.35)
        if query.function:
            w = 0.35
            weights_total += w
            cell_fn = cell.get("function", "")
            if cell_fn == query.function:
                score += w
            elif _same_gesture_family(cell_fn, query.function):
                score += w * 0.5

        # Contour (0.15)
        if query.contour:
            w = 0.15
            weights_total += w
            if cell.get("contour") == query.contour:
                score += w

        # RH texture (0.10)
        if query.texture_rh:
            w = 0.10
            weights_total += w
            if cell.get("rh_texture") == query.texture_rh:
                score += w

        # LH texture (0.05)
        if query.texture_lh:
            w = 0.05
            weights_total += w
            if cell.get("lh_texture") == query.texture_lh:
                score += w

        # Density (0.10)
        if query.density_range:
            w = 0.10
            weights_total += w
            density = cell.get("melody_density", 8)
            if query.density_range[0] <= density <= query.density_range[1]:
                score += w

        # Entry state (0.10)
        if query.entry_state:
            w = 0.10
            weights_total += w
            if cell.get("entry_state") == query.entry_state:
                score += w

        # Exit state (0.05)
        if query.exit_state:
            w = 0.05
            weights_total += w
            if cell.get("exit_state") == query.exit_state:
                score += w

        # Span beats (0.05)
        if query.min_span_beats or query.max_span_beats:
            w = 0.05
            weights_total += w
            span = cell.get("span_beats", 4.0)
            min_ok = span >= query.min_span_beats if query.min_span_beats else True
            max_ok = span <= query.max_span_beats if query.max_span_beats else True
            if min_ok and max_ok:
                score += w

        # Interaction role (0.05)
        if query.interaction_role:
            w = 0.05
            weights_total += w
            if cell.get("interaction_role") == query.interaction_role:
                score += w

        # Normalize
        if weights_total > 0:
            return score / weights_total
        return 0.5

    def retrieve(self, query: GestureQuery) -> list[GestureResult]:
        """Retrieve gestures matching the query, ranked by score."""
        # Decompose target_role if provided
        if query.target_role and query.target_role in _ROLE_DECOMPOSITIONS:
            decomp = _ROLE_DECOMPOSITIONS[query.target_role]
            if not query.function:
                query.function = decomp.get("function")
            if not query.contour:
                query.contour = decomp.get("contour")
            if not query.density_range:
                query.density_range = decomp.get("density_range")
            if not query.texture_rh:
                query.texture_rh = decomp.get("texture_rh")
            if not query.texture_lh:
                query.texture_lh = decomp.get("texture_lh")

        cells = self._load_all_cells()
        scored = []
        for cell in cells:
            s = self._score_cell(cell, query)
            if s > 0.1:
                scored.append((s, cell))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for s, cell in scored[: query.n]:
            results.append(
                GestureResult(
                    cell_id=cell.get("cell_id", ""),
                    function=cell.get("function", ""),
                    span_beats=cell.get("span_beats", 4.0),
                    accent_profile=cell.get("accent_profile", []),
                    dur_profile=cell.get("dur_profile", []),
                    contour=cell.get("contour", ""),
                    interaction_role=cell.get("interaction_role", ""),
                    harmony_binding=cell.get("harmony_binding", ""),
                    entry_state=cell.get("entry_state", ""),
                    exit_state=cell.get("exit_state", ""),
                    transform_ops=cell.get("transform_ops", []),
                    source=cell.get("source", ""),
                    rh_texture=cell.get("rh_texture", ""),
                    lh_texture=cell.get("lh_texture", ""),
                    melody_density=cell.get("melody_density", 8),
                    match_score=s,
                )
            )

        return results

    def get_function_distribution(self) -> dict[str, int]:
        """Get the distribution of gesture functions in this corpus."""
        cells = self._load_all_cells()
        counts: dict[str, int] = {}
        for cell in cells:
            fn = cell.get("function", "unknown")
            counts[fn] = counts.get(fn, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: -x[1]))


def _same_gesture_family(a: str, b: str) -> bool:
    """Check if two gesture functions are in the same family."""
    families = {
        "answer": {"answer", "answer_with_space", "echo"},
        "drive": {"insist", "sequence_step", "cadential_push"},
        "resolve": {"arrival", "cadential_release", "sustain"},
        "initiate": {"pickup", "lean_in"},
    }
    for family in families.values():
        if a in family and b in family:
            return True
    return False
