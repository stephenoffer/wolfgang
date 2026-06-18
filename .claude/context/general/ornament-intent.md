# Ornament Intent — WHY, WHEN, and HOW to Choose Ornaments

> **WMN note:** ABC examples below illustrate ornament notation for reference. For composition output, use WMN ornament objects with type values: `grace_note`, `turn`, `trill`, `mordent`, `appoggiatura`, `chromatic_neighbor`, `grace_flourish`, `arpeggio_roll`, `cadenza_flourish`. See `wmn-format-spec.md` for the ornament array schema.

> This file teaches ornament **semantics** — the purpose, emotion, and phrase integration that makes ornamentation feel inevitable rather than arbitrary. For ornament **syntax** (ABC notation, period conventions, non-chord tone catalog), see `ornamentation-embellishment.md`.

---

## 1. The Philosophy of Ornament

Every ornament should serve an expressive purpose — **"What does this EXPRESS that the bare note does not?"**

| Source | Core Principle | Implication for Composition |
|---|---|---|
| C.P.E. Bach, *Essay on the True Art of Playing Keyboard Instruments* (1753) | Ornaments are **essential vs. arbitrary**: essential ones complete the melody (appoggiaturas, trills at cadences); arbitrary ones add pleasure through improvised variation | Some ornaments are structurally necessary — omitting them leaves the melody incomplete. Others are tasteful additions. Know which is which. |
| Leopold Mozart, *Treatise on Violin Playing* (1756) | Vibrato is an **ornament**, not a default — use it "with clear expressive purpose at specific musical moments" | Every ornament is a deliberate expressive gesture, not a background texture. Place ornaments where they heighten the moment. |
| Quantz, *On Playing the Flute* (1752) | Elaborated ornaments promote "cheer and gaiety"; simple appoggiaturas arouse "tenderness and melancholy" | The **complexity** of the ornament itself communicates emotion. Complex = energetic; simple = intimate. |
| Couperin, *L'art de toucher le clavecin* (1716) | Ornaments **compensate** for what the instrument cannot naturally do — the harpsichord cannot swell, so arpeggiation and suspension create the illusion of dynamics | Choose ornaments that give the instrument what it lacks: piano needs arpeggiation for sustain; strings use vibrato for warmth; winds use flutter for texture. |
| Chopin's teaching | "Listen to great singers" — ornaments are **bel canto** transferred to instruments; the piano must sing | Ornaments should follow the shapes of vocal expression: the breath, the portamento, the melismatic flourish, the catch in the voice. |
| Debussy's practice | The melody IS ornamental — the **arabesque** dissolves the line between structural and decorative | In Impressionist style, don't "add" ornaments to a melody. Write melodies that are inherently sinuous and ornamental in character. |
| Messiaen, *The Technique of My Musical Language* (1944) | Nature (birdsong) is the **original ornament** — all human ornamentation descends from natural sound | When the program calls for nature, ornament IS the content: irregular trills, asymmetric grace-note fragments, non-metrical flourishes. |
| Baroque rhetorical tradition | Ornaments are **musical rhetoric** — the gestures, emphasis, and inflection of a persuasive speaker | Every ornament is an act of persuasion: the appoggiatura pleads, the trill excites, the turn charms, the mordent bites. |

---

## 2. The Ornament Decision Framework

**Don't pick ornaments from a catalog or distribute them at regular intervals.** Listen to what the moment needs. Sometimes the answer is "nothing — the bare note is more powerful." The table below shows *common* pairings, not prescriptions. Great composers constantly violate these defaults — Bartók strips ornaments from climaxes for starkness, Debussy puts grace notes in unexpected places, Wagner ornaments transitions rather than peaks.

