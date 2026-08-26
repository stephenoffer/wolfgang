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
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ─── Report ──────────────────────────────────────────────────────────────────


@dataclass
class MusicalReport:
    piece_id: str = ""
    bars: int = 0
    phrases: int = 0

    theme: Dict[str, Any] = field(default_factory=dict)
    cadences: Dict[str, Any] = field(default_factory=dict)
    texture: Dict[str, Any] = field(default_factory=dict)
    part_writing: Dict[str, Any] = field(default_factory=dict)
    page: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "piece_id": self.piece_id,
            "bars": self.bars,
            "phrases": self.phrases,
            "theme": self.theme,
            "cadences": self.cadences,
            "texture": self.texture,
            "part_writing": self.part_writing,
            "page": self.page,
        }


# ─── Loading ─────────────────────────────────────────────────────────────────


def _phrase_layer(phrase_state, slot: Dict[str, Any]):
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
    fields = LayerEvent.__dataclass_fields__
    for name in (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
    ):
        src = (
            realized.get(name)
            if isinstance(realized, dict)
            else getattr(realized, name, None)
        ) or []
        target = getattr(ir, name)
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
    ir.bar_count = len({e.bar for e in ir.principal_line}) or 1
    return ir


def _slot_of(phrase_state) -> Dict[str, Any]:
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


def _ordered_phrases(graph) -> List[Tuple[str, Any, Dict[str, Any]]]:
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
    for ir in layers:
        for name in (
            "principal_line",
            "bass_foundation",
            "response_layer",
            "counter_reply",
            "ornamental_surface",
        ):
            getattr(merged, name).extend(getattr(ir, name) or [])
        for vname, evs in (ir.inner_voices or {}).items():
            merged.inner_voices.setdefault(vname, []).extend(evs)
    merged.bar_count = len({e.bar for e in merged.principal_line}) or 1
    return merged


# ─── Sections of the report ──────────────────────────────────────────────────


def _theme_section(graph, layers, rows) -> Dict[str, Any]:
    from .theme_planner import analyze_theme, theme_recurrence

    out: Dict[str, Any] = {"observations": [], "concerns": []}
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

    rec = theme_recurrence(graph, theme_ir)
    out["recurrences"] = len(rec["recurrences"])
    out["sections"] = rec["sections"]
    n = len(rec["recurrences"])
    if n <= 1:
        out["concerns"].append(
            f"The principal theme appears in {n} place{'s' if n != 1 else ''} in the "
            f"whole piece. A theme that is stated and never returns is not a theme, "
            f"it is an opening. Bringing it back — transposed, re-harmonised, "
            f"fragmented, in the bass — is what makes a piece cohere."
        )
    else:
        out["observations"].append(
            f"The theme's shape returns in {n} places ({', '.join(rec['sections'])})."
        )
    return out


def _cadence_section(rows, layers) -> Dict[str, Any]:
    from .cadence_analysis import analyze_cadences, cadence_summary_lines

    specs = []
    for (pid, _state, slot), ir in zip(rows, layers):
        specs.append((ir, slot.get("cadence_bar"), slot.get("key"), slot.get("cadence_target")))
    rep = analyze_cadences(specs)
    return {
        "lines": cadence_summary_lines(rep, limit=16),
        "variety": round(rep.variety, 3),
        "repeated_formulas": rep.repeated_formulas,
        "observations": rep.observations,
        "concerns": rep.suggestions,
    }


def _texture_section(merged, style: Optional[str]) -> Dict[str, Any]:
    from .voicing import analyze_voicing, texture_runs

    rep = analyze_voicing(merged, style=style)
    runs = texture_runs(merged)
    out: Dict[str, Any] = {
        "observations": list(rep.observations),
        "concerns": list(rep.suggestions),
        "measurements": rep.as_dict(),
    }
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


def _part_writing_section(merged, key: str) -> Dict[str, Any]:
    from .counterpoint import analyze_counterpoint, summarize_for_critic

    rep = analyze_counterpoint(merged, key=key)
    return {
        "errors": rep.error_count,
        "warnings": rep.warn_count,
        "independence": round(rep.independence, 3),
        "by_kind": rep.by_kind(),
        "lines": summarize_for_critic(rep, limit=12),
    }


def _page_section(merged, style: Optional[str]) -> Dict[str, Any]:
    from .expression_enricher import expression_density
    from .ornament_realization import ornament_summary

    events = []
    for name in (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
    ):
        events.extend(getattr(merged, name) or [])
    density = expression_density(merged)
    orn = ornament_summary(events)
    out: Dict[str, Any] = {
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


# ─── Entry point ─────────────────────────────────────────────────────────────


def build_report(graph, style: Optional[str] = None, scope: str = "full") -> MusicalReport:
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
    return report


def render_text(report: MusicalReport, max_lines: int = 60) -> str:
    """The report as prose, for a reviewer to read.

    Ordered by what a musician notices first: whether the piece has a tune and
    brings it back, how it punctuates, what its texture does, whether the page
    is playable, and only last the part-writing detail.
    """
    out: List[str] = []
    out.append(f"MUSICAL REPORT — {report.piece_id or 'piece'}")
    out.append(f"{report.bars} bars across {report.phrases} realized phrases")

    def block(title: str, section: Dict[str, Any], extra_key: Optional[str] = None):
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
        out = out[:max_lines] + [f"  … {len(out) - max_lines} more lines"]
    return "\n".join(out)


def concerns_only(report: MusicalReport) -> List[str]:
    """Just the things worth a second look, worst-first-ish, for a short review."""
    out: List[str] = []
    for section in (report.theme, report.cadences, report.texture, report.page):
        out.extend(section.get("concerns") or [])
    out.extend(report.part_writing.get("lines") or [])
    return out
