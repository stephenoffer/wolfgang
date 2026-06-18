# Melodic Construction

> **Scope:** Technical construction — phrase structure, intervals, contour shapes, period-specific norms. For artistic intent (why themes work, what makes them memorable), see `melody-craft.md`.
>
> These are common-practice guidelines for building compelling melodies, not absolute rules. Different periods and styles have their own melodic norms — consult period-specific context files.

## Phrase Structure

### Basic Units

| Unit | Typical length | Function |
|---|---|---|
| Cell | 2-3 notes | Smallest recognizable unit |
| Motif | 1-2 bars | Characteristic rhythm + interval pattern |
| Phrase | 4 bars | Complete musical thought, ends with cadence |
| Period | 8 bars (4+4) | Two complementary phrases |
| Double period | 16 bars (4+4+4+4) | Extended period structure |
| Section | Multiple periods | Structural unit (exposition, development, etc.) |

### Period Structure (Antecedent-Consequent)

| Part | Bars | Cadence | Function |
|---|---|---|---|
| Antecedent | 4 | Half cadence (HC) or IAC | Question — open, incomplete |
| Consequent | 4 | Perfect authentic cadence (PAC) | Answer — closed, complete |

```abc
X:1
T:Period Structure (Question and Answer)
M:4/4
L:1/8
K:C
%% Antecedent (ends on HC - incomplete)
C2E2 G2c2 | B2A2 G4 |
%% Consequent (ends on PAC - complete)
C2E2 G2c2 | d2B2 c4 |
```

### Sentence Structure (Satz)

| Part | Bars | Content |
|---|---|---|
| Presentation: basic idea | 2 | Motif stated |
| Presentation: repetition | 2 | Motif repeated (same pitch or transposed) |
| Continuation | 2 | Fragmentation, acceleration, sequence |
| Cadential | 2 | Drive to cadence |

```abc
X:2
T:Sentence Structure (2+2+4)
M:4/4
L:1/8
K:G
%% Basic idea (2 bars)
B2d2 e2d2 | c2B2 A4 |
%% Repetition (2 bars, transposed up)
c2e2 f2e2 | d2c2 B4 |
%% Continuation + cadence (4 bars - fragmented, accelerating)
d2e2 d2c2 | B2c2 B2A2 | G2A2 B2A2 | G8 |
```

### Irregular Phrase Lengths

| Length | How it occurs | Effect |
|---|---|---|
| 3 bars | Compression, urgency | Breathless |
| 5 bars | Extension (4+1 tag) or asymmetry | Expansive |
| 6 bars | 4+2 extension or 3+3 symmetry | Broadened |
| 7 bars | 4+3 or 3+4 | Unexpected, off-balance |

### Phrase Elision
Last bar of one phrase = first bar of the next. Creates continuous flow (characteristic of Romantic and Late Romantic styles).

## Melodic Contour

| Contour | Shape | Emotional association | Best for |
|---|---|---|---|
| Arch (rise-fall) | ∧ | Completion, singing quality | Lyrical themes |
| Ascending | / | Aspiration, tension, hope | Building passages |
| Descending | \ | Resolution, grief, relaxation | Closing phrases |
| Wave | ∼ | Lyrical, flowing | Sustained melodies |
| Static/plateau | — | Contemplation, suspense | Recitative, tension |
| Inverted arch | ∨ | Settling then rising | Surprise, rebound |

### Climax Placement

| Scale | Typical placement | Notes |
|---|---|---|
| Within a phrase | Near the end (~bar 3 of 4) | Penultimate bar |
| Within a melody | ~60-75% through | Near the golden ratio |
| Within a section | After development/buildup | Earned by preparation |
| Multiple levels | Local (phrase), regional (period), global (section) | Each level peaks higher |

```abc
X:3
T:Arch Contour with Climax at ~65%
M:4/4
L:1/8
K:D
!p! D2F2 A2d2 | e2f2 g2a2 | !f! b4 a2g2 | !p! f2e2 d4 |
%% Climax on 'b' at bar 3 beat 1 (~65% through the phrase)
```

## Sequence Types

| Type | Method | Character | Typical repetitions |
|---|---|---|---|
| Real | Exact transposition | Bold, modulating | 2-3 |
| Tonal | Adjusted to stay in key | Smooth, diatonic | 2-3 |
| Modified | Contour preserved, details varied | Natural, flexible | 2-4 |
| Ascending | Pattern moves upward | Intensification, building | 2-3 (rarely 4) |
| Descending | Pattern moves downward | Relaxation, unwinding | 2-3 |

```abc
X:4
T:Tonal Sequence (descending by step)
M:4/4
L:1/8
K:C
%% Pattern stated
c2B2 A2G2 |
%% Repeated a step lower (tonal - stays in key)
B2A2 G2F2 |
%% Again
A2G2 F2E2 | C8 |
```

### Sequence Guidelines
- Three repetitions is typical for classical sequences — four can feel mechanical in that context. However, more repetitions are characteristic of Baroque sequences (circle-of-fifths chains), minimalist works, and Beethoven's development sections where insistence is the point.
- Consider varying dynamics across repetitions (typically crescendo for ascending, diminuendo for descending)
- Consider changing one element in the final repetition (rhythm, harmony, or ornament)

