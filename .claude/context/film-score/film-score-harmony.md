# Film Score Harmony — Reference Tables

## Leitmotif Harmonic Identity

Each character/concept gets a distinct harmonic "color" that recurs whenever they appear.

| Identity Type | Harmonic Color | Example |
|--------------|----------------|---------|
| Hero | Major triads, open 5ths, bright keys (C, D, Bb) | Superman (Williams) |
| Villain | Minor, diminished, chromatic, tritones | Imperial March (Williams) |
| Love | Major 7ths, added 6ths, suspensions | Across the Stars (Williams) |
| Mystery/Magic | Chromatic mediants, whole tone, modal mixture | Hedwig's Theme (Williams) |
| Nature/Wonder | Open 5ths, Lydian mode, plagal cadences | Jurassic Park (Williams) |
| Danger/Threat | Tritones, minor 2nds, chromatic descent | Jaws (Williams) |
| Nostalgia | IV chord emphasis, plagal motion, added 9ths | Up theme (Giacchino) |
| Power/Fate | Power chords, pedal points, Aeolian mode | Dark Knight (Zimmer) |


## Harmony as Instant Storytelling

Film score harmony exploits the audience's accumulated harmonic memory — decades of film-watching train listeners to associate specific harmonic gestures with emotional states. The composer uses this shared vocabulary to tell stories without words: a minor iv chord in a major love scene foreshadows betrayal before the plot reveals it. Harmony becomes subtext.

### The Temperature Metaphor

Film composers think in terms of harmonic temperature — warm, cold, or neutral — to control the audience's emotional state moment by moment:

| Temperature | Harmonic Characteristics | Emotional Effect |
|------------|------------------------|-----------------|
| Warm | Major triads, added 6ths, plagal motion, Lydian | Safety, love, nostalgia, home |
| Cool | Open 5ths, suspended chords, modal ambiguity | Mystery, wonder, uncertainty |
| Cold | Minor 2nds, tritones, chromatic clusters | Danger, dread, isolation |
| Neutral | Unison, octaves, single sustained tone | Anticipation, blankness, the moment before |
| Shifting (warm→cold) | Major to minor, diatonic to chromatic | Loss, betrayal — the audience feels the ground shifting |
| Shifting (cold→warm) | Chromatic to diatonic, minor to major (Picardy) | Hope, rescue, dawn breaking |

### Harmonic Subtext — Telling a Different Story

The most powerful film scoring occurs when the harmony tells a DIFFERENT story than the visual:

| Visual | Harmonic Subtext | What the Audience Feels |
|--------|-----------------|------------------------|
| Happy reunion | Minor coloring, unresolved sus | Something is wrong — this happiness will not last |
| Villain's calm speech | Gentle major 7ths | The villain is genuinely charming — more terrifying |
| Battle scene | Lyrical, major, hymn-like | These warriors believe they are righteous — tragic nobility |
| Child playing | Chromatic descent, ambiguity | Innocence in danger — dread beneath the surface |
| Triumphant arrival | Deceptive cadence, V → bVI | The triumph is hollow or premature — more trials await |

### The Power of Simplicity After Complexity

After extended chromatic or dissonant passages, a simple major triad creates the effect of clouds parting. Film composers leverage this contrast: the resolution's power is proportional to the complexity that preceded it. Williams's most transcendent moments (E.T. flying, Star Wars throne room) arrive on simple triads, but those triads carry the weight of everything that came before.

```abc
X:50
T:Harmonic Temperature Shift (Warm to Cold)
M:4/4
L:1/2
K:C
%% Warm: bright major with added 6th
[CEGA]2 [FAcD]2 |
%% Cooling: open 5th, ambiguity enters
[C,G,]2 [D,A,]2 |
%% Cold: minor 2nd, tritone
[C,_D,]2 [C,^F,]2 |
% The audience feels temperature dropping — something has changed
```

## Chromatic Mediant Relationships

Major third shifts create wonder, magic, otherworldliness.

| Relationship | Interval | Effect | Example Progression |
|-------------|----------|--------|-------------------|
| Upper chromatic mediant | +M3 | Brightening, wonder | C -> E |
| Lower chromatic mediant | -M3 | Darkening, mystery | C -> Ab |
| Upper diatonic mediant | +m3 | Gentle lift | C -> Eb |
| Lower diatonic mediant | -m3 | Wistful, nostalgic | C -> A |
| Double mediant | +M3 +M3 | Maximum wonder | C -> E -> G# |

### ABC — Chromatic Mediant Shift (Wonder)
```abc
X:1
T:Chromatic mediant - wonder/magic
M:4/4
L:1/2
K:C
Q:1/4=80
V:1
[CEG] [CEG] | [EG#B] [EG#B] | [CEG] [A,CE] | [CEG]4 |
```

