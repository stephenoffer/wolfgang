"""Practical instrument ranges, and what a dynamic costs at the extremes.

Audit item E14: `INSTRUMENT_RANGES` has no practical-vs-extreme distinction and
no per-dynamic limits, and the orchestration planner clamped every part to the
outer edge of what an instrument can physically produce.

That is the difference between a part a player can read and one they dread. Every
wind instrument's bottom minor third is unwieldy and its top is effortful; a
flute's low octave will not speak quietly and a trumpet's top cannot be played
pianissimo at all. Clamping an octave transfer to the physical limit lands notes
in exactly those places — legal, and unplayable as written.
"""

import pytest

from scales.models import LayerEvent, LayerIR
from scales.orchestration_planner import (
    _range_of,
    plan_orchestration,
    practical_range,
    range_warnings,
)

# ─── The practical range is inside the physical one ──────────────────────────


@pytest.mark.parametrize(
    "instrument", ["flute", "oboe", "clarinet", "bassoon", "horn", "trumpet", "trombone"]
)
def test_a_winds_practical_range_is_narrower_than_its_physical_one(instrument):
    full_lo, full_hi = _range_of(instrument)
    lo, hi = practical_range(instrument)
    assert full_lo <= lo < hi <= full_hi
    assert (lo, hi) != (full_lo, full_hi), f"{instrument} was not trimmed at all"


def test_strings_keep_almost_all_of_their_range():
    """Strings are far more forgiving than winds; only the very top is awkward."""
    full_lo, full_hi = _range_of("violin")
    lo, hi = practical_range("violin")
    assert lo == full_lo, "a violin's bottom string is perfectly usable"
    assert full_hi - hi <= 8


def test_an_unknown_instrument_gets_no_false_confidence():
    """Guessing a trim for an instrument with no entry is worse than none."""
    assert practical_range("theremin") == _range_of("theremin")


# ─── A soft dynamic narrows it further ───────────────────────────────────────


def test_a_trumpet_cannot_play_softly_at_the_top():
    normal_hi = practical_range("trumpet")[1]
    soft_hi = practical_range("trumpet", "pp")[1]
    assert soft_hi < normal_hi


def test_a_flute_will_not_speak_softly_at_the_bottom():
    normal_lo = practical_range("flute")[0]
    soft_lo = practical_range("flute", "pp")[0]
    assert soft_lo > normal_lo


def test_a_loud_dynamic_does_not_narrow_the_range():
    assert practical_range("trumpet", "ff") == practical_range("trumpet")


def test_a_string_range_is_unaffected_by_dynamic():
    """A violin plays quietly anywhere; the restriction is a wind problem."""
    assert practical_range("violin", "pp") == practical_range("violin")


def test_the_oboe_is_restricted_at_both_ends_when_soft():
    """It honks at the bottom and cannot be played softly at the top."""
    lo, hi = practical_range("oboe")
    soft_lo, soft_hi = practical_range("oboe", "pp")
    assert soft_lo > lo and soft_hi < hi


# ─── Warnings ────────────────────────────────────────────────────────────────


def test_a_note_outside_the_instrument_entirely_is_named_as_such():
    warnings = range_warnings("trumpet", [95])
    assert warnings and "outside the instrument's range entirely" in warnings[0]


def test_a_weak_low_note_is_distinguished_from_an_impossible_one():
    weak = range_warnings("flute", [61])
    impossible = range_warnings("flute", [40])
    assert weak and "outside the instrument's range entirely" not in weak[0]
    assert impossible and "outside the instrument's range entirely" in impossible[0]


def test_the_dynamic_is_named_when_it_is_the_reason():
    warnings = range_warnings("flute", [60], dynamic="pp")
    assert warnings and "will not speak at this dynamic" in warnings[0]

    loud = range_warnings("flute", [60], dynamic="ff")
    assert not loud or "will not speak at this dynamic" not in loud[0]


