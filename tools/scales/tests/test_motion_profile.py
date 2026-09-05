"""Three more things the brief never told the composer.

`voicing_profile` covered how THICK to write. This covers how the music MOVES:
whether the line steps or leaps, how fast the harmony turns over, and where on
the keyboard the writing lives. Each has a spread far too wide for a default to
serve, measured over the corpus:

    melodic motion       harmonic rhythm        lowest note
    monteverdi 85% step  bach       2.51/bar    liszt    39
    palestrina 81% step  palestrina 2.42/bar    brahms   39
    bach       74% step  handel     2.26/bar    schubert 44
    mozart     61% step  liszt      2.28/bar    chopin   46
    haydn      60% step  mozart     1.75/bar    mozart   53
    beethoven  54% step  beethoven  1.67/bar    haydn    52
    chopin     50% step  chopin     1.84/bar
    liszt      36% step

(Bach read 86% until his corpus was rebuilt on 2026-08-27; the extractor had
been collapsing the chorales' simultaneities, which changed the melodic line
those intervals were measured from. 74% is his real figure, and the stepwise
pole is vocal polyphony, where it belongs.)
    debussy    44% step  beethoven  1.61/bar
    liszt      36% step  schubert   1.45/bar

Liszt leaps where Monteverdi steps. Bach turns his harmony nearly twice as often
as Schubert. The bottom of Liszt's keyboard is a minor seventh below Mozart's.

A generated piece that steps politely through the middle of the keyboard
changing chord once a bar is plausible for nobody in particular — which is what
"generic" sounds like, and none of these three was measurable from anything the
brief previously said.
"""

import pytest

from scales.composition_brief import motion_lines, motion_profile

pytestmark = pytest.mark.calibration


def _profile(composer):
    profile = motion_profile(composer)
    if not profile:
        pytest.skip(f"{composer} corpus not present")
    return profile


# ─── Melodic motion ──────────────────────────────────────────────────────────


def test_a_leaping_composer_and_a_stepwise_one_are_far_apart():
    """Liszt at 36% stepwise against Monteverdi at 85% is the whole point.

    This used Bach as the stepwise pole at a threshold of 0.75, which he cleared
    only while his corpus was collapsing the chorales' simultaneities — the
    melodic line was being read off a texture that was not there. He measures
    0.736 now. The pole is vocal polyphony, which is stepwise because it must be
    singable.
    """
    assert _profile("monteverdi")["step_share"] > 0.75
    assert _profile("liszt")["step_share"] < 0.50


def test_renaissance_polyphony_is_the_most_stepwise_of_all():
    """A singable line: every leap is answered by a step in the other direction."""
    assert _profile("palestrina")["step_share"] > 0.75


def test_the_ordering_is_the_musical_one():
    assert _profile("palestrina")["step_share"] > _profile("bach")["step_share"]
    assert _profile("bach")["step_share"] > _profile("mozart")["step_share"]
    assert _profile("mozart")["step_share"] > _profile("liszt")["step_share"]


# ─── Harmonic rhythm ─────────────────────────────────────────────────────────


def test_baroque_harmony_turns_over_faster_than_romantic():
    """Bach moves within the bar; Schubert prolongs across it."""
    assert _profile("bach")["harmonies_per_bar"] > _profile("schubert")["harmonies_per_bar"]


def test_the_harmonic_rhythm_spread_is_wide_enough_to_matter():
    """If every composer sat near one value there would be nothing to say."""
    rates = [_profile(c)["harmonies_per_bar"] for c in ("bach", "mozart", "chopin", "schubert")]
    assert max(rates) / min(rates) > 1.4, f"harmonic rhythm barely varies: {rates}"


# ─── Tessitura ───────────────────────────────────────────────────────────────


def test_the_romantic_keyboard_reaches_lower_than_the_classical_one():
    """Liszt's bottom is a minor seventh below Mozart's."""
    assert _profile("liszt")["low"] < _profile("mozart")["low"] - 6


def test_the_range_is_ordered_and_plausible():
    for composer in ("bach", "mozart", "chopin", "liszt"):
        profile = _profile(composer)
        assert 20 < profile["low"] < profile["high"] < 108


# ─── The same guards as the voicing profile ──────────────────────────────────


def test_a_single_source_corpus_reports_nothing():
    """Weber's corpus is one clarinet work — see `test_voicing_profile`."""
    assert motion_profile("weber") is None
    assert motion_lines("weber") == []


def test_a_style_aggregates_its_members():
    style = motion_profile("style__baroque")
    if not style:
        pytest.skip("style profile not built")
    assert style.get("members", 0) > 1
    assert style["intervals"] > motion_profile("bach")["intervals"]


def test_an_unmeasurable_composer_says_nothing():
    assert motion_profile("nobody_by_this_name") is None
    assert motion_lines("nobody_by_this_name") == []


# ─── What the agent is told ──────────────────────────────────────────────────


def test_the_guidance_inverts_with_the_measurement():
    leaping = " ".join(motion_lines("liszt")).lower()
    stepping = " ".join(motion_lines("palestrina")).lower()
    assert "leaps" in leaping and "scalar melody is the wrong" in leaping
    assert "by step" in stepping


def test_the_heading_does_not_collide_with_the_existing_key_motion_section():
    """The brief already has a `KEY MOTION` section. Two headings sharing a word
    is how a reader conflates two different things — the same class as a metric
    that shares a name with another metric."""
    heading = motion_lines("chopin")[1]
    assert heading.startswith("MELODIC MOTION & HARMONIC RHYTHM")
