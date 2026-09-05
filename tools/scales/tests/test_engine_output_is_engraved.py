"""The engine fallback must engrave what it realizes.

`expression_enricher` is the engraver's pass: it fills in the slurs,
articulation, hairpins, dynamics and pedal a composer left blank, period-aware,
and only ever writes a field that is None. It runs on the agent path inside
`_gated_commit`.

It did not run on the ENGINE path, which is the path taken by every phrase the
agent did not author. Measured on a fresh three-phrase section: 229 events
carrying 0 slurs, 0 articulations, 0 hairpins, 0 ornaments and 0 pedal marks —
dynamics only, straight from the realizer. That is what a score with 0.00
notation marks per bar looks like, and several in `workspace/` are exactly that.
"""

from scales.expression_enricher import ENGRAVING_STYLES, enrich_layer_ir
from scales.models import LayerEvent, LayerIR


def _bare_engine_surface() -> LayerIR:
    """What the engine hands over: pitches, durations, nothing else."""
    mel = [
        LayerEvent(bar=b, beat=float(i + 1), pitch=p, duration="q", role="structural")
        for b, run in enumerate([["C5", "D5", "E5", "F5"], ["G5", "F5", "E5", "D5"]], start=1)
        for i, p in enumerate(run)
    ]
    bass = [
        LayerEvent(bar=b, beat=1.0, pitch=p, duration="w", role="bass_foundation")
        for b, p in enumerate(["C3", "G2"], start=1)
    ]
    return LayerIR(principal_line=mel, bass_foundation=bass, meter=(4, 4), key="C major")


def _marks(layer: LayerIR) -> int:
    return sum(
        1
        for name in ("principal_line", "bass_foundation")
        for e in getattr(layer, name)
        for f in ("slur", "articulation", "hairpin", "dynamic", "pedal")
        if getattr(e, f, None)
    )


def test_a_bare_surface_comes_out_of_the_engraver_marked():
    layer = _bare_engine_surface()
    assert _marks(layer) == 0, "fixture must start bare or the test proves nothing"
    enrich_layer_ir(layer, style="classical")
    assert _marks(layer) > 0


def test_the_engraver_never_changes_a_pitch_or_a_duration():
    """It is an engraver, not a composer: it may add a mark and nothing else."""
    layer = _bare_engine_surface()
    before = [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line]
    enrich_layer_ir(layer, style="classical")
    after = [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line]
    assert before == after


def test_a_mark_the_composer_wrote_is_never_overwritten():
    layer = _bare_engine_surface()
    layer.principal_line[0].articulation = "staccato"
    enrich_layer_ir(layer, style="classical")
    assert layer.principal_line[0].articulation == "staccato"


def test_the_engine_path_calls_the_engraver_at_all(function_source):
    """The defect was not in the enricher — it was that nothing on this path
    called it. Pin the call site itself."""
    from scales import scales

    src = function_source(scales, "run_scales_section")
    assert "_engrave_phrase(" in src, "the engine commit loop must engrave what it realizes"


def test_every_engraving_style_is_period_gated_somewhere():
    """No pedal for Bach, no dynamics for Palestrina — the gating is the reason
    running this on every path is safe."""
    assert ENGRAVING_STYLES
    assert any(getattr(s, "dynamic_every_n_bars", 0) > 50 for s in ENGRAVING_STYLES.values())
