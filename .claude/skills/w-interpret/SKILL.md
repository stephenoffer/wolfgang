---
name: w-interpret
description: "Translate images, abstract concepts, or existing piece references into musical parameters for Wolfgang composition."
argument-hint: "<image-path or concept description>"
---

# w-interpret — Translate Non-Musical Input

Translate images, abstract concepts, or piece references into musical
parameters that `/w-plan` can use.

Read `references/interpretation-guide.md` for the mapping tables
(image → tonality/form/dynamics, style mixing, derivative-work
handling). For concept mappings, the canonical doctrine lives in
`.claude/context/general/`: `emotional-vocabulary.md` (emotions),
`philosophy-to-music.md` (abstract concepts), `program-music-narrative.md`
(narrative and nature programs), `instrumental-tone-painting.md`
(instrument ↔ sound-world assignments).

## Input Types

### Images
Analyze visual elements — color, texture, movement, mood, contrast,
composition — and map to musical parameters via the guide's tables:
key, tempo, density, register, dynamics, form.

### Abstract Concepts
- "The feeling of a winter morning" → cold brightness, sparse opening, gradual warmth
- "A conversation between two friends" → dialogue texture, contrasting themes

### Piece References
- "Something like Beethoven's Moonlight Sonata" → extract: key, tempo, texture, mood, form
- "Mix of Chopin Ballade 1 and Rachmaninoff Prelude C# minor" → extract + blend
  (see the guide's derivative-work spectrum and style-mixing matrix)

## Output

Write `interpretation.json` to `workspace/<piece-id>/` using the schema
at the end of the guide, then feed its extracted parameters into
`init_workspace()` / `/w-plan`. Surface any listed ambiguities at the
next user checkpoint.
