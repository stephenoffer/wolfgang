"""A cadence that avoids closure must not be given the strongest close.

Three cadence tables in `sketch_proposer` mapped `CadenceTarget` values and fell
through to the PAC's answers. `CadenceTarget` has eight members; the tables
covered five, so:

    evaded  -> soprano ^1, bass V-I     the resolution NOT arriving is what
                                        defines an evaded cadence
    none    -> soprano ^1, bass V-I     "no cadence here" became a full
                                        authentic cadence

`_cadence_soprano_degree`'s caller already guarded `none`; `_build_cadence` did
not, so a phrase explicitly planned not to close was handed ^1 over V-I.

Fifth instance of one shape (Addenda 73-76): a lookup whose fallback is the most
stable, most consonant, most closed answer available — which is exactly what
makes a wrong answer inaudible as wrongness.
"""

import pytest

from scales.models import CadenceTarget, PhraseSlot
from scales.sketch_proposer import (
    SketchProposer,
    _cadence_bass_motion,
    _cadence_soprano_degree,
    _cadence_soprano_int,
)


def _slot(target: str) -> PhraseSlot:
    return PhraseSlot(phrase_id="p1", section_id="m1_a", bar_start=1, bar_count=4,
                      key="C major", meter=(4, 4), tempo_bpm=90, cadence_target=target)


def test_an_evaded_cadence_does_not_land_on_the_tonic():
    """The soprano avoiding ^1 is the gesture."""
    assert _cadence_soprano_degree(CadenceTarget.EVADED.value) != "^1"
    assert _cadence_soprano_int(CadenceTarget.EVADED.value) != 1


def test_an_evaded_cadence_withholds_its_resolution():
    assert _cadence_bass_motion(CadenceTarget.EVADED.value) != "V-I"


def test_a_perfect_cadence_still_closes():
    """Falsification: the fix must not weaken the cadence that should close."""
    assert _cadence_soprano_degree(CadenceTarget.PAC.value) == "^1"
    assert _cadence_bass_motion(CadenceTarget.PAC.value) == "V-I"


@pytest.mark.parametrize("target", ["none", ""])
def test_no_cadence_means_no_cadence(target):
    sp = SketchProposer.__new__(SketchProposer)
    approach = sp._build_cadence(_slot(target))
    assert approach.soprano_arrival_degree == 0
    assert approach.bass_motion == ""


def test_a_real_cadence_still_gets_its_approach():
    sp = SketchProposer.__new__(SketchProposer)
    approach = sp._build_cadence(_slot(CadenceTarget.PAC.value))
    assert approach.soprano_arrival_degree == 1
    assert approach.bass_motion == "V-I"


def test_every_cadence_type_has_an_explicit_reading():
    """The tables silently covered five of eight members. Anything not listed
    took the PAC's answers, so a missing entry was invisible."""
    unlisted = [
        m.value for m in CadenceTarget
        if m.value not in ("none",)
        and _cadence_soprano_degree(m.value) == "^1"
        and _cadence_bass_motion(m.value) == "V-I"
        and m.value not in ("PAC", "elided")
    ]
    assert not unlisted, f"still falling through to the PAC default: {unlisted}"
