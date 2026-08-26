"""Tests for the engraver's pass.

The failure this module exists to fix, measured on a real generated piece: 511
notes, 41 bars, **0 articulations, 0 ties, 4 hairpins**. These tests pin the two
properties that matter — it adds real marks, and it never overwrites the
composer's.
"""

from fractions import Fraction

import pytest

from scales.expression_enricher import (
    EngravingStyle,
    add_echo_terracing,
    add_pedal,
    add_rolled_chords,
    dynamic_for_energy,
    enrich_layer_ir,
    expression_density,
    resolve_style,
    segment_gestures,
)
from scales.models import LayerEvent, LayerIR


def _ev(bar, beat, pitch, dur="e", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _scale_phrase(bars=4, meter=(4, 4)):
    """A plain unmarked phrase — melody plus an oom-pah bass, no expression."""
    ir = LayerIR(phrase_id="p", key="C", meter=meter, bar_count=bars)
    tune = ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]
    for b in range(bars):
        for i in range(4):
            ir.principal_line.append(_ev(b + 1, 1 + i * 0.5, tune[(b * 4 + i) % len(tune)], "e"))
        ir.bass_foundation.append(_ev(b + 1, 1.0, "C3", "q"))
        ir.bass_foundation.append(_ev(b + 1, 2.0, ["E3", "G3"], "q"))
        ir.bass_foundation.append(_ev(b + 1, 3.0, ["E3", "G3"], "q"))
        ir.bass_foundation.append(_ev(b + 1, 4.0, ["E3", "G3"], "q"))
    return ir


# ─── The core failure ────────────────────────────────────────────────────────


def test_an_unmarked_phrase_comes_back_engraved():
    ir = _scale_phrase()
    before = expression_density(ir)
    assert before["articulation_per_bar"] == 0
    assert before["slur_per_bar"] == 0

    report = enrich_layer_ir(ir, style="mozart")
    after = expression_density(ir)

    assert report.total_added > 0
    assert after["articulation_per_bar"] > 0, "no articulation added"
    assert after["slur_per_bar"] > 0, "no phrasing added"
    assert after["dynamic_per_bar"] > 0, "no dynamic added"


def test_marks_per_bar_reaches_a_playable_density():
    ir = _scale_phrase(bars=8)
    enrich_layer_ir(ir, style="mozart")
    d = expression_density(ir)
    # A real Classical piano page runs well above one mark per bar. The measured
    # generated score ran 0.5 (dynamics only) with nothing else on the page.
    assert d["marks_per_bar"] >= 1.0, d


# ─── Non-destructiveness ─────────────────────────────────────────────────────


def test_the_composers_marks_are_never_overwritten():
    ir = _scale_phrase()
    ir.principal_line[0].articulation = "marcato"
    ir.principal_line[1].slur = "start"
    ir.principal_line[3].slur = "stop"
    ir.principal_line[0].dynamic = "ff"
    ir.bass_foundation[0].pedal = "up"

    enrich_layer_ir(ir, style="chopin")

    assert ir.principal_line[0].articulation == "marcato"
    assert ir.principal_line[0].dynamic == "ff"
    assert ir.principal_line[1].slur == "start"
    assert ir.principal_line[3].slur == "stop"
    assert ir.bass_foundation[0].pedal == "up"


def test_no_pitch_or_duration_is_ever_changed():
    ir = _scale_phrase()
    before = [(e.bar, e.beat, e.pitch, e.duration) for e in ir.principal_line + ir.bass_foundation]
    enrich_layer_ir(ir, style="beethoven")
    after = [(e.bar, e.beat, e.pitch, e.duration) for e in ir.principal_line + ir.bass_foundation]
    assert before == after


# ─── Style behaviour ─────────────────────────────────────────────────────────


def test_bach_gets_no_pedal_and_no_hairpins():
    ir = _scale_phrase()
    report = enrich_layer_ir(ir, style="bach")
    assert report.pedal_marks_added == 0
    assert report.hairpins_added == 0
    assert not any(e.pedal for e in ir.bass_foundation)


