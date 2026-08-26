"""Build per-composer Roman-numeral progression models from the corpus.

Harmony plans were hard-coded I-IV-V templates (`scales._default_harmony_plan`).
This learns idiomatic progressions from the P1 per-bar `roman` field: an order-2
Markov over roman transitions, bucketed by key mode, with phrase-start and
cadence-target distributions. Mirrors `build_corpus_profiles.py`.

Writes `compiled_packs/<composer>/progression_model.json`.

Usage:
    python3 -m scripts.build_progression_model              # all composers w/ romans
    python3 -m scripts.build_progression_model mozart beethoven
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from scales.harmony_analysis import parse_roman, spell_roman

from scripts.build_corpus_indexes import all_composers_with_bars, group_by_source, load_bars

_TOOLS = Path(__file__).resolve().parent.parent
COMPILED_PACKS = _TOOLS / "compiled_packs"


def norm_roman(fig: Optional[str], mode: str = "major") -> Optional[str]:
    """Canonical form of a Roman numeral, INVERSION AND SEVENTH INTACT.

    This used to strip every digit ("V7" -> "V", "I64" -> "I", "ii65" -> "ii"),
    so the learned model contained no sevenths and no inversions at all: every
    progression it could produce was a chain of root-position triads, which is
    the one thing common-practice harmony never is. The bass line that results
    leaps between roots instead of stepping, and the dominant never sounds like
    a dominant.
    """
    if not fig:
        return None
    parsed = parse_roman(str(fig).strip(), mode)
    if not parsed:
        return None
    return spell_roman(
        int(parsed["degree"]), str(parsed["quality"]), int(parsed["inversion"]), 0, mode
    )


def _beat_count(bar) -> int:
    ts = bar.get("time_sig") or [4, 4]
    try:
        num, den = int(ts[0]), int(ts[1])
    except (TypeError, ValueError):
        return 4
    if den == 8 and num in (6, 9, 12):
        return num // 3
    return max(1, num)


def _runs(bars, mode):
    """Contiguous runs of bars in one mode from one source, in bar order.

    Filtering a movement down to its major-key bars and then reading the result
    as a sequence invents transitions across every modulation: the last bar
    before a minor-key episode appeared to move directly to the first bar after
    it. A progression model built from that learns chord successions nobody
    wrote.
    """
    out = []
    for _src, mb in group_by_source(bars).items():
        run = []
        for b in sorted(mb, key=lambda x: x.get("bar_num", 0)):
            if b.get("key_mode") != mode or not b.get("roman"):
                if run:
                    out.append(run)
                    run = []
                continue
            if run and b.get("bar_num", 0) != run[-1].get("bar_num", 0) + 1:
                out.append(run)
                run = []
            run.append(b)
        if run:
            out.append(run)
    return out


def _bars_for(reference: str) -> List[Dict[str, Any]]:
    """Bar records for a composer OR a style.

    `load_bars` reads one composer's own directory. A style id
    (`style__classical`) has no directory of its own — it aggregates over its
    member composers at read time — so building a progression model for a style
    silently found nothing and every style fell back to hard-coded I-IV-V
    templates. Composing "in the Classical style" rather than "as Mozart" is a
    first-class mode of this system, and it had no corpus harmony at all.
    """
    from scales.style_registry import is_style_id, style_members

    if not is_style_id(reference):
        return load_bars(reference)
    bars: List[Dict[str, Any]] = []
    for member in style_members(reference, armed_only=True):
        member_bars = load_bars(member)
        # Keep the source tag distinct per member so `_runs` never splices one
        # composer's cadence onto another's approach chord.
        for b in member_bars:
            b = dict(b)
            b["source"] = f"{member}:{b.get('source', '')}"
            bars.append(b)
    return bars


def build_model(composer: str, order: int = 2, min_bars: int = 6) -> Optional[Dict[str, Any]]:
    bars = _bars_for(composer)
    if not bars:
        return None
    by_mode: Dict[str, Dict[str, Any]] = {}
    total = 0
    for mode in ("major", "minor"):
        trans: Dict[str, Counter] = defaultdict(Counter)
        trans1: Dict[str, Counter] = defaultdict(Counter)
        uni: Counter = Counter()
        starts: Counter = Counter()
        cadence_targets: Dict[str, Counter] = {"PAC": Counter(), "HC": Counter(), "IAC": Counter()}
        mode_bars = [b for b in bars if b.get("key_mode") == mode and b.get("roman")]
        for run in _runs(bars, mode):
            seq = [norm_roman(b.get("roman"), mode) for b in run]
            pairs = [(r, b) for r, b in zip(seq, run) if r]
            if len(pairs) < min_bars:
                continue
            seq = [r for r, _ in pairs]
            starts[seq[0]] += 1
            for r in seq:
                uni[r] += 1
            for i in range(1, len(seq)):
                trans1[seq[i - 1]][seq[i]] += 1
            for i in range(order, len(seq)):
                ctx = "|".join(seq[i - order : i])
                trans[ctx][seq[i]] += 1
                total += 1
            # Cadences are PHRASE endings, not just the last bar of a movement.
            # Training on movement ends gave ~30 samples per composer and made
            # the commonest "approach to a final tonic" the tonic itself, so
            # sampled phrases ended I-I: no dominant, no cadence, nothing to
            # resolve. Every bar the extractor marks "cadential" or "closing" is
            # a cadence, which is thousands of samples.
            for i in range(1, len(seq)):
                pos = pairs[i][1].get("phrase_position")
                if pos not in ("cadential", "closing"):
                    continue
                pen, last = seq[i - 1], seq[i]
                base = last.rstrip("0123456789")
                if base in ("I", "i") and pen.rstrip("0123456789") not in ("I", "i"):
                    cadence_targets["PAC" if last in ("I", "i") else "IAC"][pen] += 1
                elif base in ("V", "v"):
                    cadence_targets["HC"][pen] += 1
        # WITHIN-BAR patterns, keyed by the bar's BEAT COUNT. They used to be
        # keyed by how many chords the bar contained, and then looked up by beat
        # count — so every 4/4 bar was handed a pattern that changes chord four
        # times and every 3/4 bar one that changes three times. The result was a
        # chord frame that moves harmony on every single beat of every single
        # bar, which no composer in this corpus writes.
        within: Dict[str, Counter] = defaultdict(Counter)
        moved: Counter = Counter()
        seen_bars: Counter = Counter()
        for b in mode_bars:
            beats = str(_beat_count(b))
            seen_bars[beats] += 1
            evs = [norm_roman(e.get("roman"), mode) for e in (b.get("harmony_events") or [])]
            evs = [e for e in evs if e]
            if len(evs) < 2:
                continue
            moved[beats] += 1
            within[beats]["|".join(evs)] += 1
        # Prune the long tail. A Roman numeral seen twice in 7,000 bars is an
        # analysis artefact, not vocabulary: sampling from the raw distribution
        # put "vo", "II+" and "biio6" into ordinary phrase plans, and the brief
        # then told the agent to write an augmented supertonic in a Mozart
        # andante. Everything the composer really uses survives a floor this low.
        floor = max(4, int(0.004 * sum(uni.values())))
        keep = {r for r, c in uni.items() if c >= floor}
        if keep:
            uni = Counter({r: c for r, c in uni.items() if r in keep})
            starts = Counter({r: c for r, c in starts.items() if r in keep})
            trans = {
                ctx: Counter({r: c for r, c in row.items() if r in keep})
                for ctx, row in trans.items()
                if all(part in keep for part in ctx.split("|"))
            }
            trans = {ctx: row for ctx, row in trans.items() if row}
            trans1 = {
                ctx: Counter({r: c for r, c in row.items() if r in keep})
                for ctx, row in trans1.items()
                if ctx in keep
            }
            trans1 = {ctx: row for ctx, row in trans1.items() if row}
            cadence_targets = {
                k: Counter({r: c for r, c in v.items() if r in keep})
                for k, v in cadence_targets.items()
            }
            within = {
                beats: Counter(
                    {
                        pat: c
                        for pat, c in row.items()
                        if all(part in keep for part in pat.split("|"))
                    }
                )
                for beats, row in within.items()
            }
        if uni:
            by_mode[mode] = {
                "starts": dict(starts),
                "uni": dict(uni),
                "trans": {k: dict(v) for k, v in trans.items()},
                "trans1": {k: dict(v) for k, v in trans1.items()},
                "cadence_targets": {k: dict(v) for k, v in cadence_targets.items()},
                "within_bar": {k: dict(v.most_common(60)) for k, v in within.items() if v},
                # The composer's OWN rate of moving harmony inside a bar, per
                # meter. The sampler used to hard-code 0.5 while its own comment
                # claimed it used the corpus rate.
                "within_rate": {
                    k: round(moved[k] / seen_bars[k], 4) for k in seen_bars if seen_bars[k] >= 20
                },
            }
    if not by_mode:
        return None
    return {"composer": composer, "order": order, "total_transitions": total, "by_mode": by_mode}


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    composers = argv or all_composers_with_bars()
    for c in composers:
        model = build_model(c)
        if model is None:
            print(f"  {c}: no roman data — skipped (re-extract with P1 first)")
            continue
        outdir = COMPILED_PACKS / c
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "progression_model.json").write_text(json.dumps(model, separators=(",", ":")))
        modes = ", ".join(f"{m}:{len(v['uni'])} romans" for m, v in model["by_mode"].items())
        wb = sum(
            len(pats)
            for v in model["by_mode"].values()
            for pats in (v.get("within_bar") or {}).values()
        )
        print(
            f"  {c}: {model['total_transitions']} transitions ({modes}); {wb} within-bar patterns"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
