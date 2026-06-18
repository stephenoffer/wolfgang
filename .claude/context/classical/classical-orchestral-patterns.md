# Classical Orchestral Patterns

Genre-wide orchestral patterns common across the Classical period (c. 1750-1820). These patterns appear in works by Haydn, Mozart, Beethoven, and their contemporaries. Each entry includes a name, reference, 2-4 bar ABC notation with multi-voice scoring, usage context, and a variation suggestion.

---

## Tutti Patterns

### OP1. Full Orchestral Tutti (Homophonic)
**Ref:** Mozart Symphony No. 41, I; Haydn Symphony No. 104, I
```abc
X:300
T:Full Tutti (Homophonic)
M:4/4
L:1/8
K:D
V:Fl name="Flute" clef=treble
!f! d4 c4 | B4 A4 | d8 |
V:Ob name="Oboe" clef=treble
!f! d4 c4 | B4 A4 | d8 |
V:Vn1 name="Violin I" clef=treble
!f! d4 c4 | B4 A4 | d8 |
V:Vn2 name="Violin II" clef=treble
!f! F4 A4 | D4 F4 | A8 |
V:Vla name="Viola" clef=alto
!f! A,4 E4 | B,4 D4 | F8 |
V:Hn name="Horn (D)" clef=treble
!f! [DA]8 | [DA]8 | [DA]8 |
V:Tpt name="Trumpet (D)" clef=treble
!f! D4 D4 | D4 D4 | D8 |
V:Timp name="Timpani"
!f! D,4 A,,4 | D,4 A,,4 | D,8 |
V:Vc name="Cello/Bass" clef=bass
!f! D,4 A,,4 | G,,4 D,4 | D,8 |
```
**Context:** Opening statements, cadential arrivals, recapitulation entries; maximum orchestral weight.
**Variation:** Omit trumpets and timpani for a slightly softer tutti in flat keys where they cannot play.

### OP2. Tutti Unison Octaves
**Ref:** Beethoven Symphony No. 5, I; Mozart Symphony No. 40, I
```abc
X:301
T:Tutti Unison Octaves
M:4/4
L:1/8
K:Cm
V:Vn1 name="Violin I" clef=treble
!ff! G4 _E4 | F4 D4 | C8 |
V:Vn2 name="Violin II" clef=treble
!ff! G4 _E4 | F4 D4 | C8 |
V:Vla name="Viola" clef=alto
!ff! G,4 _E,4 | F,4 D,4 | C,8 |
V:Ob name="Oboe" clef=treble
!ff! G4 _E4 | F4 D4 | C8 |
V:Cl name="Clarinet" clef=treble
!ff! G4 _E4 | F4 D4 | C8 |
V:Bsn name="Bassoon" clef=bass
!ff! G,4 _E,4 | F,4 D,4 | C,8 |
V:Vc name="Cello/Bass" clef=bass
!ff! G,,4 _E,,4 | F,,4 D,,4 | C,,8 |
```
**Context:** Dramatic statements, opening motives, development climaxes; raw power through unison.
**Variation:** Break the unison on the last beat with harmonization for a sudden textural bloom.

### OP3. Forte-Piano (fp) Punctuation
**Ref:** Haydn Symphony No. 44 "Trauer," I; Mozart Symphony No. 40, I
```abc
X:302
T:Forte-Piano Punctuation
M:4/4
L:1/8
K:Dm
V:Vn1 name="Violin I" clef=treble
!fp! [DA]4 z4 | !fp! [CF]4 z4 | !fp! [DA]4 z4 | !fp! [EG]4 z4 |
V:Vn2 name="Violin II" clef=treble
!fp! [DF]4 z4 | !fp! [CA]4 z4 | !fp! [DF]4 z4 | !fp! [CE]4 z4 |
V:Vla name="Viola" clef=alto
!fp! D,4 z4 | !fp! C,4 z4 | !fp! D,4 z4 | !fp! C,4 z4 |
V:Vc name="Cello" clef=bass
!fp! D,4 z4 | !fp! F,4 z4 | !fp! D,4 z4 | !fp! C,4 z4 |
```
**Context:** Dramatic gestures, Sturm und Drang passages; the sudden drop after impact creates urgency.
**Variation:** Add string tremolo on the piano continuation for sustained tension.

