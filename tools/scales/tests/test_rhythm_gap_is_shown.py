"""The rest rate is the one the brief calls the clearest tell of a machine.

RHYTHMIC FINGERPRINT has always stated the composer's own figure — "43% of these
bars contain a REST. Music that never stops sounding is the single clearest tell
of a machine" — and never the piece's. Measured:

    chopin nocturne   20% of bars rest   against his 43%
    mozart andante    27%                against his 60%
    palestrina motet  28%                against his 29%   (already right)

The last line is why this is worth stating: the check has to be able to say
"you are fine", or it is a complaint that fires on everyone.

Dotted rhythm is deliberately NOT compared in compound metre. In 12/8 the beat
is itself a dotted quarter, so the nocturne reads 100% dotted against a corpus
figure drawn mostly from 3/4 mazurkas — a true number and a meaningless
comparison, which is worse than no number at all.
"""

from scales.composition_brief import _rest_and_dotted_so_far, render_rhythmic_fingerprint
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _graph(events, meter=(4, 4)) -> PieceGraph:
    layer = LayerIR(principal_line=events, bass_foundation=[], meter=meter, key="C major")
    g = PieceGraph()
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=2,
                        key="C major", meter=meter, tempo_bpm=90),
        realized=layer, agent_authored=True,
    )
    return g


def _ev(bar, pitch, duration="q"):
    return LayerEvent(bar=bar, beat=1.0, pitch=pitch, duration=duration, role="structural")


def test_a_bar_with_a_rest_is_counted_once():
    rest, _dotted, bars, _c = _rest_and_dotted_so_far(
        _graph([_ev(1, "C5"), _ev(1, "rest"), _ev(2, "D5")])
    )
    assert bars == 2
    assert abs(rest - 0.5) < 1e-9


def test_music_that_never_rests_measures_zero():
    rest, _d, _b, _c = _rest_and_dotted_so_far(_graph([_ev(1, "C5"), _ev(2, "D5")]))
    assert rest == 0.0


def test_dotted_durations_are_recognised():
    _r, dotted, _b, _c = _rest_and_dotted_so_far(_graph([_ev(1, "C5", "dq"), _ev(2, "D5", "q")]))
    assert abs(dotted - 0.5) < 1e-9


def test_compound_metre_suppresses_the_dotted_comparison():
    """12/8: the beat IS a dotted quarter, so the figure is structural."""
    _r, _d, _b, compound = _rest_and_dotted_so_far(_graph([_ev(1, "C5", "dq")], meter=(12, 8)))
    assert compound
    lines = " ".join(render_rhythmic_fingerprint("chopin", _graph([_ev(1, "C5", "dq")], (12, 8))))
    assert "not compared here" in lines
    assert "carry a dotted rhythm (his" not in lines


def test_simple_metre_still_compares_dotted():
    lines = " ".join(render_rhythmic_fingerprint("mozart", _graph([_ev(1, "C5", "dq")], (4, 4))))
    assert "carry a dotted rhythm (his" in lines


def test_an_empty_piece_reports_nothing():
    assert _rest_and_dotted_so_far(PieceGraph()) is None


def test_without_a_graph_the_section_is_unchanged():
    lines = " ".join(render_rhythmic_fingerprint("mozart"))
    assert "RHYTHMIC FINGERPRINT" in lines
    assert "BREATHING SO FAR" not in lines
