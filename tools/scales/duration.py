"""
Duration and meter utilities for SCALES.

Ported from tools/v3/pitch_utils.py duration section.
"""

from fractions import Fraction
from typing import Union

# ─── Duration Constants ──────────────────────────────────────────────────────
#
# Values are exact ``Fraction``s, never floats: music21 reproduces a tuplet or a
# 64th perfectly from an exact quarterLength (1/3 -> eighth in a 3:2 tuplet) but
# a float 0.333… drifts, and float snapping is what used to destroy every
# triplet and every 32nd on the way to MusicXML. Fraction arithmetic keeps beat
# cursors exact too, so a bar of triplets sums to the meter on the nose.

DURATION_VALUES = {
    # Longer than a whole note. A breve (double whole) is an ordinary value in
    # Renaissance polyphony and in any slow movement with a note held across
    # bars, and the table stopped at the dotted whole — so every one of the
    # **11,894 breves in the corpus** was read as a dotted whole, losing two
    # beats each, and no composer using this system could write a note longer
    # than six quarters at all. The barline splitter turns one into tied
    # fragments on the way to the page, which is how it is engraved anyway.
    "br": Fraction(8),  # breve / double whole
    "dbr": Fraction(12),  # dotted breve
    "lo": Fraction(16),  # longa
    # Standard
    "w": Fraction(4),  # whole
    "h": Fraction(2),  # half
    "q": Fraction(1),  # quarter
    "e": Fraction(1, 2),  # eighth
    "s": Fraction(1, 4),  # sixteenth
    "16": Fraction(1, 4),  # sixteenth alias
    "t": Fraction(1, 8),  # thirty-second
    "32": Fraction(1, 8),  # thirty-second alias
    "x": Fraction(1, 16),  # sixty-fourth
    "64": Fraction(1, 16),  # sixty-fourth alias
    # Dotted
    "dw": Fraction(6),
    "dh": Fraction(3),
    "dq": Fraction(3, 2),
    "de": Fraction(3, 4),
    "ds": Fraction(3, 8),
    "dt": Fraction(3, 16),
    # Double-dotted
    "ddh": Fraction(7, 2),
    "ddq": Fraction(7, 4),
    "dde": Fraction(7, 8),
    # Triplets (three in the space of two)
    "trip_w": Fraction(8, 3),
    "trip_h": Fraction(4, 3),
    "trip_q": Fraction(2, 3),
    "trip_e": Fraction(1, 3),
    "trip_s": Fraction(1, 6),
    "trip_t": Fraction(1, 12),
    # Quintuplets / sextuplets / septuplets (per quarter-note beat)
    "quint_e": Fraction(2, 5),
    "quint_s": Fraction(1, 5),
    "sext_s": Fraction(1, 6),
    "sept_s": Fraction(1, 7),
}

# Codes that notate as a tuplet. Kept explicit so the shorthand parser can
# recognize a tuplet suffix and the assembler can label the bracket.
TUPLET_PREFIXES = ("trip_", "quint_", "sext_", "sept_")

# Base (non-tuplet) code -> tuplet code, so "e_trip" / "etrip" style suffixes can
# be normalized onto a real code.
TRIPLET_OF = {
    "w": "trip_w",
    "h": "trip_h",
    "q": "trip_q",
    "e": "trip_e",
    "s": "trip_s",
    "t": "trip_t",
}


# ─── Grace ornaments ────────────────────────────────────────────────────────
#
# Ornaments whose note is played BEFORE (or crushed into) its principal and
# therefore consumes no metric time. This set is the single source of truth:
# the shorthand parser, the meter validator, the commit gate and the assembler
# all need the same answer, and each of them used to carry its own idea of it.
# Three separate places tested `ornament != "grace"` and so counted an
# appoggiatura or an acciaccatura against the bar's capacity — a bar with one
# in it was reported as overfull and rejected, which made the whole
# slashed/unslashed grace distinction unusable the moment it was added.
GRACE_ORNAMENTS = frozenset({"grace", "appoggiatura", "acciaccatura"})


