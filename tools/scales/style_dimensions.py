"""Multi-dimensional style fingerprint over bar records.

The original corpus comparison (corpus_metrics.bar_metrics) only covered
rhythm/texture/density. Style lives on more axes — this module adds HARMONY,
MELODY, and RHYTHM-VALUE dimensions, computed from the note-level content the
bar records already carry (rh_display/lh_display pitches, interval_from_root,
durations). The SAME function runs on corpus bars and on an assembled piece's
bars (via build_full_corpus.analyze_score_bars), so the comparison is
apples-to-apples — exactly like corpus_metrics, just broader.

Each dimension reduces to a small dict of scalar features so a piece can be
scored against a composer's per-feature mean/sd (see build_corpus_profiles).
"""

from __future__ import annotations

import itertools
import statistics
from typing import Any

# Diatonic scale-degree sets as semitone offsets from the tonic.
_MAJOR = frozenset({0, 2, 4, 5, 7, 9, 11})
_MINOR = frozenset({0, 2, 3, 5, 7, 8, 10})  # natural + common raised 6/7 handled as chromatic

# Melodic interval buckets (absolute semitones).
_STEP = (1, 2)
_THIRD = (3, 4)
_LEAP = (5, 7)  # 4th–5th

# Note name → pitch class (handles #, b, -, double accidentals).
_PC_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _note_to_midi(name: str) -> int | None:
    """Parse a music21 nameWithOctave (e.g. 'Db4', 'F##5', 'Ab-1') → MIDI."""
    if not name or name[0] not in _PC_BASE:
        return None
    pc = _PC_BASE[name[0]]
    i = 1
    while i < len(name) and name[i] in "#b-":
        if name[i] == "#":
            pc += 1
        else:  # both 'b' and '-' are flats in music21 nameWithOctave
            pc -= 1
        i += 1
    octave_str = name[i:]
    try:
        octave = int(octave_str)
    except ValueError:
        return None
    return pc + 12 * (octave + 1)


def _rh_notes(bar: dict[str, Any]) -> list[dict[str, Any]]:
    return [e for e in bar.get("rh_display", []) if e.get("type") == "note"]


def _melody_notes(bar: dict[str, Any]) -> list[dict[str, Any]]:
    """The real top-voice melody (P1 `melody_line`); fall back to rh_display
    notes for un-reingested shards. Melodic metrics must measure the LINE, not
    the chord-soup of the whole staff."""
    line = bar.get("melody_line")
    if line:
        return [e for e in line if e.get("type") == "note"]
    return _rh_notes(bar)


def _all_events(bar: dict[str, Any]) -> list[dict[str, Any]]:
    return list(bar.get("rh_display", [])) + list(bar.get("lh_display", []))


def _scale_for(bar: dict[str, Any]) -> frozenset:
    return _MINOR if bar.get("key_mode") == "minor" else _MAJOR


# ─── Harmony ─────────────────────────────────────────────────────────────────


def harmonic_metrics(bars: list[dict[str, Any]]) -> dict[str, float]:
    """Chromaticism, chord vocabulary, vertical density, harmonic rhythm."""
    total_notes = chromatic_notes = 0
    chord_count = maj = minr = dim = aug = sevenths = 0
    chord_sizes: list[int] = []
    bass_changes: list[int] = []  # distinct LH bass pitch-classes per bar ≈ harmonic rhythm

    for bar in bars:
        scale = _scale_for(bar)
        # Chromaticism via interval_from_root (semitones above tonic).
        for e in _all_events(bar):
            if e.get("type") == "note":
                iv = e.get("interval_from_root")
                if iv is not None:
                    total_notes += 1
                    if iv % 12 not in scale:
                        chromatic_notes += 1
            elif e.get("type") == "chord":
                for iv in e.get("intervals", []):
                    total_notes += 1
                    if iv % 12 not in scale:
                        chromatic_notes += 1
        # Chord vocabulary from vertical sonorities.
        for e in _all_events(bar):
            if e.get("type") != "chord":
                continue
            pcs = sorted({iv % 12 for iv in e.get("intervals", [])})
            chord_count += 1
            chord_sizes.append(len(e.get("intervals", [])))
            quality = _classify_chord(pcs)
            if quality == "maj":
                maj += 1
            elif quality == "min":
                minr += 1
            elif quality == "dim":
                dim += 1
            elif quality == "aug":
                aug += 1
            if quality == "seventh":
                sevenths += 1
        # Harmonic rhythm proxy: how many distinct bass pitch-classes this bar.
        lh_pcs = {
            e.get("interval_from_root", 0) % 12
            for e in bar.get("lh_display", [])
            if e.get("type") in ("note", "chord")
        }
        if lh_pcs:
            bass_changes.append(len(lh_pcs))

    cc = max(chord_count, 1)
    return {
        "chromatic_ratio": round(chromatic_notes / max(total_notes, 1), 4),
        "chord_pct": round(chord_count / max(len(bars), 1), 4),  # chords per bar
        "maj_chord_ratio": round(maj / cc, 4),
        "min_chord_ratio": round(minr / cc, 4),
        "dim_aug_chord_ratio": round((dim + aug) / cc, 4),
        "seventh_chord_ratio": round(sevenths / cc, 4),
        "avg_chord_size": round(statistics.fmean(chord_sizes), 3) if chord_sizes else 0.0,
        "harmonic_rhythm": round(statistics.fmean(bass_changes), 3) if bass_changes else 0.0,
    }


