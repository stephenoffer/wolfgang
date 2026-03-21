# Thematic Techniques Reference for w-themes

## Melodic Construction Principles

### Range Guidelines
| Context | Recommended Range | Notes |
|---------|------------------|-------|
| Vocal-style (cantabile) | Octave to 10th | Singability = memorability |
| Instrumental solo | Up to 2 octaves | Allows virtuosic sweep |
| Motive / cell | Perfect 4th to octave | Compact, easy to develop |
| Chorale theme | 6th to octave | Dignified restraint |
| Fanfare | 5th to 12th | Open, triadic leaps |

### Contour Types
| Contour | Shape | Character | Example Interval Pattern |
|---------|-------|-----------|------------------------|
| Arch | rise then fall | Balanced, classical | +2 +2 +3 -2 -2 -3 |
| Inverted arch | fall then rise | Yearning, romantic | -3 -2 +2 +3 +2 |
| Ascending | steady rise | Aspiring, building | +2 +2 +1 +3 +2 |
| Descending | steady fall | Relaxing, sighing | -2 -1 -2 -3 -2 |
| Wave | oscillating | Lyrical, flowing | +3 -2 +4 -3 +2 -1 |
| Static | narrow band | Tension, recitative | +1 -1 +2 -2 0 +1 |
| Rocket | quick ascent | Energetic, Mannheim style | +3 +3 +4 +5 |

### Climax Placement
| Position | Fraction | Effect |
|----------|----------|--------|
| Golden section | ~0.618 (bar 5 of 8) | Natural, satisfying |
| Late climax | 0.75-0.85 | Dramatic, Romantic |
| Early climax | 0.2-0.3 | Surprising, declamatory |
| Final note | 1.0 | Resolving, cadential |
| Multiple peaks | varies | Complex, developmental |

## Intervallic Vocabulary by Style Period

| Period | Preferred Intervals | Avoided / Rare | Character |
|--------|-------------------|----------------|-----------|
| Baroque | 3rds, 4ths, 5ths, steps | Tritone (melodic), 7ths | Triadic, sequential |
| Classical | Steps, 3rds, 4ths, octave | Augmented intervals | Balanced, diatonic |
| Romantic | 6ths, chromatic steps, dim7 | None avoided | Expressive, wide |
| Late Romantic | Augmented, chromatic | None avoided | Ambiguous, yearning |
| Impressionist | Whole-tone steps, tritones | Leading tones | Floating, modal |
| Nationalistic | Scale-specific (modal) | Chromatic alteration | Folk-derived |
| Modern | All intervals equally | None | Angular, dissonant |
| Minimalist | Octaves, 5ths, steps | Wide leaps | Hypnotic, simple |
| Film Score | Varies by temp, often 5ths/4ths | Depends on mood | Hybrid of all periods |

## Rhythmic Character Types

| Type | Pattern Description | Typical Use | ABC Example (L:1/8) |
|------|-------------------|-------------|---------------------|
| Lyrical | Long-short, gentle syncopation | Cantabile themes | `A3 B c2 d2 \| e3 d c2 B2` |
| March | Dotted rhythm, strong downbeats | Military, heroic | `A3/2B/ c2 A2 G2 \| A3/2B/ c4 z2` |
| Dance (waltz) | Strong 1, light 2-3 | Scherzo, waltz | `c4 BA \| G4 FE` (in 3/4) |
| Dance (minuet) | Stately, even | Classical 3rd mvt | `C2 D2 E2 \| F4 E2` (in 3/4) |
| Declamatory | Irregular, speech-like | Recitative, dramatic | `A A2 z A3 \| B,4 z2 A2` |
| Perpetual motion | Even, continuous | Toccata, moto perpetuo | `CDEF GABC \| DEFG ABcd` |
| Chorale | Even, sustained | Hymn-like | `C4 D4 \| E4 F4` |
| Fanfare | Triadic, dotted | Brass calls, openings | `C2 G,2 C2 E2 \| G3/2A/ G2 E2 C2` |

## Theme Types

### Cantabile Theme
Singable, lyrical melody. Usually 8-16 bars, stepwise with expressive leaps.
```abc
L:1/8
K:Eb
!mp! (B,2 E2) G2 F2 | (A2 G2) F2 E2 | (D2 F2) B2 A2 | G6 z2 |
```

### Motive-Based Theme
Built from a short cell (2-4 notes) repeated and varied.
```abc
L:1/8
K:C
!f! G2 z G G2 z G | A2 B2 c4 | G2 z G G2 z G | F2 E2 D4 |
```

### Chorale Theme
Hymn-like, homophonic, sustained note values.
```abc
L:1/4
K:Bb
M:4/4
!mf! B c d B | c2 d2 | e d c B | A4 |
```

