# Mozart — Composition Guide

## Fingerprints
Any section claiming Mozart's style needs ≥3 of these 5 present.

1. **Vocal thinking in instrumental writing** — Every melody could be sung. The line breathes naturally, has an identifiable phrase shape (rise → peak → cadential fall), and never asks the instrument to do something a good singer couldn't do. The phrase IS a vocal utterance.
2. **Chromatic inflection for emotional nuance** — A single chromatic note (lowered 6th, raised 4th, Neapolitan chord) colors the emotional temperature of the phrase. Not a modulation — one note reveals everything.
3. **Transparent, chamber-like texture** — Each instrument's role is distinct. Mozart thins deliberately, letting single instruments emerge.
4. **Symmetrical phrase structure subverted at one moment** — 4-bar phrases balance each other, but once per section a phrase extends (4+4 becomes 4+5) or elides. This surprise makes the symmetry around it more satisfying.
5. **Minor-mode shadow in major contexts** — A sudden shift to parallel minor that passes like a cloud. The return to major feels like relief.

---

## Corpus-Derived Texture Rules (6,987 bars, 18 sonatas, 69 movements)

### Left Hand Texture Distribution
| LH Pattern | % of bars | Guideline |
|------------|-----------|-----------|
| alberti | 19.4% | Only 1 in 5 bars — NOT the default! Max 2-3 consecutive bars. |
| bass_melody | 15.1% | Nearly as common as Alberti. Use for dialogue, development, transitions. |
| block_chord_sparse | 11.1% | Dramatic emphasis, forte passages, Sturm und Drang. |
| pedal_point | 6.6% | Dominant pedals in development, tonic pedals in codas. |
| sparse_punctuation | 6.4% | Textural breathing — let the RH speak alone. |
| walking_bass | 5.5% | Chromatic passages, transitions, development counterpoint. |
| block_chord_offbeat | 4.3% | Syncopated energy, dance-like passages. |
| silence | 3.9% | The music MUST breathe. Nearly 4% of bars have LH silent. |
| broken_chord_wave | 3.6% | Expressive arpeggiation, lyric second themes. |

**Rule: DO NOT use Alberti bass for more than 2-3 consecutive bars.** Mozart's REAL LH rotates through: Alberti (19%), bass melody (15%), block chords (11%), pedal points (7%), walking bass (6%), silence (4%). Vary LH texture every 2-4 bars.

### Right Hand Texture Distribution
| RH Texture | % of bars |
|------------|-----------|
| singing_melody | 45.1% |
| scalar_run | 16.9% |
| zigzag_figuration | 12.8% |
| chordal | 8.6% |
| passage_work | 3.5% |
| dotted_pairs | 2.1% |
| ornamental_cascade | 1.8% |
| held_note | 1.6% |
| stammer_repeat | 1.4% |

### Top Texture Combinations (RH + LH)
| Combination | % of bars | Notes |
|-------------|-----------|-------|
| singing_melody + alberti | 9.3% | The stereotype — but only 9%! |
| singing_melody + bass_melody | 7.7% | Nearly as common as the stereotype. |
| singing_melody + block_chord_sparse | 5.1% | Dramatic lyric passages. |
| scalar_run + alberti | 4.3% | Passage work over Alberti — transitional. |
| singing_melody + pedal_point | 3.2% | Pedal-grounded lyric themes. |
| singing_melody + walking_bass | 2.2% | Contrapuntal lyric writing. |

### Melody Density Targets by Movement Type
| Movement Type | Events/bar (RH) | Events/bar (LH) |
|---------------|-----------------|-----------------|
| Adagio/Andante | 3-6 | 3-5 |
| Allegretto/Moderato | 6-8 | 4-6 |
| Allegro | 8-13 | 5-8 |
| Corpus average | 6.9 | 5.2 |

---

## Building the Mozart Period — Note by Note

The fundamental unit is the **8-bar period**: antecedent (4 bars, HC ending) + consequent (4 bars, PAC ending). The consequent's last bar is the PAC. Everything in a Mozart section is either a period, a variation of it, or connective tissue between periods.

### The Antecedent Phrase (bars 1–4)

**Bar 1**: State the opening gesture. It should have an identifiable character — a direction (rising or falling), a rhythm (dotted, even, or syncopated), and a starting interval. The first 3 notes are the phrase's DNA.

