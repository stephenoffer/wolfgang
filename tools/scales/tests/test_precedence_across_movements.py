""""Earlier" is (movement, bar) — not bar alone.

Bar numbers RESTART per movement: a two-movement sonatina has two phrases at
bar 1 and two at bar 38. So `other.bar_start < slot.bar_start` is not "earlier"
in a multi-movement work. For a phrase at bar 20 of movement two it admits
movement one's bars 1-19 and rejects its bars 20-38 — an arbitrary slice of a
different movement, silently.

Two consumers had it, and they want opposite scopes:

  * `_cadences_already_used` drives "you have closed three phrases the same way".
    A cadence recurring in a LATER movement is not repetition, so this is scoped
    to the movement.
  * `_derive_continuation`'s motif history is deliberately WORK-wide — a theme
    stated in movement one and taken up in movement three is cyclic form, and
    the composer of movement three needs to know. That one needs real
    performance order, not a bar comparison.
"""

from scales.composition_brief import _phrases_before, _phrases_in_scope
from scales.models import MovementContract, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _graph():
    g = PieceGraph()

    class _Work:
        movements = [MovementContract(id="m1"), MovementContract(id="m2")]

    g.work_graph = _Work()
    for mid in ("m1", "m2"):
        for bar in (1, 20, 38):
            pid = f"{mid}_a_b{bar}"
            g.phrases[pid] = PhraseState(
                slot=PhraseSlot(phrase_id=pid, section_id=f"{mid}_a", bar_start=bar,
                                bar_count=4, key="C major", meter=(4, 4), tempo_bpm=90)
            )
    return g


def _ids(states):
    return sorted(s.slot.phrase_id for s in states)


def test_everything_in_an_earlier_movement_precedes_this_one():
    g = _graph()
    here = g.phrases["m2_a_b20"].slot
    before = _ids(_phrases_before(g, here))
    assert "m1_a_b38" in before, "a later bar of an EARLIER movement still comes first"
    assert "m1_a_b1" in before


def test_later_bars_of_this_movement_do_not_precede_it():
    g = _graph()
    before = _ids(_phrases_before(g, g.phrases["m2_a_b20"].slot))
    assert "m2_a_b38" not in before
    assert "m2_a_b1" in before


def test_the_first_phrase_of_the_work_has_nothing_before_it():
    g = _graph()
    assert _phrases_before(g, g.phrases["m1_a_b1"].slot) == []


def test_a_single_movement_piece_is_unaffected():
    g = PieceGraph()
    for bar in (1, 20):
        pid = f"m1_a_b{bar}"
        g.phrases[pid] = PhraseState(
            slot=PhraseSlot(phrase_id=pid, section_id="m1_a", bar_start=bar, bar_count=4,
                            key="C major", meter=(4, 4), tempo_bpm=90)
        )
    assert _ids(_phrases_before(g, g.phrases["m1_a_b20"].slot)) == ["m1_a_b1"]


def test_cadence_history_stays_inside_the_movement():
    """The other half: cadences are movement-scoped, because reusing a cadence
    in a later movement is not the defect the warning is about."""
    g = _graph()
    scoped = _ids(_phrases_in_scope(g, "m2_a"))
    assert all(pid.startswith("m2_") for pid in scoped)
