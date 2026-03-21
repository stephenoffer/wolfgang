# Arvo Part (b. 1935) — Composer Profile

## Harmonic Language

| Parameter | Value |
|-----------|-------|
| System | Tintinnabuli (from 1976 onward) |
| Tonality | Triadic, single triad as harmonic center |
| Modulation | Rare — pieces often stay in one tonal center |
| Dissonance | Passing only, from M-voice motion against T-voice |
| Chord types | Root position triads, open voicings, bare octaves |
| Cadences | Often unresolved; fade to silence |
| Key preference | A minor, D minor, white-note modes |

### Tintinnabuli System — Core Principle

Two voice types combine:
- **M-voice** (melodic): stepwise motion, scale-based
- **T-voice** (tintinnabuli): arpeggiated triad notes only

| Voice | Motion | Pitch Source | Character |
|-------|--------|-------------|-----------|
| M-voice | Stepwise (up or down from center) | Scale degrees | Searching, human |
| T-voice | Nearest triad tone (above or below) | Triad (e.g., A-C-E) | Bell-like, eternal |

### T-voice Position Rules

| Position | Rule | From M-note D (A minor triad A-C-E) |
|----------|------|--------------------------------------|
| 1st superior | Nearest triad tone above | E |
| 2nd superior | Second nearest triad tone above | A |
| 1st inferior | Nearest triad tone below | C |
| 2nd inferior | Second nearest triad tone below | A |
| Alternating | Alternates superior/inferior | E, C, A, A... |

### ABC — Tintinnabuli Demonstration (A minor)
```abc
X:1
T:Tintinnabuli - M-voice and T-voice
M:4/4
L:1/4
K:Am
V:1 name="M-voice" clef=treble
%% Stepwise descent from E
E D C B, | A, B, C D | E F G A | G F E D |
V:2 name="T-voice (1st superior)" clef=treble
%% Nearest A-minor triad tone above each M-note
E E C C | A C C E | E A A A | A A E E |
```

### ABC — Tintinnabuli (1st inferior position)
```abc
X:2
T:Tintinnabuli - 1st inferior T-voice
M:4/4
L:1/4
K:Am
V:1 name="M-voice"
A B c d | e d c B | A G F E |
V:2 name="T-voice (1st inferior)"
%% Nearest A-minor triad tone below each M-note
E A A C | C C A A | E E E C |
```

## Melodic Style

| Parameter | Value |
|-----------|-------|
| Motion | Almost exclusively stepwise |
| Range | Narrow to moderate (octave to 10th) |
| Center tone | Often A, D, or E — M-voice orbits this pitch |
| Direction | Systematic: ascending, descending, or expanding |
| Ornamentation | None — absolute austerity |
| Repetition | Patterns repeat with systematic expansion |
| Silence | Integral — rests are structural, not decorative |

### M-voice Motion Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| Descending scale | Steps down from starting tone | E D C B A |
| Ascending scale | Steps up from starting tone | A B C D E |
| Expanding wedge | Alternates above/below center | A B A G A C A F |
| Contracting wedge | Narrows toward center | E ... F ... D ... G ... C |
| Palindrome | Forward then reversed | A B C D E D C B A |

### ABC — Expanding Wedge M-voice
```abc
X:3
T:Expanding wedge from A
M:free
L:1/4
K:Am
A | B A | G A | c A | F A | d A | E A | e A |
```

### Phrase Length by Text Syllables

| Text Element | Musical Result |
|-------------|----------------|
| 1 syllable | 1 note |
| 2 syllables | 2 notes |
| Comma | Short rest |
| Period | Long rest (often full bar) |
| Paragraph | Extended silence |

## Rhythmic Characteristics

| Parameter | Value |
|-----------|-------|
| Pulse | Slow, often imperceptible |
| Tempo | Typically MM=40-72 |
| Meter | Often free or long bars |
| Rhythm source | Text syllables in choral works |
| Note values | Whole notes, half notes dominate |
| Acceleration | Rare — systematic when present |
| Rubato | Not indicated; performers add naturally |

### Duration Systems

| System | Rule | Example Work |
|--------|------|-------------|
| Syllabic | 1 syllable = 1 note, equal duration | Passio |
| Proportional | Phrase length = syllable count | Magnificat |
| Additive | Each phrase adds one note | Fur Alina |
| Palindromic | Durations mirror around center | Cantus |

