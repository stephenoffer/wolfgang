"""Per-style performance parameters — how a period is PLAYED, not just written.

A single `StylePerfProfile` carries the constants every performance workstream
reads (velocity shaping, rubato, swing, pedal, articulation, ensemble timing,
per-layer voicing balance). Resolving by historical period (baroque / classical
/ romantic / …) means a Bach fugue is played with light pedal and crisp
inégalité while a Chopin nocturne breathes with deep rubato and a singing top
voice — instead of one hardcoded constant set for everyone.

Deterministic and dependency-light: no music21, no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class StylePerfProfile:
    """Performance-practice constants for one period. Defaults = classical."""

    period: str = "classical"

    # Tempo / timing
    rubato_depth: float = 0.06  # max tempo deviation fraction in arcs
    rubato_shape: str = "s_curve"  # curve kind for rubato windows
    tempo_arc_depth: float = 0.04  # section-level accel/release fraction
    swing_ratio: float = 0.0  # 0 = even; 0.2 ≈ gentle long-short eighths
    inegalite_strength: float = 0.0  # period inégalité applied to eighth pairs
    upbeat_lean_ms: float = 6.0  # anticipation on weak-beat upbeats
    downbeat_stress_ms: float = 4.0  # slight delay + weight on downbeats

    # Velocity
    velocity_curve_kind: str = "s_curve"  # hairpin shaping
    dissonance_emphasis: float = 0.06  # leading-tone / suspension boost fraction
    repeated_note_variance: float = 4.0  # ± MIDI on consecutive same-pitch notes
    micro_velocity_jitter: float = 2.0  # ± MIDI everywhere (kills flat passages)
    held_note_decay: float = 0.04  # velocity droop fraction on long values
    velocity_floor: int = 24
    velocity_ceiling: int = 127

    # Articulation → MIDI
    staccato_gate: float = 0.5  # duration multiplier for staccato
    accent_boost: float = 0.18  # attack velocity boost fraction
    tenuto_extend: float = 0.12  # duration stretch fraction for tenuto

    # Pedal
    pedal_lead_ms: float = 30.0  # release this far before a chord change

    # Ensemble / hands
    ensemble_spread_ms: float = 12.0  # spread of simultaneous chord attacks
    hand_offset_ms: float = 6.0  # bass-vs-treble onset offset

    # Per-layer voicing balance (velocity multipliers by source_layer)
    voicing_balance: Dict[str, float] = field(
        default_factory=lambda: {
            "principal_line": 1.12,
            "counter_reply": 1.04,
            "bass_foundation": 1.0,
            "response_layer": 0.94,
            "ornamental_surface": 0.9,
        }
    )


# ─── Period presets ──────────────────────────────────────────────────────────

_BAROQUE = StylePerfProfile(
    period="baroque",
    rubato_depth=0.025,
    rubato_shape="linear",
    tempo_arc_depth=0.02,
    swing_ratio=0.0,
    inegalite_strength=0.22,  # notes inégales
    upbeat_lean_ms=4.0,
    downbeat_stress_ms=3.0,
    velocity_curve_kind="linear",
    dissonance_emphasis=0.05,
    repeated_note_variance=3.0,
    micro_velocity_jitter=1.5,
    held_note_decay=0.03,
    staccato_gate=0.55,
    accent_boost=0.12,
    tenuto_extend=0.08,
    pedal_lead_ms=0.0,  # harpsichord idiom: ~no pedal
    ensemble_spread_ms=8.0,
    hand_offset_ms=4.0,
    voicing_balance={
        "principal_line": 1.08,
        "counter_reply": 1.06,
        "bass_foundation": 1.04,
        "response_layer": 0.96,
        "ornamental_surface": 0.92,
    },
)

_CLASSICAL = StylePerfProfile(period="classical")  # all defaults

_ROMANTIC = StylePerfProfile(
    period="romantic",
    rubato_depth=0.11,
    rubato_shape="s_curve",
    tempo_arc_depth=0.07,
    swing_ratio=0.0,
    inegalite_strength=0.05,
    upbeat_lean_ms=9.0,
    downbeat_stress_ms=6.0,
    velocity_curve_kind="exp",
    dissonance_emphasis=0.09,
    repeated_note_variance=5.0,
    micro_velocity_jitter=2.5,
    held_note_decay=0.05,
    staccato_gate=0.55,
    accent_boost=0.2,
    tenuto_extend=0.15,
    pedal_lead_ms=40.0,
    ensemble_spread_ms=16.0,
    hand_offset_ms=10.0,
    voicing_balance={
        "principal_line": 1.16,
        "counter_reply": 1.05,
        "bass_foundation": 1.02,
        "response_layer": 0.9,
        "ornamental_surface": 0.86,
    },
)

# A few later periods lean romantic for performance practice.
_PERIOD_PROFILES: Dict[str, StylePerfProfile] = {
    "renaissance": _BAROQUE,
    "baroque": _BAROQUE,
    "classical": _CLASSICAL,
    "romantic": _ROMANTIC,
    "late-romantic": _ROMANTIC,
    "impressionist": _ROMANTIC,
    "nationalistic": _ROMANTIC,
    "modern": _CLASSICAL,
    "minimalist": _CLASSICAL,
    "film-score": _ROMANTIC,
}


def profile_for_period(period: Optional[str]) -> StylePerfProfile:
    """Profile for a period name (synonyms resolved). Defaults to classical."""
    if not period:
        return _CLASSICAL
    p = str(period).strip().lower()
    return _PERIOD_PROFILES.get(p, _CLASSICAL)


def profile_for_composer(composer_or_style: Optional[str]) -> StylePerfProfile:
    """Resolve a composer or style reference to its period's performance profile.

    Uses style_registry so 'mozart'/'classical'/'galant' all map to classical,
    'chopin'/'romantic' to romantic, 'bach'/'baroque' to baroque, etc. Honest
    fallback to classical when unknown (never silently mis-styled).
    """
    if not composer_or_style:
        return _CLASSICAL
    ref = str(composer_or_style).strip().lower()
    try:
        from .style_registry import _STYLE_MEMBERS, _SYNONYMS
    except Exception:
        return _CLASSICAL
    # direct style name or synonym
    if ref in _STYLE_MEMBERS:
        return profile_for_period(ref)
    if ref in _SYNONYMS:
        return profile_for_period(_SYNONYMS[ref])
    if ref.startswith("style__"):
        return profile_for_period(ref[len("style__") :])
    # composer name -> owning period
    for period, members in _STYLE_MEMBERS.items():
        if ref in members:
            return profile_for_period(period)
    return _CLASSICAL
