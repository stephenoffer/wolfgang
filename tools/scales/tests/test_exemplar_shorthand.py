"""Tests for _adapted_to_shorthand — the converter that renders real corpus
bars as the exemplar shorthand shown to Claude in briefs. A faithfully-adapted
exemplar must sum to the meter, so grace notes (corpus dur 0.0) must NOT be
rendered as real 32nd notes that overflow the bar.

Run: python3 -m scales.tests.test_exemplar_shorthand
"""

from scales import composition_brief as cb
from scales import direct_compose
from scales.corpus_adapter import AdaptedBar
from scales.duration import dur_to_beats
from scales.validator import validate_layer_ir  # noqa: E402


def test_grace_note_rendered_as_grace_not_32nd():
    # A bar: quarter, GRACE (dur 0.0), then notes filling the remaining 3 beats.
    rh = [
        {"type": "note", "pitch": "C5", "dur": 1.0},
        {"type": "note", "pitch": "D5", "dur": 0.0},  # grace
        {"type": "note", "pitch": "E5", "dur": 1.0},
        {"type": "note", "pitch": "F5", "dur": 1.0},
        {"type": "note", "pitch": "G5", "dur": 1.0},
    ]
    bar = AdaptedBar(rh_events=rh, lh_events=[], target_key="C")
    rh_sh, _ = cb._adapted_to_shorthand(bar)
    assert ":grace" in rh_sh, rh_sh
    assert "D5t" not in rh_sh, f"grace rendered as a 32nd: {rh_sh}"


def test_grace_exemplar_sums_to_meter_through_direct_compose():
    rh = [
        {"type": "note", "pitch": "C5", "dur": 1.0},
        {"type": "note", "pitch": "D5", "dur": 0.0},  # grace — must take no time
        {"type": "note", "pitch": "E5", "dur": 1.0},
        {"type": "note", "pitch": "F5", "dur": 1.0},
        {"type": "note", "pitch": "G5", "dur": 1.0},
    ]
    rh_sh, _ = cb._adapted_to_shorthand(AdaptedBar(rh_events=rh, target_key="C"))
    layer = direct_compose.compose_phrase(
        [{"rh": rh_sh, "lh": ""}], key="C", bar_start=1, phrase_id="t", meter=[4, 4]
    )
    # the non-grace principal events must sum to exactly the bar capacity
    non_grace = sum(
        dur_to_beats(e.duration)
        for e in layer.principal_line
        if e.bar == 1 and e.pitch != "rest" and "grace" not in (e.ornament or "")
    )
    assert abs(non_grace - 4.0) < 1e-6, f"bar sums to {non_grace}, not 4.0"
    rep = validate_layer_ir(layer)
    overflow = [
        i.message for i in rep.issues if "duration sum" in i.message and "principal" in i.message
    ]
    assert not overflow, overflow


def test_ornament_flags_render_in_shorthand():
    # has_trill / has_turn carried through the adapter must surface as
    # parseable suffixes, and must not change the metrical sum.
    rh = [
        {"type": "note", "pitch": "C5", "dur": 1.0, "has_trill": True},
        {"type": "note", "pitch": "D5", "dur": 1.0, "has_turn": True},
        {"type": "note", "pitch": "E5", "dur": 2.0},
    ]
    rh_sh, _ = cb._adapted_to_shorthand(AdaptedBar(rh_events=rh, target_key="C"))
    assert ":tr" in rh_sh, rh_sh
    assert ":turn" in rh_sh, rh_sh
    # ornament suffixes are stripped by the beat counter — bar still sums to 4
    assert cb._shorthand_beats(rh_sh) == 4.0, rh_sh
    # and direct_compose parses the trill/turn back out
    layer = direct_compose.compose_phrase(
        [{"rh": rh_sh, "lh": ""}], key="C", bar_start=1, phrase_id="t", meter=[4, 4]
    )
    orns = {e.ornament for e in layer.principal_line if e.ornament}
    assert "trill" in orns and "turn" in orns, orns


def test_adapter_carries_ornament_metadata():
    from scales.corpus_adapter import CorpusAdapter

    bar = {
        "key": "C",
        "rh_display": [
            {"type": "note", "pitch": "C5", "interval_from_root": 0, "dur": 1.0, "has_trill": True},
            {"type": "note", "pitch": "E5", "interval_from_root": 4, "dur": 1.0, "is_grace": True},
        ],
        "lh_display": [],
    }
    adapted = CorpusAdapter().transpose_bar(bar, "G")
    assert adapted.rh_events[0].get("has_trill") is True, adapted.rh_events
    assert adapted.rh_events[1].get("is_grace") is True, adapted.rh_events


