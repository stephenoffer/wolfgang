# Brahms — Composition Guide

## Fingerprints
Any section claiming Brahms's style needs ≥3 of these 5 present.

1. **Hemiola at cadences** — 3-against-2 rhythmic displacement before structural arrivals. In 3/4 time, the last two bars before a cadence feel like 6/4 (two groups of three becoming three groups of two). The bar line is subverted by accent placement. This creates a rhythmic "gathering" before the cadential arrival — the music takes a deep breath.
2. **Low register density — thick inner voices** — Brahms's texture is bottom-heavy. The LH in piano writing, or the low strings and violas in orchestral writing, carry complex inner voice parts. Where Mozart is transparent and high, Brahms is thick and warm. Chord voicings cluster in the tenor register (C3–G4).
3. **Subdominant gravity — plagal coloring** — IV–I (plagal cadence), bVII–I, bVI–I — subdominant-family chords resolving to the tonic. Brahms leans toward the flat side of the key. Where Beethoven uses dominant function for drama, Brahms uses subdominant function for weight and inevitability.
4. **Motivic saturation — theme permeates accompaniment** — The main theme's interval, rhythm, or contour appears in the accompaniment, the bass line, the inner voices. Every strand of the texture is derived from the same material. The accompaniment is not just harmonic support — it's thematic commentary.
5. **Harmonic ambiguity at phrase openings** — Brahms avoids the tonic on the downbeat of phrase beginnings. Phrases often start on I6 (first inversion tonic), or on IV, or with a pedal that delays the harmonic resolution. The tonic is always arrived at, never given for free.

---

## Note-Level Technique 1: Hemiola at the Cadence (3/4 → felt-as-2/4)

Two bars of normal 3/4 followed by two bars of hemiola — the 6 beats of bars 7–8 re-grouped as 3 pairs of 2 (accent on beats 1, 3, 5 of the 6-beat span). The effect: the meter seems to temporarily shift to 2/4, then the cadence resolves the ambiguity.

**Normal 3/4 (bars 5–6) → hemiola (bars 7–8) → cadential arrival (bar 9):**
```json
{"bar_num": 5, "_feel": "Normal 3/4 — three equal quarter-note beats per bar", "voices": {
  "soprano": [
    {"p": "D5", "d": "q", "dyn": "mf"},
    {"p": "C5", "d": "q"},
    {"p": "B4", "d": "q"}
  ],
  "bass": [
    {"p": "G2", "d": "q"},
    {"p": "D3", "d": "q"},
    {"p": "B3", "d": "q"}
  ]
}},
{"bar_num": 6, "voices": {
  "soprano": [
    {"p": "A4", "d": "q"},
    {"p": "G4", "d": "q"},
    {"p": "F#4","d": "q"}
  ],
  "bass": [
    {"p": "D2", "d": "q"},
    {"p": "A3", "d": "q"},
    {"p": "F#3","d": "q"}
  ]
}},
{"bar_num": 7, "_feel": "Hemiola begins — accent on beat 1 AND beat 3. The bar has two downbeats.", "voices": {
  "soprano": [
    {"p": "G4", "d": "q", "dyn": "f",  "art": "sfz"},
    {"p": "F#4","d": "q"},
    {"p": "E4", "d": "q", "art": "sfz"}
  ],
  "bass": [
    {"p": "C2", "d": "h"},
    {"p": "G3", "d": "q"}
  ]
}},
{"bar_num": 8, "_feel": "Hemiola continues — accent on beat 2, not beat 1. The metric ground has shifted.", "voices": {
  "soprano": [
    {"p": "D4", "d": "q"},
    {"p": "C4", "d": "q", "art": "sfz"},
    {"p": "B3", "d": "q"}
  ],
  "bass": [
    {"p": "G2", "d": "h"},
    {"p": "D3", "d": "q"}
  ]
}},
{"bar_num": 9, "_feel": "Cadential arrival — the 3/4 reasserts itself. The hemiola tension resolves.", "voices": {
  "soprano": [
    {"p": "G3", "d": "dh", "dyn": "mp"}
  ],
  "bass": [
    {"p": "G2", "d": "dh", "dyn": "mp"}
  ]
}}
```
Bar 5–6: normal 3/4, accent on beat 1 only. Bars 7–8: sfz marks appear on beat 1 AND beat 3 of bar 7, then beat 2 of bar 8 — the hemiola grouping. The 6 beats of bars 7–8 group as: (beat1+beat2)(beat3+beat4)(beat5+beat6) = 3 groups of 2. Bar 9: the tonic arrival resolves the ambiguity; regular 3/4 resumes. The LH moves to half notes during the hemiola — reinforcing the duple feel.

