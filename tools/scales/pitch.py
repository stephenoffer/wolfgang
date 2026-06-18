"""
Pitch, interval, key, chord, and scale utilities for SCALES.

Ported from tools/v3/pitch_utils.py with fixes:
- Key-aware enharmonic spelling
- Double sharp/flat support
- Chord quality intervals
- Voice leading cost
"""

import re
from typing import List, Optional, Union

# ─── Pitch Constants ─────────────────────────────────────────────────────────

NOTE_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

SEMITONE_TO_NOTE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

SEMITONE_TO_NOTE_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

_SHARP_KEYS = frozenset(
    {
        "C",
        "G",
        "D",
        "A",
        "E",
        "B",
        "F#",
        "C#",
        "Am",
        "Em",
        "Bm",
        "F#m",
        "C#m",
        "G#m",
        "D#m",
    }
)


def prefer_sharps(key: str) -> bool:
    """Return True if the key uses sharps in its key signature."""
    return _normalize_key(key) in _SHARP_KEYS


# ─── Scale Intervals ─────────────────────────────────────────────────────────

SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
}

# ─── Chord Quality Intervals ─────────────────────────────────────────────────

CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "hdim7": [0, 3, 6, 10],
    "aug7": [0, 4, 8, 10],
    "sus4": [0, 5, 7],
    "sus2": [0, 2, 7],
}


# ─── Pitch Conversion ────────────────────────────────────────────────────────


def pitch_to_midi(p: Union[str, int, float, list, None]) -> Optional[int]:
    """Convert pitch string to MIDI number.

    Handles: 'C4'->60, 'F#5'->78, 'Bb3'->58, 'C##4'->62, 'Dbb3'->49
    Lists (chords): returns highest note.
    """
    if p is None or p == "rest":
        return None
    if isinstance(p, list):
        midis = [pitch_to_midi(n) for n in p if n != "rest"]
        midis = [m for m in midis if m is not None]
        return max(midis) if midis else None
    if isinstance(p, (int, float)):
        return int(p)

    s = str(p).strip()
    if not s:
        return None

    match = re.match(r"^([A-Ga-g])(#{0,2}|b{0,2})(\d+)$", s)
    if not match:
        return None

    note_name = match.group(1).upper()
    accidental = match.group(2)
    octave = int(match.group(3))

    midi = (octave + 1) * 12 + NOTE_TO_SEMITONE.get(note_name, 0)
    midi += accidental.count("#") - accidental.count("b")
    return midi


