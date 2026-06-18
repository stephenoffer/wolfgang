# Gabriel Faure — Harmonic Language

Faure's harmony is the most continuously surprising in French music. The surface is tonal — there is always a key, always a direction — but the path is never straight. Modulations arrive through enharmonic sleight-of-hand, modal inflections tilt the key just enough to feel foreign, and cadences are systematically avoided or elided. The effect: music that flows like a river, always moving, never arriving.

For shared Impressionist harmonic vocabulary (planing, extended chords, whole-tone), see [impressionist-harmony.md](../../impressionist-harmony.md). This file covers what is distinctly Faurean.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Continuous modulation | Key changes every 2-4 bars through smooth enharmonic pivots | All mature works; most extreme in late period |
| Modal inflection within tonality | Dorian, Mixolydian, Lydian notes color an otherwise tonal phrase | Everywhere — the defining Faure sound |
| Plagal cadences | IV-I preferred over V-I; subdominant approach | Requiem, Nocturnes, song endings |
| Elided/avoided cadences | V-I is approached but deflected — V goes to VI, or IV, or continues | All works; systematic from Op.40 onward |
| Enharmonic pivot modulation | One note reinterpreted (Db = C#) to shift key smoothly | Middle and late period — increasingly bold |
| Chromatic inner voices | Middle voices move by semitone while outer voices hold | Piano writing, quartet textures |
| Late austerity | Harmony stripped bare; dissonance accepted without resolution | Op.109 onward — the deaf period |

## Modal Inflection — The Faure Signature

The single most characteristic Faure technique: a diatonic melody in a clear key, with one modal note that shifts the color.

| Mode Used | Characteristic Note | Key Example | Effect |
|-----------|-------------------|-------------|--------|
| Dorian | Raised 6th in minor | B natural in D minor context | Warmth within sadness; avoids pathos |
| Mixolydian | Flat 7th in major | F natural in G major context | Relaxed, unhurried; dominant weakened |
| Lydian | Raised 4th in major | F# in C major context | Luminous, floating, slightly strange |
| Phrygian | Flat 2nd | Db in C minor context | Dark, momentary — used sparingly |
| Aeolian | Natural 7th in minor | G natural in A minor | Avoids leading-tone pull; phrases drift |

```abc
X:1
T:Faure — Modal Inflection in D minor (Dorian raised 6th)
M:6/8
L:1/8
K:Dm
%% Standard D minor melody with one Dorian note (B natural)
!p!D2E F2G|A2G F2E|D2E F2B|A6|
%% The B natural in bar 3: this is the Faure moment. One note, and the key tilts.
```

## Continuous Modulation

Faure modulates more frequently and more smoothly than any French contemporary. The technique: one note is reinterpreted enharmonically, creating a pivot that slides the key without rupture.

| Modulation Type | Mechanism | Smoothness |
|----------------|-----------|------------|
| Enharmonic pivot | Db reread as C#; key shifts from Gb to A major | Seamless — the listener barely notices |
| Common-tone modulation | One sustained note while harmony shifts around it | Very smooth — the held note anchors the shift |
| Modal slide | Mixolydian flat-7th treated as new dominant | Gentle — the key "leans" rather than "jumps" |
| Chromatic voice-leading | Inner voices move by semitone into new key | Gradual — the new key emerges rather than arriving |
| Deceptive resolution | V resolves to VI, which reinterprets as I of new key | Elegant — the expected cadence becomes a departure |

```abc
X:2
T:Faure — Enharmonic Pivot Modulation (Db = C#)
M:4/4
L:1/4
K:Db
%% Start in Db major, pivot through enharmonic reinterpretation
!p![D,F,_A,_D] [_E,_G,_B,_E] [_D,F,_A,_D] [^C,E,^G,^C]|
w: Db: I_ ii_ I_ -> A: III
%% The Db (= C#) sustains while the harmony rotates around it
```

## Plagal Cadence Preference

| Cadence Type | Progression | Faure Context |
|-------------|-------------|---------------|
| Pure plagal | IV - I | Song endings, Requiem movements |
| Dark plagal | iv - I | Minor-tinged resolution in major key passages |
| Mixolydian plagal | bVII - I | The flat-7th chord sinks to tonic |
| Extended plagal | ii - IV - I | Subdominant chain without dominant |
| Plagal + modal | IV(add9) - I | Added color to the cadence |

```abc
X:3
T:Faure — Plagal Cadences (Requiem character)
M:4/4
L:1/2
K:D
%% Three plagal endings — no dominant anywhere
[GAd] [F,A,D]|[G_Bd] [F,A,D]|[CEA] [GAd] [F,A,D]2|
w: IV-I iv-I bVII-IV-I
%% Warm, hymnal, consoling — this is the Requiem sound
```

## Avoided Cadences — The Elision

| Approach | Expected Resolution | Faure's Deflection | Effect |
|----------|--------------------|--------------------|--------|
| V7 | I | VI (deceptive) | Phrase continues without closure |
| V7 | I | IV6 (plagal substitute) | Energy redirected downward |
| V | I | bVII | Modal surprise; dominant function cancelled |
| ii-V | I | ii-V-vi-IV | The cadence becomes a new progression |
| Any approach | Tonic | New phrase begins before arrival | Elision: the old phrase and new phrase overlap |

## Harmonic Rhythm

| Context | Typical Rate | Faure Signature |
|---------|-------------|-----------------|
| Melodie (song) | 1-2 chords per bar | Flowing, supports the vocal line without crowding |
| Nocturne | 1 chord per bar, arpeggiated | The broken-chord accompaniment IS the harmonic rhythm |
| Chamber allegro | 2-4 chords per bar | More active, but voice-leading always smooth |
| Late works | Slow — 1 chord per 2 bars | Stripped, bare, almost motionless |
| Requiem | Very slow — sustained chords | Organ-like pedal tones; the harmony breathes |

## Voice-Leading Principles

| Principle | Faure's Application |
|-----------|---------------------|
| Stepwise motion in all voices | Inner voices move by step, always; no voice jumps unnecessarily |
| Common tones sustained | When chords change, shared notes are held — maximum smoothness |
| Chromatic inner voices | The tenor or alto moves by semitone while soprano and bass are stable |
| No parallel 5ths/8ves | Faure respects Classical voice-leading — unlike Debussy/Satie |
| Bass independence | The bass has its own lyrical line, not just chord roots |

## Key Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Most characteristic | D minor, G minor, E minor, Eb major, Bb major | Warm, middle register, not too bright, not too dark |
| Requiem | D minor (but ending in D major — the "lullaby" resolution) | The journey from grief to peace |
| Late works | E minor, F# minor, C minor | Darker, more austere, further from comfort |
| Avoided | Extreme sharps (F# major, C# major) | Too brilliant for Faure's intimate warmth |

## Late Period Harmonic Austerity (Op.109-121)

| Feature | Middle Period (Op.45-100) | Late Period (Op.109-121) |
|---------|--------------------------|--------------------------|
| Modulation frequency | Every 4-8 bars | Every 2-4 bars — almost continuous |
| Dissonance treatment | Prepared, resolved (mostly) | Often unresolved; dissonance as texture |
| Chord complexity | 7ths, 9ths, modal inflections | Raw intervals; bare 4ths and 5ths; sometimes near-atonal |
| Texture | Full, arpeggiated, flowing | Stripped, linear, exposed |
| Dynamic range | pp to mf | pp to p — the dynamic world contracts |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #1 (modal harmony), #4 (elided cadences)
- [melodic-style.md](melodic-style.md) — Modal inflection in melody
- [orchestration.md](orchestration.md) — Transparent voicing serves harmonic clarity
- [../../impressionist-harmony.md](../../impressionist-harmony.md) — Shared Impressionist harmonic vocabulary
- [cross-references.md](cross-references.md) — Harmonic bridge from Saint-Saens to Debussy
