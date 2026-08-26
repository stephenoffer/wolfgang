"""The dramatic plan must give every phrase a reason to exist.

Before this module, planning produced a form skeleton and nothing else:
``narrative.sections`` was empty, ``primary_climax_section`` was blank,
``curves.tension``/``register``/``brightness`` were empty lists,
``forward_context`` was None, and ``rhetorical_goals`` had no writer or reader.
Each test here pins one thing the composer can now be told.
"""

from scales import dramatic_plan as DP
from scales.models import StyleDNA
from scales.scales import _build_sonata, _build_ternary


def _ternary():
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    info = DP.build(slots)
    return slots, info


def _sonata():
    slots = _build_sonata("D minor", 120, (4, 4), StyleDNA())
    info = DP.build(slots)
    return slots, info


# ─── Roles ──────────────────────────────────────────────────────────────────


def test_every_phrase_gets_a_dramatic_role():
    slots, _ = _ternary()
    assert all(s.dramatic_role for s in slots)


def test_section_abbreviations_resolve_to_the_right_arc():
    """'m1_retr' must be recognised as a retransition, or its job comes out as
    'establish' when what it has to do is subside."""
    slots, _ = _ternary()
    retr = [s for s in slots if s.section_id.endswith("retr")]
    assert retr and retr[0].dramatic_role == DP.RETREAT


def test_a_development_gets_a_crisis():
    slots, info = _sonata()
    roles = [s.dramatic_role for s in slots if "dev" in s.section_id]
    assert DP.CRISIS in roles
    assert "dev" in (info["climax_phrase"] or "")


# ─── Climax and arc ─────────────────────────────────────────────────────────


def test_exactly_one_phrase_is_the_climax():
    slots, _ = _ternary()
    assert sum(1 for s in slots if s.climax_distance == 0) == 1


def test_tension_peaks_at_the_climax_and_relaxes_at_the_close():
    slots, _ = _ternary()
    peak = next(s for s in slots if s.climax_distance == 0)
    close = next(s for s in slots if s.dramatic_role == DP.CLOSE)
    assert max(peak.curves.tension) > max(close.curves.tension)


def test_the_climax_is_the_loudest_and_the_close_the_quietest():
    slots, _ = _sonata()
    peak = next(s for s in slots if s.climax_distance == 0)
    close = next(s for s in slots if s.dramatic_role == DP.CLOSE)
    opening = slots[0]
    assert max(peak.curves.energy) > max(opening.curves.energy)
    assert max(peak.curves.energy) > max(close.curves.energy)


def test_register_arc_is_populated_for_every_phrase():
    slots, _ = _ternary()
    assert all(len(s.curves.register) == s.bar_count for s in slots)


# ─── Dynamic shape ──────────────────────────────────────────────────────────


def test_dynamic_shape_is_not_flat_within_a_phrase():
    """A per-function default returned a CONSTANT for continuation phrases, so
    scaling it by a per-phrase constant left the climax an unchanging mf."""
    slots, _ = _ternary()
    for s in slots:
        if s.bar_count >= 4:
            assert len(set(s.curves.energy)) > 1, f"{s.phrase_id} has a flat energy curve"


def test_building_roles_rise_and_subsiding_roles_fall():
    slots, _ = _sonata()
    rising = [s for s in slots if s.dramatic_role in (DP.INTENSIFY, DP.CRISIS, DP.DEPART)]
    falling = [s for s in slots if s.dramatic_role in (DP.RETREAT, DP.CLOSE)]
    assert rising and falling
    for s in rising:
        assert s.curves.energy[-1] >= s.curves.energy[0]
    for s in falling:
        assert s.curves.energy[-1] <= s.curves.energy[0]


def test_articulation_is_populated():
    slots, _ = _ternary()
    assert all(s.curves.articulation for s in slots)


# ─── Returns ────────────────────────────────────────────────────────────────


def test_returns_get_a_concrete_strategy():
    slots, _ = _ternary()
    returns = [s for s in slots if s.dramatic_role == DP.RETURN]
    assert returns
    assert all(s.return_strategy and s.return_strategy_detail for s in returns)


