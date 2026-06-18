"""
Claim Registry — registry of measurable claims derived from compiled packs.

Each claim maps a textual/structural assertion from the context doctrine to
a testable predicate over EvidenceBundle. Claims accumulate support/contradiction
evidence as new scores are ingested.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ─── Claim Model ────────────────────────────────────────────────────────────


@dataclass
class MeasurableClaim:
    """A single testable claim derived from the compiled context system."""

    claim_id: str = ""
    source_file: str = ""  # e.g., "fingerprint_rules.json"
    source_entry_id: str = ""  # e.g., "vocal_thinking_in_instrumental_writing"
    category: str = ""  # fingerprint | distribution | figuration |
    # melody_prior | harmonic_device | anti_pattern |
    # cadence | prompt_semantic
    description: str = ""
    test_type: str = ""  # distribution | threshold | ratio | presence
    test_config: Dict[str, Any] = field(default_factory=dict)

    # Evidence accumulation
    support_count: int = 0
    contradiction_count: int = 0
    total_tested: int = 0
    confidence: float = 0.0  # support / (support + contradiction)
    current_grounding: str = "unverified"  # hard_corroborated | soft_corroborated
    # | interpretive | unverified | contradicted

    def update_confidence(self) -> None:
        """Recalculate confidence from support/contradiction counts."""
        total = self.support_count + self.contradiction_count
        if total > 0:
            self.confidence = round(self.support_count / total, 4)
        else:
            self.confidence = 0.0

    def record_support(self) -> None:
        self.support_count += 1
        self.total_tested += 1
        self.update_confidence()

    def record_contradiction(self) -> None:
        self.contradiction_count += 1
        self.total_tested += 1
        self.update_confidence()

    def record_neutral(self) -> None:
        """Evidence was tested but neither supports nor contradicts."""
        self.total_tested += 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MeasurableClaim:
        known = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)


# ─── Claim Registry ────────────────────────────────────────────────────────


class ClaimRegistry:
    """Registry of measurable claims for a single composer."""

    def __init__(self, composer: str):
        self.composer = composer
        self.claims: Dict[str, MeasurableClaim] = {}

    def add(self, claim: MeasurableClaim) -> None:
        self.claims[claim.claim_id] = claim

    def get(self, claim_id: str) -> Optional[MeasurableClaim]:
        return self.claims.get(claim_id)

    def get_by_category(self, category: str) -> List[MeasurableClaim]:
        return [c for c in self.claims.values() if c.category == category]

    def get_all(self) -> List[MeasurableClaim]:
        return list(self.claims.values())

    def __len__(self) -> int:
        return len(self.claims)

    def save(self, output_dir: Path) -> Path:
        """Save registry to claims.json in the given directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / "claims.json"
        data = {
            "composer": self.composer,
            "claim_count": len(self.claims),
            "claims": [c.to_dict() for c in self.claims.values()],
        }
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        return out_path

    @classmethod
    def load(cls, path: Path) -> ClaimRegistry:
        """Load registry from claims.json."""
        with open(path) as f:
            data = json.load(f)
        registry = cls(composer=data.get("composer", ""))
        for cd in data.get("claims", []):
            claim = MeasurableClaim.from_dict(cd)
            registry.add(claim)
        return registry

    def save_support_stats(self, output_dir: Path) -> Path:
        """Save aggregate support statistics."""
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / "support_stats.json"

        by_category: Dict[str, Dict[str, Any]] = {}
        for c in self.claims.values():
            cat = c.category
            if cat not in by_category:
                by_category[cat] = {
                    "count": 0,
                    "supported": 0,
                    "contradicted": 0,
                    "avg_confidence": 0.0,
                    "tested": 0,
                }
            by_category[cat]["count"] += 1
            by_category[cat]["supported"] += c.support_count
            by_category[cat]["contradicted"] += c.contradiction_count
            by_category[cat]["tested"] += c.total_tested

        for cat_stats in by_category.values():
            cat_stats["count"]
            total = cat_stats["supported"] + cat_stats["contradicted"]
            cat_stats["avg_confidence"] = round(cat_stats["supported"] / max(total, 1), 3)

        data = {
            "composer": self.composer,
            "total_claims": len(self.claims),
            "by_category": by_category,
        }
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
        return out_path


