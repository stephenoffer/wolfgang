# Film Score Orchestration — Reference Tables

## Standard Film Orchestra

### Woodwinds
| Instrument | Count | Range (ABC) | Role |
|-----------|-------|-------------|------|
| Flute | 2-3 | C' - C'''' | Melody, color, high shimmer |
| Piccolo | 1 | D'' - C''''' (sounds 8va) | Brilliance, high accents |
| Oboe | 2 | Bb - A''' | Pastoral melody, poignant solo |
| English Horn | 1 | E - A'' | Warm melody, nostalgic |
| Clarinet (Bb) | 2-3 | D - Bb''' | Versatile melody, agility |
| Bass Clarinet | 1 | Bb,, - G'' | Low atmosphere, darkness |
| Bassoon | 2 | Bb,, - Eb'' | Bass line, comic, lyrical |
| Contrabassoon | 1 | Bb,,, - Bb, | Ultra-low depth |

### Brass
| Instrument | Count | Range (ABC) | Role |
|-----------|-------|-------------|------|
| French Horn | 4-6 | B,, - F'' | Heroic themes, warmth, sustain |
| Trumpet (Bb) | 3-4 | F#, - D''' | Fanfare, melody, brilliance |
| Trombone | 3 | E, - Bb'' | Power, warmth, dark weight |
| Bass Trombone | 1 | C, - G' | Low power, menace |
| Tuba | 1 | D,, - F' | Foundation, weight |

