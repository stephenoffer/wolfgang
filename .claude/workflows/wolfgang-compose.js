export const meta = {
  name: 'wolfgang-compose',
  description: 'Deterministically compose a PLANNED Wolfgang piece: survey sections, compose each phrase via the phrase-composer subagent with a code-enforced 3-attempt gate-retry loop, fresh-ears review every section via music-critic, ACT on the review with one bounded targeted-revision pass plus a re-review, then assemble. Control flow (loops, retry, review, revise) is in code, not prose — the orchestrator cannot skip a step.',
  whenToUse: 'After /w-plan has built the contract + form + phrase slots for a piece. Pass args:{piece_id, composer}. Resume-safe: already agent-authored phrases are skipped.',
  phases: [
    { title: 'Survey' },
    { title: 'Compose' },
    { title: 'Review' },
    { title: 'Revise' },
    { title: 'Assemble' },
  ],
}

// ── inputs ───────────────────────────────────────────────────────────────────
const piece = args && args.piece_id
if (!piece) {
  throw new Error('args.piece_id is required — plan the piece first with /w-plan')
}
const composer = (args && args.composer) || ''
const composerArg = composer ? `, composer='${composer}'` : ''

// ── schemas (force structured, deterministic agent returns) ───────────────────
const SURVEY = {
  type: 'object', additionalProperties: false,
  required: ['sections'],
  properties: {
    sections: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['section_id', 'phrases'],
        properties: {
          section_id: { type: 'string' },
          phrases: {
            type: 'array',
            items: {
              type: 'object', additionalProperties: false,
              required: ['phrase_id', 'agent_authored'],
              properties: {
                phrase_id: { type: 'string' },
                agent_authored: { type: 'boolean' },
              },
            },
          },
        },
      },
    },
  },
}

const SECTION_COMMIT = {
  type: 'object', additionalProperties: false,
  required: ['section_id', 'phrases'],
  properties: {
    section_id: { type: 'string' },
    phrases: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['phrase_id', 'committed'],
        properties: {
          phrase_id: { type: 'string' },
          committed: { type: 'boolean' },
          blocking: { type: 'string', description: 'gate/brief block reason if not committed' },
        },
      },
    },
    summary: { type: 'string', description: 'one line on the section as a whole musical thought' },
  },
}

const REVIEW = {
  type: 'object', additionalProperties: false,
  required: ['section_id', 'verdict'],
  properties: {
    section_id: { type: 'string' },
    verdict: { type: 'string', enum: ['approve', 'revise'] },
    section_gate_passed: { type: 'boolean' },
    // What specifically to fix, so a revision pass has a target rather than
    // "make it better". Without these the critic's verdict is unactionable.
    fix_bars: {
      type: 'array',
      description: 'bar numbers that need rewriting, most important first',
      items: { type: 'integer' },
    },
    notes: { type: 'string' },
  },
}

const REVISION = {
  type: 'object', additionalProperties: false,
  required: ['section_id', 'revised_bars'],
  properties: {
    section_id: { type: 'string' },
    revised_bars: { type: 'integer' },
    notes: { type: 'string' },
  },
}

const READINESS = {
  type: 'object', additionalProperties: false,
  required: ['ready'],
  properties: {
    ready: { type: 'boolean' },
    missing: { type: 'array', items: { type: 'string' } },
    thin: { type: 'array', items: { type: 'string' } },
    phrases: { type: 'integer' },
    motifs: { type: 'integer' },
    narrative_sections: { type: 'integer' },
    reference_studies: { type: 'integer' },
  },
}

const ASSEMBLE = {
  type: 'object', additionalProperties: false,
  required: ['ok'],
  properties: {
    ok: { type: 'boolean' },
    output_path: { type: 'string' },
    error: { type: 'string' },
  },
}

// ── 1. Survey: the deterministic work-list, read from the committed graph ─────
phase('Survey')

// Preflight the PLAN before spending dozens of composers on it. Every part of a
// plan is optional at the type level, so a piece can reach the phrase composers
// with an empty narrative, no motifs and no reference study — and the briefs
// simply omit those sections, so nothing anywhere says so. Measured over the
// twelve pieces in workspace/: five had a populated motif bank and not one had
// an elected principal theme or a single placement; one of twelve had a saved
// reference study. This runs in code so it cannot be skipped.
const readiness = await agent(
  `Run exactly this and return ONLY the JSON it prints (no commentary):\n` +
  '```\n' +
  `.venv/bin/python -c "import json; ` +
  `from scales.scales import plan_readiness; ` +
  `print(json.dumps(plan_readiness('${piece}')))"\n` +
  '```',
  { label: 'plan-readiness', phase: 'Survey', schema: READINESS })

