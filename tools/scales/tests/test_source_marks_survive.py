"""A score loaded as SOURCE must arrive with its markings on it.

`parse_musicxml_to_events` read pitch, duration and dynamic and nothing else, so
every mode that loads a source score — `reduce_to_piano`, `orchestrate`,
`variation`, `style_transfer`, `continue_piece`, five of the six — saw the music
with its articulation, phrasing, ornaments and ties stripped off. A Clara
Schumann polonaise carrying 27 slurs reduced to a piano part carrying none: the
reduction could not preserve phrasing it was never shown.

Slurs are SPANNERS rather than note attributes, which is why reading
`element.articulations` alone never found them.
"""

import pytest

music21 = pytest.importorskip("music21")

from scales.music_io import _get_marks, parse_musicxml_to_events  # noqa: E402
from scales.role_decomposer import RoleEvent  # noqa: E402


def _note_with(**kw):
    n = music21.note.Note("C4")
    if kw.get("slur"):
        other = music21.note.Note("D4")
        sl = music21.spanner.Slur([n, other])
        music21.stream.Stream([n, other, sl])
    if kw.get("articulation"):
        n.articulations.append(music21.articulations.Staccato())
    if kw.get("tie"):
        n.tie = music21.tie.Tie("start")
    return n


def test_an_articulation_is_read_off_the_note():
    assert _get_marks(_note_with(articulation=True)).get("articulation") == "staccato"


def test_a_tie_is_read_off_the_note():
    assert _get_marks(_note_with(tie=True)).get("tie") == "start"


def test_a_slur_is_found_even_though_it_is_a_spanner():
    """The reason the original extractor missed every slur in every source."""
    assert _get_marks(_note_with(slur=True)).get("slur") == "start"


def test_a_plain_note_gains_no_marks():
    assert _get_marks(music21.note.Note("C4")) == {}


def test_the_role_event_carries_the_marks_it_is_given():
    ev = RoleEvent(pitch="C4", slur="start", articulation="staccato", tie="start")
    assert (ev.slur, ev.articulation, ev.tie) == ("start", "staccato", "start")


def test_a_real_score_round_trips_its_slur_count():
    """27 slurs in the source is 54 endpoints — start and stop — in the events."""
    import pathlib
    import tempfile

    path = next(p for p in music21.corpus.getCorePaths() if "polonaise_op1n1" in str(p))
    sc = music21.corpus.parse(path)
    n_slurs = len(list(sc.recurse().getElementsByClass(music21.spanner.Slur)))
    with tempfile.TemporaryDirectory() as d:
        out = str(pathlib.Path(d) / "src.musicxml")
        sc.write("musicxml", fp=out)
        events, _ = parse_musicxml_to_events(out)
    endpoints = sum(1 for e in events if e.get("slur"))
    assert n_slurs > 0
    assert endpoints == 2 * n_slurs
