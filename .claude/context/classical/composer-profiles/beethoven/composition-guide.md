# Beethoven — Composition Guide

**CRITICAL: Specify which Beethoven period before composing.** The three periods are fundamentally different aesthetics. Composing "Beethoven" without a period is composing nothing specific.

## Fingerprints

### Middle Period (the most requested — Op.59, Symphony 5, Waldstein, Appassionata)
Any section claiming middle-period Beethoven needs ≥3 of these 5 present:

1. **Motivic cell driving everything** — A 2–4 note rhythmic-melodic cell (the "fate" rhythm: ♩♩♩♩̄, the opening 5th leap, a scalar fragment) recurs constantly across all voices in development sections. NOT just in the melody — in the accompaniment, the bass, the inner voices. The cell IS the music.
2. **Sudden dynamic contrasts** — Subito piano after forte, or sforzando on unexpected beats. Not gradual crescendos — shocking contrasts. The sfz is placed off the downbeat to destabilize the meter.
3. **Modal mixture as drama** — bVI, bVII, iv in major contexts. The shift to the parallel minor is a dramatic event. The return to major after minor feels like genuine triumph, not just harmonic convenience.
4. **Sustained development that escalates** — Development sections don't wander; they build. Each sequence iteration is louder, higher, more harmonically intense. A 64-bar development should feel like it's physically arriving somewhere.
5. **False recapitulation / structural deception** — The return of the main theme in the wrong key (a third away, in the subdominant) before the real recapitulation. Or an expected climax that deflates to piano before rebuilding. Beethoven plays with formal expectations as a dramatic tool.

### Late Period (Op.106, Op.111, Op.131, Symphony 9)
Any section claiming late Beethoven needs ≥3 of these 5:

1. **Fugue as struggle** — Fugue appears not as Baroque exercise but as expression of psychological conflict. The counterpoint is tight, the entries overlapping, the texture dense. It *strains*.
2. **Variation as transcendence** — A simple theme is varied into something barely recognizable — ornamented to pure filigree, stripped to skeleton, inverted, fugued, absorbed into a new world. Each variation moves further from the theme.
3. **Radical harmonic relationship** — Key changes that skip traditional pivot chords: C major to Db major (a semitone), or C major to A major (a third) directly. These arrive without preparation.
4. **Extreme register contrasts** — Very high + very low simultaneously with a gap between them. Or a melody that descends into the bass register unexpectedly. Or a single high note held against a dense low cluster.
5. **Rests as structural events** — Silences that last more than a bar, placed at dramatic peaks. The silence IS the climax, not the note before or after it.

### Early Period (Op.1-22 — less commonly requested)
Fingerprints: Strong Classical phrase structure (Haydn influence), but with Beethoven's grander scale (longer phrases, more extensive development). Modal mixture present but not dominant. Formal subversion less extreme.

---

## Note-Level Technique 1: Motivic Cell Compression (Development Engine)

The motivic cell (2–4 notes) is presented, then compressed: 4 bars → 2 bars → 1 bar → fragments. This escalation is Beethoven's primary development technique. Each compression doubles the energy — the cell arrives twice as fast, twice as often.

