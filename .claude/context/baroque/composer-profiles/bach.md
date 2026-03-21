# Composer Profile: Johann Sebastian Bach (1685-1750)

> Reference for AI composition agents emulating Bach's style.

---

## 1. Core Style Traits

| Trait | Description |
|---|---|
| Contrapuntal supremacy | Unmatched mastery of independent voice leading |
| Motivic spinning-out (Fortspinnung) | Short motif generates long, continuous melodic lines |
| Harmonic richness | Dense chromaticism within functional tonality |
| Structural architecture | Mathematical proportions, symmetry, mirror structures |
| Universal synthesis | Combined Italian, French, and German styles |
| Dance mastery | Every dance genre elevated to art music |
| Sacred devotion | Music as theology; numerological symbolism |

## 2. Counterpoint Techniques

| Technique | Description | Frequency |
|---|---|---|
| Imitation | Voices enter successively with same material | Constant |
| Invertible counterpoint | Voices swappable at octave, 10th, or 12th | Very common |
| Canon | Strict imitation at fixed interval and distance | Common |
| Stretto | Subject overlaps with itself | Fugue climaxes |
| Augmentation | Subject in longer note values | Late fugue entries |
| Diminution | Subject in shorter note values | Developmental |
| Retrograde | Subject backwards | Rare, learned |
| Mirror inversion | Subject upside-down | Moderate |
| Double/triple fugue | Multiple subjects combined | Grand fugues |
| Pedal point + counterpoint | Free voices over sustained bass | Conclusions |

### ABC Example: Invertible counterpoint at the octave
```abc
X:1
M:4/4
L:1/8
K:C
V:1
%% Version 1: melody above
C2 DE FGAB | c2 BA GFED |
V:2
E,2 F,G, A,B,C D | E2 DC B,A,G,F, |
```
```abc
X:2
M:4/4
L:1/8
K:C
V:1
%% Version 2: melody below (inverted)
E2 FG ABcd | e2 dc BAGF |
V:2
C,2 D,E, F,G,A,B, | C2 B,A, G,F,E,D, |
```

## 3. Melodic Characteristics (Fortspinnung)

| Feature | Description |
|---|---|
| Spinning out | Short motif generates long, unbroken lines |
| Continuous motion | Avoids cadential breaks; phrases elide |
| Sequential development | Motif sequenced through key areas |
| Wide range | Melodies span full instrument range |
| Compound melody | Single line implies 2-3 voices |
| Ornamental integration | Ornaments are structural, not decorative |

### Melodic Construction Pattern

| Phase | Description | Bars (typical) |
|---|---|---|
| Vordersatz (head) | Motif stated, establishes key | 1-2 |
| Fortspinnung (spin) | Motif developed sequentially, modulates | 2-6 |
| Epilog (cadence) | Cadential arrival | 1-2 |

### ABC Example: Fortspinnung melody
```abc
X:3
M:4/4
L:1/16
K:C
%% Head: establishing motif
CDEF GABc |
%% Spin: sequential development
dBcA BAGF | EAGF GFED |
%% Cadence
CEDB, C4 z4 |
```

## 4. Harmonic Language

| Feature | Description |
|---|---|
| Rich chromaticism | Chromatic passing tones, applied chords frequent |
| Suspension density | Multiple simultaneous suspensions |
| Well-tempered modulation | Exploits all 24 keys (WTC) |
| Circle of 5ths | Extended sequential circles |
| Diminished 7th chords | Dramatic, expressive, modulatory |
| Neapolitan | Used expressively in minor keys |
| Augmented 6th (emerging) | Occasional, pre-Classical usage |
| Cross-relations | Accepted between voices |
| Chromatic bass | Lament bass, chromatic descents |

### Chorale Harmonization Principles

| Principle | Application |
|---|---|
| One chord per melody note (minimum) | Often 2+ chords per note with passing harmonies |
| Bass line melodic | Independent, often stepwise or sequential |
| Inner voices active | Alto and tenor have melodic interest |
| Passing tones on weak beats | Extensive non-chord tones |
| Suspensions at cadences | 4-3 standard at every cadence |
| Key variety | Modulate to related keys within short chorale |
| Fermata = cadence | Each fermata marks a phrase-ending cadence |

## 5. Fugue Construction (Bach Specifics)

| Feature | Bach's Approach |
|---|---|
| Subject design | Compact, rhythmically distinctive, harmonically clear |
| Answer type | Tonal answer for ^1-^5 subjects; real otherwise |
| Countersubject | Usually retained; invertible with subject |
| Episode craft | Derived from subject/countersubject fragments |
| Key plan | Exposition (I) -> middle entries (related keys) -> return (I) |
| Stretto | Reserved for climax; not all fugues have it |
| Pedal point | Tonic or dominant pedal near end |
| Final entry | Subject in tonic, often with full texture |

