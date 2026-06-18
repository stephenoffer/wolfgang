# Smetana — Composition Guide

## Fingerprints
Any section claiming Smetana's style needs ≥3 of these 5 present.

1. **Czech dance idiom — Polka and Furiant** — The Polka is a fast 2/4 Bohemian couple dance with characteristic dotted rhythm (♩. ♪ ♩.) and strong downbeats. Smetana brought the polka into art music with complete conviction — it is not a "national color" decoration, it IS the structural material. The Furiant (shared with Dvořák) combines 3/4 and 2/4 rhythms in hemiola.
2. **Vltava/landscape program — the tone poem tradition** — Má vlast (My Homeland) is the paradigm: music that represents specific Czech landscapes, legends, and places. The water surface of the Vltava river, the Bohemian forests, Vyšehrad castle — Smetana describes these through specific musical techniques (string tremolo for rippling water, fanfare for castles, folk melody for villages).
3. **Folk melody as structural theme** — Smetana's main themes often sound folk-like: singable, diatonic, with the character of Czech village music. But unlike Dvořák, Smetana frequently uses real Czech folk tunes as his thematic material (especially in Má vlast).
4. **Clear, Classical formal logic** — Despite nationalistic content, Smetana's musical language is rooted in Germanic Classicism (he studied with Liszt's influence, was inspired by Schumann). His forms are clear: sonata structure with identifiable themes, development, recapitulation. The "Czech" quality is in the themes and dance idioms, not in the formal structure.
5. **Idyllic vs. heroic contrast** — Smetana alternates between two emotional worlds: the pastoral/idyllic (the Bohemian countryside, village life, gentle rippling water) and the heroic/epic (Vyšehrad, Libuše, the Hussite legacy). The contrast between these two worlds IS the dramatic arc of Má vlast and much of his other music.

## Pattern Directives

**Polka rhythm:**
- 2/4, fast (♩ = 120–160).
- Bar 1: ♩. ♪ | ♩ (dotted-eighth + sixteenth + quarter) — the polka "hop."
- Beat 1: strong accent (the hop). Beat 2: light.
- Bass: simple quarter-note tonic-dominant or waltz-bass pattern.
- Character: bright, cheerful, vigorous — never refined or delicate.

**Vltava water texture:**
- Strings: rapid arpeggiated figuration (sixteenth-note sextuplets or eighth-note triplets) in a rocking pattern.
- The figuration rocks between two pitches (E and B, or similar open-5th interval) simulating water surface.
- Above: a folk-like melody in the winds (flute or oboe).
- Dynamic: begins pp, builds gradually as the river "grows."

**Folk melody:**
- Diatonic, major key, stepwise with occasional 3rd or 4th leaps.
- 8 bars: 4 bars question + 4 bars answer.
- Rhythm: simple quarter and half notes. No complex subdivisions.
- Harmonization: I-IV-V-I. The simplicity supports the folk character.

**Heroic/epic texture:**
- Brass fanfare: dotted rhythms, P4 and P5 intervals, forte to fortissimo.
- Full orchestra: strings in rhythmic octaves, timpani reinforcing the beat.
- Harmonic rhythm: slow (one chord per bar), stable tonic or dominant pedal.

## Anti-patterns (what sounds wrong)

- **Abstract, non-programmatic writing.** Smetana's orchestral music is almost always about something specific. Abstract formal music is more characteristic of Brahms.
- **Complex chromatic harmony.** Smetana's language is clear and tonal. Wagner-style chromaticism is not his territory.
- **Refined, aristocratic character.** Even the "beautiful" passages in Smetana have a folk directness. Sophisticated elegance belongs to Mendelssohn, not Smetana.
- **Absence of Czech dance rhythm.** At least one section should have identifiable Czech dance character (polka or furiant rhythm). Without this, the "Czech" quality disappears.

## ShortScore Field Recommendations

**Polka:**
- `"time_sig": "2/4"`, `"tempo": 132`.
- Melody: `{"p": "C5", "d": "qd"}`, `{"p": "D5", "d": "e"}`, `{"p": "E5", "d": "q"}` — dotted-note rhythm.
- `"art": "marcato"` on all beat-1 notes.
- `"expr": "vivace"`.

**Water texture:**
- `vln1`/`vln2`: rapid ascending/descending arpeggiated figure, pp.
- Write out the first full measure explicitly; use the pattern consistently.
- `"_feel": "Vltava — the river surface, rippling, pp"`.

**Heroic fanfare:**
- `tpt`: dotted-note fanfare figure, ff, P4 and P5 intervals.
- `timp`: reinforcing beat 1 of each bar.
- `"expr": "grandioso"`.
