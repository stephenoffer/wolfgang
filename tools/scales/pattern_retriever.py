"""
PatternRetriever — runtime access to 24,615 canonical LH patterns.

Lazy-loads 16 hex-sharded JSON files from pattern_library/canonical/.
Indexes by texture type and density. Provides transposition and
LayerEvent conversion for direct use by the realizer.
"""

from __future__ import annotations

import json
import logging
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .duration import bar_duration
from .enums import NoteRole
from .models import LayerEvent
from .pitch import key_to_root_midi, midi_to_pitch, pitch_to_midi

logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
_DEFAULT_PATTERN_DIR = _BASE / "pattern_library" / "canonical"


# Textures whose NAME asserts the left hand is carrying the bass.
# Only labels the library actually produces. `oom_pah` and `broken_octave` were
# in this set and match nothing: the pattern library's 16 texture labels do not
# include them, so they were two names that could never fire — the dead-label
# shape this project has hit before, where readers were updated and the
# generator was not. `walking_bass_chromatic` is a real label and belongs here.
_BASS_TEXTURES = frozenset(
    {"walking_bass", "walking_bass_chromatic", "bass_melody", "pedal_point", "alberti"}
)

_MIDDLE_C = 60


def _reaches_the_bass(pattern: Dict) -> bool:
    """Does this pattern put a single note below middle C?"""
    for event in pattern.get("lh_events", []):
        value = event.get("p")
        if not value or value == "rest":
            continue
        for name in value if isinstance(value, list) else [value]:
            try:
                midi = pitch_to_midi(name)
            except (ValueError, KeyError, TypeError):
                continue
            if midi is not None and midi < _MIDDLE_C:
                return True
    return False


