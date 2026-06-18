# Felix Mendelssohn — Harmonic Language

Mendelssohn's harmony is Classical in structure, Romantic in color. Every progression is functional — there is no harmonic wandering, no tonal ambiguity for its own sake — but the voicings are warm, the modulations smooth, and the chromatic touches delicate rather than disruptive. Where Chopin dissolves and Schumann fragments, Mendelssohn clarifies.

For shared Romantic harmonic vocabulary (chromatic mediants, augmented 6ths, sequences), see [romantic-harmony.md](../../romantic-harmony.md). This file covers what is distinctly Mendelssohnian.

## Core Harmonic Character

| Feature | Description | Where It Appears |
|---------|-------------|-----------------|
| Functional clarity | Every chord has a job; progressions move purposefully from tonic to dominant and back | All works — this is the foundation |
| Smooth modulation | Key changes prepared by pivot chords or chromatic voice-leading; no abrupt juxtapositions | Transitions in sonata forms, development sections |
| Diatonic preference | The basic vocabulary is diatonic; chromaticism is seasoning, not structure | Fast movements, scherzi, most outer movements |
| Transparent voicing | Open spacing, few doublings, each voice distinct — the ear can follow every line | Orchestral and chamber works equally |
| Major-mode brightness | Major keys predominate; minor-key works resolve toward major (the Violin Concerto, "Italian" Symphony) | Overall aesthetic — Mendelssohn's world is sunlit |
| Sequence as propulsion | Diatonic sequences (descending 5ths, ascending 2nds) drive transitions and developments | Development sections, bridge passages |
| Cadential clarity | Perfect authentic cadences; half-cadences cleanly articulated; few deceptive resolutions | Phrase endings throughout |

## Modulation Style

| Technique | How Mendelssohn Uses It | Compared to Contemporaries |
|-----------|------------------------|---------------------------|
| Pivot chord | Shared chord between keys; the transition is seamless | More systematic than Schubert's abrupt shifts |
| Chromatic voice-leading | One inner voice moves by semitone to establish the new key | Less pervasive than Chopin; more purposeful |
| Dominant preparation | New key announced by its dominant; classical V-I in the new key | Closer to Mozart than to Schumann |
| Mediant relations | Third-related keys (C to E, C to Ab) used for color in development | Less radical than Schubert's mediant adventures |
| Sequential modulation | Rising or falling sequence carries the harmony through multiple keys | Used in development; always returns home cleanly |

```abc
X:1
T:Mendelssohn Pivot-Chord Modulation — C major to A minor
M:4/4
L:1/4
K:C
[CEG] [FAc] [DFA] [EGB]|[Ace] [EGB] [Ace]2|
w: C:I IV ii V/vi vi(=Am:i) V i
%% The pivot (vi = i) is seamless — the listener barely notices the key change
```

## Characteristic Progressions

| Progression | Context | Character |
|------------|---------|-----------|
| I - IV - V - I | Basic phrase harmonization | Classical clarity; Mendelssohn's default |
| I - vi - IV - V - I | Extended phrase | Warm, song-like — the Songs Without Words basis |
| i - iv - V - VI - i | Minor-key phrase | The minor sixth (VI) provides momentary brightness |
| I - V/vi - vi - V/V - V - I | Chromatic enrichment | Applied dominants add color without disrupting function |
| I - I6 - IV - iv - V - I | The Mendelssohn "shadow" | The iv (minor four) is his one Romantic darkening — brief, poignant, resolved |

```abc
X:2
T:Mendelssohn Shadow Progression — iv in Major Context
M:3/4
L:1/4
K:G
[B,DG] [B,DG] [CEG]|[CF_A] [B,DF] [B,DG]|
w: I I IV iv V I
%% The borrowed iv is brief and resolves immediately — shadow passing through sunlight
```

## The Barcarolle Harmonic Pattern

| Beat | Harmony | Voice Distribution |
|------|---------|-------------------|
| Beat 1 (dotted quarter) | Bass note alone — root of chord | Low register, single note |
| Beat 2 (dotted quarter) | Chord — upper notes of harmony | Mid register, 2-3 notes |
| Across the bar | Harmony changes every bar or every 2 bars | Slow harmonic rhythm creates rocking calm |

```abc
X:3
T:Mendelssohn Barcarolle Harmony — Songs Without Words character
M:6/8
L:1/8
K:G
%% LH pattern: bass-chord-chord creating the rocking motion
G,3 [B,D]3|D,3 [A,C]3|E,3 [B,E]3|D,3 [A,D^F]3|G,3 [B,DG]3|
w: I _ V7 _ vi _ V/V _ I
%% Each bar rocks gently; harmonic rhythm = 1 chord per bar
```

## Key Signatures and Character

| Key | Mendelssohn Association | Representative Work |
|-----|------------------------|-------------------|
| E minor | Lyrical intensity, the violin's home key | Violin Concerto |
| A major | Bright, Italian warmth | Italian Symphony (1st mvt) |
| A minor | Scottish landscape, modal coloring | Scottish Symphony |
| E major | Sparkling, fairy-like | Midsummer Night's Dream Overture |
| D minor | Serious, fugal | Reformation Symphony |
| G major/minor | Gentle lyricism | Songs Without Words |
| F minor | Late anguish (rare) | String Quartet Op. 80 |

## Harmonic Rhythm

| Context | Typical Rate | Mendelssohn Signature |
|---------|-------------|----------------------|
| Lyrical theme | 1 chord/bar | Melody floats over stable harmony — classical poise |
| Scherzo | 1 chord/2 bars or slower | Harmony almost static; the interest is rhythmic/textural, not harmonic |
| Development | Moderate acceleration | Sequences drive through keys but always with clear direction |
| Cadence | Standard V-I at phrase speed | Clean arrival; none of Brahms's cadential avoidance |
| Transition | Sequence-driven acceleration | Rising energy, not harmonic complexity |

## Voice-Leading Priorities

| Priority | Mendelssohn Practice |
|----------|---------------------|
| 1. Clarity | Every voice audible; avoid muddying doublings |
| 2. Smooth motion | Stepwise voice-leading preferred; leaps only in bass and melody |
| 3. Functional bass | Bass moves by 5th, 4th, or step — always functional |
| 4. Open spacing | Upper voices spaced widely; avoid cluster voicings |
| 5. Chromatic restraint | Chromatic passing tones in inner voices; never chromatic saturation |

```abc
X:4
T:Mendelssohn Voice-Leading — Transparent Spacing
M:4/4
L:1/2
K:E
[E,B,E] [A,CE]|[B,,^DF] [E,B,E]|
w: I IV V I
%% Wide spacing between voices; every note audible; Classical purity
```

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #5 (Protestant clarity) applied to harmony
- [formal-approach.md](formal-approach.md) — How harmonic design serves Classical form
- [orchestration.md](orchestration.md) — Voicing and doubling in orchestral context
- [../../romantic-harmony.md](../../romantic-harmony.md) — Shared Romantic techniques (used sparingly by Mendelssohn)
