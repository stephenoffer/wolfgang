# Ensemble Templates Reference

## String Quartet

**Forces:** Violin I, Violin II, Viola, Violoncello

```abc
%%score [Vln1 Vln2 Vla Vc]
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla clef=alto name="Viola" snm="Vla"
V:Vc clef=bass name="Violoncello" snm="Vc"
```

| Voice | Typical Role |
|---|---|
| Vln I | Melody, highest voice, virtuosic passages |
| Vln II | Harmony, countermelody, dialogue with Vln I |
| Vla | Inner voice, harmonic fill, occasional melody |
| Vc | Bass line, melody (esp. tenor register), countermelody |

**Scoring notes:** All four voices should be melodically interesting. Frequent role-swapping. Dialogue between Vln I and Vc is idiomatic. Double stops extend harmonic possibilities.

## String Orchestra

**Forces:** Violin I, Violin II, Viola, Violoncello, Contrabass

```abc
%%score [(Vln1 Vln2) (Vla) (Vc Cb)]
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla clef=alto name="Viola" snm="Vla"
V:Vc clef=bass name="Violoncello" snm="Vc"
V:Cb clef=bass name="Contrabass" snm="Cb"
```

| Voice | Typical Role |
|---|---|
| Vln I | Principal melody, upper voice |
| Vln II | Harmony, countermelody, parallel motion with Vln I |
| Vla | Inner harmony, rhythmic figures, countermelody |
| Vc | Bass line, tenor melody, harmonic anchor |
| Cb | Bass reinforcement (often doubles Vc 8vb), pizz. bass |

**Scoring notes:** Cb typically doubles Vc but can have independent lines. Divisi available in all sections. Typical section sizes: Vln I (8-12), Vln II (8-10), Vla (6-8), Vc (4-6), Cb (3-4).

## Classical Orchestra

**Forces:** Strings + 2Fl, 2Ob, 2Cl(Bb), 2Bsn, 2Hn(F), 2Tpt(Bb/C), Timpani

```abc
%%score [(Fl1 Fl2) (Ob1 Ob2) (Cl1 Cl2) (Bsn1 Bsn2)] [(Hn1 Hn2) (Tpt1 Tpt2)] [Timp] [(Vln1 Vln2) (Vla) (Vc Cb)]
V:Fl1 clef=treble name="Flute 1" snm="Fl 1"
V:Fl2 clef=treble name="Flute 2" snm="Fl 2"
V:Ob1 clef=treble name="Oboe 1" snm="Ob 1"
V:Ob2 clef=treble name="Oboe 2" snm="Ob 2"
V:Cl1 clef=treble name="Clarinet 1 in Bb" snm="Cl 1" transpose=-2
V:Cl2 clef=treble name="Clarinet 2 in Bb" snm="Cl 2" transpose=-2
V:Bsn1 clef=bass name="Bassoon 1" snm="Bsn 1"
V:Bsn2 clef=bass name="Bassoon 2" snm="Bsn 2"
V:Hn1 clef=treble name="Horn 1 in F" snm="Hn 1" transpose=-7
V:Hn2 clef=treble name="Horn 2 in F" snm="Hn 2" transpose=-7
V:Tpt1 clef=treble name="Trumpet 1 in Bb" snm="Tpt 1" transpose=-2
V:Tpt2 clef=treble name="Trumpet 2 in Bb" snm="Tpt 2" transpose=-2
V:Timp clef=bass name="Timpani" snm="Timp"
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla clef=alto name="Viola" snm="Vla"
V:Vc clef=bass name="Violoncello" snm="Vc"
V:Cb clef=bass name="Contrabass" snm="Cb"
```

| Group | Role |
|---|---|
| Strings | Foundation: melody, bass, inner voices, everything |
| Woodwinds in pairs | Color, doubling, solo passages, dialogue with strings |
| 2 Horns | Sustain, harmonic fill, bridge between strings and winds |
| 2 Trumpets | Fanfare, rhythmic accent, reinforce forte passages |
| Timpani | Rhythmic punctuation, tonic/dominant pedals |

**Scoring notes:** Haydn/Mozart model. Winds often double strings or provide sustained harmony. Brass limited to notes of the harmonic series in period style. Timpani tuned to tonic/dominant.

## Romantic Orchestra

**Forces:** Strings + 2Fl+Picc, 2Ob+EngHn, 2Cl+BsCl, 2Bsn+Cbsn, 4Hn, 2Tpt, 3Tbn, Tuba, Timp, Perc, Harp

