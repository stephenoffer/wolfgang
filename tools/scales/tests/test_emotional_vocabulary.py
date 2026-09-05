"""The emotion-to-music table was compiled into every pack and read by nothing.

`prompt_semantics.json` holds 74 emotion words per composer, each with a tempo
range, mode, dynamic, texture, register, articulation, rhythm type and harmonic
language. `style_resolver` loads all of it into `StyleProgram.prompt_semantics`
and deduplicates it. Grep for a consumer of that field and there is none:
compiled, loaded, deduped, dropped.

So a request for "a melancholy nocturne" reached the composer with none of what
this project already knows melancholy sounds like:

    melancholy   tempo 56-76   Minor/Aeolian   p-mp
                 texture "Medium, descending lines"   register "Mid-low"
                 articulation "Legato, sighing"   rhythm "Gentle, dragging"
                 harmony "iv-i, added 6ths"

The emotional content of the user's own request was being discarded between the
pack and the page — the least defensible place to lose it, and the same shape as
the two complete modules nothing imported.
"""

import pytest

from scales.composition_brief import (
    emotional_lines,
    emotional_vocabulary,
    match_emotional_words,
)

pytestmark = pytest.mark.calibration


def _vocab(composer="chopin"):
    table = emotional_vocabulary(composer)
    if not table:
        pytest.skip("packs not compiled")
    return table


def test_the_vocabulary_is_actually_large():
    """74 words with a full musical specification each."""
    assert len(_vocab()) >= 60


def test_a_feeling_in_the_intent_is_translated_into_music():
    lines = emotional_lines("a melancholy return", "chopin")
    text = " ".join(lines).lower()
    assert "melancholy" in text
    assert "56-76" in text, "the tempo range is the most concrete thing it knows"
    assert "aeolian" in text and "sighing" in text


def test_several_feelings_are_all_reported():
    text = " ".join(emotional_lines("triumph and grandeur at the climax", "chopin")).lower()
    assert "triumph" in text and "grandeur" in text


def test_the_longer_phrase_wins_over_the_word_inside_it():
    """ "gentle tension" and "tension" are both entries. Matching the short one
    first would describe the wrong feeling."""
    if "gentle tension" not in _vocab():
        pytest.skip("this vocabulary lacks the overlapping pair")
    hits = match_emotional_words("a passage of gentle tension", "chopin")
    assert hits and hits[0]["word"] == "gentle tension"


def test_a_word_inside_another_word_does_not_match():
    """ "pain" must not fire on "painting", or every intent matches something."""
    assert not [
        h for h in match_emotional_words("a painting of a garden", "chopin") if h["word"] == "pain"
    ]


def test_an_intent_with_no_feeling_named_says_nothing():
    assert emotional_lines("bar 5 continues the phrase", "chopin") == []
    assert emotional_lines("", "chopin") == []


def test_the_guidance_is_offered_not_imposed():
    """Only physical constraints are strict; this is doctrine, and the brief
    must say so or the agent will read a tempo range as a requirement."""
    text = " ".join(emotional_lines("a melancholy return", "chopin")).lower()
    assert "not a specification" in text


def test_an_unknown_composer_falls_back_rather_than_crashing():
    assert emotional_lines("melancholy", "nobody_by_this_name") == []


# ─── Where the feeling words actually live ───────────────────────────────────


def test_the_users_own_words_are_what_get_matched():
    """Matching only `creative_intent` under-fires badly.

    That string is built from `dramatic_plan.ROLE_INTENT` templates whose
    language is structural — "return", "establish", "intensify" — and names no
    emotion at all. The words a listener would recognise are in the REQUEST:
    "a melancholy nocturne". Wiring the table to the templated intent alone
    would have looked wired and fired on almost nothing.
    """
    from scales.composition_brief import _feeling_text

    class _Contract:
        description = "A melancholy nocturne in E-flat major"

    class _Narrative:
        overall_character = ""
        sections: list = []

    class _Graph:
        contract = _Contract()
        narrative = _Narrative()

    class _Slot:
        section_id = "m1_a"

    text = _feeling_text(_Graph(), _Slot())
    assert "melancholy" in text
    assert emotional_lines(text, "chopin"), "the request named a feeling and nothing was said"


def test_a_section_character_also_counts():
    from scales.composition_brief import _feeling_text

    class _Section:
        id = "m1_b"
        character = "shot through with dread, then longing"

    class _Narrative:
        overall_character = ""
        sections = [_Section()]

    class _Graph:
        contract = None
        narrative = _Narrative()

    class _Slot:
        section_id = "m1_b"

    words = {h["word"] for h in match_emotional_words(_feeling_text(_Graph(), _Slot()), "chopin")}
    assert "dread" in words or "longing" in words


def test_a_request_that_names_no_feeling_stays_silent():
    """ "A nocturne in E-flat major for solo piano, in the style of Chopin"
    names no emotion, and inventing one would be worse than saying nothing."""
    assert emotional_lines("A nocturne in E-flat major for solo piano", "chopin") == []


# ─── The vocabulary is nouns; people write adjectives ────────────────────────


def test_the_adjective_a_person_writes_reaches_the_noun():
    """The correction to my own earlier claim.

    Wiring the emotion table into the brief was real, and it fired on almost no
    actual request: the vocabulary is keyed on NOUNS — serenity, joy, melancholy,
    sorrow, triumph, playfulness, tenderness, mystery, anguish, peace, passion,
    nostalgia — and people write ADJECTIVES. Twelve of twelve natural prompts
    matched nothing, including the one that exposed it: a style brief for
    "A **serene** minuet in the classical style" came back with no emotional
    section at all.
    """
    pairs = [
        ("a serene minuet", "serenity"),
        ("a joyful rondo", "joy"),
        ("a melancholic nocturne", "melancholy"),
        ("a sorrowful adagio", "sorrow"),
        ("a triumphant finale", "triumph"),
        ("a playful scherzo", "playfulness"),
        ("a mysterious prelude", "mystery"),
        ("a tender song", "tenderness"),
        ("an anguished outcry", "anguish"),
        ("a peaceful evening", "peace"),
        ("a passionate declaration", "passion"),
        ("a nostalgic waltz", "nostalgia"),
    ]
    missed = [
        text
        for text, want in pairs
        if want not in {h["word"] for h in match_emotional_words(text, "mozart")}
    ]
    assert not missed, f"these natural requests still match nothing: {missed}"


def test_plain_musical_prose_matches_nothing():
    """The other half. A stem short enough to catch every adjective is also
    short enough to catch words that are not feelings at all."""
    for text in (
        "a sonata in three movements",
        "a fugue on a chromatic subject",
        "an etude in sixths",
        "a set of variations",
        "the recapitulation returns",
        "a painting of a garden",
        "bar 5 continues the phrase",
    ):
        assert not match_emotional_words(text, "mozart"), text


def test_melancholy_is_not_stemmed_as_an_adverb():
    """`melancholy` ends in "ly" and is not an adverb. Stripping it gave
    `melancho` where `melancholic` gives `melanchol`, so the one word most
    likely to appear in a request for a nocturne was the one that missed."""
    from scales.composition_brief import _emotion_stem

    assert _emotion_stem("melancholy") == _emotion_stem("melancholic")


def test_a_short_word_survives_stemming():
    """`joy` must not be eaten. `joyful` -> `joy` needs a floor of 3, not 4."""
    from scales.composition_brief import _emotion_stem

    assert _emotion_stem("joyful") == _emotion_stem("joy") == "joy"
