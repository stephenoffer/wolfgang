"""A phrase's close should depend on what kind of close it is.

Every phrase ending this engine wrote had the identical rhythm — a quarter then
an eighth — for a perfect authentic cadence, a half cadence, an evaded one and a
plagal Amen alike. Seven of nine endings in one piece, against a real Mozart
figure of a third to a half. The cadence TYPE was planned, stored on the slot,
and never reached the rhythm.
"""

from scales.duration import dur_to_beats
from scales.models import LayerEvent, LayerIR
from scales.surface_composer import _shape_the_cadence


def _phrase(meter=(3, 8), last_bar=4):
    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="D minor", meter=meter, bar_count=4
    )
    layer.principal_line = [
        LayerEvent(bar=last_bar, beat=1.0, pitch="F5", duration="q", role="structural"),
        LayerEvent(bar=last_bar, beat=2.0, pitch="D5", duration="e", role="structural"),
    ]
    return layer


def _sig(layer, bar):
    return tuple(
        e.duration for e in sorted(layer.principal_line, key=lambda e: float(e.beat))
        if e.bar == bar
    )


def test_a_perfect_authentic_cadence_is_a_full_stop():
    """The cadence pitch arrives on the downbeat and holds the bar."""
    layer = _phrase()
    assert _shape_the_cadence(layer, (3, 8), "PAC", 4) is True
    remaining = [e for e in layer.principal_line if e.bar == 4]
    assert len(remaining) == 1
    assert remaining[0].beat == 1.0
    assert remaining[0].pitch == "D5", "the CADENCE pitch must survive, not the approach"
    assert float(dur_to_beats(remaining[0].duration)) == 1.5


def test_a_half_cadence_breathes_instead():
    """A comma, not a full stop — the note shortens so a rest opens after it."""
    layer = _phrase()
    before = float(dur_to_beats(layer.principal_line[-1].duration))
    assert _shape_the_cadence(layer, (3, 8), "HC", 4) is True
    after = float(dur_to_beats(layer.principal_line[-1].duration))
    assert after < before
    assert len([e for e in layer.principal_line if e.bar == 4]) == 2


def test_an_evaded_cadence_is_left_alone():
    """It is not stopping. That is the whole point of an evaded cadence."""
    layer = _phrase()
    before = _sig(layer, 4)
    assert _shape_the_cadence(layer, (3, 8), "evaded", 4) is False
    assert _sig(layer, 4) == before


def test_an_unknown_cadence_name_carries_on_rather_than_guessing():
    layer = _phrase()
    before = _sig(layer, 4)
    assert _shape_the_cadence(layer, (3, 8), "something_new", 4) is False
    assert _sig(layer, 4) == before


def test_the_closes_are_actually_different_from_each_other():
    """The point is variety: if every type produced the same rhythm the
    detector would be right to keep firing."""
    sigs = set()
    for cadence in ("PAC", "HC", "evaded", "plagal", "IAC"):
        layer = _phrase()
        _shape_the_cadence(layer, (3, 8), cadence, 4)
        sigs.add(_sig(layer, 4))
    assert len(sigs) >= 3, f"only {len(sigs)} distinct closes: {sigs}"


def test_a_full_stop_never_overfills_the_bar():
    for meter in ((3, 8), (4, 4), (6, 8), (2, 4), (12, 8), (7, 8)):
        layer = _phrase(meter=meter)
        _shape_the_cadence(layer, meter, "PAC", 4)
        from scales.duration import bar_duration

        cap = float(bar_duration(meter))
        for e in layer.principal_line:
            end = float(e.beat) - 1 + float(dur_to_beats(e.duration))
            assert end <= cap + 1e-9, f"{meter}: ends at {end} of {cap}"


def test_a_tied_note_is_not_reshaped():
    """`_hold_over_barline` binds a note to the next bar; rewriting it
    underneath would leave a tie joining two different lengths."""
    layer = _phrase()
    for e in layer.principal_line:
        e.tie = "start"
    before = _sig(layer, 4)
    assert _shape_the_cadence(layer, (3, 8), "PAC", 4) is False
    assert _sig(layer, 4) == before


def test_a_single_note_bar_is_not_stripped_to_nothing():
    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="D minor", meter=(3, 8), bar_count=4
    )
    layer.principal_line = [
        LayerEvent(bar=4, beat=1.0, pitch="D5", duration="e", role="structural")
    ]
    _shape_the_cadence(layer, (3, 8), "PAC", 4)
    assert len(layer.principal_line) == 1


# ─── the bass closes too ─────────────────────────────────────────────────────


def _with_bass(meter=(3, 4), last_bar=4):
    layer = _phrase(meter=meter, last_bar=last_bar)
    layer.bass_foundation = [
        LayerEvent(bar=last_bar, beat=1.0, pitch="D3", duration="q", role="bass_foundation"),
        LayerEvent(bar=last_bar, beat=2.0, pitch="A2", duration="q", role="bass_foundation"),
        LayerEvent(bar=last_bar, beat=3.0, pitch="D3", duration="q", role="bass_foundation"),
    ]
    return layer


def test_a_full_stop_rests_the_bass_as_well():
    """Shaping only the melody left the accompaniment playing the same figure at
    every phrase end — 78% reuse on the left-hand staff against a real p90 of
    76%, while the melody was already inside its range at 44%. The two staves
    are measured separately."""
    layer = _with_bass()
    assert _shape_the_cadence(layer, (3, 4), "PAC", 4) is True
    bass = [e for e in layer.bass_foundation if e.bar == 4]
    assert len(bass) == 1
    assert bass[0].beat == 1.0
    assert float(dur_to_beats(bass[0].duration)) == 3.0


def test_a_half_cadence_shortens_the_bass_without_removing_it():
    layer = _with_bass()
    before = len([e for e in layer.bass_foundation if e.bar == 4])
    assert _shape_the_cadence(layer, (3, 4), "HC", 4) is True
    after = [e for e in layer.bass_foundation if e.bar == 4]
    assert len(after) == before
    assert float(dur_to_beats(after[-1].duration)) < 1.0


def test_an_evaded_cadence_leaves_the_bass_alone_too():
    layer = _with_bass()
    before = [(e.beat, e.duration) for e in layer.bass_foundation]
    assert _shape_the_cadence(layer, (3, 4), "evaded", 4) is False
    assert [(e.beat, e.duration) for e in layer.bass_foundation] == before


def test_a_full_stop_keeps_a_chord_that_is_already_there():
    """The thickening may have put a chord on the final bass note, and a full
    stop is the last place to thin one out."""
    layer = _with_bass()
    layer.bass_foundation.append(
        LayerEvent(bar=4, beat=3.0, pitch="A3", duration="q", role="bass_foundation")
    )
    _shape_the_cadence(layer, (3, 4), "PAC", 4)
    final = [e for e in layer.bass_foundation if e.bar == 4]
    assert len(final) == 2, f"the chord was thinned to {[e.pitch for e in final]}"
    assert {e.pitch for e in final} == {"D3", "A3"}


def test_the_bass_close_never_overfills_the_bar():
    from scales.duration import bar_duration

    for meter in ((3, 4), (4, 4), (6, 8), (2, 4), (12, 8)):
        layer = _with_bass(meter=meter)
        _shape_the_cadence(layer, meter, "PAC", 4)
        cap = float(bar_duration(meter))
        for e in layer.bass_foundation:
            assert float(e.beat) - 1 + float(dur_to_beats(e.duration)) <= cap + 1e-9
