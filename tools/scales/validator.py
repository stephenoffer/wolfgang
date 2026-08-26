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
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from .duration import bar_duration, dur_to_beats, is_grace
from .models import EventIR, LayerEvent, LayerIR, PhysicalConstraints
from .pitch import pitch_to_midi

# ─── Voice Ranges ────────────────────────────────────────────────────────────

# Written-pitch ranges in MIDI numbers (sounding pitch for the non-transposing
# instruments; transposing parts are notated by the orchestration planner at
# sounding pitch and these bounds are the sounding limits). An instrument missing
# from this table used to fall back to the full PIANO range (21-108), which let
# the orchestration planner write a piccolo down to A0 and a tuba up to C8 with
# nothing flagging it — so the table now covers the standard orchestra.
INSTRUMENT_RANGES = {
    # Keyboard
    "solo_piano": (21, 108),
    "piano": (21, 108),
    "celesta": (60, 108),
    "harpsichord": (29, 89),
    "organ": (24, 96),
    "harp": (24, 104),
    # Strings
    "violin": (55, 103),
    "viola": (48, 91),
    "cello": (36, 81),  # C2-A5: thumb position is ordinary writing, not extended
    "double_bass": (28, 67),
    # Woodwinds
    "piccolo": (74, 108),
    "flute": (60, 96),
    "alto_flute": (55, 91),
    "oboe": (58, 91),
    "english_horn": (52, 84),
    "clarinet": (50, 91),
    "bass_clarinet": (38, 79),
    "bassoon": (34, 75),
    "contrabassoon": (22, 63),
    "soprano_sax": (58, 89),
    "alto_sax": (49, 84),
    "tenor_sax": (44, 79),
    "baritone_sax": (37, 72),
    # Brass
    "horn": (34, 77),
    "trumpet": (52, 84),  # E3-C6 sounding: written F#3 on a B-flat trumpet sounds E3
    "piccolo_trumpet": (60, 89),
    "cornet": (52, 84),  # same instrument family as the trumpet, same sounding floor
    "trombone": (40, 72),
    "bass_trombone": (34, 67),
    "tuba": (26, 65),  # D1-F4: the old top of B-flat3 excluded the whole tenor register
    "euphonium": (34, 72),
    # Voices
    "soprano": (60, 81),
    "mezzo_soprano": (57, 79),
    "alto": (53, 76),
    "tenor": (48, 72),
    "baritone": (45, 69),
    "bass": (40, 64),
    # Pitched percussion
    "timpani": (36, 60),  # a modern five-drum set reaches C4
    "glockenspiel": (79, 108),
    "xylophone": (65, 108),  # sounds an octave above written; the old top clipped that octave
    "marimba": (45, 96),
    "vibraphone": (53, 89),
    "tubular_bells": (60, 77),
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
    events: List[LayerEvent],
    meter: Tuple[int, int] = (4, 4),
    bar_count: int = 4,
    pickup_bar: Optional[int] = None,
) -> List[ValidationIssue]:
    """Check that note durations sum correctly per bar.

    Iterates the bars that actually CARRY EVENTS. LayerEvents hold absolute bar
    numbers (a phrase starting at bar 17 has events in bars 17-24), so the old
    ``range(1, bar_count + 1)`` loop found nothing for any phrase but the first
    and the check silently passed everything — mis-metered bars reached the score
    unchallenged for every phrase after bar 1.

    An overfull bar is an error (it cannot be engraved as written). An underfull
    bar is a warning: it may be a deliberate rest at the end of the bar, but it
    is just as often a truncated exemplar copied one beat short.
    """
    issues = []
    expected_beats = bar_duration(meter)

    # Group events by bar
    bars: Dict[int, List[LayerEvent]] = {}
    for event in events:
        bars.setdefault(event.bar, []).append(event)

    for bar_num in sorted(bars):
        bar_events = bars[bar_num]
        if not bar_events:
            continue
        if pickup_bar is not None and bar_num == pickup_bar:
            continue  # an anacrusis is a partial measure by definition

        # Grace notes take no metrical time (direct_compose does not advance
        # the beat cursor for them), so they must not count toward the bar sum.
        total = sum(dur_to_beats(e.duration) for e in bar_events if not is_grace(e.ornament))
        if total > expected_beats + Fraction(1, 1000):
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="meter",
                    bar=bar_num,
                    message=(
                        f"Bar {bar_num}: duration sum {float(total):.4g} exceeds the "
                        f"{meter[0]}/{meter[1]} bar ({float(expected_beats):g} beats)"
                    ),
                )
            )
        elif total < expected_beats - Fraction(1, 1000):
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="meter",
                    bar=bar_num,
                    message=(
                        f"Bar {bar_num}: duration sum {float(total):.4g} is short of the "
                        f"{meter[0]}/{meter[1]} bar ({float(expected_beats):g} beats) — "
                        f"write the remainder as a rest if the silence is intended"
                    ),
                )
            )

        issues.extend(_overlap_issues(bar_num, bar_events))

    return issues


