"""No bar may hold more beats than its meter, in any metre the engine builds.

This is the invariant behind a long chain of defects, each of which presented as
one bar per piece exporting over its meter:

  * a rest sharing a note's onset, kept as though it were a chord tone, then
    laid out sequentially past the barline;
  * the repair not running last, so `_thicken_principal_line` and
    `_hold_over_barline` left onsets it would have fixed — a 64th at 67/48 of a
    beat, a position no binary note can occupy, in a bar that then cannot tile;
  * a 3/8 bar exporting as 85/56 because a binary note was read as a septuplet.

Every one was invisible to a bounds check. "Is any event at or past the
capacity?" is answerable and was answered correctly — none were — while the
defect sat INSIDE the bar at a position that cannot divide it. Divisibility is
not an inequality, so the only instrument that catches these is the one below:
build a section and add the bar up.

Marked `calibration` because each metre runs the engine end to end.
"""

from __future__ import annotations

import warnings

import pytest

_CASES = [
    ((4, 4), "C major", "mozart"),
    ((3, 4), "g minor", "mozart"),
    ((3, 8), "A major", "mozart"),
    ((6, 8), "D major", "mozart"),
    ((12, 8), "C major", "mozart"),
    ((6, 4), "G major", "mozart"),
    ((5, 4), "C major", "mozart"),
    ((2, 2), "F major", "mozart"),
]


@pytest.mark.calibration
@pytest.mark.parametrize("meter,key,composer", _CASES, ids=lambda v: str(v))
def test_no_bar_holds_more_than_its_meter(meter, key, composer):
    warnings.filterwarnings("ignore")
    import music21

    from scales.scales import (
        build_form_graph,
        compile_style,
        init_workspace,
        run_scales_section,
        self_evaluate,
    )

    piece = f"_test_tiles_{meter[0]}_{meter[1]}"
    init_workspace(piece, mode="compose_from_text", description="a metre probe")
    compile_style(piece, composers=[composer])
    build_form_graph(piece, form="rounded_binary", key=key, tempo_bpm=100, meter=meter)
    run_scales_section(piece, "m1_a")

    report = self_evaluate(piece, "m1_a", composer=composer)
    assert report.get("assembled_path"), report

    score = music21.converter.parse(report["assembled_path"])
    overfull = []
    for part in score.parts:
        for measure in part.getElementsByClass("Measure"):
            signature = measure.timeSignature or measure.getContextByClass("TimeSignature")
            capacity = float(signature.barDuration.quarterLength) if signature else 4.0
            held = sum(float(n.quarterLength) for n in measure.notesAndRests)
            if abs(held - capacity) > 0.01:
                overfull.append(f"{part.partName} m{measure.number}: {held} of {capacity}")
    assert not overfull, "\n  ".join(overfull)
