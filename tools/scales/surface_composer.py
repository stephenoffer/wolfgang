"""
SurfaceComposer — phrase-level, context-driven composition.

Replaces the bar-by-bar fallback approach with a phrase-level composer that:
1. Retrieves phrase prototypes from PhraseBank
2. Plans gesture slots between melody anchors
3. Co-composes melody + accompaniment per gesture slot
4. Uses gesture families from GestureBank for melodic fill
5. Adapts patterns to harmony via chord-tone slot roles
6. Integrates cadences as specialized gesture slots
7. Falls back constructively with style-specific figuration

Every bar is shaped by corpus-derived, hand-made musical material.
Procedural filler is a last-resort repair path, not a normal path.
"""

from __future__ import annotations

import collections
import logging
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Optional

from .cadence_bank import CadenceBank
from .corpus_bar_retriever import CorpusBarRetriever
from .duration import DURATION_VALUES, bar_duration
from .enums import AccompType, NoteJustification, NoteRole
from .gesture_bank import GestureBank
from .harmony_analysis import roman_pitches
from .models import (
    ALL_LAYERS,
    Anchor,
    CadenceQuery,
    ContextTrace,
    GestureQuery,
    GestureResult,
    HarmonicCell,
    LayerEvent,
    LayerIR,
    MotifPlacement,
    OnsetBundle,
    OnsetEvent,
    OnsetJustification,
    PhraseBoundaryState,
    PhraseContext,
    PhraseControlIR,
    PhraseQuery,
    PhraseResult,
    StyleProgram,
)
from .motif_realization import (
    emit_motif_melody_events,
    first_scale_degree_midi,
    pick_motif_slot_for_bar,
)
from .pattern_retriever import PatternRetriever
from .phrase_bank import PhraseBank
from .pitch import (
    SCALE_INTERVALS,
    build_scale,
    chord_tones,
    clamp_to_range,
    is_minor_key,
    key_to_root_midi,
    midi_to_pitch,
    pitch_to_midi,
    snap_to_scale,
)

logger = logging.getLogger(__name__)


# ─── Internal dataclasses ─────────────────────────────────────────────────────


@dataclass
class GestureSlot:
    """A time span within a phrase where one gesture family operates."""

    bar_start: int = 1
    beat_start: float = 1.0
    bar_end: int = 1
    beat_end: float = 1.0
    span_beats: float = 4.0
    function: str = "continuation"  # pickup, answer, sequence, insist, cadential, arrival
    rh_texture: str = "singing_melody"
    lh_texture: str = "alberti"
    anchor_start: Anchor | None = None
    anchor_end: Anchor | None = None
    bass_anchors: list[Anchor] = field(default_factory=list)
    harmonic_cells: list[HarmonicCell] = field(default_factory=list)
    density_target: int = 8
    is_cadence_zone: bool = False
    #: Bars whose ACCOMPANIMENT this slot writes. Assigned across the whole slot
    #: list by `_assign_bar_ownership`, because "which slot owns this bar" cannot
    #: be answered from one slot alone — see the note there.
    owned_bars: list[int] = field(default_factory=list)


@dataclass
class SlotExitState:
    """Exit state from one gesture slot, feeds into the next."""

    last_melody_midi: int | None = None
    last_bass_midi: int | None = None
    last_beat: float = 1.0
    last_dynamic: str | None = None
    contour: str = ""  # ascending / descending / static


# ─── SurfaceComposer ──────────────────────────────────────────────────────────


def _duration_code_for(beats: Fraction) -> tuple[str, Fraction] | None:
    """The longest written duration that fits in `beats`, or None.

    Used to shorten a note the gesture profile made too long for the bar it
    lands in. Returns the code AND its exact length so the caller's cursor stays
    exact — returning only the code would put the cursor back on floats, which
    is the drift this module already had once.
    """
    best: tuple[str, Fraction] | None = None
    for code, value in DURATION_VALUES.items():
        span = value if isinstance(value, Fraction) else Fraction(str(value)).limit_denominator(96)
        if span <= beats and (best is None or span > best[1]):
            best = (code, span)
    return best


def _approach_the_cadence(bundles: list[OnsetBundle], control: PhraseControlIR) -> None:
    """Give a cadence bar an approach note instead of one held chord.

    Every phrase closed on a single note filling its whole bar — `E4dh` for the
    half cadence, `D4dh` for the perfect one — so all three phrase endings in a
    section shared one rhythm, which `detect_cadence_formula_reuse` calls the
    single loudest tell of a machine. A cadence is a GESTURE: the arrival is
    approached, and the approach is most of what makes it sound like an ending
    rather than a stop.

    The arriving pitch never moves — it is the harmonic goal. The note before it
    is a step above, which is the commonest cadential approach in the corpus
    (Bach's 2-1 outright; the others reach it as often as any other single
    figure).

    Only fires on a cadence bar whose melody is ONE long note. A cadence that
    already has a gesture is left alone.
    """
    from .duration import beats_to_dur, dur_to_beats

    cadence_bar = getattr(control, "cadence_bar", None)
    if not cadence_bar:
        return
    in_bar = [b for b in bundles if b.bar == cadence_bar]
    melodic = [
        (b, o) for b in in_bar for o in b.events if getattr(o, "voice", "") in ("soprano", "melody")
    ]
    if len(melodic) != 1:
        return
    bundle, onset = melodic[0]
    try:
        span = float(dur_to_beats(onset.duration))
    except (ValueError, KeyError, TypeError):
        return
    if span < 2:
        return

    approach_beats = 1.0 if span >= 3 else span / 2
    try:
        approach_code = beats_to_dur(approach_beats)
        arrival_code = beats_to_dur(span - approach_beats)
    except (ValueError, KeyError, TypeError):
        return

    pitch = onset.pitch[0] if isinstance(onset.pitch, list) else onset.pitch
    try:
        midi = pitch_to_midi(pitch)
    except (ValueError, KeyError, TypeError):
        return
    if midi is None:
        return

    # `local_key`, not `key`. PhraseControlIR has no `key` field at all, so
    # `getattr(control, "key", "")` returned the default and every cadence was
    # approached as though the piece were in C major — which put an F# above the
    # E of a D minor half cadence. Reading a field that does not exist, with a
    # default that hides it, is the defect I have spent this session removing
    # from other people's code.
    key = str(getattr(control, "local_key", "") or "C")

    # The next degree of the KEY's own scale, not a fixed number of semitones.
    # Which semitone step is diatonic depends on where in the scale you are.
    mode = "minor" if is_minor_key(key) else "major"
    tonic_pc = key_to_root_midi(key) % 12
    degrees = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
    scale_pcs = sorted({(tonic_pc + d) % 12 for d in degrees})
    above = [pc for pc in scale_pcs if (pc - midi) % 12 in (1, 2)]
    step_above = midi + (((above[0] - midi) % 12) if above else 2)

    approach = OnsetBundle(bar=bundle.bar, beat=float(bundle.beat))
    approach.harmonic_cell = bundle.harmonic_cell
    approach.events = [
        OnsetEvent(
            voice=getattr(onset, "voice", "soprano"),
            pitch=midi_to_pitch(step_above, key),
            duration=approach_code,
            role=NoteRole.NEIGHBOR.value,
        )
    ]
    onset.duration = arrival_code
    bundle.beat = float(bundle.beat) + approach_beats
    bundles.insert(bundles.index(bundle), approach)


def _merge_bundles_at_one_instant(bundles: list[OnsetBundle]) -> list[OnsetBundle]:
    """One bundle per (bar, beat), and one onset per voice inside it.

    The per-slot collapse cannot see across slots, and adjacent slots share an
    instant: a slot's opening anchor is written explicitly AND the gesture's own
    first note lands on that same beat. So a bar came out with two identical
    onsets on its downbeat —

        beat 1.000  G4  q     beat 2.000  G4  e     beat 3.000  A4  q
        beat 1.000  G4  q     beat 2.500  G4  e     beat 4.000  A4  e

    — 5.0 beats in a 4/4 bar, and the melody carrying the same duplication the
    accompaniment had before bar ownership was assigned.

    A layer is one voice, so at a shared instant one onset survives; the LONGER
    is kept, because the structural anchor outlasts the gesture note that landed
    on it. Different voices at the same instant are a chord and are left alone.
    """
    from .duration import dur_to_beats as _dtb

    def _span(onset) -> float:
        try:
            return float(_dtb(onset.duration))
        except (ValueError, KeyError, TypeError):
            return 0.0

    by_position: dict[tuple, OnsetBundle] = {}
    order: list[tuple] = []
    for bundle in bundles:
        key = (bundle.bar, round(float(bundle.beat), 4))
        target = by_position.get(key)
        if target is None:
            by_position[key] = bundle
            order.append(key)
            continue
        target.events.extend(bundle.events)

    for key in order:
        bundle = by_position[key]
        best: dict[str, object] = {}
        seq: list[str] = []
        for onset in bundle.events:
            voice = getattr(onset, "voice", "")
            if voice not in best:
                best[voice] = onset
                seq.append(voice)
            elif _span(onset) > _span(best[voice]):
                best[voice] = onset
        bundle.events = [best[v] for v in seq]

    ordered = [by_position[k] for k in order]
    _clip_to_next_onset_in_voice(ordered)
    return ordered


def _clip_to_next_onset_in_voice(bundles: list[OnsetBundle]) -> None:
    """Shorten any note that outlasts the next onset of its OWN voice.

    A decoration was being inserted between existing onsets without shortening
    the note it decorates, so a 4/4 bar held five and a half beats:

        beat 1.000  G4  q     (ends 2.0)
        beat 1.750  G4  s     <- starts inside the quarter
        beat 2.000  G4  h     (ends 4.0)
        beat 3.000  A4  q     <- starts inside the half

    A sixteenth before the beat means the note before it is a dotted eighth.
    That is what a composer writes, and it is what one hand can play: the
    earlier note ends where the next begins.

    Within a bar only. A note tied across a barline is legitimate writing and
    must not be shortened — the same boundary the reduction packer draws.
    """
    from .duration import dur_to_beats

    positions: dict[str, list[tuple[int, float, object]]] = {}
    for bundle in bundles:
        for onset in bundle.events:
            voice = getattr(onset, "voice", "")
            positions.setdefault(voice, []).append((bundle.bar, float(bundle.beat), onset))

    for entries in positions.values():
        entries.sort(key=lambda e: (e[0], e[1]))
        for index, (bar, beat, onset) in enumerate(entries):
            if index + 1 >= len(entries):
                continue
            next_bar, next_beat, _ = entries[index + 1]
            if next_bar != bar:
                continue
            room = next_beat - beat
            if room <= 0:
                continue
            try:
                span = float(dur_to_beats(onset.duration))
            except (ValueError, KeyError, TypeError):
                continue
            if span <= room + 1e-9:
                continue
            fitted = _duration_code_for(Fraction(str(round(room, 6))).limit_denominator(96))
            if fitted is not None:
                onset.duration = fitted[0]


