"""The layer-name groups must not drift from the model.

Nine modules carried hand-typed copies of these tuples and most listed only the
five PIANO layers, so orchestral music was silently invisible to them — the
critic's whole-piece merge dropped every orchestral note and reported one bar,
theme recurrence reported "no theme" for every orchestral piece, and the
musicality metrics returned a clean bill of health for a score they could not
see. None of it raised; each produced a plausible number instead.

Duplicated enumerations are this repo's documented first source of bugs. These
tests exist because a comment saying "keep this in step" is not a mechanism.
"""

from scales.models import (
    ALL_LAYERS,
    LOWER_LAYERS,
    MELODIC_LAYERS,
    ORCHESTRAL_LAYERS,
    PIANO_LAYERS,
    UPPER_LAYERS,
    LayerEvent,
    LayerIR,
)


def test_all_layers_matches_the_dataclass():
    """Adding a layer to the model must not need a second edit here."""
    assert set(ALL_LAYERS) == set(LayerIR.event_layer_names()), (
        "ALL_LAYERS has drifted from LayerIR — a layer is in one and not the other, "
        "which is exactly how orchestral music became invisible to nine modules"
    )


def test_the_two_groups_partition_the_whole():
    assert set(PIANO_LAYERS) | set(ORCHESTRAL_LAYERS) == set(ALL_LAYERS)
    assert not set(PIANO_LAYERS) & set(ORCHESTRAL_LAYERS)


def test_every_named_group_names_real_fields():
    for group in (PIANO_LAYERS, ORCHESTRAL_LAYERS, MELODIC_LAYERS, UPPER_LAYERS, LOWER_LAYERS):
        for name in group:
            assert name in LayerIR.__dataclass_fields__, f"{name} is not a LayerIR field"


def test_upper_and_lower_cover_both_instrumentations():
    """A hand grouping that only knew the piano layers put orchestral notes in
    neither hand, so they were counted in no density measurement at all."""
    for group in (UPPER_LAYERS, LOWER_LAYERS):
        assert set(group) & set(PIANO_LAYERS), f"{group} names no piano layer"
        assert set(group) & set(ORCHESTRAL_LAYERS), f"{group} names no orchestral layer"


def test_melodic_layers_cover_both_instrumentations():
    assert "principal_line" in MELODIC_LAYERS and "foreground" in MELODIC_LAYERS


# ─── The asymmetry that made the piano-only lists never crash ────────────────


def test_the_default_asymmetry_is_still_real():
    """Piano layers default to [], orchestral ones to None.

    This is why `getattr(ir, name).extend(...)` worked on every piano layer and
    would have raised on any orchestral one — the hand-written lists never hit
    the error that would have exposed them. If this ever becomes uniform, the
    guards below are harmless; the test is here so the change is noticed.
    """
    ir = LayerIR()
    piano_defaults = {getattr(ir, n) is None for n in PIANO_LAYERS}
    orch_defaults = {getattr(ir, n) is None for n in ORCHESTRAL_LAYERS}
    assert piano_defaults == {False}, "a piano layer no longer defaults to []"
    assert orch_defaults == {True}, "an orchestral layer no longer defaults to None"


def test_ensure_layer_makes_every_layer_appendable():
    ir = LayerIR()
    for name in ALL_LAYERS:
        ir.ensure_layer(name).append(LayerEvent(bar=1, beat=1.0, pitch="C4", duration="q"))
    assert len(ir.all_events()) == len(ALL_LAYERS)


def test_all_events_sees_orchestral_material():
    ir = LayerIR(instrumentation="ensemble")
    ir.ensure_layer("foreground").append(LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"))
    ir.ensure_layer("harmonic_mass").append(LayerEvent(bar=1, beat=1.0, pitch="E4", duration="w"))
    assert len(ir.all_events()) == 2
    assert [e.pitch for e in ir.melody_line()] == ["C5"]
    assert [e.pitch for e in ir.bass_line()] == ["E4"]
