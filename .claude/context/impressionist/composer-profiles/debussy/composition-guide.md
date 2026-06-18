# Debussy — Composition Guide

## Fingerprints
Any section claiming Debussy's style needs ≥3 of these 5 present.

1. **Parallel chord movement** — Entire chords slide in parallel motion (parallel 7ths, 9ths, 11ths, major triads) without voice-leading. These are not individual chord tones moving — entire harmonic structures float together as blocks of color. Resolution is irrelevant; the motion itself IS the harmony.
2. **Pentatonic/whole-tone melodic surface** — Melody and harmony built from scales that avoid the leading tone and traditional tonal gravity: pentatonic (five notes, no semitones), whole-tone (all whole steps), or Debussy's modes (Lydian, Dorian, Phrygian). The listener cannot predict where the melody will go because there's no gravitational pull.
3. **Texture as primary parameter** — The register, density, and timbre of each moment defines its character more than the pitch content. A cluster of harmonics in the top of the piano range IS a different musical idea from a unison in the bass — not just a different dynamic. Texture IS composition.
4. **Static harmony / non-functional chord successions** — Chords don't progress (I→IV→V→I); they are juxtaposed or sustained as color. A chord may last 8 bars. Two unrelated chords may follow each other without preparation. The absence of progression IS the harmonic language.
5. **Orchestral color as melody** — In orchestral works, the "melody" is often a timbral blend — flute+muted strings, or horn+harp — rather than a single instrument carrying a tune. Debussy's melodies can be disassembled across instruments without any single one "having" the tune.

---

## Note-Level Technique 1: Parallel Chord Movement (Planing)

The entire chord shape — all four voices — shifts together by the same interval. No voice leads independently; no dissonance resolves. The chord is a timbral block that slides.

**Parallel major 7th chords ascending by whole tone (Cmaj7 → Dmaj7 → Emaj7):**
```json
{"bar_num": 1, "_feel": "The chord shape slides — color moving without harmonic function", "voices": {
  "soprano": [
    {"p": ["E5","G5","B5","D6"],  "d": "h",  "dyn": "p"},
    {"p": ["F#5","A5","C#6","E6"],"d": "h"}
  ],
  "bass": [
    {"p": ["C3","E3","G3","B3"],  "d": "h"},
    {"p": ["D3","F#3","A3","C#4"],"d": "h"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": ["G#5","B5","D#6","F#6"], "d": "h", "dyn": "mp"},
    {"p": ["A5","C#6","E6","G#6"],  "d": "h"}
  ],
  "bass": [
    {"p": ["E3","G#3","B3","D#4"],  "d": "h"},
    {"p": ["F#3","A#3","C#4","F4"], "d": "h"}
  ]
}}
```
Every note moves up by a whole tone simultaneously. Parallel 5ths everywhere — intentional. The chord shape (1–3–5–7) does not change; only the root level changes. After 2–4 bars of planing, break the parallel motion with a different texture (pedal point or sudden registral leap).

**Parallel major triads descending by semitone (simpler version):**
```json
{"bar_num": 5, "_feel": "Triads slide down by semitone — shimmer texture", "voices": {
  "soprano": [
    {"p": ["C5","E5","G5"],   "d": "q", "dyn": "pp"},
    {"p": ["B4","D#5","F#5"], "d": "q"},
    {"p": ["Bb4","D5","F5"],  "d": "q"},
    {"p": ["A4","C#5","E5"],  "d": "q"}
  ],
  "bass": [{"p": "C3", "d": "w"}]
}}
```
Four chords in 4 beats, each a semitone lower — same major triad voicing throughout. Top voice descends by chromatic step. Bottom voice descends. Bass pedal stays on C3. The result: chromatic wash of color above a stable pedal.

---

## Note-Level Technique 2: Registral Gap Texture

Debussy places the melody in the extreme high register and the bass in the extreme low register, leaving the middle of the keyboard completely empty. This space is expressive — the resonance of the low bass rises up and blurs into the high melody through the sustain pedal.

**High melody (C6 range) + low bass (C2 range), middle empty:**
```json
{"bar_num": 1, "_feel": "The gap IS the texture — high against low, nothing between", "voices": {
  "soprano": [
    {"p": "Bb6", "d": "dh", "dyn": "pp", "expr": "doux et flottant"},
    {"p": "Ab6", "d": "q",  "art": "legato"}
  ],
  "bass": [{"p": "Gb2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "G6",  "d": "h",  "dyn": "ppp"},
    {"p": "F6",  "d": "h"}
  ],
  "bass": [{"p": "Db2", "d": "w"}]
}},
{"bar_num": 3, "_feel": "Harmony added above the bass — still no middle register", "voices": {
  "soprano": [
    {"p": "Eb6", "d": "h"},
    {"p": "D6",  "d": "h",  "dyn": "pp"}
  ],
  "bass": [
    {"p": "Ab2", "d": "h"},
    {"p": "Eb2", "d": "h"}
  ]
}}
```
RH never goes below C5. LH never goes above D3. The gap = approximately 2 octaves of silence (D3 to C5). The LH bass notes are whole notes — sustained (resonating with the sustain pedal) while the RH melody floats above. Write every note explicitly; do not use formula references for Debussy's piano textures.

---

## Note-Level Technique 3: Non-Functional Chord Succession (Static Harmony)

