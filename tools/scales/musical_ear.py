"""The "musical ear" — bar/beat-level defect detectors that give the actor-critic
loop a feedback signal for the failures users actually report but the old metrics
could not see: vertical clashes, a buried melody, unresolved non-chord tones,
lack of breathing, and monotony / absent development.

Inputs: the assembled MusicXML path (for accurate vertical simultaneity via
music21 chordify) + the generated bar records (cheap symbolic checks). Output: a
flat list of EarFinding dicts the music-critic folds into bar-targeted revisions
and `_section_gate` promotes (clash / buried-melody) to hard fails.

Honest scope: this catches structural/harmonic/voicing defects. Timbre and true
perceived "aliveness" are NOT symbolically detectable and stay the fresh-ears
critic's call (see `undetectable`).
"""

from __future__ import annotations

from typing import Any, Dict, List

# Diatonic scale-degree sets (semitones above tonic) for the in-key check.
# Minor covers natural, harmonic AND melodic: the raised leading tone is what
# makes a minor-key dominant a dominant, and the raised sixth is ordinary
# melodic-minor writing. Listing only the natural minor meant every V-i cadence
# in every minor-key piece had its leading tone flagged as a chromatic wrong
# note.
_MAJOR = frozenset({0, 2, 4, 5, 7, 9, 11})
_MINOR = frozenset({0, 2, 3, 5, 7, 8, 9, 10, 11})

_UNDETECTABLE = [
    "timbre / tone colour",
    "true performed expressivity (whether rubato is tasteful)",
    "memorability / emotional impact (the fresh-ears critic's call)",
]


def _finding(detector, bar, beat, severity, problem, fix_hint, **evidence) -> Dict[str, Any]:
    return {
        "detector": detector,
        "bar": bar,
        "beat": beat,
        "severity": severity,
        "problem": problem,
        "fix_hint": fix_hint,
        "evidence": evidence,
    }


# ─── Score-based detectors (need real simultaneity) ──────────────────────────


def detect_vertical_clashes(score, cap: int = 8) -> List[Dict[str, Any]]:
    """Flag simultaneously-sounding pitches that clash: a cross-relation (G♮+G♭ —
    same letter, different accidental) is an error; a bare half-step cluster is a
    warning (it may be an appoggiatura). Uses chordify so both hands are merged
    into the literal sounding sonority."""
    out: List[Dict[str, Any]] = []
    try:
        chordy = score.chordify()
    except Exception:
        return out
    # A grace note is played BEFORE the beat, not on it — but chordify merges it
    # into an ordinary chord at its principal's offset and drops the grace flag,
    # so an ordinary appoggiatura-from-below (E5 grace into F5) registered as a
    # minor-2nd clash on every statement of a theme that opens with one. Collect
    # the grace pitches from the source score and exclude them by position.
    grace_at: Dict[Any, set] = {}
    try:
        for n in score.recurse().notes:
            if getattr(n.duration, "isGrace", False):
                key = (n.measureNumber, round(float(n.offset), 4))
                grace_at.setdefault(key, set()).update(p.nameWithOctave for p in n.pitches)
    except Exception:
        grace_at = {}

    for ch in chordy.recurse().getElementsByClass("Chord"):
        graces = grace_at.get((ch.measureNumber, round(float(ch.offset), 4)), set())
        ps = (
            [p for p in ch.pitches if p.nameWithOctave not in graces]
            if graces
            else list(ch.pitches)
        )
        if len(ps) < 2:
            continue
        bar = ch.measureNumber
        try:
            beat = round(float(ch.beat), 2)
            if beat != beat:  # nan guard (no time signature in fragment)
                beat = None
        except (TypeError, ValueError):
            beat = None
        # cross-relation: same step letter, different pitch class
        by_step: Dict[str, set] = {}
        for p in ps:
            by_step.setdefault(p.step, set()).add(p.pitchClass)
        cross = [s for s, pcs in by_step.items() if len(pcs) > 1]
        if cross:
            names = ", ".join(sorted({p.nameWithOctave for p in ps if p.step in cross}))
            # Stays a WARNING even for a close cross-relation. Falsified against
            # the reference corpus: three Beethoven sonatas, three Mozart sonatas
            # and three Chopin mazurkas produce 45 same-octave cross-relations
            # between them (diminished-seventh resolutions, chromatic passing
            # tones). Promoting this to an error would reject real music, which
            # is the standing test every rule here has to pass.
            out.append(
                _finding(
                    "vertical_clash",
                    bar,
                    beat,
                    "warn",
                    f"Bar {bar} beat {beat}: cross-relation — {names} sound together "
                    f"(same letter, conflicting accidental). Often idiomatic (a false "
                    f"relation or passing tone, as in Bach/Beethoven) — judge by ear.",
                    "If it grates, spell both the same or move one to a chord tone.",
                    pitches=[p.nameWithOctave for p in ps],
                )
            )
            if len(out) >= cap:
                break
            continue
        # half-step cluster among simultaneously sounding pitches (softer)
        midis = sorted(p.midi for p in ps)
        clash_pair = next(((a, b) for a, b in zip(midis, midis[1:]) if (b - a) == 1), None)
        if clash_pair:
            a, b = clash_pair
            import music21

            out.append(
                _finding(
                    "vertical_clash",
                    bar,
                    beat,
                    "warn",
                    f"Bar {bar} beat {beat}: minor-2nd clash "
                    f"{music21.pitch.Pitch(midi=a).nameWithOctave}/"
                    f"{music21.pitch.Pitch(midi=b).nameWithOctave} — fine only if it's a "
                    f"prepared/resolving appoggiatura.",
                    "Ensure the dissonant tone resolves by step, or remove it.",
                    midis=[a, b],
                )
            )
            if len(out) >= cap:
                break
    return out


