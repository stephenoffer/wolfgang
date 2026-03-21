# ABC Orchestral Writing Guide for w-compose

## Voice Naming Conventions

### Standard Orchestra Voice IDs

| Section | Voice ID | Full Name | Clef | Transposition |
|---------|----------|-----------|------|---------------|
| **Woodwinds** | | | | |
| Piccolo | `Picc` | Piccolo | treble | transpose=12 |
| Flute 1-2 | `Fl1`, `Fl2` | Flute | treble | none |
| Oboe 1-2 | `Ob1`, `Ob2` | Oboe | treble | none |
| English Horn | `EHn` | English Horn | treble | transpose=-7 |
| Clarinet Bb 1-2 | `Cl1`, `Cl2` | Clarinet in Bb | treble | transpose=-2 |
| Clarinet A | `ClA` | Clarinet in A | treble | transpose=-3 |
| Bass Clarinet | `BCl` | Bass Clarinet | treble | transpose=-14 |
| Bassoon 1-2 | `Bsn1`, `Bsn2` | Bassoon | bass | none |
| Contrabassoon | `CBsn` | Contrabassoon | bass | transpose=-12 |
| **Brass** | | | | |
| Horn F 1-4 | `Hn1`-`Hn4` | Horn in F | treble | transpose=-7 |
| Trumpet Bb 1-2 | `Tpt1`, `Tpt2` | Trumpet in Bb | treble | transpose=-2 |
| Trumpet C | `TptC1` | Trumpet in C | treble | none |
| Trombone 1-2 | `Tbn1`, `Tbn2` | Trombone | bass | none |
| Bass Trombone | `BTbn` | Bass Trombone | bass | none |
| Tuba | `Tba` | Tuba | bass | none |
| **Percussion** | | | | |
| Timpani | `Timp` | Timpani | bass | none |
| Snare Drum | `SD` | Snare Drum | perc | none |
| Bass Drum | `BD` | Bass Drum | perc | none |
| Cymbals | `Cym` | Cymbals | perc | none |
| Triangle | `Tri` | Triangle | perc | none |
| Glockenspiel | `Glock` | Glockenspiel | treble | transpose=24 |
| Harp | `Hp` | Harp | treble / bass | none |
| **Strings** | | | | |
| Violin I | `Vln1` | Violin I | treble | none |
| Violin II | `Vln2` | Violin II | treble | none |
| Viola | `Vla` | Viola | alto | none |
| Violoncello | `Vc` | Violoncello | bass | none |
| Contrabass | `Cb` | Contrabass | bass | transpose=-12 |

## Voice Declarations

### Full Header Example
```abc
V:Fl1 clef=treble name="Flute I" sname="Fl.I"
V:Ob1 clef=treble name="Oboe I" sname="Ob.I"
V:Cl1 clef=treble name="Clarinet in Bb I" sname="Cl.I" transpose=-2
V:Bsn1 clef=bass name="Bassoon I" sname="Bsn.I"
V:Hn1 clef=treble name="Horn in F I" sname="Hn.I" transpose=-7
V:Hn2 clef=treble name="Horn in F II" sname="Hn.II" transpose=-7
V:Tpt1 clef=treble name="Trumpet in Bb I" sname="Tpt.I" transpose=-2
V:Tbn1 clef=bass name="Trombone I" sname="Tbn.I"
V:Tba clef=bass name="Tuba" sname="Tba."
V:Timp clef=bass name="Timpani" sname="Timp."
V:Vln1 clef=treble name="Violin I" sname="Vln.I"
V:Vln2 clef=treble name="Violin II" sname="Vln.II"
V:Vla clef=alto name="Viola" sname="Vla."
V:Vc clef=bass name="Violoncello" sname="Vc."
V:Cb clef=bass name="Contrabass" sname="Cb."
```

### Staves Layout
```
%%staves [Fl1 Ob1 Cl1 Bsn1] [Hn1 Hn2 Tpt1 Tbn1 Tba] [Timp] [Vln1 Vln2 Vla Vc Cb]
```

Brackets group by family. Nested braces `{Vln1 Vln2}` for shared-staff divisi.

## Transposing Instruments

**Rule**: Write in concert pitch. The `transpose=` value tells the renderer to display at written pitch. Negative = sounds lower than written.

| Instrument | transpose= | Concert C sounds as written... |
|------------|-----------|-------------------------------|
| Bb Clarinet | -2 | D (written note = concert pitch + 2 semitones) |
| A Clarinet | -3 | Eb |
| F Horn | -7 | G |
| Bb Trumpet | -2 | D |
| English Horn | -7 | G |
| Piccolo | 12 | C an octave lower |
| Contrabass | -12 | C an octave higher |
| Bass Clarinet | -14 | Eb an octave higher |
| Contrabassoon | -12 | C an octave higher |
| Glockenspiel | 24 | C two octaves lower |

