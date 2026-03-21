# Chord Vocabulary Reference

## Chord Types

| Type | Symbol | Structure (semitones) | Example in C | Typical Periods |
|------|--------|-----------------------|-------------|-----------------|
| Major triad | I | 0-4-7 | C E G | All |
| Minor triad | i | 0-3-7 | C Eb G | All |
| Diminished triad | vii° | 0-3-6 | B D F | All |
| Augmented triad | III+ | 0-4-8 | C E G# | Romantic+ |
| Dominant 7th | V7 | 0-4-7-10 | G B D F | All |
| Major 7th | Imaj7 | 0-4-7-11 | C E G B | Impressionist+ |
| Minor 7th | ii7 | 0-3-7-10 | D F A C | Classical+ |
| Half-dim 7th | iiø7 | 0-3-6-10 | B D F A | All |
| Fully-dim 7th | vii°7 | 0-3-6-9 | B D F Ab | Baroque+ |
| Dom 9th | V9 | 0-4-7-10-14 | G B D F A | Romantic+ |
| Dom 11th | V11 | 0-4-7-10-14-17 | G B D F A C | Late-Romantic+ |
| Dom 13th | V13 | 0-4-7-10-14-17-21 | G B D F A C E | Impressionist+ |
| Italian +6 | It+6 | b6-1-#4 | Ab C F# | Classical+ |
| French +6 | Fr+6 | b6-1-2-#4 | Ab C D F# | Classical+ |
| German +6 | Ger+6 | b6-1-b3-#4 | Ab C Eb F# | Classical+ |
| Neapolitan | N or bII | bII in 1st inv | Db F Ab | Classical+ |
| Aug Dom | V+7 | 0-4-8-10 | G B D# F | Romantic+ |

## Roman Numeral Conventions

| Notation | Meaning |
|----------|---------|
| Upper case (I, IV, V) | Major triad |
| Lower case (ii, iii, vi) | Minor triad |
| ° | Diminished (vii°) |
| + | Augmented (III+) |
| 7, 9, 11, 13 | Extensions (V7, V9) |
| maj7 | Major seventh (Imaj7) |
| ø7 | Half-diminished (iiø7) |
| Figured bass (6, 6/4, 4/3, 4/2) | Inversions |
| / | Secondary function (V/V = V of V) |
| b, # before numeral | Chromatic alteration (bVI, #iv°) |

## ABC Chord Notation

Chords appear as quoted strings above the staff in ABC:
```abc
X:1
T:Chord symbols in ABC
M:4/4
L:1/4
K:C
"C"C E G c|"F"F A c f|"G7"G B d f|"C"e2 c2|
```

Guitar-chord style with positions:
```abc
"Am"A, C E A|"Dm"D F A d|"E7"E ^G B e|"Am"A2 c2|
```

For analysis annotations use `"^text"` above or `"_text"` below:
```abc
"^I""C"C E G c|"^IV""F"F A c f|"^V7""G7"G B d f|"^I""C"e2 c2|
```

## Common Progressions by Period

### Baroque (1600-1750)
```abc
%%% Circle of fifths
"^I"C2"^IV"F2|"^vii°"B,2"^iii"E2|"^vi"A,2"^ii"D2|"^V"G,2"^I"C2|
```
- Circle of 5ths: I-IV-vii°-iii-vi-ii-V-I
- Descending tetrachord bass: i-v6-iv6-V (Lament)
- Romanesca: I-V-vi-III (or III-VII-i-V in minor)

### Classical (1750-1820)
```abc
%%% Standard classical cadential progression
"^I"[CEG]2"^IV"[FAc]2|"^V"[GBd]2"^I"[CEG]2|
"^I"[CEG]2"^ii6"[FAd]2|"^V6/4"[GCE]"^V7"[GBdF]"^I"[CEGc]2|
```
- I-IV-V-I, I-ii6-V-I, I-vi-IV-V-I
- Mannheim rocket: arpeggiated I rising
- Rule of the octave harmonization

### Romantic (1820-1900)
```abc
%%% Chromatic mediant relationship
"^I"[CEG]2"^bVI"[_A,C_E]2|"^I"[CEG]2"^III"[EG#B]2|
```
- Chromatic mediants: I-bVI, I-III, I-bIII
- Omnibus progression (chromatic voice exchange)
- Wagner: Tristan progression (Fr+6 resolving deceptively)
- Augmented 6th approaches to V

### Impressionist (1880-1920)
```abc
%%% Parallel chord motion (planing)
"^Cmaj7"[CEGb]2"^Dbmaj7"[_D_F_Ac]2|"^Ebmaj7"[_EG_Bd]2"^Fmaj7"[FAce]2|
```
- Parallel major 7ths, 9ths (planing)
- Whole-tone harmony: I-II-III+ (all augmented)
- Non-functional progressions, modal color
- Added-note chords (add9, add6)

