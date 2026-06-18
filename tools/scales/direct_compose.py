"""
Direct composition — Claude writes notes, Python assembles.

Bypasses the SCALES engine entirely. Claude specifies every note
in a compact bar-by-bar format, and this module converts it to
LayerIR for assembly into MusicXML.

Format per bar:
{
    "rh": "(C5q D5e:tr E5e) [F5,A5]q~ [F5,A5]q",
    "lh": "<C3e G3e E3e G3e! C3e G3e E3e G3e",
    "dyn": "p",           # optional dynamic for this bar
    "art": None,          # optional articulation
}

Shorthand grammar (whitespace-separated tokens):
    C5q          note: pitch + duration code (w h q e s t, dotted: dh dq de ds)
    rest_q       rest (also r_q)
    [C5,E5,G5]q  chord — comma-separated pitches in brackets, no spaces
    (  ...  )    slur: '(' prefix starts, ')' suffix stops
    C5q~         tie start (the next same-pitch note auto-receives the stop)
    <C5q         crescendo hairpin starts on this note
    >C5q         diminuendo hairpin starts on this note
    C5q!         hairpin stops on this note
    C5q:tr       ornament/articulation/dynamic suffixes (stackable):
                 :tr :mord :turn :grace :ferm
                 :stacc :acc :ten :marc
                 :pp :p :mp :mf :f :ff :sfz
Example bar (RH): "(<C5e D5e E5e F5e G5q!:tr) [E5,G5]h:p"
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from .models import LayerEvent, LayerIR

_DUR_CODES = ["ddh", "ddq", "dde", "dh", "dq", "de", "ds", "w", "h", "q", "e", "s", "t"]

_ORNAMENTS = {
    "tr": "trill",
    "trill": "trill",
    "mord": "mordent",
    "turn": "turn",
    "grace": "grace",
    "ferm": "fermata",
}
_ARTICULATIONS = {
    "stacc": "staccato",
    "acc": "accent",
    "ten": "tenuto",
    "marc": "marcato",
    "leg": "legato",
}
_DYNAMICS = {"ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "sfz", "fp"}


def _parse_token(tok: str) -> Optional[Dict[str, Any]]:
    """Parse one shorthand token into an event dict, or None if empty."""
    ev: Dict[str, Any] = {
        "pitch": None,
        "dur": "q",
        "tie": None,
        "slur": None,
        "ornament": None,
        "articulation": None,
        "hairpin": None,
        "dynamic": None,
    }

    # Prefix flags
    while tok and tok[0] in "(<>":
        if tok[0] == "(":
            ev["slur"] = "start"
        elif tok[0] == "<":
            ev["hairpin"] = "cresc_start"
        elif tok[0] == ">":
            ev["hairpin"] = "dim_start"
        tok = tok[1:]

    # Suffix flags and `:xxx` modifiers, in any interleaving
    # (e.g. "G5q!:tr)" or "C5q:tr~")
    import re

    while tok:
        ch = tok[-1]
        if ch == ")":
            ev["slur"] = "stop" if ev["slur"] != "start" else ev["slur"]
            tok = tok[:-1]
            continue
        if ch == "~":
            ev["tie"] = "start"
            tok = tok[:-1]
            continue
        if ch == "!":
            ev["hairpin"] = ev["hairpin"] or "stop"
            tok = tok[:-1]
            continue
        m = re.search(r":([a-zA-Z]+)$", tok)
        if m:
            mod = m.group(1).lower()
            if mod in _ORNAMENTS:
                ev["ornament"] = _ORNAMENTS[mod]
            elif mod in _ARTICULATIONS:
                ev["articulation"] = _ARTICULATIONS[mod]
            elif mod in _DYNAMICS:
                ev["dynamic"] = mod
            # Unknown modifiers are stripped and ignored
            tok = tok[: m.start()]
            continue
        break

    if not tok:
        return None

    # Rest
    if tok.startswith("rest") or (tok.startswith("r") and "_" in tok):
        dur = tok.split("_")[1] if "_" in tok else "q"
        ev["pitch"], ev["dur"] = "rest", dur
        return ev

    # Chord: [C5,E5,G5]dur
    if tok.startswith("["):
        close = tok.find("]")
        if close == -1:
            return None
        pitches = [p.strip() for p in tok[1:close].split(",") if p.strip()]
        dur = tok[close + 1 :] or "q"
        ev["pitch"] = pitches if len(pitches) > 1 else (pitches[0] if pitches else None)
        ev["dur"] = dur if dur in _DUR_CODES else "q"
        return ev if ev["pitch"] else None

    # Note: pitch + duration suffix (longest match first)
    for dur_code in _DUR_CODES:
        if tok.endswith(dur_code) and len(tok) > len(dur_code):
            ev["pitch"] = tok[: -len(dur_code)]
            ev["dur"] = dur_code
            return ev
    # No duration suffix — default quarter
    ev["pitch"] = tok
    return ev


def _parse_shorthand(s: str) -> List[Dict[str, Any]]:
    """Parse a shorthand string into event dicts (see module docstring)."""
    events = []
    for tok in s.strip().split():
        ev = _parse_token(tok)
        if ev:
            events.append(ev)
    return events


def _normalize(seq: Union[str, List]) -> List[Dict[str, Any]]:
    """Accept shorthand strings, legacy (pitch, dur) tuples, or dicts."""
    if isinstance(seq, str):
        return _parse_shorthand(seq)
    out = []
    for item in seq:
        if isinstance(item, dict):
            base = {
                "pitch": None,
                "dur": "q",
                "tie": None,
                "slur": None,
                "ornament": None,
                "articulation": None,
                "hairpin": None,
                "dynamic": None,
            }
            base.update(item)
            out.append(base)
        else:  # legacy tuple
            pitch, dur = item
            out.append(
                {
                    "pitch": pitch,
                    "dur": dur,
                    "tie": None,
                    "slur": None,
                    "ornament": None,
                    "articulation": None,
                    "hairpin": None,
                    "dynamic": None,
                }
            )
    return out


def _resolve_ties(events: List[LayerEvent]) -> None:
    """Auto-close ties: a tie-start's next same-pitch event gets the stop."""
    for i, e in enumerate(events):
        if e.tie != "start":
            continue
        for nxt in events[i + 1 :]:
            if nxt.pitch == e.pitch:
                nxt.tie = "continue" if nxt.tie == "start" else "stop"
                break


