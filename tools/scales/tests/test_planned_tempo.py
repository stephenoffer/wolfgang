"""A planned accelerando or ritardando has to actually happen.

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
