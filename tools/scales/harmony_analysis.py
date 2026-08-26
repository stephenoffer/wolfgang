"""Duration-weighted harmonic analysis — the one place a sonority becomes a
Roman numeral.

Why this exists
---------------
The corpus used to read harmony by collecting *every pitch class sounding
anywhere* in a beat and handing the set to ``music21.roman.romanNumeralFromChord``.
Every scale run, every passing tone and every appoggiatura therefore counted as a
chord tone, so the opening bar of K.279/i — three beats of unmixed C major —
came out ``I7``, and bar 2 came out ``ii6 / iii43 / I65 / V42``. Measured over
the shipped corpus that produced 43,627 of 102,439 bars labelled "chromatic",
with ``I6``, ``ii7``, ``V7`` and ``I64`` at the top of the list.

Everything downstream read that: the progression model the chord frame is
sampled from, the phrase segmentation (which keys off tonic/dominant arrivals),
cadence retrieval, and the harmonic-colour doctrine in every brief.

What it does instead
--------------------
1. Weight each pitch class by how long it actually *sounds* inside the span.
2. Score every root x quality template against those weights, charging for
   foreign weight and for chord tones the passage never states, so a four-note
   template has to earn its seventh.
3. Spell the winner directly — degree, quality and inversion — rather than
   round-tripping through figured bass, which is where ``iii43`` and ``#iø``
   came from.
4. Classify function from the *structure* (degree + quality + applied-ness), not
   by string-matching a figure, which is what made every inverted and every
   seventh chord "chromatic".
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

# (name, semitone template, weight of the "characteristic" tones)
CHORD_TEMPLATES: Tuple[Tuple[str, Tuple[int, ...]], ...] = (
    ("major", (0, 4, 7)),
    ("minor", (0, 3, 7)),
    ("dim", (0, 3, 6)),
    ("aug", (0, 4, 8)),
    ("dom7", (0, 4, 7, 10)),
    ("min7", (0, 3, 7, 10)),
    ("maj7", (0, 4, 7, 11)),
    ("halfdim7", (0, 3, 6, 10)),
    ("dim7", (0, 3, 6, 9)),
)

# How much more a pitch counts when it begins on the beat being analysed.
_ONSET_EMPHASIS = 2.0

_TRIAD_FIGURE = {0: "", 1: "6", 2: "64"}
_SEVENTH_FIGURE = {0: "7", 1: "65", 2: "43", 3: "42"}

_QUALITY_MARK = {"dim": "o", "halfdim7": "ø", "dim7": "o", "aug": "+"}

# How likely each sonority is to be a real harmony rather than a triad plus a
# passing note, in units of the span's total weight. Common-practice music is
# built from triads and dominant sevenths; a major seventh chord is almost never
# a functional harmony in this corpus, and reading one is nearly always a
# neighbour tone misfiled — which is how a plain I6 with a passing leading tone
# came out as "I7".
_QUALITY_PRIOR = {
    "major": 0.08,
    "minor": 0.05,
    "dom7": 0.03,
    "dim": 0.0,
    "min7": -0.05,
    "halfdim7": -0.02,
    "dim7": -0.02,
    "maj7": -0.16,
    "aug": -0.18,
}
_MINOR_QUALITIES = {"minor", "dim", "min7", "halfdim7", "dim7"}

# Degree spelling per mode: semitones above tonic -> uppercase numeral.
_DEGREE_MAJOR = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}
_DEGREE_MINOR = {
    0: "I",
    1: "bII",
    2: "II",
    3: "III",
    4: "#III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "VI",
    9: "#VI",
    10: "VII",
    11: "#VII",
}

# The triad quality each scale degree carries in the key. An incomplete sonority
# (no third sounding — a melody over a bass, which is most of keyboard texture)
# leaves the quality undetermined, and without this the fit is a coin flip: a bar
# of plain F major with no A sounding read as F MINOR, and "i" and "v" turned up
# in the chord frame of major-key phrases.
_DIATONIC_QUALITY_MAJOR = {
    0: "major",
    2: "minor",
    4: "minor",
    5: "major",
    7: "major",
    9: "minor",
    11: "dim",
}
_DIATONIC_QUALITY_MINOR = {
    0: "minor",
    2: "dim",
    3: "major",
    5: "minor",
    7: "major",
    8: "major",
    10: "major",
    11: "dim",
}

_MAJOR_SCALE = (0, 2, 4, 5, 7, 9, 11)
# Natural + harmonic + melodic minor together: the leading tone and the raised
# sixth are diatonic to minor-key practice, and treating them as chromatic is
# what made every minor-key dominant a "chromatic" chord.
_MINOR_SCALE = (0, 2, 3, 5, 7, 8, 9, 10, 11)


def _assert_real_midi(spans: Sequence[Tuple[float, float, Sequence[int]]]) -> None:
    """Catch pitch classes passed where MIDI numbers are required.

    Every pitch under 12 across a whole bar means the caller collapsed pitches
    to classes. That reading is not *wrong-looking* — it produces plausible
    chords with the wrong inversions — so it has to be caught at the boundary.
    A genuine C0-B0 sonority (MIDI 12-23) is below the piano's bottom note, so
    there is no real music this rejects.
    """
    seen = [int(m) for _st, _end, midis in spans for m in (midis or [])]
    if len(seen) >= 3 and max(seen) < 12:
        raise ValueError(
            "pc_weights expects real MIDI numbers, not pitch classes: every "
            f"pitch given is under 12 (max {max(seen)}). Passing pitch classes "
            "makes the lowest CLASS the bass, so inversions come out wrong "
            "while still looking like valid chords."
        )


def pc_weights(
    spans: Sequence[Tuple[float, float, Sequence[int]]], lo: float, hi: float
) -> Tuple[List[float], Optional[int]]:
    """Duration-weighted pitch-class profile over ``[lo, hi)``, plus the bass pc.

    ``spans`` is ``(start, end, [midi, ...])`` — **real MIDI numbers, not pitch
    classes**. The bass is the lowest pitch of the sonority sounding at ``lo``,
    which is what decides the inversion, and it is found by comparing absolute
    pitch. Hand this function pitch classes and the lowest *class* wins instead:
    a root-position F major triad containing a C reports C as the bass and the
    chord reads as I64. That failure is silent, so it is checked for here rather
    than described in prose.
    """
    w = [0.0] * 12
    bass_pc: Optional[int] = None
    bass_midi: Optional[int] = None
    _assert_real_midi(spans)
    for st, end, midis in spans:
        overlap = min(end, hi) - max(st, lo)
        if overlap <= 1e-9 or not midis:
            continue
        # Metric weight: what sounds ON the beat is far more likely to be a chord
        # tone than what passes between beats. Weighting purely by duration made
        # a bar of four equal sixteenths — one chord tone and three passing notes
        # — look like a four-note chord.
        emphasis = _ONSET_EMPHASIS if st <= lo + 1e-9 else 1.0
        for m in midis:
            w[int(m) % 12] += float(overlap) * emphasis
        if st <= lo + 1e-9:
            low = min(int(m) for m in midis)
            if bass_midi is None or low < bass_midi:
                bass_midi, bass_pc = low, low % 12
    if bass_pc is None:
        # Nothing starts exactly at lo — take the lowest note sounding anywhere
        # in the span rather than declaring the chord bass-less.
        lows = [
            min(int(m) for m in midis)
            for st, end, midis in spans
            if midis and min(end, hi) - max(st, lo) > 1e-9
        ]
        if lows:
            bass_pc = min(lows) % 12
    return w, bass_pc


def fit_chord(
    weights: Sequence[float], bass_pc: Optional[int], tonic_pc: int, mode: str
) -> Optional[Tuple[int, str, int]]:
    """Best (root_pc, quality, inversion) for a duration-weighted profile.

    Returns None when the span carries too little pitch information to be worth
    an analysis — better an honest gap than an invented chord.
    """
    total = sum(weights)
    if total <= 0:
        return None
    scale = _MAJOR_SCALE if mode != "minor" else _MINOR_SCALE
    sounding = {pc for pc, w in enumerate(weights) if w > total * 0.02}
    if not sounding:
        return None
    solo = len(sounding) == 1

    best = None
    best_score = float("-inf")
    for root in range(12):
        for quality, template in CHORD_TEMPLATES:
            tones = [(root + iv) % 12 for iv in template]
            present = [t for t in tones if t in sounding]
            # A chord has to be stated, not inferred — but the bar for "stated"
            # scales with the template. Demanding three sounding tones of every
            # template disqualified every incomplete triad (a melody over a bass,
            # with no fifth — the commonest sonority in keyboard music) while
            # four-note templates sailed through on three of four, so sevenths
            # beat triads by construction. A lone pitch class reads as the root
            # of its own diatonic triad (see `candidates`).
            if solo:
                if tones[0] not in sounding or len(template) > 3:
                    continue
            else:
                need = 3 if len(tones) > 3 else 2
                if len(present) < need or (tones[0] not in sounding and tones[1] not in sounding):
                    continue
            covered = sum(weights[t] for t in tones)
            foreign = total - covered
            # Foreign weight is charged more than covered weight is credited, so
            # a template only wins by explaining the passage rather than by
            # covering more pitch classes.
            score = covered - 1.6 * foreign
            # Parsimony: each extra chord tone must pay for itself. Without this
            # a plain triad plus one passing note always "fits" a seventh chord.
            score -= 0.18 * total * (len(template) - 3)
            # Missing tones the passage never states weaken the reading.
            score -= 0.08 * total * (len(tones) - len(present))
            if ((root - tonic_pc) % 12) in scale:
                score += 0.10 * total
            if all(((t - tonic_pc) % 12) in scale for t in tones):
                score += 0.12 * total
            if bass_pc is not None and bass_pc in tones:
                score += 0.10 * total
                # The bass is the strongest single piece of harmonic evidence in
                # tonal music, and root position is the unmarked reading. Without
                # this, four notes of a C major scale over a C bass fit D-F-A-C
                # better than C-E-G and the bar came out ii42.
                if bass_pc == tones[0]:
                    score += 0.25 * total
            if weights[tones[0]] > 0:
                score += 0.05 * total
            score += _QUALITY_PRIOR.get(quality, 0.0) * total
            score += _diatonic_bonus(root, quality, tones, sounding, tonic_pc, mode) * total
            if score > best_score:
                inv = 0
                if bass_pc is not None and bass_pc in tones:
                    inv = tones.index(bass_pc)
                best_score, best = score, (root, quality, inv)
    if best is None or best_score <= 0:
        return None
    return best


def _diatonic_bonus(root, quality, tones, sounding, tonic_pc, mode) -> float:
    """Credit for reading a chord as the quality its scale degree actually has.

    Weighted by how much the passage LEAVES undetermined: when the third is
    sounding, the ear decides and this barely matters; when it is not, the key is
    the only evidence there is.
    """
    degree = (root - tonic_pc) % 12
    table = _DIATONIC_QUALITY_MINOR if mode == "minor" else _DIATONIC_QUALITY_MAJOR
    want = table.get(degree)
    if want is None:
        return 0.0
    third_heard = tones[1] in sounding
    got = quality
    if quality == "dom7":
        got = "major"
    elif quality == "min7":
        got = "minor"
    elif quality == "maj7":
        got = "major"
    elif quality in ("dim7", "halfdim7"):
        got = "dim"
    if got != want:
        return 0.0 if third_heard else -0.30
    return 0.06 if third_heard else 0.30


def spell_roman(root_pc: int, quality: str, inversion: int, tonic_pc: int, mode: str) -> str:
    """(root, quality, inversion) -> a readable Roman numeral.

    Spelled directly from the structure. Round-tripping through music21's
    figured bass is what produced ``iii43``, ``#iø`` and ``iiio64`` — symbols
    that are not wrong so much as unreadable, and that no downstream vocabulary
    could match.
    """
    degree = (root_pc - tonic_pc) % 12
    base = (_DEGREE_MINOR if mode == "minor" else _DEGREE_MAJOR)[degree]
    acc = base[: -len(base.lstrip("b#"))] if base[0] in "b#" else ""
    numeral = base[len(acc) :]
    if quality in _MINOR_QUALITIES:
        numeral = numeral.lower()
    mark = _QUALITY_MARK.get(quality, "")
    seventh = len(dict(CHORD_TEMPLATES)[quality]) == 4
    figure = (_SEVENTH_FIGURE if seventh else _TRIAD_FIGURE).get(inversion, "")
    if quality == "maj7":
        # "I7" cannot mean both C-E-G-Bb and C-E-G-B. Spelling the major seventh
        # explicitly is what makes the symbol round-trip back to the same chord.
        mark = "maj"
    return f"{acc}{numeral}{mark}{figure}"


_TONIC_DEGREES = {0, 4, 9}  # I, iii, vi  (and III, VI in minor)
_PREDOMINANT_DEGREES = {2, 5}  # ii, IV
_DOMINANT_DEGREES = {7, 11}  # V, vii


def classify_function(root_pc: int, quality: str, tonic_pc: int, mode: str) -> str:
    """Harmonic function from structure — tonic / predominant / dominant / chromatic.

    Reads the chord, not its printed figure. The old classifier string-matched
    ``romanNumeralAlone`` against a list of seven bare symbols, so ``I6``,
    ``V7``, ``ii65`` and every chord in a minor key with a flat numeral fell
    through to "chromatic" — 42.6% of the whole corpus, headed by the four most
    ordinary chords in tonal music.
    """
    degree = (root_pc - tonic_pc) % 12
    if mode == "minor":
        if degree in (0, 3, 8):  # i, III, VI
            return "tonic"
        if degree in (2, 5):  # ii(o), iv
            return "predominant"
        if degree in (7, 11, 10):  # V/v, vii(o), VII
            return "dominant"
    else:
        if degree in _TONIC_DEGREES:
            return "tonic"
        if degree in _PREDOMINANT_DEGREES:
            return "predominant"
        if degree in _DOMINANT_DEGREES:
            return "dominant"
        if degree == 10:  # bVII — mixture, leads like a subdominant
            return "predominant"
        if degree == 8:  # bVI — mixture
            return "predominant"
    if degree == 1:  # Neapolitan
        return "predominant"
    # A dominant seventh anywhere else is an applied dominant: it functions as a
    # dominant, of whatever it points at.
    if quality == "dom7":
        return "dominant"
    return "chromatic"


def applied_target(root_pc: int, quality: str, tonic_pc: int, mode: str) -> Optional[str]:
    """If this is an applied dominant, the numeral it points at (``"V/V"`` -> ``"V"``)."""
    if quality not in ("dom7", "dim7", "halfdim7"):
        return None
    degree = (root_pc - tonic_pc) % 12
    if degree == 7 and quality == "dom7":
        return None  # the key's own dominant
    target = (degree + 5) % 12 if quality == "dom7" else (degree + 1) % 12
    scale = _MAJOR_SCALE if mode != "minor" else _MINOR_SCALE
    if target not in scale:
        return None
    # A leading-tone chord resolving to the tonic IS the key's own vii, not an
    # applied one — "viioø43/I" is not a symbol anybody writes.
    if target == 0:
        return None
    # Applied dominants are chromatic by definition. A diatonic seventh is
    # better spelled literally (vi7, IV7) than as a borrowed dominant.
    tones = [(root_pc + iv) % 12 for iv in dict(CHORD_TEMPLATES)[quality]]
    if all(((t - tonic_pc) % 12) in scale for t in tones):
        return None
    base = (_DEGREE_MINOR if mode == "minor" else _DEGREE_MAJOR)[target]
    minor_targets = (2, 4, 9) if mode != "minor" else (0, 5)
    return base.lower() if target in minor_targets else base


def analyze_span(
    spans: Sequence[Tuple[float, float, Sequence[int]]],
    lo: float,
    hi: float,
    tonic_pc: int,
    mode: str,
) -> Optional[Dict[str, object]]:
    """Full analysis of one time span: roman, function, root, quality, inversion."""
    weights, bass_pc = pc_weights(spans, lo, hi)
    fit = fit_chord(weights, bass_pc, tonic_pc, mode)
    if fit is None:
        return None
    root, quality, inversion = fit
    roman = spell_roman(root, quality, inversion, tonic_pc, mode)
    applied = applied_target(root, quality, tonic_pc, mode)
    if applied:
        figure = roman.lstrip("b#").lstrip("IiVv")
        roman = f"V{figure}/{applied}" if quality == "dom7" else f"viio{figure}/{applied}"
    return {
        "roman": roman,
        "function": classify_function(root, quality, tonic_pc, mode),
        "root_pc": root,
        "quality": quality,
        "inversion": inversion,
        "degree": (root - tonic_pc) % 12,
        "applied": applied,
    }


def exact(x) -> Fraction:
    """Exact rational value of a music21 offset/quarterLength."""
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(x).limit_denominator(3360)
    except (TypeError, ValueError):
        return Fraction(0)


def candidates(
    weights: Sequence[float], bass_pc: Optional[int], tonic_pc: int, mode: str, top: int = 6
) -> List[Tuple[float, int, str, int]]:
    """Best-scoring (score, root_pc, quality, inversion) readings for one span.

    ``weights`` is a **12-slot vector indexed by pitch class**, as returned by
    ``pc_weights`` — not a ``{pc: weight}`` dict. Passing a dict is silently
    wrong rather than an error: ``sum()`` over a dict adds its KEYS, so the
    total is non-zero, `enumerate` walks the keys as if they were weights, and
    the function returns ``[]`` or nonsense with no exception anywhere. Hence
    the explicit shape check.
    """
    if isinstance(weights, dict):
        raise TypeError(
            "candidates() expects a 12-slot pitch-class vector (as returned by "
            "pc_weights), not a dict. A dict silently produces a wrong total "
            "and an empty result. Convert with "
            "[d.get(pc, 0.0) for pc in range(12)]."
        )
    if len(weights) != 12:
        raise ValueError(
            f"candidates() expects exactly 12 pitch-class weights, got {len(weights)}."
        )
    total = sum(weights)
    if total <= 0:
        return []
    scale = _MAJOR_SCALE if mode != "minor" else _MINOR_SCALE
    sounding = {pc for pc, w in enumerate(weights) if w > total * 0.02}
    if not sounding:
        return []
    # A single sounding pitch class is still a harmony when the key is known: an
    # octave C on the downbeat of a C major cadence is the tonic, not an
    # unreadable bar. Requiring two distinct pitch classes threw away the
    # clearest arrival in tonal music — a final tonic whose bass is struck alone
    # — so the reading skipped the downbeat and picked up the chord a beat or two
    # later, mis-timing and mis-inverting every such cadence.
    solo = len(sounding) == 1
    out: List[Tuple[float, int, str, int]] = []
    for root in range(12):
        for quality, template in CHORD_TEMPLATES:
            tones = [(root + iv) % 12 for iv in template]
            present = [t for t in tones if t in sounding]
            if solo:
                # Read it as the root of its own diatonic triad, nothing fancier.
                if tones[0] not in sounding or len(template) > 3:
                    continue
            else:
                need = 3 if len(tones) > 3 else 2
                if len(present) < need or (tones[0] not in sounding and tones[1] not in sounding):
                    continue
            covered = sum(weights[t] for t in tones)
            foreign = total - covered
            score = covered - 1.6 * foreign
            score -= 0.18 * total * (len(template) - 3)
            score -= 0.08 * total * (len(tones) - len(present))
            if ((root - tonic_pc) % 12) in scale:
                score += 0.10 * total
            if all(((t - tonic_pc) % 12) in scale for t in tones):
                score += 0.12 * total
            inv = 0
            if bass_pc is not None and bass_pc in tones:
                score += 0.10 * total
                inv = tones.index(bass_pc)
                if bass_pc == tones[0]:
                    score += 0.25 * total
            if weights[tones[0]] > 0:
                score += 0.05 * total
            score += _QUALITY_PRIOR.get(quality, 0.0) * total
            score += _diatonic_bonus(root, quality, tones, sounding, tonic_pc, mode) * total
            out.append((score / total, root, quality, inv))
    out.sort(reverse=True)
    return out[:top]


# Cost of changing harmony from one beat to the next, in units of normalized
# score. Harmonic rhythm is slow: reading each beat independently makes a bar
# that prolongs one chord report four different ones, which is where "I7 / I /
# viioø42 / V6" for a bar of plain C major came from.
_CHANGE_PENALTY = 0.45


def analyze_bar(
    spans: Sequence[Tuple[float, float, Sequence[int]]],
    bar_len: float,
    beat_len: float,
    tonic_pc: int,
    mode: str,
    prev_chord: Optional[Tuple[int, str]] = None,
    merge: bool = True,
) -> List[Dict[str, object]]:
    """Harmonic reading of one bar, smoothed for harmonic inertia.

    Returns one entry per distinct HARMONY (``beat`` is 1-based, and is where
    that harmony arrives); pass ``merge=False`` for one entry per beat. A bass
    that arpeggiates inside a held chord changes the inversion but not the
    harmony, and reporting that as a chord change made a cadence look like it
    arrived a beat late, in first inversion, on a weak beat.

    Each entry carries roman/function/root/quality/inversion. A Viterbi pass over the per-beat candidates charges
    for changing chord, so the reading prefers the explanation a listener hears —
    one harmony held across a bar — over the locally best fit at every beat.
    """
    if beat_len <= 0 or not spans:
        return []
    beats: List[Tuple[float, List[Tuple[float, int, str, int]]]] = []
    beat = 0.0
    while beat < bar_len - 1e-6:
        w, bass = pc_weights(spans, beat, min(beat + beat_len, bar_len))
        beats.append((beat, candidates(w, bass, tonic_pc, mode)))
        beat += beat_len
    if not any(c for _, c in beats):
        return []

    # Viterbi over (root, quality); inversion rides along with the winner.
    paths: Dict[Tuple[int, str], Tuple[float, List[Tuple[int, str, int]]]] = {}
    for idx, (_pos, cands) in enumerate(beats):
        if not cands:
            continue
        nxt: Dict[Tuple[int, str], Tuple[float, List[Tuple[int, str, int]]]] = {}
        for sc, root, qual, inv in cands:
            key = (root, qual)
            if not paths:
                base = sc
                if prev_chord is not None and prev_chord != key:
                    base -= _CHANGE_PENALTY
                nxt[key] = (base, [(root, qual, inv)])
                continue
            best_prev, best_val = None, float("-inf")
            for pkey, (pval, _seq) in paths.items():
                val = pval + sc - (0.0 if pkey == key else _CHANGE_PENALTY)
                if val > best_val:
                    best_val, best_prev = val, pkey
            nxt[key] = (best_val, paths[best_prev][1] + [(root, qual, inv)])
        if nxt:
            paths = nxt
    if not paths:
        return []
    _val, seq = max(paths.values(), key=lambda x: x[0])

    positions = [pos for pos, cands in beats if cands]
    out: List[Dict[str, object]] = []
    seen_chord: Optional[Tuple[int, str]] = None
    for pos, (root, qual, inv) in zip(positions, seq):
        if merge and seen_chord == (root, qual):
            continue
        seen_chord = (root, qual)
        roman = spell_roman(root, qual, inv, tonic_pc, mode)
        applied = applied_target(root, qual, tonic_pc, mode)
        if applied:
            figure = roman.lstrip("b#").lstrip("IiVv").replace("o", "").replace("ø", "")
            roman = f"V{figure}/{applied}" if qual == "dom7" else f"viio{figure}/{applied}"
        out.append(
            {
                "beat": round(pos + 1.0, 4),
                "roman": roman,
                "function": classify_function(root, qual, tonic_pc, mode),
                "root_pc": root,
                "quality": qual,
                "inversion": inv,
            }
        )
    return out


# ── Roman numeral -> structure ────────────────────────────────────────────────
#
# The inverse of `spell_roman`. It exists so nothing has to hand-maintain a
# lookup table of symbols: the two tables that used to do this job listed
# "viio7" but not "V7", and "I6" but not "I64", so every dominant seventh in
# every progression model was silently degraded to a plain triad and every
# second-inversion chord to root position. A parser cannot have holes.

_NUMERAL_DEGREE_MAJOR = {"I": 0, "II": 2, "III": 4, "IV": 5, "V": 7, "VI": 9, "VII": 11}
_NUMERAL_DEGREE_MINOR = {"I": 0, "II": 2, "III": 3, "IV": 5, "V": 7, "VI": 8, "VII": 10}

_FIGURE_TO_INVERSION = {
    "": (3, 0),
    "6": (3, 1),
    "64": (3, 2),
    "7": (4, 0),
    "65": (4, 1),
    "43": (4, 2),
    "42": (4, 3),
    "2": (4, 3),
    "9": (4, 0),
    "53": (3, 0),
    "63": (3, 1),
}

# Chords whose symbol is a name rather than a numeral+figure. music21 writes the
# augmented sixths with their figured-bass digits attached ("Ger65", "Fr43"), and
# a table keyed only on the bare names missed every one of them — they appear in
# the Mozart and Beethoven corpora and were silently dropped from the progression
# model and rendered as "?" in the chord frame.
_SPECIAL_ROMANS = {
    "N": (1, "major", 0),
    "N6": (1, "major", 1),
    "It6": (8, "major", 0),
    "It": (8, "major", 0),
    "Fr6": (8, "dom7", 0),
    "Fr43": (8, "dom7", 2),
    "Fr": (8, "dom7", 0),
    "Ger6": (8, "dom7", 0),
    "Ger65": (8, "dom7", 1),
    "Ger7": (8, "dom7", 0),
    "Ger": (8, "dom7", 0),
    "Sw": (8, "dom7", 0),
    "Cad64": (0, "major", 2),
}

_ROMAN_RE = None


def parse_roman(symbol: str, mode: str = "major") -> Optional[Dict[str, object]]:
    """``"V65/V"`` -> {degree, quality, inversion, applied}. None if unreadable.

    ``degree`` is semitones above the tonic; ``inversion`` is 0-3.
    """
    global _ROMAN_RE
    if not symbol:
        return None
    import re

    if _ROMAN_RE is None:
        _ROMAN_RE = re.compile(
            r"^(?P<acc>[b#-]*)(?P<num>[ivIV]+)(?P<qual>maj|o7|o|°7|°|ø7|ø|%|\+|M)?"
            r"(?P<fig>64|65|43|42|53|63|9|7|6|2)?$"
        )
    sym = str(symbol).strip()
    applied = None
    if "/" in sym:
        sym, target = sym.split("/", 1)
        applied = target.strip()
    if sym in _SPECIAL_ROMANS:
        deg, qual, inv = _SPECIAL_ROMANS[sym]
        return {"degree": deg, "quality": qual, "inversion": inv, "applied": applied}
    m = _ROMAN_RE.match(sym)
    if not m:
        return None
    acc, num, qual, fig = (
        m.group("acc"),
        m.group("num"),
        m.group("qual") or "",
        m.group("fig") or "",
    )
    table = _NUMERAL_DEGREE_MINOR if mode == "minor" else _NUMERAL_DEGREE_MAJOR
    base = table.get(num.upper())
    if base is None:
        return None
    degree = (base + acc.count("#") - acc.count("b") - acc.count("-")) % 12

    size, inversion = _FIGURE_TO_INVERSION.get(fig, (3, 0))
    if qual in ("maj", "M"):
        quality, size = "maj7", 4
    elif qual in ("o7", "°7"):
        quality, size = "dim7", 4
    elif qual in ("ø7", "ø", "%"):
        quality, size = "halfdim7", 4
    elif qual in ("o", "°"):
        quality = "dim7" if size == 4 else "dim"
    elif qual == "+":
        quality = "aug"
    elif num.islower():
        quality = "min7" if size == 4 else "minor"
    else:
        quality = "dom7" if size == 4 else "major"
    if size == 4 and quality in ("major", "minor", "dim"):
        quality = {"major": "dom7", "minor": "min7", "dim": "dim7"}[quality]
    if inversion >= len(dict(CHORD_TEMPLATES)[quality]):
        inversion = 0

    if applied:
        tgt = parse_roman(applied, mode)
        if tgt is not None:
            degree = (degree + tgt["degree"]) % 12
    return {"degree": degree, "quality": quality, "inversion": inversion, "applied": applied}


def roman_degree(symbol: str, mode: str = "major") -> int:
    """Semitones above the tonic for a Roman numeral (0 when unreadable)."""
    parsed = parse_roman(symbol, mode)
    return int(parsed["degree"]) if parsed else 0


def roman_quality(symbol: str, mode: str = "major") -> str:
    """Chord quality for a Roman numeral ("major" when unreadable)."""
    parsed = parse_roman(symbol, mode)
    return str(parsed["quality"]) if parsed else "major"


def roman_pitches(symbol: str, tonic_pc: int, mode: str = "major") -> List[int]:
    """Pitch classes of a Roman numeral, bass first."""
    parsed = parse_roman(symbol, mode)
    if not parsed:
        return []
    template = dict(CHORD_TEMPLATES)[str(parsed["quality"])]
    root = (tonic_pc + int(parsed["degree"])) % 12
    tones = [(root + iv) % 12 for iv in template]
    inv = int(parsed["inversion"]) % len(tones)
    return tones[inv:] + tones[:inv]


def roman_function(symbol: str, mode: str = "major") -> str:
    """Harmonic function of a Roman numeral symbol."""
    parsed = parse_roman(symbol, mode)
    if not parsed:
        return "chromatic"
    return classify_function(int(parsed["degree"]), str(parsed["quality"]), 0, mode)
