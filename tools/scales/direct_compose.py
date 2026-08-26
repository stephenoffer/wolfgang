"""
Direct composition — Claude writes notes, Python assembles.

Bypasses the SCALES engine entirely. Claude specifies every note
in a compact bar-by-bar format, and this module converts it to
LayerIR for assembly into MusicXML.

Format per bar:
{
    "rh": "(C5q D5e:tr E5e) [F5,A5]q~ [F5,A5]q",
    "lh": "<C3e G3e E3e G3e! C3e G3e E3e G3e",
    "dyn": "p",           # optional dynamic for this bar (printed ONCE, not
                          # once per staff)
    "art": "stacc",       # optional articulation applied to every sounding
                          # note in the bar; a per-note mark overrides it
    "text": "dolce",      # optional italic character text over the bar
    "ped": True,          # optional pedal-down mark at the bar's first LH note
    "pickup": True,       # optional: this bar is an anacrusis (partial measure);
                          # its content right-aligns to the barline
}

Shorthand grammar (whitespace-separated tokens):
    C5q          note: pitch + duration code
                 plain:   w h q e s t x   (whole … 32nd, 64th)
                 dotted:  dw dh dq de ds dt   double-dotted: ddh ddq dde
                 tuplets: trip_q trip_e trip_s trip_t (also quint_/sext_/sept_)
                          — three trip_e fill one beat exactly
    rest_q       rest (also r_q, rest_trip_e)
    [C5,E5,G5]q  chord — comma-separated pitches in brackets, no spaces
    (  ...  )    slur: '(' prefix starts, ')' suffix stops
    a // b // c  independent simultaneous voices in ONE hand (any number; each
                 parses from beat 1 and must fill the bar on its own)
    C5q~         tie start (the next same-pitch note auto-receives the stop).
                 Write a note held over the barline as `C5h~` at the end of one
                 bar and `C5h` at the start of the next.
    <C5q         crescendo hairpin starts on this note
    >C5q         diminuendo hairpin starts on this note
    C5q!         hairpin stops on this note
    C5q:tr       stackable `:xxx` suffixes —
                 ornaments:     :tr :mord :imord/:prall :turn :iturn :schl
                                :grace :acci :appo :ferm
                 articulations: :stacc :stacciss :port :spicc :acc :ten :marc
                                :breath :caes
                 techniques:    :arp :arpu :arpd (rolled chord) :trem
                                :gliss/:glissend :8va :8vb :loco
                 dynamics:      :pp :p :mp :mf :f :ff :sfz :fp :sf …
                 pedal:         :ped :pedup :pedch
                 character:     :dolce :cantabile :espressivo :leggiero
                                :sotto_voce :agitato :morendo … (italic text)
                 fingering:     :fin3 or bare :3
Example bar (RH): "(<C5e D5e E5e F5e G5q!:tr) [E5,G5]h:p"
Rolled chord with pedal: {'rh': '[C5,E5,G5,C6]h:arp', 'lh': 'C2h:ped'}
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union

from .duration import (
    DURATION_VALUES,
    GRACE_ORNAMENTS,
    TRIPLET_OF,
    dur_codes_longest_first,
    normalize_dot_suffix,
)
from .models import LayerEvent, LayerIR

# Longest-first so "trip_e" wins over "e" and "ds" over "s" — a short-first scan
# turned every "C5trip_e" into a 32nd note.
_DUR_CODES = dur_codes_longest_first()

_ORNAMENTS = {
    "tr": "trill",
    "trill": "trill",
    "mord": "mordent",
    "mordent": "mordent",
    # An INVERTED mordent (the "prall", the single most common Classical
    # ornament after the trill) had no spelling at all, so every one the agent
    # wanted became a plain mordent or was dropped.
    "imord": "inverted_mordent",
    "prall": "inverted_mordent",
    "pralltriller": "inverted_mordent",
    "turn": "turn",
    "iturn": "inverted_turn",
    "gruppetto": "turn",
    "schl": "schleifer",
    "slide": "schleifer",
    "grace": "grace",
    # Slashed (crushed) vs unslashed (accented, takes time from the principal)
    # are different ornaments that engrave differently and sound different.
    "acci": "acciaccatura",
    "appo": "appoggiatura",
    "ferm": "fermata",
    "fermata": "fermata",
}
_ARTICULATIONS = {
    "stacc": "staccato",
    "acc": "accent",
    "ten": "tenuto",
    "marc": "marcato",
    "leg": "legato",
    # Wedge/dash staccatissimo, portato (the dot-under-slur "carried" touch),
    # spiccato, and the breath/caesura marks that make a phrase breathe on the
    # page as well as in the playback.
    "stacciss": "staccatissimo",
    "wedge": "staccatissimo",
    "port": "portato",
    "spicc": "spiccato",
    "breath": "breath",
    "caes": "caesura",
    "stress": "stress",
    "unstress": "unstress",
}
_DYNAMICS = {
    "ppp",
    "pp",
    "p",
    "mp",
    "mf",
    "f",
    "ff",
    "fff",
    "pppp",
    "ffff",
    "sfz",
    "sf",
    "sffz",
    "fp",
    "fz",
    "mfp",
    "pf",
    "rfz",
}
# Playing techniques: neither articulation nor ornament. A rolled chord is the
# single most characteristic piano notation there is and was inexpressible.
_TECHNIQUES = {
    "arp": "arpeggio",
    "roll": "arpeggio",
    "arpu": "arpeggio_up",
    "arpd": "arpeggio_down",
    "trem": "tremolo",
    "gliss": "gliss_start",
    "glissend": "gliss_stop",
    "8va": "8va",
    "8vb": "8vb",
    "loco": "octave_stop",
}
# Pedal marks written on a note.
_PEDALS = {"ped": "down", "pedup": "up", "pedch": "change"}
# Character words that engrave as italic text over the note. A real score is
# full of these and the shorthand had no way to write one.
_EXPRESSIONS = {
    "dolce",
    "cantabile",
    "espressivo",
    "espress",
    "grazioso",
    "scherzando",
    "leggiero",
    "sostenuto",
    "marcato_text",
    "tranquillo",
    "agitato",
    "appassionato",
    "risoluto",
    "semplice",
    "misterioso",
    "lamentoso",
    "giocoso",
    "maestoso",
    "teneramente",
    "mesto",
    "con_forza",
    "sotto_voce",
    "una_corda",
    "pesante",
    "delicato",
    "brillante",
    "calando",
    "smorzando",
    "morendo",
    "perdendosi",
    "slancio",
    "amoroso",
    "doloroso",
    "energico",
    "flebile",
    "nobilmente",
    "placido",
    "rubato",
    "sempre_legato",
    "ben_marcato",
}


# The canonical set lives in duration.py — see the note there on why.
_GRACE_ORNAMENTS = GRACE_ORNAMENTS


def _expression_text(word: str) -> str:
    """Render an expression keyword as the italic text an engraver would print."""
    return word.replace("_text", "").replace("_", " ")


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
        "tuplet": None,
        "technique": None,
        "pedal": None,
        "expression": None,
        "fingering": None,
    }

    # Slur start/stop are tracked separately so a one-note slur "(C5q)" can be
    # recognized and dropped instead of leaving a dangling start that swallows
    # every following note into the spanner.
    slur_start = slur_stop = False

    # Prefix flags
    while tok and tok[0] in "(<>":
        if tok[0] == "(":
            slur_start = True
        elif tok[0] == "<":
            ev["hairpin"] = "cresc_start"
        elif tok[0] == ">":
            ev["hairpin"] = "dim_start"
        tok = tok[1:]

    # Suffix flags and `:xxx` modifiers, in any interleaving
    # (e.g. "G5q!:tr)" or "C5q:tr~")
    while tok:
        ch = tok[-1]
        if ch == ")":
            slur_stop = True
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
        # Tolerate hairpin marks written as a suffix (e.g. "Db4q)<") — the
        # grammar documents '<'/'>' as a prefix, but accept them either side.
        if ch == "<":
            ev["hairpin"] = ev["hairpin"] or "cresc_start"
            tok = tok[:-1]
            continue
        if ch == ">":
            ev["hairpin"] = ev["hairpin"] or "dim_start"
            tok = tok[:-1]
            continue
        # Tolerate a trailing tuplet marker written after the duration
        # ("F5e_trip", "Ab5s_triplet") — normalized onto a real tuplet code
        # below rather than dropped, which used to silently halve the value.
        mt = re.search(r"_*trip(?:let)?_*$", tok)
        if mt and mt.start() > 0 and "trip_" not in tok:
            ev["tuplet"] = "triplet"
            tok = tok[: mt.start()]
            continue
        # A `:xxx` modifier. Digits and underscores are allowed so `:8va`,
        # `:sotto_voce` and the fingering form `:fin3` all parse; a bare
        # `:3` is a fingering.
        m = re.search(r":([a-zA-Z0-9_]+)$", tok)
        if m:
            mod = m.group(1).lower()
            if mod in _ORNAMENTS:
                ev["ornament"] = _ORNAMENTS[mod]
            elif mod in _ARTICULATIONS:
                ev["articulation"] = _ARTICULATIONS[mod]
            elif mod in _DYNAMICS:
                ev["dynamic"] = mod
            elif mod in _TECHNIQUES:
                ev["technique"] = _TECHNIQUES[mod]
            elif mod in _PEDALS:
                ev["pedal"] = _PEDALS[mod]
            elif mod in _EXPRESSIONS:
                ev["expression"] = _expression_text(mod)
            elif mod.startswith("fin") and mod[3:].isdigit():
                ev["fingering"] = mod[3:]
            elif mod.isdigit() and len(mod) <= 2:
                ev["fingering"] = mod
            # Unknown modifiers are stripped and ignored
            tok = tok[: m.start()]
            continue
        break

    # A slur needs two notes: "(C5q)" on its own is not a slur, and emitting the
    # start alone left the spanner open across the rest of the phrase.
    if slur_start and not slur_stop:
        ev["slur"] = "start"
    elif slur_stop and not slur_start:
        ev["slur"] = "stop"

    if not tok:
        return None

    # Rest — "rest_q", "r_q", "rest_trip_s" (split once: the duration code may
    # itself contain an underscore).
    if tok.startswith("rest") or (tok.startswith("r") and "_" in tok):
        dur = tok.split("_", 1)[1] if "_" in tok else "q"
        ev["pitch"], ev["dur"] = "rest", _normalize_dur(dur, ev)
        return ev

    # Chord: [C5,E5,G5]dur
    if tok.startswith("["):
        close = tok.find("]")
        if close == -1:
            return None
        pitches = [p.strip() for p in tok[1:close].split(",") if p.strip()]
        dur = tok[close + 1 :] or "q"
        ev["pitch"] = pitches if len(pitches) > 1 else (pitches[0] if pitches else None)
        ev["dur"] = _normalize_dur(dur, ev)
        return ev if ev["pitch"] else None

    # Note: pitch + duration suffix (longest match first). A trailing-dot
    # spelling ("C5h.") is split off first so "h." is not read as bare "h".
    pitch, dur = tok, "q"
    body, dots = tok.rstrip("."), "." * (len(tok) - len(tok.rstrip(".")))
    for dur_code in _DUR_CODES:
        if body.endswith(dur_code) and len(body) > len(dur_code):
            pitch, dur = body[: -len(dur_code)], dur_code + dots
            break

    # Salvage: if junk is embedded after the pitch (a mis-encoded grace/
    # ornament, e.g. "Bb5dq:grace:Ab5"), extract the leading valid pitch token
    # so the note still engraves instead of being silently dropped at assembly.
    mp = re.match(r"^([A-Ga-g](?:##|#|bb|b|--|-)?[0-9])(.+)$", pitch)
    if mp:
        tail = mp.group(2).lstrip(":")
        pitch = mp.group(1)
        for dur_code in _DUR_CODES:  # longest-first, so "trip_e" beats "e"
            if tail.startswith(dur_code):
                rest_after = tail[len(dur_code) :]
                dur = dur_code + ("." * (len(rest_after) - len(rest_after.lstrip("."))))
                break

    ev["pitch"], ev["dur"] = pitch, _normalize_dur(dur, ev)
    return ev


def _normalize_dur(dur: str, ev: Dict[str, Any]) -> str:
    """Resolve a duration code, folding a parsed tuplet marker into it.

    ``C5e_trip`` arrives here as dur='e' with ev['tuplet']='triplet' and leaves
    as 'trip_e'. Unknown codes fall back to a quarter (as before) rather than
    silently producing a zero-length event.
    """
    dur = normalize_dot_suffix(dur)
    if ev.get("tuplet") == "triplet" and dur in TRIPLET_OF:
        return TRIPLET_OF[dur]
    return dur if dur in DURATION_VALUES else "q"


def _parse_shorthand(s: str) -> List[Dict[str, Any]]:
    """Parse a shorthand string into event dicts (see module docstring)."""
    events = []
    for tok in s.strip().split():
        ev = _parse_token(tok)
        if ev:
            events.append(ev)
    return events


_EVENT_DEFAULTS: Dict[str, Any] = {
    "pitch": None,
    "dur": "q",
    "tie": None,
    "slur": None,
    "ornament": None,
    "articulation": None,
    "hairpin": None,
    "dynamic": None,
    "technique": None,
    "pedal": None,
    "expression": None,
    "fingering": None,
}


def _normalize(seq: Union[str, List]) -> List[Dict[str, Any]]:
    """Accept shorthand strings, legacy (pitch, dur) tuples, or dicts.

    The default key set is shared with the token parser so a dict-authored bar
    and a shorthand-authored bar carry exactly the same fields — a per-call
    hand-written default dict is how the notation fields kept getting dropped
    on the dict path only.
    """
    if isinstance(seq, str):
        return _parse_shorthand(seq)
    out = []
    for item in seq:
        base = dict(_EVENT_DEFAULTS)
        if isinstance(item, dict):
            base.update(item)
        else:  # legacy (pitch, dur) tuple
            base["pitch"], base["dur"] = item
        out.append(base)
    return out


def _resolve_ties(events: List[LayerEvent]) -> None:
    """Auto-close ties on the IMMEDIATELY following event, or drop the tie.

    A tie joins two adjacent soundings of the same pitch. Searching forward for
    the next same-pitch event anywhere in the phrase produced ties that jumped
    over intervening notes ("C5q~ D5q C5q" tied across the D5), which MusicXML
    cannot represent and MuseScore renders as a broken slur-like artifact. If the
    next event is not the same pitch there is nothing to tie to, so the tie is
    dropped rather than mis-bound.
    """
    for i, e in enumerate(events):
        if e.tie != "start":
            continue
        nxt = events[i + 1] if i + 1 < len(events) else None
        if nxt is not None and nxt.pitch == e.pitch and nxt.pitch != "rest":
            nxt.tie = "continue" if nxt.tie == "start" else "stop"
            # The far side of a tie is not a new attack, so it carries no attack
            # marking. A bar-level `art` used to stamp a staccato dot onto the
            # continuation of a tied note — a note that is never struck told to
            # be struck short, which is a contradiction on the page and an
            # audible re-articulation in the MIDI preview.
            nxt.articulation = None
            nxt.ornament = None
            nxt.dynamic = None
            nxt.technique = None
        elif nxt is None:
            # The LAST event of the phrase. Its partner lives in the next
            # phrase, which this function cannot see, so leave the start alone
            # for the assembler to bind (`_resolve_cross_phrase_ties`). Clearing
            # it here is what made an ELIDED cadence — the resolution held over
            # into the next phrase's downbeat — impossible to write: the one
            # place a tie matters most was the one place it was silently erased.
            pass
        else:
            e.tie = None


def _split_voices(hand) -> List[List[Dict]]:
    """Split a hand spec into independent simultaneous voices.

    A ``//`` in a shorthand string separates voices that sound together, each
    parsed from beat 1 (e.g. a sustained melody over a moving inner line in one
    hand: ``"Ab5h. Gb5q // Db5e Eb5e F5e Gb5e Ab5e Bb5e"``). A plain string or a
    token list is a single voice. This is what lets the agent write genuine
    two-voice-per-hand polyphony, not just block chords.
    """
    if isinstance(hand, str) and "//" in hand:
        return [_normalize(p) for p in hand.split("//") if p.strip()]
    return [_normalize(hand)]


def _infer_roles(tokens: List[Dict[str, Any]], default_role: str) -> List[str]:
    """Assign each note a real melodic role from its melodic context.

    "Every note carries a role" was not true: every RH note was tagged
    ``structural`` and every non-first LH note ``arpeggiated_fill``, so the role
    field was a constant and everything downstream that reads it (musicality
    metrics, non-chord-tone checks, voice-leading analysis) was reading noise.

    These are the roles derivable from the LINE alone, without a harmonic
    analysis: a note stepped into and out of in the same direction is passing;
    stepped away from and back is a neighbour; a note leapt into and resolved by
    step is an appoggiatura; a repeat of the previous pitch under a tie context
    is pedal support. Anything else keeps the caller's default.
    """
    from .pitch import pitch_to_midi

    def _midi(ev):
        p = ev.get("pitch")
        if not p or p == "rest":
            return None
        names = p if isinstance(p, list) else [p]
        vals = []
        for n in names:
            try:
                m = pitch_to_midi(n)
            except (ValueError, KeyError, TypeError):
                m = None
            if m is not None:
                vals.append(m)
        return max(vals) if vals else None

    mids = [_midi(t) for t in tokens]
    roles: List[str] = []
    for i, tok in enumerate(tokens):
        if tok.get("ornament") in _GRACE_ORNAMENTS:
            roles.append("ornamental")
            continue
        cur, prev = mids[i], (mids[i - 1] if i > 0 else None)
        nxt = mids[i + 1] if i + 1 < len(mids) else None
        if cur is None or prev is None or nxt is None:
            roles.append(default_role)
            continue
        approach, leave = cur - prev, nxt - cur
        if approach == 0:
            roles.append("pedal_support" if default_role != "structural" else "structural")
        elif abs(approach) <= 2 and abs(leave) <= 2 and approach * leave > 0:
            roles.append("passing")
        elif abs(approach) <= 2 and leave == -approach:
            roles.append("neighbor")
        elif abs(approach) > 2 and 0 < abs(leave) <= 2:
            roles.append("appoggiatura")
        elif abs(approach) > 2 and abs(leave) > 2:
            roles.append("arpeggiated_fill" if default_role != "structural" else "structural")
        else:
            roles.append(default_role)
    return roles


def _emit_voice(
    target,
    tokens,
    source_layer,
    bar_num,
    dyn,
    default_role,
    start_beat=None,
    bar_art=None,
    bar_text=None,
    bar_pedal=None,
):
    """Append one independent voice's events to ``target``, advancing its own
    beat cursor from beat 1 (so voices in the same hand are time-aligned).

    The cursor is an exact ``Fraction`` so a run of triplets lands on 1, 4/3,
    5/3, 2 rather than drifting; only the stored value is a rounded float (the IR
    is JSON), and the assembler recovers the exact position from it.

    ``bar_art`` / ``bar_text`` / ``bar_pedal`` are the bar-level defaults. The
    bar dict's ``art`` key was documented in this module's own docstring and then
    never read, so every bar-level articulation the agent wrote was silently
    discarded; a per-note mark always wins over the bar default.
    """
    beat_cursor = Fraction(1) if start_beat is None else Fraction(start_beat)
    roles = _infer_roles(tokens, default_role)
    for i, ev in enumerate(tokens):
        role = roles[i]
        is_grace = ev["ornament"] in _GRACE_ORNAMENTS
        target.append(
            LayerEvent(
                bar=bar_num,
                beat=round(float(beat_cursor), 6),
                pitch=ev["pitch"],
                duration=ev["dur"],
                role=role,
                dynamic=ev["dynamic"] or (dyn if i == 0 else None),
                # A bar-level articulation applies to the sounding notes, not to
                # rests and not to grace notes (a staccato dot on a grace note is
                # meaningless and clutters the page).
                articulation=ev["articulation"]
                or (bar_art if (ev["pitch"] != "rest" and not is_grace) else None),
                ornament=ev["ornament"],
                tie=ev["tie"],
                slur=ev["slur"],
                hairpin=ev["hairpin"],
                technique=ev.get("technique"),
                pedal=ev.get("pedal") or (bar_pedal if i == 0 else None),
                expression=ev.get("expression") or (bar_text if i == 0 else None),
                fingering=ev.get("fingering"),
                source_layer=source_layer,
            )
        )
        if not is_grace:  # grace notes take no time
            beat_cursor += DURATION_VALUES.get(ev["dur"], Fraction(1))


def _pickup_start_beat(bar_data, meter) -> Fraction:
    """Beat on which a pickup bar's content begins, right-aligned to the barline.

    A three-beat 4/4 pickup starts on beat 2. The longest SOUNDING voice sets the
    alignment so all voices of the anacrusis line up.

    A voice that is nothing but rests does not count. The other hand is normally
    silent under an upbeat, and writing that silence as ``rest_q`` — the obvious
    thing to write — made a lone eighth-note upbeat in 3/4 align as if it were a
    whole beat long, so it landed on beat 3 with an eighth of silence in front of
    it instead of on the second half of the beat.
    """
    capacity = Fraction(int(meter[0]) * 4, int(meter[1]))
    longest = Fraction(0)
    for hand in ("rh", "lh"):
        for voice in _split_voices(bar_data.get(hand, [])):
            if not any(ev.get("pitch") not in (None, "rest") for ev in voice):
                continue  # silence under the upbeat, not content
            total = sum(
                DURATION_VALUES.get(ev["dur"], Fraction(1))
                for ev in voice
                if ev.get("ornament") not in _GRACE_ORNAMENTS
            )
            longest = max(longest, Fraction(total))
    if longest <= 0 or longest >= capacity:
        return Fraction(1)
    return capacity - longest + 1


def _emit_extra_voices(layer, voices, staff: str, bar_num: int, pickup_start) -> None:
    """Third and further voices in one hand, each on its own numbered staff voice."""
    for i, tokens in enumerate(voices, start=3):
        name = f"{staff}{i}"
        layer.inner_voices.setdefault(name, [])
        _emit_voice(
            layer.inner_voices[name],
            tokens,
            name,
            bar_num,
            None,
            "structural",
            start_beat=pickup_start,
        )


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
        # Bar-level articulation / character text / pedal. ``art`` was documented
        # in this module's docstring and never read by anything.
        bar_art = _ARTICULATIONS.get(str(bar_data.get("art") or "").lower()) or (
            bar_data.get("art") if bar_data.get("art") in set(_ARTICULATIONS.values()) else None
        )
        raw_text = bar_data.get("text") or bar_data.get("expr")
        bar_text = _expression_text(str(raw_text).lower()) if raw_text else None
        raw_ped = bar_data.get("ped")
        bar_pedal = (
            "down"
            if raw_ped is True
            else (_PEDALS.get(str(raw_ped).lower(), str(raw_ped)) if raw_ped else None)
        )
        # An anacrusis: this bar is a PARTIAL measure, so its content is
        # right-aligned to the barline rather than starting on beat 1.
        pickup_start = _pickup_start_beat(bar_data, meter) if bar_data.get("pickup") else None
        if pickup_start is not None:
            layer.pickup_beats = float(
                Fraction(int(meter[0]) * 4, int(meter[1])) - (pickup_start - 1)
            )

        # Right hand: voice 0 → principal_line (the melody); any further '//'
        # voices → counter_reply (treble inner voice — rendered as staff voice 2).
        rh_voices = _split_voices(bar_data.get("rh", []))
        _emit_voice(
            layer.principal_line,
            rh_voices[0],
            "principal_line",
            bar_num,
            dyn,
            "structural",
            start_beat=pickup_start,
            bar_art=bar_art,
            bar_text=bar_text,
        )
        if len(rh_voices) > 1:
            _emit_voice(
                layer.counter_reply,
                rh_voices[1],
                "counter_reply",
                bar_num,
                None,
                "structural",
                start_beat=pickup_start,
                bar_art=bar_art,
            )
        # A third or fourth voice in the hand gets its OWN numbered voice. Merging
        # every extra voice into counter_reply stacked independent lines on top of
        # each other, so three-voice writing was impossible without hand-authored
        # LayerIR — which is why no generated piece has ever had real counterpoint.
        _emit_extra_voices(layer, rh_voices[2:], "treble", bar_num, pickup_start)

        # Left hand. Explicit '//' voices → bass_foundation + response_layer as
        # independent voices. Otherwise the single-stream pedal-under-figuration
        # split (backward compatible).
        beats_per_bar = Fraction(int(meter[0]) * 4, int(meter[1]))
        lh_voices = _split_voices(bar_data.get("lh", []))
        if len(lh_voices) > 1:
            _emit_voice(
                layer.bass_foundation,
                lh_voices[0],
                "bass_foundation",
                bar_num,
                None,
                "structural",
                start_beat=pickup_start,
                bar_art=bar_art,
                bar_pedal=bar_pedal,
            )
            _emit_voice(
                layer.response_layer,
                lh_voices[1],
                "response_layer",
                bar_num,
                None,
                "arpeggiated_fill",
                start_beat=pickup_start,
                bar_art=bar_art,
            )
            _emit_extra_voices(layer, lh_voices[2:], "bass", bar_num, pickup_start)
            continue
        lh_events = lh_voices[0]
        # Pedal semantics: a full-bar first event followed by more events is a
        # sustained bass UNDER the figuration, not before it — the figuration
        # re-anchors at beat 1 (sequential parsing would overflow the bar).
        lh_first_is_pedal = (
            len(lh_events) > 1
            and DURATION_VALUES.get(lh_events[0]["dur"], Fraction(1)) >= beats_per_bar
        )
        if not lh_first_is_pedal:
            # A plain single-stream left hand is ONE voice, so all of it is the
            # bass line. Splitting note[0] into bass_foundation and everything
            # else into response_layer meant every generated piece had a
            # bass_foundation of exactly one note per bar — a static whole-bar
            # drone by construction — while the actual moving bass was filed as
            # "arpeggiated fill" in a second voice that does not exist. Every
            # per-layer statistic, the voice-leading check (which reads
            # bass_foundation as the lower voice) and the engraved staff voicing
            # were all reading that artifact.
            _emit_voice(
                layer.bass_foundation,
                lh_events,
                "bass_foundation",
                bar_num,
                None,
                "structural",
                start_beat=pickup_start,
                bar_art=bar_art,
                bar_pedal=bar_pedal,
            )
            continue
        # Pedal note + figuration are two independent voices, so emit them
        # through the SAME emitter as every other voice. Hand-inlining a second
        # copy of the emit loop here is what silently dropped every new notation
        # field (technique, pedal, expression, fingering) from the left hand
        # whenever the bar used pedal-under-figuration.
        _emit_voice(
            layer.bass_foundation,
            lh_events[:1],
            "bass_foundation",
            bar_num,
            None,
            "structural",
            start_beat=pickup_start,
            bar_art=bar_art,
            bar_pedal=bar_pedal,
        )
        _emit_voice(
            layer.response_layer,
            lh_events[1:],
            "response_layer",
            bar_num,
            None,
            "arpeggiated_fill",
            start_beat=pickup_start,
            bar_art=bar_art,
        )

    _resolve_ties(layer.principal_line)
    _resolve_ties(layer.counter_reply)
    for _name, _evs in (layer.inner_voices or {}).items():
        _resolve_ties(_evs)
    # bass_foundation and response_layer are INDEPENDENT voices (voice 1 and 2
    # of the bass staff). Resolving ties over their merged, time-sorted union let
    # a tie in the pedal voice bind to the next figuration note that happened to
    # share its pitch — a tie between two different voices, which MusicXML
    # cannot represent and MuseScore draws as a stray hook.
    _resolve_ties(layer.bass_foundation)
    _resolve_ties(layer.response_layer)
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
    _PIANO = (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
    )
    _ORCH = (
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    )
    for p in phrases:
        for name in _PIANO:
            getattr(merged, name).extend(getattr(p, name) or [])
        # Orchestral layers default to None; merging used to skip them entirely,
        # so merging orchestrated phrases dropped six layers on the floor.
        for name in _ORCH:
            src = getattr(p, name, None)
            if not src:
                continue
            if getattr(merged, name, None) is None:
                setattr(merged, name, [])
            getattr(merged, name).extend(src)
        for name, evs in (getattr(p, "inner_voices", None) or {}).items():
            merged.inner_voices.setdefault(name, []).extend(evs)
        merged.instrumentation = p.instrumentation or merged.instrumentation
    return merged
