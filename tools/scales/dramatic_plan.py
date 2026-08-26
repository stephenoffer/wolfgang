"""The dramatic plan: what each phrase is FOR.

Before this, planning produced a form skeleton and nothing else. Measured on a
freshly planned ternary piece: ``narrative.sections`` was empty,
``primary_climax_section`` was blank, ``curves.tension``/``register``/
``brightness`` were all empty lists, ``forward_context`` was None, and
``rhetorical_goals``/``development_techniques`` had no reader anywhere in the
codebase. A phrase knew its cadence and its bar count and nothing about why it
exists — so every section came out as competent local writing with no arc, which
is what "lacks structure" means.

This module gives every phrase four things the composer needs and could not
previously be told:

1. a DRAMATIC ROLE — establish, extend, depart, intensify, crisis, retreat,
   return, confirm, close — drawn from where it sits in the form;
2. its distance from the piece's CLIMAX, so the writing can build toward it and
   subside after it, instead of every phrase being locally optimal;
3. curves that actually arc — tension, register and brightness, not just a
   dynamics ramp;
4. for a return, an explicit STRATEGY for how it must differ from the statement
   (a return that is the exposition plus ornaments is the machine tell that no
   metric catches), and for every phrase, what comes NEXT so it can prepare it.

Nothing here generates notes. It states intent the brief can hand to the agent.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# ─── Dramatic roles ──────────────────────────────────────────────────────────

ESTABLISH = "establish"
EXTEND = "extend"
DEPART = "depart"
INTENSIFY = "intensify"
CRISIS = "crisis"
RETREAT = "retreat"
RETURN = "return"
CONFIRM = "confirm"
CLOSE = "close"

# What each role asks of the music, in the composer's terms.
ROLE_INTENT: Dict[str, str] = {
    ESTABLISH: "state the idea plainly and let it be heard; nothing here needs to prove anything",
    EXTEND: "carry the idea further than its first statement — spin it out, do not restate it",
    DEPART: "leave home; the listener should feel the ground shift",
    INTENSIFY: "raise the stakes — register, harmonic rate, dissonance, or all three",
    CRISIS: "the point of most tension in the piece; commit to it, do not hedge",
    RETREAT: "let the pressure out; the music has to breathe after the crisis",
    RETURN: "the idea comes back CHANGED by what happened in between",
    CONFIRM: "settle the key beyond doubt; drive the structural cadence",
    CLOSE: "stop persuading — take leave of the material",
}

# Section-role -> the arc of dramatic roles its phrases take, in order. The last
# entry repeats if the section has more phrases than the pattern.
_SECTION_ARC: Dict[str, List[str]] = {
    "a": [ESTABLISH, EXTEND, CONFIRM],
    "b": [DEPART, INTENSIFY],
    "retransition": [RETREAT],
    "a2": [RETURN, CONFIRM],
    "coda": [CLOSE],
    "pt": [ESTABLISH, EXTEND],
    "tr": [DEPART],
    "st": [ESTABLISH, EXTEND, CONFIRM],
    "cl": [CONFIRM],
    "development": [DEPART, INTENSIFY, CRISIS, RETREAT],
    "dev": [DEPART, INTENSIFY, CRISIS, RETREAT],
    "recap": [RETURN, CONFIRM],
    "rec_pt": [RETURN, EXTEND],
    "rec_tr": [DEPART],
    "rec_st": [RETURN, CONFIRM],
    "theme": [ESTABLISH, CONFIRM],
    "variation": [RETURN, CONFIRM],
}

# ─── Return strategies ───────────────────────────────────────────────────────
#
# A return that is the statement plus a trill is the single most recognisable
# machine tell in this repertoire, and no statistic catches it — the metrics all
# read "matches the exposition", which is exactly the problem. Each strategy
# names ONE concrete thing that must be different.

RETURN_STRATEGIES: List[Tuple[str, str]] = [
    (
        "reharmonized",
        "the same melody over a different bass; take it somewhere the first "
        "statement did not go before rejoining the cadence",
    ),
    (
        "registrally_displaced",
        "state it an octave away, or hand it to the left hand while the right "
        "accompanies — the listener should hear the same idea from a new place",
    ),
    (
        "texturally_intensified",
        "keep the line and thicken what surrounds it: an added inner voice, "
        "doubled thirds, a busier accompaniment than the statement had",
    ),
    (
        "abbreviated",
        "cut into it — arrive at the cadence sooner than the statement did, so "
        "the return feels urgent rather than dutiful",
    ),
    (
        "expanded",
        "the opposite: interrupt the expected cadence and extend, so the return "
        "costs more than the statement did",
    ),
    (
        "dissolved",
        "keep the pitches but break the rhythm down into smaller values, so the "
        "melody now MOVES where it used to hold — a variation of the line itself, "
        "not decoration added on top of it",
    ),
]


# Section ids are abbreviated in the form specs ("m1_retr", "m1_dev"), so the
# lookup has to know the abbreviations or a retransition silently gets the
# default arc and is told to "establish" when its job is to subside.
_STEM_ALIASES = {
    "retr": "retransition",
    "retrans": "retransition",
    "dev": "development",
    "devel": "development",
    "rec": "recap",
    "recap_pt": "rec_pt",
    "recap_st": "rec_st",
    "second": "st",
    "primary": "pt",
    "close": "cl",
    "closing": "cl",
    "intro": "a",
    "b2": "b",
    "a3": "a2",
}


def _section_stem(section_id: str) -> str:
    """'m1_rec_pt' -> 'rec_pt'; 'm1_var2' -> 'variation'; 'm1_retr' -> 'retransition'."""
    raw = section_id or ""
    stem = raw.split("_", 1)[-1] if "_" in raw else raw
    stem = (stem or "").lower()
    if stem.startswith("var"):
        return "variation"
    return _STEM_ALIASES.get(stem, stem)


def role_for(section_id: str, index: int) -> str:
    """The dramatic role of the ``index``-th phrase of a section.

    Exposed so the planner can resolve a role BEFORE building the slot, which is
    what lets harmony sampling depend on what the phrase is for.
    """
    arc = _SECTION_ARC.get(_section_stem(section_id)) or [ESTABLISH, EXTEND, CONFIRM]
    return arc[min(max(0, index), len(arc) - 1)]


def assign_dramatic_roles(slots) -> None:
    """Give every slot a dramatic role from its position in its section."""
    by_section: Dict[str, List] = {}
    for slot in slots:
        by_section.setdefault(slot.section_id, []).append(slot)
    for section_id, group in by_section.items():
        arc = _SECTION_ARC.get(_section_stem(section_id)) or [ESTABLISH, EXTEND, CONFIRM]
        for i, slot in enumerate(group):
            slot.dramatic_role = arc[min(i, len(arc) - 1)]


def locate_climax(slots) -> Optional[str]:
    """The phrase that carries the piece's peak.

    Preference order: an explicit CRISIS phrase (a development has one); else the
    last INTENSIFY; else the phrase just before the return, which is where a
    ternary form's pressure actually peaks. Returns a phrase_id.
    """
    crisis = [s for s in slots if getattr(s, "dramatic_role", "") == CRISIS]
    if crisis:
        return crisis[-1].phrase_id
    intensify = [s for s in slots if getattr(s, "dramatic_role", "") == INTENSIFY]
    if intensify:
        return intensify[-1].phrase_id
    returns = [i for i, s in enumerate(slots) if getattr(s, "dramatic_role", "") == RETURN]
    if returns and returns[0] > 0:
        return slots[returns[0] - 1].phrase_id
    return slots[len(slots) // 2].phrase_id if slots else None


def _arc_value(distance: int, span: int, peak: float, floor: float) -> float:
    """A value that rises to ``peak`` at distance 0 and falls to ``floor`` away."""
    if span <= 0:
        return peak
    closeness = max(0.0, 1.0 - abs(distance) / span)
    return round(floor + (peak - floor) * closeness, 3)


def apply_dramatic_curves(slots, climax_phrase_id: Optional[str]) -> None:
    """Fill tension, register and brightness so the piece has a shape.

    Only ``energy`` was ever populated, from a per-function default that rose
    monotonically to each phrase's own last bar — so every phrase peaked at its
    own cadence and the PIECE had no peak at all.
    """
    if not slots:
        return
    ids = [s.phrase_id for s in slots]
    peak_idx = ids.index(climax_phrase_id) if climax_phrase_id in ids else len(ids) // 2
    span = max(1, len(ids) - 1)

    for i, slot in enumerate(slots):
        d = i - peak_idx
        n = max(1, slot.bar_count)
        role = getattr(slot, "dramatic_role", EXTEND)

        # Tension peaks at the climax and relaxes either side; a CONFIRM/CLOSE
        # phrase relaxes further because its job is to settle.
        base = _arc_value(d, span, peak=0.95, floor=0.25)
        if role in (CONFIRM, CLOSE):
            base *= 0.7
        elif role == RETREAT:
            base *= 0.8
        slot.curves.tension = [
            round(min(1.0, base * (0.85 + 0.3 * (b / max(1, n - 1) if n > 1 else 1))), 3)
            for b in range(n)
        ]

        # Register: the climax is also the highest point. Within a phrase the
        # line arches rather than climbing straight to its cadence.
        reg_peak = _arc_value(d, span, peak=0.9, floor=0.35)
        slot.curves.register = [round(reg_peak * (0.8 + 0.25 * _hump(b, n)), 3) for b in range(n)]

        # Brightness: minor-key and DEPART/CRISIS material darkens.
        bright = 0.7 if role in (ESTABLISH, RETURN, CONFIRM, CLOSE) else 0.45
        if role in (DEPART, CRISIS):
            bright = 0.3
        slot.curves.brightness = [bright] * n

        # Energy: BUILD the curve rather than scaling whatever the per-function
        # default left. Those defaults return a constant for CONTINUATION, so
        # scaling a flat line by a per-phrase constant left it flat — the climax of
        # the piece came out as an unchanging mf. Energy is the piece-level arc
        # (loudest at the climax, quietest at the extremes) crossed with a
        # within-phrase swell, which is what a dynamic plan has to be to be usable.
        phrase_peak = _arc_value(d, span, peak=0.95, floor=0.30)
        phrase_floor = max(0.15, phrase_peak - 0.28)
        # Each role has its own SHAPE, not all the same arch: material that is
        # building should grow across the phrase, material that is subsiding
        # should recede, and only lyrical material arches. A single shape for
        # every phrase is how a dynamic plan ends up sounding applied rather than
        # composed.
        shape = _ROLE_SHAPE.get(role, _hump)
        slot.curves.energy = [
            round(phrase_floor + (phrase_peak - phrase_floor) * shape(b, n), 3) for b in range(n)
        ]
        if role in (CONFIRM, CLOSE):
            drop = 0.12 if role == CONFIRM else 0.28
            slot.curves.energy = [round(max(0.10, e - drop), 3) for e in slot.curves.energy]
        elif role == ESTABLISH:
            # an opening states the idea; it does not need to be loud
            slot.curves.energy = [round(max(0.10, e - 0.15), 3) for e in slot.curves.energy]


def _rise(i: int, n: int) -> float:
    """0 at the start, 1 at the end — material that is building."""
    return round(i / (n - 1), 3) if n > 1 else 1.0


def _fall(i: int, n: int) -> float:
    """1 at the start, 0 at the end — material that is subsiding."""
    return round(1.0 - i / (n - 1), 3) if n > 1 else 1.0


def _hump(i: int, n: int) -> float:
    """0 at the edges, 1 in the middle — a one-phrase arch."""
    if n <= 1:
        return 1.0
    x = i / (n - 1)
    return round(1.0 - abs(2 * x - 1), 3)


# Which way each role's energy travels across its own phrase.
_ROLE_SHAPE = {
    ESTABLISH: _hump,
    EXTEND: _hump,
    DEPART: _rise,
    INTENSIFY: _rise,
    CRISIS: _rise,
    RETREAT: _fall,
    RETURN: _hump,
    CONFIRM: _rise,
    CLOSE: _fall,
}


def assign_return_strategies(slots) -> None:
    """Give each returning phrase a concrete way to differ from the statement.

    Rotated deterministically so a piece with several returns (a recapitulation
    and a coda, or a set of variations) does not use the same device twice
    running.
    """
    n = 0
    for slot in slots:
        if getattr(slot, "dramatic_role", "") != RETURN:
            continue
        name, how = RETURN_STRATEGIES[n % len(RETURN_STRATEGIES)]
        slot.return_strategy = name
        slot.return_strategy_detail = how
        n += 1


def link_forward_context(slots) -> None:
    """Tell every phrase what it is leading INTO.

    ``forward_context`` existed on the model and was never populated, so no
    phrase could prepare the next one — which is why generated sections read as a
    sequence of separately-validated phrases rather than one fabric.
    """
    for cur, nxt in zip(slots, slots[1:]):
        role = getattr(nxt, "dramatic_role", "")
        cur.forward_context = (
            f"leads into {nxt.phrase_id} ({nxt.function}, {role}) in {nxt.key} — "
            f"{ROLE_INTENT.get(role, '')}"
        )
    if slots:
        slots[-1].forward_context = "final phrase — nothing follows; land it"


def key_journey(slots) -> None:
    """Mark each phrase as staying, leaving or arriving, and name the pivot.

    A slot carried one key and no notion of motion, so a modulation was simply a
    different key on the next phrase with nothing in between: the listener gets
    teleported rather than taken somewhere.
    """
    from .pitch import parse_key

    for prev, cur in zip([None] + list(slots[:-1]), slots):
        if prev is None or prev.key == cur.key:
            cur.key_motion = "prolong"
            cur.pivot_hint = ""
            continue
        try:
            a, b = parse_key(prev.key), parse_key(cur.key)
            # the pivot: a chord belonging to both keys, named in the OLD key
            shared = {p.name for p in a.pitches} & {p.name for p in b.pitches}
            cur.key_motion = "arrive"
            cur.pivot_hint = (
                f"from {prev.key} to {cur.key}; tones common to both: "
                f"{'/'.join(sorted(shared))} — pivot on one of these rather than "
                f"restating in the new key"
            )
        except Exception:
            cur.key_motion = "arrive"
            cur.pivot_hint = f"from {prev.key} to {cur.key}"
        if prev is not None:
            prev.key_motion = prev.key_motion or "prolong"
            if prev.key_motion == "prolong":
                prev.key_motion = "depart"


# What a section of each dramatic character is trying to ACHIEVE, and the
# techniques that achieve it. `SectionContract.rhetorical_goals` and
# `development_techniques` existed on the model with no writer and no reader.
SECTION_RHETORIC: Dict[str, Tuple[List[str], List[str]]] = {
    ESTABLISH: (
        ["make the idea memorable on first hearing", "establish the key beyond doubt"],
        ["clear periodic phrasing", "diatonic harmony", "one accompaniment character"],
    ),
    EXTEND: (
        ["carry the idea past its first statement", "avoid literal repetition"],
        ["sequence", "fragmentation of the head motif", "melodic extension", "added inner voice"],
    ),
    DEPART: (
        ["destabilise the home key", "make the listener want resolution"],
        ["pivot chord", "applied dominant", "modal mixture", "chromatic bass"],
    ),
    INTENSIFY: (
        ["raise tension continuously", "spend register and dissonance"],
        ["rising sequence", "shortened harmonic rhythm", "stretto", "registral ascent"],
    ),
    CRISIS: (
        ["reach the piece's maximum tension", "commit to the dissonance"],
        ["diminished-seventh prolongation", "dominant pedal", "textural saturation", "silence"],
    ),
    RETREAT: (
        ["release tension", "prepare the return without announcing it"],
        ["dominant prolongation", "thinning texture", "descending register", "liquidation"],
    ),
    RETURN: (
        ["bring the idea back CHANGED", "make the return feel earned"],
        ["reharmonisation", "registral displacement", "rhythmic dissolution", "added counterpoint"],
    ),
    CONFIRM: (
        ["settle the key past argument", "drive the structural cadence"],
        ["cadential 6-4", "expanded cadence", "pedal-point confirmation"],
    ),
    CLOSE: (
        ["take leave of the material", "stop persuading"],
        ["plagal colour", "tonic pedal", "thinning to a single line", "codetta repetition"],
    ),
}


def section_rhetoric(roles: List[str]) -> Tuple[List[str], List[str]]:
    """(goals, techniques) for a section, unioned over its phrases' roles."""
    goals: List[str] = []
    techs: List[str] = []
    for role in roles:
        g, t = SECTION_RHETORIC.get(role, ([], []))
        goals += [x for x in g if x not in goals]
        techs += [x for x in t if x not in techs]
    return goals, techs


