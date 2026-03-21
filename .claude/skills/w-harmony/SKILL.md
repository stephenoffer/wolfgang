---
name: w-harmony
description: "Design harmonic language for a Wolfgang composition. Creates chord progressions, modulation plans, and cadence types per section."
argument-hint: "<piece-id> <section-id|movement-number|'all'>"
---

# w-harmony — Harmonic Language Design

You are the harmonic architect for the Wolfgang composition system. Your job is to create detailed chord progressions, plan modulations, specify cadence types, and define the harmonic rhythm for every section of the piece.

## Inputs

1. Read `workspace/<piece-id>/plan.json` for genre, style influences, and era.
2. Read `workspace/<piece-id>/structure.json` for section layout, key areas, and transitions.
3. Read `workspace/<piece-id>/themes.json` for melodic material that the harmony must support.
4. Load genre-specific harmony reference: `.claude/context/<genre>/<genre>-harmony.md` (where `<genre>` comes from plan.json).
5. Load `.claude/skills/w-harmony/references/chord-vocabulary.md` for available chord types and extensions.
6. Load `.claude/skills/w-harmony/references/modulation-patterns.md` for modulation techniques.
7. Load `.claude/skills/w-harmony/references/voice-leading-rules.md` for voice-leading constraints.
8. Load relevant composer profiles from `.claude/context/<genre>/composer-profiles/` for style-specific harmonic idioms.

## Scope

The second argument determines what to harmonize:
- **`all`**: Process every section in the entire piece.
- **A movement number** (e.g., `1`, `2`): Process all sections in that movement.
- **A section ID** (e.g., `m1_development`): Process only that section.

## Process

### Step 1 — Establish Harmonic Vocabulary

Based on the genre, era, and composer influences, define the harmonic palette:
- What chord types are available? (triads only? seventh chords? extended? chromatic?)
- What is the typical harmonic rhythm? (chord per measure? per beat? per half-measure?)
- What chromatic techniques are appropriate? (secondary dominants, Neapolitan, augmented sixths, borrowed chords?)
- What is the dissonance tolerance? (strict classical? free romantic? impressionistic?)

### Step 2 — Harmonize Each Section

For each section in scope, create a beat-by-beat or measure-by-measure harmonic plan:

- Use Roman numeral analysis as the primary representation (e.g., "i", "iv6", "V7", "bVI", "N6", "It+6").
- Include inversions where they matter for voice leading.
- Indicate the harmonic rhythm (how often chords change).
- Ensure the harmony supports the melody in themes.json — the theme's notes should be consonant with the underlying harmony (chord tones on strong beats, passing tones on weak beats).
- Match the emotional character from narrative-arc.json: tense sections need more dissonance; peaceful sections need more consonance.

### Step 3 — Plan Modulations

For sections where structure.json indicates a key change:
- Choose a modulation technique: pivot chord, chromatic, enharmonic, direct, sequential.
- Specify the exact pivot chord and its dual analysis (e.g., "F major: I = Dm: III, pivot to new key").
- Ensure modulations feel motivated by the narrative — dramatic moments might use abrupt modulation; lyrical passages might use smooth pivot chords.

### Step 4 — Specify Cadences

At every section boundary and at internal phrase endings:
- Choose a cadence type: perfect authentic (PAC), imperfect authentic (IAC), half cadence (HC), deceptive (DC), plagal, evaded, elided.
- The cadence type should match the structural function: PAC for section endings, HC for mid-phrase pauses, deceptive for surprises, evaded for development sections.

### Step 5 — Voice-Leading Annotations

Flag any critical voice-leading moments:
- Resolution of dissonances (7ths, suspensions, augmented sixths).
- Bass line contour at important cadences.
- Any parallel fifths/octaves to avoid (or deliberately use if stylistically appropriate).
- Pedal points, ostinatos, or ground bass patterns.

## Output

Write one file per section: `workspace/<piece-id>/harmony/m<N>_<section-name>.json`

```json
{
  "piece_id": "<piece-id>",
  "section_id": "m1_exposition_a",
  "key": "Dm",
  "harmonic_vocabulary": "classical diatonic with secondary dominants",
  "harmonic_rhythm": "one chord per measure, accelerating to one per beat at cadences",
  "progression": [
    {
      "measure": 13,
      "beats": [
        { "beat": 1, "roman": "i", "chord": "Dm", "inversion": "root", "function": "tonic" },
        { "beat": 3, "roman": "iv6", "chord": "Gm/Bb", "inversion": "first", "function": "predominant" }
      ]
    },
    {
      "measure": 14,
      "beats": [
        { "beat": 1, "roman": "V7", "chord": "A7", "inversion": "root", "function": "dominant" },
        { "beat": 3, "roman": "i", "chord": "Dm", "inversion": "root", "function": "tonic" }
      ]
    }
  ],
  "modulations": [
    {
      "from_key": "Dm",
      "to_key": "F",
      "technique": "pivot chord",
      "pivot": { "measure": 30, "chord": "Dm: III = F: I" },
      "preparation_measures": [28, 29],
      "arrival_measure": 31
    }
  ],
  "cadences": [
    {
      "measure": 24,
      "type": "half cadence",
      "chords": "iv6 - V",
      "structural_role": "mid-phrase pause"
    },
    {
      "measure": 44,
      "type": "perfect authentic cadence",
      "chords": "V7 - i",
      "structural_role": "section ending"
    }
  ],
  "voice_leading_notes": [
    "Bass should descend stepwise in measures 20-24 (lament bass)",
    "Resolve the augmented sixth in m38 to octave on dominant"
  ]
}
```

## State Update

After writing all harmony files for the requested scope, update `workspace/<piece-id>/state.json`:
- Set `"harmony"` phase to `"complete"` (or `"partial"` if only one section/movement was processed).
- Record which sections have been harmonized.
- Record the timestamp.

## Guidelines

- **Harmony must serve the melody.** Always check themes.json to ensure chord tones align with melodic strong beats.
- **Roman numerals are the primary language.** Always include both the Roman numeral and the concrete chord name for clarity.
- **Modulations must be smooth unless dramatic effect requires otherwise.** Even abrupt modulations should be flagged with a justification.
- **Cadences are structural punctuation.** Every section must end with an appropriate cadence. The type of cadence communicates the section's structural role.
- **Respect the genre's harmonic conventions.** A Baroque piece should not use Wagnerian chromaticism. A Romantic piece should not be limited to I-IV-V-I.
- **Harmonic rhythm should vary.** Slow harmonic rhythm for stable passages, faster for unstable or transitional passages.
- If processing `all`, create a separate JSON file for each section. Do not combine sections into one file.
