"""
PieceGraph — the single source of truth for a composition.

Replaces the scattered JSON files (plan.json, narrative-arc.json,
form_graph.json, motif_bank.json, continuity.json, state.json) with
one auditable, patchable graph.
"""

from __future__ import annotations

import json
from dataclasses import asdict, fields
from dataclasses import fields as dataclass_fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .atomic_io import write_json_atomic
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


def _coerce(hint, raw):
    """Coerce one serialized value to what its type hint asks for.

    Recurses through the containers the models actually use:
    ``Optional[X]``, ``List[X]``, ``Dict[K, V]`` and ``Tuple[...]``, in any
    nesting. The earlier version handled only a bare ``List[Dataclass]`` and a
    bare dataclass, so a field typed ``Optional[List[LayerEvent]]`` — which is
    every orchestra layer — or ``Dict[str, List[LayerEvent]]`` — which is
    `inner_voices`, the third and fourth contrapuntal voices — fell through to
    the raw branch and came back as **plain dicts pretending to be notes**.
    Nothing downstream type-checks, so those layers reached the assembler as
    dicts and simply produced no sound.
    """
    import dataclasses
    import typing

    if hint is None:
        return raw
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin is typing.Union:  # includes Optional[X]
        if raw is None:
            return None
        inner = [a for a in args if a is not type(None)]
        return _coerce(inner[0], raw) if len(inner) == 1 else raw
    if origin is list:
        if not isinstance(raw, list):
            return raw
        return [_coerce(args[0], x) for x in raw] if args else list(raw)
    if origin is dict:
        if not isinstance(raw, dict):
            return raw
        return {k: _coerce(args[1], v) for k, v in raw.items()} if len(args) == 2 else dict(raw)
    if origin is tuple:
        return tuple(raw) if isinstance(raw, list) else raw
    if dataclasses.is_dataclass(hint) and isinstance(raw, dict):
        return _dataclass_from_dict(hint, raw)
    return raw


# Where pieces live, so an output path can be recorded durably.
_WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent / "workspace"


def record_output(piece_graph, kind: str, filepath) -> None:
    """Record where an output was written, and PERSIST it.

    ``assemble`` and ``render_midi`` both set ``piece_graph.output_paths[...]``
    and neither saved the graph, while the documented flow is "load the graph,
    call the function, print the path" — so the field was written to an object
    the caller then discarded. Measured over the twelve pieces in ``workspace/``,
    ``output_paths`` is populated in four; the rest have been assembled and have
    no record of it, so ``get_status`` reports a piece with no output.

    Saving is best-effort: a graph assembled to a scratch directory, or one whose
    workspace has been removed, must not turn a successful export into an error.
    """
    piece_graph.output_paths[kind] = str(filepath)
    piece_id = getattr(piece_graph, "piece_id", "")
    if not piece_id:
        return
    target = _WORKSPACE_ROOT / piece_id / "piece_graph.json"
    if not target.exists():
        return
    try:
        piece_graph.save(str(target))
    except (OSError, TypeError, ValueError):
        pass


def _dataclass_from_dict(cls, data):
    """Rebuild a dataclass from a dict by its OWN declared fields.

    Hand-enumerated loaders are how this project keeps losing state: the
    PhraseSlot loader listed ten fields and silently dropped every other one, so
    `curves` (the narrative energy arc), `motif_transforms` (the theme
    placements the theme planner attaches at plan time), `harmony_detail`,
    `pickup_beats`, `continuation` and `notes` all vanished on the first save/load
    round-trip. Adding a field to a model must not require remembering to add it
    here too — so this reads the field list from the dataclass and recurses into
    nested dataclasses through every container in `_coerce`.

    `test_piece_graph_roundtrip.py` fails if any model loses a field.
    """
    import dataclasses
    import typing

    if not dataclasses.is_dataclass(cls):
        return data
    if not isinstance(data, dict):
        return cls()
    try:
        hints = typing.get_type_hints(cls)
    except Exception:
        hints = {}
    kwargs = {}
    for f in dataclasses.fields(cls):
        if f.name not in data:
            continue
        kwargs[f.name] = _coerce(hints.get(f.name), data[f.name])
    try:
        return cls(**kwargs)
    except TypeError:
        return cls()


def _slot_from_dict(slot_data):
    """Rebuild a PhraseSlot from serialized form, losing nothing."""
    slot = _dataclass_from_dict(PhraseSlot, slot_data)
    if isinstance(slot.meter, list):
        slot.meter = tuple(slot.meter)
    return slot


