"""A bar planned as a texture has to be written as that texture.

The RH plan was good — Chopin's `zigzag_figuration` was scheduled at 19.5%
against a real 16.3% — and none of it reached the score: every zigzag bar came
back classified `singing_melody`, so the piece held 0% of a texture that is a
sixth of the composer.

Two independent reasons, one per axis of the classifier:

* DENSITY. `_classify_rh_texture` wants more than two notes per beat. The slot
  carried a `density_target` that nothing read, and the melody took its note
  count from whatever gesture was retrieved — a cell shorter than the slot
  simply stopped, leaving the rest empty.
* CONTOUR. The same classifier calls anything 60% stepwise a `scalar_run`, and
  the melody is built by walking scale indices between two anchors, which over
  a short span can produce nothing else.
"""

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scales.composition_brief import median_bar_texture_density  # noqa: E402
from scales.duration import DURATION_VALUES, dur_to_beats  # noqa: E402
from scales.surface_composer import (  # noqa: E402
    SurfaceComposer,
    _duration_code_for,
    _tuplet_family_of,
)


def test_the_density_target_follows_the_metre_not_just_the_composer():
    """Chopin's zigzag is 8 notes in 3/4 and 12 in 4/4.

    The pooled median is 8 because 902 of his 1303 zigzag bars are mazurkas.
    Handing that to a 4/4 piece asks for two thirds of the notes he writes —
    the aggregate-vs-member error, in the one place it decides note counts.
    """
    in_four = median_bar_texture_density("chopin", "zigzag_figuration", "rh", (4, 4))
    in_three = median_bar_texture_density("chopin", "zigzag_figuration", "rh", (3, 4))
    assert in_four and in_three
    assert in_four > in_three, (in_four, in_three)


def test_an_unattested_texture_returns_nothing_rather_than_a_number():
    """So the caller keeps its own default instead of aiming at a stray."""
    assert median_bar_texture_density("chopin", "not_a_texture", "rh", (4, 4)) is None


def test_a_zigzag_is_not_written_as_a_scale():
    """The contour axis, measured the way the classifier measures it."""
    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]

    def stepwise_share(pitches):
        moves = [abs(b - a) for a, b in zip(pitches, pitches[1:]) if b != a]
        if not moves:
            return 1.0
        return sum(1 for m in moves if m <= 2) / len(moves)

    walked = composer._interpolate_melody_pitches(60, 67, 12, scale, "C major")
    turned = composer._interpolate_melody_pitches(60, 67, 12, scale, "C major", zigzag=True)
    assert stepwise_share(walked) >= 0.6, "the walk is stepwise, which is the premise here"
    assert stepwise_share(turned) < 0.6, stepwise_share(turned)


def test_the_anchors_survive_the_zigzag():
    """The endpoints are harmonic facts; only the shape between them is free."""
    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76]
    plain = composer._interpolate_melody_pitches(60, 67, 9, scale, "C major")
    zig = composer._interpolate_melody_pitches(60, 67, 9, scale, "C major", zigzag=True)
    assert zig[0] == plain[0]
    assert zig[-1] == plain[-1]


def test_the_fitter_never_invents_a_tuplet_family():
    """A sliver in a quintuplet run must not be filled with a triplet.

    `_duration_code_for` took the longest value that fit from every code, so
    filling the remainder of a quintuplet bar chose a triplet-16th, then a
    64th, then a triplet-32nd rest — three families inside a quarter of one
    beat, in the middle of a quintuplet group. music21 completes such groups
    during `makeNotation` and needs a 2048th to do it, which MusicXML cannot
    express: the export raises and the entire score is lost.
    """
    quintuplet = Fraction(1, 5)
    fitted = _duration_code_for(Fraction(1, 6), _tuplet_family_of(quintuplet))
    assert fitted is not None
    assert _tuplet_family_of(fitted[1]) in (frozenset({5}), frozenset()), fitted


def test_the_fitter_keeps_a_note_in_its_own_family_when_it_can():
    """A shortened triplet stays a triplet, so its group survives."""
    triplet = Fraction(1, 3)
    fitted = _duration_code_for(Fraction(1, 3), _tuplet_family_of(triplet))
    assert fitted is not None
    assert _tuplet_family_of(fitted[1]) == frozenset({3}), fitted


