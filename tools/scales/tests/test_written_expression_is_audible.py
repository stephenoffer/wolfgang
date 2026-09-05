"""What the composer wrote must be audible in the preview the critic judges.

`midi_renderer` read `dynamic`, `articulation`, `ornament`, `tie` and
`technique` — and ignored `slur`, `hairpin`, `expression`, `pedal` and
`fingering`. Text and fingering do not sound, but a hairpin and a slur do:

  * rendering a phrase with and without a written crescendo produced
    BYTE-IDENTICAL velocities. Every crescendo and diminuendo the composer
    wrote, the enricher added and the assembler engraved was, to the only
    listener in the loop, not there.
  * a slur is the legato marking, and slurred and unslurred phrases came out
    with identical note lengths. Articulation was audible (staccato, tenuto and
    spiccato all gate the duration); phrasing — the mark the enricher adds most
    of — was not.

Note the measurement trap these tests avoid: music21's MIDI reader quantizes
durations to musical values, so a 1.12x legato extension reads back as exactly
1.0 and looks like no change at all. Lengths are asserted in raw TICKS.
"""

import tempfile

import pytest

from scales.midi_renderer import _hairpin_scale, _slurred_events, render_midi
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState
from scales.piece_graph import PieceGraph

music21 = pytest.importorskip("music21")


def _graph(mark_first=None, mark_last=None, field="hairpin"):
    mel = [
        LayerEvent(bar=1 + i // 4, beat=float(i % 4 + 1), pitch=p, duration="q", role="structural")
        for i, p in enumerate(["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    ]
    if mark_first:
        setattr(mel[0], field, mark_first)
        setattr(mel[-1], field, mark_last)
    layer = LayerIR(
        principal_line=mel, bass_foundation=[], meter=(4, 4), key="C major", phrase_id="p1"
    )
    g = PieceGraph()
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(
            phrase_id="p1",
            section_id="m1_a",
            bar_start=1,
            bar_count=2,
            key="C major",
            meter=(4, 4),
            tempo_bpm=90,
        ),
        realized=layer,
        agent_authored=True,
    )
    return g


def _velocities(graph):
    with tempfile.TemporaryDirectory() as d:
        sc = music21.converter.parse(render_midi(graph, output_dir=d), format="midi")
        return [n.volume.velocity for n in sc.flatten().notes if n.volume.velocity]


def _tick_lengths(graph):
    with tempfile.TemporaryDirectory() as d:
        mf = music21.midi.MidiFile()
        mf.open(render_midi(graph, output_dir=d))
        mf.read()
        mf.close()
    lens, on = [], {}
    for track in mf.tracks:
        t = 0
        for e in track.events:
            t += e.time or 0
            if e.isNoteOn() and e.velocity > 0:
                on[e.pitch] = t
            elif (e.isNoteOff() or (e.isNoteOn() and e.velocity == 0)) and e.pitch in on:
                lens.append(t - on.pop(e.pitch))
    return lens


def test_a_written_crescendo_gets_louder():
    v = _velocities(_graph("<", "!"))
    assert v[-1] - v[0] > 15, f"crescendo is inaudible: {v}"


def test_a_written_diminuendo_gets_quieter():
    v = _velocities(_graph(">", "!"))
    assert v[-1] - v[0] < -15, f"diminuendo is inaudible: {v}"


def test_the_two_hairpins_are_not_the_same_sound():
    assert _velocities(_graph("<", "!")) != _velocities(_graph(">", "!"))


def test_a_hairpin_is_narrower_than_a_step_between_written_dynamics():
    """A crescendo shapes the current level; it does not replace marking a new
    one. Runaway hairpins would make every dynamic mark meaningless."""
    scale = _hairpin_scale(
        [
            LayerEvent(
                bar=1,
                beat=float(i + 1),
                pitch="C5",
                duration="q",
                role="structural",
                hairpin=("<" if i == 0 else ("!" if i == 3 else None)),
            )
            for i in range(4)
        ]
    )
    assert scale and max(scale.values()) <= 1.20


def test_a_slur_is_played_legato():
    """Asserted in TICKS: music21's reader quantizes a 1.12x extension back to
    exactly 1.0, which is what made this look like a no-op."""
    plain = _tick_lengths(_graph())
    slurred = _tick_lengths(_graph("start", "stop", field="slur"))
    assert plain and slurred
    assert slurred[0] > plain[0], "a slur must lengthen the note under it"


def test_the_composers_own_articulation_beats_the_slur():
    """A staccato inside a slur is portato — the written mark decides, not the
    slur."""
    mel = [
        LayerEvent(bar=1, beat=float(i + 1), pitch="C5", duration="q", role="structural")
        for i in range(4)
    ]
    mel[0].slur, mel[-1].slur = "start", "stop"
    mel[1].articulation = "staccato"
    assert id(mel[1]) in _slurred_events(mel)


def test_an_unclosed_hairpin_does_not_run_to_the_end_of_the_piece():
    events = [
        LayerEvent(bar=1, beat=float(i + 1), pitch="C5", duration="q", role="structural")
        for i in range(8)
    ]
    events[0].hairpin = "<"
    events[4].dynamic = "f"  # a dynamic closes a hairpin: it leads INTO it
    scale = _hairpin_scale(events)
    assert not any(id(e) in scale for e in events[5:])
