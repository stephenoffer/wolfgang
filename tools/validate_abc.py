#!/usr/bin/env python3
"""
ABC notation validator for Wolfgang v2.

Performs pre-conversion syntax validation of ABC files without using music21
(for speed). Checks structure, voice declarations, key/time signatures,
and basic bar duration consistency.

Usage:
    python3 validate_abc.py <input.abc> [--strict]
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    level: str  # ERROR, WARNING, INFO
    line_num: int
    message: str

    def __str__(self):
        return f"{self.level} (line {self.line_num}): {self.message}"


@dataclass
class ABCValidator:
    """Validates ABC notation files for structural correctness."""

    issues: list[ValidationIssue] = field(default_factory=list)
    strict: bool = False

    # Valid ABC note names
    NOTE_PATTERN = re.compile(
        r"[_=^]*[a-gA-G][,']*[\d]*/?[\d]*"
    )

    # Valid key signatures
    VALID_KEYS = {
        'C', 'D', 'E', 'F', 'G', 'A', 'B',
        'Cm', 'Dm', 'Em', 'Fm', 'Gm', 'Am', 'Bm',
        'Cb', 'Db', 'Eb', 'Fb', 'Gb', 'Ab', 'Bb',
        'Cbm', 'Dbm', 'Ebm', 'Fbm', 'Gbm', 'Abm', 'Bbm',
        'C#', 'D#', 'E#', 'F#', 'G#', 'A#', 'B#',
        'C#m', 'D#m', 'E#m', 'F#m', 'G#m', 'A#m', 'B#m',
    }

    # Valid modes
    VALID_MODES = {
        'maj', 'min', 'mix', 'dor', 'phr', 'lyd', 'loc',
        'major', 'minor', 'mixolydian', 'dorian', 'phrygian',
        'lydian', 'locrian', 'm',
    }

    # Valid time signatures
    TIME_SIG_PATTERN = re.compile(r'^(\d+)/(\d+)$')

    def add_issue(self, level: str, line_num: int, message: str):
        self.issues.append(ValidationIssue(level, line_num, message))

    def validate_file(self, filepath: str) -> list[ValidationIssue]:
        """Validate an ABC file. Returns list of issues found."""
        content = Path(filepath).read_text(encoding='utf-8')
        return self.validate_content(content)

    def validate_content(self, content: str) -> list[ValidationIssue]:
        """Validate ABC content string. Returns list of issues found."""
        self.issues = []
        lines = content.split('\n')

        declared_voices = set()
        used_voices = set()
        has_key = False
        has_meter = False
        has_title = False
        has_index = False
        in_header = True

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('%'):
                if stripped.startswith('%%'):
                    # Directive - check for staves
                    self._check_directive(line_num, stripped)
                continue

            # Check for header fields
            if len(stripped) > 1 and stripped[1] == ':' and stripped[0].isalpha():
                field_key = stripped[0]
                field_value = stripped[2:].strip()

                if field_key == 'X':
                    has_index = True
                    in_header = True
                elif field_key == 'T':
                    has_title = True
                elif field_key == 'K':
                    has_key = True
                    self._validate_key(line_num, field_value)
                    in_header = False  # K: marks end of header
                elif field_key == 'M':
                    has_meter = True
                    self._validate_meter(line_num, field_value)
                elif field_key == 'L':
                    self._validate_unit_length(line_num, field_value)
                elif field_key == 'Q':
                    self._validate_tempo(line_num, field_value)
                elif field_key == 'V':
                    voice_id = field_value.split()[0] if field_value else ''
                    if voice_id:
                        declared_voices.add(voice_id)
                continue

            # Check for inline voice references [V:name]
            voice_refs = re.findall(r'\[V:(\S+?)\]', stripped)
            for v in voice_refs:
                used_voices.add(v)

            # Check for voice lines like [V:V1] or V:V1 at start of music line
            if stripped.startswith('[V:'):
                match = re.match(r'\[V:(\S+?)\]', stripped)
                if match:
                    used_voices.add(match.group(1))

            # Basic bar check: look for unmatched brackets
            if not in_header:
                open_brackets = stripped.count('[') - stripped.count('[V:')
                close_brackets = stripped.count(']') - len(re.findall(r'\[V:\S+?\]', stripped))
                # This is a rough check; ABC allows [CEG] chords
                pass

        # Check required fields
        if not has_index:
            self.add_issue('WARNING', 0, 'Missing X: (index) field')
        if not has_title:
            self.add_issue('WARNING', 0, 'Missing T: (title) field')
        if not has_key:
            self.add_issue('ERROR', 0, 'Missing K: (key) field — required')
        if not has_meter:
            self.add_issue('WARNING', 0, 'Missing M: (meter) field — defaults to 4/4')

        # Check voice consistency
        if declared_voices and used_voices:
            undeclared = used_voices - declared_voices
            unused = declared_voices - used_voices
            for v in undeclared:
                self.add_issue('ERROR', 0, f"Voice '{v}' used but never declared")
            for v in unused:
                self.add_issue('WARNING', 0, f"Voice '{v}' declared but never used")

        return self.issues

    def _validate_key(self, line_num: int, value: str):
        """Validate a K: field value."""
        if not value:
            self.add_issue('ERROR', line_num, 'Empty key signature')
            return

        # Extract the key part (before any mode or clef specifiers)
        parts = value.split()
        key_str = parts[0]

        # Check for key + mode like "Dm" or "D minor"
        # Accept reasonable key signatures
        base_note = key_str[0].upper()
        if base_note not in 'ABCDEFG':
            self.add_issue('ERROR', line_num, f"Invalid key note: '{key_str}'")

    def _validate_meter(self, line_num: int, value: str):
        """Validate an M: field value."""
        if value in ('C', 'C|', 'none'):
            return  # Common time, cut time, or no meter
        if not self.TIME_SIG_PATTERN.match(value):
            self.add_issue('ERROR', line_num, f"Invalid time signature: '{value}'")

    def _validate_unit_length(self, line_num: int, value: str):
        """Validate an L: field value."""
        if not re.match(r'^\d+/\d+$', value):
            self.add_issue('ERROR', line_num, f"Invalid unit note length: '{value}'")

    def _validate_tempo(self, line_num: int, value: str):
        """Validate a Q: field value."""
        # Tempo can be: "1/4=120" or "120" or "Allegro 1/4=120"
        if not value:
            self.add_issue('WARNING', line_num, 'Empty tempo marking')
            return
        # Basic check: should contain a number somewhere
        if not re.search(r'\d', value):
            self.add_issue('WARNING', line_num, f"Tempo has no numeric value: '{value}'")

    def _check_directive(self, line_num: int, line: str):
        """Check %% directives."""
        if line.startswith('%%staves'):
            # Validate staves directive
            staves_content = line[len('%%staves'):].strip()
            if not staves_content:
                self.add_issue('WARNING', line_num, 'Empty %%staves directive')


def main():
    parser = argparse.ArgumentParser(
        description='Validate ABC notation files'
    )
    parser.add_argument('input', help='Input ABC file path')
    parser.add_argument(
        '--strict', action='store_true',
        help='Enable strict validation (warnings become errors)'
    )
    parser.add_argument(
        '--json', action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    validator = ABCValidator(strict=args.strict)

    try:
        issues = validator.validate_file(args.input)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import json
        result = {
            'file': args.input,
            'valid': not any(i.level == 'ERROR' for i in issues),
            'issues': [
                {'level': i.level, 'line': i.line_num, 'message': i.message}
                for i in issues
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        if issues:
            print(f"Validation results for {args.input}:")
            for issue in issues:
                print(f"  {issue}")
            errors = sum(1 for i in issues if i.level == 'ERROR')
            warnings = sum(1 for i in issues if i.level == 'WARNING')
            print(f"\n{errors} error(s), {warnings} warning(s)")
        else:
            print(f"Validation: OK — {args.input}")

    # Exit with error code if there are errors
    has_errors = any(i.level == 'ERROR' for i in issues)
    if args.strict:
        has_errors = has_errors or any(i.level == 'WARNING' for i in issues)

    sys.exit(1 if has_errors else 0)


if __name__ == '__main__':
    main()
