# Melody Craft — Writing Themes That Sing

> **Scope:** Artistic intent — why themes work, what makes them memorable, how to think about melody as expression. For technical construction (phrase structure, intervals, contour shapes), see `melodic-construction.md`.

## The Melody-First Principle

A theme is not chord tones arranged horizontally. Before thinking about harmony, voicing, or orchestration, the melody should exist as a **singable, independent line** — something a person could hum walking down the street and recognize instantly.

**The Hum Test**: Imagine hearing only the first 4 notes of your theme, unaccompanied. Would you recognize it? If those notes could belong to any piece, the theme lacks identity. Every great theme has a **fingerprint** — a rhythmic cell, a signature interval, a distinctive contour — that makes it unmistakable.

**Melody vs. Chord-Tone Noodling**: If the melody only touches chord tones on every beat, it sounds like an arpeggiated accompaniment rather than a singing voice. Real melodies create tension against the harmony through non-chord tones (appoggiaturas, suspensions, passing tones) on strong beats, resolving to chord tones — this is what gives melody its expressive power.

**The Breath Principle**: A melody breathes like a human voice. It rises with inhalation (tension) and falls with exhalation (release). Phrases have natural resting points. Even in instrumental music, the greatest melodies respect the singer's breath — because that's how the human brain processes melodic shape.

---

## Psychology of Memorable Melody

What makes a theme stick in the listener's memory? Research in music cognition reveals consistent patterns across centuries of memorable themes.

### The Hook

Every memorable theme has one distinctive element — the **hook** — that identifies it instantly:

| Hook Type | Mechanism | Famous Example |
|-----------|-----------|----------------|
| Rhythmic cell | Unique rhythm pattern | Beethoven 5th: short-short-short-LONG |
| Signature interval | One striking leap | Tchaikovsky Swan Lake: minor 6th leap |
| Contour shape | Distinctive melodic arc | Ode to Joy: steady rise then gentle fall |
| Rhythmic surprise | Syncopation or meter play | Brahms 3rd: hemiola across barline |
| Opening gesture | Arresting first notes | Rachmaninoff PC3: single stepwise ascent |

### Gap-Fill (Narmour's Implication-Realization)

A large leap creates an **implication** — the listener's ear expects stepwise motion to fill the gap. Satisfying this expectation creates melodic coherence; delaying it creates tension.

| Pattern | Mechanism | Emotional Effect |
|---------|-----------|-----------------|
| Leap up → stepwise descent | Gap filled immediately | Yearning, then settling |
| Leap up → more leaps | Gap unfilled, tension builds | Excitement, instability |
| Leap up → hover → stepwise fill | Delayed satisfaction | Suspense, then relief |
| Stepwise rise → leap down | Reversal of expectation | Surprise, dramatic |
| Leap up → leap down (opposite) | Compensatory motion | Balance, classical poise |

```abc
X:1
T:Gap-fill examples
M:4/4
L:1/8
K:C
% Leap up (M6), then stepwise descent filling the gap
C2 A2 G2 F2 | E2 D2 C4 ||
% Leap up, delayed fill — hover before descending
C2 A2 B2 A2 | G2 F2 E2 D2 | C6 z2 ||
```

### Repetition-Surprise Balance

The brain craves patterns AND novelty. Memorable melodies repeat their core idea 2-3 times, then **surprise** at the cadence:

```
Statement:    [core idea] ────────────── (recognition)
Repetition:   [core idea, slightly varied] (confirmation)
Surprise:     [different ending / new direction] (delight)
```

This is why consequent phrases work: the listener recognizes the antecedent's opening, relaxes into familiarity, then is rewarded with a new cadential resolution.

### Conjunct-Disjunct Balance

Memorable melodies are predominantly **stepwise** (easy to follow, singable) with **strategic leaps** at moments of emotional emphasis:

| Balance | Character | Risk |
|---------|-----------|------|
| All stepwise | Smooth but potentially bland | Can feel like a scale exercise |
| Mostly stepwise, 1-2 leaps | Ideal for lyrical themes | None — this is the sweet spot |
| Frequent leaps | Dramatic, angular | Can lose singability |
| All leaps | Virtuosic, fragmented | Loses melodic coherence |

