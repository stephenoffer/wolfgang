"""What the top voice does at a cadence — blank in 856 of 856 scripts.

`cadence_scripts.json` carries a `soprano_line` field and `composition_brief`
reads it. The compiler hard-codes it to `[]`, in every script, for every
composer. So the brief could tell the agent WHICH cadence to write and never
what the melody does when it arrives — which is the half a listener hears. A
cadence is the most audible marker of style there is.

Measured over real V-I cadences rather than asserted from the textbook, because
the textbook answer turns out to be one composer's habit:

    composer     cadences   commonest approach -> arrival
    bach              636   2 -> 1   (stepwise from above)
    beethoven        1083   5 -> 1, then 7 -> 1
    chopin            618   5 -> 1
    mozart            539   5 -> 1, then 7 -> 1

And the arrival is the tonic only about a third of the time — the 5th on a fifth
of cadences, the 3rd on an eighth. A generated piece that lands every cadence on
the tonic in the melody is more final, more often, than any real composer.
"""

import pytest

from scales.composition_brief import cadence_soprano_lines, cadence_soprano_profile

pytestmark = pytest.mark.calibration


def _p(composer):
    profile = cadence_soprano_profile(composer)
    if not profile:
        pytest.skip(f"{composer} corpus not present")
    return profile


def test_enough_real_cadences_are_found_to_say_anything():
    """A detector that FINDS needs to find what is definitely there: every one
    of these composers wrote hundreds of V-I cadences."""
    for composer in ("bach", "mozart", "beethoven", "chopin"):
        assert _p(composer)["cadences"] >= 200, composer


def test_the_melody_does_not_land_on_the_tonic_most_of_the_time():
    """The finding that makes this worth telling the agent."""
    for composer in ("bach", "mozart", "beethoven", "chopin"):
        arrivals = dict(_p(composer)["arrivals"])
        total = _p(composer)["cadences"]
        assert arrivals.get(0, 0) / total < 0.5, (
            f"{composer} lands on the tonic {arrivals.get(0, 0) / total:.0%} of the time — "
            "if this were most cadences the guidance would be wrong"
        )


def test_bach_approaches_by_step_where_the_others_leap():
    """Bach's commonest is 2->1; Beethoven's and Chopin's is 5->1. A single
    textbook formula would have been one composer's habit taught to all."""

    def top_move(composer):
        return tuple(_p(composer)["moves"][0][0])

    assert top_move("bach") == (2, 0)
    assert top_move("beethoven")[0] != 2
    assert top_move("chopin")[0] != 2


def test_the_guidance_names_degrees_a_musician_would_use():
    text = " ".join(cadence_soprano_lines("mozart"))
    assert "the tonic" in text and "the 5th" in text
    assert "leading tone" in text or "the 2nd" in text or "the 3rd" in text
    assert "%" in text, "the shares are the evidence; state them"


def test_a_style_aggregates_its_members():
    style = cadence_soprano_profile("style__classical")
    if not style:
        pytest.skip("style profile not built")
    assert style["cadences"] > _p("mozart")["cadences"]
    assert style.get("members", 0) > 1


def test_an_unmeasurable_composer_says_nothing():
    assert cadence_soprano_profile("nobody_by_this_name") is None
    assert cadence_soprano_lines("nobody_by_this_name") == []
