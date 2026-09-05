"""A minor 2nd is not rare in real music, and the ear said so with no scale.

`detect_vertical_clashes` fires on **79% of real Mozart movements and 100% of
real Palestrina and Haydn**. The critic reads these before deciding what to
revise, so a warning that is present in essentially all real music teaches it to
discount the ones that matter. Measured as clashes per 100 bars there IS a
signal:

    real mozart sonatas   median  2.8   max 22.2
    real chopin mazurkas  median  3.5   max 11.6
    real haydn quartets   median  7.1   max 17.4
    real palestrina       median 11.6   max 22.2
    generated pieces      median 16.7   max 40.0

Presence carries almost none of that; the rate carries it, and only against the
right repertoire — suspension-driven polyphony clashes about four times as often
as a sonata by construction. The finding is left advisory (`convergence` keys off
this detector name, and a real cross-relation is idiomatic in Bach) and given the
number the critic needs to weigh it.
"""

from __future__ import annotations

import music21


def _score(pitch_pairs, bars: int):
    """A score of `bars` bars, clashing on the downbeat of the first few."""
    score = music21.stream.Score()
    upper, lower = music21.stream.Part(), music21.stream.Part()
    for bar in range(1, bars + 1):
        top, bottom = music21.stream.Measure(number=bar), music21.stream.Measure(number=bar)
        if bar <= pitch_pairs:
            top.append(music21.note.Note("C5", quarterLength=4))
            bottom.append(music21.note.Note("B4", quarterLength=4))
        else:
            top.append(music21.note.Note("C5", quarterLength=4))
            bottom.append(music21.note.Note("G4", quarterLength=4))
        upper.append(top)
        lower.append(bottom)
    score.insert(0, upper)
    score.insert(0, lower)
    return score


def _clashes(score):
    from scales.musical_ear import detect_vertical_clashes

    return [f for f in detect_vertical_clashes(score) if f.get("detector") == "vertical_clash"]


def test_the_count_is_not_truncated_by_the_listing_cap():
    """It used to `break` at the cap, so the rate could not have been computed at
    all: twenty clashes and eight clashes reported the same number."""
    found = _clashes(_score(pitch_pairs=20, bars=40))
    assert len(found) == 8, "still lists at most `cap`"
    assert found[0]["evidence"]["clashes_in_piece"] == 20


def test_the_rate_distinguishes_a_short_piece_from_a_long_one():
    """Eight listed clashes in 40 bars is a different piece from eight in 400."""
    dense = _clashes(_score(pitch_pairs=20, bars=40))[0]["evidence"]
    sparse = _clashes(_score(pitch_pairs=20, bars=400))[0]["evidence"]
    assert dense["clashes_per_100_bars"] == 50.0
    assert sparse["clashes_per_100_bars"] == 5.0


def test_every_clash_finding_carries_the_real_music_reference():
    for finding in _clashes(_score(pitch_pairs=3, bars=40)):
        assert finding["evidence"]["real_per_100_bars"]["mozart sonatas"]


def test_the_first_finding_says_it_in_words():
    """The critic reads prose, not evidence dicts."""
    problem = _clashes(_score(pitch_pairs=3, bars=40))[0]["problem"]
    assert "per 100" in problem and "judge the RATE" in problem


def test_a_clean_score_says_nothing():
    assert not _clashes(_score(pitch_pairs=0, bars=40))


def test_convergence_ranks_by_the_real_count_not_the_listed_one():
    """`composite_score` ranks a revision by its per-detector counts, and
    `detector_counts` counted the LIST — which every detector caps. Measured on
    the workspace: a piece with 560 overfull bars and one with 13 both reported
    12, so a revision repairing 547 of them scored as no improvement.
    """
    from scales.convergence import detector_counts

    findings = [
        {"detector": "bar_length", "severity": "error", "evidence": {"occurrences": 560}}
        for _ in range(12)
    ]
    assert detector_counts(findings)["bar_length"] == 560


def test_a_detector_that_does_not_report_occurrences_still_counts_normally():
    from scales.convergence import detector_counts

    findings = [{"detector": "monotony", "severity": "warn"} for _ in range(3)]
    assert detector_counts(findings)["monotony"] == 3


def test_the_listed_count_wins_when_it_is_larger():
    """A stale or under-reported `occurrences` must never shrink the count below
    what is actually in the list."""
    from scales.convergence import detector_counts

    findings = [
        {"detector": "bar_length", "severity": "error", "evidence": {"occurrences": 1}}
        for _ in range(5)
    ]
    assert detector_counts(findings)["bar_length"] == 5
