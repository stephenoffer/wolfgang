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

import collections
import json
import logging
import re
import statistics
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Optional, Tuple

from .atomic_io import write_json_atomic
from .corpus_adapter import AdaptedBar, CorpusAdapter, CorpusQuery
from .duration import bar_duration, beats_to_dur, dur_to_beats
from .pitch import is_minor_key, pitch_to_midi

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
_ORNAMENT_CACHE: Dict[str, Any] = {}
_FINGERPRINT_CACHE: Dict[str, Any] = {}
_SCOPE_CACHE: Dict[str, Any] = {}
_TEXTURE_TEMPLATE_CACHE: Dict[str, Dict[str, Any]] = {}
_PACK_CACHE: Dict[str, Any] = {}  # compiled_packs/<composer>/<name>.json
_PACK_SOURCE: Dict[str, str] = {}  # which id actually supplied each cached pack


def _pack_dir(composer: str) -> str:
    """Filesystem-safe pack directory for a composer/style/blend id.

    Reads must use the same mapping the compiler writes with, or a blended
    style silently reads no pack at all and the brief falls back to generic
    numbers without saying so. See `style_registry.pack_dir_name`.
    """
    from .style_registry import pack_dir_name

    try:
        return pack_dir_name(composer)
    except ValueError:
        return ""


_PROFILE_CACHE: Dict[str, Dict[str, Any]] = {}
_PHRASE_BANK_CACHE: Dict[str, Any] = {}
_CADENCE_BANK_CACHE: Dict[str, Any] = {}
_PATTERN_RETRIEVER = None  # shared across composers (one library)


def _aggregate_members(composer: str):
    """Member composers if `composer` is an AGGREGATE reference, else None.

    Both a style (``style__<name>``) and a blend (``blend:a+b+c``) draw on the
    real corpora of their armed members — so a blend of two armed composers is
    grounded in actual bars exactly as a style is, instead of resolving to an
    empty id and forcing the agent to compose blind.
    """
    from .style_registry import is_style_id, style_members, style_name

    if composer and composer.startswith("blend:"):
        return [m.strip() for m in composer[6:].replace("+", ",").split(",") if m.strip()]
    if is_style_id(composer):
        return style_members(style_name(composer)) or None
    return None


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
    path = _COMPILED_PACKS / _pack_dir(composer) / f"{name}.json"
    data: Any = None
    if path.exists():
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = None
    if data is None:
        members = _aggregate_members(composer)
        if members:
            for member in members:
                member_pack = _load_pack(member, name)
                if member_pack:
                    data = member_pack
                    # Which member stood in. A style with no pack of its own
                    # gets ONE member's doctrine — Haydn's cadence scripts and
                    # ornament intents were printed under "STYLE DOCTRINE" for
                    # `style__classical` with nothing saying they were his
                    # rather than the style's. The substitution is reasonable;
                    # making it silent is the part this project keeps paying for.
                    _PACK_SOURCE[key] = member
                    break
    _PACK_CACHE[key] = data
    return data


def pack_source(composer: str, name: str) -> str:
    """Which id actually supplied a pack — the reference itself, or the member
    that stood in for an aggregate that has no pack of its own."""
    key = f"{composer}/{name}"
    if key not in _PACK_CACHE:
        _load_pack(composer, name)
    return _PACK_SOURCE.get(key, composer)


def corpus_profile(composer: str) -> Dict[str, Any]:
    """Per-composer metric distribution profile (corpus_profile.json), cached.

    A profile written by an older build is worse than no profile: `self_evaluate`
    narrows its discriminator bands to `mean ± 2σ` from these numbers, so stale
    values silently become the standard a section is judged against.

    Staleness is detected from the metric vocabulary rather than a version
    field, because there is no version field and adding one would not help the
    files already on disk. `melody_direction_change_pct` is the marker: it was
    renamed from `direction_changes_per_bar` precisely because that name was
    being used for **two different quantities** — a fraction of bars whose
    direction label changes (~0.55) and a per-bar count of contour reversals
    (~1-3). A profile still carrying the old name predates the rename, and every
    other metric in it predates the rename too.
    """
    if composer in _PROFILE_CACHE:
        return _PROFILE_CACHE[composer]
    data = _load_pack(composer, "corpus_profile") or {}
    metrics = data.get("metrics") if isinstance(data, dict) else None
    if isinstance(metrics, dict) and metrics and "melody_direction_change_pct" not in metrics:
        # Discarding the stale profile is right; leaving nothing in its place is
        # not. An AGGREGATE reference (a style or a `blend:a+b`) has armed
        # members whose own profiles are current, and `build_corpus_profiles`
        # — the rebuild this used to recommend — does not write aggregate packs
        # at all, so for a blend the advice named a command that could not fix
        # it. `blend__beethoven-liszt/corpus_profile.json` has sat two months
        # stale beside a `density_stats.json` rebuilt this month, and every
        # piece on that blend was compared against nothing.
        members = _aggregate_members(composer) or []
        fallback = next((corpus_profile(m) for m in members if corpus_profile(m)), {})
        if fallback:
            logger.warning(
                "corpus_profile for %r predates the metric rename; using %s's "
                "current profile instead. This is a SUBSTITUTION, not %r's own "
                "distribution — rebuild the aggregate pack to judge it against "
                "itself.",
                composer,
                members[0] if members else "?",
                composer,
            )
            data = fallback
        else:
            logger.warning(
                "corpus_profile for %r predates the metric rename (no "
                "melody_direction_change_pct); ignoring it rather than judging a "
                "section against stale numbers. Rebuild with "
                "`.venv/bin/python -m scripts.build_corpus_profiles`.",
                composer,
            )
            data = {}
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
    # Where the harmony moves INSIDE this real bar, e.g. "1:ii6 2:I64 3:V7".
    # Two thirds of Mozart's bars carry more than one functional harmony; showing
    # only a bar's headline chord taught a harmonic rhythm of one chord per bar.
    harmony: str = ""


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
    # Named idioms from the composer's own pack, with the notes and the
    # expression already on them. See _gestures.
    gestures: List[Dict[str, Any]] = field(default_factory=list)
    # Real shapes from the corpus, indexed by what they DO. See _corpus_gestures.
    corpus_gestures: List[Dict[str, Any]] = field(default_factory=list)
    # Written rules / doctrine (WS-C) — the composer's voice + phrase-scoped craft
    fingerprints: List[Dict[str, str]] = field(default_factory=list)
    doctrine: Dict[str, Any] = field(default_factory=dict)
    anti_patterns: List[str] = field(default_factory=list)
    # Human-composer methodology: the FEELING this moment must convey, the
    # per-beat chord frame to voice against (prevents clashes), and the real
    # composed theme + a suggested development for this section.
    creative_intent: str = ""
    #: Everything in the piece that names a FEELING — see `_feeling_text`.
    #: Held on the brief because `render_text` has no graph to ask.
    feeling_text: str = ""
    # The MOTIFS this phrase must state or transform (motif_bank + slot plan).
    motifs: List[Dict[str, Any]] = field(default_factory=list)
    # What this phrase is FOR (dramatic_plan): role, climax distance, return
    # strategy, key journey, forward context, register arc.
    dramatic: List[str] = field(default_factory=list)
    chord_frame: List[Dict[str, Any]] = field(default_factory=list)
    theme_block: Dict[str, str] = field(default_factory=dict)
    # The agent's OWN analysis of whole reference scores it studied at plan time
    # (form, themes, harmonic language, what makes them work) — its understanding
    # of real music, fed forward so every phrase composes from it.
    lock_contract: List[str] = field(default_factory=list)
    reference_study: List[Dict[str, str]] = field(default_factory=list)
    # How well this composer is actually armed. Composing "as Corelli" from 19
    # bars is a different act from composing as Mozart from 7,022, and the brief
    # said so only obliquely, through scattered "no corpus stats for texture X"
    # warnings the agent had to add up for itself.
    coverage: Dict[str, Any] = field(default_factory=dict)


# ─── Composer resolution ─────────────────────────────────────────────────────


_VOICING_CACHE: Dict[str, Any] = {}
#: Below this many measured attacks the shares are noise, not a profile.
_VOICING_MIN_ATTACKS = 200
_VOICING_MAX_BARS = 4000
#: One source's scoring is not a composer's habit — see the note at the guard.
_VOICING_MIN_SOURCES = 3


def _event_midis(event: Dict[str, Any]) -> List[int]:
    """MIDI numbers of one corpus display event; empty for a rest."""
    kind = event.get("type")
    if kind == "chord":
        pitches = event.get("pitches") or []
    elif kind == "note":
        pitches = [event.get("pitch")]
    else:
        return []
    out: List[int] = []
    for pitch in pitches:
        if not pitch:
            continue
        try:
            out.append(pitch_to_midi(pitch))
        except (ValueError, KeyError, TypeError):
            continue
    return out


_MUDDY_RATE_CACHE: Dict[str, Optional[float]] = {}


def muddy_low_interval_rate(composer: str) -> Optional[float]:
    """How often this composer writes two notes a 2nd-to-3rd apart below C3.

    "Avoid thirds below C3" is an editor's rule of thumb, and real composers
    disagree with it by an order of magnitude — Liszt 0.094 per bar, Beethoven
    0.023, Mozart 0.0077, Haydn 0.0007, Palestrina exactly 0.0000 across 60,677
    bars. A count with no scale attached cannot tell a reviewer whether what they
    are looking at is a defect or the idiom, which is what
    `feedback_percentile_is_not_the_bound` and the composer-relative floors in
    `voicing.py` are both about. Returns None when the composer has no corpus.
    """
    key = (composer or "").lower()
    if key in _MUDDY_RATE_CACHE:
        return _MUDDY_RATE_CACHE[key]
    from .pitch import pitch_to_midi

    hits = bars = 0
    for bar in _iter_corpus_bars(composer):
        bars += 1
        for side in ("lh_display", "rh_display"):
            found = False
            for event in bar.get(side) or []:
                if not isinstance(event, dict) or event.get("type") != "chord":
                    continue
                midis = sorted(
                    m for m in ((pitch_to_midi(p) or 0) for p in (event.get("pitches") or [])) if m
                )
                if any(hi < 48 and 1 <= hi - lo <= 4 for lo, hi in zip(midis, midis[1:])):
                    hits += 1
                    found = True
                    break
            if found:
                break
    rate = (hits / bars) if bars else None
    _MUDDY_RATE_CACHE[key] = rate
    return rate


def voicing_profile(composer: str) -> Optional[Dict[str, Any]]:
    """How THICK this composer's writing is, measured from his own bars.

    The brief told the agent what the left hand plays, how dense the bar is and
    which rhythms recur — and never once how many notes are sounding in the
    melody. So a Chopin nocturne came back with a right hand that is a single
    line in 99% of its attacks, against a real Chopin figure of 22%, and nothing
    anywhere remarked on it: per-movement the 10th percentile of chord share is
    0.00, because some real movements genuinely are single-line, so no
    distribution test can catch a piece that is single-line ALL the way through.
    It is not a defect a threshold finds. It is something the composer has to be
    told before writing.

    Measured over the corpus (share of right-hand attacks that sound more than
    one note, median span of each hand within a bar, median gap between the
    hands):

        liszt       50.5%   the right hand is chordal half the time
        debussy     28.4%
        chopin      21.9%
        beethoven   17.7%
        brahms      16.9%
        schubert    15.8%
        mozart       8.4%
        handel       6.9%
        haydn        6.3%
        bach         0.7%   counterpoint: one note per voice, by definition
        palestrina   0.0%   vocal parts do not play chords

    A single number could not serve that range, which is why this is measured
    per composer and why "add some chords" is not the guidance. Returns None
    when the corpus cannot support the measurement.
    """
    if composer in _VOICING_CACHE:
        return _VOICING_CACHE[composer]
    # A style is the union of its members, but `_iter_corpus_bars` yields them
    # one composer at a time and the bar cap below would stop inside the FIRST
    # one — so `style__romantic` came back as Chopin's numbers exactly, to three
    # decimal places, which is what gave it away. Aggregate the members' own
    # profiles instead, weighted by how much each was measured on.
    members = _aggregate_members(composer)
    if members:
        parts = [(m, voicing_profile(m)) for m in members]
        parts = [(m, p) for m, p in parts if p]
        total = sum(p["attacks"] for _m, p in parts)
        if not total:
            _VOICING_CACHE[composer] = None
            return None
        blended = {
            key: sum(p[key] * p["attacks"] for _m, p in parts) / total
            for key in (
                "rh_chord_share",
                "rh_chord_size",
                "lh_chord_share",
                "lh_chord_size",
                "lh_span",
                "rh_span",
                "hand_gap",
            )
        }
        blended["rh_chord_share"] = round(blended["rh_chord_share"], 3)
        blended["rh_chord_size"] = round(blended["rh_chord_size"], 2)
        blended["lh_chord_share"] = round(blended["lh_chord_share"], 3)
        blended["lh_chord_size"] = round(blended["lh_chord_size"], 2)
        for key in ("lh_span", "rh_span", "hand_gap"):
            blended[key] = int(round(blended[key]))
        blended["attacks"] = total
        blended["members"] = len(parts)
        _VOICING_CACHE[composer] = blended
        return blended
    profile = None
    try:
        chords = attacks = 0
        lh_chords = lh_attacks = 0
        sizes: List[int] = []
        lh_sizes: List[int] = []
        lh_spans: List[int] = []
        rh_spans: List[int] = []
        gaps: List[int] = []
        sources: set = set()
        for seen, bar in enumerate(_iter_corpus_bars(composer)):
            if seen > _VOICING_MAX_BARS:
                break
            sources.add(bar.get("source"))
            rh_mid: List[int] = []
            lh_mid: List[int] = []
            for event in bar.get("rh_display") or []:
                if not isinstance(event, dict) or event.get("type") == "rest":
                    continue
                midis = _event_midis(event)
                if not midis:
                    continue
                attacks += 1
                rh_mid.extend(midis)
                # DISTINCT pitches: two voices doubling a unison arrive as a
                # two-note "chord" (1,471 of them in the corpus), and counting
                # that as thickness overstates how chordal the hand is. The span
                # above is unaffected either way, so only the chord test moves.
                distinct = set(midis)
                if len(distinct) > 1:
                    chords += 1
                    sizes.append(len(distinct))
            for event in bar.get("lh_display") or []:
                if not isinstance(event, dict) or event.get("type") == "rest":
                    continue
                midis = _event_midis(event)
                if not midis:
                    continue
                # THE LEFT HAND'S THICKNESS, which this measured for the right
                # hand only. The composer was told the melody is 8% chords and
                # nothing at all about the accompaniment — which in real Mozart
                # is 18.5%, more than double, and ranges from Haydn's 11.9% to
                # Chopin's 37.9% over 164,000 attacks. The engine wrote 0.0%
                # until this was measured, and its accompaniment had 11 distinct
                # bar-shapes where real Mozart 3/8 has at least 14.
                lh_attacks += 1
                lh_mid.extend(midis)
                lh_distinct = set(midis)
                if len(lh_distinct) > 1:
                    lh_chords += 1
                    lh_sizes.append(len(lh_distinct))
            if rh_mid:
                rh_spans.append(max(rh_mid) - min(rh_mid))
            if lh_mid:
                lh_spans.append(max(lh_mid) - min(lh_mid))
            if rh_mid and lh_mid:
                gaps.append(min(rh_mid) - max(lh_mid))
        # A count of attacks is not enough on its own. Weber's whole corpus is
        # ONE clarinet work, and a clarinet cannot play a chord — so 1,200
        # attacks yielded a confident 0.0% and would have told the composer to
        # write a Romantic piano piece as a bare single line. The scoring of one
        # source is not a composer's habit.
        if attacks >= _VOICING_MIN_ATTACKS and len(sources) >= _VOICING_MIN_SOURCES:
            profile = {
                "rh_chord_share": round(chords / attacks, 3),
                "rh_chord_size": round(mean(sizes), 2) if sizes else 0.0,
                "lh_chord_share": round(lh_chords / lh_attacks, 3) if lh_attacks else 0.0,
                "lh_chord_size": round(mean(lh_sizes), 2) if lh_sizes else 0.0,
                "lh_span": int(median(lh_spans)) if lh_spans else 0,
                "rh_span": int(median(rh_spans)) if rh_spans else 0,
                "hand_gap": int(median(gaps)) if gaps else 0,
                "attacks": attacks,
            }
    except Exception:
        profile = None
    _VOICING_CACHE[composer] = profile
    return profile


def piece_forces(graph) -> tuple[str, str, bool]:
    """What to call the two staves of a corpus exemplar, for THIS piece's forces.

    The brief never knew what the piece was scored for — the word
    "instrumentation" did not appear in this file. So a four-voice motet was
    briefed entirely in "RH:" and "LH:", and told its composer "each hand spans
    about 3 semitones; the hands sit about 15 semitones apart". A choir has no
    hands, and the composer reading that has to translate it before it means
    anything.

    The corpus bar records really are a two-hand reduction, so the labels change
    but the claim does not: for anything not played at a keyboard the two staves
    are the upper and lower voices of the texture.

    Returns ``(upper_label, lower_label, keyboard)``.
    """
    from .models import is_keyboard

    target = getattr(getattr(graph, "contract", None), "target", None)
    if isinstance(target, dict):
        instrumentation = target.get("instrumentation") or ""
    else:
        instrumentation = getattr(target, "instrumentation", "") or ""
    if is_keyboard(instrumentation):
        return ("RH", "LH", True)
    return ("UPPER", "LOWER", False)


def voicing_lines(composer: str, graph=None, movement_id: str = "") -> List[str]:
    """The VOICING section of the brief, or nothing when unmeasurable."""
    profile = voicing_profile(composer)
    if not profile:
        return []
    share = profile["rh_chord_share"]
    if share >= 0.30:
        how = (
            f"The melody is CHORDAL — {round(share * 100)}% of right-hand attacks sound "
            f"{profile['rh_chord_size']:.1f} notes on average. Write the tune in octaves, "
            "thirds and full chords far more often than as a single line."
        )
    elif share >= 0.12:
        how = (
            f"{round(share * 100)}% of right-hand attacks are more than one note "
            f"({profile['rh_chord_size']:.1f} notes on average) — the melody is doubled in "
            "thirds or sixths, or thickened into a chord, roughly every fourth or fifth note. "
            "A tune that is a bare single line throughout is the commonest way this comes out "
            "thin."
        )
    elif share >= 0.03:
        how = (
            f"The melody is mostly a single line: only {round(share * 100)}% of right-hand "
            "attacks carry more than one note, saved for accents and cadences."
        )
    else:
        how = (
            "The right hand is a SINGLE LINE — this idiom does not thicken the melody. "
            "Independent voices, not chords."
        )
    upper, lower, keyboard = piece_forces(graph)
    if not keyboard:
        # Same measurement, in words that mean something to a composer writing
        # for voices or an ensemble. "Each hand spans" is not a fact about them.
        how = how.replace("right-hand", "upper-voice").replace("right hand", "upper line")
        spacing = (
            f"  The upper voices span about {profile['rh_span']} semitones within a bar and "
            f"the lower about {profile['lh_span']}; the two groups sit about "
            f"{profile['hand_gap']} semitones apart."
        )
    else:
        spacing = (
            f"  Each hand spans about {profile['lh_span']} semitones (LH) and "
            f"{profile['rh_span']} (RH) within a bar; the hands sit about "
            f"{profile['hand_gap']} semitones apart."
        )
    # THE LEFT HAND HAS A THICKNESS TOO, and this section reported only its
    # SPAN — so the composer was told the melody is 8% chords and nothing about
    # the accompaniment, which in real Mozart is 21%, more than double. It is
    # not a smaller version of the same instruction either: Bach's right hand is
    # thicker than his left, and every keyboard composer's left hand is thicker
    # than his right.
    lh_share = profile.get("lh_chord_share") or 0.0
    lh_size = profile.get("lh_chord_size") or 0.0
    if lh_share >= 0.25:
        lh_how = (
            f"  The accompaniment is CHORDAL — {round(lh_share * 100)}% of left-hand attacks "
            f"sound {lh_size:.1f} notes. Full chords under the tune, not a single bass line."
        )
    elif lh_share >= 0.08:
        lh_how = (
            f"  The left hand plays a chord on {round(lh_share * 100)}% of its attacks "
            f"({lh_size:.1f} notes) — an oom-pah, a broken chord that closes into a block, "
            "a held third under a moving bass. An accompaniment of single notes throughout "
            "is the commonest way the texture comes out thin."
        )
    elif lh_share > 0:
        lh_how = (
            f"  The left hand is nearly always a single line — only "
            f"{round(lh_share * 100)}% of its attacks carry a chord."
        )
    else:
        lh_how = "  The lower part is a single line; this idiom does not chord beneath the tune."
    if not keyboard:
        lh_how = lh_how.replace("left-hand", "lower-voice").replace("left hand", "lower line")
        lh_how = lh_how.replace("accompaniment", "lower voices")

    lines = [
        "",
        f"VOICING (how thick, measured over {profile['attacks']} real {composer} attacks):",
        f"  {how}",
        lh_how,
        spacing,
    ]
    # ...and where THIS piece actually sits. The target alone has not moved the
    # output: a nocturne came out with a bare single line in 93% of bars against
    # a real Chopin range of 5-63%, with this very section stating 21% in front
    # of the composer the whole time. A target is a number to agree with; a gap
    # is a number to act on, and MARKS SO FAR earns its place the same way.
    if graph is not None:
        got = _rh_thickness_so_far(graph, movement_id)
        if got is not None:
            target = profile.get("rh_chord_share") or 0.0
            verdict = (
                "already there"
                if got >= target * 0.8
                else f"about {target / got:.0f}x thinner than his"
                if got
                else "not once so far — a bare single line the whole way"
            )
            lines.append(
                f"  THICKNESS SO FAR: {got:.0%} of your right-hand attacks are more "
                f"than one note, against his {target:.0%} — {verdict}."
            )
        # The same gap for the hand that carries more of the weight. Reporting
        # only the melody's meant a piece could sit at the composer's own
        # right-hand figure with a bass of bare single notes throughout and
        # nothing here would say so.
        lh_got = _lh_thickness_so_far(graph, movement_id)
        if lh_got is not None and lh_share:
            lh_verdict = (
                "already there"
                if lh_got >= lh_share * 0.8
                else f"about {lh_share / lh_got:.0f}x thinner than his"
                if lh_got
                else "not once so far — a bass of bare single notes"
            )
            lines.append(
                f"  LEFT-HAND THICKNESS SO FAR: {lh_got:.0%} against his "
                f"{lh_share:.0%} — {lh_verdict}."
            )
    return lines


def _narrative_section_for(graph, slot):
    """The narrative section covering this phrase, in the right movement.

    Falls back to the section's `id`/`label` prefix when `movement_id` is unset,
    so narratives written before the field existed still resolve correctly if
    they named their movement (`"m2_open"`).
    """
    nar = getattr(graph, "narrative", None)
    sections = list(getattr(nar, "sections", None) or []) if nar else []
    if not sections:
        return None
    bar = getattr(slot, "bar_start", 0) or 0
    mid = (getattr(slot, "section_id", "") or "").split("_", 1)[0]

    from .models import narrative_section_is_in_movement

    covering = [s for s in sections if s.bar_start <= bar <= s.bar_end]
    return next((s for s in covering if narrative_section_is_in_movement(s, mid)), None)


def _phrases_before(graph, slot):
    """Phrases that precede ``slot`` in PERFORMANCE order, across movements.

    Bar numbers restart per movement, so `other.bar_start < slot.bar_start` is
    not "earlier" in a multi-movement work — for a phrase at bar 20 of movement
    two it admits movement one's bars 1-19 and rejects its bars 20-38. Anything
    reasoning about what the piece has already done needs (movement index, bar),
    not bar alone.

    Motif history is deliberately WORK-wide rather than movement-scoped: a theme
    stated in the first movement and taken up in the third is cyclic form, not
    repetition, and the composer of the third movement needs to know.
    """
    movements = [
        getattr(m, "id", "")
        for m in (getattr(getattr(graph, "work_graph", None), "movements", None) or [])
    ]

    def order(section_id: str) -> int:
        mid = (section_id or "").split("_", 1)[0]
        return movements.index(mid) if mid in movements else 0

    here_section = getattr(slot, "section_id", "") or ""
    here = (order(here_section), getattr(slot, "bar_start", 0) or 0)
    out = []
    for st in (getattr(graph, "phrases", {}) or {}).values():
        s2 = getattr(st, "slot", None)
        if s2 is None:
            continue
        there = (order(getattr(s2, "section_id", "") or ""), getattr(s2, "bar_start", 0) or 0)
        if there < here:
            out.append(st)
    return out


def _phrases_in_scope(graph, movement_id: str = ""):
    """Committed phrases that belong to the SAME MOVEMENT as ``slot``.

    Every "so far" figure in the brief describes what the composer has written
    up to now, and in a multi-movement work "up to now" must mean this movement.
    Reporting the opening allegro's rest rate and articulation counts to the
    slow movement mixes two pieces of music with genuinely different habits —
    the same mistake as telling three movements each that they hold the climax
    of the whole piece (Addendum 65), one measurement layer down.

    Single-movement pieces are unaffected: every phrase is in scope.
    """
    states = list((getattr(graph, "phrases", {}) or {}).values())
    movements = getattr(getattr(graph, "work_graph", None), "movements", None) or []
    mid = (movement_id or "").split("_", 1)[0]
    if not mid or len(movements) < 2:
        return states
    scoped = [
        st
        for st in states
        if (getattr(getattr(st, "slot", None), "section_id", "") or "").split("_", 1)[0] == mid
    ]
    return scoped or states


_RH_LAYERS = ("principal_line", "response_layer", "ornamental_surface")
_LH_LAYERS = ("bass_foundation",)


def _thickness_so_far(graph, movement_id: str, layers) -> Optional[float]:
    """Share of committed attacks in these layers that sound more than one note.

    A CHORD HAS TWO REPRESENTATIONS HERE and this counted only one. The agent
    path writes `[E4,G4,C5]` and arrives as a single event with a list pitch;
    the engine writes coincident events at one instant. Testing
    `isinstance(pitch, list)` therefore reported **0.0%** on an engine-realized
    piece whose right hand was in fact thickened 10.3% of the time — and the
    brief told its composer "not once so far — a bare single line the whole
    way", about a piece already at Mozart's own rate. Wrong in the direction
    that makes someone act.

    Counted per INSTANT, which is also the unit the corpus side uses: one
    three-note chord is one attack there, so it must be one attack here.
    """
    multi = total = 0
    for state in _phrases_in_scope(graph, movement_id):
        layer = getattr(state, "realized", None)
        if layer is None:
            continue
        at_instant: Dict[Any, int] = {}
        for name in layers:
            for e in getattr(layer, name, None) or []:
                pitch = getattr(e, "pitch", None)
                if not pitch or pitch == "rest":
                    continue
                voices = len({str(p) for p in pitch}) if isinstance(pitch, list) else 1
                key = (name, e.bar, round(float(e.beat), 4))
                at_instant[key] = at_instant.get(key, 0) + voices
        total += len(at_instant)
        multi += sum(1 for n in at_instant.values() if n > 1)
    return (multi / total) if total else None


def _rh_thickness_so_far(graph, movement_id: str = "") -> Optional[float]:
    """Share of committed right-hand attacks that are more than one note."""
    return _thickness_so_far(graph, movement_id, _RH_LAYERS)


def _lh_thickness_so_far(graph, movement_id: str = "") -> Optional[float]:
    """The same for the left hand, which nothing measured."""
    return _thickness_so_far(graph, movement_id, _LH_LAYERS)


_TIE_RATE_CACHE: Dict[str, Any] = {}

#: Used when a composer's own rate cannot be measured. Between Mozart's 0.070
#: and Beethoven's 0.134, so it errs toward the middle of real practice rather
#: than toward either extreme.
_DEFAULT_TIE_RATE = 0.07


