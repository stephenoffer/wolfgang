"""
Expression enricher — the marks a human engraver puts on the page.

Measured on the most recent generated piece (a 41-bar Mozart-style Andante,
511 notes): **0 articulations, 0 ties, 4 hairpin marks and 16 dynamics.** A real
Mozart andante of that length carries several hundred articulation marks, dozens
of slurs, a dynamic or hairpin every bar or two, and ties across most barlines.
The notation vocabulary existed; nothing was writing it. An unarticulated score
sounds like a MIDI file because it *is* one — that is the single loudest
"machine wrote this" signal in the output.

This module fills in what the composer left blank, and **only** what was left
blank. Every rule is non-destructive: a field the agent wrote is never touched,
and a region the agent already phrased is skipped whole. The agent stays the
composer; this is the engraver's pass that follows it.

Design rules, in order of importance:

1. **Never overwrite.** ``_blank(ev, "articulation")`` gates every write.
2. **Style decides.** A Baroque score gets no pedal and few hairpins; a Romantic
   one gets long pedal and long hairpins; Classical gets short slurs, staccato
   accompaniment and terraced dynamics. See ``ENGRAVING_STYLES``.
3. **Structure decides placement.** Slurs follow gestures (rests, long notes and
   direction changes break them), hairpins follow the melodic arch, pedal
   follows the harmonic rhythm, dynamics follow the energy curve.
4. **Report everything.** ``EnrichmentReport`` says exactly what was added, so a
   reviewer can tell the engraver's marks from the composer's.

Nothing here invents or changes a *pitch* or a *duration*. It cannot alter the
music, only how the music is played.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .duration import dur_to_beats
from .pitch import pitch_to_midi

# ─── Style profiles ──────────────────────────────────────────────────────────
#
# Each profile says how a period's engraver marks a page. The numbers are not
# quotas: they are ceilings and preferences that shape where a mark is *allowed*
# to go. "slur_max_notes" is the longest gesture that gets a single slur —
# Baroque and Classical phrase in short arcs, Romantic in long ones.


@dataclass
class EngravingStyle:
    name: str = "classical"
    # Phrasing
    slur_min_notes: int = 3
    slur_max_notes: int = 8
    slur_breaks_on_leap: int = 5  # semitones; a bigger leap ends the arc
    # Articulation
    accompaniment_staccato: bool = True  # detached oom-pah / repeated chords
    staccato_max_beats: Fraction = Fraction(1, 2)  # only short notes get dots
    tenuto_on_appoggiatura: bool = True
    accent_on_syncopation: bool = True
    # Dynamics
    terraced: bool = True  # echo a literal repeat one step softer
    hairpin_min_notes: int = 4
    hairpin_max_bars: int = 2
    dynamic_every_n_bars: int = 4  # at most one written dynamic this often
    # Pedal
    pedal: str = "sparing"  # "none" | "sparing" | "harmonic" | "long"
    # Rolled chords
    arpeggiate_span: int = 12  # LH/RH chords wider than this get rolled
    # Character words
    uses_character_words: bool = True


ENGRAVING_STYLES: Dict[str, EngravingStyle] = {
    "renaissance": EngravingStyle(
        name="renaissance",
        slur_min_notes=4,
        slur_max_notes=12,
        accompaniment_staccato=False,
        tenuto_on_appoggiatura=False,
        accent_on_syncopation=False,
        terraced=False,
        hairpin_min_notes=99,  # effectively off — dynamics are not notated
        dynamic_every_n_bars=99,
        pedal="none",
        arpeggiate_span=99,
        uses_character_words=False,
    ),
    "baroque": EngravingStyle(
        name="baroque",
        slur_min_notes=3,
        slur_max_notes=6,
        slur_breaks_on_leap=4,
        accompaniment_staccato=True,
        tenuto_on_appoggiatura=False,
        terraced=True,
        hairpin_min_notes=99,  # Bach did not write hairpins
        dynamic_every_n_bars=8,
        pedal="none",
        arpeggiate_span=14,
        uses_character_words=False,
    ),
    "classical": EngravingStyle(
        name="classical",
        slur_min_notes=2,
        slur_max_notes=8,
        slur_breaks_on_leap=5,
        accompaniment_staccato=True,
        tenuto_on_appoggiatura=True,
        terraced=True,
        hairpin_min_notes=4,
        hairpin_max_bars=2,
        dynamic_every_n_bars=4,
        pedal="sparing",
        arpeggiate_span=12,
    ),
    "romantic": EngravingStyle(
        name="romantic",
        slur_min_notes=3,
        slur_max_notes=16,
        slur_breaks_on_leap=8,
        accompaniment_staccato=False,
        staccato_max_beats=Fraction(1, 4),
        tenuto_on_appoggiatura=True,
        terraced=False,
        hairpin_min_notes=3,
        hairpin_max_bars=4,
        dynamic_every_n_bars=3,
        pedal="long",
        arpeggiate_span=10,
    ),
    "impressionist": EngravingStyle(
        name="impressionist",
        slur_min_notes=3,
        slur_max_notes=20,
        slur_breaks_on_leap=10,
        accompaniment_staccato=False,
        terraced=False,
        hairpin_min_notes=3,
        hairpin_max_bars=6,
        dynamic_every_n_bars=3,
        pedal="long",
        arpeggiate_span=9,
    ),
}

# Composer → period, so a caller can pass either.
_COMPOSER_PERIOD = {
    "palestrina": "renaissance",
    "monteverdi": "renaissance",
    "byrd": "renaissance",
    "victoria": "renaissance",
    "bach": "baroque",
    "handel": "baroque",
    "corelli": "baroque",
    "vivaldi": "baroque",
    "scarlatti": "baroque",
    "telemann": "baroque",
    "purcell": "baroque",
    "haydn": "classical",
    "mozart": "classical",
    "beethoven": "classical",
    "clementi": "classical",
    "hummel": "classical",
    "schubert": "romantic",
    "chopin": "romantic",
    "schumann": "romantic",
    "liszt": "romantic",
    "brahms": "romantic",
    "mendelssohn": "romantic",
    "tchaikovsky": "romantic",
    "grieg": "romantic",
    "rachmaninoff": "romantic",
    "wagner": "romantic",
    "debussy": "impressionist",
    "ravel": "impressionist",
    "satie": "impressionist",
    "faure": "impressionist",
    "scriabin": "impressionist",
}


def resolve_style(name: Optional[str]) -> EngravingStyle:
    """Accept a composer name, a style id (``style__classical``) or a period."""
    if not name:
        return ENGRAVING_STYLES["classical"]
    key = str(name).strip().lower().replace(" ", "_")
    if key.startswith("style__"):
        key = key[len("style__") :]
    if key in ENGRAVING_STYLES:
        return ENGRAVING_STYLES[key]
    period = _COMPOSER_PERIOD.get(key)
    if period:
        return ENGRAVING_STYLES[period]
    # A blend id ("mozart+chopin") resolves on its first recognised member so a
    # blended style still gets *a* considered engraving convention rather than
    # silently falling through to the Classical default.
    for part in key.replace("+", " ").replace("__", " ").replace("-", " ").split():
        if part in ENGRAVING_STYLES:
            return ENGRAVING_STYLES[part]
        if part in _COMPOSER_PERIOD:
            return ENGRAVING_STYLES[_COMPOSER_PERIOD[part]]
    return ENGRAVING_STYLES["classical"]


# ─── Report ──────────────────────────────────────────────────────────────────


@dataclass
class EnrichmentReport:
    """What the engraver's pass added, so a reviewer can separate it out."""

    slurs_added: int = 0
    articulations_added: int = 0
    dynamics_added: int = 0
    hairpins_added: int = 0
    pedal_marks_added: int = 0
    techniques_added: int = 0
    expressions_added: int = 0
    fermatas_added: int = 0
    ties_added: int = 0
    notes_seen: int = 0
    author_marks_kept: int = 0
    style: str = "classical"
    detail: List[str] = field(default_factory=list)

    @property
    def total_added(self) -> int:
        return (
            self.slurs_added
            + self.articulations_added
            + self.dynamics_added
            + self.hairpins_added
            + self.pedal_marks_added
            + self.techniques_added
            + self.expressions_added
            + self.fermatas_added
            + self.ties_added
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style,
            "notes_seen": self.notes_seen,
            "author_marks_kept": self.author_marks_kept,
            "total_added": self.total_added,
            "slurs": self.slurs_added,
            "articulations": self.articulations_added,
            "dynamics": self.dynamics_added,
            "hairpins": self.hairpins_added,
            "pedal": self.pedal_marks_added,
            "techniques": self.techniques_added,
            "expressions": self.expressions_added,
            "fermatas": self.fermatas_added,
            "ties": self.ties_added,
            "detail": self.detail[:40],
        }


