"""Falsification harness: the review gate's targets must describe real music.

This is the test that would have caught the worst guidance bug in the system.
The gate's fallback targets were written from prose rather than measured, and
asked for a ``texture_change_pct`` of **52** where 20 real movements measure a
median of **20.5** — so every composed section was told to change its
accompaniment idiom two and a half times more often than Mozart, Beethoven or
Chopin ever did. A target no real music meets does not raise quality; it
manufactures the exact restlessness it was meant to prevent.

Marked ``calibration`` because it needs the score corpus and music21.
Run with ``pytest -m calibration``.
"""

import glob
import statistics

import pytest

from scales.review_style_gate import build_style_targets_from_dna

pytestmark = pytest.mark.calibration

# How far outside the measured band a target may sit before it is a bug. A
# target is allowed to differ from the median — it is not allowed to sit outside
# what any real movement does.
_TOLERANCE_SIGMAS = 2.0

_CHECK = (
    "rest_ratio",
    "rhythmic_variety",
    "chromatic_pct",
    "leap_pct",
    "texture_change_pct",
    "direction_changes_per_bar",
    "density_cv",
    "stepwise_pct",
)


def _real_metrics():
    from scales.style_analyzer import analyze_score

    paths = (
        sorted(glob.glob("tools/reference_scores/mozart-piano-sonatas/kern/sonata0[1-9]-*.krn"))[:10]
        + sorted(glob.glob("tools/reference_scores/beethoven-piano-sonatas/**/*.krn", recursive=True))[:5]
        + sorted(glob.glob("tools/reference_scores/chopin-mazurkas/**/*.krn", recursive=True))[:5]
    )
    if not paths:
        pytest.skip("score corpus not present")
    rows = []
    for path in paths:
        try:
            m = analyze_score(path)
        except Exception:
            continue
        if m:
            rows.append(m)
    if len(rows) < 8:
        pytest.skip("not enough real movements parsed")
    return rows


def test_every_gate_target_describes_real_music():
    rows = _real_metrics()
    targets = build_style_targets_from_dna({}, tempo_bpm=100)
    offenders = []
    for metric in _CHECK:
        vals = [float(r[metric]) for r in rows if isinstance(r.get(metric), (int, float))]
        if len(vals) < 8:
            continue
        # Trim one extreme outlier before judging the range: a single unusual
        # movement should not license an arbitrarily wide target.
        vals = sorted(vals)
        med = statistics.median(vals)
        core = [v for v in vals if v <= max(med * 4, med + 1)]
        spec = targets.get(metric)
        if not spec:
            continue
        mean, sd = float(spec["mean"]), float(spec["stdev"])
        lo, hi = mean - _TOLERANCE_SIGMAS * sd, mean + _TOLERANCE_SIGMAS * sd
        # The real median must be reachable inside the target's own band.
        if not (lo <= med <= hi):
            offenders.append(
                f"{metric}: target {mean}±{sd} excludes the real median {med:.2f} "
                f"(real range {min(core):.2f}-{max(core):.2f})"
            )
    assert not offenders, (
        "these gate targets do not describe real music:\n" + "\n".join(offenders)
    )


def test_the_texture_change_target_has_not_drifted_back_up():
    """The specific regression: 52 against a measured median of 20.5."""
    targets = build_style_targets_from_dna({}, tempo_bpm=100)
    mean = float(targets["texture_change_pct"]["mean"])
    assert mean < 35, (
        f"texture_change_pct target is back at {mean}; real music measures a "
        f"median near 20 and no movement measured exceeded 62"
    )


def test_density_fallbacks_are_not_busier_than_real_music():
    """The old 8/6 fallback was 40% busier than any real movement measured."""
    targets = build_style_targets_from_dna({}, tempo_bpm=100)
    assert float(targets["events_per_bar"]["mean"]) < 12.0