def test_comfortable_writing_draws_no_warnings():
    assert range_warnings("violin", [60, 67, 72], dynamic="mf") == []
    assert range_warnings("clarinet", [55, 62, 70], dynamic="mf") == []


def test_warnings_are_advisory_not_a_clamp():
    """A shrieking piccolo at a climax is a choice, not a defect."""
    warnings = range_warnings("piccolo", [100], dynamic="ff")
    # It reports; it does not refuse, and nothing here modifies a pitch.
    assert isinstance(warnings, list)


def test_the_range_never_inverts():
    """A trim that would cross itself must fall back, not produce lo > hi."""
    for instrument in ("piccolo", "tuba", "trumpet", "soprano", "bass"):
        for dyn in (None, "pp", "ppp", "ff"):
            lo, hi = practical_range(instrument, dyn)
            assert lo < hi, f"{instrument} at {dyn} inverted: ({lo}, {hi})"


# ─── Every mark reaches the orchestral part ──────────────────────────────────
#
# `_event_dict` listed seven fields by hand and dropped six. The audible
# consequence was worse than a missing mark: an appoggiatura arrived in the
# orchestral score as a plain note, took real time instead of leaning on its
# principal, collided with the note it was decorating, and left the bar summing
# to 3.5 beats of a 3/4. A dropped ornament is a wrong rhythm.


def test_every_notation_field_survives_orchestration():
    from scales.models import LayerEvent
    from scales.orchestration_planner import _event_dict

    e = LayerEvent(
        bar=3,
        beat=2.0,
        pitch="C5",
        duration="e",
        dynamic="p",
        articulation="tenuto",
        slur="start",
        ornament="appoggiatura",
        tie="start",
        hairpin="cresc_start",
        expression="dolce",
        technique="arpeggio",
        pedal="down",
        fingering="3",
    )
    out = _event_dict(e)
    for field in (
        "dynamic",
        "articulation",
        "slur",
        "ornament",
        "tie",
        "hairpin",
        "expression",
        "technique",
        "pedal",
        "fingering",
    ):
        assert out.get(field) is not None, f"{field} was dropped on the way to the part"


def test_the_field_list_is_derived_not_hand_written():
    """A field added to LayerEvent must reach the parts without an edit here."""
    from scales.models import LayerEvent
    from scales.orchestration_planner import _EVENT_CARRIED_FIELDS

    declared = set(LayerEvent.__dataclass_fields__)
    carried = set(_EVENT_CARRIED_FIELDS) | {"bar", "beat", "pitch", "role", "source_layer"}
    assert declared <= carried, f"not carried: {declared - carried}"


def test_a_transposed_pitch_still_carries_its_marks():
    from scales.models import LayerEvent
    from scales.orchestration_planner import _event_dict

    e = LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q", ornament="trill")
    out = _event_dict(e, pitch="C4")
    assert out["pitch"] == "C4"
    assert out["ornament"] == "trill"


# ─── Doubling, not distribution ──────────────────────────────────────────────
#
# A two-part piano core has two populated layers. Assigning them across ten
# instruments leaves eight with nothing, and a score whose named instruments are
# tacet is not an orchestration of the material — it is a distribution of it.
# Measured on a real orchestrated section before this: flute 0, horn 0,
# violin_2 0, clarinet 1, bassoon 1, viola 2, against cello 60 and violin_1 47.


def _two_part_core():
    from scales.models import LayerEvent, LayerIR

    ir = LayerIR(key="F major", meter=(3, 4))
    for b in range(1, 9):
        for i, p in enumerate(["F5", "G5", "A5"]):
            ir.principal_line.append(
                LayerEvent(
                    bar=b,
                    beat=1 + i,
                    pitch=p,
                    duration="q",
                    dynamic=("f" if b == 5 and i == 0 else None),
                )
            )
        ir.bass_foundation.append(LayerEvent(bar=b, beat=1.0, pitch="F2", duration="dh"))
    return ir