Common-practice melodies are often roughly 70-80% stepwise motion with leaps placed at phrase peaks or emotional turning points. This varies widely by style — Baroque Fortspinnung may be more stepwise, angular Modern themes far less so, and fanfare themes are heavily triadic/disjunct.

### The Zeigarnik Effect

The brain remembers incomplete patterns more vividly than completed ones. Melodically, this means:
- **Half cadences** within a theme create forward pull — the ear needs resolution
- **Deceptive cadences** at phrase endings keep the listener leaning in
- **Sequences that break pattern** on the third repetition create surprise through incompleteness
- The antecedent phrase of a period IS the Zeigarnik effect in action — it poses a question the ear demands be answered

---

## Phrase Architecture — Step-by-Step Construction

### Building a Period (Antecedent + Consequent)

The period is the most fundamental melodic structure. It creates a question-and-answer effect.

**Step 1 — Antecedent (the question):**
- Bars 1-2: Opening gesture — this IS the hook. Make it distinctive.
- Bars 3-4: Develop the opening idea, arrive at a **half cadence** (on V). The phrase feels incomplete.

**Step 2 — Consequent (the answer):**
- Bars 5-6: Begin with the **same or similar** opening gesture (recognition). The listener thinks "I know this."
- Bars 7-8: **Diverge** from the antecedent, arrive at a **perfect authentic cadence** (V-I). Resolution.

```abc
X:2
T:Period — Lyrical theme in G major
M:4/4
L:1/8
K:G
% Antecedent: opens with hook (dotted rhythm + leap), ends on half cadence (D)
"mp"B,3 D G2 A2 | B3 A G2 E2 | D3 E F2 G2 | A6 z2 |
% Consequent: same opening, different ending → PAC on G
B,3 D G2 A2 | B3 A G2 B2 | A3 G F2 E2 | D2 G4 z2 ||
```

**Why this works:**
- Hook: dotted rhythm on B→D (rising 3rd, distinctive rhythmic cell)
- Gap-fill: after the leap B→D, stepwise motion continues upward then returns
- Antecedent ends on A (dominant area) — incomplete
- Consequent reuses bars 1-2 exactly (recognition), then diverges to cadence on G

### Building a Sentence (Presentation + Continuation)

The sentence builds momentum through repetition and fragmentation.

**Step 1 — Basic idea (2 bars):** The hook. Short, distinctive.
**Step 2 — Repetition (2 bars):** Repeat or vary at a new pitch level (sequence).
**Step 3 — Continuation (4 bars):** Fragment the basic idea, accelerate the harmonic rhythm, drive toward cadence.

```abc
X:3
T:Sentence — Heroic theme in D major
M:4/4
L:1/8
K:D
% Basic idea (hook: triadic leap + rhythmic cell)
"f"D2 F2 A2 d2 | c2 B2 A4 |
% Repetition — same rhythm, up a step
E2 G2 B2 e2 | d2 c2 B4 |
% Continuation — fragment (first 4 notes only), accelerate, cadence
D2 F2 A2 z2 | E2 G2 B2 z2 | A3 G F2 E2 | D6 z2 ||
```

**Why this works:**
- Basic idea: triadic ascent (hook) + stepwise descent (release)
- Repetition: same shape, one step higher (sequence = building energy)
- Continuation: only the ascending fragment remains (fragmentation), two quick statements, then cascading descent to cadence (liquidation)

### Phrase Extension Techniques

When 8 bars feel too short or too predictable:

| Technique | How It Works | Effect |
|-----------|-------------|--------|
| Deceptive cadence | Replace expected I with vi or bVI at bar 8 | "Not yet!" — extends by 2-4 bars |
| Sequential extension | Add a sequence at bars 5-6 before cadencing | Builds momentum, delays arrival |
| Cadential expansion | Stretch the final cadence with I6/4 → V7 → I | Grandeur, weight at the ending |
| Internal expansion | Repeat bars 3-4 at new pitch before continuing | Widens the middle, creates breadth |
| Evaded cadence | Approach cadence, then restart the phrase | Heightens tension dramatically |

### Asymmetric Phrases

