# Classical Piano Figuration Patterns (~1750-1820)

Genre-wide building blocks for all Classical piano writing. These are the standard vocabulary — Mozart, Haydn, Clementi, early Beethoven all draw from this shared pool. Every accompaniment and melodic passage should use or combine these patterns.

---

## 1. Accompaniment Patterns

### A01: Alberti Bass (Standard)

| Attribute | Value |
|-----------|-------|
| Pattern | low-high-mid-high (1-5-3-5) |
| Period | Core Classical (~1750-1820) |
| Tempo | Andante to Allegro (80-140) |
| Character | Graceful, flowing, elegant |
| Usage | Default piano sonata LH, slow and moderate movements |
| Composers | Mozart (sonatas), Clementi, Haydn |

```abc
X:1
T:A01 Alberti Bass (Standard)
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! e4 d2c2 d4 e4 | f4 e2d2 c8 |
V:LH clef=bass
C,G,EG, C,G,EG, C,G,EG, C,G,EG, | F,C,AC, F,C,AC, G,D,BD, G,D,BD, |
```

### A02: Alberti Bass (Inverted)

| Attribute | Value |
|-----------|-------|
| Pattern | high-low-mid-low (5-1-3-1) |
| Character | Slightly brighter, more sparkle |
| Usage | Lighter passages, higher register accompaniment |

```abc
X:2
T:A02 Alberti Inverted
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! e4 g4 f4 e4 | d4 c8 z4 |
V:LH clef=bass
G,C,EC, G,C,EC, G,C,EC, G,C,EC, | G,B,,DG, G,B,,DG, C,G,EG, C,8 |
```

### A03: Alberti Bass (Broken-3rd / Extended)

| Attribute | Value |
|-----------|-------|
| Pattern | 1-3-5-3 or 1-5-8-5 spanning wider intervals |
| Character | Fuller, more resonant than standard Alberti |
| Usage | When standard Alberti feels thin; Beethoven broader sonatas |

```abc
X:3
T:A03 Alberti Extended
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! c4 e2d2 c4 B4 | c8 z8 |
V:LH clef=bass
C,E,G,E, C,E,G,E, C,E,G,E, C,E,G,E, | F,A,CA, F,A,CA, G,B,DG, G,B,DG, |
```

### A04: Murky Bass (Octave Alternation)

| Attribute | Value |
|-----------|-------|
| Pattern | Root-octave alternation (C2-C3-C2-C3) |
| Period | Early Classical, Galant style |
| Tempo | Moderate (80-120) |
| Character | Solid, grounded, somewhat archaic |
| Usage | Sturdy accompaniment, simpler textures, early sonatas |

```abc
X:4
T:A04 Murky Bass
M:4/4
L:1/8
K:C
V:RH clef=treble
!mf! [CEG]2 [CEG]2 [CEG]2 [CEG]2 | [DFA]2 [DFA]2 [BDG]2 [BDG]2 |
V:LH clef=bass
C,CC,C C,CC,C | D,DD,D G,,GG,,G |
```

### A05: Drum Bass

| Attribute | Value |
|-----------|-------|
| Pattern | Repeated single bass note on each beat |
| Character | Simple, steady pulse, march-like |
| Usage | Straightforward accompaniment, march passages, minuets |

```abc
X:5
T:A05 Drum Bass
M:3/4
L:1/4
K:G
V:RH clef=treble
!f! B d G | A c F | G B d | G3 |
V:LH clef=bass
G, G, G, | D, D, D, | G, G, G, | G,3 |
```

### A06: Walking Bass

| Attribute | Value |
|-----------|-------|
| Pattern | Stepwise bass movement through chord tones and passing tones |
| Character | Forward momentum, harmonic richness, contrapuntal |
| Usage | Transitions, development passages, variation sets |

```abc
X:6
T:A06 Walking Bass
M:4/4
L:1/8
K:C
V:RH clef=treble
[EG]4 [EG]4 | [FA]4 [DG]4 | [EG]8 |
V:LH clef=bass
C,D,E,F, G,A,B,C | D,E,F,G, A,B,CD | C,8 |
```

### A07: Repeated Chord (Blocked)