def _thicken_principal_line(layer: LayerIR, key: str, share: float = 0.10) -> int:
    """Give the melody weight at its arrivals — thirds, sixths and octaves.

    Every melody this engine wrote was 100% single notes, so no moment sounded
    fuller than any other and a climax read as just another note. Real keyboard
    writing thickens 17% of right-hand attacks (measured over 206,000 attacks by
    Mozart, Beethoven, Chopin, Schubert, Haydn, Liszt and Brahms), and it is
    strongly personal: Haydn 6.7%, Mozart 8.5%, Beethoven 18.6%, Chopin 23.8%,
    Liszt 50.5%. 71% of those are two notes, and the commonest spacings are the
    octave, the third and the sixth — in that order.

    So this stays deliberately near the bottom of the real range. The added note
    always sits BELOW the melody, which keeps the line itself the top voice, and
    is always diatonic. The phrase's peak takes the octave because that is the
    one arrival worth the most weight.

    Runs AFTER the physical repair pass, not before: the repair clamps a note's
    duration against the next LATER onset, and a doubling shares its principal's
    onset, so thickening first made the repair re-measure every span it had
    already settled.
    """
    # `budget = max(1, round(n * share))` thickens one note even at share 0,
    # so a caller disabling this pass got a pass that still fired once — and a
    # control arm that was not a control. Its sibling passes guard this; this
    # one did not, which I asserted otherwise about before checking.
    if share <= 0:
        return 0
    notes = [e for e in layer.principal_line if e.pitch != "rest" and not isinstance(e.pitch, list)]
    if len(notes) < 8:
        return 0

    midis = {id(e): pitch_to_midi(e.pitch) for e in notes}
    notes = [e for e in notes if midis[id(e)] is not None]
    if len(notes) < 8:
        return 0

    # Never thicken an instant that already carries more than one note — the
    # composer put a chord there and it is not this pass's business.
    counts: dict = {}
    for e in layer.principal_line:
        counts[(e.bar, round(float(e.beat), 4))] = (
            counts.get((e.bar, round(float(e.beat), 4)), 0) + 1
        )

    mode = "minor" if is_minor_key(key) else "major"
    scale = build_scale(key_to_root_midi(key) + 24, mode, octaves=6)
    scale_pcs = {m % 12 for m in scale}

    structural = [e for e in notes if e.role == NoteRole.STRUCTURAL.value] or notes
    peak = max(notes, key=lambda e: midis[id(e)])

    # THE BUDGET IS IN INSTANTS, LESS WHAT IS ALREADY THICKENED.
    #
    # Measured against `len(notes)`, the pass counted its own output as input:
    # a second call saw more events, computed a bigger budget, and thickened
    # further. A revision loop runs these again, so a phrase revised twice came
    # out thicker than either the composer or the corpus asked for — the same
    # compounding that took a section from 7 dynamics to 9.
    already = sum(1 for n in counts.values() if n > 1)
    budget = max(1, round(len(counts) * share)) - already
    if budget <= 0:
        return 0
    chosen: list = [peak]
    if budget > 1 and len(structural) > 1:
        step = max(1, len(structural) // (budget - 1))
        for e in structural[::step]:
            if e is not peak and len(chosen) < budget:
                chosen.append(e)

    added = 0
    for event in chosen:
        instant = (event.bar, round(float(event.beat), 4))
        if counts.get(instant, 0) > 1:
            continue
        top = midis[id(event)]
        # The peak gets the octave; elsewhere a third, then a sixth.
        candidates = [12, 9, 8, 4, 3] if event is peak else [3, 4, 9, 8, 12]
        for interval in candidates:
            below = top - interval
            if below < MELODY_RANGE[0] or below % 12 not in scale_pcs:
                continue
            layer.principal_line.append(
                LayerEvent(
                    bar=event.bar,
                    beat=event.beat,
                    pitch=midi_to_pitch(below, key),
                    duration=event.duration,
                    role=event.role,
                    articulation=event.articulation,
                    source_layer="principal_line",
                )
            )
            counts[instant] = counts.get(instant, 0) + 1
            added += 1
            break

    if added:
        layer.principal_line.sort(key=lambda e: (e.bar, float(e.beat)))
    return added


class PassReport:
    """What a surface pass did, and — when it did nothing — why.

    Every surface pass returns the number of edits it made, and a pass that
    does nothing returns 0. So does a pass that correctly declined, one whose
    quota rounded away, one switched off by a zero rate, and one that never ran
    at all. Five states, one integer, and "0" reads as "there was nothing to do"
    in every log there is. That is the generator-side form of the thing this
    repo keeps finding on the checking side: something reporting nothing may be
    unable to report anything.

    It hid two separate faults in one afternoon. `_rest_the_downbeat` was inert
    on every planned piece because its theme guard was eating whole phrases, and
    `_hold_over_barline` was idle on three composers because "never swallow a
    structural arrival" excluded everything once a theme was placed. Both showed
    up as a plausible `0`, and both were located in one run once the passes said
    which condition was doing the declining.

    THE REASON, NOT ONLY THE COUNT. `declined: 9` says a pass is declining and
    not why; `{"theme statement": 7, "quota met": 2}` says which rule to look
    at. Shared by every surface pass so a section reports one shape:

        {"pass": "downbeat_rests", "ran": True, "considered": 41,
         "eligible": 4, "allowance": 1, "applied": 1,
         "declined": {"cadence bar": 9, "the downbeat is the bar's peak": 9}}

    `reason` replaces the per-bar breakdown when the pass exits before looking
    at any candidate — a zero rate, or material too short to judge.
    """

    __slots__ = ("name", "considered", "eligible", "allowance", "applied", "declined", "reason")

    def __init__(self, name: str):
        self.name = name
        self.considered = 0
        self.eligible = 0
        self.allowance = 0
        self.applied = 0
        self.declined: collections.Counter = collections.Counter()
        self.reason = ""

    def decline(self, why: str) -> None:
        """One candidate rejected, recorded under the rule that rejected it."""
        self.declined[why] += 1

    def stop(self, report, why: str) -> int:
        """The pass gives up. Records the reason, writes the report, returns 0.

        It writes the report itself so the two cannot be done in the wrong
        order — a first version left `_finish` to the caller and every early
        return published a report with the `reason` field missing, which is
        precisely the information the early returns exist to carry.
        """
        self.reason = why
        _finish(report, self)
        return 0

    def as_dict(self) -> dict:
        out = {
            "pass": self.name,
            "ran": True,
            "considered": self.considered,
            "eligible": self.eligible,
            "allowance": self.allowance,
            "applied": self.applied,
            "declined": dict(self.declined),
        }
        if self.reason:
            out["reason"] = self.reason
        return out

    @property
    def idle(self) -> bool:
        """Did nothing — which is worth surfacing whether or not it was right to."""
        return self.applied == 0


def _report_into(report, name: str) -> "PassReport":
    """A PassReport, writing through to the caller's dict if one was given."""
    made = PassReport(name)
    if report is not None:
        report.clear()
        report["_report"] = made
    return made


def _finish(report, made: "PassReport") -> None:
    if report is not None:
        report.pop("_report", None)
        report.update(made.as_dict())


def _rest_the_downbeat(
    layer: LayerIR,
    meter: tuple,
    share: float = 0.08,
    composer: str = "",
    bar_start: int = 1,
    protect_bars: frozenset = frozenset(),
    report: Optional[dict] = None,
) -> int:
    """Let the melody be silent at the top of a bar.

    A bar can lack a fresh downbeat attack two ways: the previous note is held
    across the barline, or the bar simply OPENS WITH A REST. `_hold_over_barline`
    covers the first. Nothing covered the second, and it is the larger share —
    real melodies rest on 5-12% of downbeats where they tie on 1-5%.

    Measured on this engine's own output: **zero** leading rests, in any layer,
    across two complete pieces. Not a low rate — none. Every bar of the melody
    began with an attack, and the 8-10% of leading rests visible in the exported
    left hand were the assembler PADDING bars where the accompaniment had no
    downbeat note, not composed silence. A statistic that looked healthy in the
    score and did not exist in the music.

    A bar is eligible only where the silence costs nothing structural: not the
    phrase's opening bar (the statement has to land), not a bar carrying a motif
    placement (the theme is the one thing that must be heard), not the cadence
    bar, and only where the note being removed is a passing or neighbour tone
    with real melody left after it in the bar. The rest is written explicitly,
    with the duration of the gap it opens, because an implicit gap is something
    the assembler fills and nobody chose.

    A PASS THAT DECLINES AND A PASS THAT NEVER RAN LOOK THE SAME. Both return 0.
    So does one whose quota rounded to nothing, one that found no eligible bar,
    and one switched off by a zero rate — four different states, one integer, and
    "0" reads as "correctly decided there was nothing to do" in every log we
    have. Pass a `report` dict to get the counts instead:

        {"considered": 12, "eligible": 5, "allowance": 2, "applied": 2,
         "declined": {"theme statement": 5, "no accompaniment on the downbeat": 2}}

    and, when the pass exits before looking at any bar, a single `reason`.

    The REASON matters more than the count. A bare `declined: 9` says the pass
    is declining and not why; the breakdown says which condition is doing it,
    which is what turns "this pass is inert" into "the theme guard is eating the
    whole phrase" without an A/B run. This shape is shared with the sibling
    surface passes so a section reports one thing.

    Rules taken from the sibling passes, each of which learned one the hard way:
    inert at `share <= 0`; the budget measured over ELIGIBLE bars rather than
    over whatever the pass has already written, so a second application finds
    the quota met and adds nothing; a running quota over absolute bar numbers so
    the rate is the piece's and not each phrase's; and no `max(1, ...)` floor,
    which would put one rest in every phrase whatever the composer's rate.
    """
    made = _report_into(report, "downbeat_rests")
    if share <= 0:
        return made.stop(report, "share is zero")
    if composer:
        from .composition_brief import downbeat_rest_rate

        measured = downbeat_rest_rate(composer)
        if measured is not None:
            share = measured
            if share <= 0:
                return made.stop(report, f"{composer} rests on no downbeats")

    from .duration import beats_to_dur, dur_to_beats, largest_dur_at_most

    line = sorted(
        (e for e in layer.principal_line if not isinstance(e.pitch, list)),
        key=lambda e: (e.bar, float(e.beat)),
    )
    if len(line) < 8:
        return made.stop(report, f"melody too short to judge ({len(line)} notes)")

    by_bar: dict[int, list] = {}
    for event in line:
        by_bar.setdefault(event.bar, []).append(event)

    cadence_bar = max(by_bar)
    # The bars carrying a theme statement come from the CALLER, which holds the
    # slot. A first version read a `NoteRole.MOTIF` off the events — there is no
    # such member, and the `hasattr` guard I had written around it would have
    # made the whole protection permanently dead while looking deliberate. The
    # theme is the one thing in the piece that must be heard; silencing its
    # downbeat is the single worst bar this pass could choose.
    protected = frozenset(protect_bars)

    # NOT THE PHRASE'S FIRST BAR — that exclusion was backwards.
    #
    # It looked obviously right ("the entry has to land") and cost more than any
    # other condition: on a 2/4 ternary it declined 18 of 41 bars, because a
    # four-bar phrase spends half its bars on an entry or a cadence. Measured
    # over the corpus by phrase position, an OPENING bar is where real melodies
    # rest MOST:
    #
    #     position     mozart  beethoven  schubert  haydn  bach
    #     opening       14.6%      12.2%     14.3%   9.2%  6.3%
    #     middle         8.3%      12.5%     10.6%   7.0%  7.0%
    #     cadential      4.7%       8.1%     14.5%   7.2%  3.4%
    #
    # A phrase that begins with a rest is an upbeat entry, which is ordinary
    # writing and is the thing `metric_entry: anacrusis` already names. The
    # cadence bar stays excluded: it is the arrival, and it is the position
    # where the classical composers do this least.
    #
    # WHAT MAKES A DOWNBEAT SAFE TO SILENCE.
    #
    # Not the note's role. A first version required the removed note to be a
    # passing or neighbour tone, which measured one eligible bar in twenty-two:
    # this generator anchors a STRUCTURAL note on nearly every downbeat, so the
    # rule could almost never fire. The role is also not the musical question.
    # When a real melody rests at the top of a bar the note is simply not
    # written and the line enters later; what has to remain true is that the bar
    # still states its harmony and still has a melody.
    #
    # So: the accompaniment must sound on that downbeat (the harmony is stated
    # without the melody), the bar must keep real melodic content after the
    # rest, and the note removed must not be the bar's melodic peak — silencing
    # the highest note in a bar is silencing the thing it was shaped toward.
    bass_downbeats = {
        e.bar
        for e in (layer.bass_foundation or []) + (layer.response_layer or [])
        if e.pitch != "rest" and abs(float(e.beat) - 1.0) < 1e-6
    }
    eligible = []
    for bar in sorted(by_bar):
        if bar == cadence_bar:
            made.decline("cadence bar")
            continue
        if bar in protected:
            made.decline("theme statement")
            continue
        if bar not in bass_downbeats:
            made.decline("no accompaniment on the downbeat")
            continue
        events = by_bar[bar]
        # TWO, not three. A bar whose melody is a rest and then one note is
        # ordinary writing — in 2/4 it is a half-bar rest and an entry — and
        # requiring three left a four-bar phrase in 2/4 with ZERO eligible bars,
        # so the piece's quota landed on phrases that could not spend it.
        if len(events) < 2:
            made.decline("too few melody notes in the bar")
            continue
        head, nxt = events[0], events[1]
        if head.pitch == "rest" or nxt.pitch == "rest":
            made.decline("already silent")
            continue
        if getattr(head, "tie", None) or getattr(nxt, "tie", None):
            made.decline("tied")
            continue
        if abs(float(head.beat) - 1.0) > 1e-6:
            made.decline("bar already starts late")
            continue  # nothing to silence: the bar already starts late
        tops = [pitch_to_midi(e.pitch) for e in events if e.pitch != "rest"]
        tops = [m for m in tops if m is not None]
        head_midi = pitch_to_midi(head.pitch)
        if tops and head_midi is not None and head_midi >= max(tops):
            made.decline("the downbeat is the bar's peak")
            continue  # the bar's peak is not a note to delete
        gap = float(nxt.beat) - float(head.beat)
        if gap <= 0:
            continue
        eligible.append((bar, head, gap))
    made.considered = len(by_bar)
    made.eligible = len(eligible)
    if not eligible:
        return made.stop(report, "no bar could take a rest")

    # AN EXACT RUNNING QUOTA OVER ABSOLUTE BARS.
    #
    # Three ways to get this wrong, and the first two were mine. A quota of
    # `round(len(phrase_bars) * share)` is zero for every four-bar phrase at any
    # real rate (4 x 0.083 rounds to 0), so it can never produce the rate;
    # `max(1, ...)` is the mirror of it and puts one rest in every phrase
    # whatever the composer does. Replacing it with an independent per-bar draw
    # fixed the bias and left the variance: with two eligible bars in a phrase
    # and a draw of 0.17, most phrases still got none, and Mozart came out at
    # 6.0% against his 8.3% and Beethoven at 2.4% against his 11.1%.
    #
    # This phrase's exact share of the piece's total is the difference between
    # the running quotas at its last and first bars. It needs no state carried
    # between phrases, has no variance, and sums to the composer's own rate over
    # the whole work however the phrases are cut.
    # THE QUOTA IS EXACT AND SOME OF IT IS FORFEITED. Both halves are true and
    # the second is a known shortfall, not an oversight.
    #
    # This phrase's exact share of the piece's total is the difference between
    # the running quotas at its last and first ABSOLUTE bars. It needs no state
    # carried between phrases, has no variance, and sums to the composer's own
    # rate over the whole work however the phrases are cut. What it cannot do is
    # move an allowance to a phrase that can spend it: over a 41-bar ternary it
    # allotted three rests and two landed on phrases with ZERO eligible bars,
    # where they were forfeited. Measured result, against each composer's own
    # rate: sonatas 6.0-7.2% against 8.3-11.1%, ternaries 2.4-7.3% against
    # 7.5-11.6%. Short, never over.
    #
    # Weighting the quota by each phrase's eligible fraction was tried and
    # OVERSHOT — a phrase with few eligible bars gets weighted up by more than
    # it was starved, and Beethoven came out at 18.1% against his 11.1%. For a
    # pass that removes notes, short is the safe error: a melody that breathes
    # slightly less often than Beethoven's is still a melody, and one that
    # breathes twice as often is a different piece. Closing the gap properly
    # means carrying the deficit between phrases, which is state this function
    # deliberately does not have.
    lo, hi = min(by_bar), max(by_bar)
    allowance = int(hi * share) - int((lo - 1) * share)
    already = sum(1 for events in by_bar.values() if events and events[0].pitch == "rest")
    allowance -= already
    made.allowance = allowance
    if allowance <= 0:
        return made.stop(report, "this phrase's share of the piece's quota is already met")

    # Spread across the phrase rather than taking the first N in a row.
    if len(eligible) > allowance:
        step = len(eligible) / allowance
        eligible = [eligible[min(len(eligible) - 1, int(i * step))] for i in range(allowance)]

    done = 0
    for bar, head, gap in eligible:
        duration = beats_to_dur(gap) or largest_dur_at_most(gap)
        if duration is None or (dur_to_beats(duration) or 0) <= 0:
            continue
        head.pitch = "rest"
        head.duration = duration
        head.tie = None
        head.articulation = None
        head.ornament = None
        done += 1
    made.applied = done
    _finish(report, made)
    return done


def _hold_over_barline(
    layer: LayerIR,
    meter: tuple,
    share: float = 0.09,
    composer: str = "",
    protect_bars: frozenset = frozenset(),
) -> int:
    """Let the melody lean into the next bar instead of restarting every time.

    Every bar of this engine's melody began with an attack on beat 1, because
    `_build_anchors` places a downbeat anchor in every bar. Real keyboard
    writing does not: measured over 40,000 bars, **89.8%** begin with a
    right-hand attack — Mozart 91.7%, Beethoven 88.9%, Schubert 88.4%, Liszt
    63.1%. The missing tenth is the difference between a line that breathes and
    one that resets, and it is why `tie_absent` could report that nothing in the
    piece was ever held over a barline.

    A bar is chosen only when holding into it displaces nothing structural: the
    note being absorbed must be a passing or neighbour tone, and the held pitch
    must be in the key so the downbeat it now covers stays consonant. The held
    note is written as a tied pair, which is what an engraver writes and what
    the MIDI preview sounds.
    """
    if share <= 0:
        return 0
    # HOW OFTEN, from the composer's own music. Real practice varies eightfold —
    # Haydn 0.015 ties per bar, Beethoven 0.134, Palestrina 0.192 — and a fixed
    # 0.09 was right for nobody but Mozart and Chopin. Measured at 0.09 the
    # engine tied Haydn eight times his own rate and Chopin three times his.
    # `tie_rate_per_bar` returns None where the corpus cannot answer (Schubert,
    # Liszt and Brahms carry no ties in their sources at all), and then the
    # generic rate stands rather than a zero that is really a missing encoding.
    if composer:
        from .composition_brief import tie_rate_per_bar

        measured = tie_rate_per_bar(composer)
        if measured is not None:
            share = measured
            if share <= 0:
                return 0
    events = sorted(
        (e for e in layer.principal_line if e.pitch != "rest" and not isinstance(e.pitch, list)),
        key=lambda e: (e.bar, float(e.beat)),
    )
    if len(events) < 12:
        return 0

    from .duration import dur_to_beats

    cap = float(bar_duration(meter))
    key = layer.key or "C major"
    mode = "minor" if is_minor_key(key) else "major"
    scale_pcs = {m % 12 for m in build_scale(key_to_root_midi(key) + 24, mode, octaves=6)}

    # A TIE JOINS ONE NOTE TO ONE NOTE.
    #
    # `_thicken_principal_line` runs first, so an arrival may already be a
    # chord. Tying a two-note chord to a single note is not a tie anyone can
    # engrave, and music21 resolved it by splitting off a 1/48 stub that
    # started exactly ON the barline — four bars of every 3/8 piece exporting
    # at 73/48 of a 3/8 bar.
    occupancy: dict = {}
    for e in layer.principal_line:
        instant = (e.bar, round(float(e.beat), 4))
        occupancy[instant] = occupancy.get(instant, 0) + 1

    absorbable = {NoteRole.PASSING.value, NoteRole.NEIGHBOR.value}
    candidates = []
    for a, b in zip(events, events[1:]):
        # ALREADY TIED. Nothing filtered these, so a second call re-selected the
        # same pair, re-set the same two fields, and returned 1 — reporting work
        # it had not done. The state was idempotent and the COUNT was not, which
        # is the harder half to notice.
        if a.tie or b.tie:
            continue
        if occupancy.get((a.bar, round(float(a.beat), 4)), 0) > 1:
            continue
        if occupancy.get((b.bar, round(float(b.beat), 4)), 0) > 1:
            continue
        if b.bar != a.bar + 1 or abs(float(b.beat) - 1.0) > 1e-6:
            continue
        if abs((float(a.beat) + float(dur_to_beats(a.duration))) - (1.0 + cap)) > 1e-6:
            continue
        # A SUSPENSION DISPLACES A STRUCTURAL ARRIVAL — that is what makes it a
        # suspension. Refusing every structural downbeat was safe while nothing
        # else protected the theme, but once a theme is placed almost every
        # downbeat is structural and this pass went idle on Bach, Haydn and
        # Schubert alike: Schubert's quota granted four ties and found nothing
        # eligible for one. The bars that must keep their downbeat are the ones
        # where the theme is STATED, and `_theme_statement_bars` reconstructs
        # exactly those; everywhere else a held note over the barline is the
        # ordinary device rather than a loss.
        #
        # The repeated-pitch case stays as its own reason: `_build_anchors` puts
        # an anchor on every downbeat, so a pitch repeating across the barline
        # is an artifact of that placement and one held note is what anyone
        # would write.
        if b.bar in protect_bars:
            continue
        if b.role not in absorbable and a.pitch != b.pitch and b.role != NoteRole.STRUCTURAL.value:
            continue
        midi = pitch_to_midi(a.pitch)
        if midi is None or midi % 12 not in scale_pcs:
            continue
        candidates.append((a, b))

    if not candidates:
        return 0

    # Less the ties already there, so a revision loop does not add a fresh
    # budget's worth on every pass — the same compounding the thickening passes
    # had against `len(events)`.
    # A RUNNING QUOTA OVER THE PIECE'S BARS, not `max(1, ...)` per phrase.
    #
    # The floor of 1 guaranteed a tie in every phrase whatever the rate, so the
    # composer-relative rate above changed nothing at all: nine phrases meant
    # nine ties whether the composer was Beethoven at 0.134 per bar or Haydn at
    # 0.015. Third time today a `max(1, round(n * share))` has made a share
    # ornamental.
    #
    # Counting from the phrase's absolute bar numbers gives the piece the right
    # rate without any state between calls: a phrase earns a tie exactly when
    # the running quota crosses a whole number inside it. Haydn gets none in a
    # 41-bar piece (his real rate predicts 0.6); Beethoven gets five (5.5).
    first_bar = min(e.bar for e in events)
    last = max(e.bar for e in events)
    # ROUND, not truncate. `int()` discards the fraction at every phrase
    # boundary, so a 41-bar Mozart piece at his measured 0.070 per bar — 2.9
    # ties — was granted its first only past bar 15 and landed none at all.
    # Rounding totals `round(41 * 0.070) = 3`, which is the rate.
    quota = round(last * share) - round((first_bar - 1) * share)
    already = sum(1 for e in layer.principal_line if e.tie == "start")
    budget = quota - already
    if budget <= 0:
        return 0
    step = max(1, len(candidates) // budget)
    held = 0
    for a, b in candidates[::step]:
        if held >= budget:
            break
        # `b` becomes the CONTINUATION of `a` rather than a new attack.
        a.tie = "start"
        b.pitch = a.pitch
        b.tie = "stop"
        b.role = a.role
        b.articulation = None
        b.ornament = None
        held += 1
    return held


def _thicken_bass_foundation(layer: LayerIR, key: str, share: float = 0.15) -> int:
    """Give the left hand weight — thirds, fifths and octaves above the bass.

    Every accompaniment this engine wrote was single notes: 11 distinct LH
    bar-shapes across 41 bars of 3/8, against a real Mozart 3/8 minimum of 14
    and a median of 19. The shapes were thin because the *chord sizes* were all
    1, and real left hands are not: **Mozart 18.5% of LH attacks are chords,
    Beethoven 22.1%, Schubert 36.9%, Chopin 37.9%, Haydn 11.9%** — over 164,000
    attacks. Two notes in the great majority, then three.

    The added note goes ABOVE the bass, which is the mirror of the melody rule:
    there the tune must stay the top voice, here the bass must stay the bottom
    one. It is diatonic, it never exceeds an octave (so one hand can take it),
    and it never lands on an instant that already carries more than one note —
    that is a texture the composer chose.
    """
    if share <= 0:
        return 0
    events = [
        e for e in layer.bass_foundation if e.pitch != "rest" and not isinstance(e.pitch, list)
    ]
    if len(events) < 8:
        return 0

    midis = {id(e): pitch_to_midi(e.pitch) for e in events}
    events = [e for e in events if midis[id(e)] is not None]
    if len(events) < 8:
        return 0

    occupancy: dict = {}
    for e in layer.bass_foundation:
        instant = (e.bar, round(float(e.beat), 4))
        occupancy[instant] = occupancy.get(instant, 0) + 1

    mode = "minor" if is_minor_key(key) else "major"
    scale_pcs = {m % 12 for m in build_scale(key_to_root_midi(key) + 24, mode, octaves=6)}

    # A downbeat is where an accompaniment takes its weight.
    on_beat = [e for e in events if abs(float(e.beat) - round(float(e.beat))) < 1e-6]
    preferred = on_beat or events

    # In INSTANTS, less what is already a chord — see `_thicken_principal_line`.
    already = sum(1 for n in occupancy.values() if n > 1)
    budget = max(1, round(len(occupancy) * share)) - already
    if budget <= 0:
        return 0
    step = max(1, len(preferred) // budget)
    added = 0
    for event in preferred[::step]:
        if added >= budget:
            break
        instant = (event.bar, round(float(event.beat), 4))
        if occupancy.get(instant, 0) > 1:
            continue
        bottom = midis[id(event)]
        # THE INTERVAL DEPENDS ON THE REGISTER, and trying a third first
        # regardless produced eleven `muddy_low_interval` warnings where there
        # had been none. Measured over 41,000 real left-hand chords by Mozart,
        # Beethoven, Chopin, Haydn and Schubert, the interval above the bass is:
        #
        #     bass below C2   median 12 semitones, only 4.8% under a fourth
        #     bass C2-C3      median 12,           17.0% under a fourth
        #     bass C3-C4      median  4,           50.7% under a fourth
        #     bass above C4   median  4,           77.2% under a fourth
        #
        # Low in the register the partials of a third collide and the sound is
        # mud; a tenth or an octave is what a pianist actually plays down there.
        # Above C3 the third is right and is what the corpus does half the time.
        if bottom < 48:
            preferred = (12, 7, 9, 8, 4, 3)
        else:
            preferred = (3, 4, 7, 12, 8, 9)
        for interval in preferred:
            above = bottom + interval
            if above > BASS_RANGE[1] or above % 12 not in scale_pcs:
                continue
            layer.bass_foundation.append(
                LayerEvent(
                    bar=event.bar,
                    beat=event.beat,
                    pitch=midi_to_pitch(above, key),
                    duration=event.duration,
                    role=event.role,
                    articulation=event.articulation,
                    source_layer="bass_foundation",
                )
            )
            occupancy[instant] = occupancy.get(instant, 0) + 1
            added += 1
            break

    if added:
        layer.bass_foundation.sort(key=lambda e: (e.bar, float(e.beat)))
    return added


#: How a phrase's last bar behaves, by the kind of close it is.
#: `full_stop` — the cadence note arrives on the downbeat and is held.
#: `breathe`   — the note is shortened so a rest opens before the next phrase.
#: `carry_on`  — nothing changes; the line is not stopping here.
_CADENCE_SHAPE = {
    "PAC": "full_stop",
    "plagal": "full_stop",
    "HC": "breathe",
    "IAC": "carry_on",
    "evaded": "carry_on",
    "deceptive": "breathe",
    "none": "carry_on",
}


def _shape_the_bass_cadence(layer: LayerIR, bar_len, shape: str, last_bar: int) -> bool:
    """The accompaniment's own close, matched to the kind of cadence it is.

    A full stop rests the bass on its final note for the bar; a half cadence
    leaves it short so the texture opens before the next phrase. Both change the
    cadential rhythm of the LEFT-HAND staff, which `cadence_formula` measures
    separately and which was the staff still tripping it.
    """
    from .duration import beats_to_dur, dur_to_beats

    events = sorted(
        (e for e in layer.bass_foundation if e.bar == last_bar and e.pitch != "rest" and not e.tie),
        key=lambda e: float(e.beat),
    )
    if not events:
        return False
    final = events[-1]
    if shape == "full_stop":
        if len(events) < 2:
            return False
        held = beats_to_dur(bar_len)
        if held is None:
            return False
        # Keep whatever sounds WITH the final note — the thickening may have put
        # a chord there and a full stop is the last place to thin one out.
        at_final = [e for e in events if abs(float(e.beat) - float(final.beat)) < 1e-6]
        for e in events:
            if e not in at_final:
                layer.bass_foundation.remove(e)
        for e in at_final:
            e.beat = 1.0
            e.duration = held
        return True
    span = Fraction(str(dur_to_beats(final.duration))).limit_denominator(96)
    shorter = beats_to_dur(span / 2)
    if shorter is None or span / 2 <= 0:
        return False
    final.duration = shorter
    return True


def _shape_the_cadence(layer: LayerIR, meter: tuple, cadence: str, last_bar: int) -> bool:
    """Let the close depend on what kind of close it is.

    Every phrase ending this engine wrote had the identical rhythm — a quarter
    then an eighth — for a perfect authentic cadence, a half cadence, an evaded
    one and a plagal Amen alike. Seven of nine endings in one piece, where real
    Mozart reuses a cadential rhythm in a third to a half of his. The cadence
    TYPE was known all along and simply never reached the rhythm.

    A perfect authentic cadence is a full stop: the cadence note lands on the
    downbeat and is held. A half cadence is a comma: the note is shortened and a
    rest opens after it. An evaded cadence is not stopping at all, so it is left
    alone — which is the whole point of an evaded cadence.
    """
    shape = _CADENCE_SHAPE.get((cadence or "none").strip(), "carry_on")
    if shape == "carry_on":
        return False

    from .duration import beats_to_dur, dur_to_beats

    bar_len = Fraction(str(bar_duration(meter))).limit_denominator(96)

    # THE BASS CLOSES TOO. Shaping only the melody left the accompaniment
    # playing the same cadential figure at every phrase end: 78% reuse on the
    # left-hand staff, against a real p90 of 76% (median 39%) measured over 267
    # movements. The melody was already inside its own range at 44%, and the
    # two staves are measured separately.
    _shape_the_bass_cadence(layer, bar_len, shape, last_bar)

    events = sorted(
        (e for e in layer.principal_line if e.bar == last_bar and e.pitch != "rest" and not e.tie),
        key=lambda e: float(e.beat),
    )
    if not events:
        return False
    final = events[-1]

    if shape == "full_stop":
        # The cadence pitch arrives on the downbeat and holds the bar. Anything
        # else in the melody's last bar is the approach to it, and a full stop
        # does not keep moving underneath itself.
        if len(events) < 2:
            return False
        held = beats_to_dur(bar_len)
        if held is None:
            return False
        for e in events[:-1]:
            layer.principal_line.remove(e)
        final.beat = 1.0
        final.duration = held
        return True

    # `breathe`: shorten the last note so a rest opens before the next phrase.
    span = Fraction(str(dur_to_beats(final.duration))).limit_denominator(96)
    shorter = beats_to_dur(span / 2)
    if shorter is None or span / 2 <= 0:
        return False
    final.duration = shorter
    return True


def _clamp_to_period_register(layer: LayerIR, composer: str) -> int:
    """Bring notes back inside the keyboard the composer actually had.

    `MELODY_RANGE` was widened to 55..90 from the measured distribution of real
    melody notes over an accompaniment — across every composer at once. But
    Bach's harpsichord stops at 86 and Mozart's fortepiano at 89, so a Baroque
    pastiche gained a climax on a note the instrument did not have. Not a
    physical constraint on a modern piano, which is why `score_realism` only
    warns; but the fix improves the music as well, because the register a
    composer wrote in is part of how he sounds.

    Displaced by OCTAVES, not clamped: an octave keeps the pitch class and the
    line's shape, where a clamp flattens every note above the ceiling onto the
    ceiling and invents a repeated note that was never written.

    The table is `score_realism._HISTORICAL_KEYBOARD` — imported rather than
    restated, because two copies of a range table is how one of them goes stale.
    """
    from .score_realism import _HISTORICAL_KEYBOARD

    span = _HISTORICAL_KEYBOARD.get((composer or "").strip().lower())
    if not span:
        return 0
    low, high = span
    moved = 0
    for name in ALL_LAYERS:
        for event in getattr(layer, name, None) or []:
            pitch = getattr(event, "pitch", None)
            if not pitch or pitch == "rest" or isinstance(pitch, list):
                continue
            midi = pitch_to_midi(pitch)
            if midi is None:
                continue
            shifted = midi
            while shifted > high:
                shifted -= 12
            while shifted < low:
                shifted += 12
            if shifted != midi and low <= shifted <= high:
                event.pitch = midi_to_pitch(shifted, layer.key or "C")
                moved += 1
    return moved


# The register a melody is allowed to occupy, measured rather than assumed.
#
# This was 60..84 — two octaves, C4 to C6. Across 33,773 melody notes written
# over an accompaniment by Mozart, Beethoven, Chopin, Liszt, Schubert, Haydn and
# Brahms, that clamp excluded 4.6% below and 7.3% above: an eighth of what real
# melodies actually play. Worse, 24 semitones is narrower than the median span
# of a real keyboard movement's melody (33 semitones over 336 movements), so no
# piece this generator wrote could reach an ordinary register range — the
# `register_stasis` audit was reading a ceiling, not a choice.
#
# 55..90 spans the same corpus's 1st to 99th percentile, leaving room above the
# left hand (clamped 36..60) for the two to stay out of each other's way.
MELODY_RANGE = (55, 90)

#: The register the left hand occupies, so the one bound has one name.
BASS_RANGE = (36, 60)


def _eighth_positions(bar_dur: float) -> list[float]:
    """Every eighth-note position in a bar of this length, one-based.

    The accompaniment used hardcoded lists — `[1.0, 1.5, ... 4.5] if bar_dur >= 4
    else [1.0, 1.5, 2.0, 2.5]` — guarded by `if beat > bar_dur`. Both halves are
    wrong, and in opposite directions, because BEATS ARE ONE-BASED: a bar of
    length `d` spans `[1.0, 1.0 + d)`.

    In 4/4 the guard cut beat 4.5, dropping the last half of every bar. In 3/8
    (bar_dur 1.5) the list offered 2.0 and 2.5 — which ARE in the bar — and the
    short metres came back with 9 to 17 notes dropped per phrase by the surface
    repair.

    Deriving the positions from the bar makes both the list and the guard
    unnecessary: 3/8 gets three, 4/4 gets eight, 7/8 gets seven.
    """
    positions: list[float] = []
    offset = 0.0
    while offset < bar_dur - 1e-9:
        positions.append(round(1.0 + offset, 6))
        offset += 0.5
    return positions or [1.0]


def _strong_step_indices(dur_profile: list[str], bar_dur: float) -> frozenset[int]:
    """Which steps of a duration profile land on a strong beat.

    One-based to match the interpolator's `step` counter. Beats 1 and 3 of a
    four-beat bar, beat 1 of a three-beat one — the positions a listener hears
    against the harmony.
    """
    from .duration import dur_to_beats

    strong = {1.0, 3.0} if bar_dur >= 4 else {1.0}
    out: set[int] = set()
    beat = 1.0
    for index, code in enumerate(dur_profile or [], start=1):
        if round(((beat - 1.0) % bar_dur) + 1.0, 4) in strong:
            out.add(index)
        try:
            beat += float(dur_to_beats(code))
        except (ValueError, KeyError, TypeError):
            beat += 1.0
    return frozenset(out)


def _follow_harmony_per_bar(events: list, slot: GestureSlot, key: str, voicing_map=None) -> None:
    """Re-spell a melody note the harmony of ITS OWN BAR has altered.

    `_scale_following_harmony` applies one scale to a whole gesture slot, but a
    slot spans several bars and the harmony changes within it. So where bar 6
    carried a secondary dominant, the accompaniment played its raised note while
    the melody kept the natural:

        D minor  bar 6:  G#2 in the bass, G4 in the melody
        A minor  bar 6:  D#3 in the bass, D5 in the melody

    which is a false relation, and the commonest one in minor-key writing
    precisely because the raised degrees come and go with the harmony.

    Per bar, and only for a chord tone the KEY does not contain — a raised
    fourth or leading tone that this bar's chord introduces. A note already
    belonging to the chord is left alone, and so is one a whole tone away, which
    is a different degree rather than an alteration of this one.
    """
    if not events:
        return
    by_bar: dict[int, frozenset[int]] = {}
    for cell in getattr(slot, "harmonic_cells", None) or []:
        bar = getattr(cell, "bar", None)
        if bar is None:
            continue
        one = GestureSlot(bar_start=bar, beat_start=1.0, bar_end=bar, beat_end=2.0)
        one.harmonic_cells = [cell]
        by_bar[bar] = _slot_chord_pcs(one, key, voicing_map)
    if not by_bar:
        return

    mode = "minor" if is_minor_key(key) else "major"
    tonic_pc = key_to_root_midi(key) % 12
    degrees = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
    in_key = {(tonic_pc + d) % 12 for d in degrees}

    for event in events:
        pcs = by_bar.get(getattr(event, "_bar", None))
        if not pcs:
            continue
        pitch = event.pitch[0] if isinstance(event.pitch, list) else event.pitch
        if not pitch or pitch == "rest":
            continue
        try:
            midi = pitch_to_midi(pitch)
        except (ValueError, KeyError, TypeError):
            continue
        if midi is None or midi % 12 in pcs:
            continue
        raised = next(
            (pc for pc in pcs if pc not in in_key and (pc - midi) % 12 == 1),
            None,
        )
        if raised is not None:
            event.pitch = midi_to_pitch(midi + 1, key)


def _scale_following_harmony(scale: list[int], chord_pcs: frozenset[int]) -> list[int]:
    """The scale with any degree the harmony has ALTERED replaced by the chord's.

    The melody walked a fixed diatonic scale while the accompaniment built from
    the local chord, so the two disagreed about the same degree: a secondary
    dominant put F# in the harmony while the D-minor scale gave the melody F
    natural, and every cross-relation in a realized section was that one
    disagreement reported at several beats.

    A composer does not keep playing the diatonic note over an altered chord —
    the raised degree IS the chromatic inflection, and it is most of what makes
    a minor-key line sound like music rather than like a mode.

    Two rules earn their place, both learned by getting it wrong:

    * Only a chord tone the scale does NOT already contain is an alteration.
      Without this a plain D minor triad pulled the scale's E to F, because E is
      a semitone from F and F is a chord tone — destroying a legitimate degree
      and leaving F in the scale twice.

    * An alteration replaces exactly ONE degree, the one it inflects. Replacing
      every neighbour pulled the TONIC D to C# under an A7, because C# is a
      semitone from both C and D. An alteration is normally a raised degree, so
      the note a semitone BELOW it is the one it came from.
    """
    if not chord_pcs or not scale:
        return scale
    present = {m % 12 for m in scale}
    alterations = [pc for pc in sorted(chord_pcs) if pc not in present]
    if not alterations:
        return scale

    replaces: dict[int, int] = {}
    for altered in alterations:
        below = (altered - 1) % 12
        above = (altered + 1) % 12
        source = below if below in present else (above if above in present else None)
        if source is None or source in replaces:
            continue
        replaces[source] = altered

    if not replaces:
        return scale
    out: list[int] = []
    for midi in scale:
        altered = replaces.get(midi % 12)
        if altered is None:
            out.append(midi)
            continue
        shifted = midi + ((altered - (midi % 12) + 6) % 12) - 6
        out.append(shifted)
    return out


def _slot_chord_pcs(slot: GestureSlot, key: str, voicing_map=None) -> frozenset[int]:
    """Pitch classes of the chords this slot sits over.

    Reads the SOLVED voicing when there is one. The accompaniment is built from
    `voicing_map` — what `harmonic_solver` actually voiced, sevenths, inversions
    and voice-leading alterations included — while this used to re-derive a
    plain triad from the cell's roman numeral. Two derivations of the same
    harmony, free to disagree, and they did: the accompaniment played F# from a
    solved dominant seventh while the melody was told the chord was D minor and
    kept its F natural. Every remaining cross-relation in a realized section was
    that one disagreement.

    Duplicated derivations of one fact are this repo's first source of bugs. The
    roman is still the fallback, for callers with no solved voicing to hand.
    """
    pcs: set[int] = set()
    for cell in getattr(slot, "harmonic_cells", None) or []:
        voiced = (voicing_map or {}).get(getattr(cell, "bar", None))
        if voiced:
            for field, value in voiced.items():
                if field.endswith("_midi") and isinstance(value, int):
                    pcs.add(value % 12)
            if pcs:
                continue
        quality = str(getattr(cell, "quality", "") or "major").lower()
        roman = str(getattr(cell, "roman", "") or "")
        try:
            root = key_to_root_midi(str(getattr(cell, "key", "") or key)) + 48
        except (ValueError, KeyError, TypeError):
            continue
        if roman and roman[:1].islower():
            quality = "minor"
        try:
            for midi in chord_tones(root, quality if quality in ("major", "minor") else "major"):
                pcs.add(midi % 12)
        except (ValueError, KeyError, TypeError):
            continue
    return frozenset(pcs)


def _degree_number(value) -> int | None:
    """The scale-degree number in an anchor written as `^5`, `^b6`, `^#4`.

    Returns None for a pitch name, which is the caller's signal to use MIDI.
    """
    text = str(value or "").strip()
    if not text.startswith("^"):
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else None


class SurfaceComposer:
    """Phrase-level, context-driven onset bundle composer.

    Composes melody and accompaniment together per gesture slot,
    using retrieved phrase prototypes, gesture families, and
    pattern families from corpus data.
    """

    def __init__(
        self,
        pattern_retriever: PatternRetriever,
        phrase_bank: PhraseBank | None = None,
        gesture_bank: GestureBank | None = None,
        corpus_bar_retriever: CorpusBarRetriever | None = None,
        cadence_bank: CadenceBank | None = None,
        motif_bank: dict[str, Any] | None = None,
    ):
        self.pattern_retriever = pattern_retriever
        self.phrase_bank = phrase_bank
        self.gesture_bank = gesture_bank
        self.corpus_bar_retriever = corpus_bar_retriever
        self.cadence_bank = cadence_bank
        self.motif_bank = motif_bank or {}

    # ─── Public API ───────────────────────────────────────────────────────

    def compose(
        self,
        control: PhraseControlIR,
        phrase_context: PhraseContext,
        harmonic_voicings: list[dict],
        style_program: StyleProgram,
        continuation: PhraseBoundaryState | None = None,
        variant: int = 0,
    ) -> tuple[list[OnsetBundle], ContextTrace]:
        """Compose a phrase as coordinated onset bundles.

        Pipeline:
        1. Select phrase prototype from PhraseBank
        2. Plan gesture slots between melody anchors
        3. Co-compose melody + accompaniment per slot
        4. Integrate cadences
        5. Apply dynamics, breathing, boundary states
        """
        trace = ContextTrace(
            phrase_id=control.phrase_id,
            total_bar_count=control.bars,
        )
        voicing_map = self._index_voicings(harmonic_voicings)
        key = control.local_key
        mode = "minor" if is_minor_key(key) else "major"
        root = key_to_root_midi(key)
        scale = build_scale(root + 60, mode)
        bar_dur = bar_duration(control.meter)

        # Stage 1: Phrase prototype
        prototype = self._select_prototype(control, phrase_context, style_program, trace)

        # Stage 2: Gesture slot planning
        slots = self._plan_gesture_slots(control, voicing_map, prototype)

        # Stage 3: Co-composed realization per slot
        all_bundles: list[OnsetBundle] = []
        prev_exit = SlotExitState()
        if continuation and continuation.pitch:
            prev_exit.last_melody_midi = pitch_to_midi(continuation.pitch)
            prev_exit.last_dynamic = getattr(continuation, "dynamic", None)

        for slot in slots:
            slot_bundles, prev_exit = self._realize_slot(
                slot,
                control,
                phrase_context,
                voicing_map,
                style_program,
                scale,
                key,
                mode,
                root,
                bar_dur,
                variant,
                prev_exit,
                trace,
            )
            all_bundles.extend(slot_bundles)

        # Stage 5: Dynamics from sketch
        self._apply_dynamics(all_bundles, control)

        # Stage 5b: Breathing
        if phrase_context.breathing_plan:
            self._apply_breathing(all_bundles, phrase_context.breathing_plan, control, trace)

        all_bundles.sort(key=lambda b: (b.bar, b.beat))
        all_bundles = _merge_bundles_at_one_instant(all_bundles)
        # AFTER the collapse, not before. A first attempt ran this per slot and
        # skipped any cadence bar still holding two onsets at one instant — which
        # is most of them at that point, since the duplicates are only resolved
        # here. The beam then picked a candidate the helper had skipped, and the
        # cadences came out as repeated notes: measurably worse than the single
        # held note it was trying to improve on.
        _approach_the_cadence(all_bundles, control)
        return all_bundles, trace

    def bundles_to_layer_ir(
        self,
        bundles: list[OnsetBundle],
        phrase_id: str,
        key: str,
        meter: tuple[int, int],
        bar_count: int,
        instrumentation: str = "solo_piano",
    ) -> LayerIR:
        """Convert onset bundles to LayerIR for backward compatibility.

        ``instrumentation`` comes from the piece's contract. It was hardcoded
        `"solo_piano"` here, and every reader that consults the forces — the
        playability check, the texture floors, the assembler's routing — was
        therefore reading a value nothing had set. A motet's phrases claimed to
        be piano, so a nineteenth between Tenor and Bassus was measured as one
        hand's reach.

        The default keeps the engine-fallback path working for callers that have
        no contract to hand, since this realizer only runs for phrases the agent
        did not author.
        """
        layer = LayerIR(
            phrase_id=phrase_id,
            instrumentation=instrumentation or "solo_piano",
            key=key,
            meter=meter,
            bar_count=bar_count,
        )
        voice_to_layer = {
            "soprano": "principal_line",
            "melody": "principal_line",
            "bass": "bass_foundation",
            "accomp": "response_layer",
            "inner": "response_layer",
            "inner_1": "response_layer",
            "inner_2": "response_layer",
            "alto": "counter_reply",
            "tenor": "counter_reply",
            "counter": "counter_reply",
            "ornament": "ornamental_surface",
        }
        for bundle in bundles:
            for onset in bundle.events:
                layer_name = voice_to_layer.get(onset.voice, "response_layer")
                layer_list = getattr(layer, layer_name)

                pitch = onset.pitch
                if isinstance(pitch, list):
                    valid = [p for p in pitch if p != "rest"]
                    if not valid:
                        continue
                    midis = [(p, pitch_to_midi(p)) for p, _ in [(p, None) for p in valid]]
                    midis = [(p, pitch_to_midi(p)) for p in valid]
                    midis = [(p, m) for p, m in midis if m is not None]
                    if not midis:
                        continue
                    pitch = (
                        min(midis, key=lambda x: x[1])[0]
                        if layer_name == "bass_foundation"
                        else max(midis, key=lambda x: x[1])[0]
                    )

                if layer_name == "bass_foundation" and pitch != "rest":
                    m = pitch_to_midi(pitch)
                    if m is not None:
                        pitch = midi_to_pitch(clamp_to_range(m, 36, 60), key)
                if layer_name == "principal_line" and pitch != "rest":
                    m = pitch_to_midi(pitch)
                    if m is not None:
                        pitch = midi_to_pitch(clamp_to_range(m, *MELODY_RANGE), key)

                layer_list.append(
                    LayerEvent(
                        bar=bundle.bar,
                        beat=bundle.beat,
                        pitch=pitch,
                        duration=onset.duration,
                        role=onset.role,
                        dynamic=onset.dynamic,
                        articulation=onset.articulation,
                        ornament=onset.ornament,
                        tie=onset.tie,
                        expression=onset.expression,
                        source_layer=layer_name,
                    )
                )
        return layer

    # ─── Stage 1: Prototype Selection ─────────────────────────────────────

    def _select_prototype(
        self, control: PhraseControlIR, ctx: PhraseContext, sp: StyleProgram, trace: ContextTrace
    ) -> PhraseResult | None:
        """Find a phrase prototype from corpus matching this phrase's role."""
        if not self.phrase_bank:
            return None
        try:
            mode = "minor" if is_minor_key(control.local_key) else "major"
            tex0 = control.texture_program.bars[0] if control.texture_program.bars else None
            query = PhraseQuery(
                formal_function=control.phrase_function,
                cadence_type=control.cadence_target,
                length_range=(max(2, control.bars - 2), control.bars + 2),
                key_mode=mode,
                rh_texture_family=tex0.rh_texture if tex0 else None,
                lh_texture_family=tex0.lh_texture if tex0 else None,
                # Two of the three dimensions no caller ever set. `contour_class`
                # is left unset here on purpose: a PhraseControlIR carries no
                # dramatic role, and every rule read off a register curve turned
                # out to return one value for every phrase — see
                # `composition_brief._slot_contour_class`. Unset scores a neutral
                # 0.5; a wrong word scores 0.0.
                cadence_distance=control.bars,
                entry_texture=(tex0.rh_texture if tex0 else None),
                n=3,
            )
            results = self.phrase_bank.retrieve(query)
            if results:
                proto = results[0]
                trace.corpus_patterns_used.append(f"prototype:{proto.phrase_id}")
                return proto
        except Exception:
            pass
        return None

    # ─── Stage 2: Gesture Slot Planning ───────────────────────────────────

    def _plan_gesture_slots(
        self,
        control: PhraseControlIR,
        voicing_map: dict[int, dict],
        prototype: PhraseResult | None,
    ) -> list[GestureSlot]:
        """Divide the phrase into gesture slots between consecutive melody anchors."""
        anchors = sorted(control.melody_anchors, key=lambda a: (a.bar, a.beat))
        bass_anchors = sorted(control.bass_anchors, key=lambda a: (a.bar, a.beat))
        bar_dur = bar_duration(control.meter)
        cadence_bar = control.cadence_bar or (control.bar_start + control.bars - 1)
        slots: list[GestureSlot] = []

        if not anchors:
            # No melody anchors — make one slot per bar
            for bar_off in range(control.bars):
                bar = control.bar_start + bar_off
                tex = self._get_texture_for_bar(control, bar_off)
                slots.append(
                    GestureSlot(
                        bar_start=bar,
                        beat_start=1.0,
                        bar_end=bar,
                        beat_end=bar_dur,
                        span_beats=bar_dur,
                        function="continuation",
                        rh_texture=tex[0],
                        lh_texture=tex[1],
                        harmonic_cells=self._cells_for_range(control, bar, 1.0, bar, bar_dur),
                        bass_anchors=[a for a in bass_anchors if a.bar == bar],
                        density_target=tex[2],
                        is_cadence_zone=abs(cadence_bar - bar) <= 1,
                    )
                )
            self._assign_bar_ownership(slots, control)
            return slots

        # Build slots between consecutive anchors
        for i in range(len(anchors)):
            a_start = anchors[i]
            a_end = anchors[i + 1] if i + 1 < len(anchors) else None

            bar_s, beat_s = a_start.bar, a_start.beat
            if a_end:
                bar_e, beat_e = a_end.bar, a_end.beat
            else:
                # Last anchor to end of phrase
                bar_e = control.bar_start + control.bars - 1
                beat_e = bar_dur

            span = (bar_e - bar_s) * bar_dur + (beat_e - beat_s)
            if span <= 0:
                span = bar_dur

            # Infer function
            fn = self._infer_slot_function(
                i, len(anchors), a_start, a_end, cadence_bar, bar_dur, control
            )

            # Texture from plan
            bar_off = bar_s - control.bar_start
            tex = self._get_texture_for_bar(control, bar_off)

            # Is this near the cadence?
            is_cad = abs(cadence_bar - bar_e) <= 1 or abs(cadence_bar - bar_s) <= 1

            slots.append(
                GestureSlot(
                    bar_start=bar_s,
                    beat_start=beat_s,
                    bar_end=bar_e,
                    beat_end=beat_e,
                    span_beats=span,
                    function=fn,
                    rh_texture=tex[0],
                    lh_texture=tex[1],
                    anchor_start=a_start,
                    anchor_end=a_end,
                    harmonic_cells=self._cells_for_range(control, bar_s, beat_s, bar_e, beat_e),
                    bass_anchors=[a for a in bass_anchors if bar_s <= a.bar <= bar_e],
                    density_target=tex[2],
                    is_cadence_zone=is_cad,
                )
            )

        self._assign_bar_ownership(slots, control)
        return slots

    def _infer_slot_function(
        self,
        idx: int,
        total: int,
        anchor_start: Anchor,
        anchor_end: Anchor | None,
        cadence_bar: int,
        bar_dur: float,
        control: PhraseControlIR,
    ) -> str:
        """Infer the rhetorical function of a gesture slot."""
        if idx == 0:
            return "entry"
        if anchor_end is None or idx == total - 1:
            return "arrival"
        if anchor_end and abs(cadence_bar - anchor_end.bar) <= 1:
            return "cadential"
        if anchor_start.role == "peak":
            return "peak_response"
        if anchor_start.role == "motif":
            return "motif_statement"

        # Determine contour direction
        start_midi = (
            pitch_to_midi(anchor_start.pitch_or_degree)
            if not anchor_start.pitch_or_degree.startswith("^")
            else None
        )
        end_midi = (
            pitch_to_midi(anchor_end.pitch_or_degree)
            if anchor_end and not anchor_end.pitch_or_degree.startswith("^")
            else None
        )
        if start_midi and end_midi:
            if end_midi > start_midi + 2:
                return "rising_continuation"
            if end_midi < start_midi - 2:
                return "falling_continuation"

        # An anchor may be written as a SCALE DEGREE (`^5`) rather than a pitch,
        # and `pitch_to_midi` returns None for those — so the contour test above
        # was skipped entirely and a rising slot fell through to "winding_down",
        # identical to a falling one:
        #
        #     pitches  C4 -> G4  ->  rising_continuation
        #     degrees  ^1 -> ^5  ->  winding_down      (the same melody)
        #
        # Compared as scale steps, which is a coarser reading than semitones but
        # the right sign. Degrees do not wrap here: `^7 -> ^1` reads as a fall,
        # and as a contour heuristic over a gesture slot that is the useful
        # answer more often than not.
        start_deg = _degree_number(anchor_start.pitch_or_degree)
        end_deg = _degree_number(anchor_end.pitch_or_degree) if anchor_end else None
        if start_deg is not None and end_deg is not None:
            if end_deg > start_deg + 1:
                return "rising_continuation"
            if end_deg < start_deg - 1:
                return "falling_continuation"

        if idx < total // 2:
            return "continuation"
        return "winding_down"

    # ─── Stage 3: Co-Composed Realization ─────────────────────────────────

    def _realize_slot(
        self,
        slot: GestureSlot,
        control: PhraseControlIR,
        ctx: PhraseContext,
        voicing_map: dict[int, dict],
        sp: StyleProgram,
        scale: list[int],
        key: str,
        mode: str,
        root: int,
        bar_dur: float,
        variant: int,
        prev_exit: SlotExitState,
        trace: ContextTrace,
    ) -> tuple[list[OnsetBundle], SlotExitState]:
        """Co-compose melody + accompaniment for one gesture slot."""
        bundles: list[OnsetBundle] = []

        # 3a: Resolve melody anchor pitches
        start_midi = (
            self._resolve_pitch(slot.anchor_start, key, mode, root, prev_exit.last_melody_midi)
            if slot.anchor_start
            else prev_exit.last_melody_midi
        )
        end_midi = (
            self._resolve_pitch(slot.anchor_end, key, mode, root, start_midi)
            if slot.anchor_end
            else start_midi
        )

        # 3b: Retrieve gesture for melodic fill between anchors
        gesture = self._retrieve_gesture(slot, ctx, key, mode, trace)

        # 3c: Generate melody events (anchor + gesture fill)
        melody_events = self._construct_melody(
            slot,
            start_midi,
            end_midi,
            gesture,
            scale,
            key,
            bar_dur,
            trace,
            control,
            voicing_map,
        )

        _follow_harmony_per_bar(melody_events, slot, key, voicing_map)

        # 3d: Generate accompaniment events (pattern-adapted + harmony-aware)
        accomp_events = self._construct_accompaniment(
            slot,
            melody_events,
            voicing_map,
            control,
            ctx,
            sp,
            key,
            mode,
            root,
            scale,
            bar_dur,
            variant,
            trace,
        )

        # 3e: Merge into bundles
        all_events = melody_events + accomp_events

        # ONE onset per voice per instant.
        #
        # This keyed on (bar, beat, voice, PITCH), so two DIFFERENT pitches at
        # the same instant in the same voice both survived — a gesture filling a
        # slot up to an anchor, and the anchor's own note on that beat. Both
        # then counted toward the bar, and every engine-realized phrase came out
        # overfull in both hands:
        #
        #     principal_line bar 1: 5.0 beats in a 4.0-beat bar
        #         beat 3.000  D4  trip_e      <- gesture running into the anchor
        #         beat 3.000  E4  q           <- the anchor itself
        #
        # `_repair_engine_surface` then trimmed 136 overlaps and DROPPED three
        # notes outright across three phrases to make it engravable. Its own
        # docstring says those counts are the signal the generator needs fixing;
        # this is what they were signalling.
        #
        # A layer is one voice, so at a collision the LONGER note is kept: the
        # structural anchor outlasts the gesture filler that ran into it.
        from .duration import dur_to_beats as _dtb

        def _span(evt):
            try:
                return float(_dtb(evt.duration))
            except (ValueError, KeyError, TypeError):
                return 0.0

        best: dict[tuple, object] = {}
        order: list[tuple] = []
        for evt in all_events:
            sig = (evt._bar, round(evt._beat, 2), evt.voice)
            if sig not in best:
                best[sig] = evt
                order.append(sig)
            elif _span(evt) > _span(best[sig]):
                best[sig] = evt
        all_events = [best[sig] for sig in order]

        # Group by (bar, beat) — rounding ONLY to decide what shares an instant.
        #
        # The rounded key used to become the bundle's actual beat, and from
        # there the LayerIR event's beat. A triplet at 3.3333 was written to the
        # score as **3.33** and its partner at 3.6667 as **3.67** — positions no
        # notation can express, which `_repair_engine_surface` then had to snap
        # back (12 and 4 per phrase). The generator was emitting drift that the
        # repairer existed to remove.
        #
        # Two decimals is right for grouping: it is coarse enough that float
        # accumulation lands two genuinely-simultaneous onsets in one bundle.
        # It is not a position. The bundle keeps the exact beat of its earliest
        # member, so a triplet stays an exact third.
        time_groups: dict[tuple[int, float], list[OnsetEvent]] = {}
        exact_beat: dict[tuple[int, float], float] = {}
        for evt in all_events:
            k = (evt._bar, round(evt._beat, 2))
            time_groups.setdefault(k, []).append(evt)
            if k not in exact_beat or float(evt._beat) < exact_beat[k]:
                exact_beat[k] = float(evt._beat)

        for key, evts in sorted(time_groups.items()):
            bar = key[0]
            beat = exact_beat[key]
            b = OnsetBundle(bar=bar, beat=beat)
            # Find harmonic cell for this position
            for cell in slot.harmonic_cells:
                if cell.bar == bar:
                    b.harmonic_cell = cell
                    break
            for e in evts:
                b.events.append(
                    OnsetEvent(
                        voice=e.voice,
                        pitch=e.pitch,
                        duration=e.duration,
                        role=e.role,
                        dynamic=e.dynamic,
                        articulation=e.articulation,
                        ornament=e.ornament,
                        tie=e.tie,
                        expression=e.expression,
                        justification=e.justification,
                    )
                )
            bundles.append(b)

        # Update exit state
        exit_state = SlotExitState(
            last_melody_midi=end_midi or start_midi,
            last_bass_midi=self._last_bass_midi(accomp_events),
            last_beat=slot.beat_end,
            last_dynamic=prev_exit.last_dynamic,
        )
        return bundles, exit_state

    # ─── Melody Construction ──────────────────────────────────────────────

    def _construct_melody(
        self,
        slot: GestureSlot,
        start_midi: int | None,
        end_midi: int | None,
        gesture: GestureResult | None,
        scale: list[int],
        key: str,
        bar_dur: float,
        trace: ContextTrace,
        control: PhraseControlIR,
        voicing_map: dict[int, dict] | None = None,
    ) -> list[_TaggedEvent]:
        """Build melody events for a gesture slot using anchor interpolation.

        Uses gesture dur_profile for rhythm and scale-walking for pitch.
        When motif_slots + motif_bank supply material for a bar in this slot,
        emits motif rhythm/intervals instead of generic interpolation.
        """
        events: list[_TaggedEvent] = []
        if start_midi is None:
            return events

        effective_end = end_midi if end_midi is not None else start_midi

        # The motif path takes the harmony-following scale too.
        #
        # It runs FIRST and returns early, so applying the substitution only in
        # the gesture branch below left every motif-driven bar walking the plain
        # diatonic scale — and the last cross-relations in a realized section
        # were all in one such bar, the melody's F natural against the
        # accompaniment's F#. A fix in one of two branches is a fix in neither
        # for the material that takes the other.
        scale = _scale_following_harmony(scale, _slot_chord_pcs(slot, key, voicing_map))

        # Motif-driven realization for any bar in this slot with a MotifSlot
        if self.motif_bank and getattr(control, "motif_slots", None):
            motif_events: list[_TaggedEvent] = []
            for bar in range(int(slot.bar_start), int(slot.bar_end) + 1):
                ms = pick_motif_slot_for_bar(control.motif_slots, bar)
                if not ms:
                    continue
                motif = self.motif_bank.get(ms.motif_id)
                if not motif or not motif.rhythm_cell:
                    continue
                sm = start_midi
                fsd = first_scale_degree_midi(motif, scale)
                if fsd is not None:
                    sm = fsd
                placement = MotifPlacement(
                    bar=ms.bar,
                    beat=ms.beat,
                    motif_id=ms.motif_id,
                    transform=ms.transform,
                    voice=ms.voice,
                    params=dict(ms.params or {}),
                )
                raw = emit_motif_melody_events(
                    motif,
                    placement,
                    key,
                    scale,
                    int(sm),
                    bar_dur,
                )
                for r in raw:
                    if slot.bar_start <= r["bar"] <= slot.bar_end:
                        motif_events.append(
                            _TaggedEvent(
                                bar=r["bar"],
                                beat=r["beat"],
                                voice="soprano",
                                pitch=r["pitch"],
                                duration=r["duration"],
                                role=r["role"],
                                justification=OnsetJustification(
                                    structural_reasons=[NoteJustification.MOTIF.value],
                                ),
                            )
                        )
                trace.gestures_applied.append(f"motif:{ms.motif_id}")
            if motif_events:
                return motif_events

        # Place the start anchor
        events.append(
            _TaggedEvent(
                bar=slot.bar_start,
                beat=slot.beat_start,
                voice="soprano",
                pitch=midi_to_pitch(clamp_to_range(start_midi, 60, 84), key),
                duration="q",
                role=NoteRole.STRUCTURAL.value,
                justification=OnsetJustification(
                    structural_reasons=[NoteJustification.FORM.value],
                ),
            )
        )

        # If there's a gesture dur_profile, use it for rhythmic skeleton
        if gesture and gesture.dur_profile:
            _chord_pcs = _slot_chord_pcs(slot, key, voicing_map)
            pitches = self._interpolate_melody_pitches(
                start_midi,
                effective_end,
                len(gesture.dur_profile),
                scale,
                key,
                chord_pcs=_chord_pcs,
                strong_steps=_strong_step_indices(gesture.dur_profile, bar_dur),
            )
            # An EXACT cursor, and emit-then-advance.
            #
            # Two faults here, both silent. The cursor was a float advanced by
            # durations and then rounded to two decimals, so a position of
            # 1.5625 — a legitimate 64th-note offset — was emitted as `1.56`,
            # which is not a position in any bar and which no notation can
            # express. Downstream that arrived as an off-grid onset and a bar
            # that did not sum to its meter.
            #
            # And the cursor advanced BEFORE the note was emitted, so every
            # gesture started one note-value late and its last note ran past the
            # end of the slot. A four-note figure beginning on beat 1 was written
            # beginning on beat 1.5.
            beat_cursor = Fraction(str(slot.beat_start)).limit_denominator(96)
            bar_len = Fraction(str(bar_dur)).limit_denominator(96)
            bar_cursor = slot.bar_start
            for i, dur_code in enumerate(gesture.dur_profile):
                dur_beats = DURATION_VALUES.get(dur_code, Fraction(1, 2))
                if not isinstance(dur_beats, Fraction):
                    dur_beats = Fraction(str(dur_beats)).limit_denominator(96)
                # Beats are ONE-BASED: the downbeat is 1.0, so a bar spans
                # [1.0, 1.0 + bar_len). Wrapping at `> bar_len` fired on the
                # last valid beat of the bar and then subtracted the bar length
                # from a 1-based number, landing BELOW the downbeat — 60 events
                # in a single section were written at beats 0.25, 0.5 and 0.75,
                # which are not positions in any bar. The repair pass then
                # snapped and trimmed them, which is where most of its churn
                # came from.
                while beat_cursor >= bar_len + 1:
                    beat_cursor -= bar_len
                    bar_cursor += 1
                if bar_cursor > slot.bar_end:
                    break
                # Stop at the slot's END BEAT too, not just its end bar.
                #
                # This checked the bar alone, so a gesture in a slot running
                # `1b1 -> 1b3` kept emitting through the whole of bar 1 and
                # landed on beat 3 — the next anchor's own instant. Two onsets
                # in one voice at one position, and a 4/4 bar holding five
                # beats:
                #
                #     beat 3.000  D4  trip_e   <- gesture past its slot end
                #     beat 3.000  E4  q        <- the anchor
                #
                # The span is half-open: the next slot owns its start instant.
                # `_plan_gesture_slots` marks "to the end of the phrase" by
                # setting `beat_end` to the bar length, which in these 1-based
                # beats is the LAST beat rather than past it — so that case
                # extends to the true end of the bar instead of cutting it.
                end_beat = Fraction(str(slot.beat_end)).limit_denominator(96)
                if end_beat >= bar_len:
                    end_beat = bar_len + 1
                if (bar_cursor, beat_cursor) >= (slot.bar_end, end_beat):
                    break
                # Fit the note inside its own bar.
                #
                # The duration came from `gesture.dur_profile` with no regard
                # for the room left: a half note chosen for beat 4 of a 4/4 bar
                # overruns it by a beat. This generator writes no ties, so an
                # overrunning note is not a note held across the barline — it is
                # a bar that cannot be engraved, and `_repair_engine_surface`
                # was clamping them afterwards. A surface that is correct when
                # written beats one that is corrected later.
                room = bar_len + 1 - beat_cursor
                if room <= 0:
                    break
                if dur_beats > room:
                    fitted = _duration_code_for(room)
                    if fitted is None:
                        break
                    dur_code, dur_beats = fitted
                if i < len(pitches):
                    midi_val = clamp_to_range(pitches[i], *MELODY_RANGE)
                    events.append(
                        _TaggedEvent(
                            bar=bar_cursor,
                            beat=float(beat_cursor),
                            voice="soprano",
                            pitch=midi_to_pitch(midi_val, key),
                            duration=dur_code,
                            role=NoteRole.PASSING.value if i > 0 else NoteRole.STRUCTURAL.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.REGISTER_SHAPING.value],
                                local_reasons=[NoteJustification.VOICE_LEADING.value],
                                context_trace=f"gesture:{gesture.cell_id}" if gesture else "",
                            ),
                        )
                    )
                # Advance AFTER emitting, so the first note lands on the
                # slot's own start beat rather than one value past it.
                beat_cursor += dur_beats
        else:
            # No gesture — generate scale-walk between anchors
            bars_in_slot = max(1, slot.bar_end - slot.bar_start)
            if bars_in_slot > 1 and start_midi != effective_end:
                steps = self._interpolate_melody_pitches(
                    start_midi, effective_end, bars_in_slot, scale, key
                )
                for i, midi_val in enumerate(steps):
                    bar = slot.bar_start + i + 1
                    if bar > slot.bar_end:
                        break
                    midi_val = clamp_to_range(midi_val, *MELODY_RANGE)
                    # Alternate q and e for rhythmic variety
                    dur = "q" if i % 2 == 0 else "e"
                    events.append(
                        _TaggedEvent(
                            bar=bar,
                            beat=1.0,
                            voice="soprano",
                            pitch=midi_to_pitch(midi_val, key),
                            duration=dur,
                            role=NoteRole.PASSING.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.REGISTER_SHAPING.value],
                            ),
                        )
                    )

        # Place end anchor if it exists and is different from start
        if slot.anchor_end and end_midi is not None and slot.anchor_end.bar != slot.bar_start:
            events.append(
                _TaggedEvent(
                    bar=slot.anchor_end.bar,
                    beat=slot.anchor_end.beat,
                    voice="soprano",
                    pitch=midi_to_pitch(clamp_to_range(end_midi, 60, 84), key),
                    duration="q" if slot.anchor_end.role != "cadence" else "h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.FORM.value],
                    ),
                )
            )

        return events

    def _interpolate_melody_pitches(
        self,
        start_midi: int,
        end_midi: int,
        n_steps: int,
        scale: list[int],
        key: str,
        chord_pcs: frozenset[int] | None = None,
        strong_steps: frozenset[int] | None = None,
    ) -> list[int]:
        """Shape a line from `start_midi` to `end_midi` through the scale.

        This was a straight linear walk through scale indices, and a straight
        walk can only produce two things: a pure scale run when the anchors are
        far apart, or a repeated note when they are close. Measured on a
        realized section it produced a melody **98.3% stepwise with 0.4
        direction changes per bar** — against this composer's own 67% stepwise
        and roughly 2.05 direction changes. The line was structurally incapable
        of a leap or a turn, because nothing in the arithmetic could make one.

        What replaces it is the single shape every melodic doctrine in this
        project describes, from Palestrina's "one high point per phrase,
        approached and left by step" to the Romantic long arch: the line rises
        past its target and comes back to it. That gives a direction change per
        span for free, and the overshoot is where the leaps come from.

        The endpoints are never moved — they are the harmonic anchors, and the
        shape between them is the only thing at liberty here.
        """
        if n_steps <= 0:
            return []
        if not scale:
            return [start_midi] * n_steps
        if n_steps == 1:
            # The CHROMATIC midpoint of two MIDI numbers is out of key about
            # half the time. In A-flat major it turned Ab4 -> Bb4 into A
            # NATURAL, Bb4 -> Db5 into B natural, and Db5 -> Eb5 into D natural —
            # three notes that do not exist in the key, sounding against a
            # correctly-spelled left hand and surfacing as eight cross-relations
            # in the first bars of a Liszt section.
            #
            # A one-note fill is still a note of the scale. This line predates
            # the arch below and I preserved it without asking what it did.
            midpoint = (start_midi + end_midi) // 2
            return [min(scale, key=lambda m: (abs(m - midpoint), m))]

        start_idx = min(range(len(scale)), key=lambda i: abs(scale[i] - start_midi))
        end_idx = min(range(len(scale)), key=lambda i: abs(scale[i] - end_midi))

        # The peak sits above both anchors and roughly 60% of the way across —
        # late enough to feel like an arrival rather than a passing note, which
        # is where the doctrine places it.
        # An EVEN number of scale steps above an anchor is a third or a fifth
        # from it — a consonance with the chord the anchor belongs to. An odd
        # reach lands a step away, on a passing tone, and the peak is the one
        # note in the span that is held long enough to be heard against the
        # bass: a first version used an arbitrary reach and turned one
        # cross-relation into eight, every one of them the peak sounding a
        # scale degree the harmony had altered.
        span = abs(end_idx - start_idx)
        reach = 3 if span >= 5 else 2
        rising = end_idx >= start_idx
        peak_idx = (
            (max(start_idx, end_idx) + reach) if rising else (min(start_idx, end_idx) - reach)
        )
        peak_idx = max(0, min(len(scale) - 1, peak_idx))

        # The peak is the one note in the span held long enough to be heard
        # against the bass, so it has to belong to the chord under it. Reaching
        # a scale tone the harmony had ALTERED — the melody's F natural over the
        # accompaniment's F# — took cross-relations from 1 to 8 in a 14-bar
        # section, where real Chopin and Mozart run a median of 0.2-1.9 and a
        # maximum of 3.1. Nudge the peak to the nearest scale degree that is
        # also a chord tone; if none is near, leave it, because moving it far
        # would destroy the shape it exists to make.
        if chord_pcs:
            candidates = [
                i
                for i in range(len(scale))
                if scale[i] % 12 in chord_pcs and abs(i - peak_idx) <= 2
            ]
            if candidates:
                peak_idx = min(candidates, key=lambda i: (abs(i - peak_idx), -i))

        peak_at = max(1, int(round(n_steps * 0.6)))

        result: list[int] = []
        for step in range(1, n_steps + 1):
            if step <= peak_at:
                # `step / (peak_at + 1)` never reaches 1, so the line topped out
                # one scale index BELOW the peak and never actually touched it —
                # which also meant the chord-tone snap above had no effect on
                # the note that was heard. The peak is the point of the shape;
                # the path has to arrive at it.
                t = step / peak_at
                idx = start_idx + (peak_idx - start_idx) * t
            else:
                t = (step - peak_at) / (n_steps - peak_at + 1)
                idx = peak_idx + (end_idx - peak_idx) * t
            i = max(0, min(len(scale) - 1, int(round(idx))))
            # A note on a STRONG beat is heard against the bass; a note on a
            # weak one passes. Snapping only the strong ones keeps passing
            # tones — which are most of what makes a line sing — while removing
            # the clashes the arch introduced. Snapping everything would give
            # back an arpeggio, which is the opposite defect.
            if chord_pcs and strong_steps and step in strong_steps:
                near = [
                    j for j in range(len(scale)) if scale[j] % 12 in chord_pcs and abs(j - i) <= 1
                ]
                if near:
                    i = min(near, key=lambda j: abs(j - i))
            result.append(scale[i])

        return result

    # ─── Accompaniment Construction ───────────────────────────────────────

    @staticmethod
    def _assign_bar_ownership(slots: list[GestureSlot], control: PhraseControlIR) -> None:
        """Give every bar of the phrase to exactly one slot.

        `_construct_accompaniment` used to iterate every bar its slot TOUCHED,
        ignoring `beat_start`/`beat_end`. Gesture slots run between consecutive
        melody anchors and are contiguous, so most bars are touched by two:

            1b1 -> 1b3  entry           1b3 -> 2b1  continuation
            2b1 -> 2b3  peak_response   2b3 -> 3b1  cadential

        and each bar's accompaniment was generated once per slot touching it.
        Measured on a realized section, **61 of 61 bass onsets sat at a
        duplicated position** — the whole left hand written twice, then deleted
        again by the surface repair, which is why `overlaps_trimmed` came back
        at 34, 46 and 56 per phrase.

        A bar goes to the slot active at its DOWNBEAT. Whole bars, never split:
        an Alberti or arpeggio figure cut at beat 3 is not half a pattern, it is
        a broken one.

        This takes the whole LIST because the question cannot be answered from
        one slot. A phrase whose opening anchor falls on beat 3 has no slot
        active at bar 1 beat 1, and "am I the earliest slot?" is not visible
        from inside a slot — a first attempt that guessed at it from
        `bar_start == first_bar` gave bar 1 to two different slots.
        """
        if not slots:
            return
        first_bar = control.bar_start
        last_bar = control.bar_start + control.bars - 1
        for slot in slots:
            slot.owned_bars = []
        for bar in range(first_bar, last_bar + 1):
            owner = None
            for slot in slots:
                if (
                    (slot.bar_start, float(slot.beat_start))
                    <= (bar, 1.0)
                    < (
                        slot.bar_end,
                        float(slot.beat_end),
                    )
                ):
                    owner = slot
                    break
            if owner is None:
                # No slot is active at this downbeat: the phrase opens (or ends)
                # mid-bar. The nearest slot by start position takes it.
                owner = min(
                    slots, key=lambda s: abs((s.bar_start - bar) * 8 + float(s.beat_start) - 1.0)
                )
            owner.owned_bars.append(bar)

    def _construct_accompaniment(
        self,
        slot: GestureSlot,
        melody_events: list[_TaggedEvent],
        voicing_map: dict[int, dict],
        control: PhraseControlIR,
        ctx: PhraseContext,
        sp: StyleProgram,
        key: str,
        mode: str,
        root: int,
        scale: list[int],
        bar_dur: float,
        variant: int,
        trace: ContextTrace,
    ) -> list[_TaggedEvent]:
        """Generate accompaniment events aware of melody occupancy.

        Retrieval hierarchy:
        1. Pattern retrieval adapted to harmony
        2. Corpus bar retrieval
        3. Style-specific constructive fallback
        """
        events: list[_TaggedEvent] = []

        # Melody occupancy map: which beats have melody?
        mel_beats: dict[int, list[float]] = {}
        for me in melody_events:
            mel_beats.setdefault(me._bar, []).append(me._beat)

        # Process bar by bar within the slot — but only the bars this slot OWNS.
        #
        # This iterated every bar the slot TOUCHES, ignoring `beat_start` and
        # `beat_end` entirely. Gesture slots run between consecutive melody
        # anchors and are contiguous, so most bars are touched by two of them:
        #
        #     1b1 -> 1b3  entry           1b3 -> 2b1  continuation
        #     2b1 -> 2b3  peak_response   2b3 -> 3b1  cadential
        #
        # and every bar's left hand was therefore generated once per slot.
        # Measured on a realized section: **61 of 61 bass onsets sat at a
        # duplicated position**, the whole accompaniment written twice. The
        # surface repair then deleted the copy — which is why
        # `overlaps_trimmed` came back at 34, 46 and 56 per phrase and looked
        # alarming. The output was correct only because something cleaned up
        # after it.
        #
        # A bar belongs to the slot whose span contains its DOWNBEAT. Assigning
        # whole bars rather than splitting them keeps the accompaniment figure
        # intact: an Alberti or arpeggio pattern cut at beat 3 is not half a
        # pattern, it is a broken one.
        for bar in slot.owned_bars or []:
            bar_off = bar - control.bar_start
            voicing = voicing_map.get(bar)
            mel_active = mel_beats.get(bar, [])
            tex = self._get_texture_for_bar(control, bar_off)
            lh_texture = tex[1]

            # Get the harmonic cell for this bar
            cell = None
            for c in slot.harmonic_cells:
                if c.bar == bar:
                    cell = c
                    break

            # Bass anchor for this bar
            bass_anchor = None
            for ba in slot.bass_anchors:
                if ba.bar == bar:
                    bass_anchor = ba
                    break

            # Determine bass pitch
            bass_midi = self._resolve_bass_pitch(bass_anchor, voicing, key, mode, root)

            # Determine chord tones for this bar
            bar_chord_tones = self._get_chord_tones_for_bar(cell, voicing, root, mode)

            # --- Retrieval hierarchy ---
            bar_events = None

            # 1. Try pattern retrieval
            if lh_texture in ctx.active_patterns:
                patterns = ctx.active_patterns[lh_texture]
                if patterns:
                    pattern = patterns[(variant + bar_off) % len(patterns)]
                    bar_events = self._adapt_pattern_to_harmony(
                        pattern,
                        bar,
                        bar_chord_tones,
                        bass_midi,
                        key,
                        mode,
                        scale,
                        mel_active,
                        trace,
                        meter=getattr(control, "meter", None),
                    )

            # 2. Try corpus bar retrieval
            if bar_events is None and self.corpus_bar_retriever:
                bar_events = self._retrieve_corpus_bar(
                    bar, control, lh_texture, tex[0], mode, key, trace
                )

            # 3. Cadence-specialized treatment
            if bar_events is None and slot.is_cadence_zone and self.cadence_bank:
                bar_events = self._cadence_bar_events(bar, control, key, mode, voicing, trace)

            # 4. Style-specific constructive fallback
            if bar_events is None:
                bar_events = self._constructive_fallback(
                    bar,
                    lh_texture,
                    bass_midi,
                    bar_chord_tones,
                    key,
                    mode,
                    scale,
                    mel_active,
                    bar_dur,
                    sp,
                    trace,
                )

            if bar_events:
                events.extend(bar_events)

        return events

    def _adapt_pattern_to_harmony(
        self,
        pattern: dict,
        bar: int,
        chord_tones_midi: list[int],
        bass_midi: int,
        key: str,
        mode: str,
        scale: list[int],
        mel_active: list[float],
        trace: ContextTrace,
        meter=None,
    ) -> list[_TaggedEvent] | None:
        """Adapt a retrieved pattern to the current harmony by re-mapping chord slots."""
        try:
            lh_events = self.pattern_retriever.pattern_to_events(
                pattern,
                bar,
                target_key=key,
            )
        except Exception:
            return None

        if not lh_events:
            return None

        # A retrieved pattern carries the beats of the bar it was extracted from,
        # which may be in a different metre than the one being composed. Truncate
        # it to the current bar rather than emitting onsets past the barline for
        # the repair pass to drop.
        bar_cap = float(bar_duration(meter)) + 1.0
        events: list[_TaggedEvent] = []
        for _i, evt in enumerate(lh_events):
            if float(evt.beat) >= bar_cap - 1e-9:
                continue
            duration = evt.duration
            beats = DURATION_VALUES.get(duration)
            room = bar_cap - float(evt.beat)
            if beats is not None and float(beats) > room + 1e-9:
                fitted = _duration_code_for(room)
                if fitted is None:
                    continue
                duration = fitted[0]
            # A retrieved pattern's RESTS do not survive into a layer that
            # another generator is also writing into. `pitch_to_midi("rest")`
            # returns None, so the chord-tone snap below falls through to
            # `pitch = evt.pitch` and the rest passed into `bass_foundation`
            # unchanged — landing under a bass note that was already sounding.
            # A rest carries no sound and the silence it asks for is expressed
            # by not writing a note; what it actually did was make the surface
            # repair clamp the note it sat inside.
            if evt.pitch == "rest":
                continue

            # Snap each pattern pitch to nearest chord tone
            evt_midi = pitch_to_midi(evt.pitch)
            if evt_midi is not None and chord_tones_midi:
                snapped = min(chord_tones_midi, key=lambda ct: abs(ct - evt_midi))
                # Keep in LH register
                snapped = clamp_to_range(snapped, 36, 60)
                pitch = midi_to_pitch(snapped, key)
            else:
                pitch = evt.pitch

            voice = _lh_voice_for(lh_events, _i, meter)
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=evt.beat,
                    voice=voice,
                    pitch=pitch,
                    duration=duration,
                    role=evt.role or NoteRole.ARPEGGIATED_FILL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.HARMONY.value],
                        context_trace=f"pattern:{pattern.get('hash', '')}",
                    ),
                )
            )

        trace.corpus_patterns_used.append(pattern.get("hash", ""))
        return events

    def _retrieve_corpus_bar(
        self,
        bar: int,
        control: PhraseControlIR,
        lh_texture: str,
        rh_texture: str,
        mode: str,
        key: str,
        trace: ContextTrace,
    ) -> list[_TaggedEvent] | None:
        """Retrieve a corpus bar and convert to tagged events."""
        try:
            corpus_bar = self.corpus_bar_retriever.retrieve_bar(
                time_sig=control.meter,
                key_mode=mode,
                rh_texture=rh_texture,
                lh_texture=lh_texture,
            )
            if corpus_bar:
                _rh, lh = self.corpus_bar_retriever.bar_to_events(
                    corpus_bar,
                    bar,
                    key,
                )
                events = []
                for _i, evt in enumerate(lh):
                    events.append(
                        _TaggedEvent(
                            bar=bar,
                            beat=evt.beat,
                            voice=_lh_voice_for(lh, _i, getattr(control, "meter", None)),
                            pitch=evt.pitch,
                            duration=evt.duration,
                            role=evt.role or NoteRole.ARPEGGIATED_FILL.value,
                            justification=OnsetJustification(
                                structural_reasons=[NoteJustification.HARMONY.value],
                                context_trace=f"corpus_bar:{corpus_bar.get('source', '')}",
                            ),
                        )
                    )
                trace.corpus_bars_used.append(corpus_bar.get("source", ""))
                return events
        except Exception:
            pass
        return None

    def _cadence_bar_events(
        self,
        bar: int,
        control: PhraseControlIR,
        key: str,
        mode: str,
        voicing: dict | None,
        trace: ContextTrace,
    ) -> list[_TaggedEvent] | None:
        """Generate cadence-specialized accompaniment."""
        try:
            query = CadenceQuery(
                cadence_type=control.cadence_target,
                key=key,
                mode=mode,
                approach_length_bars=2,
                n=1,
            )
            results = self.cadence_bank.retrieve(query)
            if results and results[0].chord_sequence:
                cad = results[0]
                cad_bar = control.cadence_bar or (control.bar_start + control.bars - 1)
                idx = len(cad.chord_sequence) - 1 - (cad_bar - bar)
                if 0 <= idx < len(cad.chord_sequence):
                    # The chord this bar's cadence script actually names.
                    #
                    # Two faults, one inside the other. The quality was
                    # hardcoded `"major"`, so a D minor cadence put F# under the
                    # melody's F natural. And the ROOT was always the tonic —
                    # `key_to_root_midi(key)` — although `cad.chord_sequence[idx]`
                    # names the chord for this bar. So a cadence's approach
                    # chords, the `V` and the `ii6` that make it a cadence, were
                    # every one of them voiced as the tonic triad. The
                    # progression was retrieved, indexed, and then ignored.
                    #
                    # `roman_pitches` is the one place that knows what a Roman
                    # numeral means — every degree, quality and inversion, bass
                    # first. Deriving it here a second time is what produced
                    # both faults.
                    symbol = str(cad.chord_sequence[idx] or "").strip()
                    tonic_pc = key_to_root_midi(key) % 12
                    pcs = []
                    if symbol:
                        try:
                            pcs = roman_pitches(symbol, tonic_pc, mode)
                        except (ValueError, KeyError, TypeError):
                            pcs = []
                    if pcs:
                        base = 36 + ((pcs[0] - 36) % 12)
                        tones = [base] + [base + ((pc - pcs[0]) % 12) for pc in pcs[1:]]
                    else:
                        root_midi = key_to_root_midi(key) + 36
                        tones = chord_tones(root_midi, "minor" if is_minor_key(key) else "major")
                    if tones:
                        events = []
                        # Bass note
                        events.append(
                            _TaggedEvent(
                                bar=bar,
                                beat=1.0,
                                voice="bass",
                                pitch=midi_to_pitch(clamp_to_range(tones[0], 36, 60), key),
                                duration="h",
                                role=NoteRole.STRUCTURAL.value,
                                justification=OnsetJustification(
                                    structural_reasons=[NoteJustification.HARMONY.value],
                                    context_trace=f"cadence:{cad.cadence_id}",
                                ),
                            )
                        )
                        # Inner voice on beat 3
                        if len(tones) > 1:
                            events.append(
                                _TaggedEvent(
                                    bar=bar,
                                    beat=3.0,
                                    voice="accomp",
                                    pitch=midi_to_pitch(clamp_to_range(tones[1], 48, 67), key),
                                    duration="q",
                                    role=NoteRole.STRUCTURAL.value,
                                    justification=OnsetJustification(
                                        structural_reasons=[NoteJustification.HARMONY.value],
                                        context_trace=f"cadence:{cad.cadence_id}",
                                    ),
                                )
                            )
                        trace.corpus_patterns_used.append(f"cadence:{cad.cadence_id}")
                        return events
        except Exception:
            pass
        return None

    # ─── Constructive Fallback ────────────────────────────────────────────

    def _constructive_fallback(
        self,
        bar: int,
        lh_texture: str,
        bass_midi: int,
        chord_tones_midi: list[int],
        key: str,
        mode: str,
        scale: list[int],
        mel_active: list[float],
        bar_dur: float,
        sp: StyleProgram,
        trace: ContextTrace,
    ) -> list[_TaggedEvent]:
        """Style-specific constructive fallback — never dead silence.

        Generates idiomatic LH patterns from chord tones based on
        the requested texture type. Every bar sounds musical.
        """
        events: list[_TaggedEvent] = []
        bass_pitch = midi_to_pitch(clamp_to_range(bass_midi, 36, 55), key)

        # Ensure we have chord tones in LH range
        ct = (
            [clamp_to_range(t, 48, 67) for t in chord_tones_midi]
            if chord_tones_midi
            else [bass_midi + 12, bass_midi + 7]
        )
        ct_pitches = [midi_to_pitch(m, key) for m in ct]

        # Melody busy on beat 1? Thin the accompaniment
        mel_on_1 = 1.0 in mel_active

        just = OnsetJustification(
            structural_reasons=[NoteJustification.HARMONY.value],
            local_reasons=[NoteJustification.VOICE_LEADING.value],
            context_trace=f"constructive_fallback:{lh_texture}",
        )

        if lh_texture in ("alberti", AccompType.ALBERTI.value):
            # Alberti: root-fifth-third-fifth as eighths
            pattern = [
                bass_pitch,
                ct_pitches[0] if ct_pitches else bass_pitch,
                ct_pitches[1]
                if len(ct_pitches) > 1
                else ct_pitches[0]
                if ct_pitches
                else bass_pitch,
                ct_pitches[0] if ct_pitches else bass_pitch,
            ]
            beats = _eighth_positions(bar_dur)
            for i, beat in enumerate(beats):
                if beat >= bar_dur + 1:
                    break
                p = pattern[i % len(pattern)]
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass" if beat == 1.0 else "accomp",
                        pitch=p,
                        duration="e",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("broken_chord_wave", AccompType.BROKEN_CHORD_WAVE.value):
            # Broken chord ascending then descending
            up = [bass_pitch, *ct_pitches[:2]]
            down = [*list(reversed(ct_pitches[:2])), bass_pitch]
            seq = up + down
            beats = _eighth_positions(bar_dur)
            for i, beat in enumerate(beats):
                if beat >= bar_dur + 1:
                    break
                p = seq[i % len(seq)]
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass" if beat == 1.0 else "accomp",
                        pitch=p,
                        duration="e",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("walking_bass", AccompType.WALKING_BASS.value):
            # Quarter-note scale walk from bass toward next chord tone
            walk = [bass_midi]
            for s in range(1, 4):
                next_tone = bass_midi + s * (2 if mode == "major" else (2 if s != 2 else 1))
                snapped = snap_to_scale(next_tone, scale, "above")
                walk.append(snapped if snapped else next_tone)
            for i, beat in enumerate([1.0, 2.0, 3.0, 4.0]):
                if beat >= bar_dur + 1 or i >= len(walk):
                    break
                p = midi_to_pitch(clamp_to_range(walk[i], 36, 55), key)
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass",
                        pitch=p,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("bass_melody", AccompType.BASS_MELODY.value):
            # Contrapuntal bass: quarters on chord tones
            all_tones = [bass_midi, *ct[:2]]
            for i, beat in enumerate([1.0, 2.0, 3.0, 4.0]):
                if beat >= bar_dur + 1:
                    break
                m = all_tones[i % len(all_tones)]
                p = midi_to_pitch(clamp_to_range(m, 36, 60), key)
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=beat,
                        voice="bass",
                        pitch=p,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("block_chord_sparse", AccompType.BLOCK_CHORD_SPARSE.value):
            # Block chord on beats 1 and 3
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=just,
                )
            )
            if ct_pitches and bar_dur >= 3:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=3.0,
                        voice="accomp",
                        pitch=ct_pitches[0],
                        duration="h" if bar_dur >= 4 else "q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        elif lh_texture in ("pedal_point", AccompType.PEDAL_POINT.value):
            # Sustained bass
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="w" if bar_dur >= 4 else "h",
                    role=NoteRole.PEDAL_SUPPORT.value,
                    justification=just,
                )
            )

        elif lh_texture in ("sparse_punctuation", AccompType.SPARSE_PUNCTUATION.value):
            # Light touch — just beat 1 bass, short
            if not mel_on_1:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=1.0,
                        voice="bass",
                        pitch=bass_pitch,
                        duration="q",
                        role=NoteRole.STRUCTURAL.value,
                        justification=just,
                    )
                )

        else:
            # Generic: bass + one inner voice
            events.append(
                _TaggedEvent(
                    bar=bar,
                    beat=1.0,
                    voice="bass",
                    pitch=bass_pitch,
                    duration="h",
                    role=NoteRole.STRUCTURAL.value,
                    justification=just,
                )
            )
            if ct_pitches and not mel_on_1:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=2.0,
                        voice="accomp",
                        pitch=ct_pitches[0],
                        duration="q",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )
            if len(ct_pitches) > 1 and bar_dur >= 3:
                events.append(
                    _TaggedEvent(
                        bar=bar,
                        beat=3.0,
                        voice="accomp",
                        pitch=ct_pitches[1],
                        duration="q",
                        role=NoteRole.ARPEGGIATED_FILL.value,
                        justification=just,
                    )
                )

        trace.fallback_bar_count += 1
        return events

    # ─── Gesture Retrieval ────────────────────────────────────────────────

    def _retrieve_gesture(
        self, slot: GestureSlot, ctx: PhraseContext, key: str, mode: str, trace: ContextTrace
    ) -> GestureResult | None:
        """Retrieve a gesture from GestureBank matching the slot's function."""
        if not self.gesture_bank:
            return None
        try:
            query = GestureQuery(
                function=slot.function,
                texture_rh=slot.rh_texture,
                texture_lh=slot.lh_texture,
                min_span_beats=max(1.0, slot.span_beats - 4),
                max_span_beats=slot.span_beats + 4,
                key_mode=mode,
                n=3,
            )
            results = self.gesture_bank.retrieve(query)
            if results:
                g = results[0]
                trace.gestures_applied.append(g.cell_id)
                return g
        except Exception:
            pass
        return None

    # ─── Pitch Resolution Helpers ─────────────────────────────────────────

    def _resolve_pitch(
        self, anchor: Anchor | None, key: str, mode: str, root: int, prev_midi: int | None
    ) -> int | None:
        """Resolve an anchor's pitch_or_degree to a MIDI value."""
        if anchor is None:
            return None

        pitch_str = anchor.pitch_or_degree
        if pitch_str.startswith("^"):
            from .pitch import parse_scale_degree

            parsed = parse_scale_degree(pitch_str)
            if parsed is None:
                return prev_midi
            degree, alter = parsed
            intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
            idx = (degree - 1) % len(intervals)
            midi = 5 * 12 + root + intervals[idx] + alter  # octave 4
            if degree > 7:
                midi += 12
        else:
            midi = pitch_to_midi(pitch_str)
            if midi is None:
                return prev_midi

        # Voice-leading: keep within a 5th of previous
        if prev_midi is not None:
            while midi - prev_midi > 7:
                midi -= 12
            while prev_midi - midi > 7:
                midi += 12

        return clamp_to_range(midi, *MELODY_RANGE)

    def _resolve_bass_pitch(
        self, bass_anchor: Anchor | None, voicing: dict | None, key: str, mode: str, root: int
    ) -> int:
        """Resolve bass pitch from anchor or voicing."""
        if bass_anchor:
            p = bass_anchor.pitch_or_degree
            if p.startswith("^"):
                # `int(p[1:])` — which raised on `^#2`, the ordinary way to
                # write a raised second, and killed the whole section. It also
                # discarded the accidental it could not read and wrapped `^9`
                # back to the second in the SAME octave. `parse_scale_degree`
                # is the one parser for this notation; nothing else should
                # re-derive it.
                from .pitch import parse_scale_degree

                intervals = SCALE_INTERVALS.get(mode, SCALE_INTERVALS["major"])
                parsed = parse_scale_degree(p)
                if parsed is None:
                    return clamp_to_range(root + 36, 36, 55)
                degree, alter = parsed
                octave, base = divmod(degree - 1, len(intervals))
                midi = 3 * 12 + root + intervals[base] + 12 * octave + alter
                return clamp_to_range(midi, 36, 55)
            m = pitch_to_midi(p)
            if m is not None:
                return clamp_to_range(m, 36, 55)

        if voicing and "bass_midi" in voicing:
            return clamp_to_range(voicing["bass_midi"], 36, 55)
        if voicing and "bass" in voicing:
            m = pitch_to_midi(voicing["bass"])
            if m is not None:
                return clamp_to_range(m, 36, 55)

        # Default to root in bass register
        return clamp_to_range(root + 36, 36, 55)

    def _get_chord_tones_for_bar(
        self, cell: HarmonicCell | None, voicing: dict | None, root: int, mode: str
    ) -> list[int]:
        """Get MIDI chord tones for a bar from voicing or harmonic cell."""
        tones = []
        if voicing:
            for vk in ["soprano_midi", "alto_midi", "tenor_midi", "bass_midi"]:
                if vk in voicing:
                    tones.append(voicing[vk])
        if not tones:
            # Build from root + quality
            quality = "minor" if mode == "minor" else "major"
            tones = chord_tones(root + 48, quality)
        return tones

    def _last_bass_midi(self, events: list[_TaggedEvent]) -> int | None:
        """Get the last bass MIDI from accompaniment events."""
        for e in reversed(events):
            if e.voice == "bass" and e.pitch != "rest":
                m = pitch_to_midi(e.pitch)
                if m is not None:
                    return m
        return None

    # ─── Utilities ────────────────────────────────────────────────────────

    def _get_texture_for_bar(
        self, control: PhraseControlIR, bar_offset: int
    ) -> tuple[str, str, int]:
        """Get (rh_texture, lh_texture, density_target) for a bar offset."""
        if control.texture_program.bars and bar_offset < len(control.texture_program.bars):
            tp = control.texture_program.bars[bar_offset]
            return (tp.rh_texture, tp.lh_texture, tp.rh_density_target)
        return ("singing_melody", "alberti", 8)

    def _cells_for_range(
        self, control: PhraseControlIR, bar_s: int, beat_s: float, bar_e: int, beat_e: float
    ) -> list[HarmonicCell]:
        """Get harmonic cells active in a bar range."""
        result = []
        for cell in control.harmonic_cells:
            if bar_s <= cell.bar <= bar_e:
                result.append(cell)
        return result

    def _apply_dynamics(self, bundles: list[OnsetBundle], control: PhraseControlIR) -> None:
        """Apply dynamics from dynamic_shape DynamicEvent list."""
        if not control.dynamic_shape:
            return
        bar_dynamics: dict[int, str] = {}
        for de in control.dynamic_shape:
            if hasattr(de, "bar") and hasattr(de, "level"):
                bar_dynamics[de.bar] = de.level
        for bundle in bundles:
            dyn = bar_dynamics.get(bundle.bar)
            if dyn and bundle.beat <= 1.5:
                for event in bundle.events:
                    if event.dynamic is None:
                        event.dynamic = dyn

    def _apply_breathing(
        self,
        bundles: list[OnsetBundle],
        breathing_rules: list,
        control: PhraseControlIR,
        trace: ContextTrace,
    ) -> None:
        """Insert a real breath in the melody, making room for it.

        This inserted 72 rests across an eight-phrase piece and 4 survived, all
        of them duplicates piled on two instants. Three separate reasons, and
        each one alone was enough to make the breathing plan decorative:

        * Every rule of the same category computed the SAME (bar, beat) — the
          phrase midpoint or its last bar — so three rules produced three rests
          at one instant. The rule itself was read only for whether its
          `placement` string contained "before".
        * `duration_beats_min` / `duration_beats_max` were never read. A rule
          whose technique is "Grand pause (G.P.) after dominant chord", asking
          for one to four beats of silence, produced an eighth rest.
        * The rest was appended on top of whatever was already sounding, and
          `_repair_engine_surface` correctly deletes a rest that shares a note's
          onset. The pass fed its own output to a repair that undid it.

        A breath is not an extra event laid over the line; it is the player
        cutting the previous note short to take air. So the note sounding across
        that instant is SHORTENED and the rest occupies the gap — and if there
        is no room to shorten, the breath is skipped rather than forced.
        """
        from .duration import beats_to_dur, dur_to_beats, largest_dur_at_most

        first_bar = control.bar_start
        last_bar = control.bar_start + control.bars - 1
        climax_bar = getattr(control, "cadence_bar", 0) or last_bar
        breathed: set[int] = set()

        for rule in breathing_rules:
            placement = str(getattr(rule, "placement", "") or "").lower()
            rtype = str(getattr(rule, "type", "") or "").lower()

            # WHICH BAR, read from what the rule says rather than from a
            # substring search for "before" that put every rule in one place.
            if "between_sections" in placement or "contemplat" in rtype:
                bar = last_bar  # a breath before the next section begins
            elif "after_climax" in placement or "aftermath" in rtype:
                bar = min(last_bar, climax_bar + 1)
            elif "before" in placement or "anticip" in rtype:
                bar = max(first_bar, climax_bar - 1)
            else:
                bar = control.bar_start + control.bars // 2
            bar = max(first_bar, min(last_bar, bar))
            if bar in breathed:
                continue  # one breath per bar, however many rules ask for it

            # A breath needs a note it can CUT. Take the last melody note in the
            # bar with room to be shortened, rather than naming an instant and
            # giving up when something is already sounding there — which is what
            # produced a rest laid over a note for the repair to delete.
            candidates = [
                (bundle, event, dur_to_beats(event.duration) or 0.0)
                for bundle in bundles
                if bundle.bar == bar
                for event in bundle.events
                if event.voice in ("soprano", "melody") and event.pitch != "rest"
            ]
            # A BEAT is the floor. A breath carved out of an eighth note is not
            # a breath, it is a rhythmic artifact — the note becomes a sixteenth
            # and gains a sixteenth rest nobody asked for. You cut a long note to
            # take air.
            candidates = [c for c in candidates if c[2] >= 1.0]
            if not candidates:
                continue
            bundle, event, span = max(candidates, key=lambda c: float(c[0].beat))

            # Cut the note to the largest notatable value that leaves the breath
            # room, and open the rest exactly where the note now ends — so the
            # silence IS the note's shortening, with no gap between them.
            want = float(getattr(rule, "duration_beats_min", 0) or 0) or 0.5
            want = min(want, span / 2)
            shorter = largest_dur_at_most(span - want)
            if shorter is None:
                continue
            kept = dur_to_beats(shorter) or 0.0
            gap = span - kept
            if kept <= 0 or gap < 0.25:
                continue
            dur = beats_to_dur(gap) or largest_dur_at_most(gap)
            if dur is None:
                continue

            event.duration = shorter
            rest_bundle = OnsetBundle(bar=bar, beat=float(bundle.beat) + kept)
            rest_bundle.events.append(
                OnsetEvent(
                    voice="soprano",
                    pitch="rest",
                    duration=dur,
                    role=NoteRole.STRUCTURAL.value,
                    justification=OnsetJustification(
                        structural_reasons=[NoteJustification.FORM.value],
                    ),
                )
            )
            bundles.append(rest_bundle)
            breathed.add(bar)
            trace.breathing_rules_applied.append(getattr(rule, "type", ""))

    def _index_voicings(self, voicings: list[dict]) -> dict[int, dict]:
        """Index voicings by bar number."""
        result: dict[int, dict] = {}
        for v in voicings:
            bar = v.get("bar", 0)
            if bar not in result:
                result[bar] = v
        return result


