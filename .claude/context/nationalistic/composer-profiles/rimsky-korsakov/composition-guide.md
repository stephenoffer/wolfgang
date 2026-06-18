# Rimsky-Korsakov — Composition Guide

## Fingerprints
Any section claiming Rimsky-Korsakov's style needs ≥3 of these 5 present.

1. **Orchestral color as the primary compositional parameter** — Rimsky-Korsakov thought in colors: each instrument is a specific color, and composition means arranging colors. His Principles of Orchestration remains the definitive manual of Late Romantic orchestration. A Rimsky passage is judged first by how it sounds — which instruments, in which registers, with which doubling — before anything else.
2. **The Rimsky-Korsakov scale (octatonic) as exotic color** — Rimsky-Korsakov regularly used the octatonic scale (alternating whole-step and half-step: C-D-Eb-F-Gb-Ab-A-B-C) for fantasy and supernatural passages. Scheherazade's demonic characters, the magic sections of Sadko — all draw on this scale. It produces a specific "otherworldly" color distinct from either diatonic or whole-tone.
3. **Arabian Nights exotic color — modal scales and augmented 2nds** — Scheherazade, the Spanish Capriccio, Antar — Rimsky's exotic subjects call for specific scale types: harmonic minor (with its augmented 2nd between the 6th and 7th degrees), Phrygian mode, Arabic double-harmonic scale (C-Db-E-F-G-Ab-B-C). These are not chromatic color — they are specific modal languages for specific cultural contexts.
4. **Brilliant solo woodwind writing — the storyteller's voice** — Rimsky's orchestral solos are legendary: the bassoon in the opening of Scheherazade, the clarinet in the Spanish Capriccio, the flute in Sadko. Each solo is individually crafted for the specific timbre and technical capabilities of the instrument. These are not generic "woodwind melodies" — they are portraits of specific instrument personalities.
5. **Narrative orchestration — music as visual image** — Rimsky's program music is specifically visual: the sea (Scheherazade), the sunrise, the flight of the bumblebee. The orchestration creates these images through specific technical means: string tremolo for shimmer, woodwind fluttering for the bumblebee, sustained brass for sunrise. The technique is always in service of a specific visual or narrative image.

## Pattern Directives

**Octatonic passage:**
- Octatonic scale on C: C-D-Eb-F-F#-G#-A-B-C.
- Write 4–8 bars of melody using only these pitches.
- Harmonize with octatonic chords: C major and Eb major simultaneously, or F# major and A minor.
- The effect: mysterious, supernatural, neither major nor minor.

**Arabic/exotic modal melody:**
- Harmonic minor (exotic 2nd version): C-D-Eb-F-G-Ab-B-C (the augmented 2nd between Ab and B is the "exotic" sound).
- Double harmonic scale: C-Db-E-F-G-Ab-B-C (two augmented 2nds).
- Write a melody using the augmented 2nd as the featured interval — approach it stepwise from below, leap it, or sustain on either side of it.

**Scheherazade texture:**
- Solo violin: long, decorated melodic line with trills and ornaments. p.
- Harp: arpeggiated chords in middle register.
- Low strings: pizzicato accompaniment, very light.
- No brass or heavy woodwinds for the storyteller passages.

**Sea texture (orchestral picture):**
- Strings: tremolo on repeated note or chord, pp. The shimmer of light on water.
- Woodwinds: rising scales or arpeggios, pp. Waves.
- Brass: sustained pedal tone in horns, pp.
- The texture should feel like movement without pulse — the sea breathes, it doesn't march.

## Anti-patterns (what sounds wrong)

- **Generic orchestration.** In Rimsky, every orchestral choice has a reason tied to color or imagery. "Strings play the melody; woodwinds double it" is not sufficient — what color, what register, what specific effect?
- **Absence of exotic modal color.** A Rimsky-style passage that uses only Western diatonic major/minor has missed his defining contribution. Some modal or octatonic coloring is essential.
- **Emotional abstraction.** Rimsky's music is almost always about something specific and often visual. Abstract emotional expression is not his primary language.
- **Thick, muddy orchestration.** Despite the large orchestra, Rimsky's orchestration is clear. Each family is in its appropriate register, doublings are transparent. Muddy chords where everything is in the same register are the opposite of his teaching.
- **Undecorated solo lines.** Rimsky's solos have ornaments: trills at phrase peaks, grace notes, turns. A bare, unornamented solo line doesn't use the solo instrument's personality.

## ShortScore Field Recommendations

**Octatonic harmony:**
- Write the scale explicitly: `"_feel": "octatonic on C — supernatural, neither major nor minor"`.
- Harmonic pairs: `["C3","E3","G3"]` (C major) simultaneous with `["Eb3","G3","Bb3"]` (Eb major).

**Exotic solo:**
- `"expr": "esotique"` or `"expr": "come una fantastica"` (like a fantasy).
- Solo instrument: write every ornament explicitly.
- `"orn": "trill"` at phrase peaks; `"orn": "grace:upper"` at phrase beginnings.

**Sea tremolo:**
- `vln1`/`vln2`: `{"p": "A4", "d": "w", "art": "tremolo", "dyn": "pp"}`.
- Harp: arpeggiated whole-note chords, pp.

**Dynamics:**
- Rimsky: pp to ff. Orchestral grandeur is the goal.
- Solo passages: pp to p — the solo instrument must sing above a near-silent orchestra.
- `"expr": "brillante"` for fast, colorful passages.
- `"expr": "fantastico"` for supernatural sections.
