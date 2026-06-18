"""
CompositionBrief — everything Claude needs in front of it before writing notes.

The brief is the load-bearing fix for mechanical output: instead of composing
blind, the agent receives REAL corpus bars (actual pitches and durations,
rendered in direct_compose shorthand so tokens can be lifted and transformed),
the density / ornament / texture statistics the phrase should live up to, and
the continuity state from the previous phrase.

This module is read-only over the PieceGraph, the reference_index corpus,
compiled packs, and texture templates. Thresholding lives in commit_gate.py.
"""

from __future__ import annotations

import json
import logging
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .corpus_adapter import AdaptedBar, CorpusAdapter, CorpusQuery
from .duration import beats_to_dur, dur_to_beats
from .pitch import is_minor_key

logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
_REFERENCE_INDEX = _BASE / "reference_index"
_COMPILED_PACKS = _BASE / "compiled_packs"
_TEXTURE_TEMPLATES = _BASE / "texture_templates"

_DEFAULT_COMPOSER = "mozart"

# Process-level caches: corpus shards are 20-90MB per composer, so within
# one python invocation (especially run_agent_section_briefs) load once.
_ADAPTER_CACHE: Dict[str, CorpusAdapter] = {}
_DENSITY_CACHE: Dict[str, Dict[str, Any]] = {}
_TEXTURE_TEMPLATE_CACHE: Dict[str, Dict[str, Any]] = {}
_PACK_CACHE: Dict[str, Any] = {}  # compiled_packs/<composer>/<name>.json
_PROFILE_CACHE: Dict[str, Dict[str, Any]] = {}
_PHRASE_BANK_CACHE: Dict[str, Any] = {}
_CADENCE_BANK_CACHE: Dict[str, Any] = {}
_PATTERN_RETRIEVER = None  # shared across composers (one library)


def _load_pack(composer: str, name: str) -> Any:
    """Load a compiled doctrine pack (cached). Returns {} / [] shaped default.

    For a style reference, the style's OWN pack (e.g. an aggregated
    corpus_profile / density_stats under compiled_packs/style__<name>/) wins;
    if the style has no such pack, fall back to a representative armed member
    so phrase-scoped doctrine (cadence scripts, ornament intents, …) still
    resolves for style-targeted composition.
    """
    key = f"{composer}/{name}"
    if key in _PACK_CACHE:
        return _PACK_CACHE[key]
    path = _COMPILED_PACKS / composer / f"{name}.json"
    data: Any = None
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = None
    if data is None:
        from .style_registry import is_style_id, style_members, style_name

        if is_style_id(composer):
            for member in style_members(style_name(composer)):
                member_pack = _load_pack(member, name)
                if member_pack:
                    data = member_pack
                    break
    _PACK_CACHE[key] = data
    return data


def corpus_profile(composer: str) -> Dict[str, Any]:
    """Per-composer metric distribution profile (corpus_profile.json), cached."""
    if composer in _PROFILE_CACHE:
        return _PROFILE_CACHE[composer]
    data = _load_pack(composer, "corpus_profile") or {}
    _PROFILE_CACHE[composer] = data
    return data


# ─── Data model ──────────────────────────────────────────────────────────────


@dataclass
class ExemplarView:
    """One real corpus bar, transposed to the target key, in shorthand."""

    source: str = ""
    source_bar: Any = None
    source_key: str = ""
    target_key: str = ""
    rh_texture: str = ""
    lh_texture: str = ""
    melody_density: int = 0
    accomp_density: int = 0
    phrase_position: str = ""
    rh: str = ""  # direct_compose shorthand, chords as [p1,p2]dur
    lh: str = ""


@dataclass
class CompositionBrief:
    phrase_id: str = ""
    composer: str = ""
    slot_summary: Dict[str, Any] = field(default_factory=dict)
    sketch_summary: Dict[str, Any] = field(default_factory=dict)
    ledger_state: List[str] = field(default_factory=list)
    # Actionable, binding constraints derived from the ledger (A4): what THIS
    # phrase must resolve / must not use / is on cooldown / is locked.
    ledger_constraints: Dict[str, Any] = field(default_factory=dict)
    transition: Dict[str, Any] = field(default_factory=dict)
    exemplars: List[ExemplarView] = field(default_factory=list)
    target_stats: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    # Multi-level patterns (WS-A) — corpus material above the single-bar level
    phrase_shape: Dict[str, Any] = field(default_factory=dict)
    cadence_exemplars: List[Dict[str, Any]] = field(default_factory=list)
    transition_patterns: Dict[str, Any] = field(default_factory=dict)
    lh_vocabulary: List[Dict[str, Any]] = field(default_factory=list)
    # Written rules / doctrine (WS-C) — the composer's voice + phrase-scoped craft
    fingerprints: List[Dict[str, str]] = field(default_factory=list)
    doctrine: Dict[str, Any] = field(default_factory=dict)
    anti_patterns: List[str] = field(default_factory=list)


# ─── Composer resolution ─────────────────────────────────────────────────────


def _iter_corpus_bars(composer: str):
    """Yield all corpus bars for a composer (sharded or inline).

    A style reference (``style__<name>``) yields the union of its armed member
    composers' bars, so density stats and any bar-level aggregation work for a
    style exactly as for a single composer.
    """
    from .style_registry import is_style_id, style_members, style_name

    if is_style_id(composer):
        for member in style_members(style_name(composer)):
            yield from _iter_corpus_bars(member)
        return

    composer_dir = _REFERENCE_INDEX / composer
    shards = sorted(composer_dir.glob("bars_*.json"))
    if shards:
        for shard in shards:
            try:
                with open(shard) as f:
                    yield from json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
        return
    index_path = composer_dir / "bar_index.json"
    if index_path.exists():
        try:
            with open(index_path) as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("bars"), list):
                yield from data["bars"]
        except (json.JSONDecodeError, OSError):
            return


def _has_corpus(d: Path) -> bool:
    if any(d.glob("bars_*.json")):
        return True
    index_path = d / "bar_index.json"
    if not index_path.exists():
        return False
    try:  # cheap check: inline corpora keep bars in bar_index.json
        with open(index_path) as f:
            head = f.read(2048)
        return '"bars"' in head
    except OSError:
        return False


def available_corpus_composers() -> List[str]:
    if not _REFERENCE_INDEX.exists():
        return []
    return sorted(d.name for d in _REFERENCE_INDEX.iterdir() if d.is_dir() and _has_corpus(d))