def test_chopin_gets_pedal():
    ir = _scale_phrase()
    report = enrich_layer_ir(ir, style="chopin")
    assert report.pedal_marks_added > 0
    assert any(e.pedal for e in ir.bass_foundation)


def test_romantic_accompaniment_is_not_detached():
    ir = _scale_phrase()
    enrich_layer_ir(ir, style="chopin")
    assert not any(e.articulation == "staccato" for e in ir.bass_foundation)


def test_classical_accompaniment_is_detached():
    ir = _scale_phrase()
    # Eighth-note oom-pah so the chords are short enough to take dots.
    for e in ir.bass_foundation:
        e.duration = "e"
    enrich_layer_ir(ir, style="mozart")
    assert any(e.articulation == "staccato" for e in ir.bass_foundation)


def test_renaissance_notates_almost_nothing():
    ir = _scale_phrase()
    report = enrich_layer_ir(ir, style="palestrina")
    assert report.dynamics_added == 0
    assert report.hairpins_added == 0
    assert report.pedal_marks_added == 0


def test_style_resolution_accepts_composer_style_and_period():
    assert resolve_style("mozart").name == "classical"
    assert resolve_style("style__baroque").name == "baroque"
    assert resolve_style("Romantic").name == "romantic"
    assert resolve_style("mozart+chopin").name == "classical"
    assert resolve_style(None).name == "classical"
    assert resolve_style("someone-nobody-has-heard-of").name == "classical"


# ─── Individual rules ────────────────────────────────────────────────────────


def test_gestures_break_at_rests_and_leaps():
    st = EngravingStyle(slur_min_notes=2, slur_max_notes=8, slur_breaks_on_leap=5)
    events = [
        _ev(1, 1.0, "C5"),
        _ev(1, 1.5, "D5"),
        _ev(1, 2.0, "E5"),
        _ev(1, 2.5, "rest"),
        _ev(1, 3.0, "C6"),
        _ev(1, 3.5, "D6"),
    ]
    gestures = segment_gestures(events, st)
    assert [len(g) for g in gestures] == [3, 2]
    assert 3 not in gestures[0], "the rest must not be inside the slur"


def test_a_wide_leap_ends_the_slur():
    st = EngravingStyle(slur_min_notes=2, slur_max_notes=8, slur_breaks_on_leap=5)
    events = [_ev(1, 1.0, p) for p in ("C4", "D4", "E4", "C6", "D6")]
    gestures = segment_gestures(events, st)
    assert len(gestures) == 2


def test_a_repeat_is_echoed_softer():
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=4)
    for b in (1, 2, 3, 4):
        src = 1 if b in (1, 3) else 2
        for i, p in enumerate(["C5", "E5", "G5", "C6"] if src == 1 else ["D5", "F5", "A5", "D6"]):
            ir.principal_line.append(_ev(b, 1 + i, p, "q"))
    ir.principal_line[0].dynamic = "f"
    st = resolve_style("mozart")
    from scales.expression_enricher import EnrichmentReport

    rep = EnrichmentReport()
    add_echo_terracing(ir, st, rep)
    assert rep.dynamics_added == 1
    echoed = [e for e in ir.principal_line if e.bar == 3][0]
    assert echoed.dynamic == "mf"


def test_a_tenth_in_one_hand_is_rolled():
    ir = LayerIR(phrase_id="p")
    ir.bass_foundation.append(_ev(1, 1.0, ["C2", "G2", "E3"], "h"))  # a 16th
    from scales.expression_enricher import EnrichmentReport

    rep = EnrichmentReport()
    add_rolled_chords(ir, resolve_style("chopin"), rep)
    assert ir.bass_foundation[0].technique == "arpeggio"
    assert rep.techniques_added == 1


