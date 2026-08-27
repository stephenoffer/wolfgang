"""Bar-record metrics — the shared yardstick for piece-vs-corpus comparison.

The point of this module is *apples-to-apples*: the exact same functions run
over real corpus bars (``reference_index/<composer>/bars*``) and over a
generated piece's bars (assembled to MusicXML, then re-extracted with
``build_full_corpus.analyze_score_bars``). Because both sides flow through the
identical metric definitions, a generated piece can be scored against the
distribution of real movements with a meaningful z-score.

NAMING — ``melody_direction_change_pct`` is the fraction of consecutive BARS
whose coarse melodic direction label changes (0-1). It is NOT
``musicality.direction_changes_per_bar``, which counts contour reversals per bar
(0-many). The two shared a name until 2026-08-18, so the commit gate told the
agent the corpus norm was "1.0-2.0" while the brief, reading the corpus profile,
said Beethoven's mean was 0.41 — the same label, two incomparable quantities,
contradicting each other in the same context window.

CONSTRAINT — only fields produced by BOTH paths may be used. Since the generated
side runs ``analyze_score_bars`` itself (see ``scales._extract_generated_bars``),
"both paths" means "whatever that function emits", which today includes
melody_density, accomp_density, rh_texture, lh_texture, melody_direction,
has_grace_notes, has_dotted_rhythms, has_rests, register_center, harmony_quality,
phrase_position, roman/function, melody_line and the rh/lh display event lists.
This note used to assert that ``has_rests`` and the event lists were NOT emitted
— they are, and have been — which kept silence out of the comparison entirely.
Silence is one of the strongest human/machine discriminators there is. Keep this
set in sync with ``analyze_score_bars`` if it changes.
"""

from __future__ import annotations

import statistics
from fractions import Fraction
from typing import Any, Dict, List, Tuple

# Metrics this module computes per bar-list. Kept as a module constant so the
# profile builder, compare_to_corpus, and self_evaluate agree on the set.
SCALAR_METRICS = [
    "events_per_bar",
    "events_per_bar_rh",
    "events_per_bar_lh",
    "texture_change_pct",
    "lh_texture_change_pct",
    "rh_texture_change_pct",
    "density_cv",
    "melody_direction_change_pct",
    "grace_ratio",
    "dotted_ratio",
    "register_span",
    "rest_bar_ratio",
    "rest_event_ratio",
]

_DENSITY_DELTA = 4  # note-count shift that counts as a texture change


def _total_densities(bars: List[Dict[str, Any]]) -> List[int]:
    return [int(b.get("melody_density", 0)) + int(b.get("accomp_density", 0)) for b in bars]


def _frac_changes(seq: List[Any]) -> float:
    if len(seq) < 2:
        return 0.0
    changes = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    return changes / (len(seq) - 1)


