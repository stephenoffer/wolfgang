#!/usr/bin/env python3
"""
Build comprehensive corpus from all available sources:
1. Existing reference_scores/ kern files (224 files: Mozart, Beethoven, Chopin)
2. music21 built-in corpus (433 Bach, 26 Beethoven, 16 Mozart, 9 Haydn)
3. Extract bar indices for all composers found
4. Build patterns and add to the pattern library

This script extends the corpus beyond the original 3 composers.
"""

import json
import os
import re
import time
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REF_INDEX = BASE / "reference_index"
REF_INDEX.mkdir(exist_ok=True)


def _staff_voices(measure, bar_len=None, prefer="top"):
    """Split a staff's measure into (main, inner) timed note/rest lists.

    ``prefer`` picks which line is the MAIN one: "top" for the upper staff (the
    melody is the highest line) and "bottom" for the lower staff (the bass is the
    lowest line). Using "top" for both put the inner figuration of a two-voice
    left hand into ``lh_display`` and hid the actual bass in the inner voice — so
    every left-hand exemplar of a pedal-under-figuration bar showed the filler
    rather than the foundation it sits on.

    Returns two lists of ``(offset, element)`` pairs — one per independent
    notated voice — where no two elements in the same list overlap in time.

    This is what makes an exemplar bar SUM TO THE BAR. Previously the left hand
    was read with a bare ``measure.recurse().notesAndRests``, which flattens
    simultaneous voices into one sequential stream: a two-voice LH came out at
    twice the bar's length. Measured over the shipped corpus, that produced
    left-hand exemplars overflowing their own bar in 51% of Liszt bars, 19% of
    Chopin, 16% of Beethoven and 12% of Mozart — bars the agent was told to
    study and adapt.

    Explicit ``Voice`` containers are honored when present; otherwise
    overlapping content is packed greedily into two voices by pitch height.
    """
    voices = list(measure.getElementsByClass("Voice"))
    if len(voices) >= 2:

        def mean_pitch(v):
            ps = [p.midi for n in v.notes for p in n.pitches]
            return sum(ps) / len(ps) if ps else 0.0

        ordered = sorted(voices, key=mean_pitch, reverse=(prefer == "top"))
        main = [(float(el.offset), el) for el in ordered[0].notesAndRests]
        inner = [(float(el.offset), el) for v in ordered[1:] for el in v.notesAndRests]
        return sorted(main, key=lambda x: x[0]), sorted(inner, key=lambda x: x[0])

    # No explicit voices: pack by onset. Notes that start while an earlier note
    # is still sounding belong to a second voice, not later in the same line.
    items = []
    for el in measure.recurse().notesAndRests:
        try:
            items.append((float(el.offset), el))
        except (TypeError, ValueError):
            continue

    def top_midi(el):
        try:
            return max(p.midi for p in el.pitches)
        except (ValueError, AttributeError):
            return -1

    def low_midi(el):
        try:
            return min(p.midi for p in el.pitches)
        except (ValueError, AttributeError):
            return 128

    # At a shared onset the MAIN voice's note is taken first: the highest for an
    # upper staff, the lowest for a lower staff.
    items.sort(key=lambda x: (x[0], -top_midi(x[1]) if prefer == "top" else low_midi(x[1])))
    main, inner = [], []
    main_end = inner_end = -1e9
    for off, el in items:
        if el.isRest:
            continue  # rests are re-derived from the gaps, so they can't double-count
        dur = float(el.quarterLength)
        if off >= main_end - 1e-6:
            main.append((off, el))
            main_end = off + dur
        elif off >= inner_end - 1e-6:
            inner.append((off, el))
            inner_end = off + dur
        # a third simultaneous layer is dropped: two voices is what the '//'
        # shorthand can express, and keeping it would overflow the bar again
    return main, inner


# Gaps smaller than a 64th are notation noise, not rests.
_MIN_GAP = Fraction(1, 16)
# Shortest gap that can be a real, heard rest (a 16th).
_REST_MIN = Fraction(1, 4)


def _frac(x) -> Fraction:
    """Exact rational value of a music21 offset/quarterLength.

    music21 hands back ``Fraction`` for tuplets and ``float`` elsewhere; both
    must land on the same exact value or a cursor built from one will not meet an
    onset expressed as the other.
    """
    if isinstance(x, Fraction):
        return x
    try:
        return Fraction(x).limit_denominator(_OFFSET_DENOM)
    except (TypeError, ValueError):
        return Fraction(0)


# Largest denominator a notated position can have: 64ths (1/16), triplet-32nds
# (1/12), sextuplet-32nds (1/24), quintuplets (1/5), septuplets (1/7).
_OFFSET_DENOM = 3360


def _round_dur(x) -> float:
    """Duration as a JSON-safe float, kept exact enough to re-read as the same
    rational (1/6 -> 0.166667, which limit_denominator recovers as 1/6)."""
    return round(float(x), 6)


def _clean_roman(figure):
    """Reduce a music21 Roman figure to a readable symbol.

    music21 emits raw figured bass — "bII#7#3", "iii4b3", "#ivob5", "viio#74" —
    which is not something to hand a composer as "the harmony of this bar". Keeps
    the accidental, the numeral, the quality mark and a standard inversion figure;
    drops the rest.
    """
    import re as _re

    if not figure:
        return figure
    m = _re.match(r"^([b#-]*)([ivIV]+)(o|0|ø|\+|%)?(64|65|43|42|6|7|2)?", str(figure).strip())
    if not m:
        return figure
    acc, numeral, quality, inversion = m.group(1), m.group(2), m.group(3) or "", m.group(4) or ""
    return f"{acc.replace('-', 'b')}{numeral}{quality}{inversion}"


# music21 expression class -> the shorthand ornament suffix that writes it.
_ORNAMENT_CLASSES = (
    ("Trill", "tr"),
    ("Mordent", "mord"),
    ("Turn", "turn"),
    ("Appoggiatura", "grace"),
    ("Schleifer", "grace"),
)


