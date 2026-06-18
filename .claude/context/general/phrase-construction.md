# Phrase Construction — Note-Level Technique Library

Every technique here is shown as actual ShortScore measures. Not descriptions. Not rules. Notes.

When you write a phrase, you are assembling specific gestures from this vocabulary. A musical phrase is made of these atomic units, combined and connected by voice-leading. Learn to recognize which gesture each situation calls for.

---

## 1. The Appoggiatura and Sigh

The appoggiatura lands on a **dissonant** note on a strong beat, then resolves DOWN by step. It is not a grace note — it holds its duration. The dissonance creates a lean; the resolution is the release. "The melody sighs."

**Situation**: Melody approaches a chord tone from a step above. The dissonant note gets the full beat; the chord tone gets the second half.

```json
{"bar_num": 5, "voices": {
  "rh": [
    {"p": "E5",  "d": "q",  "dyn": "mf", "expr": "espressivo"},
    {"p": "D5",  "d": "q"},
    {"p": "C5",  "d": "h"}
  ],
  "lh": {"formula": "block_chord", "bass": "F2", "chord_tones": ["C3","F3","A3"]}
}}
```
Bar is in F major. E5 is the 7th (dissonance over F major) — it leans into D5 (6th) then falls to C5 (5th). The dissonance on beat 1 is the expressive moment.

**The sigh figure** (short version — grace note approach):
```json
{"p": "E5", "d": "e", "orn": "grace:F5"},
{"p": "D5", "d": "q"}
```
F5 arrives as a grace note, falls to E5, then resolves to D5. Three notes, one gesture. The grace note is the lean; E5 is the appoggiatura; D5 is the release.

---

## 2. The 4-3 Suspension

The melody holds the 4th above the bass through a bar change. The 4th is dissonant over the new chord; it resolves DOWN to the 3rd. Effective over a dominant chord: the 4th (=7th of the key) resolves to the major 3rd.

**In A minor over an E major chord:**
Bar N: melody holds A4 (the 4th above E) — sustained over the entire bar.
Bar N+1: A4 steps down to G#4 (the 3rd of E major). This is the resolution.

```json
{"bar_num": 8, "voices": {
  "rh": [{"p": "A4", "d": "w", "dyn": "mp", "art": "tenuto"}],
  "lh": {"formula": "block_chord", "bass": "E2", "chord_tones": ["B2","E3","G#3"]}
}},
{"bar_num": 9, "voices": {
  "rh": [
    {"p": "G#4", "d": "h", "expr": "dolce"},
    {"p": "A4",  "d": "q"},
    {"p": "E4",  "d": "q"}
  ],
  "lh": {"formula": "block_chord", "bass": "A2", "chord_tones": ["E3","A3","C4"]}
}}
```
Bar 8: melody holds A4 (suspended 4th over E major). Bar 9: G#4 is the resolution (3rd of E). The held note creates the tension; the single step resolves it.

**The 9-8 suspension** (more intense): same logic, melody holds the 9th (one step above the octave) and resolves down to the 8th. Used at climactic arrivals.

---

## 3. The Lament Bass (Descending Chromatic Bass)

Bass descends C–B–Bb–A over 4 bars while an upper voice holds or moves slowly. One of the most expressive devices in tonal music — the inexorable falling bass creates a sense of grief, inevitability, or deep pathos. From Purcell's Dido through Barber's Adagio.

```json
{"bar_num": 1, "voices": {
  "vln1": [{"p": "E5",  "d": "w", "dyn": "p"}],
  "vc":   [{"p": "C2",  "d": "w", "dyn": "p"}]
}},
{"bar_num": 2, "voices": {
  "vln1": [{"p": "D5",  "d": "w"}],
  "vc":   [{"p": "B1",  "d": "w"}]
}},
{"bar_num": 3, "voices": {
  "vln1": [{"p": "C5",  "d": "h"}, {"p": "B4",  "d": "h"}],
  "vc":   [{"p": "Bb1", "d": "w"}]
}},
{"bar_num": 4, "voices": {
  "vln1": [{"p": "A4",  "d": "w", "orn": "trill"}],
  "vc":   [{"p": "A1",  "d": "w"}]
}}
```
Bass: C–B–Bb–A (4 bars, one chromatic step per bar). Top voice responds. Bar 4 arrives on tonic A minor — the Bb in bar 3 is the chromatic passing tone that makes the whole descent ache.

