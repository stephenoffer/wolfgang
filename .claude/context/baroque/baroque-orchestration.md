# Baroque Period Orchestration Reference

> Dense reference for AI composition agents. Covers orchestration c. 1600-1750.

---

## 1. Core Ensembles

### Continuo Group (Foundation of ALL Baroque Music)

| Instrument | Role | Required |
|---|---|---|
| Harpsichord | Chord realization, rhythmic drive | Yes (most contexts) |
| Organ | Chord realization (sacred music) | Sacred contexts |
| Cello / Viola da gamba | Bass line reinforcement | Yes |
| Double bass / Violone | Bass line (octave below) | Common in larger ensembles |
| Bassoon | Bass line doubling | Optional, common |
| Lute / Theorbo | Chord realization (chamber, opera) | Optional, adds color |

### Continuo Realization Principles

| Principle | Description |
|---|---|
| Read figures | Realize figured bass into chords |
| Voice count | Typically 3-4 voices above bass |
| Spacing | Follow standard voice-leading rules |
| Rhythm | Match prevailing rhythmic activity |
| Register | Stay below solo instrument |
| Texture density | Thinner in solo passages, fuller in tutti |
| Arpeggiation | Harpsichord may arpeggiate chords |

## 2. Concerto Grosso Texture

The defining orchestral texture of the Baroque.

| Component | Instruments | Role |
|---|---|---|
| Concertino | 2-3 soloists (typically 2 violins + cello) | Featured, virtuosic passages |
| Ripieno (tutti) | Full string orchestra + continuo | Ritornello, full passages |
| Continuo | Harpsichord + cello/bass | Plays throughout |

### Textural Alternation Patterns

| Pattern | Description | Usage |
|---|---|---|
| Tutti-solo-tutti | Ritornello principle | Most common |
| Concertino alone | Reduced, intimate | Episode passages |
| Full tutti | Maximum sonority | Openings, cadences |
| Solo over continuo | Single voice + bass | Slow movements |
| Echo | Forte group echoed piano | Dramatic contrast |

### ABC Example: Concerto grosso texture contrast
```abc
X:1
M:4/4
L:1/8
K:D
%% Tutti (forte)
!f! D2 F2 A2 d2 | c2 B2 A2 G2 |
%% Concertino (piano)
!p! f2 e2 d2 c2 | B2 A2 G2 F2 |
```

## 3. Terraced Dynamics

Baroque dynamics are NOT gradual. They shift in blocks.

| Dynamic Level | Context | Scoring |
|---|---|---|
| Forte (tutti) | Full ensemble passages | All instruments |
| Piano (solo/reduced) | Concertino or reduced scoring | Few instruments |
| Echo piano | Immediate repetition, softer | Reduced forces or distance |
| Forte -> Piano -> Forte | Block alternation | Standard concerto texture |

### Rules

| Rule | Description |
|---|---|
| No crescendo/decrescendo | Dynamic changes are SUDDEN, not gradual |
| Dynamics = scoring | Loud = more instruments, soft = fewer |
| Echo convention | Repeat phrase immediately at piano |
| Messa di voce | Vocal: swell on single note (solo only, not orchestral) |
| Organ registration | Dynamics via stop changes, not touch |

## 4. Standard Baroque Orchestral Forces

### Late Baroque Orchestra (Bach/Handel)

| Section | Instruments | Quantity |
|---|---|---|
| Strings | Violin I | Section (4-8) |
| | Violin II | Section (4-8) |
| | Viola | Section (2-4) |
| | Cello | Section (2-4) |
| | Double Bass | 1-2 |
| Woodwinds | Oboe | 1-3 |
| | Flute (traverso) | 1-2 |
| | Recorder | 1-2 (often alternate with flute) |
| | Bassoon | 1-2 (doubles bass) |
| Brass | Trumpet (natural) | 1-3 (in D or C) |
| | Horn (natural) | 2 (in F, D, or Bb) |
| Percussion | Timpani | 2 (paired with trumpets) |
| Continuo | Harpsichord/Organ | 1-2 |

### Chamber Forces

| Ensemble | Instruments |
|---|---|
| Trio sonata | 2 melody instruments + continuo (= 4 players) |
| Solo sonata | 1 melody instrument + continuo |
| Continuo aria | Voice + continuo |
| Chamber cantata | Voice + 1-2 obbligato instruments + continuo |

## 5. String Writing

### Baroque Violin Technique

