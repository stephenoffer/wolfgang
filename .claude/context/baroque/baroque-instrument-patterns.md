# Baroque Instrument Patterns -- Genre-Wide Encyclopedia

Comprehensive collection of idiomatic Baroque instrumental patterns applicable across composers and genres. Each pattern includes name, ABC example with instrument designation, usage context, and variation suggestions.

---

## Continuo Patterns

### BP1: Walking Bass (Stepwise Motion)
```abc
X:400
T:Baroque Walking Bass
M:4/4
L:1/8
K:C
V:1 name="Melody"
V:2 name="Basso Continuo" clef=bass
%% Stepwise ascending/descending bass; one note per beat
[V:1] e4 d4|c4 B4|A4 G4|C4 z4|
[V:2] C,2D,2 E,2F,2|G,2A,2 B,2G,2|F,2E,2 D,2G,2|C,4 z4|
```
**Usage:** Standard continuo motion in arias, choruses, and instrumental movements. Creates forward momentum while outlining harmony.
**Variation:** Add chromatic passing tones; use leaps at cadences; mix stepwise and arpeggiated motion.

### BP2: Ground Bass (Ostinato)
```abc
X:401
T:Baroque Ground Bass
M:3/4
L:1/4
K:Dmin
V:1 name="Bass" clef=bass
%% Repeating 4- or 8-bar bass pattern; supports variations above
D2 C|B,2 A,|G,2 F,|E, A, D,|D2 C|B,2 A,|G, A, A,,|D,3|
```
**Usage:** Passacaglias, chaconnes, lament arias. The repeating bass anchors an entire movement while upper voices elaborate freely.
**Variation:** Chromaticize the descent; migrate to upper voices; fragment in later variations; ornament the bass itself.

### BP3: Alberti-Precursor Arpeggiated Bass
```abc
X:402
T:Baroque Arpeggiated Continuo
M:4/4
L:1/8
K:G
V:1 name="Melody"
V:2 name="Continuo" clef=bass
%% Broken chord bass; proto-Alberti; light texture
[V:1] d4 B4|c4 A4|B4 G4|G4 z4|
[V:2] G,B,D G,B,D G,B,|C,E,G, C,E,G, C,E,|D,F,A, D,F,A, D,|G,,B,,D, G,,4 z|
```
**Usage:** Lighter textures in keyboard continuo realization; sonatas and chamber music. Provides harmonic fill without heaviness.
**Variation:** Vary arpeggiation direction; mix with sustained bass notes; thin out for delicate passages.

### BP4: Pedal Point Bass (Tonic Drone)
```abc
X:403
T:Baroque Tonic Pedal Bass
M:4/4
L:1/4
K:D
V:1 name="Upper voices"
V:2 name="Continuo" clef=bass
%% Sustained tonic pedal; harmony moves freely above
[V:1] F A d c|B A G F|E F G A|D4|
[V:2] D, D, D, D,|D, D, D, D,|D, D, D, D,|D,4|
```
**Usage:** Opening and closing passages; ritornello beginnings; moments of tonal stability. Creates anchor for harmonic movement above.
**Variation:** Dominant pedal for pre-cadential tension; oscillating pedal (tonic-dominant alternation); rhythmicize the pedal.

### BP5: Figured Bass Realization -- Standard Chord Patterns
```abc
X:404
T:Baroque Figured Bass Realization
M:4/4
L:1/4
K:C
V:1 name="Realization (RH)"
V:2 name="Bass" clef=bass
%% Right-hand chordal realization above bass; standard figures
[V:1] [CEG] [DFA] [EGB] [FAc]|[EGc] [DFA] [DGB] [CEG]|
[V:2] C, D, E, F,|C, D, G,, C,|
```
**Usage:** Keyboard continuo realization from figured bass. The right hand fills in harmonies above the written bass line.
**Variation:** Add passing tones between chords; arpeggiate instead of block chords; add inner voice movement.

### BP6: Continuo Punctuation (Chordal Stabs)
```abc
X:405
T:Baroque Continuo Punctuation
M:4/4
L:1/4
K:Amin
V:1 name="Solo (voice/instrument)"
V:2 name="Continuo" clef=bass
%% Short chords punctuating between phrases; recitative style
[V:1] A B c d|e4|d c B A|A4|
[V:2] [A,CE] z z z|[E,^GB,] z z z|[D,FA] z z z|[A,,CE] z z z|
```
**Usage:** Recitative accompaniment; light textures under solo passages. Brief chords mark harmonic changes without obscuring melody.
**Variation:** Add arpeggiated chords; vary density of punctuation; sustain chords for accompagnato texture.