def bar_metrics(bars: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute the scalar metric vector for one bar-list (a movement or piece).

    Returns a dict over SCALAR_METRICS. Bar-lists shorter than 2 bars yield
    zeros for the delta-based metrics (no adjacency to measure).
    """
    n = len(bars)
    if n == 0:
        return {m: 0.0 for m in SCALAR_METRICS}

    md = [int(b.get("melody_density", 0)) for b in bars]
    ad = [int(b.get("accomp_density", 0)) for b in bars]
    total = [a + b for a, b in zip(md, ad, strict=True)]
    rh_tex = [b.get("rh_texture", "unclassified") for b in bars]
    lh_tex = [b.get("lh_texture", "unclassified") for b in bars]
    directions = [b.get("melody_direction", "static") for b in bars]
    registers = [float(b.get("register_center", 0)) for b in bars]

    # texture change = adjacent total-density shift >= delta
    if n >= 2:
        tex_shifts = sum(1 for a, b in zip(total, total[1:]) if abs(a - b) >= _DENSITY_DELTA)
        texture_change_pct = tex_shifts / (n - 1)
    else:
        texture_change_pct = 0.0

    mean_total = statistics.fmean(total) if total else 0.0
    density_cv = statistics.pstdev(total) / mean_total if mean_total > 0 and n >= 2 else 0.0

    return {
        "events_per_bar": round(mean_total, 3),
        "events_per_bar_rh": round(statistics.fmean(md), 3) if md else 0.0,
        "events_per_bar_lh": round(statistics.fmean(ad), 3) if ad else 0.0,
        "texture_change_pct": round(texture_change_pct, 4),
        "lh_texture_change_pct": round(_frac_changes(lh_tex), 4),
        "rh_texture_change_pct": round(_frac_changes(rh_tex), 4),
        "density_cv": round(density_cv, 4),
        "melody_direction_change_pct": round(_frac_changes(directions), 4),
        "grace_ratio": round(sum(1 for b in bars if b.get("has_grace_notes")) / n, 4),
        "dotted_ratio": round(sum(1 for b in bars if b.get("has_dotted_rhythms")) / n, 4),
        "register_span": round(max(registers) - min(registers), 2) if registers else 0.0,
        # Silence. Generated music's most consistent tell is that it never stops
        # playing: real Mozart rests somewhere in a majority of his bars.
        "rest_bar_ratio": round(sum(1 for b in bars if b.get("has_rests")) / n, 4),
        "rest_event_ratio": round(_rest_event_ratio(bars), 4),
    }


def _rest_event_ratio(bars: List[Dict[str, Any]]) -> float:
    """Fraction of notated events (both hands) that are rests."""
    rests = events = 0
    for b in bars:
        for key in ("rh_display", "rh_inner_display", "lh_display", "lh_inner_display"):
            for e in b.get(key) or []:
                events += 1
                if e.get("type") == "rest":
                    rests += 1
    return (rests / events) if events else 0.0


def texture_distribution(bars: List[Dict[str, Any]], hand: str = "lh") -> Dict[str, float]:
    """Normalized texture distribution over a bar-list (proportions sum to 1)."""
    key = f"{hand}_texture"
    counts: Dict[str, int] = {}
    for b in bars:
        t = b.get(key, "unclassified")
        counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values())
    if total == 0:
        return {}
    return {t: round(c / total, 4) for t, c in counts.items()}


def l1_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    """L1 distance between two distributions (0 identical, max 2 disjoint)."""
    keys = set(a) | set(b)
    return round(sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys), 4)


def zscore(value: float, mean: float, stdev: float) -> float:
    """Z-score with a stdev floor so near-constant metrics don't explode."""
    floor = max(stdev, 1e-6)
    return round((value - mean) / floor, 2)


# ── Vertical sonority ────────────────────────────────────────────────────────
#
# "Does this staff notate a chord" is a KEYBOARD question. Asked of four
# independent voice streams it is a category error: a chorale's chords are
# vertical alignments ACROSS streams, and every one of Bach's arrives as its own
# single-note event. `avg_chord_size` reads a `type` field, so it found chords in
# 39 of his 470 movements — those where his keyboard writing happens to notate
# one in a hand — and reported 0.171 for the rest, which is not a size.
#
# More than half of Bach's notes and 55% of Palestrina's live in the INNER
# streams, which the old measure never read at all.
#
# So: reconstruct each stream's onsets by walking its durations, then ask how
# many pitches are sounding at each attack. That question has the same meaning
# for a piano chord and for four voices arriving together, which is the point.

_DISPLAY_STREAMS = ("rh_display", "rh_inner_display", "lh_display", "lh_inner_display")


def _stream_spans(bar: Dict[str, Any]) -> List[Tuple[Fraction, Fraction, str]]:
    """(start, end, pitch) for every sounding note in a bar, across all streams."""
    spans: List[Tuple[Fraction, Fraction, str]] = []
    for stream in _DISPLAY_STREAMS:
        cursor = Fraction(0)
        for event in bar.get(stream) or []:
            if event.get("is_grace"):
                continue  # a grace takes no metric time
            try:
                dur = Fraction(str(event.get("dur", 0))).limit_denominator(64)
            except (TypeError, ValueError):
                continue
            if dur <= 0:
                continue
            if event.get("type") != "rest":
                pitches = event.get("pitches") or ([event["pitch"]] if event.get("pitch") else [])
                for pitch in pitches:
                    spans.append((cursor, cursor + dur, str(pitch)))
            cursor += dur
    return spans


def sonority_metrics(bars: List[Dict[str, Any]]) -> Dict[str, float]:
    """How many notes sound together, measured across every voice stream.

    `mean_sonority` is the average number of pitches sounding at an attack;
    `chorded_attack_pct` the share of attacks where more than one does. Both are
    defined for a piano chord and for four independent voices, which is what
    makes them comparable across the corpus.
    """
    total = 0
    sounding = 0
    chorded = 0
    for bar in bars:
        spans = _stream_spans(bar)
        if not spans:
            continue
        for attack, _end, _pitch in sorted({(s, e, p) for s, e, p in spans}):
            here = {p for s, e, p in spans if s <= attack < e}
            if not here:
                continue
            total += 1
            sounding += len(here)
            if len(here) > 1:
                chorded += 1
    if not total:
        return {"mean_sonority": 0.0, "chorded_attack_pct": 0.0, "attacks": 0}
    return {
        "mean_sonority": round(sounding / total, 3),
        "chorded_attack_pct": round(100 * chorded / total, 2),
        "attacks": total,
    }
