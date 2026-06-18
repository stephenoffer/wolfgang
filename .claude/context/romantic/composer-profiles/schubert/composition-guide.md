# Schubert — Composition Guide

## Fingerprints
Any section claiming Schubert's style needs ≥3 of these 5 present.

1. **Parallel major-minor shift (the Schubertian flip)** — Schubert moves between tonic major and tonic minor as a primary expressive device: C major → C minor → C major, without modulation. The shift carries immediate emotional weight: major is daylight, minor is shadow, and Schubert moves between them constantly. No other composer does this as naturally or as often.
2. **Third-relation harmony (mediant motion)** — Harmonic moves by major or minor third instead of fifth: C major → E major, or C major → Ab major, or C major → A major. These are not modulations — they are color shifts. The key a third away is not tension: it's a different light on the same landscape.
3. **Celestial prolongation — the moment that stops time** — Schubert's slow movements contain passages where the music seems to stop being in time: a single chord sustained for many bars, pp or ppp, high strings tremolo or no accompaniment at all, melody suspended in an impossible register. This is the Schubert "divine moment" — the music touching something beyond normal human experience.
4. **Song melody in instrumental writing** — Every Schubert melody sings. It's not abstract — it has breath, phrase shape, the cadence of a spoken sentence. The melody could be set to words. The piano or strings sing the melody; the accompaniment breathes with it.
5. **Wandering harmonic language — never quite settling** — Schubert's harmonic language creates restlessness: even in the tonic, a chromatic inflection or unexpected chord color suggests that rest is not final. His music wanders, and the listener never quite knows where home is — until the very end, and sometimes not even then.

---

## Note-Level Technique 1: Major-Minor Flip (One Note Changes Everything)

The Schubertian flip: C major → C minor, triggered by changing E→Eb (and nothing else). The melody may be IDENTICAL; only the third of the chord changes. Maximum emotional swing from minimum note change. Do not rewrite the melody — apply the third-change to the existing phrase.

**Same melody in C major, then C minor, then back:**
```json
{"bar_num": 1, "_feel": "C major — open, daylit", "voices": {
  "soprano": [
    {"p": "E5",  "d": "h",  "dyn": "mp", "expr": "innig"},
    {"p": "G5",  "d": "q"},
    {"p": "F5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","E3","C3"]}
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "E5",  "d": "dh"},
    {"p": "D5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","E3","C3"]}
}},
{"bar_num": 3, "_feel": "C minor — shadow descends. ONLY the third changes: E→Eb. Everything else identical.", "voices": {
  "soprano": [
    {"p": "Eb5", "d": "h",  "dyn": "p"},
    {"p": "G5",  "d": "q"},
    {"p": "F5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","Eb3","C3"]}
}},
{"bar_num": 4, "voices": {
  "soprano": [
    {"p": "Eb5", "d": "dh"},
    {"p": "D5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","Eb3","C3"]}
}},
{"bar_num": 5, "_feel": "C major returns — daylight again. One note. The world shifts twice.", "voices": {
  "soprano": [
    {"p": "E5",  "d": "h",  "dyn": "mp"},
    {"p": "G5",  "d": "q"},
    {"p": "F5",  "d": "q"}
  ],
  "bass": {"formula": "alberti", "bass": "C2", "chord_tones": ["G3","E3","C3"]}
}}
```
Bar 1–2: C major (E natural). Bar 3–4: C minor — change ONLY E→Eb in both RH melody and LH chord tones. Bar 5: back to C major. One note difference; the emotional shift is total. Mark: `"_feel": "tonic minor — same melody, different light"`.

---

## Note-Level Technique 2: Third-Relation Key Shift (C major → Ab major)

Schubert arrives at Ab major (a minor 3rd below C) without preparation — no dominant approach, no pivot chord. The new key simply begins on the next bar, heard immediately through the new chord. The effect: a veil descends, or a new landscape appears. Use at phrase endings.