def tie_rate_per_bar(composer: str) -> Optional[float]:
    """How often this composer holds a line across a barline, per bar.

    Real practice varies by a factor of eight and a fixed rate cannot serve it:

        palestrina 0.192   beethoven 0.134   chopin 0.071
        mozart     0.070   bach      0.019   haydn  0.015

    The suspension IS Renaissance polyphony, and a Haydn quartet movement holds
    almost nothing over a barline. A generator tying at one rate is wrong for
    everyone except whoever it was tuned on.

    **A zero is not an answer here.** Schubert, Liszt and Brahms all read 0.000
    across thousands of bars — their sources are MIDI and kern editions that
    carry no ties at all, which is a fact about the encoding and not about the
    music. Returning 0.0 for them would tell the composer to write a Schubert
    impromptu with nothing held anywhere. Unmeasurable returns None, and the
    caller uses the generic rate.
    """
    key = (composer or "").strip().lower()
    if key in _TIE_RATE_CACHE:
        return _TIE_RATE_CACHE[key]
    rate = None
    try:
        bars = ties = 0
        for bar in _iter_corpus_bars(composer):
            bars += 1
            for event in bar.get("rh_events") or []:
                if isinstance(event, dict) and event.get("tie") == "start":
                    ties += 1
        if bars >= 200 and ties > 0:
            rate = round(ties / bars, 4)
    except Exception:
        rate = None
    _TIE_RATE_CACHE[key] = rate
    return rate


_MOVEMENT_RATES_CACHE: Dict[str, Any] = {}

#: What a movement is measured on. Each is a share of the movement's own bars or
#: attacks, so they are comparable across movements of different lengths.
MOVEMENT_METRICS = ("ties_per_bar", "downbeat_rest_share", "lh_chord_share", "rh_chord_share")


def movement_rates(composer: str) -> List[Dict[str, Any]]:
    """Per-MOVEMENT texture rates, not the composer's mean.

    A composer's average is the wrong grain for a piece that has a character.
    Mozart ties on 7.0% of bars and opens 8.3% with a rest — but his C minor
    slow movement `sonata14-3` ties in 15% of bars and opens 12% with a rest,
    twice his mean in both. That is not noise; it is what a slow movement in a
    minor key does, and a generated piece asked to be sustained has more in
    common with that movement than with Mozart.

    So: one row per movement, each a share of that movement's own bars, with
    enough of them that a caller can ask for a *range* rather than a point.
    Movements under 24 bars are excluded — a share over a dozen bars is noise,
    and the corpus splits some theme-and-variations sets into single variations.
    """
    key = (composer or "").strip().lower()
    if key in _MOVEMENT_RATES_CACHE:
        return _MOVEMENT_RATES_CACHE[key]

    from collections import defaultdict

    by_source: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
    try:
        for bar in _iter_corpus_bars(composer):
            by_source[bar.get("source")].append(bar)
    except Exception:
        _MOVEMENT_RATES_CACHE[key] = []
        return []

    rows: List[Dict[str, Any]] = []
    for source, bars in by_source.items():
        if len(bars) < 24:
            continue
        ties = rests = 0
        lh_attacks = lh_chords = rh_attacks = rh_chords = 0
        for bar in bars:
            rh = bar.get("rh_events") or []
            if rh:
                first = rh[0]
                if isinstance(first, dict) and first.get("type") == "rest":
                    rests += 1
            for event in rh:
                if not isinstance(event, dict):
                    continue
                if event.get("tie") == "start":
                    ties += 1
                if event.get("type") in ("note", "chord"):
                    rh_attacks += 1
                    if event.get("type") == "chord":
                        rh_chords += 1
            for event in bar.get("lh_events") or []:
                if isinstance(event, dict) and event.get("type") in ("note", "chord"):
                    lh_attacks += 1
                    if event.get("type") == "chord":
                        lh_chords += 1
        rows.append(
            {
                "source": source,
                "bars": len(bars),
                "ties_per_bar": round(ties / len(bars), 4),
                "downbeat_rest_share": round(rests / len(bars), 4),
                "lh_chord_share": round(lh_chords / lh_attacks, 4) if lh_attacks else 0.0,
                "rh_chord_share": round(rh_chords / rh_attacks, 4) if rh_attacks else 0.0,
            }
        )
    rows.sort(key=lambda r: str(r["source"]))
    _MOVEMENT_RATES_CACHE[key] = rows
    return rows


def movement_rate_range(composer: str, metric: str) -> Optional[Dict[str, float]]:
    """The spread of one metric across a composer's movements.

    `{"min", "p25", "median", "p75", "max", "movements"}`, or None when the
    corpus cannot support it. A caller wanting "sustained" can reach for `p75`
    and one wanting "plain" for `p25`, instead of every piece by one composer
    getting the same number.
    """
    if metric not in MOVEMENT_METRICS:
        return None
    values = sorted(row[metric] for row in movement_rates(composer))
    if len(values) < 4:
        return None

    def _at(q: float) -> float:
        return values[min(len(values) - 1, int(q * (len(values) - 1)))]

    return {
        "min": values[0],
        "p25": _at(0.25),
        "median": _at(0.5),
        "p75": _at(0.75),
        "max": values[-1],
        "movements": len(values),
    }


_DOWNBEAT_REST_CACHE: Dict[str, Optional[float]] = {}


def downbeat_rest_rate(composer: str) -> Optional[float]:
    """How often this composer's melody lets a bar BEGIN with silence.

    A bar can lack a fresh downbeat attack two ways: the previous note is held
    across the barline, or the bar simply opens with a rest. `tie_rate_per_bar`
    covers the first. This is the second, and it is the larger share — real
    melodies rest on 5-12% of downbeats where they tie on 1-5%:

        median movement:  beethoven 0.088  schubert 0.077  mozart 0.073
                          haydn     0.042  chopin    0.030  bach   0.027
        pooled over bars: beethoven 0.111  schubert 0.116  mozart 0.083
                          haydn     0.075  chopin    0.089  bach   0.053

    Measured on the melody staff only. The accompaniment rests on downbeats at
    its own, different rates (Haydn 16.8%, Bach 4.6%) and a shared number would
    be right for neither.

    The two columns above are the correction: every pooled figure sits ABOVE its
    own median because the distribution is right-skewed, so composing to the
    aggregate writes a piece more sustained than most of what the composer
    actually wrote — Chopin by a factor of three.

    Unmeasurable returns None, as with ties — but for the opposite reason. A
    zero here would be a real finding rather than a missing encoding, since a
    rest is present in a source or it is not; the floor on sample size is what
    guards it.
    """
    key = (composer or "").strip().lower()
    if key in _DOWNBEAT_REST_CACHE:
        return _DOWNBEAT_REST_CACHE[key]

    # THE MEDIAN MOVEMENT, not the mean of every bar.
    #
    # A piece has a character and resembles some movement of a composer, never
    # the average of all of them. The two differ by more than rounding: Chopin's
    # bars rest on 8.9% of downbeats in aggregate and his MEDIAN movement on
    # 3.0%; Bach 5.3% against 2.7%. Both distributions are right-skewed — a few
    # movements rest a great deal — so the aggregate describes a piece more
    # sustained than most of what the composer wrote.
    #
    # This is the same correction the tie rate needed for a starker reason:
    # Haydn's median movement ties ZERO times, and his aggregate of 0.015 is a
    # number no movement of his resembles.
    rate = None
    try:
        spread = movement_rate_range(composer, "downbeat_rest_share")
        if spread and spread.get("median") is not None:
            rate = round(float(spread["median"]), 4)
    except Exception:
        rate = None
    if rate is not None:
        _DOWNBEAT_REST_CACHE[key] = rate
        return rate

    # Fall back to the pooled rate when there are too few movements to have a
    # median — a composer armed from three sources still gets an answer.
    try:
        bars = opening_rests = 0
        for bar in _iter_corpus_bars(composer):
            events = bar.get("rh_display") or []
            if not events:
                continue
            bars += 1
            first = min(events, key=lambda e: float(e.get("beat", e.get("offset", 0)) or 0))
            if first.get("type") == "rest":
                opening_rests += 1
        if bars >= 200:
            rate = round(opening_rests / bars, 4)
    except Exception:
        rate = None
    _DOWNBEAT_REST_CACHE[key] = rate
    return rate


_MOTION_CACHE: Dict[str, Any] = {}


def motion_profile(composer: str) -> Optional[Dict[str, Any]]:
    """How this composer's music MOVES — by step or by leap, how fast the
    harmony turns over, and where on the keyboard it lives.

    Three facts the brief never carried, each with a spread far too wide for a
    default to serve. Measured over the corpus:

        melodic motion       harmonic rhythm        lowest note
        monteverdi 86% step  bach       2.60/bar    liszt    39
        bach       86% step  palestrina 2.41/bar    brahms   39
        palestrina 81% step  handel     2.26/bar    schubert 44
        chopin     67% step  debussy    2.22/bar    chopin   46
        mozart     60% step  mozart     1.86/bar    mozart   53
        beethoven  53% step  chopin     1.68/bar    haydn    52
        debussy    44% step  beethoven  1.61/bar    palestr. 53
        liszt      36% step  schubert   1.45/bar

    Liszt leaps where Monteverdi steps; Bach turns his harmony nearly twice as
    often as Schubert; and the bottom of Liszt's keyboard is a minor seventh
    below the bottom of Mozart's. A generated piece that steps politely through
    the middle of the keyboard changing chord once a bar is plausible for
    nobody in particular — which is exactly how "generic" sounds.

    Same guards as `voicing_profile`: silent below the sample and source floors,
    and a style aggregates its members rather than reporting its first.
    """
    if composer in _MOTION_CACHE:
        return _MOTION_CACHE[composer]
    members = _aggregate_members(composer)
    if members:
        parts = [(m, motion_profile(m)) for m in members]
        parts = [(m, prof) for m, prof in parts if prof]
        total = sum(prof["intervals"] for _m, prof in parts)
        if not total:
            _MOTION_CACHE[composer] = None
            return None
        blended = {
            key: sum(prof[key] * prof["intervals"] for _m, prof in parts) / total
            for key in ("step_share", "leap_share", "harmonies_per_bar")
        }
        blended = {k: round(v, 3) for k, v in blended.items()}
        blended["low"] = min(prof["low"] for _m, prof in parts)
        blended["high"] = max(prof["high"] for _m, prof in parts)
        blended["intervals"] = total
        blended["members"] = len(parts)
        _MOTION_CACHE[composer] = blended
        return blended

    profile = None
    try:
        steps = leaps = wide = 0
        harmonies: List[int] = []
        lows: List[int] = []
        highs: List[int] = []
        sources: set = set()
        bars = 0
        for seen, bar in enumerate(_iter_corpus_bars(composer)):
            if seen > _VOICING_MAX_BARS:
                break
            bars += 1
            sources.add(bar.get("source"))
            line = [
                e.get("midi")
                for e in (bar.get("melody_line") or [])
                if isinstance(e, dict) and e.get("midi")
            ]
            for first, second in zip(line, line[1:]):
                gap = abs(second - first)
                if gap <= 2:
                    steps += 1
                elif gap <= 4:
                    leaps += 1
                else:
                    wide += 1
            events = bar.get("harmony_events")
            harmonies.append(len(events) if isinstance(events, list) and events else 1)
            midis = [
                m
                for hand in ("rh_display", "lh_display")
                for e in (bar.get(hand) or [])
                if isinstance(e, dict)
                for m in _event_midis(e)
            ]
            if midis:
                lows.append(min(midis))
                highs.append(max(midis))
        total = steps + leaps + wide
        if total >= _VOICING_MIN_ATTACKS and len(sources) >= _VOICING_MIN_SOURCES:
            profile = {
                "step_share": round(steps / total, 3),
                "leap_share": round(wide / total, 3),
                "harmonies_per_bar": round(mean(harmonies), 2) if harmonies else 1.0,
                "low": int(median(lows)) if lows else 0,
                "high": int(median(highs)) if highs else 0,
                "intervals": total,
            }
    except Exception:
        profile = None
    _MOTION_CACHE[composer] = profile
    return profile


def motion_lines(composer: str) -> List[str]:
    """The MELODIC MOTION & HARMONIC RHYTHM section, or nothing when unmeasurable."""
    profile = motion_profile(composer)
    if not profile:
        return []
    step = profile["step_share"]
    leap = profile["leap_share"]
    if step >= 0.75:
        melody = (
            f"The line moves BY STEP — {round(step * 100)}% of melodic intervals are a tone "
            "or less, and a leap is an event the line steps back inside afterwards."
        )
    elif step >= 0.55:
        melody = (
            f"{round(step * 100)}% of melodic intervals are stepwise, "
            f"{round(leap * 100)}% are a fifth or wider. Mostly conjunct, with real leaps "
            "for shape."
        )
    else:
        melody = (
            f"The line LEAPS — only {round(step * 100)}% of intervals are stepwise and "
            f"{round(leap * 100)}% span a fifth or more. A smooth scalar melody is the "
            "wrong instrument for this idiom."
        )
    rate = profile["harmonies_per_bar"]
    if rate >= 2.2:
        harmony = (
            f"The harmony turns over {rate:.1f} times a bar — it moves WITHIN the bar, "
            "not on the barline."
        )
    elif rate >= 1.7:
        harmony = f"About {rate:.1f} harmonies a bar: the chord usually changes mid-bar."
    else:
        harmony = (
            f"Slow harmonic rhythm — {rate:.1f} harmonies a bar. A chord is prolonged; "
            "changing it every beat busies the surface and flattens the phrase."
        )
    return [
        "",
        # NOT "MOTION": the brief already has a `KEY MOTION` section, and two
        # headings sharing a word is how a reader conflates two different
        # things. Never let two things in one context window share a name.
        f"MELODIC MOTION & HARMONIC RHYTHM (measured over {profile['intervals']} "
        f"real {composer} melodic intervals):",
        f"  {melody}",
        f"  {harmony}",
        f"  The writing lives between MIDI {profile['low']} and {profile['high']} "
        f"— go outside that range only for a reason.",
    ]


_CADENCE_SOPRANO_CACHE: Dict[str, Any] = {}
#: Semitones above the tonic -> how a musician names that scale degree.
_DEGREE_NAME = {
    0: "the tonic",
    1: "the flat 2nd",
    2: "the 2nd",
    3: "the minor 3rd",
    4: "the 3rd",
    5: "the 4th",
    6: "the tritone",
    7: "the 5th",
    8: "the minor 6th",
    9: "the 6th",
    10: "the flat 7th",
    11: "the leading tone",
}


#: Suffixes that turn one of these nouns into the adjective a person actually
#: writes. Stripped from BOTH sides before comparing, so `serene` reaches
#: `serenity` without anyone hand-writing 2,000 synonym lists.
#:
#: Order matters: the longest form of each family comes first, or `iousness`
#: is eaten as `ness` and the rest is left behind.
_EMOTION_SUFFIXES = (
    "fulness",
    "iousness",
    "ousness",
    "edness",
    "ness",
    "ically",
    "ical",
    "ially",
    "ial",
    "ful",
    "ious",
    "ous",
    "ally",
    "al",
    "ated",
    "ate",
    "ant",
    "ent",
    "ing",
    "ed",
    # NOT a bare "ly": `melancholy` is not an adverb, and stripping it gave
    # `melancho` where `melancholic` gives `melanchol`. The `ically`/`ally`
    # forms above already cover the adverbs that occur.
    # The noun endings, which is what the vocabulary is keyed on.
    "ity",
    "ety",
    "ia",
    "ic",
    "y",
    "e",
)
#: Below this the stems stop being distinguishable — `joy` must survive whole,
#: so the floor is 3, not 4. `joyful` -> `joy` needs it.
_EMOTION_STEM_FLOOR = 3


def _emotion_stem(word: str) -> str:
    """A word reduced far enough that `serene` and `serenity` meet.

    The vocabulary is keyed on NOUNS — serenity, joy, melancholy, sorrow,
    triumph, playfulness, tenderness — and people write ADJECTIVES: serene,
    joyful, melancholic, sorrowful, triumphant, playful, tender. Twelve of
    twelve natural requests matched nothing, so the emotional layer was wired
    and firing on almost no real prompt.

    Deliberately crude. It only has to bring two forms of the same feeling
    together, and every candidate is checked against a fixed 74-word list, so a
    stem that over-shortens costs a wrong match at worst — and the length floor
    below is what stops that.
    """
    low = re.sub(r"[^a-z]", "", (word or "").lower())
    changed = True
    while changed and len(low) > _EMOTION_STEM_FLOOR:
        changed = False
        for suffix in _EMOTION_SUFFIXES:
            if low.endswith(suffix) and len(low) - len(suffix) >= _EMOTION_STEM_FLOOR:
                low = low[: -len(suffix)]
                changed = True
                break
    return low


def _tonic_pc(key: Optional[str]) -> Optional[int]:
    if not key:
        return None
    root = str(key).split()[0].replace("-", "b")
    try:
        return pitch_to_midi(root + "4") % 12
    except (ValueError, KeyError, TypeError):
        return None


def cadence_soprano_profile(composer: str) -> Optional[Dict[str, Any]]:
    """What the TOP VOICE does at this composer's own V-I cadences.

    `cadence_scripts.json` carries a `soprano_line` field, `composition_brief`
    reads it, and it is an empty list in **856 of 856 scripts** — the compiler
    hard-codes `[]`. So the brief could say which cadence to write and never
    what the melody does when it gets there, which is the half a listener
    actually hears.

    Measured over real V-I cadences rather than asserted from the textbook,
    because the textbook answer (2-1) turns out to be one composer's habit:

        composer     cadences   commonest approach -> arrival
        bach              636   2 -> 1   (stepwise from above)
        beethoven        1083   5 -> 1, then 7 -> 1
        chopin            618   5 -> 1
        mozart            539   5 -> 1, then 7 -> 1

    and the arrival degree is not always the tonic — it is the tonic only about
    a third of the time, the 5th on a fifth of cadences, the 3rd on an eighth.
    A generated piece that lands every cadence on the tonic in the melody is
    more final, more often, than any real composer is.
    """
    if composer in _CADENCE_SOPRANO_CACHE:
        return _CADENCE_SOPRANO_CACHE[composer]
    members = _aggregate_members(composer)
    if members:
        arrivals: collections.Counter = collections.Counter()
        moves: collections.Counter = collections.Counter()
        total = 0
        for member in members:
            part = cadence_soprano_profile(member)
            if not part:
                continue
            total += part["cadences"]
            arrivals.update(dict(part["arrivals"]))
            moves.update({tuple(k): v for k, v in part["moves"]})
        result = (
            {
                "cadences": total,
                "arrivals": arrivals.most_common(4),
                "moves": [(list(k), v) for k, v in moves.most_common(3)],
                "members": len(members),
            }
            if total
            else None
        )
        _CADENCE_SOPRANO_CACHE[composer] = result
        return result

    profile = None
    try:
        arrivals: collections.Counter = collections.Counter()
        moves: collections.Counter = collections.Counter()
        previous = None
        for bar in _iter_corpus_bars(composer):
            roman = (bar.get("roman") or "").strip()
            tonic = _tonic_pc(bar.get("key"))
            line = [
                e.get("midi")
                for e in (bar.get("melody_line") or [])
                if isinstance(e, dict) and e.get("midi")
            ]
            if previous and tonic is not None and line:
                prev_roman, prev_line = previous
                if prev_roman.upper().startswith("V") and roman in ("I", "i"):
                    arrival = (line[-1] - tonic) % 12
                    arrivals[arrival] += 1
                    if prev_line:
                        moves[((prev_line[-1] - tonic) % 12, arrival)] += 1
            previous = (roman, line)
        if sum(arrivals.values()) >= 40:
            profile = {
                "cadences": sum(arrivals.values()),
                "arrivals": arrivals.most_common(4),
                "moves": [(list(k), v) for k, v in moves.most_common(3)],
            }
    except Exception:
        profile = None
    _CADENCE_SOPRANO_CACHE[composer] = profile
    return profile


def cadence_soprano_lines(composer: str) -> List[str]:
    """The CADENTIAL MELODY section of the brief."""
    profile = cadence_soprano_profile(composer)
    if not profile:
        return []
    total = profile["cadences"]
    arrivals = ", ".join(
        f"{_DEGREE_NAME.get(deg, str(deg))} {count / total:.0%}"
        for deg, count in profile["arrivals"]
    )
    moves = "; ".join(
        f"{_DEGREE_NAME.get(a, str(a))} → {_DEGREE_NAME.get(z, str(z))}"
        for (a, z), _n in [((m[0][0], m[0][1]), m[1]) for m in profile["moves"]]
    )
    return [
        "",
        f"CADENTIAL MELODY (what the top voice does at {total} real {composer} V-I cadences):",
        f"  It lands on: {arrivals}.",
        f"  It gets there by: {moves}.",
        "  Landing every cadence on the tonic in the melody is more final, more often, "
        "than he ever is — save it for the ones that really close.",
    ]


_SEMANTICS_CACHE: Dict[str, Any] = {}


def emotional_vocabulary(composer: str) -> Dict[str, Dict[str, Any]]:
    """The compiled emotion-to-music table, keyed by word.

    `prompt_semantics.json` holds 74 emotion words per composer, each with a
    tempo range, mode, dynamic, texture, register, articulation, rhythm type
    and harmonic language. `style_resolver` loads all of it into
    `StyleProgram.prompt_semantics`, deduplicates it — and **nothing reads it
    from there**. Compiled, loaded, deduped, dropped.

    So a request for "a melancholy nocturne" reached the composer with none of
    what the project already knows melancholy sounds like:

        melancholy   tempo 56-76   Minor/Aeolian   p-mp
                     texture "Medium, descending lines"   register "Mid-low"
                     articulation "Legato, sighing"   rhythm "Gentle, dragging"
                     harmony "iv-i, added 6ths"

    The emotional content of the user's own request was being discarded between
    the pack and the page, which is the least defensible place to lose it.
    """
    if composer in _SEMANTICS_CACHE:
        return _SEMANTICS_CACHE[composer]
    table: Dict[str, Dict[str, Any]] = {}
    for name in _aggregate_members(composer) or [composer]:
        data = _load_pack(name, "prompt_semantics")
        items = data if isinstance(data, list) else []
        for entry in items:
            if not isinstance(entry, dict) or not entry.get("word"):
                continue
            table.setdefault(str(entry["word"]).lower(), entry)
            for synonym in entry.get("synonyms") or []:
                table.setdefault(str(synonym).lower(), entry)
    _SEMANTICS_CACHE[composer] = table
    return table


def match_emotional_words(text: str, composer: str) -> List[Dict[str, Any]]:
    """Emotion entries whose word appears in this text, longest first.

    Longest-first matters: "gentle tension" and "tension" are both entries, and
    matching the short one first would describe the wrong thing.
    """
    table = emotional_vocabulary(composer)
    if not table or not text:
        return []
    low = f" {text.lower()} "
    hits: List[Dict[str, Any]] = []
    seen: set = set()
    # Exact phrases first, longest first: "gentle tension" and "tension" are both
    # entries and matching the short one first would describe the wrong feeling.
    for word in sorted(table, key=len, reverse=True):
        if re.search(r"[\s,;:.\-(]" + re.escape(word) + r"[\s,;:.\-)]", low):
            entry = table[word]
            key = entry.get("word")
            if key not in seen:
                seen.add(key)
                hits.append(entry)
    # Then by stem, so the ADJECTIVE a person writes reaches the noun the
    # vocabulary is keyed on — see `_emotion_stem`. Single words only: a
    # multi-word entry is already handled above and stemming it would be noise.
    stems = {
        _emotion_stem(word): entry
        for word, entry in sorted(table.items(), key=lambda kv: len(kv[0]), reverse=True)
        if " " not in word
    }
    for token in re.findall(r"[a-z]+", low):
        entry = stems.get(_emotion_stem(token))
        if entry and entry.get("word") not in seen:
            seen.add(entry.get("word"))
            hits.append(entry)
    return hits


def emotional_lines(text: str, composer: str, limit: int = 2) -> List[str]:
    """The EMOTIONAL VOCABULARY section: what this feeling sounds like."""
    hits = match_emotional_words(text, composer)[:limit]
    if not hits:
        return []
    lines = ["", "EMOTIONAL VOCABULARY (what this project already knows this feeling sounds like):"]
    for entry in hits:
        parts: List[str] = []
        tempo = entry.get("tempo_range")
        if isinstance(tempo, list) and len(tempo) == 2:
            parts.append(f"tempo {tempo[0]}-{tempo[1]}")
        for key, label in (
            ("mode_scale", ""),
            ("dynamics", "dynamic"),
            ("register", "register"),
            ("texture", "texture"),
            ("articulation", "articulation"),
            ("rhythm_type", "rhythm"),
            ("harmonic_language", "harmony"),
        ):
            value = entry.get(key)
            if isinstance(value, list):
                value = "/".join(str(v) for v in value)
            if value:
                parts.append(f"{label} {value}".strip())
        lines.append(f"  {entry['word']}: " + "; ".join(parts))
    lines.append(
        "  These are starting points from the doctrine, not a specification — "
        "the emotional story drives the notes."
    )
    return lines


def _feeling_text(graph, slot) -> str:
    """Everything in this piece that names a FEELING, for the emotion lookup.

    Matching only `creative_intent` under-fires badly: that string is built from
    `dramatic_plan.ROLE_INTENT` templates, whose language is structural —
    "return", "establish", "intensify" — and names no emotion at all. The words
    a listener would recognise live in three other places, and the user's own
    are the most important of them:

      * the request itself (`contract.description`) — "a MELANCHOLY nocturne";
      * the narrative's `overall_character`;
      * this section's own `character` prose.

    Joining them means the emotional content of the request reaches the phrase
    that has to carry it, rather than stopping at the contract.
    """
    parts: List[str] = []
    contract = getattr(graph, "contract", None)
    if contract is not None:
        parts.append(str(getattr(contract, "description", "") or ""))
    narrative = getattr(graph, "narrative", None)
    if narrative is not None:
        parts.append(str(getattr(narrative, "overall_character", "") or ""))
        section_id = str(getattr(slot, "section_id", "") or "")
        for section in getattr(narrative, "sections", None) or []:
            if not section_id or str(getattr(section, "id", "")) == section_id:
                parts.append(str(getattr(section, "character", "") or ""))
    return " ".join(p for p in parts if p)


def _iter_corpus_bars(composer: str):
    """Yield all corpus bars for a composer (sharded or inline).

    A style reference (``style__<name>``) yields the union of its armed member
    composers' bars, so density stats and any bar-level aggregation work for a
    style exactly as for a single composer.
    """
    members = _aggregate_members(composer)
    if members:
        for member in members:
            yield from _iter_corpus_bars(member)
        return

    composer_dir = _REFERENCE_INDEX / composer
    shards = sorted(composer_dir.glob("bars_*.json"))
    if shards:
        for shard in shards:
            try:
                with open(shard) as f:
                    yield from json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                # SAY SO. A corrupt or half-written shard was skipped in
                # silence, so a composer quietly lost several thousand bars and
                # every statistic downstream — density targets, fingerprints,
                # the corpus profile the gate compares against — was computed
                # over less corpus than it reported. An interrupted rebuild is
                # the ordinary way to get one, and nothing anywhere said which
                # file to rebuild.
                logger.warning(
                    "corpus shard unreadable, SKIPPED (its bars are missing from "
                    "every statistic for %s): %s — %s",
                    composer,
                    shard,
                    exc,
                )
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
    scope = corpus_scope(composer) if has_corpus else {}
    # One pass: bar count, distinct source movements, and a richness sample.
    n_bars = 0
    sources: set = set()
    sampled = harm_hits = mel_hits = 0
    if has_corpus:
        for bar in _iter_corpus_bars(composer):
            n_bars += 1
            sources.add(bar.get("source"))
            if sampled < 300:
                sampled += 1
                if bar.get("roman"):
                    harm_hits += 1
                if bar.get("melody_line"):
                    mel_hits += 1
    has_density = (_COMPILED_PACKS / _pack_dir(composer) / "density_stats.json").exists()
    has_profile = (_COMPILED_PACKS / _pack_dir(composer) / "corpus_profile.json").exists()

    # Record richness — the tier above counts BARS but is blind to whether those
    # bars carry the harmonic frame (roman/function) and melody line the brief
    # needs. MIDI-acquired or pre-rich-rewrite corpora can be "tier A" by bar
    # count yet thin in content; surface that so the orchestrator can re-acquire.
    harmony_cov = round(harm_hits / sampled, 2) if sampled else 0.0
    melody_cov = round(mel_hits / sampled, 2) if sampled else 0.0
    records_rich = sampled > 0 and harmony_cov >= 0.5 and melody_cov >= 0.5
    n_sources = len(sources)

    if n_bars == 0:
        tier = "D"
    elif not records_rich or n_sources < 3:
        # A corpus of one movement, or one whose records carry no harmonic frame
        # and no melody line, cannot teach a composer's voice however many bars
        # it has. Four composers shipped as "armed" on a single music21 file
        # each (corelli 19 bars, handel 54, schubert 82, weber 241) with zero
        # Roman-numeral coverage — briefs for them were noise presented as
        # evidence. Tier C is honest: there is corpus, but not enough to compose from.
        tier = "C"
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
        "distinct_sources": n_sources,
        # richness of the bar records themselves (harmony + melody coverage)
        "harmony_coverage": harmony_cov,
        "melody_coverage": melody_cov,
        "records_rich": records_rich,
        "needs_reacquire": bool(has_corpus and not is_style_id(composer) and not records_rich),
        # A corpus can be large, rich and complete and still teach only one
        # genre. Bach reported tier A on 410 source movements — all 410 of them
        # four-part chorales, which is why his measured ornament rate is 0.003
        # trills per bar. `armed` says he has a corpus; `genre_narrow` says what
        # that corpus can and cannot be asked about.
        "dominant_genre": scope.get("dominant") if has_corpus else None,
        "genre_share": scope.get("dominant_share") if has_corpus else None,
        "genre_narrow": bool(has_corpus and scope.get("narrow")),
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


