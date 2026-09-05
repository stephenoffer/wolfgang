"""A tie must not swallow the marks that describe a MOMENT.

`_resolve_ties` cleared every field in `_ATTACK_FIELDS` on the far side of a tie,
with the reasoning that "the far side of a tie is not a new attack". True of
articulation and ornament — you do not re-articulate a tied note. False of a
dynamic, a text expression and a pedal change, which mark a point in time that
happens whether or not a note is struck there: "mp" on the far side of a tie
means "from here, mp".

The B-flat andante has two phrases that elide into the next bar over a tie, and
BOTH of their opening dynamics — bar 9 mp, bar 32 p — vanished between the
LayerIR and the score. Silently, and at exactly the places a composer puts them.
"""

from scales.assembler import _REARTICULATION_FIELDS, _resolve_cross_phrase_ties
from scales.models import EventIR


def _pair(**kw):
    a = EventIR(bar=1, beat=2.0, pitch="G5", duration="q", staff="treble", tie="start")
    b = EventIR(bar=2, beat=1.0, pitch="G5", duration="q", staff="treble", **kw)
    return [a, b]


def test_a_dynamic_survives_the_far_side_of_a_tie():
    evs = _pair(dynamic="mp")
    _resolve_cross_phrase_ties(evs)
    assert evs[1].tie == "stop"
    assert evs[1].dynamic == "mp"


def test_an_expression_and_a_pedal_survive():
    evs = _pair(expression="a tempo", pedal="start")
    _resolve_cross_phrase_ties(evs)
    assert evs[1].expression == "a tempo"
    assert evs[1].pedal == "start"


def test_re_articulation_marks_are_still_dropped():
    """These describe how a note is STRUCK; a tied note is not struck again."""
    evs = _pair(articulation="staccato", ornament="tr")
    _resolve_cross_phrase_ties(evs)
    assert evs[1].articulation is None
    assert evs[1].ornament is None


def test_the_two_field_sets_are_distinct_and_correct():
    from scales.assembler import _ATTACK_FIELDS

    assert set(_REARTICULATION_FIELDS) < set(_ATTACK_FIELDS)
    for f in ("dynamic", "expression", "pedal"):
        assert f not in _REARTICULATION_FIELDS, f


def test_the_tie_itself_is_still_formed():
    evs = _pair(dynamic="mp")
    _resolve_cross_phrase_ties(evs)
    assert evs[0].tie == "start" and evs[1].tie == "stop"


def test_a_pitch_mismatch_still_breaks_the_tie():
    a = EventIR(bar=1, beat=2.0, pitch="G5", duration="q", staff="treble", tie="start")
    b = EventIR(bar=2, beat=1.0, pitch="A5", duration="q", staff="treble", dynamic="mp")
    _resolve_cross_phrase_ties([a, b])
    assert a.tie is None
    assert b.dynamic == "mp"
