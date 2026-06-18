"""
PieceGraph — the single source of truth for a composition.

Replaces the scattered JSON files (plan.json, narrative-arc.json,
form_graph.json, motif_bank.json, continuity.json, state.json) with
one auditable, patchable graph.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .enums import CompositionMode, PhraseStatus, PipelinePhase
from .models import (
    CandidateNode,
    ContextTrace,
    ContextUtilizationReport,
    FormGraph,
    LayerEvent,
    LayerIR,
    MotifObject,
    MovementContract,
    NarrativeArc,
    PhraseSlot,
    PhraseState,
    PieceContract,
    ReviewResult,
    RevisionEntry,
    SectionContract,
    SketchIR,
    StyleDNA,
    StyleProgram,
    WorkGraph,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _deep_serialize(obj: Any) -> Any:
    """Recursively convert dataclasses and special types to JSON-safe dicts."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _deep_serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _deep_serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_deep_serialize(v) for v in obj]
    if isinstance(obj, set):
        return sorted(_deep_serialize(v) for v in obj)
    return obj


def _get_nested(data: dict, path: str) -> Any:
    """Get a value from a nested dict using dot-separated path."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _set_nested(data: dict, path: str, value: Any) -> None:
    """Set a value in a nested dict using dot-separated path."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value


def _delete_nested(data: dict, path: str) -> bool:
    """Delete a value from a nested dict. Returns True if found and deleted."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    if isinstance(current, dict) and parts[-1] in current:
        del current[parts[-1]]
        return True
    return False


def _append_nested(data: dict, path: str, value: Any) -> None:
    """Append a value to a list at a nested path."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    key = parts[-1]
    if key not in current or not isinstance(current[key], list):
        current[key] = []
    current[key].append(value)


def _merge_nested(data: dict, path: str, value: dict) -> None:
    """Merge a dict into a nested path."""
    existing = _get_nested(data, path)
    if existing is None or not isinstance(existing, dict):
        _set_nested(data, path, value)
    else:
        existing.update(value)


def _reconstruct_sketch_ir(data: dict) -> "SketchIR":
    """Reconstruct a SketchIR from a dict."""
    from .models import (
        Anchor,
        BreathPoint,
        CadenceApproach,
        DynamicEvent,
        HarmonyEvent,
        SketchIR,
    )

    def _anchors(key: str) -> list:
        return [
            Anchor(
                bar=a.get("bar", 1),
                beat=a.get("beat", 1.0),
                pitch_or_degree=a.get("pitch_or_degree", ""),
                weight=a.get("weight", 1.0),
                role=a.get("role", "structural"),
            )
            for a in data.get(key, [])
            if isinstance(a, dict)
        ]

    def _harmony() -> list:
        return [
            HarmonyEvent(
                bar=h.get("bar", 1),
                beat=h.get("beat", 1.0),
                roman=h.get("roman", "I"),
                key=h.get("key", "C"),
                function=h.get("function", "tonic"),
            )
            for h in data.get("harmonic_rhythm", [])
            if isinstance(h, dict)
        ]

    def _dynamics() -> list:
        return [
            DynamicEvent(
                bar=d.get("bar", 1),
                beat=d.get("beat", 1.0),
                level=d.get("level", "mf"),
                hairpin=d.get("hairpin"),
            )
            for d in data.get("dynamic_shape", [])
            if isinstance(d, dict)
        ]

    def _breaths() -> list:
        return [
            BreathPoint(
                bar=b.get("bar", 1),
                beat=b.get("beat", 1.0),
                type=b.get("type", "rest"),
            )
            for b in data.get("breath_points", [])
            if isinstance(b, dict)
        ]

    cadence_data = data.get("cadence", {})
    cadence = (
        CadenceApproach(
            type=cadence_data.get("type", "PAC"),
            approach_bar=cadence_data.get("approach_bar", 7),
            arrival_bar=cadence_data.get("arrival_bar", 8),
            soprano_arrival_degree=cadence_data.get("soprano_arrival_degree", 1),
            bass_motion=cadence_data.get("bass_motion", "V-I"),
        )
        if cadence_data
        else CadenceApproach()
    )

    return SketchIR(
        phrase_id=data.get("phrase_id", ""),
        melody_anchors=_anchors("melody_anchors"),
        bass_anchors=_anchors("bass_anchors"),
        harmonic_rhythm=_harmony(),
        dynamic_shape=_dynamics(),
        breath_points=_breaths(),
        cadence=cadence,
    )


