# Sibelius — Composition Guide

**CRITICAL: Specify early or late Sibelius — these are different aesthetics.**

## Fingerprints (Late Sibelius — 7th Symphony, Tapiola, Voiless — the definitive voice)
Any section claiming Sibelius needs ≥3 of these 5 present.

1. **Frozen pedal stasis** — Entire passages built over a sustained single pitch or harmonic interval in the bass (pedal point), while harmonies and melodic fragments appear and disappear above it. Time feels suspended, not moving. The bass note is not a tonic preparation — it IS the tonal center, held without resolution needed, like a held note in an empty room.
2. **Motivic cells that don't "develop" — they accumulate** — Sibelius fragments his themes into 2–3 note cells and repeats them in different instruments at different dynamic levels, gradually accumulating density until the theme emerges complete. The theme is not developed FROM the opening — it ARRIVES through accumulation of its own fragments.
3. **Nordic modal language** — Modal scales (especially Dorian and Aeolian) rather than standard major/minor, combined with specific harmonic moves: bVII→I (lowered 7th to tonic), IV→I (plagal), and modal mixture (major and minor simultaneously). The "cold" Nordic quality comes from the specific intervals in these modes — no leading tone, no dominant pull.
4. **Orchestral texture as landscape** — The orchestral texture doesn't change for dramatic reasons — it changes to describe something physical (mist thickening, wind strengthening, forest deepening). Texture IS the musical narrative, not just supporting it.
5. **Structural organicism — the form grows** — A Sibelius movement doesn't announce its themes and then develop them. Fragments appear, repeat, grow, join together, and at some point you realize the full theme has been present all along in pieces. The form is biological — it grows, it doesn't argue.

## Pattern Directives

**Pedal stasis:**
- Choose a tonic pitch. Sustain it in the bass (low strings, low brass, or timpani) for 8–24 bars.
- Above the pedal: slowly changing harmonies (write each chord change as a new event, not a progression — these are harmonic colors, not functions).
- Melodic fragments: appear briefly in solo instruments (flute, oboe), 2–4 notes, then disappear. Not themes yet — hints.
- Dynamic: ppp to p throughout the pedal section.

**Accumulation of theme from fragments:**
- Write a complete 8-bar theme. Now FORGET IT.
- Instead: write bar 1 of the theme in the flute, pp, alone.
- 4 bars later: write bars 1–2 in the clarinet.
- 4 bars later: write bars 1–3 in the strings.
- Eventually (after 24–32 bars): the full theme arrives in the full orchestra.
- This is the Sibelius entrance — the theme emerges from itself.

**Nordic modal harmony:**
- Key of E minor (modal, no leading tone D#): use natural D instead of D#.
- Harmonic moves: i → VII → VI → VII → i (Aeolian). No V chord pulling to the tonic.
- bVII → I cadence: the most Sibelian cadence. D major → E minor (in E mode) — no tension, just arrival.
- Major and minor together: C major chord under an E minor melody, both present.

**Orchestration as landscape:**
- Mist/morning: muted strings tremolo (pppp), sustained horn pedal, solo flute fragment.
- Forest deepening: strings add in layers (vln2, then vla, then vc), each with the same slow sustained pitch.
- Storm: full orchestra, brass melody against string figuration, timpani providing pulse rather than accent.

## Fingerprints (Early Sibelius — Finlandia, Violin Concerto, more Romantic)
Early Sibelius fingerprints:
1. Strong nationalistic melody (pentatonic-influenced, folk-like)
2. Clear orchestral rhetoric (Romantic development, clear themes)
3. Dramatic orchestral climaxes (not the late-period accumulation)
4. Patriotic/heroic character (Finlandia, En Saga)
5. Violin Concerto — extremely demanding virtuosity combined with folk melody character

## Anti-patterns (what sounds wrong)

- **Regular 4-bar phrases.** Sibelius's late music has irregular phrase lengths determined by organic growth, not formal convention.
- **Obvious development.** Taking a theme and modifying it through standard Beethoven-style development is wrong for late Sibelius. The theme shouldn't be "developed" — it should "appear."
- **Conventional harmonic resolution.** A V→I cadence sounds Classical, not Sibelian. The plagal cadence (IV→I) and the modal bVII→I are his harmonic signatures.
- **Constant texture change.** Sibelius holds textures for long stretches. A texture that changes every 4 bars is busy, not Nordic.
- **Warm, Romantic orchestral sound.** Sibelius's late sound is cold, spare, sometimes bleak. Lush string vibrato and warm orchestral blend belong to Tchaikovsky.

## ShortScore Field Recommendations

**Pedal stasis:**
- `vc`/`cb`: `{"p": "E1", "d": "w", "dyn": "pp"}` — very long values, sustained.
- Solo flute fragments: `{"p": "B5", "d": "q"}`, `{"p": "A5", "d": "h"}` — short, isolated.
- No rhythmic pulse in any voice. Each event is placed in time, not pulsed.

**Modal harmony:**
- Write harmonies as simultaneous note arrays (not chord symbols): `["E3","G3","B3"]` for E minor, `["D3","F#3","A3"]` for D major (bVII in E mode).
- Move between these by stepwise voice-leading in the inner voices.

**Dynamics:**
- Late Sibelius lives in ppp to mp range for most of its duration.
- Climaxes: f to ff, but brief — immediately return to pp.
- `"expr": "misterioso"` for pedal passages.
- `"expr": "grandioso"` for brief climactic arrivals.
