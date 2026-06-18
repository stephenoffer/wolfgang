# Minimalist Harmony Reference

## Core Harmonic Principles

| Principle | Description |
|-----------|-------------|
| Diatonic simplicity | Harmony drawn from single diatonic scale |
| Consonance focus | Triads, open intervals, major/minor chords |
| Slow evolution | Chord changes happen gradually over long spans |
| Repetition as stasis | Repeated chord creates harmonic plateau |
| Additive change | New pitches added one at a time |
| Phase-created harmony | Overlapping patterns create emergent chords |
| Process over progression | Harmony results from process, not planned progression |
| Drone foundation | Sustained or repeated bass provides ground |


## Harmony as Process and Meditation

Minimalist harmony discovers that repetition transforms the nature of a chord. After 16 bars, a triad ceases to be "a chord" and becomes an environment — the listener stops hearing it as an event and begins to inhabit it. This is harmony as architecture of attention: the slow accretion of small changes creates the effect of watching a landscape from a moving train, where the vast background remains constant while details shift in the foreground.

### Repetition as Harmonic Deepening

| Repetition Duration | What the Listener Experiences | Compositional Effect |
|--------------------|------------------------------|---------------------|
| 1-4 bars | Recognition — "this is the chord" | Establishing identity |
| 4-8 bars | Acceptance — the chord becomes expected | Settling, comfort |
| 8-16 bars | Immersion — the chord becomes the world | The listener stops analyzing and starts inhabiting |
| 16-32 bars | Transformation — overtones, beating, room acoustics become audible | Perception itself changes; the chord reveals hidden interior details |
| 32+ bars | Transcendence — the distinction between listener and sound blurs | Deep listening, meditative absorption |

### Emergent Harmony from Phase Processes

In Reich's phasing technique, harmony is not composed — it emerges from the interaction of two identical patterns gradually shifting out of sync. The resulting harmonies are both inevitable (determined by the process) and surprising (unpredictable to the ear). This creates a unique emotional quality: the listener senses an underlying logic but cannot predict the next moment, producing a state of alert relaxation.

### Consonance as Radical Act

After a century of increasing dissonance (Schoenberg, Webern, Boulez), the return to simple triads by Part, Gorecki, and Tavener was itself shocking and deeply moving. A bare A minor triad in Part's "Spiegel im Spiegel" carries more emotional weight than any twelve-tone row — not because triads are inherently superior, but because the historical context makes simplicity a radical statement. The listener hears both the chord and the century of complexity it renounces.

```abc
X:50
T:Consonance as Radical Act - Tintinnabuli Stillness
M:3/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice"
E A E | C E A | E C E | A E C |
V:2 name="M-voice"
B A G | F E D | C B, A, | B, C D |
% Simple triadic + stepwise motion — after a century of complexity, this IS the radical gesture
```

## Diatonic Simplicity

| Mode | Character | Common Use |
|------|-----------|------------|
| C major (Ionian) | Bright, pure | Glass, Adams |
| D Dorian | Warm, neutral | Reich, Glass |
| E Phrygian | Dark, Spanish | Part |
| A Aeolian (natural minor) | Solemn, gentle sadness | Part, Gorecki |
| F Lydian | Luminous, floating | Adams |
| G Mixolydian | Grounded, earthy | Riley, Reich |

```abc
X:1
T:Diatonic Harmony - Slow Chord Evolution
M:4/4
L:1/1
K:C
[CEG] | [CEG] | [CEG] | [CEGA] | [DFAC] | [DFAC] | [DFAC] | [DFAc] |
```

## Additive Harmony

| Step | Process | Result |
|------|---------|--------|
| 1 | Single pitch sustained | Unison / octave |
| 2 | Add 5th above | Open 5th |
| 3 | Add 3rd | Triad |
| 4 | Add 7th or 2nd | Extended chord |
| 5 | Change one pitch by step | New chord |
| 6 | Continue single-pitch changes | Gradual progression |

```abc
X:2
T:Additive Harmony Process
M:4/4
L:1/1
K:C
"^Step 1"C, | "^Step 2"[C,G,] | "^Step 3"[C,E,G,] | "^Step 4"[C,E,G,B,] |
"^Step 5 (E->D)"[C,D,G,B,] | "^Step 6 (B->A)"[C,D,G,A,] |
```

