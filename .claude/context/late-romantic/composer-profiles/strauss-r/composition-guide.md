# Richard Strauss — Composition Guide

## Fingerprints
Any section claiming Richard Strauss's style needs ≥3 of these 5 present.

1. **Tone poem narrative — music as biography or story** — Strauss doesn't write abstract music. Every major orchestral work has a specific extra-musical program: a character (Don Quixote, Till Eulenspiegel), a philosophical concept (Also sprach Zarathustra), an autobiography (Ein Heldenleben, Symphonia Domestica). The music is cinematic before cinema existed. Every structural event corresponds to a narrative event.
2. **Post-Wagnerian orchestral mastery — 100+ players as a single instrument** — Strauss inherited Wagner's orchestra and expanded it further: quadruple woodwinds, 8 horns, 5 trumpets, strings divided into 16 parts. The orchestral texture can whisper (solo violin harmonics alone) or thunder (full orchestra, fff, with extra brass). The range from quietest to loudest, thinnest to thickest, is unprecedented.
3. **Chromatic lushness — the Straussian harmonic swell** — Strauss takes Wagnerian chromaticism and adds Brahmsian richness: thick inner voices, added 9ths and 11ths in chords, chromatic voice-leading in all parts. The result is a specific "lush" sound — harmonically complex, tonally clear, emotionally overwhelming. He always knows where home is, even when the harmony is maximally chromatic.
4. **Ironic self-quotation and musical joke** — Strauss quotes himself, quotes other composers, and quotes common-practice formulas with deliberate incongruity. Till Eulenspiegel's pranks are actual musical pranks: the pompous theme that suddenly falls on its face, the heroic arrival undercut by a comic figure, the solemn chorale turned into a dance. Irony is a structural element, not a decorative one.
5. **Late style — autumnal lyricism (Der Rosenkavalier, Four Last Songs)** — In his mature and late works, Strauss abandons programmatic complexity for pure lyrical beauty: long, arching, harmonically rich vocal or string melody, supported by warm orchestral texture. The chromaticism serves melody, not drama. This is his most approachable and most beautiful voice.

## Pattern Directives

**Tone poem narrative structure:**
- Define the program in advance: what happens, in what order, what it means.
- Each narrative event = distinct musical section with its own tempo, character, instrumentation.
- Leitmotif-style tags for key characters or concepts (but less systematic than Wagner — more like recurring themes).
- Transitions between sections: abrupt cuts for drama (Till's prank), or long transitions for meditative sections (Zarathustra's sunrise).

**Orchestral amplitude:**
- Maximum texture: all instrument families simultaneously, differentiated by role.
  - Strings: melody or sustained harmony.
  - Woodwinds: melodic counter-line or harmonic filling.
  - Brass: structural arrivals or melodic statement.
  - Timpani + percussion: rhythmic support.
- Minimum texture: solo woodwind or solo string, pppp, all other instruments silent.
- The contrast between maximum and minimum IS the orchestral drama.

**Chromatic lushness:**
- Add 9ths and 11ths to all tonic and dominant chords: not C-E-G but C-E-G-B-D.
- Inner voices: move chromatically between chord tones (C-E-G → C-Eb-G: the inner E becomes Eb).
- The outer voices (bass and soprano) move diatonically; the inner voices are chromatic.

**Autumnal melody (late style):**
- Long phrases: 12–16 bars without internal cadence.
- Melody: rises slowly to a peak in bar 10–12, then descends gently.
- Harmony: warm, chromatic, tonally clear — Db major with added 9ths and 6ths.
- Scoring: solo violin or high strings; low brass sustaining below; no rhythmic pulse.

## Anti-patterns (what sounds wrong)

- **Abstract, non-programmatic writing.** Strauss almost always has a program. Music that is purely formal (sonata without a story) loses his defining purpose.
- **Sparse orchestration.** Even in "chamber" moments, Strauss maintains at least 3 independent orchestral layers. He never writes as sparsely as Brahms or late Beethoven.
- **Harmonic timidity.** A Strauss passage that stays in one key and uses only triads sounds like early 19th century. His harmony is always enriched, always layered.
- **Short climaxes.** A Strauss climax builds for 30–60 bars before arrival. A sudden fortissimo without preparation is not Strauss.
- **Emotional one-dimensionality.** Strauss is complex: heroic and comic, tender and ironic, lush and spare. A passage with only one emotional quality has missed him.

## ShortScore Field Recommendations

**Orchestral texture layers:**
- Write each instrument family explicitly: `vln1`, `vln2`, `vla`, `vc`, `cb`, `fl`, `ob`, `cl`, `bsn`, `hn`, `tpt`, `tbn`, `tba`, `timp`.
- Document each instrument's role: `"_feel": "vln1: melody; hn: harmonic sustain; cl: counter-line"`.

**Chromatic inner voices:**
- Chord progression: write each chord as a note array with 5–7 voices.
- `["C2", "G2", "E3", "B3", "D4", "G4", "B4"]` — C major with 9th, all voices.
- Inner voices move by half-step between chords.

**Late-style melody:**
- `"tempo": 60` or slower.
- `"expr": "sehr innig"` (very intimate) for autumnal passages.
- `"dyn": "p"` throughout; occasional `"dyn": "mf"` at peak.
- Melody: every note explicitly written, full arch documented.
