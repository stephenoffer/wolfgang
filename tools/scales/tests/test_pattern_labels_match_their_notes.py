"""A retrieved pattern must actually be the idiom that was asked for.

The pattern library was labelled under an older texture vocabulary and never
rebuilt when the corpus was. Re-classifying each pattern's own notes with the
classifier the corpus uses today, only **22%** agreed with the stored label, and
the vocabularies had drifted apart in both directions:

    6,519 of 24,615 patterns (26%) carried a label the corpus no longer emits
        unclassified 3753   sparse_punctuation 734   broken_chord_descending 532
        broken_chord_ascending 441   walking_bass_chromatic 414
        sparse_octaves 331   oscillation_trill 314

    three labels the corpus DOES emit had zero patterns, so asking for any of
    them retrieved nothing at all:
        broken_chord_asc   broken_chord_desc   interlocking

`broken_chord_ascending` and `broken_chord_asc` are one idiom under a rename:
973 patterns were unreachable by the name the planner asks for. This is the
shape recorded as `project_dead_label_vocabulary` — readers were updated, the
stored data was not, and every lookup missed silently. It is also why a peer
session's three scheduler changes moved nothing: the plan asked for
`broken_chord_wave` in 68% of a Chopin piece, retrieval honoured the request
every time, and the notes that came back were something else.

`scripts/relabel_pattern_library.py` re-derives the label from each pattern's
own notes. Retrieval now returns the requested idiom 55 times out of 55.
"""

from __future__ import annotations

import collections

import pytest
from scripts.build_full_corpus import _classify_lh_texture

from scales.pattern_retriever import PatternRetriever
from scales.pitch import pitch_to_midi

_METER = {
    1.5: (3, 8),
    2.0: (2, 4),
    3.0: (3, 4),
    4.0: (4, 4),
    6.0: (6, 8),
    8.0: (4, 2),
    12.0: (12, 8),
}


def _classify(pattern):
    import music21

    notes, offset = [], 0.0
    for event in pattern.get("lh_events") or []:
        pitch = event.get("p")
        duration = float(event.get("d", 0.25) or 0.25)
        if not pitch or pitch == "rest":
            offset += duration
            continue
        raw = pitch if isinstance(pitch, list) else [pitch]
        midis = [pitch_to_midi(x) for x in raw if x]
        midis = [m for m in midis if m is not None]
        if not midis:
            offset += duration
            continue
        note = music21.chord.Chord(midis) if len(midis) > 1 else music21.note.Note()
        if len(midis) == 1:
            note.pitch.midi = midis[0]
        note.quarterLength = duration
        note.offset = offset
        offset += duration
        notes.append(note)
    if not notes:
        return None
    return _classify_lh_texture(
        notes, _METER.get(round(float(pattern.get("duration_total") or 0), 3), (4, 4))
    )


def test_the_classifier_harness_reproduces_the_corpus_labels():
    """The precondition, before this file is allowed to judge anything.

    A first version of this measurement said `broken_chord_wave` patterns
    classify as `alberti` before any adaptation — a confident, plausible,
    entirely wrong answer produced by a harness that read the wrong fields. It
    agreed with the corpus's own labels 0% of the time, which is what caught it.
    No probe reported until it reproduces a number someone already holds.
    """
    import music21
    from scripts.build_corpus_indexes import load_bars

    agree = collections.Counter()
    for bar in load_bars("mozart")[:400]:
        meter, stored = bar.get("time_sig"), bar.get("lh_texture")
        if not meter or not stored:
            continue
        notes, offset = [], 0.0
        for event in bar.get("lh_display") or []:
            duration = float(event.get("dur", 0.25) or 0.25)
            if event.get("type") == "rest":
                offset += duration
                continue
            raw = event.get("pitches") if event.get("type") == "chord" else [event.get("pitch")]
            midis = [pitch_to_midi(p) for p in (raw or []) if p]
            midis = [m for m in midis if m is not None]
            if not midis:
                offset += duration
                continue
            note = music21.chord.Chord(midis) if len(midis) > 1 else music21.note.Note()
            if len(midis) == 1:
                note.pitch.midi = midis[0]
            note.quarterLength = duration
            note.offset = offset
            offset += duration
            notes.append(note)
        agree[_classify_lh_texture(notes, tuple(meter)) == stored] += 1
    total = sum(agree.values())
    if total < 100:
        pytest.skip("corpus not available")
    assert agree[True] / total > 0.9, (
        f"the harness reproduces the corpus's own labels only {agree[True] / total:.0%} "
        "of the time — nothing it says about the pattern library can be trusted"
    )


def test_retrieval_returns_the_idiom_that_was_asked_for():
    retriever = PatternRetriever()
    retriever._ensure_loaded()
    wrong = []
    for texture in sorted(retriever._by_texture):
        if texture == "silence":
            continue
        for pattern in retriever.retrieve(texture, n=5):
            got = _classify(pattern)
            if got is not None and got != texture:
                wrong.append(f"asked {texture}, got {got}")
    assert not wrong, "retrieval returns a different idiom than requested:\n  " + "\n  ".join(
        wrong[:10]
    )


def test_no_pattern_carries_a_label_the_corpus_no_longer_produces():
    from scripts.build_corpus_indexes import load_bars

    current = set()
    for composer in ("mozart", "beethoven", "chopin", "haydn", "bach"):
        current |= {b.get("lh_texture") for b in load_bars(composer) if b.get("lh_texture")}
    if not current:
        pytest.skip("corpus not available")
    retriever = PatternRetriever()
    retriever._ensure_loaded()
    stale = {k: len(v) for k, v in retriever._by_texture.items() if k not in current}
    assert not stale, (
        f"pattern label(s) the corpus no longer emits: {stale}. A planner asking "
        "for a current label cannot reach these, and retrieval falls back to "
        "whatever else it can find — silently."
    )


def test_every_idiom_the_corpus_produces_can_be_retrieved():
    """The other direction: `broken_chord_asc` had zero patterns and returned
    nothing, while 441 sat under `broken_chord_ascending`."""
    from scripts.build_corpus_indexes import load_bars

    current = {b.get("lh_texture") for b in load_bars("mozart") if b.get("lh_texture")}
    current.discard("silence")
    if not current:
        pytest.skip("corpus not available")
    retriever = PatternRetriever()
    empty = [t for t in sorted(current) if not retriever.retrieve(t, n=1)]
    assert not empty, f"idiom(s) the corpus produces that retrieve nothing: {empty}"
