#!/usr/bin/env python3
"""
Musical Continuity Document (MCD) tracker for Wolfgang v2.

Parses a newly composed ABC section and updates continuity.json with:
- Tonal history (keys visited, cadence types)
- Theme appearances
- Intensity arc data
- Orchestration state
- Structural milestones

Usage:
    python3 continuity_tracker.py <workspace-path> <section-id>
"""

import argparse
import json
import re
import sys
from pathlib import Path

from music21 import converter, key, dynamics, tempo, instrument


def parse_abc_section(abc_path: str):
    """Parse an ABC section file and extract musical information."""
    content = Path(abc_path).read_text(encoding='utf-8')

    info = {
        'keys_found': [],
        'dynamics_found': [],
        'tempo_found': None,
        'instruments_used': [],
        'note_count': 0,
        'measure_count': 0,
    }

    # Extract key from header
    key_match = re.search(r'K:(\S+)', content)
    if key_match:
        info['keys_found'].append(key_match.group(1))

    # Count measures (barlines)
    info['measure_count'] = content.count('|') // max(1, len(re.findall(r'\[V:\S+?\]', content)))

    # Extract dynamics
    for dyn in re.findall(r'!(\w+)!', content):
        if dyn in ('f', 'ff', 'fff', 'p', 'pp', 'ppp', 'mf', 'mp', 'sfz'):
            info['dynamics_found'].append(dyn)

    # Extract tempo
    tempo_match = re.search(r'Q:.*?(\d+)', content)
    if tempo_match:
        info['tempo_found'] = int(tempo_match.group(1))

    # Extract voices used
    voices = re.findall(r'\[V:(\S+?)\]', content)
    info['instruments_used'] = list(set(voices))

    # Count notes (rough estimate)
    note_pattern = re.compile(r'[a-gA-G][,\']*\d*/?')
    info['note_count'] = len(note_pattern.findall(content))

    return info


def estimate_intensity(dynamics_list: list[str]) -> float:
    """Estimate intensity (0.0-1.0) from dynamics markings."""
    dyn_values = {
        'ppp': 0.1, 'pp': 0.2, 'p': 0.3, 'mp': 0.4,
        'mf': 0.6, 'f': 0.7, 'ff': 0.85, 'fff': 0.95, 'sfz': 0.9,
    }
    if not dynamics_list:
        return 0.5  # default moderate

    values = [dyn_values.get(d, 0.5) for d in dynamics_list]
    return sum(values) / len(values)


def update_continuity(workspace_path: str, section_id: str):
    """Update continuity.json with information from a newly composed section."""
    workspace = Path(workspace_path)
    continuity_path = workspace / 'continuity.json'
    structure_path = workspace / 'structure.json'

    # Load or initialize continuity document
    if continuity_path.exists():
        mcd = json.loads(continuity_path.read_text())
    else:
        mcd = {
            'piece_id': workspace.name,
            'global_state': {
                'measures_composed': 0,
                'current_section': '',
                'current_movement': 1,
                'sections_completed': 0,
            },
            'tonal_history': [],
            'harmonic_regions_used': {},
            'themes_introduced': {},
            'intensity_arc': [],
            'orchestration_state': {
                'instruments_used_recently': [],
                'tutti_count': 0,
                'solo_passages': [],
                'texture_history': [],
            },
            'unresolved_elements': [],
            'structural_milestones': [],
            'user_feedback_applied': [],
        }

    # Find the composed ABC file
    composed_dir = workspace / 'composed'
    abc_files = list(composed_dir.glob(f'*{section_id}*.abc'))
    if not abc_files:
        # Try with movement prefix
        abc_files = list(composed_dir.glob(f'*_{section_id}.abc'))
    if not abc_files:
        print(f"Warning: No ABC file found for section {section_id}", file=sys.stderr)
        return

    abc_path = abc_files[0]

    # Parse the section
    info = parse_abc_section(str(abc_path))

    # Determine movement number from section_id
    mvt_match = re.match(r'm(\d+)_', section_id)
    mvt_num = int(mvt_match.group(1)) if mvt_match else 1

    # Update global state
    mcd['global_state']['current_section'] = section_id
    mcd['global_state']['current_movement'] = mvt_num
    mcd['global_state']['measures_composed'] += info['measure_count']
    mcd['global_state']['sections_completed'] = mcd['global_state'].get('sections_completed', 0) + 1

    # Update tonal history
    for k in info['keys_found']:
        mcd['tonal_history'].append({
            'section': section_id,
            'keys_visited': info['keys_found'],
        })
        # Track harmonic region usage
        if k not in mcd['harmonic_regions_used']:
            mcd['harmonic_regions_used'][k] = 0
        mcd['harmonic_regions_used'][k] += info['measure_count']
        break  # Only add one entry per section

    # Update intensity arc
    intensity = estimate_intensity(info['dynamics_found'])
    mcd['intensity_arc'].append({
        'section': section_id,
        'intensity': round(intensity, 2),
        'dynamics': info['dynamics_found'][:5],  # Keep compact
    })

    # Update orchestration state
    mcd['orchestration_state']['instruments_used_recently'] = info['instruments_used']

    # Detect texture type (rough heuristic)
    n_instruments = len(info['instruments_used'])
    if n_instruments >= 10:
        texture = 'tutti'
        mcd['orchestration_state']['tutti_count'] += 1
    elif n_instruments >= 5:
        texture = 'mixed'
    elif n_instruments >= 2:
        texture = 'chamber'
    else:
        texture = 'solo'

    mcd['orchestration_state']['texture_history'].append(texture)
    # Keep only last 20 entries
    mcd['orchestration_state']['texture_history'] = \
        mcd['orchestration_state']['texture_history'][-20:]

    # Check themes (if themes.json exists)
    themes_path = workspace / 'themes.json'
    if themes_path.exists():
        themes = json.loads(themes_path.read_text())
        usage_plan = themes.get('usage_plan', {})
        if section_id in usage_plan:
            for theme_ref in usage_plan[section_id]:
                theme_name = theme_ref.split(':')[0]
                if theme_name not in mcd['themes_introduced']:
                    mcd['themes_introduced'][theme_name] = {
                        'first_appearance': section_id,
                        'appearances': 0,
                        'last_transformation': 'original',
                    }
                mcd['themes_introduced'][theme_name]['appearances'] += 1
                if ':' in theme_ref:
                    mcd['themes_introduced'][theme_name]['last_transformation'] = \
                        theme_ref.split(':', 1)[1]

    # Write updated continuity document
    continuity_path.write_text(json.dumps(mcd, indent=2))
    print(f"Updated continuity.json for section {section_id}")
    print(f"  Measures composed: {mcd['global_state']['measures_composed']}")
    print(f"  Sections completed: {mcd['global_state']['sections_completed']}")
    print(f"  Current intensity: {intensity:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description='Update Musical Continuity Document after section composition'
    )
    parser.add_argument('workspace', help='Path to workspace directory')
    parser.add_argument('section_id', help='Section ID (e.g., m1_expo_pt)')

    args = parser.parse_args()

    try:
        update_continuity(args.workspace, args.section_id)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