**Use with inner voices filling harmony:**
Inner voices can move between bars to create counterpoint against the falling bass. The bass is the structural anchor; the inner voices provide harmonic color.

---

## 4. The Walking Bass

Bass walks by step, connecting harmonic roots. Essential in Baroque, jazz, and any style that wants the bass to have melodic purpose.

**ii–V–I in D minor (bars 1–3):**
```json
{"bar_num": 1, "voices": {
  "melody": [{"p": "F4", "d": "h"}, {"p": "E4", "d": "q"}, {"p": "D4", "d": "q"}],
  "bass":   [
    {"p": "G2",  "d": "q", "dyn": "mp"},
    {"p": "A2",  "d": "q"},
    {"p": "Bb2", "d": "q"},
    {"p": "C3",  "d": "q"}
  ]
}},
{"bar_num": 2, "voices": {
  "melody": [{"p": "C#4", "d": "h"}, {"p": "A4", "d": "h"}],
  "bass":   [
    {"p": "A2",  "d": "q"},
    {"p": "G2",  "d": "q"},
    {"p": "F2",  "d": "q"},
    {"p": "E2",  "d": "q"}
  ]
}},
{"bar_num": 3, "voices": {
  "melody": [{"p": "D4", "d": "w"}],
  "bass":   [{"p": "D2",  "d": "w"}]
}}
```
Bar 1 bass: G–A–Bb–C walks down by step to the dominant. Bar 2 bass: A–G–F–E walks down through the dominant chord to the leading tone. Bar 3: arrives on tonic D. The bass creates direction; the melody creates expression.

---

## 5. The Ascending Sequence (Tension Builder)

A 2-bar cell is restated starting one step higher, twice or three times. Each repetition is slightly louder. The direction is upward; the listener is being pulled toward the peak.

**Cell (D minor, 2 bars) stated, then sequenced up:**
```json
{"bar_num": 9, "_feel": "Sequence begins — forward lean, slightly urgent", "voices": {
  "vln1": [
    {"p": "D4", "d": "q", "dyn": "mf"},
    {"p": "E4", "d": "q"},
    {"p": "F4", "d": "q"},
    {"p": "G4", "d": "q"}
  ],
  "vc": [{"p": "D3", "d": "h"}, {"p": "A2", "d": "h"}]
}},
{"bar_num": 10, "voices": {
  "vln1": [{"p": "A4", "d": "h"}, {"p": "G4", "d": "q"}, {"p": "F4", "d": "q"}],
  "vc":   [{"p": "F2", "d": "h"}, {"p": "C3", "d": "h"}]
}},
{"bar_num": 11, "_feel": "One step higher — pushing harder now", "voices": {
  "vln1": [
    {"p": "E4", "d": "q", "dyn": "f"},
    {"p": "F4", "d": "q"},
    {"p": "G4", "d": "q"},
    {"p": "A4", "d": "q"}
  ],
  "vc": [{"p": "E3", "d": "h"}, {"p": "B2", "d": "h"}]
}},
{"bar_num": 12, "voices": {
  "vln1": [{"p": "B4", "d": "h"}, {"p": "A4", "d": "q"}, {"p": "G4", "d": "q"}],
  "vc":   [{"p": "G2", "d": "h"}, {"p": "D3", "d": "h"}]
}},
{"bar_num": 13, "_feel": "Final sequence push — the peak is the next bar", "voices": {
  "vln1": [
    {"p": "F4", "d": "q", "dyn": "ff"},
    {"p": "G4", "d": "q"},
    {"p": "A4", "d": "q"},
    {"p": "Bb4","d": "q"}
  ],
  "vc": [{"p": "F2", "d": "h"}, {"p": "C3", "d": "h"}]
}}
```
Each 2-bar unit starts a step higher (D→E→F). Each repetition increases dynamics (mf→f→ff). The peak arrives in bar 14. This is the mechanical spine of most climax builds.

---

## 6. The Deceptive Cadence

V expects to resolve to I. Instead it resolves to VI (or bVI). The shock is that the melody's held note is consonant on VI but NOT the tonic — it's stranded, hanging, tender. Often followed by a second attempt at the cadence that finally lands on I.

