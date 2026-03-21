#!/usr/bin/env python3
"""
ABC to MusicXML converter for Wolfgang v2.

Converts multi-voice ABC notation files to MusicXML via music21.
Because music21's ABC parser doesn't reliably handle multi-voice ABC,
this tool splits voices into individual ABC tunes, parses each separately,
and assembles them into a single Score.

Handles: orchestral scores, transposing instruments, tempo/dynamics,
and produces both .musicxml and .mxl output.

Usage:
    python3 abc_to_musicxml.py <input.abc> [--output <output.musicxml>] [--compress]
"""

import argparse
import re
import sys
from pathlib import Path

from music21 import converter, instrument, stream, metadata


# Standard orchestral instrument mappings
# Maps voice name patterns to music21 instrument classes
INSTRUMENT_MAP = {
    # Strings
    'violin 1': instrument.Violin,
    'violin 2': instrument.Violin,
    'violin i': instrument.Violin,
    'violin ii': instrument.Violin,
    'v1': instrument.Violin,
    'v2': instrument.Violin,
    'vln1': instrument.Violin,
    'vln2': instrument.Violin,
    'viola': instrument.Viola,
    'va': instrument.Viola,
    'vla': instrument.Viola,
    'cello': instrument.Violoncello,
    'vc': instrument.Violoncello,
    'vcl': instrument.Violoncello,
    'violoncello': instrument.Violoncello,
    'contrabass': instrument.Contrabass,
    'double bass': instrument.Contrabass,
    'cb': instrument.Contrabass,

    # Woodwinds
    'flute': instrument.Flute,
    'fl': instrument.Flute,
    'fl1': instrument.Flute,
    'fl2': instrument.Flute,
    'flute 1': instrument.Flute,
    'flute 2': instrument.Flute,
    'oboe': instrument.Oboe,
    'ob': instrument.Oboe,
    'ob1': instrument.Oboe,
    'ob2': instrument.Oboe,
    'clarinet': instrument.Clarinet,
    'cl': instrument.Clarinet,
    'cl1': instrument.Clarinet,
    'cl2': instrument.Clarinet,
    'clarinet in bb': instrument.Clarinet,
    'bassoon': instrument.Bassoon,
    'bn': instrument.Bassoon,
    'bsn': instrument.Bassoon,
    'bsn1': instrument.Bassoon,
    'bsn2': instrument.Bassoon,

    # Brass
    'horn': instrument.Horn,
    'hn': instrument.Horn,
    'hn1': instrument.Horn,
    'hn2': instrument.Horn,
    'french horn': instrument.Horn,
    'horn in f': instrument.Horn,
    'trumpet': instrument.Trumpet,
    'tr': instrument.Trumpet,
    'tpt': instrument.Trumpet,
    'tpt1': instrument.Trumpet,
    'tpt2': instrument.Trumpet,
    'trumpet in bb': instrument.Trumpet,
    'trombone': instrument.Trombone,
    'tbn': instrument.Trombone,
    'tbn1': instrument.Trombone,
    'tbn2': instrument.Trombone,
    'tuba': instrument.Tuba,

    # Percussion
    'timpani': instrument.Timpani,
    'timp': instrument.Timpani,

    # Keyboard
    'piano': instrument.Piano,
    'pn': instrument.Piano,
    'piano rh': instrument.Piano,
    'piano lh': instrument.Piano,
    'pn_rh': instrument.Piano,
    'pn_lh': instrument.Piano,
    'harpsichord': instrument.Harpsichord,
    'organ': instrument.Organ,
    'celesta': instrument.Celesta,

    # Other
    'harp': instrument.Harp,
}


def resolve_instrument(voice_name: str) -> instrument.Instrument | None:
    """Map a voice/part name to a music21 Instrument object."""
    name_lower = voice_name.lower().strip()
    for pattern, inst_class in INSTRUMENT_MAP.items():
        if pattern == name_lower or pattern in name_lower:
            return inst_class()
    return None


def parse_voice_header(voice_line: str) -> dict:
    """Parse a V: header line into voice properties.

    Example: 'V:V1 clef=treble name="Violin I"'
    Returns: {'id': 'V1', 'clef': 'treble', 'name': 'Violin I'}
    """
    props = {}

    # Remove V: prefix
    content = voice_line.strip()
    if content.startswith('V:'):
        content = content[2:]

    parts = content.split(None, 1)
    if not parts:
        return props

    props['id'] = parts[0]

    if len(parts) > 1:
        remainder = parts[1]
        # Extract name="..." or name=...
        name_match = re.search(r'name="([^"]*)"', remainder)
        if name_match:
            props['name'] = name_match.group(1)
        else:
            name_match = re.search(r'name=(\S+)', remainder)
            if name_match:
                props['name'] = name_match.group(1)

        # Extract clef=...
        clef_match = re.search(r'clef=(\S+)', remainder)
        if clef_match:
            props['clef'] = clef_match.group(1)

        # Extract transpose=...
        trans_match = re.search(r'transpose=(-?\d+)', remainder)
        if trans_match:
            props['transpose'] = int(trans_match.group(1))

    return props