| Musical Context | What the Moment Often Needs | Common Choice | Why It Can Work | ABC Pattern |
|---|---|---|---|---|
| Phrase entry (bar 1) | Signal fresh beginning; draw attention | Grace note from below | Mimics a singer's intake of breath before the first word | `{c}d4` |
| Approaching phrase climax | Intensify anticipation; build yearning | Appoggiatura (lean-resolve) | Dissonance on strong beat creates longing before the peak | `{e}d4` or written `e2d4` |
| Sustained note in slow melody | Fill silence; keep the line alive | Turn group around held note | Mimics a singer's vibrato or melismatic turn; the note breathes | `(3ded c4` |
| Cadential arrival (V→I) | Mark the structural boundary | Trill on supertonic | Dominant tension sustained and released at resolution | `!trill!D8 DEDC C8` |
| Emotional peak of section | Maximize expressiveness | Chromatic neighbor sigh | Half-step dissonance = most intimate, most painful interval | `{_e}d4` |
| Between two phrases (link) | Bridge the gap; maintain momentum | Scalar or arpeggiated flourish | Fills silence with directional motion toward next phrase | `DEFG ABcd` (run) |
| Theme return (recap/rondo) | Mark the return as evolved | Add ornaments absent from first statement | Ornamented return = the character has grown; bare original = innocence | First: `d4`; Return: `{c}d2 (3efe d2` |
| Deceptive cadence | Heighten surprise | Escape tone or unexpected leap after V | The ornament "misses" the expected resolution — surprise through misdirection | Step to D, leap to B |
| Dying away (morendo) | Express fading life/energy | Fragmenting ornaments, slowing | Full turn → half-turn → single grace → bare note: the ornament dissolves | `(3ded c2` → `{d}c2` → `c4` |
| Silence after intensity | Let the absence speak | NO ornament — deliberate nakedness | Stripping ornaments where expected creates more power than adding them | Bare note after ornamented passage |

---

## 3. Ornament Psychology — What Makes Listeners Remember

| Principle | What It Means | Bad Example | Good Example |
|---|---|---|---|
| **Ornament as breath** | Ornaments follow speech rhythm: inhale (grace from below), speak (main note), exhale (resolution) | Grace note randomly on beat 3 of bar 5 | Grace note at phrase start = breath before speaking |
| **Ornament as surprise** | Deploy ornaments where the listener does NOT expect them; unexpectedness creates memorability | Trill on every cadence (predictable = invisible) | Trill at cadence 1; silence at cadence 2; appoggiatura at cadence 3 |
| **Ornament as motif** | When an ornament appears, repeat it at structurally parallel moments — it becomes part of the theme's identity | Different ornament type every 4 bars (random) | Same sigh figure `{_e}d` at the start of each phrase in Theme A |
| **Density arc** | Fewer ornaments at the start, more as emotional intensity builds, then strip them away at resolution | Same density throughout (flat = background noise) | Bare → adorned → filigree → bare |
| **Absence = power** | Removing ornaments where the listener expects them creates impact through silence | Always adding ornaments to meet a quota | Ornamented theme in exposition; bare, stripped theme in development = vulnerability, rawness |
| **Ornament as character** | Assign specific ornament types to specific themes — the ornament becomes a leitmotif | Generic ornaments applied everywhere equally | Hero theme: ascending grace `{c}d`; Lament theme: descending chromatic sigh `{_e}d` |
| **Emotional marking** | The brain remembers ornaments at emotional peaks more than ornaments in neutral passages | Ornaments evenly distributed regardless of emotional content | Concentrate the most distinctive ornaments at the section's emotional climax |
| **The unexpected familiar** | Combine predictability (listener expects embellishment at a cadence) with surprise (the specific ornament chosen is not the obvious one) | Always the same cadential trill | A turn where a trill was expected; a silence where a flourish was expected |

---

## 4. Ornaments as Natural Sounds

When the narrative or program calls for nature imagery, ornaments ARE the primary compositional tool — they paint the scene.

