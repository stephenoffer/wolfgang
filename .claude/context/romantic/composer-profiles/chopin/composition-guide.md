# Chopin — Composition Guide

## Fingerprints
Any section claiming Chopin's style needs ≥3 of these 5 present.

1. **Nocturne bass** — LH broken octave spanning 9th–12th. Low root on beat 1, chord tones spread above. NOT Alberti. Write every LH note explicitly.
2. **Grace-note entry** — Phrases begin with a grace note leaning into the first structural pitch. The melody breathes before it sings. Combined with rubato, the arrival is never mechanical.
3. **Chromatic inner voice** — While soprano moves diatonically, a middle voice descends chromatically (often C–B–Bb–A) creating warmth and ache beneath the melody.
4. **Enharmonic modulation** — Distant key arrived at through a diminished seventh or German augmented sixth respelled. The listener finds themselves somewhere new without a clear "moment of departure."
5. **Ornamental passagework as melody** — Chromatic runs, cascading sixteenth passages from a peak note are not decoration — they ARE the melody continuing. Do not write them as ornament shorthand; write out every note.

---

## Composing a Chopin Phrase: Step by Step

**Before writing bar 1**, decide: What is the emotional temperature of this phrase? Longing? Tenderness? Urgency? The LH texture, the starting note, and the first ornament are all answers to this question.

### Step 1 — Write the LH first

**CRITICAL — NOTE DENSITY**: Real Chopin nocturnes have 25-40+ notes per bar total. The LH alone typically has 6-12 notes per bar as arpeggiated eighth notes, NOT 3 quarter notes. A 3-quarter-note LH produces skeletal, un-Chopin-like music. This was verified by analyzing Chopin Op.9/2 (33 notes/bar, 74% eighths), Op.27/2, and Op.48/1 (42 notes/bar).

Choose the key area. The LH in 3/4 time follows this pattern:
- Beat 1: bass root as a single note, very low (Eb2, Db1 range) — quarter note or eighth note
- Beats 2-3: chord tones arpeggiated as EIGHTH NOTES, rising and falling across a wide span (7th to 12th above the root)

The arpeggiation on beats 2-3 is continuous — typically 4-5 eighth notes flowing upward through chord tones, creating the characteristic "nocturne wash" that sustains under the pedal.

**LH for Eb major chord, 3/4 (standard density — 6 eighth notes):**
```json
"bass": [
  {"p": "Eb2", "d": "e"},
  {"p": "Bb3", "d": "e"},
  {"p": "Eb4", "d": "e"},
  {"p": "G4",  "d": "e"},
  {"p": "Eb4", "d": "e"},
  {"p": "Bb3", "d": "e"}
]
```
Eb2 is the bass anchor. Then Bb3→Eb4→G4 rises through the chord, and Eb4→Bb3 descends back. Six eighth notes = 3 beats in 3/4. The pedal sustains the low Eb2 throughout while the upper tones ripple. Span: Eb2 to G4 = compound 10th + major 3rd.

**LH for C minor chord, 3/4 (standard density):**
```json
"bass": [
  {"p": "C2",  "d": "e"},
  {"p": "G3",  "d": "e"},
  {"p": "C4",  "d": "e"},
  {"p": "Eb4", "d": "e"},
  {"p": "C4",  "d": "e"},
  {"p": "G3",  "d": "e"}
]
```
C2 bass, then G3→C4→Eb4 rising, Eb4→C4→G3 falling. Same 6-eighth-note pattern.

**LH for Db major chord, 3/4 — ACTUAL Chopin pattern (verified from Op.9/2):**

Real Chopin LH has TWO layers per beat: a single bass note + a 2-3 note chord. Each beat = bass eighth + chord eighth. This is NOT single-note arpeggiation — it's bass + chord arpeggiation, creating 12 events (containing 20+ individual pitches) per bar.

```json
"bass": [
  {"p": "Db1",          "d": "e"},
  {"p": ["Ab2","Db3"],  "d": "e"},
  {"p": ["Db3","F3","Ab3"], "d": "e"},
  {"p": "Ab1",          "d": "e"},
  {"p": ["Db3","F3"],   "d": "e"},
  {"p": ["Ab3","Db4","F4"], "d": "e"}
]
```
Beat 1: Db1 (bass) → [Ab2,Db3] (chord) → [Db3,F3,Ab3] (fuller chord). Beat 2: Ab1 (bass shift) → [Db3,F3] → [Ab3,Db4,F4]. The bass note on each beat is a single low note; the upper voices are 2-3 note chords that ripple upward. Span: Db1 to F4 = nearly 3 octaves. Under pedal, this creates the characteristic nocturne "wash."

