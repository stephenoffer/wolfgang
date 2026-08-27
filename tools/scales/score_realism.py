"""Score-realism audit — the read-back detectors for "this sounds machine-made".

`musical_ear` catches defects that are *wrong*: a bar holding five beats of a
4/4, a note outside the instrument's range, a cross-relation that grates. It
reported **zero errors and zero warnings** on a 41-bar andante that used the same
cadence formula in seven of its bars, put a `rit.` on nine of them, had twelve
bars of the identical left-hand triplet arpeggio, and contained not one
articulation mark or tie in the whole score. Nothing there is *wrong*. It is
just obviously not written by a person.

This module is the missing half: detectors for **formula, uniformity and
notational poverty** — the properties that separate generated music from
engraved music even when every note is legal.

Everything here is advisory by construction. These are diagnostics for the
fresh-ears critic to read and weigh, never auto-blocks: a piece may repeat a bar
verbatim on purpose, and a Palestrina motet legitimately has no dynamics at all.
Each detector carries the calibration that justifies its threshold, and every
threshold in this file was set by running the detector over the real
Mozart/Beethoven/Chopin corpus under `tools/reference_scores/` (see
``tools/tests/test_score_realism_calibration.py``) and choosing a bound the real
music clears. A detector that fires on canonical music is a broken detector.

Input is the ASSEMBLED score, not the IR. Export bugs are real (a whole class of
them has shipped here before) and only reading the finished file back can see
them.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import style_registry

# Advisory severities. Nothing in this module ever emits "error" — see the
# module docstring.
_WARN = "warn"
_INFO = "info"


def _finding(detector, bar, severity, problem, fix_hint, **evidence) -> Dict[str, Any]:
    return {
        "detector": detector,
        "bar": bar,
        "beat": None,
        "severity": severity,
        "problem": problem,
        "fix_hint": fix_hint,
        "evidence": evidence,
    }


# ─── Bar extraction ──────────────────────────────────────────────────────────


def _bar_table(score) -> List[Dict[str, Any]]:
    """Flatten the assembled score into one record per bar per staff.

    Each record holds what the formula detectors need: the onset grid, the
    duration multiset, the pitch contour, and the notation marks actually
    present. Reading this off the finished score (rather than the IR) is
    deliberate — it is the only view that includes what the exporter did.
    """
    import music21

    out: List[Dict[str, Any]] = []
    parts = list(score.parts) or [score]
    for staff_idx, part in enumerate(parts):
        for m in part.getElementsByClass("Measure"):
            onsets: List[float] = []
            durs: List[float] = []
            midis: List[int] = []
            tops: List[int] = []
            chord_sizes: List[int] = []
            arts: List[str] = []
            orns: List[str] = []
            ties = 0
            rests = 0
            n_grace = 0
            for n in m.flatten().notesAndRests:
                off = float(n.offset)
                if isinstance(n, music21.note.Rest):
                    rests += 1
                    continue
                if getattr(n.duration, "isGrace", False):
                    n_grace += 1
                    continue
                onsets.append(round(off, 4))
                durs.append(round(float(n.quarterLength), 4))
                ps = list(n.pitches)
                chord_sizes.append(len(ps))
                mm = [p.midi for p in ps]
                midis.extend(mm)
                tops.append(max(mm))
                for a in n.articulations:
                    arts.append(type(a).__name__)
                for e in n.expressions:
                    orns.append(type(e).__name__)
                if n.tie is not None:
                    ties += 1
            texts = []
            dyns = []
            for e in m.flatten().getElementsByClass(["TextExpression", "Dynamic", "MetronomeMark"]):
                if isinstance(e, music21.dynamics.Dynamic):
                    dyns.append(e.value)
                elif isinstance(e, music21.tempo.MetronomeMark):
                    texts.append(f"__tempo__{e.number}")
                else:
                    texts.append(str(e.content))
            try:
                bar_beats = float(m.barDuration.quarterLength)
            except Exception:
                bar_beats = 4.0
            out.append(
                {
                    "bar": m.number,
                    "staff": staff_idx,
                    "bar_beats": bar_beats,
                    "onsets": onsets,
                    "durations": durs,
                    "midis": midis,
                    "tops": tops,
                    "chord_sizes": chord_sizes,
                    "articulations": arts,
                    "ornaments": orns,
                    "ties": ties,
                    "rests": rests,
                    "graces": n_grace,
                    "texts": texts,
                    "dynamics": dyns,
                }
            )
    return out


def _rhythm_sig(rec: Dict[str, Any]) -> Tuple:
    """The bar's rhythm alone: (onset, duration) pairs."""
    return tuple(zip(rec["onsets"], rec["durations"], strict=True))


def _contour_sig(rec: Dict[str, Any]) -> Tuple:
    """Interval sequence of the bar's top line (transposition-invariant)."""
    tops = rec["tops"]
    return tuple(b - a for a, b in zip(tops, tops[1:]))


#: Interval size classes: unison, step, small leap (3rd/4th), leap (5th-7th),
#: octave or more. A major and a minor third land in the same class, which is
#: the whole point — see `_contour_shape_sig`.
def _interval_class(semitones: int) -> int:
    size = abs(semitones)
    sign = (semitones > 0) - (semitones < 0)
    if size == 0:
        return 0
    return sign * (1 if size <= 2 else 2 if size <= 4 else 3 if size <= 7 else 4)


def _contour_shape_sig(rec: Dict[str, Any]) -> Tuple:
    """The bar's contour as a SHAPE, blind to chord quality.

    `_contour_sig` compares exact semitones, so the same arpeggio played over a
    major chord `(7, 5, 4, 3, ...)` and over a minor one `(7, 5, 3, 4, ...)`
    read as two unrelated idioms. That is a distinction the ear does not make
    about accompaniment figuration: it is one figure following the harmony,
    which is what an accompaniment IS.

    The cost was that `accompaniment_monoculture` fragmented a single idiom
    across many signatures and undercounted it. A generated nocturne whose left
    hand is one arpeggio shape from beginning to end — bar 4 identical to bar 2,
    bar 5 to bar 1 — measured 0.56 against a 0.70 bound and passed silently,
    while its three commonest "different" signatures were the same
    root-fifth-octave-tenth figure over different chords.
    """
    tops = rec["tops"]
    return tuple(_interval_class(b - a) for a, b in zip(tops, tops[1:]))


def _full_sig(rec: Dict[str, Any]) -> Tuple:
    """Verbatim identity of a bar: exact pitches at exact positions."""
    return (tuple(rec["onsets"]), tuple(rec["durations"]), tuple(rec["midis"]))


# ─── Formula detectors ───────────────────────────────────────────────────────


def detect_repeated_bars(bars: List[Dict[str, Any]], cap: int = 6) -> List[Dict[str, Any]]:
    """Whole bars repeated VERBATIM (same pitches, same rhythm) at an extreme rate.

    **Read the calibration before touching the bound.** Verbatim bar repetition
    is not a defect — it is how real music is built. Measured over 52
    staff-views of 26 canonical movements (14 Mozart sonata movements, 6 Chopin
    mazurkas, 6 Beethoven sonata movements): the share of a staff's bars that
    are verbatim repeats of another bar runs **median 0.38, p90 0.78, max
    0.91**, and the single most-repeated bar recurs **median 4, p90 8, max 16**
    times. The bound this detector originally shipped with (share >= 0.5 or 4
    repeats) fired on **20 of those 26 canonical movements**.

    So the bound is now set above the real maximum and the finding is `info`,
    not `warn`. What actually reads as machine-made is a restatement that fails
    to *develop* — and that is a musical judgement belonging to the fresh-ears
    critic, not a countable property of the score.
    """
    out: List[Dict[str, Any]] = []
    for staff in sorted({b["staff"] for b in bars}):
        recs = [b for b in bars if b["staff"] == staff and b["midis"]]
        if len(recs) < 8:
            continue
        counts = Counter(_full_sig(r) for r in recs)
        repeated = sum(c for c in counts.values() if c > 1)
        share = repeated / len(recs)
        worst_sig, worst_n = counts.most_common(1)[0]
        # Above the canonical maximum on BOTH axes — see the docstring.
        if share < 0.92 or worst_n < 17:
            continue
        where = [r["bar"] for r in recs if _full_sig(r) == worst_sig]
        if True:
            out.append(
                _finding(
                    "repeated_bars",
                    where[0] if where else None,
                    _INFO,
                    f"Staff {staff}: {round(share * 100)}% of bars are verbatim repeats of "
                    f"another bar; one bar is repeated {worst_n} times (bars "
                    f"{', '.join(str(w) for w in where[:8])}).",
                    "Vary a restatement rather than copying it: re-voice it, change the "
                    "figuration, add or remove a decoration, or reharmonise the second half.",
                    repeat_share=round(share, 3),
                    max_repeats=worst_n,
                    bars=where[:12],
                )
            )
        if len(out) >= cap:
            break
    return out


