# Rachmaninoff — Composition Guide

## Fingerprints
Any section claiming Rachmaninoff's style needs ≥3 of these 5 present.

1. **Long arching melodic line** — The primary melody spans 8–16 bars in a single long breath before reaching a breathing point. It rises toward a peak on the 6th or 7th scale degree (the most expressive interval in minor), then descends with ornamental elaboration. The melody is not a short motif — it is a sustained flight. If a phrase feels complete after 4 bars, extend it.
2. **Wide-range piano texture** — The piano spans its entire range simultaneously: LH can reach as low as A1, while RH melody sits at C5–G6. Inner voices fill the middle register. A Rachmaninoff piano chord often spans more than two octaves. This requires large hands (his own were enormous). If the texture fits in two octaves, it isn't Rachmaninoff.
3. **Subdominant approach to climax** — The emotional peak is often approached through the subdominant (IV) rather than the dominant (V). Specifically: bVI → IV → I (the flat-sixth to subdominant to tonic), creating a "dark triumph" quality — minor-inflected approach to a major arrival. The dominant approach feels expected; the subdominant approach feels inevitable.
4. **Bell-like resonance — tonic pedal under chromatic harmony** — The tonic is sustained in the bass as a pedal point while harmonies above it move through chromaticism, creating a sense of resonance (like a church bell that keeps ringing while the overtones change). The harmonic tension "rings" against the sustained tonic. Write the bass tonic as a very long note value or repeated long notes.
5. **Sequence in long ascending sweeps** — Ascending sequences that build for 8–16 bars toward a climax. Each sequence repetition is louder, higher, and more harmonically intense. The sweep IS the climax architecture — not a single moment but a long trajectory. The target: same melodic phrase, one octave higher, ff, with doubled thirds or octaves.

---

## Composing the Peak First

Rachmaninoff's music is built around peaks. Before writing bar 1:

**Define the peak moment:**
- What is the highest note in the melody at the climax?
- What bass note grounds it? (Usually tonic or subdominant for the bVI→IV→I approach)
- Is the melody harmonized in parallel thirds or octaves at the peak?
- Dynamic: ff or fff?
- Texture: full chord voicing spanning A1–G6

Write this measure first. Then ask: what sequence of events leads here? That is your section.

**The approach trajectory:**
- Bars N-8 to N-4: start the ascending sequence at mezzo-forte in the middle register
- Bars N-4 to N-2: same fragment one step higher, forte, add inner octave doubling
- Bar N-1: the preparation — bVI or IV, dominant pedal in bass, dramatic pause or fermata if appropriate
- Bar N: arrival — fff, highest pitch, full texture, bass on tonic

**After the peak:**
- The fall is gradual — Rachmaninoff does not crash from fff to pp in one bar
- The melody descends with ornamental figuration, as if the voice is still ringing after the note
- Bass sustains on tonic, letting the harmonic resonance fade

---

---

## Note-Level Technique: Complete Ascending Sequence Buildup (4 Steps)

Before writing bar 1, fix the peak note (e.g., G6, fff, bar 20). Then build the 4-step sequence that leads there. Each step: same melodic fragment, one step higher, one layer thicker, one dynamic louder.

