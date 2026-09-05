"""
One musical report, written for a person to read.

Analysis that nobody reads changes nothing. The fresh-ears critic drives every
artistic revision in this system, and until now it received the ``self_evaluate``
discriminator report — z-scores and corpus distances — plus the score itself.
Meanwhile the questions a musician would actually ask on opening a score had no
answers anywhere: does the theme ever come back? are all the cadences the same?
does the texture ever change? is anything on the page for the player to
interpret? are there parallel octaves between the melody and the bass?

This module asks those questions across a whole piece and answers them in
sentences. It aggregates:

* ``counterpoint``     — part-writing in the real texture
* ``voicing``          — texture, register, and where it holds and changes
* ``cadence_analysis`` — what actually closes each phrase, and how varied
* ``theme_planner``    — whether the principal theme returns
* ``expression_enricher`` / ``ornament_realization`` — is the page engraved

Two rules govern what comes out:

**Prose, not z-scores.** This project has already learned that handing a
composer a z-score turns composition into metric whack-a-mole, and that
optimizing one dimension breaks another. Every line here names a musical fact
("the theme never returns after bar 16"), not a distance from a distribution.

**Nothing here is a verdict.** The report says what is true of the score. The
critic decides what matters. A deliberately static texture, a piece that ends
on a half cadence, an unaccompanied line — all legitimate, all reported, none
condemned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import LayerIR

# ─── Report ──────────────────────────────────────────────────────────────────


@dataclass
class MusicalReport:
    piece_id: str = ""
    bars: int = 0
    phrases: int = 0

    theme: dict[str, Any] = field(default_factory=dict)
    cadences: dict[str, Any] = field(default_factory=dict)
    texture: dict[str, Any] = field(default_factory=dict)
    part_writing: dict[str, Any] = field(default_factory=dict)
    page: dict[str, Any] = field(default_factory=dict)
    craft: dict[str, Any] = field(default_factory=dict)
    orchestration: dict[str, Any] = field(default_factory=dict)
    continuity: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "bars": self.bars,
            "phrases": self.phrases,
            "theme": self.theme,
            "cadences": self.cadences,
            "texture": self.texture,
            "part_writing": self.part_writing,
            "page": self.page,
            "craft": self.craft,
            "orchestration": self.orchestration,
            "continuity": self.continuity,
        }


# ─── Loading ─────────────────────────────────────────────────────────────────


def _phrase_layer(phrase_state, slot: dict[str, Any]):
    """Rebuild a LayerIR from a phrase's realized material.

    Accepts the dict form (a loaded PieceGraph) and the object form
    interchangeably, because callers have both and getting it wrong produces an
    empty analysis that looks like a clean bill of health.
    """
    from .models import LayerEvent, LayerIR

    realized = getattr(phrase_state, "realized", None)
    if realized is None and isinstance(phrase_state, dict):
        realized = phrase_state.get("realized")
    if not realized:
        return None

    meter = slot.get("meter") or [4, 4]
    ir = LayerIR(
        phrase_id=str(slot.get("phrase_id", "")),
        key=str(slot.get("key", "C") or "C"),
        meter=(int(meter[0]), int(meter[1])),
    )
    for name in _CARRIED:
        val = (
            realized.get(name) if isinstance(realized, dict) else getattr(realized, name, None)
        )
        if val:
            setattr(ir, name, val)
    fields = LayerEvent.__dataclass_fields__
    for name in _LAYER_NAMES:
        src = (
            realized.get(name)
            if isinstance(realized, dict)
            else getattr(realized, name, None)
        ) or []
        if not src:
            continue
        target = ir.ensure_layer(name)
        for n in src:
            if isinstance(n, dict):
                target.append(LayerEvent(**{k: v for k, v in n.items() if k in fields}))
            else:
                target.append(n)
    inner = (
        realized.get("inner_voices")
        if isinstance(realized, dict)
        else getattr(realized, "inner_voices", None)
    ) or {}
    for vname, evs in inner.items():
        ir.inner_voices[vname] = [
            LayerEvent(**{k: v for k, v in n.items() if k in fields})
            if isinstance(n, dict)
            else n
            for n in evs
        ]
    ir.bar_count = _count_bars(ir)
    return ir


def _slot_of(phrase_state) -> dict[str, Any]:
    slot = getattr(phrase_state, "slot", None)
    if slot is None and isinstance(phrase_state, dict):
        slot = phrase_state.get("slot")
    if slot is None:
        return {}
    if isinstance(slot, dict):
        return slot
    return {
        k: getattr(slot, k, None)
        for k in (
            "phrase_id",
            "section_id",
            "bar_start",
            "bar_count",
            "key",
            "meter",
            "cadence_bar",
            "cadence_target",
            "harmony_plan",
        )
    }


def _ordered_phrases(graph) -> list[tuple[str, Any, dict[str, Any]]]:
    phrases = getattr(graph, "phrases", None) or {}
    rows = []
    for pid, state in phrases.items():
        slot = _slot_of(state)
        slot.setdefault("phrase_id", pid)
        rows.append((pid, state, slot))
    rows.sort(key=lambda r: (r[2].get("bar_start") or 0, r[0]))
    return rows


def _merge(layers):
    """One LayerIR for the whole piece, for measurements that need the arc."""
    from .models import LayerIR

    if not layers:
        return None
    merged = LayerIR(
        phrase_id="whole",
        key=layers[0].key,
        meter=layers[0].meter,
    )
    for name in _CARRIED:
        for ir in layers:
            if getattr(ir, name, None):
                setattr(merged, name, getattr(ir, name))
                break
    for ir in layers:
        for name in _LAYER_NAMES:
            src = getattr(ir, name, None)
            if not src:
                continue
            merged.ensure_layer(name).extend(src)
        for vname, evs in (ir.inner_voices or {}).items():
            merged.inner_voices.setdefault(vname, []).extend(evs)
    merged.bar_count = _count_bars(merged)
    return merged


# The layer names, derived from the model rather than typed out. Three separate
# hand-written lists here carried only the five PIANO layers, so an orchestral
# piece reached the critic as an EMPTY report: the six orchestral layers were
# dropped, `bar_count` was computed from an empty `principal_line` (giving 1),
# and `instrumentation` was never carried, so the ensemble texture floors could
# not fire on the production path at all. Deriving the names means a new layer
# joins every reader at once.
_LAYER_NAMES: tuple[str, ...] = tuple(LayerIR.event_layer_names())
_CARRIED: tuple[str, ...] = ("instrumentation", "pickup_beats")


def _all_events(ir) -> list:
    """Every sounding event in a LayerIR, whatever its instrumentation.

    `LayerIR.all_events()` already covers all eleven layers and the inner
    voices; this is a thin alias so the merge reads the same as the readers.
    """
    return ir.all_events()


def _count_bars(ir) -> int:
    return len({e.bar for e in _all_events(ir)}) or 1


# ─── Sections of the report ──────────────────────────────────────────────────


def _theme_section(graph, layers, rows) -> dict[str, Any]:
    from .theme_planner import analyze_theme

    out: dict[str, Any] = {"observations": [], "concerns": []}
    surface = getattr(graph, "principal_theme_surface", None)
    if not surface:
        out["observations"].append(
            "No principal theme was captured, so there is nothing for the piece to "
            "bring back. A piece without a stated theme has no memory: every phrase "
            "is new, and nothing the listener heard earlier pays off later."
        )
        return out

    theme_ir = _phrase_layer({"realized": surface}, {"key": getattr(graph, "key", "C")})
    if theme_ir is None:
        return out
    analysis = analyze_theme(theme_ir)
    out["analysis"] = analysis
    out["observations"].extend(analysis.get("observations", []))
    out["concerns"].extend(analysis.get("concerns", []))

    from .theme_planner import theme_return_evidence

    evidence = theme_return_evidence(graph, theme_ir)
    out["recurrences"] = evidence["count"]
    out["sections"] = evidence["sections"]
    out["evidence_source"] = evidence["source"]
    n = evidence["count"]

    if evidence["source"] == "plan":
        # Exact: the plan says which sections carry the theme.
        if n <= 1:
            out["concerns"].append(
                f"The plan places the principal theme in {n} section"
                f"{'s' if n != 1 else ''}. A theme that is stated and never "
                f"brought back is not a theme, it is an opening — restating it "
                f"transposed, re-harmonised, fragmented or in the bass is what "
                f"makes a piece cohere."
            )
        else:
            out["observations"].append(
                f"the plan brings the theme back in {n} sections "
                f"({', '.join(evidence['sections'])})"
            )
        return out

    # Contour matching only — a LOWER BOUND, and it must be reported as one.
    # Measured against six Mozart variations that provably contain their theme,
    # this finds four and matches unrelated material a third of the time. Saying
    # "the theme never returns" on the strength of a miss would be overstating a
    # measurement that cannot support it.
    if n <= 1:
        out["observations"].append(
            f"The theme's opening shape was found in {n} place"
            f"{'s' if n != 1 else ''} by contour matching — which finds only "
            f"about two thirds of real returns, so this is a floor rather than "
            f"a count. Worth checking by ear whether the theme comes back at "
            f"all; if it does not, that is the piece's largest structural gap."
        )
    else:
        out["observations"].append(
            f"the theme's shape recurs in at least {n} places "
            f"({', '.join(evidence['sections'])})"
        )
    return out


def _cadence_section(rows, layers) -> dict[str, Any]:
    from .cadence_analysis import analyze_cadences, cadence_summary_lines

    specs = []
    # STRICT: one LayerIR per kept phrase, built together in `build_report`.
    # A mismatch would drop phrases off the end of the report silently, so a
    # piece would be reviewed as if it were shorter than it is.
    for (_pid, _state, slot), ir in zip(rows, layers, strict=True):
        specs.append((ir, slot.get("cadence_bar"), slot.get("key"), slot.get("cadence_target")))
    rep = analyze_cadences(specs)
    return {
        "lines": cadence_summary_lines(rep, limit=16),
        "variety": round(rep.variety, 3),
        "repeated_formulas": rep.repeated_formulas,
        "observations": rep.observations,
        "concerns": rep.suggestions,
    }


def _continuity_section(kept, layers) -> dict[str, Any]:
    """Whether each phrase continues from the last, or restarts.

    Reports where each phrase's melody came to rest and any dissonance it left
    hanging, then checks whether the next phrase picked either up. Nothing has
    ever carried these across a phrase boundary: `ContinuationContext` declares
    the fields and no code writes or reads them, and the live continuity context
    reports the melody's recent RANGE but never its ENDPOINT — a different
    question, and the one a composer asks first.
    """
    from .counterpoint import continuation_hint, phrase_tail
    from .pitch import pitch_to_midi

    out: dict[str, Any] = {"observations": [], "concerns": [], "tails": {}}
    if len(layers) < 2:
        return out

    tails = []
    for (pid, _state, slot), ir in zip(kept, layers, strict=True):
        tail = phrase_tail(ir, key=slot.get("key"))
        tails.append((pid, tail))
        hint = continuation_hint(tail)
        if hint:
            out["tails"][pid] = hint

    unresolved = [pid for pid, t in tails[:-1] if t.get("pending_resolution")]
    if unresolved:
        out["concerns"].append(
            f"{len(unresolved)} phrase(s) end with a dissonance still sounding "
            f"({', '.join(unresolved[:3])}). Nothing carries that across the "
            f"barline, so the next phrase does not know it owes a resolution."
        )

    # A phrase whose melody starts a long way from where the last one ended is
    # beginning again rather than continuing. A leap across a phrase boundary is
    # a legitimate gesture; doing it every time is a piece of disconnected
    # fragments.
    jumps = 0
    for ((_pid_a, tail), ir_b) in zip(tails, layers[1:], strict=False):
        prev = tail.get("last_soprano_midi")
        first = next(
            (
                e
                for e in sorted(ir_b.principal_line, key=lambda e: (e.bar, e.beat))
                if e.pitch and e.pitch != "rest"
            ),
            None,
        )
        if prev is None or first is None:
            continue
        names = first.pitch if isinstance(first.pitch, list) else [first.pitch]
        vals = [v for v in (pitch_to_midi(n) for n in names) if v is not None]
        if vals and abs(max(vals) - prev) > 12:
            jumps += 1
    if jumps and jumps >= max(2, (len(layers) - 1) // 2):
        out["concerns"].append(
            f"{jumps} of {len(layers) - 1} phrase boundaries jump more than an "
            f"octave from where the previous phrase's melody ended. One is a "
            f"gesture; this many reads as a set of fragments rather than a line."
        )
    if not out["concerns"]:
        out["observations"].append("each phrase picks up near where the last one left off")
    return out


def _texture_section(merged, style: str | None) -> dict[str, Any]:
    from .voicing import CORPUS_TEXTURE, analyze_voicing, compare_to_corpus_texture, texture_runs

    rep = analyze_voicing(merged, style=style)
    runs = texture_runs(merged)
    out: dict[str, Any] = {
        "observations": list(rep.observations),
        "concerns": list(rep.suggestions),
        "measurements": rep.as_dict(),
    }
    # How this texture sits against the period it is written in. Prose, not
    # z-scores: handing a composer a distance from a distribution turns
    # composition into metric whack-a-mole, which this project has already
    # established is a ceiling rather than a path.
    period = "romantic" if (rep.style or "") in ("romantic", "impressionist") else "classical"
    for line in compare_to_corpus_texture(rep, CORPUS_TEXTURE.get(period)):
        out["observations"].append(line)

    # A long unchanging run is the "twelve bars of the same figure" finding,
    # made visible without anyone having to read the score by eye.
    long_runs = [(lab, a, b) for lab, a, b in runs if b - a + 1 >= 8]
    out["runs"] = [f"bars {a}-{b}: {lab}" for lab, a, b in runs]
    for lab, a, b in long_runs:
        out["concerns"].append(
            f"Bars {a}-{b} ({b - a + 1} bars) hold one texture — {lab.replace('_', ' ')} — "
            f"without changing. That is long enough for a listener to stop hearing it."
        )
    return out


def _part_writing_section(merged, key: str) -> dict[str, Any]:
    from .counterpoint import analyze_counterpoint, summarize_for_critic

    rep = analyze_counterpoint(merged, key=key)
    return {
        "errors": rep.error_count,
        "warnings": rep.warn_count,
        "independence": round(rep.independence, 3),
        "by_kind": rep.by_kind(),
        "lines": summarize_for_critic(rep, limit=12),
    }


def _orchestration_section(kept) -> dict[str, Any]:
    """Range and dynamic problems in an orchestrated section.

    Only says anything when a piece has actually been orchestrated. A part
    written at the outer edge of what an instrument can produce is legal and
    miserable to play, and until now nothing looked.
    """
    out: dict[str, Any] = {"observations": [], "concerns": []}
    from .orchestration_planner import audit_orchestration

    seen = set()
    instruments = set()
    for _pid, state, _slot in kept:
        parts = getattr(state, "orchestration", None)
        if parts is None and isinstance(state, dict):
            parts = state.get("orchestration")
        if not isinstance(parts, dict) or not parts:
            continue
        instruments.update(parts.keys())
        for line in audit_orchestration(parts):
            if line not in seen:
                seen.add(line)
                out["concerns"].append(line)
    if instruments:
        out["observations"].append(
            f"orchestrated for {len(instruments)} parts: "
            f"{', '.join(sorted(instruments)[:12])}"
        )
    return out


def _page_section(merged, style: str | None) -> dict[str, Any]:
    from .expression_enricher import expression_density
    from .ornament_realization import ornament_summary

    events = _all_events(merged)
    density = expression_density(merged)
    orn = ornament_summary(events)
    out: dict[str, Any] = {
        "marks_per_bar": density.get("marks_per_bar", 0.0),
        "detail": density,
        "ornaments": orn,
        "observations": [],
        "concerns": [],
    }
    out["observations"].append(
        f"{density.get('marks_per_bar', 0)} expression marks per bar "
        f"({density.get('articulation_per_bar', 0)} articulations, "
        f"{density.get('slur_per_bar', 0)} slurs, "
        f"{density.get('dynamic_per_bar', 0)} dynamics)"
    )
    if density.get("articulation_per_bar", 0) == 0:
        out["concerns"].append(
            "Not one articulation mark in the whole piece. Nothing tells the player "
            "what is detached, what is leaned on, what is carried — so it will be "
            "played, and previewed, exactly as a sequencer would play it."
        )
    if density.get("slur_per_bar", 0) == 0:
        out["concerns"].append(
            "No slurs anywhere, so nothing on the page groups notes into gestures. "
            "The line has no phrasing for a player to shape."
        )
    if density.get("tie_per_bar", 0) == 0:
        out["concerns"].append(
            "No ties in the whole piece — nothing is held across a barline, which "
            "is unusual enough in real writing to be worth a second look."
        )
    if orn["ornaments"] and orn["audible"] == 0:
        out["concerns"].append(
            f"{orn['ornaments']} ornaments are written and none of them are the kind "
            f"that produce sounding notes, so nothing of the ornamental surface "
            f"reaches the ear."
        )
    return out


def _craft_section(kept, layers) -> dict[str, Any]:
    """The phrase-sanctity checklist, per phrase.

    The checklist has existed all along and has run on **no phrase the system
    ever composed** — ``craft_check`` is written only inside the engine fallback
    path, which the default flow never takes. Measured 0 of 164 phrases across
    12 pieces. Running it here is the first time its findings reach anyone.
    """
    from .craft_checker import check_phrase, craft_score

    out: dict[str, Any] = {"observations": [], "concerns": [], "per_phrase": {}}
    scores = []
    counts: dict[str, int] = {}
    for (pid, _state, _slot), ir in zip(kept, layers, strict=True):
        check, findings = check_phrase(ir)
        scores.append(craft_score(check))
        if findings:
            out["per_phrase"][pid] = findings
            for f in findings:
                counts[f] = counts.get(f, 0) + 1
    if scores:
        out["mean_score"] = round(sum(scores) / len(scores), 3)
        out["observations"].append(
            f"craft checklist: {out['mean_score']:.0%} of checks pass on average "
            f"across {len(scores)} phrases"
        )
    # Report a fault that recurs across phrases once, not once per phrase — a
    # reviewer needs the pattern, not forty copies of the same sentence.
    for finding, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n >= max(2, len(scores) // 3):
            out["concerns"].append(f"[{n} of {len(scores)} phrases] {finding}")
    return out


# ─── Entry point ─────────────────────────────────────────────────────────────


def build_report(graph, style: str | None = None, scope: str = "full") -> MusicalReport:
    """Analyze a whole PieceGraph and return the musician's-eye report."""
    rows = _ordered_phrases(graph)
    if scope.startswith("section-"):
        want = scope[len("section-") :]
        rows = [r for r in rows if str(r[2].get("section_id", "")) == want]

    layers, kept = [], []
    for pid, state, slot in rows:
        ir = _phrase_layer(state, slot)
        if ir is None:
            continue
        layers.append(ir)
        kept.append((pid, state, slot))

    report = MusicalReport(piece_id=str(getattr(graph, "piece_id", "")), phrases=len(layers))
    if not layers:
        report.page = {"observations": ["nothing realized yet"], "concerns": []}
        return report

    merged = _merge(layers)
    report.bars = merged.bar_count
    key = str(kept[0][2].get("key", "C") or "C")
    if style is None:
        dna = getattr(graph, "style_dna", None)
        style = (
            getattr(dna, "composer_id", None) or getattr(dna, "active_period", None)
            if dna
            else None
        )

    report.theme = _theme_section(graph, layers, kept)
    report.cadences = _cadence_section(kept, layers)
    report.texture = _texture_section(merged, style)
    report.part_writing = _part_writing_section(merged, key)
    report.page = _page_section(merged, style)
    report.craft = _craft_section(kept, layers)
    report.orchestration = _orchestration_section(kept)
    report.continuity = _continuity_section(kept, layers)
    return report


