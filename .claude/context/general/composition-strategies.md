# Composition Strategies — Section Type → WMN Field Choices

Every section of music has a character, and that character should dictate every WMN field. This file maps common section types to specific melody, accompaniment, dynamics, and ornament decisions. Think of each row as a recipe: the section type is the dish, the columns are the ingredients.

Cross-reference: `figuration-patterns.md` for accompaniment pattern details; `ornament-intent.md` for ornament placement rationale; `harmonic-expression.md` for chord progression design.

---

## Universal Principles

These apply broadly, though deliberate departures are valid when they serve the music:

| Principle | Why It Matters |
|-----------|----------------|
| **Most phrases benefit from dynamic shaping** | Flat dynamics tend to sound lifeless. Even pp passages typically swell and breathe. Use `markings[]` in dynamics objects. Steady dynamics are valid for Baroque terraced style, marches, or meditative passages. |
| **Texture typically changes between sections** | If two consecutive sections use the same pattern + voicing_style, the listener may hear one long blur. For contrast, consider changing pattern, voicing_style, register, or instrument density. Deliberate textural continuity across sections is valid when it serves the character (ostinato-driven works, minimalist passages). |
| **Silence is an instrument** | A `"content_type": "silence"` phrase for 1-2 bars between sections creates anticipation. Rests within phrases let melody breathe. |
| **Accompaniment pattern typically rotates** | Consider using `"variation": "change_shape_every_4_bars"` or `"change_shape_every_2_bars"`. A sustained single shape throughout a section is valid when repetition serves the intent (ostinato, hypnotic effect, Alberti bass in Classical sonatas). |
| **Ornaments mark structure** | Grace at phrase entry, turn at peak, trill at cadence. Ornaments are punctuation, not decoration. |
| **Register shapes energy** | Low register = gravity, weight. High register = light, tension. Mid = neutral. Move between registers to shape emotional arcs. |
| **Instruments enter and exit** | Not everyone plays all the time. Use `"silence"` pattern for resting parts. Build texture by adding voices; thin it by removing them. |

---

## Section Type Strategies

### 1. Theme Presentation (First Statement)

*The listener hears this melody for the first time. Let it speak clearly — bare, then gently enriched.*

| WMN Field | Choice | Notes |
|-----------|--------|-------|
| **melody.content_type** | `"theme"` | `transformation: "original"`, single voice first |
| **melody.harmonization** | `null` bars 1-4; `"parallel_thirds"` or `"parallel_sixths"` bars 5-8 | Bare → enriched arc within one statement |
| **accompaniment.pattern** | `"alberti"` / `"separated_bass_chord"` / `"pedal_point"` | Gentle, stays out of melody's way |
| **accompaniment.voicing_style** | `"classical_close"` or `"romantic_wide"` | Depends on period |
| **dynamics.start** | `"p"` | Intimate entry |
| **dynamics.markings** | crescendo bars 3→6, level `"mf"` bar 6, diminuendo to end | Gentle swell to phrase peak |
| **ornaments** | `grace_note` at bar 1 beat 1; `turn` at melodic peak | Mark entry and peak — nothing more |
| **expression** | `"cantabile, semplice"` | Singing, simple |

**Genre Variants:**

| Genre | Pattern | Voicing | Ornament Flavor | Special |
|-------|---------|---------|-----------------|---------|
| Baroque | `"alberti"` or `"walking_bass"` | `"chorale"` | Mordent at entries, trill at cadence | One voice alone first (fugue-like entry) |
| Classical | `"alberti"` | `"classical_close"` | Grace notes, turns | Clean 8-bar periods |
| Romantic | `"separated_bass_chord"` | `"romantic_wide"` | Appoggiatura at peak | Wider leaps in melody |
| Late Romantic | `"wide_arpeggio"` | `"romantic_wide"` | Chromatic neighbor | Lush, sustained pedal beneath |
| Impressionist | `"pedal_point"` or `"wide_arpeggio"` | `"open_fifth"` | Grace_flourish | Parallel chord streams, modal color |
| Modern | `"silence"` or `"pedal_point"` | `"open_fifth"` | Minimal | Stark, unaccompanied entry |
| Minimalist | `"broken_octave"` | `"open_fifth"` | None | Repetition with micro-variation |
| Film Score | `"tremolo"` (strings) | `"romantic_wide"` | Grace_flourish | Orchestral pad beneath solo instrument |

---

### 2. Theme Return (Enriched)

*The familiar melody returns — it typically GROWS. Richer harmonization, fuller accompaniment, more ornamental beauty. However, some returns are deliberately stripped-down for vulnerability or contrast.*

