# Anti-Patterns — BORING vs GOOD WMN Decisions

Side-by-side examples of lifeless composition choices and their living alternatives. Every BORING example is technically valid WMN — it just sounds like a computer wrote it. The GOOD examples sound like a human who cares about the listener.

> **Important framing:** These anti-patterns describe common pitfalls, not absolute prohibitions. Context matters — what sounds lifeless in one setting may be exactly right in another. The goal is intentional choices, not mechanical avoidance.

---

## 1. Single Phrase Covering Entire Section

**WHY it's typically boring:** One 32-bar phrase with no internal structure sounds like a machine reading a run-on sentence.

```json
// BORING: one monolithic phrase
"phrases": [{"bars": [1, 32], "melody": {"content_type": "theme", "theme_name": "main", "transformation": "original"}}]

// GOOD: multiple phrases with evolution
"phrases": [
  {"bars": [1, 8], "melody": {"transformation": "original", "harmonization": null}},
  {"bars": [9, 16], "melody": {"transformation": "original", "harmonization": {"type": "parallel_thirds"}}},
  {"bars": [17, 24], "melody": {"transformation": "sequence_up_step"}},
  {"bars": [25, 32], "melody": {"transformation": "fragmentation_tail"}}
]
```

**The listener typically needs phrase boundaries to breathe with the music.**

---

## 2. Same Accompaniment Pattern Throughout

**WHY it's often boring:** Unchanging texture can put the ear to sleep — the brain may stop listening after many bars of identical pattern.

**However, sustained repetition is valid and powerful when intentional:** Alberti bass in Mozart sonata movements, ostinato in Ravel's *Boléro*, Chopin's Prelude No. 15 ("Raindrop") with its repeated Ab through 80+ bars, Beethoven's "Waldstein" first movement with its pulsing repeated chords, minimalist works by Reich and Glass. The question is whether the repetition serves the music's intent or is simply a failure of imagination.

```json
// FLAT: alberti for 32 bars with no reason
"accompaniment": {"pattern": "alberti", "chord_progression": [...]}

// RICHER: pattern rotation
"phrases": [
  {"bars": [1, 8], "accompaniment": {"pattern": "alberti"}},
  {"bars": [9, 16], "accompaniment": {"pattern": "separated_bass_chord"}},
  {"bars": [17, 24], "accompaniment": {"pattern": "wide_arpeggio"}},
  {"bars": [25, 32], "accompaniment": {"pattern": "pedal_point"}}
]
```

**By default, rotating patterns refreshes the ear and signals new phrases. But sustained patterns can be equally effective when they serve a compositional purpose (hypnotic effect, building intensity, textural consistency).**

---

## 3. Theme Stated Identically Every Time

**WHY it's often boring:** Exact repetition without purpose can feel mechanical. Humans tend to embellish on return.

```json
// FLAT: identical restatement
{"melody": {"transformation": "original", "harmonization": null}, "dynamics": {"start": "mf"}}
// ... later ...
{"melody": {"transformation": "original", "harmonization": null}, "dynamics": {"start": "mf"}}

// GOOD: enriched return
{"melody": {"transformation": "original", "harmonization": null}, "dynamics": {"start": "p"}}
// ... later ...
{"melody": {"transformation": "original", "harmonization": {"type": "chordal"}}, "dynamics": {"start": "f"},
 "ornaments": [{"type": "turn", "bar": 6, "beat": 2}, {"type": "chromatic_neighbor", "bar": 3, "beat": 1}]}
```

**Each return typically benefits from adding something — harmony, ornaments, dynamics, register — though exact repetition can be effective for formal clarity (rondo refrains, da capo returns) or deliberate simplicity.**

---

## 4. Flat Dynamics

**WHY it's often boring:** Music without dynamic shape is like speech in monotone — technically communicating, emotionally dead.

```json
// FLAT: single level, no markings
"dynamics": {"start": "mf", "markings": []}

// GOOD: waves within the phrase
"dynamics": {
  "start": "p",
  "markings": [
    {"type": "crescendo", "from_bar": 1, "to_bar": 4},
    {"type": "level", "bar": 4, "value": "mf"},
    {"type": "diminuendo", "from_bar": 5, "to_bar": 7},
    {"type": "level", "bar": 7, "value": "p"}
  ]
}
```

**Most phrases benefit from dynamic shaping; steady dynamics are valid in context (Baroque terraced dynamics, meditative passages, marches, certain minimalist works). The key is that the dynamic choice should be intentional, not accidental.**

---

## 5. No Ornaments

**WHY it's often boring:** Unornamented melody is a skeleton. Ornaments are the flesh, the gesture, the personality.

```json
// BARE: no ornaments
"ornaments": []

// GOOD: ornaments marking phrase structure
"ornaments": [
  {"type": "grace_note", "bar": 1, "beat": 1, "part": "rh", "style": "appoggiatura"},
  {"type": "turn", "bar": 4, "beat": 3, "part": "rh"},
  {"type": "trill", "bar": 8, "beat": 3, "part": "rh", "duration": "quarter", "style": "cadential"}
]
```

