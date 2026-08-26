export const meta = {
  name: 'imagine-converge',
  description: 'Compose a planned Wolfgang piece as an actor-critic loop: CONCEIVE a memorable theme via a candidate panel (judge picks, capture it as real material to develop), then per section REALIZE (the agent composes every note from full context — feeling/theme/chord-frame — free to invent or adapt), RENDER, CRITIQUE with the musical_ear (clashes/buried-melody/monotony/breathing) + fresh-ears music-critic, and REVISE flagged bars in a bounded loop until it CONVERGES (no audible errors, gate passes, critic approves) or stops on no-improvement. Convergence/keep-best logic is in code. The agent composes; statistics only inform and evaluate.',
  whenToUse: 'After /w-plan. Pass args:{piece_id, composer, max_passes?}. Resume-safe (agent-authored phrases are skipped).',
  phases: [
    { title: 'Survey' },
    { title: 'Conceive' },
    { title: 'Compose' },
    { title: 'Converge' },
    { title: 'Assemble' },
  ],
}

const _args = typeof args === 'string' ? JSON.parse(args || '{}') : (args || {})
const piece = _args.piece_id
if (!piece) throw new Error('args.piece_id is required — plan the piece first with /w-plan')
const composer = _args.composer || ''
const cArg = composer ? `, composer='${composer}'` : ''
const MAX_PASSES = _args.max_passes || 3
const PY = `.venv/bin/python -c "`

// ── schemas ───────────────────────────────────────────────────────────────────
const SURVEY = {
  type: 'object', additionalProperties: false, required: ['sections'],
  properties: { sections: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['section_id', 'phrases'],
    properties: { section_id: { type: 'string' }, phrases: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['phrase_id', 'agent_authored'],
      properties: { phrase_id: { type: 'string' }, agent_authored: { type: 'boolean' } } } } } } } },
}
const CAND = {
  type: 'object', additionalProperties: false, required: ['lens', 'committed'],
  properties: { lens: { type: 'string' }, committed: { type: 'boolean' },
    blocking: { type: 'string' }, pitch: { type: 'string' } },
}
const JUDGE = {
  type: 'object', additionalProperties: false, required: ['winner'],
  properties: { winner: { type: 'string', description: 'winning lens' },
    captured: { type: 'boolean' }, reasoning: { type: 'string' } },
}
const COMMIT = {
  type: 'object', additionalProperties: false, required: ['phrase_id', 'committed'],
  properties: { phrase_id: { type: 'string' }, committed: { type: 'boolean' },
    blocking: { type: 'string' }, summary: { type: 'string' } },
}
const SECTION_COMMIT = {
  type: 'object', additionalProperties: false, required: ['section_id', 'phrases'],
  properties: {
    section_id: { type: 'string' },
    phrases: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['phrase_id', 'committed'],
      properties: { phrase_id: { type: 'string' }, committed: { type: 'boolean' },
        blocking: { type: 'string' } } } },
    summary: { type: 'string', description: 'one line on the section as a whole musical thought' },
  },
}
const CRITIQUE = {
  type: 'object', additionalProperties: false, required: ['section_id', 'verdict', 'error_count'],
  properties: {
    section_id: { type: 'string' },
    verdict: { type: 'string', enum: ['approve', 'revise'] },
    quality: { type: 'number', description: '0-5: sings? memorable? develops? idiomatic? breathes?' },
    error_count: { type: 'integer', description: 'musical_ear error-severity findings (clash/buried)' },
    section_gate_passed: { type: 'boolean' },
    revised_bars: { type: 'integer', description: 'how many flagged bars this pass rewrote (0 if none)' },
    notes: { type: 'string' },
  },
}
const ASSEMBLE = {
  type: 'object', additionalProperties: false, required: ['ok'],
  properties: { ok: { type: 'boolean' }, output_path: { type: 'string' }, error: { type: 'string' } },
}

// ── 1. Survey ─────────────────────────────────────────────────────────────────
phase('Survey')
const survey = await agent(
  `Run this and return ONLY the JSON it prints:\n${PY}` +
  `from scales.scales import list_sections; import json; print(json.dumps(list_sections('${piece}')))"\n` +
  `Map each section to {section_id, phrases:[{phrase_id, agent_authored}]}; on error return {"sections":[]}.`,
  { label: 'survey', phase: 'Survey', schema: SURVEY })
const sections = (survey && survey.sections) || []
if (!sections.length) throw new Error(`no sections for '${piece}' — run /w-plan first`)
const themePhrase = sections[0].phrases[0].phrase_id
log(`${piece}: ${sections.length} sections; theme phrase = ${themePhrase}`)

