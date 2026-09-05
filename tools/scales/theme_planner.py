"""Elect ONE principal theme and force its recurrence/development across sections.

Motifs were only ever realized if hand-placed in a sketch; nothing stated a
theme and brought it back, so pieces had no memorable through-line. This elects
the most theme-like motif at plan time and attaches motif placements to each
section-opening phrase (statement at expositions/A, fragment/sequence in
development, augmented restatement at the recap) — reusing the existing
MotifTransform algebra so the normal realization path then materializes them.
"""

from __future__ import annotations

from itertools import pairwise

from .models import MELODIC_LAYERS, MotifObject, MotifTransform, MotifTransformOp
from .pitch import midi_to_pitch

_DEV_ROLES = ("development", "contrasting", "episode")
_RECAP_ROLES = ("recap", "return", "reprise", "a2", "a_return", "coda")


def elect_principal_theme(motif_bank: dict[str, MotifObject]) -> str | None:
    """Pick the most theme-like motif: a real contour + recognition anchor +
    a non-trivial rhythm cell. Returns its id, or None for an empty bank."""
    if not motif_bank:
        return None

    def score(m: MotifObject) -> int:
        return (
            len(m.interval_contour or [])
            + len(m.rhythm_cell or [])
            + (3 if m.recognition_anchor else 0)
        )

    return max(motif_bank.values(), key=score).motif_id


def plan_section_opening_placements(role: str, theme_id: str) -> list[MotifTransform]:
    """MotifTransform(s) for a section's opening phrase, by section role:
    development → fragment, recap/coda → augment (transformed restatement),
    everything else → state (clear statement)."""
    r = (role or "").lower()
    if any(k in r for k in _RECAP_ROLES):
        op = MotifTransformOp.AUGMENT.value
    elif any(k in r for k in _DEV_ROLES):
        op = MotifTransformOp.FRAGMENT.value
    else:
        op = MotifTransformOp.STATE.value
    return [MotifTransform(operation=op, params={"motif_id": theme_id})]


# ─── Theme as REAL composed material (not an abstract contour) ────────────────

# Duration algebra for augmentation and diminution. The old tables were a
# 7-entry dict and its reverse, so a theme in triplets, 32nds, 64ths or
# double-dotted values came back UNCHANGED from "augment" — the transform
# silently did nothing and the brief told the agent it was an augmentation.
# Deriving both directions from the real duration values covers every code.
_DUR_HALVE: dict[str, str] = {}
_DUR_DOUBLE: dict[str, str] = {}


def _build_duration_tables() -> None:
    from .duration import DURATION_VALUES

    by_value: dict[object, str] = {}
    for code, val in DURATION_VALUES.items():
        # Prefer the canonical spelling over an alias ("s" over "16").
        if val not in by_value or len(code) < len(by_value[val]):
            by_value[val] = code
    for code, val in DURATION_VALUES.items():
        half = by_value.get(val / 2)
        if half:
            _DUR_HALVE[code] = half
        double = by_value.get(val * 2)
        if double:
            _DUR_DOUBLE[code] = double


_build_duration_tables()


def _ev_top_midi(ev) -> int | None:
    """Top MIDI of a LayerEvent pitch (note name or chord-name list)."""
    import music21
    p = ev.pitch
    names = p if isinstance(p, list) else [p]
    mids = []
    for n in names:
        if n and n != "rest":
            try:
                mids.append(music21.pitch.Pitch(n).midi)
            except Exception:
                pass
    return max(mids) if mids else None