def detect_bar_length_errors(score, cap: int = 12) -> List[Dict[str, Any]]:
    """Bars whose engraved length does not match their time signature.

    This is the one class of defect that is unambiguously an ERROR: a 4/4 bar
    holding 7.5 beats is not an artistic choice, it is a corrupt score, and it
    is exactly what several notation bugs in this system have produced (voice
    overlap serialized without a backup, a sequentially-parsed pedal figure
    overflowing, an exemplar copied a beat long). Every one of those shipped
    silently because nothing ever read the assembled file back and checked it.

    The length is measured as the largest `offset + duration` reached — how far
    into the bar the last sounding thing extends. That is written out explicitly
    rather than taken from `measure.duration.quarterLength`, which happens to be
    the same number (`Stream.duration` is `highestTime`) but only for as long as
    that stays true of a `Measure`; the property this detector needs is "does
    anything still sound past the barline", and overlapping voices must not be
    double-counted.

    **A known false positive, recorded honestly.** Run over the reference
    corpus, this fires an `error` on bar 43 of Mozart's K.281 third movement:
    music21's Humdrum importer lays that bar out with offsets running 0 to 16
    inside a 2/2 measure. The music is fine; the *parse* is not, and no
    measurement of the parsed stream can tell the difference between "the
    importer merged some bars" and "our exporter overflowed one". Since this is
    the only detector family whose findings block a section, that limit is worth
    stating: it is trustworthy on the MusicXML this system writes (where it
    catches the 7.5-beats-in-4/4 shape several notation bugs have produced), and
    it should not be pointed at freshly-imported Humdrum without checking.
    `test_score_realism_calibration` tolerates exactly this one file.
    """

    def _sounding_extent(measure) -> float:
        """How far into the bar the last sounding thing reaches."""
        end = 0.0
        for el in measure.recurse().notesAndRests:
            try:
                end = max(end, float(el.offset) + float(el.duration.quarterLength))
            except (TypeError, ValueError):
                continue
        return end

    out: List[Dict[str, Any]] = []
    for part in score.parts:
        for m in part.getElementsByClass("Measure"):
            ts = m.timeSignature or m.getContextByClass("TimeSignature")
            if ts is None:
                continue
            expected = float(ts.barDuration.quarterLength)
            actual = _sounding_extent(m)
            if actual <= 0:
                continue  # an empty measure says nothing about the meter
            # The first bar may legitimately be a pickup (a partial measure).
            if m.number in (0, 1) and actual < expected:
                continue
            if actual > expected + 0.01:
                # OVERFULL is an error: unengravable, and the signature of every
                # notation bug this system has shipped.
                out.append(
                    _finding(
                        "bar_length",
                        m.number,
                        None,
                        "error",
                        f"Bar {m.number} ({part.partName or 'part'}) holds "
                        f"{actual:g} beats but the meter is {ts.ratioString} "
                        f"({expected:g} beats).",
                        "Make every voice in the bar sum to the meter. A sustained "
                        "bass under figuration is a second voice, not a longer first note.",
                        expected=expected,
                        actual=actual,
                    )
                )
                if len(out) >= cap:
                    return out
            elif actual < expected - 0.01:
                # UNDERFULL is only a warning. Falsified against the reference
                # corpus: real engraved scores are full of short bars (second
                # endings, repeat structures, written-out partial measures) —
                # 22 of them across nine sonatas and mazurkas.
                out.append(
                    _finding(
                        "bar_length",
                        m.number,
                        None,
                        "warn",
                        f"Bar {m.number} ({part.partName or 'part'}) holds "
                        f"{actual:g} of the meter's {expected:g} beats — fine for a "
                        f"pickup or a written-out partial bar, otherwise content is missing.",
                        "Fill the bar or write the remaining silence as a rest.",
                        expected=expected,
                        actual=actual,
                    )
                )
                if len(out) >= cap:
                    return out
    return out


def detect_out_of_range(score, low: int = 21, high: int = 108, cap: int = 8):
    """Notes outside the instrument's playable range — a physical impossibility."""
    out: List[Dict[str, Any]] = []
    for n in score.recurse().notes:
        for p in n.pitches:
            if p.midi < low or p.midi > high:
                out.append(
                    _finding(
                        "out_of_range",
                        n.measureNumber,
                        None,
                        "error",
                        f"Bar {n.measureNumber}: {p.nameWithOctave} (MIDI {p.midi}) is "
                        f"outside the playable range [{low}, {high}].",
                        "Move the note into range, or transpose the passage by an octave.",
                        pitch=p.nameWithOctave,
                    )
                )
                if len(out) >= cap:
                    return out
    return out


