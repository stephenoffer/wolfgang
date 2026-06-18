# Franz Liszt — Harmonic Language

Liszt's harmony is a blade that cuts open the tonal system. Where Chopin's chromaticism whispers and seduces, Liszt's chromaticism assaults, pivots, and sometimes abandons tonality entirely. He was the first to build entire passages on augmented triads — chords with no gravitational center. He was the first to use the whole-tone scale as a compositional resource. His late works contain passages that are genuinely atonal, thirty years before Schoenberg. The harmonic language evolves so radically across his career that "Liszt harmony" is not one thing — it is a trajectory from Romantic chromaticism toward the dissolution of key.

For shared Romantic harmonic vocabulary (chromatic mediants, augmented sixths, Neapolitan, enharmonic modulation), see [romantic-harmony.md](../../romantic-harmony.md). This file covers what is distinctly Lisztian.

---

## Core Harmonic Character

| Feature | Description | Typical Usage |
|---------|-------------|--------------|
| Augmented triad chains | Sequences of augmented chords sharing two common tones | Faust Symphony (Mephistopheles), Dante Sonata — harmonic groundlessness |
| Whole-tone passages | Melody and/or harmony moving by whole steps only | Late works; also Faust Symphony tritone motif |
| Enharmonic pivot modulation | Reinterpreting a chord (dim7, aug triad, Ger+6) to jump to remote keys | Everywhere — Liszt modulates to anywhere, instantly |
| Tritone axis | Keys a tritone apart treated as related (C and F#) | B minor Sonata (B-F relationship); Mephisto Waltz |
| Chromatic saturation | Bars where every semitone is sounded; key dissolves | Development sections; Mephistopheles scherzo |
| Non-resolving dominants | V7 or V9 chords that slide to another V7 instead of resolving | Chromatic sequences; creates perpetual motion without arrival |
| Late-period atonality | Passages with no discernible key center | Nuages gris, Bagatelle sans tonalite, Unstern! |
| Augmented 6th as pivot | Ger+6 = V7 of distant key; instant modulation | Standard Romantic technique but Liszt uses it more freely |
| Pedal point under remote harmony | Tonic or dominant pedal sustained while wild chromaticism happens above | Dante Sonata; creates tension between stability and chaos |

---

## The Augmented Triad: Liszt's Signature Chord

The augmented triad divides the octave into three equal major thirds. It belongs to NO key. Three augmented triads cover all 12 pitches.

| Augmented Triad | Notes | Enharmonic Equivalents | Keys It Can Resolve To |
|----------------|-------|----------------------|----------------------|
| Aug I | C-E-G# | C+, E+, Ab+ | Am, C#m, Fm, C, E, Ab |
| Aug II | Db-F-A | Db+, F+, A+ | Bbm, Dm, F#m, Db, F, A |
| Aug III | D-F#-A# | D+, F#+, Bb+ | Bm, Eb m, Gm, D, F#, Bb |

**Voice-leading principle:** Move ANY one note of an augmented triad by a semitone and you get a major or minor triad. This is why Liszt chains them — each is a crossroads to six possible destinations.

```abc
X:1
T:Liszt Augmented Triad Chain — Faust Symphony Character
M:4/4
L:1/2
K:C
%% Each augmented triad shares 2 notes with the next; key dissolves
[CE^G] [^CE^G] | [^CF^A] [^C^FA] | [DA^F] [D^FA] |
w: C+ C#+ F+ F#+ D+ D+
%% No key — the harmony floats between worlds
```

---

## Whole-Tone Scale Usage

| Context | Scale Form | Harmonic Function | Example |
|---------|-----------|------------------|---------|
| Mephistopheles theme | C-D-E-F#-G#-A# | Represents the demonic/ironic | Faust Symphony, mvt 3 |
| Transitional passages | Ascending whole-tone over tremolo bass | Bridges between tonal sections | Dante Sonata |
| Late piano works | Melody in whole tones; harmony absent | Complete tonal dissolution | Nuages gris, Unstern! |
| Descending sequences | Whole-tone bass descent under diminished chords | Creates sliding, sinking effect | Mephisto Waltz No. 1 |

```abc
X:2
T:Liszt Whole-Tone Passage — Mephistopheles Character
M:4/4
L:1/8
K:C
%% Whole-tone scale ascending — no leading tone, no gravity
!p!C2 D2 E2 ^F2|^G2 ^A2 c2 d2|e2 ^f2 ^g2 ^a2|
%% The devil has no home key
```

---

## Enharmonic Modulation Techniques

| Pivot Type | Original Function | Reinterpreted As | Key Change | Example Work |
|-----------|-------------------|-----------------|------------|-------------|
| Diminished 7th (4 keys) | viio7 of C | viio7 of Eb, F#, A | C to anywhere equidistant | B minor Sonata development |
| Augmented triad (3 keys) | Aug of C | Aug of E, Aug of Ab | C to E or Ab instantly | Faust Symphony |
| German Aug 6th = V7 | Ger+6 in C | V7 of Db | C to Db | Les Preludes |
| V7 = Ger+6 | V7 of C | Ger+6 of B | C to B | Dante Symphony |
| Common-tone modulation | Hold one note; change everything else | Root, 3rd, or 5th of new chord | Anywhere | Mephisto Waltz No. 1 |
| Tritone substitution | V7 of C (G7) | V7 of Gb (Db7) | C to Gb | Late works; proto-jazz |

```abc
X:3
T:Liszt Enharmonic Pivot — Dim7 Four-Way Crossroads
M:4/4
L:1/4
K:C
%% Same dim7 chord resolves to 4 different keys
[=B,DF_A] [CEGc]|[=B,DF_A] [^CE^Gc]|[=B,DF^G] [^C^EA^c]|[=B,DF_A] [_B,_EG_B]|
w: viio7->C viio7->C# viio7->A viio7->Ebm
```

---

## Tritone Axis

Liszt treats keys a tritone apart as structural mirrors. The B minor Sonata's tonal plan orbits B and F — the tritone poles.

| Work | Primary Key | Tritone Pole | How They Interact |
|------|------------|-------------|-------------------|
| Sonata in B minor | B minor | F major/minor | Second theme in F; development oscillates B-F |
| Mephisto Waltz No. 1 | A major | Eb/D# | Mephistopheles' key opposes the village dance |
| Faust Symphony | C minor (Faust) | F# (Mephistopheles) | Tritone = the demonic inversion |
| Dante Sonata | D minor | Ab | Inferno vs. Purgatorio tonal conflict |

---

## Late-Period Harmonic Dissolution

After 1870, Liszt wrote pieces that abandon conventional harmony. These are not failures of craft — they are deliberate experiments in what music sounds like without tonality.

| Technique | Description | Example Work |
|-----------|-------------|-------------|
| Unresolved augmented triads | Final chord is augmented — no tonic | Nuages gris (1881) |
| Bare parallel fifths | Medieval/archaic texture, no functional harmony | Via Crucis (1879) |
| Tritone oscillation | Two notes a tritone apart alternate; no resolution | Unstern! (1881) |
| Whole-tone melody over silence | Melody without harmonic support | Bagatelle sans tonalite (1885) |
| Chords built on fourths | Quartal harmony replacing triads | Late pieces anticipate Scriabin, Bartok |
| No cadence at end | Music stops rather than concludes | Multiple late works — the void |

```abc
X:4
T:Liszt Late Harmonic Dissolution — Bagatelle Character
M:3/4
L:1/4
K:C
%% No key signature meaningful; tritone oscillation
!pp!B,2 F|B,2 F|_E2 _B|_E2 _B|
%% Bare tritones. No resolution. No home. This is 1885.
```

---

## Cadence Types

| Cadence | Progression | Character | Where Used |
|---------|-------------|-----------|-----------|
| Heroic PAC | Ger+6 -> Cad64 -> V7 -> I (ff, marcato) | Triumphant arrival | Les Preludes conclusion; concerto endings |
| Deceptive to augmented | V7 -> Aug triad | The ground dissolves instead of resolving | Faust Symphony; development sections |
| Plagal with Picardy | iv -> I (major) | Religious, organ-like | Sacred works; Weimar period codas |
| No cadence (late) | Music stops on dissonance or silence | The void | Nuages gris, Unstern!, late piano works |
| Rhetorical caesura | Full stop (silence) -> restart in new key/tempo | Theatrical gesture | B minor Sonata; throughout career |
| Hungarian cadence | Augmented 2nd in bass -> V -> i with ornament | Folk character | Hungarian Rhapsodies |

---

## Harmonic Rhythm

| Context | Typical Rate | Effect |
|---------|-------------|--------|
| Heroic transformation | 1 chord per bar; massive sonority | Weight, grandeur |
| Virtuosic passage | 2-4 chords per bar over running figuration | Momentum, brilliance |
| Augmented chain | 1 chord per beat; each chord pivots | Groundlessness, vertigo |
| Late sparse texture | 1 chord per 2-4 bars; silence between | Desolation, timelessness |
| Hungarian lassan | Slow; rubato; chord on beat 1, ornament fills bar | Improvisatory weight |
| Cadential drive | Accelerating: 1/bar -> 2/bar -> 1/beat -> fff arrival | Maximum tension to release |

---

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #3 (chromatic saturation), augmented chains in practice
- [melodic-style.md](melodic-style.md) — How harmonic choices support thematic transformation
- [formal-approach.md](formal-approach.md) — How harmony articulates the one-movement sonata form
- [stylistic-evolution.md](stylistic-evolution.md) — How the harmonic language changes across three periods
- [../../romantic-harmony.md](../../romantic-harmony.md) — Shared Romantic vocabulary (don't duplicate)
- [cross-references.md](cross-references.md) — Harmonic contrasts with Chopin, Wagner, and forward to Debussy