## Modal Harmony

### Common Modal Progressions

| Mode | Progression | Character |
|------|-------------|-----------|
| Ionian | I - V - vi - IV | Pure, bright |
| Dorian | i - IV - i - IV | Warm oscillation |
| Aeolian | i - bVI - bVII - i | Solemn, hymn-like |
| Mixolydian | I - bVII - I - bVII | Earthy, hypnotic |
| Lydian | I - II - I - II | Floating, luminous |
| Phrygian | i - bII - i - bII | Dark, devotional |

```abc
X:3
T:Modal Oscillation (Dorian: i - IV)
M:4/4
L:1/4
K:Dm
[DAd] [DAd] [DAd] [DAd] | [GBd] [GBd] [GBd] [GBd] |
[DAd] [DAd] [DAd] [DAd] | [GBd] [GBd] [GBd] [GBd] |
```

```abc
X:4
T:Aeolian Progression (i - bVI - bVII - i)
M:4/4
L:1/2
K:Am
[A,EA] [FAc] | [GBd] [A,EA] |
[A,EA] [FAc] | [GBd] [A,EA] |
```

## Drone-Based Harmony

| Type | Description | Composer |
|------|-------------|----------|
| Pitch drone | Single sustained note | La Monte Young |
| Octave drone | Same pitch in multiple octaves | Riley, Young |
| Fifth drone | Root + 5th sustained | Indian influence |
| Shifting drone | Drone pitch changes very slowly | Feldman |
| Pulse drone | Repeated note as rhythmic drone | Reich, Glass |
| Harmonics drone | Overtones of fundamental | Young, Radigue |

```abc
X:5
T:Pulse Drone with Evolving Upper Voices
M:4/4
L:1/8
K:C
%%staves {1 2}
V:1 name="Upper"
z4 E2G2 | E2G2 A2G2 | E2G2 A2c2 | E2c2 A2G2 |
V:2 name="Drone"
C,C,C,C, C,C,C,C, | C,C,C,C, C,C,C,C, | C,C,C,C, C,C,C,C, | C,C,C,C, C,C,C,C, |
```

## Slowly Evolving Chord Progressions

| Duration Scale | Chord Changes | Effect |
|---------------|---------------|--------|
| Fast minimal | Every 2-4 bars | Glass-like arpeggiated |
| Medium | Every 8-16 bars | Gradual unfolding |
| Slow | Every 30-60 seconds | Glacial, Feldman-like |
| Very slow | Every 2-5 minutes | Drone-based, Young |
| Imperceptible | Barely noticeable change | Radigue, deep listening |

### Long-Duration Chord Map
```
Time:    0:00    1:00    2:00    3:00    4:00    5:00
Chord:   Am      Am(add9) Am7    Dm/A    Dm      Dm(add2)
Change:  ------- gradual-------- gradual -------- gradual--
```

```abc
X:6
T:Slow Evolution (one chord over many bars)
M:4/4
L:1/4
K:Am
[A,EA]4 | [A,EA]4 | [A,EA]4 | [A,EAB]4 |
[A,EAB]4 | [A,EAB]4 | [A,EBd]4 | [A,EBd]4 |
```

## Tintinnabuli Technique (Arvo Part)

| Voice | Function | Rule |
|-------|----------|------|
| M-voice (melody) | Stepwise diatonic movement | Moves by step, centers on tonic |
| T-voice (tintinnabuli) | Triad pitches only | Only plays notes of tonic triad |
| Relationship | T-voice finds nearest triad tone to M-voice | Above, below, or alternating |

### T-Voice Position Rules

| Position | Rule | Example (over M-voice D in C major) |
|----------|------|--------------------------------------|
| 1st superior | Nearest triad tone above | E |
| 2nd superior | Second-nearest triad tone above | G |
| 1st inferior | Nearest triad tone below | C |
| 2nd inferior | Second-nearest triad tone below | G (below) |
| Alternating | Alternates above/below | E, C, G, C... |

