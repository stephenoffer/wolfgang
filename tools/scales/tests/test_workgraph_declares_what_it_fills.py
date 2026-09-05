"""A declared structure nothing fills should say so.

`WorkGraph` declares five cross-movement structures — `theme_families`,
`climax_reservations`, `cross_movement_recalls`, `orchestral_macro_arc`,
`cyclic_obligations` — 24 fields across five dataclasses. **Nothing in the
codebase writes any of them.** `init_work`, whose docstring says "this is WHERE
Wolfgang decides the symphony's dramatic destiny", populates only
`emotional_narrative` and `finale_payoff`.

That is the dead-parameter defect (Addenda 57-58) one layer down: a data model
implying a capability the code does not have. Reporting it is not a fix — the
feature is unimplemented either way — but a caller planning a symphony can now
tell that the cyclic material they described is not being tracked anywhere,
instead of assuming a populated field exists because the type does.
"""

import shutil

import pytest

from scales import scales as scales_mod
from scales.models import WorkGraph
from scales.scales import init_work, init_workspace

PID = "_workgraph_declares_probe"
CROSS_MOVEMENT = (
    "theme_families",
    "climax_reservations",
    "cross_movement_recalls",
    "orchestral_macro_arc",
    "cyclic_obligations",
)


@pytest.fixture
def piece():
    path = scales_mod._WORKSPACE / PID
    shutil.rmtree(path, ignore_errors=True)
    init_workspace(PID, mode="compose_from_text", description="A symphony in C minor")
    try:
        yield PID
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_the_structures_are_declared_on_the_model():
    """If a name here disappears, the report below is silently wrong."""
    declared = set(WorkGraph.__dataclass_fields__)
    assert set(CROSS_MOVEMENT) <= declared


def test_init_work_reports_what_it_did_not_plan(piece):
    result = init_work(piece, movement_count=4, emotional_narrative="winter into spring")
    assert set(result["declared_but_not_planned"]) == set(CROSS_MOVEMENT)
    assert "not yet populated by any tool" in result["note"]


def test_what_it_does_fill_is_not_listed(piece):
    """`emotional_narrative` and `finale_payoff` are really stored, so they must
    not appear in the unplanned list — a report that flags everything is noise."""
    result = init_work(
        piece, movement_count=4, emotional_narrative="winter", finale_payoff="the theme returns"
    )
    assert "emotional_narrative" not in result["declared_but_not_planned"]
    assert result["emotional_narrative"] == "winter"


def test_nothing_in_the_codebase_writes_them():
    """The claim the report rests on. If someone implements one of these, this
    test fails and the report must be updated rather than left lying."""
    import pathlib
    import re

    sources = [
        p.read_text()
        for p in pathlib.Path(scales_mod.__file__).parent.rglob("*.py")
        if "test" not in str(p) and p.name != "models.py"
    ]
    body = "\n".join(sources)
    for name in CROSS_MOVEMENT:
        writes = re.findall(rf"\.{name}\s*=|\.{name}\.append\(|\b{name}\s*=\s*\[", body)
        assert not writes, f"{name} is now written — update init_work's report"
