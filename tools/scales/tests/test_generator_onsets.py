"""Generated onsets must be positions a bar actually has.

The engine fallback was shipping bars holding 4.875 beats of a 4/4 and onsets at
1.56, 2.06 and 0.06 — the last of which is below beat 1 and not a position in any
bar. A repair pass downstream now snaps them, but a generator that emits
positions the notation cannot express is producing something no engraver can
read, and repairing it downstream hides that.

Two faults, both in this lane, both silent:

* **A float cursor rounded to two decimals.** `1.5625` — a legitimate 64th
  offset — was emitted as `1.56`. Advancing a float by `1/3` for a triplet
  compounds the error across a bar.
* **The cursor advanced BEFORE the note was emitted.** Every gesture started one
  note-value late and its last note ran past the end of its slot: a four-note
  figure beginning on beat 1 was written beginning on beat 1.5.
"""

from fractions import Fraction

import pytest

from scales.duration import DURATION_VALUES

# The finest grid on which every supported duration is exact. The denominators
# in `DURATION_VALUES` are 1,2,3,4,5,6,7,8,12,16 and their least common multiple
# is 1680.
#
# Two opposite mistakes are possible here and the repair path hit both:
#
# * **Too coarse.** 1/48 is the obvious choice — it covers triplets,
#   sextuplets, 32nds and 64ths — and it silently destroys quintuplets (1/5) and
#   septuplets (1/7), because 5 and 7 do not divide 48. A five-note quintuplet
#   snapped to it drifts up to 0.0083 of a beat per note and no longer sums to
#   its own beat. That is the 16th-note quantization that once destroyed every
#   triplet in this system, moved out one tuplet family.
# * **Too fine.** 1/1680 is exact for every real duration and therefore useless
#   as a *repair* grid: a smeared onset of 1.56 is already on it (941/1680), so
#   snapping leaves the smear untouched.
#
# So this constant is the right invariant for the DURATION TABLE — every value
# must be expressible — and not a repair rule. Repair resolves a position to the
# simplest subdivision that explains it within a tolerance, walking subdivisions
# coarsest first and restricted to divisors of 1680; that lives in
# `scales._resolve_position` and is tested in `test_patch_engine.py`.
_GRID = Fraction(1, 1680)


def _on_grid(beat: float) -> bool:
    return (Fraction(str(beat)).limit_denominator(1000) % _GRID) == 0


def _positions(durations, start=Fraction(1)):
    """Emit-then-advance with an exact cursor — the corrected arithmetic."""
    beat = Fraction(start)
    out = []
    for code in durations:
        out.append(beat)
        beat += DURATION_VALUES[code]
    return out, beat


# ─── The grid property ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "profile",
    [
        ["trip_e", "trip_e", "trip_e"],
        ["trip_s"] * 6,
        ["s", "s", "trip_e", "trip_e", "trip_e"],
        ["t"] * 8,
        ["x"] * 8,
        ["quint_s"] * 5,
        ["sext_s"] * 6,
        ["dq", "e", "s", "s"],
    ],
)
def test_every_onset_of_a_gesture_lands_on_the_notation_grid(profile):
    positions, _end = _positions(profile)
    off = [float(p) for p in positions if (p % _GRID) != 0]
    assert not off, f"{profile} produced off-grid onsets {off}"


@pytest.mark.parametrize(
    "profile,expected_end",
    [
        (["trip_e"] * 3, Fraction(2)),
        (["trip_s"] * 6, Fraction(2)),
        (["q"] * 4, Fraction(5)),
        (["e"] * 8, Fraction(5)),
        (["quint_s"] * 5, Fraction(2)),
    ],
)
def test_a_gesture_ends_exactly_where_it_should(profile, expected_end):
    """Float arithmetic ends a bar of triplets at 1.9999999999999998."""
    _positions_, end = _positions(profile)
    assert end == expected_end


def test_the_first_note_lands_on_the_slots_own_start_beat():
    """Advance-then-emit displaced every gesture by its own first duration."""
    positions, _ = _positions(["trip_s"] * 3 + ["s"] * 2, start=Fraction(1))
    assert positions[0] == Fraction(1), (
        f"the gesture starts at {float(positions[0])}, not on its slot's beat 1"
    )