**Compare to REAL Op.9/2 bar 1 LH:**
`Eb2(e) → [G3,Eb4](e) → [Bb3,Eb4,G4](e) → Eb3(e) → [Ab3,D4](e) → [Cb4,D4,Ab4](e)`
Bass single note, then 2-note chord, then 3-note chord. Two harmonic beats per bar.

**For a simpler but still authentic pattern (6 events, mix of singles and chords):**
```json
"bass": [
  {"p": "Db1",          "d": "e"},
  {"p": ["Ab2","F3"],   "d": "e"},
  {"p": ["Db3","Ab3"],  "d": "e"},
  {"p": "Db2",          "d": "e"},
  {"p": ["Ab2","F3"],   "d": "e"},
  {"p": ["Db3","Ab3"],  "d": "e"}
]
```

**NEVER write the LH as single-note arpeggiation only** — that's too thin. Real Chopin's beats 2-3 use 2-3 note chords to create harmonic fullness.

### Step 2 — Write the melody (VERIFIED from real Op.9/2 analysis)

**The #1 mistake in AI-generated Chopin: uniform rhythm.** Real Chopin melodies mix dq, e, q, and s within every bar. A bar of all quarter notes (q, q, q) is never Chopin — it's a hymn.

**Real Chopin Op.9/2 first phrase melody (bars 1-4), verified from score:**
```json
[
  {"_bar": 1, "soprano": [
    {"p": "G5",  "d": "dq"},
    {"p": "G5",  "d": "e"},
    {"p": "F5",  "d": "e"},
    {"p": "G5",  "d": "e"},
    {"p": "F5",  "d": "dq"},
    {"p": "Eb5", "d": "q"},
    {"p": "Bb4", "d": "e"}
  ]},
  {"_bar": 2, "soprano": [
    {"p": "G5",  "d": "q"},
    {"p": "C5",  "d": "e", "orn": "turn"},
    {"p": "C6",  "d": "q"},
    {"p": "G5",  "d": "e"},
    {"p": "Bb5", "d": "dq"},
    {"p": "Ab5", "d": "q"},
    {"p": "G5",  "d": "e"}
  ]},
  {"_bar": 3, "soprano": [
    {"p": "F5",  "d": "dq"},
    {"p": "G5",  "d": "q"},
    {"p": "D5",  "d": "e"},
    {"p": "Eb5", "d": "dq"},
    {"p": "C5",  "d": "dq"}
  ]},
  {"_bar": 4, "soprano": [
    {"p": "Bb4", "d": "e"},
    {"p": "D6",  "d": "e"},
    {"p": "C6",  "d": "e"},
    {"p": "Bb5", "d": "s"},
    {"p": "Ab5", "d": "s"},
    {"p": "G5",  "d": "s"},
    {"p": "Ab5", "d": "s"},
    {"p": "C5",  "d": "s"},
    {"p": "D5",  "d": "s"},
    {"p": "Eb5", "d": "dq"},
    {"p": "Bb4", "d": "e"}
  ]}
]
```

**Key observations from this REAL phrase:**

1. **Rhythmic variety WITHIN every bar**: Bar 1 uses dq, e, e, e, dq, q, e — NEVER uniform rhythm. This is what makes Chopin's melody sound like speech, not a metronome.

2. **Notes per bar breathe**: Bar 1: 7 notes. Bar 2: 7 notes. Bar 3: 5 notes (settling). Bar 4: **11 notes** (cascade!). Density is NOT uniform — it alternates sparse/dense like breathing.

3. **The dq+e pair is the fingerprint rhythm**: Dotted-quarter followed by eighth. This "lean-and-release" pattern appears in nearly every bar. It IS the Chopin rubato sound.

4. **Octave leaps in the melody**: Bar 2 leaps C5→C6 (one octave!). Real Chopin melodies span nearly 2 octaves even in simple phrases. Don't restrict the melody to a narrow range.

5. **Ornamental cascades with mixed durations**: Bar 4 has eighths THEN sixteenths — the cascade accelerates as it descends. The rhythm tightens toward the phrase's end.

