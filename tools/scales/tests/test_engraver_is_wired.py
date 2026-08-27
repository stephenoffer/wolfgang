"""Every path that stores a phrase must run the engraver's pass.

`expression_enricher` was complete, tested and called by nothing, so every
score the system produced carried **zero articulation marks and zero ties**
where the 26-movement reference corpus runs a median of 0.57 articulations and
0.18 ties per bar. Twenty-nine passing unit tests said nothing about it,
because they all built their objects in memory.

So this file tests the *wiring*, not the rules: that each commit entry point
runs the pass, that the pass reports what it did, and that it never touches
what the composer wrote.
"""

from __future__ import annotations

import ast

import pytest

from scales import scales


def _commit_entry_points():
    return [
        scales.commit_agent_phrase_layer_ir,
        scales.commit_agent_phrase_direct_bars,
    ]


@pytest.mark.parametrize("fn", _commit_entry_points(), ids=lambda f: f.__name__)
def test_the_agent_commit_paths_reach_the_engraver(fn, function_source):
    """Both route through `_gated_commit`, which calls `_engrave_phrase`."""
    src = function_source(scales, fn.__name__)
    assert "_gated_commit" in src, f"{fn.__name__} no longer goes through _gated_commit"
    assert "_engrave_phrase" in function_source(scales, "_gated_commit"), (
        "_gated_commit no longer runs the engraver's pass — this is exactly the "
        "state in which the system shipped scores with no articulation in them"
    )


def test_the_candidate_path_engraves_too(function_source):
    """The panel judge picks a winner from a rendered preview.

    An unengraved preview has no articulation, no phrasing and no pedal, so the
    judge was choosing between MIDI dumps and only the winner was engraved.
    """
    src = function_source(scales, "commit_candidate_phrase")
    assert "_engrave_phrase" in src


def test_promoting_a_candidate_goes_through_a_gated_commit(function_source):
    src = function_source(scales, "promote_candidate")
    assert "commit_agent_phrase_layer_ir" in src


def test_the_engraving_report_is_returned_to_the_caller(function_source):
    """A reviewer must be able to tell the engraver's marks from the composer's."""
    src = function_source(scales, "_gated_commit")
    assert '"engraving"' in src or "'engraving'" in src


def test_a_failing_engraver_cannot_block_a_good_commit(function_source):
    """It is the last step before storing a phrase the gate already passed.

    A crash in a cosmetic pass must never cost the notes.
    """
    tree = ast.parse(function_source(scales, "_engrave_phrase").lstrip())
    handlers = [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]
    assert handlers, "_engrave_phrase must not let an exception escape into the commit path"


def test_the_engraver_never_changes_a_pitch_or_a_duration(tmp_path, monkeypatch):
    """The composer stays the author. This is why it does not add ties, either:
    a tie changes what sounds, and that is a compositional decision."""
    from scales.expression_enricher import enrich_layer_ir
    from scales.models import LayerEvent, LayerIR

    rh = [
        LayerEvent(bar=b, beat=float(i + 1), pitch=f"{'CDEFGAB'[i]}5", duration="q")
        for b in range(1, 5)
        for i in range(4)
    ]
    lh = [LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w") for b in range(1, 5)]
    layer = LayerIR(phrase_id="p1", principal_line=rh, bass_foundation=lh, bar_count=4)
    before = [(e.bar, e.beat, e.pitch, e.duration, e.tie) for e in rh + lh]

    report = enrich_layer_ir(layer, style="mozart")

    after = [(e.bar, e.beat, e.pitch, e.duration, e.tie) for e in rh + lh]
    assert before == after, "the engraver changed a pitch, a duration or a tie"
    assert report.total_added > 0, "the engraver did nothing at all on a plain phrase"


def test_the_engraver_keeps_every_mark_the_composer_wrote():
    from scales.expression_enricher import enrich_layer_ir
    from scales.models import LayerEvent, LayerIR

    rh = [
        LayerEvent(bar=b, beat=float(i + 1), pitch=f"{'CDEFGAB'[i]}5", duration="q")
        for b in range(1, 5)
        for i in range(4)
    ]
    rh[0].articulation = "marcato"
    rh[5].ornament = "mordent"
    rh[9].dynamic = "ff"
    layer = LayerIR(phrase_id="p1", principal_line=rh, bar_count=4)
    enrich_layer_ir(layer, style="mozart")
    assert rh[0].articulation == "marcato"
    assert rh[5].ornament == "mordent"
    assert rh[9].dynamic == "ff"
