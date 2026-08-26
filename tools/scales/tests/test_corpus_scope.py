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
    render_rhythmic_fingerprint,
)


def _scope(c):
    sc = corpus_scope(c)
    if not sc.get("bars"):
        pytest.skip(f"{c} corpus not present")
    return sc


# These tests originally pinned the CONTENTS of each corpus — haydn "string
# quartets 100%", chopin "mazurkas 100%". Broadening those two corpora then broke
# four tests that were describing a snapshot rather than a behaviour. What must
# hold is the mechanism: a single-genre corpus is detected and reported.


def test_a_single_genre_corpus_is_detected(monkeypatch):
    from scales import composition_brief as cb

    bars = [{"source": f"bach/bwv{i}.6"} for i in range(200)]
    monkeypatch.setattr(cb, "_iter_corpus_bars", lambda c: iter(bars))
    cb._SCOPE_CACHE.pop("synthetic", None)
    sc = cb.corpus_scope("synthetic", refresh=True)
    assert sc["dominant"] == "four-part chorales"
    assert sc["dominant_share"] == 1.0
    assert sc["narrow"]


def test_a_mixed_corpus_is_not_flagged(monkeypatch):
    from scales import composition_brief as cb

    bars = [{"source": f"bach/bwv{i}.6"} for i in range(100)]
    bars += [{"source": f"chopin_nocturne_op9_n{i}"} for i in range(100)]
    monkeypatch.setattr(cb, "_iter_corpus_bars", lambda c: iter(bars))
    cb._SCOPE_CACHE.pop("mixed", None)
    sc = cb.corpus_scope("mixed", refresh=True)
    assert not sc["narrow"], sc["genres"]


def test_music21_work_ids_are_classified():
    """music21's bundled corpora carry no genre label, only a work id, and both
    this project ingests are a single genre. A looser pattern read Bach as 54%
    chorale and concluded his corpus was broad."""
    import re

    from scales.composition_brief import _GENRE_PATTERNS

    def label(src):
        for name, pat in _GENRE_PATTERNS:
            if re.search(pat, src):
                return name
        return "unclassified"

    assert label("bach/bwv371") == "four-part chorales"
    assert label("bach/bwv248.64-6") == "four-part chorales"
    assert label("opus74no1/movement4") == "string quartets"
    assert label("hob-xvi-28-iii-presto") == "piano sonatas"
    assert label("chopin_nocturne_op9_n3") == "nocturnes"
    assert label("mazurka33-4") == "mazurkas"


def test_the_warning_names_the_genre_and_defers_to_the_composer(monkeypatch):
    from scales import composition_brief as cb

    bars = [{"source": f"opus74no{i}/movement1"} for i in range(200)]
    monkeypatch.setattr(cb, "_iter_corpus_bars", lambda c: iter(bars))
    cb._SCOPE_CACHE.pop("q", None)
    text = " ".join(cb.render_corpus_scope("q"))
    assert "string quartets" in text
    assert "not q entire" in text
    assert "trust what you know" in text


def test_at_least_one_real_corpus_is_still_single_genre():
    """A live canary: some corpora here really are one genre, and if this ever
    stops being true the warning has done its job."""
    from scales.composition_brief import available_corpus_composers, corpus_scope

    armed = available_corpus_composers()
    if not armed:
        pytest.skip("no armed composers")
        return
    assert any(corpus_scope(c).get("narrow") for c in armed)


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
