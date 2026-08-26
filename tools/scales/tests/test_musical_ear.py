"""Unit tests for musical_ear.py — each detector fires on a planted defect and
stays quiet on clean material. Run: python3 tools/scales/tests/test_musical_ear.py
"""

import tempfile

import music21

from scales import musical_ear as E


def _score(measures):
    """measures: list of (rh_chord_or_note_list, lh_list); each list of pitch names
    forming one whole-note sonority for simplicity."""
    s = music21.stream.Score()
    treble, bass = music21.stream.Part(), music21.stream.Part()
    treble.insert(0, music21.clef.TrebleClef())
    bass.insert(0, music21.clef.BassClef())
    for i, (rh, lh) in enumerate(measures, 1):
        mt, mb = music21.stream.Measure(number=i), music21.stream.Measure(number=i)
        mt.timeSignature = music21.meter.TimeSignature("4/4")
        mt.append(music21.chord.Chord(rh) if len(rh) > 1 else music21.note.Note(rh[0]))
        mb.append(music21.chord.Chord(lh) if len(lh) > 1 else music21.note.Note(lh[0]))
        treble.append(mt)
        bass.append(mb)
    s.insert(0, treble)
    s.insert(0, bass)
    fp = tempfile.mktemp(suffix=".musicxml")
    s.write("musicxml", fp=fp)
    return music21.converter.parse(fp)


def test_clash_detected():
    sc = _score([(["G5", "G-5"], ["C3"])])  # cross-relation G natural vs G-flat
    found = E.detect_vertical_clashes(sc)
    # Surfaced as an ADVISORY warn (cross-relations are often idiomatic) — the
    # fresh-ears critic decides; it must never be a hard/blocking error.
    assert found, "cross-relation should be surfaced for the ear"
    assert all(f["severity"] != "error" for f in found), "must be advisory, not a hard error"


def test_clean_chord_no_clash():
    sc = _score([(["C5"], ["C3", "E3", "G3"])])  # clean C major
    assert not E.detect_vertical_clashes(sc), "clean chord should not clash"


def test_melody_buried_detected():
    # A bar whose melody (treble, C5-F5) sits entirely under a high bass voice
    # (C6) — substantially buried — surfaces as an ADVISORY warn (voices cross
    # legitimately in real counterpoint, so it must never be a hard error).
    s = music21.stream.Score()
    treble, bass = music21.stream.Part(), music21.stream.Part()
    treble.insert(0, music21.clef.TrebleClef())
    bass.insert(0, music21.clef.BassClef())
    mt, mb = music21.stream.Measure(number=1), music21.stream.Measure(number=1)
    mt.timeSignature = music21.meter.TimeSignature("4/4")
    for p in ("C5", "D5", "E5", "F5"):
        mt.append(music21.note.Note(p, quarterLength=1))
    for _ in range(4):
        mb.append(music21.note.Note("C6", quarterLength=1))  # bass voice above the tune
    treble.append(mt)
    bass.append(mb)
    s.insert(0, treble)
    s.insert(0, bass)
    fp = tempfile.mktemp(suffix=".musicxml")
    s.write("musicxml", fp=fp)
    found = E.detect_melody_buried(music21.converter.parse(fp))
    assert found, "a substantially buried melody must be surfaced"
    assert all(f["severity"] != "error" for f in found), "must be advisory, not a hard error"


def test_unresolved_nct_chromatic_leap():
    # F#5 (chromatic in C major) leapt to and from
    bars = [
        {
            "bar_num": 1,
            "key": "C",
            "key_mode": "major",
            "melody_line": [
                {"type": "note", "midi": 60, "dur": 1},  # C5
                {"type": "note", "midi": 66, "dur": 1},  # F#5 (chromatic), leapt both sides
                {"type": "note", "midi": 60, "dur": 1},  # C5
            ],
        }
    ]
    assert E.detect_unresolved_nct(bars), "chromatic leapt-to/from note should flag"


def test_diatonic_passing_no_nct():
    # D5 passing between C5 and E5 — diatonic, stepwise → no flag
    bars = [
        {
            "bar_num": 1,
            "key": "C",
            "key_mode": "major",
            "melody_line": [
                {"type": "note", "midi": 60, "dur": 1},
                {"type": "note", "midi": 62, "dur": 1},
                {"type": "note", "midi": 64, "dur": 1},
            ],
        }
    ]
    assert not E.detect_unresolved_nct(bars), "diatonic stepwise passing tone must not flag"


def test_no_breathing_at_cadence():
    bars = [
        {
            "bar_num": 8,
            "key": "C",
            "key_mode": "major",
            "phrase_position": "cadential",
            "melody_density": 8,
            "accomp_density": 8,
            "melody_line": [{"type": "note", "midi": 60, "dur": 0.5} for _ in range(8)],
        }
    ]
    assert E.detect_no_breathing(bars), "cadence with no rest/long note should flag"


def _line(midis):
    return [{"type": "note", "midi": m, "dur": 0.5} for m in midis]


