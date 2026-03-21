# Baroque Forms Reference

## Suite Structure

Standard order (all movements share key):

| Position | Dance       | Meter | Tempo     | Character                        | Origin   |
|----------|-------------|-------|-----------|----------------------------------|----------|
| 1        | Prelude*    | free  | moderate  | improvisatory, toccata-like      | --       |
| 2        | Allemande   | 4/4   | moderate  | flowing, serious, contrapuntal   | German   |
| 3        | Courante    | 3/4   | moderate+ | running passages, cross-rhythms  | French   |
| 3 alt    | Corrente    | 3/4   | fast      | lighter, homophonic Italian style| Italian  |
| 4        | Sarabande   | 3/4   | slow      | stately, accent on beat 2        | Spanish  |
| 5        | Optional(s) | varies| varies    | galanteries -- see below         | various  |
| 6        | Gigue       | 6/8   | fast      | fugal, lively, compound meter    | British  |

*Optional. Present in English suites (Bach), often absent elsewhere.

### Optional Galanteries (inserted between Sarabande and Gigue)

| Dance      | Meter | Tempo    | Character                          |
|------------|-------|----------|------------------------------------|
| Minuet     | 3/4   | moderate | elegant, paired (I & II)           |
| Gavotte    | 2/2   | moderate | starts half-bar upbeat, cheerful   |
| Bourree    | 2/2   | fast     | starts quarter-note upbeat, lively |
| Passepied  | 3/8   | fast     | light, quick minuet variant        |
| Loure      | 6/4   | slow     | dotted rhythms, heavy              |
| Polonaise  | 3/4   | moderate | accented beat 1, feminine cadences |
| Air        | 4/4   | slow     | songlike, lyrical                  |
| Anglaise   | 4/4   | fast     | energetic, simple                  |

### Suite Section Proportions (typical bar counts)

| Dance      | A section | B section | Ratio A:B |
|------------|-----------|-----------|-----------|
| Allemande  | 8-16      | 12-24     | ~1:1.5    |
| Courante   | 8-16      | 12-20     | ~1:1.3    |
| Sarabande  | 8-12      | 12-16     | ~1:1.3    |
| Gigue      | 12-24     | 16-32     | ~1:1.4    |
| Minuet     | 8         | 8-16      | ~1:1.5    |
| Gavotte    | 8         | 8-12      | ~1:1.2    |
| Bourree    | 8         | 8-12      | ~1:1.2    |

### ABC Example -- Allemande Opening (Binary Form, D minor)

```abc
X:1
T:Allemande
M:4/4
L:1/16
K:Dm
Q:1/4=72
|:"A" A,2DE FAGF EDCE D2A,2|D4 F2A2 d2c2 B2A2|
G2FG A2Bc d2ef g2fe|dcBA GFED ^C2D2 E2^F2:|
|:"B" G2AB cBAG FGAB cdef|g2fe d2c2 B2A2 G2^F2|
G2AB c2de f2ed ^c2d2|e2d2 ^c2B2 A4 D4:|
```

---

## Binary Form

Used in virtually all Baroque dance movements.

### Simple Binary (Type 1)

```
||: A :||: B :||
   I->V     V->I
```

- A section: tonic to dominant (or relative major if minor key)
- B section: dominant area back to tonic
- No return of opening material in B

### Rounded Binary (Type 2)

```
||: A :||: B  A' :||
   I->V    V->..->I
```

- B section begins with development/new material
- A' = return of opening theme in tonic
- Precursor to sonata form

### Balanced Binary

```
||: A :||: B :||
   I->V     V->I
```

- End of B uses same cadential material as end of A, transposed to tonic

### Binary Form Key Scheme

| Section | Major Key      | Minor Key          |
|---------|----------------|--------------------|
| A open  | I              | i                  |
| A close | V (or iii)     | III (or v)         |
| B open  | V (or vi, iii) | III (or v, iv)     |
| B close | I              | i                  |

---