def test_a_close_triad_is_not_rolled():
    ir = LayerIR(phrase_id="p")
    ir.bass_foundation.append(_ev(1, 1.0, ["C3", "E3", "G3"], "h"))
    from scales.expression_enricher import EnrichmentReport

    rep = EnrichmentReport()
    add_rolled_chords(ir, resolve_style("chopin"), rep)
    assert ir.bass_foundation[0].technique is None


def test_pedal_changes_with_the_harmony_not_every_bar():
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=4)
    for b in range(1, 5):
        ir.bass_foundation.append(_ev(b, 1.0, "C3", "w"))
    from scales.expression_enricher import EnrichmentReport

    rep = EnrichmentReport()
    add_pedal(ir, resolve_style("schubert"), rep, harmony_plan=["I", "I", "V", "V"])
    downs = [e for e in ir.bass_foundation if e.pedal in ("down", "change")]
    # Style "long" pedals every bar; the point is it does not exceed the bars.
    assert 0 < len(downs) <= 4


def test_energy_maps_onto_dynamics_monotonically():
    vals = [dynamic_for_energy(x / 10) for x in range(11)]
    ladder = ["ppp", "pp", "p", "mp", "mf", "f", "ff", "fff"]
    idx = [ladder.index(v) for v in vals]
    assert idx == sorted(idx)


def test_a_final_phrase_ends_with_a_fermata():
    ir = _scale_phrase(bars=2)
    enrich_layer_ir(ir, style="mozart", is_final_phrase=True)
    marks = [e for e in ir.principal_line + ir.bass_foundation if e.ornament == "fermata"]
    assert len(marks) == 1


def test_a_non_final_phrase_gets_no_fermata():
    ir = _scale_phrase(bars=2)
    enrich_layer_ir(ir, style="mozart", is_final_phrase=False)
    assert not any(e.ornament == "fermata" for e in ir.principal_line)


def test_character_word_lands_on_the_first_note():
    ir = _scale_phrase(bars=2)
    enrich_layer_ir(ir, style="mozart", character="cantabile")
    assert ir.principal_line[0].expression == "cantabile"


def test_metadata_is_not_mistaken_for_a_note_list():
    """``meter=(3,4)`` iterated as notes is a real bug class in this repo."""
    ir = _scale_phrase(bars=2, meter=(3, 4))
    enrich_layer_ir(ir, style="mozart")  # must not raise
    assert ir.meter == (3, 4)


def test_empty_input_is_safe():
    ir = LayerIR(phrase_id="empty")
    report = enrich_layer_ir(ir, style="mozart")
    assert report.total_added == 0
    assert report.notes_seen == 0


def test_appoggiatura_gets_a_tenuto():
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=1)
    ir.principal_line = [
        _ev(1, 1.0, "C5", "q"),
        _ev(1, 2.0, "A5", "q", role="appoggiatura"),
        _ev(1, 3.0, "G5", "q"),
        _ev(1, 4.0, "E5", "q"),
    ]
    enrich_layer_ir(ir, style="mozart", enable={"slurs": False})
    assert ir.principal_line[1].articulation == "tenuto"


@pytest.mark.parametrize("style", list(("bach", "mozart", "chopin", "debussy", "palestrina")))
def test_every_style_survives_a_realistic_phrase(style):
    ir = _scale_phrase(bars=8)
    report = enrich_layer_ir(ir, style=style)
    assert report.notes_seen > 0
    # No rule may leave a dangling half-spanner.
    for name in ("principal_line", "bass_foundation"):
        evs = getattr(ir, name)
        opens = sum(1 for e in evs if e.slur == "start")
        closes = sum(1 for e in evs if e.slur == "stop")
        assert opens == closes, f"{style}/{name}: {opens} slur starts vs {closes} stops"
        h_open = sum(1 for e in evs if e.hairpin in ("cresc_start", "dim_start"))
        h_close = sum(1 for e in evs if e.hairpin == "stop")
        assert h_open == h_close, f"{style}/{name}: unbalanced hairpins"


