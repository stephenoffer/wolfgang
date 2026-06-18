# Figuration Patterns — Turning Chords Into Music

> **WMN note:** ABC examples below are for reference and analysis. For composition output, use WMN phrase-level JSON with pattern keywords (see `wmn-format-spec.md`). The mapping: Alberti → `alberti`, arpeggios → `flowing_arpeggio` or `broken_chord`, tremolo → `tremolo`, walking bass → `walking`, block chords → `chorale` or `driving`, ostinato → `ostinato`, dialogue → `dialogue`.

The bridge between a harmony plan (chord symbols) and flowing composed music. Every chord should typically be REALIZED as a figuration — block chords are reserved for deliberate effect (hymn, chorale, climax, dramatic punctuation).

> **Important framing:** Pattern variety is generally desirable, but sustained repetition of a single figuration is equally valid when it serves the music. Chopin's Prelude No. 15 sustains one repeated-note pattern throughout; Ravel's *Boléro* maintains its ostinato for the entire piece; Beethoven's "Waldstein" opens with relentless repeated chords. The question is always whether the choice is intentional.

## 1. The Figuration Catalog

Base chord: C major (C-E-G). All examples in `L:1/16` (sixteenth notes) unless otherwise noted.

| # | Name | ABC Pattern | Period/Style | Tempo | Character |
|---|------|-------------|-------------|-------|-----------|
| 1 | Alberti bass | `C,G,EG,` | Classical (Mozart, Haydn) | Moderate (100-140) | Graceful, flowing, elegant |
| 2 | Ascending arpeggio | `C,EGc` | All periods; Romantic esp. | Any | Rising energy, openness, aspiration |
| 3 | Descending arpeggio | `cGEC,` | All periods; Romantic esp. | Any | Falling, sighing, resolution, descent |
| 4 | Murky bass (octave alternation) | `C,CC,C` | Early Classical, Galant | Moderate (80-120) | Solid, grounded, simple support |
| 5 | Waltz bass (3/4, L:1/8) | `C,4 [EG]2 [EG]2` | Romantic (Chopin, Strauss) | Waltz tempo (120-180) | Dance-like, lilting, elegant |
| 6 | Rachmaninoff wide-span | `C,,G,CEGce` | Late Romantic | Slow-moderate (60-100) | Expansive, passionate, sweeping |
| 7 | Turn-based | `CDCB,CEDC` | Classical, Baroque | Moderate (100-140) | Ornamental, playful, decorative |
| 8 | Scalar fill ascending | `C,DEFGABc` | All periods | Moderate-fast (100-160) | Building, forward motion, urgency |
| 9 | Scalar fill descending | `cBAGFEDC,` | All periods | Moderate-fast (100-160) | Releasing, calming, closing |
| 10 | Tremolo | `C,G,C,G,C,G,C,G,` | Romantic, orchestral | Any | Tension, suspense, sustained energy |
| 11 | Broken octave with fill | `C,CEC,CEC,CE` | Classical, early Romantic | Moderate (100-140) | Busy, perpetual motion, industrious |
| 12 | Chordal with passing tones | `[CE]2[DF]2[EG]2[FA]2` | Romantic, choral style | Slow-moderate (60-110) | Hymn-like, rich, warm, broadening |

### Choosing a Figuration

