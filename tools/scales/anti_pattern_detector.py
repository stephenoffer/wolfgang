"""
AntiPatternDetector — 8 symbolic detectors for AI tells.

Each detector takes a LayerIR and returns (detected, severity, detail).
Run all detectors on a candidate to get an anti-pattern risk score.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .models import AntiPatternRule, LayerEvent, LayerIR, PhraseState
from .pitch import pitch_to_midi


def detect_flat_dynamics(layer: LayerIR, params: Optional[Dict] = None) -> Tuple[bool, str, str]:
    """All dynamics identical across bars → flat, lifeless music."""
    max_same_ratio = (params or {}).get("max_same_ratio", 0.8)
    dynamics = []
    for evt in layer.principal_line:
        if evt.dynamic:
            dynamics.append(evt.dynamic)

    if len(dynamics) < 2:
        return False, "warning", "Insufficient dynamics data"

    from collections import Counter

    counts = Counter(dynamics)
    most_common_count = counts.most_common(1)[0][1]
    ratio = most_common_count / len(dynamics)

    if ratio > max_same_ratio:
        return True, "warning", f"{ratio:.0%} of dynamics are '{counts.most_common(1)[0][0]}'"
    return False, "warning", ""


def detect_same_accompaniment(
    layer: LayerIR, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """LH pattern doesn't change across the phrase."""
    events = layer.response_layer
    if len(events) < 4:
        return False, "warning", "Insufficient accompaniment data"

    # Group events by bar, check if interval patterns repeat
    bars: Dict[int, List[int]] = {}
    for evt in events:
        if evt.pitch != "rest" and not isinstance(evt.pitch, list):
            try:
                midi = pitch_to_midi(evt.pitch)
                if midi is not None:
                    bars.setdefault(evt.bar, []).append(midi)
            except (ValueError, KeyError, TypeError):
                pass

    if len(bars) < 3:
        return False, "warning", ""

    # Check if all bars have identical interval patterns
    patterns = []
    for bar_num in sorted(bars.keys()):
        midis = bars[bar_num]
        if len(midis) >= 2:
            intervals = tuple(midis[i + 1] - midis[i] for i in range(len(midis) - 1))
            patterns.append(intervals)

    if len(patterns) < 3:
        return False, "warning", ""

    unique = set(patterns)
    repeat_ratio = 1.0 - (len(unique) / len(patterns))
    threshold = (params or {}).get("max_repeat_ratio", 0.6)

    if repeat_ratio > threshold:
        return True, "warning", f"{repeat_ratio:.0%} of bars have identical LH pattern"
    return False, "warning", ""


