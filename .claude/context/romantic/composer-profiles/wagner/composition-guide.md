# Wagner — Composition Guide (Romantic Period)

**Note: Wagner appears in both romantic/ and late-romantic/ directories.**
**This file covers Wagner's full output. The late-romantic/wagner profile covers the same material.**

## Fingerprints
Any section claiming Wagner's style needs ≥3 of these 5 present.

1. **Leitmotif as structural DNA** — Wagner's music is built from Leitmotifs: short musical tags (3–8 notes, specific rhythm, specific harmony) associated with characters, objects, emotions, or ideas. These aren't themes — they're symbols. A Leitmotif can appear in any instrument, any register, transformed beyond recognition in notes but still carrying its symbolic identity. The texture of Wagnerian music is the constant weaving and collision of these Leitmotifs.
2. **Endless melody — no cadences, no phrases** — Wagner abolished the Baroque/Classical phrase structure. His melodies don't end — they elide into the next phrase, which elides into the next. A Wagnerian "phrase" may run for 32 bars without a clear cadence. The harmonic language supports this by consistently avoiding the tonic at phrase endings (deceptive cadences, half cadences, modal cadences — never the full V→I close).
3. **Chromatic harmony as emotional coloring** — The Tristan chord (half-diminished 7th resolving by half-step motion to another half-diminished 7th) is the paradigm: chromatic harmony that doesn't resolve but intensifies. Augmented chords, Neapolitan harmonies, chromatic inner voice motion, enharmonic pivots — all used to sustain harmonic tension across many bars, deferring resolution almost indefinitely.
4. **Orchestral texture as psychological interior** — Wagner's orchestra doesn't accompany the voice or describe action — it represents the unconscious: what the character feels but cannot say. The strings may play the character's longing while the character sings about the weather.
5. **Transformation and intensification — the long wave** — Wagner builds very slowly over long spans (10–30 minutes) toward a single climactic moment. The entire preceding structure is preparation. His music only makes sense across enormous time spans.

---

## Note-Level Technique: The Tristan Chord

The Tristan chord is F–B–D#–G# (a half-diminished 7th built on F). What makes it Wagnerian is not the chord itself but its resolution: each voice moves by a half step, arriving at a chord that is also ambiguous — no clear tonic revealed.

**Tristan chord → intensification (no resolution, just more tension):**
```json
{"bar_num": 1, "_feel": "Breathe in — the harmony is ambiguous, suspended, yearning", "voices": {
  "vln1": [{"p": "G#5", "d": "w", "dyn": "p"}],
  "vln2": [{"p": "D#5", "d": "w"}],
  "vla":  [{"p": "B4",  "d": "w"}],
  "vc":   [{"p": "F3",  "d": "w"}]
}},
{"bar_num": 2, "_feel": "Each voice moves by half-step — still no arrival", "voices": {
  "vln1": [{"p": "A5",  "d": "w", "dyn": "mp"}],
  "vln2": [{"p": "E5",  "d": "w"}],
  "vla":  [{"p": "C5",  "d": "w"}],
  "vc":   [{"p": "F#3", "d": "w"}]
}},
{"bar_num": 3, "_feel": "The harmonic 'resolution' reveals another unresolved chord — the yearning intensifies", "voices": {
  "vln1": [{"p": "Bb5", "d": "w", "dyn": "mf"}],
  "vln2": [{"p": "F5",  "d": "w"}],
  "vla":  [{"p": "Db5", "d": "w"}],
  "vc":   [{"p": "G3",  "d": "w"}]
}}
```
Bar 1: F3–B4–D#5–G#5 = Tristan chord (half-diminished 7th on F). Bar 2: each voice moves up by half-step → F#3–C5–E5–A5 (E major chord with added major 7th = another ambiguous harmony). Bar 3: continues moving → G3–Db5–F5–Bb5 (still unresolved). No tonic appears. Each bar is more intense than the last.

**After 4–8 bars of this**: The delayed dominant finally arrives. The tonic, when it comes, has been deferred so long that the listener physically exhales.

---

## Note-Level Technique: Endless Melody (Phrase Elision)

In normal music: phrase ends with a cadence → silence → new phrase begins. In Wagner: the phrase "ending" is simultaneously the beginning of the next phrase. The harmony shifts but no pause occurs. The melody flows without stopping.

**Phrase 1 approaching bar 8 — normal music would cadence here. Wagner does not:**
```json
{"bar_num": 7, "voices": {
  "vln1": [
    {"p": "A5",  "d": "q", "dyn": "mf"},
    {"p": "G#5", "d": "q"},
    {"p": "F#5", "d": "q"},
    {"p": "E5",  "d": "q"}
  ],
  "vc":   [{"p": "A2",  "d": "h"}, {"p": "E3",  "d": "h"}]
}},
{"bar_num": 8,
  "_feel": "Deceptive cadence — phrase 1 should end here but the VI chord arrives instead. The melody keeps going without pause.",
  "voices": {
  "vln1": [
    {"p": "D5",  "d": "q",  "dyn": "p"},
    {"p": "E5",  "d": "q"},
    {"p": "F5",  "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "vc":   [{"p": "F#2", "d": "h"}, {"p": "D3",  "d": "h"}]
}},
{"bar_num": 9, "voices": {
  "vln1": [
    {"p": "A5",  "d": "dh", "dyn": "mf"},
    {"p": "G5",  "d": "q"}
  ],
  "vc":   [{"p": "B2",  "d": "h"}, {"p": "F#3", "d": "h"}]
}}
```
Bar 7: melody descends toward what sounds like an A minor cadence (E2 in bass). Bar 8: the expected A minor tonic in the bass is replaced by F#minor (the VI) — deceptive cadence. The melody doesn't notice — it keeps rising. Bar 9: another phrase continues. No silence. No pause. The phrases flow into each other like water.