| Technique | Description | Usage |
|---|---|---|
| Non-vibrato (default) | Straight tone, pure intonation | Standard |
| Selective vibrato | Ornament on sustained notes | Expressive moments |
| Bariolage | Rapid alternation between strings | Virtuosic passages |
| Multiple stops | Double, triple, quadruple stops | Chords, polyphonic |
| Scordatura | Altered tuning | Special effects (Biber) |
| High positions | Up to 7th position | Virtuosic solo |
| Arpeggiation | Broken chord figures | Accompaniment, solo |

### String Section Roles

| Instrument | Primary Roles |
|---|---|
| Violin I | Melody, virtuosic passages, top voice |
| Violin II | Countermelody, harmony, imitation of Vln I |
| Viola | Inner harmony, occasional melody |
| Cello | Bass line (= continuo bass), solo melody (Bach Suites) |
| Double Bass | Reinforces cello 8vb |

### String Texture Types

| Texture | Description | Context |
|---|---|---|
| 4-part chorale | Homophonic, hymn-like | Slow movements, chorales |
| Fugal | Imitative counterpoint | Fugues, overtures |
| Unison/octave | All strings together | Ritornello themes, emphasis |
| Solo + continuo | One violin + bass | Slow movements, concertos |
| Tremolo | Measured repeated notes | Agitation (opera) |
| Pizzicato | Plucked | Special effect, continuo-like |

### ABC Example: Baroque string trio texture
```abc
X:2
M:4/4
L:1/8
K:G
V:1 name="Violin I"
B2 AG FG AB | c2 Bc d4 |
V:2 name="Violin II"
G2 FE DE FG | A2 GA B4 |
V:3 name="Cello" clef=bass
G,2 A,2 B,2 D2 | E2 C2 G,4 |
```

## 6. Wind Instruments

### Oboe

| Feature | Description |
|---|---|
| Role | Primary Baroque wind; doubles Violin I or solos |
| Range | C4-D6 (practical) |
| Character | Bright, penetrating, pastoral |
| Usage | Doubles strings in tutti; solos in arias |
| Pairing | Commonly in pairs; with strings in 3rds |

### Flute (Traverso) and Recorder

| Feature | Traverso Flute | Recorder |
|---|---|---|
| Range | D4-A6 | F4-G6 (soprano); varies by size |
| Character | Warm, breathy, pastoral | Sweet, gentle, archaic |
| Usage | Solo, pastoral scenes | Pastoral, death scenes, birds |
| Volume | Softer than modern flute | Very soft |
| Period | More common late Baroque | More common early-mid Baroque |

### Bassoon

| Feature | Description |
|---|---|
| Role | Bass line doubling, continuo reinforcement |
| Range | Bb1-F5 |
| Solo | Rare in orchestral; featured in some concertos |
| Pairing | With cello and continuo bass |

## 7. Natural Brass

### Trumpet (Natural, no valves)

| Feature | Description |
|---|---|
| Keys | D and C most common |
| Range | Written C4-D6 (harmonics 3-13) |
| Character | Ceremonial, festive, triumphant, sacred |
| Usage | Festive works, sacred cantatas, trumpet-and-drum movements |
| Limitation | Only natural harmonics; scalewise in very high register (clarino) |
| Clarino register | High register (harmonics 8-16): stepwise melody possible |
| Principale register | Mid register: triadic fanfares |

### Horn (Natural)

| Feature | Description |
|---|---|
| Keys | F, D, Bb most common |
| Role | Sustain, hunting calls, pedal tones |
| Character | Noble, pastoral, hunting |
| Usage | Less common than in Classical; pastoral and hunting contexts |

### ABC Example: Trumpet clarino writing in D
```abc
X:3
M:4/4
L:1/8
K:D
%% High register: harmonics 8-12 allow stepwise motion
d2 ef gf ed | c2 BA B2 A2 | d4 d4 |
```

## 8. Timpani

| Feature | Description |
|---|---|
| Number | 2 drums |
| Tuning | Tonic and dominant of the key ONLY |
| Pairing | ALWAYS with trumpets; never alone |
| Patterns | Rhythmic reinforcement of bass at cadences |
| Sticks | Harder than Classical era; more articulate |
| Dynamic | Only forte passages; no pp timpani |

## 9. Texture Catalogue

