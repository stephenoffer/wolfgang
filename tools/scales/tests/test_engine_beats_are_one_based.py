"""Beats are ONE-BASED. The engine's bar-wrap did not know that.

A bar spans beats [1.0, 1.0 + bar_len): the downbeat is 1.0, and in 3/4 the last
valid position is just under 4.0. `_construct_melody` wrapped with
`while beat_cursor > bar_len`, which fires on 3.0 — the last beat of the bar —
and then subtracted the bar length from a one-based number, landing at 0.5.

Sixty events in a single section were written at beats 0.25, 0.5 and 0.75, which
are not positions in any bar. The repair pass snapped and trimmed them, which is
where most of its churn came from and why 24 notes were being discarded.
"""

import shutil

import pytest

_SRC = "haydn-sonatina-gmaj-20260826"
_PID = "_test_one_based_beats"


@pytest.fixture()
def engine_realized():
    import os

    from scales import surface_composer as SC
    from scales.scales import _WORKSPACE, run_scales_section

    if not os.path.exists(_WORKSPACE / _SRC / "piece_graph.json"):
        pytest.skip("sonatina not present")
    shutil.rmtree(_WORKSPACE / _PID, ignore_errors=True)
    shutil.copytree(_WORKSPACE / _SRC, _WORKSPACE / _PID)

    seen = []
    orig = SC._TaggedEvent

    def spy(*a, **kw):
        if kw.get("beat") is not None:
            seen.append(float(kw["beat"]))
        return orig(*a, **kw)

    SC._TaggedEvent = spy
    try:
        run_scales_section(_PID, "m2_a")
    finally:
        SC._TaggedEvent = orig
    yield seen
    shutil.rmtree(_WORKSPACE / _PID, ignore_errors=True)


def test_no_event_is_written_below_the_downbeat(engine_realized):
    below = [b for b in engine_realized if b < 1.0]
    assert not below, f"{len(below)} events below beat 1.0, e.g. {sorted(set(below))[:5]}"


def test_the_engine_still_produces_notes(engine_realized):
    """A wrap that never fires would also pass the test above."""
    assert len(engine_realized) > 50, len(engine_realized)


def test_the_wrap_threshold_is_one_based():
    """Guard the specific comparison, because `> bar_len` reads plausible."""
    import inspect

    from scales import surface_composer as SC

    src = inspect.getsource(SC)
    assert "while beat_cursor > bar_len:" not in src
    assert "while beat_cursor >= bar_len + 1:" in src
