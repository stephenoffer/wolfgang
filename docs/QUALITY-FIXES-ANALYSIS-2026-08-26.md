# What the system could not hear — analysis and guidance, 2026-08-26

Companion to `QUALITY-FIXES-2026-08-26.md` (notation, expression, the dead-code
findings) and `AUDIT-CORPUS-2026-08-26.md` (corpus, harmony, briefs). This pass
covers the **musical analysis layer and the guidance the composer reads**: the
questions a musician asks on opening a score, none of which anything in the
system could answer, and the numeric targets the composer was told to hit, four
of which no real composer has ever met.

**Method, throughout.** Nothing here was allowed to warn until it had been run
over real music and shown not to reject it. The corpus was 20–24 canonical
movements from `tools/reference_scores/` — Mozart piano sonatas, Beethoven piano
sonatas, Chopin mazurkas, 64 bars each. Three harnesses under
`pytest -m calibration` keep it that way.

Two things I was confident about turned out to be wrong, and both are recorded
below, because acting on either would have made the music worse.

---

## 1. The guidance was telling the composer to write music no one has written

This is the largest finding of the pass, and it is not a code bug — it is the
instructions.

`human-sounding-music.md` lists numeric targets under "AI Music Tells", and
`review_style_gate.build_style_targets_from_dna` restates several as scoring
targets. Measured against 24 real movements:

| target the composer is told to hit | share of REAL movements that FAIL it | real median |
|---|---|---|
| `density_cv > 0.5` | 92% | 0.37 |
| chord share `> 20%` | 58% | 0.148 |
| distinct bass roots/bar `> 0.3` ("4 per 8-bar phrase") | **100%** | 0.154 |
| LH unique patterns/bars `> 0.6` ("5+ patterns, change every phrase") | **100%** | 0.254 |
| direction changes/bar `> 0.8` | 0% ✓ | 2.5 |

Only the last survived.

The two 100% failures are the damaging ones, because of *what* they ask for.
"Four distinct bass roots per 8-bar phrase" forces a chord change every other
bar. "Five distinct LH patterns, change at every phrase boundary" forces the
accompaniment to churn. Real music does neither: roughly one new bass root every
six to seven bars, and three quarters of Chopin's bars reuse a figure already
heard. A restless, unsettled surface is itself one of the loudest machine tells —
so the guidance was manufacturing the defect it was written to prevent.

The same fault, worse, in the review gate's own targets. Measured with
`style_analyzer.analyze_score` over 20 real movements — its own function, so the
comparison is apples to apples:

| gate target | asked for | real median | real range |
|---|---|---|---|
| `texture_change_pct` | **52.0** | **20.5** | 4.7 – 61.3 |
| `rest_ratio` | 8.0 | 17.1 | 4.3 – 28.9 |
| `dynamic_markings_per_bar` | 0.15 | 0.77 | 0.06 – 2.22 |
| `stepwise_pct` | 45.0 | 58.7 | 35.5 – 76.4 |
| `chromatic_pct` | 12.0 | 26.3 | 10.7 – 85.4 |
| `rhythmic_variety` | 5.0 | 8.5 | 5.0 – 12.0 |
| events/bar fallback | RH 8 / LH 6 | RH 5.1 / LH 4.1 | — |

`texture_change_pct` is the 2026-08-18 audit's finding E5 confirmed with data:
the gate asked for two and a half times the real rate. Nine of eleven targets
were wrong, almost all in the direction of "busier than any real score".

**Fixed:** every number rewritten from measurement, with the derivation in the
comment beside it. `human-sounding-music.md`'s four false targets replaced by
per-composer measured ranges, each stated as a description rather than a goal,
and the file now closes with *Do not compose to a number* — that a measurement
should change what you write only when it says the music is outside the
repertoire's whole range, not when it differs from an average.

**Pinned:** `test_corpus_style_targets.py` fails if any gate target's ±2σ band
excludes the real median, with a named check for the texture-change regression.

---

## 1b. The comparator ignored the spread it was given

Fixing §1's numbers exposed a deeper fault, and it was mine to find only because
I checked my own work the same way: after rewriting every target from
measurement, **19 of 20 real movements still failed at least one metric.**

Two causes, one behind the other.

The bands were too narrow for genuinely wide distributions. `triplet_pct` runs
0–74 in the repertoire, `chromatic_pct` 10.7–85.4. A correct centre with a
plausible-looking spread still rejects most real music.

