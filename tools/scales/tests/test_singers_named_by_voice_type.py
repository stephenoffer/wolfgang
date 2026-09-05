"""Singers named by VOICE TYPE must be recognised as people.

`_infer_instrumentation` knew the words "voice", "voices", "choir" and "satb",
so it read "a sacred motet for four voices" correctly — and read "a sacred
piece for soprano, alto, tenor and bass" as `solo_piano`. Four singers, named
plainly, got a grand staff, the pianist's hand-span limit and no vocal range
check: the motet failure that module's docstring describes as fixed, wearing
different words.

The naive repair is worse than the defect, which is why both halves are pinned
here. Voice types are shared with instruments — "bass clarinet", "alto
saxophone", "tenor trombone", "double bass" — and several of them ("tenor",
"cantus", "bass") also name a REGISTER in keyboard writing, so "a chorale
prelude for organ with the cantus in the tenor" must stay a keyboard work.
"""

import pytest

from scales.scales import _infer_instrumentation, _singer_voice_types

SINGERS = [
    "a sacred piece for soprano, alto, tenor and bass",
    "an art song for soprano and piano",
    "a duet for soprano and alto",
    "a lament for solo contralto and organ",
    "a song for mezzo-soprano and harpsichord",
    "a bass aria with continuo",
    "an aria for tenor and strings",
    "a psalm setting for countertenor and baritone",
]

#: Every one of these names an instrument or a line in a keyboard texture.
NOT_SINGERS = [
    "a piece for bass clarinet and piano",
    "a duo for alto saxophone and piano",
    "a sonata for tenor trombone and organ",
    "a piece for double bass and piano",
    "a quartet with alto flute",
    "a piece for soprano recorder and harpsichord",
    "a chorale prelude for organ with the cantus in the tenor",
    "a fugue for keyboard whose tenor entry is inverted",
    "a toccata for organ over a walking bass",
    "an aria with figured bass realized at the harpsichord",
    "a concerto for double bass and orchestra",
]


@pytest.mark.parametrize("description", SINGERS)
def test_a_named_voice_type_hires_a_singer(description):
    assert _infer_instrumentation(description) == "choir", description


@pytest.mark.parametrize("description", NOT_SINGERS)
def test_an_instrument_sharing_a_voice_name_is_not_a_singer(description):
    assert _infer_instrumentation(description) != "choir", description


def test_the_existing_three_classes_still_decide_as_before():
    """The words that already worked must not regress behind the new class."""
    assert _infer_instrumentation("a sacred motet for four voices") == "choir"
    assert _infer_instrumentation("a two-voice invention in D minor for keyboard") is None
    assert _infer_instrumentation("a chorale prelude for organ") is None
    assert _infer_instrumentation("an organ mass") is None
    assert _infer_instrumentation("a string quartet in G major") == "ensemble"
    assert _infer_instrumentation("a nocturne for solo piano") is None


def test_four_singers_are_not_given_a_pianists_hand():
    """The failure that started this: hand span is a STRICT physical constraint,
    and it was being applied to Tenor and Bassus as one hand."""
    from scales.models import is_keyboard, is_vocal
    from scales.piece_graph import PieceGraph

    inst = _infer_instrumentation("a sacred piece for soprano, alto, tenor and bass")
    assert is_vocal(inst) and not is_keyboard(inst)

    graph = PieceGraph()
    graph.contract.target.instrumentation = inst
    from scales.scales import _physical_constraints

    assert not _physical_constraints(graph).keyboard


def test_a_voice_type_is_read_in_context_not_as_a_bare_word():
    """The guard is positional; a word list alone cannot do this."""
    assert _singer_voice_types("for soprano and piano") == {"soprano"}
    assert _singer_voice_types("for bass clarinet") == set()
    assert _singer_voice_types("for double bass") == set()
    assert _singer_voice_types("the tenor line of the fugue") == set()
    # plurals collapse to one voice, so "two distinct types" means two people
    assert _singer_voice_types("sopranos and soprano") == {"sopranos", "soprano"}
