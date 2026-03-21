# Film Score Forms Reference

## Cue Structure

| Element | Description |
|---------|-------------|
| Cue | A single piece of music for a specific scene |
| Cue number | Identified by reel/scene (e.g., 3m2 = Reel 3, cue 2) |
| In-point | Exact frame where music begins |
| Out-point | Exact frame where music ends |
| Duration | Determined by scene length, not musical logic |
| Tempo | Often locked to visual timing needs |
| Pre-lap | Music begins before scene change |
| Post-lap | Music continues after scene change |

### Cue Length Guidelines

| Scene Type | Typical Cue Duration |
|-----------|---------------------|
| Transition/sting | 5-15 seconds |
| Short dialogue scene | 30-90 seconds |
| Action sequence | 2-5 minutes |
| Emotional set piece | 3-8 minutes |
| Main title | 1-3 minutes |
| End credits | 3-6 minutes |
| Extended sequence (montage) | 3-10 minutes |

## Underscore vs. Source Music

| Type | Definition | Examples |
|------|-----------|----------|
| Underscore | Non-diegetic — characters can't hear it | Orchestral score, tension music |
| Source music | Diegetic — exists in the story world | Radio, band at party, jukebox |
| Source-to-score | Starts diegetic, transitions to non-diegetic | Song on radio becomes orchestral |
| Score-to-source | Non-diegetic fades into diegetic | Score resolves into character's humming |

## Leitmotif System

### Building a Leitmotif System

| Component | Rule | Example (Star Wars) |
|-----------|------|---------------------|
| Hero theme | Major, ascending, noble intervals | Luke's Theme (Bb major) |
| Villain theme | Minor, chromatic, angular | Imperial March (G minor) |
| Love theme | Lyrical, legato, warm | Han & Leia (D major) |
| Place theme | Modal, atmospheric | Tatooine (pentatonic) |
| Object theme | Short, distinctive motif | Force Theme (modal) |
| Conflict theme | Dissonant, rhythmic | Battle music |
| Mystery theme | Chromatic, unresolved | Yoda's Theme (uncertain) |

### Leitmotif Transformation Techniques

| Transformation | Method | Dramatic Effect |
|---------------|--------|-----------------|
| Reharmonization | Same melody, different chords | Changed emotional context |
| Mode change | Major to minor or reverse | Hope to despair (or reverse) |
| Tempo change | Fast to slow or reverse | Action to reflection |
| Orchestration change | Solo to tutti or reverse | Intimate to epic |
| Fragmentation | Only part of theme used | Memory, foreshadowing |
| Augmentation | Notes stretched longer | Noble, grand statement |
| Diminution | Notes compressed shorter | Urgency, panic |
| Inversion | Melody flipped | Corruption, reversal |
| Combination | Two themes played together | Characters meeting |
| Quotation | Brief reference within other music | Subtle reminder |

```abc
X:1
T:Leitmotif Transformation Example
M:4/4
L:1/8
K:C
"^Original (heroic)"C2 E2 G2 c2 | B2 A2 G4 |
"^Minor (tragic)"C2 _E2 G2 c2 | _B2 _A2 G4 |
"^Fragmented (memory)"C2 E2 z4 | z8 |
"^Augmented (noble)"C4 E4 | G4 c4 |
```

## Thematic Transformation Across Cues

### Film-Wide Thematic Arc

| Act | Theme Treatment | Orchestration | Dynamic |
|-----|----------------|---------------|---------|
| Act I intro | Theme hinted, fragmented | Solo instrument | p |
| Act I full | Theme stated completely | Small ensemble | mf |
| Act II development | Theme varied, transformed | Moderate orchestra | varies |
| Act II low point | Theme in minor, broken | Solo over sparse chords | pp |
| Act III return | Theme triumphant, full | Full orchestra | f-ff |
| Act III climax | Theme at maximum power | Full orchestra + choir | fff |
| Resolution | Theme gentle, complete | Reduced, warm | p-mp |

## Hit Points and Sync

| Sync Type | Technique | Example |
|-----------|-----------|---------|
| Hard hit | Musical accent on visual event | Cymbal crash on explosion |
| Soft hit | Harmonic change on visual event | Chord change on door opening |
| Mickey-mousing | Music literally follows action | Running notes match footsteps |
| Anticipation | Music reaches accent before visual | Builds to hit slightly early |
| Delayed reaction | Musical response after visual | Emotional realization |
| Underplay | Music ignores obvious hit point | More sophisticated scoring |

### Tempo and Click Track

| Method | Description |
|--------|-------------|
| Free timing | No click, conductor follows streamers/punches |
| Click track | Constant tempo, locked to picture |
| Variable click | Tempo changes mapped to scene |
| Rubato | Click with built-in flex points |
| Streamers | Visual lines crossing screen for cue points |
| Punches | Flash frames at exact hit points |

