# Steve Reich — Composition Guide

## Fingerprints
Any section claiming Steve Reich's style needs ≥3 of these 5 present.

1. **Phasing — the same pattern in two voices, slightly out of sync** — Reich's defining technique: two instruments play the identical rhythmic pattern, but one gradually speeds up (or starts later), moving through all possible phase relationships with the other. Piano Phase and Violin Phase are the paradigms. The phasing creates constantly shifting rhythmic patterns from a single simple pattern.
2. **Gradual process — the process is the music** — Reich: "I am interested in perceptible processes. I want to be able to hear the process happening throughout the sounding music." The process (phasing, addition, subtraction) is not hidden — it IS what you listen to. The music is the experience of a process happening in real time.
3. **Pulsing pattern texture — the constant eighth-note stream** — Reich's ensembles produce a constant, steady stream of eighth notes (or 16th notes), with the melody embedded in which notes are emphasized by the players. The "tune" emerges from selective accenting within a constant pulse — it is not a melody played against a background; the melody IS the background.
4. **Diatonic tonality — simple harmony, complex rhythm** — Unlike Glass (modal cycling), Reich is often purely diatonic: C major, no chromaticism. The harmonic language is simple, even simple-minded. The rhythmic complexity is where all the interest lives. The harmony is stable so that the rhythmic structure can be heard without harmonic distraction.
5. **Rhythmic canons and interlocking parts** — Reich writes for multiple performers playing complementary rhythmic patterns that interlock: one player has the "off-beat" version of the pattern another player has on the "on-beat." Together, they fill in all the rhythmic space. Each part is incomplete; together they are dense.

## Pattern Directives

**Phasing texture:**
- Write one 4-bar pattern (the basic unit).
- Player 1: plays the pattern at exactly the given tempo.
- Player 2: begins playing the same pattern ONE EIGHTH NOTE LATER than Player 1.
- Write both parts explicitly for the phase-shifted version.
- The rhythmic conflict between them creates the texture.

**Interlocking parts:**
- Player A has the pattern on all odd sixteenth-note positions: 1, 3, 5, 7 of each bar.
- Player B has the pattern on all even positions: 2, 4, 6, 8.
- Together: all 8 positions covered.
- Each part alone: spare; together: dense.

**Constant pulse with melodic implication:**
- Write 8 sixteenth notes per beat (32nds in a slow tempo): all the same pitch.
- Selectively accent 3 or 4 of them: these form the "melody."
- The unaccented notes are still played — they are the pulse.
- The melody is the selective emphasis within the constant stream.

**Gradual addition:**
- Start with 1 note of the pattern.
- Each repetition: add one more note until the complete pattern sounds.
- The listener hears the pattern "assembling itself."

## Anti-patterns (what sounds wrong)

- **Sudden changes.** Reich's processes are gradual. A sudden change of texture, key, or tempo is wrong.
- **Complex harmony.** Simple, diatonic, unchanging — the harmony should never be interesting on its own. The interest is all rhythmic.
- **Emotional expression.** Reich's music is process-driven, not emotion-driven. An "expressive" dynamic gesture, a ritardando, a rallentando — these break the process.
- **Individual solos.** Reich's music is ensemble music. Individual soloistic passages with elaborate melody break the collective texture.
- **Silence.** Reich's music doesn't stop. Unlike Pärt or Webern, the pulse is constant. A bar of silence is extremely unusual.

## ShortScore Field Recommendations

**Phasing:**
- Write both parts explicitly: `"p1"` and `"p2"` parts.
- Mark the phase offset: `"_feel": "p2 is one eighth note behind p1 — the phase begins here"`.
- Write out both parts in full for the phased section.

**Interlocking:**
- `"p1"`: notes on 16th-note positions 1, 3, 5, 7.
- `"p2"`: notes on 16th-note positions 2, 4, 6, 8.
- Together: `{"p": "E4", "d": "s"}` × 8 per beat across both parts.

**Constant pulse:**
- All notes: same duration (sixteenth or eighth), no variation.
- Selective accent: `"art": "accent"` on the 3–4 "melody" notes within the stream.
- All other notes: no marking (they are the pulse).

**Dynamics:**
- Reich: mp constant. No dramatic swings.
- The process creates dynamic interest; the performers don't add to it.
- `"expr": "mechanical"` — the aesthetic is precision, not warmth.
- `"dyn": "mp"` throughout most pieces. The pattern change IS the dynamic event.
