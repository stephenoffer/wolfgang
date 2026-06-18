# Webern — Composition Guide

## Fingerprints
Any section claiming Webern's style needs ≥3 of these 5 present.

1. **Extreme brevity — the haiku principle** — Webern's entire output fits on a few CDs. His pieces are extraordinarily short: Symphony Op.21 is under 10 minutes; the Five Pieces Op.10 for orchestra total under 4 minutes. This is not minimalism — it is compression. Every note carries an enormous amount of information because there are so few of them.
2. **Pointillism — single notes in isolated voices** — Webern fragments melody across instruments so that no single instrument plays more than 1–2 consecutive notes before passing to another instrument. A "melody" may consist of one note in the flute, one in the harp, one in the violin, one in the horn. The melodic line is heard by the listener but played by no one alone. This technique is called Klangfarbenmelodie (tone-color melody).
3. **Silence as primary structural material** — More than any other composer, Webern uses silence. Between each Klangfarbenmelodie note: a rest. The rests are as long as the notes, or longer. The silence is not empty — it is the space in which each note resonates and dies.
4. **Perfect symmetry and palindrome** — Webern's serial works are often perfectly symmetrical: the second half of a movement is the retrograde of the first half (palindrome). The structure can only be perceived on paper, not by the ear — but it is absolutely there. Structural perfection as an aesthetic value.
5. **Twelve-tone serial method — strict application** — Webern applies serial technique more strictly than Schoenberg or Berg. His rows are often themselves symmetrical (a row built from repeated interval patterns), and the serial transformations (P, R, I, RI) are used in a highly organized, almost mathematical way.

## Pattern Directives

**Pointillistic Klangfarbenmelodie:**
- Choose 5–8 different instruments.
- Assign one note to each instrument: each note a different pitch, different register, different octave.
- The notes form a recognizable melodic direction (ascending, descending) but are distributed.
- Between each note: at least one beat of rest in all instruments.
- The "melody" is assembled by the listener, not by any single instrument.

**Extreme brevity:**
- An entire "movement" in Webern may be 8–16 bars.
- Each note event must carry maximum information: specific dynamic (pp? ppp? sfz?), specific articulation (staccato? tenuto?), specific register.
- Nothing is left vague.

**Symmetrical row:**
- A row that generates its inversion from itself: the second half is the retrograde inversion of the first half.
- Example: C-Eb-G-Db-Ab-Bb (first half) → E-A-F-D-F#-B (second half, which is RI-6 of the first half).

**Silence structure:**
- Write 4 notes. Then 4 rests of equal length. Then 4 notes in retrograde. The silence is as long as the music.
- `{"p": "rest", "d": "q"}` in every instrument voice simultaneously.

## Anti-patterns (what sounds wrong)

- **Long melodic lines in a single instrument.** In Webern, no single instrument carries melody for more than 2–3 notes consecutively.
- **Dense, continuous texture.** Webern's textures are very sparse. A passage with all instruments playing continuously is not Webern.
- **Emotional display.** Webern's music is cool, precise, abstract. Romantic emotional expression is absent. His music is closer to mathematics or crystallography than to feeling.
- **Ignoring the serial method.** Webern's post-1924 music is strictly serial. Writing "atonal" notes without following a row is wrong for this period.
- **Long duration.** A "Webern-style" piece that lasts 10 minutes has already become something else.

## ShortScore Field Recommendations

**Klangfarbenmelodie:**
- Assign one note per instrument per "phrase."
- `fl`: `{"p": "G5", "d": "e", "dyn": "ppp"}`.
- `hn`: `{"p": "Eb3", "d": "e", "dyn": "pp"}`.
- `vln1`: `{"p": "B4", "d": "e", "dyn": "ppp"}`.
- `hp`: `{"p": "D5", "d": "e", "dyn": "pp"}`.
- Each in a different measure or after rests.

**Row definition:**
- `"_row": "C-Eb-G-Db-Ab-Bb-E-A-F-D-F#-B"`.
- `"_row_forms": ["P0", "I5", "R0", "RI5"]` — the specific forms in use.

**Silence:**
- `{"p": "rest", "d": "h"}` in ALL voices simultaneously.
- Mark: `"_feel": "silence — the note dies; the next note has not yet arrived"`.

**Dynamics:**
- Webern: pppp to ff. Most notes: ppp.
- Isolated sfz or fz for structural accents: one note, then immediately back to ppp.
- `"expr": "zart"` (tender) — Webern's own marking.
- `"expr": "äusserst ruhig"` (extremely quiet) for sustained passages.