def _melody_of(source) -> list:
    """The melodic line of a phrase, whatever forces it is scored for.

    Every read in this module was `principal_line`, which orchestral music
    never populates — its tune is in `foreground` — so theme capture,
    recurrence and `phrase_carries_theme` reported "no theme" for every
    orchestral piece, indistinguishable from a piece that genuinely has none.

    `LayerIR.melody_line()` already did exactly this and already carried the
    explanation; this only adds the two shapes it cannot take. Delegating
    rather than reimplementing is the point — a private fifth copy of a model
    method is how the divergence starts.
    """
    if source is None:
        return []
    # A bare sequence of events IS the line. `_midis_of` passes one, and an
    # earlier version of this helper returned [] for it rather than passing it
    # through — the caller distinguished None from empty, so every
    # list-of-events call silently measured nothing.
    if isinstance(source, (list, tuple)):
        return list(source)
    if isinstance(source, dict):
        for name in MELODIC_LAYERS:
            evs = source.get(name)
            if evs:
                return list(evs)
        return []
    line = getattr(source, "melody_line", None)
    if callable(line):
        return line()
    for name in MELODIC_LAYERS:
        evs = getattr(source, name, None)
        if evs:
            return list(evs)
    return []


def capture_theme_surface(graph, phrase_id: str, n_bars: int = 4):
    """Store the COMPOSED theme (the principal_line of the first n_bars of the
    committed theme phrase) on the graph, so later sections DEVELOP the real
    melody the agent wrote — not re-invent it. Returns the captured LayerIR or
    None."""
    from .models import LayerEvent, LayerIR

    st = graph.phrases.get(phrase_id)
    if not st or not getattr(st, "realized", None):
        return None
    real = st.realized
    _src = _melody_of(real)
    bars = sorted({e.bar for e in _src})[:n_bars]
    theme = LayerIR(phrase_id=f"{phrase_id}__theme", key=real.key, meter=real.meter,
                    instrumentation=real.instrumentation, bar_count=len(bars))
    base = bars[0] if bars else 1
    for e in sorted(_src, key=lambda x: (x.bar, x.beat)):
        if e.bar in bars:
            theme.principal_line.append(
                LayerEvent(bar=e.bar - base + 1, beat=e.beat, pitch=e.pitch,
                           duration=e.duration, role=e.role, source_layer="principal_line")
            )
    graph.principal_theme_surface = theme
    # ``principal_theme_id`` names a MOTIF in ``motif_bank`` — that is what
    # ``elect_principal_theme`` puts there and what the brief looks up. Writing
    # a phrase id into the same field made one field carry two incompatible
    # kinds of name, which is this repo's most reliable bug generator:
    #
    #   * after election it held "motif_A"        → the brief's
    #     "is this phrase the theme's own phrase" test compared a motif id to a
    #     phrase id and was **permanently False**;
    #   * after a capture it held "m1_a_p1__theme" → the brief's motif lookup
    #     found nothing in the bank and **silently fell back to motifs[0]**,
    #     showing the agent a motif that was never elected.
    #
    # So the capture records the SOURCE PHRASE separately, and only fills the
    # motif id if nothing has elected one — never overwriting an election.
    graph.principal_theme_phrase_id = phrase_id
    if not getattr(graph, "principal_theme_id", ""):
        graph.principal_theme_id = elect_principal_theme(getattr(graph, "motif_bank", {}) or {}) or ""
    return theme


def principal_theme_phrase(graph) -> str:
    """The phrase the principal theme was captured FROM, or "".

    Resolves whichever convention a graph happens to carry, including graphs
    saved while ``principal_theme_id`` held a phrase id with a ``__theme``
    suffix. Callers asking "does this phrase carry the theme?" should compare
    against this, never against ``principal_theme_id``.
    """
    explicit = getattr(graph, "principal_theme_phrase_id", "") or ""
    if explicit:
        return explicit
    surface = getattr(graph, "principal_theme_surface", None)
    pid = getattr(surface, "phrase_id", "") if surface is not None else ""
    if pid.endswith("__theme"):
        return pid[: -len("__theme")]
    if pid:
        return pid
    legacy = getattr(graph, "principal_theme_id", "") or ""
    if legacy.endswith("__theme"):
        return legacy[: -len("__theme")]
    return ""


