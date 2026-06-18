# Philip Glass — Composition Guide

## Fingerprints
Any section claiming Philip Glass's style needs ≥3 of these 5 present.

1. **Additive process — building by addition** — Glass's primary compositional technique: a short pattern (e.g., 3 eighth notes) is repeated, then one note is added (4 eighth notes), repeated again, then another added (5 eighth notes), and so on. The process continues until a longer pattern is reached, then the process reverses (subtractive). The structure IS the process — the listener hears the addition happening.
2. **Arpeggiated keyboard figuration — the Glass pattern** — The most recognized Glass texture: rapid, continuous arpeggiated patterns in the keyboard (piano or organ/synthesizer), steady eighth-note or sixteenth-note stream, cycling through the chord tones. The pattern is not harmony + melody — it IS everything simultaneously. The chord is embedded in the arpeggio.
3. **Modal harmony — no functional progression** — Glass uses a small number of diatonic chords from a modal scale, cycling through them in sequence. The sequence has no goal — it cycles back to the beginning. There is no tension-resolution, no dominant-tonic motion. The harmony is a cycle, not a progression.
4. **Slow harmonic rhythm under fast surface figuration** — The surface (the arpeggio pattern) moves very fast (eighth notes at ♩ = 120+). The harmony changes very slowly (every 4–8 bars). This combination — fast surface / slow harmony — creates the specifically Glass hypnotic effect.
5. **Repetition as hypnosis — the listener's time dissolves** — Glass's pieces repeat patterns many more times than seems necessary. A pattern that has "arrived" repeats 8 more times. The purpose: the repetition dissolves the listener's sense of measured time. The piece creates its own interior time. This is not laziness — it is a carefully calculated effect.

## Pattern Directives

**Additive process:**
- Choose a starting cell: 3 eighth notes (e.g., E-G-A).
- State it 4–8 times.
- Add one note: E-G-A-B (4 eighth notes). State 4–8 times.
- Add one more: E-G-A-B-E (5 eighth notes). State 4–8 times.
- Continue to 8–10 notes.
- Then reverse: subtract one note at a time.
- The process IS the structure. Don't skip steps.

**Arpeggiated pattern:**
- Right hand: rapid arpeggiation of the chord (16th or 8th notes, depending on tempo).
- Left hand: bass note on beat 1 (the root), then silent or a second bass note on beat 3.
- Pattern cycles without stopping — no breaks between repetitions.
- Dynamic: constant mp or mf throughout (the repetition has its own dynamic effect).

**Modal harmony cycle:**
- Choose 3–4 chords from D Dorian: Dm, C major, Bb major, Am.
- Each chord lasts 4–8 bars (NOT 4 beats — 4–8 entire bars).
- Cycle: Dm → C → Bb → Am → Dm → C → Bb → Am → ...
- Repeat the cycle 6–8 times before changing.
- No harmonic development — only circulation.

## Anti-patterns (what sounds wrong)

- **Functional harmony.** V→I, secondary dominants, harmonic resolution — none of these belong in Glass. His harmony circles, never resolves.
- **Varied rhythm or melody.** Glass's textures are relentlessly regular. Melodic development, rhythmic variation, expressive rubato — these destroy the hypnotic effect.
- **Short sections.** A Glass section that changes after 8 bars is not Glass. His sections continue for 64–128 bars or longer.
- **Emotional expression in the Romantic sense.** Glass doesn't "express" — he creates states. The music is about the listener's internal experience, not the composer's emotion.
- **Interesting harmony.** Interesting, complex, or ambiguous harmony pulls the listener's attention. Glass uses simple, uninteresting harmony deliberately — to keep the listener's attention on the process, not the content.

## ShortScore Field Recommendations

**Arpeggiated pattern:**
- `rh`: write out the complete pattern as explicit notes, every eighth note.
- `lh`: bass note on beat 1, rest for remaining beats.
- `"_feel": "Glass arpeggio — the pattern begins cycling here, continue for [N] bars"`.
- Do NOT use formula references for the RH arpeggio — write it out explicitly.

**Additive process:**
- Annotate each stage: `"_feel": "additive step 3 — 5 notes now: E-G-A-B-E"`.
- Each stage: write out the full pattern explicitly, note by note.

**Harmonic cycle:**
- Write each chord as a complete arpeggio pattern over the full bar.
- `"_feel": "Dm — bar 1 of 8"`, `"_feel": "Dm — bar 2 of 8"` etc.
- Chord changes: simply change the pitches in the arpeggio pattern.

**Dynamics:**
- Glass: mp for most of the piece. No dramatic swings.
- Occasional crescendo/decrescendo within a cycle — but very gradual.
- `"expr": "steady and hypnotic"` — the instruction is the aesthetic.