**In ABC body**: Always write **concert pitch**. The transpose parameter handles display.

## Writing for Strings

### Articulations and Techniques
```abc
% Pizzicato / Arco
[V:Vc] "pizz." C,2 E,2 G,2 C2 | "arco" !mf! (C,4 E,4) |

% Tremolo (notated as repeated notes or with !trem! decoration)
[V:Vln1] !trem! A4 !trem! G4 |

% Double stop (use chord notation within a single voice)
[V:Vln1] [e2a2] [d2g2] [c2f2] [B2e2] |

% Divisi (use separate voice labels)
V:Vln1a clef=treble name="Violin I div.a"
V:Vln1b clef=treble name="Violin I div.b"

% Bowings
[V:Vln1] !downbow! C4 !upbow! D4 | !downbow! (EFGA) |

% Sul ponticello / sul tasto
[V:Vln1] "sul pont." e4 f4 | "ord." g8 |

% Harmonics
[V:Vln1] !open! e'4 |

% Mute
[V:Vln1] "con sord." !pp! e4 d4 c4 B4 |
[V:Vln1] "senza sord." !mf! e4 d4 c4 B4 |
```

### String Ranges (Concert Pitch)

| Instrument | Low | High (orchestral safe) | ABC Low | ABC High |
|------------|-----|----------------------|---------|----------|
| Violin | G3 | E7 | `G,` | `e'''` |
| Viola | C3 | A6 | `C,` | `a''` |
| Cello | C2 | A5 | `C,,` | `a'` |
| Contrabass | E1 (sounds) | G4 (sounds) | `E,,,` | `G` |

## Writing for Winds

### Breath and Articulation
```abc
% Staccato passage
[V:Fl1] .c .d .e .f | .g .a .b .c' |

% Legato / slurred phrase
[V:Ob1] (cdef) (gabc') |

% Tonguing emphasis
[V:Cl1] !accent!c2 !accent!e2 !accent!g2 !accent!c'2 |

% Flutter tongue
[V:Fl1] "flz." !trill! c'4 |
```

### Wind Ranges (Concert Pitch)

| Instrument | Low | High (safe) | ABC Low | ABC High |
|------------|-----|-------------|---------|----------|
| Flute | C4 | C7 | `C` | `c'''` |
| Oboe | Bb3 | A6 | `_B,` | `a''` |
| Clarinet Bb | D3 (sounds) | Bb6 (sounds) | `D,` | `_b''` |
| Bassoon | Bb1 | Eb5 | `_B,,,` | `_e'` |

## Writing for Brass

### Techniques
```abc
% Muted brass
[V:Tpt1] "con sord." !mp! c2 e2 g2 c'2 |
[V:Tpt1] "open" !f! c'4 g4 |

% Horn stopped
[V:Hn1] "+" c2 "o" e4 c2 |

% Sforzando brass accent
[V:Tbn1] !sfz! C,4 z4 |

% Fanfare pattern
[V:Tpt1] !ff! c2c2 g,2c2 | e2g2 c'4 |
```

### Brass Ranges (Concert Pitch)

| Instrument | Low | High (safe) | ABC Low | ABC High |
|------------|-----|-------------|---------|----------|
| Horn F | B1 (sounds) | F5 (sounds) | `B,,,` | `f'` |
| Trumpet Bb | E3 (sounds) | Bb5 (sounds) | `E,` | `_b'` |
| Trombone | E2 | Bb4 | `E,,` | `_b` |
| Tuba | D1 | F4 | `D,,,,` | `F` |

## Writing for Timpani

```abc
V:Timp clef=bass name="Timpani" sname="Timp."
% Standard tuning notes written as played
[V:Timp] !f! C,4 z2 G,,2 | C,2 C,2 G,,4 |

% Roll (tremolo)
[V:Timp] !trem! C,8 |

% Tuning change
[V:Timp] "muta C in D" Z2 | D,4 A,,4 |
```

## Writing for Unpitched Percussion

```abc
V:SD clef=perc stafflines=1 name="Snare Drum" sname="S.D."
V:BD clef=perc stafflines=1 name="Bass Drum" sname="B.D."
% Use a single pitch (e.g., c) as placeholder
[V:SD] c2 cc c2 cc | c4 z4 |
[V:BD] c4 z2 c2 | c4 c4 |
```

## Dynamics and Expression

### Dynamic Markings (inline decorations)
```abc
!ppp! !pp! !p! !mp! !mf! !f! !ff! !fff!
!sfz! !sfp! !fp!
```