| Texture | Voicing | Usage | Example |
|---|---|---|---|
| Monody | Solo voice + continuo | Recitative, early Baroque | Opera, cantata |
| Trio sonata | 2 treble + continuo | Chamber standard | Corelli, Handel |
| Concerto grosso | Concertino + ripieno | Orchestral standard | Corelli Op. 6, Handel Op. 6 |
| Solo concerto | Soloist + orchestra | Virtuosic display | Vivaldi, Bach |
| Chorale setting | 4-part SATB + instruments | Sacred | Bach cantatas |
| Fugal | Imitative polyphony | Structural, learned | Bach, Handel |
| Choral-orchestral | Chorus + full orchestra | Grand sacred | Handel oratorios, Bach Passions |
| Dance suite | Various textures per movement | Secular entertainment | Bach, Handel |
| French overture | Slow (dotted) -> Fast (fugal) | Opening | Handel, Bach |
| Italian overture | Fast-Slow-Fast | Opening | Vivaldi, later opera |

## 10. Continuo Realization Guide

### Chord Voicing by Figure

| Figure | Realization (C bass) | Notes |
|---|---|---|
| 5/3 (unmarked) | C-E-G (+ doubled root or 3rd) | Default |
| 6 | C-E-A (1st inv of A minor or F major) | Context determines |
| 6/4 | C-F-A or C-E-A | Restricted; passing or cadential |
| 7 | C-E-G-B (or Bb) | Seventh chord |
| #6 | Raised 6th above bass | Often indicates modulation |
| 4-3 | Suspend 4th, resolve to 3rd | On the beat |

### Realization Style

| Context | Realization Approach |
|---|---|
| Recitative | Block chords, held, sparse |
| Aria accompaniment | Light, rhythmic, supportive |
| Orchestral tutti | Simple, doubles bass line, minimal figuration |
| Chamber trio sonata | Active, fills out harmony fully |
| Solo passages | Thinner, stay below soloist |

## 11. Doubling Practices

| Doubling | Effect | Frequency |
|---|---|---|
| Oboe + Violin I (unison) | Reinforced melody | Very common in tutti |
| Bassoon + Cello (unison) | Reinforced bass | Standard |
| Trumpet + Violin I (octave) | Brilliant, festive | Festive movements |
| Recorder + Violin (unison) | Softened color | Pastoral |
| Flute + Violin (unison) | Brightened | Common |
| All strings unison | Maximum power | Ritornello themes |

### Avoid

| Combination | Problem |
|---|---|
| Trumpet + oboe (same register) | Trumpet overpowers |
| Solo instrument doubled | Defeats solo purpose |
| Horn in non-harmonic context | Limited pitches, exposed |

## 12. Orchestration by Genre

| Genre | Standard Forces | Texture |
|---|---|---|
| Solo sonata | Melody + continuo | 2 real voices |
| Trio sonata | 2 melody + continuo | 3-4 real voices |
| Concerto grosso | Concertino + ripieno + continuo | Alternating tutti/solo |
| Solo concerto | Soloist + strings + continuo | Soloist vs tutti |
| Opera | Voices + orchestra + continuo | Varies by scene |
| Cantata | Voice(s) + instruments + continuo | Varied: recit, aria, chorus |
| Oratorio | Soloists + chorus + orchestra + continuo | Grand, varied |
| Suite/Partita | Varies; solo or orchestral | Dance-specific |
| Fugue | Keyboard solo or ensemble | Pure counterpoint |
| French overture | Full orchestra | Dotted rhythms -> fugue |

## 13. Register and Spacing

| Register | Active Instruments | Spacing |
|---|---|---|
| Bass (C2-C3) | Cello, bass, bassoon, organ pedal | Open: octaves, 5ths |
| Tenor (C3-C4) | Viola, cello, bassoon | Moderate spacing |
| Alto (C4-C5) | Violin II, oboe, flute, viola | Close to moderate |
| Soprano (C5-C7) | Violin I, oboe, flute, trumpet (clarino) | Close spacing |

### Principle: Baroque spacing often puts wider intervals low and closer intervals high, same as later periods. Crossing of inner voices is acceptable in contrapuntal textures.

## 14. Transparency Checklist for Baroque Scoring

| Check | Requirement |
|---|---|
| Continuo present? | Every Baroque piece needs basso continuo |
| Bass line clear? | Continuo bass must be audible and functional |
| Dynamics terraced? | No gradual crescendo/diminuendo |
| Trumpet with timpani? | Trumpets and timpani pair together |
| Solo vs tutti clear? | Distinguish concertino from ripieno |
| Voice leading clean? | Strict counterpoint rules apply |
| Figures playable? | Continuo realization follows from figures |
| Natural brass pitches? | Only harmonics available for trumpet/horn |
| No anachronisms? | No clarinet, no valved brass, no modern flute |
