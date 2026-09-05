"""Fields the compiler wrote empty beside the data that fills them.

A field-level audit across every compiled pack found **34,244 blank field
instances** in 28 field kinds. The decisive question for each was not "is it
blank" but two others:

  1. Does anything READ it? (`chord_sequence` -> `harmonic_solver`, `cadence_bank`,
     `donor_strategy`; `emotional_color` and `soprano_line` -> the brief.)
  2. Does the SOURCE contain what would fill it?

The second question is what stopped this becoming an exercise in inventing
data. Probing the doctrine for each field:

    modulation_scripts.chord_sequence      2,133 source mentions   <- lost data
    figuration_templates.register_sugg.      722
    cadence_scripts.inner_voice_rules        262
    figuration_templates.density_sugg.       170
    ---------------------------------------------------------------
    harmonic_devices.chord_sequence            9 rows in 409 (2%)  <- honest blank
    cadence_scripts.typical_texture            0
    gesture_templates.phrase_functions         0
    counterpoint_rules.repair_recipe           0

So most blanks are NOT lost data — the schema promises fields the doctrine never
contained, and filling them would mean inventing chords. Only where the source
actually says something was anything changed:

    harmonic_devices.emotional_color      100% blank -> 36%
    modulation_scripts.chord_sequence     100% blank -> 61%
    modulation_scripts.voice_leading      100% blank -> 53%
    harmonic_devices.voice_leading        100% blank -> 96%
    harmonic_devices.chord_sequence       100% blank -> 99%   (2% is all there is)
"""

import glob
import json

import pytest

from scales.context_compiler import _pivot_chords, _voice_leading_hints


def _field_blank_rate(pack, field):
    blank = total = 0
    for path in glob.glob(f"tools/compiled_packs/*/{pack}.json"):
        data = json.load(open(path))
        items = (
            data
            if isinstance(data, list)
            else next((v for v in data.values() if isinstance(v, list)), [])
        )
        for item in items:
            if isinstance(item, dict) and field in item:
                total += 1
                if not item[field]:
                    blank += 1
    if not total:
        pytest.skip(f"{pack} not compiled")
    return blank / total


# ─── The emotional reading was collected and then written blank beside itself ─


def test_emotional_colour_is_no_longer_blank_in_every_device():
    """`contexts` held the emotional reading; `emotional_color` was set to ""
    on the next line. The same table cell, filed once and discarded once."""
    assert _field_blank_rate("harmonic_devices", "emotional_color") < 0.5


def test_a_pivot_modulation_carries_its_three_chords():
    """A pivot IS a three-chord sequence, and the chords were already sitting
    in the two fields beside the empty one."""
    assert _field_blank_rate("modulation_scripts", "chord_sequence") < 0.75


# ─── Extracting chords, not prose ────────────────────────────────────────────


def test_only_the_numerals_are_taken_from_a_pivot_row():
    """Taking the cells whole gave `["C major", "I = IV", "IV of G"]` — a key
    name, an equation and a prose phrase. A field that is WRONG is worse than a
    field that is empty, because a reader trusts it."""
    assert _pivot_chords("C major", "I = IV", "IV of G") == ["I", "IV"]
    assert _pivot_chords("Am", "vi = iv", "iv of Em... or iii = vi") == [
        "vi",
        "iv",
        "iii",
        "vi",
    ]


def test_a_row_with_no_numerals_yields_nothing():
    assert _pivot_chords("the relative major", "by ear", "") == []


def test_a_repeated_numeral_is_not_repeated_consecutively():
    assert _pivot_chords("I", "I = I", "I") == ["I"]


# ─── Voice-leading hints ─────────────────────────────────────────────────────


def test_voice_leading_is_read_out_of_the_prose():
    hints = _voice_leading_hints("The common tone is held while the bass moves by step")
    assert "common tone held" in hints and "step in the bass" in hints


def test_prose_that_describes_no_voice_motion_yields_nothing():
    assert _voice_leading_hints("A bright and cheerful passage") == []
    assert _voice_leading_hints("") == []


# ─── The audit's own conclusion, kept as a guard ─────────────────────────────


def test_the_honest_blanks_are_left_alone():
    """`harmonic_devices.chord_sequence` stays mostly blank ON PURPOSE.

    Only 9 of 409 device-table rows across the whole doctrine spell out a chord
    chain — the documents name devices by effect, not by progression. If this
    ever drops sharply, someone has started inventing chords to fill a field,
    which is the failure this project exists to avoid.
    """
    rate = _field_blank_rate("harmonic_devices", "chord_sequence")
    assert rate > 0.9, (
        f"only {1 - rate:.0%} of harmonic devices were blank — the sources support "
        "about 2%, so anything much above that is invented"
    )


