---
name: w-research
description: "Research unknown composers or styles via web search. Build temporary composer profiles for Wolfgang composition."
argument-hint: "<composer-name or style description>"
---

# w-research — Composer/Style Research

Research unknown composers or styles and build a temporary **text profile**
(harmonic/melodic/textural prose) for composition.

**First, GET THE SCORES — then research.** This skill builds the
*doctrine/profile* layer from web text; it does NOT download or index any real
corpus bars. A profile alone produces a brief with no exemplars, which the gate
blocks (`brief_insufficient`). The bars Claude actually composes from come from
the **acquisition pipeline**, which is the primary step for any unknown composer:

```bash
# from tools/ — music21 local corpus first, then allowlisted web
#   (KernScores **kern, then Mutopia MIDI), validated + armed end to end
.venv/bin/python -m scripts.acquire_composer <composer> --max-files 120
.venv/bin/python -m scripts.acquire_composer --status <composer>   # tier + richness
```

Acquisition writes `reference_index/<composer>/` + `corpus_profile.json` +
`density_stats.json` and lifts the coverage tier. The `--status` report tells
you both how MUCH material (`tier`, `bars`) and how GOOD the records are
(`records_rich`, `harmony_coverage`, `melody_coverage`, `needs_reacquire`) — if
`needs_reacquire` is true, re-run acquisition to regenerate rich records.
**Run acquisition BEFORE composing** for any composer that isn't already armed
and rich. Use w-research to add the prose profile on top of (not instead of) an
armed corpus.

If acquisition reports `no_scores_found` (a rare, modern, or misspelled
composer with nothing public-domain), say so honestly and offer the closest
armed style — never silently substitute another composer.

Read `references/research-template.md` for the profile schema, search
query templates, source-reliability tiers, and the output checklist.

## When to Use

- User requests a composer not in `.claude/context/`
- User requests a style blend with an unknown component
- User references a specific piece that needs analysis

## Process

1. **Web search** for the composer/style (query templates: research-template.md)
2. **Extract** key characteristics: harmonic language, melodic style, preferred forms, texture approach, rhythmic character — written as research artifacts in `workspace/<piece-id>/research/` per the template schema
3. **Build** a temporary ComposerPack from them:

```bash
.venv/bin/python -c "
from scales.context_compiler import ContextCompiler
compiler = ContextCompiler()
result = compiler.compile('<composer>', '<genre>')
print(result)
"
```

4. **Set expectations** honestly — report the support tier:

| Tier | Description | Example |
|------|-------------|---------|
| A | Large corpus + full profile | Mozart, Beethoven, Chopin |
| B | Good corpus in related style | Haydn, Schubert |
| C | Sparse data + profile exists | Brahms, Debussy, Liszt |
| D | Unknown — pure era/genre inference | Any unlisted composer |

## Output

A compiled ComposerPack at `tools/compiled_packs/<composer>/` that the StyleResolver can load.
