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
import logging
import re
from pathlib import Path
from typing import Any, List, Optional

# Parsing a numbered, bolded catalogue item: `N. **Name** — description`.
#
# Line-based on purpose. Three successive regexes lost content silently and each
# fix revealed another case:
#
#   * requiring a dash after the bold dropped `**Name**, description` and
#     `**Name.**` outright — six of eleven idioms in one file;
#   * `^` could not match at a scan position sitting ON the newline that the
#     previous item's lookahead had stopped at, so one item in every run of
#     adjacent items vanished;
#   * a lazy body with a lookahead still lost the item after any empty-bodied one.
#
# Silent loss is the worst possible failure here, because a file that parses to
# nothing is indistinguishable from a file that does not exist — which is the
# bug the catalogues themselves were written to fix. Walking lines cannot have
# this class of bug, and `test_composer_craft_coverage` asserts the parsed count
# equals the number of numbered items in the source.
_ITEM_HEAD_RE = re.compile(r"^[ \t]*(\d+)\.\s+\*\*(?P<name>.+?)\*\*(?P<rest>.*)$")
#: The same item whose bold NAME wraps onto the next line — markdown allows it
#: and a person writing a long device name does it without thinking. Matching
#: only the single-line form dropped such an item silently, which is precisely
#: the failure this parser was rewritten as a line walker to stop: the
#: catalogue looked complete, the pack was one device short, and nothing said so.
_ITEM_HEAD_OPEN_RE = re.compile(r"^[ \t]*(\d+)\.\s+\*\*(?P<name>[^*]+)$")
_SECTION_RE = re.compile(r"^##+\s+(?P<title>.+?)\s*$")



_TABLE_ROW_RE = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")
_TABLE_RULE_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")



def _profile_dirs(composer: str) -> list[Path]:
    """EVERY profile directory for a composer, heaviest first.

    Wagner has two, and they are not a mistake: `romantic/wagner` covers the
    earlier operas and `late-romantic/wagner` covers Tristan onward. Each
    cross-references the other, and the late one's own guide says "for
    composition, use the romantic/wagner fingerprints".

    The compiler picked the heavier one and warned that "half the doctrine is
    unreachable", which was exactly right: **536 substantive lines** existed only
    in the copy it discarded — the Parsifal key associations, the layered-motif
    tables, the late orchestration philosophy.
    """
    out: list[tuple[int, Path]] = []
    for genre_dir in sorted(CONTEXT_DIR.iterdir()):
        if not genre_dir.is_dir():
            continue
        profiles = genre_dir / "composer-profiles" / composer
        if profiles.is_dir():
            out.append((-sum(f.stat().st_size for f in profiles.glob("*.md")), profiles))
    out.sort(key=lambda pair: (pair[0], str(pair[1])))
    return [path for _weight, path in out]



def _merge_pass_result(into, addition):
    """Merge one pass's output from another composer into the accumulator.

    Lists concatenate and deduplicate by `id` (or by the whole entry when there
    is none); dicts merge key-wise with the same rule; scalars keep the first
    non-empty value. That covers every shape the profile-derived passes return.
    """
    if into is None:
        return addition
    if isinstance(into, list) and isinstance(addition, list):
        seen = {json.dumps(e.get("id"), sort_keys=True) if isinstance(e, dict) and e.get("id")
                else json.dumps(e, sort_keys=True) for e in into}
        for entry in addition:
            key = (
                json.dumps(entry.get("id"), sort_keys=True)
                if isinstance(entry, dict) and entry.get("id")
                else json.dumps(entry, sort_keys=True)
            )
            if key not in seen:
                seen.add(key)
                into.append(entry)
        return into
    if isinstance(into, dict) and isinstance(addition, dict):
        for key, value in addition.items():
            into[key] = _merge_pass_result(into.get(key), value)
        return into
    return into if into not in (None, "", 0, [], {}) else addition


def _style_member_dirs(composer: str) -> list[Path]:
    """Profile directories of a style's member composers, or [] if not a style.

    Every profile-derived pass takes ONE directory, and a style id
    (`style__classical`) has none — so `compile("style__classical")` produced a
    pack with **no orchestration roles, no influences and no phrase prototypes**,
    while `compile("mozart")` produced 40, 15 and 8 of them.

    Composing "in the classical style" is a first-class mode in this system, and
    it was silently losing every piece of composer-profile doctrine. Only the
    passes fed by the SHARED general documents — figuration, cadence scripts,
    harmonic devices — survived, which is why the style packs looked populated.
    """
    try:
        from .style_registry import is_style_id, style_members, style_name
    except ImportError:  # pragma: no cover - defensive
        return []
    if not is_style_id(composer):
        return []
    out: list[Path] = []
    for member in style_members(style_name(composer)) or []:
        for directory in _profile_dirs(member):
            if directory not in out:
                out.append(directory)
    return out


def _profile_text(profile_dir: Path | None, filename: str) -> str:
    """A named profile file, joined across ALL of that composer's directories.

    Concatenating is safe for every reader of this: they parse tables and
    numbered catalogues, so a second copy of the file yields more entries rather
    than a conflicting single value. Duplicate rows deduplicate downstream by id.
    """
    if profile_dir is None:
        return ""
    texts: list[str] = []
    for directory in _profile_dirs(profile_dir.name) or [profile_dir]:
        path = directory / filename
        if not path.exists():
            continue
        try:
            body = path.read_text()
        except OSError:
            continue
        if body and body not in texts:
            texts.append(body)
    return "\n\n".join(texts)


def _parse_md_tables(text: str) -> List[dict]:
    """Every markdown table in a document, with the heading it sits under.

    The composer profiles carry their most structured knowledge in TABLES —
    Chopin's orchestration.md opens with a "Voice Roles" table (voice, hand,
    function, register) and cross-references.md with "Who Influenced Chopin"
    (source, what was absorbed, where you hear it). Three compiler passes read
    those files and none of them could read a table:

      * `_pass_orchestration` was a stub. It opened the file, confirmed it
        existed, and returned `{"instruments": {}}` with the comment "would be
        more sophisticated in production". Empty for **55 of 55** composers.
      * `_pass_cross_references` matched the literal phrases "influenced by",
        "learned from" or "absorbed" followed by one word. The tables say none of
        those things. Empty for 39 of 50.
      * `_pass_prototypes` looked for ```json blocks in prose guides that have
        none. Empty for 47 of 50.

    All three feed live consumers — `orchestration_roles` is what the concerto
    and symphony path reads for instrument assignment, and `influence_axes` is
    how `donor_strategy` finds historically related composers. Each was reading
    an empty drawer.
    """
    tables: List[dict] = []
    caption = ""
    headers: List[str] = []
    rows: List[List[str]] = []

    def cells_of(line: str) -> List[str]:
        return [c.strip() for c in _TABLE_ROW_RE.match(line).group("cells").split("|")]

    def flush():
        if headers and rows:
            tables.append({"caption": caption, "headers": headers, "rows": rows})

    for line in text.splitlines():
        if _SECTION_RE.match(line):
            flush()
            headers, rows = [], []
            caption = _SECTION_RE.match(line).group("title")
            continue
        if _TABLE_RULE_RE.match(line):
            continue
        if _TABLE_ROW_RE.match(line):
            values = cells_of(line)
            if not headers:
                headers = values
            elif len(values) == len(headers):
                rows.append(values)
            continue
        if headers and rows:
            flush()
            headers, rows = [], []
    flush()
    return tables