| Attribute | Value |
|-----------|-------|
| Pattern | Full chords struck repeatedly on each beat |
| Character | Emphatic, energetic, driving |
| Usage | Forte passages, climaxes, Beethoven dramatic style |
| Composers | Beethoven (Pathetique), Haydn (Sturm und Drang) |

```abc
X:7
T:A07 Repeated Blocked Chords
M:4/4
L:1/8
K:Cm
V:RH clef=treble
!f! [CEG]2 [CEG]2 [CEG]2 [CEG]2 | [DF_A]2 [DF_A]2 [DG_B]2 [DG_B]2 |
V:LH clef=bass
C,2 C,2 C,2 C,2 | F,2 F,2 G,2 G,2 |
```

### A08: Repeated Chord (Broken / Afterbeat)

| Attribute | Value |
|-----------|-------|
| Pattern | Bass note on downbeat, chord on offbeats |
| Character | Lighter than blocked, buoyant |
| Usage | Moderate tempo, accompanimental lightness |

```abc
X:8
T:A08 Broken Repeated Chord
M:4/4
L:1/8
K:C
V:RH clef=treble
!mf! e2 g2 f2 e2 | d2 c2 B4 |
V:LH clef=bass
C,2 [EG]2 C,2 [EG]2 | G,2 [BD]2 G,2 [BD]2 |
```

### A09: Arpeggiated Chord (Ascending)

| Attribute | Value |
|-----------|-------|
| Pattern | Root upward through chord tones across one+ octave |
| Character | Rising energy, opening, aspiration |
| Usage | Phrase openings, transitions, building momentum |

```abc
X:9
T:A09 Ascending Arpeggio
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! e4 d2c2 B4 c4 | d4 e2f2 g8 |
V:LH clef=bass
C,E,G,C E,G,CE C,E,G,C E,G,CE | G,B,D,G, B,D,G,B, G,B,D,G, B,8 |
```

### A10: Arpeggiated Chord (Descending)

| Attribute | Value |
|-----------|-------|
| Pattern | High to low through chord tones |
| Character | Falling, sighing, resolution, calming |
| Usage | Phrase endings, resolution passages, winding down |

```abc
X:10
T:A10 Descending Arpeggio
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! g4 f2e2 d4 c4 | B4 A2G2 G8 |
V:LH clef=bass
CEG,C EG,CE GEC,G, EC,G,E, | CEEC G,CEC G,EC,G, C,8 |
```

### A11: Arpeggiated Chord (Wave / Up-Down)

| Attribute | Value |
|-----------|-------|
| Pattern | Ascending then descending in continuous wave |
| Character | Undulating, perpetual motion, water-like |
| Usage | Lyrical passages, sustained accompaniment |

```abc
X:11
T:A11 Wave Arpeggio
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! e4 g4 f4 e4 | d4 c8 z4 |
V:LH clef=bass
C,E,G,C EG,CE G,CE,G, C,E,G,C | F,A,C,F, A,CF,A, G,B,DG, G,8 |
```

### A12: Tremolo (Measured 8ths)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid alternation between two notes/intervals at eighth-note speed |
| Character | Suspense, tension, sustained energy |
| Usage | Dramatic passages, accompanied recitative, Sturm und Drang |

```abc
X:12
T:A12 Measured Tremolo (8ths)
M:4/4
L:1/8
K:Cm
V:RH clef=treble
!ff! [CE][CE] [CE][CE] [CE][CE] [CE][CE] | [DF][DF] [DF][DF] [DG][DG] [DG][DG] |
V:LH clef=bass
C,G, C,G, C,G, C,G, | F,_A, F,_A, G,_B, G,_B, |
```

### A13: Tremolo (Measured 16ths)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid alternation at sixteenth-note speed |
| Character | Higher tension, more agitated |
| Usage | Climactic passages, storm scenes, Beethoven late sonatas |

```abc
X:13
T:A13 Measured Tremolo (16ths)
M:4/4
L:1/16
K:Cm
V:RH clef=treble
!ff! G2_B2 G2_B2 G2_B2 G2_B2 | _A2c2 _A2c2 G2_B2 G2_B2 |
V:LH clef=bass
C,G,C,G, C,G,C,G, C,G,C,G, C,G,C,G, | F,C,F,C, F,C,F,C, G,D,G,D, G,D,G,D, |
```

### A14: Pedal Point Pattern

