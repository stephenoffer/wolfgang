"""A phrase that was never composed was counted as one the engine wrote.

`_authoring_summary` split phrases two ways:

    if getattr(st, "agent_authored", False): authored += 1
    else:                                    engine   += 1

so a phrase with `status="planned"` and **zero events** landed in
`engine_realized`. A real workspace piece with 3 of 9 phrases composed reported

    {"phrases": 9, "agent_authored": 3, "engine_realized": 6}

which reads as a finished piece realized by two different paths. `warnings` was
`[]`. The assembled score was simply shorter, with nothing anywhere saying why,
and every metric in the report — density, cadences, realism, the ear — described
one third of the intended piece as though it were the whole.
"""

from __future__ import annotations

from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph
from scales.scales import _authoring_summary


def _slot(pid: str) -> PhraseSlot:
    return PhraseSlot(
        phrase_id=pid, section_id="m1_a", bar_start=1, bar_count=2,
        key="C major", meter=(4, 4), tempo_bpm=90,
    )


def _notes() -> LayerIR:
    return LayerIR(
        principal_line=[
            LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural")
        ],
        meter=(4, 4),
        key="C major",
    )


def _graph() -> PieceGraph:
    graph = PieceGraph()
    graph.phrases["agent"] = PhraseState(
        slot=_slot("agent"), realized=_notes(), agent_authored=True, status="realized"
    )
    graph.phrases["engine"] = PhraseState(
        slot=_slot("engine"), realized=_notes(), agent_authored=False, status="realized"
    )
    graph.phrases["never"] = PhraseState(
        slot=_slot("never"), realized=LayerIR(meter=(4, 4), key="C major"), status="planned"
    )
    graph.phrases["also_never"] = PhraseState(slot=_slot("also_never"), status="planned")
    return graph


def test_an_empty_phrase_is_not_engine_realized():
    got = _authoring_summary(_graph(), None)
    assert got["agent_authored"] == 1
    assert got["engine_realized"] == 1
    assert got["unrealized"] == 2


def test_the_unrealized_phrases_are_named():
    got = _authoring_summary(_graph(), None)
    assert set(got["unrealized_phrases"]) == {"never", "also_never"}


def test_a_phrase_the_engine_really_did_realize_still_counts():
    """The fix must not turn engine work into "unrealized" — that would hide the
    engine fallback the same way the old code hid missing phrases."""
    got = _authoring_summary(_graph(), None)
    assert got["engine_realized"] == 1


def test_a_complete_piece_reports_nothing_unrealized():
    graph = PieceGraph()
    graph.phrases["a"] = PhraseState(
        slot=_slot("a"), realized=_notes(), agent_authored=True, status="realized"
    )
    got = _authoring_summary(graph, None)
    assert got["unrealized"] == 0
    assert got["unrealized_phrases"] == []


def test_notes_in_any_layer_count_as_realized():
    """A phrase can be written entirely into inner voices or the bass."""
    graph = PieceGraph()
    graph.phrases["bass_only"] = PhraseState(
        slot=_slot("bass_only"),
        realized=LayerIR(
            bass_foundation=[
                LayerEvent(bar=1, beat=1.0, pitch="C3", duration="w", role="structural")
            ],
            meter=(4, 4),
            key="C major",
        ),
        status="realized",
    )
    assert _authoring_summary(graph, None)["unrealized"] == 0