def detect_melody_buried(score, cap: int = 8) -> List[Dict[str, Any]]:
    """Per bar, is the melody (top of the highest-register part) actually the
    highest sounding pitch, or is an accompaniment voice sitting above it?"""
    out: List[Dict[str, Any]] = []
    parts = list(score.parts)
    if len(parts) < 2:
        return out

    # Melody = the TREBLE-clef part (the upper staff carries the tune by
    # convention); register can't decide it, since a buried melody is exactly the
    # case where accompaniment rises above the tune. Fall back to parts[0].
    def has_treble(p):
        return any("Treble" in type(c).__name__ for c in p.recurse().getElementsByClass("Clef"))

    mel_part = next((p for p in parts if has_treble(p)), parts[0])
    others = [p for p in parts if p is not mel_part]
    mel_measures = list(mel_part.getElementsByClass("Measure"))
    for m in mel_measures:
        bar = m.number
        mel_notes = [n for n in m.recurse().notes if n.pitches]
        if not mel_notes:
            continue
        buried_beats = 0
        for n in mel_notes:
            mel_top = max(n.pitches).midi
            off = float(n.offset)
            acc_max = -1
            for op in others:
                om = next((x for x in op.getElementsByClass("Measure") if x.number == bar), None)
                if om is None:
                    continue
                for an in om.recurse().notes:
                    if float(an.offset) <= off < float(an.offset) + float(an.quarterLength):
                        acc_max = max(acc_max, max(an.pitches).midi)
            if acc_max - mel_top >= 3:  # accompaniment ≥ m3 above the tune
                buried_beats += 1
        # Only flag a bar where the tune is buried for MOST of the bar — and even
        # then it is advisory: voices legitimately cross in real counterpoint
        # (Bach, Beethoven), so this is a hint for the ear, never a hard defect.
        if buried_beats and buried_beats >= max(2, len(mel_notes) * 0.6):
            out.append(
                _finding(
                    "melody_buried",
                    bar,
                    None,
                    "warn",
                    f"Bar {bar}: the melody may be buried — another voice sounds above it on "
                    f"{buried_beats}/{len(mel_notes)} notes (fine if voices are meant to cross).",
                    "If the tune should lead, voice the accompaniment below it or thin the "
                    "inner voices on the melodic beats.",
                    buried=buried_beats,
                    total=len(mel_notes),
                )
            )
            if len(out) >= cap:
                break
    return out


# ─── Bar-record detectors (cheap symbolic) ───────────────────────────────────


def _scale(bar) -> frozenset:
    return _MINOR if bar.get("key_mode") == "minor" else _MAJOR


def detect_unresolved_nct(bars: List[Dict[str, Any]], cap: int = 8) -> List[Dict[str, Any]]:
    """Melody notes outside the key AND outside the bar's harmony, approached AND
    left by leap, inside an otherwise stepwise line — these read as wrong notes.

    Falsified against the rebuilt corpus (73 real movements across seven
    composers): fires on **6 of 73 = 8%**, down from 83%. The three conditions were each added
    because the version without it flagged canonical music:

    * key only, no chord check -> 20/24 Mozart+Beethoven movements, every case a
      secondary dominant's leading tone (F#5 in C major, B-4 in G major);
    * headline chord only, not the bar's other harmonies -> still 17/24, because
      a bar's ``roman`` is only what it sits on at the downbeat;
    * no texture guard -> broken-chord and broken-octave figures, where every
      note is leapt to by construction and "leapt to and from" describes the
      texture rather than a mistake.
    """
    out: List[Dict[str, Any]] = []
    for bar in bars:
        line = [e for e in (bar.get("melody_line") or []) if e.get("type") == "note"]
        if len(line) < 3:
            continue
        scale = _scale(bar)  # in-key pcs relative to tonic
        tonic = _tonic_pc(bar)
        # A chromatic note that BELONGS TO THE BAR'S CHORD is not a wrong note,
        # however it is approached. Falsified against the rebuilt corpus: without
        # this the detector fired on 10 of 12 real Mozart movements and 10 of 12
        # Beethoven, and every case inspected was a secondary dominant's leading
        # tone inside an arpeggiated figure — F#5 in C major, B-4 in G major —
        # which is the commonest chromatic note in the repertoire, not a mistake.
        chord = _chord_pcs(bar)
        mids = [e.get("midi") for e in line if e.get("midi") is not None]
        # In a broken-chord or alternating-register figure, "approached and left
        # by leap" describes the TEXTURE, not a mistake — every note in it is
        # leapt to. Falsified against the rebuilt corpus: the remaining false
        # positives were all bars like Beethoven Op.2/1/iv b22 (a C minor
        # arpeggio with a passing F#) and Op.2/2/iv b73 (a chromatic scale in
        # broken octaves). A wrong note is only legible as one inside a line that
        # is otherwise stepwise.
        # A bar needs enough motion to HAVE a texture: with two intervals, "all
        # leaps" says nothing about the idiom, and a lone chromatic leap in a
        # sparse bar is exactly the case worth flagging.
        steps = [abs(b - a) for a, b in zip(mids, mids[1:])]
        if len(steps) >= 4 and sum(1 for d in steps if d > 2) / len(steps) > 0.5:
            continue
        for i in range(1, len(mids) - 1):
            # High precision: only a truly CHROMATIC (out-of-key, out-of-chord)
            # note, leapt to AND from, is a likely wrong note. Diatonic passing
            # tones are fine.
            if ((mids[i] - tonic) % 12) in scale:
                continue
            if chord and (mids[i] % 12) in chord:
                continue
            approach = abs(mids[i] - mids[i - 1])
            leave = abs(mids[i + 1] - mids[i])
            if approach > 2 and leave > 2:
                # Name the note the way the KEY writes it. music21 defaults to
                # sharps, so a flagged A-flat was reported as "G#5" — a message
                # naming a different note than the one on the page.
                from .pitch import midi_to_pitch

                out.append(
                    _finding(
                        "unresolved_nct",
                        bar.get("bar_num"),
                        None,
                        "warn",
                        f"Bar {bar.get('bar_num')}: {midi_to_pitch(mids[i], bar.get('key') or 'C')} "
                        f"is chromatic (outside {bar.get('key')} {bar.get('key_mode')}) and is both "
                        f"approached and left by leap — reads as a wrong note.",
                        "Resolve it by step into a chord/scale tone, or remove the leap into it.",
                        key=bar.get("key"),
                    )
                )
                if len(out) >= cap:
                    return out
    return out


