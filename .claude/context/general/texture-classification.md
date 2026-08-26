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

## Varying Texture at the Keyboard

Everything above is written for an ensemble, where texture changes by adding and
removing players. At a keyboard there are no players to remove, and the guidance
does not transfer — which is why generated piano writing tends to hold one
texture for a whole section without anyone noticing.

**The measurement that exposes it.** Count how many notes are **sounding at
once** at each attack, then take the coefficient of variation across the piece.
Measured over 22 real movements: **Mozart 0.21–0.41, Beethoven 0.32–0.50,
Chopin 0.17–0.30.**

> This is **simultaneity CV** — how much the *thickness* varies. Do not confuse
> it with the **density CV** in `human-sounding-music.md` (Mozart 0.21–0.47),
> which counts *events per bar* — how much the *activity* varies. The two
> numbers look alike and measure different things: a bar of running sixteenths
> in one voice is dense but thin, and a held four-note chord is thick but not
> dense. Three quantities in this codebase have already worn confusingly similar
> names and two of them disagreed by 3–4× inside a single context window.
Generated pieces come in at 0.19 and below — outside the range of any of them.
Not too thin, and not too busy: the number of notes sounding *never changes*.
It is the single texture measurement on which generated music most reliably
leaves the repertoire.

Note what this is not saying. The same measurements found the generated right
hand at 1.13 notes per attack against real Mozart's 1.22 — inside the range —
and its texture-change rate at 0.62 against Mozart's 0.47–0.77. The average
thickness was fine. What was missing was the **variance**: the piece never
thickened at a climax and never thinned into a cadence.

### The devices, in rough order of how much they change

| Device | What it does | Where it belongs |
|---|---|---|
| Melody in octaves | Doubles the tune's weight without adding harmony | A theme's forceful return; the top of a crescendo |
| Melody in thirds or sixths | Adds warmth and body to one line | A lyrical phrase's high point; a repeat of a phrase already heard plain |
| Added inner voice | Fills the hole between melody and bass | Anywhere the middle sounds empty; a suspension or a held dissonance |
| Broken-chord accompaniment → block chords | Thickens and steadies | Approaching a cadence; the arrival of a new section |
| Block chords → broken chords | Loosens and moves | Leaving a cadence; a transition |
| Bass in octaves | Deepens the floor | A climax; the last statement of a theme |
| Drop to two bare voices | Sudden intimacy | After a climax; the start of a development |
| Melody alone, unaccompanied | Maximum exposure | An opening; a moment of suspension before a return |
| Register transfer up an octave | Same material, new colour | A varied repeat; the second half of a period |

### How real music paces it

Real writing does **not** change accompaniment idiom every bar or every phrase.
Measured across the same movements, distinct left-hand bar-patterns per bar have
medians of 0.33 (Mozart), 0.27 (Beethoven) and 0.15 (Chopin) — three quarters of
Chopin's bars reuse a figure already heard. The figure holds; what changes is
the **weight**.

So the practical rule is not "vary the texture more often". It is:

- Let an accompaniment figure hold for a phrase or longer. That is what real
  music does, and churning it is its own machine tell.
- Change the *thickness* at the points where the music means something — the
  climax, the cadence, the return, the moment a theme comes back.
- **Eight bars is the outer limit** for one unchanging texture before a listener
  stops hearing it as a texture at all. If a stretch that long has to stay, give
  it a register transfer or a single thinned bar to breathe.

### The cheapest fixes, when a piece measures flat

1. **Thin one bar before each cadence.** Drop the accompaniment to the bare bass
   note for a bar. It costs nothing and it is what makes a cadence sound like an
   arrival rather than a bar that happens to end.
2. **Thicken the climax.** Wherever the melody reaches its highest point, put the
   tune in octaves or add a third under it for those two or three bars.
3. **Vary the repeat.** When a phrase returns unchanged, change its texture
   rather than its notes: plain the first time, in thirds the second.

Each of these moves the measurement, but that is not the reason to do them. They
are the reason the measurement exists.

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
