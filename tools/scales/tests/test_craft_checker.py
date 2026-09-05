"""The phrase-sanctity checklist, and the four checks that failed real music.

Measured over 126 real 8-bar phrases (Mozart, Beethoven, Chopin), the checklist
passed:

| check | before | after |
|---|---|---|
| `has_memorable_detail` | **0%** | 99.2% |
| `accompaniment_responds_to_melody` | 31.0% | 100% |
| `harmony_is_voiced` | 55.6% | 97.6% |
| `entry_exit_earned` | 75.4% | 100% |

Three of the four were reading the *layer a note was filed under* rather than
the music — the same fault as the phantom bass line, where a statistic taken off
a broken layer was mistaken for evidence about the notes. A plain single-stream
left hand goes entirely to ``bass_foundation``, so every check keyed on
``response_layer`` was blind for most real writing. The fourth indexed the
melody in list order rather than time order and demanded that the phrase's last
event be a note, when lifting into a rest is how a phrase breathes.

A checklist no canonical music can satisfy does not raise standards; it teaches
the composer to write toward whatever artefact the check is actually measuring.
"""

import pytest

from scales.craft_checker import CraftChecker, check_phrase, craft_findings, craft_score
from scales.models import LayerEvent, LayerIR


def _ev(bar, beat, pitch, dur="q", **kw):
    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _decent_phrase():
    """Melody over a chordal accompaniment, varied rhythm, a rest, a leap."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=4)
    tune = [
        ("C5", "q"),
        ("E5", "e"),
        ("G5", "e"),
        ("C6", "h"),
        ("B5", "q"),
        ("A5", "q"),
        ("G5", "h"),
        ("F5", "e"),
        ("E5", "e"),
        ("D5", "q"),
        ("rest", "h"),
        ("E5", "q"),
        ("D5", "q"),
        ("C5", "h"),
    ]
    bar, beat = 1, 1.0
    for pitch, dur in tune:
        ir.principal_line.append(_ev(bar, beat, pitch, dur))
        beat += {"q": 1.0, "e": 0.5, "h": 2.0}[dur]
        while beat > 4.0:
            beat -= 4.0
            bar += 1
    for b in range(1, 5):
        ir.bass_foundation.append(_ev(b, 1.0, "C3", "q"))
        for i in (2, 3, 4):
            ir.bass_foundation.append(_ev(b, float(i), ["E3", "G3"], "q"))
    return ir


def _empty_phrase():
    """One repeated note, no accompaniment — the thing the checklist is for."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=4)
    for b in range(1, 5):
        for i in range(4):
            ir.principal_line.append(_ev(b, 1 + i, "C5"))
    return ir


# ─── The four rewritten checks ───────────────────────────────────────────────


def test_harmony_counts_notes_that_sound_not_the_layer_they_are_filed_in():
    """Chords in `bass_foundation` are voiced harmony; the old check said no."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [_ev(1, 1.0, "C5", "w"), _ev(2, 1.0, "E5", "w")]
    ir.bass_foundation = [
        _ev(1, 1.0, ["C3", "E3", "G3"], "w"),
        _ev(2, 1.0, ["C3", "E3", "G3"], "w"),
    ]
    assert ir.response_layer == [], "the fixture must not use response_layer"
    assert CraftChecker().check(ir).harmony_is_voiced


def test_a_bare_two_part_texture_is_not_voiced_harmony():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [_ev(1, 1.0, "C5", "w"), _ev(2, 1.0, "E5", "w")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "w"), _ev(2, 1.0, "G2", "w")]
    assert not CraftChecker().check(ir).harmony_is_voiced


def test_an_accompaniment_in_the_bass_layer_counts_as_an_accompaniment():
    ir = _decent_phrase()
    assert ir.response_layer == []
    assert CraftChecker().check(ir).accompaniment_responds_to_melody


def test_one_bass_note_per_bar_is_not_an_accompaniment():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=4)
    ir.principal_line = [_ev(b, 1.0, "C5", "w") for b in range(1, 5)]
    ir.bass_foundation = [_ev(b, 1.0, "C3", "w") for b in range(1, 5)]
    assert not CraftChecker().check(ir).accompaniment_responds_to_melody


def test_a_phrase_that_lifts_into_a_rest_has_still_ended():
    ir = _decent_phrase()
    ir.principal_line.append(_ev(4, 4.0, "rest", "q"))
    assert CraftChecker().check(ir).entry_exit_earned


def test_entry_and_exit_are_read_in_time_order_not_list_order():
    """Unsorted material made the old check test two arbitrary events."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [
        _ev(2, 1.0, "E5", "w"),  # deliberately out of order
        _ev(1, 1.0, "C5", "w"),
    ]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "w")]
    assert CraftChecker().check(ir).entry_exit_earned


