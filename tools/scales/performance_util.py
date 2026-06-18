"""Performance humanization primitives — the deterministic source of "human
imperfection" for the MIDI render.

Two pure functions used everywhere in the performance layer:

  jitter(seed_parts, amplitude) -> float
      A STABLE pseudo-random value in [-amplitude, +amplitude] derived from a
      hash of seed_parts. This is the ONLY source of variance in the
      performance layer — never `random`/`time`/`Date`, because resume and
      caching depend on byte-identical MIDI for the same PieceGraph. Two calls
      with the same seed return the same value, across processes and runs.

  shape(frac, kind, depth) -> float
      A reusable [0,1] curve generator for hairpins, rubato, and tempo arcs —
      replaces the inline linear math that made every crescendo a straight ramp.
"""

from __future__ import annotations

import hashlib
import math
from typing import Tuple

# ─── Deterministic jitter ────────────────────────────────────────────────────


def _unit_hash(seed_parts: Tuple) -> float:
    """Map any tuple to a stable float in [0, 1) via md5 (process-independent —
    Python's hash() is salted per process and would break determinism)."""
    h = hashlib.md5(repr(seed_parts).encode("utf-8")).digest()
    # take 8 bytes -> integer -> [0,1)
    n = int.from_bytes(h[:8], "big")
    return n / float(1 << 64)


def jitter(seed_parts: Tuple, amplitude: float) -> float:
    """Deterministic value in [-amplitude, +amplitude] keyed on seed_parts.

    Use a seed that uniquely identifies the event being humanized, e.g.
    ``(bar, beat, pitch)`` for velocity micro-variance or ``(bar, beat, "rep")``
    for repeated-note variation, so distinct events get distinct (but stable)
    offsets and the same event always gets the same one.
    """
    if amplitude <= 0:
        return 0.0
    return (2.0 * _unit_hash(seed_parts) - 1.0) * amplitude


# ─── Curve shapes ────────────────────────────────────────────────────────────

_VALID_SHAPES = ("linear", "s_curve", "exp", "log", "arch")


def shape(frac: float, kind: str = "linear", depth: float = 1.0) -> float:
    """Map a progress fraction ``frac`` ∈ [0,1] to a [0,1] curve value.

    kinds:
      linear  — straight ramp (frac)
      exp     — slow start, accelerating (frac**2) — late-blooming crescendo
      log     — fast start, decelerating (sqrt) — early-blooming swell
      s_curve — slow-fast-slow (smoothstep) — the natural expressive arc
      arch    — rise to a peak at the midpoint then fall (0→1→0)

    ``depth`` blends the shaped value toward the linear one: depth=1.0 is the
    full shape, depth=0.0 is linear. Lets a per-style profile dial intensity.
    """
    f = max(0.0, min(1.0, frac))
    if kind == "exp":
        shaped = f * f
    elif kind == "log":
        shaped = math.sqrt(f)
    elif kind == "s_curve":
        shaped = f * f * (3.0 - 2.0 * f)  # smoothstep
    elif kind == "arch":
        shaped = 1.0 - abs(2.0 * f - 1.0)  # tent: 0 at ends, 1 at midpoint
    else:  # linear / unknown
        shaped = f
    d = max(0.0, min(1.0, depth))
    return shaped * d + f * (1.0 - d)
