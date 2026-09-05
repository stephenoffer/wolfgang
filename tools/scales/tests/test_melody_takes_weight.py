"""The melody thickens at its arrivals, and assembly never rewrites the piece.

Real keyboard writing chords 17% of right-hand attacks — measured over ~206,000
attacks by Mozart, Beethoven, Chopin, Schubert, Haydn, Liszt and Brahms, and
strongly personal (Haydn 6.7%, Mozart 8.5%, Chopin 23.8%, Liszt 50.5%). The
engine wrote 0%, so nothing ever sounded fuller than anything else.
"""

from dataclasses import replace

import pytest

from scales.assembler import _merge_simultaneous_into_chords
from scales.models import LayerEvent, LayerIR
from scales.pitch import pitch_to_midi
from scales.surface_composer import _thicken_principal_line


def _line(pitches, key="D minor"):
    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key=key, meter=(4, 4), bar_count=4
    )
    layer.principal_line = [
        LayerEvent(
            bar=1 + i // 4, beat=1.0 + (i % 4), pitch=p, duration="q", role="structural"
        )
        for i, p in enumerate(pitches)
    ]
    return layer


_TUNE = ["D5", "E5", "F5", "G5", "A5", "G5", "F5", "E5", "D5", "F5", "A5", "D6"]


def test_the_melody_gets_weight_at_its_arrivals():
    layer = _line(_TUNE)
    before = len(layer.principal_line)
    added = _thicken_principal_line(layer, "D minor", share=0.25)
    assert added > 0
    assert len(layer.principal_line) == before + added


def test_the_added_note_sits_below_the_melody():
    """The line must stay the top voice — a doubling above it takes the tune."""
    layer = _line(_TUNE)
    _thicken_principal_line(layer, "D minor", share=0.25)
    by_instant: dict = {}
    for e in layer.principal_line:
        by_instant.setdefault((e.bar, e.beat), []).append(pitch_to_midi(e.pitch))
    original = {
        (1 + i // 4, 1.0 + (i % 4)): pitch_to_midi(p) for i, p in enumerate(_TUNE)
    }
    for instant, midis in by_instant.items():
        assert max(midis) == original[instant], f"the doubling took the tune at {instant}"


def test_the_peak_takes_the_octave():
    layer = _line(_TUNE)
    _thicken_principal_line(layer, "D minor", share=0.25)
    peak = max(layer.principal_line, key=lambda e: pitch_to_midi(e.pitch))
    partners = [
        pitch_to_midi(e.pitch)
        for e in layer.principal_line
        if (e.bar, e.beat) == (peak.bar, peak.beat) and e is not peak
    ]
    assert partners, "the phrase's peak was not thickened"
    assert pitch_to_midi(peak.pitch) - max(partners) == 12


def test_every_added_note_is_in_the_key():
    for key in ("D minor", "C major", "F# minor", "Eb major"):
        layer = _line(_TUNE, key=key)
        originals = {id(e) for e in layer.principal_line}
        _thicken_principal_line(layer, key, share=0.3)
        from scales.pitch import build_scale, is_minor_key, key_to_root_midi

        mode = "minor" if is_minor_key(key) else "major"
        pcs = {m % 12 for m in build_scale(key_to_root_midi(key) + 24, mode, octaves=6)}
        for e in layer.principal_line:
            if id(e) in originals:
                continue
            assert pitch_to_midi(e.pitch) % 12 in pcs, f"{e.pitch} is not in {key}"


def test_a_short_line_is_left_alone():
    """Too few notes for an arrival to mean anything."""
    layer = _line(["D5", "E5", "F5"])
    assert _thicken_principal_line(layer, "D minor") == 0


def test_an_instant_that_already_has_a_chord_is_not_thickened_again():
    layer = _line(_TUNE)
    layer.principal_line.append(
        LayerEvent(bar=1, beat=1.0, pitch="A4", duration="q", role="structural")
    )
    layer.principal_line.sort(key=lambda e: (e.bar, float(e.beat)))
    _thicken_principal_line(layer, "D minor", share=0.5)
    at_one = [e for e in layer.principal_line if (e.bar, e.beat) == (1, 1.0)]
    assert len(at_one) == 2, "the composer's own chord was added to"


# ─── assembly reads the piece; it does not compose it ────────────────────────


def test_merging_chords_does_not_mutate_the_events_it_was_given():
    """Setting `top.pitch = [...]` in place wrote the merged chord back into the
    PieceGraph — assembling a piece silently rewrote it, and the engine's
    never-touch-agent-work guarantee failed on the second assembly."""
    a = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural")
    b = LayerEvent(bar=1, beat=1.0, pitch="E5", duration="q", role="structural")
    for e in (a, b):
        e.voice = 1
    merged, aliases = _merge_simultaneous_into_chords([a, b])
    assert a.pitch == "C5" and b.pitch == "E5", "the inputs were mutated"
    assert len(merged) == 1
    assert sorted(merged[0].pitch) == ["C5", "E5"]
    assert aliases, "the chord must answer to the id that carries the marks"


def test_different_durations_at_one_onset_stay_two_voices():
    """A pedal under figuration is genuinely two voices, not a chord."""
    a = LayerEvent(bar=1, beat=1.0, pitch="C3", duration="w", role="pedal_support")
    b = LayerEvent(bar=1, beat=1.0, pitch="E4", duration="e", role="arpeggiated_fill")
    for e in (a, b):
        e.voice = 1
    merged, _ = _merge_simultaneous_into_chords([a, b])
    assert len(merged) == 2


def test_a_pitch_that_is_already_a_chord_is_left_alone():
    a = LayerEvent(bar=1, beat=1.0, pitch=["C5", "E5"], duration="q", role="structural")
    merged, _ = _merge_simultaneous_into_chords([a])
    assert merged[0].pitch == ["C5", "E5"]
    assert merged[0] is a or replace(a) == merged[0]


# ─── the line leans into the next bar ────────────────────────────────────────


def _two_bars(last_pitch, downbeat_pitch, downbeat_role):
    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=4
    )
    events = []
    for bar in (1, 2, 3, 4):
        for i, beat in enumerate((1.0, 2.0, 3.0, 4.0)):
            pitch = "E5"
            role = "structural" if beat == 1.0 else "passing"
            if bar == 2 and beat == 4.0:
                pitch = last_pitch
            if bar == 3 and beat == 1.0:
                pitch, role = downbeat_pitch, downbeat_role
            events.append(
                LayerEvent(bar=bar, beat=beat, pitch=pitch, duration="q", role=role)
            )
    layer.principal_line = events
    return layer


