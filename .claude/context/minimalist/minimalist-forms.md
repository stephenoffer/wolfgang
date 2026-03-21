# Minimalist Forms Reference

## Core Formal Principles

| Principle | Description |
|-----------|-------------|
| Process as form | Structure emerges from audible process |
| Gradual change | Transformation happens slowly enough to hear |
| Repetition as content | Repeated material is the music, not preparation |
| Non-teleological | Music doesn't necessarily "go somewhere" |
| Duration freedom | Pieces can be any length, often long |
| Listener attention | Form engages deep listening, not narrative following |
| Non-developmental | Material repeats/transforms, doesn't develop classically |

## Phase Shifting (Steve Reich)

### Process

| Step | Description |
|------|-------------|
| 1 | Two identical patterns in unison |
| 2 | One pattern gradually accelerates (very slightly) |
| 3 | Patterns drift apart, creating new resultant |
| 4 | Arrive at next rhythmic alignment |
| 5 | Hold new alignment (new "locked" position) |
| 6 | Resume shifting to next alignment |
| 7 | Continue until patterns return to unison |

### Phase Positions

| Offset | Relationship | Texture |
|--------|-------------|---------|
| 0 (unison) | Identical | Monophonic clarity |
| 1 unit | Canon at 1 beat | New combined pattern |
| 2 units | Canon at 2 beats | Different combined pattern |
| n/2 (halfway) | Maximum displacement | Most complex resultant |
| n-1 units | Nearly back to unison | Similar to offset 1, reversed |
| n (full cycle) | Back to unison | Return to start |

```abc
X:1
T:Phase Shifting Process (Piano Phase style)
M:4/4
L:1/16
K:E
%%staves {1 2}
V:1 name="Piano 1 (steady)"
E^FBE ^FBEF ^FBE^F | E^FBE ^FBEF ^FBE^F |
V:2 name="Piano 2 (shifts ahead by 1)"
z E^FB E^FBE ^FBE^F | BE^FB E^FBE ^FBE^F |
```

```abc
X:2
T:Phase Position - Locked at offset 3
M:4/4
L:1/16
K:E
%%staves {1 2}
V:1 name="Piano 1"
E^FBE ^FBEF ^FBE^F |
V:2 name="Piano 2 (offset 3)"
E^FBE ^FE^FB E^FBE |
```

## Additive Process (Philip Glass)

### Technique

| Step | Pattern | Length |
|------|---------|--------|
| 1 | A | 3 notes |
| 2 | A + B | 3 + 2 = 5 notes |
| 3 | A + B + C | 3 + 2 + 3 = 8 notes |
| 4 | A + B + C + D | 3 + 2 + 3 + 2 = 10 notes |
| Peak | Full pattern | Maximum length |
| Reverse (optional) | Remove units | Back to 3 notes |

```abc
X:3
T:Additive Process (Glass-style)
M:4/4
L:1/8
K:Fm
"^3 notes"FAc FAc FAc FAc |
"^5 notes"FAcAF FAcAF FAcAF |
"^8 notes"FAcAFcAF FAcAFcAF |
"^10 notes"FAcAFcAFAc FAcAFcAFAc |
```

### Additive Process Formal Map
```
Section:  |---A---|---A+B---|---A+B+C---|---A+B+C+D---|
Bars:     8       8         8           8
Pattern:  |||     |||||     ||||||||    ||||||||||
Notes:    3       5         8           10
```

## Subtractive Process (Reich: Drumming)

### Technique

| Step | Description |
|------|-------------|
| 1 | Full rhythmic pattern (all beats present) |
| 2 | Replace one beat with rest |
| 3 | Replace another beat with rest |
| Continue | Pattern gradually "erased" |
| End | Only rests remain (or single beat) |

```abc
X:4
T:Subtractive Process
M:4/4
L:1/8
K:C
"^Full pattern"C D E C D E C D |
"^-1 note"C D E z D E C D |
"^-2 notes"C D z z D E C z |
"^-3 notes"C z z z D z C z |
"^-4 notes"C z z z z z C z |
```

## Music as Gradual Process (Reich's Manifesto)

| Principle | Implementation |
|-----------|---------------|
| Process must be audible | Listener can hear what's happening |
| No hidden structure | No secret row, no inaudible organization |
| Once set up, runs by itself | Composer initiates, process continues |
| Details unpredictable | Exact resultant patterns emerge, not planned |
| Attention to listening | Focused, meditative engagement |
| Impersonal | Process, not personal expression |

### Process Types

| Process | Description | Composer |
|---------|-------------|----------|
| Phase shift | Two patterns gradually drift | Reich |
| Additive | Pattern grows by adding notes | Glass |
| Subtractive | Pattern shrinks by removing notes | Reich |
| Augmentation | Notes gradually lengthen | Feldman, Part |
| Diminution | Notes gradually shorten | Various |
| Substitution | Replace notes one by one | Reich (Drumming) |
| Filtering | Gradually remove frequency bands | Lucier |

## Arch Form in Minimalism

