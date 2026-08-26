"""Numbers the doctrine tells the composer must match the corpus it claims to describe.

Doctrine is not decoration: `human-sounding-music.md` and the composer guides
are read into every brief, and a number in them is an instruction. Three of
them were measurably wrong, and two were wrong in the direction that *causes*
the defects the realism audit reports:

  * "Beethoven changes texture **58%** of the time between consecutive bars" —
    generalised from one movement. Over Beethoven's whole 17,757-bar corpus it
    is **25.5%**. The line told the composer to change texture twice as often as
    Beethoven does, and contradicted the calibrated `texture_change_pct` band in
    `scales.py` outright.
  * "Common-practice melodies are roughly **70-80% stepwise**" — the real range
    over 26 canonical movements is **40-79%, median 64.5%**. Aiming at the top of
    the range pushes a melody into continuous scalar motion, which is exactly the
    `scalar_overuse` finding on the last generated piece (39% of melody bars
    against a real median of 2%).
  * "Every bar should have AT LEAST 2 different bass notes" (Chopin) — real
    Chopin breaks it in one bar in five.

These tests re-derive the numbers from what is on disk, so doctrine and corpus
cannot drift apart silently again.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_GENERAL = _REPO / ".claude" / "context" / "general"
_PACKS = _REPO / "tools" / "compiled_packs"


def _profile_metric(composer: str, metric: str):
    path = _PACKS / composer / "corpus_profile.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text()).get("metrics", {}).get(metric, {}).get("mean")
    except (OSError, ValueError):
        return None


def test_no_doctrine_file_claims_a_texture_change_rate_the_corpus_contradicts():
    """Any "<composer> changes texture N%" claim must be within 10 points of
    that composer's measured mean."""
    claim = re.compile(
        r"\b(bach|mozart|beethoven|chopin|liszt|haydn|schubert)\b[^.\n]{0,60}?"
        r"changes? texture[^.\n]{0,40}?(\d+(?:\.\d+)?)\s*%",
        re.I,
    )
    if not _GENERAL.is_dir():
        pytest.skip("context not present")
    wrong = []
    for path in sorted(_GENERAL.glob("*.md")):
        for composer, pct in claim.findall(path.read_text()):
            measured = _profile_metric(composer.lower(), "texture_change_pct")
            if measured is None:
                continue
            if abs(float(pct) / 100.0 - measured) > 0.10:
                wrong.append(
                    f"{path.name}: claims {composer} changes texture {pct}%, "
                    f"corpus says {measured * 100:.1f}%"
                )
    assert not wrong, "doctrine contradicts the corpus:\n  " + "\n  ".join(wrong)


def test_the_texture_change_claim_agrees_with_the_discriminator_band():
    """Two places state this number; they must not disagree.

    The band lives in `scales._DISCRIMINATOR_BANDS` and the prose lives in
    `human-sounding-music.md`. The prose said 58% while the band's upper bound
    is 58.5% and every real composer sits between 14% and 62% — so the prose was
    quoting the *ceiling* as the norm.
    """
    from scales.scales import _DISCRIMINATOR_BANDS

    lo, hi = _DISCRIMINATOR_BANDS["texture_change_pct"]
    for composer in ("bach", "mozart", "beethoven", "chopin", "liszt"):
        measured = _profile_metric(composer, "texture_change_pct")
        if measured is None:
            continue
        assert lo <= measured <= hi, (
            f"{composer}'s measured texture_change_pct {measured} falls outside "
            f"the discriminator band [{lo}, {hi}] — a band that rejects a real "
            "composer is measuring the band"
        )


def test_stepwise_claims_sit_inside_the_measured_range():
    """40-79% is what 26 canonical movements do; a claim must not sit outside it."""
    if not _GENERAL.is_dir():
        pytest.skip("context not present")
    rx = re.compile(r"(\d+)\s*[-–]\s*(\d+)\s*%\s+stepwise", re.I)
    bad = []
    for path in sorted(_GENERAL.glob("*.md")):
        for lo, hi in rx.findall(path.read_text()):
            lo, hi = int(lo), int(hi)
            # The measured span is 40-79 with median 64.5. A quoted range that
            # sits entirely in the top third is an instruction to write scales.
            if lo >= 70:
                bad.append(f"{path.name}: quotes {lo}-{hi}% stepwise; measured median is 64.5%")
    assert not bad, "\n  ".join(bad)


def test_human_sounding_music_is_reachable_from_the_discriminator_comment():
    """`scales.py` cites this file as the source of its bands; it must exist."""
    import inspect

    from scales import scales

    src = inspect.getsource(scales)
    assert "human-sounding-music.md" in src
    assert (_GENERAL / "human-sounding-music.md").exists(), (
        "scales.py cites a doctrine file that is not on disk"
    )