---

## Wind Choir Patterns

### OP4. Paired-Wind Chorale
**Ref:** Mozart Symphony No. 39, II; Beethoven Symphony No. 6, II
```abc
X:303
T:Wind Chorale (Paired Winds)
M:4/4
L:1/4
K:Bb
V:Ob1 name="Oboe I" clef=treble
!p! B c d c | B2 z2 |
V:Ob2 name="Oboe II" clef=treble
!p! F A B A | F2 z2 |
V:Cl1 name="Clarinet I" clef=treble
!p! d e f e | d2 z2 |
V:Cl2 name="Clarinet II" clef=treble
!p! B c d c | B2 z2 |
V:Bsn1 name="Bassoon I" clef=bass
!p! B, C D C | B,2 z2 |
V:Bsn2 name="Bassoon II" clef=bass
!p! F, G, A, G, | F,2 z2 |
```
**Context:** Slow movements, pastoral passages; winds create a warm, organ-like chorale texture.
**Variation:** Add horns sustaining root and 5th beneath the wind choir for a richer foundation.

### OP5. Wind Soli over Pizzicato Strings
**Ref:** Mozart Concerto K. 482, II; Haydn Symphony No. 101, II
```abc
X:304
T:Wind Solo over Pizzicato Strings
M:4/4
L:1/8
K:C
V:Ob name="Oboe (solo)" clef=treble
!p! C2E2 G2c2 | B2A2 G2F2 | E4 z4 |
V:Vn1 name="Violin I (pizz.)" clef=treble
z2 [CE]2 z2 [CE]2 | z2 [DF]2 z2 [DF]2 | [CE]4 z4 |
V:Vn2 name="Violin II (pizz.)" clef=treble
z2 G,2 z2 G,2 | z2 A,2 z2 A,2 | G,4 z4 |
V:Vc name="Cello (pizz.)" clef=bass
C,2 z2 C,2 z2 | G,,2 z2 G,,2 z2 | C,4 z4 |
```
**Context:** Slow movement second themes, lyrical digressions; intimate, chamber-like color.
**Variation:** Transfer the solo to clarinet for warmer, more legato character.

### OP6. Wind Call and Response
**Ref:** Mozart Symphony No. 41, II; Beethoven Symphony No. 4, II
```abc
X:305
T:Wind Call and Response
M:4/4
L:1/8
K:F
V:Fl name="Flute" clef=treble
!p! F2A2 c2f2 | z8 | e2d2 c2B2 | z8 |
V:Ob name="Oboe" clef=treble
z8 | !p! A2c2 e2a2 | z8 | g2f2 e2d2 |
V:Bsn name="Bassoon" clef=bass
F,4 F,4 | F,4 F,4 | C,4 C,4 | C,4 C,4 |
```
**Context:** Slow movements, development episodes; winds pass phrases between each other in dialogue.
**Variation:** Add a third instrument entering in stretto (overlapping the end of the second phrase).

---

## String Writing Patterns

### OP7. Melody and Accompaniment (Standard Texture)
**Ref:** Mozart Eine kleine Nachtmusik, I; Haydn "Surprise" Symphony, I
```abc
X:306
T:String Melody + Accompaniment
M:4/4
L:1/8
K:G
V:Vn1 name="Violin I" clef=treble
!p! G2B2 d4 | e2d2 c2B2 | A2c2 e2d2 | d4 z4 |
V:Vn2 name="Violin II" clef=treble
D2D2 D2D2 | E2E2 F2F2 | F2F2 G2G2 | D4 z4 |
V:Vla name="Viola" clef=alto
B,2B,2 B,2B,2 | C2C2 D2D2 | D2D2 E2E2 | B,4 z4 |
V:Vc name="Cello/Bass" clef=bass
G,4 G,4 | C,4 D,4 | D,4 C,4 | G,4 z4 |
```
**Context:** First and second themes; Vn I carries the melody, inner voices provide harmonic rhythm.
**Variation:** Transfer melody to Vn II or Viola for a richer, darker tonal quality.

