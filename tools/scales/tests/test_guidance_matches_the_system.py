"""The guidance the agent reads must describe the system it is driving.

The composer reads `note-writing-craft.md` and the skill files, and acts on
what they say. Every gap between those documents and the code is a capability
the agent will not use or an instruction it will follow into a wall.

Three kinds of drift, all of which had happened:

- **A brief section nobody is told about.** Ten sections of the composition
  brief were absent from the craft doc's "read every section" list, including
  the two carrying the composer's own named idioms and the corpus's real
  gestures. A section the composer does not know exists is a section it skips.
- **A capability the docs do not mention.** `br`/`dbr`/`lo` were added to the
  duration table and the grammar table still stopped at the dotted whole.
- **A table that disagrees with its implementation.** The revision operations
  offered to the critic, and the gate diagnostics a composer is told to read.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_CRAFT = Path(".claude/skills/w-compose/references/note-writing-craft.md")
_CRITIC = Path(".claude/agents/music-critic.md")


def _craft() -> str:
    if not _CRAFT.exists():
        pytest.skip("craft reference not present")
    return _CRAFT.read_text()


@pytest.mark.parametrize(
    "section",
    [
        "CREATIVE INTENT",
        "PRINCIPAL THEME",
        "CHORD FRAME",
        "TRANSITION IN",
        "NAMED GESTURES",
        "CORPUS GESTURES",
        "RHYTHMIC FINGERPRINT",
        "COMPOSER FINGERPRINTS",
        "STYLE DOCTRINE",
        "PHRASE SHAPE",
        "CADENCE PATTERN",
        "TEXTURE TRANSITIONS",
        "LH VOCABULARY",
        "EXEMPLARS",
        "TARGET STATS",
        "AVOID",
    ],
)
def test_every_brief_section_is_named_in_the_guidance(section):
    assert section in _craft(), (
        f"the brief renders a {section} section and the craft doc never mentions it — "
        "a section the composer does not know exists is a section it skips"
    )


@pytest.mark.parametrize("code", ["br", "dbr", "lo", "trip_e", "quint_s", "sept_s", "ddh", "dw"])
def test_every_duration_code_the_grammar_offers_is_real(code):
    from scales.duration import DURATION_VALUES

    assert code in DURATION_VALUES, f"the docs offer `{code}` and the table has no such code"


def test_the_long_durations_are_documented():
    """Added to the table and absent from the grammar table for a while."""
    craft = _craft()
    assert "`br`" in craft and "breve" in craft


def test_every_blocking_gate_error_is_in_the_diagnostics_table():
    """A composer told only about `meter` cannot act on `unwritable_tokens`."""
    craft = _craft()
    for diagnostic in ("meter", "brief_not_fetched", "brief_insufficient", "unwritable_tokens"):
        assert f"`{diagnostic}`" in craft, f"{diagnostic} blocks a commit and is undocumented"


def test_the_shorthand_suffixes_in_the_docs_all_parse():
    from scales.direct_compose import (
        _ARTICULATIONS,
        _DYNAMICS,
        _EXPRESSIONS,
        _ORNAMENTS,
        _PEDALS,
        _TECHNIQUES,
    )

    known = (
        set(_ORNAMENTS)
        | set(_ARTICULATIONS)
        | set(_DYNAMICS)
        | set(_TECHNIQUES)
        | set(_PEDALS)
        | set(_EXPRESSIONS)
    )
    craft = _craft()
    offered = {
        m.group(1)
        for m in re.finditer(r"`:([a-z_0-9]+)", craft)
        if not m.group(1).startswith("xxx")
    }
    unknown = {
        s
        for s in offered
        if s not in known
        # `:fin3` and the bare `:3` are both fingerings; the parser takes either.
        and not (s.startswith("fin") and s[3:].isdigit())
        and not (s.isdigit() and len(s) <= 2)
    }
    assert not unknown, f"the docs offer suffixes the parser does not know: {sorted(unknown)}"


def test_the_critic_is_offered_exactly_the_operations_that_exist():
    if not _CRITIC.exists():
        pytest.skip("critic guidance not present")
    from scales.scales import _REVISION_OPS

    text = _CRITIC.read_text()
    for op in _REVISION_OPS:
        assert f"`{op}`" in text, f"{op} is implemented and never offered to the critic"


def test_the_realism_detectors_a_composer_may_see_are_explained():
    """The critic and the composer both read these names; an unexplained
    finding is one nobody can act on."""
    craft = _craft()
    for detector in (
        "cadence_formula",
        "scalar_overuse",
        "articulation_absent",
        "tie_absent",
        "notation_spam",
        "accompaniment_monoculture",
    ):
        assert detector in craft, f"{detector} can be reported and is undocumented"
