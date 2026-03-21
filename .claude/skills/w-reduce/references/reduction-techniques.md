# Reduction & Arrangement Techniques — w-reduce

## Piano Reduction Principles

Piano reduction distills a multi-instrument score to two staves. The goal is **playability** while preserving musical essence.

### Priority Hierarchy for Voice Selection

| Priority | Element               | Rationale                                    |
|----------|-----------------------|----------------------------------------------|
| 1        | Melody (top voice)    | Primary identity of the music                |
| 2        | Bass line             | Harmonic foundation                          |
| 3        | Harmonic pillars      | Chord identity (3rd, 7th, chromatic tones)   |
| 4        | Counter-melodies      | Include when hands allow                     |
| 5        | Inner voice motion    | Simplify to block chords when necessary      |
| 6        | Doublings             | Omit unless timbral (e.g., octave melody)    |
| 7        | Pedal tones           | Sustain pedal can maintain; simplify notation|
| 8        | Ornamental figuration | Simplify or omit; preserve character         |

### Decision Framework

```
Is voice carrying melody?        → ALWAYS KEEP
Is voice carrying bass?          → ALWAYS KEEP
Is voice providing unique pitch? → KEEP if hand allows
Is voice doubling at unison?     → OMIT
Is voice doubling at octave?     → KEEP one octave only
Is voice purely textural?        → SIMPLIFY or OMIT
```

## Orchestral to Piano: Voice Allocation

### Right Hand (treble staff)

| Source                     | Treatment                              |
|----------------------------|----------------------------------------|
| Melody instrument          | Direct transfer; preserve rhythm       |
| Woodwind doublings at 8va  | Omit unless melody is in winds only    |
| High sustained strings     | Simplify to chord tones on beats       |
| Harp arpeggios             | Preserve if idiomatic for piano        |
| Tremolo strings            | Convert to tremolo or repeated chords  |

### Left Hand (bass staff)

| Source                  | Treatment                                 |
|-------------------------|-------------------------------------------|
| Bass instruments        | Direct transfer                           |
| Cello melody            | Transfer; may need RH if range overlaps   |
| Low brass chords        | Simplify to root + 5th or root + 3rd      |
| Timpani rolls           | Tremolo or repeated notes                 |
| Contrabass + cello      | Single bass line (cello part preferred)   |

### Shared / Crossed Hands

| Situation                        | Solution                                     |
|----------------------------------|----------------------------------------------|
| Cello melody above LH chords    | Cross hands or move melody to RH             |
| Wide spacing (bass + high melody)| Arpeggio fill or accept gap                  |
| Three distinct voices            | RH: melody + alto, LH: bass                 |
| Four distinct voices             | SATB chorale style                           |

## Hand Span and Playability Limits

| Constraint                    | Limit                                          |
|-------------------------------|------------------------------------------------|
| Maximum comfortable span      | 9th (C to D, one octave up) for average hand   |
| Maximum stretch span          | 10th (occasional, not sustained)               |
| Chord density (RH)            | 4 notes max in close position                  |
| Chord density (LH)            | 3-4 notes; wider intervals below middle C      |
| Repeated chord speed          | Up to 16ths at ~120 BPM comfortably            |
| Octave passage speed          | Up to 8ths at ~132 BPM                         |
| Thumb-under passages          | Smooth at moderate tempo; awkward in fast runs  |
| Black-key chord limit         | Avoid 4+ black keys simultaneously             |

### Register Considerations

| Register             | Best Use                                  | Avoid                          |
|----------------------|-------------------------------------------|--------------------------------|
| Below C2             | Single bass notes, octaves                | Chords (muddy)                 |
| C2-C3                | Bass + 5th, open voicing                  | Close-position triads          |
| C3-C4                | Full chords, LH melody                    | Dense chromatic clusters       |
| C4-C6                | Primary melodic + harmonic range          | Nothing specific               |
| Above C6             | Melodic highlights, trills                | Thick chords (thin sound)      |

## Pedaling Notation in Reductions