---

## Note-Level Technique 2: Melody in Parallel Thirds (Brahms's Signature Warmth)

Brahms harmonizes his melody in parallel thirds more consistently than any other Romantic composer. Write BOTH notes of every interval — the upper (melody) and the lower (harmony third). Do NOT write just the melody and imply the harmonization. The two notes together create the characteristic "warm" Brahms sound.

**Melody + parallel thirds below, RH only (4 bars in G major):**
```json
{"bar_num": 1, "_feel": "Parallel thirds — both voices written. The warmth is the chord, not the single note.", "voices": {
  "soprano": [
    {"p": ["D5","B4"], "d": "q",  "dyn": "mp", "art": "legato"},
    {"p": ["C5","A4"], "d": "q"},
    {"p": ["B4","G4"], "d": "q"},
    {"p": ["A4","F#4"],"d": "q"}
  ],
  "bass": [{"p": "G2", "d": "h"}, {"p": "D3", "d": "h"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": ["G4","E4"], "d": "h",  "dyn": "mf"},
    {"p": ["F#4","D4"],"d": "q"},
    {"p": ["E4","C#4"],"d": "q"}
  ],
  "bass": [{"p": "D2", "d": "h"}, {"p": "A3", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": ["D4","B3"], "d": "q"},
    {"p": ["E4","C4"], "d": "q"},
    {"p": ["F#4","D4"],"d": "q"},
    {"p": ["G4","E4"], "d": "q", "dyn": "f"}
  ],
  "bass": [{"p": "G2", "d": "h"}, {"p": "B2", "d": "h"}]
}},
{"bar_num": 4, "voices": {
  "soprano": [
    {"p": ["A4","F#4"],"d": "dh", "dyn": "mf"},
    {"p": ["G4","E4"], "d": "q",  "art": "legato"}
  ],
  "bass": [{"p": "D2", "d": "h"}, {"p": "A3", "d": "h"}]
}}
```
Every RH event is a chord array of 2 notes — upper melody + lower third. The intervals: D5/B4 = major 3rd; C5/A4 = minor 3rd; B4/G4 = major 3rd. Brahms alternates major and minor thirds following the key signature (not all the same size). The LH provides bass support — it need not be elaborate; the thirds carry the expressive weight.

---

## Note-Level Technique 3: LH Two-Voice Thick Texture (Bass + Inner Harmony)

Brahms's LH in piano writing is not just a bass note or an Alberti bass — it carries TWO independent voices: a bass voice (low) and an inner harmonic voice that moves against the RH melody. Write both voices explicitly. The span: often a 10th or more.

**LH two-voice texture in G minor, 4 bars:**
```json
{"bar_num": 1, "_feel": "LH: bass voice low, inner harmony mid-register. Two independent voices.", "voices": {
  "soprano": [
    {"p": ["D5","Bb4"],"d": "h",  "dyn": "mp"},
    {"p": ["C5","A4"], "d": "h"}
  ],
  "bass": [
    {"p": "G2", "d": "q"},
    {"p": "G3", "d": "q"},
    {"p": "Bb3","d": "q"},
    {"p": "D4", "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": ["Bb4","G4"],"d": "h",  "dyn": "mf"},
    {"p": ["A4","F#4"],"d": "h"}
  ],
  "bass": [
    {"p": "D2", "d": "q"},
    {"p": "A3", "d": "q"},
    {"p": "F#3","d": "q"},
    {"p": "D4", "d": "q"}
  ]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": ["G4","Eb4"],"d": "h",  "dyn": "f"},
    {"p": ["F4","D4"], "d": "h"}
  ],
  "bass": [
    {"p": "Eb2","d": "q"},
    {"p": "Bb3","d": "q"},
    {"p": "G3", "d": "q"},
    {"p": "Eb4","d": "q"}
  ]
}},
{"bar_num": 4, "voices": {
  "soprano": [
    {"p": ["D4","Bb3"],"d": "dh", "dyn": "mf"}
  ],
  "bass": [
    {"p": "D2", "d": "h"},
    {"p": "D3", "d": "h"}
  ]
}}
```
LH bars 1–3: four quarter notes per bar — the first note is the bass (G2, D2, Eb2) and the remaining three form an arpeggiated inner harmony. The bass is in the low 2nd octave; the inner harmony climbs through the middle register. The total span (G2 to D4 = 17th = more than 2 octaves) requires a large hand. Bar 4: LH simplifies to two bass octaves for the cadential arrival. Never use the Alberti formula for Brahms: his LH is more irregular and harmonically dense.

