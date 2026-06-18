# Stravinsky — Composition Guide

**CRITICAL: Stravinsky has THREE completely different aesthetics. Specify the period.**

## Russian Period (1910–1920) — Firebird, Petrushka, Rite of Spring, Pulcinella

### Fingerprints (Russian Period)
Any section claiming Russian-period Stravinsky needs ≥3 of these 5:

1. **Block juxtaposition** — Distinct musical blocks (each with its own tempo, texture, key, rhythm) are placed side-by-side without transition. The cut is abrupt, cinematic. The friction between juxtaposed blocks IS the formal structure. No development — only collision.
2. **Ostinato as hypnosis** — A short pattern (2–4 notes, simple rhythm) repeated obsessively for 8–32 bars while harmony gradually shifts underneath it, or a new layer is added above. The repetition doesn't bore — it hypnotizes through accumulation.
3. **Polytonality / polytonal harmony** — Two or more key areas sounding simultaneously. The Petrushka chord (C major + F# major simultaneously) is the paradigm. The two keys don't fight each other — they create a new, specific color neither could produce alone.
4. **Asymmetric, constantly changing meter** — Time signatures change every bar (5/8, 7/8, 3/8, 11/16). The "Rite of Spring" principle: the downbeat falls where the music needs it, not where the meter places it. The rhythm is primary; the meter follows.
5. **Pagan/folk rawness — unresolved dissonance** — Cluster chords, added dissonances (major 7ths, minor 9ths) left unresolved. The sound is deliberately rough, primitive, energetic. Smooth voice-leading is avoided. The "wrong" notes are intentionally wrong.

## Neo-Classical Period (1920–1951) — Symphony in C, Octet, Pulcinella (revision), Symphony of Psalms, Concerto in D

### Fingerprints (Neo-Classical Period)
Any section claiming Neo-Classical Stravinsky needs ≥3 of these 5:

1. **Tonal but displaced** — Diatonic melodies placed over deliberately "wrong" harmonies. A C major scale melody over an A major chord, or an F major phrase harmonized from D minor. The friction between clearly tonal melody and non-matching harmony is ironic, witty — beauty and wrongness simultaneously.
2. **Baroque formal containers, contemporary content** — Fugue, passacaglia, ritornello, chorale — Baroque/Classical forms used as containers for Stravinsky's modern rhythmic language. The form is historically correct; the accent displacement and metric irregularity are modern.
3. **Ostinato regularity (mechanical beauty)** — Repeated accompanying patterns, exactly repeated, providing a machine-like regularity against which the melody floats. Unlike Russian-period ostinato (hypnotic accumulation), Neo-Classical ostinato is a formal principle — the regular against which irregularity is measured.
4. **Dry, non-vibrato orchestral sound** — Staccato, marcato, no portamento, limited vibrato. The sound is dry, precise, slightly inhuman. Expressivity comes from line and structure, not from romantic instrumental warmth.
5. **Ironic quotation** — Historical material (Baroque gesture, operatic convention, Classical cadence formula) appears, correctly executed, but in an unexpected context — making the familiar strange and the conventional witty.

## Serial Period (1953–1971) — Agon, Threni, Requiem Canticles, The Rake's Progress (transitional)

### Fingerprints (Serial Period) — less commonly requested, brief overview
- Twelve-tone rows as melodic material, stated completely before repetition.
- Row transformations: retrograde, inversion, retrograde inversion.
- Stravinsky's serialism is austere and ritualistic, not expressionistic (unlike Schoenberg). Sparse textures, long silences, chant-like vocal writing.

---

---

## Note-Level Technique 1: The Petrushka Chord (Polytonal Superposition)

The Petrushka chord is C major + F# major sounding simultaneously — two triads a tritone apart, neither one "winning." Write both triads as a single simultaneous chord array. Every note belongs to one triad or the other; none belong to both. The sound: harsh, dissonant, yet not atonal — it has a specific color and identity.

**Petrushka chord in full, sustained then arpeggiated:**
```json
{"bar_num": 1, "_feel": "C major + F# major simultaneously — the tritone clash IS the Stravinsky sound", "voices": {
  "soprano": [
    {"p": ["C5","E5","G5","F#5","A#5","C#6"], "d": "h",  "dyn": "ff"},
    {"p": ["C5","E5","G5","F#5","A#5","C#6"], "d": "h"}
  ],
  "bass": [
    {"p": ["C3","E3","G3","F#3","A#3"],       "d": "w",  "dyn": "ff"}
  ]
}},
{"bar_num": 2, "_feel": "Arpeggiated — the two triads interleave", "voices": {
  "soprano": [
    {"p": "C5",  "d": "e"},
    {"p": "F#5", "d": "e"},
    {"p": "E5",  "d": "e"},
    {"p": "A#5", "d": "e"},
    {"p": "G5",  "d": "e"},
    {"p": "C#6", "d": "e"},
    {"p": "C5",  "d": "e"},
    {"p": "F#5", "d": "e"}
  ],
  "bass": [
    {"p": "C3",  "d": "h"},
    {"p": "F#2", "d": "h"}
  ]
}}
```
Bar 1: {C, E, G} (C major) + {F#, A#, C#} (F# major) as one chord — 6 notes total. Bar 2: the two triads interleave in alternation: C5, F#5, E5, A#5, G5, C#6 — the C-major notes and F#-major notes alternate. The result is a rapid coloristic shimmer. Bass: C3 (one root), F#2 (the other root) — the tritone in the bass is the structural anchor.

---

## Note-Level Technique 2: Ostinato Accumulation (Russian Period)

A 2-bar cell is established and repeated exactly. On the 4th (or 8th) repetition, a new melodic layer enters above the unchanged ostinato. The ostinato provides hypnotic stability; the new layer is the event.

**Bass ostinato (2-bar cell), repeated with new layers added:**
```json
{"bar_num": 1, "_feel": "Ostinato cell established — this pattern will repeat without change", "voices": {
  "vc": [
    {"p": "D2",  "d": "q",  "dyn": "mf", "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "F#2", "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "q",  "art": "staccato"}
  ]
}},
{"bar_num": 2, "voices": {
  "vc": [
    {"p": "E2",  "d": "q",  "art": "staccato"},
    {"p": "E2",  "d": "e",  "art": "staccato"},
    {"p": "E2",  "d": "e",  "art": "staccato"},
    {"p": "A2",  "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "q",  "art": "staccato"}
  ]
}},
{"bar_num": 3, "_feel": "Bars 3–4: exact repeat of ostinato — identical", "voices": {
  "vc": [
    {"p": "D2",  "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "F#2", "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "q",  "art": "staccato"}
  ]
}},
{"bar_num": 4, "voices": {
  "vc": [
    {"p": "E2",  "d": "q",  "art": "staccato"},
    {"p": "E2",  "d": "e",  "art": "staccato"},
    {"p": "E2",  "d": "e",  "art": "staccato"},
    {"p": "A2",  "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "q",  "art": "staccato"}
  ]
}},
{"bar_num": 5, "_feel": "New layer enters above unchanged ostinato — the EVENT after 4 bars of repetition", "voices": {
  "fl": [
    {"p": "A5",  "d": "h",  "dyn": "f"},
    {"p": "G5",  "d": "q"},
    {"p": "F#5", "d": "q"}
  ],
  "vc": [
    {"p": "D2",  "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "D2",  "d": "e",  "art": "staccato"},
    {"p": "F#2", "d": "q",  "art": "staccato"},
    {"p": "D2",  "d": "q",  "art": "staccato"}
  ]
}}
```
Bars 1–4: vc ostinato, exact repeat twice. Bar 5: fl melody enters above — the ostinato is UNCHANGED. The fl entry is the structural event; it arrives because the repetition has made it expected. The listener's attention is primed by repetition to hear the new layer when it arrives. Continue the ostinato for 8–12 more bars; add another layer at bar 8 or 12.

---

## Note-Level Technique 3: Changing Meter (Rite of Spring Principle)

Time signatures change every bar, driven by the accent needs of the material. The accent determines the bar length; the bar length is not imposed. A bar of 5/8 means: this group of notes has 5 eighth-note values before the next accent. Not "five beats."

**3-bar sequence of changing meter (D major pentatonic melody):**
```json
{"bar_num": 1, "_feel": "5/8 — five eighths before the next accent impulse", "voices": {
  "vln1": [
    {"p": "D5",  "d": "e",  "dyn": "f",  "art": "marcato"},
    {"p": "E5",  "d": "e"},
    {"p": "F#5", "d": "e"},
    {"p": "A5",  "d": "e"},
    {"p": "G5",  "d": "e"}
  ],
  "cb": [{"p": "D2", "d": "q"}, {"p": "D2", "d": "dq"}]
}},
{"bar_num": 2, "_feel": "3/8 — the accent arrives sooner than expected. Jolt.", "voices": {
  "vln1": [
    {"p": "F#5", "d": "e",  "dyn": "ff", "art": "sfz"},
    {"p": "E5",  "d": "e"},
    {"p": "D5",  "d": "e"}
  ],
  "cb": [{"p": "A2", "d": "dq"}]
}},
{"bar_num": 3, "_feel": "7/8 — longer than expected. The motion continues without expected resolution.", "voices": {
  "vln1": [
    {"p": "E5",  "d": "e",  "art": "marcato"},
    {"p": "D5",  "d": "e"},
    {"p": "A4",  "d": "e",  "dyn": "mf"},
    {"p": "F#4", "d": "e"},
    {"p": "D4",  "d": "e"},
    {"p": "E4",  "d": "e"},
    {"p": "F#4", "d": "e"}
  ],
  "cb": [{"p": "D2", "d": "q"}, {"p": "A2", "d": "q"}, {"p": "D2", "d": "dq"}]
}}
```
Bar 1 (5/8): e+e+e+e+e = 5/8 ✓. Bar 2 (3/8): e+e+e = 3/8 ✓. Bar 3 (7/8): e×7 = 7/8 ✓. The time signatures are DERIVED from the accent pattern — the accent fell on bar 1 beat 1, bar 2 beat 1 (which arrived 5 eighths later), bar 3 beat 1 (3 eighths after bar 2). Each sfz/marcato marking IS the bar line. Mark every changing time signature explicitly in the WMN metadata or as a `"_time_sig"` field per measure if the format supports it.

---

## Pattern Directives (Russian Period)

**Block structure:**
- Identify 2–3 distinct musical blocks with different character (slow ostinato | fast dance | lyrical solo).
- Place them in sequence without transition — hard cut between bars.
- Return blocks can be exact repetitions (Stravinsky doesn't develop — he juxtaposes).

**Ostinato writing:**
- Write a 2-bar pattern, repeat it exactly 8 times.
- On the 4th and 8th repetitions, add a new melodic layer above the ostinato (woodwind color).
- The ostinato remains unchanged; the additions accumulate.

**Irregular meter:**
- Accent placement determines bar line, not the other way around.
- Typical Rite of Spring passage: |♩♩♩♩♩| |♩♩♩| |♩♩♩♩♩♩| |♩♩♩♩| — a "melody" of 5+3+6+4 eighth notes as bars.

## Pattern Directives (Neo-Classical Period)

**Tonal but wrong:**
- Write the melody in a clear key (C major scale). Then harmonize it with chords from a different but related key (A minor or G major). The melody should be recognizably "in" the new harmonization but not "correctly" harmonized.
- The bass line is the most important element — it determines the "wrong" harmonic context.

**Baroque container:**
- Fugue subject stated in one voice; answer in another voice a fifth above/below.
- But use Stravinsky's rhythmic displacement — the subject's accent doesn't fall on the downbeat of each measure.

## Anti-patterns

**Russian period:**
- **Smooth transitions.** No transition, no preparation. Blocks are cut.
- **Development.** Stravinsky doesn't develop motivically. He juxtaposes, accumulates, returns.
- **Romantic expression.** The Rite of Spring is not expressive in the Romantic sense — it's ritualistic, relentless, impersonal.

**Neo-Classical:**
- **Complete harmonic correctness.** Neo-Classical Stravinsky is intentionally, ironically "wrong." Perfect functional harmony with no dissonance is Haydn, not Neo-Classical Stravinsky.
- **Romantic orchestral warmth.** Dry and precise is the sound. Vibrato and portamento are wrong.

## ShortScore Field Recommendations

**Russian period:**
- Write each block as a separate section with distinct tempo, meter, and instrumentation.
- Ostinato: write 4 bars of pattern, then mark to continue while new layers are added above.
- Meter: specify time signature changes bar-by-bar.

**Neo-Classical:**
- Bass line first (it determines the "wrong" harmonic context).
- Melody: diatonic and clear.
- Staccato and marcato articulations throughout (`"art": "staccato"`, `"art": "marcato"`).

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #18: Whole-Tone Passage — used in Stravinsky's atmospheric transitions (rare but present)
- Technique #14: Pentatonic Melody — the folk cell source for Russian-period melodic writing
- Technique #15: Dorian Mode phrase — modal folk writing in Russian and Neo-Classical periods
- Technique #17: Parallel Chord Movement — Neo-Classical Stravinsky uses this for ironic harmonic stasis
