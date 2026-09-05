"""A target the composer has been ignoring should be shown as a GAP.

The brief has always printed the composer's own thickness — "21% of right-hand
attacks are more than one note" for Chopin. It did not move the output: a
nocturne came out with a bare single line in 93% of bars, 1% multi-note attacks,
against a real Chopin range of 5-63%, with that sentence in front of the composer
the whole time.

`self_evaluate` measured the shortfall afterwards and told the critic. The
composer, who could still act on it, was never told. A target is a number to
agree with; a gap is a number to act on — which is why MARKS SO FAR earns its
place, and this now does the same.
"""

from scales.composition_brief import _rh_thickness_so_far, voicing_lines
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph


def _graph(pitches) -> PieceGraph:
    events = [
        LayerEvent(bar=1, beat=float(i + 1), pitch=p, duration="q", role="structural")
        for i, p in enumerate(pitches)
    ]
    layer = LayerIR(principal_line=events, bass_foundation=[], meter=(4, 4), key="C major")
    g = PieceGraph()
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=1,
                        key="C major", meter=(4, 4), tempo_bpm=90),
        realized=layer, agent_authored=True,
    )
    return g


def test_a_single_line_measures_zero():
    assert _rh_thickness_so_far(_graph(["C5", "D5", "E5", "F5"])) == 0.0


def test_every_attack_a_chord_measures_one():
    assert _rh_thickness_so_far(_graph([["C5", "E5"]] * 4)) == 1.0


def test_a_doubled_unison_is_not_thickness():
    """`[G5,G5]` is one pitch written twice — real in the score, not a chord."""
    assert _rh_thickness_so_far(_graph([["G5", "G5"]] * 4)) == 0.0


def test_a_mixed_texture_measures_between():
    got = _rh_thickness_so_far(_graph([["C5", "E5"], "D5", ["E5", "G5"], "F5"]))
    assert abs(got - 0.5) < 1e-9


def test_an_empty_piece_reports_nothing_rather_than_zero():
    """Nothing committed is not the same as a thin texture."""
    assert _rh_thickness_so_far(PieceGraph()) is None


def test_the_gap_reaches_the_brief():
    """At exactly zero there is no ratio to quote, so the wording has to carry
    it — `target / 0` would be a crash and "0x thinner" would be nonsense."""
    lines = " ".join(voicing_lines("chopin", _graph(["C5", "D5", "E5", "F5"])))
    assert "THICKNESS SO FAR" in lines
    assert "a bare single line the whole way" in lines


def test_a_thin_but_nonzero_piece_gets_the_ratio():
    lines = " ".join(voicing_lines("chopin", _graph([["C5", "E5"]] + ["D5"] * 19)))
    assert "thinner than his" in lines


def test_a_piece_already_at_the_target_is_told_so():
    lines = " ".join(voicing_lines("chopin", _graph([["C5", "E5"]] * 4)))
    assert "already there" in lines


def test_without_a_graph_the_section_is_unchanged():
    """The brief is still buildable when no piece state is available."""
    lines = " ".join(voicing_lines("chopin"))
    assert "VOICING" in lines
    assert "THICKNESS SO FAR" not in lines


def test_each_piece_position_report_has_its_own_label():
    """Four sections now tell the composer where the piece stands: MARKS,
    RANGE, BREATHING and THICKNESS. Two of them opened with the same words
    ("SO FAR THIS PIECE") while measuring completely different quantities —
    the same-name-for-two-things trap that `feedback_contradictory_guidance`
    records, in miniature and in the composer's own reading order.
    """
    import collections
    import re

    from scales.scales import get_composition_brief

    text = get_composition_brief(
        "chopin-nocturne-ebmaj-20260826", "m1_a_p1", composer="chopin"
    )
    labels = re.findall(r"^\s*([A-Z][A-Z ]*SO FAR)", text, re.M)
    assert len(labels) >= 3, f"expected several position reports, found {labels}"
    counts = collections.Counter(x.strip() for x in labels)
    assert not [k for k, v in counts.items() if v > 1], f"duplicated label: {counts}"
