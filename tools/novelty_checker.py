#!/usr/bin/env python3
"""
Theme novelty checker for Wolfgang v2.

Compares generated themes against a database of known classical melodies
using interval sequence edit distance and Parsons code (melodic contour).

Usage:
    python3 novelty_checker.py <themes.json> [--threshold 0.7] [--index <famous-themes-index.md>]
"""

import argparse
import json
import re
import sys
from pathlib import Path


# Well-known classical theme interval patterns (semitone deltas)
# Format: (name, intervals, rhythm_hint)
FAMOUS_THEMES = [
    ("Beethoven 5th - Opening", [0, 0, -3, 0, 0, -4], "short-short-short-long"),
    ("Beethoven 9th - Ode to Joy", [0, 2, 2, 0, -2, -2, -1, 0, 0, 2, 2, 1, 0], "even"),
    ("Mozart 40 - Opening", [0, -1, 0, -1, 0, 3, 0, -1, 0, -1], "short-short-long"),
    ("Tchaikovsky PC1 - Opening", [0, 2, 0, -2, 0, 2, 0, 0], "broad"),
    ("Rachmaninoff PC2 - Theme", [-2, -1, -2, 5, -2, -1, -2, 3], "lyrical"),
    ("Rachmaninoff PC3 - Opening", [0, -2, -1, 3, -1, -2, 0, 2], "flowing"),
    ("Dvorak 9 - Largo", [3, 2, -2, -3, 3, 2, 5, -2], "slow-broad"),
    ("Grieg PC - Opening", [-1, -2, -2, -1, -2, -2, -5], "descending"),
    ("Tchaikovsky 6 - Theme", [2, 2, 1, 2, -3, 2, 2, -2], "lyrical"),
    ("Chopin Ballade 1 - Theme", [0, 5, -1, -2, 2, -2, -1, 5], "rubato"),
    ("Bach Toccata Dm", [0, -1, 0, -2, -2, -1, 0, -3], "virtuosic"),
    ("Brahms 1 - Finale", [0, 2, 2, 1, 2, 2, 2, -2], "hymn-like"),
    ("Schubert Unfinished - Theme", [-3, 2, 2, 2, -2, -2, -3], "lyrical"),
    ("Mahler 5 - Adagietto", [0, 4, 3, -1, -2, -1, 3], "yearning"),
    ("Debussy Clair de Lune", [0, 0, 2, 2, -2, 0, -2, -2], "floating"),
    ("Ravel Bolero", [0, 2, 0, -2, 2, 0, 2, 2, -2], "repetitive"),
    ("Sibelius 2 - Finale", [0, 2, 2, 3, 0, -3, -2, -2, 5], "heroic"),
    ("Barber Adagio", [2, 1, 2, 2, -2, -1, -2, 3], "lamenting"),
]


def extract_intervals_from_abc(abc_str: str) -> list[int]:
    """Extract interval sequence (semitone deltas) from ABC notation."""
    # Parse ABC notes
    note_pattern = re.compile(
        r"([_=^]*)([a-gA-G])([,\']*)([\d]*/?[\d]*)"
    )

    notes = []
    for match in note_pattern.finditer(abc_str):
        accidental = match.group(1)
        note_name = match.group(2)
        octave_mod = match.group(3)

        # Convert to MIDI-like pitch number
        base_pitches = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
            'c': 12, 'd': 14, 'e': 16, 'f': 17, 'g': 19, 'a': 21, 'b': 23,
        }
        pitch = base_pitches.get(note_name, 0)

        # Apply octave modifications
        pitch += octave_mod.count("'") * 12
        pitch -= octave_mod.count(",") * 12

        # Apply accidentals
        if '^' in accidental:
            pitch += accidental.count('^')
        elif '_' in accidental:
            pitch -= accidental.count('_')

        notes.append(pitch)

    # Compute intervals
    intervals = []
    for i in range(1, len(notes)):
        intervals.append(notes[i] - notes[i - 1])

    return intervals


def parsons_code(intervals: list[int]) -> str:
    """Convert interval sequence to Parsons code (U/D/R)."""
    code = []
    for i in intervals:
        if i > 0:
            code.append('U')
        elif i < 0:
            code.append('D')
        else:
            code.append('R')
    return ''.join(code)


def edit_distance(seq1: list, seq2: list) -> int:
    """Compute Levenshtein edit distance between two sequences."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )

    return dp[m][n]


def similarity(seq1: list, seq2: list) -> float:
    """Compute similarity score (0.0 to 1.0) between two sequences."""
    if not seq1 or not seq2:
        return 0.0
    max_len = max(len(seq1), len(seq2))
    if max_len == 0:
        return 1.0
    dist = edit_distance(seq1, seq2)
    return 1.0 - (dist / max_len)


def check_novelty(themes_data: dict, threshold: float = 0.7) -> list[dict]:
    """Check all themes against known melodies.

    Returns list of flagged issues.
    """
    flags = []
    themes = themes_data.get('themes', {})

    # Also check connecting motif
    if 'connecting_motif' in themes_data:
        themes['_connecting_motif'] = themes_data['connecting_motif']

    for theme_name, theme_data in themes.items():
        abc = theme_data.get('abc', '')
        if not abc:
            continue

        intervals = extract_intervals_from_abc(abc)
        if len(intervals) < 3:
            continue

        contour = parsons_code(intervals)

        # Check against famous themes
        for known_name, known_intervals, known_rhythm in FAMOUS_THEMES:
            # Interval similarity
            int_sim = similarity(intervals, known_intervals)

            # Contour similarity
            known_contour = parsons_code(known_intervals)
            contour_sim = similarity(list(contour), list(known_contour))

            # Combined score (interval is more important)
            combined = 0.6 * int_sim + 0.4 * contour_sim

            if combined >= threshold:
                flags.append({
                    'theme': theme_name,
                    'similar_to': known_name,
                    'interval_similarity': round(int_sim, 3),
                    'contour_similarity': round(contour_sim, 3),
                    'combined_score': round(combined, 3),
                    'suggestion': f"Alter the opening intervals or change the melodic contour. "
                                  f"Current contour: {contour[:10]}. "
                                  f"Similar to: {known_contour[:10]}",
                })

    return flags


def main():
    parser = argparse.ArgumentParser(
        description='Check theme novelty against known classical melodies'
    )
    parser.add_argument('themes_json', help='Path to themes.json')
    parser.add_argument(
        '--threshold', '-t', type=float, default=0.7,
        help='Similarity threshold for flagging (0.0-1.0, default: 0.7)'
    )

    args = parser.parse_args()

    try:
        themes_path = Path(args.themes_json)
        themes_data = json.loads(themes_path.read_text())
    except Exception as e:
        print(f"Error reading themes: {e}", file=sys.stderr)
        sys.exit(1)

    flags = check_novelty(themes_data, args.threshold)

    if flags:
        print(f"NOVELTY CHECK: {len(flags)} potential similarity issue(s) found:\n")
        for flag in flags:
            print(f"  Theme: {flag['theme']}")
            print(f"  Similar to: {flag['similar_to']}")
            print(f"  Score: {flag['combined_score']} (threshold: {args.threshold})")
            print(f"  Suggestion: {flag['suggestion']}")
            print()
    else:
        print("NOVELTY CHECK: All themes appear original. No similarities above threshold.")

    # Write results as JSON to stdout if piped
    if not sys.stdout.isatty():
        json.dump({'flags': flags, 'threshold': args.threshold}, sys.stdout, indent=2)

    sys.exit(1 if flags else 0)


if __name__ == '__main__':
    main()