def test_a_line_may_be_held_over_the_barline():
    from scales.surface_composer import _hold_over_barline

    layer = _two_bars("G5", "F5", "passing")
    assert _hold_over_barline(layer, (4, 4), share=1.0) > 0
    starts = [e for e in layer.principal_line if e.tie == "start"]
    stops = [e for e in layer.principal_line if e.tie == "stop"]
    assert starts and len(starts) == len(stops)
    for start, stop in zip(starts, stops):
        assert stop.pitch == start.pitch, "a tie must join one pitch to itself"
        assert stop.bar == start.bar + 1 and stop.beat == 1.0


def test_a_theme_statement_downbeat_is_not_swallowed():
    """A suspension DISPLACES a structural arrival — that is what makes it a
    suspension — so refusing every structural downbeat was too strong. Once a
    theme is placed almost every downbeat is structural, and this pass went
    idle on Bach, Haydn and Schubert: Schubert's quota granted four ties and
    found nothing eligible for one.

    What must keep its downbeat is a bar where the theme is STATED, and those
    bars are named explicitly."""
    from scales.surface_composer import _hold_over_barline

    layer = _two_bars("G5", "F5", "structural")
    before = [(e.bar, e.beat, e.pitch) for e in layer.principal_line]
    _hold_over_barline(layer, (4, 4), share=1.0, protect_bars=frozenset({3}))
    assert [(e.bar, e.beat, e.pitch) for e in layer.principal_line] == before


def test_a_structural_downbeat_outside_the_theme_may_be_held_into():
    """The other half of the same claim — and a rule with only one side
    asserted is the one that gets half-reverted later."""
    from scales.surface_composer import _hold_over_barline

    layer = _two_bars("G5", "F5", "structural")
    assert _hold_over_barline(layer, (4, 4), share=1.0) > 0
    assert any(e.tie == "start" for e in layer.principal_line)


def test_a_repeated_pitch_across_the_barline_becomes_one_held_note():
    from scales.surface_composer import _hold_over_barline

    layer = _two_bars("G5", "G5", "structural")
    assert _hold_over_barline(layer, (4, 4), share=1.0) > 0
    assert any(e.tie == "start" for e in layer.principal_line)


