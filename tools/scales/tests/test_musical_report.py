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
from scales.musical_report import build_report, concerns_only, render_text
from scales.piece_graph import PieceGraph


def _ev(bar, beat, pitch, dur="q", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _graph(phrase_specs, piece_id="test-piece"):
    """phrase_specs: [(phrase_id, bar_start, bars, cadence_target, melody, bass)]"""
    g = PieceGraph()
    g.piece_id = piece_id
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


def test_a_contour_miss_is_reported_as_a_floor_not_a_fact():
    """Contour matching is a LOWER BOUND and must not be stated as a count.

    Ground truth: six Mozart variations that provably contain their theme. This
    matcher finds four of them and also matches unrelated material a third of
    the time. Reporting a miss as "the theme never returns" overstates a
    measurement that cannot support it — and an earlier version of this module,
    which matched the WHOLE contour rather than the head, said exactly that
    about every piece it was ever run on.
    """
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    g = _graph([("m1_a_p1", 1, 2, "PAC", mel, bass)])
    g.principal_theme_surface = LayerIR(
        key="C major",
        principal_line=[_ev(1, 1 + i, p) for i, p in enumerate(["C5", "G5", "E5", "C5"])],
    )
    rep = build_report(g, style="mozart")
    said = " ".join(rep.theme["observations"] + rep.theme["concerns"])
    assert "floor rather than a count" in said or "at least" in said
    assert "never returns" not in said


def test_a_planned_placement_is_reported_as_exact():
    """When the plan records placements, the answer is not inferred at all."""
    from scales.models import MotifTransform

    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "A5", "B5", "C6"])
    g = _graph([("m1_a_p1", 1, 1, "PAC", mel1, bass1), ("m1_b_p1", 2, 1, "PAC", mel2, bass2)])
    g.principal_theme_id = "motif_A"
    g.principal_theme_surface = LayerIR(
        key="C major",
        principal_line=[_ev(1, 1 + i, p) for i, p in enumerate(["C5", "D5", "E5", "F5"])],
    )
    for pid in ("m1_a_p1", "m1_b_p1"):
        g.phrases[pid].slot.motif_transforms = [
            MotifTransform(operation="state", params={"motif_id": "motif_A"})
        ]
    rep = build_report(g, style="mozart")
    assert rep.theme["evidence_source"] == "plan"
    assert rep.theme["recurrences"] == 2
    assert any("brings the theme back in 2 sections" in o for o in rep.theme["observations"])


def test_a_plan_that_states_the_theme_once_is_a_real_concern():
    """With exact evidence, a single placement CAN be reported as a defect."""
    from scales.models import MotifTransform

    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "A5", "B5", "C6"])
    g = _graph([("m1_a_p1", 1, 1, "PAC", mel1, bass1), ("m1_b_p1", 2, 1, "PAC", mel2, bass2)])
    g.principal_theme_id = "motif_A"
    g.principal_theme_surface = LayerIR(
        key="C major",
        principal_line=[_ev(1, 1 + i, p) for i, p in enumerate(["C5", "D5", "E5", "F5"])],
    )
    g.phrases["m1_a_p1"].slot.motif_transforms = [
        MotifTransform(operation="state", params={"motif_id": "motif_A"})
    ]
    rep = build_report(g, style="mozart")
    assert rep.theme["evidence_source"] == "plan"
    assert any("never brought back" in c for c in rep.theme["concerns"])


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
    # Eight bars is the point at which one unchanging texture is reported: long
    # enough that a listener stops hearing it, short enough that four bars of a
    # deliberately steady accompaniment is left alone.
    tune = ["C5", "D5", "E5", "F5"] * 8
    mel, bass = _plain_phrase(1, tune)
    rep = build_report(_graph([("m1_a_p1", 1, 8, "PAC", mel, bass)]), style="mozart")
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
    g = PieceGraph()
    g.piece_id = "empty"
    rep = build_report(g)
    assert rep.phrases == 0
    assert "nothing realized yet" in rep.page["observations"]
    render_text(rep)  # must not raise


def test_dict_shaped_realized_material_is_read_too():
    """Callers hold both shapes; reading only one looks like a clean score."""
    g = PieceGraph()
    g.piece_id = "dict-form"
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
    tune = ["C5", "D5", "E5", "F5"] * 8
    mel, bass = _plain_phrase(1, tune)
    rep = build_report(_graph([("m1_a_p1", 1, 8, "PAC", mel, bass)]), style="mozart")
    assert len(concerns_only(rep)) >= 2