But widening them changed nothing, because **`style_comparator` never consulted
the spread.** `target_stdev` was read from the target, stored in the report, and
printed by the CLI — and every verdict came from `|composed − mean| / mean`
against one flat 35% threshold shared by every metric. So a real movement with
no triplets diverges 100% from a mean of 16 and fails, while a metric that
naturally varies by a few percent is waved through at 34% off. No width of band
could help, because the width was never read.

Verdicts now come from a z-score when a target carries a spread, falling back to
relative divergence when it does not. Result on the same 20 real movements:
**19 of 20 failing → 1 of 20.** A deliberately mechanical score — no rests, one
duration, no dynamics, flat density, 98% stepwise — still fails.

**The lesson I had to apply to myself.** My first calibration test asserted that
the real *median* fell inside each target's band. That is much too weak, and it
passed while the gate was rejecting the entire repertoire. The test that finds
this is the one that scores whole real movements end to end, which is now what
`test_corpus_style_targets.py` does — along with a check that the gate still
rejects mechanical music, so "loosen until real music passes" cannot quietly
become "disable".

### What the fixed gate says about the piece

All 13 metrics PASS. That is not the gate failing to notice something: it is the
honest finding that this piece's problems are **not aggregate statistics**. Its
theme never returns, its page carries no articulation, four of its cadences do
not match the plan, and its texture never varies — none of which any aggregate
metric can see. It confirms from a third direction what this project already
recorded twice: aggregate density can match while the idiom does not, and metric
whack-a-mole is a ceiling rather than a path.

---

## 2. The musicality scores penalized real music

`musicality.py` returns 0–1 scores that feed `self_evaluate`, which the critic
reads. Three bands put real music *outside* the range that scores 1.0:

| score | band that scored 1.0 | real median | effect |
|---|---|---|---|
| `rest_ratio` | 3–15% rest time | **16.3%** | typical writing marked down for breathing normally |
| `direction_changes_per_bar` | 1.0–2.0 | **2.05** | the median sat at the edge; the liveliest real movement scored **0.3** |
| `rhythmic_variety` | entropy ÷ 3 bits | ceiling **2.69 bits** | a full score was unreachable; the median real movement scored 0.65 |

After recalibration real music scores 1.00 / 1.00 / up to 0.998.

One thing that was already right and is now confirmed: the melodic interval
priors (65% stepwise / 25% small leap / 10% large leap) measure 65/24/11 in the
repertoire. Left untouched.

**Pinned:** `test_corpus_musicality_bands.py`, including a test that a full score
is reachable at all — a ceiling no real movement can reach is a mis-set
normalizer, not a high standard.

---

## 3. Nobody could hear the ornaments

The critic judges by listening to the MIDI preview. Ornaments were written into
the score as symbols and never realized as notes. On the test piece: **29
ornaments across 41 bars, 0 of them audible.** A trill engraved a `tr` and played
one plain note. Appoggiatura and acciaccatura rendered identically, so the
leaning dissonance that carries most of the expression in a Classical slow
movement sounded exactly like the ornament that deliberately takes no time.

`ornament_realization.py` realizes trills, mordents (both directions), turns
(both directions and both placements), slides, appoggiaturas and acciaccaturas.
Period practice rather than the modern default: a Baroque or Classical trill
**starts on the upper note**, on the beat, and ends with a closing turn so it
lands instead of running out; a Romantic one starts on the principal. Neighbour
notes come from the key's own scale, so a trill on the leading tone is a semitone
and one on the mediant is a tone. Speed scales with tempo, floored at a 64th per
alternation — below that there is no trill, only a smear.

On the test piece: 12 realizable ornaments → **100 sounding notes**.

---

## 4. The questions a musician asks had no answers

Five analyzers, each answering a question nothing in the system could:

| module | question | falsification result |
|---|---|---|
| `counterpoint.py` | parallels, leading tones, sevenths, spacing, voice independence — in the *real* texture | 41 errors → **0** on 770 canonical bars |
| `voicing.py` | how thick, how wide, where does the texture hold and change | thresholds set below the minimum of 22 real movements |
| `cadence_analysis.py` | what actually closes each phrase, does it match the plan, are they all the same | **15/15** real movement endings read correctly |
| `theme_planner.analyze_theme` / `theme_recurrence` | is the theme a theme, does it come back | — |
| `musical_report.py` | all of it, in sentences, for the critic | — |

### The falsification that mattered most

The first counterpoint pass reported **41 errors and 292 warnings across 770 bars
of real Mozart, Beethoven and Chopin.** Two causes:

- **217 "parallel octaves" were octave doublings.** Real Mozart doubles the
  melody at the octave constantly. A pair of voices locked in octaves is *one
  line written twice*, not two voices in parallel — `find_doubled_pairs` now
  recognizes that.