6. **Written-out ornaments**: The turn on C5 in bar 2 is explicit. Mordents appear as pairs of sixteenth notes. Don't use ornament shorthand — write the notes.

7. **The ORNAMENTED REPEAT is 2-3x denser**: The first phrase (bars 1-4) = 30 RH notes. The decorated repeat (bars 5-8) = **53 RH notes** — bars 5-6 have 15 notes each (almost entirely sixteenths). The decoration doesn't add 1-2 notes per bar; it doubles or triples the density with chromatic passing tones, mordents, and cascading runs.

**How to apply this to composition:**
- Bars 1-4 (simple phrase): 5-7 RH notes per bar, dq+e rhythm, one breath point
- Bars 5-8 (ornamented repeat): 10-15 RH notes per bar, sixteenth-note filigree fills gaps
- Bar 4/8 (phrase cadence with cascade): 8-11 RH notes, cascade of sixteenths descending

**Grace-note entry:**
```json
{"p": "Bb4", "d": "dq", "dyn": "p", "orn": "grace:C5"}
```
C5 (grace note, one step above) → Bb4 (first melody note, dotted quarter — NOT dotted half). A dq is the typical opening duration — the melody moves quickly to the next note.

### Step 3 — Add the chromatic inner voice

On any bar where the melody holds a long note, add a chromatic descent in the middle register. Write it as explicit notes, not a formula. The inner voice lives in the RH (written as chord arrays with the melody note as the top):

**Soprano holds G4 for 4 beats; inner voice descends:**
```json
{"bar_num": 5, "voices": {
  "soprano": [
    {"p": ["G4","E4"],  "d": "q", "dyn": "mp"},
    {"p": ["G4","Eb4"], "d": "q"},
    {"p": ["G4","D4"],  "d": "q"},
    {"p": ["G4","Db4"], "d": "q"}
  ],
  "bass": [
    {"p": "C2", "d": "q"},
    {"p": "G3", "d": "q"},
    {"p": "C4", "d": "q"}
  ]
}}
```
RH arrays: top note = soprano G4 (held); inner note descends E4→Eb4→D4→Db4 (chromatic). The soprano is stationary; the chromatic motion underneath it creates the sense of "the harmony changing beneath a fixed star." The inner voice descent is the emotional substance of the bar.

### Step 4 — Write the ornamental passagework

When the melody reaches a peak or a long held note, follow it with a chromatic run descending to the next structural note. This run is NOT optional — it IS the next phrase of the melody. Write every note:

**Peak on Bb5, then chromatic run descending to G4:**
```json
{"bar_num": 8, "voices": {
  "soprano": [
    {"p": "Bb5", "d": "q",  "dyn": "f",  "art": "tenuto"},
    {"p": "A5",  "d": "e"},
    {"p": "Ab5", "d": "e"},
    {"p": "G5",  "d": "e"},
    {"p": "F5",  "d": "e"}
  ]
}},
{"bar_num": 9, "voices": {
  "soprano": [
    {"p": "Eb5", "d": "e"},
    {"p": "D5",  "d": "e"},
    {"p": "Db5", "d": "e"},
    {"p": "C5",  "d": "e"},
    {"p": "Bb4", "d": "e"},
    {"p": "Ab4", "d": "e"},
    {"p": "G4",  "d": "q"},
    {"p": "rest","d": "q"}
  ]
}}
```
Bb5 is the peak (tenuto, forte). Then a chromatic run descends through 10 notes to G4. The run is MELODY — not decoration. The run is what the melody does after it peaks: it exhales, cascades, dissolves. G4 is the structural arrival (the 5th of C minor or the 3rd of Eb).

---

## Complete Opening Phrase — Nocturne Idiom

This is what 4 bars of a Chopin nocturne actually look like, note by note. **Modeled directly from the REAL Op.9/2 bar structure** — verified by parsing the MusicXML score. Note: mixed rhythmic values (dq, e, q, s) in the RH, and LH with bass+chord pattern.

