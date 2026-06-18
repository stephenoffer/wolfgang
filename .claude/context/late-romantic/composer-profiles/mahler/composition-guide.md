# Mahler — Composition Guide

## Fingerprints
Any section claiming Mahler's style needs ≥3 of these 5 present.

1. **Chamber-within-orchestra** — After a massive tutti climax, the texture suddenly collapses to 2–3 solo instruments (often solo violin, or solo oboe + pizzicato cello). This contrast — overwhelming grandeur immediately followed by naked, vulnerable solo — IS Mahler's primary emotional device. The small instrumentation after the large one makes the exposed voice unbearably fragile.
2. **Folk song / march / dance material in unexpected contexts** — A Ländler (Austrian dance), a military march, or a folk song appears within a symphony movement where it creates dramatic irony. The "low" genre material (dance, march) in a "high" genre context (symphony) creates either nostalgia, grief, or grotesque humor depending on the context.
3. **Tonal dissolution — key wandering without arrival** — Mahler's harmonies wander through keys for long passages without establishing any key firmly. He may spend 32 bars passing through F, Ab, B, D (augmented-fifth cycle) without ever landing. The tonal center is always implied but rarely confirmed.
4. **Postlude as the real climax** — The "ending" of a Mahler movement often comes long after the musical climax. A 20–40 bar postlude after the main material has concluded — adding a final echo, a final dissolution, a last transformation of the theme. The movement doesn't end when it seems to; it keeps speaking.
5. **Song-like melody in orchestral context** — Mahler's melodies derive from his own songs (Das Lied von der Erde, Des Knaben Wunderhorn). They have a vocal, text-derived character even when played by instruments: shaped by natural speech rhythm, with octave leaps at emotional peaks, and a sense of personal address.

---

## Note-Level Technique 1: Chamber Reduction (Tutti → Naked Solo)

After a massive tutti climax, the texture collapses — suddenly — to one solo instrument + ppp pizzicato strings. No gradual diminuendo. A bar of silence (or a fermata), then the solo enters. The emotional shock is the contrast.

**Tutti climax → sudden chamber texture:**
```json
{"bar_num": 45, "_feel": "Tutti climax — the peak of the movement. Everyone, everything, fff.", "voices": {
  "vln1": [{"p": "C6",  "d": "w", "dyn": "fff"}],
  "vln2": [{"p": "G5",  "d": "w", "dyn": "fff"}],
  "vla":  [{"p": "Eb5", "d": "w", "dyn": "fff"}],
  "vc":   [{"p": "C4",  "d": "w", "dyn": "fff"}],
  "cb":   [{"p": "C2",  "d": "w", "dyn": "fff"}]
}},
{"bar_num": 46, "_feel": "Sudden silence — one full bar of rest. The abyss between grandeur and vulnerability.", "voices": {
  "vln1": [{"p": "rest", "d": "w"}],
  "vln2": [{"p": "rest", "d": "w"}],
  "vla":  [{"p": "rest", "d": "w"}],
  "vc":   [{"p": "rest", "d": "w"}],
  "cb":   [{"p": "rest", "d": "w"}]
}},
{"bar_num": 47, "_feel": "Solo violin alone — high register, piano, as if speaking to no one. The vulnerability IS the point.", "voices": {
  "vln1": [
    {"p": "E6",  "d": "h",  "dyn": "p", "expr": "wie verlassen"},
    {"p": "D6",  "d": "q"},
    {"p": "C#6", "d": "q"}
  ],
  "vc": [
    {"p": "C2",  "d": "q",  "dyn": "ppp", "art": "pizz"},
    {"p": "rest","d": "q"},
    {"p": "G2",  "d": "q",  "art": "pizz"},
    {"p": "rest","d": "q"}
  ]
}},
{"bar_num": 48, "voices": {
  "vln1": [
    {"p": "B5",  "d": "h",  "dyn": "pp"},
    {"p": "A5",  "d": "h"}
  ],
  "vc": [
    {"p": "E2",  "d": "q",  "art": "pizz"},
    {"p": "rest","d": "q"},
    {"p": "C2",  "d": "h",  "art": "pizz"}
  ]
}}
```
Bar 45: full orchestra, fff. Bar 46: complete silence — all instruments rest. Bar 47: only vln1 (melody) and vc (pizzicato harmonic support, ppp) — nothing else. The contrast between fff tutti and this exposed solo is the Mahler emotional gesture. `"expr": "wie verlassen"` = as if abandoned. The solo violin should be in its highest comfortable register.

