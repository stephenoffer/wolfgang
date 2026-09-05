"""Three compiler passes read rich documents and produced nothing.

The composer profiles carry their most structured knowledge in markdown TABLES
and in fenced JSON blocks. Three passes opened those files, confirmed they
existed, and compiled empty packs — each in a different way, and none with an
error:

  * `_pass_orchestration` was a stub. It returned `{"instruments": {}}` under
    the comment "would be more sophisticated in production". **Empty for 55 of
    55 composers.**
  * `_pass_cross_references` matched the literal phrases "influenced by",
    "learned from" or "absorbed" followed by one word. The influence tables say
    none of those things. Empty for 39 of 50.
  * `_pass_prototypes` called `json.loads` on each fenced block. The blocks hold
    SEVERAL objects one after another, so it raised "Extra data" and the
    `except: continue` threw away the whole block including the object it had
    already parsed. **55 of 66 blocks lost, and not one composer had a block
    that parsed.**

All three feed live consumers. `orchestration_roles` is what the concerto and
symphony path reads for instrument assignment; `influence_axes` is how
`donor_strategy` finds historically related composers to borrow material from;
`phrase_prototypes` is loaded by `style_resolver`. Each was reading an empty
drawer, which is indistinguishable from a composer who has nothing to say.

    orchestration_roles     0 -> 1472 entries      55/55 empty -> 8/55
    influence_axes          ~0 -> 707 entries      39/50 empty -> 9/50
    phrase_prototypes       11 -> 213 entries      46/50 empty -> 33/50
    empty pack files total  165 -> 79
"""

import glob
import json
import os
from pathlib import Path

import pytest

from scales.context_compiler import ContextCompiler, _parse_md_tables, _table_column

_PROFILES = sorted(glob.glob(".claude/context/*/composer-profiles/*/"))


def _c():
    return ContextCompiler.__new__(ContextCompiler)


def _dir(name):
    hits = glob.glob(f".claude/context/*/composer-profiles/{name}/")
    if not hits:
        pytest.skip(f"{name} has no profile")
    return Path(hits[0])


# ─── The table parser ────────────────────────────────────────────────────────


def test_a_table_is_read_with_its_heading():
    text = (
        "## Voice Roles\n\n"
        "| Voice | Hand/Register | Function |\n"
        "|-------|---------------|----------|\n"
        "| Bass | LH, lowest | Harmonic root |\n"
        "| Soprano | RH, top | Primary melody |\n"
    )
    tables = _parse_md_tables(text)
    assert len(tables) == 1
    assert tables[0]["caption"] == "Voice Roles"
    assert tables[0]["headers"][0] == "Voice"
    assert len(tables[0]["rows"]) == 2


def test_two_tables_under_different_headings_stay_apart():
    text = (
        "## First\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n"
        "## Second\n\n| C | D |\n|---|---|\n| 3 | 4 |\n"
    )
    tables = _parse_md_tables(text)
    assert [t["caption"] for t in tables] == ["First", "Second"]


def test_a_ragged_row_is_dropped_not_misaligned():
    """A row with the wrong cell count would shift every field if kept."""
    text = "## T\n\n| A | B |\n|---|---|\n| 1 | 2 |\n| oops |\n| 3 | 4 |\n"
    assert _parse_md_tables(text)[0]["rows"] == [["1", "2"], ["3", "4"]]


def test_a_column_is_not_claimed_twice():
    """Chopin's table heads a column `Hand/Register`, which matches both the
    hand lookup and the register lookup — so one cell was filed as two facts."""
    table = {"headers": ["Voice", "Hand/Register", "Function"], "rows": []}
    claimed = {0}
    first = _table_column(table, "register", "range", taken=claimed)
    claimed.add(first)
    second = _table_column(table, "hand", taken=claimed)
    assert first == 1 and second is None


# ─── Concatenated JSON ───────────────────────────────────────────────────────


def test_several_objects_in_one_block_are_all_recovered(tmp_path):
    """The failure that lost 55 of 66 blocks."""
    guide = tmp_path / "composition-guide.md"
    guide.write_text(
        '```json\n{"id": "a", "n": 1}\n\n{"id": "b", "n": 2}\n\n{"id": "c", "n": 3}\n```\n'
    )
    got = _c()._pass_prototypes(tmp_path)["prototypes"]
    assert [p["data"]["id"] for p in got] == ["a", "b", "c"]


