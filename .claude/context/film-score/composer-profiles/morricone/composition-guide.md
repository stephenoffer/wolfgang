# Ennio Morricone — Composition Guide

## Fingerprints
Any section claiming Morricone's style needs ≥3 of these 5 present.

1. **Eclectic instrumentation — "wrong" instruments for the context** — Morricone uses instruments that shouldn't work together: solo soprano voice singing a wordless melody over electric guitar and orchestra; ocarina or jaw harp as melodic instrument; solo trumpet in extreme high register against strings. The unexpected instrument combination IS the personality. A Morricone sound is immediately recognizable partly because no one else would choose those instruments for that melody.
2. **Simple, singable primary melody over complex texture** — The primary melody is always simple enough to hum — even when the orchestral background is harmonically complex or rhythmically unusual. The melody anchors everything. The harmonic richness, the unusual instruments, the rhythmic energy — all of these support a melody that could be whistled.
3. **Spaghetti Western sonic world — open spaces and silence** — For the Leone films: wide-open harmonic space (open 5ths, single sustained notes), much silence (the gap between events creates tension), and specific sound objects (twangy guitar arpeggios, clanking chains, distant trumpet, wind). The silence IS the tension.
4. **Modal/folk melodic language — not Classical, not pop** — Morricone's melodies often draw on Italian folk music, Spanish/Latin American inflections, or modal scales (Dorian, Phrygian) that give them a timeless, ancient quality. They don't sound like Hollywood movie music — they sound like they come from somewhere real.
5. **Countermelody architecture — multiple layers singing simultaneously** — Morricone builds textures where 2–3 simultaneous melodic layers are all singable and all independent. In The Good, the Bad and the Ugly main theme: the main melody, a countermelody in the bass register, and a rhythmic ostinato — three distinct melodic layers at once. Each layer is complete; together they are extraordinary.

## Pattern Directives

**Eclectic instrumental combination:**
- Choose: one "wrong" solo instrument for the melody (harmonica, ocarina, solo soprano voice).
- Support: a "normal" supporting texture underneath (strings, guitar, light percussion).
- The "wrong" instrument carries the most important melodic line.
- The contrast between the intimate solo color and the orchestral support is the Morricone moment.

**Simple melody, complex accompaniment:**
- Write the melody first — 8 bars, stepwise, completely singable.
- Then construct the accompaniment as a complex orchestral texture beneath it.
- The melody must be audible as a single coherent line above the complex texture.

**Open-space tension texture:**
- Two sustained notes an open 5th apart: E2 and B2 (or similar).
- Complete silence for 2–4 bars.
- Single guitar arpeggio or single trumpet note.
- More silence.
- The tension IS the space between events.

**Countermelody architecture:**
- Melody 1: the whistled main theme (any instrument, singable).
- Melody 2: a descending bass countermelody moving independently (cello, bass trumpet, or baritone voice).
- Ostinato: rhythmic/melodic pattern repeated beneath both (guitar or low strings).
- All three active simultaneously at different dynamics.

## Anti-patterns (what sounds wrong)

- **Conventional Hollywood orchestration.** Morricone doesn't sound like John Williams or Howard Shore. The "big orchestra sweeping strings + horns" sound is not Morricone — his is sparser, more eccentric.
- **Complex melody.** The primary melody must be simple. A complicated, hard-to-sing melody lacks Morricone's populist core.
- **Filling all the space.** The silence is part of the composition. A texture that is constantly active without pauses loses the tension that silence creates.
- **Single melodic layer.** Morricone builds simultaneous melodies. A single-melody texture is simpler than his most characteristic work.
- **Emotional homogeneity.** Morricone's best scores have extreme emotional contrasts within a single cue: a moment of violent percussion, then silence, then a heartbreaking melody.

## ShortScore Field Recommendations

**Eclectic solo:**
- `"instrument": "harmonica"` or `"instrument": "human_whistle"` for the solo line.
- Write every note of the solo melody explicitly.
- Supporting orchestra: pp, or completely absent (the solo is alone).

**Open-space tension:**
- `cb`/`vc`: `{"p": "E1", "d": "w"}` and `{"p": "B1", "d": "w"}` — open 5th, pp.
- All other voices: `{"p": "rest", "d": "w"}` for 2–4 bars.
- `"_feel": "silence — the tension is the space"`.

**Countermelody layers:**
- Write each layer explicitly as a separate voice.
- `"_feel": "layer 1: main melody; layer 2: bass countermelody; layer 3: rhythmic ostinato"`.
- Different dynamics: layer 1 = mp; layer 2 = p; layer 3 = pp.

**Dynamics:**
- Morricone: pppp to ff (rarely fff — he doesn't thunder).
- The pppp silence is as important as the ff climax.
- `"expr": "intenso"` for climactic passages.
- `"expr": "solitudine"` (solitude) for open-space passages.
