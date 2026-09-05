"""
Musicality — cheap symbolic metrics over a LayerIR.

Used by the commit gate and section review to measure properties the
structural validators can't see: rhythmic life, melodic shape, figuration
richness. All functions are pure, O(n) per phrase, and return
``(score, detail)`` where score is 0-1 (higher = more musical) and detail
is a dict explaining the number so diagnostics can cite it.

These are *measurements*, not rules. Thresholding and artistic judgment
live in commit_gate.py and the review skills.
"""

from __future__ import annotations

import math
from collections import Counter
from itertools import pairwise
from typing import Any

from .duration import dur_to_beats
from .models import ALL_LAYERS, LOWER_LAYERS, UPPER_LAYERS, LayerEvent, LayerIR
from .pitch import pitch_to_midi

# ─── Helpers ─────────────────────────────────────────────────────────────────

# These listed only the five piano layers, so every metric in this module —
# rhythmic variety, interval profile, figuration richness, contour, rest ratio —
# measured an ORCHESTRAL piece as having no notes and returned a clean bill of
# health rather than an error. Now the model's own grouping, so an added layer
# joins every reader at once.
_PIANO_LAYERS = ALL_LAYERS
_RH_LAYERS = UPPER_LAYERS
_LH_LAYERS = LOWER_LAYERS


def _events(layer: LayerIR, layer_names=ALL_LAYERS) -> list[LayerEvent]:
    out: list[LayerEvent] = []
    for name in layer_names:
        out.extend(getattr(layer, name, None) or [])
    return out


def _is_rest(event: LayerEvent) -> bool:
    return event.pitch == "rest" or event.pitch is None


def _event_midis(event: LayerEvent) -> list[int]:
    """MIDI pitches for an event; chords yield all members."""
    if _is_rest(event):
        return []
    pitches = event.pitch if isinstance(event.pitch, list) else [event.pitch]
    midis = []
    for p in pitches:
        if p == "rest":
            continue
        try:
            m = pitch_to_midi(p)
        except (ValueError, KeyError, TypeError):
            continue
        # pitch_to_midi RETURNS None for an unparseable pitch (it does not
        # always raise); a None here would later crash interval/contour math
        # (`line[i+1] - line[i]`) and take down the whole commit gate.
        if m is not None:
            midis.append(m)
    return midis


def _melody_line(layer: LayerIR) -> list[int]:
    """Top-note melodic line from principal_line, in time order."""
    events = sorted(layer.principal_line, key=lambda e: (e.bar, e.beat))
    line = []
    for e in events:
        midis = _event_midis(e)
        if midis:
            line.append(max(midis))  # top note carries the melody
    return line


def _melody_intervals(layer: LayerIR) -> list[int]:
    line = _melody_line(layer)
    return [line[i + 1] - line[i] for i in range(len(line) - 1)]


def events_per_bar(layer: LayerIR, hand: str = "rh") -> float:
    """Mean sounding events per bar for one hand.

    Counts *events* (a chord = 1 event) to stay comparable with the
    corpus ``melody_density`` / ``accomp_density`` fields, which count
    events the same way.
    """
    names = _RH_LAYERS if hand == "rh" else _LH_LAYERS
    sounding = [e for e in _events(layer, names) if not _is_rest(e)]
    bars = max(1, layer.bar_count)
    return len(sounding) / bars


# ─── Metrics ─────────────────────────────────────────────────────────────────


