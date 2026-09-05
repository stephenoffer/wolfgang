"""The brief did not know what the piece was scored for.

The word "instrumentation" did not appear anywhere in `composition_brief.py`. So
a four-voice motet was briefed entirely in "RH:" and "LH:", and its VOICING
section told the composer:

    Each hand spans about 3 semitones (LH) and 3 (RH) within a bar;
    the hands sit about 15 semitones apart.

A choir has no hands. Every exemplar, every named gesture and every continuity
line arrived in a vocabulary the composer had to translate before it meant
anything — and this is the document Claude reads before writing every note.

The corpus bar records genuinely ARE a two-hand reduction, so the labels change
and the measurement does not: for anything not played at a keyboard those two
staves are the upper and lower voices of the texture.
"""

from __future__ import annotations

from scales.composition_brief import piece_forces


class _Target:
    def __init__(self, instrumentation):
        self.instrumentation = instrumentation


class _Contract:
    def __init__(self, instrumentation):
        self.target = _Target(instrumentation)


class _Graph:
    def __init__(self, instrumentation):
        self.contract = _Contract(instrumentation)


def test_a_keyboard_piece_still_reads_in_hands():
    for spelling in ("solo_piano", "piano", "harpsichord", ""):
        assert piece_forces(_Graph(spelling)) == ("RH", "LH", True)


def test_a_sung_or_played_ensemble_reads_in_voices():
    for spelling in ("choir", "satb choir", "string quartet", "orchestra", "ensemble"):
        upper, lower, keyboard = piece_forces(_Graph(spelling))
        assert (upper, lower) == ("UPPER", "LOWER"), spelling
        assert not keyboard, spelling


def test_no_graph_falls_back_to_hands():
    """`render_text(brief)` is called without a graph in several places, and the
    keyboard reading is the one that can only over-report — the same default
    `is_keyboard` takes, and for the same reason."""
    assert piece_forces(None) == ("RH", "LH", True)


def test_a_dict_target_resolves_too():
    """Graphs on disk carry `contract.target` as a dict as often as a dataclass;
    reading only the attribute would silently give every loaded piece hands."""

    class _DictGraph:
        class contract:  # noqa: N801
            target = {"instrumentation": "choir"}

    assert piece_forces(_DictGraph()) == ("UPPER", "LOWER", False)


def test_the_preview_the_critic_hears_uses_the_right_instruments():
    """The music-critic judges the MIDI preview. `midi_renderer` carried a THIRD
    copy of the vocal word list — the short one, which knew "choir" but not
    "motet" — and knew nothing about strings at all. So a motet was previewed,
    and therefore reviewed, as a piano and a cello.
    """
    import music21

    from scales.midi_renderer import _score_from_parts

    parts = {"melody": [], "counter_reply": [], "response": [], "bass": []}
    expected = {
        "a sacred motet for four voices": ["Soprano", "Alto", "Tenor", "Bass"],
        "satb choir": ["Soprano", "Alto", "Tenor", "Bass"],
        "string quartet": ["Violin", "Violin", "Viola", "Violoncello"],
        # An orchestral piece really does have winds in it.
        "orchestra": ["Violin", "Clarinet", "Bassoon", "Violoncello"],
        "solo_piano": ["Piano", "Piano", "Piano", "Piano"],
    }
    for instrumentation, want in expected.items():
        score = _score_from_parts(music21.stream.Part(), music21, parts, instrumentation)
        got = [
            getattr(p.getInstrument(returnDefault=False), "instrumentName", None)
            for p in score.parts
        ]
        assert got == want, f"{instrumentation}: {got}"


def test_the_craft_advice_is_true_for_the_forces():
    """`_MINDSET` is written for a pianist, because for a long time every piece
    was one. It told the motet's composer to write "two-voice-per-hand
    polyphony" and offered `:arp` as "the most characteristic piano notation
    there is" — a rolled chord no choir can sing. The advice is sound; the
    phrasing was not."""
    from scales.composition_brief import mindset_for

    piano, voices = mindset_for(True), mindset_for(False)
    for keyboard_only in (
        "two-voice-per-hand polyphony",
        "simultaneous voices in ONE hand",
        "USE THE WHOLE KEYBOARD",
        "the most characteristic piano notation there is",
    ):
        assert keyboard_only in piano
        assert keyboard_only not in voices
    for reworded in ("two independent voices per staff", "USE THE WHOLE RANGE"):
        assert reworded in voices


def test_the_shorthand_keys_are_spelled_out_when_the_labels_change():
    """A bar dict is always `{'rh': ..., 'lh': ...}`. Renaming the exemplar
    labels to UPPER/LOWER without saying so would be exactly the contradictory
    guidance the brief exists to avoid."""
    from scales.composition_brief import mindset_for

    voices = mindset_for(False)
    assert "'rh'" in voices and "'lh'" in voices
    assert "UPPER and LOWER staff" in voices
    assert "BAR DICT KEYS STAY" in voices
