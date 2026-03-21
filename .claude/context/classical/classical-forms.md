# Classical Forms Reference

## Sonata Form (First Movement Form)

### Overview

| Section | Proportion | Key (major) | Key (minor) | Function |
|---------|-----------|-------------|-------------|----------|
| Introduction (opt.) | 5-10% | I (slow) | i (slow) | Set mood, anticipate |
| Exposition | 30-35% | I -> V | i -> III | Present themes |
| Development | 20-30% | Unstable, various | Unstable, various | Transform, explore |
| Recapitulation | 30-35% | I throughout | i throughout (mostly) | Resolve, confirm |
| Coda (opt.) | 5-15% | I | i or I | Clinch, extend |

### Exposition Detail

| Sub-section | Bars (approx) | Key | Content |
|------------|--------------|-----|---------|
| P (Primary theme) | 8-20 | I (or i) | Strong, distinctive theme; establishes tonic |
| TR (Transition) | 8-16 | I -> V (or III) | Modulating, energy building; often based on P |
| MC (Medial caesura) | 1-2 | V (or III) | Brief pause/half cadence; marks arrival |
| S (Secondary theme) | 8-20 | V (or III) | Contrasting character; lyrical or new texture |
| EEC (Essential expositional closure) | 1-2 | V (or III) | Strong PAC in new key |
| C (Closing/Codetta) | 4-16 | V (or III) | Cadential, confirming new key |
| *Repeat sign* | | | Exposition typically repeated |

### Transition Types

| Type | Description | Example |
|------|-------------|---------|
| Dissolving P | P material fragments, gains energy | Mozart K. 545/I |
| Independent TR | New material, often forte | Beethoven Op. 2 No. 1/I |
| Dependent TR | P material modulated/sequenced | Haydn common practice |
| TR => MC | Energy builds to half cadence | Standard |

### Development Techniques

| Technique | Description | Frequency |
|-----------|-------------|-----------|
| Fragmentation | P or S broken into motives | Very common |
| Sequence | Motive through descending 5ths or other | Very common |
| Key exploration | Move through remote keys | Essential |
| Inversion | Theme upside down | Common (Haydn, Beethoven) |
| Stretto | Overlapping theme entries | Moderate |
| New theme | Entirely new material | Rare (but Beethoven "Eroica") |
| Fugato | Imitative passage using P motive | Moderate |
| Retransition | Dominant pedal preparing recap | Standard ending |
| False recap | Theme returns in wrong key | Haydn specialty |

### Development Key Plans

| Type | Key sequence | Style |
|------|-------------|-------|
| Standard (major) | V -> vi -> ii -> (various) -> V pedal -> I | Mozart |
| Flat-side (major) | V -> IV -> ii -> bVI -> V pedal -> I | Beethoven |
| Standard (minor) | III -> iv -> v -> (various) -> V pedal -> i | General |
| Remote wandering | Multiple remote keys via dim7 pivots | Late Classical |

### Recapitulation Adjustments

| Adjustment | Purpose | Detail |
|-----------|---------|--------|
| P in tonic | Confirm home key | Usually faithful return |
| TR rewritten | Avoid modulation to V | Must lead to S in tonic |
| S in tonic | Tonal resolution | The point of recap |
| S may be altered | New register, orchestration | Variety within resolution |
| C in tonic | Confirms tonic closure | May be expanded into coda |

### Sonata Form ABC Skeleton
```abc
X:1
T:Sonata Form Skeleton (C major)
M:4/4
L:1/8
K:C
% P theme (I)
!f! C2E2 G2c2 | d2c2 B2A2 | G4 z4 |
% Transition
G2A2 B2c2 | d2e2 ^f2g2 |
% S theme (V = G major)
!p! G2B2 d2g2 | f2e2 d4 |
% Closing
D2G2 B2d2 | d4 B4 | G8 |
```

## Minuet and Trio

### Structure

