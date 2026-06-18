# Ravel — Composition Guide

## Fingerprints
Any section claiming Ravel's style needs ≥3 of these 5 present.

1. **Surface precision — crystalline voicing** — Where Debussy's harmonies float, Ravel's are meticulously voiced and crystalline. Every note of every chord is placed in a specific register for a specific timbral reason. The harmonies may be extended (9th, 11th, 13th chords) but they are CLEAR — you can hear every note separately.
2. **Mechanical regularity as aesthetic** — Ravel embraces repetition, ostinato, and clockwork regularity (Boléro is the extreme example). Unlike Debussy who flows fluidly, Ravel often uses strict rhythmic patterns, exactly repeated accompaniment figures, and metronomic precision as expressive tools — the machine becoming beautiful.
3. **Bitonality / polytonal color** — Two key areas sounding simultaneously, or a melody harmonized by chords from a different key than the bass. The effect is a slight "wrongness" — almost right, but with a beautiful friction. Ravel uses this for irony, exoticism, or emotional complexity.
4. **Spanish / Basque / Iberian color** — Ravel's Basque heritage manifests in specific rhythmic patterns (bolero rhythm, habanera rhythm), ornamental gestures (guitar-like strumming, castenet-imitating percussion), and modal scales with Phrygian inflections (lowered second). Even in non-Spanish works, this Iberian DNA appears.
5. **Textural stratification** — Multiple independent musical layers sounding simultaneously, each in its own register and with its own rhythm. The melody is one layer, the accompaniment another, the bass a third — and they can be from different metric orientations. The richness comes from their coexistence, not their blending.

---

## Note-Level Technique 1: Crystalline Chord Voicing (Ravel vs Debussy)

Ravel's chords are not a harmonic wash — they are precisely voiced: each note in a specific register, each note audible. Extended chords (9ths, 11ths, 13ths) are spread across the piano's range but spaced so all notes are clear. Write every note. Never use a formula for Ravel piano harmonies.