def test_monotony_run():
    sig = [{"type": "note", "dur": 0.5} for _ in range(8)]
    bars = [
        {"bar_num": i, "rh_display": list(sig), "melody_line": _line([60, 62, 64, 65])}
        for i in range(1, 6)
    ]  # 5 identical bars
    assert E.detect_monotony(bars), "5 identical RH bars should flag monotony"


def test_monotony_ignores_a_repeated_rhythm_with_a_developing_line():
    """A steady rhythm is an idiom, not a defect — only stamped-out PITCHES are."""
    sig = [{"type": "note", "dur": 0.5} for _ in range(8)]
    contours = (
        [60, 62, 64, 65],
        [60, 64, 67, 72],
        [72, 71, 69, 67],
        [67, 65, 62, 60],
        [60, 67, 64, 60],
    )
    bars = [
        {"bar_num": i + 1, "rh_display": list(sig), "melody_line": _line(c)}
        for i, c in enumerate(contours)
    ]
    assert not E.detect_monotony(bars)


def test_static_bass_run_is_flagged():
    bars = [
        {
            "bar_num": i,
            "melody_density": 6,
            "roman": "i",
            "lh_display": [{"type": "note", "pitch": "A2", "dur": 3}],
        }
        for i in range(1, 7)
    ]
    findings = E.detect_static_bass(bars)
    assert findings and findings[0]["detector"] == "static_bass"


def test_static_bass_tolerates_a_moving_bass():
    bars = [
        {
            "bar_num": i,
            "melody_density": 6,
            "roman": "i",
            "lh_display": [{"type": "note", "pitch": p, "dur": 1}],
        }
        for i, p in enumerate(("A2", "D3", "E3", "F3", "G3", "A3"), 1)
    ]
    assert not E.detect_static_bass(bars)


def test_harmonic_stagnation_needs_a_long_run():
    ok = [{"bar_num": i, "roman": r} for i, r in enumerate(["i", "i", "iv", "V", "i"], 1)]
    assert not E.detect_harmonic_stagnation(ok)
    stuck = [{"bar_num": i, "roman": "i"} for i in range(1, 9)] + [{"bar_num": 9, "roman": "V"}]
    assert E.detect_harmonic_stagnation(stuck)


def test_multi_voice_per_hand():
    # A sustained melody (voice 1) over an independent moving inner line (voice 2)
    # in the SAME hand must produce two staff voices, not a block chord.
    from scales.direct_compose import compose_phrase
    from scales.music_io import layer_ir_to_event_ir

    bars = [
        {
            "rh": "Ab5h. Gb5q // Db5e Eb5e F5e Gb5e Ab5e Bb5e C6e Db6e",
            "lh": "Db2h. // Ab2e F2e Ab2e Db3e F3e Db3e",
            "dyn": "mp",
        }
    ]
    layer = compose_phrase(bars, key="Db", phrase_id="t", meter=(4, 4))
    assert len(layer.counter_reply) == 8, "RH inner voice must reach counter_reply"
    assert len(layer.response_layer) == 6, "LH inner voice must reach response_layer"
    pairs = {(e.staff, e.voice) for e in layer_ir_to_event_ir(layer)}
    assert ("treble", 2) in pairs and ("bass", 2) in pairs, f"need 2 voices/staff: {pairs}"


if __name__ == "__main__":
    import sys

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ok  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)


def test_arpeggiated_melody_is_flagged():
    """The craft guidance says "C-E-G-C is a chord, not a tune" — nothing measured it."""
    bars = [
        {
            "bar_num": i,
            "key": "C",
            "key_mode": "major",
            "roman": "I",
            "melody_line": [{"type": "note", "midi": m, "dur": 1} for m in (60, 64, 67, 72)],
        }
        for i in range(1, 7)
    ]
    found = E.detect_arpeggiated_melody(bars)
    assert found and found[0]["detector"] == "arpeggiated_melody"


def test_singing_line_with_non_chord_tones_is_not_flagged():
    """A tune earns its status through non-chord tones and stepwise connection."""
    bars = [
        {
            "bar_num": i,
            "key": "C",
            "key_mode": "major",
            "roman": "I",
            "melody_line": [{"type": "note", "midi": m, "dur": 1} for m in (67, 65, 64, 62)],
        }
        for i in range(1, 7)
    ]
    assert not E.detect_arpeggiated_melody(bars)


def test_short_arpeggiated_gesture_is_not_a_texture():
    bars = [
        {
            "bar_num": i,
            "key": "C",
            "key_mode": "major",
            "roman": "I",
            "melody_line": [{"type": "note", "midi": m, "dur": 1} for m in (60, 64, 67, 72)],
        }
        for i in range(1, 3)
    ]
    assert not E.detect_arpeggiated_melody(bars)


def _lh(pitches, dur=1.0):
    return [{"type": "note", "pitch": p, "dur": dur} for p in pitches]


