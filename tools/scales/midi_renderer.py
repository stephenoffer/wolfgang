"""
MIDI Renderer — humanized MIDI from EventIR for audio preview.

The MIDI preview is what the music-critic judges by ear, so it must not
sound like a quantized grid: velocities are interpolated along each
phrase's dynamic curve (with melody voicing emphasis), cadences get a
ritardando (real tempo marks), slurred entries get a tiny agogic lean,
and pedaled bars get audible sustain via legato overlap in the
accompaniment. PerformanceIR is built on the fly per phrase by
performance_renderer — deterministic, nothing persisted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .duration import DURATION_VALUES
from .models import EventIR, PerformanceIR
from .music_io import layer_ir_to_event_ir
from .piece_graph import PieceGraph
from .pitch import pitch_to_midi


def render_midi(
    piece_graph: PieceGraph,
    scope: str = "full",
    output_dir: Optional[str] = None,
    humanize: bool = True,
) -> str:
    """Render piece to MIDI file. Returns path to the MIDI file."""
    try:
        import music21
    except ImportError:
        raise ImportError("music21 required for MIDI rendering")

    from .performance_params import profile_for_composer
    from .performance_renderer import (
        build_performance_ir,
        microtiming_at,
        pedal_bars,
        tempo_factor_at,
        velocity_at,
    )
    from .performance_util import jitter

    # Resolve the period's performance profile once from the piece's style.
    dna = getattr(piece_graph, "style_dna", None)
    style_ref = (getattr(dna, "composer_id", "") or
                 getattr(dna, "active_period", "")) if dna else ""
    profile = profile_for_composer(style_ref)

    # Collect (events, performance, meter, key) per phrase
    phrase_renders: List[Tuple[List[EventIR], Optional[PerformanceIR],
                               Tuple[int, int], str]] = []
    tempo_bpm = 120
    got_tempo = False
    for phrase_id, phrase_state in piece_graph.phrases.items():
        if scope.startswith("section-"):
            section_id = scope.replace("section-", "")
            if not phrase_state.slot or phrase_state.slot.section_id != section_id:
                continue
        if not phrase_state.realized:
            continue
        slot = phrase_state.slot
        meter = tuple(slot.meter) if slot else (4, 4)
        key = getattr(slot, "key", "C") if slot else "C"
        if slot and not got_tempo:
            tempo_bpm = slot.tempo_bpm or 120
            got_tempo = True
        events = layer_ir_to_event_ir(phrase_state.realized)
        perf = None
        if humanize:
            try:
                sketch = getattr(phrase_state, "sketch", None)
                breaths = [(bp.bar, bp.beat) for bp in
                           (getattr(sketch, "breath_points", None) or [])
                           if hasattr(bp, "bar")]
                perf = build_performance_ir(phrase_state.realized, slot,
                                            profile=profile, breath_points=breaths)
            except Exception:
                perf = None
        phrase_renders.append((events, perf, meter, key))

    if not phrase_renders:
        raise ValueError("No realized phrases to render")

    stream = music21.stream.Stream()
    stream.insert(0, music21.tempo.MetronomeMark(number=tempo_bpm))

    dyn_velocity = {
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
    ms_per_beat = 60000.0 / max(tempo_bpm, 1)
    bar_tempo: Dict[float, float] = {}  # global bar offset → absolute bpm

    for events, perf, meter, key in phrase_renders:
        beats_per_bar = meter[0] * 4.0 / meter[1]
        pedaled = set(pedal_bars(perf)) if perf else set()
        # Tendency-tone pitch class (the leading tone) for harmony-aware
        # emphasis: it pulls toward the tonic and is played with a touch more
        # weight. Cheap, key-only, no full harmonic analysis needed.
        try:
            tonic_pc = pitch_to_midi(f"{key.rstrip('m')}4") % 12
        except Exception:
            tonic_pc = 0
        leading_pc = (tonic_pc - 1) % 12
        prev_pitch_by_voice: Dict[Tuple[str, int], int] = {}
        for event in events:
            if event.pitch == "rest":
                continue
            pitches = event.pitch if isinstance(event.pitch, list) else [event.pitch]
            midis = []
            for p in pitches:
                try:
                    m = pitch_to_midi(p)
                except (ValueError, KeyError, TypeError):
                    m = None
                if m is not None:
                    midis.append(m)
            if not midis:
                continue

            offset = (event.bar - 1) * beats_per_bar + (event.beat - 1.0)
            dur = DURATION_VALUES.get(event.duration, 1.0)

            # ── Velocity: shaped curve + per-layer balance + human variance ──
            if perf is not None:
                vel = float(velocity_at(perf, event.bar, event.beat, beats_per_bar,
                                        curve_kind=profile.velocity_curve_kind))
                if event.dynamic:  # explicit mark wins at its own onset
                    vel = float(dyn_velocity.get(event.dynamic, vel))
                # Per-layer voicing balance (principal sings, filler recedes).
                layer_mul = profile.voicing_balance.get(event.source_layer or "", None)
                if layer_mul is None:
                    layer_mul = 1.12 if (event.staff == "treble" and event.voice == 1) else 1.0
                vel *= layer_mul
                # Tendency-tone (leading-tone) emphasis.
                if midis and (max(midis) % 12) == leading_pc:
                    vel *= (1.0 + profile.dissonance_emphasis)
                # Articulation → attack: accent/marcato bite.
                if event.articulation in ("accent", "marcato"):
                    vel *= (1.0 + profile.accent_boost)
                # gentle metric shading: offbeats slightly lighter
                if abs(event.beat - round(event.beat)) > 0.01:
                    vel -= 6.0
                # Repeated-note anti-repetition: consecutive same-pitch onsets
                # in a voice get deterministic ± variance (no machine-gun).
                vkey = (event.staff, event.voice)
                if prev_pitch_by_voice.get(vkey) == (midis[0] if midis else None):
                    vel += jitter((event.bar, event.beat, midis[0], "rep"),
                                  profile.repeated_note_variance)
                prev_pitch_by_voice[vkey] = midis[0] if midis else None
                # Deterministic micro-jitter everywhere (kills perfectly flat runs).
                vel += jitter((event.bar, event.beat, midis[0], "v"),
                              profile.micro_velocity_jitter)
                vel = max(profile.velocity_floor, min(profile.velocity_ceiling, vel))
            else:
                vel = dyn_velocity.get(event.dynamic, 80) if event.dynamic else 80
            vel = int(round(vel))

            # ── Articulation → duration: staccato shortens, tenuto extends ──
            if event.articulation == "staccato":
                dur *= profile.staccato_gate
            elif event.articulation == "tenuto":
                dur *= (1.0 + profile.tenuto_extend)

            # ── Timing humanization ──
            if perf is not None:
                # agogic lean stored on the PerformanceIR (slur entries, breaths)
                lean_ms = microtiming_at(perf, event.bar, event.beat)
                if lean_ms:
                    offset += lean_ms / ms_per_beat
                frac_beat = event.beat - int(event.beat)
                # metrical stress: downbeat slightly late & weighty; offbeats lean
                if abs(frac_beat) < 0.01:
                    offset += profile.downbeat_stress_ms / ms_per_beat
                # notes inégales / swing: the off-beat eighth of a pair is held
                # back slightly (long-short), period-dependent strength
                if abs(frac_beat - 0.5) < 0.01:
                    ineg = max(profile.inegalite_strength, profile.swing_ratio)
                    if ineg:
                        offset += ineg * 0.25  # delay the short note (beats)
                # hand offset: the bass settles a hair after the melody
                if event.staff == "bass":
                    offset += profile.hand_offset_ms / ms_per_beat
                # tiny deterministic onset jitter (no two attacks perfectly aligned)
                offset += jitter((event.bar, event.beat, midis[0], "t"), 0.004)
                # record the bar's tempo factor once (one explicit mark per bar
                # downbeat keeps the tempo arc smooth and prevents drift — every
                # bar re-sets the tempo, so slowdowns never stack)
                bar_off = (event.bar - 1) * beats_per_bar
                if bar_off not in bar_tempo:
                    f = tempo_factor_at(perf, event.bar, 1.0, beats_per_bar)
                    bar_tempo[bar_off] = max(20.0, tempo_bpm * f)

            # ── Audible sustain: legato overlap in pedaled bars ──
            if perf is not None and event.bar in pedaled and event.staff == "bass":
                bar_end = (event.bar - 1) * beats_per_bar + beats_per_bar
                dur = max(dur, min(dur * 1.6, bar_end - offset))

            try:
                vol = max(1, min(127, vel))
                # ensemble spread: a chord's notes don't attack in perfect unison
                if len(midis) > 1 and perf is not None and profile.ensemble_spread_ms > 0:
                    for ti, m in enumerate(sorted(midis)):
                        sp = jitter((event.bar, event.beat, m, "e"),
                                    profile.ensemble_spread_ms) / ms_per_beat
                        nn = music21.note.Note(midi=m)
                        nn.duration = music21.duration.Duration(dur)
                        nn.volume.velocity = vol
                        stream.insert(max(0.0, offset + sp), nn)
                elif len(midis) > 1:
                    n = music21.chord.Chord(midis)
                    n.duration = music21.duration.Duration(dur)
                    n.volume.velocity = vol
                    stream.insert(offset, n)
                else:
                    n = music21.note.Note(midi=midis[0])
                    n.duration = music21.duration.Duration(dur)
                    n.volume.velocity = vol
                    stream.insert(max(0.0, offset), n)
            except Exception:
                continue

    # Rubato as real tempo marks (music21 MIDI export honors these). One mark
    # per bar downbeat — the tempo arc pushes through tension and broadens at
    # cadences. CRITICAL (C6): because EVERY sounding bar emits an explicit
    # mark, a slow bar is always followed by the next bar's mark, so slowdowns
    # can never stack and the piece never drags progressively slower.
    for off in sorted(bar_tempo):
        stream.insert(off, music21.tempo.MetronomeMark(number=bar_tempo[off]))

    # Write MIDI
    if output_dir is None:
        output_dir = f"workspace/{piece_graph.piece_id}/output"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / f"{piece_graph.piece_id}.mid"
    stream.write("midi", fp=str(filepath))

    piece_graph.output_paths["midi"] = str(filepath)
    return str(filepath)