Two unrelated chords placed side by side — no common tones, no preparation, no voice-leading. The chords are juxtaposed as color objects. The listener experiences a shift of light, not a harmonic progression.

**Bb♭maj7 → suddenly E♭maj7 (tritone apart):**
```json
{"bar_num": 7, "_feel": "Bb major 7th — sustained, floating", "voices": {
  "soprano": [{"p": ["D5","F5","A5","C6"], "d": "w", "dyn": "pp"}],
  "bass": [{"p": ["Bb2","F3","Bb3"],    "d": "w"}]
}},
{"bar_num": 8, "_feel": "Eb major 7th — no preparation. Different light. Not a modulation.", "voices": {
  "soprano": [{"p": ["G5","Bb5","D6","F6"], "d": "w", "dyn": "p"}],
  "bass": [{"p": ["Eb2","Bb2","Eb3"],    "d": "w"}]
}},
{"bar_num": 9, "_feel": "Back to Bb — equally without preparation", "voices": {
  "soprano": [{"p": ["D5","F5","A5","C6"], "d": "w", "dyn": "pp"}],
  "bass": [{"p": ["Bb2","F3","Bb3"],    "d": "w"}]
}}
```
Bar 7: Bb major 7th chord, one bar long. Bar 8: Eb major 7th — the bass leaps a tritone; all voices move by non-voice-leading intervals. No preparation. The effect: two different harmonic colors placed side by side. Bar 9: returns to Bb equally abruptly. The alternation creates oscillating color, not progression.

---

## Pattern Directives

**Piano texture (Préludes, Images, Études):**
- LH: not a bass line or accompaniment pattern but a harmonic wash — rolled chords, pedal tones sustained with pedal, or slow-moving parallel harmonies. The LH IS a color layer, not a functional bass.
- RH: melody as single notes or sparse harmonization (never thick chords in the melody voice). The melody floats above the harmonic wash.
- Middle register: Debussy often leaves the middle register empty — very low LH + high RH with nothing between. This space IS expressive.

**Parallel harmony:**
- Write a chord (major 7th, dominant 9th, or major triad) and move it in parallel motion by step, third, or fourth. Every note of the chord moves together.
- Example: Cmaj7 → Dmaj7 → Emaj7 (each chord in the same voicing, sliding up by whole step).
- Do not resolve these parallels. Let them arrive on a new static chord.

**Whole-tone usage:**
- Whole-tone scale: C-D-E-F#-G#-A# (or Db-Eb-F-G-A-B). Build chords from this scale (augmented triads, augmented dominant 7ths).
- Used for passages of ambiguity, dream-states, or the uncanny. Not for entire movements — deployed as a coloristic moment within a predominantly modal or pentatonic texture.

**Orchestration principles:**
- Muted strings as harmonic pad (ppp, sustained, high register).
- Flute in its lower register (melancholy, breathy quality).
- Harp as harmonic color and water-imagery (parallel arpeggios, glissandi).
- Avoiding brass in forte ensemble passages — Debussy's fortissimo is all strings or woodwinds.

## Anti-patterns (what sounds wrong)

- **Resolving every dissonance.** In Debussy, a chord that "should" resolve doesn't. Dominant 7ths move to other dominant 7ths or to unrelated harmonies. An analyst who marks every V7→I resolution in Debussy is missing the point — most of them don't resolve.
- **Functional bass line.** A walking bass or bass line that outlines functional harmonic motion (I–IV–V–I) is Romantic, not Impressionist. Debussy's bass is static (pedal tones) or parallel-moving (not functional).
- **Regular phrase rhythm.** Debussy's phrases don't breathe in 4-bar or 8-bar units. They expand and contract — a phrase may be 5 bars, or 11 bars, or it may be impossible to identify where one phrase ends and another begins.
- **Melody in middle register with accompaniment above and below.** Debussy's melody is always high (extreme top of the piano, or high flute/violin) against a low harmonic support. Middle-register melody sounds Classical.
- **Loud, full-orchestra climaxes.** Debussy's climaxes are often textural, not dynamic. A climax in Debussy can be ppp — the fullest harmonic complexity, the richest timbral blend, but not necessarily loud.

## ShortScore Field Recommendations

**Piano:**
- `rh`: melody in high register (C5–C7 range), single notes or sparse parallel thirds. Grace notes at phrase openings.
- `lh`: sustained bass pedal (written as long note values: half, whole) OR slowly-moving parallel harmony (write each chord as an explicit simultaneous event).
- Use wide registral gaps — RH in C6, LH in C2.

**Dynamics:**
- Debussy's dynamic range lives mostly between pp and mf. Forte is rare and specific.
- `"dyn": "ppp"` for ethereal passages (whole-tone, high register).
- Crescendo to mf or f for emotional peaks — not fff.
- `"expr": "doux et flottant"` (sweet and floating) for typical Debussy texture.

**Harmony:**
- Write chords as simultaneous events (arrays in WMN): `["C4","E4","G4","B4"]` for Cmaj7.
- Parallel motion: write each successive chord with ALL notes transposed by the same interval.
- Avoid dominant-function preparation for key areas — just arrive somewhere new.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #17: Parallel Chord Movement — complete ShortScore example with explicit 4-voice arrays
- Technique #18: Whole-Tone Passage — 3-bar example with duration-sum checks
- Technique #14: Pentatonic Melody — for Debussy's modal/folk passages
- Technique #12: Dominant Pedal — for Debussy's sustained bass pedal points
