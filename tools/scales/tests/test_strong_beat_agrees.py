"""Two implementations of "is this beat stressed", and they disagreed.

`duration.is_strong_beat` was a hand-enumerated table. It had 4/4, 3/4, 2/4 and
6/8 right, **9/8 wrong** — it named beats 1.0, 2.0 and 3.0, where the three
dotted-quarter beats of 9/8 actually fall at 1.0, 2.5 and 4.0 — **no entry for
12/8 at all**, so a nocturne in 12/8 had exactly one stressed beat per bar
instead of four, and nothing for cut time.

`performance_renderer.is_strong_beat` derives the same answer from
`metric_weight` and was right. Beats are counted in QUARTER-NOTE units, which is
what makes compound metre the trap: its beats are not on the integers.
"""

import pytest

from scales.duration import is_strong_beat
from scales.performance_renderer import is_strong_beat as by_weight

METERS = [(4, 4), (3, 4), (2, 4), (2, 2), (4, 2), (6, 8), (9, 8), (12, 8), (3, 8), (5, 4), (7, 8)]


@pytest.mark.parametrize("meter", METERS)
def test_the_two_implementations_agree(meter):
    """A convention living in two places is two conventions unless they match."""
    for i in range(25):
        beat = 1.0 + i * 0.5
        assert is_strong_beat(beat, meter) == by_weight(beat, meter), (meter, beat)


def test_compound_metre_beats_are_not_on_the_integers():
    """The specific defect: 12/8 is four dotted quarters at 1.0, 2.5, 4.0, 5.5."""
    assert is_strong_beat(1.0, (12, 8))
    assert is_strong_beat(4.0, (12, 8))  # the third beat — was missed entirely
    assert not is_strong_beat(2.0, (12, 8))  # an integer, and not a beat
    assert not is_strong_beat(3.0, (12, 8))


def test_nine_eight_stresses_only_its_downbeat():
    """It named 1.0, 2.0 and 3.0; two of those are not beats at all."""
    assert is_strong_beat(1.0, (9, 8))
    assert not is_strong_beat(2.0, (9, 8))
    assert not is_strong_beat(3.0, (9, 8))


def test_compound_duple_stresses_both_beats_and_simple_duple_does_not():
    assert is_strong_beat(2.5, (6, 8)), "6/8 is felt in two"
    assert not is_strong_beat(2.0, (2, 4)), "2/4's second beat is the weak half"


def test_simple_metres_are_unchanged():
    assert [b for b in (1.0, 2.0, 3.0, 4.0) if is_strong_beat(b, (4, 4))] == [1.0, 3.0]
    assert [b for b in (1.0, 2.0, 3.0) if is_strong_beat(b, (3, 4))] == [1.0]


def test_a_malformed_metre_falls_back_to_the_downbeat():
    for meter in (None, (0, 0), (4, 0), "nonsense", ()):
        assert is_strong_beat(1.0, meter) is True
        assert is_strong_beat(2.0, meter) is False