Not all themes follow 4+4 bar structures. Asymmetry creates surprise and naturalness:

| Grouping | Character | Example Context |
|----------|-----------|-----------------|
| 3+5 | Short question, expansive answer | Romantic themes, improvisatory feeling |
| 2+6 | Brief spark, long development | Motive-based themes (Beethoven style) |
| 5+3 | Expansive opening, terse conclusion | Declamatory, dramatic |
| 4+6 | Regular question, extended answer | Phrase extension via deceptive cadence |
| 3+3+2 | Three-part grouping, compressed close | Folk-derived themes, dance-like |

---

## Melodic Devices — The Craft Toolkit

These devices transform simple note sequences into expressive melody.

| Device | Technique | Emotional Effect | ABC Example |
|--------|-----------|-----------------|-------------|
| Appoggiatura | Non-chord tone on strong beat → step resolution | Expressive peak, "leaning" | `c4 B4` (c is appog. over G chord) |
| Suspension | Hold note from previous chord into new chord | Aching, delayed resolution | `G4- \| G2 F4` (G suspended over F chord) |
| Escape tone | Stepwise approach, leap away | Unexpected turn, wit | `E2 F2 A4` (F escapes up to A) |
| Anacrusis (pickup) | Start before the downbeat | Forward momentum, urgency | `z6 EF \| G4` |
| Sequence | Repeat phrase at new pitch (typically 2-3 times) | Building intensity, direction | `CE \| DF \| EG` (ascending) |
| Melodic acceleration | Note values shorten approaching climax | Excitement, drive | `C4 D4 \| E2 F2 G2 A2 \| Bcde` |
| Melodic deceleration | Note values lengthen at cadence | Weight, arrival, grandeur | `ABGA \| B2 A2 \| G6` |
| The "sigh" | Descending step on strong beat (often m2) | Sadness, tenderness | `_e4 d4` (appog. sigh) |
| The "reaching" leap | Ascending 6th/7th, then stepwise descent | Yearning, aspiration | `E2 c2 B2 A2 \| G4` |
| Melodic pedal | Melody returns repeatedly to one note | Obsession, insistence | `G2 A2 G2 B2 \| G2 c2 G4` |

---

## Great Theme Analysis — Why Famous Themes Work

### Beethoven — Symphony No. 5, 1st Movement
```abc
L:1/8
K:Cm
M:2/4
z G G G | _E6 | z F F F | D6 ||
```
- **Hook**: Rhythmic cell (short-short-short-LONG) — one of the most recognizable patterns in music
- **Economy**: Only 4 pitches. The rhythm IS the theme
- **Gap-fill**: The m3 descent (G→Eb) is immediately echoed by (F→D), creating sequential momentum
- **Why it works**: The rhythm is so distinctive that it can be developed, fragmented, augmented, inverted — and remain recognizable in any transformation. This is the ultimate motive-based theme

### Beethoven — "Ode to Joy" (Symphony No. 9)
```abc
L:1/4
K:D
M:4/4
F F G A | A G F E | D D E F | F3/2 E/ E2 |
F F G A | A G F E | D D E F | E3/2 D/ D2 ||
```
- **Hook**: Pure stepwise simplicity — like a folk song anyone could sing
- **Sentence structure**: Basic idea (bars 1-2), varied repeat (3-4), continuation (5-8)
- **Climax at bar 5**: Highest note (A) returns after the descent, golden-section placement
- **Repetition-surprise**: Bars 1-4 and 5-8 begin identically, but the cadence differs (F→E vs E→D)
- **Why it works**: Radical simplicity. The theme feels inevitable, as if it always existed. Its stepwise motion makes it universally singable

### Tchaikovsky — Swan Lake Theme
```abc
L:1/8
K:Bm
M:4/4
B,2 z2 B2 d2 | c2 B2 A2 G2 | ^F3 G A2 B2 | G4 E4 |
B,2 z2 B2 d2 | c2 B2 ^A2 B2 | e3 d c2 B2 | ^A4 B4 ||
```
- **Hook**: The opening leap B→D (minor 3rd) after silence, then the yearning ascent B→D (octave context)
- **Gap-fill**: After each ascending leap, stepwise descent follows — the melody "reaches" then "settles"
- **Contour**: Arching — rises to peak, then gracefully descends. Mirrors the swan's neck
- **Why it works**: The oboe timbre + minor mode + arching contour creates an ache. The melody breathes — rests at the start give it space

