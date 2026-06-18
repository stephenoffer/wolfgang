# Shostakovich — Composition Guide

## Fingerprints
Any section claiming Shostakovich's style needs ≥3 of these 5 present.

1. **Ironic major-key grotesquerie** — Bright major passages (march tempo, staccato, high piccolo or xylophone, ff) that mean the OPPOSITE of what they seem to sound. The cheerfulness is forced, the brightness is threatening. This is Shostakovich's coded political language: the "jolly" march is a funeral march wearing a mask. If major sounds innocent, it's not Shostakovich.
2. **Obsessive ostinato under chromatic distress** — A mechanical repeated pattern (often a march bass or a pedal figure) continues relentlessly while the upper voices move through increasing chromatic dissonance. The relentlessness IS the oppression — the ostinato continues regardless of what happens above it.
3. **Parody of familiar styles** — Musical quotation or imitation of a recognizable style (Baroque passacaglia, waltz, march, hymn) that is subtly or grotesquely distorted. The style is recognizable but something is "wrong" — the intervals are too wide, the rhythm slightly unstable, the harmonization inappropriate. The wrongness IS the meaning.
4. **Extremely high or extremely low instruments at climaxes** — At emotional peaks, the piccolo screams in its highest register, or the contrabasses play in their lowest. The extreme register creates physical discomfort in the listener — the beauty of the moment is inseparable from its painfulness.
5. **DSCH motif or initials-based cells** — D-Es-C-H (D-Eb-C-B in German notation) — Shostakovich's musical signature. He uses it as the basis for many themes. Even without the exact pitches, his melodic cells often have a specific half-step + major/minor third shape that feels like a signature.

---

## Note-Level Technique 1: The Ironic March (One Wrong Note)

A bright major march, staccato, forte — that carries a threatening subtext. The mechanism: everything looks correct (major key, regular rhythm, march instrumentation) except ONE note that is chromatically "wrong." That note is the crack in the mask. Place it at bar 3 of a 4-bar phrase — after the impression of normality is established.

**D major march, 4 bars, with chromatic intrusion in bar 3:**
```json
{"bar_num": 1, "_feel": "March — cheerful, bright, staccato. The smile is plastered on.", "voices": {
  "vln1": [
    {"p": "D5",  "d": "q",  "dyn": "f",  "art": "staccato"},
    {"p": "E5",  "d": "q",  "art": "staccato"},
    {"p": "F#5", "d": "q",  "art": "staccato"},
    {"p": "D5",  "d": "q",  "art": "staccato"}
  ],
  "vc": [
    {"p": "D3",  "d": "q",  "dyn": "f",  "art": "staccato"},
    {"p": "rest","d": "q"},
    {"p": "D3",  "d": "q",  "art": "staccato"},
    {"p": "rest","d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "vln1": [
    {"p": "G5",  "d": "h",  "art": "staccato"},
    {"p": "F#5", "d": "q",  "art": "staccato"},
    {"p": "E5",  "d": "q",  "art": "staccato"}
  ],
  "vc": [
    {"p": "G3",  "d": "q",  "art": "staccato"},
    {"p": "rest","d": "q"},
    {"p": "G3",  "d": "q",  "art": "staccato"},
    {"p": "rest","d": "q"}
  ]
}},
{"bar_num": 3, "_feel": "Bar 3: the wrong note. Eb instead of E natural. The march continues — nothing stops.", "voices": {
  "vln1": [
    {"p": "D5",  "d": "q",  "art": "staccato"},
    {"p": "Eb5", "d": "q",  "art": "staccato", "_feel": "The wrong note — grotesque, threatening. The march doesn't break stride."},
    {"p": "F#5", "d": "q",  "art": "staccato"},
    {"p": "A5",  "d": "q",  "dyn": "ff", "art": "staccato"}
  ],
  "vc": [
    {"p": "D3",  "d": "q",  "art": "staccato"},
    {"p": "rest","d": "q"},
    {"p": "A2",  "d": "q",  "dyn": "ff", "art": "staccato"},
    {"p": "rest","d": "q"}
  ]
}},
{"bar_num": 4, "_feel": "Normal march resumes — as if nothing happened", "voices": {
  "vln1": [
    {"p": "D5",  "d": "w",  "dyn": "f"}
  ],
  "vc": [
    {"p": "D3",  "d": "h",  "dyn": "f"},
    {"p": "A2",  "d": "h"}
  ]
}}
```
Bars 1–2 and 4: D major, staccato, regular — this is the "normal" march. Bar 3 beat 2: Eb5 (the minor 2nd = chromatic wrong note in D major). The march continues through it without flinching. The Eb5 is the same duration as the other notes (quarter); it's not dramatized; that's the horror. Add snare drum (`sn` part) on beats 2 and 4 for the full ironic march texture.

---

## Note-Level Technique 2: DSCH Motif as Melodic Cell

D–Eb–C–B (in German notation: D–Es–C–H = D–S–C–H = D.Sch = Shostakovich). This 4-note chromatic cell is his musical signature. Intervals: half-step up (D→Eb), minor 3rd down (Eb→C), half-step down (C→B). Total span: a minor 3rd (D to B). Use it as the opening of themes, as the accompaniment figure, in augmentation or retrograde.

