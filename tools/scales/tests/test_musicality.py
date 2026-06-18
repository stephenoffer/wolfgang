"""Unit tests for musicality.py. Run: python3 tools/scales/tests/test_musicality.py"""

from scales import musicality as M
from scales.models import LayerEvent, LayerIR


def _ev(bar, beat, pitch, dur, layer="principal_line"):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, source_layer=layer)


def mechanical_phrase() -> LayerIR:
    """4 bars: monotone quarter-note melody, identical Alberti, no rests."""
    layer = LayerIR(phrase_id="t1", bar_count=4, key="C")
    for bar in range(1, 5):
        for beat in (1.0, 2.0, 3.0, 4.0):
            layer.principal_line.append(_ev(bar, beat, "C5", "q"))
        layer.bass_foundation.append(_ev(bar, 1.0, "C3", "q", "bass_foundation"))
        for i, p in enumerate(["G3", "E3", "G3"]):
            layer.response_layer.append(_ev(bar, 2.0 + i, p, "q", "response_layer"))
    return layer


def musical_phrase() -> LayerIR:
    """4 bars: arched stepwise melody with varied rhythm, rests, chords."""
    layer = LayerIR(phrase_id="t2", bar_count=4, key="C")
    melody = [
        (1, 1.0, "C5", "q"),
        (1, 2.0, "D5", "e"),
        (1, 2.5, "E5", "e"),
        (1, 3.0, "F5", "dq"),
        (1, 4.5, "G5", "e"),
        (2, 1.0, "A5", "h"),
        (2, 3.0, "G5", "e"),
        (2, 3.5, "F5", "e"),
        (2, 4.0, "E5", "q"),
        (3, 1.0, "rest", "e"),
        (3, 1.5, "E5", "e"),
        (3, 2.0, "F5", "s"),
        (3, 2.25, "G5", "s"),
        (3, 2.5, "A5", "e"),
        (3, 3.0, "G5", "q"),
        (3, 4.0, "D5", "q"),
        (4, 1.0, "E5", "dq"),
        (4, 2.5, "D5", "e"),
        (4, 3.0, "C5", "h"),
    ]
    for bar, beat, p, d in melody:
        layer.principal_line.append(_ev(bar, beat, p, d))
    lh = [
        (1, 1.0, "C3", "e"),
        (1, 1.5, "G3", "e"),
        (1, 2.0, "E3", "e"),
        (1, 2.5, "G3", "e"),
        (1, 3.0, "C3", "e"),
        (1, 3.5, "G3", "e"),
        (1, 4.0, "E3", "e"),
        (1, 4.5, "G3", "e"),
        (2, 1.0, "F3", "e"),
        (2, 1.5, "A3", "e"),
        (2, 2.0, "C4", "e"),
        (2, 2.5, "A3", "e"),
        (2, 3.0, "F3", "q"),
        (2, 4.0, "rest", "q"),
        (3, 1.0, "G3", "q"),
        (3, 2.0, ["G3", "B3"], "q"),
        (3, 3.0, "G2", "e"),
        (3, 3.5, "D3", "e"),
        (3, 4.0, "B3", "q"),
        (4, 1.0, "C3", "e"),
        (4, 1.5, "G3", "e"),
        (4, 2.0, "E3", "q"),
        (4, 3.0, ["C3", "G3"], "h"),
    ]
    for bar, beat, p, d in lh:
        target = "bass_foundation" if beat == 1.0 else "response_layer"
        getattr(layer, target).append(_ev(bar, beat, p, d, target))
    return layer


def test_rhythmic_variety():
    s_mech, d_mech = M.rhythmic_variety(mechanical_phrase())
    s_mus, d_mus = M.rhythmic_variety(musical_phrase())
    assert s_mech < 0.1, f"all-quarters should score ~0, got {s_mech}"
    assert s_mus > 0.5, f"varied rhythm should score >0.5, got {s_mus}"
    assert d_mus["distinct"] >= 5