def _overlap_issues(bar_num: int, bar_events: List[LayerEvent]) -> List[ValidationIssue]:
    """Notes in ONE voice that sound while the previous one is still sounding.

    A single voice cannot play two notes at once, and the bar-sum check cannot
    see this: two half notes at beats 1 and 1.5 sum to 4 in a 4/4 bar and pass,
    while overlapping by a beat and a half. MusicXML has no way to write it, so
    the exporter serializes it without a backup and the bar spills past the
    barline — the defect this project has shipped more than once. CLAUDE.md has
    listed same-voice overlap as an enforced physical constraint for some time;
    it was not enforced anywhere.
    """
    issues: List[ValidationIssue] = []
    ordered = sorted(
        (e for e in bar_events if not is_grace(e.ornament)),
        key=lambda e: (Fraction(str(e.beat)).limit_denominator(96), str(e.pitch)),
    )
    prev_end = None
    prev = None
    for e in ordered:
        start = Fraction(str(e.beat)).limit_denominator(96)
        end = start + dur_to_beats(e.duration)
        if prev_end is not None and start < prev_end - Fraction(1, 1000):
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="meter",
                    bar=bar_num,
                    beat=float(start),
                    message=(
                        f"Bar {bar_num}: {e.pitch}{e.duration} starts at beat "
                        f"{float(start):g} while {prev.pitch}{prev.duration} is still "
                        f"sounding (ends at beat {float(prev_end):g}) — one voice "
                        f"cannot play both. Use '//' to write a second voice, or "
                        f"shorten the first note."
                    ),
                )
            )
            break  # one report per bar is enough to act on
        if prev_end is None or end > prev_end:
            prev_end, prev = end, e
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


def _sounding_outer_voices(layers, at):
    """(lowest, highest) MIDI sounding at time ``at`` across all given layers."""
    from .duration import dur_to_beats

    low = high = None
    for events in layers:
        for e in events or []:
            if e.pitch == "rest":
                continue
            start = (e.bar, float(e.beat))
            end_beat = float(e.beat) + float(dur_to_beats(e.duration))
            if start[0] != at[0]:
                continue
            if not (float(e.beat) <= at[1] + 1e-6 < end_beat - 1e-9):
                continue
            names = e.pitch if isinstance(e.pitch, list) else [e.pitch]
            for nm in names:
                m = pitch_to_midi(nm)
                if m is None:
                    continue
                low = m if low is None else min(low, m)
                high = m if high is None else max(high, m)
    return low, high


def validate_voice_leading(soprano_events, bass_events, all_layers=None):
    """Parallel fifths and octaves between the OUTER SOUNDING voices.

    Samples at every attack and takes the highest and lowest pitches actually
    sounding, rather than pairing notes that share an exact (bar, beat). The old
    version compared ``principal_line`` against ``bass_foundation`` at identical
    onsets only, which is a handful of moments per piece once the two hands have
    independent rhythms — and it was comparing against a bass_foundation that
    (before the layer-split fix) held one note per bar.

    Warning-level: real music contains parallel fifths, and this must never
    block. It exists so the critic can see them.
    """
    issues: List[ValidationIssue] = []
    layers = all_layers if all_layers is not None else [soprano_events, bass_events]

    # Sample at every attack in any layer.
    points = sorted(
        {
            (e.bar, round(float(e.beat), 4))
            for events in layers
            for e in (events or [])
            if e.pitch != "rest"
        }
    )
    samples = []
    for at in points:
        low, high = _sounding_outer_voices(layers, at)
        if low is not None and high is not None and low != high:
            samples.append((at, low, high))

    for (at1, lo1, hi1), (at2, lo2, hi2) in zip(samples, samples[1:]):
        if (lo1, hi1) == (lo2, hi2):
            continue  # nothing moved
        iv1, iv2 = (hi1 - lo1) % 12, (hi2 - lo2) % 12
        if iv1 != iv2 or iv1 not in (0, 7):
            continue
        # both voices must actually move, in the same direction
        if hi1 == hi2 or lo1 == lo2:
            continue
        if (hi2 - hi1) * (lo2 - lo1) <= 0:
            continue
        kind = "octaves/unisons" if iv1 == 0 else "5ths"
        issues.append(
            ValidationIssue(
                severity="warning",
                category="voice_leading",
                bar=at2[0],
                beat=at2[1],
                message=(
                    f"Parallel {kind} between the outer voices: bar {at1[0]} beat {at1[1]:g} "
                    f"→ bar {at2[0]} beat {at2[1]:g}"
                ),
            )
        )
    return issues


# ─── Full Validation ─────────────────────────────────────────────────────────