| Natural Sound | Ornamental Technique | Best Instrument | ABC Pattern | Repertoire Precedent |
|---|---|---|---|---|
| **Birdsong — warble** | Rapid alternation between 2 notes (measured trill), irregular rhythm, high register | Flute, piccolo, high violin | `e'/f'/e'/d'/ e'2 z/` (irregular grouping) | Beethoven *Pastoral* (2nd mvt), Messiaen *Catalogue d'oiseaux* |
| **Birdsong — call** | Grace note leap up, then step down; short, separated | Flute, oboe, clarinet | `{c}e'4 d'2 c'2` | Mozart Flute Concerto, Vivaldi *Il Gardellino* |
| **Birdsong — cuckoo** | Falling minor 3rd or major 3rd, simple, repeated | Two clarinets, or flute+oboe | `e2c2 z2 e2c2 z2` | Beethoven *Pastoral* (2nd mvt), Saint-Saens *Carnival* |
| **Flowing water** | Continuous 16th arpeggiation, smooth, stepwise bass, lilting | Piano LH, harp, strings | `C/E/G/c/ e/c/G/E/` (undulating wave) | Smetana *Moldau*, Liszt *Les jeux d'eaux*, Chopin *Barcarolle* |
| **Raindrops** | Staccato repeated notes at varying intervals, pp | Piano RH, pizzicato strings | `!pp!!staccato!e2 z2 !staccato!c2 z4 !staccato!g2` | Chopin *Raindrop Prelude* Op. 28/15 |
| **Wind — gust** | Chromatic scalar run, accelerating then fading, hairpin dynamics | Full strings, woodwinds | `!<! CDEF GABc defg abc'd' !>!` | Debussy *Ce qu'a vu le vent d'ouest* |
| **Wind — whisper** | Tremolo pp with very slow chromatic shift, muted | Muted strings, low flute | `!pp! c/B/c/B/ c/B/c/B/` | Debussy *Prelude a l'apres-midi d'un faune* |
| **Church bells** | Wide-spaced arpeggiated chord, each note ringing, deep bass | Piano, harp, chimes, low brass | `C,,/G,/C/E/ [CEGc]4` | Rachmaninoff *Prelude* C#m, Mussorgsky *Boris* |
| **Distant bells** | Single note with grace note octave below, long decay, pp | Piano, celesta, harp | `{C,}C4-C4` | Debussy *Cloches a travers les feuilles* |
| **Thunder** | Low tremolo, crescendo to sfz chord | Timpani, low strings, piano bass | `!pp! C,,/G,,/C,,/G,,/ !<! C,,/G,,/C,,/G,,/ !fff!!sfz![C,,G,,C,]4` | Beethoven *Pastoral* (4th mvt), Vivaldi *Summer* |
| **Heartbeat** | Steady pulse, paired notes (lub-dub), occasional appoggiatura "skip" | Low piano, pizz. cello, timpani | `C,,2 z C,,2 z3 \| {D,,}C,,2 z C,,2 z3` (skip) | Berlioz *Symphonie Fantastique* |
| **Human sigh** | Descending half-step appoggiatura on strong beat, diminuendo | Any lyrical instrument | `!mf! _e2 !>! d4` | Wagner *Tristan*, Rachmaninoff *2nd Concerto* |
| **Laughter** | Staccato ascending 3rds/4ths, accelerating, light | Woodwinds, piano, high strings | `!staccato! CE EG Gc ce` (getting faster) | Beethoven Scherzi, Haydn finales |
| **Weeping** | Descending chromatic neighbors with rests between sobs | Solo violin, oboe, voice | `_e2d2 z2 _B2A2 z2 F2E2 z4` | Barber *Adagio*, Puccini arias |
| **Birdsong — nightingale** | Long sustained note, then rapid filigree descent, then silence | Solo flute | `e'8 \| {e'd'c'Bag}f4 z4` | Respighi *Pines of Rome* III |

---

## 5. Ornament and Emotion

| Emotional State | Ornament Density | Ornament Types | Speed/Character | Approach |
|---|---|---|---|---|
| **Serenity, peace** | Low — sparse, gentle | Occasional gentle grace note, simple neighbor | Unhurried; ornaments barely disturb the surface | One grace per 8-bar phrase; let the melody breathe |
| **Tenderness, love** | Medium-low — selective | Appoggiaturas (sighing), gentle turns, portamento | Ornaments "lean" expressively; weight on the dissonance | Appoggiatura on the most tender word/note of each phrase |
| **Joy, delight** | Medium-high — sparkling | Rapid turns, mordents, quick ascending grace notes | Light, brilliant; ornaments add sparkle | Turns at phrase peaks; mordents on strong beats; everything dances |
| **Passion, yearning** | High — filigree | Written-out chromatic ornaments, arpeggiated flourishes, wide-span grace groups | Flexible tempo; rubato within the ornament itself | Chopin-style filigree; the ornament IS the melody's emotional content |
| **Grief, lament** | Medium — weighted | Slow appoggiaturas, suspensions, chromatic neighbors, descending sighs | Ornaments add weight and pain, not speed | Each appoggiatura is a wound; the dissonance lingers before resolving |
| **Agitation, anxiety** | High — restless | Trills, tremolo, rapid mordents, nervous repeated notes | Fast, unresolved; ornaments heighten nervous energy | Trills that don't resolve cleanly; tremolo that builds without release |
| **Triumph, grandeur** | Low-medium — structural | Written-out trills as texture, broad cadential flourishes, fanfare grace notes | Bold, not delicate; ornaments are architectural, not filigree | Cadential trills at structural arrivals; grace notes announce, not whisper |
| **Terror, dread** | Extremes — stark OR frantic | Either stark bare notes (frozen terror) or frantic over-ornamentation (panic) | Either frozen stillness or chaotic excess | Choose one extreme: the music is either paralyzed or hysterical |
| **Nostalgia, memory** | Low-medium — ghostlike | Fragments of earlier ornaments, simplified versions | Slower than the original; ornaments are echoes of what was | Quote an ornament from an earlier section, but incomplete — as if remembered imperfectly |
| **Wonder, awe** | Low — spacious | Wide-spaced arpeggiated chords, bell-like grace notes, high harmonics | Open, spacious; ornaments shimmer rather than move | Bell sonority; high sustained notes with occasional ethereal grace |