### OP8. String Tremolo (Sustained Agitation)
**Ref:** Mozart Don Giovanni Overture; Beethoven Coriolan Overture
```abc
X:307
T:String Tremolo (Dramatic)
M:4/4
L:1/32
K:Dm
V:Vn1 name="Violin I" clef=treble
!pp! D2D2D2D2D2D2D2D2 | !cresc! D2D2D2D2D2D2D2D2 | !f! D2D2D2D2D2D2D2D2 |
V:Vn2 name="Violin II" clef=treble
!pp! A,2A,2A,2A,2A,2A,2A,2A,2 | A,2A,2A,2A,2A,2A,2A,2A,2 | !f! A,2A,2A,2A,2A,2A,2A,2A,2 |
V:Vla name="Viola" clef=alto
!pp! F,2F,2F,2F,2F,2F,2F,2F,2 | F,2F,2F,2F,2F,2F,2F,2F,2 | !f! F,2F,2F,2F,2F,2F,2F,2F,2 |
V:Vc name="Cello" clef=bass
!pp! D,8 | !cresc! D,8 | !f! D,4 A,,4 |
```
**Context:** Opera overtures, dramatic development sections, storm depictions; sustained tremolo with crescendo.
**Variation:** Add a solo wind line (oboe or flute) above the tremolo carpet for a melody-over-agitation texture.

### OP9. Pizzicato Accompaniment
**Ref:** Haydn Symphony No. 101 "Clock," II; Mozart Serenade K. 525, II
```abc
X:308
T:Pizzicato String Accompaniment
M:4/4
L:1/8
K:F
V:Vn1 name="Violin I (arco melody)" clef=treble
!p! F2A2 c2f2 | e2d2 c2B2 |
V:Vn2 name="Violin II (pizz.)" clef=treble
z2 [Ac]2 z2 [Ac]2 | z2 [GB]2 z2 [GB]2 |
V:Vla name="Viola (pizz.)" clef=alto
F,2 z2 F,2 z2 | C,2 z2 C,2 z2 |
V:Vc name="Cello (pizz.)" clef=bass
F,2 z2 F,2 z2 | C,2 z2 C,2 z2 |
```
**Context:** Slow movements, dance movements, lighter passages; delicate rhythmic support.
**Variation:** Alternate pizzicato and arco within the same passage for textural variety.

### OP10. Syncopated Inner Voices
**Ref:** Mozart Symphony No. 40, I (Vn II and Vla); Beethoven Symphony No. 3, I
```abc
X:309
T:Syncopated Inner Voices
M:4/4
L:1/8
K:Gm
V:Vn1 name="Violin I (melody)" clef=treble
G2_B2 d4 | _e2d2 c2_B2 | A2d2 c2_B2 | _B4 A4 |
V:Vn2 name="Violin II (syncopation)" clef=treble
z2 D2 z2 D2 | z2 _E2 z2 _E2 | z2 F2 z2 F2 | z2 F2 z2 F2 |
V:Vla name="Viola (syncopation)" clef=alto
z2 _B,2 z2 _B,2 | z2 G,2 z2 G,2 | z2 F,2 z2 D,2 | z2 D,2 z2 C,2 |
V:Vc name="Cello" clef=bass
G,4 G,4 | C,4 _E,4 | F,4 D,4 | _B,,4 F,,4 |
```
**Context:** First movements; the offbeat inner voices create rhythmic propulsion and agitation beneath the melody.
**Variation:** Move the syncopation to the bass for a more destabilizing effect.