def _ornament_of(el):
    """Shorthand ornament code on this note, or None.

    The sources carry trills, mordents and turns (one Mozart movement has 17
    trills, 12 mordents and a turn) and the extractor discarded every one of
    them, so the corpus taught that real Mozart barely ornaments — while the
    brief's ornament targets came from a hand-authored file with no builder.
    `corpus_adapter` was already looking for `has_trill`/`has_turn` on events:
    dead code waiting for data that was never recorded.
    """
    try:
        for expr in el.expressions:
            name = type(expr).__name__
            for needle, code in _ORNAMENT_CLASSES:
                if needle in name:
                    return code
    except AttributeError:
        pass
    return None


def _rest_spans(measure):
    """(start, end) of every rest the source actually NOTATES in this measure.

    A gap between two onsets can be either a written rest or the silence left by
    a detached/gated note, and the two must not be conflated: filling a written
    rest destroys Mozart's phrasing, while writing a rest for every MIDI note-off
    turns continuous figuration into a stutter. The notation decides.
    """
    spans = []
    try:
        for el in measure.recurse().notesAndRests:
            if not getattr(el, "isRest", False):
                continue
            st = _frac(el.offset)
            spans.append((st, st + _frac(el.quarterLength)))
    except (TypeError, ValueError, AttributeError):
        return []
    return spans


def _timed_records(timed, tonic_pc, bar_len, cap=32, rest_spans=()):
    """Build (display, events, has_rests, truncated) for one voice of a measure.

    ``timed`` is the ``(offset, element)`` list from :func:`_staff_voices`. Rests
    are derived from the GAPS between onsets and a note is never allowed to run
    past the next onset or past the barline, so the record's durations sum to at
    most ``bar_len`` by construction.

    Each note/chord carries ``interval_from_root`` (semitones above the bar's
    tonic, key-agnostic) so the corpus adapter can transpose it to any key.
    ``display`` keeps absolute pitch names; ``events`` is pitch-free.
    """
    display, events = [], []
    has_rests = False
    truncated = False
    cursor = Fraction(0)
    bar_len_f = _frac(bar_len)

    def _emit(rec_display, rec_events):
        nonlocal truncated
        if len(display) < cap:
            display.append(rec_display)
            events.append(rec_events)
        else:
            truncated = True

    # Exact rational arithmetic throughout. Rounding the cursor to 4 decimals
    # put it AHEAD of the next exact onset for every tuplet: a sextuplet's second
    # note (offset 1/6 = 0.166666…) tested as "already covered" by a cursor of
    # 0.1667 and was DROPPED, and the note after it then read as a gap and became
    # a rest. Every triplet and sextuplet run in the corpus came out
    # note-rest-note-rest with half its pitches missing — the flowing figuration
    # the agent is meant to learn from, deleted at extraction time.
    ordered = sorted(((_frac(o), el) for o, el in timed), key=lambda x: x[0])
    for i, (off, el) in enumerate(ordered):
        if off > cursor + _MIN_GAP:  # a real gap → a rest
            has_rests = True
            gap = off - cursor
            _emit(
                {"type": "rest", "dur": _round_dur(gap)},
                {"type": "rest", "dur": _round_dur(gap)},
            )
            cursor = off
        elif off < cursor:
            continue  # already covered by a sounding note in this voice
        is_grace = bool(getattr(el.duration, "isGrace", False))
        orn = _ornament_of(el)
        next_off = ordered[i + 1][0] if i + 1 < len(ordered) else None
        limit = bar_len_f if next_off is None else min(bar_len_f, next_off)
        raw = Fraction(0) if is_grace else _frac(el.quarterLength)
        dur = Fraction(0) if is_grace else max(Fraction(0), min(raw, limit - off))
        # Articulation is not silence. A source whose notes are gated short
        # (every MIDI-derived score, and any kern with staccato) leaves a sliver
        # of a gap after each note; emitting those as rests turns a continuous
        # accompaniment figure into a stutter. A gap counts as a rest only when
        # it is at least a 16th AND at least half the inter-onset interval.
        if next_off is not None and dur > 0:
            ioi = next_off - off
            gap_lo, gap_hi = off + dur, next_off
            notated = any(rs < gap_hi and re_ > gap_lo for rs, re_ in rest_spans)
            if not notated and 0 < ioi - dur:
                dur = ioi
        if dur < _MIN_GAP and not is_grace:
            continue
        if getattr(el, "isChord", False):
            pitches = list(el.pitches)
            iroot = (min(p.pitchClass for p in pitches) - tonic_pc) % 12
            _emit(
                {
                    "type": "chord",
                    "pitches": [p.nameWithOctave for p in pitches],
                    "intervals": [(p.pitchClass - tonic_pc) % 12 for p in pitches],
                    "interval_from_root": iroot,
                    "dur": _round_dur(dur),
                    "is_grace": is_grace,
                    "orn": orn,
                },
                {
                    "type": "chord",
                    "intervals": [(p.pitchClass - tonic_pc) % 12 for p in pitches],
                    "interval_from_root": iroot,
                    "dur": _round_dur(dur),
                    "is_grace": is_grace,
                    "orn": orn,
                },
            )
        elif hasattr(el, "pitch"):
            iroot = (el.pitch.pitchClass - tonic_pc) % 12
            _emit(
                {
                    "type": "note",
                    "pitch": el.pitch.nameWithOctave,
                    "interval_from_root": iroot,
                    "dur": _round_dur(dur),
                    "is_grace": is_grace,
                    "orn": orn,
                },
                {
                    "type": "note",
                    "interval_from_root": iroot,
                    "dur": _round_dur(dur),
                    "is_grace": is_grace,
                    "orn": orn,
                },
            )
        else:
            continue
        cursor = off + dur

    # A rest that runs to the barline is part of the bar's rhythm. Without it a
    # bar ending in silence does not sum to the meter, and every consumer that
    # reads the record as a bar (exemplars, density, the breathing detector) sees
    # a short bar rather than a phrase coming to rest.
    if display and cursor < bar_len_f - _MIN_GAP:
        has_rests = True
        _emit(
            {"type": "rest", "dur": _round_dur(bar_len_f - cursor)},
            {"type": "rest", "dur": _round_dur(bar_len_f - cursor)},
        )

    # Adjacent rests are one silence, not two. Splitting them (a bar's rest
    # arriving as 2.0 + 1.0) made every rest count and every breathing
    # measurement read two events where a listener hears one.
    return _merge_rests(display), _merge_rests(events), has_rests, truncated