---

## 6. Ornament Integration with Phrase Structure

**Ornaments are not sprinkled on top of a finished melody. They are woven into the phrase's architecture.**

### 8-Bar Phrase Ornament Template

| Bar | Phrase Role | Ornament | Why |
|---|---|---|---|
| 1 | Entry — the first word | Grace note from below (breath) | Singer's inhale before the opening gesture |
| 2 | Continuation — momentum | None or light passing tones | Let the melody speak without interruption |
| 3 | First peak — local high point | Turn group or upper neighbor | The phrase reaches upward; the turn flowers at the peak |
| 4 | Descent — energy release | Passing tones fill the fall | The exhale; stepwise motion smooths the descent |
| 5 | Second entry — renewed energy | Varied grace or none | Contrast: if bar 1 had grace from below, bar 5 has grace from above (or silence) |
| 6 | Build to climax — tension rising | Appoggiatura on strong beat | Dissonance = yearning; the most expressive moment |
| 7 | Climax — maximum expression | Trill or written-out flourish | The culmination; the ornament is the emotional peak |
| 8 | Resolution — arrival | Simple, unornamented | Arrival needs clarity, not decoration; let the resolution land |

### ABC Example — Adagio Lyrical Phrase (Romantic style, C major)

```abc
X:1
T:Ornament Integration - Adagio Phrase
M:4/4
L:1/8
Q:1/4=66
K:C
% Bar 1: grace note breath at entry
{B,}C2 E2 G2 c2 |
% Bar 2: unornamented continuation
e2 d2 c2 B2 |
% Bar 3: turn at first peak
(3efe d2 c2 E2 |
% Bar 4: passing tones in descent
G2 FE D2 C2 |
% Bar 5: no grace (contrast with bar 1)
E2 G2 c2 e2 |
% Bar 6: appoggiatura — yearning
{f}e2 d2 {d}c2 B2 |
% Bar 7: cadential trill — climax
!trill!D6 DC |
% Bar 8: bare resolution — arrival
C8 |
```

### ABC Example — Allegro Moderato Dramatic Phrase (Classical style, D minor)

```abc
X:2
T:Ornament Integration - Allegro Phrase
M:4/4
L:1/16
Q:1/4=112
K:Dm
% Bar 1: mordent bite at entry
!mordent!D4 F4 A4 d4 |
% Bar 2: driving motion, no ornament
e4 d4 c4 B4 |
% Bar 3: written-out turn at peak
A2B2A2G2 A4 F4 |
% Bar 4: scalar descent (passing tones)
G2A2B2c2 d2c2B2A2 |
% Bar 5: silence instead of grace (surprise)
z4 D4 F4 A4 |
% Bar 6: chromatic appoggiatura — intensity
_B4 A4 G4 ^F4 |
% Bar 7: trill on dominant
!trill!A8 A2G2^F2E2 |
% Bar 8: strong unornamented cadence
D8 z8 |
```

### Ornament Density Arc Across a Full Section

| Section Position | Density | What to Do | Purpose |
|---|---|---|---|
| Opening (bars 1-8) | LOW | 1-2 simple graces, perhaps a mordent | Establish theme identity without clutter |
| Continuation (bars 9-16) | MEDIUM | Add turns at peaks, passing-tone groups, gentle trills | Theme is known; begin to flower |
| Development (bars 17-32) | MEDIUM-HIGH | Written-out flourishes, appoggiaturas, chromatic neighbors | Emotional deepening; the music becomes more expressive |
| Climax (bars 33-40) | HIGH | Filigree, cadential trills, cascading runs, maximum ornamental density | Maximum expression — this is where the most memorable ornaments go |
| Resolution (bars 41-48) | LOW | Strip ornaments away; return to simplicity | Arrival, peace — the ornament dissolution signals closure |

---

## 7. Decorative vs. Structural Ornaments

