"""A stored profile must agree with the function that computes it.

Three times today a stored `corpus_profile.json` value and a freshly computed
one were compared, disagreed, and the disagreement was diagnosed wrongly:

  * `chord_pct` 1.82 stored against 8.51 recomputed — two entirely different
    measures, one over score events and one over bar-record attacks;
  * `avg_chord_size` 0.171 against 2.087 — a PER-MOVEMENT mean against a
    whole-corpus aggregate, reported as 12x staleness by both sessions;
  * `chromatic_ratio` genuinely stale, after `_all_events` was widened to read
    the inner voice streams, and the stored file really was computed by an
    older function.

Only the third was staleness. The other two were the same number measured two
ways. This test removes the guesswork: it recomputes in the profile's OWN unit —
the per-movement mean the builder documents — and demands they match. A
disagreement here means the profile needs rebuilding, and nothing else.

Marked `calibration`: it re-derives the fingerprint for every movement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_COMPOSERS = ("bach", "mozart", "haydn", "chopin", "palestrina")
#: The builder skips movements shorter than this; the recomputation must too, or
#: it is measuring a different population and we are back where we started.
_MIN_MOVEMENT_BARS = 6


@pytest.mark.calibration
@pytest.mark.parametrize("composer", _COMPOSERS)
def test_the_stored_profile_matches_a_fresh_computation(composer):
    # The BUILDER'S OWN loaders. `group_by_source` sorts each movement by bar
    # number and `_iter_corpus_bars` does not — and every interval metric
    # depends on bar order, so grouping them myself made this test disagree with
    # the builder over `mean_abs_interval` and read it as staleness. To compare
    # against a generator, use the generator's inputs.
    from scripts.build_corpus_indexes import group_by_source, load_bars

    from scales.style_dimensions import style_fingerprint

    path = Path("tools/compiled_packs") / composer / "corpus_profile.json"
    if not path.exists():
        pytest.skip(f"no profile for {composer}")
    stored = json.loads(path.read_text()).get("metrics") or {}

    movements = [
        v for v in group_by_source(load_bars(composer)).values() if len(v) >= _MIN_MOVEMENT_BARS
    ]
    if not movements:
        pytest.skip(f"no movements long enough for {composer}")

    fingerprints = [style_fingerprint(m) for m in movements]
    drifted = []
    for feature, summary in stored.items():
        values = [fp[feature] for fp in fingerprints if fp.get(feature) is not None]
        if not values or "mean" not in (summary or {}):
            continue
        live = sum(values) / len(values)
        # A tolerance wide enough for float summation order, far below any real
        # change: the `chromatic_ratio` staleness this exists to catch was 0.009.
        if abs(live - summary["mean"]) > 1e-3:
            drifted.append(f"{feature}: stored {summary['mean']:.4f} vs live {live:.4f}")
    assert not drifted, (
        f"{composer}'s profile disagrees with the function that computes it — "
        f"rebuild with `python -m scripts.build_corpus_profiles`:\n  " + "\n  ".join(drifted)
    )