### Hairpins
```abc
[V:Vln1] !p! !crescendo(! CDEF | GABc !crescendo)! !f! c'4 z4 |
[V:Vln1] !f! !diminuendo(! c'BAG | FEDC !diminuendo)! !pp! C8 |
```

### MIDI Program (for playback, optional)
```abc
%%MIDI program 40    % Violin
%%MIDI program 68    % Oboe
%%MIDI program 56    % Trumpet
%%MIDI program 47    % Timpani
```

### Rehearsal Marks
```abc
"^A" CDEF GABc |    % Rehearsal letter A above staff
"^B" efga bc'de' |
```

## Texture Examples

### Homophonic (hymn-like)
```abc
X:1
T:Homophonic Texture
M:4/4
L:1/4
V:Vln1 clef=treble
V:Vln2 clef=treble
V:Vla clef=alto
V:Vc clef=bass
K:C
[V:Vln1] e d c d | e2 e2 |
[V:Vln2] c B A B | c2 c2 |
[V:Vla] G G E G | G2 G2 |
[V:Vc] C, G,, A,, G,, | C,2 C,2 |
```

### Contrapuntal (fugal entries)
```abc
X:1
T:Contrapuntal Texture
M:4/4
L:1/8
V:Vln1 clef=treble
V:Vln2 clef=treble
V:Vla clef=alto
V:Vc clef=bass
K:C
[V:Vln1] CDEF GABc | d2c2 B2A2 | G8 |
[V:Vln2] z8 | CDEF GABc | d2c2 B2A2 |
[V:Vla] z8 | z8 | C,D,E,F, G,A,B,C |
[V:Vc] z8 | z8 | z8 |
```

### Melody + Accompaniment
```abc
X:1
T:Melody and Accompaniment
M:3/4
L:1/8
V:Fl1 clef=treble
V:Vln1 clef=treble
V:Vln2 clef=treble
V:Vla clef=alto
V:Vc clef=bass
K:G
[V:Fl1] !mf! (B2 d2) (g2 | f2 e2) d2 |
[V:Vln1] !p! GB dB GB | AF cA FA |
[V:Vln2] !p! D2 G2 B2 | C2 F2 A2 |
[V:Vla] !p! G,2 B,2 D2 | A,2 C2 E2 |
[V:Vc] !p! G,4 G,2 | D,4 D,2 |
```

## Full Orchestral Score Template

```abc
X:1
T:Title - Movement Name
C:Wolfgang
M:4/4
L:1/8
Q:1/4=120
%%staves [Fl1 Ob1] [Cl1 Bsn1] [Hn1 Hn2] [Tpt1 Tbn1] [Timp] [Vln1 Vln2 Vla Vc Cb]
V:Fl1 clef=treble name="Flute" sname="Fl."
V:Ob1 clef=treble name="Oboe" sname="Ob."
V:Cl1 clef=treble name="Clarinet in Bb" sname="Cl." transpose=-2
V:Bsn1 clef=bass name="Bassoon" sname="Bsn."
V:Hn1 clef=treble name="Horn in F 1" sname="Hn.1" transpose=-7
V:Hn2 clef=treble name="Horn in F 2" sname="Hn.2" transpose=-7
V:Tpt1 clef=treble name="Trumpet in Bb" sname="Tpt." transpose=-2
V:Tbn1 clef=bass name="Trombone" sname="Tbn."
V:Timp clef=bass name="Timpani" sname="Timp."
V:Vln1 clef=treble name="Violin I" sname="Vln.I"
V:Vln2 clef=treble name="Violin II" sname="Vln.II"
V:Vla clef=alto name="Viola" sname="Vla."
V:Vc clef=bass name="Violoncello" sname="Vc."
V:Cb clef=bass name="Contrabass" sname="Cb."
K:C
%
[V:Fl1] z8 |
[V:Ob1] z8 |
[V:Cl1] z8 |
[V:Bsn1] z8 |
[V:Hn1] z8 |
[V:Hn2] z8 |
[V:Tpt1] z8 |
[V:Tbn1] z8 |
[V:Timp] z8 |
[V:Vln1] z8 |
[V:Vln2] z8 |
[V:Vla] z8 |
[V:Vc] z8 |
[V:Cb] z8 |
```

## Checklist Before Finalizing

1. Every voice has the same number of bars
2. Every bar sums to the correct beat count for the meter
3. Transposing instruments written in concert pitch with `transpose=` in V:
4. Clef assignments correct for each instrument
5. Note ranges within safe limits for each instrument
6. Dynamics present in all voices (not just melody)
7. Articulations consistent within sections
8. `K:` is the last header field before body
9. No leading barlines on first bar
10. Ties only cross barlines (use longer duration within a bar)
