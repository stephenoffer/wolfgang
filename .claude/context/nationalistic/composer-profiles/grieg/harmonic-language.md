# Edvard Grieg — Harmonic Language

Grieg's harmony is fresh. Not complex, not systematic, not revolutionary — fresh. His chords surprise without disorienting, color without obscuring, and create an atmosphere that is unmistakably Nordic. The secret is juxtaposition: where other composers modulate, Grieg simply places two distant harmonies next to each other and lets the listener's ear bridge the gap. This is not primitive — it is a specific technique that anticipates Debussy.

For shared Nationalistic harmonic vocabulary (folk modes, modal cadences, drone techniques), see [nationalistic-harmony.md](../../nationalistic-harmony.md). This file covers what is distinctly Griegian.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Chromatic mediant juxtaposition | Keys a major 3rd apart placed side by side: A minor - F# major, E major - C major | Everywhere — the defining Grieg harmonic device |
| Pedal point under shifting harmony | Tonic or dominant held in bass while upper voices change freely | Lyric Pieces, slow movements, atmospheric passages |
| Lydian 4th inflection (raised 4th) | D# in A minor as chromatic passing tone or chord color | The "Grieg note" — from Hardanger fiddle tuning |
| Open-5th voicing | Root + 5th without 3rd in the bass | Norwegian folk texture; landscape openness |
| Augmented triad as color | Not functional — a passing sonority for shimmer | Atmospheric moments, transitional passages |
| Modal ambiguity | Major and minor simultaneously suggested | The Norwegian folk quality — neither purely major nor minor |
| Simple surface, surprising depth | Individual chords are simple triads; the relationships between them are unexpected | The paradox of Grieg's harmonic language |

## Chromatic Mediant Juxtaposition — Grieg's Signature

Grieg does not modulate to distant keys — he teleports. No pivot chord, no dominant preparation, no sequential approach. The new key simply arrives, as if a different light fell through a cloud.

| Juxtaposition | Common Tones | Effect | Context |
|---------------|-------------|--------|---------|
| A minor - F# major | None | Maximum surprise; different world | Lyric Pieces, Piano Concerto |
| A minor - C major | C, E (two common) | Relative; gentle shift | Standard relative major |
| A minor - F major | A, C (two common) | Submediant; warm darkening | Peer Gynt, Holberg Suite |
| E major - C major | E (one common) | Bright to warm; the light changes | Late works |
| A minor - Db major | None | Tritone relation; most distant | Rare; reserved for strongest effect |

```abc
X:1
T:Grieg Chromatic Mediant — A minor to F# major (no preparation)
M:4/4
L:1/4
K:Am
%% A minor: complete, at rest
[A,CE]2 [A,CE]2|
%% F# major: arrives without warning — a different light
K:F#
[F,A,^C]2 [F,A,^C]2|
%% Back to A minor: equally sudden
K:Am
[A,CE]2 [A,CE]2|
%% No modulation. No pivot. Juxtaposition IS the technique.
```

## Pedal Point Technique

The bass holds (tonic or dominant) while the harmonies above it shift freely — often to chromatic or distantly-related chords. The pedal is the earth; the harmonies are the weather.

| Pedal Type | Bass Note | Upper Harmonies | Effect |
|-----------|-----------|-----------------|--------|
| Tonic pedal | A2 (in A minor) | Am, F major, F# major, G major, Dm | Rootedness with atmospheric color change |
| Dominant pedal | E2 (in A minor) | E major, Am, C major, F major | Suspended expectation; the view from the mountain |
| Double pedal (open 5th) | A2 + E3 | Any upper harmony | Hardanger fiddle drone — the most Norwegian texture |

```abc
X:2
T:Grieg Pedal Point — Shifting Light Over Still Ground
M:3/4
L:1/4
K:Am
V:1 name="Upper harmonies"
V:2 name="Pedal (open 5th)" clef=bass
[V:1] [CE]2 [CE]|[^CF]2 [^CF]|[CF]2 [CF]|[CE]2 [CE]|
[V:2] [A,E]3|[A,E]3|[A,E]3|[A,E]3|
w: Am F#dim Fm Am
%% Bass never moves; harmonies shift like clouds over a fjord
```

## The Lydian 4th (Raised 4th)

| Usage | Description | Duration |
|-------|-------------|----------|
| Melodic passing tone | D# between D and E in stepwise motion | Eighth or sixteenth — brief, ornamental |
| Chord color | D# added to A minor chord (A-C-D#-E) | Half note or longer — structural |
| Hardanger imitation | D# as part of open-5th drone texture | Sustained — folk instrument simulation |

