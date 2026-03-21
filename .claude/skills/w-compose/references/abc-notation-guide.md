# ABC Notation Reference for w-compose

## Header Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `X:` | Yes | Reference number (unique per tune) | `X:1` |
| `T:` | Yes | Title | `T:Symphony No.1 - Mvt 1` |
| `C:` | No | Composer | `C:Wolfgang` |
| `M:` | Yes | Meter / time signature | `M:4/4`, `M:6/8`, `M:C` |
| `L:` | Yes | Default note length | `L:1/8` (eighth note default) |
| `Q:` | No | Tempo | `Q:1/4=120`, `Q:3/8=80` |
| `K:` | Yes | Key signature (last header) | `K:Cmaj`, `K:Amin`, `K:Bb` |
| `V:` | Multi-voice | Voice declaration | `V:Vln1 clef=treble name="Violin I"` |
| `I:` | No | Instruction directive | `I:linebreak $` |
| `%%` | No | Formatting directive | `%%staves {Vln1 Vln2}` |

**Key rule**: `K:` must be the LAST header field before music begins.

## Note Naming and Octaves

| Notation | Pitch | Octave |
|----------|-------|--------|
| `C D E F G A B` | Middle octave (C4-B4) | 4 |
| `c d e f g a b` | Octave above middle (C5-B5) | 5 |
| `c' d' e'` | Two octaves above middle (C6+) | 6 |
| `c'' d''` | Three octaves above (C7+) | 7 |
| `C, D, E,` | Octave below middle (C3-B3) | 3 |
| `C,, D,,` | Two below middle (C2-B2) | 2 |
| `C,,, D,,,` | Three below (C1-B1) | 1 |

**Critical**: Uppercase = octave 4, lowercase = octave 5. Comma lowers, apostrophe raises.

## Accidentals

| Symbol | Meaning | Example |
|--------|---------|---------|
| `^` | Sharp | `^F` = F# |
| `^^` | Double sharp | `^^F` = Fx |
| `_` | Flat | `_B` = Bb |
| `__` | Double flat | `__B` = Bbb |
| `=` | Natural (cancel) | `=F` = F natural |

**Scope**: An accidental applies to that note for the rest of the bar, like standard notation. Restate in subsequent bars.

## Durations

With `L:1/8` (recommended default):

| ABC | Duration | Name |
|-----|----------|------|
| `A` | 1/8 | Eighth note |
| `A2` | 2/8 = 1/4 | Quarter note |
| `A4` | 4/8 = 1/2 | Half note |
| `A8` | 8/8 = 1 | Whole note |
| `A/` or `A/2` | 1/16 | Sixteenth note |
| `A//` or `A/4` | 1/32 | Thirty-second note |
| `A3` | 3/8 | Dotted quarter |
| `A3/2` | 3/16 | Dotted eighth |
| `A7` | 7/8 | Double-dotted half |

**Dots**: Use multiplier notation. Dotted quarter = `A3` (when L:1/8). Dotted half = `A6`.

**Ties**: Use `-` between notes: `A4-|A4` ties a half note across a barline.

## Rests

| ABC | Duration (L:1/8) | Name |
|-----|-------------------|------|
| `z` | 1/8 | Eighth rest |
| `z2` | 1/4 | Quarter rest |
| `z4` | 1/2 | Half rest |
| `z8` | 1 | Whole rest |
| `Z` | Full bar | Whole-bar rest |
| `Z4` | 4 bars | Multi-bar rest |

## Barlines

| ABC | Meaning |
|-----|---------|
| `\|` | Regular barline |
| `\|\|` | Double barline |
| `\|]` | Final (thin-thick) barline |
| `[\|` | Thick-thin barline |
| `\|:` | Start repeat |
| `:\|` | End repeat |
| `::` | End + start repeat |
| `[1` | First volta |
| `[2` | Second volta |

### Repeat / Volta Example
```abc
|: CDEF | GABc | [1 cBAG :|[2 cdef ||
```

## Key Signatures and Modes

```
K:C       % C major
K:Am      % A minor (natural)
K:Bb      % Bb major
K:F#m     % F# minor
K:Dmix    % D mixolydian
K:Edor    % E dorian
K:Glyd    % G lydian
K:Aphr    % A phrygian
K:Cloc    % C locrian
```

Inline key change: `[K:Bb]` within music body.

## Time Signatures

```
M:4/4     M:C       % common time
M:3/4     M:6/8     M:2/4
M:2/2     M:C|      % cut time
M:5/4     M:7/8     M:12/8
```

Inline meter change: `[M:3/4]` within music body.

## Tuplets

| ABC | Meaning |
|-----|---------|
| `(3abc` | Triplet: 3 notes in time of 2 |
| `(3:2:3abc` | Same as above (explicit) |
| `(5abcde` | Quintuplet: 5 in time of 4 |
| `(7abcdefg` | Septuplet: 7 in time of 4 |
| `(2ab` | Duplet in compound time |

