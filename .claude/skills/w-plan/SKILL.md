---
name: w-plan
description: "Unified planning: contract, style, narrative arc, form graph, and motifs — the complete musical architecture, written to the PieceGraph before any composing begins."
argument-hint: "<piece-id>"
---

# w-plan — Unified Composition Planning

Plan the complete musical architecture: PieceContract, StyleDNA, NarrativeArc, FormGraph (PhraseSlots), and MotifBank. All written to PieceGraph before any sketching begins.

## Step 1: Compile Style

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
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

## Step 2: Design Narrative Arc

Think about the emotional journey:
- What is the overall character? (heroic, lyrical, stormy, pastoral)
- Where is the primary climax? (typically 2/3 through)
- What are the energy/tension curves per section?
- What contrasts drive the piece?

## Step 3: Design Motifs

Create MotifObjects — musical characters with identity and transform algebra:

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
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

## Step 4: Build Form Graph

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
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

## Step 5: Self-Critique

Before finishing, verify:
- [ ] Motif journey: clear arc across the piece
- [ ] Texture contrast: sections feel different
- [ ] Cadence pacing: varied (HC, IAC, PAC, DC)
- [ ] Key as protagonist: key scheme tells a story
- [ ] Climax budget: primary climax properly built toward
- [ ] Expectation setup: promises that need fulfillment

## Output

PieceGraph now contains contract, style_dna, form, motif_bank. Ready for `/w-compose`.
