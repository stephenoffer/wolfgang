# Bela Bartok — Harmonic Language

Bartok's harmony is a personal system — neither tonal in the Classical sense nor atonal in Schoenberg's sense. It draws from three sources simultaneously: folk modes, chromatic saturation, and a symmetrical "axis system" that replaces major/minor tonality with a new logic based on tritone equivalence. The result is music that has tonal centers without tonal function — you feel where the music is going, but the rules that take it there are Bartok's own.

For shared modern harmonic vocabulary (polytonality, quartal harmony, twelve-tone), see [modern-harmony.md](../../modern-harmony.md). This file covers what is distinctly Bartokian.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Axis system | Tritone-related keys as functional equivalents (C = F#; D = Ab) | All mature works; key relationships in sonata forms |
| Folk modes | Lydian, Phrygian, Dorian, Mixolydian, pentatonic as primary scales | Melody and local harmony throughout |
| Acoustic scale | C-D-E-F#-G-A-Bb (overtone-derived; Lydian-Dominant) | Bartok's "natural" scale; appears in consonant passages |
| Chromatic compression | All 12 pitches in close proximity, organized around a tonal center | Development sections, climaxes |
| Night music harmony | Chromatic clusters (2–3 adjacent semitones) sustained in ppp | Slow movements of quartets and concertos |
| Golden section proportion | Climax placed at the golden ratio (0.618) of a section | Music for Strings, String Quartet No. 5 |
| Pitch-axis symmetry | Chords and melodies mirrored around a central pitch | Consistently from String Quartet No. 4 onward |

## The Axis System

Bartok's most important harmonic innovation. Based on the circle of fifths divided into three functional groups, each containing two tritone-related pairs:

| Function | Axis Members | Example (C tonic) |
|----------|-------------|-------------------|
| Tonic (T) | C - Eb - F# - A | C = F# = Eb = A as "tonic" |
| Subdominant (S) | F - Ab - B - D | F = B = Ab = D as "subdominant" |
| Dominant (D) | G - Bb - Db - E | G = Db = Bb = E as "dominant" |

**The key insight:** C major and F# major are not distant keys (as in Classical theory) — they are THE SAME FUNCTION. Movement from C to F# is not a modulation; it is a tonic restatement.

| Application | How It Works | Example |
|-------------|-------------|---------|
| Sonata form key areas | Exposition: C; Second group: Eb or F# (both Tonic axis) | Music for Strings, mvt 1 |
| Cadential substitute | V-I becomes Db-C (Db is dominant axis, same as G) | Common in mature works |
| Structural arrivals | Piece ends on axis-equivalent of opening key | String Quartet No. 4 |

```abc
X:1
T:Axis System — Tonic Equivalents (C and F# as same function)
M:4/4
L:1/4
K:C
%% C major arrival:
[CEG]2 [CEG]2|
%% F# major arrival (axis-equivalent tonic):
[^F^A^c]2 [^F^A^c]2|
%% Both feel like "home" — the tritone relationship is not dissonant but equivalent
```

## Folk Modes as Harmonic Resource

| Mode | Scale (from C) | Character | Bartok Use |
|------|---------------|-----------|------------|
| Pentatonic (anhemitonic) | C-D-F-G-A | No semitones; open, archaic | Primary folk-melody source |
| Lydian | C-D-E-F#-G-A-B | Raised 4th; bright, floating | Hungarian folk character |
| Phrygian | C-Db-Eb-F-G-Ab-Bb | Lowered 2nd; dark, Eastern | Romanian and Balkan folk |
| Dorian | C-D-Eb-F-G-A-Bb | Minor with raised 6th; warm | Hungarian folk melodies |
| Mixolydian | C-D-E-F-G-A-Bb | Major with flat 7th; earthy | Folk dance sections |
| Acoustic (Lydian-Dominant) | C-D-E-F#-G-A-Bb | Overtone-derived; natural | Bartok's "nature" scale |

```abc
X:2
T:Acoustic Scale Melody — The "Bartok Scale"
M:4/4
L:1/8
K:C
%% C-D-E-F#-G-A-Bb — Lydian + Mixolydian combined
C2 D2 E2 ^F2|G2 A2 _B2 c2|_B2 A2 G2 ^F2|E2 D2 C4|
%% The raised 4th (F#) and flat 7th (Bb) are BOTH present — neither major nor minor
```

## Chromatic Compression

In development sections and climaxes, Bartok saturates the chromatic space — all 12 pitches appear in close proximity — while maintaining a tonal center through pedal tone or melodic emphasis.

| Technique | Description | Effect |
|-----------|-------------|--------|
| Total chromatic within tonal frame | All 12 notes used; tonal center maintained by pedal or repetition | Dense but not directionless |
| Chromatic wedge | Two voices converge or diverge by semitone | Increasing tension as pitches approach |
| Semitone cluster | 3–4 adjacent semitones as simultaneous chord | Night music; mysterious, static |
| Chromatic saturation crescendo | Harmony becomes more chromatic as dynamics increase | Climax = maximum chromatic density |

```abc
X:3
T:Chromatic Wedge — Converging Voices
M:4/4
L:1/4
K:C
V:1 name="Upper voice"
V:2 name="Lower voice" clef=bass
%% Two voices approach each other by semitone — tension increases
[V:1] G F ^E E|_E D ^C C|
[V:2] C, ^C, D, _E,|E, F, ^F, G,|
%% Voices converge toward the middle — when they meet, maximum tension
```

## Night Music Harmony

Night music is not a harmonic system — it is a texture. The harmony is static chromatic clusters, sustained in silence, with no functional progression. Each cluster is chosen for its interval content (semitones, tritones), not for its relation to a key.

| Element | Description |
|---------|-------------|
| Cluster chords | 2–3 adjacent semitones (C-Db-D, or E-F-F#) |
| Tritone framing | The outer notes of a cluster span a tritone or augmented 4th |
| No voice-leading | Clusters appear and disappear; they don't "resolve" |
| Silence as harmony | The rests between events are part of the harmonic texture |
| Register extremes | Clusters in very high (harmonics) or very low (cello C string) register |

## Golden Section in Harmonic Structure

Bartok places structural harmonic events (key arrival, climax, thematic return) at golden-ratio proportions within sections.

| Section Length | GS Point (0.618) | What Happens There |
|---------------|-------------------|-------------------|
| 89 bars | Bar 55 | Climax or key arrival |
| 34 bars | Bar 21 | Thematic return or dynamic peak |
| 21 bars | Bar 13 | Secondary structural point |

**Note:** The Fibonacci sequence (1, 2, 3, 5, 8, 13, 21, 34, 55, 89) provides bar-count scaffolding.

## Pitch-Axis Symmetry

Chords built symmetrically around a central pitch. If the axis is D, then C# and Eb are equidistant; C and E are equidistant; B and F# are equidistant. This creates palindrome-like vertical structures.

```abc
X:4
T:Symmetric Chord Around D Axis
M:4/4
L:1/2
K:C
%% Each note has its mirror partner around D
[B,^CE^FA]2 [C_EFG_B]2|
%% B-C#-D-Eb-F is symmetric around D: B=m3 below, F=m3 above; C#=m2 below, Eb=m2 above
```

## Harmonic Rhythm

| Context | Typical Rate | Character |
|---------|-------------|-----------|
| Folk dance | 1 chord/bar or 1 chord/2 bars | Static modal harmony under moving melody |
| Night music | 1 chord/4–8 bars (or no change) | Time suspended; harmony is atmosphere |
| Percussive allegro | 2 chords/bar | Rapid, driving, motoric |
| Development | Accelerating toward chromatic saturation | Tension arc |
| Coda | Decelerating; return to modal clarity | Resolution from chromatic to diatonic |

## Key Centers and Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Most characteristic | C, D, A, E (string open-string keys) | Resonant on strings; Bartok writes for string sonority |
| Axis-paired centers | C/F#, D/Ab, E/Bb | Axis equivalents appear as paired key areas |
| Night music | No fixed center; chromatic | Atonal surface, tonal depth |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #2 (axis system), #3 (night music)
- [orchestration.md](orchestration.md) — How harmonic layers distribute across instruments
- [formal-approach.md](formal-approach.md) — Golden section and arch form in harmonic planning
- [melodic-style.md](melodic-style.md) — Folk modes as melodic source
- [cross-references.md](cross-references.md) — Bartok's axis system vs. functional tonality
- [../../modern-harmony.md](../../modern-harmony.md) — Shared modern harmonic vocabulary

---

## Cadences and closure

Bartók has no functional dominant, so closure is made by symmetry, by unison,
and by the modal degrees of the folk sources.

| Cadence | Construction | Where it belongs | Effect |
|---------|--------------|------------------|--------|
| Perfect authentic (PAC) | V–i, or the axis dominant to the tonic, in root position | Ends of folk-derived and Mikrokosmos pieces, where the tune implies it | Plain tonal closure, used deliberately |
| Half cadence (HC) | Arrival and pause on the dominant degree, or on the tonic's tritone axis partner | Between strains of a dance | Breath between repetitions |
| Unison / octave close | All voices converge on one pitch class | Movement ends | Absolute, primitive |
| Axis close | Arrival on the tonic of the axis system, approached from its tritone | Structural closes | Functional weight without a dominant |
| Modal cadence | bVII–i, or Lydian 4th falling to the final | Folk-derived material | The tune's own ending |
| Fibonacci arrival | The climax placed by golden section, then a rapid fall | Arch-form centres | Proportional, not harmonic |
| Cluster resolution | A dense chord thinning to a bare fifth or octave | Night-music endings | Clearing |
| Pizzicato snap | A single sharp attack after silence | Fast movements | Punctuation |

An authentic V-i is available to him and he uses it where a folk tune asks for it — but it is a choice, never the default, and the concert works close by symmetry and unison far more often.
