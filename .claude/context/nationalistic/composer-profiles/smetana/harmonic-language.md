# Bedrich Smetana — Harmonic Language

Smetana's harmony serves two masters: German Romantic tradition and Czech folk identity. The progressions are functional — clearly rooted in Schumann and Liszt — but the surface is Czech: polka bass patterns, folk-modal inflections, pastoral key choices. The simplicity is deliberate: Czech village music does not need Wagnerian chromaticism.

For shared nationalistic harmonic vocabulary (modal cadences, folk drones, national scales), see [nationalistic-harmony.md](../../nationalistic-harmony.md). This file covers what is distinctly Smetana's.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Clear tonal function | I-IV-V-I framework dominates; no harmonic ambiguity | Throughout — Smetana's forms are tonally grounded |
| Polka bass harmony | Root-5th alternation (oom-pah); simple I-V-I | The Bartered Bride, Czech Dances, dance sections of Ma vlast |
| Modal inflection within tonal frame | Mixolydian (lowered 7th) and Dorian touches within major/minor | Folk-melody sections; pastoral passages |
| Pastoral key relationships | Flat-side modulations (to IV, bVI) for countryside; sharp-side for heroic | Ma vlast: Vltava (E minor to major), Vysehrad (C major/minor) |
| Lisztian enharmonic modulation | Sudden key shifts via enharmonic reinterpretation | Gothenburg-period symphonic poems; operatic transitions |
| Pedal-drone passages | Open 5th drone beneath folk melody — bagpipe imitation | From Bohemian Fields and Forests; folk scenes in operas |
| Major/minor alternation | Same theme in major and minor — modal mixture for folk ambiguity | Vltava theme (minor to major); The Bartered Bride |

## Polka Harmony — The Czech Foundation

| Element | Harmonic Pattern | Character |
|---------|-----------------|-----------|
| Basic polka | I - V - V - I (2/4, each bar = one harmony) | Bright, communal, village dance |
| Extended polka | I - IV - V - I | Slightly more sophisticated; still direct |
| Minor polka | i - iv - V - i | Darker, melancholy dance; less common |
| Modulating polka | I - V - vi - IV - V - I | Dance with harmonic interest; art-music treatment |

```abc
X:1
T:Smetana Polka Harmony — Basic Czech Dance
M:2/4
L:1/8
K:G
%% Simple I-V alternation — the heartbeat of Czech music
V:1 name="Melody"
V:2 name="Bass (oom-pah)" clef=bass
[V:1] !f!B2 d2|B2 AG|B2 d2|B4|
[V:2] G,D G,D|D,A, D,A,|G,D G,D|G,4|
w: I V I V I V I
%% Direct, cheerful, no sophistication needed — the polka IS the identity
```

## Pastoral and Landscape Harmony

| Landscape | Harmonic Technique | Example Context |
|-----------|-------------------|-----------------|
| River (Vltava) | Rocking figuration over pedal; E minor modal | Vltava — the most famous landscape music |
| Forest | Drone 5th + modal melody above; horn calls | From Bohemian Fields and Forests |
| Castle (Vysehrad) | Broad arpeggiated chords; harp figuration; major key | Vysehrad — the opening of Ma vlast |
| Village | Polka/furiant harmony; bright major keys | The Bartered Bride; pastoral Ma vlast sections |
| Battle/legend | Hussite chorale; minor key with modal inflections | Tabor, Blanik — the last two Ma vlast poems |

```abc
X:2
T:Smetana Water Harmony — Vltava River Figuration
M:6/8
L:1/8
K:Em
V:1 name="River surface (strings)"
V:2 name="Harmonic bass" clef=bass
%% Rocking figuration = the river; E minor pedal = its depth
[V:1] !pp!EGB EGB|EGB EGB|DFA DFA|EGB EGB|
[V:2] E,3 E,3|E,3 E,3|B,,3 B,,3|E,3 E,3|
w: i i V i
%% The river never stops; harmony rocks gently beneath
```

## Cadential Patterns

| Cadence Type | Progression | Character | Frequency |
|-------------|------------|-----------|-----------|
| Standard PAC | V-I | Classical, firm | High — Smetana is tonally direct |
| Plagal (Czech folk) | IV-I | Hymn-like, folk warmth | Moderate — pastoral sections, codas |
| Half cadence | I-V | Open, expectant | Dance sections — the polka pauses |
| Modal (bVII-I) | bVII-I (Mixolydian) | Folk color within tonal context | Occasional — folk-melody passages |
| Picardy tierce | i - I (minor to major) | Hope, resolution | Vltava — the river emerges into sunlight |
| Deceptive | V-vi | Extending the phrase | Opera — dramatic delay |

## Harmonic Rhythm

| Context | Typical Rate | Smetana Character |
|---------|-------------|-------------------|
| Polka | 1 chord per bar (fast 2/4) | Quick harmonic change matching dance pulse |
| Furiant | Hemiola disrupts regular change | 3/4 vs. 2/4 creates harmonic cross-accent |
| Lyrical theme | 1 chord per bar (moderate) | Singing melody over stable harmony |
| Landscape painting | 1 chord per 2–4 bars | River/forest — slow change, pedal beneath |
| Heroic fanfare | 1 chord per 2 bars | Vysehrad, Blanik — broad, majestic |
| Opera recitative | Irregular, text-driven | Follows speech rhythm |

## Characteristic Progressions

### Dance Sections
```
I - V - I (polka basic)
I - IV - V - I (polka extended)
i - iv - V - i (minor dance)
I - V - vi - IV - V - I (modulating dance)
```

### Landscape/Pastoral
```
i - i - V - i (Vltava rocking)
I - IV - I (pastoral plagal)
I (pedal, 4-8 bars) - IV - I (drone + folk melody)
i - bVI - bVII - i (modal landscape)
```

### Heroic/Operatic
```
I - V/vi - vi - V - I (dramatic arc)
i - bVI - V - i (dark heroism)
I - V/V - V - I (Lisztian cadential drive)
```

## Key Preferences

| Preference | Keys | Character |
|-----------|------|-----------|
| Pastoral/river | E minor, G major, D major | Czech countryside; Vltava; warm |
| Heroic/national | C major, Bb major | Vysehrad, Libuse; majestic |
| Dance | G major, D major, F major | Bright polka keys |
| Dark/tragic | D minor, C minor | Dalibor, Tabor; Hussite gravity |
| Autobiographical | E minor (Quartet No. 1) | Personal, intimate |

```abc
X:3
T:Smetana Hussite Chorale Harmony — Dark Heroism (Tabor character)
M:4/4
L:1/2
K:Dm
%% The Hussite hymn "Ye Who Are God's Warriors" — minor, modal, grave
[DFA] [CEG]|[DFA] [A,CE]|[DFA]2|
w: i bVII i V i
%% Minor key, modal bVII, no chromaticism — the people's hymn
```

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #1 (Czech dance idiom), #4 (Classical formal logic)
- [formal-approach.md](formal-approach.md) — Tonal architecture in tone poem cycle
- [orchestration.md](orchestration.md) — Harmonic voicing in orchestral texture
- [../../nationalistic-harmony.md](../../nationalistic-harmony.md) — Czech/Bohemian harmonic character
- [cross-references.md](cross-references.md) — Contrast with Dvorak's chromaticism
