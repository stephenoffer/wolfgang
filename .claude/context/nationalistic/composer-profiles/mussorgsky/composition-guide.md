# Mussorgsky — Composition Guide

## Fingerprints
Any section claiming Mussorgsky's style needs ≥3 of these 5 present.

1. **Raw, unpolished harmonic language — intentional "wrong" notes** — Mussorgsky deliberately avoided the smooth voice-leading rules of European academic harmony. His chord connections can be abrupt, his parallel fifths deliberate, his unresolved dissonances intentional. This "wrongness" is not ignorance — it is a Russian aesthetic: the raw, the unmediated, the folk voice that doesn't care about German counterpoint rules.
2. **Speech-melody — vocal rhythm following natural Russian speech** — Mussorgsky's vocal writing in Boris Godunov and Songs follows the natural rhythm and inflection of spoken Russian, not the conventions of Italian opera. Long notes on important syllables, short notes on unstressed syllables, irregular phrase lengths determined by the text, not the music. This creates a new kind of vocal melody — more declamatory than lyrical.
3. **Whole-tone and octatonic fragments** — Before Debussy made whole-tone harmony fashionable, Mussorgsky used whole-tone fragments and octatonic scales as coloristic devices for the supernatural, demonic, or mysterious. The Night on Bald Mountain, Boris's hallucination, Baba Yaga — all use these scales not as systematic language but as brief, specific coloristic events.
4. **Modal Russian church idiom — bells and liturgy** — The Orthodox Christian liturgical tradition is embedded in Mussorgsky's writing: open 5th drone basses, parallel 5th chord movements, slow-moving choral harmonies with no leading tone. The "Boris" coronation scene, the Great Gate of Kiev — these draw directly from Russian church music, not from Western tonal harmony.
5. **Programmatic specificity — portraits and places** — Pictures at an Exhibition is the paradigm: each piece is a specific portrait, place, or scene, described with specific musical material unique to that subject. Mussorgsky doesn't write "atmospheric" music — he writes specific music about specific things. The "Promenade" theme (walking between pictures) is a structural idea about a specific action.

## Pattern Directives

**Raw harmonic connection:**
- Move from one chord to another without preparation or voice-leading: E major → C major (parallel thirds in the outer voices).
- Use parallel 5ths deliberately: bass moves C→G, inner voice also moves C→G (one octave higher).
- The raw connection IS the style. Don't smooth it out.

**Bell texture (Boris/Kiev):**
- Open 5th drone in the bass: C2–G2, sustained.
- Slow-moving chord in the inner voices: C major → F major → C major (plagal, no dominant).
- Melody: a simple, folk-like stepwise line in the upper register.
- Dynamic: beginning p to pp, building slowly to ff (the bells accumulate).

**Supernatural color (whole-tone/octatonic):**
- Whole-tone scale: C-D-E-F#-G#-A# (no semitones).
- For 4–8 bars: write melody and harmony using only these pitches.
- The effect: floating, rootless, slightly wrong — perfect for the supernatural.
- Return to normal diatonic after: the contrast emphasizes both.

**Speech-melody (if setting text or writing vocal style for instruments):**
- Determine the natural stress pattern of the phrase as if spoken.
- Assign long notes to stressed syllables; short notes to unstressed.
- Phrase lengths: irregular — 5 bars, 7 bars, 3 bars — determined by text rhythm, not musical convention.

## Anti-patterns (what sounds wrong)

- **Smooth, academic voice-leading.** If the chord connections are perfectly smooth with no parallels and all voices correctly resolved, it doesn't sound like Mussorgsky.
- **Italian bel canto melody.** Long, arching, ornamental melody is not Mussorgsky. His melody is short, declamatory, speech-like.
- **German formal structure.** Sonata form, development section, formal recapitulation — these are not Mussorgsky's tools. His forms are programmatic or sectional.
- **Absence of Russian color.** The bell bass, the church mode, the speech-rhythm — without at least one of these specifically Russian elements, the music could be written by anyone.
- **Consistent "nice" harmony.** Mussorgsky has ugly moments by choice. A passage that is harmonically well-behaved throughout is not Mussorgsky.

## ShortScore Field Recommendations

**Bell texture:**
- `cb`: `{"p": "C1", "d": "w"}`, `{"p": "G1", "d": "w"}` — open 5th drone.
- `vc`: sustained inner voices, slow whole-note movement.
- `tbn`/`hn`: brass sustaining the church-mode chords.
- `"_feel": "Russian Orthodox bells — open 5th resonance, no leading tone"`.

**Whole-tone passage:**
- Mark the scale: `"_feel": "whole-tone — supernatural, floating, no tonal center"`.
- Write all melodic and harmonic notes explicitly within the whole-tone scale.
- Transition back to diatonic: a single chromatic note that doesn't fit.

**Raw parallel motion:**
- Document deliberately: `"_feel": "parallel 5ths — intentional Russian rawness"`.
- Don't voice-lead. Move the entire chord in parallel.

**Dynamics:**
- `"dyn": "pp"` to `"dyn": "fff"` — Mussorgsky's Bell passages build to fff.
- `"expr": "pesante"` (heavy) for the Boris/Kiev ceremonial passages.
- `"expr": "misterioso"` for supernatural sections.
