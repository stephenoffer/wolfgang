# Tempo and Expression Markings Reference

## Standard Tempo Markings

| Marking | BPM Range | Character | Typical Usage |
|---------|-----------|-----------|---------------|
| Grave | 20-40 | Solemn, heavy | Introductions, funeral |
| Largo | 40-60 | Broad, very slow | Slow movements, pathos |
| Larghetto | 60-66 | Rather broad | Slightly moving slow mvt |
| Adagio | 66-76 | Slow, at ease | Slow movements, arias |
| Andante | 76-108 | Walking pace | Moderate slow movements |
| Andantino | 80-108 | Slightly faster than Andante | Light, gentle |
| Moderato | 108-120 | Moderate | Default, neutral |
| Allegretto | 112-120 | Moderately fast | Light, cheerful |
| Allegro | 120-156 | Fast, lively | Fast movements, sonata |
| Vivace | 156-176 | Lively, brisk | Energetic fast movements |
| Presto | 168-200 | Very fast | Finales, virtuosic |
| Prestissimo | 200+ | As fast as possible | Extreme passages |

### ABC Q: Field Syntax

```abc
Q:1/4=120
```
Sets quarter note = 120 BPM. Always specify the beat unit.

| ABC Q: Field | Meaning |
|-------------|---------|
| `Q:1/4=60` | Quarter = 60 (Largo) |
| `Q:1/4=72` | Quarter = 72 (Adagio) |
| `Q:1/4=92` | Quarter = 92 (Andante) |
| `Q:1/4=120` | Quarter = 120 (Allegro) |
| `Q:1/4=144` | Quarter = 144 (Allegro vivace) |
| `Q:1/4=176` | Quarter = 176 (Presto) |
| `Q:3/8=60` | Dotted quarter = 60 (compound meter) |
| `Q:1/2=60` | Half note = 60 (alla breve) |
| `Q:"Andante" 1/4=84` | Named tempo with BPM |

```abc
X:1
T:Tempo marking example
M:4/4
L:1/8
Q:"Allegro con brio" 1/4=138
K:C
CDEF GABc|defg agfe|
```

## Character / Expression Markings

### Mood and Character

| Marking | Translation | Musical Implication |
|---------|-------------|-------------------|
| Dolce | Sweetly | Soft, legato, warm tone |
| Cantabile | Singing | Lyrical, sustained melody |
| Espressivo (espr.) | Expressively | Rubato allowed, emotional |
| Con fuoco | With fire | Intense, forceful, fast |
| Con brio | With spirit | Energetic, bright |
| Maestoso | Majestic | Broad, stately, weighty |
| Grazioso | Gracefully | Light, elegant |
| Agitato | Agitated | Restless, turbulent |
| Tranquillo | Tranquil | Calm, peaceful |
| Appassionato | Passionately | Intense emotion |
| Scherzando | Playfully | Light, humorous |
| Misterioso | Mysteriously | Soft, veiled |
| Brillante | Brilliantly | Bright, sparkling |
| Pesante | Heavy | Weighted, deliberate |
| Leggiero | Lightly | Delicate touch |
| Giocoso | Joyfully | Playful, humorous |
| Furioso | Furiously | Violent, wild |
| Lamentoso | Mournfully | Sad, lamenting |
| Risoluto | Resolutely | Firm, decisive |
| Semplice | Simply | Without affectation |
| Animato | Animated | Lively, spirited |
| Morendo | Dying away | Gradually softer and slower |
| Perdendosi | Losing itself | Fading to nothing |

### Applying Character in ABC

Use `%%text` directives or embed in title/subtitle:
```abc
X:1
T:Nocturne
M:3/4
L:1/8
Q:"Andante cantabile" 1/4=72
K:Eb
```

## Tempo Modification Markings

