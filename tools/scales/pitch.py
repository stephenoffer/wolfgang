"""
Pitch, interval, key, chord, and scale utilities for SCALES.

Ported from tools/v3/pitch_utils.py with fixes:
- Key-aware enharmonic spelling
- Double sharp/flat support
- Chord quality intervals
- Voice leading cost
"""

import re
from typing import List, Optional, Union

# ─── Pitch Constants ─────────────────────────────────────────────────────────

NOTE_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

SEMITONE_TO_NOTE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

SEMITONE_TO_NOTE_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

_SHARP_KEYS = frozenset(
    {
        "C",
        "G",
        "D",
        "A",
        "E",
        "B",
        "F#",
        "C#",
        "Am",
        "Em",
        "Bm",
        "F#m",
        "C#m",
        "G#m",
        "D#m",
    }
)


def prefer_sharps(key: str) -> bool:
    """Return True if the key uses sharps in its key signature."""
    return _normalize_key(key) in _SHARP_KEYS


# ─── Scale Intervals ─────────────────────────────────────────────────────────

SCALE_INTERVALS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "whole_tone": [0, 2, 4, 6, 8, 10],
    "chromatic": list(range(12)),
}

# ─── Chord Quality Intervals ─────────────────────────────────────────────────

CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "hdim7": [0, 3, 6, 10],
    "aug7": [0, 4, 8, 10],
    "sus4": [0, 5, 7],
    "sus2": [0, 2, 7],
}


# ─── Pitch Conversion ────────────────────────────────────────────────────────


def pitch_to_midi(p: Union[str, int, float, list, None]) -> Optional[int]:
    """Convert pitch string to MIDI number.

    Handles: 'C4'->60, 'F#5'->78, 'Bb3'->58, 'C##4'->62, 'Dbb3'->49
    Lists (chords): returns highest note.
    """
    if p is None or p == "rest":
        return None
    if isinstance(p, list):
        midis = [pitch_to_midi(n) for n in p if n != "rest"]
        midis = [m for m in midis if m is not None]
        return max(midis) if midis else None
    if isinstance(p, (int, float)):
        return int(p)

    s = str(p).strip()
    if not s:
        return None

    # music21 spells a flat "-" ("B-5"), the shorthand spells it "b" ("Bb5"), and
    # both cross this boundary. Accepting only one of them meant every pitch that
    # came back from music21 read as None: silently dropped from role inference,
    # from every melodic statistic and from the voice-leading check.
    match = re.match(r"^([A-Ga-g])([#b\-]{0,2})(\d)$", s)
    if not match:
        return None

    note_name = match.group(1).upper()
    accidental = match.group(2)
    octave = int(match.group(3))

    midi = (octave + 1) * 12 + NOTE_TO_SEMITONE.get(note_name, 0)
    midi += accidental.count("#") - accidental.count("b") - accidental.count("-")
    return 0 if midi < 0 else (127 if midi > 127 else midi)


_LETTERS = "CDEFGAB"
_LETTER_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)
_MINOR_STEPS = (0, 2, 3, 5, 7, 8, 10)
# Scale degrees (0-based) that practice RAISES rather than lowers: the fourth and
# the seventh in major; the sixth and seventh in minor as well. A chromatic pitch
# a semitone above one of these is that degree sharpened; anything else is the
# degree above it flattened.
_RAISED_DEGREES_MAJOR = frozenset({3, 6})
# Minor raises its third (the Picardy), fourth, sixth and seventh.
_RAISED_DEGREES_MINOR = frozenset({2, 3, 5, 6})

_SPELLING_CACHE: dict = {}


def _accidental(name: str) -> int:
    return name.count("#") - name.count("b")


def _alter(name: str, delta: int) -> Optional[str]:
    acc = _accidental(name) + delta
    if abs(acc) > 2:
        return None
    letter = name[0]
    return letter + ("#" * acc if acc > 0 else "b" * -acc)


