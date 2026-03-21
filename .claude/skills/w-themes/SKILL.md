---
name: w-themes
description: "Create and develop musical themes and motifs for a Wolfgang composition. Defines themes as ABC fragments, plans variations, inversions, augmentations."
argument-hint: "<piece-id> ['create'|'develop' section-id|'catalog'|'regenerate' theme-name]"
---

# w-themes — Theme Creation & Development

You are the thematic inventor for the Wolfgang composition system. Your job is to create memorable, well-crafted musical themes as ABC notation fragments, pre-compute all their transformations, and plan exactly how they will be used across the entire piece.

## Inputs

1. Read `workspace/<piece-id>/plan.json` for genre, style influences, instrumentation, and any user-specified melodic preferences.
2. Read `workspace/<piece-id>/structure.json` for the section layout, key areas, and tempo markings.
3. Read `workspace/<piece-id>/narrative-arc.json` for the emotional trajectory and character of each section.
4. Load composer profiles from `.claude/context/<genre>/composer-profiles/` for any style influences specified in plan.json.
5. Load `.claude/skills/w-themes/references/thematic-techniques.md` for transformation techniques.
6. Load `.claude/skills/w-themes/references/motif-development-guide.md` for motivic development strategies.

## Modes of Operation

### Mode: `create` (default)

Create all themes for the piece from scratch.

### Mode: `develop <section-id>`

Take existing themes and create new variants specifically tailored for the given section, considering its key area, emotional character, and structural role.

### Mode: `catalog`

Read the existing themes.json and produce a human-readable catalog summarizing all themes, their characters, and their planned usage.

### Mode: `regenerate <theme-name>`

Replace a specific theme with a new one while preserving its role in the usage plan.

## Process (Create Mode)

### Step 1 — Determine Theme Requirements

From structure.json, identify how many distinct themes are needed:
- Sonata form: at least 2 contrasting themes (plus closing theme optional)
- Rondo: main refrain theme plus episode themes
- Ternary: A theme and B theme
- Theme and variations: one strong theme
- Always: one connecting motif

### Step 2 — Compose Themes in ABC Notation

For each theme, write a 4-8 measure ABC fragment. Each theme must:

- Be in valid ABC notation with proper headers (K:, M:, L: at minimum).
- Have a clear melodic profile: identifiable intervals, distinctive rhythm.
- Suit the character described in the narrative arc.
- Be idiomatic for the specified instruments.
- Contrast with the other themes (if theme A is stepwise and lyrical, theme B might be angular and rhythmic).
- Fit the key area specified in structure.json for its primary appearance.

### Step 3 — Analyze Each Theme

For each theme, compute:
- **intervals**: Array of interval descriptions (e.g., `["+2", "+2", "+3", "-2", "-5", "+4"]` where + is ascending, - is descending, numbers are semitones).
- **rhythm_profile**: Prose description of the rhythmic character (e.g., "long-short-short | long-short-short | long-long | long").
- **character**: Descriptive tags (e.g., "passionate, yearning, wide leaps").
- **home_key**: The key in which the theme is originally stated.

### Step 4 — Pre-Compute ALL Transformations

For every theme, generate ABC notation for each transformation:

- **inversion**: Flip all intervals (ascending becomes descending and vice versa), keeping the rhythm identical.
- **augmentation**: Double all note durations.
- **diminution**: Halve all note durations.
- **retrograde**: Reverse the note order, keeping rhythm aligned.
- **fragmentation**: Extract meaningful sub-phrases:
  - **head**: The first 2-3 notes (the most recognizable fragment).
  - **tail**: The last 2-3 notes.
  - **leap**: The most distinctive interval, isolated.

Every transformation must be valid ABC notation.

### Step 5 — Create the Connecting Motif

Design a short motif (3-5 notes) that:
- Is intervallically distinctive and instantly recognizable.
- Can fit into any key and any texture.
- Appears in EVERY movement of the piece.
- Works as a unifying thread across contrasting material.

Apply the same transformation set to the connecting motif.

### Step 6 — Build the Usage Plan

Create a mapping from every section ID (from structure.json) to the themes and transformations used in that section. Format: `"<theme_name>:<transformation>"` where transformation is one of: original, inversion, augmentation, diminution, retrograde, fragmentation_head, fragmentation_tail, fragmentation_leap.

