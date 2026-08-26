"""
reference_study — let the agent read WHOLE reference scores, like a human.

The composition brief shows the agent ≤8 statistically-retrieved, disconnected
exemplar bars per phrase. That is enough to imitate a texture but not enough to
reason about form, thematic development, or long-range architecture. A human
composer studies complete scores before writing a note.

This module reconstructs a complete reference piece from the corpus bar records
(which are already grouped by their ``source`` field — e.g. ``sonata01-1``) and
renders it in the same readable ``direct_compose`` shorthand the brief uses, with
the per-bar harmony (roman/function) and texture so the agent sees the harmonic
and textural arc, not just notes. The agent then writes its OWN analysis, stored
on the PieceGraph (``reference_studies``) and fed forward into every phrase brief.

Nothing here generates music. It surfaces real scores for the agent to study.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Any, Dict, List, Optional

from .composition_brief import _adapted_to_shorthand, _iter_corpus_bars
from .corpus_adapter import AdaptedBar, CorpusAdapter


def _texture_summary(textures: List[str], top: int = 3) -> List[str]:
    """Most common textures in order of frequency (drops blanks)."""
    counts: "OrderedDict[str, int]" = OrderedDict()
    for t in textures:
        if not t:
            continue
        counts[t] = counts.get(t, 0) + 1
    return [t for t, _ in sorted(counts.items(), key=lambda kv: -kv[1])[:top]]


def list_reference_scores(composer: str) -> Dict[str, Any]:
    """Enumerate the complete reference pieces available for a composer.

    Returns one entry per ``source`` (piece/movement), with enough metadata for
    the agent to pick representative pieces to study — bar count, key, meter, and
    the dominant RH/LH textures across the piece. A style id aggregates over its
    armed members (``_iter_corpus_bars`` already unions them).
    """
    sources: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
    for bar in _iter_corpus_bars(composer):
        src = bar.get("source")
        if not src:
            continue
        entry = sources.get(src)
        if entry is None:
            entry = sources[src] = {
                "source": src,
                "bars": 0,
                "key": bar.get("key", "?"),
                "key_mode": bar.get("key_mode", "?"),
                "time_sig": tuple(bar.get("time_sig", [4, 4])),
                "_rh_textures": [],
                "_lh_textures": [],
            }
        entry["bars"] += 1
        entry["_rh_textures"].append(bar.get("rh_texture", ""))
        entry["_lh_textures"].append(bar.get("lh_texture", ""))

    scores = []
    for entry in sources.values():
        scores.append(
            {
                "source": entry["source"],
                "bars": entry["bars"],
                "key": entry["key"],
                "key_mode": entry["key_mode"],
                "time_sig": list(entry["time_sig"]),
                "rh_textures": _texture_summary(entry.pop("_rh_textures")),
                "lh_textures": _texture_summary(entry.pop("_lh_textures")),
            }
        )
    # Longest pieces first — most material to learn from.
    scores.sort(key=lambda s: -s["bars"])
    return {"composer": composer, "count": len(scores), "scores": scores}


def reconstruct_score(
    composer: str,
    source: str,
    target_key: Optional[str] = None,
    max_bars: Optional[int] = None,
) -> Dict[str, Any]:
    """Reconstruct one complete reference piece in readable shorthand.

    Filters the corpus to ``source``, orders by ``bar_num``, and renders each bar
    via the brief's own shorthand renderer (``_adapted_to_shorthand``). When
    ``target_key`` is given, bars are transposed to it (so the agent can study a
    reference in the key it will compose in); otherwise the original pitches are
    shown. Each rendered bar carries its ``roman``/``function`` and textures so
    the agent reads the harmonic and textural arc, not just notes.
    """
    bars = [b for b in _iter_corpus_bars(composer) if b.get("source") == source]
    if not bars:
        return {
            "composer": composer,
            "source": source,
            "found": False,
            "warning": f"no corpus bars for source '{source}' (composer '{composer}')",
            "bars": [],
        }
    bars.sort(key=lambda b: b.get("bar_num", 0))
    if max_bars is not None:
        bars = bars[:max_bars]

    adapter = CorpusAdapter(composer) if target_key else None
    rendered: List[Dict[str, Any]] = []
    for b in bars:
        if target_key:
            adapted = adapter.transpose_bar(b, target_key, b.get("bar_num", 1))
        else:
            # Render the original pitches directly — display events already carry
            # pitch/dur/grace flags in the shape _adapted_to_shorthand expects.
            adapted = AdaptedBar(
                rh_events=b.get("rh_display") or b.get("rh_events", []),
                lh_events=b.get("lh_display") or b.get("lh_events", []),
                target_key=b.get("key", "C"),
                target_bar_num=b.get("bar_num", 1),
            )
        rh, lh = _adapted_to_shorthand(adapted)
        rendered.append(
            {
                "bar": b.get("bar_num", 1),
                "roman": b.get("roman", ""),
                "function": b.get("function", ""),
                "phrase_position": b.get("phrase_position", ""),
                "rh_texture": b.get("rh_texture", ""),
                "lh_texture": b.get("lh_texture", ""),
                "rh": rh,
                "lh": lh,
            }
        )

    first = bars[0]
    return {
        "composer": composer,
        "source": source,
        "found": True,
        "key": first.get("key", "?"),
        "key_mode": first.get("key_mode", "?"),
        "time_sig": list(first.get("time_sig", [4, 4])),
        "target_key": target_key,
        "bar_count": len(rendered),
        "bars": rendered,
    }
