# Romantic Harmony Reference

## Era Span
~1820–1900. Beethoven late works through Brahms/Tchaikovsky/Dvorak.

## Core Chromatic Techniques

### Chromatic Mediants
| Relationship | From C major | Quality | Effect |
|---|---|---|---|
| Upper chromatic mediant | C -> E major | M -> M | Bright, magical |
| Lower chromatic mediant | C -> Ab major | M -> M | Dark, warm |
| Upper double chromatic | C -> Eb major | M -> M | Shadowed |
| Lower double chromatic | C -> A major | M -> M | Luminous |
| Upper chromatic mediant (minor) | C -> E minor | M -> m | Wistful |
| Lower chromatic mediant (minor) | C -> Ab minor | M -> m | Ominous |

Common voice-leading: hold common tone, move other voices by semitone.

```abc
X:1
T:Chromatic Mediant C->Ab
M:4/4
L:1/2
K:C
%%MIDI program 0
[CEG] [C_E_A] | [CEG] [^CE^G] |
w: C Ab C E
```

### Augmented 6th Chords
| Type | Formula (on b6) | Intervals | Resolution |
|---|---|---|---|
| Italian 6th (It+6) | b6 - 1 - #4 | M3 + A4 | -> V |
| French 6th (Fr+6) | b6 - 1 - 2 - #4 | M3 + M2 + M3 | -> V |
| German 6th (Ger+6) | b6 - 1 - b3 - #4 | M3 + m3 + A2 | -> V (or Ic -> V) |
| Enharmonic Ger+6 | = dominant 7th of bII | respell #4 as b5 | -> bII (pivot modulation) |

```abc
X:2
T:Augmented 6th Chords in C minor
M:4/4
L:1/2
K:Cm
%%MIDI program 0
[_A,C^F] [G,_BDG] | [_A,CD^F] [G,_BDG] | [_A,C_E^F] [G,_BDG] |
w: It+6 V Fr+6 V Ger+6 V
```

### Neapolitan Chord (bII)
| Usage | Chord | Typical bass | Resolution |
|---|---|---|---|
| Standard | bII6 (1st inversion) | b2 in bass | -> V |
| Root position | bII | b2 in bass | -> V or -> i |
| Arpeggiated | bII6 broken | b2 in bass | -> viio7/V -> V |
| As pivot | bII = V/V in new key | enharmonic | modulation to remote key |

```abc
X:3
T:Neapolitan in C minor
M:4/4
L:1/2
K:Cm
[F_D_B,] [=B,DFG] | [CEGc] z |
w: bII6 V7 i
```

### Extended Dominant Chains
| Pattern | Progression | Usage |
|---|---|---|
| Chain of V7s | V7/vi -> vi -> V7/ii -> ii -> V7/V -> V -> I | Sequential passages |
| Descending 5ths | C7->F7->Bb7->Eb7... | Intensification |
| Applied vii dim7 | viio7/V -> V -> viio7/I -> I | Smooth chromatic motion |
| Interlocking | V7/ii -> V7/V -> V7 -> I | Cadential drive |

```abc
X:4
T:Extended Dominant Chain in C
M:4/4
L:1/4
K:C
[^F_BDA] [G_BEG] | [^FAcD] [GBdD] | [^GBd^F] [Ace] |
w: V7/ii ii V7/V V V7/vi vi
```

### Deceptive Resolutions
| Expected | Actual | Effect | Common in |
|---|---|---|---|
| V -> I | V -> vi | Standard deceptive | All periods |
| V -> I | V -> bVI | Romantic deceptive | Schubert, Brahms |
| V -> I | V -> IV6 | Plagal substitution | Brahms |
| V7 -> I | V7 -> #IVo7 | Chromatic deception | Wagner, Liszt |
| V -> i | V -> III | Modal deceptive | Dvorak, Grieg |
| V -> i | V -> bvi | Dark deception | Tchaikovsky |

```abc
X:5
T:Deceptive Cadences
M:4/4
L:1/2
K:C
[G,BDF] [_ACEA] | [G,BDF] [_A,CE_A] |
w: V7 vi V7 bVI
```

### Enharmonic Modulation Techniques
| Pivot Chord | Reinterpreted As | Key Change |
|---|---|---|
| Ger+6 in C = V7 of Db | Ger+6 -> V vs V7 -> Db | C -> Db |
| viio7 of C = viio7 of Eb = viio7 of F# = viio7 of A | 3 enharmonic respellings | Equidistant keys |
| Fr+6 in C = Fr+6 in F# | Tritone relationship | C -> F# |
| V7 of C = Ger+6 in B | Dom7 = Aug6 | C -> B |

```abc
X:6
T:Enharmonic Modulation via dim7
M:4/4
L:1/4
K:C
[=B,DF_A] [CEGc] | [=B,DF_A] [^C_EG_B] | [=B,DF^G] [^C^EAc] |
w: viio7 C viio7(=) c# viio7(=) A
```

