"""The brief never told the composer how THICK to write.

It carried what the left hand plays, how dense the bar is, which rhythms recur,
which ornaments belong and what the harmony should do — and not one word about
how many notes sound in the melody. So a generated Chopin nocturne came back
with a right hand that is a bare single line in 99% of its attacks, against a
real-Chopin figure of 22%.

Nothing caught it, and nothing could have. Measured per movement, the 10th
percentile of right-hand chord share is **0.00**, because some real movements
genuinely are single-line throughout. No distribution test separates a piece
that is single-line all the way through from a real one that is. It is not a
defect a threshold finds; it is something the composer has to be told before
writing a note.

Measured over the corpus, the range is far too wide for one number:

    liszt      50.5%      brahms     16.9%
    debussy    28.4%      bach       10.4%
    chopin     27.0%      mozart      8.5%
    schubert   19.5%      handel      6.9%
    beethoven  17.3%      haydn       6.7%
                          palestrina  0.0%

(Bach read **0.7%** until his corpus was rebuilt on 2026-08-27 — a four-part
chorale reduced to two staves cannot have almost no simultaneities, and the
extractor had been collapsing them. His real figure is 10.4%, ABOVE Mozart's,
which is right: the chorales are homophonic. The tests below once used him as
the contrapuntal pole and passed only because the data was broken.)

which is also why the guidance cannot be "add some chords".
"""

import pytest

from scales.composition_brief import voicing_lines, voicing_profile

pytestmark = pytest.mark.calibration


def _share(composer):
    profile = voicing_profile(composer)
    if not profile:
        pytest.skip(f"{composer} corpus not present")
    return profile["rh_chord_share_pooled"]


# ─── The measurement separates the idioms ────────────────────────────────────


def test_a_chordal_composer_measures_far_above_a_contrapuntal_one():
    """Liszt's right hand is chordal half the time; a Palestrina part never is.

    This used Bach as the contrapuntal pole, on a corpus that recorded him as
    having 0.0% chords across 14,238 attacks. His corpus is CHORALES — four-part
    homophony — so that was a broken measurement, not a thin texture, and the
    test was asserting the breakage. The genuine pole is vocal polyphony, where
    one part is one singer and there is nothing to thicken.
    """
    assert _share("liszt") > 0.35
    assert _share("palestrina") < 0.01


def test_the_ordering_is_the_musical_one():
    """Romantic piano writing is thicker than Classical, which is thicker than
    a single vocal line. If this ever inverts, the measurement is broken.

    Bach is deliberately NOT in this chain. Each corpus is one genre, and his
    is the chorales, whose four-part homophony is thicker than a Mozart sonata's
    right hand — so "Baroque is thinner than Classical" is a statement about
    keyboard idiom that his corpus cannot be asked to support.
    """
    assert _share("liszt") > _share("chopin") > _share("mozart") > _share("palestrina")


def test_vocal_polyphony_has_no_chords_at_all():
    """A Palestrina part is one singer. There is nothing to thicken."""
    assert _share("palestrina") == 0.0


# ─── Styles aggregate their members, and did not ─────────────────────────────


def test_a_style_is_not_just_its_first_member():
    """`_iter_corpus_bars` yields a style's members one composer at a time, so
    the bar cap stopped inside the FIRST — `style__romantic` came back as
    Chopin's numbers to three decimal places, which is what gave it away."""
    style = voicing_profile("style__romantic")
    chopin = voicing_profile("chopin")
    if not style or not chopin:
        pytest.skip("corpus not present")
    assert style.get("members", 0) > 1
    assert style["attacks"] > chopin["attacks"]
    assert style["rh_chord_share_pooled"] != chopin["rh_chord_share_pooled"]


def test_the_styles_track_the_history_of_keyboard_texture():
    """Renaissance 0%, Baroque ~4%, Classical ~11%, Romantic ~24%."""
    shares = {}
    for style in ("style__renaissance", "style__baroque", "style__classical", "style__romantic"):
        profile = voicing_profile(style)
        if not profile:
            pytest.skip(f"{style} not built")
        shares[style] = profile["rh_chord_share_pooled"]
    ordered = list(shares.values())
    assert ordered == sorted(ordered), f"texture thickness is not monotone by period: {shares}"


# ─── What the agent is actually told ─────────────────────────────────────────


