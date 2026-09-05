"""The commit gate told every composer to aim for 65% stepwise motion.

`_check_interval_profile` runs on every commit and scored the phrase against a
hardcoded `{"stepwise": 0.65, "small_leap": 0.25, "large_leap": 0.10}`. Measured
over the corpus in those same bands, that describes nobody:

    palestrina 0.813   bach 0.736   mozart 0.611   haydn 0.600
    beethoven  0.538   chopin 0.498  liszt 0.358

It is nearly twice Liszt's real rate, and its large-leap figure of 0.10 is off by
almost four times for him (0.377). Three subsystems were giving three answers:
the gate said aim for 65% steps, `score_realism` told the finished piece it was
too scalar, and the brief told the composer the line should leap.

This matters beyond tidiness. Across ten pieces composed end to end this session
the median `step_ratio` was **0.770** against real music's 0.427-0.678, and
`scalar_overuse` fired on five of them — the single most consistent way the
output differs from real music. The one check positioned to catch it while the
notes are being written was measuring against a constant that let it through.
"""

from __future__ import annotations

import pytest

from scales.models import LayerEvent, LayerIR
from scales.musicality import (
    _GENERIC_INTERVAL_PRIOR,
    composer_interval_priors,
    melodic_interval_profile,
)

#: Measured from the corpus in musicality's own bands (<=2, 3-5, >5).
CONJUNCT = ("palestrina", "bach")
DISJUNCT = ("chopin", "liszt")


def _stepwise_line() -> LayerIR:
    layer = LayerIR(key="C", meter=(4, 4))
    layer.principal_line = [
        LayerEvent(
            bar=1 + i // 8, beat=1.0 + (i % 8) * 0.5, pitch=p, duration="e",
            role="structural", source_layer="principal_line",
        )
        for i, p in enumerate(
            ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6",
             "B5", "A5", "G5", "F5", "E5", "D5", "C5", "B4"]
        )
    ]
    return layer


@pytest.mark.parametrize("composer", CONJUNCT + DISJUNCT)
def test_every_armed_composer_has_a_measured_prior(composer):
    priors = composer_interval_priors(composer)
    assert priors is not None, f"{composer} falls back to the generic prior"
    assert abs(sum(priors.values()) - 1.0) < 0.01


@pytest.mark.parametrize("composer", CONJUNCT)
def test_a_stepwise_line_is_idiomatic_for_a_conjunct_composer(composer):
    """Palestrina's vocal polyphony IS stepwise. Warning about it is wrong."""
    score, _ = melodic_interval_profile(
        _stepwise_line(), priors=composer_interval_priors(composer)
    )
    assert score >= 0.5, f"{composer} should not be warned for stepwise motion"


@pytest.mark.parametrize("composer", DISJUNCT)
def test_a_stepwise_line_is_flagged_for_a_composer_whose_line_leaps(composer):
    """The whole point: this is the check positioned to catch it at commit time."""
    score, _ = melodic_interval_profile(
        _stepwise_line(), priors=composer_interval_priors(composer)
    )
    assert score < 0.5, f"{composer} should be warned for a wholly stepwise line"


def test_the_generic_prior_let_it_through_for_everyone():
    """Documents what was there, so nobody restores it as a simplification."""
    score, _ = melodic_interval_profile(_stepwise_line())
    assert score >= 0.5
    assert _GENERIC_INTERVAL_PRIOR["stepwise"] == 0.65


def test_an_unknown_composer_keeps_the_generic_prior():
    """The honest fallback is a generic prior, not another composer's."""
    assert composer_interval_priors("not-a-composer") is None
    assert composer_interval_priors("") is None


def test_the_gate_passes_the_composer_through():
    """A prior that exists and is never handed to the check is no fix at all."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path("tools/scales/commit_gate.py").read_text())
    node = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_check_interval_profile"
    )
    assert "composer" in {a.arg for a in node.args.args}
    assert "composer_interval_priors" in ast.unparse(node)