def test_a_float_cursor_rounded_to_two_decimals_leaves_the_grid():
    """The failure this test exists to prevent, demonstrated."""
    beat = 1.0
    emitted = []
    for code in ["trip_s"] * 3 + ["s"] * 2:
        beat += float(DURATION_VALUES[code])
        emitted.append(round(beat, 2))
    assert any(not _on_grid(b) for b in emitted), (
        "the old arithmetic is expected to produce off-grid onsets"
    )
    # And the corrected arithmetic does not.
    positions, _ = _positions(["trip_s"] * 3 + ["s"] * 2)
    assert all(_on_grid(float(p)) for p in positions)


def test_no_onset_falls_below_beat_one():
    """0.06 was reaching the score; there is no such position in a bar."""
    for profile in (["trip_e"] * 3, ["s"] * 16, ["dq", "e"]):
        positions, _ = _positions(profile)
        assert all(p >= 1 for p in positions), profile


# ─── The duration table itself ───────────────────────────────────────────────


def test_every_duration_value_is_exact():
    """One float in the table reintroduces the drift everywhere it is used."""
    non_exact = [k for k, v in DURATION_VALUES.items() if not isinstance(v, Fraction)]
    assert not non_exact, f"these duration values are not exact: {non_exact}"


def test_every_duration_value_lands_on_the_grid():
    """The invariant that makes the coarse-grid bug unrepeatable.

    Any quantization grid used anywhere must have every one of these as an exact
    multiple, or it rounds a duration the system claims to support.
    """
    off = [k for k, v in DURATION_VALUES.items() if (v % _GRID) != 0]
    assert not off, f"these durations are not expressible on the 1/1680 grid: {off}"


def test_a_coarser_grid_would_corrupt_a_supported_duration():
    """Demonstrates why 1/48 is not a safe choice, so nobody re-picks it."""
    coarse = Fraction(1, 48)
    corrupted = [k for k, v in DURATION_VALUES.items() if (v % coarse) != 0]
    assert set(corrupted) >= {"quint_s", "sept_s"}, corrupted


# ─── Each bar's accompaniment is written once ────────────────────────────────


def test_a_bar_belongs_to_exactly_one_gesture_slot():
    """The fallback realizer wrote the entire left hand twice.

    `_construct_accompaniment` iterated `range(slot.bar_start, slot.bar_end + 1)`
    and never consulted `beat_start`/`beat_end`. Gesture slots run between
    consecutive melody anchors and are contiguous, so most bars are touched by
    two of them:

        1b1 -> 1b3  entry           1b3 -> 2b1  continuation
        2b1 -> 2b3  peak_response   2b3 -> 3b1  cadential

    and every bar's accompaniment was generated once per slot that touched it.
    Measured on a realized section: **61 of 61 bass onsets sat at a duplicated
    position**. The surface repair deleted the copies, which is why
    `overlaps_trimmed` came back at 34, 46 and 56 per phrase — the output was
    correct only because something cleaned up after it.

    A bar belongs to the slot whose span contains its DOWNBEAT. Whole bars, not
    split ones: an Alberti or arpeggio figure cut at beat 3 is not half a
    pattern, it is a broken one.
    """
    from scales.models import PhraseControlIR
    from scales.surface_composer import GestureSlot, SurfaceComposer

    control = PhraseControlIR(bar_start=1, bars=3, meter=(4, 4))
    slots = [
        GestureSlot(bar_start=a, beat_start=b, bar_end=c, beat_end=d)
        for a, b, c, d in [
            (1, 1.0, 1, 3.0),
            (1, 3.0, 2, 1.0),
            (2, 1.0, 2, 3.0),
            (2, 3.0, 3, 1.0),
            (3, 1.0, 3, 4.0),
        ]
    ]
    SurfaceComposer._assign_bar_ownership(slots, control)
    owned = [s.owned_bars for s in slots]
    flat = [bar for group in owned for bar in group]
    assert len(flat) == len(set(flat)), f"a bar is owned by two slots: {owned}"
    assert set(flat) == {1, 2, 3}, f"a bar is owned by no slot: {owned}"


def test_a_phrase_whose_first_anchor_is_late_still_gets_a_first_bar():
    """Otherwise a phrase opening on beat 3 has no left hand in bar 1 at all."""
    from scales.models import PhraseControlIR
    from scales.surface_composer import GestureSlot, SurfaceComposer

    slot = GestureSlot(bar_start=1, beat_start=3.0, bar_end=2, beat_end=1.0)
    control = PhraseControlIR(bar_start=1, bars=2, meter=(4, 4))
    SurfaceComposer._assign_bar_ownership([slot], control)
    assert 1 in slot.owned_bars


