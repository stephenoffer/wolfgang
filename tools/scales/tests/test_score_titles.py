"""A work has a title; a movement has a movement name. They are not the same field.

`_apply_metadata` set `md.title` and `md.movementName` to the same string, and
music21's MusicXML exporter drops `<work-title>` when the two agree — it writes
only `<movement-title>`. So a three-movement sonatina exported with NO work
title at all, and all three movements titled "three-movement sonatina".

music21 deliberately falls back to the title when no movement name is set
("musicxml often defaults to show only movement title"), so a full-score export
still carries the title in both tags. That is the compatible behaviour and is
left alone. What must hold is that `<work-title>` exists, and that assembling
ONE movement names that movement rather than repeating the work's title.
"""

from __future__ import annotations

import re
import shutil

import pytest

from scales.assembler import assemble
from scales.piece_graph import PieceGraph
from scales.scales import (
    _WORKSPACE,
    build_form_graph,
    compile_style,
    init_workspace,
    run_scales_section,
)

_PIECE = "test-titles-20260827"


@pytest.fixture(scope="module")
def two_movements():
    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)
    init_workspace(
        _PIECE,
        "compose_from_text",
        "Sonatina in C major",
        {"target": {"instrumentation": "solo_piano"}},
    )
    compile_style(_PIECE, composers=["mozart"])
    for mid, form, key, meter, tempo in (
        ("m1", "binary", "C major", (4, 4), 120),
        ("m2", "ternary", "F major", (3, 4), 66),
    ):
        rows = build_form_graph(_PIECE, form, key, tempo_bpm=tempo, meter=meter, movement_id=mid)
        for sec in sorted({r["section"] for r in rows if "section" in r}):
            run_scales_section(_PIECE, sec)
    graph = PieceGraph.load(str(_WORKSPACE / _PIECE / "piece_graph.json"))
    yield graph
    shutil.rmtree(_WORKSPACE / _PIECE, ignore_errors=True)


def _tags(path):
    raw = open(path).read()
    work = re.search(r"<work-title>(.*?)</work-title>", raw)
    mvt = re.search(r"<movement-title>(.*?)</movement-title>", raw)
    return (work.group(1) if work else None), (mvt.group(1) if mvt else None)


def test_the_full_score_carries_a_work_title(two_movements):
    work, _ = _tags(assemble(two_movements, scope="full"))
    assert work, "the exported MusicXML has no <work-title> at all"
    assert "Sonatina" in work, work


def test_one_movement_is_titled_by_its_movement_not_by_the_work(two_movements):
    work, mvt = _tags(assemble(two_movements, scope="movement-m2"))
    assert work and "Sonatina" in work, work
    assert mvt and mvt != work, f"movement-title just repeats the work title: {mvt!r}"
    assert mvt.startswith("II."), mvt


def test_the_title_is_not_the_piece_id(two_movements):
    """A score titled `test-titles-20260827` announces what it is."""
    work, _ = _tags(assemble(two_movements, scope="full"))
    assert _PIECE not in work, work
