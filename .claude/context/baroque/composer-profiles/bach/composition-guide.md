# Bach — Composition Guide

## Fingerprints
Any section claiming Bach's style needs ≥3 of these 5 present, or each absence requires artistic justification.

1. **Continuous forward motion** — The melody never stops moving. Sixteenth-note figuration fills most bars; rests are structural arrivals, not breathing spaces. Baroque spinning (Fortspinnung): a short head-motif generates the rest of the phrase through sequence and inversion.
2. **Imitative counterpoint** — At least one other voice echoes or responds to the main voice within 2–4 bars. In fugue: strict imitation at a fifth above/below. In invention: freer imitation. In accompanied melody: the bass line derives its shape from the melody's intervals.
3. **Sequence as developmental engine** — Ascending or descending sequences of 3–4 repetitions move the music forward. The sequence is harmonically directed (circle-of-fifths, descending thirds, ascending seconds) and never just decorative.
4. **Functional harmony with expressive chromaticism** — IV, V, I as the harmonic backbone. But within that, altered chords (diminished sevenths, secondary dominants, augmented sixths) appear freely — not as surprises but as logical voice-leading consequences.
5. **Motivic saturation** — A short 2–4 note cell from the opening generates everything: the melody, the bass line, the inner voices, the countersubject. If you can trace every important note back to the opening motif, it's Bach.

---

## Composing a Bach Phrase: Step by Step

Bach writes from the bass. The bass line is not accompaniment — it is a second melody, equally strong. Every melodic decision in the upper voice is constrained by what the bass is doing. Write the bass first.

### Step 1 — Write the bass line as a melody

The bass line has:
- Clear harmonic targets (root arrivals on strong beats)
- Stepwise motion between targets (walking, not leaping)
- Its own shape: rise, peak, cadential fall

**Walking bass in D minor, 4 bars (ii–V–i–iv):**
```json
{"bar_num": 1, "voices": {
  "bass": [
    {"p": "G2", "d": "q"}, {"p": "A2",  "d": "q"},
    {"p": "Bb2","d": "q"}, {"p": "C3",  "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "bass": [
    {"p": "A2", "d": "q"}, {"p": "G2",  "d": "q"},
    {"p": "F2", "d": "q"}, {"p": "E2",  "d": "q"}
  ]
}},
{"bar_num": 3, "voices": {
  "bass": [
    {"p": "D2", "d": "q"}, {"p": "E2",  "d": "q"},
    {"p": "F2", "d": "q"}, {"p": "G2",  "d": "q"}
  ]
}},
{"bar_num": 4, "voices": {
  "bass": [
    {"p": "G2", "d": "q"}, {"p": "A2",  "d": "q"},
    {"p": "Bb2","d": "q"}, {"p": "A2",  "d": "q"}
  ]
}}
```
Bass: G–A–Bb–C (bar 1, ascending), then A–G–F–E (bar 2, descending through dominant), then D–E–F–G (bar 3, tonic then ascending), then G–A–Bb–A (bar 4, approaching cadence). Stepwise throughout. A bass line like this IS a countermelody to what the RH plays above it.

### Step 2 — Write the RH as continuous sixteenth figuration

The RH never rests between structural arrivals. The head motif generates sixteenth note passagework. Strong beats (1 and 3) must land on chord tones or structurally strong scale degrees. Beats 2 and 4 are passing or neighbor tones.

**RH over the D minor bass above, bar 1 (Gm chord — beat 1 target is G or Bb or D):**
```json
{"bar_num": 1, "voices": {
  "soprano": [
    {"p": "D5",  "d": "s"}, {"p": "C5",  "d": "s"},
    {"p": "Bb4", "d": "s"}, {"p": "A4",  "d": "s"},
    {"p": "G4",  "d": "s"}, {"p": "A4",  "d": "s"},
    {"p": "Bb4", "d": "s"}, {"p": "C5",  "d": "s"},
    {"p": "D5",  "d": "s"}, {"p": "Eb5", "d": "s"},
    {"p": "F5",  "d": "s"}, {"p": "G5",  "d": "s"},
    {"p": "A5",  "d": "s"}, {"p": "Bb5", "d": "s"},
    {"p": "A5",  "d": "s"}, {"p": "G5",  "d": "s"}
  ],
  "bass": [
    {"p": "G2", "d": "q"}, {"p": "A2",  "d": "q"},
    {"p": "Bb2","d": "q"}, {"p": "C3",  "d": "q"}
  ]
}}
```
16 sixteenth notes fill bar 1. Beat 1 = D5 (5th of Gm, strong). Beat 2 = G4 (root, strong after passing tones). Beat 3 = D5 again (5th, strong). The line rises from D5 through an octave to D6, then falls back. The shape is a wave: rise then fall. The passing tones (C5, A4, Eb5) connect the chord tones.

### Step 3 — Write the sequence

After stating the opening 2-bar unit, repeat it starting a step or third lower. This is how Bach propels music forward: the same shape, harmonically transposed downward through the circle of fifths.

