"""Two realism detectors that were wrong in opposite directions.

Both were found by generating a Chopin nocturne, reading the score, and
measuring it against real Chopin rather than against intuition.

**`rhythm_vocabulary_poverty` cried wolf.** One global bound (`share >= 0.96 or
distinct <= 2`) for a quantity whose real range is entirely idiom-dependent:

    mozart sonatas (kern)       0/14    0%
    beethoven sonatas (kern)    0/14    0%
    chopin mazurkas (kern)      4/14   29%     <-- real notation, not MIDI
    chopin preludes (MIDI)      7/14   50%

20% overall, against a docstring claiming the bound was "set above the measured
maximum". It even said "a Chopin mazurka accompaniment really is 95% one value"
and then set the bound at 96%. A mazurka left hand is a repeated oom-pah-pah:
that is the dance, not a poverty of rhythm. Now read from the composer's own
distribution, as `accompaniment_vocabulary_poverty` next door already did.

**`accompaniment_monoculture` was blind.** It compared contour in EXACT
semitones, so one arpeggio over a major chord `(7, 5, 4, 3, ...)` and over a
minor one `(7, 5, 3, 4, ...)` counted as two unrelated idioms — a distinction
the ear does not make about figuration following the harmony. It fragmented a
single idiom across many signatures and undercounted it: the nocturne's left
hand is one shape from bar 1 to the end (bar 4 identical to bar 2, bar 5 to bar
1) and measured 0.56 against a 0.70 bound.

The order matters. The detector that fired was wrong and the one that stayed
silent was right to be worried about — which is why a false-positive rate is
not a nice-to-have: a warning that is wrong a third of the time teaches the
critic to discount the ones that are right.
"""

import pytest

from scales.score_realism import (
    _MONOCULTURE_MAX_SHARE,
    _contour_shape_sig,
    _contour_sig,
    _interval_class,
    _rhythm_vocabulary_bounds,
)

pytestmark = pytest.mark.calibration


# ─── The shape signature ─────────────────────────────────────────────────────


def _rec(tops):
    return {"tops": list(tops)}


def test_the_same_arpeggio_over_a_major_and_a_minor_chord_is_one_idiom():
    """Root-fifth-octave-tenth, major then minor. The ear hears one figure."""
    major = _rec([0, 7, 12, 16, 19])  # intervals 7, 5, 4, 3
    minor = _rec([0, 7, 12, 15, 19])  # intervals 7, 5, 3, 4
    assert _contour_sig(major) != _contour_sig(minor), "premise: exact semitones differ"
    assert _contour_shape_sig(major) == _contour_shape_sig(minor)


def test_genuinely_different_shapes_stay_apart():
    """Coarsening must not merge every figure into one."""
    arpeggio = _rec([0, 7, 12, 16, 19])
    scale = _rec([0, 2, 4, 5, 7])
    leaping = _rec([0, 12, 4, 16, 0])
    sigs = {_contour_shape_sig(r) for r in (arpeggio, scale, leaping)}
    assert len(sigs) == 3


def test_direction_is_preserved():
    assert _contour_shape_sig(_rec([0, 7])) != _contour_shape_sig(_rec([7, 0]))


@pytest.mark.parametrize(
    "semitones,cls",
    [(0, 0), (1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (7, 3), (8, 4), (12, 4), (-3, -2), (-12, -4)],
)
def test_the_interval_classes_are_the_musical_ones(semitones, cls):
    """Step, small leap, leap, octave-or-more — and a major and minor third in
    the same class, which is the whole point."""
    assert _interval_class(semitones) == cls


def test_the_monoculture_bound_sits_above_the_highest_real_movement():
    """`mazurka33-2` reaches 0.640 over 136 accompaniment bars.

    A first bound of 0.62 was set from an 82-movement sample that did not
    include it, and it fired on that mazurka. The bound must clear the highest
    value REAL music actually reaches, not the highest a sample happened to
    contain — and the generated nocturne this detector was meant to catch sits
    at 0.66, inside the real range, so no honest bound separates them.
    """
    assert _MONOCULTURE_MAX_SHARE > 0.640, "the bound must clear mazurka33-2, which is real Chopin"


# ─── Composer-relative rhythm bounds ─────────────────────────────────────────


def test_each_composer_gets_his_own_rhythm_bounds():
    """A mazurka and a Beethoven sonata cannot share a threshold."""
    chopin = _rhythm_vocabulary_bounds("chopin")
    beethoven = _rhythm_vocabulary_bounds("beethoven")
    if not chopin or not beethoven:
        pytest.skip("corpus not present")
    assert chopin[0] > beethoven[0], (
        "Chopin tolerates a far higher dominant-value share than Beethoven — "
        f"got chopin={chopin[0]:.2f} beethoven={beethoven[0]:.2f}"
    )
    assert beethoven[1] > chopin[1], "Beethoven's textures use more distinct values"


def test_an_unknown_composer_gets_bounds_that_err_toward_silence():
    """No measurement means no confident complaint."""
    from scales.score_realism import _RHYTHM_DISTINCT_FLOOR, _RHYTHM_SHARE_CEILING

    assert _rhythm_vocabulary_bounds("nobody_has_this_name") is None
    assert _RHYTHM_SHARE_CEILING >= 0.99
    assert _RHYTHM_DISTINCT_FLOOR <= 2
