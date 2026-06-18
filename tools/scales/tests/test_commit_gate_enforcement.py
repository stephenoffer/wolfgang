"""Enforcement tests for the hardened commit path: brief receipt requirement,
hard density floor when corpus stats are missing, blocking corpus_alignment
(composed_blind), tightened waivers, and the corpus-bar calibration guard.

Run: python3 -m scales.tests.test_commit_gate_enforcement
"""

from pathlib import Path

from scales import commit_gate, scales
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph

# ─── helpers ─────────────────────────────────────────────────────────────────


def _rh_bar(pitches, bar, dur="e"):
    return [
        LayerEvent(
            bar=bar, beat=1.0 + i * 0.5, pitch=p, duration=dur, source_layer="principal_line"
        )
        for i, p in enumerate(pitches)
    ]


def _layer_from_bars(rh_bars, lh_bars, key="C"):
    lyr = LayerIR(phrase_id="t", bar_count=len(rh_bars), key=key, meter=[4, 4])
    for bn, pitches in enumerate(rh_bars, start=1):
        lyr.principal_line.extend(_rh_bar(pitches, bn))
    for bn, pitches in enumerate(lh_bars, start=1):
        for i, p in enumerate(pitches):
            lyr.bass_foundation.append(
                LayerEvent(
                    bar=bn,
                    beat=1.0 + i * 0.5,
                    pitch=p,
                    duration="e",
                    source_layer="bass_foundation",
                )
            )
    return lyr


def _slot(bars, key="C"):
    return PhraseSlot(
        phrase_id="m1_a_p1",
        section_id="m1_a",
        bar_start=1,
        bar_count=bars,
        key=key,
        meter=[4, 4],
        texture_plan={},
    )


def _graph(slot, trace=None):
    g = PieceGraph()
    ps = PhraseState(slot=slot)
    ps.context_trace = trace
    g.phrases["m1_a_p1"] = ps
    return g


# ─── B2: hard density floor when corpus stats are missing ─────────────────────


def test_density_floor_blocks_when_stats_missing():
    # 2 events/bar LH with NO corpus stats must still be blocked (generic floor).
    layer = _layer_from_bars(
        [["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]] * 4,  # rich RH
        [["C3", "G3"]] * 4,  # skeletal LH
    )
    d = commit_gate._check_density(layer, _slot(4), density_stats={}, hand="lh")
    assert d is not None, "missing stats must NOT disable the density guard"
    assert d.severity == "block"
    assert "generic floor" in d.corpus_ref


def test_density_floor_passes_rich_lh_without_stats():
    layer = _layer_from_bars(
        [["C5"] * 8] * 4,
        [["C3", "E3", "G3", "C4", "G3", "E3", "C3", "G3"]] * 4,  # ~8 events/bar
    )
    d = commit_gate._check_density(layer, _slot(4), density_stats={}, hand="lh")
    assert d is None, "rich LH should clear the generic floor"


# ─── figuration_flat: photocopy tell, calibrated to real music ────────────────


def test_figuration_flat_ignores_short_phrase():
    # A 2-bar repeat is idiomatic, not a photocopy — too short to be the tell
    # (calibration finding: real corpus 4-bar phrases legitimately repeat).
    layer = _layer_from_bars(
        [["C5", "E5", "G5", "C6"], ["C5", "E5", "G5", "C6"]],
        [["C3", "G3", "E3", "G3"], ["C3", "G3", "E3", "G3"]],  # identical LH
    )
    d = commit_gate._check_figuration_flat(layer, _slot(2), "mozart")
    assert d is None, "2-bar repeat must not trip figuration_flat"


def test_figuration_flat_fires_on_sustained_photocopy():
    # Four+ bars of an identical FLOWING accompaniment (alberti) is the tell.
    bar = ["C3", "G3", "E3", "G3"]
    layer = _layer_from_bars(
        [["C5", "E5", "G5", "C6"]] * 4,
        [bar, bar, bar, bar],  # identical alberti every bar
    )
    d = commit_gate._check_figuration_flat(layer, _slot(4), "mozart")
    assert d is not None and d.severity == "block"


def test_figuration_flat_exempts_static_texture():
    # Block chords legitimately repeat under prolonged harmony — not a tell.
    from scales.models import BarTexturePlan

    bar = ["C3", "G3", "E3", "G3"]
    layer = _layer_from_bars([["C5", "E5", "G5", "C6"]] * 4, [bar] * 4)
    slot = _slot(4)
    slot.texture_plan = [
        BarTexturePlan(rh_texture="singing_melody", lh_texture="block_chord_offbeat")
    ] * 4
    d = commit_gate._check_figuration_flat(layer, slot, "mozart")
    assert d is None, "static block-chord texture must be exempt"


# ─── B1: corpus_alignment (composed_blind) blocks ─────────────────────────────


def test_corpus_alignment_blocks_when_surface_ignores_exemplars():
    # Exemplars: smooth stepwise eighths. Surface: huge leaps, all whole notes.
    exemplars = ["C5e D5e E5e F5e G5e A5e B5e C6e"] * 3
    layer = _layer_from_bars([["C5", "C8"]], [["C3"]])  # 2 wild notes, sparse
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0, pitch="C3", duration="w", source_layer="principal_line"),
        LayerEvent(bar=2, beat=1.0, pitch="C7", duration="w", source_layer="principal_line"),
    ]
    layer.bar_count = 2
    g = _graph(_slot(2), trace={"briefed_exemplars": exemplars})
    ds = commit_gate._check_corpus_alignment(g, "m1_a_p1", layer)
    blind = [d for d in ds if d.check == "composed_blind"]
    assert blind and blind[0].severity == "block"
    # and the trace flag was recorded for self_evaluate
    assert g.phrases["m1_a_p1"].context_trace["composed_blind"] is True


