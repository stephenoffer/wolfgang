"""How many notes sound together, across every voice stream.

"Does this staff notate a chord" is a KEYBOARD question. `avg_chord_size` asked
it by reading a `type` field off two staves — so for four independent voices it
found chords in 39 of Bach's 470 movements and reported 0.171 for the rest,
which is not a size. It reported 0.000 for Palestrina: zero chords, for music
that is nothing but vertical sonorities.

More than half of Bach's notes and 55% of Palestrina's live in the INNER
streams, which that measure never read at all.

A chorale's chords are alignments ACROSS streams. Reconstructing each stream's
onsets and asking how many pitches sound at each attack has the same meaning for
a piano chord and for four voices arriving together, which is the point.
"""

from __future__ import annotations

import itertools

import pytest

from scales.corpus_metrics import sonority_metrics


def _bar(**streams):
    return {name: list(events) for name, events in streams.items()}


def _n(pitch, dur):
    return {"type": "note", "pitch": pitch, "dur": dur}


def test_four_voices_arriving_together_are_a_four_note_sonority():
    """The case the old measure scored as zero."""
    bar = _bar(
        rh_display=[_n("G5", 1.0)],
        rh_inner_display=[_n("D5", 1.0)],
        lh_inner_display=[_n("B4", 1.0)],
        lh_display=[_n("G3", 1.0)],
    )
    result = sonority_metrics([bar])
    assert result["mean_sonority"] == 4.0, result
    assert result["chorded_attack_pct"] == 100.0, result


def test_a_notated_chord_and_four_voices_measure_the_same():
    """The whole point: one question, both kinds of writing."""
    voices = _bar(
        rh_display=[_n("G5", 1.0)],
        rh_inner_display=[_n("D5", 1.0)],
        lh_display=[_n("B3", 1.0)],
    )
    chord = _bar(
        rh_display=[{"type": "chord", "pitches": ["G5", "D5", "B3"], "dur": 1.0}],
    )
    assert sonority_metrics([voices])["mean_sonority"] == 3.0
    assert sonority_metrics([chord])["mean_sonority"] == 3.0


def test_a_single_line_is_a_sonority_of_one():
    bar = _bar(rh_display=[_n("C5", 1.0), _n("D5", 1.0), _n("E5", 1.0)])
    result = sonority_metrics([bar])
    assert result["mean_sonority"] == 1.0
    assert result["chorded_attack_pct"] == 0.0
    assert result["attacks"] == 3


def test_rests_and_graces_take_no_part():
    """A grace takes no metric time, and a rest is not a pitch."""
    bar = _bar(
        rh_display=[{"type": "rest", "dur": 1.0}, _n("C5", 1.0)],
        lh_display=[
            {"type": "note", "pitch": "B2", "dur": 0.0, "is_grace": True},
            {"type": "note", "pitch": "C3", "dur": 2.0},
        ],
    )
    result = sonority_metrics([bar])
    # The C3 spans the bar; only the C5 attack coincides with it.
    assert result["mean_sonority"] > 1.0
    assert result["attacks"] >= 2


def test_an_empty_bar_measures_nothing_rather_than_zero():
    assert sonority_metrics([])["attacks"] == 0
    assert sonority_metrics([_bar(rh_display=[{"type": "rest", "dur": 4.0}])])["attacks"] == 0


@pytest.mark.parametrize(
    "composer,floor",
    [("bach", 3.0), ("palestrina", 2.8), ("monteverdi", 2.5)],
)
def test_the_contrapuntal_composers_measure_as_polyphony(composer, floor):
    """Bach's chorales are in four parts and Palestrina's masses in four or
    five. Anything near 1 means the inner streams are being missed again."""
    from scales.composition_brief import _iter_corpus_bars

    bars = list(itertools.islice(_iter_corpus_bars(composer), 2000))
    if not bars:
        pytest.skip(f"no corpus for {composer}")
    result = sonority_metrics(bars)
    assert result["mean_sonority"] >= floor, (
        f"{composer} measures {result['mean_sonority']} voices — the old "
        f"`avg_chord_size` read {composer} as ~0 by looking at two staves only"
    )