# ─── Bootstrapping ──────────────────────────────────────────────────────────


def bootstrap_from_compiled_pack(composer: str, compiled_pack_dir: Path) -> ClaimRegistry:
    """Bootstrap a ClaimRegistry from existing compiled pack JSONs.

    Parses the 22 compiled pack files and generates testable claims
    from entries with measurable properties.
    """
    registry = ClaimRegistry(composer)

    # ── Distribution claims from scoped_statistics.json ──
    _bootstrap_distribution_claims(registry, compiled_pack_dir)

    # ── Fingerprint claims from fingerprint_rules.json ──
    _bootstrap_fingerprint_claims(registry, compiled_pack_dir)

    # ── Figuration claims from figuration_templates.json ──
    _bootstrap_figuration_claims(registry, compiled_pack_dir)

    # ── Melody prior claims from melody_priors.json ──
    _bootstrap_melody_claims(registry, compiled_pack_dir)

    # ── Harmonic device claims from harmonic_devices.json ──
    _bootstrap_harmonic_claims(registry, compiled_pack_dir)

    # ── Anti-pattern claims from anti_pattern_rules.json ──
    _bootstrap_anti_pattern_claims(registry, compiled_pack_dir)

    # ── Cadence claims from cadence_scripts.json ──
    _bootstrap_cadence_claims(registry, compiled_pack_dir)

    # ── Prompt semantic claims from prompt_semantics.json ──
    _bootstrap_prompt_claims(registry, compiled_pack_dir)

    return registry


def _load_json(path: Path) -> Any:
    """Load JSON file, returning None if missing."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def _bootstrap_distribution_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate distribution claims from scoped_statistics.json."""
    stats = _load_json(pack_dir / "scoped_statistics.json")
    if not stats:
        return

    lh_dist = stats.get("lh_distribution", {})
    for texture_name, proportion in lh_dist.items():
        registry.add(
            MeasurableClaim(
                claim_id=f"dist:lh:{texture_name}",
                source_file="scoped_statistics.json",
                source_entry_id=f"lh_distribution.{texture_name}",
                category="distribution",
                description=f"LH texture '{texture_name}' should be ~{proportion:.1%} of bars",
                test_type="distribution",
                test_config={
                    "field": "lh_texture_distribution",
                    "key": texture_name,
                    "expected_proportion": proportion,
                    "tolerance": 0.15,  # absolute tolerance for KL-like comparison
                },
                current_grounding="hard_corroborated" if proportion > 0 else "unverified",
            )
        )

    # Transition matrix claims (top transitions only)
    trans = stats.get("transition_matrix", {})
    for src, targets in trans.items():
        for tgt, prob in targets.items():
            if prob >= 0.05:  # only track meaningful transitions
                registry.add(
                    MeasurableClaim(
                        claim_id=f"trans:{src}:{tgt}",
                        source_file="scoped_statistics.json",
                        source_entry_id=f"transition_matrix.{src}.{tgt}",
                        category="distribution",
                        description=f"Transition {src}→{tgt} should be ~{prob:.1%}",
                        test_type="distribution",
                        test_config={
                            "field": "transition_counts",
                            "src": src,
                            "tgt": tgt,
                            "expected_proportion": prob,
                            "tolerance": 0.15,
                        },
                        current_grounding="hard_corroborated",
                    )
                )