def _reconstruct_layer_event(data: dict) -> LayerEvent:
    """Reconstruct a LayerEvent from a dict."""
    return LayerEvent(
        bar=data.get("bar", 1),
        beat=data.get("beat", 1.0),
        pitch=data.get("pitch", "C4"),
        duration=data.get("duration", "q"),
        role=data.get("role", "structural"),
        dynamic=data.get("dynamic"),
        articulation=data.get("articulation"),
        ornament=data.get("ornament"),
        tie=data.get("tie"),
        slur=data.get("slur"),
        hairpin=data.get("hairpin"),
        expression=data.get("expression"),
        source_layer=data.get("source_layer"),
    )


def _reconstruct_layer_ir(data: dict) -> "LayerIR":
    """Reconstruct a LayerIR from a dict."""
    from .models import LayerIR

    def _events(key: str) -> list:
        raw = data.get(key)
        if raw and isinstance(raw, list):
            return [_reconstruct_layer_event(e) for e in raw if isinstance(e, dict)]
        return []

    meter = data.get("meter", [4, 4])
    if isinstance(meter, list):
        meter = tuple(meter)

    return LayerIR(
        phrase_id=data.get("phrase_id", ""),
        instrumentation=data.get("instrumentation", "solo_piano"),
        principal_line=_events("principal_line"),
        bass_foundation=_events("bass_foundation"),
        response_layer=_events("response_layer"),
        counter_reply=_events("counter_reply"),
        ornamental_surface=_events("ornamental_surface"),
        foreground=_events("foreground") or None,
        countermelody=_events("countermelody") or None,
        harmonic_mass=_events("harmonic_mass") or None,
        rhythmic_motor=_events("rhythmic_motor") or None,
        color_layer=_events("color_layer") or None,
        punctuation=_events("punctuation") or None,
        key=data.get("key", "C"),
        meter=meter,
        bar_count=data.get("bar_count", 4),
    )


def load_layer_ir_from_dict(data: dict) -> "LayerIR":
    """Build LayerIR from JSON-compatible dict (for agent-authored note commits)."""
    return _reconstruct_layer_ir(data)


