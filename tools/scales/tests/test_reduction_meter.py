"""A reduction must be in the source's own time signature.

`BimanualPacker.pack` built its LayerIR with no `meter`, so it took the
dataclass default of 4/4 whatever the orchestral source was in. Reducing a 3/4
section mis-barred every bar of it — 32 meter violations in one section — and the
reduction of a minuet came out in common time. The caller's only recourse was to
read the meter back off the exported file and repair it afterwards, which is
fixing downstream what should never have been wrong.

`reduce_to_piano` is one of six documented composition modes.
"""

import pytest

from scales.sabre import SABRE


def _events(bars=4, per_bar=3):
    return [
        {
            "instrument": "violin_1",
            "bar": b,
            "beat": 1.0 + i,
            "pitch": ["C5", "D5", "E5", "F5"][i % 4],
            "duration": "q",
        }
        for b in range(1, bars + 1)
        for i in range(per_bar)
    ]


@pytest.mark.parametrize("meter", [(4, 4), (3, 4), (6, 8), (2, 4), (12, 8), (3, 8)])
def test_the_reduction_keeps_the_sources_meter(meter):
    ir = SABRE().reduce_to_piano(_events(), ["violin_1"], key="C", meter=meter)
    assert tuple(ir.meter) == meter


def test_omitting_the_meter_still_works_for_older_callers():
    ir = SABRE().reduce_to_piano(_events(), ["violin_1"], key="C")
    assert tuple(ir.meter) == (4, 4)


def test_a_three_four_reduction_does_not_overfill_its_bars():
    """The symptom: three quarters in 3/4 is a full bar, not three quarters of one."""
    from scales.validator import validate_meter

    ir = SABRE().reduce_to_piano(_events(bars=4, per_bar=3), ["violin_1"], key="C", meter=(3, 4))
    events = (
        ir.principal_line + ir.bass_foundation + ir.response_layer + ir.counter_reply
    )
    issues = validate_meter(events, meter=tuple(ir.meter), bar_count=ir.bar_count)
    overfull = [i for i in issues if getattr(i, "severity", "") == "error"]
    assert not overfull, [getattr(i, "message", "") for i in overfull]

    # And the same material declared as 4/4 IS overfull at three quarters a bar
    # only if it claims four — the point being that the meter has to be the
    # source's, not a default.
    assert tuple(ir.meter) == (3, 4)


def test_the_key_is_carried_too():
    ir = SABRE().reduce_to_piano(_events(), ["violin_1"], key="Eb major", meter=(3, 4))
    assert ir.key == "Eb major"
