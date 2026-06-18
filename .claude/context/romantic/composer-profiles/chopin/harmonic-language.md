# Frederic Chopin — Harmonic Language

Chopin's harmony does not argue — it seduces. Where Beethoven's chromaticism is a hammer blow and Wagner's is an ocean, Chopin's is a single tear sliding down the face of a consonance. His chromatic voice-leading transforms the simplest progressions into something aching and personal. The harmony never shouts; it leans, it sinks, it pivots to a distant key as quietly as turning a page.

For shared Romantic harmonic vocabulary (chromatic mediants, augmented sixths, Neapolitan, enharmonic modulation, deceptive cadences), see [romantic-harmony.md](../../romantic-harmony.md). This file covers what is distinctly Chopinesque.

---

## Core Harmonic Character

| Feature | Description | Typical Usage |
|---------|-------------|--------------|
| Chromatic inner-voice descent | Middle voice sinks by semitone while soprano holds | Nocturnes, slow ballade passages — the "ache beneath beauty" |
| Enharmonic pivot modulation | Dim7 or Ger+6 respelled to reach remote keys | Ballades, Fantasie — the listener arrives somewhere new without noticing the door |
| Extended dominant prolongation | V7 or V9 sustained 4-8 bars with soprano ornamentation above | Nocturne climaxes — the resolution is delayed until it becomes unbearable |
| Neapolitan as color | bII6 used not just pre-cadentially but as a tonal region | Ballades, Scherzi — moments of dark gravitas |
| Plagal tenderness | IV-I or iv-I replacing V-I at phrase ends | Berceuse, late Nocturnes — resolution without tension |
| Pedal-point harmony | Remote chords float over a sustained tonic or dominant bass | Berceuse (68 bars over tonic pedal); Barcarolle coda |
| Applied dominants in chains | V7/V, V7/IV, V7/vi linked smoothly | Etudes, Polonaises — harmonic propulsion without leaving the key |
| Mode mixture as nostalgia | iv, bVI, bVII borrowed from parallel minor | Mazurkas, Nocturnes — shadow passing through light |

---

## Chromatic Inner-Voice Technique

The signature Chopin sound: soprano holds a long note; an inner voice descends chromatically beneath it. This is NOT parallel motion — only the inner voice moves.

| Soprano | Inner Voice | Bass | Implied Harmony | Emotional Effect |
|---------|-------------|------|-----------------|-----------------|
| Bb4 (held) | D4 → Db4 → C4 → B3 | Eb2 → Ab2 → F2 → G2 | Eb → Ab → Fm → G7 | Warmth → ache → deepening → tension |
| F5 (held) | A4 → Ab4 → G4 | Dm → Bb → C → F | ii → bVII → V → I | Gentle descent to resolution |
| Eb5 (held) | G4 → Gb4 → F4 → E4 | Cm → Ab → Fm → C | i → bVI → iv → I(Picardy) | Darkness → warmth → acceptance |

```abc
X:1
T:Chopin Chromatic Inner Voice — Nocturne Texture
M:3/4
L:1/4
K:Eb
V:1 clef=treble
V:2 clef=bass
%% Soprano holds Bb; inner voice descends D-Db-C
[V:1] [DB]2 [DB]|[_DB]2 [_DB]|[CB]2 [CB]|
[V:2] _E,2 _E,|_A,,2 _A,,|F,,2 F,,|
%% The soprano is a held star; the inner voice is the earth slowly turning
```

---

## Enharmonic Modulation Techniques

| Pivot Type | Original Function | Reinterpreted As | Key Change | Example Context |
|-----------|-------------------|-----------------|------------|-----------------|
| Diminished 7th | viio7 of C minor | viio7 of Eb minor | Cm → Ebm | Ballade No. 1 development |
| German augmented 6th | Ger+6 in F minor | V7 of Gb major | Fm → Gb | Ballade No. 4 |
| Dominant 7th = Ger+6 | V7 of Db | Ger+6 in C minor | Db → Cm | Nocturne Op. 48/1 |
| Enharmonic dim7 chain | viio7 respelled 3 ways | 4 equidistant keys accessible | Cm → Em → G#m → Bbm | Fantasie Op. 49 |
| Common-tone dim7 | CT dim7 over held bass | Chromatic neighbor to I | Local color, no real modulation | Nocturnes — shimmer effect |

