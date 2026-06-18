#!/usr/bin/env python3
"""
Ingest reference scores with corpus feedback loop.

Wraps the existing build_full_corpus pipeline and adds evidence extraction,
claim matching, overlay building, and conflict detection.

Usage:
    python3 tools/scripts/ingest_with_feedback.py <score-path> <composer> [options]
    python3 tools/scripts/ingest_with_feedback.py --batch <directory> <composer> [options]

Options:
    --genre <genre>       Genre for the composer (classical, baroque, etc.)
    --recompile           Re-run context_compiler after overlay generation
    --skip-corpus         Skip updating reference_index (evidence only)
    --verbose             Print detailed progress
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from scales.feedback.claim_matcher import match_batch, match_evidence
from scales.feedback.claim_registry import (
    ClaimRegistry,
    bootstrap_from_compiled_pack,
)
from scales.feedback.conflict_resolver import (
    resolve_conflicts,
    save_conflict_report,
)
from scales.feedback.evidence_extractor import (
    EvidenceBundle,
    extract_from_file,
    save_bundle,
    save_evidence_samples,
)
from scales.feedback.overlay_builder import OverlayBuilder

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
BASE = SCRIPT_DIR.parent  # tools/
PROJECT_ROOT = BASE.parent  # wolfgang-v2/


# ─── Paths ──────────────────────────────────────────────────────────────────

COMPILED_PACKS = BASE / "compiled_packs"
CONTEXT_EVIDENCE = BASE / "context_evidence"
CONTEXT_OVERLAYS = BASE / "context_overlays"
REFERENCE_INDEX = BASE / "reference_index"


# ─── Main Pipeline ──────────────────────────────────────────────────────────


def ingest_score(
    filepath: str,
    composer: str,
    genre: str = "",
    skip_corpus: bool = False,
    recompile: bool = False,
    verbose: bool = False,
) -> dict:
    """Full ingestion pipeline for a single score.

    Steps:
        1. Parse score (via music21 inside evidence_extractor)
        2. Optionally update reference_index (existing corpus flow)
        3. Extract EvidenceBundle
        4. Load/bootstrap ClaimRegistry
        5. Match evidence against claims
        6. Check for conflicts
        7. Build overlays if sufficient evidence
        8. Optionally recompile context

    Returns a summary dict.
    """
    t0 = time.time()
    summary = {"file": filepath, "composer": composer, "steps": []}

    # ── Step 1-2: Corpus update (existing flow) ──
    if not skip_corpus:
        _step_log(summary, "corpus_update", "skipped (use build_full_corpus.py)")

    # ── Step 3: Extract evidence ──
    if verbose:
        print(f"  Extracting evidence from {os.path.basename(filepath)}...")
    bundle = extract_from_file(filepath, composer)
    if bundle is None:
        summary["error"] = "Could not extract evidence (parse failure)"
        return summary

    _step_log(
        summary,
        "evidence_extraction",
        {
            "bar_count": bundle.bar_count,
            "lh_textures": len(bundle.lh_texture_distribution),
            "transitions": sum(len(v) for v in bundle.transition_counts.values()),
        },
    )

    # Save evidence sample
    evidence_dir = CONTEXT_EVIDENCE / composer
    save_bundle(bundle, evidence_dir)

    # ── Step 4: Load or bootstrap claim registry ──
    claims_path = evidence_dir / "claims.json"
    pack_dir = COMPILED_PACKS / composer

    if claims_path.exists():
        if verbose:
            print("  Loading existing claim registry...")
        registry = ClaimRegistry.load(claims_path)
    else:
        if not pack_dir.exists():
            summary["error"] = f"No compiled pack for '{composer}'. Run context_compiler first."
            return summary
        if verbose:
            print("  Bootstrapping claim registry from compiled pack...")
        registry = bootstrap_from_compiled_pack(composer, pack_dir)
        _step_log(summary, "bootstrap", {"claims": len(registry)})

    # ── Step 5: Match evidence against claims ──
    if verbose:
        print(f"  Matching evidence against {len(registry)} claims...")
    report = match_evidence(bundle, registry)
    _step_log(summary, "claim_matching", report.summary())

    # Save updated registry
    registry.save(evidence_dir)
    registry.save_support_stats(evidence_dir)

    # ── Step 6: Conflict detection ──
    if verbose:
        print("  Checking for conflicts...")
    conflict_report = resolve_conflicts(registry)
    if conflict_report.total_conflicts > 0:
        save_conflict_report(conflict_report, evidence_dir)
        _step_log(
            summary,
            "conflicts",
            {
                "total": conflict_report.total_conflicts,
                "high": conflict_report.high_severity,
                "medium": conflict_report.medium_severity,
                "low": conflict_report.low_severity,
            },
        )
    else:
        _step_log(summary, "conflicts", {"total": 0})

    # ── Step 7: Build overlays ──
    # Only build overlays if we have enough evidence
    promotable_claims = sum(1 for c in registry.get_all() if c.total_tested >= 5)
    if promotable_claims >= 3:
        if verbose:
            print(f"  Building overlays ({promotable_claims} promotable claims)...")
        overlay_dir = CONTEXT_OVERLAYS / composer
        builder = OverlayBuilder(registry, pack_dir, [bundle])
        overlay_files = builder.build_all(overlay_dir)
        _step_log(
            summary,
            "overlay_build",
            {
                "files_written": list(overlay_files.keys()),
            },
        )
    else:
        _step_log(
            summary,
            "overlay_build",
            {
                "skipped": True,
                "reason": f"Only {promotable_claims} promotable claims (need >= 3)",
            },
        )

    # ── Step 8: Recompile ──
    if recompile:
        if verbose:
            print("  Recompiling context...")
        try:
            from scales.context_compiler import ContextCompiler

            compiler = ContextCompiler()
            compiler.compile(composer)
            _step_log(summary, "recompile", {"status": "success"})
        except Exception as e:
            _step_log(summary, "recompile", {"status": "error", "error": str(e)})
    else:
        _step_log(summary, "recompile", {"skipped": True})

    summary["elapsed_seconds"] = round(time.time() - t0, 2)
    return summary


def ingest_batch(
    directory: str,
    composer: str,
    genre: str = "",
    skip_corpus: bool = False,
    recompile: bool = False,
    verbose: bool = False,
) -> dict:
    """Ingest all score files in a directory.

    Extracts evidence from each file, then builds overlays once
    from the aggregated evidence.
    """
    t0 = time.time()
    score_dir = Path(directory)
    valid_ext = {".musicxml", ".mxl", ".xml", ".krn", ".mid", ".midi"}

    files = sorted(f for f in score_dir.iterdir() if f.suffix.lower() in valid_ext)

    if not files:
        return {"error": f"No score files found in {directory}"}

    print(f"Ingesting {len(files)} scores for {composer}...")

    # Extract all evidence bundles
    bundles: list[EvidenceBundle] = []
    for fp in files:
        if verbose:
            print(f"  [{len(bundles) + 1}/{len(files)}] {fp.name}...")
        bundle = extract_from_file(str(fp), composer)
        if bundle is not None:
            bundles.append(bundle)
        else:
            print(f"  SKIP: Could not parse {fp.name}")

    if not bundles:
        return {"error": "No evidence extracted from any file"}

    print(f"  Extracted {len(bundles)} bundles ({sum(b.bar_count for b in bundles)} bars total)")

    # Save evidence samples
    evidence_dir = CONTEXT_EVIDENCE / composer
    save_evidence_samples(bundles, evidence_dir)

    # Load or bootstrap claim registry
    claims_path = evidence_dir / "claims.json"
    pack_dir = COMPILED_PACKS / composer

    if claims_path.exists():
        registry = ClaimRegistry.load(claims_path)
    else:
        if not pack_dir.exists():
            return {"error": f"No compiled pack for '{composer}'"}
        registry = bootstrap_from_compiled_pack(composer, pack_dir)

    # Match all bundles — accumulates evidence into the registry (saved below).
    print(f"  Matching against {len(registry)} claims...")
    match_batch(bundles, registry)

    # Save updated registry
    registry.save(evidence_dir)
    registry.save_support_stats(evidence_dir)

    # Conflict detection
    conflict_report = resolve_conflicts(registry)
    if conflict_report.total_conflicts > 0:
        save_conflict_report(conflict_report, evidence_dir)
        print(
            f"  {conflict_report.total_conflicts} conflicts detected "
            f"({conflict_report.high_severity} high)"
        )

    # Build overlays from aggregated evidence
    promotable = sum(1 for c in registry.get_all() if c.total_tested >= 5)
    overlay_files = {}
    if promotable >= 3:
        print(f"  Building overlays ({promotable} promotable claims)...")
        overlay_dir = CONTEXT_OVERLAYS / composer
        builder = OverlayBuilder(registry, pack_dir, bundles)
        overlay_files = builder.build_all(overlay_dir)
        print(f"  Wrote overlays: {list(overlay_files.keys())}")
    else:
        print(f"  Skipping overlays ({promotable} promotable, need >= 3)")

    # Recompile
    if recompile:
        try:
            from scales.context_compiler import ContextCompiler

            compiler = ContextCompiler()
            compiler.compile(composer)
            print("  Recompiled context successfully")
        except Exception as e:
            print(f"  Recompile error: {e}")

    summary = {
        "composer": composer,
        "files_processed": len(files),
        "bundles_extracted": len(bundles),
        "total_bars": sum(b.bar_count for b in bundles),
        "claims": len(registry),
        "conflicts": conflict_report.total_conflicts,
        "overlay_files": list(overlay_files.keys()),
        "elapsed_seconds": round(time.time() - t0, 2),
    }

    print(f"\nDone in {summary['elapsed_seconds']}s")
    print(json.dumps(summary, indent=2))
    return summary


def _step_log(summary: dict, step: str, data: Any) -> None:
    """Append a step log to the summary."""
    summary["steps"].append({"step": step, "data": data})


# ─── CLI ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Ingest reference scores with corpus feedback loop"
    )
    parser.add_argument("input", nargs="?", help="Score file to ingest")
    parser.add_argument("composer", help="Composer name (e.g., mozart, beethoven)")
    parser.add_argument("--batch", help="Directory of score files to ingest in batch")
    parser.add_argument("--genre", default="", help="Genre (classical, baroque, etc.)")
    parser.add_argument(
        "--recompile", action="store_true", help="Recompile context after overlay generation"
    )
    parser.add_argument("--skip-corpus", action="store_true", help="Skip updating reference_index")
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress")

    args = parser.parse_args()

    if args.batch:
        result = ingest_batch(
            args.batch,
            args.composer,
            genre=args.genre,
            skip_corpus=args.skip_corpus,
            recompile=args.recompile,
            verbose=args.verbose,
        )
    elif args.input:
        result = ingest_score(
            args.input,
            args.composer,
            genre=args.genre,
            skip_corpus=args.skip_corpus,
            recompile=args.recompile,
            verbose=args.verbose,
        )
        if args.verbose:
            print(json.dumps(result, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
