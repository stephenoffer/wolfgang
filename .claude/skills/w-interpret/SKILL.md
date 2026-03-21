---
name: w-interpret
description: "Translate images, abstract concepts, or existing piece references into musical parameters for Wolfgang composition."
argument-hint: "<piece-id> <type: 'image'|'concept'|'piece-reference'> <input description>"
---

# /w-interpret -- Translate Non-Musical Input into Musical Parameters

You are translating a non-musical input into concrete musical parameters for the Wolfgang composition pipeline. Parse the arguments to determine the piece-id, input type, and the input description.

## Step 1: Determine Input Type

From the arguments, identify which of the three modes applies:

- **image** -- the user has provided or described a visual image
- **concept** -- the user has provided an abstract idea, emotion, or narrative concept
- **piece-reference** -- the user has named an existing classical work they want to reference or arrange

---

## Mode A: Image Interpretation

When the input type is `image`:

1. **Analyze visual properties.** If the user provided an image file path, read it. Otherwise work from their description. Extract:
   - **Color palette**: warm tones (reds, oranges, yellows) suggest major modes, bright timbres; cool tones (blues, greens, purples) suggest minor modes, darker timbres
   - **Movement/energy**: static compositions (landscapes, portraits) map to slower tempi (Adagio-Andante); dynamic compositions (storms, battles, dance) map to faster tempi (Allegro-Presto)
   - **Mood**: serene, turbulent, melancholic, triumphant, mysterious, pastoral, etc.
   - **Subject matter**: nature, human figures, architecture, abstract forms
   - **Texture/density**: sparse images suggest chamber texture; dense/busy images suggest orchestral fullness
   - **Contrast**: high contrast suggests wide dynamic range (pp-ff); low contrast suggests narrower dynamics
   - **Light**: bright/luminous suggests upper registers; dark/shadowy suggests lower registers

2. **Use WebSearch** to find classical pieces associated with the subject matter. For example:
   - Ocean scene: search "ocean sea classical music orchestral" to find Debussy's La Mer, Mendelssohn's Hebrides Overture, Britten's Sea Interludes
   - Forest: search "forest woodland classical music" to find Weber's Der Freischutz, Sibelius tone poems
   - Use findings as stylistic reference points, not direct copies

3. **Map to parameters:**
   - `key` and `mode` (major/minor/modal)
   - `tempo_range` (BPM range)
   - `dynamics_range` (pp to ff)
   - `register` (low/mid/high preference)
   - `texture` (monophonic/homophonic/polyphonic, density 1-5)
   - `timbre_suggestion` (instrument families that evoke the visual)
   - `mood_keywords` (3-5 descriptors)
   - `reference_works` (pieces found via search that share the mood/subject)

## Mode B: Abstract Concept Interpretation

When the input type is `concept`:

1. **Parse the concept.** Identify the core emotion, idea, or narrative.

2. **Use WebSearch** to research how classical composers expressed this concept. Search for:
   - "[concept] in classical music"
   - "classical music expressing [concept]"
   - "musical representation of [concept] techniques"
   Gather specific compositional techniques used historically.

3. **Apply standard emotion-to-music mappings, refined by research:**

   | Concept | Tempo | Mode | Texture | Dynamics | Register | Devices |
   |---------|-------|------|---------|----------|----------|---------|
   | Joy/Triumph | Allegro-Vivace | Major | Full, homophonic | f-ff | Mid-High | Fanfares, ascending lines, dotted rhythms |
   | Sorrow/Grief | Adagio-Lento | Minor | Sparse, sighing figures | pp-mp | Low-Mid | Descending chromatic lines, suspensions |
   | Anger/Fury | Allegro-Presto | Minor | Dense, aggressive | ff-fff | Full range | Tremolo, driving rhythms, dissonance |
   | Peace/Serenity | Andante-Adagio | Major/Lydian | Open, transparent | pp-p | Mid-High | Pedal tones, gentle arpeggios, thirds |
   | Mystery | Moderato | Diminished/Whole-tone | Pointillistic | pp-mp | Extremes | Muted brass, pizzicato, tritones |
   | Heroism | Allegro | Major | Bold, unison passages | f-ff | Mid-High | Dotted rhythms, leaps, brass |
   | Longing/Nostalgia | Andante | Minor/Mixed | Lyrical melody + sparse accomp | mp-mf | Mid | Appoggiature, wide leaps, rubato feel |
   | Terror/Dread | Various | Chromatic | Unstable, shifting | pp or ff | Low/Extreme | Tremolo, dissonance clusters, silences |
   | Pastoral | Moderato-Andantino | Major/Mixolydian | Light, flowing | p-mf | Mid | Drones, parallel thirds, woodwind color |
   | Love/Tenderness | Adagio-Andante | Major | Warm, flowing | p-mp | Mid | Lyrical melody, rich harmony, strings |

   Adjust and extend these defaults based on WebSearch findings.

4. **Map to the same parameter set as Mode A.**

## Mode C: Existing Piece Reference

When the input type is `piece-reference`:

1. **Identify the work.** From the input description, determine the composer, title, and catalog number if possible.

2. **Use WebSearch** to gather comprehensive information:
   - Search "[composer] [title] analysis" for structural analysis
   - Search "[composer] [title] score" for key, orchestration, form details
   - Search "[composer] [title] themes" for thematic material descriptions
   - Search "[composer] [title] structure movements" for formal plan

3. **Extract and record:**
   - `key` and modulation plan
   - `form` (sonata, rondo, ABA, theme-and-variations, etc.)
   - `tempo_markings` for each movement/section
   - `orchestration` (full instrumentation list)
   - `themes` (verbal description of principal themes: contour, interval character, rhythm)
   - `stylistic_hallmarks` (what makes this piece distinctive)
   - `harmonic_language` (diatonic, chromatic, modal, etc.)

4. **If the user wants an arrangement or reduction**, gather enough detail that `/w-reduce` can work from the parameters. Note the essential voices, textural layers, and which instruments carry which thematic material.

5. **Map to the same parameter set, plus piece-specific fields.**

---

## Step 2: Write Output

Create or update `workspace/<piece-id>/plan.json` with the interpreted parameters. The JSON structure:

```json
{
  "piece_id": "<piece-id>",
  "interpretation_source": {
    "type": "image|concept|piece-reference",
    "input": "<original input description>",
    "interpreted_at": "<ISO timestamp>"
  },
  "musical_parameters": {
    "key": "C major",
    "mode": "major|minor|modal-specify",
    "tempo_range": [80, 120],
    "dynamics_range": ["pp", "ff"],
    "register": "low|mid|high|full",
    "texture": {
      "type": "homophonic|polyphonic|monophonic|mixed",
      "density": 3
    },
    "timbre_suggestion": ["strings", "woodwinds"],
    "mood_keywords": ["serene", "flowing", "luminous"],
    "devices": ["pedal tones", "arpeggios"],
    "form_suggestion": "ternary|sonata|rondo|free"
  },
  "reference_works": [
    {
      "composer": "Debussy",
      "title": "La Mer",
      "relevance": "ocean imagery, orchestral color"
    }
  ],
  "notes": "Free-text notes on interpretation choices and reasoning."
}
```

Ensure the `workspace/<piece-id>/` directory exists before writing. If `plan.json` already exists, merge the new interpretation into it (preserve existing fields, update changed ones, add an `interpretation_history` array).

## Step 3: Report

Print a summary to the user:
- What input was analyzed
- Key musical parameters chosen and why
- Reference works found
- Any ambiguities or choices the user should confirm before proceeding to composition