def composer_coverage_tier(composer: str) -> Dict[str, Any]:
    """Report how well a composer is armed, from what's actually on disk.

    Tiers: A = richly armed (≥1500 bars + profile + density stats);
    B = armed (≥400 bars + profile or density stats); C = thin corpus
    (some bars, no derived stats); D = unarmed (no corpus — briefs for this
    composer will be insufficient until acquire_composer.py runs).
    """
    from .style_registry import is_style_id

    composer = (composer or "").lower()
    cdir = _REFERENCE_INDEX / composer
    has_corpus = is_style_id(composer) or _has_corpus(cdir)
    n_bars = sum(1 for _ in _iter_corpus_bars(composer)) if has_corpus else 0
    has_density = (_COMPILED_PACKS / composer / "density_stats.json").exists()
    has_profile = (_COMPILED_PACKS / composer / "corpus_profile.json").exists()
    if n_bars == 0:
        tier = "D"
    elif n_bars >= 1500 and has_profile and has_density:
        tier = "A"
    elif n_bars >= 400 and (has_profile or has_density):
        tier = "B"
    else:
        tier = "C"
    return {
        "composer": composer,
        "tier": tier,
        "armed": tier in ("A", "B"),
        "bars": n_bars,
        "has_density_stats": has_density,
        "has_corpus_profile": has_profile,
    }


def resolve_composer(
    graph, override: Optional[str] = None, warnings: Optional[List[str]] = None
) -> str:
    """Resolve the corpus composer for a piece. See resolve_composer_matched."""
    composer, _matched = resolve_composer_matched(graph, override, warnings)
    return composer


def resolve_composer_matched(
    graph, override: Optional[str] = None, warnings: Optional[List[str]] = None
) -> "tuple[str, bool]":
    """Resolve the corpus composer for a piece. Returns (composer, matched).

    ``matched`` is True only when the requested composer actually has corpus on
    disk. When a composer IS requested but has no corpus, we DO NOT silently
    borrow another composer's material (the old behaviour quietly fell back to
    Mozart) — we keep the requested name and return matched=False, so the brief
    comes out honestly insufficient and acquisition can arm the composer. Only
    when nothing is requested at all do we fall back to a default.
    """
    warnings = warnings if warnings is not None else []
    corpus = available_corpus_composers()

    candidates: List[str] = []
    if override:
        candidates.append(override.lower())
    dna = getattr(graph, "style_dna", None)
    if dna is not None and getattr(dna, "composer_id", ""):
        candidates.append(dna.composer_id.lower())
    contract = getattr(graph, "contract", None)
    for attr in ("style_anchor", "composer", "style"):
        v = getattr(contract, attr, None) if contract is not None else None
        if isinstance(v, str) and v:
            candidates.append(v.lower())

    from .style_registry import (
        is_style_id,
        make_style_id,
        normalize_style,
        style_members,
        style_name,
    )

    for c in candidates:
        if is_style_id(c):  # already a style id
            # style_members expects the bare style name, not the style__ id
            if style_members(style_name(c)):
                return c, True
            continue
        if c in corpus:
            return c, True
        # e.g. "mozart-late" → "mozart"
        base = c.split("-")[0].split("_")[0]
        if base in corpus:
            warnings.append(f"composer '{c}' mapped to corpus '{base}'")
            return base, True

    # No exact composer matched — a style/genre request anchors on the whole
    # idiom (multiple composers) rather than picking one.
    for c in candidates:
        canon = normalize_style(c)
        if canon and style_members(canon):
            sid = make_style_id(canon)
            members = style_members(canon)
            warnings.append(
                f"composing in '{canon}' style over {len(members)} armed "
                f"composers: {', '.join(members)}"
            )
            return sid, True

    if candidates:
        # A composer was requested but has no corpus. Keep the requested name
        # so downstream retrieval finds nothing (insufficient brief) rather
        # than silently substituting another composer's exemplars.
        requested = candidates[0]
        arm = requested.split("-")[0].split("_")[0]
        warnings.append(
            f"composer '{requested}' has NO corpus on disk — the brief will be "
            f"insufficient. Arm it with `tools/scripts/acquire_composer.py "
            f"{arm}`, or pass composer= pointing at an armed composer."
        )
        return requested, False

    fallback = (
        _DEFAULT_COMPOSER
        if _DEFAULT_COMPOSER in corpus
        else (corpus[0] if corpus else _DEFAULT_COMPOSER)
    )
    warnings.append(
        f"no composer specified for this piece; defaulting to '{fallback}'. "
        f"Pass composer= to compose in a specific style."
    )
    return fallback, (fallback in corpus)


def _adapter(composer: str) -> CorpusAdapter:
    if composer not in _ADAPTER_CACHE:
        _ADAPTER_CACHE[composer] = CorpusAdapter(composer=composer)
    return _ADAPTER_CACHE[composer]


# ─── Density statistics (per texture, from the real corpus) ─────────────────


