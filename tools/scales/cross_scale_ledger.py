"""
CrossScaleLedger — tracks musical obligations across all compositional scales.

Extends ExpectationLedger with:
- Work-level obligations (cross-movement recalls, finale payoffs)
- Movement-level obligations (development promises, recap obligations)
- Section-level obligations (cadence paths, thematic completions)
- Multi-domain tracking: motif, harmony, cadence, orchestration, rhythm,
  energy, form, recall
- ThemeGenealogy for tracking theme lives across the work
- ClimaxReservationMap for managing climax budgets
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .enums import (
    ExpectationStatus,
    WorkScale,
)
from .expectation_ledger import ExpectationLedger
from .models import (
    CrossScaleExpectation,
    OrchestrationMemory,
    ThemeGenealogy,
)


class CrossScaleLedger:
    """Tracks promises, debts, cooldowns, prohibitions, and identity locks
    across all compositional scales and musical domains.

    The phrase-level ledger (ExpectationLedger) is preserved as a delegate
    for backward compatibility. CrossScaleLedger adds work/movement/section
    level tracking.
    """

    def __init__(self):
        self.expectations: List[CrossScaleExpectation] = []
        self.theme_genealogy: Dict[str, ThemeGenealogy] = {}
        self.orchestration_memory: OrchestrationMemory = OrchestrationMemory()
        self._phrase_ledger: ExpectationLedger = ExpectationLedger()
        self._next_id: int = 1

    @property
    def phrase_ledger(self) -> ExpectationLedger:
        """Access the phrase-level ledger for backward compatibility."""
        return self._phrase_ledger

    def _gen_id(self) -> str:
        eid = f"csx_{self._next_id:04d}"
        self._next_id += 1
        return eid

    # ─── Adding expectations at each scale ─────────────────────────────

    def add_work_expectation(
        self,
        exp_type: str,
        domain: str,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str] = None,
        expected_form: Optional[str] = None,
        urgency: float = 0.5,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a work-level expectation (e.g., finale payoff, cyclic return)."""
        return self._add(
            WorkScale.WORK.value,
            exp_type,
            domain,
            object_ref,
            introduced_at,
            must_resolve_by,
            expected_form,
            urgency,
            details,
        )

    def add_movement_expectation(
        self,
        exp_type: str,
        domain: str,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str] = None,
        expected_form: Optional[str] = None,
        urgency: float = 0.5,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a movement-level expectation (e.g., development promise, recap obligation)."""
        return self._add(
            WorkScale.MOVEMENT.value,
            exp_type,
            domain,
            object_ref,
            introduced_at,
            must_resolve_by,
            expected_form,
            urgency,
            details,
        )

    def add_section_expectation(
        self,
        exp_type: str,
        domain: str,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str] = None,
        expected_form: Optional[str] = None,
        urgency: float = 0.5,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add a section-level expectation (e.g., cadence path, thematic completion)."""
        return self._add(
            WorkScale.SECTION.value,
            exp_type,
            domain,
            object_ref,
            introduced_at,
            must_resolve_by,
            expected_form,
            urgency,
            details,
        )

    def add_phrase_promise(
        self,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str] = None,
        urgency: float = 0.5,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Delegate to the phrase-level ledger."""
        return self._phrase_ledger.add_promise(
            object_ref, introduced_at, must_resolve_by, urgency=urgency, details=details
        )

    def _add(
        self,
        scale: str,
        exp_type: str,
        domain: str,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str],
        expected_form: Optional[str],
        urgency: float,
        details: Optional[Dict[str, Any]],
    ) -> str:
        eid = self._gen_id()
        self.expectations.append(
            CrossScaleExpectation(
                id=eid,
                scale=scale,
                type=exp_type,
                domain=domain,
                object_ref=object_ref,
                introduced_at=introduced_at,
                must_resolve_by=must_resolve_by,
                expected_form=expected_form,
                urgency=urgency,
                status=ExpectationStatus.OPEN.value,
                details=details or {},
            )
        )
        return eid

    # ─── Querying ──────────────────────────────────────────────────────

    def get_active_at_scale(self, scale: str) -> List[CrossScaleExpectation]:
        """Get all open expectations at a specific scale."""
        return [
            e
            for e in self.expectations
            if e.scale == scale and e.status == ExpectationStatus.OPEN.value
        ]

    def get_all_open(self) -> List[CrossScaleExpectation]:
        return [e for e in self.expectations if e.status == ExpectationStatus.OPEN.value]

    def get_overdue(
        self, current_position: str, position_order: List[str]
    ) -> List[CrossScaleExpectation]:
        """Get expectations that are past their deadline."""
        overdue: List[CrossScaleExpectation] = []
        if current_position not in position_order:
            return overdue

        current_idx = position_order.index(current_position)
        for exp in self.expectations:
            if exp.status != ExpectationStatus.OPEN.value:
                continue
            if exp.must_resolve_by and exp.must_resolve_by in position_order:
                deadline_idx = position_order.index(exp.must_resolve_by)
                if current_idx > deadline_idx:
                    overdue.append(exp)
        return overdue

    def get_due_soon(
        self, current_position: str, position_order: List[str], horizon: int = 2
    ) -> List[CrossScaleExpectation]:
        """Get expectations due within `horizon` positions."""
        due: List[CrossScaleExpectation] = []
        if current_position not in position_order:
            return due

        current_idx = position_order.index(current_position)
        for exp in self.expectations:
            if exp.status != ExpectationStatus.OPEN.value:
                continue
            if exp.must_resolve_by and exp.must_resolve_by in position_order:
                deadline_idx = position_order.index(exp.must_resolve_by)
                if 0 <= deadline_idx - current_idx <= horizon:
                    due.append(exp)
        return due

    # ─── Resolving ─────────────────────────────────────────────────────

    def satisfy(self, exp_id: str, resolved_at: str) -> bool:
        for exp in self.expectations:
            if exp.id == exp_id and exp.status == ExpectationStatus.OPEN.value:
                exp.status = ExpectationStatus.SATISFIED.value
                exp.resolved_at = resolved_at
                return True
        return self._phrase_ledger.satisfy(exp_id, resolved_at)

    def violate(self, exp_id: str, resolved_at: str) -> bool:
        for exp in self.expectations:
            if exp.id == exp_id and exp.status == ExpectationStatus.OPEN.value:
                exp.status = ExpectationStatus.VIOLATED.value
                exp.resolved_at = resolved_at
                return True
        return self._phrase_ledger.violate(exp_id, resolved_at)

    # ─── Scoring ───────────────────────────────────────────────────────

    def score_resolution(
        self, current_position: str, position_order: List[str], scale: Optional[str] = None
    ) -> float:
        """Score how well obligations are being met.

        Returns 0-1. Penalties for overdue and urgency of due-soon.
        """
        score = 1.0

        overdue = self.get_overdue(current_position, position_order)
        if scale:
            overdue = [e for e in overdue if e.scale == scale]
        score -= 0.2 * len(overdue)

        due_soon = self.get_due_soon(current_position, position_order)
        if scale:
            due_soon = [e for e in due_soon if e.scale == scale]
        for exp in due_soon:
            score -= 0.1 * exp.urgency

        # Also include phrase-level score
        phrase_score = self._phrase_ledger.score_phrase_resolution(current_position, position_order)
        score = min(score, phrase_score)

        return max(0.0, score)

    # ─── Future Value ──────────────────────────────────────────────────

    def future_value_penalty(self, current_position: str, position_order: List[str]) -> float:
        """Compute penalty for actions that would deplete future resources.

        A locally pretty choice is bad if it exhausts a climax too early
        or undermines a promised thematic return.

        Returns 0-1 where 0 = no penalty, 1 = severe penalty.
        """
        if current_position not in position_order:
            return 0.0

        current_idx = position_order.index(current_position)
        total = len(position_order)
        remaining_ratio = (total - current_idx) / max(total, 1)

        # Count high-urgency expectations that must still be resolved
        future_obligations = [
            e
            for e in self.expectations
            if e.status == ExpectationStatus.OPEN.value
            and e.urgency >= 0.7
            and e.must_resolve_by
            and e.must_resolve_by in position_order
            and position_order.index(e.must_resolve_by) > current_idx
        ]

        if not future_obligations:
            return 0.0

        # More future obligations with high urgency = higher penalty
        # for doing anything that would compromise them
        return min(1.0, len(future_obligations) * 0.15 * remaining_ratio)

    # ─── Theme Genealogy ───────────────────────────────────────────────

    def register_theme_appearance(
        self,
        theme_id: str,
        phrase_id: str,
        transform: str = "state",
        recognition_score: float = 1.0,
    ) -> None:
        """Record a theme appearance for tracking its life across the work."""
        if theme_id not in self.theme_genealogy:
            self.theme_genealogy[theme_id] = ThemeGenealogy(
                theme_id=theme_id,
                original_statement=phrase_id,
                recognition_score=recognition_score,
            )
        else:
            genealogy = self.theme_genealogy[theme_id]
            genealogy.appearances.append(
                {
                    "phrase_id": phrase_id,
                    "transform": transform,
                    "recognition_score": recognition_score,
                }
            )
            # Update overall recognition — degrades with heavy transforms
            if transform in ("fragment", "liquidate", "invert"):
                genealogy.recognition_score *= 0.9

    def get_theme_genealogy(self, theme_id: str) -> Optional[ThemeGenealogy]:
        return self.theme_genealogy.get(theme_id)

    def get_theme_appearance_count(self, theme_id: str) -> int:
        gen = self.theme_genealogy.get(theme_id)
        if not gen:
            return 0
        return 1 + len(gen.appearances)

    # ─── Serialization ─────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        from .piece_graph import _deep_serialize

        return {
            "version": 1,
            "expectations": [_deep_serialize(e) for e in self.expectations],
            "theme_genealogy": {k: _deep_serialize(v) for k, v in self.theme_genealogy.items()},
            "orchestration_memory": _deep_serialize(self.orchestration_memory),
            "phrase_ledger": self._phrase_ledger.to_dict()
            if hasattr(self._phrase_ledger, "to_dict")
            else {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CrossScaleLedger":
        """Restore a persisted ledger. Defensive: unknown fields ignored,
        malformed entries skipped — an old graph must never fail to load."""
        from dataclasses import fields as dc_fields

        ledger = cls()
        if not isinstance(data, dict):
            return ledger

        exp_fields = {f.name for f in dc_fields(CrossScaleExpectation)}
        for entry in data.get("expectations", []):
            if not isinstance(entry, dict):
                continue
            try:
                exp = CrossScaleExpectation(**{k: v for k, v in entry.items() if k in exp_fields})
                ledger.expectations.append(exp)
                num = int(exp.id.split("_")[1])
                if num >= ledger._next_id:
                    ledger._next_id = num + 1
            except (TypeError, IndexError, ValueError):
                continue

        gen_fields = {f.name for f in dc_fields(ThemeGenealogy)}
        for theme_id, gen in (data.get("theme_genealogy") or {}).items():
            if isinstance(gen, dict):
                try:
                    ledger.theme_genealogy[theme_id] = ThemeGenealogy(
                        **{k: v for k, v in gen.items() if k in gen_fields}
                    )
                except TypeError:
                    continue

        om = data.get("orchestration_memory")
        if isinstance(om, dict):
            om_fields = {f.name for f in dc_fields(OrchestrationMemory)}
            try:
                ledger.orchestration_memory = OrchestrationMemory(
                    **{k: v for k, v in om.items() if k in om_fields}
                )
            except TypeError:
                pass

        pl = data.get("phrase_ledger")
        if isinstance(pl, dict):
            try:
                ledger._phrase_ledger = ExpectationLedger.from_dict(pl)
            except Exception:
                pass

        return ledger


# ─── Attaching a ledger to a graph ───────────────────────────────────────────
#
# The ExpectationLedger is described in CLAUDE.md as one of the system's core
# design principles — "the system's working memory of unfinished musical
# business", tracking promises, debts, cooldowns and locks so a piece can carry
# expectations across time.
#
# Measured on 2026-08-26: **no piece in the workspace has ever contained a
# single ledger entry.** Not one, across twelve pieces spanning five months.
#
# The cause was not a failure to record. Planning guards every write with
# ``if _cross_ledger is not None`` / ``elif _ledger is not None``, and a
# PieceGraph has ``cross_scale_ledger = None`` and no ``expectation_ledger``
# attribute at all — so both guards are False for every section and nothing is
# ever written. The bare ``except Exception: pass`` around that block (audit
# item C21) is not the problem and never fired: there was simply no ledger to
# populate. Nothing raised, nothing was recorded, and nothing reported that.
#
# ``ensure_ledger`` makes the object exist, so a caller that wants to record an
# expectation can, without needing to know how the graph was constructed.


def ensure_ledger(graph) -> "CrossScaleLedger":
    """Return a live CrossScaleLedger for this graph, creating one if absent.

    ``PieceGraph.cross_scale_ledger`` is typed as a **dict** — the serialized
    form — so the live object is kept on a transient attribute and the dict is
    written back by :func:`persist_ledger`. Attaching the object to the dict
    field directly would break the save contract, which is exactly the kind of
    "two things share one field" mistake that has already cost this project four
    separate bugs.

    A persisted ledger is restored, so promises and debts survive across runs
    and movement boundaries instead of being silently replaced by an empty one.
    """
    live = getattr(graph, "_live_cross_ledger", None)
    if isinstance(live, CrossScaleLedger):
        return live

    stored = getattr(graph, "cross_scale_ledger", None)
    if isinstance(stored, CrossScaleLedger):
        # A caller attached the object to the dict field. Take it, and put the
        # field back to the serialized form the graph expects.
        live = stored
    elif isinstance(stored, dict) and stored:
        try:
            live = CrossScaleLedger.from_dict(stored)
        except Exception:
            live = CrossScaleLedger()
    else:
        live = CrossScaleLedger()

    try:
        graph._live_cross_ledger = live
        graph.cross_scale_ledger = live.to_dict()
    except Exception:  # pragma: no cover - an immutable graph is still usable
        pass
    return live


def persist_ledger(graph, ledger: Optional["CrossScaleLedger"] = None) -> Dict[str, Any]:
    """Write the live ledger back to the graph's serialized field.

    Call before ``graph.save()``. Without this the ledger exists only in memory
    and every promise recorded during planning is gone by the time composition
    reads it — which, for a subsystem whose entire purpose is carrying
    expectations across time, is the same as not having one.
    """
    live = ledger or getattr(graph, "_live_cross_ledger", None)
    if not isinstance(live, CrossScaleLedger):
        return {}
    data = live.to_dict()
    try:
        graph.cross_scale_ledger = data
    except Exception:  # pragma: no cover - defensive
        pass
    return data


def ledger_is_empty(graph) -> bool:
    """True when the graph carries no recorded expectations at all.

    The check that would have caught this in the first place: a documented
    subsystem holding zero entries on every piece ever produced is vestigial,
    whatever the docs say about it.
    """
    return _open_expectations(graph) == []


def _open_expectations(graph) -> List[Any]:
    """Open expectations from the live ledger or the serialized field.

    Reading only the live object reported "no ledger" on a graph freshly loaded
    from disk whose expectations had in fact survived — the same
    read-one-shape-of-two mistake that makes an empty analysis look like a clean
    bill of health.
    """
    live = getattr(graph, "_live_cross_ledger", None)
    if isinstance(live, CrossScaleLedger):
        try:
            return list(live.get_all_open())
        except Exception:  # pragma: no cover - defensive
            return []
    stored = getattr(graph, "cross_scale_ledger", None)
    if isinstance(stored, CrossScaleLedger):
        try:
            return list(stored.get_all_open())
        except Exception:  # pragma: no cover - defensive
            return []
    if isinstance(stored, dict) and stored:
        try:
            return list(CrossScaleLedger.from_dict(stored).get_all_open())
        except Exception:  # pragma: no cover - defensive
            return []
    return []


def ledger_summary(graph) -> Dict[str, Any]:
    """What the ledger is holding, for a review or a status line."""
    open_exps = _open_expectations(graph)
    attached = bool(
        getattr(graph, "_live_cross_ledger", None) is not None
        or getattr(graph, "cross_scale_ledger", None)
    )
    by_scale: Dict[str, int] = {}
    for e in open_exps:
        scale = getattr(e, "scale", "?")
        by_scale[scale] = by_scale.get(scale, 0) + 1
    out: Dict[str, Any] = {
        "attached": attached,
        "open": len(open_exps),
        "by_scale": by_scale,
        "objects": [getattr(e, "object_ref", "") for e in open_exps[:12]],
    }
    if not attached:
        out["note"] = "no ledger on this graph"
    return out