```abc
%%score [(Picc) (Fl1 Fl2) (Ob1 Ob2) (EngHn) (Cl1 Cl2) (BsCl) (Bsn1 Bsn2) (Cbsn)] [(Hn1 Hn2 Hn3 Hn4) (Tpt1 Tpt2) (Tbn1 Tbn2 Tbn3) (Tuba)] [(Timp) (Perc)] [(Harp)] [(Vln1 Vln2) (Vla) (Vc Cb)]
V:Picc clef=treble name="Piccolo" snm="Picc" octave=1
V:Fl1 clef=treble name="Flute 1" snm="Fl 1"
V:Fl2 clef=treble name="Flute 2" snm="Fl 2"
V:Ob1 clef=treble name="Oboe 1" snm="Ob 1"
V:Ob2 clef=treble name="Oboe 2" snm="Ob 2"
V:EngHn clef=treble name="English Horn" snm="E.Hn" transpose=-7
V:Cl1 clef=treble name="Clarinet 1 in Bb" snm="Cl 1" transpose=-2
V:Cl2 clef=treble name="Clarinet 2 in Bb" snm="Cl 2" transpose=-2
V:BsCl clef=treble name="Bass Clarinet in Bb" snm="B.Cl" transpose=-14
V:Bsn1 clef=bass name="Bassoon 1" snm="Bsn 1"
V:Bsn2 clef=bass name="Bassoon 2" snm="Bsn 2"
V:Cbsn clef=bass name="Contrabassoon" snm="Cbsn" octave=-1
V:Hn1 clef=treble name="Horn 1 in F" snm="Hn 1" transpose=-7
V:Hn2 clef=treble name="Horn 2 in F" snm="Hn 2" transpose=-7
V:Hn3 clef=treble name="Horn 3 in F" snm="Hn 3" transpose=-7
V:Hn4 clef=treble name="Horn 4 in F" snm="Hn 4" transpose=-7
V:Tpt1 clef=treble name="Trumpet 1 in Bb" snm="Tpt 1" transpose=-2
V:Tpt2 clef=treble name="Trumpet 2 in Bb" snm="Tpt 2" transpose=-2
V:Tbn1 clef=bass name="Trombone 1" snm="Tbn 1"
V:Tbn2 clef=bass name="Trombone 2" snm="Tbn 2"
V:Tbn3 clef=bass name="Trombone 3 (Bass)" snm="B.Tbn"
V:Tuba clef=bass name="Tuba" snm="Tba"
V:Timp clef=bass name="Timpani" snm="Timp"
V:Perc clef=perc name="Percussion" snm="Perc"
V:Harp clef=treble name="Harp" snm="Hp"
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla clef=alto name="Viola" snm="Vla"
V:Vc clef=bass name="Violoncello" snm="Vc"
V:Cb clef=bass name="Contrabass" snm="Cb"
```

| Group | Role |
|---|---|
| Strings | Core melody, lush divisi, tremolo for drama |
| WW (with doublings) | Color solos, doubling melodies, timbral variety |
| 4 Horns | Sustained harmony, heroic melodies, tutti power, glue |
| Tpt + Tbn + Tuba | Climax power, chorale, rhythmic drive |
| Harp | Arpeggiated color, harmonic support, glissandi |
| Timpani + Perc | Rhythmic backbone, dramatic accents, color |

## Late Romantic / Large Orchestra

**Forces:** Triple or quadruple winds. 6-8 Horns. Expanded percussion section (Triangle, Cymbals, Bass Drum, Snare, Tam-tam, Tubular Bells, Glockenspiel, Xylophone, Celesta). 2 Harps.

**Additional voice headers:**
```abc
V:Fl3 clef=treble name="Flute 3" snm="Fl 3"
V:Ob3 clef=treble name="Oboe 3" snm="Ob 3"
V:Cl3 clef=treble name="Clarinet 3 in Bb" snm="Cl 3" transpose=-2
V:Bsn3 clef=bass name="Bassoon 3" snm="Bsn 3"
V:Hn5 clef=treble name="Horn 5 in F" snm="Hn 5" transpose=-7
V:Hn6 clef=treble name="Horn 6 in F" snm="Hn 6" transpose=-7
V:Tpt3 clef=treble name="Trumpet 3 in Bb" snm="Tpt 3" transpose=-2
V:Harp2 clef=treble name="Harp 2" snm="Hp 2"
V:Cel clef=treble name="Celesta" snm="Cel" octave=1
```

**Scoring notes:** Mahler, Strauss, Bruckner model. Enormous dynamic range. Extended solo passages for all instruments. Complex layered textures. Divisi strings a3 or a4.

## Chamber Ensembles

### Piano Trio (Violin, Cello, Piano)
```abc
%%score [Vln Vc Pno]
V:Vln clef=treble name="Violin" snm="Vln"
V:Vc clef=bass name="Violoncello" snm="Vc"
V:Pno clef=treble name="Piano" snm="Pno"
```

| Voice | Role |
|---|---|
| Violin | Upper melody, virtuosic passages |
| Cello | Bass, countermelody, tenor melody |
| Piano | Harmonic foundation, melody, accompaniment, independent |

### Wind Quintet (Flute, Oboe, Clarinet, Horn, Bassoon)
```abc
%%score [Fl Ob Cl Hn Bsn]
V:Fl clef=treble name="Flute" snm="Fl"
V:Ob clef=treble name="Oboe" snm="Ob"
V:Cl clef=treble name="Clarinet in Bb" snm="Cl" transpose=-2
V:Hn clef=treble name="Horn in F" snm="Hn" transpose=-7
V:Bsn clef=bass name="Bassoon" snm="Bsn"
```

