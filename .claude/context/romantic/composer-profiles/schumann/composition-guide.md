# Schumann — Composition Guide

## Fingerprints
Any section claiming Schumann's style needs ≥3 of these 5 present.

1. **Inner-voice melody — the hidden tune** — Schumann's most distinctive habit: the main melody is not in the top voice but hidden inside the texture — in the tenor register, an inner piano voice, or doubled in a mid-range instrument. The soprano may carry an accompanying figure while the "real" melody lives below it. Discovering this hidden tune is the reward for close listening.
2. **Rhythmic displacement and syncopation** — Schumann systematically shifts melodic accents away from the downbeat: long notes arrive on weak beats, phrases begin mid-bar, hemiola creates cross-rhythm against the notated meter. The effect is of a melody that resists its own meter — yearning, slightly unstable.
3. **Sudden tonal leaps — the Schumannesque shift** — Abrupt moves to distantly related keys without preparation: from E major to C major, or C minor to A major. Not modulation — just arrival. The new key is stated as a fact. The effect is like a sudden memory, an intrusion.
4. **Literary/poetic program — Florestan and Eusebius** — Every piece has a hidden narrative or character: the extrovert Florestan (fast, loud, bold) or introvert Eusebius (slow, soft, inward). Sometimes both appear in the same piece, alternating. The music is always about something emotional or literary, not abstract.
5. **Piano texture as interior monologue** — Schumann's piano writing is dense, often impractical, richly layered. The piano doesn't accompany — it thinks. The texture has multiple simultaneous ideas: melody, countermelody, bass, inner harmony, pedal all present at once. A Schumann texture is crowded with meaning.

## Pattern Directives

**Hidden inner melody:**
- Write the top voice as an arpeggiated or repeated-chord accompaniment figure.
- Write the melody in the tenor voice (LH thumb or RH inner finger) simultaneously.
- The melody is marked with tenuto; the accompaniment is unmarked. The inner voice sings; the outer frame it.

**Rhythmic displacement:**
- Begin phrases on beat 2 or beat 3, not beat 1.
- Use tied notes across barlines: tie a quarter note from beat 4 into beat 1 of the next bar, so the melody "leans" over the barline.
- Hemiola: in 6/8, write three quarter notes (3×2) against the implied two dotted-quarters (2×3).

**Sudden tonal shift:**
- At the end of a phrase in C major: don't modulate — simply state E major as the next phrase's starting chord. No pivot.
- The shock IS the effect. Let it land without preparation.
- Duration of the new key: 2–4 bars, then return (or not) without formal return.

**Florestan vs. Eusebius:**
- Florestan sections: fast (Allegro vivace), f to ff, bold rhythm, major key, outward expression.
- Eusebius sections: slow (Adagio, Andante), pp to p, legato, minor key or major with flat harmonies, inward.
- Both can appear in the same piece — mark explicitly which character is speaking.

## Anti-patterns (what sounds wrong)

- **Melody on top throughout.** A Schumann piano piece where the melody is always the top voice is missing his most personal fingerprint. Look for the hidden voice.
- **Smooth, predictable harmonic rhythm.** Schumann's harmonies don't change on schedule. They linger, then shift suddenly. A chord every 2 beats with regular changes is Haydn, not Schumann.
- **Extrovert brightness.** Schumann's major-key writing always has shadow — a modal chord, a flat-VI, a moment of minor. Pure, uncomplicated brightness belongs to Mendelssohn or early Schubert.
- **Clear phrase structure.** Schumann's phrases run on — they don't cadence cleanly. They elide, interrupt, or simply stop mid-thought. A Schumann section with neat 4-bar antecedent-consequent pairs is probably wrong.
- **Programmatic vagueness.** Every Schumann piece has a specific emotional state. "Lyrical and expressive" is not enough — what is it about? What character is speaking?

## ShortScore Field Recommendations

**Hidden inner voice:**
- `lh` or `rh_inner`: write the melody explicitly note-by-note with `"art": "tenuto"`.
- `rh` or `rh_outer`: write the accompaniment pattern.
- Both explicitly noted; the inner melody is the primary voice, not the outer.

**Rhythmic displacement:**
- Use ties across barlines: `{"p": "C4", "d": "q", "tie": true}` → `{"p": "C4", "d": "q"}` — sustained across the bar.
- Syncopation: `{"p": "E4", "d": "e"}` on beat 3.5, `{"p": "E4", "d": "q."}` sustaining into next beat.

**Tonal shift:**
- No transition marking. New section simply begins in new key.
- `"_feel": "sudden memory — E major intrudes without preparation"`.

**Dynamics:**
- `"dyn": "pp"` for Eusebius sections, `"dyn": "f"` for Florestan.
- Sudden shifts: `"dyn": "ff"` followed immediately (next measure) by `"dyn": "pp"`.
- `"expr": "innig"` (intimate/heartfelt) — Schumann's most characteristic marking.

---

## Composing a Schumann phrase: step by step

The organising fact is that **the metre and the melody disagree**. Schumann
writes the tune off the beat and leaves it there, so the ear hears a pulse the
barline denies. Straighten it out and he is gone.

### Step 1 — Write the melody, then displace it

Compose the phrase on the beat first, then move every note a half-beat or a
whole beat later and tie across the barline. The syncopation is structural, not
decoration.

```json
"displaced_melody": [
  {"p": "rest", "d": "e"},
  {"p": "A4", "d": "q"},
  {"p": "C5", "d": "q"},
  {"p": "B4", "d": "q"},
  {"p": "A4", "d": "q", "tie": "start"},
  {"p": "A4", "d": "e", "tie": "stop"}
]
```

### Step 2 — Let the accompaniment keep the true beat

The left hand states the metre plainly so the displacement is audible. If both
hands are off the beat, nothing is off the beat.

```json
"steady_accompaniment": [
  {"p": "F2", "d": "q"},
  {"p": ["A3", "C4", "F4"], "d": "q"},
  {"p": ["A3", "C4", "F4"], "d": "q"},
  {"p": ["A3", "C4", "F4"], "d": "q"}
]
```

### Step 3 — Hide a melody in an inner voice

A second tune in the tenor, moving in longer values under the surface. His
textures have more going on in the middle than they appear to.

```json
"inner_melody": [
  {"p": "F3", "d": "h"},
  {"p": "E3", "d": "h"},
  {"p": "D3", "d": "h"},
  {"p": "C3", "d": "w"}
]
```

### Step 4 — Write in short character pieces and let them contrast hard

The unit is a page, not a movement. Two adjacent pieces should differ in
character completely — that contrast is the form.

### Step 5 — Modulate by third, not by fifth

A chromatic mediant or a common-tone shift. It should feel like a change of
light rather than a journey.

---

## Checking a finished phrase

- Does the melody land on a downbeat? It mostly should not.
- Does the left hand keep the metre honest?
- Is there a line in the middle worth hearing?
