"""
DonorStrategy — selects donor composers for sparse-corpus targets.

For Tier C/D composers without native corpus data, finds historically
related Tier A/B composers to borrow patterns from. All borrowed
material is filtered through target fingerprints and anti-patterns.
Donor provenance is tracked and leakage is penalized in scoring.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Tuple

from .models import DonorPlan, StyleProgram

logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
COMPILED_PACKS = _BASE / "compiled_packs"

# Known Tier A/B composers with corpus data
_TIER_AB_COMPOSERS = {
    "beethoven": ("A", "classical"),
    "mozart": ("A", "classical"),
    "chopin": ("A", "romantic"),
}

# Genre-based fallback donors
_GENRE_DONORS = {
    "baroque": ["bach"],
    "classical": ["mozart", "beethoven"],
    "romantic": ["chopin", "beethoven"],
    "late-romantic": ["beethoven"],
    "impressionist": ["chopin"],
    "nationalistic": ["beethoven", "chopin"],
    "modern": ["beethoven"],
    "minimalist": ["mozart"],
    "film-score": ["beethoven"],
}


class DonorStrategy:
    """Selects and applies donor composers for sparse-corpus targets."""

    def resolve_donors(
        self, target_composer: str, target_tier: str, target_genre: str = ""
    ) -> DonorPlan:
        """Find donor composers for a sparse-corpus target.

        Uses influence_axes.json to find historically related composers.
        Falls back to genre-level matching.

        Returns a DonorPlan with donors and weights.
        """
        if target_tier in ("A", "B"):
            # Tier A/B don't need donors
            return DonorPlan(donors=[], max_donor_weight=0.0)

        donors: List[Tuple[str, float]] = []

        # Try influence-based selection first
        influence_donors = self._find_by_influence(target_composer)
        donors.extend(influence_donors)

        # Fall back to genre-based selection
        if not donors and target_genre:
            genre_donors = _GENRE_DONORS.get(target_genre, [])
            for gd in genre_donors:
                if gd in _TIER_AB_COMPOSERS:
                    donors.append((gd, 0.4))

        # Default fallback: Mozart (most universal classical composer)
        if not donors:
            donors = [("mozart", 0.3)]

        # Normalize weights and cap at 2 donors
        donors = donors[:2]
        total_weight = sum(w for _, w in donors)
        if total_weight > 0:
            donors = [(c, w / total_weight * 0.6) for c, w in donors]

        leakage_budget = 0.2 if target_tier == "C" else 0.4

        return DonorPlan(
            donors=donors,
            max_donor_weight=max(w for _, w in donors) if donors else 0.0,
            fingerprint_filter=True,
            leakage_budget=leakage_budget,
        )

    def augment_program(self, target_program: StyleProgram, donor_plan: DonorPlan) -> StyleProgram:
        """Augment a sparse StyleProgram with donor patterns.

        - Unions gesture templates (tagged as donor-sourced)
        - Keeps target fingerprints and anti-patterns (no donor override)
        - Sets donor_plan on the program
        """
        from .style_resolver import StyleResolver

        resolver = StyleResolver()
        target_program.donor_plan = donor_plan

        for donor_composer, weight in donor_plan.donors:
            try:
                donor_prog = resolver.resolve_program(donor_composer)
            except Exception as exc:
                logger.warning("Failed to load donor %s: %s", donor_composer, exc)
                continue

            # Add donor gesture templates (tagged)
            for gesture in donor_prog.gesture_templates:
                tagged = type(gesture)(
                    id=f"donor_{donor_composer}__{gesture.id}",
                    name=f"[donor:{donor_composer}] {gesture.name}",
                    situation=gesture.situation,
                    voice_events=gesture.voice_events,
                    harmonic_context=gesture.harmonic_context,
                    phrase_functions=gesture.phrase_functions,
                    composer_affinities=[donor_composer],
                    source_file=gesture.source_file,
                    source_heading=gesture.source_heading,
                )
                target_program.gesture_templates.append(tagged)

            # Add donor harmonic devices (scaled weight)
            for device in donor_prog.harmonic_devices:
                from .models import HarmonicDevice

                scaled = HarmonicDevice(
                    id=f"donor_{donor_composer}__{device.id}",
                    name=device.name,
                    chord_sequence=device.chord_sequence,
                    voice_leading_hints=device.voice_leading_hints,
                    contexts=device.contexts,
                    frequency_weight=device.frequency_weight * weight,
                    emotional_color=device.emotional_color,
                    source_file=device.source_file,
                )
                target_program.harmonic_devices.append(scaled)

            # Add donor cadence scripts
            for cs in donor_prog.cadence_scripts:
                target_program.cadence_scripts.append(cs)

            logger.info(
                "Augmented with donor %s (weight %.2f): "
                "+%d gestures, +%d devices, +%d cadence scripts",
                donor_composer,
                weight,
                len(donor_prog.gesture_templates),
                len(donor_prog.harmonic_devices),
                len(donor_prog.cadence_scripts),
            )

        return target_program

    def _find_by_influence(self, composer: str) -> List[Tuple[str, float]]:
        """Find donors using influence_axes.json."""
        pack_dir = COMPILED_PACKS / composer
        axes_file = pack_dir / "influence_axes.json"

        if not axes_file.exists():
            return []

        try:
            with open(axes_file) as f:
                axes = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

        donors: List[Tuple[str, float]] = []
        for entry in axes.get("influenced_by", []):
            inf_composer = entry.get("composer", "").lower()
            if inf_composer in _TIER_AB_COMPOSERS:
                donors.append((inf_composer, 0.5))

        return donors
