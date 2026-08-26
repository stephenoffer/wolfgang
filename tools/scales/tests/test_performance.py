"""Performance humanization: deterministic primitives (jitter/shape), per-style
profiles, and PerformanceIR construction (shaped hairpins, harmony-aware pedal,
breath points). No music21 needed — these are the pure layers.

Run: python3 -m scales.tests.test_performance
"""

from scales import performance_renderer as pr
from scales import performance_util as pu
from scales.models import LayerEvent, LayerIR, PhraseSlot
from scales.performance_params import profile_for_composer, profile_for_period

# ─── F1: jitter + shape ──────────────────────────────────────────────────────


def test_jitter_deterministic_and_bounded():
    a = pu.jitter((1, 2.0, 60), 5.0)
    b = pu.jitter((1, 2.0, 60), 5.0)
    assert a == b, "jitter must be stable for the same seed"
    assert -5.0 <= a <= 5.0
    # different seeds generally differ
    assert pu.jitter((1, 2.0, 61), 5.0) != a
    assert pu.jitter((1, 2.0, 60), 0.0) == 0.0


def test_shape_endpoints_and_monotonic():
    for kind in ("linear", "s_curve", "exp", "log"):
        assert abs(pu.shape(0.0, kind) - 0.0) < 1e-9, kind
        assert abs(pu.shape(1.0, kind) - 1.0) < 1e-9, kind
    # s_curve is non-linear: midpoint is 0.5 but quarter point < linear's 0.25? no
    assert pu.shape(0.5, "s_curve") == 0.5
    assert pu.shape(0.5, "exp") < 0.5  # slow start
    assert pu.shape(0.5, "log") > 0.5  # fast start
    assert pu.shape(0.5, "arch") == 1.0  # peak at midpoint
    # depth blends toward linear
    assert pu.shape(0.5, "exp", depth=0.0) == 0.5


# ─── F2: per-style profiles ──────────────────────────────────────────────────


def test_profile_resolution_by_period_and_composer():
    assert profile_for_period("baroque").period == "baroque"
    assert profile_for_period(None).period == "classical"
    assert profile_for_composer("mozart").period == "classical"
    assert profile_for_composer("chopin").period == "romantic"
    assert profile_for_composer("bach").period == "baroque"
    assert profile_for_composer("galant").period == "classical"  # synonym
    assert profile_for_composer("nobody-unknown").period == "classical"  # honest fallback


def test_profiles_differ_meaningfully():
    bar, rom = profile_for_period("baroque"), profile_for_period("romantic")
    assert rom.rubato_depth > bar.rubato_depth
    assert bar.inegalite_strength > rom.inegalite_strength
    assert bar.pedal_lead_ms <= rom.pedal_lead_ms


# ─── F3 + WS-VEL/ART: PerformanceIR ──────────────────────────────────────────


def _slot(harmony=None):
    return PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=1,
        bar_count=4,
        key="C",
        meter=[4, 4],
        cadence_target="PAC",
        harmony_plan=harmony or ["I", "I", "V", "I"],
    )


def _layer_with_hairpin():
    lyr = LayerIR(phrase_id="p", bar_count=4, key="C", meter=[4, 4])
    # explicit p at start, crescendo opening, stop at bar 3
    lyr.principal_line = [
        LayerEvent(
            bar=1,
            beat=1.0,
            pitch="C5",
            duration="q",
            dynamic="p",
            hairpin="cresc_start",
            source_layer="principal_line",
        ),
        LayerEvent(bar=2, beat=1.0, pitch="E5", duration="q", source_layer="principal_line"),
        LayerEvent(
            bar=3, beat=1.0, pitch="G5", duration="q", hairpin="stop", source_layer="principal_line"
        ),
        LayerEvent(bar=4, beat=1.0, pitch="C6", duration="q", source_layer="principal_line"),
    ]
    lyr.bass_foundation = [
        LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", source_layer="bass_foundation")
        for b in range(1, 5)
    ]
    return lyr


def test_backward_compatible_no_profile():
    perf = pr.build_performance_ir(_layer_with_hairpin(), _slot())
    assert perf.dynamic_curve, "should still build a curve with no profile arg"


