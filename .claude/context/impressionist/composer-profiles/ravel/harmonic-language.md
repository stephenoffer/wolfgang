# Maurice Ravel — Harmonic Language

Ravel's harmony is functional — but barely, and beautifully. Where Debussy abandoned tonal function entirely, Ravel keeps one foot in Classical tonal logic while extending his chords into jazz-adjacent territory. A Ravel progression often has a root movement you can analyze (ii-V-I) but the chords themselves are so richly colored — 9ths, 11ths, 13ths, added notes — that the function is felt rather than heard. The precision is the point: every note of every chord is placed in a specific register for a specific timbral reason.

For shared Impressionist harmonic vocabulary, see [impressionist-harmony.md](../../impressionist-harmony.md). This file covers what is distinctly Ravelian.

## Core Harmonic Character

| Feature | Description | Artistic Function |
|---------|-------------|-------------------|
| Extended chords as primary vocabulary | 9ths, 11ths, 13ths are the norm, not exceptions | Richness without loss of clarity — every extension is voiced transparently |
| Functional roots with colorful upper structure | Bass moves in recognizable patterns (ii-V-I); upper voices add color | The listener feels harmonic direction while hearing iridescent color |
| Bitonality | Two key areas sounding simultaneously | Beautiful friction — "almost right" creates emotional complexity |
| Jazz-adjacent voicings | Major 7ths, dominant 9ths, added 6ths used as stable sonorities | Anticipates jazz harmony by decades; Bill Evans acknowledged the debt |
| Spanish/Phrygian color | Lowered 2nd scale degree (Phrygian dominant) in bass or melody | Iberian warmth; guitar-like strumming patterns |
| Precise parallel motion | Parallel chords where each voice is distinctly audible | Unlike Debussy's atmospheric wash — Ravel's parallels are crystalline |
| Mechanical repetition of harmonic patterns | Same progression repeated exactly, many times | Hypnotic — the repetition itself becomes expressive (Boléro) |

## Extended Chord Voicing — The Ravel Difference

Ravel's chords are never a "wash" — each note occupies its own register, clearly audible. This is what separates Ravel from Debussy harmonically.

| Chord Type | Ravel Voicing Principle | Register Spread | Effect |
|-----------|------------------------|----------------|--------|
| Major 9th | Root in bass, 3rd in tenor, 7th in alto, 9th on top | 2-3 octaves | Luminous, spacious |
| Dominant 13th | Root and 7th in bass, 9th-11th-13th spread above | 3+ octaves | Maximum color with complete clarity |
| Added 6th | Triad in close position, 6th placed a 9th above root | 1.5-2 octaves | Sweet, nostalgic — Pavane sonority |
| Major 7th #11 | Root-5th-7th in bass, #11 on top | 2+ octaves | Lydian sparkle; bright, open |
| Minor 9th | Root-5th in bass, b7-9 in middle, b3 on top | 2-3 octaves | Dark warmth — Ravel's melancholy |

```abc
X:1
T:Ravel — Extended Chord Voicing (Concerto in G character)
M:4/4
L:1/4
K:G
V:1 clef=treble
V:2 clef=bass
%% Gmaj9 → Am11 → Bm7 → Cmaj7#11 — functional roots, colorful extensions
[V:1] [B,DF^A] [CEGb] [DFA] [EG^Fc] |
[V:2] G,,2 A,,2 | B,,2 C,2 |
%% Root movement: G-A-B-C (stepwise, functional). Upper structure: 9ths, 11ths, #11 — Ravel color.
```

## Bitonality

Ravel superimposes two tonal centers simultaneously. The result is not chaos but a specific, controlled dissonance — two keys rubbing against each other with precision.

| Bitonal Combination | Technique | Effect | Example |
|--------------------|-----------|--------|---------|
| Melody in Gb / bass in C | RH pentatonic on Gb; LH pedal C | Dreamlike friction — "wrong" but beautiful | Concerto for Left Hand |
| Triads a tritone apart | C major + F# major sounding together | Shimmering maximum tension | La Valse, climactic passages |
| LH in one key, RH in another | Two clear tonal layers | The listener hears both; neither resolves | Valses nobles, No. 7 |
| Phrygian melody over major bass | Db melodic inflection over C major | Spanish color without full modulation | Rapsodie espagnole |

