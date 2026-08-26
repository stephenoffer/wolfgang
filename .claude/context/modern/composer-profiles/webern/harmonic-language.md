# Anton Webern — Harmonic Language

Webern's harmony is pointillism: isolated intervals placed in silence, each resonating alone before the next arrives. There are no chords in the traditional sense — only intervals, and the spaces between them. In the serial works, the twelve-tone row determines all pitch relationships, but Webern designs his rows for maximum intervallic purity: symmetrical, self-inverting, built from a small number of interval classes that recur at every level of the structure.

For shared modern harmonic vocabulary (twelve-tone method, set theory), see [modern-harmony.md](../../modern-harmony.md). This file covers what is distinctly Webernian.

## Core Harmonic Character by Period

| Feature | Early Tonal (1904–08) | Free Atonal (1908–24) | Serial (1924–43) |
|---------|----------------------|----------------------|-------------------|
| Tonal center | Present; Brahmsian | None; all intervals equal | None; row-determined |
| Vertical sonority | Triads, extended chords | Isolated intervals (m2, M3, tritone) | Row segments as simultaneities |
| Density | Moderate; chamber | Extremely sparse | Sparse; 1–3 notes at a time |
| Spacing | Standard | Extreme: wide leaps between adjacent notes | Extreme: register as structural parameter |
| Duration of events | Normal | Very short; staccato default | Short to moderate |

## Intervallic Cells

Webern's harmony is built from a small number of favored interval classes, especially the minor 2nd (ic1), major 3rd (ic4), and their inversions.

| Interval Class | Intervals | Webern's Use | Character |
|---------------|-----------|-------------|-----------|
| ic1 | Minor 2nd / Major 7th | Primary tension; the Webern "sting" | Concentrated pain, intensity |
| ic2 | Major 2nd / Minor 7th | Secondary; moderate tension | Less frequent |
| ic3 | Minor 3rd / Major 6th | Occasional; octatonic reference | Dark warmth |
| ic4 | Major 3rd / Minor 6th | Primary consonance; paired with ic1 | Beauty within strictness |
| ic5 | Perfect 4th / Perfect 5th | Structural; open | Rare in melody; structural in harmony |
| ic6 | Tritone | Axis of symmetry | Central to row design |

```abc
X:1
T:Webern Intervallic Cells — ic1 and ic4
M:3/4
L:1/4
K:C clef=treble
%% ic1 (minor 2nd) followed by ic4 (major 3rd): the Webern pairing
!ppp!B z ^G|z E z|_D z _B,|z z z|
%% B-C (ic1), then G#-E (ic4) — tension and consonance alternating
```

## Symmetrical Row Design

Webern designs rows that are their own retrograde-inversion, or that generate their inversion from internal symmetry. This means fewer distinct row forms — a more unified, crystalline structure.

| Row Property | Description | Effect |
|-------------|-------------|--------|
| Self-inverting | I-form at some transposition = P-form | Fewer distinct row forms; maximum unity |
| Derived row | Row built from a single trichord (3-note cell) transposed/inverted | All material from one cell |
| Palindromic | Row reads the same forwards and backwards | Non-retrogradable; temporal symmetry |
| Trichordal construction | Row = 4 transformations of a 3-note cell | Maximum motivic unity |

### Example: Concerto Op. 24 Row

The row of the Concerto Op. 24 is built entirely from one trichord: B-Bb-D. The row = P + RI + R + I of this cell.

| Segment | Pitches | Transformation |
|---------|---------|---------------|
| 1–3 | B Bb D | Prime (P) |
| 4–6 | Eb G F# | Retrograde Inversion (RI) |
| 7–9 | G# E F | Retrograde (R) |
| 10–12 | C C# A | Inversion (I) |

```abc
X:2
T:Concerto Op. 24 Row — Derived from Single Trichord
M:4/4
L:1/8
K:C clef=treble
%% B-Bb-D (P) | Eb-G-F# (RI) | G#-E-F (R) | C-C#-A (I)
B _B D|_E G ^F|^G E F|C ^C A|
%% Every 3-note group is a transformation of B-Bb-D
```

## Harmony as Register

In Webern, register IS harmony. The same pitch class in different octaves produces a completely different harmonic effect. A C3 next to a B5 creates vast space; a C4 next to a B4 creates compression.

