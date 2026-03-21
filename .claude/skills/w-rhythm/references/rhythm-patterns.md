# Rhythm Patterns Reference

## Simple Meter Patterns

### 4/4 (Common Time)

| Pattern Name | ABC Rhythm | Description |
|-------------|------------|-------------|
| Whole note | `C4` | Sustained |
| Half notes | `C2 E2` | Steady, hymn-like |
| Quarter notes | `C D E F` | Walking, march |
| Eighth notes | `CD EF GA Bc` | Running, energetic |
| Dotted quarter-eighth | `C3/2D/2 E3/2F/2` | Lilting, speech-like |
| Triplet quarters | `(3CDE (3FGA` | Fluid forward motion |
| Syncopated | `C/2 D C/2 D/2 E C/2` | Off-beat stress |
| Scotch snap | `C/2D3/2 E/2F3/2` | Short-long (reversed dot) |
| Backbeat | `z/2C/2 z/2C/2 z/2C/2 z/2C/2` | Emphasis on 2 and 4 |

```abc
X:1
T:4/4 Rhythmic patterns
M:4/4
L:1/8
K:C
"^walking"C2 D2 E2 F2|"^running"CDEF GABc|"^dotted"C3D E3F G3A B3c|"^syncopated"C2 DE F2 GA|
```

### 3/4

| Pattern | ABC | Usage |
|---------|-----|-------|
| Quarter notes | `C D E` | Simple triple, chorale |
| Half + quarter | `C2 D` | Gentle waltz |
| Quarter + half | `C D2` | Sarabande emphasis |
| Dotted half | `C3` | Sustained, chorale fermata |
| Eighth pairs | `CD EF GA` | Lively triple |

```abc
X:2
T:3/4 patterns
M:3/4
L:1/8
K:C
"^waltz"C4 D2|"^sarabande"C2 D4|"^lively"CDEF GA|"^minuet"C2D2 E2|
```

### 2/4

| Pattern | ABC | Usage |
|---------|-----|-------|
| March | `C D` (quarters) | Military, processional |
| Polka | `CD EF` (eighths) | Dance |
| Dotted march | `C3/2D/2 E3/2F/2` | Military snap |

## Compound Meter Patterns

### 6/8

| Pattern | ABC | Description |
|---------|-----|-------------|
| Standard | `C2D E2F` | Two groups of 3 |
| Lilting | `C3 D3` | Dotted-quarter feel |
| Barcarolle | `C2D E3` | Gentle rocking |
| Jig | `CDE FGA` | Fast dance |
| Tarantella | `CDE CDE` | Frantic dance |
| 3+3 vs 2+2+2 | `CDE FGA` vs `CD EF GA` | Hemiola |

```abc
X:3
T:6/8 patterns
M:6/8
L:1/8
K:C
"^standard"C2D E2F|"^barcarolle"C3 E3|"^jig"CDE FGA|"^hemiola trick"C2D2E2|
```

### 9/8

| Pattern | ABC | Usage |
|---------|-----|-------|
| Triple compound | `C2D E2F G2A` | Three dotted-quarter beats |
| Slip jig | `CDE FGA BcB` | Irish dance |

### 12/8

| Pattern | ABC | Usage |
|---------|-----|-------|
| Slow blues | `C3 E3 G3 c3` | Dotted-quarter pulse |
| Shuffle | `C2D E2F G2A B2c` | Swing feel |
| Pastoral | `C3 E2D C2D E3` | Gentle compound quadruple |

```abc
X:4
T:12/8 pastoral
M:12/8
L:1/8
K:C
C3 E2D C2D E3|F3 A2G F2G A3|
```

## Asymmetric Meters

### 5/4 (2+3 or 3+2)

```abc
X:5
T:5/4 patterns
M:5/4
L:1/4
K:C
"^2+3"C D E F G|"^3+2"C D E F G|
```

