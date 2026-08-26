"""Build phrase / gesture / window / transition indexes from bar records.

The flagship composers (mozart, beethoven, chopin) already ship
``phrase_catalog.json``, ``gesture_bank.json`` and ``window_index_*.json``
produced by an offline pipeline. The other corpus composers (bach, haydn,
palestrina, monteverdi, weber, handel, schubert, corelli) only have bar
records. This script rebuilds the *same schemas* for any composer, derived
purely from the bar records every composer already has, so the retrieval banks
(PhraseBank, GestureBank, CadenceBank, TransitionBank) work for all of them.

It is deliberately conservative: it never invents data it cannot derive from a
bar record, and it mirrors the field names the banks read (verified against the
flagship files). Bar fields absent for music21-sourced composers (e.g.
``time_sig``, RH events) degrade to sensible defaults.

Usage:
    python3 -m scripts.build_corpus_indexes                 # all composers w/o indexes
    python3 -m scripts.build_corpus_indexes bach haydn      # named composers
    python3 -m scripts.build_corpus_indexes --force         # rebuild even flagship
"""

from __future__ import annotations

import json
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from scales.duration import beats_to_dur

_TOOLS = Path(__file__).resolve().parent.parent
REFERENCE_INDEX = _TOOLS / "reference_index"
PATTERN_LIBRARY = _TOOLS / "pattern_library"

_WINDOW_SHARD_SIZE = 5000
_MAX_PHRASE_BARS = 16
_MIN_PHRASE_BARS = 1
_FLAGSHIP = {"mozart", "beethoven", "chopin"}


# ─── Bar loading ─────────────────────────────────────────────────────────────


def load_bars(composer: str) -> List[Dict[str, Any]]:
    """Load all bar records for a composer (sharded or inline), in file order."""
    cdir = REFERENCE_INDEX / composer
    shards = sorted(cdir.glob("bars_*.json"))
    bars: List[Dict[str, Any]] = []
    if shards:
        for shard in shards:
            with open(shard) as f:
                bars.extend(json.load(f))
        return bars
    index_path = cdir / "bar_index.json"
    if index_path.exists():
        with open(index_path) as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("bars"), list):
            bars = data["bars"]
    return bars


def group_by_source(bars: List[Dict[str, Any]]) -> "OrderedDict[str, List[Dict]]":
    """Group bars by source movement, preserving the stored (bar) order."""
    groups: "OrderedDict[str, List[Dict]]" = OrderedDict()
    for bar in bars:
        groups.setdefault(bar.get("source", "?"), []).append(bar)
    for src in groups:
        groups[src].sort(key=lambda b: b.get("bar_num", 0))
    return groups


# ─── Small derivations shared across builders ────────────────────────────────


def _events(bar: Dict[str, Any], hand: str) -> List[Dict[str, Any]]:
    """Best-available event list for a hand (rh/lh), across record variants."""
    for key in (f"{hand}_events", f"{hand}_display"):
        ev = bar.get(key)
        if isinstance(ev, list) and ev:
            return ev
    return []


def _dur_profile(events: List[Dict[str, Any]]) -> List[str]:
    out = []
    for e in events:
        if e.get("type") == "rest":
            continue
        out.append(beats_to_dur(e.get("dur", 1.0)))
    return out


def _accent_profile(events: List[Dict[str, Any]]) -> List[str]:
    out = []
    for i, e in enumerate(events):
        if e.get("type") == "rest":
            out.append("rest")
        elif i == 0:
            out.append("strong")
        else:
            out.append("weak")
    return out


def _harmony_binding(lh_texture: str) -> str:
    t = lh_texture or ""
    if t.startswith("block_chord") or t in ("sparse_punctuation",):
        return "chordal"
    if t.startswith("broken_chord") or t in ("alberti", "oscillation_trill"):
        return "arpeggiated"
    if "walking" in t or t in ("bass_melody",):
        return "linear_bass"
    if t in ("pedal_point", "silence"):
        return "pedal"
    return "chordal"


def _span_beats(bar: Dict[str, Any]) -> float:
    ts = bar.get("time_sig")
    if isinstance(ts, (list, tuple)) and len(ts) == 2 and ts[1]:
        return float(ts[0]) * 4.0 / float(ts[1])
    return 4.0


def _norm_curve(vals: List[float]) -> List[float]:
    """Normalize a list to [0,1] by its max (matches flagship density_curve)."""
    if not vals:
        return []
    mx = max(vals)
    if mx <= 0:
        return [0.0 for _ in vals]
    return [round(v / mx, 4) for v in vals]


