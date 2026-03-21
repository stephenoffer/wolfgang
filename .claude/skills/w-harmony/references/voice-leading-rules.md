# Voice Leading Rules Reference

## Strict Rules (Always Apply Unless Noted)

### Parallel Motion Prohibitions

| Error | Description | Detection |
|-------|-------------|-----------|
| Parallel 5ths | Two voices move by same interval maintaining P5 | Check all voice pairs at each chord change |
| Parallel 8ves | Two voices move by same interval maintaining P8/unison | Check all voice pairs at each chord change |
| Direct (hidden) 5ths | Outer voices move in same direction to P5 | Check S+B; inner voices less strict |
| Direct (hidden) 8ves | Outer voices move in same direction to P8 | Check S+B; soprano must step |

```abc
X:1
T:Parallel 5ths ERROR
M:4/4
L:1/2
V:1
V:2
[V:1] C D |
[V:2] F, G, |
```
C-F is P5, D-G is P5 = parallel 5ths. Fix: move one voice by step in contrary motion.

```abc
X:2
T:Corrected -- contrary motion
M:4/4
L:1/2
V:1
V:2
[V:1] C B, |
[V:2] F, G, |
```

### Resolution Rules

| Rule | Pattern | Resolution | Example |
|------|---------|------------|---------|
| Leading tone resolves up | 7 in V chord | Up by step to 1 | B->C in C major |
| Chordal 7th resolves down | 7th of V7 | Down by step | F->E in V7->I |
| Augmented intervals resolve outward | +6 | Both voices outward | Ab down G, F# up G |
| Diminished intervals resolve inward | dim5 in vii° | Both voices inward | B up C, F down E |
| Suspension resolves down | 4-3, 7-6, 9-8 | Step down (except retardation) | G->F in 4-3 sus |
| Tritone resolves | In V7: 3+7 | Inward or outward | B->C, F->E (inward) |

Exception: Leading tone in inner voice (alto/tenor) may move down to 5th of I for complete chord.

### Voice Range and Spacing

| Voice | Range | Practical Range |
|-------|-------|----------------|
| Soprano | C4-A5 | D4-G5 |
| Alto | F3-D5 | G3-C5 |
| Tenor | C3-A4 | D3-G4 |
| Bass | E2-D4 | F2-C4 |

| Spacing Rule | Guideline |
|-------------|-----------|
| Soprano-Alto | Not more than 1 octave apart |
| Alto-Tenor | Not more than 1 octave apart |
| Tenor-Bass | Can exceed 1 octave (up to 12th acceptable) |
| Voice crossing | Avoid: no voice should go above the voice above it or below the voice below it |
| Voice overlap | Avoid: no voice should move past the previous position of an adjacent voice |

```abc
X:3
T:Correct SATB spacing
M:4/4
L:1
V:S clef=treble name="S"
V:A clef=treble name="A"
V:T clef=bass name="T"
V:B clef=bass name="B"
[V:S] c |
[V:A] G |
[V:T] C |
[V:B] E, |
```

### Doubling Rules

| Chord Type | Double | Avoid Doubling |
|-----------|--------|----------------|
| Root-position major | Root (preferred) | 3rd (leading tone never) |
| Root-position minor | Root or 3rd | -- |
| First inversion | Soprano note or bass | Leading tone, altered tones |
| Second inversion | Bass note (5th) | -- |
| Diminished triad | 3rd (preferred) | Root (tendency tone) |
| Augmented triad | None standard | Context-dependent |
| 7th chords | Root; omit 5th if needed | 7th (only one resolution path) |

Never double: leading tone, chromatically altered notes, chordal 7ths, tendency tones.

## Common Voice-Leading Patterns

### Figured Bass Patterns

| Pattern | Bass Motion | Upper Voice Motion | Usage |
|---------|-----------|-------------------|-------|
| 5-6 | Held/step | 5th moves up to 6th | Ascending parallel 6ths |
| 6-6 | Stepwise (parallel 6ths) | 3rds + 6ths above bass | Fauxbourdon |
| 7-6 | Held/step | 7th resolves to 6th | Suspension chain |
| 2-3 | Held | 2nd resolves to 3rd | Bass suspension |
| 4-3 | Held | 4th resolves to 3rd | Suspension over V |
| 9-8 | Held | 9th resolves to 8ve | Top voice suspension |
| 5-6-5-6 | Ascending steps | Alternating | Extended ascending sequence |

```abc
X:4
T:7-6 suspension chain
M:4/4
L:1/4
V:1
V:2
[V:1] B A G F |
[V:2] C C B, B, |
```

### Standard Cadential Patterns

```abc
X:5
T:Cadential 6/4 voice leading
M:4/4
L:1/4
V:S clef=treble name="S"
V:A clef=treble name="A"
V:T clef=bass name="T"
V:B clef=bass name="B"
[V:S] e2 d c |
[V:A] c2 B G |
[V:T] G2 G G |
[V:B] C,2 G,, C, |
```
I6/4 -> V7 -> I. The 6/4 is a double suspension over V.

## Inner Voice Motion Principles

1. **Prefer common tones**: Hold notes shared between consecutive chords
2. **Stepwise motion**: Move remaining voices by step (2nd) when possible
3. **Contrary motion to bass**: Preferred for outer voices; reduces parallels
4. **Minimal motion**: Inner voices should move as little as possible
5. **Avoid leaps > 4th**: In inner voices; if leap, resolve by step in opposite direction
6. **Augmented 2nd prohibition**: Avoid melodic +2 (e.g., Ab to B in minor) in any voice

