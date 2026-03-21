# Modern Harmony Reference (c. 1900–1975)

## Polytonality & Bitonality

| Technique | Description | Common Usage |
|-----------|-------------|--------------|
| Bitonality | Two keys simultaneously | Milhaud, Stravinsky Petrushka chord |
| Polytonality | 3+ keys simultaneously | Ives, Milhaud |
| Petrushka chord | C major + F# major superimposed | Iconic bitonal sonority |
| Polytonal cadence | Each layer resolves in own key | Independence of strata |
| Bitonal melody | Melody in one key, accomp in another | Tension without atonality |

### Petrushka Chord (C + F#)
```abc
X:1
T:Petrushka Chord - Bitonality
M:4/4
L:1/4
K:C
%%staves {1 2}
V:1
[CEG]2 [CEG]2 |
V:2
[^F^A^c]2 [^F^A^c]2 |
```

## Quartal & Quintal Harmony

| Structure | Intervals | Sound Character | Example Composer |
|-----------|-----------|-----------------|-----------------|
| Quartal triad | P4+P4 (C-F-Bb) | Open, ambiguous | Hindemith, Bartok |
| Quintal triad | P5+P5 (C-G-D) | Spacious, hollow | Copland, Barber |
| Mixed 4ths/5ths | P4+P5 or P5+P4 | Flexible modern | Debussy, Ravel |
| Quartal stack | 4+ perfect 4ths | Dense, bright | Schoenberg Op. 16 |
| Tritone-quartal | P4+A4 | Tense, unstable | Berg |

```abc
X:2
T:Quartal Harmony Voicings
M:4/4
L:1/2
K:C
[CFB] [GcF] | [DAG] [EAd] | [CF_B_E] [G_ce] |
```

## Pandiatonicism

| Principle | Description |
|-----------|-------------|
| Definition | Free use of diatonic scale without functional hierarchy |
| No leading tone pull | 7th degree moves freely |
| No dominant function | V chord has no special role |
| Stacked diatonics | Any combination of white-note pitches |
| Copland sound | Open 5ths, widely spaced diatonic clusters |

```abc
X:3
T:Pandiatonic Cluster Voicing
M:3/4
L:1/2
K:C
[CEGB]3/2 [DFAC]3/2 | [EGBD]3/2 [FACE]3/2 |
```

## Tone Clusters

| Type | Construction | Composer |
|------|-------------|----------|
| Chromatic cluster | Adjacent chromatic pitches | Cowell, Penderecki |
| Diatonic cluster | Adjacent diatonic pitches | Cowell, Ives |
| Forearm cluster | All notes under forearm on keyboard | Cowell |
| Orchestral cluster | Divisi strings, each on adjacent pitch | Penderecki, Ligeti |
| Microcluster | 2-3 adjacent semitones | Bartok, Berg |

## Twelve-Tone Technique (Dodecaphony)

| Element | Rule |
|---------|------|
| Tone row (P-0) | All 12 chromatic pitches, each used once |
| Prime (P) | Row in original order |
| Retrograde (R) | Row backwards |
| Inversion (I) | Intervals flipped |
| Retrograde-Inversion (RI) | Inversion backwards |
| Transpositions | Each form transposable to 12 starting pitches |
| Matrix | 12x12 grid of all 48 row forms |
| Combinatoriality | Row pairs that together fill chromatic |
| Hexachordal | First 6 and last 6 pitches as sub-units |

### Example Row and Forms
```abc
X:4
T:12-Tone Row Example (P-0)
M:4/4
L:1/8
K:C clef=treble
C _E G ^F _B A D ^G E B ^C F |
```

| Row Form | Pitch Sequence |
|----------|---------------|
| P-0 | C Eb G F# Bb A D G# E B C# F |
| R-0 | F C# B E G# D A Bb F# G Eb C |
| I-0 | C A F F# D Eb Bb E G# D# B G |
| RI-0 | G B D# G# E Bb Eb D F# F A C |

## Set Theory Basics

| Concept | Definition | Example |
|---------|-----------|---------|
| Pitch class (pc) | Note regardless of octave (0-11) | C=0, C#=1 ... B=11 |
| Pitch-class set | Unordered collection of pcs | {0,1,6} = C,Db,F# |
| Normal form | Most compact ordering | [0,1,6] |
| Prime form | Most compact, starting on 0 | (0,1,6) |
| Interval class (ic) | Distance mod 12, max 6 | ic between C and G# = 4 |
| Interval vector | Tally of all ics in a set | [0,1,6] → <100011> |
| Set class 3-5 | (0,1,6) — common modern sound | Webern, Berg |
| Set class 4-Z29 | (0,1,3,7) — all-interval tetrachord | Highly varied sound |

## Messiaen's Modes of Limited Transposition

