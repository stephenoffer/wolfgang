# Grieg — Composition Guide

## Fingerprints
Any section claiming Grieg's style needs ≥3 of these 5 present.

1. **Norwegian folk scale — the raised 4th (Lydian inflection)** — The characteristic "Grieg note" is the raised 4th degree: in A minor, a D# appears as a passing tone or as a chord color. This comes from the Hardanger fiddle tradition. Combined with natural minor or Dorian, it gives a specific Norwegian coloring that is immediately recognizable. No other European composer uses this inflection as consistently.
2. **Short, atmospheric miniature forms** — Grieg's natural habitat is the short character piece: the Lyric Pieces for piano (66 pieces, each 1–4 minutes). His large-form work (Piano Concerto, Peer Gynt) is the exception. The miniature form is not a limitation — each small piece captures one specific atmosphere perfectly. The architecture is mood, not argument.
3. **Pedal point under changing harmonies** — Grieg frequently sustains a tonic or dominant pedal in the bass while the harmonies above it change freely — often to unexpected chromatic chords. The pedal gives stability; the chromatic harmonies above it give color. This technique creates a specifically Norwegian sound: rootedness (the earth, the fjord) with shifting light (clouds, water).
4. **Halling and Springar rhythms — Norwegian dance idiom** — The Halling is a lively solo dance in 2/4 with strong downbeats and wide leaps. The Springar is a triple-time dance (3/4 or 3/8) with irregular accent patterns (sometimes 2+3+2, sometimes 3+2+2). These rhythms appear throughout Grieg's instrumental music as primary material, not as decorative national color.
5. **Sudden tonal juxtaposition — Grieg's harmonic freshness** — Grieg moves between harmonically distant keys by simply placing them next to each other: A minor → F# major, or E major → C major. The move is not prepared, not modulatory — it is a juxtaposition of two different lights. Chromatic mediant relations (keys a major third apart) are his favorite harmonic distance.

---

## Note-Level Technique 1: The Norwegian Raised 4th (D#)