### OP11. String Unison Passage (Octaves)
**Ref:** Beethoven Symphony No. 5, I; Haydn Symphony No. 44, I
```abc
X:310
T:String Unison Passage
M:4/4
L:1/8
K:Cm
V:Vn1 name="Violin I" clef=treble
!f! C2D2 _E2F2 | G4 _A4 | G2F2 _E2D2 | C8 |
V:Vn2 name="Violin II" clef=treble
!f! C2D2 _E2F2 | G4 _A4 | G2F2 _E2D2 | C8 |
V:Vla name="Viola" clef=alto
!f! C,2D,2 _E,2F,2 | G,4 _A,4 | G,2F,2 _E,2D,2 | C,8 |
V:Vc name="Cello/Bass" clef=bass
!f! C,2D,2 _E,2F,2 | G,4 _A,4 | G,2F,2 _E,2D,2 | C,8 |
```
**Context:** Opening themes, development climaxes; concentrated power, no harmony -- just the line.
**Variation:** Break into harmony on the final note (all instruments take different chord tones) for resolution.

---

## Horn Patterns

### OP12. Sustained Horn Pedal (Tonic or Dominant)
**Ref:** Mozart Symphony No. 39, I; Haydn Symphony No. 103, throughout
```abc
X:311
T:Horn Pedal (Tonic and Dominant)
M:4/4
L:1/2
K:Eb
V:Hn1 name="Horn I (Eb)" clef=treble
E E | E E | B, B, | E E |
V:Hn2 name="Horn II (Eb)" clef=treble
B, B, | B, B, | E, E, | B, B, |
V:Vn1 name="Violin I" clef=treble
E2 | G2 | F2 | E2 |
V:Vc name="Cello" clef=bass
E,2 | C,2 | B,,2 | E,2 |
```
**Context:** Throughout movements; horns sustain tonic/dominant while strings and winds create harmonic motion above.
**Variation:** Use stopped horn notes for brief chromatic passing tones in the pedal voice.

### OP13. Horn Call (Hunting/Heroic)
**Ref:** Haydn Symphony No. 73 "La Chasse"; Mozart Horn Concerto K. 447
```abc
X:312
T:Horn Call (Hunting)
M:6/8
L:1/8
K:D
V:Hn1 name="Horn I (D)" clef=treble
!f! D2D D2D | A2A d3 | A2D D2D | D3 z3 |
V:Hn2 name="Horn II (D)" clef=treble
!f! D,2D, D,2D, | D2D A3 | D2D, D,2D, | D,3 z3 |
```
**Context:** Hunting scenes, menuetto trios, heroic passages; natural horn arpeggios on the harmonic series.
**Variation:** Soften to pp and slow the tempo for a distant, nostalgic echo effect.

### OP14. Horn Dialogue with Strings
**Ref:** Mozart Symphony No. 38 "Prague," I; Beethoven Symphony No. 3, III
```abc
X:313
T:Horn-String Dialogue
M:3/4
L:1/4
K:Eb
V:Hn name="Horn (Eb)" clef=treble
!f! E G B | e2 z | z3 | z3 |
V:Vn1 name="Violin I" clef=treble
z3 | z3 | !p! e d c | B2 z |
V:Vc name="Cello" clef=bass
E,2 E, | E,2 z | E, F, G, | E,2 z |
```
**Context:** Menuetto trios, development episodes; horn states a figure and strings answer or elaborate.
**Variation:** Have the horn enter in stretto (overlapping the string answer) for intensification.

---

## Timpani Patterns

### OP15. Tonic-Dominant Punctuation
**Ref:** Mozart Symphony No. 41; Haydn Symphony No. 104
```abc
X:314
T:Timpani Punctuation (Tonic-Dominant)
M:4/4
L:1/4
K:D
V:Timp name="Timpani"
!f! D A, D A, | D D D z | A, A, D D | D2 z2 |
V:Tpt name="Trumpet (D)" clef=treble
!f! D A, D A, | D D D z | A, A, D D | D2 z2 |
```
**Context:** Tutti forte passages; timpani and trumpet reinforce strong beats and cadences.
**Variation:** Add a timpani roll on the dominant before the final tonic for suspense.