```abc
X:3
T:Grieg Lydian 4th — Three Uses
M:4/4
L:1/8
K:Am
%% 1. Melodic passing tone (brief)
A2 B2 c2 ^d2|e4 c4|
%% 2. As chord color (structural)
[A,C^DE]8|
%% 3. In drone context
[A,E]4 [A,^D]4|
%% The same note — three different functions — all Norwegian
```

## Modal Scales in Grieg

| Scale | Notes (in A) | Character | Where Used |
|-------|-------------|-----------|-----------|
| Natural minor (Aeolian) | A-B-C-D-E-F-G | Base scale for most Grieg works | Default — the Norwegian minor |
| Dorian minor | A-B-C-D-E-F#-G | Warmer, less dark; the raised 6th brightens | Folk-song settings, Halling themes |
| Lydian inflection | A-B-C-D#-E-F-G | The Grieg characteristic — raised 4th | Throughout — ornamental or structural |
| Pentatonic minor | A-C-D-E-G | Folk melody without semitones | Simple folk themes, opening melodies |
| Chromatic (no system) | Free chromatic passing tones within diatonic framework | Color, not structure | Inner voices, transitional passages |

## Harmonic Rhythm

| Context | Rate | Reasoning |
|---------|------|-----------|
| Atmospheric opening | Very slow (1 chord per 2 bars) | Establishing mood; the landscape before the story |
| Lyric melody | 1 chord/bar | Supporting the melody without cluttering |
| Halling dance | 1 chord/half-bar | Fast dance = faster harmonic pulse |
| Climax approach | Accelerating | Building tension through chromatic motion |
| Pedal passage | Frozen (bass) / shifting (upper) | Dual rhythm: stability below, motion above |

## Key Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Most characteristic | A minor, E minor, G minor | The "Grieg keys" — minor, dark, Norwegian |
| Bright contrast | A major, E major, G major | Parallel major for middle sections, major episodes |
| Distant color | F# major, Db major, C major | Chromatic mediant targets — surprise keys |
| Piano Concerto | A minor (with E major, A major episodes) | The key Grieg returns to throughout his career |

## Cadential Patterns

| Cadence | Progression | Grieg Context |
|---------|------------|----------------|
| Aeolian cadence | bVII - i | Norwegian folk; dark, modal |
| Lydian cadence | II - I (major II chord) | Bright, Nordic; the raised 4th in harmonic form |
| Plagal | IV - i | Hymn-like; church quality |
| Standard PAC | V - i | Used freely — Grieg is not dogmatically modal |
| Chromatic mediant | bVI - i or III - i | Grieg's atmospheric half-cadences |
| Interrupted | V - bVI | The harmonic surprise at a structural moment |

```abc
X:4
T:Grieg Cadence Types in A minor
M:4/4
L:1/2
K:Am
%% Aeolian: bVII - i
[GBd] [ACE]|
%% Lydian: II(maj) - I (in A major)
K:A
[Bdf] [Ace]|
%% Chromatic mediant: F major - Am
K:Am
[FAc] [ACE]|
%% Three Norwegian cadences — none of them V-i
```

## Characteristic Progressions

### Atmospheric (Lyric Pieces)
```
i - bVII - bVI - bVII - i (aeolian descent and return)
i - III - bVI - i (mediant excursion)
i pedal: i - IV - bII - V - i (all over tonic pedal)
```

### Dance (Halling/Springar)
```
i - V - i - V (simple folk alternation)
i - bVII - i - V - i (folk modal + functional)
I - IV - I - V - I (major dance)
```

### Grieg's Harmonic Freshness
```
Am - F#maj - Am (chromatic mediant)
Am - Fmaj - Dbmaj - Am (descending major 3rds)
Am - Cmaj - Emaj - Am (ascending minor 3rds)
```

## Voice Leading

| Principle | Application |
|-----------|-------------|
| Parallel motion | Parallel 5ths and octaves acceptable for folk color; parallel triads for atmospheric effect |
| Drone independence | The open-5th pedal does not participate in voice-leading — it is the earth |
| Chromatic inner voice | Brief chromatic passing tones in inner voices create harmonic shimmer |
| Minimal voice movement at key changes | Chromatic mediant shifts: voices move by semitone or stay common |
| No Alberti bass | Grieg NEVER uses Alberti bass — open 5ths, waltz bass, arpeggiated chords instead |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #1 (raised 4th), #3 (pedal point), #5 (tonal juxtaposition)
- [melodic-style.md](melodic-style.md) — Melodic use of modal scales
- [orchestration.md](orchestration.md) — Harmonic voicing in orchestral texture
- [../../nationalistic-harmony.md](../../nationalistic-harmony.md) — Shared nationalistic harmonic vocabulary
- [cross-references.md](cross-references.md) — Impact on Debussy; contrast with German chromaticism