def _merge_rests(recs):
    """Collapse runs of adjacent rests into one."""
    out = []
    for r in recs:
        if r.get("type") == "rest" and out and out[-1].get("type") == "rest":
            out[-1] = {"type": "rest", "dur": round(out[-1]["dur"] + r["dur"], 6)}
        else:
            out.append(r)
    return out


# Krumhansl-Kessler key profiles (major, minor), indexed from the tonic.
_KK_MAJOR = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
_KK_MINOR = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
_PC_NAMES = ("C", "C#", "D", "E-", "E", "F", "F#", "G", "A-", "A", "B-", "B")
# Key names spelled the way the key signature is actually written: the same
# pitch class is D-flat major but C-sharp minor, and A-flat major but G-sharp
# minor. Naming both "C#" put a seven-sharp signature on a five-flat piece.
_KEY_NAMES_MAJOR = ("C", "D-", "D", "E-", "E", "F", "F#", "G", "A-", "A", "B-", "B")
_KEY_NAMES_MINOR = ("C", "C#", "D", "E-", "E", "F", "F#", "G", "G#", "A", "B-", "B")


def _key_from_weights(weights):
    """Best (name, mode, tonic_pc) for a 12-slot pitch-class duration vector.

    Plain Krumhansl-Schmuckler correlation — the same algorithm music21 uses,
    computed directly so a rolling window costs a dot product instead of
    building and analysing a stream per bar.
    """
    total = sum(weights)
    if total <= 0:
        return None
    mean_w = total / 12.0
    dev = [w - mean_w for w in weights]
    denom_w = sum(d * d for d in dev) ** 0.5
    best, best_r = None, -2.0
    for mode, profile in (("major", _KK_MAJOR), ("minor", _KK_MINOR)):
        mean_p = sum(profile) / 12.0
        pdev = [p - mean_p for p in profile]
        denom_p = sum(d * d for d in pdev) ** 0.5
        for tonic in range(12):
            num = sum(dev[(tonic + i) % 12] * pdev[i] for i in range(12))
            r = num / (denom_w * denom_p) if denom_w and denom_p else 0.0
            if r > best_r:
                names = _KEY_NAMES_MINOR if mode == "minor" else _KEY_NAMES_MAJOR
                best_r, best = r, (names[tonic], mode, tonic)
    return best


# How strongly the movement's overall key pulls each local window back toward it.
# 0 = pure local vote (flips on any subdominant passage); 1 = the local window is
# outweighed by the whole movement and modulations vanish.
_HOME_KEY_PRIOR = 0.6


def _windowed_keys(measures, window=8, extra_parts=()):
    """Local key per measure index, analysed over a WINDOW of bars.

    ``measure.analyze("key")`` on a single bar is close to noise: Krumhansl on
    three or four pitches. Measured on the shipped corpus it labelled 411 of
    4000 Chopin bars as C# — Chopin did not write a tenth of his music in C#.
    Every ``interval_from_root`` in every exemplar is relative to that tonic, so
    exemplars arrived in briefs transposed by a wrong interval, and every Roman
    numeral (hence the whole corpus progression model) was derived against a
    wrong local tonic.

    A rolling window of bars is stable enough to be meaningful and still tracks
    real modulation. Returns a list of (name, mode, tonic_pc) per measure index.
    """
    n = len(measures)
    if not n:
        return []

    # Pitch-class duration weights per bar, summed over a sliding window. EVERY
    # staff counts: reading only the melody part threw away the bass, which is
    # the strongest single evidence for both key and mode.
    from music21 import stream as _stream

    extra_measures = [list(p.getElementsByClass(_stream.Measure)) for p in extra_parts]
    per_bar = []
    for i, m in enumerate(measures):
        w = [0.0] * 12
        sources = [m] + [ms[i] for ms in extra_measures if i < len(ms)]
        for src in sources:
            try:
                for el in src.recurse().notes:
                    dur = float(el.quarterLength) or 0.25
                    for pch in el.pitches:
                        w[pch.pitchClass] += dur
            except (TypeError, ValueError, AttributeError):
                continue
        per_bar.append(w)

    out = []
    half = max(1, window // 2)
    total = [sum(b[i] for b in per_bar) for i in range(12)]
    fallback = _key_from_weights(total) or ("C", "major", 0)

    # The home key is a PRIOR, not just another candidate. A bare window vote
    # flips on any passage that dwells on the subdominant: bar 1 of K.279/ii — an
    # F major movement — came out B-flat, so every Roman numeral in the opening
    # was read against the wrong tonic. Mixing a scaled-down copy of the whole
    # movement's pitch-class weights into each window means a local key has to
    # actually earn the modulation, while real modulations (which dominate their
    # own window) still win.
    grand = sum(total) or 1.0
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half)
        agg = [0.0] * 12
        for b in per_bar[lo:hi]:
            for pc in range(12):
                agg[pc] += b[pc]
        window_mass = sum(agg)
        if window_mass:
            prior = _HOME_KEY_PRIOR * window_mass / grand
            for pc in range(12):
                agg[pc] += total[pc] * prior
        out.append(_key_from_weights(agg) or fallback)
    return out


def _phrase_positions(bars):
    """Label each bar's position in its PHRASE, not in the whole movement.

    The old rule was positional over the entire score (first two bars
    "opening", last four "cadential"/"closing"), so 94% of every corpus was
    labelled "middle" and only ~80 of 4000 Chopin bars were ever "cadential".
    Cadence-scoped retrieval had almost nothing to retrieve, and the breathing
    detector — which keys off this field — only ever inspected the last four
    bars of a piece.

    A bar ends a phrase when the melody comes to rest there (a note at least
    half the bar long, or a rest of a beat or more at the end) AND the bar sits
    on a tonic or dominant. The bar after a phrase end opens the next phrase.
    """
    n = len(bars)
    if not n:
        return
    ends = []
    for i, b in enumerate(bars):
        ts = b.get("time_sig") or [4, 4]
        bar_len = ts[0] * 4.0 / ts[1]
        line = b.get("melody_line") or []
        rests_at_rest = any(e.get("type") == "rest" and e.get("dur", 0) >= 1.0 for e in line[-2:])
        long_note = any(
            e.get("type") == "note" and e.get("dur", 0) >= bar_len / 2 for e in line[-2:]
        )
        fn = (b.get("function") or "").lower()
        arrival = fn in ("tonic", "dominant")
        ends.append(bool((rests_at_rest or long_note) and arrival))
    ends[-1] = True  # a piece always ends its last phrase
    for i, b in enumerate(bars):
        if ends[i]:
            b["phrase_position"] = "closing" if i == n - 1 else "cadential"
        elif i == 0 or (i > 0 and ends[i - 1]):
            b["phrase_position"] = "opening"
        elif i + 1 < n and ends[i + 1]:
            b["phrase_position"] = "approach"
        else:
            b["phrase_position"] = "middle"