def compose_phrase(
    bars: List[Dict],
    key: str = "Gm",
    bar_start: int = 1,
    phrase_id: str = "",
    meter: Tuple[int, int] = (4, 4),
) -> LayerIR:
    """Convert Claude's bar-by-bar composition to LayerIR.

    Args:
        bars: List of dicts, one per bar. Each has:
            rh: str (shorthand) or list — right hand notes
            lh: str (shorthand) or list — left hand notes
            dyn: optional str — dynamic marking for this bar
        key: Key string (e.g., "Gm", "Bb", "g_minor")
        bar_start: Starting bar number
        phrase_id: Phrase identifier
        meter: Time signature

    Returns:
        LayerIR with principal_line and bass_foundation populated.
    """
    from .duration import DURATION_VALUES

    layer = LayerIR(
        phrase_id=phrase_id,
        instrumentation="solo_piano",
        key=key,
        meter=meter,
        bar_count=len(bars),
    )

    for bar_idx, bar_data in enumerate(bars):
        bar_num = bar_start + bar_idx
        dyn = bar_data.get("dyn")

        # Right hand → principal_line
        beat_cursor = 1.0
        for i, ev in enumerate(_normalize(bar_data.get("rh", []))):
            dur_beats = DURATION_VALUES.get(ev["dur"], 1.0)
            layer.principal_line.append(
                LayerEvent(
                    bar=bar_num,
                    beat=round(beat_cursor, 4),
                    pitch=ev["pitch"],
                    duration=ev["dur"],
                    role="ornamental" if ev["ornament"] == "grace" else "structural",
                    dynamic=ev["dynamic"] or (dyn if i == 0 else None),
                    articulation=ev["articulation"],
                    ornament=ev["ornament"],
                    tie=ev["tie"],
                    slur=ev["slur"],
                    hairpin=ev["hairpin"],
                    source_layer="principal_line",
                )
            )
            if ev["ornament"] != "grace":  # grace notes take no time
                beat_cursor += dur_beats

        # Left hand → split between bass_foundation (beat 1) and response_layer
        beats_per_bar = meter[0] * 4.0 / meter[1]
        lh_events = _normalize(bar_data.get("lh", []))
        # Pedal semantics: a full-bar first event followed by more events is a
        # sustained bass UNDER the figuration, not before it — the figuration
        # re-anchors at beat 1 (sequential parsing would overflow the bar).
        lh_first_is_pedal = (
            len(lh_events) > 1 and DURATION_VALUES.get(lh_events[0]["dur"], 1.0) >= beats_per_bar
        )
        beat_cursor = 1.0
        for i, ev in enumerate(lh_events):
            dur_beats = DURATION_VALUES.get(ev["dur"], 1.0)
            if i == 1 and lh_first_is_pedal:
                beat_cursor = 1.0
            # First note → bass_foundation, rest → response_layer
            target = layer.bass_foundation if i == 0 else layer.response_layer
            target.append(
                LayerEvent(
                    bar=bar_num,
                    beat=round(beat_cursor, 4),
                    pitch=ev["pitch"],
                    duration=ev["dur"],
                    role="structural" if i == 0 else "arpeggiated_fill",
                    dynamic=ev["dynamic"] or (dyn if i == 0 else None),
                    articulation=ev["articulation"],
                    ornament=ev["ornament"],
                    tie=ev["tie"],
                    slur=ev["slur"],
                    hairpin=ev["hairpin"],
                    source_layer="bass_foundation" if i == 0 else "response_layer",
                )
            )
            if ev["ornament"] != "grace":
                beat_cursor += dur_beats

    _resolve_ties(layer.principal_line)
    _resolve_ties(
        sorted(layer.bass_foundation + layer.response_layer, key=lambda e: (e.bar, e.beat))
    )
    return layer


def merge_phrases(
    phrases: List[LayerIR], key: str = "Gm", meter: Tuple[int, int] = (4, 4), piece_id: str = ""
) -> LayerIR:
    """Merge multiple phrase LayerIRs into one."""
    merged = LayerIR(
        phrase_id=piece_id,
        instrumentation="solo_piano",
        key=key,
        meter=meter,
        bar_count=sum(p.bar_count for p in phrases),
    )
    for p in phrases:
        merged.principal_line.extend(p.principal_line)
        merged.bass_foundation.extend(p.bass_foundation)
        merged.response_layer.extend(p.response_layer)
        merged.counter_reply.extend(p.counter_reply)
        merged.ornamental_surface.extend(p.ornamental_surface)
    return merged
