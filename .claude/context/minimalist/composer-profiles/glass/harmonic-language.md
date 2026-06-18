# Philip Glass — Harmonic Language

## Core Principle: Modal Cycling, Not Functional Progression

Glass's harmony circulates through a small set of diatonic chords without direction or resolution. The harmony has no goal — it cycles. There is no dominant-tonic tension, no resolution, no cadence in the Classical sense.

## Harmonic Vocabulary

| Element | Description |
|---------|-------------|
| Chord types | Major and minor triads; occasional sus4 or add2 |
| Chords per cue | 3–4, rarely more |
| Mode | Dorian and Aeolian most common; Ionian for brightness |
| Chromatic notes | None — purely diatonic within chosen mode |
| Functional harmony | Absent — no V→I, no secondary dominants |
| Harmonic rhythm | Slow: each chord lasts 4–8 bars (or longer) |

## Characteristic Modal Progressions

| Mode | Progression | Character | Works |
|------|-------------|-----------|-------|
| D Dorian | Dm → C → Bb → Am → (repeat) | Warm, cycling | *Glassworks: Opening* |
| A Aeolian | Am → G → F → Em → (repeat) | Solemn, gentle | *Metamorphosis* series |
| C Ionian | C → Em → F → G → (repeat) | Bright, luminous | *The Hours* |
| E Phrygian | Em → F → Dm → Em → (repeat) | Dark, Spanish | *Akhnaten* passages |
| F Lydian | F → G → Am → F → (repeat) | Floating, radiant | Late symphonic works |

```abc
X:1
T:Dorian Modal Cycle (Glassworks style)
M:4/4
L:1/8
K:Dm
%% Dm chord arpeggiated (4 bars)
DFAD FADF | DFAD FADF | DFAD FADF | DFAD FADF |
%% C chord arpeggiated (4 bars)
CEGC EGCE | CEGC EGCE | CEGC EGCE | CEGC EGCE |
% Each chord lasts 4 full bars — the cycle, not the chord change, is the content
```

## The Arpeggio as Harmony

In Glass, harmony is not presented as block chords — it is embedded in arpeggiated patterns. The chord IS the arpeggio:

| Chord | Arpeggio Pattern | Effect |
|-------|-----------------|--------|
| Dm | D-F-A-D-F-A-D-F | Minor warmth, continuous motion |
| C | C-E-G-C-E-G-C-E | Bright lift |
| Bb | Bb-D-F-Bb-D-F-Bb-D | Darkening |
| Am | A-C-E-A-C-E-A-C | Solemn return |

```abc
X:2
T:Arpeggio as Harmony — Four Chords
M:4/4
L:1/16
K:Dm
DFAD FADF ADFA DFAD | CEGC EGCE GCEG CEGC |
_BBDF _BDFB D_BF_B DF_BD | ACEA CEAC EACE ACEA |
% The harmony lives inside the arpeggio pattern — no block chords needed
```

## Harmonic Stasis vs. Harmonic Cycling

| Approach | Description | Effect |
|----------|-------------|--------|
| Single-chord stasis | One chord for 16–64 bars | Deep immersion in one sonority |
| Two-chord oscillation | Alternating between two chords | Gentle rocking; breathing |
| Three-chord cycle | i → bVII → bVI → (repeat) | Forward momentum without goal |
| Four-chord cycle | i → bVII → bVI → v → (repeat) | Maximum Glass cyclic effect |

## Chord Transition Technique

| Transition | Method | Example |
|-----------|--------|---------|
| Smooth | Change one note in the arpeggio pattern | D-F-A → C-E-G by moving D→C, F→E, A→G |
| Pivot | One common tone held while others shift | Am (A-C-E) → F (F-A-C): A is pivot |
| Direct | All notes change at bar boundary | Clean cut between chords |
| Additive | One note changes per bar over 2–3 bars | Gradual transformation |

```abc
X:3
T:Smooth Chord Transition — One Note at a Time
M:4/4
L:1/8
K:Am
%% Am arpeggio
ACEA CEAC |
%% Transition: E becomes D (Am → Dm/A)
ACDA CDAC |
%% Full Dm
DFAD FADF |
% The chord melts from Am to Dm by changing one note
```

## Harmonic Rhythm

| Context | Chord Duration | Surface Speed |
|---------|---------------|---------------|
| Early process pieces | 16–64 bars per chord | Fast eighths/sixteenths |
| Opera (Einstein) | 8–16 bars per chord | Fast arpeggiated |
| Glassworks | 4–8 bars per chord | Medium arpeggiated |
| Film scores (The Hours) | 2–4 bars per chord | Moderate piano figuration |
| Late symphonies | 2–8 bars per chord | Varied orchestral |

**The Glass ratio:** Surface speed FAST (eighth or sixteenth notes), harmonic change SLOW (every 4–8+ bars). This ratio creates the hypnotic effect.

## Bass Treatment

| Type | Description | Works |
|------|-------------|-------|
| Root on beat 1 | Single bass note anchoring each bar | Most keyboard works |
| Pedal bass | Same bass note sustained across chord changes | *Koyaanisqatsi* |
| Walking stepwise bass | Bass moves by step every 4–8 bars | Late orchestral works |
| Absent bass | No bass; arpeggio floats without ground | Some *Metamorphosis* passages |

## Key Relationships Between Sections

| Relationship | Distance | Effect | Example |
|-------------|----------|--------|---------|
| Same key | Unison | Continuity | Most sections within a movement |
| Step up | M2 | Gentle brightening | Dm → Em between sections |
| Step down | M2 | Gentle darkening | C → Bb between sections |
| Third relation | m3/M3 | Modal shift, new color | Am → C (relative major) |
| Direct modulation | Any | Abrupt scene change | Opera scene transitions |

## Dissonance Treatment

| Dissonance | Usage | Context |
|-----------|-------|---------|
| Passing tones | Within arpeggio patterns (brief) | Added-note chords |
| Suspensions | Note held from previous chord into new one | Chord transitions |
| Clusters | Very rare — late period only | Dramatic moments in operas |
| Tritones | Absent | Not part of Glass's vocabulary |
| Chromaticism | Absent in early/middle; slight in late period | Late symphonies only |

```abc
X:4
T:Glass Harmonic Language — Complete Cycle
M:4/4
L:1/8
K:Am
%%staves {1 2}
V:1 name="RH (arpeggio)"
ACEA CEAC | GBDG BDGB | FACF ACFA | EGBE GBEG |
V:2 name="LH (bass)"
A,4 z4 | G,4 z4 | F,4 z4 | E,4 z4 |
% Am → G → F → Em: the complete Aeolian descent cycle
```

## References
- Glass, Philip. *Words Without Music: A Memoir*, 2015
- Potter, Keith. *Four Musical Minimalists* (Glass chapter), 2000
- Schwarz, K. Robert. *Minimalists*, 1996
