# Tchaikovsky — Composition Guide

## Fingerprints
Any section claiming Tchaikovsky's style needs ≥3 of these 5 present.

1. **Long, sweeping melody with a built-in arch** — Tchaikovsky's themes have a specific architecture: they begin relatively low, rise in a long sustained ascent over 8–16 bars, peak on a sustained high note with full orchestra, then descend in a shorter, more resigned return. The entire phrase is one breath. The peak is the emotional goal — everything before is approach, everything after is aftermath.
2. **Waltz rhythm as emotional vehicle** — The waltz (3/4, or 12/8 implied) pervades Tchaikovsky's writing beyond ballet: symphonies, string quartets, piano pieces. The lilt of the waltz is emotional vulnerability — the grace and sadness of something beautiful and fragile. Even tragic movements may have a waltz underneath.
3. **Sequence as escalation** — Tchaikovsky drives toward climaxes through relentless sequential repetition: the same 2-bar gesture a step higher, then a step higher again, then again. Each repetition adds orchestral mass. The sequence IS the crescendo — not a figuration technique but an emotional engine.
4. **Russian modal color within tonal framework** — Despite writing in standard keys, Tchaikovsky uses Russian folk-modal inflections: the lowered 6th degree (bVI in major keys), the Phrygian-style cadence (bII→I), and the Dorian raised 6th in minor. These appear without modulation — a single chord or melodic note carries the Russian character.
5. **Fate/doom bass ostinato at crisis moments** — At points of highest emotional tension, the lower strings and brass sustain a repeated bass figure — often a chromatic descent or a repeated threatening rhythm — while the melody tries to escape above it. The bass says: there is no escape. The melody says: but I must try.

---

## Note-Level Technique 1: The Long Melody Arch (Write Peak First)

Tchaikovsky's melody is an architectural structure — not a random sequence of notes. Before writing bar 1, decide: (1) the peak note and which bar it occupies, (2) the starting note (typically a 6th or octave below the peak), (3) the descent route after the peak. Then fill in the approach.

**A 12-bar arch in A minor: begins A4, peaks on E6 at bar 8, descends to D4:**
```json
{"bar_num": 1, "_feel": "Begin low — the climb has not started yet", "voices": {
  "vln1": [{"p": "A4", "d": "h", "dyn": "mp"}, {"p": "B4", "d": "q"}, {"p": "C5", "d": "q"}],
  "vc":   [{"p": "A2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "E3","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 2, "voices": {
  "vln1": [{"p": "D5", "d": "h"}, {"p": "C5", "d": "q"}, {"p": "B4", "d": "q"}],
  "vc":   [{"p": "A2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "E3","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 3, "voices": {
  "vln1": [{"p": "C5", "d": "q"}, {"p": "D5", "d": "q"}, {"p": "E5", "d": "q"}, {"p": "F5", "d": "q"}],
  "vc":   [{"p": "F2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "C3","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 4, "_feel": "Sequential sub-peak — the first climb reaches E5", "voices": {
  "vln1": [{"p": "E5", "d": "dh", "dyn": "mf"}, {"p": "D5", "d": "q"}],
  "vc":   [{"p": "E2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "B2","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 5, "voices": {
  "vln1": [{"p": "C5", "d": "q"}, {"p": "D5", "d": "q"}, {"p": "E5", "d": "q"}, {"p": "F#5","d": "q"}],
  "vc":   [{"p": "A2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "E3","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 6, "voices": {
  "vln1": [{"p": "G#5","d": "q", "dyn": "f"}, {"p": "A5", "d": "q"}, {"p": "B5", "d": "q"}, {"p": "C6", "d": "q"}],
  "vc":   [{"p": "E2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "B2","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 7, "_feel": "Approaching the peak — tension builds, everyone knows it's coming", "voices": {
  "vln1": [{"p": "D6", "d": "q", "dyn": "ff"}, {"p": "C6", "d": "q"}, {"p": "B5", "d": "q"}, {"p": "D6", "d": "q"}],
  "vc":   [{"p": "D2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "A2","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 8, "_feel": "THE PEAK — E6, fortissimo, sustained. Full orchestra doubles.", "voices": {
  "vln1": [{"p": "E6", "d": "h",  "dyn": "fff", "expr": "appassionato"}, {"p": "D6", "d": "h"}],
  "vc":   [{"p": "A1", "d": "h",  "dyn": "ff"},  {"p": "E2","d": "h"}]
}},
{"bar_num": 9, "_feel": "Descent — resigned, exhaling after the peak. Dynamics fall fast.", "voices": {
  "vln1": [{"p": "C6", "d": "h", "dyn": "f"}, {"p": "B5", "d": "q"}, {"p": "A5", "d": "q"}],
  "vc":   [{"p": "A1", "d": "h", "dyn": "mf"}, {"p": "E2","d": "h"}]
}},
{"bar_num": 10, "voices": {
  "vln1": [{"p": "G5", "d": "q", "dyn": "mf"}, {"p": "F5","d": "q"}, {"p": "E5","d": "q"}, {"p": "D5","d": "q"}],
  "vc":   [{"p": "D2", "d": "h"}, {"p": "A2","d": "h"}]
}},
{"bar_num": 11, "voices": {
  "vln1": [{"p": "C5", "d": "h", "dyn": "mp"}, {"p": "B4", "d": "h"}],
  "vc":   [{"p": "E2", "d": "h"}, {"p": "B2","d": "h"}]
}},
{"bar_num": 12, "_feel": "The melody settles — the arch is complete. The peak feels distant already.", "voices": {
  "vln1": [{"p": "D4", "d": "w", "dyn": "p"}],
  "vc":   [{"p": "D2", "d": "w", "dyn": "p"}]
}}
```
The peak (bar 8, E6, fff) is the structural center around which everything else is organized. Bars 1–7 approach it; bars 9–12 descend from it. The peak is longer than any other note (half note). Everything after bar 8 is softer than anything before bar 8 — the descent is always more resigned than the ascent.

