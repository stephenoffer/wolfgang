"""
Post-realization style gate — compares assembled section MusicXML metrics
against targets derived from StyleDNA, and optionally builds a RevisionScript.

Uses scales.style_analyzer + scales.style_comparator (same logic as CLI).
"""

from __future__ import annotations

import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .assembler import assemble
from .models import RevisionOp, RevisionScript
from .piece_graph import PieceGraph
from .style_analyzer import analyze_score
from .style_comparator import compare


def build_style_targets_from_dna(
    density_targets: Dict[str, Any],
    tempo_bpm: int,
) -> Dict[str, Dict[str, float]]:
    """Build comparator-style targets {metric: {mean, stdev}} from StyleDNA density."""
    cls = "slow" if tempo_bpm < 76 else ("fast" if tempo_bpm > 138 else "moderate")
    dt = density_targets.get(cls) or density_targets.get("moderate")
    if dt is None:
        rh, lh = 8.0, 6.0
    elif hasattr(dt, "rh_mean"):
        rh, lh = float(dt.rh_mean), float(dt.lh_mean)
    elif isinstance(dt, dict):
        rh = float(dt.get("rh_mean", 8.0))
        lh = float(dt.get("lh_mean", 6.0))
    else:
        rh, lh = 8.0, 6.0

    total_ev = rh + lh
    # NOTE: style_analyzer reports *_pct metrics and rest_ratio as
    # PERCENTAGES (0-100), not fractions — targets must match those units.
    return {
        "events_per_bar": {"mean": total_ev, "stdev": max(2.0, total_ev * 0.2)},
        "events_per_bar_rh": {"mean": rh, "stdev": max(1.5, rh * 0.25)},
        "events_per_bar_lh": {"mean": lh, "stdev": max(1.5, lh * 0.25)},
        "rest_ratio": {"mean": 8.0, "stdev": 6.0},
        "triplet_pct": {"mean": 6.0, "stdev": 8.0},
        "rhythmic_variety": {"mean": 5.0, "stdev": 2.5},
        "chromatic_pct": {"mean": 12.0, "stdev": 10.0},
        "leap_pct": {"mean": 18.0, "stdev": 12.0},
        "dynamic_markings_per_bar": {"mean": 0.15, "stdev": 0.12},
        # Human-vs-AI discriminators (human-sounding-music.md):
        # texture change rate is the single biggest separator — corpus
        # Beethoven ≈58%, typical AI output ≈12%
        "texture_change_pct": {"mean": 52.0, "stdev": 15.0},
        "direction_changes_per_bar": {"mean": 1.5, "stdev": 0.6},
        "density_cv": {"mean": 0.55, "stdev": 0.2},
        "stepwise_pct": {"mean": 45.0, "stdev": 12.0},
    }


def run_style_review_section(
    piece_id: str,
    section_id: str,
    threshold: float = 0.35,
    persist: bool = True,
) -> Dict[str, Any]:
    """Assemble section → analyze metrics → compare to StyleDNA-derived targets.

    Returns:
        comparison_report: output of style_comparator.compare
        revision_script: dict or None if passing
        musicxml_path: temp or workspace path used
        phrase_ids: phrases in this section (for RevisionOp targets)
    """
    workspace = Path("workspace") / piece_id
    graph_path = workspace / "piece_graph.json"
    if not graph_path.exists():
        return {"error": f"No workspace at {graph_path}"}

    graph = PieceGraph.load(str(graph_path))

    phrase_order = graph.get_section_phrases(section_id)
    if not phrase_order:
        return {"error": f"No phrases for section {section_id}"}

    tempo_bpm = 120
    for pid in phrase_order:
        ps = graph.phrases.get(pid)
        if ps and ps.slot:
            tempo_bpm = ps.slot.tempo_bpm or 120
            break

    dna = graph.style_dna
    targets = build_style_targets_from_dna(
        dna.density_targets if dna else {},
        tempo_bpm,
    )

    tmp_dir = tempfile.mkdtemp(prefix=f"wolfgang_stylegate_{piece_id}_")
    mxml_path = assemble(
        graph,
        scope=f"section-{section_id}",
        output_dir=tmp_dir,
    )

    composed_metrics = analyze_score(mxml_path)
    if composed_metrics is None:
        return {"error": "analyze_score returned None", "musicxml_path": mxml_path}

    report = compare(composed_metrics, targets, threshold=threshold)

    revision_script: Optional[Dict[str, Any]] = None
    if report.get("failing", 0) > 0:
        fixes: List[str] = []
        for _k, info in sorted(
            report.get("metrics", {}).items(),
            key=lambda x: -x[1].get("divergence_pct", 0),
        ):
            if info.get("status") == "FAIL" and info.get("fix_instruction"):
                fixes.append(str(info["fix_instruction"]))

        # Never auto-target re_realize at an agent-authored phrase (would erase notes)
        target_pid: Optional[str] = None
        for pid in phrase_order:
            ps = graph.phrases.get(pid)
            if ps and not getattr(ps, "agent_authored", False):
                target_pid = pid
                break

        if target_pid:
            rev = RevisionScript(
                section_id=section_id,
                ops=[
                    RevisionOp(
                        target_phrase=target_pid,
                        target_layer="principal_line",
                        target_bars=None,
                        operation="re_realize",
                        params={
                            "style_gate": True,
                            "failing_metrics": [
                                k
                                for k, v in report.get("metrics", {}).items()
                                if v.get("status") == "FAIL"
                            ],
                            "fix_hints": fixes[:8],
                        },
                        reason="Automated style gate: statistical divergence from StyleDNA targets",
                    )
                ],
                priority="important" if report.get("failing", 0) <= 2 else "critical",
                max_iterations=3,
            )
            revision_script = _deep_asdict(rev)
        else:
            revision_script = {
                "section_id": section_id,
                "ops": [],
                "priority": "critical",
                "max_iterations": 0,
                "gate_blocked": True,
                "reason": (
                    "Style metrics failed but every phrase in this section is "
                    "agent-authored; automatic re_realize would delete hand-written "
                    "LayerIR. Edit notes manually or clear agent_authored on specific "
                    "phrases before re-running the gate."
                ),
                "fix_hints": fixes[:12],
                "failing_metrics": [
                    k for k, v in report.get("metrics", {}).items() if v.get("status") == "FAIL"
                ],
            }

    out: Dict[str, Any] = {
        "section_id": section_id,
        "musicxml_path": mxml_path,
        "phrase_ids": phrase_order,
        "comparison_report": report,
        "revision_script": revision_script,
        "passes": report.get("failing", 0) == 0,
    }

    if persist:
        if not hasattr(graph, "style_review_reports") or graph.style_review_reports is None:
            graph.style_review_reports = {}
        graph.style_review_reports[section_id] = {
            "comparison_report": report,
            "revision_script": revision_script,
            "musicxml_path": mxml_path,
        }
        graph.save(str(graph_path))

    return out


def _deep_asdict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _deep_asdict(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _deep_asdict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_deep_asdict(v) for v in obj]
    return obj
