"""The style's own scoring preferences reached the orchestrator as silence.

Three empty drawers stacked behind one another, each hiding the next:

  1. `_pass_orchestration` was a stub returning `{"instruments": {}}` for all 55
     composers, so the pack was empty.
  2. `style_resolver` listed `orchestration_roles.json` among the files to load
     and never assigned the field, so the program was empty.
  3. `orchestrate_section` read `getattr(program, "orchestration_roles", None)`
     — and that field is on **StyleDNA**, which StyleProgram wraps. It read the
     wrong object and got `None` forever, with no error anywhere.

And behind those, a shape mismatch: `plan_orchestration` reads
`style_roles["melody"]` and expects an instrument NAME, while the packs hold the
opposite mapping — instrument name to role description. Handing the raw dict over
produced `None` for melody and, for Chopin, an `InstrumentRole` OBJECT for bass,
which failed an `in ensemble` test and fell back silently.

Fixing any one of the four would have changed nothing measurable, which is why
each survived: every layer had an empty layer behind it.

    beethoven          roles 0 -> 13
    chopin             roles 0 -> 20
    mozart             roles 0 -> 38
    style__classical   roles 0 -> 49
"""

import pytest

from scales.scales import _style_role_assignments
from scales.style_resolver import StyleResolver, _parse_register

_ENSEMBLE = ["violin_i", "violin_ii", "viola", "cello", "flute", "oboe", "horn"]


def _roles(composer):
    program = StyleResolver().resolve_program(composer)
    return program.dna.orchestration_roles


@pytest.mark.parametrize("composer", ["mozart", "chopin", "beethoven", "style__classical"])
def test_the_roles_reach_the_program(composer):
    """They were `None` at the consumer for every composer, forever."""
    assert len(_roles(composer)) >= 10, f"{composer} carries no orchestration roles"


def test_the_planner_gets_instrument_names_not_role_objects():
    """The shape the planner actually reads."""
    assigned = _style_role_assignments(_roles("style__classical"), _ENSEMBLE)
    assert assigned.get("melody") == "violin_i"
    assert assigned.get("bass") == "cello"
    assert all(isinstance(v, str) for v in assigned.values())


def test_an_instrument_not_in_the_ensemble_is_never_proposed():
    """`plan_orchestration` checks `in ensemble` and falls back; proposing a
    part that is not there wastes the check and hides the style's real choice."""
    assigned = _style_role_assignments(_roles("style__classical"), ["flute", "harp"])
    assert all(v in ("flute", "harp") for v in assigned.values())


def test_a_composer_whose_profile_states_no_function_proposes_nothing():
    """Beethoven's orchestration tables carry no function column. Guessing a
    melody instrument from a table that does not name one would be inventing a
    scoring preference and attributing it to him."""
    assert _style_role_assignments(_roles("beethoven"), _ENSEMBLE) == {}


# ─── Registers ───────────────────────────────────────────────────────────────


def test_a_written_register_is_read_as_midi():
    assert _parse_register("C1-E3") == (24, 52)
    assert _parse_register("G4-C6") == (67, 84)


def test_an_unwritten_register_falls_back_rather_than_guessing():
    """The dataclass default means "unstated" — the planner has its own
    per-instrument ranges and they are better than a guess."""
    assert _parse_register("LH, lowest note of arpeggio") == (60, 84)
    assert _parse_register("") == (60, 84)


def test_the_range_column_wins_over_the_hand_column():
    """Chopin's table heads two columns `Hand/Register` and `Register Range`.
    Matching "register" first claimed the hand column, so the entry carried
    "LH, lowest note of arpeggio" as its register and the real `C1-E3` was
    never read."""
    ranged = [r for r in _roles("chopin").values() if r.register_range != (60, 84)]
    assert ranged, "no Chopin voice carries a real register"
    assert any(r.register_range[0] < 40 for r in ranged), "the bass register is missing"
