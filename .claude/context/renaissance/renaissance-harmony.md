# Renaissance Harmony Reference

> **Why this file exists.** `style_registry` declares a `renaissance` style with
> two *armed* composers (Palestrina, Monteverdi), `compiled_packs/style__renaissance/`
> holds their corpus profiles, and there was no `.claude/context/renaissance/`
> directory at all. So both composers compiled to an **empty `cadence_scripts.json`**,
> and every fallback that resolves a genre — the shared-harmony layer, the
> texture-transition matrix — silently handed Renaissance polyphony *Classical*
> data. Modal counterpoint judged by Classical norms is not a small error.

Renaissance harmony is a **consequence of voice-leading**, not a progression of
chords. There is no functional dominant, no chord "resolving" because of its
root; there are independent lines meeting in consonance and parting through
prepared dissonance. Write the lines, and the harmony happens. Approaching it
the other way round — picking chords and filling voices in — produces the one
thing this idiom cannot survive, which is homophony wearing polyphonic clothes.

## Cadence Types

The cadence is where the modal system is most audible, and where a generated
piece most often gives itself away by reaching for V-I.

| Cadence | Progression | Context | Notes |
|---------|------------|---------|-------|
| Clausula vera | 6-8 or 3-1, two voices step in contrary motion to the octave | The fundamental cadence of the style | Upper voice rises by semitone, lower falls by tone |
| Authentic (perfect) | V-I with the leading tone raised | Final cadence of a section or piece | Musica ficta supplies the leading tone in modes that lack it |
| Phrygian | bII6-I, the bass falling a semitone | Endings in the Phrygian mode | No leading tone; the semitone is in the *bass*, not the top |
| Plagal | IV-I | "Amen"; final extension after the true cadence | Very common as an added close after a clausula vera |
| Evaded | The expected cadence note is not taken | Keeps a long polyphonic span moving | One voice rests or leaps away at the moment of arrival |
| Landini | Sixth degree interposed before the octave (7-6-8) | Older, more common early in the period | A written-out escape tone in the upper voice |
| Double leading-tone | Two voices approach by semitone | Archaic; late-medieval survival | Reserve for deliberate archaism |

**Picardy third.** A piece in a minor mode ends on a major triad. This is the
convention, not an exception.

## Dissonance Treatment

Dissonance is *prepared, struck, and resolved downward by step*. That is close
to the whole of it, and it is the rule most worth obeying literally, because it
is what makes the style sound like itself.

| Device | How it works | Where |
|---|---|---|
| Suspension | Consonant preparation, tied over the barline, dissonant on the strong beat, resolves down by step | The principal expressive device — 4-3, 7-6, 9-8, and 2-3 in the bass |
| Passing tone | Dissonant, stepwise, on the weak part of the beat | Everywhere |
| Neighbor tone | Steps away and back, weak beat | Everywhere |
| Cambiata | Down a step, down a third, up a step | A stock melodic formula, not a free choice |
| Anticipation | The resolution arrives early, weak beat | At cadences |
| Escape tone | Leaves the line by step, resolves by leap | Sparing |

Everything else is a consonance: unison, octave, fifth, third and sixth. The
fourth is a dissonance against the bass and a consonance between upper voices —
a distinction that matters constantly in four-voice writing.

## Modal Practice

The modes are not scales with different starting notes; each has its own
*final*, *reciting tone*, and cadence hierarchy, and a piece establishes its
mode by which degrees it cadences on.

| Mode | Final | Reciting tone | Character | Secondary cadence degrees |
|---|---|---|---|---|
| Dorian | D | A | Grave, flexible — the most-used mode | A, F |
| Phrygian | E | C | Severe; its half-step above the final gives the Phrygian cadence | A, C |
| Lydian | F | C | Bright; B is almost always flattened in practice | A, C |
| Mixolydian | G | D | Open, plain; no leading tone unless supplied | C, D |
| Aeolian | A | E | Added late; closest to modern minor | C, E |
| Ionian | C | G | Added late; closest to modern major | E, G |

**Musica ficta.** Accidentals were largely unwritten and supplied by the
performer: raise the seventh at a cadence, flatten B against F to avoid the
tritone, raise a note to avoid an augmented interval in a line. When writing in
this style, write the ficta *in* — the notation convention is historical, the
sound is not optional.

## Texture

| Device | What it is | Use |
|---|---|---|
| Points of imitation | Each phrase of text enters imitatively in every voice, overlapping | The structural unit of a motet or mass movement |
| Paired imitation | Two voices present the subject, then the other two answer | Gives a large texture internal articulation |
| Homorhythmic declamation | All voices move together on the text | For emphasis — a sudden clarity after polyphony |
| Voice pairing | Upper two against lower two, antiphonally | Colour and relief within a full texture |
| Full texture | All voices sounding | Reserve it; constant tutti has nowhere to grow |

Rests are structural, not decorative: a voice drops out so it can *re-enter*,
and a point of imitation is only audible because the entries are exposed. A
Renaissance texture that never thins is the same defect as a Classical one that
never thickens.

## What to avoid in this idiom

- **Functional progressions.** ii-V-I as a *goal-directed* gesture is anachronistic.
- **A leading tone where the mode has none**, other than at a cadence via ficta.
- **Unprepared dissonance**, and any dissonance that resolves upward or by leap.
- **Parallel fifths and octaves** — here this really is close to absolute; the
  whole point of the texture is voice independence.
- **Dynamics and tempo marks.** Neither was notated. The shape comes from the
  text, the entries and the register. (`expression_enricher`'s `renaissance`
  profile already suppresses hairpins, terracing and pedal for this reason.)
- **Bar-line thinking.** The tactus is steady, but each voice carries its own
  accent from its own text; strong-beat regularity across all voices at once is
  the sound of a machine, not a choir.

## See also

- [../general/counterpoint-essentials.md](../general/counterpoint-essentials.md) — species counterpoint, motion types, forbidden parallels
- [../general/human-sounding-music.md](../general/human-sounding-music.md) — the measured human/AI tells
