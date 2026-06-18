"""
Conflict Resolver — detect contradictions between evidence and doctrine.

Generates conflict reports for human review. Does NOT auto-edit canonical
doctrine (Layer 1). Can auto-adjust grounding levels and overlay weights
within conservative thresholds.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .claim_registry import ClaimRegistry, MeasurableClaim

# ─── Conflict Model ────────────────────────────────────────────────────────


@dataclass
class Conflict:
    """A detected contradiction between evidence and doctrine."""

    claim_id: str = ""
    conflict_type: str = ""  # statistical_contradiction | fingerprint_contradiction
    # | rule_contradiction | anti_pattern_false_positive
    expected: Dict[str, Any] = field(default_factory=dict)
    observed: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0  # how confident we are in the contradiction
    severity: str = ""  # low | medium | high
    recommendation: str = ""  # downgrade_grounding | narrow_scope | add_period_exception
    # | reduce_weight | mark_contradicted
    possible_resolutions: List[str] = field(default_factory=list)
    sources_tested: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConflictReport:
    """Report of all detected conflicts for a composer."""

    composer: str = ""
    generated_date: str = ""
    total_claims: int = 0
    total_conflicts: int = 0
    conflicts: List[Conflict] = field(default_factory=list)

    # Summary by severity
    high_severity: int = 0
    medium_severity: int = 0
    low_severity: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composer": self.composer,
            "generated_date": self.generated_date,
            "total_claims": self.total_claims,
            "total_conflicts": self.total_conflicts,
            "high_severity": self.high_severity,
            "medium_severity": self.medium_severity,
            "low_severity": self.low_severity,
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


# ─── Graduated Response Thresholds ──────────────────────────────────────────

# | Contradiction Confidence | Action                                      |
# |--------------------------|---------------------------------------------|
# | < 0.5                    | No action                                   |
# | 0.5 - 0.7               | Log to report only                          |
# | 0.7 - 0.8               | Downgrade grounding one level               |
# | 0.8 - 0.95              | Downgrade + reduce frequency_weight by 25%  |
# | > 0.95                   | Downgrade + mark contradicted + reduce 50%  |

REPORT_THRESHOLD = 0.5
DOWNGRADE_THRESHOLD = 0.7
WEIGHT_REDUCE_THRESHOLD = 0.8
CONTRADICT_MARK_THRESHOLD = 0.95

GROUNDING_LEVELS = [
    "hard_corroborated",
    "soft_corroborated",
    "unverified",
    "contradicted",
]


# ─── Resolver ───────────────────────────────────────────────────────────────


def resolve_conflicts(registry: ClaimRegistry) -> ConflictReport:
    """Analyze a claim registry for contradictions and generate a report.

    Also applies safe automatic adjustments (grounding downgrades)
    to claims that exceed the graduated thresholds.
    """
    report = ConflictReport(
        composer=registry.composer,
        generated_date=date.today().isoformat(),
        total_claims=len(registry),
    )

    for claim in registry.get_all():
        conflict = _check_claim_for_conflict(claim)
        if conflict is not None:
            report.conflicts.append(conflict)
            report.total_conflicts += 1

            if conflict.severity == "high":
                report.high_severity += 1
            elif conflict.severity == "medium":
                report.medium_severity += 1
            else:
                report.low_severity += 1

            # Apply safe automatic adjustments
            _apply_auto_adjustment(claim, conflict)

    return report


def _check_claim_for_conflict(claim: MeasurableClaim) -> Optional[Conflict]:
    """Check a single claim for contradiction evidence."""
    if claim.total_tested < 3:
        return None  # Not enough data

    # Calculate contradiction confidence
    total_decisive = claim.support_count + claim.contradiction_count
    if total_decisive == 0:
        return None

    contradiction_ratio = claim.contradiction_count / total_decisive

    if contradiction_ratio < REPORT_THRESHOLD:
        return None  # No significant contradiction

    # Determine conflict type based on claim category
    conflict_type = _infer_conflict_type(claim)

    # Determine severity
    if contradiction_ratio >= CONTRADICT_MARK_THRESHOLD:
        severity = "high"
    elif contradiction_ratio >= DOWNGRADE_THRESHOLD:
        severity = "medium"
    else:
        severity = "low"

    # Generate recommendations
    recommendation, resolutions = _generate_recommendations(claim, contradiction_ratio)

    return Conflict(
        claim_id=claim.claim_id,
        conflict_type=conflict_type,
        expected={
            "claim_description": claim.description,
            "test_type": claim.test_type,
            "test_config": claim.test_config,
            "current_grounding": claim.current_grounding,
        },
        observed={
            "support_count": claim.support_count,
            "contradiction_count": claim.contradiction_count,
            "total_tested": claim.total_tested,
            "contradiction_ratio": round(contradiction_ratio, 3),
        },
        confidence=round(contradiction_ratio, 3),
        severity=severity,
        recommendation=recommendation,
        possible_resolutions=resolutions,
        sources_tested=claim.total_tested,
    )


def _infer_conflict_type(claim: MeasurableClaim) -> str:
    """Infer the type of conflict from the claim category."""
    category_to_type = {
        "distribution": "statistical_contradiction",
        "fingerprint": "fingerprint_contradiction",
        "figuration": "statistical_contradiction",
        "melody_prior": "rule_contradiction",
        "harmonic_device": "rule_contradiction",
        "anti_pattern": "anti_pattern_false_positive",
        "cadence": "rule_contradiction",
        "prompt_semantic": "rule_contradiction",
    }
    return category_to_type.get(claim.category, "statistical_contradiction")


def _generate_recommendations(
    claim: MeasurableClaim, contradiction_ratio: float
) -> tuple[str, List[str]]:
    """Generate recommendation and possible resolutions."""
    resolutions = []

    if claim.category == "distribution":
        resolutions = [
            "update_expected_proportion",
            "narrow_scope_to_period",
            "add_genre_exception",
        ]
    elif claim.category == "fingerprint":
        resolutions = [
            "narrow_claim_to_presentation_phrases",
            "add_minor_mode_exception",
            "create_late_style_overlay",
            "mark_as_soft_preference",
        ]
    elif claim.category == "anti_pattern":
        resolutions = [
            "increase_detector_threshold",
            "add_style_scope_exception",
            "mark_as_style_specific",
        ]
    else:
        resolutions = [
            "downgrade_grounding",
            "narrow_scope",
            "add_period_exception",
        ]

    # Primary recommendation based on confidence
    if contradiction_ratio >= CONTRADICT_MARK_THRESHOLD:
        recommendation = "mark_contradicted"
    elif contradiction_ratio >= WEIGHT_REDUCE_THRESHOLD:
        recommendation = "reduce_weight"
    elif contradiction_ratio >= DOWNGRADE_THRESHOLD:
        recommendation = "downgrade_grounding"
    else:
        recommendation = "log_only"

    return recommendation, resolutions


def _apply_auto_adjustment(claim: MeasurableClaim, conflict: Conflict) -> None:
    """Apply safe automatic adjustments to a claim based on conflict severity.

    Only adjusts grounding level and adds flags. Never modifies Layer 1 doctrine.
    """
    contradiction_ratio = conflict.confidence

    if contradiction_ratio < DOWNGRADE_THRESHOLD:
        return  # Log only, no adjustment

    # Downgrade grounding by one level
    current_idx = -1
    for i, level in enumerate(GROUNDING_LEVELS):
        if claim.current_grounding == level:
            current_idx = i
            break

    if current_idx >= 0 and current_idx < len(GROUNDING_LEVELS) - 1:
        if contradiction_ratio >= DOWNGRADE_THRESHOLD:
            claim.current_grounding = GROUNDING_LEVELS[
                min(current_idx + 1, len(GROUNDING_LEVELS) - 1)
            ]

    # Mark as contradicted at highest severity
    if contradiction_ratio >= CONTRADICT_MARK_THRESHOLD:
        claim.current_grounding = "contradicted"


# ─── Persistence ────────────────────────────────────────────────────────────


def save_conflict_report(report: ConflictReport, output_dir: Path) -> Path:
    """Save conflict report to conflict_reports.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "conflict_reports.json"
    with open(out_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    return out_path


def load_conflict_report(path: Path) -> ConflictReport:
    """Load a conflict report from JSON."""
    with open(path) as f:
        data = json.load(f)

    report = ConflictReport(
        composer=data.get("composer", ""),
        generated_date=data.get("generated_date", ""),
        total_claims=data.get("total_claims", 0),
        total_conflicts=data.get("total_conflicts", 0),
        high_severity=data.get("high_severity", 0),
        medium_severity=data.get("medium_severity", 0),
        low_severity=data.get("low_severity", 0),
    )
    for cd in data.get("conflicts", []):
        conflict = Conflict(
            claim_id=cd.get("claim_id", ""),
            conflict_type=cd.get("conflict_type", ""),
            expected=cd.get("expected", {}),
            observed=cd.get("observed", {}),
            confidence=cd.get("confidence", 0.0),
            severity=cd.get("severity", ""),
            recommendation=cd.get("recommendation", ""),
            possible_resolutions=cd.get("possible_resolutions", []),
            sources_tested=cd.get("sources_tested", 0),
        )
        report.conflicts.append(conflict)

    return report
