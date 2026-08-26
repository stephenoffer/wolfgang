"""
Ornament realization — making written ornaments audible.

The music-critic judges this system's output by listening to the MIDI preview.
Ornaments were written into the score as *symbols* and never realized as notes,
so a trill did not trill, a mordent did not bite, a turn did not turn, and an
appoggiatura sounded exactly like an acciaccatura. Everything the ornament
vocabulary was extended to express arrived at the critic's ears as a plain
note — which means the ornaments, from the critic's point of view, did not
exist. In a Classical slow movement that is most of the expressive surface.

The realizations here follow period practice rather than the modern default:

* A Classical/Baroque **trill starts on the upper note**, on the beat, and takes
  its time from the principal note. Starting on the principal (the Romantic
  default) turns a dissonant, expressive figure into a decoration, and it is the
  single most common misreading of Classical ornamentation there is.
* An **appoggiatura takes real time** from its principal — half of it, or two
  thirds of a dotted note — and is *accented*, leaning and resolving. An
  **acciaccatura** is crushed before the beat and takes none.
* A **mordent** dips to the lower neighbour and returns; an **inverted mordent**
  (the Classical "prall") rises. Both are fast and both come off the beat's
  attack, not before it.
* A **turn** is four notes around the principal, and where it sits depends on
  whether it is written over the note or after it.

Neighbour notes are taken from the **key's scale**, not from a fixed semitone or
tone: a trill on the leading tone of a major key is a semitone at the top and a
trill on the mediant is a whole tone, and getting that wrong makes the ornament
sound wrong in a way a listener notices immediately even if they cannot say why.

Everything is deterministic and returns plain data, so the caller decides
whether to use it. Nothing here mutates the score: a realization is a
*performance*, and the notated ornament stays notated.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .pitch import build_scale, is_minor_key, key_to_root_midi

# ─── Output ──────────────────────────────────────────────────────────────────


@dataclass
class PlayedNote:
    """One sounding note of a realized ornament, relative to the principal."""

    offset_beats: Fraction  # from the principal's written onset (may be negative)
    duration_beats: Fraction
    midi: int
    velocity_scale: float = 1.0  # multiplier on the principal's velocity

    def as_tuple(self) -> Tuple[float, float, int, float]:
        return (
            float(self.offset_beats),
            float(self.duration_beats),
            self.midi,
            self.velocity_scale,
        )


# ─── Scale neighbours ────────────────────────────────────────────────────────


def _scale_pcs(key: str) -> List[int]:
    root = key_to_root_midi(key or "C")
    if root is None:
        root = 60
    minor = is_minor_key(key or "C")
    try:
        scale = build_scale(root % 12 + 60, "minor" if minor else "major", octaves=2)
        pcs = sorted({s % 12 for s in scale})
    except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
        pcs = []
    if not pcs:
        base = (root or 60) % 12
        steps = [0, 2, 3, 5, 7, 8, 10] if minor else [0, 2, 4, 5, 7, 9, 11]
        pcs = sorted({(base + s) % 12 for s in steps})
    if minor:
        # Harmonic minor: the raised leading tone is what a trill or a turn on
        # the dominant actually uses. A natural minor scale gives a trill on V a
        # flat seventh above it, which sounds modal rather than cadential.
        pcs = sorted(set(pcs) | {((root or 60) - 1) % 12})
    return pcs


def upper_neighbour(midi: int, key: str) -> int:
    """The next scale tone above — a semitone or a tone, as the key dictates."""
    pcs = _scale_pcs(key)
    for step in range(1, 13):
        if (midi + step) % 12 in pcs:
            return midi + step
    return midi + 2


def lower_neighbour(midi: int, key: str) -> int:
    """The next scale tone below.

    A *mordent's* lower note is diatonic; a trill's lower turn-note is too. The
    chromatic lower neighbour belongs to a written appoggiatura, not here.
    """
    pcs = _scale_pcs(key)
    for step in range(1, 13):
        if (midi - step) % 12 in pcs:
            return midi - step
    return midi - 2


# ─── Realizations ────────────────────────────────────────────────────────────

# Fastest note a trill is played in, as a fraction of a quarter note, scaled by
# tempo. A trill is not a fixed number of notes: at Adagio it has many, at
# Presto it is a four-note turn figure, and rendering a fixed count is why
# machine-realized trills sound like a tremolo effect rather than an ornament.
_MIN_TRILL_NOTE = Fraction(1, 8)  # a 32nd at quarter=60
_MAX_TRILL_NOTES = 32
# Fastest alternation a player can articulate: a 64th note. Anything faster is
# not an ornament, it is a smear.
_MIN_PLAYABLE_ALTERNATION = Fraction(1, 16)


def realize_trill(
    midi: int,
    duration_beats: Fraction,
    key: str,
    tempo_bpm: float = 90.0,
    start_upper: bool = True,
    termination: bool = True,
) -> List[PlayedNote]:
    """A trill: alternating principal and upper neighbour, on the beat.

    ``start_upper`` is the Baroque and Classical norm and the default. The
    closing turn (``termination``) is what makes a trill land rather than stop —
    a trill that simply runs out sounds like a mistake.
    """
    if duration_beats <= 0:
        return []
    upper = upper_neighbour(midi, key)
    # Speed scales with tempo: keep each alternation at least _MIN_TRILL_NOTE at
    # the notated tempo, so a fast movement gets fewer, wider notes.
    unit = _MIN_TRILL_NOTE * max(Fraction(1), Fraction(int(tempo_bpm), 60))
    unit = min(unit, duration_beats / 2)
    # A trill has to be playable. Below a 64th per alternation there is no
    # trill, only a note with a blur on it — and forcing one onto a short note
    # produces a two-note figure at an unplayable speed that a listener hears as
    # a glitch rather than an ornament.
    if unit <= 0 or unit < _MIN_PLAYABLE_ALTERNATION:
        return []
    n = min(_MAX_TRILL_NOTES, int(duration_beats / unit))
    if n < 3:
        return []

    notes: List[PlayedNote] = []
    tail = 3 if (termination and n >= 6) else 0
    body = n - tail
    for i in range(body):
        pitch = upper if (i % 2 == 0) == start_upper else midi
        # The first note of a trill carries the accent: it is the dissonance.
        vel = 1.06 if i == 0 else (0.9 if i % 2 else 0.95)
        notes.append(PlayedNote(unit * i, unit, pitch, vel))
    if tail:
        # Closing turn: lower neighbour, then the principal, held.
        base = unit * body
        lower = lower_neighbour(midi, key)
        notes.append(PlayedNote(base, unit, midi, 0.95))
        notes.append(PlayedNote(base + unit, unit, lower, 0.9))
        notes.append(
            PlayedNote(base + unit * 2, duration_beats - (base + unit * 2), midi, 1.0)
        )
    else:
        last = notes[-1]
        last.duration_beats = duration_beats - last.offset_beats
    return notes


def realize_mordent(
    midi: int, duration_beats: Fraction, key: str, inverted: bool = False
) -> List[PlayedNote]:
    """Principal, neighbour, principal — fast, on the beat.

    ``inverted=True`` is the upper mordent (the Classical "prall"), which was
    unspellable in the shorthand and therefore always came out as its opposite.
    """
    if duration_beats <= 0:
        return []
    nb = upper_neighbour(midi, key) if inverted else lower_neighbour(midi, key)
    unit = min(Fraction(1, 8), duration_beats / 3)
    if unit <= 0:
        return []
    return [
        PlayedNote(Fraction(0), unit, midi, 1.05),
        PlayedNote(unit, unit, nb, 0.92),
        PlayedNote(unit * 2, duration_beats - unit * 2, midi, 1.0),
    ]


def realize_turn(
    midi: int, duration_beats: Fraction, key: str, inverted: bool = False, after: bool = False
) -> List[PlayedNote]:
    """Upper, principal, lower, principal (reversed when inverted).

    ``after=True`` places the figure in the *second half* of the note — a turn
    written after the note, which holds the principal first and is a completely
    different gesture from one written over it.
    """
    if duration_beats <= 0:
        return []
    up = upper_neighbour(midi, key)
    dn = lower_neighbour(midi, key)
    seq = [up, midi, dn, midi] if not inverted else [dn, midi, up, midi]
    if after:
        hold = duration_beats / 2
        unit = (duration_beats - hold) / 4
        if unit <= 0:
            return []
        notes = [PlayedNote(Fraction(0), hold, midi, 1.0)]
        for i, p in enumerate(seq):
            notes.append(PlayedNote(hold + unit * i, unit, p, 0.9))
        return notes
    unit = min(Fraction(1, 8), duration_beats / 4)
    if unit <= 0:
        return []
    notes = [PlayedNote(unit * i, unit, p, 1.02 if i == 0 else 0.92) for i, p in enumerate(seq)]
    tail = duration_beats - unit * 4
    if tail > 0:
        notes.append(PlayedNote(unit * 4, tail, midi, 1.0))
    else:
        notes[-1].duration_beats = duration_beats - notes[-1].offset_beats
    return notes


def realize_appoggiatura(
    grace_midi: int, principal_midi: int, duration_beats: Fraction, dotted: bool = False
) -> List[PlayedNote]:
    """A leaning note that TAKES TIME from its principal and is accented.

    Half the principal's value, or two thirds of a dotted one. This is what
    separates an appoggiatura from an acciaccatura, and the two sounded
    identical because both were rendered as a crushed grace note: the leaning
    dissonance that carries most of the expression in a Classical slow movement
    was inaudible.
    """
    if duration_beats <= 0:
        return []
    share = Fraction(2, 3) if dotted else Fraction(1, 2)
    lean = duration_beats * share
    return [
        PlayedNote(Fraction(0), lean, grace_midi, 1.10),
        PlayedNote(lean, duration_beats - lean, principal_midi, 0.88),
    ]


def realize_acciaccatura(
    grace_midi: int, principal_midi: int, duration_beats: Fraction, tempo_bpm: float = 90.0
) -> List[PlayedNote]:
    """A crushed note BEFORE the beat, taking no time from the principal."""
    if duration_beats <= 0:
        return []
    crush = min(Fraction(1, 16), duration_beats / 4)
    return [
        PlayedNote(-crush, crush, grace_midi, 0.85),
        PlayedNote(Fraction(0), duration_beats, principal_midi, 1.0),
    ]


def realize_schleifer(
    midi: int, duration_beats: Fraction, key: str
) -> List[PlayedNote]:
    """A slide: two scale steps below, filled up into the principal."""
    if duration_beats <= 0:
        return []
    a = lower_neighbour(midi, key)
    b = lower_neighbour(a, key)
    unit = min(Fraction(1, 8), duration_beats / 3)
    if unit <= 0:
        return []
    return [
        PlayedNote(Fraction(0), unit, b, 0.85),
        PlayedNote(unit, unit, a, 0.9),
        PlayedNote(unit * 2, duration_beats - unit * 2, midi, 1.0),
    ]


# ─── Entry point ─────────────────────────────────────────────────────────────

_HANDLED = {
    "trill",
    "tr",
    "mordent",
    "mord",
    "inverted_mordent",
    "turn",
    "inverted_turn",
    "schleifer",
    "appoggiatura",
    "acciaccatura",
    "shake",
}


def realizes(ornament: Optional[str]) -> bool:
    """True when this ornament has an audible realization."""
    return bool(ornament) and str(ornament).lower() in _HANDLED


def realize(
    ornament: Optional[str],
    midi: int,
    duration_beats,
    key: str = "C",
    tempo_bpm: float = 90.0,
    *,
    grace_midi: Optional[int] = None,
    period: str = "classical",
) -> List[PlayedNote]:
    """Realize one ornament into sounding notes, or ``[]`` if there is nothing
    to realize (an unknown ornament, a fermata, a zero-length note).

    ``period`` decides the trill's starting note: Baroque and Classical start on
    the upper neighbour, Romantic and later on the principal. Rendering every
    trill the Romantic way is the commonest ornament error in editions and in
    software alike.
    """
    if not ornament:
        return []
    name = str(ornament).lower()
    dur = duration_beats if isinstance(duration_beats, Fraction) else Fraction(
        str(round(float(duration_beats), 6))
    ).limit_denominator(96)
    if dur <= 0:
        return []

    start_upper = period in ("baroque", "classical", "renaissance")
    if name in ("trill", "tr", "shake"):
        return realize_trill(midi, dur, key, tempo_bpm, start_upper=start_upper)
    if name in ("mordent", "mord"):
        return realize_mordent(midi, dur, key, inverted=False)
    if name == "inverted_mordent":
        return realize_mordent(midi, dur, key, inverted=True)
    if name == "turn":
        return realize_turn(midi, dur, key, inverted=False)
    if name == "inverted_turn":
        return realize_turn(midi, dur, key, inverted=True)
    if name == "schleifer":
        return realize_schleifer(midi, dur, key)
    if name == "appoggiatura" and grace_midi is not None:
        return realize_appoggiatura(grace_midi, midi, dur)
    if name == "acciaccatura" and grace_midi is not None:
        return realize_acciaccatura(grace_midi, midi, dur, tempo_bpm)
    return []


def realize_event(
    event,
    key: str = "C",
    tempo_bpm: float = 90.0,
    period: str = "classical",
    principal_midi: Optional[int] = None,
) -> List[PlayedNote]:
    """Convenience wrapper reading an EventIR/LayerEvent's own fields.

    Returns ``[]`` when the event carries no realizable ornament, so a caller
    can use the result's truthiness to decide whether to substitute.
    """
    from .duration import dur_to_beats
    from .pitch import pitch_to_midi

    orn = getattr(event, "ornament", None)
    if not realizes(orn):
        return []
    pitch = getattr(event, "pitch", None)
    if not pitch or pitch == "rest":
        return []
    names = pitch if isinstance(pitch, list) else [pitch]
    midi = pitch_to_midi(names[-1] if isinstance(pitch, list) else pitch)
    if midi is None:
        return []
    try:
        dur = dur_to_beats(getattr(event, "duration", "q"))
    except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
        return []
    return realize(
        orn,
        midi,
        dur,
        key=key,
        tempo_bpm=tempo_bpm,
        grace_midi=principal_midi,
        period=period,
    )


def ornament_summary(events: Sequence, key: str = "C") -> Dict[str, Any]:
    """How ornamented is this music, and is any of it audible?

    ``ornaments_per_bar`` against ``audible_per_bar`` is the measurement that
    exposed the problem: they were 0.29 and 0.00 on the piece under test.
    """
    bars, total, audible = set(), 0, 0
    kinds: Dict[str, int] = {}
    for e in events:
        bars.add(int(getattr(e, "bar", 1)))
        orn = getattr(e, "ornament", None)
        if not orn:
            continue
        total += 1
        kinds[str(orn)] = kinds.get(str(orn), 0) + 1
        if realizes(orn):
            audible += 1
    n = max(1, len(bars))
    return {
        "bars": n,
        "ornaments": total,
        "audible": audible,
        "ornaments_per_bar": round(total / n, 3),
        "audible_per_bar": round(audible / n, 3),
        "by_kind": kinds,
    }
