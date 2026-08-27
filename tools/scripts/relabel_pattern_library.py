"""Re-derive every canonical pattern's `lh_texture` from its own notes.

The pattern library was labelled under an older texture vocabulary and never
rebuilt when the corpus was. Measured against the labels the classifier gives
those same patterns today, only **22%** agree, and the vocabularies have drifted
apart in both directions:

    6,519 of 24,615 patterns (26%) carry a label the corpus no longer produces
        unclassified 3753   sparse_punctuation 734   broken_chord_descending 532
        broken_chord_ascending 441   walking_bass_chromatic 414
        sparse_octaves 331   oscillation_trill 314

    three labels the corpus DOES produce have zero patterns, so a request for
    any of them retrieves nothing at all:
        broken_chord_asc   broken_chord_desc   interlocking

`broken_chord_ascending` and `broken_chord_asc` are the same idiom under a
rename: 973 patterns were unreachable under the name the planner asks for, and
retrieval fell back to whatever else it could find. This is the shape recorded
as `project_dead_label_vocabulary` — readers were updated, the stored data was
not, and every lookup missed silently.

Re-labelling rather than re-extracting: the patterns' NOTES are fine (they carry
3.97 distinct pitches against the corpus bars' 3.25), it is only what they are
called that went stale. The classifier is the one `build_full_corpus` runs on
every corpus bar, so a pattern and a bar are named the same way afterwards.

Usage:
    .venv/bin/python -m scripts.relabel_pattern_library          # rewrite
    .venv/bin/python -m scripts.relabel_pattern_library --dry-run
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from scales.atomic_io import write_json_atomic
from scales.pitch import pitch_to_midi

from scripts.build_full_corpus import _classify_lh_texture

_CANONICAL = Path(__file__).resolve().parent.parent / "pattern_library" / "canonical"

#: A pattern stores no metre, so its own total duration is the only signal for
#: how many beats its bar held. Anything else keeps 4/4, which is what the
#: classifier assumes by default.
_METER_FOR_DURATION = {
    1.5: (3, 8),
    2.0: (2, 4),
    3.0: (3, 4),
    4.0: (4, 4),
    6.0: (6, 8),
    8.0: (4, 2),
    12.0: (12, 8),
}


def classify_pattern(pattern: Dict[str, Any]) -> Optional[str]:
    """The texture label this pattern's own notes earn from today's classifier."""
    import music21

    notes: List[Any] = []
    offset = 0.0
    for event in pattern.get("lh_events") or []:
        pitch = event.get("p")
        duration = float(event.get("d", 0.25) or 0.25)
        if not pitch or pitch == "rest":
            offset += duration
            continue
        raw = pitch if isinstance(pitch, list) else [pitch]
        midis = []
        for one in raw:
            try:
                midis.append(pitch_to_midi(one))
            except (ValueError, KeyError, TypeError):
                continue
        midis = [m for m in midis if m is not None]
        if not midis:
            offset += duration
            continue
        if len(midis) > 1:
            note = music21.chord.Chord(midis)
        else:
            note = music21.note.Note()
            note.pitch.midi = midis[0]
        note.quarterLength = duration
        note.offset = offset
        offset += duration
        notes.append(note)
    if not notes:
        return None
    total = round(float(pattern.get("duration_total") or 0), 3)
    meter = _METER_FOR_DURATION.get(total, (4, 4))
    return _classify_lh_texture(notes, meter)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    dry_run = "--dry-run" in argv

    shards = sorted(_CANONICAL.glob("*.json"))
    if not shards:
        print(json.dumps({"error": f"no pattern shards under {_CANONICAL}"}))
        return 1

    changed = kept = skipped = 0
    moves: Counter = Counter()
    after: Counter = Counter()
    for shard in shards:
        patterns = json.loads(shard.read_text())
        for pattern in patterns.values():
            label = classify_pattern(pattern)
            if label is None:
                skipped += 1
                continue
            after[label] += 1
            was = pattern.get("lh_texture")
            if label == was:
                kept += 1
                continue
            moves[(was, label)] += 1
            changed += 1
            pattern["lh_texture"] = label
        if not dry_run:
            write_json_atomic(shard, patterns, indent=None)

    print(
        json.dumps(
            {
                "dry_run": dry_run,
                "patterns": changed + kept + skipped,
                "relabelled": changed,
                "unchanged": kept,
                "no_notes": skipped,
                "top_moves": [{"from": a, "to": b, "n": n} for (a, b), n in moves.most_common(10)],
                "labels_after": dict(after.most_common()),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