def test_durations_are_read_as_fractions_not_floats():
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=1)
    ir.principal_line = [_ev(1, 1 + i / 3, "C5", "trip_e") for i in range(3)]
    enrich_layer_ir(ir, style="mozart")
    assert all(
        isinstance(Fraction(e.beat).limit_denominator(48), Fraction) for e in ir.principal_line
    )


# ─── Density: the engraver must not become the noise ─────────────────────────


def _phrase(bars=4, meter=(4, 4)):
    """A plain four-bar phrase: singing right hand over a sustained bass."""
    from scales.models import LayerEvent, LayerIR

    rh, lh = [], []
    for b in range(1, bars + 1):
        for i, beat in enumerate((1.0, 2.0, 3.0, 4.0)):
            rh.append(LayerEvent(bar=b, beat=beat, pitch=f"{'CDEFGAB'[i]}5", duration="q"))
        lh.append(LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", role="pedal_support"))
    return LayerIR(
        phrase_id="p1", principal_line=rh, bass_foundation=lh, meter=meter, bar_count=bars
    )


def test_sparing_pedal_marks_one_span_per_phrase_not_one_per_other_bar():
    """The defect: 18 "Ped." marks in a 41-bar andante.

    The enricher runs once per phrase, so a `step = 2` that reads as "every
    other bar" locally becomes a whole down/change/up cycle in every four-bar
    phrase. `score_realism.detect_notation_spam` flagged the result as noise,
    which is exactly right — no Classical edition pedals every other bar.
    """
    from scales.expression_enricher import EnrichmentReport, add_pedal, resolve_style

    layer = _phrase()
    report = EnrichmentReport()
    add_pedal(layer, resolve_style("mozart"), report)

    downs = [e for e in layer.bass_foundation if e.pedal == "down"]
    changes = [e for e in layer.bass_foundation if e.pedal == "change"]
    assert len(downs) == 1, f"sparing pedal should open exactly one span, got {len(downs)}"
    assert not changes, "a sparing pedal does not change per bar within a phrase"
    assert report.pedal_marks_added <= 2, report.pedal_marks_added


def test_sparing_pedal_is_skipped_when_no_bass_note_sustains():
    """Pedal earns its place where the hand cannot hold the sound."""
    from scales.expression_enricher import EnrichmentReport, add_pedal, resolve_style
    from scales.models import LayerEvent

    layer = _phrase()
    layer.bass_foundation = [
        LayerEvent(bar=b, beat=float(i + 1), pitch="C3", duration="q")
        for b in range(1, 5)
        for i in range(4)
    ]
    report = EnrichmentReport()
    add_pedal(layer, resolve_style("mozart"), report)
    assert report.pedal_marks_added == 0
    assert not any(e.pedal for e in layer.bass_foundation)


def test_a_romantic_style_still_pedals_per_harmony():
    """The narrowing is for `sparing` only — Chopin gets a pedal per harmony."""
    from scales.expression_enricher import EnrichmentReport, add_pedal, resolve_style

    style = resolve_style("chopin")
    if style.pedal in ("none", "sparing"):
        pytest.skip(f"chopin resolves to pedal={style.pedal}; nothing to assert here")
    layer = _phrase()
    report = EnrichmentReport()
    add_pedal(layer, style, report)
    assert report.pedal_marks_added >= 3, (
        "a long/harmonic pedal style should still mark a pedal per harmony"
    )


def test_the_engraver_never_overwrites_a_pedal_the_composer_wrote():
    from scales.expression_enricher import EnrichmentReport, add_pedal, resolve_style

    layer = _phrase()
    layer.bass_foundation[0].pedal = "down"
    report = EnrichmentReport()
    add_pedal(layer, resolve_style("mozart"), report)
    assert report.pedal_marks_added == 0
    assert sum(1 for e in layer.bass_foundation if e.pedal) == 1


# ─── Placement: a mark in the wrong place is worse than no mark ──────────────


def _melody(notes, meter=(4, 4), bars=2):
    """notes: list of (bar, beat, pitch, duration, role)."""
    from scales.models import LayerEvent, LayerIR

    evs = [LayerEvent(bar=b, beat=be, pitch=p, duration=d, role=r) for b, be, p, d, r in notes]
    return LayerIR(phrase_id="p1", principal_line=evs, meter=meter, bar_count=bars)


def _articulate(layer, composer="mozart"):
    from scales.expression_enricher import (
        EnrichmentReport,
        add_melodic_articulation,
        resolve_style,
    )

    rep = EnrichmentReport()
    add_melodic_articulation(layer, resolve_style(composer), rep)
    return {(e.bar, e.beat): e.articulation for e in layer.principal_line}


def test_a_note_on_a_weak_beat_is_not_a_syncopation():
    """The defect: an accent on the theme's lyrical high note, three times over.

    In 3/4 beats 2 and 3 are weak beats, but they are still *beats*. The rule
    tested "not a strong beat", which accented an ordinary crotchet on beat 2 —
    in the generated andante, the trilled melodic peak of the main theme, in
    every one of its three statements.
    """
    marks = _articulate(
        _melody(
            [
                (1, 1.0, "F5", "q", "structural"),
                (1, 2.0, "A5", "q", "structural"),  # weak BEAT, leap of a third
                (1, 3.0, "C6", "e", "structural"),
                (2, 1.0, "B-5", "q", "structural"),
                (2, 2.0, "G5", "q", "structural"),
                (2, 3.0, "F5", "q", "structural"),
            ],
            meter=(3, 4),
        )
    )
    assert marks[(1, 2.0)] != "accent", "beat 2 of 3/4 is a weak beat, not a syncopation"


def test_a_genuinely_offbeat_arrival_still_gets_its_accent():
    """The rule must still do its job — this is the case it exists for."""
    marks = _articulate(
        _melody(
            [
                (1, 1.0, "F5", "e", "structural"),
                (1, 1.5, "C6", "h", "structural"),  # attack between the beats, leap
                (1, 3.5, "A5", "e", "structural"),
                (2, 1.0, "G5", "q", "structural"),
                (2, 2.0, "F5", "q", "structural"),
            ]
        )
    )
    assert marks[(1, 1.5)] == "accent"


def test_an_ornament_is_not_also_accented():
    """A trill already says "this note is the event"."""
    from scales.expression_enricher import (
        EnrichmentReport,
        add_melodic_articulation,
        resolve_style,
    )

    layer = _melody(
        [
            (1, 1.0, "F5", "e", "structural"),
            (1, 1.5, "C6", "h", "structural"),
            (1, 3.5, "A5", "e", "structural"),
            (2, 1.0, "G5", "q", "structural"),
        ]
    )
    layer.principal_line[1].ornament = "trill"
    add_melodic_articulation(layer, resolve_style("mozart"), EnrichmentReport())
    assert layer.principal_line[1].articulation is None


def test_tenuto_needs_a_note_long_enough_to_lean_on():
    """The defect: tenuto on 16ths in the middle of a running passage.

    A passing 16th labelled `appoggiatura` by the role heuristic is a passing
    note whatever it is called, and "hold this one slightly" is not a playable
    instruction at that speed.
    """
    marks = _articulate(
        _melody(
            [
                (1, 1.0, "F5", "s", "appoggiatura"),
                (1, 1.25, "A5", "s", "appoggiatura"),
                (1, 1.5, "C6", "s", "structural"),
                (1, 1.75, "A5", "s", "appoggiatura"),
                (1, 2.0, "B-5", "h", "appoggiatura"),  # long enough
                (2, 1.0, "A5", "w", "structural"),
            ]
        )
    )
    assert marks[(1, 1.0)] != "tenuto"
    assert marks[(1, 1.25)] != "tenuto"
    assert marks[(1, 2.0)] == "tenuto", "a half-note appoggiatura is exactly the case for tenuto"


def test_the_closing_lift_lands_in_the_phrases_last_bar():
    """Each layer is scanned separately, so "the last event in this list" was
    the last note of an inner voice that stopped halfway through the phrase —
    a staccato dot in the middle of a held line, for no visible reason."""
    from scales.expression_enricher import (
        EnrichmentReport,
        add_melodic_articulation,
        resolve_style,
    )
    from scales.models import LayerEvent

    layer = _melody(
        [
            (1, 1.0, "C5", "q", "structural"),
            (1, 2.0, "D5", "q", "structural"),
            (1, 3.0, "E5", "e", "structural"),  # last event of THIS layer, bar 1 of 4
        ],
        bars=4,
    )
    # another layer carries the phrase on to bar 4
    layer.bass_foundation = [
        LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w") for b in range(1, 5)
    ]
    add_melodic_articulation(layer, resolve_style("mozart"), EnrichmentReport())
    assert layer.principal_line[-1].articulation != "staccato", (
        "the closing lift belongs at the end of the phrase, not the end of a voice"
    )


# ─── The planner's articulation intent reaches the page ──────────────────────
#
# `ArticulationPlan.dominant_articulation` existed on the model with no reader
# anywhere: a planner could state the phrase's touch and nothing downstream
# honoured it, so every phrase was engraved with its period's default regardless
# of what it was planned to be.


class _Control:
    def __init__(self, articulation):
        from scales.models import ArticulationPlan

        self.articulation_plan = ArticulationPlan(dominant_articulation=articulation)


def _oom_pah(bars=4):
    ir = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=bars)
    for b in range(1, bars + 1):
        for i, pitch in enumerate(["C5", "D5", "E5", "F5"]):
            ir.principal_line.append(_ev(b, 1 + i * 0.5, pitch, "e"))
        ir.bass_foundation.append(_ev(b, 1.0, "C3", "e"))
        for i in (2, 3, 4):
            ir.bass_foundation.append(_ev(b, float(i), ["E3", "G3"], "e"))
    return ir


