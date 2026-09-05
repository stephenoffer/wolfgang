"""
StyleResolver — blend/merge StyleDNA objects from compiled ComposerPacks.

Handles single-composer loading and multi-composer axis-owned blending.
Replaces: genre_pack.py, composer_support.py
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple

from .models import (
    AntiPatternRule,
    BreathingRule,
    CadenceRule,
    CadenceScript,
    ChromaticTechnique,
    CounterpointRule,
    DensityTarget,
    ExecutableGesture,
    FigurationTemplate,
    FingerprintRule,
    FingerprintRuleSet,
    FormTemplate,
    HarmonicDevice,
    HarmonicTemperature,
    InstrumentRole,
    MelodyPrior,
    ModulationScript,
    OrnamentIntent,
    PeriodOverlay,
    PromptSemantic,
    StyleDNA,
    StyleProgram,
)

_BASE = Path(__file__).parent.parent
COMPILED_PACKS = _BASE / "compiled_packs"
CONTEXT_OVERLAYS = _BASE / "context_overlays"
PATTERN_LIBRARY = _BASE / "pattern_library"
TEXTURE_TEMPLATES = _BASE / "texture_templates"
REFERENCE_INDEX = _BASE / "reference_index"


#: Note names as the profiles write a register, e.g. "C1-E3", "G4-C6".
_REGISTER_RE = re.compile(
    r"\b([A-G][#b]?)(-?\d)\s*[-–—]\s*([A-G][#b]?)(-?\d)\b", re.IGNORECASE
)


def _overlay_is_stale(overlay_data: dict, pack_mtime: float | None) -> bool:
    """Is this overlay's evidence older than the artefact it would override?

    Overlays are machine-written from corpus feedback and carry `last_updated`.
    When the pack has been recompiled since — because the corpus was rebuilt,
    which happened for every flagship composer today — the overlay is describing
    a corpus that no longer exists. Without a date it is treated as current,
    because a missing date is not evidence of age.
    """
    if pack_mtime is None:
        return False
    stamp = overlay_data.get("last_updated")
    if not isinstance(stamp, str):
        return False
    try:
        written = datetime.strptime(stamp[:10], "%Y-%m-%d").timestamp()
    except ValueError:
        return False
    # A day's grace: a pack and an overlay written the same day are the same
    # generation, and file mtimes are not a reliable ordering within one.
    return pack_mtime > written + 86400


def _parse_register(text: str) -> Tuple[int, int]:
    """A profile's written register as a MIDI pair.

    The orchestration tables state ranges as "C1-E3" or "G4-C6" beside each
    voice. Without this the role would carry the dataclass default (60, 84) —
    a middle-of-the-keyboard range for a double bass as readily as for a flute,
    which is worse than no range at all.
    """
    match = _REGISTER_RE.search(text or "")
    if not match:
        return (60, 84)
    from .pitch import pitch_to_midi

    try:
        low = pitch_to_midi(f"{match.group(1)}{match.group(2)}")
        high = pitch_to_midi(f"{match.group(3)}{match.group(4)}")
    except (ValueError, KeyError, TypeError):
        return (60, 84)
    if low is None or high is None:
        return (60, 84)
    return (min(low, high), max(low, high))


class StyleResolver:
    """Resolves style specifications into usable StyleDNA objects."""

    def resolve_single(
        self, composer: str, era: str = "", period: str | None = None
    ) -> StyleDNA:
        """Load StyleDNA for a single composer."""
        pack = self._load_pack(composer)
        # A STYLE's tier is its members', computed here rather than read off the
        # manifest. The style packs' manifests say "C" because the tier is
        # classified from `reference_index/<id>/` and there is no
        # `reference_index/style__classical/` — a style's corpus is the union of
        # its members'. Tier C/D is what triggers `DonorStrategy` in
        # `compile_style`, so "in the classical style" — mozart, haydn and
        # beethoven, ~27,800 bars — was augmented with a donor as though it were
        # a sparse corpus.
        #
        # Computed at load time because nothing can regenerate a style manifest:
        # `build_style_profiles` writes only the corpus profile, and running the
        # COMPILER on a style destroys the pack (it has no profile directory to
        # build from). See the guard in `compile_style`.
        tier = pack.get("manifest", {}).get("support_tier", "D")
        style_tier = self._style_tier(composer)
        dna = StyleDNA(
            composer_id=composer,
            tier=style_tier or tier,
        )

        # Fingerprints
        fp_data = pack.get("fingerprint_rules", {})
        dna.fingerprints = FingerprintRuleSet(
            required_count=fp_data.get("required_count", 3),
            items=[
                FingerprintRule(
                    id=fp.get("id", ""),
                    name=fp.get("name", ""),
                    description=fp.get("description", ""),
                    texture_affinities=fp.get("texture_affinities", []),
                    frequency=fp.get("frequency", "per_section"),
                )
                for fp in fp_data.get("items", [])
            ],
        )

        # Statistics
        stats = pack.get("scoped_statistics", {})
        dna.lh_distribution = stats.get("lh_distribution", {})
        dna.rh_distribution = stats.get("rh_distribution", {})
        dna.transition_matrix = stats.get("transition_matrix", {})

        # If no compiled stats, try loading from texture templates directly
        if not dna.lh_distribution:
            dna.lh_distribution, dna.rh_distribution = self._load_texture_stats(composer)

        # Density targets
        dna.density_targets = {
            "slow": DensityTarget(rh_mean=6.0, lh_mean=4.0),
            "moderate": DensityTarget(rh_mean=8.0, lh_mean=6.0),
            "fast": DensityTarget(rh_mean=12.0, lh_mean=8.0),
        }

        # Harmonic rules
        harmonic = pack.get("harmonic_rules", {})
        dna.cadence_vocabulary = [
            CadenceRule(type=c.get("type", ""), frequency_weight=c.get("frequency_weight", 0.5))
            for c in harmonic.get("cadence_vocabulary", [])
        ]
        dna.chromatic_techniques = [
            ChromaticTechnique(
                name=c.get("name", ""), frequency_weight=c.get("frequency_weight", 0.3)
            )
            for c in harmonic.get("chromatic_techniques", [])
        ]

        # Formal grammar
        formal = pack.get("formal_graphs", {})
        for form_name, form_data in formal.get("forms", {}).items():
            dna.form_templates[form_name] = FormTemplate(
                sections=form_data.get("sections", []),
                key_scheme=form_data.get("key_scheme", {}),
            )

        # Period overlay
        if period:
            periods = pack.get("period_overlays", {})
            for p in periods.get("periods", []):
                if p.get("id") == period:
                    dna.active_period = PeriodOverlay(
                        id=p["id"],
                        stat_modifiers=p.get("stat_modifiers", {}),
                    )
                    break

        return dna

    def resolve_blend(self, composers: dict[str, float], era: str = "") -> StyleDNA:
        """Resolve a blended StyleDNA from multiple composers.

        Args:
            composers: {"Beethoven": 0.6, "Rachmaninoff": 0.4}
        """
        if len(composers) == 1:
            composer = list(composers.keys())[0]
            return self.resolve_single(composer, era)

        # Load individual DNAs
        dnas = {}
        for composer, weight in composers.items():
            dnas[composer] = (self.resolve_single(composer, era), weight)

        # Create blended DNA
        blend = StyleDNA(
            composer_id="blend:" + "+".join(composers.keys()),
            tier=max((d.tier for d, _ in dnas.values()), default="D"),
            blend_weights=composers,
        )

        # Step 1: Axis ownership
        blend.axis_ownership = self._resolve_axis_ownership(dnas)

        # Step 2: Merge fingerprints
        blend.fingerprints = self._merge_fingerprints(dnas)

        # Step 3: Merge statistics
        blend.lh_distribution = self._merge_distributions(
            {c: (d.lh_distribution, w) for c, (d, w) in dnas.items()}
        )
        blend.rh_distribution = self._merge_distributions(
            {c: (d.rh_distribution, w) for c, (d, w) in dnas.items()}
        )

        # Step 4: Merge density targets
        blend.density_targets = self._merge_density_targets(dnas)

        # Step 5: Merge cadence vocabulary (union)
        all_cadences = []
        for (d, w) in dnas.values():
            for c in d.cadence_vocabulary:
                c.frequency_weight *= w
                all_cadences.append(c)
        blend.cadence_vocabulary = all_cadences

        # Step 6: Merge chromatic techniques (union)
        all_chromatics = []
        for (d, w) in dnas.values():
            for c in d.chromatic_techniques:
                c.frequency_weight *= w
                all_chromatics.append(c)
        blend.chromatic_techniques = all_chromatics

        # Step 7: Formal grammar from dominant composer
        dominant = max(composers, key=composers.get)
        dominant_dna, _ = dnas[dominant]
        blend.form_templates = dominant_dna.form_templates

        return blend

    # ─── Axis Ownership ───────────────────────────────────────────────────

    def _resolve_axis_ownership(self, dnas: dict[str, tuple[StyleDNA, float]]) -> dict[str, str]:
        """Determine which composer owns each style axis."""
        axes = [
            "texture_density",
            "harmonic_chromaticism",
            "phrase_length",
            "register_range",
            "dynamic_contrast",
            "formal_rigidity",
            "cadence_variety",
            "motif_development",
        ]
        ownership = {}

        for axis in axes:
            best_composer = None
            best_distinctiveness = -1

            for composer, (dna, weight) in dnas.items():
                dist = self._compute_distinctiveness(dna, axis)
                # Weight by blend proportion
                effective = dist * weight
                if effective > best_distinctiveness:
                    best_distinctiveness = effective
                    best_composer = composer

            ownership[axis] = best_composer or list(dnas.keys())[0]

        return ownership

    def _compute_distinctiveness(self, dna: StyleDNA, axis: str) -> float:
        """How distinctive is this composer on this axis? 0-1."""
        # Heuristic based on available data
        if axis == "texture_density":
            return len(dna.lh_distribution) * 0.1
        if axis == "harmonic_chromaticism":
            return len(dna.chromatic_techniques) * 0.15
        if axis == "formal_rigidity":
            return len(dna.form_templates) * 0.2
        if axis == "cadence_variety":
            return len(dna.cadence_vocabulary) * 0.1
        return 0.5

    # ─── Merge Functions ──────────────────────────────────────────────────

    def _merge_fingerprints(self, dnas: dict[str, tuple[StyleDNA, float]]) -> FingerprintRuleSet:
        """Merge fingerprints proportional to weight."""
        merged = []
        for _composer, (dna, weight) in sorted(dnas.items(), key=lambda x: -x[1][1]):
            n_to_take = max(1, round(len(dna.fingerprints.items) * weight))
            for fp in dna.fingerprints.items[:n_to_take]:
                merged.append(fp)

        return FingerprintRuleSet(
            required_count=max(2, len(merged) // 2),
            items=merged,
        )

    def _merge_distributions(
        self, distributions: dict[str, tuple[dict[str, float], float]]
    ) -> dict[str, float]:
        """Merge texture distributions using weighted average."""
        merged: dict[str, float] = {}
        for (dist, weight) in distributions.values():
            for tex, pct in dist.items():
                merged[tex] = merged.get(tex, 0) + pct * weight

        # Normalize
        total = sum(merged.values())
        if total > 0:
            merged = {k: v / total for k, v in merged.items()}
        return merged

    def _merge_density_targets(
        self, dnas: dict[str, tuple[StyleDNA, float]]
    ) -> dict[str, DensityTarget]:
        """Merge density targets using weighted interpolation."""
        result = {}
        for tempo_class in ["slow", "moderate", "fast"]:
            rh_sum, lh_sum, weight_sum = 0.0, 0.0, 0.0
            for (dna, weight) in dnas.values():
                target = dna.density_targets.get(tempo_class)
                if target:
                    rh_sum += target.rh_mean * weight
                    lh_sum += target.lh_mean * weight
                    weight_sum += weight
            if weight_sum > 0:
                result[tempo_class] = DensityTarget(
                    rh_mean=rh_sum / weight_sum,
                    lh_mean=lh_sum / weight_sum,
                )
        return result

    # ─── Loading ──────────────────────────────────────────────────────────

    def _style_tier(self, reference: str) -> str | None:
        """The tier a style earns from its members' corpora, or None if not a style."""
        from .style_registry import is_style_id, normalize_style, style_members, style_name

        canon = style_name(reference) if is_style_id(reference) else normalize_style(reference)
        if not canon:
            return None
        members = style_members(canon)
        if not members:
            return None
        best = "D"
        for member in members:
            member_tier = (
                self._load_pack(member).get("manifest", {}).get("support_tier", "D")
            )
            if member_tier < best:  # "A" < "B" < "C" < "D"
                best = member_tier
        return best

    def _load_pack(self, composer: str) -> dict:
        """Load a compiled ComposerPack."""
        from .style_registry import pack_dir_name

        pack_dir = COMPILED_PACKS / pack_dir_name(composer)
        pack = {}
        pack_built: dict[str, float] = {}
        for filename in [
            "manifest.json",
            "fingerprint_rules.json",
            "scoped_statistics.json",
            "formal_graphs.json",
            "harmonic_rules.json",
            "orchestration_roles.json",
            "period_overlays.json",
            "influence_axes.json",
            "phrase_prototypes.json",
            "review_rubric.json",
            # Pass 8-12 outputs
            "gesture_templates.json",
            "anti_pattern_rules.json",
            "harmonic_devices.json",
            "cadence_scripts.json",
            "breathing_rules.json",
            "ornament_intents.json",
            # Pass 13-18 outputs
            "prompt_semantics.json",
            "melody_priors.json",
            "figuration_templates.json",
            "modulation_scripts.json",
            "counterpoint_rules.json",
            "harmonic_temperature.json",
        ]:
            filepath = pack_dir / filename
            if filepath.exists():
                with open(filepath) as f:
                    key = filename.replace(".json", "")
                    pack[key] = json.load(f)
                pack_built[key] = filepath.stat().st_mtime

        # Load overlay files (per-composer learned overrides)
        overlay_dir = CONTEXT_OVERLAYS / composer
        if overlay_dir.is_dir():
            for overlay_path in sorted(overlay_dir.glob("*.json")):
                with open(overlay_path) as f:
                    overlay_data = json.load(f)
                key = overlay_path.stem
                if key in pack:
                    if isinstance(pack[key], list) and isinstance(overlay_data, list):
                        # Union: extend existing list
                        pack[key].extend(overlay_data)
                    elif isinstance(pack[key], dict) and isinstance(overlay_data, dict):
                        # AN OVERLAY MUST NOT OVERRIDE A NEWER MEASUREMENT.
                        #
                        # `update()` replaced the pack's keys wholesale, so
                        # Mozart's `lh_distribution` came from a four-month-old
                        # overlay (evidence dated 2026-04-19) rather than from
                        # the pack rebuilt from his corrected corpus the same
                        # day. The planned distribution was `pedal_point` 0.090
                        # against his real 0.034 and `block_chord_offbeat` 0.045
                        # against his real 0.104 — and the generated output
                        # reproduced the overlay's numbers faithfully, which is
                        # what made it look like a generator defect.
                        #
                        # An overlay is EVIDENCE, and evidence has a date. Where
                        # the compiled artefact is newer than the evidence, the
                        # measurement wins and the overlay may still contribute
                        # keys the measurement does not carry.
                        if _overlay_is_stale(overlay_data, pack_built.get(key)):
                            for field, value in overlay_data.items():
                                pack[key].setdefault(field, value)
                        else:
                            pack[key].update(overlay_data)
                    else:
                        pack[key] = overlay_data
                else:
                    pack[key] = overlay_data

        return pack

    # ─── StyleProgram Resolution ────────────────────────────────────────

    def resolve_program(
        self, composer: str, era: str = "", period: str | None = None
    ) -> StyleProgram:
        """Resolve full StyleProgram from compiled packs.

        Loads StyleDNA via existing resolve_single(), then loads pass 8-12
        outputs for executable context.
        """
        dna = self.resolve_single(composer, era, period)
        pack = self._load_pack(composer)

        program = StyleProgram(dna=dna)

        # Load pass 8 outputs: gesture templates
        for gt in pack.get("gesture_templates", []):
            program.gesture_templates.append(
                ExecutableGesture(
                    id=gt.get("id", ""),
                    name=gt.get("name", ""),
                    situation=gt.get("situation", ""),
                    voice_events=gt.get("voice_events", {}),
                    harmonic_context=gt.get("harmonic_context", ""),
                    phrase_functions=gt.get("phrase_functions", []),
                    composer_affinities=gt.get("composer_affinities", []),
                    source_file=gt.get("source_file", ""),
                    source_heading=gt.get("source_heading", ""),
                )
            )

        # Load pass 9 outputs: anti-pattern rules
        for ap in pack.get("anti_pattern_rules", []):
            program.anti_patterns.append(
                AntiPatternRule(
                    id=ap.get("id", ""),
                    name=ap.get("name", ""),
                    description=ap.get("description", ""),
                    detector=ap.get("detector", ""),
                    severity=ap.get("severity", "warning"),
                    params=ap.get("params", {}),
                    style_scope=ap.get("style_scope", ""),
                    source_file=ap.get("source_file", ""),
                )
            )

        # Load pass 10 outputs: harmonic devices + cadence scripts
        for hd in pack.get("harmonic_devices", []):
            program.harmonic_devices.append(
                HarmonicDevice(
                    id=hd.get("id", ""),
                    name=hd.get("name", ""),
                    chord_sequence=hd.get("chord_sequence", []),
                    voice_leading_hints=hd.get("voice_leading_hints", []),
                    contexts=hd.get("contexts", []),
                    frequency_weight=hd.get("frequency_weight", 0.3),
                    emotional_color=hd.get("emotional_color", ""),
                    source_file=hd.get("source_file", ""),
                )
            )
        for cs in pack.get("cadence_scripts", []):
            program.cadence_scripts.append(
                CadenceScript(
                    id=cs.get("id", ""),
                    type=cs.get("type", ""),
                    approach_chords=cs.get("approach_chords", []),
                    soprano_line=cs.get("soprano_line", []),
                    bass_motion=cs.get("bass_motion", ""),
                    inner_voice_rules=cs.get("inner_voice_rules", []),
                    strength=cs.get("strength", 3),
                    typical_texture=cs.get("typical_texture", ""),
                    preparation_bars=cs.get("preparation_bars", 2),
                )
            )

        # Load pass 11 outputs: breathing rules
        for br in pack.get("breathing_rules", []):
            program.breathing_rules.append(
                BreathingRule(
                    type=br.get("type", ""),
                    placement=br.get("placement", ""),
                    duration_beats_min=br.get("duration_beats_min", 1.0),
                    duration_beats_max=br.get("duration_beats_max", 4.0),
                    effect=br.get("effect", ""),
                    technique=br.get("technique", ""),
                    source_file=br.get("source_file", ""),
                )
            )

        # Load pass 12 outputs: ornament intents
        for oi in pack.get("ornament_intents", []):
            program.ornament_intents.append(
                OrnamentIntent(
                    context=oi.get("context", ""),
                    what_moment_needs=oi.get("what_moment_needs", ""),
                    common_choice=oi.get("common_choice", ""),
                    why=oi.get("why", ""),
                    density_arc=oi.get("density_arc", ""),
                )
            )

        # Load orchestration roles.
        #
        # `StyleProgram.orchestration_roles` is READ by `orchestrate_section`,
        # which passes it to `plan_orchestration` as `style_roles` — and nothing
        # ever assigned it, so every orchestral piece was scored generically no
        # matter whose style it was in. The field defaulted to `{}`, the getter
        # returned it, and the planner's own fallback took over silently.
        #
        # The pass that produces this data was a stub until recently (it returned
        # `{"instruments": {}}` for all 55 composers), so the empty drawer had an
        # empty drawer behind it and fixing one alone changed nothing.
        roles_pack = pack.get("orchestration_roles", {})
        # BOTH buckets. A table with a hand or register column files its rows as
        # `instruments`; one without files them as `textures`. Beethoven's
        # orchestration tables have no hand column, so reading only
        # `instruments` gave him zero roles while Chopin got twelve.
        entries = dict(roles_pack.get("instruments", {}))
        for texture in roles_pack.get("textures", []) or []:
            if isinstance(texture, dict) and texture.get("name"):
                entries.setdefault(texture["name"].lower().replace(" ", "_"), texture)
        for key, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            # The field lives on StyleDNA, which the program WRAPS —
            # `program.orchestration_roles` does not exist, and the consumer's
            # `getattr(program, "orchestration_roles", None)` hid that
            # completely: it read a field off the wrong object and got None
            # forever, with no error anywhere.
            program.dna.orchestration_roles[key] = InstrumentRole(
                name=entry.get("name", key),
                role=entry.get("function", entry.get("role", "")),
                characteristic_usage=entry.get("genre", entry.get("section", "")),
                # Any field may hold it: the tables put a range under
                # `Register Range`, `Span`, or inside the function prose.
                register_range=_parse_register(
                    " ".join(str(v) for v in entry.values() if isinstance(v, str))
                ),
                doubling_partners=[],
                solo_frequency="occasional",
            )

        # Load review rubric
        program.review_rubric = pack.get("review_rubric", {}).get("checks", [])

        # Load pass 13 outputs: prompt semantics
        for ps in pack.get("prompt_semantics", []):
            program.prompt_semantics.append(
                PromptSemantic(
                    word=ps.get("word", ""),
                    synonyms=ps.get("synonyms", []),
                    tempo_range=tuple(ps["tempo_range"]) if ps.get("tempo_range") else None,
                    mode_scale=ps.get("mode_scale", []),
                    dynamics=ps.get("dynamics", ""),
                    texture=ps.get("texture", ""),
                    register=ps.get("register", ""),
                    articulation=ps.get("articulation", ""),
                    rhythm_type=ps.get("rhythm_type", ""),
                    harmonic_language=ps.get("harmonic_language", ""),
                    interval_preferences=ps.get("interval_preferences", []),
                    density_range=tuple(ps["density_range"]) if ps.get("density_range") else None,
                    orchestration_color=ps.get("orchestration_color", ""),
                    contour=ps.get("contour", ""),
                    grounding=ps.get("grounding", "interpretive"),
                    source_files=ps.get("source_files", []),
                )
            )

        # Load pass 14 outputs: melody priors
        for mp in pack.get("melody_priors", []):
            program.melody_priors.append(
                MelodyPrior(
                    id=mp.get("id", ""),
                    category=mp.get("category", ""),
                    description=mp.get("description", ""),
                    parameters=mp.get("parameters", {}),
                    conditions=mp.get("conditions", {}),
                    grounding=mp.get("grounding", "interpretive"),
                    source_file=mp.get("source_file", ""),
                )
            )

        # Load pass 15 outputs: figuration templates
        for ft in pack.get("figuration_templates", []):
            program.figuration_templates.append(
                FigurationTemplate(
                    id=ft.get("id", ""),
                    name=ft.get("name", ""),
                    pattern_keyword=ft.get("pattern_keyword", ""),
                    period_style=ft.get("period_style", []),
                    tempo_range=tuple(ft["tempo_range"]) if ft.get("tempo_range") else None,
                    character=ft.get("character", ""),
                    when_to_use=ft.get("when_to_use", []),
                    variation_operators=ft.get("variation_operators", []),
                    density_suggestion=tuple(ft["density_suggestion"])
                    if ft.get("density_suggestion")
                    else None,
                    register_suggestion=ft.get("register_suggestion", ""),
                    grounding=ft.get("grounding", "interpretive"),
                    source_file=ft.get("source_file", ""),
                )
            )

        # Load pass 16 outputs: modulation scripts
        for ms in pack.get("modulation_scripts", []):
            program.modulation_scripts.append(
                ModulationScript(
                    id=ms.get("id", ""),
                    type=ms.get("type", ""),
                    from_key_class=ms.get("from_key_class", ""),
                    to_key_relationship=ms.get("to_key_relationship", ""),
                    mechanism=ms.get("mechanism", ""),
                    smoothness=ms.get("smoothness", ""),
                    best_for=ms.get("best_for", []),
                    chord_sequence=ms.get("chord_sequence", []),
                    voice_leading_hints=ms.get("voice_leading_hints", []),
                    pivot_chord_in_old=ms.get("pivot_chord_in_old", ""),
                    pivot_chord_in_new=ms.get("pivot_chord_in_new", ""),
                    grounding=ms.get("grounding", "interpretive"),
                    source_file=ms.get("source_file", ""),
                )
            )

        # Load pass 17 outputs: counterpoint rules
        for cr in pack.get("counterpoint_rules", []):
            program.counterpoint_rules.append(
                CounterpointRule(
                    id=cr.get("id", ""),
                    category=cr.get("category", ""),
                    description=cr.get("description", ""),
                    severity=cr.get("severity", "warning"),
                    style_permissions=cr.get("style_permissions", {}),
                    repair_recipe=cr.get("repair_recipe", ""),
                    detection_heuristic=cr.get("detection_heuristic", {}),
                    grounding=cr.get("grounding", "hard_corroborated"),
                    source_file=cr.get("source_file", ""),
                )
            )

        # Load pass 18 outputs: harmonic temperature
        for ht in pack.get("harmonic_temperature", []):
            program.harmonic_temperatures.append(
                HarmonicTemperature(
                    id=ht.get("id", ""),
                    category=ht.get("category", ""),
                    emotional_context=ht.get("emotional_context", ""),
                    tonal_move=ht.get("tonal_move", ""),
                    narrative_meaning=ht.get("narrative_meaning", ""),
                    tension_level=ht.get("tension_level"),
                    harmonic_parameters=ht.get("harmonic_parameters", {}),
                    when_to_use=ht.get("when_to_use", []),
                    grounding=ht.get("grounding", "interpretive"),
                    source_file=ht.get("source_file", ""),
                )
            )

        return program

    def resolve_blend_program(
        self, composers_weights: dict[str, float], era: str = ""
    ) -> StyleProgram:
        """Resolve blended StyleProgram from multiple composers.

        Gesture templates and anti-patterns are unioned.
        Harmonic devices are unioned with weight scaling.
        """
        dna = self.resolve_blend(composers_weights, era)
        program = StyleProgram(dna=dna)

        for composer, weight in composers_weights.items():
            individual = self.resolve_program(composer, era)
            program.gesture_templates.extend(individual.gesture_templates)
            program.anti_patterns.extend(individual.anti_patterns)
            program.breathing_rules.extend(individual.breathing_rules)
            program.ornament_intents.extend(individual.ornament_intents)

            for device in individual.harmonic_devices:
                scaled = HarmonicDevice(
                    id=device.id,
                    name=device.name,
                    chord_sequence=device.chord_sequence,
                    voice_leading_hints=device.voice_leading_hints,
                    contexts=device.contexts,
                    frequency_weight=device.frequency_weight * weight,
                    emotional_color=device.emotional_color,
                    source_file=device.source_file,
                )
                program.harmonic_devices.append(scaled)

            program.cadence_scripts.extend(individual.cadence_scripts)

            # Pass 13-18 assets: union all
            program.prompt_semantics.extend(individual.prompt_semantics)
            program.melody_priors.extend(individual.melody_priors)
            program.figuration_templates.extend(individual.figuration_templates)
            program.modulation_scripts.extend(individual.modulation_scripts)
            program.counterpoint_rules.extend(individual.counterpoint_rules)
            program.harmonic_temperatures.extend(individual.harmonic_temperatures)

        # Deduplicate prompt semantics by word
        seen_words = set()
        deduped_ps = []
        for ps in program.prompt_semantics:
            if ps.word not in seen_words:
                seen_words.add(ps.word)
                deduped_ps.append(ps)
        program.prompt_semantics = deduped_ps

        # Deduplicate counterpoint rules by id
        seen_cp = set()
        deduped_cp = []
        for cp in program.counterpoint_rules:
            if cp.id not in seen_cp:
                seen_cp.add(cp.id)
                deduped_cp.append(cp)
        program.counterpoint_rules = deduped_cp

        # Deduplicate anti-patterns and breathing rules by id/type
        seen_ap = set()
        deduped_ap = []
        for ap in program.anti_patterns:
            if ap.id not in seen_ap:
                seen_ap.add(ap.id)
                deduped_ap.append(ap)
        program.anti_patterns = deduped_ap

        seen_br = set()
        deduped_br = []
        for br in program.breathing_rules:
            key = (br.type, br.placement)
            if key not in seen_br:
                seen_br.add(key)
                deduped_br.append(br)
        program.breathing_rules = deduped_br

        return program

    # ─── Data Loading ─────────────────────────────────────────────────────

    def _load_texture_stats(self, composer: str) -> tuple[dict[str, float], dict[str, float]]:
        """Load texture distributions directly from texture templates."""
        lh, rh = {}, {}
        template_path = TEXTURE_TEMPLATES / f"{composer}.json"
        if template_path.exists():
            with open(template_path) as f:
                template = json.load(f)
            template.get("total_bars_analyzed", 1)
            for tex_name, tex_data in template.get("lh_templates", {}).items():
                lh[tex_name] = tex_data.get("pct_of_bars", 0) / 100
            for tex_name, tex_data in template.get("rh_templates", {}).items():
                rh[tex_name] = tex_data.get("pct_of_bars", 0) / 100
        return lh, rh