```abc
X:2
T:Chopin Enharmonic Pivot — Dim7 Respelling
M:4/4
L:1/4
K:Cm
%% viio7 of C minor = viio7 of Eb minor (respelled)
[=B,DF_A] [CEGc]|[=B,DF^G] [_B,_EG_B]|
w: viio7/C→C viio7(=)/Ebm→Ebm
%% Same diminished chord, two different resolutions — the door swings both ways
```

---

## Extended Dominant Prolongation

Chopin's most intense emotional passages often sit on a dominant harmony for 4-8 bars while the melody ornaments, builds, and cascades above it.

| Stage | Bars | What Happens Above | Dynamic Arc |
|-------|------|-------------------|-------------|
| Arrival on V | 1-2 | Melody reaches dominant; simple statement | p, espressivo |
| Ornamentation | 3-4 | Chromatic turns, grace notes around structural tones | p → mp |
| Intensification | 5-6 | Faster figuration, wider range, passagework builds | mp → mf |
| Cascade/resolution | 7-8 | Chromatic run from peak, resolves to I on last beat | f → p subito |

```abc
X:3
T:Chopin Extended Dominant — Nocturne Climax Pattern
M:3/4
L:1/16
K:Eb
%% 4 bars on Bb7 (V7 of Eb) — melody builds above
!p!F4 D4 F4|!mp!G4 A4 B4|!mf!c4 d4 e4 |!f!d4c4B4A4 G4F4E4D4|
%% Resolution to Eb arrives after the cascade spends itself
```

---

## Pedal-Point Harmony

| Pedal Type | Duration | Harmony Above | Example Work |
|-----------|----------|---------------|-------------|
| Tonic pedal | 68 bars | I, V7, ii, V7/V, bII, viio7 — all over Db bass | Berceuse Op. 57 |
| Dominant pedal | 8-16 bars | Remote chords float over V | Nocturne Op. 48/1 middle section |
| Inverted tonic pedal | Full section | Soprano holds tonic; LH harmony moves beneath | Barcarolle coda — F# sustained above shifting harmony |
| Double pedal (1+5) | 4-8 bars | Inner voices move chromatically between fixed outer voices | Late Nocturnes |

---

## Chopin's Cadence Palette

| Cadence Type | Progression | Character | Typical Context |
|-------------|-------------|-----------|----------------|
| Decorated PAC | V7 with chromatic run → I | The arrival is ornamented, not blunt | Nocturne phrase endings |
| Plagal close | iv → I or IV → I | Tender, hymn-like; avoids dominant tension | Berceuse, Barcarolle codas |
| Deceptive to bVI | V7 → bVI | The heart opens instead of closing | Ballade climaxes |
| Half-cadence with trill | ii → V (trill on leading tone) | Suspension — the phrase is not done | Nocturne mid-phrase |
| Phrygian half-cadence | iv6 → V | Spanish/modal darkness | Mazurkas, Ballade No. 1 |
| Evaded cadence | V → I6 (not root) | The phrase continues past its expected end | Everywhere — Chopin rarely gives a simple full stop |

```abc
X:4
T:Chopin Cadence Comparison
M:3/4
L:1/4
K:Cm
%% Decorated PAC: V7 with chromatic turn → i
[=B,DG] [=B,DF]|!trill![CEG]2 z|
%% Phrygian half-cadence: iv6 → V
[FA_B_D] [=BDG]|z3|
w: V7 appog i _ iv6 V
```

---

## Harmonic Rhythm

| Context | Typical Rate | Effect |
|---------|-------------|--------|
| Nocturne melody | 1 chord per bar | Spacious singing; melody floats |
| Mazurka | 1 chord per bar, changing on beat 3 | Dance lift; the harmony lands late |
| Etude figuration | 2 chords per bar | Propulsion within pattern |
| Ballade development | Accelerating: 1/bar → 2/bar → 1/beat | Building toward crisis |
| Climax | Held chord (V or I) for 4+ bars | Time stops at the peak |
| Coda | Decelerating; final tonic sustained | Breath after the storm |

---

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #3 (chromatic inner voice), #4 (enharmonic modulation)
- [melodic-style.md](melodic-style.md) — How harmonic choices support the bel canto line
- [formal-approach.md](formal-approach.md) — How harmony articulates form in ballades and sonatas
- [../../romantic-harmony.md](../../romantic-harmony.md) — Shared Romantic vocabulary: chromatic mediants, augmented 6ths, sequences
- [cross-references.md](cross-references.md) — Harmonic contrasts with Liszt, Schumann, and later Debussy