## Fugue Structure

### Exposition

```
Voice 1:  Subject (tonic)   ---  Countersubject  ---  free
Voice 2:  rest              Answer (dominant)     Countersubject  free
Voice 3:  rest              rest                  Subject (tonic) CS
Voice 4:  rest              rest                  rest            Answer
```

- **Subject**: main theme, in tonic
- **Answer**: subject at the 5th (real = exact interval, tonal = modified to stay in key)
- **Countersubject**: recurring counterpoint against answer/subject
- **Bridge/link**: short modulatory passage connecting subject to answer

### Real vs Tonal Answer

| Subject starts/ends | Answer type | Adjustment         |
|---------------------|-------------|--------------------|
| 1-5 (do-sol)        | Tonal       | 5-1 (sol-do)       |
| 5-1 (sol-do)        | Tonal       | 1-5 (do-sol)       |
| Stays near tonic    | Real        | Exact transposition |
| Modulates to V      | Tonal       | Modified intervals  |

### Post-Exposition Sections

| Section       | Function                                    | Typical Keys        |
|---------------|---------------------------------------------|----------------------|
| Episode 1     | Sequential development, modulation           | -> relative major/vi |
| Middle Entry  | Subject in new key                           | iii, vi, IV, ii      |
| Episode 2     | More distant modulation                      | -> iv, ii, bVI       |
| Entry         | Subject in remote key                        | various              |
| Stretto       | Overlapping subject entries                  | builds tension       |
| Pedal point   | Subject over dominant/tonic pedal            | V pedal -> I pedal   |
| Final entry   | Subject in tonic, strong cadence             | I                    |

### Fugue Proportions

| Voices | Typical Bars | Exposition | Episodes+Entries | Final Section |
|--------|-------------|------------|------------------|---------------|
| 2      | 30-50       | 20%        | 60%              | 20%           |
| 3      | 50-80       | 20%        | 60%              | 20%           |
| 4      | 70-120      | 15%        | 65%              | 20%           |
| 5      | 80-140      | 15%        | 65%              | 20%           |

### ABC Example -- 3-Voice Fugue Exposition (C major)

```abc
X:2
T:Fugue Exposition
M:4/4
L:1/8
K:C
V:1 name="Soprano"
V:2 name="Alto"
V:3 name="Bass"
[V:1] z8|z8|z8|CDEC DEFD|
[V:2] z8|CDEC DEFD|EFGE dcBA|GABG c4|
[V:3] CDEC DEFD|EFGE c2BA|G2G2 C4|z8|
```

---

## Ritornello Form

Used in Baroque concertos (concerto grosso and solo concerto).

### Structure

```
Rit1(I) -- Solo1 -- Rit2(V) -- Solo2 -- Rit3(vi) -- Solo3 -- Rit4(IV) -- Solo4 -- Rit5(I)
```

### Key Scheme (Major Key)

| Section  | Key      | Material                | Bars (approx %) |
|----------|----------|-------------------------|------------------|
| Rit 1    | I        | Full ritornello          | 15%              |
| Solo 1   | I -> V   | Virtuosic, thematic dev  | 15%              |
| Rit 2    | V        | Partial ritornello       | 8%               |
| Solo 2   | V -> vi  | New figuration           | 15%              |
| Rit 3    | vi       | Fragment of ritornello   | 5%               |
| Solo 3   | vi -> IV | Development, sequences   | 15%              |
| Rit 4    | IV or ii | Partial ritornello       | 5%               |
| Solo 4   | -> I     | Cadenza/virtuosity       | 12%              |
| Rit 5    | I        | Full or partial rit.     | 10%              |

### Key Scheme (Minor Key)

| Section  | Key         |
|----------|-------------|
| Rit 1    | i           |
| Rit 2    | III         |
| Rit 3    | v or iv     |
| Rit 4    | iv or VII   |
| Rit 5    | i           |

### Ritornello Internal Structure