def phrase_carries_theme(graph, phrase_id: str) -> bool:
    """Whether ``phrase_id`` is the phrase the principal theme was taken from."""
    return bool(phrase_id) and principal_theme_phrase(graph) == phrase_id


def _theme_span_beats(theme) -> float:
    """Beats the theme occupies, from its own bars and meter."""
    from .duration import dur_to_beats

    evs = _melody_of(theme)
    if not evs:
        return 0.0
    meter = tuple(getattr(theme, "meter", (4, 4)) or (4, 4))
    from .duration import beats_per_bar

    bpb = beats_per_bar(meter)
    bars = {int(getattr(e, "bar", 1)) for e in evs}
    span = len(bars) * bpb
    written = 0.0
    for e in evs:
        try:
            written += float(dur_to_beats(getattr(e, "duration", "q")))
        except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
            continue
    return max(span, written)


def _fit_to_span(mids, durs, span_beats: float):
    """Drop trailing notes that would run past ``span_beats``."""
    from .duration import dur_to_beats

    if span_beats <= 0:
        return mids, durs
    out_m, out_d, total = [], [], 0.0
    # STRICT: `mids` and `durs` are the same theme, split into two lists and
    # transformed in parallel. If a transform ever trims one and not the
    # other, zip's default would silently shorten the theme instead of
    # failing — a whole phrase quietly missing from a developed theme.
    for m, d in zip(mids, durs, strict=True):
        try:
            b = float(dur_to_beats(d))
        except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
            b = 1.0
        if total + b > span_beats + 1e-6:
            break
        out_m.append(m)
        out_d.append(d)
        total += b
    return (out_m, out_d) if out_m else (mids[:1], durs[:1])