**In D minor, V→bVI (instead of V→i):**
```json
{"bar_num": 15, "_feel": "The arrival everyone expects — but it doesn't come", "voices": {
  "rh": [{"p": "D5", "d": "w", "dyn": "mp", "art": "tenuto"}],
  "lh": {"formula": "block_chord", "bass": "A2", "chord_tones": ["E3","A3","C#4"]}
}},
{"bar_num": 16, "_feel": "Deceptive — bVI instead of i. The melody's D is the fifth of Bb. Consonant but wrong.", "voices": {
  "rh": [{"p": "D5", "d": "h", "dyn": "p"}, {"p": "C5", "d": "h"}],
  "lh": {"formula": "block_chord", "bass": "Bb2", "chord_tones": ["F3","Bb3","D4"]}
}}
```
Bar 15: V chord (A major) with melody held on D5 (4th = suspension, wants to resolve). Bar 16: instead of resolving to D minor (i), it resolves to Bb major (bVI). The melody's D5 is suddenly the 3rd of Bb — a soft landing but not home. Piano-subito is the right response.

---

## 7. The Neapolitan Approach (bII6)

The Neapolitan chord is a major chord on the flattened 2nd degree, in first inversion. It appears before a dominant, creating an expressive two-step approach to the cadence. Used for maximum pathos at formal arrivals.

**In D minor, bII6 → V → i:**
```json
{"bar_num": 18, "voices": {
  "rh": [
    {"p": "Bb4", "d": "h", "dyn": "mf", "art": "tenuto"},
    {"p": "A4",  "d": "h"}
  ],
  "lh": {"formula": "block_chord", "bass": "F2", "chord_tones": ["Bb2","D3","F3"]}
}},
{"bar_num": 19, "voices": {
  "rh": [{"p": "A4", "d": "dh", "orn": "trill"}, {"p": "rest", "d": "q"}],
  "lh": {"formula": "block_chord", "bass": "A2", "chord_tones": ["E3","A3","C#4"]}
}},
{"bar_num": 20, "voices": {
  "rh": [{"p": "D4",  "d": "w", "dyn": "p"}],
  "lh": {"formula": "block_chord", "bass": "D2", "chord_tones": ["F2","A2","D3"]}
}}
```
Bar 18: bII6 = Bb major in first inversion (bass = F, the 3rd). Melody on Bb4 — expressive, soft, tender. Bar 19: V (A major), melody holds A4 with a trill. Bar 20: i (D minor) arrives — the tonic. The bII6 creates a second, softer approach before the dominant; the cadence arrives with warmth, not force.

---

## 8. The Chopin Nocturne Bass (Wide Arpeggio)

The signature LH of Chopin's nocturnes: bass note on beat 1 (very low), then chord tones spanning a 9th or 10th above. NOT Alberti (low-mid-high-mid). The hand stretches: the bass note is almost an octave below the lowest chord tone.

**Bar in Eb major (Eb minor nocturne idiom), 3/4 time:**
```json
{"bar_num": 3, "voices": {
  "rh": [
    {"p": "Bb5", "d": "dh", "dyn": "p", "orn": "grace:C6"},
    {"p": "Ab5", "d": "q"}
  ],
  "lh": [
    {"p": "Eb2", "d": "q"},
    {"p": "Bb3", "d": "q"},
    {"p": "Eb4", "d": "q"}
  ]
}}
```
LH explicit notes: Eb2 (root, very low), then Bb3 (5th, a 7th above), then Eb4 (octave of root, a 9th above the bass). RH: melody with grace note from above (C6→Bb5), then Ab5. The LH spans a compound 9th — the piano's full resonance rings under the quiet melody.

**In G minor:**
```json
"lh": [
  {"p": "G2",  "d": "q"},
  {"p": "D4",  "d": "q"},
  {"p": "Bb4", "d": "q"}
]
```
G2→D4 = compound 5th (12 semitones). D4→Bb4 = minor 6th. The low bass note resonates while the upper chord tones decay — the piano's natural physics create the sustain texture. Write every note explicitly; never use a formula for Chopin nocturne LH.

---

## 9. The Chromatic Inner Voice Descent (Chopin Sigh)