def validate_tempo(tempo_bpm, constraints: Optional[PhysicalConstraints] = None):
    """A tempo a player could actually take.

    `PhysicalConstraints` has carried `min_tempo_bpm = 40` and
    `max_tempo_bpm = 200` since the model was written and NOTHING has ever read
    either. They are physical facts, not artistic preferences — below about 40
    the pulse stops being felt as a pulse, and above about 200 a quarter-note
    beat is no longer a beat anyone conducts. A planner that produces a tempo
    outside them has made an arithmetic mistake, not a bold choice, and the
    piece is unplayable at the marked speed either way.

    A warning rather than an error: the marking can be honoured by re-reading
    the beat (a "quarter = 240" is a half = 120), so this names the problem
    without refusing the music.
    """
    issues: List[ValidationIssue] = []
    c = constraints or PhysicalConstraints()
    try:
        bpm = float(tempo_bpm)
    except (TypeError, ValueError):
        return issues
    if bpm <= 0:
        issues.append(
            ValidationIssue(
                severity="error",
                category="tempo",
                message=f"tempo of {tempo_bpm} is not a speed",
            )
        )
        return issues
    if bpm < c.min_tempo_bpm:
        issues.append(
            ValidationIssue(
                severity="warning",
                category="tempo",
                message=(
                    f"tempo {bpm:g} is below {c.min_tempo_bpm} — slower than a pulse can be "
                    f"felt. If this is meant to be slow, mark it in a longer beat "
                    f"(a quarter = {bpm:g} is an eighth = {bpm * 2:g})."
                ),
            )
        )
    elif bpm > c.max_tempo_bpm:
        issues.append(
            ValidationIssue(
                severity="warning",
                category="tempo",
                message=(
                    f"tempo {bpm:g} is above {c.max_tempo_bpm} — faster than a quarter-note "
                    f"beat is conducted. If this is meant to be fast, mark it in a shorter "
                    f"beat (a quarter = {bpm:g} is a half = {bpm / 2:g})."
                ),
            )
        )
    return issues


def validate_layer_ir(
    layer_ir: LayerIR, constraints: Optional[PhysicalConstraints] = None
) -> ValidationReport:
    """Run all validators on a LayerIR."""
    report = ValidationReport()
    c = constraints or PhysicalConstraints()

    # Collect all events for range checking
    extra = [e for evs in (getattr(layer_ir, "inner_voices", None) or {}).values() for e in evs]
    all_events = (
        layer_ir.principal_line
        + layer_ir.bass_foundation
        + layer_ir.response_layer
        + layer_ir.counter_reply
        + layer_ir.ornamental_surface
        + extra
    )

    # Range
    for issue in validate_range(all_events, layer_ir.instrumentation, c):
        if issue.severity == "error":
            report.add_error(issue.category, issue.message, issue.bar, issue.beat)
        else:
            report.add_warning(issue.category, issue.message, issue.bar, issue.beat)

    # Meter — each independent VOICE must fill the bar on its own. principal_line
    # and bass_foundation are voice 1 of each staff; counter_reply is the RH inner
    # voice (treble voice 2, from '//' multi-voice writing). response_layer is left
    # lenient: it doubles as the pedal-under-figuration tail, which re-anchors.
    pickup_bar = None
    if getattr(layer_ir, "pickup_beats", 0):
        all_bars = [e.bar for e in all_events]
        pickup_bar = min(all_bars) if all_bars else None
    for layer_name, events in [
        ("principal_line", layer_ir.principal_line),
        ("bass_foundation", layer_ir.bass_foundation),
        ("counter_reply", layer_ir.counter_reply),
        # Each additional independent voice must fill its bar on its own too.
        *sorted((getattr(layer_ir, "inner_voices", None) or {}).items()),
    ]:
        if events:
            for issue in validate_meter(
                events, layer_ir.meter, layer_ir.bar_count, pickup_bar=pickup_bar
            ):
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
        inner = getattr(layer_ir, "inner_voices", None) or {}
        rh_events = (
            layer_ir.principal_line
            + layer_ir.ornamental_surface
            + layer_ir.counter_reply
            + [e for k, v in inner.items() if k.startswith("treble") for e in v]
        )
        lh_events = (
            layer_ir.bass_foundation
            + layer_ir.response_layer
            + [e for k, v in inner.items() if k.startswith("bass") for e in v]
        )

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

    # Voice leading between the outer SOUNDING voices, across every layer.
    if layer_ir.principal_line and layer_ir.bass_foundation:
        for issue in validate_voice_leading(
            layer_ir.principal_line,
            layer_ir.bass_foundation,
            all_layers=[
                layer_ir.principal_line,
                layer_ir.counter_reply,
                layer_ir.ornamental_surface,
                layer_ir.response_layer,
                layer_ir.bass_foundation,
            ],
        ):
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