def test_holding_never_lengthens_a_bar():
    from scales.duration import dur_to_beats
    from scales.surface_composer import _hold_over_barline

    layer = _two_bars("G5", "F5", "passing")
    _hold_over_barline(layer, (4, 4), share=1.0)
    by_bar: dict = {}
    for e in layer.principal_line:
        end = float(e.beat) + float(dur_to_beats(e.duration))
        by_bar[e.bar] = max(by_bar.get(e.bar, 0.0), end)
    for bar, end in by_bar.items():
        assert end <= 5.0 + 1e-6, f"bar {bar} runs to {end} in 4/4"


def test_a_short_line_is_not_held():
    from scales.surface_composer import _hold_over_barline

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=1
    )
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0 + i, pitch="E5", duration="q", role="structural")
        for i in range(4)
    ]
    assert _hold_over_barline(layer, (4, 4)) == 0


# ─── the left hand takes weight too ──────────────────────────────────────────


def _bass_line(pitches, key="D minor"):
    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key=key, meter=(4, 4), bar_count=4
    )
    layer.bass_foundation = [
        LayerEvent(
            bar=1 + i // 4, beat=1.0 + (i % 4), pitch=p, duration="q", role="bass_foundation"
        )
        for i, p in enumerate(pitches)
    ]
    return layer


_BASS = ["D3", "A2", "D3", "F3", "A2", "D3", "G2", "A2", "D3", "F3", "A2", "D3"]


def test_the_left_hand_thickens():
    """Real left hands are 12-38% chords — Mozart 18.5%, Haydn 11.9%, Chopin
    37.9% over 164,000 attacks. This engine wrote 0%, and that is why its
    accompaniment had 11 distinct bar-shapes where real Mozart 3/8 has 14."""
    from scales.surface_composer import _thicken_bass_foundation

    layer = _bass_line(_BASS)
    before = len(layer.bass_foundation)
    added = _thicken_bass_foundation(layer, "D minor", share=0.25)
    assert added > 0
    assert len(layer.bass_foundation) == before + added


def test_the_added_note_sits_above_the_bass():
    """The mirror of the melody rule: there the tune stays the top voice, here
    the bass must stay the bottom one."""
    from scales.surface_composer import _thicken_bass_foundation

    layer = _bass_line(_BASS)
    _thicken_bass_foundation(layer, "D minor", share=0.3)
    by_instant: dict = {}
    for e in layer.bass_foundation:
        by_instant.setdefault((e.bar, e.beat), []).append(pitch_to_midi(e.pitch))
    original = {
        (1 + i // 4, 1.0 + (i % 4)): pitch_to_midi(p) for i, p in enumerate(_BASS)
    }
    for instant, midis in by_instant.items():
        assert min(midis) == original[instant], f"the doubling went under the bass at {instant}"


def test_the_left_hand_stays_within_one_hand():
    from scales.surface_composer import BASS_RANGE, _thicken_bass_foundation

    layer = _bass_line(_BASS)
    _thicken_bass_foundation(layer, "D minor", share=0.5)
    by_instant: dict = {}
    for e in layer.bass_foundation:
        by_instant.setdefault((e.bar, e.beat), []).append(pitch_to_midi(e.pitch))
    for instant, midis in by_instant.items():
        assert max(midis) - min(midis) <= 12, f"span of {max(midis) - min(midis)} at {instant}"
        assert BASS_RANGE[0] <= min(midis) and max(midis) <= BASS_RANGE[1]


def test_every_added_bass_note_is_in_the_key():
    from scales.pitch import build_scale, is_minor_key, key_to_root_midi
    from scales.surface_composer import _thicken_bass_foundation

    for key in ("D minor", "C major", "Eb major"):
        layer = _bass_line(_BASS, key=key)
        originals = {id(e) for e in layer.bass_foundation}
        _thicken_bass_foundation(layer, key, share=0.4)
        mode = "minor" if is_minor_key(key) else "major"
        pcs = {m % 12 for m in build_scale(key_to_root_midi(key) + 24, mode, octaves=6)}
        for e in layer.bass_foundation:
            if id(e) not in originals:
                assert pitch_to_midi(e.pitch) % 12 in pcs, f"{e.pitch} is not in {key}"


def test_a_share_of_zero_does_nothing():
    """`max(1, round(n * share))` still thickened one note at share 0, which made
    a control arm that was not a control."""
    from scales.surface_composer import _thicken_bass_foundation

    layer = _bass_line(_BASS)
    assert _thicken_bass_foundation(layer, "D minor", share=0.0) == 0
    assert len(layer.bass_foundation) == len(_BASS)


# ─── the gap report must see both ways a chord is written ────────────────────
#
# These need no corpus, so they belong here rather than in
# `test_voicing_profile.py`, whose file-level `calibration` mark would deselect
# them from every ordinary run — a test that cannot fail in CI is a test that
# is not protecting anything.


def test_a_chord_written_as_coincident_events_counts_as_thickness():
    """A CHORD HAS TWO REPRESENTATIONS. The agent writes `[E4,G4,C5]`, which
    arrives as one event with a list pitch; the engine writes coincident events
    at one instant. Testing `isinstance(pitch, list)` reported 0.0% on a piece
    whose right hand was thickened 10.3% of the time, and the brief then told
    its composer "not once so far — a bare single line the whole way"."""
    from scales.composition_brief import _rh_thickness_so_far
    from scales.models import LayerEvent, LayerIR, PhraseState

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=1
    )
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", role="structural"),
        LayerEvent(bar=1, beat=1.0, pitch="E5", duration="q", role="structural"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q", role="passing"),
        LayerEvent(bar=1, beat=3.0, pitch="E5", duration="q", role="passing"),
        LayerEvent(bar=1, beat=4.0, pitch="F5", duration="q", role="passing"),
    ]

    class _G:
        phrases = {"p": PhraseState(realized=layer)}

    got = _rh_thickness_so_far(_G())
    assert got is not None
    assert abs(got - 0.25) < 1e-9, f"expected 1 of 4 instants thickened, got {got}"


