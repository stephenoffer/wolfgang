# Modern Orchestration Reference (c. 1900–1975)

## Extended String Techniques

| Technique | Notation/Abbrev | Effect | Example Composer |
|-----------|----------------|--------|-----------------|
| Sul ponticello | s.p. | Glassy, harmonic-rich | Penderecki, Ligeti |
| Sul tasto | s.t. | Airy, flute-like | Debussy, Bartok |
| Col legno battuto | c.l.b. | Percussive tap with wood | Holst (Mars), Bartok |
| Col legno tratto | c.l.t. | Bow with wood, scratchy | Penderecki |
| Bartok pizzicato | snap pizz (circle+line) | Snapping string against fingerboard | Bartok SQ4 |
| Natural harmonics | Small circle above note | Pure, ethereal overtone | All modern |
| Artificial harmonics | Diamond noteheads | High, crystalline | Ravel, Stravinsky |
| Quarter-tone gliss | Wavy line between pitches | Microtonal slide | Penderecki, Xenakis |
| Ricochet | Thrown bow, multiple bounces | Rapid repeated notes | Bartok |
| Tremolo sul pont. | Trem + s.p. | Shimmering, eerie | Ligeti Atmospheres |
| Behind the bridge | Play behind bridge | Metallic, unpitched | Crumb |
| Overpressure | Very heavy bow pressure | Crunching, distorted | Lachenmann |

```abc
X:1
T:String Extended Techniques Passage
M:4/4
L:1/8
K:C
"^s.p."E,2 F,2 "^nat. harm."e4 | "^c.l.b."G,G,G,G, "^ord."C4 |
"^s.t."A,2B,2 "^trem s.p."C8 | "^snap pizz"E,2 z2 "^arco"G,4 |
```

## Extended Woodwind Techniques

| Technique | Instruments | Effect |
|-----------|------------|--------|
| Multiphonics | All woodwinds | Two+ pitches simultaneously |
| Flutter-tongue | Flute, clarinet | Rapid tremolo, rolled R |
| Key clicks | All woodwinds | Percussive, pitched tapping |
| Slap-tongue | Clarinet, saxophone | Percussive pop |
| Overblowing | All | Harsh, distorted upper partials |
| Whistle tones | Flute | Extremely soft high harmonics |
| Microtones | All (special fingerings) | Quarter-tones, 6th-tones |
| Circular breathing | All | Continuous unbroken tone |
| Teeth on reed | Oboe, clarinet | Harsh, strained color |
| Air sounds | Flute | Breathy, windy texture |

```abc
X:2
T:Woodwind Extended Techniques
M:3/4
L:1/8
K:C
"^flutter"z C2D2E | "^multiphonic"[CE]4 z2 | "^key clicks"x x x x x x |
```

## Extended Brass Techniques

| Technique | Effect | Usage |
|-----------|--------|-------|
| Stopped horn | Nasal, distant (hand in bell) | Color change, muted passages |
| Flutter-tongue | Buzzed, aggressive tremolo | Climactic moments |
| Muted varieties | Straight, cup, harmon, plunger | Wide timbral range |
| Brassy (cuivre) | Forced, metallic overblown | Climax, aggression |
| Glissando | Slide between pitches | Portamento, comedy |
| Multiphonics | Sing + play simultaneously | Drone + melody |
| Pedal tones | Extreme low register | Dark foundation |
| Quarter-tones | Lip bending/valve combo | Microtonal coloring |

## Percussion Ensemble

### Standard Modern Percussion Section

| Category | Instruments | Role |
|----------|------------|------|
| Pitched metal | Vibraphone, glockenspiel, crotales, tubular bells | Melody, color |
| Pitched wood | Xylophone, marimba | Melody, rhythm |
| Unpitched metal | Cymbals (crash/susp/ride), tam-tam, triangle, anvil | Color, climax |
| Unpitched wood | Woodblock, temple block, claves, guiro | Rhythm, articulation |
| Unpitched skin | Snare, bass drum, tom-toms, bongos, congas | Rhythm, weight |
| Keyboard | Celesta, piano (as perc.) | Color, articulation |
| Special | Slapstick, ratchet, wind machine, thunder sheet | FX |

