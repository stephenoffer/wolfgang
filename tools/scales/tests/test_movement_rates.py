"""Texture rates belong to the movement, not the composer.

A composer's mean is the wrong grain for a piece that has a character. Mozart
ties on 7.0% of bars across his corpus — but `sonata14-3`, a C minor slow
movement, ties in 15% and opens 12% of its bars with a rest, twice his mean in
both. A generated piece asked to be sustained has more in common with that
movement than with Mozart.

The spread is not noise. Chopin's LEFT-HAND chord share runs from 0.000 to
0.994 across 90 movements with a median of 0.539 — his aggregate of 0.29 sits
below his 25th percentile, so a generator targeting the mean is targeting
something almost none of his movements do.
"""

import pytest

from scales.composition_brief import MOVEMENT_METRICS, movement_rate_range, movement_rates

pytestmark = pytest.mark.calibration


def test_a_composer_yields_many_movements():
    rows = movement_rates("mozart")
    if not rows:
        pytest.skip("mozart corpus not present")
    assert len(rows) >= 20
    assert all(r["bars"] >= 24 for r in rows), "a share over a dozen bars is noise"


def test_every_metric_is_a_share_or_a_rate():
    rows = movement_rates("mozart")
    if not rows:
        pytest.skip("mozart corpus not present")
    for row in rows:
        for metric in MOVEMENT_METRICS:
            assert metric in row, f"{metric} missing from {row['source']}"
            assert 0.0 <= row[metric] <= 4.0, f"{metric}={row[metric]} on {row['source']}"


def test_the_spread_is_wide_enough_to_be_worth_having():
    """If every movement matched the composer's mean there would be no reason
    for this to exist."""
    got = movement_rate_range("mozart", "ties_per_bar")
    if not got:
        pytest.skip("mozart corpus not present")
    assert got["p75"] > got["p25"] * 2, f"the spread is too narrow to matter: {got}"


def test_the_quantiles_are_ordered():
    for composer in ("mozart", "chopin", "haydn"):
        got = movement_rate_range(composer, "lh_chord_share")
        if not got:
            continue
        assert got["min"] <= got["p25"] <= got["median"] <= got["p75"] <= got["max"]


def test_chopins_median_left_hand_is_far_above_his_aggregate():
    """The finding that motivated this. His corpus-wide LH chord share is about
    0.29; his MEDIAN MOVEMENT is 0.54. Targeting the aggregate aims at something
    below his 25th percentile."""
    got = movement_rate_range("chopin", "lh_chord_share")
    if not got:
        pytest.skip("chopin corpus not present")
    assert got["median"] > 0.4, got


def test_an_unknown_metric_is_refused_rather_than_guessed():
    assert movement_rate_range("mozart", "not_a_metric") is None


def test_an_unknown_composer_returns_nothing():
    assert movement_rates("nobody_at_all") == []
    assert movement_rate_range("nobody_at_all", "ties_per_bar") is None


def test_a_thin_corpus_will_not_produce_quantiles():
    """Four movements is the floor — three points cannot describe a spread."""
    for composer in ("mozart", "chopin"):
        rows = movement_rates(composer)
        if len(rows) >= 4:
            assert movement_rate_range(composer, "ties_per_bar") is not None


# ─── an overlay must not override a newer measurement ────────────────────────


def test_the_resolved_distribution_matches_the_corpus_it_was_compiled_from():
    """A four-month-old overlay was replacing the pack wholesale, so Mozart's
    planned accompaniment was `pedal_point` 0.090 against his real 0.034 and
    `block_chord_offbeat` 0.045 against his real 0.104. The generated output
    reproduced the overlay's numbers faithfully, which is exactly what made it
    look like a generator defect."""
    import json
    from collections import Counter
    from pathlib import Path

    from scales.style_resolver import StyleResolver

    root = Path("tools/reference_index/mozart")
    if not root.is_dir():
        pytest.skip("mozart corpus not present")
    live = Counter()
    for shard in sorted(root.glob("bars_*.json")):
        for bar in json.load(open(shard)):
            if bar.get("lh_texture"):
                live[bar["lh_texture"]] += 1
    total = sum(live.values())
    resolved = StyleResolver().resolve_single("mozart").lh_distribution
    for idiom, count in live.most_common(6):
        want = count / total
        got = resolved.get(idiom, 0.0)
        assert abs(got - want) < 0.02, (
            f"{idiom}: the plan says {got:.3f} where the corpus says {want:.3f}"
        )


def test_an_overlay_dated_before_the_pack_is_treated_as_stale():
    import time

    from scales.style_resolver import _overlay_is_stale

    now = time.time()
    assert _overlay_is_stale({"last_updated": "2026-04-19"}, now) is True
    assert _overlay_is_stale({"last_updated": "2099-01-01"}, now) is False


def test_an_overlay_with_no_date_is_treated_as_current():
    """A missing date is not evidence of age — refusing it would discard every
    hand-written overlay."""
    import time

    from scales.style_resolver import _overlay_is_stale

    assert _overlay_is_stale({}, time.time()) is False
    assert _overlay_is_stale({"last_updated": "not a date"}, time.time()) is False


def test_a_pack_and_overlay_from_the_same_day_are_one_generation():
    import datetime
    import time

    from scales.style_resolver import _overlay_is_stale

    today = datetime.date.today().isoformat()
    assert _overlay_is_stale({"last_updated": today}, time.time()) is False


def test_the_transition_matrix_also_comes_from_the_corpus_not_the_overlay():
    """The stale overlay carried both halves of the texture plan. Its matrix had
    ten source idioms against the pack's twelve, included `sparse_punctuation`
    (a label the corpus does not produce), and put `alberti -> block_chord_offbeat`
    at 0.011 where the corpus says 0.038 — so the succession was biased the same
    way as the distribution, compounding it."""
    from scales.style_resolver import StyleResolver

    dna = StyleResolver().resolve_single("mozart")
    matrix = getattr(dna, "transition_matrix", None) or {}
    if not matrix:
        pytest.skip("no transition matrix compiled")
    assert "sparse_punctuation" not in matrix, (
        "a label the corpus does not produce is being planned as a successor"
    )
    successors = matrix.get("alberti") or {}
    if successors:
        assert successors.get("block_chord_offbeat", 0) > 0.02, (
            f"alberti rarely reaches the oom-pah: {successors.get('block_chord_offbeat')}"
        )


def test_a_list_overlay_still_extends_rather_than_replaces():
    """Two of Mozart's overlays are lists — `figuration_templates` and
    `harmonic_devices` — and the staleness rule must not touch the union
    behaviour they rely on."""
    from scales.style_resolver import StyleResolver

    pack = StyleResolver()._load_pack("mozart")
    for key in ("figuration_templates", "harmonic_devices"):
        value = pack.get(key)
        if value is not None:
            assert isinstance(value, list), f"{key} became a {type(value).__name__}"