def detect_register_monotony(
    layer: LayerIR, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """A melody that never leaves a narrow band → boring register.

    Threshold measured, not guessed. Real Mozart four-bar phrases have a median
    melodic span of 15 semitones but a 10th percentile of 8, so the old
    "within one octave" test fired on 15% of them at phrase scale and on 39% of
    all real phrases across the corpus — a warning that flags two of every five
    real phrases is noise that drowns the signals worth reading. A span under a
    fifth is genuinely inert; an octave is just a normal phrase.
    """
    min_range = (params or {}).get("min_range_semitones", 7)
    midis = []
    for evt in layer.principal_line:
        if evt.pitch != "rest" and not isinstance(evt.pitch, list):
            try:
                m = pitch_to_midi(evt.pitch)
                if m is not None:
                    midis.append(m)
            except (ValueError, KeyError, TypeError):
                pass

    if len(midis) < 4:
        return False, "warning", "Insufficient melody data"

    pitch_range = max(midis) - min(midis)
    if pitch_range < min_range:
        return True, "warning", f"Melody range is only {pitch_range} semitones"
    return False, "warning", ""


def detect_missing_silence(layer: LayerIR, params: Optional[Dict] = None) -> Tuple[bool, str, str]:
    """Zero rests across all layers → music doesn't breathe."""
    min_bars = (params or {}).get("min_bars_for_check", 4)
    if layer.bar_count < min_bars:
        return False, "warning", ""

    all_events = (
        layer.principal_line
        + layer.bass_foundation
        + layer.response_layer
        + layer.counter_reply
        + layer.ornamental_surface
    )

    rest_count = sum(1 for evt in all_events if evt.pitch == "rest")
    if rest_count == 0:
        return (
            True,
            "warning",
            f"No rests in {len(all_events)} events across {layer.bar_count} bars",
        )
    return False, "warning", ""


def detect_ornament_wallpaper(
    layer: LayerIR, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """Ornaments at perfectly regular intervals → mechanical."""
    events = layer.ornamental_surface
    if len(events) < 3:
        return False, "warning", ""

    # Check spacing variance
    positions = [(evt.bar, evt.beat) for evt in events]
    if len(positions) < 3:
        return False, "warning", ""

    # Compute beat positions as absolute values
    abs_positions = [p[0] * 10 + p[1] for p in positions]
    gaps = [abs_positions[i + 1] - abs_positions[i] for i in range(len(abs_positions) - 1)]

    if not gaps:
        return False, "warning", ""

    avg = sum(gaps) / len(gaps)
    variance = sum((g - avg) ** 2 for g in gaps) / len(gaps)
    threshold = (params or {}).get("min_variance", 0.5)

    if variance < threshold:
        return True, "warning", f"Ornament spacing variance={variance:.2f} (too regular)"
    return False, "warning", ""


def detect_identical_restatement(
    layer: LayerIR, prev_layer: Optional[LayerIR] = None, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """Melody contour identical to previous phrase."""
    if prev_layer is None:
        return False, "warning", ""

    def contour(events: List[LayerEvent]) -> List[int]:
        midis = []
        for evt in events:
            if evt.pitch != "rest" and not isinstance(evt.pitch, list):
                try:
                    m = pitch_to_midi(evt.pitch)
                    if m is not None:
                        midis.append(m)
                except (ValueError, KeyError, TypeError):
                    pass
        if len(midis) < 2:
            return []
        return [
            1 if midis[i + 1] > midis[i] else -1 if midis[i + 1] < midis[i] else 0
            for i in range(len(midis) - 1)
        ]

    c1 = contour(layer.principal_line)
    c2 = contour(prev_layer.principal_line)

    if not c1 or not c2:
        return False, "warning", ""

    min_len = min(len(c1), len(c2))
    if min_len < 3:
        return False, "warning", ""

    matches = sum(1 for i in range(min_len) if c1[i] == c2[i])
    ratio = matches / min_len
    threshold = (params or {}).get("max_similarity", 0.9)

    if ratio > threshold:
        return True, "warning", f"Melody contour {ratio:.0%} identical to previous phrase"
    return False, "warning", ""


def detect_metronomic_rhythm(
    layer: LayerIR, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """All note durations identical → no rhythmic variety."""
    durations = []
    for evt in layer.principal_line + layer.response_layer:
        if evt.pitch != "rest":
            durations.append(evt.duration)

    if len(durations) < 4:
        return False, "warning", ""

    unique = set(durations)
    min_unique = (params or {}).get("min_unique_durations", 3)

    if len(unique) < min_unique:
        return True, "warning", f"Only {len(unique)} distinct duration(s): {unique}"
    return False, "warning", ""


def detect_root_position_bias(
    layer: LayerIR, params: Optional[Dict] = None
) -> Tuple[bool, str, str]:
    """Bass always on chord root → no inversions, static bass."""
    # This is a simplified check — would need harmonic analysis for full accuracy
    bass_events = layer.bass_foundation
    if len(bass_events) < 4:
        return False, "warning", ""

    # Check if bass pitches repeat the same pitch class too often
    pitch_classes = []
    for evt in bass_events:
        if evt.pitch != "rest" and not isinstance(evt.pitch, list):
            try:
                midi = pitch_to_midi(evt.pitch)
                if midi is not None:
                    pitch_classes.append(midi % 12)
            except (ValueError, KeyError, TypeError):
                pass

    if len(pitch_classes) < 4:
        return False, "warning", ""

    from collections import Counter

    counts = Counter(pitch_classes)
    most_common_ratio = counts.most_common(1)[0][1] / len(pitch_classes)
    threshold = (params or {}).get("max_root_ratio", 0.6)

    if most_common_ratio > threshold:
        return True, "warning", f"Bass pitch class repeats {most_common_ratio:.0%}"
    return False, "warning", ""


def detect_scalar_fill(layer: LayerIR, params: Optional[Dict] = None) -> Tuple[bool, str, str]:
    """Consecutive stepwise motion filling an octave+ without contour identity.

    Detects runs of 8+ notes in principal_line all moving by step (+-1 or +-2
    semitones) in the same direction — a telltale sign of mechanical scale
    filling rather than melodic composition.
    """
    min_run = (params or {}).get("min_run_length", 8)
    midis = []
    for evt in layer.principal_line:
        if evt.pitch != "rest" and not isinstance(evt.pitch, list):
            try:
                m = pitch_to_midi(evt.pitch)
                if m is not None:
                    midis.append(m)
            except (ValueError, KeyError, TypeError):
                pass

    if len(midis) < min_run:
        return False, "warning", ""

    # Look for runs of consecutive stepwise motion in the same direction
    run_length = 1
    for i in range(1, len(midis)):
        interval = midis[i] - midis[i - 1]
        if 1 <= abs(interval) <= 2:
            # Same direction as the run so far?
            if run_length == 1:
                direction = 1 if interval > 0 else -1
                run_length = 2
            elif (interval > 0 and direction > 0) or (interval < 0 and direction < 0):
                run_length += 1
            else:
                run_length = 2
                direction = 1 if interval > 0 else -1
        else:
            run_length = 1

        if run_length >= min_run:
            return (
                True,
                "warning",
                f"Scalar fill: {run_length} consecutive stepwise notes in same direction",
            )

    return False, "warning", ""


def detect_safe_harmony(layer: LayerIR, params: Optional[Dict] = None) -> Tuple[bool, str, str]:
    """Lack of harmonic variety — too few unique pitch classes in bass.

    For phrases longer than 4 bars, bass_foundation should use at least 3
    distinct pitch classes. Fewer indicates I-V shuttling or pedal-point
    monotony.
    """
    min_bars = (params or {}).get("min_bars", 4)
    min_pitch_classes = (params or {}).get("min_pitch_classes", 3)

    if layer.bar_count <= min_bars:
        return False, "warning", ""

    bass_events = layer.bass_foundation
    if not bass_events:
        return False, "warning", "No bass foundation events"

    pitch_classes: set = set()
    for evt in bass_events:
        if evt.pitch != "rest" and not isinstance(evt.pitch, list):
            try:
                midi = pitch_to_midi(evt.pitch)
                if midi is not None:
                    pitch_classes.add(midi % 12)
            except (ValueError, KeyError, TypeError):
                pass

    if len(pitch_classes) < min_pitch_classes:
        return (
            True,
            "warning",
            f"Only {len(pitch_classes)} unique bass pitch class(es) across {layer.bar_count} bars",
        )

    return False, "warning", ""


# ─── Runner ────────────────────────────────────────────────────────────────

_DETECTORS = {
    "flat_dynamics": detect_flat_dynamics,
    "same_accompaniment": detect_same_accompaniment,
    "register_monotony": detect_register_monotony,
    "missing_silence": detect_missing_silence,
    "ornament_wallpaper": detect_ornament_wallpaper,
    "metronomic_rhythm": detect_metronomic_rhythm,
    "root_position_bias": detect_root_position_bias,
    "scalar_fill": detect_scalar_fill,
    "safe_harmony": detect_safe_harmony,
}


def run_all_detectors(
    layer: LayerIR,
    anti_patterns: Optional[List[AntiPatternRule]] = None,
    prev_layer: Optional[LayerIR] = None,
) -> List[Dict]:
    """Run all applicable detectors on a LayerIR.

    Returns list of {rule_id, name, detected, severity, detail} dicts.
    """
    results: List[Dict] = []

    # Run built-in detectors
    for det_name, det_func in _DETECTORS.items():
        params = {}
        rule_id = det_name
        if anti_patterns:
            for ap in anti_patterns:
                if ap.detector == det_name:
                    params = ap.params
                    rule_id = ap.id
                    break

        detected, severity, detail = det_func(layer, params)
        results.append(
            {
                "rule_id": rule_id,
                "name": det_name,
                "detected": detected,
                "severity": severity,
                "detail": detail,
            }
        )

    # Run identical restatement (needs prev_layer)
    detected, severity, detail = detect_identical_restatement(layer, prev_layer)
    results.append(
        {
            "rule_id": "identical_restatement",
            "name": "identical_restatement",
            "detected": detected,
            "severity": severity,
            "detail": detail,
        }
    )

    return results


def run_full_piece_review(
    phrase_states: Dict[str, PhraseState],
    anti_patterns: Optional[List[AntiPatternRule]] = None,
) -> Dict[str, List[Dict]]:
    """Run all detectors across every realized phrase in the piece.

    Iterates phrases in sorted order so that each phrase has proper
    prev_layer context from the preceding phrase.

    Returns a dict mapping phrase_id → list of detector result dicts.
    """
    per_phrase: Dict[str, List[Dict]] = {}
    prev_layer: Optional[LayerIR] = None

    for phrase_id in sorted(phrase_states.keys()):
        state = phrase_states[phrase_id]
        layer = state.realized
        if layer is None:
            per_phrase[phrase_id] = []
            continue

        results = run_all_detectors(layer, anti_patterns, prev_layer)
        per_phrase[phrase_id] = results
        prev_layer = layer

    return per_phrase