| Marking | Abbreviation | Effect | Duration |
|---------|-------------|--------|----------|
| Ritardando | rit. | Gradually slower | Until a tempo |
| Rallentando | rall. | Gradually slower | Until a tempo |
| Accelerando | accel. | Gradually faster | Until a tempo or new tempo |
| A tempo | a tempo | Return to original tempo | From this point |
| Rubato | rubato | Flexible tempo (push/pull) | Section or phrase |
| Stringendo | string. | Pressing forward (faster + louder) | Until climax or new tempo |
| Allargando | allarg. | Broadening (slower + louder) | Until cadence or new tempo |
| Calando | cal. | Decreasing (slower + softer) | Until new instruction |
| Ritenuto | riten. | Immediately slower (held back) | Until a tempo |
| Meno mosso | meno mosso | Less motion (slower) | New tempo section |
| Piu mosso | piu mosso | More motion (faster) | New tempo section |
| Tempo primo | Tempo I | Original tempo | From this point |
| Fermata | ^ | Hold note beyond value | Single note/rest |
| Cesura | // | Brief silence (breath) | Between notes |
| L'istesso tempo | l'ist. tempo | Same tempo (when meter changes) | New meter section |

### ABC Tempo Modification

```abc
X:2
T:Tempo modifications
M:4/4
L:1/4
Q:"Allegro" 1/4=132
K:C
CDEF|GABc|!rit.!dcBA|!fermata!G4|
Q:"a tempo" 1/4=132
CDEF|GABc|
```

Fermata in ABC: `!fermata!C4` or `HC4` (older syntax).

## Metronome Conventions by Period

| Period | Convention | Notes |
|--------|-----------|-------|
| Baroque | No metronome marks | Tempo from dance type and affect; tactus convention |
| Classical | Rare; Beethoven among first | Often debated; some markings seem too fast |
| Romantic | Common | Flexibility expected; rubato is norm |
| 20th Century | Precise | Stravinsky, Bartok: strict; others: approximate |
| Film Score | Exact (sync to picture) | Usually to the frame; click track |

### Baroque Tempo by Dance

| Dance | Approximate BPM (quarter) | Character |
|-------|--------------------------|-----------|
| Allemande | 80-100 | Moderate, flowing |
| Courante | 120-140 | Running, quick |
| Sarabande | 50-66 | Slow, stately |
| Gigue | 120-160 | Fast, lively |
| Minuet | 108-120 | Moderate, graceful |
| Gavotte | 108-120 | Moderate, cheerful |
| Bourree | 120-140 | Quick, earthy |

## Tempo Relationships Between Movements

### Symphony (4-movement)

| Movement | Typical Tempo | Typical Marking | BPM Range |
|----------|--------------|-----------------|-----------|
| I | Fast (after slow intro) | Allegro / Allegro con brio | 120-152 |
| II | Slow | Adagio / Andante / Largo | 50-92 |
| III | Moderate-fast | Menuetto/Scherzo: Allegretto-Presto | 100-176 |
| IV | Fast-very fast | Allegro / Presto / Vivace | 132-200 |

### Concerto (3-movement)

| Movement | Typical Tempo | BPM Range |
|----------|--------------|-----------|
| I | Fast | 120-144 |
| II | Slow | 50-84 |
| III | Very fast | 132-176 |

### Sonata (3-4 movements)

| Movement | Typical Tempo | BPM Range |
|----------|--------------|-----------|
| I | Allegro | 120-144 |
| II | Adagio/Andante | 50-92 |
| III (opt.) | Scherzo/Minuet | 100-160 |
| IV | Allegro/Presto | 132-200 |

### Suite (Baroque, variable)

Follow dance tempo conventions above. Movements typically alternate slow-fast.

## Dynamic Markings

| Marking | Name | Relative Level | MIDI Velocity (approx) |
|---------|------|---------------|----------------------|
| ppp | Pianississimo | Extremely soft | 16 |
| pp | Pianissimo | Very soft | 33 |
| p | Piano | Soft | 49 |
| mp | Mezzo-piano | Moderately soft | 64 |
| mf | Mezzo-forte | Moderately loud | 80 |
| f | Forte | Loud | 96 |
| ff | Fortissimo | Very loud | 112 |
| fff | Fortississimo | Extremely loud | 127 |
| sfz | Sforzando | Sudden accent | Spike to f/ff |
| fp | Forte-piano | Loud then immediately soft | f then p |
| fz | Forzando | Strong accent | Spike |
| rf/rfz | Rinforzando | Reinforced accent | Brief increase |
| cresc. | Crescendo | Gradually louder | Ramp up |
| decresc./dim. | Decrescendo/Diminuendo | Gradually softer | Ramp down |
| sotto voce | Under the voice | Very soft, subdued | pp-p |
| mezza voce | Half voice | Moderate, restrained | p-mp |

