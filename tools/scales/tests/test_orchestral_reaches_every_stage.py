"""Orchestral music must reach every stage that shapes how a piece sounds.

`LayerIR` has eleven event layers. Module after module hand-typed a list of the
five PIANO ones. Because the piano layers default to `[]` and the orchestral
ones to `None`, a piano-only enumeration never crashes — it covers half the
model, silently, forever.

The two stages pinned here are the ones where the silence did the most damage,
and neither raised anything:

  * `patch_engine` — the critic is the SOLE driver of artistic revision. Four
    revision ops defaulted their target to `principal_line`, so on an orchestral
    piece each one iterated an empty list, changed nothing, and set
    `status = REALIZED` anyway. The fix reported success and did not happen.

  * `performance_renderer` — the humanized MIDI is what the fresh-ears critic
    LISTENS to. Its top-level gather listed five layers, so an orchestral phrase
    produced an empty event list and the function returned an empty
    PerformanceIR on the next line. The critic was judging orchestral music from
    a dead-flat render, hearing exactly the machine-made quality this layer
    exists to remove.

Each test states the measured before-value, because in one case fixing the
melody lookups alone measured as NO improvement at all — an earlier gather was
the real gate, and a fix verified by "does it run" rather than by reproducing
the failure would have been reported as working.
"""

from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState, RevisionOp
from scales.patch_engine import PatchEngine
from scales.performance_renderer import build_performance_ir


def _orchestral(bars=8):
    ir = LayerIR(key="C major", meter=(4, 4), instrumentation="ensemble")
    for b in range(1, bars + 1):
        for i, p in enumerate(("C5", "E5", "G5", "F5")):
            e = LayerEvent(bar=b, beat=1.0 + i, pitch=p, duration="q")
            if i == 0:
                e.slur = "start"
            ir.ensure_layer("foreground").append(e)
        ir.ensure_layer("harmonic_mass").append(
            LayerEvent(bar=b, beat=1.0, pitch=["E4", "G4"], duration="w")
        )
    ir.bar_count = bars
    return ir


def _piano(bars=8):
    ir = LayerIR(key="C major", meter=(4, 4), instrumentation="solo_piano", bar_count=bars)
    for b in range(1, bars + 1):
        for i, p in enumerate(("C5", "E5", "G5", "F5")):
            e = LayerEvent(bar=b, beat=1.0 + i, pitch=p, duration="q")
            if i == 0:
                e.slur = "start"
            ir.principal_line.append(e)
        ir.bass_foundation.append(LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w"))
    return ir


_SLOT = PhraseSlot(
    phrase_id="p1",
    bar_start=1,
    bar_count=8,
    key="C major",
    meter=(4, 4),
    tempo_bpm=96,
    cadence_bar=8,
)


# ─── The critic's revisions must actually land ───────────────────────────────


def test_a_dynamic_revision_lands_on_an_orchestral_phrase():
    """Measured 0 marks before, 16 after."""
    ps = PhraseState(realized=_orchestral())
    PatchEngine().apply_revision_op(
        RevisionOp(operation="change_dynamic", params={"dynamic": "mf"}), ps
    )
    assert sum(1 for e in ps.realized.foreground if e.dynamic) > 0, (
        "the revision reported success and changed nothing — it edited an empty "
        "principal_line while the notes are in foreground"
    )


def test_an_articulation_revision_lands_on_an_orchestral_phrase():
    """Measured 0 before, 16 after. The critic's commonest finding by far."""
    ps = PhraseState(realized=_orchestral())
    PatchEngine().apply_revision_op(
        RevisionOp(operation="set_articulation", params={"articulation": "staccato"}), ps
    )
    assert sum(1 for e in ps.realized.foreground if e.articulation) > 0


def test_a_hairpin_revision_lands_on_an_orchestral_phrase():
    """Measured 0 before, 2 after (a hairpin marks its start and its stop)."""
    ps = PhraseState(realized=_orchestral())
    PatchEngine().apply_revision_op(
        RevisionOp(operation="set_hairpin", params={"kind": "cresc"}, target_bars=(1, 4)), ps
    )
    assert sum(1 for e in ps.realized.foreground if e.hairpin) == 2


def test_an_explicit_target_layer_still_wins():
    """The fallback must not override a layer the critic named."""
    ps = PhraseState(realized=_orchestral())
    PatchEngine().apply_revision_op(
        RevisionOp(
            operation="set_articulation",
            params={"articulation": "tenuto"},
            target_layer="harmonic_mass",
        ),
        ps,
    )
    assert all(not e.articulation for e in ps.realized.foreground)
    assert any(e.articulation == "tenuto" for e in ps.realized.harmonic_mass)


# ─── The render the critic listens to ────────────────────────────────────────


def test_an_orchestral_phrase_gets_a_performance_shape():
    """Measured: 0 dynamic points and 0 microtiming events before; 32 and 48 after."""
    perf = build_performance_ir(_orchestral(), _SLOT)
    assert perf.dynamic_curve, "the render came back with no dynamic shape at all"
    assert perf.microtiming, "the render came back with no microtiming at all"


def test_the_orchestral_shape_matches_the_piano_one():
    """Same notes, different layer — the interpretation should not differ."""
    o = build_performance_ir(_orchestral(), _SLOT)
    p = build_performance_ir(_piano(), _SLOT)
    assert len(o.dynamic_curve) == len(p.dynamic_curve)
    assert len(o.microtiming) == len(p.microtiming)


def test_the_sustain_pedal_is_gated_on_the_forces_not_on_layer_naming():
    """An orchestra has no sustain pedal.

    That was already the outcome — `bass_foundation` is a piano layer and an
    orchestral phrase leaves it empty — but by accident. An accident that
    happens to be correct is the kind of thing that stops being correct
    silently, so the gate is now the instrumentation.
    """
    assert not build_performance_ir(_orchestral(), _SLOT).pedal_events
    assert build_performance_ir(_piano(), _SLOT).pedal_events


def test_an_unknown_instrumentation_still_gets_its_pedal():
    """Unknown resolves to keyboard: this can over-pedal, never go quiet."""
    ir = _piano()
    ir.instrumentation = "something_nobody_has_written_yet"
    assert build_performance_ir(ir, _SLOT).pedal_events