| WMN Field | Choice |
|-----------|--------|
| **melody.transformation** | `"original"` but with `harmonization: "chordal"` or `"parallel_thirds"` throughout |
| **accompaniment.pattern** | One step richer than first: `"alberti"` → `"wide_arpeggio"`; `"pedal_point"` → `"separated_bass_chord"` |
| **dynamics.start** | `"mf"` → builds to `"f"` |
| **ornaments** | Everything from first statement PLUS additional: `turn` on secondary beats, `chromatic_neighbor` additions |
| **expression** | `"espressivo, con calore"` |

---

### 3. Development

*Themes are torn apart, recombined, sequenced through foreign keys. Restless, searching, surprising.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"theme"` with `transformation: "fragmentation_head"`, `"sequence_up_step"`, `"inversion"` — rotate between phrases |
| **melody.harmonization** | Changes every phrase — `null` then `"parallel_thirds"` then `"chordal"` |
| **accompaniment.pattern** | Active: `"walking_bass"`, `"tremolo"`, `"wide_arpeggio"` — change every 4 bars |
| **dynamics** | `"f"` with sudden `"p"` drops (use `"subito_piano"` markings), then rebuild |
| **ornaments** | `chromatic_neighbor` — dissonant, unsettled ornaments |
| **expression** | `"agitato, con fuoco, inquieto"` |

**Genre Variants:**

| Genre | Fragmentation Style | Accompaniment | Dynamic Character |
|-------|-------------------|---------------|-------------------|
| Baroque | Sequences in circle-of-fifths | `"walking_bass"` | Terraced dynamics |
| Classical | Motivic fragmentation, sequences | `"tremolo"` + `"alberti"` alternating | Sudden p/f contrasts |
| Romantic | Thematic transformation, chromatic wandering | `"wide_arpeggio"` | Enormous crescendo arcs |
| Late Romantic | Polyphonic layering of fragments | `"countermelody"` in multiple parts | Waves building to climax |
| Impressionist | Color shifts over pedal, whole-tone passages | `"pedal_point"` | Shimmering, no single climax |
| Modern | Rhythmic displacement, interval expansion | `"octave_bass"` or `"silence"` | Jagged, percussive accents |
| Minimalist | Phase shifting, additive process | `"broken_octave"` | Gradual, almost imperceptible |
| Film Score | Layered orchestral building | `"tremolo"` (strings) + `"octave_bass"` (brass) | Relentless crescendo |

---

### 4. Transition

*Connects two stable areas. Free material, modulatory, building forward motion.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"free"` or `"scale_passage"` / `"chromatic_run"` using motivic fragments |
| **accompaniment.pattern** | `"walking_bass"` or `"broken_octave"` — building motion |
| **dynamics** | Crescendo throughout the entire transition |
| **ornaments** | Minimal — motion itself is the ornament |
| **expression** | `"poco a poco accelerando, con moto"` |

---

### 5. Climax

*Maximum intensity. Full chords, high register, everything the piece has been building toward.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"theme"` with `transformation: "original"` or `"augmentation"`, register `"high"` |
| **melody.harmonization** | `"chordal"` — full harmony |
| **accompaniment.pattern** | `"chordal_pulse"` or `"tremolo"` — maximum activity |
| **dynamics.start** | `"ff"` → `"fff"` at peak |
| **ornaments** | `trill` on sustained peak notes, `grace_flourish` before climactic arrival, `arpeggio_roll` on final chord |
| **expression** | `"grandioso, con tutta forza, maestoso"` |

---

### 6. Coda / Resolution

*The journey ends. Energy dissipates. The final breath.*

| WMN Field | Choice |
|-----------|--------|
| **melody.transformation** | `"augmentation"` (stretching out) or `"fragmentation_tail"` (the last echo) |
| **accompaniment.pattern** | Simplifying: `"pedal_point"` → `"silence"`. Use `"variation": "thin_every_4_bars"` |
| **dynamics** | `"f"` → `"p"` → `"pp"` → `"ppp"` |
| **ornaments** | Stripped bare — maybe one final `grace_note` as a last sigh |
| **expression** | `"morendo, perdendosi, calando"` |

---

### 7. Lyrical Second Theme

*Contrasts the main theme. Singing, warm, with expressive harmonic richness.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"theme"` — a different theme from the primary |
| **melody.harmonization** | `"parallel_thirds"` or `"parallel_sixths"` throughout |
| **accompaniment.pattern** | `"separated_bass_chord"` or `"wide_arpeggio"` — flowing, not rhythmic |
| **dynamics** | `"mp"` with gentle swells (hairpin crescendo/diminuendo every 4 bars) |
| **ornaments** | `appoggiatura` on expressive notes — lean-ins that ache |
| **expression** | `"cantabile, dolce, con anima"` |

---

### 8. Scherzo / Energetic

*Rhythmic vitality, playful or fierce. The body wants to move.*