def test_scope_limits_the_report_to_one_section():
    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "A5", "B5", "C6"])
    g = _graph([("m1_a_p1", 1, 1, "PAC", mel1, bass1), ("m1_b_p1", 2, 1, "PAC", mel2, bass2)])
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


# ─── Orchestration ───────────────────────────────────────────────────────────


def test_an_unplayable_orchestral_part_reaches_the_report():
    """A note at the outer edge of an instrument is legal and miserable."""
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    g = _graph([("m1_a_p1", 1, 1, "PAC", mel, bass)])
    g.phrases["m1_a_p1"].orchestration = {
        "flute": [{"pitch": "C4", "dynamic": "pp"}, {"pitch": "G5"}],
        "trumpet": [{"pitch": "C4", "dynamic": "pp"}, {"pitch": "Bb5"}],
    }
    rep = build_report(g, style="mozart")
    joined = " ".join(rep.orchestration["concerns"])
    assert "flute" in joined and "will not speak" in joined
    assert "trumpet" in joined and "cannot be played softly" in joined


def test_comfortable_orchestration_draws_no_complaint():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    g = _graph([("m1_a_p1", 1, 1, "PAC", mel, bass)])
    g.phrases["m1_a_p1"].orchestration = {
        "violin": [{"pitch": "G4", "dynamic": "mf"}, {"pitch": "C5"}],
        "cello": [{"pitch": "C3", "dynamic": "mf"}],
    }
    rep = build_report(g, style="mozart")
    assert rep.orchestration["concerns"] == []
    assert any("orchestrated for" in o for o in rep.orchestration["observations"])


def test_a_piano_piece_says_nothing_about_orchestration():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    rep = build_report(_graph([("m1_a_p1", 1, 1, "PAC", mel, bass)]), style="mozart")
    assert rep.orchestration["observations"] == []
    assert rep.orchestration["concerns"] == []


# ─── Continuity across a phrase boundary ─────────────────────────────────────


def test_a_dissonance_left_hanging_across_a_boundary_is_reported():
    """Nothing carried this across a barline, so phrase N+1 never knew it."""
    mel1 = [_ev(1, 1.0, "C5", "h"), _ev(1, 3.0, "F5", "h")]
    bass1 = [_ev(1, 1.0, "C3", "w")]
    mel2, bass2 = _plain_phrase(2, ["E5", "D5", "C5", "B4"])
    g = _graph([("m1_a_p1", 1, 1, "HC", mel1, bass1), ("m1_a_p2", 2, 1, "PAC", mel2, bass2)])
    g.phrases["m1_a_p1"].realized.counter_reply = [_ev(1, 3.0, "Bb4", "h")]
    rep = build_report(g, style="mozart")
    assert any("dissonance still sounding" in c for c in rep.continuity["concerns"])


def test_a_line_that_continues_draws_no_complaint():
    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "F5", "E5", "D5"])
    g = _graph([("m1_a_p1", 1, 1, "HC", mel1, bass1), ("m1_a_p2", 2, 1, "PAC", mel2, bass2)])
    rep = build_report(g, style="mozart")
    assert rep.continuity["concerns"] == []
    assert any("picks up near" in o for o in rep.continuity["observations"])


def test_repeated_octave_jumps_between_phrases_are_reported():
    """One leap across a boundary is a gesture; every time is fragments."""
    specs = []
    for i in range(4):
        pitches = ["C3", "D3", "E3", "F3"] if i % 2 else ["C6", "D6", "E6", "F6"]
        mel, bass = _plain_phrase(i + 1, pitches)
        specs.append((f"m1_a_p{i + 1}", i + 1, 1, "PAC", mel, bass))
    rep = build_report(_graph(specs), style="mozart")
    assert any("jump more than an octave" in c for c in rep.continuity["concerns"])


def test_a_single_phrase_says_nothing_about_continuity():
    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    rep = build_report(_graph([("m1_a_p1", 1, 1, "PAC", mel, bass)]), style="mozart")
    assert rep.continuity["concerns"] == []
    assert rep.continuity["observations"] == []


