"""`texture_stasis` fired on the majority of real music.

The bounds shipped as attacks-per-bar spread <= 0.25 and chord-thickness spread
<= 0.35. Measured across 1,853 movements from ten composers, the real medians
are **0.171 and 0.0** — both bounds sat above the median of the thing they were
supposed to catch, and the detector fired on **72%** of real movements: Bach
76%, Mozart 70%, Chopin 59%, Beethoven 47%. Every warning it produced was noise.

The thickness criterion is gone: with a median of 0.0 it carried no information.
The attacks bound is the measured 2nd percentile.
"""

import glob
import json
import statistics

import pytest

from scales.score_realism import (
    _TEXTURE_SPREAD_FLOOR,
    detect_texture_stasis_across_sections,
)


def _bar(bar, staff, onsets, sizes):
    return {
        "bar": bar,
        "staff": staff,
        "onsets": onsets,
        "chord_sizes": sizes,
        "durations": [1.0] * len(onsets),
        "bar_beats": 4.0,
    }


def test_a_genuinely_unvarying_piece_is_still_caught():
    bars = [_bar(i, 0, [0, 1, 2, 3], [1, 1, 1, 1]) for i in range(1, 25)]
    spans = [("a", 1, 8), ("b", 9, 16), ("c", 17, 24)]
    assert detect_texture_stasis_across_sections(bars, spans)


def test_ordinary_section_contrast_is_not_flagged():
    """A 20% swing in attacks per bar is unremarkable — the real median is 17%."""
    bars = [_bar(i, 0, [0, 1, 2, 3], [1] * 4) for i in range(1, 9)] + [
        _bar(i, 0, [0, 1, 2, 3, 4], [1] * 5) for i in range(9, 17)
    ]
    spans = [("a", 1, 8), ("b", 9, 16)]
    assert detect_texture_stasis_across_sections(bars, spans) == []


def test_the_floor_is_at_the_measured_second_percentile():
    assert _TEXTURE_SPREAD_FLOOR <= 0.05, (
        "a floor above the measured p05 (0.0435) fires on more than 5% of real music"
    )


@pytest.mark.calibration
def test_the_detector_does_not_reject_real_movements():
    """The standing discipline, applied to the detector that most violated it."""
    a_spreads = []
    for comp in ("bach", "mozart", "beethoven", "chopin", "palestrina"):
        per = {}
        for f in sorted(glob.glob(f"tools/reference_index/{comp}/bars_*.json")):
            for b in json.load(open(f)):
                per.setdefault(b.get("source"), []).append(b)
        for _src, bars in per.items():
            if len(bars) < 15:
                continue
            bars = sorted(bars, key=lambda b: b.get("bar_num") or 0)
            n = len(bars) // 3
            secs = [bars[:n], bars[n : 2 * n], bars[2 * n :]]
            if not all(secs):
                continue
            att = [
                sum(b.get("melody_density", 0) + b.get("accomp_density", 0) for b in s) / len(s)
                for s in secs
            ]
            a_spreads.append((max(att) - min(att)) / max(1e-6, statistics.fmean(att)))
    if len(a_spreads) < 200:
        pytest.skip("corpora not present")
    rate = sum(1 for a in a_spreads if a <= _TEXTURE_SPREAD_FLOOR) / len(a_spreads)
    assert rate <= 0.05, (
        f"texture_stasis would fire on {rate:.1%} of {len(a_spreads)} real movements"
    )
