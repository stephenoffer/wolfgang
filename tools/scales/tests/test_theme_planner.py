"""Theme election, development, and whether the theme is a theme.

Three bugs fixed here, two of them named in the 2026-08-18 audit (C16, C17) and
still live:

* Every developed theme was spelled with flats, so a theme in E major came back
  as E-G♭-A♭ — wrong accidentals and a wrong harmonic reading of the agent's own
  principal theme, every time it was developed.
* ``augment`` doubled every duration without re-barring, so a four-quarter theme
  in 4/4 came back as eight beats and overflowed its own phrase.
* The duration tables were a 7-entry dict and its reverse, so augmenting or
  diminishing a theme in triplets, 32nds, 64ths or double-dotted values returned
  it UNCHANGED while the brief told the agent it was an augmentation.
"""

import pytest

from scales.models import LayerEvent, LayerIR, MotifObject
from scales.theme_planner import (
    analyze_theme,
    develop_theme_surface,
    elect_principal_theme,
    plan_section_opening_placements,
    theme_recurrence,
)


def _theme(pitches, durs=None, key="C major", meter=(4, 4)):
    ir = LayerIR(key=key, meter=meter)
    durs = durs or ["q"] * len(pitches)
    for i, (p, d) in enumerate(zip(pitches, durs)):
        ir.principal_line.append(LayerEvent(bar=1 + i // 4, beat=1 + (i % 4), pitch=p, duration=d))
    return ir


# ─── C16: accidentals follow the key ─────────────────────────────────────────


def test_a_theme_in_a_sharp_key_keeps_its_sharps():
    t = _theme(["E5", "F#5", "G#5", "A5"], key="E major")
    assert develop_theme_surface(t, "state") == "E5q F#5q G#5q A5q"


def test_a_theme_in_a_flat_key_keeps_its_flats():
    t = _theme(["Ab4", "Bb4", "C5", "Db5"], key="Ab major")
    out = develop_theme_surface(t, "state")
    assert "Ab4" in out and "Bb4" in out and "Db5" in out
    assert "#" not in out


def test_transposition_respells_into_the_new_pitches_not_always_flats():
    t = _theme(["C5", "D5", "E5"], key="D major")
    out = develop_theme_surface(t, "state", transpose_semitones=2)
    assert "F#5" in out, out


# ─── C17: augmentation fits its span ─────────────────────────────────────────


def test_augmentation_does_not_overflow_the_theme_s_own_bar():
    from scales.direct_compose import _parse_shorthand
    from scales.duration import dur_to_beats

    t = _theme(["E5", "F#5", "G#5", "A5"], key="E major")  # 4 beats in 4/4
    out = develop_theme_surface(t, "augment")
    total = sum(float(dur_to_beats(ev["dur"])) for ev in _parse_shorthand(out))
    assert total <= 4.0, f"augmented theme ran to {total} beats in a 4/4 bar"


def test_augmentation_still_lengthens_the_notes_it_keeps():
    t = _theme(["E5", "F#5", "G#5", "A5"], key="E major")
    assert "h" in develop_theme_surface(t, "augment")


def test_augmentation_works_on_triplets():
    """The old 7-entry table silently returned triplets unchanged."""
    ir = LayerIR(key="C major", meter=(4, 4))
    for i, p in enumerate(["C5", "D5", "E5"]):
        ir.principal_line.append(
            LayerEvent(bar=1, beat=1 + i / 3, pitch=p, duration="trip_e")
        )
    out = develop_theme_surface(ir, "augment")
    assert "trip_q" in out, out


def test_diminution_halves_a_dotted_value():
    t = _theme(["C5", "D5"], durs=["dh", "dh"], key="C major")
    assert "dq" in develop_theme_surface(t, "diminish")


# ─── The other transforms ────────────────────────────────────────────────────


def test_inversion_mirrors_around_the_first_note():
    t = _theme(["C5", "E5", "G5"], key="C major")
    out = develop_theme_surface(t, "invert").split()
    assert out[0].startswith("C5")
    assert out[1].startswith("Ab4") or out[1].startswith("G#4")


def test_retrograde_reverses():
    t = _theme(["C5", "D5", "E5"], key="C major")
    assert develop_theme_surface(t, "retrograde").split()[0].startswith("E5")


def test_fragment_takes_the_head():
    t = _theme(["C5", "D5", "E5", "F5"], key="C major")
    assert len(develop_theme_surface(t, "fragment").split()) == 2


def test_an_empty_theme_develops_to_nothing():
    assert develop_theme_surface(None, "state") == ""
    assert develop_theme_surface(LayerIR(), "augment") == ""


# ─── Election and placement ──────────────────────────────────────────────────


def test_the_most_theme_like_motif_is_elected():
    bank = {
        "thin": MotifObject(motif_id="thin", interval_contour=[1]),
        "rich": MotifObject(
            motif_id="rich",
            interval_contour=[2, 2, -1, -2],
            rhythm_cell=["q", "e", "e", "h"],
            recognition_anchor="head",
        ),
    }
    assert elect_principal_theme(bank) == "rich"


def test_an_empty_motif_bank_elects_nothing():
    assert elect_principal_theme({}) is None


def test_section_role_decides_the_transform():
    assert plan_section_opening_placements("development", "t")[0].operation == "fragment"
    assert plan_section_opening_placements("recap", "t")[0].operation == "augment"
    assert plan_section_opening_placements("a", "t")[0].operation == "state"


# ─── Is it a theme at all? ───────────────────────────────────────────────────


def test_a_scale_is_reported_as_a_scale_not_a_tune():
    t = _theme(["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
    a = analyze_theme(t)
    assert a["longest_scalar_run"] >= 5
    assert any("scale passage" in c for c in a["concerns"])


def test_an_undifferentiated_rhythm_is_called_out():
    t = _theme(["C5", "G5", "E5", "C5"])  # all quarters
    assert any("same length" in c for c in analyze_theme(t)["concerns"])


def test_a_broken_chord_is_reported_as_outlining_a_chord():
    t = _theme(["C5", "E5", "G5", "C6", "G5", "E5"], durs=["q", "e", "e", "h", "q", "q"])
    assert any("outlines a chord" in c for c in analyze_theme(t)["concerns"])


def test_a_real_tune_draws_no_concerns():
    # A shape: rises by step to a peak, leaps down, resolves — varied rhythm.
    t = _theme(
        ["C5", "D5", "E5", "G5", "C5", "D5", "E5"],
        durs=["q", "e", "e", "h", "q", "e", "h"],
    )
    a = analyze_theme(t)
    assert a["concerns"] == [], a["concerns"]


def test_a_theme_too_short_to_judge_says_so():
    a = analyze_theme(_theme(["C5", "D5"]))
    assert "too short to analyze" in a["observations"]


# ─── Recurrence ──────────────────────────────────────────────────────────────


class _Phrase:
    def __init__(self, realized):
        self.realized = realized


class _Graph:
    def __init__(self, phrases):
        self.phrases = phrases


def test_a_transposed_return_still_counts_as_the_theme():
    """Matching absolute pitch would miss every real restatement."""
    theme = _theme(["C5", "D5", "E5", "G5"])
    moved = {
        "principal_line": [
            {"bar": 9, "beat": 1.0, "pitch": p, "duration": "q"}
            for p in ("G5", "A5", "B5", "D6")  # the same contour, up a fifth
        ]
    }
    r = theme_recurrence(_Graph({"m1_b_p1": _Phrase(moved)}), theme)
    assert len(r["recurrences"]) == 1
    assert r["recurrences"][0]["exact"] is True


def test_a_different_tune_is_not_counted_as_a_return():
    theme = _theme(["C5", "D5", "E5", "G5"])
    other = {
        "principal_line": [
            {"bar": 9, "beat": 1.0, "pitch": p, "duration": "q"}
            for p in ("C5", "C4", "B5", "F4")
        ]
    }
    r = theme_recurrence(_Graph({"m1_b_p1": _Phrase(other)}), theme)
    assert r["recurrences"] == []


def test_recurrence_accepts_a_layer_ir_not_only_a_string():
    """A caller that mis-serialized a chord silently reported zero returns."""
    theme = _theme(["C5", "D5", "E5", "G5"])
    same = {
        "principal_line": [
            {"bar": 1, "beat": 1.0, "pitch": p, "duration": "q"}
            for p in ("C5", "D5", "E5", "G5")
        ]
    }
    r = theme_recurrence(_Graph({"m1_a_p1": _Phrase(same)}), theme)
    assert len(r["recurrences"]) == 1
    assert r["sections"] == ["m1_a"]


def test_chords_in_the_melody_do_not_break_the_contour():
    theme = LayerIR(key="C major")
    for i, p in enumerate([["C5", "E5"], ["D5", "F5"], ["E5", "G5"]]):
        theme.principal_line.append(LayerEvent(bar=1, beat=1 + i, pitch=p, duration="q"))
    from scales.theme_planner import _contour_of

    # Top voices are E5, F5, G5 — a semitone then a tone.
    assert _contour_of(theme) == [1, 2], "top voice of each chord makes the contour"


@pytest.mark.parametrize("key", ["C major", "E major", "Ab major", "f# minor", "bb minor"])
def test_every_key_develops_without_error(key):
    t = _theme(["C5", "D5", "E5", "F5"], key=key)
    assert develop_theme_surface(t, "state")
    assert develop_theme_surface(t, "augment")