| Attribute | Value |
|-----------|-------|
| Pattern | Sustained or repeated bass note while harmony moves above |
| Character | Stability, anticipation (dominant pedal), grounding |
| Usage | Retransitions (dominant pedal), codas (tonic pedal), development endings |

```abc
X:14
T:A14 Dominant Pedal Point
M:4/4
L:1/16
K:C
V:RH clef=treble
!crescendo(! [BD]4 [CE]4 [DF]4 [EG]4 | [FA]4 [EG]4 [DF]4 !crescendo)! [BD]4 |
V:LH clef=bass
G,4 G,4 G,4 G,4 | G,4 G,4 G,4 G,4 |
```

### A15: Chordal Pulse

| Attribute | Value |
|-----------|-------|
| Pattern | Regular chords in both hands, strict rhythmic pulse |
| Character | Hymn-like, majestic, processional |
| Usage | Slow introductions, solemn passages, Beethoven Pathetique opening |

```abc
X:15
T:A15 Chordal Pulse (Slow Introduction)
M:4/4
L:1/4
K:Cm
V:RH clef=treble
!ff! [EGc] [EGc] [F_Ac] [DG_B] | [EGc]4 |
V:LH clef=bass
[C,G,] [C,G,] [F,_A,] [G,_B,] | [C,G,]4 |
```

### A16: Hunting Horn Bass (6/8)

| Attribute | Value |
|-----------|-------|
| Pattern | Strong bass on beat 1, lighter chords on beats 2-3 in compound meter |
| Character | Outdoor, energetic, horn-call evocation |
| Usage | 6/8 finales, rondo themes, pastoral movements |

```abc
X:16
T:A16 Hunting Horn Bass (6/8)
M:6/8
L:1/8
K:D
V:RH clef=treble
!f! d2f a2f | g2e f2d | d2f a2f | d3 z3 |
V:LH clef=bass
D,3 [F,A,]3 | A,,3 [D,F,]3 | D,3 [F,A,]3 | D,3 z3 |
```

### A17: Siciliano Bass (Lilting)

| Attribute | Value |
|-----------|-------|
| Pattern | Dotted rhythm in 6/8 with gentle rocking quality |
| Character | Pastoral, tender, gentle swaying, bittersweet |
| Usage | Slow movements in 6/8, pastoral scenes, arias |

```abc
X:17
T:A17 Siciliano Bass
M:6/8
L:1/16
K:Gm
V:RH clef=treble
!p! d3e f4 d4 | c3d _e4 c4 | B3c d4 B4 | A3B A4 G4 |
V:LH clef=bass
G,6 D,2F,2A,2 | C,6 G,2_B,2D2 | G,6 D,2G,2B,2 | D,6 D,6 |
```

---

## 2. Melodic Figuration Patterns

### M01: Scale Passage (Ascending)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid stepwise ascent through the scale |
| Character | Building energy, brilliance, forward thrust |
| Usage | Transitions, cadenzas, virtuosic passages, approach to climax |

```abc
X:18
T:M01 Ascending Scale Passage
M:4/4
L:1/16
K:C
V:RH clef=treble
!crescendo(! C2D2E2F2 G2A2B2c2 | d2e2f2g2 !crescendo)! a4 g4 |
V:LH clef=bass
C,4 z4 E,4 z4 | G,4 z4 C,8 |
```

### M02: Scale Passage (Descending)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid stepwise descent |
| Character | Resolution, release, closing gesture |
| Usage | Post-climactic descent, cadential approach, phrase endings |

```abc
X:19
T:M02 Descending Scale Passage
M:4/4
L:1/16
K:C
V:RH clef=treble
!f! g2f2e2d2 c2B2A2G2 | F2E2D2C2 C8 |
V:LH clef=bass
C,4 E,4 F,4 G,4 | G,,4 G,,4 C,8 |
```

### M03: Turn Figures (Woven into Melody)

| Attribute | Value |
|-----------|-------|
| Pattern | 4-note ornamental group: upper-main-lower-main |
| Character | Elegant, flowing, vocal quality |
| Usage | Throughout melodic lines, especially at phrase peaks; Mozart signature |