def test_successive_returns_do_not_reuse_one_device():
    slots, _ = _sonata()
    strategies = [s.return_strategy for s in slots if s.return_strategy]
    assert len(strategies) >= 2
    assert len(set(strategies)) == len(strategies)


def test_no_return_is_told_to_merely_ornament():
    """The first strategy used to be 'ornamented', directly contradicting the
    warning printed beside it that a return must not be the statement plus
    ornaments."""
    slots, _ = _ternary()
    first = next(s for s in slots if s.return_strategy)
    assert first.return_strategy != "ornamented"


# ─── Continuity and key ─────────────────────────────────────────────────────


def test_every_phrase_knows_what_follows_it():
    slots, _ = _ternary()
    assert all(s.forward_context for s in slots)
    assert "nothing follows" in slots[-1].forward_context


def test_a_modulating_phrase_gets_a_pivot_hint():
    slots, _ = _ternary()
    arriving = [s for s in slots if s.key_motion == "arrive"]
    assert arriving
    assert any("common to both" in (s.pivot_hint or "") for s in arriving)


def test_section_rhetoric_differs_by_role():
    goals_a, techs_a = DP.section_rhetoric([DP.ESTABLISH])
    goals_d, techs_d = DP.section_rhetoric([DP.CRISIS])
    assert goals_a and goals_d and goals_a != goals_d
    assert techs_a != techs_d


# ─── Harmony follows the role ───────────────────────────────────────────────


def test_a_statement_is_not_built_out_of_borrowed_chords():
    """The B-flat major opening was planned as `I - iv - viio - V` — half its
    bars borrowed, five times the rate Mozart uses — while the same brief said
    "diatonic harmony" two lines above it.

    Note what this does NOT assert. The first version of this test demanded zero
    mixture in a statement, and measuring 3,964 real Mozart bars falsified it:
    mixture appears in 10.7% of his opening bars, indistinguishable from its
    10.9% rate mid-phrase. The defect was rate, not presence.
    """
    from scales.progression_model import _is_chromatic, corpus_harmony_plan

    for seed in range(1, 16):
        plan = corpus_harmony_plan("mozart", "", "PAC", 6, "Bb major", seed=seed, role="establish")
        borrowed = [r for r in plan if _is_chromatic(r, "major")]
        assert len(borrowed) <= 1, f"seed {seed}: {len(borrowed)} borrowed in {plan}"


def test_the_chromatic_ceiling_sits_above_what_mozart_actually_does():
    """A cap below the measured corpus rate would fight real music. Every role's
    ceiling must leave room for the 10.6% mixture rate measured over the
    corpus."""
    from scales.progression_model import _DEFAULT_CHROMATIC_SHARE, _ROLE_CHROMATIC_SHARE

    _MEASURED_MOZART_RATE = 0.106
    for role, share in _ROLE_CHROMATIC_SHARE.items():
        assert share > _MEASURED_MOZART_RATE, f"{role} ceiling {share} is below the corpus rate"
    assert _DEFAULT_CHROMATIC_SHARE > _MEASURED_MOZART_RATE


def test_an_unstable_role_may_reach_further_for_colour():
    from scales.progression_model import _ROLE_CHROMATIC_SHARE as SH

    assert SH["crisis"] > SH["establish"]
    assert SH["depart"] > SH["confirm"]


def test_mode_mixture_counts_as_chromatic_in_a_major_key():
    """`iv` and `VI` carry no accidental in their own symbol, so a test for
    "b"/"#" called the borrowed minor subdominant diatonic."""
    from scales.progression_model import _is_chromatic

    assert _is_chromatic("iv", "major")
    assert _is_chromatic("VI", "major")
    assert not _is_chromatic("IV", "major")
    assert not _is_chromatic("vi", "major")
    # In minor the raised leading-tone dominant is normal practice, not colour.
    assert not _is_chromatic("V", "minor")
    assert not _is_chromatic("iv", "minor")


def test_planner_hands_the_role_to_the_harmony_sampler():
    """role_for() must agree with the role the plan actually assigns, or the
    harmony is sampled for a phrase that turns out to be doing something else."""
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    DP.build(slots)
    counters = {}
    for s in slots:
        counters[s.section_id] = counters.get(s.section_id, 0) + 1
        assert s.dramatic_role == DP.role_for(s.section_id, counters[s.section_id] - 1)
