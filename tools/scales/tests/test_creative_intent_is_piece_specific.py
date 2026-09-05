"""The one line the composer is told to start from must be about THIS piece.

`_creative_intent`'s docstring says it "leads with the agent's OWN authored prose
(section.character ...) — the dramatic event that drives the notes ... (Authoring
beats bucketing.)" But `build_form_graph` fills that field itself:

    character = "; ".join(ROLE_INTENT[r] for r in roles)

so unless someone calls `save_narrative`, the field it treats as authored prose is
a bucket label wearing prose clothes. Measured on two finished pieces:

    chopin-nocturne-ebmaj  vs  mozart-andante-bb
    narrative character, all 5 sections: BYTE-IDENTICAL

The phrase-composer is told CREATIVE INTENT is "the feeling that should choose
the notes. Start here, not from the stats." Boilerplate presented as the piece's
identity is worse than an empty field, which would at least prompt for one.
"""

from scales.composition_brief import _character_is_role_derived
from scales.dramatic_plan import ROLE_INTENT


def test_planner_generated_character_is_recognised():
    roles = ["establish", "extend", "confirm"]
    character = "; ".join(dict.fromkeys((ROLE_INTENT.get(r) or "").strip() for r in roles))
    gesture = " then ".join(roles)
    assert _character_is_role_derived(character, gesture)


def test_a_semicolon_inside_one_role_intent_does_not_fool_it():
    """The first version split `character` on ';' — and several ROLE_INTENT
    values contain a semicolon, so it returned False for every real piece and
    the check silently did nothing."""
    intent = ROLE_INTENT.get("establish", "")
    assert ";" in intent, "fixture assumes a multi-clause role intent exists"
    assert _character_is_role_derived(intent, "establish")


def test_real_authored_prose_is_left_alone():
    written = "the sea before dawn: flat, grey, and holding its breath"
    assert not _character_is_role_derived(written, "establish then extend")


def test_prose_that_merely_contains_a_role_intent_is_still_authored():
    intent = ROLE_INTENT.get("establish", "")
    assert not _character_is_role_derived(intent + " — but hushed, as if overheard", "establish")


def test_an_empty_character_is_not_role_derived():
    assert not _character_is_role_derived("", "establish")
    assert not _character_is_role_derived(None, "establish")


def test_two_different_pieces_do_not_get_the_same_intent():
    """The end-to-end property. Both briefs used to print the same sentence."""
    from scales.scales import get_composition_brief

    def intent(pid, composer):
        text = get_composition_brief(pid, "m1_a_p1", composer=composer)
        return next((ln for ln in text.split("\n") if ln.startswith("CREATIVE INTENT")), "")

    a = intent("chopin-nocturne-ebmaj-20260826", "chopin")
    b = intent("mozart-andante-bb-20260826", "mozart")
    assert a and b
    assert a != b