| Grouping | Feel | Famous Example |
|----------|------|----------------|
| 2+3 | Short-long | Holst "Mars" |
| 3+2 | Long-short | Tchaikovsky Sym. 6, mvt 2 |
| 5 even | Floating | Bartok, Brubeck "Take Five" |

### 7/8 (2+2+3, 3+2+2, 2+3+2)

```abc
X:6
T:7/8 groupings
M:7/8
L:1/8
K:C
"^2+2+3"CD EF GBc|"^3+2+2"CDE FG AB|"^2+3+2"CD EFG AB|
```

### 5/8 (2+3 or 3+2)

```abc
X:7
T:5/8 patterns
M:5/8
L:1/8
K:C
"^2+3"CD EFG|"^3+2"CDE FG|
```

## Dance Rhythms

| Dance | Meter | Tempo | Characteristic Rhythm (ABC) |
|-------|-------|-------|----------------------------|
| Waltz | 3/4 | Moderate-fast | `C2 DE FG` (strong 1) |
| Minuet | 3/4 | Moderate | `C2D2 E2` (stately) |
| Polonaise | 3/4 | Moderate | `C/2D/2E E C2` (dotted rhythm on 1) |
| Mazurka | 3/4 | Moderate | `C2 D2 E2` (accent 2 or 3) |
| Sarabande | 3/4 | Slow | `C2 D4` (accent beat 2) |
| Gavotte | 4/4 | Moderate | starts beat 3: `z2 CD \| E2F2 G4` |
| Bourree | 2/2 | Lively | starts beat 2: `z2 CD \| E4 F2G2` |
| Gigue | 6/8 or 3/8 | Fast | `CDE FGA \| BcB AGF` (fugal) |
| Tarantella | 6/8 | Very fast | `CDECDE \| FGAFGA` (perpetual motion) |
| Bolero | 3/4 | Moderate | `C/2C/2C C/2C/2C C2` (snare pattern) |
| March | 4/4 or 2/4 | Various | `C3/2D/2 E2 F2 G2` (dotted figures) |
| Siciliana | 6/8 | Slow-moderate | `C3/2D/2E F3` (dotted lilting) |

### ABC Dance Examples

```abc
X:8
T:Waltz pattern
M:3/4
L:1/8
K:C
V:melody
V:accomp
[V:melody] c2 Bc de|f2 ef dc|
[V:accomp] C,2 [EG]2 [EG]2|F,2 [FA]2 [FA]2|
```

```abc
X:9
T:Mazurka pattern (accent beat 3)
M:3/4
L:1/8
K:C
C2 D2 !accent!E2|F2 G2 !accent!A2|
```

```abc
X:10
T:Polonaise rhythm
M:3/4
L:1/16
K:C
C2D2E4 E4|F2G2A4 A4|
```

```abc
X:11
T:Gigue in 6/8
M:6/8
L:1/8
K:C
CEG cGE|DFA dAF|EGB edc|BAG FED|
```

## Accompaniment Patterns

| Pattern | Description | ABC Example |
|---------|-------------|-------------|
| Alberti bass | Broken chord: low-high-mid-high | `CEGEG` -> `C/2G/2E/2G/2` per beat |
| Oom-pah | Bass + chord alternation | `C,2 [EG]2` |
| Oom-pah-pah | 3/4 version | `C,2 [EG]2 [EG]2` |
| Broken chord | Arpeggiated | `C,E,G,C` |
| Tremolo | Rapid alternation | `C8-` or `!trem!C4` |
| Ostinato | Repeating figure | Any short pattern repeated |
| Stride | Bass-chord (wide) | `C,,2 [CEG]2` (LH piano) |
| Murky bass | Octave alternation | `C,C C,C` |
| Drum bass | Repeated notes | `C,C,C,C,` |

```abc
X:12
T:Alberti bass
M:4/4
L:1/16
K:C
V:RH
V:LH
[V:RH] e4 d4 c4 B4|
[V:LH] CEGECEGE CEGECEGE|
```

