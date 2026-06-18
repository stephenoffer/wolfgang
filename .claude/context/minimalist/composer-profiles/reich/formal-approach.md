# Steve Reich — Formal Approach

## Core Principle: Process as Form

"I am interested in perceptible processes." The formal structure of a Reich piece IS the process — phasing, gradual addition, subtraction. Form is not imposed on the material; form emerges from the process applied to the material.

## Primary Formal Types

| Form Type | Structure | Works |
|-----------|-----------|-------|
| Phase structure | Pattern phases through all offset positions | *Piano Phase*, *Violin Phase* |
| Gradual process | Material added/subtracted one element at a time | *Drumming*, *Music for 18 Musicians* |
| Arch form | Build-up → peak → reduction | *Music for 18 Musicians*, *Tehillim* |
| Section chain | Discrete sections linked by shared material | *Drumming* (4 connected sections) |
| Documentary | Recorded speech drives formal structure | *Different Trains*, *The Cave* |
| Counterpoint | Solo + pre-recorded canons build texture | *Electric Counterpoint*, *Vermont Counterpoint* |

## Phase Structure Form

| Stage | Process | Duration |
|-------|---------|----------|
| Unison | Both players in sync | 30–60 sec |
| Phase shift 1 | Player 2 moves ahead by 1 eighth | 30–60 sec |
| Stabilize | Hold new relationship; listen to emergent pattern | 30–90 sec |
| Phase shift 2 | Player 2 moves ahead by another eighth | 30–60 sec |
| Stabilize | Hold and listen | 30–90 sec |
| ... | Continue through all possible offsets | ... |
| Return to unison | After cycling through all positions | Final section |

### Piano Phase — Complete Formal Map

| Phase Position | Offset | Character | Approximate Duration |
|-------|--------|-----------|---------------------|
| 1 | Unison | Clear, single pattern | 1 min |
| 2 | +1 eighth | First thickening | 1 min |
| 3 | +2 eighths | More complex | 1 min |
| ... | +3 through +11 | Cycling through all relationships | 9 min |
| 12 | +12 = unison again | Return to clarity | 1 min |

```abc
X:1
T:Phase Form — Three Stages
M:4/4
L:1/8
K:C
%%staves {1 2}
V:1 name="Piano 1 (fixed)"
ECGC EGCE | ECGC EGCE |
V:2 name="Piano 2 (shifting: unison → +1 → +2)"
ECGC EGCE | zECGC EGCz |
% Stage 1: unison. Stage 2: offset by 1 eighth. Each stage holds before next shift.
```

## Gradual Addition Form

| Step | Action | Voices Active |
|------|--------|--------------|
| 1 | Single drum plays 1 beat of the pattern | 1 |
| 2 | Add beat 2 (next note of pattern fills in) | 1 |
| 3 | Add beat 3 | 1 |
| ... | Continue until full pattern | 1 |
| N | Full pattern; second voice enters with 1 beat | 2 |
| N+1 | Second voice adds beat 2 | 2 |
| ... | Continue building second voice | 2 |
| 2N | Both voices complete; add third | 3 |

```abc
X:2
T:Gradual Addition Process (Drumming style)
M:4/4
L:1/16
K:C
V:1 name="Building the pattern"
C z z z z z z z z z z z z z z z |
C z z z z z z z C z z z z z z z |
C z z z C z z z C z z z z z z z |
C z z z C z C z C z z z z z z z |
% One beat added per cycle until the full pattern is assembled
```

## Arch Form (Music for 18 Musicians)

| Section | Chord | Process | Dynamic |
|---------|-------|---------|---------|
| Pulsing intro | All 11 chords stated | Overview | p–mp |
| Section I | Chord 1 | Full texture builds | mp |
| Section II | Chord 2 | Patterns develop | mp–mf |
| ... | Chords 3–6 | Rising intensity | mf |
| Section VI (peak) | Chord 6 | Maximum density/energy | f |
| Section VII | Chord 7 | Gradual reduction begins | mf |
| ... | Chords 8–11 | Thinning | mp |
| Section XI | Chord 11 | Sparse, quiet | p |
| Pulsing outro | All 11 chords restated | Summary | p–pp |

## Drumming — Four-Section Chain

| Section | Instruments | Key Material | Duration |
|---------|------------|-------------|----------|
| I | Tuned bongos (4 pairs) | Basic rhythmic pattern | ~20 min |
| II | Marimbas (3) + voices (2) | Same pattern, pitched; resultant melody | ~20 min |
| III | Glockenspiels (3) + piccolo + whistling | Bright, high register | ~15 min |
| IV | All instruments combined | Composite texture | ~15 min |

The connection between sections: the last few bars of each section overlap with the first few bars of the next.

## Documentary Form (Different Trains)

| Section | Content | Recorded Speech |
|---------|---------|-----------------|
| I: "America — Before the War" | Nostalgic, flowing | "From Chicago to New York" train conductor memories |
| II: "Europe — During the War" | Darker, urgent | Holocaust survivor testimonies |
| III: "After the War" | Reflective, mixed | Both American and European memories |

| Formal Principle | How It Works |
|-----------------|-------------|
| Speech melody drives harmony | String quartet follows pitch contour of speech |
| Speech rhythm drives rhythm | Musical patterns match speech rhythm |
| Meaning drives form | Emotional content of speech determines section character |
| Train sounds as material | Recorded train sounds become rhythmic patterns |

```abc
X:3
T:Documentary Form — Speech-to-Music (Different Trains style)
M:4/4
L:1/8
K:Am
%%staves {1 2}
V:1 name="Recorded speech"
A2 B2 c2 A2 |
V:2 name="Viola (doubling speech melody)"
A2 B2 c2 A2 |
% The viola doubles the exact melodic contour of the recorded speech
```

## Section Transitions

| Transition Type | Method | Duration |
|----------------|--------|----------|
| Bass clarinet cue | Bass clarinet plays signal pattern | 2–4 bars |
| Overlapping fade | Old pattern fades as new enters | 4–8 bars |
| Timbral substitution | Same pattern, new instrument | 2–4 bars |
| Abrupt cut | One pattern stops, next starts | Immediate |

## Duration and Pacing

| Scale | Duration | Works |
|-------|----------|-------|
| Short piece | 5–15 min | *Piano Phase*, *Clapping Music* |
| Medium | 15–30 min | *Electric Counterpoint*, *Different Trains* |
| Large | 30–60 min | *Drumming*, *Tehillim* |
| Very large | 55–75 min | *Music for 18 Musicians*, *The Cave* |

## How a Reich Piece Ends

| Ending Type | Description | Works |
|-------------|-------------|-------|
| Return to unison | Phased voices realign | *Piano Phase* |
| Gradual subtraction | Players drop out one by one | *Music for 18 Musicians* |
| Fade to single instrument | Full texture thins to one voice | *Drumming* sections |
| Process completion | The addition/subtraction process finishes | *Clapping Music* |
| Final chord held | Last pulsing chord sustained, then cut | Late ensemble works |

## References
- Reich, Steve. *Writings on Music 1965–2000*, 2002
- Potter, Keith. *Four Musical Minimalists*, 2000
- Schwarz, K. Robert. *Minimalists*, 1996