def is_grace(ornament) -> bool:
    """True when an ornament name denotes a note that takes no metric time."""
    return (ornament or "") in GRACE_ORNAMENTS


# Trailing-dot spelling ("h." for a dotted half, "q.." for double-dotted) — the
# form used by the examples in the brief and the craft doc. Without this the
# parser read "Ab5h." as a plain half note and every bar written from the
# documented example came out a beat short, silently.
DOTTED_OF = {
    "w": "dw",
    "h": "dh",
    "q": "dq",
    "e": "de",
    "s": "ds",
    "t": "dt",
}
DOUBLE_DOTTED_OF = {"h": "ddh", "q": "ddq", "e": "dde"}

# A code that is ALREADY dotted, plus another dot. "dh." and "dq." are natural
# things to write and both used to normalize to nothing, fall through to the
# parser's fallback, and silently become a QUARTER — turning a 3.5-beat note
# into a 1-beat one with no error anywhere.
_REDOT = {"dh": "ddh", "dq": "ddq", "de": "dde"}


def normalize_dot_suffix(code: str) -> str:
    """Fold a trailing-dot duration spelling onto its canonical code.

    Handles the plain forms ("h." → "dh", "h.." → "ddh"), the already-dotted
    forms ("dh." → "ddh"), and dotted tuplets ("trip_e." → 1.5 × a triplet
    eighth), which are real rhythms with no canonical code — they resolve to the
    nearest expressible value rather than silently collapsing to a quarter.
    """
    stripped = code.rstrip(".")
    dots = len(code) - len(stripped)
    if dots == 0:
        return code
    if dots == 1:
        if stripped in DOTTED_OF:
            return DOTTED_OF[stripped]
        if stripped in _REDOT:
            return _REDOT[stripped]
    elif dots == 2 and stripped in DOUBLE_DOTTED_OF:
        return DOUBLE_DOTTED_OF[stripped]
    # A dotted tuplet ("trip_e.", "quint_s."): no code exists for it, so express
    # the value and let beats_to_dur pick the closest notatable one.
    if stripped in DURATION_VALUES:
        factor = Fraction(2) - Fraction(1, 2**dots)
        return beats_to_dur(DURATION_VALUES[stripped] * factor)
    return code


def is_tuplet_code(code: str) -> bool:
    """True when a duration code notates as a tuplet (bracketed) figure."""
    return str(code).startswith(TUPLET_PREFIXES)


def dur_codes_longest_first() -> list:
    """Duration codes ordered so a longest-match suffix scan is unambiguous.

    ``C5trip_e`` must match ``trip_e``, not ``e``; ``C5ds`` must match ``ds``,
    not ``s``. Sorting by descending length gives both.
    """
    return sorted(DURATION_VALUES, key=len, reverse=True)


def dur_to_beats(d: Union[str, int, float]) -> Fraction:
    """Convert a duration code to quarter-note beats as an exact ``Fraction``.

    Accepts codes ('q', 'dq', 'trip_e') or numeric values. Returns 0 for
    unrecognized strings. The result is exact so bar sums are exact: three
    ``trip_e`` sum to exactly 1, where floats sum to 0.9999999999999999 and made
    every triplet bar look like a meter violation.
    """
    if isinstance(d, Fraction):
        return d
    if isinstance(d, (int, float)):
        return Fraction(d).limit_denominator(64)
    d_str = str(d).strip()
    if d_str in DURATION_VALUES:
        return DURATION_VALUES[d_str]
    try:
        return Fraction(d_str).limit_denominator(64)
    except (ValueError, TypeError, ZeroDivisionError):
        return Fraction(0)


