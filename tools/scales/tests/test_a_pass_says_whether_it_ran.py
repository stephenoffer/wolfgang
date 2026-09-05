"""A pass that never fired and a pass that found nothing to do look identical.

Both return 0 and say nothing. `_rest_the_downbeat` was inert on every planned
piece — a motif placement protects a whole phrase, and planning puts one on most
of them — and it reported exactly what it would have reported if it were working
perfectly. Finding that took an A/B run with the pass monkeypatched out.

`planning_gaps` says which INPUTS were missing. This says which passes actually
reached the notes, and reports the zeroes, because a zero is the informative case.
"""

import contextlib
import io
import shutil
import warnings

import pytest

from scales import scales as S

pytestmark = pytest.mark.calibration

_PASSES = {
    "melody_thickened",
    "bass_thickened",
    "cadences_shaped",
    "barline_ties",
    "downbeat_rests",
}


def _run(piece_id, **kwargs):
    shutil.rmtree(S._WORKSPACE / piece_id, ignore_errors=True)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        S.init_workspace(piece_id, mode="compose_from_text", description="a short piece")
        S.compile_style(piece_id, composers=[kwargs.get("composer", "mozart")])
        S.build_form_graph(
            piece_id, form="ternary", key="D minor", tempo_bpm=92, meter=(4, 4)
        )
        graph = S._load_graph(piece_id)
        section = sorted({p.slot.section_id for p in graph.phrases.values() if p.slot})[0]
        return S.run_scales_section(piece_id, section_id=section)


def test_the_result_says_what_every_surface_pass_did():
    result = _run("_t_passes_1")
    try:
        report = result.get("surface_passes")
        assert isinstance(report, dict), f"no surface_passes in {sorted(result)}"
        assert set(report) == _PASSES, f"passes missing from the report: {_PASSES - set(report)}"
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_1", ignore_errors=True)


def test_the_zeroes_are_reported_not_omitted():
    """The whole point. A pass reporting nothing is what a broken pass looks
    like, so the report must distinguish 'did nothing' from 'was not mentioned'."""
    result = _run("_t_passes_2")
    try:
        report = result.get("surface_passes") or {}
        idle = result.get("surface_passes_idle")
        zeros = {name for name, count in report.items() if not count}
        if zeros:
            assert idle is not None, "passes did nothing and nothing said so"
            assert set(idle) == zeros
        else:
            assert idle is None
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_2", ignore_errors=True)


def test_at_least_one_pass_reaches_the_notes_on_an_ordinary_piece():
    """If every pass is idle on a plain Mozart ternary, the texture work is not
    running at all — which is the failure this report exists to expose."""
    result = _run("_t_passes_3")
    try:
        report = result.get("surface_passes") or {}
        assert sum(report.values()) > 0, f"every surface pass was idle: {report}"
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_3", ignore_errors=True)


def test_the_counts_are_whole_numbers_not_booleans():
    """`cadences_shaped` returns a bool from its pass; counting it as one would
    make two shaped cadences read as True."""
    result = _run("_t_passes_4")
    try:
        for name, count in (result.get("surface_passes") or {}).items():
            assert isinstance(count, int) and not isinstance(count, bool), f"{name}={count!r}"
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_4", ignore_errors=True)


def test_an_idle_pass_says_which_rule_declined():
    """`declined: 9` says a pass is declining and not why. The whole value is
    naming the rule: Haydn's `barline_ties` is idle because his own measured
    rate of 0.015 per bar grants a quota of zero over a six-bar span — which is
    correct, and unreadable as a bare `0`."""
    result = _run("_t_passes_5", composer="haydn")
    try:
        detail = result.get("surface_pass_detail") or {}
        assert detail, "no per-pass detail at all"
        for name, report in detail.items():
            assert report.get("pass") == name
            assert "considered" in report and "applied" in report
            if not report.get("applied"):
                explained = report.get("reason") or report.get("declined")
                assert explained, f"{name} did nothing and gave no reason: {report}"
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_5", ignore_errors=True)


def test_a_decline_reason_is_a_sentence_not_a_code():
    """The reader is a person deciding which rule to look at."""
    result = _run("_t_passes_6")
    try:
        for report in (result.get("surface_pass_detail") or {}).values():
            for why in (report.get("declined") or {}):
                assert " " in why, f"{why!r} is a code, not a reason"
    finally:
        shutil.rmtree(S._WORKSPACE / "_t_passes_6", ignore_errors=True)
