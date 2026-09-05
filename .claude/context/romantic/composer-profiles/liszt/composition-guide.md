# Liszt — Composition Guide

## Fingerprints
Any section claiming Liszt's style needs ≥3 of these 5 present.

1. **Thematic transformation — one idea, many faces** — Liszt's signature formal invention: a single theme appears in completely different forms across a work — as a march, a lyrical song, a virtuosic display, a funeral chorale. The transformations change tempo, key, meter, character, but share the same melodic skeleton. This is not variation (the theme stays recognizable) — it is metamorphosis (the theme becomes unrecognizable until you compare).
2. **Virtuosic transcendence — the piano as orchestra** — Liszt treats the piano as if it contained an entire orchestra: thundering octaves in the bass, soaring melody in the soprano, rapid passagework in inner voices, all simultaneously. The textures are physically demanding to the point of superhuman. The technique is not display — it is architecture. The octave passages ARE the structure.
3. **Chromatic saturation and enharmonic pivot** — Liszt uses chromatic harmony more intensively than any composer before Wagner: chains of augmented chords, whole-tone fragments, chromatic inner-voice motion that makes the key ambiguous for bars at a time. Modulation through enharmonic reinterpretation: a G# becomes Ab and opens a door to a completely new key, without warning.
4. **Rhetorical silence and dramatic tempo changes** — Liszt uses pause (complete silence) and sudden tempo change (from Presto to Adagio in one bar) as theatrical gestures. The music doesn't transition — it stops and restarts. These theatrical caesuras are essential to his rhetorical language.
5. **Hungarian color (verbunkos style)** — The verbunkos dance: dotted rhythms (long-short-short), augmented second intervals (characteristic "Gypsy" scale: A-B-C-D-Eb-F#-G-A), rapid triplet ornaments before main beats, and sudden dynamic contrasts. Appears in the Hungarian Rhapsodies and in many works as a secondary color.

## Pattern Directives

**Thematic transformation:**
- Write the theme first in its "neutral" form (moderato, mezzo forte, simple texture).
- Write transformation 1: heroic march (Maestoso, ff, dotted rhythm, bass octaves).
- Write transformation 2: lyrical song (Andante, p, right hand melody, left hand arpeggios).
- Write transformation 3: virtuosic display (Allegro, f, rapid passagework version of the same intervals).
- All three are the same pitches in different rhythmic and dynamic clothing.

**Orchestral piano texture:**
- Bass: sustained octaves in the LH, lowest register, ff.
- Melody: RH in high soprano register, tenuto on each note.
- Middle texture: inner voice arpeggios filling the space between bass and melody.
- Everything sounding simultaneously — three distinct textural layers.

**Chromatic chain:**
- A series of augmented chords: C-E-G# → E-G#-B# → G#-B#-D## — each chord shares two notes with the next.
- The chain can move anywhere — no key implied.
- Resolution: suddenly state a clear tonic after 4–6 augmented chords. The clarity is the relief.

**Verbunkos rhythm:**
- Dotted eighth + sixteenth + eighth note (♩. ♪ ♪) — the long-short-short of Hungarian dance.
- Augmented second: in the scale, between Eb and F# (in A Gypsy minor: A-B-C-D-Eb-F#-G).
- Rapid triplet ornament before the main beat: three fast notes (upper neighbor → neighbor → main note).

## Anti-patterns (what sounds wrong)

- **Technical restraint.** Liszt doesn't hold back. If a passage calls for octaves, it calls for double octaves with chromatic inner voices. Restraint is for Brahms, not Liszt.
- **Static harmonic language.** A Liszt passage that stays in one key for 16 bars is unusual. The harmony is always moving, usually chromatically.
- **Monolithic texture.** Liszt doesn't sustain one texture for long passages (unlike Beethoven's Op. 92/ii). He changes texture every 4–8 bars, using texture change as a structural marker.
- **No thematic relationship across sections.** If you're using a Liszt formal model, all themes should be transformations of each other. Introducing unrelated themes is the Romantic symphony model, not Liszt.
- **Absence of rhetorical gesture.** A Liszt piece without at least one dramatic pause or sudden tempo change has lost his theatrical language.

