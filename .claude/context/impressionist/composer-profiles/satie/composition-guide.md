# Satie — Composition Guide

## Fingerprints
Any section claiming Satie's style needs ≥3 of these 5 present.

1. **Static, hypnotic repetition — furniture music** — Satie invented "furniture music" (musique d'ameublement): music meant to exist as sonic environment, not drama. His pieces often repeat short harmonic progressions or melodic cells without development, without narrative arc. The Gymnopédies repeat their three-bar phrase structure throughout. The repetition IS the aesthetic — not minimalism avant la lettre, but something stranger: music that refuses to go anywhere.
2. **Parallel chord movement without functional resolution** — Satie moves chords in parallel motion (all voices moving the same direction, same interval) — a technique Classical harmony forbids. He uses parallel 9ths, parallel 7ths, parallel quartal chords. The chords don't function as dominants or tonics — they are colors, each as equally valid as the last. No chord is more important than any other.
3. **Extreme simplicity as artistic choice** — Satie's surfaces are deceptively simple: a 4-bar melody repeated, three chords, no ornamentation. This simplicity is not naivety — it is the result of extreme artistic self-restraint. Everything unnecessary has been removed. What remains is not plain — it is essence.
4. **Humor as structural element — the sardonic title** — Satie's titles are ironic, absurd, or deadpan: "Three Pieces in the Shape of a Pear," "Genuine Flabby Preludes (for a Dog)," "Cold Pieces." The humor is embedded in the structure: the music contradicts its title, or the title contradicts what you expected from the music. This is not decoration — it IS the meaning.
5. **Medieval/Gregorian modal color** — Satie was influenced by Gregorian chant and medieval modes. His melodies use modes (especially Dorian and Phrygian) that give his music an archaic, timeless quality — as if the music predates the 19th century and its emotional storms.

## Pattern Directives

**Gymnopédie-style texture:**
- 3/4 time. LH: bass note on beat 1 (open 5th in the low register), chord on beats 2–3.
- The bass is NOT the root of the chord — the bass is often the 5th or 3rd below the chord. This creates a floating, rootless quality.
- RH: simple, stepwise melody, one note per beat (or occasionally two).
- Dynamic: pp throughout. No crescendo. No sfz. The music simply exists.

**Parallel chord movement:**
- Choose a chord type: e.g., major 9th.
- Move it in parallel: C major 9th → D major 9th → E major 9th.
- No voice-leading — all voices move exactly the same direction, same interval.
- The effect: a blurring of harmonic identity; color, not function.

**Medieval mode:**
- Dorian on D: D-E-F-G-A-B-C-D. The characteristic note: B natural (the raised 6th in the otherwise minor scale).
- Phrygian on E: E-F-G-A-B-C-D-E. The characteristic note: F natural (the minor 2nd, giving an archaic, almost Arabic quality).
- Melody: stepwise motion within the mode. No leaps larger than a 4th.

**Ironic construction:**
- If the title suggests grandeur: write music of extreme simplicity and quietness.
- If the title suggests comedy: write music of deadpan solemnity.
- The contradiction IS the piece.

## Anti-patterns (what sounds wrong)

- **Emotional development or climax.** Satie does not build toward climaxes. His music has no arc. A Satie piece with a "big moment" is wrong.
- **Ornamental richness.** Satie has no ornaments. No trills, no mordents, no grace notes. The melody is bare.
- **Complex texture.** Satie's piano writing is two or three layers at most: melody + simple accompaniment. Counterpoint, inner voices, complex bass lines — these are not Satie.
- **Emotional weight.** Satie is not sad and not happy — he is neutral, or subtly ironic. The Gymnopédies feel melancholy, but they don't weep. The coldness is part of the aesthetic.
- **Functional harmony.** A V→I cadence in Satie is unusual. His harmonies float without resolution. If a passage resolves cleanly and satisfyingly, it doesn't sound like Satie.

## ShortScore Field Recommendations

**Gymnopédie bass:**
- `lh`: `{"p": "G2", "d": "q"}` beat 1, `{"p": "B3D4", "d": "h"}` beats 2–3.
- The bass note (G) is the 5th of C major — floating, not grounded.

**Static harmony:**
- `"_feel": "same chord for 4 bars — the music is not going anywhere, and that is correct"`.
- Write the same harmony event for each measure.

**Modal melody:**
- Write every note explicitly in the Dorian or Phrygian mode.
- No chromatic inflections. No accidentals outside the mode.

**Dynamics:**
- Satie: pp to p exclusively. Anything louder is wrong.
- `"expr": "lent et douloureux"` (slow and painful) — Satie's marking for Gymnopédie No.1.
- `"expr": "sans ornement"` (without ornament) — literally his instruction.

---

## Composing a Satie phrase: step by step

Measured over his own bars: the two hands sit **21 semitones apart**, the widest
gap of any armed composer, and **one bar in six has no left hand at all**. The
emptiness is the sound. Filling it turns him into salon music.

### Step 1 — Put a bare bass low, and a chord far above it

Nothing in between. The octave and a half of silence between the hands is the
piece.

```json
"gymnopedie_bass": [
  {"p": "G2", "d": "h."},
  {"p": "rest", "d": "q"},
  {"p": ["B3", "D4", "F#4"], "d": "q"},
  {"p": "rest", "d": "q"}
]
```

### Step 2 — Leave the third beat empty and keep it empty

In 3/4, beat three is a rest, every bar, for pages. That is not a gap waiting to
be filled.

### Step 3 — Write a melody in long even values with no ornament

Small range — a fifth or a sixth for a whole phrase. It does not reach.

```json
"plain_melody": [
  {"p": "F#5", "d": "h"},
  {"p": "A5", "d": "q"},
  {"p": "G5", "d": "h"},
  {"p": "F#5", "d": "q"},
  {"p": "E5", "d": "w"}
]
```

### Step 4 — Move the harmony in parallel, unresolved

Sevenths and ninths moving as blocks. Nothing resolves in the textbook sense; a
seventh goes to another seventh.

```json
"parallel_sevenths": [
  {"p": ["D4", "F#4", "A4", "C#5"], "d": "h"},
  {"p": ["E4", "G4", "B4", "D5"], "d": "h"},
  {"p": ["F#4", "A4", "C#5", "E5"], "d": "w"}
]
```

### Step 5 — Repeat without developing, and mark the mood in words

Say it three times, nearly identically. Write the direction in French prose
above the staff, not in Italian.

---

## Checking a finished phrase

- Is the middle register empty?
- Did anything develop? It should not have.
- Is there a hairpin or a crescendo? There should not be.
- Does any phrase last four bars exactly? His rarely do.