def _detect_melody_part_index(parts):
    """Index of the part carrying the melody = highest mean top-MIDI.

    parts[0] is the wrong staff for many MIDI files (bass first) and ambiguous
    for SATB. Empty parts score -inf; returns 0 when nothing is pitched so
    single-part / degenerate scores never regress.
    """
    best_idx, best_mean = 0, float("-inf")
    for i, p in enumerate(parts):
        tops = []
        for n in p.recurse().notes:
            try:
                tops.append(max(x.midi for x in n.pitches))
            except Exception:
                continue
        if tops:
            m = sum(tops) / len(tops)
            if m > best_mean:
                best_mean, best_idx = m, i
    return best_idx


def _skyline_line(measure, tonic_pc, bar_len=4.0, cap=24):
    """The melody line of a measure: its top voice, in time order, with rests.

    Read through the same voice split as the exemplars. ``recurse().notesAndRests``
    returns document order and interleaves simultaneous voices, so for any bar
    with a two-voice right hand the "melody" was a concatenation of both voices —
    which is what every melodic statistic, the phrase-boundary detector and the
    theme comparison were reading.
    """
    if measure is None:
        return []
    top, _inner = _staff_voices(measure, bar_len)
    display, _events, _hr, _tr = _timed_records(
        top, tonic_pc, bar_len, cap=cap, rest_spans=_rest_spans(measure)
    )
    out = []
    for rec in display:
        if rec["type"] == "rest":
            out.append({"type": "rest", "dur": rec["dur"]})
            continue
        if rec.get("is_grace"):
            continue
        name = rec.get("pitch") or (rec.get("pitches") or [None])[-1]
        if not name:
            continue
        try:
            from music21 import pitch as m21pitch

            midi = m21pitch.Pitch(name).midi
        except Exception:
            continue
        out.append(
            {
                "type": "note",
                "pitch": name,
                "midi": midi,
                "interval_from_root": (midi - tonic_pc) % 12,
                "dur": rec["dur"],
            }
        )
    return out


def _classify_function(roman_alone):
    """Legacy string classifier, kept only for reading OLD bar records.

    New extraction classifies from structure (see
    ``scales.harmony_analysis.classify_function``): matching the printed figure
    against seven bare symbols is what made ``I6``, ``V7``, ``ii65`` and every
    flat numeral in a minor key "chromatic" — 42.6% of the shipped corpus.
    """
    r = (roman_alone or "").lower().strip()
    r = re.sub(r"(64|65|43|42|6|7|2)$", "", r)
    r = r.replace("o", "").replace("ø", "").replace("+", "").replace("%", "")
    r = r.split("/")[0]
    if r in ("i", "iii", "vi", "biii", "bvi"):
        return "tonic"
    if r in ("ii", "iv", "bii", "n"):
        return "predominant"
    if r in ("v", "vii", "bvii"):
        return "dominant"
    return "chromatic"


def _beat_len(time_sig):
    """Length of ONE heard beat, in quarter notes.

    4/denom is the notated unit, not the beat: in 6/8 that samples the harmony
    every eighth, three times per beat, which reports harmonic motion where a
    listener hears one chord. Compound meters beat in dotted values.
    """
    num, denom = int(time_sig[0]), int(time_sig[1])
    if denom == 8 and num in (6, 9, 12):
        return 1.5
    if denom == 2:
        return 2.0
    return 4.0 / denom


def _midi_spans(chord_measure):
    """(start, end, [midi, ...]) for every sonority in a chordified measure."""
    from music21 import chord as m21chord

    spans = []
    for c in chord_measure.recurse().getElementsByClass(m21chord.Chord):
        try:
            st = float(c.offset)
            ql = float(c.quarterLength)
        except (TypeError, ValueError):
            continue
        midis = [p.midi for p in c.pitches]
        if midis and ql > 0:
            spans.append((st, st + ql, midis))
    return spans


def _bar_harmony(chord_measure, score_key, tonic_pc, bar_len=4.0, beat_len=1.0, prev=None):
    """Roman / function / root for one bar, plus where the harmony MOVES inside it.

    The bar's headline harmony is what it SITS ON — the downbeat reading. The
    within-bar events are the harmonies it actually passes through, which is what
    lets a plan express a cadence compressed into a single bar rather than
    implying one chord per bar everywhere.
    """
    from scales.harmony_analysis import analyze_bar

    if chord_measure is None:
        return {}
    spans = _midi_spans(chord_measure)
    if not spans:
        return {}
    mode = "minor" if str(getattr(score_key, "mode", "")) == "minor" else "major"
    beats = analyze_bar(spans, bar_len, beat_len, tonic_pc, mode, prev_chord=prev)
    if not beats:
        return {}
    # Only a genuine CHANGE is an event: a bar prolonging one chord reports one
    # harmony, not one reading per beat.
    events = []
    last = None
    for b in beats:
        if b["roman"] != last:
            last = b["roman"]
            events.append({"beat": b["beat"], "roman": b["roman"], "function": b["function"]})
    head = beats[0]
    return {
        "roman": head["roman"],
        "function": head["function"],
        "chord_root": _PC_NAMES[head["root_pc"] % 12],
        "chord_root_interval": (head["root_pc"] - tonic_pc) % 12,
        "chord_quality": head["quality"],
        "harmony_events": events,
        "_last_chord": (beats[-1]["root_pc"], beats[-1]["quality"]),
    }