**The "fate" cell (short-short-short-LONG = ♩♩♩𝅗𝅥) compressed through 8 bars:**
```json
{"bar_num": 1, "_feel": "Cell statement — full size, 2 bars", "voices": {
  "soprano": [
    {"p": "G4", "d": "e", "dyn": "ff", "art": "staccato"},
    {"p": "G4", "d": "e", "art": "staccato"},
    {"p": "G4", "d": "e", "art": "staccato"},
    {"p": "Eb4","d": "dh","dyn": "ff"}
  ],
  "bass": [{"p": "G2", "d": "e"}, {"p": "G2", "d": "e"}, {"p": "G2", "d": "e"}, {"p": "Eb2","d": "dh"}]
}},
{"bar_num": 2, "_feel": "Answering statement — cell repeated a 4th lower", "voices": {
  "soprano": [
    {"p": "F4", "d": "e"},
    {"p": "F4", "d": "e"},
    {"p": "F4", "d": "e"},
    {"p": "D4", "d": "dh"}
  ],
  "bass": [{"p": "F2", "d": "e"}, {"p": "F2", "d": "e"}, {"p": "F2", "d": "e"}, {"p": "D2","d": "dh"}]
}},
{"bar_num": 3, "_feel": "Compression to 1 bar — cell accelerates", "voices": {
  "soprano": [
    {"p": "E4", "d": "e", "dyn": "f"},
    {"p": "E4", "d": "e"},
    {"p": "E4", "d": "e"},
    {"p": "C4", "d": "q",  "dyn": "ff"}
  ],
  "bass": [{"p": "E2", "d": "e"}, {"p": "E2", "d": "e"}, {"p": "E2", "d": "e"}, {"p": "C2","d": "q"}]
}},
{"bar_num": 4, "_feel": "Cell again immediately — no gap, no breath. The pressure increases.", "voices": {
  "soprano": [
    {"p": "F4", "d": "e", "dyn": "ff"},
    {"p": "F4", "d": "e"},
    {"p": "F4", "d": "e"},
    {"p": "D4", "d": "q"}
  ],
  "bass": [{"p": "F2", "d": "e"}, {"p": "F2", "d": "e"}, {"p": "F2", "d": "e"}, {"p": "D2","d": "q"}]
}},
{"bar_num": 5, "_feel": "Fragment — only the first two notes of the cell. Maximum compression.", "voices": {
  "soprano": [
    {"p": "G4", "d": "e", "dyn": "ff", "art": "sfz"},
    {"p": "G4", "d": "e"},
    {"p": "Ab4","d": "e", "art": "sfz"},
    {"p": "Ab4","d": "e"}
  ],
  "bass": [{"p": "Eb2","d": "q"}, {"p": "Eb2","d": "q"}]
}}
```
Bars 1–2: full 2-bar cell statements. Bars 3–4: compressed to 1 bar each — the cell runs twice as fast. Bar 5: only the first 2 notes of the cell (short-short), repeated twice — fragment level. The dynamics escalate at each step. After this compression, the dominant pedal arrives, then the recapitulation.

---

## Note-Level Technique 2: Sforzando on Off-Beat (Metric Destabilization)

Beethoven places `sfz` markings on beats 2 or 3 in 4/4, or on the weak eighth note. The strong beat is suddenly weak; the weak beat is suddenly violent. The meter appears to have shifted — the listener momentarily loses the downbeat.

**Sforzandi on beats 2 and 4, then beat 2 only — metric ambiguity:**
```json
{"bar_num": 10, "_feel": "The accents shift the floor — where is beat 1?", "voices": {
  "soprano": [
    {"p": "C5", "d": "q"},
    {"p": "Eb5","d": "q", "dyn": "sfz"},
    {"p": "C5", "d": "q"},
    {"p": "Eb5","d": "q", "dyn": "sfz"}
  ],
  "bass": [{"p": "C2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "C2","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 11, "_feel": "Sfz lands on beat 2 — the downbeat is destabilized for 2 bars", "voices": {
  "soprano": [
    {"p": "D5", "d": "q"},
    {"p": "F5", "d": "q", "dyn": "sfz"},
    {"p": "D5", "d": "q"},
    {"p": "F5", "d": "q", "dyn": "sfz"}
  ],
  "bass": [{"p": "D2", "d": "q"}, {"p": "rest","d": "q"}, {"p": "D2","d": "q"}, {"p": "rest","d": "q"}]
}},
{"bar_num": 12, "_feel": "Sfz on beat 1 — the downbeat returns with violence", "voices": {
  "soprano": [{"p": "G4", "d": "w", "dyn": "sfz"}],
  "bass": [{"p": "G2", "d": "w", "dyn": "sfz"}]
}}
```
Bars 10–11: sfz always on beat 2 and 4. The LH rests on these beats — the accent is in the RH only, which makes the off-beat feel even more naked and displaced. Bar 12: sfz on beat 1 — the downbeat violently reinstated. The resolution of metric ambiguity IS the cadential gesture here.

---

## Note-Level Technique 3: False Recapitulation (Structural Deception)

The main theme returns in the WRONG key — typically the subdominant (IV) or a key a third away — before the real recapitulation arrives. The listener recognizes the theme and relaxes; then the "wrong" key reveals the deception; development continues; the real recapitulation arrives with greater force.

