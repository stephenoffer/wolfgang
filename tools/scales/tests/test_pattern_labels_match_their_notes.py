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


# ─── A bar is not the average of bars ────────────────────────────────────────


def test_retrieval_matches_the_real_MEDIAN_BAR_of_each_idiom():
    """Real accompaniment bars are BIMODAL, and the aggregate describes none.

        idiom                  mean   median   bars 0%   bars 100%
        block_chord_offbeat   82.2%   100.0%        7%         61%
        alberti                2.1%     0.0%       94%          1%

    So `block_chord_offbeat` "is 83.8% chorded" is an attack-weighted average
    across bars, and no single bar looks like it — 61% of them are entirely
    chords. A generator writes ONE bar at a time, so the median bar is what it
    should resemble. Both of us spent an exchange scoring retrieval against the
    mean and reading a 16-point error that was the yardstick.

    This is the aggregate-versus-member correction one level below the movement:
    a bar is not the average of bars, exactly as a movement is not the average
    of movements.
    """
    import statistics

    from scripts.build_corpus_indexes import load_bars

    real = collections.defaultdict(list)
    for composer in ("mozart", "beethoven", "chopin", "haydn", "bach"):
        for bar in load_bars(composer):
            idiom = bar.get("lh_texture")
            events = [e for e in (bar.get("lh_display") or []) if e.get("type") != "rest"]
            if not idiom or not events:
                continue
            real[idiom].append(sum(1 for e in events if e.get("type") == "chord") / len(events))
    if not real:
        pytest.skip("corpus not available")

    from scales.pattern_retriever import _chord_share

    retriever = PatternRetriever()
    retriever._ensure_loaded()
    wrong = []
    for idiom, shares in real.items():
        if len(shares) < 200 or idiom == "silence":
            continue
        got = retriever.retrieve(idiom, n=5)
        if not got:
            continue
        mine = statistics.median(_chord_share(p) for p in got)
        theirs = statistics.median(shares)
        if abs(mine - theirs) > 0.25:
            wrong.append(f"{idiom}: retrieved {mine:.0%} vs real median bar {theirs:.0%}")
    assert not wrong, (
        "retrieved patterns do not resemble a real bar of their idiom:\n  " + "\n  ".join(wrong)
    )


def test_a_preference_is_not_applied_after_a_cap():
    """The candidate list was truncated to `n * 3` BEFORE the ranking ran.

    Those fifteen came from the front of a pool sorted by frequency — chosen by
    exactly the criterion the ranking exists to override — so adding a chord
    preference moved `block_chord_offbeat` not at all until the cap came off. A
    cap applied before a preference is a preference that does not apply.
    """
    # Tested by BEHAVIOUR, not by looking for "n * 3" in the source — a first
    # version did that and failed on the comment explaining the fix. Source-text
    # assertions are recorded elsewhere in this repo as a thing not to do, and
    # this is the second way they go wrong: the prose describing a defect
    # contains the defect's own text.
    from scales.pattern_retriever import PatternRetriever as PR

    r = PR()
    r._ensure_loaded()
    pool = r._by_texture["block_chord_offbeat"]
    assert len(pool) > 100
    got = r.retrieve("block_chord_offbeat", n=5)
    positions = [pool.index(p) for p in got if p in pool]
    assert max(positions) > 15, (
        f"every retrieved pattern came from the first 15 of {len(pool)}: {positions}"
    )
