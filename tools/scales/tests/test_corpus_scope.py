"""A corpus is a sample of a composer, and this one is a narrow sample.

Every statistic in this system is computed over the corpus and presented as a
fact about the composer. Measuring what the corpora actually contain:

    bach        100% four-part chorales      (ornament rate 0.003 trills/bar)
    haydn       100% string quartets         (used to teach PIANO writing)
    chopin      100% mazurkas                (0.2% of notes faster than a 16th)
    mozart      100% piano sonatas
    beethoven   100% piano sonatas
    palestrina  100% masses and motets
    monteverdi  100% madrigals

Bach's 6,795 bars and Chopin's 4,853 are not thin, so the size-based caveat
missed both. Narrowness is a separate failure and needs its own warning.
"""

import pytest

from scales.composition_brief import (
    corpus_scope,
    render_corpus_scope,
    render_rhythmic_fingerprint,
)


def _scope(c):
    sc = corpus_scope(c)
    if not sc.get("bars"):
        pytest.skip(f"{c} corpus not present")
    return sc


@pytest.mark.parametrize(
    "composer,genre",
    [
        ("bach", "four-part chorales"),
        ("haydn", "string quartets"),
        ("chopin", "mazurkas"),
        ("mozart", "piano sonatas"),
        ("palestrina", "masses and motets"),
        ("monteverdi", "madrigals"),
    ],
)
def test_each_corpus_is_identified_for_what_it_is(composer, genre):
    sc = _scope(composer)
    assert sc["dominant"] == genre, sc["genres"]
    assert sc["narrow"], sc


def test_a_large_but_single_genre_corpus_is_still_flagged():
    """The whole point. Bach has 410 source movements — and all 410 are
    chorales, so counting sources called the corpus broad."""
    sc = _scope("bach")
    assert sc["bars"] > 5000
    assert sc["narrow"]


def test_the_warning_names_the_genre_and_defers_to_the_composer():
    text = " ".join(render_corpus_scope("haydn"))
    assert "string quartets" in text
    assert "not haydn entire" in text
    assert "trust what you know" in text


def test_the_fingerprint_inherits_the_narrowness_caveat():
    """Bach passes every size test and must still be qualified."""
    head = render_rhythmic_fingerprint("bach")[0]
    assert "THIS IS THE SAMPLE, NOT THE COMPOSER" in head
    assert "four-part chorales" in head


def test_the_scope_warning_reaches_the_brief_first():
    """It qualifies every number after it, so it has to come before them."""
    import inspect

    from scales import composition_brief as cb

    src = inspect.getsource(cb)
    assert "render_corpus_scope(brief.composer)" in src
    assert src.index("render_corpus_scope(brief.composer)") < src.index(
        "render_rhythmic_fingerprint(brief.composer)"
    )