def _reconstruct_sketch_ir(data: dict) -> "SketchIR":
    """Rebuild a SketchIR from serialized form, losing nothing.

    This was a hand-enumerated loader that named six of SketchIR's eleven
    fields, so `texture_plan`, `expression_marks`, `motif_placements`,
    `entry_signature` and `exit_signature` were **silently dropped on every
    load**. The sketch is what Claude writes before composing the surface: the
    texture intent per bar, the expression marks, and the motif placements that
    tie a phrase to the piece's theme all survived the commit that wrote them
    and vanished the next time the graph was read from disk.

    Drive the field list off the dataclass — see `_dataclass_from_dict`, and
    `test_piece_graph_roundtrip.py`, which fails if any model loses a field on
    a save/load round-trip.
    """
    from .models import SketchIR

    return _dataclass_from_dict(SketchIR, data or {})


def _reconstruct_layer_event(data: dict) -> LayerEvent:
    """Reconstruct a LayerEvent from a dict.

    Hand-enumerating the field list here is a standing hazard: a field added to
    LayerEvent and not added here is silently dropped on every load, so the
    notation survives one commit and disappears the next time the graph is
    read. Drive the list off the dataclass instead of restating it.
    """
    from dataclasses import fields as _fields

    kwargs = {}
    for f in _fields(LayerEvent):
        if f.name in data:
            kwargs[f.name] = data[f.name]
    return LayerEvent(**kwargs)


