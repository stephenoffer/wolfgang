#!/usr/bin/env python3
"""
Score assembler for Wolfgang v2.

Concatenates per-section ABC files into movement-level and full-score ABC files.
Reads structure.json to determine section order.

Usage:
    python3 assemble_score.py <workspace-path> [movement-N|full]
"""

import argparse
import json
import re
import sys
from pathlib import Path


def read_structure(workspace_path: Path) -> dict:
    """Read structure.json from workspace."""
    structure_path = workspace_path / 'structure.json'
    if not structure_path.exists():
        raise FileNotFoundError(f"structure.json not found in {workspace_path}")
    return json.loads(structure_path.read_text())


def extract_header(abc_content: str) -> tuple[list[str], list[str]]:
    """Split ABC into header lines and body lines.

    Returns (header_lines, body_lines).
    """
    header = []
    body = []
    in_body = False

    for line in abc_content.split('\n'):
        stripped = line.strip()
        if not stripped:
            if in_body:
                body.append(line)
            continue

        if not in_body:
            # V: declarations can appear after K:
            if stripped.startswith('V:') or (len(stripped) > 1 and stripped[1] == ':' and stripped[0].isalpha()):
                header.append(stripped)
                if stripped[0] == 'K':
                    # K: is last required header field, but V: can follow
                    pass
            elif stripped.startswith('%%'):
                header.append(stripped)
            elif stripped.startswith('[V:') or (not stripped[0].isalpha() or stripped[1] != ':'):
                # First music line
                in_body = True
                body.append(line)
        else:
            body.append(line)

    # If we never found body content, check if V: lines were treated as header
    # but actually contained music after them
    if not body and header:
        # Re-scan: everything after K: and V: declarations is body
        header2 = []
        body2 = []
        past_key = False
        past_voices = False
        for line in header:
            if line.startswith('K:'):
                header2.append(line)
                past_key = True
            elif past_key and line.startswith('V:'):
                header2.append(line)
            elif past_key:
                body2.append(line)
            else:
                header2.append(line)
        return header2, body2

    return header, body


def extract_body_lines(abc_content: str) -> list[str]:
    """Extract only the music body lines (lines starting with [V:] or containing notes)."""
    _, body = extract_header(abc_content)
    return [l for l in body if l.strip()]


def assemble_movement(workspace_path: Path, movement_num: int,
                      structure: dict) -> str:
    """Assemble all sections of a movement into a single ABC string."""

    movements = structure.get('movements', [])
    movement = None
    for m in movements:
        if m.get('number') == movement_num:
            movement = m
            break

    if not movement:
        raise ValueError(f"Movement {movement_num} not found in structure.json")

    sections = movement.get('sections', [])
    if not sections:
        raise ValueError(f"Movement {movement_num} has no sections")

    composed_dir = workspace_path / 'composed'

    # Read the first section to get the header
    first_section_id = sections[0].get('id', '')
    first_abc_files = list(composed_dir.glob(f'*{first_section_id}*.abc'))
    if not first_abc_files:
        raise FileNotFoundError(
            f"No ABC file found for first section: {first_section_id}"
        )

    first_content = first_abc_files[0].read_text()
    header_lines, _ = extract_header(first_content)

    # Update title in header
    piece_title = structure.get('title', 'Untitled')
    mvt_title = movement.get('title', f'Movement {movement_num}')
    new_header = []
    for line in header_lines:
        if line.startswith('T:'):
            new_header.append(f'T:{piece_title} - {mvt_title}')
        else:
            new_header.append(line)

    # Collect body lines from all sections
    all_body_lines = []
    for i, section in enumerate(sections):
        section_id = section.get('id', '')
        abc_files = list(composed_dir.glob(f'*{section_id}*.abc'))

        if not abc_files:
            print(f"WARNING: No ABC file for section {section_id}", file=sys.stderr)
            continue

        content = abc_files[0].read_text()
        body_lines = extract_body_lines(content)

        if body_lines:
            # Add section comment
            all_body_lines.append(f'% === Section: {section_id} ===')
            all_body_lines.extend(body_lines)

            # Add double barline between sections (not after last)
            if i < len(sections) - 1:
                # The last barline of this section should be || (double)
                pass  # Let the original barlines stand

    # Combine
    result_lines = new_header + ['%'] + all_body_lines
    return '\n'.join(result_lines)


def assemble_full_score(workspace_path: Path, structure: dict) -> str:
    """Assemble all movements into a full score ABC string."""
    movements = structure.get('movements', [])

    if not movements:
        raise ValueError("No movements found in structure.json")

    # For a full score, we concatenate movement ABC files
    # But ABC doesn't natively support multi-movement works in one file
    # Convention: separate movements with blank lines and new X: headers

    parts = []
    for i, movement in enumerate(movements):
        mvt_num = movement.get('number', i + 1)
        mvt_abc = assemble_movement(workspace_path, mvt_num, structure)
        parts.append(mvt_abc)

    return '\n\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(
        description='Assemble per-section ABC files into movements'
    )
    parser.add_argument('workspace', help='Path to workspace directory')
    parser.add_argument(
        'scope', nargs='?', default='full',
        help='Scope: "full" for entire piece, or "movement-N" for specific movement'
    )

    args = parser.parse_args()
    workspace = Path(args.workspace)
    assembled_dir = workspace / 'assembled'
    assembled_dir.mkdir(exist_ok=True)

    try:
        structure = read_structure(workspace)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.scope.startswith('movement-'):
            mvt_num = int(args.scope.split('-')[1])
            result = assemble_movement(workspace, mvt_num, structure)
            output_path = assembled_dir / f'movement_{mvt_num}.abc'
            output_path.write_text(result)
            print(f"Assembled movement {mvt_num}: {output_path}")
        else:
            # Full score
            result = assemble_full_score(workspace, structure)
            output_path = assembled_dir / 'full_score.abc'
            output_path.write_text(result)
            print(f"Assembled full score: {output_path}")

            # Also write per-movement files
            movements = structure.get('movements', [])
            for m in movements:
                mvt_num = m.get('number', 1)
                mvt_result = assemble_movement(workspace, mvt_num, structure)
                mvt_path = assembled_dir / f'movement_{mvt_num}.abc'
                mvt_path.write_text(mvt_result)
                print(f"  Movement {mvt_num}: {mvt_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