| Mode | Structure (semitones) | Transpositions | Character |
|------|-----------------------|----------------|-----------|
| Mode 1 | 2-2-2-2-2-2 (whole tone) | 2 | Floating, Debussy |
| Mode 2 | 1-2-1-2-1-2-1-2 (octatonic) | 3 | Dark, symmetrical |
| Mode 3 | 2-1-1-2-1-1-2-1-1 | 4 | Rich, chromatic |
| Mode 4 | 1-1-3-1-1-1-3-1 | 6 | Exotic |
| Mode 5 | 1-4-1-1-4-1 | 6 | Sparse |
| Mode 6 | 2-2-1-1-2-2-1-1 | 6 | Flexible |
| Mode 7 | 1-1-1-2-1-1-1-1-2-1 | 6 | Dense |

```abc
X:5
T:Messiaen Mode 2 (Octatonic)
M:4/4
L:1/8
K:C
C ^C ^D E ^F G A _B c |
```

```abc
X:6
T:Messiaen Mode 3
M:4/4
L:1/8
K:C
C D _E E ^F G _A A B c |
```

## Neo-Classical Harmony

| Technique | Description | Example |
|-----------|-------------|---------|
| Diatonic dissonance | Added tones to triads without resolution | Stravinsky Pulcinella |
| Wrong-note style | Expected note displaced by semitone | Prokofiev |
| Pandiatonic clusters | Non-functional diatonic stacking | Copland, Stravinsky |
| Modal cadence | Cadence on modal degree, not V-I | Mixolydian bVII-I |
| Ostinato harmony | Static bass, shifting upper voices | Stravinsky |
| Superimposed triads | Two triads at non-standard interval | Ravel, Stravinsky |

```abc
X:7
T:Neo-Classical Cadence (Diatonic Dissonance)
M:4/4
L:1/4
K:C
[EGBd] [FAce] | [GBdf] [CEGc] |
```

## Modal Chromaticism

| Scale | Pattern | Color |
|-------|---------|-------|
| Lydian-Mixolydian | 1 2 3 #4 5 6 b7 | Bright but grounded |
| Lydian-Dominant | Same as above | Bartok's acoustic scale |
| Phrygian-Dominant | 1 b2 3 4 5 b6 b7 | Spanish, Middle Eastern |
| Double harmonic | 1 b2 3 4 5 b6 7 | Byzantine, exotic |
| Acoustic scale | C D E F# G A Bb | Overtone-derived, Bartok |

```abc
X:8
T:Acoustic Scale (Lydian-Dominant / Bartok Scale)
M:4/4
L:1/8
K:C
C D E ^F G A _B c |
```

## Harmonic Application Matrix

| Context | Technique | Tension Level |
|---------|-----------|---------------|
| Lyrical theme | Modal chromaticism, pandiatonic | Low-Medium |
| Development | Polytonality, set-class manipulation | High |
| Climax | Tone clusters, maximal dissonance | Very High |
| Resolution | Quartal spacing, open 5ths | Medium-Low |
| Ostinato passage | Bitonal layering | Medium |
| Recapitulation | Neo-classical diatonic dissonance | Medium |
| Coda | Pandiatonic haze, Messiaen modes | Variable |

## Voice-Leading in Modern Harmony

| Principle | Application |
|-----------|-------------|
| Semitone displacement | Move one voice by half step for color change |
| Parallel motion | Planing of quartal/quintal chords accepted |
| Intervallic consistency | Maintain same interval class through passage |
| Registral stratification | Each layer in its own register |
| Chromatic wedge | Voices converge/diverge by semitone |
| Pitch-axis symmetry | Voices mirror around central pitch (Bartok) |

```abc
X:9
T:Chromatic Wedge Voice Leading
M:4/4
L:1/4
K:C
[E,G,] [F,^F,] | [^F,F,] [G,E,] | [^G,_E,] [A,D,] |
```

## Chord-Voicing Quick Reference

| Voicing Type | Structure | Use Case |
|-------------|-----------|----------|
| Quartal stack | P4-P4-P4 | Ambiguous, modern |
| Split triad | Root + 5th low, 3rd + 7th high | Jazz-influenced modern |
| Cluster voicing | Adjacent 2nds | Percussive, dense |
| Superimposed triads | Two triads, m2/M2/m3 apart | Bitonal shimmer |
| Symmetric | Intervals mirror around axis | Bartokian |
| Added-note triad | Triad + 2nd, 4th, or 6th | Neo-classical color |

## Common Progressions (Non-Functional)

| Pattern | Motion | Effect |
|---------|--------|--------|
| Chromatic mediant | C → Ab or C → E | Dramatic color shift |
| Tritone shift | C → F# | Maximum distance |
| Semitone slide | C → Db | Eerie, uncanny |
| Whole-tone drift | C → D → E | Floating, no gravity |
| Modal plateau | I → bVII → I (mixolydian) | Earthy, grounded |
| Quartal planing | Parallel 4th chords, stepwise | Atmospheric glide |