```json
[
  {
    "m": 1,
    "_feel": "The melody enters with the characteristic dq+e lean-and-release. LH bass+chord pattern.",
    "voices": {
      "soprano": [
        {"p": "G5",  "d": "dq", "dyn": "pp", "orn": "grace:Ab5"},
        {"p": "G5",  "d": "e"},
        {"p": "F5",  "d": "e"},
        {"p": "G5",  "d": "e"},
        {"p": "F5",  "d": "dq"},
        {"p": "Eb5", "d": "q"},
        {"p": "Bb4", "d": "e"}
      ],
      "bass": [
        {"p": "Eb2",            "d": "e"},
        {"p": ["G3","Eb4"],     "d": "e"},
        {"p": ["Bb3","Eb4","G4"], "d": "e"},
        {"p": "Eb3",            "d": "e"},
        {"p": ["Ab3","D4"],     "d": "e"},
        {"p": ["Cb4","D4","Ab4"], "d": "e"}
      ]
    }
  },
  {
    "m": 2,
    "_feel": "Turn ornament on C5, then octave leap C5→C6 — the melody opens wide.",
    "voices": {
      "soprano": [
        {"p": "G5",  "d": "q"},
        {"p": "C5",  "d": "e", "orn": "turn"},
        {"p": "C6",  "d": "q"},
        {"p": "G5",  "d": "e"},
        {"p": "Bb5", "d": "dq"},
        {"p": "Ab5", "d": "q"},
        {"p": "G5",  "d": "e"}
      ],
      "bass": [
        {"p": "C2",             "d": "e"},
        {"p": ["G3","E4"],      "d": "e"},
        {"p": ["Bb3","E4","G4"], "d": "e"},
        {"p": "F2",             "d": "e"},
        {"p": ["F3","Db4"],     "d": "e"},
        {"p": ["Ab3","Db4","F4"], "d": "e"}
      ]
    }
  },
  {
    "m": 3,
    "_feel": "Cadential settling — fewer notes, dotted rhythms give weight. The phrase exhales.",
    "voices": {
      "soprano": [
        {"p": "F5",  "d": "dq", "dyn": "p"},
        {"p": "G5",  "d": "q"},
        {"p": "D5",  "d": "e"},
        {"p": "Eb5", "d": "dq"},
        {"p": "C5",  "d": "dq"}
      ],
      "bass": [
        {"p": "Bb2",            "d": "e"},
        {"p": ["F3","D4"],      "d": "e"},
        {"p": ["Bb3","D4","Ab4"], "d": "e"},
        {"p": "C3",             "d": "e"},
        {"p": ["G3","Eb4"],     "d": "e"},
        {"p": ["C4","Eb4","G4"], "d": "e"}
      ]
    }
  },
  {
    "m": 4,
    "_feel": "CASCADE — the phrase peaks with a leap to D6 then cascading sixteenths. This is Fingerprint #5: the ornamental run IS the melody.",
    "voices": {
      "soprano": [
        {"p": "Bb4", "d": "e"},
        {"p": "D6",  "d": "e"},
        {"p": "C6",  "d": "e"},
        {"p": "Bb5", "d": "s"},
        {"p": "Ab5", "d": "s"},
        {"p": "G5",  "d": "s"},
        {"p": "Ab5", "d": "s"},
        {"p": "C5",  "d": "s"},
        {"p": "D5",  "d": "s"},
        {"p": "Eb5", "d": "dq"},
        {"p": "Bb4", "d": "e"}
      ],
      "bass": [
        {"p": "Ab2",            "d": "e"},
        {"p": ["Eb3","C4"],     "d": "e"},
        {"p": ["Ab3","C4","Eb4"], "d": "e"},
        {"p": "Ab2",            "d": "e"},
        {"p": ["F3","D4"],      "d": "e"},
        {"p": ["Bb3","D4","F4"], "d": "e"}
      ]
    }
  }
]
```
**Bar 1** (7 RH + 6 LH = 13 events): G5 melody with dq+e rhythm, grace lean. LH bass+chord pattern.
**Bar 2** (7 RH + 6 LH = 13 events): Turn ornament, OCTAVE LEAP C5→C6, sighing descent.
**Bar 3** (5 RH + 6 LH = 11 events): Cadential settling, fewer notes, two dotted quarters at end.
**Bar 4** (11 RH + 6 LH = 17 events): CASCADE — leap to D6, then cascading sixteenths (Bb5→Ab5→G5→Ab5→C5→D5→Eb5). The run IS the melody.

**Average: 13.5 events/bar.** Note the density alternation: 13, 13, 11, 17. The cascade bar is the densest. This breathing density pattern is the Chopin signature.

### Verified Metrics (17 Chopin nocturnes analyzed, March 2026)

