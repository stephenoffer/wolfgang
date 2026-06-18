#!/usr/bin/env python3
"""
Build comprehensive corpus from all available sources:
1. Existing reference_scores/ kern files (224 files: Mozart, Beethoven, Chopin)
2. music21 built-in corpus (433 Bach, 26 Beethoven, 16 Mozart, 9 Haydn)
3. Extract bar indices for all composers found
4. Build patterns and add to the pattern library

This script extends the corpus beyond the original 3 composers.
"""

import json
import os
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REF_INDEX = BASE / "reference_index"
REF_INDEX.mkdir(exist_ok=True)


def analyze_score_bars(score, composer, source_name):
    """Extract bar-level data from a music21 score, matching the existing bar_index format."""
    from music21 import stream

    bars = []
    parts = list(score.parts)
    if not parts:
        return bars

    # For keyboard: assume part 0 = RH, part 1 = LH (or only part if 1 part)
    # For SATB: combine all as melody analysis
    rh_part = parts[0]
    lh_part = parts[1] if len(parts) > 1 else None

    measures_rh = list(rh_part.getElementsByClass(stream.Measure))

    for mi, measure in enumerate(measures_rh):
        bar_num = measure.number if measure.number else mi + 1

        # RH analysis
        rh_notes = list(measure.recurse().notes)
        rh_density = len(rh_notes)

        # Melody direction
        rh_midis = [n.pitch.midi for n in rh_notes if hasattr(n, "pitch")]
        if len(rh_midis) >= 2:
            if rh_midis[-1] > rh_midis[0] + 2:
                direction = "ascending"
            elif rh_midis[-1] < rh_midis[0] - 2:
                direction = "descending"
            else:
                direction = "static"
        else:
            direction = "static"

        # RH texture classification (simplified)
        if rh_density <= 2:
            rh_texture = "held_note"
        elif rh_density <= 4:
            rh_texture = "singing_melody"
        elif rh_density <= 8:
            rh_texture = (
                "singing_melody" if any(hasattr(n, "pitch") for n in rh_notes) else "chordal"
            )
        elif rh_density <= 12:
            rh_texture = "scalar_run"
        else:
            rh_texture = "zigzag_figuration"

        # Grace notes and dotted rhythms
        has_grace = any(n.duration.isGrace for n in rh_notes if hasattr(n, "duration"))
        has_dotted = any(n.duration.dots > 0 for n in rh_notes if hasattr(n, "duration"))

        # LH analysis
        lh_density = 0
        lh_texture = "silence"
        lh_display = []

        if lh_part:
            lh_measures = list(lh_part.getElementsByClass(stream.Measure))
            if mi < len(lh_measures):
                lh_measure = lh_measures[mi]
                lh_notes = list(lh_measure.recurse().notes)
                lh_density = len(lh_notes)

                # LH texture classification
                if lh_density == 0:
                    lh_texture = "silence"
                elif lh_density <= 2:
                    lh_texture = "pedal_point"
                elif lh_density <= 4:
                    lh_texture = "bass_melody"
                elif lh_density <= 8:
                    # Check for broken chord patterns
                    lh_midis_all = [n.pitch.midi for n in lh_notes if hasattr(n, "pitch")]
                    if lh_midis_all:
                        span = max(lh_midis_all) - min(lh_midis_all)
                        if span <= 12:
                            lh_texture = "alberti"
                        else:
                            lh_texture = "broken_chord_wave"
                    else:
                        lh_texture = "block_chord_sparse"
                elif lh_density <= 16:
                    lh_texture = "alberti"
                else:
                    lh_texture = "walking_bass"

                # LH display data
                for n in lh_notes[:16]:
                    if hasattr(n, "pitch"):
                        lh_display.append(
                            {
                                "type": "note",
                                "pitch": n.nameWithOctave,
                                "dur": round(n.quarterLength, 4),
                                "is_grace": n.duration.isGrace
                                if hasattr(n.duration, "isGrace")
                                else False,
                            }
                        )
                    elif hasattr(n, "pitches"):  # chord
                        lh_display.append(
                            {
                                "type": "chord",
                                "pitches": [p.nameWithOctave for p in n.pitches],
                                "dur": round(n.quarterLength, 4),
                            }
                        )

        # Key detection
        try:
            k = measure.analyze("key")
            key_name = k.tonic.name if k.tonic else "C"
            key_mode = k.mode if k.mode else "major"
        except Exception:
            key_name = "C"
            key_mode = "major"

        # Register center
        register = sum(rh_midis) / len(rh_midis) if rh_midis else 60

        # Phrase position (simplified)
        total_bars = len(measures_rh)
        if mi < 2:
            position = "opening"
        elif mi >= total_bars - 2:
            position = "closing"
        elif mi >= total_bars - 4:
            position = "cadential"
        else:
            position = "middle"

        bar_data = {
            "source": source_name,
            "bar_num": bar_num,
            "key": key_name,
            "key_mode": key_mode,
            "phrase_position": position,
            "melody_density": rh_density,
            "accomp_density": lh_density,
            "rh_texture": rh_texture,
            "lh_texture": lh_texture,
            "melody_direction": direction,
            "has_grace_notes": has_grace,
            "has_dotted_rhythms": has_dotted,
            "register_center": round(register),
            "harmony_quality": key_mode,
            "lh_display": lh_display,
        }
        bars.append(bar_data)

    return bars


