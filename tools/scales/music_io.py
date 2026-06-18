"""
MusicIO — MusicXML and MIDI parsing helpers.

Provides functions to read existing scores into the SCALES data model
and to write LayerIR/EventIR to standard formats.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import EventIR, LayerEvent, LayerIR


def parse_musicxml_to_events(path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Parse a MusicXML file into raw event dicts.

    Returns:
        (events, instruments) where events are dicts with keys:
        instrument, bar, beat, pitch, duration, dynamic
    """
    try:
        import music21
    except ImportError:
        raise ImportError(
            "music21 is required for MusicXML parsing. Install with: pip install music21"
        )

    score = music21.converter.parse(path)
    events = []
    instruments = []

    for part in score.parts:
        inst_name = part.partName or f"Part_{len(instruments)}"
        instruments.append(inst_name)

        for measure in part.getElementsByClass("Measure"):
            bar_num = measure.number
            for element in measure.flatten().notesAndRests:
                beat = float(element.offset) + 1.0  # music21 offsets are 0-based

                if element.isRest:
                    events.append(
                        {
                            "instrument": inst_name,
                            "bar": bar_num,
                            "beat": beat,
                            "pitch": "rest",
                            "duration": _m21_duration_to_code(element.duration),
                            "dynamic": None,
                        }
                    )
                elif element.isChord:
                    pitches = [str(p) for p in element.pitches]
                    events.append(
                        {
                            "instrument": inst_name,
                            "bar": bar_num,
                            "beat": beat,
                            "pitch": pitches,
                            "duration": _m21_duration_to_code(element.duration),
                            "dynamic": _get_dynamic(element),
                        }
                    )
                elif element.isNote:
                    events.append(
                        {
                            "instrument": inst_name,
                            "bar": bar_num,
                            "beat": beat,
                            "pitch": str(element.pitch),
                            "duration": _m21_duration_to_code(element.duration),
                            "dynamic": _get_dynamic(element),
                        }
                    )

    return events, instruments


def layer_ir_to_event_ir(layer_ir: LayerIR) -> List[EventIR]:
    """Convert LayerIR to a flat list of EventIR for engraving."""
    events = []

    # Piano: principal + ornamental → treble staff, bass + response → bass staff
    if layer_ir.instrumentation in ("solo_piano", "piano"):
        for event in layer_ir.principal_line:
            events.append(_layer_to_event(event, "treble", 1))
        for event in layer_ir.ornamental_surface:
            events.append(_layer_to_event(event, "treble", 2))
        for event in layer_ir.counter_reply:
            events.append(_layer_to_event(event, "treble", 2))
        for event in layer_ir.bass_foundation:
            events.append(_layer_to_event(event, "bass", 1))
        for event in layer_ir.response_layer:
            events.append(_layer_to_event(event, "bass", 2))
    else:
        # Orchestra: each layer gets its own staff
        for event in layer_ir.principal_line:
            events.append(_layer_to_event(event, "melody", 1))
        for event in layer_ir.foreground or []:
            events.append(_layer_to_event(event, "foreground", 1))
        for event in layer_ir.countermelody or []:
            events.append(_layer_to_event(event, "counter", 1))
        for event in layer_ir.harmonic_mass or []:
            events.append(_layer_to_event(event, "harmony", 1))
        for event in layer_ir.bass_foundation:
            events.append(_layer_to_event(event, "bass", 1))

    # Sort by bar, beat, staff
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))
    return events


def _layer_to_event(event: LayerEvent, staff: str, voice: int) -> EventIR:
    """Convert a LayerEvent to an EventIR."""
    return EventIR(
        staff=staff,
        bar=event.bar,
        beat=event.beat,
        pitch=event.pitch,
        duration=event.duration,
        voice=voice,
        role=event.role,
        source_layer=event.source_layer or "",
        dynamic=event.dynamic,
        articulation=event.articulation,
        ornament=event.ornament,
        tie=event.tie,
        slur=event.slur,
        hairpin=event.hairpin,
        expression=event.expression,
    )


def _m21_duration_to_code(dur) -> str:
    """Convert music21 Duration to SCALES duration code."""
    ql = dur.quarterLength
    mapping = {
        4.0: "w",
        3.0: "dh",
        2.0: "h",
        1.5: "dq",
        1.0: "q",
        0.75: "de",
        0.5: "e",
        0.375: "ds",
        0.25: "s",
        0.125: "t",
    }
    # Find closest
    best = "q"
    best_diff = abs(ql - 1.0)
    for val, code in mapping.items():
        diff = abs(ql - val)
        if diff < best_diff:
            best_diff = diff
            best = code
    return best


def _get_dynamic(element) -> Optional[str]:
    """Extract dynamic from a music21 element."""
    try:
        dynamics = element.getContextByClass("Dynamic")
        if dynamics:
            return dynamics.value
    except Exception:
        pass
    return None