| Metric | Chopin Average | Range | Target |
|--------|---------------|-------|--------|
| Notes/bar | 17.8 | 7.5–41.7 | 15-35 |
| RH notes/bar | 11.3 | 4.0–22.4 | 7-15 |
| LH notes/bar | 6.5* | 0–20.4 | 6-20 |
| Stepwise motion % | **31%** | 10–68% | 25-45% |
| Leap (>4st) % | **53%** | 24–78% | 40-60% |
| Dotted rhythm % | **15%** | 1–39% | 10-20% |
| RH distinct durations | **27** | 9–50 | 15+ |
| RH pitch range (st) | **52** | 24–74 | 36+ |
| Octave leaps per piece | ~100 | 16–260 | 40+ |

*LH average is low because MIDI parsing merges parts. MusicXML-parsed scores show 18-20 LH pitches/bar.

### Critical Ratios (what AI-generated Chopin gets wrong)

| What | AI Tendency | Real Chopin | Fix |
|------|------------|-------------|-----|
| Stepwise motion | 80%+ (scale-like) | **31%** | Add P5, m6, M6, P8 leaps at expressive peaks |
| Rhythmic variety | 5-7 duration types | **27 types** | Mix dh, dq, q, de, e, s, t, triplets freely |
| Dotted values | <3% | **15%** | Replace q+q with dq+e throughout |
| Melody range | 2 octaves | **4.3 octaves** | Push to C4–F6; use octave displacements |
| Ornamented bars | +1-2 notes vs plain | **2-3x density** | Bar goes from 7 to 15+ events |

---

## Step 5 — LH Harmonic Progression WITHIN Each Bar

**A CRITICAL PATTERN missing from most AI compositions:** Real Chopin's LH does NOT repeat the same chord for the whole bar. Each bar typically has **2-4 different bass notes** with different chord voicings above each.

**Real Op.9/2 bar 1 LH (12 events, 4 different chords):**
```
Beat group 1: Eb2 → [G3,Eb4] → [Bb3,Eb4,G4]     = Eb major
Beat group 2: Eb3 → [Ab3,D4] → [Cb4,D4,Ab4]      = Ab7/dim (chromatic D4+Cb4!)
Beat group 3: Eb2 → [G3,Eb4] → [Bb3,Eb4,G4]      = Eb major (return)
Beat group 4: D2  → [G3,Eb4] → [Bb3,Eb4,G4]      = G minor / V of vi
```

Note:
- **4 different bass notes** in one bar (Eb2, Eb3, Eb2, D2)
- **Chromatic chord tones**: Cb4 and D4 appear TOGETHER — this is NOT in Eb major. It's a diminished color creating the "ache beneath beauty."
- **The harmony MOVES** — each beat group can be a different chord function
- **The bass line is MELODIC** — Eb2→Eb3→Eb2→D2 has its own contour

**How to apply in Db major (our nocturne):**

Instead of repeating Db-major arpeggiation for the whole bar, create a harmonic micro-journey:
```json
"bass": [
  {"p": "Db1",           "d": "e"},
  {"p": ["Ab2","F3"],    "d": "e"},
  {"p": ["Db3","F3","Ab3"], "d": "e"},
  {"p": "Gb1",           "d": "e"},
  {"p": ["Db3","Eb3"],   "d": "e"},
  {"p": ["Gb3","Bb3","Eb4"], "d": "e"}
]
```
Beat 1: Db major (I). Beat 2: Gb with added Eb = IV with 6th. Two different harmonies in one bar, connected by the bass descent Db→Gb.

**Op.9/2 bar 3 LH — even more harmonic motion (4 chords in 1 bar):**
```
Bb2 → [F3,D4] → [Bb3,D4,Ab4]     = Bb7 (V7)
B2  → [G3,F4] → [D4,F4,G4]       = G7 (V/vi, chromatic B natural!)
C3  → [G3,Eb4] → [C4,Eb4,G4]     = Cm (vi)
A2  → [Gb3,Eb4] → [C4,Eb4,Gb4]   = A°7 (dim, chromatic approach)
```
Four different chord functions in one bar. The bass DESCENDS chromatically: Bb→B→C→... wait, it goes Bb→B(up)→C(up)→A(down). It's a complex motion with chromatic B natural and diminished seventh chord at the end.

**Rule: Every bar should have AT LEAST 2 different bass notes.** Most bars in Op.9/2 have 3-4.

---

## Step 6 — Cadenza Passages (RH Solo)

