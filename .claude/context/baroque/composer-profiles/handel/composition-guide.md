# Handel — Composition Guide

## Fingerprints
Any section claiming Handel's style needs ≥3 of these 5 present.

1. **Grand choral/ensemble gesture** — Homophonic arrival after polyphonic buildup. The "Hallelujah effect": voices unite in rhythmic unison at the emotional peak. Even in instrumental writing, the tutti statement has this quality — all voices together on a memorable rhythm.
2. **Immediately memorable theme** — The theme states itself completely in 4 bars and could be sung by anyone after one hearing. No Baroque spinning — the theme is a statement, not a generator. Strong opening interval (often a fifth or sixth upward), clear rhythmic identity, landing on a cadence.
3. **Da capo architecture** — A section, B section (contrasting, usually more chromatic or in a related minor key), return of A (often with ornamental elaboration). Even in instrumental writing, this ABA thinking shapes the overall arch.
4. **Sequences that build dramatic momentum** — Sequences (usually descending thirds or circle of fifths) used not just for development but for emotional buildup toward a climax. The sequence intensifies; the resolution releases.
5. **Dramatic contrast between major and minor** — Handel shifts between parallel major and minor (C major → C minor) for dramatic effect in a way Bach typically does not. A joyful section turning to minor for a sudden shadow, then returning to major triumphant.

## Pattern Directives

**When writing choral texture:**
- SATB voices moving in rhythmic unison for climax moments (homophony).
- Contrapuntal sections (fugue entries) used for buildup before homophonic arrival.
- Bass voice provides the harmonic anchor; soprano carries the primary melody.
- Inner voices (alto, tenor) fill in thirds and sixths — they don't need independent melodic interest.

**When writing aria (solo + continuo):**
- Melody in long arching lines over a steady bass. Less Baroque spinning, more Italian bel canto.
- Bass line is a walking bass or repeated rhythmic figure, not an independent melody.
- Ornaments on the longest structural notes (cadences, phrase peaks).

**When writing concerto grosso:**
- Tutti (ripieno) statements: homophonic, strong, direct.
- Solo (concertino) episodes: more elaborate, contrapuntal, ornamental.
- Return of tutti material provides structural anchoring.

**Harmonic approach:**
- Direct functional harmony. IV-V-I cadences in every phrase.
- Neapolitan (bII) used for sudden pathos — effective in slow movements.
- Circle-of-fifth sequences (vi → ii → V → I) for building momentum.

## Anti-patterns (what sounds wrong)

- **Continuous Baroque spinning.** Handel's melodies state themselves and breathe — they don't generate endless figuration. A melody that never lands is not Handel.
- **Counterpoint for its own sake.** Handel uses counterpoint as a means to a dramatic end (building to a homophonic climax), not as the goal itself. A fugue that never arrives at a unison statement sounds un-Handelian.
- **Ambiguous themes.** Handel's themes are unambiguous, direct, memorable. If a listener couldn't hum the theme after hearing it once, it's not idiomatic.
- **Chromaticism without dramatic purpose.** Handel uses chromatic harmony (diminished sevenths, Neapolitan) for specific emotional moments — not as general texture.
- **Quiet, understated climaxes.** Handel's climaxes are loud, direct, and celebratory. A subdued climax in f with no choral statement is anti-Handelian.

## ShortScore Field Recommendations

**Ensemble:**
- Chorus: `sop`, `alt`, `ten`, `bas` — unison for tutti, independent for fugue sections
- Aria: solo instrument (melody) + `vc`/`kbd` (continuo)
- Orchestral: strings (homophonic tutti) + occasional woodwind/brass color

**Melody writing:**
- Write the complete melodic statement first (4–8 bars), then harmonize.
- Strong rhythmic identity: dotted rhythms for grandeur, even quarters for dignity, triplets for momentum.
- Landing cadences on every phrase — no open-ended spinning.

**Dynamics:**
- Forte for tutti, piano for solo episodes — terraced, not gradual.
- Sforzando at unison rhythmic arrivals.

**Ornaments:**
- Trills at all cadence arrivals.
- Turns in melodic peaks of slow movements.
- Da capo return: add ornamental elaboration (additional runs, trills) to the A section repeat.