### OP16. Timpani Roll (Dramatic)
**Ref:** Haydn Symphony No. 103 "Drumroll"; Beethoven Symphony No. 5, II
```abc
X:315
T:Timpani Roll (Dramatic Introduction)
M:4/4
L:1/1
K:Eb
V:Timp name="Timpani"
!pp! E,4~ | !cresc! E,4~ | !f! E,4 | z4 |
V:Vc name="Cello (sustained)" clef=bass
!pp! E,4~ | E,4~ | !f! E,4 | z4 |
```
**Context:** Slow introductions, retransitions, dramatic suspense; the roll builds tension before a key arrival.
**Variation:** Use a dominant roll (rather than tonic) to increase harmonic tension before resolution.

---

## Mannheim Effects

### OP17. Mannheim Rocket (Full Orchestra)
**Ref:** Mozart Symphony No. 40, I; Stamitz symphonies
```abc
X:316
T:Mannheim Rocket (Full Orchestra)
M:4/4
L:1/16
K:D
V:Vn1 name="Violin I" clef=treble
!p! D4F4A4d4 | !f! f4e4d4c4 |
V:Vn2 name="Violin II" clef=treble
!p! D4F4A4d4 | !f! d4c4B4A4 |
V:Vla name="Viola" clef=alto
!p! D,4F,4A,4D4 | !f! A4G4F4E4 |
V:Ob name="Oboe" clef=treble
z16 | !f! f4e4d4c4 |
V:Vc name="Cello/Bass" clef=bass
!p! D,4F,4A,4D4 | !f! D4 z4 D,8 |
```
**Context:** Energetic opening gestures, transition passages; rapid ascending arpeggio with crescendo.
**Variation:** Invert the rocket (descending) for a sighing, deflating gesture.

### OP18. Mannheim Roller (Extended Crescendo)
**Ref:** Stamitz Sinfonia in D; Haydn Symphony No. 103 (adapted)
```abc
X:317
T:Mannheim Roller (Extended Crescendo)
M:4/4
L:1/8
K:C
V:Vn1 name="Violin I" clef=treble
!pp! C2C2C2C2 | !p! E2E2E2E2 | !mf! G2G2G2G2 | !f! c2c2c2c2 |
V:Vn2 name="Violin II" clef=treble
!pp! C2C2C2C2 | !p! C2C2C2C2 | !mf! E2E2E2E2 | !f! G2G2G2G2 |
V:Vla name="Viola" clef=alto
z8 | !p! G,2G,2G,2G,2 | !mf! C2C2C2C2 | !f! E2E2E2E2 |
V:Vc name="Cello" clef=bass
!pp! C,8 | C,8 | C,8 | !f! C,8 |
```
**Context:** Transition passages, codas; a sustained chord grows in dynamic and register simultaneously.
**Variation:** Add instruments one per bar (strings, then oboes, then horns, then full tutti).

### OP19. Mannheim Sigh (Descending Appoggiatura)
**Ref:** J.C. Bach symphonies; Mozart early symphonies
```abc
X:318
T:Mannheim Sigh
M:4/4
L:1/8
K:Eb
V:Vn1 name="Violin I" clef=treble
!mf! B4 !p! A4 | !mf! G4 !p! F4 | E8 |
V:Vn2 name="Violin II" clef=treble
!mf! G4 !p! F4 | !mf! E4 !p! D4 | B,8 |
V:Vla name="Viola" clef=alto
E,2E,2 E,2E,2 | E,2E,2 B,,2B,,2 | E,8 |
V:Vc name="Cello" clef=bass
E,4 F,4 | E,4 B,,4 | E,8 |
```
**Context:** Expressive lyrical passages, galant-style themes; the appoggiatura resolves downward with a decrescendo.
**Variation:** Layer multiple sighs in staggered entries for a chain of overlapping expressiveness.

