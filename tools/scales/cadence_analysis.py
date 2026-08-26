"""
Cadence analysis — what actually closes each phrase, and whether it varies.

A cadence is where a phrase means something: it is the punctuation of tonal
music, and a listener tracks it whether or not they can name it. Nothing in this
system reads the cadence that was *written*. The plan names a `cadence_target`
("PAC", "HC") on every phrase slot, the gate never checks it, and the review
never hears it — so a phrase planned to end on a half cadence and written to end
on a plain tonic passes everything.

The second failure is more audible and was found by eye, not by any tool: the
same cadence formula appearing in 7 of 41 bars. Real music varies its closes.
Seven identical cadences in a short piece is the punctuation equivalent of
ending every sentence with the same four words.

This module answers three questions:

1. **What cadence is this?** Read from the notes — the bass motion, the melody's
   landing degree, the metric placement — not from the plan's label.
2. **Is it the one that was planned?** A mismatch is information for the critic,
   never an automatic revision: a composer who writes a better cadence than the
   plan asked for has improved the piece.
3. **Are they all the same?** A formula fingerprint per cadence, so repetition
   is visible at a glance.

Roman numerals go through ``harmony_analysis`` rather than music21 — its
``RomanNumeral`` raises on several symbols this corpus actually contains
("V7/V", "Imaj7", "vo65"), and every call site that wrapped it in a bare
``except`` silently disabled the check it was guarding.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

from .counterpoint import extract_voices, sounding_at
from .pitch import is_minor_key, key_to_root_midi

# ─── Cadence vocabulary ──────────────────────────────────────────────────────
#
# Named as a musician names them. The distinction that matters most in practice
# is PAC vs IAC: both are V-I, but only a PAC — soprano on the tonic, both
# chords in root position — actually closes. A piece whose every "perfect"
# cadence is really imperfect never sounds finished, and nothing measured it.

CADENCE_KINDS = (
    "PAC",  # perfect authentic: V-I, both root position, melody lands on 1
    "IAC",  # imperfect authentic: V-I but inverted or melody lands on 3 or 5
    "HC",  # half: ends ON the dominant
    "PHRYGIAN",  # iv6-V in minor
    "DC",  # deceptive: V-vi (or V-VI)
    "PLAGAL",  # IV-I
    "EVADED",  # dominant that resolves to an inversion or elides
    "NONE",  # no cadential motion found
)


@dataclass
class Cadence:
    bar: int
    beat: float
    kind: str = "NONE"
    approach_roman: str = ""
    goal_roman: str = ""
    bass_motion: int | None = None  # semitones, approach -> goal
    soprano_degree: int | None = None  # scale degree the melody lands on
    root_position: bool = True
    metric_strength: str = "downbeat"  # downbeat | strong | weak
    formula: str = ""  # fingerprint for repetition detection
    confidence: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "bar": self.bar,
            "beat": round(float(self.beat), 3),
            "kind": self.kind,
            "approach": self.approach_roman,
            "goal": self.goal_roman,
            "soprano_degree": self.soprano_degree,
            "root_position": self.root_position,
            "metric_strength": self.metric_strength,
            "formula": self.formula,
            "confidence": round(self.confidence, 2),
        }

    def describe(self) -> str:
        names = {
            "PAC": "perfect authentic cadence",
            "IAC": "imperfect authentic cadence",
            "HC": "half cadence",
            "PHRYGIAN": "Phrygian half cadence",
            "DC": "deceptive cadence",
            "PLAGAL": "plagal cadence",
            "EVADED": "evaded cadence",
            "NONE": "no cadence",
        }
        base = names.get(self.kind, self.kind)
        if self.approach_roman and self.goal_roman:
            base += f" ({self.approach_roman}-{self.goal_roman})"
        if self.soprano_degree:
            base += f", melody on {self.soprano_degree}"
        return base


@dataclass
class CadenceReport:
    cadences: list[Cadence] = field(default_factory=list)
    planned: str | None = None
    matches_plan: bool | None = None
    variety: float = 0.0  # distinct formulas / total
    repeated_formulas: list[tuple[str, int]] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "cadences": [c.as_dict() for c in self.cadences],
            "planned": self.planned,
            "matches_plan": self.matches_plan,
            "variety": round(self.variety, 3),
            "repeated_formulas": self.repeated_formulas,
            "observations": self.observations,
            "suggestions": self.suggestions,
        }


# ─── Reading the notes ───────────────────────────────────────────────────────


def _tonic_and_mode(key: str) -> tuple[int, str]:
    root = key_to_root_midi(key or "C")
    tonic = (root or 60) % 12
    return tonic, ("minor" if is_minor_key(key or "C") else "major")


_DEGREE_OF_SEMITONE_MAJOR = {0: 1, 2: 2, 4: 3, 5: 4, 7: 5, 9: 6, 11: 7}
_DEGREE_OF_SEMITONE_MINOR = {0: 1, 2: 2, 3: 3, 5: 4, 7: 5, 8: 6, 10: 7, 11: 7}


def scale_degree(midi: int, tonic_pc: int, mode: str) -> int | None:
    table = _DEGREE_OF_SEMITONE_MINOR if mode == "minor" else _DEGREE_OF_SEMITONE_MAJOR
    return table.get((midi - tonic_pc) % 12)


def _metric_strength(beat: float, meter: tuple[int, int]) -> str:
    b = round(float(beat), 3)
    if abs(b - 1.0) < 0.01:
        return "downbeat"
    try:
        num, den = int(meter[0]), int(meter[1])
    except (TypeError, ValueError, IndexError):  # a malformed meter, not a bug here
        num, den = 4, 4
    if den == 8 and num in (6, 9, 12) and abs(b - 2.5) < 0.01:
        return "strong"
    if num == 4 and den == 4 and abs(b - 3.0) < 0.01:
        return "strong"
    return "weak"


def _sonority_at(spans, t) -> tuple[int | None, list[int]]:
    """(bass midi, all sounding pitch classes) at one moment."""
    state = sounding_at(spans, t)
    if not state:
        return None, []
    mids = [s.midi for s in state.values()]
    return min(mids), sorted({m % 12 for m in mids})


def _sonority_over(spans, start, end) -> tuple[int | None, list[int]]:
    """(lowest midi, pitch classes) over a SPAN rather than an instant.

    A cadence is not an instant. Read at a single point, the arrival of a
    cadence in a real texture is often one note — the bass alone, or the melody
    alone after the accompaniment has stopped — and one pitch class cannot be
    named as a chord at all. Reading five of nine cadences as "no cadence" was
    this, not a property of the music: bar 8 of the piece under test is
    unambiguous F major across the whole bar, but its final attack is a bare F.
    """
    hits = [s for s in spans if s.start < end and s.end > start]
    if not hits:
        return _sonority_at(spans, start)
    return min(s.midi for s in hits), sorted({s.midi % 12 for s in hits})


def _melody_at(spans, t) -> int | None:
    state = sounding_at(spans, t)
    mel = [
        s
        for v, s in state.items()
        if v.split("#")[0].split("@")[0] in ("principal_line", "foreground")
    ]
    if mel:
        return max(mel, key=lambda s: s.midi).midi
    return max((s.midi for s in state.values()), default=None)


def _read_roman(pcs: Sequence[int], bass: int | None, tonic_pc: int, mode: str) -> str:
    """Name the sonority through the shared analyzer, or "" if unreadable."""
    if not pcs:
        return ""
    try:
        from .harmony_analysis import candidates, spell_roman
    except ImportError:  # pragma: no cover - module optional at import time
        return ""
    # ``candidates`` takes a 12-slot vector indexed by pitch class, not a dict:
    # a dict makes ``sum(weights)`` add the KEYS and ``enumerate(weights)``
    # iterate them, so every reading came back empty and the roman fields in
    # every cadence printed as "-".
    weights = [0.0] * 12
    for pc in pcs:
        weights[pc % 12] = 1.0
    # NOT a blind except. `candidates` raises TypeError on a dict and ValueError
    # on a wrong-length vector — guards added specifically so misuse is loud —
    # and catching Exception here silently defeated them, turning "this caller
    # is wrong" into "this bar has no readable harmony". A programming error
    # must reach the programmer.
    cands = candidates(weights, (bass % 12) if bass is not None else None, tonic_pc, mode)
    if not cands:
        return ""
    _score, root, qual, inv = cands[0]
    return spell_roman(root, qual, inv, tonic_pc, mode)


def _is_dominant(pcs: Sequence[int], tonic_pc: int, mode: str) -> bool:
    """Dominant function by content: contains scale degrees 5 and 7."""
    s = {(p - tonic_pc) % 12 for p in pcs}
    return 7 in s and 11 in s


def _is_tonic(pcs: Sequence[int], tonic_pc: int, mode: str) -> bool:
    s = {(p - tonic_pc) % 12 for p in pcs}
    third = 3 if mode == "minor" else 4
    return 0 in s and (third in s or len(s) <= 2)


def _is_submediant(pcs: Sequence[int], tonic_pc: int, mode: str) -> bool:
    s = {(p - tonic_pc) % 12 for p in pcs}
    sixth = 8 if mode == "minor" else 9
    return sixth in s and 0 in s and 11 not in s


def _is_subdominant(pcs: Sequence[int], tonic_pc: int, mode: str) -> bool:
    s = {(p - tonic_pc) % 12 for p in pcs}
    return 5 in s and 0 in s and 11 not in s


def classify_cadence(
    approach_pcs: Sequence[int],
    approach_bass: int | None,
    goal_pcs: Sequence[int],
    goal_bass: int | None,
    soprano_midi: int | None,
    tonic_pc: int,
    mode: str,
    is_final: bool,
    approach_degree: int | None = None,
    goal_degree: int | None = None,
    approach_quality: str = "",
    goal_quality: str = "",
) -> tuple[str, bool, int | None]:
    """(kind, root_position, soprano_degree) from the two chords.

    When the caller knows each chord's ROOT (``*_degree``, semitones above the
    tonic, as the harmonic analyzer reports it) the classification uses it. The
    pitch-class fallback below is only for callers that do not, and it is
    genuinely unreliable: an A minor triad contains C and E, so a deceptive
    cadence onto vi in C major looked exactly like an incomplete tonic and every
    deceptive cadence in the repertoire read as an imperfect authentic one.

    Read from the notes. The plan's label is deliberately not consulted — the
    whole point is to find out whether the music agrees with the plan.
    """
    sop_deg = scale_degree(soprano_midi, tonic_pc, mode) if soprano_midi is not None else None
    goal_root_pos = goal_bass is not None and (
        (goal_bass - tonic_pc) % 12 == (goal_degree % 12 if goal_degree is not None else 0)
    )
    appr_root_pos = approach_bass is not None and (
        (approach_bass - tonic_pc) % 12
        == (approach_degree % 12 if approach_degree is not None else 7)
    )

    if goal_degree is not None:
        dom_approach = approach_degree is not None and (
            approach_degree % 12 == 7
            or (approach_degree % 12 == 11 and approach_quality.startswith(("dim", "o", "hd")))
        )
        goal_is_tonic = goal_degree % 12 == 0
        goal_is_submediant = goal_degree % 12 == (8 if mode == "minor" else 9)
        goal_is_dominant = goal_degree % 12 == 7
        appr_is_subdominant = approach_degree is not None and approach_degree % 12 == 5

        if goal_is_dominant:
            if (
                mode == "minor"
                and approach_degree is not None
                and approach_degree % 12 == 5
                and approach_bass is not None
                and (approach_bass - tonic_pc) % 12 == 8
            ):
                return "PHRYGIAN", True, sop_deg
            return "HC", True, sop_deg
        if dom_approach and goal_is_tonic:
            if goal_root_pos and appr_root_pos and sop_deg == 1:
                return "PAC", True, sop_deg
            if goal_root_pos and appr_root_pos:
                return "IAC", True, sop_deg
            return ("IAC" if goal_root_pos or sop_deg == 1 else "EVADED", goal_root_pos, sop_deg)
        if dom_approach and goal_is_submediant:
            return "DC", goal_root_pos, sop_deg
        if appr_is_subdominant and goal_is_tonic:
            return "PLAGAL", goal_root_pos, sop_deg
        if dom_approach:
            return "EVADED", goal_root_pos, sop_deg
        if is_final and goal_is_tonic:
            return "IAC", goal_root_pos, sop_deg
        return "NONE", goal_root_pos, sop_deg

    # ── Pitch-class fallback (no root information available) ─────────────────
    goal_root_pos = goal_bass is not None and (goal_bass - tonic_pc) % 12 == 0
    appr_root_pos = approach_bass is not None and (approach_bass - tonic_pc) % 12 == 7
    if not goal_pcs:
        return ("HC" if _is_dominant(approach_pcs, tonic_pc, mode) else "NONE", True, sop_deg)
    dom_approach = _is_dominant(approach_pcs, tonic_pc, mode)
    # Submediant is tested BEFORE tonic: vi shares two of its three notes with I.
    if dom_approach and _is_submediant(goal_pcs, tonic_pc, mode):
        return "DC", goal_root_pos, sop_deg
    if dom_approach and _is_tonic(goal_pcs, tonic_pc, mode):
        if goal_root_pos and appr_root_pos and sop_deg == 1:
            return "PAC", True, sop_deg
        if goal_root_pos and appr_root_pos:
            return "IAC", True, sop_deg
        return ("IAC" if goal_root_pos or sop_deg == 1 else "EVADED", goal_root_pos, sop_deg)
    if _is_subdominant(approach_pcs, tonic_pc, mode) and _is_tonic(goal_pcs, tonic_pc, mode):
        return "PLAGAL", goal_root_pos, sop_deg
    if _is_dominant(goal_pcs, tonic_pc, mode):
        if (
            mode == "minor"
            and approach_bass is not None
            and goal_bass is not None
            and (approach_bass - goal_bass) % 12 == 1
        ):
            return "PHRYGIAN", True, sop_deg
        return "HC", True, sop_deg
    if dom_approach:
        return "EVADED", goal_root_pos, sop_deg
    if is_final and _is_tonic(goal_pcs, tonic_pc, mode):
        return "IAC", goal_root_pos, sop_deg
    return "NONE", goal_root_pos, sop_deg


def _formula(c: Cadence) -> str:
    """A fingerprint for "is this the same cadence again".

    Deliberately coarse: kind, the melody's landing degree and the bass step.
    Two cadences with the same three are heard as the same gesture even if the
    figuration differs, which is exactly the repetition worth reporting.
    """
    return f"{c.kind}/{c.soprano_degree or '-'}/{c.bass_motion if c.bass_motion is not None else '-'}"


# ─── Entry points ────────────────────────────────────────────────────────────


def _beat_readings(spans, bar: int, meter, tonic_pc: int, mode: str):
    """Beat-by-beat harmonic reading of one bar, via the shared analyzer.

    Point-in-time sonorities cannot read a cadence: at the final attack of a
    real cadence bar there is often one note sounding, and one pitch class is
    not a chord. Duration-weighted beats with the analyzer's Viterbi smoothing
    give the harmony a listener actually hears — one chord held across the bar
    rather than a new "chord" on every passing note.
    """
    try:
        from .harmony_analysis import analyze_bar
    except ImportError:  # pragma: no cover - module optional
        return []
    in_bar = [sp for sp in spans if sp.bar == bar]
    if not in_bar:
        return []
    origin = min(sp.start for sp in in_bar)
    # Via the one guarded implementation: a zero denominator made Fraction(0, 0)
    # and raised out of read_cadence for any phrase with a malformed meter.
    from .duration import bar_duration

    bar_len = float(bar_duration(meter))
    try:
        den = int(meter[1])
        den = den if den > 0 else 4
    except (TypeError, ValueError, IndexError):
        den = 4
    beat_len = float(Fraction(4, den))
    triples = []
    for sp in spans:
        lo = float(sp.start - origin)
        hi = float(sp.end - origin)
        if hi <= 0 or lo >= bar_len:
            continue
        # Real MIDI, not a pitch class: ``pc_weights`` finds the bass as the
        # LOWEST PITCH of the sonority, so handing it pitch classes made C the
        # "bass" of any chord containing a C and read a root-position F major
        # tonic as I64. Every cadential goal chord in the piece was mislabelled.
        triples.append((max(0.0, lo), min(bar_len, hi), [sp.midi]))
    if not triples:
        return []
    # `analyze_bar` raises on misuse (a dict of weights, pitch classes where MIDI
    # is required). Those are programming errors and must not be swallowed into
    # "this bar has no harmony" — that is how a wrong call site stays invisible.
    return analyze_bar(triples, bar_len, beat_len, tonic_pc, mode)


def _pcs_of_roman(roman: str, tonic_pc: int, mode: str):
    try:
        from .harmony_analysis import roman_pitches

        return list(roman_pitches(roman, tonic_pc, mode) or [])
    except ImportError:  # pragma: no cover - module optional
        return []
    except (TypeError, ValueError):
        # An unreadable roman symbol is DATA, not a bug: the corpus contains
        # figures no parser covers.
        return []


def read_cadence(
    layer_ir,
    cadence_bar: int | None = None,
    key: str | None = None,
    is_final: bool = False,
) -> Cadence | None:
    """Read the cadence at ``cadence_bar`` (default: the phrase's last bar).

    The reading is taken from the notes, beat by beat, and the plan's label is
    deliberately not consulted — the whole point is to find out whether the
    music agrees with the plan.
    """
    spans = extract_voices(layer_ir)
    if not spans:
        return None
    key = key or getattr(layer_ir, "key", "C") or "C"
    tonic_pc, mode = _tonic_and_mode(key)
    meter = getattr(layer_ir, "meter", (4, 4))

    bars = sorted({s.bar for s in spans})
    target = int(cadence_bar) if cadence_bar else bars[-1]
    if target not in bars:
        target = min(bars, key=lambda b: abs(b - target))

    readings = _beat_readings(spans, target, meter, tonic_pc, mode)
    if not readings:
        return None

    # The goal is the LAST harmony of the cadence bar; the approach is the last
    # one before it that differs — taken from the previous bar when the whole
    # cadence bar is one chord, which is the commonest case of all.
    # Take the goal as the LAST HARMONIC RUN of the bar, read at the beat where
    # that harmony arrives — not at the bar's final beat. A cadence chord is
    # struck and then decorated, and the analyzer drops any beat where fewer
    # than two pitch classes sound: in the final bar of the piece under test,
    # beat 1 (the root-position tonic, bass F2 with the melody's F5) was dropped
    # for exactly that reason, and beats 2-3 read the A above it as the bass —
    # so the piece's final chord was reported as a first-inversion tonic.
    # Group by the chord's ROOT, not its printed figure: I followed by I6 is one
    # harmony in two positions, and treating the inversion change as a chord
    # change made the bar's own tonic its "approach" chord — so a plain final
    # tonic came out as a cadence from I to I6.
    def _chord_id(r):
        return (r.get("root_pc"), r.get("quality"))

    goal = readings[-1]
    goal_run_start = len(readings) - 1
    while goal_run_start > 0 and _chord_id(readings[goal_run_start - 1]) == _chord_id(goal):
        goal_run_start -= 1
    goal = readings[goal_run_start]

    approach = None
    for r in reversed(readings[:goal_run_start]):
        if _chord_id(r) != _chord_id(goal):
            approach = r
            break
    if approach is None and target - 1 in bars:
        prev = _beat_readings(spans, target - 1, meter, tonic_pc, mode)
        for r in reversed(prev):
            if _chord_id(r) != _chord_id(goal):
                approach = r
                break

    goal_pcs = _pcs_of_roman(str(goal.get("roman", "")), tonic_pc, mode)
    appr_pcs = (
        _pcs_of_roman(str(approach.get("roman", "")), tonic_pc, mode) if approach else []
    )
    goal_bass = (int(goal.get("root_pc", 0)) if goal.get("inversion", 0) == 0 else None)
    if goal_bass is None and goal_pcs:
        goal_bass = goal_pcs[0]
    appr_bass = None
    if approach:
        appr_bass = (
            int(approach.get("root_pc", 0)) if approach.get("inversion", 0) == 0 else None
        )
        if appr_bass is None and appr_pcs:
            appr_bass = appr_pcs[0]

    # The arrival is where the goal harmony STARTS in the bar, not the bar's
    # last attack: a chord struck on the downbeat and then decorated is heard as
    # landing on the downbeat, and timing it at the last attack reported every
    # cadence in a 3/4 piece as landing on beat 3.
    arrival_beat = goal.get("beat", 1.0)
    # If the harmony was already sounding before the analyzer's first readable
    # beat (a bass note struck alone on the downbeat under a single melody
    # note), the arrival is the downbeat, not the first beat that happened to
    # contain two pitch classes.
    if goal_run_start == 0 and readings and float(arrival_beat) > 1.0:
        bar_head = [sp for sp in spans if sp.bar == target]
        if bar_head:
            earliest = min(sp.start for sp in bar_head)
            head_pcs = {sp.midi % 12 for sp in bar_head if sp.start == earliest}
            if head_pcs <= set(goal_pcs):
                arrival_beat = min(float(sp.beat) for sp in bar_head if sp.start == earliest)

    # The analyzer reports the inversion of the beat it could read. When the
    # chord's real bass is struck earlier in the bar and held, that note is the
    # bass a listener hears, so re-derive the inversion from the lowest pitch
    # actually sounding from the arrival onward.
    region = [
        sp
        for sp in spans
        if sp.bar == target and float(sp.beat) >= float(arrival_beat) - 1e-6
    ]
    if region and goal_pcs:
        true_bass_pc = min(region, key=lambda sp: sp.midi).midi % 12
        root_pc = int(goal.get("root_pc", goal_pcs[0]))
        if true_bass_pc == root_pc % 12:
            goal_bass = root_pc
            goal = dict(goal)
            goal["inversion"] = 0
            goal["roman"] = str(goal.get("roman", "")).rstrip("6432")

    # The melody's LAST sounding note is what the ear hears land.
    mel = [
        sp
        for sp in spans
        if sp.bar == target
        and sp.voice.split("#")[0].split("@")[0] in ("principal_line", "foreground")
    ]
    soprano = max(mel, key=lambda sp: (sp.start, sp.midi)).midi if mel else None

    def _degree(reading):
        if not reading:
            return None
        root = reading.get("root_pc")
        return ((int(root) - tonic_pc) % 12) if root is not None else None

    kind, root_pos, sop_deg = classify_cadence(
        appr_pcs,
        appr_bass,
        goal_pcs,
        goal_bass,
        soprano,
        tonic_pc,
        mode,
        is_final,
        approach_degree=_degree(approach),
        goal_degree=_degree(goal),
        approach_quality=str(approach.get("quality", "")) if approach else "",
        goal_quality=str(goal.get("quality", "")),
    )
    # The analyzer already knows the inversion; trust it over the pc heuristic.
    if goal.get("inversion", 0) != 0:
        root_pos = False
        if kind == "PAC":
            kind = "IAC"
    if approach is not None and approach.get("inversion", 0) != 0 and kind == "PAC":
        kind = "IAC"

    cad = Cadence(
        bar=target,
        beat=float(arrival_beat),
        kind=kind,
        approach_roman=str(approach.get("roman", "")) if approach else "",
        goal_roman=str(goal.get("roman", "")),
        bass_motion=(
            ((goal_bass - appr_bass) % 12)
            if (goal_bass is not None and appr_bass is not None)
            else None
        ),
        soprano_degree=sop_deg,
        root_position=root_pos,
        metric_strength=_metric_strength(float(arrival_beat), meter),
        confidence=0.9 if (appr_pcs and goal_pcs) else 0.5,
    )
    cad.formula = _formula(cad)
    return cad


def check_against_plan(cadence: Cadence | None, planned: str | None) -> bool | None:
    """Does the written cadence match the planned one?

    ``None`` when there is nothing to compare. A mismatch is reported, never
    enforced: the plan is a plan, and a composer who writes a better cadence
    than the one asked for has improved the piece, not broken it.
    """
    if not planned or cadence is None:
        return None
    want = str(planned).strip().upper()
    aliases = {
        "AUTHENTIC": {"PAC", "IAC"},
        "PERFECT": {"PAC"},
        "IMPERFECT": {"IAC"},
        "HALF": {"HC", "PHRYGIAN"},
        "DECEPTIVE": {"DC"},
        "PLAGAL": {"PLAGAL"},
        "PAC": {"PAC"},
        "IAC": {"IAC", "PAC"},
        "HC": {"HC", "PHRYGIAN"},
        "DC": {"DC"},
    }
    accepted = aliases.get(want, {want})
    return cadence.kind in accepted


def analyze_cadences(
    phrases: Sequence[tuple[Any, int | None, str | None, str | None]],
) -> CadenceReport:
    """Cadences across a whole piece.

    ``phrases`` is a sequence of ``(layer_ir, cadence_bar, key, planned_kind)``.
    Whole-piece analysis is the only level at which the repetition question can
    be asked, and repetition is the finding that actually made the output sound
    machine-made.
    """
    report = CadenceReport()
    for i, (layer_ir, cad_bar, key, planned) in enumerate(phrases):
        cad = read_cadence(
            layer_ir, cadence_bar=cad_bar, key=key, is_final=(i == len(phrases) - 1)
        )
        if cad is None:
            continue
        cad_ok = check_against_plan(cad, planned)
        if cad_ok is False:
            report.observations.append(
                f"bar {cad.bar}: planned {planned}, wrote {cad.kind} "
                f"({cad.approach_roman}-{cad.goal_roman})"
            )
        report.cadences.append(cad)

    if not report.cadences:
        report.observations.append("no cadences readable")
        return report

    formulas: dict[str, int] = {}
    for c in report.cadences:
        formulas[c.formula] = formulas.get(c.formula, 0) + 1
    report.variety = len(formulas) / len(report.cadences)
    report.repeated_formulas = sorted(
        ((f, n) for f, n in formulas.items() if n > 1), key=lambda x: -x[1]
    )

    _suggest_cadences(report)
    return report


def _suggest_cadences(r: CadenceReport) -> None:
    n = len(r.cadences)
    kinds = [c.kind for c in r.cadences]
    r.observations.insert(0, f"{n} cadences: " + ", ".join(kinds))

    if n >= 4 and r.repeated_formulas:
        top_formula, count = r.repeated_formulas[0]
        if count >= max(3, n * 0.5):
            r.suggestions.append(
                f"The same cadence formula ({top_formula}) closes {count} of {n} "
                f"phrases. Cadences are the punctuation of the piece; using one "
                f"formula throughout is the aural equivalent of ending every "
                f"sentence with the same four words. A deceptive cadence where the "
                f"listener expects the tonic, or an inverted goal chord that keeps "
                f"the phrase open, costs two notes."
            )
    if n >= 4 and r.variety < 0.4:
        r.suggestions.append(
            f"Only {len({c.formula for c in r.cadences})} distinct cadence "
            f"gestures across {n} phrases. Interior phrases usually close weakly "
            f"(half or imperfect) so the final one can close strongly."
        )
    if n >= 3 and all(k in ("PAC", "IAC") for k in kinds):
        r.suggestions.append(
            "Every phrase ends with an authentic cadence, so every phrase sounds "
            "final and the piece has no forward momentum. A half cadence at the end "
            "of an antecedent is what makes the consequent feel answered."
        )
    if n >= 2 and kinds[-1] != "PAC":
        r.suggestions.append(
            f"The piece ends with a {kinds[-1]} rather than a perfect authentic "
            f"cadence — deliberate for an open ending, but if closure was intended "
            f"the melody needs to land on the tonic over a root-position chord."
        )
    weak_final = [c for c in r.cadences if c.metric_strength == "weak"]
    if len(weak_final) > n * 0.5 and n >= 4:
        r.suggestions.append(
            f"{len(weak_final)} of {n} cadences land off the beat. A cadence lands "
            f"on a downbeat unless it is deliberately elided."
        )


def cadence_summary_lines(report: CadenceReport, limit: int = 10) -> list[str]:
    """Reviewer-facing lines: what closes each phrase, in order."""
    return [f"bar {c.bar}: {c.describe()}" for c in report.cadences[:limit]]
