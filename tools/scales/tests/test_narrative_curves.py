"""Tests for narrative-arc -> slot-curve wiring (_apply_narrative_curves).

The planned NarrativeArc must reach per-bar PhraseCurves so dynamics, density,
and the tempo arc actually follow the emotional story rather than hardcoded
function defaults.

Run: python3 -m scales.tests.test_narrative_curves
"""

from scales import scales
from scales.composition_brief import _creative_intent
from scales.models import NarrativeArc, NarrativeSection, PhraseCurves, PhraseSlot
from scales.piece_graph import PieceGraph


def _slot(bar_start, bar_count):
    return PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=bar_start,
        bar_count=bar_count,
        key="C",
        meter=[4, 4],
        curves=PhraseCurves(energy=[0.5] * bar_count),
    )


def test_no_narrative_keeps_default():
    s = _slot(1, 4)
    applied = scales._apply_narrative_curves(s, None)
    assert applied is False
    assert s.curves.energy == [0.5, 0.5, 0.5, 0.5]
    assert s.curves.tension == []


def test_curves_interpolated_from_section():
    arc = NarrativeArc(
        sections=[
            NarrativeSection(
                id="rise",
                bar_start=1,
                bar_end=8,
                energy_curve=[0.2, 1.0],  # rising
                tension_curve=[0.0, 1.0],
                density_curve=[0.3, 0.9],
                brightness_curve=[0.5, 0.5],
            )
        ]
    )
    s = _slot(1, 8)
    applied = scales._apply_narrative_curves(s, arc)
    assert applied is True
    # energy must rise monotonically across the 8 bars
    assert s.curves.energy[0] < s.curves.energy[-1]
    assert s.curves.energy == sorted(s.curves.energy)
    assert abs(s.curves.energy[0] - 0.2) < 1e-6
    assert abs(s.curves.energy[-1] - 1.0) < 1e-6
    # tension/density/brightness now populated (were empty before)
    assert len(s.curves.tension) == 8
    assert len(s.curves.density) == 8
    assert abs(s.curves.brightness[0] - 0.5) < 1e-6


def test_slot_in_second_section_samples_that_section():
    arc = NarrativeArc(
        sections=[
            NarrativeSection(id="a", bar_start=1, bar_end=8, energy_curve=[0.3, 0.4]),
            NarrativeSection(
                id="climax", bar_start=9, bar_end=16, energy_curve=[0.9, 1.0], climax_type="primary"
            ),
        ]
    )
    s = _slot(9, 8)  # lives entirely in the climax section
    scales._apply_narrative_curves(s, arc)
    assert all(v >= 0.85 for v in s.curves.energy), s.curves.energy


def test_uncovered_bars_fall_back():
    arc = NarrativeArc(
        sections=[NarrativeSection(id="a", bar_start=1, bar_end=4, energy_curve=[0.2, 0.8])]
    )
    s = _slot(1, 8)  # bars 5-8 are uncovered
    scales._apply_narrative_curves(s, arc)
    assert len(s.curves.energy) == 8
    # uncovered tail keeps the prior default (0.5)
    assert s.curves.energy[5] == 0.5


def test_narrative_survives_save_load(tmp_path, monkeypatch):
    """Regression: narrative was serialized but never reconstructed on load, so
    section.character never reached compose time. Guard the load-drop bug class.

    `monkeypatch` rather than a bare assignment: this test used to leave
    `scales._WORKSPACE` pointed at its own tmp_path for the REST OF THE SUITE.
    Every later test that touched the workspace then ran against a directory
    that had one piece in it, and any test holding a module-level
    `from scales.scales import _WORKSPACE` (an import-time copy) silently
    diverged from the code under test — passing alone, failing in the suite.
    """
    ws = tmp_path
    monkeypatch.setattr(scales, "_WORKSPACE", ws)
    pid = "narr-roundtrip"
    (ws / pid).mkdir(parents=True)
    g = PieceGraph()
    g.piece_id = pid
    g.save(str(ws / pid / "piece_graph.json"))

    scales.save_narrative(
        pid,
        sections=[
            {
                "id": "a",
                "label": "opening",
                "bar_start": 1,
                "bar_end": 8,
                "character": "the storm finally breaks",
                "gesture": "a long exhale",
                "climax_type": "primary",
            },
            {"id": "b", "label": "calm", "bar_start": 9, "bar_end": 16},
        ],
        overall_character="from struggle to peace",
    )

    g2 = PieceGraph.load(str(ws / pid / "piece_graph.json"))
    assert len(g2.narrative.sections) == 2  # not dropped on load
    assert g2.narrative.overall_character == "from struggle to peace"
    assert g2.narrative.primary_climax_section == "a"  # inferred from climax_type
    assert g2.narrative.sections[0].character == "the storm finally breaks"
    assert g2.narrative.sections[0].gesture == "a long exhale"


def test_creative_intent_prefers_authored_prose():
    arc = NarrativeArc(
        sections=[
            NarrativeSection(
                id="a",
                label="opening",
                bar_start=1,
                bar_end=8,
                character="the storm finally breaks",
                energy_curve=[0.9],
                climax_type="primary",
            ),
            NarrativeSection(id="b", label="calm", bar_start=9, bar_end=16, energy_curve=[0.3]),
        ]
    )

    class _G:
        narrative = arc

    g = _G()
    # Section with authored prose: intent leads with the prose, not adjectives.
    intent_a = _creative_intent(
        g, PhraseSlot(phrase_id="a_p1", bar_start=3, function="presentation")
    )
    assert "the storm finally breaks" in intent_a
    assert "intense" not in intent_a  # curve-adjectives suppressed when prose present
    assert "emotional peak" in intent_a  # climax marker still added
    # Section with no prose: falls back to curve-derived adjectives.
    intent_b = _creative_intent(
        g, PhraseSlot(phrase_id="b_p1", bar_start=10, function="continuation")
    )
    assert "gentle" in intent_b


if __name__ == "__main__":
    import inspect
    import tempfile
    from pathlib import Path

    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in fns:
        if "tmp_path" in inspect.signature(fn).parameters:
            with tempfile.TemporaryDirectory() as d:
                fn(Path(d))
        else:
            fn()
        print(f"ok {name}")
    print(f"\n{len(fns)} tests passed")


def test_texture_plan_changes_at_the_composers_measured_rate():
    """Two wrong answers shipped here before: a round-robin that changed the
    accompaniment idiom every bar for no reason, then a flat hold-one-idiom that
    changed it never. Mozart's own corpus changes left-hand texture on ~54% of bar
    transitions; the plan should sit near that, not at 0% or 100%."""
    from scales.models import StyleDNA
    from scales.scales import _default_texture_plan

    style = StyleDNA()
    style.composer_id = "mozart"
    style.lh_distribution = {"alberti": 0.4, "walking_bass": 0.3, "block_chord_sparse": 0.3}
    lh = [t.lh_texture for t in _default_texture_plan(style, "presentation", "PAC", 8, (3, 4))]
    changes = sum(1 for a, b in zip(lh, lh[1:]) if a != b)
    assert 2 <= changes <= 6, f"8-bar plan changed texture {changes} times: {lh}"


def test_texture_plan_never_schedules_silence_as_an_idiom():
    from scales.models import StyleDNA
    from scales.scales import _default_texture_plan

    style = StyleDNA()
    style.composer_id = "mozart"
    style.lh_distribution = {"silence": 0.9, "alberti": 0.1}
    plan = _default_texture_plan(style, "presentation", "PAC", 8, (3, 4))
    assert "unclassified" not in [t.lh_texture for t in plan]
