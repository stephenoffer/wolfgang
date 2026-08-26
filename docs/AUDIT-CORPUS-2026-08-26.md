# Audit — the corpus was the bug

Date: 2026-08-26. Method: read the note path from raw score to brief, ran the
extractor against the raw `**kern` sources it was built from, and measured every
claim over all 102,439 corpus bars. Nothing below is inferred from docs.

Companion to `QUALITY-FIXES-2026-08-26.md`, which covers the notation and
expression layer. This one covers everything upstream of it: what the system
learns from, and what the composing agent is actually shown.

## The headline

Wolfgang composes from a corpus. That corpus was wrong in three compounding ways,
and every downstream layer — the chord frame in every brief, phrase segmentation,
cadence retrieval, harmonic-colour doctrine, the progression model — read the
wrong values and was correct about them.

| Measure | Before | After |
|---|---|---|
| Bars labelled harmonically "chromatic" | 43,627 / 102,439 (**42.6%**) | 1,010 (**1.0%**) |
| Bars with no harmonic reading | 3,010 (2.9%) | 0.4% |
| Exemplar records short of their own meter | widespread | 81 / 182,013 (0.04%) |
| Roman vocabulary in the progression model | no inversions, no sevenths | full |

---

## 1. Every triplet run in the corpus was half-deleted

`build_full_corpus._timed_records` advanced its beat cursor as a float rounded to
four decimals. A sextuplet's second note sits at offset `1/6` = 0.166666…; the
cursor read 0.1667; the note tested as "already covered by a sounding note" and
was **dropped**, and the note after it then read as a gap and became a **rest**.

K.279/ii bar 79 is eighteen continuous sextuplet-sixteenths in the source
(`A3 E4 C#4 B3 E4 D4 …`). The corpus held nine notes alternating with nine rests.
The brief showed that bar to the composer as an exemplar of Mozart's
accompaniment writing.

Fixed with exact `Fraction` arithmetic throughout. Notated rests are now
authoritative (`_rest_spans`), so a written rest survives and an articulation gap
does not become one — the two had been conflated in both directions.

Also fixed here: a rest running to the barline is now emitted (records sum to the
meter), and adjacent rests are merged (a bar's silence had been arriving as
`2.0 + 1.0`, so every rest count read two events where a listener hears one).

## 2. 42.6% of all bars were labelled "chromatic"

The four commonest "chromatic" chords in the corpus were `I6`, `ii7`, `V7` and
`I64`.

Two independent causes:

- **The function classifier matched the printed FIGURE**, against a list of seven
  bare symbols. `I6` is not in that list. Neither is `V7`, `ii65`, or any flat
  numeral in a minor key.
- **`_span_roman` collected every pitch class sounding anywhere in a beat** and
  handed the set to `music21.roman.romanNumeralFromChord`. Every scale run,
  passing tone and appoggiatura counted as a chord tone. Bar 1 of K.279/i —
  three beats of unmixed C major — came out `I7`; bar 2 came out
  `ii6 / iii43 / I65 / V42`.

Replaced by `tools/scales/harmony_analysis.py`:

- duration-weighted pitch-class profile with a 2× emphasis on what sounds *on*
  the beat;
- nine chord templates scored by covered-minus-foreign weight, with a parsimony
  penalty so a seventh has to earn itself, per-quality priors (a major seventh is
  almost never a functional harmony here), a diatonic-quality prior for when the
  third is not sounding, and a strong root-position bonus;
- a Viterbi pass with a change penalty, because harmonic rhythm is slow and
  reading each beat independently makes a bar that prolongs one chord report
  four different ones;
- direct spelling from (root, quality, inversion) rather than a round-trip
  through figured bass, which is where `iii43`, `#iø` and `iiio64` came from;
- function classified from **structure**, not from the printed symbol.

K.279/i now reads `I / ii6-V7-I-V42 / I / ii6-V7-I-V42`.