While the soprano holds or moves slowly, a middle voice descends chromatically. The soprano melody appears stable; the inner voice creates increasing tension or tenderness below it.

**Soprano holds G4; inner voice descends C4→B3→Bb3→A3; bass holds C2:**
```json
{"bar_num": 5, "voices": {
  "rh": [
    {"p": ["G4","C4"], "d": "q"},
    {"p": ["G4","B3"], "d": "q"},
    {"p": ["G4","Bb3"],"d": "q"},
    {"p": ["G4","A3"], "d": "q"}
  ],
  "lh": [{"p": "C2", "d": "w"}]
}}
```
RH written as chord arrays — soprano G4 held; inner voice [C4, B3, Bb3, A3] descends one semitone per beat. Bass holds C2. This is a descending chromatic scale 4th beneath the melody. Over these 4 beats: implied harmonies are C–Cmaj7–C7–C with added 6th. The chromatic descent is the expression.

---

## 10. The Alberti Bass (Classical)

The Classical keyboard accompaniment: bass note, then upper chord tone, then middle chord tone, then upper again. Low–High–Mid–High. Unlike Chopin's LH, Alberti stays in a narrow range (an octave, no more).

**In C major, 4/4:**
```json
{"bar_num": 1, "voices": {
  "rh": [
    {"p": "G4", "d": "h", "dyn": "p"},
    {"p": "E4", "d": "q"},
    {"p": "F4", "d": "q"}
  ],
  "lh": [
    {"p": "C3",  "d": "q"},
    {"p": "G3",  "d": "q"},
    {"p": "E3",  "d": "q"},
    {"p": "G3",  "d": "q"}
  ]
}}
```
LH: C3 (root, low), G3 (high), E3 (mid), G3 (high again) = Alberti in C major. Range: C3–G3 (a 5th, never more than an octave). Steady quarter notes, metronomic. RH: simple 2-note melodic phrase in half notes. The Alberti provides harmonic rhythm without obscuring the melody.

---

## 11. Parallel Thirds in the Melody (Two-Voice Unison)

One of the most immediately warm textures: melody doubled in parallel thirds by a second instrument or voice. The interval of the third (major or minor depending on key) creates warmth without heaviness.

**vln1 melody doubled at the third below by vln2:**
```json
{"bar_num": 7, "voices": {
  "vln1": [
    {"p": "A4", "d": "q", "dyn": "mf"},
    {"p": "G4", "d": "q"},
    {"p": "F4", "d": "q"},
    {"p": "E4", "d": "q"}
  ],
  "vln2": [
    {"p": "F4", "d": "q"},
    {"p": "E4", "d": "q"},
    {"p": "D4", "d": "q"},
    {"p": "C#4","d": "q"}
  ]
}}
```
vln1: A4–G4–F4–E4 (descending scale in A minor). vln2: F4–E4–D4–C#4 (parallel thirds below, adjusted to stay in A minor: the C#4 is the leading tone). Every note is a third apart. The result: warmth and clarity simultaneously.

---

## 12. The Suspense Pedal (Dominant Pedal)

The bass holds the dominant note while harmonies move above it — including harmonies that are dissonant against the pedal. This creates a prolonged tension that makes the eventual tonic resolution feel like a physical release.

**Dominant pedal on A (in D minor context), 4 bars:**
```json
{"bar_num": 20, "_feel": "Held breath — the A in the bass will not let go", "voices": {
  "vln1": [{"p": "F4", "d": "h"}, {"p": "E4", "d": "h"}],
  "vla":  [{"formula": "chorale_hold", "bass": "C4", "chord_tones": ["E4","C4"]}],
  "vc":   [{"p": "A2", "d": "w"}]
}},
{"bar_num": 21, "voices": {
  "vln1": [{"p": "E4", "d": "h"}, {"p": "D4", "d": "q"}, {"p": "C#4", "d": "q"}],
  "vla":  [{"formula": "chorale_hold", "bass": "A3", "chord_tones": ["E4","A3"]}],
  "vc":   [{"p": "A2", "d": "w"}]
}},
{"bar_num": 22, "voices": {
  "vln1": [{"p": "C#4", "d": "h"}, {"p": "A4",  "d": "h", "dyn": "f"}],
  "vla":  [{"formula": "chorale_hold", "bass": "E4", "chord_tones": ["E4","A3"]}],
  "vc":   [{"p": "A2", "d": "w"}]
}},
{"bar_num": 23, "_feel": "Release — the tonic arrives after 3 bars of held tension", "voices": {
  "vln1": [{"p": "D4",  "d": "w", "dyn": "p", "orn": "trill"}],
  "vla":  [{"formula": "chorale_hold", "bass": "F3", "chord_tones": ["D4","A3","F3"]}],
  "vc":   [{"p": "D2", "d": "w", "dyn": "p"}]
}}
```
Bass: A2 held for 3 bars (the dominant), then D2 arrives in bar 23 (tonic). Upper voices move through harmonies that are dissonant against A (the Dm in bar 20 includes C and F — dissonant 3rd and 6th against A). The longer the pedal holds, the more powerful the release.

