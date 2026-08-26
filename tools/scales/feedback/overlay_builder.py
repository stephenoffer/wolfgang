"""
Overlay Builder — promote recurring evidence into overlay delta JSONs.

Reads a ClaimRegistry with accumulated evidence and writes structured
overlay files to tools/context_overlays/{composer}/. These overlays are
automatically loaded by style_resolver.py during StyleProgram resolution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from .claim_registry import ClaimRegistry, MeasurableClaim
from .evidence_extractor import EvidenceBundle

# ─── Promotion Thresholds ───────────────────────────────────────────────────

MIN_TESTED = 5  # Minimum total_tested before any promotion
SUPPORT_CONFIDENCE = 0.7  # Confidence threshold to strengthen an entry
CONTRADICT_CONFIDENCE = 0.8  # Confidence threshold to weaken (asymmetric)
MAX_DIVERGENCE = 0.30  # Max shift from compiled value per update cycle


# ─── Overlay Entry ──────────────────────────────────────────────────────────


@dataclass
class OverlayEntry:
    """A single entry in an overlay delta file."""

    source_claim_id: str = ""
    action: str = ""  # "strengthen" | "weaken" | "add" | "adjust"
    evidence_source: str = "corpus_feedback"
    support_count: int = 0
    contradiction_count: int = 0
    confidence: float = 0.0
    last_updated: str = ""
    evidence_sample_ids: List[str] = None
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.evidence_sample_ids is None:
            self.evidence_sample_ids = []
        if self.data is None:
            self.data = {}


# ─── Builder ────────────────────────────────────────────────────────────────


class OverlayBuilder:
    """Build overlay delta JSONs from a ClaimRegistry with accumulated evidence."""

    def __init__(
        self,
        registry: ClaimRegistry,
        compiled_pack_dir: Path,
        bundles: Optional[List[EvidenceBundle]] = None,
    ):
        self.registry = registry
        self.compiled_pack_dir = compiled_pack_dir
        self.bundles = bundles or []
        self.today = date.today().isoformat()

    def build_all(self, output_dir: Path) -> Dict[str, Path]:
        """Build all overlay files. Returns dict of category → output path."""
        output_dir.mkdir(parents=True, exist_ok=True)
        results = {}

        # Statistics overlays (highest impact)
        path = self._build_statistics_overlay(output_dir)
        if path:
            results["scoped_statistics"] = path

        # Figuration overlays
        path = self._build_figuration_overlay(output_dir)
        if path:
            results["figuration_templates"] = path

        # Fingerprint overlays
        path = self._build_fingerprint_overlay(output_dir)
        if path:
            results["fingerprint_rules"] = path

        # Harmonic device overlays
        path = self._build_harmonic_overlay(output_dir)
        if path:
            results["harmonic_devices"] = path

        # Melody prior overlays
        path = self._build_melody_overlay(output_dir)
        if path:
            results["melody_priors"] = path

        # Review rubric overlays
        path = self._build_review_overlay(output_dir)
        if path:
            results["review_rubric"] = path

        return results

    # ── Statistics Overlay ──────────────────────────────────────────────

    def _build_statistics_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build scoped_statistics.json overlay from distribution claims."""
        claims = self.registry.get_by_category("distribution")
        promotable = [c for c in claims if self._is_promotable(c)]

        if not promotable:
            return None

        # Load existing compiled statistics for divergence capping
        compiled_stats = self._load_compiled("scoped_statistics.json") or {}
        compiled_lh = compiled_stats.get("lh_distribution", {})

        # Build FULL merged LH distribution (must include all keys since
        # style_resolver's dict.update() replaces the entire sub-dict)
        lh_merged = dict(compiled_lh)  # start from compiled baseline
        lh_changed = False
        transition_updates = {}

        for claim in promotable:
            config = claim.test_config
            field = config.get("field", "")

            if field == "lh_texture_distribution":
                key = config.get("key", "")
                expected = config.get("expected_proportion", 0.0)
                if not key or expected is None:
                    continue

                # Compute evidence-weighted update
                observed_avg = self._compute_observed_average(claim, "lh_texture_distribution", key)
                if observed_avg is None:
                    continue

                # Cap divergence from compiled value
                compiled_val = compiled_lh.get(key, expected)
                capped = self._cap_divergence(compiled_val, observed_avg)

                if abs(capped - compiled_val) > 0.005:  # only if meaningful change
                    lh_merged[key] = round(capped, 4)
                    lh_changed = True

            elif field == "transition_counts":
                # Transition matrix updates — collect raw counts
                src = config.get("src", "")
                tgt = config.get("tgt", "")
                if src and tgt:
                    if src not in transition_updates:
                        transition_updates[src] = {}
                    # Use evidence to adjust proportions
                    observed_avg = self._compute_transition_average(claim, src, tgt)
                    if observed_avg is not None:
                        transition_updates[src][tgt] = round(observed_avg, 4)

        # An overlay OVERRIDES the compiled statistics wholesale, so a texture
        # label that no longer exists survives in it forever. The shipped Mozart
        # overlay still carried "sparse_octaves", "walking_bass_chromatic",
        # "oscillation_trill" and "unclassified" from an April extraction — none
        # of which the classifier emits any more and none of which any corpus bar
        # carries — and it was overriding the freshly compiled distribution for
        # the flagship composer. The planner then scheduled textures that could
        # never be retrieved.
        from ..enums import AccompType

        valid = {t.value for t in AccompType}
        lh_merged = {k: v for k, v in lh_merged.items() if k in valid}
        transition_updates = {
            src: {t: v for t, v in tgts.items() if t in valid}
            for src, tgts in transition_updates.items()
            if src in valid
        }
        transition_updates = {k: v for k, v in transition_updates.items() if v}

        if not lh_changed and not transition_updates:
            return None

        overlay = {
            "evidence_source": "corpus_feedback",
            "last_updated": self.today,
            "bundle_count": len(self.bundles),
        }
        if lh_changed:
            overlay["lh_distribution"] = lh_merged
        if transition_updates:
            # Merge transitions into compiled baseline too
            compiled_trans = compiled_stats.get("transition_matrix", {})
            merged_trans = dict(compiled_trans)
            for src, targets in transition_updates.items():
                if src not in merged_trans:
                    merged_trans[src] = {}
                merged_trans[src].update(targets)
            overlay["transition_matrix"] = merged_trans

        return self._write_overlay(output_dir, "scoped_statistics.json", overlay)

    # ── Figuration Overlay ──────────────────────────────────────────────

    def _build_figuration_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build figuration_templates.json overlay with grounding upgrades."""
        claims = self.registry.get_by_category("figuration")
        promotable = [c for c in claims if self._is_promotable(c)]

        if not promotable:
            return None

        updates = []
        for claim in promotable:
            if claim.confidence >= SUPPORT_CONFIDENCE:
                updates.append(
                    {
                        "id": claim.source_entry_id,
                        "grounding": "hard_corroborated",
                        "evidence_source": "corpus_feedback",
                        "evidence_confidence": claim.confidence,
                        "support_count": claim.support_count,
                        "last_updated": self.today,
                    }
                )

        if not updates:
            return None

        # Figuration overlays are lists (extend existing)
        return self._write_overlay(output_dir, "figuration_templates.json", updates)

    # ── Fingerprint Overlay ─────────────────────────────────────────────

    def _build_fingerprint_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build fingerprint_rules.json overlay with confidence adjustments."""
        claims = self.registry.get_by_category("fingerprint")
        promotable = [c for c in claims if self._is_promotable(c)]

        if not promotable:
            return None

        # Fingerprint overlays update the dict (required_count stays, items extends)
        new_items = []
        for claim in promotable:
            if claim.confidence >= SUPPORT_CONFIDENCE:
                new_items.append(
                    {
                        "id": claim.source_entry_id,
                        "evidence_confidence": claim.confidence,
                        "evidence_source": "corpus_feedback",
                        "support_count": claim.support_count,
                        "contradiction_count": claim.contradiction_count,
                        "last_updated": self.today,
                    }
                )

        if not new_items:
            return None

        overlay = {"evidence_annotations": new_items}
        return self._write_overlay(output_dir, "fingerprint_rules.json", overlay)

    # ── Harmonic Device Overlay ─────────────────────────────────────────

    def _build_harmonic_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build harmonic_devices.json overlay with frequency_weight adjustments."""
        claims = self.registry.get_by_category("harmonic_device")
        promotable = [c for c in claims if self._is_promotable(c)]

        if not promotable:
            return None

        updates = []
        for claim in promotable:
            orig_weight = claim.test_config.get("frequency_weight", 0.3)

            # Adjust weight based on evidence
            if claim.confidence >= SUPPORT_CONFIDENCE:
                # Strengthen: increase weight by up to 50%
                adjustment = min(claim.confidence - 0.5, 0.5)
                new_weight = min(orig_weight * (1.0 + adjustment), 1.0)
            elif claim.confidence < (1.0 - CONTRADICT_CONFIDENCE):
                # Weaken: decrease weight
                new_weight = orig_weight * 0.75
            else:
                continue

            if abs(new_weight - orig_weight) > 0.01:
                updates.append(
                    {
                        "id": claim.source_entry_id,
                        "frequency_weight": round(new_weight, 3),
                        "evidence_source": "corpus_feedback",
                        "evidence_confidence": claim.confidence,
                        "last_updated": self.today,
                    }
                )

        if not updates:
            return None

        return self._write_overlay(output_dir, "harmonic_devices.json", updates)

    # ── Melody Prior Overlay ────────────────────────────────────────────

    def _build_melody_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build melody_priors.json overlay with grounding upgrades."""
        claims = self.registry.get_by_category("melody_prior")
        promotable = [c for c in claims if self._is_promotable(c)]

        if not promotable:
            return None

        updates = []
        for claim in promotable:
            if claim.confidence >= SUPPORT_CONFIDENCE:
                updates.append(
                    {
                        "id": claim.source_entry_id,
                        "grounding": "hard_corroborated",
                        "evidence_source": "corpus_feedback",
                        "evidence_confidence": claim.confidence,
                        "last_updated": self.today,
                    }
                )

        if not updates:
            return None

        return self._write_overlay(output_dir, "melody_priors.json", updates)

    # ── Review Rubric Overlay ───────────────────────────────────────────

    def _build_review_overlay(self, output_dir: Path) -> Optional[Path]:
        """Build review_rubric.json overlay with severity adjustments."""
        # Review rubric claims come from anti-patterns and fingerprints
        fp_claims = self.registry.get_by_category("fingerprint")
        ap_claims = self.registry.get_by_category("anti_pattern")

        all_promotable = [c for c in fp_claims + ap_claims if self._is_promotable(c)]

        if not all_promotable:
            return None

        check_updates = []
        for claim in all_promotable:
            if claim.category == "fingerprint" and claim.confidence >= 0.8:
                # Upgrade fingerprint check to "important" severity
                check_updates.append(
                    {
                        "id": f"fp_{claim.source_entry_id}",
                        "severity": "important",
                        "evidence_source": "corpus_feedback",
                        "evidence_confidence": claim.confidence,
                        "last_updated": self.today,
                    }
                )
            elif claim.category == "anti_pattern" and claim.confidence >= 0.8:
                # Upgrade anti-pattern to "error" severity
                check_updates.append(
                    {
                        "id": claim.source_entry_id,
                        "severity": "error",
                        "evidence_source": "corpus_feedback",
                        "evidence_confidence": claim.confidence,
                        "last_updated": self.today,
                    }
                )

        if not check_updates:
            return None

        overlay = {"checks": check_updates}
        return self._write_overlay(output_dir, "review_rubric.json", overlay)

    # ── Helpers ─────────────────────────────────────────────────────────

    def _is_promotable(self, claim: MeasurableClaim) -> bool:
        """Check if a claim has enough evidence to promote."""
        return claim.total_tested >= MIN_TESTED

    def _cap_divergence(self, compiled: float, observed: float) -> float:
        """Cap the observed value so it doesn't diverge too far from compiled."""
        max_shift = max(compiled * MAX_DIVERGENCE, 0.02)
        if observed > compiled + max_shift:
            return compiled + max_shift
        elif observed < compiled - max_shift:
            return max(compiled - max_shift, 0.0)
        return observed

    def _compute_observed_average(
        self, claim: MeasurableClaim, field: str, key: str
    ) -> Optional[float]:
        """Compute the average observed value for a distribution key
        across all bundles."""
        if not self.bundles:
            return None

        values = []
        for bundle in self.bundles:
            dist = getattr(bundle, field, None)
            if isinstance(dist, dict) and key in dist:
                values.append(dist[key])

        if not values:
            return None

        return sum(values) / len(values)

    def _compute_transition_average(
        self, claim: MeasurableClaim, src: str, tgt: str
    ) -> Optional[float]:
        """Compute average transition proportion across bundles."""
        if not self.bundles:
            return None

        proportions = []
        for bundle in self.bundles:
            trans = bundle.transition_counts
            if src in trans:
                total = sum(trans[src].values())
                if total > 0:
                    proportions.append(trans[src].get(tgt, 0) / total)

        if not proportions:
            return None

        return sum(proportions) / len(proportions)

    def _load_compiled(self, filename: str) -> Optional[Dict]:
        """Load a file from the compiled pack directory."""
        path = self.compiled_pack_dir / filename
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return None

    def _write_overlay(self, output_dir: Path, filename: str, data: Any) -> Path:
        """Write an overlay JSON file."""
        out_path = output_dir / filename
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        return out_path