### Percussion Notation Conventions

| Symbol | Meaning |
|--------|---------|
| x noteheads | Unpitched / cymbal |
| Diamond noteheads | Harmonics / dead stroke |
| Triangle noteheads | Rim shot / edge |
| Normal noteheads on staff | Pitched percussion |
| One-line staff | Single unpitched instrument |
| Five-line staff | Drum kit or multiple unpitched |

## Prepared Piano

| Preparation | Material | Effect | Composer |
|-------------|----------|--------|----------|
| Bolt between strings | Metal bolt | Metallic, gamelan-like | Cage |
| Rubber mute | Rubber | Dampened, thuddy | Cage |
| Screw on string | Metal screw | Buzzy, sitar-like | Cage |
| Paper on strings | Paper | Snare-drum rattle | Cage, Cowell |
| Eraser mute | Rubber eraser | Muted, dead | Cage |

```abc
X:3
T:Prepared Piano Texture
M:4/4
L:1/16
K:C
"^bolt prep"C,4 z4 E,4 z4 | "^rubber mute"G,,8 C,8 |
"^screw prep"^F,2G,2A,2B,2 C4 z4 |
```

## Aleatory (Chance) Elements

| Type | Description | Control Level | Composer |
|------|-------------|---------------|----------|
| Controlled aleatory | Choose order of written fragments | Medium | Lutoslawski |
| Time-bracket | Play material within time window | Medium | Cage, Feldman |
| Graphic score | Visual interpretation, no standard notation | Low | Cardew, Brown |
| Mobile form | Performer chooses section order | Medium | Stockhausen |
| Improvisation box | Free play within given pitches/range | Low-Medium | Penderecki |
| Dice music | Chance determines composition | None (in composition) | Cage |

### Aleatory Notation in ABC (Approximation)
```abc
X:4
T:Controlled Aleatory Box (play any order)
M:none
L:1/8
K:C
"^Box A: freely"C E G B | "^Box B: freely"D ^F A ^c |
"^Box C: freely"_E G _B d | "^Choose order: A/B/C"z8 |
```

## Pointillistic Texture

| Principle | Application |
|-----------|-------------|
| Wide register leaps | Each note in different octave |
| Fragmented melody | Single notes distributed across instruments |
| Dynamic variety per note | Each note has distinct dynamic |
| Silence as structural | Rests are compositional elements |
| Timbral melody | Color changes on each note |
| Short durations | Notes isolated, not connected |

```abc
X:5
T:Pointillistic Texture (Webern-style)
M:3/4
L:1/8
K:C
!ppp!c z !ff!E, z !mp!^f z | z !pp!_B, z !mf!^g z !p!D |
z z !fff!_A,, z z !ppp!e' |
```

## Klangfarbenmelodie (Tone-Color Melody)

| Concept | Implementation |
|---------|---------------|
| Definition | Melody defined by timbral changes, not just pitch |
| Single pitch, changing color | Same note passed between instruments |
| Chord, changing orchestration | Same harmony re-orchestrated beat by beat |
| Schoenberg Op.16/3 | Classic example: sustained chord, shifting colors |
| Webern orchestration of Bach | Each note of melody in different instrument |

### Instrument Rotation for Klangfarbenmelodie
```
Beat:     1        2        3        4
Pitch:    C4       C4       C4       C4
Color:    Flute    Oboe     Clar.    Horn
Dynamic:  pp       mp       p        pp
```

```abc
X:6
T:Klangfarbenmelodie Sketch (one staff reduction)
M:4/4
L:1/4
K:C
"^Fl pp"C "^Ob mp"C "^Cl p"C "^Hn pp"C |
"^Vln pp"E "^Va mp"E "^Vc p"E "^Fl pp"E |
```

## Spatial Distribution

| Technique | Description | Composer |
|-----------|-------------|----------|
| Antiphonal groups | Ensembles in different locations | Gabrieli revival, Stockhausen |
| Surround audience | Players around audience | Stockhausen Gruppen |
| Mobile performers | Players walk during performance | Crumb |
| Offstage instruments | Spatial depth, distance effect | Ives, Mahler tradition |
| Multiple conductors | Independent tempi by location | Stockhausen Gruppen (3 orch.) |