---

## Note-Level Technique 2: Waltz Bass (Explicit Notes, 3/4)

Tchaikovsky's waltz pattern: vc plays a quarter note on beat 1 (the bass hit), vla plays two quarter notes on beats 2–3 (the inner chord). The melody enters on beat 3 of the PRECEDING bar, so it sits on top of the waltz as a long note crossing the barline.

**Waltz bass in C major (vc + vla explicit notes, 3/4):**
```json
{"bar_num": 1, "_feel": "Waltz — beat 1 bass, beats 2–3 inner chord. Melody is already present.", "voices": {
  "vln1": [{"p": "E5",  "d": "h",  "dyn": "mp"}, {"p": "F5", "d": "q"}],
  "vla":  [{"p": "rest","d": "q"}, {"p": "E3", "d": "q"}, {"p": "G3","d": "q"}],
  "vc":   [{"p": "C2",  "d": "q"}, {"p": "rest","d": "h"}]
}},
{"bar_num": 2, "voices": {
  "vln1": [{"p": "G5",  "d": "dh"}],
  "vla":  [{"p": "rest","d": "q"}, {"p": "G3", "d": "q"}, {"p": "B3","d": "q"}],
  "vc":   [{"p": "G2",  "d": "q"}, {"p": "rest","d": "h"}]
}},
{"bar_num": 3, "voices": {
  "vln1": [{"p": "F5",  "d": "q"}, {"p": "E5","d": "q"}, {"p": "D5","d": "q"}],
  "vla":  [{"p": "rest","d": "q"}, {"p": "F3", "d": "q"}, {"p": "A3","d": "q"}],
  "vc":   [{"p": "F2",  "d": "q"}, {"p": "rest","d": "h"}]
}}
```
vc: quarter note only on beat 1, then silent. vla: silent on beat 1, then two quarter notes on beats 2 and 3 (the inner harmonic fill). vln1: the melody — in these bars it's longer values floating above the waltz rhythm. The cello resonates on its natural decay; the viola keeps the harmonic rhythm. Never write the cello as a dotted quarter — that notation would tie it into beat 2 and muddy the rhythm.

