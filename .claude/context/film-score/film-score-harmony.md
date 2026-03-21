# Film Score Harmony Reference

## Core Principle
Film score harmony serves narrative. Every chord choice supports the emotional arc of the scene. Techniques borrowed from Romantic, Impressionist, Modern, and Minimalist traditions combine freely in service of dramatic storytelling.

## Leitmotif Harmonic Language

| Technique | Description | Example |
|-----------|-------------|---------|
| Theme-specific harmony | Each leitmotif has its own harmonic world | Star Wars: Force theme in minor, heroic theme in major |
| Harmonic transformation | Same motif reharmonized for different emotion | Love theme made tragic with minor reharmonization |
| Tonal association | Specific keys = specific characters/places | Williams: Rebel = Bb major, Empire = C minor |
| Harmonic recall | Chord progression triggers memory of scene | Audience associates progression with earlier event |
| Chromatic alteration | Theme darkened/brightened via chord quality change | Major theme becoming diminished for villain reveal |

```abc
X:1
T:Leitmotif Harmonic Transformation
M:4/4
L:1/4
K:C
"^Heroic (Major)"C E G c | "^I"[CEG] "^IV"[FAc] "^V"[GBd] "^I"[CEG] |
"^Tragic (Minor reharmonization)"C _E G c | "^i"[C_EG] "^iv"[F_Ac] "^V"[GB_e] "^i"[C_EG] |
```

## Modal Mixture

| Mixture Type | Color | Usage |
|-------------|-------|-------|
| Borrowed bVI in major | Warm, bittersweet | Romance, nostalgia |
| Borrowed bVII in major | Heroic, folk-like | Adventure, triumph |
| Borrowed bIII in major | Mysterious, expansive | Wonder, discovery |
| Picardy third (I in minor context) | Hopeful resolution | Ending scenes |
| Minor iv in major | Aching, yearning | Emotional farewell |
| Major IV in minor context | Momentary brightness | Glimmer of hope |

```abc
X:2
T:Modal Mixture for Emotional Color
M:4/4
L:1/2
K:C
"^I"[CEG] "^bVI (Ab)"[_A_CE] | "^bVII (Bb)"[_BDF] "^I"[CEG] |
"^i"[C_EG] "^IV (F major in minor)"[FAc] | "^bVI"[_A_CE] "^V"[GBd] |
```

## Chromatic Mediant for Scene Changes

| Mediant Type | Interval | Effect | Usage |
|-------------|----------|--------|-------|
| Upper major 3rd | C -> E | Bright, magical | Scene transformation |
| Lower major 3rd | C -> Ab | Warm, expansive | Emotional deepening |
| Upper minor 3rd | C -> Eb | Dark, mysterious | Threat emergence |
| Lower minor 3rd | C -> A | Warm, intimate | Flashback, memory |
| Tritone | C -> F# | Maximum contrast | Shock, plot twist |

```abc
X:3
T:Chromatic Mediant Scene Change
M:4/4
L:1/2
K:C
"^Scene A (C major)"[CEG] [CEG] | "^Cut to Scene B (Ab major)"[_AcE] [_AcE] |
"^Back to A"[CEG] [CEG] | "^Twist (E major)"[^GBE] [^GBE] |
```

## Ostinato-Based Tension

| Ostinato Type | Instrument | Tension Level | Usage |
|--------------|-----------|---------------|-------|
| Single-note pulse | Low strings, piano | Low-medium | Suspense building |
| Two-note rocking | Strings | Medium | Anxiety, unease |
| Chromatic ostinato | Cellos, basses | High | Chase, danger |
| Cluster ostinato | Full strings | Very high | Horror, panic |
| Rhythmic ostinato | Percussion + low brass | Medium-high | Action, pursuit |

```abc
X:4
T:Tension Ostinato Patterns
M:4/4
L:1/8
K:Cm
"^Pulse (low tension)"C,C,C,C, C,C,C,C, |
"^Rocking (medium)"C,G,C,G, C,G,C,G, |
"^Chromatic (high)"C,_D,D,_E, E,F,^F,G, |
```

## Pandiatonic Clusters

| Voicing | Sound | Usage |
|---------|-------|-------|
| Wide-spaced diatonic | Open, vast | Landscape establishing shots |
| Close-position diatonic | Shimmering, bright | Magic, wonder |
| Pentatonic cluster | Pure, innocent | Childhood, nostalgia |
| Quartal stack | Modern, ambiguous | Sci-fi, unknown |

