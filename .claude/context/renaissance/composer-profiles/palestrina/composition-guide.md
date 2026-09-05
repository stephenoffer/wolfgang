# Palestrina — Composition Guide

## Fingerprints
Any section claiming Palestrina's style needs ≥3 of these 5 present.

1. **The line recovers from every leap** — A leap is followed by stepwise motion in the opposite direction, filling the space it opened. Leaps larger than a sixth are rare, the octave is the practical limit, and two leaps in the same direction almost never happen. This single habit is most of what makes the surface sound like Palestrina rather than like counterpoint in general.
2. **Dissonance only ever passes, suspends or neighbours** — Every dissonance is approached by step from a consonance and left by step downward. The suspension is the expressive event of the style: prepared on a weak beat, struck on a strong one, resolved down. There is no unprepared dissonance anywhere and no dissonance that resolves upward or by leap.
3. **Arch-shaped phrases with a single high note** — A phrase rises to one peak and descends from it; the peak is touched once and not returned to. The whole span is usually a ninth or less. Repeating the climax pitch inside a phrase flattens the shape and is the commonest way this idiom is faked.
4. **Points of imitation with staggered, exposed entries** — Each phrase of text enters imitatively in every voice, and each entry is audible because the other voices have thinned or rested to let it through. Voices drop out in order to re-enter; a texture that never thins has no imitation in it, only simultaneity.
5. **Rhythmic independence over a steady tactus** — The pulse is even, but each voice carries its own accent from its own text, so downbeats rarely coincide across all voices. Suspensions and syncopations are what displace them. All voices agreeing on the metre at once is the sound of a machine, not a choir.

---

## What this style will not do

- Functional harmony. Chords are the vertical result of the lines; there is no goal-directed ii–V–I.
- A leading tone outside a cadence, other than as supplied musica ficta.
- Parallel fifths or octaves. Here the prohibition really is close to absolute — voice independence is the entire point of the texture.
- Notated dynamics or tempo marks. Neither existed; shape comes from register, entry and text.
- Instrumental figuration. Every line must be singable at sight by a person with breath.

## See also
- [../../renaissance-harmony.md](../../renaissance-harmony.md) — cadences, dissonance treatment, the modes, musica ficta
- [../../../general/counterpoint-essentials.md](../../../general/counterpoint-essentials.md)

---

## Composing a point of imitation: step by step

The unit is not the phrase, it is the **point of imitation** — one clause of
text, entering in every voice in turn. A motet is a chain of them. Everything
below is one point, in D Dorian, for four voices.

### Step 1 — Write the subject from the words

The subject is a setting of one clause, not an abstract theme. Its length is the
length of the clause spoken; its accents are the accents of the words. Arch
shape, one peak, and it recovers from any leap by step in the other direction.

```json
"subject": [
  {"p": "D4", "d": "w"},
  {"p": "A4", "d": "h"},
  {"p": "G4", "d": "h"},
  {"p": "F4", "d": "h"},
  {"p": "E4", "d": "h"},
  {"p": "D4", "d": "w"}
]
```

The rising fifth D4-A4 is the only leap; the line then walks back down through
the space it opened. The peak A4 is touched once. Range: a fifth. Give a subject
more than a ninth and it stops being singable at sight.

### Step 2 — Plan the entries before writing a second note

Entries alternate tonic and dominant — the *dux* on D, the *comes* on A — and
they are staggered so each one is exposed. Two breves apart is the working
default; closer is a stretto and belongs late, not at the opening.

| Voice | Enters at bar | On | Interval from the previous |
|-------|---------------|-----|----------------------------|
| Altus | 1 | A4 | — |
| Cantus | 3 | E5 | fifth above |
| Tenor | 5 | D4 | fifth below |
| Bassus | 7 | G3 | fifth below |

### Step 3 — Continue each voice freely once it has stated the subject

A voice that has finished the subject does not stop; it continues in free
counterpoint against the next entry, and it **thins or rests** so the incoming
entry can be heard. A texture that never thins has no imitation in it, only
simultaneity.

```json
"altus_continuation": [
  {"p": "D4", "d": "w"},
  {"p": "rest", "d": "h"},
  {"p": "F4", "d": "h"},
  {"p": "G4", "d": "h"},
  {"p": "A4", "d": "h"},
  {"p": "G4", "d": "w"}
]
```

The rest after the subject is not a gap. It is what makes the Cantus entry
audible, and rests of a half or whole breve between phrases are normal here.

### Step 4 — Put the suspension at the cadence

The suspension is the expressive event of the style. Prepared as a consonance on
a weak beat, struck as a dissonance on a strong one, resolved down by step. This
is the 7-6 into a Dorian clausula:

```json
"cantus_cadence": [
  {"p": "D5", "d": "h"},
  {"p": "C5", "d": "w", "tie": "start"},
  {"p": "C5", "d": "h", "tie": "stop"},
  {"p": "B4", "d": "h"},
  {"p": "A4", "d": "w"}
]
```

```json
"tenor_cadence": [
  {"p": "F4", "d": "h"},
  {"p": "E4", "d": "h"},
  {"p": "D4", "d": "w"},
  {"p": "C#4", "d": "h"},
  {"p": "D4", "d": "w"}
]
```

The C#4 is *musica ficta* — the leading tone is raised at the cadence and
nowhere else. Write it as an accidental, not into the key signature.

### Step 5 — Overlap into the next point before this one has closed

As the lower voices reach their cadence, one upper voice begins the next
subject. A cadence where all four voices arrive and stop together is an ENDING,
and a motet should have very few. The overlap is the technique that makes the
music continuous.

---

## Checking a finished point

- Does every leap larger than a third get answered by step in the other
  direction, in every voice?
- Is every dissonance either a passing tone on a weak beat, a neighbour, or a
  prepared suspension resolving down?
- Does each voice have one high note in the phrase, touched once?
- Did at least one voice rest before each new entry?
- Do all four voices ever agree on the downbeat? If they do throughout, the
  rhythmic independence is missing.