class PieceGraph:
    """
    The single source of truth for a SCALES composition.

    All skills read from and write patches to this graph.
    The graph is persisted as a single JSON file with full audit trail.
    """

    def __init__(self):
        self.piece_id: str = ""
        self.mode: str = CompositionMode.COMPOSE_FROM_TEXT.value
        self.created_at: str = _now_iso()

        self.contract: PieceContract = PieceContract()
        self.style_dna: StyleDNA = StyleDNA()
        self.narrative: NarrativeArc = NarrativeArc()
        self.form: FormGraph = FormGraph()
        self.motif_bank: Dict[str, MotifObject] = {}
        self.phrases: Dict[str, PhraseState] = {}

        self.phase: str = PipelinePhase.INIT.value
        self.revision_history: List[RevisionEntry] = []
        self.output_paths: Dict[str, str] = {}

        # v6 additions
        self.work_graph: Optional[WorkGraph] = None
        self.style_program: Optional[StyleProgram] = None
        self.section_contracts: Dict[str, SectionContract] = {}
        self.context_traces: Dict[str, ContextTrace] = {}
        self.context_utilization: Optional[ContextUtilizationReport] = None
        self.style_review_reports: Dict[str, Any] = {}

        # Persisted CrossScaleLedger state (raw dict, schema-versioned) —
        # carries musical promises/debts across runs and movements
        self.cross_scale_ledger: Optional[Dict[str, Any]] = None

        # Internal dict representation for patching
        self._data: Dict[str, Any] = {}

    def _to_data(self) -> Dict[str, Any]:
        """Serialize the graph to a dict."""
        data = {
            "piece_id": self.piece_id,
            "mode": self.mode,
            "created_at": self.created_at,
            "contract": _deep_serialize(self.contract),
            "style_dna": _deep_serialize(self.style_dna),
            "narrative": _deep_serialize(self.narrative),
            "form": _deep_serialize(self.form),
            "motif_bank": {k: _deep_serialize(v) for k, v in self.motif_bank.items()},
            "phrases": {k: _deep_serialize(v) for k, v in self.phrases.items()},
            "phase": self.phase,
            "revision_history": [_deep_serialize(r) for r in self.revision_history],
            "output_paths": self.output_paths,
        }

        # v6 fields — serialize if present
        if self.style_program:
            data["style_program"] = _deep_serialize(self.style_program)
        if self.work_graph:
            data["work_graph"] = _deep_serialize(self.work_graph)
        if self.section_contracts:
            data["section_contracts"] = {
                k: _deep_serialize(v) for k, v in self.section_contracts.items()
            }
        if self.context_traces:
            data["context_traces"] = {k: _deep_serialize(v) for k, v in self.context_traces.items()}
        if self.context_utilization:
            data["context_utilization"] = _deep_serialize(self.context_utilization)
        if hasattr(self, "style_review_reports"):
            data["style_review_reports"] = _deep_serialize(self.style_review_reports)
        if getattr(self, "cross_scale_ledger", None):
            data["cross_scale_ledger"] = self.cross_scale_ledger

        return data

    def patch(
        self, path: str, operation: str, value: Any, skill: str = "", reason: str = ""
    ) -> bool:
        """Apply an atomic patch to the graph.

        Operations: set, append, merge, delete
        """
        data = self._to_data()

        if operation == "set":
            _set_nested(data, path, value)
        elif operation == "append":
            _append_nested(data, path, value)
        elif operation == "merge":
            _merge_nested(data, path, value)
        elif operation == "delete":
            if not _delete_nested(data, path):
                return False
        else:
            return False

        # Record in audit trail
        entry = RevisionEntry(
            timestamp=_now_iso(),
            skill=skill,
            path=path,
            operation=operation,
            reason=reason,
        )

        self._data = data
        self._load_from_data(data)
        self.revision_history.append(entry)
        return True

    def read(self, path: str = "") -> Any:
        """Read a value from the graph using dot-separated path."""
        data = self._to_data()
        if not path:
            return data
        return _get_nested(data, path)

    def _load_from_data(self, data: Dict[str, Any]) -> None:
        """Load graph state from a dict (used after patching and loading)."""
        self.piece_id = data.get("piece_id", "")
        self.mode = data.get("mode", CompositionMode.COMPOSE_FROM_TEXT.value)
        self.created_at = data.get("created_at", "")
        self.phase = data.get("phase", PipelinePhase.INIT.value)
        self.output_paths = data.get("output_paths", {})

        # Audit trail — without this, every load+save cycle wiped history
        self.revision_history = []
        for entry in data.get("revision_history", []):
            if isinstance(entry, dict):
                self.revision_history.append(
                    RevisionEntry(
                        **{
                            k: v
                            for k, v in entry.items()
                            if k in {f.name for f in fields(RevisionEntry)}
                        }
                    )
                )

        # Persisted cross-scale ledger (raw dict; reconstructed on demand
        # via CrossScaleLedger.from_dict — load defensively)
        csl = data.get("cross_scale_ledger")
        self.cross_scale_ledger = csl if isinstance(csl, dict) else None

        # Contract
        c = data.get("contract", {})
        self.contract = (
            PieceContract(
                **{k: v for k, v in c.items() if k in {f.name for f in fields(PieceContract)}}
            )
            if isinstance(c, dict)
            else PieceContract()
        )

        # FormGraph reconstruction
        form_data = data.get("form", {})
        self.form = FormGraph()
        for sec_id, sec_data in form_data.get("sections", {}).items():
            if isinstance(sec_data, dict):
                from .models import SectionSpec

                self.form.sections[sec_id] = SectionSpec(
                    id=sec_data.get("id", sec_id),
                    movement_id=sec_data.get("movement_id", ""),
                    role=sec_data.get("role", ""),
                    key=sec_data.get("key", "C"),
                    bar_start=sec_data.get("bar_start", 1),
                    bar_end=sec_data.get("bar_end", 8),
                    phrase_ids=sec_data.get("phrase_ids", []),
                )

        # Phrases reconstruction
        phrases_data = data.get("phrases", {})
        self.phrases = {}
        for pid, pdata in phrases_data.items():
            if isinstance(pdata, dict):
                ps = PhraseState(status=pdata.get("status", PhraseStatus.PLANNED.value))
                slot_data = pdata.get("slot", {})
                if isinstance(slot_data, dict):
                    meter = slot_data.get("meter", [4, 4])
                    if isinstance(meter, list):
                        meter = tuple(meter)
                    # Reconstruct texture_plan
                    from .models import BarTexturePlan

                    texture_plan = []
                    for tp in slot_data.get("texture_plan", []):
                        if isinstance(tp, dict):
                            texture_plan.append(
                                BarTexturePlan(
                                    rh_texture=tp.get("rh_texture", "singing_melody"),
                                    lh_texture=tp.get("lh_texture", "alberti"),
                                    rh_density_target=tp.get("rh_density_target", 8),
                                    lh_density_target=tp.get("lh_density_target", 6),
                                    gesture_family=tp.get("gesture_family", ""),
                                )
                            )

                    ps.slot = PhraseSlot(
                        phrase_id=slot_data.get("phrase_id", pid),
                        section_id=slot_data.get("section_id", ""),
                        bar_start=slot_data.get("bar_start", 1),
                        bar_count=slot_data.get("bar_count", 4),
                        function=slot_data.get("function", "presentation"),
                        cadence_target=slot_data.get("cadence_target", "none"),
                        cadence_bar=slot_data.get("cadence_bar"),
                        key=slot_data.get("key", "C"),
                        meter=meter,
                        tempo_bpm=slot_data.get("tempo_bpm", 120),
                        harmony_plan=slot_data.get("harmony_plan", []),
                        texture_plan=texture_plan,
                    )
                # Reconstruct sketch SketchIR if present
                sketch_data = pdata.get("sketch")
                if sketch_data and isinstance(sketch_data, dict):
                    ps.sketch = _reconstruct_sketch_ir(sketch_data)

                # Reconstruct realized LayerIR if present
                realized_data = pdata.get("realized")
                if realized_data and isinstance(realized_data, dict):
                    ps.realized = _reconstruct_layer_ir(realized_data)
                ps.agent_authored = bool(pdata.get("agent_authored", False))
                # Per-phrase context trace (briefed exemplars, composed_blind
                # flag) — a plain dict; preserve it across save/load so the
                # anti-skip check at commit can read what the brief surfaced.
                ps.context_trace = pdata.get("context_trace")
                self.phrases[pid] = ps

        # Motif bank
        motif_data = data.get("motif_bank", {})
        self.motif_bank = {}
        for mid, mdata in motif_data.items():
            if isinstance(mdata, dict):
                self.motif_bank[mid] = MotifObject(
                    motif_id=mdata.get("motif_id", mid),
                    character=mdata.get("character", ""),
                    scale_degree_contour=mdata.get("scale_degree_contour", []),
                    interval_contour=mdata.get("interval_contour", []),
                    rhythm_cell=mdata.get("rhythm_cell", []),
                    allowed_transforms=mdata.get("allowed_transforms", []),
                )

        # Reconstruct StyleDNA scalar fields. It is serialized on save but was
        # never read back, so composer_id/tier were silently lost on load —
        # which made composer/style RESOLUTION fall back to the default
        # (every loaded piece looked like Mozart). Restore at least the fields
        # that drive resolution and arming.
        dna_data = data.get("style_dna")
        if isinstance(dna_data, dict):
            for fld in ("composer_id", "tier", "active_period"):
                if fld in dna_data and hasattr(self.style_dna, fld):
                    setattr(self.style_dna, fld, dna_data[fld])
            for fld in (
                "lh_distribution",
                "rh_distribution",
                "density_targets",
                "transition_matrix",
            ):
                v = dna_data.get(fld)
                if isinstance(v, dict) and v and hasattr(self.style_dna, fld):
                    setattr(self.style_dna, fld, v)

        # v6: Reconstruct StyleProgram from compiled packs if data indicates
        # one was used (avoids serializing the full program in the graph JSON)
        sp_data = data.get("style_program")
        if sp_data and isinstance(sp_data, dict):
            # Reconstruct by re-loading from compiled packs
            composer_id = sp_data.get("dna", {}).get("composer_id", "")
            if composer_id:
                try:
                    from .style_resolver import StyleResolver

                    resolver = StyleResolver()
                    self.style_program = resolver.resolve_program(composer_id)
                except Exception:
                    self.style_program = None
            else:
                self.style_program = None
        else:
            self.style_program = None

        # v6: Reconstruct ContextTraces
        ct_data = data.get("context_traces", {})
        self.context_traces = {}
        for ct_id, ct_dict in ct_data.items():
            if isinstance(ct_dict, dict):
                self.context_traces[ct_id] = ContextTrace(
                    phrase_id=ct_dict.get("phrase_id", ct_id),
                    corpus_patterns_used=ct_dict.get("corpus_patterns_used", []),
                    corpus_bars_used=ct_dict.get("corpus_bars_used", []),
                    gestures_applied=ct_dict.get("gestures_applied", []),
                    devices_used=ct_dict.get("devices_used", []),
                    fingerprints_expressed=ct_dict.get("fingerprints_expressed", []),
                    breathing_rules_applied=ct_dict.get("breathing_rules_applied", []),
                    ornament_intents_applied=ct_dict.get("ornament_intents_applied", []),
                    fallback_bar_count=ct_dict.get("fallback_bar_count", 0),
                    donor_bar_count=ct_dict.get("donor_bar_count", 0),
                    total_bar_count=ct_dict.get("total_bar_count", 0),
                )

        # v6: SectionContracts
        sc_data = data.get("section_contracts", {})
        self.section_contracts = {}
        for sc_id, sc_dict in sc_data.items():
            if isinstance(sc_dict, dict):
                self.section_contracts[sc_id] = SectionContract(
                    id=sc_dict.get("id", sc_id),
                    movement_id=sc_dict.get("movement_id", ""),
                    role=sc_dict.get("role", ""),
                    key=sc_dict.get("key", "C"),
                    bar_start=sc_dict.get("bar_start", 1),
                    bar_end=sc_dict.get("bar_end", 8),
                    phrase_ids=sc_dict.get("phrase_ids", []),
                    cadence_path=sc_dict.get("cadence_path", []),
                    energy_envelope=sc_dict.get("energy_envelope", []),
                    texture_family=sc_dict.get("texture_family", ""),
                    transition_debt_in=sc_dict.get("transition_debt_in", ""),
                    transition_debt_out=sc_dict.get("transition_debt_out", ""),
                    rhetorical_goals=sc_dict.get("rhetorical_goals", []),
                    salience=sc_dict.get("salience", "normal"),
                    development_techniques=sc_dict.get("development_techniques", []),
                )

        # v6: WorkGraph
        wg_data = data.get("work_graph")
        if wg_data and isinstance(wg_data, dict):
            from .models import TonalItinerary

            self.work_graph = WorkGraph(
                work_id=wg_data.get("work_id", ""),
                movement_count=wg_data.get("movement_count", 1),
                emotional_narrative=wg_data.get("emotional_narrative", ""),
                finale_payoff=wg_data.get("finale_payoff", ""),
                tonal_itinerary=TonalItinerary(
                    home_key=wg_data.get("tonal_itinerary", {}).get("home_key", "C"),
                    movement_keys=wg_data.get("tonal_itinerary", {}).get("movement_keys", {}),
                ),
            )
            for mvt_data in wg_data.get("movements", []):
                if isinstance(mvt_data, dict):
                    self.work_graph.movements.append(
                        MovementContract(
                            id=mvt_data.get("id", ""),
                            form=mvt_data.get("form", ""),
                            key=mvt_data.get("key", "C"),
                            tempo_bpm=mvt_data.get("tempo_bpm", 120),
                            meter=tuple(mvt_data.get("meter", [4, 4])),
                            tempo_marking=mvt_data.get("tempo_marking", ""),
                            character=mvt_data.get("character", ""),
                            role_in_work=mvt_data.get("role_in_work", ""),
                        )
                    )
        else:
            self.work_graph = None

        self.context_utilization = None

        self.style_review_reports = dict(data.get("style_review_reports") or {})

        # Store raw data
        self._data = data

    def save(self, path: str) -> None:
        """Save the graph to a JSON file."""
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = self._to_data()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, path: str) -> "PieceGraph":
        """Load a graph from a JSON file."""
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"PieceGraph not found: {path}")
        with open(filepath) as f:
            data = json.load(f)

        graph = cls()
        graph._data = data
        graph._load_from_data(data)
        return graph

    @classmethod
    def create(cls, piece_id: str, mode: str, description: str = "") -> "PieceGraph":
        """Create a new PieceGraph."""
        graph = cls()
        graph.piece_id = piece_id
        graph.mode = mode
        graph.created_at = _now_iso()
        graph.contract = PieceContract(
            piece_id=piece_id,
            mode=mode,
            description=description,
        )
        graph.phase = PipelinePhase.INIT.value
        return graph

    def add_phrase(self, phrase_id: str, slot: PhraseSlot) -> None:
        """Add a phrase to the graph."""
        self.phrases[phrase_id] = PhraseState(
            slot=slot,
            status=PhraseStatus.PLANNED.value,
        )

    def update_phrase_status(
        self, phrase_id: str, status: str, skill: str = "", reason: str = ""
    ) -> None:
        """Update a phrase's pipeline status."""
        if phrase_id in self.phrases:
            self.phrases[phrase_id].status = status
            self.revision_history.append(
                RevisionEntry(
                    timestamp=_now_iso(),
                    skill=skill,
                    path=f"phrases.{phrase_id}.status",
                    operation="set",
                    reason=reason,
                )
            )

    def set_phrase_sketch(self, phrase_id: str, sketch: SketchIR) -> None:
        """Set the sketch for a phrase."""
        if phrase_id in self.phrases:
            self.phrases[phrase_id].sketch = sketch
            self.phrases[phrase_id].status = PhraseStatus.SKETCHED.value

    def set_phrase_candidates(self, phrase_id: str, candidates: List[CandidateNode]) -> None:
        """Set the realization candidates for a phrase."""
        if phrase_id in self.phrases:
            self.phrases[phrase_id].candidates = candidates

    def commit_phrase(self, phrase_id: str, realized: LayerIR) -> None:
        """Commit a winning realization to a phrase."""
        if phrase_id in self.phrases:
            self.phrases[phrase_id].realized = realized
            self.phrases[phrase_id].status = PhraseStatus.REALIZED.value

    def commit_agent_phrase(
        self, phrase_id: str, realized: LayerIR, *, set_agent_flag: bool = True
    ) -> None:
        """Commit LayerIR written by the agent (Claude), not the SCALES engine.

        Marks ``agent_authored`` so ``run_scales_section`` will not replace
        this surface with engine candidates (beam search keeps this layer).
        """
        self.commit_phrase(phrase_id, realized)
        if phrase_id in self.phrases and set_agent_flag:
            self.phrases[phrase_id].agent_authored = True

    def approve_phrase(self, phrase_id: str, review: ReviewResult) -> None:
        """Approve a phrase after review."""
        if phrase_id in self.phrases:
            self.phrases[phrase_id].review = review
            self.phrases[phrase_id].status = PhraseStatus.APPROVED.value

    def get_section_phrases(self, section_id: str) -> List[str]:
        """Get ordered phrase IDs for a section."""
        if section_id in self.form.sections:
            return self.form.sections[section_id].phrase_ids
        return []

    def get_status_summary(self) -> Dict[str, Any]:
        """Get a quick status summary."""
        total = len(self.phrases)
        by_status = {}
        for ps in self.phrases.values():
            by_status[ps.status] = by_status.get(ps.status, 0) + 1
        return {
            "piece_id": self.piece_id,
            "mode": self.mode,
            "phase": self.phase,
            "total_phrases": total,
            "by_status": by_status,
            "output_paths": self.output_paths,
        }
