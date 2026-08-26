"""
SCALES — Top-level orchestrator.

Sketch-Conditioned Alternating Ledger-guided Expansion Search.

This module provides the Python tool surface that Claude's skills call.
All functions operate on the PieceGraph as the single source of truth.
"""

from __future__ import annotations

import json
import logging
from dataclasses import fields
from datetime import datetime, timezone
from fractions import Fraction as _F
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .anti_pattern_detector import run_all_detectors
from .cadence_bank import CadenceBank
from .candidate_scorer import CandidateScorer
from .context_compiler import ContextCompiler
from .context_router import ContextRouter
from .context_utilization import compute_utilization
from .craft_checker import CraftChecker
from .cross_scale_ledger import CrossScaleLedger
from .donor_strategy import DonorStrategy
from .enums import (
    AccompType,
    CadenceTarget,
    ExpectationDomain,
    ExpectationType,
    PhraseFunction,
    PipelinePhase,
    TextureType,
)
from .expectation_ledger import ExpectationLedger
from .gesture_bank import GestureBank
from .harmonic_solver import HarmonicSolver
from .models import (
    BarTexturePlan,
    CandidateNode,
    ContextTrace,
    FormGraph,
    HarmonicCell,
    LayerIR,
    MotifObject,
    MotifSlot,
    MovementContract,
    MovementSpec,
    NarrativeArc,
    NarrativeSection,
    PhraseControlIR,
    PhraseCurves,
    PhraseSlot,
    SectionContract,
    SectionSpec,
    SketchIR,
    StyleDNA,
    WorkGraph,
)

# v6 imports
from .pattern_retriever import PatternRetriever
from .phrase_bank import PhraseBank
from .piece_graph import PieceGraph, load_layer_ir_from_dict
from .realizer import Realizer
from .reducer import Reducer
from .section_search import SectionSearch
from .sketch_proposer import SketchProposer
from .style_resolver import StyleResolver
from .surface_composer import SurfaceComposer

_WORKSPACE = Path("workspace")
_LOG = logging.getLogger(__name__)


