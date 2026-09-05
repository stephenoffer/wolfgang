"""A sung line has a range, and nothing was checking it.

`validate_range` looks its bounds up by the PIECE's instrumentation — "choir",
"ensemble", "orchestra" — and none of those is a key in `INSTRUMENT_RANGES`. So
every non-keyboard piece fell through to the piano's 21-108 and was clamped to it
again by `constraints.piano_low/high`. The table holds real bounds for soprano,
alto, tenor and bass (and 39 more), and no ensemble piece could reach any of
them: the check ran on every commit and could not have reported a soprano
written at C7. That is [[feedback_a_missed_lookup_is_silent]] — the check was
live, and unable to report.
"""

from __future__ import annotations

from scales.models import VOCAL_RANGES, LayerEvent, LayerIR, is_vocal
from scales.validator import validate_layer_ir


def _voice(instrumentation: str, pitches: list[str]) -> LayerIR:
    layer = LayerIR(instrumentation=instrumentation)
    layer.principal_line = [
        LayerEvent(bar=1, beat=float(i), pitch=p, duration=1.0, role="structural")
        for i, p in enumerate(pitches)
    ]
    layer.bass_foundation = [
        LayerEvent(bar=1, beat=0.0, pitch="C3", duration=4.0, role="structural")
    ]
    return layer


def _range_errors(layer: LayerIR):
    report = validate_layer_ir(layer)
    return [i for i in report.issues if i.category == "range" and i.severity == "error"]


def test_a_soprano_cannot_be_written_at_c7():
    assert _range_errors(_voice("choir", ["C7"]))


def test_a_soprano_cannot_be_written_at_c2():
    assert _range_errors(_voice("choir", ["C2"]))


def test_the_spellings_a_graph_actually_carries_all_resolve():
    """The playability check next door was a whitelist of two spellings while the
    graphs on disk carried four, so half the pieces got no check at all. Every
    phrasing a contract has actually used must reach this one."""
    for spelling in (
        "choir",
        "satb choir",
        "SATB",
        "a_cappella choir",
        "a sacred motet for four voices",
        "madrigal for five voices",
        "mass in B minor",
    ):
        assert is_vocal(spelling), spelling
        assert _range_errors(_voice(spelling, ["C7"])), spelling


def test_chorale_is_left_alone_because_the_word_is_ambiguous():
    """A chorale is sung; a chorale PRELUDE is for organ. The word cannot tell
    them apart, so it names neither — guessing "sung" would hand an organ work a
    singer's range and take away its hand-span check."""
    assert not is_vocal("chorale")
    assert not is_vocal("chorale prelude for organ")


def test_it_does_not_fire_on_music_that_is_played():
    """A pianist's right hand reaches C7, and a violin goes higher. Only a part
    that is SUNG gets a singer's bounds."""
    for spelling in ("solo_piano", "piano", "string quartet", "orchestra", ""):
        assert not _range_errors(_voice(spelling, ["C7"])), spelling


def test_the_bounds_clear_what_real_singers_actually_sing():
    """Falsified against the union of 60 Bach chorales, 40 Palestrina works and
    25 Monteverdi works. The measured extremes, which must all pass:

        soprano  Bach 60-81   Palestrina 55-79
        alto     Bach 55-74   Palestrina 50-74   Monteverdi 45-77
        tenor    Bach 49-69   Palestrina 48-69   Monteverdi 48-70
        bass     Bach 36-62   Palestrina 41-64   Monteverdi 41-65

    A narrower bound is not "stricter", it is wrong: the textbook alto figure of
    53 rejects 6.2% of real Monteverdi alto notes.
    """
    measured = {
        "soprano": (55, 81),
        "alto": (45, 77),
        "tenor": (48, 70),
        "bass": (36, 65),
    }
    for voice, (low, high) in measured.items():
        bound_low, bound_high = VOCAL_RANGES[voice]
        assert bound_low <= low, f"{voice} floor {bound_low} rejects real music at {low}"
        assert bound_high >= high, f"{voice} ceiling {bound_high} rejects real music at {high}"


def test_a_palestrina_cantus_low_note_is_not_an_error():
    """Real Palestrina cantus reaches G3, five semitones below where a Bach
    soprano starts. Judging one repertoire by the other's extremes is how I
    first mis-diagnosed the generated motet as out of range."""
    assert not _range_errors(_voice("a sacred motet for four voices", ["G3", "A5"]))


def test_the_bass_part_gets_the_bass_line():
    """SATB closed score writes the lower staff as `tenor // bass` — upper voice
    first — which is the opposite of the piano convention `bass_foundation` was
    built for (sustained pedal note first, figuration second). Taking the written
    order put the tenor in `bass_foundation` and the bass in `response_layer`,
    and since the ensemble path names one staff per layer, the part engraved as
    **Bass** sang the tenor line and **Tenor** sang the bass. Soprano and Alto
    were unaffected, which is exactly why it read as plausible.
    """
    from collections import defaultdict

    from scales.direct_compose import compose_phrase
    from scales.music_io import layer_ir_to_event_ir

    bars = [
        {
            "rh": "C5q B4q A4q G4q // E4q D4q C4q B3q",
            "lh": "G3q G3q F3q G3q // C3q G2q F2q G2q",
        }
    ]
    layer = compose_phrase(bars, key="C", meter=(4, 4), instrumentation="satb choir")
    by_staff = defaultdict(list)
    for event in layer_ir_to_event_ir(layer):
        by_staff[event.staff].append(event.pitch)

    from scales.pitch import pitch_to_midi

    bass = [pitch_to_midi(p) for p in by_staff["bass"]]
    tenor = [pitch_to_midi(p) for p in by_staff["response"]]
    assert bass and tenor
    assert max(bass) < min(tenor), (
        f"the Bass part {by_staff['bass']} sits above the Tenor {by_staff['response']}"
    )


