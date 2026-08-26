---
name: w-plan
description: "Unified planning: contract, style, narrative arc, form graph, and motifs — the complete musical architecture, written to the PieceGraph before any composing begins."
argument-hint: "<piece-id>"
---

# w-plan — Unified Composition Planning

Plan the complete musical architecture: PieceContract, StyleDNA, NarrativeArc, FormGraph (PhraseSlots), and MotifBank. All written to PieceGraph before any sketching begins.

## Step 1: Compile Style — but first, confirm the corpus is armed

Planning a composer with no (or thin) corpus wastes the whole pipeline — every
brief comes back `brief_insufficient`. Before compiling, confirm each target
composer is armed AND rich:

```bash
.venv/bin/python -m scripts.acquire_composer --status <composer>   # tier + records_rich
```

If `tier` is below B, or `needs_reacquire` is true, or the composer is unknown,
**get the scores first** — run `acquire_composer <composer> --max-files 120`
(this is the /w-research → acquire path). For a style request rather than a
named composer ("baroque", "classical"), pass the style name through; if the
style has no armed members, acquire them first. Never plan against an unarmed
composer and hope.

```bash
.venv/bin/python -c "
from scales.scales import compile_style
result = compile_style(
    piece_id='<piece-id>',
    composers=['<composer1>', '<composer2>'],
    blend_weights={'<composer1>': 0.6, '<composer2>': 0.4},
    era='<era>',
    genre='<genre>'
)
print(result)
"
```

Review the StyleDNA summary: tier, fingerprints, texture distributions, axis ownership (for blends).

## Step 2: Study Reference Scores (read whole pieces, like a human)

Before designing anything, **study complete reference scores** — the way a human
composer absorbs the repertoire before writing. Do not rely only on the
phrase-scoped exemplar bars the brief will later retrieve; read whole pieces and
form your own understanding of how they work.

1. List what's available for your composer/style:
   ```bash
   .venv/bin/python -c "
      from scales.scales import list_reference_scores
   import json; print(json.dumps(list_reference_scores('<composer-or-style>'), indent=1))
   "
   ```
2. Pick **2-4 representative pieces** (vary character/key/texture) and read each
   in full — the shorthand carries every bar with its roman/function and texture:
   ```bash
   .venv/bin/python -c "
      from scales.scales import get_reference_score
   import json; print(json.dumps(get_reference_score('<composer>', '<source>'), indent=1))
   "
   ```
   Read it as music: How is the form articulated? What makes the principal theme
   memorable? How does the harmony move and where does it cadence? How does
   texture/density ebb and flow? Where does it breathe, build, and resolve? What
   makes this piece *work*?
3. Write your **own analysis** for each piece and save it — it feeds every later
   phrase brief (the "WHAT YOU LEARNED FROM THE SCORES" section):
   ```bash
   .venv/bin/python -c "
      from scales.scales import save_reference_study
   save_reference_study('<piece-id>', '<composer>', '<source>',
       analysis='<your prose: form, themes, harmonic language, texture/dynamic arc, what makes it work>')
   "
   ```

Let what you learn here drive the narrative, motif, and form decisions below —
this study is the foundation, not a formality.

**This step is not optional.** `save_reference_study` is what populates the
"WHAT YOU LEARNED FROM THE SCORES" section of every phrase brief. If you skip
it, that section is empty and composition degrades to filling a statistics
brief rather than writing from a real understanding of the repertoire. Save at
least 2 analyses before moving on.

## Step 3: Design & SAVE the Narrative Arc

This is the emotional through-line that drives every note. Don't just think it —
**author it as prose and persist it.** For each section, write `character`: the
dramatic EVENT it enacts, in a human composer's words — not adjectives. Write
what *happens*, e.g. *"the second theme tries to console but can't quite settle —
it keeps slipping back toward the minor"* or *"the storm finally breaks here,
after three failed attempts to rise."* This prose becomes the **CREATIVE INTENT**
the composition brief puts in front of you for every phrase; if you skip it, the
brief falls back to generic curve-adjectives and the music drifts toward
slot-filling.

