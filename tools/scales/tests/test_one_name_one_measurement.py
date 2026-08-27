"""Two different numbers were both called the composer's "LH chord share".

A peer session reverted a tuning change because it could not verify it: three
values were in play — 37.9% from corpus events, 29.2% from `voicing_profile`,
43.5% from the assembled score — and it was targeting one while measuring
another. Taken apart, the three were not three definitions:

  * the DEFINITIONS agree. Counting `lh_display` events with more than one
    distinct pitch and counting `lh_events` of type `chord` give 0.182 vs 0.186
    for Mozart and 0.539 vs 0.539 for Chopin, over the same bars.

  * two of the numbers differ only in SCOPE — pooled over every attack, versus
    the median of the per-movement distribution. Chopin pools to 0.380 and his
    median movement is 0.539; Haydn pools to 0.119 and his median movement is
    0.013. Both are right, and they answer different questions.

  * the third was a SAMPLING ARTEFACT. `voicing_profile` capped at the first
    4,000 bars, which is not a sample of a composer but of whichever sources
    sort first — 24 of Beethoven's 99 works, 57 of Chopin's 99 — and it read
    0.292 for Chopin where his whole corpus reads 0.379.

So: the sample strides evenly across the corpus, and the pooled measure carries
`_pooled` in its name. Never let two metrics share a name.
"""

from __future__ import annotations

import pytest

from scales.composition_brief import (
    MOVEMENT_METRICS,
    _iter_corpus_bars,
    _sampled_corpus_bars,
    movement_rate_range,
    voicing_profile,
)

_COMPOSERS = ("mozart", "beethoven", "chopin", "haydn")


def test_the_sample_covers_the_whole_corpus_not_its_first_bars():
    """The prefix cap saw a quarter of Beethoven and called it Beethoven."""
    thin = []
    for composer in _COMPOSERS:
        every = {b.get("source") for b in _iter_corpus_bars(composer)}
        sampled = {b.get("source") for b in _sampled_corpus_bars(composer)}
        if not every:
            continue
        if len(sampled) < len(every):
            thin.append(f"{composer}: {len(sampled)} of {len(every)} works")
    assert not thin, "the voicing sample misses whole works:\n  " + "\n  ".join(thin)


def test_the_sample_is_still_capped():
    """Guard the guard — striding must not have quietly become a full pass."""
    from scales.composition_brief import _VOICING_MAX_BARS

    for composer in _COMPOSERS:
        assert len(_sampled_corpus_bars(composer)) <= _VOICING_MAX_BARS


def test_the_pooled_share_matches_the_whole_corpus():
    """A truncated sample read Chopin 23% low; an even one must not."""
    from scales.composition_brief import _event_midis

    for composer in _COMPOSERS:
        profile = voicing_profile(composer)
        if not profile:
            continue
        attacks = chords = 0
        for bar in _iter_corpus_bars(composer):
            for event in bar.get("lh_display") or []:
                midis = _event_midis(event)
                if not midis:
                    continue
                attacks += 1
                if len(set(midis)) > 1:
                    chords += 1
        if attacks < 1000:
            continue
        truth = chords / attacks
        got = profile["lh_chord_share_pooled"]
        assert abs(got - truth) < 0.02, f"{composer}: sampled {got:.3f} vs whole corpus {truth:.3f}"


def test_the_pooled_and_per_movement_measures_do_not_share_a_name():
    """The rule this file exists for."""
    profile = voicing_profile("chopin")
    assert profile is not None
    assert "lh_chord_share_pooled" in profile
    assert "lh_chord_share" not in profile, (
        "the pooled measure is using the bare name again — a caller reading it "
        "beside `movement_rate_range(..., 'lh_chord_share')` gets two different "
        "numbers under one name, which is how a tuning change becomes unverifiable"
    )
    assert "lh_chord_share" in MOVEMENT_METRICS


def test_the_two_scopes_genuinely_differ_so_the_split_is_not_cosmetic():
    """If they agreed everywhere, one name would have been fine and this whole
    exercise would be ceremony. They do not."""
    apart = []
    for composer in _COMPOSERS:
        profile = voicing_profile(composer)
        spread = movement_rate_range(composer, "lh_chord_share")
        if not profile or not spread or spread.get("median") is None:
            continue
        apart.append(abs(profile["lh_chord_share_pooled"] - spread["median"]))
    if not apart:
        pytest.skip("corpus not available")
    assert max(apart) > 0.05, f"largest pooled-vs-median gap is only {max(apart):.3f}"