**Bar 2**: Respond to bar 1. If bar 1 rose, bar 2 may fall or continue rising. If bar 1 stated a leaping gesture, bar 2 fills it in with stepwise motion.

**Bar 3**: Begin the harmonic approach to the half cadence. The melody typically rises toward the dominant.

**Bar 4**: Half cadence. The melody lands on the 2nd scale degree (or 5th). The phrase is open — it wants to continue.

**Antecedent in G major (8/4 = 4 quarter notes per bar):**
```json
{"bar_num": 1, "voices": {
  "soprano": [
    {"p": "G4", "d": "q", "dyn": "p"},
    {"p": "A4", "d": "q"},
    {"p": "B4", "d": "q"},
    {"p": "C5", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "G2", "chord_tones": ["D3","B3","G3"]}
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "D5", "d": "h"},
    {"p": "C5", "d": "q"},
    {"p": "B4", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "G2", "chord_tones": ["D3","B3","G3"]}
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "C5", "d": "q"},
    {"p": "D5", "d": "q"},
    {"p": "E5", "d": "q"},
    {"p": "F#5","d": "q", "orn": "grace:G5"}
  ],
  "bass": {"formula": "alberti", "bass": "D2", "chord_tones": ["F#3","A3","D4"]}
}},
{"bar_num": 4, "_feel": "Half cadence — open, asking, not yet home.", "voices": {
  "soprano": [
    {"p": "G5", "d": "h", "dyn": "mf"},
    {"p": "F#5","d": "q", "orn": "trill"},
    {"p": "E5", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "D2", "chord_tones": ["A3","F#3","D3"]}
}}
```
Bar 1: G4 rising stepwise to C5 (ascending 4th). Bar 2: D5 holds, then falls (the peak of antecedent). Bar 3: rise toward dominant, F#5 with grace note. Bar 4: G5 peak, then F#5 with trill, descends to E5 — the HC arrival. LH: Alberti bass (Alberti pattern: root–top–mid–top). The melody rises over 4 bars, peaks at G5, then approaches the HC.

### The Consequent Phrase (bars 5–8)

The consequent begins identically to the antecedent but diverges at bar 7 to reach a perfect authentic cadence (PAC) in bar 8. The first 4 notes of bar 5 are the same as bar 1 — the listener recognizes the material, then hears it resolve differently.