```abc
X:2
T:Ravel — Bitonality (Superimposed triads)
M:3/4
L:1/4
K:C
V:1 clef=treble name="RH: F# major"
V:2 clef=bass name="LH: C major"
%% Two keys a tritone apart — Ravel's controlled dissonance
[V:1] [^F^Ac] [^F^Ac] [^GAd] |
[V:2] [C,EG] [C,EG] [D,FA] |
%% Both layers are clear triads. The friction between C and F# is the harmony.
```

## Spanish/Phrygian Harmony

Ravel's Basque heritage surfaces as Spanish harmonic color — the lowered 2nd degree (Phrygian), guitar-like strumming, and the characteristic harmonic flamenco cadence.

| Spanish Technique | Harmonic Device | Character |
|-------------------|----------------|-----------|
| Phrygian cadence | bII → I (Db major → C major in A minor context) | Dark, flamenco, final |
| Phrygian dominant | V chord with b9 (E-G#-B-D-F in A minor) | Exotic, tense, Spanish |
| Habanera bass | Tonic-dominant alternation with syncopated rhythm | Sensuous, dance-like |
| Strummed guitar imitation | Quick arpeggiated chords, repeated | Percussive warmth |
| Augmented 2nd in melody | Raised 3rd in Phrygian mode (A-Bb-C#-D) | "Gypsy" color |

```abc
X:3
T:Ravel — Spanish Phrygian Cadence (Rapsodie espagnole character)
M:3/4
L:1/8
K:Am
%% Phrygian cadence: Bb major → A major (bII → I in A)
_B2d2f2 | e2^c2A2 | A6 |
%% The Bb to A resolution — not dominant-tonic but Phrygian. The Spanish door closes.
```

## Jazz-Adjacent Harmony

Ravel absorbed jazz during his 1928 American tour and through George Gershwin. The Piano Concerto in G, the Violin Sonata (Blues movement), and late works show jazz harmony assimilated into Classical form.

| Jazz Element | Ravel's Usage | Example |
|-------------|---------------|---------|
| Blue notes (b3, b7) | Integrated into modal/tonal context, not improvised | Violin Sonata mvt 2 "Blues" |
| Dominant 9th as resting chord | V9 sustained without resolution | Concerto in G, slow movement |
| Walking bass with extended chords | Bass in regular rhythm under rich harmony | Concerto in G, mvt 1 |
| Quartal voicings | Stacked 4ths in piano or wind writing | Late chamber works |

## Harmonic Rhythm

| Context | Typical Rhythm | Effect |
|---------|---------------|--------|
| Boléro-type ostinato | 1 chord sustained for 8-16 bars | Hypnotic — harmony IS the pedal |
| Waltz | 1-2 changes per bar, regular | Dance momentum, elegant |
| Slow movement | 1 per 2-4 beats (savored) | Each chord is a color event |
| Spanish dance | Syncopated changes (habanera) | Rhythmic harmony — the change IS the rhythm |
| Concerto dialogue | Variable, conversation-paced | Dramatic — piano and orchestra trade harmonic initiative |

## Cadential Vocabulary

| Cadence Type | Ravel's Usage | Character |
|-------------|---------------|-----------|
| Perfect authentic (V7-I) | Still used — Ravel respects Classical closure | Clear arrival; sometimes with added 9th on the I chord |
| Plagal (IV-I) | Common in pastoral/archaic contexts | Warm, non-dramatic |
| Phrygian (bII-I) | Spanish pieces; dark, modal | Flamenco closure |
| Deceptive (V-vi) | Phrase extension | The listener waits; Ravel delays |
| Added-note PAC | V9 → Iadd6 or V13 → Imaj9 | Classical function, Impressionist color |
| Mechanical repeat to close | Same cadential pattern repeated exactly | Boléro ending: the repetition IS the structure |

## References

- [composition-guide.md](composition-guide.md) — crystalline voicing WMN examples
- [biography.md](biography.md) — Basque heritage, jazz encounter, Fauré training
- [melodic-style.md](melodic-style.md) — Spanish melody over jazz harmony
- [orchestration.md](orchestration.md) — how voicing translates to orchestral scoring
- [../../impressionist-harmony.md](../../impressionist-harmony.md) — shared extended chord types, planing techniques