def _tonic_pc(bar: Dict[str, Any]) -> int:
    """Tonic pitch class of a bar's key, in any spelling this project writes.

    ``music21.pitch.Pitch("F major")`` raises, and the bare ``except`` returned
    0 — so every non-chord-tone check on a piece whose slots spell the key
    "F major" (which is how the planner writes it) was measured against C.
    """
    from .pitch import key_to_root_midi

    return key_to_root_midi(bar.get("key") or "C") % 12


def detect_no_breathing(bars: List[Dict[str, Any]], cap: int = 6) -> List[Dict[str, Any]]:
    """Phrase-end bars with no rest/long note; flat-density spans (no swell)."""
    out: List[Dict[str, Any]] = []
    for bar in bars:
        if bar.get("phrase_position") in ("cadential", "closing"):
            line = bar.get("melody_line") or []
            # "Long" is relative to the BAR, not a fixed two quarter notes. In 3/4
            # a note filling half the bar is a phrase coming to rest, and in 2/4
            # nothing shorter than the whole bar could ever qualify — so the
            # detector fired on cadences that plainly do breathe.
            ts = bar.get("time_sig") or [4, 4]
            try:
                bar_len = float(ts[0]) * 4.0 / float(ts[1])
            except (TypeError, ValueError, ZeroDivisionError):
                bar_len = 4.0
            long_enough = max(1.0, bar_len / 2.0)
            has_rest = any(e.get("type") == "rest" and e.get("dur", 0) >= 0.5 for e in line)
            has_long = any(e.get("type") == "note" and e.get("dur", 0) >= long_enough for e in line)
            if line and not (has_rest or has_long):
                out.append(
                    _finding(
                        "no_breathing",
                        bar.get("bar_num"),
                        None,
                        "warn",
                        f"Bar {bar.get('bar_num')}: phrase ends with no rest or long note — "
                        f"the line never breathes.",
                        "End the phrase with a quarter-or-longer note or a rest before the next.",
                    )
                )
                if len(out) >= cap:
                    return out
    # flat density over the whole span
    totals = [int(b.get("melody_density", 0)) + int(b.get("accomp_density", 0)) for b in bars]
    if len(totals) >= 8:
        mean = sum(totals) / len(totals)
        if mean > 0:
            import statistics

            cv = statistics.pstdev(totals) / mean
            if cv < 0.12:
                out.append(
                    _finding(
                        "no_breathing",
                        bars[0].get("bar_num"),
                        None,
                        "warn",
                        f"Bars {bars[0].get('bar_num')}–{bars[-1].get('bar_num')}: density is flat "
                        f"(cv={cv:.2f}) — no swell or release across the span.",
                        "Vary note density to shape a swell toward the peak and recede at cadences.",
                        density_cv=round(cv, 3),
                    )
                )
    return out


def detect_monotony(bars: List[Dict[str, Any]], cap: int = 6) -> List[Dict[str, Any]]:
    """Runs of near-identical consecutive bars (mechanical repetition).

    The signature is rhythm AND pitch contour. Keying on rhythm alone got the
    problem backwards: a repeated rhythm is idiomatic (that is what an
    accompaniment figure IS), while the actual machine tell — the same PITCHES
    stamped out bar after bar — went undetected because its rhythm varied.
    """
    out: List[Dict[str, Any]] = []

    def sig(b):
        rhythm = tuple(
            (e.get("type"), round(float(e.get("dur", 0)), 2)) for e in (b.get("rh_display") or [])
        )
        line = [e.get("midi") for e in (b.get("melody_line") or []) if e.get("midi") is not None]
        # Contour is transposition-invariant, so a sequence does not read as a
        # photocopy but a literally repeated bar does.
        contour = tuple(b - a for a, b in zip(line, line[1:]))
        return (rhythm, contour)

    run_start, run_len, prev = None, 1, None

    def flush(rs, rl):
        if rl >= 4 and rs is not None:  # four identical bars running
            out.append(
                _finding(
                    "monotony",
                    rs,
                    None,
                    "warn",
                    f"Bars {rs}–{rs + rl - 1}: the RH rhythmic pattern is identical for "
                    f"{rl} bars — mechanical.",
                    "Vary the figuration, ornament, or rhythm; develop the material.",
                    run=rl,
                )
            )

    for b in bars:
        s = sig(b)
        if prev is not None and s == prev and len(s[0]) > 2:
            if run_start is None:
                run_start = b.get("bar_num", 0) - 1
            run_len += 1
        else:
            flush(run_start, run_len)
            if len(out) >= cap:
                return out
            run_start, run_len = None, 1
        prev = s
    flush(run_start, run_len)  # final run
    return out