def _as_list(value, what: str):
    """Normalise a tool argument that must be a list, or say why it cannot be.

    Every function in this module is called by an agent writing a Python
    snippet, so the arguments arrive hand-typed. A bare string is a sequence of
    **characters**, and Python will iterate it happily: `compile_style(...,
    composers="mozart")` compiled six one-letter "composers" (a, m, o, r, t, z —
    the letters of the name), left `tools/compiled_packs/m/` on disk, and then
    resolved the whole piece's style against "m": tier D, zero fingerprints,
    zero cadences, zero left-hand textures. The piece still generated. It simply
    had no style, and nothing anywhere said so.

    So: coerce the two unambiguous single-item cases (a lone string, a lone
    dict) and refuse anything else loudly, because a silent misread here costs
    a whole piece.
    """
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if isinstance(value, dict):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    raise TypeError(
        f"{what} must be a list (or a single item), got {type(value).__name__}: {value!r}"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ─── Workspace Management ────────────────────────────────────────────────────


def init_workspace(
    piece_id: str, mode: str, description: str = "", params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a new workspace and initialize PieceGraph.

    Returns summary dict for Claude.
    """
    workspace = _WORKSPACE / piece_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "cache").mkdir(exist_ok=True)
    (workspace / "output").mkdir(exist_ok=True)
    (workspace / "logs").mkdir(exist_ok=True)

    graph = PieceGraph.create(piece_id, mode, description)

    if params:
        if "source_path" in params:
            from .models import SourceReference

            graph.contract.source = SourceReference(path=params["source_path"])
        if "instrumentation" in params:
            graph.contract.target.instrumentation = params["instrumentation"]
        if "difficulty" in params:
            graph.contract.target.difficulty = params["difficulty"]

    graph.phase = PipelinePhase.INIT.value
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "piece_id": piece_id,
        "workspace": str(workspace),
        "piece_graph_path": str(workspace / "piece_graph.json"),
        "mode": mode,
    }


def load_workspace(piece_id: str) -> Dict[str, Any]:
    """Load existing workspace and return status summary."""
    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"

    if not graph_path.exists():
        return {"error": f"Workspace not found: {piece_id}"}

    graph = PieceGraph.load(str(graph_path))
    return graph.get_status_summary()


def get_status(piece_id: str) -> Dict[str, Any]:
    """Quick status check."""
    return load_workspace(piece_id)


def list_sections(piece_id: str) -> Dict[str, Any]:
    """Ordered sections with a compact per-phrase summary — the deterministic
    work-list for the compose pipeline (used by the wolfgang-compose workflow
    and the orchestrator). Each phrase carries status + agent_authored so a
    resume skips already-composed phrases. Phrases are listed in their
    committed order (composition within a section is sequential)."""
    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"
    if not graph_path.exists():
        return {"error": f"Workspace not found: {piece_id}"}
    graph = PieceGraph.load(str(graph_path))
    sections = []
    for sid in graph.form.sections:  # insertion order = movement→section build order
        phrases = []
        for pid in graph.get_section_phrases(sid):
            st = graph.phrases.get(pid)
            phrases.append(
                {
                    "phrase_id": pid,
                    "status": getattr(st, "status", "missing") if st else "missing",
                    "agent_authored": bool(getattr(st, "agent_authored", False)) if st else False,
                }
            )
        sections.append({"section_id": sid, "phrases": phrases})
    return {
        "piece_id": piece_id,
        "sections": sections,
        "section_count": len(sections),
        "phrase_count": sum(len(s["phrases"]) for s in sections),
    }


# ─── Planning Tools ──────────────────────────────────────────────────────────


def compile_style(
    piece_id: str,
    composers: List[str],
    blend_weights: Optional[Dict[str, float]] = None,
    era: str = "",
    genre: str = "",
) -> Dict[str, Any]:
    """Compile StyleDNA and StyleProgram for the piece.

    Runs the context compiler (passes 1-12) and style resolver.
    For Tier C/D composers, applies donor strategy.
    """
    # A bare string is a sequence of CHARACTERS. Passing composers="mozart" — the
    # obvious call, and the one a reader of the signature makes — compiled seven
    # bogus one-letter "composers" and then resolved the whole piece's style
    # against "m": tier D, zero fingerprints, zero cadences, zero LH textures.
    # The piece still generated; it just had no style at all, and nothing said so.
    if isinstance(composers, str):
        composers = [composers]
    composers = [c for c in (composers or []) if c]
    if not composers:
        raise ValueError("compile_style needs at least one composer or style name")

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    # Compile packs for each composer (all 12 passes)
    compiler = ContextCompiler()
    for composer in composers:
        compiler.compile(composer, genre)

    # Resolve style
    resolver = StyleResolver()
    if blend_weights and len(composers) > 1:
        program = resolver.resolve_blend_program(blend_weights, era)
    else:
        program = resolver.resolve_program(composers[0], era)

    # Handle donor strategy for sparse-corpus composers
    if program.dna.tier in ("C", "D"):
        ds = DonorStrategy()
        donor_plan = ds.resolve_donors(composers[0], program.dna.tier, genre)
        if donor_plan.donors:
            program = ds.augment_program(program, donor_plan)

    graph.style_dna = program.dna  # backward compat
    graph.style_program = program  # v6
    graph.save(str(workspace / "piece_graph.json"))

    result = {
        "composer_id": program.dna.composer_id,
        "tier": program.dna.tier,
        "fingerprints": len(program.dna.fingerprints.items),
        "lh_textures": len(program.dna.lh_distribution),
        "cadences": len(program.dna.cadence_vocabulary),
        "gesture_templates": len(program.gesture_templates),
        "anti_patterns": len(program.anti_patterns),
        "harmonic_devices": len(program.harmonic_devices),
        "breathing_rules": len(program.breathing_rules),
        "ornament_intents": len(program.ornament_intents),
        "donor_plan": bool(program.donor_plan and program.donor_plan.donors),
        "axis_ownership": program.dna.axis_ownership,
    }
    # Say it out loud when the style compiled to nothing. A tier-D profile with
    # no fingerprints and no cadence vocabulary means every brief downstream will
    # be generic, and that is worth a warning rather than a silent pass.
    if not result["fingerprints"] and not result["cadences"]:
        result["warning"] = (
            f"style '{composers[0]}' compiled with no fingerprints and no cadence "
            f"vocabulary (tier {result['tier']}) — briefs will be generic. Check "
            f"the composer name, or arm it with scripts/acquire_composer.py."
        )
    return result


def build_form_graph(
    piece_id: str,
    form: str,
    key: str,
    tempo_bpm: int = 120,
    meter: Tuple[int, int] = (4, 4),
    sections: Optional[List[Dict]] = None,
    motif_ids: Optional[List[str]] = None,
) -> List[Dict]:
    """Build a form graph with PhraseSlots.

    Returns list of PhraseSlot summaries for Claude to review.
    """
    sections = _as_list(sections, "sections")
    motif_ids = _as_list(motif_ids, "motif_ids")
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    # Build sections and phrases based on form
    form_graph = FormGraph()
    phrase_summaries = []

    if form == "ternary":
        phrases = _build_ternary(key, tempo_bpm, meter, graph.style_dna)
    elif form == "sonata":
        phrases = _build_sonata(key, tempo_bpm, meter, graph.style_dna)
    elif form == "theme_variations":
        phrases = _build_theme_variations(key, tempo_bpm, meter, graph.style_dna)
    else:
        phrases = _build_simple(key, tempo_bpm, meter, form, graph.style_dna)

    # Create movement
    movement = MovementSpec(
        id="m1",
        form=form,
        key=key,
        tempo_bpm=tempo_bpm,
        meter=meter,
        sections=[],
    )

    # Group phrases into sections and add to graph
    current_section_id = ""
    for slot in phrases:
        # Wire the planned emotional arc into per-bar slot curves (keystone:
        # drives dynamics, density targets, register, and the tempo arc).
        _apply_narrative_curves(slot, graph.narrative)
        if slot.section_id != current_section_id:
            current_section_id = slot.section_id
            section = SectionSpec(
                id=current_section_id,
                movement_id="m1",
                key=slot.key,
                phrase_ids=[],
            )
            form_graph.sections[current_section_id] = section
            movement.sections.append(current_section_id)

        form_graph.sections[current_section_id].phrase_ids.append(slot.phrase_id)
        graph.add_phrase(slot.phrase_id, slot)

        phrase_summaries.append(
            {
                "phrase_id": slot.phrase_id,
                "section": slot.section_id,
                "bars": f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}",
                "function": slot.function,
                "cadence": slot.cadence_target,
                "key": slot.key,
            }
        )

    form_graph.movements.append(movement)
    graph.form = form_graph

    # The dramatic plan: what each phrase is FOR. Without this, planning produced
    # a form skeleton with an energy ramp and nothing else — no climax, no tension
    # arc, no register plan, no strategy for how a return differs from the
    # statement, and no phrase knowing what it leads into.
    from . import dramatic_plan

    plan_info = dramatic_plan.build([graph.phrases[p.phrase_id].slot for p in phrases])
    graph.narrative = _narrative_from_slots(
        [graph.phrases[p.phrase_id].slot for p in phrases], plan_info
    )

    # Build SectionContracts from the form graph sections
    for sec_id, sec_spec in form_graph.sections.items():
        # Determine section role from phrase functions
        section_phrases = [
            graph.phrases[pid].slot for pid in sec_spec.phrase_ids if pid in graph.phrases
        ]
        cadence_path = [s.cadence_target for s in section_phrases]
        energy_envelope = []
        for s in section_phrases:
            energy_envelope.extend(s.curves.energy if s.curves.energy else [0.5] * s.bar_count)

        from .dramatic_plan import section_rhetoric

        _roles = [getattr(sl, "dramatic_role", "") for sl in section_phrases]
        _goals, _techs = section_rhetoric([r for r in _roles if r])
        graph.section_contracts[sec_id] = SectionContract(
            id=sec_id,
            movement_id=sec_spec.movement_id or "m1",
            role=sec_spec.role or _infer_section_role(sec_id),
            key=sec_spec.key,
            bar_start=section_phrases[0].bar_start if section_phrases else 1,
            bar_end=(section_phrases[-1].bar_start + section_phrases[-1].bar_count - 1)
            if section_phrases
            else 8,
            phrase_ids=sec_spec.phrase_ids,
            cadence_path=cadence_path,
            energy_envelope=energy_envelope,
            rhetorical_goals=_goals,
            development_techniques=_techs,
            texture_family=(
                section_phrases[0].texture_plan[0].lh_texture
                if section_phrases and section_phrases[0].texture_plan
                else ""
            ),
        )
        for _sl in section_phrases:
            _sl.section_techniques = list(_techs)

    # ─── Populate expectations from form structure ─────────────────────
    #
    # This block wrote nothing, for any piece, for the entire life of the
    # project. Not because it raised — the `except Exception: pass` that used to
    # wrap it never fired — but because every write was guarded by
    # `if _cross_ledger is not None` / `elif _ledger is not None`, and a fresh
    # PieceGraph has `cross_scale_ledger = None` and no `expectation_ledger`
    # attribute at all. Both guards were False every time, so the loop ran to
    # completion and recorded nothing, and the swallow-everything handler hid
    # the cause. `ensure_ledger` creates or restores one, so there is now
    # something to populate.
    from .cross_scale_ledger import ensure_ledger, persist_ledger

    _cross_ledger = ensure_ledger(graph)
    _ledger = None

    for sec_id, sec_contract in graph.section_contracts.items():
        role = sec_contract.role

        # Development sections promise theme recapitulation
        if role == "development":
            if _cross_ledger is not None:
                _cross_ledger.add_movement_expectation(
                    exp_type=ExpectationType.PROMISE.value,
                    domain=ExpectationDomain.MOTIF_THEME.value,
                    object_ref=f"theme_recap_after_{sec_id}",
                    introduced_at=sec_id,
                    expected_form="theme recapitulation",
                    urgency=0.7,
                    details={"source_section": sec_id, "role": role},
                )
            elif _ledger is not None:
                _ledger.add_promise(
                    object_ref=f"theme_recap_after_{sec_id}",
                    introduced_at=sec_id,
                    expected_form="theme recapitulation",
                    urgency=0.7,
                    details={"source_section": sec_id, "role": role},
                )

        # Sections with cadence paths create a debt for cadence resolution
        if sec_contract.cadence_path:
            if _cross_ledger is not None:
                _cross_ledger.add_section_expectation(
                    exp_type=ExpectationType.DEBT.value,
                    domain=ExpectationDomain.CADENCE.value,
                    object_ref=f"cadence_resolution_{sec_id}",
                    introduced_at=sec_id,
                    must_resolve_by=sec_contract.phrase_ids[-1]
                    if sec_contract.phrase_ids
                    else None,
                    urgency=0.6,
                    details={
                        "cadence_path": [str(c) for c in sec_contract.cadence_path],
                        "section": sec_id,
                    },
                )
            elif _ledger is not None:
                _ledger.add_debt(
                    object_ref=f"cadence_resolution_{sec_id}",
                    opened_at=sec_id,
                    must_resolve_by=sec_contract.phrase_ids[-1]
                    if sec_contract.phrase_ids
                    else None,
                    urgency=0.6,
                    details={
                        "cadence_path": [str(c) for c in sec_contract.cadence_path],
                        "section": sec_id,
                    },
                )
    # Serialize before saving: `PieceGraph.cross_scale_ledger` is typed as the
    # SERIALIZED form, so leaving the live object on it breaks `save` and every
    # promise recorded here would be gone before composition ever read it.
    persist_ledger(graph, _cross_ledger)

    graph.phase = PipelinePhase.PLANNING.value
    # Decide the piece's METRIC ENTRY at the composer's own rate. A piece that
    # always begins squarely on beat 1 of bar 1 sounds squared-off, and none of
    # the twelve pieces in workspace/ has ever begun any other way — while 46% of
    # Mozart's movements and 69% of Bach's open with a pickup. The shorthand and
    # the engraver have both supported an anacrusis all along; nothing asked.
    _plan_metric_entry(graph)

    # Elect ONE principal theme and state it at every section opening
    # (transformed at the recap) — a memorable, recurring through-line instead of
    # locally-optimized, independent phrases. Runs AFTER the slots exist, and is
    # idempotent, so `resolve_motifs` can do the same work if it comes second.
    _place_principal_theme(graph)

    graph.save(str(workspace / "piece_graph.json"))

    return phrase_summaries


def _narrative_from_slots(slots, plan_info) -> "NarrativeArc":
    """Build a NarrativeArc from the planned slots' dramatic roles.

    ``narrative.sections`` was empty after planning and ``primary_climax_section``
    was blank, so every downstream consumer of the narrative (the brief's CREATIVE
    INTENT, the per-bar curve interpolation, the critic's arc judgement) had
    nothing to read.
    """
    from .dramatic_plan import ROLE_INTENT

    arc = NarrativeArc()
    by_section: Dict[str, List] = {}
    for slot in slots:
        by_section.setdefault(slot.section_id, []).append(slot)
    climax_phrase = plan_info.get("climax_phrase")
    for section_id, group in by_section.items():
        roles = [getattr(s, "dramatic_role", "") for s in group]
        is_climax = any(s.phrase_id == climax_phrase for s in group)
        arc.sections.append(
            NarrativeSection(
                id=section_id,
                label=section_id,
                bar_start=group[0].bar_start,
                bar_end=group[-1].bar_start + group[-1].bar_count - 1,
                energy_curve=[v for s in group for v in (s.curves.energy or [])],
                tension_curve=[v for s in group for v in (s.curves.tension or [])],
                density_curve=[v for s in group for v in (s.curves.density or [])],
                brightness_curve=[v for s in group for v in (s.curves.brightness or [])],
                climax_type="primary" if is_climax else "",
                character="; ".join(dict.fromkeys(ROLE_INTENT.get(r, "") for r in roles if r)),
                gesture=" then ".join(dict.fromkeys(r for r in roles if r)),
            )
        )
        if is_climax:
            arc.primary_climax_section = section_id
    return arc


def resolve_motifs(piece_id: str, motif_definitions: List[Dict]) -> Dict[str, Any]:
    """Validate and store motif definitions."""
    motif_definitions = _as_list(motif_definitions, "motif_definitions")
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    for mdef in motif_definitions:
        motif = MotifObject(
            motif_id=mdef.get("motif_id", ""),
            character=mdef.get("character", ""),
            scale_degree_contour=mdef.get("scale_degree_contour", []),
            interval_contour=mdef.get("interval_contour", []),
            rhythm_cell=mdef.get("rhythm_cell", []),
            accent_profile=mdef.get("accent_profile", []),
            recognition_anchor=mdef.get("recognition_anchor", {}),
            allowed_transforms=mdef.get("allowed_transforms", []),
        )
        graph.motif_bank[motif.motif_id] = motif

    # Back-fill theme placements onto slots that already exist.
    #
    # `build_form_graph` writes `slot.motif_transforms` only if
    # `graph.principal_theme_id` is already set, which requires the motif bank to
    # exist at that moment. The documented plan order is motifs (step 4) then
    # form (step 5), but in practice the form is built first — and then nothing
    # ever revisits it. Measured over the twelve pieces in `workspace/`: five have
    # a populated motif bank (3, 5, 6, 3 and 3 motifs) and NOT ONE has an elected
    # principal theme or a single placement on any of its 113 phrases. The theme
    # system — the thing that makes a piece memorable rather than a run of
    # individually plausible phrases — has never been active in a real run.
    #
    # Making the two steps order-independent is the fix; the election logic
    # itself works on every one of those banks.
    placed = _place_principal_theme(graph)

    graph.save(str(workspace / "piece_graph.json"))
    return {
        "motifs_stored": len(graph.motif_bank),
        "motif_ids": list(graph.motif_bank.keys()),
        "principal_theme_id": graph.principal_theme_id,
        "sections_given_a_theme_statement": placed,
    }


def _plan_metric_entry(graph) -> None:
    """Mark the opening phrase as an anacrusis when this composer usually does.

    Deterministic, not random: the decision is seeded by the piece id, so the
    same piece always plans the same way and a rebuild does not silently change
    the music.
    """
    # Read the slots OFF THE GRAPH, not from a caller's list. The graph holds its
    # own PhraseState objects, so mutating a local list of slots changes nothing
    # that gets saved — which is how this field was set correctly in memory and
    # came back empty on the very next load.
    slots = [st.slot for st in graph.phrases.values() if getattr(st, "slot", None)]
    if not slots:
        return
    from .composition_brief import anacrusis_rate, resolve_composer

    warnings: List[str] = []
    composer = resolve_composer(graph, None, warnings)
    try:
        rate = anacrusis_rate(composer)
    except Exception:
        return
    if rate <= 0:
        return
    opening = min(slots, key=lambda s: s.bar_start)
    if opening.metric_entry:
        return  # already decided (a replan, or the planner said so explicitly)
    seed = sum(ord(c) for c in (graph.piece_id or "")) % 1000 / 1000.0
    opening.metric_entry = "anacrusis" if seed < rate else "downbeat"


def _place_principal_theme(graph) -> int:
    """Elect the principal theme and place it at each section opening.

    Idempotent: a section that already carries a placement is left alone, so this
    is safe to call from both `build_form_graph` and `resolve_motifs` regardless
    of which ran first.
    """
    from .theme_planner import elect_principal_theme, plan_section_opening_placements

    if not graph.motif_bank:
        return 0
    if not graph.principal_theme_id:
        graph.principal_theme_id = elect_principal_theme(graph.motif_bank) or ""
    if not graph.principal_theme_id:
        return 0

    by_section: Dict[str, List] = {}
    for state in graph.phrases.values():
        slot = getattr(state, "slot", None)
        if slot is not None:
            by_section.setdefault(slot.section_id, []).append(slot)

    placed = 0
    for section_id, slots in by_section.items():
        slots.sort(key=lambda s: s.bar_start)
        if any(s.motif_transforms for s in slots):
            continue  # this section already has its statement planned
        slots[0].motif_transforms.extend(
            plan_section_opening_placements(
                _infer_section_role(section_id), graph.principal_theme_id
            )
        )
        placed += 1
    return placed


def save_narrative(
    piece_id: str,
    sections: List[Dict[str, Any]],
    overall_character: str = "",
    primary_climax_section: str = "",
) -> Dict[str, Any]:
    """Persist the emotional NarrativeArc the agent authored at plan time.

    Each section dict drives composition of every phrase it covers. The
    ``character`` field is the dramatic EVENT in prose (e.g. "the storm finally
    breaks, after three failed attempts to rise") — this is what the
    composition brief surfaces as CREATIVE INTENT and what should drive the
    notes, not the curve-averaged adjectives. Curves (energy/tension/
    brightness/density, 0-1) remain optional shaping cues.

    section dict keys: id, label, bar_start, bar_end, character (prose),
    gesture (optional prose), energy_curve, tension_curve, brightness_curve,
    density_curve (lists of 0-1), climax_type ("primary"|"secondary"|"anti").
    """
    sections = _as_list(sections, "sections")
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    sec_fields = {f.name for f in fields(NarrativeSection)}
    arc = NarrativeArc(
        overall_character=overall_character,
        primary_climax_section=primary_climax_section,
    )
    missing_character = []
    for sd in sections:
        if not isinstance(sd, dict):
            continue
        sec = NarrativeSection(**{k: v for k, v in sd.items() if k in sec_fields})
        if not (sec.character or "").strip():
            missing_character.append(sec.id or sec.label or f"bars {sec.bar_start}-{sec.bar_end}")
        arc.sections.append(sec)
    if not primary_climax_section:
        primary = next((s.id for s in arc.sections if s.climax_type == "primary"), "")
        arc.primary_climax_section = primary
    graph.narrative = arc
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "sections_stored": len(arc.sections),
        "overall_character": arc.overall_character,
        "primary_climax_section": arc.primary_climax_section,
        # The agent should author prose intent for every section; warn (don't
        # block) so this stays a planning discipline, not a hard gate.
        "sections_missing_character": missing_character,
        "warning": (
            f"{len(missing_character)} section(s) have no authored character prose — "
            "the brief will fall back to generic curve-adjectives there"
            if missing_character
            else ""
        ),
    }


# ─── SCALES Core ─────────────────────────────────────────────────────────────


def run_scales_section(
    piece_id: str,
    section_id: str,
    k_sketches: int = 3,
    n_realizations: int = 4,
    beam_width: int = 5,
    use_v6_pipeline: bool = True,
    run_style_gate: bool = False,
) -> Dict[str, Any]:
    """Run the full SCALES algorithm on one section.

    This is the main engine entry point. When use_v6_pipeline=True,
    uses the context-aware surface composer with onset bundles.
    Falls back to the original realizer when v6 components are unavailable.

    When run_style_gate=True, after committing the best path, runs
    ``run_style_review_section`` and attaches results under ``style_review``.
    """
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    composer_id = graph.style_dna.composer_id
    if "+" in composer_id:
        composer_id = composer_id.split("+")[0].replace("blend:", "")

    # Set up classic components
    pb = PhraseBank(composer_id)
    gb = GestureBank(composer_id)
    cb = CadenceBank(composer_id)

    proposer = SketchProposer(pb, gb, cb)
    realizer = Realizer(gb, cb, motif_bank=graph.motif_bank)
    reducer = Reducer()
    scorer = CandidateScorer(reducer)
    search = SectionSearch()

    phrase_order = graph.get_section_phrases(section_id)

    if not phrase_order:
        return {"error": f"No phrases found for section {section_id}"}

    # Set up v6 components if available
    pr = None
    cr = None
    hs = None
    sc = None
    cc = None
    cbr = None
    cross_ledger = None
    section_contract = graph.section_contracts.get(section_id)
    style_program = graph.style_program

    if use_v6_pipeline and style_program:
        pr = PatternRetriever()
        # Corpus bars: tier A/B use target composer; C/D use donor corpus when available
        from .corpus_bar_retriever import CorpusBarRetriever

        tier = style_program.dna.tier if style_program.dna else "D"
        cbr = None
        if tier in ("A", "B"):
            cbr = CorpusBarRetriever(composer_id)
        elif tier in ("C", "D") and style_program.donor_plan and style_program.donor_plan.donors:
            donors_sorted = sorted(
                style_program.donor_plan.donors,
                key=lambda x: -x[1],
            )
            for donor_composer, _w in donors_sorted:
                try:
                    cand = CorpusBarRetriever(donor_composer)
                    if cand.bar_count > 0:
                        cbr = cand
                        break
                except Exception:
                    continue
        cr = ContextRouter(pr, corpus_bar_retriever=cbr)
        hs = HarmonicSolver()
        # Set up phrase-level composer with all retrieval banks
        sc = SurfaceComposer(
            pattern_retriever=pr,
            phrase_bank=pb,
            gesture_bank=gb,
            corpus_bar_retriever=cbr,
            cadence_bank=cb,
            motif_bank=graph.motif_bank,
        )
        cc = CraftChecker()
        # Use CrossScaleLedger instead of bare ExpectationLedger —
        # restored from the graph so promises/debts survive across runs
        # and movements (defensive load: a bad payload yields a fresh one)
        saved_ledger = getattr(graph, "cross_scale_ledger", None)
        if saved_ledger:
            try:
                cross_ledger = CrossScaleLedger.from_dict(saved_ledger)
            except Exception:
                cross_ledger = CrossScaleLedger()
        else:
            cross_ledger = CrossScaleLedger()

    # Use cross-scale ledger's phrase delegate, or standalone for classic
    ledger = cross_ledger.phrase_ledger if cross_ledger else ExpectationLedger()

    # For each phrase: sketch → realize → reduce → score
    all_candidates: Dict[str, List[CandidateNode]] = {}
    all_traces: Dict[str, ContextTrace] = {}
    prev_surface = None

    for pi, phrase_id in enumerate(phrase_order):
        phrase_state = graph.phrases.get(phrase_id)
        if not phrase_state:
            continue
        slot = phrase_state.slot

        # Agent-authored LayerIR: Claude wrote final notes — do not run engine
        if getattr(phrase_state, "agent_authored", False) and phrase_state.realized is not None:
            sketch_for_score = phrase_state.sketch
            if sketch_for_score is None:
                prop = proposer.propose(slot, graph.style_dna, k=1)
                sketch_for_score = prop[0] if prop else SketchIR(phrase_id=phrase_id)
            surface = phrase_state.realized
            reduced = reducer.reduce(surface)
            agent_node = CandidateNode(
                phrase_id=phrase_id,
                sketch_idx=0,
                realization_idx=0,
                sketch=sketch_for_score,
                surface=surface,
                reduced=reduced,
            )
            candidates = [agent_node]
            if phrase_id not in all_traces:
                all_traces[phrase_id] = ContextTrace(
                    phrase_id=phrase_id,
                    total_bar_count=slot.bar_count,
                    gestures_applied=["agent_authored:layer_ir"],
                )
            scorer_kwargs_ag: Dict[str, Any] = {}
            if style_program:
                scorer_kwargs_ag["context_traces"] = {0: all_traces[phrase_id]}
                scorer_kwargs_ag["anti_patterns"] = style_program.anti_patterns
                scorer_kwargs_ag["tier"] = style_program.dna.tier
            scorer.score_all(
                candidates,
                slot,
                graph.style_dna,
                ledger,
                phrase_order,
                prev_surface,
                graph.contract.locks,
                graph.mode,
                **scorer_kwargs_ag,
            )
            all_candidates[phrase_id] = candidates
            if candidates:
                prev_surface = candidates[0].surface
            continue

        # Phase 1: Use Claude-authored sketch if available, else propose K candidates
        if phrase_state.sketch is not None:
            # Claude wrote this sketch — use it as the sole candidate
            sketches = [phrase_state.sketch]
        else:
            sketches = proposer.propose(slot, graph.style_dna, k=k_sketches)

        # Phase 2: Realize N candidates per sketch
        candidates = []
        for si, sketch in enumerate(sketches):
            if sc and cr and hs and style_program:
                # ─── v6 pipeline: context-aware onset bundle composition ───
                # Resolve context for this phrase
                phrase_ctx = cr.resolve(
                    style_program,
                    slot,
                    section_contract=section_contract,
                    phrase_index=pi,
                    total_phrases=len(phrase_order),
                )

                # Build harmonic cells from sketch's harmonic rhythm
                h_cells = [
                    HarmonicCell(bar=h.bar, beat=h.beat, roman=h.roman, key=h.key or slot.key)
                    for h in sketch.harmonic_rhythm
                ]

                # Solve harmonic voicings
                voicings = hs.solve(h_cells, slot.key, slot.meter)

                # Build PhraseControlIR from sketch + slot
                control = PhraseControlIR(
                    phrase_id=phrase_id,
                    section_id=slot.section_id,
                    phrase_function=slot.function,
                    bars=slot.bar_count,
                    bar_start=slot.bar_start,
                    meter=slot.meter,
                    tempo_bpm=slot.tempo_bpm,
                    local_key=slot.key,
                    cadence_target=slot.cadence_target,
                    cadence_bar=slot.cadence_bar,
                    harmonic_cells=h_cells,
                    melody_anchors=sketch.melody_anchors,
                    bass_anchors=sketch.bass_anchors,
                    dynamic_shape=sketch.dynamic_shape,
                    expression_marks=sketch.expression_marks,
                    cadence=sketch.cadence,
                    # Context hooks — prove context shaped this phrase
                    fingerprint_contract=[fp.id for fp in phrase_ctx.fingerprint_targets],
                    anti_pattern_set=[ap.id for ap in phrase_ctx.active_anti_patterns],
                    gesture_plan=[g.id for g in phrase_ctx.active_gestures],
                )
                # Copy texture program from slot
                from .models import TextureProgram

                control.texture_program = TextureProgram(bars=slot.texture_plan)
                control.motif_slots = [
                    MotifSlot(
                        bar=mp.bar,
                        beat=mp.beat,
                        motif_id=mp.motif_id,
                        transform=mp.transform,
                        voice=mp.voice or "melody",
                        params=dict(mp.params or {}),
                    )
                    for mp in (sketch.motif_placements or [])
                ]

                for variant in range(n_realizations):
                    # Compose onset bundles
                    bundles, trace = sc.compose(
                        control,
                        phrase_ctx,
                        voicings,
                        style_program,
                        variant=variant,
                    )

                    # Convert to LayerIR for compatibility
                    surface = sc.bundles_to_layer_ir(
                        bundles, phrase_id, slot.key, slot.meter, slot.bar_count
                    )

                    # Self-reduction
                    reduced = reducer.reduce(surface)

                    node = CandidateNode(
                        phrase_id=phrase_id,
                        sketch_idx=si,
                        realization_idx=variant,
                        sketch=sketch,
                        surface=surface,
                        reduced=reduced,
                    )
                    candidates.append(node)

                    # Store trace for first variant
                    if variant == 0:
                        all_traces[phrase_id] = trace

            else:
                # ─── Classic pipeline: hardcoded realizer ───
                realizations = realizer.realize(
                    sketch,
                    slot,
                    graph.style_dna,
                    n=n_realizations,
                    motif_bank=graph.motif_bank,
                )

                for ri, surface in enumerate(realizations):
                    reduced = reducer.reduce(surface)
                    node = CandidateNode(
                        phrase_id=phrase_id,
                        sketch_idx=si,
                        realization_idx=ri,
                        sketch=sketch,
                        surface=surface,
                        reduced=reduced,
                    )
                    candidates.append(node)

        # Phase 4: Score all candidates (with v6 context if available)
        scorer_kwargs: Dict[str, Any] = {}
        if style_program:
            # Build per-candidate context traces for scoring
            cand_traces: Dict[int, ContextTrace] = {}
            if phrase_id in all_traces:
                for ci in range(len(candidates)):
                    cand_traces[ci] = all_traces[phrase_id]
            scorer_kwargs["context_traces"] = cand_traces
            scorer_kwargs["anti_patterns"] = style_program.anti_patterns
            scorer_kwargs["tier"] = style_program.dna.tier

        scorer.score_all(
            candidates,
            slot,
            graph.style_dna,
            ledger,
            phrase_order,
            prev_surface,
            graph.contract.locks,
            graph.mode,
            **scorer_kwargs,
        )

        all_candidates[phrase_id] = candidates

        # Track best for continuity
        if candidates:
            prev_surface = candidates[0].surface

    # Phase 5: Section-level beam search
    best_path = search.beam_search(
        all_candidates,
        phrase_order,
        mode=graph.mode,
        beam_width=beam_width,
    )

    # Phase 6: Commit best path
    engine_repairs: Dict[str, Dict[str, int]] = {}
    for node in best_path.nodes:
        if node.surface:
            # The engine path committed straight to the graph with NO physical
            # validation, while the agent path has enforced meter, range and
            # same-voice overlap at commit for months. A probe of one
            # three-phrase section found 65 meter errors going silently to the
            # score: bars holding 4.875 beats of a 4/4, notes starting while the
            # same voice was still sounding, and beat positions like 1.56 that
            # are not on any notatable grid. Repair what is mechanically
            # repairable, and report the rest.
            repairs = _repair_engine_surface(node.surface, tuple(slot_meter_for(graph, node.phrase_id)))
            if repairs:
                engine_repairs[node.phrase_id] = repairs
            graph.commit_phrase(node.phrase_id, node.surface)

    # Phase 6b: Populate expectations from committed phrases
    try:
        for node in best_path.nodes:
            trace = all_traces.get(node.phrase_id)
            if not trace:
                continue

            # Chromatic devices used → add DEBT for tonal resolution
            if trace.devices_used:
                if cross_ledger is not None:
                    cross_ledger.add_section_expectation(
                        exp_type=ExpectationType.DEBT.value,
                        domain=ExpectationDomain.HARMONY_TONAL.value,
                        object_ref=f"tonal_resolution_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        urgency=0.6,
                        details={
                            "chromatic_devices": trace.devices_used,
                            "section": section_id,
                        },
                    )
                elif ledger is not None:
                    ledger.add_debt(
                        object_ref=f"tonal_resolution_{node.phrase_id}",
                        opened_at=node.phrase_id,
                        urgency=0.6,
                        details={
                            "chromatic_devices": trace.devices_used,
                            "section": section_id,
                        },
                    )

            # Motif/fingerprint placement → add PROMISE for motif development
            if trace.fingerprints_expressed:
                if cross_ledger is not None:
                    cross_ledger.add_section_expectation(
                        exp_type=ExpectationType.PROMISE.value,
                        domain=ExpectationDomain.MOTIF_THEME.value,
                        object_ref=f"motif_development_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        expected_form="motif development or return",
                        urgency=0.5,
                        details={
                            "fingerprints": trace.fingerprints_expressed,
                            "section": section_id,
                        },
                    )
                elif ledger is not None:
                    ledger.add_promise(
                        object_ref=f"motif_development_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        expected_form="motif development or return",
                        urgency=0.5,
                        details={
                            "fingerprints": trace.fingerprints_expressed,
                            "section": section_id,
                        },
                    )
    except Exception:
        pass  # Ledger not available — skip gracefully

    # Phase 7 (v6): Compute context utilization + enforce minimum context
    cu_report = None
    anti_results: List[Dict] = []
    context_violations: List[str] = []
    if style_program and all_traces:
        tier = style_program.dna.tier if style_program.dna else "D"

        # Run anti-pattern detection on committed surfaces
        prev_layer = None
        for node in best_path.nodes:
            if node.surface:
                results = run_all_detectors(node.surface, style_program.anti_patterns, prev_layer)
                anti_results.extend(results)
                prev_layer = node.surface

        cu_report = compute_utilization(
            all_traces,
            style_program.fingerprint_contract,
            anti_results,
            tier,
        )
        graph.context_traces = all_traces
        graph.context_utilization = cu_report

        # Enforce minimum context package per phrase (informational)
        fallback_budgets = {"A": 0.10, "B": 0.20, "C": 0.35, "D": 1.0}
        budget = fallback_budgets.get(tier, 1.0)
        for pid, trace in all_traces.items():
            fallback_ratio = trace.fallback_bar_count / max(trace.total_bar_count, 1)
            if fallback_ratio > budget:
                context_violations.append(
                    f"{pid}: fallback ratio {fallback_ratio:.0%} exceeds budget {budget:.0%}"
                )
            if (
                not trace.corpus_patterns_used
                and not trace.corpus_bars_used
                and not trace.gestures_applied
            ):
                context_violations.append(f"{pid}: no corpus reference (pattern, bar, or gesture)")

        # Run craft checks on committed surfaces
        if cc:
            for node in best_path.nodes:
                if node.surface:
                    ps = graph.phrases.get(node.phrase_id)
                    if ps:
                        ps.craft_check = cc.check(node.surface)

    graph.phase = PipelinePhase.REALIZING.value

    # Persist the cross-scale ledger so musical promises/debts carry
    # forward to later sections and movements
    if cross_ledger is not None:
        try:
            graph.cross_scale_ledger = cross_ledger.to_dict()
        except Exception:
            pass

    graph.save(str(workspace / "piece_graph.json"))

    result: Dict[str, Any] = {
        "section_id": section_id,
        "phrases_realized": len(best_path.nodes),
        "path_score": best_path.total_score,
        "transition_scores": best_path.transition_scores,
        "pipeline": "v6" if (sc and style_program) else "classic",
    }
    if engine_repairs:
        # Never silent. A repaired surface means the generator produced
        # something that could not be engraved, and the caller should see it.
        result["engine_repairs"] = engine_repairs
        _LOG.warning("engine surface repairs in %s: %s", section_id, engine_repairs)

    if cu_report:
        result["context_utilization"] = {
            "corpus_coverage": cu_report.corpus_coverage,
            "fallback_ratio": cu_report.fallback_ratio,
            "fingerprint_coverage": cu_report.fingerprint_coverage,
            "anti_patterns_detected": cu_report.anti_patterns_detected,
            "gestures_applied": cu_report.gestures_applied,
            "breathing_rules_applied": cu_report.breathing_rules_applied,
        }
        # The corpus-utilization floor is a GATE, not a footnote: a section
        # that exceeds its tier's fallback budget or contains phrases with no
        # corpus reference at all has not met the corpus-armed bar and must be
        # re-armed / re-composed before it is treated as done.
        result["context_gate"] = {
            "passed": not context_violations,
            "tier": tier,
            "violations": context_violations,
        }
        if context_violations:
            result["needs_attention"] = (
                f"context_gate FAILED for tier {tier}: {len(context_violations)} "
                f"phrase(s) under-used the corpus (see context_gate.violations). "
                f"Arm the composer (acquire_composer.py) or re-compose the "
                f"flagged phrases — do not treat this section as complete."
            )

    if run_style_gate:
        try:
            result["style_review"] = run_style_review_section(
                piece_id,
                section_id,
                threshold=0.35,
                persist=True,
            )
        except Exception as exc:
            result["style_review"] = {"error": str(exc)}

    return result


# ─── Form Builders ───────────────────────────────────────────────────────────


# ─── Form specifications ─────────────────────────────────────────────────────
#
# A form is DATA: an ordered list of phrase specs. Every form used to be built
# from identical 8-bar phrases (ternary = 8+8 | 8+8 | 8+8; theme-and-variations
# = 8+8 per variation), which puts a cadence in every eighth bar for the whole
# piece. Uniform phrase rhythm is one of the strongest machine tells there is —
# real classical phrases run 4, 5, 6, 8, 10 bars, extend, elide, and are
# answered by asymmetric consequents. These specs give each form its own phrase
# rhythm, and the key roles are resolved through the interval helpers so any
# key spelling works.
#
# Each entry: (section, bars, function, cadence, key_role)
#   key_role ∈ tonic | relative | dominant | subdominant | parallel

_PF = PhraseFunction
_CT = CadenceTarget

# A cadence at the end of every phrase is a cadence every four to six bars for
# the whole piece, which is a metronome at the structural level. Real phrases run
# INTO one another: a continuation that is spinning the idea out does not stop to
# cadence, it evades or simply carries on (CT.NONE), and only the structural
# arrivals — the end of a section, the confirmation, the close — actually land.
_TERNARY_SPEC = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.NONE.value, "tonic"),  # runs on
    ("m1_a", 6, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "relative"),
    ("m1_b", 5, _PF.CONTINUATION.value, _CT.IAC.value, "relative"),
    ("m1_retr", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_a2", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),  # elides into the drive
    ("m1_a2", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ("m1_coda", 4, _PF.CODA.value, _CT.PLAGAL.value, "tonic"),
]

# A complete sonata movement: exposition, development, recapitulation, coda.
# Building only the exposition (as before) meant asking for sonata form got a
# fragment that stops after the closing theme, in the wrong key, with the
# development's promised recapitulation never arriving.
_SONATA_SPEC = [
    ("m1_pt", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_pt", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_tr", 6, _PF.TRANSITION.value, _CT.EVADED.value, "dominant"),
    ("m1_st", 4, _PF.CONTRASTING_THEME.value, _CT.HC.value, "dominant"),
    ("m1_st", 4, _PF.CONTINUATION.value, _CT.NONE.value, "dominant"),
    ("m1_st", 5, _PF.CADENTIAL.value, _CT.PAC.value, "dominant"),
    ("m1_cl", 4, _PF.CLOSING.value, _CT.PAC.value, "dominant"),
    ("m1_dev", 6, _PF.FRAGMENTATION.value, _CT.NONE.value, "relative"),
    ("m1_dev", 8, _PF.SEQUENCE.value, _CT.NONE.value, "subdominant"),
    ("m1_dev", 6, _PF.LIQUIDATION.value, _CT.NONE.value, "parallel"),
    ("m1_dev", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_rec_pt", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),
    ("m1_rec_pt", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_rec_tr", 4, _PF.TRANSITION.value, _CT.EVADED.value, "tonic"),
    ("m1_rec_st", 4, _PF.RETURN_VARIED.value, _CT.NONE.value, "tonic"),
    ("m1_rec_st", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ("m1_coda", 6, _PF.CODA.value, _CT.PAC.value, "tonic"),
]

_SIMPLE_SPEC = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "relative"),
    ("m1_a2", 6, _PF.RETURN.value, _CT.PAC.value, "tonic"),
]

# Each variation gets its own character: a key role, a phrase rhythm, and a
# tempo scaling. Giving every variation the same key, meter, length and cadence
# plan (as before) makes a set of variations that vary nothing structural.
_VARIATION_CHARACTERS = [
    {"key_role": "tonic", "bars": (4, 4), "tempo_scale": 1.0, "label": "figural"},
    {"key_role": "parallel", "bars": (4, 6), "tempo_scale": 0.75, "label": "minore"},
    {"key_role": "tonic", "bars": (4, 5), "tempo_scale": 1.25, "label": "brillante"},
    {"key_role": "subdominant", "bars": (6, 6), "tempo_scale": 0.85, "label": "cantabile"},
]


def _key_for_role(key: str, role: str) -> str:
    """Resolve a form spec's key role against the piece's tonic."""
    fns = {
        "tonic": lambda k: k,
        "relative": _relative_key,
        "dominant": _dominant_key,
        "subdominant": _subdominant_key,
        "parallel": _parallel_key,
    }
    return fns.get(role, lambda k: k)(key)


def _build_from_spec(spec, key, tempo, meter, style) -> List[PhraseSlot]:
    """Materialize a form spec into PhraseSlots with running bar numbers."""
    phrases: List[PhraseSlot] = []
    bar = 1
    counters: Dict[str, int] = {}
    from .dramatic_plan import role_for

    for section_id, bars, fn, cad, key_role in spec:
        counters[section_id] = counters.get(section_id, 0) + 1
        slot_key = _key_for_role(key, key_role)
        # Resolve the dramatic role BEFORE the harmony is sampled: an opening
        # statement and a crisis should not be handed the same palette, and the
        # sampler cannot know which it is unless it is told.
        drole = role_for(section_id, counters[section_id] - 1)
        phrases.append(
            _make_slot(
                f"{section_id}_p{counters[section_id]}",
                section_id,
                bar,
                bars,
                fn,
                cad,
                slot_key,
                meter,
                tempo,
                style,
                dramatic_role=drole,
            )
        )
        bar += bars
    return phrases


def _build_ternary(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """ABA' ternary with a retransition and a coda, and asymmetric phrases."""
    return _build_from_spec(_TERNARY_SPEC, key, tempo, meter, style)


def _build_sonata(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """A complete sonata-allegro: exposition, development, recapitulation, coda."""
    return _build_from_spec(_SONATA_SPEC, key, tempo, meter, style)


def _build_theme_variations(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """Theme + four variations, each with its own key role, phrase rhythm and tempo."""
    spec = [
        ("m1_theme", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
        ("m1_theme", 4, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ]
    phrases = _build_from_spec(spec, key, tempo, meter, style)
    bar = sum(p.bar_count for p in phrases) + 1
    for i, character in enumerate(_VARIATION_CHARACTERS, start=1):
        section = f"m1_var{i}"
        var_key = _key_for_role(key, character["key_role"])
        var_tempo = max(30, int(round(tempo * character["tempo_scale"])))
        for j, (bars, fn, cad) in enumerate(
            (
                (character["bars"][0], _PF.RETURN_VARIED.value, _CT.HC.value),
                (character["bars"][1], _PF.CADENTIAL.value, _CT.PAC.value),
            ),
            start=1,
        ):
            slot = _make_slot(
                f"{section}_p{j}", section, bar, bars, fn, cad, var_key, meter, var_tempo, style
            )
            slot.notes = f"variation {i} — {character['label']}"
            phrases.append(slot)
            bar += bars
    return phrases


def _build_simple(
    key: str, tempo: int, meter: Tuple[int, int], form: str, style: StyleDNA
) -> List[PhraseSlot]:
    """A short song-form default for unrecognized form names."""
    return _build_from_spec(_SIMPLE_SPEC, key, tempo, meter, style)


def _make_slot(
    phrase_id: str,
    section_id: str,
    bar_start: int,
    bar_count: int,
    function: str,
    cadence: str,
    key: str,
    meter: Tuple[int, int],
    tempo: int,
    style: StyleDNA,
    dramatic_role: str = "",
) -> PhraseSlot:
    """Create a PhraseSlot with SUGGESTED harmony and texture plans.

    The harmony plan is a corpus-typical *default*, not a mandate: the agent
    chooses the actual harmony from what it learned studying the reference
    scores (the brief presents this plan as advisory). It also serves as the
    chord-frame for clash-avoidance and as input to the engine fallback when a
    phrase is left unauthored.
    """
    from .progression_model import corpus_harmony_plan

    composer_id = getattr(style, "composer_id", "") or ""
    target = getattr(style, "target", None)
    style_name = ""
    if isinstance(target, dict):
        style_name = target.get("genre") or target.get("era") or ""
    else:
        style_name = getattr(target, "genre", "") or getattr(style, "era", "") or ""
    from .pitch import is_minor_key
    from .progression_model import within_bar_detail

    harmony = corpus_harmony_plan(
        composer_id,
        style_name,
        cadence,
        bar_count,
        key,
        seed=bar_start,
        role=dramatic_role,
    ) or _default_harmony_plan(function, cadence, bar_count, minor=is_minor_key(key))

    # Where the harmony moves INSIDE each bar, from the composer's own within-bar
    # patterns. Without this the plan could only ever say one chord per bar.
    harmony_detail = within_bar_detail(
        composer_id,
        style_name,
        harmony,
        key,
        cadence,
        beats=int(meter[0] * 4 / meter[1]) if meter else 4,
        seed=bar_start,
    )

    texture_plan = _default_texture_plan(style, function, cadence, bar_count, meter, seed=bar_start)

    # Energy curve
    energy = _default_energy_curve(function, bar_count)

    return PhraseSlot(
        dramatic_role=dramatic_role,
        phrase_id=phrase_id,
        section_id=section_id,
        bar_start=bar_start,
        bar_count=bar_count,
        function=function,
        cadence_target=cadence,
        # A phrase that does not cadence has no cadence bar. Setting one anyway
        # made the density/texture plan thin at the end of EVERY phrase, which
        # put an audible comma in the music every four to six bars.
        cadence_bar=(
            bar_start + bar_count - 1 if cadence and cadence != CadenceTarget.NONE.value else None
        ),
        key=key,
        meter=meter,
        tempo_bpm=tempo,
        harmony_plan=harmony,
        harmony_detail=harmony_detail,
        texture_plan=texture_plan,
        curves=PhraseCurves(energy=energy),
    )


# How often the accompaniment changes character is a MEASURED property of the
# composer, not a policy. Two wrong answers have been shipped here: a round-robin
# (`options[i % len(options)]`) that planned a different idiom in every bar for no
# reason, and then a flat "hold one idiom for the whole phrase", which is just as
# wrong in the other direction — Mozart's own corpus changes left-hand texture on
# **62%** of bar transitions (measured over 402 bars of his 3/4 andantes), and his
# profile records lh_texture_change_pct ≈ 0.54. Holding one figure for six bars is
# the single most audible way generated music announces itself.
#
# So: take the rate from the composer's corpus profile, and take the SUCCESSOR
# from the corpus transition matrix — what that composer actually moves to next.
# Not accompaniment idioms a plan can schedule: silence is the absence of one,
# and "unclassified" is the extractor's junk bucket.
_UNSCHEDULABLE_LH = {"silence", "unclassified", ""}

_CADENCE_LH = {
    "alberti": "block_chord_sparse",
    "broken_chord_wave": "block_chord_sparse",
    "walking_bass": "block_chord_sparse",
    "block_chord_offbeat": "block_chord_sparse",
}


def _lh_change_rate(style) -> float:
    """The composer's own measured LH texture-change rate, or a neutral default."""
    from .composition_brief import corpus_profile

    composer = (getattr(style, "composer_id", "") or "").lower()
    prof = corpus_profile(composer) if composer else {}
    stat = (prof or {}).get("metrics", {}).get("lh_texture_change_pct") or {}
    mean = stat.get("mean")
    return float(mean) if isinstance(mean, (int, float)) and 0 < mean < 1 else 0.45


def _next_lh_texture(style, current: str, options: List[str], seed: int) -> str:
    """What this composer actually moves to after ``current``.

    This read ``trans["next"]`` — a key ``_transition_patterns`` has never
    returned. It returns ``after_previous.follow``. So the lookup was dead: the
    corpus transition matrix, built specifically to say what follows what, was
    never consulted, and the accompaniment simply cycled through the style's
    ranked textures by index.
    """
    from .composition_brief import _transition_patterns

    try:
        trans = _transition_patterns(getattr(style, "composer_id", "") or "", None, current)
        follow = ((trans or {}).get("after_previous") or {}).get("follow") or []
        ranked = [t for t, _w in follow if t != current and t not in _UNSCHEDULABLE_LH]
        if ranked:
            return ranked[seed % min(3, len(ranked))]
    except Exception:
        pass
    alt = [t for t in options if t != current and t not in _UNSCHEDULABLE_LH]
    return alt[seed % len(alt)] if alt else current


def _rh_change_rate(style) -> float:
    """The composer's own measured RH texture-change rate."""
    from .composition_brief import corpus_profile

    composer = (getattr(style, "composer_id", "") or "").lower()
    prof = corpus_profile(composer) if composer else {}
    stat = (prof or {}).get("metrics", {}).get("texture_change_pct") or {}
    mean = stat.get("mean")
    return float(mean) if isinstance(mean, (int, float)) and 0 < mean < 1 else 0.35


def _default_texture_plan(
    style, function: str, cadence: str, bar_count: int, meter, seed: int = 0
) -> List:
    """Plan the accompaniment's character bar by bar at the composer's own rate.

    Density targets scale with the bar's real beat count and the chosen texture
    rather than being the same hard-coded 8-RH / 6-LH for every bar of every
    piece in every meter.
    """

    def _ranked(dist, fallback, min_share: float = 0.05):
        """Textures this composer actually uses often, commonest first.

        The tail is dropped: rotating through the WHOLE ranked list reached
        idioms a composer uses in 1% of bars, so a tender andante's second phrase
        was planned as passage-work. Variety should stay inside the composer's
        mainstream vocabulary, not sample its extremes.
        """
        if not dist:
            return [fallback]
        ranked = sorted(dist.items(), key=lambda kv: -kv[1])
        total = sum(v for _, v in ranked) or 1.0
        keep = [k for k, v in ranked if (v / total) >= min_share]
        return keep or [ranked[0][0]] or [fallback]

    rh_opts = _ranked(getattr(style, "rh_distribution", None), TextureType.SINGING_MELODY.value)
    lh_opts = _ranked(getattr(style, "lh_distribution", None), AccompType.ALBERTI.value)
    # "silence" is a real corpus label (the staff rests for a bar) but it is not
    # something to PLAN as a phrase's accompaniment idiom — a phrase whose plan
    # opens on silence has no accompaniment at all. It was filtered out of the
    # successor choice and not out of the initial pick.
    rh_opts = [t for t in rh_opts if t not in _UNSCHEDULABLE_LH] or [
        TextureType.SINGING_MELODY.value
    ]
    lh_opts = [t for t in lh_opts if t not in _UNSCHEDULABLE_LH] or [AccompType.ALBERTI.value]
    # Every phrase used to START on the style's single most common texture and
    # accrue its changes from zero, so phrase 1 and phrase 9 of the same piece
    # were planned identically: alberti, alberti, then a change at the same bar
    # index, over and over. That IS the "same accompaniment throughout" tell the
    # brief warns about, planned in. Offsetting both the starting texture and the
    # accrual phase by where the phrase sits in the piece makes each phrase begin
    # somewhere the previous one did not, while still following the composer's
    # own distribution and change rate.
    offset = max(0, int(seed))
    # The opening states the norm — a piece should not begin on its composer's
    # fourth-commonest texture — and a RETURN should recall how the material
    # first sounded rather than arriving in a texture the listener has never
    # associated with it.
    anchored = offset <= 1 or (function or "").lower() in ("return", "recapitulation", "coda")
    step = 0 if anchored else (offset // 4)
    rh = rh_opts[step % len(rh_opts)]
    lh = lh_opts[step % len(lh_opts)]
    rate = _lh_change_rate(style)
    rh_rate_of_change = _rh_change_rate(style)

    beats = (meter[0] * 4.0 / meter[1]) if meter else 4.0
    rh_rate = {
        "held_note": 0.35,
        "singing_melody": 1.2,
        "chordal": 1.0,
        "block_chord_sparse": 0.6,
        "scalar_run": 3.0,
        "zigzag_figuration": 3.0,
        "passage_work": 3.0,
        "dotted_pairs": 1.5,
        "dialogue": 1.2,
        "ornamental_cascade": 3.5,
    }
    lh_rate = {
        "silence": 0.0,
        "pedal_point": 0.4,
        "block_chord_sparse": 0.7,
        "block_chord_offbeat": 1.2,
        "bass_melody": 1.0,
        "walking_bass": 1.2,
        "alberti": 2.0,
        "broken_chord_wave": 2.0,
        "broken_chord_asc": 2.0,
        "broken_chord_desc": 2.0,
        "interlocking": 2.0,
        "block_chord_tremolo": 3.0,
        "sparse_punctuation": 0.6,
    }
    cadence_bar = bar_count - 1 if cadence and cadence != CadenceTarget.NONE.value else -1

    plan = []
    accrued = 0.0 if anchored else (offset * 0.37) % 1.0
    rh_accrued = 0.0 if anchored else (offset * 0.61) % 1.0
    for i in range(bar_count):
        is_cadence = i == cadence_bar
        if i and not is_cadence:
            # Deterministic pacing: change once the accumulated rate crosses 1,
            # which lands the phrase's change COUNT on the composer's own rate.
            accrued += rate
            if accrued >= 1.0:
                accrued -= 1.0
                lh = _next_lh_texture(style, lh, lh_opts, i + offset)
            # The UPPER staff was pinned to one texture for the whole phrase —
            # so every bar retrieved the same exemplars and got the same density
            # target, while the brief printed the composer's real
            # texture_change_pct right underneath as a target to hit. A phrase
            # cannot change texture 40% of the time if the plan says it never
            # changes at all.
            rh_accrued += rh_rate_of_change
            if rh_accrued >= 1.0 and len(rh_opts) > 1:
                rh_accrued -= 1.0
                alt = [t for t in rh_opts if t != rh]
                rh = alt[(i + offset) % len(alt)]
        bar_lh = _CADENCE_LH.get(lh, lh) if is_cadence else lh
        # Not every cadence is a held note. Alternating the two idiomatic
        # cadential upper-staff gestures stops every phrase in every piece from
        # ending the same way.
        bar_rh = rh
        if is_cadence and rh not in ("held_note", "chordal"):
            bar_rh = "chordal" if (bar_count % 2 == 0) else "held_note"
        plan.append(
            BarTexturePlan(
                rh_texture=bar_rh,
                lh_texture=bar_lh,
                rh_density_target=max(
                    1, round(beats * (0.4 if is_cadence else rh_rate.get(bar_rh, 1.2)))
                ),
                lh_density_target=max(
                    1, round(beats * (0.5 if is_cadence else lh_rate.get(bar_lh, 1.5)))
                ),
            )
        )
    return plan


def _default_harmony_plan(
    function: str, cadence: str, bar_count: int, minor: bool = False
) -> List[str]:
    """Fallback harmony plan when the corpus model has nothing for this composer.

    Built as opening + middle + CADENCE rather than by slicing a fixed 8-bar
    template: slicing dropped the dominant out of any phrase that was not
    exactly eight bars, so a six-bar phrase asked for a perfect cadence and got
    tonic-tonic. Mode-aware too — the old version handed a phrase in A minor an
    A MAJOR tonic and a major supertonic.
    """
    if bar_count <= 0:
        return []
    tonic = "i" if minor else "I"
    sub = "iv" if minor else "IV"
    supertonic = "iio6" if minor else "ii6"
    submediant = "VI" if minor else "vi"

    dom7 = "V" if minor else "V7"
    # EVADED and ELIDED had no entry, so they fell through to an empty tail and
    # the phrase ended wherever the functional walk happened to be — no dominant,
    # no arrival, nothing to evade.
    tails = {
        CadenceTarget.PAC.value: [dom7, tonic],
        CadenceTarget.IAC.value: ["V", tonic + "6"],
        CadenceTarget.HC.value: [supertonic, "V"],
        CadenceTarget.DC.value: [dom7, submediant],
        CadenceTarget.PLAGAL.value: [sub, tonic],
        CadenceTarget.EVADED.value: [dom7, tonic + "6"],
        CadenceTarget.ELIDED.value: [supertonic, tonic + "6"],
    }
    tail = tails.get(cadence, [])
    if bar_count <= len(tail):
        return tail[-bar_count:]

    # Middle: a functional walk out from the tonic and back to the predominant,
    # long enough to fill whatever is left once the cadence is reserved.
    walk = [tonic, submediant, sub, supertonic, tonic, sub]
    body = [tonic]
    i = 0
    while len(body) < bar_count - len(tail):
        body.append(walk[i % len(walk)])
        i += 1
    return body + tail


def _default_energy_curve(function: str, bar_count: int) -> List[float]:
    """Generate a default energy curve."""
    if function in (PhraseFunction.PRESENTATION.value, PhraseFunction.RETURN.value):
        # Gentle arch
        return [0.4 + 0.3 * (i / bar_count) for i in range(bar_count)]
    if function == PhraseFunction.CADENTIAL.value:
        # Build to peak then resolve
        peak = bar_count * 2 // 3
        return [
            0.5 + 0.3 * (i / peak) if i <= peak else 0.8 - 0.3 * ((i - peak) / (bar_count - peak))
            for i in range(bar_count)
        ]
    if function == PhraseFunction.CONTRASTING_THEME.value:
        # Gentle, lower energy
        return [0.3 + 0.2 * (i / bar_count) for i in range(bar_count)]
    return [0.5] * bar_count


def _sample_curve(curve: List[float], frac: float) -> Optional[float]:
    """Linear-sample a per-section curve list at fractional position frac∈[0,1]."""
    if not curve:
        return None
    if len(curve) == 1:
        return float(curve[0])
    frac = max(0.0, min(1.0, frac))
    x = frac * (len(curve) - 1)
    lo = int(x)
    hi = min(lo + 1, len(curve) - 1)
    t = x - lo
    return float(curve[lo] * (1 - t) + curve[hi] * t)


def _apply_narrative_curves(slot: PhraseSlot, narrative) -> bool:
    """Interpolate the covering NarrativeSection's curves into the slot's
    PhraseCurves, one value per bar — the keystone wiring that lets the planned
    emotional arc actually drive dynamics, density targets, and the tempo arc.

    Falls back silently (keeps the function-default energy curve) when no
    narrative exists or no section covers the slot. Returns True if it applied.
    """
    if narrative is None or not getattr(narrative, "sections", None):
        return False
    sections = narrative.sections
    energy, tension, density, brightness = [], [], [], []
    covered = False
    for i in range(slot.bar_count):
        gbar = slot.bar_start + i
        sec = next((s for s in sections if s.bar_start <= gbar <= s.bar_end), None)
        prev_e = slot.curves.energy[i] if i < len(slot.curves.energy) else 0.5
        if sec is None:
            energy.append(prev_e)
            tension.append(0.5)
            density.append(0.5)
            brightness.append(0.5)
            continue
        covered = True
        span = max(1, sec.bar_end - sec.bar_start)
        frac = (gbar - sec.bar_start) / span
        e = _sample_curve(sec.energy_curve, frac)
        energy.append(e if e is not None else prev_e)
        tension.append(_sample_curve(sec.tension_curve, frac) or 0.5)
        density.append(_sample_curve(sec.density_curve, frac) or 0.5)
        brightness.append(_sample_curve(sec.brightness_curve, frac) or 0.5)
    if not covered:
        return False
    # Only override the default energy when the narrative actually supplied it.
    if any(s.energy_curve for s in sections):
        slot.curves.energy = energy
    slot.curves.tension = tension
    slot.curves.density = density
    slot.curves.brightness = brightness

    # Drive note density per bar from the narrative density curve (not just
    # dynamics) — low density → sparser/sustained texture, high → fuller/running.
    for i, bt in enumerate(getattr(slot, "texture_plan", []) or []):
        d = density[i] if i < len(density) else 0.5
        bt.rh_density_target = int(round(4 + 12 * d))
        bt.lh_density_target = int(round(3 + 7 * d))
    return True


def _parse_key_str(key: str):
    """Delegates to the single canonical parser (pitch.parse_key)."""
    from .pitch import parse_key

    return parse_key(key)


def _key_name(key_obj) -> str:
    """Render a music21 Key back to the project's canonical "<Tonic> <mode>" form."""
    tonic = key_obj.tonic.name.replace("-", "b")
    return f"{tonic} {key_obj.mode}"


def _transpose_key(key: str, interval_name: str, mode: Optional[str] = None) -> str:
    """Transpose a key by a NAMED interval, optionally switching mode.

    Replaces two hard-coded lookup tables that silently returned "C"/"Am"/"G"
    for any key spelling they did not contain — which was ALL of them once the
    planner started writing "a minor" instead of "Am", so every ternary B
    section and every sonata secondary theme landed in the wrong key.

    The interval is named ("P5", "m3") rather than a semitone count so the
    spelling stays diatonic: the dominant of D-flat is A-flat, not G-sharp.
    """
    import music21

    k = _parse_key_str(key)
    new_tonic = k.tonic.transpose(music21.interval.Interval(interval_name))
    return _key_name(music21.key.Key(new_tonic.name, mode or k.mode))


def _relative_key(key: str) -> str:
    """The relative major of a minor key, or the relative minor of a major key."""
    k = _parse_key_str(key)
    if k.mode == "minor":
        return _transpose_key(key, "m3", "major")
    return _transpose_key(key, "-m3", "minor")


def _dominant_key(key: str) -> str:
    """The key a sonata exposition's secondary theme goes to.

    Major: the dominant. Minor: the RELATIVE MAJOR — a minor-mode exposition
    that modulates to the minor dominant is the exception, not the rule, and the
    old table did exactly that for every minor key.
    """
    k = _parse_key_str(key)
    if k.mode == "minor":
        return _relative_key(key)
    return _transpose_key(key, "P5")


def _subdominant_key(key: str) -> str:
    return _transpose_key(key, "P4")


def _parallel_key(key: str) -> str:
    k = _parse_key_str(key)
    return _transpose_key(key, "P1", "major" if k.mode == "minor" else "minor")


def _infer_section_role(section_id: str) -> str:
    """Infer section role from its ID naming convention."""
    sid = section_id.lower()
    if "pt" in sid or "expo" in sid:
        return "exposition"
    if "dev" in sid:
        return "development"
    if "recap" in sid:
        return "recapitulation"
    if "coda" in sid:
        return "coda"
    if "_a" in sid and "_a2" not in sid:
        return "A"
    if "_b" in sid:
        return "B"
    if "_a2" in sid or "return" in sid:
        return "A_return"
    if "tr" in sid:
        return "transition"
    if "st" in sid:
        return "secondary_theme"
    if "cl" in sid:
        return "closing"
    return "A"


# ─── Work-Level Planning (multi-movement) ──────────────────────────────────


def init_work(
    piece_id: str,
    movement_count: int,
    description: str = "",
    emotional_narrative: str = "",
    finale_payoff: str = "",
) -> Dict[str, Any]:
    """Create a WorkGraph for multi-movement works.

    This is WHERE Wolfgang decides the symphony's dramatic destiny.
    """
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    from .models import TonalItinerary

    # Handle contract possibly being a dict (from JSON deserialization)
    home_key = "C"
    if hasattr(graph.contract, "target"):
        target = graph.contract.target
        if hasattr(target, "instrumentation"):
            home_key = target.instrumentation or "C"
    work = WorkGraph(
        work_id=piece_id,
        movement_count=movement_count,
        emotional_narrative=emotional_narrative,
        finale_payoff=finale_payoff,
        tonal_itinerary=TonalItinerary(home_key=home_key),
    )
    graph.work_graph = work
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "work_id": piece_id,
        "movement_count": movement_count,
        "emotional_narrative": emotional_narrative,
    }


def plan_movement(
    piece_id: str,
    movement_id: str,
    form: str,
    key: str,
    tempo_bpm: int = 120,
    meter: Tuple[int, int] = (4, 4),
    character: str = "",
    role_in_work: str = "",
    tempo_marking: str = "",
) -> Dict[str, Any]:
    """Add a MovementContract to the WorkGraph."""
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    if not graph.work_graph:
        return {"error": "No WorkGraph found — call init_work first"}

    movement = MovementContract(
        id=movement_id,
        form=form,
        key=key,
        tempo_bpm=tempo_bpm,
        meter=meter,
        tempo_marking=tempo_marking,
        character=character,
        role_in_work=role_in_work,
    )
    graph.work_graph.movements.append(movement)
    graph.work_graph.tonal_itinerary.movement_keys[movement_id] = key
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "movement_id": movement_id,
        "form": form,
        "key": key,
        "character": character,
    }


# ─── Revision Support ──────────────────────────────────────────────────────


def apply_revision(piece_id: str, section_id: str, revision_ops: List[Dict]) -> Dict[str, Any]:
    """Apply a RevisionScript to a section using the PatchEngine.

    Each op is a dict with: target_phrase, operation, params, reason.
    """
    revision_ops = _as_list(revision_ops, "revision_ops")
    from .models import RevisionOp, RevisionScript
    from .patch_engine import PatchEngine

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))

    ops = [
        RevisionOp(
            target_phrase=op.get("target_phrase", ""),
            target_layer=op.get("target_layer"),
            target_bars=tuple(op["target_bars"]) if op.get("target_bars") else None,
            operation=op.get("operation", ""),
            params=op.get("params", {}),
            reason=op.get("reason", ""),
        )
        for op in revision_ops
    ]
    script = RevisionScript(section_id=section_id, ops=ops)

    engine = PatchEngine()
    phrase_order = graph.get_section_phrases(section_id)
    affected = engine.identify_affected_phrases(script, phrase_order)

    for op in ops:
        if op.target_phrase and op.target_phrase in graph.phrases:
            graph.phrases[op.target_phrase] = engine.apply_revision_op(
                op, graph.phrases[op.target_phrase]
            )

    warnings = engine.validate_edit_coherence(affected, phrase_order)
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "affected_phrases": affected,
        "warnings": warnings,
        "needs_recomposition": [
            pid
            for pid in affected
            if graph.phrases.get(pid) and graph.phrases[pid].status in ("planned", "sketched")
        ],
    }


# ─── Engraver's pass ─────────────────────────────────────────────────────────


def _engrave_phrase(graph, phrase_id: str, layer: LayerIR, composer: Optional[str]):
    """Run the engraver's pass over a phrase the agent just wrote.

    `expression_enricher` existed, was fully tested, and was called by nothing.
    Every score the system produced therefore came out with **zero
    articulations and zero ties** where a real Mozart sonata movement carries
    0.27-1.74 articulations and up to 0.89 ties per bar (measured over the nine
    first movements in `reference_scores/mozart-piano-sonatas`). An
    unarticulated score sounds like a MIDI file because it is one.

    The pass is strictly non-destructive: it writes only fields the composer
    left blank, so the agent stays the author and this is the engraver who
    follows it. The report is stored on the phrase so a reviewer can tell the
    two apart.
    """
    from .expression_enricher import enrich_layer_ir, expression_density

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None

    style_name = composer or getattr(graph.style_dna, "composer_id", "") or ""
    curves = getattr(slot, "curves", None) if slot else None
    energy = list(getattr(curves, "energy", []) or []) if curves else None
    harmony = list(getattr(slot, "harmony_plan", []) or []) if slot else None
    cadence_bar = getattr(slot, "cadence_bar", None) if slot else None
    character = (getattr(slot, "notes", "") or "") if slot else ""
    base_dyn = None
    cont = getattr(slot, "continuation", None) if slot else None
    if cont is not None:
        base_dyn = getattr(cont, "last_dynamic", None)

    try:
        report = enrich_layer_ir(
            layer,
            style=style_name,
            energy_curve=energy,
            harmony_plan=harmony,
            cadence_bar=cadence_bar,
            base_dynamic=base_dyn,
            character=character,
            is_final_phrase=_is_final_phrase(graph, phrase_id),
        )
    except Exception as exc:  # never let the engraver block a good commit
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    out = report.as_dict()
    out["density_after"] = expression_density(layer)
    return out


def _is_final_phrase(graph, phrase_id: str) -> bool:
    """True when no later phrase exists anywhere in the piece."""
    order = list(graph.phrases.keys())
    try:
        return order.index(phrase_id) == len(order) - 1
    except ValueError:
        return False


def _gated_commit(
    graph,
    workspace: Path,
    phrase_id: str,
    layer: LayerIR,
    allow: Optional[List[Dict[str, str]]],
    composer: Optional[str],
) -> Dict[str, Any]:
    """Shared gate + commit path for both agent commit entry points.

    Enforces (in order): the brief receipt (a phrase cannot be committed unless
    its brief was fetched), then the blocking quality gate (density, figuration,
    corpus alignment). Both are hard — there is no gate-bypass flag."""
    from .commit_gate import run_commit_gate
    from .models import RevisionEntry

    # 1. Brief receipt requirement — never compose blind without a brief.
    state = graph.phrases.get(phrase_id)
    trace = getattr(state, "context_trace", None) if state else None
    trace = trace if isinstance(trace, dict) else {}
    waived = {
        str(w.get("check", "")).strip()
        for w in (allow or [])
        if str(w.get("check", "")).strip() and str(w.get("reason", "")).strip()
    }
    if not trace.get("brief_fetched"):
        return {
            "ok": False,
            "error": "brief_not_fetched",
            "hint": (
                "Call get_composition_brief(piece_id, phrase_id) for this "
                "phrase BEFORE composing. The brief's real corpus exemplars "
                "are mandatory — the commit gate will not accept a surface "
                "composed without one."
            ),
        }
    if trace.get("brief_insufficient") and "brief_insufficient" not in waived:
        return {
            "ok": False,
            "error": "brief_insufficient",
            "hint": (
                "The corpus yielded NO exemplars for this phrase, so the "
                "brief cannot anchor the writing. Arm the composer with "
                "real scores (tools/scripts/acquire_composer.py <composer>) "
                "and re-fetch the brief, or — if composing without corpus "
                "support is a deliberate choice — recommit with "
                "allow=[{'check': 'brief_insufficient', 'reason': '...'}]."
            ),
        }

    # 2. Blocking quality gate (density, figuration, corpus alignment, meter).
    gate = run_commit_gate(graph, phrase_id, layer, allow=allow, composer=composer)
    if not gate.passed:
        return {
            "ok": False,
            "error": "quality_gate_blocked",
            "blocking": [d.to_dict() for d in gate.blocking],
            "warnings": [d.to_dict() for d in gate.warnings],
            "rejected_waivers": gate.rejected_waivers,
            "hint": (
                "Revise the flagged bars and recommit, or — if the "
                "choice is genuinely intentional — recommit with "
                "allow=[{'check': '<name>', 'reason': '<musical "
                "justification>'}]. Physical constraints cannot "
                "be waived."
            ),
        }

    # 3. Engraver's pass — fill in the marks the composer left blank.
    #    Non-destructive; only blank fields are written.
    engraving = _engrave_phrase(graph, phrase_id, layer, composer)

    graph.commit_agent_phrase(phrase_id, layer)

    # 4. Craft checklist. This ran only inside `run_scales_section` — the ENGINE
    #    FALLBACK path — so it never saw a single agent-authored phrase, which
    #    is the path every piece actually takes. The checks ask the questions a
    #    composer asks of their own bar (does the melody make a claim, does the
    #    rhythm have an identity, does the bass have a purpose, does the phrase
    #    breathe, is there one detail worth remembering) and they are advisory:
    #    a phrase may fail one deliberately.
    craft = _craft_check_phrase(graph, phrase_id, layer)

    # 5. Hand the next phrase what it needs to continue from this one.
    _record_continuation(graph, phrase_id)

    # Capture the piece's principal theme from the first phrase whose dramatic
    # role is to state it. The theme machinery was entirely inert on the default
    # path: `motif_bank` is empty at plan time so no theme was ever elected, and
    # `capture_theme_surface` was called only by one optional workflow — so every
    # later phrase's brief had no theme to develop and a piece came out as N
    # independently-composed phrases with nothing binding them.
    _capture_theme_if_first_statement(graph, phrase_id)
    _settle_expectations(graph, phrase_id)

    # Overrides are auditable: every waived check lands in the history
    for ov in gate.overrides:
        graph.revision_history.append(
            RevisionEntry(
                timestamp=_now_iso(),
                skill="commit_gate",
                path=f"phrases.{phrase_id}",
                operation=f"override:{ov['check']}",
                reason=ov.get("reason", ""),
            )
        )

    graph.save(str(workspace / "piece_graph.json"))
    out: Dict[str, Any] = {"ok": True, "phrase_id": phrase_id, "agent_authored": True}
    out["gate"] = {
        "warnings": [d.to_dict() for d in gate.warnings],
        "overrides": gate.overrides,
        "rejected_waivers": gate.rejected_waivers,
    }
    out["engraving"] = engraving
    if craft:
        out["craft"] = craft
    return out


def _settle_expectations(graph, phrase_id: str) -> None:
    """Close the obligations this phrase discharges, on commit.

    The ledger had a ``satisfy`` method on both implementations and NOTHING in
    the project ever called it. Expectations were recorded at plan time and never
    resolved, so every debt stayed open for the whole piece and the brief's
    ledger section only ever grew — which is not a working memory, it is a list
    that gets longer. A composer told to resolve a cadence it already resolved
    four phrases ago learns to ignore the section.

    A section's cadence debt is discharged by the LAST phrase of that section
    (that is where its cadence lands); a theme-return promise by the first
    committed phrase of a section whose role is a return.
    """
    from .cross_scale_ledger import ensure_ledger, persist_ledger

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    if slot is None:
        return
    section_id = slot.section_id or ""
    order = graph.get_section_phrases(section_id) or []
    is_last_of_section = bool(order) and order[-1] == phrase_id
    role = _infer_section_role(section_id).lower()
    is_return = any(k in role for k in ("recap", "rec_", "a2", "return", "reprise"))

    try:
        ledger = ensure_ledger(graph)
    except Exception:
        return
    settled = False
    for exp in list(getattr(ledger, "expectations", []) or []):
        if getattr(exp, "status", "") != "open":
            continue
        ref = str(getattr(exp, "object_ref", "") or "")
        if is_last_of_section and ref == f"cadence_resolution_{section_id}":
            settled |= bool(ledger.satisfy(exp.id, phrase_id))
        elif is_return and ref.startswith("theme_recap_after_"):
            settled |= bool(ledger.satisfy(exp.id, phrase_id))
    if settled:
        persist_ledger(graph, ledger)


def _record_continuation(graph, phrase_id: str) -> None:
    """Hand the NEXT phrase what it needs to continue from this one.

    `ContinuationContext` declares thirteen fields and **nothing anywhere in the
    system ever set one**. Every phrase slot carried the default, so every field
    was None, and the brief's continuation block never rendered for any piece.
    Cross-phrase continuity ran on two values computed ad-hoc from the previous
    phrase's tail — which is why a phrase could not know the register the melody
    had been sitting in, how dense the texture had been, what the accompaniment
    was doing, or which motifs had already been stated.

    Written onto the FOLLOWING phrase's slot, at commit, from the phrase that
    was just committed.
    """
    from .models import ContinuationContext

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    layer = getattr(state, "realized", None) if state else None
    if slot is None or layer is None:
        return

    here = slot.bar_start or 0
    following = [
        (ps.slot.bar_start, pid, ps)
        for pid, ps in graph.phrases.items()
        if ps.slot and (ps.slot.bar_start or 0) > here
    ]
    if not following:
        return
    _, _next_id, nxt = min(following, key=lambda t: t[0])

    melody = [e for e in (layer.principal_line or []) if e.pitch != "rest"]
    bass = [e for e in (layer.bass_foundation or []) if e.pitch != "rest"]
    last_bar = max((e.bar for e in (layer.principal_line or [])), default=here)

    contour = None
    if len(melody) >= 3:
        from .pitch import pitch_to_midi

        tail = []
        for e in melody[-4:]:
            try:
                tail.append(pitch_to_midi(e.pitch if isinstance(e.pitch, str) else e.pitch[-1]))
            except (ValueError, KeyError, TypeError):
                pass
        if len(tail) >= 3:
            rise = tail[-1] - tail[0]
            peaked = max(tail) > max(tail[0], tail[-1])
            if peaked:
                contour = "arch"
            elif rise > 1:
                contour = "rising"
            elif rise < -1:
                contour = "falling"
            else:
                contour = "static"

    def _density(events) -> Optional[float]:
        in_bar = [e for e in events if e.bar == last_bar and e.pitch != "rest"]
        return float(len(in_bar)) if in_bar else None

    textures = list(getattr(slot, "texture_plan", None) or [])
    cadence = str(getattr(slot, "cadence_target", "") or "")
    transforms = list(getattr(slot, "motif_transforms", None) or [])

    nxt.slot.continuation = ContinuationContext(
        last_soprano_pitch=(melody[-1].pitch if melody else None),
        last_bass_pitch=(bass[-1].pitch if bass else None),
        last_soprano_contour=contour,
        last_chord=(list(getattr(slot, "harmony_plan", None) or []) or [None])[-1],
        last_key=slot.key,
        # A half cadence leaves the dominant hanging: that IS the pending
        # resolution, and the next phrase is the one that owes it.
        pending_resolution=("dominant" if cadence in ("HC", "half") else None),
        last_rh_density=_density(layer.principal_line or []),
        last_lh_density=_density((layer.bass_foundation or []) + (layer.response_layer or [])),
        last_rh_texture=(getattr(textures[-1], "rh_texture", None) if textures else None),
        last_lh_texture=(getattr(textures[-1], "lh_texture", None) if textures else None),
        last_dynamic=next(
            (e.dynamic for e in reversed(layer.principal_line or []) if e.dynamic), None
        ),
        motifs_stated=[
            str(getattr(t, "motif_id", t)) for t in transforms if getattr(t, "op", "") == "state"
        ],
        motifs_developed=[
            str(getattr(t, "motif_id", t)) for t in transforms if getattr(t, "op", "") != "state"
        ],
    )


def _craft_check_phrase(graph, phrase_id: str, layer: LayerIR) -> Optional[Dict[str, Any]]:
    """Run the craft checklist over a just-committed agent surface.

    Returns the failed checks with what each one is asking, or None when the
    phrase satisfies all of them. Advisory: a phrase may fail one on purpose
    (a deliberately static bass under a moving melody, a phrase with no rest
    because it elides into the next).
    """
    from .craft_checker import CraftChecker

    state = graph.phrases.get(phrase_id)
    if state is None:
        return None
    try:
        result = CraftChecker().check(
            layer,
            control=getattr(state, "control", None),
            bundles=getattr(state, "onset_bundles", None),
        )
    except Exception as exc:  # a checklist must never block a good commit
        return {"error": f"{type(exc).__name__}: {exc}"}
    state.craft_check = result

    asks = {
        "melodic_claim_clear": "the melody makes a claim rather than filling time",
        "rhythm_has_identity": "the rhythm is a shape, not an even stream",
        "bass_has_purpose": "the bass is a line, not a series of roots",
        "harmony_is_voiced": "the harmony is voiced, not implied",
        "has_breath_point": "the phrase breathes somewhere",
        "accompaniment_responds_to_melody": "the accompaniment answers the melody",
        "entry_exit_earned": "the phrase's entry and exit are prepared",
        "has_memorable_detail": "one detail is worth remembering",
        "all_notes_justified": "every note has a reason",
    }
    failed = [
        {"check": name, "asks": text}
        for name, text in asks.items()
        if getattr(result, name, True) is False
    ]
    return {"failed": failed, "passed": len(asks) - len(failed), "of": len(asks)} if failed else None


def slot_meter_for(graph, phrase_id: str) -> Tuple[int, int]:
    """The meter a phrase is written in (4/4 when the slot does not say)."""
    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    meter = getattr(slot, "meter", None) if slot else None
    return tuple(meter) if meter else (4, 4)


# The finest grid every notatable duration lands on exactly. The denominators in
# DURATION_VALUES are 1,2,3,4,5,6,7,8,12,16 and their LCM is 1680, so a position
# snapped here can always be bracketed.
#
# This started at 48, which covers triplets (16/48), sextuplets (8/48), 32nds
# (6/48) and 64ths (3/48) — and silently rounds every QUINTUPLET and SEPTUPLET,
# because 5 and 7 do not divide 48. A five-note quintuplet came out drifting by
# up to a 120th of a beat per note and no longer summed to its own beat. That is
# the same failure as the 16th-note grid that once destroyed every triplet in
# this system, so the invariant is asserted rather than trusted.
_POSITION_GRID = 1680

# Subdivisions of the beat, coarsest first, restricted to divisors of
# _POSITION_GRID so every result is exactly notatable. A position is explained
# by the SIMPLEST subdivision it lands on, which is why the order is by size:
# 1/7 is reached before any fine binary grid (a 48th is within tolerance of a
# septuplet and would otherwise swallow it), while a drifted 0.56 passes every
# coarse candidate and resolves at a sixteenth.
_SUBDIVISIONS = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 16, 20, 21, 24, 28, 30, 35, 40, 42, 48)
# How far a stored onset may sit from a subdivision and still be read as it.
# A 256th of a beat is far below anything anyone writes and far above float
# noise or a value rounded to four decimals.
_GRID_TOLERANCE = _F(1, 256)


def _repair_engine_surface(layer, meter: Tuple[int, int]) -> Dict[str, int]:
    """Make an engine-realized surface notatable and meter-legal.

    Three mechanical repairs, in order, each counted so the caller can report
    what was wrong rather than hiding it:

    1. **Snap every onset to the notatable grid.** A float beat cursor that
       accumulated float durations and was then rounded produced positions like
       1.56 and 2.06, which are on no grid and which the engraver has to guess at.
    2. **Truncate a note that is still sounding when its own voice re-attacks.**
       One voice cannot play two notes at once; the earlier note ends where the
       next begins.
    3. **Drop what runs past the barline.** A bar holding 4.875 beats of a 4/4
       cannot be engraved; the overflow is the engine's error, not music.

    This is a repair, not a rescue: it makes a malformed surface legal, and the
    counts it returns are the signal that the generator upstream needs fixing.
    """
    from fractions import Fraction

    from .duration import bar_duration, dur_to_beats

    capacity = bar_duration(meter)
    counts = {"snapped": 0, "overlaps_trimmed": 0, "overflow_dropped": 0}

    def _on_grid(beat) -> Fraction:
        """The SIMPLEST subdivision that explains this position.

        Two failures to avoid at once. A coarse grid (1/48) repairs float drift
        but silently rounds every quintuplet and septuplet, because 5 and 7 do
        not divide 48. A fine grid (1/1680, the LCM of every denominator in the
        duration table) preserves those exactly — and stops repairing drift,
        because 1.56 is already on it, so a smeared onset stays smeared.

        So: walk the subdivisions in order of musical plausibility (binary,
        then ternary, then quintuplet and septuplet) and take the first that
        explains the position to within a 256th of a beat. 1.56 resolves to
        1.5625 at a sixteenth; a quintuplet's 1.2 is nowhere near any binary or
        ternary position and resolves exactly at a fifth. Nothing plausible ⇒
        fall back to the finest grid, which is exact for anything notatable.
        """
        offset = Fraction(beat) - 1
        for denom in _SUBDIVISIONS:
            candidate = Fraction(round(offset * denom), denom)
            if abs(candidate - offset) <= _GRID_TOLERANCE:
                return max(Fraction(1), candidate + 1)
        return max(Fraction(1), Fraction(round(offset * _POSITION_GRID), _POSITION_GRID) + 1)

    for events in _all_event_lists(layer):
        for e in events:
            exact = _on_grid(e.beat)
            if exact != Fraction(e.beat):
                counts["snapped"] += 1
            e.beat = round(float(exact), 6)

        events.sort(key=lambda x: (x.bar, x.beat))
        keep = []
        for i, e in enumerate(events):
            start = _on_grid(e.beat) - 1
            length = dur_to_beats(e.duration)
            if start >= capacity:
                counts["overflow_dropped"] += 1
                continue
            nxt = next((x for x in events[i + 1 :] if x.bar == e.bar), None)
            room = capacity - start
            if nxt is not None:
                room = min(room, _on_grid(nxt.beat) - 1 - start)
            if room <= 0:
                counts["overlaps_trimmed"] += 1
                continue
            if length > room:
                from .duration import largest_dur_at_most

                # NOT beats_to_dur: the nearest notatable value to the room left
                # can be LONGER than the room (1.4375 -> a dotted quarter at
                # 1.5), so the clamp rounded straight back past the barline.
                e.duration = largest_dur_at_most(room)
                counts["overlaps_trimmed" if nxt is not None else "overflow_dropped"] += 1
            keep.append(e)
        events[:] = keep

    return {k: v for k, v in counts.items() if v}


def _all_event_lists(layer) -> List[List]:
    """Every event list on a LayerIR, including the numbered inner voices."""
    names = (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    )
    out = [getattr(layer, n, None) or [] for n in names]
    out.extend((getattr(layer, "inner_voices", None) or {}).values())
    return [e for e in out if e]


def _capture_theme_if_first_statement(graph, phrase_id: str) -> None:
    """Store (or refresh) the principal theme when its own phrase is committed.

    Two bugs lived in the "capture once" guard this replaces.

    It returned early whenever a theme surface already existed, so **recomposing
    the theme's own phrase left the old theme on the graph forever**. Every
    later brief then developed material that was no longer in the piece, and the
    theme-recurrence check reported the theme appearing in *zero* places —
    correctly, because the stored theme really had stopped matching anything.

    And it set the surface without setting `principal_theme_id`, so a piece
    could carry a populated theme whose id was the empty string; anything keyed
    on the id was silently working with no theme at all. A graph in that state
    is repaired here rather than left broken.
    """
    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    if slot is None:
        return
    role = getattr(slot, "dramatic_role", "")
    # The opening statement, or (for a piece planned without a dramatic role) the
    # phrase that starts at bar 1.
    is_theme_phrase = role == "establish" or slot.bar_start == 1
    have = getattr(graph, "principal_theme_surface", None)
    if have and not is_theme_phrase:
        return  # nothing to do: this is not the phrase the theme comes from
    from .theme_planner import principal_theme_phrase

    source = principal_theme_phrase(graph)
    if have and source and source != phrase_id:
        return  # the theme came from a different phrase; that capture stands
    # Either there is no theme yet, or this IS the phrase it came from and has
    # just been recomposed — re-capture so the stored theme is never stale.
    if not is_theme_phrase:
        return
    try:
        from .theme_planner import capture_theme_surface

        capture_theme_surface(graph, phrase_id, n_bars=min(4, slot.bar_count))
    except Exception:
        pass  # a missing theme must never block a commit


def commit_agent_phrase_layer_ir(
    piece_id: str,
    phrase_id: str,
    layer_ir: Dict[str, Any],
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate, gate, and store agent-written LayerIR (full note-level IR).

    Call this when Claude (not the Python realizer) authored every
    ``LayerEvent`` for the phrase. Sets ``agent_authored`` so
    ``run_scales_section`` preserves this surface.

    Physical validation is strict. The commit gate then checks for
    mechanical output (skeletal density, photocopied accompaniment) with
    corpus-derived thresholds; artistic checks can be waived via
    ``allow=[{"check": ..., "reason": ...}]`` (logged to revision history).
    """
    allow = _as_list(allow, "allow")
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}

    layer = load_layer_ir_from_dict(layer_ir)
    layer.phrase_id = phrase_id
    slot = graph.phrases[phrase_id].slot
    if slot:
        # The SLOT is authoritative for key and meter. Testing `if not
        # layer.meter` never fired, because LayerIR defaults to a truthy (4, 4) —
        # so a 3/4 phrase committed as raw LayerIR kept 4/4, the meter check then
        # allowed four beats in a three-beat bar, and the score came out mis-barred.
        # An explicit meter that disagrees with the slot is reported, not silently
        # honored: the plan and the notes must agree on the bar length.
        supplied_meter = tuple(layer.meter) if layer.meter else None
        slot_meter = tuple(slot.meter) if slot.meter else (4, 4)
        if supplied_meter and supplied_meter != slot_meter and layer_ir.get("meter"):
            return {
                "ok": False,
                "error": "meter_mismatch",
                "hint": (
                    f"LayerIR declares meter {supplied_meter} but phrase slot "
                    f"{phrase_id} is {slot_meter}. Write the phrase in the "
                    f"planned meter, or change the plan first."
                ),
            }
        layer.meter = slot_meter
        # Same trap for key: the dataclass default "C" is truthy, so an unset key
        # used to stick as C major no matter what the slot planned.
        if not layer.key or not layer_ir.get("key"):
            layer.key = slot.key

    report = validate_layer_ir(layer)
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    return _gated_commit(graph, workspace, phrase_id, layer, allow, composer)


def commit_agent_phrase_direct_bars(
    piece_id: str,
    phrase_id: str,
    bars: List[Dict[str, Any]],
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert Claude's per-bar RH/LH shorthand to LayerIR and commit (gated).

    ``bars`` format matches ``direct_compose.compose_phrase``. Shorthand
    supports chords ``[C5,E5,G5]q``, ties ``~``, slurs ``( )``, ornaments
    ``:tr :mord :turn :grace``, articulations ``:stacc :acc :ten``,
    dynamics ``:p :f``, and hairpins ``< > !``.

    The commit gate blocks unambiguously mechanical output; waive a named
    artistic check with ``allow=[{"check": ..., "reason": ...}]``.
    """
    bars = _as_list(bars, "bars")
    allow = _as_list(allow, "allow")
    from .direct_compose import compose_phrase
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    slot = graph.phrases[phrase_id].slot
    if not slot:
        return {"error": "Phrase has no slot"}

    if len(bars) != slot.bar_count:
        return {
            "error": "bar_count_mismatch",
            "expected_bars": slot.bar_count,
            "got": len(bars),
            "hint": (
                f"Write exactly {slot.bar_count} bar dicts (bars "
                f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}). A pickup "
                f"bar OCCUPIES the phrase's first bar — mark that first dict "
                f"{{'pickup': True}} and write only the upbeat in it; do not add an "
                f"extra dict for it, or the phrase would run into the next one's bars."
            ),
        }

    layer = compose_phrase(
        bars,
        key=slot.key,
        bar_start=slot.bar_start,
        phrase_id=phrase_id,
        meter=slot.meter,
    )
    report = validate_layer_ir(layer)
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    return _gated_commit(graph, workspace, phrase_id, layer, allow, composer)


def run_style_review_section(
    piece_id: str,
    section_id: str,
    threshold: float = 0.35,
    persist: bool = True,
) -> Dict[str, Any]:
    """Compare assembled section MusicXML to StyleDNA-derived targets; optional RevisionScript."""
    from .review_style_gate import run_style_review_section as _gate

    return _gate(piece_id, section_id, threshold=threshold, persist=persist)


# ─── Agent Composition Support (briefs, continuity, self-evaluation) ─────────


def commit_phrase_sketch(piece_id: str, phrase_id: str, sketch: Dict[str, Any]) -> Dict[str, Any]:
    """Record the structural plan for a phrase BEFORE its notes are written.

    ``/w-compose`` step 2 and the phrase-composer agent both describe writing
    SketchIR — anchors, harmonic rhythm, texture intent, dynamic shape, breath
    points, cadence approach — as a required step, with a seven-question
    checklist. There was no way to do it: ``state.sketch`` was written only
    inside ``run_scales_section``, the engine fallback the default flow never
    takes. So on 164 real phrases the field holds a value 10 times, all of them
    engine-realized, and the brief's SKETCH section — which is how phrase N+1
    sees what phrase N planned — was empty for everything the agent wrote.

    Accepts a plain dict, so the agent can send exactly the structure it thought
    in. Unknown keys are ignored rather than rejected; a sketch is a plan, not a
    contract, and refusing one over a stray key would just push the step back
    into being skipped.
    """
    from .models import SketchIR
    from .piece_graph import _dataclass_from_dict

    workspace = _WORKSPACE / piece_id
    path = workspace / "piece_graph.json"
    if not path.exists():
        return {"error": f"no workspace for '{piece_id}'"}
    graph = PieceGraph.load(str(path))
    state = graph.phrases.get(phrase_id)
    if state is None:
        return {"error": f"unknown phrase_id: {phrase_id} (known: {sorted(graph.phrases)[:8]})"}
    if not isinstance(sketch, dict):
        return {"error": "sketch must be a dict of SketchIR fields"}

    data = dict(sketch)
    data.setdefault("phrase_id", phrase_id)
    state.sketch = _dataclass_from_dict(SketchIR, data)
    graph.save(str(path))

    from .composition_brief import _summarize_sketch

    summary = _summarize_sketch(state.sketch)
    return {
        "ok": True,
        "phrase_id": phrase_id,
        "recorded": sorted(k for k in summary),
        "ignored_keys": sorted(set(data) - {f.name for f in __import__("dataclasses").fields(SketchIR)}),
    }


def get_composition_brief(
    piece_id: str,
    phrase_id: str,
    n_exemplars: int = 8,
    composer: Optional[str] = None,
    fmt: str = "text",
) -> Any:
    """Build the composition brief for one phrase.

    The brief contains real corpus exemplar bars (in direct_compose
    shorthand), density/ornament target stats, ledger state, and the
    continuity context from the previous phrase. Claude must read this
    BEFORE writing any notes for the phrase.

    fmt="text" returns a compact string; fmt="json" returns a dict.
    """
    from dataclasses import asdict

    from .composition_brief import build_brief, render_text

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    brief = build_brief(graph, phrase_id, n_exemplars=n_exemplars, composer=composer)
    if _persist_brief_receipt(graph, phrase_id, brief):
        graph.save(str(workspace / "piece_graph.json"))
    if fmt == "json":
        return asdict(brief)
    return render_text(brief)


def _persist_brief_receipt(graph, phrase_id: str, brief) -> bool:
    """Record a brief receipt on the phrase trace. The commit gate REQUIRES
    this receipt — a phrase cannot be committed unless its brief was fetched
    (``brief_fetched``), and a brief that yielded no corpus exemplars is marked
    ``brief_insufficient`` so the commit is blocked unless explicitly waived.
    Also persists the exemplar shorthands so the gate can check the surface
    actually adapted them (anti-skip). Returns True if anything was written."""
    state = graph.phrases.get(phrase_id)
    if state is None:
        return False
    if getattr(state, "context_trace", None) is None:
        state.context_trace = {}
    if not isinstance(state.context_trace, dict):
        return False
    rhs = [ex.rh for ex in getattr(brief, "exemplars", []) if getattr(ex, "rh", "")]
    lhs = [ex.lh for ex in getattr(brief, "exemplars", []) if getattr(ex, "lh", "")]
    state.context_trace["brief_fetched"] = True
    state.context_trace["briefed_exemplars"] = rhs
    state.context_trace["briefed_exemplar_lhs"] = lhs
    state.context_trace["brief_insufficient"] = not rhs
    composer = getattr(brief, "composer", "")
    if composer:
        state.context_trace["brief_composer"] = composer
    return True


# ─── Whole-score reference study ─────────────────────────────────────────────


def list_reference_scores(composer: str) -> Any:
    """List the complete reference pieces available to study for a composer.

    Returns one entry per source piece/movement (bar count, key, meter, dominant
    textures) so the agent can pick 2-4 representative scores to read in full
    BEFORE composing — the way a human composer studies real scores. Pass a
    composer name or a ``style__<name>`` id (aggregates over armed members).
    """
    from .reference_study import list_reference_scores as _list

    return _list(composer)


def get_reference_score(
    composer: str,
    source: str,
    target_key: Optional[str] = None,
    max_bars: Optional[int] = None,
) -> Any:
    """Read one COMPLETE reference piece in readable shorthand.

    Reconstructs the full piece from the corpus (ordered by bar), rendered in the
    same direct_compose shorthand the brief uses, with each bar's roman/function
    and RH/LH texture so the agent sees the harmonic and textural arc — not just
    disconnected notes. Pass ``target_key`` to transpose into the key you'll
    compose in. The agent reads this and writes its OWN analysis via
    ``save_reference_study``.
    """
    from .reference_study import reconstruct_score

    return reconstruct_score(composer, source, target_key=target_key, max_bars=max_bars)


def save_reference_study(
    piece_id: str,
    composer: str,
    source: str,
    analysis: str,
    observations: Optional[Dict[str, Any]] = None,
) -> Any:
    """Persist the agent's OWN analysis of a reference piece to the PieceGraph.

    ``analysis`` is the agent's prose: form, themes, harmonic language, texture
    and dynamic arc, "what makes it work". ``observations`` is optional structured
    notes (e.g. cadence points, recurring gestures). Stored under
    ``reference_studies["<composer>/<source>"]`` and fed forward into every phrase
    brief, so the agent composes from its own understanding of real scores.
    """
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    key = f"{composer}/{source}"
    graph.patch(
        path=f"reference_studies.{key}",
        operation="set",
        value={
            "composer": composer,
            "source": source,
            "analysis": analysis,
            "observations": observations or {},
        },
        skill="w-plan",
        reason=f"Whole-score study of {key}",
    )
    graph.save(str(workspace / "piece_graph.json"))
    return {"saved": True, "key": key, "studies": sorted(graph.reference_studies.keys())}


def run_agent_section_briefs(
    piece_id: str,
    section_id: str,
    n_exemplars: int = 6,
    composer: Optional[str] = None,
    fmt: str = "text",
) -> Any:
    """Build briefs for every phrase in a section with ONE corpus load.

    Prefer this over per-phrase get_composition_brief for large works —
    corpus shards (20-90MB per composer) are loaded once per process.
    """
    from dataclasses import asdict

    from .composition_brief import build_brief, render_text

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        return {"error": f"No phrases found for section '{section_id}'"}

    out = {}
    dirty = False
    for pid in phrase_ids:
        try:
            brief = build_brief(graph, pid, n_exemplars=n_exemplars, composer=composer)
            dirty = _persist_brief_receipt(graph, pid, brief) or dirty
            out[pid] = asdict(brief) if fmt == "json" else render_text(brief)
        except KeyError as exc:
            out[pid] = {"error": str(exc)}
    if dirty:
        graph.save(str(workspace / "piece_graph.json"))
    if fmt == "text":
        return "\n\n".join(v if isinstance(v, str) else json.dumps(v) for v in out.values())
    return out


def plan_readiness(piece_id: str) -> Dict[str, Any]:
    """Is this piece's plan actually complete enough to compose against?

    Every part of the plan is optional at the type level, so a piece can reach
    the phrase composers with an empty narrative, no motifs and no reference
    study, and nothing anywhere says so — the briefs simply omit those sections
    and the agent cannot tell "the planner skipped this" from "this composer has
    none".

    Measured over the twelve pieces in ``workspace/``: five have a populated
    motif bank and NOT ONE had an elected principal theme or a single placement,
    and only one of twelve carried a saved reference study. Both systems are
    documented as load-bearing. This is the check that would have caught either
    on the first run.

    Returns ``ready`` (nothing missing that changes the notes), plus ``missing``
    and ``thin`` lists naming what to go back and do.
    """
    workspace = _WORKSPACE / piece_id
    path = workspace / "piece_graph.json"
    if not path.exists():
        return {"ready": False, "missing": [f"no workspace for '{piece_id}'"], "thin": []}
    graph = PieceGraph.load(str(path))

    missing: List[str] = []
    thin: List[str] = []

    if not graph.phrases:
        missing.append("form graph — no phrase slots exist (run build_form_graph)")

    dna = getattr(graph, "style_dna", None)
    composer_id = (getattr(dna, "composer_id", "") or "").strip()
    if not composer_id or len(composer_id) < 2:
        missing.append(
            f"style — composer_id is {composer_id!r} (run compile_style with a real "
            f"composer or style name; passing a bare string where a list is "
            f"expected resolves it to a single letter)"
        )
    elif getattr(dna, "tier", "") in ("C", "D"):
        thin.append(f"style tier {dna.tier} for '{composer_id}' — briefs will be generic")

    sections = getattr(getattr(graph, "narrative", None), "sections", None) or []
    if not sections:
        missing.append(
            "narrative — no sections (run save_narrative). Without it every phrase's "
            "CREATIVE INTENT falls back to its bare function label"
        )
    elif not any((getattr(s, "character", "") or "").strip() for s in sections):
        thin.append("narrative sections have no authored `character` prose")

    if not graph.motif_bank:
        missing.append(
            "motifs — the motif bank is empty (run resolve_motifs). A piece is "
            "memorable because ONE idea recurs transformed; with no motif the "
            "brief has no material to name"
        )
    else:
        placed = sum(1 for st in graph.phrases.values() if getattr(st.slot, "motif_transforms", None))
        if not graph.principal_theme_id:
            missing.append("motifs — no principal theme elected")
        elif not placed:
            missing.append("motifs — principal theme is placed in no phrase")

    movements = getattr(getattr(graph, "form", None), "movements", None) or []
    if len(movements) > 1 and not getattr(graph, "work_graph", None):
        missing.append(
            f"work plan — {len(movements)} movements and no WorkGraph (run init_work + "
            f"plan_movement). Without it nothing decides what each movement is FOR, "
            f"how it contrasts with the last, or what the finale pays off"
        )

    if not getattr(graph, "reference_studies", None):
        missing.append(
            "reference study — none saved (run save_reference_study after reading "
            "whole scores). Every brief's 'WHAT YOU LEARNED FROM THE SCORES' "
            "section is empty without it"
        )

    return {
        "piece_id": piece_id,
        "ready": not missing,
        "missing": missing,
        "thin": thin,
        "phrases": len(graph.phrases),
        "motifs": len(graph.motif_bank or {}),
        "narrative_sections": len(sections),
        "reference_studies": len(getattr(graph, "reference_studies", None) or {}),
    }


def get_section_status(piece_id: str, section_id: str) -> Dict[str, Any]:
    """Compact, section-scoped status — use this instead of dumping the graph.

    Returns ordered phrases with status/agent_authored/bar range and, for
    committed phrases, the realized tail (what the next phrase connects to).
    """
    from .composition_brief import _last_events_summary

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        known = sorted(graph.form.sections)
        return {"error": f"Unknown section '{section_id}'", "known_sections": known}

    phrases = []
    committed = 0
    for pid in phrase_ids:
        state = graph.phrases.get(pid)
        if state is None:
            phrases.append({"phrase_id": pid, "status": "missing"})
            continue
        slot = state.slot
        entry: Dict[str, Any] = {
            "phrase_id": pid,
            "status": state.status,
            "agent_authored": bool(getattr(state, "agent_authored", False)),
            "bars": f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}",
            "function": slot.function,
            "cadence": slot.cadence_target,
        }
        if state.realized is not None:
            committed += 1
            tail = _last_events_summary(state.realized)
            if tail:
                entry["exit"] = tail
        phrases.append(entry)

    return {
        "piece_id": piece_id,
        "section_id": section_id,
        "committed": committed,
        "total": len(phrase_ids),
        "phrases": phrases,
    }


def get_phrase_continuity(piece_id: str, phrase_id: str) -> Dict[str, Any]:
    """Continuity context for one phrase, read from committed state on disk.

    Disk is the source of truth — never trust a subagent's self-reported
    exit state over what was actually committed.
    """
    from .composition_brief import _summarize_slot, _transition_context

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    state = graph.phrases.get(phrase_id)
    if state is None:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    return {
        "phrase_id": phrase_id,
        "slot": _summarize_slot(state.slot),
        "transition_in": _transition_context(graph, phrase_id),
    }


# Discriminator target bands — corpus-derived human-vs-AI tells
# (see .claude/context/general/human-sounding-music.md)
# Generic human-vs-AI bands, keyed by the metric name on the EvidenceBundle
# (i.e. what style_analyzer measures). Keep these names in sync with
# EvidenceBundle's fields — a band whose key is not a bundle attribute is
# silently skipped and the metric simply disappears from the report.
_DISCRIMINATOR_BANDS = {
    # CALIBRATED against 36 real movements by Mozart, Beethoven and Chopin
    # (5th-95th percentile, widened 10%). Every one of these was previously a
    # hand-written guess, and every one of them rejected real music — the worst,
    # texture_change_pct at (0.35, 0.70), rejected **20 of 24** real movements.
    # A band that flags what real composers actually write does not measure the
    # music; it measures the band, and it pushes the critic toward the
    # non-idiomatic. test_discriminator_bands_do_not_reject_real_music keeps
    # them honest.
    #
    # texture_change_pct was widened again once Bach was armed: the calibration
    # set was Mozart/Beethoven/Chopin only, and Bach's corpus mean is **0.622**,
    # above the old 0.585 ceiling. Every Bach section would have been reported
    # "texture change high" — the discriminator telling the critic that Bach's
    # actual texture behaviour is a defect. Per-composer means now measured over
    # the whole armed corpus span 0.144 (Chopin) to 0.622 (Bach); the band
    # covers that range with a margin. A composer with a corpus_profile is
    # judged against its own mean ± 2σ instead (see _PROFILE_OVERRIDABLE), so
    # this generic band only applies to unarmed references.
    "texture_change_pct": (0.045, 0.85),
    # A COUNT of contour reversals per bar, not a fraction (see
    # _PROFILE_OVERRIDABLE below for why that distinction matters). Real
    # movements run 0.9 to 3.6; the old (1.0, 2.0) rejected half of them,
    # including 5 of 12 Mozart sonata movements.
    "direction_changes_per_bar": (0.9, 3.6),
    "density_cv": (0.198, None),
    "rest_ratio": (0.039, 0.265),
    "stepwise_pct": (0.312, 0.831),
    "events_per_bar": (5.67, 21.23),
    "rhythmic_variety": (4.5, None),
    "dynamic_markings_per_bar": (0.072, None),
}

# Bands a composer's corpus_profile may narrow to that composer's own spread.
# This is an ALLOW-LIST on purpose. Overriding by name alone silently swapped
# units: corpus_profile's old "direction_changes_per_bar" was a FRACTION of bars
# whose direction label changes (mean 0.56), and it was overriding a band applied
# to style_analyzer's per-bar reversal COUNT (1-3 for real music). Every section
# with a healthy melodic contour was therefore reported "high" with the hint
# "melodic contour is monotonic or jittery" — the discriminator was telling the
# critic that good melody writing was a defect. Two quantities, one name.
_PROFILE_OVERRIDABLE = frozenset({"texture_change_pct", "density_cv", "events_per_bar"})


def self_evaluate(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Assemble a section (or the full piece) and compare its measured
    statistics to corpus norms — the discriminator report.

    This is what the fresh-ears reviewer reads: generated-vs-corpus on the
    metrics that most separate human music from AI output (texture change
    rate above all). Section-level by design — these metrics are
    meaningless on a single 4-bar phrase.
    """
    from .assembler import assemble
    from .composition_brief import resolve_composer
    from .feedback.evidence_extractor import extract_from_file

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    warnings: List[str] = []
    resolved = resolve_composer(graph, composer, warnings)

    scope = f"section-{section_id}" if section_id else "full"
    try:
        path = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
    except ValueError as exc:
        return {"error": str(exc)}

    bundle = extract_from_file(path, resolved)
    if bundle is None:
        return {"error": f"Could not analyze assembled score at {path}"}

    report: Dict[str, Any] = {
        "piece_id": piece_id,
        "scope": scope,
        "composer_reference": resolved,
        "bar_count": bundle.bar_count,
        "metrics": {},
        "flags": [],
        "warnings": warnings,
    }

    # style_analyzer reports these as PERCENTAGES (0-100) while the bands here are
    # fractions, so they are converted unconditionally. The old rule was "divide
    # if the value exceeds 1.5", which silently inverted any piece with under 1.5%
    # rests: 0.8% was read as the fraction 0.8 and reported as far ABOVE a
    # 0.03-0.15 band — a score with almost no breathing room was told it had too
    # much. Guessing units from magnitude is not a contract.
    _PCT_METRICS = {"texture_change_pct", "rest_ratio", "stepwise_pct"}

    # Composer-aware bands: when the resolved composer has a corpus_profile,
    # judge each metric against THAT composer's own spread (mean ± 2σ) instead
    # of the generic human-vs-AI band. Otherwise the generic band can fight the
    # composer — e.g. it demands texture_change ≥0.35 while real Beethoven/Liszt
    # sit at ~0.26-0.31, penalising idiomatic figural persistence as "monotony".
    from .composition_brief import corpus_profile as _corpus_profile

    bands = dict(_DISCRIMINATOR_BANDS)
    _prof_metrics = (_corpus_profile(resolved) or {}).get("metrics", {})
    for _m, _stat in _prof_metrics.items():
        if _m not in bands or _m not in _PROFILE_OVERRIDABLE:
            continue  # same name != same quantity; see _PROFILE_OVERRIDABLE
        _mean, _sd = _stat.get("mean"), _stat.get("stdev")
        if _mean is None or not _sd or _sd <= 0:
            continue  # degenerate (e.g. grace_ratio=0 in MIDI corpus) → keep generic
        bands[_m] = (max(0.0, _mean - 2 * _sd), _mean + 2 * _sd)

    for metric, (lo, hi) in bands.items():
        value = getattr(bundle, metric, None)
        if value is None:
            value = (bundle.raw_metrics or {}).get(metric)
        if value is None:
            continue
        if metric in _PCT_METRICS:
            value = value / 100.0
        status = "ok"
        if lo is not None and value < lo:
            status = "low"
        elif hi is not None and value > hi:
            status = "high"
        report["metrics"][metric] = {
            "value": round(float(value), 3),
            "target": [lo, hi],
            "status": status,
        }
        if status != "ok":
            hints = {
                "texture_change_pct": (
                    "texture is static — real movements change texture between "
                    "4.5% and 58.5% of consecutive bars"
                    if status == "low"
                    else "texture changes more often than any real movement in the corpus"
                ),
                "direction_changes_per_bar": (
                    "the melodic line barely changes direction (monotonic) or "
                    "reverses far more often than any real movement in the corpus"
                ),
                "density_cv": "density is flat — no ebb and flow",
                "rest_ratio": ("no breathing room" if status == "low" else "too sparse"),
                "stepwise_pct": (
                    "melody is leap-heavy/fragmented"
                    if status == "low"
                    else "melody never leaps — no peaks"
                ),
                "events_per_bar": ("skeletal writing" if status == "low" else "overstuffed"),
                "rhythmic_variety": "too few distinct durations",
                "dynamic_markings_per_bar": "dynamics are flat",
            }
            report["flags"].append(
                {
                    "metric": metric,
                    "status": status,
                    "value": report["metrics"][metric]["value"],
                    "hint": hints.get(metric, ""),
                }
            )

    # Extra context the critic can use
    report["texture_distribution"] = {
        "rh": dict(
            sorted((bundle.rh_texture_distribution or {}).items(), key=lambda kv: -kv[1])[:6]
        ),
        "lh": dict(
            sorted((bundle.lh_texture_distribution or {}).items(), key=lambda kv: -kv[1])[:6]
        ),
    }
    report["assembled_path"] = path

    # Composer-specific distribution comparison (z-scores vs this composer's
    # own corpus), reusing the already-assembled score.
    divergence = _corpus_divergence_from_path(path, resolved, scope)
    if "error" not in divergence:
        report["corpus_divergence"] = divergence

    # Anti-skip: how much of the scope Claude actually authored, and any
    # phrases flagged as composed-blind (resembling no briefed exemplar).
    report["authoring"] = _authoring_summary(graph, section_id)

    # Transparency (C4): the band-based flags above use GENERIC human-vs-AI
    # discriminator bands; the composer-specific comparison lives in
    # corpus_divergence. Say so, and flag when only the generic bands were
    # available (no corpus_profile for this composer).
    report["bands_source"] = (
        "generic human-vs-AI discriminator bands; composer-specific z-scores "
        "are in corpus_divergence"
    )
    if "corpus_divergence" not in report:
        report["warnings"].append(
            f"no composer-specific corpus_profile for '{resolved}' — only "
            f"generic discriminator bands were applied (run "
            f"scripts/build_corpus_profiles.py or arm the composer)"
        )

    # Musical ear: bar/beat-level structural defects (vertical clash, buried
    # melody, unresolved NCT, no breathing, monotony) — the feedback signal the
    # actor-critic loop revises against. Reuses the already-assembled score.
    try:
        from .musical_ear import ear_report

        report["ear"] = ear_report(
            path, _extract_generated_bars(path, resolved, scope), graph=graph
        )
    except Exception as exc:  # never let the ear crash a review
        report["ear"] = {
            "findings": [],
            "summary": {"error_count": 0, "warn_count": 0},
            "undetectable": [],
            "error": str(exc),
        }

    # Score realism: formula, uniformity and notational poverty — the defects
    # that are not *wrong* but are obviously not written by a person. The ear
    # answers "is anything broken here"; this answers "does this read as
    # engraved music". It reported nothing on a score that used one cadence
    # formula in seven of its 41 bars and carried no articulation at all,
    # because none of that is an error. Every finding is advisory: this is
    # material for the fresh-ears critic to weigh, never an auto-block.
    try:
        from .score_realism import realism_report

        report["realism"] = realism_report(path, graph=graph, scope=scope, composer=resolved)
    except Exception as exc:  # never let the audit crash a review
        report["realism"] = {
            "findings": [],
            "summary": {"by_detector": {}, "warn_count": 0, "info_count": 0},
            "notation_census": {},
            "error": f"{type(exc).__name__}: {exc}",
        }

    # Voicing and cadence analysis over the PieceGraph. These read the phrases
    # as musical objects rather than as an engraved file, so they see what the
    # score-side audit cannot: whether the texture's weight actually MOVES
    # (simultaneity_cv — the measurement that showed the previous piece was not
    # thin, it was unvarying), and whether each cadence the notes describe is
    # the cadence the plan asked for, which nothing had ever checked.
    try:
        from .cadence_analysis import analyze_cadences
        from .voicing import analyze_voicing, texture_runs

        in_scope = [
            ps
            for ps in graph.phrases.values()
            if ps.realized and (not section_id or (ps.slot and ps.slot.section_id == section_id))
        ]
        in_scope.sort(key=lambda ps: ps.slot.bar_start if ps.slot else 0)
        merged = None
        if in_scope:
            from .direct_compose import merge_phrases

            merged = merge_phrases(
                [ps.realized for ps in in_scope],
                key=(in_scope[0].slot.key if in_scope[0].slot else "C"),
                meter=(tuple(in_scope[0].slot.meter) if in_scope[0].slot else (4, 4)),
                piece_id=piece_id,
            )
        if merged is not None:
            v = analyze_voicing(merged, style=resolved)
            report["voicing"] = {
                k: getattr(v, k)
                for k in (
                    "mean_simultaneity",
                    "simultaneity_cv",
                    "rh_notes_per_attack",
                    "lh_notes_per_attack",
                    "single_line_rh_pct",
                    "register_span",
                    "widest_hand_span",
                    "unplayable_spans",
                    "thirds_sixths_pct",
                    "observations",
                    "suggestions",
                )
            }
            report["voicing"]["texture_runs"] = [
                {"idiom": lbl, "from_bar": b0, "to_bar": b1} for lbl, b0, b1 in texture_runs(merged)
            ]
            c = analyze_cadences(
                [
                    (
                        ps.realized,
                        ((ps.slot.bar_start or 1) + (ps.slot.bar_count or 1) - 1)
                        if ps.slot
                        else None,
                        (ps.slot.key if ps.slot else None),
                        (ps.slot.cadence_target if ps.slot else None),
                    )
                    for ps in in_scope
                ]
            )
            report["cadences"] = {
                "realized": [
                    (c_.__dict__ if hasattr(c_, "__dict__") else c_) for c_ in (c.cadences or [])
                ],
                "matches_plan": c.matches_plan,
                "variety": c.variety,
                "repeated_formulas": c.repeated_formulas,
                "observations": c.observations,
                "suggestions": c.suggestions,
            }
    except Exception as exc:  # never let an analyzer crash a review
        report["voicing"] = {"error": f"{type(exc).__name__}: {exc}"}

    # Section gate (C3): the discriminator report is no longer purely advisory.
    # Egregious failures (mechanical static texture, composed-blind phrases,
    # many traits far outside the corpus spread, audible harmonic clashes or a
    # buried melody) constitute a HARD failure the pipeline must act on.
    report["section_gate"] = _section_gate(report)
    return report


def review_context(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Everything the fresh-ears critic needs, in one call.

    The critic was assembling its own context out of `self_evaluate` plus a hand
    written music21 snippet, which meant each reviewer saw a slightly different
    slice and the prose analyzers (theme recurrence, part-writing, the engraved
    page) reached it only if the reviewer happened to know they existed.

    Returns the assembled paths, the discriminator report, and `musical_prose` —
    the same findings phrased as musical sentences rather than metrics. That
    phrasing is deliberate: a critic handed z-scores revises toward the z-score,
    which is the "metric whack-a-mole" this system explicitly rejects.

    Deliberately does NOT include the composer's rationale, sketch or brief.
    Fresh ears means the reviewer cannot rationalise what it is hearing.
    """
    report = self_evaluate(piece_id, section_id, composer)
    if "error" in report:
        return report
    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    scope = f"section-{section_id}" if section_id else "full"

    out: Dict[str, Any] = {
        "piece_id": piece_id,
        "section_id": section_id,
        "scope": scope,
        "evaluation": report,
    }
    try:
        from .musical_report import build_report, concerns_only, render_text

        mr = build_report(graph, style=report.get("composer_reference"), scope=scope)
        out["musical_prose"] = render_text(mr)
        out["concerns"] = concerns_only(mr)
    except Exception as exc:  # a prose failure must not cost the critic its data
        out["musical_prose"] = ""
        out["concerns"] = []
        out["prose_error"] = f"{type(exc).__name__}: {exc}"

    try:
        from .assembler import assemble
        from .midi_renderer import render_midi

        out["musicxml"] = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
        out["midi"] = render_midi(graph, scope=scope, output_dir=str(workspace / "cache"))
    except Exception as exc:
        out["render_error"] = f"{type(exc).__name__}: {exc}"
    return out


def _section_gate(report: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a pass/fail verdict from a self_evaluate report.

    Falsified against real scores (2026-06-20): statistical hard-fails
    (static-texture, |z|>3, musical_ear clash/buried) REJECTED real Chopin,
    Beethoven, and Bach, so no ARTISTIC check may block. Composing away from the
    briefed exemplars is a creative choice, not a defect, so ``composed_blind``
    stays advisory too. The critic's ear judges whether a section works.

    What DOES block is a physically broken score. The ear's ``error``-severity
    findings — a bar that holds more beats than its meter, a note outside the
    instrument's range — are not artistic judgements: they cannot be engraved or
    played, and every one of them has been shipped silently by this system at
    some point because nothing read the assembled file back. Those detectors
    were falsified against nine real sonatas and mazurkas first and produce zero
    errors on them (see musical_ear).
    """
    authoring = report.get("authoring", {})
    blind = authoring.get("composed_blind", 0)
    advisory: List[str] = []
    if blind:
        advisory.append(
            f"{blind} phrase(s) composed away from the briefed exemplars: "
            f"{authoring.get('composed_blind_phrases', [])} — fine if deliberate "
            f"invention; the critic judges by ear"
        )

    hard_failures: List[str] = []
    for finding in (report.get("ear", {}) or {}).get("findings", []):
        if finding.get("severity") != "error":
            continue
        hard_failures.append(f"{finding.get('detector')}: {finding.get('problem')}")
    if len(hard_failures) > 8:
        hard_failures = hard_failures[:8] + [f"... and {len(hard_failures) - 8} more"]

    # Realism findings are ADVISORY without exception — every one of them was
    # falsified against the reference corpus and several fire on canonical
    # movements (each detector's docstring states its false-positive rate). They
    # are surfaced here because they were previously computed and then read by
    # nobody, which is how a score with one cadence formula in seven of its bars
    # and no articulation at all passed every gate the system had.
    for finding in (report.get("realism", {}) or {}).get("findings", []):
        advisory.append(f"{finding.get('detector')}: {finding.get('problem')}")
    census = (report.get("realism", {}) or {}).get("notation_census") or {}
    if census:
        advisory.append(
            "notation census — "
            + ", ".join(
                f"{k}={census[k]}"
                for k in ("articulations", "slur", "hairpin", "ties", "ornaments", "dynamics")
                if k in census
            )
            + f" over {census.get('bars', '?')} bars "
            f"({census.get('marks_per_bar', '?')} marks/bar; real Mozart/Beethoven/Chopin "
            f"movements run 0.11-5.71, median 1.58)"
        )

    return {
        "passed": not hard_failures,
        "hard_failures": hard_failures,
        "advisory": advisory,
    }


# ─── Piece-vs-corpus distribution comparison (B3) ────────────────────────────


def _extract_generated_bars(path: str, composer: str, source_name: str):
    """Re-extract bar records from an assembled score, exactly as the corpus
    was extracted — so generated metrics are comparable to the corpus profile.
    """
    import music21
    from scripts.build_full_corpus import analyze_score_bars

    score = music21.converter.parse(path)
    return analyze_score_bars(score, composer, source_name)


def _corpus_divergence_from_path(path: str, composer: str, scope: str) -> Dict[str, Any]:
    """Compare an assembled score's bar metrics to the composer's corpus
    distribution (corpus_profile.json) via per-metric z-scores.

    Same yardstick on both sides: ``corpus_metrics.bar_metrics`` over bar
    records. ``|z| > 2`` means the generated music sits outside the spread of
    real movements for that trait.
    """
    from .composition_brief import corpus_profile
    from .corpus_metrics import (
        bar_metrics,
        l1_distance,
        texture_distribution,
        zscore,
    )
    from .style_dimensions import style_fingerprint

    profile = corpus_profile(composer)
    pm = profile.get("metrics", {}) if isinstance(profile, dict) else {}
    if not pm:
        return {
            "error": f"no corpus_profile for '{composer}' — run scripts/build_corpus_profiles.py"
        }

    try:
        bars = _extract_generated_bars(path, composer, scope)
    except Exception as exc:  # parse/extract failure must not crash review
        return {"error": f"could not extract generated bars: {exc}"}
    if not bars:
        return {"error": "no bars extracted from assembled score"}

    # Score on EVERY profiled dimension — texture/rhythm (bar_metrics) plus
    # harmony/melody/rhythm-value (style_fingerprint) — not just texture.
    gen = {**bar_metrics(bars), **style_fingerprint(bars)}
    metrics: Dict[str, Any] = {}
    flags: List[Dict[str, Any]] = []
    for name in pm:
        stat = pm.get(name)
        if not stat:
            continue
        # Skip degenerate corpus stats (zero variance) — e.g. grace_ratio is
        # always 0 in a MIDI-derived corpus because MIDI cannot encode grace
        # notes. A z-score against sd=0 is a meaningless sentinel, not evidence
        # the generated music diverges, so it must not count toward the gate.
        if not stat.get("stdev") or stat["stdev"] <= 0:
            continue
        value = gen.get(name, 0.0)
        z = zscore(value, stat["mean"], stat["stdev"])
        status = "ok" if abs(z) <= 2 else ("low" if z < 0 else "high")
        metrics[name] = {
            "value": value,
            "z": z,
            "corpus_mean": stat["mean"],
            "corpus_sd": stat["stdev"],
            "status": status,
        }
        if status != "ok":
            flags.append(
                {
                    "metric": name,
                    "z": z,
                    "value": value,
                    "corpus_mean": stat["mean"],
                    "status": status,
                }
            )

    gen_lh = texture_distribution(bars, "lh")
    corpus_lh = profile.get("lh_texture_distribution", {})
    lh_l1 = l1_distance(gen_lh, corpus_lh)
    gen_rh = texture_distribution(bars, "rh")
    corpus_rh = profile.get("rh_texture_distribution", {})
    rh_l1 = l1_distance(gen_rh, corpus_rh)
    # Judge L1 against real per-movement spread, not against 0: a single
    # movement legitimately uses a texture subset, so L1≈1 is normal.
    base = profile.get("lh_l1_baseline", {})
    lh_threshold = round(base.get("mean", 0.6) + 2 * base.get("stdev", 0.0), 3) if base else 0.6
    lh_over = lh_l1 > lh_threshold
    rh_over = bool(corpus_rh) and rh_l1 > lh_threshold  # share the calibrated band

    n_metrics = len(metrics)
    n_ok = n_metrics - len(flags)
    return {
        "composer": composer,
        "bar_count": len(bars),
        "corpus_movements": profile.get("movements_used"),
        "metrics": metrics,
        "flags": flags,
        "texture_divergence": {
            "lh_l1": lh_l1,
            "rh_l1": rh_l1,
            "threshold": lh_threshold,
            "over": lh_over or rh_over,
            "lh_over": lh_over,
            "rh_over": rh_over,
            "corpus_movement_mean": base.get("mean"),
        },
        "corpus_likeness": (
            f"{n_ok}/{n_metrics} metrics within 2σ of {composer}; "
            f"texture L1 lh={lh_l1}/rh={rh_l1} (corpus ≤{lh_threshold})"
        ),
    }


def _authoring_summary(graph, section_id: Optional[str]) -> Dict[str, Any]:
    """How much of the scope was agent-authored vs engine-realized, plus any
    composed-blind flags recorded at commit time."""
    if section_id:
        pids = graph.get_section_phrases(section_id)
    else:
        pids = list(graph.phrases.keys())
    authored = blind = engine = 0
    blind_phrases: List[str] = []
    for pid in pids:
        st = graph.phrases.get(pid)
        if st is None:
            continue
        if getattr(st, "agent_authored", False):
            authored += 1
        else:
            engine += 1
        trace = getattr(st, "context_trace", None) or {}
        if isinstance(trace, dict) and trace.get("composed_blind"):
            blind += 1
            blind_phrases.append(pid)
    return {
        "phrases": len(pids),
        "agent_authored": authored,
        "engine_realized": engine,
        "composed_blind": blind,
        "composed_blind_phrases": blind_phrases,
    }


def compare_to_corpus(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Assemble a section (or whole piece) and score it against the composer's
    real-corpus metric distribution — the post-generation divergence report.

    Returns per-metric z-scores (flagging |z|>2), LH-texture L1 divergence, and
    a one-line corpus-likeness summary. This is a DIAGNOSTIC the critic may read
    to understand where the section sits relative to the composer's real spread —
    NOT a revision driver. Out-of-band does not mean bad (real Chopin/Beethoven
    sit outside MIDI-derived bands); chasing z-scores back into band is the
    "metric whack-a-mole" the agent-creative direction rejects. Composer-specific
    (vs the generic human-sounding bands in ``self_evaluate``).
    """
    from .assembler import assemble
    from .composition_brief import resolve_composer

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    warnings: List[str] = []
    resolved = resolve_composer(graph, composer, warnings)
    scope = f"section-{section_id}" if section_id else "full"
    try:
        path = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
    except ValueError as exc:
        return {"error": str(exc)}

    report = _corpus_divergence_from_path(path, resolved, scope)
    report["piece_id"] = piece_id
    report["scope"] = scope
    report["assembled_path"] = path
    report["warnings"] = warnings
    report["authoring"] = _authoring_summary(graph, section_id)
    return report


# ─── Candidate Panel Support ─────────────────────────────────────────────────
#
# Structurally load-bearing phrases (theme statements, climaxes,
# recapitulation entries, final cadences) can be composed by 2-3
# candidate-composer subagents through different lenses. Candidates are
# stored OUTSIDE graph.phrases (so they never assemble into the score),
# previewed as standalone MusicXML for the judge, and the winner is
# promoted to the canonical phrase.


def _candidates_dir(piece_id: str) -> Path:
    d = _WORKSPACE / piece_id / "candidates"
    d.mkdir(parents=True, exist_ok=True)
    return d


def commit_candidate_phrase(
    piece_id: str,
    phrase_id: str,
    lens: str,
    bars: Optional[List[Dict[str, Any]]] = None,
    layer_ir: Optional[Dict[str, Any]] = None,
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Commit one PANEL CANDIDATE for a phrase, under a lens label.

    Validates and runs the same quality gate as a real commit, but stores
    the result in workspace/<piece>/candidates/ (never in graph.phrases),
    with a standalone MusicXML preview for the judge. Promote the winner
    with ``promote_candidate``.
    """
    bars = _as_list(bars, "bars")
    allow = _as_list(allow, "allow")
    from .commit_gate import run_commit_gate
    from .direct_compose import compose_phrase
    from .piece_graph import _deep_serialize
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    slot = graph.phrases[phrase_id].slot
    if not slot:
        return {"error": "Phrase has no slot"}

    if bars:
        if len(bars) != slot.bar_count:
            return {
                "error": "bar_count_mismatch",
                "expected_bars": slot.bar_count,
                "got": len(bars),
                "hint": (
                    f"Write exactly {slot.bar_count} bar dicts. A pickup bar occupies "
                    f"the phrase's first bar; mark it {{'pickup': True}} rather than "
                    f"adding an extra dict."
                ),
            }
        layer = compose_phrase(
            bars, key=slot.key, bar_start=slot.bar_start, phrase_id=phrase_id, meter=slot.meter
        )
    elif layer_ir is not None:
        layer = load_layer_ir_from_dict(layer_ir)
        layer.phrase_id = phrase_id
        if not layer.key:
            layer.key = slot.key
    else:
        return {"error": "Provide bars or layer_ir"}

    report = validate_layer_ir(layer)
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    gate = run_commit_gate(graph, phrase_id, layer, allow=allow, composer=composer)
    if not gate.passed:
        return {
            "ok": False,
            "error": "quality_gate_blocked",
            "blocking": [d.to_dict() for d in gate.blocking],
            "warnings": [d.to_dict() for d in gate.warnings],
            "hint": "Same gate rules as a real commit — revise the "
            "flagged bars (max 3 attempts) or waive with "
            "allow=[{'check':..,'reason':..}].",
        }

    # Engrave the candidate too, so the judge compares what will actually ship.
    # The panel judge picks a winner from a rendered preview; an unengraved
    # preview has no articulation, no phrasing and no pedal in it, so the judge
    # was choosing between three MIDI dumps and only the winner was then
    # engraved on promotion. The pass is non-destructive and idempotent — it
    # runs again on promotion and finds nothing left blank.
    engraving = _engrave_phrase(graph, phrase_id, layer, composer)

    cand_id = f"{phrase_id}__cand_{lens}"
    cand_path = _candidates_dir(piece_id) / f"{cand_id}.json"
    record = {
        "phrase_id": phrase_id,
        "lens": lens,
        "layer_ir": _deep_serialize(layer),
        "gate": {"warnings": [d.to_dict() for d in gate.warnings], "overrides": gate.overrides},
        "engraving": engraving,
        "created_at": _now_iso(),
    }
    with open(cand_path, "w") as f:
        json.dump(record, f, indent=1)

    preview_path = ""
    try:
        preview_path = _render_layer_preview(
            layer, _candidates_dir(piece_id) / f"{cand_id}.musicxml", tempo_bpm=slot.tempo_bpm
        )
    except Exception as exc:  # preview is best-effort
        preview_path = f"(preview failed: {exc})"

    return {
        "ok": True,
        "candidate_id": cand_id,
        "lens": lens,
        "path": str(cand_path),
        "preview": preview_path,
        "gate": record["gate"],
    }


def _render_layer_preview(layer: LayerIR, out_path: Path, tempo_bpm: int = 120) -> str:
    """Render a single LayerIR as a standalone MusicXML preview."""
    import music21

    from .assembler import _build_piano_score
    from .music_io import layer_ir_to_event_ir

    events = layer_ir_to_event_ir(layer)
    # Re-base bars so the preview starts at bar 1
    if events:
        shift = min(e.bar for e in events) - 1
        for e in events:
            e.bar -= shift
    score = music21.stream.Score()
    score = _build_piano_score(score, events, layer.key, layer.meter, tempo_bpm)
    score.write("musicxml", fp=str(out_path))
    return str(out_path)


def list_phrase_candidates(piece_id: str, phrase_id: str) -> Dict[str, Any]:
    """All committed panel candidates for a phrase, with previews."""
    out: Dict[str, Any] = {"phrase_id": phrase_id, "candidates": []}
    for path in sorted(_candidates_dir(piece_id).glob(f"{phrase_id}__cand_*.json")):
        try:
            with open(path) as f:
                record = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        preview = path.with_suffix(".musicxml")
        out["candidates"].append(
            {
                "candidate_id": path.stem,
                "lens": record.get("lens"),
                "path": str(path),
                "preview": str(preview) if preview.exists() else None,
                "gate_warnings": [
                    w.get("check") for w in record.get("gate", {}).get("warnings", [])
                ],
            }
        )
    return out


def promote_candidate(piece_id: str, phrase_id: str, lens: str) -> Dict[str, Any]:
    """Promote the winning panel candidate to the canonical phrase.

    Re-runs the gate (cheap; the candidate already passed it) and commits
    as agent-authored. Loser files stay on disk for the audit trail.
    """
    cand_path = _candidates_dir(piece_id) / f"{phrase_id}__cand_{lens}.json"
    if not cand_path.exists():
        listing = list_phrase_candidates(piece_id, phrase_id)
        return {
            "error": f"No candidate '{lens}' for {phrase_id}",
            "available": [c["lens"] for c in listing["candidates"]],
        }
    with open(cand_path) as f:
        record = json.load(f)

    result = commit_agent_phrase_layer_ir(
        piece_id,
        phrase_id,
        record["layer_ir"],
        allow=[
            {**ov, "reason": ov.get("reason", "panel candidate override")}
            for ov in record.get("gate", {}).get("overrides", [])
        ]
        or None,
    )
    if result.get("ok"):
        result["promoted_from"] = f"{phrase_id}__cand_{lens}"
        workspace = _WORKSPACE / piece_id
        graph = PieceGraph.load(str(workspace / "piece_graph.json"))
        from .models import RevisionEntry

        graph.revision_history.append(
            RevisionEntry(
                timestamp=_now_iso(),
                skill="candidate_panel",
                path=f"phrases.{phrase_id}",
                operation=f"promote:{lens}",
                reason=f"judge selected '{lens}' lens candidate",
            )
        )
        graph.save(str(workspace / "piece_graph.json"))
    return result


def orchestrate_section(
    piece_id: str,
    section_id: str,
    target_ensemble: Optional[List[str]] = None,
    planner: str = "idiomatic",
) -> Dict[str, Any]:
    """Expand a section's committed piano-core LayerIR into orchestral parts.

    Piano-core-first workflow for concertos/symphonies: compose and review
    the musical substance at the keyboard, then expand by role.

    planner="idiomatic" (default) uses orchestration_planner — register-
    aware assignment with climax doublings, divided inner voices, wind
    pads, range clamping. planner="sabre" falls back to the simple 3-role
    expansion. Parts go to workspace/<piece>/orchestration/<section>.json;
    render to score with ``assemble_orchestration``.
    """
    target_ensemble = _as_list(target_ensemble, "target_ensemble")
    from .direct_compose import merge_phrases

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        return {"error": f"Unknown section '{section_id}'"}

    realized = [
        graph.phrases[pid].realized
        for pid in phrase_ids
        if pid in graph.phrases and graph.phrases[pid].realized
    ]
    if not realized:
        return {"error": f"No realized phrases in section '{section_id}'"}

    first_slot = graph.phrases[phrase_ids[0]].slot
    key = first_slot.key if first_slot else "C"
    meter = first_slot.meter if first_slot else (4, 4)

    if not target_ensemble:
        target = getattr(graph.contract, "target", None)
        instrumentation = getattr(target, "instrumentation", "orchestra")
        default_ensembles = {
            "orchestra": [
                "flute",
                "oboe",
                "clarinet",
                "bassoon",
                "horn",
                "violin_1",
                "violin_2",
                "viola",
                "cello",
                "contrabass",
            ],
            "string_quartet": ["violin_1", "violin_2", "viola", "cello"],
            "string_orchestra": ["violin_1", "violin_2", "viola", "cello", "contrabass"],
        }
        target_ensemble = default_ensembles.get(instrumentation, default_ensembles["orchestra"])

    merged = merge_phrases(realized, key=key, meter=meter, piece_id=f"{piece_id}:{section_id}")
    merged.meter = meter

    if planner == "sabre":
        from .sabre import SABRE

        parts = SABRE().orchestrate_from_piano(merged, target_ensemble, key=key)
    else:
        from .orchestration_planner import plan_orchestration

        style_roles = None
        program = getattr(graph, "style_program", None)
        if program is not None:
            style_roles = getattr(program, "orchestration_roles", None)
        parts = plan_orchestration(merged, target_ensemble, key=key, style_roles=style_roles)

    out_dir = workspace / "orchestration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{section_id}.json"
    with open(out_path, "w") as f:
        json.dump(
            {
                "section_id": section_id,
                "ensemble": target_ensemble,
                "key": key,
                "meter": list(meter),
                "planner": planner,
                "parts": parts,
            },
            f,
            indent=1,
        )

    graph.output_paths[f"orchestration:{section_id}"] = str(out_path)
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "ok": True,
        "section_id": section_id,
        "ensemble": target_ensemble,
        "planner": planner,
        "part_event_counts": {k: len(v) for k, v in parts.items()},
        "path": str(out_path),
    }


def assemble_orchestration(piece_id: str, section_id: str) -> Dict[str, Any]:
    """Render orchestrated parts (from orchestrate_section) to MusicXML."""
    import music21

    from .assembler import _build_ensemble_score
    from .models import EventIR

    workspace = _WORKSPACE / piece_id
    parts_path = workspace / "orchestration" / f"{section_id}.json"
    if not parts_path.exists():
        return {"error": f"No orchestration for '{section_id}' — run orchestrate_section first"}
    with open(parts_path) as f:
        data = json.load(f)

    events: List[EventIR] = []
    for inst, inst_events in data.get("parts", {}).items():
        for ev in inst_events:
            events.append(
                EventIR(
                    staff=inst,
                    bar=ev["bar"],
                    beat=ev["beat"],
                    pitch=ev["pitch"],
                    duration=ev["duration"],
                    dynamic=ev.get("dynamic"),
                    articulation=ev.get("articulation"),
                    slur=ev.get("slur"),
                )
            )
    if not events:
        return {"error": "Orchestration has no events"}

    # Re-base bars so the score starts at bar 1
    shift = min(e.bar for e in events) - 1
    if shift:
        for e in events:
            e.bar -= shift
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))

    meter = tuple(data.get("meter", [4, 4]))
    score = music21.stream.Score()
    score = _build_ensemble_score(score, events, data.get("key", "C"), meter, 120)
    out_path = workspace / "output" / f"{piece_id}_{section_id}_orch.musicxml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(out_path))
    return {"ok": True, "path": str(out_path), "parts": sorted(data.get("parts", {}).keys())}
