"""Build per-composer distribution profiles from bar records.

For each composer, group bars by source movement, compute the
``corpus_metrics`` vector per movement, then aggregate across movements into
mean / stdev / min / max / percentiles. The result is a *distribution* of how
real movements behave (not a single pooled median), so a generated piece — one
"movement" — can be scored with a z-score per metric.

Writes ``compiled_packs/<composer>/corpus_profile.json``.

Usage:
    python3 -m scripts.build_corpus_profiles            # all composers w/ bars
    python3 -m scripts.build_corpus_profiles mozart bach
    python3 -m scripts.build_corpus_profiles --min-bars 8
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from scales.corpus_metrics import (
    SCALAR_METRICS,
    bar_metrics,
    l1_distance,
    texture_distribution,
)

from scripts.build_corpus_indexes import (
    all_composers_with_bars,
    group_by_source,
    load_bars,
)

_TOOLS = Path(__file__).resolve().parent.parent
COMPILED_PACKS = _TOOLS / "compiled_packs"

# Movements shorter than this are too small to yield a stable metric vector;
# they still count toward the pooled texture distribution.
_MIN_MOVEMENT_BARS = 6


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


def build_profile(composer: str, min_bars: int = _MIN_MOVEMENT_BARS) -> Optional[Dict[str, Any]]:
    bars = load_bars(composer)
    if not bars:
        return None
    groups = group_by_source(bars)

    pooled_lh = texture_distribution(bars, "lh")

    per_metric: Dict[str, List[float]] = {m: [] for m in SCALAR_METRICS}
    lh_l1_samples: List[float] = []  # each movement's LH-texture L1 to pooled
    movements_used = 0
    for src, mvt_bars in groups.items():
        if len(mvt_bars) < min_bars:
            continue
        metrics = bar_metrics(mvt_bars)
        for m in SCALAR_METRICS:
            per_metric[m].append(metrics[m])
        lh_l1_samples.append(l1_distance(texture_distribution(mvt_bars, "lh"), pooled_lh))
        movements_used += 1

    # Fallback: if a composer has no movement long enough, treat the whole
    # corpus as one sample so the profile still exists (stdev will be 0).
    if movements_used == 0:
        whole = bar_metrics(bars)
        for m in SCALAR_METRICS:
            per_metric[m].append(whole[m])
        movements_used = 1

    metric_stats = {m: _aggregate(v) for m, v in per_metric.items() if v}

    return {
        "composer": composer,
        "total_bars": len(bars),
        "total_movements": len(groups),
        "movements_used": movements_used,
        "min_movement_bars": min_bars,
        "metrics": metric_stats,
        "lh_texture_distribution": pooled_lh,
        "rh_texture_distribution": texture_distribution(bars, "rh"),
        # How far a single real movement's LH-texture mix sits from the pooled
        # corpus — so a generated piece's L1 is judged against real per-movement
        # spread, not naively against 0.
        "lh_l1_baseline": _aggregate(lh_l1_samples) if lh_l1_samples else {},
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    min_bars = _MIN_MOVEMENT_BARS
    if "--min-bars" in argv:
        i = argv.index("--min-bars")
        min_bars = int(argv[i + 1])
        del argv[i : i + 2]
    composers = argv or all_composers_with_bars()
    for composer in composers:
        profile = build_profile(composer, min_bars=min_bars)
        if profile is None:
            print(json.dumps({"composer": composer, "skipped": "no bars"}))
            continue
        out_path = COMPILED_PACKS / composer / "corpus_profile.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(profile, f, indent=1)
        print(
            json.dumps(
                {
                    "composer": composer,
                    "movements_used": profile["movements_used"],
                    "events_per_bar": profile["metrics"]["events_per_bar"]["mean"],
                    "texture_change_pct": profile["metrics"]["texture_change_pct"]["mean"],
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