def test_the_fitter_falls_back_to_binary_rather_than_a_foreign_family():
    """When nothing of the note's own family fits, binary — never another tuplet."""
    fitted = _duration_code_for(Fraction(1, 16), frozenset({5}))
    if fitted is not None:
        assert not _tuplet_family_of(fitted[1]), fitted


@pytest.mark.parametrize("code", sorted(DURATION_VALUES))
def test_every_duration_the_shorthand_knows_is_notatable(code):
    """The padding rest snaps to this set; nothing outside it may be written."""
    assert dur_to_beats(code) > 0


def test_padding_never_pushes_a_bar_past_its_barline():
    """The pad rest must FIT, and must be notatable.

    Two ways to get this wrong and both were live: writing a rest of whatever
    was missing (an unnotatable 33/1024, which music21 renders as a 2048th and
    refuses to export), and snapping that to the shortest notatable value
    (a 64th — longer than the gap, so the bar ends up overfull, which is the
    one thing this function exists to prevent).
    """
    music21 = pytest.importorskip("music21")
    from scales.assembler import _pad_measure_to_meter

    measure = music21.stream.Measure()
    note = music21.note.Note("C5")
    note.duration = music21.duration.Duration(float(Fraction(127, 32)))
    measure.insert(0.0, note)

    _pad_measure_to_meter(measure, music21, 4.0)

    assert float(measure.highestTime) <= 4.0 + 1e-9, float(measure.highestTime)
    notatable = set(DURATION_VALUES.values())
    for rest in measure.getElementsByClass(music21.note.Rest):
        assert Fraction(rest.duration.quarterLength).limit_denominator(1680) in notatable


def _melody_for(target, profile, span_beats=2.0):
    """Run the real melody constructor over one slot, with a dense cell."""
    from scales.models import ContextTrace, GestureResult, PhraseControlIR
    from scales.surface_composer import GestureSlot

    composer = SurfaceComposer.__new__(SurfaceComposer)
    composer.motif_bank = None
    composer.gesture_bank = None
    slot = GestureSlot(
        bar_start=1,
        beat_start=1.0,
        bar_end=1,
        beat_end=1.0 + span_beats,
        span_beats=span_beats,
        function="continuation",
        rh_texture="singing_melody",
        lh_texture="alberti",
        density_target=target,
    )
    gesture = GestureResult(
        cell_id="test", function="continuation", span_beats=span_beats, dur_profile=list(profile)
    )
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]
    events = composer._construct_melody(
        slot, 60, 72, gesture, scale, "C major", 4.0, ContextTrace(), PhraseControlIR()
    )
    return [e for e in events if e.voice == "soprano"]


def test_the_bars_note_count_is_a_ceiling_as_well_as_a_floor():
    """Overshooting a texture misclassifies it exactly as undershooting does.

    Retrieval prefers a cell running at the wanted rate, but the bank scores
    that at 0.10 and can be outvoted, so a slot could still be handed a figure
    at twice the texture's speed: a `singing_melody` bar asking six notes came
    back with ten, which `_classify_rh_texture` calls a `scalar_run`.
    """
    # Sixteen 32nds in a 2-beat slot — four times what a 6-note bar asks for.
    written = _melody_for(target=6, profile=["t"] * 16)
    allowed = max(1, int(round(6 * (2.0 / 4.0) * 1.25)))
    assert len(written) <= allowed, f"{len(written)} notes written, budget {allowed}"


def test_the_shared_anchor_is_not_charged_to_every_slot():
    """A bar is written by two slots and they share the instant between them.

    The second slot's anchor lands on the first slot's last instant, where the
    surface repair de-duplicates it, so charging every slot for its own anchor
    removes a note that was never written twice. With the target in
    outer-attack units that left TWO attacks in a four-attack bar, and 16 of
    Chopin's `singing_melody` bars came out as `held_note`.
    """
    written = _melody_for(target=4, profile=["e"] * 8)
    allowed = max(1, int(round(4 * (2.0 / 4.0))))
    assert written, "the budget must not silence the slot"
    # The slot gets its own share of the bar's attacks, not that share minus
    # the anchor it shares with its neighbour.
    assert len(written) >= allowed, f"{len(written)} written, the slot's share is {allowed}"