```abc
X:5
T:Pandiatonic Cluster - Wonder/Magic
M:4/4
L:1/1
K:C
"^Wide landscape"[C,G,EBgd'] | "^Close shimmer"[CDEGBd] |
"^Pentatonic pure"[CDEGAd] | "^Quartal ambiguous"[CFBe] |
```

## Hybrid Orchestral + Synth Harmony

| Layer | Harmonic Role | Timbral Character |
|-------|--------------|-------------------|
| Orchestral strings | Sustained harmonic foundation | Warm, organic |
| Synth pads | Tonal color, atmosphere | Smooth, electronic |
| Brass hits | Harmonic punctuation | Powerful, precise |
| Synth bass | Sub-bass foundation | Deep, rumbling |
| Orchestral woodwinds | Melodic harmony, countermelody | Human, expressive |
| Synth arpeggios | Harmonic rhythm, momentum | Pulsing, mechanical |

## Resolution Conventions

| Scene Context | Resolution Type | Harmonic Motion |
|--------------|----------------|-----------------|
| Happy ending | Perfect authentic cadence | V7 -> I (major) |
| Bittersweet ending | Plagal cadence | iv -> I |
| Cliffhanger | Deceptive cadence | V -> vi |
| Unresolved tension | Half cadence on V | I -> V (no resolution) |
| Mystery/ambiguity | Cadence on non-tonic | Ends on ii or IV |
| Tragic resolution | Plagal in minor | iv -> i |
| Triumphant | Extended cadence | IV -> V -> V/V -> V -> I |

```abc
X:6
T:Resolution Conventions
M:4/4
L:1/2
K:C
"^Happy"[GBd][CEG] | "^Bittersweet"[F_Ac][CEG] | "^Cliffhanger"[GBd][A_CE] | "^Unresolved"[CEG][GBd] |
```

## Common Film Score Progressions

| Progression | Feel | Usage |
|-------------|------|-------|
| I - bVII - bVI - bVII | Epic, heroic | Main title, action |
| i - bVI - bIII - bVII | Dark epic | Villain theme, battle |
| I - V - vi - IV | Universal emotion | Romance, montage |
| i - bVI - iv - V | Dramatic tension | Emotional climax |
| I - bVI - I - bVI | Oscillating wonder | Discovery, awe |
| i - i - iv - V | Building threat | Approaching danger |
| vi - IV - I - V | Uplifting | Victory, reunion |

```abc
X:7
T:Epic Heroic Progression (I - bVII - bVI - bVII - I)
M:4/4
L:1/2
K:C
"^I"[CEG] "^bVII"[_BDF] | "^bVI"[_A_CE] "^bVII"[_BDF] | "^I"[CEG]2 |
```

## Tension-Release Spectrum

| Tension Level | Harmonic Techniques | Scene Type |
|---------------|---------------------|------------|
| 1 (Peace) | Sustained major triad, open 5ths | Pastoral, home |
| 2 (Warmth) | I - IV - I, simple diatonic | Dialogue, friendship |
| 3 (Unease) | Added 2nds, minor color | First sign of trouble |
| 4 (Suspense) | Chromatic bass, ostinato | Investigation, creeping |
| 5 (Threat) | Tritone, diminished chords | Villain presence |
| 6 (Danger) | Cluster, dissonant pedal | Chase, confrontation |
| 7 (Terror) | Atonal clusters, extreme dissonance | Horror climax |
| 8 (Catharsis) | Resolution to major triad | After the storm |

## Key Modulation Techniques for Film

| Technique | Effect | Typical Usage |
|-----------|--------|---------------|
| Direct modulation | Instant scene change | Hard cut between scenes |
| Pivot chord | Smooth transition | Camera pan, dissolve |
| Common-tone | Seamless key shift | Continuous scene evolution |
| Enharmonic | Surprising connection | Plot twist reveal |
| Step-up modulation | Building excitement | Final chorus, big moment |
| Chromatic mediant | Magical transformation | Reveal, transformation |

## Harmonic Pacing for Scenes

| Scene Pace | Chord Changes | Effect |
|-----------|---------------|--------|
| Slow dialogue | 1 chord per 4-8 bars | Background, unobtrusive |
| Emotional moment | 1 chord per 1-2 bars | Supportive, present |
| Action sequence | 1-2 chords per bar | Driving, energetic |
| Climax | Rapid chromatic | Overwhelming |
| Aftermath | Very slow or static | Stillness, processing |