| Section | Form | Key | Repeats | Character |
|---------|------|-----|---------|-----------|
| Minuet | Rounded binary | I | Both halves repeated | Moderate 3/4, elegant |
| Trio | Rounded binary | IV, vi, or I (diff texture) | Both halves repeated | Lighter, contrasting |
| Minuet da capo | Same as above | I | No repeats on da capo | Return |

### Minuet Internal Structure (Rounded Binary)

| Part | Bars | Key | Content |
|------|------|-----|---------|
| A | 8-16 | I -> V | Theme, modulates to dominant |
| :||: | | | Repeat |
| B (first part) | 4-8 | V -> (dev) | Contrasting, developmental |
| A' | 8-16 | I | Theme returns in tonic |
| :||: | | | Repeat |

### Minuet ABC Example
```abc
X:2
T:Minuet
M:3/4
L:1/4
K:G
% A section
|: B c d | e d c | B A G | A2 z |
B c d | g f e | d c B | A2 z :|
% B section -> A'
|: f e d | e d c | B A G | F2 z |
B c d | e d c | B A G | G3 :|
```

## Rondo Forms

### Simple Rondo (ABACA)

| Section | Key | Character | Bars |
|---------|-----|-----------|------|
| A (refrain) | I | Main theme, tuneful | 8-16 |
| B (episode 1) | V or vi | Contrasting | 8-16 |
| A (refrain) | I | Return, exact or varied | 8-16 |
| C (episode 2) | IV, ii, or remote | Most contrasting | 16-24 |
| A (refrain) | I | Final return | 8-16 |
| Coda | I | Cadential extension | 4-16 |

### Sonata-Rondo (ABACABA)

| Section | Key | Content | Corresponds to |
|---------|-----|---------|---------------|
| A | I | Refrain | Expo P |
| B | V | Episode 1 | Expo S |
| A | I | Refrain return | -- |
| C (development) | Various | Central episode | Development |
| A | I | Refrain return | Recap P |
| B | I | Episode in tonic | Recap S |
| A + Coda | I | Final refrain | Coda |

### Rondo ABC Example (Refrain)
```abc
X:3
T:Rondo Refrain
M:2/4
L:1/16
K:G
|: G2B2 d4 | c2B2 A4 | G2A2 B2c2 | d4 z4 :|
```

## Theme and Variations

### Variation Techniques

| Technique | Description | Typical position |
|-----------|-------------|-----------------|
| Melodic ornament | Add passing tones, turns, runs | Var 1-2 |
| Rhythmic diminution | Faster note values | Var 2-3 |
| Accomp. change | New accompaniment pattern | Var 3-4 |
| Mode change | Major -> minor or reverse | Middle var |
| Tempo change | Adagio variation | Near end |
| Register change | Melody in bass or inner voice | Middle var |
| Texture change | Polyphonic, fugato | Late var |
| Character piece | Dance, march, etc. | Late var |
| Bravura | Virtuosic, fast | Penultimate |
| Finale | Coda, extended, triumphant | Last |

### Variation Set Plan (typical 6 variations)

| Variation | Technique | Tempo | Character |
|-----------|-----------|-------|-----------|
| Theme | Simple statement | Andante | Clear, singable |
| Var. 1 | 16th-note figuration RH | Andante | Decorated |
| Var. 2 | 16th-note figuration LH | Andante | Bass active |
| Var. 3 | Minor mode | Andante | Dark, emotional |
| Var. 4 | Adagio, ornamental | Adagio | Expressive |
| Var. 5 | Allegro, virtuosic | Allegro | Brilliant |
| Var. 6 | Extended finale (or Tempo I) | Allegro/Andante | Conclusive, coda |

### Theme and Variation ABC Example
```abc
X:4
T:Theme
M:3/4
L:1/8
K:A
|: A2 c2 e2 | f4 e2 | d2 c2 B2 | A4 z2 :|
```
```abc
X:5
T:Variation 1 (16th-note ornament)
M:3/4
L:1/16
K:A
|: A2B2 c2d2 e2f2 | f2e2f2g2 e4 | d2c2d2e2 c2B2 | A4 z4 z4 :|
```

## Concerto First-Movement Form (Double Exposition)

### Structure