def _distinct_pitches(pattern: Dict) -> int:
    """How much vocabulary a pattern actually uses — its distinct pitches.

    The measure that separates an Alberti bass from an octave alternation
    wearing its label. Chords count each of their notes.
    """
    seen: set = set()
    for event in pattern.get("lh_events") or []:
        pitch = event.get("p")
        if isinstance(pitch, list):
            seen.update(x for x in pitch if x and x != "rest")
        elif pitch and pitch != "rest":
            seen.add(pitch)
    return len(seen)


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
        self._vocab_floor: Dict[str, int] = {}

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
        ungrounded: List[Dict] = []
        for p in candidates:
            d = p.get("lh_density", 0)
            if d < density_range[0] or d > density_range[1]:
                continue
            if genre_filter and genre_filter not in p.get("genres", []):
                continue
            if p.get("composer_count", 0) < composer_count_min:
                continue
            # A pattern labelled `walking_bass` that never goes below middle C is
            # not a walking bass. 30 of 240 sampled patterns (12.5%) lie ENTIRELY
            # above middle C — pedal_point 10/40, walking_bass 9/40 — almost
            # certainly the two-voice staff split handing an inner line to the
            # left hand. A left hand may sit high, but not for a whole pattern
            # whose own label names the bass, so this is the label's definition
            # rather than a stylistic judgement.
            #
            # Sorted here rather than after the cap: callers ask for n=1, the cap
            # is n*3, and three high candidates were enough to exhaust the pool
            # before any preference could apply.
            if texture in _BASS_TEXTURES and not _reaches_the_bass(p):
                ungrounded.append(p)
                continue
            filtered.append(p)
            if len(filtered) >= n * 3:  # pre-filter cap
                break

        # No vocabulary is worse than an odd one, so fall back if nothing kept.
        if not filtered:
            filtered = ungrounded

        # MOST FREQUENT IS LEAST CHARACTERISTIC.
        #
        # The pool is sorted by `total_occurrences`, so the top of it is the
        # commonest bar shape in the corpus — which for any accompaniment idiom
        # is its most degenerate instance. The five patterns this returned for
        # `alberti`, the idiom itself:
        #
        #     occ=16917  C2 C3 C2 C3 C2 C3 C2 C3     <- an octave alternation
        #     occ=10965  G2 D3 G3 G2 D3 G3 G2 D3
        #     occ= 8408  G1 G2 G1 G2 G1 G2 G1 G2
        #
        # An Alberti bass is root-fifth-third-fifth. Retrieved alberti patterns
        # averaged 2.40 distinct pitches against 5.03 across the 3,173 in the
        # library — the material was there and the ranking could not reach it.
        # Downstream that reads as what it has become: a repeated pitch is
        # classified `pedal_point` (27% of our bars against a real 3.4%) and two
        # alternating pitches as `tremolo`.
        #
        # Frequency still ranks; it just no longer ranks alone. Candidates at or
        # above the texture's own median vocabulary come first, so the pattern
        # chosen is both well attested and recognisably the idiom. A FLOOR, not
        # a maximum — maximising picks the 15-pitch scale run that happens to be
        # labelled alberti, which is the same mistake facing the other way.
        floor = self._vocabulary_floor(texture)
        if floor > 0:
            filtered.sort(key=lambda p: _distinct_pitches(p) < floor)

        return filtered[:n]

    def _vocabulary_floor(self, texture: str) -> int:
        """Median distinct-pitch count for a texture, over the whole library."""
        if texture in self._vocab_floor:
            return self._vocab_floor[texture]
        pool = self._by_texture.get(texture, [])
        counts = sorted(_distinct_pitches(p) for p in pool)
        floor = counts[len(counts) // 2] if counts else 0
        self._vocab_floor[texture] = floor
        return floor

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
            if pitch == "rest":
                transposed_events.append({"p": pitch, "d": dur})
                continue
            if isinstance(pitch, list):
                # A CHORD used to fall straight through here untransposed, and
                # left-hand patterns are mostly chords and octaves — so the
                # canonical vocabulary the brief prints as "transposed to Eb
                # major" arrived in whatever key it was stored in. An Eb major
                # nocturne was shown `[G2,G3] [A2,A3] [B2,B3] [C3,C4] ...`:
                # C major, with three notes outside the key it was labelled as.
                moved = []
                for name in pitch:
                    try:
                        m = pitch_to_midi(name)
                    except (ValueError, KeyError, TypeError):
                        m = None
                    if m is None:
                        moved.append(name)
                    else:
                        moved.append(midi_to_pitch(max(21, min(108, m + interval)), to_key))
                transposed_events.append({"p": moved, "d": dur})
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
        meter: Tuple[int, int] = (4, 4),
    ) -> List[LayerEvent]:
        """Convert a canonical pattern into LayerEvents for a specific bar.

        Transposes to target key and creates one LayerEvent per note.

        The stored library is not clean and cannot be trusted note by note: of
        its 24,615 patterns, 9,565 event durations are values the notation
        cannot express — mostly triplets truncated to four decimals (0.3333
        rather than 1/3, so twelve of them sum to 0.9996 instead of 1) — and
        **360 events have a duration of zero**. A zero-duration note does not
        advance the cursor, so everything after it stacks on the same beat.

        So: quantize every duration onto the notatable table BEFORE using it,
        advance an exact Fraction cursor, drop the zero-length events, and stop
        at the bar's real capacity (patterns are stored as four beats and were
        being poured unchanged into 3/4 and 6/8 phrases).
        """
        transposed = self.transpose_pattern(pattern, source_key, target_key)
        events: List[LayerEvent] = []
        beat = Fraction(1)
        capacity = bar_duration(tuple(meter))

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
            dur_beats = _quantize(note.get("d", 0.25))
            if dur_beats <= 0:
                continue  # a zero-length note is corruption, not a grace note
            remaining = capacity - (beat - 1)
            if remaining <= 0:
                break
            if dur_beats > remaining:
                dur_beats = _quantize(remaining)
                if dur_beats <= 0 or dur_beats > remaining:
                    break

            events.append(
                LayerEvent(
                    bar=bar,
                    beat=round(float(beat), 6),
                    pitch=pitch,
                    duration=_beats_to_dur_str(dur_beats),
                    role=default_role,
                    dynamic=dynamic,
                    source_layer="response_layer",
                )
            )
            beat += dur_beats

        return events


def _quantize(beats) -> Fraction:
    """Snap a stored duration onto the notatable table, exactly.

    The library stores triplets as 0.3333 and 0.1667. Those resolve to the right
    CODE, but accumulating them as floats drifts the beat cursor off the grid —
    which is how onsets like 1.56 and 2.06 reached the score.
    """
    from .duration import DURATION_VALUES

    target = beats if isinstance(beats, Fraction) else Fraction(beats).limit_denominator(96)
    if target <= 0:
        return Fraction(0)
    return min(set(DURATION_VALUES.values()), key=lambda v: (abs(v - target), v))


def _beats_to_dur_str(beats) -> str:
    """Duration code for a beat value — delegates to the one duration table.

    This was a local list of eight plain values, so every tuplet and every value
    shorter than a 16th snapped to "s": a bar of corpus triplets came back as
    16ths and summed to two thirds of its meter. There is one duration table in
    this project and it knows tuplets, 32nds and 64ths.
    """
    from .duration import beats_to_dur

    return beats_to_dur(beats)
