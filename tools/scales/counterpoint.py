"""
Counterpoint and part-writing analysis over the real texture.

The audit's finding D11 was that nothing in the system detects "parallel fifths
or octaves in the real texture, unresolved dominants, doubled leading tone,
melodic tritones, static bass, harmonic stagnation, cadence correctness,
antecedent/consequent balance". Two of those got detectors; part-writing did not.
``validator.validate_voice_leading`` compares only ``principal_line`` against
``bass_foundation`` at *exact* (bar, beat) matches, so with a moving accompaniment
it makes roughly one comparison per bar and is blind by construction.

This module reads **every sounding voice at every attack point**, which is where
the errors actually are: consecutive fifths between an inner accompaniment voice
and the bass, an octave doubling that removes a voice, a leading tone that walks
down instead of up, a seventh left hanging.

Two things are load-bearing about how this is written:

**It reports, it never blocks.** Every finding carries a severity, and the
severities were chosen by running the detectors over real scores. This project's
standing test is "would this rule reject canonical music?" — and the answer for
strict species-counterpoint rules applied to Chopin is *yes, constantly*.
Parallel fifths between two inner voices of a Romantic accompaniment figure are
not an error; parallel octaves between the melody and the bass in a Classical
texture are. The severities encode that difference.

**Simultaneity is computed by sounding, not by onset.** A note is "sounding" at
time t if it started at or before t and has not yet ended. Comparing only notes
that share an exact onset misses every suspension and every pedal — which is to
say, it misses counterpoint.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import pairwise
from typing import Any

from .duration import dur_to_beats
from .pitch import is_minor_key, key_to_root_midi, pitch_to_midi

# ─── Finding ─────────────────────────────────────────────────────────────────


@dataclass
class PartWritingFinding:
    kind: str
    bar: int
    beat: float
    severity: str = "warn"  # "error" | "warn" | "info"
    voices: tuple[str, str] = ("", "")
    detail: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "bar": self.bar,
            "beat": round(float(self.beat), 4),
            "severity": self.severity,
            "voices": list(self.voices),
            "detail": self.detail,
        }


@dataclass
class CounterpointReport:
    findings: list[PartWritingFinding] = field(default_factory=list)
    attack_points: int = 0
    voice_count: int = 0
    independence: float = 0.0  # 0-1: how independently the voices move
    notes: list[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warn")

    def by_kind(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.kind] = out.get(f.kind, 0) + 1
        return out

    def as_dict(self, limit: int = 40) -> dict[str, Any]:
        return {
            "attack_points": self.attack_points,
            "voice_count": self.voice_count,
            "independence": round(self.independence, 3),
            "errors": self.error_count,
            "warnings": self.warn_count,
            "by_kind": self.by_kind(),
            "findings": [f.as_dict() for f in self.findings[:limit]],
            "notes": self.notes,
        }


# ─── Voice extraction ────────────────────────────────────────────────────────

_MELODIC_LAYERS = ("principal_line", "foreground")
_BASS_LAYERS = ("bass_foundation",)
_PIANO_LAYERS = (
    "principal_line",
    "counter_reply",
    "response_layer",
    "bass_foundation",
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


@dataclass
class _Sounding:
    """One pitch of one voice, with the span over which it sounds."""

    voice: str
    midi: int
    start: Fraction
    end: Fraction
    bar: int
    beat: float
    role: str = ""
    is_attack: bool = True


def _beats_per_bar(meter) -> Fraction:
    """Beats in a bar, via the ONE guarded implementation.

    Computed inline here before. A denominator of zero — which a
    partially-initialised slot or a malformed corpus record has — made
    `Fraction(0, 0)` and raised ZeroDivisionError out of every entry point in
    this module. Twenty-one places in the codebase did this arithmetic inline;
    duplicated inline arithmetic is this repository's most reliable bug source.
    """
    from .duration import bar_duration

    return bar_duration(meter)


def _abs_time(bar: int, beat: float, bpb: Fraction, first_bar: int) -> Fraction:
    b = Fraction(str(round(float(beat), 6))).limit_denominator(96)
    return (bar - first_bar) * bpb + (b - 1)


def _layer_names(layer_ir) -> list[str]:
    names = [n for n in _PIANO_LAYERS if getattr(layer_ir, n, None)]
    names += [n for n in _ORCH_LAYERS if getattr(layer_ir, n, None)]
    names += list((getattr(layer_ir, "inner_voices", None) or {}).keys())
    return names


def _layer_events(layer_ir, name: str) -> list:
    evs = getattr(layer_ir, name, None)
    if evs is None:
        evs = (getattr(layer_ir, "inner_voices", None) or {}).get(name)
    return evs or []


def extract_voices(layer_ir, ignore_ornamental: bool = True) -> list[_Sounding]:
    """Flatten a LayerIR into sounding spans, one per pitch per voice.

    A chord in one layer becomes several voices (``response_layer#0``,
    ``#1``, …) ordered low to high so a "voice" stays the same strand of the
    texture from chord to chord — comparing the top of one chord against the
    bottom of the next is what makes naive parallel detection useless.
    """
    bpb = _beats_per_bar(getattr(layer_ir, "meter", (4, 4)))
    all_events: list[tuple[str, Any]] = []
    for name in _layer_names(layer_ir):
        for ev in _layer_events(layer_ir, name):
            all_events.append((name, ev))
    if not all_events:
        return []
    first_bar = min(int(getattr(ev, "bar", 1)) for _, ev in all_events)

    out: list[_Sounding] = []
    for name, ev in all_events:
        pitch = getattr(ev, "pitch", None)
        if not pitch or pitch == "rest":
            continue
        role = getattr(ev, "role", "") or ""
        if ignore_ornamental and (role == "ornamental" or getattr(ev, "ornament", None) == "grace"):
            continue
        names = pitch if isinstance(pitch, list) else [pitch]
        midis = []
        for p in names:
            m = pitch_to_midi(p)
            if m is not None:
                midis.append(m)
        if not midis:
            continue
        midis.sort()
        bar = int(getattr(ev, "bar", 1))
        beat = float(getattr(ev, "beat", 1.0))
        start = _abs_time(bar, beat, bpb, first_bar)
        dur = dur_to_beats(getattr(ev, "duration", "q"))
        if dur <= 0:
            dur = Fraction(1, 8)
        for i, m in enumerate(midis):
            vname = name if len(midis) == 1 else f"{name}#{i}"
            out.append(
                _Sounding(
                    voice=vname,
                    midi=m,
                    start=start,
                    end=start + dur,
                    bar=bar,
                    beat=beat,
                    role=role,
                )
            )
    out.sort(key=lambda s: (s.start, s.midi))
    return _split_overlaps(out)


def _split_overlaps(spans: list[_Sounding]) -> list[_Sounding]:
    """Give overlapping notes of one layer their own voice names.

    Two notes of the same layer that sound at the same time ARE two voices —
    that is what "sounding at the same time" means. Leaving them under one name
    made the later one replace the earlier in ``sounding_at``, so a sustained
    pedal note under its own figuration (the commonest two-voice texture in
    keyboard writing, and the one this project already had to fix once at the
    engraving layer) was invisible to every measurement built on top: the
    simultaneity count, the hand span, the parallel check.

    Notes are assigned to the lowest-numbered strand that is free, so a voice
    stays the same strand for as long as it keeps sounding.
    """
    by_layer: dict[str, list[_Sounding]] = {}
    for sp in spans:
        by_layer.setdefault(sp.voice, []).append(sp)

    out: list[_Sounding] = []
    for name, group in by_layer.items():
        group.sort(key=lambda s: (s.start, s.midi))
        strand_free_at: list[Fraction] = []
        for sp in group:
            slot = next((i for i, free in enumerate(strand_free_at) if free <= sp.start), None)
            if slot is None:
                slot = len(strand_free_at)
                strand_free_at.append(sp.end)
            else:
                strand_free_at[slot] = sp.end
            if slot > 0:
                sp.voice = f"{name}@{slot}"
            out.append(sp)
    out.sort(key=lambda s: (s.start, s.midi))
    return out


def sounding_at(spans: Sequence[_Sounding], t: Fraction) -> dict[str, _Sounding]:
    """Which voice sounds which pitch at time ``t``."""
    out: dict[str, _Sounding] = {}
    for s in spans:
        if s.start <= t < s.end:
            prev = out.get(s.voice)
            # A voice sounding two pitches at once (a chord filed under one name)
            # keeps the later attack — that is the note the ear tracks.
            if prev is None or s.start > prev.start:
                out[s.voice] = s
    return out


def attack_times(spans: Sequence[_Sounding]) -> list[Fraction]:
    return sorted({s.start for s in spans})


# ─── Detectors ───────────────────────────────────────────────────────────────

_PERFECT = {0: "octave", 7: "fifth"}

# How many consecutive attack points a pair must stay locked at the octave (or
# unison) before it is read as a deliberate DOUBLING rather than a part-writing
# error. Falsified against 770 bars of Mozart, Beethoven and Chopin: without
# this exemption the detector fired 217 times on real music, because doubling
# the melody in octaves is one of the most common textures in the repertoire.
_DOUBLING_RUN = 3


def find_doubled_pairs(spans: Sequence[_Sounding]) -> set:
    """Voice pairs that move locked in octaves/unisons — i.e. one line, doubled.

    Returns a set of frozenset({voice_a, voice_b}). A pair in this set is one
    musical line written twice, so consecutive octaves between them are the
    point, not a mistake.
    """
    times = attack_times(spans)
    run: dict[frozenset, int] = {}
    doubled: set = set()
    prev: dict[str, _Sounding] | None = None
    for t in times:
        state = sounding_at(spans, t)
        voices = sorted(state)
        seen: set = set()
        for i, v1 in enumerate(voices):
            for v2 in voices[i + 1 :]:
                gap = abs(state[v1].midi - state[v2].midi)
                key = frozenset((v1, v2))
                if gap % 12 == 0 and gap <= 24:
                    seen.add(key)
                    run[key] = run.get(key, 0) + 1
                    if run[key] >= _DOUBLING_RUN:
                        doubled.add(key)
        for key in list(run):
            if key not in seen:
                run[key] = 0
        prev = state
    _ = prev
    return doubled


def _perfect_kind(a: int, b: int) -> str | None:
    return _PERFECT.get(abs(a - b) % 12)


def _outer_pair(v1: str, v2: str) -> bool:
    """True when the pair is melody-against-bass — the exposed one."""
    m = any(v.split("#")[0] in _MELODIC_LAYERS for v in (v1, v2))
    b = any(v.split("#")[0] in _BASS_LAYERS for v in (v1, v2))
    return m and b


def detect_parallel_perfects(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """Consecutive fifths and octaves between the same pair of voices.

    Severity is the whole point here. Parallel octaves between the melody and
    the bass are heard as the texture collapsing to one voice and are an error
    in any style. The same interval between two inner notes of a broken-chord
    accompaniment is how accompaniments work, and flagging it would reject every
    Chopin nocturne ever written — that case is ``info`` and is not counted
    against the music.
    """
    times = attack_times(spans)
    doubled = find_doubled_pairs(spans)
    prev_state: dict[str, _Sounding] | None = None
    prev_t: Fraction | None = None
    for t in times:
        state = sounding_at(spans, t)
        if prev_state is not None:
            voices = sorted(set(state) & set(prev_state))
            for i, v1 in enumerate(voices):
                for v2 in voices[i + 1 :]:
                    # One line written in octaves is a doubling, not two voices
                    # in parallel. Real Mozart does this constantly; without the
                    # exemption this detector fired 217 times on 770 canonical
                    # bars, which would make it worse than useless.
                    if frozenset((v1, v2)) in doubled:
                        continue
                    a1, b1 = prev_state[v1].midi, prev_state[v2].midi
                    a2, b2 = state[v1].midi, state[v2].midi
                    if (a1, b1) == (a2, b2):
                        continue  # nothing moved; not parallel motion
                    if (a2 - a1) * (b2 - b1) <= 0:
                        continue  # not similar motion
                    # A shared leap in the SAME direction by the SAME interval is
                    # a transposed figure (both hands moving the whole texture),
                    # not two independent voices walking in parallel.
                    if a2 - a1 == b2 - b1 and abs(a2 - a1) > 2:
                        continue
                    k1 = _perfect_kind(a1, b1)
                    k2 = _perfect_kind(a2, b2)
                    if not k1 or k1 != k2:
                        continue
                    if abs(a1 - b1) == abs(a2 - b2) == 0:
                        continue  # unison-to-unison in one written line
                    outer = _outer_pair(v1, v2)
                    same_layer = v1.split("#")[0] == v2.split("#")[0]
                    if outer:
                        sev = "warn" if k1 == "octave" else "info"
                    elif same_layer:
                        sev = "info"  # two notes of one chord figure
                    else:
                        sev = "info"
                    report.findings.append(
                        PartWritingFinding(
                            kind=f"parallel_{k1}s",
                            bar=state[v1].bar,
                            beat=state[v1].beat,
                            severity=sev,
                            voices=(v1, v2),
                            detail=(f"consecutive {k1}s {a1}->{a2} against {b1}->{b2}"),
                        )
                    )
        prev_state, prev_t = state, t
    _ = prev_t


def detect_hidden_perfects(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """Similar motion into a perfect interval with a leap in the upper voice.

    Only reported between the outer voices, and only when the top voice leaps —
    the "direct octave" that a trained ear hears at a cadence. Inside a texture
    it is unremarkable and is not reported at all.
    """
    times = attack_times(spans)
    prev_state: dict[str, _Sounding] | None = None
    for t in times:
        state = sounding_at(spans, t)
        if prev_state is not None:
            voices = sorted(set(state) & set(prev_state))
            for i, v1 in enumerate(voices):
                for v2 in voices[i + 1 :]:
                    if not _outer_pair(v1, v2):
                        continue
                    a1, b1 = prev_state[v1].midi, prev_state[v2].midi
                    a2, b2 = state[v1].midi, state[v2].midi
                    if (a2 - a1) * (b2 - b1) <= 0:
                        continue
                    k2 = _perfect_kind(a2, b2)
                    k1 = _perfect_kind(a1, b1)
                    if not k2 or k1 == k2:
                        continue  # a real parallel is another detector's job
                    upper, prev_upper = (a2, a1) if a2 > b2 else (b2, b1)
                    if abs(upper - prev_upper) <= 2:
                        continue  # the top voice stepped — this is fine
                    report.findings.append(
                        PartWritingFinding(
                            kind=f"hidden_{k2}",
                            bar=state[v1].bar,
                            beat=state[v1].beat,
                            severity="info",
                            voices=(v1, v2),
                            detail=f"similar motion by leap into a {k2}",
                        )
                    )
        prev_state = state


def detect_voice_crossing(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """The melody dipping below the bass, or the hands colliding.

    Only melody-against-bass is reported: inner voices cross all the time and it
    is not a defect, but a melody underneath its own bass line is inaudible, and
    a right hand written below the left is unplayable as notated.
    """
    for t in attack_times(spans):
        state = sounding_at(spans, t)
        mel = [s for v, s in state.items() if v.split("#")[0] in _MELODIC_LAYERS]
        bass = [s for v, s in state.items() if v.split("#")[0] in _BASS_LAYERS]
        if not mel or not bass:
            continue
        top = max(mel, key=lambda s: s.midi)
        low = max(bass, key=lambda s: s.midi)
        # A momentary brush past the accompaniment's top note is normal writing;
        # a melody buried a whole tone or more under it is the failure.
        if top.midi < low.midi - 1 and (top.end - top.start) >= Fraction(1, 4):
            report.findings.append(
                PartWritingFinding(
                    kind="voice_crossing",
                    bar=top.bar,
                    beat=top.beat,
                    severity="warn",
                    voices=(top.voice, low.voice),
                    detail=f"melody {top.midi} below accompaniment top {low.midi}",
                )
            )


def detect_spacing_gaps(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """A hole in the middle of the texture, or a muddy low cluster.

    Two failures of real keyboard writing that no check in the system looked
    for: an octave-and-a-half of empty air between the bass and everything above
    it (thin, hollow), and two notes a third apart below the bass staff (muddy —
    the reason editors write "avoid thirds below C3").

    That editorial advice is measurable, and now measured. Across Mozart,
    Haydn, Beethoven and Chopin, the smallest interval between two notes BELOW
    C3, over 914 instants:

        octave  59.5%    fourth   6.6%
        fifth   17.0%    thirds   6.5%   (minor and major combined)

    Three quarters of low doublings are an octave or a fifth; a third is the
    interval they use LEAST down there. So this is not a stylistic preference
    to be relaxed — and the rate at which it fires on real music says the same:

        mozart 0.01/bar   haydn 0.00   bach 0.04   chopin 0.07   beethoven 0.19

    It essentially never fires on Mozart or Haydn. A generated section running
    0.27/bar is above Beethoven, the thickest of them, and twenty-seven times
    Mozart's own rate. Anything that thickens a bass should double it at the
    OCTAVE down here and save the third for the register above.
    """
    for t in attack_times(spans):
        state = sounding_at(spans, t)
        if len(state) < 2:
            continue
        pitches = sorted(s.midi for s in state.values())
        # Muddy low interval
        for lo, hi in pairwise(pitches):
            if hi < 48 and 1 <= hi - lo <= 4:
                s = next(x for x in state.values() if x.midi == lo)
                report.findings.append(
                    PartWritingFinding(
                        kind="muddy_low_interval",
                        bar=s.bar,
                        beat=s.beat,
                        severity="info",
                        voices=(s.voice, ""),
                        detail=f"{hi - lo} semitones below C3 — thick and indistinct",
                    )
                )
                break
        # Gap above the bass. Real Classical keyboard writing sits the bass an
        # octave and a half below the texture as a matter of course — measured
        # at 0.37 findings per bar of genuine Mozart when the threshold was 19
        # semitones. Two full octaves is the point where it reads as hollow.
        if len(pitches) >= 3 and pitches[1] - pitches[0] > 26:
            s = next(x for x in state.values() if x.midi == pitches[0])
            report.findings.append(
                PartWritingFinding(
                    kind="texture_gap",
                    bar=s.bar,
                    beat=s.beat,
                    severity="info",
                    voices=(s.voice, ""),
                    detail=f"{pitches[1] - pitches[0]} semitones of empty air above the bass",
                )
            )


def detect_leading_tone_handling(
    spans: Sequence[_Sounding], key: str, report: CounterpointReport
) -> None:
    """A leading tone that is doubled, or that fails to rise.

    The leading tone is the one scale degree with an obligation. Doubling it
    makes the obligation unfulfillable (two voices cannot both resolve to the
    tonic without parallel octaves), and letting it fall is the single most
    audible part-writing slip there is: the cadence loses its pull.

    Reported at ``warn``, never ``error`` — a leading tone in an inner voice
    falling to the fifth is standard practice in four-part writing when the
    outer voices are correct, and a descending melodic-minor scale contains a
    falling leading tone by definition.
    """
    root = key_to_root_midi(key)
    if root is None:
        return
    lt_pc = (root - 1) % 12
    tonic_pc = root % 12
    times = attack_times(spans)
    by_voice: dict[str, list[_Sounding]] = {}
    for s in spans:
        by_voice.setdefault(s.voice, []).append(s)
    for v in by_voice:
        by_voice[v].sort(key=lambda s: s.start)

    doubled = find_doubled_pairs(spans)
    for t in times:
        state = sounding_at(spans, t)
        lts = [s for s in state.values() if s.midi % 12 == lt_pc]
        if len(lts) >= 2:
            pair = frozenset((lts[0].voice, lts[1].voice))
            # Two voices an octave apart on the leading tone are ONE doubled
            # line, which is the normal way to write a loud dominant.
            if pair in doubled or abs(lts[0].midi - lts[1].midi) % 12 == 0:
                continue
            report.findings.append(
                PartWritingFinding(
                    kind="doubled_leading_tone",
                    bar=lts[0].bar,
                    beat=lts[0].beat,
                    severity="info",
                    voices=(lts[0].voice, lts[1].voice),
                    detail="the leading tone is doubled — both voices owe a resolution",
                )
            )

    for v, seq in by_voice.items():
        for i, (a, b) in enumerate(pairwise(seq)):
            if a.midi % 12 != lt_pc:
                continue
            if b.start != a.end:
                continue  # not the immediate continuation
            if b.midi % 12 == tonic_pc:
                continue  # resolved to the tonic (up, or octave-displaced)
            if not (abs(b.midi - a.midi) <= 2 and b.midi < a.midi):
                continue
            # A leading tone PASSED THROUGH on the way down is a scale, not a
            # broken promise — a descending scale contains one every octave, and
            # descending melodic minor has one by definition. Only a leading
            # tone that was *arrived at* (leapt to, or held) is structural and
            # therefore owes a resolution.
            prev = seq[i - 1] if i > 0 else None
            stepped_down_into = (
                prev is not None and prev.end == a.start and 0 < prev.midi - a.midi <= 2
            )
            if stepped_down_into:
                continue
            if (a.end - a.start) < Fraction(1, 2):
                continue  # too quick to be heard as a structural dominant third
            sev = "info"
            report.findings.append(
                PartWritingFinding(
                    kind="leading_tone_falls",
                    bar=a.bar,
                    beat=a.beat,
                    severity=sev,
                    voices=(v, ""),
                    detail="a held leading tone steps down instead of rising to the tonic",
                )
            )


def detect_unresolved_sevenths(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """A dissonant seventh above the bass that does not step down.

    A seventh is a promise: it leans and it must fall. Left hanging, the harmony
    stops meaning anything, which is exactly how "harmonically vague" generated
    music sounds. Only sevenths against a *sounding* bass count, and only when
    the voice actually continues.
    """
    by_voice: dict[str, list[_Sounding]] = {}
    for s in spans:
        by_voice.setdefault(s.voice, []).append(s)
    for v in by_voice:
        by_voice[v].sort(key=lambda s: s.start)

    for v, seq in by_voice.items():
        if v.split("#")[0] in _BASS_LAYERS:
            continue
        for a, b in pairwise(seq):
            # A note that is merely passing through is not a chordal seventh,
            # whatever interval it happens to form with the momentary bass.
            if a.role in ("passing", "neighbor", "ornamental", "anticipation"):
                continue
            # Too short to be heard as a dissonance that owes a resolution: a
            # sixteenth in a run is figuration, not a suspended seventh.
            if (a.end - a.start) < Fraction(1, 2):
                continue
            state = sounding_at(spans, a.start)
            basses = [s for k, s in state.items() if k.split("#")[0] in _BASS_LAYERS]
            if not basses:
                continue
            bass = min(basses, key=lambda s: s.midi)
            iv = (a.midi - bass.midi) % 12
            if iv != 10:  # minor seventh above the bass
                continue
            # Require the rest of the sonority to agree that this IS a seventh
            # chord: a third or a fifth above the same bass must also sound.
            others = {
                (s.midi - bass.midi) % 12
                for s in state.values()
                if s.midi != a.midi and s.midi != bass.midi
            }
            if not ({3, 4} & others) and not ({7} & others):
                continue
            if b.start != a.end:
                continue
            step = b.midi - a.midi
            if -2 <= step < 0:
                continue  # resolved down by step — correct
            if step == 0:
                continue  # held; the resolution may come later
            report.findings.append(
                PartWritingFinding(
                    kind="unresolved_seventh",
                    bar=a.bar,
                    beat=a.beat,
                    severity="info",
                    voices=(v, bass.voice),
                    detail=f"seventh above the bass moves by {step} instead of falling a step",
                )
            )


def detect_melodic_tritone(spans: Sequence[_Sounding], report: CounterpointReport) -> None:
    """An unfilled leap of a tritone in a singing line.

    A melodic tritone is singable when it is filled in or immediately reversed;
    bare, it is the interval that makes a line sound generated rather than sung.
    Only the melodic layers are checked — an accompaniment figure outlining a
    diminished seventh is idiomatic.
    """
    by_voice: dict[str, list[_Sounding]] = {}
    for s in spans:
        if s.voice.split("#")[0] not in _MELODIC_LAYERS:
            continue
        by_voice.setdefault(s.voice, []).append(s)
    for v, seq in by_voice.items():
        seq.sort(key=lambda s: s.start)
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if abs(b.midi - a.midi) != 6:
                continue
            if b.start != a.end:
                continue  # a rest between them: not a leap, two gestures
            if (a.end - a.start) < Fraction(1, 2) and (b.end - b.start) < Fraction(1, 2):
                continue  # inside a run — figuration, not a sung interval
            nxt = seq[i + 2] if i + 2 < len(seq) else None
            if nxt is not None and nxt.start == b.end:
                # Any step away from the tritone's landing note resolves it; the
                # direction does not have to reverse (a diminished fifth filled
                # upward is standard). Requiring reversal flagged 70 intervals
                # in 770 bars of real music.
                if 0 < abs(nxt.midi - b.midi) <= 2:
                    continue
            prev = seq[i - 1] if i > 0 else None
            if prev is not None and prev.end == a.start and abs(a.midi - prev.midi) > 2:
                continue  # part of an arpeggiated outline, not a bare leap
            report.findings.append(
                PartWritingFinding(
                    kind="melodic_tritone",
                    bar=a.bar,
                    beat=a.beat,
                    severity="info",
                    voices=(v, ""),
                    detail="bare tritone leap, not recovered by step",
                )
            )


def detect_static_inner_voice(
    spans: Sequence[_Sounding], report: CounterpointReport, min_run: int = 8
) -> None:
    """A voice that repeats one pitch for a long stretch without being a pedal.

    A held pedal point is a device; a voice stuck on one note because nothing
    decided where it should go is filler, and it is the texture equivalent of a
    flat line.
    """
    by_voice: dict[str, list[_Sounding]] = {}
    for s in spans:
        by_voice.setdefault(s.voice, []).append(s)
    for v, seq in by_voice.items():
        seq.sort(key=lambda s: s.start)
        run_start, run_len = 0, 1
        for i in range(1, len(seq) + 1):
            same = i < len(seq) and seq[i].midi == seq[i - 1].midi
            if same:
                run_len += 1
                continue
            if run_len >= min_run:
                s = seq[run_start]
                report.findings.append(
                    PartWritingFinding(
                        kind="static_voice",
                        bar=s.bar,
                        beat=s.beat,
                        severity="info",
                        voices=(v, ""),
                        detail=f"{run_len} consecutive soundings of the same pitch",
                    )
                )
            run_start, run_len = i, 1


def voice_independence(spans: Sequence[_Sounding]) -> float:
    """0-1: how often the voices move in genuinely different directions.

    All voices moving in lockstep is homophony, which is a legitimate texture —
    so this is a *descriptor*, not a defect. It is the number the critic wants
    when asking "is this actually polyphonic or is it chords with a tune on
    top?", and no metric in the system answered that.
    """
    times = attack_times(spans)
    if len(times) < 2:
        return 0.0
    scored = 0
    independent = 0
    prev: dict[str, _Sounding] | None = None
    for t in times:
        state = sounding_at(spans, t)
        if prev is not None:
            shared = set(state) & set(prev)
            if len(shared) >= 2:
                dirs = set()
                for v in shared:
                    d = state[v].midi - prev[v].midi
                    dirs.add((d > 0) - (d < 0))
                scored += 1
                if len(dirs) > 1:
                    independent += 1
        prev = state
    return independent / scored if scored else 0.0


# ─── Entry point ─────────────────────────────────────────────────────────────


def analyze_counterpoint(
    layer_ir,
    key: str | None = None,
    *,
    enable: dict[str, bool] | None = None,
) -> CounterpointReport:
    """Full part-writing pass over a phrase or a whole assembled piece."""
    report = CounterpointReport()
    spans = extract_voices(layer_ir)
    if not spans:
        report.notes.append("no sounding notes")
        return report
    report.attack_points = len(attack_times(spans))
    report.voice_count = len({s.voice for s in spans})
    report.independence = voice_independence(spans)

    on = {
        "parallels": True,
        "hidden": True,
        "crossing": True,
        "spacing": True,
        "leading_tone": True,
        "sevenths": True,
        "tritone": True,
        "static": True,
    }
    on.update(enable or {})

    if on["parallels"]:
        detect_parallel_perfects(spans, report)
    if on["hidden"]:
        detect_hidden_perfects(spans, report)
    if on["crossing"]:
        detect_voice_crossing(spans, report)
    if on["spacing"]:
        detect_spacing_gaps(spans, report)
    if on["leading_tone"]:
        k = key or getattr(layer_ir, "key", None) or "C"
        detect_leading_tone_handling(spans, k, report)
    if on["sevenths"]:
        detect_unresolved_sevenths(spans, report)
    if on["tritone"]:
        detect_melodic_tritone(spans, report)
    if on["static"]:
        detect_static_inner_voice(spans, report)

    report.findings.sort(key=lambda f: (f.bar, f.beat, f.kind))
    if is_minor_key(key or getattr(layer_ir, "key", "C") or "C"):
        report.notes.append("minor key: a falling leading tone may be melodic-minor descent")
    return report


def summarize_for_critic(report: CounterpointReport, limit: int = 12) -> list[str]:
    """Plain lines a reviewer can read, worst first, without the noise.

    ``info`` findings are deliberately excluded: they describe the texture, they
    do not diagnose it, and putting them in front of a reviewer is how a
    detector becomes a revision target instead of a diagnostic.
    """
    out = []
    for f in report.findings:
        if f.severity == "info":
            continue
        out.append(f"bar {f.bar} beat {f.beat:g}: {f.kind.replace('_', ' ')} — {f.detail}")
        if len(out) >= limit:
            break
    return out


# ─── What a phrase leaves behind ─────────────────────────────────────────────
#
# The two facts a composer looks at first when continuing from the previous
# phrase: where its melody came to rest and which way it was moving, and whether
# it left a dissonance hanging. Neither existed anywhere. `ContinuationContext`
# declares `last_soprano_pitch`, `last_soprano_contour` and `pending_resolution`
# and no code writes or reads any of them; the live continuity context reports
# the melody's recent RANGE but not its endpoint, which is a different question.
#
# Without them, phrase N+1 cannot know where phrase N ended, so every phrase
# begins as if from nothing — the most audible cause of music that restarts
# rather than continues.


def phrase_tail(layer_ir, key: str | None = None) -> dict[str, Any]:
    """Where this phrase leaves the music, for the next one to continue from.

    Returns the melody's final pitch and direction, the bass's final pitch, the
    closing sonority, and any dissonance still unresolved at the double bar.
    """
    spans = extract_voices(layer_ir)
    out: dict[str, Any] = {
        "last_soprano_pitch": None,
        "last_soprano_midi": None,
        "last_soprano_contour": None,
        "last_bass_pitch": None,
        "last_bass_midi": None,
        "pending_resolution": None,
        "final_interval_from_bass": None,
    }
    if not spans:
        return out

    from .pitch import midi_to_pitch

    key = key or getattr(layer_ir, "key", "C") or "C"
    end = max(s.end for s in spans)

    def _last_of(layers):
        candidates = [s for s in spans if s.voice.split("#")[0].split("@")[0] in layers]
        return max(candidates, key=lambda s: (s.start, s.midi)) if candidates else None

    soprano = _last_of(_MELODIC_LAYERS)
    bass = _last_of(_BASS_LAYERS)
    if soprano is None:
        # A phrase with no principal line still has a top voice.
        latest = max(s.start for s in spans)
        top = [s for s in spans if s.start == latest]
        soprano = max(top, key=lambda s: s.midi) if top else None

    if soprano is not None:
        out["last_soprano_midi"] = soprano.midi
        out["last_soprano_pitch"] = midi_to_pitch(soprano.midi, key)
        # Direction of the approach to that last note — what the line was doing
        # as it arrived, which is what decides whether continuing feels natural.
        same_voice = sorted((s for s in spans if s.voice == soprano.voice), key=lambda s: s.start)
        if len(same_voice) >= 2:
            step = soprano.midi - same_voice[-2].midi
            out["last_soprano_contour"] = (
                "rising" if step > 0 else ("falling" if step < 0 else "static")
            )
            out["last_soprano_interval"] = step

    if bass is not None:
        out["last_bass_midi"] = bass.midi
        out["last_bass_pitch"] = midi_to_pitch(bass.midi, key)
        if soprano is not None:
            out["final_interval_from_bass"] = (soprano.midi - bass.midi) % 12

    # A dissonance still sounding when everything else has stopped owes a
    # resolution the next phrase has to honour.
    #
    # CALIBRATED against 126 real 8-bar phrase endings. The first version
    # counted fourths, tritones and major sevenths as well, and fired on
    # **49% of them** — because a fourth above the bass is consonant in tonal
    # practice (it is an inverted fifth), and a tritone at a phrase end is
    # usually just a half cadence's dominant seventh doing exactly what a half
    # cadence does. Neither is an unpaid debt.
    #
    # What is left is the minor seventh and the minor ninth: intervals that
    # genuinely lean, held to the end by a voice that was not merely passing
    # through.
    _OWED = {10: "seventh", 1: "minor ninth"}
    still = [
        s
        for s in spans
        if s.end >= end
        and s.role not in ("passing", "neighbor", "ornamental", "anticipation")
        and (s.end - s.start) >= Fraction(1, 2)
    ]
    if bass is not None and still:
        for s in still:
            if s.midi == bass.midi:
                continue
            iv = (s.midi - bass.midi) % 12
            if iv in _OWED:
                out["pending_resolution"] = (
                    f"{_OWED[iv]} above the bass ({midi_to_pitch(s.midi, key)} "
                    f"over {midi_to_pitch(bass.midi, key)}) is left sounding"
                )
                break
    return out


def continuation_hint(tail: dict[str, Any]) -> str:
    """One sentence telling the next phrase what it is continuing from."""
    if not tail or tail.get("last_soprano_pitch") is None:
        return ""
    parts = [f"the melody ended on {tail['last_soprano_pitch']}"]
    contour = tail.get("last_soprano_contour")
    if contour and contour != "static":
        parts.append(f"{contour} into it")
    if tail.get("last_bass_pitch"):
        parts.append(f"over {tail['last_bass_pitch']} in the bass")
    line = ", ".join(parts)
    if tail.get("pending_resolution"):
        line += f" — and a {tail['pending_resolution']}, which this phrase owes"
    return line