def test_photocopied_accompaniment_measures_proportion_not_run_length():
    """The AVOID entry is "Same Accompaniment Pattern THROUGHOUT". A fixed-run
    rule fired on real Beethoven, which repeats a figure for eight bars under a
    prolonged harmony."""
    stamped = [{"bar_num": i, "lh_display": _lh(("E3", "A3", "E3"))} for i in range(1, 17)]
    assert E.detect_photocopied_accompaniment(stamped)

    varied = stamped[:8] + [
        {"bar_num": i, "lh_display": _lh(("D3", "F3", "A3"))} for i in range(9, 17)
    ]
    assert not E.detect_photocopied_accompaniment(varied)


def test_photocopy_needs_enough_bars_to_mean_throughout():
    short = [{"bar_num": i, "lh_display": _lh(("E3", "A3", "E3"))} for i in range(1, 7)]
    assert not E.detect_photocopied_accompaniment(short)


def test_static_bass_distinguishes_a_drone_from_a_pedal():
    """A pedal is expressive — the bass holds while the harmony MOVES above it.
    Only a bass that holds under an unchanging harmony is a drone."""
    drone = [
        {"bar_num": i, "melody_density": 5, "roman": "i", "lh_display": _lh(("A2",))}
        for i in range(1, 9)
    ]
    assert E.detect_static_bass(drone)

    pedal = [
        {"bar_num": i, "melody_density": 5, "roman": r, "lh_display": _lh(("E2",))}
        for i, r in enumerate(["V", "V7", "i64", "V", "viio", "V7", "i", "V"], 1)
    ]
    assert not E.detect_static_bass(pedal)


def test_static_bass_measures_motion_not_note_count():
    """Defining it by accompaniment density missed the real failure: a held bass
    with busy filler above it has a high density and no motion at all."""
    busy_but_static = [
        {
            "bar_num": i,
            "melody_density": 4,
            "accomp_density": 8,
            "roman": "i",
            "lh_display": _lh(("A2",)),
            "lh_inner_display": _lh(("E3", "A3", "E3", "A3")),
        }
        for i in range(1, 9)
    ]
    assert E.detect_static_bass(busy_but_static)


def test_flat_harmonic_rhythm_is_flagged():
    """One chord per bar for a whole section is a plan limitation showing through,
    not a style: two thirds of Mozart's bars carry more than one harmony."""
    flat = [{"bar_num": i, "harmony_events": [{"beat": 1, "roman": "I"}]} for i in range(1, 25)]
    assert E.detect_flat_harmonic_rhythm(flat)


def test_harmony_moving_within_bars_is_not_flagged():
    moving = [
        {
            "bar_num": i,
            "harmony_events": [
                {"beat": 1, "roman": "ii6"},
                {"beat": 2, "roman": "I64"},
                {"beat": 3, "roman": "V7"},
            ],
        }
        for i in range(1, 25)
    ]
    assert not E.detect_flat_harmonic_rhythm(moving)


def test_flat_harmonic_rhythm_needs_a_long_enough_span():
    short = [{"bar_num": i, "harmony_events": [{"beat": 1, "roman": "I"}]} for i in range(1, 8)]
    assert not E.detect_flat_harmonic_rhythm(short)


def _phrase(role, bar, durs, pitches):
    from scales.models import LayerEvent, LayerIR, PhraseSlot, PhraseState

    layer = LayerIR(bar_count=4)
    layer.principal_line = [
        LayerEvent(bar=bar, beat=1.0 + i, pitch=p, duration=d)
        for i, (p, d) in enumerate(zip(pitches, durs))
    ]
    slot = PhraseSlot(phrase_id=f"{role}{bar}", section_id="s", bar_start=bar, bar_count=4)
    slot.dramatic_role = role
    return PhraseState(slot=slot, realized=layer)


def test_unvaried_return_is_flagged():
    """The machine tell no statistic catches: every metric reads "matches the
    exposition", which is exactly the defect."""
    from scales.piece_graph import PieceGraph

    g = PieceGraph()
    g.phrases["stmt"] = _phrase("establish", 1, ["q"] * 4, ["C5", "E5", "G5", "C6"])
    g.phrases["ret"] = _phrase("return", 20, ["q"] * 4, ["C5", "E5", "G5", "C6"])
    found = E.detect_unvaried_return(g)
    assert found and found[0]["detector"] == "unvaried_return"


def test_a_real_variation_of_the_return_is_not_flagged():
    from scales.piece_graph import PieceGraph

    g = PieceGraph()
    g.phrases["stmt"] = _phrase("establish", 1, ["q"] * 4, ["C5", "E5", "G5", "C6"])
    g.phrases["ret"] = _phrase("return", 20, ["e", "e", "q", "h"], ["C5", "D5", "Bb5", "A5"])
    assert not E.detect_unvaried_return(g)


def test_unvaried_return_needs_a_statement_to_compare_against():
    from scales.piece_graph import PieceGraph

    g = PieceGraph()
    g.phrases["ret"] = _phrase("return", 20, ["q"] * 4, ["C5", "E5", "G5", "C6"])
    assert not E.detect_unvaried_return(g)
