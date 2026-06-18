"""
Validator — physical constraint checking for SCALES.

Merges functionality from:
  - tools/v3/harmony_validator.py
  - tools/v3/playability_validator.py
  - tools/range_checker.py
  - tools/voice_leading_checker.py

Only enforces hard physical constraints (instrument ranges, hand spans,
meter integrity). Artistic guidance is handled by candidate_scorer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .duration import bar_duration, dur_to_beats
from .models import EventIR, LayerEvent, LayerIR, PhysicalConstraints
from .pitch import pitch_to_midi

# ─── Voice Ranges ────────────────────────────────────────────────────────────

INSTRUMENT_RANGES = {
    # Piano
    "solo_piano": (21, 108),
    "piano": (21, 108),
    # Strings
    "violin": (55, 103),
    "viola": (48, 91),
    "cello": (36, 76),
    "double_bass": (28, 67),
    # Woodwinds
    "flute": (60, 96),
    "oboe": (58, 91),
    "clarinet": (50, 91),
    "bassoon": (34, 75),
    # Brass
    "horn": (34, 77),
    "trumpet": (54, 82),
    "trombone": (40, 72),
    "tuba": (28, 58),
}


# ─── Validation Results ──────────────────────────────────────────────────────


@dataclass
class ValidationIssue:
    """A single validation issue."""

    severity: str = "error"  # error | warning
    category: str = ""  # range | meter | playability | voice_leading
    bar: Optional[int] = None
    beat: Optional[float] = None
    voice: Optional[str] = None
    message: str = ""
    auto_fixable: bool = False


@dataclass
class ValidationReport:
    """Complete validation report for a phrase or piece."""

    passed: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def add_error(
        self,
        category: str,
        message: str,
        bar: Optional[int] = None,
        beat: Optional[float] = None,
        voice: Optional[str] = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="error",
                category=category,
                bar=bar,
                beat=beat,
                voice=voice,
                message=message,
            )
        )
        self.passed = False

    def add_warning(
        self,
        category: str,
        message: str,
        bar: Optional[int] = None,
        beat: Optional[float] = None,
        voice: Optional[str] = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity="warning",
                category=category,
                bar=bar,
                beat=beat,
                voice=voice,
                message=message,
            )
        )

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


# ─── Range Validation ────────────────────────────────────────────────────────


def validate_range(
    events: List[LayerEvent],
    instrumentation: str = "solo_piano",
    constraints: Optional[PhysicalConstraints] = None,
) -> List[ValidationIssue]:
    """Check that all pitches are within instrument range."""
    issues = []
    low, high = INSTRUMENT_RANGES.get(instrumentation, (21, 108))
    if constraints:
        low = max(low, constraints.piano_low)
        high = min(high, constraints.piano_high)

    for event in events:
        if event.pitch == "rest" or isinstance(event.pitch, list):
            if isinstance(event.pitch, list):
                for p in event.pitch:
                    if p == "rest":
                        continue
                    midi = pitch_to_midi(p)
                    if midi is not None and (midi < low or midi > high):
                        issues.append(
                            ValidationIssue(
                                severity="error",
                                category="range",
                                bar=event.bar,
                                beat=event.beat,
                                message=f"Pitch {p} (MIDI {midi}) out of range [{low}, {high}]",
                            )
                        )
            continue
        midi = pitch_to_midi(event.pitch)
        if midi is not None and (midi < low or midi > high):
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="range",
                    bar=event.bar,
                    beat=event.beat,
                    message=f"Pitch {event.pitch} (MIDI {midi}) out of range [{low}, {high}]",
                )
            )

    return issues


# ─── Meter Validation ────────────────────────────────────────────────────────


def validate_meter(
    events: List[LayerEvent], meter: Tuple[int, int] = (4, 4), bar_count: int = 4
) -> List[ValidationIssue]:
    """Check that note durations sum correctly per bar."""
    issues = []
    expected_beats = bar_duration(meter)

    # Group events by bar
    bars: Dict[int, List[LayerEvent]] = {}
    for event in events:
        bars.setdefault(event.bar, []).append(event)

    for bar_num in range(1, bar_count + 1):
        bar_events = bars.get(bar_num, [])
        if not bar_events:
            continue

        # Grace notes take no metrical time (direct_compose does not advance
        # the beat cursor for them), so they must not count toward the bar sum.
        total = sum(dur_to_beats(e.duration) for e in bar_events if (e.ornament or "") != "grace")
        if abs(total - expected_beats) > 0.01:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="meter",
                    bar=bar_num,
                    message=f"Bar {bar_num}: duration sum {total:.2f} != expected {expected_beats:.2f}",
                )
            )

    return issues


# ─── Playability Validation (Piano) ──────────────────────────────────────────


def validate_playability(
    events: List[LayerEvent], hand: str = "rh", constraints: Optional[PhysicalConstraints] = None
) -> List[ValidationIssue]:
    """Check piano playability constraints (hand span, simultaneous notes)."""
    issues = []
    max_span = constraints.max_hand_span_semitones if constraints else 16
    max_notes = constraints.max_notes_per_hand if constraints else 5

    # Group simultaneous events (same bar + beat)
    simultaneous: Dict[Tuple[int, float], List[LayerEvent]] = {}
    for event in events:
        if event.pitch == "rest":
            continue
        key = (event.bar, event.beat)
        simultaneous.setdefault(key, []).append(event)

    for (bar, beat), group in simultaneous.items():
        # Check note count
        if len(group) > max_notes:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="playability",
                    bar=bar,
                    beat=beat,
                    voice=hand,
                    message=f"{hand} has {len(group)} simultaneous notes (max {max_notes})",
                )
            )

        # Check hand span
        midis = []
        for event in group:
            if isinstance(event.pitch, list):
                for p in event.pitch:
                    m = pitch_to_midi(p)
                    if m is not None:
                        midis.append(m)
            else:
                m = pitch_to_midi(event.pitch)
                if m is not None:
                    midis.append(m)

        if len(midis) >= 2:
            span = max(midis) - min(midis)
            if span > max_span:
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="playability",
                        bar=bar,
                        beat=beat,
                        voice=hand,
                        message=f"{hand} span {span} semitones exceeds max {max_span}",
                    )
                )

    return issues


# ─── Voice Leading Validation ────────────────────────────────────────────────


def validate_voice_leading(
    soprano_events: List[LayerEvent], bass_events: List[LayerEvent]
) -> List[ValidationIssue]:
    """Check for parallel fifths and octaves between outer voices."""
    issues = []

    # Build pitch sequences aligned by bar+beat
    soprano_seq = [
        (e.bar, e.beat, pitch_to_midi(e.pitch))
        for e in soprano_events
        if e.pitch != "rest" and not isinstance(e.pitch, list)
    ]
    bass_seq = [
        (e.bar, e.beat, pitch_to_midi(e.pitch))
        for e in bass_events
        if e.pitch != "rest" and not isinstance(e.pitch, list)
    ]

    if len(soprano_seq) < 2 or len(bass_seq) < 2:
        return issues

    # Align by matching bar+beat positions
    aligned = []
    s_idx, b_idx = 0, 0
    while s_idx < len(soprano_seq) and b_idx < len(bass_seq):
        s_bar, s_beat, s_midi = soprano_seq[s_idx]
        b_bar, b_beat, b_midi = bass_seq[b_idx]
        if (s_bar, s_beat) == (b_bar, b_beat):
            if s_midi is not None and b_midi is not None:
                aligned.append((s_bar, s_beat, s_midi, b_midi))
            s_idx += 1
            b_idx += 1
        elif (s_bar, s_beat) < (b_bar, b_beat):
            s_idx += 1
        else:
            b_idx += 1

    # Check consecutive aligned pairs
    for i in range(len(aligned) - 1):
        bar1, beat1, s1, b1 = aligned[i]
        bar2, beat2, s2, b2 = aligned[i + 1]
        interval1 = (s1 - b1) % 12
        interval2 = (s2 - b2) % 12

        # Parallel perfect fifths
        if interval1 == 7 and interval2 == 7 and s1 != s2:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="voice_leading",
                    bar=bar2,
                    beat=beat2,
                    message=f"Parallel 5ths: bar {bar1} beat {beat1} → bar {bar2} beat {beat2}",
                )
            )

        # Parallel octaves/unisons
        if interval1 == 0 and interval2 == 0 and s1 != s2:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="voice_leading",
                    bar=bar2,
                    beat=beat2,
                    message=f"Parallel octaves: bar {bar1} beat {beat1} → bar {bar2} beat {beat2}",
                )
            )

    return issues


# ─── Full Validation ─────────────────────────────────────────────────────────


def validate_layer_ir(
    layer_ir: LayerIR, constraints: Optional[PhysicalConstraints] = None
) -> ValidationReport:
    """Run all validators on a LayerIR."""
    report = ValidationReport()
    c = constraints or PhysicalConstraints()

    # Collect all events for range checking
    all_events = (
        layer_ir.principal_line
        + layer_ir.bass_foundation
        + layer_ir.response_layer
        + layer_ir.counter_reply
        + layer_ir.ornamental_surface
    )

    # Range
    for issue in validate_range(all_events, layer_ir.instrumentation, c):
        if issue.severity == "error":
            report.add_error(issue.category, issue.message, issue.bar, issue.beat)
        else:
            report.add_warning(issue.category, issue.message, issue.bar, issue.beat)

    # Meter (check each layer separately)
    for layer_name, events in [
        ("principal_line", layer_ir.principal_line),
        ("bass_foundation", layer_ir.bass_foundation),
    ]:
        if events:
            for issue in validate_meter(events, layer_ir.meter, layer_ir.bar_count):
                if issue.severity == "error":
                    report.add_error(
                        issue.category,
                        f"{layer_name}: {issue.message}",
                        issue.bar,
                        issue.beat,
                        layer_name,
                    )
                else:
                    report.add_warning(
                        issue.category,
                        f"{layer_name}: {issue.message}",
                        issue.bar,
                        issue.beat,
                        layer_name,
                    )

    # Playability (piano only)
    if layer_ir.instrumentation in ("solo_piano", "piano"):
        rh_events = layer_ir.principal_line + layer_ir.ornamental_surface
        lh_events = layer_ir.bass_foundation + layer_ir.response_layer

        for issue in validate_playability(rh_events, "rh", c):
            if issue.severity == "error":
                report.add_error(issue.category, issue.message, issue.bar, issue.beat, "rh")
            else:
                report.add_warning(issue.category, issue.message, issue.bar, issue.beat, "rh")

        for issue in validate_playability(lh_events, "lh", c):
            if issue.severity == "error":
                report.add_error(issue.category, issue.message, issue.bar, issue.beat, "lh")
            else:
                report.add_warning(issue.category, issue.message, issue.bar, issue.beat, "lh")

    # Voice leading (outer voices)
    if layer_ir.principal_line and layer_ir.bass_foundation:
        for issue in validate_voice_leading(layer_ir.principal_line, layer_ir.bass_foundation):
            if issue.severity == "error":
                report.add_error(issue.category, issue.message, issue.bar, issue.beat)
            else:
                report.add_warning(issue.category, issue.message, issue.bar, issue.beat)

    # Stats
    report.stats = {
        "total_events": len(all_events),
        "principal_events": len(layer_ir.principal_line),
        "bass_events": len(layer_ir.bass_foundation),
        "response_events": len(layer_ir.response_layer),
        "counter_events": len(layer_ir.counter_reply),
        "ornamental_events": len(layer_ir.ornamental_surface),
        "bar_count": layer_ir.bar_count,
    }

    return report


def validate_event_ir(
    events: List[EventIR],
    instrumentation: str = "solo_piano",
    meter: Tuple[int, int] = (4, 4),
    constraints: Optional[PhysicalConstraints] = None,
) -> ValidationReport:
    """Validate final EventIR stream."""
    report = ValidationReport()
    c = constraints or PhysicalConstraints()

    # Convert EventIR to LayerEvents for reuse
    layer_events = [
        LayerEvent(
            bar=e.bar,
            beat=e.beat,
            pitch=e.pitch,
            duration=e.duration,
            role=e.role,
        )
        for e in events
    ]

    for issue in validate_range(layer_events, instrumentation, c):
        if issue.severity == "error":
            report.add_error(issue.category, issue.message, issue.bar, issue.beat)
        else:
            report.add_warning(issue.category, issue.message, issue.bar, issue.beat)

    report.stats = {"total_events": len(events)}
    return report
