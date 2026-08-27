"""A breath is the player cutting a note short, not a rest laid over one.

`_apply_breathing` read each rule only for whether its `placement` string
contained the substring "before", and every rule of the same category then
computed the SAME (bar, beat) — so three rules produced three rests stacked on
one instant. It appended them on top of whatever was sounding there, where the
surface repair correctly deletes a rest that collides with a note: the pass fed
its own output to a repair that undid it.

It also never read `duration_beats_min` / `duration_beats_max`. A rule whose
technique is "Grand pause (G.P.) after dominant chord", asking for one to four
beats of silence, produced an eighth rest.
"""

from __future__ import annotations

from dataclasses import dataclass

from scales.duration import dur_to_beats
from scales.models import PhraseControlIR
from scales.surface_composer import OnsetBundle, OnsetEvent, SurfaceComposer


@dataclass
class _Rule:
    type: str = "anticipatory"
    placement: str = "before_climax_or_return"
    duration_beats_min: float = 1.0
    duration_beats_max: float = 4.0


class _Trace:
    def __init__(self):
        self.breathing_rules_applied = []


def _control():
    return PhraseControlIR(
        phrase_id="p", section_id="s", bars=4, bar_start=1, meter=(4, 4), cadence_bar=4
    )


def _melody(bar, beat, dur):
    b = OnsetBundle(bar=bar, beat=beat)
    b.events.append(OnsetEvent(voice="soprano", pitch="C5", duration=dur))
    return b


def _breaths(bundles):
    return [(b.bar, b.beat, e.duration) for b in bundles for e in b.events if e.pitch == "rest"]


def test_three_rules_do_not_stack_three_rests_on_one_instant():
    bundles = [_melody(3, 1.0, "w")]
    SurfaceComposer._apply_breathing(
        None, bundles, [_Rule(), _Rule(), _Rule()], _control(), _Trace()
    )
    breaths = _breaths(bundles)
    assert len(breaths) == len({(bar, beat) for bar, beat, _ in breaths}), breaths
    assert len(breaths) <= 1, breaths


def test_the_breath_takes_its_length_from_the_rule_not_a_fixed_eighth():
    bundles = [_melody(3, 1.0, "w")]
    SurfaceComposer._apply_breathing(
        None, bundles, [_Rule(duration_beats_min=1.0)], _control(), _Trace()
    )
    breaths = _breaths(bundles)
    assert breaths, "no breath inserted"
    assert dur_to_beats(breaths[0][2]) >= 1.0, breaths


def test_the_note_is_shortened_so_the_breath_has_somewhere_to_go():
    """The whole point: a breath is room made, not an event overlaid."""
    bundles = [_melody(3, 1.0, "w")]
    SurfaceComposer._apply_breathing(None, bundles, [_Rule()], _control(), _Trace())
    breaths = _breaths(bundles)
    assert breaths, "no breath inserted"
    bar, beat, _ = breaths[0]
    note = bundles[0].events[0]
    assert bundles[0].beat + dur_to_beats(note.duration) <= beat + 1e-9, (
        f"the melody still runs through the breath: note ends at "
        f"{bundles[0].beat + dur_to_beats(note.duration)}, breath at {beat}"
    )


def test_a_breath_is_not_carved_out_of_an_eighth_note():
    """A beat is the floor.

    Cutting an eighth to breathe leaves a sixteenth note and a sixteenth rest —
    a rhythmic artifact, not a breath. You cut a long note to take air.
    """
    bundles = [_melody(3, 3.5, "e")]
    SurfaceComposer._apply_breathing(None, bundles, [_Rule()], _control(), _Trace())
    assert not _breaths(bundles), _breaths(bundles)


def test_different_placements_do_not_all_collapse_to_one_spot():
    """The defect, stated directly.

    Every rule was read only for whether its placement contained "before", so a
    contemplative breath between sections and an anticipatory one before the
    climax landed on the same instant. Two placements CAN legitimately coincide
    — `after_climax` has nowhere to go when the climax is the last bar — so what
    is asserted is that they do not all collapse.
    """
    where = {}
    for placement, rtype in (
        ("between_sections", "contemplative"),
        ("after_climax", "aftermath"),
        ("before_climax_or_return", "anticipatory"),
    ):
        bundles = [_melody(bar, 1.0, "w") for bar in (1, 2, 3, 4)]
        SurfaceComposer._apply_breathing(
            None, bundles, [_Rule(type=rtype, placement=placement)], _control(), _Trace()
        )
        where[placement] = _breaths(bundles)
    assert where["before_climax_or_return"] != where["between_sections"], where
    assert all(where.values()), f"a placement produced no breath at all: {where}"
