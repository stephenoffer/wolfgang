"""A cached statistic must know which corpus it describes.

Three statistics are cached to disk under `compiled_packs/<composer>/`:
`density_stats`, `ornament_stats` and `rhythmic_fingerprint`. The first two
re-count the corpus on read and discard a cache describing a different one.
The third checked only that the FORMAT was current — so arming a new member of a
style left its fingerprint frozen:

    style__baroque   cached 6,868 bars   actual 10,914

and the numbers were materially wrong, not merely old:

    rest_bar_pct           0.2453 -> 0.3316   (35% relative)
    dotted_bar_pct         0.2050 -> 0.2345
    lh_texture_change_pct  0.6326 -> 0.5648

The brief prints these as "FACTS ABOUT HIM", and tells the composer that music
which never stops sounding is the clearest tell of a machine — while quoting a
rest rate a third too low.

This is the second time this exact defect has been fixed here: `density_stats`
was cached with no invalidation and served textures the corpus no longer
produced. Fixing one instance of a pattern is not fixing the pattern.
"""

import json

import pytest

import scales.composition_brief as CB
from scales.composition_brief import (
    _iter_corpus_bars,
    ornament_stats,
    rhythmic_fingerprint,
    texture_density_stats,
)

CACHED = (
    ("rhythmic_fingerprint", rhythmic_fingerprint, "bars"),
    ("ornament_stats", ornament_stats, "total_bars"),
    ("density_stats", texture_density_stats, "total_bars"),
)


def setup_function():
    for name in ("_FINGERPRINT_CACHE", "_ORNAMENT_CACHE", "_DENSITY_CACHE"):
        getattr(CB, name).clear()


@pytest.mark.parametrize("name,fn,bars_key", CACHED, ids=[c[0] for c in CACHED])
def test_the_cache_records_which_corpus_it_describes(name, fn, bars_key):
    stats = fn("mozart")
    assert stats.get(bars_key), f"{name} has no bar count to validate against"


@pytest.mark.parametrize("name,fn,bars_key", CACHED, ids=[c[0] for c in CACHED])
def test_a_cache_for_a_different_corpus_is_rejected(name, fn, bars_key, tmp_path, monkeypatch):
    """Plant a cache claiming the wrong bar count; it must be recomputed."""
    real = fn("mozart")
    path = CB._COMPILED_PACKS / CB._pack_dir("mozart") / f"{name}.json"
    original = path.read_text() if path.exists() else None
    try:
        poisoned = dict(real)
        poisoned[bars_key] = 1  # a corpus of one bar: certainly not the one on disk
        path.write_text(json.dumps(poisoned))
        getattr(
            CB,
            {
                "rhythmic_fingerprint": "_FINGERPRINT_CACHE",
                "ornament_stats": "_ORNAMENT_CACHE",
                "density_stats": "_DENSITY_CACHE",
            }[name],
        ).clear()
        got = fn("mozart")
        assert got.get(bars_key) != 1, f"{name} served a cache describing a different corpus"
    finally:
        if original is not None:
            path.write_text(original)


def test_the_recomputed_bar_count_matches_the_corpus_on_disk():
    actual = sum(1 for _ in _iter_corpus_bars("mozart"))
    assert rhythmic_fingerprint("mozart")["bars"] == actual