---

## Note-Level Technique 2: Orchestral Multi-Layer (4 Independent Voices)

Mahler writes 4 independent voices simultaneously — each with its own melody, rhythm, and dynamic. They are NOT in rhythmic alignment. The texture is polyphonic, not homophonic. Each voice is labeled with its character.

**4 layers, 4 different characters, in D major:**
```json
{"bar_num": 1, "_feel": "4 voices, none dominant — the orchestra is a world of simultaneous private thoughts", "voices": {
  "fl":   [
    {"p": "A5",  "d": "dh", "dyn": "mf", "expr": "cantabile"},
    {"p": "G5",  "d": "q"}
  ],
  "ob":   [
    {"p": "F#5", "d": "h",  "dyn": "mp", "expr": "dolce"},
    {"p": "E5",  "d": "q"},
    {"p": "D5",  "d": "q"}
  ],
  "vla":  [
    {"p": "D4",  "d": "q",  "dyn": "p",  "expr": "schwer"},
    {"p": "E4",  "d": "q"},
    {"p": "F#4", "d": "h"}
  ],
  "timp": [
    {"p": "D2",  "d": "q",  "dyn": "pp", "art": "staccato"},
    {"p": "rest","d": "q"},
    {"p": "D2",  "d": "q",  "art": "staccato"},
    {"p": "rest","d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "fl":   [
    {"p": "F#5", "d": "h"},
    {"p": "E5",  "d": "h",  "dyn": "mp"}
  ],
  "ob":   [
    {"p": "C#5", "d": "dh", "expr": "klagend"},
    {"p": "B4",  "d": "q"}
  ],
  "vla":  [
    {"p": "G4",  "d": "h",  "dyn": "mp"},
    {"p": "F#4", "d": "q"},
    {"p": "E4",  "d": "q"}
  ],
  "timp": [
    {"p": "A2",  "d": "e",  "art": "staccato"},
    {"p": "A2",  "d": "e"},
    {"p": "D2",  "d": "h",  "dyn": "p"}
  ]
}}
```
fl: a singing cantabile melody in the high register. ob: a lower melody with a different rhythm, marked "dolce." vla: a separate harmonic-melodic line, "schwer" (heavy). timp: a rhythmic ostinato unrelated to the melody rhythms. All four simultaneously, each at a different dynamic. The asynchrony creates the characteristic Mahler texture — orchestral counterpoint where each voice is a separate consciousness.

---

## Note-Level Technique 3: Ländler Intrusion (Folk Dance in Symphonic Context)

A Ländler (Austrian folk waltz, 3/4) appears within a slow or dramatic symphonic movement. It has its own melody, self-contained. The intrusion creates dramatic irony: the folk dance is either nostalgic (memory of simpler times), grotesque (dance on the grave), or bitter (the world dances while the protagonist suffers).

**Ländler in 3/4, solo strings, pp — appearing within a larger movement:**
```json
{"bar_num": 62, "_section": "Ländler intrusion", "_feel": "The Ländler appears — a dance memory in the middle of grief. Was this tender once?", "voices": {
  "vln1": [
    {"p": "rest","d": "q"},
    {"p": "F5",  "d": "q",  "dyn": "pp", "expr": "naiv"},
    {"p": "E5",  "d": "q"}
  ],
  "vln2": [
    {"p": "C3",  "d": "q",  "dyn": "pp", "art": "pizz"},
    {"p": "G3",  "d": "q",  "art": "pizz"},
    {"p": "G3",  "d": "q",  "art": "pizz"}
  ]
}},
{"bar_num": 63, "voices": {
  "vln1": [
    {"p": "D5",  "d": "q"},
    {"p": "C5",  "d": "q"},
    {"p": "D5",  "d": "q"}
  ],
  "vln2": [
    {"p": "F2",  "d": "q",  "art": "pizz"},
    {"p": "A3",  "d": "q",  "art": "pizz"},
    {"p": "C4",  "d": "q",  "art": "pizz"}
  ]
}},
{"bar_num": 64, "voices": {
  "vln1": [
    {"p": "E5",  "d": "dh", "dyn": "p"}
  ],
  "vln2": [
    {"p": "C3",  "d": "q",  "art": "pizz"},
    {"p": "G3",  "d": "q",  "art": "pizz"},
    {"p": "G3",  "d": "q",  "art": "pizz"}
  ]
}},
{"bar_num": 65, "_feel": "The Ländler ends as suddenly as it began — the symphony resumes", "voices": {
  "vln1": [{"p": "D5", "d": "h"}, {"p": "C5", "d": "q"}],
  "vln2": [{"p": "F2", "d": "q", "art": "pizz"}, {"p": "C3", "d": "q", "art": "pizz"}, {"p": "rest","d": "q"}]
}}
```
The Ländler uses: 3/4 time, waltz-bass pizzicato in vln2 (root on beat 1, inner chord on beats 2-3), simple folk-like melody in vln1. Dynamic: pp throughout. Expression: `"naiv"` — childlike, unguarded. This is NOT a sophisticated melody — it is simple, folk, almost banal. That simplicity in the middle of a complex symphonic movement IS the emotional content.