## ShortScore Field Recommendations

**Orchestral piano:**
- `lh`: bass octaves explicitly notated: `{"p": "C1C2", "d": "q", "dyn": "ff"}`.
- `rh`: melody in soprano: `{"p": "E5", "d": "h", "art": "tenuto"}`.
- Middle: `rh_mid` or implicit in the `lh` upper register — arpeggiated chord tones.

**Verbunkos:**
- `"time_sig": "4/4"` with explicit dotted-eighth + sixteenth groupings in notation.
- `"art": "marcato"` on all main beats.
- Rapid ornament: `"orn": "turn:upper"` or write out the three-note cell explicitly.

**Thematic transformation sections:**
- Mark each transformation: `"_feel": "same theme — march transformation, Maestoso"`.
- Document the pitch skeleton that all transformations share.

**Dynamics:**
- Liszt: pp to fff — the widest range of any composer.
- Rhetorical silence: `{"p": "rest", "d": "q"}` — short, dramatic.
- `"expr": "grandioso"` for heroic sections.
- `"expr": "dolcissimo"` for lyrical transformations.

---

## Composing a Liszt phrase: step by step

Measured over his own bars, **half of Liszt's right-hand attacks carry more than
one note** and only 36% of his melodic intervals are stepwise — the highest
chord share and the lowest step share of any armed composer. A smooth scalar
melody in single notes is the wrong instrument for this idiom.

### Step 1 — Give the theme to the middle of the keyboard, in octaves

The tune sits in the tenor register where the piano sings loudest, doubled at
the octave, with the accompaniment above AND below it. This is the
*three-hand texture* he invented.

```json
"theme_in_octaves": [
  {"p": ["Ab3", "Ab4"], "d": "q", "dyn": "mf"},
  {"p": ["C4", "C5"], "d": "e"},
  {"p": ["Db4", "Db5"], "d": "e"},
  {"p": ["Eb4", "Eb5"], "d": "h"}
]
```

### Step 2 — Wrap it in arpeggiation that crosses the theme

Both hands sweep through the harmony above and below the melody. The span is
wide — a tenth or more between consecutive notes is normal.

```json
"enveloping_arpeggio": [
  {"p": "Ab1", "d": "s"},
  {"p": "Eb2", "d": "s"},
  {"p": "Ab2", "d": "s"},
  {"p": "C3", "d": "s"},
  {"p": "Eb3", "d": "s"},
  {"p": "Ab3", "d": "s"},
  {"p": "C4", "d": "s"},
  {"p": "Eb4", "d": "s"}
]
```

### Step 3 — Transform the theme rather than developing it

The same tune returns as a march, as a lament, as a chorale — new metre, new
tempo, new accompaniment, same intervals. Thematic transformation is his
structural principle and it replaces development.

```json
"theme_transformed_march": [
  {"p": ["Ab3", "Ab4"], "d": "dq", "dyn": "ff", "art": "marcato"},
  {"p": ["C4", "C5"], "d": "s"},
  {"p": ["Db4", "Db5"], "d": "s"},
  {"p": ["Eb4", "Eb5"], "d": "q"}
]
```

### Step 4 — Move to a key a third away with no preparation

Chromatic mediants and augmented triads. He does not pivot; he simply arrives.

### Step 5 — Let the climax be genuinely enormous, then strip it bare

Full-range chords at `fff`, then a single unharmonised line at `pp`. The
contrast is the drama, and both halves must be extreme.

---

## Checking a finished phrase

- Is the right hand a bare single line anywhere for long? At 50% chordal, it
  should not be.
- Does the theme sit in the middle with texture on both sides?
- Is the widest span in the phrase at least two octaves?
