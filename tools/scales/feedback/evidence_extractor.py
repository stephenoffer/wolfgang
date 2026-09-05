"""
Evidence Extractor — extract measurable musical evidence from parsed scores.

Wraps style_analyzer.analyze_score() and build_full_corpus.analyze_score_bars()
to produce a normalized EvidenceBundle suitable for claim matching.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.build_full_corpus import analyze_score_bars

from ..style_analyzer import analyze_score

# ─── EvidenceBundle ─────────────────────────────────────────────────────────


@dataclass
class EvidenceBundle:
    """Normalized evidence extracted from a single score."""

    composer: str = ""
    source_file: str = ""
    bar_count: int = 0

    # Bar-level distributions
    lh_texture_distribution: Dict[str, float] = field(default_factory=dict)
    rh_texture_distribution: Dict[str, float] = field(default_factory=dict)
    transition_counts: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Phrase-level evidence
    phrase_lengths: List[float] = field(default_factory=list)
    phrase_length_avg: float = 0.0
    cadence_types: Dict[str, int] = field(default_factory=dict)
    phrase_roles: Dict[str, int] = field(default_factory=dict)

    # Gesture-level evidence
    gesture_functions: Dict[str, int] = field(default_factory=dict)
    gesture_contours: Dict[str, int] = field(default_factory=dict)

    # Harmonic evidence
    harmonic_rhythm_avg: Optional[float] = None
    chromatic_pct: float = 0.0
    cadence_approach_patterns: List[Dict] = field(default_factory=list)
    modulation_targets: Dict[str, int] = field(default_factory=dict)
    chord_quality_distribution: Dict[str, float] = field(default_factory=dict)
    deceptive_cadence_pct: float = 0.0
    half_cadence_pct: float = 0.0

    # Melodic evidence
    stepwise_pct: float = 0.0
    leap_pct: float = 0.0
    large_leap_pct: float = 0.0
    direction_changes_per_bar: float = 0.0
    register_range: int = 0
    register_center: float = 60.0

    # Texture evidence
    density_cv: float = 0.0
    events_per_bar: float = 0.0
    events_per_bar_rh: float = 0.0
    events_per_bar_lh: float = 0.0
    hand_simultaneity_pct: float = 0.0
    texture_change_pct: float = 0.0
    identical_consecutive_pct: float = 0.0

    # Dynamics evidence
    dynamic_markings_per_bar: float = 0.0
    sf_density: float = 0.0
    suspension_pct: float = 0.0

    # Rhythm evidence
    triplet_pct: float = 0.0
    rest_ratio: float = 0.0
    rhythmic_variety: int = 0
    bass_change_rate: float = 0.0

    # Voice leading evidence
    parallel_motion_pct: float = 0.0
    contrary_motion_pct: float = 0.0
    voice_independence_score: Optional[float] = None
    voice_leading_distance_avg: Optional[float] = None

    # Articulation evidence
    staccato_pct: Optional[float] = None
    legato_span_avg: Optional[float] = None

    # Modulation evidence
    tonal_stability: Optional[float] = None
    key_area_count: int = 0

    # Full raw metrics from style_analyzer
    raw_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EvidenceBundle:
        """Rebuild from a dict via THE field-driven reconstructor.

        This filtered `data` against the field names itself, in a body identical
        to the one in the sibling module — two copies of the rule that
        `piece_graph._dataclass_from_dict` already owns, and which recurses into
        nested dataclasses where these did not.
        """
        from ..piece_graph import _dataclass_from_dict

        return _dataclass_from_dict(cls, data)


# ─── Extraction Functions ───────────────────────────────────────────────────


def extract_from_file(filepath: str, composer: str) -> Optional[EvidenceBundle]:
    """Extract an EvidenceBundle from a score file.

    Uses both style_analyzer (high-level metrics) and build_full_corpus
    (bar-level texture/density data) to build a complete picture.
    """
    try:
        import music21

        score = music21.converter.parse(filepath)
    except Exception as e:
        print(f"  WARN: Could not parse {filepath}: {e}", file=sys.stderr)
        return None

    return extract_from_score(score, composer, filepath)


def extract_from_score(score, composer: str, source_file: str = "") -> Optional[EvidenceBundle]:
    """Extract an EvidenceBundle from an already-parsed music21 Score."""

    bundle = EvidenceBundle(
        composer=composer,
        source_file=os.path.basename(source_file) if source_file else "",
    )

    # ── Step 1: High-level metrics via style_analyzer ──
    # Write to temp file if needed, or use existing path
    if source_file:
        raw = analyze_score(source_file)
    else:
        # Write score to temp file for analysis
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            score.write("musicxml", fp=tmp_path)
            raw = analyze_score(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    if raw is None:
        return None

    bundle.raw_metrics = raw
    bundle.bar_count = raw.get("bars", 0)
    if bundle.bar_count == 0:
        return None

    # Transfer scalar metrics
    bundle.events_per_bar = raw.get("events_per_bar", 0.0)
    bundle.events_per_bar_rh = raw.get("events_per_bar_rh", 0.0)
    bundle.events_per_bar_lh = raw.get("events_per_bar_lh", 0.0)
    bundle.stepwise_pct = raw.get("stepwise_pct", 0.0)
    bundle.leap_pct = raw.get("leap_pct", 0.0)
    bundle.large_leap_pct = raw.get("large_leap_pct", 0.0)
    bundle.direction_changes_per_bar = raw.get("direction_changes_per_bar", 0.0)
    bundle.chromatic_pct = raw.get("chromatic_pct", 0.0)
    bundle.triplet_pct = raw.get("triplet_pct", 0.0)
    bundle.rest_ratio = raw.get("rest_ratio", 0.0)
    bundle.rhythmic_variety = raw.get("rhythmic_variety", 0)
    bundle.bass_change_rate = raw.get("bass_change_rate", 0.0)
    bundle.phrase_length_avg = raw.get("phrase_length_avg", 0.0)
    bundle.register_range = raw.get("register_range", 0)
    bundle.register_center = raw.get("register_center", 60.0)
    bundle.density_cv = raw.get("density_cv", 0.0)
    bundle.hand_simultaneity_pct = raw.get("hand_simultaneity_pct", 0.0)
    bundle.texture_change_pct = raw.get("texture_change_pct", 0.0)
    bundle.identical_consecutive_pct = raw.get("identical_consecutive_pct", 0.0)
    bundle.dynamic_markings_per_bar = raw.get("dynamic_markings_per_bar", 0.0)
    bundle.sf_density = raw.get("sf_density", 0.0)
    bundle.suspension_pct = raw.get("suspension_pct", 0.0)
    bundle.parallel_motion_pct = raw.get("parallel_motion_pct", 0.0)
    bundle.contrary_motion_pct = raw.get("contrary_motion_pct", 0.0)
    bundle.voice_independence_score = raw.get("voice_independence_score")
    bundle.voice_leading_distance_avg = raw.get("voice_leading_distance_avg")
    bundle.staccato_pct = raw.get("staccato_pct")
    bundle.legato_span_avg = raw.get("legato_span_avg")
    bundle.tonal_stability = raw.get("tonal_stability")
    bundle.key_area_count = raw.get("key_area_count", 0)
    bundle.harmonic_rhythm_avg = raw.get("harmonic_rhythm_avg")
    bundle.deceptive_cadence_pct = raw.get("deceptive_cadence_pct", 0.0)
    bundle.half_cadence_pct = raw.get("half_cadence_pct", 0.0)

    # Cadence types
    ct = raw.get("cadence_types")
    if isinstance(ct, dict):
        bundle.cadence_types = ct

    # Chord quality distribution (normalize to proportions)
    chord_keys = ["major_chord_pct", "minor_chord_pct", "dim_chord_pct", "dom7_chord_pct"]
    cq = {}
    for ck in chord_keys:
        v = raw.get(ck)
        if v is not None:
            cq[ck.replace("_chord_pct", "")] = v
    bundle.chord_quality_distribution = cq

    # ── Step 2: Bar-level data via build_full_corpus.analyze_score_bars ──
    source_name = os.path.splitext(os.path.basename(source_file))[0] if source_file else "unknown"
    bars = analyze_score_bars(score, composer, source_name)

    if bars:
        bundle.bar_count = max(bundle.bar_count, len(bars))

        # LH texture distribution
        lh_counts: Counter = Counter()
        rh_counts: Counter = Counter()
        for bar in bars:
            lh_counts[bar.get("lh_texture", "unclassified")] += 1
            rh_counts[bar.get("rh_texture", "unclassified")] += 1

        total = max(len(bars), 1)
        bundle.lh_texture_distribution = {
            k: round(v / total, 4) for k, v in lh_counts.most_common()
        }
        bundle.rh_texture_distribution = {
            k: round(v / total, 4) for k, v in rh_counts.most_common()
        }

        # Transition counts (consecutive bar LH texture pairs)
        trans: Dict[str, Dict[str, int]] = {}
        for i in range(1, len(bars)):
            prev_tex = bars[i - 1].get("lh_texture", "unclassified")
            curr_tex = bars[i].get("lh_texture", "unclassified")
            if prev_tex not in trans:
                trans[prev_tex] = {}
            trans[prev_tex][curr_tex] = trans[prev_tex].get(curr_tex, 0) + 1
        bundle.transition_counts = trans

        # Phrase roles
        role_counts: Counter = Counter()
        for bar in bars:
            role_counts[bar.get("phrase_position", "middle")] += 1
        bundle.phrase_roles = dict(role_counts)

    return bundle


def extract_batch(filepaths: List[str], composer: str) -> List[EvidenceBundle]:
    """Extract evidence from multiple score files."""
    bundles = []
    for fp in filepaths:
        bundle = extract_from_file(fp, composer)
        if bundle is not None:
            bundles.append(bundle)
    return bundles


def aggregate_bundles(bundles: List[EvidenceBundle]) -> Dict[str, Any]:
    """Aggregate multiple EvidenceBundle instances into summary statistics.

    Returns a dict with mean/stdev for scalar fields and merged distributions.
    """
    if not bundles:
        return {}

    import statistics

    # Collect scalar values
    scalar_fields = [
        "events_per_bar",
        "events_per_bar_rh",
        "events_per_bar_lh",
        "stepwise_pct",
        "leap_pct",
        "large_leap_pct",
        "direction_changes_per_bar",
        "chromatic_pct",
        "triplet_pct",
        "rest_ratio",
        "bass_change_rate",
        "phrase_length_avg",
        "density_cv",
        "hand_simultaneity_pct",
        "texture_change_pct",
        "identical_consecutive_pct",
        "dynamic_markings_per_bar",
        "sf_density",
        "suspension_pct",
        "parallel_motion_pct",
        "contrary_motion_pct",
        "deceptive_cadence_pct",
        "half_cadence_pct",
    ]

    summary: Dict[str, Any] = {"bundle_count": len(bundles), "total_bars": 0}

    for sf in scalar_fields:
        vals = [getattr(b, sf, None) for b in bundles]
        vals = [v for v in vals if v is not None and isinstance(v, (int, float))]
        if vals:
            summary[sf] = {
                "mean": round(statistics.mean(vals), 3),
                "stdev": round(statistics.pstdev(vals), 3),
                "min": round(min(vals), 3),
                "max": round(max(vals), 3),
                "n": len(vals),
            }

    # Merge LH distributions (weighted by bar_count)
    merged_lh: Counter = Counter()
    total_bars = 0
    for b in bundles:
        bc = max(b.bar_count, 1)
        total_bars += bc
        for tex, pct in b.lh_texture_distribution.items():
            merged_lh[tex] += pct * bc
    summary["total_bars"] = total_bars
    if total_bars > 0:
        summary["lh_distribution_merged"] = {
            k: round(v / total_bars, 4) for k, v in merged_lh.most_common()
        }

    # Merge transition counts
    merged_trans: Dict[str, Dict[str, int]] = {}
    for b in bundles:
        for src, targets in b.transition_counts.items():
            if src not in merged_trans:
                merged_trans[src] = {}
            for tgt, cnt in targets.items():
                merged_trans[src][tgt] = merged_trans[src].get(tgt, 0) + cnt
    summary["transition_counts_merged"] = merged_trans

    return summary


# ─── Persistence ────────────────────────────────────────────────────────────


def save_bundle(bundle: EvidenceBundle, output_dir: Path) -> Path:
    """Save an EvidenceBundle to JSON in the given directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"evidence_{bundle.source_file.replace('.', '_')}.json"
    out_path = output_dir / filename
    with open(out_path, "w") as f:
        json.dump(bundle.to_dict(), f, indent=2)
    return out_path


def load_bundle(path: Path) -> EvidenceBundle:
    """Load an EvidenceBundle from JSON."""
    with open(path) as f:
        data = json.load(f)
    return EvidenceBundle.from_dict(data)


def save_evidence_samples(bundles: List[EvidenceBundle], output_dir: Path) -> Path:
    """Save a list of evidence bundles as evidence_samples.json."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "evidence_samples.json"
    data = [b.to_dict() for b in bundles]
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return out_path
