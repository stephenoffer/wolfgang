"""The brief's fallback targets described no real composer.

`_DISCRIMINATOR_FALLBACK` is what the brief prints as a target when a composer
has no `corpus_profile` — so it is shown exactly when the system knows least,
where a wrong number does the most damage. The bands were hand-written.
Measured against the 28 composer profiles that DO exist:

    texture_change_pct           was "0.4-0.6"   only 5 of 36 inside; median 0.269
    melody_direction_change_pct  was "0.3-0.6"   ceiling excludes the top quarter
    density_cv                   was ">=0.30"    12 of 36 real composers below it

An unprofiled composer was told to change texture about twice as often as a
typical real one. Same discipline as every other threshold here: measure the real
distribution before writing the number down
([[feedback_falsify_detectors_against_real_scores]]).
"""

from __future__ import annotations

import glob
import json
import os
import re
import statistics

import pytest

from scales.composition_brief import _DISCRIMINATOR_FALLBACK


def _real_means(metric: str) -> list[float]:
    out = []
    for path in sorted(glob.glob("tools/compiled_packs/*/corpus_profile.json")):
        # style__ packs are aggregates OF the composers, not extra data points.
        if os.path.basename(os.path.dirname(path)).startswith("style__"):
            continue
        try:
            stats = (json.load(open(path)).get("metrics") or {}).get(metric) or {}
        except Exception:
            continue
        if isinstance(stats.get("mean"), (int, float)):
            out.append(float(stats["mean"]))
    return out


def _band(text: str) -> tuple[float, float]:
    lo, hi = re.search(r"(\d\.\d+)-(\d\.\d+)", text).groups()
    return float(lo), float(hi)


@pytest.mark.parametrize("metric", sorted(_DISCRIMINATOR_FALLBACK))
def test_the_band_contains_the_real_median(metric):
    """The failing condition: a target no typical composer meets. The old
    texture band's FLOOR sat above the median of every measured composer."""
    means = _real_means(metric)
    if len(means) < 10:
        pytest.skip(f"only {len(means)} profiles built")
    low, high = _band(_DISCRIMINATOR_FALLBACK[metric])
    assert low <= statistics.median(means) <= high


@pytest.mark.parametrize("metric", sorted(_DISCRIMINATOR_FALLBACK))
def test_a_reasonable_share_of_real_composers_sit_inside_it(metric):
    means = _real_means(metric)
    if len(means) < 10:
        pytest.skip(f"only {len(means)} profiles built")
    low, high = _band(_DISCRIMINATOR_FALLBACK[metric])
    inside = sum(1 for m in means if low <= m <= high)
    assert inside / len(means) >= 0.35, (
        f"{metric}: only {inside}/{len(means)} real composers are inside "
        f"{low}-{high} — that is a target, not a description"
    )


@pytest.mark.parametrize("metric", sorted(_DISCRIMINATOR_FALLBACK))
def test_the_text_says_what_it_was_measured_from(metric):
    """A number with no provenance is indistinguishable from a guess, and these
    WERE guesses."""
    text = _DISCRIMINATOR_FALLBACK[metric]
    assert "median" in text and "composers" in text