`parse_roman` / `spell_roman` round-trip for all 12 degrees × 9 qualities × every
inversion, so no code needs a hand-maintained symbol table again. The two that
did (`harmonic_solver._ROMAN_TO_DEGREE` / `_ROMAN_TO_QUALITY`) listed `viio7` but
not `V7`, and `I6` but not `I64` — so every dominant seventh in every chord frame
silently degraded to a triad and every second-inversion chord to root position.

## 3. The progression model could only produce root-position triads

`norm_roman` stripped every digit before counting: `V7`→`V`, `I64`→`I`,
`ii65`→`ii`. A model built that way cannot express a stepwise bass, which is what
inversions are for.

Its cadence table was trained on the last two bars of each **movement** — about
30 samples per composer — and the commonest approach to a final tonic was,
literally, the tonic. Sampled phrases ended `I–I`: no dominant, nothing resolved.

Fixed: inversions and sevenths preserved; cadences trained on every bar the
extractor marks `cadential`/`closing` (thousands); an order-1 backoff (the
sampler jumped straight from "no order-2 context" to the unigram distribution — a
context-free random chord — which happens on the second bar of every phrase); a
frequency floor that prunes analysis artefacts like `vo` and `II+`; runs split at
mode changes so no transition is invented across a modulation.

Also: `within_bar` patterns were keyed by **how many chords a bar contained** and
looked up by **beat count**, so every 4/4 bar was handed a four-chord pattern and
every 3/4 bar a three-chord one — harmony changing on every beat of every bar.
And the rate was hard-coded `0.5` while its own docstring claimed it used the
corpus. Both fixed; the model now carries the composer's measured `within_rate`
per meter (Mozart: 0.86 in 4/4, 0.71 in 3/4).

---

## What the composing agent was actually being shown

Before: `b1:I=F/A/C  b2:ii=G/B-/D  b3:i=F/A-/C  b4:V=C/E/G` — a minor tonic in
F major, music21 flat spelling the shorthand parser rejects, no within-bar motion.

After: `b1:I=F/A/C  b2[1:IV6=D/F/Bb 3:IV=Bb/D/F]  b3[1:iii=A/C/E 2:ii6=Bb/D/G
3:V=C/E/G]  b4[1:V7=C/E/G/Bb 3:V=C/E/G]`.

Other things the brief was doing wrong, all found by reading one:

- **The piece's motifs never reached it.** `/w-plan` designs MotifObjects with
  contour, rhythm cell and recognition anchor; `resolve_motifs` stores them;
  `theme_planner` writes per-phrase transforms — and the brief never mentioned
  any of it. The agent composing the notes was never shown the piece's designed
  identity. This is a first-order cause of "not memorable": a run of
  individually-plausible phrases with nothing recurring through them.
- **A shadowed variable corrupted every later section.** `for s in
  ch.get("closes_so_far")` rebound `s`, the slot summary, so every line after the
  cadence-history block read a cadence entry instead — the exemplar header said
  "transposed to **None**".
- **Exemplar transposition snapped chromatic notes onto the scale.** The brief
  tells the composer that "a single chromatic note colors the emotional
  temperature of the phrase" and then handed it exemplars with every applied
  dominant, raised fourth and Neapolitan flattened onto the nearest diatonic
  degree. Now exact interval transposition; only a change of MODE alters a pitch,
  and then only the 3rd, 6th and 7th.
- **Every brief printed a glossary as melodic guidance.** The doctrine picker took
  the first two entries from (contour, climax, phrase_structure); phrase_structure
  entries come first in every pack and are definitions — "Melody: Cell: Smallest
  recognizable unit". The six real contour priors never appeared.
- **The LH vocabulary printed Python list syntax** (`['G2', 'G3']q`) for chords —
  unparseable shorthand, so a bar copied from it lost its accompaniment. Same bug
  in the continuity tail (`['E5','G5','B-5']dq` as "the note to connect to").