def test_melodic_smoothness_and_profile():
    s_mech, _ = M.melodic_smoothness(mechanical_phrase())
    s_mus, d = M.melodic_smoothness(musical_phrase())
    assert s_mus > 0.7, f"stepwise melody should be smooth, got {s_mus}"
    score, detail = M.melodic_interval_profile(musical_phrase())
    assert score > 0.6, f"profile near generic prior, got {score}: {detail}"


def test_direction_changes():
    s_mech, d_mech = M.direction_changes_per_bar(mechanical_phrase())
    assert s_mech == 0.0, f"monotone melody has no contour, got {d_mech}"
    s_mus, d_mus = M.direction_changes_per_bar(musical_phrase())
    assert s_mus >= 0.5, f"arched melody should score, got {s_mus} {d_mus}"


def test_rest_ratio():
    s_mech, _ = M.rest_ratio(mechanical_phrase())
    assert s_mech == 0.0, "zero rests must score 0"
    s_mus, d = M.rest_ratio(musical_phrase())
    assert s_mus > 0.5, f"breathing phrase should score, got {s_mus} {d}"


def test_figuration_richness():
    stats = {"singing_melody": {"median": 5.0, "p25": 3.0, "p75": 6.0}}
    s, d = M.figuration_richness(musical_phrase(), stats, "singing_melody")
    assert s > 0.8, f"~4.75 events/bar vs median 5 should score high: {d}"
    s_sparse, d_sparse = M.figuration_richness(
        mechanical_phrase(), {"passage_work": {"median": 11.0, "p25": 9.0}}, "passage_work"
    )
    assert s_sparse < 0.5, f"4/bar vs median 11 should score low: {d_sparse}"


def test_chord_counting():
    """A chord counts as one event, matching corpus melody_density."""
    layer = LayerIR(bar_count=1)
    layer.principal_line.append(_ev(1, 1.0, ["C5", "E5", "G5"], "q"))
    assert M.events_per_bar(layer, "rh") == 1.0


def test_unparseable_pitch_does_not_crash():
    """pitch_to_midi returns None (not an exception) for an unparseable pitch;
    a None must never reach interval math (would crash the commit gate)."""
    layer = LayerIR(phrase_id="t", bar_count=1, key="C")
    layer.principal_line.append(_ev(1, 1.0, "C5", "q"))
    layer.principal_line.append(_ev(1, 2.0, "Xz9", "q"))  # garbage pitch
    layer.principal_line.append(_ev(1, 3.0, "E5", "q"))
    # none of these should raise
    M.direction_changes_per_bar(layer)
    M.melodic_interval_profile(layer)
    M.melodic_smoothness(layer)
    out = M.summarize(layer)
    assert out  # produced a report rather than crashing


def test_density_cv_flat_vs_varied():
    # Mechanical phrase: identical event count every bar -> CV ~ 0.
    flat_cv, det = M.density_cv(mechanical_phrase())
    assert det["bar_count"] >= 4
    assert flat_cv < 0.05, (flat_cv, det)
    # Musical phrase: density ebbs and flows -> CV clearly positive.
    var_cv, _ = M.density_cv(musical_phrase())
    assert var_cv > flat_cv
    assert var_cv > 0.1, var_cv


def test_density_cv_short_phrase_is_zero():
    layer = LayerIR(phrase_id="t", bar_count=1, key="C")
    layer.principal_line.append(_ev(1, 1.0, "C5", "q"))
    cv, det = M.density_cv(layer)
    assert cv == 0.0 and det["bar_count"] == 1


def test_summarize():
    out = M.summarize(musical_phrase())
    assert set(out) >= {"rhythmic_variety", "rest_ratio", "direction_changes_per_bar"}
    for name, entry in out.items():
        assert 0.0 <= entry["score"] <= 1.0, name


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