---

## Pattern Directives

**Chamber-within-orchestra technique:**
- After any tutti fortissimo passage, reduce immediately to: solo instrument (melody) + pizzicato strings (harmonic support, pp).
- No gradual diminuendo — sudden, with a fermata or bar of silence between.
- The solo instrument should be at the top of its comfortable range, and the key should be unexpected (often the relative major after a minor climax).

**Folk/march intrusions:**
- Insert a ¾ Ländler (waltz-like) passage within a slow movement. Use solo strings and woodwinds, pp to mp.
- The Ländler should have its own self-contained melody (distinct from the surrounding material) but with a phrase that references the movement's main theme by interval or rhythm.
- Insert military rhythms (dotted quarter + eighth, snare drum patterns) as punctuation in scherzo movements.

**Orchestral layering:**
- Mahler rarely writes clear melody + accompaniment. Instead: 3–4 simultaneous independent voices, each in its own register, with their own rhythm.
- Example: Flute has melody. Oboe has a counter-melody a third below. Strings have a slow-moving harmonic layer. Timpani has a separate rhythmic ostinato. All four simultaneously.

**Harmonic approach:**
- Extended tonal regions: stay in one key for 4 bars, then shift to a key a major third away (not a fifth), then another major third (augmented-fifth cycle: C → E → Ab → C).
- Neapolitan (bII) for moments of grief or nostalgia.
- Unresolved dominant pedal lasting 8+ bars before the tonic arrives.

## Anti-patterns (what sounds wrong)

- **Constant tutti writing.** Mahler's texture is in constant flux — tutti moments are climaxes, not normal states. A passage that sustains full orchestra for 32 bars without chamber reduction is un-Mahlerian.
- **Generic Romantic melody.** Mahler's melodies have the quality of someone telling you something urgent. A generic "beautiful melody" that could be anyone's is not Mahler. His melodies carry a specific character — longing, grief, bittersweet memory, grotesque irony.
- **Resolved, stable harmony.** Mahler's harmonies are in motion. A tonally stable passage (clearly in one key for 16 bars) sounds like a textbook exercise, not Mahler.
- **Missing the postlude.** A Mahler movement that ends at its climax is truncated. The long dissolution after the climax is essential — the music refuses to end.
- **No stylistic contrast.** The coexistence of "low" (dance, march) and "high" (symphonic development) material is non-negotiable. Without ironic genre mixture, it's not Mahler — it's just late Romantic.

## ShortScore Field Recommendations

**Chamber reduction passages:**
- After tutti: mark all instruments `"dyn": "ppp"` except the solo voice.
- Solo instrument: write melody explicitly in high register with subtle ornamentation (grace notes).
- Accompaniment: pizzicato strings (`"art": "pizzicato"`) with sustained harmonics above.

**Multiple simultaneous layers:**
- Write each instrumental voice with its own independent melodic line.
- Don't align all voices rhythmically — the asynchrony IS the texture.
- Label each voice with `"expr"` describing its character: `"cantabile"`, `"ironico"`, `"pesante"`.

**Dynamics:**
- Range from `"dyn": "ppp"` (chamber passages) to `"dyn": "fff"` (tutti climaxes).
- The transition between them is often abrupt (no crescendo — just a sudden change).
- Use `"dyn": "sfz"` for rhythmic displacements in march passages.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #5: Ascending Sequence — Mahler's climax builds use sequential escalation
- Technique #3: Lament Bass — for Mahler's tragic adagio passages
- Technique #12: Dominant Pedal — the unresolved dominant pedal before Mahler's cathartic arrivals
- Technique #6: Deceptive Cadence — Mahler withholds tonic constantly; deceptive cadences are structural