def test_prose_after_the_objects_does_not_discard_them(tmp_path):
    """`json.loads` raised on the trailing text and dropped everything."""
    guide = tmp_path / "composition-guide.md"
    guide.write_text('```json\n{"id": "a"}\n\n... and so on for the rest\n```\n')
    got = _c()._pass_prototypes(tmp_path)["prototypes"]
    assert len(got) == 1 and got[0]["data"]["id"] == "a"


def test_a_block_that_is_not_json_at_all_yields_nothing(tmp_path):
    guide = tmp_path / "composition-guide.md"
    guide.write_text("```json\nnot json, just words\n```\n")
    assert _c()._pass_prototypes(tmp_path)["prototypes"] == []


# ─── The passes over the real profiles ───────────────────────────────────────


def test_orchestration_is_no_longer_empty_for_the_flagship_composers():
    for name in ("chopin", "mozart", "bach", "beethoven"):
        result = _c()._pass_orchestration(_dir(name))
        entries = len(result["instruments"]) + len(result.get("textures", []))
        assert entries >= 5, f"{name} compiled only {entries} orchestration entries"


def test_influences_are_read_from_the_table_not_from_a_phrase():
    """Chopin's cross-references name Bach, Mozart, Hummel, Field and Bellini in
    a table whose header says "What Was Absorbed" — a prose regex for
    "influenced by X" finds none of them."""
    result = _c()._pass_cross_references(_dir("chopin"))
    names = " ".join(e["composer"] for e in result["influenced_by"]).lower()
    assert "bach" in names and "field" in names
    assert any(e.get("absorbed") for e in result["influenced_by"])


def test_the_direction_of_influence_is_not_reversed():
    """Handing `donor_strategy` a composer's descendants as his sources would
    be worse than handing it nothing."""
    result = _c()._pass_cross_references(_dir("chopin"))
    sources = " ".join(e["composer"] for e in result["influenced_by"]).lower()
    assert "debussy" not in sources, "a composer Chopin influenced is listed as his source"


def test_most_packs_now_carry_orchestration_roles():
    """The pack on disk, not the pass in isolation — the wiring, not the logic."""
    empty = total = 0
    for p in sorted(glob.glob("tools/compiled_packs/*/")):
        f = os.path.join(p, "orchestration_roles.json")
        if not os.path.exists(f):
            continue
        total += 1
        data = json.load(open(f))
        if not (data.get("instruments") or data.get("textures")):
            empty += 1
    if not total:
        pytest.skip("packs not compiled")
    assert empty / total < 0.25, (
        f"{empty} of {total} compiled packs still have no orchestration roles "
        "— it was 55 of 55 when this was a stub"
    )


# ─── A prototype that is a bare word is worse than no prototype ──────────────


def test_a_key_value_fragment_is_wrapped_not_read_as_a_string(tmp_path):
    """The regression this test exists for was mine.

    Many ```json blocks in these guides are a FRAGMENT of an object —
    `"bass": [ ... ]` — not a standalone value. Fixing the "Extra data" bug with
    `raw_decode` made it read `"bass"` as a string and stop at the colon, so
    SEVEN of Chopin's fourteen prototypes compiled as the bare word "bass".

    That is worse than the empty list it replaced: a reader trusts a populated
    field. It is the same principle as refusing to store
    `["C major", "I = IV", "IV of G"]` as a chord sequence.
    """
    guide = tmp_path / "composition-guide.md"
    guide.write_text(
        '```json\n"bass": [\n  {"p": "Eb2", "d": "e"},\n  {"p": "Bb3", "d": "e"}\n]\n```\n'
    )
    got = _c()._pass_prototypes(tmp_path)["prototypes"]
    assert len(got) == 1
    assert isinstance(got[0]["data"], dict)
    assert got[0]["data"]["bass"][0]["p"] == "Eb2"


def test_a_bare_scalar_is_never_stored_as_a_prototype(tmp_path):
    guide = tmp_path / "composition-guide.md"
    guide.write_text('```json\n"just a string"\n```\n```json\n42\n```\n')
    assert _c()._pass_prototypes(tmp_path)["prototypes"] == []


def test_no_compiled_prototype_anywhere_is_a_bare_scalar():
    """The end-to-end version, over every pack on disk."""
    bad = []
    for path in glob.glob("tools/compiled_packs/*/phrase_prototypes.json"):
        data = json.load(open(path))
        for proto in data.get("prototypes", []) if isinstance(data, dict) else data:
            if not isinstance(proto.get("data"), (dict, list)):
                bad.append((os.path.basename(os.path.dirname(path)), proto))
    assert not bad, f"{len(bad)} prototypes are scalars, e.g. {bad[:3]}"
