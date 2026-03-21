# Modulation Patterns Reference

## Modulation Types

### 1. Pivot Chord Modulation (Common Chord)

Smoothest modulation. A chord functions in both old and new keys.

| Old Key | Pivot Chord | Dual Function | New Key |
|---------|-------------|---------------|---------|
| C major | Am (vi) | = ii in G | G major |
| C major | Em (iii) | = vi in G | G major |
| C major | Dm (ii) | = vi in F | F major |
| C major | Am (vi) | = i in Am | A minor |
| C major | F (IV) | = bVI in Am | A minor |

```abc
X:1
T:Pivot chord modulation C major to G major
M:4/4
L:1/4
K:C
"^C: I"[CEG]"^IV"[FAc]"^vi=G:ii"[Ace]"^V7"[GBdF]|"^G: I"[GBd]4||
```

### 2. Secondary Dominant Pivot

Use V/x or vii°/x to tonicize the new key, preceded by a pivot chord.

```abc
X:2
T:Secondary dominant to modulate C to D
M:4/4
L:1/4
K:C
"^C: I"[CEG]"^vi=D:v"[Ace]"^V7/V=D:V7"[A^ceg]"^D:I"[D^FAd]|
```

Common secondary dominants: V/V, V/vi, V/IV, V/ii, V/iii

### 3. Direct / Phrase Modulation

New key enters at a phrase boundary with no harmonic preparation.

```abc
X:3
T:Direct modulation C to Db (up semitone)
M:4/4
L:1/4
K:C
"^C: I"[CEG]"^V"[GBd]"^I"[CEGc]z|
K:Db
"^Db: I"[_D_F_A_d]"^V"[_A,C_E_A]"^I"[_D_F_A_d]z|
```

Use at double bars, rehearsal marks, or after rests. Common in pop, film, and late-Romantic.

### 4. Sequential Modulation

A melodic/harmonic pattern repeats at a new pitch level, establishing new key.

```abc
X:4
T:Sequential modulation by step (C to D)
M:4/4
L:1/8
K:C
"^C:"CDEF GABc|"^D:"D^EFG ABcd|"^D: V7"[A,^CEG]4"^I"[DFA]4|
```

Typical step sizes: up by 2nd, down by 3rd. Baroque sequences often chain multiple keys.

### 5. Chromatic Modulation via Augmented 6th

The augmented 6th chord resolves to V of the new key.

```abc
X:5
T:German +6 modulation C to F#/Gb
M:4/4
L:1/2
K:C
"^C: I"[CEG]"^Ger+6->F#"[_AcE_f]|"^F#: V"[^C^EG#^c]"^I"[^F^A^c^f]||
```

| +6 Type | Notes | Resolves to | Best for |
|---------|-------|-------------|----------|
| Italian | b6, 1, #4 | V (open 5th) | Light texture |
| French | b6, 1, 2, #4 | V | Whole-tone color |
| German | b6, 1, b3, #4 | I6/4 -> V (avoid ||5) | Full texture |

### 6. Chromatic Modulation via Neapolitan

bII6 can serve as pivot to distant keys.

```abc
X:6
T:Neapolitan pivot: C minor to Bb minor
M:4/4
L:1/2
K:Cm
"^Cm: i"[C_EG]"^N6=Bb:iv6"[_D_F_B]|"^Bb: V7"[F=A_ec]"^i"[_B_Df]||
```

### 7. Enharmonic Modulation via Diminished 7th

Dim7 chord has 4 enharmonic respellings, each resolving to a different key (minor 2nd above each note).

| Dim7 Chord | Resolves to | As Root |
|-----------|-------------|---------|
| B-D-F-Ab | C minor | B°7 = vii°7/C |
| B-D-F-Ab = D-F-Ab-Cb | Eb minor | D°7 = vii°7/Eb |
| B-D-F-Ab = F-Ab-Cb-Ebb | Gb minor | F°7 = vii°7/Gb |
| B-D-F-Ab = Ab-Cb-Ebb-Gbb | A minor (enharmonic) | Ab°7 = vii°7/A |

```abc
X:7
T:Enharmonic dim7 modulation C to Eb
M:4/4
L:1/2
K:C
"^C: V7"[GBdF]"^vii°7"[Bdf_a]|
K:Eb
"^=vii°7/Eb"[Bdf_a]"^Eb: I"[_EG_Bd]||
```

### 8. Enharmonic Modulation via German +6

Ger+6 is enharmonically equivalent to a dominant 7th chord.