def _chord_pcs(bar) -> frozenset:
    """Pitch classes of EVERY harmony the bar moves through. Empty if unknown.

    Not just the headline chord. A bar's ``roman`` is what it sits on at the
    downbeat, and most bars in this corpus move through more than one harmony —
    so checking a chromatic note against the headline alone still called the
    third of a passing V/V a wrong note, because the bar's *first* chord was V.
    Falsified against the rebuilt corpus: headline-only fired on 9 of 12 real
    Mozart movements.
    """
    key = bar.get("key")
    romans = [bar.get("roman")] + [
        e.get("roman") for e in (bar.get("harmony_events") or []) if e.get("roman")
    ]
    romans = [r for r in dict.fromkeys(romans) if r]
    if not romans or not key:
        return frozenset()
    cache = _chord_pcs.__dict__.setdefault("_cache", {})
    ckey = (tuple(romans), key, bar.get("key_mode"))
    hit = cache.get(ckey)
    if hit is not None:
        return hit
    # Read through the project's own Roman parser, not music21's. The corpus
    # spells applied dominants ("V7/V"), major sevenths ("Imaj7") and figured
    # inversions ("vo65"); music21 raises on several of those, the bare except
    # returned an empty set, and the detector then silently did nothing.
    from .harmony_analysis import roman_pitches
    from .pitch import key_to_root_midi

    mode = bar.get("key_mode") or "major"
    tonic = key_to_root_midi(key) % 12
    pcs = frozenset(pc for r in romans for pc in roman_pitches(r, tonic, mode))
    cache[ckey] = pcs
    return pcs


def detect_arpeggiated_melody(bars: List[Dict[str, Any]], cap: int = 4):
    """Spans where the "melody" is outlining the harmony rather than singing.

    The craft guidance says it outright — "C-E-G-C is a chord, not a tune" — and
    nothing measured it. A tune earns its status through non-chord tones on
    strong beats (appoggiaturas, suspensions, passing motion); a line made almost
    entirely of chord tones reached by leap is accompaniment written on the top
    staff, which is one of the most recognisable ways generated music fails.

    Needs at least four consecutive bars, so an arpeggiated gesture or a fanfare
    is not mistaken for a texture.
    """
    out: List[Dict[str, Any]] = []
    run_start, run_len = None, 0

    def _bar_is_arpeggiated(bar) -> bool:
        pcs = _chord_pcs(bar)
        if not pcs:
            return False
        mids = [e.get("midi") for e in (bar.get("melody_line") or []) if e.get("midi") is not None]
        if len(mids) < 3:
            return False
        chord_tones = sum(1 for m in mids if m % 12 in pcs)
        steps = [abs(b - a) for a, b in zip(mids, mids[1:])]
        stepwise = sum(1 for d in steps if 0 < d <= 2) / len(steps) if steps else 0.0
        return chord_tones / len(mids) >= 0.9 and stepwise <= 0.25

    def _flush(start, length):
        if length >= 4 and start is not None:
            out.append(
                _finding(
                    "arpeggiated_melody",
                    start,
                    None,
                    "warn",
                    f"Bars {start}–{start + length - 1}: the melody is almost entirely "
                    f"chord tones reached by leap for {length} bars — it outlines the "
                    f"harmony rather than singing over it.",
                    "Put non-chord tones on strong beats (an appoggiatura into the beat, "
                    "a suspension held over the change) and connect leaps by step.",
                    run=length,
                )
            )

    for bar in bars:
        if _bar_is_arpeggiated(bar):
            run_start = bar.get("bar_num") if run_start is None else run_start
            run_len += 1
            continue
        _flush(run_start, run_len)
        if len(out) >= cap:
            return out
        run_start, run_len = None, 0
    _flush(run_start, run_len)
    return out


def _bass_pitch(bar):
    """Lowest sounding pitch of a bar's accompaniment staff, as a MIDI number."""
    lows = []
    for source in ("lh_display", "lh_inner_display"):
        for e in bar.get(source) or []:
            if e.get("type") == "note" and e.get("pitch"):
                lows.append(e["pitch"])
            elif e.get("type") == "chord":
                lows.extend(e.get("pitches") or [])
    if not lows:
        return None
    try:
        import music21

        return min(music21.pitch.Pitch(p).midi for p in lows)
    except Exception:
        return None