### ABC — Double Mediant Sequence
```abc
X:2
T:Double mediant shift - ethereal
M:4/4
L:1/2
K:C
[CEG]2 | [^E^G^B]2 | [^A^c^e]2 | [CEG]2 |
```

## Tritone Substitution for Tension

| Context | Standard | Tritone Sub | Effect |
|---------|----------|-------------|--------|
| Dominant approach | G7 -> C | Db7 -> C | Chromatic bass descent |
| Villain reveal | V -> i | bII7 -> i | Sinister approach |
| Plot twist | Expected V | bII instead | Harmonic surprise |
| Deceptive cadence | V -> vi | bII -> vi | Double misdirection |

### ABC — Tritone Substitution
```abc
X:3
T:Tritone sub - villain approach
M:4/4
L:1/2
K:Cm
[E,G,_B,_D] [E,G,_B,_D] | [C,_E,G,]4 |
%% Db7 (tritone of G7) resolving to Cm
```

## Modal Interchange for Emotional Shifts

| Borrowed Chord | From Mode | Emotional Effect |
|---------------|-----------|-----------------|
| bVI | Aeolian | Melancholy, fate |
| bVII | Mixolydian | Epic, anthemic |
| iv | Aeolian | Sadness in major context |
| bIII | Aeolian | Broadening, expansion |
| #IV | Lydian | Wonder, floating |
| ii dim | Phrygian | Exotic, threatening |

### ABC — Modal Interchange Sequence
```abc
X:4
T:Modal interchange - major to minor borrowings
M:4/4
L:1/2
K:C
%% I - bVI - bVII - I (epic/anthemic)
[CEG]2 | [_A,C_E]2 | [_B,DF]2 | [CEG]2 |
```

## Power Chords and Open Fifths

| Usage | Voicing | Context |
|-------|---------|---------|
| Action hits | Root + 5th, low brass + low strings | Stabs, impacts |
| Ambiguous mood | Root + 5th only (no 3rd) | Uncertain scenes |
| Trailer builds | Stacked 5ths across orchestra | Epic escalation |
| Drone base | Low root + 5th sustained | Underlying tension |

### ABC — Power Chord Action Stabs
```abc
X:5
T:Action stabs - power chords
M:4/4
L:1/8
K:Cm
Q:1/4=140
V:1 name="Brass"
[C,G,]2 z2 [_E,_B,]2 z2 | z2 [F,C]2 [G,D]2 z2 | [C,G,]4 z4 |
```

## Pedal Point for Tension/Suspense

| Pedal Type | Placement | Effect |
|-----------|-----------|--------|
| Tonic pedal | Bass sustains root | Stability, grounding |
| Dominant pedal | Bass sustains 5th | Building expectation |
| Inverted pedal | Soprano sustains note | Suspended, ethereal |
| Double pedal | Bass + soprano both sustain | Maximum tension |
| Pulsing pedal | Repeated rhythmic pedal | Ticking clock, urgency |

### ABC — Suspense Pedal Point
```abc
X:6
T:Suspense - dominant pedal with chromatic upper voices
M:4/4
L:1/4
K:Cm
Q:1/4=72
V:1 name="Upper Strings"
_E F G _A | G F _E D | _D _E F _G | F _E D C |
V:2 name="Bass Pedal"
G,, G,, G,, G,, | G,, G,, G,, G,, | G,, G,, G,, G,, | G,, G,, G,, G,, |
```

## Harmonic Rhythm and Editing Pace

| Scene Pace | Harmonic Rhythm | Chord Changes |
|-----------|-----------------|---------------|
| Slow dialogue | 1 chord per 2-4 bars | Every 4-8 seconds |
| Moderate drama | 1 chord per 1-2 bars | Every 2-4 seconds |
| Action sequence | 1-2 chords per bar | Every 0.5-2 seconds |
| Chase/fight | Rapid, every beat | Continuous motion |
| Stinger/hit | Single chord, immediate | Instant impact |
| Montage | Follows cut rhythm | Matches edit points |

## Common Progressions by Scene Type

### Action/Chase
| Progression | Description |
|-------------|-------------|
| i - bVII - bVI - V | Minor descent with dominant resolution |
| i - iv - bVI - bVII | Epic minor ascent |
| i - i - bII - i | Phrygian tension |
| Chromatic bass descent | i -> vii dim -> bVII -> vi -> bVI -> v -> bV -> iv |

```abc
X:7
T:Action progression
M:4/4
L:1/4
K:Cm
Q:1/4=152
[C,_E,G,] [C,_E,G,] [_B,,D,F,] [_B,,D,F,] | [_A,,C,_E,] [_A,,C,_E,] [G,,_B,,D,] [G,,_B,,D,] |
```

### Romance/Love Theme
| Progression | Description |
|-------------|-------------|
| I - V/vi - vi - IV | Yearning cycle |
| I - iii - IV - iv | Major to minor iv = bittersweet |
| I - bVI - IV - V | Mediant relationship = warmth |
| IVmaj7 - I - V - vi | Plagal emphasis = tenderness |

