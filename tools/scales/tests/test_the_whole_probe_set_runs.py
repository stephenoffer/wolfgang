"""Every closed finding's probe, re-run together — and proved to run at all.

A dimension you close stops being measured and therefore has no guard. Two
sessions spent a day finding defects one at a time, each fix verified against
the dimensions that fix was about. A contour finding closed early in the day
silently regressed hours later — turns per bar 3.0 back to 2.0 — because nothing
re-ran its probe. The piece is one artefact; everything moves everything.

`scripts.style_alignment_report` re-runs the whole set. This test guards the
thing that would make it useless: a probe that raises is caught and printed as
`<probe failed>`, so a broken probe degrades to a quiet blank row rather than an
error. That is the failure mode this repo keeps finding — something reporting
nothing because it cannot report anything — so it is asserted directly.
"""

from __future__ import annotations

import shutil

import pytest

_PIECE = "test-alignment-20260827"


@pytest.fixture(scope="module")
def composed():
    from scales.scales import (
        _WORKSPACE,
        build_form_graph,
        compile_style,
        init_workspace,
        resolve_motifs,
        run_scales_section,
    )

    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)
    init_workspace(
        _PIECE,
        "compose_from_text",
        "alignment probe",
        {"target": {"instrumentation": "solo_piano"}},
    )
    compile_style(_PIECE, composers=["mozart"])
    resolve_motifs(
        _PIECE,
        [
            {
                "motif_id": "head",
                "interval_contour": [0, 2, 2, -1],
                "rhythm_cell": ["e", "e", "e", "q"],
            }
        ],
    )
    rows = build_form_graph(_PIECE, "binary", "C major", tempo_bpm=110, meter=(4, 4))
    for section in sorted({r["section"] for r in rows if "section" in r}):
        run_scales_section(_PIECE, section)
    yield _PIECE
    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)


def test_every_probe_actually_runs(composed):
    """A probe that raises is reported, not silently skipped — and none may raise."""
    from scripts.style_alignment_report import report

    result = report(composed, "mozart")
    failed = [
        f"{label}: {key}" for label, key, *_ in result["rows"] if key.startswith("<probe failed")
    ]
    assert not failed, "probe(s) raised: " + "; ".join(failed)
    assert result["bars"] > 0


def test_every_metric_is_compared_against_a_member_not_a_pool(composed):
    """The whole point of the report.

    A row with no comparison is a row that cannot say anything, and a row
    compared against a pooled mean is the error that cost both sessions most.
    """
    from scripts.style_alignment_report import report

    result = report(composed, "mozart")
    uncompared = [f"{label}: {key}" for label, key, _got, med, *_ in result["rows"] if med is None]
    assert not uncompared, "metric(s) with no median-movement comparison: " + "; ".join(uncompared)
    assert len(result["rows"]) >= 10, len(result["rows"])


def test_the_quartiles_bracket_the_median(composed):
    """Guard the guard: p25 <= median <= p75, or the 'outside' flag is noise."""
    from scripts.style_alignment_report import report

    for label, key, _got, med, p25, p75 in report(composed, "mozart")["rows"]:
        if med is None:
            continue
        assert p25 <= med <= p75, f"{label}/{key}: {p25} / {med} / {p75}"


def test_a_composer_with_too_few_movements_reports_no_comparison_rather_than_a_guess(composed):
    from scripts.style_alignment_report import _median_movement

    from scales.style_dimensions import melodic_metrics

    assert _median_movement("no-such-composer", melodic_metrics) is None