Not all ornaments serve the same role. Knowing which category an ornament falls into determines whether it can be removed, varied, or should be preserved.

| Category | Definition | When to Use | Example |
|---|---|---|---|
| **Structural** | Part of the theme's identity; removing it changes the music fundamentally | Theme statements, motifs, anywhere the ornament IS the content | Beethoven's written-out turn in *Waldstein* Op. 53 — remove it and the theme loses its character |
| **Expressive** | Communicates specific emotion at a specific moment; the dissonance or gesture IS the feeling | Emotional peaks, sighs, yearning gestures, moments of intimacy | Rachmaninoff's chromatic neighbor sigh — the half-step dissonance IS the emotion of longing |
| **Transitional** | Bridges between phrases or sections; creates continuity and forward motion | Connecting passages, phrase links, between theme statements | A scalar flourish connecting first and second theme groups; keeps energy flowing |
| **Decorative** | Surface beauty; removable without changing the harmonic/melodic meaning | Returns, cadenzas, slow movements where beauty is the point | Chopin Nocturne filigree — remove it and the harmony still works, but the magic is in the ornament |

**Composition guideline:** Structural ornaments are typically consistent across all appearances of a theme. Expressive ornaments should match the emotional context. Transitional ornaments should point toward the next phrase. Decorative ornaments should suit the period and style.

---

## 8. The Melodic Embellishment Process

**How to build from skeleton to fully ornamented melody — with the reasoning behind each step.**

### Step 0: Skeleton — chord tones on strong beats

```abc
X:3
T:Step 0 - Skeleton (chord tones only)
M:4/4
L:1/4
K:C
"I"C E G E | "IV"F A F A | "V"G B G B | "I"c G E C |
```

**Why start here:** The skeleton is the harmonic foundation. Every embellishment step should preserve these structural notes on strong beats.

### Step 1: Add passing tones — smooth the connections

```abc
X:4
T:Step 1 - Passing tones
M:4/4
L:1/8
K:C
"I"C2 DE FE DC | "IV"F2 GA GF EF | "V"G2 AB AG FG | "I"c2 BA GF ED |
```

**Why:** Passing tones create stepwise motion between chord tones. They make the line singable — a voice naturally fills intervals with steps.

### Step 2: Add neighbor tones — create contour

```abc
X:5
T:Step 2 - Neighbor tones
M:4/4
L:1/8
K:C
"I"CD CE FE ED | "IV"FG FA GF EF | "V"GA AB AG ^FG | "I"cd cB AG FE |
```

**Why:** Neighbor tones add local interest — the melody touches the note above or below and returns. This creates the small waves within the larger contour.

### Step 3: Add appoggiaturas — tension on strong beats

```abc
X:6
T:Step 3 - Appoggiaturas
M:4/4
L:1/8
K:C
"I"DC CE FE ED | "IV"GF FA GF EF | "V"AB AB AG ^FG | "I"dc cB AG FE |
```

**Why:** Placing a dissonant note on the strong beat and resolving to the chord tone on the weak beat creates the most expressive gesture in tonal music — the lean-and-resolve that mimics a sigh or plea.

### Step 4: Add ornamental groups — turns at peaks

```abc
X:7
T:Step 4 - Turns at peaks
M:4/4
L:1/16
K:C
"I"D2C2 C2E2 FGFE E2D2 | "IV"G2F2 F2A2 GAGF E2F2 | "V"A2B2 A2B2 ABAG ^F2G2 | "I"dcdc c2B2 A2G2 FEDC |
```

**Why:** Turns flower at the phrase's high points. They mark the peak with a brief flourish — like a singer adding a melismatic turn on the most important word.

### Step 5: Add grace notes — breath at entries

```abc
X:8
T:Step 5 - Grace notes at entries
M:4/4
L:1/16
K:C
{B,}D2C2 C2E2 FGFE E2D2 | {E}G2F2 F2A2 GAGF E2F2 | {^F}A2B2 A2B2 ABAG ^F2G2 | {d}dcdc c2B2 A2G2 FEDC |
```

**Why:** Grace notes at phrase entries are the musical equivalent of a singer's breath before the first note. They signal "a new idea begins here" and draw the listener's attention to the entry point.

**The key insight:** Each step serves a different PURPOSE. Passing tones smooth connections. Neighbors add interest. Appoggiaturas create emotion. Turns mark peaks. Grace notes signal entries. Knowing WHY means knowing WHEN to use each technique.