def midi_to_pitch(midi_val: int, key: str = "C") -> str:
    """Convert MIDI number to pitch string with key-aware spelling."""
    octave = (midi_val // 12) - 1
    names = SEMITONE_TO_NOTE_SHARP if prefer_sharps(key) else SEMITONE_TO_NOTE_FLAT
    note = names[midi_val % 12]
    return f"{note}{octave}"


def pitch_class(midi_val: int) -> int:
    """Return pitch class (0-11) from MIDI value."""
    return midi_val % 12


def interval_semitones(p1: Union[str, int], p2: Union[str, int]) -> Optional[int]:
    """Signed interval in semitones between two pitches."""
    m1 = pitch_to_midi(p1) if isinstance(p1, str) else p1
    m2 = pitch_to_midi(p2) if isinstance(p2, str) else p2
    if m1 is None or m2 is None:
        return None
    return m2 - m1


# ─── Scale Utilities ─────────────────────────────────────────────────────────


def build_scale(root_midi: int, mode: str = "major", octaves: int = 6) -> List[int]:
    """Build a multi-octave scale from a MIDI root."""
    intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
    result = []
    for oct in range(-2, octaves):
        for iv in intervals:
            m = root_midi + oct * 12 + iv
            if 0 <= m <= 127:
                result.append(m)
    return sorted(set(result))


def nearest_scale_tone(midi_val: int, scale: List[int], direction: str = "below") -> Optional[int]:
    """Find nearest scale tone strictly above or below midi_val."""
    if direction == "below":
        candidates = [s for s in scale if s < midi_val]
        return max(candidates) if candidates else None
    else:
        candidates = [s for s in scale if s > midi_val]
        return min(candidates) if candidates else None


def snap_to_scale(midi_val: int, scale: List[int]) -> int:
    """Snap a MIDI pitch to the nearest tone in the given scale."""
    if not scale:
        return midi_val
    return min(scale, key=lambda s: abs(s - midi_val))


def clamp_to_range(midi_val: int, low: int, high: int) -> int:
    """Shift a MIDI pitch by octaves until it falls within [low, high]."""
    while midi_val < low and midi_val + 12 <= 127:
        midi_val += 12
    while midi_val > high and midi_val - 12 >= 0:
        midi_val -= 12
    return midi_val


def _normalize_key(key: str) -> str:
    """Normalize key formats to short form: 'g_minor'->'Gm', 'bb_major'->'Bb', 'eb_major'->'Eb'.

    Handles: 'g_minor', 'bb_major', 'Gm', 'Bb', 'F#m', 'C',
    and modulation arrows 'g_minor->bb_major' (returns first key).
    """
    k = key.strip()
    # Handle modulation arrows — use the first key
    if "->" in k:
        k = k.split("->")[0].strip()
    # Handle underscore format: g_minor, bb_major, f_sharp_minor, etc.
    if "_" in k:
        parts = k.split("_")
        tonic = parts[0]
        mode = parts[1] if len(parts) > 1 else "major"
        # Capitalize tonic: g -> G, bb -> Bb, eb -> Eb, f# -> F#
        if len(tonic) == 1:
            tonic = tonic.upper()
        elif len(tonic) == 2:
            if tonic[1] == "b":
                tonic = tonic[0].upper() + "b"
            elif tonic[1] == "#":
                tonic = tonic[0].upper() + "#"
            else:
                tonic = tonic[0].upper() + tonic[1]
        else:
            tonic = tonic[0].upper() + tonic[1:]
        # Handle 'sharp' and 'flat' as words
        if "sharp" in mode:
            tonic += "#"
            mode = mode.replace("sharp_", "").replace("sharp", "")
        if mode in ("minor", "min"):
            return tonic + "m"
        return tonic
    return k


def key_to_root_midi(key: str) -> int:
    """Convert key name to root MIDI in octave 0.

    Handles: 'C'->0, 'D'->2, 'F#m'->6, 'g_minor'->7, 'bb_major'->10, 'eb_major'->3.
    """
    k = _normalize_key(key)
    k = k.rstrip("m")
    match = re.match(r"^([A-G])(#{0,2}|b{0,2})$", k)
    if not match:
        return 0
    note = match.group(1)
    acc = match.group(2)
    return NOTE_TO_SEMITONE.get(note, 0) + acc.count("#") - acc.count("b")


def is_minor_key(key: str) -> bool:
    """Check if a key string represents a minor key.

    Handles: 'Gm', 'g_minor', 'c_minor', 'F#m'.
    """
    k = _normalize_key(key)
    return k.endswith("m")


# ─── Chord Utilities ─────────────────────────────────────────────────────────


def chord_tones(root_midi: int, quality: str = "major") -> List[int]:
    """Return MIDI values for chord tones given root and quality."""
    intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])
    return [root_midi + iv for iv in intervals]


def voice_leading_cost(prev: List[int], curr: List[int]) -> int:
    """Total semitone motion between two voicings (same length assumed)."""
    if len(prev) != len(curr):
        return 999
    return sum(abs(a - b) for a, b in zip(prev, curr))


def is_chord_tone(midi_val: int, root_midi: int, quality: str = "major") -> bool:
    """Check if a MIDI pitch is a chord tone."""
    ct = chord_tones(root_midi % 12, quality)
    return (midi_val % 12) in [t % 12 for t in ct]