# Energy (0-1) -> a dynamic marking. The curve existed per bar and was never
# turned into anything the composer could read, so the only dynamic guidance in
# the brief was the words "avoid flat dynamics".
_DYNAMIC_STEPS = [
    (0.22, "pp"),
    (0.36, "p"),
    (0.50, "mp"),
    (0.64, "mf"),
    (0.80, "f"),
    (1.01, "ff"),
]

# How each dramatic role wants to be touched.
ROLE_ARTICULATION: Dict[str, str] = {
    ESTABLISH: "legato, singing — slur the whole idea",
    EXTEND: "legato with the phrasing broken where the line turns a corner",
    DEPART: "slightly detached; the ground is less certain",
    INTENSIFY: "accented on the strong beats, shorter as the pressure rises",
    CRISIS: "marcato, weighted — every note wants to be heard",
    RETREAT: "legato and softening; let the ends of notes decay",
    RETURN: "legato, but touch it differently from the first statement",
    CONFIRM: "firm and articulate; the cadence should be unambiguous",
    CLOSE: "legato, unemphatic — no more argument",
}


def dynamic_for(energy: float) -> str:
    for ceiling, name in _DYNAMIC_STEPS:
        if energy < ceiling:
            return name
    return "ff"


def dynamic_shape(slot) -> str:
    """A bar-by-bar dynamic plan with hairpin direction, from the energy curve."""
    curve = list(getattr(getattr(slot, "curves", None), "energy", None) or [])
    if not curve:
        return ""
    parts = []
    for i, e in enumerate(curve):
        bar = slot.bar_start + i
        parts.append(f"b{bar} {dynamic_for(e)}")
        if i + 1 < len(curve):
            delta = curve[i + 1] - e
            parts.append("<" if delta > 0.04 else (">" if delta < -0.04 else "—"))
    return " ".join(parts)


