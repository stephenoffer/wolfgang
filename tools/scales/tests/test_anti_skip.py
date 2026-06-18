"""Unit tests for anti_skip.py. Run: python3 -m scales.tests.test_anti_skip"""

from scales import anti_skip as A
from scales.models import LayerEvent, LayerIR


def _layer(notes):
    """notes: list of (pitch, dur). One bar of principal line."""
    lyr = LayerIR(phrase_id="t", bar_count=1, key="C")
    beat = 1.0
    for p, d in notes:
        lyr.principal_line.append(
            LayerEvent(bar=1, beat=beat, pitch=p, duration=d, source_layer="principal_line")
        )
        beat += 1.0
    return lyr


def test_signature_parses_pitches_and_rhythm():
    sig = A.signature_from_shorthand("E5q G5e F5e E5e rest_q")
    assert sig["rhythm"]  # has rhythm histogram
    assert sig["intervals"]  # has interval histogram
    # 'step' should dominate (E-G is small leap, G-F-E are steps)
    assert "step" in sig["intervals"]


def test_chord_token_uses_top_note():
    sig = A.signature_from_shorthand("[C5,E5,G5]q A5q")
    # G5 (top of chord) → A5 is a step up; one interval recorded
    assert sum(sig["intervals"].values()) > 0


def test_resemblance_high_for_similar():
    a = A.signature_from_shorthand("E5q G5e F5e E5q D5q")
    b = A.signature_from_shorthand("A5q C6e B5e A5q G5q")  # same rhythm+contour
    assert A.resemblance(a, b) > 0.7


def test_resemblance_low_for_dissimilar():
    a = A.signature_from_shorthand("E5q G5e F5e E5q D5q")
    b = A.signature_from_shorthand("C5w")  # one whole note, no intervals/varied rhythm
    assert A.resemblance(a, b) < 0.5


def test_best_resemblance_empty_exemplars():
    # nothing to resemble → never falsely flag
    sig = A.signature_from_shorthand("C5w")
    score, idx = A.best_resemblance(sig, [])
    assert score == 1.0 and idx == -1


def test_check_composed_blind_flags_blind():
    exemplars = ["E5q G5e F5e E5q D5q", "A5q C6e B5e A5q G5q"]
    blind = _layer([("C6", "w")])
    finding = A.check_composed_blind(blind, exemplars)
    assert finding is not None
    assert finding["check"] == "composed_blind"
    assert finding["best_resemblance"] < A.BLIND_FLOOR


def test_check_composed_blind_passes_adapting():
    exemplars = ["E5q G5e F5e E5q D5q", "A5q C6e B5e A5q G5q"]
    adapting = _layer([("C5", "q"), ("E5", "e"), ("D5", "e"), ("C5", "q"), ("B4", "q")])
    assert A.check_composed_blind(adapting, exemplars) is None


def test_no_exemplars_returns_none():
    adapting = _layer([("C5", "q"), ("D5", "q")])
    assert A.check_composed_blind(adapting, []) is None


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