### Bach Fugue Subject Types

| Type | Character | Example |
|---|---|---|
| Rhythmic/motoric | Driving, continuous 8ths/16ths | WTC I, C major |
| Lyrical | Longer notes, expressive intervals | WTC I, C# minor |
| Chromatic | Half-step motion, expressive | WTC I, D# minor |
| Dance-like | Gigue or other dance rhythm | WTC II, A major |
| Declamatory | Bold, dramatic leaps | St. Anne Fugue |

## 6. Dance Suite Mastery

| Dance | Bach's Treatment |
|---|---|
| Allemande | Rich polyphony, continuous 16ths, serious |
| Courante | Hemiola at cadences, energetic cross-rhythms |
| Sarabande | Deeply expressive, ornate melody on beat 2 |
| Gigue | Fugal opening, compound meter, brilliant |
| Preludes | Wide variety: arpeggiated, inventive, virtuosic |
| Bourree/Gavotte | Clear phrasing, lighter texture |

## 7. Orchestration (Brandenburg Concertos as Model)

| Concerto | Unique Scoring | Innovation |
|---|---|---|
| No. 1 | 2 horns, 3 oboes, bassoon, violin piccolo | Largest forces |
| No. 2 | Trumpet, recorder, oboe, violin (concertino) | Brilliant high register |
| No. 3 | 3 violins, 3 violas, 3 cellos, continuo | Pure strings, 3-part grouping |
| No. 4 | Violin, 2 recorders | Virtuosic violin |
| No. 5 | Harpsichord, flute, violin | Harpsichord concerto birth |
| No. 6 | 2 violas, 2 gambas, cello, continuo | Dark, no violins |

### Orchestration Principles

| Principle | Description |
|---|---|
| Each instrument independent | Every part has contrapuntal interest |
| Obbligato winds | Winds have independent melodic lines, not just doubling |
| Color through register | Same instrument, different register = different character |
| Tutti vs solo clarity | Sharp contrast between full and reduced textures |
| Continuo always present | Never absent in ensemble music |

## 8. Organ Writing

| Feature | Description |
|---|---|
| Pedal independence | Feet play fully independent melodic line |
| Registration variety | Multiple manuals for dynamic/timbral contrast |
| Toccata virtuosity | Brilliant manual passages, dramatic pedal solos |
| Chorale treatment | Cantus firmus in any voice; embellished or plain |
| Trio sonata texture | Two manual voices + pedal = 3 independent lines |
| Plein jeu / Grand jeu | Full registration for climactic passages |

## 9. Keyboard Writing (Harpsichord/Clavichord)

| Feature | Description |
|---|---|
| Polyphonic | 2-5 voices, all independent |
| Style brise | Broken-chord arpeggiation (French influence) |
| Compound melody | Single line implies multiple voices |
| Ornaments | Mordents, trills, turns integral to line |
| Two-manual writing | Upper/lower keyboard for contrasting lines |
| Pedal harpsichord | Rare but used (some trio sonatas) |

## 10. Sacred Music Techniques

| Technique | Description |
|---|---|
| Chorale cantus firmus | Hymn tune as structural foundation |
| Word painting | Musical gestures depict text meaning |
| Numerology | Symbolic number relationships (e.g., 3 = Trinity) |
| Affect assignment | Each movement/aria represents one emotion |
| Instrumentation as symbol | Specific instruments represent theological ideas |
| Recitative types | Secco (continuo) and accompagnato (orchestra) |

## 11. Generation Guidelines

| Parameter | Guideline |
|---|---|
| Voice independence | EVERY voice must be melodically interesting |
| Motivic consistency | Derive all material from opening motif |
| Sequence use | Circle-of-5ths sequences are primary engine |
| Suspensions | Include 4-3 at all cadences; 7-6 chains in sequences |
| Chromaticism ratio | ~75% diatonic, ~25% chromatic (higher than peers) |
| Continuous motion | Avoid stopping; phrases elide |
| Counterpoint | At least 2 independent voices at all times |
| Bass line quality | Bass must be a singable, independent melody |
| Dance character | If suite movement, maintain dance rhythm strictly |
| Fugue rigor | Subject must be recognizable at every entry |
| Ornamentation | Trills at cadences, mordents on stressed beats |
| Texture density | 3-4 voices standard; never less than 2 in keyboard |
