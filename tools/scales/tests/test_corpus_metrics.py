"""Unit tests for corpus_metrics.py. Run: python3 -m scales.tests.test_corpus_metrics"""

from scales import corpus_metrics as CM


def _bar(
    md,
    ad,
    rh="singing_melody",
    lh="alberti",
    direction="ascending",
    reg=60,
    grace=False,
    dotted=False,
):
    return {
        "melody_density": md,
        "accomp_density": ad,
        "rh_texture": rh,
        "lh_texture": lh,
        "melody_direction": direction,
        "register_center": reg,
        "has_grace_notes": grace,
        "has_dotted_rhythms": dotted,
    }


def test_empty_and_single():
    assert CM.bar_metrics([]) == {m: 0.0 for m in CM.SCALAR_METRICS}
    one = CM.bar_metrics([_bar(5, 5)])
    # No adjacency → delta metrics are 0, but density is real
    assert one["events_per_bar"] == 10.0
    assert one["texture_change_pct"] == 0.0
    assert one["density_cv"] == 0.0


def test_events_per_bar_split():
    bars = [_bar(8, 4), _bar(6, 6)]
    m = CM.bar_metrics(bars)
    assert m["events_per_bar"] == 12.0
    assert m["events_per_bar_rh"] == 7.0
    assert m["events_per_bar_lh"] == 5.0


def test_texture_change_threshold():
    # totals 10, 10, 20 → one adjacent shift >= 4 out of two pairs
    bars = [_bar(5, 5), _bar(5, 5), _bar(10, 10)]
    m = CM.bar_metrics(bars)
    assert abs(m["texture_change_pct"] - 0.5) < 1e-6


def test_texture_and_direction_changes():
    bars = [
        _bar(5, 5, lh="alberti", direction="up"),
        _bar(5, 5, lh="walking_bass", direction="up"),
        _bar(5, 5, lh="walking_bass", direction="down"),
    ]
    m = CM.bar_metrics(bars)
    assert abs(m["lh_texture_change_pct"] - 0.5) < 1e-6  # 1 of 2 pairs
    assert abs(m["direction_changes_per_bar"] - 0.5) < 1e-6  # 1 of 2 pairs


def test_register_span_and_ratios():
    bars = [_bar(5, 5, reg=50, grace=True), _bar(5, 5, reg=70, dotted=True)]
    m = CM.bar_metrics(bars)
    assert m["register_span"] == 20.0
    assert m["grace_ratio"] == 0.5
    assert m["dotted_ratio"] == 0.5


def test_texture_distribution_and_l1():
    bars = [_bar(5, 5, lh="alberti"), _bar(5, 5, lh="alberti"), _bar(5, 5, lh="walking_bass")]
    dist = CM.texture_distribution(bars, "lh")
    assert abs(dist["alberti"] - 2 / 3) < 1e-3  # function rounds to 4 dp
    # L1 to itself is 0; to a disjoint distribution is 2
    assert CM.l1_distance(dist, dist) == 0.0
    assert CM.l1_distance({"a": 1.0}, {"b": 1.0}) == 2.0


def test_zscore_floor():
    # stdev 0 must not divide-by-zero
    assert CM.zscore(5.0, 5.0, 0.0) == 0.0
    assert CM.zscore(7.0, 5.0, 1.0) == 2.0


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
