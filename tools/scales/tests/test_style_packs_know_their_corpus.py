"""Composing "in the classical style" was treated as a sparse corpus.

Found by composing a piece in a STYLE rather than as a composer — the one path
real composition had never driven. `compile_style(piece, "classical")` reported:

    composer_id=classical  tier=D  fingerprints=0  lh_textures=0  donor_plan=True

against `compile_style(piece, "mozart")` at tier A with 10 left-hand textures.
Tier C/D is what triggers `DonorStrategy` in `compile_style`, so the classical
style — mozart, haydn and beethoven together, ~27,800 bars, the richest corpus
this system has — was augmented with a donor as though it were thin.

Two causes, both "an id in one vocabulary used in another":

1. `pack_dir_name("classical")` returned `"classical"`. Style packs are written
   `style__<name>` and `resolve_reference` returns that id, but `compile_style`
   threads the user's own word through, so `_load_pack` looked for
   `compiled_packs/classical/`, found nothing, and every field fell to its
   default — including `support_tier` "D".

2. `_pass_manifest` classifies the tier from `reference_index/<id>/bar_index.json`
   and the pattern registry, and there is no `reference_index/style__classical/`.
   A style's corpus is the union of its members'.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from scales.context_compiler import ContextCompiler
from scales.style_registry import pack_dir_name

STYLES = ["classical", "baroque", "romantic", "renaissance"]


@pytest.mark.parametrize("style", STYLES)
def test_a_bare_style_name_finds_its_pack(style):
    assert pack_dir_name(style) == f"style__{style}"


def test_a_composer_keeps_his_own_pack():
    """Only redirect when there is no pack of that name — a composer who happens
    to share a style word must not be sent to the style's pack."""
    for composer in ("mozart", "bach", "chopin", "palestrina"):
        assert pack_dir_name(composer) == composer


def test_a_blend_id_is_still_filesystem_safe():
    assert pack_dir_name("blend:beethoven+liszt") == "blend__beethoven-liszt"


@pytest.mark.parametrize("style", STYLES)
def test_a_style_counts_its_members_corpora(style):
    """The failing condition: 0 bars, hence tier C/D, hence a donor."""
    manifest = ContextCompiler()._pass_manifest(style, "", None)
    assert manifest["corpus_bar_count"] > 1000, manifest
    assert manifest["support_tier"] == "A", manifest


@pytest.mark.parametrize("style", STYLES)
def test_the_style_id_form_works_too(style):
    """`compile_style` passes the bare word; `resolve_reference` returns the id.
    Both reach the same place or the defect comes back through the other door."""
    bare = ContextCompiler()._pass_manifest(style, "", None)
    prefixed = ContextCompiler()._pass_manifest(f"style__{style}", "", None)
    assert bare["corpus_bar_count"] == prefixed["corpus_bar_count"]
    assert bare["support_tier"] == prefixed["support_tier"] == "A"


def test_a_styles_bar_count_is_the_sum_of_its_members():
    """Not merely "more than zero" — the right number."""
    from scales.style_registry import style_members

    total = 0
    for member in style_members("classical"):
        index = pathlib.Path("tools/reference_index") / member / "bar_index.json"
        if index.exists():
            total += json.loads(index.read_text()).get("total_bars", 0)
    assert ContextCompiler()._pass_manifest("classical", "", None)["corpus_bar_count"] == total


@pytest.mark.parametrize("style", STYLES)
def test_a_style_resolves_to_its_members_tier(style):
    """Read at LOAD time, not off the manifest. The style manifests say "C" and
    nothing can regenerate them: `build_style_profiles` writes only the corpus
    profile, and running the COMPILER on a style destroys the pack, because a
    style has no `composer-profiles/<name>/` directory to build from."""
    from scales.style_resolver import StyleResolver

    resolver = StyleResolver()
    assert resolver.resolve_program(style, "").dna.tier == "A"
    assert resolver.resolve_program(f"style__{style}", "").dna.tier == "A"


def test_a_composers_tier_is_untouched():
    from scales.style_resolver import StyleResolver

    resolver = StyleResolver()
    assert resolver.resolve_program("mozart", "").dna.tier == "A"


@pytest.mark.parametrize("style", STYLES)
def test_compiling_a_style_does_not_overwrite_its_pack(style, tmp_path, monkeypatch):
    """The damage this caused: the compiler builds a pack from a composer's
    markdown profile directory. A style has none, so every pass wrote EMPTY over
    the aggregate — `style__classical` lost its instruments, textures and worked
    prototypes, and the loss is to the SHARED pack, inherited by every later
    piece in that style. Verified by doing it and having
    `test_style_packs_carry_doctrine` catch it."""
    from scales import scales as S

    monkeypatch.setattr(S, "_WORKSPACE", tmp_path)
    S.init_workspace("style-pack-guard", "compose_from_text", description="probe")

    pack = pathlib.Path("tools/compiled_packs") / f"style__{style}"
    before = {f.name: f.read_bytes() for f in pack.glob("*.json")}
    S.compile_style("style-pack-guard", style)
    after = {f.name: f.read_bytes() for f in pack.glob("*.json")}
    changed = [n for n in before if before[n] != after.get(n)]
    assert not changed, f"compile_style('{style}') rewrote {changed}"


def test_compiling_a_style_leaves_no_bare_named_pack():
    """The bare-name pack is what defeated the redirect: once
    `compiled_packs/classical/` exists, `pack_dir_name` stops redirecting."""
    packs = pathlib.Path("tools/compiled_packs")
    for style in STYLES:
        assert not (packs / style).is_dir(), (
            f"compiled_packs/{style}/ exists — a bare style-name pack shadows "
            f"style__{style} and sends every lookup back to the defaults"
        )


def test_a_style_profile_carries_the_same_features_as_a_composer_profile():
    """`build_style_profiles` aggregated `SCALAR_METRICS` alone — 13 of the 39
    that `build_corpus_profiles` builds for a composer. `compare_to_corpus`
    scores a piece on whatever the profile carries, so a piece written "in the
    classical style" was judged on texture and rhythm only, and the missing 26
    were the harmony/melody/rhythm-value fingerprint plus sonority — exactly the
    dimensions that separate one classical composer from another.
    """
    composer = set(
        json.loads(
            (pathlib.Path("tools/compiled_packs/mozart/corpus_profile.json")).read_text()
        )["metrics"]
    )
    for style in STYLES:
        profile = pathlib.Path(f"tools/compiled_packs/style__{style}/corpus_profile.json")
        if not profile.exists():
            pytest.skip(f"style__{style} profile not built")
        got = set(json.loads(profile.read_text())["metrics"])
        assert not (composer - got), (
            f"style__{style} is missing {sorted(composer - got)[:8]} — a style is "
            f"scored on fewer dimensions than any of its members"
        )


def test_the_style_builder_merges_all_three_metric_sources():
    """Parsed, so a rename cannot slip past. The composer builder merges
    bar_metrics + style_fingerprint + sonority_metrics; this one merged one."""
    import ast

    tree = ast.parse(pathlib.Path("tools/scripts/build_style_profiles.py").read_text())
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    for source in ("bar_metrics", "style_fingerprint", "sonority_metrics"):
        assert source in called, f"build_style_profiles never calls {source}"