## Tension-Release for Scenes

### Building Tension

| Step | Musical Technique | Time |
|------|-------------------|------|
| 1 | Quiet sustained note or silence | 0:00 |
| 2 | Add low pulse (heartbeat) | +5s |
| 3 | Dissonant note enters | +10s |
| 4 | Harmonic movement begins (chromatic) | +15s |
| 5 | Rhythm intensifies | +25s |
| 6 | Register expands (higher + lower) | +35s |
| 7 | Full texture, maximum dissonance | +45s |
| 8 | Hit point / climax | +50s |

### Releasing Tension

| Step | Musical Technique | Time |
|------|-------------------|------|
| 1 | Sudden silence or drop to single note | 0:00 |
| 2 | Consonant chord resolves | +2s |
| 3 | Melody enters (warm instrument) | +5s |
| 4 | Simple harmonic progression | +10s |
| 5 | Full resolution cadence | +20s |

```abc
X:2
T:Tension Building Pattern
M:4/4
L:1/8
K:Cm
"^pp - sustained"C,8 | C,8 |
"^+ pulse"C,2z2 C,2z2 | "^+ dissonance"[C,_D,]2z2 [C,_D,]2z2 |
"^chromatic rise"C,2_D,2D,2_E,2 | E,2F,2^F,2G,2 |
"^fff CLIMAX"[G,C_EG_Bc]8 |
```

## Main Title and End Credits

### Main Title Structure

| Section | Duration | Content |
|---------|----------|---------|
| Studio logos | 10-20s | Silence or quiet lead-in |
| Title card | 5-10s | Theme begins, clear statement |
| Main theme | 30-60s | Full theme, memorable |
| Bridge/development | 20-30s | Theme developed |
| Transition | 10-15s | Music settles into first scene |

### End Credits Structure

| Section | Content | Pacing |
|---------|---------|--------|
| Immediate post-climax | Resolution of final scene | Emotional |
| Main theme reprise | Complete statement | Stately |
| Secondary themes | Other leitmotifs return | Varied |
| Development/medley | Extended treatment | Building |
| Final statement | Theme triumphant or reflective | Conclusive |
| Fadeout or final chord | Clean ending | Definitive |

```abc
X:3
T:Main Title Opening (fanfare + theme)
M:4/4
L:1/8
K:Bb
"^Fanfare - fff"B,4 F4 | B4 d4 |
"^Theme enters"B,2 D2 F2 B2 | A2 G2 F2 E2 | D2 F2 B2 d2 | c4 B4 |
```

## Scene-Type Form Templates

### Action Cue Structure

| Section | Bars | Content |
|---------|------|---------|
| Setup | 4-8 | Ostinato begins, tension |
| First action | 16-32 | Driving rhythm, brass stabs |
| Escalation | 8-16 | Rising pitch, thickening |
| Climax | 4-8 | Full orchestra, maximum |
| Resolution/Transition | 4-8 | Quick release or cut |

### Emotional Scene Structure

| Section | Bars | Content |
|---------|------|---------|
| Intro | 4-8 | Sparse, setting mood |
| Theme entry | 8-16 | Solo melody, simple accompaniment |
| Development | 8-16 | Theme elaborated, richer texture |
| Climax | 4-8 | Emotional peak, full strings |
| Resolution | 4-8 | Theme fragments, fading |

### Horror/Suspense Structure

| Section | Bars | Content |
|---------|------|---------|
| Silence | 2-4 | Nothing or near-nothing |
| Unease | 4-8 | Subtle dissonance, drone |
| Building | 8-16 | Increasing tension, rhythm |
| Scare | 1-2 | Sudden loud dissonance |
| Aftermath | 4-8 | Echo, settling |

## Spotting and Timing

### Spotting Session Decisions

| Decision | Description |
|----------|-------------|
| Where music starts | In-point for each cue |
| Where music stops | Out-point, often at scene change |
| What emotion | Fear, joy, tension, nostalgia |
| Which theme | Leitmotif assignment |
| Source vs. underscore | Diegetic or non-diegetic |
| Hit points | Moments music must accent |
| Tempo feel | Slow, moderate, fast |
| No music | Deciding where silence is best |

## Form Adaptation Principles

| Film Constraint | Musical Adaptation |
|----------------|-------------------|
| Scene is 47 seconds | Music must fit exactly 47 seconds |
| Actor pauses vary | Music has flexible sustain points |
| Director wants less | Thin orchestration, fewer notes |
| Scene recut shorter | Music edited (crossfade, cut) |
| Two scenes merged | Transition composed between cues |
| Temp track influence | Match tempo/feel of temp selection |
