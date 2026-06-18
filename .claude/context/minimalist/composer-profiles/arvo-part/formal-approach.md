# Arvo Pärt — Formal Approach

## Core Principle: Form as Process

Pärt does not use Classical forms (sonata, rondo, scherzo). Form emerges from the tintinnabuli process itself — the additive/subtractive expansion of stepwise melody determines the piece's shape, duration, and proportions.

## Primary Formal Types

| Form Type | Structure | Works |
|-----------|-----------|-------|
| Additive expansion | Phrases grow by one step each iteration | *Für Alina*, *Spiegel im Spiegel* |
| Canonic descent | Same melody at multiple speeds in canon | *Cantus in Memoriam Benjamin Britten* |
| Text-driven | Phrase structure follows text sentences/verses | *Passio*, *Miserere*, *Berliner Messe* |
| Proportional arch | Ascending half mirrors descending half | *Fratres* (variations) |
| Single-process | One process runs from start to finish without interruption | *Für Alina*, *Cantus* |
| Variation | Theme restated with changed T-voice position or register | *Fratres* |

## Additive/Subtractive Process Form

| Section | Phrase Length | Process |
|---------|-------------|---------|
| Opening | 2 notes | Shortest phrase |
| Build 1 | 3 notes | +1 note |
| Build 2 | 4 notes | +1 note |
| Build 3 | 5 notes | +1 note |
| ... | ... | Continue expanding |
| Peak | Maximum length | The longest phrase = the formal peak |
| (Silence) | 0 notes | Structural rest |
| Contract 1 | N-1 notes | -1 note |
| Contract 2 | N-2 notes | -1 note |
| ... | ... | Continue contracting |
| Close | 2 notes or 1 note | Return to beginning |

```abc
X:1
T:Additive Process Form (schematic)
M:4/4
L:1/4
K:Am
V:1 name="M-voice"
A B A z | A B C B A z z z | A B C D C B A z | A B C D E D C B |
% Phrase 1: 2 notes. Phrase 2: 3 notes. Phrase 3: 4 notes. Continue expanding.
```

## Canonic Process Form (Cantus Model)

| Layer | Entry Point | Speed | Duration |
|-------|------------|-------|----------|
| Layer 1 (highest) | Bar 1 | Fastest (sixteenths) | Full piece |
| Layer 2 | Bar 1 | Half speed (eighths) | Full piece |
| Layer 3 | Bar 1 | Quarter speed (quarters) | Full piece |
| Layer 4 | Bar 1 | Eighth speed (halves) | Full piece |
| Layer 5 (lowest) | Bar 1 | Slowest (wholes) | Full piece |
| Bell | Bar 1 | Single toll | Rings and decays |

All layers play the same descending scale. The piece ends when the slowest layer reaches the tonic.

```abc
X:2
T:Canonic Descent Form (Cantus model, 3 layers)
M:4/4
L:1/16
K:Am
%%staves {1 2 3}
V:1 name="Fast"
AGFE DCBA | GFED CBA,G, | F,E,D,C, B,,A,,z2 |
V:2 name="Medium"
A2G2 F2E2 | D2C2 B,2A,2 | G,2F,2 E,2D,2 |
V:3 name="Slow"
A,4 G,4 | F,4 E,4 | D,4 C,4 |
```

## Text-Driven Form (Sacred Choral Works)

| Text Element | Musical Response | Structural Role |
|-------------|-----------------|----------------|
| Sentence | One complete M-voice phrase | Basic formal unit |
| Paragraph | Group of phrases + silence | Section |
| Chapter/section | New register, new T-voice position | Formal division |
| Punctuation (period) | Rest or silence | Phrase ending |
| Climactic word | Highest M-voice pitch | Local peak |
| Final "Amen" | Convergence to unison on tonic | Formal close |

| Work | Text Source | Structural Principle |
|------|-----------|---------------------|
| *Passio* | St. John Passion (Latin) | Narrator = M-voice; Christ = T-voice; crowd = choral |
| *Te Deum* | Te Deum hymn | Verse structure = phrase structure |
| *Miserere* | Psalm 51 | Each verse = one tintinnabuli phrase expanding |
| *Berliner Messe* | Mass ordinary | Kyrie/Gloria/Credo/Sanctus/Agnus Dei sections |
| *Magnificat* | Canticle of Mary | Rising phrases for "Magnificat anima mea" |

## Fratres — Variation Form

| Element | Treatment |
|---------|-----------|
| Theme | 6-bar tintinnabuli phrase + 1-bar silence = 7-bar unit |
| Variations | Same M-voice melody, different register, different T-voice position |
| Between variations | Drum pattern or silence (version-dependent) |
| Overall form | 9 variations, each transposed upward by one step |
| Arc | Low register → high register → descent back |

```abc
X:3
T:Fratres Variation Principle (simplified)
M:7/4
L:1/4
K:Am
V:1 name="Var. 1 (low register)"
A, B, C D E D C |
V:1
A B c d e d c |
% Same melody, one octave higher — the variation IS the register shift
```

## Proportional Systems

| System | Principle | Work |
|--------|-----------|------|
| Fibonacci-related | Phrase lengths follow 1-1-2-3-5-8-13 pattern | Some late works |
| Arithmetic expansion | +1 note per phrase | *Für Alina*, early tintinnabuli |
| Geometric expansion | Each phrase doubles the previous | *Cantus* speed relationships |
| Text-proportional | Syllable count determines bar count | All sacred choral works |

## Duration and Pacing

| Element | Typical Duration | Function |
|---------|-----------------|----------|
| Single phrase | 4–16 bars | Building block |
| Silence between phrases | 1–4 bars | Breathing space |
| Section | 20–60 bars | One complete process cycle |
| Full piece | 3–15 min (most); up to 70 min (*Passio*) | One process, lived through completely |

## How a Pärt Piece Ends

| Ending Type | Description | Works |
|-------------|-------------|-------|
| Process completion | The additive/subtractive process finishes naturally | *Für Alina*, *Cantus* |
| Convergence to unison | All voices arrive on the same tonic note | *Cantus*, choral works |
| Fade to silence | Diminuendo to ppp, then nothing | *Spiegel im Spiegel* |
| Bell resonance | Final bell toll, then silence as bell decays | *Cantus* |
| Text completion | The text ends; so does the music | *Passio*, *Te Deum* |

```abc
X:4
T:Convergence Ending (all voices to unison A)
M:4/4
L:1/2
K:Am
%%staves {1 2 3}
V:1 name="Voice 1"
C B, | A, z |
V:2 name="Voice 2"
E, D, | A,, z |
V:3 name="Voice 3"
A, A, | A,, z |
% All three voices converge on A — the music arrives home and stops
```

## References
- Hillier, Paul. *Arvo Pärt* (Oxford Studies of Composers), 1997
- Brauneiss, Leopold. "Tintinnabuli: An Introduction," in *The Cambridge Companion to Arvo Pärt*, 2012
- Quinn, Peter. "Formal Processes in Pärt's Tintinnabuli Music," *Music Analysis*, 2002