### Strings
| Instrument | Count | Range (ABC) | Role |
|-----------|-------|-------------|------|
| Violin I | 16 | G, - E'''' | Melody, high emotion |
| Violin II | 14 | G, - E'''' | Harmony, counter-melody |
| Viola | 12 | C, - E''' | Inner voice, warmth |
| Cello | 10 | C,, - A'' | Melody, bass, emotion |
| Double Bass | 8 | E,,, - G' | Foundation, weight |

### Percussion
| Instrument | Type | Role |
|-----------|------|------|
| Timpani | Pitched | Dramatic punctuation, rolls |
| Bass Drum | Unpitched | Impact, heartbeat |
| Snare Drum | Unpitched | Military, tension rolls |
| Cymbals (crash/susp) | Unpitched | Climax, shimmer |
| Tam-tam | Unpitched | Doom, enormity |
| Tubular Bells | Pitched | Solemn, church, magic |
| Glockenspiel | Pitched | Sparkle, magic, childhood |
| Xylophone | Pitched | Playful, macabre |
| Vibraphone | Pitched | Jazz, mystery, shimmer |
| Marimba | Pitched | Warmth, ethnic, rhythmic |
| Celesta | Pitched | Magic, delicacy, wonder |

### Keyboards and Harp
| Instrument | Role |
|-----------|------|
| Harp (1-2) | Arpeggios, glissandi, color |
| Piano | Percussive rhythm, solo, ostinato |
| Celesta | Magic, fairy-tale color |
| Organ | Sacred, massive, horror |
| Synthesizer | Pads, textures, modern hybrid |

## Hybrid Scoring — Orchestra + Electronics

| Electronic Element | Orchestral Pairing | Effect |
|-------------------|-------------------|--------|
| Synth pad (sustained) | String sustain | Expanded low end, width |
| Sub bass (30-60Hz) | Contrabass + tuba | Visceral rumble |
| Rhythmic pulse | Pizzicato + percussion | Modern drive |
| Processed vocals | Choir | Ethereal, otherworldly |
| Granular texture | Tremolo strings | Atmospheric unease |
| Distorted synth | Brass stabs | Aggressive impact |
| Ambient drone | Sustained horn/organ | Immersive space |
| Glitch/stutter | Col legno/Bartok pizz | Technological, broken |

## Scoring Templates by Scene Type

### Action Scoring
| Layer | Instruments | Technique |
|-------|------------|-----------|
| Rhythmic drive | Low strings, timp, perc | Ostinato, marcato |
| Harmonic punch | Brass section | Staccato stabs, sfz |
| Melodic line | Trumpet/horn unison | Heroic theme fragments |
| Texture fill | Upper strings tremolo | Sustained tension |
| Accents | Full orchestra | Tutti hits on action |
| Low weight | Bass tbn, tuba, bass drum | Ground-shaking impacts |

```abc
X:1
T:Action scoring template
M:4/4
L:1/8
K:Cm
Q:1/4=152
V:1 name="Trumpet"
z4 G2 c2 | _e2 d2 c2 G2 | _A4 G4 |
V:2 name="Horns"
[C,_E,G,]2 z2 [C,_E,G,]2 z2 | [C,_E,G,]2 z2 [_A,,C,_E,]2 z2 | [G,,_B,,D,]4 [C,_E,G,]4 |
V:3 name="Low Strings" clef=bass
C,C,C,C, C,C,C,C, | C,C,C,C, _A,,_A,,_A,,_A,, | G,,2 z2 C,,4 |
V:4 name="Timpani" clef=bass
C,,2 z C,, C,,2 z C,, | C,,2 z C,, _A,,,2 z _A,,, | G,,,4 C,,,4 |
```

### Romantic/Love Theme Scoring
| Layer | Instruments | Technique |
|-------|------------|-----------|
| Solo melody | Oboe, English horn, violin solo | Legato, espressivo |
| Counter-melody | Cello, French horn | Complementary phrases |
| Harmonic cushion | Divisi strings (pp) | Sustained chords, warm |
| Color | Harp arpeggios | Rolling broken chords |
| Bass | Cello + bass (pizz or sost) | Gentle foundation |
| Sparkle | Celesta, glockenspiel | Occasional touches |

```abc
X:2
T:Romantic scoring template
M:3/4
L:1/8
K:Eb
Q:1/4=72
V:1 name="Solo Oboe"
z2 _B2 G2 | _A4 F2 | G4 _E2 | _B,4 z2 |
V:2 name="Strings"
[_E,G,_B,]4 [_E,G,_B,]2 | [F,_A,C]4 [F,_A,C]2 | [_E,G,_B,]4 [_E,G,_B,]2 | [_B,,D,F,]4 z2 |
V:3 name="Harp"
_E,G,_B, _E G _B | F,_A,C F _A c | _E,G,_B, _E G _B | _B,,D,F, _B, D F |
```

### Horror/Tension Scoring
| Layer | Instruments | Technique |
|-------|------------|-----------|
| Sustained dread | Strings sul ponticello | Glassy, unstable |
| Cluster/dissonance | Divisi strings, brass | Semitone clusters |
| Shock stingers | Full orchestra sfz | Sudden loud attacks |
| Creeping texture | Col legno, harmonics | Insect-like, alien |
| Sub-rumble | Synth + contrabass | Below perception |
| Silence | Nothing | Most terrifying element |

```abc
X:3
T:Horror texture
M:4/4
L:1/4
K:Cm
Q:1/4=52
V:1 name="Violin I (sul pont)"
"pp"C "tremolo" C C C | _D _D _D _D |
V:2 name="Violin II (sul pont)"
"pp"_D _D _D _D | C C C C |
V:3 name="Viola (col legno)" clef=alto
z G,, z G,, | z G,, z G,, |
V:4 name="Cello" clef=bass
"ppp"C,,4 | C,,4 |
```

### Epic/Trailer Scoring
| Layer | Instruments | Technique |
|-------|------------|-----------|
| Percussion foundation | Taiko, bass drum, toms | Driving quarter/eighth pulse |
| Brass fanfare | Horns + trumpets unison | ff, marcato, heroic |
| Choir | SATB or wordless | Power, reverence |
| String ostinato | Full section tremolo/repeated | Driving energy |
| Anvil/metal hits | Percussion, synth | Impact accents |
| Build layers | Add instruments progressively | Crescendo over 16-32 bars |

```abc
X:4
T:Epic trailer build
M:4/4
L:1/4
K:Dm
Q:1/4=92
V:1 name="Brass (Horns+Trumpets)"
z4 | z4 | D, F, A, D | F A d2 |
V:2 name="Choir"
z4 | z4 | z4 | [DFA]2 [DFd]2 |
V:3 name="Strings"
D, z D, z | D, F, D, z | D, F, A, D | [D,F,A,D]4 |
V:4 name="Taiko/Perc" clef=bass
D,,2 z D,, | D,,2 D,, D,, | D,,D,,D,,D,, | D,,,4 |
```

### Intimate/Understated Scoring
| Layer | Instruments | Technique |
|-------|------------|-----------|
| Solo melody | Piano, guitar, solo violin | Simple, exposed |
| Accompaniment | Piano arpeggios, guitar fingerpick | Sparse, transparent |
| Sustain | 2-4 solo strings (not section) | Warmth, not weight |
| Color | Single woodwind note | Occasional phrase endings |
| Bass | Cello pizzicato | Gentle pulse |

```abc
X:5
T:Intimate piano scoring
M:4/4
L:1/8
K:G
Q:1/4=66
V:1 name="Piano RH"
B2 d2 e2 d2 | B2 A2 G2 F2 | G4 z4 |
V:2 name="Piano LH" clef=bass
G,,B,,D, z G,,B,,D, z | C,E,G, z C,E,G, z | G,,B,,D,G, z4 |
```

## Extended Techniques for Film

| Technique | Instrument | Notation Hint | Effect |
|-----------|-----------|---------------|--------|
| Sul ponticello | Strings | "sul pont." | Glassy, eerie |
| Sul tasto | Strings | "sul tasto" | Veiled, ghostly |
| Col legno | Strings | "col legno" | Clicking, skeletal |
| Bartok pizzicato | Strings | "snap pizz." | Aggressive snap |
| Harmonic gliss | Strings | Flageolet + gliss | Ethereal, alien |
| Tremolo | Strings, timp | "trem." | Tension, shimmer |
| Flutter-tongue | Brass, flute | "flz." | Menacing, buzzing |
| Muted brass | Brass | "con sord." | Distant, muffled |
| Stopped horn | Horn | "+" symbol | Metallic, nasal |
| Multiphonic | Woodwind | Specific fingering | Horror, distortion |
| Prepared piano | Piano | Objects on strings | Percussive, unusual |
| Bowed cymbal | Percussion | "bow" | High eerie sustain |
| Bowed vibraphone | Vibraphone | "bow" | Sustained, glassy |

## Mickeymousing vs Underscoring

| Approach | Definition | When to Use |
|----------|-----------|-------------|
| Mickeymousing | Music mirrors every on-screen action | Comedy, animation, slapstick |
| Tight sync | Music hits major action points only | Action, thriller |
| Loose sync | Music follows emotional arc, not action | Drama, romance |
| Underscoring | Music provides background mood only | Dialogue scenes |
| Source music | Diegetic — music exists in the scene | Bar scenes, radio, concert |
| Contrapuntal | Music contradicts visual mood | Irony, dark comedy, Kubrick |

## Voice/Instrument Templates for ABC

### Full Orchestra Tutti
```abc
V:1 name="Flute" clef=treble
V:2 name="Oboe" clef=treble
V:3 name="Clarinet" clef=treble
V:4 name="Bassoon" clef=bass
V:5 name="Horn" clef=treble
V:6 name="Trumpet" clef=treble
V:7 name="Trombone" clef=bass
V:8 name="Tuba" clef=bass
V:9 name="Timpani" clef=bass
V:10 name="Violin I" clef=treble
V:11 name="Violin II" clef=treble
V:12 name="Viola" clef=alto
V:13 name="Cello" clef=bass
V:14 name="Bass" clef=bass
```

### Small Dramatic Ensemble
```abc
V:1 name="Solo Instrument" clef=treble
V:2 name="Horn" clef=treble
V:3 name="Violin I" clef=treble
V:4 name="Violin II" clef=treble
V:5 name="Viola" clef=alto
V:6 name="Cello" clef=bass
V:7 name="Bass" clef=bass
V:8 name="Harp" clef=treble
```

### Hybrid Action Ensemble
```abc
V:1 name="Brass" clef=treble
V:2 name="Strings" clef=treble
V:3 name="Low Strings" clef=bass
V:4 name="Percussion" clef=bass
V:5 name="Synth" clef=bass
```

## Dynamic Layering Strategy

| Build Stage | Instruments Added | Dynamic |
|-------------|------------------|---------|
| 1: Foundation | Low strings pizz, single sustained note | pp |
| 2: Color | Add woodwind, harp | p |
| 3: Motion | Add string ostinato | mp |
| 4: Theme | Add melody instrument (horn/trumpet) | mf |
| 5: Weight | Add brass harmony, timpani | f |
| 6: Full | Tutti, percussion, choir if available | ff |
| 7: Climax | Everything, extreme registers | fff |

## Common Orchestral Doublings

| Doubling | Effect | Usage |
|----------|--------|-------|
| Flute + violin I (8va) | Brightness, shimmer | Lyrical melodies |
| Oboe + cello (unison) | Rich, warm | Emotional themes |
| Horn + cello (unison) | Noble, full | Heroic themes |
| Trumpet + violin I (unison) | Brilliant, cutting | Climactic melody |
| Clarinet + viola (unison) | Mellow blend | Inner voice warmth |
| Trombone + cello + bassoon | Dark weight | Villain themes |
| Full brass + strings | Maximum power | Final statement |
| Glock + celesta + harp harmonics | Magic sparkle | Wonder moments |
