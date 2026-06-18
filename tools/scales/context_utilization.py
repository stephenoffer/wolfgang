"""
ContextUtilization — aggregation and scoring of context traces.

Computes the Context Utilization Score for a section or piece,
proving that context was actually used and anti-patterns are absent.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .models import ContextTrace, ContextUtilizationReport, FingerprintContract

# Fallback budget per tier — max fraction of bars using hardcoded fallback
FALLBACK_BUDGETS = {
    "A": 0.10,
    "B": 0.20,
    "C": 0.35,
    "D": 1.00,
}


def compute_utilization(
    traces: Dict[str, ContextTrace],
    fingerprint_contract: Optional[FingerprintContract] = None,
    anti_pattern_results: Optional[List[Dict]] = None,
    tier: str = "D",
) -> ContextUtilizationReport:
    """Compute Context Utilization Score for a section or piece.

    Aggregates all phrase-level context traces into a single report
    with coverage metrics and anti-pattern results.
    """
    report = ContextUtilizationReport()

    for phrase_id, trace in traces.items():
        report.total_bars += trace.total_bar_count
        report.bars_from_corpus_patterns += len(trace.corpus_patterns_used)
        report.bars_from_corpus_bars += len(trace.corpus_bars_used)
        report.bars_from_hardcoded_fallback += trace.fallback_bar_count
        report.bars_from_donor += trace.donor_bar_count
        report.gestures_applied += len(trace.gestures_applied)
        report.breathing_rules_applied += len(trace.breathing_rules_applied)
        report.ornament_intents_applied += len(trace.ornament_intents_applied)
        report.phrase_traces[phrase_id] = trace

    # Fingerprint coverage
    if fingerprint_contract:
        all_expressed: set = set()
        for trace in traces.values():
            all_expressed.update(trace.fingerprints_expressed)
        required = set(fingerprint_contract.required_fingerprints)
        report.fingerprints_satisfied = len(all_expressed & required)
        report.fingerprints_required = fingerprint_contract.minimum_audible_count
    else:
        report.fingerprints_required = 0

    # Anti-pattern results
    if anti_pattern_results:
        report.anti_patterns_detected = sum(
            1 for r in anti_pattern_results if r.get("detected", False)
        )
        report.anti_patterns_checked = len(anti_pattern_results)

    return report


def compute_section_coverage(
    section_id: str,
    traces: Dict[str, ContextTrace],
    fingerprint_contract: Optional[FingerprintContract] = None,
    anti_results: Optional[List[Dict]] = None,
    tier: str = "D",
) -> Dict:
    """Compute a section-level coverage report.

    Wraps ``compute_utilization()`` and returns a flat dict suitable
    for logging or aggregation across sections.
    """
    report = compute_utilization(traces, fingerprint_contract, anti_results, tier)

    budget = FALLBACK_BUDGETS.get(tier, 1.0)
    within_budget = report.fallback_ratio <= budget

    fp_coverage = (
        report.fingerprints_satisfied / max(report.fingerprints_required, 1)
        if report.fingerprints_required > 0
        else 1.0
    )

    return {
        "section_id": section_id,
        "corpus_coverage": report.corpus_coverage,
        "fallback_ratio": report.fallback_ratio,
        "fingerprint_coverage": fp_coverage,
        "within_budget": within_budget,
        "phrase_count": len(traces),
        "gestures_applied": report.gestures_applied,
        "anti_patterns_detected": report.anti_patterns_detected,
    }


def is_within_fallback_budget(report: ContextUtilizationReport, tier: str) -> bool:
    """Check if the fallback ratio is within budget for the tier."""
    budget = FALLBACK_BUDGETS.get(tier, 1.0)
    return report.fallback_ratio <= budget


def format_utilization_summary(report: ContextUtilizationReport, tier: str = "D") -> str:
    """Format a human-readable utilization summary."""
    budget = FALLBACK_BUDGETS.get(tier, 1.0)
    within = "PASS" if report.fallback_ratio <= budget else "OVER BUDGET"

    lines = [
        "Context Utilization Report",
        f"  Total bars: {report.total_bars}",
        f"  Corpus coverage: {report.corpus_coverage:.0%}",
        f"  Fallback ratio: {report.fallback_ratio:.0%} (budget: {budget:.0%}) [{within}]",
        f"  Fingerprint coverage: {report.fingerprints_satisfied}/{report.fingerprints_required}",
        f"  Gestures applied: {report.gestures_applied}",
        f"  Breathing rules applied: {report.breathing_rules_applied}",
        f"  Anti-patterns: {report.anti_patterns_detected}/{report.anti_patterns_checked} detected",
    ]
    return "\n".join(lines)