def test_the_budget_allows_an_idiomatic_figure_its_last_note():
    """A quarter over the asked-for count, so a real figure is not clipped."""
    for target, span, bar in ((6, 2.0, 4.0), (12, 4.0, 4.0), (8, 3.0, 3.0)):
        budget = max(1, int(round(target * (span / bar) * 1.25)))
        exact = target * (span / bar)
        assert budget >= exact, (target, span, bar, budget)
        assert budget <= exact * 1.4, (target, span, bar, budget)


def test_a_figure_keeps_its_reach_when_it_is_fitted_to_the_harmony():
    """`broken_chord_wave` and `alberti` differ by REACH, not by density.

    Real Chopin runs twelve attacks to the bar in both; the wave covers 18
    semitones and the Alberti 11, and the corpus classifier's boundary is 12.
    Snapping each note independently to its nearest chord tone moves every one
    by up to six semitones and the movement is inward on average, so a figure
    arrived spanning 14 and left spanning 12 — written as an Alberti bass in 14
    of 22 bars planned as waves.
    """
    from scales.surface_composer import _displace_into

    # The outermost notes must be able to move outward, not only inward.
    assert _displace_into(20, (28, 79)) >= 28
    assert _displace_into(90, (28, 79)) <= 79
    # An octave move keeps the pitch class, where a clamp would not.
    assert _displace_into(20, (28, 79)) % 12 == 20 % 12
    assert _displace_into(90, (28, 79)) % 12 == 90 % 12


def test_the_left_hand_register_holds_the_composers_who_use_it():
    """A 36-60 window excludes 24-37% of every real left hand measured.

    Mozart 36.8%, Beethoven 24.6%, Chopin 24.0%, over 226,000 notes — a guard
    that sounds careful and rejects a third of the population. 28-79 excludes
    0.5% of the worst-served composer.
    """
    from scales.surface_composer import LH_PATTERN_RANGE

    low, high = LH_PATTERN_RANGE
    assert high - low >= 42, "a left hand needs more than two octaves"
    # Wide enough for a real broken-chord wave, whose 90th percentile is 25.
    assert high - low >= 25


def test_an_accompaniment_pattern_has_to_fill_the_bar_it_is_put_in():
    """The library stores each pattern at the length of ITS OWN bar.

    Nothing checked that against the bar it was poured into, so a three-beat
    figure — a mazurka's — covered three beats of a 4/4 bar and the left hand
    simply stopped. Measured on the assembled score, the accompaniment fell
    silent before the barline in 100% of `block_chord_sparse` bars, 79% of
    `alberti` and 50% of `broken_chord_wave`, against a real 25%, 18% and 3%
    in Chopin.

    Real music does leave a bar's tail silent — it is an ordinary thing to do,
    at 2-44% depending on idiom and composer — so this is a rate, not a rule,
    which is why the selection prefers a fitting pattern rather than padding
    a short one.
    """
    from scales.pattern_retriever import PatternRetriever

    retriever = PatternRetriever()
    for idiom in ("alberti", "block_chord_sparse", "broken_chord_wave"):
        patterns = retriever.retrieve(texture=idiom, n=48)
        assert patterns, idiom
        lengths = {round(float(p.get("duration_total") or 0), 2) for p in patterns}
        assert 4.0 in lengths, (
            f"{idiom}: no four-beat pattern among 48 — a 4/4 bar could not be filled"
        )


def test_the_pattern_pool_is_big_enough_to_choose_from():
    """Eight was too few once anything downstream had a second criterion.

    Of eight offered for an idiom, as few as NONE were the right length for the
    bar, so metre-matching had nothing to match against.
    """
    from scales.pattern_retriever import PatternRetriever

    retriever = PatternRetriever()
    patterns = retriever.retrieve(texture="alberti", n=48)
    fitting = [p for p in patterns if abs(float(p.get("duration_total") or 0) - 4.0) < 1e-6]
    assert len(fitting) >= 3, f"only {len(fitting)} four-beat alberti patterns to rotate over"