---

## Keyboard Patterns

### BP7: Preludio Figuration (Broken Chord Perpetual Motion)
```abc
X:406
T:Baroque Preludio Figuration
M:4/4
L:1/16
K:C
%% Single figuration pattern repeated with changing harmonies
C2E2G2c2 E2G2c2e2|D2F2A2d2 F2A2d2f2|E2G2B2e2 G2B2e2g2|F2A2c2f2 f8|
```
**Usage:** Toccata and prelude openings; establishes key through arpeggiated figuration before fugue or more structured composition.
**Variation:** Change arpeggiation direction; mix ascending/descending; add chromatic harmonies; vary rhythm within figuration.

### BP8: Toccata Virtuosic Passage (Free Figuration)
```abc
X:407
T:Baroque Toccata Passage
M:C
L:1/32
K:Dmin
%% Free, improvisatory running passage; keyboard virtuosity
D4F4A4d4 f4a4d'4f'4|e'4d'4c'4_b4 a4g4f4e4|
d4c4_B4A4 G4F4E4D4|^C4D4E4F4 G4A4_B4^c4|d16 z16|
```
**Usage:** Toccata opening flourishes, passage-work episodes, cadenza-like passages. Demonstrates keyboard mastery.
**Variation:** Add measured trills; use chromatic scales; alternate hands rapidly; insert dramatic pauses.

### BP9: Fugue Exposition Keyboard Layout
```abc
X:408
T:Baroque Fugue Exposition (Keyboard)
M:4/4
L:1/8
K:Amin
V:1
V:2 clef=bass
%% Voice 1 (soprano), Voice 2 (alto), Voice 3 (bass) enter successively
[V:1] A,2 CE A2 GF|E2 DC B,2 A,2|z8|z8|
[V:2] z8|z8|E,2 G,B, E2 DC|B,2 A,G, F,2 E,2|
```
**Usage:** Standard fugue exposition at the keyboard. Subject enters in one voice; answer follows in another; countersubject accompanies.
**Variation:** Real vs. tonal answer; add countersubject immediately; modify for 3- or 4-voice texture.

### BP10: Keyboard Suite Prelude (Mixed Figuration)
```abc
X:409
T:Baroque Suite Prelude
M:4/4
L:1/16
K:Gmin
V:1
V:2 clef=bass
%% Combines arpeggiation, scales, and dotted rhythms in free prelude
[V:1] G,2B,2D2G2 B2d2g2b2|a2g2f2e2 d2c2B2A2|
[V:2] G,,4 G,,4 G,,4 G,,4|D,4 D,4 D,4 D,4|
```
**Usage:** Opening prelude of a keyboard suite. Free in character, establishing key and mood before structured dances.
**Variation:** Extend with improvisatory passages; add dotted-rhythm sections; modulate and return.

---

## String Patterns

### BP11: Bariolage (Rapid Open/Stopped String Alternation)
```abc
X:410
T:Baroque Bariolage - Violin
M:4/4
L:1/16
K:A
V:1 name="Violin"
%% Alternation between stopped note on one string and open string on another
c2e2c2e2 B2e2B2e2|A2e2A2e2 ^G2e2A2e2|
```
**Usage:** Extended pedal-point episodes in solo concertos and sonatas. The open string creates a drone effect while the stopped note provides melody. Characteristic of Italian violin school.
**Variation:** Use different open strings (A, D, G) as drone; shift stopped note chromatically; vary speed.

### BP12: String Tremolo (Measured Repeated Notes)
```abc
X:411
T:Baroque String Tremolo
M:4/4
L:1/16
K:Dmin
V:1 name="Violin I"
V:2 name="Violin II"
V:3 name="Viola"
V:4 name="Bass" clef=bass
%% Measured tremolo (counted 16ths); creates intensity
[V:1] d2d2d2d2 d2d2d2d2|c2c2c2c2 c2c2c2c2|
[V:2] A2A2A2A2 A2A2A2A2|G2G2G2G2 G2G2G2G2|
[V:3] F2F2F2F2 F2F2F2F2|E2E2E2E2 E2E2E2E2|
[V:4] D,2D,2D,2D,2 D,2D,2D,2D,2|C,2C,2C,2C,2 C,2C,2C,2C,2|
```
**Usage:** Dramatic passages, storm scenes, heightened emotion. In Baroque context, tremolo is always measured (counted subdivisions), not the unmeasured bow tremolo of later periods.
**Variation:** Move all parts chromatically; alternate tremolo with sustained notes; use on single part while others sustain.