if (readiness && !readiness.ready) {
  const gaps = (readiness.missing || []).join('; ')
  if (args && args.allow_incomplete_plan) {
    log(`WARNING: composing against an incomplete plan — ${gaps}`)
  } else {
    throw new Error(
      `plan is incomplete for '${piece}' — ${gaps}. ` +
      `Finish /w-plan (save_narrative, resolve_motifs, save_reference_study), or ` +
      `pass args.allow_incomplete_plan:true to compose anyway and accept that ` +
      `every brief will be missing those sections.`)
  }
}
for (const t of (readiness && readiness.thin) || []) log(`plan is thin: ${t}`)

const survey = await agent(
  `Run exactly this and return ONLY the JSON it prints (no commentary):\n` +
  '```\n' +
  `.venv/bin/python -c "import json; ` +
  `from scales.scales import list_sections; ` +
  `print(json.dumps(list_sections('${piece}')))"\n` +
  '```\n' +
  `If the JSON has an "error" key, return {"sections": []}. Otherwise map each ` +
  `section to {section_id, phrases:[{phrase_id, agent_authored}]}.`,
  { label: 'survey', phase: 'Survey', schema: SURVEY })

const sections = (survey && survey.sections) || []
if (!sections.length) {
  throw new Error(`no sections found for '${piece}' — run /w-plan first`)
}
const todo = sections.reduce((n, s) => n + s.phrases.filter(p => !p.agent_authored).length, 0)
log(`${piece}: ${sections.length} sections, ${todo} phrase(s) to compose (resume-safe)`)

// ── 2. Compose: each SECTION as ONE continuous musical thought ────────────────
// A section is one act of imagination — a line spanning its phrases, one shaped
// climax — not phrases stitched together. So ONE composer per section reads ALL
// its phrase briefs together (run_agent_section_briefs — one corpus load),
// composes the whole arc, and commits each phrase in order. Sections run in
// order so continuity flows section→section. Commit granularity stays per-phrase
// (gate/ledger/resume are per-phrase); only WHO composes together changes. Up to
// 2 section-level passes; the composer fixes gate-flagged bars per phrase.
phase('Compose')
const composedSections = []
for (const sec of sections) {
  let remaining = sec.phrases.filter(p => !p.agent_authored).map(p => p.phrase_id)
  composedSections.push(sec.section_id)
  if (!remaining.length) continue              // resume: already committed
  for (let pass = 1; pass <= 2 && remaining.length; pass++) {
    const r = await agent(
      `Compose section '${sec.section_id}' of a planned Wolfgang piece as ONE continuous musical thought.\n` +
      `piece_id='${piece}'` + (composer ? `  composer='${composer}'` : '') + `  pass ${pass}/2\n\n` +
      `Do, in order (all via: .venv/bin/python -c "...):\n` +
      `1. Fetch ALL the section's phrase briefs in ONE call (REQUIRED — commits are rejected with ` +
      `brief_not_fetched otherwise): run_agent_section_briefs('${piece}', '${sec.section_id}'${composerArg}). ` +
      `If a brief reports no exemplars (brief_insufficient), report that phrase as committed=false.\n` +
      `2. Conceive the WHOLE section before writing: one melodic line spanning these phrases (not ` +
      `${remaining.length} unrelated tunes), a single shaped peak where the CREATIVE INTENT wants it, ` +
      `accompaniment that evolves. INVENT freely or ADAPT the corpus exemplars (never copy verbatim; ` +
      `composed_blind is advisory, not a block).\n` +
      `3. Commit each phrase IN ORDER so they connect, via ` +
      `commit_agent_phrase_direct_bars('${piece}', '<phrase_id>', bars${composerArg}). Only physical ` +
      `violations block; on quality_gate_blocked (meter/range) fix the flagged bars of THAT phrase and ` +
      `recommit. Compose these phrases this pass: ${remaining.join(', ')}.\n\n` +
      `Return {section_id:'${sec.section_id}', phrases:[{phrase_id, committed, blocking}], summary}.`,
      { label: `compose:${sec.section_id}#${pass}`, phase: 'Compose',
        agentType: 'phrase-composer', schema: SECTION_COMMIT })
    const done = new Set((r && r.phrases || []).filter(p => p.committed).map(p => p.phrase_id))
    remaining = remaining.filter(pid => !done.has(pid))
  }
  if (remaining.length) {
    log(`⚠ ${sec.section_id}: ${remaining.join(', ')} not committed — engine fallback will realize them`)
  }
}

