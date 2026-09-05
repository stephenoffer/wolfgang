"""'We cannot tell' and 'it is broad' are different answers.

`corpus_scope().narrow` is False whenever the dominant genre is unknown, and
`render_corpus_scope` returned NOTHING when narrow was False. So a corpus whose
sources this project cannot identify produced silence — which reads as "this
corpus is broad enough, carry on" — for **18 of 27 composers**.

Haydn was the sharpest case: the general table classifies his quartets by the
`opusNNnoN/movement` convention, but a third of his bars are filed as a bare
`movement4`, so his dominant genre came out as *unclassified at 35%* and a
corpus that is two-thirds string quartets said nothing at all.
"""

import scales.composition_brief as CB
from scales.composition_brief import corpus_scope, render_corpus_scope


def setup_function():
    CB._SCOPE_CACHE.clear()


def test_an_unidentifiable_corpus_says_so_instead_of_staying_quiet():
    sc = corpus_scope("schubert")
    assert not sc["scope_known"]
    msg = render_corpus_scope("schubert")
    assert msg and "unknown" in msg[0].lower()


def test_a_known_narrow_corpus_still_names_its_genre():
    msg = render_corpus_scope("mozart")
    assert msg and "piano sonatas" in msg[0]


def test_a_genuinely_broad_corpus_stays_silent():
    """Silence is only correct when we actually know the corpus is broad."""
    sc = corpus_scope("haydn")
    assert sc["scope_known"] and not sc["narrow"]
    assert render_corpus_scope("haydn") == []


def test_haydns_quartets_are_recognised_by_their_own_filing():
    """A third of his bars are `movement4` with no opus prefix."""
    sc = corpus_scope("haydn")
    assert sc["dominant"] == "string quartets"
    assert dict(sc["genres"]).get("unclassified", 1.0) < 0.05


def test_the_loose_pattern_is_scoped_to_the_composer_it_is_true_for():
    """`^movement\\d+$` in the general table would swallow half of every other
    corpus. It is only a fact about the composer whose corpus is one genre."""
    assert "haydn" in CB._COMPOSER_GENRE_PATTERNS
    assert all("movement" not in pat for _name, pat in CB._GENRE_PATTERNS if "quartet" not in _name)


def test_classified_share_and_scope_known_agree():
    for composer in ("mozart", "haydn", "schubert", "bach"):
        sc = corpus_scope(composer)
        assert sc["scope_known"] == (sc["classified_share"] > 0.5)
