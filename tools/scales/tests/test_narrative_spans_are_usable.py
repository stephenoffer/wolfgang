"""A narrative section that covers no bars reaches no phrase.

`_creative_intent` matches a section to a phrase with
`s.bar_start <= phrase.bar_start <= s.bar_end`. So a span that is inverted, or
was never given at all, matches nothing — the section is stored, counted in
`sections_stored`, and silently reaches no phrase.

Missing keys fall through to the dataclass defaults, which is how a section with
no bar range comes back as a confident 1-8 covering the wrong music.

`save_narrative` already warned about a missing `character` (the field Addendum 45
showed the whole brief leans on). It said nothing about the span, which is the
other way the same section can be inert.
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.scales import init_workspace, save_narrative

PID = "_narrative_span_probe"
GOOD = {"id": "a", "label": "A", "bar_start": 1, "bar_end": 8, "character": "the sea before dawn"}


@pytest.fixture
def piece():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="a piece in C major")
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_a_well_formed_section_is_not_complained_about(piece):
    """Falsification first: a check that fires on correct input is noise."""
    assert not save_narrative(piece, sections=[GOOD])["warning"]


def test_an_inverted_span_is_reported(piece):
    bad = dict(GOOD, bar_start=9, bar_end=4)
    result = save_narrative(piece, sections=[bad])
    assert result["sections_with_an_unusable_bar_range"]
    assert "bar_end is before bar_start" in str(result["sections_with_an_unusable_bar_range"])


def test_a_missing_span_is_reported_rather_than_invented(piece):
    """Without this the section is stored as bars 1-8 — a range nobody chose."""
    result = save_narrative(piece, sections=[{"id": "a", "character": "x"}])
    assert result["sections_with_an_unusable_bar_range"]
    assert "no bar range given" in str(result["sections_with_an_unusable_bar_range"])


def test_the_report_names_the_section(piece):
    result = save_narrative(piece, sections=[dict(GOOD, id="the-storm", bar_start=9, bar_end=4)])
    assert "the-storm" in str(result["sections_with_an_unusable_bar_range"])


def test_both_kinds_of_warning_can_appear_together(piece):
    """A section can be inert for two reasons at once, and both matter."""
    result = save_narrative(piece, sections=[{"id": "a", "bar_start": 9, "bar_end": 4}])
    assert result["sections_missing_character"]
    assert result["sections_with_an_unusable_bar_range"]
    assert "character" in result["warning"] and "cover no bars" in result["warning"]


def test_the_section_is_still_stored(piece):
    """A warning, not a refusal — the planner may be mid-edit."""
    assert save_narrative(piece, sections=[dict(GOOD, bar_start=9, bar_end=4)])["sections_stored"] == 1
