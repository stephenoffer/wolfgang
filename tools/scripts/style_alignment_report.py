"""Every closed finding's probe, re-run together, against member-level targets.

A dimension you close stops being measured and therefore has no guard. Two
sessions spent a day finding defects one at a time, and each fix was verified
against the dimensions that fix was about — texture agreement for a texture
change, duration vocabulary for a notation change. A contour finding closed
early in the day silently regressed hours later (turns per bar 3.0 back to 2.0)
because nothing re-ran its probe: the piece is one artefact and everything moves
everything.

So this runs the whole set. Each row compares a generated piece to the MEDIAN
MOVEMENT of the target composer, never to a pooled corpus figure — the pooled
mean is right about a population no single piece belongs to, which is the error
that cost both sessions the most (see `corpus_metrics`' module docstring).

    .venv/bin/python -m scripts.style_alignment_report <piece-id> <composer>

Deliberately NOT a pass/fail gate. Several rows have no defensible bound (a
composer's own spread is wide, and real music covers it), and a bound guessed
from a correctly-scoped number was itself one of the day's defects. It prints
the piece, the median movement, and the composer's own p25-p75 so a reader can
see which differences are outside real practice and which are style.
"""

from __future__ import annotations

import json
import statistics
import sys
import warnings
from typing import Any, Dict, List, Optional, Tuple

warnings.filterwarnings("ignore")


def _median_movement(composer: str, fn, min_bars: int = 24) -> Optional[Dict[str, float]]:
    """Per-metric median and quartiles over the composer's own movements."""
    from scripts.build_corpus_indexes import group_by_source, load_bars

    rows: List[Dict[str, float]] = []
    for _src, bars in group_by_source(load_bars(composer)).items():
        if len(bars) < min_bars:
            continue
        try:
            rows.append(fn(bars))
        except Exception:
            continue
    if len(rows) < 4:
        return None
    out: Dict[str, float] = {}
    for key in rows[0]:
        vals = sorted(float(r.get(key, 0.0) or 0.0) for r in rows)
        out[key] = statistics.median(vals)
        out[f"{key}__p25"] = vals[len(vals) // 4]
        out[f"{key}__p75"] = vals[(3 * len(vals)) // 4]
    return out


def _generated_bars(piece_id: str, composer: str):
    import music21
    from scales.assembler import assemble
    from scales.scales import _load_graph

    from scripts.build_full_corpus import analyze_score_bars

    score = music21.converter.parse(assemble(_load_graph(piece_id), scope="full"))
    return analyze_score_bars(score, composer, piece_id)


#: (label, callable over bars -> dict, metrics to print). Every entry is a
#: finding someone closed today; the point is that they are re-run TOGETHER.
def _probes():
    from scales.corpus_metrics import median_bar_chord_share
    from scales.style_dimensions import melodic_metrics, rhythmic_metrics

    def contour(bars):
        return melodic_metrics(bars)

    def rhythm(bars):
        return rhythmic_metrics(bars)

    def extents(bars):
        """How often a hand falls silent before the barline, and by how much."""
        out = {}
        for hand, field in (("rh", "rh_display"), ("lh", "lh_display")):
            short = long_ = n = 0
            for bar in bars:
                events = bar.get(field) or []
                if not events:
                    continue
                total = last = 0.0
                for e in events:
                    total += float(e.get("dur", 0) or 0)
                    if e.get("type") != "rest":
                        last = total
                if total <= 0:
                    continue
                n += 1
                gap = total - last
                short += 1e-6 < gap <= 0.5
                long_ += gap > 1.0
            out[f"{hand}_short_gap_share"] = short / n if n else 0.0
            out[f"{hand}_long_gap_share"] = long_ / n if n else 0.0
        return out

    def lh_vocabulary(bars):
        """Distinct left-hand pitches per bar, and the median bar's chord share."""
        counts = []
        for bar in bars:
            pitches = set()
            for e in bar.get("lh_display") or []:
                if e.get("type") == "rest":
                    continue
                for p in e.get("pitches") or [e.get("pitch")]:
                    if p:
                        pitches.add(p)
            if pitches:
                counts.append(len(pitches))
        shares = median_bar_chord_share(bars)
        return {
            "lh_distinct_pitches_per_bar": statistics.fmean(counts) if counts else 0.0,
            "chordal_median_bar_chord_share": shares.get("block_chord_sparse", 0.0),
        }

    return [
        ("contour", contour, ("step_ratio", "leap_ratio", "repeat_ratio", "mean_abs_interval")),
        ("rhythm", rhythm, ("dur_variety", "quarter_ratio", "eighth_ratio")),
        ("extent", extents, ("rh_short_gap_share", "rh_long_gap_share", "lh_short_gap_share")),
        (
            "left hand",
            lh_vocabulary,
            ("lh_distinct_pitches_per_bar", "chordal_median_bar_chord_share"),
        ),
    ]


def report(piece_id: str, composer: str) -> Dict[str, Any]:
    bars = _generated_bars(piece_id, composer)
    rows: List[Tuple[str, str, float, Optional[float], Optional[float], Optional[float]]] = []
    for label, fn, keys in _probes():
        try:
            ours = fn(bars)
        except Exception as exc:  # a probe that cannot run must say so
            rows.append((label, f"<probe failed: {exc}>", 0.0, None, None, None))
            continue
        real = _median_movement(composer, fn)
        for key in keys:
            got = float(ours.get(key, 0.0) or 0.0)
            if real is None:
                rows.append((label, key, got, None, None, None))
            else:
                rows.append(
                    (
                        label,
                        key,
                        got,
                        real.get(key),
                        real.get(f"{key}__p25"),
                        real.get(f"{key}__p75"),
                    )
                )
    return {"piece": piece_id, "composer": composer, "bars": len(bars), "rows": rows}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2:
        print(
            json.dumps({"usage": "python -m scripts.style_alignment_report <piece-id> <composer>"})
        )
        return 2
    piece_id, composer = argv[0], argv[1]
    result = report(piece_id, composer)
    print(f"\n{result['piece']}  vs  {composer}'s median movement   ({result['bars']} bars)\n")
    print(f"{'':10s} {'metric':34s} {'ours':>9s} {'median':>9s} {'p25':>8s} {'p75':>8s}  outside?")
    for label, key, got, med, p25, p75 in result["rows"]:
        if med is None:
            print(f"{label:10s} {key:34s} {got:9.3f} {'-':>9s} {'-':>8s} {'-':>8s}")
            continue
        flag = "" if (p25 is not None and p25 <= got <= p75) else "  <-- outside p25-p75"
        print(f"{label:10s} {key:34s} {got:9.3f} {med:9.3f} {p25:8.3f} {p75:8.3f}{flag}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