### BP13: Double Stops (Violin Chordal Writing)
```abc
X:412
T:Baroque Violin Double Stops
M:3/4
L:1/8
K:Gmin
V:1 name="Solo Violin"
%% Chords and double stops creating implied polyphony
[D2G2] [E2A2] [F2B2]|[G2B2] [A2c2] [B2d2]|[c2e2] [B2d2] [A2^F2]|[G4B4d4] z2|
```
**Usage:** Solo sonatas and partitas; cadential emphasis in concertos. Creates harmonic fullness from a single instrument.
**Variation:** Add triple stops at strong beats; arpeggiate chords quickly; mix double stops with single-line running passages.

### BP14: Arco/Pizzicato Alternation
```abc
X:413
T:Baroque Arco-Pizzicato Pattern
M:4/4
L:1/4
K:E
V:1 name="Violin I (arco)"
V:2 name="Violin II (arco)"
V:3 name="Bass (pizz)" clef=bass
%% Arco melody with pizzicato bass; contrasting articulations
[V:1] !arco!^G2 A B|^G2 ^F E|
[V:2] !arco!E2 E E|E2 ^D B,|
[V:3] !pizz!E, z E, z|E, z B,, z|
```
**Usage:** Slow movements, delicate textures (Vivaldi Spring II). Pizzicato bass beneath arco melody creates lightness.
**Variation:** All strings pizzicato for special effect; alternate arco and pizzicato within phrases; use pizzicato for rain effects.

### BP15: Concertino vs Ripieno Texture
```abc
X:414
T:Baroque Concertino-Ripieno Contrast
M:4/4
L:1/8
K:D
V:1 name="Concertino Vn"
V:2 name="Ripieno Vn I"
V:3 name="Ripieno Bass" clef=bass
%% Small group (concertino) alternates with full ensemble (ripieno)
[V:1] !f!D2FA d2AF|!p!D2FA d2AF|
[V:2] !f!D2FA d2AF|!p!z8|
[V:3] !f!D,4 D,4|!p!D,4 D,4|
```
**Usage:** Concerto grosso texture (Corelli, Handel, Vivaldi). The alternation between small and large ensemble is the primary structural articulator.
**Variation:** Overlap concertino and ripieno; vary material between the groups; build to combined climax.

### BP16: Unison String Ritornello
```abc
X:415
T:Baroque Unison String Ritornello
M:4/4
L:1/16
K:Amin
V:1 name="All Strings (unison)"
%% Full orchestra in octave unison; maximum rhythmic power
A,4C4E4A4|B4c4d4e4|f4e4d4c4|B4A4^G4A4|A,8 z8|
```
**Usage:** Ritornello openings and returns; powerful structural markers. Unison/octave texture projects the theme with maximum clarity.
**Variation:** Harmonize on repeat; add winds doubling; fragment for abbreviated returns.

---

## Ornament Conventions

### BP17: Baroque Trill (Upper-Note Start, On Beat)
```abc
X:416
T:Baroque Trill (Upper-Note Start)
M:4/4
L:1/32
K:C
%% Trill on D: starts on upper note (E), on the beat
E4D4E4D4 E4D4E4D4|D16 z16|
%% With terminal turn
E4D4E4D4 E4D4C4D4|D16 z16|
```
**Usage:** Baroque trills characteristically begin on the upper auxiliary note, on the beat. This is the defining difference from Classical/Romantic trills. Cadential trills (on supertonic before tonic) are a strong convention of the style.
**Variation:** Vary speed (slow start, accelerate); add prefix from below; add terminal turn; extend or shorten.

### BP18: Mordent (Lower-Note, Quick)
```abc
X:417
T:Baroque Mordent
M:4/4
L:1/32
K:C
%% Mordent on D: main-lower-main, quick
D4C4D4 z4 z16|
%% Double mordent
D4C4D4C4D4 z4 z8 z4|
```
**Usage:** On stressed beats to add bite and accent. Quick alternation with note BELOW (opposite of trill which uses note above).
**Variation:** Single vs. double mordent; chromatic lower auxiliary in minor contexts; combine with other ornaments.

