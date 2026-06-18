"""
PatternRetriever — runtime access to 24,615 canonical LH patterns.

Lazy-loads 16 hex-sharded JSON files from pattern_library/canonical/.
Indexes by texture type and density. Provides transposition and
LayerEvent conversion for direct use by the realizer.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .enums import NoteRole
from .models import LayerEvent
from .pitch import key_to_root_midi, midi_to_pitch, pitch_to_midi

logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
_DEFAULT_PATTERN_DIR = _BASE / "pattern_library" / "canonical"


class PatternRetriever:
    """Retrieves real LH patterns from pattern_library/canonical/.

    Lazy-loads all 16 shards on first query. Indexes by texture type
    and density bucket for fast retrieval.

    Each canonical pattern has:
        hash, lh_events [{p, d}], lh_texture, lh_density,
        event_count, duration_total, genres, total_occurrences,
        composer_count
    """

    def __init__(self, pattern_dir: Optional[Path] = None):
        self._pattern_dir = pattern_dir or _DEFAULT_PATTERN_DIR
        self._by_texture: Dict[str, List[Dict]] = {}
        self._total_loaded = 0
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load all 16 hex shards and build indexes."""
        if self._loaded:
            return

        if not self._pattern_dir.exists():
            logger.warning("Pattern directory not found: %s", self._pattern_dir)
            self._loaded = True
            return

        for shard_file in sorted(self._pattern_dir.glob("shard_*.json")):
            try:
                with open(shard_file) as f:
                    shard = json.load(f)
                for _hash_key, pattern in shard.items():
                    texture = pattern.get("lh_texture", "unknown")
                    self._by_texture.setdefault(texture, []).append(pattern)
                    self._total_loaded += 1
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load shard %s: %s", shard_file, exc)

        # Sort each texture list by total_occurrences descending
        for texture in self._by_texture:
            self._by_texture[texture].sort(
                key=lambda p: p.get("total_occurrences", 0), reverse=True
            )

        logger.info(
            "Loaded %d canonical patterns across %d textures",
            self._total_loaded,
            len(self._by_texture),
        )
        self._loaded = True

    @property
    def texture_names(self) -> List[str]:
        """Return available texture names."""
        self._ensure_loaded()
        return list(self._by_texture.keys())

    @property
    def total_patterns(self) -> int:
        self._ensure_loaded()
        return self._total_loaded

    def retrieve(
        self,
        texture: str,
        density_range: Tuple[int, int] = (4, 24),
        genre_filter: Optional[str] = None,
        composer_count_min: int = 0,
        n: int = 5,
    ) -> List[Dict]:
        """Retrieve top-N patterns matching texture + density + genre.

        Ranked by total_occurrences within matching constraints.
        """
        self._ensure_loaded()
        candidates = self._by_texture.get(texture, [])
        if not candidates:
            return []

        filtered: List[Dict] = []
        for p in candidates:
            d = p.get("lh_density", 0)
            if d < density_range[0] or d > density_range[1]:
                continue
            if genre_filter and genre_filter not in p.get("genres", []):
                continue
            if p.get("composer_count", 0) < composer_count_min:
                continue
            filtered.append(p)
            if len(filtered) >= n * 3:  # pre-filter cap
                break

        return filtered[:n]

    def transpose_pattern(self, pattern: Dict, from_key: str, to_key: str) -> Dict:
        """Transpose a pattern's pitch events to target key.

        Returns a new pattern dict with transposed lh_events.
        """
        from_root = key_to_root_midi(from_key)
        to_root = key_to_root_midi(to_key)
        interval = to_root - from_root

        transposed_events: List[Dict] = []
        for event in pattern.get("lh_events", []):
            pitch = event.get("p", "rest")
            dur = event.get("d", 0.25)
            if pitch == "rest" or isinstance(pitch, list):
                transposed_events.append({"p": pitch, "d": dur})
                continue
            try:
                midi = pitch_to_midi(pitch)
                if midi is None:
                    transposed_events.append({"p": pitch, "d": dur})
                    continue
                new_midi = max(21, min(108, midi + interval))
                transposed_events.append(
                    {
                        "p": midi_to_pitch(new_midi, to_key),
                        "d": dur,
                    }
                )
            except (ValueError, KeyError, TypeError):
                transposed_events.append({"p": pitch, "d": dur})

        result = pattern.copy()
        result["lh_events"] = transposed_events
        return result

    def pattern_to_events(
        self,
        pattern: Dict,
        bar: int,
        target_key: str,
        source_key: str = "C",
        dynamic: Optional[str] = None,
    ) -> List[LayerEvent]:
        """Convert a canonical pattern into LayerEvents for a specific bar.

        Transposes to target key and creates one LayerEvent per note.
        """
        transposed = self.transpose_pattern(pattern, source_key, target_key)
        events: List[LayerEvent] = []
        beat = 1.0

        texture = pattern.get("lh_texture", "")
        arpeggiated_textures = {
            "alberti",
            "broken_chord_wave",
            "broken_chord_asc",
            "broken_chord_desc",
        }
        default_role = (
            NoteRole.ARPEGGIATED_FILL.value
            if texture in arpeggiated_textures
            else NoteRole.STRUCTURAL.value
        )

        for note in transposed.get("lh_events", []):
            pitch = note.get("p", "rest")
            dur_beats = note.get("d", 0.25)
            dur_str = _beats_to_dur_str(dur_beats)

            events.append(
                LayerEvent(
                    bar=bar,
                    beat=round(beat, 4),
                    pitch=pitch,
                    duration=dur_str,
                    role=default_role,
                    dynamic=dynamic,
                    source_layer="response_layer",
                )
            )
            beat += dur_beats

        return events


def _beats_to_dur_str(beats: float) -> str:
    """Convert beat duration to duration string."""
    mapping = {
        4.0: "w",
        3.0: "dh",
        2.0: "h",
        1.5: "dq",
        1.0: "q",
        0.75: "de",
        0.5: "e",
        0.25: "s",
    }
    closest = min(mapping.keys(), key=lambda k: abs(k - beats))
    return mapping[closest]
