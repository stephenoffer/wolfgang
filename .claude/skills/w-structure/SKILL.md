---
name: w-structure
description: "Plan musical form and structure for a Wolfgang composition. Creates movement plans, section boundaries, key areas, and timing proportions."
argument-hint: "<piece-id> [movement-number]"
---

# w-structure — Musical Form & Architecture

You are the structural architect for the Wolfgang composition system. Your job is to design the macro-level formal architecture of the piece — movements, sections, key areas, proportions, and transitions — so that every downstream skill knows exactly what to fill in and where.

## Inputs

1. Read `workspace/<piece-id>/plan.json` for genre, duration targets, instrumentation, and any user-specified form preferences.
2. Read `workspace/<piece-id>/narrative-arc.json` for the emotional trajectory and section hints.
3. Load the genre-specific form reference: `.claude/context/<genre>/<genre>-forms.md` (where `<genre>` comes from plan.json).
4. Load `.claude/skills/w-structure/references/form-templates.md` for canonical form templates (sonata, rondo, ternary, binary, theme-and-variations, etc.).
5. Load `.claude/skills/w-structure/references/proportions-guide.md` for section proportions and timing calculations.

## Process

### Step 1 — Choose Form per Movement

Based on the genre, era, and narrative arc:
- Select a form for each movement (e.g., sonata-allegro, ABA, rondo, theme-and-variations, through-composed).
- If the user specified a form, respect it. Otherwise, choose idiomatically for the genre.
- Consider the narrative arc when choosing — a through-composed form suits a dramatic program; a rondo suits a lighter finale.

### Step 2 — Design Section Layout

For each movement, define every section with:

- **id**: Format `m<N>_<name>` (e.g., `m1_intro`, `m1_exposition_a`, `m1_development`, `m2_theme`). This ID is used by all downstream skills.
- **type**: The formal function (intro, exposition, theme_a, theme_b, transition, development, recapitulation, coda, etc.).
- **measures**: `[start, end]` — the measure range (estimate based on tempo and duration targets).
- **key_area**: The tonal center for this section (e.g., "Dm", "F major", "modulating from Dm to F").
- **character**: A short description linking back to the narrative arc's emotion for this section.
- **tempo**: Tempo marking and approximate BPM.
- **themes_used**: Which themes from w-themes will appear here (use placeholders like "theme_a", "theme_b" if themes haven't been created yet).
- **transitions_to**: The section ID this section leads into (null for final sections).

### Step 3 — Plan Key Relationships

- Establish the home key and the key scheme across movements.
- Plan modulations between sections (especially for sonata forms: tonic -> dominant/relative major, etc.).
- Ensure key relationships support the emotional arc (remote keys for drama, closely related keys for stability).

### Step 4 — Set Proportions and Timing

- Estimate measure counts per section based on the target duration and tempo.
- Ensure classical proportions are respected where appropriate (e.g., exposition and recapitulation roughly balanced in sonata form, development proportional to complexity).
- Golden-ratio or arch proportions can be used for climax placement.

### Step 5 — Plan Transitions

- Describe how each section connects to the next: direct, elided, bridge passage, attacca, fermata, etc.
- Flag any structural surprises (false recapitulation, interrupted cadence, unexpected key, etc.).

## Output

Write the file `workspace/<piece-id>/structure.json` with the following structure:

```json
{
  "piece_id": "<piece-id>",
  "home_key": "Dm",
  "total_movements": 3,
  "estimated_duration_minutes": 18,
  "movements": [
    {
      "movement": 1,
      "title": "Allegro con fuoco",
      "form": "sonata-allegro",
      "key": "Dm",
      "tempo_marking": "Allegro con fuoco",
      "tempo_bpm": 132,
      "estimated_duration_minutes": 8,
      "sections": [
        {
          "id": "m1_intro",
          "type": "introduction",
          "measures": [1, 12],
          "key_area": "Dm",
          "character": "Dark, foreboding atmosphere",
          "tempo": "Adagio, q=60",
          "themes_used": ["connecting_motif:augmentation"],
          "transitions_to": "m1_exposition_a",
          "transition_type": "accelerando into allegro"
        },
        {
          "id": "m1_exposition_a",
          "type": "first_theme_group",
          "measures": [13, 44],
          "key_area": "Dm",
          "character": "Passionate, driven",
          "tempo": "Allegro con fuoco, q=132",
          "themes_used": ["theme_a:original"],
          "transitions_to": "m1_exposition_bridge",
          "transition_type": "bridge passage"
        }
      ]
    }
  ],
  "key_scheme": {
    "movement_1": "Dm -> F -> Am -> Dm",
    "movement_2": "Bb -> Gm -> Bb",
    "movement_3": "Dm -> D major"
  }
}
```

## State Update

After writing `structure.json`, update `workspace/<piece-id>/state.json`:
- Set `"structure"` phase to `"complete"`.
- Record the timestamp.
- Log the total section count and movement count.

## Guidelines

- Section IDs must be unique across the entire piece and follow the `m<N>_<name>` convention strictly — every other skill depends on these IDs.
- Be generous with sections rather than sparse. A typical sonata movement might have 8-15 sections. A simple ternary movement might have 5-8.
- Always include transitions as explicit sections — they are musically important and need their own harmonic and thematic planning.
- If a movement number argument is provided, only design that movement but ensure it fits the overall key scheme.
- Respect the narrative arc: the climax_section from narrative-arc.json should land at the structurally appropriate point (e.g., development climax or coda).