def test_corpus_alignment_passes_when_adapted():
    exemplars = ["C5e D5e E5e F5e G5e A5e B5e C6e"]
    # surface borrows the same stepwise-eighths DNA, transposed
    layer = _layer_from_bars([["G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5"]], [["C3"]])
    g = _graph(_slot(1), trace={"briefed_exemplars": exemplars})
    ds = commit_gate._check_corpus_alignment(g, "m1_a_p1", layer)
    assert not [d for d in ds if d.check == "composed_blind"], (
        "an adapted surface should clear corpus_alignment"
    )


def test_lh_composed_blind_warns_when_accompaniment_ignored():
    # LH exemplars: flowing eighths. Surface LH: two whole notes, no overlap.
    lh_exemplars = ["C3e G3e E3e G3e C3e G3e E3e G3e"] * 3
    layer = _layer_from_bars([["C5", "D5", "E5", "F5"]] * 2, [[], []])
    layer.bass_foundation = [
        LayerEvent(bar=1, beat=1.0, pitch="C2", duration="w", source_layer="bass_foundation"),
        LayerEvent(bar=2, beat=1.0, pitch="C7", duration="w", source_layer="bass_foundation"),
    ]
    layer.bar_count = 2
    g = _graph(
        _slot(2),
        trace={"briefed_exemplars": ["C5e D5e E5e F5e"], "briefed_exemplar_lhs": lh_exemplars},
    )
    ds = commit_gate._check_corpus_alignment(g, "m1_a_p1", layer)
    lh = [d for d in ds if d.check == "composed_blind_lh"]
    assert lh and lh[0].severity == "warn", [d.check for d in ds]
    assert g.phrases["m1_a_p1"].context_trace["composed_blind_lh"] is True


# ─── B4: tightened waivers ────────────────────────────────────────────────────


def test_waiver_requires_substantial_reason():
    layer = _layer_from_bars([["C5", "D5"]], [["C3", "G3"]])
    g = _graph(_slot(1))
    res = commit_gate.run_commit_gate(
        g,
        "m1_a_p1",
        layer,
        allow=[{"check": "density_low_lh", "reason": "sparse"}],
        composer="mozart",
    )
    assert any("real musical reason" in r for r in res.rejected_waivers)