- **185 "falling leading tones" were descending scales.** A descending scale
  passes through the leading tone by definition, and descending melodic minor
  contains one. Only a leading tone *arrived at* — leapt to, or held — owes a
  resolution.

After calibration: **0 errors, 17 warnings** on the same 770 bars. The same
detectors on the generated piece: 0 errors, 1 warning (a real parallel octave at
bar 8).

A detector that rejects the repertoire is worse than no detector, because it
teaches the composer to write blander music. This is the project's standing rule
and it earned its keep twice in one afternoon.

### What the report says about the original piece

Run unedited on `mozart-andante-fmaj-20260825`:

```
THEME     ! the principal theme appears in 1 place in the whole piece
          ! 5 consecutive steps in one direction — a scale passage, not a shape
CADENCES  · bar 14: planned PAC, wrote PLAGAL (IV-I)      [4 plan mismatches]
          ! the piece ends with an IAC rather than a PAC
TEXTURE   ! simultaneity CV 0.19 (Mozart never below 0.22)
THE PAGE  ! not one articulation mark in the whole piece
          ! no ties anywhere
PART-WRITING  ! bar 8: parallel octaves, 55->53 against 79->77
```

Every line is a musical fact, not a distance from a distribution. A test asserts
no `z=` or `sigma` reaches the critic: handing a composer a z-score turns
composition into metric whack-a-mole, which this project has already established
is a ceiling rather than a path.

---

## 4b. The craft checklist failed real music too

The same fault as §1, in code rather than in prose. `CraftChecker` runs a
phrase-sanctity checklist on every phrase. Over 126 real 8-bar phrases:

| check | passed before | passed after | why it was wrong |
|---|---|---|---|
| `has_memorable_detail` | **0 of 126** | 99.2% | looked in `ornamental_surface`, a layer nothing populates |
| `accompaniment_responds_to_melody` | 31.0% | 100% | `len(response_layer) >= 4` — empty for any single-stream left hand |
| `harmony_is_voiced` | 55.6% | 97.6% | counted events in `response_layer`/`counter_reply`, so chords in `bass_foundation` were "unvoiced" |
| `entry_exit_earned` | 75.4% | 100% | indexed the melody in **list** order, not time order, and demanded the last event be a note |

Three of the four were reading *which layer a note was filed under* rather than
the music — the phantom-bass-line lesson again: a statistic taken off a broken
layer is not evidence about the notes. They now ask about the sound: is anything
sounding three-deep at any point, does an accompaniment exist and do more than
one note per bar, does the phrase begin with sound and reach a sounding note.

`has_memorable_detail` was rewritten around what actually makes a phrase
distinctive — an expressive leap, a note twice the phrase's usual value, an
interior silence, a notated ornament or articulation *anywhere* in the texture,
a dynamic that moves — rather than around one unpopulated layer.

The discrimination survives: a phrase of one repeated note with no accompaniment
still fails 7 of the 9 checks. `test_corpus_craft_checks.py` pins both halves —
real music passes, empty music does not.

---

## 4c. Seven subsystems have never produced anything

A census across all 12 workspace pieces (164 phrases, five months of output),
asking of every documented field: has this *ever* held a value?

| field | pieces/phrases with anything |
|---|---|
| `cross_scale_ledger` | **0 / 12** |
| `style_review_reports` | **0 / 12** |
| `control` (PhraseControlIR) | **0 / 164** |
| `sketch_candidates` | **0 / 164** |
| `onset_bundles` | **0 / 164** |
| `candidates` | **0 / 164** |
| `craft_check` | **0 / 164** |
| `sketch` | 10 / 164 |
| `review` | 10 / 164 |

### The ExpectationLedger

CLAUDE.md lists it among the core design principles — "the system's working
memory of unfinished musical business", carrying promises, debts, cooldowns and
locks so a piece coheres at long range. It has never held one entry.

The 2026-08-18 audit filed this as C21: population failures hidden by a bare
`except Exception: pass`. **That was a misdiagnosis, and the correction matters
more than the original finding.** Nothing ever raised. Planning guards every
write with `if _cross_ledger is not None` / `elif _ledger is not None`, and a
fresh `PieceGraph` has `cross_scale_ledger = None` and no `expectation_ledger`
attribute at all. Both guards are False for every section, the block runs to
completion, and nothing is recorded. There was no ledger to populate.

A second defect sat behind it: the graph field is typed `Optional[Dict]`, the
*serialized* form, so even a created ledger would not survive `save` — and a
subsystem for carrying expectations across time that loses them at the first
save is the same as not having one.