# ─── Small helpers ───────────────────────────────────────────────────────────

_PIANO_LAYERS = (
    "principal_line",
    "bass_foundation",
    "response_layer",
    "counter_reply",
    "ornamental_surface",
)
_ORCH_LAYERS = (
    "foreground",
    "countermelody",
    "harmonic_mass",
    "rhythmic_motor",
    "color_layer",
    "punctuation",
)


def _blank(ev, attr: str) -> bool:
    """True when the composer left this field for the engraver to fill."""
    return getattr(ev, attr, None) in (None, "")


def _is_rest(ev) -> bool:
    return getattr(ev, "pitch", None) == "rest"


def _midis(ev) -> List[int]:
    """Every sounding MIDI number in an event (a chord yields several)."""
    p = getattr(ev, "pitch", None)
    if not p or p == "rest":
        return []
    names = p if isinstance(p, list) else [p]
    out = []
    for n in names:
        try:
            out.append(pitch_to_midi(n))
        except (ValueError, KeyError, TypeError):
            continue
    return out


def _top(ev) -> Optional[int]:
    m = _midis(ev)
    return max(m) if m else None


def _beats(ev) -> Fraction:
    try:
        return dur_to_beats(getattr(ev, "duration", "q"))
    except Exception:  # pragma: no cover - defensive
        return Fraction(1)


