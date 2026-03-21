# Classical Harmony Reference

## Functional Harmony (T-PD-D-T)

### Function Groups

| Function | Chords (major key) | Chords (minor key) | Role |
|----------|-------------------|--------------------|----|
| Tonic (T) | I, vi, iii | i, VI, III | Stability, rest |
| Pre-Dominant (PD) | ii, IV, vi | ii*, iv, VI | Tension preparation |
| Dominant (D) | V, vii* | V, vii* | Maximum tension |
| Tonic (T) | I | i | Resolution |

### Standard Progressions by Function

| Pattern | Chords | Usage |
|---------|--------|-------|
| T-D-T | I-V-I | Basic cadential motion |
| T-PD-D-T | I-IV-V-I | Standard phrase |
| T-PD-D-T | I-ii6-V-I | Stronger pre-dominant |
| T-PD-D-T | I-IV-V7-I | With dominant 7th |
| T-PD-D-T | I-ii6/5-V-I | Smooth bass voice leading |
| Extended | I-vi-IV-ii-V-I | Full functional circuit |

## Cadence Patterns

| Cadence | Progression | Soprano | Bass | Strength | Context |
|---------|------------|---------|------|----------|---------|
| PAC | V(7)-I | 2-1 or 7-1 | 5-1 | Strongest | Period endings |
| IAC | V-I | not 1 in soprano | 5-1 | Moderate | Antecedent endings |
| HC | any-V | on 2 or 7 | on 5 | Open | Antecedent, mid-phrase |
| DC | V-vi | 7-1 | 5-6 | Deceptive | Extending phrases |
| Plagal | IV-I | 6-5 or 1-1 | 4-1 | Closing | Codas, "Amen" |
| PC (Phrygian) | iv6-V | 6-5 | 6-5 (desc) | Half | Slow mvt endings (minor) |

### Cadential 6/4

| Stage | Chord | Function | Beat |
|-------|-------|----------|------|
| Approach | ii6 or IV | Pre-dominant | Weak |
| Cad 6/4 | I6/4 | Dominant preparation | Strong |
| Resolution | V or V7 | Dominant | Weak |
| Arrival | I | Tonic | Strong |

```abc
X:1
T:Cadential 6/4 Pattern
M:4/4
L:1/4
K:C
V:1 clef=treble
[FA] [EG] [EG] [EC] |
V:2 clef=bass
D, G, G, C, |
% Chords: ii6 - I6/4 - V - I
```

## Period and Sentence Structure

### Period

| Part | Bars | Cadence | Function |
|------|------|---------|----------|
| Antecedent | 4 (or 8) | HC or IAC | Question |
| Consequent | 4 (or 8) | PAC | Answer |

### Sentence

| Part | Bars | Content |
|------|------|---------|
| Presentation (basic idea) | 2 | Motive stated |
| Presentation (repetition) | 2 | Motive repeated (same or transposed) |
| Continuation | 2 | Fragmentation, sequence, acceleration |
| Cadential | 2 | Cadential progression |

### Sentence ABC Example (C major)
```abc
X:2
T:Classical Sentence Structure
M:4/4
L:1/8
K:C
% Basic idea (bars 1-2)
C2E2 G2c2 | B2A2 G4 |
% Repetition (bars 3-4, transposed up)
D2F2 A2d2 | c2B2 A4 |
% Continuation + fragmentation (bars 5-6)
G2A2 B2c2 | A2B2 c2d2 |
% Cadential (bars 7-8)
e2d2 c2B2 | c8 |
```

### Phrase Expansion Techniques

| Technique | Description | Effect |
|-----------|-------------|--------|
| Internal expansion | Extra bars within phrase | Broadens phrase |
| Cadential extension | Deceptive -> real cadence | Delays closure |
| Prefix | Introductory bar(s) | Sets up phrase |
| Suffix (codetta) | Post-cadential material | Confirms closure |
| Evaded cadence | V resolves irregularly | Restarts phrase |
| One more time | Cadential area repeated | Emphasis |

## Modulation Techniques

### Close-Key Modulations

| From (major) | To | Method | Pivot chord |
|-------------|-----|--------|-------------|
| I | V | I=IV of V | Very common |
| I | vi | I=III of vi | Very common |
| I | IV | V=I of IV, or IV=I directly | Common |
| I | ii | vi=iv of ii | Less common |
| I | iii | I=VI of iii | Less common |

| From (minor) | To | Method | Pivot chord |
|-------------|-----|--------|-------------|
| i | III | i=vi of III | Very common |
| i | v | i=iv of v | Common |
| i | iv | i=v of iv (or direct) | Common |
| i | VII | Through III | Moderate |

### Modulation ABC Example (C major to G major)
```abc
X:3
T:Pivot Chord Modulation
M:4/4
L:1/4
K:C
V:1 clef=treble
[CE] [DF] [EG] [DG] | [DF] [DB] [EC] [DB] | [B,D] [CE] [DF] [B,D] | [CE]4 |
V:2 clef=bass
C, D, E, B,, | A,, G,, C, G,, | G,, A,, B,, G,, | C,4 |
% C: I   ii   iii  (=vi of G)  G: ii  I  IV  V7  I
```