| Section | Process | Texture Direction |
|---------|---------|-------------------|
| Opening | Sparse, single pattern | Building |
| Build | Layers added, patterns grow | Increasing |
| Climax/Plateau | Maximum density and complexity | Peak |
| Recede | Layers removed, patterns simplify | Decreasing |
| Closing | Returns to sparse, echoes opening | Minimal |

```
Density:
          ___________
         /           \
        /             \
       /               \
      /                 \
     /                   \
____/                     \____
Start                     End
```

### Arch Form Timing

| Section | % of Total | Character |
|---------|-----------|-----------|
| Opening | 10-15% | Single voice, sparse |
| Build 1 | 15-20% | Adding layers |
| Build 2 | 10-15% | Approaching peak |
| Plateau | 20-30% | Full texture, maximum |
| Recede 1 | 10-15% | Thinning begins |
| Recede 2 | 10-15% | Near-original texture |
| Closing | 5-10% | Echo of opening |

## Slow Evolution Form

| Feature | Description |
|---------|-------------|
| Time scale | 15-60+ minutes |
| Change rate | Near-imperceptible |
| Drone | Sustained or slowly shifting pitch center |
| Surface | May be static or have slow pulse |
| Harmony | One chord area for extended duration |
| Deep listening | Requires meditative audience attention |
| Composers | La Monte Young, Eliane Radigue, Feldman |

### Slow Evolution Timeline
```
Time:    0:00   5:00   10:00  15:00  20:00  25:00  30:00
Pitch:   C      C      C+G    C+G    G      G+D    G+D
Dynamic: ppp    ppp    pp     pp     ppp    pp     ppp
Timbre:  Sine   +harm  +harm  Shift  New    +harm  Fade
```

## Meditation Form

| Structure | Description |
|-----------|-------------|
| Entry | Gradual emergence from silence |
| Stasis | Extended static or near-static material |
| Breathing | Subtle dynamic swells (like breath) |
| Return | Each section returns to near-silence |
| Cycles | Multiple breath-like cycles |
| Exit | Gradual dissolution into silence |

```abc
X:5
T:Meditation Form - Single Cycle
M:4/4
L:1/1
K:D
"^pp emerge"[D,A,] | "^p sustain"[D,A,D] | "^mp breathe"[D,A,DF] |
"^p recede"[D,A,D] | "^pp return"[D,A,] | "^ppp dissolve"D, |
```

## Text-Setting Repetition

| Technique | Description | Composer |
|-----------|-------------|----------|
| Repeated text | Same words set to repeating music | Glass operas |
| Syllabic repetition | Single syllable on repeated note | Glass |
| Speech melody | Natural speech rhythm as musical pattern | Reich |
| Additive text | Words added progressively | Reich (It's Gonna Rain) |
| Text as timbre | Words become pure sound through repetition | Riley, Reich |
| Chant model | Psalm-tone like recitation | Part |

```abc
X:6
T:Text-Setting Repetition (Glass opera style)
M:4/4
L:1/8
K:Am
w:This is the way the world the way the world the way
A2 A2 AA AA | AA AA AA AA | AA AA AA A2 |
```

```abc
X:7
T:Speech Melody Pattern (Reich-style)
M:4/4
L:1/16
K:D
w: Come out to show them come out to show them
D2DE F2FE D2DE F2FE | D2DE F2FE D2DE F2FE |
```

## Form Selection Guide for Minimalism

| Musical Intent | Recommended Form | Duration |
|---------------|-----------------|----------|
| Energetic, rhythmic | Phase shifting or additive | 10-25 min |
| Contemplative | Meditation form | 15-45 min |
| Sacred/spiritual | Arch form with text | 20-40 min |
| Process demonstration | Gradual process (audible) | 10-30 min |
| Immersive drone | Slow evolution | 30-90 min |
| Dramatic arc | Arch form | 15-35 min |
| Experimental | Subtractive or substitution | 10-20 min |
| Opera/theater | Text repetition + additive | Variable |

## Section Transition Methods

| Transition | Description | Effect |
|-----------|-------------|--------|
| Seamless | New pattern enters while old continues | No break perceived |
| Overlap fade | Old fades, new emerges | Smooth handoff |
| Silence gap | Brief silence between sections | Structural breath |
| Pivot note | Shared pitch connects two sections | Common-tone link |
| Drone bridge | Drone continues, patterns change | Continuity |
| Attacca | Immediate move to next section | Momentum |

## Duration Guidelines

| Form Type | Minimum | Typical | Maximum |
|-----------|---------|---------|---------|
| Phase piece | 8 min | 15-25 min | 40 min |
| Additive process | 5 min | 10-20 min | 30 min |
| Arch form | 10 min | 20-35 min | 60 min |
| Meditation | 15 min | 30-45 min | 90+ min |
| Slow evolution | 20 min | 45-60 min | 5+ hours |
| Opera act | 30 min | 60-90 min | 120 min |

## Combining Minimalist Processes

| Combination | Application |
|-------------|-------------|
| Phase + additive | Pattern grows, then phases against itself |
| Arch + additive/subtractive | Additive build, subtractive recede |
| Meditation + text | Text appears during stasis sections |
| Slow evolution + arch | Ultra-slow arch over 30+ minutes |
| Substitution + phase | Pattern changes while phasing |
