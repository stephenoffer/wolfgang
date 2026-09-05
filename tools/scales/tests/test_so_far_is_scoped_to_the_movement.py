""""So far" must mean this movement, not this folder.

Four sections of the brief report what the composer has written up to now —
MARKS, RANGE, BREATHING, THICKNESS. All of them iterated **every phrase in the
graph**, so in a multi-movement work the slow movement was shown the opening
allegro's articulation counts, rest rate and texture thickness as though they
were its own.

Two movements have genuinely different habits: a fast movement rests less and
articulates more, and averaging them describes neither. This is the same mistake
as telling three movements each that they hold the climax of the whole piece
(Addendum 65), one measurement layer down — and it was in code added earlier in
this same session, which is the part worth remembering.

Single-movement pieces are unaffected: every phrase is in scope, as before.
"""

from scales.composition_brief import _phrases_in_scope, marks_so_far
from scales.models import LayerEvent, LayerIR, MovementContract, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _graph(multi: bool) -> PieceGraph:
    g = PieceGraph()
    if multi:
        class _Work:
            movements = [MovementContract(id="m1"), MovementContract(id="m2")]

        g.work_graph = _Work()
    for mid, artic in (("m1", "staccato"), ("m2", None)):
        ev = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural",
                        articulation=artic)
        g.phrases[f"{mid}_a_p1"] = PhraseState(
            slot=PhraseSlot(phrase_id=f"{mid}_a_p1", section_id=f"{mid}_a", bar_start=1,
                            bar_count=4, key="C major", meter=(4, 4), tempo_bpm=90),
            realized=LayerIR(principal_line=[ev], bass_foundation=[], meter=(4, 4), key="C major"),
            agent_authored=True,
        )
    return g


def test_a_movement_sees_only_its_own_phrases():
    scoped = _phrases_in_scope(_graph(multi=True), "m2_a_p1")
    assert len(scoped) == 1
    assert scoped[0].slot.section_id == "m2_a"


def test_one_movements_marks_do_not_leak_into_another():
    graph = _graph(multi=True)
    assert marks_so_far(graph, "m1_a_p1")["articulation"] == 1
    assert marks_so_far(graph, "m2_a_p1")["articulation"] == 0


def test_a_single_movement_piece_counts_everything():
    """Falsification: scoping must not narrow an ordinary piece."""
    graph = _graph(multi=False)
    assert len(_phrases_in_scope(graph, "m1_a_p1")) == 2
    assert marks_so_far(graph, "m1_a_p1")["articulation"] == 1


def test_no_movement_id_counts_everything():
    graph = _graph(multi=True)
    assert len(_phrases_in_scope(graph, "")) == 2


def test_an_unknown_movement_falls_back_rather_than_reporting_nothing():
    """A phrase id that matches no movement must not silently produce an empty
    'so far' — that would read as "you have written nothing"."""
    graph = _graph(multi=True)
    assert len(_phrases_in_scope(graph, "m9_a_p1")) == 2


def test_the_register_report_is_scoped_too():
    """RANGE SO FAR was the fourth of the four "so far" sections and the one I
    named but did not fix in the same pass. A slow movement judged against the
    allegro's register has both the wrong ceiling and the wrong floor."""
    from scales.composition_brief import _register_target

    graph = PieceGraph()

    class _Work:
        movements = [MovementContract(id="m1"), MovementContract(id="m2")]

    graph.work_graph = _Work()
    wide = [
        LayerEvent(bar=1, beat=float(i + 1), pitch=p, duration="q", role="structural")
        for i, p in enumerate(["G3", "G6"])
    ]
    graph.phrases["m1_a_p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="m1_a_p1", section_id="m1_a", bar_start=1, bar_count=4,
                        key="G major", meter=(4, 4), tempo_bpm=132),
        realized=LayerIR(principal_line=wide, bass_foundation=[], meter=(4, 4), key="G major"),
        agent_authored=True,
    )
    m2_slot = PhraseSlot(phrase_id="m2_a_p1", section_id="m2_a", bar_start=1, bar_count=4,
                         key="C major", meter=(3, 4), tempo_bpm=60)
    graph.phrases["m2_a_p1"] = PhraseState(slot=m2_slot)

    # m1 sees its own three-octave span; m2 has written nothing and must not
    # inherit it.
    m1_slot = graph.phrases["m1_a_p1"].slot
    assert any("G3" in ln for ln in _register_target(graph, m1_slot))
    assert not [ln for ln in _register_target(graph, m2_slot) if "RANGE SO FAR" in ln]
