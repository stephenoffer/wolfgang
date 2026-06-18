# Messiaen — Composition Guide

## Fingerprints
Any section claiming Messiaen's style needs ≥3 of these 5 present.

1. **Modes of limited transposition** — Messiaen's self-invented scales that cannot be transposed more than 2–5 times before repeating. Most important: Mode 2 (octatonic: whole-half alternating), Mode 3 (three transpositions), Mode 6. These modes have specific characters: Mode 2 is the supernatural mode; Mode 3 is luminous and prismatic. Using these modes IS being Messiaen.
2. **Bird song transcription and imitation** — Messiaen transcribed hundreds of bird songs and used them as melodic material throughout his works. The Catalogue d'oiseaux is 13 piano pieces, each depicting a specific bird in its specific landscape. Bird songs appear as: rapid, high-register ornamental figures (woodwinds, piano treble), specific to the bird being depicted.
3. **Color-chord organ** — Messiaen was a synesthete: he experienced specific harmonies as specific colors. His "color chords" are stacked harmonies designed to produce specific color experiences. These chords often include added 9ths, 11ths, 13ths, and specific non-standard voicings that produce their characteristic luminous or dark colors.
4. **Rhythm — the non-retrogradable rhythms and Greek/Hindu influence** — Messiaen studied Greek and Hindu rhythmic modes. His rhythmic language includes: non-retrogradable rhythms (palindrome rhythms that read the same forwards and backwards), added values (a rhythm with one beat added to a pattern, making it asymmetrical), and augmentation/diminution by addition rather than multiplication.
5. **Catholic mysticism and transcendence** — Messiaen was a devout Catholic and his music is explicitly theological: the Quartet for the End of Time (from the Book of Revelation), the Turangalîla-Symphonie (love and divine joy), the Méditations sur le mystère de la Sainte Trinité. The music isn't just religious in subject — the transcendent quality is a compositional goal. When Messiaen writes a long, sustained moment of harmonic stillness, it is meant to be a mystical experience.

## Pattern Directives

**Mode 2 (octatonic) harmony:**
- Scale: C-Db-Eb-E-F#-G-A-Bb-C (alternating half-whole steps).
- All notes in the passage: from this scale only.
- Color: supernatural, mysterious, with a specific luminous-dark quality.
- Typical Messiaen chord from this mode: C-Eb-F#-A (diminished 7th, but voiced with added 9ths).

**Mode 3:**
- Scale: C-D-Db-E-Eb-F#-G-Ab-A-C (three groups of 4 notes: C-D-Db-E / Eb-F-F#-Ab / A-Bb-B-Db).
- More complex than Mode 2; produces a prismatic, rainbow quality.

**Bird song:**
- Research the specific bird's song (or imagine a specific bird).
- Write: very fast (sixteenth or thirty-second notes), high register, irregular rhythm (natural bird speech rhythm, not metric).
- The "tune" should feel improvisatory, not metrical — a bird doesn't march.
- In piano: right hand extremely high (above C6); in orchestra: solo flute or oboe in extreme register.

**Color chord:**
- Layer: root + major 3rd + augmented 5th + minor 7th + major 9th + augmented 11th.
- Write all voices as a vertical chord array.
- Sustain for several beats or bars — the color is the duration, not just the attack.
- Change color chords slowly: sustain, then move to the next color.

**Added-value rhythm:**
- Take a 4-beat pattern: ♩ ♩ ♩ ♩
- Add a dot to the 2nd note: ♩ ♩. ♩ ♩ (now 4.5 beats).
- The added dot is the Messiaen "added value." The asymmetry is the expressive element.

## Anti-patterns (what sounds wrong)

- **Standard equal temperament harmony.** Messiaen's modes are not major or minor. A passage with diatonic functional harmony is not Messiaen.
- **Regular, metric rhythm.** Messiaen's rhythm is consistently irregular. Regular 4+4+4+4 metric patterns without added values or non-retrogradable asymmetry are not his language.
- **Absent spiritual dimension.** Messiaen's music always has a transcendent or theological dimension. Music that is technically correct but spiritually inert has missed him.
- **Speed without specific birdlike character.** Fast ornamental passages need to sound like a specific bird, not just virtuosic decoration.
- **Conventional orchestration.** Messiaen uses the orchestra (and especially the Ondes Martenot) for specific color effects. "Normal" orchestration doesn't produce his distinctive luminosity.

## ShortScore Field Recommendations

**Mode 2 passage:**
- `"_mode": "Mode 2 / octatonic: C-Db-Eb-E-F#-G-A-Bb"`.
- Write all melody and harmony notes from this scale only.
- `"_feel": "Mode 2 — supernatural luminescence, dark and bright simultaneously"`.

**Bird song:**
- `fl` or `rh` (piano treble): rapid notes above C6.
- `"art": "staccato"` on the short ornamental notes.
- `"_feel": "blackbird call — rapid, irregular, unmeasured rhythm"`.
- No regular meter implied in the bird-song passage.

**Color chord:**
- Write as explicit note array: `{"p": ["C2","E3","G#3","Bb4","D5","F#5","B5"], "d": "w", "dyn": "mf"}`.
- `"_feel": "color chord — orange-gold, luminous"` (or the specific color Messiaen would give it).

**Rhythm with added value:**
- Write the dotted note explicitly: `{"p": "E4", "d": "qd"}` instead of `{"p": "E4", "d": "q"}`.
- The dot IS the Messiaen added value — mark it.

**Dynamics:**
- Messiaen: ppp to ff. Many passages sustain at ppp for long periods (the transcendent stillness).
- `"expr": "éblouissant"` (dazzling) for luminous fortissimo climaxes.
- `"expr": "très doux et mystérieux"` (very gentle and mysterious) for Mode 2 soft passages.
