"""Canonical patterns must arrive in the key the brief says they are in.

`transpose_pattern` skipped any event whose pitch was a LIST — and left-hand
patterns are mostly chords and octaves. So the vocabulary printed under
"canonical chopin patterns, transposed to Eb major" was:

    [G2,G3]q [A2,A3]e [B2,B3]e [C3,C4]e [D3,D4]e [E3,E4]e [F3,F4]e

C major, with A/B/E natural — three pitch classes outside the key it was
labelled as, handed to the composer as material to use. Transposing to Eb, Bb
and A major all returned the input unchanged.

`pattern_to_events` delegates here, so the ENGINE's generated left hand was
untransposed in exactly the same way.

Second defect in the same section: 30 of 240 sampled patterns (12.5%) lie
entirely above middle C, including 9 of 40 `walking_bass` and 10 of 40
`pedal_point`. A left hand may sit high; a walking bass that never descends
below middle C contradicts its own label.
"""

import pytest

from scales.pattern_retriever import _BASS_TEXTURES, PatternRetriever, _reaches_the_bass
from scales.pitch import pitch_to_midi

MAJOR = {
    "C major": {0, 2, 4, 5, 7, 9, 11},
    "Eb major": {3, 5, 7, 8, 10, 0, 2},
    "A major": {9, 11, 1, 2, 4, 6, 8},
}


def _pcs(pattern):
    out = set()
    for e in pattern.get("lh_events", []):
        v = e.get("p")
        if not v or v == "rest":
            continue
        for name in v if isinstance(v, list) else [v]:
            m = pitch_to_midi(name)
            if m is not None:
                out.add(m % 12)
    return out


def _a_chord_pattern():
    pr = PatternRetriever()
    for texture in ("block_chord_sparse", "block_chord_offbeat", "oom_pah"):
        for p in pr.retrieve(texture, density_range=(1, 32), n=20):
            if any(isinstance(e.get("p"), list) for e in p.get("lh_events", [])):
                return pr, p
    raise AssertionError("no chord-bearing pattern in the library")


def test_a_chord_actually_moves():
    pr, p = _a_chord_pattern()
    before = _pcs(p)
    after = _pcs(pr.transpose_pattern(p, "C", "A major"))
    assert before != after, "chords fell through transposition untouched"


def test_transposing_to_different_keys_gives_different_notes():
    pr, p = _a_chord_pattern()
    eb = _pcs(pr.transpose_pattern(p, "C", "Eb major"))
    a = _pcs(pr.transpose_pattern(p, "C", "A major"))
    assert eb != a


def test_transposition_moves_every_note_by_the_same_interval():
    """The real contract, and the only one transposition can keep.

    This asserted that the result lands DIATONIC in the target key, which is a
    claim about the pattern rather than about transposing it. Corpus patterns
    are extracted from real music and are not diatonic in any assumed source
    key: the first chord-bearing `block_chord_sparse` pattern is a B-flat major
    chord, pitch classes {2, 5, 10}, and transposing it "from C" to E-flat gives
    {5, 8, 1} — outside E-flat, correctly, because the pattern was never in C.
    Landing in the key would require re-harmonising, which is what
    `_adapt_pattern_to_harmony` does and transposition does not.

    The assertion held only because the pattern it happened to pick was diatonic
    by luck; re-labelling the library changed which pattern that is and the luck
    ran out. A test that passes on the sample it drew is not a test of the rule.
    """
    pr, p = _a_chord_pattern()
    for key, expected_shift in (("Eb major", 3), ("A major", 9)):
        moved = pr.transpose_pattern(p, "C", key)
        shifts = set()
        for before, after in zip(p["lh_events"], moved["lh_events"]):
            b, a = before.get("p"), after.get("p")
            if not b or b == "rest":
                continue
            for one_before, one_after in zip(
                b if isinstance(b, list) else [b], a if isinstance(a, list) else [a]
            ):
                shifts.add((pitch_to_midi(one_after) - pitch_to_midi(one_before)) % 12)
        assert shifts == {expected_shift}, f"{key}: notes moved by {sorted(shifts)}"


def test_a_pattern_that_IS_diatonic_stays_diatonic():
    """The half of the original claim that survives: transposing a C-major
    pattern into another major key gives notes of that key."""
    pr = PatternRetriever()
    for texture in ("block_chord_sparse", "alberti", "walking_bass"):
        for candidate in pr.retrieve(texture, density_range=(1, 32), n=40):
            if _pcs(candidate) <= MAJOR["C major"]:
                for key in ("Eb major", "A major"):
                    out = _pcs(pr.transpose_pattern(candidate, "C", key))
                    assert out <= MAJOR[key], f"{key}: {sorted(out - MAJOR[key])} outside the key"
                return
    pytest.skip("no diatonic-in-C pattern found in the library")


def test_transposition_preserves_the_number_of_notes():
    """It moves notes; it must not lose or invent any."""
    pr, p = _a_chord_pattern()
    moved = pr.transpose_pattern(p, "C", "A major")
    assert len(moved["lh_events"]) == len(p["lh_events"])
    for a, b in zip(p["lh_events"], moved["lh_events"]):
        assert isinstance(a.get("p"), list) == isinstance(b.get("p"), list)
        if isinstance(a.get("p"), list):
            assert len(a["p"]) == len(b["p"])


def test_a_bass_texture_reaches_the_bass():
    pr = PatternRetriever()
    for texture in sorted(_BASS_TEXTURES):
        pats = pr.retrieve(texture, density_range=(1, 32), n=8)
        if not pats:
            continue
        assert any(_reaches_the_bass(p) for p in pats), texture


def test_the_grounding_preference_never_returns_nothing():
    """Fallback matters: no vocabulary is worse than an odd one.

    `_ensure_loaded()` is not optional here. A `PatternRetriever()` starts with
    an EMPTY `_by_texture`, so the guard below was false for every texture and
    this test executed **zero assertions** — it passed from the day it was
    written without checking anything.
    """
    pr = PatternRetriever()
    pr._ensure_loaded()
    stocked = [t for t in sorted(_BASS_TEXTURES) if pr._by_texture.get(t)]
    assert stocked, "no bass texture has patterns — the guard would be vacuous again"
    for texture in stocked:
        assert pr.retrieve(texture, density_range=(1, 32), n=3), texture