```abc
X:20
T:M03 Turn Figures in Melody
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! E4 {FEDE}E4 G4 {AGFA}G4 | c4 {dcBc}c4 B4 c4 |
V:LH clef=bass
C,G,EG, C,G,EG, C,G,EG, C,G,EG, | F,C,AC, F,C,AC, G,D,BD, C,8 |
```

### M04: Turn Figure (Cadential)

| Attribute | Value |
|-----------|-------|
| Pattern | Turn at the cadence point, decorating the resolution |
| Character | Graceful closure, elegant punctuation |
| Usage | PAC decoration, phrase endings, Galant style |

```abc
X:21
T:M04 Cadential Turn
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! E4 F4 G4 A4 | B4 c2d2c2B2 c4 |
V:LH clef=bass
C,4 D,4 E,4 F,4 | G,8 C,8 |
```

### M05: Trill (Simple, Measured)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid alternation between main note and upper neighbor, metrically precise |
| Character | Sustained tension, brilliance, cadential emphasis |
| Usage | Cadential trills, sustained notes with energy, concerto passages |

```abc
X:22
T:M05 Simple Measured Trill
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! G4 A4 B4 c4 | d2e2d2e2 d2e2d2e2 | c8 z8 |
V:LH clef=bass
E,4 F,4 G,4 A,4 | G,8 G,,8 | C,8 z8 |
```

### M06: Trill (Chained)

| Attribute | Value |
|-----------|-------|
| Pattern | Sequential trills on descending or ascending notes |
| Character | Virtuosic display, heightened brilliance |
| Usage | Cadenzas, bravura passages, concerto finales |

```abc
X:23
T:M06 Chained Trills (Descending)
M:4/4
L:1/16
K:C
V:RH clef=treble
!f! g2a2g2a2 f2g2f2g2 | e2f2e2f2 d2e2d2e2 | c8 z8 |
V:LH clef=bass
C,4 z4 D,4 z4 | E,4 z4 G,4 z4 | C,8 z8 |
```

### M07: Trill with Termination (Nachschlag)

| Attribute | Value |
|-----------|-------|
| Pattern | Trill ending with turn suffix: ...main-upper-main-lower-main |
| Character | Definitive, classical cadential gesture |
| Usage | PAC approach, concerto cadenzas, movement endings |

```abc
X:24
T:M07 Trill with Termination
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! G4 A4 B4 c4 | d2e2d2e2 d2^c2d2c2 | c8 z8 |
V:LH clef=bass
E,4 F,4 G,4 A,4 | G,8 G,,8 | C,8 z8 |
```

### M08: Mordent

| Attribute | Value |
|-----------|-------|
| Pattern | Main-lower-main (rapid 3-note ornament) |
| Character | Crisp, biting accent, emphatic |
| Usage | Downbeat emphasis, strong beats, rhythmic punctuation |

```abc
X:25
T:M08 Mordent Patterns
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! {CB}C4 E4 {EF}E4 G4 | {AG}A4 G4 {FE}F4 E4 | {DC}D4 C8 z4 |
V:LH clef=bass
C,4 z4 C,4 z4 | F,4 z4 D,4 z4 | G,4 C,8 z4 |
```

### M09: Appoggiatura (Short — Acciaccatura)

| Attribute | Value |
|-----------|-------|
| Pattern | Quick grace note resolving immediately to main note |
| Character | Sharp, witty, comic emphasis |
| Usage | Opera buffa style, humorous passages, rhythmic piquancy |

```abc
X:26
T:M09 Short Appoggiatura
M:4/4
L:1/8
K:C
V:RH clef=treble
!mf! {D}C2 E2 {F}G4 | {A}G2 F2 {D}E4 | {F}E2 {B,}C2 C4 |
V:LH clef=bass
C,2 z2 E,4 | F,2 z2 C,4 | G,2 C,2 C,4 |
```

### M10: Appoggiatura (Long — Vocal Style)

| Attribute | Value |
|-----------|-------|
| Pattern | Stressed dissonant note on the beat, resolving down by step |
| Character | Expressive, sighing, operatic pathos |
| Usage | Slow movements, aria-like melodies, emotional weight points |

```abc
X:27
T:M10 Long Appoggiatura (Vocal Sigh)
M:4/4
L:1/8
K:C
V:RH clef=treble
!p! E2 G2 B4 | c2B2 A2G2 | A4 G4 |
V:LH clef=bass
C,2 E,2 G,4 | A,2 G,2 F,2 E,2 | D,4 G,,4 |
```

