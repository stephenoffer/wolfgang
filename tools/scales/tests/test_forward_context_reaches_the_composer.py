"""The composer must know where the phrase is GOING, not only where it came from.

`dramatic_plan.link_forward_context` exists because "forward_context existed on
the model and was never populated, so no phrase knew what it was leading into".
It populates the field. `test_every_phrase_knows_what_follows_it` asserts it is
populated. **Nothing ever read it.**

The brief carried TRANSITION IN — the previous phrase's exit — and nothing about
the next one, while the field held exactly that, per phrase, in prose:

    leads into m1_a_p2 (continuation, extend) in Eb major — carry the idea
    further than its first statement — spin it out, do not restate it

A phrase-composer works in an isolated context and cannot see its neighbours.
This is the information that stops a phrase being a well-formed dead end, and it
was computed, tested, saved, and discarded — the same "correct analysis wired to
nothing" shape recorded in `project_correct_analysis_wired_to_nothing`.
"""

from scales.composition_brief import _dramatic_brief
from scales.dramatic_plan import build
from scales.models import PhraseSlot, StyleDNA
from scales.scales import _build_ternary


def _slot(**kw):
    base = dict(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=4,
                key="C major", meter=(4, 4), tempo_bpm=90)
    base.update(kw)
    return PhraseSlot(**base)


def test_the_forward_context_is_shown():
    text = " ".join(_dramatic_brief(_slot(forward_context="leads into m1_a_p2 — spin it out")))
    assert "WHERE IT GOES NEXT" in text
    assert "spin it out" in text


def test_a_phrase_with_no_forward_context_says_nothing():
    """Falsification: no invented text when the planner has not run."""
    assert "WHERE IT GOES NEXT" not in " ".join(_dramatic_brief(_slot()))


def test_every_planned_phrase_gets_one():
    """The planner fills all of them, so the brief should carry all of them."""
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    build(slots)
    missing = [s.phrase_id for s in slots if "WHERE IT GOES NEXT" not in " ".join(_dramatic_brief(s))]
    assert not missing, f"phrases with no forward line: {missing}"


def test_the_last_phrase_is_told_that_nothing_follows():
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    build(slots)
    text = " ".join(_dramatic_brief(slots[-1]))
    assert "nothing follows" in text


def test_it_names_the_phrase_that_follows():
    """Vague continuity advice is what the brief already had; the value here is
    that it names the actual next phrase and what that phrase must do."""
    slots = _build_ternary("F major", 90, (4, 4), StyleDNA())
    build(slots)
    text = " ".join(_dramatic_brief(slots[0]))
    assert slots[1].phrase_id in text


def test_an_unplanned_phrase_still_learns_where_it_goes():
    """The two are independent: a slot can know what follows without anyone
    having decided where the piece peaks. The "no dramatic plan" notice used to
    `return` before the forward line, dropping the one thing still true."""
    text = " ".join(_dramatic_brief(_slot(forward_context="leads into m1_b_p1 — leave home")))
    assert "no dramatic plan" in text
    assert "WHERE IT GOES NEXT" in text
    assert "leave home" in text
