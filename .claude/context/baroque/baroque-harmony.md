# Baroque Harmony Reference

## Figured Bass Symbols

| Figure | Meaning | Intervals above bass | Example chord (bass C) |
|--------|---------|---------------------|----------------------|
| (none) | Root pos triad | 5-3 | C-E-G |
| 6 | First inversion | 6-3 | C-E-A (Am/C) |
| 6/4 | Second inversion | 6-4 | C-F-A (F/C) |
| 7 | Root pos seventh | 7-5-3 | C-E-G-Bb (C7) |
| 6/5 | 1st inv seventh | 6-5-3 | C-Eb-G-A (Am7/C) |
| 4/3 | 2nd inv seventh | 6-4-3 | C-D-F#-A (D7/C) |
| 4/2 or 2 | 3rd inv seventh | 6-4-2 | C-D-F-A (Dm7/C) |
| 9-8 | Suspension res | 9 resolves to 8 | |
| 4-3 | Suspension res | 4 resolves to 3 | |
| 7-6 | Suspension res | 7 resolves to 6 | |
| # | Raise 3rd | Picardy / chromatic | |
| b | Lower interval | Flattened interval | |
| + | Augmented | Raised leading tone | |

## Accidentals in Figured Bass

| Symbol | Meaning |
|--------|---------|
| #, +, or slash through number | Raise that interval a semitone |
| b before number | Lower that interval a semitone |
| Natural sign | Cancel previous accidental |
| # alone (no number) | Raise the 3rd above bass |

## Common Baroque Progressions

### Circle of Fifths (descending 5ths sequence)
```
Root motion: I - IV - vii° - iii - vi - ii - V - I
Bass line:   descending 5ths / ascending 4ths
```

ABC example (D major, circle of 5ths):
```abc
X:1
T:Circle of Fifths Sequence
M:4/4
L:1/4
K:D
V:1 clef=treble
[DF] [CE] [B,D] [A,C] | [B,D] [A,C] [A,^C] [DF] |
V:2 clef=bass
[D,A,] [A,,A,] [B,,F,] [F,,E,] | [G,,D,] [D,,C,] [A,,E,] [D,,D,] |
```

### Descending Bass Patterns (Lament Bass)

| Name | Bass line | Typical keys | Usage |
|------|-----------|-------------|-------|
| Chromatic lament | 1-7-b7-6-b6-5 | Minor keys | Arias of grief, passacaglia |
| Diatonic lament | 8-7-6-5 (minor) | D min, G min | Ground bass, chaconnes |
| Romanesca | 3-7-1-5 (ascending) | Major keys | Variation sets |
| Folia | i-V-i-VII-III-VII-i-V | D minor | Variation sets |

ABC example (chromatic lament bass in D minor):
```abc
X:2
T:Chromatic Lament Bass
M:3/4
L:1/4
K:Dm
V:1 clef=treble
[DA] [^CG] [=CE] [DF] | [B,F] [A,E] [A,^C] [D2F2] |
V:2 clef=bass
D, ^C, =C, B,, | _B,, A,, A,, D,,2 |
```

### Pedal Point Patterns

| Type | Description | Typical location |
|------|-------------|-----------------|
| Tonic pedal | Sustained tonic in bass | Opening, closing |
| Dominant pedal | Sustained dominant | Before final cadence |
| Inverted pedal | Sustained note in soprano | Development passages |
| Double pedal | Tonic + dominant sustained | Final bars, toccatas |

## Cadence Types

| Cadence | Progression | Context | ABC snippet (C major) |
|---------|------------|---------|----------------------|
| Authentic (PAC) | V-I, soprano on 1 | Section endings | `[EG][CE] \| [DF][CE]` bass `G,C,` |
| Half cadence | any-V | Mid-phrase | `[CE] \| [B,D]` bass `C,G,` |
| Phrygian | iv6-V (minor) | Slow mvt endings | bass `A,_B,` resolving to `G,` |
| Deceptive | V-vi | Extending phrases | `[B,D][CE]` bass `G,A,` |
| Plagal | IV-I | Amen, codas | `[CF][CE]` bass `F,C,` |
| Evaded | V-I with voice exchange | Delaying resolution | Soprano leaps away |
| Baroque cadence | ii6-V-I with 4-3 sus | Standard baroque ending | `[FA][G4B,4][G3B,3][EC]` |

