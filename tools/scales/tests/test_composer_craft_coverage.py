"""Every armed composer must have a craft vocabulary the compiler can read.

`mozart-lh-vocabulary.md` opens by naming the loudest texture tell there is — "a
static bass note held under perpetual figuration, the same idiom every bar" —
catalogues ten alternatives in this system's own shorthand, and says when each
belongs. It existed for **one of forty-eight composers**, and its companion
`mozart-devices.md` was read by no code at all.

So a piece composed "as Beethoven" or "as Chopin" reached the composer with no
catalogue of accompaniment idioms to reach for and no catalogue of the melodic
and structural gestures that separate that composer from generic tonal music.
The parser existed; the content did not, and for devices the reader did not
either.

These tests pin the coverage so it cannot silently regress, and the parse so a
badly-formatted file is noticed rather than silently yielding nothing.
"""

import glob
import pathlib

import pytest

from scales.context_compiler import ContextCompiler

# Composers with enough real corpus to be composed AS. Anything here must have
# both catalogues, because these are the ones the briefs actually draw on.
_ARMED = {
    "mozart": "classical",
    "beethoven": "classical",
    "haydn": "classical",
    "chopin": "romantic",
    "schubert": "romantic",
    "liszt": "romantic",
    "bach": "baroque",
    "handel": "baroque",
    "corelli": "baroque",
    "palestrina": "renaissance",
    "monteverdi": "renaissance",
}

_MIN_IDIOMS = 8
_MIN_DEVICES = 12


def _dir(name):
    return pathlib.Path(f".claude/context/{_ARMED[name]}/composer-profiles/{name}")


@pytest.mark.parametrize("composer", sorted(_ARMED))
def test_every_armed_composer_has_a_texture_vocabulary(composer):
    d = _dir(composer)
    if not d.exists():
        pytest.skip(f"{composer} profile directory absent")
    idioms = ContextCompiler._composer_hand_idioms(d)
    assert len(idioms) >= _MIN_IDIOMS, (
        f"{composer} compiles only {len(idioms)} hand idioms — a composer with no "
        f"catalogue of accompaniment idioms has nothing to reach for but the one "
        f"figure it started with"
    )


@pytest.mark.parametrize("composer", sorted(_ARMED))
def test_every_armed_composer_has_a_device_catalogue(composer):
    d = _dir(composer)
    if not d.exists():
        pytest.skip(f"{composer} profile directory absent")
    devices = ContextCompiler._composer_devices(d)
    assert len(devices) >= _MIN_DEVICES, (
        f"{composer} compiles only {len(devices)} devices — without them the "
        f"surface has no way to sound like this composer rather than like "
        f"generic tonal music"
    )


@pytest.mark.parametrize("composer", sorted(_ARMED))
def test_the_catalogues_carry_real_descriptions(composer):
    """A parse that yields empty bodies is the same as no file."""
    d = _dir(composer)
    if not d.exists():
        pytest.skip(f"{composer} profile directory absent")
    for entry in ContextCompiler._composer_hand_idioms(d) + ContextCompiler._composer_devices(d):
        assert entry["name"], f"{composer}: an entry has no name"
        # Name AND description together, because an author may legitimately put
        # most of an item inside the bold title. Checking the description alone
        # failed on `**The written-out cadenza before the final cadence** of an
        # aria.` — a perfectly good entry with a four-word tail.
        full = f"{entry['name']} {entry['description']}".strip()
        assert len(full) > 24, (
            f"{composer}: '{entry['name']}' carries only {len(full)} characters "
            f"of content — probably a formatting break in the source file"
        )


def test_devices_reach_the_compiled_pack():
    """A parser nothing calls is the same bug as a file nothing reads.

    `_composer_devices` is wired into the figuration-templates pass; if it is
    ever unwired, the catalogues stop reaching the composer while every other
    test here still passes.

    Checked against the COMPILED PACKS rather than against the source text. The
    earlier version asserted the literal string `self._composer_devices(
    profile_dir)` appeared in the compiler, and broke the moment that call was
    legitimately rewritten to run over a style's member profiles — flagging a
    correct change as a regression while proving nothing about whether any
    device ever reached a pack.
    """
    import json

    reached = 0
    for path in glob.glob("tools/compiled_packs/*/figuration_templates.json"):
        data = json.load(open(path))
        items = (
            data
            if isinstance(data, list)
            else next((v for v in data.values() if isinstance(v, list)), [])
        )
        if any(i.get("category") == "composer_device" for i in items if isinstance(i, dict)):
            reached += 1
    assert reached >= 20, (
        f"only {reached} compiled packs carry any composer_device entry — "
        "the catalogue is parsed but not fed into the pack"
    )