def detect_static_bass(bars: List[Dict[str, Any]], cap: int = 6) -> List[Dict[str, Any]]:
    """Spans where the bass never moves under a moving melody.

    Measures MOTION, not note count. Defining it by density (an accompaniment of
    one note per bar) missed the actual failure users report and this system
    produced: a held bass note with busy filler above it has a high accompaniment
    density and a completely static foundation. Verified against
    `bagatelle-am-20260621`, whose bass is one unchanging pitch under a repeating
    three-note oscillation — the density test found nothing there.
    """
    out: List[Dict[str, Any]] = []
    run_start, run_len, prev = None, 1, None
    run_romans: set = set()

    def _is_drone(length, romans):
        # A PEDAL is expressive: the bass holds while the harmony moves above it
        # (Beethoven's dominant pedals, a mazurka drone under changing chords).
        # A DRONE is the failure: nothing moves at all. Requiring the harmony to
        # be static too takes the false-positive rate on real Mozart, Beethoven
        # and Chopin from 17 findings per 1405 bars to near zero, while still
        # catching an accompaniment that never goes anywhere.
        return length >= 4 and len(romans) <= 1

    for bar in bars:
        low = _bass_pitch(bar)
        moving_melody = int(bar.get("melody_density", 0)) >= 2
        if low is not None and low == prev and moving_melody:
            run_start = run_start if run_start is not None else bar.get("bar_num", 1) - 1
            run_len += 1
            if bar.get("roman"):
                run_romans.add(bar["roman"])
            continue
        if _is_drone(run_len, run_romans) and run_start is not None:
            out.append(
                _finding(
                    "static_bass",
                    run_start,
                    None,
                    "warn",
                    f"Bars {run_start}–{run_start + run_len - 1}: the bass sits on one "
                    f"pitch for {run_len} bars while the melody moves — the foundation "
                    f"is a drone: neither the bass nor the harmony moves.",
                    "Give the bass a line: walk it, change its inversion with the "
                    "harmony, or answer the melody's rests. A pedal is a choice for a "
                    "passage, not a default.",
                    run=run_len,
                )
            )
            if len(out) >= cap:
                return out
        run_start, run_len, prev = None, 1, low
        run_romans = {bar["roman"]} if bar.get("roman") else set()
    if _is_drone(run_len, run_romans) and run_start is not None:
        out.append(
            _finding(
                "static_bass",
                run_start,
                None,
                "warn",
                f"Bars {run_start}–{run_start + run_len - 1}: bass static for {run_len} bars.",
                "Give the bass a line.",
                run=run_len,
            )
        )
    return out


def detect_photocopied_accompaniment(bars: List[Dict[str, Any]], cap: int = 4):
    """Runs where the accompaniment repeats one figure unchanged, bar after bar.

    "Same Accompaniment Pattern Throughout" is the second entry in the brief's own
    AVOID list and nothing in the ear looked for it. The commit gate's
    `figuration_flat` only sees ONE PHRASE at a time and exempts static textures,
    so a figure photocopied across a whole section passed everything.

    The signature is the interval shape AND the rhythm together, so a figure that
    follows the harmony into a new position (which is what real accompaniment
    does) reads as varied, while a literally stamped-out pattern does not.
    """
    out: List[Dict[str, Any]] = []

    def sig(bar):
        events = [
            e
            for e in (bar.get("lh_display") or []) + (bar.get("lh_inner_display") or [])
            if e.get("type") in ("note", "chord")
        ]
        if len(events) < 3:
            return None
        try:
            import music21

            mids = [
                music21.pitch.Pitch(
                    e["pitch"] if e.get("type") == "note" else (e.get("pitches") or ["C4"])[0]
                ).midi
                for e in events
            ]
        except Exception:
            return None
        intervals = tuple(b - a for a, b in zip(mids, mids[1:]))
        rhythm = tuple(round(float(e.get("dur", 0)), 3) for e in events)
        return (intervals, rhythm)

    # Measure the WHOLE span, not a run. Falsification: a fixed "identical for 6
    # bars" rule fires 8 times across 15 real Mozart/Beethoven/Chopin movements —
    # repeating an accompaniment figure under a prolonged harmony is idiomatic,
    # and Op.2 no.1 does it for eight bars straight. The AVOID entry this detector
    # serves is "Same Accompaniment Pattern **Throughout**", which is a claim
    # about proportion, so that is what gets measured.
    from collections import Counter

    sigs = [sig(bar) for bar in bars]
    present = [x for x in sigs if x is not None]
    if len(present) < 12:
        return out  # too short for "throughout" to mean anything
    ((most_common, count),) = Counter(present).most_common(1)
    share = count / len(present)
    if share < 0.7:
        return out
    first = next(
        (b.get("bar_num") for b, x in zip(bars, sigs, strict=True) if x == most_common),
            bars[0].get("bar_num"),
    )
    out.append(
        _finding(
            "photocopied_accompaniment",
            first,
            None,
            "warn",
            f"One accompaniment figure — same intervals, same rhythm — covers "
            f"{share:.0%} of the {len(present)} bars examined. The pattern is not "
            f"varying with the music; it is being stamped onto it.",
            "Keep the figure but let it follow the harmony into new positions, invert "
            "its contour at the phrase midpoint, thin it under the melodic peak, and "
            "change it where the music turns a corner.",
            share=round(share, 3),
            bars_examined=len(present),
        )
    )
    return out


