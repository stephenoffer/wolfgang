# Arnold Schoenberg — Harmonic Language

Schoenberg's harmonic language is three completely different systems. The Late Romantic Schoenberg pushes Wagner's chromaticism to the breaking point. The Atonal Schoenberg abolishes tonality entirely — the "emancipation of dissonance," where all intervals are equally valid. The Twelve-Tone Schoenberg replaces tonal organization with row-based organization: all 12 chromatic pitches in a fixed order, generating all melody and harmony.

For shared modern harmonic vocabulary (twelve-tone method, set theory), see [modern-harmony.md](../../modern-harmony.md). This file covers what is distinctly Schoenbergian.

## Core Harmonic Character by Period

| Feature | Late Romantic (1899–1908) | Atonal (1908–23) | Twelve-Tone (1923–51) |
|---------|--------------------------|-------------------|-----------------------|
| Tonal center | Present but remote; deferred resolution | None; deliberately destroyed | None; row determines pitch |
| Dissonance | Extreme chromaticism; dissonance prepared but barely resolved | All intervals equal; "emancipation of dissonance" | Row-determined; dissonance is the norm |
| Scale basis | Chromatic scale within tonal framework | All 12 pitches equally available | Tone row: fixed order of all 12 |
| Chords | Extended tertian (9ths, 11ths, 13ths) | Free; any combination | Row segments as vertical chords |
| Cadences | Deferred, chromatic, eventually tonal | None | Row completion as structural punctuation |
| Voice-leading | Chromatic, Wagnerian, smooth | Free; wide leaps acceptable | Row-determined |

## Late Romantic Harmony (1899–1908)

### Chromatic Saturation

Schoenberg takes Wagner's chromatic harmony and pushes it further: longer passages without resolution, more complex chromatic voice-leading, more remote key relationships.

| Technique | Description | Where |
|-----------|-------------|-------|
| Chromatic sequence | Sequence pattern moves by semitone instead of diatonic step | Verklarte Nacht development |
| Deferred cadence | V chord appears but resolution is delayed by 8–16 bars | Gurrelieder |
| Enharmonic ambiguity | Chords that belong to 2–3 keys simultaneously | Chamber Symphony No. 1 |
| Quartal chords | Stacked 4ths replacing tertian harmony | Chamber Symphony No. 1 (opening horn call) |
| Whole-tone passage | Floating, directionless harmony | Pelleas und Melisande |

```abc
X:1
T:Late Romantic — Chromatic Saturation (Verklarte Nacht character)
M:4/4
L:1/8
K:Dm
%% Chromatic voice-leading: every note moves by semitone; tonal center distant
!p!D ^F A ^c|d _e _d c|_B A ^G A|^F _A G _G|
%% Still tonal (D minor implied) but the chromaticism makes the key uncertain
```

### Quartal Harmony (Bridge to Atonality)

The Chamber Symphony No. 1 (1906) opens with a horn call built on stacked perfect 4ths — a chord that is neither major, minor, nor diminished. This is the bridge to atonality.

```abc
X:2
T:Quartal Horn Call — Chamber Symphony No. 1 character
M:4/4
L:1/4
K:C
%% Stacked 4ths: F-Bb-Eb-Ab-Db — no tertian root
!ff![F,_B,_E_A_d]2 z2|[F,_B,_E_A_d]4|
%% Neither major nor minor; the old harmonic categories don't apply
```

## Free Atonality (1908–1923)

### The Emancipation of Dissonance

Schoenberg's principle: "dissonance" is simply a less familiar consonance. There are no dissonances or consonances — only intervals, each with its own character.

| Principle | Description |
|-----------|-------------|
| No consonance/dissonance hierarchy | All intervals are equally valid |
| No resolution required | A tritone does not need to resolve to a 3rd |
| No tonal center | No note is "home"; all pitches are equal |
| No functional harmony | No V-I, no ii-V-I, no cadential patterns |
| Motivic coherence replaces tonal coherence | Unity comes from shared motifs, not from key |

| Interval | Atonal Schoenberg's Use | Character |
|----------|------------------------|-----------|
| Minor 2nd / Major 7th | Primary tension interval; used freely | Biting, intense |
| Major 2nd / Minor 7th | Common melodic interval | Moderate tension |
| Minor 3rd | Frequent; octatonic reference | Dark |
| Major 3rd | Used as any other interval | Neither warm nor cold |
| Tritone | Central: the most symmetrical interval | Restless, pivotal |
| Perfect intervals (4th, 5th) | Avoided in melody (too "tonal" sounding) | Used structurally, not melodically |

```abc
X:3
T:Free Atonality — No Tonal Center (Op. 11 No. 1 character)
M:3/4
L:1/8
K:C clef=treble
%% Wide leaps, no key, every interval different, compressed intensity
!p!B,2 z ^F|_E2 z ^C'|G z _B z|D' z F, z|
%% No pitch returns quickly; no interval repeated; each event is new
```

## Twelve-Tone Method (1923–1951)

### Row Organization

| Element | Description |
|---------|-------------|
| Tone row (P-0) | All 12 chromatic pitches in a specific order, each used once |
| P (Prime) | Row in original order |
| R (Retrograde) | Row backwards |
| I (Inversion) | Each interval inverted (ascending → descending) |
| RI (Retrograde Inversion) | Inversion played backwards |
| 48 row forms | 4 forms × 12 transpositions |
| Row as melody | The row stated as a linear melody |
| Row as harmony | Row pitches grouped into chords (3+3+3+3, or 4+4+4, etc.) |
| Combinatoriality | Two row forms that together fill the chromatic aggregate |

```abc
X:4
T:Twelve-Tone Row — P-0 and I-0 (Op. 25 character)
M:4/4
L:1/8
K:C clef=treble
%% P-0 (Prime):
E F G _D ^G _E _A D B ^F _B C|
%% I-0 (Inversion — every interval flipped):
E _E _D ^G D ^F C F _A B _B _E|
```

### Row Harmonization

| Strategy | Description | Sound |
|----------|-------------|-------|
| Trichordal | Row divided into 4 groups of 3; each group = a chord | 4 chords per row statement |
| Tetrachordal | Row divided into 3 groups of 4 | 3 chords per row statement |
| Hexachordal | Row divided into 2 groups of 6 | 2 large sonorities |
| Mixed | Some pitches melodic, some harmonic | Most common approach |
| Combinatorial | Two row forms paired so their first hexachords together = 12 pitches | Aggregate completion |

### American Period — Serial with Tonal References

| Feature | Description | Where |
|---------|-------------|-------|
| Row designed with tonal intervals | Rows containing triadic subsets (3rds, 5ths) | Violin Concerto, Piano Concerto |
| Tonal allusions | Moments that briefly sound like a key | String Trio Op. 45 |
| Row relaxation | Occasional pitch repetition before row completion | Late works |
| Expressive warmth | Serial technique serving lyrical, expressive writing | Violin Concerto slow movement |

## Voice-Leading

| Period | Principle |
|--------|-----------|
| Late Romantic | Chromatic; smooth; stepwise; Wagnerian |
| Atonal | Free; wide leaps; no smoothness required; pointillistic |
| Twelve-tone | Row-determined; can be smooth or disjunct depending on row design |

## References

- [composition-guide.md](composition-guide.md) — Fingerprints by period; row-writing directives
- [melodic-style.md](melodic-style.md) — How the row becomes melody
- [orchestration.md](orchestration.md) — How harmonic texture distributes across instruments
- [formal-approach.md](formal-approach.md) — Row completion as formal articulation
- [../../modern-harmony.md](../../modern-harmony.md) — Twelve-tone technique reference table
