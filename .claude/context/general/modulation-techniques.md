# Modulation Techniques

> These are common-practice guidelines for moving between keys. Different periods favor different modulation types — consult period-specific context files.

## Modulation Types

| Type | Mechanism | Smoothness | Best for |
|---|---|---|---|
| Pivot chord | Shared chord reinterpreted in new key | Very smooth | Classical transitions, expositions |
| Direct (phrase) | New key starts at phrase boundary, no preparation | Dramatic | Romantic surprises, section boundaries |
| Chromatic | Chromatic voice-leading slides into new key | Expressive | Romantic intensification |
| Enharmonic | Reinterpret a chord (Ger+6 = V7, dim7 respelling) | Distant keys | Late Romantic, distant modulation |
| Common-tone | Single note held while harmony shifts around it | Mystical | Impressionist, magical moments |
| Sequential | Sequence naturally carries harmony to new key | Natural | Development sections, transitions |

---

## Pivot Chord Modulation

The smoothest modulation: a chord that belongs to both the old and new key serves as a bridge.

### Common Pivot Chords (from C major)

| To key | Pivot chord | In C major | In new key |
|---|---|---|---|
| G major | I = IV | C major | IV of G |
| A minor | I = III | C major | III of Am |
| F major | V = I | G major | I → reinterpret as V of F... or I=V of F |
| D minor | ii = i | D minor | Same chord |
| E minor | vi = iv | Am | iv of Em... or iii = vi |

```abc
X:1
T:Pivot Chord Modulation (C major → G major)
M:4/4
L:1/4
K:C
%% In C major
[CE] [DF] [EG] [FA] |
%% Pivot: Am (= ii in G)
[Ac] [Bd] |
%% Now in G major
[Bd] [ce] | [Bd]4 |
w: C:I ii iii IV vi(=ii/G) G:iii G:V7 I
```

## Direct (Phrase) Modulation

New key begins at a phrase boundary with no harmonic preparation. Characteristically dramatic.

```abc
X:2
T:Direct Modulation (C major → Db major, no preparation)
M:4/4
L:1/4
K:C
[CEG] [DFA] [EGB] [CEG] |
[K:Db] [_D_FA] [_EG_B] [F_Ac] [_D_FA] |
w: C:I ii iii I Db:I ii iii I
```

## Chromatic Modulation

Voice-leading by semitone into the new key. The chromatic motion itself creates the bridge.

```abc
X:3
T:Chromatic Modulation (C major → E major via chromatic bass)
M:4/4
L:1/4
K:C
[CEG] [CE^G] | [^CE^G] [E^G=B] |
w: C C+ C#dim(passing) E:I
%% Bass: C → C → C# → E (chromatic ascent)
```

## Enharmonic Modulation

### Via German Augmented 6th = Dominant 7th

| In old key | Chord | Respelled as | In new key |
|---|---|---|---|
| C: Ger+6 | Ab-C-Eb-F# | Ab-C-Eb-Gb = V7 of Db | Db major |
| Am: Ger+6 | F-A-C-D# | F-A-C-Eb = V7 of Bb | Bb major |

```abc
X:4
T:Enharmonic Modulation via Ger+6 = V7
M:4/4
L:1/2
K:C
%% Ger+6 in C (Ab-C-Eb-F#)
[_A,C_E^F] |
%% Reinterpreted as V7 of Db (Ab-C-Eb-Gb)
[K:Db] [_A,C_E_G] [_DFA] |
w: C:Ger+6 Db:V7 Db:I
```

### Via Diminished 7th (4 possible resolutions)

Any dim7 chord can resolve to 4 different keys by respelling:

| dim7 chord | Resolves as viio7 of... | Keys reached |
|---|---|---|
| B-D-F-Ab | C, Eb, F#, A | 4 equidistant keys |
| C#-E-G-Bb | D, F, Ab, B | 4 equidistant keys |
| D-F-Ab-Cb | Eb, Gb, A, C | 4 equidistant keys |

