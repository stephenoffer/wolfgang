"""An aggregate is for scoring; a member is for aiming at.

The same sentence came out true at three scales in one evening, and each time
the aggregate was simply the statistic that existed:

    a bar is not the average of bars
    a movement is not the average of movements
    a piece is not the average of pieces

Concretely, all three measured:

  * `block_chord_offbeat` bars are 82.2% chorded on average. 61% of them are
    ENTIRELY chords and 7% have none — the mean describes no bar in the corpus,
    and a generator writes one bar. Scored against the mean, retrieved patterns
    read a 16-point error; against the median bar they are exact.

  * Chopin's left hand pools to 38% chords and his median MOVEMENT is 54%. His
    downbeat-rest rate pools to 8.9% and his median movement is 3.0%. A pass
    composing to the pooled rate writes a piece three times more sustained than
    most of what he wrote.

  * And two correct member-level statistics can still be incoherent together:
    Op. 28 No. 5 is 77% broken-chord wave and 0.5% chords, while the median
    chord share across his movements is 53.9%. Combining the two accessors
    targets a movement that does not exist.

This file holds the naming convention that carries the distinction, so a reader
can tell which kind of number they have from its name alone.
"""

from __future__ import annotations

import inspect

import pytest

from scales import composition_brief, corpus_metrics

#: Names that mean "aggregated over whatever bars you gave me". Score against
#: the distribution of these across real movements; never aim at the value.
_AGGREGATE_SUFFIXES = ("_pct", "_ratio", "_cv", "_pooled", "_per_bar", "_share")

#: Names that mean "one real bar" or "one real movement" — what a generator is
#: given as a target.
_MEMBER_MARKERS = ("median_bar", "median_movement", "movement_profile", "movement_idiom")


def test_the_module_contract_is_stated_where_it_binds():
    """`corpus_metrics` is the shared yardstick, so the rule lives in it."""
    doc = corpus_metrics.__doc__ or ""
    assert "SCORING, NOT TARGETING" in doc
    assert "a bar is not the average of bars" in doc


#: The one name predating the convention. It is the median semitone span of a
#: bar's register, so it IS an aggregate; renaming it would invalidate the
#: `corpus_profile.json` of every armed composer, which is a real cost for a
#: naming nicety. Listed rather than renamed, and listed rather than quietly
#: excluded — an exception nobody can see is how a convention decays.
_PREDATES_THE_CONVENTION = {"register_span"}


def test_the_scalar_metrics_are_all_aggregates_by_name():
    """Every metric in the scoring vector should read as one."""
    odd = [
        m
        for m in corpus_metrics.SCALAR_METRICS
        if not m.endswith(_AGGREGATE_SUFFIXES)
        and not m.startswith(("mean_", "events_per_bar"))
        and m not in _PREDATES_THE_CONVENTION
    ]
    assert not odd, (
        f"metric(s) in the scoring vector whose name does not read as an aggregate: {odd}. "
        "A reader cannot tell whether to score against it or aim at it."
    )


def test_the_member_level_accessors_say_so_in_their_names():
    """A generator target must be identifiable without reading the body."""
    targets = [
        "movement_profile",
        "movement_idiom_mix",
        "movement_idiom_runs",
    ]
    for name in targets:
        assert hasattr(composition_brief, name), name
        assert any(marker in name for marker in _MEMBER_MARKERS), name
    assert hasattr(corpus_metrics, "median_bar_chord_share")


def test_the_median_bar_really_differs_from_the_mean():
    """Otherwise the whole distinction is ceremony.

    Reproduces figures held independently before asserting anything new.
    """
    import statistics

    from scripts.build_corpus_indexes import load_bars

    bars = []
    for composer in ("mozart", "beethoven", "chopin", "haydn", "bach"):
        bars += load_bars(composer)
    if len(bars) < 5000:
        pytest.skip("corpus not available")

    medians = corpus_metrics.median_bar_chord_share(bars)
    assert medians.get("block_chord_offbeat") == 1.0
    assert medians.get("alberti") == 0.0

    means = {}
    for bar in bars:
        idiom = bar.get("lh_texture")
        events = [e for e in (bar.get("lh_display") or []) if e.get("type") != "rest"]
        if not idiom or not events:
            continue
        means.setdefault(idiom, []).append(
            sum(1 for e in events if e.get("type") == "chord") / len(events)
        )
    offbeat = statistics.fmean(means["block_chord_offbeat"])
    assert 0.75 < offbeat < 0.90, offbeat
    assert abs(offbeat - medians["block_chord_offbeat"]) > 0.1, (
        "the mean and the median bar agree, which would make the distinction moot"
    )


def test_a_new_public_accessor_is_not_ambiguous():
    """A guard for the convention rather than for today's names.

    Anything public in `composition_brief` returning a per-composer number a
    generator could aim at should carry `movement` or `bar` in its name. This
    catches the next one at review time instead of after it has been aimed at.
    """
    suspicious = []
    for name, obj in vars(composition_brief).items():
        if name.startswith("_") or not inspect.isfunction(obj):
            continue
        if getattr(obj, "__module__", "") != "scales.composition_brief":
            continue
        doc = (obj.__doc__ or "").lower()
        if "median movement" not in doc and "median bar" not in doc:
            continue
        if not any(marker in name for marker in ("movement", "bar", "rate")):
            suspicious.append(name)
    assert not suspicious, (
        f"accessor(s) documented as member-level whose names do not say so: {suspicious}"
    )
