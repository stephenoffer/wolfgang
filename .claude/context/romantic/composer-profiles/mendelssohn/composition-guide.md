# Mendelssohn — Composition Guide

## Fingerprints
Any section claiming Mendelssohn's style needs ≥3 of these 5 present.

1. **Scherzo lightness — the fleet, elfin texture** — Mendelssohn invented a specific sound: fast (Presto or Vivace), pp or ppp, staccato, very high register, strings playing sul ponticello or without vibrato, like fireflies or fairy wings. This texture appears in the Midsummer Night's Dream Scherzo and pervades his fast movements. It is weightless, delicate, and technically demanding.
2. **Singing tone — bel canto melody in instruments** — Mendelssohn's slow melodies are modeled on Italian bel canto: long, arching phrases, beautifully shaped, without extremes of dissonance or angst. The melody is always lovely. This is not a limitation — it is a conscious aesthetic: beauty as truth.
3. **Formal clarity with Romantic content** — Mendelssohn inhabits Classical forms (sonata, rondo, variation) with complete conviction, without irony. His development sections actually develop. His recapitulations feel like returns. The form is not a container — it is the content.
4. **Venetian barcarolle lilt** — In 6/8 or 12/8, a gentle rocking accompaniment (bass-chord-chord in the left hand, or pizzicato lower strings with sustained upper strings) suggesting water motion. The "Songs Without Words" barcarolles define this texture: peaceful, nostalgic, effortless.
5. **Bright, unclouded orchestration — the Protestant clarity** — Mendelssohn's orchestration is transparent: each instrument section audible, no muddy doublings, brass used for weight not color, strings predominant. Even his fortissimos are clear, not thick. This is not Romantic orchestral mass — it is Baroque-influenced clarity in Romantic clothing.

## Pattern Directives

**Elfin scherzo:**
- Tempo: as fast as possible. Time: 2/4 or 3/8.
- All notes: staccato. Dynamic: pp throughout (only brief f moments at structural points).
- Melody: high register (violin 1 above D5, or flute, or piano right hand above C5).
- Accompaniment: only on the beat, pizzicato or very light.
- No sustained notes. Everything darts and disappears.

**Bel canto melody:**
- 16-bar phrase in two arching 8-bar halves.
- First half: ascent to the peak (a 6th above the start).
- Second half: decorated descent, ending with a cadential trill or turn.
- No dissonances longer than a beat. The melody is always "at home" harmonically.

**Barcarolle:**
- 6/8 time. LH: bass note on beat 1, chord on beat 2 (beat = dotted-quarter in 6/8).
- The bass moves by 3rds and 5ths — never walking chromatic bass.
- Melody: begins on the 3rd eighth note of the measure (the "feminine" pickup to the next beat).
- Dynamic: mp with gentle swell to mf at the 8-bar peak.

**Bright orchestration:**
- Strings: primary carrier of all melodic content.
- Woodwinds: doubling melody at the octave, or sustained harmony.
- Brass: only for structural arrivals (the downbeat of the recapitulation, final cadence).
- Never muddy doublings: bass instruments only when needed for harmonic bass.

## Anti-patterns (what sounds wrong)

- **Darkness, angst, or existential struggle.** Mendelssohn is not Schumann or Brahms. His minor-key music is expressive but not anguished. A Mendelssohn movement that wallows in darkness has lost his essential character.
- **Harmonic ambiguity or wandering.** Mendelssohn's harmony is clear and functional. He doesn't wander like Schubert or evade like Brahms. The harmony supports the form, moves when it needs to, and arrives cleanly.
- **Heavy, massive orchestration.** Mendelssohn's orchestra is never heavy. Thick brass doublings, sustained cluster-like harmonies, dense string writing — none of these belong here.
- **Rhythmic irregularity.** Mendelssohn's rhythms are regular and song-like. Syncopation and metric irregularity are rare. The phrase lengths are almost always 4 or 8 bars.
- **Irony or modernism.** Mendelssohn is sincere, not ironic. His use of Classical forms is genuine, not nostalgic or deconstructive. He means it.

## ShortScore Field Recommendations

**Scherzo texture:**
- All notes: `"art": "staccato"`.
- `"dyn": "pp"` throughout; `"dyn": "p"` maximum except at structural points.
- Fast tempo marking: `"tempo": 176` or faster.
- Melody: write every note explicitly in high register.

**Barcarolle bass:**
- `lh`: `{"p": "C2", "d": "q."}` (beat 1), `{"p": "E3G3", "d": "q."}` (beat 2 chord).
- In 6/8, each dotted-quarter = one group of three eighth notes.

**Singing melody:**
- `"expr": "cantabile"` — always on melodic sections.
- Melody written note-by-note with tenuto on longer values.
- Ornaments: only at cadential points — a short trill or mordent at the penultimate bar.

**Dynamics:**
- Mendelssohn's range: pp to ff, but most music lives between p and f.
- `"expr": "leggiero"` (light) for fast passages.
- `"expr": "con fuoco"` (with fire) only at final climax, not maintained.

---

## Composing a Mendelssohn phrase: step by step

The organising fact is **Classical proportion carrying Romantic warmth**. The
harmony is Romantic; the phrase structure is Mozart's. Generated "Romantic
piano" usually loses the squareness, and losing it is losing him.

### Step 1 — Write a singing melody in a strict four-bar frame

Song without words: the tune must be playable by one hand and singable by one
voice, with an accompaniment that never competes.

```json
"song_melody": [
  {"p": "E5", "d": "q", "dyn": "p", "art": "legato"},
  {"p": "F#5", "d": "e"},
  {"p": "G5", "d": "e"},
  {"p": "A5", "d": "h"},
  {"p": "G5", "d": "q"},
  {"p": "F#5", "d": "q"},
  {"p": "E5", "d": "h"}
]
```

### Step 2 — Put a murmuring inner voice between the hands

His signature texture: the melody on top, the bass below, and a quiet repeated
figure in the middle played between the two. Neither hand owns it.

```json
"inner_murmur": [
  {"p": "B3", "d": "e"},
  {"p": "E4", "d": "e"},
  {"p": "B3", "d": "e"},
  {"p": "E4", "d": "e"},
  {"p": "B3", "d": "e"},
  {"p": "E4", "d": "e"}
]
```

### Step 3 — Keep the bass simple and slow

One note a bar, or two. The interest is the middle voice, and a busy bass turns
the texture muddy.

```json
"slow_bass": [
  {"p": "E2", "d": "h"},
  {"p": "B2", "d": "h"}
]
```

### Step 4 — For a scherzo, halve every value and lighten every touch

The elfin scherzo is the other Mendelssohn: staccato, pianissimo, fast, and
almost entirely stepwise so it can be played at speed.

```json
"elfin_scherzo": [
  {"p": "G5", "d": "s", "dyn": "pp", "art": "staccato"},
  {"p": "A5", "d": "s"},
  {"p": "B5", "d": "s"},
  {"p": "C6", "d": "s"},
  {"p": "B5", "d": "s"},
  {"p": "A5", "d": "s"},
  {"p": "G5", "d": "s"},
  {"p": "F#5", "d": "s"}
]
```

### Step 5 — Cadence properly and on time

He does not evade. The four-bar unit closes where it said it would.

---

## Checking a finished phrase

- Is the phrase four bars, or eight?
- Is there a voice between the hands, or only melody and bass?
- Could the tune be sung?
- In a scherzo, is anything marked louder than `p`? It should not be.