def test_a_slot_reaching_outside_the_phrase_owns_nothing_there():
    from scales.models import PhraseControlIR
    from scales.surface_composer import GestureSlot, SurfaceComposer

    slot = GestureSlot(bar_start=1, beat_start=1.0, bar_end=9, beat_end=4.0)
    control = PhraseControlIR(bar_start=1, bars=2, meter=(4, 4))
    SurfaceComposer._assign_bar_ownership([slot], control)
    assert slot.owned_bars == [1, 2]


# ─── One onset per voice per instant, across the whole phrase ────────────────


def test_adjacent_slots_do_not_write_the_same_instant_twice():
    """Two identical onsets on a downbeat made a 4/4 bar hold five beats.

    Adjacent gesture slots share an instant: a slot's opening anchor is written
    explicitly AND the gesture's own first note lands on that same beat. The
    per-slot collapse cannot see across slots, so the melody carried exactly the
    duplication the accompaniment had before bar ownership was assigned:

        beat 1.000  G4  q      beat 2.000  G4  e
        beat 1.000  G4  q      beat 2.500  G4  e     -> 5.0 beats in a 4/4 bar

    A layer is one voice, so one onset survives; the LONGER is kept, because the
    structural anchor outlasts the gesture note that landed on it.
    """
    from scales.surface_composer import OnsetBundle, OnsetEvent, _merge_bundles_at_one_instant

    def _b(bar, beat, *events):
        bundle = OnsetBundle(bar=bar, beat=beat)
        bundle.events = list(events)
        return bundle

    def _e(voice, pitch, duration):
        return OnsetEvent(voice=voice, pitch=pitch, duration=duration)

    merged = _merge_bundles_at_one_instant(
        [
            _b(1, 1.0, _e("soprano", "G4", "q")),
            _b(1, 1.0, _e("soprano", "G4", "q")),
            _b(1, 2.0, _e("soprano", "A4", "e")),
        ]
    )
    assert len(merged) == 2, "the duplicated instant survived"
    assert len(merged[0].events) == 1


def test_the_longer_onset_wins_at_a_shared_instant():
    from scales.surface_composer import OnsetBundle, OnsetEvent, _merge_bundles_at_one_instant

    short = OnsetBundle(bar=1, beat=3.0)
    short.events = [OnsetEvent(voice="soprano", pitch="D4", duration="trip_e")]
    long = OnsetBundle(bar=1, beat=3.0)
    long.events = [OnsetEvent(voice="soprano", pitch="E4", duration="q")]
    merged = _merge_bundles_at_one_instant([short, long])
    assert len(merged) == 1
    assert merged[0].events[0].pitch == "E4"


def test_different_voices_at_one_instant_are_a_chord_and_survive():
    """The rule is one onset per VOICE, not one per instant."""
    from scales.surface_composer import OnsetBundle, OnsetEvent, _merge_bundles_at_one_instant

    bundle = OnsetBundle(bar=1, beat=1.0)
    bundle.events = [
        OnsetEvent(voice="soprano", pitch="G5", duration="q"),
        OnsetEvent(voice="bass", pitch="C3", duration="q"),
    ]
    merged = _merge_bundles_at_one_instant([bundle])
    assert len(merged[0].events) == 2


def test_a_gesture_stops_at_its_slots_end_beat():
    """The loop checked only `bar_end`, so a slot running 1b1 -> 1b3 kept
    emitting through the whole bar and landed on the next anchor's beat."""
    from scales.models import PhraseControlIR
    from scales.surface_composer import GestureSlot, SurfaceComposer

    control = PhraseControlIR(bar_start=1, bars=2, meter=(4, 4))
    slots = [
        GestureSlot(bar_start=1, beat_start=1.0, bar_end=1, beat_end=3.0),
        GestureSlot(bar_start=1, beat_start=3.0, bar_end=2, beat_end=1.0),
    ]
    SurfaceComposer._assign_bar_ownership(slots, control)
    assert slots[0].owned_bars == [1]
    assert slots[1].owned_bars == [2]


# ─── A value never set at the source ─────────────────────────────────────────