### BP19: Turn (Doppelschlag)
```abc
X:418
T:Baroque Turn
M:4/4
L:1/32
K:C
%% Turn on D: upper-main-lower-main
E4D4C4D4 z16|
%% Turn between notes (connecting C to E via D-turn)
C8 E4D4C4D4 E16|
```
**Usage:** At melodic peaks, between notes as a connector, over sustained notes to maintain interest. The turn can be placed ON a note or BETWEEN two notes.
**Variation:** Inverted turn (lower-main-upper-main); vary rhythm (triplet vs. even); chromatic auxiliaries in minor.

### BP20: Appoggiatura (Long, On Beat)
```abc
X:419
T:Baroque Appoggiatura
M:4/4
L:1/8
K:C
%% Long appoggiatura: takes half the value of the main note
%% Written as grace note before D, performed as E-D
E2D2 z4|
%% Short appoggiatura (acciaccatura): crushed quickly into main note
%% Shown as very short upper neighbor
E/D3 z4|
```
**Usage:** Expressive dissonance on the beat; the appoggiatura characteristically falls on the beat (not before it). Takes time from the main note, not from the previous note. Creates lean-resolve gesture.
**Variation:** From above or below; vary length (half to three-quarters of main note value); chain appoggiaturas.

### BP21: Agrements -- French Ornamental Vocabulary
```abc
X:420
T:Baroque French Agrements Collection
M:4/4
L:1/32
K:D
%% Port de voix (ascending appoggiatura + trill)
^C4D4 E4D4E4D4E4D4|
%% Coule (descending appoggiatura)
E4D4 D16|
%% Aspiration (articulation lift before note)
D8 z4 D4 z16|
%% Pince (mordent in French style)
D4^C4D4 z4 z16|
```
**Usage:** French Baroque keyboard and orchestral music (Couperin, Rameau, French-influenced Bach). Ornaments are essential to the style; a piece without them sounds naked.
**Variation:** Combine ornaments (trill with mordent termination); add inegalite (uneven note pairs); vary density by tempo.

### BP22: Cadential Trill Formula
```abc
X:421
T:Baroque Cadential Trill
M:4/4
L:1/16
K:D
V:1 name="Melody"
V:2 name="Bass" clef=bass
%% Standard cadential trill on supertonic (E) over V, resolving to I
[V:1] F2G2A2B2 c4 z4|F2E2F2E2 F2E2D2^C2|D8 z8|
[V:2] D,4 D,4 A,,4 z4|A,,4A,,4 A,,4A,,4|D,8 z8|
```
**Usage:** Cadential trills are a strong convention of Baroque style; their omission is unusual and should be a deliberate choice. A trill on the supertonic (2nd scale degree) over the dominant is characteristic at authentic cadences.
**Variation:** Add prefix from below; extend trill over multiple beats; terminate with turn; use nachschlag (two-note suffix).

---

## Dance Patterns

### BP23: Allemande (Moderate 4/4, Upbeat of 1-3 Notes)
```abc
X:422
T:Baroque Allemande
M:4/4
L:1/16
K:Dmin
V:1
V:2 clef=bass
%% Upbeat opening; flowing 16ths; moderate tempo; binary form
[V:1] z12 D2E2|F2G2A2B2 c2d2e2f2|g2f2e2d2 c2B2A2G2|F4 z4 z8|
[V:2] z12 z4|D,4 D,4 A,,4 A,,4|B,,4 B,,4 C,4 C,4|D,4 z4 z8|
```
**Usage:** First dance of suite. Moderate quadruple meter, upbeat of 1-3 short notes, flowing character. Most complex of the dances.
**Variation:** Add richer inner voices; ornament on repeat; increase rhythmic activity for more virtuosic character.

### BP24: Courante (French: Complex 3/2, Cross-Rhythms)
```abc
X:423
T:Baroque French Courante
M:3/2
L:1/4
K:Amin
V:1
V:2 clef=bass
%% Ambiguity between 3/2 and 6/4; cross-rhythms at cadences
[V:1] A2 B c2 d|e2 d c2 B|
%% Hemiola: regroups as 6/4 at cadence
A B c d e c|B6|
[V:2] A,,2 G,, F,,2 E,,|A,,2 B,, C,2 D,|E,,2 A,,2 E,2|A,,6|
```
**Usage:** Second dance of French suite. Complex, noble character with metric ambiguity. Distinguished from the Italian corrente (faster, simpler).
**Variation:** Alternate 3/2 and 6/4 groupings; increase hemiola frequency near cadences; pair with corrente for contrast.