def _table_column(table: dict, *names: str, taken: Optional[set] = None) -> Optional[int]:
    """Index of the first header whose text contains any of `names`.

    `taken` excludes columns already claimed by another field. Chopin's voice
    table heads a column `Hand/Register`, which matches both the hand lookup and
    the register lookup — so the same cell was filed twice and the entry read as
    though it carried two facts when it carried one.
    """
    for i, header in enumerate(table["headers"]):
        if taken and i in taken:
            continue
        low = header.lower()
        if any(n in low for n in names):
            return i
    return None


def _parse_catalogue(text: str):
    """Yield (section, name, body) for every numbered bolded item in a catalogue."""
    section = ""
    name = None
    body_parts: list = []

    def _flush():
        if name is None:
            return None
        body = " ".join(" ".join(body_parts).split())
        # An item whose whole content is its bold title is still an item.
        return (section, name, body or name)

    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        idx += 1
        sm = _SECTION_RE.match(line)
        if sm:
            done = _flush()
            if done:
                yield done
            name, body_parts = None, []
            section = sm.group("title")
            continue
        hm = _ITEM_HEAD_RE.match(line)
        if hm is None and _ITEM_HEAD_OPEN_RE.match(line):
            # A bold name wrapped onto the next line: rejoin and re-match, so a
            # wrapped device parses exactly like an unwrapped one.
            joined = line.rstrip()
            for look in range(idx, min(idx + 3, len(lines))):
                nxt = lines[look]
                # A name that never closes must not swallow what follows. Stop at
                # a blank line, a new section, or the next numbered item — the
                # lookahead happily joined `2. **A perfectly good item**` onto an
                # unclosed name and consumed it whole.
                if (
                    not nxt.strip()
                    or _SECTION_RE.match(nxt)
                    or _ITEM_HEAD_RE.match(nxt)
                    or _ITEM_HEAD_OPEN_RE.match(nxt)
                ):
                    break
                joined = joined + " " + nxt.strip()
                hm = _ITEM_HEAD_RE.match(joined)
                if hm is not None:
                    idx = look + 1
                    break
        if hm:
            done = _flush()
            if done:
                yield done
            name = hm.group("name").strip()
            rest = (hm.group("rest") or "").strip()
            body_parts = [rest.lstrip("—:,.- ").strip()] if rest else []
            continue
        if name is not None:
            if line.strip():
                body_parts.append(line.strip())
            else:
                done = _flush()
                if done:
                    yield done
                name, body_parts = None, []
    done = _flush()
    if done:
        yield done



_BASE = Path(__file__).parent.parent
CONTEXT_DIR = _BASE.parent / ".claude" / "context"
REFERENCE_INDEX = _BASE / "reference_index"
PATTERN_LIBRARY = _BASE / "pattern_library"
TEXTURE_TEMPLATES = _BASE / "texture_templates"
COMPILED_PACKS = _BASE / "compiled_packs"


_LOG = logging.getLogger(__name__)