_MIN_WITHIN_BAR_SHARE = 0.10


def detect_flat_harmonic_rhythm(bars: List[Dict[str, Any]], cap: int = 1):
    """A whole span that changes harmony exactly once per bar and never within it.

    Distinct from `harmonic_stagnation`, which catches a harmony that does not
    move at all. This catches harmony that moves at a perfectly regular one-per-
    bar pulse — the signature of a plan that can only express one chord per bar.
    Two thirds of Mozart's bars carry more than one functional harmony; a section
    where none do is not a stylistic choice, it is a limitation showing through.
    """
    out: List[Dict[str, Any]] = []
    scored = [b for b in bars if b.get("harmony_events") is not None]
    if len(scored) < 12:
        return out
    within = sum(1 for b in scored if len(b.get("harmony_events") or []) > 1)
    share = within / len(scored)
    # Falsified against 15 real movements: the lowest any of them reaches is 13%
    # (K.280/i, an Allegro assai — a fast movement genuinely holds a harmony for
    # a whole bar more often). The threshold sits below real music so it fires on
    # a plan that CANNOT move harmony within a bar, not on one that chooses not to.
    if share >= _MIN_WITHIN_BAR_SHARE:
        return out
    out.append(
        _finding(
            "flat_harmonic_rhythm",
            scored[0].get("bar_num"),
            None,
            "warn",
            f"Only {share:.0%} of {len(scored)} bars change harmony within the bar — "
            f"the harmony moves on a metronomic one-chord-per-bar pulse.",
            "Move the bass inside the bar: a passing 6-4, an applied dominant on beat 3, "
            "a cadential ii6-I64-V inside one bar. Harmonic rhythm is what makes a "
            "phrase feel like it is going somewhere.",
            within_bar_share=round(share, 3),
        )
    )
    return out


def detect_harmonic_stagnation(bars: List[Dict[str, Any]], cap: int = 6):
    """Long spans on a single harmony with no melodic compensation.

    Harmonic rhythm is what makes a phrase feel like it is going somewhere.
    Nothing measured it — the planner emitted exactly one chord per bar and the
    reviewer never looked at how long the music sat still.
    """
    out: List[Dict[str, Any]] = []
    run_start, run_len, prev = None, 1, None
    for b in bars:
        roman = b.get("roman")
        if roman and roman == prev:
            run_start = run_start or b.get("bar_num", 1) - 1
            run_len += 1
            continue
        if run_len >= 6 and run_start is not None:
            out.append(
                _finding(
                    "harmonic_stagnation",
                    run_start,
                    None,
                    "warn",
                    f"Bars {run_start}–{run_start + run_len - 1}: {run_len} bars on the same "
                    f"harmony ({prev}) — the phrase stops moving.",
                    "Change the harmony, tonicize, or make the stasis expressive "
                    "(a pedal under real motion above it).",
                    run=run_len,
                    roman=prev,
                )
            )
            if len(out) >= cap:
                return out
        run_start, run_len, prev = None, 1, roman
    return out


def detect_flat_register(graph, cap: int = 6):
    """Phrases whose melody hovers instead of following its planned register arc.

    The dramatic plan gives every phrase a register curve — where the line should
    rise and fall so the PIECE has a shape rather than nine locally-arched
    phrases. Nothing checked it, so a phrase could sit in one octave through the
    climax and nothing would notice.

    Flags a phrase whose melodic span is under a fifth, or whose peak lands at an
    edge when the plan asked for an arch. Warning-level: a deliberately static
    line is a real device.
    """
    out: List[Dict[str, Any]] = []
    for pid, ps in sorted(
        (
            (pid, ps)
            for pid, ps in getattr(graph, "phrases", {}).items()
            if getattr(ps, "slot", None) and getattr(ps, "realized", None)
        ),
        key=lambda kv: kv[1].slot.bar_start,
    ):
        plan = list(getattr(ps.slot, "curves", None).register or []) if ps.slot.curves else []
        if len(plan) < 3:
            continue
        mids = []
        for e in sorted(ps.realized.principal_line, key=lambda e: (e.bar, e.beat)):
            if e.pitch == "rest":
                continue
            names = e.pitch if isinstance(e.pitch, list) else [e.pitch]
            try:
                import music21

                mids.append(max(music21.pitch.Pitch(n).midi for n in names))
            except Exception:
                continue
        if len(mids) < 4:
            continue
        span = max(mids) - min(mids)
        if span >= 7:
            continue
        out.append(
            _finding(
                "flat_register",
                ps.slot.bar_start,
                None,
                "warn",
                f"Bars {ps.slot.bar_start}-{ps.slot.bar_start + ps.slot.bar_count - 1} "
                f"({pid}): the melody stays within {span} semitones. The plan asked for a "
                f"register arc of {[round(x, 2) for x in plan]} — the line should go "
                f"somewhere across the phrase.",
                "Take the line up to a real peak and bring it back, or hand it to a "
                "different octave. Register is the cheapest drama available.",
                span=span,
            )
        )
        if len(out) >= cap:
            break
    return out


