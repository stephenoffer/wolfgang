"""Acquire real reference scores for a composer and arm Wolfgang with them.

Wolfgang composes from a *corpus* — real bars put in front of Claude in the
brief. A composer with no corpus yields an insufficient brief and the commit
gate refuses it (see scales._gated_commit). This script arms a composer end to
end so the brief has real material to anchor on.

Acquisition is local-first, web-fallback:
  1. LOCAL — music21's built-in corpus (offline, public-domain: Bach, Mozart,
     Beethoven, Haydn, Palestrina, Joplin, …). No network.
  2. WEB   — if music21 ships nothing for the composer, fetch public-domain
     Humdrum **kern from an ALLOWLISTED source (KernScores). Network is
     isolated to this script; every file is validated with music21 before use.

Then it runs the existing arming pipeline on the extracted bars:
     reference_index/<composer>/bar_index.json
       → build_corpus_indexes  (phrase_catalog, gesture_bank, window_index)
       → build_corpus_profiles (corpus_profile.json — z-score distributions)
       → texture_density_stats (density_stats.json — gate floors)

Usage:
    python3 -m scripts.acquire_composer haydn
    python3 -m scripts.acquire_composer "clementi" --max-files 40
    python3 -m scripts.acquire_composer haydn --no-web      # local only
    python3 -m scripts.acquire_composer --status haydn      # just report tier
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_TOOLS = Path(__file__).resolve().parent.parent
REFERENCE_INDEX = _TOOLS / "reference_index"

# Only these hosts may be fetched from — public-domain, score-bearing archives.
_SOURCE_ALLOWLIST = (
    "https://kern.humdrum.org",
    "https://kernscores.stanford.edu",
)
_HTTP_TIMEOUT = 30
_HTTP_RETRIES = 3


# ─── Local acquisition (music21 built-in corpus) ─────────────────────────────


def _local_score_paths(composer: str) -> List[str]:
    """Public-domain scores music21 ships locally for this composer."""
    from music21 import corpus

    paths: List[str] = []
    try:
        paths = [str(p) for p in corpus.getComposer(composer)]
    except Exception:
        paths = []
    if not paths:  # getComposer is name-list-bound; search is broader
        try:
            bundle = corpus.search(composer, "composer")
            paths = [str(m.sourcePath) for m in bundle]
        except Exception:
            paths = []
    return [p for p in paths if p.endswith((".mxl", ".xml", ".krn", ".musicxml"))]


# ─── Web acquisition (allowlisted, validated) ────────────────────────────────


def _allowlisted(url: str) -> bool:
    return any(url.startswith(prefix) for prefix in _SOURCE_ALLOWLIST)


def _http_get(url: str) -> Optional[bytes]:
    if not _allowlisted(url):
        print(f"  refused (not on allowlist): {url}")
        return None
    for attempt in range(1, _HTTP_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "wolfgang-acquire"})
            with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"  fetch attempt {attempt}/{_HTTP_RETRIES} failed: {exc}")
    return None


def _fetch_web_scores(composer: str, dest: Path, max_files: int) -> List[str]:
    """Fetch public-domain kern files for a composer from KernScores into dest.

    KernScores exposes a per-composer listing; we pull the listing, then each
    .krn file. Network/source errors degrade to 'no files' (caller falls back
    to a clear, actionable message) rather than crashing.
    """
    dest.mkdir(parents=True, exist_ok=True)
    # KernScores groups public-domain works by composer slug under /cgi-bin.
    listing_url = (
        f"https://kern.humdrum.org/cgi-bin/ksdata?l=users/craig/classical/{composer}&format=kern"
    )
    print(f"  querying KernScores: {listing_url}")
    raw = _http_get(listing_url)
    if not raw:
        return []
    try:
        entries = json.loads(raw.decode("utf-8", "replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Some endpoints return a newline list of file URLs rather than JSON.
        entries = [
            {"url": ln.strip()}
            for ln in raw.decode("utf-8", "replace").splitlines()
            if ln.strip().endswith(".krn")
        ]
    saved: List[str] = []
    for ent in entries:
        if len(saved) >= max_files:
            break
        url = ent.get("url") if isinstance(ent, dict) else None
        if not url or not _allowlisted(url):
            continue
        data = _http_get(url)
        if not data:
            continue
        fp = dest / Path(url).name
        fp.write_bytes(data)
        saved.append(str(fp))
    return saved


# ─── Extraction → arming pipeline ────────────────────────────────────────────


def _extract_bars(
    paths: List[str], composer: str, max_files: int
) -> Tuple[List[Dict[str, Any]], int, int]:
    """Parse + validate each score with music21, extract bar records."""
    import music21

    from scripts.build_full_corpus import analyze_score_bars

    bars: List[Dict[str, Any]] = []
    ok = bad = 0
    for path in paths:
        if ok >= max_files:
            break
        try:
            score = music21.converter.parse(path)
            src = Path(path).stem
            extracted = analyze_score_bars(score, composer, src)
            if extracted:
                bars.extend(extracted)
                ok += 1
        except Exception as exc:  # invalid/corrupt score — skip + log, never crash
            bad += 1
            if bad <= 5:
                print(f"  skip unparseable {Path(path).name}: {exc}")
    return bars, ok, bad


def _arm_from_bars(composer: str, bars: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Write bar_index and run the derived-index + profile + density builders."""
    from scales.composition_brief import texture_density_stats

    from scripts import build_corpus_indexes, build_corpus_profiles

    cdir = REFERENCE_INDEX / composer
    cdir.mkdir(parents=True, exist_ok=True)
    bar_index = {"composer": composer, "total_bars": len(bars), "bars": bars}
    (cdir / "bar_index.json").write_text(json.dumps(bar_index, separators=(",", ":")))
    print(f"  wrote {len(bars)} bars → {cdir / 'bar_index.json'}")

    idx = build_corpus_indexes.build_composer(composer, force=True)
    print(f"  indexes: {json.dumps(idx)}")
    build_corpus_profiles.main([composer])
    # density_stats.json (the gate's floors) — force a rebuild from new bars
    texture_density_stats(composer, refresh=True)
    return idx