### ABC Dynamic Notation

| Dynamic | ABC Syntax |
|---------|-----------|
| ppp | `!ppp!` |
| pp | `!pp!` |
| p | `!p!` |
| mp | `!mp!` |
| mf | `!mf!` |
| f | `!f!` |
| ff | `!ff!` |
| fff | `!fff!` |
| sfz | `!sfz!` |
| crescendo start | `!crescendo(!` or `!<(!` |
| crescendo end | `!crescendo)!` or `!<)!` |
| diminuendo start | `!diminuendo(!` or `!>(!` |
| diminuendo end | `!diminuendo)!` or `!>)!` |

```abc
X:3
T:Dynamic markings example
M:4/4
L:1/8
K:C
!pp!CDEF !<(!GABc|!<)!!f!defg !>(!agfe|!>)!!pp!d2c2 B2A2|!sfz!G8|
```

## Articulation Markings

| Articulation | Symbol | Effect | ABC Syntax |
|-------------|--------|--------|-----------|
| Staccato | . | Short, detached (~50% value) | `.C` or `!staccato!C` |
| Tenuto | - | Full value, slight stress | `!tenuto!C` |
| Accent | > | Strong attack | `!accent!C` or `!>!C` |
| Marcato | ^ | Very strong attack | `!marcato!C` or `!^!C` |
| Portato | -. | Slightly detached tenuto | `!tenuto!.C` (combine) |
| Staccatissimo | wedge | Very short (~25% value) | `!staccatissimo!C` |
| Fermata | U | Hold beyond written value | `!fermata!C` |
| Down bow | v-shape | String: down bow | `!downbow!C` |
| Up bow | v-shape inv | String: up bow | `!upbow!C` |
| Trill | tr | Rapid alternation with upper note | `!trill!C` or `T` |
| Turn | ~ | Ornamental 4-note figure | `!turn!C` |
| Mordent | zig | Rapid lower neighbor | `!mordent!C` |
| Inv. mordent | zig | Rapid upper neighbor | `!pralltriller!C` |

```abc
X:4
T:Articulation examples
M:4/4
L:1/4
K:C
.C .D .E .F|!tenuto!G !tenuto!A !tenuto!B !tenuto!c|!accent!C !marcato!D !trill!E !fermata!F|
```

## Combined Markings: Common Pairings

| Combination | Meaning | Example Context |
|------------|---------|-----------------|
| Allegro ma non troppo | Fast but not too much | Restrained fast movement |
| Andante con moto | Walking with motion | Not dragging |
| Adagio molto | Very slow | Deep slow movement |
| Allegro assai | Very fast (enough) | Emphatic fast |
| Presto con fuoco | Very fast with fire | Virtuosic finale |
| Largo e mesto | Broad and sad | Funeral march, lament |
| Allegro vivace | Fast and lively | Energetic outer movement |
| Tempo di Menuetto | In minuet tempo | 3/4 ~112 |
| Tempo di Valse | In waltz tempo | 3/4 ~150-180 |
| Alla marcia | In march style | 4/4, firm, dotted |
| Alla breve | Cut time (2/2) | Half note gets beat |

## Quick Reference: Setting Tempo in ABC

```abc
X:5
T:Complete header with tempo
C:Wolfgang System
M:4/4
L:1/8
Q:"Allegro moderato" 1/4=116
%%MIDI program 0
K:C
```

For compound meters:
```abc
X:6
T:Compound meter tempo
M:6/8
L:1/8
Q:"Andante pastorale" 3/8=50
K:F
```

For tempo changes mid-piece:
```abc
X:7
T:Mid-piece tempo change
M:4/4
L:1/8
Q:"Adagio" 1/4=66
K:C
C4 E4|G4 c4|
Q:"Allegro" 1/4=132
CDEF GABc|defg agfe|
```