Real Chopin nocturnes include cadenza-like passages where the LH drops out entirely and the RH plays an extended ornamental solo. In Op.9/2, bars 33-35 are a full cadenza:

**Op.9/2 bars 33-34: 24 thirty-second notes per bar (RH only, no LH):**
```
Cb7(t) Bb6(t) C7(t) A6(t) | Cb7(t) Bb6(t) C7(t) A6(t) | ... (repeating tremolo pattern)
```
Then bar 35: chromatic cascade descent from C7 down to D5 in sixteen thirty-second notes.

**How to incorporate a cadenza:**
- Place it at the retransition (bars 69-72 in our piece) or as a climactic passage
- Write 12-24 thirty-second notes per bar
- LH can be silent or hold a single pedal note
- The cadenza should feature: tremolo patterns, chromatic scales, arpeggiated flourishes
- It should end by landing on the dominant, preparing the return

**Cadenza example for Db major (retransition):**
```json
{"bar_num": 71, "_feel": "Cadenza — RH alone, the pianist's private reverie",
 "voices": {
   "soprano": [
     {"p": "Ab5","d": "t"}, {"p": "Gb5","d": "t"}, {"p": "Ab5","d": "t"}, {"p": "F5","d": "t"},
     {"p": "Ab5","d": "t"}, {"p": "Gb5","d": "t"}, {"p": "Ab5","d": "t"}, {"p": "F5","d": "t"},
     {"p": "Ab5","d": "t"}, {"p": "Gb5","d": "t"}, {"p": "F5","d": "t"}, {"p": "Eb5","d": "t"},
     {"p": "Db5","d": "t"}, {"p": "C5","d": "t"}, {"p": "Bb4","d": "t"}, {"p": "Ab4","d": "t"},
     {"p": "Gb4","d": "t"}, {"p": "F4","d": "t"}, {"p": "Eb4","d": "t"}, {"p": "Db4","d": "t"},
     {"p": "C4","d": "t"}, {"p": "Bb3","d": "t"}, {"p": "Ab3","d": "t"}, {"p": "Ab4","d": "q"}
   ],
   "bass": [
     {"p": "Ab1", "d": "dh"}
   ]
 }}
```
24 events: 23 thirty-second notes + landing quarter. Tremolo pattern at top, then chromatic cascade descent through 2+ octaves landing on Ab4 (the dominant note). LH holds a single Ab1 pedal.

---

## Step 7 — Octave Doublings and Double-Note Passages

### Octave Doublings (climactic moments)
At the emotional peak, double the melody at the octave above. Op.9/2 bars 30-31:
```
[Eb6+Eb7](q), [D6+D7](e), [C6+C7](e) ...
```
Every melody note appears as a two-note chord an octave apart. This creates maximum volume and brilliance.

**Apply in our piece (climax, bar 63):**
```json
"soprano": [
  {"p": ["F5","F6"], "d": "dq", "dyn": "ff", "art": "tenuto"},
  {"p": ["Eb5","Eb6"], "d": "e"},
  {"p": ["Db5","Db6"], "d": "q"},
  {"p": ["C5","C6"], "d": "e"},
  {"p": ["Bb4","Bb5"], "d": "e"}
]
```

### Double-Note Chromatic Passages (inner voice + melody)
Op.9/2 bar 12 has chromatic dyad progressions:
```
[G4,Eb5] → [A4,D5] → [A4,C5] → [A4,D5] → [F4,Bb4] → [F#4,B4] → [E4,B4] → [E4,Bb4,C5]
```
Both notes of each pair move chromatically — the top voice and bottom voice each have their own chromatic line. This is NOT just "melody + inner voice" — it's two independent chromatic voices creating a chain of dissonances resolving to consonances.

**Apply for chromatic inner voice bars (bars 11-12 in our piece):**
```json
"soprano": [
  {"p": ["Db5","F5"], "d": "e"},
  {"p": ["C5","F5"],  "d": "e"},
  {"p": ["C5","Eb5"], "d": "e"},
  {"p": ["Db5","Eb5"],"d": "e"},
  {"p": ["Bb4","Db5"],"d": "e"},
  {"p": ["B4","D5"],  "d": "e"},
  {"p": ["A4","D5"],  "d": "e"},
  {"p": ["A4","Db5","Eb5"],"d": "e"},
  {"p": ["Bb4","C5","Eb5"],"d": "e"},
  {"p": ["Db5","F5"], "d": "dq"}
]
```
Both voices move chromatically and sometimes in contrary motion. The F# (B4) and B natural (D5 approached from Db5) are chromatic passing tones that create the characteristic Chopin "ache."