In A minor, the raised 4th (D#) appears as a chromatic passing tone between D and E — brief, ornamental, not structural. The note is short (eighth or sixteenth); it passes through and is gone. Its presence flavors the melody without destabilizing the tonality.

**A minor melody with D# passing tone:**
```json
{"bar_num": 1, "_feel": "The Norwegian color note appears in passing — D# between D and E", "voices": {
  "soprano": [
    {"p": "C5",  "d": "q",  "dyn": "mp"},
    {"p": "D5",  "d": "q"},
    {"p": "D#5", "d": "e",  "_feel": "The raised 4th — brief, characteristic"},
    {"p": "E5",  "d": "e"},
    {"p": "A4",  "d": "h",  "art": "legato"}
  ],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "E5",  "d": "q"},
    {"p": "D5",  "d": "q"},
    {"p": "C5",  "d": "h",  "dyn": "p"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
Bar 1: C5–D5–D#5–E5–A4. The D#5 lasts only an eighth note between D and E. Bar 2: descends back through E–D–C. The LH open-5th drone (A2 + E3) is the Norwegian earth beneath.

**The D# as a chord color** (less common, more structural):
```json
{"bar_num": 5, "voices": {
  "soprano": [{"p": ["A4","C5","D#5","E5"], "d": "h", "dyn": "mf"}],
  "bass": [{"p": "A2", "d": "h"}]
}}
```
A minor chord with D# added in an inner voice — the Lydian-minor Grieg chord. Write as an explicit array. Mark `"_feel": "the characteristic Grieg chord — A minor colored with Lydian raised 4th"`.

---

## Note-Level Technique 2: Norwegian Open-5th Drone Bass

Grieg's bass frequently imitates the open strings of a Hardanger fiddle: a tonic (A2) held or quietly repeated, with the open 5th (E3) above it. Harmonies in the upper voices change freely over this immovable bass. The drone creates rootedness; the changing harmonies above create shifting light.

**Drone bass while upper harmonies shift (4 bars in A):**
```json
{"bar_num": 1, "_feel": "The fjord is still — the pedal does not move", "voices": {
  "soprano": [
    {"p": "C5",  "d": "h",  "dyn": "p"},
    {"p": "E5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "F#5", "d": "h",  "dyn": "mp"},
    {"p": "A5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "F5",  "d": "h",  "dyn": "mf"},
    {"p": "A5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 4, "_feel": "Return to tonic color — the light settles", "voices": {
  "soprano": [
    {"p": "E5",  "d": "h",  "dyn": "p"},
    {"p": "C5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
LH: A2 + E3 held throughout all 4 bars (the Hardanger drone). RH harmonies above: A minor (bar 1) → F# major (bar 2, the chromatic mediant) → F major (bar 3, Neapolitan color) → A minor (bar 4). The A pedal is stable under all three foreign harmonies. The F# major in bar 2 and F major in bar 3 are Grieg's characteristic tonal freshness — unexpected but not wrong.

---

## Note-Level Technique 3: Pentatonic Folk Melody

Norwegian folk melody uses the pentatonic minor scale: A–C–D–E–G (no semitones). The melody moves by step or leap within this set. Character: open, unadorned, ancient. The pentatonic works naturally over the drone bass because every note is consonant with A or E.

**A pentatonic minor melody, 5 bars:**
```json
{"bar_num": 1, "_feel": "Melody from the folk tradition — only 5 notes, no semitones", "voices": {
  "soprano": [
    {"p": "A4", "d": "q",  "dyn": "p",  "expr": "tranquillo"},
    {"p": "C5", "d": "q"},
    {"p": "D5", "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "E5", "d": "q"},
    {"p": "D5", "d": "q"},
    {"p": "C5", "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "G4", "d": "q"},
    {"p": "A4", "d": "q"},
    {"p": "C5", "d": "q"},
    {"p": "D5", "d": "q"}
  ],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 4, "_feel": "Reaches up to the pentatonic ceiling, then falls", "voices": {
  "soprano": [
    {"p": "E5", "d": "dh", "orn": "trill"},
    {"p": "D5", "d": "q"}
  ],
  "bass": [{"p": "E2", "d": "h"}, {"p": "B2", "d": "h"}]
}},
{"bar_num": 5, "_feel": "Returns to the tonic — folk phrase complete", "voices": {
  "soprano": [{"p": "A4", "d": "w", "dyn": "pp"}],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
All melody notes: A, C, D, E, G — strictly pentatonic. Bar 4: the trill on E5 is the decorative high point before return. Bar 5: A4 closes to tonic. LH drone unchanged. The simplicity IS the style — do not add passing tones or ornamental semitones unless you are specifically adding the raised 4th.

---

## Note-Level Technique 4: The Halling Rhythm (2/4, Wide Leaps)

The Halling is a Norwegian solo dance — fast, athletic, 2/4. Defining characteristics: P4 or P5 leap on the downbeat (ascending), short staccato notes on the upbeat, strong accent on beat 1, weak beat 2.

**Halling theme in A minor, 4 bars (♩ = 140):**
```json
{"bar_num": 1, "_feel": "Halling — the dancer's leap on the downbeat", "voices": {
  "soprano": [
    {"p": "A4", "d": "q",  "dyn": "f",  "art": "marcato"},
    {"p": "E5", "d": "e",  "art": "staccato"},
    {"p": "D5", "d": "e",  "art": "staccato"}
  ],
  "bass": [
    {"p": "A2", "d": "q"},
    {"p": "E3", "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "C5", "d": "q",  "art": "marcato"},
    {"p": "A4", "d": "e",  "art": "staccato"},
    {"p": "G4", "d": "e",  "art": "staccato"}
  ],
  "bass": [
    {"p": "A2", "d": "q"},
    {"p": "A3", "d": "q"}
  ]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "E5", "d": "q",  "dyn": "ff", "art": "marcato"},
    {"p": "D#5","d": "e",  "_feel": "The raised 4th appears even in the dance"},
    {"p": "E5", "d": "e"}
  ],
  "bass": [
    {"p": "A2", "d": "q"},
    {"p": "E3", "d": "q"}
  ]
}},
{"bar_num": 4, "voices": {
  "soprano": [
    {"p": "A5", "d": "q",  "dyn": "ff", "art": "marcato"},
    {"p": "G5", "d": "e",  "art": "staccato"},
    {"p": "E5", "d": "e",  "art": "staccato"}
  ],
  "bass": [
    {"p": "A2", "d": "q"},
    {"p": "E3", "d": "q"}
  ]
}}
```
Bar 1: A4→E5 = P5 leap ascending, then step down — the Halling hook. Bar 3: D#5 appears briefly — the raised 4th even in the dance. Bar 4: A5 at the top = the athletic peak. LH: alternating root–5th on every beat, staccato and rhythmically even. Dynamics: f → ff. Every beat 1 gets a marcato accent.

---

## Note-Level Technique 5: Tonal Juxtaposition (Chromatic Mediant)

Grieg does not modulate to distant keys — he places them side by side. A minor ends; F# major begins. No preparation, no pivot chord, no dominant approach. The surprise IS the effect. The two keys share no common tones, yet the juxtaposition feels inevitable.

**A minor → F# major, then back:**
```json
{"bar_num": 8, "_feel": "A minor — complete, grounded, home", "voices": {
  "soprano": [{"p": "A4", "d": "w", "dyn": "mf"}],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 9, "_feel": "F# major — a different light. No transition. The key is simply other.", "voices": {
  "soprano": [
    {"p": "F#4", "d": "h",  "dyn": "p"},
    {"p": "A#4", "d": "q"},
    {"p": "C#5", "d": "q"}
  ],
  "bass": [
    {"p": "F#2", "d": "h"},
    {"p": "C#3", "d": "h"}
  ]
}},
{"bar_num": 10, "voices": {
  "soprano": [
    {"p": "F#5", "d": "h",  "dyn": "mp"},
    {"p": "E5",  "d": "h"}
  ],
  "bass": [
    {"p": "F#2", "d": "h"},
    {"p": "C#3", "d": "h"}
  ]
}},
{"bar_num": 11, "_feel": "Back to A minor — equally sudden. The journey was the point.", "voices": {
  "soprano": [{"p": "A4", "d": "w", "dyn": "p"}],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
Bar 8: A minor tonic, complete. Bar 9: F# major begins with no warning — F#4, A#4, C#5 are all from F# major, none from A minor. Bar 11: A minor returns equally without preparation. The A pedal in the LH in bars 8 and 11 anchors the original key before and after; the middle section is a parenthesis of "other light."

---

## Note-Level Technique 6: Complete Lyric Piece Opening (8-Bar Miniature)

The Lyric Piece architecture is ABA: Section A (8–12 bars) establishes atmosphere; Section B (8–12 bars) contrasts gently; return to A. This is the complete Section A for a Lyric Piece in A minor — the template for the entire form.

**Section A, bars 1–8 (pp, pentatonic, drone bass):**
```json
{"bar_num": 1, "_section": "A", "_feel": "Opening — the atmosphere is already complete in bar 1", "voices": {
  "soprano": [
    {"p": "E5",  "d": "h",  "dyn": "pp", "expr": "tranquillo"},
    {"p": "D5",  "d": "q"},
    {"p": "C5",  "d": "q",  "art": "legato"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 2, "voices": {
  "soprano": [
    {"p": "A4",  "d": "h"},
    {"p": "C5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 3, "voices": {
  "soprano": [
    {"p": "D5",  "d": "q",  "dyn": "p"},
    {"p": "D#5", "d": "e",  "_feel": "The Norwegian raised 4th — the Grieg color"},
    {"p": "E5",  "d": "e"},
    {"p": "G5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 4, "voices": {
  "soprano": [
    {"p": "E5",  "d": "dh"},
    {"p": "D5",  "d": "q"}
  ],
  "bass": [{"p": "E2", "d": "h"}, {"p": "B2", "d": "h"}]
}},
{"bar_num": 5, "voices": {
  "soprano": [
    {"p": "C5",  "d": "h",  "dyn": "pp"},
    {"p": "A4",  "d": "h",  "art": "legato"}
  ],
  "bass": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 6, "voices": {
  "soprano": [
    {"p": "G4",  "d": "q"},
    {"p": "A4",  "d": "q"},
    {"p": "C5",  "d": "h"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 7, "_feel": "The tonal juxtaposition arrives — F# major, no preparation", "voices": {
  "soprano": [
    {"p": "F#5", "d": "h",  "dyn": "p"},
    {"p": "E5",  "d": "h"}
  ],
  "bass": [
    {"p": "F#2", "d": "h"},
    {"p": "C#3", "d": "h"}
  ]
}},
{"bar_num": 8, "_feel": "Return to A minor — the section closes quietly", "voices": {
  "soprano": [
    {"p": "A4",  "d": "w",  "dyn": "pp"}
  ],
  "bass": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
Bar 1: melody begins high (E5), falling — Grieg's typical opening direction. Bar 3: the raised 4th D#5 appears as an eighth-note passing tone. Bars 4–6: pentatonic descent returns to tonic register. Bar 7: F# major appears without preparation — the one moment of harmonic surprise in 8 bars. Bar 8: A minor closes the section.

**For Section B** (bars 9–16): move to A major or relative C major, increase to mp, introduce a slight rhythmic contrast (dotted rhythm or Halling element), end on a half cadence (E major) so the return to A minor section A feels like resolution.

**For Section A return** (bars 17–24): exact literal repeat of bars 1–8, or with slight dynamic reduction (ppp throughout). The return should feel like déjà vu, not development.

---

## Pattern Directives

**Norwegian scale coloring:**
- Use natural minor (A-B-C-D-E-F-G-A) with one D# appearing as a chromatic passing tone or as an A Lydian-minor inflection.
- The D# appears: between D and E in the melody (chromatic passing tone), or as the root of a D# diminished chord.
- The characteristic Grieg chord: A minor with a D# in the bass or an inner voice.

**Pedal texture:**
- `lh`: `[{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]` — the open-5th Hardanger drone.
- Above the pedal: write harmonies that change freely — E minor, F major, G major, F# major — all while the A pedal sustains.
- `"_feel": "pedal point — the fjord is still; the harmonies above it shift like weather"`.

**Lyric piece architecture:**
- Section A: 8–12 bars, establishes atmosphere. pp or p, simple melody.
- Section B: 8–12 bars, slight harmonic departure or rhythmic contrast. mp.
- Return to A: exact or slightly varied. pp.
- Total: 24–36 bars. The miniature form is complete.

**Halling rhythm:**
- 2/4, fast (♩ = 120–160).
- Wide leaps in the melody: ascending P4 or P5 on the downbeat.
- Short, detached notes: `"art": "staccato"` or `"art": "marcato"`.
- Strong dynamic accent on beat 1; weak beat 2.

---

## Anti-patterns (what sounds wrong)

- **Large-form symphonic architecture.** Grieg's natural scale is small. Forcing his material into a 30-minute form produces padding.
- **Complex chromatic harmony (Wagner-style).** Grieg's chromatic moments are fresh and surprising, not systematic. Extended chromaticism without a clear tonal center is not Grieg.
- **German Romantic emotional weight.** Grieg's emotions are clear and fresh — he doesn't brood. A Grieg passage with Brahmsian gravitas or Wagnerian angst has mischaracterized him.
- **Absence of folk or dance idiom.** Grieg's music always touches folk tradition, either in melody (folk scales), rhythm (dance forms), or texture (open-string resonance). A purely abstract Grieg passage doesn't exist.
- **Dense orchestral texture.** Grieg's orchestration (in Peer Gynt) is clear and chamber-like, even in full-orchestra passages. Thick, opaque orchestral writing is not Norwegian.
- **Alberti bass.** Grieg does not use Alberti bass. He uses open-5th drones, waltz bass (3/4), or arpeggiated patterns — never the Classical low-mid-high-mid figure. This is the single most common error.

---

## ShortScore Field Recommendations

**Norwegian raised 4th:**
- Write D# (or equivalent) explicitly as a short note (eighth or sixteenth) between D and E.
- `"_feel": "Lydian raised 4th — the Norwegian color note"`.
- Grieg chord: `{"p": ["A2","C3","D#3","E3"], "d": "h"}` as explicit chord array.

**Drone bass:**
- LH: `[{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]` — explicit notes, not a formula.
- Never use `formula: "alberti"` for Grieg LH.
- `"_feel": "open-5th drone — Hardanger fiddle texture"`.

**Tonal juxtaposition:**
- Mark the moment: `"_feel": "F# major — no preparation, no pivot. Grieg's harmonic leap."`.
- The new key begins on beat 1 of the new bar, with full chord in both hands simultaneously.

**Miniature form:**
- Mark each section explicitly: `"_section": "A"`, `"_section": "B"`, `"_section": "A-return"`.

**Dynamics:**
- Grieg: pp to mf (most music); ff only in Halling sections or climaxes.
- `"expr": "cantabile"` for melodic sections.
- `"expr": "tranquillo"` for atmospheric opening sections.
- `"expr": "animato"` for dance sections.

---

## Reference: phrase-construction.md

Load `.claude/context/general/phrase-construction.md` for:
- Technique #14: Pentatonic Melody Construction (exactly how to write the 5-note folk melody)
- Technique #16: Norwegian Open-5th Drone Bass (how to write and sustain the Hardanger drone)
- Technique #3: Lament Bass (for Grieg's more pathos-filled slow movements)
- Technique #6: Deceptive Cadence (Grieg uses these at structural arrivals)