### Dvořák — Symphony No. 9 "New World," Largo
```abc
L:1/4
K:Db
M:4/4
E | D B, B, z | B, A, B, D | E2 E z | E D B, z |
B, A, B, D | E3 z | E D B, D | E2 z ||
```
- **Hook**: Pentatonic simplicity — only 5 notes, folk-song quality
- **Breath**: Natural phrasing with rests, as if a singer is breathing between phrases
- **Narrow range**: Barely exceeds a 5th. Intimate, human, unforced
- **Why it works**: The English horn timbre + pentatonic scale + breathing pauses create a feeling of nostalgia so universal that it became "Goin' Home." Simplicity is the ultimate sophistication

### Mozart — Eine Kleine Nachtmusik, 1st Movement
```abc
L:1/8
K:G
M:4/4
G2 z D G2 z D | GBDG B2 z2 | c2 z A c2 z A | cAFA c2 z2 ||
```
- **Hook**: Triadic energy — the melody IS the G major chord, stated as a rhythmic fanfare
- **Period structure**: Antecedent (G major triadic gesture) → Consequent (C major, answering)
- **Rhythmic precision**: Crisp dotted patterns, rests as punctuation. Every note is placed with intention
- **Why it works**: The marriage of triadic simplicity with rhythmic crispness creates instant energy. The rests are as important as the notes — they give the melody swagger

### Rachmaninoff — Piano Concerto No. 3, Opening
```abc
L:1/8
K:Dm
M:4/4
D2 E2 F2 A2 | G2 F2 E2 D2 | E2 F2 G2 E2 | F4 E2 D2 |
C2 D2 E2 C2 | D2 E2 F2 D2 | E3 F G2 A2 | B2 A2 G2 F2 ||
```
- **Hook**: There IS no single hook — the hook is the quality of the LINE itself: long, stepwise, breathing
- **Narrow range**: Only a 6th for the first 4 bars. The melody is intimate, almost whispered
- **Russian character**: Predominantly stepwise, minor mode, with that particular melancholy of Russian folk melody
- **Late climax**: The melody's peak arrives in bar 7-8, after slow building — a deep breath before the exhale
- **Why it works**: The theme is so long-breathed and organic that it feels improvised, as if the pianist is singing. It needs no harmonic support to be beautiful — pure melodic line

### Debussy — Prélude à l'après-midi d'un faune
```abc
L:1/16
K:none
M:none
C2 _D2 _E2 F2 _A4 _A4 | _A2 G2 F2 _E2 _D2 F2 _E4 |
C2 _D2 _E2 F2 _A4 G4 | F2 _E2 _E2 _D2 C6 z2 ||
```
- **Hook**: The chromatic, sinuous descent — like a faun's breath, warm and languid
- **No clear key**: Whole-tone and chromatic elements. The melody floats rather than marches
- **Asymmetric**: Phrases don't conform to 4+4 — the melody unfolds organically
- **Why it works**: The flute's breathy timbre + chromatic wandering + rubato rhythm create pure sensuality. This is melody as color and atmosphere, not as architecture

### Brahms — Symphony No. 3, 1st Movement
```abc
L:1/4
K:F
M:6/4
F A _A | F2 (c | d) _d c | (c B) A ||
```
- **Hook**: The opening F→A→Ab — major 3rd leap immediately undermined by the chromatic Ab. Three notes, and the entire piece's tension is established
- **Modal ambiguity**: Major or minor? The Ab creates doubt. This tension drives the entire symphony
- **Wide arch**: The melody sweeps upward to D then descends — heroic but shadowed
- **Why it works**: The third note (Ab) is the genius stroke. It transforms a simple triadic fanfare into something questioning, conflicted, deeply Romantic

---

## Theme Voicing Progression

How a theme is **presented** matters as much as the notes themselves. Plan how voicing evolves across the piece:

| Appearance | Voicing | Character | Dynamic |
|-----------|---------|-----------|---------|
| First statement | Solo instrument, sparse accompaniment | Intimate — audience learns the melody | p - mp |
| Confirmation | Same instrument or section, richer accompaniment | Familiarity, warmth | mp - mf |
| Enriched return | Doubled in octaves or 3rds/6ths | Growing importance | mf |
| Development | Fragmented, Klangfarbenmelodie, passed between instruments | Exploration, transformation | varies |
| Climactic statement | Tutti, full voicing, 3+ octave span | Apotheosis, maximum impact | f - ff |
| Final appearance | Solo again (intimate closure) OR massive peroration | Resolution | pp or ff |

### ABC — Same Theme, Three Voicings
```abc
X:4
T:Theme voicing — First statement (solo oboe)
M:4/4
L:1/8
K:Eb
V:Ob name="Oboe"
V:Str name="Strings"
[V:Ob] "mp"B,2 E2 G2 F2 | A2 G2 F2 E2 | D2 F2 B2 A2 | G6 z2 |
[V:Str] z8 | z8 | z8 | z8 |

X:5
T:Theme voicing — Enriched (melody doubled in 3rds)
M:4/4
L:1/8
K:Eb
V:Vn1 name="Violin I"
V:Vn2 name="Violin II"
V:Va name="Viola"
[V:Vn1] "mf"B,2 E2 G2 F2 | A2 G2 F2 E2 | D2 F2 B2 A2 | G6 z2 |
[V:Vn2] G,2 C2 E2 D2 | F2 E2 D2 C2 | B,2 D2 G2 F2 | E6 z2 |
[V:Va] E,4 z4 | F,4 z4 | B,,4 z4 | E,6 z2 |

X:6
T:Theme voicing — Climactic (tutti, octave doublings)
M:4/4
L:1/8
K:Eb
V:Vn1 name="Violin I"
V:Vn2 name="Violin II"
V:Va name="Viola"
V:Vc name="Cello"
[V:Vn1] "ff"B2 e2 g2 f2 | a2 g2 f2 e2 | d2 f2 b2 a2 | g6 z2 |
[V:Vn2] B,2 E2 G2 F2 | A2 G2 F2 E2 | D2 F2 B2 A2 | G6 z2 |
[V:Va] G,2 C2 E2 D2 | F2 E2 D2 C2 | B,2 D2 G2 F2 | E6 z2 |
[V:Vc] E,2 E,2 E,2 D,2 | F,2 E,2 D,2 C,2 | B,,2 B,,2 B,,2 A,,2 | E,6 z2 |
```

---

## Common Melody-Writing Pitfalls

| Pitfall | What It Sounds Like | How to Fix |
|---------|---------------------|-----------|
| **Chord-tone noodling** | Melody only touches chord tones — sounds like arpeggiated accompaniment | Add non-chord tones on strong beats: appoggiaturas, suspensions, passing tones |
| **Scale exercise** | Melody runs up and down scales without phrasal direction | Add rests, vary direction, place a climax point, use gap-fill after leaps |
| **Too many leaps** | Angular, unsinkable, feels like an etude | Replace some leaps with stepwise motion; follow leaps with stepwise gap-fill |
| **No hook** | Generic, could belong to any piece | Give the theme ONE distinctive element: a rhythmic cell, a signature leap, an unusual starting note |
| **No cadential goal** | Melody wanders without arriving | Plan the phrase ending FIRST (half cadence or PAC), then write backward from it |
| **Metric monotony** | Every phrase starts on beat 1, every note on the beat | Use pickups (anacrusis), syncopation, tied notes across barlines |
| **Symmetry prison** | Rigid 2+2+2+2 grouping, predictable | Try 3+5 or 2+6 groupings; use phrase extensions |
| **Register stagnation** | Melody sits in one octave for the entire theme | Plan a contour that visits at least 1.5 octaves; place the climax in a different register than the opening |

---

*Cross-references: For interval expressiveness → `musical-semiotics.md`. For character archetypes → `character-theme-design.md`. For transformation techniques → `thematic-techniques.md` and `motif-development-guide.md`. For voicing and Klangfarbenmelodie → `modern-orchestration.md`, `late-romantic-orchestration.md`.*