| Pedal Type    | Notation          | Use Case                                    |
|---------------|-------------------|---------------------------------------------|
| Sustain       | `Ped.` / `*`      | Sustain bass while hands move; legato chords|
| Half-pedal    | `1/2 Ped.`        | Partial sustain for clarity in dense texture|
| Sostenuto     | `Sost. Ped.`      | Hold specific bass note while playing above |
| Una corda     | `u.c.` / `t.c.`   | Soft color, pp passages                     |

## Piano to Orchestral: Texture Expansion

### Melody Assignment

| Piano Texture          | Orchestral Expansion                                    |
|------------------------|---------------------------------------------------------|
| Single-line melody     | Solo instrument or unison section                       |
| Octave melody          | Doubled instruments (fl+ob, vln I+II)                   |
| Chordal melody (top)   | Melody in winds, harmony in strings (or reverse)       |
| Broken chord melody    | Arpeggiated strings or harp + sustained wind melody     |

### Accompaniment Expansion

| Piano Pattern          | Orchestral Equivalent                                   |
|------------------------|---------------------------------------------------------|
| Alberti bass           | Violas/cellos broken chord; or string tremolo           |
| Block chords           | Brass chorale, or string pizzicato                      |
| Arpeggios              | Harp, or divided strings, or woodwind arpeggios         |
| Tremolo                | String tremolo (measured or unmeasured)                 |
| Repeated octaves       | Timpani + low strings, or brass accents                 |
| LH melody + RH chords | Cello/viola melody + wind chords                        |
| Running passages       | Strings or flute/clarinet, depending on character       |

### Dynamic Scaling: Piano to Orchestra

| Piano Dynamic | Orchestral Equivalent                              |
|---------------|----------------------------------------------------|
| ppp           | Solo string, con sordino                           |
| pp            | Solo wind or muted strings section                 |
| p             | Light strings + one wind color                     |
| mp            | Strings + woodwinds                                |
| mf            | Full strings + winds, light brass                  |
| f             | Full winds + strings + horns                       |
| ff            | Full orchestra                                     |
| fff           | Full orchestra + percussion, tutti                 |

## Preserving Harmonic Content

### Essential Tones to Retain

| Chord Type          | Must Keep              | Can Omit          |
|---------------------|------------------------|-------------------|
| Major/minor triad   | Root, 3rd              | 5th (if needed)   |
| Dominant 7th        | Root, 3rd, 7th         | 5th               |
| Diminished 7th      | All tones              | None              |
| Aug 6th chords      | Augmented 6th interval | Inner voices      |
| Suspended           | Root, 4th (or 2nd)     | 5th               |
| 9th/11th/13th       | Root, 3rd, 7th, color  | 5th, doubled root |
| Neapolitan          | All (bII is identity)  | None              |

### Voice Leading in Reduction

```
Preserve:
  - Chromatic motion in any voice
  - Suspensions and resolutions
  - Contrary motion between outer voices
  - Leading tone resolution

Simplify:
  - Parallel doubling voices → single voice
  - Pedal tones → sustain pedal
  - Repeated-note accompaniment → simplified rhythm
```

## Chamber Ensemble Reductions

### String Quartet to Piano

| SQ Voice   | Piano Allocation                          |
|------------|-------------------------------------------|
| Violin I   | RH top voice                              |
| Violin II  | RH inner voice or LH top voice            |
| Viola       | LH top voice or RH bottom voice          |
| Cello       | LH bass                                  |

Special cases:
- Cello melody above viola: move to RH, shift other voices
- Violin I above staff: keep in RH, accept wide spacing
- Fugal entries: preserve all voices; use 4-part keyboard texture

### Piano to String Quartet

| Piano Element           | SQ Assignment                               |
|-------------------------|---------------------------------------------|
| RH melody               | Violin I                                   |
| RH inner voice          | Violin II                                  |
| LH upper voice          | Viola                                      |
| LH bass                 | Cello                                      |
| Arpeggiated chords      | Distribute across all four, or tremolo     |
| Octave doublings        | Vln I + Cello (or Vln I + Vln II)         |
| Thick chords (5+ notes) | Reduce to 4 voices; omit doublings         |
| Pedal sustained notes   | Cello or viola drone                       |

