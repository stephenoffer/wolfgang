# Ornamentation & Embellishment Reference — Catalog & Syntax

> This file is the ornament **CATALOG**: what ornaments exist, how to write them in ABC, period conventions, cadential formulas, and non-chord tone vocabulary. For **WHY and WHEN** to use ornaments (decision framework, phrase integration, natural sounds, emotional mapping, ornament psychology), see [`ornament-intent.md`](ornament-intent.md).

---

## 1. Period-Specific Ornament Conventions

### Ornament Execution by Period

| Period | Trill start | Grace note timing | Standard ornaments | Characteristic pattern |
|---|---|---|---|---|
| Baroque (1600-1750) | Upper note, on beat | On beat (appoggiatura style) | Trill, mordent, turn, slide, Schleifer | Sequential 16th groups, chain trills |
| Classical (1750-1820) | Upper note (early) / main note (late) | On beat (Mozart) / before beat (late) | Trill, turn, acciaccatura, Doppelschlag | Measured ornaments, scalar runs |
| Romantic (1820-1890) | Main note (default) | Before the beat | Written-out turns, arpeggiated grace | Filigree groups, chromatic neighbor clusters |
| Late Romantic (1880-1920) | Main note | Before the beat | Written-out ornaments, tremolo | Wide-span arpeggiation, chromatic passing |
| Impressionist (1890-1930) | Main note | Before the beat | Whole-tone runs, grace-note clusters | Parallel chord streams, modal scales |
| Modern (1900+) | Context-dependent | Context-dependent | Extended techniques, micro-ornaments | Irregular groupings, klangfarben |

### What to Typically AVOID by Period

| Period | Generally avoid |
|---|---|
| Baroque | Unornamented slow movements; grace notes before the beat; empty repeated notes |
| Classical | Excessive ornamentation in Allegro; unmeasured trills; rubato-style grace notes |
| Romantic | Mechanical trills without expressive shaping; Baroque-style mordents; sparse textures |
| Late Romantic | Simple Alberti bass; thin textures; undecorated octave passages |
| Impressionist | Heavy Germanic ornaments (mordents, turns); thick chromatic passing tones |
| Modern | Period-style trills unless quoting; conventional grace notes without purpose |

### Trill Execution Reference

| Context | Start | Realization (on note D, trill with E) | ABC |
|---|---|---|---|
| Baroque standard | Upper note, on beat | E-D-E-D-E-D-E-D | `E/D/E/D/E/D/E/D/` |
| Baroque with prefix | Ascending from below | C-D-E-D-E-D-E-D | `C/D/E/D/E/D/E/D/` |
| Classical (Mozart) | Upper note, on beat, measured | E-D-E-D E-D-E-D | `E/D/E/D/ E/D/E/D/` |
| Classical (late Beethoven) | Main note | D-E-D-E D-E-D-E | `D/E/D/E/ D/E/D/E/` |
| Romantic | Main note, accelerating | D-E, D-E-D-E, D-E-D-E-D-E | `D/E/ D/E/D/E/ D/E/D/E/D/E/` |
| Trill with suffix (any period) | Per period | ...D-E-D-C#-D (turn ending) | `...D/E/D/^C/D4` |

### Genre-Specific Ornament Vocabulary

| Genre | Signature Ornaments | Characteristic Technique | What Makes It Distinctive |
|---|---|---|---|
| Baroque | Chain trills, mordents on stressed beats, sequential 16th patterns, slides | Ornaments are integral to melody — omitting them leaves the line incomplete | Fixed ornament tables (agréments); performer adds what composer indicates by symbol |
| Classical | Measured trills with suffix, turns (Doppelschlag), acciaccaturas, Alberti + ornamental melody | Every ornament fits the meter precisely — nothing is rubato or free | Opera-derived: appoggiaturas from arias, cadential trills from recitative endings |
| Romantic | Written-out filigree, chromatic neighbor groups, arpeggiated grace-note flourishes, cadenza passages | Ornaments are THE melody, not added to it — Chopin's filigree IS the content | Bel canto vocal technique transferred to instruments; rubato within ornaments |
| Late Romantic | Wide-span arpeggiation as texture, chromatic passing tone cascades, tremolo as sustained color | Ornaments create orchestral fullness — filling the entire register from bass to treble | Scale of ornament: Rachmaninoff's bell sonority spans 4+ octaves |
| Impressionist | Whole-tone grace-note fragments, pentatonic ornamental runs, grace-note clusters as harmonic color | Ornaments blur into atmosphere — the line between decoration and structure dissolves | Grace notes are harmonic shimmer, not melodic inflection |
| Modern | Extended techniques (flutter-tongue, harmonics, multiphonics), rhythmically irregular ornamental cells | Ornament as sound event — timbre and texture matter more than pitch pattern | Each ornament is a unique sonic gesture, not drawn from a fixed vocabulary |

---

## 2. Figuration Patterns

**Source chord: C major (C E G). All patterns show one bar of figuration.**

