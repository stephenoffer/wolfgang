#!/usr/bin/env python3
"""
Theme extractor and verifier for Wolfgang v2.

Extracts interval sequences from composed ABC and searches for
expected theme patterns. Used by /w-review to verify theme presence.

Usage:
    python3 theme_extractor.py <abc-file> <themes.json> <section-id>
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_notes_from_abc(abc_content: str) -> dict[str, list[int]]:
    """Extract note sequences per voice from ABC content.

    Returns dict of voice_id -> list of MIDI-like pitch numbers.
    """
    note_pattern = re.compile(
        r"([_=^]*)([a-gA-G])([,\']*)"
    )

    base_pitches = {
        'C': 48, 'D': 50, 'E': 52, 'F': 53, 'G': 55, 'A': 57, 'B': 59,
        'c': 60, 'd': 62, 'e': 64, 'f': 65, 'g': 67, 'a': 69, 'b': 71,
    }

    voices = {}
    current_voice = None

    for line in abc_content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('%'):
            continue

        # Check for voice marker
        voice_match = re.match(r'\[V:(\S+?)\](.*)', stripped)
        if voice_match:
            current_voice = voice_match.group(1)
            music = voice_match.group(2)
        elif stripped.startswith('V:'):
            current_voice = stripped.split()[0][2:]
            continue
        else:
            music = stripped

        if current_voice is None:
            current_voice = 'default'

        if current_voice not in voices:
            voices[current_voice] = []

        for match in note_pattern.finditer(music):
            accidental = match.group(1)
            note_name = match.group(2)
            octave_mod = match.group(3)

            pitch = base_pitches.get(note_name, 60)
            pitch += octave_mod.count("'") * 12
            pitch -= octave_mod.count(",") * 12
            if '^' in accidental:
                pitch += accidental.count('^')
            elif '_' in accidental:
                pitch -= accidental.count('_')

            voices[current_voice].append(pitch)

    return voices


def notes_to_intervals(notes: list[int]) -> list[int]:
    """Convert note sequence to interval sequence (semitone deltas)."""
    return [notes[i] - notes[i - 1] for i in range(1, len(notes))]


def find_pattern(haystack: list[int], needle: list[int], tolerance: int = 0) -> list[int]:
    """Find occurrences of an interval pattern in a larger sequence.

    Args:
        haystack: The full interval sequence to search
        needle: The pattern to find
        tolerance: Allow this many semitones difference per interval (for transposition)

    Returns:
        List of starting indices where the pattern was found
    """
    if not needle or not haystack or len(needle) > len(haystack):
        return []

    matches = []
    for i in range(len(haystack) - len(needle) + 1):
        is_match = True
        for j in range(len(needle)):
            if abs(haystack[i + j] - needle[j]) > tolerance:
                is_match = False
                break
        if is_match:
            matches.append(i)

    return matches


def verify_themes(abc_path: str, themes_path: str, section_id: str) -> dict:
    """Verify that expected themes are present in a composed section.

    Returns verification report.
    """
    abc_content = Path(abc_path).read_text()
    themes_data = json.loads(Path(themes_path).read_text())

    # Get expected themes for this section
    usage_plan = themes_data.get('usage_plan', {})
    expected = usage_plan.get(section_id, [])

    if not expected:
        return {
            'section_id': section_id,
            'expected_themes': [],
            'results': [],
            'all_found': True,
            'message': 'No themes expected in this section',
        }

    # Extract notes per voice from ABC
    voices = extract_notes_from_abc(abc_content)

    results = []
    for theme_ref in expected:
        parts = theme_ref.split(':')
        theme_name = parts[0]
        transformation = parts[1] if len(parts) > 1 else 'original'

        # Get theme data
        theme_data = themes_data.get('themes', {}).get(theme_name)
        if theme_name == 'connecting_motif':
            theme_data = themes_data.get('connecting_motif')

        if not theme_data:
            results.append({
                'theme': theme_ref,
                'found': False,
                'message': f'Theme {theme_name} not found in themes.json',
            })
            continue

        # Get the ABC for this transformation
        if transformation == 'original':
            theme_abc = theme_data.get('abc', '')
        elif '.' in transformation:
            # e.g., "fragmentation.head"
            parts2 = transformation.split('.')
            trans = theme_data.get('transformations', {}).get(parts2[0], {})
            if isinstance(trans, dict):
                theme_abc = trans.get(parts2[1], '')
            else:
                theme_abc = str(trans)
        else:
            theme_abc = theme_data.get('transformations', {}).get(transformation, '')

        if not theme_abc:
            results.append({
                'theme': theme_ref,
                'found': False,
                'message': f'No ABC found for transformation {transformation}',
            })
            continue

        # Extract interval pattern from theme
        theme_notes_dict = extract_notes_from_abc(theme_abc)
        theme_notes = []
        for v in theme_notes_dict.values():
            theme_notes.extend(v)

        if len(theme_notes) < 2:
            results.append({
                'theme': theme_ref,
                'found': False,
                'message': 'Theme too short to extract intervals',
            })
            continue

        theme_intervals = notes_to_intervals(theme_notes)

        # Search for this pattern in each voice
        found_in = []
        for voice_id, voice_notes in voices.items():
            if len(voice_notes) < 2:
                continue
            voice_intervals = notes_to_intervals(voice_notes)

            # Exact match
            matches = find_pattern(voice_intervals, theme_intervals, tolerance=0)
            if matches:
                found_in.append({
                    'voice': voice_id,
                    'positions': matches,
                    'match_type': 'exact',
                })

            # Transposed match (same intervals but shifted — already handled by interval comparison)
            # Near match (allow ±1 semitone per interval)
            if not matches:
                near_matches = find_pattern(voice_intervals, theme_intervals, tolerance=1)
                if near_matches:
                    found_in.append({
                        'voice': voice_id,
                        'positions': near_matches,
                        'match_type': 'near (±1 semitone)',
                    })

        results.append({
            'theme': theme_ref,
            'found': len(found_in) > 0,
            'found_in': found_in,
            'theme_intervals': theme_intervals[:10],  # truncate for readability
        })

    all_found = all(r['found'] for r in results)

    return {
        'section_id': section_id,
        'expected_themes': expected,
        'results': results,
        'all_found': all_found,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Verify theme presence in composed ABC'
    )
    parser.add_argument('abc_file', help='Path to composed ABC file')
    parser.add_argument('themes_json', help='Path to themes.json')
    parser.add_argument('section_id', help='Section ID to verify')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    report = verify_themes(args.abc_file, args.themes_json, args.section_id)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Theme verification for section: {report['section_id']}")
        print(f"Expected: {len(report['expected_themes'])} theme(s)")
        print()

        for r in report['results']:
            status = "FOUND" if r['found'] else "NOT FOUND"
            print(f"  [{status}] {r['theme']}")
            if r['found'] and r.get('found_in'):
                for f in r['found_in']:
                    print(f"    → Voice {f['voice']} at position(s) {f['positions']} ({f['match_type']})")
            elif not r['found']:
                print(f"    → {r.get('message', 'Pattern not detected in any voice')}")

        print(f"\nOverall: {'ALL FOUND' if report['all_found'] else 'MISSING THEMES'}")

    sys.exit(0 if report['all_found'] else 1)


if __name__ == '__main__':
    main()