def split_multivoice_abc(abc_content: str) -> tuple[dict, list[tuple[dict, str]]]:
    """Split a multi-voice ABC file into individual voice ABC strings.

    Handles two formats:
    1. Voice headers in header section + [V:name] inline in body
    2. V:name as section dividers in body

    Returns:
        (header_fields, [(voice_props, voice_abc_body), ...])
    """
    lines = abc_content.split('\n')

    # Collect header fields and voice declarations
    header_fields = {}  # field_key -> value (or list for multiple)
    voice_declarations = {}  # voice_id -> props dict
    voice_order = []  # preserve declaration order

    header_lines = []  # lines that go in every voice's header
    body_started = False
    body_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and pure comments in header
        if not stripped:
            if body_started:
                body_lines.append(line)
            continue

        if stripped.startswith('%') and not stripped.startswith('%%'):
            if body_started:
                body_lines.append(line)
            continue

        # V: declarations can appear both in header and after K:
        # (common ABC pattern: K: first, then V: declarations, then music)
        if len(stripped) > 1 and stripped[0] == 'V' and stripped[1] == ':':
            props = parse_voice_header(stripped)
            vid = props.get('id', '')
            if vid and vid not in voice_declarations:
                voice_declarations[vid] = props
                voice_order.append(vid)
            elif vid and vid in voice_declarations:
                # Update with any new properties
                voice_declarations[vid].update(
                    {k: v for k, v in props.items() if k != 'id'}
                )
            if body_started:
                body_lines.append(line)
            continue

        # Check for header fields
        if not body_started and len(stripped) > 1 and stripped[1] == ':' and stripped[0].isalpha():
            field_key = stripped[0]
            field_value = stripped[2:].strip()

            if field_key == 'K':
                # K: marks end of header
                header_fields['K'] = field_value
                header_lines.append(stripped)
                body_started = True
            else:
                header_fields[field_key] = field_value
                header_lines.append(stripped)
            continue

        # Directives (%%staves etc) — include in header
        if stripped.startswith('%%') and not body_started:
            header_lines.append(stripped)
            continue

        # We're in the body now
        body_started = True
        body_lines.append(line)

    # Now split body by voices
    # Format 1: [V:name] at start of lines
    # Format 2: V:name as standalone lines separating voice content

    voice_bodies = {}  # voice_id -> list of music lines

    # Check which format we're dealing with
    has_inline_voice = any(re.match(r'\[V:\S+?\]', l.strip()) for l in body_lines)
    has_section_voice = any(re.match(r'V:\S+', l.strip()) and not l.strip().startswith('[') for l in body_lines)

    if has_inline_voice:
        # Format 1: [V:V1] d2 ef | g2 fe |
        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r'\[V:(\S+?)\]\s*(.*)', stripped)
            if match:
                vid = match.group(1)
                music = match.group(2)
                if vid not in voice_bodies:
                    voice_bodies[vid] = []
                    if vid not in voice_declarations:
                        voice_declarations[vid] = {'id': vid}
                        voice_order.append(vid)
                voice_bodies[vid].append(music)
    elif has_section_voice:
        # Format 2: V:V1\n music lines \n V:V2 \n music lines
        current_voice = None
        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r'V:(\S+)', stripped)
            if match and not stripped.startswith('['):
                current_voice = match.group(1)
                # There might be voice properties on this line
                if current_voice not in voice_declarations:
                    props = parse_voice_header(stripped)
                    voice_declarations[current_voice] = props
                    voice_order.append(current_voice)
                if current_voice not in voice_bodies:
                    voice_bodies[current_voice] = []
            elif current_voice:
                voice_bodies[current_voice].append(stripped)
    else:
        # Single voice — no voice markers at all
        single_body = '\n'.join(l for l in body_lines if l.strip())
        if single_body.strip():
            voice_declarations['V1'] = {'id': 'V1', 'name': 'Part 1'}
            voice_order = ['V1']
            voice_bodies['V1'] = [single_body]

    # Build per-voice ABC strings
    voices = []
    for i, vid in enumerate(voice_order):
        props = voice_declarations.get(vid, {'id': vid})
        body = '\n'.join(voice_bodies.get(vid, []))

        if not body.strip():
            continue

        # Build a complete ABC tune for this voice
        voice_abc_lines = [f'X:{i + 1}']

        # Add title
        title = header_fields.get('T', 'Untitled')
        voice_name = props.get('name', vid)
        voice_abc_lines.append(f'T:{title} - {voice_name}')

        # Add composer
        if 'C' in header_fields:
            voice_abc_lines.append(f'C:{header_fields["C"]}')

        # Add meter
        if 'M' in header_fields:
            voice_abc_lines.append(f'M:{header_fields["M"]}')

        # Add unit length
        if 'L' in header_fields:
            voice_abc_lines.append(f'L:{header_fields["L"]}')

        # Add tempo
        if 'Q' in header_fields:
            voice_abc_lines.append(f'Q:{header_fields["Q"]}')

        # Add key (with clef if specified)
        key_str = header_fields.get('K', 'C')
        clef = props.get('clef')
        if clef:
            voice_abc_lines.append(f'K:{key_str} clef={clef}')
        else:
            voice_abc_lines.append(f'K:{key_str}')

        # Add music body
        voice_abc_lines.append(body)

        voice_abc = '\n'.join(voice_abc_lines)
        voices.append((props, voice_abc))

    return header_fields, voices


