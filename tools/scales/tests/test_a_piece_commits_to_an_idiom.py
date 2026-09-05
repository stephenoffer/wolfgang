"""A piece is one movement, and a movement commits.

Scheduling the accompaniment from a composer's POOLED idiom distribution changes
idiom about twice as often as he does. Measured over each composer's own
movements, the median gives its top accompaniment 76.2% of its bars for Chopin,
54.4% for Bach and 36.4% for Beethoven — against pooled figures of 44.8%, 41.5%
and 20.9%. Three of four generated pieces scored below their composer's own p25
for concentration before this.

The fix is not to average movements: averaging concentrations reproduces the
same flattening one level down. `movement_idiom_mix` returns an ACTUAL
movement's distribution — the one sitting at the median concentration.
"""

import pytest

from scales.composition_brief import movement_idiom_mix

pytestmark = pytest.mark.calibration


def test_a_movement_is_more_concentrated_than_the_composer():
    from scales.style_resolver import StyleResolver

    for composer in ("chopin", "bach", "beethoven"):
        mix = movement_idiom_mix(composer)
        pooled = StyleResolver().resolve_single(composer).lh_distribution or {}
        if not mix or not pooled:
            continue
        idioms = mix.get("idioms") or {}
        if not idioms:
            continue
        movement_top = max(idioms.values()) / (sum(idioms.values()) or 1)
        pooled_top = max(pooled.values()) / (sum(pooled.values()) or 1)
        assert movement_top > pooled_top, (
            f"{composer}: a movement ({movement_top:.3f}) should commit harder "
            f"than the corpus ({pooled_top:.3f})"
        )


def test_the_mix_is_a_real_movement_not_an_average():
    """Averaging concentrations is the defect, not the fix — an averaged mix has
    no `source` because no movement produced it."""
    mix = movement_idiom_mix("chopin")
    if not mix:
        pytest.skip("chopin corpus not present")
    assert mix.get("source"), "the mix must name the movement it came from"
    assert mix.get("spread"), "a caller needs the spread to score against"


def test_the_scheduler_uses_the_movement_mix():
    """The wiring, not the measurement — a correct accessor nothing reads is the
    defect this repo finds most often."""
    import inspect

    from scales import scales as S

    source = inspect.getsource(S._default_texture_plan)
    assert "movement_idiom_mix" in source, (
        "the texture planner is still scheduling from the pooled distribution"
    )


def test_an_unmeasurable_composer_falls_back_to_the_pooled_distribution():
    assert movement_idiom_mix("nobody_at_all") in (None, {}, )


# ─── a run crosses a phrase opening ──────────────────────────────────────────


def test_a_continuing_phrase_inherits_the_accompaniment():
    """Every phrase re-picked its idiom from the ranked list, so a run could
    never outlast one phrase — and 52-66% of real runs of eight bars or more DO
    cross a phrase opening, the median crossing exactly one."""
    from scales.scales import _default_texture_plan
    from scales.style_resolver import StyleResolver

    style = StyleResolver().resolve_single("mozart")
    # An idiom the planner would actually schedule — inheriting one it has
    # filtered out (below the 5% floor, or `silence`) is correctly refused, so
    # the fixture has to name a real option or it tests the refusal instead.
    options = [
        t
        for t, share in sorted((style.lh_distribution or {}).items(), key=lambda kv: -kv[1])
        if share >= 0.05 and t != "silence"
    ]
    if len(options) < 2:
        pytest.skip("mozart pack has too few schedulable idioms")
    inherited = options[-1]
    plan = _default_texture_plan(
        style, "continuation", "none", 4, (4, 4), seed=9, prev_lh_texture=inherited
    )
    if not plan:
        pytest.skip("no texture plan")
    assert plan[0].lh_texture == inherited, (
        f"a continuation should carry the {inherited} it inherited, got {plan[0].lh_texture}"
    )


def test_a_statement_does_not_inherit():
    """A presentation, a contrasting theme and a return each STATE something and
    should be free to state it in a new accompaniment."""
    from scales.scales import _default_texture_plan
    from scales.style_resolver import StyleResolver

    style = StyleResolver().resolve_single("mozart")
    for function in ("presentation", "contrasting_theme", "return"):
        plan = _default_texture_plan(
            style, function, "none", 4, (4, 4), seed=9, prev_lh_texture="pedal_point"
        )
        if plan and len(plan) and plan[0].lh_texture == "pedal_point":
            # Only a failure if walking_bass was not what it would have picked anyway.
            without = _default_texture_plan(style, function, "none", 4, (4, 4), seed=9)
            assert without and without[0].lh_texture == "pedal_point", (
                f"{function} inherited when it should state afresh"
            )


def test_an_unschedulable_inherited_idiom_is_refused():
    """`silence` is a real corpus label and not something to plan as a phrase's
    accompaniment — inheriting it would plan a phrase with none."""
    from scales.scales import _default_texture_plan
    from scales.style_resolver import StyleResolver

    style = StyleResolver().resolve_single("mozart")
    plan = _default_texture_plan(
        style, "continuation", "none", 4, (4, 4), seed=9, prev_lh_texture="silence"
    )
    if plan:
        assert plan[0].lh_texture != "silence"


def test_the_plan_holds_an_idiom_longer_than_one_bar():
    """The whole point of the tail: a plan whose longest run is 1 changes
    accompaniment every bar, which no composer does."""
    from scales.scales import _build_ternary
    from scales.style_resolver import StyleResolver

    style = StyleResolver().resolve_single("mozart")
    slots = _build_ternary("C major", 92, (4, 4), style)
    seq = [bp.lh_texture for s in slots for bp in (getattr(s, "texture_plan", None) or [])]
    if len(seq) < 8:
        pytest.skip("plan too short")
    longest = best = 1
    for a, b in zip(seq, seq[1:]):
        best = best + 1 if a == b else 1
        longest = max(longest, best)
    assert longest >= 4, f"longest run is {longest} bars: {seq[:20]}"