```
[Head motif] -- [Continuation/Sequence] -- [Cadential figure]
    4 bars          4-8 bars                 2-4 bars
```

Partial ritornellos typically use Head motif only, or Head + Cadential.

---

## Concerto Grosso Structure

Three-movement plan:

| Movement | Tempo  | Form              | Character          |
|----------|--------|-------------------|--------------------|
| I        | Fast   | Ritornello        | Energetic, bold    |
| II       | Slow   | Binary/Free/Aria  | Lyrical, expressive|
| III      | Fast   | Ritornello/Fugal  | Dance-like, finale |

### Concertino vs Ripieno

| Group      | Typical Forces              | Role              |
|------------|-----------------------------|--------------------|
| Concertino | 2 violins + cello + continuo| Soloistic passages |
| Ripieno    | Full string orchestra        | Tutti sections     |

### Corelli Chiesa vs Camera

| Type    | Movements        | Character            |
|---------|------------------|----------------------|
| Chiesa  | Slow-Fast-Slow-Fast | Serious, contrapuntal |
| Camera  | Suite-like dances   | Dance-based, lighter  |

---

## Da Capo Aria (ABA)

```
A section (I) -- B section (contrast) -- A section da capo (with ornamentation)
```

| Section | Key           | Bars (approx) | Character              |
|---------|---------------|----------------|------------------------|
| A       | I -> V -> I   | 40-60%         | Main affect, ritornello|
| B       | vi, IV, ii, iii| 20-30%        | Contrasting affect     |
| A (d.c.)| I -> V -> I   | = A section    | Ornamented repeat      |

### A Section Internal Structure

```
Rit(orch) -- Vocal A1(I->V) -- Rit(partial) -- Vocal A2(->I) -- Rit(closing)
```

### Da Capo Conventions

| Convention             | Description                                      |
|------------------------|--------------------------------------------------|
| A section repeat       | Singer ornaments melody on return                |
| B section contrast     | Shorter, different affect/key/texture            |
| Opening ritornello     | Orchestra introduces A material                  |
| Closing ritornello     | Orchestra closes A section                       |
| Improvised cadenza     | Singer adds cadenza before final cadence of A    |

### ABC Example -- Da Capo Aria A Section (G major)

```abc
X:3
T:Da Capo Aria - A Section
M:3/4
L:1/8
K:G
%% Orchestral Ritornello
|:d4 B2|A4 G2|E2 G2 A2|B6|
d4 e2|d2 c2 B2|A2 B2 c2|d6:|
%% Vocal Entry
|B4 d2|c4 B2|A2 G2 ^F2|G6|
```

---

## Passacaglia / Chaconne

Ground bass (4-8 bars) repeated with continuous variation above.

### Ground Bass Patterns (common, in minor)

```abc
X:4
T:Passacaglia Bass Patterns
M:3/4
L:1/4
K:Dm
%% Pattern 1: Descending tetrachord (diatonic)
D2D|C2C|B,2B,|A,2A,|
%% Pattern 2: Chromatic descent
D2D|^C2C|C2=C|B,2B,|A,2A,|
%% Pattern 3: With leaps
D2A,|B,2^F,|G,2E,|A,3|
```

### Variation Techniques (cumulative intensity)

| Var Group | Technique                          | Texture            |
|-----------|------------------------------------|--------------------|
| 1-4       | Simple melody over bass            | Homophonic         |
| 5-8       | Running 8ths, arpeggiation         | Figural            |
| 9-12      | Running 16ths, scalar passages     | Virtuosic          |
| 13-16     | Syncopation, chromatic inflection  | Intensifying       |
| 17-20     | Mode change (major/minor switch)   | Contrast           |
| 21-24     | Dense counterpoint, stretto-like   | Climactic          |
| Final     | Return to simplicity or grand close| Resolution         |

### ABC Example -- Passacaglia Theme and First Variation

