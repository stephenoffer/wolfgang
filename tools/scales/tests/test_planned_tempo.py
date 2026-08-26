"""Planned performance directives have to actually happen.

Four declared fields shaped nothing before this:
``RhythmPlan.accelerando_bars`` / ``.ritardando_bars``, and
``PerformanceIntentProfile.rubato_contexts`` / ``.pedal_rules`` /
``.voicing_priorities`` — which map exactly onto the three things the
performance renderer produces and were read by no code at all.

``RhythmPlan.accelerando_bars`` and ``.ritardando_bars`` existed on the model
with **no reader anywhere in the codebase**. A planner could name a stretch of
bars to push through or to broaden, and nothing would happen — so the only tempo
shaping any generated piece has ever had is the automatic broadening of a
cadence bar, and a deliberate accelerando into a climax was inexpressible.

The same vestigial-field pattern as the ExpectationLedger and the craft
checklist: declared, documented, never read.
"""

import pytest

from scales.models import LayerEvent, LayerIR, PhraseSlot, RhythmPlan
from scales.performance_renderer import build_performance_ir, tempo_factor_at


class _Control:
    def __init__(self, **kw):
        self.rhythm_plan = RhythmPlan(**kw)


def _phrase(bars=8):
    ir = LayerIR(key="C", meter=(4, 4))
    for b in range(1, bars + 1):
        ir.principal_line.append(LayerEvent(bar=b, beat=1.0, pitch="C5", duration="w"))
        ir.bass_foundation.append(LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w"))
    return ir, PhraseSlot(phrase_id="p", bar_start=1, bar_count=bars, key="C", meter=(4, 4))


def _factors(perf, bars=8):
    return [round(tempo_factor_at(perf, b, 1.0, 4.0), 4) for b in range(1, bars + 1)]


def test_with_no_plan_the_tempo_is_steady():
    ir, slot = _phrase()
    assert _factors(build_performance_ir(ir, slot)) == [1.0] * 8


def test_a_planned_accelerando_speeds_up_across_its_bars():
    ir, slot = _phrase()
    f = _factors(build_performance_ir(ir, slot, control=_Control(accelerando_bars=(3, 6))))
    assert f[2] < f[3] < f[4] < f[5], f
    assert f[5] > 1.0, "the accelerando never got faster"


def test_a_planned_ritardando_slows_down_across_its_bars():
    ir, slot = _phrase()
    f = _factors(build_performance_ir(ir, slot, control=_Control(ritardando_bars=(5, 8))))
    assert f[4] > f[5] > f[6] > f[7], f
    assert f[7] < 1.0, "the ritardando never got slower"


def test_the_change_ramps_rather_than_stepping():
    """A tempo change that arrives all at once is a tempo MARK, not a rit."""
    ir, slot = _phrase()
    f = _factors(build_performance_ir(ir, slot, control=_Control(ritardando_bars=(1, 8))))
    steps = [abs(b - a) for a, b in zip(f, f[1:])]
    assert max(steps) < 0.1, f"stepped rather than ramped: {f}"


def test_bars_outside_the_span_are_untouched():
    ir, slot = _phrase()
    f = _factors(build_performance_ir(ir, slot, control=_Control(accelerando_bars=(4, 6))))
    assert f[0] == f[1] == f[2] == 1.0
    assert f[6] == f[7] == 1.0


def test_a_span_of_one_bar_is_ignored():
    """One bar cannot ramp; asking for it should not divide by zero."""
    ir, slot = _phrase()
    f = _factors(build_performance_ir(ir, slot, control=_Control(accelerando_bars=(3, 3))))
    assert f == [1.0] * 8


def test_a_span_outside_the_phrase_is_clipped_not_crashed():
    ir, slot = _phrase()
    perf = build_performance_ir(ir, slot, control=_Control(ritardando_bars=(20, 40)))
    assert _factors(perf) == [1.0] * 8


def test_a_malformed_span_is_ignored():
    ir, slot = _phrase()
    for bad in ((None, None), ("a", "b"), (3,)):
        control = _Control()
        control.rhythm_plan.accelerando_bars = bad
        assert _factors(build_performance_ir(ir, slot, control=control)) == [1.0] * 8


def test_the_plan_can_also_be_read_off_the_slot():
    ir, slot = _phrase()
    slot.rhythm_plan = RhythmPlan(accelerando_bars=(2, 5))
    f = _factors(build_performance_ir(ir, slot))
    assert f[4] > 1.0


@pytest.mark.parametrize("period", ["baroque", "classical", "romantic"])
def test_every_period_shapes_the_change_by_its_own_rubato_depth(period):
    from scales.performance_params import profile_for_period

    ir, slot = _phrase()
    perf = build_performance_ir(
        ir, slot, profile=profile_for_period(period), control=_Control(ritardando_bars=(5, 8))
    )
    assert _factors(perf)[7] < 1.0


# ─── The plan's performance intent ───────────────────────────────────────────


class _Intent:
    def __init__(self, **kw):
        from scales.models import PerformanceIntentProfile

        self.performance_intent = PerformanceIntentProfile(**kw)


def _cadential_slot(bars=4):
    ir, slot = _phrase(bars)
    slot.cadence_target = "PAC"
    return ir, slot


def test_a_plan_asking_for_no_pedal_gets_none():
    from scales.performance_renderer import pedal_bars

    ir, slot = _cadential_slot()
    assert pedal_bars(build_performance_ir(ir, slot)), "the default pedals"
    dry = build_performance_ir(ir, slot, control=_Intent(pedal_rules=[{"style": "dry"}]))
    assert pedal_bars(dry) == []


def test_a_pedal_rule_is_read_from_several_spellings():
    from scales.models import PerformanceIntentProfile
    from scales.performance_renderer import pedal_style_from_intent

    for spelling, expected in (
        ("by_harmony", "harmonic"),
        ("legato", "long"),
        ("light", "sparing"),
        ("senza", "none"),
    ):
        intent = PerformanceIntentProfile(pedal_rules=[{"style": spelling}])
        assert pedal_style_from_intent(intent) == expected


def test_an_unrecognised_pedal_rule_leaves_the_period_default():
    from scales.performance_renderer import pedal_bars

    ir, slot = _cadential_slot()
    odd = build_performance_ir(ir, slot, control=_Intent(pedal_rules=[{"style": "shimmer"}]))
    assert pedal_bars(odd) == pedal_bars(build_performance_ir(ir, slot))


def test_the_plan_decides_which_voice_is_brought_out():
    """The default emphasised "melody" in every bar, always."""
    ir, slot = _phrase()
    default = build_performance_ir(ir, slot)
    assert {v.voice for v in default.voicing_emphasis} == {"melody"}

    bassy = build_performance_ir(ir, slot, control=_Intent(voicing_priorities=["bass"]))
    assert "bass" in {v.voice for v in bassy.voicing_emphasis}


def test_a_named_voice_outranks_the_ones_after_it():
    ir, slot = _phrase()
    perf = build_performance_ir(
        ir, slot, control=_Intent(voicing_priorities=["bass", "melody"])
    )
    boosts = {v.voice: v.boost for v in perf.voicing_emphasis}
    assert boosts["bass"] > boosts["melody"]


def test_a_climax_context_pushes_forward_rather_than_broadening():
    ir, slot = _cadential_slot()
    perf = build_performance_ir(
        ir, slot, phrase_type="climax", control=_Intent(rubato_contexts=["climax"])
    )
    assert _factors(perf, 4)[-1] > 1.0


def test_a_cadence_context_broadens():
    ir, slot = _cadential_slot()
    perf = build_performance_ir(ir, slot, control=_Intent(rubato_contexts=["cadence"]))
    assert _factors(perf, 4)[-1] < 1.0


def test_a_context_that_does_not_apply_here_changes_nothing():
    ir, slot = _phrase()
    perf = build_performance_ir(ir, slot, control=_Intent(rubato_contexts=["recitative"]))
    assert _factors(perf) == [1.0] * 8


def test_no_intent_leaves_the_period_in_charge():
    ir, slot = _cadential_slot()
    plain = _factors(build_performance_ir(ir, slot), 4)
    empty = _factors(build_performance_ir(ir, slot, control=_Intent()), 4)
    assert plain == empty


def test_the_intent_can_come_from_a_style_program():
    from scales.models import PerformanceIntentProfile

    class _Program:
        performance_intents = PerformanceIntentProfile(voicing_priorities=["bass"])

    ir, slot = _phrase()
    perf = build_performance_ir(ir, slot, style_program=_Program())
    assert "bass" in {v.voice for v in perf.voicing_emphasis}


def test_a_dict_shaped_intent_is_read_too():
    ir, slot = _phrase()

    class _DictIntent:
        performance_intent = {"voicing_priorities": ["bass"]}

    perf = build_performance_ir(ir, slot, control=_DictIntent())
    assert "bass" in {v.voice for v in perf.voicing_emphasis}