`ensure_ledger(graph)` / `persist_ledger(graph, ledger)` make the object exist
and reach disk, restoring a persisted ledger so promises survive movement
boundaries. `ledger_summary` reads both the live object and the stored dict:
reading only the live one reported "no ledger" on a freshly loaded graph whose
expectations had in fact survived.

### The craft checklist

`craft_check` is written in exactly one place — inside `run_scales_section`, the
**engine fallback path**, which CLAUDE.md states the default flow never takes.
So the phrase-sanctity checklist has never been applied to an agent-authored
phrase, which is every phrase the system actually composes.

This is also the explanation for §4b: a check that never runs cannot be observed
to be wrong. Four of the nine had been broken for as long as they had existed,
and one of them could not be passed by any music at all.

`check_phrase(layer_ir)` now returns `(check, findings)` where findings are
sentences a composer can act on, ordered worst-first, and the report runs the
checklist over every phrase — reporting a fault that recurs across phrases once
with a count, rather than forty copies of the same sentence.

### The generalisable check

A documented subsystem holding zero values across every piece ever produced is
vestigial, whatever the documentation claims. That question — *has this ever
held a value?* — takes about twenty lines of script and found seven of them here,
after two earlier sessions had each found one by accident.

---

## 4d. Three of my own detectors were wrong, and the repertoire found all three

Recorded in detail because the pattern is the most transferable thing in this
document: **a detector's own author is the worst-placed person to spot its false
positives.** Each of these survived my own review and died on contact with real
music.

**The hand-span check counted everything *sounding* together.** The reasoning
seemed sound — a note sustained under a later one is the commonest way a stretch
appears, and the existing playability check compares only identical onsets, so it
misses them. But a low bass note held under a chord the hand plays higher up is
the ordinary pedal-point idiom: released by the fingers, held by the pedal.
Measured that way, real Mozart, Beethoven and Chopin produced **211 "unplayable"
stretches across 1,027 bars**, median widest span 28 semitones. Now only
simultaneous *attacks* count, at a threshold of 16 semitones taken from the
distribution (real median 8, p95 12, p99 16). A test of mine had asserted the
wrong behaviour and is now inverted, with the reasoning recorded in it.

**A bug I introduced, then measured through.** Splitting overlapping notes of one
layer into strands named them `principal_line@1`, but `_hand_of` stripped only
the `#` suffix, not `@` — so every strand of a melody overlapping itself, which
is most sustained melodic writing, was counted as a **left-hand** note. It skewed
both hands' density figures and put phantom 17-semitone stretches in the left
hand of real Chopin. The `CORPUS_TEXTURE` baselines were re-measured afterwards:
Mozart's right-hand density 1.15 → 1.22, single-line-RH 0.79 → 0.62. The earlier
figures — quoted to the composer as fact — had been measured through the bug.

**The falsification test itself was wrong.** Its first version judged Chopin
mazurkas against the *Classical* floor and duly complained about 5 of 16 real
movements. That is precisely the mistake the style-aware floors exist to prevent:
Chopin's simultaneity CV reaches 0.17 and Mozart's never drops below 0.21, so one
floor cannot serve both. The test now judges each movement against its own
period.

Three corrections, two of which reversed a conclusion I had been confident enough
about to build on.

---

## 4e. Orchestral parts were written to the edge of what an instrument can produce

Audit item E14. `INSTRUMENT_RANGES` gives the notes an instrument *can* sound,
and the orchestration planner clamped every octave transfer to those limits — so
material that did not fit landed in the weak bottom or the effortful top of
whichever instrument received it. Legal, and miserable to play.

Two distinctions were missing, and both are ordinary orchestration:

**Practical versus physical range.** Every wind instrument's bottom minor third
is unwieldy and its top is effortful; strings are far more forgiving and only
their very top is awkward. The trims are small — a tone or two off each end for
winds, a fifth off the top for strings — and parts are now fitted inside them.
An instrument with no entry is used unmodified rather than guessed at.

**What a dynamic costs at the extremes.** A flute's low octave will not speak
quietly. A trumpet, horn, trombone or oboe cannot be played pianissimo at the top
of its range at all. Ask for it and the part simply comes out louder than
written, which unbalances everything around it — a quiet orchestration that is
not quiet. `practical_range(instrument, dynamic)` takes another fourth off
whichever end refuses.

`audit_orchestration(parts)` reads each part's own written dynamics, so a note
comfortable at forte and impossible at pianissimo is judged against the dynamic
actually in force, and the findings reach the critic through the report. Advisory
throughout: a shrieking piccolo at a climax is a choice, and this exists so a
reviewer can tell a deliberate extreme from an accidental one.

