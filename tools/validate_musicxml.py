#!/usr/bin/env python3
"""
MusicXML validator for Wolfgang v2.

Validates MusicXML files for:
- Well-formed XML
- Structural correctness (parts match part-list)
- Measure count consistency
- Optional XSD schema validation

Usage:
    python3 validate_musicxml.py <input.musicxml> [--schema <musicxml.xsd>]
"""

import argparse
import sys
from pathlib import Path

from lxml import etree


def validate_wellformed(xml_path: str) -> list[str]:
    """Check that the file is well-formed XML."""
    issues = []
    try:
        tree = etree.parse(xml_path)
        return issues, tree
    except etree.XMLSyntaxError as e:
        issues.append(f"XML SYNTAX ERROR: {e}")
        return issues, None


def validate_structure(tree: etree._ElementTree) -> list[str]:
    """Validate MusicXML structural correctness."""
    issues = []
    root = tree.getroot()

    # Remove namespace for easier querying
    ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''

    # Check for score-partwise or score-timewise
    tag = root.tag.replace(ns, '')
    if tag not in ('score-partwise', 'score-timewise'):
        issues.append(f"ERROR: Root element is '{tag}', expected 'score-partwise' or 'score-timewise'")
        return issues

    # Get declared parts from part-list
    part_list = root.find(f'{ns}part-list')
    if part_list is None:
        issues.append("ERROR: Missing <part-list> element")
        return issues

    declared_parts = {}
    for sp in part_list.findall(f'{ns}score-part'):
        pid = sp.get('id', '')
        pname = sp.find(f'{ns}part-name')
        declared_parts[pid] = pname.text if pname is not None and pname.text else pid

    # Get actual parts
    actual_parts = {}
    for part in root.findall(f'{ns}part'):
        pid = part.get('id', '')
        measures = part.findall(f'{ns}measure')
        actual_parts[pid] = len(measures)

    # Check part consistency
    for pid in declared_parts:
        if pid not in actual_parts:
            issues.append(f"WARNING: Part '{declared_parts[pid]}' ({pid}) declared but has no content")

    for pid in actual_parts:
        if pid not in declared_parts:
            issues.append(f"ERROR: Part {pid} has content but is not declared in part-list")

    # Check measure count consistency
    measure_counts = list(actual_parts.values())
    if measure_counts and len(set(measure_counts)) > 1:
        details = {declared_parts.get(pid, pid): count
                   for pid, count in actual_parts.items()}
        issues.append(f"WARNING: Parts have different measure counts: {details}")

    # Report summary
    if not issues:
        n_parts = len(actual_parts)
        n_measures = measure_counts[0] if measure_counts else 0
        print(f"Structure: {n_parts} parts, {n_measures} measures")

    return issues


def validate_schema(tree: etree._ElementTree, schema_path: str) -> list[str]:
    """Validate against MusicXML XSD schema."""
    issues = []
    try:
        schema = etree.XMLSchema(etree.parse(schema_path))
        is_valid = schema.validate(tree)
        if not is_valid:
            for error in schema.error_log:
                issues.append(f"SCHEMA: {error}")
    except Exception as e:
        issues.append(f"SCHEMA ERROR: Could not load schema: {e}")
    return issues


def main():
    parser = argparse.ArgumentParser(
        description='Validate MusicXML files'
    )
    parser.add_argument('input', help='Input MusicXML file path')
    parser.add_argument(
        '--schema', help='Path to MusicXML XSD schema for full validation'
    )
    parser.add_argument(
        '--json', action='store_true', help='Output as JSON'
    )

    args = parser.parse_args()

    all_issues = []

    # Step 1: Well-formed XML
    issues, tree = validate_wellformed(args.input)
    all_issues.extend(issues)

    if tree is None:
        print(f"FAILED: File is not well-formed XML")
        for issue in all_issues:
            print(f"  {issue}")
        sys.exit(1)

    # Step 2: Structural validation
    struct_issues = validate_structure(tree)
    all_issues.extend(struct_issues)

    # Step 3: Optional schema validation
    if args.schema:
        schema_issues = validate_schema(tree, args.schema)
        all_issues.extend(schema_issues)

    # Report
    if args.json:
        import json
        result = {
            'file': args.input,
            'valid': not any('ERROR' in i for i in all_issues),
            'issues': all_issues,
        }
        print(json.dumps(result, indent=2))
    else:
        if all_issues:
            print(f"Validation results for {args.input}:")
            for issue in all_issues:
                print(f"  {issue}")
            errors = sum(1 for i in all_issues if 'ERROR' in i)
            warnings = sum(1 for i in all_issues if 'WARNING' in i)
            print(f"\n{errors} error(s), {warnings} warning(s)")
        else:
            print(f"Validation: OK — {args.input}")

    has_errors = any('ERROR' in i for i in all_issues)
    sys.exit(1 if has_errors else 0)


if __name__ == '__main__':
    main()
