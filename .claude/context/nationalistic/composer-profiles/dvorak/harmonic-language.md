# Antonin Dvorak — Harmonic Language

Dvorak's harmony lives in the space between folk simplicity and Romantic craft. His chord progressions are warm, clear, and functional — never ambiguous, never dissolving — but flavored with modal inflections that place them unmistakably in Bohemia. Where Brahms deepens tonality, Dvorak brightens it. Where Wagner dissolves it, Dvorak plants it in the earth.

For shared Nationalistic harmonic vocabulary (folk modes, modal cadences, drone techniques), see [nationalistic-harmony.md](../../nationalistic-harmony.md). This file covers what is distinctly Dvorakian.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| bVII chord (Mixolydian) | Bb major in C major context; the folk-modal color chord | Everywhere — the single most Dvorak chord |
| Pentatonic melody over simple harmony | I-V-I underneath a 5-note tune | New World themes, Slavonic Dances, American Quartet |
| Major-minor fluctuation | 3rd degree alternates freely between major and minor | Czech folk tradition; appears in every period |
| Plagal emphasis | IV-I preferred at phrase endings and codas | Hymn-like quality from village church background |
| Warm chromaticism (not dissolving) | Chromatic passing tones and secondary dominants that enrich, never destabilize | Middle and late period — absorbed from Brahms |
| Added 6th color | Major triad with added 6th (C-E-G-A) for pastoral warmth | Slow movements, pastoral passages |
| Simple harmonic rhythm | 1 chord per bar in dance movements; 2 chords per bar in lyrical passages | Dance and song — never harmonically busy |

## The bVII Chord — Dvorak's Signature

The flat-VII chord in major keys gives Dvorak's music its Bohemian folk character. It is not a dominant substitute — it is a modal color that says "village square, not concert hall."

| Context | Progression | Effect |
|---------|------------|--------|
| Phrase ending | bVII - I | Folk-modal cadence; warm, unpretentious |
| Approach from IV | IV - bVII - I | Double plagal — broad, sweeping |
| Alternation | I - bVII - I - bVII | Oscillation creates dance-like energy |
| In minor | bVII - i | Natural minor cadence; darker folk color |

```abc
X:1
T:Dvorak bVII Cadence Types in G major
M:3/4
L:1/4
K:G
%% Three uses of the flat-VII (F major in G major)
[FAc]2 [GBd]|[CEG] [FAc] [GBd]|[FAc] [GBd] [FAc]|[GBd]3|
w: bVII-I IV-bVII-I bVII-I-bVII I
%% The F natural chord against the G tonic: Bohemian color
```

## Pentatonic Harmonic Framework

Dvorak harmonizes pentatonic melodies with the simplest possible chords — the melody does the expressive work, not the harmony.

| Melody Scale | Harmony | Character |
|-------------|---------|-----------|
| C-D-E-G-A (major pentatonic) | I and V only | Maximum folk simplicity |
| A-C-D-E-G (minor pentatonic) | i and iv | Melancholy folk |
| Db-Eb-F-Ab-Bb (New World) | I - IV - V - I | American-period warmth |

```abc
X:2
T:Pentatonic Melody with Simple Harmony (New World character)
M:4/4
L:1/8
K:Db
V:1 name="Melody (cor anglais)"
V:2 name="Harmony" clef=bass
[V:1] !pp!F4 A4|f4 e4|d4 B4|A8|
[V:2] [D,A,F]8|[D,A,F]8|[A,,E,C]8|[D,A,F]8|
w: I I V I
%% The simplest harmony under the most memorable melody
```

## Modal Inflections

| Inflection | Scale Effect | Dvorak's Use |
|-----------|-------------|-------------|
| Mixolydian (b7) | C-D-E-F-G-A-Bb | Dance movements, polkas, furiants |
| Dorian (natural 6 in minor) | A-B-C-D-E-F#-G | Dumka slow sections — warm melancholy |
| Major/minor 3rd fluctuation | E/Eb alternation in C | Throughout — the Czech folk ambiguity |
| Lydian (raised 4th) | Rare; occasional brightening | Less characteristic than in Grieg |

