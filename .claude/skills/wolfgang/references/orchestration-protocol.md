# Wolfgang Orchestration Protocol

Complete step-by-step pipeline for generating a full classical music score. This protocol ensures the master `/wolfgang` skill can resume from any point by reading `state.json`.

## State Machine

`state.json` tracks:
```json
{
  "piece_id": "<id>",
  "current_phase": "<phase-name>",
  "current_detail": "<specific step within phase>",
  "completed_phases": ["<phase1>", "<phase2>"],
  "completed_sections": ["m1_intro", "m1_expo_pt"],
  "completed_movements": [1],
  "errors": [],
  "user_feedback": []
}
```

## Phase Sequence

### Phase 0: PARSE
- Parse user request into `plan.json`
- State: `"current_phase": "parse"`
- On completion: `"current_phase": "checkpoint_interpretation"`

### Phase 0.5: CHECKPOINT — Interpretation
- Present interpretation to user via AskUserQuestion
- Apply any corrections to `plan.json`
- On completion: `"current_phase": "narrative"`

### Phase 1: NARRATIVE
- Invoke: `/w-narrative <piece-id>`
- Reads: `plan.json`
- Writes: `narrative-arc.json`
- State: `"current_phase": "narrative"`
- On completion: `"current_phase": "checkpoint_narrative"`

### Phase 1.5: CHECKPOINT — Narrative Arc
- Present emotional arc to user
- On completion: `"current_phase": "structure"`

### Phase 2: STRUCTURE
- Invoke: `/w-structure <piece-id>`
- Reads: `plan.json`, `narrative-arc.json`
- Writes: `structure.json`
- State: `"current_phase": "structure"`
- On completion: `"current_phase": "themes"`

### Phase 3: THEMES
- Invoke: `/w-themes <piece-id> create`
- Reads: `plan.json`, `structure.json`, `narrative-arc.json`
- Writes: `themes.json`
- Then: `/w-novelty <piece-id>` to verify originality
- If any theme flagged: `/w-themes <piece-id> regenerate <theme-name>`
- State: `"current_phase": "themes"`
- On completion: `"current_phase": "checkpoint_themes"`

### Phase 3.5: CHECKPOINT — Themes
- Present themes to user (show ABC snippets, describe character)
- On completion: `"current_phase": "planning"`

### Phase 4: PLANNING
For each movement (1 to N):
- `/w-harmony <piece-id> movement-<N>`
- `/w-rhythm <piece-id> movement-<N>`
- `/w-orchestration <piece-id> movement-<N>`
- State: `"current_phase": "planning", "current_detail": "movement-<N>-<skill>"`
- On all movements complete: `"current_phase": "composition"`

Initialize `continuity.json` with empty tracking state.

### Phase 5: COMPOSITION
For each section in `structure.json` order (across all movements):
1. `/w-compose <piece-id> <section-id>`
2. Run: `python3 tools/continuity_tracker.py workspace/<piece-id> <section-id>`
3. `/w-review <piece-id> <section-id> 1`
4. If review requests changes: edit ABC or re-compose, then review again (max 3 iterations)
5. Mark section complete in `state.json.completed_sections`
6. Every 10 completed sections: `/w-holistic <piece-id> mini-review`

State: `"current_phase": "composition", "current_detail": "<section-id>"`

### Phase 6: MOVEMENT REVIEW
After all sections of a movement complete:
- `/w-holistic <piece-id> movement-<N>`
- State: `"current_phase": "movement_review", "current_detail": "movement-<N>"`
- CHECKPOINT: Present movement summary to user
- If user requests changes: re-compose specific sections, then re-review
- Mark movement complete in `state.json.completed_movements`

### Phase 7: CROSS-MOVEMENT REVIEW
After all movements complete:
- `/w-holistic <piece-id> full-review`
- State: `"current_phase": "cross_movement_review"`
- CHECKPOINT: Present full piece summary
- If critical issues: re-compose flagged sections

### Phase 8: ASSEMBLY
- `/w-assemble <piece-id> full`
- State: `"current_phase": "assembly"`
- Produces: `output/<piece-id>.musicxml` and `output/<piece-id>.mxl`
- CHECKPOINT: Deliver final file to user

### Phase 9: COMPLETE
- State: `"current_phase": "complete"`

## Recovery

To resume after context compaction:
1. Read `state.json`
2. Check `current_phase` and `current_detail`
3. Jump to the appropriate phase
4. Read relevant workspace files to reconstruct context
5. Continue from where we left off

All intermediate state is on disk. Nothing critical exists only in conversation memory.
