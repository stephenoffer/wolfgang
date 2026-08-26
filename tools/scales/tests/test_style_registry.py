"""Unit tests for style_registry.py. Run: .venv/bin/python -m pytest tools/scales/tests/test_style_registry.py"""

import pytest

from scales import style_registry as SR


def test_normalize_and_synonyms():
    assert SR.normalize_style("classical") == "classical"
    assert SR.normalize_style("Galant") == "classical"
    assert SR.normalize_style("baroque-era") == "baroque"
    assert SR.normalize_style("nonsense-xyz") is None


def test_style_id_helpers():
    sid = SR.make_style_id("classical")
    assert sid == "style__classical"
    assert SR.is_style_id(sid)
    assert not SR.is_style_id("mozart")
    assert SR.style_name(sid) == "classical"
    assert SR.style_name("mozart") == "mozart"  # non-style passthrough


def test_members_armed_filtering():
    # classical members are armed (corpus present in this repo)
    members = SR.style_members("classical")
    assert "mozart" in members and "haydn" in members
    # superset includes composers that may not be armed
    assert set(SR.all_style_members("classical")) >= set(members)


def test_resolve_composer_vs_style_vs_unknown():
    assert SR.resolve_reference("mozart")["kind"] == "composer"
    r_style = SR.resolve_reference("classical")
    assert r_style["kind"] == "style" and r_style["id"] == "style__classical"
    assert r_style["armed"] and r_style["members"]
    r_unknown = SR.resolve_reference("rachmaninoff")
    assert r_unknown["kind"] == "unknown" and not r_unknown["armed"]


def test_unknown_style_with_no_armed_members():
    # impressionist is a known style but has no armed composers in this repo
    r = SR.resolve_reference("impressionist")
    assert r["kind"] == "style"
    assert r["armed"] is False
    assert r["members"] == []


def test_styles_for_composer():
    styles = SR.styles_for_composer("mozart")
    assert "classical" in styles


def test_available_styles_nonempty():
    avail = {s["style"] for s in SR.available_styles()}
    # at least the armed period styles in this repo
    assert {"classical", "baroque", "romantic"} <= avail


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")


# ─── Every composer must resolve to a style, and to its OWN genre data ───────


def test_every_compiled_pack_has_a_style():
    """A composer missing from `_STYLE_MEMBERS` is invisible to style references.

    Liszt sat unlisted while being one of only twelve armed composers, so
    "compose in a romantic style" drew on Chopin, Schubert and Weber and quietly
    ignored the Liszt corpus — and `genre_for("liszt")` fell through to
    "classical", handing a Liszt piece Classical texture-transition odds.
    """
    import os

    from scales.style_registry import _STYLE_MEMBERS

    packs_dir = os.path.join("tools", "compiled_packs")
    if not os.path.isdir(packs_dir):
        pytest.skip("compiled_packs not present")
    members = {m for v in _STYLE_MEMBERS.values() for m in v}
    packs = {
        d
        for d in os.listdir(packs_dir)
        if os.path.isdir(os.path.join(packs_dir, d))
        and not d.startswith(("style__", "blend__", "."))
    }
    missing = sorted(packs - members)
    assert not missing, (
        f"compiled pack(s) with no entry in _STYLE_MEMBERS: {missing} — these "
        "resolve to no style at all and drop to the classical genre fallback"
    )


def test_armed_composers_all_resolve_to_a_real_genre():
    """The armed composers are the ones whose corpus actually gets used."""
    import os

    from scales.style_registry import genre_for, styles_for_composer

    idx = os.path.join("tools", "reference_index")
    if not os.path.isdir(idx):
        pytest.skip("reference_index not present")
    armed = [d for d in os.listdir(idx) if os.path.isdir(os.path.join(idx, d))]
    unclassified = [c for c in armed if not styles_for_composer(c)]
    assert not unclassified, (
        f"armed composer(s) with no style: {sorted(unclassified)}; "
        f"genre_for gives them {[genre_for(c) for c in unclassified]}"
    )


def test_a_style_reference_loads_its_own_genre_matrix_not_classical():
    """The fallback was hard-coded to `by_genre/classical.json` for everyone.

    Genre matrices for baroque, romantic, late-romantic, impressionist, modern,
    minimalist, nationalistic and film-score sat unread beside it, so every
    style reference in the system was given Classical texture-transition odds —
    in the one place whose entire job is style fidelity.
    """
    from pathlib import Path

    from scales.style_registry import load_transition_matrix

    lib = Path("tools") / "pattern_library"
    if not (lib / "transitions" / "by_genre" / "romantic.json").exists():
        pytest.skip("pattern library not present")

    for ref, expected in (
        ("style__romantic", "romantic"),
        ("style__baroque", "baroque"),
        ("style__classical", "classical"),
    ):
        matrix = load_transition_matrix(ref, lib)
        assert matrix.get("genre") == expected, (
            f"{ref} loaded the {matrix.get('genre')!r} matrix, expected {expected!r}"
        )


def test_genre_for_falls_back_honestly_on_an_unknown_name():
    from scales.style_registry import genre_for

    assert genre_for("") == "classical"
    assert genre_for("someone-nobody-has-heard-of") == "classical"