_ENSEMBLE = [
    "flute",
    "oboe",
    "clarinet",
    "bassoon",
    "horn",
    "trumpet",
    "violin_1",
    "violin_2",
    "viola",
    "cello",
]


def test_no_named_instrument_is_left_tacet():
    from scales.orchestration_planner import plan_orchestration

    parts = plan_orchestration(_two_part_core(), _ENSEMBLE, key="F major")
    silent = [k for k in _ENSEMBLE if not parts.get(k)]
    assert not silent, f"these named instruments got nothing to play: {silent}"


def test_a_doubling_is_diatonic():
    """A sixth below F in F major is A-flat — a wrong note in every bar."""
    from scales.orchestration_planner import plan_orchestration

    parts = plan_orchestration(_two_part_core(), _ENSEMBLE, key="F major")
    f_major = {"F", "G", "A", "B-", "Bb", "C", "D", "E"}
    for event in parts["violin_2"]:
        pitches = event["pitch"] if isinstance(event["pitch"], list) else [event["pitch"]]
        for p in pitches:
            name = p[:-1]
            assert name in f_major, f"violin_2 plays {p}, which is not in F major"


def test_the_orchestration_passes_its_own_range_audit():
    from scales.orchestration_planner import audit_orchestration, plan_orchestration

    parts = plan_orchestration(_two_part_core(), _ENSEMBLE, key="F major")
    assert audit_orchestration(parts) == []


def test_the_flute_octave_is_skipped_rather_than_clamped():
    """Clamping a climax octave into the top of the flute is a shriek, not a
    brightening — and this module's own audit flags it."""
    from scales.orchestration_planner import plan_orchestration
    from scales.pitch import pitch_to_midi

    parts = plan_orchestration(_two_part_core(), _ENSEMBLE, key="F major")
    hi = practical_range("flute", "f")[1]
    for event in parts["flute"]:
        p = event["pitch"] if not isinstance(event["pitch"], list) else event["pitch"][-1]
        assert pitch_to_midi(p) <= hi