| Pattern | ABC | Suits |
|---|---|---|
| Alberti bass | `C/E/G/E/ C/E/G/E/` | Classical keyboard, Andante-Allegro |
| Wide arpeggiation | `C,/G,/C/E/ G/C/E/G/` | Romantic piano, Andante-Moderato |
| Scalar fill | `C/D/E/F/ G/A/B/c/` | Classical runs, Allegro transitions |
| Turn-based figuration | `C/D/C/B,/ C/E/D/C/` | Baroque keyboard, Andante |
| Broken octave | `C,/C/C,/C/ C,/C/C,/C/` | Scarlatti, fast movements |
| Chordal pulse + passing | `[CE]2[DF]2 [EG]2[FA]2` | Chorale texture, Andante |
| Tremolo | `C/G/C/G/ C/G/C/G/` | Beethoven, dramatic Allegro |
| Wide-span Rachmaninoff | `C,,/G,/C/E/ G/c/e/g/` | Late Romantic piano, Moderato |
| Bass-chord waltz | `C,,2 [G,CE]2 [G,CE]2` | Waltz/oom-pah, 3/4 Allegretto |
| Murky bass | `C,/G,/C,/G,/ C,/G,/C,/G,/` | Galant style, Allegro |

### Full Progression Figurated: I-IV-V-I in C

**Alberti bass realization:**
```abc
X:7
T:Alberti Bass - I IV V I
M:4/4
L:1/8
K:C
V:1 clef=treble
[EG]4 [EG]4 | [FA]4 [FA]4 | [DF]4 [DF]4 | [EG]4 [EG]4 |
V:2 clef=bass
C,E,G,E, C,E,G,E, | F,A,C,A, F,A,C,A, | G,B,D,B, G,B,D,B, | C,E,G,E, C,E,G,E, |
```

**Wide arpeggiation realization:**
```abc
X:8
T:Wide Arpeggiation - I IV V I
M:4/4
L:1/16
K:C
V:1 clef=treble
E2G2c2e2 d2c2B2A2 | F2A2c2f2 e2d2c2B2 | D2G2B2d2 c2B2A2G2 | E2G2c2e2 c4 z4 |
V:2 clef=bass
C,,2G,,2C,2E,2 G,4 z4 | F,,2C,2F,2A,2 C4 z4 | G,,2D,2G,2B,2 D4 z4 | C,,2G,,2C,2E,2 C,4 z4 |
```

**Tremolo/dramatic realization (Beethoven style):**
```abc
X:9
T:Tremolo Realization - I IV V I
M:4/4
L:1/16
K:C
V:1 clef=treble
CEGECEGE CEGECEGE | CFA,CFAC FA,CFA,CF | DB,GDB,GD B,GDB,GD | CEGECEGE C4 z4 |
V:2 clef=bass
C,,2C,,2C,,2C,,2 C,,2C,,2C,,2C,,2 | F,,2F,,2F,,2F,,2 F,,2F,,2F,,2F,,2 | G,,2G,,2G,,2G,,2 G,,2G,,2G,,2G,,2 | C,,2C,,2C,,2C,,2 C,,4 z4 |
```

---

## 3. Cadential Ornamentation

### Standard Cadential Formulas

| Cadence type | Ornament | Where | Period |
|---|---|---|---|
| PAC | Trill on supertonic (2-1) | Penultimate note, upper voice | All |
| PAC | Turn on leading tone | Before resolution to tonic | Classical |
| PAC | Appoggiatura (4-3) over V | Strong beat before resolution | Baroque, Classical |
| HC | Grace note into dominant | Approach by step from above | All |
| Deceptive | Ornamental escape after V | Soprano leaps up instead of resolving | Romantic |

### ABC Examples -- Cadential Ornaments

**Trill on supertonic before PAC (Classical):**
```abc
X:10
T:Cadential Trill (PAC in C)
M:4/4
L:1/16
K:C
V:1 clef=treble
G2A2B2c2 DEDE DEDC | C8 z8 |
V:2 clef=bass
E,2F,2G,2E,2 G,,4 G,,4 | C,,8 z8 |
```

**Turn on leading tone (Classical):**
```abc
X:11
T:Turn on Leading Tone
M:4/4
L:1/16
K:C
G4 F4 E4 D4 | BcBA G4 F4 E4 | C8 z8 |
```

**Grace notes approaching final (Romantic):**
```abc
X:12
T:Grace Note Cadential Approach
M:4/4
L:1/4
K:C
G A {Bc} B {AB}c | {d}c4 |
```

**Cadenza-like flourish before final cadence (Romantic):**
```abc
X:13
T:Cadenza Flourish Before PAC
M:4/4
L:1/32
K:C
V:1 clef=treble
CDEFGAB^c defgabc'd' | c'8 z8 |
V:2 clef=bass
"I64"C,,4 z4 "V7"G,,4 z4 | "I"C,,8 z8 |
```

**Cadential comparison -- Classical vs Romantic PAC:**
```abc
X:14
T:Classical PAC (measured trill)
M:4/4
L:1/16
K:C
"I64"E4G4 "V7"DFDF DFD2 | "I"C8 z8 |
```
```abc
X:15
T:Romantic PAC (written-out flourish)
M:4/4
L:1/32
K:C
"I64"E4G4c4e4 "V7"fede dcBA GFED CB,A,G, | "I"C,8 z24 |
```