General form: `(p:q:r` where p notes in time of q, for r notes.

### Triplet Example
```abc
L:1/8
(3ABc (3ded (3cBA | (3:2:4 ABcd |
```

## Multi-Voice Format

### Voice Declaration (in header)
```abc
V:Vln1 clef=treble name="Violin I" sname="Vln.I"
V:Vln2 clef=treble name="Violin II" sname="Vln.II"
V:Vla clef=alto name="Viola" sname="Vla."
V:Vc clef=bass name="Violoncello" sname="Vc."
```

### Voice Content (in body)
```abc
[V:Vln1] e4 d4 | c8 |
[V:Vln2] c4 B4 | A8 |
[V:Vla] A4 G4 | E8 |
[V:Vc] A,4 G,4 | C,8 |
```

**Rule**: Each voice line must have matching bar counts. Every `|` must align across voices.

### Staves Directive
```
%%staves {Vln1 Vln2 Vla Vc}
```
Curly braces = brace (piano), square brackets `[Vln1 Vln2]` = bracket.

## Chords

Simultaneous notes: `[CEG]`, `[C2E2G2]` (all same duration), `[CEG]2` (chord with duration after).

**Do NOT use chords for separate orchestral voices.** Use `V:` declarations instead.

## Slurs, Grace Notes, Dynamics

| Feature | ABC Syntax | Example |
|---------|-----------|---------|
| Slur | `(notes)` | `(ABCD)` |
| Staccato | `!staccato!` or `.` before note | `!staccato!A` or `.A` |
| Accent | `!accent!` | `!accent!A` |
| Tenuto | `!tenuto!` | `!tenuto!A` |
| Fermata | `!fermata!` | `!fermata!A` |
| Grace note | `{g}A` | Single grace |
| Grace notes | `{gag}A` | Multiple graces |
| Acciaccatura | `{/g}A` | Slashed grace |
| Trill | `!trill!` | `!trill!A4` |
| Turn | `!turn!` | `!turn!A4` |
| Mordent | `!mordent!` | `!mordent!A4` |
| Piano | `!p!` | `!p! CDEF` |
| Forte | `!f!` | `!f! CDEF` |
| Pianissimo | `!pp!` | |
| Fortissimo | `!ff!` | |
| mf | `!mf!` | |
| mp | `!mp!` | |
| Crescendo start | `!crescendo(!` or `!<(!` | |
| Crescendo end | `!crescendo)!` or `!<)!` | |
| Diminuendo start | `!diminuendo(!` or `!>(!` | |
| Diminuendo end | `!diminuendo)!` or `!>)!` | |
| Down bow | `!downbow!` | |
| Up bow | `!upbow!` | |
| Pizzicato | `"pizz."` | Text annotation |

## Inline Field Changes

Any header field can be changed inline with `[field:value]`:
```abc
CDEF | [K:Bb] _BAGF | [M:3/4] cBA | [Q:1/4=80] EFG |
```

## Common LLM Pitfalls

| Pitfall | Wrong | Correct |
|---------|-------|---------|
| Bar length mismatch | 5 eighth notes in 4/4 bar | Must total exactly to meter |
| Octave confusion | `c` for cello melody | `C,` or `C,,` for cello range |
| Missing accidental restatement | Accidental lost after barline | Restate `^F` in each new bar |
| Tied note rhythm | `A-A` same bar (pointless) | Use `A2` instead; ties cross barlines |
| Voice count mismatch | 4 bars in Vln1, 3 in Vla | Every voice must have same bar count |
| Wrong L: math | `A2` = half note always | Depends on `L:` setting |
| Chord vs voice | `[CEG]` for orchestra | Use `V:` per instrument |
| Missing K: at end | K: before M: | K: must be last header field |
| Unbalanced slurs | `(ABC` missing `)` | `(ABC)` |
| Grace note placement | `A{g}` after note | `{g}A` before note |
| Inline fields in header | `[M:3/4]` in header area | `M:3/4` plain in header |
| Rest notation | `r` for rest | `z` for rest |
| Tuplet note count | `(3AB` only 2 notes | `(3ABC` needs 3 notes |
| Barline before first note | `| CDEF |` leading bar | `CDEF |` no leading barline |

## Quick Reference: Complete Minimal Example

```abc
X:1
T:Example Piece
C:Wolfgang
M:4/4
L:1/8
Q:1/4=120
V:Mel clef=treble name="Melody"
V:Bass clef=bass name="Bass"
K:C
%
[V:Mel] !mf! (CDEF) GABc | !f! c'2B2 A2G2 | !diminuendo(! F2E2 D2C2 !diminuendo)! |]
[V:Bass] C,4 E,4 | F,4 G,4 | A,,4 G,,2 C,2 |]
```