### M11: Alberti Melody (Melody atop Broken Chord)

| Attribute | Value |
|-----------|-------|
| Pattern | Alberti motion in RH with melodic peak on top notes |
| Character | Flowing, the melody emerges from the figuration |
| Usage | When melody and accompaniment merge in one hand; two-part writing |

```abc
X:28
T:M11 Alberti Melody
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! C,GEG c,GEG C,GEG c,AFA | B,,GDG B,,GDG C,G,E,G, C,4 |
V:LH clef=bass
C,,4 z4 C,,4 z4 | G,,4 z4 C,,8 |
```

### M12: Passage Work (Arpeggiated)

| Attribute | Value |
|-----------|-------|
| Pattern | Rapid broken chords spanning two+ octaves |
| Character | Virtuosic, brilliant, dazzling |
| Usage | Cadenzas, bravura passages, transition climaxes |

```abc
X:29
T:M12 Arpeggiated Passage Work
M:4/4
L:1/16
K:C
V:RH clef=treble
!f! CEGc egce | FAcf acfa | GBdg bGBd | c8 z8 |
V:LH clef=bass
C,4 z4 | F,4 z4 | G,4 z4 | C,8 z8 |
```

### M13: Passage Work (Scalar)

| Attribute | Value |
|-----------|-------|
| Pattern | Extended scale runs spanning multiple octaves |
| Character | Brilliant, sweeping, climactic |
| Usage | Cadenzas, transition endings, approach to structural cadences |

```abc
X:30
T:M13 Scalar Passage Work
M:4/4
L:1/16
K:C
V:RH clef=treble
!f! CDEF GABc defg abc'b | c'4 z4 z8 |
V:LH clef=bass
C,4 z4 z8 | C,4 z4 z8 |
```

### M14: Written-Out Grace Note Patterns

| Attribute | Value |
|-----------|-------|
| Pattern | Small-note ornamental figures written in full notation |
| Character | Precise, measured elegance |
| Usage | When grace note placement must be exact; pedagogical clarity |

```abc
X:31
T:M14 Written-Out Grace Notes
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! D2C2 E4 F2E2 G4 | A2G2F2E2 D2C2B,2C2 | C8 z8 |
V:LH clef=bass
C,G,EG, C,G,EG, C,G,EG, C,G,EG, | F,C,AC, G,D,BD, G,,4 G,,4 | C,8 z8 |
```

### M15: Cadenza Pattern (I6/4 - Trill - Resolution)

| Attribute | Value |
|-----------|-------|
| Pattern | Cadential 6/4 chord, extended trill on supertonic, resolution to tonic |
| Character | Concerto convention, dramatic anticipation and release |
| Usage | Concerto cadenzas, movement endings, structural punctuation |

```abc
X:32
T:M15 Cadenza Pattern
M:4/4
L:1/16
K:C
V:RH clef=treble
%% I6/4 held, then ascending run into trill
!f! [EGc]8 z4 CEGc | efga gfed cedc BAGF | EDEDEDEDE2^C2D2C2 | C8 z8 |
V:LH clef=bass
G,8 z8 | z16 | G,,8 G,,8 | C,8 z8 |
```

### M16: Sequence Pattern (Ascending)

| Attribute | Value |
|-----------|-------|
| Pattern | Short motive transposed upward by step or third |
| Character | Building tension, intensification, urgency |
| Usage | Development sections, transitions, building toward climax |

```abc
X:33
T:M16 Ascending Sequence
M:4/4
L:1/16
K:C
V:RH clef=treble
!crescendo(! C2D2E2D2 D2E2F2E2 | E2F2G2F2 !crescendo)! G2A2B2c2 |
V:LH clef=bass
C,4 z4 D,4 z4 | E,4 z4 G,8 |
```

### M17: Sequence Pattern (Descending, Circle of 5ths)

| Attribute | Value |
|-----------|-------|
| Pattern | Motive sequenced downward following descending fifths |
| Character | Winding down, releasing tension, warm sequential descent |
| Usage | Development episodes, pre-retransition passages |

