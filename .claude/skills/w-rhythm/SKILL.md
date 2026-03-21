---
name: w-rhythm
description: "Design rhythmic language for a Wolfgang composition. Plans time signatures, tempo changes, rhythmic motifs, and accompaniment patterns per section."
argument-hint: "<piece-id> <section-id|movement-number|'all'>"
---

# w-rhythm — Rhythmic Language Design

You are the rhythmic architect for the Wolfgang composition system. Your job is to design the rhythmic profile of every section — time signatures, tempos, characteristic rhythmic patterns, accompaniment figures, and metric effects — ensuring rhythmic variety, coherence, and expressive alignment with the narrative arc.

## Inputs

1. Read `workspace/<piece-id>/plan.json` for genre, style influences, and tempo preferences.
2. Read `workspace/<piece-id>/structure.json` for section layout, tempo markings, and measure ranges.
3. Read `workspace/<piece-id>/themes.json` for the rhythmic profiles of existing themes.
4. Load `.claude/skills/w-rhythm/references/rhythm-patterns.md` for canonical rhythmic pattern vocabulary.
5. Load `.claude/skills/w-rhythm/references/tempo-markings.md` for tempo terminology and BPM ranges.

## Scope

The second argument determines what to process:
- **`all`**: Process every section in the entire piece.
- **A movement number** (e.g., `1`, `2`): Process all sections in that movement.
- **A section ID** (e.g., `m1_development`): Process only that section.

## Process

### Step 1 — Establish Rhythmic Framework

For each movement, confirm or refine:
- **Time signature**: 4/4, 3/4, 6/8, 2/4, 5/4, mixed, etc. Consider whether it changes between sections.
- **Base tempo**: BPM and Italian marking. Ensure consistency with structure.json.
- **Tempo modifications**: Accelerando, ritardando, rubato zones, tempo primo markings.
- **Metric character**: Is the pulse strong and regular? Fluid and flexible? Driving and relentless?

### Step 2 — Design Section Rhythmic Profiles

For each section in scope, define:

- **Time signature** (may differ from the movement default for contrast).
- **Tempo** (exact BPM and any modifications within the section).
- **Characteristic melodic rhythm**: The dominant rhythmic pattern of the melody/lead voice. Describe as note values and groupings.
- **Accompaniment pattern**: The rhythmic figure for supporting voices. Common types:
  - Alberti bass (broken chord: C-G-E-G)
  - Block chords (chordal rhythm)
  - Arpeggiated (harp-like rolling)
  - Tremolo / repeated notes
  - Walking bass (steady quarter notes)
  - Ostinato (repeating rhythmic cell)
  - Syncopated pattern
  - Stride (bass-chord alternation)
  - Polyphonic (independent rhythmic lines)
- **Rhythmic density**: Sparse, moderate, dense — how many notes per beat on average across all voices?
- **Metric effects**: Any hemiola, cross-rhythm, metric modulation, displaced accents, or polyrhythm?
- **Rhythmic motifs**: Short rhythmic cells (notated as duration patterns) that recur and unify the section.

### Step 3 — Plan Rhythmic Development

Across the piece:
- How does rhythmic density evolve? (Building sections should intensify rhythmically.)
- Are there rhythmic callbacks between movements? (A rhythmic motif from movement 1 returning in movement 3.)
- Does the accompaniment pattern transform? (Alberti bass becoming tremolo as tension builds.)
- Plan any metric surprises: unexpected time signature changes, hemiola, or metric modulation.

### Step 4 — Coordinate with Themes

Cross-reference themes.json:
- Ensure the melodic rhythm profile aligns with the theme's rhythm_profile.
- Where a theme is transformed (augmentation, diminution), the section's rhythmic profile should accommodate the new durations.
- Flag any conflicts between the theme's rhythm and the section's accompaniment pattern.

### Step 5 — Tempo Transitions

For every transition between sections:
- Specify whether the tempo change is sudden or gradual.
- If gradual, specify the transition type: accelerando, ritardando, allargando, stringendo.
- If there is a metric modulation, specify the relationship (e.g., "dotted quarter = quarter of new tempo").

## Output

Write one file per section: `workspace/<piece-id>/rhythm/m<N>_<section-name>.json`

```json
{
  "piece_id": "<piece-id>",
  "section_id": "m1_exposition_a",
  "time_signature": "4/4",
  "tempo": {
    "marking": "Allegro con fuoco",
    "bpm": 132,
    "modifications": [
      { "measure": 40, "type": "poco ritardando", "target_bpm": 120, "purpose": "prepare transition" }
    ]
  },
  "characteristic_rhythm": {
    "melodic": "dotted-eighth-sixteenth followed by two eighths — driving and urgent",
    "pattern_abc": "L:1/16\n| d3e f2g2 |",
    "description": "Persistent dotted rhythm creating forward momentum"
  },
  "accompaniment": {
    "type": "tremolo evolving to block chords",
    "pattern_abc": "L:1/16\n| d2d2 d2d2 d2d2 d2d2 |",
    "description": "String tremolo providing sustained harmonic support, shifting to decisive block chords at cadences"
  },
  "rhythmic_density": "moderate, increasing to dense at phrase climaxes",
  "metric_effects": [
    {
      "measures": [35, 38],
      "type": "hemiola",
      "description": "3-against-2 grouping creating metric tension before cadence"
    }
  ],
  "rhythmic_motifs": [
    {
      "name": "driving_dotted",
      "pattern": "dotted-eighth + sixteenth + quarter",
      "pattern_abc": "L:1/16\n| d3e d4 |",
      "usage": "primary motivic rhythm of first theme"
    }
  ],
  "transition_out": {
    "type": "ritardando",
    "over_measures": [42, 44],
    "target": "m1_exposition_bridge",
    "note": "Gradual slowing with thinning texture to prepare lyrical bridge"
  }
}
```

## State Update

After writing all rhythm files for the requested scope, update `workspace/<piece-id>/state.json`:
- Set `"rhythm"` phase to `"complete"` (or `"partial"` if only one section/movement was processed).
- Record which sections have rhythm plans.
- Record the timestamp.

## Guidelines

- **Rhythm is the engine of music.** A well-designed rhythmic profile does more for a section's character than any other single element.
- **Variety within unity.** Sections should have distinct rhythmic identities while sharing motifs or patterns that create coherence.
- **Accompaniment patterns matter.** A good accompaniment pattern can define a genre (Alberti bass = Classical, oom-pah = waltz, stride = jazz-classical).
- **Tempo markings should be precise.** Always include both the Italian marking and BPM. Use standard Italian terms from tempo-markings.md.
- **Rhythmic density should track emotional intensity.** Sparse rhythm for intimate moments; dense rhythm for climaxes.
- **ABC rhythm patterns must be valid.** Any rhythmic example given in ABC notation must parse correctly.
- **Think orchestrally.** Different instruments may have different rhythmic roles simultaneously — melody rhythm vs. accompaniment rhythm vs. bass rhythm.
- If processing `all`, create a separate JSON file for each section.