# ─── The other half: a chord must not vanish from the line it is part of ────


def test_a_thickened_melody_is_still_a_melody():
    """The TOP of a chord is the melodic line.

    `craft_checker._check_melodic_claim` and `candidate_scorer`'s novelty
    comparison both built their contour with
    `not isinstance(e.pitch, list)` — dropping every chord. That was harmless
    while melodies were 100% single notes and became wrong the moment they were
    deliberately thickened to a tenth of their attacks, which is what real
    keyboard writing does. A phrase whose line was fine could fail for having
    taken weight at its arrivals.
    """
    from scales.craft_checker import CraftChecker
    from scales.models import LayerEvent, LayerIR

    def melody(pitches):
        layer = LayerIR(phrase_id="p", meter=(4, 4), bar_count=1)
        layer.principal_line = [
            LayerEvent(bar=1, beat=1.0 + i, pitch=p, duration="q", source_layer="principal_line")
            for i, p in enumerate(pitches)
        ]
        return layer

    checker = CraftChecker()
    plain = melody(["C5", "E5", "G5", "F5"])
    thick = melody([["C5", "E5"], ["E5", "G5"], ["G5", "C6"], ["F5", "A5"]])

    assert checker._check_melodic_claim(plain), "a plain line must pass"
    assert checker._check_melodic_claim(thick), (
        "a thickened line lost its contour — the chord tops ARE the melody"
    )


def test_the_contour_reads_the_top_of_a_chord_not_the_bottom():
    """A melody chorded downward still rises if its top voice does."""
    from scales.anti_pattern_detector import _voice_midi

    assert _voice_midi(["C5", "E5", "G5"], "top") == _voice_midi("G5", "top")
    assert _voice_midi(["C5", "E5", "G5"], "bottom") == _voice_midi("C5", "top")
    assert _voice_midi("rest", "top") is None
    assert _voice_midi(None, "top") is None


@pytest.mark.calibration
@pytest.mark.parametrize("composer,ceiling", [("mozart", 0.05), ("haydn", 0.05), ("bach", 0.10)])
def test_muddy_low_intervals_are_rare_in_real_music(composer, ceiling):
    """`detect_spacing_gaps` calls two notes within a third below C3 muddy.

    That is editorial advice, and it is measurable: across Mozart, Haydn,
    Beethoven and Chopin the smallest interval between two notes below C3 is an
    octave 59.5% of the time and a fifth 17.0%, against 6.5% for thirds. Three
    quarters of low doublings are an octave or a fifth.

    A detector that FLAGS has to clear real music, so this pins the rate. If it
    ever rises, either the threshold has drifted or the corpus has.
    """
    import itertools

    from scales.composition_brief import _iter_corpus_bars
    from scales.corpus_metrics import _stream_spans
    from scales.pitch import pitch_to_midi

    bars = list(itertools.islice(_iter_corpus_bars(composer), 1500))
    if not bars:
        pytest.skip(f"no corpus for {composer}")

    muddy = measured = 0
    for bar in bars:
        spans = [(s, e, pitch_to_midi(p)) for s, e, p in _stream_spans(bar)]
        spans = [(s, e, m) for s, e, m in spans if m is not None]
        if not spans:
            continue
        measured += 1
        for attack in sorted({s for s, _, _ in spans}):
            pitches = sorted({m for s, e, m in spans if s <= attack < e})
            if any(hi < 48 and 1 <= hi - lo <= 4 for lo, hi in zip(pitches, pitches[1:])):
                muddy += 1
                break

    rate = muddy / max(measured, 1)
    assert rate <= ceiling, (
        f"{composer} trips muddy_low_interval on {rate:.3f} of his bars — a "
        f"detector that flags what real composers write measures the threshold, "
        f"not the music"
    )