def render_text(report: MusicalReport, max_lines: int = 60) -> str:
    """The report as prose, for a reviewer to read.

    Ordered by what a musician notices first: whether the piece has a tune and
    brings it back, how it punctuates, what its texture does, whether the page
    is playable, and only last the part-writing detail.
    """
    out: list[str] = []
    out.append(f"MUSICAL REPORT — {report.piece_id or 'piece'}")
    out.append(f"{report.bars} bars across {report.phrases} realized phrases")

    def block(title: str, section: dict[str, Any], extra_key: str | None = None):
        obs = section.get("observations") or []
        con = section.get("concerns") or []
        if not (obs or con or section.get(extra_key or "")):
            return
        out.append("")
        out.append(title)
        for line in obs:
            out.append(f"  · {line}")
        if extra_key:
            for line in (section.get(extra_key) or [])[:12]:
                out.append(f"  · {line}")
        for line in con:
            out.append(f"  ! {line}")

    block("THEME", report.theme)
    block("CADENCES", report.cadences, extra_key="lines")
    block("TEXTURE", report.texture)
    block("THE PAGE", report.page)
    block("CRAFT", report.craft)
    block("CONTINUITY", report.continuity)
    block("ORCHESTRATION", report.orchestration)

    pw = report.part_writing
    if pw.get("lines") or pw.get("errors"):
        out.append("")
        out.append("PART-WRITING")
        out.append(
            f"  · voice independence {pw.get('independence', 0)}; "
            f"{pw.get('errors', 0)} errors, {pw.get('warnings', 0)} warnings"
        )
        for line in pw.get("lines", []):
            out.append(f"  ! {line}")

    if len(out) > max_lines:
        out = [*out[:max_lines], f"  … {len(out) - max_lines} more lines"]
    return "\n".join(out)


def concerns_only(report: MusicalReport) -> list[str]:
    """Just the things worth a second look, worst-first-ish, for a short review."""
    out: list[str] = []
    for section in (
        report.theme,
        report.cadences,
        report.texture,
        report.page,
        report.craft,
        report.orchestration,
        report.continuity,
    ):
        out.extend(section.get("concerns") or [])
    out.extend(report.part_writing.get("lines") or [])
    return out