| Voice | Role |
|---|---|
| Fl | Upper melody, agile passages |
| Ob | Melody, expressive solos |
| Cl | Melody, agile runs, wide-range flexibility |
| Hn | Harmonic fill, sustained notes, melody |
| Bsn | Bass, tenor melody, comic character |

### Piano Quintet (2 Violins, Viola, Cello, Piano)
```abc
%%score [(Vln1 Vln2) (Vla) (Vc)] [Pno]
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla clef=alto name="Viola" snm="Vla"
V:Vc clef=bass name="Violoncello" snm="Vc"
V:Pno clef=treble name="Piano" snm="Pno"
```

### Brass Quintet (2 Trumpets, Horn, Trombone, Tuba)
```abc
%%score [Tpt1 Tpt2 Hn Tbn Tuba]
V:Tpt1 clef=treble name="Trumpet 1 in Bb" snm="Tpt 1" transpose=-2
V:Tpt2 clef=treble name="Trumpet 2 in Bb" snm="Tpt 2" transpose=-2
V:Hn clef=treble name="Horn in F" snm="Hn" transpose=-7
V:Tbn clef=bass name="Trombone" snm="Tbn"
V:Tuba clef=bass name="Tuba" snm="Tba"
```

### String Sextet (2 Violins, 2 Violas, 2 Cellos)
```abc
%%score [Vln1 Vln2 Vla1 Vla2 Vc1 Vc2]
V:Vln1 clef=treble name="Violin I" snm="Vln I"
V:Vln2 clef=treble name="Violin II" snm="Vln II"
V:Vla1 clef=alto name="Viola I" snm="Vla I"
V:Vla2 clef=alto name="Viola II" snm="Vla II"
V:Vc1 clef=bass name="Violoncello I" snm="Vc I"
V:Vc2 clef=bass name="Violoncello II" snm="Vc II"
```

### Octet (String Quartet + Wind Quartet or Double Quartet)
Common configurations:
- Schubert Octet: Cl, Hn, Bsn + Vln, Vla, Vc, Cb
- Mendelssohn Octet: 4 Vln, 2 Vla, 2 Vc
- Stravinsky Octet: Fl, Cl, 2 Bsn, 2 Tpt, 2 Tbn

## Solo Concerto Orchestras

### Piano Concerto Orchestra
Typically Classical or Romantic orchestra. Piano part on grand staff.
```abc
V:Pno_R clef=treble name="Piano" snm="Pno"
V:Pno_L clef=bass name="" snm=""
```
**Scoring notes:** Orchestra reduces to p/mp when piano plays melody. Orchestral tuttis between solo sections. Wind solos dialogue with piano. Avoid doubling piano melody in strings (muddies).

### Violin Concerto Orchestra
Standard orchestra, often without 2nd pair of horns in Classical. Solo violin part notated above Vln I.
```abc
V:Solo clef=treble name="Solo Violin" snm="Solo"
```
**Scoring notes:** Accompaniment must be very light (pp-mp) during solo passages. Avoid high woodwinds doubling solo line. Low strings and winds provide harmonic bed.

### Cello Concerto Orchestra
Standard orchestra. Solo cello notated above orchestral cellos.
```abc
V:Solo clef=bass name="Solo Violoncello" snm="Solo Vc"
```
**Scoring notes:** Most challenging balance — solo cello in tenor range can be covered easily. Keep accompaniment very thin. Avoid bass instruments playing in the same register as soloist.

## Seating Chart Implications for Spatial Effects

### Standard Modern Seating
```
                    [Conductor]
          Vln I (L)          Vln II (R)
     Vla (center-R)      Vc (center-L)
              Cb (far right/back)
    Fl  Ob  |  Cl  Bsn       (behind strings)
       Hn   |  Tpt  Tbn  Tuba (behind winds)
            Timp + Perc        (back center/L)
            Harp               (far left)
```

### Spatial Scoring Techniques
| Effect | Technique | Example |
|---|---|---|
| Stereo melody | Vln I (L) echoed by Vln II (R) | Antiphonal passages |
| Depth layering | Strings (front) vs brass (back) | Foreground/background |
| Surround sweep | Melody passes L to center to R | Vln I > Vla > Vc |
| Brass wall | All brass together (back center) | Power climaxes |
| Intimate chamber | Solo strings or winds (front) | Quiet passages |
| Wide spread | Harp (far L) + Perc (far R) | Coloristic effects |

### Alternative Seating: Vln I / Vln II Antiphonal
```
                    [Conductor]
          Vln I (L)          Vln II (R)
               Vla (center)
          Vc (inner L)    Cb (inner R)
```
Used for antiphonal string writing (Mahler, some Baroque). Enhances dialogue between violin sections.
