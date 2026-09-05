"""A suggestion must quote the threshold it actually applied.

The critic reads `musical_prose` first and is told to trust it. It contained:

    The right hand averages 1.14 notes per attack — below the 1.06 minimum of
    every real movement measured.

1.14 is not below 1.06. The check was right — the floor is COMPOSER-SCOPED and
Chopin's right hand runs 1.30-2.43 notes per attack, so 1.14 genuinely fires —
but the sentence hard-coded `1.06`, which is the LEFT hand's minimum. The
reviewer was handed a number that was the wrong hand, arithmetically false
against the value beside it, and unrelated to the threshold actually used.

A self-contradicting concern is worse than a missing one: it invites the reader
to discount the rest.
"""

import re

from scales.voicing import _FLOOR, VoicingReport, _suggest, floors_for


def _report(**kw) -> VoicingReport:
    """A report that is unremarkable except for what the caller sets, so only
    the check under test can fire."""
    r = VoicingReport()
    r.bars = [None] * 16  # `_suggest` needs 8+ bars to say anything
    r.registers_used = ("bass", "tenor", "alto", "soprano", "high")
    r.register_span = 48
    r.single_line_rh_pct = 0.10
    r.texture_shift_pct = 0.50
    r.thirds_sixths_pct = 0.20
    r.simultaneity_cv = 0.30
    r.rh_notes_per_attack = 1.60
    r.lh_notes_per_attack = 1.60
    for k, v in kw.items():
        setattr(r, k, v)
    return r


def _fire_rh(value: float, floor: dict) -> str:
    r = _report(rh_notes_per_attack=value)
    _suggest(r, floor)
    return next((s for s in r.suggestions if "right hand averages" in s), "")


def test_the_message_quotes_the_floor_that_was_applied():
    floor = dict(_FLOOR, rh_notes_per_attack=1.18)
    msg = _fire_rh(1.14, floor)
    assert msg, "the check must fire below its floor"
    assert "1.18" in msg
    assert "1.06" not in msg, "1.06 is the LEFT hand's minimum"


def test_the_quoted_number_is_arithmetically_above_the_measured_one():
    """The sentence says 'below X' — X must actually exceed the value."""
    for applied in (1.12, 1.18, 1.30):
        floor = dict(_FLOOR, rh_notes_per_attack=applied)
        msg = _fire_rh(applied - 0.04, floor)
        quoted = [float(n) for n in re.findall(r"\b\d\.\d{2}\b", msg)]
        assert len(quoted) >= 2, msg
        measured, threshold = quoted[0], quoted[1]
        assert measured < threshold, f"'{msg}' is self-contradicting"


def test_a_value_above_the_floor_says_nothing():
    floor = dict(_FLOOR, rh_notes_per_attack=1.12)
    assert not _fire_rh(1.40, floor)


def test_the_left_hand_message_quotes_its_own_floor():
    r = _report(lh_notes_per_attack=1.00)
    floor = dict(_FLOOR, lh_notes_per_attack=1.04)
    _suggest(r, floor)
    msg = next((s for s in r.suggestions if "left hand averages" in s), "")
    assert msg and "1.04" in msg


def test_chopins_floor_really_is_stricter_than_the_generic_one():
    """If this ever stops being true the message would be quoting a constant
    again without anyone noticing."""
    assert floors_for("chopin", None)["rh_notes_per_attack"] > _FLOOR["rh_notes_per_attack"]
