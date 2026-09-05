"""Ten composers compiled with no musical form at all.

`formal_graphs.json` was empty for arvo-part, glass, monteverdi, morricone,
mussorgsky, palestrina, reich, williams, zimmer and style__renaissance — which
is precisely the set who write something other than sonata form. Two causes,
both silent:

  * **The vocabulary was three words.** `sonata`, `rondo`, `ternary` — the
    Classical instrumental repertoire and nobody else. Palestrina's own
    formal-approach.md opens by saying asking where the B section is "mistakes
    the genre", describes the POINT OF IMITATION at length, and the compiler had
    no word for it, so it recorded that he has no form.

  * **An asserted form was discarded unless it carried percentages.** The
    non-sonata branch read `elif sections:`, and section proportions come from
    "(35-40%)" patterns most profiles never use. So a form the document plainly
    asserts in a heading was dropped for lacking a percentage table.

285 forms across 55 packs now. Bach has fugue, toccata, prelude, ritornello and
suite where he had "sonata"; Palestrina has the point of imitation; Glass has
additive process; Pärt has tintinnabuli; Williams has leitmotif and cue.
"""

import glob
from pathlib import Path

import pytest

from scales.context_compiler import _FORM_VOCABULARY, ContextCompiler, _form_is_asserted


def _forms(composer):
    hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/")
    if not hits:
        pytest.skip(f"{composer} has no profile")
    compiler = ContextCompiler.__new__(ContextCompiler)
    return set(compiler._pass_formal_grammar(Path(hits[0]))["forms"])


# ─── Each composer gets his OWN forms ────────────────────────────────────────


@pytest.mark.parametrize(
    "composer,expected",
    [
        ("palestrina", "point of imitation"),
        ("monteverdi", "madrigal"),
        ("glass", "additive process"),
        ("arvo-part", "tintinnabuli"),
        ("williams", "leitmotif"),
        ("bach", "fugue"),
        ("mozart", "sonata"),
    ],
)
def test_a_composer_gets_the_form_he_actually_writes(composer, expected):
    assert expected in _forms(composer)


def test_bach_is_more_than_a_sonata_composer():
    """He compiled with exactly one form, and it was the one he is least
    known for."""
    forms = _forms("bach")
    assert {"fugue", "suite"} <= forms
    assert len(forms) >= 5


def test_no_armed_composer_compiles_with_no_form_at_all():
    compiler = ContextCompiler.__new__(ContextCompiler)
    empty = [
        Path(d.rstrip("/")).name
        for d in glob.glob(".claude/context/*/composer-profiles/*/")
        if not compiler._pass_formal_grammar(Path(d.rstrip("/")))["forms"]
    ]
    assert not empty, f"these composers compile with no form: {empty}"


# ─── A form is only counted where the document asserts it ────────────────────


def test_a_denied_form_is_not_recorded():
    """Palestrina's opens "There is no sonata, no rondo, no ternary reprise"."""
    assert not _form_is_asserted("There is no sonata in this repertoire", "sonata")
    assert "sonata" not in _forms("palestrina")


def test_a_form_named_in_a_heading_or_a_table_is_asserted():
    assert _form_is_asserted("## The point of imitation", "point of imitation")
    assert _form_is_asserted("| Kyrie | Ternary by liturgy | ... |", "ternary")


def test_a_form_asserted_without_proportions_is_still_recorded():
    """The `elif sections:` bug: a form was dropped for lacking a percentage
    table, which is how ten composers ended up with none."""
    assert "point of imitation" in _forms("palestrina")


# ─── Word boundaries ─────────────────────────────────────────────────────────


def test_a_form_name_inside_another_word_does_not_count():
    """`"mass" in "massive"` gave Zimmer a Mass; `"arch" in "architecture"`
    gave everyone arch form. The same collision that made `chorale` match
    `choral` and turn a solo organ work into a choir."""
    assert not _form_is_asserted("A massive orchestral cue", "mass")
    assert not _form_is_asserted("The architecture of the piece", "arch")
    assert _form_is_asserted("## The Mass movements", "mass")


def test_the_vocabulary_spans_more_than_the_classical_repertoire():
    vocab = set(_FORM_VOCABULARY)
    assert {"sonata", "rondo"} <= vocab, "the Classical forms must survive"
    assert {"point of imitation", "madrigal"} <= vocab, "Renaissance"
    assert {"fugue", "ritornello", "passacaglia"} <= vocab, "Baroque"
    assert {"additive process", "cue", "leitmotif"} <= vocab, "later and film"


# ─── A composer with two profile directories ─────────────────────────────────


def test_both_of_wagners_profiles_are_read():
    """Wagner's two directories are deliberate, not an accident.

    `romantic/wagner` covers the earlier operas; `late-romantic/wagner` covers
    Tristan onward. Each cross-references the other, and the late one's own
    guide says "for composition, use the romantic/wagner fingerprints".

    The compiler picked the heavier directory and logged that "half the doctrine
    is unreachable" — which was exactly right: **536 substantive lines** existed
    only in the copy it discarded, including the Parsifal key associations, the
    layered-motif tables and the late orchestration philosophy.
    """
    from scales.context_compiler import _profile_dirs

    dirs = _profile_dirs("wagner")
    if len(dirs) < 2:
        pytest.skip("wagner is no longer split")
    compiler = ContextCompiler.__new__(ContextCompiler)
    both = compiler._pass_orchestration(dirs[0])
    entries = len(both["instruments"]) + len(both.get("textures", []))
    assert entries > 35, (
        f"only {entries} orchestration entries — the heavier directory alone gives 30, "
        "so the second is not being read"
    )
    assert "leitmotif" in compiler._pass_formal_grammar(dirs[0])["forms"]


def test_a_composer_with_one_directory_is_unaffected():
    """Reading every directory must not change the single-directory case."""
    from scales.context_compiler import _profile_dirs, _profile_text

    dirs = _profile_dirs("chopin")
    assert len(dirs) == 1
    joined = _profile_text(dirs[0], "orchestration.md")
    assert joined == (dirs[0] / "orchestration.md").read_text()


def test_a_missing_file_in_one_directory_is_skipped_not_fatal():
    from scales.context_compiler import _profile_dirs, _profile_text

    dirs = _profile_dirs("wagner")
    if not dirs:
        pytest.skip("wagner has no profile")
    assert _profile_text(dirs[0], "no-such-file.md") == ""