# Bump when the meaning of a density record changes (e.g. the texture label
# vocabulary), so every cached file is recomputed rather than served stale.
_DENSITY_SCHEMA = 4


def _density_cache_is_current(composer: str, stats: Dict[str, Any]) -> bool:
    """Is a cached density file still describing the corpus that is on disk?

    The cache had no provenance and was never invalidated, so rebuilding the
    corpus did NOT update the density targets the briefs hand the agent: a cache
    written under an older label vocabulary kept serving textures
    ("dialogue_chords", "passage_work", "ornamental_cascade") that the corpus no
    longer produces at all, alongside numbers computed from a different set of
    bars. The commit gate's density floors read the same stale file.
    """
    if stats.get("schema") != _DENSITY_SCHEMA:
        return False
    cached_bars = stats.get("total_bars")
    if not isinstance(cached_bars, int):
        return False
    actual = sum(1 for _ in _iter_corpus_bars(composer))
    return actual == cached_bars


def texture_density_stats(composer: str, refresh: bool = False) -> Dict[str, Any]:
    """Per-texture events/bar percentiles aggregated from reference_index.

    Returns {"rh": {texture: {median, p25, p75, mean, n}},
             "lh": {texture: {...}}, "total_bars": int}.
    Cached on disk at compiled_packs/<composer>/density_stats.json and
    in memory for the process.
    """
    if not refresh and composer in _DENSITY_CACHE:
        return _DENSITY_CACHE[composer]

    cache_path = _COMPILED_PACKS / _pack_dir(composer) / "density_stats.json"
    if not refresh and cache_path.exists():
        try:
            with open(cache_path) as f:
                stats = json.load(f)
            if _density_cache_is_current(composer, stats):
                _DENSITY_CACHE[composer] = stats
                return stats
        except (json.JSONDecodeError, OSError):
            pass

    rh_vals: Dict[str, List[float]] = {}
    lh_vals: Dict[str, List[float]] = {}
    rh_per_beat: Dict[str, List[float]] = {}
    lh_per_beat: Dict[str, List[float]] = {}
    total = 0
    for bar in _iter_corpus_bars(composer):
        total += 1
        md = bar.get("melody_density", 0)
        ad = bar.get("accomp_density", 0)
        rt = bar.get("rh_texture", "unclassified")
        lt = bar.get("lh_texture", "unclassified")
        # Bucketed BY METER as well as pooled. Pooling every meter into one
        # events-per-bar figure meant a 3/4 phrase was handed the median of a set
        # dominated by other meters, and the density gate then checked the phrase
        # against that same wrong number. Mozart's Alberti bass runs a median of
        # 8 events in a 2- or 4-beat bar and 6 in a 3-beat bar; the pooled figure
        # says 8 for all of them.
        #
        # Scaling a per-BEAT median by the beat count is not good enough either —
        # the distribution is multimodal (two notes a beat and six notes a beat
        # are both Alberti), so the per-beat median lands between the modes and
        # scales to a figure no real bar has.
        beats = _beat_count(bar.get("time_sig") or [4, 4])
        if md > 0:
            rh_vals.setdefault(rt, []).append(md)
            rh_per_beat.setdefault((rt, beats), []).append(md)
        if ad > 0:
            lh_vals.setdefault(lt, []).append(ad)
            lh_per_beat.setdefault((lt, beats), []).append(ad)

    def _summary(vals: List[float], places: int = 1) -> Dict[str, float]:
        vals = sorted(vals)
        n = len(vals)
        return {
            "median": round(statistics.median(vals), places),
            "p25": round(vals[n // 4], places),
            "p75": round(vals[(3 * n) // 4], places),
            "mean": round(statistics.fmean(vals), 2),
            "n": n,
        }

    def _merge(per_bar, by_meter):
        out = {}
        for t, v in per_bar.items():
            if len(v) < 5:
                continue
            entry = _summary(v)
            buckets = {
                str(beats): _summary(vals)
                for (tex, beats), vals in by_meter.items()
                if tex == t and len(vals) >= 12
            }
            if buckets:
                entry["by_meter"] = buckets
            out[t] = entry
        return out

    stats = {
        "composer": composer,
        "schema": _DENSITY_SCHEMA,
        "total_bars": total,
        "rh": _merge(rh_vals, rh_per_beat),
        "lh": _merge(lh_vals, lh_per_beat),
    }

    try:
        write_json_atomic(cache_path, stats, indent=1)
    except OSError as exc:
        logger.warning("could not write density cache: %s", exc)

    _DENSITY_CACHE[composer] = stats
    return stats


_FINGERPRINT_SCHEMA = 1
# A dotted value is 1.5x a plain one. Written out rather than computed so the
# 32nd-note case (0.1875) is visible and cannot be lost to float comparison.
_DOTTED_QLS = frozenset({0.1875, 0.375, 0.75, 1.5, 3.0, 6.0})


def rhythmic_fingerprint(composer: str, refresh: bool = False) -> Dict[str, Any]:
    """The handful of surface facts that most decide whether a phrase sounds
    like this composer, measured from his own bars.

    Written because a piece can sit inside every band this system checks and
    still be obviously machine-made. A B-flat andante passed the commit gate,
    the ear and the realism audit while resting in 22% of its bars against
    Mozart's 62%, carrying a dotted rhythm in 4.9% against his 22%, and holding
    NOTHING faster than a sixteenth against his 12.6%. Every one of those facts
    was derivable from the corpus and none of them was ever put in front of the
    composer as a fact — the brief carried per-note ratios, which are the same
    truth in a unit nobody reasons in.

    These are descriptions of what the composer does, not quotas. Returned per
    composer and cached beside the other measured stats.
    """
    if not refresh and composer in _FINGERPRINT_CACHE:
        return _FINGERPRINT_CACHE[composer]
    cache_path = _COMPILED_PACKS / _pack_dir(composer) / "rhythmic_fingerprint.json"
    if not refresh and cache_path.exists():
        try:
            with open(cache_path) as f:
                got = json.load(f)
            # Schema alone is not provenance. `density_stats` and
            # `ornament_stats` both re-count the corpus and discard a cache
            # describing a different one; this checked only that the FORMAT was
            # current, so arming a new member of a style left its fingerprint
            # frozen: `style__baroque` served numbers computed over 6,868 bars
            # while the corpus behind it had grown to 10,914. The brief prints
            # these as "FACTS ABOUT HIM".
            if got.get("schema") == _FINGERPRINT_SCHEMA and got.get("bars") == sum(
                1 for _ in _iter_corpus_bars(composer)
            ):
                _FINGERPRINT_CACHE[composer] = got
                return got
        except (json.JSONDecodeError, OSError):
            pass

    bars = 0
    rest_bars = 0
    dotted_bars = 0
    notes = 0
    fast_notes = 0
    durs: Dict[float, int] = {}
    lh_prev = None
    lh_changes = 0
    lh_transitions = 0
    for bar in _iter_corpus_bars(composer):
        bars += 1
        mel = [e for e in (bar.get("melody_line") or []) if isinstance(e, dict)]
        if any(e.get("type") == "rest" for e in mel) or bar.get("has_rests"):
            rest_bars += 1
        if bar.get("has_dotted_rhythms"):
            dotted_bars += 1
        for e in mel:
            if e.get("type") == "rest":
                continue
            try:
                q = round(float(e.get("dur") or 0), 4)
            except (TypeError, ValueError):
                continue
            if q <= 0:
                continue
            notes += 1
            durs[q] = durs.get(q, 0) + 1
            if q <= 0.125:
                fast_notes += 1
        lh = bar.get("lh_texture")
        if lh_prev is not None:
            lh_transitions += 1
            if lh != lh_prev:
                lh_changes += 1
        lh_prev = lh

    top = sorted(durs.items(), key=lambda kv: -kv[1])[:5]
    out = {
        "composer": composer,
        "schema": _FINGERPRINT_SCHEMA,
        "bars": bars,
        "notes": notes,
        "rest_bar_pct": round(rest_bars / bars, 4) if bars else 0.0,
        "dotted_bar_pct": round(dotted_bars / bars, 4) if bars else 0.0,
        "fast_note_pct": round(fast_notes / notes, 4) if notes else 0.0,
        "lh_texture_change_pct": round(lh_changes / lh_transitions, 4) if lh_transitions else 0.0,
        "top_note_values": [[q, round(n / notes, 4)] for q, n in top] if notes else [],
    }
    try:
        write_json_atomic(cache_path, out, indent=1)
    except OSError:
        pass
    _FINGERPRINT_CACHE[composer] = out
    return out


_QL_NAME = {
    4.0: "whole",
    3.0: "dotted half",
    2.0: "half",
    1.5: "dotted quarter",
    1.0: "quarter",
    0.75: "dotted eighth",
    0.5: "eighth",
    0.375: "dotted 16th",
    0.3333: "triplet eighth",
    0.25: "16th",
    0.1667: "triplet 16th",
    0.125: "32nd",
    0.0625: "64th",
}


def render_rhythmic_fingerprint(composer: str, graph=None, movement_id: str = "") -> List[str]:
    """The fingerprint as brief lines, in the units a composer reasons in."""
    fp = rhythmic_fingerprint(composer)
    if not fp.get("bars"):
        return []
    vals = ", ".join(
        f"{_QL_NAME.get(q, str(q))} {share:.0%}" for q, share in fp.get("top_note_values") or []
    )
    # Never assert a thin sample as a fact about the composer. Liszt's corpus is
    # 437 bars from the four lyrical works that are public domain, and it holds
    # nothing faster than a sixteenth — true of the sample, flatly false of
    # Liszt, and actively harmful to tell a composer.
    tier = composer_coverage_tier(composer)
    sources = tier.get("distinct_sources") or 0
    # THIN and NARROW are different failures and both make the numbers a fact
    # about the sample. Bach's 410 sources are 410 chorales; counting sources
    # alone called that corpus broad.
    scope = corpus_scope(composer)
    thin = tier.get("tier") != "A" or sources < 12 or scope.get("narrow")
    if thin:
        head = [
            f"RHYTHMIC FINGERPRINT ({composer}) — measured over {fp['bars']} bars from "
            f"{sources} source movement(s)"
            + (
                f", {scope['dominant_share']:.0%} of them {scope['dominant']}"
                if scope.get("narrow")
                else ""
            )
            + ". THIS IS THE SAMPLE, NOT THE COMPOSER: a corpus this narrow "
            "under-reports whatever those particular pieces do not happen to do. "
            "Where it disagrees with what you know of him, trust what you know.",
        ]
    else:
        head = [
            f"RHYTHMIC FINGERPRINT ({composer}, measured over {fp['bars']} of his own bars "
            f"from {sources} movements — these are FACTS ABOUT HIM, not quotas):",
        ]
    # Where THIS piece stands against the two facts a composer can act on while
    # still writing. The brief has always stated the target and never the gap:
    # a nocturne rested in 20% of its bars against Chopin's 43%, and an andante
    # in 27% against Mozart's 60%, with "the single clearest tell of a machine"
    # printed above it the whole time. `render_marks_so_far` and the VOICING
    # gap earn their place the same way — a target is a number to agree with.
    so_far: List[str] = []
    if graph is not None:
        got = _rest_and_dotted_so_far(graph, movement_id)
        if got:
            rest, dotted, bars, compound = got
            line = (
                f"  BREATHING SO FAR ({bars} committed bars): {rest:.0%} of your bars "
                f"contain a rest (his {fp['rest_bar_pct']:.0%})"
            )
            # Dotted values are only comparable in SIMPLE metre. In 12/8 the beat
            # itself is a dotted quarter, so a nocturne reads 100% dotted against
            # a corpus figure drawn mostly from 3/4 mazurkas — a true number and
            # a meaningless comparison, which is worse than no number at all.
            if compound:
                line += (
                    "; dotted rhythm is not compared here — this phrase is in compound "
                    "metre, where the beat is already dotted"
                )
            else:
                line += f", {dotted:.0%} carry a dotted rhythm (his {fp['dotted_bar_pct']:.0%})"
            so_far.append(line + ".")
    return (
        head
        + [
            f"  • {fp['rest_bar_pct']:.0%} of these bars contain a REST. Music that never stops "
            f"sounding is the single clearest tell of a machine.",
            f"  • {fp['dotted_bar_pct']:.0%} of them carry a DOTTED rhythm.",
            f"  • {fp['fast_note_pct']:.0%} of the melody notes are a 32nd or faster "
            f"(written `t`; 64ths are `x`).",
            f"  • the LEFT HAND changes character on {fp['lh_texture_change_pct']:.0%} of barlines "
            f"— one accompaniment idiom held all the way through is not his texture.",
            f"  • note values actually written here: {vals}.",
        ]
        + so_far
    )


def _rest_and_dotted_so_far(graph, movement_id: str = ""):
    """(rest-bar share, dotted-bar share, bar count) over committed phrases.

    Counted per BAR, not per note, to match how the corpus fingerprint counts
    them — a share of notes and a share of bars are different quantities, and
    `feedback_contradictory_guidance` is about exactly this kind of unit slip.
    """
    rest_bars: dict = {}
    dotted_bars: dict = {}
    for state in _phrases_in_scope(graph, movement_id):
        layer = getattr(state, "realized", None)
        if layer is None:
            continue
        for name in (
            "principal_line",
            "bass_foundation",
            "response_layer",
            "counter_reply",
            "ornamental_surface",
        ):
            for e in getattr(layer, name, None) or []:
                bar = getattr(e, "bar", None)
                if bar is None:
                    continue
                rest_bars.setdefault(bar, False)
                dotted_bars.setdefault(bar, False)
                if getattr(e, "pitch", None) == "rest":
                    rest_bars[bar] = True
                if "." in str(getattr(e, "duration", "")) or str(
                    getattr(e, "duration", "")
                ).startswith("d"):
                    dotted_bars[bar] = True
    if not rest_bars:
        return None
    n = len(rest_bars)
    compound = False
    for state in _phrases_in_scope(graph, movement_id):
        meter = getattr(getattr(state, "slot", None), "meter", None)
        if meter and len(meter) == 2 and meter[1] == 8 and meter[0] % 3 == 0:
            compound = True
            break
    return (sum(rest_bars.values()) / n, sum(dotted_bars.values()) / n, n, compound)


# How a source name betrays its genre. Deliberately coarse: the point is to warn
# that a corpus is narrow, not to catalogue the repertoire.
_GENRE_PATTERNS = (
    # music21's bundled corpora carry no genre label, only a work id, and both
    # of the ones this project ingests are a single genre: `bach/bwv<n>` is the
    # 371 four-part chorales, and `opusNNnoN/movementN` is the Haydn STRING
    # QUARTETS. Matching those conventions is what makes the warning fire at
    # all — a looser pattern read Bach as 54% chorale / 46% unclassified and
    # concluded his corpus was broad.
    ("four-part chorales", r"bach/bwv\d+|bwv\d+\.\d+|chorale|choral"),
    ("string quartets", r"opus\d+no\d+/movement|quartet"),
    # Hoboken group XVI is Haydn's keyboard sonatas; the group number is the
    # only thing in a Mutopia filename that says so.
    ("piano sonatas", r"sonat|hob[-_ ]?xvi"),
    ("oratorio and sacred", r"tantum|ergo|missa|oratori|creation|schopfung|part-i+-aria"),
    ("songs and anthems", r"deutschlandlied|austria|greis|lied\b"),
    ("mazurkas", r"mazurka"),
    ("nocturnes", r"nocturne"),
    ("etudes", r"etude|\betud"),
    ("preludes", r"prelude"),
    ("waltzes", r"waltz|valse"),
    ("ballades", r"ballade"),
    ("symphonies", r"symphon|sinfon"),
    ("masses and motets", r"mass|credo|kyrie|gloria|sanctus|agnus|benedictus|motet|magnificat"),
    ("madrigals", r"madrigal"),
    ("concertos", r"concerto|conc\b"),
    ("fugues and inventions", r"fugue|invent|wtc"),
    ("suites and partitas", r"suite|partita|allemand|courant|sarab|gigue"),
    ("songs", r"lied|song|aria"),
)


# Patterns that are only true for one composer, tried before the general table.
#
# music21's Haydn corpus is the string quartets — the general table already says
# so via `opusNNnoN/movement`. But a third of his bars are filed as a bare
# `movement4` with no opus prefix, so they fell through to "unclassified", his
# dominant genre came out as *unclassified at 35%*, and a corpus that is quartets
# end to end produced no narrowness warning at all. A pattern this loose cannot
# go in the general table (`movement\d+` would swallow half of every corpus);
# scoped to the composer whose corpus is known to be one genre, it is just true.
_COMPOSER_GENRE_PATTERNS: Dict[str, tuple] = {
    "haydn": (("string quartets", r"^movement\d+$|opus\d+no\d+"),),
}


def corpus_scope(composer: str, refresh: bool = False) -> Dict[str, Any]:
    """WHAT this composer's corpus actually contains, by genre.

    Every statistic in this system — density, ornament rates, texture change,
    the rhythmic fingerprint, the discriminator z-scores — is computed over the
    corpus and presented as a fact about the composer. Measuring the corpora
    showed how far that can drift:

      · Bach is **97% four-part chorales**. His ornament rate reads as 0.003
        trills per bar, which is true of chorales and wildly false of the
        keyboard music. A brief for a Bach keyboard piece was quoting vocal
        part-writing statistics.
      · Chopin is **100% mazurkas** — no nocturnes, no études, no ballades. His
        measured share of notes faster than a sixteenth is 0.2%.

    Neither corpus is *thin* (6,795 and 4,853 bars), so a size-based caveat
    misses both. Narrowness is the thing to report.
    """
    if not refresh and composer in _SCOPE_CACHE:
        return _SCOPE_CACHE[composer]

    counts: Dict[str, int] = {}
    total = 0
    for bar in _iter_corpus_bars(composer):
        total += 1
        src = str(bar.get("source") or "").lower()
        label = "unclassified"
        for name, pat in _COMPOSER_GENRE_PATTERNS.get(composer, ()) + _GENRE_PATTERNS:
            if re.search(pat, src):
                label = name
                break
        counts[label] = counts.get(label, 0) + 1

    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    top = ranked[0] if ranked else ("unclassified", 0)
    share = (top[1] / total) if total else 0.0
    out = {
        "composer": composer,
        "bars": total,
        "genres": [[g, round(n / total, 4)] for g, n in ranked[:5]] if total else [],
        "dominant": top[0],
        "dominant_share": round(share, 4),
        # One genre carrying three-quarters of the corpus means every statistic
        # derived from it describes that genre, not the composer.
        "narrow": bool(total and share >= 0.75 and top[0] != "unclassified"),
        # ...but "not narrow" and "we cannot tell" are different answers, and
        # only one of them is reassuring. `narrow` is False whenever the genre
        # is unknown, which read as "this corpus is broad" for 18 of 27
        # composers — including Haydn, whose corpus is string quartets end to
        # end and whose sources are filed as bare `movement4`, missing the
        # `opusNNnoN/movement` pattern written for him. A silent False is the
        # worst possible answer to "is this corpus one genre?".
        "classified_share": round(1.0 - (counts.get("unclassified", 0) / total), 4)
        if total
        else 0.0,
        "scope_known": bool(total and (counts.get("unclassified", 0) / total) < 0.5),
    }
    _SCOPE_CACHE[composer] = out
    return out


def render_corpus_scope(composer: str) -> List[str]:
    """The scope warning, or nothing when the corpus is broad enough."""
    sc = corpus_scope(composer)
    if not sc.get("bars"):
        return []
    if not sc.get("scope_known"):
        # Say the honest thing rather than the reassuring one.
        return [
            f"WHAT THIS CORPUS ACTUALLY IS — unknown. "
            f"{1 - sc.get('classified_share', 0):.0%} of the {composer} bars "
            f"behind every number below come from sources this project cannot "
            f"identify by genre, so whether they are one genre or twenty is not "
            f"established. Treat the statistics as describing *these particular "
            f"works*, and where they conflict with what you know of his writing "
            f"in the genre you are composing, trust what you know of the genre.",
        ]
    if not sc.get("narrow"):
        return []
    return [
        f"WHAT THIS CORPUS ACTUALLY IS — {sc['dominant_share']:.0%} of the "
        f"{composer} bars behind every number below are {sc['dominant']}. Each "
        f"statistic in this brief describes {sc['dominant']}, not {composer} "
        f"entire. Where they conflict with what you know of his writing in the "
        f"genre you are composing, trust what you know of the genre.",
    ]


def corpus_fidelity(composer: str) -> Dict[str, Any]:
    """Whether the corpus can be trusted on FINE detail — ornaments and fast notes.

    Genre narrowness is one way a statistic misleads; source fidelity is another,
    and fixing the first can hide the second. Broadening Chopin from mazurkas to
    ballades, nocturnes and etudes dropped `corpus_scope().narrow` to False and
    with it the warning — while his measured share of notes faster than a
    sixteenth FELL to 0.1%, because the added works came from MIDI, which carries
    no ornament marks and quantises filigree to sixteenths. The corpus got
    broader and the fine-rhythm number got worse.

    Measured, not declared: a source that records no ornament anywhere and
    nothing shorter than a sixteenth is a MIDI transcription however it is named.
    """
    per: Dict[str, Dict[str, int]] = {}
    for bar in _iter_corpus_bars(composer):
        src = str(bar.get("source") or "")
        e = per.setdefault(src, {"orn": 0, "fast": 0, "notes": 0})
        for rec in bar.get("rh_display") or []:
            if isinstance(rec, dict) and (rec.get("orn") or rec.get("is_grace")):
                e["orn"] += 1
        for note in bar.get("melody_line") or []:
            if note.get("type") == "rest":
                continue
            try:
                q = float(note.get("dur") or 0)
            except (TypeError, ValueError):
                continue
            if q <= 0:
                continue
            e["notes"] += 1
            if q <= 0.125:
                e["fast"] += 1

    coarse_bars = total_bars = 0
    for src, e in per.items():
        if e["notes"] < 40:
            continue
        total_bars += e["notes"]
        if e["orn"] == 0 and e["fast"] / e["notes"] < 0.005:
            coarse_bars += e["notes"]
    share = (coarse_bars / total_bars) if total_bars else 0.0
    return {
        "composer": composer,
        "coarse_share": round(share, 4),
        "low_fidelity": bool(share >= 0.30),
    }


def render_corpus_fidelity(composer: str) -> List[str]:
    fi = corpus_fidelity(composer)
    if not fi.get("low_fidelity"):
        return []
    return [
        f"FIDELITY WARNING — {fi['coarse_share']:.0%} of the {composer} corpus is "
        f"sources carrying NO ornament mark and nothing shorter than a sixteenth. "
        f"That can mean the source could not record them (MIDI transcription) or "
        f"that the genre does not use them (chorales); either way any ornament "
        f"rate or fast-note figure below UNDERSTATES what he writes elsewhere. A "
        f"low number there is evidence about the source, not about his hand. "
        f"Write the filigree the music wants.",
    ]


# What each lock protects, in the words a composer would use.
_LOCK_MEANING = {
    "principal_melody": "the tune itself — its pitches and its shape",
    "bass_foundation": "the bass line",
    "cadence_hits": "where the phrases close, and on what",
    "counterline": "the inner counter-melody",
    "color_events": "the harmonic colour — the borrowed and chromatic chords",
    "phrase_count": "how many phrases there are and how long each runs",
    "key_scheme": "the key of each section and the journey between them",
    "form_layout": "the shape of the piece — which section follows which",
}


def render_lock_contract(graph, slot) -> List[str]:
    """What must survive, for the modes whose whole contract is a lock policy.

    CLAUDE.md describes the six composition modes as "all one algorithm,
    different contracts", and the contract IS the lock policy. It was computed
    by `load_source_score`, stored on the graph, read only by the engine's
    candidate scorer — and never spoken to the agent, who writes every note on
    the default path. A `variation` brief did not contain the word "lock". The
    mode was decorative: the melody it was meant to preserve could be discarded
    entirely and nothing would notice.
    """
    mode = str(getattr(graph, "mode", "") or "")
    if mode in ("", "compose_from_text"):
        return []
    locks = getattr(getattr(graph, "contract", None), "locks", None)
    if locks is None:
        return []
    held = []
    for name, meaning in _LOCK_MEANING.items():
        try:
            v = float(getattr(locks, name, 0) or 0)
        except (TypeError, ValueError):
            continue
        if v >= 0.5:
            held.append((v, name, meaning))
    if not held:
        return []
    held.sort(reverse=True)
    lines = [
        f"WHAT MUST SURVIVE — this is a {mode.replace('_', ' ')}, and these are "
        f"the things the source piece is being kept for. A lock near 1.0 means "
        f"leave it alone; nearer 0.5 means it must still be recognisable:",
    ]
    for v, name, meaning in held:
        lines.append(f"  • {v:.1f}  {name} — {meaning}")

    # The source material for this phrase's bars, so "keep the melody" is a
    # thing the composer can actually see rather than a number.
    try:
        src = _source_phrase_for(graph, slot)
        if src:
            lines.append(f"  THE SOURCE, bars {src[0]}: {src[1]}")
            lines.append(
                "  Vary it — ornament, reharmonise, change the texture and the "
                "register — but a listener must still hear THIS underneath."
            )
    except Exception:
        pass
    return lines


def _source_phrase_for(graph, slot):
    """(bar-range, melody shorthand) of the source phrase covering this slot."""
    start = int(getattr(slot, "bar_start", 1) or 1)
    count = int(getattr(slot, "bar_count", 1) or 1)
    best = None
    for ps in getattr(graph, "phrases", {}).values():
        if getattr(ps, "salience", None) != "source" or not ps.realized or not ps.slot:
            continue
        a = int(ps.slot.bar_start or 1)
        b = a + int(ps.slot.bar_count or 1) - 1
        if a <= start + count - 1 and b >= start:
            best = ps
            break
    if best is None:
        return None
    ev = [e for e in (best.realized.principal_line or []) if e.pitch != "rest"][:12]
    if not ev:
        return None
    span = f"{best.slot.bar_start}-{best.slot.bar_start + best.slot.bar_count - 1}"
    return span, " ".join(f"{e.pitch}{e.duration}" for e in ev)


_ORNAMENT_SCHEMA = 1


_ANACRUSIS_CACHE: Dict[str, float] = {}


def anacrusis_rate(composer: str) -> float:
    """Fraction of this composer's movements that open with a pickup bar.

    Measured, because the alternative is a generic exhortation that nothing acts
    on: the brief has told composers "not every phrase starts on a downbeat" for
    a long time, and not one of the twelve pieces in ``workspace/`` opens off the
    beat. The corpus figure is 46% for Mozart, 57% for Beethoven, 58% for Chopin
    and 69% for Bach.
    """
    key = (composer or "").lower()
    if key in _ANACRUSIS_CACHE:
        return _ANACRUSIS_CACHE[key]
    sources: Dict[str, bool] = {}
    for b in _iter_corpus_bars(composer):
        src = b.get("source") or "?"
        sources[src] = sources.get(src, False) or (b.get("bar_num") == 0)
    rate = (sum(1 for v in sources.values() if v) / len(sources)) if sources else 0.0
    _ANACRUSIS_CACHE[key] = round(rate, 3)
    return _ANACRUSIS_CACHE[key]


def ornament_stats(composer: str, refresh: bool = False) -> Dict[str, Any]:
    """Per-texture ornament rates measured from the CORPUS.

    Ornament targets used to come from ``tools/texture_templates/``, which has no
    builder — it is hand-authored data from an earlier era of this project that
    no script regenerates. It claimed Mozart writes 0.181 grace notes per bar in
    a singing melody; his corpus says 0.059. Meanwhile the extractor was
    discarding the trills, mordents and turns the sources actually carry (one
    Mozart movement has 17 trills and 12 mordents), so nothing measured them at
    all.

    Returns {texture: {grace, trill, mordent, turn, dotted, n}} per bar, cached
    with the provenance that ``density_stats`` also carries.
    """
    if not refresh and composer in _ORNAMENT_CACHE:
        return _ORNAMENT_CACHE[composer]
    cache_path = _COMPILED_PACKS / _pack_dir(composer) / "ornament_stats.json"
    if not refresh and cache_path.exists():
        try:
            with open(cache_path) as f:
                stats = json.load(f)
            if stats.get("schema") == _ORNAMENT_SCHEMA and stats.get("total_bars") == sum(
                1 for _ in _iter_corpus_bars(composer)
            ):
                _ORNAMENT_CACHE[composer] = stats
                return stats
        except (json.JSONDecodeError, OSError):
            pass

    per: Dict[str, Dict[str, float]] = {}
    total = 0
    for bar in _iter_corpus_bars(composer):
        total += 1
        tex = bar.get("rh_texture") or "unclassified"
        e = per.setdefault(
            tex, {"n": 0, "grace": 0, "trill": 0, "mordent": 0, "turn": 0, "dotted": 0}
        )
        e["n"] += 1
        for rec in bar.get("rh_display") or []:
            if rec.get("is_grace"):
                e["grace"] += 1
            orn = rec.get("orn")
            if orn == "tr":
                e["trill"] += 1
            elif orn == "mord":
                e["mordent"] += 1
            elif orn == "turn":
                e["turn"] += 1
        if bar.get("has_dotted_rhythms"):
            e["dotted"] += 1

    out = {
        "composer": composer,
        "schema": _ORNAMENT_SCHEMA,
        "total_bars": total,
        "textures": {
            t: {k: round(v / max(1, d["n"]), 4) for k, v in d.items() if k != "n"} | {"n": d["n"]}
            for t, d in per.items()
            if d["n"] >= 10
        },
    }
    try:
        write_json_atomic(cache_path, out, indent=1)
    except OSError as exc:
        logger.warning("could not write ornament cache: %s", exc)
    _ORNAMENT_CACHE[composer] = out
    return out


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
    path = _COMPILED_PACKS / _pack_dir(composer) / "scoped_statistics.json"
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


# What a cadence is CALLED varies by the source that wrote it down. A composer
# profile writes "HC (->V)"; the shared genre harmony files write "Half
# cadence"; the Renaissance file writes "Clausula vera" and "Authentic
# (perfect)". The doctrine lookup matched with `cad.upper() in stype`, a plain
# substring test, so it found Mozart's "HC (->V)" and missed Bach's "Half
# cadence" entirely — five of the twelve armed composers got **no cadence
# script at all**, in the one place that addresses the single most reliable tell
# that a machine wrote the piece ("every phrase ends the same way").
_CADENCE_ALIASES: Dict[str, Tuple[str, ...]] = {
    "PAC": (
        "pac",
        "perfect authentic",
        "authentic (pac)",
        "authentic (perfect)",
        "perfect cadence",
        "clausula vera",  # the Renaissance structural cadence
    ),
    "IAC": ("iac", "imperfect authentic", "imperfect cadence"),
    "HC": ("hc", "half cadence", "half-cadence", "semicadence", "phrygian half"),
    "DC": ("dc", "deceptive", "interrupted"),
    "plagal": ("plagal", "amen"),
    "evaded": ("evaded", "elided"),
    "phrygian": ("phrygian",),
}


# What each cadence type REQUIRES, as a matter of definition rather than of
# style. The compiled packs declare a `soprano_line` field for this and it is
# empty in all 169 places it occurs, because the source doctrine's cadence
# tables have no soprano column — so the requirement was never stated anywhere
# the composer could read it. It does not need extracting: a perfect authentic
# cadence has the tonic in the soprano BY DEFINITION, and one that lands on the
# third or fifth is an imperfect cadence whatever the plan called it.
#
# This is the defect that had to be fixed by hand in the regenerated andante:
# the structural arrival at bar 37 was planned PAC, closed V7-I correctly, and
# still read as imperfect because the melody landed on the fifth.
_CADENCE_REQUIREMENTS = {
    "PAC": (
        "the TONIC in the soprano (scale degree 1) on the final chord, and the "
        "dominant in root position before it — land on the third or fifth and "
        "it is an imperfect cadence, whatever the plan says"
    ),
    "IAC": (
        "the third or fifth in the soprano — deliberately weaker than a PAC, so "
        "save the tonic-in-soprano close for the arrival that deserves it"
    ),
    "HC": (
        "stop ON the dominant, not on a chord that resolves to it. Scale degree "
        "2, 5 or 7 in the soprano; the phrase should sound like a question"
    ),
    "DC": (
        "the dominant resolving to vi instead of I — the promise is made and "
        "withheld, so the real cadence still has to arrive later"
    ),
    "deceptive": (
        "the dominant resolving to vi instead of I — the promise is made and "
        "withheld, so the real cadence still has to arrive later"
    ),
    "plagal": (
        "IV-I, with no dominant. An afterthought cadence: it confirms a close "
        "that has already happened rather than making one"
    ),
    "evaded": (
        "the dominant arrives and its resolution is dodged — an inversion, or "
        "the bass moving on. The ear must notice it was denied something"
    ),
    "elided": (
        "the resolution IS the next phrase's downbeat. Write the final note "
        "tied over the barline, or let the next entry overlap it — there is no "
        "gap between the phrases"
    ),
}


def cadence_requirement(cadence: str) -> str:
    """What the planned cadence requires, in one sentence, or ''."""
    return _CADENCE_REQUIREMENTS.get(str(cadence or "").strip(), "")


def _cadence_matches(cad: str, script_type: str) -> bool:
    """True when a pack's cadence script describes the cadence this phrase wants."""
    want = (cad or "").strip().upper()
    have = (script_type or "").strip().lower()
    if not want or not have:
        return False
    if want.lower() in have:
        return True
    for alias in _CADENCE_ALIASES.get(want, ()):
        if alias in have:
            return True
    # A Phrygian half cadence answers a request for HC.
    if want == "HC" and "phrygian" in have:
        return True
    return False


def _slot_contour_class(slot) -> str | None:
    """ "ascending" / "descending" / "static" for this phrase's register plan.

    The corpus vocabulary, measured over 9,569 indexed phrases: `static` 17180,
    `descending` 9912, `ascending` 9287 — and nothing else. A value outside it
    would score every candidate 0.0 instead of a neutral 0.5, so the words have
    to be exactly these three.
    """
    # Derived from the DRAMATIC ROLE, not the register curve. Two rules over the
    # curve were tried first and each returned ONE value for all 26 planned
    # slots — every planned register curve is the same arch, so nothing taken
    # from it discriminates. A discriminator with one value discriminates
    # nothing, and would have scored every candidate identically while looking
    # like it was working. The role varies across nine values and says the same
    # musical thing: a phrase that intensifies rises, one that retreats falls.
    role = str(getattr(slot, "dramatic_role", "") or "").strip().lower()
    if role in ("intensify", "crisis", "depart"):
        return "ascending"
    if role in ("retreat", "close"):
        return "descending"
    if role in ("establish", "extend", "confirm", "return"):
        return "static"
    curve = [float(x) for x in (getattr(getattr(slot, "curves", None), "register", None) or [])]
    if len(curve) < 2 or max(curve) - min(curve) < 0.02:
        return None
    return "ascending" if curve.index(max(curve)) > curve.index(min(curve)) else "descending"


def _slot_entry_texture(slot) -> str | None:
    """The texture this phrase is planned to START in, for entry continuity."""
    plan = list(getattr(slot, "texture_plan", None) or [])
    if not plan:
        return None
    first = plan[0]
    texture = getattr(first, "rh_texture", None)
    if texture is None and isinstance(first, dict):
        texture = first.get("rh_texture")
    texture = str(texture or "").strip()
    return texture or None


def _phrase_shape(composer: str, slot, role: str) -> Dict[str, Any]:
    """Top corpus phrase for this slot's role/length — its arc, not just a bar."""
    try:
        from .models import PhraseQuery

        bank = _phrase_bank(composer)
        n_bars = slot.bar_count
        # `PhraseQuery` scores retrieval on three more dimensions that NO caller
        # ever set — `contour_class`, `entry_texture`, `cadence_distance`, worth
        # 0.20 of the ranking between them. Unset, each scores a flat 0.5 for
        # every candidate, so a fifth of the relevance model was a constant. The
        # planner knows all three; it just never said so.
        q = PhraseQuery(
            formal_function=role,
            length_range=(max(1, n_bars - 2), n_bars + 2),
            cadence_type=_normalize_cadence(getattr(slot, "cadence_target", None)),
            cadence_distance=n_bars,
            contour_class=_slot_contour_class(slot),
            entry_texture=_slot_entry_texture(slot),
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
        # Six style matrices have no armed member, so they are still SYNTHETIC:
        # the Classical matrix with hand-picked multipliers ("baroque: alberti
        # x0.3, pedal_point x1.5"). Composing "in an impressionist style" against
        # those means composing against Mozart's texture habits with a fudge
        # factor. That has to be said out loud, not passed off as corpus
        # evidence — a silent substitution is how a piece ends up in the wrong
        # idiom with numbers that look supportive.
        if matrix.get("synthetic"):
            out["provenance"] = (
                "SYNTHETIC texture-transition data — no composer in this style is "
                "armed, so these odds are the Classical matrix with adjustment "
                "weights applied, NOT corpus evidence. Treat them as a weak prior "
                "and lean on the written doctrine instead."
            )
        if from_texture:
            follow = _top_follow(from_texture)
            if follow:
                out["after_previous"] = {"from": from_texture, "follow": follow}
        # primary LH texture of this phrase
        lh = [t[1] for t in _slot_textures(slot, composer)]
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


def _pitch_token(p) -> str:
    """One shorthand pitch token — a note name, or ``[C3,E3,G3]`` for a chord.

    A chord in a stored pattern is a LIST, and it was being interpolated into
    the shorthand with ``f"{e['p']}"`` — so the LH vocabulary in every brief
    printed Python list syntax (``['G2', 'G3']q``) and any bar the agent copied
    from it failed to parse, silently dropping the whole accompaniment.
    """
    if isinstance(p, (list, tuple)):
        names = _distinct_pitches(p)
        if not names:
            return ""
        return f"[{','.join(names)}]" if len(names) > 1 else names[0]
    return str(p) if p else ""


def _distinct_pitches(pitches) -> List[str]:
    """Chord members, in order, without a pitch repeated.

    A doubled unison is real in the score and meaningless in a chord token: the
    corpus carries 1,471 chords whose members repeat, and `[G5,G5]` reads as a
    two-note chord to anyone adapting it.
    """
    out: List[str] = []
    for x in pitches or []:
        name = str(x)
        if not x or name == "rest" or name in out:
            continue
        out.append(name)
    return out


def _lh_vocabulary(composer: str, slot, key: str, max_patterns: int = 2) -> List[Dict[str, Any]]:
    """Top canonical real LH patterns for this phrase's LH textures, in shorthand."""
    try:
        pr = _pattern_retriever()
        lh_textures = []
        for _, lh in _slot_textures(slot, composer):
            if lh not in lh_textures and lh not in ("silence", "unclassified"):
                lh_textures.append(lh)
        out: List[Dict[str, Any]] = []
        meter = tuple(getattr(slot, "meter", (4, 4)) or (4, 4))
        capacity = float(bar_duration(meter))
        for tex in lh_textures[:2]:
            patterns = pr.retrieve(tex, density_range=(3, 18), n=1)
            for p in patterns:
                tp = pr.transpose_pattern(p, "C", key)
                toks: List[str] = []
                used = 0.0
                for e in tp.get("lh_events", []):
                    if not e.get("p"):
                        continue
                    dur = float(e.get("d", 0.5))
                    # Fit the pattern to THIS phrase's bar. Canonical patterns
                    # are stored in whatever meter they came from, so an 8-eighth
                    # Alberti figure (4 beats) was being handed to a 3/4 phrase —
                    # a bar-and-a-third of accompaniment, which overflows the moment
                    # it is copied.
                    if used + dur > capacity + 1e-6:
                        break
                    tok = _pitch_token(e["p"])
                    if not tok:
                        continue
                    toks.append(f"{tok}{beats_to_dur(dur)}")
                    used += dur
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
    members = _aggregate_members(composer)
    if members:
        # Aggregate the shared traits of the idiom: a couple from each armed
        # member, deduped by name, capped — the blend/style's collective voice.
        out: List[Dict[str, str]] = []
        seen: set = set()
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


# What a phrase of each FUNCTION is doing, in the vocabulary the gesture bank
# indexes by. The bank's functions are what a gesture DOES — answer, insist,
# push to a cadence — which is a different axis from the exemplar bars (what a
# bar contains) and maps straight onto the slot's own phrase function.
_FUNCTION_GESTURES = {
    "presentation": ("pickup", "insist"),
    "continuation": ("answer", "insist", "answer_with_space"),
    "contrasting_theme": ("answer", "pickup"),
    "transition": ("insist", "cadential_push"),
    "cadential": ("cadential_push", "cadential_release"),
    "closing": ("cadential_release", "cadential_push"),
    "coda": ("cadential_release",),
    "retransition": ("cadential_push", "insist"),
    "fragmentation": ("insist", "answer_with_space"),
    "sequence": ("insist", "answer"),
    "liquidation": ("answer_with_space", "cadential_release"),
    "return": ("pickup", "answer"),
    "return_varied": ("pickup", "answer"),
}


def _transition_habits(composer: str, slot, incoming: Dict[str, Any]) -> Dict[str, Any]:
    """How THIS composer typically joins a phrase like this to one like that.

    `TransitionBank` scores real phrase-to-phrase joins in the corpus — register
    continuity, texture contrast, dynamic continuity, motivic logic — and it was
    called by **nothing at all**. Not the brief, not the engine, not the review.
    A whole retrieval bank, built from the corpus and wired to no one.

    The brief already tells a phrase where the previous one left off. This tells
    it what the composer usually DOES at that joint: keeps the register or
    jumps, contrasts the texture or continues it, holds the dynamic or drops it.
    That is the difference between a phrase that follows and a phrase that
    continues.
    """
    try:
        from .transition_bank import TransitionBank, TransitionQuery
    except ImportError:
        return {}
    hits = []
    for member in _bank_composers(composer):
        try:
            bank = TransitionBank(member)
            hits.extend(
                bank.retrieve(
                    TransitionQuery(
                        target_function=str(getattr(slot, "function", "") or "") or None,
                        exit_texture_lh=(incoming.get("last_lh_texture") or None),
                        exit_dynamic=(incoming.get("last_dynamic") or None),
                        n=12,
                    )
                )
            )
        except Exception:
            continue
    if not hits:
        return {}

    def _mean(attr: str) -> float:
        vals = [getattr(h, attr, None) for h in hits]
        vals = [v for v in vals if isinstance(v, (int, float))]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    return {
        "samples": len(hits),
        "register_continuity": _mean("register_continuity"),
        "texture_contrast": _mean("texture_contrast"),
        "dynamic_continuity": _mean("dynamic_continuity"),
        "motivic_logic": _mean("motivic_logic"),
    }


def _bank_composers(reference: str) -> List[str]:
    """Which composer indexes a retrieval bank should read for this reference.

    A style has no `reference_index/<name>/` directory of its own — it
    aggregates over its members at read time — so a bank constructed with
    `style__baroque` finds no file and silently returns nothing. That is the
    same failure that left every style with no progression model and hard-coded
    I-IV-V harmony: a style id is not a directory name.
    """
    try:
        from .style_registry import is_style_id, style_members
    except ImportError:
        return [reference]
    if not is_style_id(reference):
        return [reference]
    return style_members(reference, armed_only=True) or []


def _corpus_gestures(composer: str, slot, n: int = 4) -> List[Dict[str, Any]]:
    """Real gestures from the corpus, indexed by what they DO.

    `gesture_bank.json` is 89 MB of shapes extracted from the actual scores —
    rhythm profile, accent profile, contour, how the gesture enters and how it
    leaves — and it was reachable ONLY from the engine-fallback path. The
    agent-authored default path, which is the path every piece takes, never saw
    one. Mozart's bank alone holds 6,922 of them across six functions.

    This is a different axis from the exemplar bars. An exemplar says what a bar
    CONTAINS; a gesture says what a shape DOES and how it joins to what is
    around it, which is what a phrase with a function needs.
    """
    try:
        from .gesture_bank import GestureBank, GestureQuery
    except ImportError:
        return []
    function = str(getattr(slot, "function", "") or "").lower()
    wanted = _FUNCTION_GESTURES.get(function) or ("answer", "insist")
    members = _bank_composers(composer)
    if not members:
        return []
    out: List[Dict[str, Any]] = []
    per = max(1, n // max(1, len(wanted)))
    hits = []
    for member in members:
        try:
            bank = GestureBank(member)
        except Exception:
            continue
        for fn_name in wanted:
            try:
                hits.extend(bank.retrieve(GestureQuery(function=fn_name, n=per)))
            except Exception:
                continue
    for fn_name in [""]:
        for h in hits:
            durs = list(getattr(h, "dur_profile", None) or [])
            if not durs:
                continue
            out.append(
                {
                    "does": str(getattr(h, "function", "") or "").replace("_", " "),
                    "rhythm": " ".join(durs),
                    "contour": getattr(h, "contour", "") or "",
                    "enters": getattr(h, "entry_state", "") or "",
                    "leaves": getattr(h, "exit_state", "") or "",
                    "lh_texture": getattr(h, "lh_texture", "") or "",
                    "source": getattr(h, "source", "") or "",
                    "span_beats": getattr(h, "span_beats", None),
                }
            )
    return out[:n]


def _gestures(composer: str, slot, n: int = 5) -> List[Dict[str, Any]]:
    """Named gestures from the composer's own pack, written out as shorthand.

    `gesture_templates.json` exists for every one of the 51 compiled packs, with
    18-21 entries each, and **nothing in the brief ever loaded it** — so the
    composer never saw a single one. They are not statistics: each is a named
    idiom with real notes and the expression already on them ("The Appoggiatura
    and Sigh": E5 espressivo, D5, C5 held), which is exactly the material a
    phrase is built out of and exactly what the corpus exemplars cannot give,
    because an exemplar is a bar and a gesture is a shape with a name.

    Selected for the phrase where a gesture says what it is for; otherwise the
    first few, which are the ones the doctrine lists first for a reason.
    """
    entries = _load_pack(composer, "gesture_templates") or []
    if not isinstance(entries, list):
        return []
    role = str(getattr(slot, "function", "") or "").lower()
    cad = str(getattr(slot, "cadence_target", "") or "").lower()
    wanted, rest = [], []
    for g in entries:
        if not isinstance(g, dict) or not (g.get("voice_events") or {}):
            continue
        situation = f"{g.get('situation', '')} {g.get('name', '')}".lower()
        (wanted if (role and role in situation) or (cad and cad in situation) else rest).append(g)
    chosen = (wanted + rest)[:n]

    out: List[Dict[str, Any]] = []
    for g in chosen:
        hands = {}
        for hand in ("rh", "lh"):
            events = (g.get("voice_events") or {}).get(hand) or []
            tokens = []
            for e in events:
                if not isinstance(e, dict) or not e.get("p"):
                    continue
                tok = f"{e['p']}{e.get('d', 'q')}"
                for key, prefix in (("expr", ":"), ("dyn", ":"), ("art", ":"), ("orn", ":")):
                    if e.get(key):
                        tok += f"{prefix}{str(e[key]).replace(' ', '_')}"
                tokens.append(tok)
            if tokens:
                hands[hand] = " ".join(tokens)
        if hands:
            out.append(
                {
                    "name": re.sub(r"^\d+\.\s*", "", str(g.get("name", "") or "")).strip(),
                    "situation": g.get("situation") or "",
                    **hands,
                }
            )
    return out


def _doctrine_slices(composer: str, slot, role: str) -> Dict[str, Any]:
    """Select only the doctrine that applies to THIS phrase (not the firehose)."""
    out: Dict[str, Any] = {}
    cad = _normalize_cadence(getattr(slot, "cadence_target", None))

    # Cadence script for the slot's cadence
    if cad:
        requirement = cadence_requirement(cad)
        if requirement:
            out["cadence_requirement"] = requirement
        scripts = _load_pack(composer, "cadence_scripts") or []
        for s in scripts if isinstance(scripts, list) else []:
            if _cadence_matches(cad, s.get("type", "") or ""):
                out["cadence_script"] = {
                    "type": s.get("type"),
                    "approach": s.get("approach_chords"),
                    "soprano": s.get("soprano_line"),
                    "bass": s.get("bass_motion"),
                    "usage": s.get("usage"),
                    "strength": s.get("strength"),
                }
                break

    # Ornament intent matching the phrase position
    position = "cadence" if cad else ("entry" if role == "opening" else "middle")
    intents = _load_pack(composer, "ornament_intents") or []
    chosen = []
    # THIS composer's own ornament habits lead. `ornament_intents.json` was
    # identical for all twelve armed composers, so every brief recommended the
    # same ornament in the same place whether it was writing Bach or Chopin —
    # while the table saying what each composer actually does sat uncompiled in
    # their profile. Ornament choice is one of the most composer-specific things
    # in the idiom.
    for it in intents if isinstance(intents, list) else []:
        if it.get("category") != "composer_ornament_usage":
            continue
        name = (it.get("ornament") or "").strip()
        usage = (it.get("usage") or "").strip()
        intent = (it.get("intent") or "").strip()
        if name and usage:
            chosen.append(f"{name} — {usage}" + (f" ({intent})" if intent else ""))
    composer_specific = len(chosen)
    for it in intents if isinstance(intents, list) else []:
        ctx = (it.get("context", "") or "").lower()
        if position in ctx or (role == "opening" and "entry" in ctx):
            chosen.append(f"{it.get('what_moment_needs', '')} → {it.get('common_choice', '')}")
    if chosen:
        out["ornament_intent"] = chosen[: max(3, composer_specific + 1)][:4]

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

    # Melody priors: the CONTOUR this phrase wants, plus where its peak falls.
    #
    # This used to take the first two entries whose category was contour, climax
    # or phrase_structure. The phrase_structure entries come first in every pack
    # and are a GLOSSARY — "Cell: Smallest recognizable unit", "Motif:
    # Characteristic rhythm + interval pattern" — so those two definitions
    # appeared under "Melody:" in every brief ever written, and the six real
    # contour priors ("Arch (rise-fall): completion, singing quality") never did.
    priors = _load_pack(composer, "melody_priors") or []
    priors = priors if isinstance(priors, list) else []
    by_cat: Dict[str, List[str]] = {}
    for pr in priors:
        cat = (pr.get("category", "") or "").lower()
        desc = (pr.get("description", "") or "").strip()
        if desc:
            by_cat.setdefault(cat, []).append(desc)
    fn = (getattr(slot, "function", "") or "").lower()
    role_l0 = (role or "").lower()
    # Match the contour to what the phrase is FOR, rather than taking whichever
    # one the pack happens to list first.
    if "cadential" in fn or "closing" in role_l0 or cad in ("PAC", "IAC"):
        want = ("descending", "arch")
    elif "antecedent" in fn or "presentation" in fn or "opening" in role_l0:
        want = ("arch", "ascending")
    elif "continuation" in fn or "develop" in fn:
        want = ("ascending", "wave")
    else:
        want = ("arch", "wave")
    shape: List[str] = []
    for token in want:
        for desc in by_cat.get("contour", []):
            if desc.lower().startswith(token) and desc not in shape:
                shape.append(desc)
                break
        if shape:
            break
    for cat in ("climax", "peak_timing"):
        if by_cat.get(cat):
            shape.append(by_cat[cat][0])
            break
    # The COMPOSER's own melodic voice leads, ahead of the generic contour and
    # climax priors. Those two generic lines were all this slice ever carried,
    # and they are identical for every composer — so the brief's melody doctrine
    # said the same thing whether it was building a Bach fugue subject or a
    # Chopin nocturne, while a `melodic-style.md` describing the actual voice sat
    # unread in 44 profile directories.
    voice = by_cat.get("composer_melodic_voice", [])
    if voice or shape:
        out["melody_priors"] = voice[:4] + shape[:2]

    # ── Richer compiled doctrine that previously reached only the fallback
    # engine (via ContextRouter). Surfaced here, phrase-scoped, so the agent
    # composes with the full doctrine the system actually compiled. ──

    # Modulation mechanism — when this phrase likely modulates (transition /
    # development / bridge / retransition role). The agent chooses whether and
    # how; this just puts the corpus mechanism in front of it.
    role_l = (role or "").lower()
    if any(k in role_l for k in ("transition", "develop", "bridge", "retrans", "modulat")):
        mods = _load_pack(composer, "modulation_scripts") or []
        picks = [
            f"{m.get('type', '')}: {m.get('mechanism', '')} ({m.get('smoothness', '')})"
            for m in (mods if isinstance(mods, list) else [])
            if m.get("mechanism")
        ]
        if picks:
            out["modulation_scripts"] = picks[:2]

    # Counterpoint guidance — a couple of preferred voice-leading rules; matters
    # whenever inner voices move (esp. contrapuntal / imitative textures).
    cps = _load_pack(composer, "counterpoint_rules") or []
    cp_lines = [
        c.get("description", "")
        for c in (cps if isinstance(cps, list) else [])
        if c.get("severity") in ("suggestion", "preferred", "rule") and c.get("description")
    ]
    if cp_lines:
        out["counterpoint"] = cp_lines[:2]

    # Figuration template matching the slot's LH accompaniment idiom — the
    # corpus's named realization of that texture (character + when-to-use).
    lh_textures = {
        (getattr(tp, "lh_texture", "") or "").lower()
        for tp in (getattr(slot, "texture_plan", None) or [])
    }
    figs = _load_pack(composer, "figuration_templates") or []
    fig_lines = []
    # The composer's own left-hand catalogue first, matched to this phrase's
    # planned textures where it can be and offered as alternatives where it
    # cannot. `<composer>-lh-vocabulary.md` exists to answer "what else could
    # the left hand be doing", which is the question behind the single most
    # mechanical thing this system produces: one accompaniment idiom, every bar,
    # for a whole piece. It was read by nothing.
    idioms = [
        f
        for f in (figs if isinstance(figs, list) else [])
        if f.get("category") == "composer_hand_idiom"
    ]
    matched = [
        i
        for i in idioms
        if lh_textures
        and any(t and t.split("_")[0] in i.get("name", "").lower() for t in lh_textures)
    ]
    for i in (matched or idioms)[:3]:
        fig_lines.append(f"LH idiom — {i.get('name', '')}: {i.get('description', '')[:180]}")

    # The composer's DEVICE catalogue. Every entry was loaded and then dropped:
    # the loop below matches on `pattern_keyword`, which the general figuration
    # library has and a device does not, so a device fell through both branches.
    # 276 entries across 13 packs reached the pack and never the composer — the
    # appoggiatura sigh, the terraced echo, the general pause, Beethoven's
    # sforzando on a weak beat. They are the most directly usable thing in the
    # pack, because each description carries the shorthand written out.
    devices = [
        f
        for f in (figs if isinstance(figs, list) else [])
        if f.get("category") == "composer_device"
    ]
    # A phrase needs BOTH kinds: something to do with the line, and something to
    # do with the shape. Which it needs MORE of depends on its job — a thematic
    # phrase leans melodic, a transition or a real cadential arrival leans
    # structural. Selecting on the cadence target alone put the same three
    # structural devices in front of every phrase, because nearly every phrase
    # has one.
    function = str(getattr(slot, "function", "") or "").lower()
    cadence = str(getattr(slot, "cadence_target", "") or "").lower()
    melodic = [d for d in devices if "melod" in str(d.get("section", "")).lower()]
    structural = [d for d in devices if "melod" not in str(d.get("section", "")).lower()]

    structural_lean = function in (
        "transition",
        "retransition",
        "sequence",
        "fragmentation",
        "liquidation",
        "cadential",
        "closing",
        "coda",
    ) or cadence in ("pac", "iac")
    # Rotate the starting point by the phrase's own bar so consecutive phrases
    # are not handed the identical three devices — the catalogue is 15 entries
    # deep and a piece should see more than the first three of them.
    offset = int(getattr(slot, "bar_start", 1) or 1)

    def _take(pool, n):
        if not pool:
            return []
        start = offset % len(pool)
        return [pool[(start + i) % len(pool)] for i in range(min(n, len(pool)))]

    picked = (
        _take(structural, 2) + _take(melodic, 1)
        if structural_lean
        else _take(melodic, 2) + _take(structural, 1)
    )
    for d in (picked or devices)[:3]:
        section = str(d.get("section", "") or "device").split("/")[0].strip()
        fig_lines.append(f"{section} — {d.get('name', '')}: {str(d.get('description', ''))[:200]}")

    # The general figuration library, matched to this phrase's planned textures.
    general = []
    for fdef in figs if isinstance(figs, list) else []:
        kw = (fdef.get("pattern_keyword", "") or "").lower()
        if kw and any(kw in lt for lt in lh_textures):
            char = fdef.get("character", "")
            use = (fdef.get("when_to_use") or [""])[0]
            general.append(f"{fdef.get('name', kw)} — {char}; {use}")
    fig_lines.extend(general[:2])

    # A per-category budget, not a global cap: `fig_lines[:5]` let the three LH
    # idioms take most of it and left no room for anything else.
    if fig_lines:
        out["figuration"] = fig_lines[:8]

    # Harmonic temperature — the tonal-motion intent appropriate to this phrase's
    # energy/role (prolongation early, instability mid, resolution at cadence).
    temps = _load_pack(composer, "harmonic_temperature") or []
    energy = 0.5
    curves = getattr(slot, "curves", None)
    if curves and getattr(curves, "energy", None):
        e = list(curves.energy)
        energy = sum(e) / len(e) if e else 0.5
    if isinstance(temps, list) and temps:
        if cad:
            want = ("cadence", "resolution", "dominant")
        elif role == "opening" or energy < 0.4:
            want = ("prolongation", "tonic")
        elif energy > 0.66:
            want = ("instability", "chromatic", "sequence", "tension")
        else:
            want = ("departure", "prolongation")
        picks = []
        for t in temps:
            blob = f"{t.get('category', '')} {t.get('tonal_move', '')}".lower()
            if any(w in blob for w in want):
                picks.append(f"{t.get('tonal_move', '')} — {t.get('narrative_meaning', '')}")
        if picks:
            out["harmonic_temperature"] = picks[:1]

    return out


def _is_structural_phrase(graph, slot) -> bool:
    """Structurally pivotal phrases — theme statements, climaxes, recapitulation
    entries, codas/final cadences — that most reward seeing MORE real corpus
    material. These are the moments where exemplar diversity pays off."""
    sec_id = (getattr(slot, "section_id", "") or "").lower()
    if any(k in sec_id for k in ("recap", "return", "reprise", "coda", "climax", "finale")):
        return True
    # The principal theme's own phrase. `principal_theme_id` names a MOTIF in
    # the motif bank, not a phrase, so comparing a phrase id against it was a
    # test that could never pass — this arm never fired for any piece.
    from .theme_planner import phrase_carries_theme

    if phrase_carries_theme(graph, getattr(slot, "phrase_id", "") or ""):
        return True
    # A phrase the narrative marks as a climax.
    nar = getattr(graph, "narrative", None)
    if nar and getattr(nar, "sections", None):
        sec = _narrative_section_for(graph, slot)
        if sec and sec.climax_type in ("primary", "secondary"):
            return True
    return False


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


# Density thresholds on the slot's 0-1 density curve, and the raw per-bar event
# counts they correspond to. The corpus's melody_density percentiles are
# 35th=4, 65th=7, so the curve's 0.35/0.65 breaks land on 4 and 7 events.
_INFER_LO_MID = 0.35
_INFER_MID_HI = 0.65
_INFER_BAND_EDGES = (4, 7)  # raw melody_density: <4 lo, 4-6 mid, >=7 hi

_TEXTURE_MODE_CACHE: Dict[str, List[Tuple[str, str]]] = {}

# Last-resort pair when there is no corpus to measure at all. Corpus-real
# labels only — see the vocabulary note in `_infer_textures`.
_INFER_FALLBACK = [
    ("held_note", "block_chord_sparse"),
    ("singing_melody", "bass_melody"),
    ("zigzag_figuration", "bass_melody"),
]


def _texture_modes(composer: str) -> List[Tuple[str, str]]:
    """The modal (rh, lh) texture pair per density band, measured from the
    composer's own corpus. Returns [lo, mid, hi].

    Derived rather than tabulated so it follows a corpus rebuild instead of
    going stale, and so no one has to hand-maintain a texture table.
    """
    key = composer or "_global"
    if key in _TEXTURE_MODE_CACHE:
        return _TEXTURE_MODE_CACHE[key]
    from collections import Counter

    rh: List[Counter] = [Counter(), Counter(), Counter()]
    lh: List[Counter] = [Counter(), Counter(), Counter()]
    seen = 0
    try:
        for bar in _iter_corpus_bars(composer):
            d = bar.get("melody_density", 0) or 0
            band = 2 if d >= _INFER_BAND_EDGES[1] else 1 if d >= _INFER_BAND_EDGES[0] else 0
            if bar.get("rh_texture"):
                rh[band][bar["rh_texture"]] += 1
            if bar.get("lh_texture"):
                lh[band][bar["lh_texture"]] += 1
            seen += 1
    except Exception:  # a missing or unreadable corpus is not a composing error
        seen = 0

    out: List[Tuple[str, str]] = []
    for band in range(3):
        # Too few bars in a band is not evidence; fall back rather than infer
        # a composer's idiom from a handful of measures.
        r = (
            rh[band].most_common(1)[0][0]
            if sum(rh[band].values()) >= 40
            else _INFER_FALLBACK[band][0]
        )
        left = (
            lh[band].most_common(1)[0][0]
            if sum(lh[band].values()) >= 40
            else _INFER_FALLBACK[band][1]
        )
        out.append((r, left))
    if seen < 200:
        out = list(_INFER_FALLBACK)
    _TEXTURE_MODE_CACHE[key] = out
    return out


def _infer_textures(slot, composer: str = "") -> List[Tuple[str, str]]:
    """Infer per-bar (rh, lh) textures when texture_plan is empty.

    This used to return three hard-coded pairs, and both halves were wrong.

    The RH pair for a dense bar was ``passage_work`` — a label from an older
    vocabulary that **the corpus does not produce at all** (see
    `_density_cache_is_current`, which documents the same dead label on the
    cache side). Every lookup keyed by it therefore missed: exemplar retrieval,
    per-texture density targets, and ornament stats. `_check_expression_zero`
    reads ornament density for the inferred RH texture and stays silent when it
    finds none, so for every dense phrase without a texture plan it could not
    fire — measured at 0.000 ornament density for `passage_work` across all 48
    packs.

    The LH pair was ``alberti`` for anything above the low band. Measured over
    all armed composers, alberti is not the modal LH texture at ANY density
    band — it is Mozart's habit (and Haydn's, and Beethoven's mid band) written
    into a function that every composer goes through. Bach's dense LH is
    broken_chord_wave, Chopin's block_chord_sparse, Monteverdi's walking_bass.

    So the modes are now measured per composer from the corpus itself.
    """
    curves = getattr(slot, "curves", None)
    density = list(getattr(curves, "density", []) or [])
    modes = _texture_modes(composer)
    out = []
    for i in range(slot.bar_count):
        d = density[i] if i < len(density) else 0.5
        band = 2 if d >= _INFER_MID_HI else 1 if d >= _INFER_LO_MID else 0
        out.append(modes[band])
    return out


def _slot_textures(slot, composer: str = "") -> List[Tuple[str, str]]:
    """Per-bar (rh, lh) textures — DECLARED where the slot has a plan, INFERRED
    otherwise.

    Callers that use the result to SUPPRESS a check must not use this: an
    inferred texture is a guess derived from a density curve, not evidence
    about the idiom, and suppressing on a guess switches the check off for
    every phrase that has no plan. Read `slot.texture_plan` directly there.
    """
    plan = getattr(slot, "texture_plan", None) or []
    if plan:
        return [
            (getattr(b, "rh_texture", "singing_melody"), getattr(b, "lh_texture", "bass_melody"))
            for b in plan
        ]
    return _infer_textures(slot, composer)


def _positions_for(slot, n_bars: int) -> List[str]:
    pos = ["middle"] * n_bars
    if n_bars:
        pos[0] = "opening"
        if getattr(slot, "cadence_target", "none") not in ("none", "", None):
            pos[-1] = "cadential"
    return pos


# ─── Exemplar retrieval & rendering ──────────────────────────────────────────


#: Corpus articulation names -> the shorthand suffix the agent writes.
_ARTICULATION_SUFFIXES = {
    "staccato": "stacc",
    "staccatissimo": "stacciss",
    "accent": "acc",
    "strong-accent": "marc",
    "marcato": "marc",
    "tenuto": "ten",
    "portato": "port",
    "detached-legato": "port",
    "legato": "leg",
    "spiccato": "spicc",
    "breath": "breath",
    "caesura": "caes",
}


def _tie_mark(event: Dict[str, Any]) -> str:
    """`~` when this corpus note ties into the next, as the shorthand spells it."""
    tie = str(event.get("tie") or "").strip().lower()
    return "~" if tie in ("start", "continue", "start-stop") else ""


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
            # Articulation and TIE, from the corpus record. These were never
            # rendered: the exemplar renderer emitted ornament suffixes and
            # nothing else, so a real bar reached the agent stripped of the
            # staccato it was written with and of every tie in it — while the
            # brief in the same breath instructs "TIE ACROSS BARLINES. The last
            # generated score had ZERO ties."
            #
            # Being shown 125,325 real bars containing no tie and told to write
            # one is not an instruction, it is a contradiction.
            suffix = ":grace" if is_grace else ""
            # The corpus stores this as a LIST — `['staccato']`, one entry in
            # all but a handful of bars. Stringifying it gave "['staccato']",
            # which matches no name, so every articulation in 125,325 bars was
            # dropped one step after being carried through.
            raw = e.get("artic")
            if isinstance(raw, (list, tuple)):
                raw = raw[0] if raw else ""
            artic = str(raw or "").strip().lower()
            if artic in _ARTICULATION_SUFFIXES:
                suffix += f":{_ARTICULATION_SUFFIXES[artic]}"
            if e.get("has_trill"):
                suffix += ":tr"
            if e.get("has_turn"):
                suffix += ":turn"
            if e.get("type") == "rest":
                if is_grace:
                    continue  # a zero-length rest carries no information
                toks.append(f"rest_{dur_code}")
            elif e.get("type") == "chord":
                # Two voices doubling one pitch arrive as a two-note "chord"
                # (`['G5','G5']`) — 1,471 of them across the corpus, 1.05% of
                # every chord, and the brief printed `[Ab5,Ab5]s` as material to
                # adapt. It is a real unison in the score and a nonsense chord in
                # shorthand, so the duplicate goes here, in the rendering, and
                # the bar records keep what they measured.
                pitches = _distinct_pitches(e.get("pitches", []))
                if len(pitches) > 1:
                    toks.append(f"[{','.join(pitches)}]{dur_code}{suffix}{_tie_mark(e)}")
                elif pitches:
                    toks.append(f"{pitches[0]}{dur_code}{suffix}{_tie_mark(e)}")
            elif e.get("pitch"):
                toks.append(f"{e['pitch']}{dur_code}{suffix}{_tie_mark(e)}")
        return toks

    def _with_inner(main_events, inner_events) -> str:
        # Real corpus polyphony — show the inner voice so the agent imitates it
        # rather than collapsing four parts into two.
        #
        # But `//` means "these two voices sound together", and when the MAIN
        # voice is empty this emitted a hand beginning " // B3q rest_e ..." —
        # a silent upper voice over an inner line, which is not what the bar
        # does and not something to imitate. 6.2% of multi-voice exemplar hands
        # read that way. One voice sounding is written as one voice.
        main = " ".join(_tokens(main_events))
        inner = " ".join(_tokens(inner_events or []))
        if main and inner:
            return f"{main} // {inner}"
        return main or inner

    rh = _with_inner(adapted.rh_events, getattr(adapted, "rh_inner_events", []))
    lh = _with_inner(adapted.lh_events, getattr(adapted, "lh_inner_events", []))
    return rh, lh


def _shorthand_beats(shorthand: str) -> Optional[float]:
    """Total metrical beats of a shorthand string (grace notes count 0).

    A ``//`` string carries **independent voices**, each of which fills the bar
    on its own, so the length of the bar is the length of its longest voice —
    not the sum. The previous version had no case for ``//`` at all: the token
    failed the note regex, the function returned ``None``, and both callers
    read ``None`` as "unparseable, don't judge it". So **every multi-voice
    exemplar bypassed the malformed-bar filter entirely** — which is most
    exemplars for exactly the composers where it matters most (a Bach sample
    averages four voices per bar). Measured across the armed corpus, 5% of the
    voices handed to the composer did not fill their bar, and the composer is
    told to adapt them.

    Returns None only if a token genuinely cannot be parsed.
    """
    if "//" in (shorthand or ""):
        lengths = [_shorthand_beats(v.strip()) for v in shorthand.split("//") if v.strip()]
        real = [x for x in lengths if x is not None]
        if not real:
            return None
        return round(max(real), 4)

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


def _shorthand_underfills_bar(shorthand: str, capacity: float) -> bool:
    """True when a shorthand bar clearly falls short of its meter.

    An unparseable bar returns False (never judged), and a small tolerance keeps
    a legitimately-notated tuplet remainder from being rejected.
    """
    beats = _shorthand_beats(shorthand)
    if beats is None or beats <= 0:
        return False
    return beats < capacity - 0.02


def _retrieve_exemplars_style(
    style_ref: str, slot, n_exemplars: int, warnings: List[str]
) -> List[ExemplarView]:
    """Gather exemplars from every armed member of a style/blend, interleaved so
    the brief shows real bars from several composers of that idiom (not one)."""
    members = _aggregate_members(style_ref)
    if not members:
        warnings.append(f"'{style_ref}' has no armed members")
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


_CORPUS_METER_CACHE: Dict[str, List[Tuple[int, int]]] = {}


def _corpus_meters(composer: str) -> List[Tuple[int, int]]:
    """Every metre this composer's corpus actually contains, commonest first."""
    key = composer or "_global"
    if key in _CORPUS_METER_CACHE:
        return _CORPUS_METER_CACHE[key]
    from collections import Counter

    counts: Counter = Counter()
    try:
        for bar in _iter_corpus_bars(composer):
            ts = bar.get("time_sig")
            if ts and len(ts) == 2:
                counts[(int(ts[0]), int(ts[1]))] += 1
    except Exception:
        pass
    out = [m for m, _ in counts.most_common()]
    _CORPUS_METER_CACHE[key] = out
    return out


def _is_compound(num: int, den: int) -> bool:
    """Compound metre: the beat divides into three (6/8, 9/8, 12/8, 6/16...)."""
    return den in (8, 16) and num in (6, 9, 12)


def _equivalent_meters(meter: Tuple[int, int], available) -> List[Tuple[int, int]]:
    """Corpus meters that are the SAME metrical structure as ``meter``, best first.

    A 4/2 bar and a 4/4 bar are the same measure notated at different levels —
    alla breve against common time. Palestrina wrote 58,038 of his 60,677 bars
    in 4/2 and not one in 4/4, so a 4/4 request matched nothing at any level of
    the texture relaxation and his brief came back EMPTY: 60,677 bars, tier A,
    unusable. Five other armed composers have no 4/4 bar either (bartok,
    bruckner, dvorak, mussorgsky, rimsky-korsakov).

    Ordered by how much borrowing costs: the same beat COUNT at another
    notation level first (a straight duration rescale), then any meter of the
    same total length (4/4 against 2/2), and nothing beyond that — a 3/4 bar is
    not a 4/4 bar and pretending otherwise teaches the wrong rhythm.
    """
    # A malformed metre defaults to 4/4 here exactly as it does in
    # `duration.bar_duration`, so the two cannot disagree about what (0, 0)
    # means. The guard that used to follow this could never fire — `or 4` had
    # already replaced the zero.
    num, den = int(meter[0] or 4), int(meter[1] or 4)
    target_compound = _is_compound(num, den)
    same_count, same_length = [], []
    target_len = Fraction(num * 4, den)
    for cand in available:
        if tuple(cand) == (num, den) or not cand or len(cand) != 2:
            continue
        c_num, c_den = int(cand[0] or 0), int(cand[1] or 0)
        if c_num <= 0 or c_den <= 0:
            continue
        # Simple and compound never borrow from each other. 3/4 and 6/8 are both
        # three quarters long, so a length test alone calls them equivalent —
        # but 6/8 is two dotted beats subdividing in threes and 3/4 is three
        # plain ones. Renotating either as the other by a duration factor
        # teaches exactly the wrong rhythm, which is the same objection that
        # keeps 2/4 away from 4/4.
        if _is_compound(c_num, c_den) != target_compound:
            continue
        if c_num == num:
            same_count.append((c_num, c_den))
        elif Fraction(c_num * 4, c_den) == target_len:
            same_length.append((c_num, c_den))
    # Prefer the closest notation level, so 4/4 borrows 4/2 before 4/8.
    same_count.sort(key=lambda m: abs(m[1] - den))
    same_length.sort(key=lambda m: abs(m[1] - den))
    return same_count + same_length


def _rescale_bar_durations(adapted, factor: Fraction) -> None:
    """Renotate an adapted bar at another metrical level, in place.

    Borrowing a 4/2 bar for a 4/4 phrase without this shows the agent eight
    beats of material for a four-beat bar — which the overflow guard then drops,
    so relaxing the meter alone would have changed nothing at all.
    """
    if factor == 1:
        return
    for name in ("rh_events", "rh_inner_events", "lh_events", "lh_inner_events"):
        for event in getattr(adapted, name, None) or []:
            dur = event.get("dur")
            if isinstance(dur, (int, float)) and dur > 0:
                event["dur"] = float(Fraction(dur).limit_denominator(64) * factor)


def _retrieve_exemplars(
    composer: str, slot, n_exemplars: int, warnings: List[str]
) -> List[ExemplarView]:
    if _aggregate_members(composer):
        return _retrieve_exemplars_style(composer, slot, n_exemplars, warnings)
    adapter = _adapter(composer)
    key = getattr(slot, "key", "C")
    key_mode = "minor" if is_minor_key(key) else "major"
    meter = tuple(getattr(slot, "meter", (4, 4)))

    textures = _slot_textures(slot, composer)
    positions = _positions_for(slot, len(textures))

    # One query per distinct (texture pair, position) in the phrase
    seen_specs = []
    for (rh, lh), pos in zip(textures, positions, strict=True):
        spec = (rh, lh, pos)
        if spec not in seen_specs:
            seen_specs.append(spec)

    exemplars: List[ExemplarView] = []
    used_sources: set = set()
    used_content: set = set()

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
        # Last relaxation: another NOTATION LEVEL of the same metre. Held back
        # until every texture and mode relaxation has failed, because borrowing
        # across levels needs a duration rescale and an exemplar in the phrase's
        # own metre is always the better teacher.
        borrowed_from: Optional[Tuple[int, int]] = None
        if not candidates:
            for alt in _equivalent_meters(meter, _corpus_meters(composer)):
                query.time_sig = alt
                query.rh_texture = rh
                query.lh_texture = lh
                query.key_mode = key_mode
                query.phrase_position = pos
                candidates = adapter.retrieve(query)
                if not candidates:
                    query.rh_texture = None
                    query.lh_texture = None
                    query.phrase_position = None
                    candidates = adapter.retrieve(query)
                if candidates:
                    borrowed_from = alt
                    warnings.append(
                        f"{composer} has no {meter[0]}/{meter[1]} bars; exemplars "
                        f"renotated from {alt[0]}/{alt[1]}"
                    )
                    break
            query.time_sig = meter
        if not candidates:
            # Name the REAL blocker. This used to report the texture in every
            # case — "no corpus exemplars for singing_melody/broken_chord_wave"
            # for a 6/8 Bach phrase, when Bach has thousands of bars of that
            # texture and simply never wrote 6/8. A message that names the wrong
            # cause sends the next reader after a problem that does not exist.
            available_meters = _corpus_meters(composer)
            if available_meters and tuple(meter) not in available_meters:
                spelled = ", ".join(f"{m[0]}/{m[1]}" for m in available_meters[:4])
                warnings.append(
                    f"{composer} has no {meter[0]}/{meter[1]} bars and nothing "
                    f"metrically equivalent to borrow — he wrote {spelled}. "
                    f"The metre, not the texture, is what yields nothing here."
                )
            else:
                warnings.append(f"no corpus exemplars for {rh}/{lh}/{pos} in {composer}")
            continue
        # Map the source BAR LENGTH onto the target's, not denominator onto
        # denominator. 4/2 is eight quarters against 4/4's four, so it halves;
        # 2/2 is already four and must not be touched. The denominator form got
        # the first case right and quietly halved the second to a two-beat bar,
        # which the overflow guard then dropped — Mussorgsky and Bruckner still
        # came back empty while the warning claimed their bars were renotated.
        rescale = Fraction(1)
        if borrowed_from:
            src_len = Fraction(borrowed_from[0] * 4, borrowed_from[1])
            tgt_len = Fraction(int(meter[0] or 4) * 4, int(meter[1] or 4))
            if src_len > 0:
                rescale = tgt_len / src_len

        added = 0
        # Why bars were dropped. Every filter below is a `continue`, so a spec
        # whose candidates ALL fail returns nothing and says nothing — handel and
        # schubert came back with zero exemplars and zero warnings, which reads
        # as "this composer has no material" when it is really "every bar we
        # found was unusable, and here is why".
        dropped: Dict[str, int] = {}

        def _drop(reason: str) -> None:
            dropped[reason] = dropped.get(reason, 0) + 1

        for bar in candidates:
            src = f"{bar.get('source', '?')}:{bar.get('bar_num', '?')}"
            if src in used_sources:
                _drop("already shown")
                continue
            # A truncated record is only PART of a bar (the extractor caps how
            # many events it stores). Presenting half a bar as a bar to adapt
            # teaches a rhythm that does not fill the measure.
            if bar.get("truncated"):
                _drop("truncated record")
                continue
            # An OLD-FORMAT record, from before the extractor learned to emit
            # rh_display/time_sig/harmony. What reaches the brief from one of
            # these is half a bar: Corelli's exemplars came out with an empty
            # right hand and a "left hand" playing at E5 — his melody, filed as
            # accompaniment. That does not teach less than a rich record, it
            # teaches something false (the melody is silent, the accompaniment
            # sits in the treble). `composer_coverage_tier` already flags these
            # composers `needs_reacquire`; this stops the brief showing their
            # bars as though they were usable in the meantime.
            if "rh_display" not in bar:
                _drop("old record format — composer needs re-acquiring")
                continue
            adapted = adapter.transpose_bar(bar, key)
            _rescale_bar_durations(adapted, rescale)
            rh_sh, lh_sh = _adapted_to_shorthand(adapted)
            if not rh_sh and not lh_sh:
                _drop("no notes after adaptation")
                continue
            # Skip bars whose RH or LH overflows the meter — a corrupted
            # multi-voice flatten in the corpus record. Showing them misleads
            # Claude and they fail meter validation if copied. (See
            # _shorthand_overflows_bar.)
            capacity = float(bar_duration(meter))
            if _shorthand_overflows_bar(rh_sh, capacity) or _shorthand_overflows_bar(
                lh_sh, capacity
            ):
                _drop("overflows the bar")
                continue
            # …and bars that fall SHORT of the meter. Only overflow was checked,
            # so half-bars reached briefs as complete bars to adapt — an exemplar
            # reading "RH: F4q  LH: [F3,A3]q F2q" in a 3/4 phrase teaches a bar
            # that is a beat and a half short, and the agent that copies its
            # rhythm writes a bar the meter gate then rejects.
            if _shorthand_underfills_bar(rh_sh, capacity) or _shorthand_underfills_bar(
                lh_sh, capacity
            ):
                _drop("underfills the bar")
                continue
            # Dedup by CONTENT, not just by source bar. Two different bars of a
            # sonata are frequently the same music (an exposition bar and its
            # recapitulation), and showing the identical bar twice spends the
            # agent's attention without adding an idiom.
            fingerprint = (rh_sh, lh_sh)
            if fingerprint in used_content:
                _drop("duplicate of a bar already shown")
                continue
            used_content.add(fingerprint)
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
                    # A bar that holds ONE harmony has no within-bar events, and
                    # the exemplar then printed no harmony at all — the agent saw
                    # real notes with no idea what chord they spell.
                    harmony=(
                        " ".join(
                            f"{e.get('beat'):g}:{e.get('roman')}"
                            for e in (bar.get("harmony_events") or [])
                            if e.get("roman")
                        )
                        or (f"1:{bar['roman']}" if bar.get("roman") else "")
                    ),
                )
            )
            used_sources.add(src)
            added += 1
            if added >= per_spec or len(exemplars) >= n_exemplars:
                break
        if added == 0 and dropped:
            why = ", ".join(f"{n} {reason}" for reason, n in sorted(dropped.items()))
            warnings.append(
                f"{composer}: {len(candidates)} candidate bars for {rh}/{lh}/{pos} "
                f"were all unusable ({why})"
            )
        if len(exemplars) >= n_exemplars:
            break

    return exemplars[:n_exemplars]


# ─── Target stats ─────────────────────────────────────────────────────────────

# Fallback bands when a composer has no corpus_profile — shown to the composer
# as a TARGET, and therefore shown exactly when the system knows least, where a
# wrong number does the most harm.
#
# The bands here were hand-written, and measuring the 28 composer profiles that
# DO exist falsified all three:
#
#   texture_change_pct           was "0.4-0.6"   real: min 0.088  median 0.269  max 0.598
#                                                only 5 of 36 composers fall inside it,
#                                                and its floor is above the median
#   melody_direction_change_pct  was "0.3-0.6"   real: min 0.346  median 0.558  max 0.667
#                                                its ceiling excludes the top quarter
#   density_cv                   was ">=0.30"    real: min 0.213  median 0.318  max 0.583
#                                                12 of 36 real composers are below it
#
# An unprofiled composer was being told to change texture roughly twice as often
# as a typical real one. Each band is now the measured middle half (p25-p75) with
# the median named, so the target is a place real music actually sits.
_DISCRIMINATOR_FALLBACK = {
    "texture_change_pct": (
        "0.18-0.33 (median 0.27 across 28 measured composers; the full real "
        "range is 0.09-0.60, so a settled texture is not a fault)"
    ),
    "melody_direction_change_pct": (
        "0.51-0.59 (median 0.56 across 27 measured composers; real range 0.35-0.67)"
    ),
    "density_cv": (
        "0.27-0.36 (median 0.32 across 28 measured composers; real range 0.21-0.58) "
        "— let density ebb and flow"
    ),
}


# Domain of each metric, so mean ± σ never prints an impossible band.
_METRIC_BOUNDS = {
    "texture_change_pct": (0.0, 1.0),
    "lh_texture_change_pct": (0.0, 1.0),
    "rh_texture_change_pct": (0.0, 1.0),
    "density_cv": (0.0, None),
    "melody_direction_change_pct": (0.0, 1.0),
    "events_per_bar": (0.0, None),
    "mean_abs_interval": (0.0, None),
    "leap_ratio": (0.0, 1.0),
    "wide_leap_ratio": (0.0, 1.0),
    "repeat_ratio": (0.0, 1.0),
    "melodic_range": (0.0, None),
    "eighth_ratio": (0.0, 1.0),
    "sixteenth_ratio": (0.0, 1.0),
    "triplet_ratio": (0.0, 1.0),
    "dotted_eighth_ratio": (0.0, 1.0),
    "dur_variety": (0.0, None),
    "chord_pct": (0.0, None),
    "chromatic_ratio": (0.0, 1.0),
    "seventh_chord_ratio": (0.0, 1.0),
}
# Only meaningful across a movement, not within one phrase.
_MOVEMENT_SCALE_METRICS = {"melodic_range", "dur_variety"}


def _discriminator_targets(composer: str, slot=None) -> Dict[str, str]:
    """Per-composer targets for the human-vs-AI discriminator metrics.

    Derived from the composer's own corpus distribution (corpus_profile.json)
    as [mean-σ, mean+σ] bands per metric, so the agent aims at THIS composer's
    real spread rather than a generic constant. Falls back to fixed guidance.

    ``slot`` (optional) lets phrase-scale briefs drop metrics that are only
    meaningful across a whole movement.
    """
    profile = corpus_profile(composer)
    metrics = profile.get("metrics", {}) if isinstance(profile, dict) else {}
    if not metrics:
        return dict(_DISCRIMINATOR_FALLBACK)
    out: Dict[str, str] = {}
    # Texture/rhythm-rate discriminators PLUS the melody / rhythm-value /
    # harmony dimensions — so the agent aims at the composer's real melodic
    # leap profile, rhythmic-value mix, and chordal density, not just texture.
    for name in (
        # texture & density
        "texture_change_pct",
        "lh_texture_change_pct",
        "density_cv",
        "melody_direction_change_pct",
        "events_per_bar",
        # melody — the biggest "mechanical" tell when wrong
        "mean_abs_interval",
        "leap_ratio",
        "wide_leap_ratio",
        "repeat_ratio",
        "melodic_range",
        # rhythm-value vocabulary
        "eighth_ratio",
        "sixteenth_ratio",
        "triplet_ratio",
        "dotted_eighth_ratio",
        "dur_variety",
        # harmony
        "chord_pct",
        "chromatic_ratio",
        "seventh_chord_ratio",
    ):
        m = metrics.get(name)
        if not m:
            continue
        # Metrics measured over a whole MOVEMENT do not transfer to an 8-bar
        # phrase. Printing "melodic_range = 34-52 semitones" as a target for a
        # single phrase asks for four octaves in eight bars — unreachable, and
        # it teaches the agent that the numbers are not to be taken literally.
        if name in _MOVEMENT_SCALE_METRICS and getattr(slot, "bar_count", 99) < 16:
            continue  # slot is None for whole-piece callers → metric kept
        mean, sd = m.get("mean", 0.0), m.get("stdev", 0.0)
        lo, hi = mean - sd, mean + sd
        # Clamp to each metric's real domain. mean ± σ on a bounded quantity
        # printed impossible bands — "triplet_ratio = -0.04 to 0.34",
        # "seventh_chord_ratio = -0.01 to 0.05" — which read as noise.
        bound = _METRIC_BOUNDS.get(name)
        if bound:
            if bound[0] is not None:
                lo = max(bound[0], lo)
            if bound[1] is not None:
                hi = min(bound[1], hi)
        out[name] = f"{round(lo, 2)}–{round(hi, 2)} (corpus mean {round(mean, 2)})"
    return out or dict(_DISCRIMINATOR_FALLBACK)


def _scale_density(entry: Dict[str, Any], beats: int) -> Dict[str, Any]:
    """Corpus density for THIS phrase's meter, falling back to the pooled figure.

    Densities are pooled over every meter the composer wrote in, so the raw
    events-per-bar median for a texture is dominated by whichever meter he used
    most: Mozart's Alberti bass runs a median of 8 events in a 4-beat bar and 6
    in a 3-beat bar, and the pooled figure told every 3/4 phrase 8. The density
    gate then measured the phrase against that same wrong number.
    """
    bucket = (entry.get("by_meter") or {}).get(str(beats))
    return bucket or entry


def _build_target_stats(composer: str, slot, warnings: List[str]) -> Dict[str, Any]:
    density = texture_density_stats(composer)
    ornaments = ornament_stats(composer)
    templates = _texture_templates(composer)
    rh_templates = templates.get("rh_templates", {})
    self_cont = _self_continuation(composer)

    textures = _slot_textures(slot, composer)
    rh_set = sorted({t[0] for t in textures})
    lh_set = sorted({t[1] for t in textures})

    stats: Dict[str, Any] = {
        "rh_textures": {},
        "lh_textures": {},
        "self_continuation": {t: self_cont[t] for t in lh_set if t in self_cont},
        "discriminators": _discriminator_targets(composer, slot),
    }

    beats_here = _beat_count(getattr(slot, "meter", (4, 4)) or (4, 4))
    expected_rh_total = 0.0
    for t in rh_set:
        entry: Dict[str, Any] = {}
        d = density.get("rh", {}).get(t)
        if d:
            entry["events_per_bar"] = _scale_density(d, beats_here)
            expected_rh_total += entry["events_per_bar"]["median"]
        tmpl = rh_templates.get(t, {})
        # Measured from the corpus, not from the builderless hand-authored file
        # in tools/texture_templates/ (see ornament_stats).
        orn = (ornaments.get("textures") or {}).get(t) or {}
        measured = {
            k: v
            for k, v in orn.items()
            if k in ("grace", "trill", "mordent", "turn", "dotted") and v
        }
        if measured:
            entry["ornament_density"] = measured
        elif tmpl.get("avg_ornament_density"):
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
            stats["lh_textures"][t] = {"events_per_bar": _scale_density(d, beats_here)}
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
    """The piece's open expectations, across EVERY scale.

    This read only ``CrossScaleLedger.phrase_ledger``. Expectations are recorded
    at the scale they belong to — a promise to recapitulate a theme is a
    *movement*-scale obligation and a cadence debt is a *section*-scale one —
    and essentially nothing is ever recorded at phrase scale. So the brief's
    ledger section was empty for every phrase of every piece even once the
    ledger was being populated: it was reading the one drawer nothing is filed
    in. Long-range coherence is the whole point of the subsystem, and a
    phrase-composer that cannot see a debt cannot pay it.
    """
    live = getattr(graph, "expectation_ledger", None)
    if live is not None and getattr(live, "entries", None):
        return live
    raw = getattr(graph, "cross_scale_ledger", None)
    if not raw:
        return live
    try:
        from .cross_scale_ledger import CrossScaleLedger

        csl = CrossScaleLedger.from_dict(raw)
    except Exception:
        return live

    class _AllScales:
        """A read-only view whose ``entries`` spans every scale."""

        def __init__(self, ledger):
            self._csl = ledger
            phrase = list(getattr(ledger.phrase_ledger, "entries", []) or [])
            wider = [e for e in ledger.get_all_open() if e not in phrase]
            self.entries = phrase + wider

        def __getattr__(self, name):
            # The caller expects an ExpectationLedger's API (prohibitions,
            # cooldowns, locks). CrossScaleLedger is a container of those, so
            # forward to the phrase ledger first and only then to the container.
            inner = getattr(self._csl, "phrase_ledger", None)
            if inner is not None and hasattr(inner, name):
                return getattr(inner, name)
            return getattr(self._csl, name)

    view = _AllScales(csl)
    return view if view.entries else (live or None)


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
    # These three ledger queries all exist (expectation_ledger.py). Catching bare
    # Exception around them meant a real bug in the ledger — the module that
    # carries every long-range musical promise — surfaced as an empty
    # "THIS PHRASE MUST / MUST NOT" block and nothing else. Narrow the catch to
    # the shapes that legitimately vary (an older graph, a missing attribute) so
    # anything else is loud.
    try:
        for e in ledger.get_active_prohibitions(cur, order):
            out["must_not_use"].append(
                {"object": getattr(e, "object_ref", ""), "form": getattr(e, "expected_form", None)}
            )
        for e in ledger.get_active_cooldowns(cur, order):
            out["cooldown"].append({"object": getattr(e, "object_ref", "")})
        for e in ledger.get_locks():
            out["locked"].append(
                {"object": getattr(e, "object_ref", ""), "form": getattr(e, "expected_form", None)}
            )
    except (AttributeError, TypeError, KeyError, ValueError) as exc:
        logger.warning("ledger constraints unavailable for %s: %s", cur, exc)
    return out


def _ledger_lines(graph, phrase_id: str) -> List[str]:
    """Open expectations THIS phrase can act on, plus a count of the rest.

    Every open entry was listed, so a phrase in the exposition was shown the
    recapitulation's cadence debt and the coda's — eight obligations, most of
    them belonging to sections that have not happened yet. A list where almost
    nothing is this phrase's business reads as noise and gets skipped, which
    defeats the point of a ledger.
    """
    ledger = _reconstruct_ledger(graph)
    entries = (getattr(ledger, "entries", None) if ledger else None) or []
    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    section = (getattr(slot, "section_id", "") or "").lower()

    mine: List[str] = []
    elsewhere = 0
    for e in entries:
        status = getattr(e, "status", "")
        if status in ("fulfilled", "expired", "satisfied", "violated"):
            continue
        kind = getattr(e, "kind", getattr(e, "type", "expectation"))
        obj = str(getattr(e, "object_ref", "") or "")
        scale = str(getattr(e, "scale", "") or "").lower()
        low = obj.lower()
        # A movement-scale obligation is everyone's business; a section-scale one
        # is only the business of phrases in that section.
        # Match the section EXACTLY, as the trailing component of the reference.
        # A substring test makes "m1_a" match "m1_a2", so every phrase of the A
        # section was also shown the return section's debt.
        owner = low.split("cadence_resolution_")[-1] if "cadence_resolution_" in low else ""
        relevant = (
            scale in ("movement", "piece")
            or (section and owner == section)
            or (section and not owner and section in low)
        )
        if relevant:
            mine.append(f"{kind}: {obj} ({status or 'open'})")
        else:
            elsewhere += 1
    if elsewhere:
        mine.append(f"({elsewhere} more open elsewhere in the piece — not this phrase's to pay)")
    return mine[:8]


def _last_events_summary(layer, n: int = 4) -> Dict[str, Any]:
    """Tail of a realized LayerIR: what the next phrase must connect to."""
    if layer is None:
        return {}
    events = sorted(layer.principal_line, key=lambda e: (e.bar, e.beat))
    tail = [e for e in events if e.pitch != "rest"][-n:]
    bass = sorted(layer.bass_foundation, key=lambda e: (e.bar, e.beat))
    last_bass = next((e for e in reversed(bass) if e.pitch != "rest"), None)
    dyn = next((e.dynamic for e in reversed(events) if e.dynamic), None)
    # Chords are lists. Interpolating one straight into an f-string printed
    # Python list syntax ("['E5', 'G5', 'B-5']dq") as the note the next phrase
    # must connect to — unreadable as music and unparseable as shorthand.
    out = {
        "melody_tail": [f"{_pitch_token(e.pitch)}{e.duration}" for e in tail],
        "last_bass": (_pitch_token(last_bass.pitch) if last_bass else None),
        "last_dynamic": dyn,
    }
    # The whole final BAR, both hands, is what a composer actually looks at to
    # continue a line — four melody notes with no accompaniment and no metric
    # position is not enough to join two phrases seamlessly.
    last_bar = max((e.bar for e in events), default=None)
    if last_bar is not None:

        def _bar_tokens(seq):
            evs = sorted(
                (e for e in seq if e.bar == last_bar), key=lambda e: (e.beat, str(e.pitch))
            )
            return " ".join(
                f"{'rest_' + e.duration if e.pitch == 'rest' else _pitch_token(e.pitch) + e.duration}"
                for e in evs
                if e.pitch
            )

        rh = _bar_tokens(layer.principal_line)
        lh = _bar_tokens(layer.bass_foundation + layer.response_layer)
        if rh or lh:
            out["last_bar"] = {"bar": last_bar, "rh": rh, "lh": lh}
    return out


def _cadence_signature(layer, bar_count: int) -> Optional[Dict[str, Any]]:
    """How a realized phrase actually CLOSED — its last bar, described.

    Rhythm, final melodic interval, whether it lands on a strong beat, whether
    it is followed by a rest, and whether anything is held over the barline.
    That is enough to say "this phrase closed the same way as that one".
    """
    if layer is None or not layer.principal_line:
        return None
    last_bar = max(e.bar for e in layer.principal_line)
    bar_events = sorted(
        (e for e in layer.principal_line if e.bar == last_bar), key=lambda e: e.beat
    )
    if not bar_events:
        return None
    sounding = [e for e in bar_events if e.pitch != "rest"]
    if not sounding:
        return None
    final = sounding[-1]
    rhythm = tuple((round(float(e.beat), 3), e.duration) for e in bar_events)
    interval = None
    if len(sounding) >= 2:
        try:
            from .pitch import pitch_to_midi

            a, b = sounding[-2].pitch, final.pitch
            if isinstance(a, str) and isinstance(b, str):
                interval = pitch_to_midi(b) - pitch_to_midi(a)
        except (ValueError, KeyError, TypeError):
            interval = None
    return {
        "bar": last_bar,
        "rhythm": rhythm,
        "final_beat": round(float(final.beat), 3),
        "on_strong_beat": abs(final.beat - round(final.beat)) < 0.01
        and int(round(final.beat)) in (1, 3),
        "ends_with_rest": bar_events[-1].pitch == "rest",
        "tied_over": final.tie in ("start", "continue"),
        "final_interval": interval,
        "final_pitch": final.pitch if isinstance(final.pitch, str) else None,
    }


def _cadences_already_used(graph, phrase_id: str) -> Dict[str, Any]:
    """Every cadence already committed in this piece, so this one can differ.

    The single loudest measured defect in generated output was **seven of nine
    phrase endings sharing one cadential rhythm** — every phrase closing the
    same way, so the form had no punctuation. The cause is structural: each
    phrase is composed in an isolated subagent context that has no idea how any
    other phrase ended, so the same locally-reasonable close gets chosen every
    time.

    This puts the history in front of the composer BEFORE it writes, which is
    the only point at which it can act on it.
    """
    state = graph.phrases.get(phrase_id)
    if state is None or state.slot is None:
        return {}
    here = state.slot.bar_start or 0
    used: List[Dict[str, Any]] = []
    # Scoped to this movement. Bar numbers RESTART per movement — a two-movement
    # sonatina has two phrases at bar 1 and two at bar 38 — so the
    # `bar_start < here` filter below silently admitted an arbitrary slice of the
    # other movement: for a phrase at bar 20 of movement 2, all of movement 1's
    # bars 1-19 and none of its bars 20-38. That both over-reports reuse (a
    # cadence is allowed to recur across movements) and does it inconsistently.
    scoped = _phrases_in_scope(graph, getattr(state.slot, "section_id", "") or "")
    for ps in scoped:
        pid = getattr(getattr(ps, "slot", None), "phrase_id", "") or ""
        if pid == phrase_id or not ps.realized or ps.slot is None:
            continue
        if (ps.slot.bar_start or 0) >= here:
            continue  # only what has already happened
        sig = _cadence_signature(ps.realized, ps.slot.bar_count or 1)
        if sig:
            sig["phrase_id"] = pid
            sig["planned"] = getattr(ps.slot, "cadence_target", "") or ""
            used.append(sig)
    used.sort(key=lambda s: s["bar"])
    if not used:
        return {}
    counts: Dict[Any, int] = {}
    for s in used:
        counts[s["rhythm"]] = counts.get(s["rhythm"], 0) + 1
    repeated = max(counts.values()) if counts else 0
    return {
        "closes_so_far": used[-6:],
        "distinct_rhythms": len(counts),
        "most_repeated": repeated,
        "warn": repeated >= 2,
    }


def _texture_and_register_run(graph, phrase_id: str) -> Dict[str, Any]:
    """How long the current texture and register have already been going.

    A phrase composed in an isolated context has no idea that the eight bars
    before it were all melody-and-accompaniment in the same octave — so it
    writes a ninth, and the piece sits in one place. The analyzers can see this
    afterwards; only the brief can prevent it.
    """
    state = graph.phrases.get(phrase_id)
    if state is None or state.slot is None:
        return {}
    here = state.slot.bar_start or 0
    prior = [
        ps
        for ps in graph.phrases.values()
        if ps.realized and ps.slot and (ps.slot.bar_start or 0) < here
    ]
    if not prior:
        return {}
    prior.sort(key=lambda ps: ps.slot.bar_start or 0)
    try:
        from .direct_compose import merge_phrases
        from .voicing import texture_runs
    except ImportError:
        return {}
    try:
        merged = merge_phrases(
            [ps.realized for ps in prior],
            key=(prior[0].slot.key if prior[0].slot else "C"),
            meter=(tuple(prior[0].slot.meter) if prior[0].slot else (4, 4)),
            piece_id=graph.piece_id,
        )
        runs = texture_runs(merged)
    except Exception:
        return {}
    out: Dict[str, Any] = {}
    if runs:
        label, b0, b1 = runs[-1]
        out["current_texture"] = label
        out["texture_unchanged_for"] = (b1 - b0) + 1
        out["texture_since_bar"] = b0
    # Where the melody has been sitting, so this phrase can move if it should.
    tops = [
        e.pitch
        for ps in prior[-2:]
        for e in (ps.realized.principal_line or [])
        if isinstance(e.pitch, str) and e.pitch != "rest"
    ]
    if tops:
        from .pitch import pitch_to_midi

        vals = []
        for pname in tops:
            try:
                vals.append(pitch_to_midi(pname))
            except (ValueError, KeyError, TypeError):
                continue
        if vals:
            out["recent_melody_low"] = min(vals)
            out["recent_melody_high"] = max(vals)
            out["recent_melody_span"] = max(vals) - min(vals)
    return out


def _resolve_for_transition(graph) -> str:
    """The composer id for corpus lookups during transition analysis."""
    return (getattr(getattr(graph, "style_dna", None), "composer_id", "") or "").lower()


def _transition_context(graph, phrase_id: str) -> Dict[str, Any]:
    """Continuity info from the previous phrase, read from disk state."""
    out: Dict[str, Any] = {}
    state = graph.phrases.get(phrase_id)
    if state is None:
        return out
    cadences = _cadences_already_used(graph, phrase_id)
    if cadences:
        out["cadence_history"] = cadences
    run = _texture_and_register_run(graph, phrase_id)
    if run:
        out["texture_run"] = run
    habits = _transition_habits(
        _resolve_for_transition(graph), state.slot, out.get("continuation") or {}
    )
    if habits:
        out["transition_habits"] = habits

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

    # Derive the continuation from the previous phrase's REALIZED music.
    #
    # This used to copy `slot.continuation`, a `ContinuationContext` dataclass
    # declaring thirteen fields that no code outside models.py has ever written.
    # So the block below — which the brief renders in full, including the
    # hanging-dominant warning and the list of motifs already stated — was empty
    # for every phrase of every piece. There are now two representations of one
    # idea and only this one is alive; see the note on ContinuationContext.
    if prev_id and prev_id in graph.phrases:
        derived = _derive_continuation(graph, prev_id)
        if derived:
            out["continuation"] = derived
    return out


def _derive_continuation(graph, prev_id: str) -> Dict[str, Any]:
    """What the previous phrase leaves behind, read off its committed notes."""
    prev = graph.phrases.get(prev_id)
    layer = getattr(prev, "realized", None) if prev else None
    if layer is None:
        return {}
    out: Dict[str, Any] = {}

    mel = sorted(
        (e for e in (layer.principal_line or []) if e.pitch != "rest"),
        key=lambda e: (e.bar, e.beat),
    )
    if not mel:
        return {}
    last_bar = mel[-1].bar
    slot_for_key = getattr(prev, "slot", None)

    # Where the phrase came to rest — the pitch, the direction it arrived from,
    # the bass under it, and anything left hanging. `counterpoint.phrase_tail`
    # is the ONE implementation of this: it reads the real interval above the
    # bass and was falsified against 126 real phrase endings, where a first
    # heuristic (counting fourths, tritones and major sevenths as unpaid debts)
    # fired on 49% of them. Re-deriving contour or a hanging dissonance here
    # would be a second, unfalsified answer to the same question.
    try:
        from .counterpoint import phrase_tail

        tail_facts = phrase_tail(layer, key=getattr(slot_for_key, "key", None)) or {}
    except Exception:
        tail_facts = {}
    for field_name in (
        "last_soprano_pitch",
        "last_soprano_contour",
        "last_bass_pitch",
        "pending_resolution",
    ):
        if tail_facts.get(field_name):
            out[field_name] = tail_facts[field_name]
    out.setdefault("last_soprano_pitch", _pitch_token(mel[-1].pitch))

    out["last_rh_density"] = float(sum(1 for e in mel if e.bar == last_bar))
    lh = [
        e
        for e in (layer.bass_foundation or []) + (layer.response_layer or [])
        if e.pitch != "rest" and e.bar == last_bar
    ]
    out["last_lh_density"] = float(len(lh))

    slot = getattr(prev, "slot", None)
    textures = _slot_textures(slot) if slot else []
    if textures:
        out["last_rh_texture"], out["last_lh_texture"] = textures[-1]
    if slot is not None:
        out["last_key"] = getattr(slot, "key", None)
        plan = getattr(slot, "harmony_plan", None) or []
        if plan:
            out["last_chord"] = plan[-1]
            # A PLANNED dominant close is a weaker signal than a sounding one,
            # so it only fills in where the notes said nothing.
            from .harmony_analysis import roman_function

            mode = "minor" if is_minor_key(getattr(slot, "key", "C") or "C") else "major"
            if roman_function(plan[-1], mode) == "dominant":
                out.setdefault("pending_resolution", "the dominant, left hanging")
    dyn = next((e.dynamic for e in reversed(mel) if e.dynamic), None)
    if dyn:
        out["last_dynamic"] = dyn

    # Which motifs the piece has already put on the table, so the next phrase
    # develops rather than invents.
    stated, developed = [], []
    for st in _phrases_before(graph, slot) if slot else []:
        s2 = getattr(st, "slot", None)
        if s2 is None or not getattr(st, "realized", None):
            continue
        for mt in getattr(s2, "motif_transforms", None) or []:
            params = getattr(mt, "params", None) or (
                mt.get("params") if isinstance(mt, dict) else {}
            )
            mid = (params or {}).get("motif_id")
            op = getattr(mt, "operation", "") or (
                mt.get("operation") if isinstance(mt, dict) else ""
            )
            if not mid:
                continue
            (stated if op in ("", "state") else developed).append(mid)
    if stated:
        out["motifs_stated"] = sorted(dict.fromkeys(stated))
    if developed:
        out["motifs_developed"] = sorted(dict.fromkeys(developed))
    return out


# ─── Public API ──────────────────────────────────────────────────────────────


def _key_obj(key: str):
    """Delegates to the single canonical parser (pitch.parse_key)."""
    from .pitch import parse_key

    return parse_key(key)


def _chord_frame(slot, key: str) -> List[Dict[str, Any]]:
    """Per-bar chord tones (note names) the agent voices against — the concrete
    aid that prevents vertical clashes.

    Tones are spelled the way the shorthand writes them ("Bb", not music21's
    "B-"): the frame is meant to be copied into a bar, and a token the parser
    rejects is a note that never reaches the score.
    """
    from .harmony_analysis import roman_pitches
    from .pitch import is_minor_key, key_to_root_midi, midi_to_pitch

    detail = getattr(slot, "harmony_detail", None) or []
    meter = tuple(getattr(slot, "meter", (4, 4)) or (4, 4))
    beats = _beat_count(meter)
    mode = "minor" if is_minor_key(key) else "major"
    tonic_pc = key_to_root_midi(key) % 12
    out: List[Dict[str, Any]] = []

    key_obj = _key_obj(key)

    def _tones(roman: str) -> List[str]:
        # Spell from the CHORD, not from the key signature. Reducing a chord to
        # pitch classes and then naming them by the prevailing key signature
        # spells G minor's raised leading tone as G-flat instead of F-sharp — so
        # the frame handed the agent V = D/Gb/A, which is not a chord. music21
        # knows a Roman numeral's own spelling; only the accidental style is ours
        # ("Bb", not "B-", because the frame is meant to be copied into a bar and
        # a token the parser rejects is a note that never reaches the score).
        # `harmony_analysis` is this project's Roman parser and decides WHICH
        # NOTES the symbol means; music21 is used only to SPELL them, and only
        # when the two agree about the notes.
        #
        # music21 reads some of this project's own symbols differently, and
        # silently — it does not raise. `#viio` in D minor is the leading-tone
        # diminished triad, C#-E-G; music21 raises a viio whose root is already
        # the leading tone and returns C##-E#-G#. The agent was handed a chord
        # spelled with a double sharp and told it was the harmony.
        pcs = roman_pitches(roman, tonic_pc, mode)
        try:
            import music21

            names = [p.name for p in music21.roman.RomanNumeral(roman, key_obj).pitches]
            spelled = [n.replace("-", "b") for n in names]
            if spelled and (
                not pcs or [music21.pitch.Pitch(n).pitchClass for n in names] == list(pcs)
            ):
                return spelled
        except Exception:
            pass
        if not pcs:
            return []
        # Spelling from the key signature alone turns a raised leading tone into
        # a flat (G minor's V became D/Gb/A), so prefer music21 above; this is
        # the honest fallback when the two readings disagree.
        return [midi_to_pitch(60 + pc, key)[:-1] for pc in pcs]

    for i, roman in enumerate(getattr(slot, "harmony_plan", []) or []):
        within = detail[i] if i < len(detail) else []
        entry: Dict[str, Any] = {
            "bar": slot.bar_start + i,
            "roman": roman,
            "tones": _tones(roman),
        }
        if len(within) > 1:
            # Beat positions the harmony moves through inside this bar. The
            # placement used to be `beats // len(within)`, which for five chords
            # in a four-beat bar gave a step of 1 and put a chord on "beat 5".
            entry["within"] = [
                {"beat": b, "roman": r, "tones": _tones(r)}
                for b, r in zip(_spread_beats(beats, len(within)), within, strict=True)
            ]
        out.append(entry)
    return out


def _beat_count(meter) -> int:
    """Heard beats per bar (6/8 has two, not six)."""
    try:
        num, den = int(meter[0]), int(meter[1])
    except (TypeError, ValueError, IndexError):
        return 4
    if den == 8 and num in (6, 9, 12):
        return num // 3
    return max(1, num)


def _spread_beats(beats: int, n: int) -> List:
    """``n`` positions spread evenly across ``beats`` beats, 1-based.

    Three chords in a four-beat bar sit on 1, 2.5 and 4 — not 1, 2, 3 with a
    silent fourth beat, and never past the barline.
    """
    if n <= 1:
        return [1]
    if n >= beats:
        return [1 + i for i in range(min(n, beats))] + [beats] * max(0, n - beats)
    step = (beats - 1) / (n - 1)
    return [round(1 + i * step, 2) for i in range(n)]


def _theme_block(graph, slot) -> Dict[str, str]:
    """The agent's own composed theme + a suggested development for this section
    (so the theme recurs as REAL material, transformed — not re-invented)."""
    th = getattr(graph, "principal_theme_surface", None)
    if not th or not getattr(th, "principal_line", None):
        return {}
    from .theme_planner import develop_theme_surface

    return_ops = {
        "recap": "state",
        "return": "state",
        "reprise": "state",
        "coda": "augment",
        "a2": "vary",
    }
    role = " ".join(
        str(getattr(slot, attr, "") or "") for attr in ("function", "section_id", "dramatic_role")
    ).lower()
    op = "state"
    for token, chosen in return_ops.items():
        if token in role:
            op = chosen
            break
    else:
        if any(x in role for x in ("develop", "contrast", "episode", "_b", "transition")):
            op = "fragment"
        elif any(x in role for x in ("climax", "peak", "culminat")):
            # The peak of the piece is where a theme is TRANSFORMED, not restated
            # unchanged. The old mapping had no climax case at all, so the brief
            # for the climax of the piece said "this section calls for: STATE".
            op = "augment"
        elif "continuation" in role or "consequent" in role:
            op = "vary"
    semis = _theme_transpose_semitones(th, slot)
    statement = develop_theme_surface(th, "state")
    suggested = develop_theme_surface(th, op, semis)
    if suggested == statement and semis:
        suggested = develop_theme_surface(th, "state", semis)
    return {
        "statement": statement,
        "op": op,
        "suggested": suggested,
        "transposed": bool(semis),
    }


def _theme_transpose_semitones(theme, slot) -> int:
    """Nearest-octave transposition from the theme's key to this phrase's key."""
    from .pitch import key_to_root_midi

    try:
        semis = key_to_root_midi(getattr(slot, "key", "C")) - key_to_root_midi(
            getattr(theme, "key", "C")
        )
    except (TypeError, ValueError):
        return 0
    return ((semis + 6) % 12) - 6


_DRAMATIC_ROLE_BRIEF = {
    "establish": "ESTABLISH: state the material plainly and memorably. Everything "
    "later refers back to this, so it has to be worth referring to.",
    "extend": "EXTEND: continue what was just said without restating it — spin the "
    "line forward, keep the same character, go somewhere new inside it.",
    "depart": "DEPART: leave home. Change key, register or texture so the listener "
    "feels the ground move.",
    "intensify": "INTENSIFY: raise the pressure — denser, higher, harmonically "
    "sharper than what came before. This is a build, not a plateau.",
    "crisis": "CRISIS: the point of maximum instability. Let it hurt — dissonance, "
    "register extremes, rhythmic disruption.",
    "retreat": "RETREAT: subside. Thin the texture, fall in register, let the "
    "energy drain away after what just happened.",
    "return": "RETURN: the material comes back — but a literal repeat is dead on "
    "arrival. It must be changed by everything that happened in between.",
    "confirm": "CONFIRM: settle the key. Cadential, stable, no new departures.",
    "close": "CLOSE: end it. The last gesture has to sound final, not merely stopped.",
}


_DEGREE_NAMES = ("1", "b2", "2", "b3", "3", "4", "#4", "5", "b6", "6", "b7", "7")


def _motif_brief(graph, slot) -> List[Dict[str, Any]]:
    """The motifs this phrase is supposed to carry, with their identity.

    ``/w-plan`` spends a whole step designing MotifObjects — character, scale-degree
    contour, interval contour, rhythm cell, recognition anchor — ``resolve_motifs``
    stores them in ``graph.motif_bank``, and ``theme_planner`` writes per-phrase
    ``motif_transforms`` onto the slot. None of it appeared in the brief. The agent
    composing the notes was never shown the piece's own designed identity, which is
    why pieces came out as a run of individually-plausible phrases with nothing
    recurring through them.
    """
    # The bank is a {motif_id: MotifObject} dict on the graph; accept a list too
    # so this never silently returns nothing if that shape ever changes.
    bank = getattr(graph, "motif_bank", None) or {}
    if isinstance(bank, dict):
        motifs = list(bank.values())
    else:
        motifs = list(getattr(bank, "motifs", None) or bank or [])
    if not motifs:
        return []
    by_id = {getattr(m, "motif_id", "") or "": m for m in motifs}

    # What this phrase was PLANNED to do with which motif; otherwise the piece's
    # principal motif, stated.
    wanted: List[Tuple[str, str]] = []
    for mt in getattr(slot, "motif_transforms", None) or []:
        # A MotifTransform is (operation, params) — the motif id lives in
        # params["motif_id"]. Reading `mt.motif_id` and `mt.transform` found
        # neither, so even a phrase WITH a planned placement showed no motif.
        if isinstance(mt, dict):
            params = mt.get("params") or {}
            mid = params.get("motif_id") or mt.get("motif_id") or ""
            op = mt.get("operation") or mt.get("transform") or ""
        else:
            params = getattr(mt, "params", None) or {}
            mid = params.get("motif_id") or getattr(mt, "motif_id", "") or ""
            op = getattr(mt, "operation", "") or getattr(mt, "transform", "") or ""
        if mid:
            wanted.append((mid, op or "state"))
    if not wanted:
        principal = getattr(graph, "principal_theme_id", "") or ""
        if principal not in by_id:
            # The principal is elected while the form is built, so a motif bank
            # written afterwards has no elected principal. Falling back to
            # nothing meant the brief showed no motif at all.
            principal = getattr(motifs[0], "motif_id", "") or ""
        if principal:
            wanted.append((principal, "state"))

    out: List[Dict[str, Any]] = []
    seen: set = set()
    for mid, op in wanted:
        m = by_id.get(mid)
        if m is None or mid in seen:
            continue
        seen.add(mid)
        degrees = [
            _DEGREE_NAMES[d % 12] if isinstance(d, int) and d > 11 else str(d)
            for d in (getattr(m, "scale_degree_contour", None) or [])
        ]
        anchor_d = getattr(m, "recognition_anchor", None) or {}
        out.append(
            {
                "id": mid,
                "transform": op,
                "character": getattr(m, "character", "") or "",
                "degrees": " ".join(degrees),
                "intervals": " ".join(str(i) for i in (getattr(m, "interval_contour", None) or [])),
                "rhythm": " ".join(getattr(m, "rhythm_cell", None) or []),
                "anchor": ", ".join(f"{k}={v}" for k, v in anchor_d.items() if v),
                "allowed": ", ".join(getattr(m, "allowed_transforms", None) or []),
            }
        )
    return out[:3]


def _register_target(graph, slot) -> List[str]:
    """Where this phrase's melody should LIVE, in actual pitches.

    The brief already carried a register arc, and it looked like this:

        register arc: [0.67, 1.0, 0.0]

    Three abstract numbers. Nothing anywhere told the composer how high "1.0"
    was in pitches, so nothing acted on it, and the result is measurable: the
    last generated andante kept its melody inside **19 semitones across 41
    bars** while the 26 canonical movements in the reference corpus span **24 to
    49 (median 32.5)**. It was narrower than any real movement measured, and
    every phrase of it was locally reasonable — the ceiling was never set
    anywhere, so nobody ever reached for it.

    This converts the arc into instructions a composer can act on: the range the
    piece has actually used so far, and a concrete ceiling for this phrase given
    where it sits in the arc. Suggestions, not constraints — nothing enforces
    them, and a phrase with a reason to sit low should sit low.
    """
    from .pitch import midi_to_pitch

    key = getattr(slot, "key", "C") or "C"
    used: List[int] = []
    # Scoped to this movement, like the other "so far" reports: a slow
    # movement judged against the allegro's register has the wrong ceiling and
    # the wrong floor. (This was the fourth of the four sections in Addendum 66
    # and the one I named but did not fix in the same pass.)
    for ps in _phrases_in_scope(graph, getattr(slot, "section_id", "") or ""):
        layer = getattr(ps, "realized", None)
        if layer is None or not getattr(ps, "agent_authored", False):
            continue
        for ev in getattr(layer, "principal_line", None) or []:
            m = pitch_to_midi(getattr(ev, "pitch", None))
            if m is not None:
                used.append(m)

    out: List[str] = []
    curve = list(getattr(getattr(slot, "curves", None), "register", []) or [])
    peak = max(curve) if curve else None
    dist = getattr(slot, "climax_distance", None)

    if used:
        lo, hi = min(used), max(used)
        span = hi - lo
        out.append(
            f"RANGE SO FAR: the melody has used {midi_to_pitch(lo, key)}-"
            f"{midi_to_pitch(hi, key)} ({span} semitones). Real movements span "
            f"24-49 (median 32.5)."
        )
        if span < 24:
            need = 24 - span
            out.append(
                f"  The piece is {need} semitone(s) narrower than the narrowest "
                f"canonical movement measured. Unless this phrase has a reason to "
                f"stay put, take it somewhere the piece has not been — above "
                f"{midi_to_pitch(hi, key)} or below {midi_to_pitch(lo, key)}."
            )
        # A climax that does not out-reach what came before is not a climax.
        if dist == 0:
            out.append(
                f"  This is the climax: its melodic peak should sit ABOVE "
                f"{midi_to_pitch(hi, key)}, the highest note the piece has "
                f"reached so far."
            )
        elif isinstance(dist, int) and dist < 0 and peak is not None and peak >= 0.95:
            out.append(
                "  This phrase carries the local high point, but the piece's "
                "climax is still ahead — leave headroom above it."
            )
    elif peak is not None:
        out.append(
            "RANGE: nothing committed yet, so this phrase sets the piece's "
            "opening register. Start below where you intend to peak — a melody "
            "that opens at its ceiling has nowhere to go."
        )
    return out


def _coverage_note(composer: str) -> Dict[str, Any]:
    """How much real music stands behind this brief, in one line.

    `composer_coverage_tier` has always known this; nothing put it in front of
    the agent. Corelli, Handel, Schubert and Weber are all "armed" and all
    report tier C, on 19, 54, 82 and 241 bars respectively — against Mozart's
    7,022. An exemplar drawn from 19 bars is not weak evidence of a style, it is
    a single page of one piece, and the agent should know that before it decides
    how much weight to give it.
    """
    try:
        rep = composer_coverage_tier(composer)
    except Exception:
        return {}
    tier = rep.get("tier")
    bars = rep.get("bars") or 0
    advice = {
        "A": "richly armed — the exemplars are representative; follow them closely.",
        "B": "armed — the exemplars are real but the sample is small; treat them "
        "as evidence, not as the whole style.",
        "C": "THIN CORPUS. There is very little real music behind this brief, so "
        "the exemplars are a sample of one or two pieces rather than of a style. "
        "Lean on the written doctrine and your own study of the scores, and do "
        "not read a statistic drawn from this few bars as a target.",
        "D": "UNARMED — there is no corpus for this composer at all.",
    }.get(tier, "")
    return {"tier": tier, "bars": bars, "advice": advice}


def _movement_brief(graph, slot) -> List[str]:
    """Which movement this phrase belongs to, and what that movement is for."""
    if graph is None or slot is None:
        return []
    work = getattr(graph, "work_graph", None)
    movements = list(getattr(work, "movements", None) or []) if work else []
    if len(movements) < 2:
        return []  # a single-movement piece needs no orientation
    section = getattr(slot, "section_id", "") or ""
    mid = section.split("_", 1)[0]
    mv = next((m for m in movements if getattr(m, "id", "") == mid), None)
    if mv is None:
        return []
    ordinal = movements.index(mv) + 1
    bits = [f"MOVEMENT {ordinal} of {len(movements)}"]
    for label, value in (
        ("its role in the work", getattr(mv, "role_in_work", "")),
        ("character", getattr(mv, "character", "")),
        ("marking", getattr(mv, "tempo_marking", "")),
    ):
        value = (value or "").strip()
        if value:
            bits.append(f"{label}: {value}")
    lines = [" — ".join(bits)] if len(bits) > 1 else []

    # The WORK's plan, which `init_work` stores and nothing has ever read:
    # `emotional_narrative`, `finale_payoff` and `home_key` are all written and
    # never surfaced. The home key even carries a comment about the bug where a
    # G major sonatina recorded "C" — "and every later question about where the
    # work lives got the wrong answer" — except there is no later question,
    # because no reader exists. A movement composed without the work's arc is a
    # piece that happens to be third in a folder.
    narrative = (getattr(work, "emotional_narrative", "") or "").strip()
    if narrative:
        lines.append(f"THE WHOLE WORK: {narrative}")
    home = (getattr(getattr(work, "tonal_itinerary", None), "home_key", "") or "").strip()
    if home and home != (getattr(mv, "key", "") or ""):
        lines.append(
            f"  (the work's home key is {home}; this movement is in "
            f"{getattr(mv, 'key', '?')} — the distance is part of the plan)"
        )
    # The payoff belongs to the movement that has to deliver it.
    payoff = (getattr(work, "finale_payoff", "") or "").strip()
    if payoff and ordinal == len(movements):
        lines.append(f"THIS MOVEMENT MUST PAY OFF: {payoff}")
    return lines


def _dramatic_brief(slot, graph=None) -> List[str]:
    """Why this phrase exists — its role in the piece's arc, in plain language.

    A phrase used to know its cadence and its bar count and nothing about why it
    exists, so every one came out locally optimal and the piece had no arc.
    """
    # The ROLE's intent is NOT repeated here: CREATIVE INTENT already prints it,
    # from ``dramatic_plan.ROLE_INTENT``. A second, differently-worded copy of the
    # same instruction in the same brief is how two versions of one rule drift
    # apart and begin contradicting each other.
    out: List[str] = []
    # Sign convention: NEGATIVE is before the climax, positive is after (the
    # planner counts m1_a_p1 as -4 and the coda as +4). Reading it the other way
    # told the opening phrase of the piece that it was four phrases PAST the peak
    # and must not re-peak.
    dist = getattr(slot, "climax_distance", None)
    # `climax_distance` defaults to 0 and 0 MEANS "this is the climax", so a
    # phrase the dramatic planner never touched claims the peak of the piece.
    # Measured across the workspace: nine pieces in which **every** phrase was
    # told it was the climax — 9 of 9 phrases in the F major andante, 56 of 56
    # in the seasons sonata. A piece whose every phrase is written as the
    # highest, densest, most charged moment has no arc at all, which is the
    # complaint the dramatic planner exists to answer.
    #
    # The planner always assigns a role alongside the distance, so an empty role
    # is the reliable signal that no plan ran. Say nothing rather than something
    # false: a phrase with no plan should be told it has no plan.
    # WHICH MOVEMENT this is, and what that movement is for. `plan_movement`
    # stores `role_in_work`, `character` and `tempo_marking` on a
    # MovementContract and **nothing has ever read any of them**: a phrase in the
    # slow movement of a symphony got a brief indistinguishable in kind from one
    # in the opening allegro. For a multi-movement work that is the largest piece
    # of context there is, and it was sitting on the graph unused.
    out += _movement_brief(graph, slot)

    # An absent ARC does not make the rest of the plan absent. This branch used
    # to `return` immediately, and every later addition — forward context, then
    # section goals — silently vanished for an unplanned phrase until a test
    # caught it. Say the arc is missing and carry on, rather than treating one
    # missing field as "no plan at all".
    planned = bool(getattr(slot, "dramatic_role", ""))
    if not planned:
        out.append(
            "WHERE YOU ARE: this phrase has no dramatic plan — nothing has "
            "decided where the piece peaks or where this sits relative to it. "
            "Do not assume this is the climax. Judge the shape from the "
            "surrounding music and the form, and leave somewhere to go."
        )
    # In a multi-movement work "the whole piece" is a lie told three times: the
    # dramatic plan runs per movement, so a three-movement sonatina produced
    # THREE phrases each told they were the peak of everything, with two more
    # movements still to come after the first of them. Scope the claim to what
    # is actually true — the movement — and say where the work's own peak is
    # decided, which is nowhere yet (`WorkGraph.climax_reservations` exists and
    # nothing fills it, Addendum 59).
    n_movements = len(getattr(getattr(graph, "work_graph", None), "movements", None) or [])
    scope = "whole piece" if n_movements < 2 else "MOVEMENT"
    if planned and isinstance(dist, int):
        if dist == 0:
            out.append(
                f"WHERE YOU ARE: this is the CLIMAX of the {scope}. Everything "
                "before has been building to it and everything after subsides from "
                "it. It must be the highest, densest, most harmonically charged "
                "moment — and it must cost something. Do not write another good "
                "phrase here; write the peak."
                + (
                    " (Each movement has its own peak; which of them is the WORK's "
                    "apex is not recorded anywhere, so judge it from the work's arc "
                    "above.)"
                    if n_movements >= 2
                    else ""
                )
            )
        elif dist < 0:
            out.append(
                f"WHERE YOU ARE: {abs(dist)} phrase(s) before "
                f"{'this movement' if n_movements >= 2 else 'the piece'}'s climax — "
                f"still climbing. Leave somewhere higher to go; do not spend the "
                f"peak here."
            )
        else:
            out.append(
                f"WHERE YOU ARE: {dist} phrase(s) past the climax — the music is "
                f"coming down. Do not re-peak."
            )
    strategy = (getattr(slot, "return_strategy", "") or "").strip()
    if strategy:
        detail = (getattr(slot, "return_strategy_detail", "") or "").strip()
        out.append(f"THE RETURN MUST DIFFER BY: {strategy}" + (f" — {detail}" if detail else ""))
    entry = (getattr(slot, "metric_entry", "") or "").strip().lower()
    if entry == "anacrusis":
        out.append(
            "METRIC ENTRY: this phrase begins with an UPBEAT, not on the downbeat. "
            "Mark the first bar dict 'pickup': True and write only the upbeat in it "
            "— it right-aligns to the barline and engraves as a real partial "
            "measure. The pickup OCCUPIES that bar, so `bars` still has exactly "
            "bar_count dicts."
        )
    elif entry == "downbeat":
        out.append("METRIC ENTRY: this phrase begins on the downbeat.")
    motion = (getattr(slot, "key_motion", "") or "").strip()
    if motion:
        pivot = (getattr(slot, "pivot_hint", "") or "").strip()
        out.append(f"KEY MOTION: {motion}" + (f" (pivot tones: {pivot})" if pivot else ""))
    # The section's technique list belongs to the whole section, and dumping all
    # of it on every phrase produced eleven lines that contradict each other
    # ("one accompaniment character" next to "added inner voice", "clear periodic
    # phrasing" next to "fragmentation of the head motif"). Give the phrase the
    # slice that is its turn.
    # The GOAL before the technique: a technique with no goal is a recipe, and
    # the composer was getting only the recipe. Goals are few and do not
    # contradict each other the way a unioned technique list does, so they are
    # given whole.
    goals = [g for g in (getattr(slot, "section_goals", None) or []) if g]
    if goals:
        out.append(f"WHAT THIS SECTION IS FOR: {'; '.join(goals[:3])}")
    techs = [t for t in (getattr(slot, "section_techniques", None) or []) if t]
    if techs:
        idx = max(0, int(getattr(slot, "bar_start", 1)) - 1) // max(
            1, int(getattr(slot, "bar_count", 4) or 4)
        )
        picked = [techs[(idx * 2 + k) % len(techs)] for k in range(min(2, len(techs)))]
        seen: set = set()
        for tech in picked:
            if tech not in seen:
                seen.add(tech)
                out.append(f"TECHNIQUE to reach for here: {tech}")
    notes = (getattr(slot, "notes", "") or "").strip()
    if notes:
        out.append(f"CHARACTER: {notes}")
    # Where this phrase is GOING. `dramatic_plan.link_forward_context` was
    # written because "forward_context existed on the model and was never
    # populated, so no phrase knew what it was leading into" — it populates the
    # field, `test_every_phrase_knows_what_follows_it` asserts it is populated,
    # and **nothing ever read it**. The composer got TRANSITION IN (where the
    # phrase comes from) and nothing about where it goes, which is precisely the
    # information that stops a phrase being a well-formed dead end.
    forward = (getattr(slot, "forward_context", "") or "").strip()
    if forward:
        out.append(f"WHERE IT GOES NEXT: {forward}")
    if graph is not None:
        try:
            out += _register_target(graph, slot)
        except Exception:
            pass  # a missing register hint must never cost the brief
    return out


def _character_is_role_derived(character: str, gesture: str = "") -> bool:
    """Is this section 'character' the agent's prose, or the planner's default?

    `build_form_graph` fills `NarrativeSection.character` with
    `"; ".join(ROLE_INTENT[r] for r in roles)` — pure role text. So the field
    `_creative_intent` treats as "the agent's OWN authored prose" is, unless
    someone called `save_narrative`, a bucket label wearing prose clothes.
    Measured: a Chopin nocturne and a Mozart andante carry **byte-identical**
    character on all five sections.

    That matters because CREATIVE INTENT is the one section the phrase-composer
    is told to start from — "the feeling that should choose the notes ... the
    intent is the goal". Boilerplate presented as the piece's identity is worse
    than an empty field, which would at least prompt for one.

    Detected by RECONSTRUCTION rather than a flag, because the graphs already on
    disk have no flag. `build_form_graph` writes the pair together —

        character = "; ".join(ROLE_INTENT[r] for r in roles)
        gesture   = " then ".join(roles)

    — so the roles can be read back out of `gesture` and the expected character
    rebuilt exactly. (Splitting `character` on ";" does not work: several
    ROLE_INTENT values contain a semicolon of their own, which is what made the
    first version of this check silently return False for every real piece.)
    """
    text = (character or "").strip()
    if not text:
        return False
    try:
        from .dramatic_plan import ROLE_INTENT
    except Exception:  # pragma: no cover - defensive
        return False
    roles = [r.strip() for r in (gesture or "").split(" then ") if r.strip()]
    if roles:
        rebuilt = "; ".join(dict.fromkeys((ROLE_INTENT.get(r) or "").strip() for r in roles))
        if rebuilt.strip("; ") == text:
            return True
    # No gesture to reconstruct from: fall back to "is it exactly one known intent".
    return text in {(v or "").strip() for v in ROLE_INTENT.values() if v}


def _creative_intent(graph, slot) -> str:
    """The FEELING this moment must convey — human-composer terms, from the
    narrative arc + phrase function (NOT analytics).

    Leads with the agent's OWN authored prose (section.character / .gesture,
    written at plan time) — the dramatic event that drives the notes. The
    curve-derived adjectives are a terse fallback/suffix only, never the
    primary intent. (Authoring beats bucketing.)"""
    parts: List[str] = []
    # THIS PHRASE's own intent comes first. The narrative section's `character`
    # is the whole section's — for a three-phrase A section it is the three role
    # intents joined with semicolons, so every phrase in it was told to "state the
    # idea plainly AND carry it further AND settle the key beyond doubt AND drive
    # the structural cadence" at once. A phrase asked to do four contradictory
    # things does none of them.
    own_role = (getattr(slot, "dramatic_role", "") or "").strip()
    section_character = ""
    nar = getattr(graph, "narrative", None)
    sec = None
    if nar and getattr(nar, "sections", None):
        sec = _narrative_section_for(graph, slot)
    if own_role:
        try:
            from .dramatic_plan import ROLE_INTENT

            intent = (ROLE_INTENT.get(own_role) or "").strip()
        except Exception:
            intent = ""
        if intent:
            parts.append(intent)
    if sec:
        character = (getattr(sec, "character", "") or "").strip()
        gesture = (getattr(sec, "gesture", "") or "").strip()
        # Role-derived text is not authored intent, and must not be presented as
        # it: the phrase-composer is told to start from this line. When that is
        # all there is, say so and hand over the one thing that IS specific to
        # this piece — the request it was written from — rather than letting a
        # form-shaped default stand in for the piece's identity.
        if _character_is_role_derived(character, gesture):
            character = ""
            described = ""
            contract = getattr(graph, "contract", None)
            if contract is not None:
                described = (getattr(contract, "description", "") or "").strip()
            if described:
                parts.append(
                    f"(no piece-specific intent was written for this section — "
                    f"the role default above is generic to the form. What this "
                    f"piece IS: \u201c{described}\u201d. Decide from that what this "
                    f"moment has to feel like.)"
                )
        section_character = character
        if character and not parts:
            parts.append(character)
        elif character and own_role:
            # Keep the section's shape as CONTEXT, clearly marked as such.
            parts.append(f"(this section overall: {gesture or character})")
        elif gesture:
            parts.append(f"gesture: {gesture}")
        # Curve-derived mood — a terse cue only, and only when no prose was
        # authored, so it never dilutes a real authored intent.
        if not section_character and not parts:
            if sec.label:
                parts.append(sec.label)

            def avg(c):
                return sum(c) / len(c) if c else 0.5

            e, t, br = avg(sec.energy_curve), avg(sec.tension_curve), avg(sec.brightness_curve)
            mood = ["intense" if e > 0.66 else "gentle" if e < 0.4 else "flowing"]
            if t > 0.6:
                mood.append("yearning/tense")
            if br > 0.6:
                mood.append("luminous")
            elif br < 0.4:
                mood.append("shadowed")
            parts.append(", ".join(mood))
        if sec.climax_type == "primary":
            parts.append("THE emotional peak of the piece")
    fn = getattr(slot, "function", "")
    return f"{fn} — " + " · ".join(p for p in parts if p) if parts else fn


def _reference_study_lines(graph, composer: str) -> List[Dict[str, str]]:
    """The agent's own whole-score analyses, surfaced for this composer/style.

    Pulls from graph.reference_studies (written at plan time by
    save_reference_study). Scoped to the resolved composer (or, for a style id,
    its member composers) so a phrase composes from the agent's understanding of
    real scores — not just from retrieved exemplar bars.
    """
    studies = getattr(graph, "reference_studies", None)
    if not isinstance(studies, dict) or not studies:
        return []
    members = set(_aggregate_members(composer) or [])
    members.add(composer)
    out: List[Dict[str, str]] = []
    for entry in studies.values():
        if not isinstance(entry, dict):
            continue
        comp = entry.get("composer", "")
        if comp and members and comp not in members:
            continue
        analysis = entry.get("analysis", "")
        if analysis:
            out.append({"source": entry.get("source", "?"), "analysis": analysis})
    return out


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

    # Structurally pivotal phrases see more real corpus material — the most
    # important moments deserve the widest exemplar window (token-bounded).
    eff_exemplars = n_exemplars
    if _is_structural_phrase(graph, slot):
        eff_exemplars = max(n_exemplars, 14)

    try:
        _locks = render_lock_contract(graph, state.slot)
    except Exception:
        _locks = []
    brief = CompositionBrief(
        lock_contract=_locks,
        phrase_id=phrase_id,
        composer=resolved,
        slot_summary=_summarize_slot(slot),
        sketch_summary=_summarize_sketch(state.sketch),
        ledger_state=_ledger_lines(graph, phrase_id),
        ledger_constraints=_ledger_constraints(graph, phrase_id),
        transition=transition,
        exemplars=_retrieve_exemplars(resolved, slot, eff_exemplars, warnings),
        target_stats=_build_target_stats(resolved, slot, warnings),
        # WS-A: multi-level corpus patterns
        phrase_shape=_phrase_shape(resolved, slot, role),
        cadence_exemplars=_cadence_exemplars(resolved, slot),
        transition_patterns=_transition_patterns(resolved, slot, transition.get("exit_lh_texture")),
        lh_vocabulary=_lh_vocabulary(resolved, slot, key),
        gestures=_gestures(resolved, slot),
        corpus_gestures=_corpus_gestures(resolved, slot),
        # WS-C: written rules / doctrine, scoped to this phrase
        fingerprints=_fingerprints(resolved),
        doctrine=_doctrine_slices(resolved, slot, role),
        anti_patterns=_anti_pattern_tells(resolved),
        creative_intent=_creative_intent(graph, slot),
        feeling_text=_feeling_text(graph, slot),
        dramatic=_dramatic_brief(slot, graph),
        motifs=_motif_brief(graph, slot),
        chord_frame=_chord_frame(slot, key),
        theme_block=_theme_block(graph, slot),
        reference_study=_reference_study_lines(graph, resolved),
        coverage=_coverage_note(resolved),
        warnings=warnings,
    )
    # Say it when a section of the brief is empty. A composer can be armed by
    # corpus and still have NO written doctrine (palestrina, monteverdi, corelli
    # and weber have bar records but no profile directory at all), and the
    # renderer simply omits an empty section — so the phrase composer could not
    # tell "this composer has no fingerprints" from "I skipped that part".
    if not brief.fingerprints:
        warnings.append(
            f"no composer fingerprints for '{resolved}' — there is no written "
            f"profile for it, so the brief cannot say what makes this voice "
            f"recognizable. Compose from the exemplars and your own score study."
        )
    if not brief.doctrine:
        warnings.append(f"no style doctrine for '{resolved}' (cadence/ornament/colour)")
    if not brief.reference_study:
        warnings.append(
            "no reference study saved for this piece — run save_reference_study "
            "at plan time so composition works from whole scores, not only bars"
        )
    return brief


_MINDSET = (
    "HOW TO COMPOSE (think like a human composer, not an analyzer):\n"
    "  • Start from the FEELING this moment must convey (see CREATIVE INTENT) — "
    "let the emotion choose the notes.\n"
    "  • Imagine and SING the melodic line in your head; write what sings, not "
    "what fills bars.\n"
    "  • Think in GESTURES and CHARACTER — a yearning rise, a stormy surge, a "
    "tender sigh, a question and its answer — not in note counts.\n"
    "  • Shape DRAMATIC TIMING — where the music breathes, builds, breaks, and "
    "resolves. Silence and a long note are expressive choices.\n"
    "  • Use the reference material as a real composer uses their training: you "
    "may INVENT freely, or QUOTE / ADAPT / DEVELOP a passage below — your choice "
    "per moment. Never copy verbatim; make it yours.\n"
    "  • The corpus stats and the 'musical ear' are GUARDRAILS that catch "
    "mistakes (clashes, a buried tune, monotony) — they are NOT the goal. Never "
    "compose to hit a number. The STYLE TARGETS below are a reality check on "
    "the finished phrase, not a specification to satisfy: a phrase that sings "
    "and sits outside a band is better than one that hits every band and does "
    "not.\n"
    "\n"
    "CRAFT THE HUMAN ELEMENTS (the difference between notes and music — use the "
    "shorthand fully; copy the IDIOMS, not the pitches, from the exemplars):\n"
    "  • METRIC ENTRY: not every phrase starts on a downbeat — the plan says "
    "which this one is, under WHY THIS PHRASE EXISTS, with the mechanics.\n"
    "  • INNER VOICES: write genuine two-voice-per-hand polyphony with '//' — a "
    'sustained melody over a moving inner line, e.g. rh="Ab5h. Gb5q // Db5e Eb5e '
    "F5e Gb5e\". The '//' separates simultaneous voices in ONE hand. Use it; do "
    "not reduce everything to block chords.\n"
    "  • RHYTHM that breathes: vary it like a human — dotted figures, ties across "
    "beats, triplets, syncopation, agogic long notes. Avoid wall-to-wall even "
    "eighths; let the rhythm phrase. Triplets are written trip_q/trip_e/trip_s "
    "(three trip_e fill one beat) and 32nds/64ths are t/x — all of them engrave "
    "correctly, so the fine rhythm you hear is the rhythm you can write.\n"
    "  • ORNAMENTS with intent: place :tr :turn :mord :grace where the line "
    "yearns or arrives (an appoggiatura into a strong beat, a turn at a peak, a "
    "trill at a cadence) — as the exemplars do, not decoratively.\n"
    "  • IDIOMATIC PATTERNS: figuration must TRACK the harmony (follow the chord "
    "frame through its inversions) and the phrase (denser into a climax, thinning "
    "at a cadence) — never a fixed pattern stamped on every bar.\n"
    "\n"
    "WRITE THE MARKS WITH THE NOTES — five things that are easy to leave out "
    "and audible when they are missing (the ranges are measured over 26 "
    "canonical Mozart / Beethoven / Chopin movements; what THIS piece has "
    "actually used so far is reported under MARKS SO FAR):\n"
    "  • ARTICULATE. Real movements carry 0.11-5.71 notation marks per bar "
    "(median 1.58). Slur the sighing pairs, detach the accompaniment where it should be "
    "light, put a tenuto on the note that has to be leaned on: "
    ":stacc :stacciss :port :acc :ten :marc, and '( ... )' for a slur.\n"
    "  • TIE ACROSS BARLINES. Real keyboard scores tie a median 0.35 times per "
    "bar (p25 0.06); a score with none has every bar sealed off from the next. "
    "Write C5h~ at the end of one bar and C5h at "
    "the start of the next — a melody leaning into the next bar, a suspension "
    "resolving late, a pedal bass held through a phrase joint.\n"
    "  • VARY THE CADENCE. Closing every phrase with the same rhythm leaves the "
    "form no punctuation, only a repeating full stop. Land one on a weak beat, elide one into the next "
    "entry, tie one over the barline, decorate one with an appoggiatura, cut one "
    "short. Save the plainest, strongest close for the moment that needs it.\n"
    "  • DON'T WALK SCALES. Plain unbroken stepwise runs are 0-15% of melody "
    "bars in real movements (median 2%). A "
    "scale connects two ideas — it is not one. Break a run with a leap and a "
    "gap-fill, turn it back on itself, or give it a rhythmic profile.\n"
    "  • USE THE WHOLE KEYBOARD. Real movements span 24-49 semitones in the "
    "melody (median 32.5) — a narrower span means nothing ever sounds high or "
    "low relative to anything else. See RANGE SO FAR below for where "
    "this piece has actually been. Open below where you intend to peak, take a "
    "return an octave up, drop to the tenor for the darkest phrase.\n"
    "Also available: :arp (the rolled chord — the most "
    "characteristic piano notation there is), :acci / :appo (crushed vs accented "
    "grace), :ped, :8va, and character text (:dolce :cantabile :leggiero "
    ":sotto_voce :agitato …). A bar dict also takes 'art', 'text' and 'ped'."
)


#: `_MINDSET` is written for a pianist, because for a long time every piece was
#: one. A choir cannot roll a chord, has no hands to put two voices in, and does
#: not have a keyboard to use the whole of. These are the phrases that say
#: something false to anyone writing for voices or an ensemble; the craft advice
#: they carry is sound, so it is reworded rather than removed.
_KEYBOARD_PHRASINGS = (
    ("two-voice-per-hand polyphony", "two independent voices per staff"),
    ("simultaneous voices in ONE hand", "simultaneous voices on ONE staff"),
    ("USE THE WHOLE KEYBOARD", "USE THE WHOLE RANGE"),
    (
        ":arp (the rolled chord — the most characteristic piano notation there is)",
        ":arp (the rolled chord — for instruments that can roll one)",
    ),
)

#: The shorthand keys do not change with the forces: a bar dict is always
#: `{'rh': ..., 'lh': ...}`. Saying UPPER/LOWER everywhere else and leaving this
#: unsaid would be the contradiction the brief is supposed to avoid.
_STAFF_KEY_NOTE = (
    "\n  • THE BAR DICT KEYS STAY 'rh' AND 'lh'. For this piece they mean the "
    "UPPER and LOWER staff, not two hands — 'rh' carries the upper voices, 'lh' "
    "the lower, and '//' separates two voices sharing one staff.\n"
)


def mindset_for(keyboard: bool) -> str:
    """`_MINDSET`, in language that is true for this piece's forces."""
    if keyboard:
        return _MINDSET
    text = _MINDSET
    for phrase, replacement in _KEYBOARD_PHRASINGS:
        text = text.replace(phrase, replacement)
    return text + _STAFF_KEY_NOTE


def marks_so_far(graph, movement_id: str = "") -> Dict[str, int]:
    """What the composer has actually written into THIS piece up to now.

    The brief used to assert, in its most emphatic section, that the system had
    "measurably never" articulated, tied, pedalled or rolled a chord — frozen
    numbers from one score in one session. Measured against the very piece whose
    brief said it: 19 articulations, 2 ties, 82 pedal marks and 4 rolled chords.
    Four falsehoods, stated with numbers, in the section the composer is most
    likely to act on. A brief that is wrong about the piece in front of it
    spends the credibility of everything true around it.
    """
    counts = {k: 0 for k in ("articulation", "tie", "slur", "pedal", "arpeggio", "ornament")}
    for state in _phrases_in_scope(graph, movement_id):
        layer = getattr(state, "realized", None)
        if layer is None:
            continue
        for name in (
            "principal_line",
            "bass_foundation",
            "response_layer",
            "counter_reply",
            "ornamental_surface",
            "inner_voices",
        ):
            for e in getattr(layer, name, None) or []:
                if getattr(e, "articulation", None):
                    counts["articulation"] += 1
                if getattr(e, "tie", None):
                    counts["tie"] += 1
                if getattr(e, "slur", None):
                    counts["slur"] += 1
                if getattr(e, "pedal", None):
                    counts["pedal"] += 1
                if str(getattr(e, "technique", "") or "").startswith("arpeggio"):
                    counts["arpeggio"] += 1
                if getattr(e, "ornament", None):
                    counts["ornament"] += 1
    return counts


def render_marks_so_far(graph, movement_id: str = "") -> List[str]:
    """The live version of what the frozen claims used to assert.

    ``movement_id`` scopes the count to one movement; without it, every phrase
    in the graph counts.
    """
    counts = marks_so_far(graph, movement_id)
    bars = 0
    for state in _phrases_in_scope(graph, movement_id):
        st_slot = getattr(state, "slot", None)
        if st_slot is not None and getattr(state, "realized", None) is not None:
            bars += int(getattr(st_slot, "bar_count", 0) or 0)
    if not bars:
        return [
            "MARKS SO FAR: nothing committed yet — this is the first phrase, so "
            "every mark in the piece is one you are about to write.",
        ]
    missing = [k for k, v in counts.items() if v == 0]
    body = ", ".join(f"{k} {v}" for k, v in counts.items())
    line = f"MARKS SO FAR ({bars} committed bars): {body}."
    if missing:
        line += (
            f" Nothing in this piece has used: {', '.join(sorted(missing))} — "
            f"if that is deliberate, fine; if it is drift, this is where it shows."
        )
    return [line]


def render_text(brief: CompositionBrief, graph=None) -> str:
    """Compact, note-complete text rendering of a brief for the agent.

    ``graph`` lets the marks report be measured from the piece instead of
    asserted from a constant; without it that section is simply omitted, which
    is better than printing a frozen claim about a different piece.
    """
    s = brief.slot_summary
    # What the two staves of a corpus exemplar should be CALLED for this piece —
    # a motet's composer should not be reading "RH:" and "LH:".
    _upper, _lower, _keyboard = piece_forces(graph)
    lines = [
        f"COMPOSITION BRIEF — phrase {brief.phrase_id} ({brief.composer})",
        "",
        mindset_for(_keyboard),
        "",
    ]
    movement_id = (brief.phrase_id or "").split("_", 1)[0]
    if graph is not None:
        lines.extend(render_marks_so_far(graph, movement_id))
        lines.append("")
    cov = brief.coverage or {}
    if cov.get("tier"):
        lines.append(
            f"CORPUS COVERAGE: tier {cov['tier']} — {cov.get('bars', 0)} real bars "
            f"on disk. {cov.get('advice', '')}"
        )
    if brief.dramatic:
        lines.append("")
        lines.append("── WHY THIS PHRASE EXISTS (the dramatic plan) ──")
        lines += [f"  {line}" for line in brief.dramatic]
    if brief.creative_intent:
        lines.append(f"CREATIVE INTENT (what this passage must FEEL like): {brief.creative_intent}")
        # The emotion-to-music table has been compiled into every pack all
        # along and read by nothing. This is where it belongs: beside the
        # sentence that says what the passage must feel like.
        lines.extend(emotional_lines(brief.feeling_text, brief.composer))
    if brief.reference_study:
        lines.append("")
        lines.append(
            "WHAT YOU LEARNED FROM THE SCORES (your own study of complete "
            "reference pieces — compose from this understanding, not just the "
            "exemplar bars below):"
        )
        for st in brief.reference_study:
            lines.append(f"  [{st.get('source', '?')}] {st.get('analysis', '')}")
    tb = brief.theme_block
    if tb.get("statement"):
        op = tb.get("op", "state").upper()
        suggested = tb.get("suggested", "")
        same = suggested == tb["statement"]
        note = (
            "  (the mechanical transform returns the theme unchanged — the "
            "development is YOUR job: reharmonize it, re-rhythm it, put it in "
            "another voice, break it into its first cell)"
            if same
            else ""
        )
        key_note = f", transposed into {s.get('key')}" if tb.get("transposed") else ""
        lines.append(
            f"PRINCIPAL THEME (your own composed theme — DEVELOP it, don't re-invent):\n"
            f"  statement: {tb['statement']}\n"
            f"  this section calls for: {op}{key_note}  "
            f"suggested (a starting point, develop it further): {suggested}"
            + (f"\n{note}" if note else "")
        )
    if brief.motifs:
        lines.append("")
        lines.append(
            "MOTIFS THIS PHRASE CARRIES (the piece's designed identity — a piece is "
            "memorable because ONE idea keeps coming back changed, not because every "
            "phrase is individually well made):"
        )
        for m in brief.motifs:
            lines.append(f"  [{m['id']}] {m['transform'].upper()} — {m['character']}")
            for label, key in (
                ("scale degrees", "degrees"),
                ("intervals", "intervals"),
                ("rhythm", "rhythm"),
                ("recognise by", "anchor"),
                ("transforms allowed", "allowed"),
            ):
                if m.get(key):
                    lines.append(f"      {label}: {m[key]}")
    if brief.chord_frame:

        def _bar_frame(c):
            within = c.get("within")
            if within:
                # A bar the harmony moves through, written out beat by beat.
                inner = " ".join(
                    f"{w['beat']:g}:{w['roman']}={'/'.join(w['tones']) or '?'}" for w in within
                )
                return f"b{c['bar']}[{inner}]"
            return f"b{c['bar']}:{c['roman']}={'/'.join(c['tones']) or '?'}"

        frame = "  ".join(_bar_frame(c) for c in brief.chord_frame)
        moving = sum(1 for c in brief.chord_frame if c.get("within"))
        moved_note = (
            f"{moving} of {len(brief.chord_frame)} bars here move harmony inside "
            "the bar (shown in [brackets], beat by beat)"
            if moving
            else "no bar here moves harmony inside the bar — if the music wants "
            "a cadence compressed into one bar, write it"
        )
        lines.append(
            "CHORD FRAME (a corpus-typical harmonic option, NOT a mandate — YOU "
            "choose the harmony from what you learned studying the reference "
            "scores. If you follow a frame here, voicing beats against its chord "
            f"tones avoids clashes and non-chord tones resolve by step. "
            f"{moved_note}):\n  {frame}"
        )
    lines += [
        "",
        "── REFERENCE & CONSTRAINTS (context for your creativity) ──",
        f"Slot: bars {s.get('bars')} ({s.get('bar_count')} bars), "
        f"{s.get('key')}, {'/'.join(map(str, s.get('meter', [4, 4])))}, "
        f"♩={s.get('tempo_bpm')}",
        f"Function: {s.get('function')} | Cadence: "
        f"{s.get('cadence', {}).get('target')} at bar "
        f"{s.get('cadence', {}).get('bar')}",
    ]
    if s.get("harmony_plan"):
        lines.append(
            "Harmony plan (suggested default — adapt or replace based on your "
            "reference study): " + " | ".join(s["harmony_plan"])
        )
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
        lb = t.get("last_bar")
        if lb:
            parts.append(f"previous bar {lb['bar']} — {_upper}: {lb['rh']} | {_lower}: {lb['lh']}")
        if t.get("last_bass"):
            parts.append(f"last bass: {t['last_bass']}")
        if t.get("last_dynamic"):
            parts.append(f"dynamic: {t['last_dynamic']}")
        lines.append(
            "TRANSITION IN: " + " | ".join(parts) if parts else "TRANSITION IN: (piece opening)"
        )

        # How every earlier phrase already closed. Without this each phrase is
        # composed blind to the others' endings, and the same locally-reasonable
        # close gets chosen every time — which is exactly what happened: seven of
        # nine phrase endings shared one cadential rhythm.
        cont = t.get("continuation") or {}
        if cont:
            bits = []
            if cont.get("last_soprano_contour"):
                bits.append(f"the melody arrives {cont['last_soprano_contour']}")
            if cont.get("last_rh_density") is not None:
                bits.append(
                    f"last bar had {cont['last_rh_density']:g} melody / "
                    f"{(cont.get('last_lh_density') or 0):g} accompaniment attacks"
                )
            if cont.get("last_lh_texture"):
                bits.append(f"left hand was '{cont['last_lh_texture']}'")
            if bits:
                lines.append("  coming out of the last phrase: " + "; ".join(bits))
            if cont.get("pending_resolution"):
                lines.append(
                    f"  ⚠ the previous phrase left something hanging: "
                    f"{cont['pending_resolution']}. This phrase owes that resolution — "
                    f"answer it at the entry, or make the delay deliberate and audible."
                )
            if cont.get("motifs_stated"):
                lines.append(
                    f"  motifs already STATED: {', '.join(cont['motifs_stated'])} — "
                    f"develop them here rather than inventing new material"
                )
            if cont.get("motifs_developed"):
                lines.append(f"  motifs already developed: {', '.join(cont['motifs_developed'])}")

        habits = t.get("transition_habits") or {}
        if habits:

            def _describe(value, high, low):
                return high if value >= 0.7 else (low if value <= 0.4 else "either way")

            lines.append(
                "  how this composer joins a phrase like this ("
                f"{habits['samples']} real joints): register "
                f"{_describe(habits['register_continuity'], 'stays put', 'jumps')}, "
                f"texture {_describe(habits['texture_contrast'], 'contrasts', 'continues')}, "
                f"dynamic {_describe(habits['dynamic_continuity'], 'holds', 'shifts')}"
            )

        tr = t.get("texture_run") or {}
        if tr.get("texture_unchanged_for", 0) >= 6:
            lines.append(
                f"  ⚠ the last {tr['texture_unchanged_for']} bars (from bar "
                f"{tr['texture_since_bar']}) have all been "
                f"'{tr.get('current_texture')}' — long enough for a listener to stop "
                f"hearing it. Change what the left hand DOES here, or thin to a single "
                f"line, or drop out for a bar."
            )
        elif tr.get("current_texture"):
            lines.append(
                f"  texture coming in: '{tr['current_texture']}' for "
                f"{tr.get('texture_unchanged_for', 1)} bar(s)"
            )
        if tr.get("recent_melody_span") is not None:
            lines.append(
                f"  the melody has been sitting between MIDI {tr['recent_melody_low']} and "
                f"{tr['recent_melody_high']} (span {tr['recent_melody_span']} semitones) — "
                f"register is a structural device, so move it if this phrase should feel "
                f"like a different place."
            )

        ch = t.get("cadence_history") or {}
        # NOT `for s in ...`: `s` is the slot summary for the whole of this
        # function, and rebinding it here silently replaced the phrase's key,
        # meter and tempo with a cadence-history entry for every line after this
        # loop — so every brief with any cadence history told the composer its
        # exemplars were "transposed to None".
        for close in ch.get("closes_so_far", []):
            shape = " ".join(f"{b:g}:{d}" for b, d in close.get("rhythm", ()))
            traits = []
            if close.get("ends_with_rest"):
                traits.append("ends in a rest")
            if close.get("tied_over"):
                traits.append("tied over the barline")
            traits.append("strong beat" if close.get("on_strong_beat") else "weak beat")
            iv = close.get("final_interval")
            if iv is not None:
                traits.append(f"final move {iv:+d} semitones")
            lines.append(
                f"    bar {close['bar']} ({close['phrase_id']}"
                + (f", planned {close['planned']}" if close.get("planned") else "")
                + f"): {shape}  [{', '.join(traits)}]"
            )
        if ch.get("closes_so_far"):
            lines.insert(
                len(lines) - len(ch["closes_so_far"]),
                "  CADENCES ALREADY USED IN THIS PIECE "
                "(close this phrase DIFFERENTLY — see craft §4b):",
            )
            if ch.get("warn"):
                lines.append(
                    f"  ⚠ one cadential rhythm has already been used "
                    f"{ch['most_repeated']}x across {ch['distinct_rhythms']} distinct "
                    f"shape(s). Do not reuse it. Land on a weak beat, elide into the "
                    f"next entry, tie over the barline, decorate the arrival, or cut "
                    f"the phrase short."
                )

    if brief.gestures:
        lines.append("")
        lines.append(
            f"NAMED GESTURES ({brief.composer} — this composer's own idioms, "
            f"written out; the expression is part of the gesture):"
        )
        for g in brief.gestures:
            head = f"  • {g['name']}"
            if g.get("situation"):
                head += f" — {g['situation']}"
            lines.append(head)
            for hand, label in (("rh", _upper), ("lh", _lower)):
                if g.get(hand):
                    lines.append(f"      {label}: {g[hand]}")

    if brief.corpus_gestures:
        lines.append("")
        lines.append(
            f"CORPUS GESTURES for a '{s.get('function', '')}' phrase — real shapes from "
            f"{brief.composer}'s scores, by what they DO (rhythm and contour, not pitches; "
            f"the pitches are yours):"
        )
        for g in brief.corpus_gestures:
            joint = " → ".join(x for x in (g.get("enters"), g.get("leaves")) if x)
            lines.append(
                f"  • {g['does']}: {g['rhythm']}"
                + (f"  [{g['contour']}]" if g.get("contour") else "")
                + (f"  ({joint})" if joint else "")
                + (f"  — {g['source']}" if g.get("source") else "")
            )

    ts = brief.target_stats
    lines.append("")
    # The fingerprint goes ABOVE the per-texture medians deliberately: it is the
    # part a composer can hold in mind while writing, and the medians below are
    # the part that gets skimmed.
    # The scope warning goes FIRST because it qualifies every number after it:
    # Bach's corpus is 100% four-part chorales and Haydn's is 100% string
    # quartets, and both were being quoted as facts about the composer to
    # someone writing solo piano.
    # What must survive comes FIRST for a mode whose contract is a lock policy:
    # it constrains everything that follows.
    lock_lines = list(getattr(brief, "lock_contract", None) or [])
    if lock_lines:
        lines.extend(lock_lines)
        lines.append("")
    try:
        scope_lines = render_corpus_scope(brief.composer)
    except Exception:
        scope_lines = []
    if scope_lines:
        lines.extend(scope_lines)
        lines.append("")
    try:
        fid_lines = render_corpus_fidelity(brief.composer)
    except Exception:
        fid_lines = []
    if fid_lines:
        lines.extend(fid_lines)
        lines.append("")
    try:
        fp_lines = render_rhythmic_fingerprint(brief.composer, graph, movement_id)
    except Exception:
        fp_lines = []
    if fp_lines:
        lines.extend(fp_lines)
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
            # Spelled out as a COUNT per bar. The same fact appears three times
            # in this brief in three units — 0.04 of notes, 0.22 of bars, 0.27
            # per bar are all "Mozart's dotted rhythm" — and an unlabelled 0.27
            # beside an unlabelled 0.01 reads as a contradiction.
            line += " | ornaments per bar (a count, not a share): " + ", ".join(
                f"{k} {v:.2f}" for k, v in top if v >= 0.01
            )
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
        # Group by musical dimension so the agent sees melody / rhythm / harmony
        # targets distinctly — not just texture. These are the composer's REAL
        # ranges; hit them by writing actual idiomatic gestures, not by formula.
        groups = {
            "TEXTURE/DENSITY": (
                "texture_change_pct",
                "lh_texture_change_pct",
                "density_cv",
                "events_per_bar",
            ),
            "MELODY (leap & shape — avoid step-wise mechanical lines)": (
                "mean_abs_interval",
                "leap_ratio",
                "wide_leap_ratio",
                "repeat_ratio",
                "melodic_range",
                "melody_direction_change_pct",
            ),
            "RHYTHM (note-value mix — avoid all-eighths monotony)": (
                "eighth_ratio",
                "sixteenth_ratio",
                "triplet_ratio",
                "dotted_eighth_ratio",
                "dur_variety",
            ),
            "HARMONY": ("chord_pct", "chromatic_ratio", "seventh_chord_ratio"),
        }
        lines.append(
            f"  STYLE TARGETS ({brief.composer}'s own corpus, mean ± σ — a reality "
            f"check on the finished phrase, NOT a target to compose toward). "
            f"NOTE ON UNITS — these are all SHARES OF NOTES, which is not how "
            f"the numbers above are counted. 'events_per_bar' here counts BOTH "
            f"HANDS together while the per-texture medians count one hand; and "
            f"'dotted_eighth_ratio' is the share of NOTES that are dotted "
            f"eighths (~0.01 for Mozart), which is the same music as the ~0.27 "
            f"dotted ornaments PER BAR above and the ~0.22 of BARS that contain "
            f"one. Low ratios here do not mean 'avoid dotted rhythms':"
        )
        for label, keys in groups.items():
            present = [(k, disc[k]) for k in keys if k in disc]
            if present:
                lines.append(f"    {label}: " + "; ".join(f"{k}={v}" for k, v in present))

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
        # If an aggregate reference had no doctrine pack of its own, ONE member
        # supplied it. That fallback is reasonable and it is currently unused
        # (every armed style has its own packs) — but it is live code, and when
        # it does fire the reader has to be told whose doctrine they are reading.
        stood_in = sorted(
            {
                src
                for pack in ("cadence_scripts", "ornament_intents", "breathing_rules")
                if (src := pack_source(brief.composer, pack)) != brief.composer
            }
        )
        if stood_in:
            lines.append(
                f"  (NOTE: {brief.composer} has no doctrine pack of its own — what "
                f"follows is {', '.join(stood_in)}'s, standing in for the style. "
                f"Read it as one member's practice, not the idiom's consensus.)"
            )
        req = doc.get("cadence_requirement")
        if req:
            lines.append(f"  THIS CADENCE REQUIRES: {req}")
        cs = doc.get("cadence_script")
        if cs:
            parts = [f"type {cs.get('type')}"]
            approach = cs.get("approach")
            if approach:
                # Chords as music, not as a Python list repr.
                parts.append(
                    "approach "
                    + (
                        " - ".join(str(a) for a in approach)
                        if isinstance(approach, (list, tuple))
                        else str(approach)
                    )
                )
            if cs.get("bass"):
                parts.append(f"bass degrees {cs['bass']}")
            if cs.get("usage"):
                parts.append(str(cs["usage"]))
            lines.append("  Cadence: " + ", ".join(str(p) for p in parts))
        for intent in doc.get("ornament_intent", []):
            lines.append(f"  Ornament: {intent}")
        for br in doc.get("breathing", []):
            lines.append(f"  Breathe: {br}")
        for dev in doc.get("harmonic_devices", []):
            lines.append(f"  Color: {dev.get('name')} — {dev.get('use')}")
        for mp in doc.get("melody_priors", []):
            lines.append(f"  Melody: {mp}")
        for ht in doc.get("harmonic_temperature", []):
            lines.append(f"  Tonal motion: {ht}")
        for mod in doc.get("modulation_scripts", []):
            lines.append(f"  Modulation: {mod}")
        for fig in doc.get("figuration", []):
            lines.append(f"  Figuration: {fig}")
        for cp in doc.get("counterpoint", []):
            lines.append(f"  Counterpoint: {cp}")

    # ── Phrase-level shape (the arc, above the single bar) ──
    ps = brief.phrase_shape
    if ps:
        lines.append("")
        rng = ps.get("bars") or []
        span = f"{rng[0]}-{rng[-1]}" if len(rng) >= 2 else (str(rng[0]) if rng else "?")
        lines.append(
            f"PHRASE SHAPE (corpus {ps.get('source')} bars {span}, role {ps.get('role')}):"
        )
        # A flat arc says nothing — printing "[1.0, 1.0, 1.0, 1.0] (peak at bar 1)"
        # as this phrase's shape is worse than printing nothing, because it reads
        # as an instruction to keep the density constant.
        arc = ps.get("density_arc") or []
        if arc and len(set(arc)) > 1:
            lines.append(f"  density arc: {arc} (peak at bar {ps.get('peak_at')})")
        reg = ps.get("register_arc") or []
        if reg and len(set(reg)) > 1:
            lines.append(f"  register arc: {reg}")

    if brief.transition_patterns.get("provenance"):
        lines.append("")
        lines.append(f"  ! {brief.transition_patterns['provenance']}")

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

    # ── Voicing: how thick the writing is ──
    # The brief said what the left hand plays, how dense the bar is and which
    # rhythms recur, and never how many notes sound in the melody. A nocturne
    # came back with a right hand that is a single line in 99% of its attacks
    # against a real-Chopin 22%, and no distribution test can catch that: the
    # per-movement 10th percentile of chord share is 0.00, because some real
    # movements genuinely are single-line. It has to be said up front.
    lines.extend(voicing_lines(brief.composer, graph, movement_id))
    lines.extend(motion_lines(brief.composer))
    lines.extend(cadence_soprano_lines(brief.composer))

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
        if ex.harmony:
            lines.append(f"   harmony within the bar: {ex.harmony}")
        if ex.rh:
            lines.append(f"   {_upper}: {ex.rh}")
        if ex.lh:
            lines.append(f"   {_lower}: {ex.lh}")
    if not brief.exemplars:
        lines.append("  (none found — see warnings)")

    if brief.anti_patterns:
        lines.append("")
        lines.append("AVOID (AI tells): " + "; ".join(brief.anti_patterns))

    if brief.warnings:
        lines.append("")
        lines.append("WARNINGS: " + "; ".join(brief.warnings))

    return "\n".join(lines)