```abc
X:5
T:Dim7 Resolving to 4 Different Keys
M:4/4
L:1/2
K:C
%% Same dim7 → different resolutions
[=BDF_A] [CEGc] | [=BDF_A] [_E,_EG_B] | [=BDF_A] [^F,^FA^c] | [=BDF_A] [A,CEA] |
w: viio7→C viio7→Eb viio7→F# viio7→A
```

## Common-Tone Modulation

One note is sustained while the harmony shifts around it. Characteristically mystical or magical.

```abc
X:6
T:Common-Tone Modulation (C held, C major → Ab major)
M:4/4
L:1/2
K:C
[CEG]2 | [C_E_A]2 | [C_E_A] [_B,_DG] | [_A,C_E]2 |
w: C _ Ab(C is common tone) Eb7 Ab
```

## Sequential Modulation

A melodic-harmonic sequence naturally drifts into a new key without a specific pivot moment.

```abc
X:7
T:Sequential Modulation (C → D via ascending sequence)
M:4/4
L:1/8
K:C
%% Sequence step 1 (C area)
C2E2 G2c2 | B2A2 G4 |
%% Sequence step 2 (up a step → D area)
D2^F2 A2d2 | ^c2B2 A4 |
%% Confirm D major
[K:D] D8 |
```

## Key Relationships

| Relationship | Example from C | Distance | Effect |
|---|---|---|---|
| Dominant (V) | C → G | 1 sharp | Very smooth, natural |
| Subdominant (IV) | C → F | 1 flat | Warm, relaxed |
| Relative minor (vi) | C → Am | Same sig | Darkening |
| Relative major (III) | Cm → Eb | Same sig | Brightening |
| Chromatic mediant (M3) | C → E or C → Ab | Remote | Magical, colorful |
| Chromatic mediant (m3) | C → Eb or C → A | Moderate | Shadowed or luminous |
| Tritone | C → F# | Maximum | Shocking, dramatic |
| Semitone | C → Db or C → B | Very close (but remote) | Dramatic shift |

## Modulation by Period

| Period | Typical modulations | Favorite techniques |
|---|---|---|
| Baroque | V, relative major/minor | Sequential, circle of 5ths |
| Classical | Exposition: I→V (major), i→III (minor) | Pivot chord, dominant preparation |
| Romantic | Chromatic mediants, any 3rd relationship | Chromatic, enharmonic, direct |
| Late Romantic | Continuous modulation, anywhere | Chromatic voice-leading, dim7 pivot |
| Impressionist | Parallel motion, not functional modulation | Common-tone, modal shift, planing |
| Modern | Atonal (no modulation) or block juxtaposition | Direct, unprepared |

## Common Modulation Paths

### Sonata Exposition
| Key scheme | Major | Minor |
|---|---|---|
| Standard | I → V | i → III |
| Romantic | I → iii, bVI, or bIII | i → V, bVI, or III |

### Development Section
- Through circle of 5ths: I → vi → ii → V → (remote) → V/I → I
- Flat-side exploration: visit bVI, bIII, bVII before returning

### Return to Tonic
| Technique | Method | Bars needed |
|---|---|---|
| Dominant pedal | Sustained V, increasing intensity above | 4-16 |
| Retransition | Gradual approach to V, then resolve | 8-32 |
| Dramatic arrival | Sudden V7 → I | 1-2 |

```abc
X:8
T:Dominant Pedal Retransition
M:4/4
L:1/4
K:C
%% Sustained G in bass while upper voices become increasingly chromatic
V:1 clef=treble
[DF] [^CE] [DF] [EG] | [^FG] [^GA] [AB] [Bc] |
V:2 clef=bass
G,4 | G,4 |
%% Resolution
V:1
[Ec]4 |
V:2
C,4 |
w: _ _ _ _ _ _ _ _ V_pedal_________ I
```

## Modulation Smoothness Guide

| Desired effect | Use this type | Key distance |
|---|---|---|
| Seamless, unnoticeable | Pivot chord | Close keys (V, IV, vi) |
| Gentle color change | Common-tone | Chromatic mediants |
| Dramatic surprise | Direct/phrase | Any distance |
| Intensification | Sequential | Step-by-step |
| Mysterious, remote | Enharmonic (dim7) | Distant keys |
| Yearning, chromatic | Chromatic | Semitone or whole-tone |
