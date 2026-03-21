---
name: w-novelty
description: "Check generated themes for originality against known classical melodies. Flags potential plagiarism and requests regeneration."
argument-hint: "<piece-id>"
---

# /w-novelty -- Originality Check for Generated Themes

You are checking the generated themes for a Wolfgang composition against known classical melodies to detect potential unintentional plagiarism. Parse the arguments to extract the piece-id.

## Step 1: Read Themes

Read `workspace/<piece-id>/themes.json`. This file contains the generated themes with their ABC notation. Each theme entry should have at minimum a name/label and ABC note sequence.

If the file does not exist, report the error and stop.

## Step 2: Extract Fingerprints

For each theme in the file, compute three fingerprints:

### A. Interval Profile
Extract the sequence of semitone intervals between consecutive pitches (ignoring rhythm). Use signed integers: +2 means up a whole step, -1 means down a semitone, 0 means repeated note.

Example: C D E C -> [+2, +2, -4]

### B. Parsons Contour Code
Convert the melody to Parsons code (direction-only representation):
- `*` for the first note (reference)
- `U` for each note higher than the previous
- `D` for each note lower than the previous
- `R` for each note the same as the previous

Example: C D E C -> *UUD

### C. Rhythm Profile
Extract the sequence of note durations as ratios relative to the beat unit, independent of pitch.

Example: quarter, quarter, half, quarter -> [1, 1, 2, 1]

## Step 3: Compare Against Known Themes

### 3a. Famous Themes Index
Read `famous-themes-index.md` (check in `.claude/context/`, `tools/`, and project root). This file contains curated interval patterns for well-known classical themes. Compare each generated theme's interval profile against entries in the index.

### 3b. Python Checker
Check if `tools/novelty_checker.py` exists. If it does, run it:
```
python3 tools/novelty_checker.py workspace/<piece-id>/themes.json
```
Parse its output for any flagged matches.

### 3c. Web Search (Optional)
For any theme that looks potentially common (simple stepwise motion, triadic patterns, very singable contours), use WebSearch to query:
- Search the Parsons code on Musipedia if possible: "musipedia [parsons-code]"
- Search the interval sequence: "classical melody intervals [first 6-8 intervals]"
- Search for the note sequence itself: "[note names] classical theme"

This step is supplementary. Not all themes need web checking -- focus on themes that have simple, memorable patterns most likely to collide with existing works.

## Step 4: Matching Algorithm

For each generated theme compared against each known theme:

1. **Interval similarity**: Compute the longest common subsequence (LCS) of the interval profiles. Calculate: `similarity = LCS_length / min(len(generated), len(known))`

2. **Rhythm similarity**: Same LCS approach on rhythm profiles.

3. **Combined score**: `combined = (0.6 * interval_similarity) + (0.4 * rhythm_similarity)`

4. **Flag threshold**: If `combined > 0.70` (70%), flag the match.

5. **Contour check**: If the Parsons codes share a prefix of 8+ symbols, flag as additional concern even if the combined score is below threshold.

## Step 5: Generate Report

For each theme, produce a result:

```json
{
  "theme_name": "main_theme_A",
  "status": "clear|flagged|warning",
  "interval_profile": [2, 2, -4, ...],
  "parsons_code": "*UUD...",
  "rhythm_profile": [1, 1, 2, 1, ...],
  "matches": [
    {
      "known_theme": "Beethoven Symphony 5 - Opening motif",
      "interval_similarity": 0.85,
      "rhythm_similarity": 0.72,
      "combined_score": 0.80,
      "concern": "Opening 4-note rhythm pattern matches exactly",
      "suggestion": "Alter the rhythm in bar 1: change dotted-eighth-sixteenth to even eighths, or modify the opening interval from -3 to -4"
    }
  ]
}
```

Status levels:
- **clear**: combined score < 0.50 against all known themes
- **warning**: combined score 0.50-0.70, or Parsons prefix match 6-7 symbols
- **flagged**: combined score > 0.70, or Parsons prefix match 8+ symbols

## Step 6: Write Suggestions for Flagged Themes

For each flagged theme, provide specific, actionable suggestions:

- **Which notes to change**: "Alter the 3rd note from E to F# (change interval from +4 to +6)"
- **Which rhythms to change**: "Change bar 2 from [dotted quarter, eighth] to [quarter, quarter]"
- **Minimum edit distance**: Suggest the fewest changes needed to bring the combined score below 0.50
- **Preserve character**: Note which aspects of the theme are distinctive and should be kept

## Step 7: Write Output

Write the full report to `workspace/<piece-id>/novelty-report.json`:

```json
{
  "piece_id": "<piece-id>",
  "checked_at": "<ISO timestamp>",
  "themes_checked": 4,
  "themes_clear": 3,
  "themes_warning": 1,
  "themes_flagged": 0,
  "results": [ ... ],
  "overall_status": "pass|review-recommended|regeneration-needed",
  "summary": "3 of 4 themes are clear. Theme B has a warning-level similarity to Brahms Symphony 4 finale theme (0.58 combined). Consider minor interval adjustment in bars 3-4."
}
```

Overall status:
- **pass**: All themes clear or warning-only with low concern
- **review-recommended**: One or more warnings worth human review
- **regeneration-needed**: One or more themes flagged above 0.70

## Report

Print a concise summary:
- Number of themes checked
- Status of each theme (clear/warning/flagged)
- For any flagged or warning themes: what they resemble and suggested fixes
- Overall recommendation