def test_the_fallback_realizer_takes_the_pieces_forces():
    """`instrumentation` was hardcoded `"solo_piano"` when building the LayerIR.

    So the forces could be inferred perfectly from the request — "a sacred motet
    for four voices" — and still never reach the checks that consult them. Every
    reader was correct and all of them were wrong, because the value was never
    set at the source. A nineteenth between Tenor and Bassus is ordinary vocal
    writing and was measured as one hand's reach.

    This is also the second reason the ensemble texture floors reached nothing:
    fixing the whole-piece merge that dropped the field still left every phrase
    in the graph carrying `"solo_piano"`.
    """
    from scales.surface_composer import OnsetBundle, OnsetEvent, SurfaceComposer

    bundle = OnsetBundle(bar=1, beat=1.0)
    bundle.events = [OnsetEvent(voice="soprano", pitch="C5", duration="q")]
    composer = SurfaceComposer.__new__(SurfaceComposer)

    piano = composer.bundles_to_layer_ir([bundle], "p1", "C major", (4, 4), 1)
    choir = composer.bundles_to_layer_ir(
        [bundle], "p1", "C major", (4, 4), 1, instrumentation="choir"
    )
    assert piano.instrumentation == "solo_piano", "the fallback default changed"
    assert choir.instrumentation == "choir"


def test_the_contract_is_where_the_forces_come_from():
    from scales.piece_graph import PieceGraph
    from scales.scales import _contract_instrumentation

    graph = PieceGraph()
    assert _contract_instrumentation(graph) == "solo_piano"
    graph.contract.target.instrumentation = "choir"
    assert _contract_instrumentation(graph) == "choir"


def test_a_reduction_is_still_a_piano_whatever_the_source_was():
    """The one hardcode in this family that should stay: the OUTPUT of a
    reduction is a keyboard, and the playability check it enables is exactly
    what a reduction needs most.

    Tested by REDUCING something, not by reading the source for a literal. An
    earlier version asserted `'instrumentation="solo_piano"' in
    inspect.getsource(...)`, which would pass on a commented-out line and fail
    on a correct refactor — it described the code rather than the behaviour.
    """
    from scales.music_io import parse_musicxml_to_events
    from scales.sabre import SABRE

    events = [
        {"bar": 1, "beat": 1.0, "pitch": "C5", "duration": "q", "instrument": "violin_i"},
        {"bar": 1, "beat": 1.0, "pitch": "C3", "duration": "q", "instrument": "cello"},
        {"bar": 1, "beat": 2.0, "pitch": "E5", "duration": "q", "instrument": "violin_i"},
        {"bar": 1, "beat": 2.0, "pitch": "G3", "duration": "q", "instrument": "cello"},
    ]
    assert parse_musicxml_to_events  # the production path feeds dicts like these
    layer = SABRE().reduce_to_piano(
        events, instruments=["violin_i", "cello"], mode="reduce_to_piano",
        key="C major", meter=(4, 4),
    )
    assert layer.instrumentation == "solo_piano", (
        "a reduction whose target is not a keyboard never gets the hand-span check"
    )


# ─── A decoration shortens the note it decorates ─────────────────────────────


def test_a_note_is_shortened_by_the_decoration_that_follows_it():
    """A sixteenth before the beat means the note before it is a dotted eighth.

    Decorations were inserted between existing onsets without shortening what
    they decorate, so a 4/4 bar held five and a half beats:

        beat 1.000  G4  q     (ends 2.0)
        beat 1.750  G4  s     <- starts inside the quarter
        beat 2.000  G4  h     (ends 4.0)
        beat 3.000  A4  q     <- starts inside the half

    That is what a composer writes and what one hand can play: the earlier note
    ends where the next begins.
    """
    from scales.surface_composer import (
        OnsetBundle,
        OnsetEvent,
        _clip_to_next_onset_in_voice,
    )

    def _b(bar, beat, voice, pitch, duration):
        bundle = OnsetBundle(bar=bar, beat=beat)
        bundle.events = [OnsetEvent(voice=voice, pitch=pitch, duration=duration)]
        return bundle

    bundles = [
        _b(1, 1.0, "soprano", "G4", "q"),
        _b(1, 1.75, "soprano", "G4", "s"),
        _b(1, 2.0, "soprano", "G4", "h"),
    ]
    _clip_to_next_onset_in_voice(bundles)
    assert bundles[0].events[0].duration != "q", "the quarter still runs through its decoration"
    assert bundles[1].events[0].duration == "s", "the decoration itself was altered"