**4-step buildup in C minor, arriving at G6 peak:**
```json
{"bar_num": 12, "_feel": "Step 1 — the cell, quiet, small. The peak is 8 bars away.", "voices": {
  "soprano": [
    {"p": "C5",  "d": "q",  "dyn": "mp", "expr": "con passione"},
    {"p": "Eb5", "d": "q"},
    {"p": "F5",  "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "bass": [
    {"p": "C2",  "d": "q"},
    {"p": "G3",  "d": "q"},
    {"p": "Eb4", "d": "q"},
    {"p": "G4",  "d": "q"}
  ]
}},
{"bar_num": 13, "voices": {
  "soprano": [
    {"p": "Ab5", "d": "h",  "dyn": "mf"},
    {"p": "G5",  "d": "h",  "art": "tenuto"}
  ],
  "bass": [
    {"p": "C2",  "d": "h"},
    {"p": "G3",  "d": "h"}
  ]
}},
{"bar_num": 14, "_feel": "Step 2 — one step higher, mf to f, add inner octave in LH", "voices": {
  "soprano": [
    {"p": "D5",  "d": "q",  "dyn": "f"},
    {"p": "F5",  "d": "q"},
    {"p": "G5",  "d": "q"},
    {"p": "A5",  "d": "q"}
  ],
  "bass": [
    {"p": "D2",  "d": "q"},
    {"p": "A3",  "d": "q"},
    {"p": "F4",  "d": "q"},
    {"p": "A4",  "d": "q"}
  ]
}},
{"bar_num": 15, "voices": {
  "soprano": [
    {"p": "Bb5", "d": "h",  "dyn": "f"},
    {"p": "A5",  "d": "h"}
  ],
  "bass": [
    {"p": "D2",  "d": "h"},
    {"p": "F3",  "d": "h"}
  ]
}},
{"bar_num": 16, "_feel": "Step 3 — higher again. f → ff. RH now in thirds. The climax is close.", "voices": {
  "soprano": [
    {"p": ["E5","C5"],  "d": "q",  "dyn": "ff"},
    {"p": ["G5","Eb5"], "d": "q"},
    {"p": ["A5","F5"],  "d": "q"},
    {"p": ["B5","G5"],  "d": "q"}
  ],
  "bass": [
    {"p": "Ab2", "d": "q"},
    {"p": "Eb3", "d": "q"},
    {"p": "C4",  "d": "q"},
    {"p": "Eb4", "d": "q"}
  ]
}},
{"bar_num": 17, "voices": {
  "soprano": [
    {"p": ["C6","Ab5"], "d": "h",  "dyn": "ff"},
    {"p": ["B5","G5"],  "d": "h"}
  ],
  "bass": [
    {"p": "Ab2", "d": "h"},
    {"p": "Eb3", "d": "h"}
  ]
}},
{"bar_num": 18, "_feel": "Step 4 — final approach. fff. RH in octaves. The peak is the next bar.", "voices": {
  "soprano": [
    {"p": ["F5","F6"],  "d": "q",  "dyn": "fff"},
    {"p": ["G5","G6"],  "d": "q"},
    {"p": ["Ab5","Ab6"],"d": "q"},
    {"p": ["Bb5","Bb6"],"d": "q"}
  ],
  "bass": [
    {"p": "F2",  "d": "q"},
    {"p": "C3",  "d": "q"},
    {"p": "Ab3", "d": "q"},
    {"p": "F4",  "d": "q"}
  ]
}},
{"bar_num": 19, "voices": {
  "soprano": [
    {"p": ["Bb5","Bb6"],"d": "h",  "dyn": "fff"},
    {"p": ["Ab5","Ab6"],"d": "h"}
  ],
  "bass": [
    {"p": "F2",  "d": "h"},
    {"p": "Ab2", "d": "h"}
  ]
}},
{"bar_num": 20, "_feel": "THE PEAK — G6, fff, the entire section has aimed at this moment", "voices": {
  "soprano": [
    {"p": ["G5","G6"],  "d": "w",  "dyn": "fff", "expr": "pesante", "art": "tenuto"}
  ],
  "bass": [
    {"p": "C2",  "d": "w",  "dyn": "fff"}
  ]
}}
```
Step 1 (bars 12–13): C5 melody, mp, simple LH arpeggio. Step 2 (bars 14–15): D5 melody, f, richer LH. Step 3 (bars 16–17): E5 in melody doubled in thirds (both notes), ff. Step 4 (bars 18–19): F5 in melody doubled at the OCTAVE (two notes 12 semitones apart), fff. Bar 20: peak — G5/G6 octave in RH, C2 in LH, fff. Each step also goes higher in pitch: C→D→E→F→G across 8 bars.

---

## Pattern Directives

**Piano concerto / solo piano texture:**
- LH: wide arpeggiated chords (bass note spanning down to A1–C2, chord tones spread across two octaves above). OR octave melody doubling at the 8va below the RH at climactic bars.
- RH: singing melody in high register (Bb4–G6), harmonized in thirds or sixths at the peaks. Write ALL melody notes explicitly — do not use formula references for the melody.
- Inner voices: the piano's middle register (C3–C5) carries inner harmonic motion. Write these as note-level events, not formula, when they are melodically active.

**Bell texture (sustained pedal):**
- Write bass tonic as half note or whole note with very long duration to imply sustain pedal
- Upper voices move through chromatic harmony above the held bass
- Do NOT use staccato in the bass of slow movements — everything sustains