// ── 3. Review: fresh ears on EVERY section (cannot be skipped) ────────────────
phase('Review')
const reviews = await parallel(composedSections.map(sid => () =>
  agent(
    `Review section '${sid}' of piece '${piece}' with FRESH EARS.\n` +
    `Generate the discriminator report yourself:\n` +
    `.venv/bin/python -c "import json; ` +
    `from scales.scales import self_evaluate; ` +
    `print(json.dumps(self_evaluate('${piece}', section_id='${sid}'${composerArg}), indent=1))"\n` +
    `Read the assembled score + the report. Judge BY EAR: singing line, narrative arc, a ` +
    `memorable moment, cross-phrase connection, person-vs-machine, and ` +
    `does-it-sound-like-the-composer. corpus_divergence/section_gate are advisory ` +
    `diagnostics (no artistic hard-failures) — your ear decides, never chase a z-score.\n` +
    `Return {section_id:'${sid}', verdict:'approve'|'revise', section_gate_passed, ` +
    `fix_bars:[<bar numbers needing work, most important first>], notes}.`,
    { label: `review:${sid}`, phase: 'Review', agentType: 'music-critic', schema: REVIEW })))

// ── 4. Revise: ACT on the verdicts ────────────────────────────────────────────
// This step did not exist. The workflow collected the critic's verdicts into a
// variable, reported them in the return value, and assembled anyway — so the
// component the architecture calls "the sole driver of revision" drove nothing
// on the default path, and every measurement feeding it was decoration. One
// bounded pass: revise the bars the critic named, then re-review those sections
// only. Bounded because an unbounded loop is how the earlier actor-critic
// attempts oscillated.
phase('Revise')
const flagged = reviews.filter(Boolean).filter(r => r.verdict === 'revise')
if (flagged.length) {
  log(`${flagged.length} section(s) flagged for revision: ${flagged.map(r => r.section_id).join(', ')}`)
}
const revisions = await parallel(flagged.map(r => () =>
  agent(
    `Revise section '${r.section_id}' of piece '${piece}'. A fresh-ears critic ` +
    `heard it and asked for changes.

` +
    `WHAT THE CRITIC SAID:
${r.notes || '(no notes)'}
` +
    `BARS TO FIX: ${(r.fix_bars && r.fix_bars.length) ? r.fix_bars.join(', ') : '(critic named none — use its notes)'}

` +
    `Fix ONLY what the critic named. Re-fetch the brief for each affected phrase, ` +
    `rewrite those bars, and recommit the phrase with commit_agent_phrase_direct_bars ` +
    `(the whole phrase, with your revised bars in place). Do not re-roll phrases the ` +
    `critic did not mention — a targeted revision that leaves the rest alone is the ` +
    `point. If you conclude the critic is wrong about a bar, leave it and say why.
` +
    `Return {section_id:'${r.section_id}', revised_bars:<count>, notes:'<what you changed>'}.`,
    { label: `revise:${r.section_id}`, phase: 'Revise', agentType: 'phrase-composer', schema: REVISION })))

const rerevised = await parallel(
  revisions.filter(Boolean).filter(v => v.revised_bars > 0).map(v => () =>
    agent(
      `Re-review section '${v.section_id}' of piece '${piece}' with FRESH EARS after a ` +
      `revision pass. Regenerate the discriminator report:
` +
      `.venv/bin/python -c "import json; ` +
      `from scales.scales import self_evaluate; ` +
      `print(json.dumps(self_evaluate('${piece}', section_id='${v.section_id}'${composerArg}), indent=1))"
` +
      `Judge the section as it now stands. Did the revision help, and does anything ` +
      `still need work?
` +
      `Return {section_id:'${v.section_id}', verdict:'approve'|'revise', ` +
      `section_gate_passed, fix_bars:[], notes}.`,
      { label: `re-review:${v.section_id}`, phase: 'Revise', agentType: 'music-critic', schema: REVIEW })))

// Final verdict per section: the re-review where there was one, else the first.
const finalReviews = reviews.filter(Boolean).map(r => {
  const again = rerevised.filter(Boolean).find(x => x && x.section_id === r.section_id)
  return again || r
})
const stillFlagged = finalReviews.filter(r => r.verdict === 'revise')

// ── 5. Assemble ───────────────────────────────────────────────────────────────
phase('Assemble')
const asm = await agent(
  `Assemble piece '${piece}' to MusicXML (the /w-assemble path). Run:\n` +
  '```\n' +
  `.venv/bin/python -c "` +
  `from scales.piece_graph import PieceGraph; from scales.assembler import assemble; ` +
  `g=PieceGraph.load('workspace/${piece}/piece_graph.json'); ` +
  `print(assemble(g, scope='full'))"\n` +
  '```\n' +
  `The printed path is the MusicXML output. Return {ok:true, output_path:'<path>'} ` +
  `on success, else {ok:false, error:'<message>'}.`,
  { label: 'assemble', phase: 'Assemble', schema: ASSEMBLE })

return {
  piece,
  sections: sections.length,
  phrases_composed: todo,
  sections_revised: revisions.filter(Boolean).filter(v => v.revised_bars > 0).map(v => v.section_id),
  sections_still_flagged: stillFlagged.map(r => r.section_id),
  reviews: finalReviews,
  output: asm,
}
