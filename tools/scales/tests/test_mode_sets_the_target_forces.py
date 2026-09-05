"""Two modes had their target forces exactly inverted.

`reduce_to_piano` and `orchestrate` describe a TRANSFORMATION, so their
descriptions name the SOURCE:

    "reduce this symphony to piano"     -> inferred `ensemble`   (the source)
    "orchestrate this piano piece"      -> inferred `solo_piano` (the source)

Both are the opposite of what is being produced. The word-based inference was
right about the words and wrong about which end of the transformation they
describe.

The inversion matters most where it is least visible. The piano playability
check — hand span — runs ONLY for keyboard targets:

    instrumentation=solo_piano   a two-octave stretch -> 1 playability error
    instrumentation=ensemble     the same stretch     -> 0

So a reduction, whose entire purpose is to fit two hands and which is the one
output that most needs the check, was the only one never given it. And an
orchestration was being checked against a span no orchestra has.
"""

import shutil

import pytest

from scales.models import LayerEvent, LayerIR
from scales.scales import _MODE_TARGET_INSTRUMENTATION, _WORKSPACE, _load_graph, init_workspace
from scales.validator import validate_layer_ir


def _target(mode, description):
    pid = f"_t_mode_{mode}"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    try:
        init_workspace(pid, mode=mode, description=description)
        return _load_graph(pid).contract.target.instrumentation
    finally:
        shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)


def test_a_reduction_targets_the_piano_however_the_source_is_described():
    assert _target("reduce_to_piano", "reduce this symphony for full orchestra to piano") == (
        "solo_piano"
    )


def test_an_orchestration_targets_the_ensemble():
    assert _target("orchestrate", "orchestrate this solo piano prelude") == "ensemble"


def test_the_other_modes_still_read_the_request():
    """Only the two transformation modes are forced; everywhere else the words
    are the only evidence there is."""
    assert "compose_from_text" not in _MODE_TARGET_INSTRUMENTATION
    assert _target("compose_from_text", "a sacred motet for four voices") == "choir"
    assert _target("compose_from_text", "a string quartet in C") == "ensemble"
    assert _target("compose_from_text", "a nocturne for piano") == "solo_piano"


def test_an_explicit_instrumentation_still_wins_over_the_mode():
    """A caller who names the forces means it."""
    pid = "_t_mode_explicit"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    try:
        init_workspace(
            pid,
            mode="orchestrate",
            description="orchestrate this",
            params={"instrumentation": "choir"},
        )
        assert _load_graph(pid).contract.target.instrumentation == "choir"
    finally:
        shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)


# ─── Why it matters ──────────────────────────────────────────────────────────


def _playability_findings(instrumentation):
    import dataclasses

    ir = LayerIR(key="C major", meter=(4, 4), instrumentation=instrumentation, bar_count=1)
    ir.bass_foundation.append(LayerEvent(bar=1, beat=1.0, pitch=["C2", "C4"], duration="w"))
    ir.principal_line.append(LayerEvent(bar=1, beat=1.0, pitch="G5", duration="w"))
    report = validate_layer_ir(ir)
    data = dataclasses.asdict(report) if dataclasses.is_dataclass(report) else vars(report)
    return [
        item
        for value in data.values()
        if isinstance(value, list)
        for item in value
        if "playability" in str(item).lower()
    ]


def test_the_playability_check_follows_the_target():
    """A two-octave stretch in one hand: an error for a keyboard, silence for
    an ensemble. That is correct — and it is why the inverted target meant the
    reduction was never checked."""
    assert _playability_findings("solo_piano")
    assert not _playability_findings("ensemble")


@pytest.mark.parametrize("mode,expected", sorted(_MODE_TARGET_INSTRUMENTATION.items()))
def test_every_forced_mode_is_one_of_the_two_transformations(mode, expected):
    assert mode in ("reduce_to_piano", "orchestrate")
    assert expected in ("solo_piano", "ensemble")
