"""
Motif-driven melody materialization — shared by SurfaceComposer and Realizer.

Uses MotifObject.rhythm_cell + interval_contour at MotifPlacement / MotifSlot
locations, with basic transform algebra (state, sequence, fragment, invert).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .duration import DURATION_VALUES
from .enums import MotifTransformOp, NoteRole
from .models import MotifObject, MotifPlacement, MotifSlot
from .pitch import clamp_to_range, midi_to_pitch, snap_to_scale


def _apply_transform(
    intervals: List[int],
    rhythms: List[str],
    op: str,
    params: dict,
) -> Tuple[List[int], List[str]]:
    """Return transformed (intervals, rhythms) lists."""
    op_l = (op or MotifTransformOp.STATE.value).lower()
    ints = list(intervals)
    rhys = list(rhythms)

    if op_l == MotifTransformOp.SEQUENCE.value:
        steps = int(params.get("steps", params.get("degree", 2)))
        ints = [i + steps for i in ints]
    elif op_l == MotifTransformOp.INVERT.value:
        ints = [-i for i in ints]
    elif op_l == MotifTransformOp.FRAGMENT.value:
        n = max(1, len(ints) // 2)
        ints = ints[:n]
        rhys = rhys[: n + 1] if len(rhys) > n + 1 else rhys[: max(1, len(rhys) // 2)]
    elif op_l == MotifTransformOp.AUGMENT.value:
        ints = ints + ints
        rhys = rhys + rhys
    elif op_l == MotifTransformOp.RETROGRADE.value:
        ints = list(reversed(ints))
        rhys = list(reversed(rhys))

    return ints, rhys


def _motif_note_midis(start_midi: int, intervals: List[int], scale: List[int]) -> List[int]:
    cur = clamp_to_range(start_midi, 55, 90)
    out: List[int] = [cur]
    for step in intervals:
        cur = snap_to_scale(cur + int(step), scale)
        out.append(clamp_to_range(cur, 55, 90))
    return out


def emit_motif_melody_events(
    motif: MotifObject,
    placement: MotifPlacement,
    key: str,
    scale: List[int],
    start_midi: int,
    beats_per_bar: float = 4.0,
) -> List[Dict[str, Any]]:
    """Return list of {bar, beat, pitch, duration, role} for RH melody."""
    rhythms = list(motif.rhythm_cell or [])
    intervals = list(motif.interval_contour or [])
    if not rhythms:
        return []

    intervals, rhythms = _apply_transform(
        intervals,
        rhythms,
        placement.transform,
        placement.params or {},
    )
    n_notes = len(rhythms)
    if n_notes < 1:
        return []

    iv_use = intervals[: max(0, n_notes - 1)]
    midis = _motif_note_midis(start_midi, iv_use, scale)
    while len(midis) < n_notes:
        midis.append(midis[-1])
    midis = midis[:n_notes]

    events: List[Dict[str, Any]] = []
    bar = placement.bar
    beat = float(placement.beat)
    for j in range(n_notes):
        dur = rhythms[j] if j < len(rhythms) else "q"
        events.append(
            {
                "bar": bar,
                "beat": beat,
                "pitch": midi_to_pitch(midis[j], key),
                "duration": dur,
                "role": NoteRole.STRUCTURAL.value
                if j in (0, n_notes - 1)
                else NoteRole.PASSING.value,
            }
        )
        beat += float(DURATION_VALUES.get(dur, 1.0))
        while beat > beats_per_bar + 0.001:
            beat -= beats_per_bar
            bar += 1
    return events


def pick_motif_slot_for_bar(
    motif_slots: List[MotifSlot],
    bar: int,
) -> Optional[MotifSlot]:
    for ms in motif_slots:
        if ms.bar == bar and ms.voice in ("melody", "soprano", ""):
            return ms
    return None


def pick_motif_placement_for_bar(
    placements: List[MotifPlacement],
    bar: int,
) -> Optional[MotifPlacement]:
    for mp in placements:
        if mp.bar == bar and mp.voice in ("melody", "soprano", ""):
            return mp
    return None


def first_scale_degree_midi(motif: MotifObject, scale: List[int]) -> Optional[int]:
    """If motif has scale_degree_contour, return MIDI for first degree (^1 = 1)."""
    degs = motif.scale_degree_contour
    if not degs:
        return None
    d0 = int(degs[0])
    idx = (d0 - 1) % 7
    if 0 <= idx < len(scale):
        return scale[idx]
    return None