---

## Texture and Dynamic Patterns

### OP20. Tutti-to-Chamber Reduction
**Ref:** Mozart Symphony No. 40, I (P to S transition); Haydn "London" symphonies
```abc
X:319
T:Tutti to Chamber Reduction
M:4/4
L:1/8
K:G
V:Fl name="Flute" clef=treble
!f! d4 B4 | d8 | z8 | z4 d2e2 |
V:Ob name="Oboe" clef=treble
!f! d4 B4 | d8 | z8 | z8 |
V:Vn1 name="Violin I" clef=treble
!f! d4 B4 | d8 | !p! B2A2 G2F2 | G4 z4 |
V:Vn2 name="Violin II" clef=treble
!f! B4 G4 | B8 | !p! G2F2 E2D2 | D4 z4 |
V:Vc name="Cello" clef=bass
!f! G,4 D,4 | G,8 | !p! G,2 z2 D,2 z2 | G,4 z4 |
```
**Context:** Transitions between first and second themes; the texture thins suddenly as dynamic drops.
**Variation:** Thin the texture gradually over 4 bars rather than suddenly for a more Haydnesque approach.

### OP21. Crescendo to Fortissimo Arrival
**Ref:** Beethoven Symphony No. 3, I (recapitulation); Mozart Symphony No. 41, IV
```abc
X:320
T:Crescendo to Fortissimo Arrival
M:4/4
L:1/8
K:C
V:Vn1 name="Violin I" clef=treble
!p! G,2C2 E2G2 | !cresc! c2e2 g2c'2 | !ff! [Gc']8 |
V:Vn2 name="Violin II" clef=treble
!p! E,2G,2 C2E2 | !cresc! G2c2 e2g2 | !ff! [Ee]8 |
V:Ob name="Oboe" clef=treble
z8 | !cresc! c2e2 g2c'2 | !ff! c'8 |
V:Hn name="Horn" clef=treble
z8 | !cresc! [CE]4 [CE]4 | !ff! [CE]8 |
V:Timp name="Timpani"
z8 | !cresc! C,4 G,,4 | !ff! C,8 |
V:Vc name="Cello/Bass" clef=bass
!p! C,4 E,4 | !cresc! G,4 C4 | !ff! C,8 |
```
**Context:** Recapitulation arrivals, coda climaxes; the orchestra gradually builds to maximum force.
**Variation:** Delay the full fortissimo by one extra bar for heightened anticipation.

### OP22. Pianissimo String Carpet (Sotto Voce)
**Ref:** Mozart Symphony No. 39, I (S theme); Haydn "Surprise" Symphony, II
```abc
X:321
T:Pianissimo String Carpet
M:4/4
L:1/8
K:Bb
V:Vn1 name="Violin I" clef=treble
!pp! B,2D2 F2B2 | A2G2 F2E2 |
V:Vn2 name="Violin II" clef=treble
!pp! F,2B,2 D2F2 | E2D2 C2B,2 |
V:Vla name="Viola" clef=alto
!pp! D,2F,2 B,2D2 | C2B,2 A,2G,2 |
V:Vc name="Cello" clef=bass
!pp! B,,4 B,,4 | F,,4 F,,4 |
```
**Context:** Second theme presentations, transitions to solo passages; hushed, intimate string texture.
**Variation:** Add a single sustained horn note for warmth beneath the whispered strings.

### OP23. Dramatic Grand Pause
**Ref:** Haydn Symphony No. 94, I; Mozart Don Giovanni, I
```abc
X:322
T:Grand Pause (Full Orchestra)
M:4/4
L:1/4
K:D
V:All name="All instruments" clef=treble
!ff! [DFA]2 [DFA]2 | z4 | z4 | !p! D2 F2 |
V:Vc name="Cello/Bass" clef=bass
!ff! D,2 D,2 | z4 | z4 | !p! D,2 z2 |
```
**Context:** After climactic tutti passages; a full bar (or more) of silence creates shock, suspense, or humor.
**Variation:** Use a fermata over the rest to let the silence stretch uncomfortably for maximum drama.

