"""
MusicIO — MusicXML and MIDI parsing helpers.

Provides functions to read existing scores into the SCALES data model
and to write LayerIR/EventIR to standard formats.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import EventIR, LayerEvent, LayerIR, is_keyboard


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
        # Part names are not unique. A piano grand staff is TWO parts both
        # called "Piano", so keying anything by name collapses the two hands
        # into one — every consumer that split treble from bass by instrument
        # name saw a single part and put the whole score in one hand. Number
        # the duplicates.
        base = part.partName or part.id or f"Part_{len(instruments) + 1}"
        inst_name = str(base)
        if inst_name in instruments:
            n = 2
            while f"{base}-{n}" in instruments:
                n += 1
            inst_name = f"{base}-{n}"
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
                            **_get_marks(element),
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
                            **_get_marks(element),
                        }
                    )

    return events, instruments


def layer_ir_to_event_ir(layer_ir: LayerIR) -> List[EventIR]:
    """Convert LayerIR to a flat list of EventIR for engraving."""
    events = []

    # Piano: principal + ornamental → treble staff, bass + response → bass staff
    # One decider (models.is_keyboard) — see the note there on why unknown
    # spellings resolve to keyboard rather than ensemble.
    if is_keyboard(layer_ir):
        for event in layer_ir.principal_line:
            events.append(_layer_to_event(event, "treble", 1))
        # counter_reply and ornamental_surface are DIFFERENT voices. Filing both
        # as treble voice 2 put two independent lines in one music21 Voice at
        # overlapping offsets, which serializes without a backup and spills past
        # the barline — the same class of defect the pedal-under-figuration fix
        # addressed for the left hand.
        for event in layer_ir.counter_reply:
            events.append(_layer_to_event(event, "treble", 2))
        orn_voice = 3 if layer_ir.counter_reply else 2
        for event in layer_ir.ornamental_surface:
            events.append(_layer_to_event(event, "treble", orn_voice))
        for event in layer_ir.bass_foundation:
            events.append(_layer_to_event(event, "bass", 1))
        for event in layer_ir.response_layer:
            events.append(_layer_to_event(event, "bass", 2))
        # Third and fourth voices per hand, each on its own numbered staff voice.
        for name, evs in (getattr(layer_ir, "inner_voices", None) or {}).items():
            staff = "treble" if name.startswith("treble") else "bass"
            voice = int(name[-1]) if name[-1].isdigit() else 3
            for event in evs or []:
                events.append(_layer_to_event(event, staff, voice))
    else:
        # Orchestra: each layer gets its own staff. EVERY layer must be emitted —
        # rhythmic_motor, color_layer, punctuation, response_layer, counter_reply
        # and ornamental_surface used to be silently dropped here, so an
        # orchestrated section lost whole instrumental parts on the way to the
        # score with no error anywhere.
        for staff, layer in (
            ("melody", layer_ir.principal_line),
            ("foreground", layer_ir.foreground),
            ("counter", layer_ir.countermelody),
            ("counter_reply", layer_ir.counter_reply),
            ("harmony", layer_ir.harmonic_mass),
            ("response", layer_ir.response_layer),
            ("motor", layer_ir.rhythmic_motor),
            ("color", layer_ir.color_layer),
            ("punctuation", layer_ir.punctuation),
            ("ornament", layer_ir.ornamental_surface),
            ("bass", layer_ir.bass_foundation),
        ):
            for event in layer or []:
                events.append(_layer_to_event(event, staff, 1))

    # Sort by bar, beat, staff
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))
    return events


def _layer_to_event(event: LayerEvent, staff: str, voice: int) -> EventIR:
    """Convert a LayerEvent to an EventIR.

    Every notation field on LayerEvent must be forwarded. This conversion is
    the single choke point between "what the agent wrote" and "what gets
    engraved": a field missing from this list is a mark that vanishes with no
    error anywhere, which is how ``expression`` used to be lost.
    """
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
        technique=getattr(event, "technique", None),
        pedal=getattr(event, "pedal", None),
        fingering=getattr(event, "fingering", None),
    )


def _m21_duration_to_code(dur) -> str:
    """Convert a music21 Duration to a SCALES duration code.

    Delegates to ``duration.beats_to_dur``, which knows tuplets. The old local
    table had no tuplet entries, so every triplet read out of a real score was
    rounded to the nearest 16th — silently corrupting the rhythm of any ingested
    reference material.
    """
    from .duration import beats_to_dur

    return beats_to_dur(dur.quarterLength)


def _get_marks(element) -> Dict[str, Any]:
    """Everything the source note is MARKED with, beyond its dynamic.

    The extractor read pitch, duration and dynamic and nothing else, so every
    mode that loads a source score — `reduce_to_piano`, `orchestrate`,
    `variation`, `style_transfer`, `continue_piece`, five of the six — saw the
    music with its articulation, phrasing, ornaments and ties stripped off. A
    Clara Schumann polonaise carrying 27 slurs reduced to a piano part carrying
    none: the reduction could not preserve phrasing it was never shown.

    Slurs are SPANNERS, not note attributes, which is why reading
    ``element.articulations`` alone never found them.
    """
    out: Dict[str, Any] = {}

    arts = [a.name for a in (getattr(element, "articulations", None) or []) if getattr(a, "name", None)]
    if arts:
        out["articulation"] = arts[0].replace(" ", "_")

    exprs = [
        type(e).__name__.lower()
        for e in (getattr(element, "expressions", None) or [])
        if type(e).__name__.lower() in _ORNAMENT_NAMES
    ]
    if exprs:
        out["ornament"] = exprs[0]

    tie = getattr(element, "tie", None)
    if tie is not None and getattr(tie, "type", None):
        out["tie"] = tie.type

    try:
        for sp in element.getSpannerSites():
            if type(sp).__name__ != "Slur":
                continue
            if sp.isFirst(element):
                out["slur"] = "start"
            elif sp.isLast(element):
                out["slur"] = "stop"
            break
    except Exception:
        pass  # a spanner music21 cannot resolve must not lose the note

    return out


_ORNAMENT_NAMES = {
    "trill",
    "mordent",
    "invertedmordent",
    "turn",
    "invertedturn",
    "appoggiatura",
    "acciaccatura",
    "schleifer",
    "fermata",
}


def _get_dynamic(element) -> Optional[str]:
    """Extract dynamic from a music21 element."""
    try:
        dynamics = element.getContextByClass("Dynamic")
        if dynamics:
            return dynamics.value
    except Exception:
        pass
    return None