Then save it (the curves are optional 0-1 shaping cues; `character` is the point):

```bash
.venv/bin/python -c "
from scales.scales import save_narrative
print(save_narrative('<piece-id>',
    sections=[
        {'id': 'm1_a', 'label': 'opening', 'bar_start': 1, 'bar_end': 8,
         'character': '<the dramatic event, in prose>',
         'gesture': '<optional physical shape, e.g. a long exhale>',
         'energy_curve': [0.4, 0.5, 0.6], 'tension_curve': [0.3, 0.4, 0.5],
         'brightness_curve': [0.6, 0.6, 0.5], 'climax_type': None},
        # ... one per section; mark the climactic section climax_type='primary'
    ],
    overall_character='<one line: the whole piece in a breath>'))
"
```

Decisions to make as you author:
- What is the overall character? (heroic, lyrical, stormy, pastoral)
- Where is the primary climax? (typically 2/3 through — mark it `climax_type='primary'`)
- What is the dramatic event of each section — what *changes*?
- What contrasts drive the piece, and how does each section set up the next?
- Bar ranges per section must cover the form you build in Step 5.

## Step 4: Design Motifs

Create MotifObjects — musical characters with identity and transform algebra:

```bash
.venv/bin/python -c "
from scales.scales import resolve_motifs
result = resolve_motifs('<piece-id>', [
    {
        'motif_id': 'theme_a',
        'character': 'Bold, rising, confident',
        'scale_degree_contour': [1, 3, 5, 4, 3, 2, 1],
        'interval_contour': [4, 3, -2, -2, -2, -2],
        'rhythm_cell': ['q', 'q', 'q', 'e', 'e', 'q', 'h'],
        'accent_profile': [1.0, 0.5, 0.8, 0.3, 0.3, 0.5, 0.7],
        'recognition_anchor': {'intervals': [4, 3], 'rhythm': ['q', 'q']},
        'allowed_transforms': ['state', 'sequence', 'fragment', 'invert', 'augment'],
    },
])
print(result)
"
```

Each motif needs: character, contour, rhythm, recognition anchor, allowed transforms.

**This is what makes the piece memorable, and it is not decoration.** The motif
you define here is printed at the top of every phrase brief — its character,
scale-degree contour, interval contour, rhythm cell and recognition anchor — with
the transform that phrase is meant to apply. A piece is memorable because ONE
idea keeps coming back changed, not because every phrase is individually well
made. Define one idea worth hearing nine times, give it a `recognition_anchor`
specific enough that a listener could pick it out (a signature interval pair plus
a rhythm), and let the form deploy it. Skip this step and the composer writes
nine unrelated good phrases.

## Step 5: Build Form Graph

```bash
.venv/bin/python -c "
from scales.scales import build_form_graph
phrases = build_form_graph(
    piece_id='<piece-id>',
    form='<form>',
    key='<key>',
    tempo_bpm=<tempo>,
    meter=(<num>, <denom>),
)
for p in phrases:
    print(f'{p[\"phrase_id\"]}: {p[\"function\"]} -> {p[\"cadence\"]} ({p[\"bars\"]})')
"
```

Review: key scheme, cadence pacing, texture contrast, motif obligations.

## Step 6: Self-Critique

Before finishing, verify:
- [ ] Reference study: 2-4 whole scores read and analyzed AND saved via save_reference_study (required — empty study ⇒ empty briefs)
- [ ] Narrative arc SAVED via save_narrative; every section has authored `character` prose (no section relying on curve-adjectives)
- [ ] Motif journey: clear arc across the piece
- [ ] Texture contrast: sections feel different
- [ ] Cadence pacing: varied (HC, IAC, PAC, DC)
- [ ] Key as protagonist: key scheme tells a story
- [ ] Climax budget: primary climax properly built toward
- [ ] Expectation setup: promises that need fulfillment

## Output

PieceGraph now contains contract, style_dna, form, motif_bank. Ready for `/w-compose`.