def analyze_score_bars(score, composer, source_name):
    """Extract bar-level data from a music21 score, matching the existing bar_index format."""
    from music21 import meter as m21meter
    from music21 import stream

    bars = []
    parts = list(score.parts)
    if not parts:
        return bars

    # The real MELODY part (highest mean register) — NOT blindly parts[0], which
    # is the bass staff in many MIDI files (e.g. Liszt).
    mel_idx = _detect_melody_part_index(parts)
    mel_part = parts[mel_idx]
    mel_measures = list(mel_part.getElementsByClass(stream.Measure))

    # The upper staff IS the melody part, and the lower staff is whatever else
    # there is. Hard-coding parts[0] as the right hand meant that for every
    # bass-first MIDI source the "RH melody exemplar" shown in briefs was
    # actually the left hand, and the two densities were swapped.
    rh_part = mel_part
    others = [p for i, p in enumerate(parts) if i != mel_idx]
    lh_part = others[0] if others else None
    rh_inner_parts: list = []
    lh_inner_parts: list = []
    if len(others) > 1:
        # More than two staves — SATB, a chorale, a mass, a reduction. Taking two
        # parts and dropping the rest kept only 33% of the notes of a Bach chorale
        # and 39% of a Palestrina mass: the alto and tenor of every contrapuntal
        # score in the corpus were discarded, so the one body of music the system
        # has for COUNTERPOINT taught nothing but outer voices.
        #
        # Fold them into a keyboard layout instead: the melody part leads the
        # upper staff, the lowest part is the bass, and everything between becomes
        # an inner voice of whichever staff it sits closer to — which is exactly
        # what the brief's '//' two-voice-per-hand syntax can express.
        lh_part = min(others, key=_mean_top_midi)
        middle = [p for p in others if p is not lh_part]
        if middle:
            top_reg = _mean_top_midi(mel_part)
            bass_reg = _mean_top_midi(lh_part)
            split = (top_reg + bass_reg) / 2.0
            for part in middle:
                (rh_inner_parts if _mean_top_midi(part) >= split else lh_inner_parts).append(part)

    # Score-level key + a single chordify for per-bar harmonic (roman) analysis.
    score_key = None
    chordified_by_num = {}
    try:
        score_key = score.analyze("key")
        chordy = score.chordify()
        for cm in chordy.getElementsByClass(stream.Measure):
            chordified_by_num[cm.number] = cm
    except Exception:
        pass

    measures_rh = list(rh_part.getElementsByClass(stream.Measure))
    # Local key per bar over a rolling window — a single bar is not enough
    # evidence to name a key (see _windowed_keys).
    local_keys = _windowed_keys(measures_rh, extra_parts=[p for p in parts if p is not rh_part])

    prev_chord = None
    for mi, measure in enumerate(measures_rh):
        # `if measure.number` treats a PICKUP measure (numbered 0) as falsy and
        # renumbers it to 1, colliding with the real bar 1 — and every later
        # lookup keyed on bar_num then points one bar early. The harmony lookup
        # below (`chordified_by_num[bar_num]`) is one of them, so for the 40% of
        # movements that open with an upbeat, EVERY bar carried the Roman numeral
        # of the bar before it. That fed the progression model, the chord frames,
        # and every harmonic detector.
        bar_num = measure.number if measure.number is not None else mi + 1

        # Time signature: prefer a local marking, else the active one in context
        # (MIDI/score TS often declared only at the first bar). Default 4/4.
        ts_obj = measure.timeSignature or measure.getContextByClass(m21meter.TimeSignature)
        time_sig = [ts_obj.numerator, ts_obj.denominator] if ts_obj else [4, 4]

        # RH analysis. Inner parts folded onto this staff count as part of what
        # the staff plays — otherwise a chorale's soprano+alto reports the density
        # of the soprano alone, and the texture classifier calls a four-part
        # chorale a single "singing melody".
        rh_notes = list(measure.recurse().notes) + [
            el for _off, el in _extra_part_voices(rh_inner_parts, mi)
        ]
        rh_density = len(rh_notes)

        # RH texture: classified from what the bar DOES per beat, not from a raw
        # note count. Counting per bar conflated a 3/8 bar with a 4/4 bar, and
        # the old `<= 8` branch tested `hasattr(n, "pitch")` — true for every
        # Note — so "chordal" was unreachable and 81% of Chopin's bars came out
        # labelled "singing_melody". Texture-scoped retrieval and every
        # per-texture density statistic were built on that.
        rh_texture = _classify_rh_texture(rh_notes, time_sig)

        # Grace notes and dotted rhythms
        has_grace = any(n.duration.isGrace for n in rh_notes if hasattr(n, "duration"))
        bar_ornaments = [o for o in (_ornament_of(n) for n in rh_notes) if o and o != "grace"]
        has_dotted = any(n.duration.dots > 0 for n in rh_notes if hasattr(n, "duration"))

        # LH analysis
        lh_density = 0
        lh_texture = "silence"
        lh_measure = None

        if lh_part:
            lh_measures = list(lh_part.getElementsByClass(stream.Measure))
            if mi < len(lh_measures):
                lh_measure = lh_measures[mi]
                lh_notes = list(lh_measure.recurse().notes) + [
                    el for _off, el in _extra_part_voices(lh_inner_parts, mi)
                ]
                lh_density = len(lh_notes)

                lh_texture = _classify_lh_texture(lh_notes, time_sig)

        # Local key (windowed — see _windowed_keys)
        key_name, key_mode, tonic_pc = local_keys[mi] if mi < len(local_keys) else ("C", "major", 0)

        # Note-level display + events (with interval_from_root for transposition).
        # Both hands go through the timed two-voice split, so the records sum to
        # the bar instead of concatenating simultaneous voices end to end.
        bar_len = time_sig[0] * 4.0 / time_sig[1]
        rh_top, rh_inner = _staff_voices(measure, bar_len)
        rh_inner = rh_inner + _extra_part_voices(rh_inner_parts, mi)
        rh_rests = _rest_spans(measure)
        rh_display, rh_events, rh_has_rests, rh_trunc = _timed_records(
            rh_top, tonic_pc, bar_len, rest_spans=rh_rests
        )
        rh_inner_display = (
            _timed_records(rh_inner, tonic_pc, bar_len, rest_spans=rh_rests)[0] if rh_inner else []
        )
        if lh_measure is not None:
            lh_top, lh_inner = _staff_voices(lh_measure, bar_len, prefer="bottom")
            lh_inner = lh_inner + _extra_part_voices(lh_inner_parts, mi)
            lh_rests = _rest_spans(lh_measure)
            lh_display, lh_events, lh_has_rests, lh_trunc = _timed_records(
                lh_top, tonic_pc, bar_len, rest_spans=lh_rests
            )
            lh_inner_display = (
                _timed_records(lh_inner, tonic_pc, bar_len, rest_spans=lh_rests)[0]
                if lh_inner
                else []
            )
        else:
            lh_display, lh_events, lh_has_rests, lh_trunc = [], [], False, False
            lh_inner_display = []
        has_rests = rh_has_rests or lh_has_rests
        truncated = rh_trunc or lh_trunc

        # Real melody line (skyline of the detected melody part) + its register.
        mel_measure = mel_measures[mi] if mi < len(mel_measures) else None
        melody_line = _skyline_line(mel_measure, tonic_pc, bar_len)
        mel_midis = [e["midi"] for e in melody_line if e["type"] == "note"]
        melody_register = round(sum(mel_midis) / len(mel_midis)) if mel_midis else None

        # Per-bar harmony (roman / function / root) from the chordified score,
        # read against the LOCAL key rather than the movement's opening key.
        local_key = _key_obj(key_name, key_mode) or score_key
        harm = _bar_harmony(
            chordified_by_num.get(bar_num),
            local_key,
            tonic_pc,
            bar_len=bar_len,
            beat_len=_beat_len(time_sig),
            prev=prev_chord,
        )
        # Harmonic inertia carries ACROSS the barline too — a chord held from the
        # previous bar should not be re-analysed as something new on the downbeat.
        prev_chord = harm.pop("_last_chord", None) or prev_chord

        # Direction and register come from the MELODY LINE, in time order.
        # Reading them off `recurse().notes` used document order, and its
        # `hasattr(n, "pitch")` filter dropped every chord — so a bar whose upper
        # staff is chordal reported "static" and a register of 60 regardless of
        # what it plays.
        if len(mel_midis) >= 2:
            if mel_midis[-1] > mel_midis[0] + 2:
                direction = "ascending"
            elif mel_midis[-1] < mel_midis[0] - 2:
                direction = "descending"
            else:
                direction = "static"
        else:
            direction = "static"
        register = sum(mel_midis) / len(mel_midis) if mel_midis else 60

        # Density is what the RECORD shows. Counting raw note objects across all
        # voices while the exemplar shows only the split top line meant the
        # density target in a brief and the exemplar printed beneath it were
        # measuring different things — and the brief's "median events/bar" is
        # what the density gate then checked the agent's phrase against.
        def _attacks(*recs):
            return sum(1 for rs in recs for r in rs if r.get("type") != "rest")

        rh_density = _attacks(rh_display, rh_inner_display)
        lh_density = _attacks(lh_display, lh_inner_display)

        # Phrase position is filled in by _phrase_positions once every bar's
        # melody line and harmonic function are known (it needs the whole list).
        position = "middle"

        bar_data = {
            "source": source_name,
            "bar_num": bar_num,
            "time_sig": time_sig,
            "key": key_name,
            "key_mode": key_mode,
            "phrase_position": position,
            "melody_density": rh_density,
            "accomp_density": lh_density,
            "rh_texture": rh_texture,
            "lh_texture": lh_texture,
            "melody_direction": direction,
            "has_grace_notes": has_grace,
            # Written-out ornaments on this bar's upper staff (tr / mord / turn).
            "ornaments": bar_ornaments,
            "has_dotted_rhythms": has_dotted,
            "has_rests": has_rests,
            "register_center": round(register),
            "harmony_quality": harm.get("chord_quality") or key_mode,
            "rh_display": rh_display,
            "rh_inner_display": rh_inner_display,  # inner RH voice(s), for // polyphony in briefs
            "rh_events": rh_events,
            "lh_display": lh_display,
            "lh_inner_display": lh_inner_display,  # inner LH voice(s)
            "lh_events": lh_events,
            # a truncated record is only PART of a bar — briefs must not present
            # it as a complete bar to adapt
            "truncated": truncated,
            # P1 additive: real top-voice melody (correct register) + harmony
            "melody_part_index": mel_idx,
            "melody_line": melody_line,
            "melody_register": melody_register,
            "roman": harm.get("roman"),
            "function": harm.get("function"),
            "chord_root": harm.get("chord_root"),
            "chord_root_interval": harm.get("chord_root_interval"),
            "chord_quality": harm.get("chord_quality"),
            # Where the harmony moves WITHIN the bar (see _harmony_events).
            "harmony_events": harm.get("harmony_events") or [],
        }
        bars.append(bar_data)

    # Phrase position needs the whole bar list (melody rest + harmonic arrival),
    # so it is a post-pass rather than a per-bar guess.
    _phrase_positions(bars)
    return bars