### ABC — Syllabic Rhythm (text-driven)
```abc
X:4
T:Text-driven rhythm example
M:free
L:1/4
K:Am
w: Do- mi- ne,  De- us me- us.
   A   B   C  z D  E  F   E  z2 |
```

### ABC — Additive Rhythm (Fur Alina style)
```abc
X:5
T:Additive phrase lengths
M:free
L:1/2
K:Bm
%% Phrase 1: 1 note
B z2 |
%% Phrase 2: 2 notes
B A z2 |
%% Phrase 3: 3 notes
B c d z2 |
%% Phrase 4: 4 notes
B A G F z2 |
%% Phrase 5: 5 notes
B c d e f z2 |
```

## Preferred Forms

| Form | Description | Example |
|------|-------------|---------|
| Through-composed | No repetition, text dictates form | Passio |
| Arch / palindrome | Climax at center, mirror structure | Cantus |
| Additive | Expanding phrase structure | Fur Alina |
| Sectional (text) | Sections follow liturgical text | Te Deum, Magnificat |
| Symmetrical | Binary or ternary with exact symmetry | Tabula Rasa |
| Descending process | Continuous descent, expanding canon | Cantus in Memory of Benjamin Britten |

### Cantus Form (Descending Canon)
```
Layer 1 (Violin I):    whole notes, descending A scale
Layer 2 (Violin II):   half notes, descending, enters 1 bar later
Layer 3 (Viola):        quarter notes, descending, enters 2 bars later
Layer 4 (Cello):        eighth notes, descending, enters 3 bars later
Layer 5 (Bass):         sixteenth notes, descending, enters 4 bars later
Bell:                   A, marking structural points
All converge on low A unison at climax.
```

### ABC — Cantus-style Descending Canon
```abc
X:6
T:Descending canon (Cantus-inspired)
M:4/4
L:1/4
K:Am
Q:1/4=56
V:1 name="Violin I"
A4 | G4 | F4 | E4 | D4 | C4 | B,4 | A,4 |
V:2 name="Violin II"
z4 | A2 G2 | F2 E2 | D2 C2 | B,2 A,2 | G,2 F,2 | E,2 D,2 | C,4 |
V:3 name="Viola" clef=alto
z4 | z4 | A, B, C D | E F G A | G F E D | C B, A, G, | F, E, D, C, | B,,4 |
V:4 name="Cello" clef=bass
z4 | z4 | z4 | A,B,CD EFGA | GFED CB,A,G, | F,E,D,C, B,,A,,G,,F,, | E,,4 z2 z2 | A,,4 |
```

## Orchestration

| Ensemble | Instruments | Example Work |
|----------|-------------|-------------|
| Solo piano | Piano alone | Fur Alina |
| Solo + piano | Violin/cello + piano | Spiegel im Spiegel |
| String orchestra | Strings + bell | Cantus, Fratres (version) |
| Chamber | Varied small forces | Fratres (multiple versions) |
| Choir + organ | SATB, organ | Magnificat, Te Deum |
| Choir + orchestra | Full forces | Passio, Te Deum |

### Texture Characteristics

| Texture | Description | Usage |
|---------|-------------|-------|
| Monophony | Single line, unison | Opening statements |
| Two-part tintinnabuli | M-voice + T-voice | Core texture throughout |
| Doubled tintinnabuli | M+T in multiple octaves | Climactic passages |
| Homorhythmic choir | All voices same rhythm | Text declamation |
| Unison | All instruments on same pitch | Structural arrival |
| Silence | Extended rests | Between sections, phrases |

### Dynamic Approach

| Dynamic | Usage |
|---------|-------|
| ppp-pp | Most common; default level |
| p-mp | Normal melodic passages |
| mf-f | Rare; reserved for structural climax |
| ff | Extremely rare; single climactic moment |
| Crescendo | Very gradual — over 8-32 bars |
| Decrescendo | Fade to niente common |
| Subito changes | Almost never used |

### ABC — Spiegel im Spiegel Style
```abc
X:7
T:Spiegel im Spiegel style
M:6/4
L:1/4
K:F
Q:1/4=56
V:1 name="Violin"
z2 z2 A2 | A2 G2 F2 | z2 z A2 G | F2 G2 A2 |
B2 A2 G2 | A2 z2 z2 | z2 z2 C'2 | B2 A2 G2 |
V:2 name="Piano" clef=bass
[F,A,C]6 | [F,A,C]6 | [F,A,C]6 | [F,A,C]6 |
[F,A,C]6 | [F,A,C]6 | [F,A,C]6 | [F,A,C]6 |
```