def test_waiver_caps_blocking_checks():
    layer = _layer_from_bars([["C5", "D5"]], [["C3", "G3"]])
    g = _graph(_slot(1))
    res = commit_gate.run_commit_gate(
        g,
        "m1_a_p1",
        layer,
        allow=[
            {"check": "density_low_rh", "reason": "deliberate pointillist gap here"},
            {"check": "density_low_lh", "reason": "deliberate pointillist gap here"},
        ],
        composer="mozart",
    )
    assert any("too many blocking checks" in r for r in res.rejected_waivers)


# ─── A: brief receipt requirement through the public commit API ───────────────


def _valid_layer_dict():
    """A 2-bar IR whose principal_line and bass_foundation each fill the bar
    (8 eighths = 4.0 beats), so physical validation passes and the commit
    reaches the brief gate."""
    import dataclasses

    rh = [["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]] * 2
    lh = [["C3", "G3", "E3", "G3", "C3", "G3", "E3", "G3"]] * 2
    layer = _layer_from_bars(rh, lh)
    layer.phrase_id = "m1_a_p1"
    return dataclasses.asdict(layer)


def _temp_piece(tmp, trace=None):
    """Write a minimal piece graph into a temp workspace; return piece_id."""
    piece_id = "enf-test-piece"
    g = _graph(_slot(2), trace=trace)
    ws = tmp / piece_id
    ws.mkdir(parents=True, exist_ok=True)
    g.save(str(ws / "piece_graph.json"))
    return piece_id


def test_commit_rejected_without_brief(tmp_workspace):
    piece_id = _temp_piece(tmp_workspace, trace=None)
    r = scales.commit_agent_phrase_layer_ir(
        piece_id, "m1_a_p1", _valid_layer_dict(), composer="mozart"
    )
    assert r.get("error") == "brief_not_fetched", r


def test_commit_rejected_when_brief_insufficient(tmp_workspace):
    trace = {"brief_fetched": True, "brief_insufficient": True, "briefed_exemplars": []}
    piece_id = _temp_piece(tmp_workspace, trace=trace)
    r = scales.commit_agent_phrase_layer_ir(
        piece_id, "m1_a_p1", _valid_layer_dict(), composer="mozart"
    )
    assert r.get("error") == "brief_insufficient", r
    # ...but an explicit waiver clears the brief gate (still subject to quality gate)
    r2 = scales.commit_agent_phrase_layer_ir(
        piece_id,
        "m1_a_p1",
        _valid_layer_dict(),
        composer="mozart",
        allow=[
            {
                "check": "brief_insufficient",
                "reason": "composing without corpus support is intentional here",
            }
        ],
    )
    assert r2.get("error") != "brief_insufficient", r2


# ─── Calibration guard: my new checks must not fire on real corpus ────────────


def _real_mozart_phrases(limit=60):
    """Yield (layer, exemplar_rhs) for real consecutive Mozart 4-bar phrases."""
    import glob
    import json
    from collections import defaultdict

    from scales import composition_brief as cb
    from scales import direct_compose

    root = Path(__file__).resolve().parents[2] / "reference_index" / "mozart"
    shards = sorted(glob.glob(str(root / "bars_0*.json")))
    if not shards:
        return
    bars_by_src = defaultdict(dict)
    for f in shards[:1]:
        for b in json.load(open(f)):
            bars_by_src[b["source"]][b["bar_num"]] = b
    adapter = cb._adapter("mozart")
    n = 0
    for src, bd in bars_by_src.items():
        nums = sorted(bd)
        for i in range(0, len(nums) - 3, 4):
            run = nums[i : i + 4]
            if run != list(range(run[0], run[0] + 4)):
                continue
            key = bd[run[0]].get("key", "C")
            try:
                shbars = []
                for bn in run:
                    rh, lh = cb._adapted_to_shorthand(adapter.transpose_bar(bd[bn], key))
                    shbars.append({"rh": rh, "lh": lh})
                layer = direct_compose.compose_phrase(
                    shbars, key=key, bar_start=1, phrase_id="c", meter=[4, 4]
                )
            except Exception:
                continue
            yield layer, [b["rh"] for b in shbars if b["rh"]]
            n += 1
            if n >= limit:
                return


def test_real_corpus_never_flagged_composed_blind():
    """The corpus-alignment check must NEVER flag a real corpus surface as
    composed_blind when briefed with itself — else the guarantee is miscalibrated.
    """
    checked = 0
    for layer, exemplars in _real_mozart_phrases():
        g = _graph(_slot(layer.bar_count), trace={"briefed_exemplars": exemplars})
        ds = commit_gate._check_corpus_alignment(g, "m1_a_p1", layer)
        blind = [d for d in ds if d.check == "composed_blind"]
        assert not blind, (
            "real Mozart surface wrongly flagged composed_blind "
            f"against its own exemplars: {blind[0].detail}"
        )
        checked += 1
    if checked == 0:
        print("  (skipped: no mozart reference_index present)")
    else:
        print(f"  ({checked} real Mozart phrases cleared corpus_alignment)")


def test_generic_density_floor_inactive_for_armed_composer():
    """For an armed composer (mozart has density_stats), the generic floor must
    never engage — the real corpus medians are used instead."""
    from scales.composition_brief import texture_density_stats

    stats = texture_density_stats("mozart")
    assert stats.get("lh") or stats.get("rh"), "mozart should have density stats"


# ─── C1: no silent composer fallback ─────────────────────────────────────────


def test_unarmed_composer_not_silently_substituted():
    from scales import composition_brief as cb

    g = PieceGraph()
    name, matched = cb.resolve_composer_matched(g, override="sibelius")
    assert name == "sibelius" and matched is False, (name, matched)
    # an armed composer resolves and matches
    name2, matched2 = cb.resolve_composer_matched(g, override="mozart")
    assert name2 == "mozart" and matched2 is True
    # an armed STYLE id resolves matched too (style-targeting integration) —
    # must NOT be treated as an unarmed composer and blocked
    from scales import style_registry as sr

    if sr.style_members("classical"):  # skip if classical members unarmed
        sname, smatched = cb.resolve_composer_matched(g, override=sr.make_style_id("classical"))
        assert smatched is True and sr.is_style_id(sname), (sname, smatched)


# ─── C3: section gate elevates egregious flags ────────────────────────────────


def test_section_gate_flags_composed_blind_and_static_texture():
    report = {
        "metrics": {"texture_change_pct": {"status": "low", "value": 0.05}},
        "authoring": {"composed_blind": 2, "composed_blind_phrases": ["p1", "p2"]},
        "corpus_divergence": {"composer": "mozart", "metrics": {}},
    }
    gate = scales._section_gate(report)
    assert gate["passed"] is False
    assert any("mechanically static" in h for h in gate["hard_failures"])
    assert any("composed blind" in h for h in gate["hard_failures"])


def test_section_gate_passes_clean_report():
    report = {
        "metrics": {"texture_change_pct": {"status": "ok", "value": 0.5}},
        "authoring": {"composed_blind": 0, "composed_blind_phrases": []},
        "corpus_divergence": {"composer": "mozart", "metrics": {}},
    }
    gate = scales._section_gate(report)
    assert gate["passed"] is True and not gate["hard_failures"]


if __name__ == "__main__":
    import shutil
    import tempfile

    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for name, fn in fns:
        if "tmp_workspace" in fn.__code__.co_varnames[: fn.__code__.co_argcount]:
            tmp = Path(tempfile.mkdtemp())
            orig = scales._WORKSPACE
            scales._WORKSPACE = tmp
            try:
                fn(tmp)
            finally:
                scales._WORKSPACE = orig
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            fn()
        print(f"ok {name}")
        passed += 1
    print(f"\n{passed} tests passed")