# ─── Internal tagged event (carries bar/beat for grouping) ────────────────


@dataclass
class _TaggedEvent:
    """Internal event carrying bar/beat position + voice + pitch + metadata."""

    _bar: int = 1
    _beat: float = 1.0
    voice: str = "soprano"
    pitch: str = "C4"
    duration: str = "q"
    role: str = NoteRole.STRUCTURAL.value
    dynamic: str | None = None
    articulation: str | None = None
    ornament: str | None = None
    tie: str | None = None
    expression: str | None = None
    justification: OnsetJustification = field(default_factory=OnsetJustification)

    def __init__(self, bar: int = 1, beat: float = 1.0, **kwargs):
        self._bar = bar
        self._beat = beat
        for k, v in kwargs.items():
            if k == "justification" and v is None:
                v = OnsetJustification()
            setattr(self, k, v)
        if not hasattr(self, "justification") or self.justification is None:
            self.justification = OnsetJustification()


def _lh_voice_for(events, index: int, meter) -> str:
    """Which voice a left-hand event belongs to.

    `direct_compose` settled this and recorded why: a plain single-stream left
    hand is ONE voice, so all of it is the bass line. Filing note[0] as the bass
    and everything after it as "accompaniment" gave every generated piece a
    `bass_foundation` of exactly one short note per bar — a bass that plays once
    and stops — while the actual moving bass was filed in a second voice that
    does not exist. Every per-layer statistic, the voice-leading check (which
    reads bass_foundation as the lower voice) and the craft checklist were all
    reading that artifact; the checklist duly reports "the bass does not sound
    in most bars" on engine output about real corpus patterns.

    The genuine two-voice case is a PEDAL under figuration: a first event that
    lasts the whole bar. That one keeps the split.
    """
    from .duration import bar_duration, dur_to_beats

    if not events:
        return "bass"
    try:
        cap = bar_duration(tuple(meter or (4, 4)))
        first = dur_to_beats(getattr(events[0], "duration", "q"))
    except Exception:
        return "bass"
    if first >= cap:  # a real pedal under a real figure
        return "bass" if index == 0 else "accomp"
    return "bass"
