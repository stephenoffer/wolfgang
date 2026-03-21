#!/usr/bin/env python3
"""
Instrument range checker for Wolfgang v2.

Verifies all notes in a MusicXML or music21 Score are within
playable instrument ranges.

Usage:
    python3 range_checker.py <input.musicxml>
"""

import argparse
import sys
from pathlib import Path

from music21 import converter, pitch


# Instrument ranges as (lowest_midi, highest_midi)
# Using concert pitch for all
RANGES = {
    # Strings
    'Violin': (55, 103),       # G3 to G7
    'Viola': (48, 88),         # C3 to E6
    'Violoncello': (36, 81),   # C2 to A5
    'Contrabass': (28, 67),    # E1 to G4

    # Woodwinds (concert pitch)
    'Flute': (60, 98),         # C4 to D7
    'Oboe': (58, 93),          # Bb3 to A6
    'Clarinet': (50, 94),      # D3 to Bb6 (concert: concert Bb2 to Ab6)
    'Clarinet in B-flat': (50, 94),
    'Bassoon': (34, 75),       # Bb1 to Eb5

    # Brass (concert pitch)
    'Horn': (35, 77),          # B1 to F5
    'Horn in F': (35, 77),
    'French Horn': (35, 77),
    'Trumpet': (52, 82),       # E3 to Bb5
    'Trumpet in B-flat': (52, 82),
    'Trombone': (40, 72),      # E2 to C5
    'Tuba': (26, 65),          # D1 to F4

    # Percussion
    'Timpani': (36, 60),       # C2 to C4

    # Keyboard
    'Piano': (21, 108),        # A0 to C8
    'Harpsichord': (29, 89),   # F1 to F6
    'Celesta': (60, 108),      # C4 to C8
    'Organ': (24, 108),        # C1 to C8

    # Other
    'Harp': (24, 103),         # C1 to G7

    # Extended woodwinds
    'Piccolo': (74, 108),      # D5 to C8
    'English Horn': (52, 84),  # E3 to C6
    'Bass Clarinet': (38, 82), # D2 to Bb5
    'Contrabassoon': (22, 60), # Bb0 to C4
}


def check_ranges(musicxml_path: str) -> list[dict]:
    """Check all notes against instrument ranges.

    Returns list of violations.
    """
    score = converter.parse(musicxml_path)
    violations = []

    for part in score.parts:
        part_name = part.partName or 'Unknown'

        # Find the instrument
        instruments = list(part.getInstruments())
        inst_name = instruments[0].instrumentName if instruments else part_name

        # Look up range
        range_bounds = None
        for range_name, bounds in RANGES.items():
            if range_name.lower() in inst_name.lower() or inst_name.lower() in range_name.lower():
                range_bounds = bounds
                break

        if range_bounds is None:
            # Try partial matching
            for range_name, bounds in RANGES.items():
                if any(word in inst_name.lower() for word in range_name.lower().split()):
                    range_bounds = bounds
                    break

        if range_bounds is None:
            continue  # Can't check unknown instrument

        low, high = range_bounds

        # Check every note
        for n in part.recurse().notes:
            if hasattr(n, 'pitches'):
                # Chord
                for p in n.pitches:
                    midi = p.midi
                    if midi < low or midi > high:
                        measure = n.measureNumber or 0
                        violations.append({
                            'part': part_name,
                            'instrument': inst_name,
                            'measure': measure,
                            'note': str(p),
                            'midi': midi,
                            'range': f"{pitch.Pitch(midi=low)} to {pitch.Pitch(midi=high)}",
                            'direction': 'too low' if midi < low else 'too high',
                        })
            elif hasattr(n, 'pitch'):
                midi = n.pitch.midi
                if midi < low or midi > high:
                    measure = n.measureNumber or 0
                    violations.append({
                        'part': part_name,
                        'instrument': inst_name,
                        'measure': measure,
                        'note': str(n.pitch),
                        'midi': midi,
                        'range': f"{pitch.Pitch(midi=low)} to {pitch.Pitch(midi=high)}",
                        'direction': 'too low' if midi < low else 'too high',
                    })

    return violations


def main():
    parser = argparse.ArgumentParser(
        description='Check instrument ranges in MusicXML'
    )
    parser.add_argument('input', help='Input MusicXML file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    violations = check_ranges(args.input)

    if args.json:
        import json
        print(json.dumps({'violations': violations, 'count': len(violations)}, indent=2))
    else:
        if violations:
            print(f"Range violations in {args.input}:")
            for v in violations:
                print(f"  {v['part']} ({v['instrument']}), "
                      f"measure {v['measure']}: "
                      f"{v['note']} is {v['direction']} "
                      f"(range: {v['range']})")
            print(f"\n{len(violations)} violation(s) found")
        else:
            print(f"Range check: OK — {args.input}")

    sys.exit(1 if violations else 0)


if __name__ == '__main__':
    main()
