"""A whitelist of two spellings, against four the graphs actually carry.

`validator.validate_layer_ir` records this defect in a comment: the playability
check was written as `instrumentation in ("solo_piano", "piano")` while the
graphs on disk carry `solo_piano` (54 pieces), `piano` (2), `piano_solo` (2) and
`solo piano` (1). Two more copies of the same whitelist survived elsewhere, and
both fail silently — which is why neither was noticed:

- `expression_enricher._add_pedal` returned early, so three workspace pieces got
  NO pedal marks at all. A missing pedal looks exactly like a style that pedals
  sparingly.
- `scales._physical_constraints` set `keyboard=False`, which makes
  `validate_layer_ir` skip hand span and notes-per-hand — a STRICT physical
  constraint switched off by a space in a string.

`models.is_keyboard` normalizes spacing, hyphens and case, and is the one
decider. See [[feedback_a_missed_lookup_is_silent]].
"""

from __future__ import annotations

import pytest

from scales.expression_enricher import enrich_layer_ir
from scales.models import LayerEvent, LayerIR, is_keyboard

#: Every spelling a `contract.target.instrumentation` has actually held, plus the
#: free-text forms a planner writes.
PIANO_SPELLINGS = ("solo_piano", "piano", "piano_solo", "solo piano", "Solo-Piano")


def _romantic_phrase(instrumentation: str) -> LayerIR:
    layer = LayerIR(instrumentation=instrumentation, key="Eb", meter=(4, 4), bar_count=2)
    layer.principal_line = [
        LayerEvent(bar=bar, beat=float(i), pitch=p, duration=1.0, role="structural")
        for bar in (1, 2)
        for i, p in enumerate(["Eb5", "G5", "Bb5", "G5"])
    ]
    layer.bass_foundation = [
        LayerEvent(bar=bar, beat=0.0, pitch="Eb2", duration=4.0, role="structural")
        for bar in (1, 2)
    ]
    return layer


@pytest.mark.parametrize("spelling", PIANO_SPELLINGS)
def test_every_piano_spelling_gets_its_pedal(spelling):
    assert enrich_layer_ir(_romantic_phrase(spelling), style="romantic").pedal_marks_added > 0


@pytest.mark.parametrize("spelling", ("harpsichord", "organ", "clavichord", "celesta"))
def test_a_keyboard_without_a_sustain_pedal_gets_none(spelling):
    assert enrich_layer_ir(_romantic_phrase(spelling), style="romantic").pedal_marks_added == 0


@pytest.mark.parametrize("spelling", ("choir", "string quartet", "orchestra", "ensemble"))
def test_nothing_that_is_not_a_keyboard_gets_a_pedal(spelling):
    assert enrich_layer_ir(_romantic_phrase(spelling), style="romantic").pedal_marks_added == 0


@pytest.mark.parametrize("spelling", PIANO_SPELLINGS)
def test_every_piano_spelling_keeps_its_hand_span_check(spelling):
    """`keyboard=False` makes the validator skip playability entirely. A solo
    piano work written "solo piano" had no hand-span constraint at all."""
    assert is_keyboard(spelling), spelling


def test_the_constraints_a_piece_is_gated_by_follow_the_same_decider():
    from scales.models import PieceContract
    from scales.scales import _physical_constraints

    class _Graph:
        contract = PieceContract()

    for spelling in PIANO_SPELLINGS:
        _Graph.contract.target.instrumentation = spelling
        assert _physical_constraints(_Graph()).keyboard is True, spelling
    for spelling in ("choir", "string quartet", "orchestra"):
        _Graph.contract.target.instrumentation = spelling
        assert _physical_constraints(_Graph()).keyboard is False, spelling
