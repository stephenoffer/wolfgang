"""No movement is a scale model of its composer's corpus.

Accompaniment idioms are scheduled from the whole-corpus distribution, so a
piece uses `block_chord_sparse` at Mozart's corpus rate of 24%. But a real
movement picks an accompaniment and RETURNS to it; the aggregate is the average
of many such commitments and resembles none of them:

    composer    top idiom, pooled    top idiom, median movement
    chopin                  44.8%                         76.2%
    haydn                   21.0%                         37.9%
    beethoven               20.9%                         36.4%
    bach                    41.5%                         54.4%
    mozart                  29.1%                         33.5%

A Chopin movement gives three quarters of its bars to one accompaniment.
Measured on generated output, three of four pieces sit BELOW the 25th percentile
of real concentration — they change idiom more often than any real movement of
that composer does, Chopin at 46% against his median 77%.

Same correction as `movement_rate_range`, one level up: the rate belongs to the
movement, and so does the idiom mix.
"""

from __future__ import annotations

import collections
import statistics

import pytest

from scales.composition_brief import movement_idiom_mix

_COMPOSERS = ("mozart", "beethoven", "chopin", "haydn")


def test_the_measurement_reproduces_numbers_already_held():
    """Before trusting a new probe, check it answers a question already answered.

    Four of my probes today were wrong before the code was, and every one was
    caught only because its number could not be true — a tell, not a method.
    These four idiom shares were measured independently by another session.
    """
    from scripts.build_corpus_indexes import load_bars

    bars = load_bars("mozart")
    counts = collections.Counter(b.get("lh_texture") for b in bars if b.get("lh_texture"))
    total = sum(counts.values())
    if total < 1000:
        pytest.skip("corpus not available")
    for idiom, expected in (
        ("block_chord_sparse", 0.237),
        ("block_chord_offbeat", 0.104),
        ("bass_melody", 0.086),
        ("pedal_point", 0.034),
    ):
        assert abs(counts[idiom] / total - expected) < 0.02, (
            f"{idiom}: {counts[idiom] / total:.3f} against the held {expected}"
        )


def test_a_movement_commits_harder_than_the_corpus_does():
    """The claim the accessor exists for. If these agreed, it would be ceremony."""
    from scripts.build_corpus_indexes import group_by_source, load_bars

    gaps = []
    for composer in _COMPOSERS:
        bars = load_bars(composer)
        pooled = collections.Counter(b.get("lh_texture") for b in bars if b.get("lh_texture"))
        if not pooled:
            continue
        pooled_top = pooled.most_common(1)[0][1] / sum(pooled.values())
        per = []
        for _src, movement in group_by_source(bars).items():
            if len(movement) < 24:
                continue
            counts = collections.Counter(
                b.get("lh_texture") for b in movement if b.get("lh_texture")
            )
            if counts:
                per.append(counts.most_common(1)[0][1] / sum(counts.values()))
        if per:
            gaps.append(statistics.median(per) - pooled_top)
    if not gaps:
        pytest.skip("corpus not available")
    assert min(gaps) > 0, "some composer's median movement is LESS concentrated than his corpus"
    assert max(gaps) > 0.15, f"largest concentration gap is only {max(gaps):.3f}"


def test_it_returns_a_real_movements_mix_not_an_average_of_movements():
    """Averaging concentrations reproduces the same flattening one level down."""
    mix = movement_idiom_mix("chopin")
    if mix is None:
        pytest.skip("corpus not available")
    assert mix["source"], "no movement named — this is an average, not a movement"
    assert abs(sum(mix["idioms"].values()) - 1.0) < 0.01, mix["idioms"]
    assert mix["idioms"][mix["top_idiom"]] == max(mix["idioms"].values())
    # And it is a committed one, as Chopin's movements are.
    assert mix["idioms"][mix["top_idiom"]] > 0.5, mix["idioms"]


def test_the_spread_lets_a_piece_be_scored_rather_than_matched():
    """One movement is a sample; the spread is what a generated piece is judged
    against, exactly as `movement_rate_range` is used for the rates."""
    mix = movement_idiom_mix("mozart")
    if mix is None:
        pytest.skip("corpus not available")
    spread = mix["spread"]
    assert spread["min"] <= spread["p25"] <= spread["median"] <= spread["p75"] <= spread["max"]
    assert mix["movements"] >= 4


def test_too_few_movements_returns_none_rather_than_a_guess():
    assert movement_idiom_mix("no-such-composer") is None


# ─── How the idioms are laid out in time ─────────────────────────────────────


