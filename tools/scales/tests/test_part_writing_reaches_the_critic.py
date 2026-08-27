"""Part-writing must reach the thing that judges the music.

`analyze_counterpoint` finds parallel fifths and octaves, hidden octaves into
cadences, doubled leading tones, unresolved sevenths and voice independence. It
lived only in `musical_report`, while the music-critic's own description says it
sees "only the score and the self_evaluate discriminator report" and
`w-review/SKILL.md` hands it exactly that.

So a three-voice fugue with **5 parallel fifths and 2 parallel octaves** passed
review with nothing to look at, and a Palestrina motet with 6 parallel fifths —
the one prohibition that style treats as near-absolute — did too.

The fixture is built here rather than read from `workspace/`, so the test owns
everything it asserts on.
"""

import shutil

import pytest

_PID = "_test_part_writing"


@pytest.fixture()
def piece():
    from scales.scales import (
        _WORKSPACE,
        build_form_graph,
        commit_agent_phrase_direct_bars,
        compile_style,
        get_composition_brief,
        init_workspace,
    )

    ws = _WORKSPACE / _PID
    shutil.rmtree(ws, ignore_errors=True)
    init_workspace(_PID, mode="compose_from_text", description="A study for solo piano")
    compile_style(_PID, composers=["bach"])
    build_form_graph(_PID, form="simple", key="C major", tempo_bpm=90, meter=(4, 4))
    from scales.piece_graph import PieceGraph

    g = PieceGraph.load(str(ws / "piece_graph.json"))
    pid = sorted(g.phrases, key=lambda k: g.phrases[k].slot.bar_start)[0]
    slot = g.phrases[pid].slot
    # Genuine parallel octaves, NOT a doubling. Two lines running in octaves the
    # whole way are one line doubled — `detect_parallel_perfects` exempts that on
    # purpose, because without the exemption it fired 217 times on 770 canonical
    # bars. These two voices move in octaves once and then diverge to tenths.
    bars = [{"rh": "C5q D5q A4q B4q", "lh": "C4q D4q F3q G3q"} for _ in range(slot.bar_count)]
    get_composition_brief(_PID, pid, composer="bach")
    r = commit_agent_phrase_direct_bars(_PID, pid, bars, composer="bach")
    if not r.get("ok"):
        pytest.skip(f"fixture would not commit: {r}")
    yield _PID
    shutil.rmtree(ws, ignore_errors=True)


def test_self_evaluate_carries_a_part_writing_section(piece):
    from scales.scales import self_evaluate

    pw = self_evaluate(piece).get("part_writing") or {}
    assert pw, "self_evaluate has no part_writing section"
    for k in ("errors", "warnings", "independence", "by_kind", "lines"):
        assert k in pw, f"part_writing is missing {k!r}"


def test_bare_parallel_octaves_are_reported(piece):
    from scales.scales import self_evaluate

    pw = self_evaluate(piece).get("part_writing") or {}
    kinds = pw.get("by_kind") or {}
    assert any("parallel" in k for k in kinds), kinds


def test_findings_are_locatable(piece):
    """A finding a reviewer cannot find in the score is not actionable."""
    from scales.scales import self_evaluate

    for line in (self_evaluate(piece).get("part_writing") or {}).get("lines") or []:
        assert "bar" in str(line).lower(), line


def test_an_analyser_failure_never_breaks_the_report(piece, monkeypatch):
    """The report is what the reviewer reads; one broken analyser must not take
    the whole thing down.

    Tested by BREAKING the analyser and reading the report, rather than by
    inspecting the source for a try/except. The previous versions asked the
    question of the text — first by character distance, then structurally
    through the AST — and both went through `inspect.getsource`, which locates a
    function by the line number recorded when the module was IMPORTED. Once the
    file changes on disk that returns whatever now occupies those lines, which
    is what made this intermittent. A guard is a behaviour; the only way to know
    it holds is to need it.
    """
    import scales.counterpoint as cp_mod
    from scales.scales import self_evaluate

    def _explode(*_a, **_k):
        raise RuntimeError("the analyser is broken")

    monkeypatch.setattr(cp_mod, "analyze_counterpoint", _explode)

    report = self_evaluate(piece)
    assert isinstance(report, dict) and "error" not in report, (
        "a broken analyser took the whole report down"
    )
    # And it says so rather than pretending the analysis ran clean.
    pw = report.get("part_writing")
    assert pw is not None, "part-writing must still be reported, even as a failure"
    assert "error" in pw, f"a failed analyser must report its failure, got {pw!r}"
    assert "RuntimeError" in str(pw["error"]), pw


# ─── The utilization report, also documented as reaching the critic ──────────


def test_self_evaluate_carries_the_utilization_report(piece):
    """CLAUDE.md documents `context_utilization` as "embedded in self_evaluate".
    It was wired into `run_scales_section` only, so the reviewer — whose whole
    input is this report — could not tell a phrase built from the briefed corpus
    exemplars from one invented beside them."""
    from scales.scales import self_evaluate

    cu = self_evaluate(piece).get("context_utilization")
    assert cu, "self_evaluate carries no context_utilization"
    assert "error" not in cu, cu


def test_an_agent_authored_piece_is_not_reported_as_zero_corpus_use(piece):
    """The engine populates those counters and an agent commit does not, so the
    raw report is all zeros on the default path. Handed to a reviewer that reads
    as "this piece used no corpus evidence at all" — a number that looks like
    evidence and is not."""
    from scales.scales import self_evaluate

    cu = self_evaluate(piece).get("context_utilization") or {}
    if cu.get("path") != "agent_authored":
        pytest.skip("fixture did not take the agent path")
    assert cu["phrases_briefed"] >= 1
    assert cu["exemplars_shown"] >= 1
    assert "note" in cu, "the inapplicable-counter caveat must travel with it"


def test_a_persisted_trace_is_usable(piece):
    """`context_trace` round-trips through JSON as a plain dict while
    `compute_utilization` reads dataclass attributes, so on any graph loaded
    from disk — which is every graph a reviewer sees — the report raised."""
    from scales.models import ContextTrace
    from scales.piece_graph import PieceGraph, _dataclass_from_dict
    from scales.scales import _WORKSPACE

    g = PieceGraph.load(str(_WORKSPACE / piece / "piece_graph.json"))
    for pid, ps in g.phrases.items():
        raw = getattr(ps, "context_trace", None)
        if not isinstance(raw, dict) or not raw:
            continue
        t = _dataclass_from_dict(ContextTrace, {"phrase_id": pid, **raw})
        assert hasattr(t, "total_bar_count")
        break


# ─── The craft checklist, third of the same shape ────────────────────────────


def test_self_evaluate_carries_the_craft_checklist(piece):
    """`craft_checker` runs on every commit and stores its result on the phrase.
    Nothing surfaced it: the reviewer, whose whole input is this report, never
    saw a single craft finding."""
    from scales.scales import self_evaluate

    c = self_evaluate(piece).get("craft")
    if not c:
        pytest.skip("fixture produced no craft findings")
    assert "error" not in c, c
    assert c["count"] >= 1
    assert all("phrase" in f and "note" in f for f in c["findings"])


def test_the_craft_findings_travel_with_their_false_positive_rate():
    """Measured over 200 real corpus phrases from five composers, the individual
    checks fire on 1.5%-13.5% of real music. A reviewer handed them without that
    context would read a hint as a verdict."""
    import inspect

    from scales import scales as S

    src = inspect.getsource(S.self_evaluate)
    i = src.index('report["craft"]')
    window = src[max(0, i - 1400) : i + 900]
    assert "Advisory" in window
    assert "13.5%" in window