```abc
X:13
T:Oom-pah-pah waltz accompaniment
M:3/4
L:1/4
K:C
V:mel
V:acc
[V:mel] e d c |
[V:acc] C, [EG] [EG] |
```

## Rhythmic Development Techniques

| Technique | Description | ABC Example |
|-----------|-------------|-------------|
| Augmentation | Double all durations | `CDEF` -> `C2D2E2F2` |
| Diminution | Halve all durations | `C2D2E2F2` -> `CDEF` |
| Syncopation | Shift accents off-beat | `z/2C/2 C z/2C/2 C` |
| Hemiola | 3-against-2 feel | `C2D2E2` in 6/8 (sounds 3/4) |
| Polyrhythm | 2 simultaneous meters | 3-vs-2: `(3CDE` vs `C2D2` |
| Cross-rhythm | Accent pattern against meter | 3/4 with `C/2D/2 E/2F/2 G/2A/2` accented in 2s |
| Displacement | Shift entire pattern | `CDEF` -> `zCDE F` |
| Additive | Build up layers | 1 note -> 2 -> 4 -> 8 |

```abc
X:14
T:Hemiola in 3/4 (last 2 bars)
M:3/4
L:1/4
K:C
C D E|F G A|"^hemiola"B2 c2 d2|
```

## Style-Period Rhythmic Characteristics

| Period | Meter | Typical Rhythms | Special Features |
|--------|-------|----------------|-----------------|
| Baroque | Simple/compound, alla breve | Steady pulse, running 16ths, dotted | Rhythmic motoric drive, notes inegales |
| Classical | 4/4, 3/4, 2/4 | Clear phrase-based, Alberti bass | Regular 4+4 phrases, cadential rhythm |
| Romantic | All standard meters | Rubato, cross-rhythms, triplets vs duplets | Expressive flexibility, polyrhythm |
| Late Romantic | All, some asymmetric | Complex tuplets, metric ambiguity | Metric fluidity, tempo modification |
| Impressionist | All, often 5/4, 7/8 | Free, speech-like, overlapping | Rhythmic dissolution, no strong downbeat |
| Nationalistic | Folk meters (7/8, 11/8, 5/8) | Additive meters, folk dance patterns | Aksak rhythms, regional dance |
| Minimalist | Steady pulse | Phase shifting, additive process | Constant 8ths/16ths, gradual change |
| Film Score | Any | Ostinato, rhythmic builds, sudden silence | Rhythmic sync to picture, hybrid meters |

## Tuplet Notation in ABC

| Tuplet | ABC Syntax | Meaning |
|--------|-----------|---------|
| Triplet | `(3CDE` | 3 notes in time of 2 |
| Duplet (in compound) | `(2CD` | 2 notes in time of 3 |
| Quintuplet | `(5CDEFG` | 5 in time of 4 |
| Sextuplet | `(6CDEFGA` | 6 in time of 4 |
| Septuplet | `(7CDEFGAB` | 7 in time of 4 |
| General | `(p:q:r` | p notes in time of q, next r notes |

```abc
X:15
T:Tuplet examples
M:4/4
L:1/8
K:C
(3CDE (3FGA (3Bcd (3efg|(5CDEFG (5ABcde (3fga (3bag|
```

## Pickup (Anacrusis) Notation

```abc
X:16
T:Pickup bar
M:3/4
L:1/4
K:C
E|"^full bar"C D E|F G A|
```
ABC auto-detects incomplete first bar as anacrusis.

## Ties, Dotted, and Rests

| Element | ABC Syntax | Example |
|---------|-----------|---------|
| Dotted note | Add 3/2 multiplier | `C3/2` (dotted quarter when L:1/4) |
| Double dot | Add 7/4 multiplier | `C7/4` |
| Tie | Hyphen after note | `C2-C2` (half tied to half) |
| Quarter rest | `z` | `Cz Dz` |
| Eighth rest | `z/2` | `Cz/2 Dz/2` |
| Half rest | `z2` | `z2 C2` |
| Whole rest | `z4` (in 4/4) | `z4` |
