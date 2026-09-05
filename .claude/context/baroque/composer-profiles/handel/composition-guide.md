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

---

## Composing a Handel phrase: step by step

The organising fact is scale, not intricacy. If the inner parts are as busy as
the outer ones, the grandeur is gone and you have written Bach.

### Step 1 — Choose the ground plan before the notes

A movement is usually one of three: a fugue on a single subject, a homophonic
declamation, or a ground bass with varied material above. Choosing settles most
later decisions.

### Step 2 — Write the bass first, and let it walk

```json
"walking_bass": [
  {"p": "D2", "d": "q"},
  {"p": "C#2", "d": "q"},
  {"p": "B1", "d": "q"},
  {"p": "A1", "d": "q"},
  {"p": "G1", "d": "q"},
  {"p": "F#1", "d": "q"},
  {"p": "E1", "d": "q"},
  {"p": "A1", "d": "q"}
]
```

A descending tetrachord in even quarters. Under it, one chord per bar or per
two — Handel prolongs where Bach moves.

### Step 3 — Put a singable, leaping melody over it

Wider intervals than Bach's and more vocal in shape: a rising fourth or fifth,
then a stepwise descent filling it.

```json
"aria_melody": [
  {"p": "D5", "d": "dq", "art": "legato"},
  {"p": "A4", "d": "e"},
  {"p": "B4", "d": "q"},
  {"p": "C#5", "d": "q"},
  {"p": "D5", "d": "h"},
  {"p": "C#5", "d": "q"},
  {"p": "B4", "d": "q"},
  {"p": "A4", "d": "h"}
]
```

### Step 4 — Sequence it, exactly

Handel builds by sequence more than by development. State the idea, restate it a
step or a third lower, **transposed exactly**. Varying a sequence is the wrong
idiom.

```json
"sequence_step_down": [
  {"p": "C5", "d": "dq"},
  {"p": "G4", "d": "e"},
  {"p": "A4", "d": "q"},
  {"p": "B4", "d": "q"},
  {"p": "B4", "d": "dq"},
  {"p": "F#4", "d": "e"},
  {"p": "G4", "d": "q"},
  {"p": "A4", "d": "q"}
]
```

### Step 5 — Terrace the dynamic; never taper it

```json
"echo_pair": [
  {"p": ["D4", "F#4", "A4"], "d": "h", "dyn": "f"},
  {"p": ["D4", "F#4", "A4"], "d": "h", "dyn": "p"}
]
```

The phrase, then the same phrase softer. That is the period's dynamic
vocabulary. No hairpins.

### Step 6 — Stop everything before the final cadence

A grand pause, then the cadence. Handel uses it in every chorus and it costs
nothing to write.

---

## Checking a finished phrase

- Is the harmonic rhythm slow enough — one chord a bar or slower?
- Are the sequences exact transpositions?
- Are the inner parts quieter than the outer ones?
- Is there a hairpin anywhere? There should not be.