def process_music21_corpus():
    """Extract bars from all music21 built-in corpus files."""
    from music21 import converter, corpus

    composers_to_process = {
        "bach": "baroque",
        "haydn": "classical",
    }

    results = {}

    for composer, genre in composers_to_process.items():
        print(f"\n=== Processing {composer} (music21 corpus) ===")
        try:
            paths = corpus.getComposer(composer)
        except Exception:
            print(f"  No corpus data for {composer}")
            continue

        all_bars = []
        processed = 0
        errors = 0

        for path in paths:
            path_str = str(path)
            # Skip non-score files
            if not (
                path_str.endswith(".mxl") or path_str.endswith(".xml") or path_str.endswith(".krn")
            ):
                continue

            try:
                score = converter.parse(path_str)
                source_name = (
                    os.path.basename(os.path.dirname(path_str))
                    + "/"
                    + os.path.basename(path_str).replace(".mxl", "").replace(".krn", "")
                )
                bars = analyze_score_bars(score, composer, source_name)
                all_bars.extend(bars)
                processed += 1
                if processed % 20 == 0:
                    print(f"  Processed {processed} files, {len(all_bars)} bars...")
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"  Error parsing {os.path.basename(path_str)}: {e}")

        if all_bars:
            # Save bar index
            bar_index = {
                "composer": composer,
                "total_bars": len(all_bars),
                "source_files": processed,
                "bars": all_bars,
            }
            out_path = REF_INDEX / f"{composer}_bar_index.json"
            with open(out_path, "w") as f:
                json.dump(bar_index, f, separators=(",", ":"))
            print(
                f"  Saved: {out_path} ({len(all_bars)} bars from {processed} files, {errors} errors)"
            )
            results[composer] = len(all_bars)
        else:
            print(f"  No bars extracted for {composer}")

    return results


def main():
    t0 = time.time()
    print("=== Building Full Corpus ===\n")

    # Phase 1: Process music21 corpus for new composers
    results = process_music21_corpus()

    # Phase 2: Summary
    elapsed = time.time() - t0
    print(f"\n=== COMPLETE ({elapsed:.0f}s) ===")
    print("New bar indices created:")
    for composer, count in results.items():
        print(f"  {composer}: {count} bars")

    # Show what we now have
    print("\nAll bar indices in reference_index/:")
    for f in sorted(REF_INDEX.glob("*_bar_index.json")):
        size = os.path.getsize(f) / 1024 / 1024
        print(f"  {f.name}: {size:.1f} MB")


if __name__ == "__main__":
    main()