**Consequent (G major, bars 5–8):**
```json
{"bar_num": 5, "voices": {
  "soprano": [
    {"p": "G4", "d": "q", "dyn": "p"},
    {"p": "A4", "d": "q"},
    {"p": "B4", "d": "q"},
    {"p": "C5", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "G2", "chord_tones": ["D3","B3","G3"]}
}},
{"bar_num": 6, "voices": {
  "soprano": [
    {"p": "D5", "d": "h"},
    {"p": "C5", "d": "q"},
    {"p": "B4", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "G2", "chord_tones": ["D3","B3","G3"]}
}},
{"bar_num": 7, "_feel": "Now the phrase goes somewhere different — toward the PAC instead of the HC.", "voices": {
  "soprano": [
    {"p": "Eb5","d": "q", "dyn": "mf"},
    {"p": "D5", "d": "q"},
    {"p": "C5", "d": "q"},
    {"p": "B4", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","E3","C3"]}
}},
{"bar_num": 8, "_feel": "PAC — home, complete, resolved.", "voices": {
  "soprano": [
    {"p": "A4", "d": "q"},
    {"p": "B4", "d": "q", "orn": "grace:C5"},
    {"p": "D5", "d": "q"},
    {"p": "G4", "d": "q", "orn": "trill"}
  ],
  "bass": {"formula": "alberti", "bass": "D2", "chord_tones": ["A3","F#3","D3"]}
}}
```
Bar 5–6 = bars 1–2 literally. Bar 7 = DIVERGENCE: Eb5 appears (the minor shadow, the lowered 6th of G major — Mozart's chromatic inflection). Then descending through D5–C5–B4 to approach the cadence from above. Bar 8: PAC — trill on G4, then the phrase closes. The Eb5 in bar 7 is the ONE chromatic note that makes this phrase Mozart and not a student exercise.

---

## The Mozart Shadow (minor inflection)

Bar 7 in the example above contains Eb5 — the flattened 6th of G major. This note implies G minor for one beat. It passes through and resolves, but its presence changes the emotional temperature of the entire phrase. Without it: the period is pleasant and empty. With it: the period is human.

**Where the shadow goes:**
- Minor 6th (b6) in a major-key phrase: the darkest, most Mozartian inflection
- Neapolitan (bII6) in slow movements: a long shadow, dwelt on
- Diminished 7th in transitions: the passage through darkness before re-arriving in light

---

## Anti-patterns

- **Thick, heavy textures.** Mozart's music breathes. Four instruments all forte simultaneously is Beethoven, not Mozart.
- **Dramatic gestures in early positions.** Mozart's ff outburst in bar 3 is wrong. It belongs at bar 16, where it's proportionate.
- **Melody without vocal shape.** If a singer couldn't make sense of it, it's not Mozart.
- **No chromatic inflection.** Completely diatonic Mozart is flavorless. One expressive chromatic note per 8-bar period minimum (the minor shadow).
- **Both phrases ending identically.** The antecedent (HC) and consequent (PAC) must diverge at bar 7. If they don't, there's no period — just two identical 4-bar phrases.

---

## Data-Driven Findings (from 69-movement corpus analysis, March 2026)

### LH Accompaniment Pattern Distribution (across 2,159 bars, 10 sonatas)
| Pattern | % of bars | When to use |
|---------|-----------|-------------|
| Broken chord | 28.9% | Expressive passages, transitions, 2nd themes |
| Alberti | 22.1% | Lyrical passages, galant style, default for moderate tempo |
| Block chord | 21.7% | Dramatic emphasis, forte arrivals, Sturm und Drang |
| Sparse/octaves | 6.1% | Slow movements, textural gasps, after climaxes |
| Walking bass | 4.7% | Development sections, transitions, chromatic passages |
| Oscillation | 0.4% | K.310-specific: development counterpoint, anxiety |

**Implication**: Block chord tremolo is NOT the default — it's only 22% of bars. Broken chord (29%) and Alberti (22%) are equally common. Vary the LH pattern across sections.

### Ornament Rates (corpus-wide)
- Grace notes: 0.254/bar average (range 0.01-0.90). Apply at phrase entries and before cadences.
- Dotted rhythms: 0.60/bar average. K.310 is highest at 0.79/bar.
- Cadential trills: appear in 8/10 sonatas at major structural cadences.

### Harmonic Vocabulary (across 9,908 vertical sonorities)
| Chord quality | % | Notes |
|---------------|---|-------|
| Major triads | 25.8% | Tonic and dominant areas |
| Minor triads | 20.6% | Subdominant, relative minor |
| Diminished | 2.2% | Leading-tone chords, viio7 pivots |
| Augmented | 0.3% | Rare — save for special moments |

### Cadence Distribution (693 cadences across corpus)
| Cadence | % | Usage |
|---------|---|-------|
| Half cadence | 20.6% | Antecedent endings, mid-phrase pauses |
| IAC | 14.0% | Weaker phrase closings |
| PAC | 9.7% | Strong period endings, section closings |
| Plagal | 3.5% | Codas, "amen" closings |
| Deceptive | 1.4% | Phrase extensions — rare but powerful |

**Implication**: Half cadences are the MOST common cadence type — Mozart leaves phrases open more often than he closes them. Deceptive cadences are rare (1.4%) — use sparingly for maximum impact.

### Minor-Key Sonata Targets (K.310 + K.457)
- Chromatic %: 15-35% (higher in development)
- Events/bar: 10-20 (fast movements), 15-25 (slow movements)
- RH parallel 3rds: ~0.5-1.0 per bar in dialogue passages
- Rest ratio: 10-15% — the music MUST breathe
- Phrase length: 8-15 beats average (NOT 20+)

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #10: Alberti Bass (exactly how to write the LH pattern with chord_tones)
- Technique #11: Parallel Thirds (how to harmonize the melody in 3rds for vln2)
- Technique #13: Cadential 6/4 → V → I (Mozart's standard phrase closure formula)
- Technique #7: Neapolitan Approach (for slow movements and moments of maximum tenderness)