def acquire(composer: str, use_web: bool = True, max_files: int = 60) -> Dict[str, Any]:
    """Arm a composer end to end. Returns a coverage report."""
    from scales.composition_brief import composer_coverage_tier

    composer = composer.lower().strip()
    before = composer_coverage_tier(composer)
    print(
        f"=== Acquiring '{composer}' (currently tier {before['tier']}, {before['bars']} bars) ==="
    )

    print("→ local: music21 built-in corpus")
    paths = _local_score_paths(composer)
    source = "music21-local"
    if not paths and use_web:
        print(f"  none locally; → web fallback (allowlist: {', '.join(_SOURCE_ALLOWLIST)})")
        tmp = _TOOLS / "reference_scores" / f"_fetch_{composer}"
        paths = _fetch_web_scores(composer, tmp, max_files)
        source = "kernscores-web"
    if not paths:
        return {
            "ok": False,
            "composer": composer,
            "error": "no_scores_found",
            "hint": (
                f"music21 ships no '{composer}' corpus"
                + ("" if use_web else " and --no-web was set")
                + ". Provide local score files and ingest them with "
                "tools/scripts/ingest_with_feedback.py, or check the "
                "composer spelling."
            ),
            "coverage": before,
        }
    print(f"  {len(paths)} candidate score files ({source})")

    bars, ok, bad = _extract_bars(paths, composer, max_files)
    if not bars:
        return {
            "ok": False,
            "composer": composer,
            "error": "no_bars_extracted",
            "files_ok": ok,
            "files_bad": bad,
            "coverage": before,
        }

    _arm_from_bars(composer, bars)
    after = composer_coverage_tier(composer)
    print(
        f"=== Done: tier {before['tier']} → {after['tier']} "
        f"({after['bars']} bars, source={source}) ==="
    )
    return {
        "ok": True,
        "composer": composer,
        "source": source,
        "files_used": ok,
        "files_skipped": bad,
        "coverage_before": before,
        "coverage_after": after,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Acquire + arm a composer corpus")
    ap.add_argument("composer", help="composer name (e.g. haydn, clementi)")
    ap.add_argument(
        "--no-web", action="store_true", help="local music21 corpus only; do not fetch from the web"
    )
    ap.add_argument(
        "--max-files", type=int, default=60, help="max score files to ingest (default 60)"
    )
    ap.add_argument(
        "--status", action="store_true", help="report the composer's coverage tier and exit"
    )
    args = ap.parse_args(argv)

    from scales.composition_brief import composer_coverage_tier

    if args.status:
        print(json.dumps(composer_coverage_tier(args.composer), indent=2))
        return 0

    result = acquire(args.composer, use_web=not args.no_web, max_files=args.max_files)
    print(json.dumps({k: v for k, v in result.items() if k != "coverage"}, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