```abc
X:3
T:Major-Minor 3rd Fluctuation (Czech folk character)
M:2/4
L:1/8
K:C
%% The 3rd flickers between major and minor
E2 G2|_E2 G2|C2 E2|_E2 C2|
%% Neither major nor minor — both at once — the folk ambiguity
```

## Harmonic Rhythm

| Context | Rate | Reasoning |
|---------|------|-----------|
| Furiant | 1 chord/bar | Dance pulse drives harmony; simplicity = energy |
| Polka | 1 chord/half-bar | Faster dance = faster harmonic pulse |
| Dumka (slow section) | 1 chord/bar or slower | Sustained melancholy needs harmonic stillness |
| Dumka (fast section) | 1 chord/bar | Dance energy returns |
| Lyrical slow movement | 1 chord/2 beats | Melody breathes over gentle harmonic motion |
| Development section | Accelerated | Sequential modulation; but never as fast as Beethoven |

## Key Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Most characteristic | D major, E minor, G major, Db major | Warm, resonant, open-string friendly |
| American period | Db major, E minor, F major | The "New World" keys — slightly flat-side warmth |
| Slavonic dances | D major, G minor, C major, Ab major | Dance brightness and folk minor |
| Symphonic weight | D minor (Sym 7), E minor (Sym 9) | The serious, Brahmsian side |

## Cadential Patterns

| Cadence | Progression | Dvorak Context |
|---------|------------|----------------|
| Folk modal | bVII - I | Standard Dvorak phrase ending |
| Plagal | IV - I | Hymn-like closings, codas |
| Standard PAC | V - I | Used freely — Dvorak is not dogmatically modal |
| Double plagal | bVII - IV - I | Broad, sweeping endings |
| Picardy | i - I | Minor movements ending in major — warmth at the close |
| Deceptive to bVI | V - bVI | Less common; reserved for harmonic surprise |

```abc
X:4
T:Dvorak Cadential Chain — D major
M:4/4
L:1/2
K:D
[CEA]2|[DFA]2|[CEG] [DFA]|[DFA]2|
w: bVII I bVII I
%% C major chord (bVII) resolving to D major (I) — the Bohemian cadence
```

## Characteristic Progressions

### Czech Dance (Major)
```
I - IV - I - V - I (polka)
I - bVII - I - V - I (furiant)
I - vi - IV - bVII - I (lyrical dance)
```

### Dumka (Minor - Major alternation)
```
i - iv - V - i (slow, melancholy)
I - IV - V - I (fast, dance)
i → I (the dumka switch: same tonic, mode change)
```

### American Period
```
I - IV - I - V - I (pentatonic simplicity)
I - bVII - IV - I (open, spacious)
i - bVII - bVI - V - i (New World development)
```

## Voice Leading

| Principle | Application |
|-----------|-------------|
| Parallel 3rds | Melody doubled in 3rds — standard Dvorak texture; acceptable parallel motion |
| Simple bass | Root-position chords; bass moves by 4th/5th; no elaborate bass lines |
| Folk cross-relations | Major/minor 3rd simultaneously — tolerated for folk color |
| Pedal points | Tonic or dominant pedal under simple harmony — village drone |
| Clear part-writing | Every voice audible; no thick chromatic inner voices (contrast with Brahms) |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #3 (bVII chord), pattern directives
- [melodic-style.md](melodic-style.md) — Pentatonic melody construction
- [orchestration.md](orchestration.md) — Harmonic voicing in orchestral texture
- [../../nationalistic-harmony.md](../../nationalistic-harmony.md) — Shared nationalistic harmonic vocabulary
- [cross-references.md](cross-references.md) — Contrast with Brahms's harmonic depth