def _texture_shape(notes, time_sig):
    """Shared measurements behind both texture classifiers.

    Returns (attacks_per_beat, chord_ratio, span, stepwise_ratio, shape).
    ``attacks`` counts note/chord ONSETS (a chord is one attack) and is divided
    by the bar's real beat count, so the same figure in 3/8 and 4/4 classifies
    the same way.

    Notes are read in ONSET order. ``measure.recurse().notes`` returns document
    order, which for any two-voice staff interleaves the voices — so the melodic
    interval sequence that decides "stepwise" and "alberti" was being computed
    over a scrambled line.
    """
    bar_len = time_sig[0] * 4.0 / time_sig[1] if time_sig else 4.0
    attacks = len(notes)
    if not attacks or bar_len <= 0:
        return 0.0, 0.0, 0, 0.0, ""
    chords = sum(1 for n in notes if getattr(n, "isChord", False))
    ordered = sorted(notes, key=lambda n: (_frac(getattr(n, "offset", 0)), -_top_of(n)))
    tops, lows = [], []
    for n in ordered:
        try:
            tops.append(max(p.midi for p in n.pitches))
            lows.append(min(p.midi for p in n.pitches))
        except (ValueError, AttributeError):
            continue
    span = (max(tops) - min(tops)) if len(tops) >= 2 else 0
    steps = [abs(b - a) for a, b in zip(tops, tops[1:])]
    stepwise = (sum(1 for d in steps if d <= 2) / len(steps)) if steps else 0.0
    return attacks / bar_len, (chords / attacks), span, stepwise, _figure_shape(tops)