def test_a_line_that_runs_out_is_held_not_dropped():
    """A line that STOPS is not the same as a line that RESTS.

    The melody took its length from the retrieved cell and from the slot's note
    budget, and when either ran out the emit loop stopped — leaving the rest of
    the bar with no melody. `_pad_measure_to_meter` filled the gap with a rest,
    so the bar notated correctly and SOUNDED empty, which is why nothing
    upstream objected. Measured on the assembled score, the melody fell silent
    before the barline in 54% of Chopin's bars and 68% of Mozart's against a
    real 8-14%, and in 100% of `chordal` bars.
    """
    from scales.duration import dur_to_beats

    # A four-note cell in a bar wanting four notes: the last note has to carry
    # to the barline rather than leaving a beat of nothing.
    written = _melody_for(target=4, profile=["q"] * 2, span_beats=4.0)
    assert written
    last = written[-1]
    ends_at = float(last._beat) + float(dur_to_beats(last.duration))
    assert ends_at >= 5.0 - 1e-6, f"the line stops at beat {ends_at} of a 4/4 bar"


def test_holding_the_last_note_does_not_add_an_attack():
    """The bar's note COUNT is unchanged; only the final duration grows.

    Filling the tail by emitting more notes would undo the per-slot ceiling and
    push a singing melody back into scalar-run territory.
    """
    short = _melody_for(target=4, profile=["q"] * 2, span_beats=4.0)
    assert len(short) <= max(1, int(round(4 * (4.0 / 4.0) * 1.25)))


def test_the_arch_does_not_round_two_steps_onto_one_note():
    """A line that rounds twice onto one degree is not a repeated note.

    `_interpolate_melody_pitches` walks scale INDICES and rounds each to the
    nearest, so whenever more notes are asked for than the span has indices,
    consecutive steps land on the same degree. Measured against the corpus the
    melody repeated its pitch in 20% of adjacent pairs against a real 8-9% —
    a line sitting on one note is among the plainest tells of a machine, and
    none of those repeats was chosen.
    """
    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]
    # Twelve notes over a third: far more steps than the span has degrees, so
    # the unguarded arch can only round onto repeats.
    pitches = composer._interpolate_melody_pitches(60, 64, 12, scale, "C major")
    repeats = sum(1 for a, b in zip(pitches, pitches[1:]) if a == b)
    share = repeats / max(1, len(pitches) - 1)
    assert share <= 0.25, f"{share:.0%} of adjacent pairs repeat"


def test_a_line_still_turns():
    """Nudging a rounded repeat must not straighten the arch into a scale."""
    composer = SurfaceComposer.__new__(SurfaceComposer)
    scale = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79]
    pitches = composer._interpolate_melody_pitches(60, 67, 10, scale, "C major")
    signs = [1 if b > a else -1 for a, b in zip(pitches, pitches[1:]) if b != a]
    turns = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    assert turns >= 1, "the arch has to come back down"


def test_the_density_target_is_in_the_units_the_generator_writes():
    """Two quantities were both called density, and the generator got the wrong one.

    `melody_density` counts attacks across `rh_display` AND `rh_inner_display` —
    voice-events, not rhythmic positions. Real music spends the difference on
    simultaneities: a Chopin `chordal` bar reads 6 by that count, has 4 outer
    attacks and carries 9 notes. A single-voice generator handed 6 spends every
    unit on a separate rhythmic position, which is how a bar ends up with three
    and four distinct note values where half of his use one.
    """
    outer = median_bar_texture_density("chopin", "chordal", "rh", (4, 4))
    assert outer is not None
    # The outer-voice count must be below the voice-event count it replaced.
    assert outer <= 5, f"chordal target {outer} is still the voice-event count"


def test_the_uniform_preference_is_asked_of_the_right_metre():
    """A composer's uniform-bar rate swings by three and a half times between metres.

    Chopin's `zigzag_figuration` is 81% single-value in 4/4 and 23% in 3/4,
    because his 3/4 corpus is mazurkas. Preferring a uniform figure on the 4/4
    figure would impose it on a mazurka.
    """
    from scales.composition_brief import uniform_bar_share

    in_four = uniform_bar_share("chopin", "zigzag_figuration", "rh", (4, 4))
    in_three = uniform_bar_share("chopin", "zigzag_figuration", "rh", (3, 4))
    assert in_four and in_three
    assert in_four >= 0.5, in_four
    assert in_three < 0.5, in_three
    assert in_four > in_three * 2, (in_four, in_three)


