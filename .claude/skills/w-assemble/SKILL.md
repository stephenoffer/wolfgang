---
name: w-assemble
description: "Assemble all composed sections into complete movements and convert to MusicXML. Runs the Python conversion pipeline and validates the output."
argument-hint: "<piece-id> ['movement' N | 'full']"
---

# W-Assemble — Final Assembly and MusicXML Conversion

You are the final assembly agent for Wolfgang. You collect all composed sections, assemble them into complete movements, and produce the final MusicXML file.

## Process

### Step 1: Read Structure

Read `workspace/$ARGUMENTS[0]/structure.json` to get the section order for each movement.

### Step 2: Determine Scope

If `$ARGUMENTS[1]` is `movement N`: assemble only movement N.
If `$ARGUMENTS[1]` is `full`: assemble all movements.

### Step 3: Assemble ABC Files

For each movement in scope:
1. Read all section ABC files in order from `workspace/$ARGUMENTS[0]/composed/`
2. Run `python3 tools/assemble_score.py` to concatenate them:
   ```bash
   python3 tools/assemble_score.py workspace/$ARGUMENTS[0] [movement-N|full]
   ```
   This produces:
   - `workspace/$ARGUMENTS[0]/assembled/movement_<N>.abc` (per movement)
   - `workspace/$ARGUMENTS[0]/assembled/full_score.abc` (if full)

If `assemble_score.py` is not yet available, manually concatenate:
1. Take the first section's header (X:, T:, C:, M:, L:, Q:, K:, V: declarations)
2. For each section in order, append the music lines (the [V:name] lines)
3. Insert double barlines (||) at section boundaries
4. Insert final barlines (|]) at movement ends
5. Write the assembled ABC file

### Step 4: Validate ABC

Run the ABC validator:
```bash
python3 tools/validate_abc.py workspace/$ARGUMENTS[0]/assembled/full_score.abc
```

If errors found, report them and attempt to fix (usually missing barlines or duration mismatches).

### Step 5: Convert to MusicXML

Run the converter:
```bash
python3 tools/abc_to_musicxml.py workspace/$ARGUMENTS[0]/assembled/full_score.abc \
  --output output/$ARGUMENTS[0].musicxml \
  --validate --compress
```

This produces:
- `output/$ARGUMENTS[0].musicxml` — full MusicXML score
- `output/$ARGUMENTS[0].mxl` — compressed version for smaller file size

### Step 6: Post-Conversion Validation

Run additional validation if tools are available:
```bash
python3 tools/validate_musicxml.py output/$ARGUMENTS[0].musicxml
python3 tools/range_checker.py output/$ARGUMENTS[0].musicxml
```

### Step 7: Report Results

Report to the user:
- File path to the generated MusicXML
- Number of parts, measures, and movements
- Any validation warnings
- Suggest: "Open this file in MuseScore to hear and review the composition"

### Step 8: Update State

Update `state.json`:
```json
{
  "current_phase": "complete",
  "output_file": "output/<piece-id>.musicxml",
  "output_mxl": "output/<piece-id>.mxl"
}
```

## Error Handling

If music21 conversion fails:
1. Check `tools/validate_abc.py` output for syntax errors
2. Identify the problematic section (usually duration mismatches)
3. Report which section needs re-composition
4. The orchestrator can re-invoke `/w-compose` + `/w-review` on that section

If validation shows range violations:
1. Report the specific instruments and measures
2. These can be fixed by the orchestrator re-invoking `/w-review` on the relevant sections
