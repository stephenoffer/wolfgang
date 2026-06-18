# Vivaldi — Composition Guide

## Fingerprints
Any section claiming Vivaldi's style needs ≥3 of these 5 present.

1. **Ritornello anchor** — A complete orchestral theme that opens the movement, returns in related keys at structural points, and closes in the home key. The ritornello is the structural frame; everything else happens between its returns. It must be self-contained, rhythmically driving, and harmonically complete.
2. **Soloist as elaborator, not inventor** — The solo episodes develop material from the ritornello: fragmenting it, sequencing it, ornamenting it, taking it to new keys. The soloist doesn't introduce fundamentally new material — they transform what the orchestra stated.
3. **Driving rhythmic ostinato in the accompaniment** — The string accompaniment (when not playing ritornello) provides a relentless repeated pattern: usually repeated eighth notes or a short rhythmic cell. The drive never stops. This energy is what makes Vivaldi exciting.
4. **Violin-derived figuration** — Melodies are built from what the violin does naturally: arpeggiated runs, scale passages with string crossings, double stops at phrase endings, high-register singing lines. Even when writing for other instruments, the idiom comes from the violin.
5. **Clear, direct harmony with sudden contrast** — Vivaldi's harmony is functionally clear (I-IV-V), but he deploys sudden moves to the parallel minor or Neapolitan for expressive color — without preparation. The surprise IS the effect.

## Pattern Directives

**When writing ritornello:**
- 8–16 bars, tonally closed (begins and ends in same key).
- Clear head motif (2–4 notes, strong rhythmic identity) stated in unison or octaves.
- A sequence section in the middle (circle of fifths or descending sequence).
- Cadential close with trill.

**When writing solo episodes:**
- Soloist takes a fragment of the ritornello head and sequences it upward or downward.
- Accompaniment: repeated eighth-note string pattern (the ostinato) under the solo.
- Move through 2–3 key areas during the episode (relative minor, dominant, subdominant).
- End by approach the next ritornello statement — don't cadence fully; let the ritornello arrival be the cadence.

**When writing slow movements:**
- Solo instrument sings a long, ornamented melody in the high register.
- Accompaniment: sustained strings with gentle pizzicato or very sparse harmonic support.
- Less rhythmic drive; more lyrical expansion.
- One or two tutti interruptions for structural punctuation.

**Harmonic approach:**
- Root position chords predominant. Vivaldi is direct, not subtle.
- Secondary dominants used liberally for color.
- Sudden parallel minor or Neapolitan for expressive moments in slow movements.

## Anti-patterns (what sounds wrong)

- **Ritornello that doesn't return.** The ritornello MUST return. An "opening theme" that's stated once and never heard again is not Vivaldi — it's missing the entire structural logic.
- **Soloist who ignores the ritornello material.** The solo episodes should transform ritornello fragments. A solo that introduces completely new melodic material is un-Vivaldian.
- **Slow, ruminative accompaniment in fast movements.** The driving eighth-note pulse IS Vivaldi's fast movement. Without it, the music loses its characteristic energy.
- **Overly complex counterpoint.** Vivaldi doesn't write fugue — he writes melody + bass + supporting inner parts. Independent counterpoint in all voices is Bach, not Vivaldi.
- **Gradual dynamic changes (crescendo/diminuendo).** Vivaldi's dynamics are terraced: forte tutti, piano solo. No gradual dynamics.

## ShortScore Field Recommendations

**Instrumentation:**
- Solo instrument (melody, episodes and parts of ritornello)
- `vln1`, `vln2` (ripieno — ritornello statements, ostinato accompaniment)
- `vla` (inner harmony)
- `vc` + `kbd` (continuo bass + figured bass realization)

**Melody (solo):**
- Write the complete solo line note-by-note: runs, sequences, arpeggiated patterns.
- For violin: running sixteenth notes across all four strings, reaching up to high positions.
- Ornaments: trills at all structural arrivals, grace notes approaching peaks.

**Accompaniment (ripieno during episodes):**
- Repeated eighth-note patterns in `vln1`/`vln2` on single harmonic pitches.
- `vc`: walking bass or repeated root eighths.

**Dynamics:**
- Forte: all ritornello statements (full orchestra).
- Piano: all solo episodes (soloist + continuo only, or light string support).
