"""The harmonic metrics must see the inner voices.

`_all_events` returned the two outer staves only, so for every contrapuntal
corpus it measured soprano and bass and discarded the alto and tenor —
77,749 of Bach's events against 72,555 outer, 374,182 of Palestrina's against
304,150. `analyze_score_bars` folds them into `rh_inner_display` /
`lh_inner_display` precisely so they survive the extraction; nothing downstream
read them.
"""

import pytest

from scales.style_dimensions import _all_events


def _bar():
    return {
        "rh_display": [{"type": "note", "interval_from_root": 0, "dur": 1.0}],
        "lh_display": [{"type": "note", "interval_from_root": 7, "dur": 1.0}],
        "rh_inner_display": [{"type": "note", "interval_from_root": 4, "dur": 1.0}],
        "lh_inner_display": [{"type": "note", "interval_from_root": 10, "dur": 1.0}],
    }


def test_the_inner_voices_are_counted():
    assert len(_all_events(_bar())) == 4


def test_a_two_staff_bar_is_unaffected():
    bar = {k: v for k, v in _bar().items() if "inner" not in k}
    assert len(_all_events(bar)) == 2


def test_a_bar_with_no_events_is_empty_not_an_error():
    assert _all_events({}) == []


@pytest.mark.calibration
def test_the_contrapuntal_corpora_gain_their_middle_voices():
    """A regression here is silent: the metric still returns a plausible number,
    computed on half the notes."""
    import json
    from pathlib import Path

    for composer, minimum in (("bach", 1.3), ("palestrina", 1.5)):
        root = Path("tools/reference_index") / composer
        if not root.is_dir():
            pytest.skip(f"{composer} corpus not present")
        outer = inner = 0
        for shard in sorted(root.glob("bars_*.json"))[:2]:
            for bar in json.load(open(shard)):
                outer += len(bar.get("rh_display") or []) + len(bar.get("lh_display") or [])
                inner += len(bar.get("rh_inner_display") or []) + len(
                    bar.get("lh_inner_display") or []
                )
        if not inner:
            pytest.skip(f"{composer} shards carry no inner voices")
        assert (outer + inner) / max(outer, 1) >= minimum, (
            f"{composer}: inner voices are {inner} against {outer} outer — "
            f"the metric would be measuring half the music"
        )
