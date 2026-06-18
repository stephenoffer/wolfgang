# Copland — Composition Guide

## Fingerprints
Any section claiming Copland's style needs ≥3 of these 5 present.

1. **Open, widely-spaced harmonies — the American landscape** — Copland's most immediately recognizable sound: chords with open 5ths and 4ths in the bass, wide spacing (bass in the lowest register, melody in the highest, virtually nothing in between), and lots of silence. The spacing suggests vast space — the American prairie, the open sky. A Copland chord is not lush; it is lean, spare, and spacious.
2. **Pandiatonicism — all notes of the key simultaneously** — Copland uses all seven notes of a diatonic scale simultaneously or in rapid succession, without any one note functioning as a tension/resolution agent. The result is a bright, major-sounding, "all-white-key" or "all-black-key" texture that is tonal but non-functional. No note is more important than any other — they all contribute to the color.
3. **American folk and hymn melody** — From Appalachian Spring and Billy the Kid: the folk melody (Simple Gifts, Western cowboy tunes, hoedown tunes) is used as direct thematic material or as the model for Copland's own composed folk-like tunes. These melodies are simple, modal, often pentatonic, with straightforward rhythms.
4. **Sudden silence and wide dynamic range** — Copland punctuates his music with complete silence — rests of 2–4 bars — as structural events. The silence represents the openness of the American landscape: the space between events is as important as the events themselves. After a loud section, sudden pp or silence is typical.
5. **Jazz-influenced rhythm — the "hoedown" energy** — In fast movements (Rodeo Hoedown, El Salón México), Copland uses jazz-influenced syncopation: off-beat accents, irregular groupings (3+3+2 in a 4/4 bar), and dance rhythm. This is not jazz harmony — it is jazz rhythm applied to orchestral or piano writing.

## Pattern Directives

**Open-spacing:**
- Bass: root note in the lowest register (C1–C2).
- Next note: 5th above (G2–G3) — at least a 9th above the bass.
- Melody: at the very top, 2 octaves above the bass.
- Middle of the keyboard: empty, or only a single sustained note.
- The gap between bass and melody IS the Copland sound.

**Pandiatonic chord:**
- In C major: all 7 notes stacked: C-D-E-F-G-A-B (as a chord or spread arpeggiation).
- Harmonic "progress": another 7-note stack, but with different spacings.
- No voice-leading rules apply — the diatonic cluster is the harmony.

**Appalachian Spring texture:**
- Solo instrument (clarinet or oboe): folk melody, simple quarter and half notes, p.
- Strings: sustained open 5th or octave harmonics, ppp.
- No bass activity. No movement below the string pads.
- The melody floats in a very quiet, spacious texture.

**Hoedown rhythm:**
- Fast (♩ = 152+), 4/4.
- Groupings: 3+3+2 eighth notes across the bar (accent pattern: 1, 1.5, 2, 2.5, 3.5).
- This creates a syncopated, slightly stumbling energy — the hoedown stumble-step.
- Bass: steady quarter notes (the floor); melody: syncopated pattern above.

## Anti-patterns (what sounds wrong)

- **Dense, lush harmonics.** Copland is lean. A thick orchestral texture with all registers filled is not Copland — it is Mahler or Strauss.
- **European Romantic melody.** A long, arching, decorated Romantic melody is not Copland's melodic language. His melodies are simple, folk-like, direct.
- **Complex chromatic harmony.** Copland's harmony is fundamentally diatonic (with jazz inflections in fast sections). Heavy chromaticism is not his language.
- **Absence of space.** A Copland passage with no rests, no silences, constant texture — has lost the American landscape. Space and silence are structural.
- **Irony or darkness.** Copland's public style (ballets, Fanfare for the Common Man) is genuinely optimistic. The darkness in his late serial works is a different Copland. For the American sound, it is bright, open, earnest.

## ShortScore Field Recommendations

**Open-5th bass:**
- `cb`: `{"p": "C1", "d": "w"}`.
- `vc`: `{"p": "G2", "d": "w"}` — at least a 12th above the bass.
- Middle register: empty, or `vla`: single sustained note at p.
- `"_feel": "Copland open spacing — the American landscape"`.

**Pandiatonic cluster:**
- Write as explicit note array: `{"p": ["C3","D3","E3","G3","A3","B3"], "d": "h"}`.
- All diatonic pitches, no chromatic alterations.

**Folk melody:**
- `"expr": "simply"` — Copland's own instruction.
- Write melody in quarter and half notes only (no complex subdivisions).
- No ornaments.

**Hoedown:**
- `"time_sig": "4/4"`, `"tempo": 160`.
- Accent groupings: mark 3+3+2 explicitly.
- `"art": "staccato"` on all fast notes.
- `"expr": "vivace e energico"`.

**Dynamics:**
- Copland: pppp to ff. Uses pppp (very rare in other composers) for the landscape silence.
- Fanfare sections: ff, brass.
- Folk melody sections: p, solo woodwind.
- `"expr": "freely"` for pastoral sections — slight flexibility in the hymn-like passages.