---

## Note-Level Technique: Leitmotif Weaving

Two Leitmotifs woven simultaneously in inner voices while a new melody plays above. Each Leitmotif is recognizable by its first 3 notes; the listener may not consciously hear them, but their presence colors the texture.

**Leitmotif A ("Longing"): E4–F4–D#4 (chromatic sigh figure)**
**Leitmotif B ("Fate"): D4–D4–D4–A3 (three repeated notes + falling P5)**

**Both woven in inner voices while vln1 melody plays above:**
```json
{"bar_num": 12,
  "_feel": "The orchestra knows what the character does not — Longing and Fate sound simultaneously below the melody.",
  "voices": {
  "vln1": [
    {"p": "C#5", "d": "h",  "dyn": "mf", "expr": "sehr ausdrucksvoll"},
    {"p": "D5",  "d": "h"}
  ],
  "vln2": [
    {"p": "E4",  "d": "q"},
    {"p": "F4",  "d": "q"},
    {"p": "D#4", "d": "h"}
  ],
  "vla":  [
    {"p": "D4",  "d": "q"},
    {"p": "D4",  "d": "q"},
    {"p": "D4",  "d": "q"},
    {"p": "A3",  "d": "q"}
  ],
  "vc":   [{"p": "A2",  "d": "w", "dyn": "p"}]
}}
```
vln1: new melody (C#5–D5). vln2: Leitmotif A (E4–F4–D#4 = the chromatic sigh, "Longing"). vla: Leitmotif B (D4–D4–D4–A3 = three repeated notes then falling P5, "Fate"). vc: bass pedal. The melody and the two Leitmotifs are simultaneously active, independently, at different dynamics. The texture has four voices — the melody, two symbolic layers, and the bass.

---

## Pattern Directives

**Leitmotif weaving:**
- Define 2–3 Leitmotifs for the section: each 4–6 notes with a specific harmonic context.
- In the accompaniment: the Leitmotifs appear fragmented — 2 notes from Motif A, 3 from Motif B, 2 from Motif A inverted.
- The vocal line (or solo instrument) carries a different, newer melody.
- The two layers (Leitmotif texture + present melody) are independent — the orchestra comments on the melody's subtext.

**Endless melody:**
- Write a phrase that would normally cadence at bar 8. At bar 7, instead of V→I: use a deceptive cadence (V→VI) and continue.
- The new phrase begins on beat 3 of bar 8 (elided with the preceding phrase's "ending").
- Continue: 16 bars without full cadence.
- When the cadence finally arrives: it carries the weight of all the deferred resolution.

**Orchestral layers:**
- Strings: Leitmotif fragments in inner register, sustained and woven.
- Winds: harmonic filling, sustained chords.
- Brass: key Leitmotifs at structural moments, forte.
- All layers: simultaneously active but at different dynamic levels.

---

## Anti-patterns

- **Clear phrase endings.** Wagner does not cadence cleanly. Any V→I cadence that sounds final is wrong — Wagner defers finality constantly.
- **Literal repetition.** Wagner doesn't repeat. He transforms, develops, combines. The same Leitmotif appearing twice in exactly the same form is unusual.
- **Single-layer texture.** A Wagnerian texture with melody + simple accompaniment is not Wagner — it's Schubert. Wagner's textures have 3–5 independent layers at all times.
- **Short time scale.** A 4-bar Wagnerian passage is a fragment, not a structure.

---

## ShortScore Field Recommendations

**Chromatic harmony (write as explicit note arrays, not chord symbols):**
```json
{"p": ["F3","B4","D#5","G#5"], "d": "w"}
```
Each voice in its own part (not as a chord array) for independent voice-leading.

**Endless melody:**
- `"_feel": "phrase elides — no cadence, continue immediately"` at phrase junctions.
- No structural pause. The next measure's first beat continues the melodic phrase.

**Dynamics:**
- Wagner's range: ppp to fff. The long crescendo is his most important device.
- Mark gradual crescendo: `"dyn": "ppp"` → many bars later → `"dyn": "fff"`.
- `"expr": "sehr ausdrucksvoll"` (very expressive) — Wagner's marking.
- `"expr": "leidenschaftlich"` (passionately) for climactic sections.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #6: Deceptive Cadence (the core mechanism of endless melody)
- Technique #12: Dominant Pedal (Wagner's "held breath" before climax)
- Technique #2: The 4-3 Suspension (frequently used at structural moments)