def apply_articulation(slots) -> None:
    """Fill `curves.articulation`, which existed on the model and was never set."""
    for slot in slots:
        role = getattr(slot, "dramatic_role", "")
        # 1.0 = fully legato, 0.0 = fully detached
        base = {
            ESTABLISH: 0.9,
            EXTEND: 0.85,
            DEPART: 0.6,
            INTENSIFY: 0.45,
            CRISIS: 0.3,
            RETREAT: 0.85,
            RETURN: 0.9,
            CONFIRM: 0.65,
            CLOSE: 0.95,
        }.get(role, 0.8)
        slot.curves.articulation = [base] * max(1, slot.bar_count)


def build(slots) -> Dict[str, object]:
    """Run the whole dramatic plan over a form's slots. Mutates them in place."""
    slots = list(slots)
    assign_dramatic_roles(slots)
    climax = locate_climax(slots)
    apply_dramatic_curves(slots, climax)
    assign_return_strategies(slots)
    apply_articulation(slots)
    link_forward_context(slots)
    key_journey(slots)
    for slot in slots:
        slot.climax_distance = _phrase_distance(slots, slot.phrase_id, climax)
    return {
        "climax_phrase": climax,
        "roles": {s.phrase_id: getattr(s, "dramatic_role", "") for s in slots},
    }


def _phrase_distance(slots, phrase_id: str, climax_id: Optional[str]) -> int:
    ids = [s.phrase_id for s in slots]
    if climax_id not in ids or phrase_id not in ids:
        return 0
    return ids.index(phrase_id) - ids.index(climax_id)