def test_shorthand_beats_and_overflow():
    # grace notes count zero; sparse bars are fine; only >capacity overflows
    assert cb._shorthand_beats("C5q D5q") == 2.0
    assert cb._shorthand_beats("C5q D5s:grace E5q F5q G5q") == 4.0
    assert cb._shorthand_overflows_bar("C5e D5e E5e F5e G5e A5e B5e C6e", 4.0) is False
    assert cb._shorthand_overflows_bar("C5q D5q", 4.0) is False  # sparse OK
    assert (
        cb._shorthand_overflows_bar("rest_dh C4e G3e D4e G3e E4q rest_e rest_e D4e F3e", 4.0)
        is True
    )  # 8.0


def test_retrieved_exemplars_never_overflow():
    """The brief must not show Claude corpus bars that overflow the meter
    (corrupted multi-voice flattens). Skip cleanly if no mozart corpus."""
    from scales.composition_brief import _REFERENCE_INDEX, _has_corpus
    from scales.models import PhraseSlot

    if not _has_corpus(_REFERENCE_INDEX / "mozart"):
        print("  (skipped: no mozart corpus)")
        return

    class _TP:
        def __init__(self, rh, lh):
            self.rh_texture, self.lh_texture = rh, lh

    checked = 0
    for rh, lh in [
        ("singing_melody", "alberti"),
        ("scalar_run", "alberti"),
        ("singing_melody", "block_chord_offbeat"),
    ]:
        tp = _TP(rh, lh)
        slot = PhraseSlot(
            phrase_id="p",
            section_id="s",
            bar_start=1,
            bar_count=4,
            key="C",
            meter=[4, 4],
            texture_plan=[tp, tp, tp, tp],
        )
        for ex in cb._retrieve_exemplars("mozart", slot, 8, []):
            assert not cb._shorthand_overflows_bar(ex.rh, 4.0), ex.rh
            assert not cb._shorthand_overflows_bar(ex.lh, 4.0), ex.lh
            checked += 1
    assert checked > 0, "expected some exemplars to verify"
    print(f"  ({checked} retrieved exemplars all meter-valid)")


if __name__ == "__main__":
    fns = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in fns:
        fn()
        print(f"ok {name}")
    print(f"\n{len(fns)} tests passed")


# ─── Multi-voice bars must be length-checked too ─────────────────────────────


def test_a_two_voice_bar_is_measured_by_its_longest_voice():
    """`//` carries independent voices; each fills the bar on its own.

    `_shorthand_beats` had no case for `//` at all, so the token failed the note
    regex and the function returned `None` — which both callers read as
    "unparseable, don't judge it". Every multi-voice exemplar therefore bypassed
    the malformed-bar filter, and that is most exemplars for exactly the
    composers where it matters most: a Bach sample averages four voices a bar.
    """
    from scales.composition_brief import _shorthand_beats

    assert _shorthand_beats("C5q D5q E5q F5q") == 4.0
    assert _shorthand_beats("C5q D5q E5q F5q // G4q A4q B4q C5q") == 4.0
    # the longest voice defines the bar, not the sum
    assert _shorthand_beats("C5q D5q E5q F5q // G4h") == 4.0


def test_an_overfull_voice_is_caught_inside_a_multi_voice_bar():
    from scales.composition_brief import _shorthand_overflows_bar

    good = "C5q D5q E5q F5q // G4q A4q B4q C5q"
    bad = "C5q D5q E5q F5q // G4q A4q B4q C5q D5q"
    assert not _shorthand_overflows_bar(good, 4.0)
    assert _shorthand_overflows_bar(bad, 4.0), (
        "a voice that runs past the barline must be caught even when it is the "
        "second voice of a `//` pair"
    )


def test_grace_notes_still_take_no_metrical_time():
    from scales.composition_brief import _shorthand_beats

    assert _shorthand_beats("rest_q G4s:grace rest_dh") == 4.0
    assert _shorthand_beats("rest_q G4s:grace rest_dh // C4w") == 4.0


def test_an_unparseable_bar_is_still_never_judged():
    """The `None` path must survive — a bar we cannot read is not a bar we
    know to be wrong."""
    from scales.composition_brief import _shorthand_beats, _shorthand_overflows_bar

    assert _shorthand_beats("!!! not shorthand !!!") is None
    assert not _shorthand_overflows_bar("!!! not shorthand !!!", 4.0)