# ─── The answer was two tables further down the same document ────────────────


def test_a_figuration_carries_its_register_and_density():
    """`figuration-patterns.md` has a "Climax Building Reference Table" mapping
    each dynamic to a register span, a rhythmic density, and the figuration
    NUMBERS it applies to. Every template shipped with `density_suggestion:
    None` and `register_suggestion: ""` — 660 blank fields read by
    `style_resolver` — while the answer sat in the same file, indexed by the
    very number in each template's own id."""
    assert _field_blank_rate("figuration_templates", "register_suggestion") < 0.5
    assert _field_blank_rate("figuration_templates", "density_suggestion") < 0.5


def test_the_climax_table_indexes_by_figuration_number():
    from scales.context_compiler import _climax_suggestions

    text = (
        "## Climax Building Reference Table\n\n"
        "| Dynamic | Texture | Figurations to Use | Register Span | Rhythmic Density |\n"
        "|---|---|---|---|---|\n"
        "| pp | Single line | #2, #3 | 1-2 octaves | Quarter notes |\n"
        "| ff | Cascading | #6, #10 | 4+ octaves | Dense sixteenths |\n"
    )
    got = _climax_suggestions(text)
    assert got["2"]["register"] == ["1-2 octaves"]
    assert got["6"]["density"] == ["Dense sixteenths"]
    assert "3" in got and "10" in got


def test_a_figuration_the_table_never_names_gets_nothing():
    """Two of the twelve are absent from the climax table, and inventing a
    register for them would be worse than leaving them blank."""
    from scales.context_compiler import _climax_suggestions

    got = _climax_suggestions(
        "## T\n\n| Dynamic | Figurations to Use | Register Span |\n"
        "|---|---|---|\n| pp | #2 | 1-2 octaves |\n"
    )
    assert "5" not in got


def test_a_table_without_a_figuration_column_is_ignored():
    """Otherwise every table in the document contributes noise."""
    from scales.context_compiler import _climax_suggestions

    assert (
        _climax_suggestions(
            "## Other\n\n| Name | Register Span |\n|---|---|\n| Thing | 2 octaves |\n"
        )
        == {}
    )


# ─── An idiom's own notes ────────────────────────────────────────────────────


def test_a_hand_idiom_carries_the_pattern_that_it_is():
    """Every `*-lh-vocabulary.md` entry states its idiom as real shorthand —
    `Ab1e Eb3e Ab3e C4e Eb4e C4e Ab3e Eb3e` — and the compiler kept only the
    prose, truncated to 400 characters. The brief could NAME a composer's
    left-hand idioms without handing over the notes, while the pattern sat
    inside a string it had already read."""
    from pathlib import Path

    from scales.context_compiler import ContextCompiler

    hits = glob.glob(".claude/context/*/composer-profiles/chopin/")
    if not hits:
        pytest.skip("chopin profile missing")
    idioms = ContextCompiler._composer_hand_idioms(Path(hits[0]))
    playable = [i for i in idioms if i.get("shorthand")]
    assert playable, "not one Chopin left-hand idiom carries its pattern"
    for idiom in playable:
        assert idiom["register"][0] < idiom["register"][1]
        assert idiom["events"] >= 2


def test_the_measured_reach_separates_the_idioms():
    """Chopin's wide arpeggiated wave spans 31 semitones; Mozart's Alberti
    spans 7. That difference is the texture, and no document states it in
    words — it is only computable from the pattern."""
    from pathlib import Path

    from scales.context_compiler import ContextCompiler

    def widest(composer):
        hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/")
        if not hits:
            pytest.skip(f"{composer} profile missing")
        spans = [
            i["span_semitones"]
            for i in ContextCompiler._composer_hand_idioms(Path(hits[0]))
            if i.get("span_semitones")
        ]
        if not spans:
            pytest.skip(f"{composer} has no playable idiom")
        return max(spans)

    assert widest("chopin") > widest("mozart")


def test_prose_with_no_pattern_adds_no_fields():
    """An idiom described only in words must not acquire an invented register."""
    from scales.context_compiler import _idiom_shape

    assert _idiom_shape("the left hand simply rests for the bar") == {}
    assert _idiom_shape("") == {}


def test_an_unparseable_pattern_keeps_the_text_and_claims_no_measurement():
    from scales.context_compiler import _idiom_shape

    shape = _idiom_shape("written as `Q9z Q9z` in the old notation")
    assert "register" not in shape and "span_semitones" not in shape
