# Holistic Review Checklist

## For Mini-Review (every 10 sections)

Quick checks against continuity.json:

| Check | Source | Flag If |
|-------|--------|---------|
| Intensity arc on track | continuity.json intensity_arc vs narrative-arc.json | Intensity diverges by >0.3 from planned |
| Theme usage | continuity.json themes_introduced | A theme has >20 appearances (overused) or 0 in last 10 sections |
| Harmonic variety | continuity.json harmonic_regions_used | Any key region used >50% of total measures |
| Texture variety | continuity.json orchestration_state.texture_history | Same texture for >5 consecutive sections |
| Unresolved elements | continuity.json unresolved_elements | Elements unresolved for >15 sections |

## For Movement Review

Full analysis of a complete movement:

### Thematic Coherence
- Are themes developed progressively across the movement?
- Does the development section (if sonata form) actually develop the themes?
- Are there enough callbacks to earlier thematic material?
- Is the connecting motif present at key structural points?

### Tonal Journey
- Does the movement visit enough tonal areas for its form?
- Does the sonata exposition properly establish tonic and secondary key?
- Does the recapitulation return themes to the home key?
- Is the final cadence strong and conclusive?

### Intensity Arc
- Does the emotional trajectory match the narrative plan?
- Is the climax properly placed (typically at ~60-70% through the movement)?
- Are there sufficient contrasts (not a flat dynamic line)?
- Does the ending match the planned character?

### Orchestral Balance
- Has every instrument group had meaningful material?
- Are there overly long stretches (>16 measures) of similar texture?
- Is the solo instrument (in a concerto) featured enough?
- Are tutti passages properly scored (not thin)?

### Pacing
- Are section proportions appropriate for the form?
- Is the development section substantial enough (~30-40% of sonata form)?
- Are transitions smooth or are there jarring jumps?
- Is the coda proportional (not too long or abrupt)?

### Structural Integrity
- **Sonata**: Does recap reference exposition? Is development thematically based?
- **Rondo**: Does refrain match original within tolerance?
- **Theme & Variations**: Does each variation clearly derive from the theme?
- **Ternary**: Does A' properly recall A?

## For Full-Piece Review

Cross-movement analysis:

### Cross-Movement Thematic Coherence
- Connecting motif present in opening and closing of each movement
- Any cyclic theme returns (Beethoven 5th style)?
- Thematic transformation shows progression across movements

### Overall Tonal Journey
- Each movement's home key relates logically to the next
- Final movement ends in same key as first (or parallel major if tragedy-to-triumph)
- Middle movements provide tonal contrast

### Emotional Narrative
- The overall emotional arc matches the program/narrative from plan.json
- Each movement contributes to the story
- The ending resolves the narrative satisfactorily

### Variety and Contrast
- Each movement has distinct character (fast-slow-fast, etc.)
- Orchestration varies between movements
- Different textures and techniques across movements

## Scoring

Rate each category 1-10:

| Category | 1-3 (Poor) | 4-6 (Acceptable) | 7-9 (Good) | 10 (Excellent) |
|----------|-----------|-------------------|-------------|-----------------|
| Thematic | Themes missing/wrong | Present but underdeveloped | Well-developed | Masterful development |
| Tonal | Wrong keys/no plan | Functional but predictable | Effective journey | Sophisticated & satisfying |
| Intensity | Flat/wrong | Some contrast | Good arc | Compelling narrative |
| Orchestration | Errors/thin | Functional | Effective colors | Brilliant scoring |
| Structure | Broken form | Follows form | Well-proportioned | Inspired structure |

**Overall score**: Average of categories. Flag for re-composition if any category < 4.
