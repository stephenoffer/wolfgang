export const meta = {
  name: 'wolfgang-compose',
  description: 'Deterministically compose a PLANNED Wolfgang piece: survey sections, compose each phrase via the phrase-composer subagent with a code-enforced 3-attempt gate-retry loop, fresh-ears review every section via music-critic, then assemble. Control flow (loops, retry, review-per-section) is in code, not prose — the orchestrator cannot skip a step.',
  whenToUse: 'After /w-plan has built the contract + form + phrase slots for a piece. Pass args:{piece_id, composer}. Resume-safe: already agent-authored phrases are skipped.',
  phases: [
    { title: 'Survey' },
    { title: 'Compose' },
    { title: 'Review' },
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

const COMMIT = {
  type: 'object', additionalProperties: false,
  required: ['phrase_id', 'committed'],
  properties: {
    phrase_id: { type: 'string' },
    committed: { type: 'boolean' },
    blocking: { type: 'string', description: 'gate/brief block reason if not committed' },
    summary: { type: 'string', description: 'one line on what was written' },
  },
}

const REVIEW = {
  type: 'object', additionalProperties: false,
  required: ['section_id', 'verdict'],
  properties: {
    section_id: { type: 'string' },
    verdict: { type: 'string', enum: ['approve', 'revise'] },
    section_gate_passed: { type: 'boolean' },
    notes: { type: 'string' },
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
const survey = await agent(
  `Run exactly this and return ONLY the JSON it prints (no commentary):\n` +
  '```\n' +
  `python3 -c "import sys,json; sys.path.insert(0,'tools'); ` +
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

// ── 2. Compose: sections in order; phrases sequential within a section ────────
// Continuity flows phrase→phrase (and section→section), so composition is
// deliberately sequential. The 3-attempt gate-retry is enforced HERE, in code.
phase('Compose')
const composedSections = []
for (const sec of sections) {
  for (const ph of sec.phrases) {
    if (ph.agent_authored) continue            // resume: already committed
    let committed = false
    for (let attempt = 1; attempt <= 3 && !committed; attempt++) {
      const r = await agent(
        `You are composing ONE phrase of a planned Wolfgang piece.\n` +
        `piece_id='${piece}'  phrase_id='${ph.phrase_id}'  attempt ${attempt}/3` +
        (composer ? `  composer='${composer}'` : '') + `\n\n` +
        `Do, in order (all via: python3 -c "import sys; sys.path.insert(0,'tools'); ...):\n` +
        `1. Fetch the brief: get_composition_brief('${piece}', '${ph.phrase_id}'${composerArg}). ` +
        `This is REQUIRED — the commit is rejected (brief_not_fetched) without it. ` +
        `If it reports no exemplars (brief_insufficient), return committed=false with that as blocking.\n` +
        `2. Compose every note by ADAPTING the brief's real corpus exemplars ` +
        `(never copy verbatim, never ignore — the gate blocks composed_blind).\n` +
        `3. Commit via commit_agent_phrase_direct_bars('${piece}', '${ph.phrase_id}', bars${composerArg}). ` +
        `On quality_gate_blocked, revise ONLY the flagged bars and recommit; ` +
        `this is attempt ${attempt} of 3.\n\n` +
        `Return {phrase_id, committed:true} when the commit returns ok:true, ` +
        `else {phrase_id, committed:false, blocking:'<reason>'}.`,
        { label: `compose:${ph.phrase_id}#${attempt}`, phase: 'Compose',
          agentType: 'phrase-composer', schema: COMMIT })
      committed = !!(r && r.committed)
    }
    if (!committed) {
      log(`⚠ ${ph.phrase_id}: not committed after 3 attempts — engine fallback will realize it`)
    }
  }
  composedSections.push(sec.section_id)
}

// ── 3. Review: fresh ears on EVERY section (cannot be skipped) ────────────────
phase('Review')
const reviews = await parallel(composedSections.map(sid => () =>
  agent(
    `Review section '${sid}' of piece '${piece}' with FRESH EARS.\n` +
    `Generate the discriminator report yourself:\n` +
    `python3 -c "import sys,json; sys.path.insert(0,'tools'); ` +
    `from scales.scales import self_evaluate; ` +
    `print(json.dumps(self_evaluate('${piece}', section_id='${sid}'${composerArg}), indent=1))"\n` +
    `Read the assembled score + the report. Judge singing line, narrative arc, a ` +
    `memorable moment, cross-phrase connection, person-vs-machine, and ` +
    `does-it-sound-like-the-composer. HONOR section_gate: do not approve over an ` +
    `unaddressed section_gate.passed=false.\n` +
    `Return {section_id:'${sid}', verdict:'approve'|'revise', section_gate_passed, notes}.`,
    { label: `review:${sid}`, phase: 'Review', agentType: 'music-critic', schema: REVIEW })))

const revised = reviews.filter(Boolean).filter(r => r.verdict === 'revise')

// ── 4. Assemble ───────────────────────────────────────────────────────────────
phase('Assemble')
const asm = await agent(
  `Assemble piece '${piece}' to MusicXML (the /w-assemble path). Run:\n` +
  '```\n' +
  `python3 -c "import sys; sys.path.insert(0,'tools'); ` +
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
  sections_flagged_for_revision: revised.map(r => r.section_id),
  reviews: reviews.filter(Boolean),
  output: asm,
}
