# Full Orchestra Example -- Tutti Passage in ABC Notation

Reference for writing full orchestral tutti in the Romantic style. Key of D minor (Wolfgang default test key).

**Key techniques demonstrated:**
- Melody doubled between V1 and FL1/OB1 (standard orchestral doubling)
- V2 and VA provide harmonic fill
- Brass (HN1, TPT1, TBN1) sustain harmonic pillars
- Timpani on tonic (D) and dominant (A)
- Contrabass doubles Cello at the octave
- Transposing instruments: CL1 (Bb clarinet), HN1 (F horn) -- written at concert pitch with `transpose=` hints
- PN_RH/PN_LH for piano concerto texture
- Dynamic markings for full ensemble balance

**Structure:** 8 measures, 4/4 time, D minor, Romantic tutti
- mm. 1-4: Main theme tutti, D minor (ff)
- mm. 5-6: Dominant prolongation, A major (sf accents)
- mm. 7-8: Cadential resolution back to D minor (ff)

**Transposition reference:**
- CL1 (Bb clarinet): Concert pitch up a major 2nd. Concert D = written E. Key: concert Dm = written Em.
- HN1 (F horn): Concert pitch up a perfect 5th. Concert D = written A. Key: concert Dm = written Am.
- TPT1 (Bb trumpet): Write at concert pitch for Wolfgang; converter handles transposition.

Note: In this example, all parts are written at **concert pitch** with `transpose=` hints on the V: line. This is the recommended Wolfgang convention -- write at concert pitch and let `abc_to_musicxml.py` handle transposition on export.

```abc
X:1
T:Orchestral Tutti in D Minor
C:Wolfgang Example
M:4/4
L:1/8
Q:1/4=120
K:Dm
%%staves [(FL1 OB1 CL1 BN1) (HN1 TPT1 TBN1) TIMP (PN_RH PN_LH) (V1 V2 VA VC CB)]
V:FL1 clef=treble name="Flute 1"
V:OB1 clef=treble name="Oboe 1"
V:CL1 clef=treble name="Clarinet 1" transpose=-2
V:BN1 clef=bass name="Bassoon 1"
V:HN1 clef=treble name="Horn in F 1" transpose=-7
V:TPT1 clef=treble name="Trumpet 1"
V:TBN1 clef=bass name="Trombone 1"
V:TIMP clef=bass name="Timpani"
V:PN_RH clef=treble name="Piano RH"
V:PN_LH clef=bass name="Piano LH"
V:V1 clef=treble name="Violin I"
V:V2 clef=treble name="Violin II"
V:VA clef=alto name="Viola"
V:VC clef=bass name="Cello"
V:CB clef=bass name="Contrabass"
%
% ============================================================
% MEASURES 1-2: Main theme, D minor, full tutti (ff)
% Melody in V1, FL1, OB1. Harmony in all others.
% ============================================================
%
% -- Woodwinds --
[V:FL1] !ff! d'4 c'2 d'2 | e'4 d'2 c'2 |
[V:OB1] !ff! d'4 c'2 d'2 | e'4 d'2 c'2 |
[V:CL1] !ff! a4 g2 a2 | b4 a2 g2 |
[V:BN1] !ff! D,4 E,2 F,2 | G,4 F,2 E,2 |
%
% -- Brass (sustained harmony) --
[V:HN1] !ff! d4 d4 | e4 d4 |
[V:TPT1] !ff! d'4 d'4 | e'4 d'4 |
[V:TBN1] !ff! D,4 D,4 | G,4 F,4 |
%
% -- Percussion --
[V:TIMP] !ff! D,4 z4 | D,4 z4 |
%
% -- Piano (concerto soloist, doubled melody + chords) --
[V:PN_RH] !ff! d'4 c'2 d'2 | e'4 d'2 c'2 |
[V:PN_LH] !ff! [D,A,D]4 [D,A,D]4 | [G,,B,,D,G,]4 [D,A,D]4 |
%
% -- Strings --
[V:V1] !ff! d'4 c'2 d'2 | e'4 d'2 c'2 |
[V:V2] !ff! a4 g2 a2 | b4 a2 g2 |
[V:VA] !ff! f4 e2 f2 | g4 f2 e2 |
[V:VC] !ff! D4 E2 F2 | G4 F2 E2 |
[V:CB] !ff! D,4 E,2 F,2 | G,4 F,2 E,2 |
%
% ============================================================
% MEASURES 3-4: Theme continuation, driving toward dominant
% ============================================================
%
% -- Woodwinds --
[V:FL1] d'2 e'2 f'2 e'2 | d'2 ^c'2 d'4 |
[V:OB1] d'2 e'2 f'2 e'2 | d'2 ^c'2 d'4 |
[V:CL1] a2 b2 c'2 b2 | a2 g2 a4 |
[V:BN1] D,4 A,,4 | A,,4 D,4 |
%
% -- Brass --
[V:HN1] d4 c4 | A,4 d4 |
[V:TPT1] d'4 c'4 | A4 d'4 |
[V:TBN1] D,4 A,,4 | A,,4 D,4 |
%
% -- Percussion --
[V:TIMP] D,4 A,,4 | A,,4 D,4 |
%
% -- Piano --
[V:PN_RH] d'2 e'2 f'2 e'2 | d'2 ^c'2 d'4 |
[V:PN_LH] [D,A,D]4 [A,,E,A,]4 | [A,,^C,E,]4 [D,A,D]4 |
%
% -- Strings --
[V:V1] d'2 e'2 f'2 e'2 | d'2 ^c'2 d'4 |
[V:V2] a2 b2 c'2 b2 | a2 g2 a4 |
[V:VA] f2 g2 a2 g2 | f2 e2 f4 |
[V:VC] D4 A,4 | A,4 D4 |
[V:CB] D,4 A,,4 | A,,4 D,4 |
%
% ============================================================
% MEASURES 5-6: Dominant prolongation (A major), sf accents
% ============================================================
%
% -- Woodwinds --
[V:FL1] !sf! e'4 e'2 d'2 | ^c'4 d'2 e'2 |
[V:OB1] !sf! e'4 e'2 d'2 | ^c'4 d'2 e'2 |
[V:CL1] !sf! b4 b2 a2 | g4 a2 b2 |
[V:BN1] !sf! A,,4 A,,4 | A,,4 A,,4 |
%
% -- Brass --
[V:HN1] !sf! e4 e4 | e4 e4 |
[V:TPT1] !sf! e'4 e'4 | e'4 e'4 |
[V:TBN1] !sf! A,,4 A,,4 | A,,4 A,,4 |
%
% -- Percussion (dominant pedal) --
[V:TIMP] !sf! A,,4 A,,4 | A,,4 A,,4 |
%
% -- Piano --
[V:PN_RH] !sf! e'4 e'2 d'2 | ^c'4 d'2 e'2 |
[V:PN_LH] !sf! [A,,E,A,]4 [A,,E,A,]4 | [A,,^C,E,]4 [A,,E,A,]4 |
%
% -- Strings --
[V:V1] !sf! e'4 e'2 d'2 | ^c'4 d'2 e'2 |
[V:V2] !sf! ^c'4 c'2 a2 | e4 f2 g2 |
[V:VA] !sf! a4 a2 f2 | e4 f2 e2 |
[V:VC] !sf! A,4 A,4 | A,4 A,4 |
[V:CB] !sf! A,,4 A,,4 | A,,4 A,,4 |
%
% ============================================================
% MEASURES 7-8: Cadential resolution to D minor (ff)
% ============================================================
%
% -- Woodwinds --
[V:FL1] !ff! f'4 e'4 | d'8 |]
[V:OB1] !ff! f'4 e'4 | d'8 |]
[V:CL1] !ff! c'4 b4 | a8 |]
[V:BN1] !ff! D,4 A,,4 | D,8 |]
%
% -- Brass --
[V:HN1] !ff! f4 e4 | d8 |]
[V:TPT1] !ff! f'4 e'4 | d'8 |]
[V:TBN1] !ff! D,4 A,,4 | D,8 |]
%
% -- Percussion --
[V:TIMP] !ff! D,4 A,,4 | D,8 |]
%
% -- Piano --
[V:PN_RH] !ff! [d'f'a']4 [^c'e'a']4 | [d'f'a']8 |]
[V:PN_LH] !ff! [D,A,D]4 [A,,E,A,]4 | [D,,A,,D,]8 |]
%
% -- Strings --
[V:V1] !ff! f'4 e'4 | d'8 |]
[V:V2] !ff! a4 a4 | a8 |]
[V:VA] !ff! f4 ^c4 | d8 |]
[V:VC] !ff! D4 A,4 | D8 |]
[V:CB] !ff! D,4 A,,4 | D,8 |]
```

