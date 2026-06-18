"""Style/genre references — compose "in a classical style", not "as Mozart".

A *style reference* is a named aggregation of several composers who share an
idiom (e.g. ``classical`` → mozart + haydn + beethoven). It lets Wolfgang
target a style without pinning a single composer: the brief draws exemplars
from every armed member, and the corpus_profile / density_stats used for
comparison are aggregated across the whole style.

A style is addressed as a pseudo-composer id ``style__<name>`` (filesystem-safe,
no colon) so it flows through the same per-``composer`` machinery: the corpus
primitives in composition_brief detect the prefix and aggregate over members.

Membership is by historical period and filtered to composers that are actually
armed (have corpus on disk) — so as `acquire_composer` adds composers, the
styles they belong to automatically grow. Genres with no armed composer yet
(late-romantic, impressionist, …) resolve to *unsupported* with an honest
message rather than a silent substitution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

STYLE_PREFIX = "style__"

# Canonical period → member composers (supersets; filtered to armed at runtime).
# Names align with tools/pattern_library/transitions/by_genre/ and
# .claude/context/<genre>/ where they exist.
_STYLE_MEMBERS: Dict[str, List[str]] = {
    "renaissance": ["palestrina", "monteverdi"],
    "baroque": ["bach", "handel", "corelli", "vivaldi", "scarlatti"],
    "classical": ["mozart", "haydn", "beethoven", "clementi"],
    "romantic": ["chopin", "schubert", "schumann", "brahms", "weber"],
    "late-romantic": ["mahler", "bruckner", "strauss-r", "elgar"],
    "impressionist": ["debussy", "ravel", "satie"],
    "modern": ["bartok", "stravinsky", "prokofiev", "shostakovich", "copland"],
    "minimalist": ["glass", "reich", "arvo-part"],
    "nationalistic": ["dvorak", "grieg", "smetana"],
    "film-score": ["williams", "zimmer", "morricone"],
}

# Request synonyms → canonical style name.
_SYNONYMS: Dict[str, str] = {
    "galant": "classical",
    "viennese": "classical",
    "classical-era": "classical",
    "high-classical": "classical",
    "baroque-era": "baroque",
    "contrapuntal": "baroque",
    "fugal": "baroque",
    "early-romantic": "romantic",
    "romantic-era": "romantic",
    "romanticism": "romantic",
    "lyrical-romantic": "romantic",
    "renaissance-polyphony": "renaissance",
    "early-music": "renaissance",
    "modal-polyphony": "renaissance",
    "impressionism": "impressionist",
    "impressionistic": "impressionist",
    "20th-century": "modern",
    "modernist": "modern",
    "neoclassical": "modern",
    "minimalism": "minimalist",
    "cinematic": "film-score",
    "film": "film-score",
    "soundtrack": "film-score",
}


def normalize_style(name: Optional[str]) -> Optional[str]:
    """Map a free-text style/genre request to a canonical style name, or None."""
    if not name:
        return None
    n = str(name).strip().lower().replace(" ", "-").replace("_", "-")
    if n.startswith(STYLE_PREFIX):
        n = n[len(STYLE_PREFIX) :]
    if n in _STYLE_MEMBERS:
        return n
    return _SYNONYMS.get(n)


def is_style_id(ref: Optional[str]) -> bool:
    return bool(ref) and str(ref).startswith(STYLE_PREFIX)


def style_name(ref: str) -> str:
    return ref[len(STYLE_PREFIX) :] if is_style_id(ref) else ref


def make_style_id(name: str) -> str:
    canon = normalize_style(name) or str(name).strip().lower()
    return f"{STYLE_PREFIX}{canon}"


def all_style_members(style: str) -> List[str]:
    """Full membership superset for a canonical style (ignores arming)."""
    return list(_STYLE_MEMBERS.get(normalize_style(style) or style, []))


def style_members(style: str, armed_only: bool = True) -> List[str]:
    """Members of a style. When armed_only, keep only composers with corpus."""
    members = all_style_members(style)
    if not armed_only:
        return members
    from .composition_brief import available_corpus_composers

    armed = set(available_corpus_composers())
    return [m for m in members if m in armed]


def styles_for_composer(composer: str) -> List[str]:
    """Which styles a composer belongs to (used for unknown-composer fallback)."""
    c = (composer or "").lower().split("-")[0].split("_")[0]
    out = []
    for style, members in _STYLE_MEMBERS.items():
        if any(m.split("-")[0] == c for m in members):
            out.append(style)
    return out


def resolve_reference(request: Optional[str]) -> Dict[str, Any]:
    """Resolve a free-text request to a reference.

    Returns a dict with:
      kind:    'composer' | 'style' | 'unknown'
      id:      the reference id to thread as ``composer`` (composer name or
               ``style__<name>``); for unknown, the requested name verbatim
      members: armed member composers (for a style; [] otherwise)
      armed:   whether the reference has corpus to anchor a brief
      note:    a human-readable status line
    """
    from .composition_brief import available_corpus_composers

    armed = set(available_corpus_composers())
    req = (request or "").strip()
    low = req.lower()

    # 1. Exact composer match (armed)
    base = low.split("-")[0].split("_")[0]
    if low in armed:
        return {
            "kind": "composer",
            "id": low,
            "members": [],
            "armed": True,
            "note": f"composer '{low}' (armed)",
        }
    if base in armed and not normalize_style(low):
        return {
            "kind": "composer",
            "id": base,
            "members": [],
            "armed": True,
            "note": f"composer '{low}' → '{base}' (armed)",
        }

    # 2. Style / genre request
    canon = normalize_style(low)
    if canon:
        members = style_members(canon, armed_only=True)
        sid = make_style_id(canon)
        if members:
            return {
                "kind": "style",
                "id": sid,
                "members": members,
                "armed": True,
                "note": (
                    f"style '{canon}' over {len(members)} armed composers: {', '.join(members)}"
                ),
            }
        # known style but nothing armed in it yet
        superset = all_style_members(canon)
        return {
            "kind": "style",
            "id": sid,
            "members": [],
            "armed": False,
            "note": (
                f"style '{canon}' has no armed composers yet — arm one "
                f"of {superset[:4]} with acquire_composer.py"
            ),
        }

    # 3. Unknown composer — suggest its style for fallback, but do not substitute
    fallback_styles = styles_for_composer(low)
    armed_fallback = [s for s in fallback_styles if style_members(s)]
    return {
        "kind": "unknown",
        "id": low,
        "members": [],
        "armed": False,
        "note": (
            f"'{req}' is not an armed composer or known style. "
            + (f"Closest armed style(s): {armed_fallback}. " if armed_fallback else "")
            + f"Arm it with `acquire_composer.py {base}` or pass a "
            f"style like 'classical'/'baroque'/'romantic'."
        ),
    }


def available_styles() -> List[Dict[str, Any]]:
    """Styles that currently have ≥1 armed composer (for status/UX)."""
    out = []
    for style in _STYLE_MEMBERS:
        members = style_members(style, armed_only=True)
        if members:
            out.append({"style": style, "members": members})
    return out
