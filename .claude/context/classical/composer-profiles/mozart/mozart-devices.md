# Mozart Idiomatic Device Catalog (RH, structure, density)

Companion to `mozart-lh-vocabulary.md` (left-hand idioms). These are the
specific behaviors that make a line/section sound like Mozart rather than
generic tonal music. Weave several in per phrase — but always in service
of the phrase's character, never as a checklist.

## Melodic / right-hand devices

1. **Parallel thirds & sixths** — the signature Mozart sweetness for
   lyrical themes. Double the melody a 3rd or 6th below in the same rhythm:
   `[F5,A5]q [E5,G5]e [D5,F5]e ...`. Use across lyrical second themes and
   consoling passages. Don't overuse in stormy material.
2. **Appoggiatura "sigh"** — a dissonance ON the strong beat resolving DOWN
   by step on the weak beat, slurred two-note: `(G5q F5q)` over an F chord
   (the G leans, the F resolves). The emotional core of Mozart's minor-key
   writing. Place at phrase peaks and cadential approaches.
3. **Cadential trill** — a trill on scale-degree 2 (or the dominant note)
   approaching a PAC, ideally with a turned suffix: `A5h:tr` then resolve to
   the tonic. Reserve for real cadences (PAC, important HC), not every bar.
4. **Turns & mordents** — a gruppetto (turn) wrapping a sustained melody
   note `:turn`, a mordent `:mord` on an accented note. Ornament arrivals
   and long notes, not running passages.
5. **Grace-note appoggiatura** — a short `:grace` note leaning into a strong
   beat from a step above. Adds vocal inflection at phrase starts/peaks.
6. **Echo dynamics (terraced repetition)** — state a 1-2 bar idea `f`, then
   immediately repeat it (often an octave up or same register) `p`. A
   quintessential Mozart/Classical gesture. Great for presentation phrases
   and codettas. Mark the dynamics explicitly.
7. **Triplet contrast** — break prevailing duple (eighths/sixteenths) with a
   bar or two of triplet figuration for rhythmic variety and forward lilt.
8. **Scale flourish as punctuation** — a fast run is connective/cadential
   tissue, used ONCE to drive into an arrival — not the default surface.
   If a phrase is >55% stepwise, replace some runs with arpeggios/leaps.
9. **Leap-to-peak then step-down** — approach a registral apex by leap
   (6th, octave, arpeggio), then release it by step. Gives the line a
   profile and a clear high point.

## Structural / harmonic behaviors

10. **Periodic structure** — antecedent (4 bars, ends on a HC, "question")
    + consequent (4 bars, begins like the antecedent, ends PAC, "answer").
    Make the consequent's opening RECOGNIZABLY echo the antecedent.
11. **Sentence structure** — presentation (a 2-bar basic idea + its
    repetition, often sequenced up a step or varied) → continuation
    (fragment the idea, accelerate harmonic rhythm) → cadence. Mozart's
    primary themes are often sentences.
12. **Deceptive feint** — approach the cadence, then resolve V→vi instead of
    V→I once, before finally landing the real PAC. Adds a moment of surprise.
13. **Cadential 6/4** — at important cadences: I6/4 → V(7) → I. Lean the 6/4
    on a strong beat (it's a dominant-function suspension).
14. **Feminine cadence** — resolve the final tonic on a WEAK beat (e.g. beat
    2), often after an appoggiatura. Gentler than a downbeat slam; very
    Mozart for lyrical endings.
15. **Neapolitan (bII6)** — in minor, a flat-supertonic-sixth chord for a
    dark expressive stab before the dominant. Let it land (fp, slight hold).

## Density ebb-and-flow (the breathing the metrics measure)

Real Mozart constantly alternates BUSY bars and SPARSE bars. A piece where
every bar has the same note-count sounds mechanical even with varied idioms.

- **Thin the phrase openings and the comma (antecedent end).** A bar can be
  as sparse as a held melody note + a single LH chord (3-5 events total).
- **Flare the cadential approach.** Let the bar before a PAC bristle with a
  run or arpeggiated sixteenths (14-18 events), then resolve.
- **Aim for real contrast across each 4-bar unit**: e.g. sparse–medium–
  busy–cadence, not four equal note-walls.
- **Texture drop-outs**: occasionally let the melody sound ALONE (LH rests),
  or the LH alone answer (RH rests). Silence and exposure are expressive.
- A deliberately sparse bar may trip the density floor — waive
  `density_low_lh`/`density_low_rh` with an honest reason
  (`allow=[{'check':..., 'reason':'cadential breath / texture drop-out'}]`).
  Do NOT re-thicken a bar that is meant to breathe.

## Per-function quick guide

- **Primary theme (storm, D minor)**: sentence structure; bare unison head
  + churning continuation; murky/broken octaves; echo dynamics; cadential
  trill into the HC; density contrast between statement and drive.
- **Transition**: circle-of-fifths or sequential drive; walking/murky bass;
  one scale flourish to the medial caesura; big density swell then a break.
- **Lyrical second theme**: parallel thirds/sixths; appoggiatura sighs;
  light oom-pah/Alberti; turns at arrivals; echo dynamics; feminine cadence;
  the SPARSEST textures in the piece.
- **Development**: motivic fragmentation; sequences; diminished 7ths;
  dominant pedal retransition; the dynamic + registral climax.
- **Recapitulation**: as the exposition but second theme in the tonic
  (minor here = darkened); can enrich the LH with counterpoint (varied
  recap); Neapolitan + cadential 6/4 into the final PAC.
- **Coda/closing**: confirmation gestures, brilliant flourishes, echo,
  emphatic cadential trill, octave unison for the final stamp.