def texture_density_stats(composer: str, refresh: bool = False) -> Dict[str, Any]:
    """Per-texture events/bar percentiles aggregated from reference_index.

    Returns {"rh": {texture: {median, p25, p75, mean, n}},
             "lh": {texture: {...}}, "total_bars": int}.
    Cached on disk at compiled_packs/<composer>/density_stats.json and
    in memory for the process.
    """
    if not refresh and composer in _DENSITY_CACHE:
        return _DENSITY_CACHE[composer]

    cache_path = _COMPILED_PACKS / composer / "density_stats.json"
    if not refresh and cache_path.exists():
        try:
            with open(cache_path) as f:
                stats = json.load(f)
            _DENSITY_CACHE[composer] = stats
            return stats
        except (json.JSONDecodeError, OSError):
            pass

    rh_vals: Dict[str, List[int]] = {}
    lh_vals: Dict[str, List[int]] = {}
    total = 0
    for bar in _iter_corpus_bars(composer):
        total += 1
        md = bar.get("melody_density", 0)
        ad = bar.get("accomp_density", 0)
        rt = bar.get("rh_texture", "unclassified")
        lt = bar.get("lh_texture", "unclassified")
        if md > 0:
            rh_vals.setdefault(rt, []).append(md)
        if ad > 0:
            lh_vals.setdefault(lt, []).append(ad)

    def _summary(vals: List[int]) -> Dict[str, float]:
        vals = sorted(vals)
        n = len(vals)
        return {
            "median": round(statistics.median(vals), 1),
            "p25": round(vals[n // 4], 1),
            "p75": round(vals[(3 * n) // 4], 1),
            "mean": round(statistics.fmean(vals), 2),
            "n": n,
        }

    stats = {
        "composer": composer,
        "total_bars": total,
        "rh": {t: _summary(v) for t, v in rh_vals.items() if len(v) >= 5},
        "lh": {t: _summary(v) for t, v in lh_vals.items() if len(v) >= 5},
    }

    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(stats, f, indent=1)
    except OSError as exc:
        logger.warning("could not write density cache: %s", exc)

    _DENSITY_CACHE[composer] = stats
    return stats


def _texture_templates(composer: str) -> Dict[str, Any]:
    if composer in _TEXTURE_TEMPLATE_CACHE:
        return _TEXTURE_TEMPLATE_CACHE[composer]
    path = _TEXTURE_TEMPLATES / f"{composer}.json"
    data: Dict[str, Any] = {}
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    _TEXTURE_TEMPLATE_CACHE[composer] = data
    return data


def _self_continuation(composer: str) -> Dict[str, float]:
    """LH texture self-continuation probabilities from scoped statistics."""
    path = _COMPILED_PACKS / composer / "scoped_statistics.json"
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            tm = json.load(f).get("transition_matrix", {})
        return {t: round(row.get(t, 0.0), 3) for t, row in tm.items()}
    except (json.JSONDecodeError, OSError):
        return {}


# ─── Multi-level corpus patterns (phrase / cadence / transition / LH vocab) ──


def _phrase_bank(composer: str):
    if composer not in _PHRASE_BANK_CACHE:
        from .phrase_bank import PhraseBank

        _PHRASE_BANK_CACHE[composer] = PhraseBank(composer)
    return _PHRASE_BANK_CACHE[composer]


def _cadence_bank(composer: str):
    if composer not in _CADENCE_BANK_CACHE:
        from .cadence_bank import CadenceBank

        _CADENCE_BANK_CACHE[composer] = CadenceBank(composer)
    return _CADENCE_BANK_CACHE[composer]


def _pattern_retriever():
    global _PATTERN_RETRIEVER
    if _PATTERN_RETRIEVER is None:
        from .pattern_retriever import PatternRetriever

        _PATTERN_RETRIEVER = PatternRetriever()
    return _PATTERN_RETRIEVER


# Map a planning cadence label onto the cadence-bank / cadence-script vocabulary.
_CADENCE_NORMALIZE = {
    "authentic": "PAC",
    "perfect": "PAC",
    "pac": "PAC",
    "v-i": "PAC",
    "imperfect": "IAC",
    "iac": "IAC",
    "half": "HC",
    "hc": "HC",
    "dominant": "HC",
    "deceptive": "DC",
    "dc": "DC",
    "evaded": "evaded",
    "plagal": "plagal",
    "iv-i": "plagal",
}


def _normalize_cadence(label: Optional[str]) -> Optional[str]:
    if not label or label in ("none", "", None):
        return None
    return _CADENCE_NORMALIZE.get(str(label).lower(), str(label))


def _phrase_shape(composer: str, slot, role: str) -> Dict[str, Any]:
    """Top corpus phrase for this slot's role/length — its arc, not just a bar."""
    try:
        from .models import PhraseQuery

        bank = _phrase_bank(composer)
        n_bars = slot.bar_count
        q = PhraseQuery(
            formal_function=role,
            length_range=(max(1, n_bars - 2), n_bars + 2),
            cadence_type=_normalize_cadence(getattr(slot, "cadence_target", None)),
            n=1,
        )
        res = bank.retrieve(q)
        if not res:
            return {}
        p = res[0]
        return {
            "source": p.source,
            "bars": list(p.bar_range),
            "role": p.role,
            "cadence_type": p.cadence_type,
            "density_arc": [round(x, 2) for x in (p.density_curve or [])],
            "register_arc": [round(x, 2) for x in (p.register_curve or [])],
            "peak_at": (
                p.density_curve.index(max(p.density_curve)) + 1 if p.density_curve else None
            ),
            "lh_textures": p.lh_textures,
        }
    except Exception as exc:  # never let a pattern lookup break the brief
        logger.debug("phrase_shape lookup failed: %s", exc)
        return {}


def _cadence_exemplars(composer: str, slot) -> List[Dict[str, Any]]:
    cad = _normalize_cadence(getattr(slot, "cadence_target", None))
    if cad is None:
        return []
    try:
        from .models import CadenceQuery

        key = getattr(slot, "key", "C")
        mode = "minor" if is_minor_key(key) else "major"
        res = _cadence_bank(composer).retrieve(
            CadenceQuery(cadence_type=cad, key=key, mode=mode, n=2)
        )
        out = []
        for c in res:
            if not (c.chord_sequence or c.bass_motion):
                continue  # skip empty corpus-phrase stubs
            out.append(
                {
                    "type": c.cadence_type,
                    "chords": c.chord_sequence,
                    "soprano_arrival": c.soprano_arrival,
                    "bass_motion": c.bass_motion,
                    "strength": c.strength,
                }
            )
        return out[:2]
    except Exception as exc:
        logger.debug("cadence lookup failed: %s", exc)
        return []


def _transition_patterns(composer: str, slot, from_texture: Optional[str]) -> Dict[str, Any]:
    """Idiomatic texture follow-ons: what the corpus does after `from_texture`,
    plus the phrase's own primary-texture continuation odds (intra-phrase variety).
    """
    try:
        bank = _phrase_bank(composer)
        matrix = bank._load_transition_matrix()
        counts = matrix.get("counts", {})

        def _top_follow(tex: str, k: int = 3) -> List[Tuple[str, float]]:
            row = counts.get(tex, {})
            total = sum(row.values())
            if not total:
                return []
            ranked = sorted(row.items(), key=lambda kv: -kv[1])
            return [(t, round(c / total, 2)) for t, c in ranked[:k] if c]

        out: Dict[str, Any] = {}
        if from_texture:
            follow = _top_follow(from_texture)
            if follow:
                out["after_previous"] = {"from": from_texture, "follow": follow}
        # primary LH texture of this phrase
        lh = [t[1] for t in _slot_textures(slot)]
        primary = max(set(lh), key=lh.count) if lh else None
        if primary:
            follow = _top_follow(primary)
            self_p = bank.get_transition_probability(primary, primary)
            out["within_phrase"] = {
                "primary": primary,
                "self_continuation": round(self_p, 2),
                "vary_toward": [f for f in follow if f[0] != primary][:2],
            }
        return out
    except Exception as exc:
        logger.debug("transition lookup failed: %s", exc)
        return {}


def _lh_vocabulary(composer: str, slot, key: str, max_patterns: int = 2) -> List[Dict[str, Any]]:
    """Top canonical real LH patterns for this phrase's LH textures, in shorthand."""
    try:
        pr = _pattern_retriever()
        lh_textures = []
        for _, lh in _slot_textures(slot):
            if lh not in lh_textures and lh not in ("silence", "unclassified"):
                lh_textures.append(lh)
        out: List[Dict[str, Any]] = []
        for tex in lh_textures[:2]:
            patterns = pr.retrieve(tex, density_range=(3, 18), n=1)
            for p in patterns:
                tp = pr.transpose_pattern(p, "C", key)
                toks = []
                for e in tp.get("lh_events", []):
                    if e.get("p"):
                        toks.append(f"{e['p']}{beats_to_dur(e.get('d', 0.5))}")
                if toks:
                    out.append(
                        {
                            "texture": tex,
                            "occurrences": p.get("total_occurrences"),
                            "lh": " ".join(toks),
                        }
                    )
                if len(out) >= max_patterns:
                    return out
        return out
    except Exception as exc:
        logger.debug("lh_vocabulary lookup failed: %s", exc)
        return []


# ─── Written rules / doctrine (fingerprints, phrase-scoped craft, AI tells) ──


def _fingerprints(composer: str) -> List[Dict[str, str]]:
    from .style_registry import is_style_id, style_members, style_name

    if is_style_id(composer):
        # Aggregate the shared traits of the idiom: a couple from each armed
        # member, deduped by name, capped — the style's collective voice.
        out: List[Dict[str, str]] = []
        seen: set = set()
        members = style_members(style_name(composer))
        for member in members:
            for fp in _fingerprints(member)[:2]:
                if fp["name"] not in seen:
                    seen.add(fp["name"])
                    out.append({**fp, "from": member})
                if len(out) >= 5:
                    return out
        return out
    pack = _load_pack(composer, "fingerprint_rules") or {}
    items = pack.get("items", []) if isinstance(pack, dict) else []
    out = []
    for it in items[:5]:
        desc = it.get("description", "")
        # first sentence only — keep the brief tight
        first = desc.split(". ")[0].strip()
        out.append({"name": it.get("name", it.get("id", "")), "rule": first})
    return out


def _doctrine_slices(composer: str, slot, role: str) -> Dict[str, Any]:
    """Select only the doctrine that applies to THIS phrase (not the firehose)."""
    out: Dict[str, Any] = {}
    cad = _normalize_cadence(getattr(slot, "cadence_target", None))

    # Cadence script for the slot's cadence
    if cad:
        scripts = _load_pack(composer, "cadence_scripts") or []
        for s in scripts if isinstance(scripts, list) else []:
            stype = (s.get("type", "") or "").upper()
            if cad.upper() in stype:
                out["cadence_script"] = {
                    "type": s.get("type"),
                    "approach": s.get("approach_chords"),
                    "soprano": s.get("soprano_line"),
                    "bass": s.get("bass_motion"),
                    "strength": s.get("strength"),
                }
                break

    # Ornament intent matching the phrase position
    position = "cadence" if cad else ("entry" if role == "opening" else "middle")
    intents = _load_pack(composer, "ornament_intents") or []
    chosen = []
    for it in intents if isinstance(intents, list) else []:
        ctx = (it.get("context", "") or "").lower()
        if position in ctx or (role == "opening" and "entry" in ctx):
            chosen.append(f"{it.get('what_moment_needs', '')} → {it.get('common_choice', '')}")
    if chosen:
        out["ornament_intent"] = chosen[:2]

    # Breathing / silence guidance (favor cadence/climax-relevant rules)
    breathing = _load_pack(composer, "breathing_rules") or []
    breaths = []
    for b in breathing if isinstance(breathing, list) else []:
        placement = (b.get("placement", "") or "").lower()
        if cad and ("caden" in placement or "climax" in placement or "return" in placement):
            breaths.append(f"{b.get('technique', '')} — {b.get('effect', '')}")
    if breaths:
        out["breathing"] = breaths[:1]

    # Top harmonic devices (the composer's signature colors)
    devices = _load_pack(composer, "harmonic_devices") or []
    if isinstance(devices, list) and devices:
        ranked = sorted(devices, key=lambda d: -d.get("frequency_weight", 0))
        out["harmonic_devices"] = [
            {"name": d.get("name"), "use": (d.get("contexts") or [""])[0]} for d in ranked[:2]
        ]

    # Melody priors for contour/climax (phrase-shaping guidance)
    priors = _load_pack(composer, "melody_priors") or []
    shape = []
    for p in priors if isinstance(priors, list) else []:
        cat = (p.get("category", "") or "").lower()
        if cat in ("contour", "climax", "phrase_structure"):
            shape.append(p.get("description", ""))
    if shape:
        out["melody_priors"] = shape[:2]

    return out


def _anti_pattern_tells(composer: str, max_tells: int = 4) -> List[str]:
    rules = _load_pack(composer, "anti_pattern_rules") or []
    out = []
    for r in rules if isinstance(rules, list) else []:
        if r.get("severity") == "warning":
            name = r.get("name", "")
            # strip leading "N. " numbering for readability
            name = name.split(". ", 1)[-1] if name[:2].strip().isdigit() else name
            out.append(name)
        if len(out) >= max_tells:
            break
    return out


# ─── Slot → corpus queries ───────────────────────────────────────────────────


def _infer_textures(slot) -> List[Tuple[str, str]]:
    """Infer per-bar (rh, lh) textures when texture_plan is empty."""
    curves = getattr(slot, "curves", None)
    density = list(getattr(curves, "density", []) or [])
    out = []
    for i in range(slot.bar_count):
        d = density[i] if i < len(density) else 0.5
        if d >= 0.65:
            out.append(("passage_work", "alberti"))
        elif d >= 0.35:
            out.append(("singing_melody", "alberti"))
        else:
            out.append(("singing_melody", "block_chord_sparse"))
    return out


def _slot_textures(slot) -> List[Tuple[str, str]]:
    plan = getattr(slot, "texture_plan", None) or []
    if plan:
        return [
            (getattr(b, "rh_texture", "singing_melody"), getattr(b, "lh_texture", "alberti"))
            for b in plan
        ]
    return _infer_textures(slot)


def _positions_for(slot, n_bars: int) -> List[str]:
    pos = ["middle"] * n_bars
    if n_bars:
        pos[0] = "opening"
        if getattr(slot, "cadence_target", "none") not in ("none", "", None):
            pos[-1] = "cadential"
    return pos


# ─── Exemplar retrieval & rendering ──────────────────────────────────────────


def _adapted_to_shorthand(adapted: AdaptedBar) -> Tuple[str, str]:
    """Render an AdaptedBar as direct_compose shorthand, preserving chords."""

    def _tokens(events: List[Dict]) -> List[str]:
        toks = []
        for e in events:
            dur = e.get("dur", 1.0)
            # Grace notes carry dur 0.0 in the corpus. Rendering them with
            # beats_to_dur(0.0) emits a real 32nd, which overflows the bar
            # (a faithfully-adapted exemplar would then fail meter validation).
            # Emit them with :grace — direct_compose gives those zero bar-time —
            # so the exemplar both shows the ornament AND sums to the meter.
            is_grace = isinstance(dur, (int, float)) and dur <= 1e-6 or e.get("is_grace")
            dur_code = beats_to_dur(0.25 if is_grace else dur)
            # Ornament suffixes the corpus actually records (carried through
            # corpus_adapter._transpose_events). Stackable, ":"-delimited so
            # _shorthand_beats strips them cleanly.
            suffix = ":grace" if is_grace else ""
            if e.get("has_trill"):
                suffix += ":tr"
            if e.get("has_turn"):
                suffix += ":turn"
            if e.get("type") == "rest":
                if is_grace:
                    continue  # a zero-length rest carries no information
                toks.append(f"rest_{dur_code}")
            elif e.get("type") == "chord":
                pitches = [p for p in e.get("pitches", []) if p]
                if len(pitches) > 1:
                    toks.append(f"[{','.join(pitches)}]{dur_code}{suffix}")
                elif pitches:
                    toks.append(f"{pitches[0]}{dur_code}{suffix}")
            elif e.get("pitch"):
                toks.append(f"{e['pitch']}{dur_code}{suffix}")
        return toks

    return " ".join(_tokens(adapted.rh_events)), " ".join(_tokens(adapted.lh_events))


def _shorthand_beats(shorthand: str) -> Optional[float]:
    """Total metrical beats of a shorthand string (grace notes count 0).

    Returns None if a token can't be parsed (so callers don't falsely judge
    an unparseable bar as overflowing)."""
    import re

    total = 0.0
    for tok in (shorthand or "").split():
        if ":grace" in tok:
            continue  # grace notes take no metrical time
        # strip expression suffixes after the duration code
        head = re.split(r"[:(~<>!)]", tok)[0]
        m = re.match(r"^(?:\[[^\]]+\]|rest_|rest|[A-G][#b\-]*\d+)(.*)$", head)
        if not m:
            return None
        code = m.group(1).strip("_") or "q"
        try:
            total += dur_to_beats(code)
        except Exception:
            return None
    return round(total, 4)


def _shorthand_overflows_bar(shorthand: str, capacity: float) -> bool:
    """True when a hand's shorthand sums to MORE than the bar capacity — the
    signature of a corrupted multi-voice flatten in the corpus bar record
    (the offline extractor concatenated overlapping voices). Such an exemplar
    is malformed: shown to Claude it misleads, and copied verbatim it fails
    meter validation. A bar that sums to LESS than capacity is fine (rests
    fill the remainder)."""
    beats = _shorthand_beats(shorthand)
    if beats is None:
        return False  # unparseable → don't filter on a false signal
    return beats > capacity + 0.01


def _retrieve_exemplars_style(
    style_ref: str, slot, n_exemplars: int, warnings: List[str]
) -> List[ExemplarView]:
    """Gather exemplars from every armed member of a style, interleaved so the
    brief shows real bars from several composers of that idiom (not one)."""
    from .style_registry import style_members, style_name

    members = style_members(style_name(style_ref))
    if not members:
        warnings.append(f"style '{style_name(style_ref)}' has no armed members")
        return []
    per_member = max(2, -(-n_exemplars // len(members)))  # ceil, ≥2
    by_member = [_retrieve_exemplars(m, slot, per_member, warnings) for m in members]
    # Round-robin interleave so no single composer dominates the brief.
    merged: List[ExemplarView] = []
    for i in range(max((len(b) for b in by_member), default=0)):
        for b in by_member:
            if i < len(b):
                merged.append(b[i])
                if len(merged) >= n_exemplars:
                    return merged
    return merged


def _retrieve_exemplars(
    composer: str, slot, n_exemplars: int, warnings: List[str]
) -> List[ExemplarView]:
    from .style_registry import is_style_id

    if is_style_id(composer):
        return _retrieve_exemplars_style(composer, slot, n_exemplars, warnings)
    adapter = _adapter(composer)
    key = getattr(slot, "key", "C")
    key_mode = "minor" if is_minor_key(key) else "major"
    meter = tuple(getattr(slot, "meter", (4, 4)))

    textures = _slot_textures(slot)
    positions = _positions_for(slot, len(textures))

    # One query per distinct (texture pair, position) in the phrase
    seen_specs = []
    for (rh, lh), pos in zip(textures, positions):
        spec = (rh, lh, pos)
        if spec not in seen_specs:
            seen_specs.append(spec)

    exemplars: List[ExemplarView] = []
    used_sources: set = set()

    per_spec = max(1, -(-n_exemplars // max(1, len(seen_specs))))  # ceil
    for rh, lh, pos in seen_specs:
        query = CorpusQuery(
            time_sig=meter,
            key_mode=key_mode,
            rh_texture=rh,
            lh_texture=lh,
            phrase_position=pos,
            n=per_spec + 4,
        )
        candidates = adapter.retrieve(query)
        if not candidates:  # relax textures
            query.rh_texture = None
            query.lh_texture = None
            candidates = adapter.retrieve(query)
        if not candidates and key_mode == "minor":  # use major corpus
            query.key_mode = "major"
            query.rh_texture = rh
            query.lh_texture = lh
            candidates = adapter.retrieve(query)
        if not candidates:
            query.rh_texture = None
            query.lh_texture = None
            query.phrase_position = None
            candidates = adapter.retrieve(query)
        if not candidates:
            warnings.append(f"no corpus exemplars for {rh}/{lh}/{pos} in {composer}")
            continue

        added = 0
        for bar in candidates:
            src = f"{bar.get('source', '?')}:{bar.get('bar_num', '?')}"
            if src in used_sources:
                continue
            adapted = adapter.transpose_bar(bar, key)
            rh_sh, lh_sh = _adapted_to_shorthand(adapted)
            if not rh_sh and not lh_sh:
                continue
            # Skip bars whose RH or LH overflows the meter — a corrupted
            # multi-voice flatten in the corpus record. Showing them misleads
            # Claude and they fail meter validation if copied. (See
            # _shorthand_overflows_bar.)
            capacity = meter[0] * 4.0 / meter[1]
            if _shorthand_overflows_bar(rh_sh, capacity) or _shorthand_overflows_bar(
                lh_sh, capacity
            ):
                continue
            exemplars.append(
                ExemplarView(
                    source=bar.get("source", "?"),
                    source_bar=bar.get("bar_num"),
                    source_key=bar.get("key", "?"),
                    target_key=key,
                    rh_texture=bar.get("rh_texture", ""),
                    lh_texture=bar.get("lh_texture", ""),
                    melody_density=bar.get("melody_density", 0),
                    accomp_density=bar.get("accomp_density", 0),
                    phrase_position=bar.get("phrase_position", ""),
                    rh=rh_sh,
                    lh=lh_sh,
                )
            )
            used_sources.add(src)
            added += 1
            if added >= per_spec or len(exemplars) >= n_exemplars:
                break
        if len(exemplars) >= n_exemplars:
            break

    return exemplars[:n_exemplars]


# ─── Target stats ─────────────────────────────────────────────────────────────

# Fallback bands when a composer has no corpus_profile (human-sounding-music.md).
_DISCRIMINATOR_FALLBACK = {
    "texture_change_pct": "≈0.4-0.6 (change texture every 1-2 bars)",
    "direction_changes_per_bar": "1.0-2.0",
    "density_cv": "≥0.30 — let density ebb and flow",
}


def _discriminator_targets(composer: str) -> Dict[str, str]:
    """Per-composer targets for the human-vs-AI discriminator metrics.

    Derived from the composer's own corpus distribution (corpus_profile.json)
    as [mean-σ, mean+σ] bands per metric, so the agent aims at THIS composer's
    real spread rather than a generic constant. Falls back to fixed guidance.
    """
    profile = corpus_profile(composer)
    metrics = profile.get("metrics", {}) if isinstance(profile, dict) else {}
    if not metrics:
        return dict(_DISCRIMINATOR_FALLBACK)
    out: Dict[str, str] = {}
    for name in (
        "texture_change_pct",
        "lh_texture_change_pct",
        "density_cv",
        "direction_changes_per_bar",
        "events_per_bar",
    ):
        m = metrics.get(name)
        if not m:
            continue
        mean, sd = m.get("mean", 0.0), m.get("stdev", 0.0)
        lo, hi = round(mean - sd, 2), round(mean + sd, 2)
        out[name] = f"{lo}–{hi} (corpus mean {round(mean, 2)})"
    return out or dict(_DISCRIMINATOR_FALLBACK)


def _build_target_stats(composer: str, slot, warnings: List[str]) -> Dict[str, Any]:
    density = texture_density_stats(composer)
    templates = _texture_templates(composer)
    rh_templates = templates.get("rh_templates", {})
    self_cont = _self_continuation(composer)

    textures = _slot_textures(slot)
    rh_set = sorted({t[0] for t in textures})
    lh_set = sorted({t[1] for t in textures})

    stats: Dict[str, Any] = {
        "rh_textures": {},
        "lh_textures": {},
        "self_continuation": {t: self_cont[t] for t in lh_set if t in self_cont},
        "discriminators": _discriminator_targets(composer),
    }

    expected_rh_total = 0.0
    for t in rh_set:
        entry: Dict[str, Any] = {}
        d = density.get("rh", {}).get(t)
        if d:
            entry["events_per_bar"] = d
            expected_rh_total += d["median"]
        tmpl = rh_templates.get(t, {})
        if tmpl.get("avg_ornament_density"):
            entry["ornament_density"] = tmpl["avg_ornament_density"]
        if tmpl.get("avg_event_count"):
            entry["avg_event_count"] = tmpl["avg_event_count"]
        if entry:
            stats["rh_textures"][t] = entry
        else:
            warnings.append(f"no corpus stats for rh texture '{t}'")

    for t in lh_set:
        d = density.get("lh", {}).get(t)
        if d:
            stats["lh_textures"][t] = {"events_per_bar": d}
        else:
            warnings.append(f"no corpus stats for lh texture '{t}'")

    # Whole-phrase expectation — the "not 9 notes" line
    if expected_rh_total and textures:
        per_bar = expected_rh_total / max(1, len(rh_set))
        total = round(per_bar * slot.bar_count)
        stats["whole_phrase_expectation"] = (
            f"~{max(total - 4, int(total * 0.8))}-{total + 4} RH events "
            f"across {slot.bar_count} bars"
        )

    return stats


# ─── Slot / sketch / ledger / transition summaries ──────────────────────────


def _summarize_slot(slot) -> Dict[str, Any]:
    return {
        "bars": f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}",
        "bar_count": slot.bar_count,
        "key": slot.key,
        "meter": list(slot.meter),
        "tempo_bpm": slot.tempo_bpm,
        "function": slot.function,
        "cadence": {"target": slot.cadence_target, "bar": slot.cadence_bar},
        "harmony_plan": list(getattr(slot, "harmony_plan", []) or []),
        "texture_plan": [
            {"bar": slot.bar_start + i, "rh": rh, "lh": lh}
            for i, (rh, lh) in enumerate(_slot_textures(slot))
        ],
    }


def _summarize_sketch(sketch) -> Dict[str, Any]:
    if sketch is None:
        return {}
    out: Dict[str, Any] = {}
    anchors = getattr(sketch, "melody_anchors", []) or []
    if anchors:
        out["melody_anchors"] = [
            f"b{a.bar}.{a.beat:g} {a.pitch_or_degree} ({a.role})" for a in anchors
        ]
    bass = getattr(sketch, "bass_anchors", []) or []
    if bass:
        out["bass_anchors"] = [f"b{a.bar}.{a.beat:g} {a.pitch_or_degree}" for a in bass]
    hr = getattr(sketch, "harmonic_rhythm", []) or []
    if hr:
        out["harmony"] = [f"b{h.bar}.{h.beat:g} {h.roman}" for h in hr]
    dyn = getattr(sketch, "dynamic_shape", []) or []
    if dyn:
        out["dynamics"] = [
            f"b{d.bar} {d.level}" + (f" {d.hairpin}" if d.hairpin else "") for d in dyn
        ]
    breaths = getattr(sketch, "breath_points", []) or []
    if breaths:
        out["breath_points"] = [f"b{b.bar}.{b.beat:g} {b.type}" for b in breaths]
    return out


def _reconstruct_ledger(graph):
    """The per-piece ExpectationLedger. It is persisted on the graph as the raw
    ``cross_scale_ledger`` dict (and reconstructed via CrossScaleLedger), so the
    brief must rebuild it rather than read a (non-existent) live attribute."""
    live = getattr(graph, "expectation_ledger", None)
    if live is not None and getattr(live, "entries", None) is not None:
        return live
    raw = getattr(graph, "cross_scale_ledger", None)
    if not raw:
        return None
    try:
        from .cross_scale_ledger import CrossScaleLedger

        return CrossScaleLedger.from_dict(raw).phrase_ledger
    except Exception:
        return None


def _global_phrase_order(graph) -> List[str]:
    """All phrase ids in performance order (movements → sections → phrases).
    The ledger's deadline/cooldown math is relative to this order."""
    order: List[str] = []
    form = getattr(graph, "form", None)
    if form is not None and getattr(form, "movements", None):
        for mv in form.movements:
            for sec_id in getattr(mv, "sections", []) or []:
                sec = form.sections.get(sec_id)
                if sec:
                    order.extend(getattr(sec, "phrase_ids", []) or [])
    if not order:
        order = list(getattr(graph, "phrases", {}).keys())
    return order


def _ledger_constraints(graph, phrase_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """Turn open ledger entries into binding, phrase-scoped constraints the
    surface MUST honor: resolve overdue/due-soon promises & debts, avoid
    prohibited material and active cooldowns, preserve identity locks. This is
    the single source the brief renders and the commit gate (B6) checks."""
    out: Dict[str, List[Dict[str, Any]]] = {
        "must_resolve": [],
        "must_not_use": [],
        "cooldown": [],
        "locked": [],
    }
    ledger = _reconstruct_ledger(graph)
    if ledger is None:
        return out
    order = _global_phrase_order(graph)
    cur = phrase_id
    try:
        overdue = ledger.get_overdue(cur, order)
    except Exception:
        overdue = []
    try:
        due = ledger.get_due_soon(cur, order, horizon=1)
    except Exception:
        due = []
    overdue_ids = {getattr(e, "id", id(e)) for e in overdue}
    seen = set()
    for e in list(overdue) + list(due):
        eid = getattr(e, "id", id(e))
        if eid in seen:
            continue
        seen.add(eid)
        out["must_resolve"].append(
            {
                "type": getattr(e, "type", "promise"),
                "object": getattr(e, "object_ref", ""),
                "form": getattr(e, "expected_form", None),
                "urgency": getattr(e, "urgency", 0.5),
                "overdue": eid in overdue_ids,
            }
        )
    try:
        for e in ledger.get_active_prohibitions(cur, order):
            out["must_not_use"].append(
                {"object": getattr(e, "object_ref", ""), "form": getattr(e, "expected_form", None)}
            )
    except Exception:
        pass
    try:
        for e in ledger.get_active_cooldowns(cur, order):
            out["cooldown"].append({"object": getattr(e, "object_ref", "")})
    except Exception:
        pass
    try:
        for e in ledger.get_locks():
            out["locked"].append(
                {"object": getattr(e, "object_ref", ""), "form": getattr(e, "expected_form", None)}
            )
    except Exception:
        pass
    return out


def _ledger_lines(graph, phrase_id: str) -> List[str]:
    ledger = _reconstruct_ledger(graph)
    lines: List[str] = []
    entries = getattr(ledger, "entries", None) if ledger else None
    if entries:
        for e in entries:
            status = getattr(e, "status", "")
            if status in ("fulfilled", "expired", "satisfied", "violated"):
                continue
            kind = getattr(e, "kind", getattr(e, "type", "expectation"))
            obj = getattr(e, "object_ref", "")
            lines.append(f"{kind}: {obj} ({status or 'open'})")
    return lines[:8]


def _last_events_summary(layer, n: int = 4) -> Dict[str, Any]:
    """Tail of a realized LayerIR: what the next phrase must connect to."""
    if layer is None:
        return {}
    events = sorted(layer.principal_line, key=lambda e: (e.bar, e.beat))
    tail = [e for e in events if e.pitch != "rest"][-n:]
    bass = sorted(layer.bass_foundation, key=lambda e: (e.bar, e.beat))
    last_bass = next((e for e in reversed(bass) if e.pitch != "rest"), None)
    dyn = next((e.dynamic for e in reversed(events) if e.dynamic), None)
    return {
        "melody_tail": [f"{e.pitch}{e.duration}" for e in tail],
        "last_bass": (last_bass.pitch if last_bass else None),
        "last_dynamic": dyn,
    }


def _transition_context(graph, phrase_id: str) -> Dict[str, Any]:
    """Continuity info from the previous phrase, read from disk state."""
    out: Dict[str, Any] = {}
    state = graph.phrases.get(phrase_id)
    if state is None:
        return out

    section_id = state.slot.section_id
    order = graph.get_section_phrases(section_id)
    prev_id: Optional[str] = None
    if phrase_id in order:
        idx = order.index(phrase_id)
        if idx > 0:
            prev_id = order[idx - 1]
    if prev_id is None:
        # Fall back to bar ordering across the whole piece (covers both
        # unknown phrase IDs and the first phrase of a section, whose
        # predecessor lives in the previous section)
        candidates = [
            (pid, ps)
            for pid, ps in graph.phrases.items()
            if ps.slot.bar_start < state.slot.bar_start
        ]
        if candidates:
            prev_id = max(candidates, key=lambda kv: kv[1].slot.bar_start)[0]

    if prev_id and prev_id in graph.phrases:
        prev = graph.phrases[prev_id]
        out["previous_phrase"] = prev_id
        tail = _last_events_summary(prev.realized)
        if tail:
            out.update(tail)
        prev_textures = _slot_textures(prev.slot)
        if prev_textures:
            out["exit_lh_texture"] = prev_textures[-1][1]
        sketch = prev.sketch
        exit_sig = getattr(sketch, "exit_signature", None) if sketch else None
        if exit_sig and getattr(exit_sig, "pitch", None):
            out["exit_signature"] = {
                "pitch": exit_sig.pitch,
                "register_center": exit_sig.register_center,
                "dynamic": exit_sig.dynamic,
                "last_chord": exit_sig.last_chord,
            }

    cont = getattr(state.slot, "continuation", None)
    if cont and getattr(cont, "last_soprano_pitch", None):
        out.setdefault("continuation", {})
        out["continuation"] = {
            "last_soprano_pitch": cont.last_soprano_pitch,
            "last_bass_pitch": cont.last_bass_pitch,
            "last_chord": cont.last_chord,
            "last_dynamic": cont.last_dynamic,
            "pending_resolution": cont.pending_resolution,
        }
    return out


# ─── Public API ──────────────────────────────────────────────────────────────


def build_brief(
    graph, phrase_id: str, n_exemplars: int = 8, composer: Optional[str] = None
) -> CompositionBrief:
    """Assemble the composition brief for one phrase."""
    warnings: List[str] = []
    state = graph.phrases.get(phrase_id)
    if state is None:
        raise KeyError(f"unknown phrase '{phrase_id}' — known: {sorted(graph.phrases)[:10]}...")
    slot = state.slot

    resolved = resolve_composer(graph, composer, warnings)
    role = _positions_for(slot, slot.bar_count)[0] if slot.bar_count else "middle"
    transition = _transition_context(graph, phrase_id)
    key = getattr(slot, "key", "C")

    brief = CompositionBrief(
        phrase_id=phrase_id,
        composer=resolved,
        slot_summary=_summarize_slot(slot),
        sketch_summary=_summarize_sketch(state.sketch),
        ledger_state=_ledger_lines(graph, phrase_id),
        ledger_constraints=_ledger_constraints(graph, phrase_id),
        transition=transition,
        exemplars=_retrieve_exemplars(resolved, slot, n_exemplars, warnings),
        target_stats=_build_target_stats(resolved, slot, warnings),
        # WS-A: multi-level corpus patterns
        phrase_shape=_phrase_shape(resolved, slot, role),
        cadence_exemplars=_cadence_exemplars(resolved, slot),
        transition_patterns=_transition_patterns(resolved, slot, transition.get("exit_lh_texture")),
        lh_vocabulary=_lh_vocabulary(resolved, slot, key),
        # WS-C: written rules / doctrine, scoped to this phrase
        fingerprints=_fingerprints(resolved),
        doctrine=_doctrine_slices(resolved, slot, role),
        anti_patterns=_anti_pattern_tells(resolved),
        warnings=warnings,
    )
    return brief


def render_text(brief: CompositionBrief) -> str:
    """Compact, note-complete text rendering of a brief for the agent."""
    s = brief.slot_summary
    lines = [
        f"COMPOSITION BRIEF — phrase {brief.phrase_id} ({brief.composer})",
        f"Slot: bars {s.get('bars')} ({s.get('bar_count')} bars), "
        f"{s.get('key')}, {'/'.join(map(str, s.get('meter', [4, 4])))}, "
        f"♩={s.get('tempo_bpm')}",
        f"Function: {s.get('function')} | Cadence: "
        f"{s.get('cadence', {}).get('target')} at bar "
        f"{s.get('cadence', {}).get('bar')}",
    ]
    if s.get("harmony_plan"):
        lines.append("Harmony plan: " + " | ".join(s["harmony_plan"]))
    tp = s.get("texture_plan") or []
    if tp:
        lines.append("Texture plan: " + "  ".join(f"b{b['bar']} {b['rh']}/{b['lh']}" for b in tp))

    sk = brief.sketch_summary
    if sk:
        lines.append("")
        lines.append("SKETCH:")
        for key_name in ("melody_anchors", "bass_anchors", "harmony", "dynamics", "breath_points"):
            if sk.get(key_name):
                lines.append(f"  {key_name}: " + "  ".join(sk[key_name]))

    if brief.ledger_state:
        lines.append("")
        lines.append("LEDGER (open expectations):")
        for entry in brief.ledger_state:
            lines.append(f"  {entry}")

    lc = brief.ledger_constraints or {}
    if any(lc.get(k) for k in ("must_resolve", "must_not_use", "cooldown", "locked")):
        lines.append("")
        lines.append("THIS PHRASE MUST / MUST NOT (binding — long-range coherence):")
        for r in lc.get("must_resolve", []):
            tag = "OVERDUE" if r.get("overdue") else "due now"
            form = f" as {r['form']}" if r.get("form") else ""
            lines.append(
                f"  ✓ resolve {r.get('type')} '{r.get('object')}'{form} "
                f"({tag}, urgency {round(r.get('urgency', 0.5), 2)})"
            )
        for p in lc.get("must_not_use", []):
            form = f" ({p['form']})" if p.get("form") else ""
            lines.append(f"  ✗ do NOT use '{p.get('object')}'{form} — reserved")
        for c in lc.get("cooldown", []):
            lines.append(f"  ✗ '{c.get('object')}' on cooldown — avoid / use sparingly")
        for k in lc.get("locked", []):
            form = f" ({k['form']})" if k.get("form") else ""
            lines.append(f"  ⚓ preserve locked '{k.get('object')}'{form}")

    if brief.transition:
        lines.append("")
        t = brief.transition
        parts = []
        if t.get("previous_phrase"):
            parts.append(f"prev={t['previous_phrase']}")
        if t.get("melody_tail"):
            parts.append("melody tail: " + " ".join(t["melody_tail"]))
        if t.get("last_bass"):
            parts.append(f"last bass: {t['last_bass']}")
        if t.get("last_dynamic"):
            parts.append(f"dynamic: {t['last_dynamic']}")
        lines.append(
            "TRANSITION IN: " + " | ".join(parts) if parts else "TRANSITION IN: (piece opening)"
        )

    ts = brief.target_stats
    lines.append("")
    lines.append(f"TARGET STATS ({brief.composer}):")
    for t, entry in ts.get("rh_textures", {}).items():
        d = entry.get("events_per_bar", {})
        line = (
            f"  RH {t}: median {d.get('median')} events/bar "
            f"(p25 {d.get('p25')}, p75 {d.get('p75')})"
        )
        orn = entry.get("ornament_density")
        if orn:
            top = sorted(orn.items(), key=lambda kv: -kv[1])[:3]
            line += " | ornaments/bar: " + ", ".join(f"{k} {v:.2f}" for k, v in top if v >= 0.01)
        lines.append(line)
    for t, entry in ts.get("lh_textures", {}).items():
        d = entry.get("events_per_bar", {})
        lines.append(
            f"  LH {t}: median {d.get('median')} events/bar "
            f"(p25 {d.get('p25')}, p75 {d.get('p75')})"
        )
    for t, v in ts.get("self_continuation", {}).items():
        lines.append(f"  LH {t} self-continuation {v} — persist but vary, don't photocopy bars")
    if ts.get("whole_phrase_expectation"):
        lines.append(f"  WHOLE PHRASE: {ts['whole_phrase_expectation']}")
    disc = ts.get("discriminators", {})
    if disc:
        lines.append(
            f"  Corpus targets ({brief.composer}): "
            + "; ".join(f"{k}={v}" for k, v in disc.items())
        )

    # ── Composer fingerprints (the voice — write these in) ──
    if brief.fingerprints:
        lines.append("")
        lines.append(f"COMPOSER FINGERPRINTS ({brief.composer} — make the phrase exhibit these):")
        for fp in brief.fingerprints:
            lines.append(f"  • {fp['name']}: {fp['rule']}")

    # ── Phrase-scoped doctrine ──
    doc = brief.doctrine
    if doc:
        lines.append("")
        lines.append("STYLE DOCTRINE (this phrase):")
        cs = doc.get("cadence_script")
        if cs:
            parts = [f"type {cs.get('type')}"]
            if cs.get("approach"):
                parts.append(f"approach {cs['approach']}")
            if cs.get("bass"):
                parts.append(f"bass {cs['bass']}")
            lines.append("  Cadence: " + ", ".join(str(p) for p in parts))
        for intent in doc.get("ornament_intent", []):
            lines.append(f"  Ornament: {intent}")
        for br in doc.get("breathing", []):
            lines.append(f"  Breathe: {br}")
        for dev in doc.get("harmonic_devices", []):
            lines.append(f"  Color: {dev.get('name')} — {dev.get('use')}")
        for mp in doc.get("melody_priors", []):
            lines.append(f"  Melody: {mp}")

    # ── Phrase-level shape (the arc, above the single bar) ──
    ps = brief.phrase_shape
    if ps:
        lines.append("")
        lines.append(
            f"PHRASE SHAPE (corpus {ps.get('source')} bars "
            f"{ps.get('bars')}, role {ps.get('role')}):"
        )
        if ps.get("density_arc"):
            lines.append(f"  density arc: {ps['density_arc']} (peak at bar {ps.get('peak_at')})")
        if ps.get("register_arc"):
            lines.append(f"  register arc: {ps['register_arc']}")

    # ── Cadence pattern ──
    if brief.cadence_exemplars:
        lines.append("")
        lines.append("CADENCE PATTERN (corpus):")
        for c in brief.cadence_exemplars:
            lines.append(
                f"  {c.get('type')}: chords {c.get('chords')} | "
                f"soprano→{c.get('soprano_arrival')} | bass {c.get('bass_motion')}"
            )

    # ── Texture transitions (how to move between textures idiomatically) ──
    tps = brief.transition_patterns
    if tps:
        lines.append("")
        lines.append("TEXTURE TRANSITIONS (corpus):")
        ap = tps.get("after_previous")
        if ap:
            follow = ", ".join(f"{t} {p}" for t, p in ap["follow"])
            lines.append(f"  after prev '{ap['from']}' → {follow}")
        wp = tps.get("within_phrase")
        if wp:
            vary = ", ".join(f"{t} {p}" for t, p in wp.get("vary_toward", []))
            lines.append(
                f"  '{wp['primary']}' self-continues {wp['self_continuation']}"
                f" — vary toward: {vary or '(stay)'}"
            )

    # ── LH vocabulary (canonical real LH patterns) ──
    if brief.lh_vocabulary:
        lines.append("")
        lines.append(
            f"LH VOCABULARY (canonical {brief.composer} patterns, transposed to {s.get('key')}):"
        )
        for v in brief.lh_vocabulary:
            lines.append(f"  {v['texture']}: {v['lh']}")

    lines.append("")
    lines.append(
        f"EXEMPLARS (real {brief.composer} bars, transposed to "
        f"{s.get('key')}; adapt — never copy verbatim, "
        f"never ignore):"
    )
    for i, ex in enumerate(brief.exemplars, 1):
        lines.append(
            f"[E{i}] {ex.source} b{ex.source_bar} "
            f"{ex.rh_texture}/{ex.lh_texture} "
            f"md={ex.melody_density} ad={ex.accomp_density} "
            f"({ex.phrase_position})"
        )
        if ex.rh:
            lines.append(f"   RH: {ex.rh}")
        if ex.lh:
            lines.append(f"   LH: {ex.lh}")
    if not brief.exemplars:
        lines.append("  (none found — see warnings)")

    if brief.anti_patterns:
        lines.append("")
        lines.append("AVOID (AI tells): " + "; ".join(brief.anti_patterns))

    if brief.warnings:
        lines.append("")
        lines.append("WARNINGS: " + "; ".join(brief.warnings))

    return "\n".join(lines)