#: Fewest phrase openings (or endings) before "nothing comes back" is a claim
#: about the music rather than about the sample. Measured over real movements
#: from six composers, the share where the most common figure appears exactly
#: once: 6.2% / 2.9% at four phrases, 3.0% / 0.5% at six.
_RECURRENCE_MIN_PHRASES = 6


def detect_no_recurring_material(
    bars: List[Dict[str, Any]],
    phrase_start_bars: Sequence[int],
    phrase_end_bars: Sequence[int],
    melody_staff: int = 0,
    cap: int = 2,
) -> List[Dict[str, Any]]:
    """Nothing in the piece ever comes back.

    Every detector in this file catches too MUCH sameness. None of them catches
    too little, and a piece where nothing recurs passes all of them — which is
    the other half of sounding machine-made, and the more common half here. On
    an 85-bar generated piece: the most common phrase opening appeared in 1 of
    19 phrases, against a real median of a third. That is not variety. It is a
    piece with no theme, where the listener is given nothing to recognise.

    Measured over 304 real movements (mozart, beethoven, chopin, haydn,
    schubert, bach) with at least six marked phrase openings, the most common
    opening figure appears exactly once in **3.0%** of them; for cadential
    rhythms, **0.5%** of 386. Below six phrases the same measure hits 6.2% and
    2.9%, because at four phrases "nothing repeated" is as much a statement
    about the sample as about the music — hence the floor.

    `info`, never `warn`: a composer may genuinely write through-composed music
    with no returning figure, and the fresh-ears critic is better placed than a
    counter to say whether this piece wanted one.
    """
    out: List[Dict[str, Any]] = []
    for label, positions, key in (
        (
            "opening",
            phrase_start_bars,
            lambda r: (_rhythm_sig(r), _contour_sig(r)),
        ),
        ("cadence", phrase_end_bars, _rhythm_sig),
    ):
        marks = set(int(b) for b in positions)
        recs = [b for b in bars if b["staff"] == melody_staff and b["bar"] in marks and b["midis"]]
        if len(recs) < _RECURRENCE_MIN_PHRASES:
            continue
        counts = Counter(key(r) for r in recs)
        top = counts.most_common(1)[0][1]
        if top > 1:
            continue
        out.append(
            _finding(
                "no_recurring_material",
                min(r["bar"] for r in recs),
                _INFO,
                f"No {label} figure appears twice: all {len(recs)} phrase {label}s "
                f"are different. Real movements reuse one in about a third of "
                f"their phrases; nothing here comes back for the listener to "
                f"recognise.",
                "Bring the head-motif back — literally at a return, varied in a "
                "sequence, in the bass under new material, inverted in a "
                "development. A piece with no recurring idea has nothing to "
                "develop and nothing to resolve.",
                phrases_examined=len(recs),
                kind=label,
            )
        )
        if len(out) >= cap:
            break
    return out


#: Share of phrase endings sharing one rhythm before it reads as formula rather
#: than style. Per staff: see `detect_cadence_formula_reuse` for the measured
#: distributions these come from. Both sit at an 8% false-positive rate on real
#: movements — the same rate, not the same number, because the two staves do not
#: behave the same way.
_CADENCE_FORMULA_BOUND = 0.66
_CADENCE_FORMULA_BOUND_ACCOMP = 0.78


def detect_cadence_formula_reuse(
    bars: List[Dict[str, Any]],
    phrase_end_bars: Sequence[int],
    cap: int = 3,
    melody_staff: int = 0,
) -> List[Dict[str, Any]]:
    """The same cadential gesture at nearly every phrase ending.

    This is the single loudest tell in the baseline score: seven of its 41 bars
    were the identical "half note plus quarter rest", one at every phrase end,
    and the left hand under them was the identical "root, chord, rest". A human
    varies the close — feminine ending, escape tone, a held note over the
    barline, a rest, an overlapping entry.

    Compared on RHYTHM ONLY, so a cadence that keeps the shape but changes the
    pitches still counts as the same formula (it is).

    THE TWO STAVES HAVE DIFFERENT DISTRIBUTIONS and one bound was applied to
    both. Measured over 261 real movements (mozart, beethoven, chopin, haydn),
    taking the bars the corpus marks `cadential` or `closing`, with this
    function's own signature:

        staff   median reuse   p90    flagged at 0.66   at 0.78
        melody           33%   61%                 8%        3%
        accomp           39%   76%                18%        8%

    The melody figure is where the "about a third to a half" above comes from.
    An accompaniment genuinely repeats more — that is what an accompaniment
    does — so at 0.66 this flagged nearly one real movement in five on the lower
    staff. The bound that puts the accompaniment at the melody's false-positive
    rate is 0.78, and the reasoning above was derived from the melody and then
    applied to both without re-measuring.
    """
    out: List[Dict[str, Any]] = []
    ends = set(int(b) for b in phrase_end_bars)
    if len(ends) < 3:
        return out
    for staff in sorted({b["staff"] for b in bars}):
        recs = [b for b in bars if b["staff"] == staff and b["bar"] in ends and b["midis"]]
        if len(recs) < 3:
            continue
        counts = Counter(_rhythm_sig(r) for r in recs)
        sig, n = counts.most_common(1)[0]
        share = n / len(recs)
        # Two-thirds of cadences sharing a rhythm is a formula in the MELODY.
        # The accompaniment's own distribution sits higher; see the table above.
        bound = _CADENCE_FORMULA_BOUND if staff == melody_staff else _CADENCE_FORMULA_BOUND_ACCOMP
        if n >= 3 and share >= bound:
            where = [r["bar"] for r in recs if _rhythm_sig(r) == sig]
            out.append(
                _finding(
                    "cadence_formula",
                    where[0],
                    _WARN,
                    f"Staff {staff}: {n} of {len(recs)} phrase endings use the identical "
                    f"cadential rhythm (bars {', '.join(str(w) for w in where[:8])}). "
                    f"Every phrase closes the same way.",
                    "Give each close its own character: land one on a weak beat, tie one "
                    "over the barline into the next phrase, let one elide with the next "
                    "entry, decorate one with a turn or an appoggiatura, leave one open.",
                    formula_share=round(share, 3),
                    bars=where[:12],
                )
            )
        if len(out) >= cap:
            break
    return out


#: Above the highest value reached by any real movement measured (0.640,
#: mazurka33-2). An earlier 0.62 was set from a sample that missed it.
#: The measurement and its breakdown are in the detector's docstring below.
_MONOCULTURE_MAX_SHARE = 0.68


def detect_accompaniment_monoculture(
    bars: List[Dict[str, Any]], accomp_staff: int = 1, cap: int = 2
) -> List[Dict[str, Any]]:
    """One accompaniment idiom for the whole piece.

    Measured as the share of accompaniment bars sharing both a rhythm signature
    and a contour signature — i.e. the same figure transposed. The baseline
    score ran a broken-chord triplet arpeggio in 12 of 41 bars and a
    rest-plus-repeated-chord figure in most of the rest, so two idioms covered
    the entire piece.

    Calibration note: a persistent figure is a legitimate device (a Chopin
    berceuse, an Alberti-bass Mozart andante), so the finding is advisory.

    The contour is compared as a SHAPE rather than in exact semitones — see
    `_contour_shape_sig`. Comparing exact semitones split one arpeggio idiom
    across a signature per chord quality and undercounted it badly: a generated
    nocturne running a single left-hand figure from beginning to end measured
    0.56 and passed a 0.70 bound.

    Re-measured over **82 canonical movements** under the shape signature:

        fires    repertoire                  median   p90    max
        0/16     chopin mazurkas (kern)        0.27   0.48   0.59
        0/16     chopin preludes (MIDI)        0.22   0.32   0.46
        0/16     mozart sonatas (kern)         0.11   0.20   0.28
        0/16     beethoven sonatas (kern)      0.12   0.15   0.20
        0/18     bach / haydn (MIDI)           0.10   0.13   0.19
        ---------------------------------------------------------
        none     all                           0.13   p95 0.40

    That sample's maximum was 0.59, and taking it as the ceiling was wrong: the
    calibration harness's own corpus contains **mazurka33-2 at 0.640** — 136
    accompaniment bars, and the sample above had missed it. The bound is
    therefore 0.68, above the highest real value actually observed.

    A consequence worth stating rather than burying, because it is the reason
    this detector is not the answer it looks like: a generated nocturne whose
    left hand is demonstrably ONE figure from beginning to end — bar 4 identical
    to bar 2, bar 5 to bar 1 — measures 0.66, which is INSIDE the range real
    Chopin occupies. This measure asks how often the commonest figure recurs,
    and a mazurka recurs that often by design. It cannot separate the two, and a
    bound tuned to the 0.02 between them would be fitting noise.

    What does separate them is how MANY figures the hand knows across the piece
    — 6 for that nocturne against a real-Chopin median of 23 — which is
    `detect_accompaniment_vocabulary_poverty`, next door, and a different
    question from this one.
    """
    recs = [b for b in bars if b["staff"] == accomp_staff and b["midis"]]
    if len(recs) < 10:
        return []
    counts = Counter((_rhythm_sig(r), _contour_shape_sig(r)) for r in recs)
    sig, n = counts.most_common(1)[0]
    share = n / len(recs)
    if share < _MONOCULTURE_MAX_SHARE:
        return []
    where = [r["bar"] for r in recs if (_rhythm_sig(r), _contour_shape_sig(r)) == sig]
    return [
        _finding(
            "accompaniment_monoculture",
            where[0],
            _WARN,
            f"{n} of {len(recs)} accompaniment bars ({round(share * 100)}%) are the same "
            f"figure transposed — one idiom carries the entire piece.",
            "Change the left hand where the music changes: thin it to bare octaves at a "
            "quiet return, break it into real two-voice writing at a modulation, let it "
            "take the melody's rhythm for a bar, drop it entirely for a bar of breath.",
            idiom_share=round(share, 3),
            bars=where[:12],
        )
    ][:cap]