def _bootstrap_fingerprint_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate presence claims from fingerprint_rules.json."""
    fp_data = _load_json(pack_dir / "fingerprint_rules.json")
    if not fp_data:
        return

    items = fp_data.get("items", [])
    for item in items:
        fp_id = item.get("id", "")
        name = item.get("name", "")
        desc = item.get("description", "")

        # Map fingerprint names to testable metrics
        test_config = _fingerprint_to_test_config(fp_id, name, desc)

        registry.add(
            MeasurableClaim(
                claim_id=f"fingerprint:{fp_id}",
                source_file="fingerprint_rules.json",
                source_entry_id=fp_id,
                category="fingerprint",
                description=f"Fingerprint: {name}",
                test_type=test_config.get("test_type", "presence"),
                test_config=test_config,
                current_grounding="soft_corroborated",
            )
        )


def _fingerprint_to_test_config(fp_id: str, name: str, desc: str) -> Dict[str, Any]:
    """Map fingerprint descriptions to testable metric configurations.

    Many fingerprints are qualitative and hard to test automatically.
    We map what we can to quantitative proxies.
    """
    name_lower = name.lower()
    desc_lower = desc.lower()

    # Vocal/singable → high stepwise, moderate leaps
    if "vocal" in name_lower or "singable" in name_lower or "sung" in desc_lower:
        return {
            "test_type": "threshold",
            "metric": "stepwise_pct",
            "direction": "gte",
            "threshold": 45.0,
            "description": "Vocal writing implies high stepwise motion",
        }

    # Chromatic inflection → moderate chromatic percentage
    if "chromatic" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "chromatic_pct",
            "direction": "gte",
            "threshold": 3.0,
            "description": "Chromatic inflection implies some accidentals",
        }

    # Transparent texture → moderate density, low hand simultaneity
    if "transparent" in name_lower or "chamber" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "events_per_bar",
            "direction": "lte",
            "threshold": 30.0,
            "description": "Transparent texture implies moderate density",
        }

    # Symmetrical phrase → phrase length clustering near 4-bar units
    if "symmetr" in name_lower or "phrase structure" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "phrase_length_avg",
            "direction": "range",
            "min": 8.0,
            "max": 24.0,
            "description": "Symmetrical phrasing implies consistent lengths",
        }

    # Minor-mode shadow → some mode mixture
    if "minor" in name_lower and "shadow" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "chromatic_pct",
            "direction": "gte",
            "threshold": 2.0,
            "description": "Minor-mode shadows involve chromatic alterations",
        }

    # Dynamic contrast
    if "dynamic" in name_lower or "contrast" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "density_cv",
            "direction": "gte",
            "threshold": 0.2,
            "description": "Dynamic contrast implies texture variation",
        }

    # Silence / breathing
    if "silence" in name_lower or "breath" in name_lower:
        return {
            "test_type": "threshold",
            "metric": "rest_ratio",
            "direction": "gte",
            "threshold": 2.0,
            "description": "Breathing implies some rests",
        }

    # Default: qualitative, tested as presence (always passes)
    return {
        "test_type": "presence",
        "metric": None,
        "description": "Qualitative fingerprint — no automatic metric test",
    }


def _bootstrap_figuration_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate claims from figuration_templates.json."""
    figs = _load_json(pack_dir / "figuration_templates.json")
    if not figs or not isinstance(figs, list):
        return

    for fig in figs:
        fig_id = fig.get("id", "")
        keyword = fig.get("pattern_keyword", "")
        if not keyword:
            continue

        registry.add(
            MeasurableClaim(
                claim_id=f"figuration:{fig_id}",
                source_file="figuration_templates.json",
                source_entry_id=fig_id,
                category="figuration",
                description=f"Figuration '{keyword}' should appear in LH corpus",
                test_type="distribution",
                test_config={
                    "field": "lh_texture_distribution",
                    "key": keyword,
                    "expected_proportion": None,  # no specific target, just presence
                    "presence_only": True,
                },
                current_grounding=fig.get("grounding", "unverified"),
            )
        )


def _bootstrap_melody_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate claims from melody_priors.json."""
    priors = _load_json(pack_dir / "melody_priors.json")
    if not priors or not isinstance(priors, list):
        return

    for prior in priors:
        prior_id = prior.get("id", "")
        category = prior.get("category", "")
        params = prior.get("parameters", {})

        # Phrase length claims
        if category == "phrase_structure" and "typical_length" in params:
            length_str = params["typical_length"]
            # Try to extract bar count (e.g., "4 bars", "8 bars (4+4)")
            test_config = {
                "test_type": "presence",
                "metric": None,
                "raw_value": length_str,
                "description": f"Phrase structure: {prior.get('description', '')}",
            }
        else:
            test_config = {
                "test_type": "presence",
                "metric": None,
                "description": prior.get("description", ""),
            }

        registry.add(
            MeasurableClaim(
                claim_id=f"melody:{prior_id}",
                source_file="melody_priors.json",
                source_entry_id=prior_id,
                category="melody_prior",
                description=prior.get("description", ""),
                test_type=test_config.get("test_type", "presence"),
                test_config=test_config,
                current_grounding=prior.get("grounding", "unverified"),
            )
        )


def _bootstrap_harmonic_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate claims from harmonic_devices.json."""
    devices = _load_json(pack_dir / "harmonic_devices.json")
    if not devices or not isinstance(devices, list):
        return

    for device in devices:
        dev_id = device.get("id", "")
        freq = device.get("frequency_weight", 0.0)
        contexts = device.get("contexts", [])

        registry.add(
            MeasurableClaim(
                claim_id=f"harmonic:{dev_id}",
                source_file="harmonic_devices.json",
                source_entry_id=dev_id,
                category="harmonic_device",
                description=f"Harmonic device: {device.get('name', dev_id)}",
                test_type="presence",
                test_config={
                    "metric": None,
                    "frequency_weight": freq,
                    "contexts": contexts,
                    "description": f"Device '{dev_id}' with weight {freq}",
                },
                current_grounding="soft_corroborated",
            )
        )