---

## 4. Non-Chord Tone Vocabulary in Practice

### Passing Tone (PT) -- unaccented and accented

```abc
X:16
T:Passing Tones in Context
M:4/4
L:1/8
K:C
% Unaccented PT: D between C and E (weak beat)
"I"C2 DE E2 GF | "V7"F2 ED D2 B,2 | "I"C4 z4 |
% Accented PT: D falls on strong beat
"I"C2 D2 E2 G2 |
```

### Neighbor Tone (NT) -- upper, lower, chromatic

```abc
X:17
T:Neighbor Tones
M:4/4
L:1/8
K:C
% Upper neighbor (diatonic)
"I"E2 FE E2 FE | "I"G2 AG G2 AG |
% Lower neighbor (chromatic)
"I"E2 ^DE E2 ^DE | "I"G2 ^FG G2 ^FG |
```

### Appoggiatura (APP) -- lean and resolve

```abc
X:18
T:Appoggiatura in Context
M:4/4
L:1/4
K:C
% F leans on E (resolves down by step over I chord)
"I"C F E G | "IV"A B A F | "V"B c B G | "I"c4 |
```

### Suspension Chain (SUS) -- 4-3 chain

```abc
X:19
T:4-3 Suspension Chain
M:4/4
L:1/2
K:C
V:1 clef=treble
% Prepare-suspend-resolve pattern chained
C F | E A | G c | B c |
V:2 clef=bass
"I"C, "IV"F, | "I6"E, "ii"D, | "I64"C, "V"G, | "V7"G, "I"C, |
```

### Escape Tone (ET) -- step to, leap away

```abc
X:20
T:Escape Tone
M:4/4
L:1/8
K:C
% Step up to D, leap down to B (escape tone D)
"I"C2 DE DB, C2 | E2 FG FD E2 |
```

### Anticipation -- arrive early

```abc
X:21
T:Anticipation
M:4/4
L:1/8
K:C
% C arrives one 8th early before I chord resolves
"V7"B2 D2 FD "I"CC | C6 z2 |
```

### Pedal Point -- bass holds through changes

```abc
X:22
T:Dominant Pedal Point
M:4/4
L:1/4
K:C
V:1 clef=treble
[EG] [FA] [DF] [EG] | [^FG] [EG] [DF] [B,D] | [CE]4 |
V:2 clef=bass
% G pedal holds through I, IV, ii, I6, V/V, I6, ii, V resolutions
G,,4 | G,,4 | C,,4 |
```

### Changing Tones (Double Neighbor)

```abc
X:23
T:Changing Tones (Double Neighbor)
M:4/4
L:1/8
K:C
% E -> F(upper) -> D(lower) -> E (return)
"I"E2 FD E2 z2 | G2 AF G2 z2 |
```

---

## 5. Variety & Rotation Checklist

> These are sensible defaults, not hard limits. Many great pieces sustain a single pattern well beyond these numbers when it serves the compositional intent — Chopin's Prelude No. 15 repeats one note for 80+ bars, Ravel's *Boléro* sustains its ostinato throughout, Beethoven's development sections often maintain a single texture for extended passages.

| Guideline | Default threshold | Suggested action |
|---|---|---|
| Same figuration pattern | ~4 bars | Consider switching to contrasting pattern (e.g., Alberti → arpeggiation) |
| Same rhythmic subdivision | ~8 bars | Consider changing (8ths → 16ths, or triplets → straight, etc.) |
| Same register | ~8 bars | Consider shifting texture up/down by octave, or redistribute voices |
| Predictable pattern | ~16 bars | Consider inserting one unexpected element: chromatic PT, deceptive cadence, rhythmic break |
| Static bass pattern | ~4 bars | Consider varying bass rhythm or inverting pattern |
| Unvaried dynamics | ~8 bars | Consider introducing hairpin or terrace dynamic change |

### Embellishment Density by Tempo

| Tempo | Density | Note values for ornaments | Approach |
|---|---|---|---|
| Adagio (66-76) | High | 32nds, sextuplets | Filigree; fills silences between long melody notes |
| Andante (76-108) | Medium-high | 16ths, triplet 16ths | Flowing; passing tones + occasional turn/trill |
| Moderato (108-120) | Medium | 16ths, 8th triplets | Selective; ornament peaks and cadences only |
| Allegro (120-156) | Low-medium | 8ths, occasional 16ths | Structural; scale runs at transitions, trills at cadences |
| Presto (176+) | Minimal | 8ths only | Notes are already fast; ornament by harmonic surprise instead |

### Figuration Rotation Template (16-bar block)

| Bars | Pattern | Purpose |
|---|---|---|
| 1-4 | Alberti or arpeggiation | Establish texture |
| 5-6 | Scalar passage / sequence | Build energy |
| 7-8 | Chordal / reduced texture | Contrast, breathe |
| 9-12 | New figuration (tremolo, wide-span) | Renew interest |
| 13-14 | Return of opening pattern (varied) | Unity |
| 15-16 | Cadential ornament + resolution | Close phrase group |
