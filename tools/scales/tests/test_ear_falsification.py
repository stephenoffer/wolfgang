"""The ear's bar-record detectors, measured against real music.

CLAUDE.md's standing rule: "Falsify every rule against real scores. Before any
check is allowed to block or even warn at scale, ask whether it would reject
canonical music, and test it." A detector that fires on most of the repertoire is
noise the critic has to triage away, which is worse than no detector.

These bounds are what the detectors measure TODAY on the rebuilt corpus. They are
deliberately loose — the point is to catch a regression that makes a detector
start rejecting real music, not to pin an exact number.

Marked `calibration` because it reads the corpus; run with `pytest -m calibration`.
"""

import collections

import pytest

from scales import musical_ear as ME
from scales.composition_brief import _iter_corpus_bars

pytestmark = pytest.mark.calibration

_COMPOSERS = ("mozart", "beethoven", "chopin", "bach", "haydn")

# detector -> the most real movements it may fire on, as a fraction.
# unresolved_nct began at 0.83 (10 of 12 real Mozart movements, every case a
# secondary dominant's leading tone inside an arpeggio) before three conditions
# were added; see its docstring.
_MAX_FALSE_POSITIVE_RATE = {
    "unresolved_nct": 0.20,
    "no_breathing": 0.35,
    "monotony": 0.35,
    "arpeggiated_melody": 0.45,
    "static_bass": 0.45,
}


def _movements(composer, minimum=16, cap=12):
    by = collections.defaultdict(list)
    for bar in _iter_corpus_bars(composer):
        by[bar.get("source")].append(bar)
    out = [sorted(v, key=lambda b: b.get("bar_num", 0)) for v in by.values() if len(v) >= minimum]
    return out[:cap]


@pytest.mark.parametrize("name,rate", sorted(_MAX_FALSE_POSITIVE_RATE.items()))
def test_a_detector_may_not_fire_on_most_of_the_repertoire(name, rate):
    fn = getattr(ME, f"detect_{name}")
    fired = total = 0
    for composer in _COMPOSERS:
        movements = _movements(composer)
        if not movements:
            continue
        total += len(movements)
        fired += sum(1 for m in movements if fn(m))
    if not total:
        pytest.skip("no corpus available")
    observed = fired / total
    assert observed <= rate, (
        f"detect_{name} fires on {fired}/{total} = {observed:.0%} of real movements "
        f"(bound {rate:.0%}). A check that rejects canonical music is broken, not strict."
    )


def test_no_bar_record_detector_reports_an_error_on_real_music():
    """Only PHYSICAL defects may be errors, and real scores have none."""
    offenders = []
    for composer in _COMPOSERS:
        for movement in _movements(composer):
            for name in _MAX_FALSE_POSITIVE_RATE:
                for finding in getattr(ME, f"detect_{name}")(movement):
                    if finding.get("severity") == "error":
                        offenders.append(f"{name} on {movement[0].get('source')}")
    assert not offenders, "error-severity findings on real music: " + "; ".join(offenders[:5])
