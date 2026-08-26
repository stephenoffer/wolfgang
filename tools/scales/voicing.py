"""
Texture and voicing analysis — how thick, how wide, how varied.

The recurring complaint about this system's output is that it is *thin*: a
single-note tune over a repeating figure, in one register, for the whole piece.
That was diagnosed once by hand (the right hand averaged 1.25 notes per attack;
hand-composing the same piece with real chord voicings took it to 2.02 and the
critic called the result "a real and substantial improvement") but nothing
measures it, so nothing prevents it coming back.

Nothing in the system answered these questions:

* How many notes sound at once, and does that number ever change?
* How much of the keyboard does the piece use, and does the register move?
* Is the right hand a single line, or does it ever sing in thirds and sixths?
* Where does the texture actually change, and is the change musical or an
  artefact of counting notes?

``corpus_metrics.texture_change_pct`` claims to answer the last one but is
computed off note-count deltas between adjacent bars, which is meter- and
tempo-blind and cannot tell a change of idiom from a busier bar of the same
idiom. The measurements here are about the *sound*: simultaneity, span,
register, and what the hands are actually doing.

Everything here is descriptive. There are no thresholds that block: the
suggestions at the end are written for a composer to read and disagree with.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from statistics import mean, pstdev
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .counterpoint import attack_times, extract_voices, sounding_at

# ─── Registers ───────────────────────────────────────────────────────────────
#
# Named by how they sound at the piano, not by octave number, because that is
# how a composer thinks about them.

_REGISTERS: List[Tuple[str, int, int]] = [
    ("sub_bass", 21, 40),  # A0-E2
    ("bass", 41, 52),  # F2-E3
    ("tenor", 53, 60),  # F3-C4
    ("alto", 61, 71),  # C#4-B4
    ("soprano", 72, 83),  # C5-B5
    ("high", 84, 95),  # C6-B6
    ("brilliant", 96, 108),  # C7-C8
]


def register_of(midi: int) -> str:
    for name, lo, hi in _REGISTERS:
        if lo <= midi <= hi:
            return name
    return "sub_bass" if midi < 21 else "brilliant"


_PIANO_MELODIC = ("principal_line", "counter_reply")
_PIANO_ACCOMP = ("bass_foundation", "response_layer")


# ─── Measured corpus baselines ───────────────────────────────────────────────
#
# Taken by running the measurements in this module over 22 real movements
# (Mozart sonatas, Beethoven sonatas, Chopin mazurkas), 64 bars each. They are
# here so the thresholds below are *observed* rather than guessed, and so a
# reader can see what "normal" actually is.
#
#                       rh/attack   lh/attack   simult   single-RH%  span  shift   CV    3rds
#   Mozart      median     1.22        1.48       2.33      0.62      51   0.61   0.33   0.07
#               range   1.14-1.58   1.15-1.62  1.97-2.68  0.39-0.80  41-57 .47-.77 .21-.41
#   Beethoven   median     1.58        1.62       2.91      0.41      57   0.61   0.40   0.16
#               range   1.19-2.20   1.09-1.85  2.36-3.82  0.06-0.71  53-58 .36-.72 .32-.50
#   Chopin      median     1.70        1.89       3.79      0.22      55   0.50   0.19   0.25
#               range   1.30-2.43   1.06-2.57  3.36-4.06  0.05-0.58  50-67 .27-.75 .17-.30
#
# Re-measured after fixing a bug in this module's own hand assignment: the voice
# namer produces both "principal_line#1" (a chord member) and "principal_line@1"
# (an overlapping strand), and `_hand_of` stripped only the "#". Every strand of
# a melody overlapping itself — which is most sustained melodic writing — was
# therefore counted as a left-hand note. It shifted the right-hand figures down
# and the left-hand ones up, and put phantom 17-semitone stretches in the left
# hand of real Chopin.
#
# Two things this refuted, and they are worth stating because both were assumed:
# a generated piece measured at 1.13 RH notes per attack looked "thin" next to
# the hand-composed 2.02 that once fixed a different piece — but real Mozart's
# median is 1.15, so that piece's right hand was not thin at all. And its
# texture-change rate of 0.62 sits comfortably inside Mozart's 0.37-0.67. What
# WAS outside the repertoire's range was its simultaneity CV: 0.19 against a
# real-score minimum of 0.16 and a Mozart minimum of 0.22 — the texture never
# thickens or thins. That is the finding the numbers actually support.
CORPUS_TEXTURE = {
    "classical": {
        "rh_notes_per_attack": 1.22,
        "lh_notes_per_attack": 1.48,
        "mean_simultaneity": 2.33,
        "single_line_rh_pct": 0.62,
        "register_span": 51,
        "texture_shift_pct": 0.61,
        "simultaneity_cv": 0.33,
        "thirds_sixths_pct": 0.07,
    },
    "romantic": {
        "rh_notes_per_attack": 1.70,
        "lh_notes_per_attack": 1.89,
        "mean_simultaneity": 3.79,
        "single_line_rh_pct": 0.22,
        "register_span": 55,
        "texture_shift_pct": 0.50,
        "simultaneity_cv": 0.19,
        "thirds_sixths_pct": 0.25,
    },
}

# Floors set BELOW the minimum any of the 22 real movements reached, so a
# suggestion means "outside the repertoire", not "below average". A rule tuned
# to the median would fire on half of Mozart.
_FLOOR = {
    "rh_notes_per_attack": 1.12,  # real minimum 1.14
    "lh_notes_per_attack": 1.04,  # real minimum 1.06
    "single_line_rh_pct": 0.84,  # real maximum 0.80
    "register_span": 38,  # real minimum 41
    "texture_shift_low": 0.24,  # real minimum 0.27
    "texture_shift_high": 0.80,  # real maximum 0.77
    "simultaneity_cv": 0.15,  # real minimum 0.17 (Chopin; Mozart never below 0.21)
    "thirds_sixths_pct": 0.02,  # real minimum 0.03
    "registers_used": 4,  # real minimum 5
}

# Per-style tightenings, where one period's observed range is meaningfully
# narrower than the union. Judging a Classical piece against Chopin's floor
# lets through a texture that no Classical movement ever has: Mozart's
# simultaneity CV never drops below 0.22, but Chopin's reaches 0.16, so the
# union floor of 0.14 is blind to a Mozart pastiche whose texture never moves.
_STYLE_FLOOR = {
    "classical": {"simultaneity_cv": 0.19, "lh_notes_per_attack": 1.13},
    "baroque": {"simultaneity_cv": 0.14},
    "romantic": {"rh_notes_per_attack": 1.18, "thirds_sixths_pct": 0.05},
}

# Composer -> period, so a caller can pass either. Kept in sync with
# expression_enricher._COMPOSER_PERIOD by way of the shared helper below.
def _period_of(style: Optional[str]) -> Optional[str]:
    """Resolve a composer/style/period name to a period key, or None."""
    if not style:
        return None
    from .expression_enricher import resolve_style

    name = resolve_style(style).name
    return name if name in ("classical", "baroque", "romantic", "impressionist") else None


def floors_for(style: Optional[str] = None) -> Dict[str, float]:
    """The suggestion floors in force, with any per-style tightening applied."""
    out = dict(_FLOOR)
    period = _period_of(style)
    if period and period in _STYLE_FLOOR:
        out.update(_STYLE_FLOOR[period])
    return out


# ─── Report ──────────────────────────────────────────────────────────────────


@dataclass
class BarTexture:
    bar: int
    attacks: int = 0
    notes: int = 0
    max_simultaneity: int = 0
    mean_simultaneity: float = 0.0
    rh_notes_per_attack: float = 0.0
    lh_notes_per_attack: float = 0.0
    span: int = 0  # semitones, lowest to highest
    low: int = 0
    high: int = 0
    registers: Tuple[str, ...] = ()
    rh_is_single_line: bool = True
    has_rest: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "bar": self.bar,
            "attacks": self.attacks,
            "notes": self.notes,
            "max_simultaneity": self.max_simultaneity,
            "mean_simultaneity": round(self.mean_simultaneity, 2),
            "rh_notes_per_attack": round(self.rh_notes_per_attack, 2),
            "lh_notes_per_attack": round(self.lh_notes_per_attack, 2),
            "span": self.span,
            "registers": list(self.registers),
            "rh_single_line": self.rh_is_single_line,
        }


@dataclass
class VoicingReport:
    bars: List[BarTexture] = field(default_factory=list)
    # Whole-piece summary
    mean_simultaneity: float = 0.0
    rh_notes_per_attack: float = 0.0
    lh_notes_per_attack: float = 0.0
    single_line_rh_pct: float = 0.0
    register_span: int = 0
    registers_used: Tuple[str, ...] = ()
    span_range: Tuple[int, int] = (0, 0)
    texture_shift_pct: float = 0.0
    simultaneity_cv: float = 0.0
    widest_hand_span: int = 0
    unplayable_spans: List[Tuple[int, float, int]] = field(default_factory=list)
    thirds_sixths_pct: float = 0.0
    style: str = ""
    suggestions: List[str] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)

    def as_dict(self, per_bar: bool = False) -> Dict[str, Any]:
        out = {
            "mean_simultaneity": round(self.mean_simultaneity, 2),
            "rh_notes_per_attack": round(self.rh_notes_per_attack, 2),
            "lh_notes_per_attack": round(self.lh_notes_per_attack, 2),
            "single_line_rh_pct": round(self.single_line_rh_pct, 3),
            "register_span_semitones": self.register_span,
            "registers_used": list(self.registers_used),
            "bar_span_min_max": list(self.span_range),
            "texture_shift_pct": round(self.texture_shift_pct, 3),
            "simultaneity_cv": round(self.simultaneity_cv, 3),
            "widest_hand_span": self.widest_hand_span,
            "unplayable_spans": self.unplayable_spans[:10],
            "thirds_sixths_pct": round(self.thirds_sixths_pct, 3),
            "style": self.style,
            "observations": self.observations,
            "suggestions": self.suggestions,
        }
        if per_bar:
            out["bars"] = [b.as_dict() for b in self.bars]
        return out


# ─── Measurement ─────────────────────────────────────────────────────────────


def _hand_of(voice: str) -> str:
    """Which hand plays this voice.

    Both suffixes have to come off. ``extract_voices`` names a chord's members
    ``principal_line#0``, ``#1`` … and an overlapping strand of one layer
    ``principal_line@1``. Stripping only ``#`` left ``principal_line@1``
    unmatched, so it fell through to the left hand — and every strand of a
    melody that overlaps itself (a held note under its own continuation, which
    is most sustained melodic writing) was counted as an accompaniment note. It
    corrupted the right-hand and left-hand density measurements and put phantom
    17-semitone stretches in the left hand of real Chopin.
    """
    base = voice.split("#")[0].split("@")[0]
    if base in _PIANO_MELODIC or base in ("foreground", "countermelody") or base.startswith(
        "treble"
    ):
        return "rh"
    return "lh"


def measure_bars(layer_ir) -> List[BarTexture]:
    """Per-bar texture measurements taken from what actually sounds."""
    spans = extract_voices(layer_ir, ignore_ornamental=True)
    if not spans:
        return []
    times = attack_times(spans)
    per_bar: Dict[int, BarTexture] = {}
    sim_by_bar: Dict[int, List[int]] = {}
    rh_by_bar: Dict[int, List[int]] = {}
    lh_by_bar: Dict[int, List[int]] = {}
    pitches_by_bar: Dict[int, List[int]] = {}

    for t in times:
        state = sounding_at(spans, t)
        if not state:
            continue
        # Attribute the moment to the bar of the notes that START here.
        starting = [s for s in state.values() if s.start == t]
        bar = min((s.bar for s in starting), default=min(s.bar for s in state.values()))
        bt = per_bar.setdefault(bar, BarTexture(bar=bar))
        bt.attacks += 1
        bt.notes += len(starting)
        sim_by_bar.setdefault(bar, []).append(len(state))
        rh = [s for v, s in state.items() if _hand_of(v) == "rh" and s.start == t]
        lh = [s for v, s in state.items() if _hand_of(v) == "lh" and s.start == t]
        if rh:
            rh_by_bar.setdefault(bar, []).append(len(rh))
        if lh:
            lh_by_bar.setdefault(bar, []).append(len(lh))
        pitches_by_bar.setdefault(bar, []).extend(s.midi for s in state.values())

    out: List[BarTexture] = []
    for bar in sorted(per_bar):
        bt = per_bar[bar]
        sims = sim_by_bar.get(bar) or [0]
        bt.max_simultaneity = max(sims)
        bt.mean_simultaneity = mean(sims)
        rh = rh_by_bar.get(bar) or []
        lh = lh_by_bar.get(bar) or []
        bt.rh_notes_per_attack = mean(rh) if rh else 0.0
        bt.lh_notes_per_attack = mean(lh) if lh else 0.0
        bt.rh_is_single_line = bt.rh_notes_per_attack <= 1.05
        ps = pitches_by_bar.get(bar) or [0]
        bt.low, bt.high = min(ps), max(ps)
        bt.span = bt.high - bt.low
        bt.registers = tuple(sorted({register_of(p) for p in ps}))
        out.append(bt)
    return out


def _hand_spans(layer_ir) -> List[Tuple[int, float, int]]:
    """Widest reach a hand is actually asked to make: (bar, beat, semitones).

    Only notes **struck together** count. An earlier version counted everything
    *sounding* together, on the reasoning that a note sustained under a later one
    is the commonest way a stretch appears — and that was wrong in a way real
    music settles immediately: a low bass note held under a chord the hand plays
    higher up is the ordinary pedal-point idiom, released by the fingers and held
    by the pedal. Measured with that rule, real Mozart, Beethoven and Chopin
    produced **211 "unplayable" stretches across 1,027 bars**, with a median
    widest span of 28 semitones — an octave and a half, which no hand spans and
    every pianist plays.

    A simultaneous attack is a different matter: those notes have to be under the
    fingers at the same instant, and a tenth is already a stretch.
    """
    spans = extract_voices(layer_ir)
    out: List[Tuple[int, float, int]] = []
    for t in attack_times(spans):
        for hand in ("rh", "lh"):
            struck = [
                s
                for s in spans
                if s.start == t and _hand_of(s.voice) == hand
            ]
            if len(struck) < 2:
                continue
            lo = min(struck, key=lambda s: s.midi)
            hi = max(struck, key=lambda s: s.midi)
            out.append((lo.bar, lo.beat, hi.midi - lo.midi))
    return out


def _thirds_and_sixths(layer_ir) -> float:
    """Share of right-hand attacks written in parallel thirds or sixths.

    Singing in thirds is one of the most recognisable textures in Classical and
    Romantic keyboard writing and one of the cheapest ways to add depth to a
    thin line. Measured at zero on every generated piece examined.
    """
    spans = extract_voices(layer_ir)
    total = harmonised = 0
    for t in attack_times(spans):
        state = sounding_at(spans, t)
        rh = sorted(
            (s for v, s in state.items() if _hand_of(v) == "rh" and s.start == t),
            key=lambda s: s.midi,
        )
        if not rh:
            continue
        total += 1
        for a, b in zip(rh, rh[1:]):
            if (b.midi - a.midi) in (3, 4, 8, 9):
                harmonised += 1
                break
    return harmonised / total if total else 0.0


def _texture_shift_pct(bars: Sequence[BarTexture]) -> float:
    """Share of bar boundaries where the texture genuinely changes.

    "Genuinely" means one of: the number of simultaneous parts changes, a hand
    switches between single-line and chordal, or the register centre moves by
    more than a fifth. Counting a note-count delta — the existing approach —
    calls a busier bar of the same Alberti figure a texture change, and calls a
    switch from an Alberti bass to block chords at the same note count no change
    at all. Both readings are backwards.
    """
    if len(bars) < 2:
        return 0.0
    changes = 0
    for a, b in zip(bars, bars[1:]):
        centre_a = (a.low + a.high) / 2
        centre_b = (b.low + b.high) / 2
        if (
            round(a.mean_simultaneity) != round(b.mean_simultaneity)
            or a.rh_is_single_line != b.rh_is_single_line
            or abs(centre_a - centre_b) > 7
        ):
            changes += 1
    return changes / (len(bars) - 1)


# ─── Entry point ─────────────────────────────────────────────────────────────


# Reach at which a simultaneous attack is reported. MEASURED over 2,430
# simultaneous attacks in 16 real movements: the median is 8 semitones, the 95th
# percentile 12, the 99th 16. A threshold of 14 — a comfortable large hand —
# still flags 2% of real simultaneities, because a two-staff score cannot say
# which hand plays a cross-staff note and a rolled chord is notated as a
# simultaneity. 16 keeps the check meaningful (a hand does not span more than a
# twelfth) while leaving real writing alone at 0.6%.
_DEFAULT_MAX_HAND_SPAN = 16


def analyze_voicing(
    layer_ir, max_hand_span: int = _DEFAULT_MAX_HAND_SPAN, style: Optional[str] = None
) -> VoicingReport:
    """Texture, register and voicing over a phrase, a section or a whole piece.

    ``style`` (a composer name, style id or period) tightens the suggestion
    floors to that period's own observed range — see ``_STYLE_FLOOR``.
    """
    report = VoicingReport()
    bars = measure_bars(layer_ir)
    report.bars = bars
    if not bars:
        report.observations.append("no sounding notes")
        return report

    sims = [b.mean_simultaneity for b in bars]
    rh = [b.rh_notes_per_attack for b in bars if b.rh_notes_per_attack]
    lh = [b.lh_notes_per_attack for b in bars if b.lh_notes_per_attack]
    report.mean_simultaneity = mean(sims)
    report.rh_notes_per_attack = mean(rh) if rh else 0.0
    report.lh_notes_per_attack = mean(lh) if lh else 0.0
    report.single_line_rh_pct = sum(1 for b in bars if b.rh_is_single_line) / len(bars)
    lows = [b.low for b in bars]
    highs = [b.high for b in bars]
    report.register_span = max(highs) - min(lows)
    report.registers_used = tuple(sorted({r for b in bars for r in b.registers}))
    report.span_range = (min(b.span for b in bars), max(b.span for b in bars))
    report.texture_shift_pct = _texture_shift_pct(bars)
    report.simultaneity_cv = (pstdev(sims) / mean(sims)) if mean(sims) else 0.0
    report.thirds_sixths_pct = _thirds_and_sixths(layer_ir)

    hs = _hand_spans(layer_ir)
    if hs:
        report.widest_hand_span = max(s for _, _, s in hs)
        report.unplayable_spans = [
            (bar, beat, span) for bar, beat, span in hs if span > max_hand_span
        ]

    report.style = _period_of(style) or ""
    _observe(report)
    _suggest(report, floors_for(style))
    return report


def _observe(r: VoicingReport) -> None:
    n = len(r.bars)
    r.observations.append(
        f"{n} bars, mean {r.mean_simultaneity:.1f} notes sounding, "
        f"RH {r.rh_notes_per_attack:.2f} notes per attack"
    )
    r.observations.append(
        f"register: {r.register_span} semitones across {len(r.registers_used)} "
        f"registers ({', '.join(r.registers_used)})"
    )
    r.observations.append(
        f"texture changes at {r.texture_shift_pct:.0%} of bar boundaries; "
        f"simultaneity CV {r.simultaneity_cv:.2f}"
    )


def _suggest(r: VoicingReport, floor: Optional[Dict[str, float]] = None) -> None:
    """Composer-facing prompts, phrased as questions, never as targets.

    Every threshold is a floor set outside the range measured on 22 real
    movements (see ``CORPUS_TEXTURE``), so a suggestion means the music has left
    the repertoire's territory, not that it is below some average. Each one
    names the measurement and the real range so the composer can decide it is
    wrong — which for a deliberately spare texture it often is.
    """
    floor = floor or _FLOOR
    n = len(r.bars)
    if n < 8:
        return  # too short to say anything about texture over time

    if r.single_line_rh_pct > floor["single_line_rh_pct"]:
        r.suggestions.append(
            f"The right hand is a bare single line in {r.single_line_rh_pct:.0%} of bars. "
            f"Real Mozart runs 50-89%, Chopin 5-63%. Thirds or sixths at the phrase's "
            f"high point, or an inner voice under a held melody note, is what gives a "
            f"keyboard texture body."
        )
    if r.rh_notes_per_attack and r.rh_notes_per_attack < floor["rh_notes_per_attack"]:
        r.suggestions.append(
            f"The right hand averages {r.rh_notes_per_attack:.2f} notes per attack — "
            f"below the 1.06 minimum of every real movement measured. It is one line "
            f"and nothing else, all the way through."
        )
    if r.lh_notes_per_attack and r.lh_notes_per_attack < floor["lh_notes_per_attack"]:
        r.suggestions.append(
            f"The left hand averages {r.lh_notes_per_attack:.2f} notes per attack "
            f"(real range 1.05-2.57). Even a simple accompaniment usually carries a "
            f"third above the bass somewhere."
        )
    if r.thirds_sixths_pct < floor["thirds_sixths_pct"]:
        r.suggestions.append(
            "Nothing in the piece is written in parallel thirds or sixths — one of the "
            "most characteristic keyboard sounds there is, and free depth on a line "
            "that already exists. Real scores run 1-50% of attacks."
        )
    if r.register_span < floor["register_span"]:
        r.suggestions.append(
            f"The whole piece lives inside {r.register_span} semitones; the narrowest "
            f"real movement measured spans 41. A return that comes back an octave "
            f"higher costs nothing and changes everything."
        )
    if len(r.registers_used) <= floor["registers_used"]:
        r.suggestions.append(
            f"Only {len(r.registers_used)} registers are used "
            f"({', '.join(r.registers_used)}); real movements use 5-7."
        )
    if r.texture_shift_pct < floor["texture_shift_low"]:
        r.suggestions.append(
            f"The texture is unchanged at {1 - r.texture_shift_pct:.0%} of bar "
            f"boundaries (real scores change at 27-75%). Sameness over a whole piece "
            f"reads as inattention even when every bar is well written."
        )
    if r.texture_shift_pct > floor["texture_shift_high"]:
        r.suggestions.append(
            f"The texture changes at {r.texture_shift_pct:.0%} of bar boundaries, above "
            f"the 75% high-water mark of any real movement measured. Restlessness reads "
            f"as indecision; an accompaniment idiom usually holds for a phrase."
        )
    if r.simultaneity_cv < floor["simultaneity_cv"]:
        r.suggestions.append(
            f"The number of notes sounding barely varies (CV {r.simultaneity_cv:.2f}; "
            f"real scores 0.16-0.50, Mozart never below 0.22). The texture never "
            f"thickens at a climax or thins into a cadence — this is the measurement "
            f"most reliably outside the repertoire on generated music."
        )
    if r.unplayable_spans:
        bar, beat, span = r.unplayable_spans[0]
        r.suggestions.append(
            f"{len(r.unplayable_spans)} simultaneous attacks exceed a hand's reach "
            f"(widest {span} semitones at bar {bar} beat {beat:g}). Roll them, "
            f"redistribute between the hands, or drop a note — though check the "
            f"score first: a chord written across the staves, or one meant to be "
            f"rolled, reads the same way here."
        )


def compare_to_corpus_texture(
    report: VoicingReport, corpus: Optional[Dict[str, float]] = None
) -> List[str]:
    """Lines comparing this texture to a corpus profile, when one is available.

    Deliberately returns prose, not z-scores: this project has already learned
    that handing the composer a z-score turns composition into metric
    whack-a-mole. The comparison is here to *inform* the ear, not to be hit.
    """
    if not corpus:
        return []
    out = []
    pairs = [
        ("rh_notes_per_attack", "right-hand thickness", report.rh_notes_per_attack),
        ("mean_simultaneity", "notes sounding at once", report.mean_simultaneity),
        ("texture_shift_pct", "texture change rate", report.texture_shift_pct),
    ]
    for key, label, mine in pairs:
        theirs = corpus.get(key)
        if theirs is None:
            continue
        if theirs and abs(mine - theirs) / max(theirs, 1e-6) > 0.35:
            direction = "thinner/less" if mine < theirs else "thicker/more"
            out.append(f"{label}: {mine:.2f} vs corpus {theirs:.2f} — noticeably {direction}")
    return out


def suggest_thickening_points(layer_ir, limit: int = 6) -> List[Dict[str, Any]]:
    """Bars where adding a voice would do the most good.

    Ranked by how exposed the moment is: a long melody note, high in the phrase's
    arc, with nothing else sounding, is where a bare single line is most audible
    and where a third or an inner voice pays for itself.
    """
    spans = extract_voices(layer_ir)
    if not spans:
        return []
    mel = [s for s in spans if s.voice.split("#")[0] in ("principal_line", "foreground")]
    if not mel:
        return []
    peak = max(s.midi for s in mel)
    out = []
    for s in mel:
        sim = len(sounding_at(spans, s.start))
        held = s.end - s.start
        if sim > 2 or held < Fraction(1, 2):
            continue
        score = float(held) * (1.0 + (s.midi >= peak - 2)) * (3 - sim)
        out.append(
            {
                "bar": s.bar,
                "beat": round(s.beat, 3),
                "pitch_midi": s.midi,
                "sounding": sim,
                "held_beats": float(held),
                "score": round(score, 3),
                "why": (
                    "exposed melody note at the phrase's peak"
                    if s.midi >= peak - 2
                    else "long melody note with nothing under it"
                ),
            }
        )
    out.sort(key=lambda d: -d["score"])
    return out[:limit]


def hand_span_at(layer_ir, bar: int, beat: float) -> Dict[str, int]:
    """Reach required in each hand at one moment — for a targeted revision."""
    spans = extract_voices(layer_ir)
    bpb = Fraction(int(getattr(layer_ir, "meter", (4, 4))[0]) * 4,
                   int(getattr(layer_ir, "meter", (4, 4))[1]))
    first = min((s.bar for s in spans), default=bar)
    t = (bar - first) * bpb + (Fraction(str(round(float(beat), 4))).limit_denominator(48) - 1)
    state = sounding_at(spans, t)
    out = {}
    for hand in ("rh", "lh"):
        ms = [s.midi for v, s in state.items() if _hand_of(v) == hand]
        out[hand] = (max(ms) - min(ms)) if len(ms) >= 2 else 0
    return out


def texture_label(bt: BarTexture) -> str:
    """A short human name for one bar's texture — for briefs and reviews.

    Named by what a listener hears, not by note count. The corpus labels are
    count thresholds, which is why 81% of Chopin came back as one label.
    """
    if bt.notes == 0:
        return "silence"
    if bt.max_simultaneity <= 1:
        return "monophonic"
    if bt.rh_is_single_line and bt.lh_notes_per_attack <= 1.05:
        return "two_part"
    if bt.rh_is_single_line and bt.lh_notes_per_attack > 1.05:
        return "melody_and_accompaniment"
    if not bt.rh_is_single_line and bt.rh_notes_per_attack >= 2.5:
        return "chordal"
    if not bt.rh_is_single_line:
        return "harmonised_melody"
    return "mixed"


def texture_timeline(layer_ir) -> List[Tuple[int, str]]:
    """(bar, texture label) — the shape of the piece at a glance."""
    return [(b.bar, texture_label(b)) for b in measure_bars(layer_ir)]


def texture_runs(layer_ir) -> List[Tuple[str, int, int]]:
    """(label, first_bar, last_bar) runs — where the texture actually holds.

    Twelve bars of one label is the "12 bars of identical LH triplet arpeggios"
    finding, made visible without anyone having to read the score by eye.
    """
    timeline = texture_timeline(layer_ir)
    if not timeline:
        return []
    runs: List[Tuple[str, int, int]] = []
    label, start, prev = timeline[0][1], timeline[0][0], timeline[0][0]
    for bar, lab in timeline[1:]:
        if lab != label:
            runs.append((label, start, prev))
            label, start = lab, bar
        prev = bar
    runs.append((label, start, prev))
    return runs