def beats_to_dur(beats: float) -> str:
    """Convert a beat value to the nearest duration code.

    Plain (non-tuplet) codes win ties, so an ordinary 16th never round-trips
    into a tuplet code just because both are equidistant.
    """
    target = Fraction(beats).limit_denominator(64) if not isinstance(beats, Fraction) else beats
    best, best_key = "q", (abs(target - Fraction(1)), 0)
    for code, val in DURATION_VALUES.items():
        key = (abs(val - target), 1 if is_tuplet_code(code) else 0)
        if key < best_key:
            best_key, best = key, code
    return best


def largest_dur_at_most(beats) -> str:
    """The longest notatable value that does NOT exceed ``beats``.

    ``beats_to_dur`` returns the NEAREST code, which can be longer than what was
    asked for: the nearest value to 1.4375 beats is a dotted quarter at 1.5. So
    clamping a note to the room left in its bar and then converting produced a
    note that ran past the barline again — the clamp was a no-op precisely when
    it mattered. Anything that has to fit inside a span must ask for this
    instead.

    Falls back to the shortest notatable value when nothing fits, so callers get
    a value they can engrave rather than an empty string.
    """
    target = beats if isinstance(beats, Fraction) else Fraction(beats).limit_denominator(96)
    fitting = [(v, c) for c, v in DURATION_VALUES.items() if v <= target]
    if not fitting:
        return min(DURATION_VALUES, key=lambda c: DURATION_VALUES[c])
    best = max(v for v, _ in fitting)
    # Prefer the plain spelling of a value over its tuplet alias.
    return min(
        (c for v, c in fitting if v == best),
        key=lambda c: (is_tuplet_code(c), len(c)),
    )


# What a bar holds when the time signature is unusable. A malformed meter is
# DATA — it arrives from a corpus record, a hand-written slot, a partially
# written phrase — and it must not take down the analysis layer.
_DEFAULT_METER = (4, 4)


def bar_duration(time_sig) -> Fraction:
    """Total beats in a bar given a time signature (num, denom), exact.

    (4, 4) -> 4, (3, 4) -> 3, (6, 8) -> 3, (4, 2) -> 8

    Malformed input falls back to 4/4 rather than raising. Twenty-one places in
    this codebase computed this inline as ``Fraction(int(meter[0]) * 4,
    int(meter[1]))``, and a denominator of zero — which a partially-initialised
    slot has — made ``Fraction(0, 0)`` and took out **twelve separate analysis
    entry points** with a ZeroDivisionError: every counterpoint, voicing,
    cadence, expression, craft and performance call on that phrase.

    One guarded implementation, since duplicated inline arithmetic is this
    repository's most reliable bug source.
    """
    try:
        num, denom = int(time_sig[0]), int(time_sig[1])
    except (TypeError, ValueError, IndexError, KeyError):
        num, denom = _DEFAULT_METER
    if num <= 0 or denom <= 0:
        num, denom = _DEFAULT_METER
    return Fraction(num * 4, denom)


def beats_per_bar(time_sig) -> float:
    """``bar_duration`` as a float, for callers that want one."""
    return float(bar_duration(time_sig))


def is_strong_beat(beat: float, time_sig: tuple) -> bool:
    """Check if a beat position is a strong beat in the given meter."""
    num, denom = time_sig
    if denom == 4:
        if num == 4:
            return beat in (1.0, 3.0)
        if num == 3:
            return beat == 1.0
        if num == 2:
            return beat == 1.0
    if denom == 8:
        if num == 6:
            return beat in (1.0, 2.5)  # compound duple
        if num == 9:
            return beat in (1.0, 2.0, 3.0)
    return beat == 1.0


def is_downbeat(beat: float) -> bool:
    """Check if this is beat 1."""
    return abs(beat - 1.0) < 0.001


def beats_per_measure(time_sig: tuple) -> float:
    """Beats per measure in quarter-note units."""
    return bar_duration(time_sig)


def subdivisions_per_beat(time_sig: tuple) -> int:
    """Common subdivision count per beat."""
    _, denom = time_sig
    if denom == 8:
        return 3  # compound
    return 2  # simple