**Sequence: bar 1-2 cell stated in D minor, then repeated in C major (a step lower), then Bb major:**
- Bar 1–2: D minor. RH pattern starting on D5.
- Bar 3–4: C major. Same RH shape starting on C5, bass adjusted to C–D–E–F.
- Bar 5–6: Bb major. Same RH shape starting on Bb4, bass adjusted to Bb–C–D–Eb.
- Bar 7–8: Arrives on A major (dominant of D minor) — the sequence has traveled a fifth.

Each repetition: same note values, same direction, different pitch level. The listener tracks the shape, not the individual notes — and feels the harmonic journey.

### Step 4 — Add imitation

If there are two independent voices (two-part invention, violin + bass, etc.), the second voice enters 2 bars after the first with the same opening motif, a fifth lower (or fourth higher):

```json
{"bar_num": 1, "voices": {
  "vln": [
    {"p": "D5", "d": "s"}, {"p": "C5", "d": "s"}, {"p": "Bb4","d": "s"}, {"p": "A4", "d": "s"},
    {"p": "G4", "d": "s"}, {"p": "A4", "d": "s"}, {"p": "Bb4","d": "s"}, {"p": "C5", "d": "s"},
    {"p": "D5", "d": "q"}, {"p": "E5", "d": "q"}
  ],
  "vc": [{"p": "D2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "vln": [
    {"p": "F5", "d": "s"}, {"p": "E5", "d": "s"}, {"p": "D5", "d": "s"}, {"p": "C5", "d": "s"},
    {"p": "Bb4","d": "s"}, {"p": "A4", "d": "s"}, {"p": "G4", "d": "s"}, {"p": "F4", "d": "s"},
    {"p": "E4", "d": "q"}, {"p": "F4", "d": "q"}
  ],
  "vc": [{"p": "A1", "d": "h"}, {"p": "G1", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "vln": [{"p": "G4", "d": "h"}, {"p": "F4", "d": "q"}, {"p": "E4", "d": "q"}],
  "vc": [
    {"p": "G1", "d": "s"}, {"p": "F1", "d": "s"}, {"p": "E1", "d": "s"}, {"p": "D1", "d": "s"},
    {"p": "C2", "d": "s"}, {"p": "D2", "d": "s"}, {"p": "E2", "d": "s"}, {"p": "F2", "d": "s"},
    {"p": "G2", "d": "s"}, {"p": "A2", "d": "s"}, {"p": "Bb2","d": "s"}, {"p": "C3", "d": "s"},
    {"p": "D3", "d": "q"}, {"p": "E3", "d": "q"}
  ]
}}
```
Bar 1: violin starts with the motif. Bar 3: cello enters with the same motif but starting on G (a fifth lower). While the cello states the opening motif, the violin has moved on to continuation material. The two voices never align on the same rhythmic beat — they overlap, like a conversation where each speaker begins before the other has finished.

---

## The Bach Cadence

A Bach phrase always ends on a clear harmonic arrival with a trill on the penultimate note. The trill is not optional — it IS the cadential gesture.

**Authentic cadence arrival in D minor (V → i):**
```json
{"bar_num": 8, "voices": {
  "soprano": [
    {"p": "E5",  "d": "e", "dyn": "mf"},
    {"p": "D5",  "d": "e", "orn": "trill"},
    {"p": "C#5", "d": "q"},
    {"p": "D5",  "d": "h"}
  ],
  "bass": [
    {"p": "A2",  "d": "h"},
    {"p": "D2",  "d": "h"}
  ]
}}
```
E5 (approach), D5 with trill (the resolving note, trilled from E5), C#5 (leading tone approaching final D5), D5 (tonic arrival). Bass: A2 (dominant) → D2 (tonic). The trill marks the cadence; the leading tone C#5 confirms the dominant resolution. This is Bach's cadential fingerprint.

---

## Anti-patterns

- **Melody that rests mid-phrase.** Bach melodies breathe via phrase overlap, not actual rests. A melody that stops for a full beat in mid-phrase breaks the forward flow.
- **Block chord accompaniment.** Every voice must move — the bass line is a melody.
- **Dynamic hair-pins within a phrase.** Baroque dynamics are terraced (forte vs. piano) not graduated crescendos. No `<` or `>` hairpins.
- **Simple diatonic melody without motivic development.** A melody that just steps up and down without a driving cell is not Bach.
- **Parallel fifths or octaves between outer voices.** These are forbidden. Check every bar.
- **Sequences that don't modulate.** Bach's sequences almost always pass through a key area.
- **Cadence without a trill** on the penultimate note. No trill = no cadence in this style.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #4: Walking Bass (exactly how to construct the bass line step-by-step)
- Technique #5: Ascending Sequence (how to build and sequence a 2-bar cell)
- Technique #12: Dominant Pedal (suspense before a structural cadence)
- Technique #13: Cadential 6/4 → V → I (standard phrase closure)
