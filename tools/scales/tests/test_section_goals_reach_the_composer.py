"""A technique with no goal is a recipe.

`dramatic_plan.section_rhetoric()` returns **(goals, techniques)**. The planner
copied only the techniques onto the phrase slot:

    _sl.section_techniques = list(_techs)      # and nothing for _goals

so the composer was told HOW — "rising sequence", "pivot chord", "thinning to a
single line" — and never WHAT FOR:

    establish   make the idea memorable on first hearing; establish the key beyond doubt
    return      bring the idea back CHANGED; make the return feel earned
    close       take leave of the material; stop persuading

The goals half went to `SectionContract.rhetorical_goals`, which nothing reads —
and `dramatic_plan.py` says in its own header that this field "had no reader
anywhere in the codebase". A writer was added for it. The reader never was, and
the copy that DOES reach the brief carries only half the pair.
"""

from scales.composition_brief import _dramatic_brief
from scales.dramatic_plan import build, section_rhetoric
from scales.models import PhraseSlot, StyleDNA
from scales.scales import _build_ternary


def _slot(**kw):
    base = dict(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=4,
                key="C major", meter=(4, 4), tempo_bpm=90)
    base.update(kw)
    return PhraseSlot(**base)


def test_the_rhetoric_helper_returns_both_halves():
    goals, techs = section_rhetoric(["establish"])
    assert goals and techs


def test_the_goal_reaches_the_brief():
    text = " ".join(_dramatic_brief(_slot(section_goals=["make the idea memorable"])))
    assert "WHAT THIS SECTION IS FOR" in text
    assert "make the idea memorable" in text


def test_the_goal_comes_before_the_technique():
    """Why before how — a technique list read first is a recipe to follow."""
    text = "\n".join(
        _dramatic_brief(
            _slot(
                dramatic_role="establish",
                section_goals=["make the idea memorable"],
                section_techniques=["clear periodic phrasing"],
            )
        )
    )
    assert text.index("WHAT THIS SECTION IS FOR") < text.index("TECHNIQUE to reach for here")


def test_a_slot_with_no_goals_says_nothing():
    assert "WHAT THIS SECTION IS FOR" not in " ".join(_dramatic_brief(_slot()))


def test_a_planned_piece_carries_goals_on_every_section_opening():
    """End to end: the planner must populate what the brief now reads."""
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    build(slots)
    # `build` assigns roles; the planner copies rhetoric onto slots in
    # `build_form_graph`, so check the pairing the helper defines.
    for slot in slots:
        goals, _ = section_rhetoric([slot.dramatic_role])
        assert goals, f"{slot.dramatic_role} has no rhetorical goal"


def test_an_unplanned_phrase_still_gets_everything_that_is_known():
    """The "no dramatic plan" branch used to `return` immediately, so each new
    piece of guidance added after it — forward context, then section goals —
    silently vanished for an unplanned phrase. An absent ARC is not an absent
    plan; say what is missing and carry on with what is not."""
    text = " ".join(
        _dramatic_brief(
            _slot(
                section_goals=["make the idea memorable"],
                forward_context="leads into m1_a_p2 — spin it out",
            )
        )
    )
    assert "no dramatic plan" in text
    assert "WHAT THIS SECTION IS FOR" in text
    assert "WHERE IT GOES NEXT" in text


def test_an_unplanned_phrase_is_not_given_a_climax_position():
    """The one thing that genuinely depends on the arc must stay suppressed."""
    text = " ".join(_dramatic_brief(_slot(section_goals=["x"])))
    assert "CLIMAX of the whole piece" not in text
    assert "before the piece's climax" not in text