### BP25: Corrente (Italian: Fast 3/4 or 3/8, Running)
```abc
X:424
T:Baroque Italian Corrente
M:3/8
L:1/16
K:G
V:1
V:2 clef=bass
%% Fast, running character; lighter than French courante
[V:1] G2A2B2|c2B2A2|B2c2d2|e2d2c2|B2A2G2|A2B2c2|B2A2G2|G6|
[V:2] G,6|A,6|G,6|C,6|D,6|D,6|D,6|G,,6|
```
**Usage:** Fast triple-meter dance in Italian suites. Lighter, simpler than French courante. Running eighth/sixteenth notes.
**Variation:** Add dotted rhythms; extend sequences; increase tempo for presto finale character.

### BP26: Sarabande (Slow 3/4, Beat-2 Emphasis)
```abc
X:425
T:Baroque Sarabande
M:3/4
L:1/8
K:Dmin
V:1
V:2 clef=bass
%% Slow; characteristic emphasis on beat 2 (dotted or agogic)
[V:1] D2 E3F|G2 A3B|c2 B2 A2|A4 G2|F2 D2 E2|D4 z2|
[V:2] D,2 C,3D,|E,2 F,3G,|A,,2 B,,2 C,2|D,4 E,2|D,2 B,,2 A,,2|D,,4 z2|
```
**Usage:** Central slow dance of suite. The defining feature is emphasis on beat 2 (longer note, ornament, or harmonic weight on beat 2). Most emotionally profound of the dances.
**Variation:** Heavily ornament the melody; write doubles (ornamental variation); add chordal texture for gravity.

### BP27: Gigue (Fast 6/8, Often Fugal)
```abc
X:426
T:Baroque Gigue
M:6/8
L:1/8
K:G
V:1
V:2 clef=bass
%% Fast compound meter; quasi-fugal opening; dotted rhythms
[V:1] z2 D|G2 B d2 B|A2 ^F D2 A|B2 G E2 G|^F D A, z2 D|G3 z3|
[V:2] z6|z6|z6|z6|z2 G,|D,2 G, B,,2 G,|
```
**Usage:** Final dance of suite. Fast compound meter, often with fugal or imitative opening. Inverted subject for second half is common.
**Variation:** Use strict fugal opening; invert subject in second half; add triplet embellishments; extend with stretto.

### BP28: Minuet (Moderate 3/4, Elegant Simplicity)
```abc
X:427
T:Baroque Minuet
M:3/4
L:1/4
K:G
V:1
V:2 clef=bass
%% Elegant, balanced; clear 4+4 bar phrases; simplest dance
[V:1] G A B|c2 B|A G ^F|G3|d c B|A2 G|^F E ^F|G3|
[V:2] G, ^F, G,|E, A,, D,|D, E, D,|G,,3|B,, A,, G,,|D, ^F, G,|D, C, D,|G,,3|
```
**Usage:** Optional dance in suites (often paired with Minuet II/Trio). The most straightforward of Baroque dances; elegant simplicity.
**Variation:** Pair with Minuet II in minor (or trio with different instrumentation); ornament on repeat; use as basis for variation set.

### BP29: Bourree (Quick 2/2, Quarter-Note Upbeat)
```abc
X:428
T:Baroque Bourree
M:2/2
L:1/8
K:Emin
V:1
V:2 clef=bass
%% Quick duple; characteristic quarter-note upbeat; sturdy
[V:1] z2 B,2|E2 F2 G2 A2|B2 c2 d2 B2|A2 G2 ^F2 E2|^D2 B,2 z2 B2|e4 z4|
[V:2] z2 z2|E,4 E,4|G,4 B,,4|C,4 A,,4|B,,4 z2 ^D,2|E,4 z4|
```
**Usage:** Quick, vigorous dance; optional movement in suites. Defined by the quarter-note (half-bar) upbeat.
**Variation:** Pair with Bourree II in contrasting key; add countermelody; increase virtuosity with running passages.

### BP30: Gavotte (Moderate 2/2, Half-Bar Upbeat)
```abc
X:429
T:Baroque Gavotte
M:2/2
L:1/4
K:D
V:1
V:2 clef=bass
%% Moderate duple; half-bar upbeat starting mid-bar; graceful
[V:1] z2 D E|F2 G A|B2 A G|F2 E D|E2 ^C D|
[V:2] z2 z2|D,2 E, F,|G,2 F, E,|D,2 C, B,,|A,,2 A,, D,|
```
**Usage:** Elegant dance in suites; occasionally paired with Musette (gavotte with drone bass). Half-bar upbeat is the defining feature.
**Variation:** Add musette trio (with drone bass); ornament on repeat; use as rondeau theme.