**Main theme in C minor, false recapitulation in Ab major (bVI):**
```json
{"bar_num": 55, "_feel": "False recapitulation — the theme is back, but wrong. Ab major, not C minor.", "voices": {
  "soprano": [
    {"p": "Eb5", "d": "q", "dyn": "p"},
    {"p": "F5",  "d": "q"},
    {"p": "G5",  "d": "q"},
    {"p": "Ab5", "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "Ab2", "chord_tones": ["Eb3","C4","Ab3"]}
}},
{"bar_num": 56, "voices": {
  "soprano": [
    {"p": "Bb5", "d": "h"},
    {"p": "Ab5", "d": "q"},
    {"p": "G5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "Ab2", "chord_tones": ["Eb3","C4","Ab3"]}
}},
{"bar_num": 57, "_feel": "The wrong key reveals itself — Ab harmonies are not the home. Development resumes.", "voices": {
  "soprano": [
    {"p": "G5",  "d": "q", "dyn": "mf"},
    {"p": "F5",  "d": "q"},
    {"p": "Eb5", "d": "q"},
    {"p": "D5",  "d": "q", "dyn": "f"}
  ],
  "bass": {"formula": "alberti", "bass": "G2", "chord_tones": ["D3","B3","G3"]}
}}
```
Bars 55–56: the theme arrives in Ab major — the listener hears the familiar theme, relaxes. Bar 57: the Ab begins moving toward G major (dominant) — the "wrong" key is being corrected. The real recapitulation in C minor will arrive 8–12 bars later with greater force, having been denied once.

---

## Pattern Directives

**Middle-period development sections:**
- Start with the main theme fragment, state it 4 bars, then answer in a related key 4 bars, then compress to 2-bar statements, then 1-bar, then fragment to single notes. This is the standard developmental escalation.
- Bass: rising or descending sequences (descending thirds are most common for building tension).
- Each iteration: stepwise upward (or downward) transpositional sequence. Arrive at a dominant pedal before the recapitulation.

**Beethoven accompaniment:**
- Never neutral. The LH/accompaniment part should participate in the motivic argument, not just provide harmonic support.
- In piano writing: LH often doubles or echoes the RH theme a bar later, or provides the answering phrase.
- Tremolo in the accompaniment for sustained tension (Moonlight Sonata model).

**Cadences:**
- PAC (perfect authentic cadence) is earned, not given. Beethoven often avoids the expected V→I, substituting a deceptive cadence (V→vi) to withhold resolution. When the PAC finally arrives, it's conclusive.
- Ends of movements: Beethoven often ends with multiple repeated cadences (coda reinforcing the tonic). Repetition here is NOT quota-filling — it IS the musical content (the insistence on arrival).

## Anti-patterns (what sounds wrong)

- **Smooth, predictable dynamics.** Beethoven's dynamics are violent: fff followed immediately by ppp. A smooth, well-behaved dynamic curve is Haydn, not Beethoven.
- **Development that meanders.** A development that passes through keys without building tension is un-Beethovenian. Development sections should feel like they're fighting their way toward the recapitulation.
- **Themes that don't develop.** Middle-period Beethoven themes exist *to be developed* — they are designed with motivic cells precisely so they can be broken apart. A theme that presents itself and is then not developed in any way is incomplete.
- **Late-period music without strangeness.** If a piece is described as late Beethoven and sounds comfortable and familiar, it's wrong. Late Beethoven is often strange, austere, or radically unconventional.
- **Missing sforzandi.** The sfz is Beethoven's rhythmic disruption tool — it should appear where the meter is being intentionally destabilized.

## ShortScore Field Recommendations

**Melody:**
- Write the cell first. Identify a 2–4 note unit (rhythmic + melodic) and make it the source of the melody, bass, and inner voices.
- Middle-period: strong rhythmic identity (dotted rhythms, syncopation) is more important than elegant melodic contour.

**Dynamics:**
- `"dyn": "sfz"` — placed on off-beats, on non-root chords, at moments of harmonic surprise
- Sudden `"dyn": "p"` after sustained forte without crescendo/diminuendo transition
- Development sections: escalating dynamic levels (mp → mf → f → ff across the span)

**Expression:**
- `"expr": "con fuoco"` — fast, driven passages
- `"expr": "espressivo"` — lyrical second themes
- `"expr": "pesante"` — heavy, deliberate forte passages

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #5: Ascending Sequence — the mechanical spine of Beethoven's development escalations
- Technique #6: Deceptive Cadence — Beethoven withholds V→I constantly; VI appears instead
- Technique #2: The 4-3 Suspension — used at structural cadences in lyrical second themes
- Technique #12: Dominant Pedal — the held dominant before recapitulation (the "held breath")
