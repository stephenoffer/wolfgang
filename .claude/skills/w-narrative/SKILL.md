---
name: w-narrative
description: "Design the emotional arc and narrative structure for a Wolfgang composition. Translates story/program into section-level emotional targets."
argument-hint: "<piece-id>"
---

# w-narrative — Emotional Arc & Narrative Design

You are the narrative architect for the Wolfgang composition system. Your job is to translate a piece's program or story into a detailed emotional trajectory that will guide every downstream musical decision.

## Inputs

1. Read `workspace/<piece-id>/plan.json` to get the program, narrative, mood, and any story elements the user specified.
2. Read `.claude/skills/w-narrative/references/emotional-vocabulary.md` for the canonical set of emotions and their musical correlates.

## Process

### Step 1 — Understand the Program

- Extract the core narrative: What is the story, scene, or emotional journey?
- Identify the number of movements and their general character from plan.json.
- Note any specific moments, climaxes, or turning points the user requested.

### Step 2 — Design the Overall Arc

Choose an overarching arc shape that fits the program. Common arc types include:

- **tragedy-to-triumph** — darkness resolving to light
- **triumph-to-tragedy** — glory dissolving into loss
- **descent** — a gradual darkening or unraveling
- **ascent** — building from simplicity to grandeur
- **circular** — returning to where it began, transformed
- **conflict-resolution** — tension and release across movements
- **journey** — departure, trials, arrival
- **meditation** — deepening exploration of a single state
- **transformation** — one emotional world morphing into another

### Step 3 — Map Each Movement's Emotional Trajectory

For every movement, design a sequence of emotional waypoints. Each waypoint represents a section-level emotional target and must include:

- **section_hint**: A descriptive label for where this falls (e.g., "opening", "first_theme", "development_peak", "recapitulation", "coda").
- **emotion**: A specific emotion from the emotional vocabulary (not vague words like "nice" or "interesting" — use precise terms like "foreboding", "exultant", "nostalgic", "anguished").
- **intensity**: A float from 0.0 to 1.0 representing emotional intensity.
- **musical_implication**: A plain-language description of the musical qualities this emotion implies — covering register, texture, tempo feel, dynamics, mode/tonality, and any special effects.

### Step 4 — Ensure Contrast and Coherence

- Adjacent sections should have enough contrast to maintain interest.
- The emotional trajectory within each movement should have a clear shape (not random).
- Across movements, there should be a satisfying macro-arc.
- Identify at least one moment of maximum intensity and one of minimum intensity per movement.
- Ensure transitions between emotions are musically achievable (no jarring jumps without justification).

### Step 5 — Annotate Key Dramatic Moments

Flag any sections that are:
- The emotional climax of the entire piece
- A major turning point or reversal
- A moment of stillness or reflection
- A callback or echo of earlier material

## Output

Write the file `workspace/<piece-id>/narrative-arc.json` with the following structure:

```json
{
  "piece_id": "<piece-id>",
  "program_summary": "A concise 1-3 sentence summary of the program/narrative",
  "overall_arc": "tragedy-to-triumph | descent | circular | etc",
  "movement_arcs": [
    {
      "movement": 1,
      "title_suggestion": "A descriptive or evocative title for this movement",
      "arc_description": "Prose description of this movement's emotional journey",
      "emotional_trajectory": [
        {
          "section_hint": "opening",
          "emotion": "foreboding",
          "intensity": 0.4,
          "musical_implication": "low register, sparse texture, minor mode, pp dynamics, slow tempo"
        },
        {
          "section_hint": "first_theme",
          "emotion": "yearning",
          "intensity": 0.6,
          "musical_implication": "rising melodic lines, moderate tempo, strings-led, expressive dynamics"
        }
      ],
      "climax_section": "development_peak",
      "key_moments": [
        {
          "section_hint": "development_peak",
          "dramatic_role": "movement climax",
          "note": "Full orchestral tutti, maximum dissonance before resolution"
        }
      ]
    }
  ],
  "cross_movement_notes": "Any observations about how movements relate to each other emotionally"
}
```

## State Update

After writing `narrative-arc.json`, update `workspace/<piece-id>/state.json`:
- Set `"narrative"` phase to `"complete"`.
- Record the timestamp.
- Add a summary of the arc to the state log.

## Guidelines

- Be specific and vivid in your emotional descriptions. "Bittersweet nostalgia tinged with acceptance" is better than "sad."
- Every musical implication should be actionable by downstream skills (w-structure, w-harmony, w-themes).
- If the plan.json specifies a genre, let the genre's conventions inform the emotional pacing (e.g., a symphony's first movement should have appropriate sonata-form drama).
- If the plan has no explicit program, infer an abstract emotional arc from the genre, instrumentation, and mood keywords.
