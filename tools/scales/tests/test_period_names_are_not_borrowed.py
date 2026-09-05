"""A minimalist trill started on the upper note, which is Baroque practice.

`_PERIOD_PROFILES` shares performance parameters between periods on purpose — an
impressionist piece really is played with romantic freedom, a minimalist one with
classical precision. But it shared the profile OBJECT, so it shared the period
NAME, and `profile.period` is read to decide period-specific behaviour:

    ornament_realization: start_upper = period in ("baroque", "classical", "renaissance")

So everything the registry calls `modern` or `minimalist` — Glass, Reich,
Stravinsky, Schoenberg, Bartok, Copland, Messiaen, Prokofiev, Shostakovich,
Webern, Arvo Pärt — reported itself as "classical" and got upper-note trills,
wrong by a century and a half, and audible in the MIDI preview the critic judges.

The file already contains this exact fix for one period:
`_RENAISSANCE = replace(_BAROQUE, period="renaissance")`, with the note that
"Palestrina reporting himself as baroque is simply wrong". The other six
borrowings were left.
"""

from __future__ import annotations

import pytest

from scales.performance_params import _PERIOD_PROFILES, profile_for_composer


def _starts_on_the_upper_note(period: str) -> bool:
    """The rule `ornament_realization.realize_trill` actually applies."""
    return period in ("baroque", "classical", "renaissance")


@pytest.mark.parametrize("name,period", sorted(_PERIOD_PROFILES.items()))
def test_every_profile_reports_its_own_period(name, period):
    assert period.period == name, f"{name} reports itself as {period.period}"


UPPER_NOTE_COMPOSERS = ("palestrina", "monteverdi", "bach", "corelli", "mozart", "haydn")
MAIN_NOTE_COMPOSERS = (
    "chopin", "liszt", "debussy", "ravel", "mahler",
    "glass", "reich", "stravinsky", "schoenberg", "bartok", "prokofiev",
)


@pytest.mark.parametrize("composer", UPPER_NOTE_COMPOSERS)
def test_a_trill_before_1800_starts_above(composer):
    assert _starts_on_the_upper_note(profile_for_composer(composer).period), composer


@pytest.mark.parametrize("composer", MAIN_NOTE_COMPOSERS)
def test_a_trill_after_1800_starts_on_the_note(composer):
    assert not _starts_on_the_upper_note(profile_for_composer(composer).period), composer


def test_sharing_parameters_is_still_allowed():
    """The point is the NAME, not the numbers: an impressionist piece should
    still be played with romantic rubato."""
    impressionist = _PERIOD_PROFILES["impressionist"]
    romantic = _PERIOD_PROFILES["romantic"]
    assert impressionist.period != romantic.period
    from dataclasses import replace

    assert replace(impressionist, period="romantic") == romantic