| If the music needs... | Use figurations # |
|-----------------------|-------------------|
| Grace and elegance | 1, 5, 7 |
| Building energy | 2, 8, 10 |
| Winding down | 3, 9, 12 |
| Rhythmic drive | 4, 10, 11 |
| Lyrical expansion | 5, 6, 12 |
| Virtuosic display | 6, 8, 9, 11 |
| Climactic density | 10, 12, 6 |
| Simple support (stay out of melody's way) | 1, 4, 5 |

---

## 2. Four-Chord Progression Realized 6 Ways

Progression: **I - IV - V - I** in C major, 4 bars, each chord = 1 bar.

### Style 1: Classical Alberti (Mozart)

```abc
X:1
T:I-IV-V-I Classical Alberti
M:4/4
L:1/16
K:C
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
[V:RH] E2G2c2G2 E2G2c2G2 | F2A2c2A2 F2A2c2A2 | D2G2B2G2 D2G2B2G2 | E2G2c2G2 E2G2c4 |
[V:LH] C,4 z4 C,4 z4 | F,4 z4 F,4 z4 | G,4 z4 G,4 z4 | C,4 z4 C,8 |
```

### Style 2: Beethoven Driving (repeated chords + bass octaves)

```abc
X:1
T:I-IV-V-I Beethoven Driving
M:4/4
L:1/8
K:C
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
[V:RH] !f! [CEG]2 [CEG]2 [CEG]2 [CEG]2 | [CFA]2 [CFA]2 [CFA]2 [CFA]2 | [BDG]2 [BDG]2 [BDG]2 [BDG]2 | !ff! [CEG]2 [CEG]2 [CEG]4 |
[V:LH] C,C C,C C,C C,C | F,F F,F F,F F,F | G,G G,G G,G G,G | C,C C,C C,4 |
```

### Style 3: Chopin Nocturne (wide-span LH arpeggios)

```abc
X:1
T:I-IV-V-I Chopin Nocturne
M:4/4
L:1/16
K:C
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
[V:RH] !p! z4 e4 g2a2 g2e2 | z4 f4 a2b2 a2f2 | z4 d4 g2a2 g2f2 | !pp! z4 e4 g2e2 c4 |
[V:LH] C,2G,2E2G,2 C,2G,2E2G,2 | F,2C2A2C2 F,2C2A2C2 | G,2D2B2D2 G,2D2B2D2 | C,2G,2E2G,2 C,2G,2E2c2 |
```

### Style 4: Rachmaninoff (separated bass + rolling chords)

```abc
X:1
T:I-IV-V-I Rachmaninoff
M:4/4
L:1/16
K:C
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
[V:RH] !mf! z4 [EG]2[ce]2 z2[EG]2 [ce]4 | z4 [FA]2[cf]2 z2[FA]2 [cf]4 | z4 [DG]2[Bd]2 z2[DG]2 [Bd]4 | !f! z4 [EG]2[ce]2 z2[EG]2 [ce]4 |
[V:LH] C,,4 z4 C,4 z4 | F,,4 z4 F,4 z4 | G,,4 z4 G,4 z4 | C,,4 z4 C,8 |
```

### Style 5: Brahms (interleaving hands, cross-rhythm)

```abc
X:1
T:I-IV-V-I Brahms Interleaving
M:4/4
L:1/8
K:C
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
[V:RH] !mf! (3EGc (3GcE (3cEG (3EGc | (3FAc (3AcF (3cFA (3FAc | (3DGB (3GBD (3BDG (3DGB | (3EGc (3GcE [ce]4 |
[V:LH] C,2 [E,G,]2 C,2 [E,G,]2 | F,2 [A,C]2 F,2 [A,C]2 | G,2 [B,D]2 G,2 [B,D]2 | C,2 [E,G,]2 C,4 |
```

### Style 6: Orchestral Reduction (tremolo strings + sustained winds)

```abc
X:1
T:I-IV-V-I Orchestral Reduction
M:4/4
L:1/16
K:C
V:RH clef=treble name="Winds/Upper Strings"
V:LH clef=bass name="Lower Strings"
%
[V:RH] !f! [EGc]16- | [FAc]16- | [DGB]16- | [EGc]16 |
[V:LH] C,G,C,G, C,G,C,G, C,G,C,G, C,G,C,G, | F,C F,C F,C F,C F,C F,C F,C F,C | G,DG,D G,DG,D G,DG,D G,DG,D | C,G,C,G, C,G,C,G, C,G,C,G, C,8 |
```

---

## 3. Figuration Variation Within a Section

Demonstrates changing the accompaniment pattern every 4 bars while keeping the SAME harmony. Progression: I - vi - IV - V (repeated), C major, melody above.

### Bars 1-4: Alberti Pattern Under Melody

```abc
X:1
T:Figuration Variation Example
M:4/4
L:1/16
K:C
V:RH clef=treble name="Melody"
V:LH clef=bass name="Accompaniment"
%
[V:RH] !mf! e4 d2c2 d4 e4 | f4 e2d2 e4 c4 | A4 B2c2 d4 c4 | B4 c2d2 B4 G4 |
[V:LH] C,G,EG, C,G,EG, C,G,EG, C,G,EG, | A,,E,CE, A,,E,CE, A,,E,CE, A,,E,CE, | F,C AF,C AF,C A F,C AF,C A | G,D BG,D B G,D BG,D B |
```

### Bars 5-8: Bass-Chord Pattern (DIFFERENT texture, same harmony)

```abc
[V:RH] !crescendo(! e4 d2c2 d4 e4 | f4 e2d2 e4 !crescendo)! c4 | !f! A4 B2c2 d4 c4 | B4 c2d2 B4 G4 |
[V:LH] C,4 [EG]4 C,4 [EG]4 | A,,4 [CE]4 A,,4 [CE]4 | F,4 [AC]4 F,4 [AC]4 | G,4 [BD]4 G,4 [BD]4 |
```

The listener hears the same melody and harmony but the texture shifts from flowing Alberti to punctuated bass-chord, creating interest and forward motion without changing the harmonic plan.

**Variation strategies for longer sections (consider rotating every 4 bars or so):**

| Bars | LH Pattern | Effect |
|------|-----------|--------|
| 1-4 | Alberti | Flowing, classical |
| 5-8 | Bass-chord | Grounded, punctuated |
| 9-12 | Wide arpeggio | Romantic, expansive |
| 13-16 | Tremolo | Tension building |
| 17-20 | Scalar fill | Virtuosic energy |
| 21-24 | Waltz bass | Dance-like relief |

---

## 4. Figuration for Climax Building

Shows how to increase textural density through figuration changes over 8 bars, from pp to fff.

Chord progression: i - iv - V - i - VI - iv - V7 - i (D minor)

```abc
X:1
T:Climax Building Through Figuration
M:4/4
L:1/16
K:Dm
V:RH clef=treble name="Right Hand"
V:LH clef=bass name="Left Hand"
%
%%% Bar 1 — pp: Simple arpeggios, wide spacing
[V:RH] !pp! d4 c2A2 d4 f4 |
[V:LH] D,2A,2D2A,2 D,2A,2D2A,2 |
%%% Bar 2 — pp→p: Add bass octave doubling
[V:RH] !crescendo(! g4 f2e2 f4 d4 |
[V:LH] G,2G2_B2G2 G,4 [G,_B,D]4 |
%%% Bar 3 — mp: Figurations become sixteenths, more active
[V:RH] !mp! A2^c2d2e2 f2e2d2^c2 |
[V:LH] A,E^CE A,E^CE A,E^CE A,E^CE |
%%% Bar 4 — mf: Inner voice movement, thickening
[V:RH] !mf! [Dd]4 [CA]2[DF]2 [DA]4 [Dd]4 |
[V:LH] D,2A,2D2F2 A,2D2F2A2 |
%%% Bar 5 — f: Both hands more active, chordal enrichment
[V:RH] !f! [_Bdf]4 [Ace]2[_Bdf]2 [ceg]4 [_Bdf]4 |
[V:LH] _B,,2F,2_B,2D2 F,2_B,2D2F2 |
%%% Bar 6 — f→ff: Rapid figurations with melodic interest
[V:RH] !crescendo)! [GAd]2[FA^c]2 [GAd]2[Ace]2 [_Bdf]2[Ace]2 [GAd]2[FA^c]2 |
[V:LH] G,2D2G2_B2 G,DG_B G,DG_B |
%%% Bar 7 — ff: Full chordal texture, rhythmic unison approach
[V:RH] !ff! [A^ceg]4 [A^ceg]4 [A^ceg]2[Gd_bf]2 [A^ceg]4 |
[V:LH] A,,2A,2E2^C2 A,,2E,2A,2^C2 |
%%% Bar 8 — fff: Maximum spread, cascading resolution
[V:RH] !fff! d2/f/a/d'/ [fad']4 z2 !sfz! [DFAd]8 |
[V:LH] D,,2/A,,/D,/F,/ [D,A,D]4 z2 [D,,D,]8 |
```

### Climax Building Reference Table

| Dynamic | Texture | Figurations to Use | Register Span | Rhythmic Density |
|---------|---------|-------------------|---------------|-----------------|
| pp | Single line or simple arpeggio | #2, #3 (slow) | 1-2 octaves | Quarter/eighth notes |
| p | Arpeggio + bass octave doubling | #2, #3, #4 | 2 octaves | Eighth notes |
| mp | Active figurations, passing tones | #1, #7, #8 | 2-3 octaves | Sixteenth notes begin |
| mf | Inner voices added, chordal thickening | #11, #12 | 2-3 octaves | Sixteenth notes |
| f | Both hands active, enriched melody | #6, #8, #12 | 3-4 octaves | Sixteenth notes throughout |
| ff | Rhythmic unison chords or cascading arpeggios | #6, #10, #12 | 4+ octaves | Dense sixteenths or heavy chords |
| fff | Maximum spread, tremolo, full voicing | #6, #10 + chordal | 5+ octaves | Maximum density or massive chords |

### Guidelines for Climax Building

1. **Typically avoid skipping more than one dynamic level** — go p→mp→mf, not p→ff (though sudden dynamic leaps are effective for shock or surprise)
2. **Each dynamic level should ideally add something new**: a voice, a register, rhythmic activity, or harmonic density
3. **The peak (fff) is most effective when it uses a figuration that has NOT appeared in the section yet** — novelty reinforces climax
4. **After the peak, consider de-escalating**: reverse the process in 2-4 bars, removing layers
5. **Register expansion typically tracks dynamics**: louder = wider register span between bass and treble
