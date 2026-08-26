"""Load + sample corpus Roman-numeral progression models (built by
scripts/build_progression_model.py). Replaces hard-coded I-IV-V templates with
idiomatic, corpus-derived progressions, constrained to start on tonic and land
on the slot's cadence target.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from .pitch import is_minor_key

_COMPILED_PACKS = Path(__file__).resolve().parent.parent / "compiled_packs"
_CACHE: Dict[str, Any] = {}


def load_progression_model(composer_id: str, style: str = "") -> Optional[Dict[str, Any]]:
    """Composer model first, then style aggregate, else None (caller falls back)."""
    for key in (composer_id or "").lower(), (style or "").lower():
        if not key:
            continue
        if key in _CACHE:
            if _CACHE[key] is not None:
                return _CACHE[key]
            continue
        from .style_registry import pack_dir_name

        try:
            safe = pack_dir_name(key)
        except ValueError:
            continue
        path = _COMPILED_PACKS / safe / "progression_model.json"
        data = None
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                data = None
        _CACHE[key] = data
        if data is not None:
            return data
    return None


def _weighted(counter: Dict[str, int], rng: random.Random, exclude=()) -> Optional[str]:
    items = [(k, w) for k, w in counter.items() if k not in exclude and w > 0]
    if not items:
        return None
    total = sum(w for _, w in items)
    r = rng.uniform(0, total)
    acc = 0.0
    for k, w in items:
        acc += w
        if r <= acc:
            return k
    return items[-1][0]


def _is_dominant_function(symbol: str, mode: str = "major") -> bool:
    """Does this Roman numeral resolve to the tonic as a dominant?

    Only two degrees do: the fifth (V/v, with any figure or inversion) and the
    LEADING-TONE chord (viio, viiø, and their inversions; ``#viio`` in minor,
    where the seventh has to be raised to be a leading tone).

    The distinctions matter and are easy to get wrong:
    - ``vi`` is not ``v`` — a prefix test on "v" accepts the submediant, which
      makes vi-I, a deceptive resolution backwards, not a cadence.
    - ``VII`` (uppercase) in minor is the SUBTONIC, a whole tone below the
      tonic. It has no leading tone and no dominant function; ``bVII`` even
      less so. Only lowercase ``vii`` is the leading-tone chord.
    """
    sym = str(symbol or "").strip()
    if not sym:
        return False
    sym = sym.split("/")[0]  # "V7/V" is still a dominant where it stands
    if sym.startswith("b"):
        return False  # a flattened degree is never the leading-tone chord
    body = sym.lstrip("#")
    stem = ""
    for ch in body:
        if ch in "ivIV":
            stem += ch
        else:
            break
    if not stem:
        return False
    lower = stem.lower()
    if lower == "v":
        return True
    # Leading-tone chord: lowercase only. "VII" is the subtonic.
    return lower == "vii" and stem.islower()


def _backoff(mb: Dict[str, Any], plan: List[str], order: int, rng, exclude=()) -> Optional[str]:
    """Next chord from the longest context the model actually has data for.

    The sampler used to jump straight from "no order-2 context" to the UNIGRAM
    distribution — a draw from the composer's marginal chord frequencies with no
    memory at all. That happens on the second bar of every phrase (there is no
    two-chord context yet) and on every sparse context after it, so a large share
    of the harmony in every generated piece was a context-free random chord. An
    order-1 backoff is the difference between "what follows a tonic" and "what
    this composer plays a lot of".
    """
    trans, trans1, uni = mb.get("trans", {}), mb.get("trans1", {}), mb.get("uni", {})
    if len(plan) >= order:
        got = _weighted(trans.get("|".join(plan[-order:]), {}), rng, exclude=exclude)
        if got:
            return got
    if plan:
        got = _weighted(trans1.get(plan[-1], {}), rng, exclude=exclude)
        if got:
            return got
    return _weighted(uni, rng, exclude=exclude)


# Romans that colour a phrase rather than establishing one: borrowed, applied,
# altered or chromatic. A statement should be plainly in its key; a departure or
# a crisis is where these belong.
# In a MAJOR key these are borrowed from the parallel minor even though their
# symbols carry no accidental — a lowercase tonic/subdominant/dominant, or an
# uppercase mediant/submediant/subtonic. Testing only for "b"/"#" missed all of
# them, which is how an opening statement in B-flat major came to be planned as
# `I - iv - viio - V`: `iv` is the minor subdominant and reads as a shadow, not a
# statement.
_BORROWED_IN_MAJOR = {"i", "iv", "v", "III", "VI", "VII", "bIII", "bVI", "bVII"}
_BORROWED_IN_MINOR = {"I", "IV", "V"}  # V is normal in minor; see below


def _is_chromatic(roman: str, mode: str = "major") -> bool:
    r = str(roman or "")
    if not r:
        return False
    if (
        r[0] in "b#"
        or "/" in r
        or any(x in r for x in ("Ger", "Fr", "It", "N", "+", "ø", "%"))
    ):
        return True
    # strip inversion figures before testing the numeral itself
    base = r.rstrip("0123456789")
    if mode == "major":
        return base in _BORROWED_IN_MAJOR
    # In minor, the raised-leading-tone V and viio are normal practice, so only a
    # major tonic or subdominant reads as borrowed.
    return base in {"I", "IV"}


# How diatonic each dramatic role wants its harmony to be. The progression model
# samples from the composer's transitions without regard to what the phrase is
# FOR, so an opening statement — whose own doctrine in the same brief says "clear
# periodic phrasing, diatonic harmony" — was handed `I - iv - viio - V`. A
# statement that opens on borrowed chords does not read as a statement.
_ROLE_ALLOWS_CHROMATIC = {
    "establish": False,
    "confirm": False,
    "close": False,
    "return": False,
    "extend": True,
    "depart": True,
    "intensify": True,
    "crisis": True,
    "retreat": True,
}


def sample_progression(
    model: Dict[str, Any],
    mode: str,
    bar_count: int,
    cadence: str,
    tonic: str,
    seed: int = 0,
    allow_chromatic: bool = True,
) -> Optional[List[str]]:
    """Sample a roman walk: tonic start, corpus-idiomatic middle, cadence ending.

    Returns None if the model lacks this mode.
    """
    mb = model.get("by_mode", {}).get(mode)
    if not mb:
        return None
    rng = random.Random(seed)
    order = model.get("order", 2)
    cad = mb.get("cadence_targets", {})

    # The approach chord must not BE the goal chord: a "cadence" of I-I resolves
    # nothing, and that is what the movement-end-trained table returned most
    # often (its top PAC approach to a final I was, literally, I).
    def _approach(bucket: str, default: str) -> str:
        pick = _weighted(cad.get(bucket, {}), rng, exclude=(tonic, tonic.upper(), tonic.lower()))
        return pick or default

    def _dominant_approach(default: str) -> str:
        """The chord before an authentic cadence must have DOMINANT function.

        Sampling the corpus's "what precedes a final tonic" table freely
        returned things like ``IV64`` — which makes IV64-I, a plagal cadence,
        not the perfect authentic one the planner asked for. Every phrase
        planned as a PAC could come out closing without a dominant at all, and
        a piece whose structural cadences never resolve V-I never sounds
        finished. Restrict the draw to dominant-function chords and fall back
        to a plain V7/V rather than to whatever was most frequent.
        """
        options = {
            k: w
            for k, w in (cad.get("PAC", {}) or {}).items()
            if _is_dominant_function(k, mode)
        }
        pick = _weighted(options, rng)
        return pick or default

    dom = "V7" if mode == "major" else "V"
    sub = "IV" if mode == "major" else "iv"
    sub6 = "IV6" if mode == "major" else "iv6"
    submed = "vi" if mode == "major" else "VI"
    # Every cadence type the planner can ask for gets a real formula. Four of the
    # eight fell through to `[tonic]`, so a phrase planned to end plagally, to be
    # evaded, or to elide simply ended on the tonic with no approach chord at all
    # — which is not a cadence, and is a large part of why phrases stopped rather
    # than closed.
    if cadence in ("PAC", "IAC"):
        tail = [_dominant_approach(dom), tonic]
    elif cadence == "HC":
        tail = [_approach("HC", "ii6" if mode == "major" else "iv6"), "V"]
    elif cadence in ("DC", "deceptive"):
        tail = [dom, submed]
    elif cadence == "plagal":
        # IV-I. The subdominant is the whole point; without it this was I-I.
        tail = [sub, tonic]
    elif cadence == "evaded":
        # The dominant arrives and its resolution is dodged — an inversion or a
        # submediant instead of the root-position tonic that was promised.
        tail = [dom, (tonic + "6")]
    elif cadence == "elided":
        # The cadence chord IS the next phrase's downbeat, so this phrase ends
        # leaning forward: approach, then a weak-form tonic to be overrun.
        tail = [sub6, (tonic + "6")]
    else:
        tail = [tonic]

    # Everything chromatic in this mode's vocabulary, computed once: a statement
    # should be plainly in its key, and the sampler has no idea what the phrase is
    # for unless it is told.
    chromatic_block: tuple = ()
    if not allow_chromatic:
        chromatic_block = tuple(
            r for r in (mb.get("uni") or {}) if _is_chromatic(r, mode)
        )

    n_mid = max(1, bar_count - len(tail))
    plan: List[str] = [tonic]
    while len(plan) < n_mid:
        # No exclusion of the previous chord: real music prolongs, and forbidding
        # a repeat forces the harmony to change on every bar, which is a machine
        # tell. The only guard is against a chord running more than three bars.
        # A stable role should not sit on one chord for three bars either — a
        # statement that repeats I6 three times is not prolonging, it is stalling.
        repeat_limit = 2 if not allow_chromatic else 3
        exclude = (
            (plan[-1],)
            if len(plan) >= repeat_limit and len(set(plan[-repeat_limit:])) == 1
            else ()
        )
        if chromatic_block:
            exclude = tuple(exclude) + chromatic_block
        plan.append(_backoff(mb, plan, order, rng, exclude=exclude) or tonic)
    return (plan[:n_mid] + tail)[:bar_count]


def within_bar_detail(
    composer_id: str,
    style: str,
    plan: List[str],
    key: str,
    cadence: str,
    beats: int,
    seed: int = 0,
) -> List[List[str]]:
    """Per bar, the harmonies it moves through — [] where the bar holds one chord.

    Sampled from the composer's own within-bar patterns at the composer's own
    rate, so the plan can finally express what two thirds of Mozart's bars do:
    move harmony inside the bar. A bar that holds one chord is a choice; a piece
    where EVERY bar holds one chord is the plan's limitation showing through.

    The cadence bar always gets its motion — compressing a cadence into one bar
    (ii6-I64-V7) is the single most characteristic use of the device.
    """
    model = load_progression_model(composer_id, style)
    if not model or beats < 2:
        return [[] for _ in plan]
    mode = "minor" if is_minor_key(key) else "major"
    mb = (model.get("by_mode") or {}).get(mode) or {}
    # Patterns recorded for THIS meter. They used to be keyed by how many chords
    # a bar contained and looked up by beat count, so a 4/4 bar was always handed
    # a four-chord pattern and a 3/4 bar a three-chord one: harmony changing on
    # every beat of every bar, which no composer in this corpus writes.
    pats = (mb.get("within_bar") or {}).get(str(beats)) or {}
    if not pats:
        return [[] for _ in plan]
    rng = random.Random(seed)
    total_bars = len(plan)
    # The composer's OWN rate of moving harmony inside a bar, in this meter. The
    # old code hard-coded 0.5 while its docstring claimed it used the corpus.
    rate = float((mb.get("within_rate") or {}).get(str(beats), 0.0)) or 0.35

    out: List[List[str]] = []
    accrued = 0.0
    for i, roman in enumerate(plan):
        is_cadence = i == total_bars - 1
        take = is_cadence
        if not take:
            accrued += rate
            if accrued >= 1.0:
                accrued -= 1.0
                take = True
        if not take:
            out.append([])
            continue
        # prefer a pattern that STARTS on this bar's planned harmony, so the
        # bar-level plan and the detail agree
        matching = {k: v for k, v in pats.items() if k.split("|")[0] == roman}
        chosen = _weighted(matching, rng)
        if not chosen:
            # No recorded pattern starts on this bar's harmony. Substituting one
            # that starts elsewhere made the bar plan and its own beat-by-beat
            # detail disagree — the brief printed "b3:ii7" over a frame reading
            # I64 then V7. The bar's planned chord keeps the downbeat; the
            # borrowed pattern only supplies the motion after it.
            alt = _weighted(pats, rng) or ""
            chosen = "|".join([roman] + [r for r in alt.split("|")[1:] if r])
        # Collapse consecutive repeats: a bar listed as "I|I|V" moves harmony once,
        # not twice, and printing "b3[1:I 2:I]" tells the composer to change chord
        # to the chord it is already on.
        steps: List[str] = []
        for step in (chosen or "").split("|"):
            if step and (not steps or step != steps[-1]):
                steps.append(step)
        # The cadence bar's within-bar motion has to LAND on the planned cadence
        # chord. A sampled pattern that happens to end on V turned a phrase
        # planned as a perfect cadence into one that stops on the dominant — the
        # detail silently overriding the cadence it was meant to elaborate.
        if is_cadence and steps and steps[-1] != roman:
            steps = [x for x in steps if x != roman] + [roman]
            steps = [x for i, x in enumerate(steps) if i == 0 or x != steps[i - 1]]
        out.append(steps if len(steps) > 1 else [])
    return out


def corpus_harmony_plan(
    composer_id: str,
    style: str,
    cadence: str,
    bar_count: int,
    key: str,
    seed: int = 0,
    role: str = "",
) -> Optional[List[str]]:
    """Idiomatic progression for a phrase slot, or None if no model (the caller
    then uses the hard-coded template fallback)."""
    model = load_progression_model(composer_id, style)
    if not model:
        return None
    minor = is_minor_key(key)
    mode = "minor" if minor else "major"
    tonic = "i" if minor else "I"
    return sample_progression(
        model,
        mode,
        bar_count,
        cadence,
        tonic,
        seed=seed,
        allow_chromatic=_ROLE_ALLOWS_CHROMATIC.get(role, True),
    )
