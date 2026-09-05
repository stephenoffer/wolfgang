"""The bassoon was given the bass because its NAME contains "bass".

`_style_role_assignments` decides which instrument a style gives the melody and
the bass to. It matched `_BASS_WORDS` — which contains `"bass"` — against text
that included the instrument's **own name**. `"bass" in "bassoon"` is True, so
any ensemble containing a bassoon resolved to `{"bass": "bassoon"}`.

The cello was then left with nothing, and `plan_orchestration`'s last pass —
"anything still silent doubles the melody, better a real part than a tacet
stave" — handed the cello the TUNE. Measured on a real orchestration off this
system:

    Viola         48-60
    Violoncello   63-74     <- the cello playing entirely above the viola

for a whole movement. `bass_clarinet` and `bass_trombone` collide identically.

The fix is not a better word list: an instrument must never be given a role
because of what it is CALLED, only because of what the style says it DOES.
"""

from __future__ import annotations

import pytest

from scales.scales import _BASS_WORDS, _MELODY_WORDS, _style_role_assignments

ENSEMBLE = [
    "flute", "oboe", "clarinet", "bassoon", "horn",
    "violin_1", "violin_2", "viola", "cello", "contrabass",
]


class _Role:
    def __init__(self, name, role="", usage=""):
        self.name = name
        self.role = role
        self.characteristic_usage = usage


def test_a_bassoon_is_not_the_bass_just_for_being_called_one():
    roles = {"bassoon": _Role("Bassoon"), "cello": _Role("Cello")}
    assert "bass" not in _style_role_assignments(roles, ENSEMBLE)


@pytest.mark.parametrize("instrument", ["bassoon", "bass_clarinet", "bass_trombone"])
def test_no_instrument_earns_a_role_from_its_own_name(instrument):
    roles = {instrument: _Role(instrument.replace("_", " ").title())}
    assert _style_role_assignments(roles, ENSEMBLE + [instrument]) == {}


def test_a_style_that_actually_says_so_is_still_heard():
    """The point is to read the style, not to ignore it."""
    roles = {
        "cello": _Role("Cello", role="carries the bass line under everything"),
        "violin_1": _Role("Violin 1", role="sings the principal melody"),
    }
    got = _style_role_assignments(roles, ENSEMBLE)
    assert got.get("bass") == "cello"
    assert got.get("melody") == "violin_1"


def test_the_word_lists_still_collide_which_is_why_the_name_is_excluded():
    """Documents the trap rather than pretending it is gone: 'bass' really is a
    substring of 'bassoon', so any future matcher that sees the instrument name
    reintroduces this exactly."""
    assert any(w in "bassoon" for w in _BASS_WORDS)
    assert not any(w in "cello" for w in _BASS_WORDS)
    assert any(w in "sings the principal melody" for w in _MELODY_WORDS)


def test_the_planner_puts_the_cello_under_the_viola():
    """End to end: the string section has to stack in the right order."""
    from scales.models import LayerEvent, LayerIR
    from scales.orchestration_planner import plan_orchestration
    from scales.pitch import pitch_to_midi

    layer = LayerIR(key="C minor", meter=(4, 4))
    layer.principal_line = [
        LayerEvent(bar=1, beat=float(i + 1), pitch=p, duration="q", role="structural",
                   source_layer="principal_line")
        for i, p in enumerate(["C5", "Eb5", "G5", "C6"])
    ]
    layer.bass_foundation = [
        LayerEvent(bar=1, beat=float(i + 1), pitch=p, duration="q", role="structural",
                   source_layer="bass_foundation")
        for i, p in enumerate(["C2", "G2", "C3", "G2"])
    ]
    parts = plan_orchestration(layer, ENSEMBLE, key="C minor")

    def top(name):
        got = [
            pitch_to_midi(x)
            for e in parts.get(name) or []
            for x in (e["pitch"] if isinstance(e["pitch"], list) else [e["pitch"]])
            if x and x != "rest"
        ]
        return [m for m in got if m]

    cello, viola = top("cello"), top("viola")
    assert cello and viola
    assert max(cello) <= min(viola) + 12, (
        f"cello {min(cello)}-{max(cello)} sits above viola {min(viola)}-{max(viola)}"
    )
