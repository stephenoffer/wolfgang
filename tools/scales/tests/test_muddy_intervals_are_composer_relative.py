"""A count with no scale attached cannot tell a defect from the idiom.

`muddy_low_interval` — two notes a 2nd-to-3rd apart below C3, the "avoid thirds
below C3" rule of thumb — is the loudest finding the counterpoint analyser
produces: 392 of them across the workspace, all `info` severity, all bare counts.

Real composers disagree with that rule by two orders of magnitude, measured over
their own corpora:

    liszt        0.0938 / bar
    beethoven    0.0233
    mozart       0.0077
    chopin       0.0042
    haydn        0.0007
    bach         0.0007
    palestrina   0.0000   (in 60,677 bars — never once)

So the same figure means opposite things. A piece at 0.171 per bar is
unremarkable for Liszt and **22x his own practice** for Mozart, and the reviewer
had no way to tell which they were looking at.
"""

import pytest

from scales.composition_brief import muddy_low_interval_rate

# Measured; used as an ordering check, not as exact expectations.
RATES = {
    "palestrina": 0.0000,
    "haydn": 0.0007,
    "bach": 0.0007,
    "chopin": 0.0042,
    "mozart": 0.0077,
    "beethoven": 0.0233,
    "liszt": 0.0938,
}


@pytest.mark.parametrize("composer", sorted(RATES))
def test_every_armed_composer_has_a_measurable_rate(composer):
    rate = muddy_low_interval_rate(composer)
    assert rate is not None, f"{composer} has no corpus to measure"
    assert 0.0 <= rate < 0.5


def test_palestrina_never_writes_one():
    """60,677 bars of Renaissance vocal polyphony, zero. If this ever becomes
    non-zero the corpus or the detector has changed, not Palestrina."""
    assert muddy_low_interval_rate("palestrina") == 0.0


def test_the_composers_are_ordered_as_measured():
    """Liszt writes them freely and Haydn essentially never — an absolute
    threshold cannot serve both."""
    assert muddy_low_interval_rate("liszt") > muddy_low_interval_rate("beethoven")
    assert muddy_low_interval_rate("beethoven") > muddy_low_interval_rate("mozart")
    assert muddy_low_interval_rate("mozart") > muddy_low_interval_rate("haydn")


def test_an_unknown_composer_returns_none_rather_than_a_guess():
    assert muddy_low_interval_rate("nobody_by_this_name") is None


def test_the_rate_is_cached_not_recomputed():
    import scales.composition_brief as CB

    CB._MUDDY_RATE_CACHE.pop("mozart", None)
    first = muddy_low_interval_rate("mozart")
    assert "mozart" in CB._MUDDY_RATE_CACHE
    assert muddy_low_interval_rate("mozart") == first
