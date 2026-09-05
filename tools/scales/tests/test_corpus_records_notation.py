"""The corpus records ties, articulation and slurs.

`analyze_score_bars` captured `type`, `dur`, `is_grace` and `orn` and nothing
else, so every composer's bar records reported **0.0% tied notes** — all eleven
of them, across 125,325 bars. That is not a property of the music: measured
over 46,180 notes of real Bach, Mozart, Beethoven and Haydn, 6.5% of notes are
tied, 7.2% carry an articulation, and the sample holds 5,783 slurs.

Nothing could brief the agent on a note held across a barline, because nothing
in the pipeline had ever seen one.
"""

import pytest

pytestmark = pytest.mark.calibration


def _sample_bars():
    import music21
    from scripts.build_full_corpus import analyze_score_bars

    out = []
    truth = {"notes": 0, "ties": 0, "artic": 0}
    for path in music21.corpus.getComposer("bach")[:4]:
        try:
            score = music21.converter.parse(path)
        except Exception:
            continue
        notes = list(score.recurse().notes)
        truth["notes"] += len(notes)
        truth["ties"] += sum(1 for n in notes if n.tie is not None)
        truth["artic"] += sum(1 for n in notes if n.articulations)
        try:
            out.extend(analyze_score_bars(score, "bach", str(path)))
        except Exception:
            continue
    return out, truth


def _events(bars):
    return [
        e
        for b in bars
        for side in ("rh_events", "lh_events")
        for e in (b.get(side) or [])
        if isinstance(e, dict) and e.get("type") in ("note", "chord")
    ]


def test_the_extractor_records_ties_at_all():
    bars, truth = _sample_bars()
    if not bars or not truth["ties"]:
        pytest.skip("music21 corpus sample has no ties to find")
    events = _events(bars)
    assert events, "no note events extracted"
    tied = sum(1 for e in events if e.get("tie"))
    assert tied > 0, "the corpus reported 0.0% tied notes on music that ties"


def test_the_tie_rate_is_in_the_right_neighbourhood():
    """Not an exact match — the extractor reduces a four-part chorale to two
    staves, so its denominator is smaller than music21's note count. But a
    capture that is an order of magnitude off is a capture that is wrong."""
    bars, truth = _sample_bars()
    if not bars or not truth["ties"]:
        pytest.skip("music21 corpus sample has no ties to find")
    events = _events(bars)
    got = sum(1 for e in events if e.get("tie")) / len(events)
    expected = truth["ties"] / truth["notes"]
    assert expected / 4 <= got <= expected * 4, f"extracted {got:.2%} against {expected:.2%}"


def test_tie_values_are_the_notated_kinds():
    bars, _ = _sample_bars()
    if not bars:
        pytest.skip("no bars")
    for e in _events(bars):
        if e.get("tie") is not None:
            assert e["tie"] in ("start", "stop", "continue", "let-ring"), e["tie"]


def test_articulation_and_slur_fields_are_present_and_typed():
    bars, _ = _sample_bars()
    if not bars:
        pytest.skip("no bars")
    events = _events(bars)
    assert events
    for e in events:
        assert isinstance(e.get("artic"), list), "artic must always be a list"
        assert e.get("slur") in (None, "start", "stop", "inner"), e.get("slur")
