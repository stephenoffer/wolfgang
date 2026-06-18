# Fauré — Composition Guide

## Fingerprints
Any section claiming Fauré's style needs ≥3 of these 5 present.

1. **Modal harmony within tonal framework — the slipping tonic** — Fauré uses Dorian, Mixolydian, and Lydian modal inflections constantly, creating a harmonic language that is tonal (has a clear tonic and harmonic motion) but never quite "Classical" — the flat-7th appears without being a dominant preparation, the raised 4th gives a Lydian shimmer. The tonic "slips": you can feel it shift slightly under your feet without ever disappearing.
2. **Gentle rhythmic displacement — the nocturne pulse** — Fauré's accompaniment is almost always a gentle, flowing triplet or eighth-note figure that creates a rhythmic haze: the beat is present but soft, cushioned. This is the "night music" of French romanticism — not Bartók's Night Music (no darkness) but the sound of Parisian late evenings, soft lamplight, the Seine at dusk.
3. **Long melodic line with subtle modal inflection** — Fauré's melodies are long (12–16 bars), stepwise, and have one moment of unexpected modal color (a Dorian raised 6th, a Phrygian fall) that gives the otherwise conventional melody its distinctive character. The melody is lovely before the inflection; unforgettable after it.
4. **Harmonic non-resolution — the elided cadence** — Fauré systematically avoids full V→I cadences at phrase endings. His phrases end on half cadences, deceptive cadences (V→VI), or simply continue without closing. The music flows without punctuation — sentences that don't end, only continue.
5. **Intimacy as primary aesthetic — chamber scale** — Even when writing for orchestra (Pelléas et Mélisande, Requiem), Fauré maintains a chamber-music intimacy: the dynamic range rarely exceeds mf, the textures are transparent, the emotional language is private rather than public. He never shouts; he whispers.

## Pattern Directives

**Modal harmonic color:**
- In D major: use B natural instead of Bb (Dorian) — the characteristic sharpened 6th.
- In G major: use F natural instead of F# (Mixolydian) — the characteristic flat-7th.
- These modal notes appear as passing tones in the melody or as chord roots.
- The effect: the key feels stable but subtly "off" — familiar yet foreign.

**Nocturne accompaniment:**
- 9/8 or 6/8 time: arpeggiated broken chord in triplet eighths, LH.
- Beat distribution: bass note on beat 1 of each triplet group; arpeggiated 5th and 3rd on beats 2–3.
- Dynamic: p throughout, no accent on any beat.
- The texture should feel like breathing, not like pulse.

**Long melody with inflection:**
- Write 8 bars of conventional, beautiful diatonic melody.
- At bar 9: introduce the modal note — a Dorian 6th or a Mixolydian 7th — as the main melodic pitch for one beat.
- Continue conventionally for bars 10–16.
- The single modal note makes the melody distinctively Fauré.

**Avoided cadence:**
- Approach the end of a phrase: melody descends to the 2nd degree (D in C major), implying V→I resolution.
- Instead: bass moves to A (VI) — deceptive cadence.
- The phrase doesn't end — it redirects, continues.

## Anti-patterns (what sounds wrong)

- **Emotional excess.** Fauré is not Tchaikovsky. His music does not weep or thunder. The emotional temperature is warm, slightly melancholy, always contained. A Fauré climax is an inner warmth, not an outburst.
- **Loud dynamics.** Fauré's music rarely exceeds mf. A fortissimo in Fauré is reserved for extraordinary moments and brief.
- **Clear cadential resolution.** If the phrase ends with a full V→I cadence that sounds closed and satisfied, it doesn't sound like Fauré.
- **Germanic density.** Fauré's textures are light. The French quality is transparency, airiness, clarity. Dense string doublings, thick brass, complex inner-voice counterpoint — these belong in the Rhine, not the Seine.
- **Programmatic drama.** Fauré doesn't tell stories or depict events. His music is atmospheric, emotional, purely musical. Narrative or programmatic elements are not his language.

## ShortScore Field Recommendations

**Nocturne texture:**
- `lh`: broken-chord triplet pattern in 9/8: `{"p": "G2", "d": "e"}`, `{"p": "D3", "d": "e"}`, `{"p": "B3", "d": "e"}` per beat group.
- `rh`: melody, one note per beat, `"art": "legato"`.
- `"dyn": "p"` throughout.

**Modal inflection:**
- Mark modal notes: `"_feel": "Dorian raised 6th — the characteristic Fauré shimmer"`.
- These are single notes in an otherwise diatonic melody, not chord changes.

**Harmony:**
- Write chord voicings explicitly as note arrays — 3 or 4 voices, transparent spacing.
- Deceptive cadence: approach V, arrive at VI — write both chords explicitly.
- `"_feel": "avoided cadence — the phrase continues rather than closes"`.

**Dynamics:**
- Fauré: pp to mf. `"dyn": "f"` only at extended climactic passages; `"dyn": "ff"` very rare.
- `"expr": "dolce"` for melodic entries.
- `"expr": "très doux"` (very soft) — Fauré's typical marking.
