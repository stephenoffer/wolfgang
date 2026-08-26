"""
MIDI Renderer — humanized MIDI from EventIR for audio preview.

This file is for a HUMAN to listen to. Nothing in the quality loop consumes it:
the music-critic is a language model reading a score and a report, not an audio
listener, so none of the humanization below influences a single compositional
decision. (An earlier version of this docstring claimed the critic "judges it by
ear", which is not possible — see the note in .claude/agents/music-critic.md.)
There is no acoustic signal anywhere in this system; every judgment it makes is
symbolic.

That is still worth doing well, because the user's ear is the one that finally
matters, and a quantized grid misrepresents the score. So: velocities are
interpolated along each
phrase's dynamic curve (with melody voicing emphasis), cadences get a
ritardando (real tempo marks), slurred entries get a tiny agogic lean,
and pedaled bars get audible sustain via legato overlap in the
accompaniment. PerformanceIR is built on the fly per phrase by
performance_renderer — deterministic, nothing persisted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .duration import DURATION_VALUES, bar_duration
from .models import EventIR, PerformanceIR
from .music_io import layer_ir_to_event_ir
from .piece_graph import PieceGraph
from .pitch import pitch_to_midi

# How fast a rolled chord rolls, and the re-strike unit of a measured tremolo,
# both in quarter-note beats. A roll is a gesture, not a broken chord: about a
# 32nd between entries is what a pianist does.
_ROLL_STEP_BEATS = 0.125
_TREMOLO_UNIT = 0.125


def _tied_extensions(events) -> Dict[int, float]:
    """Extra sounding length each tie-START inherits from its continuations.

    A tie is one note, held. Walk each voice in time order and, for every event
    marked ``tie="start"``, absorb the durations of the ``continue``/``stop``
    events that follow it at the same pitch. Returned by ``id(event)`` so the
    render loop can look up an extension without re-scanning.
    """
    from collections import defaultdict

    by_voice = defaultdict(list)
    for e in events:
        if e.pitch == "rest":
            continue
        by_voice[(e.staff, getattr(e, "voice", 1) or 1)].append(e)

    extra: Dict[int, float] = {}
    for evs in by_voice.values():
        evs.sort(key=lambda e: (e.bar, e.beat))
        i = 0
        while i < len(evs):
            if evs[i].tie != "start":
                i += 1
                continue
            held = 0.0
            j = i + 1
            while j < len(evs) and evs[j].tie in ("continue", "stop"):
                if evs[j].pitch != evs[i].pitch:
                    break
                held += DURATION_VALUES.get(evs[j].duration, 1.0)
                if evs[j].tie == "stop":
                    j += 1
                    break
                j += 1
            if held:
                extra[id(evs[i])] = float(held)
            i = max(j, i + 1)
    return extra


def _clip_same_pitch_overlaps(specs: List[list]) -> None:
    """Shorten any note that would still be ringing when its own pitch re-attacks.

    Legato between DIFFERENT pitches is expressive; a pitch retriggered while
    still sounding is a glitch, and the sustain/legato humanization produced 25 of
    them in a 41-bar piece (repeated offbeat chords stretched 1.6x ran straight
    into their own next attack).
    """
    from collections import defaultdict

    by_pitch = defaultdict(list)
    for spec in specs:
        for m in spec[2]:
            by_pitch[m].append(spec)
    for _m, group in by_pitch.items():
        group.sort(key=lambda sp: sp[0])
        for cur, nxt in zip(group, group[1:]):
            gap = nxt[0] - cur[0]
            if gap <= 1e-6:
                # Two attacks of one pitch at the SAME instant. This is what a
                # grace note written on its own principal's pitch produces, and
                # it is not a unison — it is one note triggered twice. Silence
                # the shorter of the two.
                if cur[1] <= nxt[1]:
                    cur[1] = 0.0
                else:
                    nxt[1] = 0.0
                continue
            # leave a hair of silence so the retrigger is clean
            cur[1] = min(cur[1], max(0.03, gap * 0.98))


def _ramped_tempo_marks(bar_tempo: Dict[float, float], beats_per_bar: float):
    """Interpolate tempo across each bar instead of stepping at the downbeat."""
    offsets = sorted(bar_tempo)
    out = []
    steps = max(1, int(round(beats_per_bar)))
    for i, off in enumerate(offsets):
        start = bar_tempo[off]
        end = bar_tempo[offsets[i + 1]] if i + 1 < len(offsets) else start
        for k in range(steps):
            frac = k / steps
            out.append((off + frac * beats_per_bar, round(start + (end - start) * frac, 2)))
    return out


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

    from .ornament_realization import realize_event
    from .performance_params import profile_for_composer
    from .performance_renderer import (
        build_performance_ir,
        metric_weight,
        microtiming_at,
        pedal_bars,
        tempo_factor_at,
        velocity_at,
    )
    from .performance_util import jitter

    # Resolve the period's performance profile once from the piece's style.
    dna = getattr(piece_graph, "style_dna", None)
    style_ref = (
        (getattr(dna, "composer_id", "") or getattr(dna, "active_period", "")) if dna else ""
    )
    profile = profile_for_composer(style_ref)

    # Collect (events, performance, meter, key) per phrase
    phrase_renders: List[Tuple[List[EventIR], Optional[PerformanceIR], Tuple[int, int], str]] = []
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
                breaths = [
                    (bp.bar, bp.beat)
                    for bp in (getattr(sketch, "breath_points", None) or [])
                    if hasattr(bp, "bar")
                ]
                perf = build_performance_ir(
                    phrase_state.realized, slot, profile=profile, breath_points=breaths
                )
            except Exception:
                perf = None
        phrase_renders.append((events, perf, meter, key))

    if not phrase_renders:
        raise ValueError("No realized phrases to render")

    stream = music21.stream.Stream()
    stream.insert(0, music21.tempo.MetronomeMark(number=tempo_bpm))
    # Notes are collected first and emitted after a pass that clips same-pitch
    # overlaps (see _clip_same_pitch_overlaps): the legato/sustain humanization
    # below lengthens notes, and a lengthened note that runs into the NEXT attack
    # of the same pitch is not legato, it is a retrigger — audibly a glitch.
    specs: List[list] = []

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

    # Bar -> global start offset, accumulated across phrases so a meter change
    # does not shift every later bar. Computing `(bar - 1) * beats_per_bar` from
    # EACH phrase's own meter made the MIDI and the MusicXML disagree about where
    # bars are the moment a piece changed time signature.
    bar_starts: Dict[int, float] = {}
    cursor = 0.0
    for events, _perf, meter, _key in phrase_renders:
        per_bar = float(bar_duration(meter))
        for bar in sorted({e.bar for e in events}):
            if bar not in bar_starts:
                bar_starts[bar] = cursor
                cursor += per_bar

    for events, perf, meter, key in phrase_renders:
        beats_per_bar = float(bar_duration(meter))
        pedaled = set(pedal_bars(perf)) if perf else set()
        # Tendency-tone pitch class (the leading tone) for harmony-aware
        # emphasis: it pulls toward the tonic and is played with a touch more
        # weight. Cheap, key-only, no full harmonic analysis needed.
        try:
            # key_to_root_midi understands every spelling the system uses
            # ("a minor", "Am", "g_minor"). `key.rstrip('m')` silently failed on
            # the space-separated form the planner writes, so the leading-tone
            # emphasis was applied relative to C for most pieces.
            from .pitch import key_to_root_midi

            tonic_pc = key_to_root_midi(key) % 12
        except Exception:
            tonic_pc = 0
        leading_pc = (tonic_pc - 1) % 12
        prev_pitch_by_voice: Dict[Tuple[str, int], int] = {}
        # A tie means ONE sounding note, not two attacks. Nothing here read the
        # tie field, so every tied note re-articulated in the preview — the bug
        # was invisible only because the engraving path could not produce a tie
        # in the first place, so no generated score had ever contained one.
        tie_extra = _tied_extensions(events)
        for event in events:
            if event.pitch == "rest":
                continue
            if event.tie in ("stop", "continue"):
                continue  # sounded as part of the note it is tied to
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

            offset = bar_starts.get(event.bar, (event.bar - 1) * beats_per_bar) + (event.beat - 1.0)
            dur = DURATION_VALUES.get(event.duration, 1.0)
            # A tie start absorbs the length of everything tied to it.
            dur += tie_extra.get(id(event), 0.0)

            # ── Velocity: shaped curve + per-layer balance + human variance ──
            if perf is not None:
                vel = float(
                    velocity_at(
                        perf,
                        event.bar,
                        event.beat,
                        beats_per_bar,
                        curve_kind=profile.velocity_curve_kind,
                    )
                )
                if event.dynamic:  # explicit mark wins at its own onset
                    vel = float(dyn_velocity.get(event.dynamic, vel))
                # Per-layer voicing balance (principal sings, filler recedes).
                layer_mul = profile.voicing_balance.get(event.source_layer or "", None)
                if layer_mul is None:
                    layer_mul = 1.12 if (event.staff == "treble" and event.voice == 1) else 1.0
                vel *= layer_mul
                # Tendency-tone (leading-tone) emphasis.
                if midis and (max(midis) % 12) == leading_pc:
                    vel *= 1.0 + profile.dissonance_emphasis
                # Articulation → attack: accent/marcato bite.
                if event.articulation in ("accent", "marcato"):
                    vel *= 1.0 + profile.accent_boost
                # Metric hierarchy. The old rule ("offbeats are 6 velocity
                # lighter") flattens a bar to two levels, so all six eighths of
                # a 6/8 got equal stress and a jig came out sounding like a
                # march. A real hierarchy is per-meter and has more than two
                # levels.
                vel *= metric_weight(event.beat, meter)
                # Repeated-note anti-repetition: consecutive same-pitch onsets
                # in a voice get deterministic ± variance (no machine-gun).
                vkey = (event.staff, event.voice)
                if prev_pitch_by_voice.get(vkey) == (midis[0] if midis else None):
                    vel += jitter(
                        (event.bar, event.beat, midis[0], "rep"), profile.repeated_note_variance
                    )
                prev_pitch_by_voice[vkey] = midis[0] if midis else None
                # Deterministic micro-jitter everywhere (kills perfectly flat runs).
                vel += jitter((event.bar, event.beat, midis[0], "v"), profile.micro_velocity_jitter)
                vel = max(profile.velocity_floor, min(profile.velocity_ceiling, vel))
            else:
                vel = dyn_velocity.get(event.dynamic, 80) if event.dynamic else 80
            vel = int(round(vel))

            # ── Articulation → duration ──
            # A staccatissimo wedge is shorter than a staccato dot, a portato is
            # barely detached, a spiccato is short and light. Rendering all of
            # them (and, before that, only two of them) as one gate threw away
            # the distinctions the composer wrote.
            art = event.articulation
            if art == "staccato":
                dur *= profile.staccato_gate
            elif art == "staccatissimo":
                dur *= profile.staccato_gate * 0.6
            elif art == "spiccato":
                dur *= profile.staccato_gate * 0.75
            elif art == "portato":
                dur *= 0.85
            elif art == "tenuto":
                dur *= 1.0 + profile.tenuto_extend
            elif art in ("breath", "caesura"):
                # A breath is taken out of the note BEFORE it, not added after.
                dur *= 0.6 if art == "breath" else 0.45
            # A fermata holds. Without this the pause the composer wrote at the
            # end of the piece simply did not happen in the preview.
            if event.ornament == "fermata":
                dur *= 1.8

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
                bar_off = bar_starts.get(event.bar, (event.bar - 1) * beats_per_bar)
                if bar_off not in bar_tempo:
                    f = tempo_factor_at(perf, event.bar, 1.0, beats_per_bar)
                    bar_tempo[bar_off] = max(20.0, tempo_bpm * f)

            # ── Audible sustain: legato overlap in pedaled bars ──
            if perf is not None and event.bar in pedaled and event.staff == "bass":
                bar_end = bar_starts.get(event.bar, (event.bar - 1) * beats_per_bar) + beats_per_bar
                dur = max(dur, min(dur * 1.6, bar_end - offset))

            try:
                vol = max(1, min(127, vel))
                # Ornaments were ENGRAVED and then silent: a trill printed `tr`
                # and played one plain note, and an appoggiatura sounded
                # identical to an acciaccatura. In a Classical slow movement
                # that is most of the expression, and the critic judging the
                # preview never heard any of it.
                orn_notes = realize_event(
                    event, key=key, tempo_bpm=tempo_bpm, period=profile.period
                )
                technique = getattr(event, "technique", None)
                if orn_notes:
                    for pn in orn_notes:
                        o, d, m, vscale = pn.as_tuple()
                        specs.append(
                            [max(0.0, offset + o), d, [m], max(1, min(127, int(vol * vscale)))]
                        )
                elif technique in ("arpeggio", "arpeggio_up", "arpeggio_down") and len(midis) > 1:
                    # A rolled chord actually rolls: the notes enter in sequence
                    # from the bottom (or the top, for a downward roll) and all
                    # release together. Written but silent until now.
                    order = sorted(midis, reverse=(technique == "arpeggio_down"))
                    step = min(_ROLL_STEP_BEATS, dur / max(2, len(order)))
                    for i, m in enumerate(order):
                        start = max(0.0, offset + i * step)
                        specs.append([start, max(0.05, dur - i * step), [m], vol])
                elif technique == "tremolo" and midis:
                    # Measured tremolo: the written value re-struck in 32nds.
                    reps = max(2, int(dur / _TREMOLO_UNIT))
                    unit = dur / reps
                    for i in range(reps):
                        specs.append([max(0.0, offset + i * unit), unit * 0.95, sorted(midis), vol])
                # ensemble spread: a chord's notes don't attack in perfect unison
                elif len(midis) > 1 and perf is not None and profile.ensemble_spread_ms > 0:
                    for m in sorted(midis):
                        sp = (
                            jitter((event.bar, event.beat, m, "e"), profile.ensemble_spread_ms)
                            / ms_per_beat
                        )
                        specs.append([max(0.0, offset + sp), dur, [m], vol])
                else:
                    specs.append([max(0.0, offset), dur, sorted(midis), vol])
            except Exception:
                continue

    # Emit the notes, with same-pitch retriggers clipped.
    _clip_same_pitch_overlaps(specs)
    for off, dur, midis, vol in specs:
        if dur <= 0:
            continue
        n = music21.chord.Chord(midis) if len(midis) > 1 else music21.note.Note(midi=midis[0])
        n.duration = music21.duration.Duration(dur)
        n.volume.velocity = vol
        stream.insert(off, n)

    # Rubato as real tempo marks (music21 MIDI export honors these). RAMPED, not
    # stepped: one mark per bar produced a single-bar drop from 76 to 68 and an
    # instant snap back, which does not sound like a ritardando — it sounds like
    # the playback lurching. Interpolating across the bar gives an audible slowing
    # and recovery. Every bar still emits marks, so slowdowns cannot stack.
    for off, bpm in _ramped_tempo_marks(bar_tempo, beats_per_bar):
        stream.insert(off, music21.tempo.MetronomeMark(number=bpm))

    # Write MIDI
    if output_dir is None:
        output_dir = f"workspace/{piece_graph.piece_id}/output"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / f"{piece_graph.piece_id}.mid"
    stream.write("midi", fp=str(filepath))

    # Setting the field alone wrote it to an object the caller then discards —
    # the documented flow is load the graph, call this, print the path — so the
    # MIDI render was never recorded and `get_status` reported a piece with no
    # output. `record_output` sets it and persists, best-effort.
    from .piece_graph import record_output

    record_output(piece_graph, "midi", filepath)
    return str(filepath)