Ger+6 in C (Ab-C-Eb-F#) = Ab7 (Ab-C-Eb-Gb) = V7 of Db

```abc
X:8
T:Enharmonic Ger+6 pivot: C to Db
M:4/4
L:1/2
K:C
"^C: I"[CEG]"^Ger+6=Db:V7"[_AcE_f]|
K:Db
"^Db: I"[_DF_A_d]2||
```

## Modulation Targets by Key Relationship

| Relationship | From C major | Interval | Smoothness |
|-------------|-------------|----------|------------|
| Dominant | G major | +P5 | Very smooth |
| Subdominant | F major | +P4 | Very smooth |
| Relative minor | A minor | -m3 | Smooth |
| Relative of dominant | E minor | +M3 | Smooth |
| Relative of subdominant | D minor | +M2 | Smooth |
| Parallel minor | C minor | 0 (mode) | Moderate |
| Chromatic mediant (upper) | E major | +M3 | Colorful |
| Chromatic mediant (lower) | Ab major | +m6 | Colorful |
| Flat mediant | Eb major | +m3 | Colorful |
| Tritone | F#/Gb major | +TT | Extreme |
| Semitone up | Db major | +m2 | Extreme |
| Semitone down | B major | -m2 | Extreme |

## Modulation Distance by Style Period

| Period | Typical Distance | Common Targets | Method |
|--------|-----------------|----------------|--------|
| Baroque | Close keys (1 accidental) | V, iv, vi, relative | Pivot chord, sequence |
| Classical | Close keys | V, IV, vi, ii, relative | Pivot chord, secondary dom |
| Early Romantic | Close + mediant | V, bVI, III, bIII, vi | Chromatic pivot, +6 chords |
| Late Romantic | Any key | Chromatic mediants, tritone | Enharmonic, direct, sequence |
| Impressionist | Non-functional | Parallel motion, whole-tone | Planing, direct, modal |
| Nationalistic | Modal inflection | Modal centers, bVII, bIII | Modal, direct |
| Film Score | Any, rapid | Semitone, tritone, mediant | Direct, sequential, montage |

## Tonicization vs. Modulation

| Feature | Tonicization | Modulation |
|---------|-------------|------------|
| Duration | 1-2 chords | Full phrase+ |
| Cadence in new key | No | Yes (usually PAC) |
| Notation | V/x or vii°/x | New key area |
| Return to original | Immediate | After extended passage |
| MCD tracking | Note as color | Log key change in continuity.json |

```abc
X:9
T:Tonicization of V (not modulation)
M:4/4
L:1/4
K:C
"^I"[CEG]"^V/V"[DF#A]"^V"[GBd]"^I"[CEG]|
```

## Key Scheme Templates by Form

### Sonata Form
| Section | Major Key | Minor Key |
|---------|-----------|-----------|
| Exposition PT | I | i |
| Exposition ST | V (or III) | III (or v) |
| Development | Unstable -- vi, ii, iv, remote | Unstable -- free |
| Recapitulation PT | I | i |
| Recapitulation ST | I | I or i |
| Coda | I | I (picardy) or i |

### Rondo (ABACA / ABACABA)
| Section | Key |
|---------|-----|
| A (refrain) | I |
| B (1st episode) | V or vi |
| A (return) | I |
| C (2nd episode) | IV, ii, bVI, or remote |
| A (final) | I |

### Theme and Variations
| Section | Key |
|---------|-----|
| Theme | I |
| Vars 1-N | I (with possible mode change) |
| Central var | Relative or parallel minor/major |
| Final var | I |
| Coda | I |

### Ternary (ABA')
| Section | Key |
|---------|-----|
| A | I |
| B | Contrasting (V, vi, IV, bVI) |
| A' | I |

### Binary (AB)
| Section | Key |
|---------|-----|
| A | I -> V (or i -> III) |
| B | V -> I (or III -> i) |

## Modulation Planning Checklist

1. Identify source key and target key
2. Count shared chords (pivot candidates)
3. Choose modulation type based on style period
4. Plan voice leading through the pivot
5. Confirm cadence in new key (at least HC)
6. Update continuity.json with key change
7. Verify smooth bass line through transition

## Modulatory Sequences

| Sequence Type | Pattern | Keys Touched |
|--------------|---------|-------------|
| Descending 5ths | I-IV-vii°-iii-vi-ii-V-I | Tonicizes each step |
| Ascending 2nds | I-ii-iii-IV-V | Real sequence, shifts key |
| Descending 3rds | I-vi-IV-ii | Circle of mediants |
| Chromatic ascending | I-bII-II-bIII-III... | Semitone drift |
| Rosalia (up by step) | Pattern repeats up M2 | Each repetition = new key |

```abc
X:10
T:Rosalia sequence (ascending by step)
M:4/4
L:1/8
K:C
"^C:"CEGC EGCE|"^D:"DF^AD F^ADF|"^E:"E^G^BE ^G^BE^G|
```
