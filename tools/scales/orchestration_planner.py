"""
OrchestrationPlanner — idiomatic piano-core → orchestra expansion.

Replaces SABRE's naive 3-role assignment with register-aware, dynamics-
aware planning: melody with climax doublings, divided inner voices,
sustained wind harmony, octave bass doubling, per-instrument range
clamping. Still deliberately conservative — it voices an already-finished
musical argument, it does not invent material.

Plan shape (per layer → instruments):
  principal_line     → lead violin/wind; flute doubles 8va at f+;
                       oboe doubles unison at mp-mf in singing register
  bass_foundation    → cello; contrabass doubles 8vb at mf+
  response_layer     → violin_2 / viola split by register; condensed
                       into sustained wind chords (clarinet+bassoon)
  counter_reply      → oboe (or viola)
  ornamental_surface → flute (when not doubling), else stays with lead
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from .duration import beats_to_dur
from .models import LayerEvent, LayerIR
from .pitch import midi_to_pitch, pitch_to_midi
from .validator import INSTRUMENT_RANGES

_DYN_RANK = {
    "ppp": 0,
    "pp": 1,
    "p": 2,
    "mp": 3,
    "mf": 4,
    "f": 5,
    "ff": 6,
    "fff": 7,
    "sfz": 5,
    "fp": 4,
}

# Instrument-name → range-table key
_RANGE_ALIASES = {
    "violin_1": "violin",
    "violin_2": "violin",
    "violin_i": "violin",
    "violin_ii": "violin",
    "contrabass": "double_bass",
}

_MELODY_PREFERENCE = ["violin_1", "violin", "flute", "oboe", "clarinet", "trumpet"]
_BASS_PREFERENCE = ["cello", "bassoon", "trombone", "tuba", "double_bass", "contrabass"]


def _range_of(instrument: str) -> Tuple[int, int]:
    key = _RANGE_ALIASES.get(instrument.lower(), instrument.lower())
    return INSTRUMENT_RANGES.get(key, (21, 108))


def _clamp_octave(midi: int, lo: int, hi: int) -> int:
    while midi < lo:
        midi += 12
    while midi > hi:
        midi -= 12
    return max(lo, min(hi, midi))


def _transpose_event_pitch(pitch, semitones: int, lo: int, hi: int, key: str):
    """Transpose a pitch (or chord list) and clamp into [lo, hi]."""

    def one(p):
        try:
            m = pitch_to_midi(p)
        except (ValueError, KeyError, TypeError):
            return None
        if m is None:
            return None
        return midi_to_pitch(_clamp_octave(m + semitones, lo, hi), key)

    if isinstance(pitch, list):
        out = [one(p) for p in pitch]
        out = [p for p in out if p]
        return out if len(out) > 1 else (out[0] if out else None)
    return one(pitch)


def _event_dict(e: LayerEvent, pitch=None) -> Dict[str, Any]:
    return {
        "bar": e.bar,
        "beat": e.beat,
        "pitch": pitch if pitch is not None else e.pitch,
        "duration": e.duration,
        "dynamic": e.dynamic,
        "articulation": e.articulation,
        "slur": e.slur,
    }


def _bar_dynamics(layer: LayerIR) -> Dict[int, int]:
    """Per-bar loudness rank, carried forward from the last marking."""
    marks: Dict[int, int] = {}
    events = sorted(
        (e for e in layer.principal_line + layer.bass_foundation if e.dynamic),
        key=lambda e: (e.bar, e.beat),
    )
    for e in events:
        marks[e.bar] = _DYN_RANK.get(e.dynamic, 4)
    out: Dict[int, int] = {}
    current = 4  # mf default
    last_bar = max((e.bar for e in layer.principal_line + layer.bass_foundation), default=1)
    first_bar = min((e.bar for e in layer.principal_line + layer.bass_foundation), default=1)
    for bar in range(first_bar, last_bar + 1):
        if bar in marks:
            current = marks[bar]
        out[bar] = current
    return out


def _pick(preferences: List[str], ensemble: List[str], taken: set) -> Optional[str]:
    lower = {i.lower(): i for i in ensemble}
    for pref in preferences:
        inst = lower.get(pref)
        if inst and inst not in taken:
            return inst
    for inst in ensemble:
        if inst not in taken:
            return inst
    return None


def plan_orchestration(
    layer: LayerIR,
    ensemble: List[str],
    key: str = "C",
    style_roles: Optional[Dict[str, Any]] = None,
) -> Dict[str, List[Dict]]:
    """Voice a piano-core LayerIR across an ensemble, idiomatically.

    ``style_roles`` (compiled_packs orchestration_roles.json, when
    populated) can override the lead/bass choice via entries like
    {"melody": "clarinet"}.
    """
    parts: Dict[str, List[Dict]] = {inst: [] for inst in ensemble}
    loudness = _bar_dynamics(layer)
    taken: set = set()
    style_roles = style_roles or {}

    # Legacy piano-core shape: whole LH lives in bass_foundation with no
    # response_layer. Split it — first event per bar anchors the bass,
    # the rest is inner motion — so the inner instruments have material.
    bass_events = list(layer.bass_foundation)
    response_events = list(layer.response_layer)
    bar_count = max(1, layer.bar_count)
    if not response_events and len(bass_events) > bar_count * 1.5:
        by_bar: Dict[int, List[LayerEvent]] = defaultdict(list)
        for e in sorted(bass_events, key=lambda e: (e.bar, e.beat)):
            by_bar[e.bar].append(e)
        bass_events, response_events = [], []
        for bar, evs in sorted(by_bar.items()):
            sounding = [e for e in evs if e.pitch != "rest"]
            if sounding:
                bass_events.append(sounding[0])
                response_events.extend(sounding[1:])
            else:
                bass_events.extend(evs)
    layer = LayerIR(
        phrase_id=layer.phrase_id,
        instrumentation=layer.instrumentation,
        principal_line=layer.principal_line,
        bass_foundation=bass_events,
        response_layer=response_events,
        counter_reply=layer.counter_reply,
        ornamental_surface=layer.ornamental_surface,
        key=layer.key,
        meter=layer.meter,
        bar_count=layer.bar_count,
    )

    # ── Leads ──
    lead = (style_roles.get("melody") if style_roles.get("melody") in ensemble else None) or _pick(
        _MELODY_PREFERENCE, ensemble, taken
    )
    if lead:
        taken.add(lead)
    bass = (style_roles.get("bass") if style_roles.get("bass") in ensemble else None) or _pick(
        _BASS_PREFERENCE, ensemble, taken
    )
    if bass:
        taken.add(bass)

    lower_ens = {i.lower(): i for i in ensemble}
    flute = lower_ens.get("flute")
    oboe = lower_ens.get("oboe") if lower_ens.get("oboe") != lead else None
    clarinet = lower_ens.get("clarinet") if lower_ens.get("clarinet") not in (lead,) else None
    bassoon = lower_ens.get("bassoon") if lower_ens.get("bassoon") not in (bass,) else None
    horn = lower_ens.get("horn")
    violin_2 = lower_ens.get("violin_2")
    viola = lower_ens.get("viola")
    contrabass = lower_ens.get("contrabass") or lower_ens.get("double_bass")

    # ── Melody → lead, with doublings ──
    if lead:
        lo, hi = _range_of(lead)
        for e in layer.principal_line:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[lead].append(_event_dict(e, p))
        # Flute doubles 8va in loud bars (climaxes shine)
        if flute and flute != lead:
            flo, fhi = _range_of(flute)
            for e in layer.principal_line:
                if e.pitch == "rest" or loudness.get(e.bar, 4) < 5:
                    continue
                p = _transpose_event_pitch(e.pitch, 12, flo, fhi, key)
                if p:
                    parts[flute].append(_event_dict(e, p))
        # Oboe doubles at unison in singing mid dynamics
        if oboe and oboe != lead:
            olo, ohi = _range_of(oboe)
            for e in layer.principal_line:
                if e.pitch == "rest" or not (3 <= loudness.get(e.bar, 4) <= 4):
                    continue
                p = _transpose_event_pitch(e.pitch, 0, olo, ohi, key)
                if p:
                    parts[oboe].append(_event_dict(e, p))

    # ── Bass → cello-class, contrabass 8vb at mf+ ──
    if bass:
        lo, hi = _range_of(bass)
        for e in layer.bass_foundation:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[bass].append(_event_dict(e, p))
        if contrabass and contrabass != bass:
            clo, chi = _range_of(contrabass)
            for e in layer.bass_foundation:
                if e.pitch == "rest" or loudness.get(e.bar, 4) < 4:
                    continue
                p = _transpose_event_pitch(e.pitch, -12, clo, chi, key)
                if p:
                    parts[contrabass].append(_event_dict(e, p))

    # ── Inner motion → violin_2 / viola split by register ──
    inner_high = violin_2 or _pick(["violin_2", "viola", "clarinet"], ensemble, taken)
    inner_low = viola if viola and viola != inner_high else None
    for e in layer.response_layer:
        if e.pitch == "rest":
            continue
        first = e.pitch[0] if isinstance(e.pitch, list) else e.pitch
        try:
            m = pitch_to_midi(first)
        except (ValueError, KeyError, TypeError):
            continue
        if m is None:
            continue
        target = inner_high if (m >= 60 or not inner_low) else inner_low
        if not target:
            continue
        lo, hi = _range_of(target)
        p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
        if p:
            parts[target].append(_event_dict(e, p))

    # ── Sustained wind/horn harmony condensed from inner motion ──
    pads = [i for i in (clarinet, bassoon, horn) if i and i not in (lead, bass)]
    if pads:
        by_bar: Dict[int, List[int]] = defaultdict(list)
        for e in layer.response_layer + layer.counter_reply:
            if e.pitch == "rest":
                continue
            for p in e.pitch if isinstance(e.pitch, list) else [e.pitch]:
                try:
                    m = pitch_to_midi(p)
                except (ValueError, KeyError, TypeError):
                    continue
                if m is not None:
                    by_bar[e.bar].append(m)
        bpb = layer.meter[0] * 4.0 / layer.meter[1] if layer.meter else 4.0
        pad_dur = beats_to_dur(bpb)
        for bar, midis in sorted(by_bar.items()):
            # Horn pads loud bars; clarinet+bassoon pad soft/mid bars
            chord = sorted(set(midis))
            if not chord:
                continue
            if loudness.get(bar, 4) >= 5 and horn and horn in pads:
                lo, hi = _range_of(horn)
                p = midi_to_pitch(_clamp_octave(chord[len(chord) // 2], lo, hi), key)
                parts[horn].append(
                    {
                        "bar": bar,
                        "beat": 1.0,
                        "pitch": p,
                        "duration": pad_dur,
                        "dynamic": None,
                        "articulation": None,
                        "slur": None,
                    }
                )
            else:
                for inst, idx in ((clarinet, -1), (bassoon, 0)):
                    if not inst:
                        continue
                    lo, hi = _range_of(inst)
                    p = midi_to_pitch(_clamp_octave(chord[idx], lo, hi), key)
                    parts[inst].append(
                        {
                            "bar": bar,
                            "beat": 1.0,
                            "pitch": p,
                            "duration": pad_dur,
                            "dynamic": None,
                            "articulation": None,
                            "slur": None,
                        }
                    )

    # ── Counter-melody → oboe (or viola) ──
    counter_inst = oboe or viola
    if counter_inst:
        lo, hi = _range_of(counter_inst)
        for e in layer.counter_reply:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[counter_inst].append(_event_dict(e, p))

    # ── Ornamental surface → flute when free, else stays with lead ──
    orn_inst = flute or lead
    if orn_inst:
        lo, hi = _range_of(orn_inst)
        for e in layer.ornamental_surface:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[orn_inst].append(_event_dict(e, p))

    for inst in parts:
        parts[inst].sort(key=lambda d: (d["bar"], d["beat"]))
    return parts
