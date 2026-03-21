# String Quartet Example -- Four-Voice ABC Notation

Reference for writing string quartet music with V1, V2, VA, VC voices.

**Key techniques demonstrated:**
- Theme in Violin I with countermelody in Cello
- Harmonic fill in V2 and VA (sustained notes, complementary rhythm)
- Voice-leading: smooth stepwise motion in inner parts
- Dynamic changes across the ensemble
- Texture contrasts: homophonic opening (mm. 1-4), contrapuntal middle (mm. 9-12), homophonic close
- Articulations and expression marks

**Structure:** 16 measures, 3/4 time, G minor
- mm. 1-4: Homophonic statement of theme (all parts, mf)
- mm. 5-8: Theme develops, V2 gains independence (cresc)
- mm. 9-12: Contrapuntal passage -- imitative entries (f, then p)
- mm. 13-16: Return to homophony, final cadence (cresc to f)

```abc
X:1
T:String Quartet in G Minor
C:Wolfgang Example
M:3/4
L:1/8
Q:1/4=96
K:Gm
%%staves [V1 V2 VA VC]
V:V1 clef=treble name="Violin I"
V:V2 clef=treble name="Violin II"
V:VA clef=alto name="Viola"
V:VC clef=bass name="Cello"
%
% == Measures 1-4: Homophonic theme statement ==
%
[V:V1] !mf! d3 e d2 | g4 f2 | e2 d2 c2 | d6 |
[V:V2] !mf! B4 A2 | B4 A2 | G2 F2 E2 | D6 |
[V:VA] !mf! G4 F2 | D4 D2 | C2 A,2 G,2 | A,6 |
[V:VC] !mf! G,4 D,2 | G,4 D,2 | C,2 D,2 C,2 | D,6 |
%
% == Measures 5-8: Development, V2 gains independence ==
%
[V:V1] !cresc! d2 e2 f2 | g4 a2 | B4 c2 | d6 |
[V:V2] !cresc! B2 c2 d2 | B4 c2 | d4 e2 | d6 |
[V:VA] !cresc! G4 A2 | G4 F2 | G4 G2 | F6 |
[V:VC] !cresc! G,4 D,2 | E,4 F,2 | G,4 C,2 | D,6 |
%
% == Measures 9-12: Contrapuntal passage -- imitative entries ==
%
[V:V1] !f! d3 e d2 | z2 z2 d2 | e2 f2 g2 | !p! f4 e2 |
[V:V2] !f! z4 z2 | d3 e d2 | c2 d2 e2 | !p! d4 c2 |
[V:VA] !f! z4 z2 | z4 z2 | G3 A B2 | !p! A4 G2 |
[V:VC] !f! G,3 A, B,2 | A,2 G,2 F,2 | E,2 D,2 G,2 | !p! D,4 C,2 |
%
% == Measures 13-16: Homophonic return, final cadence ==
%
[V:V1] !cresc! d3 e d2 | g4 ^f2 | !f! g6- | g6 |]
[V:V2] !cresc! B4 A2 | B4 A2 | !f! B6- | B6 |]
[V:VA] !cresc! G4 F2 | D4 D2 | !f! D6- | D6 |]
[V:VC] !cresc! G,4 D,2 | G,4 D,2 | !f! G,6- | G,6 |]
```

## Notes for the composing agent

| Technique | How it appears |
|-----------|---------------|
| Homophonic texture | All parts move in the same rhythm (mm. 1-4) |
| Contrapuntal texture | Staggered entries using rests (`z`) for imitation (mm. 9-11) |
| Countermelody | VC has independent melodic line against V1 theme (mm. 9-10) |
| Voice-leading | Inner parts (V2, VA) move by step; avoid parallel 5ths/octaves |
| Clef assignment | V1, V2: `clef=treble`; VA: `clef=alto`; VC: `clef=bass` |
| Tied notes | `g6-` at bar end ties into `g6` at next bar start |
| Raised leading tone | `^f2` in m. 14 for dominant-to-tonic cadence in G minor |
| Rest notation | `z2` = quarter rest, `z4` = half rest, `z6` = dotted-half rest in L:1/8 |
| Bar completeness | Each bar must total 6 eighth-note units in 3/4 with L:1/8 |
| Dynamic balance | Theme voice (V1) often louder; inner parts shape around it |
| Texture planning | Vary density across sections: full chords, then thinned to 2 voices, then full again |