**C major phrase ends; Ab major begins immediately:**
```json
{"bar_num": 8, "_feel": "C major phrase completes cleanly — the tonic is clear, the phrase is done", "voices": {
  "soprano": [{"p": "G4", "d": "w", "dyn": "mf"}],
  "bass": {"formula": "block_chord", "bass": "C2", "chord_tones": ["E3","G3","C4"]}
}},
{"bar_num": 9, "_feel": "Ab major — no preparation. A different, veiled light. Not darker — simply other.", "voices": {
  "soprano": [
    {"p": "C5",  "d": "h",  "dyn": "p"},
    {"p": "Eb5", "d": "h",  "art": "legato"}
  ],
  "bass": {"formula": "block_chord", "bass": "Ab1", "chord_tones": ["Eb3","Ab3","C4"]}
}},
{"bar_num": 10, "voices": {
  "soprano": [
    {"p": "Ab5", "d": "h",  "dyn": "mp"},
    {"p": "Eb5", "d": "h"}
  ],
  "bass": {"formula": "block_chord", "bass": "Ab1", "chord_tones": ["Eb3","Ab3","C4"]}
}},
{"bar_num": 11, "_feel": "Return to C major — equally without preparation. The parenthesis closes.", "voices": {
  "soprano": [{"p": "E4", "d": "w", "dyn": "p"}],
  "bass": {"formula": "block_chord", "bass": "C2", "chord_tones": ["E3","G3","C4"]}
}}
```
Bar 8: C major tonic. Bar 9: Ab major begins — bass drops from C to Ab (minor third lower), and the chord tones are from Ab major (Eb, Ab, C). No transition. Bar 11: C major returns equally abruptly. The third-relation key is a parenthesis — it opens and closes without modulation. Use `"_feel": "third-relation to Ab major — veiling, mysterious"`.

---

## Note-Level Technique 3: The Divine Moment (Time Stops)

A sustained passage of absolute stillness: one chord, pp or ppp, high strings only (low strings and bass tacet), no harmonic movement. Sustained for 3–8 bars. The chord may have harmonics (artificial or natural). The melody, if present, moves in very slow half notes. Time stops.