def test_a_note_that_already_fits_is_untouched():
    from scales.surface_composer import (
        OnsetBundle,
        OnsetEvent,
        _clip_to_next_onset_in_voice,
    )

    first = OnsetBundle(bar=1, beat=1.0)
    first.events = [OnsetEvent(voice="soprano", pitch="C5", duration="q")]
    second = OnsetBundle(bar=1, beat=2.0)
    second.events = [OnsetEvent(voice="soprano", pitch="D5", duration="q")]
    _clip_to_next_onset_in_voice([first, second])
    assert first.events[0].duration == "q"


def test_a_note_held_across_a_barline_is_not_shortened():
    """A tie over the barline is legitimate writing — the same boundary the
    reduction packer draws."""
    from scales.surface_composer import (
        OnsetBundle,
        OnsetEvent,
        _clip_to_next_onset_in_voice,
    )

    first = OnsetBundle(bar=1, beat=4.0)
    first.events = [OnsetEvent(voice="soprano", pitch="C5", duration="h")]
    second = OnsetBundle(bar=2, beat=1.0)
    second.events = [OnsetEvent(voice="soprano", pitch="D5", duration="q")]
    _clip_to_next_onset_in_voice([first, second])
    assert first.events[0].duration == "h"


def test_another_voice_does_not_clip_this_one():
    """The rule is per VOICE: a bass note under a melody note is not a
    collision."""
    from scales.surface_composer import (
        OnsetBundle,
        OnsetEvent,
        _clip_to_next_onset_in_voice,
    )

    melody = OnsetBundle(bar=1, beat=1.0)
    melody.events = [OnsetEvent(voice="soprano", pitch="C5", duration="w")]
    bass = OnsetBundle(bar=1, beat=2.0)
    bass.events = [OnsetEvent(voice="bass", pitch="C3", duration="q")]
    _clip_to_next_onset_in_voice([melody, bass])
    assert melody.events[0].duration == "w"


# ─── The line has a shape ────────────────────────────────────────────────────


def test_the_melody_between_anchors_is_not_a_straight_scale():
    """`_interpolate_melody_pitches` walked linearly through scale indices.

    A straight walk can produce only two things: a pure scale run when the
    anchors are far apart, or a repeated note when they are close. Measured on
    a realized section it gave a melody **98.3% stepwise with 0.4 direction
    changes per bar**, against this composer's own 67% and roughly 2.05. The
    line was structurally incapable of a leap or a turn.

    What replaces it is the shape every melodic doctrine in this project
    describes — Palestrina's "one high point per phrase, approached and left by
    step", the Romantic long arch: the line rises past its target and comes
    back to it. The endpoints never move; they are the harmonic anchors.
    """
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]
    pitches = composer._interpolate_melody_pitches(60, 67, 8, scale, "C major")

    assert len(pitches) == 8
    directions = {(b > a) - (b < a) for a, b in zip(pitches, pitches[1:]) if a != b}
    assert len(directions) == 2, f"the line never turns: {pitches}"
    assert max(pitches) > max(60, 67), "the arch never rises past its anchors"


def test_the_peak_lands_on_a_chord_tone_when_the_harmony_is_known():
    """The peak is the one note held long enough to be heard against the bass.

    Reaching a scale degree the harmony had ALTERED took cross-relations from 1
    to 8 in a 14-bar section, where real Chopin and Mozart run a median of
    0.2-1.9 and a maximum of 3.1.
    """
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]
    c_major = frozenset({0, 4, 7})
    pitches = composer._interpolate_melody_pitches(60, 67, 8, scale, "C major", chord_pcs=c_major)
    assert max(pitches) % 12 in c_major, f"the peak is not a chord tone: {pitches}"


def test_the_endpoints_are_never_moved():
    """They are the harmonic anchors; only the span between them is at liberty."""
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72]
    for n in (2, 3, 5, 9):
        pitches = composer._interpolate_melody_pitches(60, 67, n, scale, "C major")
        assert len(pitches) == n
        assert all(60 - 12 <= p <= 79 for p in pitches)


def test_an_empty_scale_does_not_crash():
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    assert composer._interpolate_melody_pitches(60, 67, 4, [], "C major") == [60] * 4


def test_strong_beats_are_identified_from_the_duration_profile():
    from scales.surface_composer import _strong_step_indices

    # four quarters in 4/4: steps 1 and 3 land on beats 1 and 3
    assert _strong_step_indices(["q", "q", "q", "q"], 4.0) == frozenset({1, 3})
    # in 3/4 only the downbeat is strong
    assert _strong_step_indices(["q", "q", "q"], 3.0) == frozenset({1})


