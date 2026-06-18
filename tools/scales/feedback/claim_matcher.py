"""
Claim Matcher — match evidence bundles against claims, update support/contradiction.

Runs each claim's test against an EvidenceBundle and records whether
the new evidence supports, contradicts, or is neutral to the claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .claim_registry import ClaimRegistry, MeasurableClaim
from .evidence_extractor import EvidenceBundle

# ─── Match Result ───────────────────────────────────────────────────────────


@dataclass
class ClaimMatchResult:
    """Result of matching one claim against one evidence bundle."""

    claim_id: str = ""
    verdict: str = ""  # "support" | "contradict" | "neutral" | "untestable"
    delta: float = 0.0  # strength of support/contradiction (0.0 - 1.0)
    detail: str = ""  # human-readable explanation
    observed_value: Any = None
    expected_value: Any = None


@dataclass
class MatchReport:
    """Report of matching all claims against one evidence bundle."""

    composer: str = ""
    source_file: str = ""
    total_claims: int = 0
    tested: int = 0
    supported: int = 0
    contradicted: int = 0
    neutral: int = 0
    untestable: int = 0
    results: List[ClaimMatchResult] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        return {
            "composer": self.composer,
            "source_file": self.source_file,
            "total_claims": self.total_claims,
            "tested": self.tested,
            "supported": self.supported,
            "contradicted": self.contradicted,
            "neutral": self.neutral,
            "untestable": self.untestable,
        }


# ─── Matching Engine ────────────────────────────────────────────────────────

# Configurable thresholds
DISTRIBUTION_SUPPORT_THRESHOLD = 0.3  # KL-like divergence below this = support
DISTRIBUTION_CONTRADICT_THRESHOLD = 0.7  # above this = contradiction
THRESHOLD_SUPPORT_STDEVS = 1.0  # within N stdevs = support
THRESHOLD_CONTRADICT_STDEVS = 2.0  # beyond N stdevs = contradiction


def match_evidence(bundle: EvidenceBundle, registry: ClaimRegistry) -> MatchReport:
    """Match an evidence bundle against all claims in the registry.

    Updates claim support/contradiction counts in place.
    Returns a MatchReport with per-claim results.
    """
    report = MatchReport(
        composer=registry.composer,
        source_file=bundle.source_file,
        total_claims=len(registry),
    )

    for claim in registry.get_all():
        result = _match_single_claim(bundle, claim)
        report.results.append(result)

        # Update claim counts
        if result.verdict == "support":
            claim.record_support()
            report.supported += 1
            report.tested += 1
        elif result.verdict == "contradict":
            claim.record_contradiction()
            report.contradicted += 1
            report.tested += 1
        elif result.verdict == "neutral":
            claim.record_neutral()
            report.neutral += 1
            report.tested += 1
        else:
            report.untestable += 1

    return report


def _match_single_claim(bundle: EvidenceBundle, claim: MeasurableClaim) -> ClaimMatchResult:
    """Match a single claim against a single evidence bundle."""
    test_type = claim.test_type

    if test_type == "distribution":
        return _test_distribution(bundle, claim)
    elif test_type == "threshold":
        return _test_threshold(bundle, claim)
    elif test_type == "presence":
        return _test_presence(bundle, claim)
    else:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"Unknown test type: {test_type}",
        )


def _test_distribution(bundle: EvidenceBundle, claim: MeasurableClaim) -> ClaimMatchResult:
    """Test a distribution claim (e.g., LH texture proportions)."""
    config = claim.test_config
    field_name = config.get("field", "")
    key = config.get("key", "")
    expected = config.get("expected_proportion")
    tolerance = config.get("tolerance", 0.15)
    presence_only = config.get("presence_only", False)

    # Handle transition matrix claims
    if field_name == "transition_counts":
        return _test_transition_distribution(bundle, claim)

    # Get the distribution from the bundle
    dist = getattr(bundle, field_name, None)
    if not isinstance(dist, dict):
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"Field '{field_name}' not available in bundle",
        )

    observed = dist.get(key, 0.0)

    # Presence-only test: just check if texture appears at all
    if presence_only:
        if observed > 0:
            return ClaimMatchResult(
                claim_id=claim.claim_id,
                verdict="support",
                delta=1.0,
                detail=f"'{key}' present at {observed:.1%}",
                observed_value=observed,
            )
        else:
            return ClaimMatchResult(
                claim_id=claim.claim_id,
                verdict="neutral",
                delta=0.0,
                detail=f"'{key}' not found in this score (may be style-specific)",
                observed_value=0.0,
            )

    if expected is None:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail="No expected proportion configured",
        )

    # Compute divergence
    divergence = abs(observed - expected)

    if divergence <= tolerance:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="support",
            delta=round(1.0 - divergence / max(tolerance, 0.01), 3),
            detail=f"'{key}': observed {observed:.3f} vs expected {expected:.3f} "
            f"(within tolerance {tolerance})",
            observed_value=observed,
            expected_value=expected,
        )
    elif divergence >= tolerance * 2:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="contradict",
            delta=round(min(divergence / max(expected, 0.01), 1.0), 3),
            detail=f"'{key}': observed {observed:.3f} vs expected {expected:.3f} "
            f"(exceeds 2x tolerance)",
            observed_value=observed,
            expected_value=expected,
        )
    else:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="neutral",
            delta=round(divergence / max(tolerance, 0.01), 3),
            detail=f"'{key}': observed {observed:.3f} vs expected {expected:.3f} "
            f"(between tolerance thresholds)",
            observed_value=observed,
            expected_value=expected,
        )


def _test_transition_distribution(
    bundle: EvidenceBundle, claim: MeasurableClaim
) -> ClaimMatchResult:
    """Test a transition matrix claim."""
    config = claim.test_config
    src = config.get("src", "")
    tgt = config.get("tgt", "")
    expected = config.get("expected_proportion", 0.0)
    tolerance = config.get("tolerance", 0.15)

    trans = bundle.transition_counts
    if not trans or src not in trans:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"No transitions from '{src}' in bundle",
        )

    src_targets = trans[src]
    total = sum(src_targets.values())
    if total == 0:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"Zero transitions from '{src}'",
        )

    observed = src_targets.get(tgt, 0) / total
    divergence = abs(observed - expected)

    if divergence <= tolerance:
        verdict = "support"
    elif divergence >= tolerance * 2:
        verdict = "contradict"
    else:
        verdict = "neutral"

    return ClaimMatchResult(
        claim_id=claim.claim_id,
        verdict=verdict,
        delta=round(divergence / max(expected, 0.01), 3),
        detail=f"Transition {src}→{tgt}: observed {observed:.3f} vs expected {expected:.3f}",
        observed_value=observed,
        expected_value=expected,
    )


def _test_threshold(bundle: EvidenceBundle, claim: MeasurableClaim) -> ClaimMatchResult:
    """Test a threshold claim (metric above/below/within range)."""
    config = claim.test_config
    metric = config.get("metric")
    direction = config.get("direction", "gte")
    threshold = config.get("threshold")
    is_anti = config.get("is_anti_pattern", False)

    if not metric:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail="No metric configured for threshold test",
        )

    observed = getattr(bundle, metric, None)
    if observed is None:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"Metric '{metric}' not available in bundle",
        )

    # Range test
    if direction == "range":
        min_val = config.get("min", 0.0)
        max_val = config.get("max", float("inf"))
        in_range = min_val <= observed <= max_val

        if is_anti:
            # Anti-pattern: being IN range means the anti-pattern is present
            # → contradiction (corpus shouldn't have anti-patterns)
            verdict = "contradict" if in_range else "support"
        else:
            verdict = "support" if in_range else "contradict"

        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict=verdict,
            delta=round(abs(observed - (min_val + max_val) / 2) / max(max_val - min_val, 0.01), 3),
            detail=f"{metric}={observed:.2f}, expected range [{min_val}, {max_val}]",
            observed_value=observed,
            expected_value=f"[{min_val}, {max_val}]",
        )

    if threshold is None:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail="No threshold configured",
        )

    # Directional test
    if direction == "gte":
        passes = observed >= threshold
    elif direction == "lte":
        passes = observed <= threshold
    elif direction == "eq":
        passes = abs(observed - threshold) < threshold * 0.1
    else:
        passes = observed >= threshold

    if is_anti:
        # Anti-pattern: passing the test means anti-pattern IS present
        # In real corpus, anti-patterns should be ABSENT → passing = contradict
        # But actually: for anti-pattern claims, the claim is "this pattern
        # is bad." If corpus shows it, the claim is supported (it IS bad).
        # If corpus doesn't show it, neutral (correct behavior).
        if passes:
            verdict = "support"  # Anti-pattern detected in corpus — confirms it exists
        else:
            verdict = "neutral"
    else:
        verdict = "support" if passes else "contradict"

    margin = abs(observed - threshold)
    return ClaimMatchResult(
        claim_id=claim.claim_id,
        verdict=verdict,
        delta=round(min(margin / max(abs(threshold), 0.01), 1.0), 3),
        detail=f"{metric}={observed:.2f} {'meets' if passes else 'fails'} "
        f"threshold {direction} {threshold}",
        observed_value=observed,
        expected_value=threshold,
    )


def _test_presence(bundle: EvidenceBundle, claim: MeasurableClaim) -> ClaimMatchResult:
    """Test a presence claim (qualitative — always neutral unless mapped)."""
    config = claim.test_config
    metric = config.get("metric")

    # If no metric, this is a qualitative claim — always neutral
    if not metric:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="neutral",
            detail="Qualitative claim — no automatic metric test available",
        )

    observed = getattr(bundle, metric, None)
    if observed is None:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="untestable",
            detail=f"Metric '{metric}' not available in bundle",
        )

    # Presence means the metric exists and is non-zero
    if isinstance(observed, (int, float)) and observed > 0:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="support",
            delta=1.0,
            detail=f"'{metric}' present with value {observed}",
            observed_value=observed,
        )
    else:
        return ClaimMatchResult(
            claim_id=claim.claim_id,
            verdict="neutral",
            delta=0.0,
            detail=f"'{metric}' absent or zero",
            observed_value=observed,
        )


# ─── Batch Matching ─────────────────────────────────────────────────────────


def match_batch(bundles: List[EvidenceBundle], registry: ClaimRegistry) -> List[MatchReport]:
    """Match multiple evidence bundles against a claim registry.

    Accumulates evidence across all bundles. Returns per-bundle reports.
    """
    reports = []
    for bundle in bundles:
        report = match_evidence(bundle, registry)
        reports.append(report)
    return reports
