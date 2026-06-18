# G.F. Handel — Formal Approach

Handel inhabits forms the way a great actor inhabits roles: the structure is given, but the life within it is entirely his own. Where Bach treats form as architecture — building symmetrical cathedrals where every beam bears weight — Handel treats form as theatre. The structure serves the drama, and when the drama demands it, the structure bends.

This pragmatic, audience-facing approach to form is Handel's signature. He did not invent new forms; he made existing ones communicate.

## Forms and Mastery

| Form/Genre | Mastery Level | How Handel Makes It His Own |
|-----------|--------------|----------------------------|
| Da capo aria | Definitive | The A-B-A becomes a dramatic arc: statement, shadow, restoration |
| Oratorio | Invented the English form | Chorus as protagonist; dramatic narrative without staging |
| Opera seria | Excellent | Vivid characterization within rigid conventions |
| French overture | Masterful | Dotted majesty into fugal energy — the audience knows something important is beginning |
| Concerto grosso | Masterful | Tutti/solo contrast as drama, not just texture |
| Organ concerto | Pioneering | Created the genre; improvisation within structure |
| Anthem | Excellent | Multi-section choral works building to climactic chorus |
| Keyboard suite | Good | Dance movements as character pieces |
| Trio sonata | Excellent | Conversational texture, Italian influence |
| Ground bass/Chaconne | Masterful | Variations that build dramatic arc over repeating bass |

## The Da Capo Aria — Handel's Central Form

The ABA structure is the engine of Handel's dramatic art. It is not mere repetition but a journey: the A section makes a statement, the B section challenges or shadows it, and the return of A — now ornamented — is the statement transformed by experience.

### Structure

| Section | Key | Character | Vocal Approach | Typical Length |
|---------|-----|-----------|---------------|----------------|
| Ritornello | Tonic | Orchestral introduction of A material | — | 4-8 bars |
| A | Tonic, modulating to V (or III in minor) | Primary affect — the emotional thesis | Full voice, moderate ornament | 16-32 bars |
| A cadence | V or III | Orchestral interlude confirming modulation | — | 2-4 bars |
| B | Related minor, iv, or contrasting key | Counter-affect — shadow, doubt, contrast | Simpler, more syllabic | 8-16 bars |
| A (da capo) | Tonic throughout | Return of primary affect, ornamented | Singer elaborates freely | Same as A |
| Final ritornello | Tonic | Orchestral confirmation | — | 2-4 bars |

### Aria Types and Their Formal Character

| Aria Type | A Section | B Section | Da Capo Treatment |
|-----------|-----------|-----------|-------------------|
| Rage | Driving, virtuosic, wide leaps | Often slower, brooding | Even more virtuosic; added runs |
| Lament | Descending lines over chromatic bass | Contrasting — may shift to major | More ornate sighing figures |
| Pastoral | Lilting compound meter, gentle | Usually in relative minor | Added graces, more elaborate |
| Triumphant | Fanfare, dotted rhythms, brass-like | Softer, reflective contrast | Full display of vocal power |
| Love | Flowing legato, stepwise warmth | Minor-mode yearning | More intimate, personal embellishment |
| Bravura | Extended coloratura on key words | Contrasting simplicity | Maximum virtuosity — the showpiece moment |

```abc
X:1
T:Da Capo Aria Skeleton — A Section
M:3/4
L:1/8
K:G
V:1 name="Voice"
V:2 name="Bass" clef=bass
%% Ritornello (orchestral preview)
[V:1] z6|z6|
[V:2] G,2B,2 D2|G,2A,2 B,2|
%% A section: vocal entry, arching melody, cadence on V
[V:1] d4 B2|A4 G2|E2 G2 A2|B6|
[V:2] G,4 G,2|D,4 E,2|C,4 D,2|G,6|
```

```abc
X:2
T:Da Capo Aria Skeleton — B Section (Contrasting)
M:3/4
L:1/8
K:Em
V:1 name="Voice"
V:2 name="Bass" clef=bass
%% B section: relative minor, simpler, more syllabic
[V:1] E4 F2|G4 A2|B2 A2 G2|F4 E2|
[V:2] E,4 D,2|C,4 A,,2|G,,4 E,2|B,,4 E,2|
%% After B, da capo returns to A in G major — now ornamented
```

## Oratorio — Handel's Grand Invention

The English oratorio is Handel's greatest formal achievement. When Italian opera failed commercially, he did not simply add English words to opera — he created a new dramatic form where the chorus replaces the staged action.

### Oratorio Dramatic Architecture

| Component | Handel's Treatment | Dramatic Function |
|-----------|-------------------|-------------------|
| French overture | Slow dotted majesty + fugal allegro | Sets the tone; the audience settles; grandeur is promised |
| Recitative (secco) | Voice + continuo, speech-rhythm | Narrative: moves the story forward efficiently |
| Recitative (accompagnato) | Voice + full strings | Heightened drama: visions, prophecies, turning points |
| Aria (da capo) | Solo voice + orchestra | Emotional reflection on the dramatic situation |
| Chorus (homophonic) | Block chords, rhythmic unanimity | Collective declaration — the crowd speaks as one |
| Chorus (fugal) | Staggered entries, contrapuntal buildup | Energy building toward homophonic climax |
| Chorus (antiphonal) | Two choirs in dialogue | Spatial drama, call-and-response |
| Instrumental interlude | Pastoral sinfonia, march, dance | Scene-setting, contrast, breathing space |

### Dramatic Pacing — The Handel Arc

