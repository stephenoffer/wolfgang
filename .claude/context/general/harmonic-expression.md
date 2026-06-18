# Harmonic Expression — Why Chords Move the Listener

This file distills the artistic insights of major theorist-composers: Rameau, C.P.E. Bach, Schoenberg, Schenker, Piston, Rimsky-Korsakov, Berlioz, Wagner, Debussy, Messiaen, Hindemith. Their ideas are creative tools, not academic formulas. Use them as inspiration for making harmonic choices that serve the emotional intent of the piece.

Cross-reference: `musical-semiotics.md` for interval/chord affect tables. This file covers the *why* and *how* of harmonic decision-making.

---

## 1. Harmony as Narrative — The Deep Structure

**Schenker's insight:** An entire movement can be "about" a single harmonic journey — I→V→I at the deepest level. All surface harmony ornaments this fundamental motion through prolongation. Knowing the one big gesture first gives every surface chord its purpose.

### Prolongation: Holding Emotional Breath

| Concept | What It Means | Compositional Use |
|---------|---------------|-------------------|
| Tonic prolongation | Surface chords move, but the ear holds onto I as the anchor | Opening sections: establish home for 8-16 bars before departing |
| Dominant prolongation | V is sustained or circled around, building expectation | Pre-recapitulation, climactic approaches: stretch V for 4-8 bars |
| Linear progression | Stepwise voice-leading connects two structural chords | Development sections: chromatic lines "walk" between distant harmonies |
| Interruption | The deep I→V→I is broken and restarted | Sonata form: exposition stops at V (interruption); recap completes to I |

**Practical rule:** Before writing a single chord, ask: *What is the ONE big harmonic motion in this section?* Then fill in surface detail that serves it. If you can't name the big motion, the section will feel aimless.

### Long-Range Tonal Narrative