**Dominant 13th chord in G, fully voiced across registers:**
```json
{"bar_num": 1, "_feel": "Crystalline — every note of the 13th chord in its own register. Ravel, not Debussy.", "voices": {
  "soprano": [
    {"p": ["E6","B5","G5","F5"], "d": "h",  "dyn": "mf"},
    {"p": ["D6","A5","F5","E5"], "d": "h"}
  ],
  "bass": [
    {"p": ["G2","D3","F3","A3"], "d": "h"},
    {"p": ["C3","G3","E3","B3"], "d": "h"}
  ]
}},
{"bar_num": 2, "_feel": "The chord shape slides up by step — Ravelian parallel harmony, precisely voiced", "voices": {
  "soprano": [
    {"p": ["F#6","C#6","A5","G5"],"d": "h",  "dyn": "mp"},
    {"p": ["E6","B5","G5","F#5"],"d": "h"}
  ],
  "bass": [
    {"p": ["A2","E3","G3","B3"], "d": "h"},
    {"p": ["D3","A3","F#3","C#4"],"d": "h"}
  ]
}}
```
Each chord array has 4 notes, each in a distinct register. The top voice (E6, F#6) is the melody; the inner voices provide the harmonic color. Unlike Debussy's atmospheric wash, every note here is intentionally placed — you can hear E6, B5, G5, F5 as four separate pitches. Writing `{"formula": "block_chord", ...}` for Ravel is wrong — write every note explicitly.

---

## Note-Level Technique 2: Habanera/Bolero LH Ostinato (Written Out, Exact)

Ravel's accompaniment figures are never formula references — they are written out note-for-note. The habanera rhythm (dotted quarter + eighth in 2/4) or bolero snare pattern must be written as explicit notes in an explicit voice. Exact repetition is compositional principle, not laziness.

**Habanera rhythm LH in 2/4 (4 bars, exact ostinato):**
```json
{"bar_num": 1, "_feel": "Habanera LH — dotted quarter then eighth. Written out, not formula.", "voices": {
  "soprano": [{"p": "E5",  "d": "h",  "dyn": "mp"}],
  "bass": [
    {"p": "A2",  "d": "q",  "dyn": "mp"},
    {"p": "E3",  "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [{"p": "D5",  "d": "q"}, {"p": "C#5","d": "q"}],
  "bass": [
    {"p": "A2",  "d": "q"},
    {"p": "E3",  "d": "q"}
  ]
}},
{"bar_num": 3, "_feel": "Same LH pattern exactly — the ostinato does not change", "voices": {
  "soprano": [{"p": "C#5", "d": "h"}],
  "bass": [
    {"p": "A2",  "d": "q"},
    {"p": "E3",  "d": "q"}
  ]
}},
{"bar_num": 4, "voices": {
  "soprano": [{"p": "A4",  "d": "h",  "dyn": "mf"}],
  "bass": [
    {"p": "A2",  "d": "q"},
    {"p": "E3",  "d": "q"}
  ]
}}
```
LH: A2 (root, beat 1) + E3 (5th, beat 2) — exact same every bar. For the habanera syncopation, use: `[{"p": "A2", "d": "dq"}, {"p": "E3", "d": "e"}]` = dotted quarter + eighth = beat 1 long + syncopated beat 2.

**Habanera syncopated variant (2/4):**
```json
"bass": [
  {"p": "A2", "d": "dq"},
  {"p": "E3", "d": "e"}
]
```
Sum: dq + e = 3/8 + 1/8 = 4/8 = 2/4 ✓. The dotted quarter creates the syncopated lean that is the habanera idiom. Repeat this LH pattern EXACTLY for 8–16 bars without change — the melody changes; the ostinato does not.

---

## Note-Level Technique 3: Boléro Texture Accumulation

The same melody, same harmony, same bass — but each repetition adds one new instrument/timbre to the texture. Write the melody identically each time; vary only the orchestration. After 4–6 repetitions, the texture is full but the pitch content is unchanged.

**Pass 1 (solo flute), Pass 2 (add clarinet doubling), Pass 3 (add strings):**
```json
{"bar_num": 1, "_section": "Bolero pass 1 — fl solo", "_feel": "Solo flute — the melody alone. Very precise.", "voices": {
  "fl": [
    {"p": "G5",  "d": "q",  "dyn": "p"},
    {"p": "A5",  "d": "q"},
    {"p": "Bb5", "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "sn": [
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"}
  ]
}},
{"bar_num": 17, "_section": "Bolero pass 2 — fl + cl", "_feel": "Same melody. Clarinet added below flute. Not louder — thicker.", "voices": {
  "fl": [
    {"p": "G5",  "d": "q",  "dyn": "p"},
    {"p": "A5",  "d": "q"},
    {"p": "Bb5", "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "cl": [
    {"p": "G4",  "d": "q",  "dyn": "p"},
    {"p": "A4",  "d": "q"},
    {"p": "Bb4", "d": "q"},
    {"p": "G4",  "d": "q"}
  ],
  "sn": [
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"}
  ]
}},
{"bar_num": 33, "_section": "Bolero pass 3 — fl + cl + vln1", "_feel": "Same melody, same dynamic. Strings added. Texture thickens; pitch unchanged.", "voices": {
  "fl": [
    {"p": "G5",  "d": "q",  "dyn": "mp"},
    {"p": "A5",  "d": "q"},
    {"p": "Bb5", "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "cl": [
    {"p": "G4",  "d": "q",  "dyn": "mp"},
    {"p": "A4",  "d": "q"},
    {"p": "Bb4", "d": "q"},
    {"p": "G4",  "d": "q"}
  ],
  "vln1": [
    {"p": "G5",  "d": "q",  "dyn": "mp"},
    {"p": "A5",  "d": "q"},
    {"p": "Bb5", "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "sn": [
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"},
    {"p": "D2",  "d": "e", "art": "staccato"}
  ]
}}
```
Bar 1 = pass 1: fl alone. Bar 17 = pass 2: fl + cl (IDENTICAL melody, different timbre). Bar 33 = pass 3: fl + cl + vln1 (IDENTICAL melody in all three). The snare drum (`sn`) plays the same 4-eighth-note pattern in every bar, every pass — unchanged. This is the Boléro principle: the only thing that changes is how many instruments are playing the same thing. Dynamic goes from p to mp to mf across passes — not from crescendos within passages, but from the accumulation of voices.

---

## Pattern Directives

**Piano writing (Sonatine, Gaspard de la Nuit, Miroirs):**
- RH: melody in clear single notes or parallel seconds/sevenths (Ravel uses dissonant parallelism more than Debussy, who uses thirds/fourths).
- LH: precisely figured accompaniment — either a repeating ostinato figure (written out note-for-note, repeated) or a clear textural layer distinct from the melody.
- Ravel's virtuosity is architectural, not romantic: runs and cascades exist to create texture, not expression.

**Orchestral Ravel (Bolero, La Valse, orchestrations):**
- Melody: clear single-instrument statement (C clarinet, or horn, or solo violin) — never tutti unison for primary melody.
- Accompaniment: layered ostinato figures in different instruments at different rhythmic rates.
- Each orchestral "variation" in Boléro adds a new instrument to the texture while KEEPING the same melody and harmony. Ravel's principle: texture variation IS the composition.

**Boléro rhythm (when applicable):**
- Basic bolero pattern: ♩♩♪♩♩♩♩♪♪ (snare drum) beneath a long sustained melody.
- Write the rhythm-layer (percussion or pizzicato) as a distinct explicit voice.

**Harmonic approach:**
- Use complete extended chords (major 9th, dominant 13th) but voice them transparently — each note in its own register.
- Bitonality: melody in Gb major over a bass pedal in C. Write the melody notes and bass notes explicitly without trying to "resolve" the contradiction.
- Phrygian Dominant: the chord built on the fifth scale degree with a lowered second (Spanish character) — V chord with a flat 9th.

## Anti-patterns (what sounds wrong)

- **Imprecise, impressionistic texture.** Ravel is NOT Debussy. Ravel's textures are precise, clear, and exactly voiced. A vague harmonic wash is Debussy; a crystalline, carefully-voiced dissonance is Ravel.
- **Rubato and expressive flexibility.** Ravel's music has metronomic precision. The Bolero must not breathe or flex — its power comes from its relentlessness. Even his lyrical works (Pavane pour une infante défunte) have structural regularity.
- **Melody that gets lost in texture.** In Ravel, you always know where the melody is. Even in the most complex textures, the melody sings through clearly (usually in a solo instrument or the top voice of a precise chord structure).
- **Romantic emotion-by-parameter.** Ravel is cool, ironic, observational. Emotional excess is wrong. La Valse is a waltz that disintegrates — but coldly, not tragically. The emotion comes from the precision, not from expressivity.
- **Lack of repetition.** Ravel embraces repetition as structural principle (Bolero) or as hypnotic device. A section that varies everything each time is un-Ravelian. Exact repetition IS a Ravel technique.

## ShortScore Field Recommendations

**Piano texture:**
- `rh`: melody as explicit single notes (very clear register, usually high). Parallel seconds or sevenths where Debussy would use thirds.
- `lh`: ostinato figure — write the pattern out for 4 bars, then mark it to repeat. Every note explicit.

**Dynamics:**
- Ravel's piano music often begins pp and builds through exact textural additions — not dynamic swells.
- `"expr": "précis"` — a Ravel character marking in spirit.
- Bolero-style build: maintain same dynamic level while adding instruments (the texture IS the dynamic change).

**Rhythm:**
- Habanera rhythm in LH: ♩ ♪ ♪♪ (long-short-two-shorts). Write this as dotted eighth + sixteenth + two eighths.
- Ravel's accompaniments are written-out ostinatos, not formula references. Write every note explicitly.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #17: Parallel Chord Movement — Ravel's chord planing (precisely voiced, not atmospheric)
- Technique #12: Dominant Pedal — Ravel sustains bass pedals under moving parallel harmony
- Technique #14: Pentatonic Melody — used in Ravel's Asian-inflected passages (Ma Mère l'Oye)
- Technique #15: Dorian Mode phrase — Ravel uses modal scales in Iberian-inflected works
