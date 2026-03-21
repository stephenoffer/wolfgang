# Composer Profile: Arvo Part (b. 1935)

## Style Overview

| Element | Part's Approach |
|---------|----------------|
| Core technique | Tintinnabuli (from 1976 onward) |
| Harmonic language | Triadic, diatonic, consonance-focused |
| Aesthetic | Sacred minimalism, silence as music |
| Texture | Two-voice (M + T), sparse, transparent |
| Form | Text-driven, symmetrical, additive |
| Expression | Deep stillness, spiritual intensity |
| Periods | Neo-classical -> Serial/Collage -> Silence -> Tintinnabuli |

## Period Overview

| Period | Years | Key Works | Style |
|--------|-------|-----------|-------|
| Neo-classical | 1958-1963 | Symphony 1, Nekrolog | Shostakovich influence |
| Serial/Collage | 1964-1968 | Collage on B-A-C-H, Credo | 12-tone, polystylism |
| Silence | 1968-1976 | 8 years of study, no major works | Chant, early music study |
| Tintinnabuli | 1976-present | Fur Alina, Tabula Rasa, Spiegel im Spiegel | Tintinnabuli method |

## Tintinnabuli Technique — Complete Reference

### Definition
Two simultaneous voices: one moves stepwise (M-voice), one sounds only notes of the tonic triad (T-voice). Named after Latin "tintinnabulum" (little bell) — the T-voice rings like a bell against the moving M-voice.

### M-Voice (Melody Voice)

| Rule | Description |
|------|-------------|
| Stepwise motion | Moves only by step (major or minor 2nd) |
| Centered on tonic | Revolves around tonic pitch |
| Diatonic only | Uses only notes of the mode |
| Direction patterns | Can ascend, descend, or alternate |
| Rhythmic freedom | Rhythm varies; often follows text |

### T-Voice (Tintinnabuli Voice)

| Rule | Description |
|------|-------------|
| Triad tones only | Sounds only root, 3rd, or 5th of tonic triad |
| Nearest to M-voice | Finds closest triad tone to current M-voice pitch |
| Position types | 1st superior, 2nd superior, 1st inferior, 2nd inferior |
| Alternating | May alternate above/below systematically |
| No stepwise motion | Leaps between triad tones |

### T-Voice Position Types

| Position | Abbreviation | Rule | Example (T in Am triad, M on D) |
|----------|-------------|------|----------------------------------|
| 1st position superior | T1+ | Nearest triad tone above M | E (nearest above D) |
| 2nd position superior | T2+ | Second-nearest triad tone above M | A (second above D) |
| 1st position inferior | T1- | Nearest triad tone below M | C (nearest below D) |
| 2nd position inferior | T2- | Second-nearest triad tone below M | A (second below D) |

### Complete Tintinnabuli Voice Table (A minor triad: A-C-E)

| M-voice pitch | T1+ | T2+ | T1- | T2- |
|---------------|-----|-----|-----|-----|
| A | C | E | E (below) | C (below) |
| B | C | E | A | E (below) |
| C | E | A | A | E (below) |
| D | E | A | C | A (below) |
| E | A | C (above) | C | A |
| F | A | C (above) | E | C |
| G | A | C (above) | E | C |

```abc
X:1
T:Tintinnabuli - M-voice descending, T1+ (Am)
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (1st superior)"
C E A E | A C E A |
V:2 name="M-voice (descending from A)"
A G F E | D C B, A, |
```

```abc
X:2
T:Tintinnabuli - M-voice ascending, T1- (Am)
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (1st inferior)"
E A A C | C E E E |
V:2 name="M-voice (ascending from A)"
A B c d | e f g a |
```

```abc
X:3
T:Tintinnabuli - Alternating above/below
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (alternating T1+/T1-)"
C E A C | E A A E |
V:2 name="M-voice"
A G F E | D C B, A, |
```

## Fur Alina (1976) — Foundational Work

| Aspect | Detail |
|--------|--------|
| Key | B minor |
| Voices | 2: M-voice (RH) + T-voice (LH) |
| M-voice rule | Descending stepwise from B, extending range each phrase |
| T-voice | T2- position (second inferior, B minor triad) |
| Form | Expanding phrases: 1 note, 2 notes, 3 notes... |
| Dynamic | pppp throughout |
| Sustain pedal | Held throughout — notes accumulate |

```abc
X:4
T:Fur Alina Opening (simplified)
M:none
L:1/4
K:Bm
%%staves {1 2}
V:1 name="M-voice (RH)"
B3 | BA3 | BAG3 | BAGF3 |
V:2 name="T-voice (LH)"
^F3 | ^F D3 | ^F DB,3 | ^F DB,^F,3 |
```

## Silence as Music

| Principle | Application |
|-----------|-------------|
| Rests are structural | Silences carry meaning equal to notes |
| Breath marks | Natural pauses between phrases |
| Long fermatas | Extended silence between sections |
| Decay time | Let resonance die naturally |
| Beginning from silence | Pieces emerge from stillness |
| Returning to silence | Pieces dissolve back to nothing |
| Inner silence | Even sounding notes have stillness quality |

## Simple Melodic Lines

| Characteristic | Description |
|---------------|-------------|
| Stepwise | Almost exclusively stepwise motion |
| Narrow range | Often within an octave |
| Centered | Melody revolves around tonic |
| Expanding | Range gradually widens outward |
| Contracting | Range gradually narrows inward |
| Palindromic | Melody mirrors itself |
| Text-derived | Rhythm follows natural speech |