def _top_of(n):
    try:
        return max(p.midi for p in n.pitches)
    except (ValueError, AttributeError):
        return 0


def _figure_shape(tops):
    """Name the SHAPE of a single-line accompaniment figure.

    "" (none) | "alberti" | "octave" | "arpeggio_up" | "arpeggio_down" | "repeat"

    The old test asked only whether every odd-index note sat above every
    even-index note with the even notes within a whole tone of each other. A real
    Alberti bass (C-G-E-G) fails it — its even notes are a third apart — while a
    plain octave oscillation (F2-F3-F2-F3) passes, so every corpus octave bass
    was filed as "alberti" and the Alberti exemplars the brief offered were
    octave leaps.
    """
    if len(tops) < 4:
        return ""
    distinct = sorted(set(tops))
    if len(distinct) == 1:
        return "repeat"
    if len(distinct) == 2 and distinct[1] - distinct[0] == 12 and tops[0] == distinct[0]:
        if all(t == distinct[i % 2] for i, t in enumerate(tops)):
            return "octave"
    # Alberti: a 4-cycle low-high-middle-high, the low note on the beat.
    if len(tops) >= 4 and len(tops) % 2 == 0:
        cyc = tops[:4]
        if (
            cyc[1] == cyc[3]
            and cyc[0] < cyc[2] < cyc[1]
            and all(tops[i] == cyc[i % 4] for i in range(len(tops)))
        ):
            return "alberti"
        # …and the loose form: lowest note on every 4th attack, upper notes above.
        if (
            all(tops[i] == min(tops[i : i + 4]) for i in range(0, len(tops) - 3, 4))
            and cyc[1] == cyc[3]
        ):
            return "alberti"
    diffs = [b - a for a, b in zip(tops, tops[1:])]
    if all(d > 0 for d in diffs):
        return "arpeggio_up"
    if all(d < 0 for d in diffs):
        return "arpeggio_down"
    return ""


def _classify_rh_texture(notes, time_sig):
    """Upper-staff texture label from the bar's density, chord content and shape."""
    per_beat, chord_ratio, span, stepwise, _shape = _texture_shape(notes, time_sig)
    if per_beat == 0:
        return "silence"
    if chord_ratio >= 0.5:
        # Both are TextureType values. "block_chord_sparse" is an ACCOMPANIMENT
        # label and must not be used for the melody staff — it made the RH and LH
        # density statistics share a key that means different things.
        return "chordal"
    if per_beat <= 0.5:
        return "held_note"
    if per_beat <= 2.0:
        return "singing_melody"
    return "scalar_run" if stepwise >= 0.6 else "zigzag_figuration"


def _classify_lh_texture(notes, time_sig):
    """Accompaniment texture label. Distinguishes the idioms that actually differ
    (pedal, block chords, Alberti, broken-chord waves, walking bass) instead of
    slicing one note count into arbitrary bands."""
    per_beat, chord_ratio, span, stepwise, shape = _texture_shape(notes, time_sig)
    if per_beat == 0:
        return "silence"
    if chord_ratio >= 0.5:
        return "block_chord_sparse" if per_beat <= 1.0 else "block_chord_offbeat"
    if per_beat <= 0.5:
        return "pedal_point"
    if shape == "repeat":
        return "pedal_point" if per_beat <= 1.0 else "block_chord_tremolo"
    if shape == "octave":
        # An octave oscillation is its own idiom, and calling it Alberti taught
        # the composer to write leaping octaves whenever a brief asked for one.
        return "interlocking"
    if per_beat >= 1.5:
        if shape == "alberti":
            return "alberti"
        if shape == "arpeggio_up":
            return "broken_chord_asc"
        if shape == "arpeggio_down":
            return "broken_chord_desc"
        if span > 12:
            return "broken_chord_wave"
        return "walking_bass" if stepwise >= 0.5 else "alberti"
    return "walking_bass" if stepwise >= 0.5 else "bass_melody"


def _key_obj(name, mode):
    """music21 Key for a (name, mode) pair, cached; None if unparseable."""
    cache = _key_obj.__dict__.setdefault("_cache", {})
    hit = cache.get((name, mode))
    if hit is not None or (name, mode) in cache:
        return hit
    try:
        from music21 import key as m21key

        obj = m21key.Key(name, mode)
    except Exception:
        obj = None
    cache[(name, mode)] = obj
    return obj


def _extra_part_voices(parts, measure_index):
    """(offset, element) pairs for one measure of each additional part.

    Used to fold the inner parts of a multi-staff score (a chorale's alto and
    tenor) into the staff they sit closest to, instead of dropping them.
    """
    from music21 import stream

    out = []
    for part in parts:
        measures = list(part.getElementsByClass(stream.Measure))
        if measure_index >= len(measures):
            continue
        for el in measures[measure_index].recurse().notesAndRests:
            if el.isRest:
                continue
            try:
                out.append((float(el.offset), el))
            except (TypeError, ValueError):
                continue
    return sorted(out, key=lambda x: x[0])


def _mean_top_midi(part) -> float:
    tops = []
    for n in part.recurse().notes:
        try:
            tops.append(max(x.midi for x in n.pitches))
        except (ValueError, AttributeError):
            continue
    return sum(tops) / len(tops) if tops else 0.0


