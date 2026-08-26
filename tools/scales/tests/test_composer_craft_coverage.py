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
        assert len(entry["description"]) > 20, (
            f"{composer}: '{entry['name']}' has a {len(entry['description'])}-char "
            f"description — probably a formatting break in the source file"
        )


def test_devices_reach_the_compiled_pack():
    """A parser nothing calls is the same bug as a file nothing reads.

    `_composer_devices` is wired into the figuration-templates pass; if it is
    ever unwired, the catalogues stop reaching the composer while every other
    test here still passes.
    """
    source = pathlib.Path("tools/scales/context_compiler.py").read_text()
    assert "self._composer_devices(profile_dir)" in source, (
        "the devices catalogue is parsed but no longer fed into the pack"
    )


def test_the_catalogues_are_findable_by_convention():
    """Adding one for a new composer must need no code change."""
    for composer in _ARMED:
        d = _dir(composer)
        if not d.exists():
            continue
        assert list(d.glob("*-lh-vocabulary.md")), f"{composer}: no *-lh-vocabulary.md"
        assert list(d.glob("*-devices.md")), f"{composer}: no *-devices.md"