```abc
X:5
T:Passacaglia
M:3/4
L:1/8
K:Cm
V:1
V:2 clef=bass
%% Theme
[V:1] z6|z6|z6|z6|
[V:2] C,2C,2C,2|B,,2B,,2B,,2|A,,2A,,2A,,2|G,,4 z2|
%% Variation 1
[V:1] G2AB c2|d2 edc2|c2BA G2|G4 z2|
[V:2] C,2C,2C,2|B,,2B,,2B,,2|A,,2A,,2A,,2|G,,4 z2|
```

---

## French Overture

```
Slow (dotted) -- Fast (fugal) -- [Slow return]
```

| Section | Meter   | Tempo | Style                        | Proportion |
|---------|---------|-------|------------------------------|------------|
| A       | 4/4     | Grave | Dotted rhythms, majestic     | 30%        |
| B       | 3/4,4/4 | Allegro| Fugal/imitative, lighter   | 55%        |
| A'*     | 4/4     | Grave | Brief return of dotted style | 15%        |

*Optional. Sometimes B just slows at the end.

### Double-Dotting Convention

Notated dotted rhythms performed with even sharper inequality (near double-dotted).

### ABC Example -- French Overture Opening

```abc
X:6
T:French Overture
M:4/4
L:1/8
K:D
Q:1/4=56
|D3E F3G|A3B A2G2|F3E D3^C|D6 z2|
|D3E F3G|A2Bd c3B|A3G ^F3E|D6 z2|
```

### ABC Example -- French Overture Allegro (Fugal)

```abc
X:7
T:French Overture - Allegro
M:3/4
L:1/8
K:D
V:1
V:2
[V:1] D2 FAFA|Bd cBAG|F2 z6|z6|
[V:2] z6|z6|A,2 DEDE|FA GFED|
```

---

## Italian Overture (Sinfonia)

```
Fast -- Slow -- Fast (dance)
```

| Section | Meter | Tempo    | Style                    | Proportion |
|---------|-------|----------|--------------------------|------------|
| I       | 4/4   | Allegro  | Homophonic, brilliant    | 40%        |
| II      | 3/4   | Adagio   | Lyrical, thin texture    | 25%        |
| III     | 3/8   | Presto   | Dance-like, binary form  | 35%        |

### ABC Example -- Italian Overture Opening

```abc
X:8
T:Italian Overture - Allegro
M:4/4
L:1/16
K:D
|D4F4 A4d4|c4B4 A4G4|F4E4 D4^C4|D8 z8|
```

---

## Chorale Prelude Forms

| Type                  | Technique                                           | Voices |
|-----------------------|-----------------------------------------------------|--------|
| Cantus firmus         | Chorale in long notes (soprano), free counterpoint   | 3-4    |
| Chorale fugue         | Each chorale phrase = fugue subject                  | 3-4    |
| Chorale fantasia      | Elaborate, large-scale, ornamented cantus firmus     | 4-5    |
| Ornamental chorale    | Embellished chorale melody, homophonic accompaniment | 3-4    |
| Chorale canon         | Chorale melody in canon between two voices           | 3-4    |
| Chorale partita       | Theme and variations on chorale tune                 | varies |

### ABC Example -- Chorale Prelude (Cantus Firmus in Soprano)

```abc
X:9
T:Chorale Prelude
M:4/4
L:1/8
K:G
V:1 name="Soprano (Cantus Firmus)"
V:2 name="Alto"
V:3 name="Bass"
[V:1] G4 A4|B4 A4|G8|
[V:2] D2EF G2AB|d2cB A2GF|G2FE D4|
[V:3] G,2A,B, C2D2|G,2A,B, D2D,2|G,8|
```

---

## Toccata

| Feature    | Description                                        |
|------------|----------------------------------------------------|
| Character  | Improvisatory, virtuosic, free-form                |
| Sections   | Alternating free (scale runs, arpeggios) and strict (fugal) |
| Instrument | Organ or harpsichord                               |
| Purpose    | Display instrument and player capabilities         |
| Harmony    | Exploratory; establishes key through exploration   |
| Pairing    | Often paired with fugue (Toccata and Fugue)        |

