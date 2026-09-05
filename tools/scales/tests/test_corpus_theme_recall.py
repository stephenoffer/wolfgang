"""Falsification, the other half: does the detector FIND what is definitely there?

Every other calibration harness in this directory asks "would this reject real
music?". That question cannot catch a detector that is simply blind — one that
never fires, on anything, and therefore never rejects anything either.

`theme_recurrence` failed exactly that way for a long time without being noticed.
It matched the theme's WHOLE interval contour, which for one Mozart sonata is 47
intervals and has no chance of recurring intact, so it reported "the theme
appears in 1 place" on every piece it was ever run on — a finding that was
repeated as fact and was purely an artifact.

Mozart K.331/i is a theme with six variations, and this corpus stores each
variation as its own file. That gives real ground truth: six pieces of material
that *provably* contain the theme. Measured across matchers:

    matcher                     variations found   unrelated matched
    contour + rhythm, head 3-6        0 / 6              0 / 6
    contour only, head 3              6 / 6              5 / 6
    contour only, head 4              4 / 6              2 / 6
    contour only, head 5-6            0 / 6              0 / 6

Requiring rhythm guarantees failure, because rhythm is what a variation changes.
A three-interval contour finds everything and also matches five of six unrelated
Chopin mazurkas. There is no operating point with both sensitivity and
specificity, which is why the function is documented as a lower bound and why
`theme_return_evidence` prefers the plan's own placements.

These tests pin the floor (it must still find most of what is provably there)
and the ceiling (it must not match everything).
"""

import glob

import pytest

from scales.duration import beats_to_dur
from scales.models import LayerEvent, LayerIR
from scales.theme_planner import theme_recurrence

pytestmark = pytest.mark.calibration

# Measured at head=4: four of six provable returns found, two of six unrelated
# movements matched. Both bounds are deliberately loose — the point is to catch
# a detector that has gone blind or gone indiscriminate, not to pin an exact
# rate that will drift with the corpus.
_MIN_RECALL = 0.5
_MAX_FALSE_RATE = 0.5


class _Phrase:
    def __init__(self, realized):
        self.realized = realized


class _Graph:
    def __init__(self, phrases):
        self.phrases = phrases


def _melody(path):
    import music21 as m21

    s = m21.converter.parse(path)
    parts = list(s.parts)
    if len(parts) < 2:
        return []
    out = []
    for m in parts[0].getElementsByClass("Measure"):
        if m.number is None:
            continue
        for v in list(m.voices) or [m]:
            for n in v.notes:
                try:
                    d = beats_to_dur(n.duration.quarterLength)
                except Exception:
                    d = "q"
                out.append(
                    LayerEvent(
                        bar=m.number,
                        beat=1.0 + float(n.offset),
                        pitch=max(n.pitches, key=lambda p: p.midi).nameWithOctave,
                        duration=d,
                    )
                )
            break
    return sorted(out, key=lambda e: (e.bar, e.beat))


def _as_graph(events):
    return _Graph(
        {
            "m1_a_p1": _Phrase(
                {
                    "principal_line": [
                        {"bar": e.bar, "beat": e.beat, "pitch": e.pitch, "duration": e.duration}
                        for e in events
                    ]
                }
            )
        }
    )


def _variations():
    files = sorted(glob.glob("tools/reference_scores/mozart-piano-sonatas/kern/sonata11-1*.krn"))
    if len(files) < 4:
        pytest.skip("K.331/i variations not present")
    theme = _melody(files[0])
    if len(theme) < 8:
        pytest.skip("theme did not parse")
    others = [(f, _melody(f)) for f in files[1:]]
    others = [(f, m) for f, m in others if len(m) >= 8]
    if len(others) < 3:
        pytest.skip("not enough variations parsed")
    return theme, others


def _theme_ir(events, n_bars=4):
    bars = sorted({e.bar for e in events})[:n_bars]
    ir = LayerIR(key="A major")
    ir.principal_line = [e for e in events if e.bar in bars]
    return ir


def test_the_detector_finds_a_theme_that_is_provably_there():
    """The blindness test. A detector that never fires never rejects either."""
    theme, others = _variations()
    ir = _theme_ir(theme)
    found = sum(1 for _f, m in others if theme_recurrence(_as_graph(m), ir)["recurrences"])
    recall = found / len(others)
    assert recall >= _MIN_RECALL, (
        f"the theme was found in only {found} of {len(others)} variations that "
        f"provably contain it ({recall:.0%}) — the matcher has gone blind"
    )


def test_the_detector_does_not_match_everything():
    """The other failure: loosen until it fires on unrelated music."""
    theme, _others = _variations()
    ir = _theme_ir(theme)
    unrelated = [
        _melody(p)
        for p in sorted(
            glob.glob("tools/reference_scores/chopin-mazurkas/**/*.krn", recursive=True)
        )[:6]
    ]
    unrelated = [m for m in unrelated if len(m) >= 40]
    if len(unrelated) < 3:
        pytest.skip("not enough unrelated movements parsed")
    matched = sum(1 for m in unrelated if theme_recurrence(_as_graph(m), ir)["recurrences"])
    rate = matched / len(unrelated)
    assert rate <= _MAX_FALSE_RATE, (
        f"a Mozart theme matched {matched} of {len(unrelated)} unrelated Chopin "
        f"mazurkas ({rate:.0%}) — the matcher is indiscriminate"
    )


def test_the_result_advertises_that_it_is_a_lower_bound():
    """A caller must not be able to mistake this for a count."""
    from scales.theme_planner import _RECURRENCE_FALSE_RATE, _RECURRENCE_RECALL

    assert 0 < _RECURRENCE_RECALL < 1
    assert 0 < _RECURRENCE_FALSE_RATE < 1
    assert theme_recurrence.__doc__ and "lower bound" in theme_recurrence.__doc__.lower()
