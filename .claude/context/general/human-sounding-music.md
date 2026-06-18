# Human-Sounding Music — Avoiding AI Tells

> Updated with v4 corpus findings from 6,987 Mozart bars (69 movements), 10-sonata deep study, and unified gesture analysis. All guidance is flexible — art, not rules.

## The Core Principle

Music is not assembled from independent dimensions (melody + harmony + rhythm + texture). It is a **single integrated fabric** where every element responds to every other. A melody's rhythm IS its harmony's rhythm. A texture change IS a harmonic event. The #1 AI tell is treating these as separate layers stacked on top of each other.

### Unified Gestures (from v4 corpus analysis)
A real bar is ONE gesture where both hands work together. The 20 unified gesture types include:
- `held_melody_over_bass` (6.5%): RH holds long notes (h, dh), LH has bass melody — only 1-3 RH events!
- `arpeggio_as_melody` (9.9%): RH arpeggio IS the theme — not just accompaniment
- `parallel_hands` (6.0%): both hands move together in the same rhythm and direction
- `silence_lh_only` (3.9%): LH completely empty — dramatic silence
- `grace_cluster_launch` (2%): grace notes cluster then held note — dramatic opening
- `stammer_repeat` (1%): same note repeated 3x with changing LH chords

Real Mozart uses ALL 20 gesture types. The typical AI composition uses only 2-3.

---

## AI Music Tells (Ranked by Detectability)

### Tell #1: Flat Density (same events/bar throughout)
Real music breathes — dense passages alternate with sparse ones. A piece at constant 8 events/bar sounds mechanical.
- **Fix:** Manage a density arc: sparse at boundaries, dense at climaxes, breathing room between intense passages
- **Metric:** Density coefficient of variation should be > 0.5

### Tell #2: Repetitive Accompaniment (same LH pattern every bar)
Real accompaniment responds to the melody — simplifies at peaks, fills during rests, changes pattern every 4-8 bars.
- **Fix:** Use at least 5 distinct LH patterns per piece. Change pattern at every phrase boundary.
- **Metric:** LH unique patterns / total bars > 0.6

### Tell #3: No Inner Voice (only melody + bass)
Real piano writing has 3-6 simultaneous voices. The middle voices provide harmonic color.
- **Fix:** Add sustained inner voices. Use chords in RH (melody on top, chord tones below).
- **Metric:** Chord percentage > 20% for piano writing

### Tell #4: Stale Harmony (oscillating between 2 chords)
Real harmony progresses — ii→V→I, deceptive cadences, walking bass, circle of 5ths.
- **Fix:** Minimum 4 distinct bass roots per 8-bar phrase. Cadential preparation (ii→V→I or cad 6/4→V7→I).
- **Metric:** Distinct bass roots / bars > 0.3

### Tell #5: No Appoggiaturas or Suspensions
Real melody leans into chord tones through non-chord tones on strong beats. Clean chord tones on every beat = arpeggiated accompaniment, not melody.
- **Fix:** Add at least 1 appoggiatura or suspension per 8-bar phrase.

### Tell #6: Monotonous Melody Direction
Real melody changes direction 1-2x per bar. A melody that descends for 4 bars without changing direction sounds like a scale exercise.
- **Fix:** After 3 notes in one direction, step back or leap the other way.
- **Metric:** Direction changes per bar > 0.8

### Tell #7: No Texture Evolution
Real pieces evolve texture across sections. The same texture from start to finish = one long section.
- **Fix:** Plan a voice-count arc: 2→3→4→6→8→6→4→2→1 across the piece.

### Tell #8: Missing Expression (no dynamics, slurs, tempo)
Real music has pp→ff arcs, slurs over phrases, tempo changes at section boundaries.
- **Fix:** Minimum 1 dynamic marking per 8 bars, 1 slur per phrase, tempo markings at section boundaries.

### Tell #9: Wrong Enharmonic Spelling
G# in Eb minor = wrong. Ab = correct. The key signature determines spelling.
- **Fix:** Use flat spellings for flat keys (Eb, Bb, Ab, Db, Gb, Cb). Never create notes from MIDI integers — use pitch name strings.

### Tell #10: Mechanical Rhythm (all even note values)
Real music mixes durations: quarters, dotted quarters, eighths, sixteenths, triplets, tied notes.
- **Fix:** Minimum 6 distinct note durations used across the piece.
- **Metric:** Rhythmic variety >= 6

