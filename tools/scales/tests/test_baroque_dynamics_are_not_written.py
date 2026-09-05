"""A Bach invention came out with five dynamics the composer never wrote.

`ENGRAVING_STYLES["baroque"]` carried `dynamic_every_n_bars=8` — one written
dynamic every eight bars — with no justification beside it, while the
`renaissance` entry directly above states plainly "dynamics are not notated".
Measured over the corpus this system learns Baroque from:

    bach      20/20 scores carry ZERO dynamics (median 0.000/bar, max 0.000)
    corelli    1/1  zero
    handel     1/1  0.278/bar     <- the only counter-example, and n = 1

against real Mozart at 0.873/bar and real Chopin at 0.472. A 22-bar generated
invention came out with five, none of them the composer's.

The Handel file is recorded rather than dismissed: Baroque ORCHESTRAL music does
mark echo effects, so if that repertoire is armed this wants re-measuring rather
than inheriting. [[feedback_falsify_detectors_against_real_scores]].
"""

from __future__ import annotations

import pytest

from scales.expression_enricher import ENGRAVING_STYLES

#: dynamics per bar in real music, measured with music21 over the armed corpora.
REAL_DYNAMICS_PER_BAR = {
    "bach": 0.000,
    "corelli": 0.000,
    "mozart": 0.873,
    "chopin": 0.472,
}


@pytest.mark.parametrize("period", ["renaissance", "baroque"])
def test_a_period_that_does_not_notate_dynamics_is_not_given_any(period):
    style = ENGRAVING_STYLES[period]
    assert style.dynamic_every_n_bars >= 99
    assert style.hairpin_min_notes >= 99


@pytest.mark.parametrize("period", ["classical", "romantic"])
def test_a_period_that_does_notate_them_still_gets_them(period):
    """The fix must not silence Mozart, who writes 0.873 dynamics per bar."""
    style = ENGRAVING_STYLES[period]
    assert style.dynamic_every_n_bars <= 8
    assert style.hairpin_min_notes <= 8


def _bach_phrase():
    from scales.models import LayerEvent, LayerIR

    layer = LayerIR(instrumentation="solo_piano", key="D minor", meter=(4, 4), bar_count=8)
    layer.principal_line = [
        LayerEvent(bar=bar, beat=float(i + 1), pitch=p, duration="q",
                   role="structural", source_layer="principal_line")
        for bar in range(1, 9)
        for i, p in enumerate(["D5", "E5", "F5", "G5"])
    ]
    layer.bass_foundation = [
        LayerEvent(bar=bar, beat=1.0, pitch="D3", duration="w",
                   role="structural", source_layer="bass_foundation")
        for bar in range(1, 9)
    ]
    return layer


def test_the_engraver_writes_no_periodic_dynamic_into_a_bach_phrase():
    """End to end: the enricher fills only what the composer left blank, and for
    Bach a blank dynamic must stay blank."""
    from scales.expression_enricher import enrich_layer_ir
    from scales.models import LayerEvent, LayerIR

    layer = LayerIR(instrumentation="solo_piano", key="D minor", meter=(4, 4), bar_count=8)
    layer.principal_line = [
        LayerEvent(bar=bar, beat=float(i + 1), pitch=p, duration="q",
                   role="structural", source_layer="principal_line")
        for bar in range(1, 9)
        for i, p in enumerate(["D5", "E5", "F5", "G5"])
    ]
    layer.bass_foundation = [
        LayerEvent(bar=bar, beat=1.0, pitch="D3", duration="w",
                   role="structural", source_layer="bass_foundation")
        for bar in range(1, 9)
    ]
    baroque = enrich_layer_ir(layer, style="baroque")
    classical = enrich_layer_ir(_bach_phrase(), style="classical")
    # Not zero unconditionally: `add_echo_terracing` may still mark ONE echo,
    # and a literal repeat taken a step softer is the defining Baroque device —
    # it is notated, unlike the periodic dynamic this fix turned off. What must
    # not happen is a dynamic every eight bars regardless of the music.
    assert baroque.dynamics_added <= 1
    assert classical.dynamics_added > baroque.dynamics_added


def test_the_measured_rates_are_recorded_not_guessed():
    """Bach and Mozart differ by more than a factor of anything — the gate is a
    measurement, and this keeps the numbers next to the rule."""
    assert REAL_DYNAMICS_PER_BAR["bach"] == 0.0
    assert REAL_DYNAMICS_PER_BAR["mozart"] > 0.5