- **The climax sign was inverted**: phrase 1 of the piece was told it was four
  phrases *past* the peak and must not re-peak.
- **Every phrase got its whole section's intent** — "state the idea plainly AND
  carry it further AND settle the key AND drive the cadence" — plus eleven
  section techniques including mutually exclusive ones.
- **Cadence doctrine was empty or contentless.** The extractor required the word
  "Cadence" in a table's HEADER ROW, so Beethoven's table (headed
  `| Strategy | How It Works | Dramatic Function |`) was invisible and the
  flagship composer shipped an empty `cadence_scripts.json`. Where the pack was
  populated, each row's columns were read into a **bare expression that was never
  assigned**, so every script carried empty approach chords. Mozart's half-cadence
  script now reads `approach I - IV - V, bass degrees 1-4-5`.

## Planning defects

- **`compile_style(piece_id, "mozart")` iterated the string as characters.** The
  parameter is `List[str]`; a bare string compiled seven one-letter "composers"
  and resolved the piece's style to **"m"** — tier D, zero fingerprints, zero
  cadence vocabulary, zero LH textures. The piece still generated; it just had no
  style, and nothing said so. Now coerced, and a style that compiles to nothing
  returns a warning.
- **`rh_distribution` had no producer anywhere.** Nothing ever wrote it, so it was
  `{}` for every composer and the planner's fallback pinned the upper staff to
  `singing_melody` for every bar of every piece ever generated. Now read from
  `corpus_profile.json`.
- **A stale evidence overlay was overriding the flagship composer's textures**
  with labels (`sparse_octaves`, `walking_bass_chromatic`, `oscillation_trill`,
  `unclassified`) that the classifier stopped emitting in April. The planner could
  schedule a texture matching no corpus bar.
- **The corpus transition matrix was dead code.** `_next_lh_texture` read
  `trans["next"]` — a key `_transition_patterns` has never returned — so the
  matrix built to say what follows what was never consulted, and the
  accompaniment cycled through the ranked list by index.
- **Every phrase started from the same texture and changed at the same bar
  index**, which is the "same accompaniment throughout" tell, planned in.
- **Four of eight cadence types fell through to `[tonic]`** — a phrase planned to
  end plagally, evaded or elided got no approach chord at all.
- **Octave oscillation (`F2-F3-F2-F3`) was classified `alberti`** and real Alberti
  (`C-G-E-G`) was not, so every "Alberti" exemplar the brief offered was an octave
  leap.

## Other silent corruptions

- `_normalize_key("b_flat_major")` returned **B major** — a semitone off, and
  every chord frame and key signature derived from it. `f_sharp_minor` returned
  F# **major**.
