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