def _sorted(events: Iterable) -> List:
    return sorted(events, key=lambda e: (getattr(e, "bar", 0), float(getattr(e, "beat", 1.0))))


def _all_layers(layer_ir) -> List[Tuple[str, List]]:
    """Every populated note list on a LayerIR, including extra inner voices.

    Naive ``vars(layer_ir).items()`` iteration treats ``meter=(3,4)`` as a note
    list — a real trap in this codebase, and the reason this helper exists.
    """
    out: List[Tuple[str, List]] = []
    for name in _PIANO_LAYERS + _ORCH_LAYERS:
        evs = getattr(layer_ir, name, None)
        if evs:
            out.append((name, evs))
    for name, evs in (getattr(layer_ir, "inner_voices", None) or {}).items():
        if evs:
            out.append((name, evs))
    return out


def _beats_per_bar(meter) -> Fraction:
    try:
        num, den = int(meter[0]), int(meter[1])
        return Fraction(num * 4, den)
    except Exception:  # pragma: no cover - defensive
        return Fraction(4)


def _is_compound(meter) -> bool:
    """6/8, 9/8, 12/8 — beats group in threes, which changes where accents go."""
    try:
        num, den = int(meter[0]), int(meter[1])
    except Exception:  # pragma: no cover - defensive
        return False
    return den == 8 and num in (6, 9, 12)