| WMN Field | Choice |
|-----------|--------|
| **melody.transformation** | `"dotted_variant"` or rhythmic alteration of theme |
| **accompaniment.pattern** | `"octave_bass"` or `"bass_chord_alternation"` — driving |
| **dynamics** | `"f"` with sfz accents on downbeats |
| **ornaments** | Minimal — `mordent` for crispness, nothing lingering |
| **expression** | `"scherzando, con brio, vivace"` |

---

### 9. Slow Movement

*Time stretches. Beauty is paramount. Typically the most ornamentally rich section.*

| WMN Field | Choice |
|-----------|--------|
| **melody** | Bare first, gradually add `harmonization` phrase by phrase |
| **accompaniment.pattern** | `"separated_bass_chord"` or `"pedal_point"` — sustained, breathing |
| **dynamics** | `"pp"` → `"mp"` → `"pp"` — gentle arch |
| **ornaments** | Maximum beauty: `turn` at phrase peaks, `appoggiatura` at expressive intervals, `trill` at cadences, `grace_flourish` in late phrases |
| **expression** | `"adagio, con molto espressione, sostenuto"` |

---

### 10. Fugal / Contrapuntal

*Voices enter one by one. The accompaniment IS the other voices. Architecture made audible.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"theme"` — subject in each voice, staggered entry bars |
| **accompaniment** | Other voices use `"countermelody"` pattern — each voice is melodic |
| **dynamics** | Builds with each entry: one voice `"mp"`, two voices `"mf"`, three `"f"` |
| **ornaments** | Only ornaments intrinsic to the subject itself — `mordent` or `trill` if part of the theme |
| **expression** | `"con rigore, maestoso"` |

---

### 11. Recitative / Dramatic

*Free, speech-like. The music breathes with the drama, not with the bar line.*

| WMN Field | Choice |
|-----------|--------|
| **melody.content_type** | `"free"` — irregular rhythms, rests between phrases |
| **accompaniment.pattern** | `"silence"` or `"tremolo"` — sparse punctuation |
| **dynamics** | Sudden contrasts: `"pp"` to `"ff"` within 2 bars |
| **ornaments** | `appoggiatura` on strong beats — the expressive lean of speech |
| **expression** | `"recitativo, drammatico, parlando"` |

---

### 12. March / Processional

*Strong, regular, dignified. Dotted rhythms and weight on downbeats.*

| WMN Field | Choice |
|-----------|--------|
| **melody.transformation** | `"dotted_variant"` or original with strong rhythmic profile |
| **accompaniment.pattern** | `"bass_chord_alternation"` or `"octave_bass"` — bass on every downbeat |
| **dynamics** | `"f"` steady, with sfz on downbeats |
| **ornaments** | Crisp: `mordent` only, no lingering ornaments |
| **expression** | `"alla marcia, maestoso, con gravita"` |

---

## Instrument Family Quick Reference

*Which accompaniment patterns are most idiomatic for each family?*

| Pattern | Keyboard | Strings | Winds | Brass | Percussion |
|---------|----------|---------|-------|-------|------------|
| `separated_bass_chord` | Native home (piano, organ) | Pizz cello+bass / arco upper | Rare | Rare | N/A |
| `wide_arpeggio` | Idiomatic (piano, harp) | Harp; divisi strings | Flute runs | Rare | N/A |
| `alberti` | Piano signature | Unusual | Unusual | Not idiomatic | N/A |
| `tremolo` | Piano tremolo | Bowed tremolo — core technique | Flutter-tongue | Lip trill | Rolls |
| `octave_bass` | Piano bass | Cello+bass unison | Bassoon | Tuba, trombone | Timpani |
| `chordal_pulse` | Organ, piano | Divisi sustained | Chorale scoring | Chorale brass | Marimba chords |
| `walking_bass` | Piano LH, organ pedal | Cello, bass (jazz/baroque) | Bassoon | Tuba (march) | N/A |
| `pedal_point` | Organ (literal pedal) | Open string drone | Sustained whole notes | Horn pedal | Timpani roll |
| `broken_octave` | Piano LH | Cello pizzicato | Unusual | Unusual | N/A |
| `countermelody` | Any keyboard voice | Any string part | Oboe, flute, clarinet | Horn (lyrical) | N/A |
| `bass_chord_alternation` | Piano oom-pah | Pizz bass + arco chords | Bassoon + upper winds | Tuba + upper brass | N/A |

### Register Guidance by Family

| Family | Low Register | Mid Register | High Register |
|--------|-------------|--------------|---------------|
| Keyboard | Dark, thunderous, weighty | Singing, warm, neutral | Brilliant, crystalline, fragile |
| Strings | Rich, sonorous, grounded | Expressive, versatile | Intense, ethereal, strained |
| Winds | Hollow, mysterious, breathy | Sweet, characterful | Piercing, bright, exposed |
| Brass | Powerful, ominous, dark | Noble, warm, heroic | Blazing, triumphant, strained |
| Percussion | Deep rumble, gravity | Resonant, clear | Sharp, cutting, brittle |
