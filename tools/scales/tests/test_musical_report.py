"""The report the critic reads.

Analysis nobody reads changes nothing. The fresh-ears critic drives every
artistic revision, and it received z-scores and corpus distances — while the
questions a musician actually asks on opening a score had no answers anywhere:
does the theme come back, are the cadences all the same, does the texture ever
move, is anything on the page for a player to interpret.

The contract these tests pin: findings are musical sentences, not distances from
a distribution, and nothing in the report is a verdict.
"""

import pytest

from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph
from scales.musical_report import build_report, concerns_only, render_text


def _ev(bar, beat, pitch, dur="q", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _graph(phrase_specs, piece_id="test-piece"):
    """phrase_specs: [(phrase_id, bar_start, bars, cadence_target, melody, bass)]"""
    g = PieceGraph(piece_id=piece_id)
    for pid, bar_start, bars, cad, melody, bass in phrase_specs:
        slot = PhraseSlot(
            phrase_id=pid,
            section_id=pid.rsplit("_p", 1)[0],
            bar_start=bar_start,
            bar_count=bars,
            key="C major",
            meter=(4, 4),
            cadence_bar=bar_start + bars - 1,
            cadence_target=cad,
        )
        ir = LayerIR(phrase_id=pid, key="C major", meter=(4, 4))
        ir.principal_line = list(melody)
        ir.bass_foundation = list(bass)
        g.phrases[pid] = PhraseState(slot=slot, realized=ir, status="realized")
    return g


def _plain_phrase(bar_start, tune, bass_pitch="C3"):
    mel = [_ev(bar_start + i // 4, 1 + (i % 4), p) for i, p in enumerate(tune)]
    bass = [_ev(bar_start + b, 1.0, bass_pitch, "w") for b in range(max(1, len(tune) // 4))]
    return mel, bass


# ─── It reports the things nothing else did ──────────────────────────────────


def test_a_theme_that_never_returns_is_reported():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    g = _graph([("m1_a_p1", 1, 2, "PAC", mel, bass)])
    g.principal_theme_surface = LayerIR(
        key="C major", principal_line=[_ev(1, 1 + i, p) for i, p in enumerate(["C5", "G5", "E5", "C5"])]
    )
    rep = build_report(g, style="mozart")
    assert any("never returns" in c or "1 place" in c for c in rep.theme["concerns"])


def test_a_piece_with_no_theme_at_all_says_so():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    rep = build_report(_graph([("m1_a_p1", 1, 1, "PAC", mel, bass)]), style="mozart")
    assert any("no memory" in o or "No principal theme" in o for o in rep.theme["observations"])


def test_an_unengraved_page_is_reported():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    rep = build_report(_graph([("m1_a_p1", 1, 2, "PAC", mel, bass)]), style="mozart")
    joined = " ".join(rep.page["concerns"])
    assert "articulation" in joined
    assert rep.page["marks_per_bar"] == 0


def test_an_engraved_page_draws_no_complaint():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    for e in mel:
        e.articulation = "staccato"
    mel[0].slur, mel[-1].slur = "start", "stop"
    mel[0].dynamic = "p"
    mel[0].tie = "start"
    rep = build_report(_graph([("m1_a_p1", 1, 2, "PAC", mel, bass)]), style="mozart")
    assert not any("Not one articulation" in c for c in rep.page["concerns"])


def test_a_cadence_that_disagrees_with_the_plan_is_reported():
    """Nothing checked `cadence_target` against the notes before."""
    mel = [_ev(1, 1.0, "D5", "h"), _ev(1, 3.0, "B4", "h"), _ev(2, 1.0, "C5", "w")]
    bass = [_ev(1, 1.0, "G2", "w"), _ev(2, 1.0, "C3", "w"), _ev(2, 3.0, ["E3", "G3"], "h")]
    g = _graph([("m1_a_p1", 1, 2, "HC", mel, bass)])
    rep = build_report(g, style="mozart")
    assert any("planned HC" in o for o in rep.cadences["observations"])


def test_a_long_unchanging_texture_run_is_reported():
    tune = ["C5", "D5", "E5", "F5"] * 4
    mel, bass = _plain_phrase(1, tune)
    rep = build_report(_graph([("m1_a_p1", 1, 4, "PAC", mel, bass)]), style="mozart")
    assert any("hold one texture" in c for c in rep.texture["concerns"])


def test_parallel_octaves_reach_the_report():
    mel = [_ev(1, 1.0, "E5"), _ev(1, 2.0, "C5"), _ev(1, 3.0, "D5")]
    bass = [_ev(1, 1.0, "G3"), _ev(1, 2.0, "C3"), _ev(1, 3.0, "D3")]
    rep = build_report(_graph([("m1_a_p1", 1, 1, "PAC", mel, bass)]), style="mozart")
    assert "parallel_octaves" in rep.part_writing["by_kind"]


# ─── The contract ────────────────────────────────────────────────────────────


def test_the_report_speaks_in_sentences_not_z_scores():
    """Handing a composer a z-score turns composition into metric whack-a-mole."""
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    text = render_text(build_report(_graph([("m1_a_p1", 1, 2, "PAC", mel, bass)]), style="mozart"))
    assert "z=" not in text and "z-score" not in text
    assert "sigma" not in text.lower()


def test_it_renders_without_a_realized_phrase():
    g = PieceGraph(piece_id="empty")
    rep = build_report(g)
    assert rep.phrases == 0
    assert "nothing realized yet" in rep.page["observations"]
    render_text(rep)  # must not raise


def test_dict_shaped_realized_material_is_read_too():
    """Callers hold both shapes; reading only one looks like a clean score."""
    g = PieceGraph(piece_id="dict-form")
    slot = PhraseSlot(
        phrase_id="m1_a_p1",
        section_id="m1_a",
        bar_start=1,
        bar_count=1,
        key="C major",
        meter=(4, 4),
        cadence_bar=1,
    )
    g.phrases["m1_a_p1"] = PhraseState(
        slot=slot,
        realized={
            "principal_line": [
                {"bar": 1, "beat": 1.0, "pitch": "C5", "duration": "q"},
                {"bar": 1, "beat": 2.0, "pitch": "E5", "duration": "q"},
            ],
            "bass_foundation": [{"bar": 1, "beat": 1.0, "pitch": "C3", "duration": "h"}],
        },
        status="realized",
    )
    rep = build_report(g)
    assert rep.phrases == 1
    assert rep.bars == 1


def test_concerns_only_gathers_every_section():
    tune = ["C5", "D5", "E5", "F5"] * 4
    mel, bass = _plain_phrase(1, tune)
    rep = build_report(_graph([("m1_a_p1", 1, 4, "PAC", mel, bass)]), style="mozart")
    assert len(concerns_only(rep)) >= 2


def test_scope_limits_the_report_to_one_section():
    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "A5", "B5", "C6"])
    g = _graph(
        [("m1_a_p1", 1, 1, "PAC", mel1, bass1), ("m1_b_p1", 2, 1, "PAC", mel2, bass2)]
    )
    assert build_report(g, scope="section-m1_a").phrases == 1
    assert build_report(g, scope="full").phrases == 2


def test_render_respects_its_line_budget():
    tune = ["C5", "D5", "E5", "F5"] * 8
    mel, bass = _plain_phrase(1, tune)
    rep = build_report(_graph([("m1_a_p1", 1, 8, "PAC", mel, bass)]), style="mozart")
    assert len(render_text(rep, max_lines=10).splitlines()) <= 11


@pytest.mark.parametrize("style", ["mozart", "chopin", "bach", None])
def test_every_style_reports_without_error(style):
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    rep = build_report(_graph([("m1_a_p1", 1, 2, "PAC", mel, bass)]), style=style)
    assert rep.bars == 2
    render_text(rep)
