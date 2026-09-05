"""The preview must have a real sustain pedal — and only where one exists.

Before this the rendered MIDI contained **no controller event of any kind**.
What stood in for a pedal was lengthening bass notes in bars the renderer chose:
that sustains one hand, ignores any pedal the composer wrote, and cannot blur a
harmony the way lifting the dampers does. For Romantic piano writing the pedal is
not an effect on the sound, it is most of the sound.

The second half matters as much. `pedal_lead_ms=0.0` was the only thing standing
for "harpsichord: no pedal" — a release timing, not a prohibition — so pedal bars
were generated for Bach and Palestrina all along (16 bars in a two-part
invention), silently stretching their bass notes. Emitting real CC64 would have
turned that into a damper pedal on a harpsichord and on unaccompanied voices.
"""

import tempfile

import pytest

from scales.midi_renderer import _pedal_spans, render_midi
from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState, StyleDNA
from scales.performance_params import profile_for_composer
from scales.piece_graph import PieceGraph

music21 = pytest.importorskip("music21")


def _sustain_events(path) -> int:
    """Count CC64. NOTE: a NoteOn's `parameter1` is its PITCH, so filtering on
    `parameter1 == 64` alone counts every E4 in the piece — which is exactly the
    false reading that made a pedal-free Bach look like it had 30 pedal events."""
    from music21 import midi as m21

    mf = m21.MidiFile()
    mf.open(str(path))
    try:
        mf.read()
    finally:
        mf.close()
    return sum(
        1
        for track in mf.tracks
        for e in track.events
        if getattr(e, "type", None) == m21.ChannelVoiceMessages.CONTROLLER_CHANGE
        and e.parameter1 == 64
    )


def _graph(composer: str, pedal_mark=None) -> PieceGraph:
    mel = [
        LayerEvent(bar=1, beat=float(i + 1), pitch=p, duration="q", role="structural")
        for i, p in enumerate(["C5", "E5", "G5", "C6"])
    ]
    bass = [LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q", role="bass_foundation")]
    if pedal_mark:
        bass[0].pedal = pedal_mark
    layer = LayerIR(
        principal_line=mel, bass_foundation=bass, meter=(4, 4), key="C major", phrase_id="p1"
    )
    g = PieceGraph()
    g.style_dna = StyleDNA(composer_id=composer)
    g.phrases["p1"] = PhraseState(
        slot=PhraseSlot(
            phrase_id="p1",
            section_id="m1_a",
            bar_start=1,
            bar_count=1,
            key="C major",
            meter=(4, 4),
            tempo_bpm=90,
        ),
        realized=layer,
        agent_authored=True,
    )
    return g


def test_a_pedal_the_composer_wrote_reaches_the_midi():
    with tempfile.TemporaryDirectory() as d:
        assert _sustain_events(render_midi(_graph("chopin", "down"), output_dir=d)) >= 2


def test_a_harpsichord_gets_no_damper_pedal():
    with tempfile.TemporaryDirectory() as d:
        assert _sustain_events(render_midi(_graph("bach"), output_dir=d)) == 0


def test_unaccompanied_voices_get_no_pedal():
    with tempfile.TemporaryDirectory() as d:
        assert _sustain_events(render_midi(_graph("palestrina"), output_dir=d)) == 0


def test_the_period_profiles_say_which_instruments_have_a_pedal():
    assert not profile_for_composer("bach").uses_pedal
    assert not profile_for_composer("palestrina").uses_pedal
    assert profile_for_composer("chopin").uses_pedal
    assert profile_for_composer("mozart").uses_pedal


def test_palestrina_is_not_baroque():
    """`renaissance` mapped straight onto the baroque profile object, so
    `profile.period` answered "baroque" for Palestrina. The values are shared on
    purpose; the label was simply wrong."""
    assert profile_for_composer("palestrina").period == "renaissance"


def test_the_pedal_lifts_before_the_barline():
    """A pedal held THROUGH a bar line is what makes a change of harmony sound
    like mud."""
    spans = _pedal_spans(
        None,
        [
            (
                [
                    LayerEvent(
                        bar=1,
                        beat=1.0,
                        pitch="C3",
                        duration="q",
                        role="bass_foundation",
                        pedal="down",
                    )
                ],
                None,
                (4, 4),
                "C major",
            )
        ],
        4.0,
        {1: 0.0},
    )
    assert spans
    for down, up in spans:
        assert up - down < 4.0


def test_the_notes_still_survive_the_pedal_rewrite():
    """The file is reopened and its delta times recomputed; losing a note to that
    would be a far worse bug than having no pedal."""
    with tempfile.TemporaryDirectory() as d:
        path = render_midi(_graph("chopin", "down"), output_dir=d)
        sc = music21.converter.parse(path, format="midi")
        assert len(list(sc.flatten().notes)) == 5
