# Texture Classification

> These are guidelines for understanding and managing musical texture. Different periods and genres favor different textures — consult period-specific context files.

## Texture Types

| Texture | Description | Voices | Period association |
|---|---|---|---|
| Monophonic | Single unaccompanied melodic line | 1 | Chant, solo passages, unison |
| Homophonic | Melody + chordal accompaniment | 2+ (1 melody) | Classical default, Romantic |
| Polyphonic (contrapuntal) | Multiple independent melodic lines | 2-6 | Baroque, development sections |
| Heterophonic | Simultaneous variations of same melody | 2+ | Folk music, some Impressionism |
| Homorhythmic | All voices same rhythm, different pitches | 2+ | Chorales, hymns, brass writing |
| Melody + bass | Two-voice framework, implied harmony | 2 | Baroque continuo, simple accompaniment |

```abc
X:1
T:Homophonic Texture (melody + chordal accompaniment)
M:4/4
L:1/8
K:C
V:Melody clef=treble
!mf! c2d2 e2f2 | g4 e4 |
V:Accomp clef=bass
[C,E,G,]4 [D,F,A,]4 | [E,G,B,]4 [C,E,G,]4 |
```

```abc
X:2
T:Polyphonic Texture (two independent lines)
M:4/4
L:1/8
K:C
V:1 clef=treble
c2B2 A2G2 | F2E2 D2C2 |
V:2 clef=bass
C,2D,2 E,2F,2 | G,2A,2 B,2c2 |
%% Voices move independently, often in contrary motion
```

## Texture Density Scale

| Level | Description | Typical dynamic | Context |
|---|---|---|---|
| Solo line | Single unaccompanied instrument | pp-p | Openings, exposed moments |
| Duo | Two voices/instruments | pp-mp | Dialogue, intimate |
| Trio | Three voices | p-mf | Chamber, clarity |
| Quartet | Four voices (SATB model) | p-f | Standard ensemble |
| Chamber group | 5-9 instruments | mp-f | Rich but transparent |
| Section | One orchestral section (e.g., strings) | mf-ff | Section melodies |
| Multiple sections | Two or more sections combined | f-ff | Building passages |
| Full orchestra | All sections together | ff-fff | Climaxes, tutti |
| Massive tutti | Full orchestra + percussion + extra forces | fff-ffff | Maximum impact |

## Texture as Form Marker

Texture changes characteristically signal structural boundaries:

| Structural moment | Texture change | Effect |
|---|---|---|
| Section boundary | Thin → thick or thick → thin | Clear articulation |
| Theme entry | Reduction to melody + light accompaniment | Focus on new theme |
| Development opening | Fragmentation, contrapuntal texture | Increased complexity |
| Pre-recapitulation | Thinning, dominant pedal, single instrument | Anticipation |
| Climax | Maximum density, full scoring | Peak impact |
| Coda opening | Sudden thinning after climax | Reflective space |

## Texture Transitions

| From | To | Technique | Effect |
|---|---|---|---|
| Tutti | Solo | Voices drop out one by one | Gradual thinning |
| Tutti | Solo | Sudden stop, solo enters in silence | Dramatic contrast |
| Solo | Tutti | Voices layer in (additive) | Gradual building |
| Solo | Tutti | Sudden full entry | Explosion |
| Homophonic | Polyphonic | Inner voices gain independence | Increasing complexity |
| Polyphonic | Homophonic | Voices converge to same rhythm | Simplification, arrival |
| Dense | Sparse | Instruments peel away, register narrows | Wind-down, dissolution |
| Sparse | Dense | Instruments enter, register expands | Building intensity |

