"""
PerformanceRenderer — populate PerformanceIR and humanize playback.

Bridges the (previously orphaned) PerformanceIR model and PerformanceBank
templates into something audible: interpolated velocity curves, cadential
rubato, per-bar sustain pedal, melody voicing emphasis, and gentle
microtiming. Everything here is deterministic — same phrase in, same
performance out — so renders are reproducible.

Split of responsibilities (by design):
- Continuous/expressive (velocity interpolation, microtiming, rubato
  tempo bends, audible sustain) → MIDI preview only, via midi_renderer.
- Discrete/notational (pedal marks, rit. text) → can also go to the
  score; pedal marks are emitted by midi_renderer's notation hook.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from .models import (
    DynamicPoint,
    PedalEvent,
    PerformanceIR,
    RubatoWindow,
    TimingOffset,
    VoicingEmphasis,
)
from .performance_params import StylePerfProfile, profile_for_period
from .performance_util import shape

_DYN_VELOCITY = {
    "ppp": 28,
    "pp": 40,
    "p": 55,
    "mp": 65,
    "mf": 80,
    "f": 100,
    "ff": 115,
    "fff": 127,
    "sfz": 110,
    "fp": 90,
}

_DEFAULT_VELOCITY = 80


def _beats_per_bar(meter: Tuple[int, int]) -> float:
    return meter[0] * 4.0 / meter[1]


def build_performance_ir(
    layer,
    slot=None,
    phrase_type: Optional[str] = None,
    profile: Optional[StylePerfProfile] = None,
    narrative_section=None,
    neighbor_slots: Optional[Tuple] = None,
    breath_points: Optional[Sequence[Tuple[int, float]]] = None,
) -> PerformanceIR:
    """Derive a PerformanceIR for one phrase from its notes, slot, and the
    period's performance profile.

    Uses PerformanceBank templates for the cadential shape; hairpins are shaped
    by the profile's velocity curve; pedal follows the harmonic rhythm; breath
    points lift the pedal and seed a micro-stretch. ``profile`` (period-resolved
    performance practice), ``narrative_section`` (for tempo arcs, WS-TEMPO), and
    ``neighbor_slots`` (cross-phrase continuity) are optional/defaulted so older
    callers keep working.
    """
    if profile is None:
        profile = profile_for_period(None)  # classical default
    perf = PerformanceIR(phrase_id=getattr(layer, "phrase_id", ""))
    meter = tuple(getattr(layer, "meter", (4, 4)) or (4, 4))
    bpb = _beats_per_bar(meter)

    all_events = sorted(
        (
            layer.principal_line
            + layer.bass_foundation
            + layer.response_layer
            + layer.counter_reply
            + layer.ornamental_surface
        ),
        key=lambda e: (e.bar, e.beat),
    )
    if not all_events:
        return perf
    first_bar = min(e.bar for e in all_events)
    last_bar = max(e.bar for e in all_events)

    # ── Dynamic curve: anchor points at every explicit dynamic ──
    seen_points = set()
    for e in all_events:
        if e.dynamic and (e.bar, round(e.beat, 2)) not in seen_points:
            perf.dynamic_curve.append(
                DynamicPoint(
                    bar=e.bar, beat=e.beat, velocity=_DYN_VELOCITY.get(e.dynamic, _DEFAULT_VELOCITY)
                )
            )
            seen_points.add((e.bar, round(e.beat, 2)))
    # Hairpins refine the curve: a cresc/dim start with no explicit end
    # dynamic gets a +/-12 velocity target at the stop point
    open_hp: Optional[Tuple[str, int, float]] = None
    for e in all_events:
        hp = getattr(e, "hairpin", None) or ""
        if hp.startswith("cresc") and hp != "cresc_stop":
            open_hp = ("cresc", e.bar, e.beat)
        elif hp.startswith("dim") and hp != "dim_stop":
            open_hp = ("dim", e.bar, e.beat)
        elif hp in ("stop", "!", "cresc_stop", "dim_stop") and open_hp:
            kind, b0, beat0 = open_hp
            base = velocity_at(perf, b0, beat0, bpb)
            # Delta scales with hairpin span (a long swell goes further) and the
            # curve is shaped by the profile (slow-fast romantic vs even baroque)
            # by inserting intermediate points along the span.
            span_beats = max(0.5, ((e.bar - b0) * bpb + (e.beat - beat0)))
            mag = max(8, min(28, int(8 + span_beats * 2)))
            delta = mag if kind == "cresc" else -mag
            n_mid = 3
            for k in range(1, n_mid + 1):
                frac = k / n_mid
                shaped = shape(frac, profile.velocity_curve_kind)
                mb = b0 + int((beat0 - 1.0 + frac * span_beats) // bpb)
                mbeat = 1.0 + ((beat0 - 1.0 + frac * span_beats) % bpb)
                if (mb, round(mbeat, 2)) in seen_points:
                    continue
                vel = max(20, min(127, int(round(base + delta * shaped))))
                perf.dynamic_curve.append(DynamicPoint(bar=mb, beat=mbeat, velocity=vel))
                seen_points.add((mb, round(mbeat, 2)))
            open_hp = None
    perf.dynamic_curve.sort(key=lambda p: (p.bar, p.beat))

    # ── Tempo arc + cadential rubato (one unified window over the phrase) ──
    # A real performance pushes through rising tension and broadens at the
    # cadence — instead of a metronome that only slows the final bar. The arc
    # is driven by the narrative-fed per-bar tension/energy curve (C1), shaped
    # by the period's rubato depth; the final bar gets an additional broadening
    # when the phrase cadences. All factors are tempo MULTIPLIERS (<1 = slower).
    cadence_target = getattr(slot, "cadence_target", None) if slot else None
    is_cadential = cadence_target not in (None, "", "none")
    n_bars = last_bar - first_bar + 1
    curves = getattr(slot, "curves", None) if slot else None
    tension = (list(getattr(curves, "tension", []) or
                    getattr(curves, "energy", []) or []) if curves else [])
    if narrative_section is not None and getattr(narrative_section, "tension_curve", None):
        tension = list(narrative_section.tension_curve)
    depth = profile.tempo_arc_depth
    arc: List[float] = []
    for i in range(n_bars):
        if tension:
            # sample the (possibly differently-sized) curve across the phrase
            frac = i / max(1, n_bars - 1)
            idx = min(len(tension) - 1, int(round(frac * (len(tension) - 1))))
            t_norm = max(0.0, min(1.0, float(tension[idx])))
        else:
            t_norm = 0.5
        # high tension → push (faster); low → relax (slower)
        arc.append(1.0 + depth * (2.0 * t_norm - 1.0))
    if is_cadential or phrase_type == "cadence_approach":
        # broaden the final bar (ritardando into the cadence), on top of the arc
        if arc:
            arc[-1] = min(arc[-1], 1.0) * 0.90
    if arc and (is_cadential or any(abs(f - 1.0) > 0.005 for f in arc)):
        perf.rubato_windows.append(
            RubatoWindow(bar_start=first_bar, bar_end=last_bar, curve=arc)
        )

    # ── Pedal: follow the harmonic rhythm, releasing just before each chord
    #    change (pedal_lead) to clear blur; fall back to per-bar with no plan.
    #    A breath bar lifts the pedal. ──
    lh_bars = sorted(
        {e.bar for e in layer.bass_foundation + layer.response_layer if e.pitch != "rest"}
    )
    breath_bars = {b for (b, _bt) in (breath_points or [])}
    harmony_plan = list(getattr(slot, "harmony_plan", []) or []) if slot else []
    pedal_lead_beats = (profile.pedal_lead_ms / 1000.0) * 2.0  # ms→~beats at moderate tempo
    if harmony_plan and lh_bars:
        i = 0
        while i < len(harmony_plan):
            chord = harmony_plan[i]
            j = i
            while j + 1 < len(harmony_plan) and harmony_plan[j + 1] == chord:
                j += 1
            down_bar, up_bar = first_bar + i, first_bar + j
            if down_bar in lh_bars and down_bar not in breath_bars:
                perf.pedal_events.append(
                    PedalEvent(bar=down_bar, beat=1.0, type="sustain", action="down")
                )
                up_beat = max(1.0, bpb + 0.95 - pedal_lead_beats)
                perf.pedal_events.append(
                    PedalEvent(bar=up_bar, beat=up_beat, type="sustain", action="up")
                )
            i = j + 1
    else:
        for bar in lh_bars:
            if bar in breath_bars:
                continue
            perf.pedal_events.append(PedalEvent(bar=bar, beat=1.0, type="sustain", action="down"))
            up_beat = max(1.0, bpb + 0.9 - pedal_lead_beats)
            perf.pedal_events.append(PedalEvent(bar=bar, beat=up_beat, type="sustain", action="up"))

    # ── Voicing: melody rides above the accompaniment (per-layer balance is
    #    applied per-event in the MIDI stage; this keeps the bar-level hook). ──
    for bar in range(first_bar, last_bar + 1):
        perf.voicing_emphasis.append(VoicingEmphasis(bar=bar, beat=1.0, voice="melody", boost=0.12))

    # ── Microtiming: agogic lean into slurred entries; a pre-onset stretch at
    #    breath points (a performer takes a breath before resuming). ──
    for e in layer.principal_line:
        if e.slur == "start":
            perf.microtiming.append(
                TimingOffset(bar=e.bar, beat=e.beat, offset_ms=profile.upbeat_lean_ms + 2.0)
            )
    for b, bt in breath_points or []:
        perf.microtiming.append(
            TimingOffset(bar=b, beat=bt, offset_ms=profile.downbeat_stress_ms + 6.0)
        )

    return perf


def velocity_at(
    perf: PerformanceIR,
    bar: int,
    beat: float,
    beats_per_bar: float,
    base: int = _DEFAULT_VELOCITY,
    curve_kind: str = "linear",
) -> int:
    """Interpolated velocity at a time point. ``curve_kind`` shapes the segment
    between anchors (s_curve/exp/log/arch) so crescendos swell non-linearly
    instead of as a straight ramp; default 'linear' preserves old behavior."""
    points = perf.dynamic_curve
    if not points:
        return base

    def _pos(b, bt):
        return (b - 1) * beats_per_bar + (bt - 1.0)

    t = _pos(bar, beat)
    prev = nxt = None
    for p in points:
        pt = _pos(p.bar, p.beat)
        if pt <= t:
            prev = (pt, p.velocity)
        elif nxt is None:
            nxt = (pt, p.velocity)
            break
    if prev is None:
        return nxt[1] if nxt else base
    if nxt is None or nxt[0] == prev[0]:
        return prev[1]
    frac = (t - prev[0]) / (nxt[0] - prev[0])
    if curve_kind != "linear":
        frac = shape(frac, curve_kind)
    return int(round(prev[1] + frac * (nxt[1] - prev[1])))


def tempo_factor_at(perf: PerformanceIR, bar: int, beat: float, beats_per_bar: float) -> float:
    """Tempo multiplier at a time point (1.0 = a tempo, <1 = slower).

    Per-bar curve: ``curve[i]`` is the factor at the DOWNBEAT of bar
    (bar_start + i), interpolated smoothly toward the next bar within the bar.
    So sampling at beat 1.0 returns exactly that bar's planned factor (the
    cadence broadening on the last entry actually lands on the last bar).
    """
    for w in perf.rubato_windows:
        if w.bar_start <= bar <= w.bar_end and w.curve:
            idx = bar - w.bar_start
            lo = min(idx, len(w.curve) - 1)
            hi = min(idx + 1, len(w.curve) - 1)
            within = max(0.0, min(1.0, (beat - 1.0) / max(beats_per_bar, 1e-6)))
            return w.curve[lo] + within * (w.curve[hi] - w.curve[lo])
    return 1.0


def microtiming_at(perf: PerformanceIR, bar: int, beat: float) -> float:
    """Timing offset in ms for an onset (0 when none applies)."""
    for m in perf.microtiming:
        if m.bar == bar and abs(m.beat - beat) < 0.01:
            return m.offset_ms
    return 0.0


def pedal_bars(perf: PerformanceIR) -> List[int]:
    """Bars with sustain-pedal down events."""
    return sorted({p.bar for p in perf.pedal_events if p.action == "down"})