---

## 13. The Cadential 6/4 → V → I

The 6/4 chord (I in second inversion = the 5th in the bass) followed by V then I is the standard closure for every Classical period. It is the harmonic equivalent of a full stop. Arrival on the 6/4 delays the tonic; V resolves it; I closes it.

**In G major, bars 7-8:**
```json
{"bar_num": 7, "voices": {
  "rh": [{"p": "B4", "d": "h", "dyn": "f"}, {"p": "A4", "d": "h", "orn": "trill"}],
  "lh": [
    {"p": "D3", "d": "h"},
    {"p": "D3", "d": "h"}
  ]
}},
{"bar_num": 8, "voices": {
  "rh": [{"p": "G4", "d": "w", "dyn": "p"}],
  "lh": [{"p": "G2", "d": "w"}]
}}
```
Bar 7: bass = D (the dominant note). RH: B4 + A4 with trill = the 6/4 over D bass, then the leading tone approaching tonic. Bar 8: G4 over G2 = tonic arrival. The D in the bass for a full bar is the preparation; the G is the resolution.

---

## 14. Pentatonic Melody Construction (Folk/Norwegian/Celtic)

The pentatonic minor scale: root–m3–P4–P5–m7. In A: A–C–D–E–G. No semitones — no leading tone, no tritone. Character: ancient, open, modal, unsentimental. The melody moves naturally by step or leap within these five notes. Any note is consonant over a drone bass.

