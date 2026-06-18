---
name: w-compose
description: "Compose a phrase end-to-end: read the corpus-armed brief, write SketchIR (structural plan), then compose every note and commit through the blocking quality gate. Engine realization is the fallback for phrases Claude doesn't author."
argument-hint: "<piece-id> <phrase-id | section-id>"
---

# w-compose — Brief → Sketch → Notes → Gated Commit

You compose each phrase end-to-end: fetch its brief, plan its structure
as SketchIR, then write every final pitch and duration by adapting the
brief's exemplars, committing through the quality gate.

Read `references/note-writing-craft.md` before composing — it is the
single source of truth for the shorthand grammar (§8), the gate loop
(§9), the adapt toolkit (§7), and the canonical tool-call snippets (§10).

## Step 1 — Get the brief (ENFORCED, not just expected)

**Never write anchors or notes you have not earned from the brief**
(craft §1). This is now enforced at commit: fetching the brief writes a
**receipt** on the phrase, and `commit_agent_phrase_*` returns
`brief_not_fetched` if you try to commit a phrase whose brief you never
fetched. There is no gate-bypass flag. Fetch it with
`get_composition_brief(piece_id, phrase_id)` —
or `run_agent_section_briefs(piece_id, section_id)` for a whole section
in one corpus load (snippets: craft §10). The brief is the corpus, the
rules, and the patterns distilled for this exact phrase — read **every**
section, not just the exemplars (full list: craft §1):
- up to 8 real **corpus exemplar bars** + density/ornament targets,
- **COMPOSER FINGERPRINTS** to make the phrase exhibit,
- **STYLE DOCTRINE** (cadence script, ornament intent, breathing, harmonic
  color, melody priors) scoped to this phrase,
- **PHRASE SHAPE / CADENCE PATTERN / TEXTURE TRANSITIONS / LH VOCABULARY**
  — corpus patterns above the single bar,
- composer-specific **corpus targets**, **AVOID (AI tells)**, ledger items,
  and continuity state (previous tail, next needs).

If the brief returns **no exemplars**, the corpus cannot anchor this
phrase: the commit will be blocked with `brief_insufficient`. Stop and
report — do not improvise blind. The right fix is to **arm the composer**
with real scores (`tools/scripts/acquire_composer.py <composer>`) and
re-fetch the brief; only waive `brief_insufficient` if composing without
corpus support is a deliberate, stated choice.

The corpus-alignment gate now **blocks** (not just warns) a surface that
resembles no briefed exemplar (`composed_blind`) — so adapt them in
earnest. If composing away from the corpus is genuinely intended, recommit
with `allow=[{'check':'composed_blind','reason': ...}]` (logged).

The brief supplies idiomatic raw material and statistical reality; you
still own the rhetorical intent, motif placements, harmonic plan, and
where the phrase peaks and breathes.

## Step 2 — Sketch (SketchIR: structure, not final notes)

Plan the phrase as ONE musical thought (4-16 bars), in gestures, not
notes — "answer softly, leave room, cadence toward V". Ask:

1. **What is this phrase FOR?** (rhetorical role, emotional purpose)
2. **Where are the structural pitches?** (entry, peak, cadence arrival)
3. **What harmony drives it?** (tension/release pattern)
4. **What texture family?** (what do the brief's exemplars actually do?)
5. **Where does it breathe?** (rests, silences, phrase breaths)
6. **Which motif appears and how?** (stated, sequenced, fragmented, inverted?)
7. **How does it connect to neighbors?** (entry from previous, exit to next)

SketchIR content — every anchor has a reason:

- **Melody anchors** — key melodic pitches at important moments
- **Bass anchors** — structural bass moments tied to harmony
- **Harmonic rhythm** — chord changes (Roman numerals per bar)
- **Texture intent** — per-bar RH/LH texture types and density targets.
  Real corpus texture changes every 1-2 bars; an 8-bar phrase with one
  unchanging texture plan is usually a planning smell, not a style.
- **Dynamic shape** — energy curve with hairpins
- **Motif placements** — where motifs appear and with what transform
- **Breath points** — planned silences
- **Cadence approach** — how the cadence is approached and arrived at
- **Entry/exit signatures** — boundary states for transition continuity

## Step 3 — Compose every note

1. **Study the exemplars and patterns** — what makes each bar
   non-mechanical? Where does texture shift, where do non-chord tones
   land, how does the LH track the harmony, where does it breathe? Cross
   them against the FINGERPRINTS, DOCTRINE, PHRASE SHAPE arc, and LH
   VOCABULARY — the phrase should be recognizably this composer, with at
   least one or two fingerprints worked in where the music invites them.
2. **Choose an adapt strategy per bar** (craft §7): transpose /
   reharmonize / re-contour / splice / vary density / fresh-in-idiom.
   Adapt — never copy verbatim, never ignore.
3. **Write the bars** in shorthand (grammar: craft §8), with expression
   as part of the notes: slurs, hairpins, ornaments, dynamics.
4. **Density honesty:** match the brief's target, not a comfortable
   minimum. If the brief says ~10 LH events/bar and you wrote 3 quarter
   notes, you wrote a sketch. Under-filling a bar because shorthand is
   easier is not a musical decision.
5. **Commit** via `commit_agent_phrase_direct_bars` — or
   `commit_agent_phrase_layer_ir` for genuinely multi-voice writing
   (snippets: craft §10) — then carry the committed exit state into the
   next phrase.

## Step 4 — The gate loop

Commits run, in order: the **brief receipt** check (`brief_not_fetched` /
`brief_insufficient`), physical validation (strict, never waivable), then a
quality gate with corpus-derived thresholds. Blocking gate checks:
`density_low_rh/lh` (skeletal vs corpus median — a hard generic floor
applies even when the composer has no density stats), `figuration_flat`
(photocopied accompaniment), `composed_blind` (ignored the exemplars), and
`meter`. On `quality_gate_blocked`: respond to the diagnostic, don't
recompose blindly — revise only the flagged bars and recommit. **Max 3
attempts per phrase.** If the gate is wrong for genuine musical reasons,
recommit with `allow=[{'check': ..., 'reason': ...}]` — but waivers now
require a **real reason (≥20 chars)** and **at most one blocking check may
be waived per commit** (waiving the whole set is rejected). Every waiver is
logged. Diagnostics table and fix patterns: craft §9.

## Step 5 — Engine fallback

If you can't satisfy the gate and have no honest override, skip the
commit and let the engine realize that phrase:

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import run_scales_section
print(run_scales_section(piece_id='<piece-id>', section_id='<section-id>',
                         k_sketches=3, n_realizations=4, beam_width=5))
"
```

`run_scales_section` never overwrites `agent_authored` phrases. When
adjudicating engine candidates: does the melody sing, does the bass
support, is the texture alive, is the cadence convincing, is there one
surprise, does it breathe.

## Delegation note

In the orchestrated pipeline this workflow runs inside `phrase-composer`
subagents (see `/wolfgang` → Delegation) so the main conversation holds
plans and summaries, not note lists. The rules above are the same
either way.