def _minmax_curve(vals: List[float]) -> List[float]:
    if not vals:
        return []
    lo, hi = min(vals), max(vals)
    if hi - lo <= 0:
        return [0.0 for _ in vals]
    return [round((v - lo) / (hi - lo), 4) for v in vals]


# ─── Gesture functions / roles (mirrors the flagship vocabulary) ─────────────


def _gesture_function(pos: str, idx: int, n: int, density: int) -> str:
    if pos == "opening":
        return "pickup" if idx == 0 else "lean_in"
    if pos == "cadential":
        return "cadential_push"
    if pos == "closing":
        return "cadential_release" if idx == n - 1 else "arrival"
    # middle
    if density >= 9:
        return "insist"
    if density <= 3:
        return "answer_with_space"
    return "answer"


def _phrase_role(slice_bars: List[Dict[str, Any]]) -> str:
    first = slice_bars[0].get("phrase_position", "middle")
    last = slice_bars[-1].get("phrase_position", "middle")
    if first == "opening":
        return "opening"
    if last in ("cadential", "closing"):
        return "closing"
    return "middle"


def _cadence_type(slice_bars: List[Dict[str, Any]]) -> str:
    """Coarse cadence label from the closing bar.

    We do not have explicit Roman-numeral cadence data in bar records, so this
    is a heuristic: a phrase that ends on a cadential/closing bar is labelled
    'authentic' (the common case) or 'half' when the final harmony is unstable.
    Phrases that do not close are 'none'. Honest and documented; CadenceBank
    only needs a non-'none' label to surface a cadence exemplar.
    """
    last = slice_bars[-1]
    pos = last.get("phrase_position", "middle")
    if pos not in ("cadential", "closing"):
        return "none"
    direction = last.get("melody_direction", "static")
    return "authentic" if direction == "descending" else "half"


# ─── Phrase segmentation ─────────────────────────────────────────────────────