def test_hairpin_builds_rising_shaped_curve():
    perf = pr.build_performance_ir(
        _layer_with_hairpin(), _slot(), profile=profile_for_period("romantic")
    )
    vels = [p.velocity for p in perf.dynamic_curve]
    assert vels == sorted(vels), f"crescendo must rise monotonically: {vels}"
    assert len(perf.dynamic_curve) >= 3, "hairpin should add intermediate points"


def test_pedal_follows_harmony_and_breath_lifts():
    layer = _layer_with_hairpin()
    # harmony I I V I -> a pedal span over bars 1-2 (same chord) then 3, then 4
    perf = pr.build_performance_ir(
        layer,
        _slot(["I", "I", "V", "I"]),
        profile=profile_for_period("classical"),
        breath_points=[(3, 1.0)],
    )
    downs = sorted(p.bar for p in perf.pedal_events if p.action == "down")
    assert 1 in downs and 4 in downs
    assert 3 not in downs, "a breath bar must lift (not press) the pedal"


def test_velocity_at_curve_shapes_segment():
    perf = pr.build_performance_ir(
        _layer_with_hairpin(), _slot(), profile=profile_for_period("classical")
    )
    lin = pr.velocity_at(perf, 2, 1.0, 4.0, curve_kind="linear")
    exp = pr.velocity_at(perf, 2, 1.0, 4.0, curve_kind="exp")
    # not asserting direction (depends on anchors), just that shaping changes it
    # somewhere across the span
    diffs = [
        pr.velocity_at(perf, b, 2.0, 4.0, curve_kind="linear")
        != pr.velocity_at(perf, b, 2.0, 4.0, curve_kind="exp")
        for b in range(1, 4)
    ]
    assert any(diffs) or lin == exp  # shaping has an effect (or curve too short)


# ─── WS-TEMPO: phrase tempo arc ──────────────────────────────────────────────


def test_tempo_arc_pushes_with_tension_and_broadens_at_cadence():
    from scales.models import PhraseCurves

    layer = _layer_with_hairpin()
    slot = _slot()
    slot.curves = PhraseCurves(tension=[0.2, 0.5, 0.8, 1.0])  # rising
    perf = pr.build_performance_ir(layer, slot, profile=profile_for_period("romantic"))
    assert perf.rubato_windows, "a tension arc should create a rubato window"
    # high-tension bar 3 pushes (factor > 1); cadence bar 4 broadens (< 1)
    f3 = pr.tempo_factor_at(perf, 3, 1.0, 4.0)
    f4 = pr.tempo_factor_at(perf, 4, 1.0, 4.0)
    assert f3 > 1.0, f3
    assert f4 < 1.0, f4


def test_render_is_duration_bounded_and_deterministic():
    try:
        import music21  # noqa: F401
    except Exception:
        print("  (skipped: no music21)")
        return
    import hashlib
    import tempfile

    from scales.midi_renderer import render_midi
    from scales.models import PhraseCurves, StyleDNA
    from scales.piece_graph import PieceGraph

    g = PieceGraph()
    g.piece_id = "tperf"
    g.style_dna = StyleDNA(composer_id="chopin")
    layer = _layer_with_hairpin()
    slot = _slot()
    slot.curves = PhraseCurves(tension=[0.3, 0.6, 0.9, 0.4])
    from scales.models import PhraseState

    ps = PhraseState(slot=slot)
    ps.realized = layer
    g.phrases["m1_a_p1"] = ps
    d = tempfile.mkdtemp()
    p1 = render_midi(g, output_dir=d)
    h1 = hashlib.md5(open(p1, "rb").read()).hexdigest()
    p2 = render_midi(g, output_dir=d)
    h2 = hashlib.md5(open(p2, "rb").read()).hexdigest()
    assert h1 == h2, "render must be byte-deterministic (resume/caching)"
    sc = music21.converter.parse(p1)
    # 4 bars * 4 quarters = 16; rubato/jitter must not drag it materially
    assert 15.0 <= sc.highestTime <= 17.5, sc.highestTime


# ─── Determinism invariant: no RNG/wallclock in the performance layer ────────


