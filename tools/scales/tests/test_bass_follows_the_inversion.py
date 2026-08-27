"""The bass note of a chord is the one its INVERSION puts there.

`Realizer._harmony_to_bass` kept its own Roman-numeral table — nineteen entries
mapping a symbol to a scale degree, with everything unlisted falling through to
`0`, the root. Only `ii6` and `I64` of all the inversions in common use were in
it, so `i6`, `I6`, `V6`, `V65`, `V43` and the rest were silently played in root
position: the notation says one thing and the bass plays another.

In G minor that put G under an `i6` where the notation says B flat, and a
subsequent scale snap moved it to B NATURAL — a note outside the key, sounding
against the melody's B flat and reported as a cross-relation.

`harmony_analysis` is this project's one Roman parser and already covered every
degree, quality and inversion.
"""

from __future__ import annotations

import pytest

from scales.duration import bar_duration
from scales.models import HarmonyEvent
from scales.pitch import midi_to_pitch
from scales.realizer import Realizer
from scales.scales import _WORKSPACE


def _bass(roman: str, key: str) -> str:
    realizer = Realizer.__new__(Realizer)
    midi = realizer._harmony_to_bass(HarmonyEvent(bar=1, beat=1.0, roman=roman), [], key)
    return midi_to_pitch(midi, key)


@pytest.mark.parametrize(
    "roman,expected",
    [
        ("i", "G"),  # root position
        ("i6", "Bb"),  # the third — was G, then B natural
        ("V", "D"),
        ("V6", "F#"),  # the leading tone, raised in minor
        ("V43", "A"),  # the seventh's second inversion puts the fifth in the bass
        ("I64", "D"),  # a cadential six-four IS the fifth in the bass
        ("iv", "C"),
        ("VI", "Eb"),
    ],
)
def test_the_bass_is_the_note_the_inversion_names(roman, expected):
    assert _bass(roman, "g minor").rstrip("0123456789") == expected


def test_the_same_holds_in_major():
    assert _bass("I", "C major").rstrip("0123456789") == "C"
    assert _bass("I6", "C major").rstrip("0123456789") == "E"
    assert _bass("V65", "C major").rstrip("0123456789") == "B"
    assert _bass("ii6", "C major").rstrip("0123456789") == "F"


def test_the_bass_stays_in_the_bass():
    """An inversion is a different NOTE, not a different register."""
    realizer = Realizer.__new__(Realizer)
    for roman in ("i", "i6", "V", "V6", "V43", "I64", "iv", "VI"):
        midi = realizer._harmony_to_bass(HarmonyEvent(bar=1, beat=1.0, roman=roman), [], "g minor")
        assert 36 <= midi <= 60, f"{roman} put the bass at midi {midi}"


def test_an_unparseable_symbol_falls_back_to_the_tonic():
    """Deliberate, and no longer the answer for most inversions in common use."""
    assert _bass("not-a-roman", "g minor").rstrip("0123456789") == "G"


def test_no_second_roman_table_is_maintained_here(function_source):
    """The table is what was wrong; a new one would be the same bug again."""
    from scales import realizer

    src = function_source(realizer, "_harmony_to_bass")
    assert "roman_pitches" in src, "the bass must come from the one Roman parser"
    assert "degree_offsets" not in src, "a second Roman-numeral table has come back"


# ─── The cadence, in the same module and the same shape ─────────────────────


def test_the_final_note_of_a_phrase_fills_its_bar():
    """`dur = "h" if anchor.role == "cadence" else "q"` — and `sketch_proposer`
    emits only "passing" and "structural".

    That branch had never once executed. Every phrase ended on a QUARTER NOTE
    and left its bar three-quarters empty, while the code read as though
    cadences were being given long notes. The final anchor IS the cadence, by
    construction: it is the last one, with nothing after it to bound its length.

    Falsified against the corpus rather than guessed. Cadential bars in real
    music are a median 100% sounding (Chopin, Beethoven, Bach, Haydn) and 75%
    in Mozart, with only 16-33% at or below half full.
    """
    from scales.duration import dur_to_beats
    from scales.piece_graph import PieceGraph
    from scales.scales import (
        build_form_graph,
        compile_style,
        init_workspace,
        run_scales_section,
    )

    piece = "_test_cadence_fills_its_bar"
    init_workspace(piece, mode="compose_from_text", description="A study in D minor")
    compile_style(piece, composers=["mozart"])
    build_form_graph(piece, form="rounded_binary", key="d minor", tempo_bpm=96, meter=(4, 4))
    # The pre-v6 path is where this realizer runs.
    run_scales_section(piece, "m1_a", use_v6_pipeline=False)

    graph = PieceGraph.load(str(_WORKSPACE / piece / "piece_graph.json"))
    checked = 0
    for state in graph.phrases.values():
        if not state.realized or not state.slot:
            continue
        last_bar = state.slot.bar_start + state.slot.bar_count - 1
        events = [e for e in state.realized.principal_line if e.bar == last_bar]
        if not events:
            continue
        sounding = sum(float(dur_to_beats(e.duration)) for e in events if e.pitch != "rest")
        capacity = float(bar_duration(tuple(state.slot.meter)))
        checked += 1
        assert sounding >= capacity * 0.75, (
            f"cadence bar {last_bar} sounds {sounding} of {capacity} beats — real "
            f"cadential bars run a median 75-100% sounding"
        )
    assert checked, "no phrases were realized"


def test_a_branch_guarded_by_a_role_nothing_emits_is_not_a_feature():
    """The anchor roles the sketch proposer produces, against the ones the
    realizer branches on. A test for the shape of the bug, not the instance."""
    import ast
    from pathlib import Path

    here = Path(__file__).resolve().parents[1]

    def _role_values(path, mode):
        """Role strings ASSIGNED (mode="set") or COMPARED (mode="test"), from the
        parse tree — a regex over the text also matches the comments explaining
        the bug, which is how the first version of this failed on itself."""
        tree = ast.parse(Path(path).read_text())
        found = set()
        for node in ast.walk(tree):
            if mode == "set" and isinstance(node, ast.keyword) and node.arg == "role":
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    found.add(node.value.value)
            if mode == "test" and isinstance(node, ast.Compare):
                left = node.left
                if isinstance(left, ast.Attribute) and left.attr == "role":
                    for cmp in node.comparators:
                        if isinstance(cmp, ast.Constant) and isinstance(cmp.value, str):
                            found.add(cmp.value)
        return found

    produced = _role_values(here / "sketch_proposer.py", "set")
    consumed = _role_values(here / "realizer.py", "test")
    assert produced, "no anchor roles found — has the proposer changed shape?"
    assert not (consumed - produced), (
        f"realizer branches on anchor role(s) nothing emits: {sorted(consumed - produced)} "
        f"(the proposer emits {sorted(produced)})"
    )
