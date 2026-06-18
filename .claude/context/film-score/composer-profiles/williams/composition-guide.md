# John Williams — Composition Guide

## Fingerprints
Any section claiming John Williams's style needs ≥3 of these 5 present.

1. **Leitmotif system — Wagnerian in cinema** — Williams uses the Wagnerian Leitmotif system with more discipline and transparency than almost any post-Wagner composer. Each character, object, concept, or relationship in the film has a specific musical tag (3–8 notes, specific rhythm, specific harmony). These appear, combine, and transform as the film's narrative develops. The Leitmotif is not background — it IS the storytelling.
2. **Post-Romantic orchestral mastery — Holst, Korngold, Strauss** — Williams's orchestral language is deliberately Late Romantic: Holst's planetary scale, Korngold's Hollywood grandeur, Strauss's tone-poem specificity. He writes for the full symphony orchestra with complete command: brasses for heroism and power, strings for emotion, woodwinds for character and nature, percussion for drama and rhythm.
3. **March and fanfare idiom for heroism** — The Williams heroic sound: brass fanfare (trumpets, horns in unison or harmony), dotted-note rhythms, major key, fff. Star Wars main theme, Indiana Jones, Imperial March — all are built on this archetype. The fanfare is not decoration — it carries the emotional content of heroism, adventure, or threat.
4. **Lyrical soloistic "heart" themes** — Contrasting with the heroic fanfares: intimate, singable melodic themes for the emotional center of the story (the love theme from Schindler's List, the boy's theme in E.T., Hedwig's Theme). These themes are long, arching, with simple but effective harmonic support. They are the music that audiences remember.
5. **Specific harmonic fingerprints — the Williams sound** — Several characteristic harmonic moves: (1) the bVI→I "magical" cadence (Db major → C major); (2) modal mixture with lowered 3rd or 7th for ominous effect; (3) Lydian raised 4th for wonder and discovery (the Superman fanfare); (4) rapid modulation by half step for dramatic escalation.

## Pattern Directives

**Heroic fanfare:**
- Brass section: horns and trumpets in unison or close harmony.
- Dotted rhythms: ♩. ♪ | ♩ — the long-short-long of the fanfare.
- Key: major, no ambiguity.
- Dynamic: ff to fff.
- Range: trumpets in middle register (G4–D5), not screaming high.

**Leitmotif statement:**
- State the theme in its "home" instrumentation first (e.g., strings for hero's theme; brass for villain).
- Every subsequent appearance: transform (faster, slower, inverted, harmonized differently) while preserving the core interval shape.
- Document each transformation: `"_feel": "hero theme — transformed to minor, fragmented — the hero is in danger"`.

**Magical bVI→I cadence:**
- In C major: Db major chord → C major chord. One-bar each.
- The Db is completely outside C major — but the move to C gives a "wonder" feeling.
- This cadence works for: magic, discovery, wonder, the supernatural.

**Lyrical heart theme:**
- 16 bars, one arch: begins low, rises over 8 bars to the peak, descends over 8 bars.
- Solo instrument: cello or solo violin (intimate, personal).
- Harmonization: simple but beautiful (I → IV → V → I, with one unexpected chord at the peak).
- Dynamic: p to mf at the peak, returning to p.

**Lydian raised 4th (wonder):**
- In C major: use F# instead of F. The raised 4th creates a "shining" quality.
- Use it at moments of discovery, wonder, or transcendence.

## Anti-patterns (what sounds wrong)

- **Generic background music.** Williams's scores are not background — they are active storytelling. A Williams passage that could play behind anything is wrong.
- **Atonal or serial harmony.** Williams uses the full range of tonal language, including chromatic inflections, but always with a tonal center.
- **Absent Leitmotif structure.** A Williams-style score without specific thematic tags for specific story elements has lost his defining contribution.
- **Electronic or synthesizer sound.** Williams writes for orchestra. Synthesizers and electronic elements are absent from his core language.
- **Undifferentiated loudness.** Williams controls dynamic levels carefully. Not every dramatic moment is fff — many are achieved with pp solo strings or solo woodwind.

## ShortScore Field Recommendations

**Fanfare texture:**
- `tpt1`: melody, ff, dotted rhythm.
- `tpt2`/`hn`: harmony below, ff.
- `timp`: reinforcing the downbeats.
- `str`: sustained ff chord, tremolo if needed.
- `"expr": "maestoso"` or `"expr": "con fuoco"`.

**bVI→I wonder cadence:**
- Bar N: `["Db3","F3","Ab3"]` — Db major.
- Bar N+1: `["C3","E3","G3"]` — C major.
- `"_feel": "bVI→I — the magic arrives"`.

**Leitmotif documentation:**
- Define all themes at the JSON header: `"_themes": {"hero": "G-A-Bb-D-E...", "villain": "..."}`.
- Each appearance: `"_feel": "hero theme — [transformation name]"`.

**Dynamics:**
- Williams: pp to fff — the full range used deliberately.
- `"expr": "nobilmente"` for heroic themes.
- `"expr": "con moto"` for action sequences.
- `"expr": "dolce"` for heart themes.