def segment_phrases(source_bars: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Slice a movement's bars into phrases at cadence boundaries.

    Rules (in priority order):
      - close a phrase after a cadential/closing bar (the cadence ends it),
      - close before an 'opening' bar that begins a new idea,
      - never exceed _MAX_PHRASE_BARS.
    """
    phrases: List[List[Dict[str, Any]]] = []
    cur: List[Dict[str, Any]] = []
    for bar in source_bars:
        pos = bar.get("phrase_position", "middle")
        if cur and pos == "opening":
            phrases.append(cur)
            cur = []
        cur.append(bar)
        if pos in ("cadential", "closing") and len(cur) >= _MIN_PHRASE_BARS:
            phrases.append(cur)
            cur = []
        elif len(cur) >= _MAX_PHRASE_BARS:
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    return phrases


# ─── Builders ────────────────────────────────────────────────────────────────


def build_phrase_catalog(composer: str, groups: "OrderedDict[str, List[Dict]]") -> Dict[str, Any]:
    phrases: List[Dict[str, Any]] = []
    role_dist: Dict[str, int] = defaultdict(int)
    cad_dist: Dict[str, int] = defaultdict(int)
    len_dist: Dict[str, int] = defaultdict(int)
    total_len = 0

    for src, bars in groups.items():
        mvt_id = src.replace("/", "_").replace(".", "")
        for pi, slice_bars in enumerate(segment_phrases(bars)):
            n = len(slice_bars)
            md = [b.get("melody_density", 0) for b in slice_bars]
            rc = [b.get("register_center", 0) for b in slice_bars]
            role = _phrase_role(slice_bars)
            cad = _cadence_type(slice_bars)
            first = slice_bars[0]
            ts = first.get("time_sig", [4, 4])
            grace = sum(1 for b in slice_bars if b.get("has_grace_notes")) / n
            dotted = sum(1 for b in slice_bars if b.get("has_dotted_rhythms")) / n
            peak = md.index(max(md)) if md else 0
            phrases.append(
                {
                    "phrase_id": f"{composer}_{mvt_id}_p{pi}",
                    "source": src,
                    "bar_range": [first.get("bar_num", 1), slice_bars[-1].get("bar_num", n)],
                    "length": n,
                    "role": role,
                    "cadence_type": cad,
                    "key": first.get("key", "C"),
                    "key_mode": first.get("key_mode", "major"),
                    "time_sig": list(ts) if isinstance(ts, (list, tuple)) else [4, 4],
                    "density_curve": _norm_curve(md),
                    "register_curve": _minmax_curve(rc),
                    "rest_pattern": [1.0 if b.get("has_rests") else 0.0 for b in slice_bars],
                    "rh_textures": [b.get("rh_texture", "unclassified") for b in slice_bars],
                    "lh_textures": [b.get("lh_texture", "unclassified") for b in slice_bars],
                    "melody_directions": [b.get("melody_direction", "static") for b in slice_bars],
                    "harmony_path": [b.get("harmony_quality", "") for b in slice_bars],
                    "peak_bar_offset": peak,
                    "grace_note_ratio": round(grace, 4),
                    "dotted_rhythm_ratio": round(dotted, 4),
                    "avg_melody_density": round(sum(md) / n, 4) if n else 0.0,
                    "entry_state": {
                        "density": md[0] if md else 0,
                        "register_center": rc[0] if rc else 0,
                        "texture": first.get("rh_texture", "unclassified"),
                        "has_rests": bool(first.get("has_rests")),
                    },
                    "exit_state": {
                        "density": md[-1] if md else 0,
                        "register_center": rc[-1] if rc else 0,
                        "texture": slice_bars[-1].get("rh_texture", "unclassified"),
                        "has_rests": bool(slice_bars[-1].get("has_rests")),
                    },
                }
            )
            role_dist[role] += 1
            cad_dist[cad] += 1
            len_dist[str(n)] += 1
            total_len += n

    return {
        "composer": composer,
        "source_bar_index": f"reference_index/{composer}/bar_index.json",
        "total_phrases": len(phrases),
        "avg_phrase_length": round(total_len / len(phrases), 2) if phrases else 0,
        "length_distribution": dict(sorted(len_dist.items(), key=lambda kv: int(kv[0]))),
        "role_distribution": dict(role_dist),
        "cadence_distribution": dict(cad_dist),
        "phrases": phrases,
    }


def build_gesture_bank(composer: str, groups: "OrderedDict[str, List[Dict]]") -> Dict[str, Any]:
    gestures: List[Dict[str, Any]] = []
    fn_dist: Dict[str, int] = defaultdict(int)
    contour_dist: Dict[str, int] = defaultdict(int)

    for src, bars in groups.items():
        mvt_id = src.replace("/", "_").replace(".", "")
        for slice_bars in segment_phrases(bars):
            n = len(slice_bars)
            for idx, bar in enumerate(slice_bars):
                pos = bar.get("phrase_position", "middle")
                density = bar.get("melody_density", 0)
                fn = _gesture_function(pos, idx, n, density)
                contour = bar.get("melody_direction", "static")
                rh_ev = _events(bar, "rh")
                has_rests = bool(bar.get("has_rests"))
                gestures.append(
                    {
                        "cell_id": f"{composer}_{mvt_id}_b{bar.get('bar_num', 1)}",
                        "function": fn,
                        "span_beats": _span_beats(bar),
                        "accent_profile": _accent_profile(rh_ev),
                        "dur_profile": _dur_profile(rh_ev),
                        "contour": contour,
                        "contour_intervals": [],
                        "interaction_role": "lead" if pos == "opening" else "respond",
                        "harmony_binding": _harmony_binding(bar.get("lh_texture", "")),
                        "entry_state": "fresh_phrase" if idx == 0 else "continuing",
                        "exit_state": "to_rest"
                        if has_rests
                        else ("to_cadence" if pos in ("cadential", "closing") else "to_continue"),
                        "transform_ops": ["transpose", "register_shift", "rhythm_mutate"],
                        "source": f"{src} bar {bar.get('bar_num', 1)}",
                        "source_bar_range": [bar.get("bar_num", 1), bar.get("bar_num", 1)],
                        "key_mode": bar.get("key_mode", "major"),
                        "rh_texture": bar.get("rh_texture", "unclassified"),
                        "lh_texture": bar.get("lh_texture", "unclassified"),
                        "melody_density": density,
                        "has_grace_notes": bool(bar.get("has_grace_notes")),
                        "has_dotted_rhythms": bool(bar.get("has_dotted_rhythms")),
                    }
                )
                fn_dist[fn] += 1
                contour_dist[contour] += 1

    return {
        "composer": composer,
        "source_bar_index": f"reference_index/{composer}/bar_index.json",
        "total_gestures": len(gestures),
        "function_distribution": dict(sorted(fn_dist.items(), key=lambda kv: -kv[1])),
        "contour_distribution": dict(contour_dist),
        "gestures": gestures,
    }


def build_windows(composer: str, groups: "OrderedDict[str, List[Dict]]") -> List[Dict[str, Any]]:
    windows: List[Dict[str, Any]] = []
    for src, bars in groups.items():
        n = len(bars)
        for size in (1, 2, 3):
            for i in range(n - size + 1):
                win = bars[i : i + size]
                md = [b.get("melody_density", 0) for b in win]
                first, last = win[0], win[-1]
                # distance (in bars) to the next cadential/closing bar
                cad_dist = 0
                for j in range(i, n):
                    if bars[j].get("phrase_position") in ("cadential", "closing"):
                        cad_dist = j - i
                        break
                windows.append(
                    {
                        "window_id": f"{composer}_{src.replace('/', '_')}_"
                        f"{first.get('bar_num', 1)}_{size}",
                        "source": src,
                        "bar_range": [first.get("bar_num", 1), last.get("bar_num", 1)],
                        "bars": size,
                        "phrase_role": first.get("phrase_position", "middle"),
                        "cadence_distance": cad_dist,
                        "cadence_type": _cadence_type(win),
                        "harmony_path": [b.get("harmony_quality", "") for b in win],
                        "key_mode": first.get("key_mode", "major"),
                        "key": first.get("key", "C"),
                        "density_curve": _norm_curve(md),
                        "rest_curve": [1.0 if b.get("has_rests") else 0.0 for b in win],
                        "bass_contour": _harmony_binding(first.get("lh_texture", "")),
                        "interaction_type": "dialogue_with_gaps",
                        "entry_state": {
                            "density": md[0] if md else 0,
                            "register_center": first.get("register_center", 0),
                            "texture": first.get("rh_texture", "unclassified"),
                            "has_rests": bool(first.get("has_rests")),
                        },
                        "exit_state": {
                            "density": md[-1] if md else 0,
                            "register_center": last.get("register_center", 0),
                            "texture": last.get("rh_texture", "unclassified"),
                            "has_rests": bool(last.get("has_rests")),
                        },
                        "ornaments": [],
                        "rh_textures": [b.get("rh_texture", "unclassified") for b in win],
                        "lh_textures": [b.get("lh_texture", "unclassified") for b in win],
                        "melody_directions": [b.get("melody_direction", "static") for b in win],
                        "time_sig": list(first.get("time_sig", [4, 4])),
                        "allowed_transforms": [
                            "transpose",
                            "motif_map",
                            "rhythm_mutate",
                            "register_shift",
                        ],
                    }
                )
    return windows


def build_transition_matrix(groups: "OrderedDict[str, List[Dict]]") -> Dict[str, Any]:
    """LH-texture Markov counts from consecutive bars within each movement."""
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total = 0
    for bars in groups.values():
        for a, b in zip(bars, bars[1:]):
            ta = a.get("lh_texture", "unclassified")
            tb = b.get("lh_texture", "unclassified")
            counts[ta][tb] += 1
            total += 1
    self_cont: Dict[str, float] = {}
    for ta, row in counts.items():
        tot = sum(row.values())
        self_cont[ta] = round(row.get(ta, 0) / tot, 4) if tot else 0.0
    return {
        "counts": {k: dict(v) for k, v in counts.items()},
        "self_continuation": self_cont,
        "total_transitions": total,
    }


def merge_transition_matrices(matrices: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Sum several composers' texture-transition counts into one matrix."""
    counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total = 0
    for m in matrices:
        for src, row in (m.get("counts") or {}).items():
            for dst, n in row.items():
                counts[src][dst] += int(n)
                total += int(n)
    self_cont: Dict[str, float] = {}
    for src, row in counts.items():
        tot = sum(row.values())
        self_cont[src] = round(row.get(src, 0) / tot, 4) if tot else 0.0
    return {
        "counts": {k: dict(v) for k, v in counts.items()},
        "self_continuation": self_cont,
        "total_transitions": total,
    }


def build_genre_matrices(force: bool = False) -> Dict[str, Any]:
    """Aggregate each style's ARMED members into a by_genre transition matrix.

    These were built once by `migrate_pattern_library.py` and never again, so
    six of the nine were still **synthetic** — the Classical matrix with
    hand-picked multipliers applied ("baroque: alberti x0.3, pedal_point x1.5")
    — and the two real ones were wrong in different ways:

      * `baroque.json` was sourced from bach + handel + corelli **plus
        palestrina and monteverdi**, folding Renaissance polyphony into the
        Baroque odds.
      * `romantic.json` was chopin alone, while schubert, liszt and weber are
        all armed.
      * There was no `renaissance.json` at all, so Palestrina and Monteverdi
        fell through to `classical.json` — Renaissance counterpoint judged by
        Classical texture statistics.

    Membership comes from `style_registry`, so arming a composer now grows its
    style's matrix automatically instead of leaving a hand-edited file behind.
    """
    from scales.style_registry import _STYLE_MEMBERS

    armed = set(all_composers_with_bars())
    out: Dict[str, Any] = {}
    for style, members in _STYLE_MEMBERS.items():
        present = [m for m in members if m in armed]
        mats = []
        for m in present:
            path = PATTERN_LIBRARY / "transitions" / "by_composer" / f"{m}.json"
            if path.exists():
                try:
                    mats.append(json.loads(path.read_text()))
                except (OSError, ValueError):
                    continue
        if not mats:
            out[style] = {"skipped": "no armed member has a transition matrix"}
            continue
        dest = PATTERN_LIBRARY / "transitions" / "by_genre" / f"{style}.json"
        if dest.exists() and not force:
            existing = {}
            try:
                existing = json.loads(dest.read_text())
            except (OSError, ValueError):
                pass
            # A synthetic matrix is always worth replacing with real data.
            if not existing.get("synthetic"):
                out[style] = {"kept": str(dest), "hint": "pass --force to rebuild"}
                continue
        merged = merge_transition_matrices(mats)
        merged["genre"] = style
        merged["source_composers"] = present
        merged["synthetic"] = False
        _write_json(dest, merged)
        out[style] = {
            "written": str(dest),
            "sources": present,
            "transitions": merged["total_transitions"],
        }
    return out


# ─── Orchestration ───────────────────────────────────────────────────────────


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=1)