# ─── The melody follows the harmony's inflections ────────────────────────────


def test_an_altered_chord_tone_replaces_the_degree_it_inflects():
    """A secondary dominant's raised third belongs in the melody too.

    The melody walked a fixed diatonic scale while the accompaniment built from
    the local chord, so the two disagreed about the same degree — the harmony's
    F# against the scale's F natural — and every cross-relation in a realized
    D-minor section was that one disagreement at several beats.
    """
    from scales.surface_composer import _scale_following_harmony

    d_minor = [62, 64, 65, 67, 69, 70, 72, 74]
    under_d7 = _scale_following_harmony(d_minor, frozenset({2, 6, 9, 0}))
    assert 66 in under_d7 and 65 not in under_d7, "F did not become F#"


def test_the_leading_tone_appears_under_the_dominant():
    """The most important chromatic inflection in minor-key writing."""
    from scales.surface_composer import _scale_following_harmony

    d_minor = [62, 64, 65, 67, 69, 70, 72, 74]
    under_a7 = _scale_following_harmony(d_minor, frozenset({9, 1, 4, 7}))
    assert 73 in under_a7, "C did not become C#"
    assert 62 in under_a7, "the TONIC was pulled to the leading tone"


def test_an_unaltered_chord_leaves_the_scale_alone():
    """The case easy to forget to check when the altered one works.

    A plain D minor triad pulled the scale's E to F — E is a semitone from F and
    F is a chord tone — destroying a legitimate degree and leaving F twice.
    """
    from scales.surface_composer import _scale_following_harmony

    d_minor = [62, 64, 65, 67, 69, 70, 72, 74]
    assert _scale_following_harmony(d_minor, frozenset({2, 5, 9})) == d_minor
    assert _scale_following_harmony(d_minor, frozenset({10, 2, 5})) == d_minor


def test_no_harmony_and_no_scale_are_both_safe():
    from scales.surface_composer import _scale_following_harmony

    assert _scale_following_harmony([62, 64], frozenset()) == [62, 64]
    assert _scale_following_harmony([], frozenset({1})) == []


def test_the_scale_keeps_its_length_and_its_order():
    """A substitution must not add, drop or reorder degrees."""
    from scales.surface_composer import _scale_following_harmony

    d_minor = [62, 64, 65, 67, 69, 70, 72, 74]
    for pcs in ({2, 6, 9, 0}, {9, 1, 4, 7}, {2, 5, 9}):
        out = _scale_following_harmony(d_minor, frozenset(pcs))
        assert len(out) == len(d_minor)
        assert out == sorted(out)


# ─── One derivation of the harmony, not two ──────────────────────────────────


def test_the_melody_reads_the_same_harmony_the_accompaniment_plays():
    """Two derivations of one fact, free to disagree — and they did.

    The accompaniment is built from `voicing_map`: what `harmonic_solver`
    actually voiced, sevenths and voice-leading alterations included. The melody
    re-derived a plain triad from the cell's roman numeral. So the
    accompaniment played F# from a solved dominant seventh while the melody was
    told the chord was D minor and kept its F natural — and every remaining
    cross-relation in a realized section was that one disagreement, reported at
    several beats.

    Reading the solved voicing took ear findings from 3 to 0.
    """
    from scales.models import HarmonicCell
    from scales.surface_composer import GestureSlot, _slot_chord_pcs

    slot = GestureSlot(bar_start=1, beat_start=1.0, bar_end=1, beat_end=4.0)
    slot.harmonic_cells = [HarmonicCell(bar=1, beat=1.0, roman="V7", key="D minor")]

    # What the solver actually voiced: A C# E G — a dominant seventh.
    voiced = {
        1: {
            "soprano_midi": 69,
            "alto_midi": 64,
            "tenor_midi": 49,
            "bass_midi": 45,
            "roman": "V7",
            "key": "D minor",
        }
    }
    from_voicing = _slot_chord_pcs(slot, "D minor", voiced)
    assert 1 in from_voicing, "C# — the solved leading tone — is missing"

    # Without the voicing it falls back to the roman, which is the old behaviour.
    from_roman = _slot_chord_pcs(slot, "D minor", None)
    assert from_roman, "the fallback must still produce something"