def test_the_uniform_threshold_sits_where_the_data_separates():
    """0.40, not 0.50, and the difference is a real composer.

    Mozart writes 44% of his 4/4 `chordal` bars in one note value. A threshold
    of a half excluded him and took our single-value share to 0% against that
    44%; 0.40 admits him and still refuses Chopin's 3/4 textures, which sit at
    0.19-0.25 because his 3/4 corpus is mazurkas.
    """
    from scales.composition_brief import uniform_bar_share

    admitted = uniform_bar_share("mozart", "chordal", "rh", (4, 4))
    refused = uniform_bar_share("chopin", "zigzag_figuration", "rh", (3, 4))
    assert admitted is not None and refused is not None
    assert refused < 0.40 <= admitted, (refused, admitted)


def test_four_voices_sound_all_four_notes_of_a_seventh_chord():
    """The inner voices complete the chord; they do not pick by register.

    Taking the lowest and highest inner candidate chooses by REGISTER, and with
    the bass on the root and the soprano on the fifth those extremes can be two
    octaves of the third — so the seventh, the note that makes it a seventh
    chord, is never sounded. The plan asks for sevenths in 19.5% of Mozart's
    chords and the written score analysed at 5.1%, against his real 14.1%.
    """
    from scales.harmonic_solver import HarmonicSolver

    solver = HarmonicSolver.__new__(HarmonicSolver)
    # G7 spelled from G2: G B D F.
    tones = [43, 47, 50, 53]
    bass, soprano = 43, 62  # root in the bass, fifth on top
    alto, tenor = solver._fill_inner(tones, soprano, bass)
    sounded = {bass % 12, soprano % 12, tenor % 12, alto % 12}
    assert 53 % 12 in sounded, f"the seventh is missing: {sorted(sounded)}"


def test_a_triad_still_voices_without_complaint():
    """Falsification: the completion rule must not break a three-note chord."""
    from scales.harmonic_solver import HarmonicSolver

    solver = HarmonicSolver.__new__(HarmonicSolver)
    tones = [48, 52, 55]  # C major
    alto, tenor = solver._fill_inner(tones, 72, 48)
    assert 48 <= tenor <= 72 and 48 <= alto <= 72
    assert tenor <= alto, "the tenor must not sit above the alto"


def test_a_tuplet_is_written_as_a_complete_group():
    """A fragment is finished by music21, and it finishes it by SPLITTING.

    52 of 52 triplet runs in a generated piece were fragments — 32 a single
    note, 20 a pair — because a corpus cell carries whatever its source bar's
    group was cut to. Emitted as they stand, a seventh of the written notes came
    out as triplet-16ths nobody composed, against real Mozart's 0.3%.
    """
    from scales.surface_composer import _complete_tuplet_groups

    assert _complete_tuplet_groups(["trip_e"]) == ["trip_e"] * 3
    assert _complete_tuplet_groups(["trip_e", "trip_e"]) == ["trip_e"] * 3
    # A group that is already whole is left exactly as it is.
    assert _complete_tuplet_groups(["trip_e"] * 3) == ["trip_e"] * 3
    # Binary values are untouched, and a run is padded in place.
    assert _complete_tuplet_groups(["q", "trip_e", "q"]) == ["q"] + ["trip_e"] * 3 + ["q"]


def test_completion_preserves_elapsed_time():
    """Padding to a whole group keeps the bar's arithmetic.

    Rewriting a fragment to a binary value downstream loses a twelfth of a beat
    per note, which is what opens rests at the barline; completing the group
    does not.
    """
    from scales.surface_composer import _as_fraction, _complete_tuplet_groups

    padded = _complete_tuplet_groups(["trip_e"])
    assert sum((_as_fraction(c) for c in padded), Fraction(0)).denominator == 1