// ── 2. Conceive the theme (panel → judge → capture as real material) ──────────
// A memorable theme is invented as a standalone artifact, then DEVELOPED across
// the piece — the antidote to "boring". Skip if the theme phrase already exists.
phase('Conceive')
if (!sections[0].phrases[0].agent_authored) {
  const lenses = ['lyrical', 'dramatic', 'contrapuntal']
  await parallel(lenses.map(lens => () => agent(
    `Compose a MEMORABLE THEME for phrase '${themePhrase}' of '${piece}' through the ${lens} lens.\n` +
    `Fetch the brief first: ${PY}from scales.scales import get_composition_brief; ` +
    `print(get_composition_brief('${piece}','${themePhrase}'${cArg}))" — read the CREATIVE INTENT, ` +
    `sing a tune that has identity and a hook, voice it against the CHORD FRAME, then commit:\n` +
    `commit_candidate_phrase('${piece}','${themePhrase}','${lens}', bars=[...]). ` +
    `Return {lens:'${lens}', committed:true|false, blocking, pitch}.`,
    { label: `theme:${lens}`, phase: 'Conceive', agentType: 'candidate-composer', schema: CAND })))

  const judged = await agent(
    `Judge the theme candidates for phrase '${themePhrase}' of '${piece}'. List them:\n${PY}` +
    `from scales.scales import list_phrase_candidates; import json; ` +
    `print(json.dumps(list_phrase_candidates('${piece}','${themePhrase}')))"\n` +
    `Open each candidate's preview, pick the most MEMORABLE + DEVELOPABLE (hummable, distinct, ` +
    `room to grow). Promote it AND capture it as the piece's theme surface:\n${PY}` +
    `from scales.scales import promote_candidate; from scales.piece_graph import PieceGraph; ` +
    `from scales.theme_planner import capture_theme_surface; ` +
    `promote_candidate('${piece}','${themePhrase}','<winner_lens>'); ` +
    `g=PieceGraph.load('workspace/${piece}/piece_graph.json'); ` +
    `capture_theme_surface(g,'${themePhrase}'); g.save('workspace/${piece}/piece_graph.json')"\n` +
    `Return {winner:'<lens>', captured:true, reasoning}.`,
    { label: 'theme:judge', phase: 'Conceive', agentType: 'music-critic', schema: JUDGE })
  log(`theme: '${judged && judged.winner}' chosen & captured for development`)
}

// ── 3. Compose each SECTION as ONE continuous musical thought ─────────────────
// A human composes a section as a single act of imagination — a line that
// spans its phrases, one shaped climax — not four phrases stitched together.
// So we dispatch ONE composer per section: it reads ALL the section's phrase
// briefs together (run_agent_section_briefs — one corpus load), composes the
// whole arc, then commits each phrase in order. Commit granularity stays
// per-phrase (gate/ledger/resume are per-phrase); only WHO composes together
// changes. Up to 2 section-level passes; the composer fixes gate-flagged bars
// per phrase internally.
phase('Compose')
let todo = 0
for (const sec of sections) {
  let remaining = sec.phrases
    .filter(ph => !ph.agent_authored && ph.phrase_id !== themePhrase)
    .map(ph => ph.phrase_id)
  if (!remaining.length) continue
  todo += remaining.length
  for (let pass = 1; pass <= 2 && remaining.length; pass++) {
    const r = await agent(
      `Compose section '${sec.section_id}' of '${piece}' as ONE continuous musical thought` +
      `${composer ? `, composer='${composer}'` : ''} (pass ${pass}/2).\n` +
      `1. Read ALL the section's phrase briefs together (ONE call):\n${PY}` +
      `from scales.scales import run_agent_section_briefs; ` +
      `print(run_agent_section_briefs('${piece}','${sec.section_id}'${cArg}))"\n` +
      `Study them as a set: the shared CREATIVE INTENT (the section's dramatic event), the ` +
      `PRINCIPAL THEME to develop, each phrase's CHORD FRAME and the continuity tail between them.\n` +
      `2. Conceive the WHOLE section before writing: one melodic line that spans these phrases (not ` +
      `${remaining.length} unrelated tunes), a single shaped registral/dynamic peak placed where the ` +
      `intent wants it, and accompaniment that evolves across the section. INVENT or ADAPT the ` +
      `references — never copy verbatim.\n` +
      `3. Commit each phrase IN ORDER so they connect seamlessly, via ` +
      `commit_agent_phrase_direct_bars('${piece}','<phrase_id>', bars${cArg}). Only physical ` +
      `violations block; on quality_gate_blocked (meter/range) fix the flagged bars of THAT phrase ` +
      `and recommit. Compose these phrases this pass: ${remaining.join(', ')}.\n` +
      `Return {section_id:'${sec.section_id}', phrases:[{phrase_id, committed, blocking}], summary}.`,
      { label: `compose:${sec.section_id}#${pass}`, phase: 'Compose',
        agentType: 'phrase-composer', schema: SECTION_COMMIT })
    const done = new Set((r && r.phrases || []).filter(p => p.committed).map(p => p.phrase_id))
    remaining = remaining.filter(pid => !done.has(pid))
  }
  if (remaining.length) log(`⚠ ${sec.section_id}: ${remaining.join(', ')} not committed — engine fallback realizes them`)
}

