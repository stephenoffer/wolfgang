"""
Duration and meter utilities for SCALES.

Ported from tools/v3/pitch_utils.py duration section.
"""

from typing import Union

# ─── Duration Constants ──────────────────────────────────────────────────────

DURATION_VALUES = {
    # Standard
    "w": 4.0,  # whole
    "h": 2.0,  # half
    "q": 1.0,  # quarter
    "e": 0.5,  # eighth
    "s": 0.25,  # sixteenth
    "16": 0.25,  # sixteenth alias
    "t": 0.125,  # thirty-second
    "32": 0.125,  # thirty-second alias
    # Dotted
    "dw": 6.0,
    "dh": 3.0,
    "dq": 1.5,
    "de": 0.75,
    "ds": 0.375,
    # Double-dotted
    "ddh": 3.5,
    "ddq": 1.75,
    "dde": 0.875,
    # Triplets
    "trip_q": 2 / 3,
    "trip_e": 1 / 3,
    "trip_s": 1 / 6,
}


def dur_to_beats(d: Union[str, int, float]) -> float:
    """Convert a duration code to quarter-note beats.

    Accepts codes ('q', 'dq', 'trip_e') or numeric values.
    Returns 0.0 for unrecognized strings.
    """
    if isinstance(d, (int, float)):
        return float(d)
    d_str = str(d).strip()
    if d_str in DURATION_VALUES:
        return DURATION_VALUES[d_str]
    try:
        return float(d_str)
    except (ValueError, TypeError):
        return 0.0


def beats_to_dur(beats: float) -> str:
    """Convert beat value to nearest duration code."""
    best = "q"
    best_diff = abs(beats - 1.0)
    for code, val in DURATION_VALUES.items():
        diff = abs(val - beats)
        if diff < best_diff:
            best_diff = diff
            best = code
    return best


def bar_duration(time_sig: tuple) -> float:
    """Total beats in a bar given a time signature (num, denom).

    (4, 4) -> 4.0, (3, 4) -> 3.0, (6, 8) -> 3.0
    """
    num, denom = time_sig
    return num * (4.0 / denom)


def is_strong_beat(beat: float, time_sig: tuple) -> bool:
    """Check if a beat position is a strong beat in the given meter."""
    num, denom = time_sig
    if denom == 4:
        if num == 4:
            return beat in (1.0, 3.0)
        if num == 3:
            return beat == 1.0
        if num == 2:
            return beat == 1.0
    if denom == 8:
        if num == 6:
            return beat in (1.0, 2.5)  # compound duple
        if num == 9:
            return beat in (1.0, 2.0, 3.0)
    return beat == 1.0


def is_downbeat(beat: float) -> bool:
    """Check if this is beat 1."""
    return abs(beat - 1.0) < 0.001


def beats_per_measure(time_sig: tuple) -> float:
    """Beats per measure in quarter-note units."""
    return bar_duration(time_sig)


def subdivisions_per_beat(time_sig: tuple) -> int:
    """Common subdivision count per beat."""
    _, denom = time_sig
    if denom == 8:
        return 3  # compound
    return 2  # simple
