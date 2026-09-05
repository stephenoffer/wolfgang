"""`resolve_reference` called a 16-bar corpus "armed".

CLAUDE.md states the rule: *"A composer needs ≥3 distinct source movements and
real harmonic coverage to count as armed; `composer_coverage_tier` reports tier C
for anything thinner rather than pretending it can teach a voice."*

`composer_coverage_tier` applies it. `resolve_reference` — the function that
decides whether a request can be honoured — did not: its `armed` meant only "has
a corpus directory on disk". The two disagreed outright:

    composer_coverage_tier("bartok") -> tier C, armed False, 16 bars, 1 source
    resolve_reference("bartok")      -> armed True,  tier absent entirely

so "compose in Bartok's style" was answered as though the corpus could teach that
voice. `style_members`, two functions above, already consulted the tier — only
the direct-composer path, which is the commoner request, did not.
"""

from __future__ import annotations

import pytest

from scales.composition_brief import composer_coverage_tier
from scales.style_registry import resolve_reference

#: Measured from the indexes on disk.
THIN = {"bartok": 16, "bruckner": 27, "dvorak": 46}
RICH = ("mozart", "chopin", "palestrina", "bach")


@pytest.mark.parametrize("composer,bars", sorted(THIN.items()))
def test_a_thin_corpus_is_not_called_armed(composer, bars):
    got = resolve_reference(composer)
    if got.get("kind") != "composer":
        pytest.skip(f"{composer} no longer resolves to a composer")
    assert got["armed"] is False
    assert got["tier"] in ("C", "D")


@pytest.mark.parametrize("composer,bars", sorted(THIN.items()))
def test_the_answer_says_how_thin_and_what_to_do(composer, bars):
    note = resolve_reference(composer).get("note", "")
    assert "too thin" in note
    assert "acquire_composer" in note
    assert str(bars) in note or "bars" in note


@pytest.mark.parametrize("composer", RICH)
def test_a_real_corpus_is_still_armed(composer):
    got = resolve_reference(composer)
    assert got["armed"] is True
    assert got["tier"] in ("A", "B")


@pytest.mark.parametrize("composer", sorted(THIN) + list(RICH))
def test_the_two_functions_agree(composer):
    """The defect was disagreement, not either answer on its own."""
    resolved = resolve_reference(composer)
    if resolved.get("kind") != "composer":
        pytest.skip(f"{composer} does not resolve to a composer")
    assert resolved["armed"] is bool((composer_coverage_tier(composer) or {}).get("armed"))


def test_a_style_still_resolves_over_its_usable_members():
    """The fix must not narrow style requests, which were already honest."""
    got = resolve_reference("romantic")
    assert got["kind"] == "style"
    assert got["armed"] is True
    assert len(got["members"]) >= 3
    for thin in THIN:
        assert thin not in got["members"]


@pytest.mark.parametrize(
    "requested",
    ["arvo-part", "strauss-r", "vaughan-williams", "saint-saens", "rimsky-korsakov"],
)
def test_the_arm_it_hint_names_the_composer_that_was_asked_for(requested):
    """The hint used `base` — `low.split("-")[0]`, which exists to match
    "mozart-k331" back to "mozart". Used here it handed the user a command that
    cannot work for any hyphenated composer:

        vaughan-williams  ->  `acquire_composer.py vaughan`
        saint-saens       ->  `acquire_composer.py saint`
        arvo-part         ->  `acquire_composer.py arvo`

    A hint that names the wrong argument is worse than no hint, and hyphenated
    composers are not a corner case.
    """
    import re

    note = resolve_reference(requested).get("note", "")
    if "acquire_composer" not in note:
        pytest.skip(f"{requested} resolves to an armed reference")
    named = re.search(r"acquire_composer (\S+?)`", note)
    assert named and named.group(1) == requested


def test_the_hint_is_a_command_that_can_be_run_as_written():
    """`acquire_composer.py <name>` is not how this package is invoked; the
    module form is what CLAUDE.md documents and what works from any directory."""
    note = resolve_reference("vaughan-williams").get("note", "")
    assert "python -m scripts.acquire_composer" in note