def _classify_chord(pcs: list[int]) -> str:
    """Crude chord-quality label from pitch-class set (relative to its own root)."""
    if len(pcs) < 2:
        return "other"
    intervals = {(p - pcs[0]) % 12 for p in pcs}
    has_seventh = bool(intervals & {10, 11})
    if {4, 7} <= intervals:
        return "seventh" if has_seventh else "maj"
    if {3, 7} <= intervals:
        return "seventh" if has_seventh else "min"
    if {3, 6} <= intervals:
        return "dim"
    if {4, 8} <= intervals:
        return "aug"
    if has_seventh:
        return "seventh"
    return "other"


# ─── Melody ──────────────────────────────────────────────────────────────────


def melodic_metrics(bars: list[dict[str, Any]]) -> dict[str, float]:
    """Interval distribution, leap ratio, range, contour smoothness of the real
    top-voice melody line."""
    midis: list[int] = []
    for bar in bars:
        for e in _melody_notes(bar):
            m = e.get("midi")
            if m is None:
                m = _note_to_midi(e.get("pitch", ""))
            if m is not None:
                midis.append(m)

    if len(midis) < 2:
        return {
            "mean_abs_interval": 0.0,
            "step_ratio": 0.0,
            "third_ratio": 0.0,
            "leap_ratio": 0.0,
            "wide_leap_ratio": 0.0,
            "melodic_range": 0.0,
            "repeat_ratio": 0.0,
        }

    intervals = [abs(b - a) for a, b in itertools.pairwise(midis)]
    n = len(intervals)
    step = sum(1 for i in intervals if _STEP[0] <= i <= _STEP[1])
    third = sum(1 for i in intervals if _THIRD[0] <= i <= _THIRD[1])
    leap = sum(1 for i in intervals if _LEAP[0] <= i <= _LEAP[1])
    wide = sum(1 for i in intervals if i >= 8)
    repeat = sum(1 for i in intervals if i == 0)
    return {
        "mean_abs_interval": round(statistics.fmean(intervals), 3),
        "step_ratio": round(step / n, 4),
        "third_ratio": round(third / n, 4),
        "leap_ratio": round((leap + wide) / n, 4),
        "wide_leap_ratio": round(wide / n, 4),
        "melodic_range": float(max(midis) - min(midis)),
        "repeat_ratio": round(repeat / n, 4),
    }


# ─── Rhythm (note-value vocabulary) ──────────────────────────────────────────

_DUR_BUCKETS = {
    "sixteenth": (0.2, 0.3),
    "eighth": (0.45, 0.55),
    "dotted_eighth": (0.7, 0.8),
    "quarter": (0.95, 1.05),
    "dotted_quarter": (1.4, 1.6),
    "half": (1.9, 2.1),
    "whole": (3.5, 4.5),
}


def rhythmic_metrics(bars: list[dict[str, Any]]) -> dict[str, float]:
    """Distribution of note durations + triplet/syncopation proxies."""
    durs: list[float] = []
    triplet = 0
    for bar in bars:
        for e in _all_events(bar):
            d = e.get("dur")
            if d is None or e.get("type") == "rest":
                continue
            durs.append(float(d))
            frac = float(d) % 0.5
            if 0.1 < frac < 0.23 or 0.27 < frac < 0.4:  # ~triplet subdivisions
                triplet += 1
    if not durs:
        return dict.fromkeys([*list(_DUR_BUCKETS), "triplet_ratio", "dur_variety"], 0.0)
    n = len(durs)
    out: dict[str, float] = {}
    for name, (lo, hi) in _DUR_BUCKETS.items():
        out[f"{name}_ratio"] = round(sum(1 for d in durs if lo <= d <= hi) / n, 4)
    out["triplet_ratio"] = round(triplet / n, 4)
    out["dur_variety"] = float(len({round(d, 2) for d in durs}))
    return out


# ─── Combined fingerprint ────────────────────────────────────────────────────


def style_fingerprint(bars: list[dict[str, Any]]) -> dict[str, float]:
    """All dimensions in one flat dict of scalar features."""
    fp: dict[str, float] = {}
    fp.update(harmonic_metrics(bars))
    fp.update(melodic_metrics(bars))
    fp.update(rhythmic_metrics(bars))
    return fp


# Feature → human-readable dimension, for grouped reporting.
DIMENSIONS = {
    "harmony": [
        "chromatic_ratio",
        "chord_pct",
        "maj_chord_ratio",
        "min_chord_ratio",
        "dim_aug_chord_ratio",
        "seventh_chord_ratio",
        "avg_chord_size",
        "harmonic_rhythm",
    ],
    "melody": [
        "mean_abs_interval",
        "step_ratio",
        "third_ratio",
        "leap_ratio",
        "wide_leap_ratio",
        "melodic_range",
        "repeat_ratio",
    ],
    "rhythm": [
        "sixteenth_ratio",
        "eighth_ratio",
        "dotted_eighth_ratio",
        "quarter_ratio",
        "dotted_quarter_ratio",
        "half_ratio",
        "whole_ratio",
        "triplet_ratio",
        "dur_variety",
    ],
}

FINGERPRINT_FEATURES = [f for feats in DIMENSIONS.values() for f in feats]