---

## Pattern Directives

**Piano writing (Intermezzi, Capriccios, late piano pieces):**
- LH: thick arpeggiated chords spanning a 10th, not just a fifth. Often two voices in the LH (bass + inner harmony).
- RH: melody in thirds or sixths — Brahms harmonizes his melodies in parallel thirds or sixths more consistently than any other composer. The melody is never single-note in climactic sections.
- Inner voice: a middle voice that moves against both the melody and the bass creates the "warm" Brahms sound.

**Cross-rhythms:**
- 3-against-2: RH playing triplets while LH plays duple (or vice versa). This is not ornamental — it's a fundamental Brahms texture for much of the Intermezzi.
- Hemiola: bars 7–8 of an 8-bar phrase in 3/4 — group the 6 beats as 2×3 instead of 3×2. Mark this through beaming and accent.

**Development sections (chamber/orchestral):**
- Brahms develops by combining the theme with its own augmentation (slower version). Two voices: the original, and a half-speed version in the bass.
- Descending sequences in thirds (much more common than ascending sequences).
- Arrive at a dominant pedal point — sustained low note while harmonies above prepare the recapitulation.

**Harmonic approach:**
- Begin with I6 or IV6 to avoid tonic strength at phrase openings.
- Neapolitan (bII) in minor movements — appears at moments of maximum harmonic pathos.
- Return to home key: prefer plagal cadence (IV–I) over perfect authentic (V–I) for codas.

## Anti-patterns (what sounds wrong)

- **Transparent, single-note melody.** Brahms never presents a melody bare in his mature works. It's always harmonized in thirds, sixths, or octaves, or the texture is so thick that no single line is exposed.
- **Regular, undisrupted meter.** A Brahms movement that flows in regular 3/4 without hemiola or cross-rhythm at any point is wrong. The rhythmic complexity IS his style.
- **Dominant-function climaxes.** Brahms ends sections and movements with subdominant or plagal motion, not just V–I. A coda that's all dominant preparation resolving to tonic is not idiomatic.
- **Light, high-register texture.** Brahms's sound is warm and low. A texture that sits entirely in the upper register without bass depth is Mozart, not Brahms.
- **Development that doesn't combine voices.** Brahms developments are contrapuntal — themes appear simultaneously, overlapping, in augmentation against themselves. A development that just sequences the theme is not Brahms.

## ShortScore Field Recommendations

**Piano texture:**
- `rh`: melody in parallel thirds or sixths (write BOTH notes of every harmonic interval).
- `lh`: two-voice texture — bass note (explicit) + inner voice (explicit). A chord of 4 notes spanning an octave, each note written.

**Cross-rhythms:**
- Write triplets against duple explicitly: three equal-value notes spanning two beats.
- Hemiola in 3/4: bars 7–8 of phrase — accent on beats 1 and 3 of bar 7, beat 2 of bar 8 (grouping of 3+3 across the bar line).

**Dynamics:**
- Brahms's forte is warm and full, not harsh. Mark `"expr": "con calore"` for intense passages.
- Sudden piano after forte for introspective retreats (common in Intermezzi).
- Crescendo over long spans (8–16 bars) rather than sudden dynamic contrasts.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #12: Dominant Pedal — Brahms sustains dominant under harmonies in development sections
- Technique #7: Neapolitan Approach — Brahms's most pathos-laden cadential approach in minor movements
- Technique #2: The 4-3 Suspension — fundamental to Brahms's polyphonic inner-voice writing
- Technique #5: Ascending Sequence — used in development sections (Brahms prefers descending; use #5 reversed)