def rhythmic_variety(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Normalized entropy of the duration multiset across all layers.

    A phrase written entirely in quarters scores ~0; a phrase mixing
    8 distinct duration values with reasonable balance scores ~1.
    """
    durs = [e.duration for e in _events(layer) if not _is_rest(e)]
    detail: dict[str, Any] = {"counts": dict(Counter(durs)), "distinct": 0}
    if not durs:
        return 0.0, detail
    counts = Counter(durs)
    detail["distinct"] = len(counts)
    total = len(durs)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values())
    # MEASURED on 20 real movements: 1.24-2.69 bits, median 1.95, using 5-12
    # distinct duration values. Normalizing by log2(8)=3 bits made a full score
    # unreachable by any real music — the richest movement measured topped out
    # at 0.90 and the median scored 0.65. 2.7 bits is what the repertoire's own
    # ceiling actually is.
    score = min(1.0, entropy / 2.7)
    detail["entropy_bits"] = round(entropy, 3)
    return round(score, 3), detail


def melodic_smoothness(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Stepwise ratio of the principal line (|interval| <= 2 semitones)."""
    intervals = _melody_intervals(layer)
    detail: dict[str, Any] = {"interval_count": len(intervals)}
    if not intervals:
        return 0.0, detail
    stepwise = sum(1 for i in intervals if abs(i) <= 2)
    ratio = stepwise / len(intervals)
    detail["stepwise_ratio"] = round(ratio, 3)
    return round(ratio, 3), detail


_INTERVAL_PRIOR_CACHE: dict[str, dict[str, float] | None] = {}

#: Used only when a composer's own distribution is unmeasurable.
_GENERIC_INTERVAL_PRIOR = {"stepwise": 0.65, "small_leap": 0.25, "large_leap": 0.10}


def composer_interval_priors(composer: str) -> dict[str, float] | None:
    """This composer's own interval distribution, in the bands used below.

    The generic prior (65/25/10) is what every phrase was scored against, and it
    describes nobody. Measured over the corpus in these same bands:

        palestrina 0.813   bach 0.611*   mozart 0.611   haydn 0.600
        beethoven  0.538   chopin 0.498  liszt 0.358        (* bach 0.736)

    It is far too stepwise for Liszt — whose real rate is 0.358, less than half
    the prior — and not stepwise enough for Palestrina. Its large-leap figure of
    0.10 is off by nearly four times for Liszt, at 0.377.

    That matters because this runs at COMMIT time: it was telling a romantic
    phrase to aim for 65% stepwise motion while `score_realism` told the
    finished piece it was too scalar and the brief told the composer the line
    should leap. Three subsystems, three different answers, one of them a
    constant.

    Returns None when the composer has no usable corpus, in which case the
    caller keeps the generic prior — which is the honest fallback, not a
    silently wrong composer.
    """
    key = (composer or "").strip().lower()
    if not key:
        return None
    if key in _INTERVAL_PRIOR_CACHE:
        return _INTERVAL_PRIOR_CACHE[key]
    priors: dict[str, float] | None = None
    try:
        import itertools as _it

        from .composition_brief import _iter_corpus_bars

        step = small = large = 0
        for bar in _it.islice(_iter_corpus_bars(key), 4000):
            line = [
                e.get("midi")
                for e in (bar.get("melody_line") or [])
                if isinstance(e, dict) and e.get("midi") is not None
            ]
            for a, b in _it.pairwise(line):
                distance = abs(int(b) - int(a))
                if distance <= 2:
                    step += 1
                elif distance <= 5:
                    small += 1
                else:
                    large += 1
        total = step + small + large
        if total >= 200:  # below this the shape is noise, not a prior
            priors = {
                "stepwise": round(step / total, 4),
                "small_leap": round(small / total, 4),
                "large_leap": round(large / total, 4),
            }
    except Exception:
        priors = None
    _INTERVAL_PRIOR_CACHE[key] = priors
    return priors


def melodic_interval_profile(
    layer: LayerIR,
    priors: dict[str, float] | None = None,
) -> tuple[float, dict[str, Any]]:
    """Distance between the phrase's interval distribution and composer priors.

    ``priors`` maps category → proportion, categories: stepwise (<=2 st),
    small_leap (3-5 st), large_leap (>5 st). Defaults to a generic tonal
    profile (65/25/10) when no composer prior is available.
    """
    if priors is None:
        priors = dict(_GENERIC_INTERVAL_PRIOR)
    intervals = _melody_intervals(layer)
    detail: dict[str, Any] = {"priors": priors, "interval_count": len(intervals)}
    if not intervals:
        return 0.0, detail
    n = len(intervals)
    actual = {
        "stepwise": sum(1 for i in intervals if abs(i) <= 2) / n,
        "small_leap": sum(1 for i in intervals if 2 < abs(i) <= 5) / n,
        "large_leap": sum(1 for i in intervals if abs(i) > 5) / n,
    }
    detail["actual"] = {k: round(v, 3) for k, v in actual.items()}
    l1 = sum(abs(actual[k] - priors.get(k, 0.0)) for k in actual)
    score = max(0.0, 1.0 - l1 / 2.0)
    detail["l1_distance"] = round(l1, 3)
    return round(score, 3), detail


def figuration_richness(
    layer: LayerIR,
    density_stats: dict[str, Any] | None = None,
    texture: str | None = None,
    hand: str = "rh",
) -> tuple[float, dict[str, Any]]:
    """Events/bar for one hand vs the corpus median for the target texture.

    ``density_stats`` is the per-texture stats dict produced by
    composition_brief.texture_density_stats(); ``texture`` selects the entry.
    Without stats, the fallback is the MEASURED real-corpus median (RH 5.2,
    LH 4.3 events per bar over 20 movements). The previous fallback of RH 6.0 /
    LH 5.5 came from a doc rather than from measurement and asked for a busier
    bar than the repertoire's own median, so a correctly spare Classical texture
    scored as under-figured.
    """
    actual = events_per_bar(layer, hand=hand)
    detail: dict[str, Any] = {"events_per_bar": round(actual, 2), "hand": hand}

    median = None
    p25 = None
    if density_stats and texture:
        entry = density_stats.get(texture)
        if entry:
            median = entry.get("median")
            p25 = entry.get("p25")
            detail["corpus_texture"] = texture
            detail["corpus_median"] = median
            detail["corpus_p25"] = p25
    if median is None:
        median = 5.2 if hand == "rh" else 4.3
        detail["corpus_median"] = median
        detail["fallback"] = "measured real-corpus median (20 movements)"

    score = min(1.0, actual / median) if median > 0 else 0.0
    detail["ratio_to_median"] = round(actual / median, 2) if median else None
    return round(score, 3), detail


def voice_leading_smoothness(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Mean melodic motion of the principal line, penalizing leap chains.

    Mean |interval| of ~2 semitones is singable; consecutive runs of
    leaps > P5 read as instrumental fragmentation.
    """
    intervals = _melody_intervals(layer)
    detail: dict[str, Any] = {"interval_count": len(intervals)}
    if not intervals:
        return 0.0, detail
    mean_abs = sum(abs(i) for i in intervals) / len(intervals)
    detail["mean_abs_interval"] = round(mean_abs, 2)
    # 1.0 at <=2.5 st mean motion, 0.0 at >=8 st
    base = max(0.0, min(1.0, (8.0 - mean_abs) / 5.5))
    # Penalize chains of consecutive large leaps
    chain = max_chain = 0
    for i in intervals:
        chain = chain + 1 if abs(i) > 7 else 0
        max_chain = max(max_chain, chain)
    detail["max_consecutive_large_leaps"] = max_chain
    penalty = 0.15 * max(0, max_chain - 1)
    score = max(0.0, base - penalty)
    return round(score, 3), detail


def direction_changes_per_bar(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Melodic contour direction changes per bar.

    MEASURED on 20 real movements (Mozart, Beethoven, Chopin sonatas and
    mazurkas, 2026-08-26): median **2.05** changes per bar, range 1.03-6.97.
    The band used to be 1.0-2.0, which put the repertoire's median at its top
    edge and scored the most active real movement measured at 0.3 — the score
    penalized real music for having a lively melodic line. Monotonic lines are
    the actual AI signature and still score low.
    """
    intervals = [i for i in _melody_intervals(layer) if i != 0]
    bars = max(1, layer.bar_count)
    changes = sum(1 for a, b in pairwise(intervals) if (a > 0) != (b > 0))
    rate = changes / bars
    detail = {"changes": changes, "bars": bars, "per_bar": round(rate, 2)}
    if 1.0 <= rate <= 3.5:
        score = 1.0
    elif rate < 1.0:
        score = rate  # 0 changes → 0
    else:
        # Gentle taper: 7 changes/bar is real (fast figuration), not a defect.
        score = max(0.6, 1.0 - (rate - 3.5) * 0.08)
    return round(score, 3), detail


def rest_ratio(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Fraction of total event time that is rests — does the music breathe?

    MEASURED on 20 real movements: median **16.3%** of event time is rest,
    range 2.7-27.0%. The band used to be 3-15%, so the repertoire's own median
    sat OUTSIDE it and typical real music was marked down for breathing a normal
    amount. Zero rests remains a classic AI tell and still scores near 0.
    """
    rest_beats = 0.0
    total_beats = 0.0
    for e in _events(layer):
        beats = dur_to_beats(e.duration)
        total_beats += beats
        if _is_rest(e):
            rest_beats += beats
    detail: dict[str, Any] = {
        "rest_beats": round(rest_beats, 2),
        "total_beats": round(total_beats, 2),
    }
    if total_beats <= 0:
        return 0.0, detail
    ratio = rest_beats / total_beats
    detail["ratio"] = round(ratio, 3)
    if 0.025 <= ratio <= 0.28:
        score = 1.0
    elif ratio < 0.025:
        score = max(0.0, ratio / 0.025) * 0.7  # zero rests scores 0
    else:
        score = max(0.3, 1.0 - (ratio - 0.28) * 2.0)
    return round(score, 3), detail


def density_cv(layer: LayerIR) -> tuple[float, dict[str, Any]]:
    """Per-bar density coefficient of variation (RH+LH events per bar),
    mirroring corpus_metrics.density_cv exactly so piece-vs-corpus is
    apples-to-apples.

    Low CV == flat, metronomic density bar after bar — the loudest mechanical
    tell. Real music breathes: it thickens at peaks and thins at cadences.
    Returns (cv, detail). CV is 0.0 for <2 bars (no variation to measure).
    """
    import statistics

    counts: dict[int, int] = {}
    bars_seen = set()
    for e in _events(layer):
        bars_seen.add(e.bar)
        if _is_rest(e):
            continue
        counts[e.bar] = counts.get(e.bar, 0) + 1
    detail: dict[str, Any] = {"per_bar": [], "bar_count": 0}
    if not bars_seen:
        return 0.0, detail
    b0, b1 = min(bars_seen), max(bars_seen)
    per_bar = [counts.get(b, 0) for b in range(b0, b1 + 1)]  # interior 0-bars count
    detail["per_bar"] = per_bar
    detail["bar_count"] = len(per_bar)
    if len(per_bar) < 2:
        return 0.0, detail
    mean = statistics.fmean(per_bar)
    if mean <= 0:
        return 0.0, detail
    cv = statistics.pstdev(per_bar) / mean
    detail["mean"] = round(mean, 3)
    return round(cv, 4), detail


def summarize(
    layer: LayerIR,
    density_stats: dict[str, Any] | None = None,
    rh_texture: str | None = None,
    lh_texture: str | None = None,
    priors: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Run all metrics; returns {metric: {score, detail}} for gate/review use."""
    results = {
        "rhythmic_variety": rhythmic_variety(layer),
        "melodic_smoothness": melodic_smoothness(layer),
        "melodic_interval_profile": melodic_interval_profile(layer, priors),
        "figuration_richness_rh": figuration_richness(layer, density_stats, rh_texture, hand="rh"),
        "figuration_richness_lh": figuration_richness(layer, density_stats, lh_texture, hand="lh"),
        "voice_leading_smoothness": voice_leading_smoothness(layer),
        "direction_changes_per_bar": direction_changes_per_bar(layer),
        "rest_ratio": rest_ratio(layer),
    }
    return {name: {"score": score, "detail": detail} for name, (score, detail) in results.items()}