```abc
X:8
T:Love theme progression
M:3/4
L:1/4
K:C
Q:1/4=72
V:1
[EGc]3 | [EGB]3 | [CEA]3 | [DFA]3 | [CEG]3 |
```

### Mystery/Discovery
| Progression | Description |
|-------------|-------------|
| i - bVI - III - bVII | Minor with mediant lifts |
| Whole-tone chord motion | Harmonies from whole-tone scale |
| i - #IV - bVII - III | Tritone + mediants = otherworldly |
| Unresolved sus chords | Csus4 -> Ebsus2 -> Absus4 |

```abc
X:9
T:Mystery progression
M:4/4
L:1/2
K:Am
Q:1/4=66
[A,CE]2 | [F,_AC]2 | [_E,G_B]2 | [A,CE]2 |
```

### Triumph/Victory
| Progression | Description |
|-------------|-------------|
| IV - V - I | Strong authentic cadence, arrival |
| bVI - bVII - I | Epic double plagal approach |
| iv - V - I | Picardy third effect from minor iv |
| I - V - vi - iii - IV - I - IV - V | Extended major celebration |

```abc
X:10
T:Triumph progression - epic arrival
M:4/4
L:1/2
K:C
Q:1/4=100
[_A,C_E]2 | [_B,DF]2 | [C,E,G,C]4 |
```

### Horror/Dread
| Progression | Description |
|-------------|-------------|
| Semitone oscillation | i -> bII -> i -> bII |
| Tritone shift | i - #iv dim |
| Chromatic planing | Parallel minor chords descending |
| Cluster chords | Semitone stacks |
| Single note + silence | Isolation and void |

```abc
X:11
T:Horror - semitone oscillation
M:4/4
L:1/2
K:Cm
Q:1/4=52
[C,_E,G,]2 | [_D,F,_A,]2 | [C,_E,G,]2 | [_D,F,_A,]2 |
```

## "Temp Track" Classical Borrowings

Common classical harmonies borrowed for film scoring:

| Classical Source | Harmonic Device | Film Usage |
|----------------|-----------------|------------|
| Wagner: Tristan chord | Half-dim 7th, unresolved | Yearning, desire |
| Holst: Mars | 5/4 ostinato, bitonal | War, aggression |
| Barber: Adagio | Slow ascending suspensions | Grief, tragedy |
| Debussy: whole-tone | Whole-tone scales/chords | Dream, underwater |
| Orff: Carmina Burana | bVI-bVII-i power chords | Epic choir moments |
| Stravinsky: Rite | Polyrhythm, bi-chords | Primal, violent |
| Rachmaninoff: Piano Concerto 2 | Rich chromatic mediants | Romance, passion |
| Prokofiev: Battle on Ice | Driving minor ostinati | Battle, pursuit |

### ABC — Wagnerian Yearning (Tristan-derived)
```abc
X:12
T:Tristan-derived yearning
M:4/4
L:1/2
K:Am
Q:1/4=60
[F,A,_D] [F,^G,B,E] | [E,A,C] [E,^G,B,D] | [A,,A,CE]4 |
```

## Quick Harmonic Palette by Mood

| Mood | Key Area | Chords | Special Device |
|------|----------|--------|----------------|
| Joyful | Major, Lydian | I, IV, V, #IVdim | Lydian raised 4th |
| Sad | Minor, Aeolian | i, iv, bVI, v | Plagal minor motion |
| Tense | Chromatic, Locrian | dim, aug, clusters | Semitone motion |
| Epic | Major/minor mix | bVI, bVII, I, V | Modal interchange |
| Mysterious | Whole-tone, Phrygian | aug, sus, bII | Unresolved harmony |
| Romantic | Major with borrowed | I, iii, IV, iv | Minor iv in major |
| Heroic | Bright major | I, IV, V, vi | Wide-spaced triads |
| Evil | Minor, chromatic | i, bII, #iv dim, V | Tritone emphasis |
| Ethereal | Lydian, pentatonic | Imaj7, IImaj7, sus | Parallel major chords |
| Urgent | Driving minor | i, bVII, iv, V | Pulsing bass pedal |

## Modulation Techniques for Scene Transitions

| Technique | Speed | Usage |
|-----------|-------|-------|
| Direct/abrupt | Instant | Hard cut between scenes |
| Pivot chord | 1-2 bars | Smooth scene transition |
| Chromatic mediant | Instant but smooth | Shift in mood, same scene |
| Enharmonic | 1 bar | Surprise recontextualization |
| Pedal tone | 2-4 bars | Gradual scene transition |
| Fade to silence | Variable | Scene to black, then new key |
| Cross-fade | 2-4 bars | Dissolve between scenes |
