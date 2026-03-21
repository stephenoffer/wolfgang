# Piano Example -- Two-Voice ABC Notation

Reference for writing piano music with separate right-hand (PN_RH) and left-hand (PN_LH) voices.

**Key techniques demonstrated:**
- Melody in RH with broken-chord accompaniment in LH
- Dynamic markings: `!f!`, `!mf!`, `!p!`, `!cresc!`, `!decresc!`
- Modulation from D minor to F major (relative major) and back
- Mixed rhythm: eighth notes, quarter notes, dotted rhythms, ties
- Chord notation `[CEG]` in left hand for harmonic support
- Articulations: `!accent!`, staccato (`.`)

**Structure:** 16 measures, 4/4 time, D minor
- mm. 1-4: Opening theme in D minor (mf)
- mm. 5-8: Transition, modulation to F major (cresc to f)
- mm. 9-12: Contrasting theme in F major (p, legato)
- mm. 13-16: Return to D minor, cadence (cresc to f)

```abc
X:1
T:Piano Piece in D Minor
C:Wolfgang Example
M:4/4
L:1/8
Q:1/4=108
K:Dm
%%staves {PN_RH PN_LH}
V:PN_RH clef=treble name="Piano RH"
V:PN_LH clef=bass name="Piano LH"
%
% == Measures 1-4: Opening theme in D minor ==
%
[V:PN_RH] !mf! d2 ef g2 fe | d2 A2 d3 c | B2 cd e2 dc | A4 A2 z2 |
[V:PN_LH] !mf! [D,A,D]4 [D,A,D]4 | [D,A,D]4 [D,F,A,]4 | [G,,B,,D,]4 [C,E,G,]4 | [F,,A,,C,]4 [A,,C,E,]4 |
%
% == Measures 5-8: Transition, modulating to F major ==
%
[V:PN_RH] !cresc! d2 ef a2 gf | e2 c2 f3 e | d2 Bc A2 G2 | !f! F4 F2 z2 |
[V:PN_LH] !cresc! [D,A,D]4 [D,A,D]4 | [C,G,C]4 [F,,A,,C,]4 | [B,,D,F,]4 [C,E,G,]4 | !f! [F,,A,,C,]4 [F,,A,,C,]4 |
%
% == Measures 9-12: Contrasting theme in F major ==
%
[V:PN_RH] !p! F2 GA c2 BA | G2 E2 F3 G | A2 Bc d2 cB | A4 G2 F2 |
[V:PN_LH] !p! [F,,A,,C,]4 [F,,A,,C,]4 | [C,E,G,]4 [F,,A,,C,]4 | [F,,A,,C,]4 [B,,D,F,]4 | [C,E,G,]4 [C,E,G,]4 |
%
% == Measures 13-16: Return to D minor, final cadence ==
%
[V:PN_RH] !cresc! d2 ef g2 fe | d2 ^c2 d3 e | !f! f2 e2 d2 ^c2 | d8 |]
[V:PN_LH] !cresc! [D,A,D]4 [G,,B,,D,]4 | [A,,E,A,]4 [D,F,A,]4 | !f! [B,,D,F,]4 [A,,^C,E,]4 | [D,,A,,D,]8 |]
```

## Notes for the composing agent

| Technique | How it appears |
|-----------|---------------|
| Dynamic markings | `!mf!`, `!f!`, `!p!` placed before the first note of the passage |
| Crescendo/decrescendo | `!cresc!`, `!decresc!` as inline decorations |
| LH chords | `[D,A,D]` -- notes stacked in brackets, commas lower octave |
| Modulation | mm. 5-8 pivot through C major chord (V of F), confirmed by F chord in m. 8 |
| Return to tonic | m. 14 uses raised 3rd (`^c`) for A major chord (V of Dm), Picardy-free ending |
| Dotted rhythms | Use `d3 c` for dotted-quarter + eighth pattern (3+1 eighth-note units) |
| Tied notes | Use `-` between notes: `d2-d2` for a half note tied to a half note |
| Octave control | Capital `D` = D below middle C; lowercase `d` = D above middle C; `D,` = octave lower; `d'` = octave higher |
| Duration math | In L:1/8, `d2` = quarter note, `d4` = half note, `d8` = whole note, `d` = eighth note |
| Bar completeness | Each bar must total 8 eighth-note units in 4/4 with L:1/8 |