// ── 4. Converge: per section, critique (ear + fresh critic) → revise flagged ──
// bars, bounded loop. Stop when converged OR error_count stops improving (the
// keep-best / no-regression discipline; control flow lives here, in code).
phase('Converge')
const results = []
for (const sec of sections) {
  const sid = sec.section_id
  let prevErrors = Infinity, stalls = 0, last = null
  for (let p = 1; p <= MAX_PASSES; p++) {
    const c = await agent(
      `FRESH-EARS critique-and-improve of section '${sid}' of '${piece}', pass ${p}/${MAX_PASSES}.\n` +
      `Generate the report (it RE-ASSEMBLES fresh and includes the musical_ear findings — TRUST it; ` +
      `do NOT read cache/*.musicxml directly, those can be stale):\n${PY}` +
      `from scales.scales import self_evaluate; import json; ` +
      `print(json.dumps(self_evaluate('${piece}', section_id='${sid}'${cArg}), indent=1))"\n` +
      `"ear".findings are pre-localized AUDIBLE defects (the real revision targets); "section_gate" carries ` +
      `no artistic hard-failures (advisory only); "corpus_divergence" z-scores are an advisory DIAGNOSTIC — ` +
      `read them, never chase them back into band. Rate quality 0-5 by EAR: does the melody SING (a real ` +
      `cell/hook, a shaped peak)? is there a memorable moment? does the theme DEVELOP? is it idiomatic? does it BREATHE?\n\n` +
      `IF the section does not yet approve (gate fails, ear errors, or it just doesn't sing): IMPROVE the ` +
      `weakest phrase(s) now — judge by EAR, not by the quality number. ` +
      `HOW TO EDIT: re-fetch the brief, then call commit_agent_phrase_direct_bars with the full phrase ` +
      `bar-list. For a LOCAL defect (a clash, a buried note), change just those bars and leave the rest as ` +
      `they are. For a STRUCTURAL weakness (the line doesn't sing, the climax is flat, phrases don't ` +
      `connect), RE-HEAR and recompose the whole weak passage — a contiguous run of bars, even the whole ` +
      `phrase — don't patch one bar and hope. A musician rewrites the passage, not the symptom. ` +
      `Make concrete musical fixes: give the melody a recognizable ` +
      `opening cell + at least one shaped registral peak (use leaps/wider range, not wandering eighths), ` +
      `build ONE multidimensional climax (register+texture+dynamics) then release, add breathing (a rest or ` +
      `long note) at phrase ends, voice against the CHORD FRAME to kill clashes, keep the melody clearly on ` +
      `top, and steady any lurching accompaniment. Re-run self_evaluate to confirm it improved. ` +
      `Report how many bars you rewrote (>0 if you found problems).\n` +
      `Return {section_id:'${sid}', verdict:'approve'|'revise', quality, error_count, section_gate_passed, revised_bars, notes}.`,
      { label: `converge:${sid}#${p}`, phase: 'Converge', agentType: 'music-critic', schema: CRITIQUE })
    last = c || last
    const errs = (c && c.error_count) != null ? c.error_count : prevErrors
    // Converge on the critic's EAR (approve) + no audible errors + gate passes.
    // The 0-5 quality scalar is reported as a diagnostic only — gating on it
    // re-introduced a metric target through the back door (the agent's own
    // self-rating). The fresh-ears 'approve' already encodes the ear judgment.
    const converged = c && c.verdict === 'approve' && errs === 0 && c.section_gate_passed
    if (converged) { log(`✓ ${sid} converged (pass ${p}; quality ${c.quality} — diagnostic only)`); break }
    // no-improvement / no-edit guard: stop churning if errors don't fall or nothing was rewritten
    if (errs >= prevErrors || !(c && c.revised_bars)) stalls++; else stalls = 0
    prevErrors = Math.min(prevErrors, errs)
    if (stalls >= 2) { log(`■ ${sid} stopped (no improvement) after pass ${p}; residual errors=${errs}`); break }
  }
  results.push({ section_id: sid, final: last })
}

// ── 5. Assemble ───────────────────────────────────────────────────────────────
phase('Assemble')
const asm = await agent(
  `Assemble '${piece}' to MusicXML and render the MIDI preview:\n${PY}` +
  `from scales.piece_graph import PieceGraph; from scales.assembler import assemble; ` +
  `from scales.midi_renderer import render_midi; ` +
  `g=PieceGraph.load('workspace/${piece}/piece_graph.json'); ` +
  `x=assemble(g, scope='full'); m=render_midi(g); print(x); print(m)"\n` +
  `Return {ok:true, output_path:'<musicxml path>'} or {ok:false, error}.`,
  { label: 'assemble', phase: 'Assemble', schema: ASSEMBLE })

const unconverged = results.filter(r => r.final && (r.final.error_count > 0 || r.final.verdict === 'revise'))
return {
  piece,
  sections: sections.length,
  phrases_composed: todo,
  theme_phrase: themePhrase,
  sections_not_fully_converged: unconverged.map(r => r.section_id),
  per_section: results.map(r => r.final).filter(Boolean),
  output: asm,
}
