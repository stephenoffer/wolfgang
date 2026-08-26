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

from typing import Any

STYLE_PREFIX = "style__"

# Canonical period → member composers (supersets; filtered to armed at runtime).
# Names align with tools/pattern_library/transitions/by_genre/ and
# .claude/context/<genre>/ where they exist.
# A composer may belong to more than one style; `styles_for_composer` returns
# all of them. Every composer with a directory under `compiled_packs/` must
# appear here — an unlisted one resolves to no style at all, which silently
# excludes its corpus from every style reference and drops it to the hard-coded
# "classical" genre fallback. **Liszt** was missing from this table while being
# one of only twelve armed composers, so "compose in a romantic style" drew on
# Chopin, Schubert and Weber and quietly ignored the Liszt corpus entirely.
# `test_style_registry.py` fails if a compiled pack has no style.
_STYLE_MEMBERS: dict[str, list[str]] = {
    "renaissance": ["palestrina", "monteverdi"],
    "baroque": ["bach", "handel", "corelli", "vivaldi", "scarlatti"],
    "classical": ["mozart", "haydn", "beethoven", "clementi"],
    "romantic": [
        "chopin",
        "schubert",
        "schumann",
        "brahms",
        "weber",
        "liszt",
        "mendelssohn",
        "tchaikovsky",
    ],
    "late-romantic": [
        "mahler",
        "bruckner",
        "strauss-r",
        "elgar",
        "wagner",
        "rachmaninoff",
        "faure",
        "sibelius",
    ],
    "impressionist": ["debussy", "ravel", "satie"],
    "modern": [
        "bartok",
        "stravinsky",
        "prokofiev",
        "shostakovich",
        "copland",
        "schoenberg",
        "webern",
        "messiaen",
    ],
    "minimalist": ["glass", "reich", "arvo-part"],
    "nationalistic": [
        "dvorak",
        "grieg",
        "smetana",
        "mussorgsky",
        "rimsky-korsakov",
        "sibelius",
    ],
    "film-score": ["williams", "zimmer", "morricone"],
}

