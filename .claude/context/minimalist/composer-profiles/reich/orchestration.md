# Steve Reich — Orchestration

## Core Principle: Interlocking Ensemble, Not Solo Voices

Reich's instrumentation creates a collective organism where no single player carries the melody. Each part is incomplete; together, they form the complete texture.

## Primary Ensembles

| Ensemble | Typical Forces | Key Works |
|----------|---------------|-----------|
| Two pianos | 2 pianos | *Piano Phase*, *Six Pianos* |
| Percussion ensemble | 4–12 percussionists (drums, marimbas, glockenspiels) | *Drumming* |
| Large ensemble (18+) | Keyboards, mallet percussion, strings, winds, voices | *Music for 18 Musicians* |
| String quartet + tape | Standard string quartet + pre-recorded audio | *Different Trains*, *WTC 9/11* |
| Solo + tape | One instrument + pre-recorded canons | *Electric Counterpoint*, *Vermont Counterpoint* |
| Orchestra | Full symphony (late works) | *Music for Ensemble and Orchestra*, *Runner* |

## The "Counterpoint" Series

| Work | Solo Instrument | Pre-recorded Tracks | Total Parts |
|------|----------------|--------------------|----|
| *Vermont Counterpoint* (1982) | Flute | 10 pre-recorded flutes | 11 |
| *New York Counterpoint* (1985) | Clarinet | 10 pre-recorded clarinets | 11 |
| *Electric Counterpoint* (1987) | Electric guitar | 10 pre-recorded guitars + 2 bass guitars | 13 |
| *Cello Counterpoint* (2003) | Cello | 7 pre-recorded cellos | 8 |

```abc
X:1
T:Counterpoint Series Texture — Interlocking Guitar Parts
M:4/4
L:1/8
K:Em
%%staves {1 2 3}
V:1 name="Guitar 1 (live)"
E2 G2 B2 E2 |
V:2 name="Guitar 2 (tape)"
z E2 G2 B2 E |
V:3 name="Guitar 3 (tape)"
z2 E2 G2 B2 |
% Three identical patterns, staggered entries — the interlocking IS the texture
```

## Mallet Percussion (The Reich Sound)

| Instrument | Range | Role | Character |
|-----------|-------|------|-----------|
| Marimba | C3–C7 | Primary pattern instrument | Warm, woody, rhythmic |
| Vibraphone | F3–F6 | Shimmering color | Metallic, sustaining |
| Glockenspiel | G5–C8 | High register sparkle | Bright, bell-like |
| Xylophone | F4–C7 | Crisp articulation | Dry, percussive |
| Crotales | C6–C8 | Highest register color | Crystalline |

### Mallet Instrument Writing

| Technique | Description |
|-----------|-------------|
| Interlocking patterns | Two marimbas play complementary patterns that interlock |
| Doubling at octave | Same pattern in marimba + vibraphone (octave higher) |
| Resultant melody | Accented notes across mallet parts form audible melody |
| Tremolo | Sustained notes via rapid alternation |
| Four-mallet technique | Each player uses 4 mallets for chords |

```abc
X:2
T:Interlocking Mallet Parts (Drumming style)
M:4/4
L:1/16
K:C
%%staves {1 2}
V:1 name="Marimba 1 (odd beats)"
C z E z G z C z E z G z C z E z |
V:2 name="Marimba 2 (even beats)"
z D z F z A z D z F z A z D z F |
% Together: all 16th-note positions filled. Apart: each part is sparse.
```

## Keyboard Writing

| Instrument | Role | Period |
|-----------|------|--------|
| Piano (acoustic) | Primary pattern instrument | Early works (Piano Phase, Six Pianos) |
| Electric organ | Sustained pulsing chords | *Music for 18 Musicians* |
| Synthesizer | Doubling, color | Late works |

### Piano Pattern Technique

| Feature | Description |
|---------|-------------|
| Both hands | Often play different parts of the same interlocking pattern |
| Register | Middle register (C3–C5); never extreme |
| Touch | Firm, even, non-legato | Mechanical precision |
| Pedal | Minimal; clarity over resonance |

## String Writing

| Technique | Usage | Character |
|-----------|-------|-----------|
| Pulsing chords | Repeated chord in steady eighths | *Music for 18 Musicians* (sustained sections) |
| Bowed tremolo | Rapid repeated bowing | Shimmering texture |
| Speech melody doubling | Strings match contour of recorded speech | *Different Trains* |
| Sustained pedal | Long held notes beneath patterns | Grounding |
| Pizzicato | Rare; rhythmic emphasis | Late works |

```abc
X:3
T:String Quartet + Speech (Different Trains style)
M:4/4
L:1/8
K:Am
%%staves {1 2 3}
V:1 name="Vln 1 (speech melody)"
A2 B2 C2 A2 |
V:2 name="Vln 2 (pulsing)"
[AC]2 [AC]2 [AC]2 [AC]2 |
V:3 name="Vc (bass pedal)"
A,8 |
```

## Wind Writing

| Instrument | Role |
|-----------|------|
| Flute | Melody doubling; high-register patterns (*Vermont Counterpoint*) |
| Clarinet | Middle-register patterns; warm color (*New York Counterpoint*) |
| Bass clarinet | Structural signal (cue for section changes in *Music for 18 Musicians*) |
| Oboe/Bassoon | Rare; late orchestral works only |

## Vocal Writing

| Feature | Description |
|---------|-------------|
| Technique | Wordless singing ("doo", "dah") or syllabic text |
| Role | Part of the pulsing texture; not soloistic |
| Text | Hebrew psalms (*Tehillim*); spoken text transcribed (*The Cave*) |
| Range | Soprano (C4–A5); narrow within any section |

## Dynamic Palette

| Dynamic | Usage | Frequency |
|---------|-------|-----------|
| pp | Rare; only at beginnings/endings | Occasional |
| p | Build-up sections | Moderate |
| mp | Default Reich dynamic | Very frequent |
| mf | Sustained full-ensemble sections | Frequent |
| f | Climactic sections (Music for 18 Musicians peaks) | Occasional |
| ff | Very rare; large orchestral only | Rare |

**Key principle:** Dynamics are gradual. The music builds from mp to f over 2–5 minutes by adding players, not by having players play louder.

## Texture Building Technique

| Stage | Players Active | Dynamic | Duration |
|-------|---------------|---------|----------|
| 1 | 1–2 instruments (pattern stated) | p | 1–2 min |
| 2 | 3–4 instruments (pattern + interlocking) | mp | 2–3 min |
| 3 | 6–8 instruments (full pattern set) | mf | 3–5 min |
| 4 | 12–18 instruments (all forces) | f | 2–3 min |
| 5 | Players drop out gradually | mf → p | 2–3 min |

## Orchestration Anti-Patterns

| Avoid | Why |
|-------|-----|
| Solo passages | Reich writes ensemble music; no individual solos |
| Brass (in chamber works) | Too dominant; breaks the balanced texture |
| Rubato / expressive bowing | Mechanical precision is the aesthetic |
| Legato phrasing | Non-legato, even articulation preferred |
| Wide dynamic swings | Changes are gradual, never sudden |
| Orchestral tutti | Even in late orchestral works, texture is layered, not tutti |

## References
- Reich, Steve. *Writings on Music 1965–2000*, 2002
- Potter, Keith. *Four Musical Minimalists*, 2000
- Schwarz, K. Robert. *Minimalists*, 1996
