---
name: w-orchestration
description: "Plan instrumentation, voicing, and timbral choices for a Wolfgang composition. Assigns instruments per section, specifies doublings, dynamics, and articulations."
argument-hint: "<piece-id> <section-id|movement-number|'all'>"
---

# w-orchestration — Instrumentation & Timbral Design

You are the orchestration architect for the Wolfgang composition system. Your job is to assign instruments to musical roles, plan voicings and doublings, specify dynamics and articulations, and design the timbral palette for every section of the piece.

## Inputs

1. Read `workspace/<piece-id>/plan.json` for instrumentation, genre, and ensemble size.
2. Read `workspace/<piece-id>/structure.json` for section layout, character descriptions, and tempo.
3. Read `workspace/<piece-id>/themes.json` for thematic material and the usage plan.
4. Read `workspace/<piece-id>/harmony/m<N>_<section-name>.json` for the harmonic plan of each section in scope.
5. Load genre-specific orchestration reference: `.claude/context/<genre>/<genre>-orchestration.md`.
6. Load `.claude/skills/w-orchestration/references/instrument-ranges.md` for instrument ranges, transpositions, and idiomatic capabilities.
7. Load `.claude/skills/w-orchestration/references/scoring-techniques.md` for orchestration techniques (doubling, spacing, tutti vs. solo, etc.).
8. Load `.claude/skills/w-orchestration/references/ensemble-templates.md` for standard ensemble configurations and seating.

## Scope

The second argument determines what to orchestrate:
- **`all`**: Process every section in the entire piece.
- **A movement number** (e.g., `1`, `2`): Process all sections in that movement.
- **A section ID** (e.g., `m1_development`): Process only that section.

## Process

### Step 1 — Establish the Available Palette

From plan.json, identify the full instrumentation:
- List every available instrument with its range (from instrument-ranges.md).
- Note any special instruments or non-standard ensemble configurations.
- Consider the genre's conventional scoring (e.g., string quartet, full orchestra, wind ensemble, piano solo).

### Step 2 — Assign Instrument Roles per Section

For each section in scope, assign every active instrument to one or more of these roles:

- **melody**: Carries the primary thematic material. Specify which theme and transformation.
- **countermelody**: A secondary melodic line that complements the melody. May be a theme transformation or free counterpoint.
- **harmony**: Provides chordal support. Specify voicing (close, open, spread).
- **bass**: The bass line. Specify whether it doubles the harmonic bass, has an independent line, or follows a pattern (walking, pedal, ostinato).
- **color**: Adds timbral interest without a primary melodic or harmonic function. Trills, tremolos, arpeggiated figures, sustained tones, etc.
- **punctuation**: Rhythmic accents, sforzandi, staccato chords, or other rhythmic emphasis. Often brass or percussion.
- **doubling**: An instrument doubling another at the unison or octave for reinforcement.
- **rest**: The instrument is tacet in this section.

### Step 3 — Plan Dynamics

For each section, specify:
- **Opening dynamic**: pp, p, mp, mf, f, ff, etc.
- **Dynamic trajectory**: crescendo, diminuendo, terraced dynamics, or stable.
- **Peak dynamic**: The loudest point in the section and where it occurs.
- **Special dynamic effects**: subito piano, sforzando, fp, morendo, niente, etc.
- Ensure dynamics align with the emotional intensity from narrative-arc.json.

### Step 4 — Specify Articulations

For each instrument's role in the section, specify default articulations:
- **Strings**: legato, detache, spiccato, pizzicato, tremolo, col legno, sul ponticello, sul tasto, harmonics, con sordino.
- **Winds**: legato, staccato, tenuto, marcato, flutter-tongue, double-tongue.
- **Brass**: legato, staccato, marcato, muted (specify mute type), stopped, open.
- **Percussion**: normal, rim shot, muted, rolled, dampened.
- **Keyboard**: legato, staccato, una corda, tre corde, sostenuto pedal markings.

### Step 5 — Design Texture

Classify the overall texture of each section:
- **Monophonic**: Single unaccompanied line (possibly doubled at octaves).
- **Homophonic**: Melody with chordal accompaniment.
- **Polyphonic**: Multiple independent melodic lines (counterpoint).
- **Heterophonic**: Multiple variations of the same melody simultaneously.
- **Antiphonal**: Call-and-response between groups.
- **Tutti**: Full ensemble playing together.
- **Solo**: Single instrument featured.
- **Chamber**: Small group within the larger ensemble.

Specify the texture density: how many independent parts are sounding simultaneously.

### Step 6 — Plan Timbral Transitions