| Section | Key | Forces | Content |
|---------|-----|--------|---------|
| Orchestral exposition (R1) | I throughout | Orchestra alone | P, TR, S (all in I), closing |
| Solo exposition | I -> V | Solo + orchestra | P (solo), TR modulates, S in V |
| Development | Various | Solo + orchestra | Virtuosic, thematic development |
| Recapitulation | I | Solo + orchestra | P, TR, S all in I |
| Cadenza | I (over V) | Solo alone | Improvised/composed, virtuosic |
| Coda/Final ritornello | I | Orchestra (+ solo) | Orchestral close |

### Orchestral Exposition vs Solo Exposition

| Feature | Orchestral expo | Solo expo |
|---------|----------------|-----------|
| Key | Stays in tonic | Modulates to dominant |
| Character | Orchestral, thematic survey | Virtuosic, personal |
| S theme | In tonic (unusual) | In dominant (standard) |
| Length | Shorter | Longer |
| Virtuosity | None | Central |
| New material | Sets agenda | Solo may add new themes |

### Solo Entry Types

| Type | Description | Composers |
|------|-------------|-----------|
| Dramatic | Solo enters with new material, forte | Beethoven |
| Lyrical | Solo enters with P theme, piano | Mozart (many) |
| Cadenza-like | Solo enters with flourish/trill | Mozart (some) |
| Accompanied | Solo over orchestral continuation | Haydn |

### Cadenza Conventions

| Feature | Description |
|---------|-------------|
| Placement | On orchestral I6/4 chord, fermata |
| Content | Themes from movement, virtuosic display |
| Length | 1-3 minutes (Classical); longer in Beethoven |
| Ending | Long trill on supertonic -> tonic |
| Signal | Trill tells orchestra to re-enter |
| Written vs improvised | Improvised in Mozart's era; Beethoven writes them out |

### Concerto ABC Skeleton (orchestral exposition opening)
```abc
X:6
T:Concerto Opening (Orchestra)
M:4/4
L:1/8
K:Bb
V:Vn1 name="Violin I" clef=treble
!f! B2d2 f4 | e2d2 c2B2 | A2B2 c4 | d6 z2 |
V:Vc name="Cello/Bass" clef=bass
B,4 B,4 | F,4 F,4 | F,4 F,4 | B,6 z2 |
```

## Less Common Forms

### Sonatina Form (no development)

| Section | Key |
|---------|-----|
| Exposition | I -> V |
| Recapitulation | I -> I |
| (No development section) | |

### Sonata without Development (slow movement form)

| Section | Key | Notes |
|---------|-----|-------|
| Exposition | I -> V | Standard |
| Retransition | V -> I | Brief link |
| Recapitulation | I | S now in tonic |

### ABA (Ternary - slow movement)

| Section | Key | Character |
|---------|-----|-----------|
| A | I | Main theme |
| B | Related key | Contrasting |
| A (or A') | I | Return, possibly varied |

### ABAB (Binary with repeats)

| Section | Key |
|---------|-----|
| A | I -> V |
| B | V -> I |
| *Both repeated* | |

## Form Selection Guide

| Movement position | Common forms | Tempo |
|------------------|-------------|-------|
| Symphony I | Sonata | Allegro (slow intro optional) |
| Symphony II | Sonata, ABA, Theme & Var | Andante/Adagio |
| Symphony III | Minuet & Trio (or Scherzo) | Allegretto/Allegro |
| Symphony IV | Sonata, Rondo, Sonata-Rondo | Allegro/Presto |
| Concerto I | Double-expo sonata | Allegro |
| Concerto II | ABA, Theme & Var | Andante/Adagio |
| Concerto III | Rondo, Sonata-Rondo | Allegro/Presto |
| Sonata I | Sonata | Allegro |
| Sonata II | ABA, Sonata (slow) | Andante |
| Sonata III (if 3 mvts) | Rondo, Sonata-Rondo | Allegro |
| String Quartet I | Sonata | Allegro |
| String Quartet finale | Rondo, Sonata, Fugue (late) | Presto/Allegro |
