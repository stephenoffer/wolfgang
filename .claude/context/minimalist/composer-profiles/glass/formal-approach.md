# Philip Glass — Formal Approach

## Core Principle: Repetitive Structure, Not Developmental Form

Glass does not use Classical forms (sonata, rondo, ternary). His forms are built from repetition, cycling, and additive/subtractive process. A Glass piece progresses by accumulation and change of pattern, not by thematic development.

## Primary Formal Types

| Form Type | Structure | Works |
|-----------|-----------|-------|
| Additive process | Cell grows by one note per cycle | *Music in Fifths*, *Music in Similar Motion* |
| Cyclic repetition | Chord cycle repeats 6–12 times per section | *Glassworks: Opening*, *Metamorphosis* |
| Number opera | Discrete numbered sections, each self-contained | *Einstein on the Beach*, *Satyagraha* |
| Through-composed (film) | Continuous, scene-following | *The Hours*, *Koyaanisqatsi* |
| Multi-movement suite | 4–6 movements with contrasting tempi/keys | *Glassworks*, *Metamorphosis* |
| Symphonic | 3–4 movements, expanded Glass language | Symphonies 1–12 |

## Additive Process Form (Early Works)

| Stage | Cell Length | Repetitions | Duration |
|-------|-----------|-------------|----------|
| A | 3 notes | 8× | ~16 bars |
| B | 4 notes | 8× | ~16 bars |
| C | 5 notes | 8× | ~16 bars |
| D | 6 notes | 8× | ~16 bars |
| E | 7 notes | 8× | ~16 bars |
| F | 8 notes | 8× | ~16 bars |
| (Subtractive) | 7 → 6 → 5 → 4 → 3 notes | 8× each | ~80 bars |

```abc
X:1
T:Additive Process Form — Schematic
M:3/8
L:1/8
K:C
%% Stage A: 3 notes
EGA | EGA | EGA | EGA |
%% Stage B: 4 notes (add B)
M:4/8
EGAB | EGAB | EGAB | EGAB |
%% Stage C: 5 notes (add C)
M:5/8
EGABc | EGABc | EGABc | EGABc |
% The meter itself changes as notes are added — the process IS the form
```

## Cyclic Form (Middle Period)

| Element | Description |
|---------|-------------|
| Chord cycle | 3–4 chords in fixed order |
| Cycle length | 16–32 bars (4–8 bars per chord) |
| Repetitions | 6–12 complete cycles per section |
| Section change | New chord set, new key, or new arpeggio pattern |
| Transitions | Abrupt (direct cut to new pattern) or smooth (one chord shared) |

### Typical Glassworks Movement Structure

| Section | Key/Mode | Chord Cycle | Cycles | Duration |
|---------|----------|-------------|--------|----------|
| A | D Dorian | Dm → C → Bb → Am | 8 | ~3 min |
| B | F Lydian | F → G → Am → C | 6 | ~2 min |
| A' | D Dorian | Dm → C → Bb → Am | 6 | ~2 min |
| Coda | D Dorian | Dm (single chord) | 4 | ~1 min |

## Number Opera (Einstein, Satyagraha, Akhnaten)

| Feature | Description |
|---------|-------------|
| Structure | Discrete numbered scenes (not continuous drama) |
| Each scene | Self-contained musical section with own pattern/chord set |
| Knee plays | Connecting interludes between acts (Einstein) |
| Libretto | Non-narrative (Einstein); narrative but non-linear (Satyagraha) |
| Duration | 3–5 hours (Einstein); 2.5–3 hours (Satyagraha, Akhnaten) |

### Einstein on the Beach — Structural Map

| Element | Content | Duration |
|---------|---------|----------|
| Knee Play 1 | Organ chords, spoken text | ~10 min |
| Act I, Scene 1 (Train) | Additive patterns, chorus counting | ~20 min |
| Act I, Scene 2 (Trial) | Organ arpeggios, violin solo | ~20 min |
| Knee Play 2 | Organ/voice duet | ~10 min |
| ... | Continues through 4 acts + 5 knee plays | ~5 hours total |

## Film Score Form

| Approach | Description | Works |
|----------|-------------|-------|
| Scene-following | Music mirrors visual pacing; starts/stops with scenes | *The Hours* |
| Continuous process | Music runs independently of scene cuts | *Koyaanisqatsi* |
| Theme and variation | One theme adapted for different scenes/moods | *The Truman Show* |
| Suite extraction | Film cues rearranged into concert suite | *Mishima* suite |

```abc
X:2
T:Film Score Form — Theme Stated Simply, Then with Strings
M:4/4
L:1/8
K:Am
%%staves {1 2}
V:1 name="Piano (theme statement)"
A2 B2 c2 B2 | A2 G2 F2 E2 |
V:2 name="Strings (enter second statement)"
z8 | A,4 E,4 |
% First: piano alone. Second: strings join. The form is accretion, not development.
```

## Section Proportions

| Proportion | Description | Typical |
|-----------|-------------|---------|
| A section | Longest; establishes the pattern | 3–5 minutes |
| B section | Contrasting; different chord set or key | 2–3 minutes |
| A' return | Abbreviated reprise of A | 1.5–3 minutes |
| Coda | Single chord, fading | 0.5–1.5 minutes |
| Total | | 8–15 minutes per movement |

## How a Glass Piece Ends

| Ending Type | Description | Works |
|-------------|-------------|-------|
| Fade-out | Pattern continues but gets softer | *Glassworks: Opening* |
| Final chord held | Last chord sustained, no arpeggio | *Metamorphosis* movements |
| Abrupt stop | Pattern simply ceases | *Einstein on the Beach* scenes |
| Subtractive | Notes removed from pattern until 1 remains | Early process pieces |
| Cadential | Rare; a simple I chord, held | Late symphonic movements |

```abc
X:3
T:Subtractive Ending — Pattern Dissolves
M:4/4
L:1/8
K:Am
ACEA CEAC | ACE2 CE2 z | AC4 C2 | A8 |
% The arpeggio loses notes until only the root remains — the process concludes
```

## References
- Glass, Philip. *Words Without Music: A Memoir*, 2015
- Potter, Keith. *Four Musical Minimalists*, 2000
- Richardson, John. *Singing Archaeology: Philip Glass's Akhnaten*, 1999
