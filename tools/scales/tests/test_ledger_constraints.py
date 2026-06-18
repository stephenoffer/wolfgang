"""A4 — ledger actionization: open expectations become binding, phrase-scoped
constraints in the brief (must_resolve / must_not_use / cooldown / locked).

Run: python3 -m scales.tests.test_ledger_constraints
"""

from scales import composition_brief as cb
from scales.expectation_ledger import ExpectationLedger
from scales.models import FormGraph, PhraseSlot, PhraseState, SectionSpec
from scales.piece_graph import PieceGraph


def _graph_with_ledger():
    g = PieceGraph()
    # three phrases in performance order p1 -> p2 -> p3
    g.form = FormGraph()
    g.form.sections["s"] = SectionSpec(id="s", phrase_ids=["p1", "p2", "p3"])

    class _MV:
        sections = ["s"]

    g.form.movements = [_MV()]
    for pid in ("p1", "p2", "p3"):
        g.phrases[pid] = PhraseState(
            slot=PhraseSlot(phrase_id=pid, section_id="s", bar_start=1, bar_count=4, key="C")
        )

    led = ExpectationLedger()
    led.add_promise("motif_A", introduced_at="p1", must_return_by="p2")
    led.add_prohibition("climax", introduced_at="p1", must_resolve_by="p3")
    led.add_cooldown("alberti", introduced_at="p1", duration_phrases=2)
    led.add_lock("source_contour", introduced_at="p1")
    # persist as the graph does (cross_scale_ledger raw dict, phrase delegate)
    from scales.cross_scale_ledger import CrossScaleLedger

    csl = CrossScaleLedger()
    csl._phrase_ledger = led
    g.cross_scale_ledger = csl.to_dict()
    return g


def test_constraints_built_for_due_phrase():
    g = _graph_with_ledger()
    # at p2, the motif_A promise is due now; prohibition/cooldown/lock active
    lc = cb._ledger_constraints(g, "p2")
    objs = {r["object"] for r in lc["must_resolve"]}
    assert "motif_A" in objs, lc
    assert any(p["object"] == "climax" for p in lc["must_not_use"]), lc
    assert any(c["object"] == "alberti" for c in lc["cooldown"]), lc
    assert any(k["object"] == "source_contour" for k in lc["locked"]), lc


def test_overdue_flagged():
    g = _graph_with_ledger()
    # at p3, motif_A (deadline p2) is overdue
    lc = cb._ledger_constraints(g, "p3")
    mr = [r for r in lc["must_resolve"] if r["object"] == "motif_A"]
    assert mr and mr[0]["overdue"] is True, lc


def test_render_includes_binding_block():
    g = _graph_with_ledger()
    brief = cb.build_brief(g, "p2")
    text = cb.render_text(brief)
    assert "THIS PHRASE MUST" in text, text
    assert "motif_A" in text


def test_no_ledger_is_empty_not_crash():
    g = PieceGraph()
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(phrase_id="p1", section_id="s", bar_start=1, bar_count=4, key="C")
    )
    lc = cb._ledger_constraints(g, "p1")
    assert lc == {"must_resolve": [], "must_not_use": [], "cooldown": [], "locked": []}


if __name__ == "__main__":
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in fns:
        fn()
        print(f"ok {name}")
    print(f"\n{len(fns)} tests passed")
