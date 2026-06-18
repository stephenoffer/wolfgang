# Prokofiev — Composition Guide

## Fingerprints
Any section claiming Prokofiev's style needs ≥3 of these 5 present.

1. **Tonal but "wrong" — the Prokofiev harmonic stab** — Prokofiev writes in keys, with melodies, with cadences — but constantly deploys harmonies that are deliberately, slightly "wrong": a D major chord where C major is expected, a C# in a G major context. These aren't mistakes — they are Prokofiev's defining harmonic language. The "wrong" chord doesn't destroy the tonality; it spikes it with unexpected sharpness, humor, or bite.
2. **Motoric, percussive drive — the Scythian energy** — Prokofiev's fast movements have a mechanical, relentless energy: even eighth notes, strong downbeats, minimal rubato, rhythmic precision as a value. The Scythian Suite and the Second Piano Concerto first movement are the extremes. This motoric quality is not emotional — it is kinetic. The music moves like a machine or an army, without sentiment.
3. **Lyrical melodic gift — the unexpected tenderness** — Beneath the percussive exterior, Prokofiev writes extraordinarily beautiful, simple, long melodies: the love theme from Romeo and Juliet, the second theme of the Classical Symphony, the slow movement of the Fifth Symphony. These melodies are genuinely beautiful — not ironic, not distorted. Prokofiev is not all Scythian energy; the tenderness is real.
4. **Grotesque and sardonic character** — A specific Prokofiev tone: not quite Shostakovich's political darkness, but a leering, slightly manic quality — music that grins too wide. The March from Love for Three Oranges, Visions Fugitives No. 4, Suggestion Diabolique. The music seems to be laughing at something unpleasant.
5. **Neo-Classical formal clarity** — Like Stravinsky but more melodic: Prokofiev uses Classical forms (sonata, rondo, variation) with tonal clarity, clear themes, and functional structure. The Classical Symphony (Symphony No. 1) is the paradigm: Haydn-style form with Prokofiev's harmonic language. The form is not ironic — it is genuinely Classical in architecture, just with 20th-century harmony.

## Pattern Directives

**"Wrong" harmony:**
- Write a phrase in C major.
- At bar 4, where C major or G major is expected: state D major or Eb major instead.
- The "wrong" chord is stated cleanly — no preparation, no apology. Then continue.
- The effect: a harmonic sneer, a slight shock that releases immediately.

**Motoric drive:**
- 4/4 or 2/4, fast (♩ = 120–180).
- All notes: equal eighth notes or quarter notes, no rubato.
- Bass: steady repeated notes or scale passage in equal values.
- NO expressive markings. The marking is "sempre forte e secco" (always loud and dry).
- Rhythmic precision is the expressive element.

**Lyricism:**
- Tempo: Andante or Moderato.
- Melody: long (16 bars), stepwise, with simple, beautiful harmonic support.
- The "wrong" chord: appears once or twice, very briefly, as color — not as disruption.
- The melody should feel like Prokofiev remembered how to be beautiful for a moment.

**Grotesque character:**
- Fast tempo, staccato, short phrases.
- Melody: descends with 7th intervals (wide, awkward) or leaps an augmented 4th.
- Accompaniment: jagged, angular, f.
- Dynamic: constant f or ff, occasional subito pp for a sinister effect.

## Anti-patterns (what sounds wrong)

- **Pure, uncomplicated Romanticism.** A Prokofiev passage with no harmonic "bite," no wrong note, no unexpected interval sounds like Rachmaninoff, not Prokofiev.
- **Atonal or serial writing.** Prokofiev is tonal throughout. He never goes fully atonal. If there's no key feeling, it's not Prokofiev.
- **Consistent emotional darkness.** Shostakovich carries constant darkness. Prokofiev alternates: grotesque/motoric sections AND genuinely beautiful slow sections. Unrelieved darkness misses his range.
- **Impressionistic vagueness.** Prokofiev's clarity is the opposite of Debussy's blur. Clear melodies, clear rhythms, clear harmonic centers — even when the harmony is "wrong."
- **Smooth legato fast passages.** Prokofiev's fast music is staccato, marcato, dry. Smooth legato in an Allegro Prokofiev passage sounds like Chopin.

## ShortScore Field Recommendations

**"Wrong" harmony:**
- Write the unexpected chord explicitly: D major in C major context = `["D3","F#3","A3"]`.
- `"_feel": "harmonic stab — D major where C major was expected. Prokofiev's bite."`.
- Duration: one beat or one bar maximum, then move on.

**Motoric passage:**
- `"art": "staccato"` or `"art": "marcato"` on every note.
- `"expr": "secco"` (dry) — no warmth, no rubato.
- Equal note values throughout: no dotted rhythms, no ties across barlines.

**Lyrical slow melody:**
- `"expr": "cantabile"` — the rare moment of Prokofiev warmth.
- Write the full arch of the melody explicitly, every note.
- Allow one "wrong" chord in the harmonization — it will sound Prokofievian.

**Dynamics:**
- Fast sections: `"dyn": "f"` to `"dyn": "ff"`, staccato.
- Slow sections: `"dyn": "p"` to `"dyn": "mf"`, legato.
- Grotesque sections: `"dyn": "ff"` with subito `"dyn": "pp"` moments.
