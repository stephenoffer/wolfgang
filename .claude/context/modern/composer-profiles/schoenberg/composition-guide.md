# Schoenberg — Composition Guide

**CRITICAL: Schoenberg has THREE completely different aesthetic periods. Specify which.**

## Period 1: Late Romantic (1899–1908) — Verklärte Nacht, Gurrelieder, Pelleas und Melisande

### Fingerprints (Late Romantic Period)
Any section claiming this Schoenberg needs ≥3 of these 5:

1. **Post-Wagnerian chromaticism at the breaking point** — Schoenberg takes Wagner's chromatic language and pushes it further: longer stretches of harmonic ambiguity, more complex chromatic voice-leading, more deferred resolution. The tonality is still present but increasingly difficult to locate.
2. **Extreme emotional intensity — Expressionist temperature** — The late Romantic Schoenberg is emotionally overwrought by intention: enormous dynamic swings, extreme registers, intense dissonances. The emotion of the Verkärte Nacht string sextet is real and unironic.
3. **Brahmsian thematic development** — Despite the Wagnerian harmony, Schoenberg develops his themes in the Brahms manner: motivic cells transformed, fragmented, recombined. This is a specific hybrid.
4. **Large late-Romantic orchestra** — Enormous orchestral forces (Gurrelieder requires 5 soloists, 3 male choruses, 1 mixed chorus, speaker, and large orchestra).
5. **Still has a tonal center** — Despite the chromatic intensity, these works always have a key. The tonal center may be distant or delayed, but it exists.

## Period 2: Atonal / Expressionist (1908–1923) — Three Piano Pieces Op.11, Pierrot Lunaire, Five Orchestral Pieces

### Fingerprints (Atonal Period)
Any section claiming this Schoenberg needs ≥3 of these 5:

1. **Free atonality — no key, no tonal center** — No pitch is privileged over any other. There is no tonic, no dominant, no functional harmony. Dissonances are not prepared and do not resolve. Every harmonic event is equally valid or invalid.
2. **Sprechstimme (speech-song)** — In Pierrot Lunaire: a notation that is between speech and song. The written pitch is only an approximation — the performer rises toward the notated pitch and immediately falls away. It is neither speaking nor singing — it is the voice in extremis.
3. **Very short, compressed forms** — The Five Orchestral Pieces Op. 16 are very short (some under 2 minutes). The atonal language can't sustain tonal forms (sonata, etc.) — it requires new, compressed shapes.
4. **Pointillistic texture** — Individual notes in isolated instruments, sparse texture, extreme register leaps. The melodic line is fragmented across instruments.
5. **Expressionist psychological state** — Atonal Schoenberg is Expressionist: the music represents extreme psychological states (Erwartung is a monodrama of a woman who may or may not have murdered her lover). Unresolved tension is the aesthetic.

## Period 3: Twelve-Tone (Dodecaphonic) (1923–1951) — Piano Suite Op.25, Violin Concerto, Piano Concerto, String Quartet No.4

### Fingerprints (Twelve-Tone Period)
Any section claiming this Schoenberg needs ≥3 of these 5:

1. **Twelve-tone row stated before repetition** — The row (all 12 chromatic pitches in a specific order) is the primary material. No pitch repeats until all 12 have been stated. The row can appear as melody, as harmony (pitches stacked), or as accompaniment.
2. **Row transformations** — The row appears in four forms: Original (P), Retrograde (R — same row backwards), Inversion (I — all intervals inverted), Retrograde Inversion (RI — inverted backwards). All 48 versions of the row (12 transpositions × 4 forms) are potentially available.
3. **Neo-Classical forms re-inhabited** — Paradoxically, the twelve-tone Schoenberg often uses Classical forms: the Piano Suite Op.25 uses dance suite movements (Gavotte, Musette, etc.). The serial organization replaces harmonic organization, but the formal shapes are traditional.
4. **Non-repetition of pitch classes** — Before all 12 chromatic pitches have sounded, no pitch can be reused. This is the fundamental rule: the row is the constraint that prevents anything from sounding "tonal."
5. **Motivic work within the row** — Schoenberg doesn't just state rows — he finds motifs within them and develops these. The serial technique and the motivic development are simultaneous.

## Pattern Directives (Twelve-Tone — most commonly requested)

**Writing a twelve-tone row:**
- Choose 12 pitches in an order that has musical interest: specific intervals between adjacent notes, characteristic shapes within sub-groups.
- Good row: distinctive opening interval (minor 9th), followed by a recognizable pattern.
- Example row: C-F#-Bb-D-Eb-G-Ab-E-B-A-F-Db (every interval different).

**Row harmonization:**
- Divide the row into three groups of 4 pitches.
- State group 1 as a vertical chord (all four notes simultaneously).
- State group 2 as a melodic line.
- State group 3 as an accompaniment figure.
- All 12 pitches sounded before any returns.

**Inversion:**
- Original interval: ascending P5 (C→G). Inverted: descending P5 (C→F).
- Apply to each interval in the row to generate the I form.

## Anti-patterns

**Late Romantic:**
- **Writing free atonality when Late Romantic is specified.** Late Romantic Schoenberg is tonal, even if barely. No key = wrong period.

**Atonal:**
- **Functional harmony.** Any V→I resolution, any leading-tone resolution, any predictable harmonic motion — these are wrong.
- **Long-form traditional structures.** Atonal Schoenberg uses short, compressed forms.

**Twelve-Tone:**
- **Repeating a pitch before completing the row.** The rule is absolute in the strict twelve-tone system.
- **Using the row as just a melody.** The row must generate all material: melody, harmony, bass, accompaniment.

## ShortScore Field Recommendations

**Twelve-tone row header:**
- Define the row at the top of the JSON: `"_row": "C-F#-Bb-D-Eb-G-Ab-E-B-A-F-Db"`.
- Each measure: annotate which row form and transposition is in use.
- `"_feel": "P0 (original row) — pitches C through Db in order"`.

**Atonal texture:**
- Individual notes in isolated instrument voices: pointillistic.
- No long sustained melodic lines.
- Extreme register leaps: C3 → B6 → Eb2.
- `"dyn": "ppp"` to `"dyn": "fff"` — extreme range, unpredictable.

**Sprechstimme (if applicable):**
- Notated pitch with `"art": "sprechstimme"` field.
- The pitch is a target; performance rises toward it and falls away.
