"""Every orchestral part must carry its own dynamics.

Dynamics live on the piano core's melody layer, and each orchestral part
inherited only the marks that sat on the events it was built from. So the parts
derived from the melody arrived marked and everything else arrived blank —
measured on a real orchestration off this system: cello 60 notes / 0 dynamics,
violin I 48 / 0, violin II 48 / 0, viola and horn 0 of everything, and the wind
pads constructed with a literal ``"dynamic": None``.

That is the whole notation gap between a piano core (2.21 marks per staff-bar)
and its orchestration (0.63). It is not a stylistic weakness: there is no
orchestral part in the repertoire with no dynamic in it, and a wind player
holding a whole-note chord has to be told how loud to hold it.
"""

from scales.models import LayerEvent, LayerIR
from scales.orchestration_planner import _mark_part_dynamics, pad_dynamic, plan_orchestration

ENSEMBLE = [
    "flute",
    "oboe",
    "clarinet",
    "bassoon",
    "horn",
    "violin_i",
    "violin_ii",
    "viola",
    "cello",
]


def _core() -> LayerIR:
    """Four bars of piano core: a melody marked once, and a bass marked never."""
    mel = [
        LayerEvent(
            bar=b,
            beat=1.0,
            pitch=p,
            duration="q",
            role="structural",
            dynamic=("p" if b == 1 else None),
        )
        for b, p in enumerate(["C5", "D5", "E5", "F5"], start=1)
    ]
    bass = [
        LayerEvent(bar=b, beat=1.0, pitch=p, duration="h", role="bass_foundation")
        for b, p in enumerate(["C3", "G2", "C3", "F2"], start=1)
    ]
    return LayerIR(principal_line=mel, bass_foundation=bass, meter=(4, 4), key="C major")


def test_every_sounding_part_carries_a_dynamic():
    parts = plan_orchestration(_core(), ENSEMBLE, key="C major")
    unmarked = [
        inst
        for inst, evs in parts.items()
        if evs and not any(e.get("dynamic") for e in evs if isinstance(e, dict))
    ]
    assert not unmarked, f"parts a player cannot read: {unmarked}"


def test_a_dynamic_is_not_restated_bar_after_bar():
    """Re-stating an unchanged dynamic is what `detect_notation_spam` exists to
    catch, and it is what makes a score look machine-set."""
    parts = {
        "cello": [{"bar": b, "beat": 1.0, "pitch": "C3", "duration": "q"} for b in range(1, 9)]
    }
    _mark_part_dynamics(parts, {b: 4 for b in range(1, 9)})
    marked = [e for e in parts["cello"] if e.get("dynamic")]
    assert len(marked) == 1, "an unchanging dynamic is written once, at entry"
    assert marked[0]["bar"] == 1


def test_a_change_in_loudness_is_written_where_it_happens():
    parts = {
        "cello": [{"bar": b, "beat": 1.0, "pitch": "C3", "duration": "q"} for b in range(1, 5)]
    }
    _mark_part_dynamics(parts, {1: 2, 2: 2, 3: 5, 4: 5})
    marked = [(e["bar"], e["dynamic"]) for e in parts["cello"] if e.get("dynamic")]
    assert marked == [(1, "p"), (3, "f")]


def test_a_composers_own_mark_is_never_overwritten():
    parts = {"cello": [{"bar": 1, "beat": 1.0, "pitch": "C3", "duration": "q", "dynamic": "ppp"}]}
    _mark_part_dynamics(parts, {1: 6})
    assert parts["cello"][0]["dynamic"] == "ppp"


def test_a_pad_sits_below_the_texture_it_supports():
    """A pad supports rather than leads — the reason a horn chord under a
    singing oboe is marked p and not mf."""
    assert pad_dynamic(4) == "mp"  # under mf
    assert pad_dynamic(6) == "f"  # under ff
    assert pad_dynamic(0) == "ppp"  # clamps rather than falling off the table
    assert pad_dynamic(99) == "fff"