- `pitch_to_midi("B-5")` (music21's own flat spelling) returned `None`, so any
  pitch crossing back from music21 was silently dropped from role inference,
  melodic statistics and the voice-leading check.
- Two more local duration tables (`corpus_bar_retriever`, `pattern_retriever`)
  snapped every tuplet to a 16th, so a bar of corpus triplets came back a third
  short.
- `musical_ear._tonic_pc` used `music21.pitch.Pitch("F major")`, which raises; the
  bare except returned 0, so every non-chord-tone check on a piece the planner
  keyed "F major" was measured against C.
- `musical_ear` treated the minor scale as natural-only, so every V–i cadence in
  every minor-key piece had its leading tone flagged as a chromatic wrong note.
- `_chord_pcs` read Roman numerals through `music21.roman`, which raises on the
  corpus's own symbols; the bare except returned an empty set and silently
  disabled the detector.
- `corpus_adapter.adapted_bar_to_shorthand` collapsed every chord to one note.
- `style_analyzer` called `sys.exit(1)` at import time on a missing dependency and
  set `warnings.filterwarnings("ignore")` globally for the whole process.
- Silence was excluded from the piece-vs-corpus comparison on a false premise —
  a code comment asserted `analyze_score_bars` does not emit `has_rests`. It does,
  and always has. Never playing is one of the most reliable machine tells there
  is; `rest_bar_ratio` and `rest_event_ratio` are now compared.
- `MotifObject.recognition_anchor` and `accent_profile` were serialized on save
  and dropped on load — a motif came back without the two fields that define its
  identity.

## Guidance that contradicted itself

The agent read these in one context window:

- craft §2 said "the brief gives targets; **meet them**" in its first line and
  "not a total to hit" in its last.
- craft §1's "one rule" was "**never** write notes you have not earned from the
  brief", two paragraphs above "invent freely — your choice per moment".
- `anti_skip.py`'s docstring said `composed_blind` **blocks**; the gate has
  treated it as advisory since the policy changed.
- CLAUDE.md said the commit gate "blocks skeletal density and photocopied
  accompaniment" in one line and that both are advisory in four others.
- The critic and `/w-review` were told `section_gate` "always passes" — it
  hard-fails on physical defects read off the assembled score, which are real.
- The dramatic block restated `ROLE_INTENT` in different words, so every brief
  carried two versions of the same instruction.

## Rebuilding

```
cd tools
python -m scripts.build_full_corpus --reference \
  --music21 bach haydn palestrina monteverdi \
  --local liszt reference_scores/_fetch_liszt
python -m scripts.build_corpus_indexes --force
python -m scripts.build_corpus_profiles
python -m scripts.build_style_profiles
python -m scripts.build_progression_model
```

About 10 minutes. `corelli`, `handel`, `schubert` and `weber` have no
re-extractable sources and keep their older, thinner records (no `roman`);
`build_progression_model` reports them as skipped rather than pretending.

## Not fixed

- Those four composers have no re-extractable sources, and `palestrina`,
  `monteverdi`, `corelli` and `weber` have no written profile at all — armed by
  corpus, silent on doctrine. The brief now says so in its warnings instead of
  omitting the section.
- Pedal marks come out unbalanced (two `Ped.` to one release) in the performance
  layer.

---

## Round 2 — found by measuring, after the corpus was rebuilt

- **Density targets ignored the meter.** `texture_density_stats` pooled every
  meter into one events-per-bar median. Mozart's Alberti bass runs a median of
  **8 events in a 4-beat bar and 6 in a 3-beat bar**; every 3/4 phrase was told 8,
  and the density gate then measured it against the same wrong figure. Scaling a
  per-BEAT median by the beat count is not good enough either — the distribution
  is multimodal (two notes a beat and six notes a beat are both Alberti), so the
  per-beat median lands between the modes and scales to a figure no real bar has.
  Now bucketed by meter, with the pooled figure as the fallback.
- **Same-voice overlap was never enforced**, despite CLAUDE.md listing it as a
  hard physical constraint. Two half notes at beats 1 and 1.5 sum to 4 in a 4/4
  bar and passed the bar-sum check while overlapping by a beat and a half —
  unwritable in MusicXML, and the exporter spills it past the barline. Now an
  error, falsified against pedal-under-figuration, `//` two-voice writing,
  Alberti, chords, ties across the barline, triplets and grace notes (fires on
  none of them).
- **Six anti-pattern detectors skipped every chord.** `not isinstance(evt.pitch,
  list)` meant a chordally-written phrase was invisible to the register,
  silence, restatement, root-position, scalar-fill and safe-harmony checks — and
  `detect_root_position_bias`, which is *about* chords, skipped them. On a
  four-bar chordal test phrase locked in one register on one bass note, all
  three of the checks that should scream returned "insufficient data".
- **`_lh_bar_patterns` read `pitches[0]`** as the bass of a left-hand chord —
  whichever pitch happened to be written first, not the lowest.
- **`ornamental_surface` and `counter_reply` shared treble voice 2**, putting two
  independent lines in one music21 Voice at overlapping offsets.