## Orchestration reference table

| Section | Role | Voices | Notes |
|---------|------|--------|-------|
| Melody | Theme carrier | V1, FL1, OB1, PN_RH | Doubled at unison or octave for power |
| Melody support | Third below or parallel | V2, CL1 | Often a 3rd or 6th below V1 |
| Inner harmony | Fill and voice-leading | VA, CL1, HN1 | Smooth stepwise, sustained tones |
| Bass line | Foundation | VC, CB, BN1, TBN1 | CB doubles VC an octave lower |
| Harmonic pillars | Sustained chords | HN1, TPT1, TBN1 | Brass hold chord tones across bars |
| Rhythmic punctuation | Accents on strong beats | TIMP | Tonic (D) and dominant (A) only |
| Solo/concerto | Brilliant figuration | PN_RH, PN_LH | Chords on final cadence for power |

## Transposition conventions for Wolfgang

| Instrument | Voice | Transposition | Convention |
|-----------|-------|---------------|------------|
| Flute | FL1 | Concert pitch (C) | No transposition needed |
| Oboe | OB1 | Concert pitch (C) | No transposition needed |
| Clarinet in Bb | CL1 | `transpose=-2` | Write at concert pitch; converter transposes |
| Bassoon | BN1 | Concert pitch (C) | No transposition needed |
| Horn in F | HN1 | `transpose=-7` | Write at concert pitch; converter transposes |
| Trumpet in Bb | TPT1 | Concert pitch (C) | Write at concert pitch for simplicity |
| Trombone | TBN1 | Concert pitch (C) | No transposition needed |
| Timpani | TIMP | Concert pitch (C) | Only tonic and dominant pitches |

**Recommended approach:** Write ALL parts at concert pitch in the ABC. Use `transpose=` on the V: line to tell `abc_to_musicxml.py` what transposition to apply during MusicXML export. This avoids errors from manual transposition and keeps the ABC score readable.

## Tutti balance tips

- Brass ff overwhelms strings ff -- consider marking brass f when strings are ff
- Timpani rolls (`D,16` or tremolo) sustain better than repeated strokes for long notes
- Double the melody in at least 2 timbral families (strings + winds) for a true Romantic tutti
- Bass instruments (VC, CB, BN1, TBN1) should generally move in parallel on the bass line
- Inner voices (V2, VA, CL1) provide the harmonic glue -- keep them smooth and connected