**Divine moment — E major triad, high strings, 4 bars:**
```json
{"bar_num": 15, "_feel": "The divine moment — time stops. One chord. The music touches something beyond.", "voices": {
  "vln1": [{"p": "G#6", "d": "w", "dyn": "ppp", "art": "harmonics", "expr": "wie aus der Ferne"}],
  "vln2": [{"p": "E6",  "d": "w", "dyn": "ppp"}],
  "vla":  [{"p": "B5",  "d": "w", "dyn": "ppp"}],
  "vc":   [{"p": "rest","d": "w"}],
  "cb":   [{"p": "rest","d": "w"}]
}},
{"bar_num": 16, "voices": {
  "vln1": [{"p": "G#6", "d": "w"}],
  "vln2": [{"p": "E6",  "d": "w"}],
  "vla":  [{"p": "B5",  "d": "w"}],
  "vc":   [{"p": "rest","d": "w"}],
  "cb":   [{"p": "rest","d": "w"}]
}},
{"bar_num": 17, "voices": {
  "vln1": [{"p": "G#6", "d": "w"}],
  "vln2": [{"p": "E6",  "d": "w"}],
  "vla":  [{"p": "B5",  "d": "w"}],
  "vc":   [{"p": "rest","d": "w"}],
  "cb":   [{"p": "rest","d": "w"}]
}},
{"bar_num": 18, "_feel": "The divine moment ends — the world resumes", "voices": {
  "vln1": [{"p": "B5",  "d": "h", "dyn": "pp"}, {"p": "A5",  "d": "h"}],
  "vln2": [{"p": "E5",  "d": "h"}, {"p": "D#5","d": "h"}],
  "vla":  [{"p": "B4",  "d": "h"}, {"p": "G#4","d": "h"}],
  "vc":   [{"p": "E3",  "d": "h", "dyn": "pp"}, {"p": "B2",  "d": "h"}]
}}
```
Bars 15–17: E major triad sustained (G#6, E6, B5). Low strings and bass: complete silence (rest for entire bars). Three bars with zero harmonic movement — the chord simply IS. Mark with `"expr": "wie aus der Ferne"` (as if from a distance). Bar 18: normal motion resumes — the vc re-enters, the harmony moves. The divine moment is bracketed.

---

## Pattern Directives

**Major-minor flip:**
- Establish C major for 4–8 bars.
- Without preparation: state C minor as the next phrase's key. One chord change: the third (E→Eb) is the entire shift.
- Continue in C minor for 4–8 bars.
- Return to C major: again, just change the third back.
- The emotional meaning: the same melody in a different emotional light.

**Third-relation motion:**
- At a phrase ending in C major: instead of going to G major (V) or F major (IV), go to E major (III) or Ab major (bVI).
- E major feels like "lifting" — brighter, slightly unreal.
- Ab major feels like "veiling" — darker, more mysterious.
- Both return to C major without formal modulation — they're parentheses.

**The divine moment:**
- Suddenly reduce to pp or ppp.
- Sustain a single chord for 4–8 bars: no harmonic movement.
- High strings or woodwinds only — low instruments silent.
- The melody, if present, is held on a single note or moves in very slow half-notes.
- Time seems to stop. This is the Schubertian transcendence.

**Wandering harmony:**
- In a 16-bar progression: avoid the tonic for 8–10 bars.
- Use sequential chromatic motion: chain of secondary dominants that doesn't resolve "correctly" but keeps moving.
- When the tonic finally arrives: it feels earned rather than inevitable.

## Anti-patterns (what sounds wrong)

- **Stable, goal-directed harmony.** Schubert doesn't drive toward cadences — he wanders. A Schubert passage that moves confidently from I to IV to V to I sounds like Haydn, not Schubert.
- **Absence of major-minor contrast.** The tonic major/minor oscillation is Schubert's most personal fingerprint. A piece without it is missing the Schubertian soul.
- **Short, decisive phrases.** Schubert's phrases extend — they don't end where you expect. A phrase that cadences at bar 4 feels too confident for Schubert. He always finds one more bar, one more inflection.
- **Virtuosity as goal.** Schubert is not a showman. His piano writing can be technically demanding but it never displays technique — it sings. A Schubert passage that sounds like a Liszt exercise is wrong.
- **Rhythmic complexity.** Schubert's rhythm is simple: song meter, walking bass, gentle accompaniment patterns. Complex cross-rhythm, syncopation, or irregular meter is not Schubert.

## ShortScore Field Recommendations

**Major-minor flip:**
- Identical melody notes in both major and minor versions; change only the third.
- Mark the shift: `"_feel": "tonic minor — same melody, different light"`.
- The shift itself needs no special marking — the notes tell the story.

**Third-relation key:**
- `"_feel": "third-relation to E major — lifting, slightly unreal"`.
- Write the new key's tonic chord as the next measure's first event; no dominant preparation.

**Divine moment:**
- `"dyn": "ppp"` for the sustained passage.
- Very long note values: whole notes, double whole notes if the meter allows.
- `"expr": "wie aus der Ferne"` (as if from a distance) — Schubert used this marking.
- No bass activity during sustained passages.

**Accompaniment:**
- `lh`: Alberti-style broken chord or straight arpeggiated eighth notes — simple, transparent.
- Never busy accompaniment during the divine moment.
- `"expr": "innig"` (intimate) for slow lyrical sections.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #6: Deceptive Cadence — Schubert avoids the tonic constantly; deceptive cadences are structural
- Technique #1: The Appoggiatura — Schubert's vocal melodies lean on dissonances that resolve by step
- Technique #3: Lament Bass — used in Schubert's tragic slow movements
- Technique #12: Dominant Pedal — the long unresolved dominant before Schubert's tonic arrivals
