"""An appoggiatura and an acciaccatura must not sound the same.

`ornament_realization.py` was written because ornaments were engraved and then
silent, and its docstring names the appoggiatura/acciaccatura confusion as the
case it fixes. It did not fix it: the realizer needs the small note AND the note
it leans on, `midi_renderer` handed it only one event, and `realize()` returns
``[]`` for both ornaments without a `grace_midi`. So both kept falling through to
a plain short note on the beat — the exact bug, still there, underneath a comment
saying it was gone.

These tests pin the pair, not the plumbing.
"""

from fractions import Fraction

from scales.duration import dur_to_beats
from scales.midi_renderer import _pair_graces
from scales.models import LayerEvent
from scales.ornament_realization import realize


def _pair(ornament: str, grace: str = "D5", principal: str = "C5", dur: str = "q"):
    g = LayerEvent(bar=1, beat=1.0, pitch=grace, duration="s", role="ornamental", ornament=ornament)
    p = LayerEvent(bar=1, beat=1.0, pitch=principal, duration=dur, role="structural")
    pairs, consumed = _pair_graces([g, p])
    assert id(g) in consumed, "the grace must not also sound as a plain note"
    gm, orn = pairs[id(p)]
    return realize(
        orn, 72, dur_to_beats(dur), key="C major", tempo_bpm=90, grace_midi=gm, period="classical"
    )


def test_both_grace_ornaments_are_audible_at_all():
    assert _pair("appoggiatura")
    assert _pair("acciaccatura")


def test_they_do_not_sound_identical():
    def shape(ns):
        return [(n.offset_beats, n.duration_beats, n.midi) for n in ns]

    assert shape(_pair("appoggiatura")) != shape(_pair("acciaccatura"))


def test_an_appoggiatura_leans_on_the_beat_and_takes_half_the_principal():
    lean, principal = _pair("appoggiatura")
    assert lean.offset_beats == 0, "it leans ON the beat, not before it"
    assert lean.duration_beats == Fraction(1, 2), "it takes half the principal's value"
    assert principal.duration_beats == Fraction(1, 2), "the principal gives that time up"
    assert lean.velocity_scale > principal.velocity_scale, "the dissonance is the accented note"


def test_an_acciaccatura_is_crushed_before_the_beat_and_steals_no_time():
    crush, principal = _pair("acciaccatura")
    assert crush.offset_beats < 0, "it is crushed BEFORE the beat"
    assert principal.duration_beats == Fraction(1), "the principal keeps its full value"


def test_a_bare_grace_is_left_alone():
    """`grace` carries no period-specific reading worth inventing, and it already
    sounds as the short note it is written as — pairing it would silence it."""
    g = LayerEvent(bar=1, beat=1.0, pitch="D5", duration="s", role="ornamental", ornament="grace")
    p = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural")
    pairs, consumed = _pair_graces([g, p])
    assert not consumed and not pairs


def test_a_grace_with_nothing_to_lean_on_stays_a_plain_note():
    g = LayerEvent(
        bar=1, beat=1.0, pitch="D5", duration="s", role="ornamental", ornament="appoggiatura"
    )
    pairs, consumed = _pair_graces([g])
    assert not consumed and not pairs