## Secondary Dominants

| Symbol | Target | Chord quality | Resolution | ABC (in C) |
|--------|--------|--------------|------------|------------|
| V/V | V | Major triad | G major | `[D^F]` -> `[DG]` |
| V7/V | V | Dom 7th | G major | `[D^FA]` -> `[DGB]` |
| V/vi | vi | Major triad | A minor | `[^GBE]` -> `[ACE]` |
| V/IV | IV | Dom 7th | F major | `[CE_B]` -> `[CFA]` |
| V/ii | ii | Major triad | D minor | `[^F,AD]` -> `[ADF]` |
| vii*/V | V | Dim triad | G major | `[^FAC]` -> `[GBD]` |
| vii*7/V | V | Dim 7th | G major | `[^FAC_E]` -> `[GBD]` |

## Alberti Bass and Accompaniment Patterns

| Pattern | Description | ABC notation | Context |
|---------|-------------|-------------|---------|
| Alberti bass | Low-high-mid-high | `C,GEG` | Piano sonatas, slow |
| Murky bass | Octave alternation | `C,CC,C` | Energetic passages |
| Drum bass | Repeated chord tones | `C,C,C,C,` | Simple accompaniment |
| Waltz bass | Bass + chord + chord | `C, [EG] [EG]` | Triple meter |
| Tremolo | Rapid alternation | `CGCG CGCG` | Dramatic |
| Broken chord (up) | Ascending arpeggio | `C,EGc` | Moderate tempo |
| Broken chord (mixed) | Varied arpeggio | `C,GE,G` | Varied texture |

### Alberti Bass ABC Example
```abc
X:4
T:Alberti Bass Accompaniment
M:4/4
L:1/16
K:C
V:RH clef=treble
e4 e2d2 c2d2e2f2 | g8 f4e4 |
V:LH clef=bass
C,G,E,G, C,G,E,G, C,G,E,G, C,G,E,G, | C,G,E,G, C,G,E,G, B,,G,D,G, B,,G,D,G, |
```

## Harmonic Rhythm Conventions

| Tempo | Typical changes per bar (4/4) | Notes |
|-------|------------------------------|-------|
| Allegro | 1-2 | One chord per bar common |
| Andante | 2-4 | Change on beats 1 and 3 |
| Adagio | 4-8 | Rich harmonic variety |
| Minuet (3/4) | 1-2 per bar | Often 1 per bar |
| Finale (Presto) | 1 per bar | Very fast harmonic rhythm rare |

### Harmonic Rhythm Acceleration

| Location | Harmonic rhythm | Purpose |
|----------|----------------|---------|
| Phrase opening | Slow (1 per bar) | Establish key |
| Phrase middle | Moderate | Build tension |
| Pre-cadential | Fast (every beat or faster) | Drive to cadence |
| Cadence | Slow (V held) | Prepare resolution |

## Chromaticism in Classical Style

| Device | Description | Usage frequency |
|--------|-------------|-----------------|
| Secondary dominants | V/x chords | Very common |
| Augmented 6th chords | It+6, Fr+6, Ger+6 | Moderate (more in late Classical) |
| Neapolitan 6th | bII6 | Moderate, dramatic cadences |
| Chromatic passing tones | Non-chord tones | Common in inner voices |
| Mode mixture | Borrowing from parallel key | Increasingly common |
| Diminished 7th chords | Leading tone chords | Common, esp. in development |
| Enharmonic modulation | Pivoting on dim7 or Ger+6 | Rare in early Classical; Beethoven |

### Augmented 6th Chords (in C major/minor)

| Type | Notes | Resolution | ABC |
|------|-------|------------|-----|
| Italian +6 | Ab-C-F# | -> G (V) | `[_A,C^F]` -> `[G,BG]` |
| French +6 | Ab-C-D-F# | -> G (V) | `[_A,CD^F]` -> `[G,BG]` |
| German +6 | Ab-C-Eb-F# | -> G (V or cad 6/4) | `[_A,C_E^F]` -> `[G,CE]` |

## Common Tonal Plans

### Sonata Form Key Scheme

| Section | Major key | Minor key |
|---------|-----------|-----------|
| Exposition P | I | i |
| Exposition S | V | III |
| Development | Various (vi, ii, IV, remote) | Various (v, iv, VI, remote) |
| Recap P | I | i |
| Recap S | I | i (or I, mode mixture) |
| Coda | I | I or i |

### Rondo Key Scheme

| Section | Key |
|---------|-----|
| A | I |
| B | V |
| A | I |
| C | vi, IV, or remote |
| A | I |

## Voice-Leading Standards

| Rule | Classical application |
|------|---------------------|
| Parallel 5ths/8ves | Strictly avoided in all voices |
| Direct 5ths/8ves | Avoided in outer voices |
| Leading tone resolution | Up to tonic (may descend in inner voice) |
| 7th resolution | Down by step |
| Common tone retention | Hold shared pitch between chords |
| Contrary outer voices | Preferred, especially at cadences |
| Spacing | No more than octave between adjacent upper voices |
| Crossing | Avoid voice crossing |