def test_the_catalogues_are_findable_by_convention():
    """Adding one for a new composer must need no code change."""
    for composer in _ARMED:
        d = _dir(composer)
        if not d.exists():
            continue
        assert list(d.glob("*-lh-vocabulary.md")), f"{composer}: no *-lh-vocabulary.md"
        assert list(d.glob("*-devices.md")), f"{composer}: no *-devices.md"


# ─── Nothing may be silently dropped ─────────────────────────────────────────
#
# The original parser required `**Name** — description` and silently dropped any
# item written `**Name**, description` or `**Name.**` — six of eleven idioms in
# one file, with no error. Two regex fixes each revealed another case (a `^` that
# could not match at a scan position sitting on a newline; an item following any
# empty-bodied one). It is now a line walker, which cannot have this class of
# bug.
#
# Silent loss is the worst failure available here: a file that parses to nothing
# is indistinguishable from a file that does not exist, which is precisely the
# bug the catalogues were written to fix.


def _numbered_items(path):
    import re

    return re.findall(r"^\s*\d+\.\s+\*\*", path.read_text(), re.MULTILINE)


def test_every_numbered_item_in_every_catalogue_is_parsed():
    root = pathlib.Path(".claude/context")
    mismatches = []
    total_in_files = total_parsed = 0
    for d in sorted(root.glob("*/composer-profiles/*")):
        for pattern, fn in (
            ("*-lh-vocabulary.md", ContextCompiler._composer_hand_idioms),
            ("*-devices.md", ContextCompiler._composer_devices),
        ):
            files = list(d.glob(pattern))
            if not files:
                continue
            in_files = sum(len(_numbered_items(f)) for f in files)
            parsed = len(fn(d))
            total_in_files += in_files
            total_parsed += parsed
            if parsed != in_files:
                mismatches.append(f"{d.name}/{pattern}: {in_files} written, {parsed} parsed")
    assert total_in_files > 100, "the catalogues are not being found at all"
    assert not mismatches, "catalogue items are being dropped:\n" + "\n".join(mismatches)


def test_an_item_written_without_a_dash_is_still_parsed():
    """`**Name**, description` and `**Name.**` were both dropped entirely."""
    from scales.context_compiler import _parse_catalogue

    text = (
        "## Devices\n"
        "1. **With a dash** — a description.\n"
        "2. **With a comma**, a description.\n"
        "3. **Everything inside the bold.**\n"
        "4. **With a colon**: a description.\n"
    )
    items = list(_parse_catalogue(text))
    assert len(items) == 4, [i[1] for i in items]
    assert all(section == "Devices" for section, _n, _b in items)
    # An item with no body keeps its own name as the text rather than vanishing.
    assert items[2][2]


def test_an_item_following_an_empty_bodied_one_survives():
    """The regex lost exactly this case, twice, in two different ways."""
    from scales.context_compiler import _parse_catalogue

    text = "1. **First.**\n2. **Second.**\n3. **Third** — with a body.\n"
    assert len(list(_parse_catalogue(text))) == 3


def test_a_multi_line_description_is_joined():
    from scales.context_compiler import _parse_catalogue

    text = "1. **Name** — a description that\n   continues on the next line.\n"
    items = list(_parse_catalogue(text))
    assert len(items) == 1
    assert "continues on the next line" in items[0][2]


def test_an_item_whose_bold_name_wraps_is_still_parsed():
    """Markdown lets a bold name run onto the next line, and a person writing a
    long device name does it without thinking:

        15. **Themes built from a rising interval — a fifth or an octave — then
            a slow stepwise descent.** Spacious, singable, slow to unfold.

    Matching only the single-line form dropped that item silently. Bruckner's
    catalogue read 17 items and compiled 16, and nothing anywhere said so — the
    fourth distinct way this parser has lost an item without an error, which is
    why it is a line walker and why every one of them has a test.
    """
    from scales.context_compiler import _parse_catalogue

    text = (
        "## Melodic devices\n\n"
        "1. **Short name** — a body.\n\n"
        "2. **A name that runs on past the width of the line and keeps\n"
        "   going before it closes.** The body follows here.\n\n"
        "3. **Another short one** — more body.\n"
    )
    items = list(_parse_catalogue(text))
    assert len(items) == 3, f"parsed {len(items)} of 3: {[i[1] for i in items]}"
    assert "runs on past the width" in items[1][1]
    assert "The body follows here" in items[1][2]
    assert items[2][1] == "Another short one", "the item AFTER a wrapped one must survive"


def test_a_wrapped_name_that_never_closes_is_not_swallowed():
    """The lookahead must give up rather than eat the following items."""
    from scales.context_compiler import _parse_catalogue

    text = (
        "## Devices\n\n"
        "1. **An unclosed name that never gets its stars\n\n"
        "2. **A perfectly good item** — with a body.\n"
    )
    names = [i[1] for i in _parse_catalogue(text)]
    assert "A perfectly good item" in names