### Phrygian Half Cadence (characteristic baroque)
```abc
X:3
T:Phrygian Cadence in A minor
M:4/4
L:1/4
K:Am
V:1 clef=treble
[Ac] [Gc] [^G2B2] |
V:2 clef=bass
F, D, E,2 |
```

## Sequences

| Sequence type | Root motion | Bass pattern | Typical figures |
|--------------|-------------|-------------|-----------------|
| Descending 5ths | down 5th/up 4th | step descent | 7, alternating 7-5/3 |
| Descending 3rds | down 3rd/up step | 3rds with steps | 6, 5/3 alternating |
| Ascending 5-6 | up step | stepwise ascent | 5-6, 5-6 pattern |
| Monte | up step (paired) | up step in pairs | 5/3 - 6/3 |
| Fonte | down step (paired) | down by step | 6/5-5/3 repeating |
| Ponte | pedal | repeated note | Dominant pedal |

### Descending 5ths Sequence with 7ths
```abc
X:4
T:Sequential 7ths
M:4/4
L:1/4
K:C
V:1 clef=treble
[cB] [BA] [AG] [GF] | [FE] [ED] [D^F] [Gc] |
V:2 clef=bass
C, F,, B,, E,, | A,, D,, G,, C, |
```

## Continuo Realization Patterns

### Texture Density by Context

| Context | Voices in RH | Rhythm style | Notes |
|---------|-------------|-------------|-------|
| Recitative | 3-4 | Block chords, short | Sustain on fermatas only |
| Aria (slow) | 3 | Arpeggiated, flowing | Double melody sparingly |
| Aria (fast) | 2-3 | Rhythmic, detached | Follow bass rhythm |
| Chorus | 2-3 | Colla parte or independent | Fill gaps in texture |
| Solo sonata | 3-4 | Active, contrapuntal | True 3rd voice |

### Realization Rules

| Rule | Description |
|------|-------------|
| Spacing | Keep RH within octave when possible |
| Doubling | Double root or 5th; never double leading tone |
| Parallels | No parallel 5ths/8ves between outer voices |
| Resolution | 7ths resolve down; leading tones resolve up |
| Range | RH typically c4-d5; avoid crossing solo part |
| Arpeggiation | Break chords bottom-up on sustained harmonies |

## Common Key Relationships

| Home key | Close keys (typical modulations) | Remote (chromatic) |
|----------|--------------------------------|-------------------|
| C major | G major, A minor, F major, D minor | Eb major, Ab major |
| D minor | F major, A minor, G minor, Bb major | D major (Picardy) |
| G major | D major, E minor, C major, A minor | Bb major |
| A minor | C major, E minor, D minor, G major | A major (Picardy) |

## Baroque Harmonic Rhythm

| Tempo/Style | Typical harmonic rhythm | Changes per bar (4/4) |
|-------------|------------------------|----------------------|
| Allegro | 1-2 chords/bar | 1-2 |
| Andante | 2-4 chords/bar | 2-4 |
| Adagio | 4-8 chords/bar | 4-8 |
| Recitative | Irregular, text-driven | Variable |
| Sequences | Regular, 1-2 per unit | Pattern-dependent |

## Chromaticism

| Device | Description | Example context |
|--------|-------------|----------------|
| Secondary dominant | V/V, V/vi, etc. | Tonicizing modulation targets |
| Augmented 6th | Rare in early baroque, more in late | Pre-dominant chromatic |
| Neapolitan | bII6 before V | Dramatic cadences (minor keys) |
| Cross-relation | Chromatic clash between voices | English baroque (Purcell) |
| Picardy 3rd | Major I at end of minor piece | Final cadence convention |

## Voice-Leading Rules (Strict Baroque)

| Rule | Description |
|------|-------------|
| No parallel 5ths/8ves | Between any pair of voices |
| Contrary motion preferred | Especially outer voices |
| Leading tone resolves up | To tonic (except inner voice descending to 5th) |
| 7th resolves down | By step, always |
| Diminished 5th resolves inward | Augmented 4th resolves outward |
| Largest leap: octave | Avoid augmented intervals in melody |
| After a leap | Resolve by step in opposite direction |
| Bass leaps | Octave leaps acceptable; diminished leaps rare |