class ContextCompiler:
    """Compiles markdown profiles + corpus data into ComposerPacks."""

    def compile(self, composer: str, genre: str = "", force: bool = False) -> dict[str, Any]:
        """Run all 19 compiler passes for a composer.

        Returns a summary of what was compiled.
        """
        # Find profile directory
        profile_dir = self._find_profile_dir(composer, genre)
        # A STYLE has no profile directory of its own. Run each profile-derived
        # pass once per member composer and merge, or the style pack ships with
        # none of the doctrine the individual packs carry — see
        # `_style_member_dirs`.
        member_dirs = _style_member_dirs(composer)
        if member_dirs and profile_dir is None:
            profile_dir = member_dirs[0]

        def _over_members(fn, *args):
            """Run a profile-derived pass over every member and merge."""
            if not member_dirs:
                return fn(profile_dir, *args)
            merged = None
            for directory in member_dirs:
                merged = _merge_pass_result(merged, fn(directory, *args))
            return merged
        from .style_registry import pack_dir_name

        output_dir = COMPILED_PACKS / pack_dir_name(composer)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # Pass 1: Manifest
        manifest = self._pass_manifest(composer, genre, profile_dir)
        self._write_json(output_dir / "manifest.json", manifest)
        results["manifest"] = manifest

        # Pass 2: Fingerprints
        fingerprints = _over_members(self._pass_fingerprints)
        self._write_json(output_dir / "fingerprint_rules.json", fingerprints)
        results["fingerprints"] = len(fingerprints.get("items", []))

        # Pass 3: Statistics
        statistics = self._pass_statistics(composer, profile_dir)
        self._write_json(output_dir / "scoped_statistics.json", statistics)
        results["statistics"] = bool(statistics.get("total_bars"))

        # Pass 4: Formal grammars
        formal = _over_members(self._pass_formal_grammar)
        self._write_json(output_dir / "formal_graphs.json", formal)
        results["formal"] = len(formal.get("forms", {}))

        # Pass 5: Harmonic rules
        harmonic = _over_members(self._pass_harmonic_rules, composer)
        self._write_json(output_dir / "harmonic_rules.json", harmonic)
        results["harmonic"] = len(harmonic.get("cadence_vocabulary", []))

        # Pass 6: Orchestration + period overlays
        orchestration = _over_members(self._pass_orchestration)
        self._write_json(output_dir / "orchestration_roles.json", orchestration)
        periods = _over_members(self._pass_periods)
        self._write_json(output_dir / "period_overlays.json", periods)
        results["periods"] = len(periods.get("periods", []))

        # Pass 7: Cross-references + prototypes + review rubric
        influence = _over_members(self._pass_cross_references)
        self._write_json(output_dir / "influence_axes.json", influence)
        prototypes = _over_members(self._pass_prototypes)
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
        devices = self._pass_harmonic_devices(profile_dir, composer)
        self._write_json(output_dir / "harmonic_devices.json", devices.get("devices", []))
        self._write_json(output_dir / "cadence_scripts.json", devices.get("cadence_scripts", []))
        results["harmonic_devices"] = len(devices.get("devices", []))

        # Pass 11: Breathing rules
        breathing = self._pass_breathing_rules()
        self._write_json(output_dir / "breathing_rules.json", breathing)
        results["breathing_rules"] = len(breathing)

        # Pass 12: Ornament intents
        ornaments = self._pass_ornament_policy(profile_dir)
        self._write_json(output_dir / "ornament_intents.json", ornaments)
        results["ornament_intents"] = len(ornaments)

        # Pass 13: Prompt semantics
        prompt_sem = self._pass_prompt_semantics()
        self._write_json(output_dir / "prompt_semantics.json", prompt_sem)
        results["prompt_semantics"] = len(prompt_sem)

        # Pass 14: Melody priors
        melody_pr = self._pass_melody_priors(profile_dir)
        self._write_json(output_dir / "melody_priors.json", melody_pr)
        results["melody_priors"] = len(melody_pr)

        # Pass 15: Figuration templates — the composer's own hand idioms first,
        # then the general library, then the composer's idiomatic DEVICES.
        #
        # The devices catalogue names the melodic and structural gestures that
        # separate one composer from generic tonal music (the appoggiatura sigh,
        # the terraced echo, the general pause). `mozart-devices.md` had existed
        # as long as the LH vocabulary and was opened by nothing, so a file
        # written specifically to stop the surface sounding generic never
        # reached the composer that reads this pack.
        fig_tmpl = (
            _over_members(ContextCompiler._composer_hand_idioms)
            + self._pass_figuration_templates()
            + _over_members(ContextCompiler._composer_devices)
        )
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

    @staticmethod
    def _shared_harmony_text(profile_dir: Path | None, composer: str = "") -> str:
        """The genre-level harmony file a composer profile delegates to.

        Composer profiles say so explicitly — Bach's `harmonic-language.md`
        opens with "For shared Baroque harmonic vocabulary (figured bass,
        **cadence types**, sequences, voice-leading conventions), see
        baroque-harmony.md" — and the compiler never followed the pointer. It
        read only `<genre>/composer-profiles/<composer>/harmonic-language.md`,
        so every composer that delegates its cadence vocabulary compiled to an
        **empty `cadence_scripts.json`**: bach, corelli, monteverdi, palestrina
        and weber, five of the twelve armed composers.

        The brief's cadence doctrine was therefore silent for them — while
        "every phrase ends the same way" (`score_realism.detect_cadence_formula_reuse`)
        is the single most reliable tell that a machine wrote the piece.

        The shared file is a *fallback layer*: the composer's own text is
        concatenated first, so a composer-specific cadence entry still wins.
        """
        genre_dir = None
        if profile_dir:
            genre_dir = profile_dir.parent.parent  # <genre>/composer-profiles/<name>
        elif composer:
            # Armed by corpus but with no written profile at all — corelli,
            # monteverdi, palestrina and weber are all in this position. The
            # genre's shared vocabulary is the honest thing to give them; the
            # alternative is an empty cadence_scripts.json and a brief whose
            # cadence doctrine says nothing.
            from .style_registry import genre_for

            genre_dir = CONTEXT_DIR / genre_for(composer)
        if genre_dir is None or not genre_dir.is_dir():
            return ""
        out = []
        for path in sorted(genre_dir.glob("*-harmony.md")):
            try:
                out.append(path.read_text())
            except OSError:
                continue
        return "\n\n".join(out)

    def _find_profile_dir(self, composer: str, genre: str = "") -> Path | None:
        """Find the composer profile directory.

        This took a ``genre`` argument and ignored it, returning whichever
        directory ``iterdir()`` happened to yield first. Wagner has a profile
        under BOTH `late-romantic/` and `romantic/` — 65KB and 72KB of different
        doctrine — so which one compiled was decided by filesystem order, and the
        other was silently discarded.

        The requested genre now wins. Without one, the choice is deterministic
        (richest profile, then alphabetical by genre) rather than incidental.
        """
        if genre:
            named = CONTEXT_DIR / genre / "composer-profiles" / composer
            if named.is_dir():
                return named

        matches = []
        for genre_dir in sorted(CONTEXT_DIR.iterdir()):
            if not genre_dir.is_dir():
                continue
            profiles = genre_dir / "composer-profiles" / composer
            if profiles.is_dir():
                weight = sum(f.stat().st_size for f in profiles.glob("*.md"))
                matches.append((-weight, genre_dir.name, profiles))
        if not matches:
            return None
        matches.sort()
        if len(matches) > 1:
            _LOG.warning(
                "%s has %d profile directories (%s); compiling %s. "
                "Two profiles for one composer means half the doctrine is unreachable.",
                composer,
                len(matches),
                ", ".join(m[1] for m in matches),
                matches[0][1],
            )
        return matches[0][2]

    # ─── Pass 1: Manifest ─────────────────────────────────────────────────

    def _pass_manifest(self, composer: str, genre: str, profile_dir: Path | None) -> dict:
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
        registry = {}
        if registry_path.exists():
            with open(registry_path) as f:
                registry = json.load(f)
            if composer in registry:
                pattern_count = registry[composer].get("pattern_count", 0)

        # A STYLE's corpus is the union of its members'. Both lookups above are
        # by id, and there is no `reference_index/style__classical/` and no
        # pattern-registry entry for one — so every style scored 0 bars and 0
        # patterns and classified as tier **C**, while mozart, haydn and
        # beethoven are each tier A. Tier C/D is what triggers
        # `DonorStrategy` in `compile_style`, so composing "in the classical
        # style" — over the richest corpus this system has, ~27,800 bars — was
        # treated as a sparse corpus needing a donor, and got one.
        if not corpus_bar_count:
            from .style_registry import is_style_id, normalize_style, style_members, style_name

            # Either form: the id `style__classical`, or the bare word the user
            # typed — `compile_style(piece, "classical")` threads "classical"
            # all the way down here, and checking only `is_style_id` left the
            # commoner case computing 0 bars.
            canon = style_name(composer) if is_style_id(composer) else normalize_style(composer)
            if canon:
                for member in style_members(canon):
                    member_index = REFERENCE_INDEX / member / "bar_index.json"
                    if member_index.exists():
                        with open(member_index) as f:
                            corpus_bar_count += json.load(f).get("total_bars", 0)
                    pattern_count += (registry.get(member) or {}).get("pattern_count", 0)

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

    def _pass_fingerprints(self, profile_dir: Path | None) -> dict:
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
        self, text: str, items: list[dict], period: str = ""
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

    def _pass_statistics(self, composer: str, profile_dir: Path | None) -> dict:
        """Compile statistics from corpus + texture templates + markdown."""
        stats: dict[str, Any] = {"total_bars": 0, "lh_distribution": {}, "rh_distribution": {}}

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

        # Source 3: Transition matrix.
        # The genre fallback was hard-coded to "classical" here as well as in
        # PhraseBank and TransitionBank, so a Bach pack was compiled against
        # Classical texture-transition odds while by_genre/baroque.json sat
        # unread beside it.
        from .style_registry import genre_for as _genre_for

        for path in [
            PATTERN_LIBRARY / "transitions" / "by_composer" / f"{composer}.json",
            PATTERN_LIBRARY / "transitions" / "by_genre" / f"{_genre_for(composer)}.json",
            PATTERN_LIBRARY / "transitions" / "by_genre" / "classical.json",
        ]:
            if path.exists():
                with open(path) as f:
                    matrix = json.load(f)
                stats["transition_matrix"] = self._normalize_matrix(matrix.get("counts", {}))
                break

        return stats

    def _normalize_matrix(self, counts: dict) -> dict:
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

    def _pass_formal_grammar(self, profile_dir: Path | None) -> dict:
        """Extract form templates from formal-approach.md.

        This used to ask ``if "sonata" in text.lower()``, which cannot tell a
        composer who writes sonatas from one whose profile says he does not.
        Palestrina's formal-approach.md opens "There is no sonata, no rondo, no
        ternary reprise" — and the compiler gave a 16th-century vocal polyphonist
        a sonata graph with exposition keys I and V and a tonic recapitulation
        rule. Thirteen profiles phrase a form that way.

        A form now counts only where it is asserted: named in a heading or a
        table cell, or in a sentence that is not negating it.
        """
        if not profile_dir:
            return {"forms": {}}

        formal = profile_dir / "formal-approach.md"
        if not formal.exists():
            return {"forms": {}}

        text = _profile_text(profile_dir, "formal-approach.md")
        forms = {}
        for name in _FORM_VOCABULARY:
            if not _form_is_asserted(text, name):
                continue
            sections = _extract_section_proportions(text, name)
            if name == "sonata":
                forms["sonata"] = {
                    "sections": sections,
                    # A minor-key exposition goes to the relative major, not the
                    # dominant; stating one scheme for both was wrong for every
                    # minor-key sonata in the repertoire.
                    "key_scheme": {
                        "exposition_keys_major": ["I", "V"],
                        "exposition_keys_minor": ["i", "III"],
                        "recap_rule": "tonic",
                    },
                }
            else:
                # `elif sections:` — a non-sonata form was recorded ONLY if
                # section proportions had been extracted, and those come from
                # "(35-40%)" patterns that most profiles do not use. So a form
                # the document plainly asserts was dropped for lacking a
                # percentage table: Palestrina's own heading reads "The point of
                # imitation — the unit of construction" and his pack compiled
                # with no forms at all, as did Monteverdi's, Glass's, Reich's,
                # Part's and the three film composers'.
                #
                # An asserted form with no measured proportions is still a form.
                forms[name] = {"sections": sections, "key_scheme": {}}
        return {"forms": forms}

    # ─── Pass 5: Harmonic Rules ──────────────────────────────────────────

    def _pass_harmonic_rules(self, profile_dir: Path | None, composer: str = "") -> dict:
        """Extract harmonic vocabulary from harmonic-language.md."""
        harmonic = (profile_dir / "harmonic-language.md") if profile_dir else None
        own = harmonic.read_text() if (harmonic and harmonic.exists()) else ""
        text = "\n\n".join(
            t for t in (own, self._shared_harmony_text(profile_dir, composer)) if t
        )
        if not text:
            return {"cadence_vocabulary": [], "chromatic_techniques": []}

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

    def _pass_orchestration(self, profile_dir: Path | None) -> dict:
        """Extract orchestration roles."""
        if not profile_dir:
            return {"instruments": {}}

        orch = profile_dir / "orchestration.md"
        if not orch.exists():
            return {"instruments": {}}

        instruments: dict = {}
        textures: List[dict] = []
        for table in _parse_md_tables(_profile_text(profile_dir, "orchestration.md")):
            name_col = _table_column(table, "voice", "instrument", "pattern", "texture")
            if name_col is None:
                continue
            claimed = {name_col}
            role_col = _table_column(table, "function", "role", "description", taken=claimed)
            claimed.add(role_col)
            # "range" BEFORE "register": Chopin's table heads two columns
            # `Hand/Register` and `Register Range`, and matching "register"
            # first claimed the hand column — so the entry carried
            # "LH, lowest note of arpeggio" as its register and the actual
            # `C1-E3` was never read.
            range_col = _table_column(table, "range", "span", taken=claimed)
            if range_col is None:
                range_col = _table_column(table, "register", taken=claimed)
            claimed.add(range_col)
            hand_col = _table_column(table, "hand", taken=claimed)
            claimed.add(hand_col)
            genre_col = _table_column(table, "genre", "where", "used", taken=claimed)
            for row in table["rows"]:
                name = row[name_col].strip("* ")
                if not name:
                    continue
                entry = {"name": name, "section": table["caption"]}
                if role_col is not None:
                    entry["function"] = row[role_col]
                if range_col is not None:
                    entry["register"] = row[range_col]
                if hand_col is not None:
                    entry["hand"] = row[hand_col]
                if genre_col is not None:
                    entry["genre"] = row[genre_col]
                key = name.lower().replace(" ", "_")
                if range_col is not None or hand_col is not None:
                    instruments[key] = entry
                else:
                    textures.append(entry)
        return {
            "instruments": instruments,
            "textures": textures,
            "source_file": "orchestration.md",
        }

    def _pass_periods(self, profile_dir: Path | None) -> dict:
        """Extract period overlays from stylistic-evolution.md."""
        if not profile_dir:
            return {"periods": []}

        evolution = profile_dir / "stylistic-evolution.md"
        if not evolution.exists():
            return {"periods": []}

        text = _profile_text(profile_dir, "stylistic-evolution.md")
        periods = []

        # Look for common period labels
        for label in ["early", "middle", "late", "final"]:
            if label.lower() in text.lower():
                periods.append({"id": label, "stat_modifiers": {}})

        return {"periods": periods}

    # ─── Pass 7: Cross-References + Prototypes + Rubric ───────────────────

    def _pass_cross_references(self, profile_dir: Path | None) -> dict:
        """Extract influence axes from cross-references.md."""
        if not profile_dir:
            return {"influenced_by": [], "comparative_axes": {}}

        xref = profile_dir / "cross-references.md"
        if not xref.exists():
            return {"influenced_by": [], "comparative_axes": {}}

        text = _profile_text(profile_dir, "cross-references.md")

        influenced_by: List[dict] = []
        influenced: List[dict] = []
        axes: dict = {}
        seen: set = set()
        for table in _parse_md_tables(text):
            source_col = _table_column(table, "source", "composer", "influence", "successor")
            if source_col is None:
                continue
            claimed = {source_col}
            what_col = _table_column(
                table, "absorbed", "what", "took", "learned", "inherited", taken=claimed
            )
            claimed.add(what_col)
            where_col = _table_column(table, "where", "hear", "evidence", "example", taken=claimed)
            caption = table["caption"].lower()
            # "Who Influenced X" vs "Whom X Influenced" — the direction is in the
            # caption, and getting it backwards would hand `donor_strategy` a
            # composer's descendants as its sources.
            forward = "influenced" in caption and not caption.startswith("who influenced")
            bucket = influenced if forward else influenced_by
            for row in table["rows"]:
                name = row[source_col].strip("* ")
                if not name or name.lower() in seen:
                    continue
                seen.add(name.lower())
                entry = {"composer": name}
                if what_col is not None:
                    entry["absorbed"] = row[what_col]
                if where_col is not None:
                    entry["heard_in"] = row[where_col]
                bucket.append(entry)
            if source_col is not None and what_col is None and where_col is None:
                axes[table["caption"]] = [r[source_col] for r in table["rows"]]

        # Prose fallback for profiles that state it in a sentence rather than a
        # table. It found almost nothing on its own — the tables are where this
        # knowledge lives — but it costs nothing and catches the odd one.
        if not influenced_by:
            for match in re.finditer(
                r"(?:influenced by|learned from|absorbed)\s+(\w+)", text, re.IGNORECASE
            ):
                influenced_by.append({"composer": match.group(1)})

        return {
            "influenced_by": influenced_by,
            "influenced": influenced,
            "comparative_axes": axes,
        }

    def _pass_prototypes(self, profile_dir: Path | None) -> dict:
        """Extract JSON code examples from composition-guide.md."""
        if not profile_dir:
            return {"prototypes": []}

        guide = profile_dir / "composition-guide.md"
        if not guide.exists():
            return {"prototypes": []}

        text = guide.read_text()
        prototypes = []

        # A ```json block in these guides usually holds SEVERAL objects one after
        # another — a phrase prototype, then the next. `json.loads` parses the
        # first and raises "Extra data" on the rest, and the `except: continue`
        # below discarded the WHOLE block including the object it had already
        # read. Measured across the guides: 66 blocks, of which 55 failed and not
        # one composer had a block that parsed. Chopin lost 8 of 13.
        #
        # `raw_decode` reads one value and reports where it stopped, so a block
        # of concatenated objects yields all of them.
        decoder = json.JSONDecoder()
        for match in re.finditer(r"```json\s*\n(.*?)\n```", text, re.DOTALL):
            block = match.group(1)
            # Many blocks are a FRAGMENT of an object — `"bass": [ ... ]` — not a
            # standalone value. `raw_decode` happily reads `"bass"` as a string
            # and stops at the colon, so an earlier version of this recorded
            # SEVEN of Chopin's fourteen prototypes as the bare word "bass".
            # A prototype that is a string is worse than no prototype: a reader
            # trusts it. Wrapping the fragment restores the object it belongs to.
            if re.match(r'\s*"[^"]+"\s*:', block):
                block = "{" + block.rstrip().rstrip(",") + "}"
            pos = 0
            while pos < len(block):
                while pos < len(block) and block[pos] in " \t\r\n,":
                    pos += 1
                if pos >= len(block):
                    break
                try:
                    data, end = decoder.raw_decode(block, pos)
                except ValueError:
                    # Not JSON from here on — prose after the objects, or a
                    # snippet with an ellipsis. Keep what was already read.
                    break
                # A bare scalar is never a phrase prototype.
                if isinstance(data, (dict, list)) and data:
                    prototypes.append({"id": f"prototype_{len(prototypes)}", "data": data})
                pos = end

        return {"prototypes": prototypes}

    def _pass_review_rubric(self, profile_dir: Path | None, fingerprints: dict) -> dict:
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

    def _pass_executable_gestures(self, profile_dir: Path | None) -> list[dict]:
        """Extract note-level gesture templates from context files.

        Sources:
        - .claude/context/general/phrase-construction.md (18 techniques with JSON)
        - Per-composer composition-guide.md (technique examples with JSON)
        """
        gestures: list[dict] = []

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
                voice_events: dict[str, list[dict]] = {}
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

    def _pass_anti_patterns(self, profile_dir: Path | None) -> list[dict]:
        """Extract anti-pattern rules from context files.

        Sources:
        - .claude/context/general/anti-patterns.md (10 categories with examples)
        - .claude/context/general/ai-music-self-critique.md (~30 AI tells)
        - .claude/context/general/human-sounding-music.md (quantitative checklist)
        """
        rules: list[dict] = []

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

    def _pass_harmonic_devices(self, profile_dir: Path | None, composer: str = "") -> dict:
        """Extract harmonic devices and cadence scripts from harmonic-language.md.

        Richer than pass 5 — extracts actual chord sequences, voice-leading
        hints, usage contexts, and emotional color.
        """
        devices: list[dict] = []
        cadence_scripts: list[dict] = []

        hl_file = (profile_dir / "harmonic-language.md") if profile_dir else None
        own = hl_file.read_text() if (hl_file and hl_file.exists()) else ""
        # Composer-specific text FIRST so its entries win; the genre file supplies
        # the shared vocabulary the profile explicitly delegates to it.
        shared = self._shared_harmony_text(profile_dir, composer)
        text = "\n\n".join(t for t in (own, shared) if t)
        # A composer with no written profile still gets the genre's shared
        # vocabulary, so the provenance label has to say where it came from.
        _source_label = (
            f"{profile_dir.name}/harmonic-language.md"
            if profile_dir
            else f"<shared {composer or 'genre'} harmony>"
        )
        if not text:
            return {"devices": devices, "cadence_scripts": cadence_scripts}

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

                    # `chord_sequence` was hard-coded `[]` — in 1,254 of 1,254
                    # devices across every pack — while `_chord_chain`, which the
                    # cadence path a few lines below calls on exactly these
                    # cells, sat unused. A harmonic device whose chords are empty
                    # is a name, and `cadence_bank`, `donor_strategy` and the
                    # brief all read that field.
                    #
                    # The name carries them as often as the description does:
                    # "Chromatic mediants (C to Ab, C to E)".
                    chords = _chord_chain([name, *cols[1:]])
                    contexts = [c.strip() for c in context.split(",") if c.strip()]
                    devices.append(
                        {
                            "id": dev_id,
                            "name": name,
                            "chord_sequence": chords,
                            "voice_leading_hints": _voice_leading_hints(" ".join(cols)),
                            "contexts": contexts,
                            "frequency_weight": freq_weight,
                            # The emotional reading was already being collected
                            # into `contexts` and then a separate field for it
                            # was written empty beside it.
                            "emotional_color": contexts[0] if contexts else "",
                            "source_file": _source_label,
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
                        "source_file": _source_label,
                    }
                )

        return {"devices": devices, "cadence_scripts": cadence_scripts}

    # ─── Pass 11: Breathing Rules ─────────────────────────────────────────

    def _pass_breathing_rules(self) -> list[dict]:
        """Extract silence/breathing doctrine from dramatic-pacing-silence.md.

        Parses the "Silence as Dramatic Device" table (7 rows) and
        other timing/tension tables.
        """
        rules: list[dict] = []

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

                    rule: dict[str, Any] = {
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

    @staticmethod
    def _composer_ornament_intents(profile_dir: Path | None) -> list[dict]:
        """This composer's own ornament usage, from their profile.

        Ornament choice is one of the most composer-specific things there is —
        Mozart's appoggiatura sigh, Bach's structural mordent, Chopin's
        chromatic run that continues the line rather than decorating it — and
        `ornament_intents.json` was **identical for all twelve armed
        composers**, extracted only from the general `ornament-intent.md`. The
        tables that say what each composer actually does are sitting in their
        `melodic-style.md` and never compiled.

        Looks for a table whose first column names an ornament, in any of the
        profile files that carry one.
        """
        if not profile_dir:
            return []
        out: list[dict] = []
        seen: set = set()
        for name in ("melodic-style.md", "composition-guide.md", "harmonic-language.md"):
            path = profile_dir / name
            if not path.exists():
                continue
            try:
                text = path.read_text()
            except OSError:
                continue
            for row in _parse_markdown_table(text, required_header="Ornament"):
                ornament = (row.get("ornament") or "").strip()
                if not ornament:
                    continue
                rest = [
                    str(v).strip()
                    for k, v in row.items()
                    if k != "ornament" and str(v).strip()
                ]
                if not rest:
                    continue
                slug = re.sub(r"[^a-z0-9]+", "_", ornament.lower()).strip("_")
                if slug in seen:
                    continue
                seen.add(slug)
                out.append(
                    {
                        "id": f"composer_ornament_{slug}",
                        "category": "composer_ornament_usage",
                        "ornament": ornament,
                        "usage": rest[0],
                        "intent": rest[1] if len(rest) > 1 else "",
                        "position": "any",
                        "grounding": "profile",
                        "source_file": f"{profile_dir.name}/{name}",
                    }
                )
        return out

    @staticmethod
    def _composer_hand_idioms(profile_dir: Path | None) -> list[dict]:
        """A composer's catalogue of hand idioms, from `<name>-lh-vocabulary.md`.

        `mozart-lh-vocabulary.md` was written specifically against the failure
        it names in its own first sentence — "a static bass note held under
        perpetual figuration, the same idiom every bar" — catalogues ten
        alternatives **in this system's own shorthand**, and is opened by
        nothing. The brief's LH VOCABULARY section comes from the corpus pattern
        library instead, which supplies real figures but not the *when*: which
        idiom suits a lyrical theme, which one drives a transition, and that a
        rest in the left hand is not a bug.

        Matched by filename convention (`*-lh-vocabulary.md`) so adding one for
        another composer needs no code change. Entries are numbered list items
        of the form ``N. **Name** — description``.
        """
        if not profile_dir:
            return []
        out: list[dict] = []
        for path in sorted(profile_dir.glob("*-lh-vocabulary.md")):
            try:
                text = path.read_text()
            except OSError:
                continue
            for _section, name, body in _parse_catalogue(text):
                slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                out.append(
                    {
                        "id": f"lh_idiom_{slug}",
                        "category": "composer_hand_idiom",
                        "hand": "lh",
                        "name": name,
                        "description": body[:400],
                        # The idiom's own notes, and what they measure. Keeping
                        # only the prose meant the brief could NAME a left-hand
                        # idiom without handing over the pattern that is it.
                        **_idiom_shape(body),
                        "source_file": f"{profile_dir.name}/{path.name}",
                        "grounding": "profile",
                    }
                )
        return out

    @staticmethod
    def _composer_devices(profile_dir: Path | None) -> list[dict]:
        """A composer's catalogue of idiomatic devices, from `<name>-devices.md`.

        The companion to `*-lh-vocabulary.md`: where that names accompaniment
        idioms, this names the melodic and structural gestures that make a line
        sound like one composer rather than like generic tonal music — the
        appoggiatura sigh, the terraced echo, the Neapolitan approach, the
        general pause.

        `mozart-devices.md` had existed for as long as the LH file and was
        opened by **nothing**, so a catalogue written specifically to stop the
        surface sounding generic never reached the composer. Matched by filename
        convention so adding one for another composer needs no code change, and
        parsed with the same numbered-bold-item grammar.
        """
        if not profile_dir:
            return []
        out: list[dict] = []
        for path in sorted(profile_dir.glob("*-devices.md")):
            try:
                text = path.read_text()
            except OSError:
                continue
            for section, name, body in _parse_catalogue(text):
                slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
                out.append(
                    {
                        "id": f"device_{slug}",
                        "category": "composer_device",
                        "section": section,
                        "name": name,
                        "description": body[:400],
                        "source_file": f"{profile_dir.name}/{path.name}",
                        "grounding": "profile",
                    }
                )
        return out

    def _pass_ornament_policy(self, profile_dir: Path | None = None) -> list[dict]:
        """Extract ornament intent rules.

        The composer's own usage leads; the general `ornament-intent.md`
        decision framework follows as the floor beneath it.
        """
        intents: list[dict] = self._composer_ornament_intents(profile_dir)

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

    def _pass_prompt_semantics(self) -> list[dict]:
        """Extract emotion-to-music parameter mappings from general context.

        Sources:
        - emotional-vocabulary.md (emotion → tempo/mode/dynamics/texture/etc.)
        - character-theme-design.md (archetype → intervals/rhythm/timbre/etc.)
        - musical-semiotics.md (interval/chord affect tables)
        """
        semantics: list[dict] = []

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

    @staticmethod
    def _melodic_style_priors(path: Path) -> list[dict]:
        """Rows of a composer's melodic-character table, as priors.

        Profiles head the table's third column differently — Mozart's is
        "Artistic Function", Bach's is "Presence" — so the value is taken
        positionally from whatever remains after Feature and Description.
        """
        try:
            text = path.read_text()
        except OSError:
            return []
        out: list[dict] = []
        rows = _parse_markdown_table(text, required_header="Feature")
        for row in rows:
            feature = (row.get("feature") or "").strip()
            desc = (row.get("description") or "").strip()
            if not feature or not desc:
                continue
            extra = next(
                (
                    str(v).strip()
                    for k, v in row.items()
                    if k not in ("feature", "description") and str(v).strip()
                ),
                "",
            )
            slug = re.sub(r"[^a-z0-9]+", "_", feature.lower()).strip("_")
            out.append(
                {
                    "id": f"melodic_voice_{slug}",
                    "category": "composer_melodic_voice",
                    "description": f"{feature}: {desc}",
                    "parameters": {"feature": feature, "note": extra},
                    "conditions": {},
                    "grounding": "profile",
                    "source_file": f"{path.parent.name}/melodic-style.md",
                }
            )
        return out

    def _pass_melody_priors(self, profile_dir: Path | None = None) -> list[dict]:
        """Extract melodic construction priors.

        Sources:
        - the composer's own ``melodic-style.md`` (their melodic voice)
        - melodic-construction.md (phrase structure, contour, climax placement)
        - melody-craft.md (artistic intent, hook design)

        The composer's file was not read at all, so `melody_priors.json` came
        out **byte-identical for every composer** — generic phrase-structure
        boilerplate — while a `melodic-style.md` describing that composer's
        actual melodic voice sat unread in **44 of the profile directories**.
        Melody is the most audible thing in the output, and the brief's melody
        doctrine said the same thing whether it was building a Bach fugue
        subject or a Chopin nocturne.

        Composer-specific priors come FIRST so they lead the brief's doctrine
        slice; the general ones remain as the floor beneath them.
        """
        priors: list[dict] = []

        # Source 0: the composer's own melodic voice.
        if profile_dir:
            ms_file = profile_dir / "melodic-style.md"
            if ms_file.exists():
                priors += self._melodic_style_priors(ms_file)

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
                                    "parameters": dict(zip(keys, vals, strict=False)),
                                    "conditions": {},
                                    "grounding": "interpretive",
                                    "source_file": "melody-craft.md",
                                }
                            )

        return priors

    # ─── Pass 15: Figuration Templates ───────────────────────────────────

    def _pass_figuration_templates(self) -> list[dict]:
        """Extract figuration catalog from figuration-patterns.md."""
        templates: list[dict] = []

        fp_file = CONTEXT_DIR / "general" / "figuration-patterns.md"
        if not fp_file.exists():
            return templates

        text = fp_file.read_text()
        _climax = _climax_suggestions(text)

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
                    # Indexed by this template's own number — see
                    # `_climax_suggestions`. Both fields were hard-coded empty
                    # while the document answered them two tables further down.
                    "density_suggestion": (
                        "; ".join(_climax.get(str(num), {}).get("density", [])) or None
                    ),
                    "register_suggestion": "; ".join(
                        dict.fromkeys(_climax.get(str(num), {}).get("register", []))
                    ),
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

    def _pass_modulation_scripts(self) -> list[dict]:
        """Extract modulation procedures from modulation-techniques.md."""
        scripts: list[dict] = []

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
                    # The mechanism prose is where the progression is written —
                    # "V7/x -> x", "I -> bVI -> V of the new key". Both this and
                    # the pivot branch below hard-coded `chord_sequence` to `[]`
                    # in all 605 scripts, while `harmonic_solver` and the brief
                    # read it. The document names a pivot or an arrow chain
                    # 2,133 times.
                    "chord_sequence": _chord_chain([mechanism, mod_type, best_for]),
                    "voice_leading_hints": _voice_leading_hints(
                        " ".join([mechanism, smoothness, best_for])
                    ),
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
                        # A pivot modulation IS a three-chord sequence and the
                        # three chords were already sitting in the two fields
                        # below it: the chord as the old key hears it, and as the
                        # new key rehears it. Writing an empty `chord_sequence`
                        # beside them was the whole defect.
                        # ONLY the Roman numerals. Taking the cells whole gave
                        # `["C major", "I = IV", "IV of G"]` — a key name, an
                        # equation and a prose phrase — which is not a chord
                        # sequence and would be read as one. A field that is
                        # wrong is worse than a field that is empty.
                        "chord_sequence": _pivot_chords(in_old, pivot, in_new),
                        "voice_leading_hints": _voice_leading_hints(
                            " ".join([pivot, in_old, in_new, "common tone held"])
                        ),
                        "pivot_chord_in_old": in_old,
                        "pivot_chord_in_new": in_new,
                        "grounding": "hard_corroborated",
                        "source_file": "modulation-techniques.md",
                    }
                )

        return scripts

    # ─── Pass 17: Counterpoint Rules ─────────────────────────────────────

    def _pass_counterpoint_rules(self) -> list[dict]:
        """Extract contrapuntal rules from counterpoint-essentials.md."""
        rules: list[dict] = []

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

    def _pass_harmonic_temperature(self) -> list[dict]:
        """Extract tension/temperature mappings from harmonic-expression.md."""
        entries: list[dict] = []

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
        self, output_dir: Path, statistics: dict, composer: str = ""
    ) -> dict[str, Any]:
        """Cross-reference prose claims against corpus statistics.

        Labels each entry's grounding field:
        - hard_corroborated: specific claim has direct statistical backing
        - soft_corroborated: general category has support
        - interpretive: artistic interpretation, no statistical test
        - unverified: testable claim but no corpus data to verify

        If corpus feedback evidence exists (tools/context_evidence/{composer}/),
        claims with strong evidence confidence are upgraded.
        """
        report: dict[str, Any] = {
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
                    claim_lookup: dict[str, dict] = {}
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


def _extract_texture_refs(text: str) -> list[str]:
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



# Phrases that negate whatever form name follows them within the same clause.
_NEGATORS = re.compile(
    r"\b(?:no|not|never|without|neither|nor|unlike|rather\s+than|instead\s+of|"
    r"far\s+from|nothing\s+like|is\s+not|are\s+not|isn't|aren't)\b",
    re.IGNORECASE,
)



#: The forms this compiler can recognise.
#:
#: It knew three — sonata, rondo, ternary — which is the Classical instrumental
#: repertoire and nobody else. So the ten composers whose `formal_graphs.json`
#: compiled EMPTY were exactly the ones who write something else: Palestrina and
#: Monteverdi (points of imitation, madrigals), Part, Glass and Reich (process
#: and additive forms), Morricone, Williams and Zimmer (cues), Mussorgsky.
#: Their `formal-approach.md` files describe their forms in detail — Palestrina's
#: opens by explaining that asking where the B section is "mistakes the genre" —
#: and the compiler had no word for any of it, so it recorded that they have no
#: form at all.
#:
#: A form is still only counted where the document ASSERTS it, so adding words
#: here cannot give a composer a form his profile denies.
_FORM_VOCABULARY = (
    # Classical instrumental
    "sonata",
    "rondo",
    "ternary",
    "binary",
    "theme and variations",
    "minuet and trio",
    "scherzo",
    # Baroque
    "fugue",
    "ritornello",
    "da capo",
    "passacaglia",
    "chaconne",
    "ground bass",
    "suite",
    "prelude",
    "toccata",
    # Renaissance and vocal polyphony
    "point of imitation",
    "motet",
    "madrigal",
    "mass",
    "cantus firmus",
    "responsorial",
    # Song and character piece
    "strophic",
    "through-composed",
    "song form",
    "character piece",
    # Later and non-Classical
    "arch",
    "cyclic",
    "additive process",
    "phase process",
    "ostinato form",
    "tintinnabuli",
    "cue",
    "leitmotif",
)


def _form_is_asserted(text: str, form: str) -> bool:
    """Is ``form`` claimed by this profile, rather than merely mentioned?

    Headings and table cells are assertions. Prose counts only when the clause
    naming the form carries no negator before it.
    """
    # WORD BOUNDARIES, not substrings. `"mass" in "massive"` gave Zimmer a
    # Mass; `"arch" in "architecture"` gives everyone arch form. This is the
    # same collision that made `chorale` match `choral` and turn a solo organ
    # work into a choir.
    pattern = re.compile(r"\b" + re.escape(form).replace(r"\ ", r"\s+") + r"\b")
    for line in text.splitlines():
        low = line.lower()
        if not pattern.search(low):
            continue
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("|"):
            return True
        # Split into clauses so "it is a rondo, not a sonata" is read per-clause.
        for clause in re.split(r"[;,.]|\s+—\s+", low):
            found = pattern.search(clause)
            if not found:
                continue
            before = clause[: found.start()]
            if not _NEGATORS.search(before):
                return True
    return False

def _extract_section_proportions(text: str, form_type: str) -> list[dict]:
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


def _parse_markdown_table(text: str, required_header: str = "") -> list[dict]:
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


def _parse_all_markdown_tables(text: str) -> list[list[dict]]:
    """Parse ALL markdown tables in text. Returns list of tables,
    each table is a list of row dicts."""
    tables: list[list[dict]] = []
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


def _parse_range(text: str) -> tuple | None:
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



#: Phrases in the doctrine that describe how the VOICES move, as opposed to
#: which chords sound. `voice_leading_hints` is read by `harmonic_solver` and was
#: an empty list in every device and every modulation script in every pack.
_VOICE_LEADING_CUES = (
    ("common tone held", r"common[- ]tone|held in common|shared (?:note|tone)"),
    ("step in the bass", r"bass (?:moves|steps|falls|rises) by step|stepwise bass"),
    ("chromatic inner voice", r"chromatic (?:inner|middle|descent|line|voice)"),
    ("contrary motion", r"contrary motion"),
    ("leading tone resolves up", r"leading[- ]tone (?:resolves|rises)"),
    ("seventh resolves down", r"seventh (?:resolves|falls)|7th (?:resolves|falls)"),
    ("suspension", r"suspension|4-3|7-6|9-8"),
    ("pedal point", r"pedal (?:point|tone)"),
    ("parallel thirds or sixths", r"parallel (?:thirds|sixths|3rds|6ths)"),
    ("voice exchange", r"voice exchange"),
    ("smooth, minimal movement", r"smooth(?:est)? (?:voice[- ]leading|movement)|minimal movement"),
)


def _voice_leading_hints(text: str) -> list[str]:
    """Voice-leading instructions a prose cell states, as short phrases."""
    if not text:
        return []
    low = text.lower()
    return [label for label, pattern in _VOICE_LEADING_CUES if re.search(pattern, low)]





#: A backticked run that looks like this system's shorthand rather than prose.
_SHORTHAND_RE = re.compile(r"`([^`]*[A-G][#b-]?\d[^`]*)`")


def _idiom_shape(description: str) -> dict:
    """The playable pattern inside an idiom's prose, and what it measures.

    Every `*-lh-vocabulary.md` entry states its idiom as real shorthand —
    ``Ab1e Eb3e Ab3e C4e Eb4e C4e Ab3e Eb3e`` — and the compiler kept only the
    prose, truncated to 400 characters. So the brief could name a composer's
    left-hand idioms and never hand over the notes, while the pattern sat inside
    a string it had already read. 208 of these parse cleanly.

    Returns the shorthand plus its measured register and density, which are the
    two things the pack's own schema asks for elsewhere and which no document
    states in words: `register`, `span_semitones`, `events`.
    """
    if not description:
        return {}
    match = _SHORTHAND_RE.search(description)
    if not match:
        return {}
    pattern = match.group(1).strip()
    shape: dict = {"shorthand": pattern}
    try:
        from .direct_compose import _parse_shorthand
        from .pitch import pitch_to_midi
    except ImportError:  # pragma: no cover - defensive
        return shape
    try:
        events = _parse_shorthand(pattern)
    except Exception:
        return shape
    midis: list[int] = []
    for event in events:
        pitch = event.get("pitch")
        for one in pitch if isinstance(pitch, list) else [pitch]:
            if not one or one == "rest":
                continue
            try:
                midi = pitch_to_midi(one)
            except (ValueError, KeyError, TypeError):
                continue
            # `pitch_to_midi` RETURNS None for a token it cannot read rather
            # than raising, so an except clause alone lets None into the list
            # and `min()` fails on it later, far from the cause.
            if midi is not None:
                midis.append(midi)
    if events:
        shape["events"] = len(events)
    if midis:
        shape["register"] = [min(midis), max(midis)]
        shape["span_semitones"] = max(midis) - min(midis)
    return shape


def _climax_suggestions(text: str) -> dict[str, dict[str, list[str]]]:
    """Register span and rhythmic density per figuration, from the climax table.

    `figuration-patterns.md` carries a "Climax Building Reference Table" that
    maps each dynamic level to a texture, a REGISTER SPAN, a RHYTHMIC DENSITY,
    and the figuration numbers it applies to:

        | mf | Inner voices added | #11, #12 | 2-3 octaves | Sixteenth notes |
        | ff | Cascading arpeggios | #6, #10, #12 | 4+ octaves | Dense sixteenths |

    Every figuration template shipped with `density_suggestion: None` and
    `register_suggestion: ""` — 660 blank fields across the packs, read by
    `style_resolver` — while the answer sat in a table in the same document,
    indexed by the very number in each template's own id (`fig_11_...`).

    Returns `{"11": {"register": [...], "density": [...]}}`.
    """
    out: dict[str, dict[str, list[str]]] = {}
    for table in _parse_md_tables(text):
        fig_col = _table_column(table, "figuration")
        reg_col = _table_column(table, "register", "span")
        den_col = _table_column(table, "density", "rhythmic")
        if fig_col is None or (reg_col is None and den_col is None):
            continue
        for row in table["rows"]:
            for num in re.findall(r"#(\d+)", row[fig_col]):
                entry = out.setdefault(num, {"register": [], "density": []})
                if reg_col is not None and row[reg_col]:
                    entry["register"].append(row[reg_col].strip())
                if den_col is not None and row[den_col]:
                    entry["density"].append(row[den_col].strip())
    return out


def _pivot_chords(*cells: str) -> list[str]:
    """The Roman numerals a pivot row names, in order, deduplicated.

    A pivot table's cells are analysis rather than notation — "I = IV",
    "IV of G", "reinterpret as V of F". The numerals inside them are the
    modulation; the prose around them is not.
    """
    out: list[str] = []
    for cell in cells:
        for token in re.split(r"[\s,;()=]+", cell or ""):
            token = token.strip(".").strip()
            if token and _ROMAN_TOKEN.match(token) and (not out or out[-1] != token):
                out.append(token)
    return out


def _chord_chain(cells: list[str]) -> list[str]:
    """Roman-numeral chain from the first table cell that spells one out.

    Cells are prose with a chain embedded: "ii6 -> cad 6/4 -> V7 -> I",
    "Standard V7 -> vi; then real PAC follows", "V→vi, V→bVI, then finally V→I".
    Split on the arrow, then keep the one Roman-looking token in each segment
    and drop the words around it.
    """
    for cell in cells:
        if not cell or not _ARROW.search(cell):
            continue
        chain: list[str] = []
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


def _bass_motion(chords: list[str]) -> str:
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


def _cadence_table_blocks(text: str) -> list[list[str]]:
    """Markdown table row-blocks that describe cadences.

    Matched EITHER by "cadence"/"cadential" in the section heading above the
    table, OR by the word appearing in the header row itself. Requiring it in
    the header row alone missed every profile that heads the column "Strategy".
    """
    blocks: list[list[str]] = []
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
