# Philip Glass — Melodic Style

## Core Principle: Pattern Over Melody

Glass does not write melodies in the Romantic sense — singable, arching, emotionally shaped lines. Instead, his "melodies" are arpeggiated patterns that outline chords. The pattern IS the melody; the melody IS the harmony.

## Melodic Types

| Type | Description | Works |
|------|-------------|-------|
| Arpeggiated pattern | Chord tones cycled in fixed order | *Glassworks*, *Einstein on the Beach* |
| Additive melody | Short cell + one note added each iteration | *Music in Fifths*, early works |
| Scalar melody | Stepwise lines (more melodic, later period) | *Metamorphosis*, *The Hours* |
| Vocal melody | Singable lines for opera/film | *Satyagraha*, *Akhnaten* |
| Resultant melody | Melody that "emerges" from interlocking patterns | *Einstein on the Beach* |

## The Arpeggiated Pattern

| Element | Rule |
|---------|------|
| Pitches | Only chord tones (root, 3rd, 5th, octave) |
| Rhythm | Constant eighth notes or sixteenth notes |
| Direction | Usually ascending, cycling back to start |
| Duration | 4–8 notes per cycle |
| Variation | None within a section; pattern repeats exactly |

```abc
X:1
T:Arpeggiated Pattern — The Core Glass Melody
M:4/4
L:1/8
K:Am
ACEA CEAC | ACEA CEAC | ACEA CEAC | ACEA CEAC |
% This IS the melody. The arpeggio IS the tune. 16 bars of this creates the Glass effect.
```

## Additive/Subtractive Process

| Step | Cell | Notes | Repetitions |
|------|------|-------|-------------|
| 1 | E-G-A | 3 | 4–8 times |
| 2 | E-G-A-B | 4 | 4–8 times |
| 3 | E-G-A-B-C | 5 | 4–8 times |
| 4 | E-G-A-B-C-D | 6 | 4–8 times |
| 5 | E-G-A-B-C-D-E | 7 | 4–8 times |
| (reverse) | E-G-A-B-C-D | 6 | 4–8 times |
| (reverse) | E-G-A-B-C | 5 | 4–8 times |

```abc
X:2
T:Additive Melodic Process
M:6/8
L:1/8
K:C
%% 3-note cell
EGA EGA | EGA EGA |
%% 4-note cell (+B)
EGAB EGAB | EGAB EGAB |
%% 5-note cell (+C)
EGABC z | EGABC z |
% Each step adds one note. The growth IS the melodic content.
```

## Scalar Melody (Later Period)

In *Metamorphosis* and film scores, Glass writes more traditional stepwise melodies — but still within a modal, non-developmental framework:

| Feature | Description |
|---------|-------------|
| Motion | Mostly stepwise, occasional 3rd |
| Range | One octave or less |
| Shape | Gentle arch or descent |
| Rhythm | Steady, usually in eighth notes |
| Development | None — melody repeats without variation |
| Harmonization | Simple triadic arpeggiation beneath |

```abc
X:3
T:Scalar Melody — Metamorphosis Style (piano)
M:4/4
L:1/8
K:Am
%%staves {1 2}
V:1 name="RH melody"
A2 B2 c2 B2 | A2 G2 F2 E2 | A2 B2 c2 d2 | c2 B2 A4 |
V:2 name="LH arpeggio"
ACEA CEAC | ACEA CEAC | ACEA CEAC | ACEA CEAC |
% The melody arches gently above relentless arpeggiation
```

## Vocal Melody (Opera)

| Feature | *Einstein on the Beach* | *Satyagraha* | *Akhnaten* |
|---------|------------------------|-------------|-----------|
| Text | Numbers, solfege | Sanskrit (Bhagavad Gita) | Egyptian, Akkadian |
| Melodic type | Solfege patterns, additive | Lyrical arching phrases | Most tonal, hymn-like |
| Range | Limited (one octave) | Moderate | Wide for countertenor |
| Rhythm | Additive, asymmetric | Regular, flowing | Regular, devotional |

```abc
X:4
T:Opera Vocal Style — Satyagraha-like Lyrical Line
M:4/4
L:1/4
K:D
V:1 name="Soprano"
D F A F | D E F A | d c B A | F E D2 |
% More lyrical than the keyboard works — but still modal, still cycling
```

## Rhythmic Treatment

| Period | Rhythmic Character | Note Values |
|--------|-------------------|-------------|
| Early (1968–76) | Absolutely constant; no variation | All eighths or all sixteenths |
| Opera (1976–84) | Constant with grouped subdivisions (3+3+4, etc.) | Eighths grouped additively |
| Middle (1984–2000) | Mostly constant; rare rubato in slow works | Eighths with occasional quarters |
| Late (2000+) | More rhythmic variety; orchestral needs | Mixed values but still pulse-driven |

## Phrase Structure

| Structure | Description | Duration |
|-----------|-------------|----------|
| Cell | The smallest repeating unit (3–8 notes) | 1–2 beats |
| Pattern | Cell repeated 4–8 times | 2–8 bars |
| Section | One chord's worth of pattern repetition | 4–16 bars |
| Cycle | Complete sequence of all chords | 16–64 bars |
| Movement | Multiple cycles with additive/subtractive changes | 3–15 minutes |

## Melodic Anti-Patterns

| Avoid | Why |
|-------|-----|
| Large leaps (6th, 7th, octave) | Glass melodies move by step or 3rd |
| Melodic development | Glass repeats, not develops; no fragmentation, inversion, augmentation |
| Rubato or rhythmic freedom | The mechanical regularity is the aesthetic |
| Ornaments (trills, turns, grace notes) | No decoration; the bare pattern is sufficient |
| Countermelody | Glass writes one layer at a time; no independent counterpoint |
| Climactic high notes | No peaks in the Romantic sense; the melody cycles at the same level |

```abc
X:5
T:What Glass Does NOT Sound Like (avoid this)
M:4/4
L:1/8
K:Am
%% WRONG: dramatic leaps, varied rhythm, development
A2 e2 c'2 A2 | E,4 G,B,D | z2 ^ce ^gbe' | A,,,8 |
% This has leaps, chromaticism, drama — NOT Glass
```

## References
- Glass, Philip. *Words Without Music: A Memoir*, 2015
- Potter, Keith. *Four Musical Minimalists*, 2000
- Schwarz, K. Robert. *Minimalists*, 1996