def _bootstrap_anti_pattern_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate absence claims from anti_pattern_rules.json."""
    aps = _load_json(pack_dir / "anti_pattern_rules.json")
    if not aps or not isinstance(aps, list):
        return

    # Map detector names to metrics where possible
    detector_metrics = {
        "flat_dynamics": ("density_cv", "lte", 0.15, "Flat dynamics → low density CV"),
        "same_accompaniment": (
            "identical_consecutive_pct",
            "gte",
            30.0,
            "Same accompaniment → high identical consecutive %",
        ),
    }

    for ap in aps:
        ap_id = ap.get("id", "")
        detector = ap.get("detector", "")

        if detector in detector_metrics:
            metric, direction, threshold, desc = detector_metrics[detector]
            test_config = {
                "test_type": "threshold",
                "metric": metric,
                "direction": direction,
                "threshold": threshold,
                "description": desc,
                "is_anti_pattern": True,
            }
        else:
            test_config = {
                "test_type": "presence",
                "metric": None,
                "detector": detector,
                "is_anti_pattern": True,
                "description": f"Anti-pattern: {ap.get('name', ap_id)}",
            }

        registry.add(
            MeasurableClaim(
                claim_id=f"anti_pattern:{ap_id}",
                source_file="anti_pattern_rules.json",
                source_entry_id=ap_id,
                category="anti_pattern",
                description=ap.get("description", ""),
                test_type=test_config.get("test_type", "presence"),
                test_config=test_config,
                current_grounding="soft_corroborated",
            )
        )


def _bootstrap_cadence_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate claims from cadence_scripts.json about cadence type usage."""
    scripts = _load_json(pack_dir / "cadence_scripts.json")
    if not scripts or not isinstance(scripts, list):
        return

    # Track cadence types present
    for script in scripts:
        script_id = script.get("id", "")
        registry.add(
            MeasurableClaim(
                claim_id=f"cadence:{script_id}",
                source_file="cadence_scripts.json",
                source_entry_id=script_id,
                category="cadence",
                description=f"Cadence script: {script.get('id', '')}",
                test_type="presence",
                test_config={
                    "metric": None,
                    "description": f"Cadence type '{script_id}' should appear in corpus",
                },
                current_grounding="hard_corroborated",
            )
        )


def _bootstrap_prompt_claims(registry: ClaimRegistry, pack_dir: Path) -> None:
    """Generate correlation claims from prompt_semantics.json."""
    semantics = _load_json(pack_dir / "prompt_semantics.json")
    if not semantics or not isinstance(semantics, list):
        return

    for sem in semantics:
        word = sem.get("word", "")
        if not word:
            continue

        # These are interpretive by nature — just track them
        test_config = {
            "test_type": "presence",
            "metric": None,
            "tempo_range": sem.get("tempo_range"),
            "mode_scale": sem.get("mode_scale"),
            "dynamics": sem.get("dynamics"),
            "description": f"Prompt word '{word}' maps to specific parameters",
        }

        registry.add(
            MeasurableClaim(
                claim_id=f"prompt:{word}",
                source_file="prompt_semantics.json",
                source_entry_id=word,
                category="prompt_semantic",
                description=f"Prompt semantic: '{word}'",
                test_type="presence",
                test_config=test_config,
                current_grounding=sem.get("grounding", "interpretive"),
            )
        )
