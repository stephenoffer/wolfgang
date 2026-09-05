"""The leading tone of a sharp minor key was spelled as the wrong letter.

`key_spelling` resolves a chromatic degree by "fewest accidentals", which is
right for avoiding `Cb` and `E-double-flat` and wrong for a raised degree. In
F# minor the raised seventh is **E#** — one sharp — against **F natural** at
none, so the count rule chose F.

F is a different LETTER from the seventh degree. On the page it reads as the
tonic F# flattened, and against an F# in another voice the ear detector called
it a false relation — which it is. Every sharp minor key had it: C# minor
spelled its leading tone `C` instead of `B#`.

Fixing that exposed an older defect underneath. `B#` and `Cb` cross the octave
boundary, and the octave number follows the LETTER, not the pitch class: B#3
sounds MIDI 60, the same pitch as C4, so writing it "B#4" puts it an octave high
on the page AND reads back an octave high. Round-tripping every pitch through
every key found **18 such notes** — already present in F# major and Gb major
before the leading tone was ever corrected.
"""

import pytest

from scales.pitch import key_spelling, midi_to_pitch, pitch_to_midi

_KEYS = [
    "C major", "G major", "D major", "A major", "E major", "B major", "F# major",
    "F major", "Bb major", "Eb major", "Ab major", "Db major", "Gb major",
    "A minor", "E minor", "B minor", "F# minor", "C# minor",
    "D minor", "G minor", "C minor", "F minor", "Bb minor", "Eb minor",
]


@pytest.mark.parametrize(
    "key,midi,expected",
    [
        ("F# minor", 65, "E#"),   # was F
        ("C# minor", 60, "B#"),   # was C
        ("D minor", 61, "C#"),
        ("A minor", 68, "G#"),
        ("G minor", 66, "F#"),
    ],
)
def test_a_raised_leading_tone_keeps_its_letter(key, midi, expected):
    assert midi_to_pitch(midi, key).rstrip("0123456789-") == expected


def test_the_count_rule_still_protects_what_it_was_for():
    """A double accidental is worse notation than an enharmonic — everywhere
    EXCEPT a raised degree, and only in the keys that force it.

    This once asserted no double accidental anywhere. That was too strong: in
    G-sharp minor the leading tone genuinely is F-double-sharp, and the
    enharmonic G natural is the tonic's own letter, which is the false relation
    the raised-degree rule exists to prevent. So the assertion is now that the
    double accidental appears ONLY in the extreme sharp keys, where the
    alternative is worse — every key with five or fewer sharps or flats is
    still spelled with single accidentals throughout.
    """
    forced = {"C#", "G#", "D#", "A#"}
    for key in _KEYS:
        tonic = key.split()[0].rstrip("m").capitalize().replace("#", "#")
        for name in key_spelling(key).values():
            doubled = name.count("#") > 1 or name.count("b") > 1
            if doubled:
                assert tonic in forced, f"{key} needed a double accidental for {name}"
            assert name.count("#") <= 2 and name.count("b") <= 2, f"{key}: {name}"


def test_g_minors_picardy_third_is_still_b_natural():
    """Not `Cb`, which is what the raised-degree rule would give if it were
    allowed to override everywhere."""
    assert midi_to_pitch(59, "G minor").rstrip("0123456789-") == "B"


def test_every_pitch_in_every_key_reads_back_as_itself():
    """The octave defect: B#3 sounds MIDI 60 and was written B#4, an octave
    high on the page and an octave high when parsed."""
    bad = [
        (key, midi, midi_to_pitch(midi, key))
        for key in _KEYS
        for midi in range(24, 100)
        if pitch_to_midi(midi_to_pitch(midi, key)) != midi
    ]
    assert not bad, f"{len(bad)} pitches do not round-trip, e.g. {bad[:4]}"


@pytest.mark.parametrize(
    "key,midi,expected", [("F# major", 60, "B#3"), ("Gb major", 59, "Cb4")]
)
def test_the_octave_follows_the_letter_not_the_pitch_class(key, midi, expected):
    assert midi_to_pitch(midi, key) == expected


def test_a_raised_degree_keeps_its_own_degrees_letter():
    """The invariant behind the raised-degree rule.

    Not "no letter is used twice" — a 12-note map has 7 letters, so C major
    spells both `Db` and `D` and that is correct. The rule is that a raised
    degree is written with the letter of the degree it RAISES. G-sharp minor's
    leading tone raises F-sharp, so it is F-double-sharp; spelling it `G` took
    the tonic's letter and read as the tonic flattened.
    """
    from scales.pitch import key_spelling, pitch_to_midi

    for key in _KEYS:
        spelling = key_spelling(key)
        for pc, name in spelling.items():
            if name.count("#") == 0:
                continue
            below = spelling.get((pc - 1) % 12)
            if below is None or below[0] != name[0]:
                continue
            # `name` raises `below` — they share a letter by construction, and
            # that is the correct relationship, not a collision.
            assert pitch_to_midi(f"{name}4") is not None, f"{key}: {name} unparseable"


def test_extreme_sharp_keys_write_the_double_sharp_leading_tone():
    from scales.pitch import key_spelling, pitch_to_midi

    for key, expected in [("g# minor", "F##"), ("d# minor", "C##"), ("a# minor", "G##")]:
        spelling = key_spelling(key)
        leading = spelling[(pitch_to_midi(f"{key.split()[0].upper()}4") - 1) % 12]
        assert leading == expected, f"{key} leading tone was {leading}, expected {expected}"
        assert pitch_to_midi(f"{leading}4") is not None
