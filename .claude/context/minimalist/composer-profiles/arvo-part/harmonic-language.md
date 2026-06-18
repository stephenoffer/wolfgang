# Arvo Pärt — Harmonic Language

## Core Principle: Tintinnabuli Harmony

Harmony in Pärt is not chord progression — it is the **simultaneous sounding of two voices** whose relationship IS the harmony. There are no "chords" in the conventional sense; there is only the interval between M-voice and T-voice at any given moment.

## The Two-Voice System

| Voice | Function | Pitch Material | Motion |
|-------|----------|---------------|--------|
| M-voice (melodic) | Stepwise diatonic line | All notes of the diatonic scale | Steps only, never leaps |
| T-voice (tintinnabuli) | Triadic resonance | Only 3 notes of tonic triad | Nearest triad tone to M-voice |

## T-Voice Position Types

| Position | Rule | Over M-voice D in A minor (A-C-E triad) |
|----------|------|------------------------------------------|
| 1st superior | Nearest triad tone above | E |
| 2nd superior | Second-nearest triad tone above | A |
| 1st inferior | Nearest triad tone below | C |
| 2nd inferior | Second-nearest triad tone below | A (below) |
| Alternating | Switches above/below each note | E, C, A, C, E... |

```abc
X:1
T:T-voice Positions Demonstrated (A minor)
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (1st superior)"
E A E C | E A E C |
V:2 name="M-voice (ascending)"
A B C D | E F G A |
% Each T-voice note is the nearest A-C-E triad tone ABOVE the M-voice note
```

```abc
X:2
T:T-voice Alternating Position
M:4/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (alternating)"
E C A C | E C A C |
V:2 name="M-voice"
D E F G | A B c d |
% T-voice alternates: above, below, above, below
```

## Resultant Intervals

| M-voice note (A minor scale) | T-voice 1st sup. | Interval | Consonance |
|------------------------------|-------------------|----------|------------|
| A | A (unison) | P1 | Perfect |
| B | C | m2 | Dissonance — the characteristic friction |
| C | C (unison) | P1 | Perfect |
| D | E | M2 | Mild dissonance |
| E | E (unison) | P1 | Perfect |
| F | A | m3 | Consonant |
| G | A | M2 | Mild dissonance |

The dissonances are **not resolved** — they simply occur as the system dictates. The B/C minor second is characteristic of tintinnabuli: an unavoidable friction within a pure system.

## Harmonic Stasis — No Progression

| What Pärt Does NOT Use | Why |
|------------------------|-----|
| Chord progressions (I-IV-V-I) | No functional harmony — single triad throughout |
| Secondary dominants | No dominant function at all |
| Modulation | One key, one triad, entire piece |
| Chromatic alteration | Purely diatonic — no sharps/flats outside the key |
| Suspensions / preparations | No voice-leading rules in the Classical sense |
| Cadences (authentic, plagal) | No cadential function; pieces end by process completion |

## Bell Resonance — The Acoustic Model

| Bell Property | Tintinnabuli Equivalent |
|--------------|------------------------|
| Fundamental tone | Root of the tonic triad |
| Partials (overtones) | T-voice triad tones |
| Decay pattern | Long note values, diminuendo to silence |
| Strike tone | M-voice attack on each note |
| Residual hum | T-voice sustained beneath M-voice |

```abc
X:3
T:Bell Resonance Model — Cantus in Memoriam Style
M:6/4
L:1/4
K:Am
%%staves {1 2}
V:1 name="T-voice (bell)"
A2 E2 A2 | C2 E2 A2 |
V:2 name="M-voice (descending)"
A2 G2 F2 | E2 D2 C2 |
% The T-voice rings while the M-voice descends — like a bell humming as partials fade
```

## Harmonic Color by Key Choice

| Key | Character in Pärt | Works |
|-----|-------------------|-------|
| A minor | Solemn, devotional, the "home" key | *Für Alina*, *Spiegel im Spiegel* |
| D minor | Darker, more austere | *Fratres* (some versions), *Passio* |
| B minor | Intimate, inward | *Für Alina* (original) |
| C major | Luminous, rare — used for radiance | Selected choral works |
| F major | Warm, pastoral | *Berliner Messe* sections |

## Vertical Sonority Inventory

| Sonority | Occurrence | Expressive Weight |
|----------|-----------|-------------------|
| Unison (P1) | When M-voice lands on triad tone | Moments of alignment — clarity |
| Minor 2nd | M-voice on scale step adjacent to triad tone | The characteristic "friction" — poignant |
| Major 2nd | M-voice between triad tones | Gentle tension |
| Minor 3rd | M-voice a 3rd from triad tone | Warm consonance |
| Major 3rd | M-voice a 3rd from triad tone | Bright consonance |
| Perfect 5th | M-voice on 5th of triad | Open, spacious |
| Octave | M-voice doubles triad tone at distance | Expansive stillness |

## Multi-Voice Tintinnabuli (3+ parts)

| Texture | Structure | Example Work |
|---------|-----------|--------------|
| 2 voices | M + T (basic) | *Für Alina* |
| 3 voices | M + T + bass drone | *Spiegel im Spiegel* |
| 4 voices (SATB) | 2 M-voices + 2 T-voices | *Passio*, choral works |
| Orchestral | Multiple M/T pairs in different registers | *Cantus in Memoriam Benjamin Britten* |
| Canon | M-voice in canon, each with own T-voice | *Fratres* |

```abc
X:4
T:Three-Voice Tintinnabuli (Spiegel im Spiegel style)
M:3/4
L:1/4
K:Am
%%staves {1 2 3}
V:1 name="M-voice (violin)"
B C D | E F G | A G F |
V:2 name="T-voice (piano RH)"
C E A | E A C' | E C A |
V:3 name="Bass drone (piano LH)"
A,3 | A,3 | A,3 |
% Three layers: stepping melody, ringing triad, sustaining root
```

## References
- Hillier, Paul. *Arvo Pärt* (Oxford Studies of Composers), 1997
- Brauneiss, Leopold. "Musical Archetypes: The Basic Elements of the Tintinnabuli Style," in *The Cambridge Companion to Arvo Pärt*, 2012
- Cizmic, Maria. *Performing Pain: Music and Trauma in Eastern Europe*, 2012
