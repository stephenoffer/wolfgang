---
name: w-review
description: "Review and refine a composed section of a Wolfgang composition. Checks for voice-leading errors, range violations, stylistic consistency, and thematic coherence."
argument-hint: "<piece-id> <section-id> [iteration-number]"
---

# W-Review — Section Quality Reviewer

You are the quality control agent for Wolfgang. You review a single composed section and either fix issues or approve it.

## Input

Read:
1. `workspace/$ARGUMENTS[0]/composed/m<N>_$ARGUMENTS[1].abc` — the section to review
2. `workspace/$ARGUMENTS[0]/themes.json` — to verify theme usage
3. `workspace/$ARGUMENTS[0]/harmony/m<N>_$ARGUMENTS[1].json` — to verify chord adherence
4. `workspace/$ARGUMENTS[0]/orchestration/m<N>_$ARGUMENTS[1].json` — to verify instrumentation
5. `workspace/$ARGUMENTS[0]/rhythm/m<N>_$ARGUMENTS[1].json` — to verify rhythmic plan adherence
6. `workspace/$ARGUMENTS[0]/narrative-arc.json` — to verify emotional target
7. [Review Checklist](./references/review-checklist.md)

Also read the previous section's ABC for boundary checking.

## Review Checklist

### A. Notation Correctness (CRITICAL)
- [ ] Every measure has the correct duration for the time signature
- [ ] All voices declared in header are present in body
- [ ] Barlines are consistent across all voices
- [ ] Key and time signatures are correct
- [ ] No invalid ABC syntax

### B. Voice Leading (HIGH)
- [ ] No parallel 5ths between any voice pair
- [ ] No parallel octaves between any voice pair
- [ ] No parallel unisons between any voice pair
- [ ] Leading tones resolve upward
- [ ] 7ths resolve downward
- [ ] No augmented melodic intervals
- [ ] Voices don't cross unnecessarily

### C. Instrument Ranges (HIGH)
- [ ] All notes within playable range for each instrument
- [ ] No extreme registers used without musical justification
- [ ] Transposing instruments written at correct pitch

### D. Theme Verification (HIGH)
- [ ] All themes listed in usage_plan for this section are present
- [ ] Theme transformations are correct (inversion reverses intervals, etc.)
- [ ] Connecting motif appears if planned for this section
- [ ] Themes are recognizable (interval pattern matches themes.json)

### E. Harmonic Adherence (MEDIUM)
- [ ] Chords match the harmony plan at each beat/measure
- [ ] Modulations occur where planned
- [ ] Cadences at section boundaries match the plan

### F. Rhythmic Plan (MEDIUM)
- [ ] Time signature matches rhythm plan
- [ ] Tempo marking present and correct
- [ ] Characteristic rhythmic patterns are used

### G. Orchestration Plan (MEDIUM)
- [ ] Correct instruments assigned to melody/bass/harmony roles
- [ ] Dynamics markings present
- [ ] Articulation markings present
- [ ] Texture matches plan (homophonic, contrapuntal, etc.)

### H. Boundary Continuity (MEDIUM)
- [ ] Smooth transition from previous section's ending
- [ ] Register, dynamics, and texture connect naturally

### I. Musical Quality (LOW — subjective)
- [ ] Music sounds natural and expressive
- [ ] Accompaniment patterns are varied (not just block chords)
- [ ] Dynamic arc within the section makes sense

## Review Process

1. Read the ABC carefully, voice by voice
2. Check each item in the checklist above
3. For each issue found, note: category, severity (CRITICAL/HIGH/MEDIUM/LOW), specific location (measure, voice), and the fix needed

## Output

If issues found:
- **CRITICAL or HIGH issues**: Edit the ABC file directly to fix them, then write the review log
- **MEDIUM issues**: Fix if straightforward, otherwise note in the review log
- **LOW issues**: Note but don't block approval

Write review results to `workspace/$ARGUMENTS[0]/reviews/m<N>_$ARGUMENTS[1]_review_$ARGUMENTS[2].json`:
```json
{
  "section_id": "<section-id>",
  "iteration": <N>,
  "status": "approved" | "fixed" | "needs_recomposition",
  "issues_found": [
    {
      "category": "voice_leading",
      "severity": "HIGH",
      "location": "measure 12, V1-V2",
      "description": "Parallel 5ths between Violin I and Violin II",
      "fix_applied": "Changed V2 from G to A at beat 3"
    }
  ],
  "issues_remaining": [],
  "quality_notes": "Overall good voice leading, effective use of Theme A"
}
```

If status is "approved": update `state.json` to mark this section as reviewed.

## Iteration Limit

Maximum 3 review iterations per section. After iteration 3, approve with remaining issues logged as warnings. The holistic review will catch systemic problems later.