def _write_bar_index(composer, all_bars, shard_size=2000):
    """Write bar records to reference_index/<composer>/ as sharded lists."""
    cdir = REF_INDEX / composer
    cdir.mkdir(parents=True, exist_ok=True)
    for old in cdir.glob("bars_*.json"):
        old.unlink()
    n_shards = max(1, (len(all_bars) + shard_size - 1) // shard_size)
    for i in range(n_shards):
        shard = all_bars[i * shard_size : (i + 1) * shard_size]
        (cdir / f"bars_{i:02d}.json").write_text(json.dumps(shard, separators=(",", ":")))
    (cdir / "bar_index.json").write_text(
        json.dumps(
            {"composer": composer, "total_bars": len(all_bars), "schema": 3},
            separators=(",", ":"),
        )
    )
    return n_shards


# Composers whose corpus comes from music21's built-in collection.
_M21_COMPOSERS = ("bach", "haydn", "palestrina", "monteverdi")


def process_music21_corpus(composers=None, max_files=None):
    """Extract bars from music21 built-in corpus files."""
    from music21 import converter, corpus

    composers_to_process = list(composers or _M21_COMPOSERS)

    results = {}

    for composer in composers_to_process:
        print(f"\n=== Processing {composer} (music21 corpus) ===")
        try:
            paths = corpus.getComposer(composer)
        except Exception:
            print(f"  No corpus data for {composer}")
            continue

        all_bars = []
        processed = 0
        errors = 0

        for path in paths:
            if max_files and processed >= max_files:
                break
            path_str = str(path)
            # Skip non-score files
            if not (
                path_str.endswith(".mxl") or path_str.endswith(".xml") or path_str.endswith(".krn")
            ):
                continue

            try:
                score = converter.parse(path_str)
                source_name = (
                    os.path.basename(os.path.dirname(path_str))
                    + "/"
                    + os.path.basename(path_str).replace(".mxl", "").replace(".krn", "")
                )
                bars = analyze_score_bars(score, composer, source_name)
                all_bars.extend(bars)
                processed += 1
                if processed % 20 == 0:
                    print(f"  Processed {processed} files, {len(all_bars)} bars...")
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  Error parsing {os.path.basename(path_str)}: {e}")

        if all_bars:
            # Write to reference_index/<composer>/ — the layout every loader
            # actually reads. Writing a flat "<composer>_bar_index.json" put the
            # music21-sourced corpora somewhere nothing looks for them.
            _write_bar_index(composer, all_bars)
            print(f"  Saved {len(all_bars)} bars from {processed} files, {errors} errors")
            results[composer] = len(all_bars)
        else:
            print(f"  No bars extracted for {composer}")

    return results


# Flagship kern/mxl sources under reference_scores/ → composer id. These are the
# 224 hand-curated piano scores; re-extracting them through analyze_score_bars
# regenerates their shards WITH the P1 melody_line + harmony fields.
_REFERENCE_SCORE_DIRS = {
    "mozart": "mozart-piano-sonatas",
    "beethoven": "beethoven-piano-sonatas",
    "chopin": "chopin-mazurkas",
}


def process_reference_scores(composers=None, shard_size=2000):
    """Re-extract flagship kern/mxl sources into sharded bar indexes (bars_NN.json
    lists, the format the loaders expect), regenerating melody_line + harmony."""
    import glob

    from music21 import converter

    base = BASE / "reference_scores"
    targets = composers or list(_REFERENCE_SCORE_DIRS)
    results = {}
    for composer in targets:
        d = _REFERENCE_SCORE_DIRS.get(composer)
        if not d:
            print(f"  no reference_scores dir for {composer}")
            continue
        files = []
        for ext in ("krn", "xml", "mxl", "musicxml"):
            files += glob.glob(str(base / d / "**" / f"*.{ext}"), recursive=True)
        files = sorted(set(files))
        print(f"=== {composer}: {len(files)} source files ===")
        all_bars, ok, bad = [], 0, 0
        for fp in files:
            try:
                score = converter.parse(fp)
                src = os.path.splitext(os.path.basename(fp))[0]
                all_bars.extend(analyze_score_bars(score, composer, src))
                ok += 1
                if ok % 20 == 0:
                    print(f"  {ok} files, {len(all_bars)} bars...")
            except Exception as e:
                bad += 1
                if bad <= 3:
                    print(f"  skip {os.path.basename(fp)}: {e}")
        if not all_bars:
            print(f"  no bars extracted for {composer}")
            continue
        n_shards = _write_bar_index(composer, all_bars, shard_size)
        print(f"  wrote {len(all_bars)} bars in {n_shards} shards ({ok} files, {bad} errors)")
        results[composer] = len(all_bars)
    return results


def process_local_scores(composer, directory, max_files=None):
    """Extract bars from a directory of already-downloaded scores (MIDI/MusicXML).

    Web-acquired composers keep their fetched sources under
    reference_scores/_fetch_<composer>/, so their bar records can be rebuilt
    offline when the extractor changes.
    """
    import glob

    from music21 import converter

    files = []
    for ext in ("mid", "midi", "krn", "xml", "mxl", "musicxml"):
        files += glob.glob(os.path.join(str(directory), "**", f"*.{ext}"), recursive=True)
    files = sorted(set(files))
    print(f"=== {composer}: {len(files)} local files in {directory} ===")
    all_bars, ok, bad = [], 0, 0
    for fp in files:
        if max_files and ok >= max_files:
            break
        try:
            score = converter.parse(fp)
            all_bars.extend(
                analyze_score_bars(score, composer, os.path.basename(fp).rsplit(".", 1)[0])
            )
            ok += 1
        except Exception as exc:
            bad += 1
            if bad <= 3:
                print(f"  skip {os.path.basename(fp)}: {exc}")
    if all_bars:
        n = _write_bar_index(composer, all_bars)
        print(f"  wrote {len(all_bars)} bars in {n} shards ({ok} files, {bad} errors)")
    return {composer: len(all_bars)} if all_bars else {}


def main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description="Build/regenerate corpus bar indexes")
    ap.add_argument(
        "--reference",
        nargs="*",
        metavar="COMPOSER",
        help="re-extract flagship reference_scores kern (default: all of "
        + ", ".join(_REFERENCE_SCORE_DIRS),
    )
    ap.add_argument(
        "--music21",
        nargs="*",
        metavar="COMPOSER",
        help="also process the music21 built-in corpus (default: "
        + ", ".join(_M21_COMPOSERS)
        + ")",
    )
    ap.add_argument(
        "--local",
        nargs=2,
        metavar=("COMPOSER", "DIR"),
        action="append",
        help="extract a composer from a local directory of scores (repeatable)",
    )
    args = ap.parse_args(argv)

    t0 = time.time()
    print("=== Building Full Corpus ===\n")
    results = {}
    if args.reference is not None:
        results.update(process_reference_scores(args.reference or None))
    for composer, directory in args.local or []:
        results.update(process_local_scores(composer, directory))
    if args.music21 is not None or (args.reference is None and not args.local):
        results.update(process_music21_corpus(args.music21 or None))

    print(f"\n=== COMPLETE ({time.time() - t0:.0f}s) ===")
    for composer, count in results.items():
        print(f"  {composer}: {count} bars")


if __name__ == "__main__":
    main()
