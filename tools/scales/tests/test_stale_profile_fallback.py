"""Discarding a stale profile is right; leaving nothing in its place is not.

`corpus_profile` detects a profile written before the `direction_changes_per_bar`
to `melody_direction_change_pct` rename and refuses it, because `self_evaluate`
narrows its bands to mean +- 2 sigma from these numbers and stale values become
the standard a section is judged against. That part is good.

But it then returned `{}` — and for an AGGREGATE reference (a style, or a
`blend:a+b`) the members' own profiles are current. `blend__beethoven-liszt`
has carried a June profile beside an August `density_stats.json`, so every piece
composed on that blend was compared against nothing at all, silently.

The remedy the warning named made it worse: `build_corpus_profiles` writes
per-composer packs and does not write aggregate ones, so for a blend it pointed
at a command that could not fix the problem.
"""

import scales.composition_brief as CB
from scales.composition_brief import _aggregate_members, corpus_profile


def setup_function():
    CB._PROFILE_CACHE.clear()
    CB._PACK_CACHE.clear()


def test_a_blend_resolves_to_its_member_composers():
    assert _aggregate_members("blend:beethoven+liszt") == ["beethoven", "liszt"]


def test_a_stale_aggregate_profile_falls_back_instead_of_emptying():
    profile = corpus_profile("blend:beethoven+liszt")
    metrics = (profile or {}).get("metrics") or {}
    assert metrics, "a blend whose members are armed must not be judged against nothing"


def test_the_fallback_is_a_current_profile():
    metrics = (corpus_profile("blend:beethoven+liszt") or {}).get("metrics") or {}
    assert "melody_direction_change_pct" in metrics
    assert "direction_changes_per_bar" not in metrics


def test_a_real_composer_profile_is_untouched():
    metrics = (corpus_profile("mozart") or {}).get("metrics") or {}
    assert "melody_direction_change_pct" in metrics


def test_the_substitution_is_announced(caplog):
    """Silent substitution is the failure this project has repeatedly recorded;
    the warning has to say it is not the blend's own distribution.

    The cache is cleared inside the capture block, not in setup: the warning
    fires on the MISS, so a profile already cached by an earlier test emits
    nothing and the assertion would pass or fail on test order."""
    import logging

    with caplog.at_level(logging.WARNING, logger="scales.composition_brief"):
        CB._PROFILE_CACHE.clear()
        CB._PACK_CACHE.clear()
        corpus_profile("blend:beethoven+liszt")
    assert "SUBSTITUTION" in caplog.text


def test_the_rebuild_advice_names_the_venv_interpreter(function_source):
    """`python` is not guaranteed to be the interpreter that has music21."""
    src = function_source(CB, "corpus_profile")
    if "build_corpus_profiles" in src:
        assert ".venv/bin/python -m scripts.build_corpus_profiles" in src