def build_composer(composer: str, force: bool = False) -> Dict[str, Any]:
    cdir = REFERENCE_INDEX / composer
    bars = load_bars(composer)
    if not bars:
        return {"composer": composer, "skipped": "no bar records"}
    groups = group_by_source(bars)

    written: Dict[str, Any] = {"composer": composer, "movements": len(groups), "bars": len(bars)}

    # phrase_catalog
    pc_path = cdir / "phrase_catalog.json"
    if force or not pc_path.exists():
        catalog = build_phrase_catalog(composer, groups)
        _write_json(pc_path, catalog)
        written["phrases"] = catalog["total_phrases"]

    # gesture_bank
    gb_path = cdir / "gesture_bank.json"
    if force or not gb_path.exists():
        gbank = build_gesture_bank(composer, groups)
        _write_json(gb_path, gbank)
        written["gestures"] = gbank["total_gestures"]

    # window_index (sharded) + pointer
    wi_pointer = cdir / "window_index.json"
    if force or not wi_pointer.exists():
        windows = build_windows(composer, groups)
        shard_counts: List[int] = []
        for si in range(0, len(windows), _WINDOW_SHARD_SIZE):
            shard = windows[si : si + _WINDOW_SHARD_SIZE]
            _write_json(cdir / f"window_index_{si // _WINDOW_SHARD_SIZE:02d}.json", shard)
            shard_counts.append(len(shard))
        _write_json(
            wi_pointer, {"type": "window_index", "total": len(windows), "shards": shard_counts}
        )
        written["windows"] = len(windows)

    # transition matrix (by_composer) — only if absent or forced
    tm_path = PATTERN_LIBRARY / "transitions" / "by_composer" / f"{composer}.json"
    if force or not tm_path.exists():
        _write_json(tm_path, build_transition_matrix(groups))
        written["transition_matrix"] = True

    return written