def detect_unvaried_return(graph, cap: int = 4):
    """A RETURN phrase that is a near-copy of the statement it returns to.

    This is the machine tell that no statistic catches, because every metric reads
    "matches the exposition" — which is exactly the defect. Compares the returning
    phrase's melodic surface (rhythm and interval contour) against the phrase that
    first stated the material.

    Needs the PieceGraph, not just bar records: the relationship is between two
    phrases in the form, which the assembled score does not encode.
    """
    out: List[Dict[str, Any]] = []
    slots = [
        (pid, ps)
        for pid, ps in getattr(graph, "phrases", {}).items()
        if getattr(ps, "slot", None) and getattr(ps, "realized", None)
    ]
    slots.sort(key=lambda kv: kv[1].slot.bar_start)

    def surface(layer):
        evs = sorted(
            (e for e in layer.principal_line if e.pitch != "rest"),
            key=lambda e: (e.bar, e.beat),
        )
        rhythm = tuple(e.duration for e in evs)
        mids = []
        for e in evs:
            names = e.pitch if isinstance(e.pitch, list) else [e.pitch]
            try:
                import music21

                mids.append(max(music21.pitch.Pitch(n).midi for n in names))
            except Exception:
                mids.append(None)
        contour = tuple((b - a) for a, b in zip(mids, mids[1:]) if a is not None and b is not None)
        return rhythm, contour

    statements = [
        (pid, ps) for pid, ps in slots if getattr(ps.slot, "dramatic_role", "") == "establish"
    ]
    if not statements:
        return out

    for pid, ps in slots:
        if getattr(ps.slot, "dramatic_role", "") != "return":
            continue
        r_rhythm, r_contour = surface(ps.realized)
        if len(r_rhythm) < 4:
            continue
        for spid, sps in statements:
            s_rhythm, s_contour = surface(sps.realized)
            n = min(len(r_rhythm), len(s_rhythm))
            if n < 4:
                continue
            same_rhythm = sum(1 for a, b in zip(r_rhythm[:n], s_rhythm[:n]) if a == b) / n
            m = min(len(r_contour), len(s_contour))
            same_contour = (
                sum(1 for a, b in zip(r_contour[:m], s_contour[:m]) if a == b) / m if m else 0.0
            )
            if same_rhythm >= 0.85 and same_contour >= 0.85:
                strat = getattr(ps.slot, "return_strategy", "") or "vary it"
                out.append(
                    _finding(
                        "unvaried_return",
                        ps.slot.bar_start,
                        None,
                        "warn",
                        f"Bar {ps.slot.bar_start}: the return ({pid}) repeats {spid} almost "
                        f"exactly — {same_rhythm:.0%} of its rhythm and {same_contour:.0%} of "
                        f"its contour are identical. A return has to be changed by what "
                        f"happened in between.",
                        f"The plan asked for '{strat}'. Change the line itself, not the "
                        f"decoration on top of it.",
                        rhythm_match=round(same_rhythm, 3),
                        contour_match=round(same_contour, 3),
                    )
                )
                if len(out) >= cap:
                    return out
                break
    return out


# ─── Top-level ───────────────────────────────────────────────────────────────


def ear_report(score_path: str, bars: List[Dict[str, Any]], graph=None) -> Dict[str, Any]:
    """Run all detectors; return {findings, summary, undetectable}.

    ``graph`` (optional) enables the detectors that compare PHRASES to each other
    — a relationship the assembled score does not encode.
    """
    findings: List[Dict[str, Any]] = []
    try:
        import music21

        score = music21.converter.parse(score_path)
        findings += detect_bar_length_errors(score)
        findings += detect_out_of_range(score)
        findings += detect_vertical_clashes(score)
        findings += detect_melody_buried(score)
    except Exception as exc:  # parse failure must not crash review
        findings.append(
            _finding("ear_error", None, None, "info", f"could not parse score: {exc}", "")
        )
    findings += detect_unresolved_nct(bars)
    findings += detect_no_breathing(bars)
    findings += detect_monotony(bars)
    findings += detect_static_bass(bars)
    findings += detect_harmonic_stagnation(bars)
    findings += detect_arpeggiated_melody(bars)
    findings += detect_photocopied_accompaniment(bars)
    findings += detect_flat_harmonic_rhythm(bars)
    if graph is not None:
        try:
            findings += detect_unvaried_return(graph)
            findings += detect_flat_register(graph)
        except Exception as exc:  # never let a cross-phrase check crash review
            findings.append(_finding("ear_error", None, None, "info", str(exc), ""))

    by_det: Dict[str, int] = {}
    errors = warns = 0
    for f in findings:
        by_det[f["detector"]] = by_det.get(f["detector"], 0) + 1
        if f["severity"] == "error":
            errors += 1
        elif f["severity"] == "warn":
            warns += 1
    return {
        "findings": findings,
        "summary": {"by_detector": by_det, "error_count": errors, "warn_count": warns},
        "undetectable": _UNDETECTABLE,
    }
