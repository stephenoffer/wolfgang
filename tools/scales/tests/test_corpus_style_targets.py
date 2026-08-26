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
from scales.style_comparator import compare

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


def test_real_movements_actually_pass_the_gate():
    """The test that matters, and the one the first version of this file lacked.

    Checking that the real MEDIAN falls inside a target's band is far too weak:
    with that as the only check, the targets still failed **19 of 20 canonical
    movements** on at least one metric. Two separate faults hid behind it — bands
    too narrow for genuinely wide distributions (`triplet_pct` runs 0-74), and a
    comparator that read `target_stdev` and then decided every verdict from a
    flat 35% relative divergence, so no width of band could help.

    Scoring whole real movements end to end is the only version of this test that
    would have caught either.
    """
    rows = _real_metrics()
    targets = build_style_targets_from_dna({}, tempo_bpm=100)
    failing = []
    for m in rows:
        rep = compare(m, targets, threshold=0.35)
        bad = [
            k
            for k, v in (rep.get("metrics") or {}).items()
            if isinstance(v, dict) and v.get("status") == "FAIL"
        ]
        if bad:
            failing.append(bad)
    rate = len(failing) / len(rows)
    assert rate <= 0.25, (
        f"{len(failing)} of {len(rows)} real movements FAIL at least one gate "
        f"metric ({rate:.0%}). Examples: {failing[:3]}"
    )


def test_the_gate_still_rejects_mechanical_music():
    """Loosening a gate until real music passes must not disable it."""
    targets = build_style_targets_from_dna({}, tempo_bpm=100)
    mechanical = {
        "events_per_bar": 8.0,
        "events_per_bar_rh": 4.0,
        "events_per_bar_lh": 4.0,
        "rest_ratio": 0.0,          # never breathes
        "triplet_pct": 0.0,
        "rhythmic_variety": 1.0,    # one duration throughout
        "chromatic_pct": 0.0,
        "leap_pct": 2.0,
        "dynamic_markings_per_bar": 0.0,
        "texture_change_pct": 0.0,  # one texture forever
        "direction_changes_per_bar": 0.2,
        "density_cv": 0.02,         # perfectly flat
        "stepwise_pct": 98.0,       # a scale exercise
    }
    rep = compare(mechanical, targets, threshold=0.35)
    assert rep["failing"] >= 2, f"a deliberately mechanical score passed: {rep}"


def test_the_comparator_uses_the_spread_not_a_flat_percentage():
    """`target_stdev` was stored and printed but never consulted."""
    targets = {"wide": {"mean": 20.0, "stdev": 25.0}}
    # 100% away from the mean, but well inside one standard deviation.
    rep = compare({"wide": 40.0}, targets, threshold=0.35)
    entry = rep["metrics"]["wide"]
    assert entry["status"] == "PASS", entry
    assert entry["sigmas"] == 0.8

    narrow = {"narrow": {"mean": 20.0, "stdev": 1.0}}
    rep2 = compare({"narrow": 26.0}, narrow, threshold=0.35)
    assert rep2["metrics"]["narrow"]["status"] == "FAIL"


def test_a_target_without_a_spread_falls_back_to_relative_divergence():
    rep = compare({"m": 20.0}, {"m": {"mean": 10.0}}, threshold=0.35)
    assert rep["metrics"]["m"]["status"] == "FAIL"
    assert rep["metrics"]["m"]["sigmas"] is None
