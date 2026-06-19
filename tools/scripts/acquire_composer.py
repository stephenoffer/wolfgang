"""Acquire real reference scores for a composer and arm Wolfgang with them.

Wolfgang composes from a *corpus* — real bars put in front of Claude in the
brief. A composer with no corpus yields an insufficient brief and the commit
gate refuses it (see scales._gated_commit). This script arms a composer end to
end so the brief has real material to anchor on.

Acquisition is local-first, web-fallback. Web sources are tried in order
until one yields scores:
  1. LOCAL — music21's built-in corpus (offline, public-domain: Bach, Mozart,
     Beethoven, Haydn, Palestrina, Joplin, …). No network.
  2. WEB — if music21 ships nothing, fetch from ALLOWLISTED public-domain
     archives, each validated with music21 before use:
       a. KernScores — Humdrum **kern (clean, but a limited composer set).
       b. Mutopia Project — engraving-derived MIDI (clean barlines/meter),
          covering many Romantic/virtuoso composers KernScores lacks (Liszt,
          Chopin, …). A recursive /ftp/<Code>/ crawl collects every .mid.
     Network is isolated to this script.

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
import re
import urllib.error
import urllib.request
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_TOOLS = Path(__file__).resolve().parent.parent
REFERENCE_INDEX = _TOOLS / "reference_index"

# Only these hosts may be fetched from — public-domain, score-bearing archives.
_SOURCE_ALLOWLIST = (
    "https://kern.humdrum.org",
    "https://kernscores.stanford.edu",
    "https://www.mutopiaproject.org",
)
_HTTP_TIMEOUT = 30
_HTTP_RETRIES = 3

# music21-parseable symbolic score extensions we collect from web archives.
_SCORE_EXTS = (".mxl", ".xml", ".krn", ".musicxml", ".mid", ".midi")


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


def _fetch_kernscores(composer: str, dest: Path, max_files: int) -> List[str]:
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


# ─── Mutopia Project (recursive /ftp crawl of engraving-derived MIDI) ─────────

_MUTOPIA_ROOT = "https://www.mutopiaproject.org/ftp/"
_HREF_RE = re.compile(r'href="([^"?][^"]*)"', re.IGNORECASE)
_MUTOPIA_MAX_DIRS = 400  # crawl-request backstop per composer


def _html_hrefs(html: str) -> List[str]:
    """Relative hrefs from an Apache autoindex page (skip sort/parent links)."""
    out: List[str] = []
    for href in _HREF_RE.findall(html):
        # Skip absolute paths, externals, and '../' parent links.
        if href.startswith(("/", "http://", "https://", "..")):
            continue
        out.append(href)
    return out


def _mutopia_composer_code(composer: str) -> Optional[str]:
    """Resolve a composer name to a Mutopia folder code (e.g. liszt → LisztF).

    Mutopia codes are '<Surname><Initials>'. We list the /ftp/ root and match
    the first folder whose lowercased name starts with the requested surname
    (the last whitespace-separated token), so 'liszt' and 'franz liszt' both
    resolve to 'LisztF'.
    """
    raw = _http_get(_MUTOPIA_ROOT)
    if not raw:
        return None
    surname = composer.split()[-1].replace("-", "").lower()
    codes = [h.rstrip("/") for h in _html_hrefs(raw.decode("utf-8", "replace")) if h.endswith("/")]
    for code in codes:
        if code.replace("-", "").lower().startswith(surname):
            return code
    return None


def _crawl_mutopia_midis(base_url: str, max_files: int) -> List[str]:
    """Recursively collect score-file URLs under a Mutopia composer directory."""
    found: List[str] = []
    seen: set[str] = set()
    queue: List[str] = [base_url if base_url.endswith("/") else base_url + "/"]
    dirs_fetched = 0
    while queue and len(found) < max_files and dirs_fetched < _MUTOPIA_MAX_DIRS:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        raw = _http_get(url)
        dirs_fetched += 1
        if not raw:
            continue
        for href in _html_hrefs(raw.decode("utf-8", "replace")):
            child = url + href
            if href.endswith("/"):
                if child not in seen:
                    queue.append(child)
            elif href.lower().endswith(_SCORE_EXTS):
                found.append(child)
                if len(found) >= max_files:
                    break
    return found


def _fetch_mutopia(composer: str, dest: Path, max_files: int) -> List[str]:
    """Fetch public-domain MIDI for a composer from the Mutopia Project.

    Resolves the composer's folder code, recursively crawls it for score
    files, downloads each. Degrades to 'no files' on any network/lookup miss.
    """
    code = _mutopia_composer_code(composer)
    if not code:
        print("  Mutopia: no matching composer folder")
        return []
    base = _MUTOPIA_ROOT + code + "/"
    print(f"  Mutopia: crawling {base}")
    urls = _crawl_mutopia_midis(base, max_files)
    if not urls:
        return []
    dest.mkdir(parents=True, exist_ok=True)
    saved: List[str] = []
    for url in urls:
        if not _allowlisted(url):
            continue
        data = _http_get(url)
        if not data:
            continue
        # Leaf folders reuse the same basename (piece/piece.mid); disambiguate
        # with the parent folder to avoid clobbering distinct pieces.
        parent = Path(url).parent.name
        fp = dest / f"{parent}__{Path(url).name}"
        fp.write_bytes(data)
        saved.append(str(fp))
    return saved


# Web sources, tried in order until one yields scores.
_WEB_SOURCES: Tuple[Tuple[str, Any], ...] = (
    ("kernscores-web", _fetch_kernscores),
    ("mutopia-web", _fetch_mutopia),
)


# ─── Extraction → arming pipeline ────────────────────────────────────────────


def _json_default(obj: Any) -> float:
    """JSON encoder fallback: serialize music21 Fraction durations as float."""
    if isinstance(obj, Fraction):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


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
    # MIDI-parsed bars carry music21 Fraction durations (tuplets/irregular
    # values); store them as floats so the index matches the kern/mxl corpora.
    (cdir / "bar_index.json").write_text(
        json.dumps(bar_index, separators=(",", ":"), default=_json_default)
    )
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
        for src_name, fetcher in _WEB_SOURCES:
            print(f"→ web: {src_name}")
            paths = fetcher(composer, tmp, max_files)
            if paths:
                source = src_name
                break
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
