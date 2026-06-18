# Steve Reich — Harmonic Language

## Core Principle: Simple Harmony, Complex Rhythm

Reich's harmony is deliberately uninteresting — diatonic, stable, unchanging. The interest lives entirely in rhythm and pattern interaction. Harmony provides a stable ground so the rhythmic complexity can be heard.

## Harmonic Vocabulary

| Element | Description |
|---------|-------------|
| Chord types | Major and minor triads; occasional 7ths in late works |
| Chords per piece | 1–4 (often just 1–2) |
| Mode | Diatonic major or Dorian most common |
| Chromatic notes | None in early/middle works; rare in late |
| Functional harmony | Absent — no V→I, no tension-resolution |
| Harmonic rhythm | Extremely slow: one chord for 5–15 minutes |

## Harmonic Stasis

| Approach | Description | Works |
|----------|-------------|-------|
| Single chord | Entire piece on one harmony | *Piano Phase*, *Violin Phase* |
| Single mode | All notes from one diatonic scale; no single "chord" | *Music for 18 Musicians* sections |
| Oscillation | Two chords alternating every 8–16 bars | *Electric Counterpoint* |
| Slow progression | 4–6 chords over 15–60 minutes | *Music for 18 Musicians* overall arc |

```abc
X:1
T:Harmonic Stasis — Single Chord (Piano Phase style)
M:4/4
L:1/8
K:C
ECGC EGCE | ECGC EGCE | ECGC EGCE | ECGC EGCE |
% 16+ bars on one chord — the harmony never changes; the phasing creates all interest
```

## Phase-Created Harmony

When two identical patterns shift out of sync, new harmonies emerge that were not composed — they are a product of the process:

| Phase Offset | Resulting Harmony | Character |
|-------------|-------------------|-----------|
| Unison (0) | Pure unison | Clear, open |
| +1 eighth | New interval combinations | Thickening |
| +2 eighths | More complex interlocking | Dense |
| +3 eighths | Maximum complexity | Richest emergent harmony |
| +4 eighths (half pattern) | Complementary pattern | Densest; all rhythmic positions filled |

```abc
X:2
T:Phase-Created Harmony — Emergent Intervals
M:4/4
L:1/8
K:C
%%staves {1 2}
V:1 name="Pattern (on tempo)"
EGCE GCEG | EGCE GCEG |
V:2 name="Same pattern (+2 eighths)"
CEEG CEGG | CEEG CEGG |
% The intervals between voices are not composed — they emerge from the phase offset
```

## Pulsing Chord Technique (Music for 18 Musicians)

| Element | Description |
|---------|-------------|
| Chord | A single rich chord (often with 7th or 9th) |
| Presentation | All instruments pulse the chord in steady eighth notes |
| Evolution | Individual instruments drop in/out, changing the chord's color |
| Duration | Each chord lasts 4–6 minutes |
| Transition | "Bass clarinet signal" — bass clarinet plays a pattern to signal next chord |

### Music for 18 Musicians — Chord Cycle

| Section | Chord | Duration | Character |
|---------|-------|----------|-----------|
| Section I | D major + pulsing | ~5 min | Bright, opening |
| Section II | D with added B (6th) | ~5 min | Warmer |
| Section III | F# minor area | ~4 min | Darkening |
| ... | Continues through 11 sections | ... | ... |
| Section XI | Return to D major | ~5 min | Resolution |

```abc
X:3
T:Pulsing Chord Technique (Music for 18 Musicians style)
M:4/4
L:1/8
K:D
%%staves {1 2 3}
V:1 name="Pianos (pulsing)"
[DF#A] [DF#A] [DF#A] [DF#A] [DF#A] [DF#A] [DF#A] [DF#A] |
V:2 name="Marimbas (pattern)"
D2 F#2 A2 D2 | F#2 A2 D2 F#2 |
V:3 name="Bass clarinet (signal)"
z8 | z8 |
% The chord pulses; the marimba pattern adds rhythmic interest within the static harmony
```

## Modal Treatment

| Mode | Usage | Works |
|------|-------|-------|
| C major (Ionian) | Default; maximum simplicity | *Piano Phase*, *Clapping Music* |
| D Dorian | Warm, neutral | *Music for 18 Musicians* |
| E minor (Aeolian) | Darker sections | Late ensemble works |
| B Phrygian | Rare; exotic color | Specific sections |
| Pentatonic | Very common; avoids semitones | *Drumming*, mallet percussion works |

```abc
X:4
T:Pentatonic Harmony — Drumming Style
M:4/4
L:1/8
K:C
%% C pentatonic: C D E G A (no F, no B)
CDEG ADEG | CDGA CDEG | ACDE GACD | EGAC DEGA |
% No semitones — the pentatonic scale avoids all dissonance
```

## Consonance and Dissonance

| Interval | Frequency in Reich | Context |
|----------|-------------------|---------|
| Unison/Octave | Very frequent | Doubling, unison patterns |
| Perfect 5th | Very frequent | Open voicing |
| Major/minor 3rd | Frequent | Triadic harmony |
| Perfect 4th | Frequent | Interlocking patterns |
| Major 2nd | Occasional | Emergent from phasing |
| Minor 2nd | Rare | Only from phase collision |
| Tritone | Almost never | Avoided |

## Late Period Harmonic Expansion

| Feature | Early/Middle (1965–88) | Late (1988–present) |
|---------|----------------------|---------------------|
| Chord types | Triads only | Triads + 7ths + added tones |
| Chromaticism | None | Occasional (Different Trains) |
| Modulation | None | Between sections (slow) |
| Harmonic rhythm | Static | Slightly more motion |
| Tonal center | Fixed | May shift between movements |

```abc
X:5
T:Late Period — Richer Harmony (Different Trains style)
M:4/4
L:1/8
K:Am
%%staves {1 2}
V:1 name="String quartet (pulsing)"
[A,CE]2 [A,CE]2 [A,CE]2 [A,CE]2 |
V:2 name="Tape (speech melody)"
A,2 C2 E2 D2 |
% Richer harmonic context in late works — string quartet + sampled speech
```

## References
- Reich, Steve. *Writings on Music 1965–2000*, 2002
- Potter, Keith. *Four Musical Minimalists*, 2000
- Schwarz, K. Robert. *Minimalists*, 1996
