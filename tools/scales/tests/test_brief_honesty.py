"""The brief must not overstate the evidence behind it.

Composing "as Corelli" from **19 bars** is a different act from composing as
Mozart from 7,022, and the brief said so only obliquely — through scattered
"no corpus stats for texture X" warnings the agent had to add up for itself.
`composer_coverage_tier` had always known the answer; nothing put it in front
of the composer.

The same principle covers the texture-transition matrices: six of the nine
by-genre matrices have no armed member and are still **synthetic** — the
Classical matrix with hand-picked multipliers — so composing "in an
impressionist style" against them means composing against Mozart's texture
habits with a fudge factor applied. Passing that off as corpus evidence is how
a piece ends up in the wrong idiom with numbers that look supportive.
"""

from __future__ import annotations

import pytest

from scales.composition_brief import _coverage_note, composer_coverage_tier


def test_a_thin_corpus_is_declared_in_the_brief():
    note = _coverage_note("corelli")
    if not note.get("tier"):
        pytest.skip("corelli not present")
    assert note["tier"] in ("C", "D")
    assert "THIN" in note["advice"].upper() or "UNARMED" in note["advice"].upper()
    assert note["bars"] < 400


def test_a_rich_corpus_says_so_too():
    note = _coverage_note("mozart")
    if not note.get("tier"):
        pytest.skip("mozart not present")
    assert note["tier"] == "A"
    assert note["bars"] > 1500
    assert "THIN" not in note["advice"].upper()


def test_coverage_is_rendered_where_the_composer_will_read_it():
    """Near the top, not buried in the warnings block at the bottom."""
    import inspect

    from scales import composition_brief

    src = inspect.getsource(composition_brief.render_text)
    assert "CORPUS COVERAGE" in src
    header = src.index("COMPOSITION BRIEF")
    coverage = src.index("CORPUS COVERAGE")
    exemplars = src.find("EXEMPLARS")
    assert coverage > header
    if exemplars != -1:
        assert coverage < exemplars, (
            "coverage must be stated before the exemplars it qualifies"
        )


def test_an_unknown_composer_does_not_crash_the_coverage_note():
    note = _coverage_note("someone-nobody-has-armed")
    assert isinstance(note, dict)
    assert note.get("tier") in (None, "D")


def test_the_tier_thresholds_match_what_the_docstring_claims():
    """Tier A ≥1500 bars, B ≥400, C = some bars, D = none."""
    doc = composer_coverage_tier.__doc__ or ""
    assert "1500" in doc and "400" in doc
    for composer, expect in (("mozart", "A"), ("corelli", "C")):
        rep = composer_coverage_tier(composer)
        if not rep.get("bars"):
            continue
        assert rep["tier"] == expect, f"{composer} reported tier {rep['tier']}"


def test_synthetic_transition_data_is_declared_in_the_brief():
    import inspect

    from scales import composition_brief

    src = inspect.getsource(composition_brief._transition_patterns)
    assert "synthetic" in src.lower()
    assert "provenance" in src
    rendered = inspect.getsource(composition_brief.render_text)
    assert "provenance" in rendered, (
        "the synthetic-data warning is computed but never printed"
    )


# ─── Cadence doctrine must reach every armed composer ────────────────────────


def test_a_cadence_script_is_found_whatever_the_source_calls_it():
    """The lookup was a plain substring test on the label.

    A composer profile writes "HC (->V)"; the shared genre harmony files write
    "Half cadence"; the Renaissance file writes "Clausula vera". `"HC" in
    "HALF CADENCE"` is False, so five of the twelve armed composers got **no
    cadence script at all** — in the one place that addresses the single most
    reliable tell that a machine wrote the piece.
    """
    from scales.composition_brief import _cadence_matches

    assert _cadence_matches("HC", "HC (->V)")
    assert _cadence_matches("HC", "Half cadence")
    assert _cadence_matches("PAC", "Authentic (PAC)")
    assert _cadence_matches("PAC", "Authentic (perfect)")
    assert _cadence_matches("PAC", "Clausula vera")
    assert _cadence_matches("DC", "Deceptive")
    assert _cadence_matches("plagal", "Plagal")
    # and it must still discriminate
    assert not _cadence_matches("PAC", "Half cadence")
    assert not _cadence_matches("HC", "Plagal")
    assert not _cadence_matches("", "Half cadence")
    assert not _cadence_matches("HC", "")


def test_every_armed_composer_has_cadence_doctrine_for_the_common_cadences():
    """Five composers compiled to an empty `cadence_scripts.json` because the
    compiler never read the genre harmony file their profile delegates to."""
    import os
    from pathlib import Path

    from scales.composition_brief import _doctrine_slices
    from scales.models import PhraseSlot

    idx = Path("tools") / "reference_index"
    if not idx.is_dir():
        pytest.skip("corpus not present")
    armed = sorted(d for d in os.listdir(idx) if (idx / d).is_dir())

    missing = []
    for composer in armed:
        for cad in ("HC", "PAC"):
            slot = PhraseSlot(
                phrase_id="p", section_id="s", bar_start=1, bar_count=4,
                key="C major", meter=(4, 4), cadence_target=cad,
            )
            if not _doctrine_slices(composer, slot, "opening").get("cadence_script"):
                missing.append(f"{composer}/{cad}")
    assert not missing, (
        "armed composer(s) with no cadence doctrine for a common cadence: "
        f"{missing}"
    )


def test_every_armed_composer_has_real_fingerprints():
    """"COMPOSER FINGERPRINTS — the defining traits of this composer's voice"
    is the brief section the phrase-composer is told to make the phrase
    *exhibit*. Four armed composers — Corelli, Monteverdi, Palestrina and Weber
    — had no written profile at all, so the brief printed "no composer
    fingerprints for 'corelli'" and the phrase had nothing to be recognisably
    anyone's.
    """
    import json
    import os
    from pathlib import Path

    idx = Path("tools") / "reference_index"
    packs = Path("tools") / "compiled_packs"
    if not idx.is_dir() or not packs.is_dir():
        pytest.skip("corpus not present")

    thin = []
    for composer in sorted(d for d in os.listdir(idx) if (idx / d).is_dir()):
        path = packs / composer / "fingerprint_rules.json"
        if not path.exists():
            thin.append(f"{composer}: no fingerprint_rules.json")
            continue
        data = json.loads(path.read_text())
        items = data.get("items") if isinstance(data, dict) else data
        if len(items or []) < 3:
            thin.append(f"{composer}: {len(items or [])} fingerprints")
    assert not thin, (
        "armed composer(s) without enough fingerprints to make a phrase "
        f"recognisably theirs: {thin}"
    )
