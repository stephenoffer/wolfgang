"""
CommitGate — blocking quality gate for agent-authored phrases.

Runs at commit time (commit_agent_phrase_*), AFTER physical validation
(validator.py — strict, never waivable) and BEFORE the phrase is stored.

ONLY physical constraints block (meter capacity here; range/span in
validator.py). Every artistic / corpus-alignment check — skeletal density,
photocopied accompaniment, ``composed_blind`` — is ADVISORY: it surfaces as a
warning the fresh-ears music-critic weighs, and never rejects a commit. The
agent has creative liberty to invent away from the corpus; the critic's ear,
not a statistical floor, judges whether the music works.

Waivers still exist for the rare case a physical-adjacent check needs an
explicit logged exception, but the common path is: warnings inform, the critic
decides. A real corpus bar passes its own composer's gate by construction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from . import musicality
from .anti_pattern_detector import run_all_detectors
from .composition_brief import (
    _self_continuation,
    _slot_textures,
    _texture_templates,
    resolve_composer,
    texture_density_stats,
)
from .models import LayerIR
from .pitch import pitch_to_midi

# Checks that BLOCK at commit. ONLY physical constraints block — the gate must
# never fence the agent inside the corpus. ``meter`` (bar capacity) is the one
# artistic-adjacent physical check enforced here; range/span live in validator.py.
#
# Corpus-alignment checks (``density_low_*``, ``figuration_flat``,
# ``composed_blind``) are now ADVISORY: they surface as warnings the fresh-ears
# music-critic weighs, never auto-blocks. The agent has creative liberty to
# invent away from the corpus — the critic's ear, not a statistical floor, is the
# judge of whether the result is musical. (Brief-receipt is still enforced
# separately at commit in scales.py — studying references is required, but what
# the agent then writes is its own.)
_DEFAULT_BLOCKING = {
    "meter",
}

# Minimum phrase length (bars) for checks that need a window
_MIN_BARS = 3

# Half the generic human-sounding density (musicality.figuration_richness
# fallback: RH 6.0 / LH 5.5 events/bar) — the density floor used when a
# composer has no corpus density stats, so missing stats never disable the
# skeletal-writing guard.
_GENERIC_DENSITY_MEDIAN = {"rh": 6.0, "lh": 5.5}

# Max number of *blocking* checks that may be waived in a single commit.
# Waiving more than one blocking check at once usually means "make the gate
# go away", not a single honest artistic exception.
_MAX_BLOCKING_WAIVERS = 1

# Minimum length of a waiver reason — a real musical justification, not "x".
_MIN_WAIVER_REASON_LEN = 20


@dataclass
class GateDiagnostic:
    check: str = ""
    severity: str = "warn"  # block | warn
    bars: Optional[str] = None
    detail: str = ""
    suggestion: str = ""
    corpus_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check": self.check,
            "severity": self.severity,
            "bars": self.bars,
            "detail": self.detail,
            "suggestion": self.suggestion,
            "corpus_ref": self.corpus_ref,
        }


@dataclass
class GateResult:
    passed: bool = True
    blocking: List[GateDiagnostic] = field(default_factory=list)
    warnings: List[GateDiagnostic] = field(default_factory=list)
    overrides: List[Dict[str, str]] = field(default_factory=list)
    rejected_waivers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "blocking": [d.to_dict() for d in self.blocking],
            "warnings": [d.to_dict() for d in self.warnings],
            "overrides": self.overrides,
            "rejected_waivers": self.rejected_waivers,
        }


# ─── Individual checks ───────────────────────────────────────────────────────


def _dominant_textures(slot, composer: str = "") -> Tuple[str, str]:
    """Most common (rh, lh) texture pair in the slot plan.

    ``composer`` matters even though it looks optional: when the slot has no
    texture plan this falls through to inference, and inference reads the
    composer's OWN corpus modes. Without it every phrase is judged against the
    all-composer mode — Mozart's alberti bass read as bass_melody, and the
    per-texture density floors then come from the wrong idiom entirely.
    """
    from collections import Counter

    textures = _slot_textures(slot, composer)
    if not textures:
        return "singing_melody", "alberti"
    rh = Counter(t[0] for t in textures).most_common(1)[0][0]
    lh = Counter(t[1] for t in textures).most_common(1)[0][0]
    return rh, lh


def _per_bar_event_counts(layer: LayerIR, hand: str) -> Dict[int, int]:
    """Note/chord events per bar for a hand (a chord counts once, matching
    corpus melody_density / accomp_density).

    ``counter_reply`` is the RIGHT hand's inner voice — ``music_io`` engraves it
    on the treble staff as voice 2 — so it belongs to the RH count. Counting it
    as left-hand density contradicted where the notes actually appear, and once
    real inner voices started flowing through (four-part chorales), it moved the
    entire alto line onto the wrong hand: a Bach phrase reported 13 RH events
    against a corpus melody density of 55.
    """
    inner = getattr(layer, "inner_voices", None) or {}
    if hand == "rh":
        events = (
            layer.principal_line
            + layer.ornamental_surface
            + layer.counter_reply
            + [e for k, v in inner.items() if k.startswith("treble") for e in v]
        )
    else:
        events = (
            layer.bass_foundation
            + layer.response_layer
            + [e for k, v in inner.items() if k.startswith("bass") for e in v]
        )
    counts: Dict[int, int] = {}
    for e in events:
        if getattr(e, "pitch", None) == "rest":
            continue
        counts[e.bar] = counts.get(e.bar, 0) + 1
    return counts


def _bar_texture_floors(
    slot, density_stats: Dict, hand: str, composer: str = ""
) -> Dict[int, Tuple[float, float, str]]:
    """Per-bar (floor, median, texture) from each bar's OWN planned texture.

    Real phrases mix textures and thin at cadences; checking every bar against
    the phrase's single dominant texture over-blocks legitimate intra-phrase
    variation. Each bar is judged against its own texture's corpus floor.
    """
    plan = getattr(slot, "texture_plan", None) or []
    bar_start = getattr(slot, "bar_start", 1)
    out: Dict[int, Tuple[float, float, str]] = {}
    rh_def, lh_def = _dominant_textures(slot, composer)
    default_tex = rh_def if hand == "rh" else lh_def
    n = getattr(slot, "bar_count", len(plan)) or len(plan)
    for i in range(max(n, len(plan))):
        bar = bar_start + i
        tp = plan[i] if i < len(plan) else None
        tex = (getattr(tp, f"{hand}_texture", None) if tp else None) or default_tex
        entry = density_stats.get(hand, {}).get(tex)
        if entry:
            median = entry["median"]
            # Distribution-aware floor: a bar at/above the corpus 25th percentile
            # for its texture is in the normal range and must never be called
            # skeletal — half-median over-blocks high-spread, sparse-idiom
            # textures (median 10 / p25 3 wrongly flags legitimate 3-4 event
            # bars). Floor = min(half-median, p25). Calibrated on the corpus
            # self-pass harness (Beethoven's dramatic sparse phrases).
            p25 = entry.get("p25", median)
            out[bar] = (min(0.5 * median, p25), median, tex)
        else:
            median = _GENERIC_DENSITY_MEDIAN[hand]
            out[bar] = (0.5 * median, median, tex)
    return out


# Fraction of bars that must be skeletal before density blocks the phrase —
# one or two thinned bars (a cadence, a breath) is real music, not a sketch.
_SKELETAL_BAR_FRACTION = 0.6


def _check_density(
    layer: LayerIR, slot, density_stats: Dict, hand: str, composer: str = ""
) -> Optional[GateDiagnostic]:
    """Block when a MAJORITY of bars are skeletal vs their own texture's corpus
    floor (half the median). Per-bar + per-texture so real phrases that mix
    textures or thin at a cadence pass — only pervasively skeletal writing
    blocks. This is the '9 notes/bar when real Chopin writes 33' guard.
    """
    counts = _per_bar_event_counts(layer, hand)
    if not counts:
        return None
    floors = _bar_texture_floors(slot, density_stats, hand, composer)
    skeletal: List[int] = []
    worst_median = 0.0
    worst_tex = ""
    for bar, n in sorted(counts.items()):
        floor, median, tex = floors.get(
            bar, (0.5 * _GENERIC_DENSITY_MEDIAN[hand], _GENERIC_DENSITY_MEDIAN[hand], "?")
        )
        if n < floor:
            skeletal.append(bar)
            if median > worst_median:
                worst_median, worst_tex = median, tex
    frac = len(skeletal) / len(counts)
    if frac < _SKELETAL_BAR_FRACTION:
        return None
    has_stats = bool(density_stats.get(hand, {}).get(worst_tex))
    corpus_ref = (
        f"{worst_tex}: median {worst_median}"
        if has_stats
        else f"no corpus density stats for '{worst_tex}'; generic floor"
    )
    return GateDiagnostic(
        check=f"density_low_{hand}",
        severity="warn",
        bars=",".join(str(b) for b in skeletal),
        detail=(
            f"{hand.upper()} skeletal in {len(skeletal)}/{len(counts)} bars "
            f"(<half the corpus median for each bar's texture) "
            f"— this is a sketch, not a realization"
        ),
        suggestion=(
            f"Advisory: {hand.upper()} reads as a sketch here. If you want more "
            f"motion, write toward the corpus median (~{worst_median:g} "
            f"events/bar for {worst_tex}: flowing arpeggiation, passing tones, "
            f"inner motion). If the sparseness is intentional, leave it — the "
            f"critic judges by ear."
        ),
        corpus_ref=corpus_ref,
    )


# Near-zero density-variance floor. Calibration finding (corpus self-pass
# harness): real 4-bar phrases legitimately have low density_cv — chopin's 10th
# percentile is ~0.0, mozart's ~0.07 — because a consistent texture for four
# bars is normal, beautiful music. The movement-level corpus mean (≈0.35) does
# NOT transfer to phrase scale. So this is WARN-only and fires only on the truly
# metronomic (CV at/near zero — identical event count every bar). Pervasive
# flat density across a whole SECTION is the real tell and is caught there
# (see the human-ness discriminator / section gate), not per phrase.
_DENSITY_CV_FLOOR = 0.05
_DENSITY_CV_MIN_BARS = 4

# Textures whose whole character is constant emission — either constant SUSTAIN
# (a drone holds) or constant MOTION (an Alberti bass emits the same number of
# notes every bar; that is what makes it Alberti). A flat density there is the
# idiom, not a defect, so warning on it warns on the defining feature of a
# legitimate way of writing.
#
# Named for what it holds, not for "sustained" — half of it is perpetual motion.
#
# Measured across all 23 armed composers (108,575 real 4-bar windows), the
# share of windows that are metronomically flat, by dominant texture:
#
#   broken_chord_asc  21.4% | interlocking       19.6% | block_chord_offbeat 17.9%
#   broken_chord_wave 17.3% | alberti            16.6% | block_chord_sparse  11.9%
#   RH chordal        17.3% | RH zigzag_figur.   17.3% | RH scalar_run       15.6%
#   ...
#   walking_bass       7.9% | bass_melody         4.5% | RH singing_melody    5.3%
#
# The perpetual-motion accompaniment idioms cluster at the top and the lines
# that are free to breathe cluster at the bottom, which is the split this set
# encodes. **RH scalar_run is deliberately NOT exempt** despite its 15.6%: a run
# is not constant BY DEFINITION — it can accelerate, break off, be interrupted
# by rests — and flat scalar writing is a documented failure mode of this
# project's own output ("étude-scalar melody"). Exempting on the rate alone
# would have retired the one detector that catches it.
#
# This set is what the check is FOR: it now fires only where the texture could
# ebb and flow and doesn't. Corpus-wide that is 1.5% of real windows (was 4.2%,
# and 20.8% for Rimsky-Korsakov, the first heavily orchestral composer in the
# corpus — orchestral textures are far more constant per bar than keyboard ones,
# which is what made this visible rather than what made it wrong).
_SUSTAINED_RH_TEXTURES = {"held_note", "chordal", "silence", "zigzag_figuration"}
_SUSTAINED_LH_TEXTURES = {
    "pedal_point",
    "sustained",
    "drone",
    "silence",
    "block_chord_sparse",
    # constant-motion accompaniment idioms
    "alberti",
    "broken_chord_wave",
    "broken_chord_asc",
    "broken_chord_desc",
    "block_chord_offbeat",
    "interlocking",
}


def _check_density_variance(layer: LayerIR, slot, composer: str) -> Optional[GateDiagnostic]:
    """Warn on metronomically flat density — near-identical event count bar
    after bar.

    The skeletal-density check (`_check_density`) catches *too few* notes; this
    catches *zero ebb and flow*. WARN-only by design: at phrase scale, modest
    density consistency is idiomatic (see _DENSITY_CV_FLOOR), so only the truly
    flat (CV≈0) is flagged, and it never blocks.
    """
    cv, detail = musicality.density_cv(layer)
    bar_count = detail.get("bar_count", 0)
    if bar_count < _DENSITY_CV_MIN_BARS:
        return None  # too short to judge ebb-and-flow
    if cv >= _DENSITY_CV_FLOOR:
        return None
    # Sustained textures have near-constant density BY DEFINITION — that is what
    # sustained means. Falsified against the rebuilt corpus: this warned on 27%
    # of real Palestrina phrases, whose Renaissance polyphony moves in even
    # values across all voices. Warning on the defining feature of a legitimate
    # idiom is noise the critic then has to triage away.
    # Exempt only on a texture the slot ACTUALLY DECLARES.
    #
    # `_slot_textures` falls back to `_infer_textures`, which reads a density
    # curve and returns "alberti" for every bar at density >= 0.35 and
    # "block_chord_sparse" below it — and BOTH are exempt here. So reading the
    # inferred texture would switch this check off for every phrase that has no
    # texture plan, which is most of them: the detector would still run, still
    # compute, and never fire again. An inferred texture is a guess derived from
    # a density curve, not evidence about the idiom, and an unknown texture is
    # not a constant one.
    if getattr(slot, "texture_plan", None):
        rh_tex, lh_tex = _dominant_textures(slot, composer)
        if rh_tex in _SUSTAINED_RH_TEXTURES or lh_tex in _SUSTAINED_LH_TEXTURES:
            return None
    return GateDiagnostic(
        check="density_variance",
        severity="warn",
        bars=f"{slot.bar_start}-{slot.bar_start + bar_count - 1}",
        detail=(
            f"density is metronomically flat (CV {cv} < {_DENSITY_CV_FLOOR}); "
            f"event counts per bar: {detail.get('per_bar')} — identical bar "
            f"after bar, no ebb-and-flow"
        ),
        suggestion=(
            "Vary density between bars: thin under the melodic peak and "
            "at cadences, thicken on the build. Let the accompaniment "
            "respond to the line rather than running at one rate."
        ),
        corpus_ref="flat-density tell (CV≈0)",
    )


def _lh_bar_patterns(layer: LayerIR) -> Dict[int, Tuple[int, ...]]:
    """Per-bar LH interval patterns (response + bass), for repeat detection."""
    bars: Dict[int, List[int]] = {}
    for evt in sorted(layer.response_layer + layer.bass_foundation, key=lambda e: (e.bar, e.beat)):
        if evt.pitch == "rest":
            continue
        # The BASS of a chord, not whichever pitch happens to be written first.
        # A left-hand chord's shape is what its lowest voice does.
        pitches = evt.pitch if isinstance(evt.pitch, list) else [evt.pitch]
        midis = []
        for pch in pitches:
            try:
                m = pitch_to_midi(pch)
            except (ValueError, KeyError, TypeError):
                m = None
            if m is not None:
                midis.append(m)
        midi = min(midis) if midis else None
        if midi is not None:
            bars.setdefault(evt.bar, []).append(midi)
    return {
        b: tuple(m[i + 1] - m[i] for i in range(len(m) - 1)) for b, m in bars.items() if len(m) >= 2
    }


# LH textures that are inherently static repetition — an oom-pah / pedal /
# sustained chord legitimately repeats bar after bar under prolonged harmony,
# so identical-pattern detection is a false positive on real music (verified
# against the corpus self-pass harness: Beethoven block_chord_offbeat triggered
# 8/10 false figuration_flat blocks). Photocopying is a tell for FLOWING
# textures (alberti, arpeggio, walking bass), not for these.
_STATIC_LH_TEXTURES = {
    "block_chord",
    "block_chord_offbeat",
    "block_chords",
    "pedal_point",
    "sustained",
    "drone",
    "repeated_chord",
    "repeated_chords",
    "sustained_chord",
    "oom_pah",
    "chordal",
    # No corpus evidence for/against variation in unclassified textures, so
    # don't block on identity alone (Chopin self-pass: all figuration_flat false
    # positives were unclassified LH).
    "unclassified",
    "",
}

# A photocopy tell needs enough comparable bars to be meaningful — a normal
# 4-bar phrase repeating its figure is idiomatic, not mechanical.
_FIGURATION_FLAT_MIN_BARS = 4


def _check_figuration_flat(layer: LayerIR, slot, composer: str) -> Optional[GateDiagnostic]:
    """Block when a FLOWING accompaniment is photocopied identically across a
    sustained span — the machine signature.

    Corpus self-continuation says patterns PERSIST (e.g. Mozart alberti 0.67)
    but are continuously varied. The block threshold is composer/texture-
    relative (self_continuation + margin, clamped) so high-persistence textures
    aren't over-blocked. Inherently-static textures (block chords, pedal) are
    exempt — they legitimately repeat under prolonged harmony. Below threshold
    this is left to the warn-level same_accompaniment detector.
    """
    _, lh_tex = _dominant_textures(slot, composer)
    if lh_tex in _STATIC_LH_TEXTURES:
        return None  # repetition is the idiom for these textures

    patterns = _lh_bar_patterns(layer)
    if len(patterns) < _FIGURATION_FLAT_MIN_BARS:  # too short to be a photocopy tell
        return None
    values = list(patterns.values())
    from collections import Counter

    most_common, count = Counter(values).most_common(1)[0]
    ratio = count / len(values)

    cont = _self_continuation(composer).get(lh_tex)
    # Threshold scales with how persistent this texture is in the corpus.
    threshold = max(0.9, round((cont or 0.0) + 0.25, 3)) if cont is not None else 0.9
    threshold = min(threshold, 1.0)
    if ratio < threshold:
        return None

    ref = (
        f"corpus {lh_tex} self-continuation {cont} (block ≥{threshold})"
        if cont is not None
        else "corpus patterns persist but vary bar to bar"
    )
    bars_sorted = sorted(patterns)
    return GateDiagnostic(
        check="figuration_flat",
        severity="warn",
        bars=f"{bars_sorted[0]}-{bars_sorted[-1]}",
        detail=(
            f"{ratio:.0%} of bars have an identical LH pattern "
            f"({len(values)} bars checked) — accompaniment on "
            f"photocopier"
        ),
        suggestion=(
            "Keep the figure but vary it: shift a chord tone, "
            "invert the contour at the phrase midpoint, follow the "
            "harmony into a new position, drop to half motion under "
            "the melodic peak"
        ),
        corpus_ref=ref,
    )


def _check_corpus_alignment(graph, phrase_id: str, layer: LayerIR) -> List[GateDiagnostic]:
    """Flag when the committed surface resembles NONE of the briefed corpus
    exemplars (anti-skip). The brief puts real corpus bars in front of the
    agent and says 'adapt — never copy, never ignore'; this verifies the
    surface didn't ignore them.

    Both RH and LH are ADVISORY (warn-only): inventing away from the corpus is a
    legitimate creative choice, not an error — the fresh-ears music-critic judges
    whether the result sings. The signal is still recorded (``composed_blind`` on
    the trace) so self_evaluate and the critic can weigh it.
    """
    from .anti_skip import check_composed_blind

    state = graph.phrases.get(phrase_id)
    trace = getattr(state, "context_trace", None) if state else None
    if not isinstance(trace, dict):
        return []
    out: List[GateDiagnostic] = []

    rh_exemplars = trace.get("briefed_exemplars")
    if rh_exemplars:
        finding = check_composed_blind(layer, rh_exemplars, hand="rh")
        trace["composed_blind"] = bool(finding)
        if finding:
            out.append(
                GateDiagnostic(
                    check="composed_blind",
                    severity="warn",
                    detail=finding["message"],
                    suggestion=(
                        "Advisory: the surface resembles none of the briefed "
                        "exemplars. If that's deliberate invention, fine — the "
                        "critic will judge it by ear. If it drifted by accident, "
                        "consider anchoring in the exemplars' rhythmic cells and "
                        "interval shapes (transpose/reharmonize/splice)."
                    ),
                    corpus_ref=(
                        f"best resemblance {finding['best_resemblance']} < "
                        f"floor {finding['floor']} over "
                        f"{finding['n_exemplars']} exemplars"
                    ),
                )
            )

    lh_exemplars = trace.get("briefed_exemplar_lhs")
    if lh_exemplars:
        lh_finding = check_composed_blind(layer, lh_exemplars, hand="lh")
        trace["composed_blind_lh"] = bool(lh_finding)
        if lh_finding:
            out.append(
                GateDiagnostic(
                    check="composed_blind_lh",
                    severity="warn",
                    detail=lh_finding["message"],
                    suggestion=(
                        "Anchor the accompaniment in the briefed LH "
                        "vocabulary — borrow its figure and follow it into "
                        "the harmony rather than inventing a pattern."
                    ),
                    corpus_ref=(
                        f"best LH resemblance {lh_finding['best_resemblance']}"
                        f" < floor {lh_finding['floor']} over "
                        f"{lh_finding['n_exemplars']} LH exemplars"
                    ),
                )
            )
    return out


# The corpus and the hand-authored texture templates name the same quantities
# differently — "grace"/"trill"/"turn" against "grace_notes"/"trills"/"turns" —
# and the corpus path filtered to its own four keys while the template path
# summed whatever it found. So a template fallback contributed either nothing
# (its keys matched no filter) or too much (it summed `dotted_pairs`, which is a
# rhythm, not an ornament). One normalizer, one vocabulary, both paths.
_ORNAMENT_KEY_ALIASES = {
    "grace": "grace",
    "grace_notes": "grace",
    "trill": "trill",
    "trills": "trill",
    "mordent": "mordent",
    "mordents": "mordent",
    "turn": "turn",
    "turns": "turn",
    "written_ornaments": "written",
    # Deliberately absent: "dotted"/"dotted_pairs" is a rhythmic figure, not an
    # ornament, and counting it made an unornamented phrase look ornamented.
}


def _ornament_rates(stats: Dict) -> Dict[str, float]:
    """Ornaments-per-bar by canonical name, from either vocabulary."""
    out: Dict[str, float] = {}
    for key, value in (stats or {}).items():
        canon = _ORNAMENT_KEY_ALIASES.get(key)
        if canon and isinstance(value, (int, float)):
            out[canon] = out.get(canon, 0.0) + float(value)
    return out


def _check_expression_zero(layer: LayerIR, slot, composer: str) -> Optional[GateDiagnostic]:
    """Warn when corpus says ornaments/slurs are pervasive but the phrase
    has none at all."""
    if layer.bar_count < max(_MIN_BARS, 4):
        return None
    events = (
        layer.principal_line
        + layer.bass_foundation
        + layer.response_layer
        + layer.counter_reply
        + layer.ornamental_surface
    )
    has_expression = any(e.ornament or e.slur or getattr(e, "hairpin", None) for e in events)
    if has_expression:
        return None

    rh_tex, _ = _dominant_textures(slot, composer)
    templates = _texture_templates(composer).get("rh_templates", {})
    # Corpus-measured first; the hand-authored templates are only a fallback and
    # have no builder (see composition_brief.ornament_stats).
    from .composition_brief import ornament_stats

    measured = (ornament_stats(composer).get("textures") or {}).get(rh_tex) or {}
    orn = _ornament_rates(measured) or _ornament_rates(
        (templates.get(rh_tex) or {}).get("avg_ornament_density") or {}
    )
    total_orn = sum(orn.values())
    # Compare an EXPECTED COUNT for this phrase, not a per-bar rate against a
    # fixed number. `total_orn` is ornaments per bar: at Chopin's measured 0.07
    # in zigzag figuration, a 4-bar phrase is expected to carry 0.28 of an
    # ornament, and warning that it has none says nothing. The old fixed 0.1/bar
    # floor sat ABOVE the measured rate for every composer but Mozart, so for 26
    # of 27 armed composers this check could not fire at any phrase length —
    # while a long phrase in a genuinely ornamented idiom went unremarked.
    #
    # One expected ornament is the smallest claim worth making: below it, "you
    # wrote none" is not evidence of anything.
    #
    # Where this now fires, by the composer's own dense-texture rate: Mozart at
    # 3 bars, Haydn 11, Chopin 15, Beethoven 22, Bach effectively never (0.004 —
    # his corpus is chorales, which do not ornament). For the other 19 armed
    # composers it still cannot fire at any length, and that is a CORPUS limit
    # rather than a threshold one: their scores were acquired as MIDI, which
    # carries no ornament marks at all, so the measured rate is a structural
    # zero and not a finding. Silence here means "no evidence", never "this
    # idiom does not ornament" — do not read it as the latter, and do not raise
    # the rate to make the check fire on composers whose corpus cannot support it.
    bars = getattr(layer, "bar_count", 0) or getattr(slot, "bar_count", 0) or 1
    expected = total_orn * bars
    if expected < 1.0:
        return None
    return GateDiagnostic(
        check="expression_zero",
        severity="warn",
        detail=(
            f"No ornaments, slurs, or hairpins anywhere in "
            f"{bars} bars; corpus '{rh_tex}' carries ~{total_orn:.2f} "
            f"ornaments/bar, so ~{expected:.1f} would be expected here, "
            f"plus phrasing slurs"
        ),
        suggestion=(
            "Expression is part of the notes, not decoration: "
            "slur the singing line, place ornaments where the "
            "music yearns or arrives (see ornament-intent.md), "
            "shape dynamics with hairpins"
        ),
        corpus_ref=f"{rh_tex} ornament density {total_orn:.2f}/bar",
    )


def _check_contour(layer: LayerIR) -> Optional[GateDiagnostic]:
    score, detail = musicality.direction_changes_per_bar(layer)
    if layer.bar_count < _MIN_BARS or detail.get("per_bar", 1.0) >= 0.5:
        return None
    return GateDiagnostic(
        check="direction_changes_per_bar",
        severity="warn",
        detail=(
            f"Melodic contour changes direction only "
            f"{detail.get('per_bar')}×/bar (corpus norm 1.0-2.0) — "
            f"the line is monotonic"
        ),
        suggestion=(
            "Let the melody breathe in waves: rise to a local peak, fall back, gap-fill after leaps"
        ),
        corpus_ref="human corpus: 1.0-2.0 direction changes/bar",
    )


def _check_interval_profile(layer: LayerIR) -> Optional[GateDiagnostic]:
    score, detail = musicality.melodic_interval_profile(layer)
    if detail.get("interval_count", 0) < 8 or score >= 0.5:
        return None
    actual = detail.get("actual", {})
    return GateDiagnostic(
        check="interval_distribution",
        severity="warn",
        detail=(
            f"Melodic interval mix {actual} is far from the tonal prior {detail.get('priors')}"
        ),
        suggestion=(
            "Aim for mostly stepwise motion with strategic leaps "
            "at peaks; a leap-dominated line reads as arpeggiated "
            "accompaniment, not melody"
        ),
    )


# ─── Gate runner ─────────────────────────────────────────────────────────────


def _check_meter_overflow(layer: LayerIR) -> Optional[GateDiagnostic]:
    """Physical constraint: no event may extend past its bar's capacity.

    Catches sequentially-parsed content that exceeds the meter (e.g. five
    quarters of melody in a 4/4 bar). Pedal-under-figuration is handled at
    parse time by direct_compose and never reaches this check overflowed.
    """
    from fractions import Fraction

    from .duration import bar_duration, dur_to_beats, is_grace

    meter = getattr(layer, "meter", (4, 4)) or (4, 4)
    capacity = bar_duration(tuple(meter))
    tol = Fraction(1, 1000)
    bad: List[str] = []
    # Each entry is one independent notated voice, so an overlap WITHIN an entry
    # is a real defect (two notes claiming the same instant in one voice) while
    # an overlap between entries is legitimate polyphony. response_layer is
    # exempt from the overlap check: it doubles as the pedal-under-figuration
    # tail, which re-anchors to beat 1 under the sustained bass by design.
    for name, events, check_overlap in (
        ("principal_line", layer.principal_line, True),
        ("bass_foundation", layer.bass_foundation, True),
        ("counter_reply", layer.counter_reply, True),
        ("response_layer", layer.response_layer, False),
        ("ornamental_surface", layer.ornamental_surface, False),
        # Third and fourth voices per hand are independent notated voices, so
        # each must fill its bar and must not overlap itself.
        *[(k, v, True) for k, v in sorted((getattr(layer, "inner_voices", None) or {}).items())],
    ):
        timed = [e for e in (events or []) if not is_grace(getattr(e, "ornament", None))]
        for ev in timed:
            dur = dur_to_beats(ev.duration)
            end = Fraction(ev.beat).limit_denominator(96) - 1 + dur
            if end > capacity + tol:
                bad.append(
                    f"{name} bar {ev.bar} beat {ev.beat} "
                    f"{ev.pitch}{ev.duration} ends at {float(end):.4g}/{float(capacity):g}"
                )
        if not check_overlap:
            continue
        for a, b in zip(timed, timed[1:]):
            if a.bar != b.bar:
                continue
            a_end = Fraction(a.beat).limit_denominator(96) + dur_to_beats(a.duration)
            if a_end > Fraction(b.beat).limit_denominator(96) + tol:
                bad.append(
                    f"{name} bar {a.bar}: {a.pitch}{a.duration} at beat {a.beat} still "
                    f"sounds when {b.pitch} enters at beat {b.beat} (one voice cannot "
                    f"overlap itself — use '//' for a second voice in the hand)"
                )
    if not bad:
        return None
    return GateDiagnostic(
        check="meter",
        severity="block",
        detail=f"{len(bad)} metric problem(s): " + "; ".join(bad[:5]),
        suggestion="Each bar's content must sum to the meter capacity per "
        "voice. For a sustained bass UNDER figuration, write the "
        "pedal as a full-bar first LH event — the figuration "
        "after it re-anchors to beat 1 automatically.",
    )


def run_commit_gate(
    graph,
    phrase_id: str,
    layer: LayerIR,
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> GateResult:
    """Run all artistic gate checks on an agent-authored phrase.

    ``allow`` waives named checks with a reason (logged by the caller).
    Returns a GateResult; the commit is rejected when ``passed`` is False.
    """
    result = GateResult()
    state = graph.phrases.get(phrase_id)
    slot = state.slot if state else None
    if slot is None:
        return result  # nothing to check against

    warnings_sink: List[str] = []
    resolved = resolve_composer(graph, composer, warnings_sink)
    density_stats = texture_density_stats(resolved)

    waived: Dict[str, str] = {}
    blocking_waivers = 0
    for w in allow or []:
        check = str(w.get("check", "")).strip()
        reason = str(w.get("reason", "")).strip()
        if not check:
            continue
        if check in ("validation", "physical", "range", "meter", "span"):
            result.rejected_waivers.append(
                f"'{check}' is a physical constraint and cannot be waived"
            )
            continue
        if len(reason) < _MIN_WAIVER_REASON_LEN:
            result.rejected_waivers.append(
                f"waiver for '{check}' needs a real musical reason "
                f"(≥{_MIN_WAIVER_REASON_LEN} chars), not '{reason}'"
            )
            continue
        # Cap how many *blocking* checks may be waived at once — waiving the
        # whole blocking set is "make the gate go away", not an exception.
        if check in _DEFAULT_BLOCKING:
            if blocking_waivers >= _MAX_BLOCKING_WAIVERS:
                result.rejected_waivers.append(
                    f"too many blocking checks waived at once ('{check}'); "
                    f"at most {_MAX_BLOCKING_WAIVERS} may be waived per commit "
                    f"— revise the bars instead of waiving them all"
                )
                continue
            blocking_waivers += 1
        waived[check] = reason

    diagnostics: List[GateDiagnostic] = []

    # Physical constraint: bar capacity (never waivable)
    d = _check_meter_overflow(layer)
    if d:
        diagnostics.append(d)

    # Density floors (the skeletal-writing guard)
    for hand in ("rh", "lh"):
        d = _check_density(layer, slot, density_stats, hand, composer)
        if d:
            diagnostics.append(d)

    # Density variance (flat-at-the-median guard)
    d = _check_density_variance(layer, slot, resolved)
    if d:
        diagnostics.append(d)

    # Photocopied accompaniment
    d = _check_figuration_flat(layer, slot, resolved)
    if d:
        diagnostics.append(d)

    # Corpus alignment: did the surface actually adapt the briefed exemplars?
    diagnostics.extend(_check_corpus_alignment(graph, phrase_id, layer))

    # Anti-pattern detectors (all warn-level here; same_accompaniment at
    # its 0.6 threshold over-fires on legitimately persistent figures)
    prev_layer = _previous_realized(graph, phrase_id)
    style_program = getattr(graph, "style_program", None)
    anti_patterns = getattr(style_program, "anti_patterns", None)
    try:
        detector_results = run_all_detectors(layer, anti_patterns, prev_layer)
    except Exception:
        detector_results = []
    for det in detector_results:
        if not det.get("detected"):
            continue
        name = det.get("name", det.get("rule_id", "anti_pattern"))
        if name == "same_accompaniment" and any(x.check == "figuration_flat" for x in diagnostics):
            continue  # already covered by the stronger check
        diagnostics.append(
            GateDiagnostic(
                check=name,
                severity="warn",
                detail=det.get("detail", ""),
                suggestion="See anti-patterns.md — make the choice intentional or vary it",
            )
        )

    # Musicality warns
    for check_fn in (_check_contour, _check_interval_profile):
        d = check_fn(layer)
        if d:
            diagnostics.append(d)
    d = _check_expression_zero(layer, slot, resolved)
    if d:
        diagnostics.append(d)

    # Partition into blocking / warnings, honoring waivers
    for diag in diagnostics:
        if diag.check in waived:
            result.overrides.append(
                {"check": diag.check, "reason": waived[diag.check], "detail": diag.detail}
            )
            continue
        if diag.check in _DEFAULT_BLOCKING and diag.severity == "block":
            result.blocking.append(diag)
        else:
            result.warnings.append(diag)

    result.passed = not result.blocking
    return result


def _previous_realized(graph, phrase_id: str) -> Optional[LayerIR]:
    """The previous phrase's committed surface, for restatement detection."""
    state = graph.phrases.get(phrase_id)
    if state is None:
        return None
    order = graph.get_section_phrases(state.slot.section_id)
    if phrase_id in order:
        idx = order.index(phrase_id)
        if idx > 0:
            prev = graph.phrases.get(order[idx - 1])
            return prev.realized if prev else None
    return None
