"""The readiness report must not accept the planner's own text as authorship.

`plan_readiness` checked that narrative sections exist and that at least one has
non-empty `character`. Both pass on a piece whose narrative is entirely
planner-generated: `build_form_graph` writes
`"; ".join(ROLE_INTENT[r] for r in roles)` into that field, so five sections of
default text satisfy "has authored prose".

Measured byte-for-byte, a Chopin nocturne and a Mozart andante carried identical
character on all five sections — and the readiness report called both complete.
It was reporting that the FORM's shape was present, not the PIECE's.

The piece here is built from scratch rather than copied out of `workspace/`: an
earlier version of this test copied a real piece and passed alone but failed in
the suite, because another test mutates that piece and the copy was of whatever
state it happened to be in.
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.dramatic_plan import ROLE_INTENT
from scales.models import NarrativeArc, NarrativeSection
from scales.piece_graph import PieceGraph
from scales.scales import plan_readiness

ROLES = ("establish", "depart", "retreat", "return", "close")
PID = "_narrative_readiness_probe"


def _workspace():
    """Resolved at CALL time, not import time.

    Other tests in this suite `monkeypatch.setattr(scales, "_WORKSPACE", ...)`.
    A module-level `from scales.scales import _WORKSPACE` binds a COPY, so the
    fixture would write to one directory while `plan_readiness` read another —
    which is exactly how this test passed alone and failed in the suite.
    """
    return scales_mod._WORKSPACE


def _section(i: int, role: str, character: str) -> NarrativeSection:
    return NarrativeSection(
        label=f"m1_s{i}",
        bar_start=1 + i * 4,
        bar_end=4 + i * 4,
        character=character,
        gesture=role,
    )


@pytest.fixture
def piece():
    path = _workspace() / PID
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    graph = PieceGraph()
    graph.piece_id = PID
    graph.narrative = NarrativeArc(sections=[])
    graph.save(str(path / "piece_graph.json"))
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _write(pid: str, characters):
    path = _workspace() / pid / "piece_graph.json"
    graph = PieceGraph.load(str(path))
    graph.narrative = NarrativeArc(
        sections=[_section(i, r, c) for i, (r, c) in enumerate(zip(ROLES, characters))]
    )
    graph.save(str(path))


def _narrative_complaints(pid):
    report = plan_readiness(pid)
    return [t for t in (report.get("thin") or []) if "character" in t]


def _default(role: str) -> str:
    return (ROLE_INTENT.get(role) or "").strip()


def test_an_all_default_narrative_is_reported(piece):
    _write(piece, [_default(r) for r in ROLES])
    complaints = _narrative_complaints(piece)
    assert complaints and "every section" in complaints[0]


def test_authored_prose_is_accepted(piece):
    """Falsification: the check must be quiet on a real narrative."""
    _write(piece, [f"{i}: the sea before dawn, holding its breath" for i in range(len(ROLES))])
    assert not _narrative_complaints(piece)


def test_a_partly_default_narrative_names_the_sections(piece):
    characters = [f"{i}: an intent written by hand" for i in range(len(ROLES))]
    characters[1] = _default(ROLES[1])
    _write(piece, characters)
    complaints = _narrative_complaints(piece)
    assert complaints and "1 of" in complaints[0]
    assert "m1_s1" in complaints[0]