def key_spelling(key: str = "C") -> dict:
    """pitch class -> the note name that key actually writes.

    A key is not "all sharps" or "all flats". D minor has one flat AND spells its
    raised fourth G-sharp and its leading tone C-sharp; the old allowlist gave
    A-flat and D-flat — different notes on the page, and a semitone from what was
    meant. Diatonic degrees are spelled from the key's own letter sequence, and
    each chromatic degree is spelled as the alteration real practice makes:
    sharpening the fourth and seventh (and the sixth in minor), flattening the
    rest.
    """
    norm = _normalize_key(key)
    if norm in _SPELLING_CACHE:
        return _SPELLING_CACHE[norm]
    minor = norm.endswith("m")
    tonic = norm[:-1] if minor else norm
    if not tonic or tonic[0].upper() not in _LETTER_PC:
        tonic = "C"
    letter0 = tonic[0].upper()
    tonic_pc = key_to_root_midi(key) % 12
    steps = _MINOR_STEPS if minor else _MAJOR_STEPS

    out: dict = {}
    degree_of: dict = {}
    for i, off in enumerate(steps):
        letter = _LETTERS[(_LETTERS.index(letter0) + i) % 7]
        pc = (tonic_pc + off) % 12
        acc = (pc - _LETTER_PC[letter]) % 12
        acc = acc - 12 if acc > 6 else acc
        name = _alter(letter, acc)
        if name is None:  # a key needing triple accidentals — fall back
            _SPELLING_CACHE[norm] = _fallback_spelling(key)
            return _SPELLING_CACHE[norm]
        out[pc] = name
        degree_of[pc] = i

    raised = _RAISED_DEGREES_MINOR if minor else _RAISED_DEGREES_MAJOR
    for pc in range(12):
        if pc in out:
            continue
        below, above = out.get((pc - 1) % 12), out.get((pc + 1) % 12)
        sharp = _alter(below, +1) if below else None
        flat = _alter(above, -1) if above else None
        # Fewest accidentals wins first — otherwise G minor's Picardy third comes
        # out "Cb" and D-flat major's second comes out "E-double-flat". Only when
        # both candidates are equally simple does the raised/lowered convention
        # decide, and then D minor writes G-sharp for its raised fourth and
        # E-flat for its Neapolitan.
        candidates = [c for c in (sharp, flat) if c]
        if not candidates:
            out[pc] = SEMITONE_TO_NOTE_FLAT[pc]
            continue
        best = min(abs(_accidental(c)) for c in candidates)
        simple = [c for c in candidates if abs(_accidental(c)) == best]
        if len(simple) == 1:
            out[pc] = simple[0]
            continue
        prefer_sharp = below is not None and degree_of.get((pc - 1) % 12) in raised
        out[pc] = (sharp if prefer_sharp else flat) or simple[0]
    _SPELLING_CACHE[norm] = out
    return out


def _fallback_spelling(key: str) -> dict:
    names = SEMITONE_TO_NOTE_SHARP if prefer_sharps(key) else SEMITONE_TO_NOTE_FLAT
    return {pc: names[pc] for pc in range(12)}


