# Ludwig van Beethoven — Harmonic Language

Beethoven's harmony is drama. Where Mozart's chromaticism is a passing shadow across sunlit diatonicism, and Haydn's is a witty surprise, Beethoven's chromatic moves are seismic events — they change the landscape of the piece. A shift to bVI is not color; it is a character entering the scene. A Neapolitan sixth is not a device; it is a darkening of the sky.

For shared Classical harmonic vocabulary (functional harmony, cadence types, secondary dominants, sequences, voice-leading standards), see [classical-harmony.md](../../classical-harmony.md). This file covers what is distinctly Beethovenian.

## Core Harmonic Character

| Feature | Description | Period Intensity |
|---------|-------------|-----------------|
| Modal mixture as drama | bVI, bVII, iv in major contexts — parallel-minor borrowing as emotional argument | Moderate (early) → Heavy (middle) → Structural (late) |
| Submediant relationships | Third-related key areas (C→Ab, C→E, C→A) instead of Classical dominant | Rare (early) → Common (middle) → Dominant (late) |
| Sudden modulation | Direct juxtaposition of remote keys without pivot chord | Minimal (early) → Dramatic (middle) → Radical (late) |
| Neapolitan emphasis | bII6 as intensified pre-dominant, especially in minor | Present in all periods; late period: bII as key area |
| Sforzando as harmonic event | Sfz marks the moment of harmonic surprise, not just dynamic accent | Constant from Op. 2 onward |
| Dominant prolongation | Extended V pedals before structural arrivals | Present in all periods; middle period: 20+ bars |
| Deceptive cadence strategy | V→vi (or V→bVI) to withhold resolution; PAC earned, not given | Constant — Beethoven's most characteristic cadential habit |
| Enharmonic reinterpretation | Diminished 7th or German augmented 6th pivoting to remote keys | Rare (early) → Moderate (middle) → Frequent (late) |

## Modal Mixture — The Beethoven Signature

The borrowing of chords from the parallel minor into major is Beethoven's most distinctive harmonic tool. Where Mozart uses iv or bVI as a single cloud across the sun, Beethoven builds entire passages — sometimes entire developments — in the mixture world.

| Borrowed Chord | Color | Beethoven's Typical Use |
|----------------|-------|------------------------|
| iv | Plaintive shadow | Pre-dominant substitute; the moment hope darkens |
| bVI | Warm darkness, dramatic weight | Deceptive resolution (V→bVI); surprise key area in exposition |
| bVII | Modal, elemental force | Approach to tonic; "primitive" or folk-like character |
| bIII | Bright but foreign | Exposition second key area (instead of V); Eroica |
| ii° | Tense pre-dominant | Intensified approach to cadence in major contexts |
| i (in major context) | Momentary tragic shadow | Theme restated in minor for contrast |

```abc
X:1
T:Beethoven Modal Mixture — bVI as Dramatic Event (C major)
M:4/4
L:1/4
K:C
V:1 clef=treble
V:2 clef=bass
%% The shift to bVI is not color — it is a change of world
[V:1] [EG]2 [EG]2|!sfz![C_E_A]4|[CEG]4|
[V:2] C,2 C,2|_A,,4|C,4|
%% I - bVI(sfz!) - I : the darkness arrives, then the light reasserts
```

## Key Relationships by Period

| Period | Typical Key Relationships | Character |
|--------|--------------------------|-----------|
| Early | I→V (exposition), i→III (minor), closely related keys | Classical norms respected |
| Middle | I→III (Waldstein: C→E), i→bVI, development to remote flat keys | Third-relationships replace fifth-relationships |
| Late | Direct semitone (C→Db), unprepared major thirds (C→A), tonal areas by 3rds | Key relationships defy pivot-chord logic |

### The Third-Relationship Revolution

Beethoven's shift from fifth-based to third-based key relationships is one of the most consequential harmonic innovations in Western music. It makes the tonal landscape richer and stranger.

| Classical Norm | Beethoven Alternative | Example |
|----------------|----------------------|---------|
| I → V (exposition) | I → III (major third up) | Waldstein Sonata: C major → E major |
| i → III (minor) | i → bVI (minor) | Appassionata: F minor → Db major |
| Development to vi, IV | Development to bVI, bIII, Neapolitan | Symphony 3: Eb → C# minor, remote flats |
| V → I (recapitulation) | bVI → I or IV → I approach | Op. 57: Db major approaches F minor recapitulation |