def test_a_list_pitch_still_counts():
    """The representation that always worked must keep working."""
    from scales.composition_brief import _rh_thickness_so_far
    from scales.models import LayerEvent, LayerIR, PhraseState

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=1
    )
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0, pitch=["C5", "E5"], duration="q", role="structural"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q", role="passing"),
    ]

    class _G:
        phrases = {"p": PhraseState(realized=layer)}

    assert abs(_rh_thickness_so_far(_G()) - 0.5) < 1e-9


def test_a_unison_doubling_is_not_thickness():
    """Two voices on the same pitch is one sound, not a chord."""
    from scales.composition_brief import _rh_thickness_so_far
    from scales.models import LayerEvent, LayerIR, PhraseState

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=1
    )
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0, pitch=["C5", "C5"], duration="q", role="structural"),
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="q", role="passing"),
    ]

    class _G:
        phrases = {"p": PhraseState(realized=layer)}

    assert _rh_thickness_so_far(_G()) == 0.0


def test_the_left_hand_has_its_own_gap_report():
    from scales.composition_brief import _lh_thickness_so_far
    from scales.models import LayerEvent, LayerIR, PhraseState

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="C major", meter=(4, 4), bar_count=1
    )
    layer.bass_foundation = [
        LayerEvent(bar=1, beat=1.0, pitch="C3", duration="q", role="bass_foundation"),
        LayerEvent(bar=1, beat=1.0, pitch="G3", duration="q", role="bass_foundation"),
        LayerEvent(bar=1, beat=3.0, pitch="C3", duration="q", role="bass_foundation"),
    ]

    class _G:
        phrases = {"p": PhraseState(realized=layer)}

    assert abs(_lh_thickness_so_far(_G()) - 0.5) < 1e-9


# ─── how wide the left hand's chord is depends on where it sits ──────────────


def test_a_low_bass_is_thickened_at_the_octave_not_the_third():
    """A third low in the register is mud — the partials collide. Measured over
    41,000 real LH chords: with the bass below C2 the median interval above it
    is 12 semitones and only 4.8% are under a fourth; above C3 the median is 4
    and half are under a fourth.

    Trying a third first regardless produced eleven `muddy_low_interval`
    warnings on a piece that had none.
    """
    from scales.surface_composer import _thicken_bass_foundation

    low = ["D2", "A1", "D2", "F2", "A1", "D2", "G1", "A1", "D2", "F2", "A1", "D2"]
    layer = _bass_line(low)
    _thicken_bass_foundation(layer, "D minor", share=0.4)
    by_instant: dict = {}
    for e in layer.bass_foundation:
        by_instant.setdefault((e.bar, e.beat), []).append(pitch_to_midi(e.pitch))
    thickened = [v for v in by_instant.values() if len(v) > 1]
    assert thickened, "nothing was thickened"
    for midis in thickened:
        interval = max(midis) - min(midis)
        assert interval >= 7, f"{interval} semitones above a bass at {min(midis)} is mud"