### ABC — Fratres-Style Tintinnabuli (String Orchestra)
```abc
X:8
T:Fratres-style passage
M:7/4
L:1/4
K:Am
Q:1/4=60
V:1 name="Violin I"
E F G A G F E | D E F G F E D | C D E F E D C |
V:2 name="Violin II (T-voice, 1st sup)"
E A A A A A E | E E A A A E E | C E E A E E C |
V:3 name="Viola" clef=alto
A, B, C D C B, A, | G, A, B, C B, A, G, | E, G, A, B, A, G, E, |
V:4 name="Cello" clef=bass
A,, E, A, C A, E, A,, | G,, E, A, C A, E, G,, | C, E, A, C A, E, C, |
V:5 name="Bass" clef=bass
A,,2 z z z z A,, | G,,2 z z z z G,, | C,2 z z z z C, |
```

## Representative Works — Quick Reference

| Work | Year | Forces | Key Technique | Duration |
|------|------|--------|---------------|----------|
| Fur Alina | 1976 | Piano | First tintinnabuli work, additive | 3 min |
| Tabula Rasa | 1977 | 2 violins, strings, piano | Tintinnabuli, two movements | 26 min |
| Fratres | 1977+ | Multiple versions | Tintinnabuli, arch form | 10 min |
| Cantus in Memory of Britten | 1977 | Strings + bell | Descending canon, proportional | 6 min |
| Spiegel im Spiegel | 1978 | Violin/cello + piano | Additive melody, arpeggiated piano | 8 min |
| Passio | 1982 | Soloists, choir, ensemble | Text-driven, syllabic | 70 min |
| Te Deum | 1984-85 | Choir, strings, tape | Large-scale tintinnabuli | 30 min |
| Magnificat | 1989 | Choir | Pure choral tintinnabuli | 7 min |
| Berliner Messe | 1990-92 | Choir, strings, organ | Liturgical, tintinnabuli | 25 min |
| Lamentate | 2002 | Piano + orchestra | Large-scale, dramatic | 35 min |

## Style Emulation Parameters

| Parameter | Setting |
|-----------|---------|
| Tempo | MM=40-72 (slow) |
| Key | A minor, D minor, F major preferred |
| Time signature | Free, 3/4, 4/4, 6/4, 7/4 |
| Texture | 2-part tintinnabuli minimum |
| Harmonic rhythm | Static — often single triad for entire piece |
| Dynamic range | ppp to mf (ff only at single climax) |
| Silence proportion | 15-30% of total duration |
| Articulation | Sustained, connected, no accents |
| Vibrato | Minimal to none (historically informed) |
| Register | Middle — extremes avoided except for effect |

## Generating Tintinnabuli — Step by Step

1. **Choose tonal center**: Select root triad (e.g., A minor: A-C-E)
2. **Compose M-voice**: Write stepwise melody around center tone
3. **Determine T-voice position**: Choose 1st/2nd superior/inferior
4. **Generate T-voice**: For each M-note, find nearest triad tone per rule
5. **Set rhythm**: Text syllables or systematic additive/proportional
6. **Set dynamics**: Start pp, single gradual arc if any
7. **Add silence**: Insert structural rests between phrases
8. **Orchestrate**: Minimal forces, exposed writing, doubled at octave for climax

### T-Voice Lookup Table (A minor: A-C-E)

| M-note | 1st Sup | 2nd Sup | 1st Inf | 2nd Inf |
|--------|---------|---------|---------|---------|
| A | C | E | E (below) | C (below) |
| B | C | E | A | E |
| C | E | A | A | E |
| D | E | A | C | A |
| E | A | C | C | A |
| F | A | C | E | C |
| G | A | C | E | C |

## Common Pitfalls When Emulating Part

| Mistake | Correction |
|---------|------------|
| Too many notes | Reduce; silence is structural |
| Chromatic motion in M-voice | Keep strictly diatonic/modal |
| T-voice deviates from triad | T-voice uses ONLY triad tones |
| Fast tempo | Slow down; Part is rarely above MM=72 |
| Thick orchestration | Thin out; 2-3 real voices maximum |
| Dynamic extremes | Stay soft; ff is once per piece at most |
| Developing themes | No development — process unfolds systematically |
| Adding expression marks | Minimal markings; austerity is the aesthetic |
| Ignoring silence | Rests must be proportionally significant |
| Harmonic complexity | One triad can sustain an entire piece |
