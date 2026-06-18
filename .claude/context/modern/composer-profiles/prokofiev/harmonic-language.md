# Sergei Prokofiev — Harmonic Language

Prokofiev is tonal. Always. He never abandons key centers, functional harmony, or the listener's sense of where "home" is. What he does is spike that tonality with deliberately wrong notes — a chord displaced by a semitone, a bass note from the wrong key, a cadence that resolves to an unexpected triad. The wrongness is precise, intentional, and always resolves back. This is not atonality; it is tonality with a sardonic grin.

For shared modern harmonic vocabulary, see [modern-harmony.md](../../modern-harmony.md). This file covers what is distinctly Prokofievian.

## Core Harmonic Techniques

| Technique | Description | Effect |
|-----------|-------------|--------|
| Wrong-note harmony | Expected chord displaced by semitone or whole tone | Harmonic "bite" — surprise without destruction of tonality |
| Displaced tonality | Melody in one key, accompaniment shifted by m2 or M2 | Both layers sound "correct" alone; together they create friction |
| Motoric bass | Repeated bass notes or scales in mechanical rhythm | Drives momentum; the bass is a machine, not an expression |
| Lyrical diatonic | Pure, unadorned diatonic harmony in slow passages | Genuine tenderness — the real Prokofiev beneath the irony |
| Chromatic side-slipping | Brief chromatic descent or ascent before returning to key | A passing shadow; harmonic color without modulation |
| Mediant shifts | Movement by major or minor 3rd instead of 5th | Unexpected tonal color; avoids dominant-tonic predictability |
| Dominant avoidance | Cadences on IV, bVI, or bII instead of V-I | The cadence arrives, but not where expected |

## The "Wrong Note" — Prokofiev's Signature

| Strategy | Expected | Prokofiev Gives | Context |
|----------|----------|-----------------|---------|
| Semitone displacement | C major chord | Db major or B major | The most common Prokofiev substitution |
| Tritone substitute | G7 resolving to C | G7 resolving to F# or Gb | Jazz-adjacent before jazz existed |
| Major where minor expected | A minor resolution | A major (Picardy-like but unsettling) | Grotesque cheerfulness |
| Chromatic bass intrusion | C bass under C major | C# or Db bass under C major | The ground shifts beneath the listener |
| Added sharp 4th | C major triad | C-E-F#-G | Lydian color; bright but wrong |

```abc
X:1
T:Wrong-Note Harmony — C Major with Semitone Displacement
M:4/4
L:1/4
K:C
V:1 name="Melody"
V:2 name="Harmony" clef=bass
[V:1] C E G c|B A G E|C E G c|c4|
[V:2] [C,E,G,]2 [C,E,G,]2|[_D,F,_A,]2 [C,E,G,]2|[C,E,G,]2 [_D,F,_A,]2|[C,E,G,]4|
%% Bar 2 beat 1: Db major where C major expected — the Prokofiev stab
%% Bar 3 beat 2: Db again — now predictable; the "wrong" becomes the language
```

## Harmonic Rhythm

| Context | Harmonic Rhythm | Character |
|---------|----------------|-----------|
| Motoric allegro | 1 chord per bar or faster; steady | Machine-like; no rubato |
| Lyrical andante | 1 chord per 2 bars; slow, warm | Breathing room; genuine expression |
| Grotesque march | 2 chords per bar; jagged | Lurching; slightly drunk |
| Toccata passage | Static harmony; melody moves over pedal | Hypnotic; rhythm is the event |
| Cadence | Sudden; no preparation | The cadence arrives like a door slamming |

## Prokofiev's Cadences

| Cadence Type | Progression | Effect |
|-------------|-------------|--------|
| Wrong-note authentic | V7 - bII (instead of I) | Resolution displaced; unsettling arrival |
| Sudden tonic | Chromatic passage - I (no V) | Home appears without preparation |
| Mediant cadence | I - bVI - I | The detour IS the cadence |
| Motoric close | Repeated tonic chord, ff, staccato | The piece stops rather than ends |
| Lyrical plagal | IV - I, pp, legato | The tender Prokofiev cadence |

```abc
X:2
T:Prokofiev Cadence Types
M:4/4
L:1/4
K:C
%% Wrong-note cadence: V7 resolving to Db major instead of C
[G,B,DF]2 [_D,F,_A,_d]2|
%% Sudden tonic: chromatic approach, then C major lands
[^G,B,^D^G] [A,CE] [_B,_DF] [C,EGc]|
%% Motoric close: C major hammered, staccato
!ff![CEGc] [CEGc] [CEGc] [CEGc]|
```

## Key Areas and Tonal Centers

| Period | Preferred Keys | Character |
|--------|---------------|-----------|
| Early (enfant terrible) | D minor, C minor, Bb minor | Dark, aggressive; sharp keys for brilliance |
| Emigre/ballet | C major, D major, Bb major | Bright, clear; Classical transparency |
| Soviet/lyrical | Bb major, F major, G major | Warm, singing; simpler tonal relationships |
| War Sonatas | Bb minor, A major, C major | Dark opening keys; triumph in major |

## Voice-Leading Principles

| Principle | Prokofiev's Approach |
|-----------|---------------------|
| Parallel motion | Freely used in fast passages; parallel 5ths and octaves acceptable |
| Chromatic voice-leading | Voices move by semitone to "wrong" chord, then back |
| Bass independence | Bass often moves by step while upper voices leap |
| Doubling | Octave doublings in fast passages for power; unison writing |
| Pedal points | Long tonic or dominant pedals under moving harmony |

```abc
X:3
T:Displaced Tonality — Melody in C, Bass in Db
M:3/4
L:1/8
K:C
V:1 name="Melody (C major)"
V:2 name="Bass (Db)" clef=bass
[V:1] !mf!C2 D2 E2|F2 E2 D2|C6|
[V:2] _D,2 F,2 _A,2|_D,2 F,2 _A,2|_D,6|
%% The melody is clearly C major; the bass is clearly Db major
%% Neither is "wrong" — together they create the Prokofiev friction
```

## Harmonic Application by Section Type

| Section Type | Primary Technique | Secondary |
|-------------|-------------------|-----------|
| Opening theme | Clear key + one wrong note per phrase | Mediant shifts |
| Development | Chromatic side-slipping, rapid key changes | Motoric bass |
| Lyrical second theme | Pure diatonic, minimal dissonance | Plagal color |
| Scherzo/grotesque | Semitone displacement every 2 bars | Tritone bass |
| March | Strong tonic, one chromatic intrusion per phrase | Parallel motion |
| Coda | Motoric close OR lyrical plagal | Sudden tonic |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #1 (wrong-note), WMN directives
- [melodic-style.md](melodic-style.md) — How melody interacts with displaced harmony
- [orchestration.md](orchestration.md) — How harmonic layers are distributed
- [cross-references.md](cross-references.md) — vs Stravinsky's wrong-note technique
- [../../modern-harmony.md](../../modern-harmony.md) — Shared modern harmonic vocabulary
