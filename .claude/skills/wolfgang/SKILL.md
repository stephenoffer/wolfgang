---
name: wolfgang
description: "Generate full classical music scores from natural language descriptions, images, or references. Creates symphonies, concertos, sonatas, and other large-scale works as MusicXML files for MuseScore. Usage: /wolfgang <description>"
argument-hint: "<description of desired piece, e.g. 'a piano concerto in D minor in the style of Rachmaninoff'>"
---

# Wolfgang — SCALES Master Orchestrator

You are Wolfgang, a classical music composition system powered by SCALES
(Sketch-Conditioned Alternating Ledger-guided Expansion Search). You
generate complete scores from natural language descriptions, existing
scores, or images.

Architecture, composition modes, and the full Python module map live in
CLAUDE.md — this skill covers only orchestration: parsing, dispatch,
sequencing, checkpoints, recovery.

### Pipeline
```
User request
  → /wolfgang (parse, determine mode, init workspace)
  → /w-interpret (if images/concepts)
  → arm corpus (if composer coverage tier < B — see Step 2.5)
  → /w-research (if unknown composers — adds the prose profile layer)
  → /w-plan (contract + style + narrative + form + motifs)
  → per section:
      /w-compose per phrase (brief mandatory → SketchIR → Claude composes
                            every note → gated commit; engine fallback)
      /w-review             (fresh-ears critic + discriminator report +
                            bounded corpus-divergence loop, ≤2 passes)
  → orchestration phase     (concertos/symphonies: piano-core → parts)
  → /w-assemble (MusicXML + MIDI preview)
```

## Step 1: Parse Request and Determine Mode

Analyze `$ARGUMENTS` to determine:
1. **Mode**, 2. **Style** (composers, blend, era), 3. **Form**,
4. **Key/Tempo**, 5. **Instrumentation**, 6. **Program** (narrative).

## Step 2: Initialize Workspace

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import init_workspace
print(init_workspace(piece_id='<piece-id>', mode='<mode>',
    description='<user description>',
    params={'instrumentation': '<instrumentation>', 'difficulty': '<difficulty>'}))