### Film Score (Modern)
- Power chord parallels (root + 5th)
- Modal interchange (borrowing from parallel minor/major)
- Lydian IV (I-II), Mixolydian bVII-I
- Deceptive resolutions for tension

## Cadence Types

| Cadence | Formula | Strength | Usage |
|---------|---------|----------|-------|
| Perfect Authentic (PAC) | V(7)-I, soprano on 1 | Strongest | Phrase/section endings |
| Imperfect Authentic (IAC) | V-I, soprano not on 1 | Moderate | Interior phrases |
| Half (HC) | X-V | Suspense | Mid-phrase, question |
| Deceptive (DC) | V-vi (or V-bVI) | Surprise | Delayed resolution |
| Plagal (PC) | IV-I | "Amen" | Codas, hymns |
| Evaded | V7-I6 or V7-vi6 | Weak | Continuation |
| Phrygian HC | iv6-V (in minor) | Archaic | Baroque, slow mvts |

### ABC Cadence Examples
```abc
X:1
T:Cadence Types in C major
M:4/4
L:1/2
K:C
%%% PAC
[V:1]"^PAC" Bd|ce||
[V:2] GG|EC||
%%% HC
[V:1]"^HC" EG|AB||
[V:2] CG,|FG,||
%%% DC
[V:1]"^DC" Bd|ce||
[V:2] GG|EA,||
```

```abc
X:2
T:PAC in C major (4 voices)
M:4/4
L:1/2
K:C
V:S clef=treble name="S"
V:A clef=treble name="A"
V:T clef=bass name="T"
V:B clef=bass name="B"
[V:S] B c ||
[V:A] d e ||
[V:T] G, G, ||
[V:B] G,, C, ||
```

## Non-Chord Tones

| Type | Abbr | Approach | Leave | Metric | ABC Example |
|------|------|----------|-------|--------|-------------|
| Passing | PT | step | step (same dir) | weak | `C D E` (D passing) |
| Neighbor | NT | step | step (return) | weak | `C D C` (D neighbor) |
| Suspension | SUS | held | step down | strong | `G2 G F` (G sus -> F) |
| Retardation | RET | held | step up | strong | `B2 B c` (B ret -> c) |
| Appoggiatura | APP | leap | step (opposite) | strong | `C F E` (F app) |
| Anticipation | ANT | step | same | weak last | `E F F` (2nd F ant) |
| Escape tone | ET | step | leap (opposite) | weak | `C D B,` (D escape) |
| Pedal | PED | held | held | any | bass holds while chords move |
| Changing tone | CT | step+step | both neighbor | weak | `C D B C` (D+B cambiata) |

```abc
X:3
T:Non-chord tones over C major
M:4/4
L:1/8
K:C
"^PT"C2 DE FG Ac|"^NT"C2 DC E2 FE|"^SUS"[GB]4 [FA]4|"^APP"C2 FE G2 cB|
```

## Composer Signature Progressions

| Composer | Signature Progression | Context |
|----------|-----------------------|---------|
| J.S. Bach | Circle of 5ths w/ 7ths: I-IV7-vii°7-iii7-vi7-ii7-V7-I | Sequences |
| Mozart | I-ii6-I6/4-V7-I; chromatic ascending bass | Cadential areas |
| Beethoven | I-bVI-bVII-I; subito piano after ff | Dramatic contrasts |
| Schubert | I-bVI; I-iii; modal mixture (major<->minor) | Harmonic color |
| Chopin | ii°7-V7-I with chromatic passing; +6 chords | Nocturnes |
| Wagner | Half-dim 7th -> V+7 (Tristan); deceptive chains | Continuous harmony |
| Debussy | Parallel maj7/9; whole-tone; pentatonic harmony | Color, atmosphere |
| Brahms | iii as substitute for I; hemiola with harmony | Developmental |
| Tchaikovsky | Descending chromatic bass; dim7 sequences | Emotional climax |
| Dvorak | bVI-bVII-I; plagal emphasis; modal inflection | Slavonic color |
| Ravel | Add9/add6 chords; bitonal superimposition | Refined color |
| Mahler | Progressive tonality; I-bII oscillation | Symphonic scale |
| R. Strauss | Rapid key changes; tritone relationships | Tone poems |
| John Williams | I-bVII-bVI-bVII-I; Lydian I-II | Heroic themes |
| Hans Zimmer | i-bVI-bIII-bVII; power ostinato | Epic film cues |
| Howard Shore | Modal progressions; dorian/phrygian color | Dark atmosphere |

## Chord Voicing Density by Register

| Register | Recommended Spacing | Notes |
|----------|-------------------|-------|
| Bass (C2-E3) | Wide (10ths+) | Avoid close voicing below E3 -- muddiness |
| Tenor (C3-C4) | Moderate (3rds-8ves) | Core harmonic support |
| Alto (F3-F4) | Close or moderate | Harmonic fill |
| Soprano (C4-C6) | Close (2nds-6ths) | Melody + color |
| Full orchestra | Open spacing bass, tighten upward | Follow overtone series |
