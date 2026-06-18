# Arvo Pärt — Melodic Style

## Core Melodic Principle: Stepwise Motion Only

The M-voice (melodic voice) in tintinnabuli moves **only by step** within the diatonic scale. No leaps. The entire melodic content is determined by: (1) starting pitch, (2) direction (ascending or descending), (3) how many steps before reversal.

## Melodic Motion Rules

| Rule | Description | Violation |
|------|-------------|-----------|
| Steps only | M-voice moves by 2nd (major or minor within the scale) | Any leap of 3rd or larger |
| Diatonic only | Notes from one diatonic scale, no chromatic alteration | Any accidental |
| Single direction per phrase | Ascending OR descending, not mixed within a phrase | Zigzag motion within a phrase |
| Reversal = new phrase | Change of direction marks phrase boundary | Continuing without articulation |
| Scale-degree anchoring | Phrases begin and end on scale degrees, not chromatic tones | Starting on altered pitches |

## Melodic Contour Types

| Contour | Shape | Typical Duration | Example |
|---------|-------|-----------------|---------|
| Ascending line | A-B-C-D-E-F-G-A | 4–16 bars | *Für Alina* ascending passages |
| Descending line | A-G-F-E-D-C-B-A | 4–16 bars | *Cantus* cascading descent |
| Arch (rise + fall) | A-B-C-D-E-D-C-B-A | 8–32 bars | *Spiegel im Spiegel* overall shape |
| Expanding wedge | Starts at center, each phrase extends one step further | Whole piece | *Für Alina* additive process |
| Contracting wedge | Starts at extremes, each phrase shortens by one step | Whole piece | End of *Cantus* |

```abc
X:1
T:Ascending Line (Spiegel im Spiegel style)
M:3/4
L:1/4
K:Am
V:1 name="M-voice"
A B C | D E F | G A B | c d e |
% Pure stepwise ascent — no leaps, no chromaticism
```

```abc
X:2
T:Expanding Wedge (Für Alina style)
M:free
L:1/4
K:Bm
V:1 name="M-voice"
B A | B C B A G | B C D C B A G ^F |
% Each phrase adds one step further in each direction from B
```

## Additive/Subtractive Melodic Process

| Phase | Process | Example (starting on A) |
|-------|---------|------------------------|
| Phrase 1 | 1 step up, return | A-B-A |
| Phrase 2 | 2 steps up, return | A-B-C-B-A |
| Phrase 3 | 3 steps up, return | A-B-C-D-C-B-A |
| Phrase 4 | 4 steps up, return | A-B-C-D-E-D-C-B-A |
| ... | Continue expanding | Each phrase one step longer |
| Peak | Maximum extension reached | The piece's ceiling |
| Reverse | Subtract one step per phrase | Mirror of the buildup |

```abc
X:3
T:Additive Melodic Process
M:4/4
L:1/4
K:Am
V:1 name="M-voice"
A B A z | A B C B A z z z | A B C D C B A z | A B C D E D C B |
% Each phrase extends one note further — the process IS the melody
```

## Silence as Melodic Element

| Silence Type | Function | Duration |
|-------------|----------|----------|
| Inter-phrase rest | Breathing space between stepwise phrases | 1–4 beats |
| Structural silence | Full bar(s) of rest at formal junctures | 1–4 bars |
| Peak silence | Rest before or after highest/lowest note | 1 full bar minimum |
| Terminal silence | Music fades to nothing before final note | 2–8 bars of diminuendo |

```abc
X:4
T:Silence as Melodic Punctuation
M:4/4
L:1/4
K:Am
V:1 name="M-voice"
A B C D | z4 | E F G A | z4 | z4 | G F E D |
% The two bars of silence at mm.5 are not empty — they are the center of the piece
```

## Rhythmic Treatment of Melody

| Approach | Description | Works |
|----------|-------------|-------|
| Equal note values | All quarter notes or all half notes; rhythm is not expressive | *Für Alina*, *Spiegel im Spiegel* |
| Text-derived rhythm | One note per syllable; rhythm follows speech | *Passio*, *Te Deum*, *Miserere* |
| Proportional augmentation | Each phrase doubles duration of previous | *Cantus in Memoriam Benjamin Britten* |
| Free/unmeasured | No bar lines; duration by performer's breath | *Für Alina* (original) |

## Cantus Technique — Canonic Melodic Descent

In *Cantus in Memoriam Benjamin Britten*, the melody is a descending A minor scale in canon at multiple speeds:

| Voice | Speed | Starting Pitch | Character |
|-------|-------|---------------|-----------|
| Violin 1 | Sixteenth notes | A5 | Rapid, falling |
| Violin 2 | Eighth notes | A4 | Medium pace |
| Viola | Quarter notes | A3 | Steady |
| Cello | Half notes | A2 | Slow, weighty |
| Bass | Whole notes | A1 | Glacial, grounding |

```abc
X:5
T:Cantus Technique — Canonic Descent (simplified)
M:4/4
L:1/16
K:Am
%%staves {1 2 3}
V:1 name="Fast descent"
AGFE DCBA | GFED CBA,G, |
V:2 name="Medium descent"
A,2G,2 F,2E,2 | D,2C,2 B,,2A,,2 |
V:3 name="Slow descent"
A,,4 G,,4 | F,,4 E,,4 |
% Same descending scale at three speeds simultaneously — a cascading waterfall
```

## Melodic Range and Register

| Voice/Instrument | Typical Range | Character |
|-----------------|---------------|-----------|
| Soprano / Violin | C4–E5 (narrow) | The M-voice lives in a small, comfortable space |
| Alto / Viola | A3–C5 | Slightly lower, warm |
| Tenor / Cello | C3–E4 | Rich middle ground |
| Bass / Double bass | A1–C3 | Deep, grounding |
| Piano (RH) | C4–C6 | M-voice in piano works |
| Piano (LH) | C2–C4 | T-voice / bass |

**Key principle:** The melodic range is deliberately narrow. A Pärt piece that spans more than an octave and a half in one voice is unusual. The narrow range concentrates attention on each interval.

## Text-Melody Relationship (Vocal Works)

| Principle | Application |
|-----------|------------|
| Syllabic setting | One note per syllable — never melismatic |
| Speech rhythm | Note durations follow natural word stress |
| Accentuation | Stressed syllables on stronger beats, but not rigidly |
| Language as structure | Phrase lengths determined by sentence structure, not musical convention |
| Latin preference | Latin texts provide rhythmic variety + sacred gravity |

```abc
X:6
T:Text-Derived Melody (Berliner Messe style)
M:free
L:1/8
K:Dm
w:Ky-ri-e e-le-i-son
D2 E2 F2 | G4 A2 G2 | F4 E4 | D8 |
% Rhythm follows the natural speech pattern of "Kyrie eleison"
```

## References
- Hillier, Paul. *Arvo Pärt* (Oxford Studies of Composers), 1997
- Brauneiss, Leopold. "Tintinnabuli: An Introduction," in *The Cambridge Companion to Arvo Pärt*, 2012
- Quinn, Peter. "Arvo Pärt's White Light," 2017