def test_a_rich_core_is_not_given_redundant_doublings():
    """Doublings fill silence; they must not pile onto a full texture."""
    from scales.models import LayerEvent, LayerIR
    from scales.orchestration_planner import plan_orchestration

    ir = LayerIR(key="C major", meter=(4, 4))
    for b in range(1, 5):
        for i in range(4):
            ir.principal_line.append(LayerEvent(bar=b, beat=1 + i, pitch="C5", duration="q"))
            ir.response_layer.append(LayerEvent(bar=b, beat=1 + i, pitch="E4", duration="q"))
            ir.counter_reply.append(LayerEvent(bar=b, beat=1 + i, pitch="G4", duration="q"))
        ir.bass_foundation.append(LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w"))
    parts = plan_orchestration(ir, _ENSEMBLE, key="C major")
    assert not [k for k in _ENSEMBLE if not parts.get(k)]


def test_the_bass_anchor_sustains_under_moving_inner_parts():
    """A piano-core left hand is split — first event per bar anchors the bass,
    the rest becomes inner motion — but the anchor kept its ORIGINAL value. In a
    bar whose left hand read `C3q C3q C2e C3e C2e C3e`, the cello was given one
    quarter note and three beats of silence while every other part moved. An
    orchestral bass sustains or repeats; it does not blip once and vanish.
    """
    from scales.models import LayerEvent, LayerIR
    from scales.orchestration_planner import plan_orchestration

    lh = []
    for bar in (1, 2, 3, 4):
        for i, beat in enumerate((1.0, 2.0, 3.0, 4.0)):
            lh.append(
                LayerEvent(
                    bar=bar,
                    beat=beat,
                    pitch="C3" if i else "C2",
                    duration="q",
                    role="bass_foundation",
                )
            )
    rh = [
        LayerEvent(bar=bar, beat=b, pitch="G4", duration="q", role="principal_line")
        for bar in (1, 2, 3, 4)
        for b in (1.0, 2.0, 3.0, 4.0)
    ]
    layer = LayerIR(
        phrase_id="p",
        principal_line=rh,
        bass_foundation=lh,
        key="C minor",
        meter=(4, 4),
        bar_count=4,
    )
    parts = plan_orchestration(layer, ["cello", "violin_1", "viola"])
    cello = parts.get("cello") or []
    assert cello, "the cello must receive the bass line"

    from scales.duration import dur_to_beats

    by_bar = {}
    for e in cello:
        pitch = e.get("pitch") if isinstance(e, dict) else getattr(e, "pitch", None)
        if pitch == "rest":
            continue
        bar = e.get("bar") if isinstance(e, dict) else getattr(e, "bar", None)
        dur = e.get("duration") if isinstance(e, dict) else getattr(e, "duration", None)
        by_bar.setdefault(bar, 0.0)
        by_bar[bar] += float(dur_to_beats(dur))
    assert by_bar, "the cello part carries no sounding notes"
    for bar, held in by_bar.items():
        assert held >= 3.0, f"bar {bar}: cello sounds for only {held} of 4 beats"


# ─── Nearly-empty is not the same as empty ───────────────────────────────────


def _core(inner_bars, bars=14):
    """A two-part piano core with inner motion in only the named bars."""
    ir = LayerIR(key="C minor", meter=(4, 4), instrumentation="solo_piano", bar_count=bars)
    for b in range(1, bars + 1):
        for i, p in enumerate(["C5", "Eb5", "G5", "F5"]):
            ir.principal_line.append(LayerEvent(bar=b, beat=1.0 + i, pitch=p, duration="q"))
        ir.bass_foundation.append(LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w"))
    for b in inner_bars:
        for i, p in enumerate(["Eb3", "G3", "Bb3"]):
            ir.response_layer.append(LayerEvent(bar=b, beat=1.0 + i, pitch=p, duration="q"))
    return ir


_ENS = ["violin_i", "violin_ii", "viola", "cello", "flute", "oboe", "clarinet", "bassoon", "horn"]


def _bars_played(parts, name):
    events = parts.get(name) or []
    return len({e["bar"] if isinstance(e, dict) else e.bar for e in events})


@pytest.mark.parametrize(
    "label,inner",
    [("one bar of fourteen", [13]), ("none at all", []), ("throughout", list(range(1, 15)))],
)
def test_no_instrument_is_left_effectively_tacet(label, inner):
    """The wind pads and the inner strings both fell back only when their
    source layer was ENTIRELY empty.

    A core with a LITTLE inner motion — three events, all in one bar of
    fourteen — is not empty, so neither fallback fired: clarinet, bassoon and
    viola each came out with exactly ONE note in the whole section. Nearly-empty
    reached the same tacet outcome as empty, through the guard rather than
    around it.

    Deciding per bar needs no coverage threshold, which is the better reason for
    it: a real orchestrator voices the harmony each bar implies, from whichever
    line implies it.
    """
    parts = plan_orchestration(_core(inner), _ENS, key="C minor")
    silent = [name for name in _ENS if name in parts and _bars_played(parts, name) <= 2]
    assert not silent, f"with inner motion {label}, these are effectively tacet: {silent}"


def test_the_pads_cover_the_whole_section_when_inner_motion_is_sparse():
    """The measured case: 1 bar of 14 -> 14 of 14."""
    parts = plan_orchestration(_core([13]), _ENS, key="C minor")
    for wind in ("clarinet", "bassoon", "horn"):
        assert _bars_played(parts, wind) >= 13, f"{wind} pads only {_bars_played(parts, wind)} bars"


def test_real_inner_motion_is_still_preferred_over_the_fallback():
    """The fallback must fill gaps, not replace the written inner line."""
    parts = plan_orchestration(_core(list(range(1, 15))), _ENS, key="C minor")
    dense = parts.get("violin_ii") or parts.get("viola") or []
    assert len(dense) >= 14, "the written inner motion was thrown away"