---

## Step 8 — Melodic Interval Profile

**THE MOST COMMON AI FAILURE: Too much stepwise motion.**

Real Chopin melodies are **53% leaps** (intervals > 4 semitones). AI tends to write 80%+ stepwise. The fix:

| Interval type | Chopin % | AI tendency | Fix |
|--------------|---------|-------------|-----|
| Unison/repeat | 5% | 10% | Reduce repeated notes |
| Steps (1-2 st) | **31%** | **80%** | Cut in HALF |
| Small leaps (3-4 st) | 11% | 5% | Add minor/major 3rds |
| Medium leaps (5-7 st) | 18% | 3% | Add P4, P5, TT |
| Large leaps (8-12 st) | 25% | 2% | Add m6, M6, m7, P8 |
| Huge leaps (>12 st) | 10% | 0% | Add compound intervals |

**Specific leap patterns from Op.9/2:**
- Bar 2: C5→C6 (↑P8) — octave leap at turn ornament
- Bar 4: Bb4→D6 (↑16st) — compound 10th leap before cascade!
- Bar 6: G5→B4 (↓m6), then C5→F5 (↑P4), then E5→Ab5 (↑M3), then G5→Db6 (↑TT)
- Bar 11: G5→A4 (↓m7), then A4→F5 (↑m6)
- Bar 27: Ab5→C5 (↓m6), then Eb5→G6 (↑16st = compound m10)

**Rule: Every 4-bar phrase should contain at least 2 leaps of P5 or wider.** The cascade bar (bar 4/8 of each phrase) typically contains the widest leap followed by chromatic descent.

---

---

## Step 9 — Harmonic Micro-Progressions (the soul of the nocturne)

**Chopin's harmony is NOT "one chord per bar."** Each bar is a harmonic micro-journey. The LH's changing bass notes and chord voicings create a progression WITHIN the bar that gives the music its sense of constant gentle motion.

**Verified harmonic progressions from Op.9/2 (in Eb major):**

| Bar | Beat 1 harmony | Beat 2 harmony | Emotional function |
|-----|---------------|---------------|-------------------|
| 1 | Eb (I) | Ab7 with Cb (IV with dim color) | Home → subdominant darkening |
| 2 | C (V/vi) | F7→F (V/V → V) | Secondary dominant chain |
| 3 | Bb7 (V7) | G7→Cm→A°7 (V/vi → vi → dim approach) | Dominant → chromatic exploration |
| 4 | Bb (V) | Eb (I) | Dominant → home (PAC) |
| 9 | Bb (V) | F (V/V, then pedal) | Double dominant |
| 10 | Ab (IV) → Ab with Cb (iv coloring) | Eb (I) | Plagal with minor coloring → home |
| 11 | E7 (V/vi, chromatic!) | F7→G (V→V/vi) | Chromatic secondary dominants |
| 12 | C→F→Bb→A→G# (chromatic descent!) | G→F→Bb (falling, then V approach) | Chromatic bass descent through dyads |

**Key observations:**
1. **Every bar has 2 harmonies.** This creates constant harmonic motion even at slow tempo.
2. **Chromatic chords appear in EVERY phrase** — not just at modulation points. Diminished, augmented 6th, secondary dominants are woven into the fabric, not reserved for special moments.
3. **The bass line tells its own story.** Bass notes in bars 1-4: Eb→Eb→C→F→Bb→B→C→A→Bb→Bb→Eb→Eb. This is NOT just root-position chords — it's a melodic bass line with chromatic passing tones (B natural!).
4. **Deceptive resolutions are common.** Instead of V→I, Chopin often goes V→vi, V→bVI, or V→IV. The ear expects resolution and gets something warmer or more poignant.
5. **Diminished 7ths as color, not just pivots.** A common-tone diminished 7th appears within phrases just for its quality of anxiety/beauty — it doesn't necessarily modulate anywhere.

**How to apply in Db major:**
Instead of:
```
Bar N: Db major throughout (one harmony)
```
Write:
```
Bar N, beat 1: Db major (I)
Bar N, beat 2: Bbm7 (vi7) or Gb with added 6th (IV6) or Ab with chromatic approach
```
The second harmony should either (a) move toward the next bar's harmony, (b) create chromatic color, or (c) add a secondary dominant function.

