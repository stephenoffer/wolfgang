"""Build aggregated corpus profiles + density stats for STYLE references.

A style (``classical``, ``baroque``, …) is a set of composers. To compare a
generated piece against a *style* — not a single composer — we aggregate every
armed member's movements into one distribution, written under
``compiled_packs/style__<name>/`` so the same machinery that scores against a
composer scores against the style.

Reuses the style-aware ``_iter_corpus_bars`` (composition_brief) for bars and
``texture_density_stats`` for the gate floors. Run after acquiring composers,
or whenever membership changes.

Usage:
    python3 -m scripts.build_style_profiles            # all styles with members
    python3 -m scripts.build_style_profiles classical baroque
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional

from scales.atomic_io import write_json_atomic
from scales.composition_brief import _iter_corpus_bars, texture_density_stats
from scales.corpus_metrics import (
    SCALAR_METRICS,
    bar_metrics,
    l1_distance,
    sonority_metrics,
    texture_distribution,
)
from scales.style_dimensions import FINGERPRINT_FEATURES, style_fingerprint
from scales.style_registry import (
    available_styles,
    make_style_id,
    style_members,
)

_TOOLS = Path(__file__).resolve().parent.parent
COMPILED_PACKS = _TOOLS / "compiled_packs"
_MIN_MOVEMENT_BARS = 6

# The SAME feature vector `build_corpus_profiles` builds for a composer. This
# file aggregated `SCALAR_METRICS` alone — 13 of the 39 — so a style profile
# described texture and rhythm and said nothing about harmony, melody or how
# many notes sound together. `compare_to_corpus` scores a piece on whatever the
# profile carries, so composing "in the classical style" was judged on a third
# of the dimensions a named composer is judged on, and the missing two thirds
# were exactly the ones that separate one classical composer from another.
_SONORITY_FEATURES = ("mean_sonority", "chorded_attack_pct")
_ALL_FEATURES = list(SCALAR_METRICS) + list(FINGERPRINT_FEATURES) + list(_SONORITY_FEATURES)


def _aggregate(values: List[float]) -> Dict[str, float]:
    vals = sorted(values)
    n = len(vals)
    out = {
        "mean": round(statistics.fmean(vals), 4),
        "stdev": round(statistics.pstdev(vals), 4) if n >= 2 else 0.0,
        "min": round(vals[0], 4),
        "max": round(vals[-1], 4),
        "n": n,
    }
    if n >= 4:
        out["p25"] = round(vals[n // 4], 4)
        out["p50"] = round(statistics.median(vals), 4)
        out["p75"] = round(vals[(3 * n) // 4], 4)
    return out


def _group_by_source(bars: List[Dict[str, Any]]) -> "OrderedDict[str, List[Dict]]":
    groups: "OrderedDict[str, List[Dict]]" = OrderedDict()
    for bar in bars:
        groups.setdefault(bar.get("source", "?"), []).append(bar)
    return groups


def build_style_profile(style: str, min_bars: int = _MIN_MOVEMENT_BARS) -> Optional[Dict[str, Any]]:
    members = style_members(style)
    if not members:
        return None
    style_id = make_style_id(style)
    bars = list(_iter_corpus_bars(style_id))
    if not bars:
        return None
    groups = _group_by_source(bars)
    pooled_lh = texture_distribution(bars, "lh")

    per_metric: Dict[str, List[float]] = {m: [] for m in _ALL_FEATURES}
    lh_l1_samples: List[float] = []
    movements_used = 0
    for src, mvt_bars in groups.items():
        if len(mvt_bars) < min_bars:
            continue
        metrics = {
            **bar_metrics(mvt_bars),
            **style_fingerprint(mvt_bars),
            **sonority_metrics(mvt_bars),
        }
        for m in _ALL_FEATURES:
            per_metric[m].append(metrics.get(m, 0.0))
        lh_l1_samples.append(l1_distance(texture_distribution(mvt_bars, "lh"), pooled_lh))
        movements_used += 1

    if movements_used == 0:  # fallback: whole style as one sample
        whole = {**bar_metrics(bars), **style_fingerprint(bars), **sonority_metrics(bars)}
        for m in _ALL_FEATURES:
            per_metric[m].append(whole.get(m, 0.0))
        movements_used = 1

    return {
        "composer": style_id,
        "style": style,
        "members": members,
        "total_bars": len(bars),
        "total_movements": len(groups),
        "movements_used": movements_used,
        "min_movement_bars": min_bars,
        "metrics": {m: _aggregate(v) for m, v in per_metric.items() if v},
        "lh_texture_distribution": pooled_lh,
        "rh_texture_distribution": texture_distribution(bars, "rh"),
        "lh_l1_baseline": _aggregate(lh_l1_samples) if lh_l1_samples else {},
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    styles = argv or [s["style"] for s in available_styles()]
    for style in styles:
        profile = build_style_profile(style)
        if profile is None:
            print(json.dumps({"style": style, "skipped": "no armed members"}))
            continue
        style_id = make_style_id(style)
        out_dir = COMPILED_PACKS / style_id
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json_atomic(out_dir / "corpus_profile.json", profile, indent=1)
        # density stats (gate floors) for the style, via style-aware iterator
        texture_density_stats(style_id, refresh=True)
        print(
            json.dumps(
                {
                    "style": style,
                    "id": style_id,
                    "members": profile["members"],
                    "movements_used": profile["movements_used"],
                    "total_bars": profile["total_bars"],
                    "events_per_bar": profile["metrics"]["events_per_bar"]["mean"],
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