def all_composers_with_bars() -> List[str]:
    if not REFERENCE_INDEX.exists():
        return []
    out = []
    for d in sorted(REFERENCE_INDEX.iterdir()):
        if d.is_dir() and load_bars(d.name):
            out.append(d.name)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    force = "--force" in argv
    argv = [a for a in argv if a != "--force"]
    # Skipping the flagship composers by default made "rebuild the indexes" a
    # silent no-op for mozart, beethoven and chopin — the three composers most
    # pieces are written against. Their catalogs then survived across corpus
    # changes: beethoven's phrase_catalog was 59% MOZART phrases, so a Beethoven
    # brief cited "corpus K.279/i" for its phrase shape. Stale is now opt-in.
    composers = argv or all_composers_with_bars()
    if not argv and not force:
        stale = [c for c in composers if c in _FLAGSHIP]
        if stale:
            print(
                f"note: rebuilding flagship composers too ({', '.join(sorted(stale))}); "
                f"existing per-artifact files are still kept unless --force"
            )
    for composer in composers:
        result = build_composer(composer, force=force)
        print(json.dumps(result))

    # Genre matrices are derived from the per-composer ones, so they must be
    # rebuilt after them or they go stale the moment a composer is armed.
    print(json.dumps({"genre_matrices": build_genre_matrices(force=force)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
