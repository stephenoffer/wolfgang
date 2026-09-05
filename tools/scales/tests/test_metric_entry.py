"""Metric entry: the piece decides whether it opens on the downbeat.

Measured over the corpus, 46% of Mozart's movements and 69% of Bach's open with
a pickup bar. None of the twelve pieces in ``workspace/`` ever did — the
shorthand and the engraver had supported an anacrusis all along and nothing ever
asked for one.
"""

import json
import shutil

import pytest

from scales.composition_brief import anacrusis_rate
from scales.direct_compose import compose_phrase
from scales.scales import _WORKSPACE, build_form_graph, compile_style, init_workspace


def _fresh(piece_id, composer="mozart"):
    shutil.rmtree(_WORKSPACE / piece_id, ignore_errors=True)
    init_workspace(piece_id, "compose_from_text", "t", params={"instrumentation": "solo_piano"})
    compile_style(piece_id, composer)
    build_form_graph(piece_id, form="ternary", key="C major", tempo_bpm=100, meter=(4, 4))
    return json.loads((_WORKSPACE / piece_id / "piece_graph.json").read_text())


def test_the_corpus_rate_is_measured_not_assumed():
    """A real figure, or the plan has no basis for the decision."""
    rate = anacrusis_rate("mozart")
    assert 0.2 < rate < 0.8, f"mozart anacrusis rate {rate} is not a plausible measurement"


def test_the_opening_phrase_gets_a_decided_metric_entry():
    data = _fresh("t_metric_entry")
    opening = min(data["phrases"].values(), key=lambda p: p["slot"]["bar_start"])
    assert opening["slot"]["metric_entry"] in ("anacrusis", "downbeat")
    shutil.rmtree(_WORKSPACE / "t_metric_entry", ignore_errors=True)


def test_the_decision_survives_the_save():
    """It was set on a local list of slots, not on the graph's own, so it was
    correct in memory and empty on the very next load."""
    data = _fresh("t_metric_entry_persist")
    entries = [p["slot"].get("metric_entry") for p in data["phrases"].values()]
    assert any(e for e in entries), "metric_entry was lost between planning and save"
    shutil.rmtree(_WORKSPACE / "t_metric_entry_persist", ignore_errors=True)


def test_the_decision_is_deterministic():
    """A rebuild must not silently change the music."""
    a = _fresh("t_metric_entry_det")
    b = _fresh("t_metric_entry_det")

    def first(d):
        return min(d["phrases"].values(), key=lambda p: p["slot"]["bar_start"])

    assert first(a)["slot"]["metric_entry"] == first(b)["slot"]["metric_entry"]
    shutil.rmtree(_WORKSPACE / "t_metric_entry_det", ignore_errors=True)


@pytest.mark.parametrize("meter,upbeat,expected_beat", [((4, 4), "G4q", 4.0), ((3, 4), "G4e", 3.5)])
def test_an_upbeat_right_aligns_to_the_barline(meter, upbeat, expected_beat):
    layer = compose_phrase(
        [{"rh": upbeat, "lh": "rest_q", "pickup": True}, {"rh": "C5w", "lh": "C3w"}],
        key="C major",
        meter=meter,
        bar_start=1,
    )
    assert layer.principal_line[0].beat == pytest.approx(expected_beat)
    assert layer.pickup_beats > 0