| Leap Handling | Rule |
|--------------|------|
| Leap of 3rd | May continue or reverse |
| Leap of 4th | Preferably reverse by step |
| Leap of 5th+ | Must reverse by step |
| Successive leaps | Same direction only if outlining chord; otherwise reverse |
| Leap to/from dissonance | Forbidden (approach/leave NCTs by step) |

## Bass Line Construction

| Principle | Guideline |
|-----------|-----------|
| Stepwise motion | Preferred; creates smooth support |
| Root motion by 5th | Strong harmonic progression |
| Root motion by 3rd | Weaker but colorful |
| Root motion by 2nd | Weak; needs good upper voices |
| Leaps of octave | Acceptable for register shift |
| Repeated notes | OK at cadences, less good mid-phrase |
| Avoid stagnation | Bass should have melodic interest |
| Cadential bass | Scale degrees 5-1 or 4-5-1 at cadences |

```abc
X:6
T:Good bass line -- stepwise with occasional leaps
M:4/4
L:1/4
K:C
C, D, E, F,|G, A, B, C|G, F, E, D,|C,4|
```

## Part-Writing by Texture

### SATB Chorale
- All rules above apply strictly
- Each voice should be independently singable
- Aim for contrary motion between outer voices
- Complete chords (root, 3rd, 5th); omit 5th in 7th chords

### Keyboard (Piano)
- RH typically carries melody + inner voices
- LH provides bass + harmonic support
- Voice-leading rules relaxed for idiomatic figuration
- Parallel 3rds/6ths in one hand acceptable
- Wide LH spacing OK in low register

### Orchestral
- Double at octave for power (does not create parallels)
- Horns/winds follow strict voice leading
- Strings can use parallel passages idiomatically
- Spacing follows overtone series: wide low, close high
- Divisi sections treated as independent voices

### String Quartet
- Near-SATB rules apply
- Crossing acceptable for color
- All four instruments must be independently interesting
- Double stops expand texture temporarily

## When Rules Can Be Broken

| Style/Context | Relaxed Rule | Reason |
|--------------|-------------|--------|
| Impressionist (Debussy) | Parallel 5ths/8ves | Planing is a stylistic feature |
| Film scoring | Parallel power chords | Genre convention |
| Brass fanfare | Parallel motion | Tradition, reinforcement |
| Orchestral doubling | Octave parallels | Timbral blend, not part-writing |
| Modal writing | Leading tone resolution | No leading tone in modes |
| Homorhythmic texture | Close spacing rules | Chordal blocks are expected |
| Extreme register | Spacing rules | Physical necessity |
| Pedal point | Dissonance rules | Pedal is understood; other voices resolve |
| Post-1900 | Most rules | But justify with stylistic consistency |

## Error Detection for AI-Generated Music

### Common AI Voice-Leading Errors

| Error | Detection Method | Fix |
|-------|-----------------|-----|
| Parallel 5ths/8ves | Check interval between all voice pairs across barline | Move one voice by step in contrary motion |
| Unresolved leading tone | Check 7th scale degree in V chord -> next chord | Resolve up to tonic |
| Unresolved 7th | Check chordal 7th -> next chord | Resolve down by step |
| Voice crossing | Compare adjacent voice pitches | Swap notes or respace |
| Spacing > octave (S-A, A-T) | Measure intervals | Respace inner voices |
| Doubled leading tone | Check for 2 instances of scale degree 7 | Redistribute |
| Melodic augmented 2nd | Check for +2 in any voice (especially in minor) | Use natural minor ascending or respace |
| Missing 3rd in chord | Check all tones present | Redistribute doublings |
| Exposed 5th/8ve | Check outer voices approach P5/P8 | Soprano approaches by step |
| Leap unresolved | Check leaps >4th are followed by step in opposite direction | Add step-back |
| Static inner voices | Check for voices holding same note 3+ chords | Add passing/neighbor motion |
| Range violations | Check voice stays within range limits | Transpose, respace |

### Checking Process

1. Extract each voice as a separate line
2. Compute intervals between all voice pairs at each beat
3. Flag consecutive P5->P5 or P8->P8 (parallel)
4. Flag same-direction approach to P5/P8 in outer voices (direct)
5. Check resolution of each tendency tone
6. Verify spacing at each chord
7. Check for voice crossing/overlap
8. Verify doubling at each chord
9. Check melodic intervals for augmented/dissonant leaps

## Quick Reference: SATB Checklist

- [ ] No parallel 5ths or 8ves between any pair
- [ ] No direct 5ths/8ves in outer voices (unless soprano steps)
- [ ] Leading tones resolve up (exception: inner voice to 5th)
- [ ] Chordal 7ths resolve down by step
- [ ] S-A within octave, A-T within octave
- [ ] No voice crossing or overlap
- [ ] Root doubled in root-position triads
- [ ] 5th doubled in 6/4 chords
- [ ] No doubled leading tones or altered tones
- [ ] Leaps > 4th resolved by step in opposite direction
- [ ] No augmented melodic intervals
- [ ] Each chord has at least root and 3rd present
- [ ] Bass line has melodic shape
- [ ] Outer voices predominantly in contrary motion