**Chromatic chord insertions for Db major (use freely between diatonic pillars):**
- V7/IV (Ab7 → Gb): creates pull toward subdominant
- V7/V (Bb7 → Ab): intensifies dominant
- V7/vi (F7 → Bbm): chromatic approach to relative minor
- CT°7 (common-tone diminished): over Db bass, add B-D-F-Ab (dim7 with chromatic B natural)
- Neapolitan (D major or Ebb in bass): for dark gravitas at cadences
- German augmented 6th: for intensified approach to dominant

---

## Step 10 — Dynamic Shaping (not a flat arc)

Real Op.9/2 has **18 dynamic markings** across 38 bars — roughly one every 2 bars. The dynamic changes are frequent and dramatic:

```
p → p → pp → f → fp → p → f → fp → pp → p → f → ff → pp → ppp
```

Key patterns:
- **fp (fortepiano)**: A sudden loud accent that immediately drops to piano. Appears at emotional peaks within phrases.
- **Rapid swells**: p→f within 2-4 bars, not across 16 bars.
- **Subito dynamics**: Dynamic changes happen on specific NOTES, not at bar boundaries.
- **The climax is ff, not fff.** Chopin nocturnes rarely exceed ff. The intensity comes from registral extremity and harmonic tension, not brute force.
- **The ending is ppp** (not pp). The final bars dissolve beyond pp into near-silence.

**Anti-pattern**: A smooth pp→p→mp→mf→f→ff→p→pp arc over 100 bars. Real Chopin dynamics are *volatile* — they change quickly and often, like breathing, not like a tide.

---

## Anti-patterns (verified against 17 real nocturnes)

### FATAL (will sound nothing like Chopin)
- **Stepwise melody (>50%)** — The #1 AI failure. Real Chopin is **31% stepwise, 53% leaps**. If your melody has more steps than leaps, it's a scale exercise. Add P5, m6, P8 leaps at every expressive peak.
- **Uniform rhythm** (q, q, q or e, e, e, e, e, e). Real Chopin mixes dq+e+q+s within EVERY bar. A bar with all-same durations is never Chopin.
- **LH repeating one chord per bar.** Real Chopin has 2-4 different bass notes per bar with different chord voicings above each. The LH is a harmonic PROGRESSION, not a single-chord arpeggiation. (See Step 5)
- **No cadenza passage.** Every mature nocturne has at least one passage of 12-24 thirty-second notes (RH solo, no LH). Typically at the retransition or climax approach. (See Step 6)

### SEVERE (will sound generic)
- **Only 5-7 duration types used.** Real Chopin uses 27 different durations. Use the full vocabulary: dh, h, dq, q, de, e, s, t, trip_e, trip_q, and irregular groups (0.375, 0.125).
- **Melody range < 3 octaves.** Real Chopin melodies average 4.3 octaves (52 semitones). Use octave leaps, octave doublings, and extreme register for climaxes.
- **Dotted rhythms < 5%.** Real Chopin uses 15% dotted values. Replace q+q with dq+e throughout.
- **LH without chromatic voicings.** Real Chopin LH chords include chromatic alterations (Cb, D natural in Eb major context). The inner chord tones create the "ache beneath beauty."
- **No octave doublings at climax.** The emotional peak should double the melody at the octave: `[F5,F6]`, `[Eb5,Eb6]`. (See Step 7)
- **Ornamented repeat adds only 1-2 notes.** Real decorated repeats DOUBLE or TRIPLE note count — bars go from 7 to 15+ events.

### MODERATE (weakens authenticity)
- **No double-note chromatic passages.** Bars with two independent chromatic voices (dyad chains) create the characteristic rich inner texture. (See Step 7)
- **Block chords in LH** at any moment in a nocturne. The only exception is the climax peak bar (1-2 bars maximum).
- **Melody without grace-note entries.** First note of each phrase should lean from a grace note above.
- **Pure diatonic harmony.** Every phrase needs chromatic color — chromatic inner voice, borrowed chords, chromatic passing tones in LH voicings.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #1: Appoggiatura and Sigh (Chopin's main phrase-ending gesture)
- Technique #3: Lament Bass (used in ballades and the Op.23 Ballade)
- Technique #9: Chromatic Inner Voice Descent (the "sigh" beneath held soprano)
- Technique #8: Chopin Nocturne Bass (full note-level example of the wide LH arpeggio)