---

## Note-Level Technique 3: Sequential Escalation (3-Step Crescendo)

Tchaikovsky's climax build: a 2-bar cell is restated a step higher three times, each time with more instruments. Each step is louder. The destination (bar 7 in this example) is the climax — the sequence is the preparation.

**2-bar cell in A minor, sequenced to C minor, E minor, then peak:**
```json
{"bar_num": 1, "_feel": "Sequence step 1 — the gesture, quiet, small ensemble", "voices": {
  "vln1": [{"p": "A4","d": "q", "dyn": "mp"}, {"p": "B4","d": "q"}, {"p": "C5","d": "q"}, {"p": "D5","d": "q"}],
  "vc":   [{"p": "A2","d": "h"}, {"p": "E2","d": "h"}]
}},
{"bar_num": 2, "voices": {
  "vln1": [{"p": "E5","d": "h"}, {"p": "D5","d": "q"}, {"p": "C5","d": "q"}],
  "vc":   [{"p": "A2","d": "h"}, {"p": "E2","d": "h"}]
}},
{"bar_num": 3, "_feel": "Sequence step 2 — one step higher. Cellos enter to double. mf.", "voices": {
  "vln1": [{"p": "C5","d": "q", "dyn": "mf"}, {"p": "D5","d": "q"}, {"p": "Eb5","d": "q"}, {"p": "F5","d": "q"}],
  "vln2": [{"p": "G4","d": "q"}, {"p": "A4","d": "q"}, {"p": "Bb4","d": "q"}, {"p": "C5","d": "q"}],
  "vc":   [{"p": "C2","d": "h"}, {"p": "G2","d": "h"}]
}},
{"bar_num": 4, "voices": {
  "vln1": [{"p": "G5","d": "h"}, {"p": "F5","d": "q"}, {"p": "Eb5","d": "q"}],
  "vln2": [{"p": "Eb5","d": "h"},{"p": "D5","d": "q"}, {"p": "C5","d": "q"}],
  "vc":   [{"p": "C2","d": "h"}, {"p": "G2","d": "h"}]
}},
{"bar_num": 5, "_feel": "Sequence step 3 — one step higher again. Violas double melody. f.", "voices": {
  "vln1": [{"p": "E5","d": "q", "dyn": "f"}, {"p": "F#5","d": "q"}, {"p": "G#5","d": "q"}, {"p": "A5","d": "q"}],
  "vln2": [{"p": "B4","d": "q"}, {"p": "C#5","d": "q"}, {"p": "D#5","d": "q"}, {"p": "E5","d": "q"}],
  "vla":  [{"p": "E4","d": "q"}, {"p": "F#4","d": "q"}, {"p": "G#4","d": "q"}, {"p": "A4","d": "q"}],
  "vc":   [{"p": "E2","d": "h"}, {"p": "B2","d": "h"}]
}},
{"bar_num": 6, "voices": {
  "vln1": [{"p": "B5","d": "h", "dyn": "ff"}, {"p": "A5","d": "q"}, {"p": "G#5","d": "q"}],
  "vln2": [{"p": "G#5","d": "h"},{"p": "F#5","d": "q"}, {"p": "E5","d": "q"}],
  "vla":  [{"p": "B4","d": "h"}, {"p": "A4","d": "q"},  {"p": "G#4","d": "q"}],
  "vc":   [{"p": "E2","d": "h"}, {"p": "B2","d": "h"}]
}},
{"bar_num": 7, "_feel": "The climax arrives — full orchestra, fff", "voices": {
  "vln1": [{"p": "A5","d": "w", "dyn": "fff", "expr": "appassionato"}],
  "vc":   [{"p": "A1","d": "w", "dyn": "fff"}]
}}
```
Bar 1–2: A minor cell, mp, thin texture. Bars 3–4: same cell in C minor, mf, add vln2. Bars 5–6: same cell in E minor, f, add vla. Bar 7: climax, fff, all strings. Each step adds one instrument family AND moves one step higher in pitch. The arrival is inevitable.

