"""Unit tests for direct_compose shorthand. Run: python3 tools/scales/tests/test_direct_compose.py"""

from scales.direct_compose import _parse_shorthand, compose_phrase


def test_legacy_tokens():
    evs = _parse_shorthand("G4q Bb4e D5dq rest_q")
    assert [(e["pitch"], e["dur"]) for e in evs] == [
        ("G4", "q"),
        ("Bb4", "e"),
        ("D5", "dq"),
        ("rest", "q"),
    ]


def test_chords():
    evs = _parse_shorthand("[C5,E5,G5]q [F3,A3]h")
    assert evs[0]["pitch"] == ["C5", "E5", "G5"] and evs[0]["dur"] == "q"
    assert evs[1]["pitch"] == ["F3", "A3"] and evs[1]["dur"] == "h"


def test_slur_tie_hairpin():
    evs = _parse_shorthand("(<C5e D5e E5q!) F5h~ F5q")
    assert evs[0]["slur"] == "start" and evs[0]["hairpin"] == "cresc_start"
    assert evs[2]["slur"] == "stop" and evs[2]["hairpin"] == "stop"
    assert evs[3]["tie"] == "start"


def test_modifiers():
    evs = _parse_shorthand("D5q:tr E5e:stacc G5q:mord:f A5q:grace")
    assert evs[0]["ornament"] == "trill"
    assert evs[1]["articulation"] == "staccato"
    assert evs[2]["ornament"] == "mordent" and evs[2]["dynamic"] == "f"
    assert evs[3]["ornament"] == "grace"


def test_interleaved_flags():
    evs = _parse_shorthand("G5q!:tr) >B4h:p")
    assert evs[0]["ornament"] == "trill"
    assert evs[0]["hairpin"] == "stop" and evs[0]["slur"] == "stop"
    assert evs[1]["hairpin"] == "dim_start" and evs[1]["dynamic"] == "p"


def test_compose_phrase_round_trip():
    bars = [
        {"rh": "(C5q D5e E5e F5q:tr G5q)", "lh": "C3e G3e E3e G3e C3e G3e E3e G3e", "dyn": "p"},
        {"rh": "[C5,E5,G5]h~ [C5,E5,G5]h", "lh": "C3q G2q C3h"},
    ]
    layer = compose_phrase(bars, key="C", phrase_id="t_p1")
    assert layer.bar_count == 2
    assert len(layer.principal_line) == 7
    # 8+3 LH events → 1 bass per bar, the rest response
    assert len(layer.bass_foundation) == 2
    assert len(layer.response_layer) == 7 + 2
    trills = [e for e in layer.principal_line if e.ornament == "trill"]
    assert len(trills) == 1
    # chord tie auto-resolution
    tied = [e for e in layer.principal_line if e.tie]
    assert [e.tie for e in tied] == ["start", "stop"]
    # slur survives
    slurs = [e.slur for e in layer.principal_line if e.slur]
    assert slurs == ["start", "stop"]
    # bar dynamic lands on first events
    assert layer.principal_line[0].dynamic == "p"


def test_legacy_tuple_input():
    bars = [{"rh": [("C5", "q"), ("D5", "e")], "lh": [("C3", "h")]}]
    layer = compose_phrase(bars, key="C")
    assert len(layer.principal_line) == 2
    assert layer.principal_line[1].beat == 2.0


def test_grace_takes_no_time():
    bars = [{"rh": "D5e:grace C5q D5q", "lh": "C3h"}]
    layer = compose_phrase(bars, key="C")
    beats = [e.beat for e in layer.principal_line]
    assert beats == [1.0, 1.0, 2.0], beats


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
