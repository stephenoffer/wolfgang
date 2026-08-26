"""
CorpusBarRetriever — clean access to bar-level corpus data.

Provides per-composer lazy-loaded retrieval of real bars from
reference_index/<composer>/bars_*.json. Each bar contains actual
note events (rh_display, lh_display) with texture classification,
density, harmony, and register data.

A general-purpose API (no hardcoded recipes) for the context-aware
surface composer and the brief builder.
"""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .enums import NoteRole
from .models import LayerEvent
from .pitch import key_to_root_midi, midi_to_pitch, pitch_to_midi

logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
CORPUS_DIR = _BASE / "reference_index"


class CorpusBarRetriever:
    """Retrieves real bars from the corpus for a specific composer.

    Lazy-loads and indexes bars by (time_sig, key_mode, rh_texture, lh_texture).
    Provides transposition and LayerEvent conversion.
    """

    def __init__(self, composer: str):
        self.composer = composer
        self._bars: List[Dict] = []
        self._index: Dict[tuple, List[Dict]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        composer_dir = CORPUS_DIR / self.composer
        if not composer_dir.exists():
            logger.warning("Corpus directory not found: %s", composer_dir)
            self._loaded = True
            return

        for path in sorted(composer_dir.glob("bars_*.json")):
            try:
                with open(path) as f:
                    self._bars.extend(json.load(f))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load %s: %s", path, exc)

        # Build index
        for bar in self._bars:
            ts = tuple(bar.get("time_sig", [4, 4]))
            mode = bar.get("key_mode", "major")
            rh = bar.get("rh_texture", "unclassified")
            lh = bar.get("lh_texture", "unclassified")
            md = bar.get("melody_density", 0)
            ad = bar.get("accomp_density", 0)
            if md < 1 and ad < 1:
                continue
            key = (ts, mode, rh, lh)
            self._index.setdefault(key, []).append(bar)

        logger.info(
            "Loaded %d bars for %s (%d index keys)",
            len(self._bars),
            self.composer,
            len(self._index),
        )
        self._loaded = True

    @property
    def bar_count(self) -> int:
        self._ensure_loaded()
        return len(self._bars)

    def retrieve_bar(
        self,
        time_sig: Tuple[int, int],
        key_mode: str,
        rh_texture: str = "",
        lh_texture: str = "",
        min_density: int = 3,
    ) -> Optional[Dict]:
        """Retrieve a matching corpus bar.

        Tries exact match first, then relaxes textures progressively.
        Returns None if no match found.
        """
        self._ensure_loaded()

        key = (time_sig, key_mode, rh_texture, lh_texture)
        candidates = self._index.get(key, [])

        if not candidates and rh_texture:
            # Relax LH texture
            for k, v in self._index.items():
                if k[0] == time_sig and k[1] == key_mode and k[2] == rh_texture:
                    candidates.extend(v)

        if not candidates:
            # Relax both textures
            for k, v in self._index.items():
                if k[0] == time_sig and k[1] == key_mode:
                    candidates.extend(v)

        # Filter by density
        dense = [
            b
            for b in candidates
            if b.get("melody_density", 0) + b.get("accomp_density", 0) >= min_density
        ]
        if dense:
            candidates = dense

        if candidates:
            return random.choice(candidates)
        return None

    def bar_to_events(
        self,
        bar: Dict,
        target_bar_num: int,
        target_key: str,
        max_beats: float = 4.0,
        dynamic: Optional[str] = None,
    ) -> Tuple[List[LayerEvent], List[LayerEvent]]:
        """Convert a corpus bar into RH and LH LayerEvent lists.

        Transposes from the bar's source key to target_key.
        Returns (rh_events, lh_events).
        """
        src_key = bar.get("key", "C")
        transposition = _compute_transposition(src_key, target_key)

        def process_hand(display_key: str, layer_name: str) -> List[LayerEvent]:
            events: List[LayerEvent] = []
            beat = 1.0

            for evt in bar.get(display_key, []):
                if evt.get("is_grace"):
                    continue
                dur_beats = evt.get("dur", 0.25)
                # Do NOT snap the beat cursor to a 16th grid: two notes of a
                # triplet run land on the same position and one of them is lost.
                dur_beats = _quantize_duration(dur_beats)

                if beat > max_beats + 0.01:
                    break
                remaining = max_beats - beat + 1.0
                if dur_beats > remaining + 0.05:
                    dur_beats = _quantize_duration(max(0.25, remaining))

                dur_str = _beats_to_dur_str(dur_beats)

                if evt.get("type") == "rest":
                    beat += dur_beats
                    continue
                elif evt.get("type") == "chord":
                    for p_str in evt.get("pitches", []):
                        tp = _transpose_pitch(p_str, transposition, target_key)
                        if tp:
                            events.append(
                                LayerEvent(
                                    bar=target_bar_num,
                                    beat=round(beat, 2),
                                    pitch=tp,
                                    duration=dur_str,
                                    role=NoteRole.STRUCTURAL.value,
                                    dynamic=dynamic
                                    if beat <= 1.1 and display_key == "rh_display"
                                    else None,
                                    source_layer=layer_name,
                                )
                            )
                else:
                    pitch_str = evt.get("pitch", "")
                    tp = _transpose_pitch(pitch_str, transposition, target_key)
                    if tp:
                        events.append(
                            LayerEvent(
                                bar=target_bar_num,
                                beat=round(beat, 2),
                                pitch=tp,
                                duration=dur_str,
                                role=NoteRole.STRUCTURAL.value,
                                dynamic=dynamic
                                if beat <= 1.1 and display_key == "rh_display"
                                else None,
                                source_layer=layer_name,
                            )
                        )
                beat += dur_beats
            return events

        rh = process_hand("rh_display", "principal_line")
        lh = process_hand("lh_display", "bass_foundation")
        return rh, lh


def _compute_transposition(src_key: str, dst_key: str) -> int:
    """Compute chromatic transposition interval, normalized to [-6, +5]."""
    src_pc = key_to_root_midi(src_key)
    dst_pc = key_to_root_midi(dst_key)
    diff = dst_pc - src_pc
    if diff > 6:
        diff -= 12
    elif diff < -6:
        diff += 12
    return diff


def _transpose_pitch(pitch_str: str, transposition: int, dst_key: str) -> Optional[str]:
    """Transpose a pitch by a chromatic interval."""
    try:
        midi = pitch_to_midi(pitch_str)
    except (ValueError, KeyError):
        return None
    if midi is None:
        return None
    new_midi = max(21, min(108, midi + transposition))
    return midi_to_pitch(new_midi, dst_key)


def _quantize_duration(beats: float) -> float:
    """Snap to the nearest value the notation can actually express.

    The old list held eight plain durations, so a triplet eighth (1/3) snapped to
    a 16th and a 32nd vanished — a bar of corpus triplets came back a third
    short. The duration table IS the definition of what is notatable.
    """
    from .duration import DURATION_VALUES

    values = sorted({float(v) for v in DURATION_VALUES.values()})
    return min(values, key=lambda v: abs(v - float(beats)))


def _beats_to_dur_str(beats: float) -> str:
    """Duration code for a beat value — delegates to the one duration table.

    This was a local list of eight plain values, so every tuplet and every value
    shorter than a 16th snapped to "s": a bar of corpus triplets came back as
    16ths and summed to two thirds of its meter. There is one duration table in
    this project and it knows tuplets, 32nds and 64ths.
    """
    from .duration import beats_to_dur

    return beats_to_dur(beats)