| Register Strategy | Description | Effect |
|------------------|-------------|--------|
| Wide dispersal | Adjacent row pitches placed 2–3 octaves apart | Open, crystalline; each note isolated |
| Close compression | Adjacent row pitches in same octave | Dense, tense; cluster-like |
| Registral symmetry | Pitches placed symmetrically around a central axis | Mirror harmony; Bartok-influenced |
| Extreme register | Notes at the very top (C7) or very bottom (C1) | Ethereal or ominous; boundary-touching |

```abc
X:3
T:Register as Harmony — Same Pitches, Different Spacing
M:4/4
L:1/4
K:C clef=treble
%% Compressed (same octave):
!pp!C B, _E ^F|
%% Dispersed (different octaves — imagine these spread across 3 octaves):
!ppp!C,, z B z|_E' z ^F,, z|
%% Same 4 pitch classes — completely different harmonic experience
```

## Vertical Sonorities (Chords)

Webern rarely writes traditional "chords." When multiple notes sound simultaneously, they are row segments stacked vertically.

| Sonority Type | Construction | Where |
|--------------|-------------|-------|
| Dyad (2 notes) | Two row-adjacent pitches stacked | Most common; Op. 21, 27 |
| Trichord (3 notes) | Three row-adjacent pitches stacked | Op. 24, Op. 28 |
| Tetrachord (4 notes) | Four row-adjacent pitches stacked | Rare; climactic moments |
| Full aggregate | All 12 pitches in close succession | Structural punctuation |

## Harmonic Rhythm

| Context | Speed | Character |
|---------|-------|-----------|
| Pointillistic passage | Very slow: 1 note every 2–4 beats | Each note resonates in silence |
| Canonic passage | Moderate: notes at regular intervals | Architecturally regular |
| Climactic | Faster: notes compressed | Maximum density (for Webern = 3–4 notes close together) |
| Silence | Rest: 2–8 beats | As important as any note |

## Voice-Leading

| Principle | Description |
|-----------|-------------|
| No parallel motion | Each voice completely independent |
| Wide leaps preferred | Stepwise motion is rare; intervals of 6th–9th common |
| Register as voice identity | A "voice" occupies a specific register; crossing is structural |
| Silence between notes | A voice's notes are separated by rests |
| Canon as voice-leading | Two or more voices state the same row in staggered entries |

## Pedal and Resonance

| Technique | Description | Where |
|-----------|-------------|-------|
| Sustained harp tone | Single harp note sustaining while others move | Op. 21 |
| Piano pedal resonance | Sustain pedal held; notes resonate together | Op. 27 |
| Bell-like decay | Note struck, then silence; the decay IS the music | Throughout |
| No sustained chords | Instruments do not hold chords; they play single notes that decay | All serial works |

## References

- [composition-guide.md](composition-guide.md) — Fingerprints #1 (brevity), #2 (pointillism), #5 (strict serial)
- [melodic-style.md](melodic-style.md) — Row as dispersed melody
- [orchestration.md](orchestration.md) — How intervals distribute across instruments
- [formal-approach.md](formal-approach.md) — Row symmetry as formal architecture
- [../../modern-harmony.md](../../modern-harmony.md) — Twelve-tone technique reference

---

## Cadences and closure

Twelve-tone music has no cadence. What ends a Webern phrase is the completion of
a row, a registral fixing, and silence — and these are structural, not
decorative.

| Closure device | Construction | Where it belongs | Effect |
|----------------|--------------|------------------|--------|
| Row completion | The aggregate finishes; all twelve pitch classes have sounded | Phrase and section ends | Structural closure |
| Symmetrical arrival | The row's palindromic centre lands on a fixed register | Formal centres | Balance |
| Registral fixing | A pitch returns to the exact octave it held earlier | Movement ends | Recognition, place |
| Silence | A rest longer than any note in the phrase | Between everything | The primary punctuation |
| Dynamic extinction | ppp on an isolated single note | Movement ends | Vanishing |
| Klangfarben cadence | The final gesture passed between three instruments | Ends of variations | Dissolution of the line |

Silence is not the absence of the music here; it is the strongest event in it.
Writing continuous texture destroys the idiom completely.
