# Bartók — Composition Guide

## Fingerprints
Any section claiming Bartók's style needs ≥3 of these 5 present.

1. **Folk-derived melodic cells** — Melody fragments derived from Hungarian, Romanian, or Bulgarian folk music: pentatonic patterns (no semitones), specific folk scales (Lydian with raised 4th, Phrygian with lowered 2nd), and asymmetric phrase lengths (5-bar or 7-bar phrases instead of 4 or 8). These are not "exotic decorations" — the folk material IS the melodic DNA.
2. **Axis system tonality** — Tonal organization where tritone-related keys function as equivalents (C and F# are interchangeable tonal centers in Bartók's system). Movement from C to F# feels like a "tonic" arrival, not a distant modulation. This creates a new kind of tonality — not random chromaticism, but an organized alternative to major/minor.
3. **Night music texture** — Mysterious, static passages with sustained chromatic clusters, flutter-tongue flutes, harmonics in strings, irregular ppp pizzicato — evoking nocturnal sounds (insects, distant calls). No clear melody, no pulse, just atmospheric chromatic texture. Appears in slow movements of the quartets and concertos.
4. **Bulgarian/Balkan asymmetric rhythms** — Time signatures like 5/8 (2+3 or 3+2), 7/8 (2+2+3 or 3+2+2), 8/8 (3+2+3). These are not counted as "five beats" — they are felt as patterns of long and short. The Mikrokosmos and Music for Strings use these patterns as primary material.
5. **Percussive, motoric piano writing** — The piano as percussion instrument, not singing instrument. Hammered repeated notes, staccato octaves, cluster-chord rhythms. The melody is sometimes inside the texture (as interior voices) rather than on top. The percussive use of the piano is Bartók's most distinctive contribution to 20th-century keyboard writing.

---

## Note-Level Technique 1: 5/8 Asymmetric Rhythm (2+3 Pattern)

5/8 is not "five beats" — it is TWO unequal beat groups: short (2 eighths) + long (3 eighths). Feel: TI-ka | TUM-ta-ta. Write the bar as: e + e + q + e, or e + e + dq (dotted quarter = 3 eighths). The bass must mirror the same grouping.

**Bartók folk dance in C pentatonic, 5/8 (2+3 grouping):**
```json
{"bar_num": 1, "_feel": "5/8 as 2+3 — short|short|long. The asymmetry IS the rhythm.", "voices": {
  "soprano": [
    {"p": "C5",  "d": "e",  "dyn": "mf", "art": "marcato"},
    {"p": "D5",  "d": "e"},
    {"p": "F5",  "d": "q"},
    {"p": "G5",  "d": "e",  "art": "staccato"}
  ],
  "bass": [
    {"p": "C2",  "d": "q"},
    {"p": "C3",  "d": "dq"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "A5",  "d": "e",  "dyn": "f",  "art": "marcato"},
    {"p": "G5",  "d": "e"},
    {"p": "F5",  "d": "e"},
    {"p": "D5",  "d": "q"}
  ],
  "bass": [
    {"p": "G2",  "d": "q"},
    {"p": "G3",  "d": "dq"}
  ]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "C5",  "d": "e",  "art": "marcato"},
    {"p": "D5",  "d": "e"},
    {"p": "C5",  "d": "q"},
    {"p": "D5",  "d": "e",  "art": "staccato"}
  ],
  "bass": [
    {"p": "C2",  "d": "q"},
    {"p": "G3",  "d": "dq"}
  ]
}},
{"bar_num": 4, "_feel": "Asymmetric phrase ends on bar 4 — 5-bar phrase, not 4", "voices": {
  "soprano": [
    {"p": "G4",  "d": "e",  "dyn": "mf"},
    {"p": "A4",  "d": "e"},
    {"p": "C5",  "d": "dq"}
  ],
  "bass": [
    {"p": "C2",  "d": "e"},
    {"p": "C3",  "d": "e"},
    {"p": "G3",  "d": "dq"}
  ]
}},
{"bar_num": 5, "_feel": "Phrase ends here — 5 bars, not 4. The asymmetric phrase length is as important as the rhythm.", "voices": {
  "soprano": [
    {"p": "C4",  "d": "q",  "dyn": "mp"},
    {"p": "rest","d": "q"},
    {"p": "rest","d": "e"}
  ],
  "bass": [
    {"p": "C2",  "d": "q"},
    {"p": "rest","d": "dq"}
  ]
}}
```
Duration sums per bar: e+e+q+e = 1/8+1/8+2/8+1/8 = 5/8 ✓. Bars 1–5: 5-bar phrase (not 4). LH mirrors the 2+3 grouping: q (=2 eighths) + dq (=3 eighths) = 5/8 ✓. All melody notes from {C, D, F, G, A} — the C pentatonic. No B♭, no E♭. The folk character comes from pentatonic + asymmetric phrase, not from ornaments.

**7/8 variant (2+2+3 pattern) for reference:**
```json
{"bar_num": 1, "_feel": "7/8 as 2+2+3: short|short | short|short | long-long-long", "voices": {
  "soprano": [
    {"p": "D5", "d": "e",  "art": "marcato"},
    {"p": "E5", "d": "e"},
    {"p": "F5", "d": "e",  "art": "marcato"},
    {"p": "G5", "d": "e"},
    {"p": "A5", "d": "dq"}
  ],
  "bass": [
    {"p": "D2", "d": "q"},
    {"p": "A2", "d": "q"},
    {"p": "D3", "d": "dq"}
  ]
}}
```
Duration sum: e+e+e+e+dq = 1/8+1/8+1/8+1/8+3/8 = 7/8 ✓. LH: q+q+dq = 2/8+2/8+3/8 = 7/8 ✓.

---

## Note-Level Technique 2: Night Music Texture (Chromatic Cluster, ppp)

Night music: no pulse, chromatic clusters, ppp, extreme registers, no melody. Each instrument sustains a chromatic cluster (2–3 adjacent semitones). The texture is atmospheric, not harmonic. Sparse, isolated events — like sounds in the dark.

**Night music opening — strings only, 4 bars, no pulse:**
```json
{"bar_num": 1, "_feel": "Night — no pulse, no melody, no harmony. Only atmosphere.", "voices": {
  "vln1": [{"p": ["F5","G5","Ab5"],  "d": "w", "dyn": "ppp", "art": "harmonics"}],
  "vln2": [{"p": ["C5","Db5","D5"],  "d": "w", "dyn": "ppp"}],
  "vla":  [{"p": ["Ab4","A4","Bb4"], "d": "w", "dyn": "ppp"}],
  "vc":   [{"p": "E2",               "d": "w", "dyn": "ppp", "art": "pizz"}]
}},
{"bar_num": 2, "_feel": "A single note appears — isolated, distant, then silence", "voices": {
  "vln1": [{"p": "rest", "d": "h"}, {"p": "Bb6", "d": "e", "dyn": "ppp", "art": "harmonics"}, {"p": "rest","d": "q"}],
  "vln2": [{"p": ["C5","Db5","D5"],  "d": "w"}],
  "vla":  [{"p": ["Ab4","A4","Bb4"], "d": "w"}],
  "vc":   [{"p": "E2",               "d": "w", "art": "pizz"}]
}},
{"bar_num": 3, "voices": {
  "vln1": [{"p": ["E5","F5","F#5"],  "d": "w", "dyn": "ppp"}],
  "vln2": [{"p": "rest",             "d": "h"}, {"p": ["Db5","D5","Eb5"], "d": "h"}],
  "vla":  [{"p": ["Bb4","B4","C5"],  "d": "w", "dyn": "ppp"}],
  "vc":   [{"p": "F#2",              "d": "w", "art": "pizz"}]
}},
{"bar_num": 4, "_feel": "The texture thins to silence — a single held harmonic remains", "voices": {
  "vln1": [{"p": "A6",  "d": "w", "dyn": "pppp", "art": "harmonics"}],
  "vln2": [{"p": "rest","d": "w"}],
  "vla":  [{"p": "rest","d": "w"}],
  "vc":   [{"p": "rest","d": "w"}]
}}
```
Each cluster = 2–3 chromatic semitones as simultaneous chord array. Bar 2: single isolated event (Bb6 harmonic, eighth note) — then silence. Bar 4: single harmonic remains, everything else rests. The rests are structural — they ARE the night music. No bass motion; no melody; no rhythmic pulse.

---

## Note-Level Technique 3: Percussive Piano (Staccato + Folk Cell)

Bartók's fast piano writing: staccato octaves or chords in a relentless rhythmic pattern. The melody is often in the middle, not the top. The RH and LH play the same rhythm (unlike Classical piano where they have independent functions). Energy comes from percussive attack.

**Allegro barbaro idiom — D major pentatonic, hammered octaves:**
```json
{"bar_num": 1, "_feel": "Percussive — attack, not singing. The piano as drum.", "voices": {
  "soprano": [
    {"p": ["D5","D4"], "d": "q",  "dyn": "ff", "art": "staccato"},
    {"p": ["F#5","F#4"],"d": "q", "art": "staccato"},
    {"p": ["A5","A4"], "d": "q",  "art": "staccato"},
    {"p": ["D5","D4"], "d": "q",  "art": "staccato"}
  ],
  "bass": [
    {"p": ["D3","D2"], "d": "q",  "dyn": "ff", "art": "staccato"},
    {"p": "rest",      "d": "q"},
    {"p": ["D3","D2"], "d": "q",  "art": "staccato"},
    {"p": "rest",      "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": ["E5","E4"], "d": "q",  "art": "staccato"},
    {"p": ["D5","D4"], "d": "q",  "art": "staccato"},
    {"p": ["B4","B3"], "d": "q",  "dyn": "sfz"},
    {"p": ["A4","A3"], "d": "q",  "art": "staccato"}
  ],
  "bass": [
    {"p": ["D3","D2"], "d": "q",  "art": "staccato"},
    {"p": "rest",      "d": "q"},
    {"p": ["A2","A1"], "d": "q",  "dyn": "sfz"},
    {"p": "rest",      "d": "q"}
  ]
}},
{"bar_num": 3, "_feel": "Sforzando off the beat — metric displacement, Bartókian energy", "voices": {
  "soprano": [
    {"p": ["D5","D4"], "d": "e",  "art": "staccato"},
    {"p": ["D5","D4"], "d": "e",  "art": "staccato"},
    {"p": ["F#5","F#4"],"d": "q", "dyn": "sfz"},
    {"p": ["A5","A4"], "d": "q",  "art": "staccato"}
  ],
  "bass": [
    {"p": ["D3","D2"], "d": "e",  "art": "staccato"},
    {"p": "rest",      "d": "e"},
    {"p": ["D3","D2"], "d": "q",  "dyn": "sfz"},
    {"p": "rest",      "d": "q"}
  ]
}}
```
Every RH note is a two-note octave (staccato). LH plays beats 1 and 3 only — an incomplete metric pattern that destabilizes the regularity. Bar 3: eighth-note pairs at the start = displaced energy. The sfz in bar 2 and 3 comes off the expected downbeat. Total effect: driven, relentless, percussive — no lyricism.

---

## Pattern Directives

**Folk-derived melody:**
- Use a pentatonic cell as the melodic source: C-D-F-G-A (no B, no Eb). Build a phrase from 4–7 of these pitches.
- Asymmetric phrase length: 5 bars (4+1) or 7 bars (4+3) rather than 4 or 8.
- The melody should "sound like" it could be from an Eastern European folk song — short, descending, with a specific modal character.

**Night music passage:**
- All instruments: ppp. No clear pulse. Sustain with long values.
- Chromatic cluster harmony: multiple adjacent semitones sounding simultaneously (C-Db-D-Eb as a chord).
- Individual instruments: flutter-tongue (flute), col legno (strings struck with the wood of the bow), harmonics (strings).
- The texture should be ambiguous — no clear meter, no clear melody, just atmospheric sound.

**Asymmetric rhythm:**
- 5/8 time: feel it as 2+3 (short-short-LONG-LONG-LONG). Mark the accent pattern explicitly.
- 7/8 time: feel it as 2+2+3 (short-short | short-short | LONG-LONG-LONG).
- Write the melody with explicit durations matching the rhythmic pattern, not just "quarter and eighth."

**Chromatic saturation:**
- Bartók's harmony often uses all 12 chromatic pitches in close proximity — not serially, but as total chromaticism within a local tonal center.
- The tonal center is implied by pedal tone or by the melody's implied key, even when the harmony is fully chromatic.

## Anti-patterns (what sounds wrong)

- **Generic "atonal" writing.** Bartók is not random — he has a tonal system (axis system). Writing chromatic music without a tonal center and calling it Bartók is wrong. There's always an organizing principle.
- **Western European melody.** A melody that sounds like Romantic or Classical Western music over chromatic harmonies is not Bartók. The folk-derived modal character of the melody is essential.
- **Smooth, connected textures in fast movements.** Bartók's fast movements are percussive and spiky — staccato, marcato, hammered. Smooth legato in a Bartók Allegro barbaro is wrong.
- **Night music without the atmosphere.** The "night music" texture requires the specific combination: chromatic clusters, no pulse, ppp, extended techniques. A slow pp passage with regular harmony is not night music.
- **Regular meter in folk-dance sections.** If you're writing in Bartók's folk-dance idiom, irregular meter (5/8, 7/8) is mandatory. Regular 4/4 makes it sound generic.

## ShortScore Field Recommendations

**Piano (percussive style):**
- Melody: often interior (left hand at mid-register) rather than top-voice.
- Accompaniment: repeated staccato notes or cluster chords in a rhythmic pattern.
- Articulation: `"art": "staccato"` and `"art": "marcato"` predominate.

**Night music:**
- All parts: very long note values (half, whole), `"dyn": "ppp"`.
- Include chromatic cluster chords as simultaneous note arrays.
- No rhythmic pulse — each event occurs without metric regularity.

**Folk-dance sections:**
- 5/8 or 7/8 time signature with explicit accent grouping.
- Melody: modal (Lydian, Phrygian, pentatonic) with short phrases.
- Bass: repeated single-note ostinato matching the asymmetric rhythmic pattern.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #14: Pentatonic Melody — the C-D-F-G-A cell with drone bass
- Technique #15: Dorian Mode phrase — Bartók uses Dorian extensively in Hungarian folk idiom
- Technique #5: Ascending Sequence — used in fast sections for escalation
- Technique #12: Dominant Pedal — for Bartók's sustained-tension moments before resolution