### OP24. Antiphonal Winds and Strings
**Ref:** Mozart Symphony No. 41, I; Beethoven Symphony No. 1, II
```abc
X:323
T:Antiphonal Exchange
M:4/4
L:1/8
K:C
V:Ob name="Winds (phrase)" clef=treble
!p! C2E2 G2c2 | z8 | B2A2 G2F2 | z8 |
V:Vn1 name="Strings (answer)" clef=treble
z8 | !p! e2d2 c2B2 | z8 | A2G2 F2E2 |
V:Vc name="Cello" clef=bass
C,4 z4 | G,4 z4 | G,4 z4 | C,4 z4 |
```
**Context:** Lyrical passages, exposition second groups; spatial dialogue between wind and string choirs.
**Variation:** Overlap the phrases by one beat for a more continuous flow.

---

## Formal-Function Patterns

### OP25. Opening Fanfare (Trumpets + Timpani)
**Ref:** Haydn Symphony No. 97 (C major); Mozart Symphony No. 34
```abc
X:324
T:Opening Fanfare
M:4/4
L:1/8
K:C
V:Tpt name="Trumpet (C)" clef=treble
!ff! C4 C4 | C2G,2 C2E2 | G4 C4 | C8 |
V:Timp name="Timpani"
!ff! C,4 C,4 | C,2G,,2 C,2C,2 | G,,4 C,4 | C,8 |
V:Hn name="Horn" clef=treble
!ff! [CE]4 [CE]4 | [CG]4 [CE]4 | [CE]4 [CE]4 | [CE]8 |
```
**Context:** Ceremonial openings in C or D major; trumpets and timpani establish festive character.
**Variation:** Follow the fanfare immediately with a pianissimo string theme for maximum contrast.

### OP26. Cadential Reinforcement (V-I)
**Ref:** Universal Classical cadence orchestration
```abc
X:325
T:Cadential Reinforcement (Full Orchestra)
M:4/4
L:1/4
K:D
V:Vn1 name="Violin I" clef=treble
!f! E F | !ff! D2 z2 |
V:Vn2 name="Violin II" clef=treble
!f! C D | !ff! A,2 z2 |
V:Ob name="Oboe" clef=treble
!f! E F | !ff! D2 z2 |
V:Hn name="Horn (D)" clef=treble
!f! [EA]2 | !ff! [DA]2 z2 |
V:Tpt name="Trumpet" clef=treble
!f! A, D | !ff! D2 z2 |
V:Timp name="Timpani"
!f! A, D, | !ff! D,2 z2 |
V:Vc name="Cello/Bass" clef=bass
!f! A, D, | !ff! D,2 z2 |
```
**Context:** Movement endings, section cadences, exposition closes; every instrument reinforces V-I.
**Variation:** Repeat the cadence 3-4 times (Mozart's "opera buffa" close) for emphatic finality.

### OP27. Retransition Dominant Pedal
**Ref:** Haydn Symphony No. 104, I development; Mozart Symphony No. 40, I
```abc
X:326
T:Retransition Dominant Pedal
M:4/4
L:1/8
K:G
V:Vn1 name="Violin I" clef=treble
!p! F2E2 D2^C2 | D2E2 F2G2 | !cresc! A2B2 c2d2 | !f! d4 B4 |
V:Vn2 name="Violin II" clef=treble
!p! D2D2 D2D2 | D2D2 D2D2 | D2D2 D2D2 | !f! D4 D4 |
V:Hn name="Horn" clef=treble
D8 | D8 | D8 | !f! D8 |
V:Vc name="Cello/Bass" clef=bass
D,8 | D,8 | D,8 | !f! D,4 G,,4 |
```
**Context:** End of development, before recapitulation; dominant pedal builds maximum harmonic tension.
**Variation:** Add a timpani roll on the dominant note for extra suspense before the tonic arrival.