## Melodic Development Techniques

| Technique | Description | ABC Example |
|---|---|---|
| Fragmentation | Use only the head motif (first 2-4 notes) | `C2E2` from `C2E2G2c2` |
| Augmentation | Double note values | `C4E4G4c4` from `C2E2G2c2` |
| Diminution | Halve note values | `CEGC` from `C2E2G2c2` |
| Inversion | Flip intervals (up→down, down→up) | `c2A2F2C2` from `C2E2G2c2` |
| Retrograde | Play backwards | `c2G2E2C2` from `C2E2G2c2` |
| Sequence | Transpose pattern up or down | See above |
| Interpolation | Insert notes within existing melody | `C2D2E2F2G2A2c2` |
| Extension | Add bars to phrase end | `c2B2A2G2 | G8` (tag) |
| Compression | Remove notes, shorten phrase | `C2G2 c4` from full phrase |
| Ornamentation | Add grace notes, turns, trills | `{B}c2E2 {F}G2c2` |

```abc
X:5
T:Development Techniques Applied to a Motif
M:4/4
L:1/8
K:C
%% Original motif
C2E2 G2c2 |
%% Inversion
c2A2 F2C2 |
%% Fragmentation (head only)
C2E2 z2 C2 | E2 z2 C2E2 |
%% Augmentation
C4 E4 | G4 c4 |
```

## Intervallic Character

| Interval | Melodic character | Best for |
|---|---|---|
| m2 (semitone) | Pain, tension, sighing | Lament, chromaticism |
| M2 (whole tone) | Neutral, stepwise | Scalar motion, folk melody |
| m3 (minor 3rd) | Gentle, minor quality | Lyrical minor themes |
| M3 (major 3rd) | Warm, bright | Major themes, joy |
| P4 (perfect 4th) | Open, call-like | Fanfare, horn calls |
| P5 (perfect 5th) | Stable, heroic | Opening gestures, strength |
| m6 (minor 6th) | Yearning, expressive | Romantic leaps |
| M6 (major 6th) | Warm yearning | Love themes, lyricism |
| P8 (octave) | Power, drama | Dramatic openings |
| Tritone | Tension, evil, uncertainty | Dramatic, unsettled themes |

## Period-Specific Melodic Norms

| Period | Melodic approach | Phrase structure | Characteristic |
|---|---|---|---|
| Baroque | Fortspinnung (spinning-out), sequence-driven | Irregular, continuous | Motor rhythm, sequence chains |
| Classical | Balanced periods, periodic structure | Regular 4+4, 8+8 | Symmetry, antecedent-consequent |
| Romantic | Long lyrical lines, irregular phrases | 4+5, 4+6, elision | Singing quality, wide range |
| Impressionist | Fragmentary, coloristic | Brief, floating | Pentatonic, whole-tone |
| Modern | Angular, wide intervals | Irregular, pointillistic | Dissonant leaps, unpredictable |
| Minimalist | Repetitive, gradually changing | Process-based, additive | Small cells, phasing |

```abc
X:6
T:Baroque Fortspinnung vs Classical Period
M:4/4
L:1/8
K:C
%% Baroque: spinning-out (no regular phrase boundary)
C2E2G2c2 | B2c2d2e2 | d2c2B2A2 | G2A2B2c2 | d8 |
%% Classical: balanced period (clear 4+4)
C2E2 G2c2 | B2A2 G4 | C2E2 G2c2 | d2B2 c4 |
```

## Melody + Harmony Interaction

### Strong-Beat Melody Notes
- Melody notes on strong beats are typically chord tones
- Non-chord tones (passing, neighbor, suspension, appoggiatura) resolve by step to chord tones
- Appoggiaturas on strong beats create expressive tension — characteristic of Romantic style

### Melodic Pacing
| Emotional state | Note density | Register | Intervals |
|---|---|---|---|
| Calm, reflective | Slower (quarters, halves) | Middle | Steps, small leaps |
| Building tension | Accelerating | Rising | Growing intervals |
| Climactic | Fastest or sustained peak | Highest point | Large leaps or sustained high notes |
| Resolution | Decelerating | Descending | Steps, settling |

```abc
X:7
T:Melodic Pacing (calm → build → climax → resolve)
M:4/4
L:1/8
K:D
%% Calm
!p! D4 F4 | A4 d4 |
%% Building
!mf! d2e2 f2g2 | a2b2 c'2d'2 |
%% Climax
!ff! d'8 |
%% Resolution
!p! c'2b2 a2f2 | d8 |
```

## Constructing a Theme: Step-by-Step

1. **Choose a contour** — arch, ascending, wave, etc.
2. **Select a characteristic interval** — this becomes the theme's "fingerprint"
3. **Set the rhythm** — a distinctive rhythmic pattern makes themes memorable
4. **Write the antecedent** — 4 bars ending on HC (open)
5. **Write the consequent** — 4 bars ending on PAC (closed)
6. **Test singability** — if you can hum it, it works
7. **Check against harmony** — strong-beat notes should fit the chord progression
8. **Add ornamentation** — grace notes, turns at cadences, appoggiaturas at peaks
