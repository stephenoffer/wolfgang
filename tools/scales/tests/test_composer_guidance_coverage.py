"""Every armed composer must carry craft guidance the brief can read.

Two files per composer feed the brief directly: `<name>-lh-vocabulary.md` (what
the left hand actually plays, with real shorthand) and `<name>-devices.md` (the
idiomatic catalogue, parsed into `composer_device` pack entries). A composer
armed with thousands of bars but no guidance gets exemplars with no explanation
of what makes them his.

Six were missing both: satie, mussorgsky, rimsky-korsakov, weber, bruckner and
bartok — including satie at 913 bars and mussorgsky at 458.

The tests below check the two things a file-exists check misses: that the
catalogue actually PARSES into entries (the parser silently dropped items three
separate times before it was rewritten as a line walker), and that a document
whose corpus cannot support its claims says so.
"""

import glob
import re
from pathlib import Path

import pytest

_PROFILES = sorted(glob.glob(".claude/context/*/composer-profiles/*/"))


def _armed_composers():
    from scales.composition_brief import composer_coverage_tier

    out = []
    for d in sorted(glob.glob("tools/reference_index/*/")):
        name = Path(d.rstrip("/")).name
        if composer_coverage_tier(name).get("bars", 0) > 0:
            out.append(name)
    return out


def _profile_dir(composer):
    hits = glob.glob(f".claude/context/*/composer-profiles/{composer}/")
    return Path(hits[0]) if hits else None


@pytest.mark.parametrize("composer", _armed_composers())
def test_every_armed_composer_has_both_craft_documents(composer):
    d = _profile_dir(composer)
    if d is None:
        pytest.skip(f"{composer} has no profile directory")
    assert (d / f"{composer}-lh-vocabulary.md").exists(), f"{composer} has no LH vocabulary"
    assert (d / f"{composer}-devices.md").exists(), f"{composer} has no device catalogue"


@pytest.mark.parametrize("composer", _armed_composers())
def test_every_device_catalogue_parses_into_entries(composer):
    """A file that exists and parses to nothing is the worse failure.

    The catalogue parser dropped items silently three times — it required a dash
    after the bold name, its `^` could not match at a scan position sitting on a
    newline, and any item following an empty-bodied one vanished. Existence is
    not the check; yield is.
    """
    from scales.context_compiler import ContextCompiler

    d = _profile_dir(composer)
    if d is None or not (d / f"{composer}-devices.md").exists():
        pytest.skip(f"{composer} has no device catalogue")
    entries = ContextCompiler._composer_devices(d)
    assert len(entries) >= 10, f"{composer}'s catalogue yielded only {len(entries)} entries"
    assert all(e.get("name") and e.get("section") for e in entries)


@pytest.mark.parametrize("composer", _armed_composers())
def test_every_catalogue_says_what_to_avoid(composer):
    """The negative half is what stops the agent writing the wrong composer."""
    d = _profile_dir(composer)
    if d is None or not (d / f"{composer}-devices.md").exists():
        pytest.skip(f"{composer} has no device catalogue")
    text = (d / f"{composer}-devices.md").read_text()
    assert "What to avoid" in text, f"{composer}'s catalogue has no 'What to avoid' section"


# ─── Documents must not out-claim their corpus ───────────────────────────────

#: Composers whose armed corpus is too thin or too narrow to measure a habit
#: from. Their documents are craft knowledge and must say so, rather than
#: presenting knowledge as measurement.
_THIN = {"bruckner": 27, "bartok": 16, "weber": 241}


@pytest.mark.parametrize("composer,bars", sorted(_THIN.items()))
def test_a_thin_corpus_is_declared_in_the_document(composer, bars):
    """Weber's 241 bars are one CLARINET work, so measuring right-hand
    thickness on them returns a confident and meaningless 0% — which is why
    `voicing_profile` refuses him. A document that quietly presented craft
    knowledge as corpus measurement would be the same error in prose."""
    d = _profile_dir(composer)
    if d is None:
        pytest.skip(f"{composer} has no profile directory")
    for name in (f"{composer}-lh-vocabulary.md", f"{composer}-devices.md"):
        path = d / name
        if not path.exists():
            continue
        text = path.read_text().lower()
        assert "caveat" in text or "craft knowledge" in text, (
            f"{name} states habits from {bars} bars without declaring the corpus is thin"
        )


def test_shorthand_examples_use_the_real_grammar():
    """A vocabulary file's whole value is that its examples are playable."""
    from scales.direct_compose import _parse_shorthand

    bad = []
    for d in _PROFILES:
        for path in glob.glob(f"{d}*-lh-vocabulary.md"):
            for line in Path(path).read_text().splitlines():
                m = re.fullmatch(r"\s*`([^`]+)`\s*", line)
                if not m or "//" in m.group(1) and m.group(1).count("//") > 1:
                    continue
                try:
                    events = _parse_shorthand(m.group(1))
                except Exception as exc:
                    bad.append(
                        f"{Path(path).name}: {m.group(1)[:40]} -> {type(exc).__name__} {exc}"
                    )
                    continue
                if not events:
                    bad.append(f"{Path(path).name}: {m.group(1)[:40]} -> parsed to nothing")
    assert not bad, "unplayable shorthand in LH vocabulary docs:\n  " + "\n  ".join(bad[:12])


# ─── One composer, one profile directory ─────────────────────────────────────


def test_no_composer_has_two_profile_directories():
    """The compiler picks ONE and warns; the other half is unreachable.

    Rachmaninoff and Tchaikovsky each had their craft files in a different genre
    directory from the rest of their doctrine — rachmaninoff's devices under
    `late-romantic`, everything else under `romantic`. The compiler chose
    `romantic`, so **62 craft items across the two composers were written and
    zero compiled**. Both files existed, and a coverage check that globs
    `*/composer-profiles/<name>/` reported them present, which is how it went
    unnoticed: the files were there, just not where the compiler looks.

    Wagner's two directories hold genuinely different content and are a
    pre-existing editorial decision, so he is exempted by name rather than
    silently tolerated.
    """
    import collections

    seen = collections.defaultdict(list)
    for d in _PROFILES:
        seen[Path(d.rstrip("/")).name].append(Path(d.rstrip("/")).parent.parent.name)
    split = {n: g for n, g in seen.items() if len(g) > 1 and n != "wagner"}
    assert not split, (
        "a composer's doctrine is split across genre directories and the "
        f"compiler reads only one of them: {split}"
    )


@pytest.mark.parametrize("composer", ["rachmaninoff", "tchaikovsky"])
def test_the_reunited_craft_files_actually_compile(composer):
    """Existence was never the question — reaching the pack was."""
    import json
    import os

    path = f"tools/compiled_packs/{composer}/figuration_templates.json"
    if not os.path.exists(path):
        pytest.skip(f"{composer} pack not compiled")
    data = json.load(open(path))
    items = data if isinstance(data, list) else data.get("templates", [])
    devices = [i for i in items if isinstance(i, dict) and i.get("category") == "composer_device"]
    assert len(devices) >= 10, f"{composer} compiled only {len(devices)} devices"
