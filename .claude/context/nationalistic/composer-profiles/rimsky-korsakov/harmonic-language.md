# Nikolai Rimsky-Korsakov — Harmonic Language

Rimsky-Korsakov's harmony is a system of colors. Where Mussorgsky moved chords by instinct and Wagner dissolved them into chromaticism, Rimsky organized modal and synthetic scales into a coherent language: diatonic for the real world, octatonic for magic, whole-tone for mystery. His harmony is not merely colorful — it is systematically colorful, each scale assigned a dramatic meaning.

For shared nationalistic harmonic vocabulary (modal cadences, drone harmony, folk modes), see [nationalistic-harmony.md](../../nationalistic-harmony.md). This file covers what is distinctly Rimsky-Korsakovian.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Octatonic scale as system | Alternating W-H (C-D-Eb-F-F#-G#-A-B) or H-W for supernatural/magic scenes | Snow Maiden, Sadko, Kashchei — all magic characters |
| "Real vs. magic" harmony | Diatonic = human world; octatonic/whole-tone = supernatural world | All fairy-tale operas; the harmonic language IS the dramaturgy |
| Whole-tone for mystery | Whole-tone scale (C-D-E-F#-G#-A#) for floating, rootless passages | Sea scenes (Sadko), dreamlike transitions |
| Brilliant color harmony | Major-key brightness with modal inflections; the harmony shimmers | Scheherazade, Capriccio espagnol, Russian Easter |
| Pedal-point grounding | Long dominant or tonic pedals under changing upper harmony | Orchestral showpieces; creates harmonic shimmer over stable base |
| Chromatic mediant shifts | Third-related key changes (C to E, C to Ab) for dramatic color | Between "real" and "magic" scenes; tonal juxtaposition |
| Tritone axis | Keys a tritone apart as paired opposites (C and F#) | Kashchei: the deathless one's key is the tritone of the heroine's |

## The Octatonic Scale — Rimsky's Signature

Rimsky-Korsakov was the first composer to use the octatonic scale systematically. It became his harmonic fingerprint and the foundation of Russian harmonic modernity (inherited by Stravinsky and Scriabin).

| Scale Form | Pitches (on C) | Character | Dramatic Use |
|-----------|---------------|-----------|-------------|
| Octatonic W-H | C-D-Eb-F-F#-G#-A-B | Dark supernatural, demonic | Kashchei, enchantments, underwater kingdoms |
| Octatonic H-W | C-Db-Eb-E-F#-G-A-Bb | Brighter supernatural, fairy-like | Snow Maiden's magic, forest spirits |
| Three transpositions only | OCT(0,1), OCT(0,2), OCT(1,2) | Each has unique color | Different transpositions for different magical characters |

### Octatonic Chord Pairs

The octatonic scale contains major triads a tritone apart — these simultaneous or alternating triads create the "magical" harmonic sound.

| Triad Pair | Within OCT(0,1) | Effect |
|-----------|-----------------|--------|
| C major + F# major | C-E-G + F#-A#-C# | Two keys at once; neither dominates |
| Eb major + A major | Eb-G-Bb + A-C#-E | Shimmering ambiguity |
| D minor + Ab minor | D-F-A + Ab-Cb-Eb | Dark supernatural |

```abc
X:1
T:Rimsky-Korsakov Octatonic Harmony — Magic Scene Character
M:4/4
L:1/4
K:C
%% Octatonic on C (W-H): C-D-Eb-F-F#-G#-A-B
!pp![CEG] [^F^AB]|[_EG_B] [AC^E]|[CEG]2|
%% C major and F# major alternate — the "magic" sound
%% Neither chord resolves; they shimmer between two tonal centers
```

## Real vs. Magic — The Harmonic Dramaturgy

| World | Harmonic Language | Scale Type | Example |
|-------|------------------|------------|---------|
| Human/real | Diatonic major/minor; folk modes; functional harmony | Major, minor, Dorian, Aeolian | Snow Maiden's human characters; Scheherazade's Sultan |
| Supernatural/magic | Octatonic; tritone pairs; non-functional | Octatonic (W-H or H-W) | Snow Maiden herself; Sadko's Sea King; Kashchei |
| Nature/transition | Whole-tone fragments; pedal-based | Whole-tone | Sea shimmer (Sadko); forest scenes |
| Exotic/oriental | Harmonic minor; augmented 2nds; Phrygian | Arabic, Phrygian | Scheherazade's Arabian scenes; Capriccio espagnol |

```abc
X:2
T:Rimsky — "Real" World (diatonic folk melody + functional harmony)
M:3/4
L:1/8
K:G
%% Human character: warm, diatonic, folk-like
!mf!G2 A2 B2|c2 B2 A2|G2 F2 G2|G6|
%% Major key; stepwise; folk contour; the "real" world sounds normal
```

```abc
X:3
T:Rimsky — "Magic" World (octatonic, same melody transformed)
M:3/4
L:1/8
K:C
%% Supernatural character: the melody shifts to octatonic
!pp!C2 D2 _E2|^F2 _E2 D2|C2 B,2 C2|C6|
%% Same contour, but octatonic pitches; the "magic" world glitters
```

## Exotic Modal Harmony — The Oriental Color

| Scale | Pitches (on A) | Character | Where Used |
|-------|---------------|-----------|------------|
| Harmonic minor | A-B-C-D-E-F-G#-A | Exotic tension; augmented 2nd (F-G#) | Scheherazade, Antar |
| Double harmonic | A-Bb-C#-D-E-F-G#-A | Maximum exoticism; two augmented 2nds | Scheherazade oriental scenes |
| Phrygian | E-F-G-A-B-C-D-E | Spanish/Eastern; dark intensity | Capriccio espagnol |
| Phrygian dominant | E-F-G#-A-B-C-D-E | Flamenco-like brilliance | Spanish Capriccio cadenzas |

```abc
X:4
T:Rimsky — Exotic Melody with Augmented 2nd (Scheherazade character)
M:4/4
L:1/16
K:Am
%% Harmonic minor: the augmented 2nd (F-G#) IS the exotic sound
!p!A2Bc d2cB A2FE F2^G2|A4 z4 A2Bc d2ef|
%% Ornamental, decorated, the solo violin spins the tale
```

## Harmonic Rhythm

| Context | Typical Rate | Character |
|---------|-------------|-----------|
| "Real" scenes | 1-2 chords/bar | Normal functional rhythm |
| "Magic" scenes | Static or oscillating | Octatonic shimmer; no functional movement |
| Sea/nature | Very slow (1 chord/4 bars) | Pedal-based; the sea breathes, not pulses |
| Oriental melody | Moderate, following melody | Harmony supports the melodic arabesque |
| Climactic tutti | Accelerating to cadence | Building to orchestral explosion |

## Cadential Patterns

| Cadence Type | Progression | World | Character |
|-------------|------------|-------|-----------|
| Standard PAC | V-I | Real | Human resolution; conventional |
| Octatonic dissolution | Tritone pair resolves outward | Magic | No cadence — the magic fades |
| Plagal (Russian) | IV-I or bVII-I | Real (folk) | Russian folk gravity |
| Phrygian half | iv6-V | Exotic | Spanish/oriental tension unresolved |
| Whole-tone fade | Whole-tone chord dissolving to silence | Nature | The sea recedes |
| Tritone resolution | F#-C resolution by semitone voice-leading | Magic-to-real | Enchantment broken; returning to human world |

## Key Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Bright, brilliant | A major, D major, E major | Orchestral showpieces, celebrations |
| Octatonic centers | C, F#, and their tritone pairs | Magic scenes |
| Folk/Russian | G major, D minor, A minor | Folk scenes, "real" characters |
| Exotic | A minor (harmonic), E Phrygian | Oriental melody, Scheherazade |
| Late chromatic | Remote keys, frequent modulation | Kashchei, Golden Cockerel |

## References

- [composition-guide.md](composition-guide.md) — Fingerprints #2 (octatonic), #3 (exotic modal color)
- [orchestration.md](orchestration.md) — Harmonic color linked to orchestral timbre
- [formal-approach.md](formal-approach.md) — How "real vs. magic" organizes opera structure
- [../../nationalistic-harmony.md](../../nationalistic-harmony.md) — Shared nationalistic harmonic vocabulary
- [cross-references.md](cross-references.md) — Octatonic legacy in Stravinsky and Scriabin