**DSCH cell — original, then inverted, then augmented:**
```json
{"bar_num": 1, "_feel": "DSCH — Shostakovich's initials as music. 4 notes, one cell.", "voices": {
  "vla": [
    {"p": "D4",  "d": "q",  "dyn": "mf"},
    {"p": "Eb4", "d": "q"},
    {"p": "C4",  "d": "q"},
    {"p": "B3",  "d": "q"}
  ],
  "vc": [{"p": "D2", "d": "w", "dyn": "p"}]
}},
{"bar_num": 2, "_feel": "Inversion: each interval flipped. D→C# (half step down), C#→E (minor 3rd up), E→F (half step up)", "voices": {
  "vla": [
    {"p": "D4",  "d": "q"},
    {"p": "C#4", "d": "q"},
    {"p": "E4",  "d": "q"},
    {"p": "F4",  "d": "q",  "dyn": "f"}
  ],
  "vc": [{"p": "G1", "d": "w"}]
}},
{"bar_num": 3, "_feel": "Augmentation — same intervals, double duration. DSCH stretched across 2 bars.", "voices": {
  "vla": [
    {"p": "D4",  "d": "h",  "dyn": "mp"},
    {"p": "Eb4", "d": "h"}
  ],
  "vc": [{"p": "D2", "d": "w"}]
}},
{"bar_num": 4, "voices": {
  "vla": [
    {"p": "C4",  "d": "h"},
    {"p": "B3",  "d": "h",  "dyn": "p"}
  ],
  "vc": [{"p": "D2", "d": "w"}]
}}
```
Original cell: D4–Eb4–C4–B3 = H.step up, m3 down, H.step down. Inversion: D4–C#4–E4–F4 = H.step down, m3 up, H.step up. Augmentation: the 4 notes occupy 2 bars (half notes) instead of 1. The cell is the same; the time is different. In development sections, combine: original in one voice, inverted in another, simultaneously.

---

## Pattern Directives

**Ironic march:**
- Tempo: Allegro or faster. Key: major. Dynamic: f to ff.
- Melody: simple, stepwise or with P4/P5 leaps. Staccato articulation.
- Accompaniment: mechanical, regular (one pattern per bar, no variation).
- Instrumentation: piccolo, xylophone, snare drum, brass (trumpets staccato). OR pizzicato strings imitating a mechanical band.
- **The key to irony:** at least one "wrong" note (chromatic note that doesn't belong, an unexpected minor chord in the progression, a rhythm that stumbles). The overall impression is cheerful; something underneath is terrifying.

**Passacaglia/ground bass (Shostakovich's tragedy mode):**
- Repeating bass line (8 bars, chromatic or modal, minor).
- Upper voices: gradually increasing complexity and chromaticism over each repetition.
- Dynamic arc: ppp → ff over 5–6 repetitions.
- The relentlessness of the repeating bass IS the statement.

**Extreme register climax:**
- At the peak: piccolo playing above written C6 (extremely high), OR contrabass below E1.
- The rest of the orchestra at full dynamic.
- The extreme instrument sounds almost broken — this IS the intended effect.

**Slow movement (the real Shostakovich):**
- Adagio or Largo. Strings only, or strings + solo wind.
- Long, sustained melody in the viola or cello (the most expressive string voice).
- The melody is not conventionally beautiful — it has an aching quality, sometimes ugly leaps, sometimes a too-long sustained dissonance.
- Dynamic: p to mp. Never ff in slow movements.

## Anti-patterns (what sounds wrong)

- **Genuine, unironic happiness.** If a major-key passage is straightforwardly, innocently joyful, it's not Shostakovich. His major-key moments are always complicated — either grotesque or bittersweet.
- **Smooth, Romantic orchestral writing.** Shostakovich's orchestral sound is spare, dry, and often deliberately uncomfortable. Lush string doublings and warm orchestral blend are Tchaikovsky, not Shostakovich.
- **Development that "resolves."** Shostakovich's music often ends ambiguously, or ends with the wrong emotion — the C minor symphony ending in "triumphant" C major is read by scholars as forced triumph, not genuine victory.
- **Absence of obsessive repetition.** A Shostakovich passage that varies constantly without ostinato or repetition lacks his characteristic sense of mechanical coercion.
- **Ornamentation for beauty.** Ornaments in Shostakovich (grace notes, trills) are expressive of something uncomfortable — a nervous tic, not a decoration.

## ShortScore Field Recommendations

**Ironic march:**
- `"dyn": "f"` throughout.
- `"art": "staccato"` on all melodic and accompaniment notes.
- Melody: explicit quarter-note and eighth-note values — very regular.
- `"expr": "ironico"` at the beginning of ironic march sections.

**Passacaglia bass:**
- Write the 8-bar bass pattern explicitly (specific chromatic pitches).
- Over each repetition, write new upper voices — explicitly different each time.
- Add `"_feel": "repetition [N] — the walls close in"` annotations.

**Slow movement:**
- `"dyn": "p"` or `"pp"` throughout.
- Solo viola or cello: write the melody note-by-note with specific ornaments (`"orn": "grace:X"`) at moments of anguish.
- `"expr": "dolente"` (grieving) or `"expr": "senza espressione"` (without expression — the numbness is expressive).

**Extreme register:**
- Piccolo: write above C6 — these are the highest notes, barely controllable.
- Contrabass: write below E1 — these are below the instrument's ideal range, which creates strain.
- The strain IS the compositional intent.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #5: Ascending Sequence — Shostakovich uses escalating sequences in scherzo development
- Technique #3: Lament Bass — the passacaglia bass is a lament bass variant (chromatic descent)
- Technique #12: Dominant Pedal — Shostakovich's unresolved dominant pedals in tragic adagios
- Technique #15: Dorian Mode phrase — Shostakovich uses Dorian and other modes in folk-inflected passages