---

## Pattern Directives

**The long melody:**
- Plan the architecture first: start pitch, peak pitch (a 6th or octave above), duration of ascent (8–12 bars), duration of descent (4 bars).
- Ascent: stepwise or with occasional leaps; each phrase a half-step or step higher than previous; sustained notes at the top of each sub-phrase.
- Peak: the highest note, forte or fortissimo, held for 2–4 beats, full orchestra.
- Descent: softer, faster, resigned — the emotional exhale after the peak.

**Waltz character:**
- 3/4 time with bass on beat 1, chord on beats 2–3.
- Melody: begins on beat 3 of the bar (the "feminine" entry), sustains across barline.
- Inner voice: sustained harmonic notes on beat 2.
- The rhythm is gentle, never mechanical — slight agogic elongation of beat 1 implied.

**Sequential escalation:**
- Write a 2-bar melodic gesture in C minor.
- Repeat it in D minor (one step up): same shape, new pitch level.
- Repeat in E minor.
- Each repetition: add one instrument (or double the existing ones). The orchestra thickens with the sequence.
- After 3–4 repetitions: full orchestra entrance, ff, the goal arrives.

**Russian modal inflection:**
- In C major: use Ab major chord (bVI) as a color chord at phrase endings. No preparation, no resolution — just the flat-six as a flavor.
- Cadence: Db major → C major (bII→I, Phrygian cadence) for a specifically Russian finality.

## Anti-patterns (what sounds wrong)

- **Short, symmetrical themes.** Tchaikovsky's themes are long and asymmetrical (5-bar + 7-bar = 12 bars, not 4+4). Short, square themes sound like Haydn, not Tchaikovsky.
- **Restrained climax.** Tchaikovsky is not restrained at climaxes. The peak of a Tchaikovsky theme is always fully orchestrated, always ff or fff. Holding back at the moment of arrival destroys the architecture.
- **Absence of sequential approach.** A Tchaikovsky climax that arrives without sequential preparation is missing his most powerful technique. The sequence is the journey; the climax is the destination.
- **Neutral harmonic language.** Tchaikovsky's harmony always has Russian color — a flat-six, a Phrygian move, a modal inflection. A piece that uses only standard functional harmony sounds German, not Russian.
- **Irony or emotional distance.** Tchaikovsky wears his heart on his sleeve. Emotional restraint, irony, or emotional complexity beyond direct feeling is Shostakovich, not Tchaikovsky. The emotion is direct, large, and unashamed.

## ShortScore Field Recommendations

**Long melody arc:**
- Write every note of the melody explicitly: pitch + duration for the full 12–16 bar arc.
- Mark the peak note: `"dyn": "ff"`, `"expr": "appassionato"`.
- The descent: `"dyn": "f"` → `"dyn": "mf"` → `"dyn": "mp"` as it falls.

**Sequential escalation:**
- Write each sequence statement as a separate phrase block with sequential pitch transposition noted.
- `"_feel": "sequence step 2 — one step higher, add cello doublings"`.
- Each step: add one voice to the orchestration.

**Waltz bass:**
- `vc`/`cb`: `{"p": "C2", "d": "q."}` on beat 1 — full resonance.
- `vla`: `{"p": "E3", "d": "q"}` on beat 2, `{"p": "G3", "d": "q"}` on beat 3.

**Dynamics:**
- Tchaikovsky's dynamic range: pp to fff — the full range exploited.
- `"expr": "appassionato"` at climax.
- `"expr": "mesto"` (sad) at quiet lyrical sections.
- Sudden p after ff: the "collapse" after climax — one of his most effective moves.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #5: Ascending Sequence — the 3-step sequence that builds Tchaikovsky's climaxes
- Technique #3: Lament Bass — for Tchaikovsky's "fate" ostinato moments in minor
- Technique #2: The 4-3 Suspension — used at lyrical phrase openings in slow movements
- Technique #6: Deceptive Cadence — Tchaikovsky regularly withholds the tonic at phrase endings