def test_a_higher_bass_still_takes_a_third():
    """The rule is register-dependent, not "always wide" — above C3 the third is
    what the corpus does half the time."""
    from scales.surface_composer import _thicken_bass_foundation

    high = ["D3", "A3", "D4", "F3", "A3", "D4", "G3", "A3", "D4", "F3", "A3", "D4"]
    layer = _bass_line(high)
    _thicken_bass_foundation(layer, "D minor", share=0.4)
    by_instant: dict = {}
    for e in layer.bass_foundation:
        by_instant.setdefault((e.bar, e.beat), []).append(pitch_to_midi(e.pitch))
    intervals = [max(v) - min(v) for v in by_instant.values() if len(v) > 1]
    assert intervals, "nothing was thickened"
    assert min(intervals) <= 4, f"no third taken up here: {intervals}"


def test_thickening_adds_no_counterpoint_faults_of_its_own():
    """The A/B that caught the muddy intervals: the same phrase, thickened and
    not, must not differ in what the counterpoint checker finds."""
    from scales.counterpoint import analyze_counterpoint
    from scales.surface_composer import _thicken_bass_foundation

    def _kinds(share):
        layer = _bass_line(["D2", "A2", "D3", "F2", "A2", "D3", "G2", "A2", "D3", "F2", "A2", "D3"])
        layer.principal_line = [
            LayerEvent(bar=1 + i // 4, beat=1.0 + (i % 4), pitch=p, duration="q", role="structural")
            for i, p in enumerate(_TUNE)
        ]
        _thicken_bass_foundation(layer, "D minor", share=share)
        report = analyze_counterpoint(layer)
        data = report.as_dict() if hasattr(report, "as_dict") else report
        return {f.get("kind") for f in (data.get("findings") or [])}

    assert not (_kinds(0.4) - _kinds(0.0)), (
        f"thickening introduced {_kinds(0.4) - _kinds(0.0)}"
    )


# ─── each pass applies the RIGHT NUMBER of times ─────────────────────────────
#
# "Does it happen" and "does it happen once" are different questions. Every pass
# here was tested for the first and none for the second, and the melody pass was
# thickening a note even when asked for a share of zero.


def _full_layer():
    layer = _bass_line(
        ["D3", "A2", "D3", "F3", "A2", "D3", "G2", "A2", "D3", "F3", "A2", "D3"]
    )
    layer.principal_line = [
        LayerEvent(
            bar=1 + i // 4,
            beat=1.0 + (i % 4),
            pitch=p,
            duration="q",
            role="structural" if i % 4 == 0 else "passing",
        )
        for i, p in enumerate(_TUNE)
    ]
    return layer


def test_every_pass_is_inert_at_a_share_of_zero():
    from scales.surface_composer import _hold_over_barline, _thicken_bass_foundation

    for pass_fn, args in (
        (_thicken_principal_line, ("D minor",)),
        (_thicken_bass_foundation, ("D minor",)),
    ):
        layer = _full_layer()
        before = (len(layer.principal_line), len(layer.bass_foundation))
        assert pass_fn(layer, *args, share=0.0) == 0, f"{pass_fn.__name__} fired at share 0"
        assert (len(layer.principal_line), len(layer.bass_foundation)) == before

    layer = _full_layer()
    before = [(e.bar, e.beat, e.tie) for e in layer.principal_line]
    assert _hold_over_barline(layer, (4, 4), share=0.0) == 0
    assert [(e.bar, e.beat, e.tie) for e in layer.principal_line] == before


def test_no_pass_exceeds_its_budget():
    from scales.surface_composer import _thicken_bass_foundation

    for share in (0.1, 0.25, 0.5):
        layer = _full_layer()
        budget = max(1, round(len(layer.principal_line) * share))
        assert _thicken_principal_line(layer, "D minor", share=share) <= budget
        layer = _full_layer()
        budget = max(1, round(len(layer.bass_foundation) * share))
        assert _thicken_bass_foundation(layer, "D minor", share=share) <= budget


def test_shaping_a_cadence_twice_changes_nothing_the_second_time():
    """A revision loop runs these again. A pass that is not idempotent
    compounds — which is how a section went from 7 dynamics to 9."""
    from scales.surface_composer import _shape_the_cadence

    layer = _full_layer()
    last_bar = max(e.bar for e in layer.principal_line)
    assert _shape_the_cadence(layer, (4, 4), "PAC", last_bar) is True
    after_first = [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line]
    assert _shape_the_cadence(layer, (4, 4), "PAC", last_bar) is False
    assert [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line] == after_first


def test_thickening_twice_does_not_double_the_chords():
    from scales.surface_composer import _thicken_bass_foundation

    layer = _full_layer()
    _thicken_principal_line(layer, "D minor", share=0.25)
    _thicken_bass_foundation(layer, "D minor", share=0.25)
    after_first = (len(layer.principal_line), len(layer.bass_foundation))
    _thicken_principal_line(layer, "D minor", share=0.25)
    _thicken_bass_foundation(layer, "D minor", share=0.25)
    assert (len(layer.principal_line), len(layer.bass_foundation)) == after_first, (
        "a second pass thickened instants that already carried a chord"
    )


def test_holding_over_the_barline_is_idempotent_in_state_and_in_count():
    """The state was already idempotent and the COUNT was not: nothing filtered
    pairs that were already tied, so a second call re-selected the same pair,
    re-set the same two fields, and returned 1 — reporting work it had not done.
    A pass that lies about how much it did misleads everything downstream that
    trusts the number."""
    from scales.surface_composer import _hold_over_barline

    layer = LayerIR(
        phrase_id="p", instrumentation="solo_piano", key="D minor", meter=(4, 4), bar_count=6
    )
    tune = ["D5", "E5", "F5", "G5"] * 6
    layer.principal_line = [
        LayerEvent(
            bar=1 + i // 4,
            beat=1.0 + (i % 4),
            pitch=p,
            duration="q",
            role="structural" if i == 0 else "passing",
        )
        for i, p in enumerate(tune)
    ]
    counts = [_hold_over_barline(layer, (4, 4), share=0.2) for _ in range(4)]
    assert counts[0] > 0, "nothing was tied at all"
    assert counts[1:] == [0, 0, 0], f"a later call claimed new work: {counts}"
    starts = sum(1 for e in layer.principal_line if e.tie == "start")
    assert starts == counts[0], f"{starts} ties in the score against {counts[0]} reported"


# ─── how often to hold over a barline is the composer's own rate ─────────────


def test_the_tie_rate_is_measured_per_composer_not_fixed():
    """Real practice varies eightfold — Haydn 0.015 ties per bar, Mozart 0.070,
    Beethoven 0.134, Palestrina 0.192. A fixed 0.09 tied Haydn at eight times
    his own rate and Chopin at three times his."""
    from scales.composition_brief import tie_rate_per_bar

    rates = {c: tie_rate_per_bar(c) for c in ("haydn", "mozart", "beethoven", "palestrina")}
    measured = {c: r for c, r in rates.items() if r is not None}
    if len(measured) < 3:
        pytest.skip("corpus not present")
    assert measured["haydn"] < measured["mozart"] < measured["beethoven"]
    assert max(measured.values()) / min(measured.values()) > 3


def test_a_composer_whose_sources_carry_no_ties_returns_none_not_zero():
    """Schubert, Liszt and Brahms all read 0.000 across thousands of bars —
    their editions carry no ties at all. Returning 0.0 would tell a composer to
    write a Schubert impromptu with nothing held anywhere; the honest answer is
    'cannot say', and the caller then uses the generic rate."""
    from scales.composition_brief import tie_rate_per_bar

    for composer in ("schubert", "liszt", "brahms"):
        assert tie_rate_per_bar(composer) is None


def test_an_unknown_composer_cannot_be_measured():
    from scales.composition_brief import tie_rate_per_bar

    assert tie_rate_per_bar("nobody_at_all") is None


def test_the_quota_tracks_the_rate_across_a_piece_rather_than_flooring_per_phrase():
    """`max(1, round(bars * share))` guaranteed one tie per phrase whatever the
    rate, so the composer-relative rate changed nothing at all: nine phrases
    meant nine ties for Haydn and for Beethoven alike."""
    from scales.surface_composer import _hold_over_barline

    def _piece(share, first_bar, n_bars=4):
        layer = LayerIR(
            phrase_id="p",
            instrumentation="solo_piano",
            key="D minor",
            meter=(4, 4),
            bar_count=n_bars,
        )
        tune = ["D5", "E5", "F5", "G5"] * n_bars
        layer.principal_line = [
            LayerEvent(
                bar=first_bar + i // 4,
                beat=1.0 + (i % 4),
                pitch=p,
                duration="q",
                role="structural" if i == 0 else "passing",
            )
            for i, p in enumerate(tune)
        ]
        return layer

    # A rate of 0.015 over four bars must not force a tie the way the old floor did.
    assert _hold_over_barline(_piece(0.015, 1), (4, 4), share=0.015) == 0
    # A high rate over the same span does earn several.
    assert _hold_over_barline(_piece(0.5, 1), (4, 4), share=0.5) >= 1


def test_the_bass_thickening_targets_the_median_movement():
    """A first attempt targeted `voicing_profile`'s pooled share and I reverted
    it as a regression. That figure was measured from the first 4,000 bars of
    each composer — a quarter of Beethoven, chosen by filename — so Chopin's
    real pooled share is 0.380 and not the 0.292 I aimed at. The pooled figure
    is also the wrong question: an aggregate over bars does not describe a
    piece. Chopin's median movement chords 53.9% of its left-hand attacks;
    Haydn's chords 1.3%."""
    from scales.composition_brief import movement_rate_range

    chopin = movement_rate_range("chopin", "lh_chord_share")
    haydn = movement_rate_range("haydn", "lh_chord_share")
    if not chopin or not haydn:
        pytest.skip("corpus not present")
    assert chopin["median"] > 0.4
    assert haydn["median"] < 0.1
    assert chopin["median"] > haydn["median"] * 10, (
        "a single rate cannot serve two composers this far apart"
    )


def test_an_unmeasurable_composer_keeps_the_default_share():
    """`movement_rate_range` returns None below four movements, and the pass
    must then fall back rather than treat None as zero."""
    from scales.surface_composer import _thicken_bass_foundation

    layer = _bass_line(
        ["D3", "A2", "D3", "F3", "A2", "D3", "G2", "A2", "D3", "F3", "A2", "D3"]
    )
    assert _thicken_bass_foundation(layer, "D minor", composer="nobody_at_all") > 0


# ─── melody chord share belongs to the RH texture ────────────────────────────


def test_only_a_chordal_bar_is_thickened():
    """Melody chord share belongs to the RH TEXTURE, as the left hand's belongs
    to its accompaniment idiom. Measured per bar over five composers: a
    `chordal` bar has a median share of 100% and 70% of them are chords all the
    way through, while `singing_melody`, `scalar_run`, `zigzag_figuration` and
    `held_note` all have a median of 0%. A flat share put chords in 25% of our
    singing-melody bars, where real music puts none in 90% of them."""
    layer = _line(_TUNE)
    for e in layer.principal_line:
        e.bar = 1 + (e.bar - 1)
    textures = {1: "singing_melody", 2: "chordal", 3: "singing_melody"}
    added = _thicken_principal_line(layer, "D minor", bar_textures=textures)
    assert added > 0
    by_bar: dict = {}
    for e in layer.principal_line:
        by_bar.setdefault(e.bar, []).append(e)
    for bar, events in by_bar.items():
        instants: dict = {}
        for e in events:
            instants.setdefault(round(float(e.beat), 4), 0)
            instants[round(float(e.beat), 4)] += 1
        thick = sum(1 for n in instants.values() if n > 1)
        if textures.get(bar) == "chordal":
            assert thick == len(instants), f"bar {bar} is chordal and only {thick} attacks are chords"
        else:
            assert thick == 0, f"bar {bar} is {textures.get(bar)} and carries {thick} chords"


def test_a_phrase_with_no_chordal_bar_is_left_alone():
    layer = _line(_TUNE)
    report: dict = {}
    assert _thicken_principal_line(
        layer, "D minor", bar_textures={1: "singing_melody", 2: "scalar_run"}, report=report
    ) == 0
    assert report.get("reason"), "an idle pass must say why"


def test_without_a_texture_map_the_old_sampling_still_applies():
    """The texture-free path is what a caller with no plan gets, and it must
    keep working rather than silently doing nothing."""
    layer = _line(_TUNE)
    assert _thicken_principal_line(layer, "D minor", share=0.25) > 0
