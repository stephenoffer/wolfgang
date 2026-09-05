"""How many shapes the accompaniment KNOWS, as distinct from how often it repeats.

Found by reading a finished score rather than measuring it. A B-flat andante's
left hand used 11 distinct bar-shapes across 41 bars while its most-common-shape
share was 24% — sitting on Mozart's median of 25%, so `accompaniment_monoculture`
had nothing to say. Real Mozart movements use 13-43 shapes. The hand was not
monotonous; it was working from a tiny vocabulary, which reads as "lacks texture"
and is a different defect.
"""

import glob
import json
from collections import Counter, defaultdict

import pytest

from scales.score_realism import (
    _accompaniment_vocabulary_floor,
    detect_accompaniment_vocabulary_poverty,
)


def _bar(staff, bar, durs, chords):
    return {
        "staff": staff,
        "bar": bar,
        "durations": durs,
        "chord_sizes": chords,
        "bar_beats": 4.0,
    }


def test_a_hand_with_one_shape_is_flagged():
    bars = [_bar(1, i, [0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1]) for i in range(1, 41)]
    out = detect_accompaniment_vocabulary_poverty(bars, composer="mozart", melody_staff=0)
    assert out and out[0]["detector"] == "accompaniment_vocabulary_poverty"


def test_a_varied_hand_is_not_flagged():
    """Two earlier versions of this fixture produced 12 shapes and tripped
    Mozart's floor of 13 — which is the detector working, not failing. Build
    genuinely distinct shapes and count them."""
    values = [0.25, 0.5, 0.75, 1.0, 1.5]
    bars = []
    for i in range(1, 41):
        n = 2 + (i % 5)
        durs = [values[(i + k) % len(values)] for k in range(n)]
        chords = [1 + ((i + k) % 3) for k in range(n)]
        bars.append(_bar(1, i, durs, chords))
    distinct = len({tuple(zip(b["durations"], b["chord_sizes"])) for b in bars})
    floor = _accompaniment_vocabulary_floor("mozart") or 6
    assert distinct > floor, f"fixture has {distinct} shapes, not above the floor {floor}"
    out = detect_accompaniment_vocabulary_poverty(bars, composer="mozart", melody_staff=0)
    assert out == [], out


def test_the_melody_staff_is_not_judged_as_accompaniment():
    """It is judged against the MELODY floor, which is a different number —
    Mozart's melody floor is 20 shapes and his accompaniment floor is 13. This
    test originally asserted no finding at all, which was true only while the
    detector ignored the melody entirely."""
    bars = [_bar(0, i, [0.5, 0.5, 0.5, 0.5], [1, 1, 1, 1]) for i in range(1, 41)]
    out = detect_accompaniment_vocabulary_poverty(bars, composer="mozart", melody_staff=0)
    kinds = {f["detector"] for f in out}
    assert "accompaniment_vocabulary_poverty" not in kinds, kinds
    assert kinds <= {"melody_vocabulary_poverty"}, kinds


def test_short_excerpts_are_left_alone():
    bars = [_bar(1, i, [0.5, 0.5], [1, 1]) for i in range(1, 10)]
    assert detect_accompaniment_vocabulary_poverty(bars, composer="mozart") == []


def test_the_floor_is_composer_relative():
    """A fixed bound taken from Mozart would reject most of real Chopin: his
    mazurka accompaniments genuinely run on very few shapes."""
    mz = _accompaniment_vocabulary_floor("mozart")
    ch = _accompaniment_vocabulary_floor("chopin")
    if mz is None or ch is None:
        pytest.skip("corpora not present")
    assert mz > ch, (mz, ch)


@pytest.mark.calibration
def test_the_floor_does_not_reject_real_movements():
    """The standing discipline: measure the real distribution before the bound
    is allowed to fire. Each composer's floor is his own 5th percentile, so by
    construction it must reject about 5% of his movements and no more."""
    failures = []
    for comp in ("mozart", "beethoven", "chopin", "haydn"):
        floor = _accompaniment_vocabulary_floor(comp)
        if floor is None:
            continue
        per = defaultdict(list)
        for f in sorted(glob.glob(f"tools/reference_index/{comp}/bars_*.json")):
            for b in json.load(open(f)):
                sig = tuple(
                    (
                        round(float(e.get("dur") or 0), 3),
                        len(e.get("pitches") or ()) if e.get("type") == "chord" else 1,
                    )
                    for e in (b.get("lh_display") or [])
                    if isinstance(e, dict) and e.get("type") != "rest"
                )
                if sig:
                    per[b.get("source")].append(sig)
        vals = [len(Counter(v)) for v in per.values() if len(v) >= 30]
        if len(vals) < 8:
            continue
        rate = sum(1 for v in vals if v < floor) / len(vals)
        if rate > 0.10:
            failures.append(f"{comp}: floor {floor} rejects {rate:.0%} of real movements")
    assert not failures, "\n".join(failures)


# ─── the melody has a floor too ─────────────────────────────────────────────


def test_a_melody_of_one_shape_is_flagged():
    """The detector looked only at the accompaniment. A melody repeating its
    shape IS a style — Chopin's most-common melody shape covers 18% of bars at
    the median and 84% at the 95th percentile — but there is still a floor:
    across 85 real Chopin movements the 5th percentile is 6 distinct melody
    shapes, and a melody below that has stopped being a melody."""
    bars = []
    for i in range(1, 41):
        bars.append(_bar(0, i, [1.0] * 4, [1] * 4))
        n = 2 + (i % 7)
        bars.append(_bar(1, i, [0.25] * n, [1 + (i % 3)] * n))
    out = detect_accompaniment_vocabulary_poverty(bars, composer="mozart", melody_staff=0)
    kinds = {f["detector"] for f in out}
    assert "melody_vocabulary_poverty" in kinds, kinds
    assert "accompaniment_vocabulary_poverty" not in kinds, "the varied hand must not be flagged"


def test_the_melody_floor_is_composer_relative():
    """Chopin's melody floor is far below Mozart's; a fixed bound taken from one
    would misjudge the other."""
    from scales.score_realism import _shape_vocabulary_floor

    mz = _shape_vocabulary_floor("mozart", "rh")
    ch = _shape_vocabulary_floor("chopin", "rh")
    if mz is None or ch is None:
        pytest.skip("corpora not present")
    assert mz > ch, (mz, ch)


def test_each_hand_is_measured_against_its_own_floor():
    """A melody and an accompaniment do not have the same vocabulary; measuring
    both against one number would flag the wrong hand."""
    from scales.score_realism import _shape_vocabulary_floor

    for comp in ("mozart", "chopin", "beethoven"):
        rh = _shape_vocabulary_floor(comp, "rh")
        lh = _shape_vocabulary_floor(comp, "lh")
        if rh is None or lh is None:
            continue
        assert rh != lh or rh is None, f"{comp}: identical floors {rh}/{lh} is suspicious"


def test_a_real_piece_is_not_flagged():
    """My own nocturne sits at 17 melody shapes with the commonest covering 34%
    — inside Chopin's range, on the repetitive side. Reading it, I thought it
    was too repetitive; measuring said otherwise, and metric-chasing it would
    have made the music worse."""
    import os

    from scales.scales import self_evaluate

    if not os.path.exists("workspace/chopin-nocturne-ebmaj-20260826/piece_graph.json"):
        pytest.skip("nocturne not present")
    fs = self_evaluate("chopin-nocturne-ebmaj-20260826")["realism"].get("findings") or []
    assert not any(f["detector"] == "melody_vocabulary_poverty" for f in fs)
