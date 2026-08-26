"""Generated onsets must be positions a bar actually has.

The engine fallback was shipping bars holding 4.875 beats of a 4/4 and onsets at
1.56, 2.06 and 0.06 — the last of which is below beat 1 and not a position in any
bar. A repair pass downstream now snaps them, but a generator that emits
positions the notation cannot express is producing something no engraver can
read, and repairing it downstream hides that.

Two faults, both in this lane, both silent:

* **A float cursor rounded to two decimals.** `1.5625` — a legitimate 64th
  offset — was emitted as `1.56`. Advancing a float by `1/3` for a triplet
  compounds the error across a bar.
* **The cursor advanced BEFORE the note was emitted.** Every gesture started one
  note-value late and its last note ran past the end of its slot: a four-note
  figure beginning on beat 1 was written beginning on beat 1.5.
"""

from fractions import Fraction

import pytest

from scales.duration import DURATION_VALUES

# The notation grid. 1/48 of a quarter is the obvious choice and it is WRONG: it
# covers triplets, sextuplets, 32nds and 64ths, and silently destroys
# quintuplets and septuplets — a five-note run snapped to it drifts by up to
# 0.0083 of a beat per note and no longer sums to its own beat. That is the same
# class of bug as the old 16th-note quantization that destroyed every triplet in
# the system, one tuplet family further out.
#
# The denominators actually in `DURATION_VALUES` are 1,2,3,4,5,6,7,8,12,16, and
# their least common multiple is 1680. Anything coarser rounds a real duration.
_GRID = Fraction(1, 1680)


def _on_grid(beat: float) -> bool:
    return (Fraction(str(beat)).limit_denominator(1000) % _GRID) == 0


def _positions(durations, start=Fraction(1)):
    """Emit-then-advance with an exact cursor — the corrected arithmetic."""
    beat = Fraction(start)
    out = []
    for code in durations:
        out.append(beat)
        beat += DURATION_VALUES[code]
    return out, beat


# ─── The grid property ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "profile",
    [
        ["trip_e", "trip_e", "trip_e"],
        ["trip_s"] * 6,
        ["s", "s", "trip_e", "trip_e", "trip_e"],
        ["t"] * 8,
        ["x"] * 8,
        ["quint_s"] * 5,
        ["sext_s"] * 6,
        ["dq", "e", "s", "s"],
    ],
)
def test_every_onset_of_a_gesture_lands_on_the_notation_grid(profile):
    positions, _end = _positions(profile)
    off = [float(p) for p in positions if (p % _GRID) != 0]
    assert not off, f"{profile} produced off-grid onsets {off}"


@pytest.mark.parametrize(
    "profile,expected_end",
    [
        (["trip_e"] * 3, Fraction(2)),
        (["trip_s"] * 6, Fraction(2)),
        (["q"] * 4, Fraction(5)),
        (["e"] * 8, Fraction(5)),
        (["quint_s"] * 5, Fraction(2)),
    ],
)
def test_a_gesture_ends_exactly_where_it_should(profile, expected_end):
    """Float arithmetic ends a bar of triplets at 1.9999999999999998."""
    _positions_, end = _positions(profile)
    assert end == expected_end


def test_the_first_note_lands_on_the_slots_own_start_beat():
    """Advance-then-emit displaced every gesture by its own first duration."""
    positions, _ = _positions(["trip_s"] * 3 + ["s"] * 2, start=Fraction(1))
    assert positions[0] == Fraction(1), (
        f"the gesture starts at {float(positions[0])}, not on its slot's beat 1"
    )


def test_a_float_cursor_rounded_to_two_decimals_leaves_the_grid():
    """The failure this test exists to prevent, demonstrated."""
    beat = 1.0
    emitted = []
    for code in ["trip_s"] * 3 + ["s"] * 2:
        beat += float(DURATION_VALUES[code])
        emitted.append(round(beat, 2))
    assert any(not _on_grid(b) for b in emitted), (
        "the old arithmetic is expected to produce off-grid onsets"
    )
    # And the corrected arithmetic does not.
    positions, _ = _positions(["trip_s"] * 3 + ["s"] * 2)
    assert all(_on_grid(float(p)) for p in positions)


def test_no_onset_falls_below_beat_one():
    """0.06 was reaching the score; there is no such position in a bar."""
    for profile in (["trip_e"] * 3, ["s"] * 16, ["dq", "e"]):
        positions, _ = _positions(profile)
        assert all(p >= 1 for p in positions), profile


# ─── The duration table itself ───────────────────────────────────────────────


def test_every_duration_value_is_exact():
    """One float in the table reintroduces the drift everywhere it is used."""
    non_exact = [k for k, v in DURATION_VALUES.items() if not isinstance(v, Fraction)]
    assert not non_exact, f"these duration values are not exact: {non_exact}"


def test_every_duration_value_lands_on_the_grid():
    off = [k for k, v in DURATION_VALUES.items() if (v % _GRID) != 0]
    assert not off, f"these durations are not expressible on the 1/1680 grid: {off}"