```abc
X:7
T:Tintinnabuli Technique (M-voice + T-voice)
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (Am triad)"
A E A C | E A E C |
V:2 name="M-voice (stepwise)"
A G F E | D C B, A, |
```

```abc
X:8
T:Tintinnabuli - Fur Alina Style
M:3/4
L:1/4
K:Bm
%%staves {1 2}
V:1 name="T (Bm triad: B-D-F#)"
^F D B | ^F D B |
V:2 name="M (stepwise descending)"
B A G | ^F E D |
```

## Consonance Focus

| Interval | Consonance Rating | Minimalist Usage |
|----------|-------------------|-----------------|
| Unison/Octave | Perfect | Drone, doubling |
| Perfect 5th | Perfect | Open voicing, Copland-like |
| Perfect 4th | Perfect | Quartal stacking |
| Major 3rd | Imperfect | Triadic warmth |
| Minor 3rd | Imperfect | Triadic warmth |
| Major 6th | Imperfect | Inversion of minor 3rd |
| Minor 6th | Imperfect | Inversion of major 3rd |
| Major 2nd | Mild dissonance | Added-note color, clusters |
| Minor 7th | Mild dissonance | Modal color |
| Minor 2nd | Dissonance | Rare — tension only |
| Tritone | Dissonance | Very rare in minimalism |

## Phase Relationships Creating Harmony

| Phase Offset | Harmonic Result | Texture |
|-------------|-----------------|---------|
| Unison (0) | Perfect consonance | Single pattern |
| 1 beat offset | Canonic, interlocking | Thicker, emergent harmony |
| 2 beats offset | New rhythmic/harmonic patterns | Complex resultant |
| Half-pattern offset | Maximum complexity | Densest emergent harmony |
| Near-unison (gradual) | Slowly shifting interference | Phasing process |

```abc
X:9
T:Phase Harmony - Two Voices Offset
M:4/4
L:1/8
K:C
%%staves {1 2}
V:1 name="Voice 1"
CEGC EGCE | CEGC EGCE |
V:2 name="Voice 2 (offset by 1 eighth)"
z CEGC EGCE | CEGC EGCz |
```

## Harmonic Rhythm in Minimalism

| Tempo | Bars per Chord | Application |
|-------|---------------|-------------|
| Very fast | 16-32 bars | Glass early (rapid arpeggio, slow change) |
| Fast | 8-16 bars | Reich, Adams |
| Moderate | 4-8 bars | Adams, late Glass |
| Slow | 1-2 bars | Post-minimal (Muhly, Richter) |
| None | Entire piece on one chord/mode | La Monte Young, early Riley |

## Chord Voicing Preferences

| Voicing | Character | Composer Association |
|---------|-----------|---------------------|
| Root position triads | Grounded, simple | Part, Gorecki |
| Open 5ths (no 3rd) | Hollow, spacious | Adams, Part |
| First inversion triads | Flowing, less stable | Glass (arpeggios) |
| Widely spaced | Vast, resonant | Feldman, Adams |
| Close-position cluster | Bell-like, ringing | Part (tintinnabuli) |
| Octave doubling | Reinforced, powerful | Gorecki Symphony 3 |

```abc
X:10
T:Voicing Comparison
M:4/4
L:1/1
K:C
"^Root pos"[CEG] | "^Open 5th"[C,G,] | "^1st inv"[EGc] |
"^Wide"[C,Gc'] | "^Close cluster"[CDE] | "^Octave dbl"[C,CEGce] |
```

## Harmonic Application Guide

| Emotional Target | Harmony Choice | Mode | Tempo of Change |
|-----------------|---------------|------|-----------------|
| Serenity | Open triads, slow evolution | Major, Lydian | Very slow |
| Devotion | Tintinnabuli, drone | Aeolian, Dorian | Slow |
| Energy | Arpeggiated triads, phase | Major, Mixolydian | Fast pattern, slow change |
| Meditation | Single chord, pulse drone | Any mode | None/imperceptible |
| Grief | Minor triads, stepwise bass | Aeolian, Phrygian | Slow |
| Joy | Bright triads, additive buildup | Major, Lydian | Moderate |
| Transcendence | Gradual build to consonance | Major | Very slow evolution |
