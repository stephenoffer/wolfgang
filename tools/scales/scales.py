"""
SCALES — Top-level orchestrator.

Sketch-Conditioned Alternating Ledger-guided Expansion Search.

This module provides the Python tool surface that Claude's skills call.
All functions operate on the PieceGraph as the single source of truth.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
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

    return {
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
        )

    # ─── Populate expectations from form structure ─────────────────────
    try:
        _ledger = getattr(graph, "expectation_ledger", None)
        _cross_ledger = getattr(graph, "cross_scale_ledger", None)

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
    except Exception:
        pass  # Ledger not initialized — skip gracefully

    graph.phase = PipelinePhase.PLANNING.value
    graph.save(str(workspace / "piece_graph.json"))

    return phrase_summaries


def resolve_motifs(piece_id: str, motif_definitions: List[Dict]) -> Dict[str, Any]:
    """Validate and store motif definitions."""
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

    graph.save(str(workspace / "piece_graph.json"))
    return {
        "motifs_stored": len(graph.motif_bank),
        "motif_ids": list(graph.motif_bank.keys()),
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
    for node in best_path.nodes:
        if node.surface:
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


def _build_ternary(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """Build ABA ternary form."""
    phrases = []
    bar = 1

    # A section: 2 phrases (8+8 bars)
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.PRESENTATION.value, CadenceTarget.HC.value),
            (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_a_p{i + 1}", "m1_a", bar, 8, fn, cad, key, meter, tempo, style)
        )
        bar += 8

    # B section: 2 phrases (8+8 bars)
    b_key = _relative_key(key)
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.CONTRASTING_THEME.value, CadenceTarget.HC.value),
            (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_b_p{i + 1}", "m1_b", bar, 8, fn, cad, b_key, meter, tempo, style)
        )
        bar += 8

    # A' section: 2 phrases (8+8 bars)
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.RETURN.value, CadenceTarget.HC.value),
            (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_a2_p{i + 1}", "m1_a2", bar, 8, fn, cad, key, meter, tempo, style)
        )
        bar += 8

    return phrases


def _build_sonata(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """Build sonata-allegro exposition."""
    phrases = []
    bar = 1

    # Primary theme area
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.PRESENTATION.value, CadenceTarget.HC.value),
            (PhraseFunction.CONTINUATION.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_pt_p{i + 1}", "m1_pt", bar, 8, fn, cad, key, meter, tempo, style)
        )
        bar += 8

    # Transition
    phrases.append(
        _make_slot(
            "m1_tr_p1",
            "m1_tr",
            bar,
            8,
            PhraseFunction.TRANSITION.value,
            CadenceTarget.HC.value,
            key,
            meter,
            tempo,
            style,
        )
    )
    bar += 8

    # Secondary theme
    s_key = _dominant_key(key)
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.CONTRASTING_THEME.value, CadenceTarget.HC.value),
            (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_st_p{i + 1}", "m1_st", bar, 8, fn, cad, s_key, meter, tempo, style)
        )
        bar += 8

    # Closing
    phrases.append(
        _make_slot(
            "m1_cl_p1",
            "m1_cl",
            bar,
            4,
            PhraseFunction.CLOSING.value,
            CadenceTarget.PAC.value,
            s_key,
            meter,
            tempo,
            style,
        )
    )

    return phrases


def _build_theme_variations(
    key: str, tempo: int, meter: Tuple[int, int], style: StyleDNA
) -> List[PhraseSlot]:
    """Build theme + 3 variations."""
    phrases = []
    bar = 1

    # Theme
    for i, (fn, cad) in enumerate(
        [
            (PhraseFunction.PRESENTATION.value, CadenceTarget.HC.value),
            (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
        ]
    ):
        phrases.append(
            _make_slot(f"m1_theme_p{i + 1}", "m1_theme", bar, 8, fn, cad, key, meter, tempo, style)
        )
        bar += 8

    # Variations
    for var in range(1, 4):
        for i, (fn, cad) in enumerate(
            [
                (PhraseFunction.RETURN_VARIED.value, CadenceTarget.HC.value),
                (PhraseFunction.CADENTIAL.value, CadenceTarget.PAC.value),
            ]
        ):
            phrases.append(
                _make_slot(
                    f"m1_var{var}_p{i + 1}",
                    f"m1_var{var}",
                    bar,
                    8,
                    fn,
                    cad,
                    key,
                    meter,
                    tempo,
                    style,
                )
            )
            bar += 8

    return phrases


def _build_simple(
    key: str, tempo: int, meter: Tuple[int, int], form: str, style: StyleDNA
) -> List[PhraseSlot]:
    """Build a simple 2-phrase structure."""
    return [
        _make_slot(
            "m1_a_p1",
            "m1_a",
            1,
            8,
            PhraseFunction.PRESENTATION.value,
            CadenceTarget.HC.value,
            key,
            meter,
            tempo,
            style,
        ),
        _make_slot(
            "m1_a_p2",
            "m1_a",
            9,
            8,
            PhraseFunction.CADENTIAL.value,
            CadenceTarget.PAC.value,
            key,
            meter,
            tempo,
            style,
        ),
    ]


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
) -> PhraseSlot:
    """Create a PhraseSlot with default harmony and texture plans."""
    # Simple harmony plan
    harmony = _default_harmony_plan(function, cadence, bar_count)

    # Default texture plan from style
    texture_plan = []
    rh_options = list(style.rh_distribution.keys()) or [TextureType.SINGING_MELODY.value]
    lh_options = list(style.lh_distribution.keys()) or [AccompType.ALBERTI.value]

    for i in range(bar_count):
        rh = rh_options[i % len(rh_options)] if rh_options else TextureType.SINGING_MELODY.value
        lh = lh_options[i % len(lh_options)] if lh_options else AccompType.ALBERTI.value
        texture_plan.append(
            BarTexturePlan(
                rh_texture=rh,
                lh_texture=lh,
                rh_density_target=8,
                lh_density_target=6,
            )
        )

    # Energy curve
    energy = _default_energy_curve(function, bar_count)

    return PhraseSlot(
        phrase_id=phrase_id,
        section_id=section_id,
        bar_start=bar_start,
        bar_count=bar_count,
        function=function,
        cadence_target=cadence,
        cadence_bar=bar_start + bar_count - 1,
        key=key,
        meter=meter,
        tempo_bpm=tempo,
        harmony_plan=harmony,
        texture_plan=texture_plan,
        curves=PhraseCurves(energy=energy),
    )


def _default_harmony_plan(function: str, cadence: str, bar_count: int) -> List[str]:
    """Generate a default harmony plan."""
    if bar_count <= 4:
        if cadence == CadenceTarget.PAC.value:
            return ["I", "IV", "V", "I"]
        if cadence == CadenceTarget.HC.value:
            return ["I", "ii", "IV", "V"]
        return ["I", "IV", "V", "I"]

    # 8-bar plan
    if cadence == CadenceTarget.PAC.value:
        return ["I", "I", "IV", "ii", "V", "V7", "I", "I"]
    if cadence == CadenceTarget.HC.value:
        return ["I", "I", "vi", "IV", "ii", "ii6", "V", "V"]
    return ["I", "vi", "IV", "I", "ii", "V", "I", "I"]


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
    return True


def _relative_key(key: str) -> str:
    """Get relative major/minor key."""
    if key.endswith("m"):
        # minor → relative major (up minor 3rd)
        relatives = {
            "Am": "C",
            "Dm": "F",
            "Em": "G",
            "Bm": "D",
            "F#m": "A",
            "C#m": "E",
            "Gm": "Bb",
            "Cm": "Eb",
        }
        return relatives.get(key, "C")
    # major → relative minor (down minor 3rd)
    relatives = {"C": "Am", "G": "Em", "D": "Bm", "A": "F#m", "F": "Dm", "Bb": "Gm", "Eb": "Cm"}
    return relatives.get(key, "Am")


def _dominant_key(key: str) -> str:
    """Get dominant key (V)."""
    dominants = {
        "C": "G",
        "G": "D",
        "D": "A",
        "A": "E",
        "E": "B",
        "F": "C",
        "Bb": "F",
        "Eb": "Bb",
        "Ab": "Eb",
        "Cm": "Gm",
        "Gm": "Dm",
        "Dm": "Am",
        "Am": "Em",
        "Em": "Bm",
        "Fm": "Cm",
    }
    return dominants.get(key, "G")


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

    graph.commit_agent_phrase(phrase_id, layer)

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
    return out


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
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = PieceGraph.load(str(workspace / "piece_graph.json"))
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}

    layer = load_layer_ir_from_dict(layer_ir)
    layer.phrase_id = phrase_id
    slot = graph.phrases[phrase_id].slot
    if slot:
        if not layer.key:
            layer.key = slot.key
        if not layer.meter:
            layer.meter = slot.meter

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
_DISCRIMINATOR_BANDS = {
    "texture_change_pct": (0.35, 0.70),
    "direction_changes_per_bar": (1.0, 2.0),
    "density_cv": (0.30, None),
    "rest_ratio": (0.03, 0.15),
    "stepwise_pct": (0.35, 0.60),
    "events_per_bar": (6.0, 18.0),
    "rhythmic_variety": (5, None),
    "dynamic_markings_per_bar": (0.10, None),
}


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

    # Metrics reported as percentages by the analyzer; bands are fractions
    _PCT_METRICS = {"texture_change_pct", "rest_ratio", "stepwise_pct"}

    for metric, (lo, hi) in _DISCRIMINATOR_BANDS.items():
        value = getattr(bundle, metric, None)
        if value is None:
            value = (bundle.raw_metrics or {}).get(metric)
        if value is None:
            continue
        if metric in _PCT_METRICS and value > 1.5:
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
                    "texture is static — real corpus changes texture "
                    "between ~40-70% of consecutive bars"
                ),
                "direction_changes_per_bar": ("melodic contour is monotonic or jittery"),
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

    # Section gate (C3): the discriminator report is no longer purely advisory.
    # Egregious failures (mechanical static texture, composed-blind phrases,
    # many traits far outside the corpus spread) constitute a HARD failure the
    # pipeline must act on before the section is accepted.
    report["section_gate"] = _section_gate(report)
    return report


def _section_gate(report: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a hard pass/fail verdict from a self_evaluate report. Only
    egregious, unambiguous failures block — ordinary out-of-band flags remain
    advisory for the fresh-ears critic to weigh."""
    hard: List[str] = []

    metrics = report.get("metrics", {})
    # The single strongest human-vs-AI discriminator: static texture. A value
    # far below the band (≤0.15 of consecutive bars changing) is mechanical.
    tcp = metrics.get("texture_change_pct")
    if tcp and tcp.get("status") == "low" and tcp.get("value", 1.0) <= 0.15:
        hard.append(f"texture is mechanically static (texture_change_pct={tcp['value']} ≤ 0.15)")

    # Phrases that ignored every briefed corpus exemplar.
    authoring = report.get("authoring", {})
    blind = authoring.get("composed_blind", 0)
    if blind:
        hard.append(
            f"{blind} phrase(s) composed blind (resemble no briefed "
            f"exemplar): {authoring.get('composed_blind_phrases', [])}"
        )

    # Many traits far outside the composer's own corpus spread (|z|>3).
    div = report.get("corpus_divergence", {})
    far = [m for m, s in (div.get("metrics", {}) or {}).items() if abs(s.get("z", 0)) > 3]
    if len(far) >= 3:
        hard.append(
            f"{len(far)} metrics far outside {div.get('composer', '')} corpus spread (|z|>3): {far}"
        )

    return {"passed": not hard, "hard_failures": hard}


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
        SCALAR_METRICS,
        bar_metrics,
        l1_distance,
        texture_distribution,
        zscore,
    )

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

    gen = bar_metrics(bars)
    metrics: Dict[str, Any] = {}
    flags: List[Dict[str, Any]] = []
    for name in SCALAR_METRICS:
        stat = pm.get(name)
        if not stat:
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
    a one-line corpus-likeness summary. This is the global piece-vs-corpus
    check that drives the bounded auto-revision loop; it is composer-specific
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

    if bars is not None:
        if len(bars) != slot.bar_count:
            return {
                "error": "bar_count_mismatch",
                "expected_bars": slot.bar_count,
                "got": len(bars),
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

    cand_id = f"{phrase_id}__cand_{lens}"
    cand_path = _candidates_dir(piece_id) / f"{cand_id}.json"
    record = {
        "phrase_id": phrase_id,
        "lens": lens,
        "layer_ir": _deep_serialize(layer),
        "gate": {"warnings": [d.to_dict() for d in gate.warnings], "overrides": gate.overrides},
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

    if target_ensemble is None:
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