# Request synonyms → canonical style name.
_SYNONYMS: dict[str, str] = {
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


def normalize_style(name: str | None) -> str | None:
    """Map a free-text style/genre request to a canonical style name, or None.

    The ``style__`` prefix has to come off BEFORE separators are normalized.
    Replacing ``_`` with ``-`` first turned this system's own canonical id
    ``style__classical`` into ``style--classical``, which then failed the
    prefix test, was never stripped, and matched nothing — so
    ``normalize_style`` returned None for every ``style__`` id the system
    itself produces, and with it ``all_style_members`` and ``style_members``
    returned an empty list for all four armed styles.
    """
    if not name:
        return None
    n = str(name).strip().lower()
    if n.startswith(STYLE_PREFIX):
        n = n[len(STYLE_PREFIX) :]
    n = n.replace(" ", "-").replace("_", "-")
    if n in _STYLE_MEMBERS:
        return n
    return _SYNONYMS.get(n)


def is_style_id(ref: str | None) -> bool:
    return bool(ref) and str(ref).startswith(STYLE_PREFIX)


def style_name(ref: str) -> str:
    return ref[len(STYLE_PREFIX) :] if is_style_id(ref) else ref


def make_style_id(name: str) -> str:
    canon = normalize_style(name) or str(name).strip().lower()
    return f"{STYLE_PREFIX}{canon}"


def all_style_members(style: str) -> list[str]:
    """Full membership superset for a canonical style (ignores arming)."""
    return list(_STYLE_MEMBERS.get(normalize_style(style) or style, []))


def style_members(style: str, armed_only: bool = True) -> list[str]:
    """Members of a style. When armed_only, keep only composers with corpus."""
    members = all_style_members(style)
    if not armed_only:
        return members
    from .composition_brief import available_corpus_composers

    armed = set(available_corpus_composers())
    return [m for m in members if m in armed]


def styles_for_composer(composer: str) -> list[str]:
    """Which styles a composer belongs to (used for unknown-composer fallback)."""
    c = (composer or "").lower().split("-")[0].split("_")[0]
    out = []
    for style, members in _STYLE_MEMBERS.items():
        if any(m.split("-")[0] == c for m in members):
            out.append(style)
    return out


def resolve_reference(request: str | None) -> dict[str, Any]:
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


def available_styles() -> list[dict[str, Any]]:
    """Styles that currently have ≥1 armed composer (for status/UX)."""
    out = []
    for style in _STYLE_MEMBERS:
        members = style_members(style, armed_only=True)
        if members:
            out.append({"style": style, "members": members})
    return out


# ─── Filesystem-safe pack directory names ────────────────────────────────────


def pack_dir_name(composer_id: str) -> str:
    """The directory name a composer/style/blend id gets under `compiled_packs/`.

    A composer id came straight from the user's request into a filesystem path
    with no sanitising, which had two consequences.

    The mild one: a blend id is built as ``blend:beethoven+liszt`` (see
    `style_resolver.resolve_blend_program`), and a colon is not a legal filename
    character on Windows, so a blended style could not compile there at all.
    Style ids were already written ``style__<name>`` precisely to avoid this —
    the convention existed and blends did not follow it.

    The sharper one: nothing stopped a name containing ``/`` or ``..`` from
    walking out of `compiled_packs/` entirely. Composer names arrive from free
    text ("compose something like Kapustin"), and `acquire_composer` will
    happily be pointed at whatever it is given.

    Empty or fully-stripped input is refused rather than silently mapped to the
    packs root — writing a pack over the directory that holds every other pack
    is not a failure mode worth having.
    """
    raw = str(composer_id or "").strip()
    # ':' separates the blend marker from its members; '+' joins the members.
    safe = raw.replace(":", "__").replace("+", "-")
    safe = "".join(c if (c.isalnum() or c in "-_.") else "_" for c in safe)
    safe = safe.strip("._")
    if not safe:
        raise ValueError(f"composer id {composer_id!r} has no filesystem-safe form")
    return safe


# ─── Texture-transition matrices ─────────────────────────────────────────────

_MATRIX_CACHE: dict[str, dict[str, Any]] = {}


def genre_for(composer: str) -> str:
    """The genre whose corpus data stands in when a composer has none of its own.

    Both `PhraseBank` and `TransitionBank` carried a byte-identical
    `_load_transition_matrix` that fell back to `by_genre/classical.json` for
    *every* composer. There are genre matrices for baroque, romantic,
    late-romantic, impressionist, modern, minimalist, nationalistic and
    film-score sitting unused beside it, so a Bach piece with no composer matrix
    was given Classical texture-transition odds, and so was a
    ``style__romantic`` one — silently, and in the one place whose entire job is
    style fidelity.
    """
    ref = (composer or "").strip().lower()
    if not ref:
        return "classical"
    if is_style_id(ref):
        name = style_name(ref)
        return name if name in _STYLE_MEMBERS else "classical"
    if ref in _STYLE_MEMBERS:
        return ref
    styles = styles_for_composer(ref)
    return styles[0] if styles else "classical"


def load_transition_matrix(composer: str, pattern_library: Any) -> dict[str, Any]:
    """Load a composer's LH texture-transition matrix, or its genre's.

    The single implementation. `pattern_library` is the ``pattern_library/``
    Path (callers already hold it).
    """
    ref = (composer or "").strip().lower() or "classical"
    if ref in _MATRIX_CACHE:
        return _MATRIX_CACHE[ref]

    import json

    candidates = [
        pattern_library / "transitions" / "by_composer" / f"{ref}.json",
        pattern_library / "transitions" / "by_genre" / f"{genre_for(ref)}.json",
        pattern_library / "transitions" / "by_genre" / "classical.json",
    ]
    for path in candidates:
        try:
            if path.exists():
                with open(path) as fh:
                    matrix = json.load(fh)
                _MATRIX_CACHE[ref] = matrix
                return matrix
        except (OSError, ValueError):
            continue
    _MATRIX_CACHE[ref] = {"counts": {}}
    return _MATRIX_CACHE[ref]