def test_the_run_measure_reproduces_numbers_already_held():
    """The probe precondition again, on the second measurement."""
    from scales.composition_brief import movement_idiom_runs

    held = {
        "chopin": (0.86, 20),
        "beethoven": (0.73, 12),
        "mozart": (0.37, 7),
        "haydn": (0.40, 6),
        "bach": (0.26, 5),
    }
    for composer, (share, longest) in held.items():
        stats = movement_idiom_runs(composer)
        if stats is None:
            pytest.skip("corpus not available")
        assert abs(stats["share_with_run_over_8"] - share) < 0.02, composer
        assert stats["longest_run_median"] == longest, composer


def test_a_movement_settles_somewhere():
    """The finding the measure exists for.

    Generated output already matches real practice on the TYPICAL figure — the
    dominant idiom's run is a median of 2-3 bars in both, and about a third of
    departures last exactly one bar in both. What it has never had is a passage
    that simply holds: our longest run is 2 to 6 bars for every composer, where
    86% of Chopin's movements contain a run of eight or more and his median
    longest is twenty.
    """
    from scales.composition_brief import movement_idiom_runs

    for composer in ("chopin", "beethoven"):
        stats = movement_idiom_runs(composer)
        if stats is None:
            pytest.skip("corpus not available")
        assert stats["share_with_run_over_8"] > 0.5, composer
        assert stats["longest_run_median"] >= 12, composer
        # And the typical run is still short — the tail is the whole point, and
        # a measure that reported long runs everywhere would be measuring wrong.
        assert stats["run_median"] <= 4, composer


def test_it_counts_the_dominant_idioms_runs_and_not_every_labels():
    """A first version reported a median run of 1 bar for every composer and
    would have concluded real movements never settle at all.

    It counted runs of EVERY label, and the one-bar departures outnumber the
    long stretches so completely that they set the median. Reading one real
    score bar by bar is what caught it — Chopin's Op. 28 No. 5 holds
    `broken_chord_wave` for 6 bars, 2, then 12, with single bars of `alberti`
    between — and no aggregate would have.
    """
    from scales.composition_brief import movement_idiom_runs

    stats = movement_idiom_runs("chopin")
    if stats is None:
        pytest.skip("corpus not available")
    assert stats["longest_run_median"] > 1, (
        "the measure is counting every label's runs again, where the one-bar "
        "departures swamp the dominant idiom's long stretches"
    )


# ─── One movement, described once ────────────────────────────────────────────


def test_combining_two_correct_accessors_describes_no_real_piece():
    """The error this profile exists to make impossible.

    `movement_idiom_mix` returns the movement at the median CONCENTRATION;
    `movement_rate_range` returns the median of a rate across all movements.
    Both verifiable alone. Together they describe different pieces — and the gap
    is not subtle:

        Chopin's Op. 28 No. 5 is 77% broken-chord wave and its actual left-hand
        chord share is 0.5%. Combining the two accessors targets 53.9%.

    A broken-chord wave is 2.3% chords where a block-chord bar is 86%, so a
    movement that is three quarters broken-chord wave CANNOT be half chords. A
    peer session built a thickening pass against exactly that pair of numbers.

    Third variety of the same-yardstick error, and the least visible: not two
    definitions of a quantity, not two scopes of one, but two correct statistics
    about DIFFERENT MEMBERS of the same population.
    """
    from scales.composition_brief import movement_profile, movement_rate_range

    profile = movement_profile("chopin")
    spread = movement_rate_range("chopin", "lh_chord_share")
    if profile is None or spread is None:
        pytest.skip("corpus not available")
    combined = spread["median"]
    coherent = profile["lh_chord_share"]
    assert abs(combined - coherent) > 0.3, (
        "the two accessors now agree for Chopin, which would make this test "
        f"vacuous: combined {combined}, coherent {coherent}"
    )
    assert profile["top_idiom"] == "broken_chord_wave"
    assert coherent < 0.1, profile


def test_a_profile_is_one_movement_and_says_which():
    """Everything in it comes from one set of bars, or it is an average again."""
    from scales.composition_brief import movement_profile

    for composer in _COMPOSERS:
        profile = movement_profile(composer)
        if profile is None:
            continue
        assert profile["source"], "no movement named"
        assert profile["bars"] >= 24
        assert abs(sum(profile["idioms"].values()) - 1.0) < 0.01
        for metric in ("ties_per_bar", "downbeat_rest_share", "lh_chord_share", "rh_chord_share"):
            assert metric in profile, metric
            assert 0.0 <= profile[metric] <= 10.0


def test_the_profile_agrees_with_the_mix_it_replaces():
    """It must pick the SAME movement `movement_idiom_mix` does, or there are
    now two answers to "which movement is representative"."""
    from scales.composition_brief import movement_profile

    for composer in _COMPOSERS:
        profile = movement_profile(composer)
        mix = movement_idiom_mix(composer)
        if profile is None or mix is None:
            continue
        assert profile["source"] == mix["source"], composer
        assert profile["idioms"] == mix["idioms"], composer
