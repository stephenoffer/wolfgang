# W.A. Mozart — Orchestration

Mozart's orchestra is a chamber ensemble that can blaze. The default is transparency — individual instruments emerge from the texture like characters stepping forward to speak. The tutti is reserved for structural moments (cadences, ritornellos, climaxes); the rest of the time, Mozart thins deliberately, trusting a single oboe or clarinet to carry the emotional weight. This economy is itself an orchestral philosophy: every instrument earns its presence.

## Instrument Roles

| Instrument | Mozart's Role | Characteristic Usage |
|---|---|---|
| Violin I | Melodic leader, operatic soprano | Carries the primary theme in nearly all contexts; sings, doesn't merely play |
| Violin II | Harmonic partner, dialogue voice | Parallel thirds/sixths with Vln I; occasionally takes melody in dialogue passages |
| Viola | Harmonic filler, occasionally melodic | Often doubled with bass; gains independence in late works (K.515, K.516) |
| Cello/Bass | Harmonic foundation | Bass line, Alberti patterns in piano writing; cello solos rare but memorable (K.515) |
| Flute | Bright color, high register | Flute Concertos K.313-314; doubles oboe or violin at the octave; used sparingly in symphonies |
| Oboe | Principal wind voice, expressive warmth | Standard in all orchestral works; solos in slow movements; pairs for warmth |
| Clarinet | Mozart's beloved — warm, vocal, infinitely flexible | Late discovery (from ~1781); Clarinet Concerto K.622, Clarinet Quintet K.581 |
| Bassoon | Wind bass, comic character | Doubles bass in tutti; comic solos in opera (Figaro); pairs with oboe for warmth |
| Horn | Sustaining warmth, hunting calls, heroic color | Pairs in E-flat or D; horn concertos K.412-495; warm sustained notes in slow movements |
| Trumpet | Festive brilliance, ceremonial | Only in D or C major works with timpani; not a solo voice — structural punctuation |
| Timpani | Rhythmic anchor, dramatic thunder | Always paired with trumpets; tonic-dominant tuning; dramatic rolls in development |
| Piano (concertos) | Protagonist — the operatic lead | Dialogues with orchestra as equal; has arias (lyric), recitatives (passage work), ensembles (with winds) |

## Wind Writing — Mozart's Revolution

Mozart liberated wind instruments from mere doubling. In his mature works, winds are independent characters with their own melodic material, especially in slow movements and opera.

| Wind Technique | Description | Example Works |
|---------------|-------------|--------------|
| Wind serenade texture | Pairs of oboes, clarinets, horns, bassoons in pure wind harmony | Gran Partita K.361, Wind Serenades K.375/388 |
| Solo wind over strings | Single wind carries melody, strings accompany | K.622 Clarinet Concerto, K.488 Adagio (clarinet solo) |
| Wind dialogue with piano | Piano and single wind trade phrases in concertos | K.482 Andante (clarinet + piano), K.491 (wind solos) |
| Wind choir punctuation | Winds enter in block chords at cadences | Standard in symphonies — the "wind breath" between string phrases |
| Paired winds in thirds | Two instruments a third apart, moving in parallel | Oboe + clarinet pairs; flute + oboe pairs; warmth and blend |

```abc
X:1
T:Mozart Wind Serenade Texture (Gran Partita style)
M:4/4
L:1/8
K:Bb
V:Ob name="Oboe"
V:Cl name="Clarinet"
V:Hn name="Horn"
V:Bn name="Bassoon" clef=bass
%% Four wind voices — each independent, together creating warmth no strings can match
[V:Ob] d4 c2B2|A2G2 F4|
[V:Cl] B4 A2G2|F2E2 D4|
[V:Hn] F4 F4|C4 B,4|
[V:Bn] B,,4 F,,4|F,,4 B,,4|
```

## The Clarinet — Mozart's Discovery

Mozart encountered the clarinet seriously in Mannheim (1777) and fell in love. The instrument's vocal range, warm tone, and ability to sustain long phrases perfectly matched his melodic ideals.

| Clarinet Quality | Why Mozart Loved It | Where You Hear It |
|-----------------|-------------------|-------------------|
| Three distinct registers (chalumeau, clarion, altissimo) | Each register = a different character voice | K.622: chalumeau = intimate, clarion = singing, altissimo = passionate |
| Vocal sustain | Can hold a note like a singer, with dynamic nuance | K.581 slow movement — long held notes that breathe |
| Warm blending | Merges with strings and other winds uniquely | K.488 — clarinet replaces oboe, warming the entire orchestra |
| Dynamic flexibility | pp to ff without changing tone quality | K.622 — whispered low notes, soaring high notes in the same phrase |

## Texture Strategies

| Strategy | When Mozart Uses It | Resulting Sound |
|----------|-------------------|----------------|
| Full tutti | First theme forte, cadential arrivals, ritornellos | Bright, celebratory — the whole company assembled |
| Strings alone | Lyric themes, intimate passages, quartet texture | Chamber music transparency — the conversation |
| Winds alone | Serenade episodes, wind choir interludes | Warm, pastoral — a different sound world |
| Solo instrument + light accompaniment | Concerto solo passages, aria-like moments | Operatic — one character speaks to the audience |
| Piano + wind dialogue | Piano concerto slow movements | Two characters in intimate conversation |
| Gradual thinning | Approaching a solo or quiet theme | The crowd disperses; one voice remains |
| Crescendo buildup | Approaching tutti cadences | Mannheim crescendo — borrowed and refined |