```abc
X:34
T:M17 Descending 5ths Sequence
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! c2B2A2G2 B2A2G2F2 | A2G2F2E2 G2F2E2D2 | C8 z8 |
V:LH clef=bass
C,4 F,4 B,,4 E,4 | A,,4 D,4 G,,4 G,,4 | C,8 z8 |
```

### M18: Sequence Pattern (Modulating)

| Attribute | Value |
|-----------|-------|
| Pattern | Motive transposed through secondary dominants |
| Character | Harmonic restlessness, exploratory journey |
| Usage | Development sections, dramatic transitions |

```abc
X:35
T:M18 Modulating Sequence
M:4/4
L:1/16
K:C
V:RH clef=treble
!mf! E2^F2G2A2 ^F2^G2A2B2 | ^G2^A2B2^c2 d4 z4 |
V:LH clef=bass
C,4 D,4 D,4 E,4 | E,4 ^F,4 G,4 z4 |
```

---

## 3. Textural Patterns

### T01: Homophonic (Melody + Accompaniment)

| Attribute | Value |
|-----------|-------|
| Pattern | Singing melody in RH, one of the above accompaniment patterns in LH |
| Character | Clear, vocal, the default Classical texture |
| Usage | Theme statements, lyrical passages, the standard starting point |

```abc
X:36
T:T01 Standard Homophonic Texture
M:4/4
L:1/16
K:C
V:RH clef=treble
!p! E4 G4 c4 B4 | A4 G4 F4 E4 | D4 F4 A4 G4 | G8 z8 |
V:LH clef=bass
C,G,EG, C,G,EG, C,G,EG, C,G,EG, | F,C,AC, F,C,AC, D,A,FA, D,A,FA, | G,D,BD, G,D,BD, G,D,BD, G,D,BD, | C,G,EG, C,G,EG, C,8 |
```

### T02: Dialogue Between Hands

| Attribute | Value |
|-----------|-------|
| Pattern | Melody alternates between RH and LH in call-and-response |
| Character | Conversational, witty, operatic |
| Usage | Development sections, playful passages, Haydn humor |

```abc
X:37
T:T02 Hand Dialogue
M:4/4
L:1/8
K:G
V:RH clef=treble
!mf! G2B2 d4 | z8 | e2d2 c2B2 | z8 |
V:LH clef=bass
z8 | G,2B,2 D4 | z8 | E,2D,2 C,2B,,2 |
```

### T03: Unison Octaves

| Attribute | Value |
|-----------|-------|
| Pattern | Both hands playing the same line one or two octaves apart |
| Character | Powerful, dramatic, stark, cutting |
| Usage | Opening statements, dramatic unison passages, Beethoven |

```abc
X:38
T:T03 Unison Octaves
M:4/4
L:1/8
K:Cm
V:RH clef=treble
!ff! C2E2 G2c2 | _A2G2 F2E2 | D2F2 _A2G2 | G4 z4 |
V:LH clef=bass
C,2E,2 G,2C2 | _A,2G,2 F,2E,2 | D,2F,2 _A,2G,2 | G,4 z4 |
```

### T04: Chorale Texture

| Attribute | Value |
|-----------|-------|
| Pattern | Four-part chords in both hands, hymn-like voice leading |
| Character | Solemn, noble, devotional, broad |
| Usage | Slow introductions, codas, variation themes, funeral marches |

```abc
X:39
T:T04 Chorale Texture
M:4/4
L:1/4
K:C
V:RH clef=treble
!p! [EG] [FA] [EG] [EG] | [DF] [EG] [DF] [CE] |
V:LH clef=bass
[C,G,] [D,A,] [E,G,] [C,G,] | [G,,B,] [C,G,] [G,,B,] [C,G,] |
```

### T05: Perpetual Motion (Moto Perpetuo)

| Attribute | Value |
|-----------|-------|
| Pattern | Continuous, unbroken stream of equal-value notes |
| Character | Restless energy, brilliance, unstoppable momentum |
| Usage | Finales, fast movements, toccata-like passages, Clementi |

```abc
X:40
T:T05 Perpetual Motion
M:4/4
L:1/16
K:C
V:RH clef=treble
!f! CDEF GABc defg abc'b | c'bag fedc BAGF EDCB, |
V:LH clef=bass
C,4 E,4 G,4 C4 | C4 A,4 F,4 G,4 |
```