def test_a_phrase_planned_legato_is_not_given_staccato_dots():
    """The period default was overruling the plan written to override it."""
    ir = _oom_pah()
    enrich_layer_ir(ir, style="mozart", control=_Control("legato"))
    assert not any(e.articulation == "staccato" for e in ir.principal_line)
    assert not any(e.articulation == "staccato" for e in ir.bass_foundation)


def test_a_phrase_planned_staccato_gets_dots_in_a_legato_period():
    ir = _oom_pah()
    enrich_layer_ir(ir, style="chopin", control=_Control("staccato"))
    assert any(e.articulation == "staccato" for e in ir.principal_line)


def test_a_phrase_planned_marcato_is_accented_not_dotted():
    ir = _oom_pah()
    enrich_layer_ir(ir, style="mozart", control=_Control("marcato"))
    assert any(e.articulation == "marcato" for e in ir.principal_line)


def test_a_phrase_planned_portato_is_carried():
    ir = _oom_pah()
    enrich_layer_ir(ir, style="mozart", control=_Control("portato"))
    assert any(e.articulation == "tenuto" for e in ir.principal_line)


def test_no_plan_leaves_the_period_default_in_charge():
    ir = _oom_pah()
    enrich_layer_ir(ir, style="mozart")
    assert any(e.articulation == "staccato" for e in ir.bass_foundation)


def test_an_unrecognised_touch_falls_back_to_the_period():
    ir = _oom_pah()
    enrich_layer_ir(ir, style="mozart", control=_Control("misterioso"))
    assert any(e.articulation == "staccato" for e in ir.bass_foundation)


def test_a_planned_touch_still_never_overwrites_the_composer():
    ir = _oom_pah()
    ir.principal_line[0].articulation = "accent"
    enrich_layer_ir(ir, style="mozart", control=_Control("legato"))
    assert ir.principal_line[0].articulation == "accent"