---

## 5. Two things I was wrong about

Recorded because both were about to drive work in the wrong direction, and
because the pattern — an eye-diagnosis that measurement refutes — is the reason
the falsification step exists.

**"The texture is thin."** The right hand averaged 1.13 notes per attack, next to
a hand-composed 2.02 that had once fixed a different piece. But real Mozart's
median is **1.15**. The texture was not thin; it was Mozart-thin. Chasing
thickness would have produced a piece less like Mozart, not more.

**"The texture is restless."** It changed at 62% of bar boundaries. Mozart's own
range is **0.37–0.67**. Also normal.

What measurement *did* find, and what the eye had not: **simultaneity CV 0.19,
against a Mozart floor of 0.22 and a real-corpus floor of 0.16.** The number of
notes sounding at once barely varies from bar to bar — the texture never thickens
at a climax or thins into a cadence. That is the one texture measurement outside
the repertoire, and it is the variance, not the average, that was missing.

The style-aware floors in `voicing.py` exist for exactly this: judged against the
union of all three periods the piece passes, because Chopin reaches 0.16. Judged
against Classical practice it does not.

---

## 6. One field, two meanings

`principal_theme_id` had come to hold two incompatible kinds of name: a **motif**
id after election (`scales.py`), and a **phrase** id with a `__theme` suffix
after a theme capture (`theme_planner.py`). Consequences, both silent and both
permanent:

- `composition_brief.py:1072` compares it to `slot.phrase_id` to ask "is this the
  principal theme's own phrase?" — comparing a motif id to a phrase id, so the
  answer was **always False**;
- `composition_brief.py:2118` looks it up in the motif bank — after any theme
  capture it was not there, so the brief **fell back to `motifs[0]`** and showed
  the agent a motif that was never elected.

`capture_theme_surface` no longer overwrites the field. It records the source
phrase separately and fills the motif id by election only when empty. New
`principal_theme_phrase(graph)` and `phrase_carries_theme(graph, phrase_id)`
resolve any convention including already-saved graphs, and survive a save/load.

Duplicated names for different things is this repository's most reliable bug
generator; this is the fourth instance found.

---

## 7. Two audit items still live, now reproduced and fixed

Both from `AUDIT-2026-08-18.md`, both still present:

**C16 — every developed theme was spelled in flats.** A theme in E major came
back as `E5q Gb5q Ab5q A5q`: wrong accidentals and a wrong harmonic reading of
the agent's own principal theme, every time it was developed. Now spelled in the
theme's key.

**C17 — `augment` doubled durations without re-barring.** A four-quarter theme in
4/4 came back as eight beats and overflowed its own phrase. And a related bug the
audit did not catch: the duration tables were a seven-entry dict plus its
reverse, so augmenting or diminishing a theme written in **triplets, 32nds, 64ths
or double-dotted values returned it unchanged** while the brief told the agent it
was an augmentation. Both tables are now derived from `DURATION_VALUES`, so every
code round-trips.

---

## What is still wrong

**The theme is a scale and it never returns.** `analyze_theme` reports five
consecutive steps in one direction; `theme_recurrence` finds the theme's shape in
exactly one place — the section it was captured from. No code change fixes this:
a memorable theme is a compositional act, and the system can now *say* the theme
is unmemorable without being able to invent a better one. What the tooling
contributes is that the critic is now told, in words, rather than being handed a
score and asked to notice.

**The measurements cannot hear the music.** Everything here reports facts about
notes. A phrase can satisfy every one of them and still be dull, and the ear
outranks the numbers whenever they disagree — which is why every finding in
`musical_report` is phrased for a musician to overrule.

---

## Falsification harnesses

Run with `pytest -m calibration` (~2 minutes):

| harness | what it prevents |
|---|---|
| `test_corpus_counterpoint.py` | part-writing detectors drifting back into rejecting the canon (0 errors, ≤0.05 warnings/bar over 770 real bars) |
| `test_corpus_cadence.py` | a cadence reader that cannot read real cadences, or that answers PAC for everything |
| `test_corpus_style_targets.py` | a gate target whose ±2σ band excludes the real median |
| `test_corpus_musicality_bands.py` | a score band real music sits outside, or a ceiling it cannot reach |
| `test_corpus_craft_checks.py` | a craft check canonical music fails — and, in the same file, a check so loose it passes a one-note phrase |
| `test_corpus_voicing.py` | a texture floor drifting inside the repertoire, and real music being told its hands cannot reach |