def test_the_roman_remains_the_fallback():
    """Callers with no solved voicing still get an answer."""
    from scales.models import HarmonicCell
    from scales.surface_composer import GestureSlot, _slot_chord_pcs

    slot = GestureSlot(bar_start=1, beat_start=1.0, bar_end=1, beat_end=4.0)
    slot.harmonic_cells = [HarmonicCell(bar=1, beat=1.0, roman="i", key="D minor")]
    pcs = _slot_chord_pcs(slot, "D minor", {})
    assert pcs and 2 in pcs, "the tonic D is missing from a i chord"


def test_a_voicing_for_another_bar_is_not_used():
    """Indexed by bar: bar 2's chord must not colour bar 1's melody."""
    from scales.models import HarmonicCell
    from scales.surface_composer import GestureSlot, _slot_chord_pcs

    slot = GestureSlot(bar_start=1, beat_start=1.0, bar_end=1, beat_end=4.0)
    slot.harmonic_cells = [HarmonicCell(bar=1, beat=1.0, roman="i", key="D minor")]
    unrelated = {2: {"soprano_midi": 61, "bass_midi": 61}}
    assert 1 not in _slot_chord_pcs(slot, "D minor", unrelated)


# ─── The cadence plays the chords its own script names ───────────────────────


def test_a_cadence_chord_is_the_one_the_script_names():
    """Two faults, one inside the other.

    The quality was hardcoded `"major"`, so a D minor cadence put F# under the
    melody's F natural. And the ROOT was always the tonic, although
    `cad.chord_sequence[idx]` names the chord for that bar — so a cadence's
    approach chords, the `V` and the `ii6` that make it a cadence at all, were
    every one of them voiced as the tonic triad. The progression was retrieved,
    indexed, and then ignored.

    `roman_pitches` is the one place that knows what a Roman numeral means —
    every degree, quality and inversion, bass first. Deriving it a second time
    is what produced both faults, and it is this repository's most reliable
    defect.
    """
    from scales.harmony_analysis import roman_pitches
    from scales.pitch import key_to_root_midi, midi_to_pitch

    tonic = key_to_root_midi("D minor") % 12

    def voiced(symbol):
        pcs = roman_pitches(symbol, tonic, "minor")
        base = 36 + ((pcs[0] - 36) % 12)
        return [
            midi_to_pitch(t, "D minor")
            for t in [base] + [base + ((pc - pcs[0]) % 12) for pc in pcs[1:]]
        ]

    # The dominant of a MINOR key is major — its third is the leading tone.
    assert voiced("V") == ["A2", "C#3", "E3"]
    # The tonic is minor, which the old key-mode shortcut got right by luck.
    assert voiced("i") == ["D2", "F2", "A2"]
    # An inversion puts a chord tone other than the root in the bass.
    assert voiced("ii6")[0] == "G2"
    # A seventh has four notes, not three.
    assert len(voiced("V7")) == 4


def test_the_dominant_is_not_given_the_keys_mode():
    """`"minor" if is_minor_key(key) else "major"` is the KEY's quality, not the
    CHORD's. Right for `i`, wrong for `V`, `VI`, `III` and `VII`."""
    from scales.harmony_analysis import roman_pitches
    from scales.pitch import key_to_root_midi

    tonic = key_to_root_midi("G minor") % 12
    dominant = roman_pitches("V", tonic, "minor")
    # D major: D F# A — the third is 4 semitones above the root, not 3.
    assert (dominant[1] - dominant[0]) % 12 == 4


# ─── A cadence is a gesture, not a held note ─────────────────────────────────


def _cadence_bundles(pitch, duration, key="D minor", bar=4):
    from scales.models import PhraseControlIR
    from scales.surface_composer import OnsetBundle, OnsetEvent

    bundle = OnsetBundle(bar=bar, beat=1.0)
    bundle.events = [OnsetEvent(voice="soprano", pitch=pitch, duration=duration)]
    control = PhraseControlIR(bar_start=1, bars=bar, meter=(4, 4))
    control.local_key = key
    control.cadence_bar = bar
    return [bundle], control


def test_a_cadence_bar_gets_an_approach_note():
    """Every phrase closed on one note filling its bar — `E4dh`, `D4dh` — so all
    three phrase endings in a section shared one rhythm, which
    `detect_cadence_formula_reuse` calls the single loudest tell of a machine.

    A cadence is a gesture: the arrival is approached, and the approach is most
    of what makes it sound like an ending rather than a stop.
    """
    from scales.surface_composer import _approach_the_cadence

    bundles, control = _cadence_bundles("D4", "dh")
    _approach_the_cadence(bundles, control)
    assert len(bundles) == 2, "the cadence is still a single held note"
    approach, arrival = bundles[0], bundles[1]
    assert approach.events[0].pitch == "E4", "2-1 is the commonest cadential approach"
    assert arrival.events[0].pitch == "D4", "the arriving pitch must not move"
    assert float(arrival.beat) > float(approach.beat)