def test_each_phrases_tail_is_reported_for_the_next_one():
    mel1, bass1 = _plain_phrase(1, ["C5", "D5", "E5", "F5"])
    mel2, bass2 = _plain_phrase(2, ["G5", "F5", "E5", "D5"])
    g = _graph([("m1_a_p1", 1, 1, "HC", mel1, bass1), ("m1_a_p2", 2, 1, "PAC", mel2, bass2)])
    tails = build_report(g, style="mozart").continuity["tails"]
    assert "m1_a_p1" in tails
    assert "the melody ended on" in tails["m1_a_p1"]


# ─── Orchestral material must survive the trip to the critic ─────────────────
#
# Three separate hand-written layer lists in this module carried only the five
# PIANO layers. LayerIR has eleven. An orchestral piece therefore reached the
# critic as an empty report — every orchestral note dropped, `bar_count` derived
# from an empty `principal_line` (so: 1), and `instrumentation` never carried,
# which meant the ensemble texture floors could not fire on the production path
# at all no matter how carefully they were measured.
#
# These tests go through `build_report`, deliberately. The earlier ensemble
# tests passed because they handed `analyze_voicing` a LayerIR they had built
# themselves with `instrumentation="ensemble"` — they proved the floors worked
# when reached, never that anything reached them. Testing the object you
# constructed rather than the one production builds is the failure this session
# has now hit four times.


def _orchestral_graph(bars=8):
    g = PieceGraph()
    g.piece_id = "orch-piece"
    slot = PhraseSlot(
        phrase_id="m1_a_p1",
        section_id="m1_a",
        bar_start=1,
        bar_count=bars,
        key="C major",
        meter=(4, 4),
        cadence_bar=bars,
        cadence_target="PAC",
    )
    ir = LayerIR(phrase_id="m1_a_p1", key="C major", meter=(4, 4), instrumentation="ensemble")
    # The six orchestral layers default to None, not [] — the same asymmetry
    # that made the merge above crash the moment orchestral music reached it.
    ir.foreground, ir.harmonic_mass, ir.punctuation = [], [], []
    tune = ["C5", "D5", "E5", "F5", "G5", "A5", "G5", "E5"]
    for b in range(1, bars + 1):
        for i, p in enumerate(tune[:4]):
            ir.foreground.append(_ev(b, 1.0 + i, p, "q"))
        ir.harmonic_mass.append(_ev(b, 1.0, ["E4", "G4"], "w"))
        ir.punctuation.append(_ev(b, 1.0, "C2", "w"))
    g.phrases["m1_a_p1"] = PhraseState(slot=slot, realized=ir, status="realized")
    return g


def test_an_orchestral_piece_does_not_reach_the_critic_empty():
    report = build_report(_orchestral_graph(bars=8))
    assert report.bars == 8, (
        f"the report counted {report.bars} bars in an 8-bar orchestral phrase — "
        "bar_count is being derived from a piano layer that orchestral music "
        "never populates"
    )
    text = render_text(report)
    assert "nothing realized yet" not in text
    assert report.page.get("marks_per_bar") is not None


def test_instrumentation_survives_to_the_texture_floors():
    """Otherwise every ensemble piece is judged by the piano floors."""
    from scales.musical_report import _merge, _ordered_phrases, _phrase_layer

    g = _orchestral_graph()
    layers = [_phrase_layer(st, sl) for _pid, st, sl in _ordered_phrases(g)]
    assert layers[0].instrumentation == "ensemble", "dropped rebuilding the phrase"
    assert _merge(layers).instrumentation == "ensemble", "dropped merging the piece"


def test_the_ensemble_relaxation_actually_reaches_production():
    """The end-to-end claim: ensemble scoring draws no hand-span complaint."""
    concerns = " ".join(concerns_only(build_report(_orchestral_graph())))
    assert "hand" not in concerns.lower(), (
        f"an ensemble piece was told its hands cannot reach: {concerns}"
    )


def test_a_piano_piece_is_still_judged_as_a_piano_piece():
    """Relaxing for ensembles must not quietly relax the keyboard case."""
    from scales.musical_report import _merge, _ordered_phrases, _phrase_layer

    mel, bass = _plain_phrase(1, ["C5", "D5", "E5", "F5"] * 4)
    g = _graph([("m1_a_p1", 1, 4, "PAC", mel, bass)])
    layers = [_phrase_layer(st, sl) for _pid, st, sl in _ordered_phrases(g)]
    merged = _merge(layers)
    from scales.voicing import _is_keyboard, floors_for

    assert _is_keyboard(merged)
    assert floors_for("mozart", merged)["simultaneity_cv"] > 0.0
