"""Every other detector in `score_realism` catches too MUCH sameness.

None of them catches too little, and a piece where nothing recurs passes all of
them — which is the other half of sounding machine-made, and the more common
half of it here. Measured on an 85-bar generated piece: the most common phrase
opening appeared in 1 of 19 phrases, against a real median of a third. That is
not variety; it is a piece with no theme, where the listener is handed nothing
to recognise, and the audit called it clean.

Both falsification questions are asked below, because this detector FINDS rather
than FLAGS and the two need different evidence:

  * would it reject real music?  —  3.0% of 304 real movements with six or more
    marked phrase openings have no opening figure appearing twice (0.5% of 386
    for cadential rhythms). Recorded in the calibration harness.
  * would it find what is definitely there?  —  the tests below, on material
    where the answer is known by construction.
"""

from __future__ import annotations

from scales.score_realism import _RECURRENCE_MIN_PHRASES, detect_no_recurring_material


def _bar(bar, onsets, tops, staff=0):
    return {
        "bar": bar,
        "staff": staff,
        "onsets": list(onsets),
        "durations": [1.0] * len(onsets),
        "tops": list(tops),
        "midis": list(tops),
        "chord_sizes": [1] * len(onsets),
    }


#: Distinct INTERVAL patterns. `_contour_sig` is transposition-invariant by
#: design, so [60,62,64] and [62,64,66] are the same figure a step higher — a
#: first version of these fixtures transposed one shape and asserted the
#: detector should call them all different, which would have been wrong.
_DISTINCT = [
    [60, 62, 64],
    [60, 65, 67],
    [60, 59, 55],
    [60, 72, 64],
    [60, 61, 66],
    [60, 67, 60],
    [60, 63, 58],
    [60, 68, 71],
    [60, 55, 62],
    [60, 64, 57],
]


def _piece(openings, first=1, spacing=4):
    """One bar per phrase opening; `openings` gives each one's contour."""
    bars, starts = [], []
    for i, tops in enumerate(openings):
        bar = first + i * spacing
        bars.append(_bar(bar, [0.0, 1.0, 2.0], tops))
        starts.append(bar)
    return bars, starts


_N = _RECURRENCE_MIN_PHRASES


def test_it_fires_when_every_phrase_opens_differently():
    bars, starts = _piece(_DISTINCT[: _N + 2])
    found = detect_no_recurring_material(bars, starts, [])
    assert found, "every opening different and nothing reported"
    assert found[0]["detector"] == "no_recurring_material"
    assert found[0]["evidence"]["kind"] == "opening"


def test_it_is_silent_when_the_theme_comes_back_even_once():
    """The bar is deliberately low: ONE return is enough to have a theme."""
    theme = [60, 62, 64]
    openings = [theme, *_DISTINCT[1 : _N + 1], theme]
    bars, starts = _piece(openings)
    assert not detect_no_recurring_material(bars, starts, []), "one genuine return is a theme"


def test_it_is_silent_on_a_piece_with_a_strong_recurring_head_motif():
    theme = [60, 62, 64]
    openings = [theme if i % 2 == 0 else [67, 65, 64] for i in range(_N + 2)]
    bars, starts = _piece(openings)
    assert not detect_no_recurring_material(bars, starts, [])


def test_it_says_nothing_when_there_are_too_few_phrases_to_tell():
    """At four phrases "nothing repeated" is as much a claim about the sample as
    about the music — the real-corpus rate doubles below six."""
    bars, starts = _piece(_DISTINCT[: _N - 1])
    assert not detect_no_recurring_material(bars, starts, [])


def test_it_reads_the_melody_staff_it_is_given():
    """Not staff 0, which is the melody only on a piano grand staff."""
    bars, starts = _piece(_DISTINCT[: _N + 2])
    for b in bars:
        b["staff"] = 3
    assert not detect_no_recurring_material(bars, starts, [], melody_staff=0)
    assert detect_no_recurring_material(bars, starts, [], melody_staff=3)


def test_cadences_are_judged_on_rhythm_alone():
    """A cadence that keeps its rhythm and changes its pitches has come back."""
    bars, ends = _piece(_DISTINCT[: _N + 2])
    found = detect_no_recurring_material(bars, [], ends)
    assert not found, (
        "these share one rhythm and differ only in pitch — as cadences, that is "
        f"the same formula returning: {found}"
    )


def test_the_finding_is_advisory_not_a_warning():
    """A composer may genuinely write through-composed music with no returning
    figure. The fresh-ears critic is better placed than a counter to judge it."""
    bars, starts = _piece(_DISTINCT[: _N + 2])
    assert detect_no_recurring_material(bars, starts, [])[0]["severity"] == "info"