**Ascending sequence buildup:**
- Fragment: 2–4 notes. State at C4–E4 range, mp.
- Repeat at D4–F4, mf, slightly thicker accompaniment.
- Repeat at E4–G4, f, add inner octave.
- Repeat at F4–A4, ff, full chord voicing.
- Final arrival: top note at A5–G6, fff, triple octave span.
- Each repetition: `dyn` changes in the WMN events, `_feel` annotations noting "pushing forward, more urgent"

**Harmonic language:**
- Minor mode is home. Major arrivals (picardy thirds, parallel major sections) feel like hard-won triumph — use them sparingly.
- bVI → iv → V → i: the Rachmaninoff "dark" cadence progression
- Augmented chords (I+) at phrase peaks for expressive intensity — write as chord array: `["C4","E4","G#4"]`
- Chromatic neighbor tones in the melody: approach a chord tone from a semitone above or below

---

## Anti-patterns (what sounds wrong)

- **Short, fragmented melody.** Rachmaninoff does not do short motifs. His melodies unfold. A 4-bar theme is not a Rachmaninoff theme — it is a sentence that will be extended to 12 bars by the time it completes its thought. If you feel the urge to end a phrase at bar 4, extend it with a deceptive cadence.
- **Light, transparent texture.** Rachmaninoff's piano writing is thick and resonant. A Debussy-like transparent texture with empty space between registers is wrong. The piano's middle register should be full.
- **Major mode throughout.** Rachmaninoff's natural habitat is minor. A section in the pure major mode without chromatic shadows is atypical in his mature works.
- **Climax by volume alone.** The climax must arrive through the ascending sequence buildup AND the harmonic approach (bVI → IV → I or similar). A sudden fff without the harmonic approach trajectory feels unmotivated.
- **Moderate tempo.** Rachmaninoff's slow movements are extremely slow (Adagio, not Andante). His fast movements are extremely fast. The dynamic contrast of tempos is as important as dynamic contrast of volume.
- **Formula references for the melody.** Never. The long arching Rachmaninoff melody must be written note-by-note. The breathing, the ornamental turns, the placement of dissonances — these are what make it Rachmaninoff.

---

## ShortScore Field Recommendations

**Melody (rh for piano):**
```json
{"p": "F#5", "d": "dh", "dyn": "mf", "art": "tenuto", "expr": "con passione"}
```
Long note values. Tenuto on phrase peaks. `con passione` at first theme entry.

**LH arpeggiated chord (explicit notes, not formula — at climactic bars):**
```json
[
  {"p": "C2",  "d": "q"},
  {"p": "G3",  "d": "q"},
  {"p": "Eb4", "d": "q"},
  {"p": "G4",  "d": "q"}
]
```
Bass note down to C2. Chord tones spread across two octaves. Each note an eighth or quarter — arpeggiated feel from explicit note sequence.

**LH formula (non-climactic bars):**
```json
{"formula": "arpeggiated_up", "bass": "C2", "chord_tones": ["G3", "Eb4", "C5"]}
```
Only use formula when the bar is not structurally decisive. At peak bars, write every note.

**Bell pedal:**
```json
{"p": "C2", "d": "w", "dyn": "p"}
```
Whole note bass on tonic, letting it ring through the bar as upper voices move.

**Dynamics:**
- Begin themes `p` or `pp` (the long melody needs space to grow into)
- `_feel`: `"Begin as if far away — this melody is a memory"` at pp opening
- Build to `ff` at sequence climax — the buildup IS the dynamic arc
- `"expr": "pesante"` at climactic arrivals on tonic
- `"expr": "dolcissimo"` for lyrical secondary themes

**Sequence buildup `_feel` annotations:**
```json
{"bar_num": 14, "_feel": "Sequence repetition 1 — slightly more intense, lean into the melody"}
{"bar_num": 16, "_feel": "Sequence repetition 2 — pushing forward now, the climax is in sight"}
{"bar_num": 18, "_feel": "Climax — hold this note. Let it ring. The whole section has been aimed here."}
```

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #5: Ascending Sequence — the mechanical engine of every Rachmaninoff climax build
- Technique #12: Dominant Pedal — the held bass before the final approach to tonic
- Technique #8: Chopin Nocturne Bass — Rachmaninoff's wide LH arpeggio (spans 10th+) shares this pattern
- Technique #7: Neapolitan Approach — used at moments of maximum harmonic pathos in minor movements
```