### T06: Thick Chordal Texture (Beethoven Climactic)

| Attribute | Value |
|-----------|-------|
| Pattern | Full chords in both hands, maximum sonority within playability |
| Character | Monumental, thundering, climactic |
| Usage | Climaxes, codas, dramatic peaks; late Beethoven |

```abc
X:41
T:T06 Thick Chordal Climax
M:4/4
L:1/4
K:Cm
V:RH clef=treble
!fff! [EGc] [F_Ac] [EGc] [DG_B] | [EGc]4 |
V:LH clef=bass
[C,G,C] [F,_A,C] [C,G,C] [G,,G,_B,] | [C,G,C]4 |
```

---

## 4. Pattern Selection Guide

### By Emotional Context

| Emotional Need | Recommended Patterns |
|---------------|---------------------|
| Graceful elegance | A01, A02, M03, T01 |
| Building energy | A09, M01, M16, A12 |
| Calm resolution | A10, M02, A17, T04 |
| Driving force | A04, A07, A13, T05 |
| Lyrical singing | A01, A11, M10, T01 |
| Virtuosic display | M05-M07, M12, M13, M15 |
| Dramatic intensity | A07, A12, A13, T03, T06 |
| Pastoral tenderness | A16, A17, M03, T04 |
| Playful wit | A05, A08, M08, M09, T02 |
| Noble solemnity | A15, T04, T06 |

### By Formal Position

| Position in Form | Primary Patterns | Rationale |
|-----------------|-----------------|-----------|
| Theme statement (P) | A01, A08, T01 | Clear, singing, uncluttered |
| Transition (TR) | A09, M01, M16, A12 | Building energy, modulatory |
| Secondary theme (S) | A01, A11, M03, M10 | Lyrical contrast |
| Closing (C) | A07, M05, M12 | Cadential confirmation, brilliance |
| Development | M16-M18, A12, A13, T02 | Modulatory, fragmentary |
| Retransition | A14 (dom. pedal), A12 | Suspense, anticipation |
| Recapitulation | Vary from exposition | Freshness within return |
| Coda | A15, T04, T06, A14 | Summation, confirmation |
| Cadenza | M05-M07, M12, M13, M15 | Virtuosic, thematic recall |

### By Tempo

| Tempo Marking | Best Accompaniment | Best Melodic |
|--------------|-------------------|-------------|
| Adagio (40-65) | A01, A11, A14, A17 | M03, M05, M10, M14 |
| Andante (66-100) | A01, A02, A08, A11 | M03, M04, M08, M09 |
| Allegretto (100-120) | A01, A04, A08, A16 | M03, M08, M16 |
| Allegro (120-156) | A04, A07, A09, A12 | M01, M02, M12, M13 |
| Presto (168+) | A04, A05, A07 | M13, T05 |

### Combining Patterns Within a Section

| Bars | Pattern | Effect of Change |
|------|---------|-----------------|
| 1-4 | A01 (Alberti) | Establish texture |
| 5-8 | A08 (broken chord) | Slight rhythmic shift |
| 9-12 | A09 (ascending arp.) | Energy builds |
| 13-16 | A12 (tremolo) | Climactic tension |
| 17-20 | A01 return | Resolution, recapitulation of texture |

---

## 5. Period-Specific Usage Notes

### Early Classical / Galant (1750-1770)

- Favor A01, A04, A05 for accompaniment
- Ornaments measured and on the beat (M03, M08)
- Textures simpler: T01 dominates
- Short phrases (4 bars), symmetrical periods

### High Classical / Mozart-Haydn (1770-1800)

- Full accompaniment vocabulary available
- Dialogue between hands (T02) characteristic of Haydn
- Richer turns and appoggiaturas (M03, M09, M10) in Mozart
- Cadential trills with termination (M07) essential at PAC
- Walking bass (A06) in development sections

### Late Classical / Early Beethoven (1795-1810)

- A07, A12, A13 gain prominence — more driving energy
- T03 (unison octaves) becomes structural, not just dramatic
- T06 (thick chordal) emerges at climaxes
- Passage work (M12, M13) more extended and virtuosic
- Pedal points (A14) structurally important
- Sequence patterns (M16-M18) more harmonically adventurous