---

## Quantitative Discriminator Checklist

| Metric | Target | Range | What it catches |
|--------|--------|-------|-----------------|
| Events per bar | 10-12 | 6-18 | Skeletal writing |
| RH events/bar | 5-7 | 3-12 | Thin melody |
| LH events/bar | 5-6 | 3-10 | Missing accompaniment |
| Rest ratio | 5-10% | 3-15% | Too empty |
| Stepwise motion | 35-50% | 25-60% | Too many leaps |
| Direction changes/bar | 1.0-2.0 | 0.8-2.5 | Monotonous melody |
| Bass change rate | 2.0-3.0 | 1.5-3.5 | Static harmony |
| Chord percentage | 25-40% | 15-50% | Missing inner voices |
| Rhythmic variety | 8-10 | 6-12 | Mechanical rhythm |
| Triplet percentage | 1-5% | 0-10% | Missing texture |

---

## Texture Architecture

### The Voice-Count Arc
Plan how many simultaneous voices are active at each section boundary:

```
Opening:        2 voices (melody + bass, or just melody)
Theme entry:    3 voices (add inner voice or accompaniment)
Development:    4-6 voices (add counter-melody, thicken chords)
Climax:         6-8 voices (full chords both hands)
Aftermath:      3-4 voices (stripping back)
Return:         3 voices (thinner than original)
Coda:           2→1→0 voices (dissolving)
```

### RH Texture Types (from corpus analysis, 16,812 bars)

| Texture | Frequency | Description | When to use |
|---------|-----------|-------------|-------------|
| singing_melody | 37.7% | Quarter/half notes, vocal shape | Theme statements |
| chordal | 17.5% | 3-4 note chords on beats | Climaxes, block passages |
| zigzag_figuration | 10.4% | Broken 3rd/6th alternation | Flowing passages |
| passage_work | 9.1% | Mixed sixteenths | Development, virtuosic |
| scalar_run | 6.6% | Stepwise sixteenths | Transitions, cascades |
| held_note | 4.3% | Sustained half/whole | Sparse moments |
| dialogue_chords | 3.5% | Dyads with rests | Call-and-response |
| dotted_pairs | 3.4% | Dotted-eighth + sixteenth | French overture, dramatic |
| ornamental_cascade | 2.1% | Rapid grace-note runs | Before climaxes |
| stammer_repeat | 0.7% | Repeated note + neighbor | Agitated |

### LH Texture Types

| Texture | Frequency | Description | When to use |
|---------|-----------|-------------|-------------|
| bass_melody | 15.3% | Independent melodic bass | Counter-melody |
| alberti | 14.9% | Low-high-mid-high broken chord | Classical accompaniment |
| block_chord_sparse | 13.2% | Chords on beats 1 and 3 | Punctuation |
| pedal_point | 7.0% | Sustained/repeated single note | Dominant preparation |
| walking_bass | 5.4% | Stepwise bass quarters | Baroque-influenced |
| broken_chord_wave | 4.7% | Up-down rocking arpeggio | Flowing accompaniment |
| broken_chord_descending | 3.3% | Downward arpeggio | Cadential approaches |
| broken_chord_ascending | 2.9% | Upward arpeggio | Building passages |
| block_chord_offbeat | 2.7% | Chords on 2-3-4 | Syncopated |
| oscillation_trill | 2.4% | Two-note tremolo | Sustained tension |
| block_chord_tremolo | 1.4% | Rapid repeated chords | Storm/fury |

### Top Texture Combinations (what actually appears in Beethoven)

| RH + LH | % | Character |
|----------|---|-----------|
| singing_melody + bass_melody | 7.6% | Two independent melodies |
| singing_melody + block_chord_sparse | 4.5% | Melody over chordal punctuation |
| singing_melody + alberti | 4.3% | Classic piano sonata texture |
| chordal + alberti | 3.7% | Thick RH over flowing LH |
| singing_melody + pedal_point | 3.0% | Melody over sustained bass |
| singing_melody + walking_bass | 2.6% | Melody over stepwise bass |
| passage_work + alberti | 2.1% | Virtuosic over flowing |

---

## Harmonic Authenticity