def test_the_approach_is_diatonic_to_the_pieces_own_key():
    """`PhraseControlIR` has no `key` field — it is `local_key`. Reading `key`
    with a getattr default silently made every piece C major, which put an F#
    above the E of a D minor half cadence. Which semitone step is diatonic
    depends on where in the scale you are, so this takes the next degree of the
    KEY's scale rather than a fixed number of semitones."""
    from scales.surface_composer import _approach_the_cadence

    bundles, control = _cadence_bundles("E4", "dh", key="D minor")
    _approach_the_cadence(bundles, control)
    assert bundles[0].events[0].pitch == "F4", "F# is not in D minor"

    bundles, control = _cadence_bundles("E4", "dh", key="C major")
    _approach_the_cadence(bundles, control)
    assert bundles[0].events[0].pitch == "F4", "F is the diatonic step above E"


def test_a_cadence_that_already_has_a_gesture_is_left_alone():
    from scales.models import PhraseControlIR
    from scales.surface_composer import OnsetBundle, OnsetEvent, _approach_the_cadence

    first = OnsetBundle(bar=4, beat=1.0)
    first.events = [OnsetEvent(voice="soprano", pitch="E4", duration="q")]
    second = OnsetBundle(bar=4, beat=2.0)
    second.events = [OnsetEvent(voice="soprano", pitch="D4", duration="h")]
    control = PhraseControlIR(bar_start=1, bars=4, meter=(4, 4))
    control.local_key = "D minor"
    control.cadence_bar = 4
    bundles = [first, second]
    _approach_the_cadence(bundles, control)
    assert len(bundles) == 2, "an existing cadential gesture was overwritten"


def test_a_short_cadence_note_is_not_split():
    """Splitting a quarter gives two eighths, which is a different figure, not
    an approach."""
    from scales.surface_composer import _approach_the_cadence

    bundles, control = _cadence_bundles("D4", "q")
    _approach_the_cadence(bundles, control)
    assert len(bundles) == 1


def test_a_phrase_with_no_cadence_bar_is_untouched():
    from scales.surface_composer import _approach_the_cadence

    bundles, control = _cadence_bundles("D4", "dh")
    control.cadence_bar = None
    _approach_the_cadence(bundles, control)
    assert len(bundles) == 1


# ─── A one-note fill is still a note of the scale ────────────────────────────


def test_a_single_step_fill_stays_in_the_key():
    """`return [(start_midi + end_midi) // 2]` — the CHROMATIC midpoint.

    Out of key about half the time. In A-flat major it turned Ab4 -> Bb4 into A
    NATURAL, Bb4 -> Db5 into B natural, and Db5 -> Eb5 into D natural: three
    notes that do not exist in the key, sounding against a correctly-spelled
    left hand and surfacing as eight cross-relations in the first bars of a
    Liszt section.

    The line predates the arch and I preserved it without asking what it did.
    """
    from scales.pitch import midi_to_pitch
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    # A-flat major, two octaves
    a_flat = [56, 58, 60, 61, 63, 65, 67, 68, 70, 72, 73, 75, 77, 79]
    for start, end in ((68, 70), (70, 73), (73, 75)):
        got = composer._interpolate_melody_pitches(start, end, 1, a_flat, "Ab major")
        assert got[0] in a_flat, (
            f"{midi_to_pitch(start, 'Ab major')}->{midi_to_pitch(end, 'Ab major')} filled with "
            f"{midi_to_pitch(got[0], 'Ab major')}, which is not in A-flat major"
        )


def test_the_fill_is_the_nearest_scale_tone_to_the_midpoint():
    """Nearest, so the line still moves through the middle of the span."""
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    c_major = [60, 62, 64, 65, 67, 69, 71, 72]
    assert composer._interpolate_melody_pitches(60, 64, 1, c_major, "C major") == [62]


def test_a_single_step_fill_survives_an_empty_scale():
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    assert composer._interpolate_melody_pitches(60, 64, 1, [], "C major") == [60]