## Special Instrument Effects: Piano Equivalents

| Orchestral Effect      | Piano Equivalent                            | ABC Notation          |
|------------------------|---------------------------------------------|-----------------------|
| Pizzicato              | Staccato, dry (no pedal)                    | notes with `.`        |
| Tremolo (bowed)        | Tremolo or trill                            | `!trill!` or rolls    |
| Tremolo (fingered)     | Same fingered tremolo                       | measured alternation  |
| Con sordino            | Una corda pedal + pp                        | `!pp!` + `u.c.`      |
| Harmonics              | High register pp, no pedal                  | high octave + `!pp!`  |
| Col legno              | Very dry staccato ppp                       | `.` + `!ppp!`         |
| Sul ponticello         | Tremolo pp (glassy quality cannot replicate)| `!trill!` + `!pp!`   |
| Glissando              | Glissando (idiomatic on piano)              | gliss marking         |
| Double stops           | Direct transfer (idiomatic)                 | chords                |
| Brass sforzando        | Sforzando accent                            | `!sfz!`               |
| Horn call              | RH melody forte, detached                   | `!f!` + detached      |
| Woodwind trills        | Trills (idiomatic on piano)                 | `!trill!`             |
| Harp glissando         | Glissando (very idiomatic)                  | gliss marking         |
| Timpani roll           | LH tremolo on single note or octave        | measured tremolo      |

## Maintaining Dynamic Arc in Reduction

### Principles

1. **Map orchestral dynamics to piano dynamics** — ff tutti != piano ff; scale relatively
2. **Texture density substitutes for volume** — thicker chords = louder
3. **Register placement affects perceived dynamics** — lower = heavier, higher = brighter
4. **Articulation reinforces dynamics** — marcato for ff, legato for p

### Dynamic Mapping When Reducing Ensemble Size

| Full Orchestra | Chamber (10 players) | Piano Solo | Piano 4-hands |
|----------------|----------------------|------------|----------------|
| ppp            | pp                   | ppp        | ppp            |
| pp             | pp                   | pp         | pp             |
| p              | p                    | p          | p              |
| mp             | mp                   | mp         | mp             |
| mf             | mf                   | mf         | mf             |
| f              | f                    | f          | f              |
| ff             | f+                   | ff         | ff             |
| fff            | ff                   | fff        | fff            |

## Re-Orchestration Guidelines

### Expanding Ensemble Size

| From             | To                     | Strategy                                     |
|------------------|------------------------|----------------------------------------------|
| Solo instrument  | Chamber (3-5)          | Add harmonic support + bass                  |
| Piano            | String quartet         | Voice extraction (see above)                 |
| String quartet   | Chamber orchestra      | Double strings, add winds for color          |
| Chamber orch     | Full orchestra         | Add brass, percussion, double winds          |
| Small orchestra  | Large orchestra        | Triple winds, expand brass, add harp/perc    |

### Reducing Ensemble Size

| From             | To                     | Strategy                                     |
|------------------|------------------------|----------------------------------------------|
| Full orchestra   | Chamber orchestra      | Priority voices only; single winds           |
| Full orchestra   | String quartet         | Melody, bass, 2 inner voices                |
| Full orchestra   | Piano                  | See orchestral-to-piano section above        |
| Chamber orch     | Piano trio             | Melody (vln), bass (cello), harmony (piano) |
| String orchestra | Solo piano             | Outer voices + essential harmony             |

### When Reducing, Always Preserve

- Thematic material (primary and secondary themes)
- Bass line contour and harmonic rhythm
- Dynamic shape of phrases
- Formal landmarks (cadences, transitions, climaxes)
- Character-defining rhythmic patterns
- Tempo relationships between sections

### When Reducing, Acceptable to Simplify

- Inner voice doublings (keep one of each pitch)
- Textural figuration (simplify repeated patterns)
- Sustained tones (use ties or pedal instead of held instruments)
- Percussion coloristic effects (omit or approximate)
- Rapid passage doublings (keep most idiomatic version)