### Bass Motion Rules
1. **Walk between chord roots** — Don't jump. If moving from Ebm to Abm, the bass should step: Eb→F→Gb→Ab (not Eb→Ab)
2. **Common tones** — Keep shared notes between chords in the same voice
3. **Cadential preparation** — Every phrase ending needs ii→V→I or cad 6/4→V7→I
4. **Harmonic rhythm acceleration** — Chords change slowly at phrase start (1/bar), faster toward cadence (2-4/bar)
5. **Deceptive cadences** — Use V→vi to extend phrases (don't always resolve V→I)

### Most Common 4-Bar Bass Progressions (from corpus)
1. R→R→R→R (static — 20%): Pedal point, sustained section
2. R→4→4→4 (subdominant area): Moving to iv
3. R→5→5→5 (dominant area): Building toward cadence
4. R→R→R→5 (late dominant): Delaying the move
5. R→b6→b6→b6 (flat submediant): Beethoven's signature shadow chord

---

## Playability Constraints (Piano)

| Constraint | Limit | Why |
|-----------|-------|-----|
| Chord span (one hand) | ≤ 15 semitones (10th) | Average adult hand span |
| Notes per chord | ≤ 5 | Five fingers per hand |
| Consecutive large leaps | ≤ 2 (octave+5th) | Hand repositioning time |
| Register | A0 (21) to C8 (108) | Standard piano range |
| Speed | ≤ 12 notes/beat at Allegro | Physical limitation |
| Cross-hand | RH above LH (usually) | Arm collision |

### Common Voicing Fixes
- Chord too wide (>15 semitones): Move lowest note up an octave
- Too many notes: Remove doubled notes (keep root + 3rd + 7th)
- Hands crossing: Redistribute voices between staves

---

## Integration: How Elements Work Together

**Melody informs harmony:** The melody's climax note should coincide with the strongest harmonic arrival (V→I).

**Harmony informs texture:** When harmony changes, the accompaniment pattern should shift — at least change the arpeggio's chord tones.

**Rhythm informs density:** A dotted-rhythm theme needs SPACE around it (LH should simplify). An even-eighth melody can tolerate denser LH.

**Texture informs structure:** Texture changes MARK structural boundaries. The listener hears a section change when the texture changes, even if the key and melody stay the same.

**Dynamics inform all:** A pp passage needs thin texture (1-2 voices). An ff passage needs thick texture (6-8 voices). Don't write ff with 2 voices or pp with 8.

---

## The Critical Insight: Bar-Level Texture Variation

**Beethoven changes texture 58% of the time between consecutive bars.** Average texture run = 1.4 bars. Most common run length = 1 bar (137 instances in the Appassionata).

This is the single biggest difference between human and AI composition. AI holds the same texture for 8-20 bars. Beethoven holds it for 1-2 bars.

From Appassionata mvt 1 analysis:
```
m0:  singing_melody + walking_bass          ← changes
m1:  singing_melody + walking_bass          ← same
m2:  dotted_pairs + walking_bass            ← RH changes!
m3:  dotted_pairs + block_chord_sparse      ← LH changes!
m4:  singing_melody + sparse_punctuation    ← both change!
m5:  singing_melody + walking_bass          ← LH changes
m6:  dotted_pairs + bass_melody             ← both change
m7:  dotted_pairs + block_chord_sparse      ← LH changes
m8:  unclassified + sparse_punctuation      ← both change
```

Every 1-2 bars, something shifts. This constant micro-variation is what makes Beethoven sound alive.

### How to Achieve This

Use the **Texture Sequencer** (`tools/v3/texture_sequencer.py`) which generates bar-by-bar texture assignments using a Markov chain trained on the Beethoven corpus:

```python
from v3.texture_sequencer import TextureSequencer
seq = TextureSequencer('tools/texture_templates/beethoven_transition_model.json')
textures = seq.generate_sequence(n_bars=20, section_character='lyrical')
# Returns: [('singing_melody','alberti'), ('scalar_run','alberti'), ('singing_melody','bass_melody'), ...]
```

Then use the **Texture Retriever** (`tools/v3/texture_retriever.py`) to get actual Beethoven bar patterns for each assigned texture:

```python
from v3.texture_retriever import TextureRetriever
ret = TextureRetriever('tools/texture_templates/beethoven_piano.json')
for rh_tex, lh_tex in textures:
    templates = ret.search(rh_texture=rh_tex, lh_texture=lh_tex, target_key='Ebm')
    # Each template has real Beethoven pitches + durations, transposed to your key
```

### RH Melody: Single Notes, Not Chords

From corpus analysis, Beethoven's "singing_melody" bars have RH density 4-6 (single notes with ornaments). The LH provides all harmony via 8-12 event Alberti/broken chord patterns.

**WRONG (hymn):** `(Gb4+Db5):1.5 (Eb4+Gb4):0.5` — 3-note chords = organ
**RIGHT (piano):** `Db5:1.5 Gb4:0.5 Eb4:1.0` — single voice melody

Reserve chords for: climaxes (fff), octave doublings at peaks, cadential arrivals.

---

## Corpus-Derived Statistical Model (Beethoven 3/4, 1,154 bars)

Use `tools/texture_templates/beethoven_comprehensive_model.json` for exact numbers. Key findings:

### LH Rhythm Distribution (USE THIS, not just Alberti)
| Rhythm | Frequency | Description |
|--------|-----------|-------------|
| (1.0, 1.0, 1.0) | **17.0%** | Three quarters — MOST COMMON. Walking bass. |
| (0.5, 0.5, 0.5, 0.5, 0.5, 0.5) | 14.0% | Six eighths — Alberti/broken chord |
| (3.0,) | 7.5% | Held note — pedal point |
| (0.25 x 12) | 6.9% | Twelve sixteenths — rapid figuration |
| (0.333 x 9) | 4.7% | Nine triplet eighths — flowing |
| (2.0, 1.0) | 4.7% | Half + quarter |
| (0.5, 0.5, 0.5, 0.5, 1.0) | 2.2% | Four eighths + quarter |
| (1.0, 0.5, 0.5, 1.0) | 1.7% | Quarter-eighth-eighth-quarter |

**CRITICAL**: Alberti (6 eighths) is only 14% of Beethoven's LH in 3/4. Quarters (17%) are MORE common. Use weighted random selection from this distribution.

### Most Common 4-Bar Harmonic Progressions
| Progression | Count | Musical meaning |
|------------|-------|-----------------|
| R→R→R→R | 96 | Static/pedal (20%) |
| R→4→4→4 | 18 | Move to subdominant |
| R→R→R→5 | 15 | Late dominant arrival |
| R→5→5→5 | 15 | Sustained dominant |
| R→bVII→VI→bVII | 11 | Oscillation with bVII |
| R→b6→b6→b6 | 8 | Flat submediant area |

### Melody Contour Shapes
| Shape | Frequency | Meaning |
|-------|-----------|---------|
| D (descending) | 6.3% | Single descent |
| DUDUD (oscillating) | **5.2%** | Most common multi-note shape! |
| DU (down-up) | 4.8% | Arch |
| U (ascending) | 4.5% | Single ascent |
| DD (double descent) | 2.9% | Extended fall |

**CRITICAL**: DUDUD oscillation is the most common melodic shape with 5+ notes. Not scales, not arches — OSCILLATION. Melodies breathe up-down-up-down.

### Bar-to-Bar Density Changes
| Change | Frequency |
|--------|-----------|
| Same (±1) | 47.7% |
| Small decrease (-1 to -4) | 19.0% |
| Small increase (+1 to +4) | 15.3% |
| Big decrease (>-4) | 9.9% |
| Big increase (>+4) | 8.2% |

**Density is mostly stable.** It's TEXTURE that changes, not density. Don't confuse variety with density variation.

---

## The Scalable Approach

Don't hardcode patterns. Mine them from corpus data:

1. **Texture templates** (`texture_extractor.py`): Extract actual bar-level patterns from reference scores
2. **Template library** (`texture_templates/<composer>_piano.json`): 160+ texture combos, 1800+ templates
3. **Transition model** (`texture_templates/<composer>_transition_model.json`): Markov chain of texture-to-texture probabilities
4. **Texture sequencer** (`texture_sequencer.py`): Generate bar-by-bar texture assignments matching section character
5. **Texture retriever** (`texture_retriever.py`): Find matching templates, transpose to target key
6. **Playability validator** (`playability_validator.py`): Check chord spans, registers, leaps

This works for ANY composer/genre — just change the corpus.