def convert_abc_to_score(abc_content: str) -> stream.Score:
    """Parse multi-voice ABC content into a music21 Score.

    Splits voices, parses each independently, and assembles into a single Score.
    """
    header_fields, voices = split_multivoice_abc(abc_content)

    if not voices:
        # Fallback: try direct parsing
        return converter.parse(abc_content, format='abc')

    score = stream.Score()

    # Set metadata
    md = metadata.Metadata()
    md.title = header_fields.get('T', 'Untitled')
    md.composer = header_fields.get('C', '')
    score.metadata = md

    for props, voice_abc in voices:
        try:
            parsed = converter.parse(voice_abc, format='abc')
        except Exception as e:
            print(f"Warning: Failed to parse voice {props.get('id', '?')}: {e}",
                  file=sys.stderr)
            continue

        # Extract the part from parsed result
        if isinstance(parsed, stream.Score) and parsed.parts:
            part = parsed.parts[0]
        elif isinstance(parsed, stream.Part):
            part = parsed
        else:
            # Wrap in a Part
            part = stream.Part()
            for el in parsed:
                part.append(el)

        # Set part name
        voice_name = props.get('name', props.get('id', 'Part'))
        part.partName = voice_name

        # Assign instrument
        inst = resolve_instrument(voice_name)
        if inst:
            part.insert(0, inst)

        score.append(part)

    return score


def write_musicxml(score: stream.Score, output_path: str, compress: bool = False) -> str:
    """Write a music21 Score to MusicXML format."""
    output = Path(output_path)

    if compress or output.suffix == '.mxl':
        fmt = 'mxl'
        if output.suffix != '.mxl':
            output = output.with_suffix('.mxl')
    else:
        fmt = 'musicxml'
        if output.suffix not in ('.musicxml', '.xml'):
            output = output.with_suffix('.musicxml')

    score.write(fmt, fp=str(output))
    return str(output)


def convert_file(input_path: str, output_path: str | None = None, compress: bool = False) -> str:
    """Convert an ABC file to MusicXML.

    Args:
        input_path: Path to input .abc file
        output_path: Path for output .musicxml file (default: same name, .musicxml extension)
        compress: If True, also produce compressed .mxl

    Returns:
        Path to the generated MusicXML file
    """
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    abc_content = input_file.read_text(encoding='utf-8')

    # Parse and post-process
    score = convert_abc_to_score(abc_content)

    # Determine output path
    if output_path is None:
        suffix = '.mxl' if compress else '.musicxml'
        output_path = str(input_file.with_suffix(suffix))

    # Write MusicXML
    result_path = write_musicxml(score, output_path, compress=compress)

    # If compress requested and we wrote .musicxml, also write .mxl
    if compress and not output_path.endswith('.mxl'):
        mxl_path = str(Path(output_path).with_suffix('.mxl'))
        write_musicxml(score, mxl_path, compress=True)
        print(f"Compressed: {mxl_path}")

    return result_path


def validate_score(score: stream.Score) -> list[str]:
    """Run basic validation on a parsed score."""
    issues = []

    if len(score.parts) == 0:
        issues.append("ERROR: Score has no parts")
        return issues

    # Check that all parts have the same number of measures
    measure_counts = {}
    for part in score.parts:
        name = part.partName or f"Part-{part.id}"
        count = len(part.getElementsByClass('Measure'))
        measure_counts[name] = count

    if len(set(measure_counts.values())) > 1:
        issues.append(
            f"WARNING: Parts have different measure counts: {measure_counts}"
        )

    # Check for empty parts
    for part in score.parts:
        name = part.partName or f"Part-{part.id}"
        notes = list(part.recurse().notes)
        if len(notes) == 0:
            issues.append(f"WARNING: Part '{name}' has no notes")

    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Convert ABC notation to MusicXML'
    )
    parser.add_argument('input', help='Input ABC file path')
    parser.add_argument('--output', '-o', help='Output MusicXML file path')
    parser.add_argument(
        '--compress', '-c', action='store_true',
        help='Also produce compressed .mxl file'
    )
    parser.add_argument(
        '--validate', '-v', action='store_true',
        help='Validate the score after conversion'
    )

    args = parser.parse_args()

    try:
        result = convert_file(args.input, args.output, args.compress)
        print(f"Converted: {result}")

        if args.validate:
            abc_content = Path(args.input).read_text(encoding='utf-8')
            score = convert_abc_to_score(abc_content)
            issues = validate_score(score)
            if issues:
                print("\nValidation issues:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print("Validation: OK")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