### BP31: Siciliano (Slow 6/8 or 12/8, Dotted Pastoral)
```abc
X:430
T:Baroque Siciliano
M:6/8
L:1/8
K:Gmin
V:1
V:2 clef=bass
%% Lilting compound meter; dotted pastoral character; often minor
[V:1] G3 A2G|F3 E2D|E3 F2G|D3 z3|B3 c2d|c3 B2A|G3 ^F2G|G3 z3|
[V:2] G,3 F,3|E,3 D,3|C,3 D,3|G,,3 z3|G,3 A,3|F,3 G,3|E,3 D,3|G,,3 z3|
```
**Usage:** Slow movements in concertos and sonatas; pastoral arias. The lilting dotted rhythm in compound meter suggests simplicity and tenderness.
**Variation:** Add ornamental turns at dotted-note peaks; use in major for brighter character; increase chromaticism for pathos.

### BP32: Passepied (Quick 3/8, Light Triple)
```abc
X:431
T:Baroque Passepied
M:3/8
L:1/8
K:Bb
V:1
V:2 clef=bass
%% Quick, light triple meter; starts on third beat upbeat
[V:1] z2 F|B2 c|d2 c|B2 A|G3|F2 G|A2 B|c2 B|B3|
[V:2] z2 z|B,,3|B,,3|D,3|E,3|F,3|F,3|F,3|B,,3|
```
**Usage:** Light, quick dance sometimes found in suites. Similar to minuet but faster and lighter in character.
**Variation:** Pair with second passepied; add ornamental variations on repeat; use as scherzo-like movement.

---

## Ensemble Texture Patterns

### BP33: Trio Sonata Texture (2 Treble + Bass)
```abc
X:432
T:Baroque Trio Sonata Texture
M:4/4
L:1/8
K:Gmin
V:1 name="Violin I"
V:2 name="Violin II"
V:3 name="Basso Continuo" clef=bass
%% Two equal treble voices in imitation over bass
[V:1] G2 AB cBAG|z8|d2 dc BAG^F|
[V:2] z8|G,2 G,B, DCBA,|z8|
[V:3] G,,4 C,,4|G,,4 G,,4|D,4 D,4|
```
**Usage:** Fundamental Baroque chamber texture. Two treble instruments imitate and intertwine over continuo. The cornerstone of Corelli, Handel, and Bach chamber music.
**Variation:** Replace violins with flutes/oboes; add imitative entries in bass; use for fugal episodes.

### BP34: Full Baroque Orchestra Tutti
```abc
X:433
T:Baroque Full Orchestral Tutti
M:4/4
L:1/8
K:D
V:1 name="Ob/Vn I"
V:2 name="Ob/Vn II"
V:3 name="Va"
V:4 name="Bsn/Vc/Bass" clef=bass
%% Oboes double violins in tutti; full D major scoring
[V:1] D2FA d2AF|D2FA d4 z2|
[V:2] D2DF A2FD|D2DF A4 z2|
[V:3] A,2A,A, D2DA,|A,2A,A, D4 z2|
[V:4] D,4 D,4|D,4 D,4|
```
**Usage:** Standard Baroque orchestral tutti texture. Oboes double violins; bassoon doubles cello/bass. Terraced dynamics through adding/removing instruments.
**Variation:** Add trumpets/timpani for festive D major; remove oboes for solo passages; use horn instead of trumpet.

### BP35: Choral-Orchestral Colla Parte
```abc
X:434
T:Baroque Colla Parte Chorale
M:4/4
L:1/4
K:G
V:1 name="Ob+S"
V:2 name="A"
V:3 name="T" clef=bass
V:4 name="Bsn+B" clef=bass
%% Instruments double voices; standard Baroque church texture
[V:1] G A B c|d2 c B|A B A G|G4|
[V:2] D F G G|A A G G|F G F E|D4|
[V:3] B, D D E|F F E D|D D D C|B,4|
[V:4] G, D, G, C,|D, D, E, G,|D, B,, D, E,|G,4|
```
**Usage:** Church cantata chorales; instruments play the same notes as voices (colla parte = "with the part"). Standard Lutheran service texture.
**Variation:** Add independent instrumental interludes between chorale phrases; use obbligato instrument above chorale; ornament instrumental doubling.