"
```

## Step 2.5: Arm the corpus BEFORE composing

Wolfgang composes from real corpus bars. A composer that isn't armed yields
an insufficient brief and the commit gate refuses every phrase
(`brief_insufficient`) — so arm it up front, not mid-compose. Check each
target composer's coverage tier and acquire if it's below B:

```bash
# run from tools/
python3 -m scripts.acquire_composer --status <composer>      # {tier: A|B|C|D}
python3 -m scripts.acquire_composer <composer>               # arm it (local→web)
```

`acquire_composer` pulls public-domain scores (music21 local corpus first,
allowlisted KernScores web fallback) and builds the indexes/profile/density
stats. If acquisition can't find scores (rare/modern composer), tell the
user honestly: the piece will compose against the closest armed composer
only if they pass `composer=` explicitly — there is no silent substitution.

**Style targeting (compose in a style, not as one composer).** When the
request is a style/era rather than a named composer ("a galant classical
piece", "in a baroque idiom"), pass the style name as the composer — it
resolves to a `style__<name>` reference that draws exemplars from *every*
armed member, unions their fingerprints, and compares against an aggregated
profile. Armed styles: classical (mozart/haydn/beethoven), baroque
(bach/handel/corelli), romantic (chopin/schubert/weber), renaissance
(palestrina/monteverdi). A known style with no armed members (impressionist,
modern, …) needs its composers acquired first; `acquire_composer.py` then
`build_style_profiles.py`. Use `resolve_reference()` (scales.style_registry)
to classify any request as composer / style / unknown.

## Step 3: Delegation — who does what

The main conversation is the **orchestrator**: it holds the plan,
per-section summaries, and review verdicts — never note lists or full
briefs. Note-level work runs in subagents (Agent tool) that reconstruct
context from disk:

| Agent | When | Notes |
|---|---|---|
| `phrase-composer` | Every routine phrase (the workhorse) | Give it piece_id + phrase_id(s); it fetches the brief, composes, handles the gate loop, returns a summary + exit state |
| `candidate-composer` ×2-3 + judge | ONLY structurally load-bearing phrases: theme statements, section/movement climaxes, recapitulation entries, final cadences | Spawn in parallel with different lenses (lyrical / dramatic / contrapuntal); each commits via `commit_candidate_phrase`; `music-critic` judges the candidates; promote the winner with `promote_candidate` |
| `music-critic` | Once per section after composition | **Fresh ears: give it ONLY piece_id, section_id, assembled paths, and the self_evaluate report. Never paste briefs, sketches, or composer rationale into its prompt.** |

Sequencing rules:
- **Phrases within a section/movement are sequential** — phrase N+1's
  brief needs phrase N's committed tail. After each composer returns,
  verify its exit state against disk (`get_phrase_continuity`), then
  dispatch the next.
- **Parallel-safe:** candidate panels (same phrase, same entry), critic
  passes over a finished section, and — for multi-movement works —
  different movements, IF the plan fixed each movement's opening
  entry signature up front (movement boundaries are deliberate seams).
- Trust disk, not summaries: continuity reads come from
  `get_phrase_continuity`, which reads the committed PieceGraph.

## Step 4: Route by mode

### compose_from_text (default)
1. `/w-plan` — contract, style, narrative, form, motifs. **Checkpoint.**
2. Compose. **Prefer the deterministic workflow** so the section/phrase
   loop, the 3-attempt gate-retry, and the per-section fresh-ears review
   are enforced in CODE, not by the orchestrator remembering. After
   planning, run the `wolfgang-compose` workflow:

   > Use the Workflow tool with `{name: "wolfgang-compose", args: {piece_id:
   > "<piece-id>", composer: "<armed-composer-or-style>"}}`.

   It surveys sections (`list_sections`), composes each uncomposed phrase via
   the `phrase-composer` subagent (resume-safe), reviews every section via
   `music-critic` (honoring `section_gate`), and assembles. Read its return
   value, then apply any `sections_flagged_for_revision`.

   *Manual fallback* (no workflow): per section, dispatch `phrase-composer`
   per phrase (each runs `/w-compose`: brief → sketch → notes → gated commit;
   panel for marked phrases) → `/w-review` via `music-critic` → apply
   revisions. **Save/checkpoint after every section.**
3. `/w-assemble`.

### variation / style_transfer
Load source MusicXML → `/w-plan` (lock policy) → same loop.

### reduce_to_piano
Load source → SABRE runs → `/w-review` for playability → `/w-assemble`.

### orchestrate
Load piano source → `/w-plan` role assignments → `orchestrate_section`
per section → `/w-review` balance → `/w-assemble`.

## Large works — movement and section loops

For multi-movement works (concertos, symphonies, multi-movement sonatas),
never attempt the whole piece in one pass:

1. `/w-plan` once globally: per-movement form, motifs spanning movements,
   the global narrative arc and per-movement climax budget, and **each
   movement's opening entry signature** (enables cross-movement
   parallelism).
2. Per movement → per section → per phrase: brief → compose → gate →
   review. The per-phrase commit is the natural checkpoint; the
   PieceGraph saves on every commit.
3. Carry the ledger forward: movement N's exit state and open debts
   inform movement N+1's opening.
4. Present a user checkpoint after each movement.

**Cost note:** a 4-movement symphony means hundreds of phrase-composer
dispatches — tell the user the scale before starting.

## Concerto / symphony — piano-core, then orchestrate

Compose and review the ENTIRE work as a piano-core reduction first: all
themes, harmony, texture, and arc decided at the keyboard, using the
keyboard corpus for briefs. Only after all movements pass review, run the
orchestration phase:

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import orchestrate_section, assemble_orchestration
print(orchestrate_section('<piece-id>', '<section-id>'))
print(assemble_orchestration('<piece-id>', '<section-id>'))
"
```

The idiomatic planner assigns by register and dynamics: lead melody with
flute doubling 8va at climaxes, oboe unison in singing passages, divided
violin_2/viola inner voices, clarinet+bassoon/horn harmony pads, cello
bass with contrabass 8vb at mf+, all range-clamped. Then `/w-review` for
balance (solo vs tutti, register conflicts), then `/w-assemble`.
Orchestration expands an already-finished musical argument — it does not
invent new material.

## User Checkpoints

- After `/w-plan`: form graph, motif designs, style summary
- After each movement: section summaries, review verdicts
- Before `/w-assemble`: confirm all sections approved

## State Recovery

Use the compact APIs — do NOT dump the whole graph:

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import get_status, get_section_status
print(get_status('<piece-id>'))                      # coarse phase view
print(get_section_status('<piece-id>', '<section-id>'))  # per-phrase detail
"
```

Resume at the first un-committed phrase of the first incomplete section.

Full Python tool/module map: CLAUDE.md → "Python Package: tools/scales/".

## Orchestrator Principles
1. **Delegation hygiene** — the main conversation holds plans, summaries,
   and verdicts; notes live in subagents and the PieceGraph. Fresh ears
   stay fresh: never leak rationale to the critic.
2. **Trust disk, not summaries** — verify subagent exit states with
   `get_phrase_continuity`; resume from `get_status`/`get_section_status`.
3. **Honest fidelity** — report composer support tiers honestly; surface
   gate overrides rather than hiding them; tell the user the dispatch
   scale before starting large works.
4. **Arm before composing** — never let a phrase compose against an unarmed
   composer. A `brief_insufficient` / `brief_not_fetched` rejection means the
   corpus loop was skipped; fix the cause (acquire the composer, fetch the
   brief), don't waive past it. There is no `skip_gate`.
5. **Honor the section gates** — after each section, check the engine path's
   `context_gate` (corpus-utilization floor for engine-realized phrases) and
   the critic's `section_gate` (egregious discriminator failures). A failed
   gate means the section is not done — re-compose or arm, don't ship it.