| Position in Act | Texture | Dynamics | Emotional Direction |
|----------------|---------|----------|---------------------|
| Opening | Overture or chorus | Forte | Establishment |
| Early | Recitative + aria alternation | Mixed | Character introduction |
| Building | More complex arias, ensemble | Growing | Tension increases |
| Climactic chorus | Full SATB + orchestra | Fortissimo | Emotional peak — this is what the audience came for |
| Resolution | Reflective aria or gentle chorus | Piano to forte | Catharsis |
| Final chorus | Grand, homophonic, often fugal-to-homophonic | Fortissimo | Closing statement — send them home remembering |

### The Fugue-to-Homophony Arc (Handel's Signature Choral Move)

This is perhaps the most Handelian of all formal gestures: a chorus begins with fugal entries — voices entering one by one, building polyphonic complexity — then suddenly all voices unite in rhythmic homophony for the emotional climax. The buildup IS the form.

| Phase | Texture | Bars (typical) | Effect |
|-------|---------|----------------|--------|
| Subject entry (Bass) | Monophonic | 1-4 | Quiet beginning, single voice |
| Answer (Tenor) | 2-voice polyphony | 5-8 | Growing complexity |
| Entry (Alto) | 3-voice polyphony | 9-12 | Thickness builds |
| Entry (Soprano) | Full 4-voice fugue | 13-16 | Maximum contrapuntal density |
| Homophonic arrival | Block chords, rhythmic unison | 17-20 | CLIMAX — all voices united |

## Concerto Grosso — Dramatic Texture

Handel's Op. 6 concerti grossi use form as dramatic contrast rather than architectural plan.

### Movement Plan (Variable)

| Position | Typical Character | Tempo | Form |
|----------|------------------|-------|------|
| 1st | Grand, introductory | Slow or Moderate | French overture or free |
| 2nd | Energetic, contrapuntal | Allegro | Fugal or ritornello |
| 3rd | Lyrical, singing | Larghetto/Adagio | Binary or through-composed |
| 4th | Lively, dance-like | Allegro | Binary, rondo, or free |
| 5th (optional) | Dance: minuet, musette | Moderate | Binary with repeats |
| 6th (optional) | Brilliant finale | Allegro | Fugal or homophonic |

### Tutti/Solo Contrast

| Element | Tutti (Ripieno) | Solo (Concertino) |
|---------|----------------|-------------------|
| Forces | Full string orchestra + continuo | 2 violins + cello |
| Texture | Homophonic, strong, direct | Elaborate, ornamental, conversational |
| Dynamics | Forte | Piano |
| Function | Structural pillars, thematic statement | Episodes, development, display |
| Character | The public voice | The intimate voice |

```abc
X:3
T:Concerto Grosso — Tutti/Solo Contrast
M:4/4
L:1/8
K:Gm
V:1 name="Concertino Vn I"
V:2 name="Ripieno Vn I"
V:3 name="Bass" clef=bass
%% TUTTI: full, forte, direct
[V:1] !f!G2AB c2dB|
[V:2] !f!G2AB c2dB|
[V:3] !f!G,4 C,4|
%% SOLO: concertino only, piano, more elaborate
[V:1] !p!G2AB cBAG|FGAB cdef|
[V:2] !p!z8|z8|
[V:3] !p!G,4 A,4|B,4 C4|
```

## French Overture

| Section | Tempo | Character | Texture | Length |
|---------|-------|-----------|---------|--------|
| Slow | Grave/Adagio | Majestic, ceremonial | Homophonic, double-dotted | 8-16 bars |
| Fast | Allegro | Energetic, learned | Fugal, imitative entries | 30-60 bars |
| Slow (optional) | Adagio | Brief return of opening | Homophonic | 2-4 bars |

The double-dotted rhythm of the slow section is the sound of authority: court, ceremony, divine order. The fugal allegro is the sound of energy released within that order.

## Handel vs Bach — Formal Philosophy

| Aspect | Handel | Bach |
|--------|--------|------|
| Form serves... | Drama and audience | Architecture and theology |
| Repetition means... | Emphasis, rhetoric, audience satisfaction | Structural symmetry, cosmic order |
| When form doesn't work... | Change it — cut an aria, add a chorus | Deepen it — add more counterpoint |
| Climax achieved by... | Fugue resolving into homophony | Cumulative contrapuntal density |
| Movement count | Variable (3-6 in concerti) | Fixed (typically 3 or 4) |
| Most important moment | The audience's emotional peak | The structural completion |
| Relationship to convention | Uses convention, bends when needed | Transcends convention from within |

## Practical Formal Guidelines

| Principle | Application |
|-----------|-------------|
| Every section needs a clear destination | Build toward cadences; the audience should sense arrival |
| Contrast creates form | A becomes meaningful because B was different |
| The chorus is a structural event | Place it at emotional peaks, not as filler |
| Repetition is rhetoric | Repeating material is not lazy — it is persuasive |
| Allow breathing room | Rests between sections; silence is a formal element |
| Build to homophonic climax | Polyphonic complexity resolving into unison IS the drama |
| Da capo return should add, not merely repeat | Ornamentation transforms repetition into development |

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #3 (da capo architecture), Fingerprint #1 (grand choral gesture)
- [harmonic-language.md](harmonic-language.md) — harmonic progressions supporting formal structure
- [melodic-style.md](melodic-style.md) — melody types for each formal context
- [stylistic-evolution.md](stylistic-evolution.md) — how formal approach changed across career phases
- [orchestration.md](orchestration.md) — instrumentation for each formal context
- [cross-references.md](cross-references.md) — formal comparison with Bach, Vivaldi