def _strong_beats(meter) -> List[Fraction]:
    """Beat positions (1-based) that carry metric stress in this meter."""
    try:
        num, den = int(meter[0]), int(meter[1])
    except Exception:  # pragma: no cover - defensive
        num, den = 4, 4
    if _is_compound(meter):
        # 6/8 stresses beats 1 and 4 (in eighth-note counting) = quarters 1, 2.5
        group = Fraction(3, 2)
        return [Fraction(1) + group * i for i in range(num // 3)]
    if num == 4 and den == 4:
        return [Fraction(1), Fraction(3)]
    if num == 2:
        return [Fraction(1)]
    if num == 3:
        return [Fraction(1)]
    return [Fraction(1)]


_DYN_LADDER = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]


def _softer(dyn: str, steps: int = 1) -> str:
    try:
        i = _DYN_LADDER.index(dyn)
    except ValueError:
        return dyn
    return _DYN_LADDER[max(0, i - steps)]


def _louder(dyn: str, steps: int = 1) -> str:
    try:
        i = _DYN_LADDER.index(dyn)
    except ValueError:
        return dyn
    return _DYN_LADDER[min(len(_DYN_LADDER) - 1, i + steps)]


def dynamic_for_energy(energy: float) -> str:
    """Map a 0-1 narrative energy value onto a written dynamic."""
    if energy < 0.12:
        return "pp"
    if energy < 0.3:
        return "p"
    if energy < 0.45:
        return "mp"
    if energy < 0.62:
        return "mf"
    if energy < 0.8:
        return "f"
    return "ff"


# ─── Gesture segmentation ────────────────────────────────────────────────────


def segment_gestures(events: Sequence, style: EngravingStyle, meter=(4, 4)) -> List[List[int]]:
    """Split a single voice into slur-able gestures, as index runs.

    A gesture ends at a rest, at a note long enough to be its own event, at a
    leap wider than the style tolerates, and at the style's maximum arc length.
    This is what makes a slur mean something: a slur drawn over an arbitrary
    fixed window is worse than no slur at all, because it tells the player to
    connect notes that do not belong together.
    """
    gestures: List[List[int]] = []
    current: List[int] = []
    long_note = max(_beats_per_bar(meter) / 2, Fraction(1))
    prev_top: Optional[int] = None

    def flush():
        nonlocal current
        if len(current) >= 2:
            gestures.append(current)
        current = []

    for i, ev in enumerate(events):
        if _is_rest(ev):
            flush()
            prev_top = None
            continue
        top = _top(ev)
        if top is None:
            flush()
            prev_top = None
            continue
        if prev_top is not None and abs(top - prev_top) > style.slur_breaks_on_leap:
            flush()
        if len(current) >= style.slur_max_notes:
            flush()
        current.append(i)
        prev_top = top
        # A note held for half a bar or more is a destination, not a step on the
        # way somewhere: the arc lands on it and a new one starts after.
        if _beats(ev) >= long_note and len(current) >= 2:
            flush()
            prev_top = top
    flush()
    return [g for g in gestures if len(g) >= max(2, style.slur_min_notes)]


def _region_already_phrased(events: Sequence, idxs: Sequence[int]) -> bool:
    """True if the composer already wrote a slur touching this run."""
    lo, hi = min(idxs), max(idxs)
    window = range(max(0, lo - 2), min(len(events), hi + 3))
    return any(getattr(events[i], "slur", None) for i in window)


# ─── Rule: phrasing slurs ────────────────────────────────────────────────────


def add_phrasing_slurs(layer_ir, style: EngravingStyle, report: EnrichmentReport) -> None:
    """Draw slurs over melodic gestures in the singing voices.

    Applied to the melodic layers only. Slurring an Alberti bass is wrong — the
    accompaniment's articulation is decided separately by
    ``add_accompaniment_articulation``.
    """
    meter = getattr(layer_ir, "meter", (4, 4))
    for name in ("principal_line", "counter_reply", "foreground", "countermelody"):
        events = getattr(layer_ir, name, None)
        if not events or len(events) < 3:
            continue
        events = _sorted(events)
        for gesture in segment_gestures(events, style, meter):
            if _region_already_phrased(events, gesture):
                report.author_marks_kept += 1
                continue
            first, last = events[gesture[0]], events[gesture[-1]]
            if not (_blank(first, "slur") and _blank(last, "slur")):
                continue
            first.slur = "start"
            last.slur = "stop"
            report.slurs_added += 1
        report.detail.append(f"slurs:{name}")


# ─── Rule: melodic articulation ──────────────────────────────────────────────


def add_melodic_articulation(layer_ir, style: EngravingStyle, report: EnrichmentReport) -> None:
    """Tenuto on leaning notes, accents on off-beat stresses, dots on light
    repeated notes — the marks that separate a phrased melody from a MIDI dump.
    """
    meter = getattr(layer_ir, "meter", (4, 4))
    bpb = _beats_per_bar(meter)
    strong = set(_strong_beats(meter))
    for name in ("principal_line", "counter_reply", "foreground", "countermelody"):
        events = _sorted(getattr(layer_ir, name, None) or [])
        if len(events) < 3:
            continue
        # The phrase's last bar, across ALL layers — not just this one.
        last_bar = max(
            (int(getattr(e, "bar", 1)) for _, evs in _all_layers(layer_ir) for e in evs),
            default=1,
        )
        for i, ev in enumerate(events):
            if _is_rest(ev) or not _blank(ev, "articulation"):
                if not _blank(ev, "articulation"):
                    report.author_marks_kept += 1
                continue
            role = getattr(ev, "role", "") or ""
            beat = Fraction(str(round(float(getattr(ev, "beat", 1.0)), 4))).limit_denominator(48)
            dur = _beats(ev)

            # A leaning dissonance is played with weight and released — tenuto is
            # the mark for that, and it is the single most characteristic
            # articulation of a Classical slow movement.
            #
            # It must be a note long enough to lean ON, though. Without the
            # duration floor this marked tenuto on 16th notes in the middle of a
            # running passage, where the instruction is unplayable and reads as
            # noise on the page: a passing 16th tagged `appoggiatura` by the
            # role heuristic is a passing note, whatever it is called.
            if (
                style.tenuto_on_appoggiatura
                and role in ("appoggiatura", "suspension")
                and dur >= Fraction(1, 2)
            ):
                ev.articulation = "tenuto"
                report.articulations_added += 1
                continue

            # A long note that arrives BETWEEN the beats is a syncopation: it
            # wants an accent, because the metre will not give it one.
            #
            # "Not on a strong beat" is not the same thing as "syncopated". In
            # 3/4 beats 2 and 3 are weak beats but they are still beats, so the
            # old test accented an ordinary crotchet on beat 2 — which in this
            # system's output meant an accent on the lyrical high note of the
            # theme, in every one of its three statements. Require an attack
            # genuinely off the beat, and never fight an ornament: a trill or a
            # turn already tells the player this note is the event.
            offbeat = beat.denominator != 1
            if (
                style.accent_on_syncopation
                and offbeat
                and dur >= Fraction(1)
                and beat not in strong
                and not getattr(ev, "ornament", None)
                and i > 0
                and abs((_top(ev) or 0) - (_top(events[i - 1]) or 0)) >= 3
            ):
                ev.articulation = "accent"
                report.articulations_added += 1
                continue

            # A short note repeated from its predecessor and repeated again
            # after: a drummed repeated-note figure, which is detached in every
            # period before the Romantics.
            if (
                style.accompaniment_staccato
                and dur <= style.staccato_max_beats
                and 0 < i < len(events) - 1
                and _top(ev) is not None
                and _top(ev) == _top(events[i - 1]) == _top(events[i + 1])
            ):
                ev.articulation = "staccato"
                report.articulations_added += 1
                continue

            # The last note of a phrase, short, after a rest-free run: lift it.
            #
            # Scoped to the phrase's final bar. Each *layer* is scanned
            # separately, so "the last event in this list" was the last note of
            # an inner voice that stopped halfway through the phrase — producing
            # a staccato dot in the middle of a held line, for no reason a
            # player could see.
            if (
                i == len(events) - 1
                and dur <= Fraction(1, 2)
                and bpb >= 2
                and int(getattr(ev, "bar", 1)) >= last_bar
            ):
                ev.articulation = "staccato"
                report.articulations_added += 1
        report.detail.append(f"articulation:{name}")


# ─── Rule: accompaniment articulation ────────────────────────────────────────


def add_accompaniment_articulation(
    layer_ir, style: EngravingStyle, report: EnrichmentReport
) -> None:
    """Detach a repeated-chord or repeated-bass accompaniment.

    The Classical "oom-pah" is played detached; written without dots it is
    played legato, which is the muddy, undifferentiated sound that makes a
    generated accompaniment read as machine output. Romantic accompaniments are
    left legato, which is equally deliberate.
    """
    if not style.accompaniment_staccato:
        return
    for name in ("bass_foundation", "response_layer", "harmonic_mass", "rhythmic_motor"):
        events = _sorted(getattr(layer_ir, name, None) or [])
        if len(events) < 4:
            continue
        # Only mark a layer that is genuinely a repeated-chord accompaniment:
        # more than half its events are chords or repeats of the previous pitch,
        # and they are short. A walking bass or a melodic bass is left alone.
        short = [e for e in events if not _is_rest(e) and _beats(e) <= style.staccato_max_beats]
        if len(short) < len(events) * 0.5:
            continue
        chordal = sum(1 for e in short if isinstance(getattr(e, "pitch", None), list))
        repeats = 0
        prev = None
        for e in short:
            t = _top(e)
            if t is not None and t == prev:
                repeats += 1
            prev = t
        if chordal + repeats < len(short) * 0.4:
            continue
        marked = 0
        for e in short:
            if _blank(e, "articulation") and _blank(e, "slur"):
                e.articulation = "staccato"
                marked += 1
        if marked:
            report.articulations_added += marked
            report.detail.append(f"detached-accompaniment:{name}:{marked}")


# ─── Rule: dynamics ──────────────────────────────────────────────────────────


def add_dynamics(
    layer_ir,
    style: EngravingStyle,
    report: EnrichmentReport,
    energy_curve: Optional[Sequence[float]] = None,
    base_dynamic: Optional[str] = None,
) -> None:
    """Put a written dynamic where a player needs one.

    A phrase with no dynamic anywhere is unplayable as written: the performer
    has to guess. The rule is one dynamic at the phrase's entry, plus a change
    where the energy curve genuinely moves a step, never more often than the
    style writes them.
    """
    if style.dynamic_every_n_bars > 50:
        return  # this style does not notate dynamics at all (Renaissance vocal)
    melody = _sorted(getattr(layer_ir, "principal_line", None) or [])
    if not melody:
        for _, evs in _all_layers(layer_ir):
            melody = _sorted(evs)
            break
    if not melody:
        return
    sounding = [e for e in melody if not _is_rest(e)]
    if not sounding:
        return

    bars = sorted({int(getattr(e, "bar", 1)) for e in sounding})
    first_bar = bars[0]

    # Bar -> the dynamic the energy curve asks for.
    wanted: Dict[int, str] = {}
    if energy_curve:
        for i, bar in enumerate(bars):
            e = energy_curve[min(i, len(energy_curve) - 1)]
            try:
                wanted[bar] = dynamic_for_energy(float(e))
            except (TypeError, ValueError):
                continue
    default = base_dynamic or wanted.get(first_bar) or "mf"

    existing_bars = {
        int(getattr(e, "bar", 1)) for e in melody if getattr(e, "dynamic", None)
    }
    if existing_bars:
        report.author_marks_kept += len(existing_bars)

    last_written: Optional[str] = None
    last_bar: Optional[int] = None
    for bar in bars:
        if bar in existing_bars:
            last_written = None  # composer took over; re-baseline
            last_bar = bar
            continue
        target = wanted.get(bar, default if bar == first_bar else None)
        if target is None:
            continue
        if bar != first_bar:
            if last_written == target:
                continue
            if last_bar is not None and bar - last_bar < style.dynamic_every_n_bars:
                continue
        head = next(
            (
                e
                for e in sounding
                if int(getattr(e, "bar", 1)) == bar and _blank(e, "dynamic")
            ),
            None,
        )
        if head is None:
            continue
        head.dynamic = target
        last_written, last_bar = target, bar
        report.dynamics_added += 1
    report.detail.append(f"dynamics:{report.dynamics_added}")


def add_echo_terracing(layer_ir, style: EngravingStyle, report: EnrichmentReport) -> None:
    """A literal repeat is echoed a step softer.

    Terraced echo is the oldest expressive device in keyboard music and it is
    free: when the composer repeats a two-bar unit note for note, marking the
    repeat softer turns a photocopy into a rhetorical figure. Without it a
    literal repeat is simply a repeat, which is exactly what a generated score
    is always accused of.
    """
    if not style.terraced:
        return
    melody = _sorted(getattr(layer_ir, "principal_line", None) or [])
    if len(melody) < 8:
        return
    by_bar: Dict[int, List] = {}
    for e in melody:
        by_bar.setdefault(int(getattr(e, "bar", 1)), []).append(e)
    bars = sorted(by_bar)
    if len(bars) < 4:
        return

    def sig(bar: int) -> Tuple:
        return tuple(
            (getattr(e, "pitch", None) if not isinstance(getattr(e, "pitch", None), list)
             else tuple(getattr(e, "pitch")), getattr(e, "duration", "q"))
            for e in by_bar.get(bar, [])
        )

    for span in (2, 1):
        for i in range(len(bars) - 2 * span + 1):
            a = [sig(bars[i + k]) for k in range(span)]
            b = [sig(bars[i + span + k]) for k in range(span)]
            if not all(a) or a != b:
                continue
            first = next(
                (e for e in by_bar[bars[i + span]] if not _is_rest(e)), None
            )
            if first is None or not _blank(first, "dynamic"):
                continue
            # Find the dynamic in force so the echo is one real step below it.
            in_force = "mf"
            for e in melody:
                if int(getattr(e, "bar", 1)) > bars[i + span]:
                    break
                if getattr(e, "dynamic", None):
                    in_force = e.dynamic
            first.dynamic = _softer(in_force)
            report.dynamics_added += 1
            report.detail.append(f"echo:bar{bars[i + span]}")
            return  # one echo per phrase is a gesture; more is a mannerism


# ─── Rule: hairpins ──────────────────────────────────────────────────────────


def add_hairpins(layer_ir, style: EngravingStyle, report: EnrichmentReport) -> None:
    """Crescendo into the melodic peak, diminuendo away from it.

    The melodic arch is the phrase's shape; a hairpin that follows it is what a
    composer writes and what a listener hears as intention. Hairpins are placed
    only where the arch is real (a genuine rise of at least a third over at
    least ``hairpin_min_notes``), never on a flat line.
    """
    if style.hairpin_min_notes > 50:
        return  # this style does not notate hairpins
    melody = _sorted(getattr(layer_ir, "principal_line", None) or [])
    sounding = [e for e in melody if not _is_rest(e)]
    if len(sounding) < style.hairpin_min_notes * 2:
        return
    if any(getattr(e, "hairpin", None) for e in melody):
        report.author_marks_kept += 1
        return

    tops = [_top(e) for e in sounding]
    if any(t is None for t in tops):
        sounding = [e for e, t in zip(sounding, tops) if t is not None]
        tops = [t for t in tops if t is not None]
    if len(sounding) < style.hairpin_min_notes * 2:
        return

    peak_i = max(range(len(tops)), key=lambda i: tops[i])
    # Walk back from the peak while the line is broadly rising.
    start = peak_i
    while start > 0 and tops[start - 1] <= tops[start] + 1:
        start -= 1
        if peak_i - start >= style.hairpin_max_bars * 8:
            break
    end = peak_i
    while end < len(tops) - 1 and tops[end + 1] <= tops[end] + 1:
        end += 1
        if end - peak_i >= style.hairpin_max_bars * 8:
            break

    rise = tops[peak_i] - tops[start]
    fall = tops[peak_i] - tops[end]
    if peak_i - start >= style.hairpin_min_notes and rise >= 3:
        if _blank(sounding[start], "hairpin") and _blank(sounding[peak_i], "hairpin"):
            sounding[start].hairpin = "cresc_start"
            sounding[peak_i].hairpin = "stop"
            report.hairpins_added += 1
            report.detail.append(f"cresc:{getattr(sounding[start], 'bar', '?')}")
    if end - peak_i >= style.hairpin_min_notes and fall >= 3:
        src = peak_i if _blank(sounding[peak_i], "hairpin") else peak_i + 1
        if src < len(sounding) and _blank(sounding[src], "hairpin") and _blank(
            sounding[end], "hairpin"
        ):
            sounding[src].hairpin = "dim_start"
            sounding[end].hairpin = "stop"
            report.hairpins_added += 1
            report.detail.append(f"dim:{getattr(sounding[src], 'bar', '?')}")


def add_cadential_diminuendo(
    layer_ir, style: EngravingStyle, report: EnrichmentReport, cadence_bar: Optional[int] = None
) -> None:
    """A soft landing on a closing cadence, unless the cadence is a climax.

    Written into the last two bars only, and only if nothing else is happening
    there dynamically.
    """
    if style.hairpin_min_notes > 50 or cadence_bar is None:
        return
    melody = _sorted(getattr(layer_ir, "principal_line", None) or [])
    tail = [
        e
        for e in melody
        if not _is_rest(e) and int(getattr(e, "bar", 1)) >= int(cadence_bar) - 1
    ]
    if len(tail) < 3:
        return
    if any(getattr(e, "hairpin", None) for e in tail):
        return
    if not (_blank(tail[0], "hairpin") and _blank(tail[-1], "hairpin")):
        return
    tail[0].hairpin = "dim_start"
    tail[-1].hairpin = "stop"
    report.hairpins_added += 1
    report.detail.append(f"cadential-dim:{cadence_bar}")


# ─── Rule: pedal ─────────────────────────────────────────────────────────────


def add_pedal(
    layer_ir,
    style: EngravingStyle,
    report: EnrichmentReport,
    harmony_plan: Optional[Sequence[str]] = None,
) -> None:
    """Notate the sustain pedal where the harmony asks for it.

    Pedal is *not* a global switch: it changes with the harmony or it turns the
    texture to mud. The rule is one change per harmony, taken from the plan when
    there is one and from the bass line's own changes when there is not. Baroque
    and Renaissance styles get none, which is also a decision.

    Density matters as much as placement, and this is where it went wrong. The
    enricher runs **once per phrase**, and a phrase is four or five bars, so
    "every other bar" — which is what `step = 2` means locally — came out as a
    complete down/change/up pedal cycle in every phrase: **18 "Ped." marks in a
    41-bar andante**, which `score_realism.detect_notation_spam` duly flagged as
    noise. No Classical edition looks like that; Mozart's instrument barely had
    a sustain mechanism, and editions print "Ped." at a handful of deliberate
    moments.

    So "sparing" now means what the word says: **at most one pedal span per
    phrase**, placed where the hand genuinely cannot hold the sound — the bar
    whose bass note is longest, and only when that note lasts at least half a
    bar. "harmonic" and "long" still pedal per harmony change, which is right
    for the Romantic styles that ask for them.
    """
    if style.pedal == "none":
        return
    if getattr(layer_ir, "instrumentation", "solo_piano") not in ("solo_piano", "piano"):
        return
    bass = _sorted(getattr(layer_ir, "bass_foundation", None) or [])
    if not bass:
        return
    if any(getattr(e, "pedal", None) for e in bass):
        report.author_marks_kept += 1
        return

    sounding = [e for e in bass if not _is_rest(e)]
    if not sounding:
        return
    meter = getattr(layer_ir, "meter", (4, 4))
    half_bar = _beats_per_bar(meter) / 2
    marked = 0

    if style.pedal == "sparing":
        # One span, on the bar with the most sustain to give.
        head = max(sounding, key=lambda e: (_beats(e), -int(getattr(e, "bar", 1))))
        if _beats(head) < half_bar:
            return
        if not _blank(head, "pedal"):
            return
        head.pedal = "down"
        marked = 1
        tail = [e for e in sounding if _sorted([e, head])[0] is head and e is not head]
        lift = tail[-1] if tail else None
        if lift is not None and _blank(lift, "pedal"):
            lift.pedal = "up"
            marked += 1
    else:
        bars = sorted({int(getattr(e, "bar", 1)) for e in sounding})
        for idx, bar in enumerate(bars):
            if harmony_plan is not None and idx < len(harmony_plan) and idx > 0:
                if harmony_plan[idx] == harmony_plan[idx - 1] and style.pedal != "long":
                    continue
            head = next(
                (
                    e
                    for e in sounding
                    if int(getattr(e, "bar", 1)) == bar and _blank(e, "pedal")
                ),
                None,
            )
            if head is None:
                continue
            head.pedal = "down" if marked == 0 else "change"
            marked += 1
        if marked:
            # Lift at the end so the pedal is not left down past the final barline.
            if _blank(sounding[-1], "pedal"):
                sounding[-1].pedal = "up"
                marked += 1

    if marked:
        report.pedal_marks_added += marked
        report.detail.append(f"pedal:{style.pedal}:{marked}")


# ─── Rule: rolled chords ─────────────────────────────────────────────────────


def add_rolled_chords(layer_ir, style: EngravingStyle, report: EnrichmentReport) -> None:
    """Roll a chord too wide to strike cleanly.

    A tenth in the left hand is unreachable for most players and is *written*
    rolled; a generated score that stacks one and expects it struck is not
    playable music. The arpeggio sign is also, in Romantic writing, a colour in
    its own right.
    """
    if style.arpeggiate_span > 50:
        return
    for name, events in _all_layers(layer_ir):
        for ev in events:
            if not isinstance(getattr(ev, "pitch", None), list):
                continue
            m = _midis(ev)
            if len(m) < 3:
                continue
            if max(m) - min(m) < style.arpeggiate_span:
                continue
            if not _blank(ev, "technique"):
                report.author_marks_kept += 1
                continue
            ev.technique = "arpeggio"
            report.techniques_added += 1
        if report.techniques_added:
            report.detail.append(f"rolled:{name}")


# ─── Rule: final fermata and closing word ────────────────────────────────────


def add_closing_marks(
    layer_ir,
    style: EngravingStyle,
    report: EnrichmentReport,
    is_final_phrase: bool = False,
    character: Optional[str] = None,
) -> None:
    """A fermata on the last chord of the piece; a character word at the head.

    Small marks, but their absence is conspicuous: no generated score has ever
    ended with a fermata, and every real one does.
    """
    if is_final_phrase:
        last = None
        for _, events in _all_layers(layer_ir):
            for ev in _sorted(events):
                if _is_rest(ev):
                    continue
                if last is None or (
                    getattr(ev, "bar", 0),
                    float(getattr(ev, "beat", 1.0)),
                ) > (getattr(last, "bar", 0), float(getattr(last, "beat", 1.0))):
                    last = ev
        if last is not None and _blank(last, "ornament"):
            last.ornament = "fermata"
            report.fermatas_added += 1
            report.detail.append("final-fermata")

    if character and style.uses_character_words:
        melody = _sorted(getattr(layer_ir, "principal_line", None) or [])
        head = next((e for e in melody if not _is_rest(e)), None)
        if head is not None and _blank(head, "expression"):
            head.expression = character
            report.expressions_added += 1
            report.detail.append(f"character:{character}")


# ─── Entry point ─────────────────────────────────────────────────────────────


def enrich_layer_ir(
    layer_ir,
    *,
    style: Optional[str] = None,
    energy_curve: Optional[Sequence[float]] = None,
    harmony_plan: Optional[Sequence[str]] = None,
    cadence_bar: Optional[int] = None,
    base_dynamic: Optional[str] = None,
    character: Optional[str] = None,
    is_final_phrase: bool = False,
    enable: Optional[Dict[str, bool]] = None,
) -> EnrichmentReport:
    """Fill in the engraver's marks the composer left blank.

    Returns an :class:`EnrichmentReport`. The LayerIR is modified in place, and
    **only** in fields that were empty. Callers that want the composer's page
    exactly as written can pass ``enable={...: False}`` per rule, or simply not
    call this.
    """
    st = resolve_style(style)
    report = EnrichmentReport(style=st.name)
    on = {
        "slurs": True,
        "melodic_articulation": True,
        "accompaniment_articulation": True,
        "dynamics": True,
        "terracing": True,
        "hairpins": True,
        "cadential_dim": True,
        "pedal": True,
        "rolled_chords": True,
        "closing": True,
    }
    on.update(enable or {})

    for _, events in _all_layers(layer_ir):
        report.notes_seen += len(events)
        for ev in events:
            if any(
                getattr(ev, f, None)
                for f in ("articulation", "slur", "hairpin", "dynamic", "pedal", "technique")
            ):
                report.author_marks_kept += 1

    if on["slurs"]:
        add_phrasing_slurs(layer_ir, st, report)
    if on["melodic_articulation"]:
        add_melodic_articulation(layer_ir, st, report)
    if on["accompaniment_articulation"]:
        add_accompaniment_articulation(layer_ir, st, report)
    if on["dynamics"]:
        add_dynamics(layer_ir, st, report, energy_curve=energy_curve, base_dynamic=base_dynamic)
    if on["terracing"]:
        add_echo_terracing(layer_ir, st, report)
    if on["hairpins"]:
        add_hairpins(layer_ir, st, report)
    if on["cadential_dim"]:
        add_cadential_diminuendo(layer_ir, st, report, cadence_bar=cadence_bar)
    if on["pedal"]:
        add_pedal(layer_ir, st, report, harmony_plan=harmony_plan)
    if on["rolled_chords"]:
        add_rolled_chords(layer_ir, st, report)
    if on["closing"]:
        add_closing_marks(
            layer_ir, st, report, is_final_phrase=is_final_phrase, character=character
        )
    return report


def expression_density(layer_ir) -> Dict[str, float]:
    """Marks per bar, by kind — the measurement that exposed the empty page.

    A real Classical piano score runs roughly 1.5-4 articulations per bar and
    0.3-1 slurs per bar. Anything near zero means the score has not been
    engraved, whatever else is right about it.
    """
    counts = {"articulation": 0, "slur": 0, "hairpin": 0, "dynamic": 0, "tie": 0, "ornament": 0}
    bars = set()
    for _, events in _all_layers(layer_ir):
        for ev in events:
            bars.add(int(getattr(ev, "bar", 1)))
            for f in counts:
                if getattr(ev, f, None):
                    counts[f] += 1
    n = max(1, len(bars))
    out = {f"{k}_per_bar": round(v / n, 3) for k, v in counts.items()}
    out["bars"] = float(n)
    out["marks_per_bar"] = round(sum(counts.values()) / n, 3)
    return out
