"""Every reduction of a real score failed the strict meter gate.

Reducing an actual Bach organ work, B-minor Mass movement and chorale — parsed
from the scores on disk, in each source's own key and metre — produced:

    BWV533              137 validator errors, all `meter`
    B minor Mass        259
    Bach_BrichAn         32

Meter is the one constraint this system will not waive. So the reduction path
could not produce a committable result from any real orchestral source, and the
mode had never been run end to end to find out.

Two causes, both the same shape: **a layer is ONE voice, and the packer wrote
several parts into it.**

  1. `_pack_bar` emitted a separate event per source part, so notes sounding at
     the SAME instant were appended sequentially. A four-part chorale reduced to
     a right hand whose 4/4 bars held 5, 6 and 9 beats, and whose own validator
     said "G4q starts at beat 1 while D4q is still sounding — one voice cannot
     play both". A pianist plays those as a chord.
  2. Merging onsets left a held note being overlapped by a LATER, shorter one —
     "A4h at beat 3, F#4q at beat 3" is still two notes in one voice. The
     earlier note now ends where the next begins, which is what a single hand
     does.

    137 -> 0        259 -> 0        32 -> 0
"""

import dataclasses
import glob

import pytest

from scales.bimanual_packer import _clip_to_next_onset, _merge_simultaneous
from scales.models import LayerEvent
from scales.validator import validate_layer_ir

pytestmark_calibration = pytest.mark.calibration


def _ev(bar, beat, pitch, duration):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=duration)


# ─── Merging simultaneous onsets ─────────────────────────────────────────────


def test_notes_at_one_instant_become_a_chord():
    merged = _merge_simultaneous(
        [_ev(1, 1.0, "C4", "q"), _ev(1, 1.0, "E4", "q"), _ev(1, 1.0, "G4", "q")]
    )
    assert len(merged) == 1
    assert merged[0].pitch == ["C4", "E4", "G4"]


def test_a_single_note_is_left_alone():
    one = [_ev(1, 1.0, "C4", "q")]
    assert _merge_simultaneous(one)[0].pitch == "C4"


def test_the_chord_takes_the_shortest_duration():
    """Taking the longest would push the chord over the next onset and
    re-create the overflow this exists to remove."""
    merged = _merge_simultaneous([_ev(1, 1.0, "C4", "h"), _ev(1, 1.0, "E4", "q")])
    assert merged[0].duration == "q"


def test_different_onsets_are_not_merged():
    merged = _merge_simultaneous([_ev(1, 1.0, "C4", "q"), _ev(1, 2.0, "D4", "q")])
    assert len(merged) == 2


def test_a_duplicate_pitch_is_not_doubled_in_the_chord():
    merged = _merge_simultaneous([_ev(1, 1.0, "C4", "q"), _ev(1, 1.0, "C4", "q")])
    assert merged[0].pitch == "C4"


# ─── Clipping an overlapped note ─────────────────────────────────────────────


def test_a_held_note_ends_where_the_next_begins():
    clipped = _clip_to_next_onset([_ev(1, 3.0, "A4", "h"), _ev(1, 3.5, "F#4", "e")])
    assert clipped[0].duration == "e", "the half note still runs through the next onset"


def test_a_note_that_fits_is_untouched():
    kept = _clip_to_next_onset([_ev(1, 1.0, "C4", "q"), _ev(1, 2.0, "D4", "q")])
    assert kept[0].duration == "q"


def test_a_note_held_across_a_barline_is_not_shortened():
    """A tie over the barline is legitimate and clipping it would be wrong."""
    kept = _clip_to_next_onset([_ev(1, 4.0, "C4", "h"), _ev(2, 1.0, "D4", "q")])
    assert kept[0].duration == "h"


# ─── The end-to-end claim ────────────────────────────────────────────────────


@pytest.mark.calibration
def test_real_scores_reduce_without_a_single_meter_error():
    import music21

    from scales.music_io import parse_musicxml_to_events
    from scales.sabre import SABRE
    from scales.scales import _source_key, _source_meter

    sources = []
    for path in sorted(glob.glob("tools/reference_scores/_fetch_*/*.mid")):
        try:
            score = music21.converter.parse(path)
        except Exception:
            continue
        if len(list(score.parts)) >= 4:
            sources.append(path)
        if len(sources) >= 3:
            break
    if not sources:
        pytest.skip("no multi-part sources present")

    offenders = []
    for path in sources:
        events, instruments = parse_musicxml_to_events(path)
        meter = _source_meter(path) or (4, 4)
        layer = SABRE().reduce_to_piano(
            events,
            instruments=instruments,
            mode="reduce_to_piano",
            key=_source_key(path) or "C",
            meter=meter,
        )
        layer.meter = meter
        report = validate_layer_ir(layer)
        data = dataclasses.asdict(report) if dataclasses.is_dataclass(report) else vars(report)
        errors = [
            i
            for v in data.values()
            if isinstance(v, list)
            for i in v
            if isinstance(i, dict) and i.get("severity") == "error"
        ]
        if errors:
            offenders.append((path.split("/")[-1], len(errors), errors[0].get("message", "")[:70]))
    assert not offenders, f"reductions still fail the strict gate: {offenders}"