### Omnibus Progression
Chromatic voice exchange: outer voices move in contrary chromatic motion while inner voices sustain or move stepwise.

| Step | Bass | Soprano | Inner voices | Chord |
|---|---|---|---|---|
| 1 | C | E | E G | C major |
| 2 | B | F | E G | G7 (2nd inv) |
| 3 | Bb | F# | E G | dim7 |
| 4 | A | G | E G | Am (or A7) |
| 5 | Ab | G# | E G | Ab+ or Ger+6 |

```abc
X:7
T:Omnibus Progression
M:4/4
L:1/4
K:C
[C,EGe] [B,,EGf] [_B,,EG^f] [A,,EGg] |
w: I V43 viio7 vi
```

### Non-Functional Progressions
| Type | Example | Principle |
|---|---|---|
| Parallel planing | C -> Db -> D -> Eb (all major) | Voice-leading by step |
| Chromatic bass descent | C -> C/B -> Am/C -> C/Bb -> F/A | Lamento bass variant |
| Tritone substitution (proto) | Db7 -> C | bII7 = altered V7 |
| Common-tone augmented | C -> C+( -> Am | Chromatic neighbor |
| Slide progression | Cm -> Db major | Hold 3rd/5th, move root |

```abc
X:8
T:Chromatic Bass Descent
M:4/4
L:1/4
K:C
[CEGc] [=BDGc] [AcEA] [_BcEA] | [AFcF] z2 z |
w: I I/7 vi I/b7 IV
```

## Romantic Cadence Types
| Cadence | Progression | Character |
|---|---|---|
| Plagal with added 6th | IV(add6) -> I | Warm, hymn-like |
| Chromatic plagal | iv -> I | Darker plagal |
| Deceptive to bVI | V -> bVI | Expansive, unexpected |
| Evaded | V -> I6 (not root) | Continuation required |
| Half-cadence on V with app. | ii -> Cad64 -> V | Extended suspense |
| Romantic PAC | Ger+6 -> Cad64 -> V7 -> I | Full Romantic |

## Modulation Distance by Period
| Era | Typical Distance | Example |
|---|---|---|
| Early Romantic | 3rds, relative keys | C -> E, C -> Ab |
| Mid Romantic | Any diatonic + chromatic 3rd | C -> Db, C -> F# |
| Late Romantic | Tritone, semitone, anywhere | C -> F#, C -> Db |

## Sequence Patterns
| Type | Pattern | Motion |
|---|---|---|
| Descending 5ths (diatonic) | I-IV-viio-iii-vi-ii-V-I | Functional |
| Descending 5ths (chromatic) | I-IV-bVII-bIII-bVI-bII-V-I | Expanded |
| Ascending 2nds | V/ii-ii-V/iii-iii-V/IV-IV | Rising tension |
| Descending 3rds | I-vi-IV-ii-viio-V | Warm, nostalgic |
| Chromatic ascending | C-C#o-Dm-D#o-Em | Intensification |

```abc
X:9
T:Chromatic Descending 5ths Sequence
M:4/4
L:1/4
K:C
[CEGc] [CF_Ac] | [_B,DF_B] [_B,_EG_B] | [_A,C_E_A] [_A,_D=F_A] |
w: I IV7 bVII bIII7 bVI bII7
```

## Common Romantic Progressions (Quick Reference)
| Label | Progression | Found in |
|---|---|---|
| Romantic cliche | I -> V6/5 -> I6 -> IV -> iv -> I | Countless works |
| Schubert shift | I -> bVI -> bVII -> I | Schubert, Brahms |
| Chopin chromatic | i -> V7/iv -> iv -> It+6 -> V -> i | Chopin, Liszt |
| Wagner sequence | V9 -> Ger+6 -> Cad64 -> V7 -> deceptive | Wagner, Bruckner |
| Grieg color | I -> I+ -> vi -> iv6 -> I | Grieg, Dvorak |
| Brahms plagal | I -> IV -> iv -> I | Brahms |

## Voice Leading Priorities (Romantic)
1. Chromatic voice leading > functional root motion
2. Common tones sustained across remote chords
3. Bass may move chromatically independent of harmony
4. Inner voices may create chromatic lines (Brahms)
5. Parallel 3rds/6ths between outer voices acceptable
6. Doubling rules relaxed for color (doubled 3rds common)
7. Cross-relations between voices used for color

## Pedal Point Usage
| Type | Description | Effect |
|---|---|---|
| Tonic pedal | Held tonic, harmony moves above | Stability, coda |
| Dominant pedal | Held 5th, builds tension | Pre-recapitulation |
| Inverted pedal | Sustained top voice | Ethereal, floating |
| Double pedal | Tonic + dominant held | Maximum stability |
| Chromatic over pedal | Remote harmonies over pedal | Tension without losing key |