def test_the_transition_matrix_loader_exists_only_once():
    """`PhraseBank` and `TransitionBank` carried byte-identical copies."""
    import ast
    import inspect

    from scales import phrase_bank, transition_bank

    for mod in (phrase_bank, transition_bank):
        tree = ast.parse(inspect.getsource(mod))
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            if fn.name != "_load_transition_matrix":
                continue
            # Strip the docstring — it *describes* the by_genre bug it fixed.
            stmts = [n for n in fn.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
            body = "\n".join(ast.unparse(n) for n in stmts)
            assert "load_transition_matrix" in body, (
                f"{mod.__name__}._load_transition_matrix does not delegate to "
                "style_registry.load_transition_matrix"
            )
            assert "by_genre" not in body, (
                f"{mod.__name__}._load_transition_matrix builds genre paths "
                "itself instead of delegating; that duplication is what fell "
                "back to classical.json for every composer"
            )


# ─── A composer id is not a safe path component ──────────────────────────────


def test_pack_dir_name_makes_a_blend_id_filesystem_safe():
    """`blend:beethoven+liszt` contains a colon, which Windows will not accept.

    Style ids were already written `style__<name>` precisely to avoid this;
    blends did not follow the convention, so a blended style could not compile
    on Windows at all.
    """
    assert ":" not in SR.pack_dir_name("blend:beethoven+liszt")
    assert SR.pack_dir_name("blend:beethoven+liszt") == "blend__beethoven-liszt"


def test_pack_dir_name_leaves_ordinary_ids_alone():
    """No migration for anything already on disk."""
    for name in ("mozart", "style__classical", "strauss-r", "arvo-part", "rimsky-korsakov"):
        assert SR.pack_dir_name(name) == name


def test_pack_dir_name_cannot_escape_the_packs_directory():
    """Composer names arrive from free text, and went straight into a path."""
    for hostile in ("../../etc/passwd", "a/b", "..", "./x", "~/.ssh"):
        try:
            safe = SR.pack_dir_name(hostile)
        except ValueError:
            continue  # refusing outright is also a correct outcome
        assert "/" not in safe and ".." not in safe, f"{hostile!r} -> {safe!r}"


def test_pack_dir_name_refuses_a_name_with_no_safe_form():
    """Better than silently mapping to the packs root and writing a pack over
    the directory that holds every other pack."""
    for empty in ("", "   ", "...", "___"):
        with pytest.raises(ValueError):
            SR.pack_dir_name(empty)


def test_every_pack_path_goes_through_the_sanitiser():
    """Seven read/write sites built `COMPILED_PACKS / composer` by hand."""
    import re
    from pathlib import Path

    offenders = []
    for name in (
        "context_compiler.py",
        "style_resolver.py",
        "donor_strategy.py",
        "composition_brief.py",
        "progression_model.py",
    ):
        path = Path("tools") / "scales" / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if re.search(r"(COMPILED_PACKS|_COMPILED_PACKS)\s*/\s*(composer|key)\b", line):
                offenders.append(f"{name}: {line.strip()}")
    assert not offenders, (
        "raw composer id used as a path component; route it through "
        "style_registry.pack_dir_name:\n  " + "\n  ".join(offenders)
    )


# ─── Genre matrices must come from real armed members ────────────────────────


def test_genre_matrices_are_not_contaminated_across_periods():
    """`baroque.json` was sourced from bach + handel + corelli **plus
    palestrina and monteverdi** — Renaissance polyphony folded into Baroque
    texture odds."""
    import json
    from pathlib import Path

    lib = Path("tools") / "pattern_library" / "transitions" / "by_genre"
    if not lib.is_dir():
        pytest.skip("pattern library not present")
    for path in sorted(lib.glob("*.json")):
        style = path.stem
        data = json.loads(path.read_text())
        sources = data.get("source_composers") or []
        if not sources:
            continue
        members = set(SR._STYLE_MEMBERS.get(style, []))
        strays = [c for c in sources if c not in members]
        assert not strays, (
            f"{path.name} is built from {strays}, which are not members of the "
            f"{style!r} style"
        )


def test_every_armed_style_has_a_real_matrix():
    """A style with armed members must not still be using the synthetic one.

    Six matrices were synthesised once from Classical with hand-picked
    multipliers and never rebuilt; `renaissance.json` did not exist at all, so
    Palestrina and Monteverdi fell through to Classical texture statistics.
    """
    import json
    import os
    from pathlib import Path

    idx = Path("tools") / "reference_index"
    lib = Path("tools") / "pattern_library" / "transitions" / "by_genre"
    if not idx.is_dir() or not lib.is_dir():
        pytest.skip("corpus not present")
    armed = {d for d in os.listdir(idx) if (idx / d).is_dir()}

    for style, members in SR._STYLE_MEMBERS.items():
        if not (set(members) & armed):
            continue  # no armed member — synthetic is the only option
        path = lib / f"{style}.json"
        assert path.exists(), f"{style} has armed members but no by_genre matrix"
        data = json.loads(path.read_text())
        assert not data.get("synthetic"), (
            f"{style} has armed members ({sorted(set(members) & armed)}) but its "
            "matrix is still the synthetic Classical derivative"
        )


def test_a_synthetic_matrix_is_declared_as_such():
    """A style with nothing armed may only use synthetic data if it says so."""
    import json
    from pathlib import Path

    lib = Path("tools") / "pattern_library" / "transitions" / "by_genre"
    if not lib.is_dir():
        pytest.skip("pattern library not present")
    for path in sorted(lib.glob("*.json")):
        data = json.loads(path.read_text())
        assert "synthetic" in data or data.get("source_composers"), (
            f"{path.name} declares neither real sources nor synthetic provenance"
        )