**A pentatonic minor melody, 5 bars:**
```json
{"bar_num": 1, "_feel": "Folk melody — 5 notes only, no semitones", "voices": {
  "rh": [
    {"p": "A4", "d": "q",  "dyn": "p", "expr": "tranquillo"},
    {"p": "C5", "d": "q"},
    {"p": "D5", "d": "h"}
  ],
  "lh": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "rh": [
    {"p": "E5", "d": "q"},
    {"p": "D5", "d": "q"},
    {"p": "C5", "d": "h"}
  ],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "rh": [
    {"p": "G4", "d": "q"},
    {"p": "A4", "d": "q"},
    {"p": "C5", "d": "q"},
    {"p": "D5", "d": "q"}
  ],
  "lh": [{"p": "A2", "d": "w"}]
}},
{"bar_num": 4, "_feel": "Reaches the pentatonic ceiling — trill, then descends", "voices": {
  "rh": [
    {"p": "E5", "d": "dh", "orn": "trill"},
    {"p": "D5", "d": "q"}
  ],
  "lh": [{"p": "E2", "d": "h"}, {"p": "B2", "d": "h"}]
}},
{"bar_num": 5, "voices": {
  "rh": [{"p": "A4", "d": "w", "dyn": "pp"}],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
Every melody note is from {A, C, D, E, G}. No B♭, no F, no leading tone. The trill in bar 4 decorates E5 (the 5th, the pentatonic "ceiling"). The drone bass (A2 + E3) is the natural foundation. **Transposition**: shift all melody AND bass notes by the same interval. In D pentatonic minor: D–F–G–A–C.

---

## 15. Modal Phrase — Dorian Mode

Dorian = natural minor with raised 6th. In D Dorian: D–E–F–G–A–B–C–D (B♮, not B♭). The raised 6th gives the mode a brighter, folksier quality than natural minor. Used by Grieg (Norwegian Dorian), Bartók (Hungarian folk), and modal jazz.

**D Dorian melody with characteristic B♮:**
```json
{"bar_num": 1, "_feel": "Dorian — minor with the raised 6th. Neither major nor minor — both.", "voices": {
  "rh": [
    {"p": "D4", "d": "q",  "dyn": "mp"},
    {"p": "E4", "d": "q"},
    {"p": "F4", "d": "q"},
    {"p": "G4", "d": "q"}
  ],
  "lh": [{"p": "D2", "d": "w"}]
}},
{"bar_num": 2, "voices": {
  "rh": [
    {"p": "A4", "d": "h"},
    {"p": "B4", "d": "q",  "_feel": "B♮ — the Dorian raised 6th. This is the characteristic note."},
    {"p": "A4", "d": "q"}
  ],
  "lh": [{"p": "D2", "d": "h"}, {"p": "A2", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "rh": [
    {"p": "G4", "d": "q"},
    {"p": "F4", "d": "q"},
    {"p": "E4", "d": "q"},
    {"p": "D4", "d": "q"}
  ],
  "lh": [{"p": "D2", "d": "w"}]
}}
```
Bar 2: B4 (B♮) is the Dorian note — it would be B♭ in D natural minor. The difference of one semitone changes the emotional character from darkness to folk-brightness. **Use Dorian when**: the style is folk (Grieg, Bartók), Celtic, or modal jazz. Do NOT use the harmonic minor leading tone (C#) in Dorian — that is a different mode.

---

## 16. Norwegian Open-5th Drone Bass (Hardanger Idiom)

The Hardanger fiddle has open-string resonance that colors every note. Grieg imitates this in piano: bass holds tonic + open 5th as explicit notes (not a formula). Harmonies in the upper voices change freely above. The bass never moves for 4–8 bars.

**Open-5th drone while upper harmonies shift (A minor context):**
```json
{"bar_num": 1, "_feel": "The drone never moves — the earth beneath", "voices": {
  "rh": [{"p": "C5", "d": "h", "dyn": "p"}, {"p": "E5", "d": "h"}],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 2, "_feel": "F# major above the A drone — the chromatic mediant juxtaposition", "voices": {
  "rh": [{"p": "F#5", "d": "h", "dyn": "mp"}, {"p": "A5", "d": "h"}],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 3, "_feel": "F major — the Neapolitan neighbor, still over the drone", "voices": {
  "rh": [{"p": "F5",  "d": "h", "dyn": "mf"}, {"p": "A5", "d": "h"}],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 4, "_feel": "Return to A minor color — the light settles", "voices": {
  "rh": [{"p": "E5", "d": "h", "dyn": "p"},  {"p": "C5", "d": "h"}],
  "lh": [{"p": "A2", "d": "h"}, {"p": "E3", "d": "h"}]
}}
```
LH: A2 + E3 (the open 5th = P5 = 7 semitones) held through all 4 bars. Write as explicit notes, NOT as `formula: "alberti"` or `formula: "block_chord"`. The open 5th has no third — it is neither major nor minor. This is intentional: it gives the bass a timeless, modal quality. **Grieg also uses**: A1 + E2 + A2 (doubled drone across two octaves) for piano writing where low resonance is needed.

---

## 17. Parallel Chord Movement (Debussy)

Debussy moves chords in parallel — same voicing, shifted up or down by step or whole tone. This violates Classical voice-leading (parallel 5ths and octaves everywhere) and that is the point. The chords become timbral events, not harmonic functions. The progression does not imply a key — it creates color.

**Parallel major 7th chords moving by whole tone (C → D → E):**
```json
{"bar_num": 1, "_feel": "The chord shape slides — no voice-leading, just color moving", "voices": {
  "rh": [
    {"p": ["E5","G5","B5","D6"], "d": "h", "dyn": "p"},
    {"p": ["F#5","A5","C#6","E6"], "d": "h"}
  ],
  "lh": [
    {"p": ["C3","E3","G3","B3"], "d": "h"},
    {"p": ["D3","F#3","A3","C#4"], "d": "h"}
  ]
}},
{"bar_num": 2, "voices": {
  "rh": [
    {"p": ["G#5","B5","D#6","F#6"], "d": "h", "dyn": "mp"},
    {"p": ["A#5","C#6","F6","G#6"],"d": "h"}
  ],
  "lh": [
    {"p": ["E3","G#3","B3","D#4"], "d": "h"},
    {"p": ["F#3","A#3","C#4","F4"], "d": "h"}
  ]
}}
```
Each chord is the same voicing (root–M3–P5–M7 = major 7th chord) shifted up by whole tone. The parallel 5ths are intentional — they are Debussy's "planing" technique. Character: shimmering, suspended, like light on water. **Use sparingly**: 2–4 chords in parallel, then break with a different gesture. Sustained parallel planing for 16 bars becomes monotonous.

**Simpler parallel triads (moving by semitone):**
```json
{"bar_num": 5, "_feel": "Chord shape descends by semitone — impressionist watercolor", "voices": {
  "rh": [
    {"p": ["C5","E5","G5"],  "d": "q", "dyn": "pp"},
    {"p": ["B4","D#5","F#5"],"d": "q"},
    {"p": ["Bb4","D5","F5"], "d": "q"},
    {"p": ["A4","C#5","E5"], "d": "q"}
  ],
  "lh": [{"p": "C3", "d": "w"}]
}}
```
Four chords in 4 beats, each a semitone lower, same major triad voicing. The bass stays on C3 (pedal point). The top voice descends C5–B4–Bb4–A4 — a chromatic bass line in the soprano. Debussy.

---

## 18. Whole-Tone Passage

The whole-tone scale: C–D–E–F#–G#–Bb (all whole steps). Only two whole-tone scales exist (the other starts on C#). Key properties: no perfect 5th, no leading tone, every interval is a major 2nd or augmented. Character: dreamlike, suspended, directionless — useful for transitional moments or scenes of unreality.

**Melody in the whole-tone scale (ascending, then descending):**
```json
{"bar_num": 1, "_feel": "Whole-tone — no gravity, no direction, suspended in air", "voices": {
  "rh": [
    {"p": "C5",  "d": "q",  "dyn": "p"},
    {"p": "D5",  "d": "q"},
    {"p": "E5",  "d": "q"},
    {"p": "F#5", "d": "q"}
  ],
  "lh": [{"p": "C3", "d": "h"}, {"p": "G#3", "d": "h"}]
}},
{"bar_num": 2, "voices": {
  "rh": [
    {"p": "G#5", "d": "q"},
    {"p": "Bb5", "d": "q"},
    {"p": "G#5", "d": "q"},
    {"p": "F#5", "d": "q"}
  ],
  "lh": [{"p": "Bb2", "d": "h"}, {"p": "E3", "d": "h"}]
}},
{"bar_num": 3, "voices": {
  "rh": [
    {"p": "E5",  "d": "q"},
    {"p": "D5",  "d": "q"},
    {"p": "C5",  "d": "h",  "dyn": "pp"}
  ],
  "lh": [{"p": "C3", "d": "h"}, {"p": "G#3", "d": "h"}]
}}
```
Every note is from {C, D, E, F#, G#, Bb}. The LH uses augmented chords (C–E–G# = augmented triad; Bb–D–F# = same augmented triad enharmonically). Three bars of suspension, then the passage must resolve INTO normal tonal language — the whole-tone section has no internal cadence structure. **Do not end a section in the whole-tone scale**: it cannot cadence to a tonic. Use it as a transition passage of 2–6 bars, leading INTO a tonal resolution.

---

## How to Use This Library in Composition

**Step 1**: Identify what the current bar needs to do emotionally and harmonically.

**Step 2**: Choose the technique from this library that serves that need:
- Tension and lean → Appoggiatura or Suspension
- Grief, inevitability → Lament Bass
- Building toward peak → Ascending Sequence
- Surprise and emotional reversal → Deceptive Cadence
- Pathos at a cadence → Neapolitan approach
- Final closure → Cadential 6/4
- Folk atmosphere → Pentatonic Melody + Drone Bass
- Modal folk brightness → Dorian Mode phrase
- Impressionist shimmer → Parallel Chord Movement
- Dreamlike suspension → Whole-Tone Passage

**Step 3**: Adapt the example to your key and voices. Every example here is in a specific key — transpose the pitches as needed (shift every note by the same semitone interval).

**Step 4**: Connect the techniques with voice-leading. Each technique has a start note and an end note for each voice. The next technique begins from those end notes.

A phrase is a sequence of techniques connected by voice-leading. A melody is a sequence of phrases connected by register and direction.
