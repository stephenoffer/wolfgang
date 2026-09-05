# Haydn — Composition Guide

## Fingerprints
Any section claiming Haydn's style needs ≥3 of these 5 present.

1. **Formal subversion** — Haydn sets up a structural expectation and then violates it for effect: a false recapitulation in the wrong key, a theme that arrives too early or too late, a fermata on an unexpected chord followed by piano instead of the expected climax, a movement that ends before the listener realizes it's ending. The humor IS the composition.
2. **Simple, folk-like themes with hidden sophistication** — Haydn's themes often sound almost naïvely simple at first (a scale, a repeated note, a folk-song interval). Their sophistication emerges in development: they turn out to be infinitely fragmented, sequenced, inverted. The simplicity is structural genius.
3. **Sudden dynamic contrast as punchline** — The famous "Surprise" (a loud orchestral crash after a soft passage) is representative: Haydn uses sudden forte after piano, or subito piano after forte, as structural jokes with perfect timing. The contrast is always in exactly the right place to maximally surprise.
4. **Monothematic sonata form** — In many Haydn movements, the "second theme" is actually a transformation of the first theme — not a contrasting melody but the same melody in a new harmonic context. The listener expects contrast; Haydn provides the same thing cleverly disguised.
5. **String quartet as conversation** — Each instrument in the quartet has an equal and individual voice. The first violin doesn't dominate — the cello gets melodic statements, the viola has its own character, the second violin completes what the first violin started. Real four-way conversation.

## Pattern Directives

**Sonata form first movement:**
- Exposition: main theme (tonic), transition (modulating), secondary theme (dominant — which may be a transformation of main theme), codetta.
- Development: fragment the theme into its smallest cell, sequence it through related keys, build toward dominant preparation.
- Recapitulation: may arrive in unexpected way (wrong key, delayed, shortened).
- **Haydn specific:** Don't always signal the recapitulation clearly. The false recapitulation in a wrong key, followed by the true one, is the Haydn structural joke.

**String quartet writing:**
- Assign melodic interest to all four instruments across the movement.
- Cello gets at least one melodic phrase per movement (not just bass function).
- Viola provides inner harmonic interest — not just sustained chords.
- Second violin responds to first violin phrases (dialogue, not accompaniment).

**Theme development:**
- Start with the complete theme (8 bars). Then in development, use only the first 2 bars. Then only the first bar. Then a single note's rhythm. The fragmentation reveals the theme's genetic material.
- Sequence: state the fragment, repeat it a step lower, repeat again — each time harmonically moving (circle of fifths or descending thirds).

**Humor:**
- False cadence: approach V→I and substitute V→vi (deceptive cadence). Then pause. Then complete V→I. Timing is everything.
- Unexpected silence: place a fermata on a dissonant chord. Then piano resolution.
- Extended piano section where forte is expected: delay the expected tutti.

## Anti-patterns (what sounds wrong)

- **Second themes that are completely different in character from the first.** Haydn's second themes often surprise by being the same material. A dramatically different second theme is more Beethoven/Schubert than Haydn.
- **No formal wit.** A perfectly regular Haydn movement that never subverts a single expectation is not Haydn — it's a theory textbook exercise.
- **First violin dominance.** If the cello only plays bass notes for the entire movement, it's not a Haydn quartet — it's a melody with bass accompaniment and two filler parts.
- **Heavy orchestration.** Haydn's sound is clear and balanced. Thick, doubly-reinforced textures belong to Beethoven's expanded orchestra.
- **Undifferentiated instruments.** In a symphony, the woodwind instruments should have distinct personalities — they're not just string reinforcement.

## ShortScore Field Recommendations

**First movement (4/4 Allegro):**
- Main theme: clear, simple, rhythmically defined. Should be singable and memorable.
- Development fragment: take just the first 4 notes of the theme and sequence them.
- Recapitulation: may arrive quietly, in wrong key briefly, or with textural change.

**String quartet voicing:**
- `vln1`: primary melody, but give the cello a melody in at least one movement.
- `vln2`: harmonizes in thirds/sixths below vln1, or provides rhythmic complement.
- `vla`: inner voice — often moving against the outer voices when others are static.
- `vc`: bass function primarily, but one 8-bar solo statement per movement.

**Dynamics:**
- The "Surprise" principle: use `"dyn": "f"` where the listener expects `"p"`, and vice versa. At least once per section.
- Extended piano passages suddenly interrupted by forte outburst.
- Use `"dyn": "fp"` at structural surprise points.

---

## Composing a Haydn phrase: step by step

The organising fact is **wit**, which in music means setting up an expectation
precisely and then not meeting it. A Haydn phrase that behaves is a Mozart
phrase.

### Step 1 — State a short, plain idea

Shorter than Mozart's and deliberately ordinary — often just a triad in rhythm.
The material has to be simple enough that the audience notices what happens to
it later.

```json
"opening_idea": [
  {"p": "D5", "d": "q", "dyn": "f"},
  {"p": "D5", "d": "e"},
  {"p": "D5", "d": "e"},
  {"p": "F#5", "d": "q"},
  {"p": "A5", "d": "q"}
]
```

### Step 2 — Answer it, and cadence on the dominant

Four bars out, four bars back. The answer is the same idea adjusted to close on
V — the antecedent-consequent frame the joke will later break.

### Step 3 — Break the phrase length

Now write the third phrase **five bars long, or three**. Extend by repeating the
cadential bar, or cut by eliding the last bar of one phrase with the first of
the next. This is the single most Haydnesque thing available and Mozart does it
far less.

```json
"elided_cadence": [
  {"p": "A4", "d": "q"},
  {"p": "G4", "d": "q"},
  {"p": "F#4", "d": "h"},
  {"p": "D5", "d": "q", "dyn": "f"},
  {"p": "D5", "d": "e"},
  {"p": "D5", "d": "e"}
]
```

The F#4 resolves the phrase and the next idea starts in the same bar. The seam
is the point.

### Step 4 — Put the silence in

A general pause where the ear expects the next bar. Haydn stops the music mid-
sentence more than any composer before Beethoven, and the rest is the joke.

```json
"the_pause": [
  {"p": ["D4", "F#4", "A4"], "d": "q", "dyn": "ff"},
  {"p": "rest", "d": "q"},
  {"p": "rest", "d": "h"},
  {"p": ["A3", "C#4", "E4"], "d": "h", "dyn": "pp"}
]
```

### Step 5 — Keep the accompaniment sparse and let it rest

Real Haydn bars are full of long values and rests. His left hand is thinner than
Mozart's — repeated block triads, an open fifth drone from the folk dances, and
whole bars where it simply does not play.

```json
"sparse_accompaniment": [
  {"p": ["D3", "F#3", "A3"], "d": "q"},
  {"p": "rest", "d": "q"},
  {"p": ["D3", "F#3", "A3"], "d": "q"},
  {"p": "rest", "d": "q"}
]
```

### Step 6 — Develop by fragmenting, not by spinning out

Take the first three notes of the idea and sequence them through remote keys.
Haydn develops one small cell hard, where Mozart introduces new material.

---

## Checking a finished phrase

- Is any phrase not four bars long? At least one should not be.
- Is there a real silence anywhere?
- Does the left hand ever stop?
- Was the surprise set up plainly enough that it registers as one?
