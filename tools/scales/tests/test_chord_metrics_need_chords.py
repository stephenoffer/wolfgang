""""Your chords are too big" — from two chords.

Five of the profiled metrics are computed over the piece's CHORD events alone:
`avg_chord_size`, `maj_chord_ratio`, `min_chord_ratio`, `dim_aug_chord_ratio`,
`seventh_chord_ratio`. Each is a ratio or a mean whose denominator is the chord
count, so a mostly single-line texture — a Baroque keyboard piece, a two-part
invention, a fugue — makes them meaningless rather than extreme.

`_Z_DEGENERATE = 8.0` catches only the extremes. A baroque-style piece with
**two** chord events in 388 notes reported

    avg_chord_size  value 3.0  z +3.48  status "high"

and it reached the flags the critic reads. A mostly single-line texture is a
texture, not a fault.
"""

from __future__ import annotations

from scales.scales import _CHORD_SAMPLE_METRICS, _MIN_CHORD_SAMPLE, _Z_DEGENERATE


def test_the_guarded_set_is_exactly_the_chord_denominated_metrics():
    """Every one of these divides by the chord count in
    `style_dimensions._harmony_features`; nothing else does."""
    assert _CHORD_SAMPLE_METRICS == {
        "avg_chord_size",
        "maj_chord_ratio",
        "min_chord_ratio",
        "dim_aug_chord_ratio",
        "seventh_chord_ratio",
    }


def test_chord_pct_is_not_guarded():
    """`chord_pct` is chords per BAR — its denominator is the bar count, which a
    single-line piece has plenty of. Guarding it would hide a real finding."""
    assert "chord_pct" not in _CHORD_SAMPLE_METRICS
    assert "mean_sonority" not in _CHORD_SAMPLE_METRICS


def test_the_threshold_is_small_enough_to_leave_real_pieces_alone():
    assert 4 <= _MIN_CHORD_SAMPLE <= 12
    assert _MIN_CHORD_SAMPLE < _Z_DEGENERATE * 2


def test_a_single_line_piece_does_not_get_a_chord_criticism(tmp_path):
    """End to end on the two pieces that bracket the case."""
    import glob
    import json
    import os

    import pytest

    from scales.scales import compare_to_corpus

    thin = "verify-style-baroque-20260827"
    if not os.path.isdir(f"workspace/{thin}"):
        pytest.skip("the baroque probe piece is not in this workspace")
    report = compare_to_corpus(thin, composer="baroque")
    entry = (report.get("metrics") or {}).get("avg_chord_size") or {}
    assert entry.get("status") == "unreliable"
    assert entry.get("chord_events", 99) < _MIN_CHORD_SAMPLE
    assert "avg_chord_size" not in [f.get("metric") for f in (report.get("flags") or [])]
    assert "chord event" in entry.get("note", "")
    del glob, json


def test_a_chord_rich_piece_is_still_scored():
    """The guard must not silence the metric where it IS evidence."""
    import os

    import pytest

    from scales.scales import compare_to_corpus

    rich = "verify-nocturne-ebm-20260827"
    if not os.path.isdir(f"workspace/{rich}"):
        pytest.skip("the nocturne probe piece is not in this workspace")
    entry = (compare_to_corpus(rich, composer="chopin").get("metrics") or {}).get(
        "avg_chord_size"
    ) or {}
    assert entry.get("status") != "unreliable"