def test_the_guidance_differs_by_idiom_not_only_the_number():
    """ "Add some chords" would be wrong for eight of the eleven composers."""
    chordal = " ".join(voicing_lines("liszt")).lower()
    linear = " ".join(voicing_lines("palestrina")).lower()
    assert "chordal" in chordal and "octaves" in chordal
    assert "single line" in linear and "not chords" in linear
    assert "octaves" not in linear, "Bach must not be told to write the tune in octaves"


def test_the_section_names_its_evidence():
    """A claim the agent cannot trace is a claim it should discount."""
    text = " ".join(voicing_lines("chopin"))
    assert "real chopin attacks" in text
    assert "semitones" in text


def test_an_unmeasurable_composer_says_nothing():
    """Silence beats a number invented from forty bars."""
    assert voicing_profile("nobody_by_this_name") is None
    assert voicing_lines("nobody_by_this_name") == []


# ─── A number needs more than one score behind it ────────────────────────────


def test_a_single_source_corpus_yields_no_voicing_claim():
    """Weber's entire corpus is ONE clarinet work.

    A clarinet cannot play a chord, so 1,200 measured attacks produced a
    confident 0.0% — and the brief would have told a composer writing Weber, a
    Romantic piano composer, that his idiom is a bare single line. The count of
    attacks looked like plenty. It was one piece of orchestration, not a habit.

    This is the reason the guard is on SOURCES and not on sample size: a large
    sample of the wrong thing is still the wrong thing, and it arrives looking
    more trustworthy than a small one.
    """
    assert voicing_profile("weber") is None
    assert voicing_lines("weber") == []


def test_a_composer_with_real_breadth_still_reports():
    """The guard must not silence everyone thin."""
    for composer in ("chopin", "bach", "mozart"):
        assert voicing_profile(composer), composer


# ─── the left hand has a thickness too ───────────────────────────────────────


def _lh_share(composer):
    profile = voicing_profile(composer)
    if not profile:
        pytest.skip(f"{composer} corpus not present")
    return profile["lh_chord_share_pooled"]


def test_the_left_hand_thickness_is_measured_at_all():
    """This section reported the left hand's SPAN and never its thickness, so
    the composer was told the melody is 8% chords and nothing whatever about the
    accompaniment — which in real Mozart is 21%, more than double."""
    assert _lh_share("mozart") > 0.1


def test_the_left_hand_is_thicker_than_the_right_in_keyboard_writing():
    """Melody-and-accompaniment: the tune is a line, the chords are underneath.
    Every keyboard composer measured shows it."""
    for composer in ("mozart", "haydn", "beethoven", "chopin"):
        rh = voicing_profile(composer)
        if not rh:
            continue
        assert rh["lh_chord_share_pooled"] > rh["rh_chord_share_pooled"], (
            f"{composer}: LH {rh['lh_chord_share_pooled']} is not above RH {rh['rh_chord_share_pooled']}"
        )


def test_a_chorale_bass_is_not_chordal():
    """Bach's corpus is four-part chorales: the bass is ONE VOICE, so its staff
    holds one note. His right hand, carrying soprano and alto, is thicker than
    his left — the reverse of every keyboard composer, and a real fact about the
    idiom rather than a measurement failure."""
    profile = voicing_profile("bach")
    if not profile:
        pytest.skip("bach corpus not present")
    assert profile["lh_chord_share_pooled"] < 0.05
    assert profile["rh_chord_share_pooled"] > profile["lh_chord_share_pooled"]


def test_vocal_polyphony_has_no_chords_in_either_hand():
    assert _lh_share("palestrina") == 0.0


def test_the_guidance_names_the_left_hand_separately():
    """One instruction for both hands would be wrong for every composer
    measured: they differ by a factor of two or more."""
    for composer in ("mozart", "chopin"):
        lines = " ".join(voicing_lines(composer)).lower()
        if not lines:
            continue
        assert "left hand" in lines or "accompaniment" in lines
        assert "right-hand" in lines or "melody" in lines


def test_a_style_blends_the_left_hand_too():
    style = voicing_profile("style__romantic")
    if not style:
        pytest.skip("style__romantic not built")
    assert "lh_chord_share_pooled" in style
    assert style["lh_chord_share_pooled"] > 0
