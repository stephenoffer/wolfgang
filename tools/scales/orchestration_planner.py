"""
OrchestrationPlanner — idiomatic piano-core → orchestra expansion.

Replaces SABRE's naive 3-role assignment with register-aware, dynamics-
aware planning: melody with climax doublings, divided inner voices,
sustained wind harmony, octave bass doubling, per-instrument range
clamping. Still deliberately conservative — it voices an already-finished
musical argument, it does not invent material.

Plan shape (per layer → instruments):
  principal_line     → lead violin/wind; flute doubles 8va at f+;
                       oboe doubles unison at mp-mf in singing register
  bass_foundation    → cello; contrabass doubles 8vb at mf+
  response_layer     → violin_2 / viola split by register; condensed
                       into sustained wind chords (clarinet+bassoon)
  counter_reply      → oboe (or viola)
  ornamental_surface → flute (when not doubling), else stays with lead
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .duration import bar_duration, beats_to_dur
from .models import LayerEvent, LayerIR
from .pitch import midi_to_pitch, pitch_to_midi
from .validator import INSTRUMENT_RANGES

_DYN_RANK = {
    "ppp": 0,
    "pp": 1,
    "p": 2,
    "mp": 3,
    "mf": 4,
    "f": 5,
    "ff": 6,
    "fff": 7,
    "sfz": 5,
    "fp": 4,
}

# The reverse direction, for parts the orchestrator WRITES rather than carries.
_RANK_DYN = ("ppp", "pp", "p", "mp", "mf", "f", "ff", "fff")


def pad_dynamic(rank: int) -> str:
    """What a sustaining wind pad is marked, under a melody at ``rank``.

    A pad supports rather than leads, so it sits one step below the texture it
    is holding up — the standard balance instruction in orchestral writing, and
    the reason a horn chord under a singing oboe is marked p and not mf.

    This exists because the pads were written with ``"dynamic": None``: the
    horn, clarinet and bassoon parts arrived carrying whole notes and no
    marking at all, which is not a stylistic weakness but an unplayable part.
    A wind player holding a chord has to be told how loud to hold it.
    """
    return _RANK_DYN[max(0, min(len(_RANK_DYN) - 1, int(rank) - 1))]

# Instrument-name → range-table key
_RANGE_ALIASES = {
    "violin_1": "violin",
    "violin_2": "violin",
    "violin_i": "violin",
    "violin_ii": "violin",
    "contrabass": "double_bass",
}

_MELODY_PREFERENCE = ["violin_1", "violin", "flute", "oboe", "clarinet", "trumpet"]
_BASS_PREFERENCE = ["cello", "bassoon", "trombone", "tuba", "double_bass", "contrabass"]


# ─── Practical range, and what a dynamic costs at the extremes ───────────────
#
# `INSTRUMENT_RANGES` gives the notes an instrument *can* produce. Writing to
# those limits is not orchestration — it is the difference between a part a
# player can read and one they dread. Every wind instrument's bottom minor third
# is unwieldy and will not speak quietly; every one's top is effortful and will
# not speak quietly either. A flute's lowest octave cannot be heard over a full
# orchestra at any dynamic, and a trumpet's top cannot be played pianissimo at
# all.
#
# The trims below are in semitones off each end of the playable range, and the
# dynamic rules say which end refuses which dynamic. Where an instrument has no
# entry the range is used unmodified rather than guessed at — an unknown
# instrument gets no false confidence.

_PRACTICAL_TRIM: dict[str, tuple[int, int]] = {
    # (semitones off the bottom, semitones off the top)
    "flute": (2, 4),          # the low octave is weak; the top is shrill and hard
    "piccolo": (3, 3),
    "alto_flute": (2, 4),
    "oboe": (2, 4),           # the lowest notes honk and cannot be played softly
    "english_horn": (2, 4),
    "clarinet": (0, 5),       # the chalumeau is fine; the top is effortful
    "bass_clarinet": (0, 5),
    "bassoon": (2, 5),
    "contrabassoon": (2, 5),
    "horn": (3, 4),           # the pedal register and the high register both
    "trumpet": (1, 4),
    "cornet": (1, 4),
    "piccolo_trumpet": (1, 3),
    "trombone": (2, 4),
    "bass_trombone": (2, 4),
    "tuba": (2, 4),
    "euphonium": (2, 4),
    "soprano_sax": (1, 3),
    "alto_sax": (1, 3),
    "tenor_sax": (1, 3),
    "baritone_sax": (1, 3),
    # Strings are far more forgiving; only the very top of each is awkward.
    "violin": (0, 7),
    "viola": (0, 7),
    "cello": (0, 7),
    "double_bass": (0, 7),
    # Voices: the extremes exist but are not sustainable.
    "soprano": (2, 2),
    "mezzo_soprano": (2, 2),
    "alto": (2, 2),
    "tenor": (2, 2),
    "baritone": (2, 2),
    "bass": (2, 2),
}

# Instruments that cannot play softly at the top of their range, and those that
# cannot play softly at the bottom. Asking for either produces a part that will
# simply come out louder than written, which then unbalances everything around
# it — a quiet orchestration that is not quiet.
_NO_SOFT_HIGH = {
    "trumpet", "cornet", "piccolo_trumpet", "horn", "trombone", "bass_trombone",
    "tuba", "euphonium", "oboe", "piccolo",
}
_NO_SOFT_LOW = {
    "flute", "alto_flute", "oboe", "english_horn", "bassoon", "contrabassoon",
    "soprano_sax", "alto_sax", "tenor_sax", "baritone_sax",
}
_SOFT_DYNAMICS = {"ppp", "pp", "p", "pppp"}
_LOUD_DYNAMICS = {"f", "ff", "fff", "ffff"}


def _canonical(instrument: str) -> str:
    return _RANGE_ALIASES.get(instrument.lower(), instrument.lower())


def _range_of(instrument: str) -> tuple[int, int]:
    """The full playable range — every note the instrument can produce."""
    return INSTRUMENT_RANGES.get(_canonical(instrument), (21, 108))


def practical_range(instrument: str, dynamic: str | None = None) -> tuple[int, int]:
    """The range this instrument sounds GOOD in, optionally at a given dynamic.

    Writing at the edge of the playable range is what makes an orchestration read
    as generated: the notes are legal and the part is miserable. At a soft
    dynamic the usable range narrows further, because several instruments
    physically cannot play quietly at one end or the other.
    """
    key = _canonical(instrument)
    lo, hi = INSTRUMENT_RANGES.get(key, (21, 108))
    trim_lo, trim_hi = _PRACTICAL_TRIM.get(key, (0, 0))
    lo, hi = lo + trim_lo, hi - trim_hi
    if dynamic and dynamic.lower() in _SOFT_DYNAMICS:
        # Another fourth off whichever end refuses to speak quietly.
        if key in _NO_SOFT_HIGH:
            hi -= 5
        if key in _NO_SOFT_LOW:
            lo += 5
    if lo >= hi:  # a trim that would invert the range is not a range
        return INSTRUMENT_RANGES.get(key, (21, 108))
    return lo, hi


def range_warnings(instrument: str, midis, dynamic: str | None = None):
    """Notes outside what this instrument does well, as readable lines.

    Advisory. Writing at an extreme is a legitimate effect — a shrieking piccolo
    at a climax is a choice — so this reports rather than clamps.
    """
    key = _canonical(instrument)
    full_lo, full_hi = _range_of(instrument)
    lo, hi = practical_range(instrument, dynamic)
    out = []
    for m in sorted({int(x) for x in midis}):
        if m < full_lo or m > full_hi:
            out.append(f"{instrument}: MIDI {m} is outside the instrument's range entirely")
        elif m < lo:
            reason = (
                "will not speak at this dynamic"
                if dynamic and key in _NO_SOFT_LOW and dynamic.lower() in _SOFT_DYNAMICS
                else "in the weak bottom of the range"
            )
            out.append(f"{instrument}: MIDI {m} {reason}")
        elif m > hi:
            reason = (
                "cannot be played softly"
                if dynamic and key in _NO_SOFT_HIGH and dynamic.lower() in _SOFT_DYNAMICS
                else "in the effortful top of the range"
            )
            out.append(f"{instrument}: MIDI {m} {reason}")
    return out


def _clamp_octave(midi: int, lo: int, hi: int) -> int:
    while midi < lo:
        midi += 12
    while midi > hi:
        midi -= 12
    return max(lo, min(hi, midi))


def _transpose_event_pitch(pitch, semitones: int, lo: int, hi: int, key: str):
    """Transpose a pitch (or chord list) and clamp into [lo, hi]."""

    def one(p):
        try:
            m = pitch_to_midi(p)
        except (ValueError, KeyError, TypeError):
            return None
        if m is None:
            return None
        return midi_to_pitch(_clamp_octave(m + semitones, lo, hi), key)

    if isinstance(pitch, list):
        out = [one(p) for p in pitch]
        out = [p for p in out if p]
        return out if len(out) > 1 else (out[0] if out else None)
    return one(pitch)


def _transpose_diatonic(pitch, semitones: int, lo: int, hi: int, key: str):
    """Transpose and snap into the KEY'S SCALE, then clamp.

    A doubling has to be diatonic. Transposing chromatically produces a parallel
    line in the wrong mode: a sixth below the melody in F major is A-flat, which
    is not in F major, and a second violin playing it against the first is simply
    a wrong note in every bar. Chromatic transposition is right for an OCTAVE
    doubling (where it cannot go wrong) and wrong for every other interval.
    """
    from .pitch import build_scale, is_minor_key, key_to_root_midi, snap_to_scale

    root = key_to_root_midi(key or "C")
    try:
        scale = build_scale(
            (root or 60) % 12 + 60, "minor" if is_minor_key(key or "C") else "major", octaves=8
        )
    except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
        scale = []

    def one(p):
        try:
            m = pitch_to_midi(p)
        except (ValueError, KeyError, TypeError):
            return None
        if m is None:
            return None
        moved = m + semitones
        if scale and semitones % 12 != 0:
            moved = snap_to_scale(moved, scale)
        return midi_to_pitch(_clamp_octave(moved, lo, hi), key)

    if isinstance(pitch, list):
        out = [one(p) for p in pitch]
        out = [p for p in out if p]
        return out if len(out) > 1 else (out[0] if out else None)
    return one(pitch)


def _top_midi(pitch):
    """Highest MIDI in a pitch or chord, or None."""
    names = pitch if isinstance(pitch, list) else [pitch]
    vals = []
    for n in names:
        try:
            m = pitch_to_midi(n)
        except (ValueError, KeyError, TypeError):
            continue
        if m is not None:
            vals.append(m)
    return max(vals) if vals else None


# Everything a LayerEvent carries that is not its position or its pitch. Derived
# from the dataclass rather than listed, so a field added to LayerEvent reaches
# the orchestral parts without anyone having to remember this function exists.
#
# The hand-written list this replaces carried seven fields and dropped six —
# `ornament`, `tie`, `hairpin`, `expression`, `technique`, `pedal`, `fingering`.
# The audible consequence was worse than a missing mark: an **appoggiatura**
# arrived in the orchestral score as a plain note, took real time instead of
# leaning on its principal, collided with the note it was decorating and left the
# bar summing to 3.5 beats of a 3/4. A dropped ornament is not a lost decoration;
# it is a wrong rhythm.
_EVENT_CARRIED_FIELDS = tuple(
    f
    for f in LayerEvent.__dataclass_fields__
    if f not in ("bar", "beat", "pitch", "source_layer", "role")
)


def _event_dict(e: LayerEvent, pitch=None) -> dict[str, Any]:
    """Serialize one event for an orchestral part, carrying every mark it has."""
    out: dict[str, Any] = {
        "bar": e.bar,
        "beat": e.beat,
        "pitch": pitch if pitch is not None else e.pitch,
    }
    for field in _EVENT_CARRIED_FIELDS:
        out[field] = getattr(e, field, None)
    # Provenance is useful downstream and harmless to carry.
    out["role"] = getattr(e, "role", None)
    return out


def _bar_dynamics(layer: LayerIR) -> dict[int, int]:
    """Per-bar loudness rank, carried forward from the last marking."""
    marks: dict[int, int] = {}
    events = sorted(
        (e for e in layer.principal_line + layer.bass_foundation if e.dynamic),
        key=lambda e: (e.bar, e.beat),
    )
    for e in events:
        marks[e.bar] = _DYN_RANK.get(e.dynamic, 4)
    out: dict[int, int] = {}
    current = 4  # mf default
    last_bar = max((e.bar for e in layer.principal_line + layer.bass_foundation), default=1)
    first_bar = min((e.bar for e in layer.principal_line + layer.bass_foundation), default=1)
    for bar in range(first_bar, last_bar + 1):
        if bar in marks:
            current = marks[bar]
        out[bar] = current
    return out


def _pick(preferences: list[str], ensemble: list[str], taken: set) -> str | None:
    lower = {i.lower(): i for i in ensemble}
    for pref in preferences:
        inst = lower.get(pref)
        if inst and inst not in taken:
            return inst
    for inst in ensemble:
        if inst not in taken:
            return inst
    return None


def plan_orchestration(
    layer: LayerIR,
    ensemble: list[str],
    key: str = "C",
    style_roles: dict[str, Any] | None = None,
) -> dict[str, list[dict]]:
    """Voice a piano-core LayerIR across an ensemble, idiomatically.

    ``style_roles`` (compiled_packs orchestration_roles.json, when
    populated) can override the lead/bass choice via entries like
    {"melody": "clarinet"}.
    """
    parts: dict[str, list[dict]] = {inst: [] for inst in ensemble}
    loudness = _bar_dynamics(layer)
    taken: set = set()
    style_roles = style_roles or {}

    # Legacy piano-core shape: whole LH lives in bass_foundation with no
    # response_layer. Split it — first event per bar anchors the bass,
    # the rest is inner motion — so the inner instruments have material.
    bass_events = list(layer.bass_foundation)
    response_events = list(layer.response_layer)
    bar_count = max(1, layer.bar_count)
    if not response_events and len(bass_events) > bar_count * 1.5:
        by_bar: dict[int, list[LayerEvent]] = defaultdict(list)
        for e in sorted(bass_events, key=lambda e: (e.bar, e.beat)):
            by_bar[e.bar].append(e)
        from dataclasses import replace as _replace


        capacity = float(bar_duration(tuple(layer.meter or (4, 4))))
        bass_events, response_events = [], []
        for bar, evs in sorted(by_bar.items()):
            sounding = [e for e in evs if e.pitch != "rest"]
            if sounding:
                # The anchor must SUSTAIN. Keeping its original value gave the
                # cello one quarter note followed by three beats of silence in a
                # bar where every other part is moving — the bass line of an
                # orchestral tutti reduced to isolated blips. Hold it until the
                # bar ends (the next anchor is the next downbeat), which is what
                # a bass instrument does under moving inner parts.
                anchor = sounding[0]
                span = max(0.0, capacity - float(anchor.beat) + 1.0)
                try:
                    held = _replace(anchor, duration=beats_to_dur(span))
                except Exception:
                    held = anchor
                bass_events.append(held)
                response_events.extend(sounding[1:])
            else:
                bass_events.extend(evs)
    layer = LayerIR(
        phrase_id=layer.phrase_id,
        instrumentation=layer.instrumentation,
        principal_line=layer.principal_line,
        bass_foundation=bass_events,
        response_layer=response_events,
        counter_reply=layer.counter_reply,
        ornamental_surface=layer.ornamental_surface,
        key=layer.key,
        meter=layer.meter,
        bar_count=layer.bar_count,
    )

    # ── Leads ──
    lead = (style_roles.get("melody") if style_roles.get("melody") in ensemble else None) or _pick(
        _MELODY_PREFERENCE, ensemble, taken
    )
    if lead:
        taken.add(lead)
    bass = (style_roles.get("bass") if style_roles.get("bass") in ensemble else None) or _pick(
        _BASS_PREFERENCE, ensemble, taken
    )
    if bass:
        taken.add(bass)

    lower_ens = {i.lower(): i for i in ensemble}
    flute = lower_ens.get("flute")
    oboe = lower_ens.get("oboe") if lower_ens.get("oboe") != lead else None
    clarinet = lower_ens.get("clarinet") if lower_ens.get("clarinet") != lead else None
    bassoon = lower_ens.get("bassoon") if lower_ens.get("bassoon") != bass else None
    horn = lower_ens.get("horn")
    violin_2 = lower_ens.get("violin_2")
    viola = lower_ens.get("viola")
    contrabass = lower_ens.get("contrabass") or lower_ens.get("double_bass")

    # ── Melody → lead, with doublings ──
    #
    # Parts are fitted to the PRACTICAL range, not the physical one. Clamping an
    # octave transfer to the outer limit of what an instrument can produce lands
    # notes in the weak bottom or the effortful top — legal, and miserable to
    # play. The trims are small (a tone or two at each end for winds, a fifth off
    # the top for strings) so nothing useful is lost.
    if lead:
        lo, hi = practical_range(lead)
        for e in layer.principal_line:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[lead].append(_event_dict(e, p))
        # Flute doubles 8va in loud bars (climaxes shine)
        if flute and flute != lead:
            # Practical, not physical: clamping a climax octave into the top of
            # the flute is how a brightening becomes a shriek. This module's own
            # range audit flags the result.
            flo, fhi = practical_range(flute, "f")
            for e in layer.principal_line:
                if e.pitch == "rest" or loudness.get(e.bar, 4) < 5:
                    continue
                p = _transpose_event_pitch(e.pitch, 12, flo, fhi, key)
                if p:
                    parts[flute].append(_event_dict(e, p))
        # Oboe doubles at unison in singing mid dynamics
        if oboe and oboe != lead:
            olo, ohi = practical_range(oboe, "f")
            for e in layer.principal_line:
                if e.pitch == "rest" or not (3 <= loudness.get(e.bar, 4) <= 4):
                    continue
                p = _transpose_event_pitch(e.pitch, 0, olo, ohi, key)
                if p:
                    parts[oboe].append(_event_dict(e, p))

    # ── Bass → cello-class, contrabass 8vb at mf+ ──
    if bass:
        lo, hi = practical_range(bass)
        for e in layer.bass_foundation:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[bass].append(_event_dict(e, p))
        if contrabass and contrabass != bass:
            clo, chi = practical_range(contrabass)
            for e in layer.bass_foundation:
                if e.pitch == "rest" or loudness.get(e.bar, 4) < 4:
                    continue
                p = _transpose_event_pitch(e.pitch, -12, clo, chi, key)
                if p:
                    parts[contrabass].append(_event_dict(e, p))

    # ── Inner motion → violin_2 / viola split by register ──
    inner_high = violin_2 or _pick(["violin_2", "viola", "clarinet"], ensemble, taken)
    inner_low = viola if viola and viola != inner_high else None
    # The inner STRINGS have the same nearly-empty hole the wind pads had: this
    # reads `response_layer` alone, so a core whose inner motion covers one bar
    # of fourteen leaves violin II and viola with one bar of material and
    # thirteen of silence. Where a bar carries no inner motion, they take the
    # harmony that bar implies from the outer texture — the same principle as
    # the pads below, and the same reason: a real orchestrator voices what the
    # bar implies rather than falling silent because one layer is thin.
    inner_events = list(layer.response_layer or [])
    _inner_bars = {e.bar for e in inner_events if e.pitch != "rest"}
    for e in layer.bass_foundation or []:
        if e.bar not in _inner_bars and e.pitch != "rest":
            inner_events.append(e)
    inner_events.sort(key=lambda e: (e.bar, float(e.beat)))
    for e in inner_events:
        if e.pitch == "rest":
            continue
        first = e.pitch[0] if isinstance(e.pitch, list) else e.pitch
        try:
            m = pitch_to_midi(first)
        except (ValueError, KeyError, TypeError):
            continue
        if m is None:
            continue
        target = inner_high if (m >= 60 or not inner_low) else inner_low
        if not target:
            continue
        lo, hi = practical_range(target)
        p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
        if p:
            parts[target].append(_event_dict(e, p))

    # ── Sustained wind/horn harmony ──
    #
    # Condensed from the inner motion when there is any, and from the WHOLE
    # texture when there is not. That fallback is the difference between an
    # orchestration and a distribution: a two-part piano core has empty
    # `response_layer` and `counter_reply`, so building pads only from those
    # left every wind with nothing to play. Measured on a real orchestrated
    # section: flute 0, horn 0, violin_2 0, clarinet 1, bassoon 1, viola 2
    # events against cello 60 and violin_1 47 — six of ten instruments
    # effectively tacet, in a score written for all ten.
    #
    # The harmony a two-part texture implies is perfectly playable; a real
    # orchestrator hears it and gives it to the winds. Nothing has to be
    # invented, only heard.
    pads = [i for i in (clarinet, bassoon, horn) if i and i not in (lead, bass)]
    if pads:
        # PER BAR, not all-or-nothing. The guard below used to be
        # `if not pad_source`, which fires only when the inner layers are
        # entirely empty. A core with a LITTLE inner motion — three events, all
        # in one bar of fourteen — is not empty, so the fallback never fired and
        # `by_bar` had a single key: clarinet, bassoon and viola each came out
        # with exactly ONE note in the whole section. Nearly-empty reached the
        # same tacet outcome as empty, through the guard rather than around it.
        #
        # Deciding per bar needs no coverage threshold either, which is the
        # better reason for it: a real orchestrator voices the harmony each bar
        # implies, from whichever line implies it. Measured on the section that
        # exposed this, pad coverage went from 1 bar of 14 to 14 of 14.
        by_bar: dict[int, list[int]] = defaultdict(list)
        inner_by_bar: dict[int, list[int]] = defaultdict(list)
        outer_by_bar: dict[int, list[int]] = defaultdict(list)

        def _collect(events, into):
            for e in events or []:
                if e.pitch == "rest":
                    continue
                for p in e.pitch if isinstance(e.pitch, list) else [e.pitch]:
                    try:
                        m = pitch_to_midi(p)
                    except (ValueError, KeyError, TypeError):
                        continue
                    if m is not None:
                        into[e.bar].append(m)

        _collect(layer.response_layer, inner_by_bar)
        _collect(layer.counter_reply, inner_by_bar)
        _collect(layer.principal_line, outer_by_bar)
        _collect(layer.bass_foundation, outer_by_bar)
        for bar in set(inner_by_bar) | set(outer_by_bar):
            by_bar[bar] = inner_by_bar.get(bar) or outer_by_bar.get(bar, [])
        # `bar_duration` is imported at the top and is the guarded form. This
        # inline version is the one that raised ZeroDivisionError on a
        # malformed meter — it was the root cause of twelve separate crashes.
        bpb = float(bar_duration(layer.meter or (4, 4)))
        pad_dur = beats_to_dur(bpb)
        pad_marked: dict[str, str] = {}

        def _pad_event(inst: str, bar: int, pitch: str, rank: int) -> dict[str, Any]:
            """One pad note, marked the way a part is marked: at entry, and on
            every change of dynamic thereafter — never re-stating the same mark
            bar after bar, which is what `score_realism.detect_notation_spam`
            exists to catch."""
            dyn = pad_dynamic(rank)
            written = dyn if pad_marked.get(inst) != dyn else None
            pad_marked[inst] = dyn
            return {
                "bar": bar,
                "beat": 1.0,
                "pitch": pitch,
                "duration": pad_dur,
                "dynamic": written,
                "articulation": None,
                "slur": None,
            }

        for bar, midis in sorted(by_bar.items()):
            # Horn pads loud bars; clarinet+bassoon pad soft/mid bars
            chord = sorted(set(midis))
            if not chord:
                continue
            if loudness.get(bar, 4) >= 5 and horn and horn in pads:
                lo, hi = practical_range(horn)
                p = midi_to_pitch(_clamp_octave(chord[len(chord) // 2], lo, hi), key)
                parts[horn].append(_pad_event(horn, bar, p, loudness.get(bar, 4)))
            else:
                for inst, idx in ((clarinet, -1), (bassoon, 0)):
                    if not inst:
                        continue
                    lo, hi = practical_range(inst)
                    p = midi_to_pitch(_clamp_octave(chord[idx], lo, hi), key)
                    parts[inst].append(
                        _pad_event(inst, bar, p, loudness.get(bar, 4))
                    )

    # ── Counter-melody → oboe (or viola) ──
    counter_inst = oboe or viola
    if counter_inst:
        lo, hi = practical_range(counter_inst)
        for e in layer.counter_reply:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[counter_inst].append(_event_dict(e, p))

    # ── Ornamental surface → flute when free, else stays with lead ──
    orn_inst = flute or lead
    if orn_inst:
        lo, hi = practical_range(orn_inst)
        for e in layer.ornamental_surface:
            if e.pitch == "rest":
                continue
            p = _transpose_event_pitch(e.pitch, 0, lo, hi, key)
            if p:
                parts[orn_inst].append(_event_dict(e, p))

    for inst in parts:
        parts[inst].sort(key=lambda d: (d["bar"], d["beat"]))
    # ── Idle instruments: doubling, not distribution ─────────────────────────
    #
    # Anything still empty is given a real orchestral job. A score for ten
    # instruments in which six of them are tacet is not an orchestration of the
    # material, it is a distribution of it — and a two-part piano core has only
    # two layers to distribute however many players are waiting.
    #
    # What a real orchestrator does instead is DOUBLE: the flute takes the
    # melody an octave up where the music is loud, the second violin sings a
    # third below the first, the horn sustains the root under everything. None
    # of that exists in the piano core to be assigned; it is added at
    # orchestration time, which is what orchestration means.
    _add_doublings(parts, layer, ensemble, lead, bass, key, loudness)
    _mark_part_dynamics(parts, loudness)
    _bow_string_parts(parts)
    return parts


# Strings, for the parts that need a bow rather than a breath.
# Substrings, so `violin_i`/`violin_ii` both match — but NOT a bare "bass",
# which matches `bassoon`, a double reed that has never been bowed.
_STRING_KEYS = ("violin", "viola", "cello", "contrabass", "double_bass", "string_bass")

# Slurs per 100 notes, measured per part over 82 real multi-part scores in the
# music21 core corpus — the RANGE, because a mean is not a bound:
#   violin  n=103  min  1.4  median 14.9  max 26.5
#   viola   n= 51  min  1.0  median 11.4  max 24.5
#   cello   n= 49  min  0.3  median  9.5  max 21.6
#
# Read these as a CEILING and nothing else. The sample counts only parts that
# carry at least one slur, so the minima are an artifact of that filter, not a
# floor: plenty of real parts have none. A large share of the multi-part scores
# in this corpus are Bach chorale transcriptions, which mark no slurs anywhere,
# and a chorale part at 0 is perfectly correct. What the numbers license is the
# upper bound below, not a claim that every part must be bowed.
_REAL_STRING_SLUR_RANGE = {"violin": (1.4, 26.5), "viola": (1.0, 24.5), "cello": (0.3, 21.6)}


def _bow_string_parts(parts: dict[str, list[dict]]) -> None:
    """Slur the string parts, because for a string player the slur IS the bowing.

    The parts built from the piano core's melody inherit its slurs and come out
    fine. The parts built from the **bass** inherit nothing, because a pianist's
    left hand is not phrased the way a cello is bowed — measured on a real
    orchestration off this system, cello 60 notes and 0 slurs, viola 0. Real
    orchestral strings that are bowed at all run a median 9.5-14.9 slurs per 100
    notes. (Not every real part is: Bach chorale transcriptions mark none, which
    is why this only ever ADDS bowing to a part that has none in a texture that
    calls for it, and never asserts a part must be slurred.)

    Bowing is added the way it is added on the stand: a slur over a **conjunct
    run inside one bar**, and a bow change wherever the line leaps, repeats a
    note, rests, or crosses a barline. Leaving leaps and repetitions separately
    bowed is what keeps the rate near the corpus instead of slurring everything
    in sight, and it is also simply how the passage is played.
    """
    for inst, events in parts.items():
        if not any(k in inst.lower() for k in _STRING_KEYS):
            continue
        ordered = sorted(
            (e for e in events if isinstance(e, dict)),
            key=lambda e: (e.get("bar", 0), e.get("beat", 0)),
        )
        if any(e.get("slur") for e in ordered):
            continue  # this part already carries the composer's own phrasing
        run: list[dict] = []

        def _close(run: list[dict]) -> None:
            # Three notes, not two. Slurring every stepwise pair put the rate at
            # 25 slurs per 100 notes against a real 9.6-13.7 — twice as bowed as
            # real music, which reads as fussy rather than as phrased.
            if len(run) < 3:
                return
            run[0]["slur"] = "start"
            run[-1]["slur"] = "stop"

        prev_midi = None
        prev_bar = None
        for ev in ordered:
            midi = _top_midi(ev.get("pitch"))
            step = (
                midi is not None
                and prev_midi is not None
                and 0 < abs(midi - prev_midi) <= 2
                and ev.get("bar") == prev_bar
            )
            if step:
                run.append(ev)
            else:
                _close(run)
                run = [ev] if midi is not None else []
            prev_midi, prev_bar = midi, ev.get("bar")
        _close(run)


def _mark_part_dynamics(parts: dict[str, list[dict]], loudness: dict[int, int]) -> None:
    """Give every part its own dynamics, the way a real part has them.

    Dynamics live on the piano core's melody layer, and each orchestral part
    inherits only the marks that were on the events it was built from. So the
    parts derived from the melody arrived marked and **everything else arrived
    blank**: measured on a real orchestration off this system, cello 60 notes /
    0 dynamics, violin I 48 / 0, violin II 48 / 0, viola and horn 0 of
    everything. It is the whole of the notation gap between a piano core (2.21
    marks per staff-bar) and its orchestration (0.63) — and it is not a
    stylistic weakness, it is a part a player cannot use. There is no orchestral
    part in the repertoire with no dynamic in it.

    Marks go in where a copyist puts them: at the part's entry, and on each
    change thereafter. Never bar after bar — `score_realism.detect_notation_spam`
    is the check that would (rightly) fire on that, and re-stating an unchanged
    dynamic is what makes a score look machine-set.
    """
    for events in parts.values():
        if not events:
            continue
        ordered = sorted(
            (e for e in events if isinstance(e, dict)),
            key=lambda e: (e.get("bar", 0), e.get("beat", 0)),
        )
        last: str | None = None
        for ev in ordered:
            if ev.get("dynamic"):
                last = ev["dynamic"]
                continue
            want = _RANK_DYN[max(0, min(len(_RANK_DYN) - 1, loudness.get(ev.get("bar", 1), 4)))]
            if want != last:
                ev["dynamic"] = want
                last = want


def _add_doublings(parts, layer, ensemble, lead, bass, key, loudness) -> None:
    """Give every silent instrument a musically sensible line.

    Each doubling is the standard one for that instrument, and each is applied
    only where it belongs: the flute octave at loud bars, the second violin
    under the melody throughout, the horn on the bass root where the harmony
    holds. Nothing is doubled into a range it cannot play.
    """
    melody = [e for e in layer.principal_line if e.pitch != "rest"]
    bassline = [e for e in layer.bass_foundation if e.pitch != "rest"]
    if not melody and not bassline:
        return

    def _empty(name):
        return name and name in parts and not parts[name]

    def _loud(bar) -> bool:
        return (loudness or {}).get(bar, 2) >= 3

    # 1. Flute (or piccolo) doubles the melody an octave up where it is loud —
    #    the standard brightening, and the one already used at climaxes.
    for name in ("flute", "piccolo", "alto_flute"):
        inst = _pick([name], ensemble, set())
        if not _empty(inst):
            continue
        lo, hi = practical_range(inst)
        for e in melody:
            if not _loud(e.bar):
                continue
            # Only double at the octave where the octave actually FITS. Clamping
            # it into the effortful top of the instrument is how a brightening
            # becomes a shriek, and this module's own range audit flags it.
            top = _top_midi(e.pitch)
            if top is None or not (lo <= top + 12 <= hi):
                continue
            p = _transpose_event_pitch(e.pitch, 12, lo, hi, key)
            if p:
                parts[inst].append(_event_dict(e, p))
        break

    # 2. Second violin sings a third below the first. A real third would need the
    #    harmony; a diatonic-sounding minor/major third alternation is wrong, so
    #    the interval is taken as a sixth below (an inverted third) which stays
    #    consonant against the melody far more often, then range-clamped.
    inst = _pick(["violin_2", "violin"], ensemble, {lead, bass})
    if _empty(inst):
        lo, hi = practical_range(inst)
        for e in melody:
            p = _transpose_diatonic(e.pitch, -9, lo, hi, key)
            if p:
                parts[inst].append(_event_dict(e, p))

    # 3. Horn sustains the bass's note under each bar — the pad that gives an
    #    orchestral texture its floor.
    inst = _pick(["horn", "trombone", "bassoon"], ensemble, {lead, bass})
    if _empty(inst) and bassline:
        lo, hi = practical_range(inst, "mp")
        # `bar_duration` is imported at the top and is the guarded form. This
        # inline version is the one that raised ZeroDivisionError on a
        # malformed meter — it was the root cause of twelve separate crashes.
        bpb = float(bar_duration(layer.meter or (4, 4)))
        held = beats_to_dur(bpb)
        seen = set()
        for e in sorted(bassline, key=lambda x: (x.bar, x.beat)):
            if e.bar in seen:
                continue
            seen.add(e.bar)
            p = _transpose_event_pitch(e.pitch, 12, lo, hi, key)
            if p:
                ev = _event_dict(e, p)
                ev["beat"] = 1.0
                ev["duration"] = held
                ev["articulation"] = None
                parts[inst].append(ev)

    # 4. Viola fills the middle by doubling the bass an octave up — the oldest
    #    filler in the orchestra and always idiomatic.
    inst = _pick(["viola", "cello"], ensemble, {lead, bass})
    if _empty(inst) and bassline:
        lo, hi = practical_range(inst)
        for e in bassline:
            p = _transpose_event_pitch(e.pitch, 12, lo, hi, key)
            if p:
                parts[inst].append(_event_dict(e, p))

    # 5. Anything still silent takes a part, quietly — better a real part than a
    #    tacet stave in a score that names it. But WHICH part depends on where
    #    the instrument lives.
    #
    #    This doubled the MELODY unconditionally. In a concerto tutti, where the
    #    piano core is octaves over a bass and there is little inner material,
    #    that left flute, oboe, clarinet, bassoon AND violin 1 all on the tune —
    #    five instruments in unison at 95-100% the same pitch classes — while
    #    violin 2 had 4 notes and the cello 8 across eight bars. A bassoon
    #    doubling a soprano melody is not a thin part, it is a wrong one.
    #
    #    A low instrument doubles the BASS instead, which is what step 4 already
    #    does for the viola and calls "the oldest filler in the orchestra".
    for inst, events in list(parts.items()):
        if events:
            continue
        lo, hi = practical_range(inst, "p")
        centre = (lo + hi) / 2
        # Below the melody's own centre of gravity, an instrument belongs under
        # the texture rather than on top of it.
        melody_midis = [
            m
            for e in melody
            for m in ([pitch_to_midi(x) for x in e.pitch] if isinstance(e.pitch, list)
                      else [pitch_to_midi(e.pitch)])
            if m is not None
        ]
        melody_centre = (sum(melody_midis) / len(melody_midis)) if melody_midis else 72
        source = melody if centre >= melody_centre - 7 else (bassline or melody)
        shift = 12 if source is bassline and centre > 55 else 0
        if not source:
            continue
        for e in source:
            p = _transpose_event_pitch(e.pitch, shift, lo, hi, key)
            if p:
                ev = _event_dict(e, p)
                ev["dynamic"] = None
                parts[inst].append(ev)


def audit_orchestration(parts: dict[str, list[dict]]) -> list[str]:
    """Range problems across a finished orchestration, as readable lines.

    Reads each part's own written dynamics, so the verdict accounts for the fact
    that a note comfortable at forte may be unplayable at pianissimo. Advisory
    throughout: writing at an extreme is a legitimate effect, and this exists so
    a reviewer can tell a deliberate one from an accident.
    """
    from .pitch import pitch_to_midi

    out: list[str] = []
    for instrument, events in (parts or {}).items():
        # Group the part's notes by the dynamic in force when they sound, since
        # that is what decides whether an extreme is reachable.
        in_force: str | None = None
        by_dynamic: dict[str | None, list[int]] = {}
        for e in events:
            if not isinstance(e, dict):
                continue
            if e.get("dynamic"):
                in_force = str(e["dynamic"])
            pitch = e.get("pitch")
            if not pitch or pitch == "rest":
                continue
            names = pitch if isinstance(pitch, list) else [pitch]
            for n in names:
                m = pitch_to_midi(n)
                if m is not None:
                    by_dynamic.setdefault(in_force, []).append(m)
        seen = set()
        for dynamic, midis in by_dynamic.items():
            for line in range_warnings(instrument, midis, dynamic=dynamic):
                if line not in seen:
                    seen.add(line)
                    out.append(line)
    return out