def test_a_string_quartets_cello_gets_the_cello_line():
    """The same convention, and the fix for it was first gated to VOCAL scores —
    too narrow. A quartet written `viola // cello` came out with the viola part
    labelled Violoncello and playing 40-59, below the viola's lowest string
    (C3 = 48). Every closed-score ensemble writes the lower staff's upper voice
    first; the keyboard is the exception.
    """
    from collections import defaultdict

    from scales.direct_compose import compose_phrase
    from scales.music_io import layer_ir_to_event_ir
    from scales.pitch import pitch_to_midi

    bars = [
        {
            "rh": "D5q G5e F#5e G5e A5e // B4q D5e B4e D5e B4e",
            "lh": "G4q G4e G4e G4e G4e // G3q D3q B2q",
        }
    ]
    for instrumentation in ("string quartet", "orchestra", "satb choir"):
        layer = compose_phrase(bars, key="G", meter=(3, 4), instrumentation=instrumentation)
        by_staff = defaultdict(list)
        for event in layer_ir_to_event_ir(layer):
            by_staff[event.staff].append(event.pitch)
        low = [pitch_to_midi(p) for p in by_staff["bass"]]
        inner = [pitch_to_midi(p) for p in by_staff["response"]]
        assert low and inner
        assert max(low) < min(inner), (
            f"{instrumentation}: the bass part {by_staff['bass']} sits above the "
            f"inner voice {by_staff['response']}"
        )


def test_a_pianists_left_hand_keeps_its_written_order():
    """The pedal-under-figuration split depends on the first written voice being
    the sustained bass. Only sung parts are reordered by pitch."""
    from scales.direct_compose import compose_phrase

    bars = [{"rh": "C5q", "lh": "C2w // E3e G3e C4e G3e"}]
    layer = compose_phrase(bars, key="C", meter=(4, 4), instrumentation="solo_piano")
    assert [e.pitch for e in layer.bass_foundation] == ["C2"]


def test_a_string_quartet_is_not_a_mixed_chamber_group():
    """With no roles table of its own, a string quartet's abstract layer names
    resolved through `_LAYER_INSTRUMENTS`: melody became a Violin, but
    counter_reply became a CLARINET and response a BASSOON. "A quartet in
    Haydn's style" — written from a corpus that IS string quartets — came out
    scored for violin, clarinet, bassoon and cello, with the parts named
    "Melody", "Counter Reply", "Response", "Bass".
    """
    from scales.assembler import _instrument_for, string_part_name

    expected = {
        "melody": ("Violin", "Violin I"),
        "counter_reply": ("Violin", "Violin II"),
        "response": ("Viola", "Viola"),
        "bass": ("Violoncello", "Violoncello"),
    }
    for staff, (instrument_name, part_name) in expected.items():
        got = _instrument_for(staff, strings=True)
        assert (getattr(got, "instrumentName", None) or type(got).__name__) == instrument_name
        assert string_part_name(staff) == part_name


def test_only_a_named_string_ensemble_gets_strings():
    """"quartet" alone will not do: a quartet can be winds, brass or voices, and
    guessing strings would hand a wind quartet a viola."""
    from scales.models import is_string_ensemble

    for yes in ("string quartet", "strings", "string orchestra", "a string quintet"):
        assert is_string_ensemble(yes), yes
    for no in ("quartet", "wind quartet", "satb choir", "solo piano", "orchestra", ""):
        assert not is_string_ensemble(no), no


def test_a_real_instrument_name_still_wins_over_the_roles_table():
    """A cantata genuinely has an orchestra in it, and an orchestration plan
    spells its staves 'flute', 'violin_1', 'timpani'."""
    from scales.assembler import _instrument_for

    for staff, expected in (("flute", "Flute"), ("timpani", "Timpani")):
        for kwargs in ({"strings": True}, {"vocal": True}):
            got = _instrument_for(staff, **kwargs)
            assert (getattr(got, "instrumentName", None) or type(got).__name__) == expected


def test_the_four_voice_example_in_the_craft_doc_produces_satb():
    """`note-writing-craft.md` prints this exact bar as "four-voice writing: S+A
    in the right hand, T+B in the left". Its left hand puts the TENOR first,
    which is the SATB convention — and the convention that used to land the tenor
    in `bass_foundation` and come out labelled Bass. A documented snippet is a
    promise; this is the promise.
    """
    from collections import defaultdict

    from scales.direct_compose import compose_phrase
    from scales.music_io import layer_ir_to_event_ir

    bars = [{"rh": "C5h B4h // G4h G4h", "lh": "E3h D3h // C3h G2h"}]
    layer = compose_phrase(bars, key="C", meter=(4, 4), instrumentation="satb choir")
    by_staff = defaultdict(list)
    for event in layer_ir_to_event_ir(layer):
        by_staff[event.staff].append(event.pitch)

    assert by_staff["melody"] == ["C5", "B4"]  # Soprano
    assert by_staff["counter_reply"] == ["G4", "G4"]  # Alto
    assert by_staff["response"] == ["E3", "D3"]  # Tenor
    assert by_staff["bass"] == ["C3", "G2"]  # Bass