```abc
X:2
T:Mozart Texture Change — Tutti to Chamber to Solo
M:4/4
L:1/8
K:D
V:V1 name="Vln I"
V:V2 name="Vln II"
V:Va name="Viola" clef=alto
V:Vc name="Cello" clef=bass
%% Bar 1: Full strings tutti
[V:V1] [D2F2A2] [D2F2A2] [E2G2B2] [E2G2B2]|
[V:V2] [A,2D2F2] [A,2D2F2] [B,2E2G2] [B,2E2G2]|
[V:Va] D,4 E,4|
[V:Vc] D,,4 E,,4|
%% Bar 2: Only Vln I remains — the character steps forward
[V:V1] f4 e2d2|
[V:V2] z8|
[V:Va] z8|
[V:Vc] z8|
```

## Piano Concerto Orchestra

The piano concerto is Mozart's laboratory. The orchestra is not accompaniment — it is the other character in an operatic scene.

| Orchestral Function | Role in Concerto | Operatic Parallel |
|-------------------|-----------------|-------------------|
| Opening ritornello | Introduces themes; sets the scene | Overture — the world before the protagonist enters |
| Accompaniment to solo | Light texture, sustained notes, gentle commentary | Orchestra under an aria — supportive but present |
| Wind dialogue with piano | Winds trade phrases with soloist | Ensemble scene — equals conversing |
| Tutti interruptions | Orchestra breaks in with forte statements | Chorus interrupting the soloist — the collective voice |
| Orchestral cadence after solo | Confirms what the soloist just said | Applause, agreement, affirmation |
| Silent pauses (cadenza) | Orchestra waits while soloist improvises | The audience holds its breath |

## Ensemble Configurations

| Ensemble | Standard Instrumentation | Typical Works |
|----------|------------------------|--------------|
| Early symphony | Strings + 2 oboes + 2 horns | Symphonies K.16-200 |
| Mature symphony | Strings + 1 flute + 2 oboes + 2 bassoons + 2 horns + 2 trumpets + timpani | Symphonies 35-41 |
| Symphony with clarinets | As above but clarinets replace or join oboes | K.543 (clarinets, no oboes) |
| Piano concerto (early) | Strings + 2 oboes + 2 horns | K.271, K.414-415 |
| Piano concerto (late) | Strings + flute + 2 oboes/clarinets + 2 bassoons + 2 horns + 2 trumpets + timpani | K.466, K.491, K.503 |
| Wind serenade | 2 oboes + 2 clarinets + 2 horns + 2 bassoons (+ contrabassoon/basset horns) | K.361, K.375, K.388 |
| String quartet | 2 violins + viola + cello | K.387-465, K.499, K.575-590 |
| String quintet | 2 violins + 2 violas + cello | K.515-516, K.593, K.614 |
| Opera orchestra | Full symphony orchestra + trombones (for sacred/supernatural scenes) | Figaro, Don Giovanni, Magic Flute |

## Corpus Piano Texture Statistics (6,987 bars, 18 sonatas, 69 movements)

### Right Hand Textures
| RH Texture | % of bars | Description |
|------------|-----------|-------------|
| singing_melody | 45.1% | Dominant — almost half of all bars are singing melody |
| scalar_run | 16.9% | Passage work, transitions, development |
| zigzag_figuration | 12.8% | Alberti-like RH patterns, broken intervals |
| chordal | 8.6% | Block chords, dramatic punctuation |
| passage_work | 3.5% | Virtuosic figuration |
| dotted_pairs | 2.1% | French overture influence, march-like |
| ornamental_cascade | 1.8% | Cadenzas, written-out ornamentation |
| held_note | 1.6% | Sustained tones over active LH |
| stammer_repeat | 1.4% | Repeated-note figuration |

### Left Hand Textures
| LH Texture | % of bars | Description |
|------------|-----------|-------------|
| alberti | 19.4% | Only 1 in 5 bars — NOT the majority! |
| bass_melody | 15.1% | Nearly as common as Alberti — LH sings too |
| block_chord_sparse | 11.1% | Simple harmonic punctuation |
| pedal_point | 6.6% | Sustained bass, dominant or tonic pedals |
| sparse_punctuation | 6.4% | Minimal bass, RH-dominant texture |
| walking_bass | 5.5% | Stepwise bass motion, contrapuntal |
| block_chord_offbeat | 4.3% | Syncopated chordal accompaniment |
| silence | 3.9% | LH tacet — the music breathes |
| broken_chord_wave | 3.6% | Arpeggiated, wave-like patterns |

**Key Insight**: The "singing melody over Alberti bass" stereotype represents only 9.3% of Mozart's piano writing. He uses bass melodies (15.1%), block chords (11.1%), pedal points (6.6%), walking bass (5.5%), and silence (3.9%) far more than the stereotype suggests. A convincing Mozart piano texture MUST vary the LH pattern every 2-4 bars.

## References

- [composition-guide.md](composition-guide.md) — Fingerprint #3: transparent, chamber-like texture
- [biography.md](biography.md) — Mannheim orchestra, wind serenade tradition
- [melodic-style.md](melodic-style.md) — vocal quality shapes which instruments carry melody
- [formal-approach.md](formal-approach.md) — concerto dialogue as formal principle
- [../../classical-harmony.md](../../classical-harmony.md) — harmonic progressions that drive orchestral texture