**Grace at entry (hello), turn at peak (emotion), trill at cadence (punctuation). However, some styles and textures call for sparse or absent ornamentation — Modern austerity, certain folk styles, or passages where nakedness is the expressive point.**

---

## 6. All Instruments Playing All the Time

**WHY it's often boring:** Constant tutti is sonic wallpaper. The ear craves contrast in density.

```json
// FLAT: every part active in every phrase
"phrases": [{"bars": [1, 16], "parts_active": ["vln1", "vln2", "vla", "vc", "cb", "fl1", "ob1", "cl1", "bsn1"]}]

// GOOD: instruments entering and exiting
"phrases": [
  {"bars": [1, 4], "melody": {"part": "vln1"}, "accompaniment": {"part": "vc", "pattern": "pedal_point"}},
  {"bars": [5, 8], "melody": {"part": "vln1"}, "accompaniment": [{"part": "vc"}, {"part": "vla"}, {"part": "ob1", "pattern": "countermelody"}]},
  {"bars": [9, 16], "melody": {"part": "vln1"}, "accompaniment": [{"part": "vc"}, {"part": "vla"}, {"part": "vln2"}, {"part": "fl1"}, {"part": "ob1"}]}
]
```

**Build texture by adding voices. The entrance of each instrument is an event the listener feels. (Exception: sustained tutti is characteristic of certain passages — march sections, climactic peroration, chorale-style writing.)**

---

## 7. All Voices in Rhythmic Unison

**WHY it's often boring:** When every part moves at the same time, you hear one thick blob — not independent voices.

```json
// FLAT: all parts with identical rhythm
"melody": {"part": "rh", "content_type": "theme"}, "accompaniment": {"part": "lh", "pattern": "unison_with_melody"}

// GOOD: rhythmic independence
"melody": {"part": "rh", "content_type": "theme"},
"accompaniment": {"part": "lh", "pattern": "separated_bass_chord", "variation": "change_shape_every_4_bars"}
```

**The melody sings in quarters and eighths; the bass moves in its own rhythm. Two living voices, not one fat one. (Rhythmic unison is appropriate for homorhythmic chorale texture, dramatic unison passages, and certain climactic moments.)**

---

## 8. Block Chords for Accompaniment

**WHY it can be boring:** Block chords without purpose can feel static. Flowing figuration typically adds more narrative interest.

**However, block chords are appropriate and idiomatic for:** hymn/chorale writing, climactic moments (Beethoven's fortissimo chordal passages), brass fanfares, certain march textures, dramatic punctuation, and organ registration effects.

```json
// FLAT: block chords as unthinking default
"accompaniment": {"pattern": "chordal_pulse", "variation": null}

// RICHER: flowing figuration
"accompaniment": {"pattern": "wide_arpeggio", "voicing_style": "romantic_wide", "variation": "change_shape_every_4_bars"}
```

**By default, aim for flowing figuration; however, `chordal_pulse` is the right choice for hymn-like, chorale, climactic, or processional moments.**

---

## 9. Theme Melody Sounds Like Arpeggiated Chords

**WHY it's typically boring:** A melody that just outlines chord tones (C-E-G-C-E-G) has no personality — it is the harmony, not a voice above it.

```json
// FLAT: melody = chord tones only
"pitches": [
  {"pitch": "C4", "duration": "quarter"}, {"pitch": "E4", "duration": "quarter"},
  {"pitch": "G4", "duration": "quarter"}, {"pitch": "C5", "duration": "quarter"}
]

// GOOD: melody with non-chord tones and direction
"pitches": [
  {"pitch": "C4", "duration": "quarter"}, {"pitch": "D4", "duration": "eighth"},
  {"pitch": "E4", "duration": "eighth"}, {"pitch": "F4", "duration": "quarter"},
  {"pitch": "E4", "duration": "eighth"}, {"pitch": "D4", "duration": "eighth"},
  {"pitch": "C4", "duration": "half"}
]
```

**Real melodies typically have passing tones, neighbor tones, suspensions, and a sense of arc — not just the chord spelled out horizontally. (Triadic melodies are characteristic of fanfares, horn calls, and certain heroic themes — Mozart's *Eine Kleine Nachtmusik* is essentially triadic and iconic.)**

---

## 10. Generic Transition (Scales)

**WHY it's often boring:** A plain scale run connecting two themes can sound like a student exercise rather than composed music.

```json
// FLAT: bare scale passage
"melody": {"content_type": "scale_passage", "start_pitch": "C4", "end_pitch": "C5", "direction": "ascending"}

// GOOD: thematic transition using fragmented motifs
"phrases": [
  {"bars": [1, 2], "melody": {"content_type": "theme", "theme_name": "main", "transformation": "fragmentation_head"}},
  {"bars": [3, 4], "melody": {"content_type": "theme", "theme_name": "main", "transformation": "sequence_up_step"}},
  {"bars": [5, 6], "melody": {"content_type": "chromatic_run", "start_pitch": "E4", "end_pitch": "G4"}},
  {"bars": [7, 8], "melody": {"content_type": "theme", "theme_name": "lyric", "transformation": "fragmentation_head"}}
]
```

**A great transition typically dismantles the old theme and hints at the new one — the listener feels the story turning, not just the key changing.**