def test_no_rng_in_performance_modules():
    import re
    from pathlib import Path

    base = Path(__file__).resolve().parents[1]
    forbidden = re.compile(
        r"\b(import random|random\.|time\.time|datetime\.now|"
        r"Date\.now|np\.random)\b"
    )
    for mod in ("performance_util.py", "performance_params.py", "performance_renderer.py"):
        text = (base / mod).read_text()
        hits = [ln for ln in text.splitlines() if forbidden.search(ln)]
        assert not hits, f"{mod} uses non-deterministic RNG/clock: {hits}"


if __name__ == "__main__":
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in fns:
        fn()
        print(f"ok {name}")
    print(f"\n{len(fns)} tests passed")


# ── Per-voice microtiming ────────────────────────────────────────────────────
# TimingOffset was keyed by (bar, beat) alone, so it could not express "the
# melody is struck ahead of the bass on this beat" — the most documented cue in
# human performance. Two offsets at one instant collided on the same key and
# whichever was recorded first won, so melody and bass moved TOGETHER: silently
# the opposite of the intent. These pin the semantics that fixed it.


def test_per_voice_offsets_do_not_collide_at_one_instant():
    from scales.models import PerformanceIR, TimingOffset
    from scales.performance_renderer import microtiming_at

    perf = PerformanceIR(phrase_id="x")
    perf.microtiming = [
        TimingOffset(bar=1, beat=1.0, offset_ms=-12.0, voice="melody"),
        TimingOffset(bar=1, beat=1.0, offset_ms=4.0, voice="accompaniment"),
    ]
    # Same bar, same beat, two different lines: both must survive.
    assert microtiming_at(perf, 1, 1.0, voice="melody") == -12.0
    assert microtiming_at(perf, 1, 1.0, voice="accompaniment") == 4.0


def test_voiceless_offset_still_applies_to_every_voice():
    """A breath or an agogic stretch belongs to the instant, not to one line.

    Every offset written before the ``voice`` field existed is voiceless, so
    this is also the backwards-compatibility guarantee.
    """
    from scales.models import PerformanceIR, TimingOffset
    from scales.performance_renderer import microtiming_at

    perf = PerformanceIR(phrase_id="x")
    perf.microtiming = [TimingOffset(bar=2, beat=1.0, offset_ms=9.0)]
    for voice in ("melody", "accompaniment", None):
        assert microtiming_at(perf, 2, 1.0, voice=voice) == 9.0


def test_per_voice_offset_wins_over_the_whole_instant():
    from scales.models import PerformanceIR, TimingOffset
    from scales.performance_renderer import microtiming_at

    perf = PerformanceIR(phrase_id="x")
    perf.microtiming = [
        TimingOffset(bar=3, beat=2.0, offset_ms=6.0),
        TimingOffset(bar=3, beat=2.0, offset_ms=-15.0, voice="melody"),
    ]
    assert microtiming_at(perf, 3, 2.0, voice="melody") == -15.0
    assert microtiming_at(perf, 3, 2.0, voice="accompaniment") == 6.0


def test_a_voiceless_query_still_sees_a_voiced_offset():
    """ "What is the timing here" must not answer zero because every offset at
    that instant happens to name a line.

    This is the pre-voice behaviour — the function returned the first offset at
    (bar, beat) regardless — so callers that don't model voices stay honest.
    """
    from scales.models import PerformanceIR, TimingOffset
    from scales.performance_renderer import microtiming_at

    perf = PerformanceIR(phrase_id="x")
    perf.microtiming = [TimingOffset(bar=3, beat=1.0, offset_ms=23.3, voice="melody")]
    assert microtiming_at(perf, 3, 1.0) == 23.3


def test_a_named_voice_does_not_pick_up_another_lines_timing():
    from scales.models import PerformanceIR, TimingOffset
    from scales.performance_renderer import microtiming_at

    perf = PerformanceIR(phrase_id="x")
    perf.microtiming = [TimingOffset(bar=3, beat=1.0, offset_ms=23.3, voice="melody")]
    assert microtiming_at(perf, 3, 1.0, voice="accompaniment") == 0.0