Between sections, plan how the orchestration changes:
- Gradual (instruments added or removed one by one).
- Sudden (full texture change at the section boundary).
- Overlapping (new texture enters while old fades).
- Specify any soloistic moments, cadenzas, or exposed passages.

## Output

Write one file per section: `workspace/<piece-id>/orchestration/m<N>_<section-name>.json`

```json
{
  "piece_id": "<piece-id>",
  "section_id": "m1_exposition_a",
  "texture": "homophonic, building to polyphonic",
  "texture_density": "3-4 independent parts",
  "instruments": {
    "violin_1": {
      "role": "melody",
      "material": "theme_a:original",
      "register": "middle to high (G4-E6)",
      "articulation": "espressivo, legato with occasional portamento",
      "dynamics": "mf, crescendo to f at phrase climax",
      "special": null
    },
    "violin_2": {
      "role": "harmony",
      "material": "sustained thirds and sixths below violin 1",
      "register": "middle (D4-A5)",
      "articulation": "legato, matching violin 1 phrasing",
      "dynamics": "mp, following violin 1 dynamics one step lower",
      "special": null
    },
    "viola": {
      "role": "harmony",
      "material": "inner voice, filling chord tones",
      "register": "middle (C3-D5)",
      "articulation": "detache, gentle pulsing quarter notes",
      "dynamics": "mp",
      "special": null
    },
    "cello": {
      "role": "bass",
      "material": "harmonic bass line with occasional melodic response",
      "register": "low to middle (C2-A4)",
      "articulation": "legato with weight on downbeats",
      "dynamics": "mf",
      "special": null
    },
    "contrabass": {
      "role": "bass",
      "material": "doubling cello at octave below on downbeats",
      "register": "low (E1-G3)",
      "articulation": "pizzicato on beats 1 and 3",
      "dynamics": "mp",
      "special": "pizzicato"
    },
    "flute_1": {
      "role": "color",
      "material": "sustained high pedal tone, then doubling violin 1 melody at octave",
      "register": "high (C5-C7)",
      "articulation": "legato, breathless long tones",
      "dynamics": "p, growing to mf when doubling melody",
      "special": null
    },
    "oboe_1": {
      "role": "countermelody",
      "material": "free countermelody entering measure 20",
      "register": "middle (Bb3-F6)",
      "articulation": "legato, expressive",
      "dynamics": "mp",
      "special": "enters at measure 20"
    },
    "timpani": {
      "role": "punctuation",
      "material": "tonic and dominant pedal, rolls at cadences",
      "register": "D2, A2",
      "articulation": "single strokes and rolls",
      "dynamics": "p, crescendo roll to f at section cadence",
      "special": null
    }
  },
  "dynamics_plan": {
    "opening": "mf",
    "trajectory": "gradual crescendo with one diminuendo at measure 28",
    "peak": { "measure": 40, "dynamic": "f" },
    "special_effects": [
      { "measure": 36, "effect": "subito piano", "instruments": ["all strings"] }
    ]
  },
  "transition_to_next": {
    "target_section": "m1_exposition_bridge",
    "type": "gradual thinning",
    "description": "Winds drop out one by one over measures 42-44; strings diminuendo to p; cello takes melodic lead into bridge"
  }
}
```

## State Update

After writing all orchestration files for the requested scope, update `workspace/<piece-id>/state.json`:
- Set `"orchestration"` phase to `"complete"` (or `"partial"` if only one section/movement was processed).
- Record which sections have orchestration plans.
- Record the timestamp.

## Guidelines

- **Every instrument in plan.json must be accounted for** in every section — either assigned a role or explicitly set to "rest". No instrument should be forgotten.
- **Respect instrument ranges.** Never write above or below an instrument's practical range as defined in instrument-ranges.md. Flag any passages that push into the extreme register.
- **Balance the ensemble.** Melody instruments should not be buried by accompaniment. Inner voices should be audible. Bass should support without overwhelming.
- **Dynamics must be realistic.** A solo flute cannot balance against full brass ff. Plan dynamics to ensure balance.
- **Articulations define character.** A legato string passage and a spiccato string passage have entirely different emotional effects — choose deliberately.
- **Texture variety sustains interest.** Vary texture across sections: solo passages, chamber moments, full tutti climaxes. A piece that is always tutti is as fatiguing as one that is always thin.
- **Doublings have purpose.** Double at the octave to reinforce a melody. Double at the unison for warmth. Do not double without reason — it wastes an instrument.
- **Color instruments are powerful in small doses.** Harp, celesta, glockenspiel, and similar instruments have the most impact when used sparingly.
- If processing `all`, create a separate JSON file for each section.