Every section must have at least one theme or motif assigned. Development sections should use multiple transformations. The connecting motif should appear in the first and last sections of every movement at minimum.

## Output

Write the file `workspace/<piece-id>/themes.json`:

```json
{
  "piece_id": "<piece-id>",
  "themes": {
    "theme_a": {
      "label": "Main Theme A - Passionate declaration",
      "abc": "K:Dm\nM:4/4\nL:1/8\n|: d2 ef | g2 fe | d2 A2 | d4 :|",
      "intervals": ["+2", "+2", "+3", "-2", "-2", "-5", "+4"],
      "rhythm_profile": "long-short-short | long-short-short | long-long | long",
      "character": "passionate, yearning, wide leaps",
      "home_key": "Dm",
      "transformations": {
        "inversion": "K:Dm\nM:4/4\nL:1/8\n|: d2 cB | A2 Bc | d2 g2 | d4 :|",
        "augmentation": "K:Dm\nM:4/4\nL:1/4\n|: d2 ef | g2 fe | d2 A2 | d4 :|",
        "diminution": "K:Dm\nM:4/4\nL:1/16\n|: d2 ef | g2 fe | d2 A2 | d4 :|",
        "retrograde": "K:Dm\nM:4/4\nL:1/8\n|: d4 | A2 d2 | ef g2 | fe d2 :|",
        "fragmentation": {
          "head": "K:Dm\nM:4/4\nL:1/8\n| d2 ef |",
          "tail": "K:Dm\nM:4/4\nL:1/8\n| d2 A2 | d4 |",
          "leap": "K:Dm\nM:4/4\nL:1/8\n| A2 d2 |"
        }
      }
    },
    "theme_b": {
      "label": "Second Theme B - Lyrical tenderness",
      "abc": "...",
      "intervals": ["..."],
      "rhythm_profile": "...",
      "character": "...",
      "home_key": "...",
      "transformations": { "..." : "..." }
    }
  },
  "connecting_motif": {
    "label": "Connecting Motif - Fate knocking",
    "abc": "K:Dm\nM:4/4\nL:1/8\n| d2 d2 d2 A2 |",
    "intervals": ["+0", "+0", "-5"],
    "rhythm_profile": "even, insistent",
    "character": "stark, memorable, rhythmically driven",
    "home_key": "Dm",
    "transformations": {
      "inversion": "...",
      "augmentation": "...",
      "diminution": "...",
      "retrograde": "...",
      "fragmentation": { "head": "...", "tail": "...", "leap": "..." }
    }
  },
  "usage_plan": {
    "m1_intro": ["connecting_motif:original"],
    "m1_exposition_a": ["theme_a:original", "connecting_motif:fragmentation_head"],
    "m1_exposition_b": ["theme_b:original"],
    "m1_development": ["theme_a:inversion", "theme_a:fragmentation_head", "theme_b:augmentation", "connecting_motif:diminution"],
    "m1_recapitulation_a": ["theme_a:original"],
    "m1_recapitulation_b": ["theme_b:original"],
    "m1_coda": ["theme_a:fragmentation_head", "connecting_motif:augmentation"]
  }
}
```

## State Update

After writing `themes.json`, update `workspace/<piece-id>/state.json`:
- Set `"themes"` phase to `"complete"`.
- Record the timestamp.
- Log the number of themes created and total transformation count.

## Guidelines

- **Melodic quality is paramount.** Themes must be singable, memorable, and have clear contour. Avoid random note sequences.
- **ABC notation must be valid.** Double-check all headers, bar lines, note lengths, and accidentals.
- **Contrasting themes must truly contrast.** If theme A moves by step, theme B should have leaps. If theme A is rhythmically even, theme B should be syncopated.
- **The connecting motif must be short enough to embed anywhere** — 3-5 notes maximum. Think Beethoven's Fifth (da-da-da-DUM) or Wagner's leitmotifs.
- **Transformations must be musically correct.** Inversion flips intervals, not just random rewriting. Augmentation exactly doubles durations. Retrograde reverses note order.
- **The usage plan must cover every section** in structure.json. No section should be left without thematic material assigned.
- When in `develop` mode, consider the section's key area and transpose themes accordingly.
- When in `regenerate` mode, preserve the character tags and structural role of the original theme.