```abc
X:2
T:Beethoven Third-Relationship — C major to Ab major (bVI) Direct
M:4/4
L:1/8
K:C
V:1 clef=treble
V:2 clef=bass
%% No pivot chord — the key simply shifts by a major third down
[V:1] G2c2 e2g2|!ff![_e2g2] [_ec]4 z2|
[V:2] C,2E,2 G,2C2|_A,,4 _A,,4|
%% C major → Ab major: the floor drops; a new tonal world
```

## The Neapolitan as Character

In Beethoven, the Neapolitan (bII) grows from a cadential chord into a key area and a dramatic character.

| Usage Level | What It Does | Example |
|-------------|-------------|---------|
| Chord (all periods) | bII6 before V in minor cadences | Pathetique Sonata cadences |
| Key area (middle) | Extended passage in bII as tonal region | Appassionata development: Gb major |
| Structural pillar (late) | bII as thematic key alongside tonic | Op. 111: C minor vs. Db |

## Harmonic Rhythm

| Context | Beethoven's Approach | Compared to Haydn/Mozart |
|---------|---------------------|--------------------------|
| Exposition themes | Slow harmonic rhythm; theme breathes | Similar to Classical norm |
| Transitions | Accelerating; sequences pile up | More aggressive acceleration |
| Development | Fastest — every beat may change key | Much more intense than predecessors |
| Pre-recapitulation | Dominant pedal, 8–20+ bars | Longer than Classical norm |
| Coda | Slow then fast — second development within coda | Haydn: brief. Beethoven: a second development |

## Cadential Strategy

Beethoven's approach to cadences is one of his most personal traits. The PAC is not a punctuation mark — it is a dramatic destination that must be earned.

| Strategy | How It Works | Dramatic Function |
|----------|-------------|-------------------|
| Deceptive cadence chain | V→vi, V→bVI, then finally V→I | Resolution denied, denied, then explosively granted |
| Evaded cadence | V resolves but melody continues past tonic | Momentum sustained through the "ending" |
| Coda as true resolution | Exposition/recap cadences are partial; coda provides the real PAC | The piece's dramatic argument resolves only at the very end |
| Multiple final cadences | 5–10 repeated V→I at the close | Insistence — the tonic is hammered home as a statement of triumph |

```abc
X:3
T:Beethoven Cadential Strategy — Deceptive then Authentic
M:4/4
L:1/4
K:Cm
V:1 clef=treble
V:2 clef=bass
%% V→vi (denied), V→bVI (denied again), V→i (earned)
[V:1] [B,D]2 [CE]2|!p![B,D]2 [C_E_A]2|!ff![B,D]2 [CG]2|[C4_E4G4]|
[V:2] G,,2 C,2|G,,2 _A,,2|G,,2 G,,2|C,4|
%% V-vi, V-bVI, V-V, i: resolution earned through repeated denial
```

## Late-Period Harmonic Radicalism

| Device | Description | Effect |
|--------|-------------|--------|
| Semitone key juxtaposition | C major followed directly by Db major | Tonal vertigo; the listener's sense of key is suspended |
| Tritone relationship | C→F# or C→Gb with no modulatory bridge | Maximum tonal distance traversed instantly |
| Extended trills as harmonic events | Trills lasting 4–8 bars while harmony shifts beneath them | The surface is static; the ground moves |
| Recitative in instrumental music | Free, speech-like passages interrupting sonata form | Op. 31/2 (Tempest), Op. 110, Ninth Symphony |
| Fugue as harmonic compression | All voices pursuing independent harmonic goals simultaneously | Grosse Fuge — the harmony strains under contrapuntal pressure |

```abc
X:4
T:Late Beethoven — Semitone Key Shift (Op. 111 character)
M:3/4
L:1/8
K:Cm
V:1 clef=treble
V:2 clef=bass
%% C minor to Db — the ground shifts by a semitone
[V:1] G2 c2 _e2|!ff!_d2 f2 _a2|
[V:2] C,2 E,2 G,2|_D,2 F,2 _A,2|
%% No pivot, no preparation — the new key simply arrives
```

## References

- [composition-guide.md](composition-guide.md) — Fingerprints: modal mixture (#3), sfz placement, dynamic contrasts
- [stylistic-evolution.md](stylistic-evolution.md) — Harmonic language intensifies across three periods
- [formal-approach.md](formal-approach.md) — How harmonic events serve formal drama
- [../../classical-harmony.md](../../classical-harmony.md) — Shared functional harmony, cadences, secondary dominants, mode mixture
- [cross-references.md](cross-references.md) — Harmonic contrasts with Haydn and Mozart
