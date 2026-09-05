"""Three tables look instruments up by name, and real scores miss all three.

`RoleDecomposer._ROLE_PRIORS` is keyed `violin_1`, `cello`, `flute`. SABRE's
part-picking uses the same spellings. `validator.INSTRUMENT_RANGES` is keyed
`cello`, `double_bass`, `english_horn`. A real score's `partName` says "Violin
I", "1st Violin", "Violoncello", "Contrabass", "Cor Anglais".

Measured over the part names in real music21 scores, **11 of 15 missed**
`_ROLE_PRIORS` — every violin spelling and all four voice names — and a miss
returns `HARMONIC_PAD`. So in `reduce_to_piano` the first violin, the part
carrying the tune, was filed as filler in every real orchestral score, and SABRE
fell back to "the first part is the melody and the last is the bass", which is
true only by accident of score order.

One resolver now: `models.canonical_instrument`.
"""

from __future__ import annotations

import pytest

from scales.models import canonical_instrument

#: Every one of these appears as a `partName` in a real score.
REAL_NAMES = {
    "1st Violin": ("violin", 1),
    "2nd Violin": ("violin", 2),
    "Violin I": ("violin", 1),
    "Violin II": ("violin", 2),
    "Violin 1": ("violin", 1),
    "Violin": ("violin", None),
    "Violoncello": ("cello", None),
    "Contrabass": ("double_bass", None),
    "Double Bass": ("double_bass", None),
    "Cor Anglais": ("english_horn", None),
    "Corno inglese": ("english_horn", None),
    "Vla.": ("viola", None),
    "Fagotto": ("bassoon", None),
    "Horn 2": ("horn", 2),
    "Bassus": ("bass", None),
    "Soprano": ("soprano", None),
}


@pytest.mark.parametrize("name,expected", sorted(REAL_NAMES.items()))
def test_a_real_part_name_resolves(name, expected):
    assert canonical_instrument(name) == expected


def test_a_division_is_kept_separate_from_the_instrument():
    """"Violin I" and "Violin II" are different ROLES but the same instrument,
    so a range check wants the instrument and a role prior wants the division."""
    assert canonical_instrument("Violin I")[0] == canonical_instrument("Violin II")[0]
    assert canonical_instrument("Violin I")[1] != canonical_instrument("Violin II")[1]


def test_every_real_part_name_gets_an_orchestral_role():
    """Was 11 of 15 falling through to HARMONIC_PAD."""
    from scales.role_decomposer import RoleDecomposer

    priors = RoleDecomposer._ROLE_PRIORS
    for name in REAL_NAMES:
        key, division = canonical_instrument(name)
        divided = f"{key}_{division}" if division else ""
        instrument = divided if divided in priors else key
        assert instrument in priors, f"{name} -> {instrument} still misses"


def test_the_first_violin_is_the_melody_and_the_cello_the_bass():
    """The whole point: a reduction has to know which part is the tune."""
    from scales.role_decomposer import RoleDecomposer

    priors = RoleDecomposer._ROLE_PRIORS
    assert priors["violin_1"] == "principal_melody"
    assert priors["violin"] == "principal_melody"
    assert priors["soprano"] == "principal_melody"
    assert priors["cello"] == "bass_foundation"
    assert priors["bass"] == "bass_foundation"


def test_a_range_check_finds_the_instrument_behind_the_spelling():
    from scales.validator import INSTRUMENT_RANGES

    for name in REAL_NAMES:
        key, _ = canonical_instrument(name)
        assert key in INSTRUMENT_RANGES, f"{name} -> {key} has no range"


def test_an_unknown_name_resolves_to_itself_rather_than_guessing():
    assert canonical_instrument("Theremin") == ("theremin", None)
    assert canonical_instrument("") == ("", None)
    assert canonical_instrument(None) == ("", None)