def test_a_phrase_that_starts_with_silence_has_no_entry():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [
        _ev(1, 1.0, "rest", "q"),
        _ev(1, 2.0, "rest", "q"),
        _ev(1, 3.0, "rest", "q"),
        _ev(1, 4.0, "rest", "q"),
        _ev(2, 1.0, "C5", "w"),
    ]
    assert not CraftChecker().check(ir).entry_exit_earned


def test_an_anacrusis_still_counts_as_an_entry():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [_ev(1, 4.0, "G4", "q"), _ev(2, 1.0, "C5", "w")]
    assert CraftChecker().check(ir).entry_exit_earned


# ─── Memorable detail: the check no real phrase could pass ───────────────────


def test_an_expressive_leap_is_a_memorable_detail():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=1)
    ir.principal_line = [_ev(1, 1.0, "C5"), _ev(1, 2.0, "A5"), _ev(1, 3.0, "G5", "h")]
    assert CraftChecker().check(ir).has_memorable_detail


def test_an_arrival_note_is_a_memorable_detail():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=2)
    ir.principal_line = [
        _ev(1, 1.0, "C5", "e"),
        _ev(1, 1.5, "D5", "e"),
        _ev(1, 2.0, "E5", "e"),
        _ev(1, 2.5, "F5", "e"),
        _ev(1, 3.0, "G5", "w"),  # twice the phrase's usual value
    ]
    assert CraftChecker().check(ir).has_memorable_detail


def test_an_ornament_anywhere_in_the_texture_counts():
    """The old check looked only at a layer nothing populates."""
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=1)
    ir.principal_line = [_ev(1, 1.0, "C5"), _ev(1, 2.0, "D5"), _ev(1, 3.0, "E5")]
    ir.bass_foundation = [_ev(1, 1.0, "C3", "h", ornament="trill")]
    assert CraftChecker().check(ir).has_memorable_detail


def test_an_interior_silence_counts():
    ir = LayerIR(key="C major", meter=(4, 4), bar_count=1)
    ir.principal_line = [
        _ev(1, 1.0, "C5"),
        _ev(1, 2.0, "rest"),
        _ev(1, 3.0, "D5"),
        _ev(1, 4.0, "E5"),
    ]
    assert CraftChecker().check(ir).has_memorable_detail


def test_a_featureless_phrase_has_no_memorable_detail():
    assert not CraftChecker().check(_empty_phrase()).has_memorable_detail


# ─── It still discriminates ──────────────────────────────────────────────────


def test_a_decent_phrase_passes_the_whole_checklist():
    chk = CraftChecker().check(_decent_phrase())
    failed = [k for k, v in vars(chk).items() if isinstance(v, bool) and not v]
    assert not failed, f"a well-written phrase failed: {failed}"


def test_an_empty_phrase_fails_most_of_the_checklist():
    """Loosening the checks must not make them pass everything."""
    chk = CraftChecker().check(_empty_phrase())
    failed = [k for k, v in vars(chk).items() if isinstance(v, bool) and not v]
    assert len(failed) >= 5, f"only {failed} failed on a one-note phrase"


