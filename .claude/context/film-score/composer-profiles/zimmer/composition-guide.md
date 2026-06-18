# Hans Zimmer — Composition Guide

## Fingerprints
Any section claiming Hans Zimmer's style needs ≥3 of these 5 present.

1. **Hybrid orchestra — electronics integrated with acoustic** — Zimmer's core sound combines synthesizers, electronic textures, and sampled sounds with live orchestra. The electronics and orchestra are not separate layers — they are one integrated palette. A sustained cello note bleeds into a synthesizer pad. A recorded voice becomes a harmonic texture. The hybrid IS the sound, not an addition to it.
2. **Ostinato-driven momentum — the engine** — Zimmer's action and tension cues are built on ostinato patterns: a short rhythmic cell (often 4 notes) repeated relentlessly in the strings or brass, gradually thickening, while other musical elements layer above it. The ostinato IS the emotion — mechanical, inevitable, powerful.
3. **Slow harmonic language — minimal changes, maximum weight** — Zimmer changes harmony slowly (every 4–16 bars) and uses only 2–4 chords in any cue. The chords themselves are simple (often just triads or power chords), but the harmonic stasis gives each chord enormous weight. The Interstellar score uses sustained single notes for minutes at a time.
4. **BRAAAM — the modern climactic sound** — The massive, distorted, low-frequency horn blast (the "Inception BRAAAM," extended through Interstellar, Dunkirk) is Zimmer's signature climactic sound. It is not a chord or a melody — it is a sonic event, a physical impact. It combines brass, synthesizer bass, and electronics into a single wall of sound.
5. **Emotional directness — the score tells you what to feel** — Zimmer's scores are emotionally direct in a way that Classical music never is. The "sad" cue sounds sad using every tool available. The "heroic" cue sounds heroic. The emotional effect is the goal; the technical means are in service of it. This is film-scoring pragmatism.

## Pattern Directives

**Ostinato tension build:**
- Choose a 4-note rhythmic pattern: ♩ ♪ ♪ ♩ (or ♪ ♪ ♩ ♪ ♪ ♩).
- String section: play this pattern at ff, all notes the same pitch (power chord on one note).
- Every 4 bars: add one more string section (or brass section) doubling the pattern.
- After 16 bars: full orchestra on the pattern, fff.
- The build IS the cue.

**Slow harmonic change:**
- Chord 1: C minor (or power-chord C-G). Hold for 8 bars.
- Chord 2: Ab major. Hold for 8 bars.
- Chord 3: Bb major. Hold for 8 bars.
- Return to C minor.
- The minimal harmonic change gives each chord geological weight.

**Hybrid texture:**
- Strings: sustained chord, pp, held throughout.
- Electronics layer: sustained synthesizer pad on the same pitch, pp, slightly different timbre.
- Together: the two blend — neither is alone; neither dominates.
- `"_feel": "hybrid pad — strings and synthesizer as one texture"`.

**Emotional "heart" layer:**
- Above the ostinato and harmonic pad: one solo melody, simple, in a solo instrument or voice.
- The melody is 4–8 bars, stepwise, clearly "sad" or "heroic" in character.
- This is the "human" layer above the mechanical bass.

## Anti-patterns (what sounds wrong)

- **Complex polyphony.** Zimmer's textures are layered but not contrapuntal. Independent melodic lines in different instruments (Bach-style) are not his language.
- **Sophisticated harmonic movement.** A Zimmer cue with many chord changes is atypical. His power comes from harmonic stasis.
- **Chamber-scale intimacy.** Zimmer writes at cinematic scale — large forces, large dynamics. Intimate chamber-music textures are not his primary language.
- **Conventional Classical form.** Sonata form, development sections, formal recapitulation — these Classical structures don't appear in Zimmer. His cues are linear, not cyclical.
- **Academic counterpoint.** Voice-leading rules, prepared dissonances, proper resolutions — these belong in Baroque counterpoint class, not in Zimmer.

## ShortScore Field Recommendations

**Ostinato strings:**
- `vln1`/`vln2`/`vla`/`vc`: all playing the same rhythmic pattern, same pitch or power-chord.
- Write the pattern explicitly: 4 measures showing the full rhythmic cell.
- `"_feel": "ostinato engine — this pattern continues for [N] bars"`.
- Gradually add voices with `"_feel": "bars 9–12: add brass doublings"`.

**Hybrid pad:**
- `str`: sustained chord, pp, `"art": "legato"`.
- `"synth"` or `"pad"`: same pitch, pp (note: WMN may not support synth directly — use `"_feel"` to document).
- `"_feel": "hybrid texture — strings and synthesizer pad as one blended sound"`.

**BRAAAM:**
- `tbn`/`tba`: `{"p": "Bb1", "d": "w", "dyn": "fff", "art": "marcato"}` — the lowest register.
- All brass: unison on this note.
- `"_feel": "BRAAAM — the wall of sound, orchestral impact"`.

**Dynamics:**
- Zimmer: pp (hybrid pad) to fff (climax). The range is extreme.
- Slow build from pp to fff over 32–64 bars is his primary dynamic device.
- `"expr": "intensamente"` for emotional peaks.
- No expression markings for mechanical sections — the emotion IS the lack of expression.
