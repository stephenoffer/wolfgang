"""
ContextRouter — resolves active context per phrase from StyleProgram.

Given a StyleProgram + PhraseControlIR (or PhraseSlot), determines which
gestures, patterns, breathing rules, ornament intents, harmonic devices,
cadence scripts, and fingerprint targets are ACTIVE for this specific
phrase.

This is the routing layer that stops the system from averaging everything
into generic music. A presentation phrase gets different gestures than a
cadential phrase. A development section gets more chromatic devices.
"""

from __future__ import annotations

import logging
from typing import Any

from .corpus_bar_retriever import CorpusBarRetriever
from .enums import CadenceTarget, PhraseFunction
from .models import (
    BreathingRule,
    CadenceScript,
    CounterpointRule,
    ExecutableGesture,
    FigurationTemplate,
    FingerprintRule,
    HarmonicDevice,
    HarmonicTemperature,
    MelodyPrior,
    ModulationScript,
    MovementContract,
    OrnamentIntent,
    PhraseContext,
    PhraseControlIR,
    PhraseSlot,
    SectionContract,
    StyleProgram,
    WorkGraph,
)
from .pattern_retriever import PatternRetriever

logger = logging.getLogger(__name__)


class ContextRouter:
    """Resolves active context per phrase from StyleProgram + phrase state.

    Each subsystem has explicit resolution rules that filter the full
    StyleProgram down to what's relevant for this exact phrase.
    """

    def __init__(
        self,
        pattern_retriever: PatternRetriever,
        corpus_bar_retriever: CorpusBarRetriever | None = None,
    ):
        self.pattern_retriever = pattern_retriever
        self.corpus_bar_retriever = corpus_bar_retriever

    def resolve(
        self,
        program: StyleProgram,
        slot: PhraseSlot,
        section_contract: SectionContract | None = None,
        phrase_index: int = 0,
        total_phrases: int = 1,
        movement_contract: MovementContract | None = None,
        work_graph: WorkGraph | None = None,
        narrative_energy: float = 0.5,
        is_near_climax: bool = False,
        control: PhraseControlIR | None = None,
        ledger: Any | None = None,
    ) -> PhraseContext:
        """Resolve active context for one phrase.

        Returns a PhraseContext containing only the context items
        relevant to this specific phrase.
        """
        ctx = PhraseContext()

        section_role = ""
        if section_contract:
            section_role = section_contract.role

        # 1. Gesture selection
        ctx.active_gestures = self._resolve_gestures(program.gesture_templates, slot, section_role)

        # 2. Pattern retrieval per texture
        ctx.active_patterns = self._resolve_patterns(slot, program)

        # 3. Breathing rules
        ctx.breathing_plan = self._resolve_breathing(
            program.breathing_rules,
            slot,
            phrase_index,
            total_phrases,
            is_near_climax,
            narrative_energy,
        )

        # 4. Ornament intents
        ctx.ornament_intents = self._resolve_ornaments(
            program.ornament_intents, slot, narrative_energy
        )

        # 5. Harmonic devices
        ctx.available_devices = self._resolve_devices(program.harmonic_devices, slot, section_role)

        # 6. Cadence scripts
        ctx.cadence_scripts = self._resolve_cadence_scripts(program.cadence_scripts, slot)

        # 7. Anti-patterns (always all active)
        ctx.active_anti_patterns = list(program.anti_patterns)

        # 8. Fingerprint distribution
        ctx.fingerprint_targets = self._resolve_fingerprints(
            program.dna.fingerprints.items if program.dna.fingerprints else [],
            phrase_index,
            total_phrases,
        )

        # 9. Melody priors (pass 14)
        ctx.active_melody_priors = self._resolve_melody_priors(program.melody_priors, slot)

        # 10. Figuration templates (pass 15)
        ctx.active_figuration_templates = self._resolve_figuration_templates(
            program.figuration_templates, slot, program.dna
        )

        # 11. Modulation scripts (pass 16)
        ctx.active_modulation_scripts = self._resolve_modulation_scripts(
            program.modulation_scripts, slot, section_contract
        )

        # 12. Counterpoint rules (pass 17)
        ctx.active_counterpoint_rules = self._resolve_counterpoint_rules(
            program.counterpoint_rules, program
        )

        # 13. Harmonic temperatures (pass 18)
        ctx.active_harmonic_temperatures = self._resolve_harmonic_temperatures(
            program.harmonic_temperatures, slot, narrative_energy
        )

        # 14. Ledger consultation — filter context based on expectations
        if ledger:
            self._apply_ledger_constraints(ctx, ledger, slot)

        # 15. Validate minimum context package
        self._validate_minimum_context(ctx, slot)

        return ctx

    def _resolve_gestures(
        self, gestures: list[ExecutableGesture], slot: PhraseSlot, section_role: str
    ) -> list[ExecutableGesture]:
        """Filter gestures by phrase function and harmonic context."""
        scored: list[tuple] = []

        for g in gestures:
            score = 0.0

            # Match phrase function
            if g.phrase_functions:
                if slot.function in g.phrase_functions:
                    score += 2.0
            else:
                score += 0.5  # general gestures get baseline score

            # Match harmonic context
            if g.harmonic_context:
                hc = g.harmonic_context.lower()
                if "cadent" in hc and slot.cadence_target != CadenceTarget.NONE.value:
                    score += 1.5
                if "development" in hc and section_role == "development":
                    score += 1.5
                if "lyric" in hc and slot.function == PhraseFunction.CONTRASTING_THEME.value:
                    score += 1.0

            # Match composer
            if g.composer_affinities:
                # Composer-specific gestures rank higher
                score += 1.0

            if score > 0:
                scored.append((score, g))

        # Sort by score, take top 5
        scored.sort(key=lambda x: x[0], reverse=True)
        return [g for _, g in scored[:5]]

    def _resolve_patterns(self, slot: PhraseSlot, program: StyleProgram) -> dict[str, list[Any]]:
        """Retrieve LH patterns for each texture in the phrase's texture plan."""
        result: dict[str, list[Any]] = {}
        seen_textures: set = set()

        for bar_plan in slot.texture_plan:
            texture = bar_plan.lh_texture
            if texture in seen_textures:
                continue
            seen_textures.add(texture)

            density_target = bar_plan.lh_density_target or 8
            density_range = (max(2, density_target - 4), density_target + 8)

            # Determine genre filter from style
            genre = None
            tier = program.dna.tier if program.dna else "D"
            if tier in ("A", "B"):
                genre = None  # Tier A/B have their own patterns, no filter needed

            patterns = self.pattern_retriever.retrieve(
                texture=texture,
                density_range=density_range,
                genre_filter=genre,
                n=8,
            )
            if patterns:
                result[texture] = patterns

        return result

    def _resolve_breathing(
        self,
        rules: list[BreathingRule],
        slot: PhraseSlot,
        phrase_index: int,
        total_phrases: int,
        is_near_climax: bool,
        energy: float,
    ) -> list[BreathingRule]:
        """Match breathing rules by phrase position."""
        active: list[BreathingRule] = []

        for rule in rules:
            rule.placement.lower() if rule.placement else ""
            rtype = rule.type.lower() if rule.type else ""

            # Section opening
            if phrase_index == 0 and ("gathering" in rtype or "structural" in rtype):
                active.append(rule)
                continue

            # Section closing
            if phrase_index == total_phrases - 1 and "structural" in rtype:
                active.append(rule)
                continue

            # Near climax
            if is_near_climax and "anticip" in rtype:
                active.append(rule)
                continue

            # After climax
            if energy < 0.3 and ("aftermath" in rtype or "contemplat" in rtype):
                active.append(rule)
                continue

            # Slow tempo
            if slot.tempo_bpm < 80 and "contemplat" in rtype:
                active.append(rule)
                continue

        return active[:3]  # max 3 breathing rules per phrase

    def _resolve_ornaments(
        self, intents: list[OrnamentIntent], slot: PhraseSlot, energy: float
    ) -> list[OrnamentIntent]:
        """Map phrase function to ornament contexts."""
        fn = slot.function
        context_map = {
            PhraseFunction.PRESENTATION.value: "phrase_entry",
            PhraseFunction.CADENTIAL.value: "cadential_arrival",
            PhraseFunction.CONTRASTING_THEME.value: "between_phrases",
            PhraseFunction.RETURN.value: "theme_return",
            PhraseFunction.RETURN_VARIED.value: "theme_return",
            PhraseFunction.CLOSING.value: "dying_away",
            PhraseFunction.CODA.value: "dying_away",
        }
        target_context = context_map.get(fn, "")

        # Also consider energy-based contexts
        energy_contexts = set()
        if energy > 0.8:
            energy_contexts.add("approaching_climax")
            energy_contexts.add("emotional_peak")
        if energy < 0.2:
            energy_contexts.add("dying_away")
            energy_contexts.add("silence_after_intensity")

        active: list[OrnamentIntent] = []
        for intent in intents:
            ctx = intent.context.lower()
            if target_context and target_context in ctx:
                active.append(intent)
            elif any(ec in ctx for ec in energy_contexts):
                active.append(intent)

        return active[:4]  # max 4 ornament intents per phrase

    def _resolve_devices(
        self, devices: list[HarmonicDevice], slot: PhraseSlot, section_role: str
    ) -> list[HarmonicDevice]:
        """Filter harmonic devices by section role and phrase function."""
        active: list[HarmonicDevice] = []

        for device in devices:
            # Development sections get all devices
            if section_role == "development":
                active.append(device)
                continue

            # Check device contexts
            if device.contexts:
                for ctx in device.contexts:
                    ctx_lower = ctx.lower()
                    if (
                        "pre-cadent" in ctx_lower
                        and slot.cadence_target != CadenceTarget.NONE.value
                    ):
                        active.append(device)
                        break
                    if (
                        "transition" in ctx_lower
                        and slot.function == PhraseFunction.TRANSITION.value
                    ):
                        active.append(device)
                        break
                    if "development" in ctx_lower and section_role == "development":
                        active.append(device)
                        break
            else:
                # Devices without specific contexts are always available
                if device.frequency_weight >= 0.2:
                    active.append(device)

        return active

    def _resolve_cadence_scripts(
        self, scripts: list[CadenceScript], slot: PhraseSlot
    ) -> list[CadenceScript]:
        """Find cadence scripts matching the phrase's cadence target."""
        if slot.cadence_target == CadenceTarget.NONE.value:
            return []

        matching: list[CadenceScript] = []
        for script in scripts:
            if script.type and slot.cadence_target.lower() in script.type.lower():
                matching.append(script)

        return matching

    def _resolve_fingerprints(
        self, fingerprints: list[FingerprintRule], phrase_index: int, total_phrases: int
    ) -> list[FingerprintRule]:
        """Distribute fingerprint obligations across phrases.

        Each phrase gets 1-2 fingerprint targets. The first phrase gets
        the most distinctive fingerprint. Round-robin for the rest.
        """
        if not fingerprints:
            return []

        # First phrase gets the first fingerprint
        if phrase_index == 0:
            return fingerprints[:1]

        # Last phrase gets a different one
        if phrase_index == total_phrases - 1 and len(fingerprints) > 1:
            return fingerprints[1:2]

        # Middle phrases round-robin through remaining
        if len(fingerprints) > 2:
            idx = (phrase_index - 1) % (len(fingerprints) - 2) + 2
            if idx < len(fingerprints):
                return [fingerprints[idx]]

        return []

    # ─── Pass 13-18 Resolution Methods ───────────────────────────────────

    def _resolve_melody_priors(
        self, priors: list[MelodyPrior], slot: PhraseSlot
    ) -> list[MelodyPrior]:
        """Filter melody priors by phrase function and conditions."""
        if not priors:
            return []

        active: list[MelodyPrior] = []
        fn = slot.function

        for prior in priors:
            # Phrase structure priors always relevant
            if prior.category in ("phrase_structure", "contour"):
                active.append(prior)
                continue

            # Peak timing relevant for longer phrases
            if prior.category == "peak_timing" and slot.bar_count >= 4:
                active.append(prior)
                continue

            # Interval language always relevant
            if prior.category == "interval_language":
                active.append(prior)
                continue

            # Breath span relevant for all phrases
            if prior.category == "breath_span":
                active.append(prior)
                continue

            # Check conditions
            conditions = prior.conditions
            if conditions.get("best_for"):
                best_for = conditions["best_for"].lower()
                if fn in best_for or "all" in best_for:
                    active.append(prior)

        return active

    def _resolve_figuration_templates(
        self, templates: list[FigurationTemplate], slot: PhraseSlot, style_dna: Any
    ) -> list[FigurationTemplate]:
        """Filter figuration templates by tempo, style period, and texture needs."""
        if not templates:
            return []

        active: list[FigurationTemplate] = []
        for tmpl in templates:
            # Check tempo range
            if tmpl.tempo_range:
                lo, hi = tmpl.tempo_range
                if not (lo - 20 <= slot.tempo_bpm <= hi + 20):
                    continue

            active.append(tmpl)

        return active[:8]  # max 8 figuration templates per phrase

    def _resolve_modulation_scripts(
        self,
        scripts: list[ModulationScript],
        slot: PhraseSlot,
        section: SectionContract | None = None,
    ) -> list[ModulationScript]:
        """Only include modulation scripts at key change boundaries."""
        if not scripts:
            return []

        # Only relevant for transition phrases or at section boundaries
        fn = slot.function
        is_transition = fn in (
            PhraseFunction.TRANSITION.value,
            PhraseFunction.RETRANSITION.value,
            PhraseFunction.SEQUENCE.value,
        )

        if not is_transition:
            return []

        return scripts  # all modulation types available during transitions

    def _resolve_counterpoint_rules(
        self, rules: list[CounterpointRule], program: StyleProgram
    ) -> list[CounterpointRule]:
        """Filter counterpoint rules by style period permissions."""
        if not rules:
            return []

        active: list[CounterpointRule] = []
        for rule in rules:
            # If no style permissions specified, include by default
            if not rule.style_permissions:
                active.append(rule)
                continue

            # Check if common_practice is permitted (default style)
            if rule.style_permissions.get("common_practice", True):
                active.append(rule)

        return active

    def _resolve_harmonic_temperatures(
        self, temps: list[HarmonicTemperature], slot: PhraseSlot, narrative_energy: float
    ) -> list[HarmonicTemperature]:
        """Filter harmonic temperature entries by narrative position."""
        if not temps:
            return []

        active: list[HarmonicTemperature] = []

        for temp in temps:
            # Tension curve entries: always relevant
            if temp.category == "tension_curve":
                active.append(temp)
                continue

            # Harmonic rhythm: always relevant
            if temp.category == "harmonic_rhythm":
                active.append(temp)
                continue

            # Cadence punctuation: relevant for cadential phrases
            if temp.category == "cadence_punctuation":
                if slot.cadence_target != CadenceTarget.NONE.value:
                    active.append(temp)
                continue

            # Prolongation: relevant for specific section types
            if temp.category == "prolongation":
                active.append(temp)
                continue

            # Emotional-to-harmonic: match by energy level
            if temp.category == "emotional_to_harmonic":
                if temp.tension_level is not None:
                    if abs(temp.tension_level - narrative_energy) < 0.3:
                        active.append(temp)
                else:
                    active.append(temp)

        return active

    def _apply_ledger_constraints(self, ctx: PhraseContext, ledger: Any, slot: PhraseSlot) -> None:
        """Filter context based on ledger state (expectations, cooldowns, prohibitions)."""
        try:
            # Check active cooldowns — remove recently-used textures
            cooldowns = ledger.get_active_cooldowns(slot.phrase_id)
            if cooldowns:
                cooldown_refs = {c.object_ref for c in cooldowns}
                # Remove figuration templates matching cooled-down textures
                ctx.active_figuration_templates = [
                    ft
                    for ft in ctx.active_figuration_templates
                    if ft.pattern_keyword not in cooldown_refs
                ]

            # Check active prohibitions — remove forbidden devices
            prohibitions = ledger.get_active_prohibitions(slot.phrase_id)
            if prohibitions:
                prohibited_refs = {p.object_ref for p in prohibitions}
                ctx.available_devices = [
                    d for d in ctx.available_devices if d.id not in prohibited_refs
                ]
        except (AttributeError, TypeError):
            # Ledger may not have all methods — graceful degradation
            pass

    def _validate_minimum_context(self, ctx: PhraseContext, slot: PhraseSlot) -> None:
        """Ensure every phrase has at least the minimum context package.

        Logs warnings but does not block — informational enforcement.
        """
        issues = []

        if not ctx.fingerprint_targets:
            issues.append("no_fingerprint_target")

        if not ctx.active_gestures:
            issues.append("no_gesture_template")

        if not ctx.active_anti_patterns:
            issues.append("no_anti_pattern_checks")

        if issues:
            logger.debug("Minimum context gaps for %s: %s", slot.phrase_id, ", ".join(issues))