## Extreme Registers

| Register | Instruments | Effect |
|----------|------------|--------|
| Sub-bass (< C2) | Contrabassoon, tuba, bass trom, contrabass | Rumbling, ominous |
| Super-high (> C7) | Piccolo, violin harmonics, celesta | Ethereal, piercing |
| Flageolet range | String harmonics above normal | Glass-like, spectral |
| Pedal tones | Brass lowest register | Grinding, dark |
| Altissimo | Clarinet/sax above normal | Screaming, intense |

```abc
X:7
T:Extreme Register Contrasts
M:4/4
L:1/4
K:C
"^Contrabass"C,,2 D,,2 | "^Violin harm."c'''2 d'''2 |
"^Tuba pedal"G,,,2 "^Picc"g'''2 |
```

## Modern Orchestral Textures

| Texture | Description | Scoring Approach |
|---------|-------------|-----------------|
| Cluster band | Dense mass of adjacent pitches | Divisi strings, each player different pitch |
| Sound mass | Slowly evolving timbral block | Penderecki Threnody — 52 strings |
| Pointillism | Isolated sonic events in silence | Webern — single notes, varied color |
| Stratified layers | Independent simultaneous layers | Ives, Carter — different tempi |
| Heterophony | Same melody, slight variations simultaneously | Cowell, influenced by Asian music |
| Micropolyphony | Dense canon at very small intervals | Ligeti Atmospheres, Lux Aeterna |

```abc
X:8
T:Micropolyphonic Entry (Ligeti-style, reduced)
M:4/4
L:1/16
K:C
%%staves {1 2 3}
V:1
z4 C2D2 _E2E2 F2^F2 |
V:2
z8 C2D2 _E2E2 |
V:3
z12 C2D2 |
```

## Orchestration Decision Matrix

| Musical Need | Primary Technique | Secondary Technique |
|-------------|-------------------|---------------------|
| Eerie atmosphere | Sul pont. tremolo strings | Whistle tones flute |
| Aggressive climax | Cuivre brass, Bartok pizz | Tam-tam, bass drum |
| Delicate texture | Harmonics, celesta | Crotales, vibraphone |
| Chaos / violence | Tone clusters, aleatory box | Full percussion, brass ffff |
| Isolation / loneliness | Solo instrument, extreme register | Long silence, pppp |
| Mechanical / obsessive | Ostinato, col legno battuto | Xylophone, piano percussive |
| Mystical / transcendent | Micropolyphony, harmonics | Tubular bells, organ |
| Humorous / grotesque | Wrong register, muted brass | Woodblock, slide whistle |

## Dynamic Range in Modern Scores

| Marking | Level | Usage |
|---------|-------|-------|
| pppppp | Near silence | Feldman, Nono |
| ppp | Barely audible | Webern, Ligeti |
| pp-p | Soft | Standard |
| mp-mf | Moderate | Standard |
| f-ff | Loud | Standard |
| fff | Very loud | Climax |
| ffff | Extreme | Penderecki, Xenakis |
| fffff | Absolute maximum | Rare, extreme effect |
| niente (n) | From/to nothing | Hairpin to/from circle |

## Timbral Combination Quick Reference

| Combination | Effect | Register |
|-------------|--------|----------|
| Flute + violin harmonics | Ethereal shimmer | High |
| Oboe + muted trumpet | Nasal, penetrating | Middle |
| Clarinet + viola | Warm, dark blend | Middle-low |
| Bassoon + cello pizz | Dry, articulate | Low |
| Horn + trombone stopped | Mysterious, distant | Middle |
| Xylophone + piano staccato | Bright, percussive | High-middle |
| Vibraphone + harp harmonics | Glassy, resonant | High |
| Tam-tam + bass drum + contrabass | Massive, dark | Low |
| Celesta + glockenspiel | Crystalline, bell-like | High |
| Marimba + bass clarinet | Woody, dark | Low-middle |