def midi_to_pitch(midi_val: int, key: str = "C") -> str:
    """Convert MIDI number to pitch string, spelled the way ``key`` writes it."""
    midi_val = int(midi_val)
    octave = (midi_val // 12) - 1
    return f"{key_spelling(key)[midi_val % 12]}{octave}"


def pitch_class(midi_val: int) -> int:
    """Return pitch class (0-11) from MIDI value."""
    return midi_val % 12


def interval_semitones(p1: Union[str, int], p2: Union[str, int]) -> Optional[int]:
    """Signed interval in semitones between two pitches."""
    m1 = pitch_to_midi(p1) if isinstance(p1, str) else p1
    m2 = pitch_to_midi(p2) if isinstance(p2, str) else p2
    if m1 is None or m2 is None:
        return None
    return m2 - m1


# ─── Scale Utilities ─────────────────────────────────────────────────────────


def build_scale(root_midi: int, mode: str = "major", octaves: int = 6) -> List[int]:
    """Build a multi-octave scale from a MIDI root."""
    intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
    result = []
    for oct in range(-2, octaves):
        for iv in intervals:
            m = root_midi + oct * 12 + iv
            if 0 <= m <= 127:
                result.append(m)
    return sorted(set(result))


def nearest_scale_tone(midi_val: int, scale: List[int], direction: str = "below") -> Optional[int]:
    """Find nearest scale tone strictly above or below midi_val."""
    if direction == "below":
        candidates = [s for s in scale if s < midi_val]
        return max(candidates) if candidates else None
    else:
        candidates = [s for s in scale if s > midi_val]
        return min(candidates) if candidates else None


def snap_to_scale(midi_val: int, scale: List[int]) -> int:
    """Snap a MIDI pitch to the nearest tone in the given scale."""
    if not scale:
        return midi_val
    return min(scale, key=lambda s: abs(s - midi_val))


def clamp_to_range(midi_val: int, low: int, high: int) -> int:
    """Shift a MIDI pitch by octaves until it falls within [low, high]."""
    while midi_val < low and midi_val + 12 <= 127:
        midi_val += 12
    while midi_val > high and midi_val - 12 >= 0:
        midi_val -= 12
    return midi_val


_KEY_RE = re.compile(
    r"^\s*(?P<tonic>[A-Ga-g])"
    r"(?P<acc>(?:##|bb|--|#|b|-|\s*sharp|\s*flat|\s*is|\s*es)*)"
    r"[\s_-]*(?P<mode>minor|min|moll|m|major|maj|dur)?\s*$",
    re.IGNORECASE,
)


def _normalize_key(key: str) -> str:
    """Normalize any key spelling this project uses to short form ('Gm', 'Bb').

    Handles 'g_minor', 'bb_major', 'a minor', 'F#m', 'C', 'f_sharp_minor',
    'b_flat_major', 'Eb Major', and modulation arrows ('g_minor->bb_major',
    first key wins).

    The old word-splitting version got the spelled-out forms exactly wrong:
    'f_sharp_minor' split into tonic='f', mode='sharp', consumed the word and
    left mode empty — so it returned 'F#', a MAJOR key. 'b_flat_major' was worse:
    'flat' was never handled at all, so B-flat major came back as B major, a
    semitone off, and every chord frame, every transposition and every key
    signature derived from it was in the wrong key.
    """
    k = str(key or "").strip()
    if "->" in k:
        k = k.split("->")[0].strip()
    if not k:
        return "C"
    m = _KEY_RE.match(k.replace("_", " "))
    if not m:
        return k
    tonic = m.group("tonic").upper()
    acc = (m.group("acc") or "").lower().replace(" ", "").replace("_", "")
    if "flat" in acc or "sharp" in acc:
        # "e-flat minor": the hyphen is a separator, not a second flat sign.
        acc = acc.replace("-", "")
    # Spelled-out accidentals are consumed FIRST. Counting symbols first meant
    # the hyphen in "e-flat minor" counted as one flat and the word "flat" as
    # another, giving E-double-flat.
    sharps = acc.count("sharp") + acc.count("is")
    flats = acc.count("flat") + acc.count("es")
    acc = acc.replace("sharp", "").replace("flat", "").replace("is", "").replace("es", "")
    sharps += acc.count("#")
    flats += acc.count("b") + acc.count("-")
    tonic += "#" * max(0, sharps) + "b" * max(0, flats)
    mode = (m.group("mode") or "").lower()
    return tonic + "m" if mode in ("minor", "min", "moll", "m") else tonic


def key_to_root_midi(key: str) -> int:
    """Convert key name to root MIDI in octave 0.

    Handles: 'C'->0, 'D'->2, 'F#m'->6, 'g_minor'->7, 'bb_major'->10, 'eb_major'->3.
    """
    k = _normalize_key(key)
    k = k.rstrip("m")
    match = re.match(r"^([A-G])(#{0,2}|b{0,2})$", k)
    if not match:
        return 0
    note = match.group(1)
    acc = match.group(2)
    return NOTE_TO_SEMITONE.get(note, 0) + acc.count("#") - acc.count("b")


def parse_key(key: str):
    """The one key parser: any spelling this project uses -> a music21 Key.

    Accepts "F major", "a minor", "Am", "F", "g_minor", "bb_major", "F#m", and
    modulation arrows ("g_minor->bb_major", first key wins).

    There were FOUR independent key parsers, and three of them silently returned
    None or C major for the space-separated form the planner actually writes.
    `composition_brief._key_obj("F major")` returned None, so
    `RomanNumeral(roman, None)` fell back to C major — meaning the chord frame in
    every brief, the one concrete harmonic aid the agent is given, was computed in
    the WRONG KEY. Consolidating them here is the fix; delegating to it is the
    rule.
    """
    import music21

    norm = _normalize_key(key)
    mode = "minor" if norm.endswith("m") else "major"
    tonic = norm[:-1] if norm.endswith("m") else norm
    tonic = tonic.replace("b", "-") if len(tonic) > 1 and tonic[1:] == "b" else tonic
    for candidate in (tonic, tonic[:1].upper()):
        try:
            return music21.key.Key(candidate, mode)
        except Exception:
            continue
    return music21.key.Key("C", "major")


def is_minor_key(key: str) -> bool:
    """Check if a key string represents a minor key.

    Handles: 'Gm', 'g_minor', 'c_minor', 'F#m'.
    """
    k = _normalize_key(key)
    return k.endswith("m")


# ─── Chord Utilities ─────────────────────────────────────────────────────────


def chord_tones(root_midi: int, quality: str = "major") -> List[int]:
    """Return MIDI values for chord tones given root and quality."""
    intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])
    return [root_midi + iv for iv in intervals]


def voice_leading_cost(prev: List[int], curr: List[int]) -> int:
    """Total semitone motion between two voicings (same length assumed)."""
    if len(prev) != len(curr):
        return 999
    return sum(abs(a - b) for a, b in zip(prev, curr, strict=True))


def is_chord_tone(midi_val: int, root_midi: int, quality: str = "major") -> bool:
    """Check if a MIDI pitch is a chord tone."""
    ct = chord_tones(root_midi % 12, quality)
    return (midi_val % 12) in [t % 12 for t in ct]


def parallel_perfect(s1: int, b1: int, s2: int, b2: int) -> bool:
    """True if the outer-voice motion (soprano s1->s2 over bass b1->b2) forms a
    parallel perfect 5th or octave/unison. Single source of truth for both the
    validator (post-hoc check) and the harmonic solver (generation constraint)."""
    if s1 == s2 and b1 == b2:
        return False  # no motion -> not "parallel"
    i1, i2 = (s1 - b1) % 12, (s2 - b2) % 12
    return i1 == i2 and i1 in (0, 7) and s1 != s2 and b1 != b2
