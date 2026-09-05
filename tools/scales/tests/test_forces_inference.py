"""Reading the performing forces out of a request.

Nothing read them at all, and the two attempts to fix that each broke the other
direction:

  1. Every request was `solo_piano`. "A short sacred motet for FOUR VOICES in
     the Dorian mode" had the pianist's hand-span limit applied to Tenor and
     Bassus as though they were one hand, and failed its commit with "lh span
     19 semitones exceeds max 16" — true of a hand, meaningless for two singers.

  2. The fix for that over-corrected, and the over-correction was worse. "A
     two-voice invention in D minor FOR KEYBOARD" came back `choir`, because
     "N-voice" is the standard way to describe keyboard counterpoint and the
     named instrument in the same sentence was never consulted. The piece routed
     down the ensemble path and exported with the LEFT HAND AS A CELLO — two
     instruments instead of a grand staff, no brace, LH on its own MIDI channel.
     That path is also the documented cause of the voice-overlap bar overflow
     that desyncs the hands.

  3. And the fix for THAT had a substring collision: "chorale" contains
     "choral", so "a chorale prelude for organ" — a solo organ work — was a
     choir again.

Three word classes and word-boundary matching. These cases are the record of
what each version got wrong, so a fourth version has to keep all of them.
"""

import pytest

from scales.scales import _infer_instrumentation

# ─── Keyboard counterpoint is not a choir ────────────────────────────────────


@pytest.mark.parametrize(
    "description",
    [
        "a two-voice invention in D minor for keyboard",
        "a three-voice fugue for harpsichord",
        "a four-voice fugue for organ",
        "a two-part invention for piano",
        "a 3-voice ricercar for clavier",
        "a four-part fugue for organ",
    ],
)
def test_n_voice_counterpoint_with_a_named_instrument_is_not_a_choir(description):
    """ "N-voice" counts contrapuntal LINES, not people."""
    assert _infer_instrumentation(description) is None, description


@pytest.mark.parametrize(
    "description",
    ["a chorale prelude for organ", "an organ mass", "a chorale prelude on a hymn for organ"],
)
def test_vocal_REPERTOIRE_with_a_named_instrument_stays_a_keyboard_work(description):
    """A chorale prelude and an organ mass are solo organ literature."""
    assert _infer_instrumentation(description) is None, description


# ─── But an unqualified vocal request is still vocal ─────────────────────────


@pytest.mark.parametrize(
    "description,expected",
    [
        ("a short sacred motet for four voices in the Dorian mode", "choir"),
        ("a work for four voices", "choir"),
        ("an anthem for SATB", "choir"),
        ("a cappella setting", "choir"),
        ("a mass", "choir"),
        ("a madrigal", "choir"),
        ("a requiem", "choir"),
        ("a four-part chorale harmonization", "choir"),
    ],
)
def test_an_unqualified_vocal_request_is_vocal(description, expected):
    """No instrument named, so "four voices" means four people."""
    assert _infer_instrumentation(description) == expected, description


def test_singers_beat_the_orchestra_they_sing_with():
    """ "A cantata for choir and orchestra" is choral, not orchestral."""
    assert _infer_instrumentation("a cantata for choir and orchestra") == "choir"
    assert _infer_instrumentation("a mass for choir and orchestra") == "choir"


def test_a_named_keyboard_is_not_a_shortcut_past_the_ensemble_words():
    """Or "a piano trio" resolves to a solo keyboard piece."""
    assert _infer_instrumentation("a piano trio") == "ensemble"
    assert _infer_instrumentation("a piano concerto in A minor") == "ensemble"
    assert _infer_instrumentation("a piano quintet") == "ensemble"


@pytest.mark.parametrize(
    "description,expected",
    [
        ("a string quartet in C", "ensemble"),
        ("a symphony in G", "ensemble"),
        ("a wind octet", "ensemble"),
        ("orchestral suite", "ensemble"),
        ("a nocturne for piano", None),
        ("a mazurka", None),
        ("a sonata for solo piano", None),
        ("", None),
        (None, None),
    ],
)
def test_the_ordinary_cases(description, expected):
    assert _infer_instrumentation(description) == expected


# ─── Words that only LOOK like forces ────────────────────────────────────────


def test_a_bass_line_is_not_a_bass_singer():
    """Single voice-part names are deliberately not force words: "double bass",
    "bass line" and "soprano recorder" are all instruments."""
    assert _infer_instrumentation("a piece with a walking bass line for piano") is None
    assert _infer_instrumentation("a duet for soprano recorder and harpsichord") is None


def test_chorale_does_not_match_choral():
    """The substring collision, named. `chorale` ⊃ `choral`."""
    assert _infer_instrumentation("a chorale prelude for organ") is None
    assert _infer_instrumentation("a choral work") == "choir"
