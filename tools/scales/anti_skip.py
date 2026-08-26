"""Anti-skip: detect a committed surface that ignored every briefed exemplar.

The brief puts real corpus bars in front of the agent and says "adapt — never
copy, never ignore". Nothing used to verify the second half: an agent could
write a phrase with totally different rhythmic and intervallic DNA from all the
exemplars and pass the gate. This module compares a committed melody's rhythm
and interval vocabulary against the briefed exemplars; if it resembles none of
them, the phrase is flagged ``composed_blind``.

The commit gate treats ``composed_blind`` as an **advisory warning**, not a
block (``commit_gate._DEFAULT_BLOCKING`` holds only ``meter``). This docstring
said the opposite long after the policy changed, which is worth naming: a comment
that contradicts the code is how two versions of a rule end up in one context
window. Inventing away from the corpus is a legitimate creative choice; the flag
tells the fresh-ears critic where to listen harder, and the critic decides.

Pure-Python: no music21, so it runs inside the commit path cheaply.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .pitch import pitch_to_midi

# Interval buckets (absolute semitones): unison, step, small leap, leap, big leap
_INTERVAL_BUCKETS = ["rep", "step", "small_leap", "leap", "big_leap"]


def _interval_bucket(semitones: int) -> str:
    a = abs(semitones)
    if a == 0:
        return "rep"
    if a <= 2:
        return "step"
    if a <= 4:
        return "small_leap"
    if a <= 7:
        return "leap"
    return "big_leap"


def _normalize(hist: Dict[str, float]) -> Dict[str, float]:
    total = sum(hist.values())
    if total <= 0:
        return {}
    return {k: v / total for k, v in hist.items()}


def _hist_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    """1 - 0.5*L1 over two normalized histograms → [0,1] (1 = identical)."""
    if not a or not b:
        return 0.0
    keys = set(a) | set(b)
    l1 = sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)
    return max(0.0, 1.0 - 0.5 * l1)


def _signature(midis: List[int], durs: List[str]) -> Dict[str, Dict[str, float]]:
    """Rhythm + interval histograms for one melodic line."""
    rhythm: Dict[str, float] = {}
    for d in durs:
        rhythm[d] = rhythm.get(d, 0.0) + 1.0
    intervals: Dict[str, float] = {}
    for a, b in zip(midis, midis[1:]):
        bucket = _interval_bucket(b - a)
        intervals[bucket] = intervals.get(bucket, 0.0) + 1.0
    return {"rhythm": _normalize(rhythm), "intervals": _normalize(intervals)}


# A direct_compose token: pitch+dur (E5q), chord ([C5,E5]q), rest (rest_q).
# Double accidentals are part of the grammar ("C##4", "Dbb3"); matching only one
# made those tokens fail the pattern and drop out of the signature entirely.
_TOKEN_RE = re.compile(r"^(\[[^\]]+\]|rest|[A-Ga-g](?:##|bb|--|[#b\-])?\d)(.*)$")


def signature_from_shorthand(rh: str) -> Dict[str, Dict[str, float]]:
    """Parse an exemplar RH shorthand string into a melodic signature.

    Chords contribute their top note to the melodic line; rests are skipped
    for intervals but still carry rhythm.
    """
    midis: List[int] = []
    durs: List[str] = []
    for tok in (rh or "").split():
        m = _TOKEN_RE.match(tok.strip())
        if not m:
            continue
        head, tail = m.group(1), m.group(2)
        # strip trailing expression marks (:tr, ( ), ~, < >, !) to bare dur code
        dur = re.split(r"[:(~<>!)]", tail)[0].strip("_") or "q"
        durs.append(dur)
        if head == "rest":
            continue
        if head.startswith("["):
            pitches = head[1:-1].split(",")
            top = pitches[-1].strip()
            mv = pitch_to_midi(top)
        else:
            mv = pitch_to_midi(head)
        if mv is not None:
            midis.append(mv)
    return _signature(midis, durs)


# Which LayerIR layers form the "line" for each hand. RH = the melody;
# LH = the accompaniment foundation + responses (the figure whose rhythm and
# interval vocabulary the LH composed_blind check inspects).
_RH_SIG_LAYERS = ("principal_line",)
_LH_SIG_LAYERS = ("bass_foundation", "response_layer")


def _pitch_for_hand(pitch, hand: str) -> Optional[int]:
    """A representative MIDI for an event: RH takes the top note (the melody),
    LH the bottom note (the bass line). Chords carry a list of pitches."""
    if not pitch or pitch == "rest":
        return None
    pitches = pitch if isinstance(pitch, list) else [pitch]
    midis = [m for m in (pitch_to_midi(p) for p in pitches if p != "rest") if m is not None]
    if not midis:
        return None
    return max(midis) if hand == "rh" else min(midis)


def signature_from_layer(layer, hand: str = "rh") -> Dict[str, Dict[str, float]]:
    """Rhythm+interval signature from a committed LayerIR, per hand.

    RH inspects the principal melody (top notes); LH inspects the accompaniment
    foundation (bottom notes) so a wholly-invented accompaniment that ignored
    the briefed LH vocabulary can be caught too.
    """
    names = _RH_SIG_LAYERS if hand == "rh" else _LH_SIG_LAYERS
    events = []
    for nm in names:
        events.extend(getattr(layer, nm, None) or [])
    events.sort(key=lambda e: (e.bar, e.beat))
    midis: List[int] = []
    durs: List[str] = []
    for e in events:
        durs.append(str(getattr(e, "duration", "q")))
        mv = _pitch_for_hand(getattr(e, "pitch", None), hand)
        if mv is not None:
            midis.append(mv)
    return _signature(midis, durs)


def resemblance(a: Dict[str, Dict[str, float]], b: Dict[str, Dict[str, float]]) -> float:
    """Combined rhythm+interval resemblance of two signatures, [0,1]."""
    r = _hist_similarity(a.get("rhythm", {}), b.get("rhythm", {}))
    i = _hist_similarity(a.get("intervals", {}), b.get("intervals", {}))
    return round(0.5 * r + 0.5 * i, 3)


def best_resemblance(
    surface: Dict[str, Dict[str, float]], exemplar_rhs: List[str]
) -> Tuple[float, int]:
    """Best resemblance of a surface to any briefed exemplar.

    Returns (best_score, index_of_best). Empty exemplar list → (1.0, -1) so we
    never falsely flag when there was nothing to resemble.
    """
    if not exemplar_rhs:
        return 1.0, -1
    best, best_i = 0.0, -1
    for i, rh in enumerate(exemplar_rhs):
        score = resemblance(surface, signature_from_shorthand(rh))
        if score > best:
            best, best_i = score, i
    return round(best, 3), best_i


# Below this, a surface shares almost no rhythmic/intervallic vocabulary with
# any exemplar — i.e. it was very likely composed without consulting them.
BLIND_FLOOR = 0.30
# LH accompaniment is idiomatically more repetitive and self-similar than the
# melody, so its vocabulary overlaps the exemplars more loosely — a lower floor
# avoids over-flagging real (varied) accompaniment as blind.
BLIND_FLOOR_LH = 0.22


def check_composed_blind(
    layer, exemplar_rhs: List[str], hand: str = "rh", floor: Optional[float] = None
) -> Optional[Dict[str, object]]:
    """Return a composed_blind finding if the surface (for ``hand``) resembles
    no briefed exemplar.

    ``hand='lh'`` checks the accompaniment against the briefed LH exemplars; its
    default floor is lower (BLIND_FLOOR_LH) because LH vocabulary is more
    repetitive. The returned ``check`` is ``composed_blind`` for RH and
    ``composed_blind_lh`` for LH.
    """
    if not exemplar_rhs:
        return None
    if floor is None:
        floor = BLIND_FLOOR if hand == "rh" else BLIND_FLOOR_LH
    surface = signature_from_layer(layer, hand)
    if not surface.get("rhythm") and not surface.get("intervals"):
        return None
    best, idx = best_resemblance(surface, exemplar_rhs)
    if best < floor:
        check = "composed_blind" if hand == "rh" else "composed_blind_lh"
        return {
            "check": check,
            "best_resemblance": best,
            "floor": floor,
            "n_exemplars": len(exemplar_rhs),
            "message": (
                f"{hand.upper()} surface resembles no briefed exemplar "
                f"(best {best} < {floor}); did you adapt them?"
            ),
        }
    return None
