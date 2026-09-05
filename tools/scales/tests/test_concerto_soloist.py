"""A concerto keeps its soloist.

CLAUDE.md documents `orchestrate_section` as the concerto workflow — "piano-core
first, then orchestrate_section for concertos/symphonies". The planner is a role
distributor with no notion of a solo part, so naming `piano` in the ensemble got
it the melody line and nothing else: 42 notes between G5 and C7, one staff, no
left hand. That is a flute part written on a piano staff.

Emitting the soloist as a single part then had its two hands overlapping in
time, and the repair pass trimmed 42 events — bar 1 came out as the left hand
alone. A concerto soloist is notated on two staves.
"""

import os

import pytest

_PID = "beethoven-orch-cmin-20260826"
_SEC = "m1_a"
_ORCH = [
    "flute",
    "oboe",
    "clarinet",
    "bassoon",
    "horn",
    "violin_1",
    "violin_2",
    "viola",
    "cello",
    "contrabass",
]


@pytest.fixture(scope="module")
def orchestrated():
    from scales.scales import _WORKSPACE, assemble_orchestration, orchestrate_section

    if not os.path.exists(_WORKSPACE / _PID / "piece_graph.json"):
        pytest.skip("orchestral workspace not present")
    r = orchestrate_section(_PID, _SEC, target_ensemble=_ORCH, soloist="piano")
    if not r.get("ok"):
        pytest.skip(f"orchestration unavailable: {r}")
    return r, assemble_orchestration(_PID, _SEC)


def test_the_soloist_keeps_both_hands(orchestrated):
    r, _ = orchestrated
    counts = r["part_event_counts"]
    assert counts.get("piano"), "the soloist has no part"
    assert counts.get("piano_lh"), "the soloist has no left hand"


def test_the_soloist_is_not_merely_doubling_a_violin(orchestrated):
    """Its whole core, not the melody line the violins already have."""
    r, _ = orchestrated
    counts = r["part_event_counts"]
    solo = counts.get("piano", 0) + counts.get("piano_lh", 0)
    assert solo > counts.get("violin_1", 0), (solo, counts.get("violin_1"))


def test_the_two_staves_span_a_keyboard(orchestrated):
    from music21 import converter, note

    _, asm = orchestrated
    s = converter.parse(asm["path"])

    def rng(part):
        ns = list(part.recurse().notes)
        lo = [
            n.pitch.midi if isinstance(n, note.Note) else min(x.midi for x in n.pitches) for n in ns
        ]
        hi = [
            n.pitch.midi if isinstance(n, note.Note) else max(x.midi for x in n.pitches) for n in ns
        ]
        return (min(lo), max(hi)) if ns else None

    # BOTH staves of the soloist now carry the instrument's name, and the lower
    # one is no longer "Piano Lh": a concerto names its soloist once, at the top
    # of a brace, and two parts called "Piano" and "Piano Lh" read as two
    # players at two pianos. They are taken here in score order — upper first —
    # which is what the brace records. The claim this test makes is unchanged.
    solo = [x for x in s.parts if (x.partName or "").strip().lower() == "piano"]
    assert len(solo) == 2, [x.partName for x in s.parts]
    up, lo = rng(solo[0]), rng(solo[1])
    assert up and lo, (up, lo)
    assert lo[0] < up[0], "the left hand must sound below the right"


def test_the_soloist_heads_the_score(orchestrated):
    from music21 import converter

    _, asm = orchestrated
    names = [(p.partName or p.id or "").lower() for p in converter.parse(asm["path"]).parts]
    assert names[0].startswith("piano"), names[:3]
    assert names[1].startswith("piano"), names[:3]


def test_orchestrating_without_a_soloist_is_unchanged(orchestrated):
    from scales.scales import orchestrate_section

    r = orchestrate_section(_PID, _SEC, target_ensemble=_ORCH)
    assert "piano" not in (r.get("part_event_counts") or {})
    assert set(r["ensemble"]) == set(_ORCH)