```abc
X:5
T:Expanding Melodic Range
M:4/4
L:1/4
K:Am
"^Phrase 1 (narrow)"A B A z | "^Phrase 2 (wider)"A B c B A z |
"^Phrase 3 (wider)"A B c d c B A z | "^Phrase 4 (widest)"A B c d e d c B A z |
```

## Bell-Like Sonority

| Element | Contribution |
|---------|--------------|
| Triad | Pure, resonant sound |
| Wide spacing | Intervals spread across registers |
| Sustain | Notes ring, overlap |
| Consonance | No dissonance to disrupt ring |
| Attack + decay | Single stroke, natural fade |
| Register contrast | M-voice and T-voice in different octaves |
| Tubular bells | Literal bells in some works (Cantus) |

```abc
X:6
T:Bell-Like Sonority (Cantus in Memory of Benjamin Britten style)
M:4/4
L:1/2
K:Am
"^Bell"[A,, A, A a a'] z | z z |
```

## Choral Writing Mastery

### Characteristics

| Feature | Application |
|---------|-------------|
| Syllabic text setting | One note per syllable, mostly |
| Homophonic | Voices move together rhythmically |
| Tintinnabuli voices | Some voices as T, some as M |
| Simple counterpoint | Two-voice texture expanded to SATB |
| Dynamic restraint | Rarely above mf |
| Breath | Natural phrasing based on text |

### Vocal Range Usage

| Voice | Role Options | Range |
|-------|-------------|-------|
| Soprano | M-voice (ascending) or T-voice (high) | C4-A5 |
| Alto | M-voice or T-voice | F3-D5 |
| Tenor | M-voice or T-voice | C3-A4 |
| Bass | M-voice (descending) or T-voice (low) | E2-E4 |

```abc
X:7
T:SATB Tintinnabuli Texture
M:4/4
L:1/4
K:Am
%%staves {(S A) (T B)}
V:S name="S (T-voice)"
E A E C | A E C A |
V:A name="A (M-voice)"
D C B, A, | G, F, E, D, |
V:T name="T (M-voice)" clef=treble-8
A G F E | D C B, A, |
V:B name="B (T-voice)" clef=bass
A, E, A,, E, | A,, C, E, A,, |
```

## Key Works Reference

| Work | Year | Forces | Key Feature |
|------|------|--------|-------------|
| Fur Alina | 1976 | Solo piano | First tintinnabuli piece |
| Fratres | 1977 | Many versions | Clapping + silence + tintinnabuli |
| Cantus in Memory of B. Britten | 1977 | String orch + bell | Proportional canon, descending |
| Tabula Rasa | 1977 | 2 violins, strings, prepared piano | Double concerto, tintinnabuli |
| Spiegel im Spiegel | 1978 | Violin/cello + piano | Purest tintinnabuli |
| Passio | 1982 | Soloists, choir, ensemble | St. John Passion setting |
| Te Deum | 1984 | Choir, strings, tape | Large-scale tintinnabuli |
| Magnificat | 1989 | Choir | Pure choral tintinnabuli |
| Berliner Messe | 1990 | Choir + organ | Liturgical setting |
| Symphony 4 "Los Angeles" | 2008 | Orchestra + choir | Extended orchestral tintinnabuli |

## Spiegel im Spiegel — Paradigm Work

| Aspect | Detail |
|--------|--------|
| Key | F major |
| Piano | T-voice: arpeggiated F major triad, steady rhythm |
| Violin/Cello | M-voice: expanding stepwise phrases |
| Form | Additive: each phrase extends by one note |
| Dynamic | p throughout, absolutely still |
| Tempo | Very slow, ~q=50-56 |
| Character | Infinite calm, mirror-like |

```abc
X:8
T:Spiegel im Spiegel - Opening (reduction)
M:3/4
L:1/4
K:F
%%staves {1 2}
V:1 name="Violin (M-voice)"
z z F | z F G | F G A |
V:2 name="Piano (T-voice)"
F,CF ACF | F,CF ACF | F,CF ACF |
```

## Structural Techniques

| Technique | Description | Work |
|-----------|-------------|------|
| Proportional canon | Each voice at different speed (1:2:4) | Cantus |
| Additive phrases | Each phrase one note longer | Spiegel, Fur Alina |
| Palindrome | Second half mirrors first | Fratres sections |
| Text-determined form | Sentence structure = musical structure | Passio, Te Deum |
| Expanding/contracting | Material widens then narrows | Many works |
| Cyclic return | Material returns exactly | Fratres |

## Style Markers for Generation

| Parameter | Setting |
|-----------|---------|
| Harmony | Single triad, diatonic mode |
| Voices | Two: M-voice (stepwise) + T-voice (triad) |
| Dynamics | pp-p, rarely above mf |
| Tempo | Slow to very slow (q=40-72 typical) |
| Texture | Transparent, 2-4 voices maximum |
| Silence | Essential structural element |
| Form | Additive phrases, palindrome, text-driven |
| Orchestration | Strings, choir, piano, bells |
| Expression | Stillness, devotion, spiritual intensity |
| Duration | 3-30 minutes typical |

## Compositional Fingerprints

| Fingerprint | Description |
|-------------|-------------|
| Tintinnabuli | M-voice + T-voice, always |
| Triadic purity | Only triad tones in T-voice |
| Stepwise M-voice | Melody by step only |
| Expanding phrases | Each phrase one unit longer |
| Bell sonority | Resonant, ringing quality |
| Sacred stillness | Music of deep quiet |
| Minimal material | Maximum expression from minimum means |
| Text as structure | Musical form follows text structure |
| Silence scoring | Rests and fermatas as composition |
| Descending motion | Gravity, settling, resolution through descent |