### Fanfare Theme
Triadic, rhythmically bold, brass-idiomatic.
```abc
L:1/8
K:D
!ff! D2 D2 ^F2 A2 | d3/2e/ d2 A2 ^F2 | D2 A,2 D4 |
```

### Passacaglia Theme
Bass-line theme for ground bass variations. 4-8 bars, stepwise with key anchors.
```abc
L:1/4
K:Dm
M:3/4
D E F | G A _B | A G ^F | G2 D |
```

## Theme Length Conventions

| Form Context | Typical Length | Structure |
|-------------|---------------|-----------|
| Sonata - Primary | 8-16 bars | Period (antecedent + consequent) |
| Sonata - Secondary | 8-12 bars | Often lyrical, contrasting |
| Rondo - Refrain | 8-16 bars | Closed, returns to tonic |
| Fugue - Subject | 2-4 bars | Single phrase, modulatory end |
| Variation - Theme | 8-32 bars | Complete harmonic circuit |
| Minuet / Scherzo | 8 bars (each half) | Binary `\|: a :\|\|: b :\|` |
| Song form (ABA) | 8 bars per section | Symmetrical phrases |
| Film cue - Leitmotif | 2-8 bars | Short, instantly recognizable |

## Phrase Structures

### Period (antecedent + consequent)
```
Bars 1-4 (antecedent): opens, ends on half cadence (V)
Bars 5-8 (consequent): similar opening, ends on PAC (I)
```

### Sentence (presentation + continuation)
```
Bars 1-2: basic idea
Bars 3-4: basic idea repeated / varied
Bars 5-8: continuation (fragmentation, acceleration, cadence)
```

### Bar Form (AAB / Stollen)
```
Bars 1-4: Stollen a
Bars 5-8: Stollen a' (same melody, different ending)
Bars 9-16: Abgesang (contrasting continuation + close)
```

## Opening Gesture Types

| Gesture | Description | Effect | ABC Example (L:1/8) |
|---------|-------------|--------|---------------------|
| Anacrusis | Upbeat pickup | Forward momentum | `z6 EF \| G4` |
| Downbeat | Strong first beat | Authority, arrival | `C4 E2 G2` |
| Long note | Sustained entry | Calm, dignity | `C8 \| D4 E4` |
| Leap up | Rising interval | Aspiration, energy | `C,2 G2 c4` |
| Leap down | Falling interval | Weight, gravity | `c2 E2 C4` |
| Scale run | Stepwise ascent | Building, approach | `CDEF GABc` |
| Tremolo | Repeated note | Urgency, agitation | `cccc cccc` |
| Rest-then-note | Silence first | Surprise, intimacy | `z2 z2 C2 E2` |

## Creating Memorable Themes

### Memorability Checklist
1. **Singability**: Can a non-musician hum it? Mostly stepwise, leaps < octave
2. **Distinctive interval**: One "signature" leap that defines it (e.g., rising 6th)
3. **Rhythmic identity**: A unique rhythmic cell (e.g., Beethoven 5th: short-short-short-long)
4. **Repetition with variation**: Repeat core idea with small changes
5. **Clear contour**: Identifiable shape even when transposed
6. **Metric clarity**: Strong beat alignment (or deliberate, consistent syncopation)
7. **Harmonic implication**: Melody implies its own harmony unambiguously

### Connecting Motif Design
Short motifs used for transitions, bridges, and developmental passages:

| Property | Guideline |
|----------|-----------|
| Length | 2-6 notes |
| Interval content | One distinctive interval (4th, tritone, etc.) |
| Rhythmic flexibility | Augmentable and diminishable |
| Tonal ambiguity | Should work in multiple keys |
| Derivation | Often extracted from main theme's head or tail |

```abc
% Main theme head motif
L:1/8
K:C
G2 z G G2 c2 |
% Connecting motif derived from first 3 notes
G2 z G |
% Used sequentially as transition material
G2 z G | A2 z A | B2 z B | c2 z c |
```

## Theme Design by Emotional Character

| Emotion | Key Choices | Contour | Rhythm | Intervals |
|---------|-------------|---------|--------|-----------|
| Heroic | D, Eb, Bb major | Ascending / arch | Dotted, march | 4ths, 5ths, octave |
| Pastoral | F, G, Bb major | Wave / gentle arch | Lilting 6/8 or 3/4 | 3rds, steps, 6ths |
| Tragic | C, D, G minor | Descending | Slow, heavy | Minor 2nds, dim5 |
| Noble | Eb, Ab major | Broad arch | Sustained, even | 4ths, steps |
| Playful | C, G, A major | Bouncing wave | Short, staccato | 3rds, steps |
| Mysterious | Whole-tone, octatonic | Static / chromatic | Irregular | Tritones, half-steps |
| Passionate | Bb, F#, E minor | Wide arch, late climax | Surging, rubato | 6ths, 7ths, chromatic |