def test_an_empty_layer_ir_is_safe():
    chk = CraftChecker().check(LayerIR())
    assert not chk.melodic_claim_clear
    assert not chk.harmony_is_voiced


@pytest.mark.parametrize("meter", [(4, 4), (3, 4), (6, 8)])
def test_every_meter_checks_without_error(meter):
    ir = _decent_phrase()
    ir.meter = meter
    CraftChecker().check(ir)  # must not raise


# ─── Findings a person can act on ────────────────────────────────────────────
#
# `check` returns nine booleans, which tell a reviewer that something is wrong
# but not what. And the checklist has never run on a phrase the system composed:
# `craft_check` is written only inside the engine fallback path, measured at
# 0 of 164 phrases across 12 pieces. A check that never runs cannot be observed
# to be wrong, which is how the four broken ones survived.


def test_a_failing_phrase_produces_sentences_not_booleans():
    _chk, findings = check_phrase(_empty_phrase())
    assert findings
    assert all(isinstance(f, str) and len(f) > 30 for f in findings)


def test_a_passing_phrase_produces_no_findings():
    _chk, findings = check_phrase(_decent_phrase())
    assert findings == []


def test_findings_are_ordered_worst_first():
    """No melodic shape is a different order of problem from no ornament."""
    findings = craft_findings(CraftChecker().check(_empty_phrase()))
    assert "no clear shape" in findings[0]
    assert "distinctive" in findings[-1]


def test_the_score_summarizes_without_gating():
    assert craft_score(CraftChecker().check(_decent_phrase())) == 1.0
    assert craft_score(CraftChecker().check(_empty_phrase())) < 0.4


def test_findings_name_only_what_failed():
    ir = _decent_phrase()
    ir.principal_line = [e for e in ir.principal_line if e.pitch != "rest"]
    findings = craft_findings(CraftChecker().check(ir))
    assert any("No rest anywhere" in f for f in findings)
    assert not any("no clear shape" in f for f in findings)


# ─── An empty list must mean "nothing failed", never "I could not tell" ──────


def test_the_natural_composition_of_the_two_functions_works():
    """`craft_findings(check_phrase(ir))` is the obvious way to use these.

    `check_phrase` returns `(check, findings)`, and passing that tuple to
    `craft_findings` returned `[]` — a tuple has none of the named attributes,
    so `getattr(check, name) is False` was False for every one and the phrase
    read as passing.

    I wrote both functions and still made that call while falsifying these
    checks against real scores. It reported **zero findings across 133 real
    phrases**, which looked like a clean bill of health and was a broken
    harness. The real rates are 2-13%. An empty result that means "I could not
    tell" is the failure mode this whole session has been about.
    """
    from scales.craft_checker import check_phrase, craft_findings

    ir = LayerIR(key="D minor", meter=(4, 4), instrumentation="solo_piano", bar_count=1)
    for i, pitch in enumerate(["F5", "A5", "G5", "F5"]):
        ir.principal_line.append(LayerEvent(bar=1, beat=1.0 + i, pitch=pitch, duration="q"))
    for i, pitch in enumerate(["D2", "A2", "D3", "F3", "A3", "F3", "D3", "A2"]):
        ir.bass_foundation.append(LayerEvent(bar=1, beat=1.0 + i * 0.5, pitch=pitch, duration="e"))

    pair = check_phrase(ir)
    assert isinstance(pair, tuple)
    assert craft_findings(pair), "the tuple form reported nothing wrong with a bare texture"
    assert craft_findings(pair) == craft_findings(pair[0])


def test_a_phrase_that_passes_still_reports_nothing():
    """The fix must not turn every input into findings."""
    from scales.craft_checker import craft_findings

    class _AllGood:
        pass

    assert craft_findings(_AllGood()) == []
    assert craft_findings(None) == []
    assert craft_findings(()) == []
