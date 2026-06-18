"""
ExpectationLedger — tracks musical promises, debts, cooldowns, and locks.

Replaces the shallow continuity tracker with a system that models
unfinished musical intentions the way a human composer tracks them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .enums import ExpectationStatus, ExpectationType


@dataclass
class Expectation:
    """A single musical expectation.

    Types:
      promise   — motif/theme must return (e.g., "motif_A must return by recap")
      debt      — harmonic/tonal obligation (e.g., "V7 must resolve to I")
      cooldown  — recently used element needs rest (e.g., "alberti just used, wait 2 phrases")
      prohibition — something must NOT happen (e.g., "no climax here, bigger one reserved later")
      identity_lock — structural element must be preserved (e.g., "source theme contour locked")
    """

    id: str = ""
    type: str = ExpectationType.PROMISE.value
    object_ref: str = ""  # what this is about (motif_id, chord, texture, etc.)
    introduced_at: str = ""  # phrase_id where created
    must_resolve_by: Optional[str] = None  # phrase_id deadline; None = open-ended
    expected_form: Optional[str] = None  # how it should resolve
    urgency: float = 0.5  # 0-1, increases as deadline approaches
    status: str = ExpectationStatus.OPEN.value
    resolved_at: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def is_open(self) -> bool:
        return self.status == ExpectationStatus.OPEN.value

    def is_overdue(self, current_phrase: str, phrase_order: List[str]) -> bool:
        """Check if this expectation is past its deadline."""
        if self.must_resolve_by is None:
            return False
        if self.status != ExpectationStatus.OPEN.value:
            return False
        try:
            deadline_idx = phrase_order.index(self.must_resolve_by)
            current_idx = phrase_order.index(current_phrase)
            return current_idx > deadline_idx
        except ValueError:
            return False


class ExpectationLedger:
    """
    Tracks all musical expectations across a composition.

    This is the system's "working memory" of unfinished musical business:
    - Motif promises that need to be fulfilled
    - Unresolved dissonances or tendency tones
    - Sequences in progress
    - Dynamic/registral climbs in progress
    - Post-climax breathing requirements
    - Minor-mode shadows that need payoff
    - Theme returns that should sound matured
    """

    def __init__(self):
        self.entries: List[Expectation] = []
        self._id_counter = 0

    def _next_id(self) -> str:
        self._id_counter += 1
        return f"exp_{self._id_counter:04d}"

    # ─── Add expectations ─────────────────────────────────────────────────

    def add_promise(
        self,
        object_ref: str,
        introduced_at: str,
        must_return_by: Optional[str] = None,
        expected_form: Optional[str] = None,
        urgency: float = 0.5,
        details: Optional[Dict] = None,
    ) -> str:
        """A motif/theme/idea must return or be developed."""
        exp = Expectation(
            id=self._next_id(),
            type=ExpectationType.PROMISE.value,
            object_ref=object_ref,
            introduced_at=introduced_at,
            must_resolve_by=must_return_by,
            expected_form=expected_form,
            urgency=urgency,
            details=details or {},
        )
        self.entries.append(exp)
        return exp.id

    def add_debt(
        self,
        object_ref: str,
        opened_at: str,
        must_resolve_by: Optional[str] = None,
        urgency: float = 0.7,
        details: Optional[Dict] = None,
    ) -> str:
        """A harmonic/tonal obligation that needs resolution."""
        exp = Expectation(
            id=self._next_id(),
            type=ExpectationType.DEBT.value,
            object_ref=object_ref,
            introduced_at=opened_at,
            must_resolve_by=must_resolve_by,
            urgency=urgency,
            details=details or {},
        )
        self.entries.append(exp)
        return exp.id

    def add_cooldown(
        self,
        object_ref: str,
        introduced_at: str,
        duration_phrases: int = 2,
        details: Optional[Dict] = None,
    ) -> str:
        """A recently used element needs a rest period."""
        exp = Expectation(
            id=self._next_id(),
            type=ExpectationType.COOLDOWN.value,
            object_ref=object_ref,
            introduced_at=introduced_at,
            urgency=0.3,
            details={"duration_phrases": duration_phrases, **(details or {})},
        )
        self.entries.append(exp)
        return exp.id

    def add_prohibition(
        self,
        object_ref: str,
        introduced_at: str,
        must_resolve_by: Optional[str] = None,
        reason: str = "",
        details: Optional[Dict] = None,
    ) -> str:
        """Something must NOT happen until a condition is met."""
        exp = Expectation(
            id=self._next_id(),
            type=ExpectationType.PROHIBITION.value,
            object_ref=object_ref,
            introduced_at=introduced_at,
            must_resolve_by=must_resolve_by,
            expected_form=reason,
            urgency=0.8,
            details=details or {},
        )
        self.entries.append(exp)
        return exp.id

    def add_lock(
        self,
        object_ref: str,
        introduced_at: str,
        preserve_aspects: Optional[List[str]] = None,
        details: Optional[Dict] = None,
    ) -> str:
        """A structural element must be preserved."""
        exp = Expectation(
            id=self._next_id(),
            type=ExpectationType.IDENTITY_LOCK.value,
            object_ref=object_ref,
            introduced_at=introduced_at,
            urgency=1.0,
            details={"preserve": preserve_aspects or [], **(details or {})},
        )
        self.entries.append(exp)
        return exp.id

    # ─── Query expectations ───────────────────────────────────────────────

    def get_open(self, type_filter: Optional[str] = None) -> List[Expectation]:
        """Get all open expectations, optionally filtered by type."""
        result = [e for e in self.entries if e.is_open()]
        if type_filter:
            result = [e for e in result if e.type == type_filter]
        return result

    def get_overdue(self, current_phrase: str, phrase_order: List[str]) -> List[Expectation]:
        """Get all expectations that are past their deadline."""
        return [e for e in self.entries if e.is_overdue(current_phrase, phrase_order)]

    def get_due_soon(
        self, current_phrase: str, phrase_order: List[str], horizon: int = 2
    ) -> List[Expectation]:
        """Get expectations due within `horizon` phrases."""
        try:
            current_idx = phrase_order.index(current_phrase)
        except ValueError:
            return []
        result = []
        for e in self.entries:
            if not e.is_open() or e.must_resolve_by is None:
                continue
            try:
                deadline_idx = phrase_order.index(e.must_resolve_by)
                if 0 <= deadline_idx - current_idx <= horizon:
                    result.append(e)
            except ValueError:
                continue
        return result

    def get_active_cooldowns(
        self, current_phrase: str, phrase_order: List[str]
    ) -> List[Expectation]:
        """Get active cooldowns at the current phrase."""
        try:
            current_idx = phrase_order.index(current_phrase)
        except ValueError:
            return []
        result = []
        for e in self.entries:
            if e.type != ExpectationType.COOLDOWN.value or not e.is_open():
                continue
            try:
                start_idx = phrase_order.index(e.introduced_at)
                duration = e.details.get("duration_phrases", 2)
                if current_idx < start_idx + duration:
                    result.append(e)
            except ValueError:
                continue
        return result

    def get_active_prohibitions(
        self, current_phrase: str, phrase_order: List[str]
    ) -> List[Expectation]:
        """Get active prohibitions at the current phrase."""
        try:
            current_idx = phrase_order.index(current_phrase)
        except ValueError:
            return []
        result = []
        for e in self.entries:
            if e.type != ExpectationType.PROHIBITION.value or not e.is_open():
                continue
            if e.must_resolve_by is None:
                result.append(e)
                continue
            try:
                end_idx = phrase_order.index(e.must_resolve_by)
                if current_idx <= end_idx:
                    result.append(e)
            except ValueError:
                result.append(e)
        return result

    def get_locks(self) -> List[Expectation]:
        """Get all active identity locks."""
        return [
            e for e in self.entries if e.type == ExpectationType.IDENTITY_LOCK.value and e.is_open()
        ]

    # ─── Resolve expectations ─────────────────────────────────────────────

    def satisfy(self, exp_id: str, resolved_at: str) -> bool:
        """Mark an expectation as satisfied."""
        for e in self.entries:
            if e.id == exp_id:
                e.status = ExpectationStatus.SATISFIED.value
                e.resolved_at = resolved_at
                return True
        return False

    def violate(self, exp_id: str, resolved_at: str) -> bool:
        """Mark an expectation as violated."""
        for e in self.entries:
            if e.id == exp_id:
                e.status = ExpectationStatus.VIOLATED.value
                e.resolved_at = resolved_at
                return True
        return False

    def expire_cooldowns(self, current_phrase: str, phrase_order: List[str]) -> int:
        """Expire cooldowns that have passed their duration. Returns count."""
        try:
            current_idx = phrase_order.index(current_phrase)
        except ValueError:
            return 0
        count = 0
        for e in self.entries:
            if e.type != ExpectationType.COOLDOWN.value or not e.is_open():
                continue
            try:
                start_idx = phrase_order.index(e.introduced_at)
                duration = e.details.get("duration_phrases", 2)
                if current_idx >= start_idx + duration:
                    e.status = ExpectationStatus.EXPIRED.value
                    e.resolved_at = current_phrase
                    count += 1
            except ValueError:
                continue
        return count

    # ─── Scoring ──────────────────────────────────────────────────────────

    def score_phrase_resolution(self, phrase_id: str, phrase_order: List[str]) -> float:
        """Score how well expectations are being managed at this phrase.

        Returns 0.0-1.0:
          1.0 = all expectations on track
          0.0 = critical violations
        """
        if not self.entries:
            return 1.0

        overdue = self.get_overdue(phrase_id, phrase_order)
        due_soon = self.get_due_soon(phrase_id, phrase_order)
        open_count = len(self.get_open())

        if open_count == 0:
            return 1.0

        # Penalties
        overdue_penalty = len(overdue) * 0.2
        urgency_pressure = sum(e.urgency for e in due_soon) * 0.1

        score = 1.0 - min(overdue_penalty + urgency_pressure, 1.0)
        return max(score, 0.0)

    # ─── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": [
                {
                    "id": e.id,
                    "type": e.type,
                    "object_ref": e.object_ref,
                    "introduced_at": e.introduced_at,
                    "must_resolve_by": e.must_resolve_by,
                    "expected_form": e.expected_form,
                    "urgency": e.urgency,
                    "status": e.status,
                    "resolved_at": e.resolved_at,
                    "details": e.details,
                }
                for e in self.entries
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExpectationLedger":
        ledger = cls()
        for entry_data in data.get("entries", []):
            exp = Expectation(
                id=entry_data.get("id", ""),
                type=entry_data.get("type", ExpectationType.PROMISE.value),
                object_ref=entry_data.get("object_ref", ""),
                introduced_at=entry_data.get("introduced_at", ""),
                must_resolve_by=entry_data.get("must_resolve_by"),
                expected_form=entry_data.get("expected_form"),
                urgency=entry_data.get("urgency", 0.5),
                status=entry_data.get("status", ExpectationStatus.OPEN.value),
                resolved_at=entry_data.get("resolved_at"),
                details=entry_data.get("details", {}),
            )
            ledger.entries.append(exp)
            # Keep ID counter in sync
            try:
                num = int(exp.id.split("_")[1])
                if num >= ledger._id_counter:
                    ledger._id_counter = num
            except (IndexError, ValueError):
                pass
        return ledger