def develop_theme_surface(theme, op: str, transpose_semitones: int = 0) -> str:
    """Render a SUGGESTED development of the real theme melody as shorthand, for
    the brief. The agent treats it as a starting point to develop creatively, not
    a verbatim output. op ∈ state/sequence/fragment/invert/augment/retrograde."""
    if theme is None or not _melody_of(theme):
        return ""
    evs = sorted(_melody_of(theme), key=lambda x: (x.bar, x.beat))
    notes = [(_ev_top_midi(e), e.duration) for e in evs]
    notes = [(m, d) for m, d in notes if m is not None]
    if not notes:
        return ""
    op_l = (op or "state").lower()
    mids = [m for m, _ in notes]
    durs = [d for _, d in notes]

    if op_l == "fragment":
        k = max(1, len(notes) // 2)
        mids, durs = mids[:k], durs[:k]
    elif op_l == "retrograde":
        mids, durs = list(reversed(mids)), list(reversed(durs))
    elif op_l == "invert":
        head = mids[0]
        mids = [head - (m - head) for m in mids]
    elif op_l == "augment":
        durs = [_DUR_DOUBLE.get(d, d) for d in durs]
        # Augmentation doubles the theme's LENGTH, so the same number of notes
        # no longer fits the same number of bars. Handing the agent a suggestion
        # that overflows its own phrase is worse than handing it nothing: it
        # either gets truncated at the barline or pushes the phrase out of shape.
        # Trim to what the theme's own span can hold.
        mids, durs = _fit_to_span(mids, durs, _theme_span_beats(theme))
    elif op_l == "diminish":
        durs = [_DUR_HALVE.get(d, d) for d in durs]
    # sequence/state: pitch handled by transpose below

    mids = [m + transpose_semitones for m in mids]

    # Spell in the theme's own key. Spelling everything with flats turned a
    # theme in E major into E-Gb-Ab — wrong accidentals, and a wrong harmonic
    # reading of the agent's own principal theme every time it was developed.
    key = getattr(theme, "key", None) or "C"
    return " ".join(
        f"{midi_to_pitch(m, key)}{d}" for m, d in zip(mids, durs, strict=True)
    )


# ─── Is it actually a theme? ─────────────────────────────────────────────────
#
# The system elects a "principal theme" by counting how many entries its motif
# object has, which measures how much data was written down, not whether the
# tune is memorable. Nothing ever asked whether the elected theme has the
# properties that make a melody stick: a distinctive rhythm, a shape with a
# clear high point, a singable range, and an interval profile that is neither a
# scale nor an arpeggio.
#
# These are descriptive. A great theme can break any of them (the Fifth
# Symphony's is four notes and three of them are the same pitch), so nothing
# here blocks — it exists so a reviewer can be told "this is a scale, not a
# tune", which is the commonest failure of generated melody and the one nobody
# was measuring.


def analyze_theme(theme) -> dict[str, object]:
    """Memorability properties of a captured theme surface.

    Returns measurements plus plain-language observations. ``None`` fields mean
    the theme was too short to say.
    """
    from .duration import dur_to_beats

    evs = sorted(
        (e for e in _melody_of(theme)
         if getattr(e, "pitch", None) and e.pitch != "rest"),
        key=lambda e: (getattr(e, "bar", 1), getattr(e, "beat", 1.0)),
    )
    out: dict[str, object] = {
        "notes": len(evs),
        "observations": [],
        "concerns": [],
    }
    if len(evs) < 3:
        out["observations"].append("too short to analyze")
        return out

    mids = [m for m in (_ev_top_midi(e) for e in evs) if m is not None]
    if len(mids) < 3:
        out["observations"].append("no readable pitches")
        return out

    durs = []
    for e in evs:
        try:
            durs.append(float(dur_to_beats(getattr(e, "duration", "q"))))
        except (ValueError, KeyError, TypeError):  # pragma: no cover - defensive
            durs.append(1.0)

    intervals = [b - a for a, b in pairwise(mids)]
    steps = sum(1 for i in intervals if 0 < abs(i) <= 2)
    leaps = sum(1 for i in intervals if abs(i) > 2)
    repeats = sum(1 for i in intervals if i == 0)
    n_iv = max(1, len(intervals))

    out["range_semitones"] = max(mids) - min(mids)
    out["step_ratio"] = round(steps / n_iv, 3)
    out["leap_ratio"] = round(leaps / n_iv, 3)
    out["repeat_ratio"] = round(repeats / n_iv, 3)
    out["distinct_durations"] = len(set(durs))
    out["peak_position"] = round(mids.index(max(mids)) / (len(mids) - 1), 3)
    # A theme whose every interval points the same way is a scale or an
    # arpeggio, not a shape.
    dirs = [(1 if i > 0 else -1) for i in intervals if i != 0]
    changes = sum(1 for a, b in pairwise(dirs) if a != b)
    out["direction_changes"] = changes

    # Longest run of consecutive same-direction steps: 5+ is a scale passage.
    run = best = 1
    for a, b in pairwise(dirs):
        run = run + 1 if a == b else 1
        best = max(best, run)
    out["longest_scalar_run"] = best

    obs, concerns = out["observations"], out["concerns"]
    obs.append(
        f"{len(mids)} notes spanning {out['range_semitones']} semitones, "
        f"{out['step_ratio']:.0%} steps / {out['leap_ratio']:.0%} leaps, "
        f"peak {out['peak_position']:.0%} of the way through"
    )

    if out["distinct_durations"] < 2:
        concerns.append(
            "every note is the same length — a theme is remembered by its rhythm "
            "at least as much as its pitches, and an undifferentiated stream has "
            "no rhythmic identity to remember"
        )
    if best >= 5:
        concerns.append(
            f"{best} consecutive steps in one direction — this is a scale passage, "
            f"not a shape a listener can hold on to"
        )
    if changes == 0:
        concerns.append("the line never changes direction; it has no arch")
    if out["range_semitones"] < 4:
        concerns.append(
            f"the whole theme sits inside {out['range_semitones']} semitones — "
            f"too narrow to have a profile"
        )
    if out["range_semitones"] > 24:
        concerns.append(
            f"{out['range_semitones']} semitones is beyond what a listener hears as "
            f"one melodic line"
        )
    if out["leap_ratio"] > 0.7:
        concerns.append(
            "almost every move is a leap — this outlines a chord rather than "
            "singing a tune"
        )
    if out["repeat_ratio"] > 0.6:
        concerns.append("most of the theme is one repeated pitch")
    if not concerns:
        obs.append("has a distinct rhythm, a clear shape and a singable range")
    return out


# ─── Thematic return: what can and cannot be measured ────────────────────────
#
# GROUND TRUTH TEST, and it is a negative result worth recording in full.
#
# Mozart K.331/i is a theme with six variations, and this corpus stores each
# variation as its own file — so there are six pieces of material that
# *provably* contain the theme. Searching for the theme's head in them:
#
#   matcher                     variations found   unrelated movements matched
#   contour + rhythm, head 3-6        0 / 6                  0 / 6
#   contour only, head 3              6 / 6                  5 / 6
#   contour only, head 4              4 / 6                  2 / 6
#   contour only, head 5-6            0 / 6                  0 / 6
#
# Requiring rhythm guarantees failure, because rhythm is exactly what a
# variation changes. Dropping to a three-interval contour finds every variation
# and also matches five of six unrelated Chopin mazurkas — a three-note shape is
# not distinctive in tonal music. There is **no operating point with both
# sensitivity and specificity**.
#
# So this function reports a LOWER BOUND, not a fact. It cannot distinguish "the
# theme never returns" from "the theme returns in a form I cannot see", and a
# caller that presents its output as the former is overstating it. `head=4` is
# used as the least-bad setting, with the measured error rates carried in the
# result so nobody has to rediscover them.
#
# The reliable version of this question is not textual matching at all: ask the
# PLAN how many sections were given a placement of the principal theme. That is
# exact. `planned_theme_placements` does it, and `theme_return_evidence`
# prefers it whenever the plan carries placements.
_HEAD_INTERVALS = 4

# Measured on the ground-truth test above, at head=4.
_RECURRENCE_RECALL = 0.67
_RECURRENCE_FALSE_RATE = 0.33


def planned_theme_placements(graph) -> dict[str, object]:
    """Sections whose plan places the principal theme. Exact, not inferred.

    Reads `slot.motif_transforms`, which is where the planner records that a
    phrase restates or develops the elected theme. Unlike contour matching this
    cannot be wrong — it is what the plan says — though it says nothing about
    whether the composer honoured it.
    """
    principal = getattr(graph, "principal_theme_id", "") or ""
    sections: dict[str, list[str]] = {}
    for pid, state in (getattr(graph, "phrases", None) or {}).items():
        slot = getattr(state, "slot", None)
        transforms = getattr(slot, "motif_transforms", None) or []
        for mt in transforms:
            params = getattr(mt, "params", None) or (
                mt.get("params") if isinstance(mt, dict) else {}
            )
            mid = (params or {}).get("motif_id", "")
            if principal and mid and mid != principal:
                continue
            op = getattr(mt, "operation", None) or (
                mt.get("operation") if isinstance(mt, dict) else ""
            )
            section = getattr(slot, "section_id", "") or pid.rsplit("_p", 1)[0]
            sections.setdefault(section, []).append(str(op or "state"))
    return {
        "sections": sorted(sections),
        "placements": sections,
        "count": len(sections),
    }


def theme_return_evidence(graph, theme_surface) -> dict[str, object]:
    """Does the theme come back? Answered from the plan when possible.

    Returns ``source`` = "plan" when the planner recorded placements (exact) or
    "contour" when it fell back to matching (a lower bound with a measured
    two-thirds recall). The distinction matters: a caller must not report a
    contour miss as "the theme never returns".
    """
    planned = planned_theme_placements(graph)
    if planned["count"]:
        return {
            "source": "plan",
            "sections": planned["sections"],
            "count": planned["count"],
            "reliable": True,
            "placements": planned["placements"],
        }
    matched = theme_recurrence(graph, theme_surface)
    return {
        "source": "contour",
        "sections": matched["sections"],
        "count": len(matched["recurrences"]),
        "reliable": False,
        "recall": _RECURRENCE_RECALL,
        "false_rate": _RECURRENCE_FALSE_RATE,
    }


def theme_recurrence(
    graph, theme_surface, tolerance: int = 1, head: int = _HEAD_INTERVALS
) -> dict[str, object]:
    """Where the principal theme's shape comes back across the piece.

    Matching is on the INTERVAL contour of the theme's HEAD, not on absolute
    pitch and not on the whole theme. Contour rather than pitch means a
    transposed, re-harmonised or differently-registered return still counts;
    the head rather than the whole means a return that continues differently —
    which is most of them — still counts too.

    **This is a lower bound.** Measured against six Mozart variations that
    provably contain their theme, this setting finds four of them and also
    matches unrelated material a third of the time. A miss here does NOT mean
    the theme never returns. Prefer `theme_return_evidence`, which uses the
    plan's own placements when there are any.
    """
    full = _contour_of(theme_surface)
    target = full[:head] if len(full) > head else full
    hits: list[dict[str, object]] = []
    if len(target) < 3:
        return {
            "theme_length": len(full),
            "head_length": len(target),
            "recurrences": hits,
            "sections": [],
        }

    for phrase_id, state in (getattr(graph, "phrases", None) or {}).items():
        realized = getattr(state, "realized", None)
        if realized is None:
            continue
        line = _melody_of(realized)
        if not line:
            continue
        mids = _midis_of(line)
        bars = [
            (e.get("bar") if isinstance(e, dict) else getattr(e, "bar", 1)) for e in line
        ]
        contour = [b - a for a, b in pairwise(mids)]
        for i in range(len(contour) - len(target) + 1):
            window = contour[i : i + len(target)]
            if all(abs(a - b) <= tolerance for a, b in zip(window, target, strict=False)):
                hits.append(
                    {
                        "phrase_id": phrase_id,
                        "bar": bars[i] if i < len(bars) else None,
                        "exact": window == target,
                    }
                )
                break  # one hit per phrase is enough to say "it returns here"
    return {
        "theme_length": len(full),
        "head_length": len(target),
        "recurrences": hits,
        "sections": sorted({str(h["phrase_id"]).rsplit("_p", 1)[0] for h in hits}),
    }


def _midis_of(source) -> list[int]:
    """Top MIDI per note from a shorthand string, a LayerIR, or an event list.

    Accepting only a shorthand string forced every caller to re-serialize its
    material first, and a caller that got that wrong — printing a chord as
    ``['A5', 'F5']`` — silently produced an empty contour and reported that the
    theme never recurs. Taking the material directly removes the round-trip.
    """
    from .pitch import pitch_to_midi

    def _top(pitch):
        if not pitch or pitch == "rest":
            return None
        names = pitch if isinstance(pitch, list) else [pitch]
        vals = [v for v in (pitch_to_midi(n) for n in names) if v is not None]
        return max(vals) if vals else None

    if isinstance(source, str):
        from .direct_compose import _parse_shorthand

        return [m for m in (_top(ev.get("pitch")) for ev in _parse_shorthand(source)) if m is not None]

    events = _melody_of(source)
    if events is None:
        events = source if isinstance(source, (list, tuple)) else []
    out = []
    for e in events:
        pitch = e.get("pitch") if isinstance(e, dict) else getattr(e, "pitch", None)
        m = _top(pitch)
        if m is not None:
            out.append(m)
    return out


def _contour_of(source) -> list[int]:
    """Interval contour of a melody, given in any of the accepted forms."""
    mids = _midis_of(source)
    return [b - a for a, b in pairwise(mids)]