### ABC Example -- Toccata Opening (D minor, Organ)

```abc
X:10
T:Toccata Opening
M:4/4
L:1/16
K:Dm
|A4 z4 G4 z4|F4 z4 E4 z4|
D2E2F2G2 A2B2c2d2|e2d2^c2d2 A4 z4|
```

---

## Prelude Types

| Type            | Description                                     |
|-----------------|-------------------------------------------------|
| Improvisatory   | Free, arpeggiated, exploratory (WTC preludes)   |
| Inventive       | Single motif developed continuously              |
| Dance-like      | Structured, rhythmic (some WTC preludes)         |
| Chorale prelude | Based on chorale melody (organ)                  |
| Pairing         | Before fugue, suite, or liturgical piece         |

---

## Baroque Cadence Types

| Cadence       | Bass Motion | Usage                          |
|---------------|-------------|--------------------------------|
| Perfect auth. | V -> I      | Section/piece endings          |
| Imperfect     | V -> I (inv)| Internal phrase endings        |
| Half          | -> V        | End of A section (binary)      |
| Deceptive     | V -> vi     | Avoid resolution, extend phrase|
| Phrygian      | iv6 -> V    | Minor key slow mvt endings     |
| Plagal        | IV -> I     | "Amen" cadence, codas          |
| Evaded        | V -> I6     | Continue motion, avoid closure |

---

## Trio Sonata / Solo Sonata

### Trio Sonata (2 melody + continuo)

| Type    | Movements        | Character            |
|---------|------------------|----------------------|
| Chiesa  | Slow-Fast-Slow-Fast | Serious, contrapuntal |
| Camera  | Suite dances        | Dance-based, lighter  |

### Solo Sonata (1 melody + continuo)

Same movement plans as trio sonata. Solo voice more virtuosic.

---

## Form-Function Quick Reference

| If generating...          | Use this form                      |
|---------------------------|------------------------------------|
| Concerto fast movement    | Ritornello form                    |
| Concerto slow movement    | Binary, ABA, or arioso             |
| Vocal aria                | Da capo (ABA)                      |
| Keyboard prelude          | Improvisatory or inventive         |
| Keyboard fugue            | Fugue (3-4 voices)                 |
| Dance movement            | Binary form with suite conventions |
| Ground bass piece         | Passacaglia/chaconne               |
| Orchestral opening        | French or Italian overture         |
| Chorale setting           | 4-part homophonic + passing tones  |
| Organ prelude             | Toccata, prelude, or chorale prelude|
| Chamber music             | Trio sonata or solo sonata (3-4 mvts)|

---

## Section ID Mapping for Baroque Forms

| Form            | Section IDs                                              |
|-----------------|----------------------------------------------------------|
| Suite-Allemande | `m1_allemande_a`, `m1_allemande_b`                       |
| Suite-Gigue     | `m6_gigue_a`, `m6_gigue_b`                               |
| Fugue           | `m1_expo`, `m1_ep1`, `m1_mid1`, `m1_ep2`, `m1_stretto`, `m1_coda` |
| Ritornello      | `m1_rit1`, `m1_solo1`, `m1_rit2`, `m1_solo2`, ...        |
| Da Capo Aria    | `m1_rit_a`, `m1_voc_a1`, `m1_voc_a2`, `m1_b`, `m1_dc`   |
| Passacaglia     | `m1_theme`, `m1_var01`, `m1_var02`, ...                   |
| French Overture | `m1_grave`, `m1_allegro`, `m1_grave_return`               |
| Italian Overture| `m1_allegro`, `m1_adagio`, `m1_presto`                    |
| Chorale Prelude | `m1_phrase1`, `m1_phrase2`, `m1_phrase3`, ...              |
| Trio Sonata     | `m1_adagio`, `m2_allegro`, `m3_adagio`, `m4_allegro`     |
