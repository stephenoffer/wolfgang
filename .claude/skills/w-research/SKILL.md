---
name: w-research
description: "Research unknown composers or styles via web search. Build temporary composer profiles for Wolfgang composition."
argument-hint: "<composer-name or style description>"
---

# w-research — Composer/Style Research

Research unknown composers or styles and build a temporary **text profile**
(harmonic/melodic/textural prose) for composition.

**Important — this skill does NOT acquire reference scores.** It builds the
*doctrine/profile* layer from web text; it does not download or index any
real corpus bars. A profile alone produces a brief with no exemplars, which
the commit gate now blocks (`brief_insufficient`). To actually **arm** a
composer with real corpus material (the bars Claude composes from), use the
acquisition pipeline instead:

```bash
# music21 local corpus first, allowlisted web fallback (KernScores) second
python3 -m scripts.acquire_composer <composer>           # run from tools/
python3 -m scripts.acquire_composer --status <composer>  # just the tier
```

Acquisition writes `reference_index/<composer>/` + `corpus_profile.json` +
`density_stats.json` and lifts the coverage tier. Run it BEFORE composing
for any composer that isn't already armed. Use w-research to add the prose
profile on top of (not instead of) an armed corpus.

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
python3 -c "
import sys; sys.path.insert(0, 'tools')
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
