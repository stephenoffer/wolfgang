"""A style must not be backed by a corpus too thin to teach anything.

`style_members` gated on "has a corpus directory on disk", which is not the same
question as "can this corpus anchor a brief". `composer_coverage_tier` already
answers the second one — CLAUDE.md's rule is that a thin corpus reports tier C
"rather than pretending it can teach a voice" — and nothing consulted it here.

Measured before the fix:

    modern           1 member  — bartok, 16 bars — 100% of the style
    nationalistic    4 members — dvorak 46, mussorgsky 458, rimsky-korsakov 352
                                 were 53% of its material
    impressionist    2 members — debussy 342 bars was 27%

"Compose in a modern style" was therefore anchored entirely on sixteen bars.
"""

from scales.composition_brief import composer_coverage_tier
from scales.style_registry import _STYLE_MEMBERS, resolve_reference, style_members


def test_no_style_is_anchored_on_an_unusable_corpus():
    for style in _STYLE_MEMBERS:
        for member in style_members(style):
            tier = (composer_coverage_tier(member) or {}).get("tier", "D")
            assert tier in ("A", "B"), f"{style} includes {member} at tier {tier}"


def test_a_style_with_only_stubs_reports_itself_unsupported():
    """`modern` has one member and it is a 16-bar stub. Saying so is the point:
    the alternative is composing 'in a modern style' off sixteen bars and
    calling it armed."""
    assert style_members("modern") == []
    ref = resolve_reference("modern")
    assert ref["armed"] is False
    assert not ref["members"]


def test_the_unsupported_message_still_names_what_to_acquire():
    """An honest failure has to be actionable, so the composers that WOULD make
    the style available must survive the filter that removed them."""
    ref = resolve_reference("modern")
    assert "bartok" in str(ref.get("note", "")).lower()
    assert style_members("modern", usable_only=False)


def test_a_direct_request_for_a_thin_composer_still_works():
    """Only STYLE membership is gated. Asking for Debussy by name is a decision
    the caller made with the coverage tier reported to them, not a silent
    substitution."""
    for name in ("debussy", "bartok", "corelli"):
        assert resolve_reference(name)["kind"] == "composer"


def test_the_well_armed_styles_are_untouched():
    for style, expect in (("classical", 3), ("renaissance", 2)):
        assert len(style_members(style)) == expect