```abc
X:3
T:Texture Transition - Additive (solo → full)
M:4/4
L:1/8
K:G
%%staves [V1 V2 Va Vc]
V:V1 name="Violin I"
V:V2 name="Violin II"
V:Va name="Viola" clef=alto
V:Vc name="Cello" clef=bass
%% Bar 1: solo
[V:V1] !p! B2d2 e2d2 |
[V:V2] z8 |
[V:Va] z8 |
[V:Vc] z8 |
%% Bar 2: duo
[V:V1] B2d2 e2d2 |
[V:V2] !p! G2B2 c2B2 |
[V:Va] z8 |
[V:Vc] z8 |
%% Bar 3: trio
[V:V1] B2d2 e2f2 |
[V:V2] G2B2 c2d2 |
[V:Va] !p! D2G2 A2B2 |
[V:Vc] z8 |
%% Bar 4: full quartet
[V:V1] !f! g8 |
[V:V2] !f! d8 |
[V:Va] !f! B8 |
[V:Vc] !f! G,8 |
```

## Accompaniment Texture Patterns

| Pattern | Description | Character | ABC shorthand |
|---|---|---|---|
| Block chords | Sustained or repeated chords | Hymn-like, stable | `[CEG]4` |
| Alberti bass | Low-high-mid-high | Classical, piano | `C,GEG` |
| Arpeggiation | Broken chord, ascending or mixed | Flowing, Romantic | `C,EGc` |
| Tremolo | Rapid repeated notes | Agitation, shimmer | `C,C,C,C,C,C,C,C,` |
| Waltz bass | Bass + chord + chord | Dance, triple meter | `C, [EG] [EG]` |
| Ostinato | Repeated pattern (may be melodic) | Driving, persistent | Fixed pattern repeating |
| Counter-melody | Independent secondary melody | Rich, polyphonic | Full melodic line |
| Pedal point | Sustained bass under moving harmony | Anchored tension | `C,8` under changes |
| Pizzicato | Plucked strings as accompaniment | Light, rhythmic | Staccato patterns |
| Tremolo strings | Sustained tremolo | Atmospheric, tense | Measured or unmeasured |

## Texture by Period

| Period | Default texture | Special textures | Density |
|---|---|---|---|
| Baroque | Continuo + melody, fugal polyphony | Terraced dynamics (block changes) | Moderate |
| Classical | Alberti bass, homophonic | Fugal development sections | Light-moderate |
| Romantic | Rich accompaniment, orchestral density | Song texture, brass chorale | Moderate-dense |
| Impressionist | Layered colors, parallel streams | Floating, heterophonic | Varies widely |
| Modern | Pointillistic, clusters, sparse | Spatial, extended techniques | Extremes |
| Minimalist | Repetitive layers, additive | Phasing, gradual process | Gradually increasing |
| Film Score | Narrative-driven, hybrid | Electronic + acoustic layers | Serves scene |

## Register and Texture Interaction

| Register | Texture considerations |
|---|---|
| Very low (C1-C3) | Wide spacing required; thick texture = mud |
| Low-mid (C3-C4) | Can thicken moderately; cellos, bassoons, violas |
| Mid (C4-C5) | Dense scoring possible; all instruments comfortable |
| High (C5-C7) | Thinner scoring; brightness; flutes, violins |
| Very high (C7+) | Solo only; extreme brilliance; piccolo, harmonics |

```abc
X:4
T:Register-Appropriate Spacing
M:4/4
L:1/2
K:C
V:1 clef=treble
%% High register: thin (2 voices, wide apart)
[cg] [df] |
V:2 clef=bass
%% Low register: wide spacing (voices far apart)
[C,,G,,] [D,,A,,] |
```

## Texture Density and Dynamics

| Dynamic | Typical density | Notes |
|---|---|---|
| ppp-pp | Solo or duo | Maximum sparseness |
| p | Small group, light scoring | Transparent |
| mp-mf | Section or chamber | Standard |
| f | Multiple sections | Rich, full |
| ff-fff | Full forces | Maximum density |

Exceptions are powerful: a ppp tutti (all instruments very quiet) creates eerie atmosphere; an fff solo (single instrument maximum volume) creates desperate intensity.