def detect_notation_spam(bars: List[Dict[str, Any]], cap: int = 4) -> List[Dict[str, Any]]:
    """The same performance direction printed absurdly often.

    A `rit.` is a rare, structural mark. The baseline score had nine of them
    alternating with nine `a tempo` marks — a tempo instruction on almost every
    other bar, which no engraved score contains. This detector exists so that
    if the placement logic regresses, the audit says so instead of the defect
    shipping again.
    """
    out: List[Dict[str, Any]] = []
    span = len({b["bar"] for b in bars}) or 1
    counts: Counter = Counter()
    first_at: Dict[str, int] = {}
    for b in sorted(bars, key=lambda r: r["bar"]):
        for t in b["texts"]:
            if t.startswith("__tempo__"):
                t = "tempo mark"
            counts[t] += 1
            first_at.setdefault(t, b["bar"])
    for text, n in counts.most_common():
        # One instruction per eight bars is already generous for rit./a tempo;
        # a character word like "dolce" recurring is normal, so only
        # tempo-modifying directions are held to the tight bound.
        tempo_word = any(
            k in text.lower() for k in ("rit", "tempo", "accel", "rall", "string", "allarg")
        )
        limit = max(2, span // (8 if tempo_word else 3))
        if n > limit:
            out.append(
                _finding(
                    "notation_spam",
                    first_at.get(text),
                    _WARN,
                    f'"{text}" appears {n} times in {span} bars. A tempo or expression '
                    f"direction repeated that often reads as noise, not instruction.",
                    "Keep tempo directions for genuine structural moments — a sectional "
                    "close, the approach to a coda — and let the notes carry the rest.",
                    count=n,
                    bars_span=span,
                )
            )
        if len(out) >= cap:
            break
    return out


# ─── Notational poverty detectors ────────────────────────────────────────────


def _is_renaissance(composer: str) -> bool:
    """Whether this piece belongs to a repertoire that predates the notation.

    Dynamics and articulation marks are not sparse in Renaissance vocal
    polyphony, they are ABSENT — the notation did not exist. Measured over real
    scores, `dynamic_poverty` fires on 100% of Palestrina and 100% of Monteverdi
    and `articulation_absent` on 100% and 92%, against 0% of real Bach chorales
    and 0% of real Mozart piano. `expression_enricher` is already period-gated
    NOT to add either for the Renaissance, so faulting their absence penalises
    the engraver for being correct — the system contradicting itself.
    """
    return "renaissance" in style_registry.styles_for_composer((composer or "").lower())


def detect_articulation_absence(
    bars: List[Dict[str, Any]], composer: str = ""
) -> List[Dict[str, Any]]:
    """A score with (almost) no articulation marks.

    Real Classical and Romantic piano writing is dense with them. Measured over
    the 26-movement reference corpus, articulation marks per bar run **0.041 to
    2.24, median 0.57** — every canonical movement has at least some. The
    baseline generated score had **zero** in 41 bars, on both staves.

    The bound sits at exactly zero on purpose: this catches "the composer wrote
    none at all", which is a different failure from "the composer chose sparse
    articulation".

    **Known false-positive rate: ~5%.** Two of the forty sampled canonical
    movements (Beethoven Op.31 No.3 slow movement, Mozart K.309 second
    movement) carry no articulation at all *in this Humdrum edition* — an
    encoding limit as much as a musical fact. So this is a prompt to check
    whether the bare page was deliberate, not proof that it was wrong. It stays
    a `warn` because for generated output an articulation count of zero is
    essentially never a deliberate choice.

    Movements under 24 bars are skipped: the reference corpus splits
    theme-and-variations movements into separate 18-bar files, and a variation
    is not a score.
    """
    if _is_renaissance(composer):
        return []  # see `_is_renaissance`
    n_bars = len({b["bar"] for b in bars}) or 1
    total = sum(len(b["articulations"]) for b in bars)
    per_bar = total / n_bars
    if per_bar > 0.0 or n_bars < 24:
        return []
    return [
        _finding(
            "articulation_absent",
            min((b["bar"] for b in bars), default=None),
            _WARN,
            f"{total} articulation marks in {n_bars} bars. Nothing on the page says how "
            f"any of it is to be touched.",
            "Articulation is part of the idea, not decoration added afterwards: slur the "
            "sighing pairs, detach the accompaniment where it should be light, mark the "
            "arrival, put a tenuto on the note that has to be leaned on.",
            marks=total,
            per_bar=round(per_bar, 3),
        )
    ]


def detect_tie_absence(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Nothing held across a barline anywhere in a long score.

    Measured over the 26-movement reference corpus: tied notes per bar run
    **0.0 to 0.95, median 0.18** — but two canonical movements (Mozart K.279
    third movement, Chopin Op.30 No.2) contain **no ties at all**. Zero ties is
    therefore not by itself a defect, and this finding is `info`: a piece where
    every bar is a sealed box is worth the critic's attention, not an automatic
    mark against it.
    """
    n_bars = len({b["bar"] for b in bars}) or 1
    total = sum(b["ties"] for b in bars)
    if total > 0 or n_bars < 24:
        return []
    return [
        _finding(
            "tie_absent",
            None,
            _INFO,
            f"No tied notes anywhere in {n_bars} bars — nothing is held over a barline "
            f"and every bar starts from silence.",
            "Let a line lean into the next bar: a melody note tied over the barline, a "
            "suspension resolving late, a pedal bass held through a phrase joint. Write "
            "it as `C5h~` at the end of one bar and `C5h` at the start of the next.",
            bars_checked=n_bars,
        )
    ]


def detect_dynamic_poverty(
    bars: List[Dict[str, Any]], hairpins: int, composer: str = ""
) -> List[Dict[str, Any]]:
    """Fewer volume events than any real movement carries.

    This replaces an earlier `dynamic_terracing` detector that fired on **26 of
    26** canonical movements. It asked whether the score had hairpins, and the
    answer was always no — not because Mozart never swells, but because the
    Humdrum importer that reads the reference corpus does not create wedge
    spanners. The detector was measuring the file format.

    What *is* measurable, and what the reference corpus does bound, is the total
    density of volume events (written dynamics plus hairpins): **0.163 to 2.22
    per bar, median 0.77**, across the 26 movements. Terraced dynamics are
    idiomatic for early music and for Mozart's echo effects, so the shape of the
    change is not the question; the amount of it is.
    """
    if _is_renaissance(composer):
        return []  # see `_is_renaissance`
    n_bars = len({b["bar"] for b in bars}) or 1
    n_dyn = sum(len(b["dynamics"]) for b in bars)
    per_bar = (n_dyn + hairpins) / n_bars
    # Below the canonical minimum of 0.163/bar.
    if n_bars < 24 or per_bar >= 0.16:
        return []
    return [
        _finding(
            "dynamic_poverty",
            None,
            _WARN,
            f"{n_bars} bars carry {n_dyn} dynamic marks and {hairpins} hairpins "
            f"({round(per_bar, 3)} per bar). The quietest real movement in the reference "
            f"corpus carries 0.163 per bar; nothing here grows or subsides.",
            "Shape within the phrase, not just between sections: a crescendo into the "
            "peak and a diminuendo off it, a subito piano where the harmony turns.",
            dynamics=n_dyn,
            hairpins=hairpins,
            per_bar=round(per_bar, 3),
        )
    ]


def detect_voicing_poverty(bars: List[Dict[str, Any]], melody_staff: int = 0, staff_count: int = 2):
    """A melody that is single notes and nothing else — on a keyboard.

    Real piano melody writing thickens at arrivals — thirds, sixths, octaves,
    full chords — and the thickening is how a climax reads as a climax.
    Measured over the 26-movement reference corpus: the share of melody-staff
    attacks that are single notes runs **0.40-0.98 (median 0.91)**. Real
    melodies are overwhelmingly single-note, so only a score that has *never
    once* thickened is remarkable — the bound sits above the canonical maximum
    of 0.980, and needs a long enough score for the absence to mean anything.

    That corpus is 26 PIANO movements, and "the right hand never thickens" is
    not a defect a violin or a soprano can avoid: one note at a time is the
    instrument. Run against music21's own corpus, which is quartets and motets
    rather than sonatas, this fired on 50% of real Mozart and 78% of real Haydn
    — telling canonical chamber music that no moment sounds fuller than any
    other. Staff count separates the two cases cleanly: the piano corpus is 2
    staves throughout, quartets are 4, and the motets 4-8. So the detector now
    speaks only about the grand staff it was measured on.
    """
    if staff_count != 2:
        return []
    recs = [b for b in bars if b["staff"] == melody_staff and b["chord_sizes"]]
    if len(recs) < 32:
        return []
    sizes = [s for b in recs for s in b["chord_sizes"]]
    if not sizes:
        return []
    single = sum(1 for s in sizes if s == 1) / len(sizes)
    if single < 0.99:
        return []
    return [
        _finding(
            "voicing_poverty",
            recs[0]["bar"],
            _WARN,
            f"{round(single * 100)}% of melody attacks are single notes — the right hand "
            f"never thickens, so no moment sounds fuller than any other.",
            "Double the line in thirds or sixths where it should warm, take the peak in "
            "octaves, put a full chord on the arrival. Weight is a structural device.",
            single_note_share=round(single, 3),
        )
    ]


# ─── Uniformity detectors ────────────────────────────────────────────────────


_RHYTHM_VOCAB_CACHE: Dict[str, Any] = {}

#: Used only when a composer's own distribution is unmeasurable. Set from the
#: union across composers rather than from Mozart, so it errs toward silence.
_RHYTHM_SHARE_CEILING = 0.99
_RHYTHM_DISTINCT_FLOOR = 2


def _rhythm_vocabulary_bounds(composer: str) -> Optional[Tuple[float, int]]:
    """`(max dominant share, min distinct values)` from this composer's own
    staves — his 95th percentile share and 5th percentile distinct count.

    None when unmeasurable, in which case the caller falls back to bounds that
    err toward saying nothing.
    """
    if composer in _RHYTHM_VOCAB_CACHE:
        return _RHYTHM_VOCAB_CACHE[composer]
    bounds = None
    try:
        from collections import defaultdict

        from .composition_brief import _iter_corpus_bars

        per: Dict[Tuple[Any, str], List[float]] = defaultdict(list)
        for bar in _iter_corpus_bars(composer):
            for hand in ("rh_display", "lh_display"):
                for e in bar.get(hand) or []:
                    if isinstance(e, dict) and e.get("type") != "rest" and e.get("dur"):
                        per[(bar.get("source"), hand)].append(round(float(e["dur"]), 3))
        shares, distincts = [], []
        sources: set = set()
        for (source, _hand), durs in per.items():
            if len(durs) < 40:
                continue
            counts = Counter(durs)
            shares.append(counts.most_common(1)[0][1] / len(durs))
            distincts.append(len(counts))
            sources.add(source)
        # MOVEMENTS, not staff-views. The guard counted staff-views, and the two
        # staves of one movement are not independent samples of a composer:
        # Liszt cleared a threshold of 8 with 8 views drawn from FOUR pieces, so
        # his 95th percentile share was effectively the second-highest of four.
        # It came out at 0.714, and a generated Liszt tripped the detector at
        # 73% and 97% — while real CHOPIN left hands exceed 97% in a quarter of
        # his movements. A band that narrow is a fact about the sample.
        #
        # Four composers were affected: debussy and liszt at 4 movements,
        # rimsky-korsakov and vivaldi at 5. They fall back to the wide
        # cross-composer band, which errs toward saying nothing — the right
        # failure for a thinly-armed composer.
        if len(sources) >= 8 and len(shares) >= 8:
            shares.sort()
            distincts.sort()
            bounds = (
                shares[int(0.95 * (len(shares) - 1))],
                distincts[int(0.05 * (len(distincts) - 1))],
            )
    except Exception:
        bounds = None
    _RHYTHM_VOCAB_CACHE[composer] = bounds
    return bounds


def detect_rhythm_vocabulary_poverty(bars: List[Dict[str, Any]], cap: int = 2, composer: str = ""):
    """Too few distinct note values in play.

    Measured over 52 staff-views of the 26-movement reference corpus: a staff
    uses **3-10 distinct written durations (median 6.5)** and its commonest
    value covers **34%-95% of attacks (median 51%, p90 80%)**.

    That corpus is Classical, and a single global bound taken from it rejects
    real Chopin. Re-measured against 56 canonical movements, the shipped
    thresholds (share >= 0.96 or distinct <= 2) fire on:

        mozart sonatas (kern)       0/14    0%
        beethoven sonatas (kern)    0/14    0%
        chopin mazurkas (kern)      4/14   29%      <-- real notation, not MIDI
        chopin preludes (MIDI)      7/14   50%

    20% overall, against a docstring that claimed the bound was "set above the
    measured maximum". The docstring even says "a Chopin mazurka accompaniment
    really is 95% one value" — and then sets the bound at 96%, which four
    mazurkas exceed. A mazurka left hand is a repeated oom-pah-pah; that is the
    dance, not a poverty of rhythm.

    So the bounds are the COMPOSER'S OWN, exactly as
    `detect_accompaniment_vocabulary_poverty` next door already does for the
    same reason. A detector that cries wolf on a third of real Chopin does more
    harm than one that says nothing: the critic reads these before deciding what
    to revise, and a warning that is wrong that often teaches it to discount the
    ones that are right.

    Per-composer bounds were not enough on their own, because the finding was
    then decided by whichever ONE staff tripped a 95th-percentile bound — see the
    aggregation note in the body. Measured over real scores, before and after
    fixing that:

        palestrina  26% -> 5%      monteverdi  30% -> 13%
        haydn       22% -> 0%      bach        15% -> 0%
        mozart       8% -> 0%
    """
    bounds = _rhythm_vocabulary_bounds(composer) if composer else None
    max_share, min_distinct = bounds or (_RHYTHM_SHARE_CEILING, _RHYTHM_DISTINCT_FLOOR)
    # The corpus bar records hold a TWO-HAND reduction, so a corpus "staff" is an
    # aggregate of however many real voices were folded into that hand. Folding
    # voices together can only add note values, never remove them, so a floor
    # read off that view sits above what a single real staff does: Monteverdi's
    # corpus floor is 5 distinct values while his real madrigal parts reach 4.
    # One value of slack is the measured size of that view mismatch.
    min_distinct = max(1, min_distinct - 1)
    tripped: List[Dict[str, Any]] = []
    staves_measured = 0
    for staff in sorted({b["staff"] for b in bars}):
        recs = [b for b in bars if b["staff"] == staff]
        durs = [d for b in recs for d in b["durations"]]
        if len(durs) < 40:
            continue
        staves_measured += 1
        counts = Counter(durs)
        top_val, top_n = counts.most_common(1)[0]
        share = top_n / len(durs)
        distinct = len(counts)
        if share > max_share or distinct < min_distinct:
            tripped.append(
                _finding(
                    "rhythm_vocabulary_poverty",
                    recs[0]["bar"] if recs else None,
                    _WARN,
                    f"Staff {staff}: {distinct} distinct note values, and one value covers "
                    f"{round(share * 100)}% of all attacks — beyond "
                    f"{composer or 'the reference corpus'}'s own "
                    f"{round(max_share * 100)}%/{min_distinct}. The rhythm has one gear.",
                    "Mix the values inside the bar the way speech mixes syllable lengths: "
                    "a long note followed by a run, a dotted pair, a rest where the ear "
                    "expects a note.",
                    distinct_durations=distinct,
                    dominant_share=round(share, 3),
                )
            )
    # "The rhythm has one gear" is a claim about the PIECE, and it was being
    # decided by whichever single staff happened to trip. Because the bounds are
    # a 95th/5th percentile, roughly one real staff in ten trips by construction,
    # so the piece-level false-positive rate compounded with the staff count:
    # ~8% on two-staff Mozart but 26% on a five-voice Palestrina motet, which is
    # backwards — the polyphony most likely to be judged is the least able to
    # survive the judgement. Requiring a majority of staves measures the claim at
    # the scale the claim is made.
    if len(tripped) <= staves_measured / 2:
        return []
    return tripped[:cap]


_LH_VOCAB_CACHE: Dict[str, Any] = {}


def _shape_vocabulary_floor(composer: str, hand: str = "lh") -> Optional[int]:
    """The 5th-percentile count of distinct bar-shapes for this composer's own
    movements, on the given hand. None when unmeasurable.

    Measured for BOTH hands. The detector originally looked only at the
    accompaniment, on the reasoning that a melody repeating its shape is a style
    (Chopin's most-common melody shape covers 18% of bars at the median and 84%
    at the 95th percentile — he really does repeat). But the floor is real:
    across 85 real Chopin movements the 5th percentile is 6 distinct melody
    shapes, and a melody below that has stopped being a melody.
    """
    cache_key = f"{composer}/{hand}"
    if cache_key in _LH_VOCAB_CACHE:
        return _LH_VOCAB_CACHE[cache_key]
    floor = None
    try:
        from collections import defaultdict

        from .composition_brief import _iter_corpus_bars

        per = defaultdict(list)
        field = "lh_display" if hand == "lh" else "rh_display"
        for bar in _iter_corpus_bars(composer):
            ev = bar.get(field) or []
            # NOTES ONLY, and (duration, chord-size) — the score side reads
            # `durations`/`chord_sizes`, which exclude rests, so the corpus side
            # must exclude them too or the floor is measured on a different
            # quantity than the thing compared against it.
            sig = tuple(
                (
                    round(float(e.get("dur") or 0), 3),
                    len(e.get("pitches") or ()) if e.get("type") == "chord" else 1,
                )
                for e in ev
                if isinstance(e, dict) and e.get("type") != "rest"
            )
            if sig:
                per[bar.get("source")].append(sig)
        vals = sorted(len(Counter(v)) for v in per.values() if len(v) >= 30)
        if len(vals) >= 8:
            floor = vals[int(0.05 * (len(vals) - 1))]
    except Exception:
        floor = None
    _LH_VOCAB_CACHE[cache_key] = floor
    return floor


def _accompaniment_vocabulary_floor(composer: str) -> Optional[int]:
    """Back-compatible alias for the accompaniment hand."""
    return _shape_vocabulary_floor(composer, "lh")


def detect_accompaniment_vocabulary_poverty(
    bars: List[Dict[str, Any]], composer: str = "", melody_staff: int = 0, staff_count: int = 2
):
    """How MANY different shapes the accompaniment knows, not how often it
    repeats its favourite.

    Found by reading a finished score rather than measuring it. The left hand of
    a B-flat andante used 9 distinct bar-shapes across 41 bars; its
    most-common-shape share was 24%, sitting exactly on Mozart's median of 25%,
    so `accompaniment_monoculture` had nothing to say. Real Mozart movements use
    **16-43 shapes (median 27, p10 16)**. The hand was not monotonous — it was
    working from a tiny vocabulary, which is a different defect and reads as
    "lacks texture".

    The threshold has to be COMPOSER-RELATIVE. Chopin's mazurka accompaniments
    genuinely run on 3-11 shapes (median 11, p05 4), so any fixed bound taken
    from Mozart would reject most of real Chopin. Measured across 253 movements
    of five composers, an absolute floor of 6 fires on 3.6% of them and is used
    only when the composer's own distribution is unavailable.
    """
    out: List[Dict[str, Any]] = []
    staves = sorted({b["staff"] for b in bars})
    accomp = [st for st in staves if st != melody_staff]
    checks = [("lh", accomp[0])] if accomp else []
    if melody_staff in staves:
        checks.append(("rh", melody_staff))
    for hand, st in checks:
        out += _vocabulary_for_hand(bars, st, hand, composer, staff_count=staff_count)
    return out


def _vocabulary_for_hand(bars, st, hand, composer, staff_count: int = 2):
    out: List[Dict[str, Any]] = []
    recs = [b for b in bars if b["staff"] == st]
    if len(recs) < 24:
        return out

    shapes = Counter()
    for b in recs:
        sig = tuple(zip(b.get("durations") or (), b.get("chord_sizes") or ()))
        if sig:
            shapes[sig] += 1
    distinct = len(shapes)
    if not distinct:
        return out

    floor = _shape_vocabulary_floor(composer, hand) if composer else None
    basis = f"{composer}'s own 5th percentile" if floor is not None else "an absolute floor"
    if staff_count != 2:
        # The corpus floor is counted on a TWO-HAND reduction, where each "hand"
        # is however many voices were folded into it. Folding can only add
        # shapes, so the floor describes an ensemble, not a part. Measured on
        # real single staves: Mozart quartets reach 12 distinct shapes, Haydn 10,
        # Monteverdi 6, Palestrina 5, against corpus floors of 20/12/14/13 — so
        # the floor rejected 24-29% of real ensemble movements for owning one
        # voice's worth of vocabulary. 4 sits below the real minimum of 5 across
        # 66 ensemble movements, and still catches a part with three shapes.
        floor = 4
        basis = "the measured minimum for a single ensemble part"
    elif floor is None:
        floor = 6
    if distinct >= floor:
        return out
    what = "accompaniment" if hand == "lh" else "melody"
    return [
        _finding(
            f"{what}_vocabulary_poverty",
            recs[0]["bar"] if recs else None,
            _WARN,
            f"The {what} uses only {distinct} distinct bar-shapes across "
            f"{len(recs)} bars — below {floor} ({basis}). It is not repeating one "
            f"figure; it simply does not know many.",
            "Bring in shapes the hand has not used yet — a walking bass, an "
            "offbeat chord pair, a held pedal under a moving inner voice, a bar "
            "of octaves, a bar of silence under a solo line. Vocabulary is a "
            "different thing from variation.",
            distinct_shapes=distinct,
            floor=floor,
        )
    ]


def detect_syncopation_absence(bars: List[Dict[str, Any]], cap: int = 1, composer: str = ""):
    """Every attack on the beat, in every bar, for the whole piece.

    Reference corpus: off-beat and off-subdivision attacks are 12-45% of all
    attacks in Mozart and 18-52% in Chopin. A piece where essentially every
    onset lands on a beat is metrically flat, and metrical flatness is one of
    the most reliable signals that music was generated rather than felt.

    That premise holds from the Baroque onward and is false for Renaissance
    vocal polyphony, where the rhythmic unit is the minim and the characteristic
    displacement — the suspension — is a whole beat, so it lands ON a beat.
    Measured off-beat share of all attacks, over real scores:

        mozart      median 47%   min 29%     below the 5% floor   0/12
        haydn       median 48%   min  8%                          0/9
        bach        median 24%   min  0%                          1/20   5%
        monteverdi  median  3%   min  0%                         16/30  53%
        palestrina  median  0.4% min  0%                         39/40  98%

    So the detector was telling 98% of real Palestrina that it had been
    generated rather than felt. A composer-derived floor does not rescue it:
    the corpus bar records fold several voices into two hands, which manufactures
    off-beat onsets that the score does not have (Mozart reads 63% there against
    47% in the score), so a floor taken from that view sits ABOVE what real works
    do and starts rejecting Mozart instead. The honest move is to withhold a
    judgement the evidence does not support, and leave the detector exactly as
    calibrated everywhere it was validated.
    """
    for style in style_registry.styles_for_composer((composer or "").lower()):
        if style == "renaissance":
            return []
    onsets = [o for b in bars for o in b["onsets"]]
    if len(onsets) < 60:
        return []
    off = sum(1 for o in onsets if abs(o - round(o)) > 1e-6)
    share = off / len(onsets)
    if share >= 0.05:
        return []
    return [
        _finding(
            "syncopation_absent",
            None,
            _WARN,
            f"{round(share * 100)}% of attacks fall off the beat. Every note in the piece "
            f"lands squarely on a beat.",
            "Let something arrive late or early: an anticipation before the downbeat, a "
            "suspension that resolves on the second half of the beat, an accompaniment "
            "figure that enters on the off-beat.",
            offbeat_share=round(share, 4),
        )
    ][:cap]


def detect_uniform_phrase_lengths(phrase_lengths: Sequence[int]) -> List[Dict[str, Any]]:
    """Every phrase exactly the same number of bars.

    Four-bar phrases are the Classical default and a piece built entirely from
    them is not wrong — but a piece in which *no* phrase is ever extended,
    elided or interrupted has no rhythm at the level above the bar. Reference
    corpus: Mozart sonata expositions run 2-3 distinct phrase lengths.
    """
    lens = [int(x) for x in phrase_lengths if x]
    if len(lens) < 4:
        return []
    if len(set(lens)) > 1:
        return []
    return [
        _finding(
            "uniform_phrase_lengths",
            None,
            _WARN,
            f"All {len(lens)} phrases are exactly {lens[0]} bars long. The music never "
            f"stretches, contracts or overruns a phrase.",
            "Extend one phrase by two bars to delay an arrival, elide one into the next so "
            "the cadence lands mid-phrase, or interrupt one and restart it.",
            phrase_lengths=lens,
        )
    ]


def detect_identical_phrase_openings(
    bars: List[Dict[str, Any]],
    phrase_start_bars: Sequence[int],
    cap: int = 2,
    melody_staff: int = 0,
):
    """Every phrase starting with the same figure.

    A returning head-motif is the point of a theme; a piece where every phrase,
    including the contrasting ones, opens identically has no contrast at all.

    Measured over 242 real movements (mozart, beethoven, chopin, haydn), taking
    the bars the corpus marks `opening`: median share 0.33, p90 0.58, and the
    0.75 bound fires on 7% — the same false-positive rate the cadence bounds
    carry. Bound unchanged; recorded here because until now it had never been
    run on a real score at all (see `test_phrase_bound_detectors_calibration`).

    The staff was hardcoded to index 0, which is the melody's staff on a piano
    grand staff and is whichever part happens to be first on anything else.
    `realism_report` already resolves the melody staff from the score.
    """
    out: List[Dict[str, Any]] = []
    starts = set(int(b) for b in phrase_start_bars)
    if len(starts) < 4:
        return out
    for staff in (melody_staff,):
        recs = [b for b in bars if b["staff"] == staff and b["bar"] in starts and b["midis"]]
        if len(recs) < 4:
            continue
        counts = Counter((_rhythm_sig(r), _contour_sig(r)) for r in recs)
        sig, n = counts.most_common(1)[0]
        share = n / len(recs)
        if n >= 4 and share >= 0.75:
            where = [r["bar"] for r in recs if (_rhythm_sig(r), _contour_sig(r)) == sig]
            out.append(
                _finding(
                    "identical_phrase_openings",
                    where[0],
                    _WARN,
                    f"{n} of {len(recs)} phrases open with the identical figure (bars "
                    f"{', '.join(str(w) for w in where[:8])}) — including the ones that "
                    f"are supposed to contrast.",
                    "Keep the head-motif for the statements that mean it. Start a "
                    "contrasting phrase from its answer, from the middle of the shape, "
                    "inverted, or from a different beat of the bar.",
                    opening_share=round(share, 3),
                    bars=where[:12],
                )
            )
    return out[:cap]


def detect_register_stasis(
    bars: List[Dict[str, Any]], melody_staff: int = 0, cap: int = 1, staff_count: int = 2
):
    """The melody living inside one narrow band for the whole piece.

    Measured over the 26-movement reference corpus (movements of 24+ bars): the
    melody staff spans **24 to 49 semitones, median 32.5**. The narrowest real
    movement in the corpus is Chopin's Op.33 No.1 mazurka at exactly two
    octaves; nothing canonical is narrower than that.

    The bound this shipped with was 17 semitones — comfortably below anything
    real, and therefore below the generated output it was written to catch: the
    baseline andante spanned **19 semitones across 41 bars**, five short of the
    narrowest real movement, and this detector said nothing. Register is one of
    the few structural devices that survives any listening condition; a piece
    that never uses it sounds like it is being played through a keyhole.

    Two octaves is a piano melody's range. It is more than a singer HAS: a
    Palestrina cantus lives inside a ninth or a tenth, and the ensemble gets its
    register from the other voices, not from that one. So this fired on 100% of
    real Palestrina and 68% of real Monteverdi, faulting each part for the range
    of the human throat. Gated to the grand staff for the same reason as
    `detect_voicing_poverty` above; on an ensemble the span that matters belongs
    to the whole texture, which is not what this measures.
    """
    if staff_count != 2:
        return []
    tops = [t for b in bars if b["staff"] == melody_staff for t in b["tops"]]
    n_bars = len({b["bar"] for b in bars if b["staff"] == melody_staff})
    if len(tops) < 40 or n_bars < 24:
        return []
    span = max(tops) - min(tops)
    # 24 semitones = the narrowest canonical movement in the corpus.
    if span >= 24:
        return []
    return [
        _finding(
            "register_stasis",
            None,
            _WARN,
            f"The melody spans {span} semitones across {n_bars} bars — narrower than "
            f"any of the 26 canonical movements measured, whose minimum is 24. It never "
            f"leaves one register, so nothing sounds high or low relative to anything else.",
            "Use register structurally: open lower than the peak, lift an octave at the "
            "return, drop into the tenor for the darkest phrase.",
            span_semitones=span,
        )
    ][:cap]


def detect_scalar_overuse(
    bars: List[Dict[str, Any]], melody_staff: int = 0, cap: int = 3, composer: str = ""
):
    """Bars whose melody is a plain unbroken scale.

    A scale is a figure, not a melody. The baseline score had eight bars that
    were pure stepwise runs in one direction, several of them a full octave.
    Reference corpus: whole-bar unbroken scale runs are 0-9% of melody bars in
    Mozart and 0-14% in Beethoven (études excluded), so the bound was 0.25.

    Re-measured on real scores, that bound sat *inside* the real distribution
    rather than above it — share of whole-bar scale runs on the melody staff:

        piano reference corpus   median 0.016   max 0.247
        mozart (quartets)        median 0.027   max 0.239
        monteverdi               median 0.062   max 0.269      1/13 over 0.25
        haydn (quartets)         median 0.053   max 0.286      2/9  over 0.25
        palestrina               median 0.231   max 0.438      4/11 over 0.25

    Palestrina's MEDIAN movement sits at the old bound, because conjunct motion
    is what Renaissance vocal polyphony is made of — the line is designed to be
    singable, and a singer reads steps. Calling that a figure rather than a
    melody is a category error. So the bound is now set above what real music
    does, with the Renaissance given the ceiling its own repertoire needs.
    """
    ceiling = 0.30
    for style in style_registry.styles_for_composer((composer or "").lower()):
        if style == "renaissance":
            ceiling = 0.50
            break
    recs = [b for b in bars if b["staff"] == melody_staff and len(b["tops"]) >= 4]
    if len(recs) < 12:
        return []

    def _is_scale(rec) -> bool:
        ivs = _contour_sig(rec)
        if len(ivs) < 3:
            return False
        # Every step 1-2 semitones, all the same direction.
        return all(0 < abs(i) <= 2 for i in ivs) and (
            all(i > 0 for i in ivs) or all(i < 0 for i in ivs)
        )

    scalar = [r["bar"] for r in recs if _is_scale(r)]
    share = len(scalar) / len(recs)
    if share < ceiling:
        return []
    return [
        _finding(
            "scalar_overuse",
            scalar[0],
            _WARN,
            f"{len(scalar)} of {len(recs)} melody bars ({round(share * 100)}%) are plain "
            f"unbroken scale runs (bars {', '.join(str(b) for b in scalar[:8])}).",
            "A scale fills time without saying anything. Break the run with a leap and a "
            "gap-fill, turn back on itself, or give it a rhythmic profile instead of even "
            "values.",
            scalar_share=round(share, 3),
            bars=scalar[:12],
        )
    ][:cap]


def detect_closing_gesture_absence(bars: List[Dict[str, Any]], cap: int = 1):
    """A final bar with no sign that it is the last one.

    Calibration note: the bound this shipped with fired on **8 of 26** canonical
    movements, for two reasons. It read the highest-numbered measure, which in
    the reference corpus is often an empty barline artifact of the Humdrum
    import; and it required an absolute duration of 3 quarter-notes, which no
    ending in 2/4 can meet. Measured properly over the corpus, the last
    *sounding* bar has a longest value of 0.0-3.0 quarters and a widest chord of
    0-5 notes — real endings genuinely can be short and thin, so this is `info`.

    It fires only when the ending is unmarked on **every** axis at once: no
    fermata, no closing direction, no thickened chord, no value reaching half a
    bar, and a final bar whose rhythm is one the piece has already used
    elsewhere. That last clause is what separates "a deliberately curt ending"
    from "the generator simply stopped".
    """
    if not bars:
        return []
    n_bars = len({b["bar"] for b in bars})
    if n_bars < 12:
        return []
    # The last bar that actually SOUNDS — trailing empty barline measures are an
    # import artifact, not an ending.
    sounding = [b["bar"] for b in bars if b["midis"]]
    if not sounding:
        return []
    last = max(sounding)
    recs = [b for b in bars if b["bar"] == last]
    if not recs:
        return []
    has_ferm = any("Fermata" in o for r in recs for o in r["ornaments"])
    has_text = any(r["texts"] for r in recs)
    widest_chord = max((max(r["chord_sizes"]) if r["chord_sizes"] else 0) for r in recs)
    longest = max((max(r["durations"]) if r["durations"] else 0) for r in recs)
    bar_beats = max((r.get("bar_beats") or 4.0) for r in recs)
    if has_ferm or has_text or widest_chord >= 3 or longest >= bar_beats / 2:
        return []
    # Is the closing rhythm one the piece already used? If it is unique, the
    # ending is at least distinct, whatever else it lacks.
    final_sig = tuple(sorted(_rhythm_sig(r) for r in recs))
    earlier = {
        tuple(sorted(_rhythm_sig(b) for b in bars if b["bar"] == bn))
        for bn in sounding
        if bn != last
    }
    if final_sig not in earlier:
        return []
    return [
        _finding(
            "closing_gesture_absent",
            last,
            _INFO,
            f"The final bar ({last}) carries no sign of being the end — no fermata, no "
            f"held value, no thickened chord, no closing direction — and its rhythm is "
            f"one already used earlier in the piece. It stops rather than ends.",
            "Give the last bar the weight of an ending: a fuller final chord (add the "
            "octave below and the third above), a fermata or a held whole note, and a "
            "closing direction if the style takes one.",
            final_bar=last,
        )
    ][:cap]


# The 2nd percentile of attacks-per-bar spread measured across 1,853 real
# movements from ten composers. Firing above this reports normal music.
_TEXTURE_SPREAD_FLOOR = 0.03


def detect_texture_stasis_across_sections(
    bars: List[Dict[str, Any]],
    section_spans: Sequence[Tuple[str, int, int]],
    cap: int = 2,
    composer: str = "",
):
    """Sections that are texturally indistinguishable from one another.

    Contrast between sections is what makes form audible — in the idioms this
    was calibrated on. It was written against Classical and Romantic piano
    music, and applied to Baroque counterpoint it is simply wrong: measured over
    268 real Bach movements, the thresholds fire on **48% of them**, because a
    chorale, an invention and a fugue hold one texture from first bar to last by
    design. That is the genre, not a defect.

    Skipped for composers whose corpus shows uniform section texture as the
    norm — measured, not declared, from that composer's own movements.
    """

    if len(section_spans) < 2:
        return []
    profile: List[Tuple[str, float, float]] = []
    for name, b0, b1 in section_spans:
        recs = [b for b in bars if b0 <= b["bar"] <= b1]
        if not recs:
            continue
        n_bars = len({r["bar"] for r in recs}) or 1
        attacks = sum(len(r["onsets"]) for r in recs) / n_bars
        thick = [s for r in recs for s in r["chord_sizes"]]
        profile.append((name, attacks, (sum(thick) / len(thick)) if thick else 1.0))
    if len(profile) < 2:
        return []
    attacks = [p[1] for p in profile]
    thicks = [p[2] for p in profile]
    a_spread = (max(attacks) - min(attacks)) / max(1e-6, sum(attacks) / len(attacks))
    t_spread = max(thicks) - min(thicks)
    # Measured over 1,853 real movements from ten composers: attacks-per-bar
    # spread runs a median of 0.171 and thickness spread a median of 0.0. The
    # bounds that shipped here — 0.25 and 0.35 — sat ABOVE both medians and
    # fired on 72% of real music (Mozart 70%, Chopin 59%, Bach 76%). Every
    # warning this ever produced was noise.
    #
    # The thickness criterion is dropped from the test entirely: with a median
    # of 0.0 it carries no information, and requiring it changed almost nothing.
    # The attacks bound is the measured 2nd percentile, which fires on 1.9%.
    if a_spread > _TEXTURE_SPREAD_FLOOR:
        return []
    return [
        _finding(
            "texture_stasis",
            None,
            _WARN,
            f"All {len(profile)} sections have effectively the same texture "
            f"(attacks/bar spread {round(a_spread * 100)}%, chord-thickness spread "
            f"{round(t_spread, 2)}). The form is not audible.",
            "Make each section sound like a different place: change what the left hand "
            "does, change how thick the right hand is, change the register, change how "
            "much silence there is.",
            sections=[
                {"section": n, "attacks_per_bar": round(a, 2), "thickness": round(t, 2)}
                for n, a, t in profile
            ],
        )
    ][:cap]


# ─── Top level ───────────────────────────────────────────────────────────────


def _count_spanners(score) -> Dict[str, int]:
    """Slur / hairpin / ottava / glissando counts off the finished score."""
    counts = {"slur": 0, "hairpin": 0, "ottava": 0, "glissando": 0}
    try:
        import music21

        for sp in score.recurse().getElementsByClass("Spanner"):
            if isinstance(sp, music21.spanner.Slur):
                counts["slur"] += 1
            elif isinstance(sp, music21.dynamics.DynamicWedge):
                counts["hairpin"] += 1
            elif isinstance(sp, music21.spanner.Ottava):
                counts["ottava"] += 1
            elif isinstance(sp, music21.spanner.Glissando):
                counts["glissando"] += 1
    except Exception:
        pass
    return counts


# The keyboard the composer actually had. A piece "in the style of Mozart"
# that reaches C7 is not in the style of Mozart: his instrument stopped at f3
# (F6), and the register limit shapes how the repertoire is written — the peak
# of a Mozart melody sits where it does partly because there was nothing above
# it. Values are (low, high) MIDI for the composer's own instrument.
#
# Advisory only, and only for keyboard writing: a user may legitimately want a
# modern-piano realization of a Classical style, and the corpus itself is
# performed on modern instruments.
_HISTORICAL_KEYBOARD = {
    # Fortepiano, FF-f3
    "mozart": (29, 89),
    "haydn": (29, 89),
    # Harpsichord / organ manuals, GG-d3
    "bach": (31, 86),
    "handel": (31, 86),
    "scarlatti": (31, 86),
    # Beethoven's range grew across his life; the late sonatas reach c4.
    "beethoven": (22, 96),
    "schubert": (22, 96),
    "weber": (22, 96),
    # By the 1830s the instrument is essentially the modern one. Chopin's
    # Pleyel and Liszt's Érard both reach into the seventh octave; the ceilings
    # here were a semitone too low and clipped a real mazurka.
    "chopin": (22, 103),
    "liszt": (21, 108),
    "style__baroque": (31, 86),
    "style__classical": (29, 89),
    "style__romantic": (22, 106),
}


def detect_out_of_period_register(
    bars: List[Dict[str, Any]], composer: str = "", cap: int = 1
) -> List[Dict[str, Any]]:
    """Notes the composer's own instrument did not have.

    Not a physical constraint — a modern piano plays them — so this never
    blocks. But a Classical pastiche whose climax sits a fourth above the top
    of Mozart's keyboard is inauthentic in a way no statistic catches, and the
    fix (take the peak down an octave, or find the range at the bottom instead)
    usually improves the music as well.
    """
    key = (composer or "").strip().lower()
    span = _HISTORICAL_KEYBOARD.get(key)
    if not span:
        return []
    low, high = span
    over = sorted({m for b in bars for m in b["midis"] if m > high})
    under = sorted({m for b in bars for m in b["midis"] if m < low})
    if not over and not under:
        return []
    import music21

    def _name(m):
        try:
            return music21.pitch.Pitch(midi=m).nameWithOctave
        except Exception:
            return str(m)

    where = [b["bar"] for b in bars if any(m > high or m < low for m in b["midis"])]
    detail = []
    if over:
        detail.append(f"{len(over)} above {_name(high)} (up to {_name(over[-1])})")
    if under:
        detail.append(f"{len(under)} below {_name(low)} (down to {_name(under[0])})")
    return [
        _finding(
            "out_of_period_register",
            where[0] if where else None,
            _WARN,
            f"Notes outside {composer}'s own keyboard ({_name(low)}-{_name(high)}): "
            + "; ".join(detail)
            + f". Bars {', '.join(str(w) for w in where[:8])}.",
            "Take the passage into the register the composer actually wrote in — "
            "usually an octave down at the top. The limits of the instrument are "
            "part of why the repertoire sounds the way it does.",
            above=len(over),
            below=len(under),
            bars=where[:12],
        )
    ][:cap]


def phrase_boundaries(graph, scope: str = "full") -> Dict[str, Any]:
    """Phrase start/end bars, lengths and section spans, read off the PieceGraph.

    The realism detectors need to know where the phrases are: "the same rhythm
    at every phrase ending" is not computable from the score alone. Bars are
    re-based the same way the assembler re-bases a partial scope, so the numbers
    line up with the bars in the assembled file.

    IT DID NOT FILTER BY SCOPE. Every phrase in the graph was collected however
    narrow the scope, so evaluating one section of a three-movement work handed
    the detectors phrase ends at bars 4, 8, 12 … 85 against an assembled file
    holding bars 1-8. Two of those ends existed, the detectors need three, and
    all four of them returned nothing — so `self_evaluate` reported a clean
    realism audit on every section of every piece, and the section gate's
    advisories were empty because the detectors could not see the music, not
    because the music was clean. A section that does not start at bar 1 was
    worse: `shift` came from the global minimum, so nothing was re-based either.

    `_in_scope` is the assembler's own answer to "is this phrase in this scope",
    and asking it is what keeps these bar numbers aligned with the file the
    detectors are reading.
    """
    from .assembler import _in_scope

    starts: List[int] = []
    ends: List[int] = []
    lengths: List[int] = []
    sections: Dict[str, List[int]] = {}
    for ps in (getattr(graph, "phrases", None) or {}).values():
        slot = getattr(ps, "slot", None)
        if slot is None or not getattr(ps, "realized", None):
            continue
        if not _in_scope(ps, scope):
            continue
        b0 = int(slot.bar_start or 1)
        n = int(slot.bar_count or 1)
        starts.append(b0)
        ends.append(b0 + n - 1)
        lengths.append(n)
        sec = slot.section_id or ""
        span = sections.setdefault(sec, [b0, b0 + n - 1])
        span[0] = min(span[0], b0)
        span[1] = max(span[1], b0 + n - 1)
    shift = (min(starts) - 1) if (starts and scope != "full") else 0
    if shift:
        starts = [b - shift for b in starts]
        ends = [b - shift for b in ends]
        sections = {k: [v[0] - shift, v[1] - shift] for k, v in sections.items()}
    return {
        "starts": sorted(starts),
        "ends": sorted(ends),
        "lengths": lengths,
        "sections": [(k, v[0], v[1]) for k, v in sorted(sections.items(), key=lambda kv: kv[1][0])],
    }


# Layer/staff names that carry the melody and the accompaniment, in PREFERENCE
# order — several parts can be melodic at once ("melody" and "foreground" both
# are), and the principal line has to win over the secondary one. Matching on
# "first part whose name is in the set" instead picks whichever happens to sort
# first, which is not a musical criterion.
_MELODY_NAMES = ("melody", "principal", "soprano", "foreground", "treble", "violin", "flute")
_ACCOMP_NAMES = ("bass", "harmony", "accompaniment", "response", "motor", "violoncello")


def identify_staves(score, bars: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Which staff index carries the melody, and which the accompaniment.

    A two-staff piano score is (0, 1) and always was. An ORCHESTRAL score is
    not: music21 hands back its parts in whatever order the exporter wrote
    them, which for a generated orchestral score is alphabetical — so staff 0
    was "Bass" and every melody detector in this module was analysing the
    double basses as the tune.

    Resolved by part name where the name is recognisable, and otherwise by
    register: the highest mean pitch is the melody, the lowest the bass.
    """
    try:
        names = [str(p.partName or p.id or "").strip().lower() for p in score.parts]
    except Exception:
        names = []
    if len(names) <= 2:
        return 0, 1 if len(names) > 1 else 0

    def _best(preferences) -> Optional[int]:
        for key in preferences:  # preference order, not part order
            for i, n in enumerate(names):
                if key in n:
                    return i
        return None

    melody = _best(_MELODY_NAMES)
    accomp = _best(_ACCOMP_NAMES)
    if melody is None or melody == accomp:
        means = {}
        for i in range(len(names)):
            mid = [m for b in bars if b["staff"] == i for m in b["midis"]]
            if mid:
                means[i] = sum(mid) / len(mid)
        if means:
            melody = max(means, key=means.get)
            accomp = min(means, key=means.get)
    return (melody if melody is not None else 0), (accomp if accomp is not None else 1)


def realism_report(
    score_path: str,
    graph=None,
    scope: str = "full",
    composer: str = "",
    melody_staff: int = 0,
    accomp_staff: int = 1,
) -> Dict[str, Any]:
    """Run every realism detector over an assembled score.

    Returns ``{findings, summary, notation_census, undetectable}``. All findings
    are advisory: this is what the fresh-ears critic reads before deciding what
    to revise, and what a regression test reads to check that a formula the
    system used to produce has not come back.
    """
    import music21

    try:
        score = music21.converter.parse(score_path)
    except Exception as exc:
        return {
            "findings": [_finding("realism_error", None, _INFO, f"could not parse: {exc}", "")],
            "summary": {"by_detector": {}, "warn_count": 0},
            "notation_census": {},
            "undetectable": [],
        }

    bars = _bar_table(score)
    spanners = _count_spanners(score)
    # Default indices are right for a piano grand staff and wrong for anything
    # with more parts — resolve them from the score itself.
    if melody_staff == 0 and accomp_staff == 1:
        melody_staff, accomp_staff = identify_staves(score, bars)
    bounds = (
        phrase_boundaries(graph, scope)
        if graph is not None
        else {"starts": [], "ends": [], "lengths": [], "sections": []}
    )

    # How many staves the music is written on. The bounds in this file were
    # measured on a 2-staff piano corpus, and a few of them describe the grand
    # staff rather than music — see detect_voicing_poverty.
    staff_count = len({b["staff"] for b in bars})

    findings: List[Dict[str, Any]] = []
    findings += detect_repeated_bars(bars)
    findings += detect_cadence_formula_reuse(bars, bounds["ends"], melody_staff=melody_staff)
    findings += detect_accompaniment_monoculture(bars, accomp_staff)
    findings += detect_notation_spam(bars)
    findings += detect_articulation_absence(bars, composer=composer)
    findings += detect_tie_absence(bars)
    findings += detect_dynamic_poverty(bars, spanners["hairpin"], composer=composer)
    findings += detect_voicing_poverty(bars, melody_staff, staff_count=staff_count)
    # `composer` selects WHICH corpus this is judged against. Omitting it here
    # would silently fall back to the cross-composer bounds and judge a mazurka
    # by them — the same optional-parameter trap that has already produced two
    # defects in this codebase today.
    findings += detect_rhythm_vocabulary_poverty(bars, composer=composer)
    findings += detect_accompaniment_vocabulary_poverty(
        bars, composer=composer, melody_staff=melody_staff, staff_count=staff_count
    )
    findings += detect_syncopation_absence(bars, composer=composer)
    findings += detect_uniform_phrase_lengths(bounds["lengths"])
    findings += detect_identical_phrase_openings(bars, bounds["starts"], melody_staff=melody_staff)
    # The mirror of the two above: everything else in this file catches too much
    # sameness, and a piece where nothing recurs passes all of them.
    findings += detect_no_recurring_material(
        bars, bounds["starts"], bounds["ends"], melody_staff=melody_staff
    )
    findings += detect_register_stasis(bars, melody_staff, staff_count=staff_count)
    findings += detect_scalar_overuse(bars, melody_staff, composer=composer)
    findings += detect_closing_gesture_absence(bars)
    findings += detect_texture_stasis_across_sections(bars, bounds["sections"], composer=composer)
    findings += detect_out_of_period_register(bars, composer)

    n_bars = len({b["bar"] for b in bars}) or 1
    census = {
        "bars": n_bars,
        "notes": sum(len(b["onsets"]) for b in bars),
        "articulations": sum(len(b["articulations"]) for b in bars),
        "ornaments": sum(len(b["ornaments"]) for b in bars),
        "ties": sum(b["ties"] for b in bars),
        "graces": sum(b["graces"] for b in bars),
        "dynamics": sum(len(b["dynamics"]) for b in bars),
        "texts": sum(len(b["texts"]) for b in bars),
        "rests": sum(b["rests"] for b in bars),
        **spanners,
    }
    census["marks_per_bar"] = round(
        (
            census["articulations"]
            + census["ornaments"]
            + census["dynamics"]
            + census["slur"]
            + census["hairpin"]
            + census["ties"]
        )
        / n_bars,
        2,
    )

    by_det: Dict[str, int] = {}
    for f in findings:
        by_det[f["detector"]] = by_det.get(f["detector"], 0) + 1
    return {
        "findings": findings,
        "summary": {
            "by_detector": by_det,
            "warn_count": sum(1 for f in findings if f["severity"] == _WARN),
            "info_count": sum(1 for f in findings if f["severity"] == _INFO),
        },
        "notation_census": census,
        "undetectable": [
            "whether the theme is memorable",
            "whether the harmony is beautiful rather than merely correct",
            "whether the piece is worth hearing twice",
        ],
    }