| Tonal Move | Narrative Meaning | When To Use |
|-----------|-------------------|-------------|
| Tonic → dominant (I→V) | Setting out from home, expectation | Expositions, first halves, questions |
| Tonic → relative minor (I→vi) | Turning inward, shadow falls | Introspective episodes, B sections |
| Tonic → chromatic mediant (I→bVI, I→III) | Sudden new world, transformation | Magical moments, dramatic pivots |
| Tonic → tritone (I→bII or #IV) | Maximum distance, crisis point | Development climaxes, dramatic rupture |
| Return to tonic | Homecoming — but transformed by the journey | Recapitulations, final resolutions |
| Progressive tonality (end ≠ start) | The journey changed us; we can't go back | Mahler symphonies, narrative works |

```abc
X:1
T:Deep Structure — surface ornaments one motion
M:4/4
L:1/4
K:C
V:1 clef=treble name="Surface"
V:2 clef=bass name="Deep"
[V:1] [CEG] [DFA] [EGB] [FAc] | [EGB] [DFA] [Bdf] [ceg] |
[V:2] C,2 z2 | z2 G,2 |
% Surface: I-ii-iii-IV-iii-ii-V7-I (8 chords of activity)
% Deep structure: just I ---- prolonged ---- V --- I
% The ear hears the journey but feels the single arc
```

---

## 2. Tension-Resolution as Breathing

**Rameau's foundation:** Chords have natural gravitational tendencies — dominant pulls to tonic like an exhale follows an inhale. **C.P.E. Bach's refinement:** The *speed* and *delay* of that resolution is where expression lives. Hold a dissonance longer and the resolution means more.

### Interval Tension Gradation (after Hindemith)

| Tension Level | Intervals | Sensation | Compositional Role |
|--------------|-----------|-----------|-------------------|
| 1 (rest) | Unison, octave | Perfect agreement, stillness | Arrivals, pedal points, endings |
| 2 (calm) | Perfect 5th | Open, stable, spacious | Foundations, open cadences |
| 3 (gentle motion) | Major 3rd, minor 6th | Warm consonance | Harmonic sweetness, major-mode repose |
| 4 (soft tension) | Minor 3rd, major 6th | Darker consonance, slight pull | Minor-mode warmth, gentle longing |
| 5 (active) | Major 2nd, minor 7th | Movement, needs continuation | Passing motion, suspensions resolving |
| 6 (sharp tension) | Minor 2nd, major 7th | Friction, urgency | Appoggiaturas, leading-tone pull, Romantic yearning |
| 7 (maximum) | Tritone | Instability, demands resolution | Dominant function, dramatic crisis |

### Harmonic Rhythm as Breathing Rate

| Rhythm | Sensation | Use For |
|--------|-----------|---------|
| 1 chord per 2-4 bars | Deep, meditative breathing | Openings, codas, pedal-point passages, establishing home |
| 1 chord per bar | Calm, steady pacing | Stable themes, hymn-like passages |
| 2 chords per bar | Walking pace, purposeful | Standard phrase motion, moderate development |
| 1 chord per beat | Rapid breathing, urgency | Cadential acceleration, approaching climax |
| Faster than beat | Hyperventilation, crisis | Development peaks, cadenza-like passages |
| Sudden freeze (1 chord sustained) | Held breath, anticipation or shock | Before a major structural event, general pauses |

**The art of delayed resolution:** The same V7→I cadence prepared with 1 beat of dominant vs. 4 bars of dominant suspension are emotionally worlds apart. The longer preparation builds desire — the resolution becomes cathartic.

```abc
X:2
T:Short vs. Long Dominant Preparation
M:4/4
L:1/4
K:C
V:1 clef=treble name="Quick"
V:2 clef=treble name="Prolonged"
[V:1] [CEG]2 [GBdF] [CEGc] ||
[V:2] [CEG] z [GBdF]2 | [GBdF]2 [GBdF] !fermata![CEGc] ||
% Quick: functional but unstated
% Prolonged: the V hangs, tension builds, resolution is earned
```

### Cadences as Punctuation

| Cadence | Punctuation | Narrative Function | Emotional Effect |
|---------|-------------|-------------------|-----------------|
| PAC (V→I, strong) | Period. | Sentence ended, thought complete | Satisfaction, closure, arrival |
| IAC (V→I, weak) | Comma, | Thought pauses but continues | Partial rest, more to come |
| HC (→V) | Question mark? | Question asked, answer awaited | Suspense, expectation |
| DC (V→vi) | "But—" | Expected ending denied | Surprise, redirection, emotional twist |
| Evaded (V→I6) | Ellipsis... | Almost there, not quite | Frustration, continuation forced |
| Plagal (IV→I) | Soft period. "Amen." | Gentle affirmation after the real ending | Warmth, benediction, coda |
| Elided | New sentence starts mid-word | No breath between phrases | Breathless urgency, Wagnerian flow |

---

## 3. Chord Color vs. Chord Function — Two Philosophies

**Rameau/Piston:** Every chord has a *job* — tonic rests, pre-dominant prepares, dominant drives. Choosing chords means choosing functions that propel the narrative forward.

**Debussy/Messiaen:** Every chord has a *color* — warm, cold, bright, dark, floating. Choosing chords means choosing sensations. A chord need not "go" anywhere; it can simply *be*.

Most great music uses **both**. The skill is knowing when to think functionally (driving toward a goal) and when to think coloristically (painting an atmosphere).

### Color Families

| Family | Characteristic Sound | Chord Types | Emotional Quality | Best For |
|--------|---------------------|-------------|-------------------|----------|
| Warm | Rich, comforting, golden | Major triads, Imaj7, add6 | Contentment, nostalgia, love | Lyrical themes, resolutions, pastoral |
| Cold | Austere, bleak, icy | Minor + b9, sus2, bare 5ths | Isolation, grief, winter | Desolate passages, alienation |
| Bright | Sparkling, radiant, ascending | Lydian (#4), augmented, major high | Joy, wonder, transcendence | Heroic themes, revelations |
| Dark | Heavy, descending, shadowed | Phrygian (b2), diminished, low minor | Dread, gravity, fate | Villains, doom, tragedy |
| Floating | Weightless, dreamlike, untethered | Whole-tone, quartal, add9 no root | Mystery, enchantment, reverie | Impressionist scenes, magical moments |
| Burning | Intense, restless, chromatic | Aug6 chords, dim7 chains, altered V | Passion, desperation, crisis | Climactic peaks, emotional extremity |

### When to Use Function vs. Color

| Musical Situation | Think Functionally | Think Coloristically |
|-------------------|-------------------|---------------------|
| Driving toward a cadence | Yes — T→PD→D→T creates momentum | No — color logic softens arrival |
| Painting an atmosphere | No — function creates unwanted "direction" | Yes — let chords be sensations |
| Development section | Primarily — modulations need functional logic | Color at local level within functional arc |
| Transition between worlds | Blend — function for direction, color for new flavor | Blend — introduce new colors within functional motion |
| Coda/closing | Function for final cadence | Color for poetic afterglow |
| Impressionist style | Rarely — avoid V→I cadences | Primarily — parallel motion, planing, modal |

### Messiaen's Modes as Color Palettes

| Mode | Structure | Color Metaphor | Effect |
|------|-----------|---------------|--------|
| Mode 1 (whole-tone) | T-T-T-T-T-T | Fog, dissolving edges | Floating, directionless, dreamlike |
| Mode 2 (octatonic) | S-T-S-T-S-T-S-T | Stained glass, kaleidoscopic | Mysterious, symmetrical, Stravinsky/Bartók |
| Mode 3 | T-S-S-T-S-S-T-S-S | Iridescent oil on water | Shimmering, complex, otherworldly |

---

## 4. Voice-Leading as Expression

**Schoenberg's "musical prose":** The best harmony feels like natural speech — not textbook exercises. Each voice should move as if singing its own melody, and the harmony that results feels inevitable.

### Voice-Motion Archetypes

| Voice Motion | Emotional Meaning | Famous Usage | ABC Sketch |
|-------------|-------------------|-------------|-----------|
| Chromatic bass descent | Lament, grief, inevitability | Purcell "Dido's Lament", Baroque passacaglia | `C, B,, _B,, A,, _A,, G,,` |
| Chromatic bass ascent | Striving, growing intensity | Romantic developmental passages | `C, ^C, D, ^D, E,` |
| Soprano ascending by step | Hope, aspiration, reaching | Mozart arias, hymn tunes | `C D E F G` |
| Soprano descending by step | Resignation, settling, closure | Bach chorales, lullabies | `G F E D C` |
| Contrary motion (outer voices) | Opening up, expansion, grandeur | Climactic cadences, orchestral swells | Bass down + soprano up |
| Converging voices | Tightening, closing in, tension | Pre-cadential compression | Outer voices approach by step |
| Pedal with moving voices | Grounded tension or stability | Dominant pedals, tonic codas | Bass holds while upper voices roam |
| All voices in same direction | Power, inevitability, or planing | Debussy parallels, brass fanfares | Parallel triads ascending |

### When "Rule-Breaking" Becomes Expression

| "Violation" | The Expressive Purpose | Who Does It |
|------------|----------------------|-------------|
| Parallel 5ths | Raw power, archaic strength, or coloristic planing | Debussy, film scores, Mussorgsky |
| Unresolved 7th | Sustained longing, continuous yearning | Wagner, Mahler, Romantic opera |
| Doubled leading tone | Defiance, emphasis, breaking expectation | Late Beethoven, Bartók |
| Voice crossing | Textural complexity, weaving independence | Bach fugues, Brahms inner voices |
| Unprepared dissonance | Shock, sudden emotion, modern expression | Schoenberg, Stravinsky |

---

## 5. Creating Memorable Harmonic Moments

Not every chord needs to be clever. A piece with 2-3 *unforgettable* harmonic moments and simple connecting material is more powerful than one where every chord is interesting but nothing stands out.

### Six Techniques for Memorable Harmony

| Technique | How It Works | Why It's Memorable |
|-----------|-------------|-------------------|
| **The unexpected mediant** | After establishing tonal expectation, shift by a 3rd instead of a 5th (I→bVI, I→III) | The listener expects V; the mediant is close enough to accept but far enough to astonish |
| **The deceptive twist** | V resolves to vi (or bVI, IV6) instead of I at a key structural moment | Expectation is built then redirected — the surprise deepens the eventual resolution |
| **Harmonic recall** | Bring back a specific voicing or chord color from earlier at a key moment | Creates "rhyme" — the listener recognizes the return and feels the narrative arc close |
| **Silence before the chord** | General pause (GP) before a structurally important harmony | Silence creates anticipation; the chord lands with enormous weight |
| **The register shift** | Repeat a familiar chord in a completely different register | Same harmony, new character — like seeing a familiar face in unexpected light |
| **The pedal release** | Sustain a pedal point through dissonant harmony, then finally move the bass | The release of the held note creates visceral physical relief |

```abc
X:3
T:The Unexpected Mediant — C major to Ab major
M:4/4
L:1/2
K:C
V:1 clef=treble
V:2 clef=bass
[V:1] [CEG] [CEG] | [C_E_A] [C_E_A] |
[V:2] C,2 | _A,,2 |
% Bar 1: comfortable, established tonic
% Bar 2: bVI arrives — same C in soprano (common tone) but the world shifts
% The listener feels the floor tilt — wonder, not wrongness
```

```abc
X:4
T:Silence Before the Chord
M:4/4
L:1/4
K:Cm
V:1 clef=treble
V:2 clef=bass
[V:1] !ff![G=BdF]2 z2 | z4 | !fff![C_EGc]4 |
[V:2] G,,2 z2 | z4 | C,,4 |
% Dominant seventh — silence (full bar GP) — then tonic crashes in
% The silence IS the drama. The listener holds their breath.
```

```abc
X:5
T:Pedal Release
M:4/4
L:1/4
K:C
V:1 clef=treble
V:2 clef=bass
[V:1] [EG]2 [FA]2 | [^FA]2 [GB]2 | [Gc]4 |
[V:2] G,,4 | G,,4 | C,,4 |
% Dominant pedal holds for 2 bars while upper voices move chromatically
% When the bass finally moves G→C, the physical relief is palpable
```

---

## 6. Harmonic Rhythm as Drama

Harmonic rhythm — the rate of chord change — is a dramatic tool as powerful as melody or dynamics. Controlling it shapes the listener's sense of time.

### Four Dramatic Shapes

| Shape | Pattern | Emotional Arc | Use For |
|-------|---------|---------------|---------|
| Steady | Same rate throughout (1/bar) | Calm, processional, inevitable | Marches, chorales, minimalist |
| Accelerating | Slow → fast (1/2bars → 1/bar → 2/bar → 1/beat) | Building tension, approaching climax | Pre-cadential drive, development peaks |
| Decelerating | Fast → slow (2/bar → 1/bar → 1/2bars) | Settling, arriving, breathing out | Post-climax resolution, codas |
| Arch | Slow → fast → slow | Complete dramatic arc within a passage | Self-contained phrases, single-section pieces |

### The Harmonic Freeze

Stopping all harmonic motion (repeating one chord for 4-8+ bars) creates either:
- **Anticipation** — if tension preceded it (dominant freeze before resolution)
- **Trance** — if consonance surrounds it (tonic freeze in minimalist style)
- **Dread** — if dissonance is sustained (diminished 7th freeze)

The freeze is powerful because it violates the listener's expectation of change. Use sparingly.

---

## 7. Register & Voicing as Color

**Rimsky-Korsakov's principle:** Harmony and timbre are inseparable. The same chord voiced for different instruments in different registers is a different emotional entity.

### The Overtone Principle

| Register | Ideal Spacing | Violating It Creates |
|----------|--------------|---------------------|
| Low (C2–E3) | Wide: 10ths, octaves, open 5ths | Muddiness if close-voiced (except for deliberate dark effect) |
| Mid (F3–B4) | Moderate: 3rds to octaves | This is where most "harmonic meaning" lives — the vocal range |
| High (C5+) | Close: 2nds, 3rds, 4ths | Thinness if too spread; but close voicing here shimmers |

### How Orchestration Changes Harmonic Meaning

| Voicing Assignment | What It Does to the Harmony |
|-------------------|---------------------------|
| Brass chorale (close, mid-register) | Sacred, monumental, ceremonial — Bruckner |
| String divisi (close, many parts) | Intimate, complex, shimmering — Mahler Adagietto |
| Solo woodwind over string pedal | Vulnerable, personal, exposed — Mozart slow movements |
| Full tutti with octave doublings | Overwhelming, climactic, irresistible — Beethoven codas |
| Piano wide-spread voicing | Personal, immediate, Romantic — Rachmaninoff |
| Harp arpeggiated chords | Magical, cascading, ethereal — Debussy, Ravel |

For the shorthand voicing grammar used when composing these chords, see `.claude/skills/w-compose/references/note-writing-craft.md`.

---

## 8. Treatise Quick-Reference

| Thinker | Core Insight | When to Apply |
|---------|-------------|---------------|
| **Rameau** (1722) | Chords have natural gravitational functions; the fundamental bass creates logical motion by 5ths and 3rds | Building any functional progression; understanding why V→I feels like arrival |
| **C.P.E. Bach** (1753) | Expression lives in *nuance*: hold a dissonance longer, resolve more softly, surprise with dynamics at harmonic junctions | Slow, expressive passages; Empfindsamkeit and galant styles |
| **Schoenberg** (1911) | "Dissonance is merely a more remote consonance." Every sound can serve expression; chromaticism expands the palette, it doesn't break it | Late-Romantic, chromatic, and transitional passages; permission to be bold |
| **Schenker** (1935) | Surface complexity serves deep simplicity; know the fundamental harmonic motion (Ursatz) before composing the details | Planning large-scale harmonic arcs for movements; ensuring coherence |
| **Piston** (1941) | Clear functional analysis makes progressions logical. The stronger the function, the stronger the emotional drive | Classical-era and any "clear" tonal writing; pedagogical clarity |
| **Rimsky-Korsakov** (1891) | Harmony and timbre are inseparable; how you voice and orchestrate a chord IS its meaning | All orchestral scoring; choosing between registers and instruments |
| **Berlioz** (1844) | Novel combinations of harmony + orchestration create theatrical effects no single dimension can achieve | Dramatic orchestral moments; surprising the listener with color |
| **Wagner** | Perpetually deferred resolution creates continuous yearning; each leitmotif carries its own harmonic world | Late-Romantic continuous textures; leitmotif development; opera |
| **Debussy** | "Chords are free." Resolution is optional; the pleasure of the ear is the only rule. Chords are sensations, not steps | Impressionist and atmospheric passages; color-driven harmony |
| **Messiaen** (1944) | Modes of limited transposition create specific "stained glass" harmonic colors unavailable in diatonic or chromatic systems | Modal color, religious ecstasy, exotic timbres, non-Western influence |
| **Hindemith** (1937) | Every interval has quantifiable tension; compositional drama = managing the arc of tension across time | Modern/neo-classical tension management; quartal/quintal harmony |

---

## 9. Applying These Ideas When Composing Harmony

When planning a phrase's harmony, consider these at each stage:

| Planning Stage | Ask Yourself | Source |
|---------------|-------------|--------|
| Before any chords | What is the ONE big harmonic motion? | Schenker |
| Setting harmonic vocabulary | Am I thinking functionally, coloristically, or both? | Rameau vs. Debussy |
| Choosing specific chords | Does this chord serve the emotion, or just the theory? | C.P.E. Bach |
| Planning modulations | What *narrative* purpose does this key change serve? | Wagner, Mahler |
| Setting harmonic rhythm | Where should the listener breathe? Where should they gasp? | Rameau, Hindemith |
| Annotating voicing | How should this chord *sound* — register, spacing, color? | Rimsky-Korsakov |
| Identifying key moments | Which 2-3 chords should the listener *remember*? | Memorable moments techniques |
| Final review | Does the plan tell a harmonic story, or just list correct chords? | Schenker + intuition |

---

## Cross-References

- `musical-semiotics.md` — Emotional meaning of specific intervals and chord types
- `dramatic-pacing-silence.md` — How silence interacts with harmonic tension
- `philosophy-to-music.md` — Abstract concept-to-harmony mapping
- Genre-specific harmony files in `.claude/context/<genre>/` — Period-appropriate techniques
