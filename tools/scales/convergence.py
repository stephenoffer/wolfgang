"""Convergence mechanics for the actor-critic composition loop.

Prior loops OSCILLATED (fixing a clash buried the melody; de-monotonizing broke
texture) and a bug committed the LAST attempt instead of the BEST. These pure
helpers make the loop converge:
- a LEXICOGRAPHIC composite score where audible errors dominate everything, so a
  candidate can never "win" by trading one defect for another or by gaming a
  corpus metric;
- `dominates` / keep-best so the canonical phrase is replaced only by a strict
  improvement (quality is monotonic — it cannot oscillate);
- `pareto_improves` so a targeted revision is accepted only if NO detector gets
  worse (the anti-whack-a-mole rule);
- `converged` — a multi-criteria stop.

Pure functions (dicts in, scalars/bools out) so the workflow and tests share them.
"""

from __future__ import annotations

from typing import Any


def corpus_distance(divergence: dict[str, Any]) -> float:
    """Σ max(0, |z|-2) over the composer-divergence metrics. In-band metrics
    contribute 0, so gaming a metric to its mean earns nothing; only being
    OUTSIDE the corpus's real spread is penalized."""
    metrics = (divergence or {}).get("metrics", {}) or {}
    total = 0.0
    for stat in metrics.values():
        z = abs(float(stat.get("z", 0.0)))
        if z > 2.0:
            total += z - 2.0
    return round(total, 3)


# Detectors whose warnings describe an idiom, not a defect. Counting them in the
# ranking made the loop prefer whichever candidate had the least chromaticism and
# the fewest simultaneities — it actively selected for BLANDER music, because a
# cross-relation warning that the detector itself calls "often idiomatic" cost a
# candidate exactly as much as a real problem.
_ADVISORY_DETECTORS = frozenset({"vertical_clash", "melody_buried", "unresolved_nct"})


def actionable_warn_count(cand: dict[str, Any]) -> int:
    """Warnings that describe a defect rather than an idiom.

    Falls back to the raw ``warn_count`` when no per-detector breakdown is
    available, so older candidate records still rank.
    """
    counts = cand.get("detector_counts")
    if not isinstance(counts, dict):
        return int(cand.get("warn_count", 0))
    return sum(n for det, n in counts.items() if det not in _ADVISORY_DETECTORS)


def composite_score(cand: dict[str, Any]) -> tuple:
    """Lexicographic tuple (higher is better), compared field-by-field:
      (-errors, -actionable_warns, critic_quality, -critic_rank)
    Audible errors dominate; after that the fresh-ears CRITIC is the judge.

    Only ACTIONABLE warnings enter the ordering (see _ADVISORY_DETECTORS): the
    ear's idiom-level observations are for the critic to read, not a score to
    minimize. corpus_distance (z-scores) is deliberately NOT in the ordering —
    chasing a revision back into the corpus's band is the "metric whack-a-mole"
    the agent-creative direction rejects. z-scores remain a reported diagnostic
    (``corpus_distance`` helper), never a selection driver."""
    return (
        -int(cand.get("error_count", 0)),
        -actionable_warn_count(cand),
        float(cand.get("critic_quality", 0.0)),
        -int(cand.get("critic_rank", 0)),
    )


def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """True if candidate `a` is STRICTLY better than `b` AND never has more
    errors (belt-and-suspenders over the lexicographic order)."""
    if int(a.get("error_count", 0)) > int(b.get("error_count", 0)):
        return False
    return composite_score(a) > composite_score(b)


def pareto_improves(after: dict[str, int], before: dict[str, int]) -> bool:
    """Is a targeted revision an improvement, without trading one defect for another?

    A revision is accepted when at least one detector improves and no ACTIONABLE
    detector gets worse. Requiring that literally nothing move upward was too
    strict to be usable: any real musical revision jostles the advisory,
    idiom-level detectors (a new appoggiatura adds a clash warning, a widened
    climax adds a buried-melody note), so genuine improvements were rejected and
    the loop stalled on its first attempt. `after`/`before` map detector name ->
    finding count."""
    keys = set(after) | set(before)
    improved = False
    for k in keys:
        a, b = after.get(k, 0), before.get(k, 0)
        if a > b and k not in _ADVISORY_DETECTORS:
            return False  # a real defect got worse
        if a < b:
            improved = True
    return improved


def converged(
    *,
    error_count: int,
    critic_quality: float,
    section_gate_passed: bool,
    critic_approved: bool = True,
    quality_threshold: float = 4.0,
    corpus_divergence: dict[str, Any] = None,
) -> bool:
    """A section is done when the fresh-ears critic approves at/above the quality
    bar, the section gate (physical + grounding only) passes, and there are no
    hard errors.

    corpus_divergence is accepted but ADVISORY — falsification against real scores
    showed an out-of-band z-score does not mean bad music (real Chopin/Beethoven
    sit outside a MIDI-derived corpus's narrow bands), so it must not block
    convergence. The critic weighs it; it is not a gate.
    """
    _ = corpus_divergence  # advisory only — never blocks
    if error_count > 0 or not section_gate_passed or not critic_approved:
        return False
    return critic_quality >= quality_threshold


def detector_counts(findings) -> dict[str, int]:
    """Per-detector finding counts from an ear_report's findings list."""
    out: dict[str, int] = {}
    for f in findings or []:
        out[f.get("detector", "?")] = out.get(f.get("detector", "?"), 0) + 1
    return out