def _reconstruct_layer_ir(data: dict) -> "LayerIR":
    """Rebuild a LayerIR from serialized form, losing nothing.

    Hand-enumerating the field list here is a standing hazard: a field added to
    LayerIR (or to LayerEvent) and not added here is silently dropped on every
    load, so the notation survives one commit and disappears the next time the
    graph is read. `inner_voices` (three- and four-voice counterpoint) and
    `pickup_beats` (the anacrusis marker) were both lost that way. The field
    list now comes from the dataclass.
    """
    from .models import LayerIR

    layer = _dataclass_from_dict(LayerIR, data or {})
    if isinstance(layer.meter, list):
        layer.meter = tuple(layer.meter)
    # The orchestra layers are Optional and the assembler branches on `is None`
    # to decide whether a part exists at all; an empty list would engrave a
    # silent staff for every instrument the piece does not use.
    for name in (
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    ):
        if not getattr(layer, name, None):
            setattr(layer, name, None)
    layer.pickup_beats = float(layer.pickup_beats or 0)
    return layer


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
        self.principal_theme_id: str = ""  # elected recurring MOTIF (theme_planner)
        # The PHRASE the theme surface was captured from. Kept separate because
        # `principal_theme_id` names a motif: one field holding both meanings is
        # what made two brief checks permanently false.
        self.principal_theme_phrase_id: str = ""
        self.principal_theme_surface: Optional[LayerIR] = None  # the COMPOSED theme, to develop
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

        # Whole-score reference study — the agent's OWN analysis of complete
        # reference pieces it read before composing (form, themes, harmonic
        # language, texture arc, "what makes it work"). Keyed by
        # "<composer>/<source>". Feeds the planning step and every phrase
        # brief, so the agent composes from its own understanding of real
        # scores, not just from statistically-retrieved disconnected bars.
        self.reference_studies: Dict[str, Any] = {}

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
            "principal_theme_id": self.principal_theme_id,
            "principal_theme_phrase_id": self.principal_theme_phrase_id,
            "principal_theme_surface": (
                _deep_serialize(self.principal_theme_surface)
                if self.principal_theme_surface
                else None
            ),
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
        if getattr(self, "reference_studies", None):
            data["reference_studies"] = _deep_serialize(self.reference_studies)
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

        # Contract. Filtering the top-level keys left every NESTED dataclass —
        # target, source, style, locks, constraints — as a raw dict, so
        # `contract.target.instrumentation` worked before a save and raised
        # after a load. Callers had grown "dict or dataclass" branches to cope.
        c = data.get("contract", {})
        self.contract = (
            _dataclass_from_dict(PieceContract, c) if isinstance(c, dict) else PieceContract()
        )

        # NarrativeArc reconstruction — without this, narrative was serialized
        # but never loaded back, so the agent's authored emotional intent
        # (section.character) never survived to compose time. Defensive,
        # field-filtered like the other dataclass loads.
        nar_data = data.get("narrative", {})
        self.narrative = (
            _dataclass_from_dict(NarrativeArc, nar_data)
            if isinstance(nar_data, dict)
            else NarrativeArc()
        )

        # FormGraph. `movements` was not loaded AT ALL — a multi-movement work
        # lost its movement structure on every read — and SectionSpec was
        # hand-listed at seven fields, so anything added to it was dropped.
        from .models import SectionSpec

        form_data = data.get("form", {}) or {}
        self.form = FormGraph()
        if isinstance(form_data, dict):
            for sec_id, sec_data in (form_data.get("sections") or {}).items():
                if isinstance(sec_data, dict):
                    sec_data.setdefault("id", sec_id)
                    self.form.sections[sec_id] = _dataclass_from_dict(SectionSpec, sec_data)
            for mv in form_data.get("movements") or []:
                if isinstance(mv, dict):
                    self.form.movements.append(_dataclass_from_dict(MovementContract, mv))
            for fld in ("form_type", "total_bars", "key_scheme"):
                if fld in form_data and hasattr(self.form, fld):
                    setattr(self.form, fld, form_data[fld])

        # Phrases reconstruction
        phrases_data = data.get("phrases", {})
        self.phrases = {}
        for pid, pdata in phrases_data.items():
            if isinstance(pdata, dict):
                ps = PhraseState(status=pdata.get("status", PhraseStatus.PLANNED.value))
                slot_data = pdata.get("slot", {})
                if isinstance(slot_data, dict):
                    slot_data.setdefault("phrase_id", pid)
                    ps.slot = _slot_from_dict(slot_data)
                # Reconstruct sketch SketchIR if present
                sketch_data = pdata.get("sketch")
                if sketch_data and isinstance(sketch_data, dict):
                    ps.sketch = _reconstruct_sketch_ir(sketch_data)

                # Reconstruct realized LayerIR if present
                realized_data = pdata.get("realized")
                if realized_data and isinstance(realized_data, dict):
                    ps.realized = _reconstruct_layer_ir(realized_data)
                ps.agent_authored = bool(pdata.get("agent_authored", False))
                # Every REMAINING field, driven off the dataclass rather than
                # hand-listed. This loader named five of PhraseState's thirteen
                # fields, so `craft_check` (the craft checklist) and `review`
                # (the fresh-ears critic's own verdict) were written on save and
                # silently dropped on load — the reviewer's judgement did not
                # survive to the revision pass that was supposed to act on it.
                # `slot`, `sketch` and `realized` need real reconstruction and
                # are handled above; the rest are plain JSON.
                # Fields whose type is a dataclass have to be REBUILT, not
                # assigned: `ps.review.passed` raises on a raw dict, and the
                # revision pass reads exactly that.
                _typed = {
                    "review": ReviewResult,
                    "craft_check": None,  # PhraseCraftCheck lives in craft_checker
                    "candidates": CandidateNode,
                    "sketch_candidates": SketchIR,
                }
                _handled = {"slot", "sketch", "realized", "agent_authored", "status"}
                for _f in dataclass_fields(PhraseState):
                    if _f.name in _handled or _f.name not in pdata:
                        continue
                    raw = pdata[_f.name]
                    target = _typed.get(_f.name)
                    if _f.name == "craft_check" and isinstance(raw, dict):
                        from .craft_checker import PhraseCraftCheck

                        target = PhraseCraftCheck
                    if target is not None and isinstance(raw, dict):
                        raw = _dataclass_from_dict(target, raw)
                    elif target is not None and isinstance(raw, list):
                        raw = [
                            _dataclass_from_dict(target, x) if isinstance(x, dict) else x
                            for x in raw
                        ]
                    setattr(ps, _f.name, raw)
                self.phrases[pid] = ps

        # Motif bank
        motif_data = data.get("motif_bank", {})
        self.motif_bank = {}
        for mid, mdata in motif_data.items():
            if isinstance(mdata, dict):
                # Every field, not six of twelve. `recognition_anchor` (what
                # makes the motif recognizable) and `accent_profile` (where it
                # leans) were serialized on save and silently dropped on load, so
                # a motif came back without the two fields that define its
                # identity — and the appearances list, which is how the piece
                # knows where the motif has already been.
                self.motif_bank[mid] = MotifObject(
                    motif_id=mdata.get("motif_id", mid),
                    character=mdata.get("character", ""),
                    scale_degree_contour=mdata.get("scale_degree_contour", []) or [],
                    interval_contour=mdata.get("interval_contour", []) or [],
                    rhythm_cell=mdata.get("rhythm_cell", []) or [],
                    accent_profile=mdata.get("accent_profile", []) or [],
                    recognition_anchor=mdata.get("recognition_anchor", {}) or {},
                    phrase_functions=mdata.get("phrase_functions", []) or [],
                    harmonic_contexts=mdata.get("harmonic_contexts", []) or [],
                    accompaniment_hints=mdata.get("accompaniment_hints", []) or [],
                    typical_registers=[
                        tuple(r) for r in (mdata.get("typical_registers") or []) if r
                    ],
                    allowed_transforms=mdata.get("allowed_transforms", []) or [],
                    appearances=mdata.get("appearances", []) or [],
                )
        self.principal_theme_id = data.get("principal_theme_id", "")
        self.principal_theme_phrase_id = data.get("principal_theme_phrase_id", "")
        pts = data.get("principal_theme_surface")
        self.principal_theme_surface = _reconstruct_layer_ir(pts) if isinstance(pts, dict) else None

        # Reconstruct StyleDNA scalar fields. It is serialized on save but was
        # never read back, so composer_id/tier were silently lost on load —
        # which made composer/style RESOLUTION fall back to the default
        # (every loaded piece looked like Mozart). Restore at least the fields
        # that drive resolution and arming.
        # Seven of StyleDNA's eighteen fields were read back. The COMPOSER
        # FINGERPRINTS (the traits that make a voice recognizable), the cadence
        # vocabulary, the chromatic techniques, the progression graph, the form
        # templates, the orchestration roles and the phrase-structure rules were
        # all serialized on save and destroyed on load — so a piece re-opened
        # after planning had almost none of the compiled style profile left.
        dna_data = data.get("style_dna")
        if isinstance(dna_data, dict):
            self.style_dna = _dataclass_from_dict(StyleDNA, dna_data)

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

        # v6: ContextTraces, SectionContracts and the WorkGraph.
        #
        # All three were hand-enumerated and all three dropped fields:
        # SectionContract lost `orchestration_role_map` and
        # `theme_families_active`; TonalItinerary lost `key_relationships` and
        # `progressive_tonality`; MovementContract lost `sections`,
        # `theme_families_active`, `development_strategies`, `recap_logic`,
        # `coda_logic`, `contrast_with_previous` and `orchestration_zones` —
        # which is most of what makes a movement contract worth having. A
        # symphony planned with cyclic themes and a recapitulation strategy read
        # those fields back as empty on the very next tool call.
        self.context_traces = {
            ct_id: _dataclass_from_dict(ContextTrace, ct_dict)
            for ct_id, ct_dict in (data.get("context_traces") or {}).items()
            if isinstance(ct_dict, dict)
        }
        for ct_id, ct in self.context_traces.items():
            if not ct.phrase_id:
                ct.phrase_id = ct_id

        self.section_contracts = {
            sc_id: _dataclass_from_dict(SectionContract, sc_dict)
            for sc_id, sc_dict in (data.get("section_contracts") or {}).items()
            if isinstance(sc_dict, dict)
        }
        for sc_id, sc in self.section_contracts.items():
            if not sc.id:
                sc.id = sc_id

        wg_data = data.get("work_graph")
        if wg_data and isinstance(wg_data, dict):
            self.work_graph = _dataclass_from_dict(WorkGraph, wg_data)
            for mvt in self.work_graph.movements:
                if isinstance(getattr(mvt, "meter", None), list):
                    mvt.meter = tuple(mvt.meter)
        else:
            self.work_graph = None

        self.context_utilization = None

        self.style_review_reports = dict(data.get("style_review_reports") or {})

        self.reference_studies = dict(data.get("reference_studies") or {})

        # Store raw data
        self._data = data

    def save(self, path: str) -> None:
        """Save the graph to a JSON file, atomically.

        `open(path, "w")` truncates before it writes, so this file was empty for
        as long as the write took — and the graph is the SINGLE SOURCE OF TRUTH
        for a whole composition. Anything interrupting the write left an empty
        or half-written file where hours of work had been: a crash, a Ctrl-C, a
        full disk. A concurrent reader saw the same thing, which is how it
        surfaced — a test fixture reading a graph mid-save got
        `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, the
        signature of decoding an empty string.

        Write beside it, flush to the platter, then rename. `os.replace` is
        atomic, so a reader sees either the whole previous file or the whole new
        one and never a partial one.
        """
        filepath = Path(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        data = self._to_data()
        # Same directory: `os.replace` is only atomic within one filesystem.
        write_json_atomic(filepath, data, indent=2, default=str)

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
