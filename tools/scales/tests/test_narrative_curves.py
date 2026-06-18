"""Tests for narrative-arc -> slot-curve wiring (_apply_narrative_curves).

The planned NarrativeArc must reach per-bar PhraseCurves so dynamics, density,
and the tempo arc actually follow the emotional story rather than hardcoded
function defaults.

Run: python3 -m scales.tests.test_narrative_curves
"""

from scales import scales
from scales.models import NarrativeArc, NarrativeSection, PhraseCurves, PhraseSlot


def _slot(bar_start, bar_count):
    return PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=bar_start,
        bar_count=bar_count,
        key="C",
        meter=[4, 4],
        curves=PhraseCurves(energy=[0.5] * bar_count),
    )


def test_no_narrative_keeps_default():
    s = _slot(1, 4)
    applied = scales._apply_narrative_curves(s, None)
    assert applied is False
    assert s.curves.energy == [0.5, 0.5, 0.5, 0.5]
    assert s.curves.tension == []


def test_curves_interpolated_from_section():
    arc = NarrativeArc(
        sections=[
            NarrativeSection(
                id="rise",
                bar_start=1,
                bar_end=8,
                energy_curve=[0.2, 1.0],  # rising
                tension_curve=[0.0, 1.0],
                density_curve=[0.3, 0.9],
                brightness_curve=[0.5, 0.5],
            )
        ]
    )
    s = _slot(1, 8)
    applied = scales._apply_narrative_curves(s, arc)
    assert applied is True
    # energy must rise monotonically across the 8 bars
    assert s.curves.energy[0] < s.curves.energy[-1]
    assert s.curves.energy == sorted(s.curves.energy)
    assert abs(s.curves.energy[0] - 0.2) < 1e-6
    assert abs(s.curves.energy[-1] - 1.0) < 1e-6
    # tension/density/brightness now populated (were empty before)
    assert len(s.curves.tension) == 8
    assert len(s.curves.density) == 8
    assert abs(s.curves.brightness[0] - 0.5) < 1e-6


def test_slot_in_second_section_samples_that_section():
    arc = NarrativeArc(
        sections=[
            NarrativeSection(id="a", bar_start=1, bar_end=8, energy_curve=[0.3, 0.4]),
            NarrativeSection(
                id="climax", bar_start=9, bar_end=16, energy_curve=[0.9, 1.0], climax_type="primary"
            ),
        ]
    )
    s = _slot(9, 8)  # lives entirely in the climax section
    scales._apply_narrative_curves(s, arc)
    assert all(v >= 0.85 for v in s.curves.energy), s.curves.energy


def test_uncovered_bars_fall_back():
    arc = NarrativeArc(
        sections=[NarrativeSection(id="a", bar_start=1, bar_end=4, energy_curve=[0.2, 0.8])]
    )
    s = _slot(1, 8)  # bars 5-8 are uncovered
    scales._apply_narrative_curves(s, arc)
    assert len(s.curves.energy) == 8
    # uncovered tail keeps the prior default (0.5)
    assert s.curves.energy[5] == 0.5


if __name__ == "__main__":
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in fns:
        fn()
        print(f"ok {name}")
    print(f"\n{len(fns)} tests passed")
