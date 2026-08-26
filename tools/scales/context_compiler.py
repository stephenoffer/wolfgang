"""
ContextCompiler — offline compilation of markdown profiles + corpus data
into structured ComposerPacks.

Nineteen passes:
  1. Manifest builder (filesystem scan, tier classification)
  2. Fingerprint extractor (composition-guide.md → fingerprint_rules.json)
  3. Statistics compiler (corpus + texture templates → scoped_statistics.json)
  4. Formal grammar compiler (formal-approach.md → formal_graphs.json)
  5. Harmonic rules compiler (harmonic-language.md → harmonic_rules.json)
  6. Orchestration + period overlays
  7. Cross-references, prototypes, review rubric
  8. Executable gestures (phrase-construction.md + composition-guide.md → gesture_templates.json)
  9. Anti-pattern rules (anti-patterns.md + ai-music-self-critique.md → anti_pattern_rules.json)
  10. Harmonic devices + cadence scripts (harmonic-language.md → harmonic_devices.json)
  11. Breathing rules (dramatic-pacing-silence.md → breathing_rules.json)
  12. Ornament intents (ornament-intent.md → ornament_intents.json)
  13. Prompt semantics (emotional-vocabulary.md + character-theme-design.md → prompt_semantics.json)
  14. Melody priors (melodic-construction.md + melody-craft.md → melody_priors.json)
  15. Figuration templates (figuration-patterns.md → figuration_templates.json)
  16. Modulation scripts (modulation-techniques.md → modulation_scripts.json)
  17. Counterpoint rules (counterpoint-essentials.md → counterpoint_rules.json)
  18. Harmonic temperature (harmonic-expression.md → harmonic_temperature.json)
  19. Grounding (cross-reference prose claims against corpus statistics)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

_BASE = Path(__file__).parent.parent
CONTEXT_DIR = _BASE.parent / ".claude" / "context"
REFERENCE_INDEX = _BASE / "reference_index"
PATTERN_LIBRARY = _BASE / "pattern_library"
TEXTURE_TEMPLATES = _BASE / "texture_templates"
COMPILED_PACKS = _BASE / "compiled_packs"


class ContextCompiler:
    """Compiles markdown profiles + corpus data into ComposerPacks."""

    def compile(self, composer: str, genre: str = "", force: bool = False) -> Dict[str, Any]:
        """Run all 19 compiler passes for a composer.

        Returns a summary of what was compiled.
        """
        # Find profile directory
        profile_dir = self._find_profile_dir(composer, genre)
        from .style_registry import pack_dir_name

        output_dir = COMPILED_PACKS / pack_dir_name(composer)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Pass 1: Manifest
        manifest = self._pass_manifest(composer, genre, profile_dir)
        self._write_json(output_dir / "manifest.json", manifest)
        results["manifest"] = manifest

        # Pass 2: Fingerprints
        fingerprints = self._pass_fingerprints(profile_dir)
        self._write_json(output_dir / "fingerprint_rules.json", fingerprints)
        results["fingerprints"] = len(fingerprints.get("items", []))

        # Pass 3: Statistics
        statistics = self._pass_statistics(composer, profile_dir)
        self._write_json(output_dir / "scoped_statistics.json", statistics)
        results["statistics"] = bool(statistics.get("total_bars"))

        # Pass 4: Formal grammars
        formal = self._pass_formal_grammar(profile_dir)
        self._write_json(output_dir / "formal_graphs.json", formal)
        results["formal"] = len(formal.get("forms", {}))

        # Pass 5: Harmonic rules
        harmonic = self._pass_harmonic_rules(profile_dir)
        self._write_json(output_dir / "harmonic_rules.json", harmonic)
        results["harmonic"] = len(harmonic.get("cadence_vocabulary", []))

        # Pass 6: Orchestration + period overlays
        orchestration = self._pass_orchestration(profile_dir)
        self._write_json(output_dir / "orchestration_roles.json", orchestration)
        periods = self._pass_periods(profile_dir)
        self._write_json(output_dir / "period_overlays.json", periods)
        results["periods"] = len(periods.get("periods", []))

        # Pass 7: Cross-references + prototypes + review rubric
        influence = self._pass_cross_references(profile_dir)
        self._write_json(output_dir / "influence_axes.json", influence)
        prototypes = self._pass_prototypes(profile_dir)
        self._write_json(output_dir / "phrase_prototypes.json", prototypes)
        rubric = self._pass_review_rubric(profile_dir, fingerprints)
        self._write_json(output_dir / "review_rubric.json", rubric)
        results["prototypes"] = len(prototypes.get("prototypes", []))

        # Pass 8: Executable gestures
        gestures = self._pass_executable_gestures(profile_dir)
        self._write_json(output_dir / "gesture_templates.json", gestures)
        results["gesture_templates"] = len(gestures)

        # Pass 9: Anti-pattern rules
        anti_patterns = self._pass_anti_patterns(profile_dir)
        self._write_json(output_dir / "anti_pattern_rules.json", anti_patterns)
        results["anti_pattern_rules"] = len(anti_patterns)

        # Pass 10: Harmonic devices + cadence scripts
        devices = self._pass_harmonic_devices(profile_dir)
        self._write_json(output_dir / "harmonic_devices.json", devices.get("devices", []))
        self._write_json(output_dir / "cadence_scripts.json", devices.get("cadence_scripts", []))
        results["harmonic_devices"] = len(devices.get("devices", []))

        # Pass 11: Breathing rules
        breathing = self._pass_breathing_rules()
        self._write_json(output_dir / "breathing_rules.json", breathing)
        results["breathing_rules"] = len(breathing)

        # Pass 12: Ornament intents
        ornaments = self._pass_ornament_policy()
        self._write_json(output_dir / "ornament_intents.json", ornaments)
        results["ornament_intents"] = len(ornaments)

        # Pass 13: Prompt semantics
        prompt_sem = self._pass_prompt_semantics()
        self._write_json(output_dir / "prompt_semantics.json", prompt_sem)
        results["prompt_semantics"] = len(prompt_sem)

        # Pass 14: Melody priors
        melody_pr = self._pass_melody_priors()
        self._write_json(output_dir / "melody_priors.json", melody_pr)
        results["melody_priors"] = len(melody_pr)

        # Pass 15: Figuration templates
        fig_tmpl = self._pass_figuration_templates()
        self._write_json(output_dir / "figuration_templates.json", fig_tmpl)
        results["figuration_templates"] = len(fig_tmpl)

        # Pass 16: Modulation scripts
        mod_scripts = self._pass_modulation_scripts()
        self._write_json(output_dir / "modulation_scripts.json", mod_scripts)
        results["modulation_scripts"] = len(mod_scripts)

        # Pass 17: Counterpoint rules
        cp_rules = self._pass_counterpoint_rules()
        self._write_json(output_dir / "counterpoint_rules.json", cp_rules)
        results["counterpoint_rules"] = len(cp_rules)

        # Pass 18: Harmonic temperature
        harm_temp = self._pass_harmonic_temperature()
        self._write_json(output_dir / "harmonic_temperature.json", harm_temp)
        results["harmonic_temperature"] = len(harm_temp)

        # Pass 19: Grounding (cross-reference prose claims against corpus stats)
        grounding_report = self._pass_grounding(output_dir, statistics, composer=composer)
        results["grounding"] = grounding_report

        return results

    def _find_profile_dir(self, composer: str, genre: str = "") -> Optional[Path]:
        """Find the composer profile directory."""
        # Search all genre directories
        for genre_dir in CONTEXT_DIR.iterdir():
            if not genre_dir.is_dir():
                continue
            profiles = genre_dir / "composer-profiles" / composer
            if profiles.is_dir():
                return profiles
        return None

    # ─── Pass 1: Manifest ─────────────────────────────────────────────────

    def _pass_manifest(self, composer: str, genre: str, profile_dir: Optional[Path]) -> Dict:
        """Enumerate available files and classify support tier."""
        profile_files = []
        if profile_dir and profile_dir.exists():
            profile_files = [f.name for f in profile_dir.iterdir() if f.suffix == ".md"]

        corpus_files = []
        corpus_bar_count = 0
        corpus_dir = REFERENCE_INDEX / composer
        if corpus_dir.exists():
            corpus_files = [f.name for f in corpus_dir.iterdir() if f.suffix == ".json"]
            # Try to get bar count from bar_index.json
            bar_index = corpus_dir / "bar_index.json"
            if bar_index.exists():
                with open(bar_index) as f:
                    idx = json.load(f)
                corpus_bar_count = idx.get("total_bars", 0)

        # Pattern count
        pattern_count = 0
        registry_path = PATTERN_LIBRARY / "composer_registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                registry = json.load(f)
            if composer in registry:
                pattern_count = registry[composer].get("pattern_count", 0)

        # Tier classification
        tier = "D"
        if "composition-guide.md" in profile_files:
            tier = "C"
        if corpus_bar_count > 0:
            tier = "B"
        if corpus_bar_count > 1000 and pattern_count > 100:
            tier = "A"

        return {
            "composer": composer,
            "genre": genre,
            "support_tier": tier,
            "corpus_bar_count": corpus_bar_count,
            "profile_files": sorted(profile_files),
            "corpus_files": sorted(corpus_files),
            "pattern_count": pattern_count,
        }

    # ─── Pass 2: Fingerprints ─────────────────────────────────────────────

    def _pass_fingerprints(self, profile_dir: Optional[Path]) -> Dict:
        """Extract fingerprint rules from composition-guide.md.

        Handles both flat fingerprint lists and multi-period composers
        (e.g. Beethoven) where fingerprints are nested under ### Period
        subsections within ## Fingerprints.
        """
        if not profile_dir:
            return {"required_count": 0, "items": []}

        guide = profile_dir / "composition-guide.md"
        if not guide.exists():
            return {"required_count": 0, "items": []}

        text = guide.read_text()
        items = []

        # Find the Fingerprints section — capture all content including ###
        # subsections, stopping only at the next ## (same level or higher)
        fingerprint_match = re.search(
            r"^#{1,2}\s*(?:\d+\s+)?Fingerprints?\b(.*?)(?=\n#{1,2}\s[^#]|\n---|\Z)",
            text,
            re.DOTALL | re.IGNORECASE | re.MULTILINE,
        )
        if not fingerprint_match:
            return {"required_count": 0, "items": []}

        section = fingerprint_match.group(1)

        # Extract period labels for tagging (### Middle Period, ### Late Period, etc.)
        period_sections = re.split(r"\n###\s+(.+?)(?:\n|$)", section)
        # period_sections alternates: [text_before, period_label, text, label, text, ...]

        if len(period_sections) <= 1:
            # No period subsections — flat fingerprint list
            self._extract_fingerprints_from_text(section, items, period="")
        else:
            # Multi-period: process each subsection
            for i in range(1, len(period_sections), 2):
                period_label = period_sections[i].strip()
                period_text = period_sections[i + 1] if i + 1 < len(period_sections) else ""
                self._extract_fingerprints_from_text(period_text, items, period=period_label)

        # Look for required count (e.g., "≥3 of 5" or "3 of these 5")
        required = 3
        req_match = re.search(r"[≥>]\s*(\d+)\s+of", section)
        if req_match:
            required = int(req_match.group(1))

        return {"required_count": required, "items": items}

    def _extract_fingerprints_from_text(
        self, text: str, items: List[Dict], period: str = ""
    ) -> None:
        """Extract numbered fingerprint items from a text block."""
        pattern = r"\d+\.\s+\*\*([^*]+)\*\*\s*[—–-]?\s*(.*?)(?=\n\d+\.|\Z)"
        for match in re.finditer(pattern, text, re.DOTALL):
            name = match.group(1).strip()
            description = match.group(2).strip()
            fp_id = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
            if period:
                period_slug = re.sub(r"[^a-z0-9]+", "_", period.lower()).strip("_")
                fp_id = f"{period_slug}__{fp_id}"

            items.append(
                {
                    "id": fp_id,
                    "name": name,
                    "description": description[:200],
                    "texture_affinities": _extract_texture_refs(description),
                    "frequency": "per_section",
                    "period": period,
                }
            )

    # ─── Pass 3: Statistics ───────────────────────────────────────────────

    def _pass_statistics(self, composer: str, profile_dir: Optional[Path]) -> Dict:
        """Compile statistics from corpus + texture templates + markdown."""
        stats: Dict[str, Any] = {"total_bars": 0, "lh_distribution": {}, "rh_distribution": {}}

        # Source 1: the corpus profile — measured from the bar records this
        # composer was actually extracted from.
        #
        # ``rh_distribution`` had NO SOURCE AT ALL: nothing ever wrote it, so it
        # was `{}` for every composer and the texture planner's fallback pinned
        # the upper staff to "singing_melody" for every bar of every piece ever
        # generated. The left-hand distribution came from a hand-built template
        # file carrying labels the extractor no longer emits ("sparse_octaves",
        # "walking_bass_chromatic", "unclassified"), so the planner could
        # schedule a texture matching no corpus bar and exemplar retrieval would
        # silently fall back to an untextured query.
        from .style_registry import pack_dir_name

        profile_path = COMPILED_PACKS / pack_dir_name(composer) / "corpus_profile.json"
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    profile = json.load(f)
                stats["total_bars"] = profile.get("total_bars", 0)
                for hand in ("lh", "rh"):
                    dist = profile.get(f"{hand}_texture_distribution") or {}
                    stats[f"{hand}_distribution"] = {
                        k: round(float(v), 4)
                        for k, v in dist.items()
                        if k not in ("silence", "unclassified") and v
                    }
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass

        # Source 1b: the legacy texture templates, only where the corpus is silent.
        template_path = TEXTURE_TEMPLATES / f"{composer}.json"
        if not stats["lh_distribution"] and template_path.exists():
            with open(template_path) as f:
                template = json.load(f)
            stats["total_bars"] = template.get("total_bars_analyzed", 0)
            lh = template.get("lh_templates", {})
            for tex_name, tex_data in lh.items():
                pct = tex_data.get("pct_of_bars", 0)
                stats["lh_distribution"][tex_name] = round(pct / 100, 3)

        # Source 2: Corpus bar index
        bar_index_path = REFERENCE_INDEX / composer / "bar_index.json"
        if bar_index_path.exists():
            with open(bar_index_path) as f:
                idx = json.load(f)
            if idx.get("total_bars", 0) > stats["total_bars"]:
                stats["total_bars"] = idx["total_bars"]

        # Source 3: Transition matrix
        for path in [
            PATTERN_LIBRARY / "transitions" / "by_composer" / f"{composer}.json",
            PATTERN_LIBRARY / "transitions" / "by_genre" / "classical.json",
        ]:
            if path.exists():
                with open(path) as f:
                    matrix = json.load(f)
                stats["transition_matrix"] = self._normalize_matrix(matrix.get("counts", {}))
                break

        return stats

    def _normalize_matrix(self, counts: Dict) -> Dict:
        """Normalize count matrix to probabilities."""
        result = {}
        for from_tex, to_counts in counts.items():
            total = sum(to_counts.values())
            if total > 0:
                result[from_tex] = {
                    to_tex: round(count / total, 4) for to_tex, count in to_counts.items()
                }
        return result

    # ─── Pass 4: Formal Grammar ──────────────────────────────────────────

    def _pass_formal_grammar(self, profile_dir: Optional[Path]) -> Dict:
        """Extract form templates from formal-approach.md."""
        if not profile_dir:
            return {"forms": {}}

        formal = profile_dir / "formal-approach.md"
        if not formal.exists():
            return {"forms": {}}

        text = formal.read_text()
        forms = {}

        # Look for sonata form proportions
        if "sonata" in text.lower():
            forms["sonata"] = {
                "sections": _extract_section_proportions(text, "sonata"),
                "key_scheme": {"exposition_keys": ["I", "V"], "recap_rule": "tonic"},
            }

        if "rondo" in text.lower():
            forms["rondo"] = {"sections": [], "key_scheme": {}}

        if "ternary" in text.lower():
            forms["ternary"] = {"sections": [], "key_scheme": {}}

        return {"forms": forms}

    # ─── Pass 5: Harmonic Rules ──────────────────────────────────────────

    def _pass_harmonic_rules(self, profile_dir: Optional[Path]) -> Dict:
        """Extract harmonic vocabulary from harmonic-language.md."""
        if not profile_dir:
            return {"cadence_vocabulary": [], "chromatic_techniques": []}

        harmonic = profile_dir / "harmonic-language.md"
        if not harmonic.exists():
            return {"cadence_vocabulary": [], "chromatic_techniques": []}

        text = harmonic.read_text()

        # Extract cadence patterns
        cadences = []
        for cad_type in ["PAC", "IAC", "HC", "DC", "plagal", "deceptive"]:
            if cad_type.lower() in text.lower():
                cadences.append({"type": cad_type, "frequency_weight": 0.5})

        # Extract chromatic techniques
        chromatics = []
        chromatic_keywords = [
            "Neapolitan",
            "augmented sixth",
            "chromatic",
            "diminished seventh",
            "secondary dominant",
            "modal mixture",
            "borrowed chord",
        ]
        for keyword in chromatic_keywords:
            if keyword.lower() in text.lower():
                chromatics.append({"name": keyword, "frequency_weight": 0.3})

        return {
            "cadence_vocabulary": cadences,
            "chromatic_techniques": chromatics,
        }

    # ─── Pass 6: Orchestration + Periods ──────────────────────────────────

    def _pass_orchestration(self, profile_dir: Optional[Path]) -> Dict:
        """Extract orchestration roles."""
        if not profile_dir:
            return {"instruments": {}}

        orch = profile_dir / "orchestration.md"
        if not orch.exists():
            return {"instruments": {}}

        # Basic extraction — would be more sophisticated in production
        return {"instruments": {}, "source_file": "orchestration.md"}

    def _pass_periods(self, profile_dir: Optional[Path]) -> Dict:
        """Extract period overlays from stylistic-evolution.md."""
        if not profile_dir:
            return {"periods": []}

        evolution = profile_dir / "stylistic-evolution.md"
        if not evolution.exists():
            return {"periods": []}

        text = evolution.read_text()
        periods = []

        # Look for common period labels
        for label in ["early", "middle", "late", "final"]:
            if label.lower() in text.lower():
                periods.append({"id": label, "stat_modifiers": {}})

        return {"periods": periods}

    # ─── Pass 7: Cross-References + Prototypes + Rubric ───────────────────

    def _pass_cross_references(self, profile_dir: Optional[Path]) -> Dict:
        """Extract influence axes from cross-references.md."""
        if not profile_dir:
            return {"influenced_by": [], "comparative_axes": {}}

        xref = profile_dir / "cross-references.md"
        if not xref.exists():
            return {"influenced_by": [], "comparative_axes": {}}

        text = xref.read_text()

        # Extract named composers
        influenced_by = []
        for match in re.finditer(
            r"(?:influenced by|learned from|absorbed)\s+(\w+)", text, re.IGNORECASE
        ):
            influenced_by.append({"composer": match.group(1)})

        return {"influenced_by": influenced_by, "comparative_axes": {}}

    def _pass_prototypes(self, profile_dir: Optional[Path]) -> Dict:
        """Extract JSON code examples from composition-guide.md."""
        if not profile_dir:
            return {"prototypes": []}

        guide = profile_dir / "composition-guide.md"
        if not guide.exists():
            return {"prototypes": []}

        text = guide.read_text()
        prototypes = []

        # Find JSON code blocks
        for match in re.finditer(r"```json\s*\n(.*?)\n```", text, re.DOTALL):
            try:
                data = json.loads(match.group(1))
                prototypes.append(
                    {
                        "id": f"prototype_{len(prototypes)}",
                        "data": data,
                    }
                )
            except json.JSONDecodeError:
                continue

        return {"prototypes": prototypes}

    def _pass_review_rubric(self, profile_dir: Optional[Path], fingerprints: Dict) -> Dict:
        """Build review rubric from fingerprints + anti-patterns."""
        checks = []

        # Fingerprint checks
        for fp in fingerprints.get("items", []):
            checks.append(
                {
                    "id": f"fp_{fp['id']}",
                    "category": "fingerprint",
                    "description": fp.get("name", ""),
                    "severity": "soft",
                }
            )

        # Anti-pattern checks (from composition-guide.md)
        if profile_dir:
            guide = profile_dir / "composition-guide.md"
            if guide.exists():
                text = guide.read_text()
                # Find anti-pattern section
                ap_match = re.search(
                    r"anti.?pattern(.*?)(?=\n#{1,3}\s|\Z)", text, re.DOTALL | re.IGNORECASE
                )
                if ap_match:
                    for line in ap_match.group(1).split("\n"):
                        line = line.strip().lstrip("- ")
                        if len(line) > 10:
                            checks.append(
                                {
                                    "id": f"anti_{len(checks)}",
                                    "category": "anti_pattern",
                                    "description": line[:100],
                                    "severity": "soft",
                                }
                            )

        return {"checks": checks}

    # ─── Pass 8: Executable Gestures ─────────────────────────────────────

    def _pass_executable_gestures(self, profile_dir: Optional[Path]) -> List[Dict]:
        """Extract note-level gesture templates from context files.

        Sources:
        - .claude/context/general/phrase-construction.md (18 techniques with JSON)
        - Per-composer composition-guide.md (technique examples with JSON)
        """
        gestures: List[Dict] = []

        # Source 1: General phrase-construction.md
        pc_file = CONTEXT_DIR / "general" / "phrase-construction.md"
        if pc_file.exists():
            text = pc_file.read_text()
            # Split by H2 sections
            sections = re.split(r"\n##\s+", text)
            for section in sections[1:]:  # skip preamble before first ##
                lines = section.split("\n", 1)
                heading = lines[0].strip()
                body = lines[1] if len(lines) > 1 else ""
                gesture_id = re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")

                # Extract JSON blocks
                voice_events: Dict[str, List[Dict]] = {}
                situation = ""
                for jmatch in re.finditer(r"```json\s*\n(.*?)\n```", body, re.DOTALL):
                    try:
                        data = json.loads(
                            "[" + jmatch.group(1) + "]"
                            if not jmatch.group(1).strip().startswith("[")
                            else jmatch.group(1)
                        )
                        # Extract voice events from parsed JSON
                        for bar_obj in data if isinstance(data, list) else [data]:
                            if isinstance(bar_obj, dict) and "voices" in bar_obj:
                                for voice_name, events in bar_obj["voices"].items():
                                    if isinstance(events, list):
                                        voice_events.setdefault(voice_name, []).extend(events)
                            feel = bar_obj.get("_feel", "") if isinstance(bar_obj, dict) else ""
                            if feel and not situation:
                                situation = feel
                    except (json.JSONDecodeError, TypeError):
                        continue

                if voice_events:
                    gestures.append(
                        {
                            "id": f"general__{gesture_id}",
                            "name": heading,
                            "situation": situation,
                            "voice_events": voice_events,
                            "harmonic_context": "",
                            "phrase_functions": [],
                            "composer_affinities": [],
                            "source_file": "phrase-construction.md",
                            "source_heading": heading,
                        }
                    )

        # Source 2: Composer-specific composition-guide.md
        if profile_dir:
            guide = profile_dir / "composition-guide.md"
            if guide.exists():
                text = guide.read_text()
                composer_name = profile_dir.name
                # Find "Note-Level Technique" or "Technique" sections with JSON
                tech_pattern = r"##\s+((?:Note-Level\s+)?Technique\s+\d+[^#]*?)(?=\n##\s|\Z)"
                for tmatch in re.finditer(tech_pattern, text, re.DOTALL | re.IGNORECASE):
                    section_text = tmatch.group(1)
                    heading_line = section_text.split("\n")[0].strip()
                    tech_id = re.sub(r"[^a-z0-9]+", "_", heading_line.lower()).strip("_")

                    voice_events = {}
                    situation = ""
                    for jmatch in re.finditer(r"```json\s*\n(.*?)\n```", section_text, re.DOTALL):
                        try:
                            raw = jmatch.group(1).strip()
                            # Handle multiple JSON objects separated by commas
                            if raw.startswith("{"):
                                raw = "[" + raw + "]"
                            data = json.loads(raw)
                            for bar_obj in data if isinstance(data, list) else [data]:
                                if isinstance(bar_obj, dict) and "voices" in bar_obj:
                                    for vname, events in bar_obj["voices"].items():
                                        if isinstance(events, list):
                                            voice_events.setdefault(vname, []).extend(events)
                                feel = bar_obj.get("_feel", "") if isinstance(bar_obj, dict) else ""
                                if feel and not situation:
                                    situation = feel
                        except (json.JSONDecodeError, TypeError):
                            continue

                    if voice_events:
                        gestures.append(
                            {
                                "id": f"{composer_name}__{tech_id}",
                                "name": heading_line,
                                "situation": situation,
                                "voice_events": voice_events,
                                "harmonic_context": "",
                                "phrase_functions": [],
                                "composer_affinities": [composer_name],
                                "source_file": f"{composer_name}/composition-guide.md",
                                "source_heading": heading_line,
                            }
                        )

        return gestures

    # ─── Pass 9: Anti-Pattern Rules ───────────────────────────────────────

    def _pass_anti_patterns(self, profile_dir: Optional[Path]) -> List[Dict]:
        """Extract anti-pattern rules from context files.

        Sources:
        - .claude/context/general/anti-patterns.md (10 categories with examples)
        - .claude/context/general/ai-music-self-critique.md (~30 AI tells)
        - .claude/context/general/human-sounding-music.md (quantitative checklist)
        """
        rules: List[Dict] = []

        # Detector name mapping from known anti-pattern categories
        detector_map = {
            "flat dynamics": "flat_dynamics",
            "same accompaniment": "same_accompaniment",
            "theme stated identically": "identical_restatement",
            "no ornaments": "missing_ornaments",
            "all instruments playing": "no_rests_between_instruments",
            "rhythmic unison": "rhythmic_unison",
            "block chords": "block_chord_overuse",
            "arpeggiated chords": "melody_is_arpeggio",
            "generic transition": "generic_transition",
            "single phrase": "single_phrase_section",
        }

        # Source 1: anti-patterns.md
        ap_file = CONTEXT_DIR / "general" / "anti-patterns.md"
        if ap_file.exists():
            text = ap_file.read_text()
            sections = re.split(r"\n##\s+", text)
            for section in sections[1:]:
                heading = section.split("\n")[0].strip()
                heading_lower = heading.lower()
                detector = "unknown"
                for key, det in detector_map.items():
                    if key in heading_lower:
                        detector = det
                        break
                rules.append(
                    {
                        "id": f"ap_{re.sub(r'[^a-z0-9]+', '_', heading_lower).strip('_')}",
                        "name": heading,
                        "description": heading,
                        "detector": detector,
                        "severity": "warning",
                        "params": {},
                        "style_scope": "",
                        "source_file": "anti-patterns.md",
                    }
                )

        # Source 2: ai-music-self-critique.md
        critique_file = CONTEXT_DIR / "general" / "ai-music-self-critique.md"
        if critique_file.exists():
            text = critique_file.read_text()
            # Extract subsection headings as AI tell names
            for match in re.finditer(r"\n###\s+(?:The\s+)?(.+)", text):
                tell_name = match.group(1).strip()
                tell_id = re.sub(r"[^a-z0-9]+", "_", tell_name.lower()).strip("_")
                rules.append(
                    {
                        "id": f"critique_{tell_id}",
                        "name": tell_name,
                        "description": tell_name,
                        "detector": tell_id,
                        "severity": "warning",
                        "params": {},
                        "style_scope": "",
                        "source_file": "ai-music-self-critique.md",
                    }
                )

        # Source 3: human-sounding-music.md quantitative checklist
        hsm_file = CONTEXT_DIR / "general" / "human-sounding-music.md"
        if hsm_file.exists():
            text = hsm_file.read_text()
            # Parse the "Quantitative Discriminator Checklist" table
            table_match = re.search(
                r"Quantitative Discriminator.*?\n\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)",
                text,
                re.IGNORECASE,
            )
            if table_match:
                for row in table_match.group(1).strip().split("\n"):
                    cols = [c.strip() for c in row.split("|")[1:-1]]
                    if len(cols) >= 4:
                        metric = cols[0]
                        target = cols[1]
                        range_val = cols[2]
                        catches = cols[3]
                        metric_id = re.sub(r"[^a-z0-9]+", "_", metric.lower()).strip("_")
                        rules.append(
                            {
                                "id": f"quant_{metric_id}",
                                "name": metric,
                                "description": catches,
                                "detector": f"quantitative_{metric_id}",
                                "severity": "warning",
                                "params": {"target": target, "range": range_val},
                                "style_scope": "",
                                "source_file": "human-sounding-music.md",
                            }
                        )

        return rules

    # ─── Pass 10: Harmonic Devices + Cadence Scripts ──────────────────────

    def _pass_harmonic_devices(self, profile_dir: Optional[Path]) -> Dict:
        """Extract harmonic devices and cadence scripts from harmonic-language.md.

        Richer than pass 5 — extracts actual chord sequences, voice-leading
        hints, usage contexts, and emotional color.
        """
        devices: List[Dict] = []
        cadence_scripts: List[Dict] = []

        if not profile_dir:
            return {"devices": devices, "cadence_scripts": cadence_scripts}

        hl_file = profile_dir / "harmonic-language.md"
        if not hl_file.exists():
            return {"devices": devices, "cadence_scripts": cadence_scripts}

        text = hl_file.read_text()

        # Parse markdown tables for harmonic techniques
        # Look for tables with columns like: Technique | Frequency | Context | Example
        table_pattern = r"\|[^|\n]*(?:Technique|Device|Name)[^|\n]*\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)"
        for tmatch in re.finditer(table_pattern, text, re.IGNORECASE):
            for row in tmatch.group(1).strip().split("\n"):
                cols = [c.strip() for c in row.split("|")[1:-1]]
                if len(cols) >= 2:
                    name = cols[0]
                    dev_id = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                    context = cols[2] if len(cols) > 2 else ""
                    freq = cols[1] if len(cols) > 1 else ""

                    # Try to parse frequency weight
                    freq_weight = 0.3
                    freq_match = re.search(r"(\d+(?:\.\d+)?)", freq)
                    if freq_match:
                        try:
                            freq_weight = min(1.0, float(freq_match.group(1)) / 100.0)
                        except ValueError:
                            pass

                    devices.append(
                        {
                            "id": dev_id,
                            "name": name,
                            "chord_sequence": [],
                            "voice_leading_hints": [],
                            "contexts": [c.strip() for c in context.split(",") if c.strip()],
                            "frequency_weight": freq_weight,
                            "emotional_color": "",
                            "source_file": f"{profile_dir.name}/harmonic-language.md",
                        }
                    )

        # Parse cadence tables.
        #
        # Two bugs lived here. The header pattern required the literal word
        # "Cadence" in the HEADER ROW, so Beethoven's table — headed
        # "| Strategy | How It Works | Dramatic Function |" under a "Cadential
        # Strategy" heading — was invisible, and the flagship composer shipped an
        # EMPTY cadence_scripts.json. And each row's own columns were read into a
        # bare expression that was never assigned, so even where the pack was
        # populated every script carried empty approach_chords, soprano_line and
        # bass_motion — the brief could only ever print "Cadence: type PAC".
        for block in _cadence_table_blocks(text):
            for row in block:
                cols = [c.strip() for c in row.split("|")[1:-1]]
                if len(cols) < 2 or not cols[0]:
                    continue
                cad_type = cols[0]
                cad_id = re.sub(r"[^a-z0-9]+", "_", cad_type.lower()).strip("_")
                rest = cols[1:]
                chords = _chord_chain(rest)
                usage = next((c for c in rest if c and not _chord_chain([c])), "")
                cadence_scripts.append(
                    {
                        "id": f"cad_{cad_id}",
                        "type": cad_type,
                        "approach_chords": chords,
                        "soprano_line": [],
                        "bass_motion": _bass_motion(chords),
                        "usage": usage,
                        "inner_voice_rules": [],
                        "strength": 3,
                        "typical_texture": "",
                        "preparation_bars": 2,
                        "source_file": f"{profile_dir.name}/harmonic-language.md",
                    }
                )

        return {"devices": devices, "cadence_scripts": cadence_scripts}

    # ─── Pass 11: Breathing Rules ─────────────────────────────────────────

    def _pass_breathing_rules(self) -> List[Dict]:
        """Extract silence/breathing doctrine from dramatic-pacing-silence.md.

        Parses the "Silence as Dramatic Device" table (7 rows) and
        other timing/tension tables.
        """
        rules: List[Dict] = []

        dp_file = CONTEXT_DIR / "general" / "dramatic-pacing-silence.md"
        if not dp_file.exists():
            return rules

        text = dp_file.read_text()

        # Parse all markdown tables
        table_pattern = r"\|[^|\n]+\|[^|\n]+\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)"
        for tmatch in re.finditer(table_pattern, text):
            table_text = tmatch.group(0)
            # Get header columns
            header_line = table_text.split("\n")[0]
            headers = [h.strip().lower() for h in header_line.split("|")[1:-1]]

            # Check if this looks like a silence/breathing table
            if any(h in ("type", "technique") for h in headers) and any(
                h in ("placement", "effect", "duration") for h in headers
            ):
                rows = tmatch.group(1).strip().split("\n")
                for row in rows:
                    cols = [c.strip() for c in row.split("|")[1:-1]]
                    if len(cols) < 2:
                        continue

                    rule: Dict[str, Any] = {
                        "source_file": "dramatic-pacing-silence.md",
                    }
                    for i, header in enumerate(headers):
                        if i < len(cols):
                            val = cols[i]
                            if header == "type":
                                rule["type"] = val.lower().replace(" ", "_")
                            elif header == "placement":
                                rule["placement"] = val.lower().replace(" ", "_")
                            elif header == "duration":
                                # Try to parse beat ranges like "1-2 beats"
                                dur_match = re.search(
                                    r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)", val
                                )
                                if dur_match:
                                    rule["duration_beats_min"] = float(dur_match.group(1))
                                    rule["duration_beats_max"] = float(dur_match.group(2))
                                else:
                                    rule["duration_beats_min"] = 1.0
                                    rule["duration_beats_max"] = 4.0
                            elif header == "effect":
                                rule["effect"] = val
                            elif header == "technique":
                                rule["technique"] = val

                    if "type" in rule or "technique" in rule:
                        rules.append(rule)

        return rules

    # ─── Pass 12: Ornament Intents ────────────────────────────────────────

    def _pass_ornament_policy(self) -> List[Dict]:
        """Extract ornament intent rules from ornament-intent.md.

        Parses the "Ornament Decision Framework" table and emotion table.
        """
        intents: List[Dict] = []

        oi_file = CONTEXT_DIR / "general" / "ornament-intent.md"
        if not oi_file.exists():
            return intents

        text = oi_file.read_text()

        # Find the Decision Framework table
        # Columns: Musical Context | What the Moment Often Needs | Common Choice | Why | ABC Pattern
        table_pattern = (
            r"\|[^|\n]*(?:Musical Context|Context)[^|\n]*\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)"
        )
        for tmatch in re.finditer(table_pattern, text, re.IGNORECASE):
            for row in tmatch.group(1).strip().split("\n"):
                cols = [c.strip() for c in row.split("|")[1:-1]]
                if len(cols) >= 3:
                    context = cols[0]
                    moment_needs = cols[1] if len(cols) > 1 else ""
                    common_choice = cols[2] if len(cols) > 2 else ""
                    why = cols[3] if len(cols) > 3 else ""

                    intents.append(
                        {
                            "context": re.sub(r"[^a-z0-9]+", "_", context.lower()).strip("_"),
                            "what_moment_needs": moment_needs,
                            "common_choice": common_choice,
                            "why": why,
                            "density_arc": "",
                        }
                    )

        # Also parse the Ornament and Emotion table if present
        emotion_pattern = (
            r"\|[^|\n]*(?:Emotional State|Emotion)[^|\n]*\|.*?\n\|[-\s|]+\n((?:\|.*\n)*)"
        )
        for ematch in re.finditer(emotion_pattern, text, re.IGNORECASE):
            for row in ematch.group(1).strip().split("\n"):
                cols = [c.strip() for c in row.split("|")[1:-1]]
                if len(cols) >= 3:
                    emotion = cols[0]
                    density = cols[1] if len(cols) > 1 else ""
                    orn_types = cols[2] if len(cols) > 2 else ""
                    approach = cols[4] if len(cols) > 4 else ""

                    intents.append(
                        {
                            "context": f"emotion_{re.sub(r'[^a-z0-9]+', '_', emotion.lower()).strip('_')}",
                            "what_moment_needs": emotion,
                            "common_choice": orn_types,
                            "why": approach,
                            "density_arc": density,
                        }
                    )

        return intents

    # ─── Pass 13: Prompt Semantics ──────────────────────────────────────

    def _pass_prompt_semantics(self) -> List[Dict]:
        """Extract emotion-to-music parameter mappings from general context.

        Sources:
        - emotional-vocabulary.md (emotion → tempo/mode/dynamics/texture/etc.)
        - character-theme-design.md (archetype → intervals/rhythm/timbre/etc.)
        - musical-semiotics.md (interval/chord affect tables)
        """
        semantics: List[Dict] = []

        # Source 1: emotional-vocabulary.md — main emotion table
        ev_file = CONTEXT_DIR / "general" / "emotional-vocabulary.md"
        if ev_file.exists():
            text = ev_file.read_text()
            rows = _parse_markdown_table(text, required_header="Emotion")
            for row in rows:
                emotion = row.get("emotion", "").strip()
                if not emotion:
                    continue
                tempo = row.get("tempo_bpm", "")
                tempo_range = _parse_range(tempo)
                semantics.append(
                    {
                        "word": emotion.lower(),
                        "synonyms": [],
                        "tempo_range": tempo_range,
                        "mode_scale": [
                            s.strip() for s in row.get("mode_scale", "").split(",") if s.strip()
                        ],
                        "dynamics": row.get("dynamics", ""),
                        "texture": row.get("texture", ""),
                        "register": row.get("register", ""),
                        "articulation": row.get("articulation", ""),
                        "rhythm_type": row.get("rhythm_type", row.get("rhythm type", "")),
                        "harmonic_language": row.get(
                            "harmonic_language", row.get("harmonic language", "")
                        ),
                        "interval_preferences": [],
                        "density_range": None,
                        "orchestration_color": "",
                        "contour": "",
                        "grounding": "interpretive",
                        "source_files": ["emotional-vocabulary.md"],
                    }
                )

        # Source 2: character-theme-design.md — archetype table
        ctd_file = CONTEXT_DIR / "general" / "character-theme-design.md"
        if ctd_file.exists():
            text = ctd_file.read_text()
            rows = _parse_markdown_table(text, required_header="Archetype")
            for row in rows:
                archetype = row.get("archetype", "").strip()
                if not archetype:
                    continue
                intervals = row.get("intervals", "")
                contour = row.get("contour", "")
                semantics.append(
                    {
                        "word": archetype.lower(),
                        "synonyms": [],
                        "tempo_range": None,
                        "mode_scale": [],
                        "dynamics": "",
                        "texture": "",
                        "register": row.get("register", ""),
                        "articulation": "",
                        "rhythm_type": row.get("rhythm", ""),
                        "harmonic_language": row.get("harmony", ""),
                        "interval_preferences": [
                            s.strip() for s in intervals.split(",") if s.strip()
                        ],
                        "density_range": None,
                        "orchestration_color": row.get("timbre", ""),
                        "contour": contour,
                        "grounding": "interpretive",
                        "source_files": ["character-theme-design.md"],
                    }
                )

        # Source 3: musical-semiotics.md — interval affect
        ms_file = CONTEXT_DIR / "general" / "musical-semiotics.md"
        if ms_file.exists():
            text = ms_file.read_text()
            rows = _parse_markdown_table(text, required_header="Interval")
            for row in rows:
                interval = row.get("interval", "").strip()
                affect = row.get("affect", "").strip()
                if not interval or not affect:
                    continue
                # Create semantic entries for each affect word
                for word in affect.split(","):
                    word = word.strip().lower()
                    if word and len(word) > 2:
                        # Check if already exists
                        existing = next((s for s in semantics if s["word"] == word), None)
                        if existing:
                            if interval not in existing["interval_preferences"]:
                                existing["interval_preferences"].append(interval)
                            if "musical-semiotics.md" not in existing["source_files"]:
                                existing["source_files"].append("musical-semiotics.md")
                        else:
                            semantics.append(
                                {
                                    "word": word,
                                    "synonyms": [],
                                    "tempo_range": None,
                                    "mode_scale": [],
                                    "dynamics": "",
                                    "texture": "",
                                    "register": "",
                                    "articulation": "",
                                    "rhythm_type": "",
                                    "harmonic_language": "",
                                    "interval_preferences": [interval],
                                    "density_range": None,
                                    "orchestration_color": "",
                                    "contour": "",
                                    "grounding": "interpretive",
                                    "source_files": ["musical-semiotics.md"],
                                }
                            )

        return semantics

    # ─── Pass 14: Melody Priors ──────────────────────────────────────────

    def _pass_melody_priors(self) -> List[Dict]:
        """Extract melodic construction priors from general context.

        Sources:
        - melodic-construction.md (phrase structure, contour, climax placement)
        - melody-craft.md (artistic intent, hook design)
        """
        priors: List[Dict] = []

        # Source 1: melodic-construction.md
        mc_file = CONTEXT_DIR / "general" / "melodic-construction.md"
        if mc_file.exists():
            text = mc_file.read_text()

            # Parse phrase structure table
            rows = _parse_markdown_table(text, required_header="Unit")
            for row in rows:
                unit = row.get("unit", "").strip()
                length = row.get("typical_length", row.get("typical length", ""))
                function = row.get("function", "")
                if unit:
                    priors.append(
                        {
                            "id": f"phrase_structure_{unit.lower()}",
                            "category": "phrase_structure",
                            "description": f"{unit}: {function}",
                            "parameters": {
                                "unit": unit,
                                "typical_length": length,
                                "function": function,
                            },
                            "conditions": {},
                            "grounding": "hard_corroborated",
                            "source_file": "melodic-construction.md",
                        }
                    )

            # Parse contour table
            rows = _parse_markdown_table(text, required_header="Contour")
            for row in rows:
                contour = row.get("contour", "").strip()
                shape = row.get("shape", "")
                association = row.get("emotional_association", row.get("emotional association", ""))
                best_for = row.get("best_for", row.get("best for", ""))
                if contour:
                    priors.append(
                        {
                            "id": f"contour_{contour.lower().replace(' ', '_')}",
                            "category": "contour",
                            "description": f"{contour} ({shape}): {association}",
                            "parameters": {
                                "contour": contour,
                                "shape": shape,
                                "association": association,
                            },
                            "conditions": {"best_for": best_for},
                            "grounding": "interpretive",
                            "source_file": "melodic-construction.md",
                        }
                    )

            # Parse climax placement table
            rows = _parse_markdown_table(text, required_header="Scale")
            for row in rows:
                scale = row.get("scale", "").strip()
                placement = row.get("typical_placement", row.get("typical placement", ""))
                if scale and placement:
                    priors.append(
                        {
                            "id": f"peak_timing_{scale.lower().replace(' ', '_')}",
                            "category": "peak_timing",
                            "description": f"Climax placement at {scale} level: {placement}",
                            "parameters": {"scale": scale, "placement": placement},
                            "conditions": {},
                            "grounding": "soft_corroborated",
                            "source_file": "melodic-construction.md",
                        }
                    )

            # Parse irregular phrase lengths table
            rows = _parse_markdown_table(text, required_header="Length")
            for row in rows:
                length = row.get("length", "").strip()
                how = row.get("how_it_occurs", row.get("how it occurs", ""))
                effect = row.get("effect", "")
                if length:
                    priors.append(
                        {
                            "id": f"irregular_phrase_{length}",
                            "category": "phrase_structure",
                            "description": f"{length}-bar phrase: {how} → {effect}",
                            "parameters": {"length": length, "occurrence": how, "effect": effect},
                            "conditions": {},
                            "grounding": "soft_corroborated",
                            "source_file": "melodic-construction.md",
                        }
                    )

        # Source 2: melody-craft.md
        mc2_file = CONTEXT_DIR / "general" / "melody-craft.md"
        if mc2_file.exists():
            text = mc2_file.read_text()

            # Parse any tables about interval usage, hook design, etc.
            for table_rows in _parse_all_markdown_tables(text):
                if not table_rows:
                    continue
                first_row = table_rows[0]
                keys = list(first_row.keys())

                # Identify table type from headers
                if any("interval" in k.lower() for k in keys):
                    for row in table_rows:
                        vals = list(row.values())
                        if len(vals) >= 2 and vals[0].strip():
                            priors.append(
                                {
                                    "id": f"melody_craft_{re.sub(r'[^a-z0-9]+', '_', vals[0].lower()).strip('_')}",
                                    "category": "interval_language",
                                    "description": " | ".join(str(v) for v in vals[:3]),
                                    "parameters": dict(zip(keys, vals)),
                                    "conditions": {},
                                    "grounding": "interpretive",
                                    "source_file": "melody-craft.md",
                                }
                            )

        return priors

    # ─── Pass 15: Figuration Templates ───────────────────────────────────

    def _pass_figuration_templates(self) -> List[Dict]:
        """Extract figuration catalog from figuration-patterns.md."""
        templates: List[Dict] = []

        fp_file = CONTEXT_DIR / "general" / "figuration-patterns.md"
        if not fp_file.exists():
            return templates

        text = fp_file.read_text()

        # Parse the main figuration catalog table
        rows = _parse_markdown_table(text, required_header="#")
        if not rows:
            rows = _parse_markdown_table(text, required_header="Name")
        for row in rows:
            name = row.get("name", "").strip()
            if not name:
                continue
            num = row.get("", row.get("#", "")).strip()
            period = row.get("period_style", "")
            tempo = row.get("tempo", "")
            character = row.get("character", "")

            # Map name to pattern keyword
            keyword_map = {
                "alberti": "alberti",
                "ascending arpeggio": "broken_chord_asc",
                "descending arpeggio": "broken_chord_desc",
                "murky": "murky_bass",
                "waltz": "waltz_bass",
                "rachmaninoff": "wide_span_arpeggio",
                "turn-based": "turn_based",
                "scalar fill ascending": "scalar_asc",
                "scalar fill descending": "scalar_desc",
                "tremolo": "tremolo",
                "broken octave": "broken_octave",
                "chordal": "chordal_passing",
            }
            keyword = "unknown"
            name_lower = name.lower()
            for key, val in keyword_map.items():
                if key in name_lower:
                    keyword = val
                    break

            tempo_range = _parse_range(tempo)
            period_list = [s.strip() for s in period.split(",") if s.strip()] if period else []

            templates.append(
                {
                    "id": f"fig_{num}_{keyword}" if num else f"fig_{keyword}",
                    "name": name,
                    "pattern_keyword": keyword,
                    "period_style": period_list,
                    "tempo_range": tempo_range,
                    "character": character,
                    "when_to_use": [],
                    "variation_operators": [],
                    "density_suggestion": None,
                    "register_suggestion": "",
                    "grounding": "interpretive",
                    "source_file": "figuration-patterns.md",
                }
            )

        # Parse the "Choosing a Figuration" decision table
        rows = _parse_markdown_table(text, required_header="If the music needs")
        for row in rows:
            need = row.get("if_the_music_needs", "").strip()
            figs = row.get("use_figurations", "").strip()
            if need and figs:
                # Map figuration numbers to templates
                fig_nums = re.findall(r"\d+", figs)
                for tmpl in templates:
                    tmpl_num = re.search(r"fig_(\d+)", tmpl["id"])
                    if tmpl_num and tmpl_num.group(1) in fig_nums:
                        tmpl["when_to_use"].append(need)

        return templates

    # ─── Pass 16: Modulation Scripts ─────────────────────────────────────

    def _pass_modulation_scripts(self) -> List[Dict]:
        """Extract modulation procedures from modulation-techniques.md."""
        scripts: List[Dict] = []

        mt_file = CONTEXT_DIR / "general" / "modulation-techniques.md"
        if not mt_file.exists():
            return scripts

        text = mt_file.read_text()

        # Parse the main modulation types table
        rows = _parse_markdown_table(text, required_header="Type")
        for row in rows:
            mod_type = row.get("type", "").strip()
            if not mod_type:
                continue
            mechanism = row.get("mechanism", "")
            smoothness = row.get("smoothness", "")
            best_for = row.get("best_for", row.get("best for", ""))

            type_id = re.sub(r"[^a-z0-9]+", "_", mod_type.lower()).strip("_")
            scripts.append(
                {
                    "id": f"mod_{type_id}",
                    "type": type_id,
                    "from_key_class": "any",
                    "to_key_relationship": "",
                    "mechanism": mechanism,
                    "smoothness": re.sub(r"[^a-z_]+", "_", smoothness.lower()).strip("_")
                    if smoothness
                    else "",
                    "best_for": [s.strip() for s in best_for.split(",") if s.strip()],
                    "chord_sequence": [],
                    "voice_leading_hints": [],
                    "pivot_chord_in_old": "",
                    "pivot_chord_in_new": "",
                    "grounding": "hard_corroborated",
                    "source_file": "modulation-techniques.md",
                }
            )

        # Parse pivot chord tables
        rows = _parse_markdown_table(text, required_header="To key")
        for row in rows:
            to_key = row.get("to_key", row.get("to key", "")).strip()
            pivot = row.get("pivot_chord", row.get("pivot chord", "")).strip()
            in_old = row.get("in_c_major", row.get("in c major", "")).strip()
            in_new = row.get("in_new_key", row.get("in new key", "")).strip()
            if to_key and pivot:
                scripts.append(
                    {
                        "id": f"mod_pivot_to_{re.sub(r'[^a-z0-9]+', '_', to_key.lower()).strip('_')}",
                        "type": "pivot_chord",
                        "from_key_class": "major",
                        "to_key_relationship": to_key.lower(),
                        "mechanism": f"Pivot: {pivot}",
                        "smoothness": "very_smooth",
                        "best_for": ["transitions", "expositions"],
                        "chord_sequence": [],
                        "voice_leading_hints": [],
                        "pivot_chord_in_old": in_old,
                        "pivot_chord_in_new": in_new,
                        "grounding": "hard_corroborated",
                        "source_file": "modulation-techniques.md",
                    }
                )

        return scripts

    # ─── Pass 17: Counterpoint Rules ─────────────────────────────────────

    def _pass_counterpoint_rules(self) -> List[Dict]:
        """Extract contrapuntal rules from counterpoint-essentials.md."""
        rules: List[Dict] = []

        ce_file = CONTEXT_DIR / "general" / "counterpoint-essentials.md"
        if not ce_file.exists():
            return rules

        text = ce_file.read_text()

        # Parse motion types table
        rows = _parse_markdown_table(text, required_header="Motion type")
        for row in rows:
            motion = row.get("motion_type", row.get("motion type", "")).strip()
            definition = row.get("definition", "")
            usage = row.get("usage", "")
            if motion:
                rules.append(
                    {
                        "id": f"cp_motion_{motion.lower().replace(' ', '_')}",
                        "category": "motion_balance",
                        "description": f"{motion}: {definition}. {usage}",
                        "severity": "suggestion",
                        "style_permissions": {
                            "common_practice": True,
                            "impressionist": True,
                            "modern": True,
                        },
                        "repair_recipe": "",
                        "detection_heuristic": {"motion_type": motion.lower()},
                        "grounding": "hard_corroborated",
                        "source_file": "counterpoint-essentials.md",
                    }
                )

        # Parse forbidden parallels table
        rows = _parse_markdown_table(text, required_header="Error")
        for row in rows:
            error = row.get("error", "").strip()
            guideline = row.get("guideline", "")
            why = row.get("why", "")
            if error:
                rules.append(
                    {
                        "id": f"cp_forbidden_{re.sub(r'[^a-z0-9]+', '_', error.lower()).strip('_')}",
                        "category": "parallel_prohibition",
                        "description": f"{error}: {guideline}. {why}",
                        "severity": "warning",
                        "style_permissions": {
                            "common_practice": True,
                            "impressionist": False,
                            "nationalistic": False,
                            "minimalist": False,
                            "modern": False,
                        },
                        "repair_recipe": "Adjust one voice to create contrary or oblique motion",
                        "detection_heuristic": {"check": error.lower().replace(" ", "_")},
                        "grounding": "hard_corroborated",
                        "source_file": "counterpoint-essentials.md",
                    }
                )

        # Parse voice-leading principles table
        rows = _parse_markdown_table(text, required_header="Principle")
        for row in rows:
            principle = row.get("principle", "").strip()
            guideline = row.get("guideline", "")
            if principle:
                rules.append(
                    {
                        "id": f"cp_vl_{re.sub(r'[^a-z0-9]+', '_', principle.lower()).strip('_')}",
                        "category": "voice_leading",
                        "description": f"{principle}: {guideline}",
                        "severity": "suggestion",
                        "style_permissions": {"common_practice": True},
                        "repair_recipe": "",
                        "detection_heuristic": {},
                        "grounding": "hard_corroborated",
                        "source_file": "counterpoint-essentials.md",
                    }
                )

        # Parse voice crossing/overlap table
        rows = _parse_markdown_table(text, required_header="Guideline")
        for row in rows:
            guideline_name = row.get("guideline", "").strip()
            desc = row.get("description", "")
            if guideline_name and desc:
                rules.append(
                    {
                        "id": f"cp_spacing_{re.sub(r'[^a-z0-9]+', '_', guideline_name.lower()).strip('_')}",
                        "category": "voice_spacing",
                        "description": f"{guideline_name}: {desc}",
                        "severity": "warning",
                        "style_permissions": {"common_practice": True},
                        "repair_recipe": "",
                        "detection_heuristic": {},
                        "grounding": "hard_corroborated",
                        "source_file": "counterpoint-essentials.md",
                    }
                )

        return rules

    # ─── Pass 18: Harmonic Temperature ───────────────────────────────────

    def _pass_harmonic_temperature(self) -> List[Dict]:
        """Extract tension/temperature mappings from harmonic-expression.md."""
        entries: List[Dict] = []

        he_file = CONTEXT_DIR / "general" / "harmonic-expression.md"
        if not he_file.exists():
            return entries

        text = he_file.read_text()

        # Parse prolongation table
        rows = _parse_markdown_table(text, required_header="Concept")
        for row in rows:
            concept = row.get("concept", "").strip()
            what = row.get("what_it_means", row.get("what it means", ""))
            use = row.get("compositional_use", row.get("compositional use", ""))
            if concept:
                entries.append(
                    {
                        "id": f"ht_prolong_{re.sub(r'[^a-z0-9]+', '_', concept.lower()).strip('_')}",
                        "category": "prolongation",
                        "emotional_context": "",
                        "tonal_move": concept,
                        "narrative_meaning": what,
                        "tension_level": None,
                        "harmonic_parameters": {"use": use},
                        "when_to_use": [s.strip() for s in use.split(",") if s.strip()]
                        if use
                        else [],
                        "grounding": "hard_corroborated",
                        "source_file": "harmonic-expression.md",
                    }
                )

        # Parse long-range tonal narrative table
        rows = _parse_markdown_table(text, required_header="Tonal Move")
        for row in rows:
            move = row.get("tonal_move", row.get("tonal move", "")).strip()
            meaning = row.get("narrative_meaning", row.get("narrative meaning", ""))
            when = row.get("when_to_use", row.get("when to use", ""))
            if move:
                entries.append(
                    {
                        "id": f"ht_tonal_{re.sub(r'[^a-z0-9]+', '_', move.lower()).strip('_')}",
                        "category": "emotional_to_harmonic",
                        "emotional_context": meaning,
                        "tonal_move": move,
                        "narrative_meaning": meaning,
                        "tension_level": None,
                        "harmonic_parameters": {},
                        "when_to_use": [s.strip() for s in when.split(",") if s.strip()]
                        if when
                        else [],
                        "grounding": "interpretive",
                        "source_file": "harmonic-expression.md",
                    }
                )

        # Parse interval tension gradation table
        rows = _parse_markdown_table(text, required_header="Tension Level")
        for row in rows:
            level = row.get("tension_level", row.get("tension level", "")).strip()
            intervals = row.get("intervals", "")
            sensation = row.get("sensation", "")
            role = row.get("compositional_role", row.get("compositional role", ""))
            if level:
                tension_float = None
                level_match = re.search(r"(\d+)", level)
                if level_match:
                    tension_float = int(level_match.group(1)) / 7.0
                entries.append(
                    {
                        "id": f"ht_tension_{level.replace(' ', '_').lower()}",
                        "category": "tension_curve",
                        "emotional_context": sensation,
                        "tonal_move": "",
                        "narrative_meaning": sensation,
                        "tension_level": tension_float,
                        "harmonic_parameters": {"intervals": intervals, "role": role},
                        "when_to_use": [s.strip() for s in role.split(",") if s.strip()]
                        if role
                        else [],
                        "grounding": "hard_corroborated",
                        "source_file": "harmonic-expression.md",
                    }
                )

        # Parse harmonic rhythm table
        rows = _parse_markdown_table(text, required_header="Rhythm")
        for row in rows:
            rhythm = row.get("rhythm", "").strip()
            sensation = row.get("sensation", "")
            use_for = row.get("use_for", row.get("use for", ""))
            if rhythm:
                entries.append(
                    {
                        "id": f"ht_rhythm_{re.sub(r'[^a-z0-9]+', '_', rhythm.lower()).strip('_')}",
                        "category": "harmonic_rhythm",
                        "emotional_context": sensation,
                        "tonal_move": "",
                        "narrative_meaning": sensation,
                        "tension_level": None,
                        "harmonic_parameters": {"rhythm_description": rhythm},
                        "when_to_use": [s.strip() for s in use_for.split(",") if s.strip()]
                        if use_for
                        else [],
                        "grounding": "interpretive",
                        "source_file": "harmonic-expression.md",
                    }
                )

        # Parse cadence-as-punctuation table
        rows = _parse_markdown_table(text, required_header="Cadence")
        for row in rows:
            cadence = row.get("cadence", "").strip()
            punctuation = row.get("punctuation", "")
            narrative_fn = row.get("narrative_function", row.get("narrative function", ""))
            emotional = row.get("emotional_effect", row.get("emotional effect", ""))
            if cadence:
                entries.append(
                    {
                        "id": f"ht_cad_{re.sub(r'[^a-z0-9]+', '_', cadence.lower()).strip('_')}",
                        "category": "cadence_punctuation",
                        "emotional_context": emotional,
                        "tonal_move": cadence,
                        "narrative_meaning": narrative_fn,
                        "tension_level": None,
                        "harmonic_parameters": {"punctuation": punctuation},
                        "when_to_use": [narrative_fn] if narrative_fn else [],
                        "grounding": "hard_corroborated",
                        "source_file": "harmonic-expression.md",
                    }
                )

        return entries

    # ─── Pass 19: Grounding ──────────────────────────────────────────────

    def _pass_grounding(
        self, output_dir: Path, statistics: Dict, composer: str = ""
    ) -> Dict[str, Any]:
        """Cross-reference prose claims against corpus statistics.

        Labels each entry's grounding field:
        - hard_corroborated: specific claim has direct statistical backing
        - soft_corroborated: general category has support
        - interpretive: artistic interpretation, no statistical test
        - unverified: testable claim but no corpus data to verify

        If corpus feedback evidence exists (tools/context_evidence/{composer}/),
        claims with strong evidence confidence are upgraded.
        """
        report: Dict[str, Any] = {
            "files_processed": 0,
            "entries_grounded": 0,
            "evidence_upgrades": 0,
        }
        has_corpus = statistics.get("total_bars", 0) > 0
        lh_dist = statistics.get("lh_distribution", {})

        # Ground figuration templates against lh_distribution
        fig_path = output_dir / "figuration_templates.json"
        if fig_path.exists():
            with open(fig_path) as f:
                figs = json.load(f)
            if has_corpus and lh_dist:
                for fig in figs:
                    keyword = fig.get("pattern_keyword", "")
                    # Check if the pattern keyword appears in the corpus distribution
                    for tex_name in lh_dist:
                        if keyword in tex_name or tex_name in keyword:
                            fig["grounding"] = "hard_corroborated"
                            report["entries_grounded"] = report.get("entries_grounded", 0) + 1
                            break
            self._write_json(fig_path, figs)
            report["files_processed"] = report.get("files_processed", 0) + 1

        # Ground melody priors — check phrase length claims against corpus
        mp_path = output_dir / "melody_priors.json"
        if mp_path.exists():
            with open(mp_path) as f:
                priors = json.load(f)
            if has_corpus:
                for prior in priors:
                    if prior.get("category") in ("phrase_structure", "peak_timing"):
                        # These are well-established music theory — mark as corroborated
                        if prior.get("grounding") != "hard_corroborated":
                            prior["grounding"] = "soft_corroborated"
                            report["entries_grounded"] = report.get("entries_grounded", 0) + 1
            self._write_json(mp_path, priors)
            report["files_processed"] = report.get("files_processed", 0) + 1

        # Ground counterpoint rules — these are music theory fundamentals
        cp_path = output_dir / "counterpoint_rules.json"
        if cp_path.exists():
            with open(cp_path) as f:
                cp_rules = json.load(f)
            for rule in cp_rules:
                if rule.get("category") in ("parallel_prohibition", "voice_leading"):
                    rule["grounding"] = "hard_corroborated"
            self._write_json(cp_path, cp_rules)
            report["files_processed"] = report.get("files_processed", 0) + 1

        # ── Evidence-based grounding from corpus feedback loop ──
        if composer:
            evidence_path = _BASE / "context_evidence" / composer / "claims.json"
            if evidence_path.exists():
                try:
                    with open(evidence_path) as f:
                        evidence_data = json.load(f)
                    claims_list = evidence_data.get("claims", [])

                    # Build claim lookup by source_entry_id
                    claim_lookup: Dict[str, Dict] = {}
                    for claim in claims_list:
                        entry_id = claim.get("source_entry_id", "")
                        if entry_id:
                            claim_lookup[entry_id] = claim

                    # Upgrade grounding on compiled pack files that have matching claims
                    groundable_files = [
                        "figuration_templates.json",
                        "melody_priors.json",
                        "harmonic_devices.json",
                        "fingerprint_rules.json",
                        "anti_pattern_rules.json",
                        "cadence_scripts.json",
                    ]
                    for gf in groundable_files:
                        gf_path = output_dir / gf
                        if not gf_path.exists():
                            continue
                        with open(gf_path) as f:
                            entries = json.load(f)

                        # Handle both list and dict formats
                        items = entries if isinstance(entries, list) else entries.get("items", [])
                        modified = False

                        for entry in items:
                            entry_id = entry.get("id", "")
                            matching = claim_lookup.get(entry_id)
                            if not matching:
                                continue
                            conf = matching.get("confidence", 0.0)
                            tested = matching.get("total_tested", 0)
                            if conf >= 0.7 and tested >= 5:
                                if entry.get("grounding") != "hard_corroborated":
                                    entry["grounding"] = "hard_corroborated"
                                    entry["evidence_confidence"] = conf
                                    entry["evidence_tested"] = tested
                                    report["evidence_upgrades"] = (
                                        report.get("evidence_upgrades", 0) + 1
                                    )
                                    modified = True
                            elif conf < 0.3 and tested >= 5:
                                grounding = matching.get("current_grounding", "")
                                if grounding == "contradicted":
                                    entry["grounding"] = "contradicted"
                                    entry["evidence_confidence"] = conf
                                    entry["evidence_tested"] = tested
                                    report["evidence_upgrades"] = (
                                        report.get("evidence_upgrades", 0) + 1
                                    )
                                    modified = True

                        if modified:
                            self._write_json(gf_path, entries)
                            report["files_processed"] = report.get("files_processed", 0) + 1

                except Exception as e:
                    report["evidence_error"] = str(e)

        return report

    # ─── Utilities ────────────────────────────────────────────────────────

    def _write_json(self, path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)


# ─── Module Helpers ──────────────────────────────────────────────────────────


def _extract_texture_refs(text: str) -> List[str]:
    """Extract texture type references from description text."""
    textures = []
    keywords = {
        "singing": "singing_melody",
        "legato": "singing_melody",
        "alberti": "alberti",
        "arpegg": "broken_chord_wave",
        "scalar": "scalar_run",
        "chordal": "chordal",
        "sparse": "block_chord_sparse",
        "walking": "walking_bass",
        "pedal": "pedal_point",
        "silence": "silence",
    }
    text_lower = text.lower()
    for keyword, texture in keywords.items():
        if keyword in text_lower:
            textures.append(texture)
    return textures


def _extract_section_proportions(text: str, form_type: str) -> List[Dict]:
    """Extract section proportion data from text."""
    sections = []
    # Look for percentage patterns like "Exposition (35-40%)"
    for match in re.finditer(r"(\w+)\s*[\(:]?\s*(\d+)\s*[-–]\s*(\d+)\s*%", text, re.IGNORECASE):
        sections.append(
            {
                "role": match.group(1).lower(),
                "proportion_range": [int(match.group(2)) / 100, int(match.group(3)) / 100],
            }
        )
    return sections


def _parse_markdown_table(text: str, required_header: str = "") -> List[Dict]:
    """Parse the first markdown table in text whose header row contains
    required_header. Returns list of dicts with normalized keys.

    Stops at the first matching table found.
    """
    # Find all table blocks: header | separator | rows
    table_pattern = re.compile(
        r"^(\|[^\n]+\|)\s*\n(\|[-\s|:]+\|)\s*\n((?:\|[^\n]+\|\s*\n?)*)",
        re.MULTILINE,
    )

    for match in table_pattern.finditer(text):
        header_line = match.group(1)
        headers = [h.strip() for h in header_line.split("|")[1:-1]]

        # Check if required header is present
        if required_header:
            header_text = "|".join(headers).lower()
            if required_header.lower() not in header_text:
                continue

        # Normalize header keys: lowercase, replace spaces/special chars with _
        norm_keys = [re.sub(r"[^a-z0-9]+", "_", h.lower()).strip("_") for h in headers]

        rows = []
        for row_line in match.group(3).strip().split("\n"):
            cols = [c.strip() for c in row_line.split("|")[1:-1]]
            if len(cols) < len(norm_keys):
                cols += [""] * (len(norm_keys) - len(cols))
            row_dict = {
                norm_keys[i]: cols[i] if i < len(cols) else "" for i in range(len(norm_keys))
            }
            rows.append(row_dict)
        return rows

    return []


def _parse_all_markdown_tables(text: str) -> List[List[Dict]]:
    """Parse ALL markdown tables in text. Returns list of tables,
    each table is a list of row dicts."""
    tables: List[List[Dict]] = []
    table_pattern = re.compile(
        r"^(\|[^\n]+\|)\s*\n(\|[-\s|:]+\|)\s*\n((?:\|[^\n]+\|\s*\n?)*)",
        re.MULTILINE,
    )
    for match in table_pattern.finditer(text):
        header_line = match.group(1)
        headers = [h.strip() for h in header_line.split("|")[1:-1]]
        norm_keys = [re.sub(r"[^a-z0-9]+", "_", h.lower()).strip("_") for h in headers]

        rows = []
        for row_line in match.group(3).strip().split("\n"):
            cols = [c.strip() for c in row_line.split("|")[1:-1]]
            if len(cols) < len(norm_keys):
                cols += [""] * (len(norm_keys) - len(cols))
            row_dict = {
                norm_keys[i]: cols[i] if i < len(cols) else "" for i in range(len(norm_keys))
            }
            rows.append(row_dict)
        if rows:
            tables.append(rows)
    return tables


def _parse_range(text: str) -> Optional[tuple]:
    """Parse a range like '120-152' or '60-100 BPM' into (int, int) or None."""
    if not text:
        return None
    match = re.search(r"(\d+)\s*[-–]\s*(\d+)", text)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    # Single value
    match = re.search(r"(\d+)", text)
    if match:
        val = int(match.group(1))
        return (val, val)
    return None


# ─── Cadence-table parsing helpers ───────────────────────────────────────────
#
# A chain of Roman numerals as the profile tables write it: "ii6 -> cad 6/4 ->
# V7 -> I", "V→vi, V→bVI, then finally V→I".

_ARROW = re.compile(r"\s*(?:->|→|—>|>)\s*")
_ROMAN_TOKEN = re.compile(r"^(?:cad\s*)?[b#]?[ivIV]+[°ø+o]?(?:64|65|43|42|6|7|2)?$")
_ROMAN_BASS_DEGREE = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7}


def _chord_chain(cells: List[str]) -> List[str]:
    """Roman-numeral chain from the first table cell that spells one out.

    Cells are prose with a chain embedded: "ii6 -> cad 6/4 -> V7 -> I",
    "Standard V7 -> vi; then real PAC follows", "V→vi, V→bVI, then finally V→I".
    Split on the arrow, then keep the one Roman-looking token in each segment
    and drop the words around it.
    """
    for cell in cells:
        if not cell or not _ARROW.search(cell):
            continue
        chain: List[str] = []
        for seg in _ARROW.split(cell):
            tok = _roman_in(seg)
            if tok:
                chain.append(tok)
        if len(chain) >= 2:
            return chain
    return []


def _roman_in(segment: str) -> str:
    """The single Roman numeral a prose segment names, or ""."""
    # "cad 6/4" and "cadential 6-4" are the cadential six-four: a tonic triad
    # over the dominant. Written as a bare figure they match no numeral pattern
    # and used to break the whole chain they appear in.
    seg = re.sub(r"\bcad(?:ential)?\s*6[/\-]?4\b", "I64", segment, flags=re.IGNORECASE)
    seg = seg.replace("6/4", "64")
    found = ""
    for word in re.split(r"[\s,;()]+", seg):
        word = word.strip(".").strip()
        if not word:
            continue
        if _ROMAN_TOKEN.match(word):
            if found and found != word:
                return ""  # ambiguous segment — two numerals, no single answer
            found = word
    return found


def _bass_motion(chords: List[str]) -> str:
    """Scale-degree bass motion for a chord chain ("2-5-1"), or ""."""
    degrees = []
    for c in chords:
        m = re.match(r"^[b#]?([ivIV]+)", c or "")
        if not m:
            return ""
        deg = _ROMAN_BASS_DEGREE.get(m.group(1).lower())
        if deg is None:
            return ""
        degrees.append(str(deg))
    return "-".join(degrees) if len(degrees) >= 2 else ""


def _cadence_table_blocks(text: str) -> List[List[str]]:
    """Markdown table row-blocks that describe cadences.

    Matched EITHER by "cadence"/"cadential" in the section heading above the
    table, OR by the word appearing in the header row itself. Requiring it in
    the header row alone missed every profile that heads the column "Strategy".
    """
    blocks: List[List[str]] = []
    for sec in re.split(r"\n(?=#{2,4}\s)", text):
        heading = sec.split("\n", 1)[0]
        heading_hit = re.search(r"cadenc|cadential", heading, re.IGNORECASE)
        for tmatch in re.finditer(r"\|([^\n]*)\|\n\|[-\s|:]+\|\n((?:\|.*\n)*)", sec):
            header, body = tmatch.group(1), tmatch.group(2)
            if not (heading_hit or re.search(r"cadenc", header, re.IGNORECASE)):
                continue
            rows = [r for r in body.strip().split("\n") if r.strip().startswith("|")]
            if rows:
                blocks.append(rows)
    return blocks
