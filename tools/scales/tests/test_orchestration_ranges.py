"""Practical instrument ranges, and what a dynamic costs at the extremes.

Audit item E14: `INSTRUMENT_RANGES` has no practical-vs-extreme distinction and
no per-dynamic limits, and the orchestration planner clamped every part to the
outer edge of what an instrument can physically produce.

That is the difference between a part a player can read and one they dread. Every
wind instrument's bottom minor third is unwieldy and its top is effortful; a
flute's low octave will not speak quietly and a trumpet's top cannot be played
pianissimo at all. Clamping an octave transfer to the physical limit lands notes
in exactly those places — legal, and unplayable as written.
"""

import pytest

from scales.orchestration_planner import _range_of, practical_range, range_warnings

# ─── The practical range is inside the physical one ──────────────────────────


@pytest.mark.parametrize(
    "instrument", ["flute", "oboe", "clarinet", "bassoon", "horn", "trumpet", "trombone"]
)
def test_a_winds_practical_range_is_narrower_than_its_physical_one(instrument):
    full_lo, full_hi = _range_of(instrument)
    lo, hi = practical_range(instrument)
    assert full_lo <= lo < hi <= full_hi
    assert (lo, hi) != (full_lo, full_hi), f"{instrument} was not trimmed at all"


def test_strings_keep_almost_all_of_their_range():
    """Strings are far more forgiving than winds; only the very top is awkward."""
    full_lo, full_hi = _range_of("violin")
    lo, hi = practical_range("violin")
    assert lo == full_lo, "a violin's bottom string is perfectly usable"
    assert full_hi - hi <= 8


def test_an_unknown_instrument_gets_no_false_confidence():
    """Guessing a trim for an instrument with no entry is worse than none."""
    assert practical_range("theremin") == _range_of("theremin")


# ─── A soft dynamic narrows it further ───────────────────────────────────────


def test_a_trumpet_cannot_play_softly_at_the_top():
    normal_hi = practical_range("trumpet")[1]
    soft_hi = practical_range("trumpet", "pp")[1]
    assert soft_hi < normal_hi


def test_a_flute_will_not_speak_softly_at_the_bottom():
    normal_lo = practical_range("flute")[0]
    soft_lo = practical_range("flute", "pp")[0]
    assert soft_lo > normal_lo


def test_a_loud_dynamic_does_not_narrow_the_range():
    assert practical_range("trumpet", "ff") == practical_range("trumpet")


def test_a_string_range_is_unaffected_by_dynamic():
    """A violin plays quietly anywhere; the restriction is a wind problem."""
    assert practical_range("violin", "pp") == practical_range("violin")


def test_the_oboe_is_restricted_at_both_ends_when_soft():
    """It honks at the bottom and cannot be played softly at the top."""
    lo, hi = practical_range("oboe")
    soft_lo, soft_hi = practical_range("oboe", "pp")
    assert soft_lo > lo and soft_hi < hi


# ─── Warnings ────────────────────────────────────────────────────────────────


def test_a_note_outside_the_instrument_entirely_is_named_as_such():
    warnings = range_warnings("trumpet", [95])
    assert warnings and "outside the instrument's range entirely" in warnings[0]


def test_a_weak_low_note_is_distinguished_from_an_impossible_one():
    weak = range_warnings("flute", [61])
    impossible = range_warnings("flute", [40])
    assert weak and "outside the instrument's range entirely" not in weak[0]
    assert impossible and "outside the instrument's range entirely" in impossible[0]


def test_the_dynamic_is_named_when_it_is_the_reason():
    warnings = range_warnings("flute", [60], dynamic="pp")
    assert warnings and "will not speak at this dynamic" in warnings[0]

    loud = range_warnings("flute", [60], dynamic="ff")
    assert not loud or "will not speak at this dynamic" not in loud[0]


def test_comfortable_writing_draws_no_warnings():
    assert range_warnings("violin", [60, 67, 72], dynamic="mf") == []
    assert range_warnings("clarinet", [55, 62, 70], dynamic="mf") == []


def test_warnings_are_advisory_not_a_clamp():
    """A shrieking piccolo at a climax is a choice, not a defect."""
    warnings = range_warnings("piccolo", [100], dynamic="ff")
    # It reports; it does not refuse, and nothing here modifies a pitch.
    assert isinstance(warnings, list)


def test_the_range_never_inverts():
    """A trim that would cross itself must fall back, not produce lo > hi."""
    for instrument in ("piccolo", "tuba", "trumpet", "soprano", "bass"):
        for dyn in (None, "pp", "ppp", "ff"):
            lo, hi = practical_range(instrument, dyn)
            assert lo < hi, f"{instrument} at {dyn} inverted: ({lo}, {hi})"
