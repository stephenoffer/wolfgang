# Dvořák — Composition Guide

## Fingerprints
Any section claiming Dvořák's style needs ≥3 of these 5 present.

1. **Pentatonic/folk melody — the tune that everyone knows** — Dvořák's melodies have the quality of folk songs: simple, memorable, singable, often pentatonic or hexatonic. They feel like they could have existed before Dvořák wrote them. This is not a limitation — it is a specific skill: writing original melodies that sound as if they have always existed.
2. **Furiant and Dumka — Czech dance forms as structural units** — The Furiant is a fast (Presto/Vivace) dance in 3/4 with hemiola (cross-rhythm between 3/4 and 2/4) and strong, accented downbeats. The Dumka is a slow, melancholy Ukrainian/Czech form that alternates between a slow, lyrical section and a faster, lively one — mourning and dancing in the same breath. These two forms are Dvořák's most distinctive structural contributions.
3. **Flat-VII chord (Mixolydian) as characteristic color** — In major keys, Dvořák regularly uses the chord built on the flat-7th degree (in C major: Bb major chord). This chord has a folk/modal quality — it sounds like it belongs in a village square, not a concert hall. Combined with the tonic, it gives a specifically Bohemian color.
4. **Richly lyrical slow movements — the American idiom** — Dvořák's Largo/Andante movements (especially the New World Symphony's Largo) are his most personal: a single sustained melody in a solo instrument (cor anglais, cello, violin), pp to p, harmonized with a "warm" but not lush accompaniment. The melody is long, arching, deeply felt.
5. **American pentatonic color (late Dvořák)** — After his American period (1892–1895), Dvořák's pentatonic melodies took on an African-American spiritual and Native American inflection: gapped scales with no 4th or 7th degree, a specific melancholic-joyful character. This is not "Czech" Dvořák — it is the synthesis that produced the New World Symphony.

## Pattern Directives

**Folk-style melody:**
- Choose a pentatonic scale: C-D-E-G-A (no F, no B).
- Write an 8-bar melody using only these pitches.
- The melody should have a clear question-answer structure (first 4 bars rise; last 4 bars descend to the tonic).
- Harmonic support: only tonic and dominant (C and G). No complex chords needed — the melody does the work.

**Furiant (Czech dance):**
- 3/4 time, fast (♩ = 126–160).
- Bars 1–2: melody in 3/4 meter (3 clear beats).
- Bars 3–4: same melody but rhythmically grouped as 2+2+2 eighth notes — now 2/4 feel against 3/4 notation. Hemiola.
- Bars 5–6: return to clear 3/4.
- The oscillation between 3/4 and implied 2/4 IS the Furiant character.

**Dumka:**
- Section A: slow (Andante or Lento), minor key, deeply lyrical. Solo instrument, pp.
- Section B: fast (Vivace or Presto), major key, dance-like. Full ensemble, f.
- Return to A: exact or varied repeat of the slow section.
- The two characters must be genuinely different: the contrast is the point.

**bVII chord:**
- In C major: Bb major chord (Bb-D-F) as a phrase ending chord (bVII→I).
- The Bb chord has a folk-modal, unpretentious quality. It doesn't create tension — it creates a specific color.

## Anti-patterns (what sounds wrong)

- **Sophisticated harmonic language.** Dvořák's harmony is functional and straightforward. Secondary dominants, augmented chords, chromatic saturation — these belong to Wagner, not Dvořák.
- **Emotional complexity or irony.** Dvořák's emotional language is direct: joyful, melancholy, energetic, nostalgic. No irony, no subtext, no Schumannesque inner worlds.
- **Thin, chamber-like textures in orchestral writing.** Dvořák's orchestration is full-bodied, warm, with clear doublings. Spare orchestration is reserved for solo melodic moments.
- **Abstract, non-melodic writing.** Every Dvořák passage has a tune. Development sections still have tunes. There is always a melody somewhere.
- **Absence of folk character.** A Dvořák piece without a folk-like melody (pentatonic, modal, singable) has lost his defining characteristic.

## ShortScore Field Recommendations

**Pentatonic melody:**
- Write every note explicitly in the pentatonic scale.
- `"_feel": "pentatonic folk melody — could have been written by no one and everyone"`.

**Furiant hemiola:**
- Write in 3/4 but mark the hemiola with accent shifts.
- `"art": "accent"` on beats 1 and 3 of the first measure; beats 2 and 4 of the second.
- `"_feel": "hemiola — 2/4 feel against 3/4 notation"`.

**Dumka contrast:**
- Use explicit `"tempo"` field changes between slow and fast sections.
- `"expr": "mesto"` (sad) for slow section; `"expr": "vivace"` for fast.

**Dynamics:**
- Dvořák's range: pp to ff. Most music lives between p and f.
- `"expr": "cantabile"` for all melodic sections.
- `"expr": "furiant"` for the Czech dance sections.
