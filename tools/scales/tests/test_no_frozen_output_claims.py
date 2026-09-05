"""Guidance must not assert frozen facts about generated output.

The brief and the agent docs both carried hard-coded claims about "the last
generated piece" — zero articulations, zero ties, seven of nine identical
cadences, a 19-semitone span, `:arp`/`:ped` never used. Measured against the
piece whose brief printed them: 19 articulations, 2 ties, 82 pedal marks, 4
rolled chords, and 5 of 9 (not 7 of 9) repeated closings.

A constant cannot know what the current piece has done. Claims like these read
as diagnosis, go stale silently, and spend the credibility of the real corpus
figures they are bundled with — which is why the corpus numbers themselves stay
and only the assertions about output are gone.

This test is the propagation guard: the same claim was restated in six places
across four documents, and fixing the brief alone left five of them live.
"""

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]

# Phrasings that assert something about what this system has produced.
FROZEN = re.compile(
    r"the last (generated|piece)|last piece's|never yet used|measurably never done",
    re.I,
)

DOCS = sorted(p for p in (ROOT / ".claude").rglob("*.md") if p.is_file())


def test_there_are_docs_to_check():
    """A glob that matches nothing would pass every assertion below."""
    assert len(DOCS) > 5


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_no_doc_asserts_a_frozen_fact_about_generated_output(doc):
    hits = [
        f"{doc.relative_to(ROOT)}:{i}: {line.strip()[:90]}"
        for i, line in enumerate(doc.read_text().splitlines(), 1)
        if FROZEN.search(line)
    ]
    assert not hits, "frozen claim about generated output:\n" + "\n".join(hits)


def test_the_brief_constant_is_clean_too():
    from scales.composition_brief import _MINDSET

    assert not FROZEN.search(_MINDSET)
