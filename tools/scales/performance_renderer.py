"""
PerformanceRenderer — populate PerformanceIR and humanize playback.

Turns the PerformanceIR model into something audible: interpolated velocity
curves, cadential rubato, per-bar sustain pedal, melody voicing emphasis, and
gentle microtiming. Everything here is deterministic — same phrase in, same
performance out — so renders are reproducible.

It does **not** use `performance_bank.PerformanceBank`, despite what this
docstring and `build_performance_ir`'s used to say. That module is a set of
hand-written heuristic templates, it is imported by nothing, and the shapes
here are derived from the period profile and the phrase's own cadence instead.
A docstring asserting a dependency that does not exist is how a reader
concludes a job is being done that is not — which is exactly how this project
shipped a score with no articulation in it for as long as it did.

Split of responsibilities (by design):
- Continuous/expressive (velocity interpolation, microtiming, rubato
  tempo bends, audible sustain) → MIDI preview only, via midi_renderer.
- Discrete/notational (pedal marks, rit. text) → can also go to the
  score; pedal marks are emitted by midi_renderer's notation hook.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

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

    The cadential shape comes from the period profile, not from
    `performance_bank` (see the module docstring); hairpins are shaped
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


# ─── Metric hierarchy ────────────────────────────────────────────────────────
#
# Every metre has a hierarchy of stress, and it is not "downbeat vs offbeat".
# In 4/4 beat 1 is strongest, beat 3 next, beats 2 and 4 weaker, and everything
# between them weaker again. In 3/4 beat 1 dominates and 2 and 3 are near-equal.
# In 6/8 the stresses are on the two dotted-quarter beats, and a renderer that
# accents all six eighths equally makes a jig sound like a march.
#
# The playback rule this replaces was a single "offbeats are 6 velocity lighter",
# which flattens a bar to two levels and is a large part of why MIDI previews of
# this system sound like a sequencer: the metre is inaudible, so the listener has
# nothing to hang the rhythm on.

_METER_WEIGHTS: Dict[Tuple[int, int], Dict[float, float]] = {
    (4, 4): {1.0: 1.00, 3.0: 0.94, 2.0: 0.88, 4.0: 0.88},
    (2, 4): {1.0: 1.00, 2.0: 0.89},
    (2, 2): {1.0: 1.00, 3.0: 0.92},
    (3, 4): {1.0: 1.00, 2.0: 0.89, 3.0: 0.87},
    (3, 8): {1.0: 1.00, 1.5: 0.88, 2.0: 0.87},
    (6, 8): {1.0: 1.00, 2.5: 0.93, 1.5: 0.86, 2.0: 0.86, 3.0: 0.86, 3.5: 0.86},
    (9, 8): {1.0: 1.00, 2.5: 0.92, 4.0: 0.92},
    (12, 8): {1.0: 1.00, 4.0: 0.94, 2.5: 0.90, 5.5: 0.90},
    (3, 2): {1.0: 1.00, 3.0: 0.90, 5.0: 0.88},
    (4, 2): {1.0: 1.00, 5.0: 0.94, 3.0: 0.88, 7.0: 0.88},
}

# Anything not on a listed beat position is subdivision. A subdivision directly
# between two beats is stronger than one that is not (the "and" of a beat is
# stronger than the "e" or the "a"), which is what gives running sixteenths
# their internal shape instead of a flat stream.
_SUB_WEIGHT_HALF = 0.83
_SUB_WEIGHT_OTHER = 0.79


def metric_weight(beat: float, meter: Tuple[int, int] = (4, 4)) -> float:
    """Velocity multiplier for a beat position, from the metre's own hierarchy.

    Returns 1.0 on the downbeat and progressively less on weaker positions.
    Multiplicative so it composes with dynamics, hairpins and accents rather
    than overriding them.
    """
    try:
        key = (int(meter[0]), int(meter[1]))
    except Exception:  # pragma: no cover - defensive
        key = (4, 4)
    table = _METER_WEIGHTS.get(key)
    if table is None:
        # Unlisted metre: the downbeat is strong, every other whole beat is
        # middling, subdivisions are weak. Guessing a hierarchy is worse than
        # admitting there isn't a known one.
        table = {1.0: 1.0}
    b = round(float(beat), 4)
    for pos, w in table.items():
        if abs(b - pos) < 0.02:
            return w
    if abs(b - int(b) - 0.5) < 0.02:
        return _SUB_WEIGHT_HALF
    return _SUB_WEIGHT_OTHER


def is_strong_beat(beat: float, meter: Tuple[int, int] = (4, 4)) -> bool:
    """True on a beat the metre stresses — used for agogic and pedal decisions."""
    return metric_weight(beat, meter) >= 0.93


# ─── Phrase arch ─────────────────────────────────────────────────────────────


def phrase_arch_points(
    layer,
    depth: float = 0.10,
    min_notes: int = 6,
) -> List[DynamicPoint]:
    """Velocity anchors following the melody's own rise and fall.

    A performer shapes every phrase toward its high point and away again, whether
    or not a hairpin is written — it is what "phrasing" means. The renderer only
    followed *written* dynamics, so a phrase with no marks was played at one
    velocity from end to end, which no player has ever done.

    Returns anchors only; they are merged UNDER any written dynamic, so the
    composer's marks always win. ``depth`` is the fraction of the base velocity
    the arch is allowed to move (0.10 = ±10%), deliberately small: this is
    phrasing, not a crescendo.
    """
    from .pitch import pitch_to_midi

    mel = [
        e
        for e in sorted(layer.principal_line, key=lambda e: (e.bar, e.beat))
        if getattr(e, "pitch", None) and e.pitch != "rest"
    ]
    if len(mel) < min_notes:
        return []
    tops: List[int] = []
    keep = []
    for e in mel:
        names = e.pitch if isinstance(e.pitch, list) else [e.pitch]
        vals = [v for v in (pitch_to_midi(n) for n in names) if v is not None]
        if not vals:
            continue
        tops.append(max(vals))
        keep.append(e)
    if len(tops) < min_notes:
        return []

    lo, hi = min(tops), max(tops)
    if hi - lo < 3:
        return []  # a flat line has no arch to follow, and faking one is worse

    points: List[DynamicPoint] = []
    for e, top in zip(keep, tops):
        frac = (top - lo) / (hi - lo)  # 0 at the phrase's floor, 1 at its peak
        # Centred so the middle of the range is neutral: the arch lifts the
        # peak and eases the trough rather than making everything louder.
        points.append(
            DynamicPoint(
                bar=e.bar,
                beat=e.beat,
                velocity=int(round(_DEFAULT_VELOCITY * (1.0 + depth * (2.0 * frac - 1.0)))),
            )
        )
    return points


def merge_arch_under_dynamics(
    perf: PerformanceIR, arch: Sequence[DynamicPoint], written_beats: int = 2
) -> int:
    """Add arch anchors only where the composer wrote nothing nearby.

    Returns how many were added. A written dynamic owns its neighbourhood: an
    arch point next to an explicit ``p`` would argue with it, and the composer
    wins that argument every time.
    """
    if not arch:
        return 0
    written = {(p.bar, round(p.beat, 2)) for p in perf.dynamic_curve}
    if not written:
        perf.dynamic_curve.extend(arch)
        perf.dynamic_curve.sort(key=lambda p: (p.bar, p.beat))
        return len(arch)
    added = 0
    for a in arch:
        near = any(
            abs((a.bar - b) * 4 + (a.beat - bt)) <= written_beats for (b, bt) in written
        )
        if near:
            continue
        perf.dynamic_curve.append(a)
        added += 1
    perf.dynamic_curve.sort(key=lambda p: (p.bar, p.beat))
    return added


# ─── Melodic lead ────────────────────────────────────────────────────────────


def melodic_lead_beats(
    event, profile: StylePerfProfile, ms_per_beat: float, is_peak: bool = False
) -> float:
    """How far AHEAD of the accompaniment a melody note is struck.

    Pianists play the melody a few milliseconds before the notes beneath it —
    "melodic lead" — and it is one of the most reliably measured features of
    real performance and one of the strongest cues that a human is playing.
    Negative because the melody arrives *early*.

    The existing renderer delayed every bass note by a flat amount, which is the
    same idea applied bluntly: it separates the hands but does not follow the
    music, so it reads as a constant lag rather than as expression. The lead
    here grows at expressive peaks and on long notes, which is what a player
    actually does.
    """
    layer = getattr(event, "source_layer", "") or ""
    if layer not in ("principal_line", "foreground"):
        return 0.0
    lead_ms = profile.hand_offset_ms * 1.5
    if is_peak:
        lead_ms *= 1.6
    return -lead_ms / max(ms_per_beat, 1e-6)


def agogic_stretch(event, meter: Tuple[int, int], profile: StylePerfProfile) -> float:
    """Extra time a player takes over a note that matters, in beats.

    A long note on a strong beat, a note carrying an accent, and the note at the
    top of a leap all get a fraction more time than they are written. Agogic
    accent is how a pianist stresses a note on an instrument that cannot swell,
    and none of it was modelled: every note took exactly its notated length.
    """
    from .duration import dur_to_beats

    try:
        dur = float(dur_to_beats(getattr(event, "duration", "q")))
    except Exception:  # pragma: no cover - defensive
        return 0.0
    stretch = 0.0
    if dur >= 1.0 and is_strong_beat(getattr(event, "beat", 1.0), meter):
        stretch += 0.02 * profile.rubato_depth / 0.06
    if getattr(event, "articulation", None) in ("accent", "marcato", "tenuto"):
        stretch += 0.015
    if getattr(event, "role", "") in ("appoggiatura", "suspension"):
        stretch += 0.025
    return stretch


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
