# Igor Stravinsky — Harmonic Language

Stravinsky's harmony is not a single system — it is three. The Russian period superimposes keys. The Neo-Classical period displaces diatonic harmony by a semitone. The serial period organizes twelve tones into ritualistic rows. What connects them: the octatonic scale as a lifelong harmonic resource, and the principle that harmony is color and structure, never emotional expression in the Romantic sense.

For shared modern harmonic vocabulary (polytonality, quartal harmony, twelve-tone), see [modern-harmony.md](../../modern-harmony.md). This file covers what is distinctly Stravinskian.

## Core Harmonic Character by Period

| Feature | Russian (1910–20) | Neo-Classical (1920–51) | Serial (1953–66) |
|---------|-------------------|-------------------------|-------------------|
| Tonal center | Present but unstable; often two centers simultaneously | Present; deliberately misaligned with melody | Absent; row determines pitch |
| Dissonance | Unresolved clusters, polytonal clashes | Added-note triads, "wrong" harmonizations | Interval-class logic, not consonance/dissonance |
| Scale basis | Octatonic, whole-tone, folk modes | Diatonic (but displaced), octatonic | Chromatic (twelve-tone rows) |
| Voice-leading | Parallel motion, anti-smooth | Baroque stepwise (with displaced accents) | Pointillistic, wide leaps |
| Cadence | No traditional cadences; blocks end, not resolve | Ironic V-I or plagal; the cadence formula quoted | Row completion as structural punctuation |

## Polytonality (Russian Period)

| Type | Construction | Sound | Example |
|------|-------------|-------|---------|
| Petrushka chord | C major + F# major (tritone apart) | Harsh, specific, iconic | Petrushka, Second Tableau |
| Layered ostinati | Each layer in its own key | Shimmering conflict | Rite of Spring, "Augurs of Spring" |
| Bitonal melody | Melody in one key, bass in another | Tension without atonality | Firebird "Infernal Dance" |
| Polytonal cadence | Each layer resolves in its own key | Irresolution as resolution | Les Noces |

```abc
X:1
T:Petrushka Chord — C major + F# major superimposed
M:4/4
L:1/4
K:C
%%staves {1 2}
V:1
[CEG]2 [CEG]2 |[CEG]4|
V:2
[^F^A^c]2 [^F^A^c]2 |[^F^A^c]4|
%% Two triads a tritone apart — neither wins; the clash IS the harmony
```

## Octatonic Scale (All Periods)

The octatonic scale (alternating half and whole steps: C-Db-Eb-E-F#-G-A-Bb) is Stravinsky's most persistent harmonic resource. It appears in all three periods, providing symmetry and limited transposition.

| Property | Description | Compositional Use |
|----------|-------------|-------------------|
| 3 transpositions only | Only 3 distinct octatonic collections | Limits modulation possibilities — a closed system |
| Contains major AND minor triads | C major + C minor both available within one collection | Harmonic ambiguity without atonality |
| Tritone symmetry | Every interval has its tritone complement | The Petrushka chord is native to the octatonic |
| Diminished 7th chords | Two dim7 chords per collection | Provides pivot points between collections |

```abc
X:2
T:Octatonic Scale — Three Collections
M:4/4
L:1/8
K:C
%% Collection I (half-whole):
C _D _E E ^F G A _B c|
%% Collection II:
^C D E F G _A _B B ^c|
%% Collection III:
D _E F ^F ^G A B c d|
```

## Added-Note Chords (Neo-Classical Period)

| Chord Type | Construction | Example | Sound |
|-----------|-------------|---------|-------|
| Major + major 7th | C-E-G-B | Symphony in C | Bright dissonance, unresolved |
| Major + added 2nd | C-D-E-G | Pulcinella | Pandiatonic cluster |
| Minor + major 7th | C-Eb-G-B | Symphony of Psalms | Dark tension |
| Triad + tritone | C-E-G-F# | Petrushka-derived | Pungent, specific |
| Superimposed 4ths | C-F-Bb-Eb | Rite of Spring, Agon | Open, modern, ambiguous |

```abc
X:3
T:Neo-Classical Added-Note Harmony (Symphony in C character)
M:4/4
L:1/4
K:C
%% Diatonic triads with "wrong" added notes — Stravinsky's ironic sweetness
[CEGBd] [DFAce] | [EGBdf] [CEGBd] |
%% Every chord is a triad PLUS extra diatonic notes — pandiatonic stacking
```

## "Wrong-Note" Technique (Neo-Classical)

The melody sits in one diatonic collection; the harmony sits in another. Both are "correct" independently; together they create ironic friction.

| Strategy | Melody Key | Harmony Key | Effect |
|----------|-----------|-------------|--------|
| Semitone displacement | C major | Db major or B major | Every chord slightly "off" |
| Modal mismatch | C Ionian melody | C Mixolydian harmony (Bb in bass) | Familiar melody, unfamiliar support |
| Cadence subversion | V-I expected | V arrives, I doesn't (or arrives in wrong octave) | The joke: you hear the convention but it slips |

```abc
X:4
T:Wrong-Note Harmonization — C major melody over A major harmony
M:3/4
L:1/4
K:C
V:1 name="Melody (C major)"
C E G|F E D|C3|
V:2 name="Harmony (A major)" clef=bass
[A,^CE]2 [A,^CE]|[D,^FA]2 [E,^GB]|[A,^CE]3|
%% Melody is C major; harmony is A major — both correct, together wrong
```

## Serial Technique (Late Period)

| Element | Stravinsky's Approach | vs. Schoenberg |
|---------|----------------------|----------------|
| Row usage | Short rows (5–8 notes) common alongside full 12-tone rows | Schoenberg: always 12 tones |
| Rotational arrays | Row segments rotated to create vertical harmonies | Schoenberg: matrix-based |
| Rhythm | Rhythmically free; rows don't determine rhythm | Schoenberg: rhythm more tied to row |
| Texture | Spare, ritualistic, many rests | Schoenberg: denser, more continuous |
| Expression | Austere, impersonal, liturgical | Schoenberg: expressionistic, dramatic |

## Harmonic Rhythm

| Context | Russian Period | Neo-Classical | Serial |
|---------|---------------|---------------|--------|
| Static passage | Ostinato: same chord 16–32 bars | Ostinato bass, shifting upper voices | Sustained row tones, long silences |
| Active passage | Block juxtaposition (instant change) | Baroque-style sequence (regular) | Pointillistic (one note, silence, one note) |
| Climax | Polytonal accumulation, all layers at once | Full diatonic tutti, ironic ff | All row forms compressed into dense texture |

## Key Signatures and Centers

| Period | Tonal Organization | Common Centers |
|--------|-------------------|---------------|
| Russian | Multiple simultaneous centers; octatonic | D, C + F# (Petrushka), D + Eb (Rite) |
| Neo-Classical | Single center, displaced harmonization | C (Symphony in C), Eb (Symphony of Psalms), D (Concerto in D) |
| Serial | No tonal center; row determines pitch | Row-based; no key signature |

## References

- [composition-guide.md](composition-guide.md) — Fingerprints #1 (block juxtaposition), #3 (polytonality)
- [orchestration.md](orchestration.md) — How harmonic layers are distributed across instruments
- [formal-approach.md](formal-approach.md) — Harmonic stasis vs. block change as formal structure
- [cross-references.md](cross-references.md) — Stravinsky vs. Schoenberg harmonic philosophy
- [../../modern-harmony.md](../../modern-harmony.md) — Shared modern harmonic vocabulary
