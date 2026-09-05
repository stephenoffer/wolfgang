"""The piece and the corpus were measured with different metric sets.

`corpus_metrics`' docstring calls `bar_metrics` "the shared yardstick run on
BOTH corpus bars and a generated piece, so piece-vs-corpus z-scores are
apples-to-apples". `build_corpus_profiles` builds the corpus side from **three**
functions:

    {**bar_metrics(bars), **style_fingerprint(bars), **sonority_metrics(bars)}

`_corpus_divergence_from_path` built the piece side from **two**, omitting
`sonority_metrics` — which was defined and called by nothing. The comparison
loop then does `gen.get(name, 0.0)`, so both missing metrics scored 0.0 against
a real distribution:

    chorded_attack_pct   value 0.0   z -15.78   (corpus mean 95.37)
    mean_sonority        value 0.0   z  -5.10   (corpus mean  3.61)

on a piece whose attacks really are 100% chorded with a mean sonority of 3.06.
Those were the two largest deviations in the report — in every report — and the
critic reads this. [[project_correct_analysis_wired_to_nothing]].
"""

from __future__ import annotations

import glob
import json
import os

import pytest


def _profiled_metrics() -> set[str]:
    """Every metric name the corpus profiles actually carry."""
    names: set[str] = set()
    for path in glob.glob("tools/compiled_packs/*/corpus_profile.json"):
        pack = os.path.basename(os.path.dirname(path))
        # `style__` packs are aggregates OF the composers, and `blend__` packs
        # are generated per-piece artifacts that can outlive a metric rename —
        # one still carries `direction_changes_per_bar`, the old name of
        # `melody_direction_change_pct`. Neither is a source of truth about
        # which metrics the system measures; the guard above covers them.
        if pack.startswith(("style__", "blend__")):
            continue
        try:
            names |= set((json.load(open(path)).get("metrics") or {}))
        except Exception:
            continue
    return names


def _piece_metrics(bars) -> set[str]:
    from scales.corpus_metrics import bar_metrics, sonority_metrics
    from scales.style_dimensions import style_fingerprint

    return set(bar_metrics(bars)) | set(style_fingerprint(bars)) | set(sonority_metrics(bars))


def _some_bars():
    for path in sorted(glob.glob("workspace/*/output/*.musicxml"))[-6:]:
        from scales.scales import _extract_generated_bars

        try:
            bars = _extract_generated_bars(path, None, "full")
        except Exception:
            continue
        if len(bars) >= 8:
            return bars
    return None


def test_a_metric_the_piece_cannot_be_measured_on_is_skipped_not_zeroed():
    """The general guard. `gen.get(name, 0.0)` turned "we did not measure this"
    into "the piece scores zero", which is how a fully chorded nocturne reported
    z=-15.78 for having no chords. One stale blend profile still carries
    `direction_changes_per_bar`, the old name of `melody_direction_change_pct`,
    and it must surface as a gap rather than as evidence."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("tools/scales/scales.py").read_text())
    node = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_corpus_divergence_from_path"
    )
    src = ast.unparse(node)
    assert "gen.get(name, 0.0)" not in src, "a missing metric is being scored as zero"
    assert "uncomputed" in src, "a metric that cannot be computed must be reported"


def test_every_profiled_metric_is_computed_for_the_piece_too():
    profiled = _profiled_metrics()
    if len(profiled) < 20:
        pytest.skip("corpus profiles not built")
    bars = _some_bars()
    if not bars:
        pytest.skip("no assembled piece to measure")
    missing = sorted(profiled - _piece_metrics(bars))
    assert not missing, (
        f"compared against the corpus but never computed for the piece: {missing} — "
        f"each one scores 0.0 and produces a fabricated deviation"
    )


def test_the_divergence_report_merges_all_three_sources():
    """A metric added to the corpus builder and not here reappears as a phantom
    z-score. Parsed, not grepped, so a rename cannot slip past."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("tools/scales/scales.py").read_text())
    node = next(
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_corpus_divergence_from_path"
    )
    called = {
        c.func.id
        for c in ast.walk(node)
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
    }
    for source in ("bar_metrics", "style_fingerprint", "sonority_metrics"):
        assert source in called, f"the piece side never calls {source}"


def test_sonority_is_not_zero_on_a_piece_that_has_chords():
    """The specific failure: a fully chorded piece reporting no chords."""
    from scales.corpus_metrics import sonority_metrics

    bars = _some_bars()
    if not bars:
        pytest.skip("no assembled piece to measure")
    got = sonority_metrics(bars)
    assert got["attacks"] > 0
    assert got["mean_sonority"] > 1.0
