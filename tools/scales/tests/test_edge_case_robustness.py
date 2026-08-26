"""Every analysis entry point must survive the material it will actually see.

Music code meets empty phrases, one-note phrases, rests-only phrases, malformed
meters and missing keys constantly — a partially-written phrase, a corpus record
that failed to parse, a slot initialised but not filled.

A sweep of every public function in the analysis modules against nine such cases
found **12 crashes**, and all twelve were one bug: `Fraction(int(meter[0]) * 4,
int(meter[1]))` computed inline, which for a zero denominator makes
`Fraction(0, 0)` and raises. Twenty-one places in the codebase did that
arithmetic inline. It now goes through one guarded `duration.bar_duration`,
because duplicated inline arithmetic is this repository's most reliable bug
source — four of the session's findings were instances of it.

This test is the sweep, kept.
"""

import importlib
import inspect

import pytest

from scales.models import LayerEvent, LayerIR

_MODULES = [
    "counterpoint",
    "voicing",
    "cadence_analysis",
    "expression_enricher",
    "ornament_realization",
    "musical_report",
    "craft_checker",
    "musicality",
    "theme_planner",
    "performance_renderer",
    "orchestration_planner",
]

# Entry points come in three shapes, and testing only the first left three
# modules unswept — which the "no entry points found" assertion caught.
_LAYER_ARGS = {"layer_ir", "layer", "theme", "ir", "source", "merged"}
_GRAPH_ARGS = {"graph", "piece_graph"}
# A list of events or sounding spans...
_EVENTS_ARGS = {"events", "spans"}
# ...versus a mapping of instrument -> events. Feeding a list where a dict is
# expected raises, and correctly so: that is a caller bug, not degenerate data,
# and the lesson from this session is that programming errors must reach the
# programmer rather than being absorbed into an empty result.
_MAPPING_ARGS = {"parts"}


def _one_note():
    ir = LayerIR(key="C major", meter=(4, 4))
    ir.principal_line = [LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q")]
    return ir


def _cases():
    def empty():
        return LayerIR()

    def rests_only():
        ir = LayerIR(key="C major", meter=(4, 4))
        ir.principal_line = [
            LayerEvent(bar=1, beat=1.0 + i, pitch="rest", duration="q") for i in range(4)
        ]
        return ir

    def bad_meter():
        ir = _one_note()
        ir.meter = (0, 0)  # the case that took out twelve entry points
        return ir

    def bad_key():
        ir = _one_note()
        ir.key = ""
        return ir

    def unreadable_pitches():
        ir = LayerIR(key="C major", meter=(4, 4))
        ir.principal_line = [
            LayerEvent(bar=1, beat=1.0, pitch="H9", duration="q"),
            LayerEvent(bar=1, beat=2.0, pitch=[], duration="q"),
            LayerEvent(bar=1, beat=3.0, pitch=None, duration="q"),
        ]
        return ir

    def unknown_duration():
        ir = _one_note()
        ir.principal_line[0].duration = "???"
        return ir

    def negative_bar():
        ir = _one_note()
        ir.principal_line[0].bar = -5
        return ir

    def long_piece():
        ir = LayerIR(key="C major", meter=(4, 4))
        ir.principal_line = [
            LayerEvent(bar=b, beat=1.0, pitch="C5", duration="q") for b in range(1, 400)
        ]
        return ir

    return {
        "empty": empty,
        "one_note": _one_note,
        "rests_only": rests_only,
        "bad_meter": bad_meter,
        "bad_key": bad_key,
        "unreadable_pitches": unreadable_pitches,
        "unknown_duration": unknown_duration,
        "negative_bar": negative_bar,
        "long_piece": long_piece,
    }


class _EmptyGraph:
    """A PieceGraph-shaped object with nothing in it."""

    piece_id = ""
    phrases: dict = {}
    principal_theme_surface = None
    principal_theme_id = ""
    style_dna = None


def _entry_points(module_name):
    """Every public function taking a whole phrase, graph or event list first.

    Yields (name, fn, kind) so the caller knows which family of degenerate
    inputs to feed it.
    """
    module = importlib.import_module(f"scales.{module_name}")
    for name, fn in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or fn.__module__ != f"scales.{module_name}":
            continue
        params = list(inspect.signature(fn).parameters.values())
        if not params:
            continue
        first = params[0].name
        kind = (
            "layer" if first in _LAYER_ARGS
            else "graph" if first in _GRAPH_ARGS
            else "events" if first in _EVENTS_ARGS
            else "mapping" if first in _MAPPING_ARGS
            else None
        )
        if kind is None:
            continue
        required_after_first = [
            p
            for p in params[1:]
            if p.default is inspect.Parameter.empty
            and p.kind in (p.POSITIONAL_OR_KEYWORD, p.POSITIONAL_ONLY)
        ]
        if required_after_first:
            continue
        yield name, fn, kind


@pytest.mark.parametrize("module_name", _MODULES)
def test_no_analysis_entry_point_crashes_on_degenerate_material(module_name):
    failures = []
    checked = 0
    layer_cases = _cases()
    # Degenerate but correctly SHAPED input. A list where a dict is expected is
    # a caller bug and must raise; these are the empty and near-empty cases a
    # correct caller genuinely produces.
    event_cases = {"empty": lambda: []}
    mapping_cases = {
        "empty": lambda: {},
        "instrument_with_no_events": lambda: {"flute": []},
        "events_missing_fields": lambda: {"flute": [{}]},
    }
    graph_cases = {"empty_graph": _EmptyGraph}
    for fn_name, fn, kind in _entry_points(module_name):
        cases = (
            layer_cases if kind == "layer"
            else graph_cases if kind == "graph"
            else mapping_cases if kind == "mapping"
            else event_cases
        )
        for case_name, make in cases.items():
            checked += 1
            try:
                fn(make())
            except Exception as exc:  # noqa: BLE001 - the whole point is to catch any
                failures.append(f"{fn_name}({case_name}) -> {type(exc).__name__}: {exc}")
    assert checked, f"no entry points found in {module_name} — the sweep is not running"
    assert not failures, "\n".join(failures)


def test_a_malformed_meter_never_divides_by_zero():
    """The single root cause behind all twelve original crashes."""
    from scales.duration import bar_duration, beats_per_bar

    for meter in [(0, 0), (4, 0), (0, 4), (-2, 4), (3,), (), None, "", ("x", "y")]:
        assert bar_duration(meter) > 0, meter
        assert beats_per_bar(meter) > 0, meter


def test_a_valid_meter_is_still_computed_correctly():
    """A guard that returns a default for everything would also pass the above."""
    from scales.duration import bar_duration

    assert bar_duration((4, 4)) == 4
    assert bar_duration((3, 4)) == 3
    assert bar_duration((6, 8)) == 3
    assert bar_duration((4, 2)) == 8
    assert bar_duration((12, 8)) == 6
