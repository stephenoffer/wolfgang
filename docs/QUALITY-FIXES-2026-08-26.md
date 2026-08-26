# Human-likeness / authenticity fix pass — 2026-08-26

Continuation of `QUALITY-FIXES-2026-08-25.md`, which recorded the baseline read
of `workspace/mozart-andante-fmaj-20260825` and stopped there. This pass fixed
what that read found, plus what looking for it turned up.

**Method, throughout:** read the assembled score back off disk bar by bar; measure
the same property on 26 canonical movements (14 Mozart sonata movements, 6 Chopin
mazurkas, 6 Beethoven sonata movements under `tools/reference_scores/`); and only
call something a defect when the generated score sits outside what the real music
does. Two things I was confident were defects turned out to be normal, and are
recorded below as such.

---

## 1. The two largest modules in the quality layer were dead code

`expression_enricher.py` (1,049 lines, 29 passing tests) and `score_realism.py`
(37 KB, 16 detectors) were both complete, both documented in the craft
reference and the critic's prompt as if they were running, and **neither was
called by anything**. `score_realism`'s docstring cited a calibration test at
`tools/tests/test_score_realism_calibration.py`; that file did not exist.

This is the whole explanation for the headline defect. Every score the system
had ever produced carried **zero articulation marks and zero ties**, because the
pass that writes them never ran; and `musical_ear` reported **0 errors, 0
warnings** on an obviously machine-made score because the detectors written to
catch that were never invoked.

| Fix | Where |
|---|---|
| Run the engraver's pass on every agent commit, after the gate, non-destructively | `scales._engrave_phrase`, called from `_gated_commit` |
| Report what it added, so a reviewer can separate engraver from composer | `commit_*` result `["engraving"]` |
| Run the realism audit inside `self_evaluate` | `scales.self_evaluate` → `report["realism"]` |
| `_section_gate` already read `report["realism"]` — it had simply never been populated | (no change needed) |

**Measured on the same 41 bars, same notes, before → after:**

| | shipped baseline | after |
|---|---|---|
| `<articulations>` | 0 | 39 (0.95/bar; real Mozart 0.041–2.24) |
| `<slur>` | 36 | 58 |
| `<wedge>` (hairpins) | 4 | 22 |
| `<pedal>` | 0 | 2 |

---

## 2. Seven of the sixteen realism detectors fired on canonical music

A detector that flags what real composers write does not measure the music, it
measures the threshold. Run against the 26 reference movements, the shipped
detectors fired like this:

| detector | fired on | why it was wrong |
|---|---|---|
| `dynamic_terracing` | **26/26** | It asked whether the score had hairpins. The Humdrum importer never creates wedge spanners, so the answer was always no — it was measuring the file format. |
| `repeated_bars` | **20/26** | Verbatim bar repetition is how real music is built: median **38%** of a staff's bars, max 91%; the most-repeated bar recurs a median of 4 times, max 16. |
| `rhythm_vocabulary_poverty` | 9/26 | Bound at 70% dominant duration; real staves run to **95%** (a mazurka accompaniment really is one value). |
| `closing_gesture_absent` | 8/26 | Read the highest-numbered measure — often an empty trailing barline from the import — and required 3 quarter-notes of duration, which no ending in 2/4 can meet. |
| `voicing_poverty` | 3/26 | Bound at 0.97 single-note melody attacks; real max is **0.980**. |
| `tie_absent` | 2/26 | Two canonical movements contain no ties at all. |
| `articulation_absent` | 1/26 | Bound at 0.05/bar; the real minimum is **0.041**. |

Several docstrings also stated calibration ranges that had never been measured
(`articulation_absent` claimed real movements carry "0.4–2.1 marks per bar";
the measured minimum is 0.041, which is exactly why its bound fired on real
music). All corrected to the measured figures.

After recalibration: **2 of 16 fire on canonical music, both `info` severity**,
and both documented with their measured false-positive rate.

`tools/scales/tests/test_score_realism_calibration.py` is the harness the
docstring had been promising. It asserts no detector exceeds its tolerated rate,
that anything with a known false-positive rate is `info` only (checked on the
parse tree), that nothing in the module can emit `error` severity, and that
`realism_report` is still wired into `self_evaluate`.

### What this found that was actually wrong

`register_stasis` was bounded at 17 semitones — comfortably below anything real,
and therefore below the output it existed to catch. Real movements span **24–49
semitones** in the melody staff (median 32.5); the narrowest, a Chopin mazurka,
is exactly two octaves. The generated andante spanned **19 across 41 bars**. The
detector said nothing. Rebounded to 24, it now fires on the generated piece and
on none of the 26 real ones.

With the graph passed, `cadence_formula` also fires: *7 of 9 phrase endings use
the identical cadential rhythm.* That was the headline defect in the baseline
read, and nothing in the system had ever reported it.

### Two things I was wrong about

- **Verbatim bar repetition is not a defect.** The generated piece repeats 22% of
  its bars; real movements run 1.4–27.2%. I would have added a rule against it.
- **Missing hairpins are not a defect for Classical music,** and cannot be
  calibrated from a Humdrum corpus at all.

---

## 3. The documented pipeline could not run

Every code snippet in every skill, agent and workflow file invoked `python3` —
which on this machine is Homebrew's interpreter, with neither `music21` nor the
`scales` package. Because `assembler.py` imports music21 lazily, the import
succeeded and the *call* raised `ImportError: music21 is required for assembly`.
So assembly, MIDI preview and `self_evaluate` — the entire back half of the
pipeline — failed for an agent following the documentation exactly, and failed
late.

- **37** occurrences of `python3` → `.venv/bin/python`, across 12 files.
- **31** `sys.path.insert(0, 'tools')` shims removed; the package is installed
  editable and CLAUDE.md's packaging section already said so.
- `test_documented_snippets_run.py` fails on a bare `python`/`python3` or a
  reintroduced shim in any `.claude` file, and separately asserts that the
  interpreter the docs point at really can import music21.

---

## 4. Load-drop bugs: state that survived the write and vanished on the read

Hand-enumerated loaders are this repo's most productive bug source and the
failure is always silent.

| Model | Fields dropped on every load |
|---|---|
| `SketchIR` | `texture_plan`, `expression_marks`, `motif_placements`, `entry_signature`, `exit_signature` |
| `MovementContract` | `sections`, `theme_families_active`, `development_strategies`, `recap_logic`, `coda_logic`, `contrast_with_previous`, `orchestration_zones` |
| `SectionContract` | `orchestration_role_map`, `theme_families_active` |
| `TonalItinerary` | `key_relationships`, `progressive_tonality` |

All converted to the field-driven `_dataclass_from_dict`. Converting `LayerIR`
to it then exposed a deeper bug in that helper: it recursed into `List[X]` and
into a bare dataclass, but **not** into `Optional[List[X]]` or
`Dict[str, List[X]]` — so every orchestra layer and `inner_voices` (three- and
four-voice counterpoint) came back as **plain dicts pretending to be notes**.
Nothing type-checks downstream; those layers reached the assembler as dicts and
produced no sound. Fixed by routing every field through a new `_coerce` that
handles arbitrary container nesting.

`test_piece_graph_roundtrip.py` fills each model with sentinel values, sends it
through a real save/load, and asserts nothing came back different — so adding a
field to any model is now automatically covered. Two AST guards additionally
fail if any loader re-enumerates a model's field list.

---

## 5. A bare string is a sequence of characters

`compile_style(piece_id, composers="mozart")` — the obvious call, and the one a
reader of the signature makes — compiled six one-letter "composers" (a, m, o, r,
t, z), wrote `tools/compiled_packs/{a,m,o,r,t,z}/` to disk, and resolved the
piece's entire style against the composer `"m"`: tier D, zero fingerprints, zero
cadence rules, zero left-hand textures. The piece still generated. It simply had
no style, and nothing said so.

That call site had been guarded; eight other list-typed tool-surface arguments
had not. All now route through `_as_list`, which coerces the two unambiguous
single-item cases and raises with the argument named for anything else. The six
corrupt packs are deleted.

Normalising `None` to `[]` broke two `is None` default branches
(`orchestrate_section` chose its default ensemble that way,
`commit_candidate_phrase` chose between the shorthand and LayerIR paths); both
fixed, and a test asserts neither can come back.

**Related:** a composer id went straight into a filesystem path unsanitised, so
a blend compiled to `compiled_packs/blend:beethoven+liszt/` — a colon, illegal
on Windows — and nothing stopped a name containing `..` or `/` from walking out
of the packs directory. All seven read and write sites now go through
`style_registry.pack_dir_name`.

---

## 6. Notation and placement

- **Pedal is now a real MusicXML `<pedal>` line**, not the literal text "Ped.".
  The assembler wrote the glyph as a TextExpression because "music21 has no
  PedalMark in this version" — music21 9.9.1 has one, and only the real element
  makes MuseScore draw the bracket and sustain on playback.
- **The engraver was itself producing spam.** It runs once per phrase, so a
  `step = 2` meaning "every other bar" became a full down/change/up pedal cycle
  in every four-bar phrase: 18 "Ped." marks in 41 bars, which `notation_spam`
  duly flagged. "Sparing" now means at most one span per phrase, on the bar with
  the most sustain to give.
- **Three articulation rules put marks in musically wrong places.** An accent
  landed on the theme's trilled melodic peak in all three of its statements,
  because the rule tested "not a strong beat" — but beats 2 and 3 of 3/4 are
  weak *beats*, not syncopations. Tenuto landed on 16th notes inside running
  passages, where the instruction is unplayable. The closing staccato lift
  landed on the last note of an inner voice that stopped mid-phrase. A mark in
  the wrong place is worse than no mark: it is an instruction the player cannot
  make sense of.

---

## 7. Guidance: an abstract curve nobody could act on

The brief told the composer:

```
register arc: [0.67, 1.0, 0.0]
```

Three normalised numbers, with nothing anywhere saying how high "1.0" was in
pitches. So nothing ever acted on it, and the result is measurable — 19
semitones across 41 bars, narrower than any real movement. The ceiling was never
set anywhere, so nobody reached for it.

The brief now carries a concrete `RANGE SO FAR`: the pitches the melody has
actually used, how that compares to the corpus, and — at the climax — the
specific note the peak must clear. Plus new instructions, all with their
measured numbers, in the brief block, the craft reference, the phrase-composer
agent and the critic: use the whole keyboard, vary the cadence, tie across
barlines, don't walk scales.

Two surfaces claimed these numbers came from "60 canonical movements"; the
harness measures 26. Corrected, and a test now fails if any guidance file quotes
a corpus size the harness does not have. The craft reference's §6b also sat
between §4b and §5 — before both §5 and §6, while covering §6's subject — and
has been merged into §6; tests guard section ordering, uniqueness, and that
every `§N` cross-reference in every file resolves.

---

## What is still wrong, and why it is not a code fix

Re-auditing the same 41 bars after all of the above, three findings remain, and
all three are the composer's decisions rather than the pipeline's:

- `register_stasis` — 19 semitones.
- `cadence_formula` — 7 of 9 phrase endings identical.
- `scalar_overuse` — 39% of melody bars are plain scale runs (real: 0–15%).
- `tie_absent` — nothing crosses a barline.

The engraver deliberately does not fix these. It fills in blanks; it must never
change a pitch or a duration, and a tie changes what sounds. What has changed is
that all four are now *surfaced* — to the commit result, to `self_evaluate`, to
the section gate's advisory list, and to the fresh-ears critic, with the corpus
numbers attached. Before this pass the measurement layer reported nothing at all
on a score that had every one of them.

Confirming the improvement in composed output needs a fresh agent run; the
before/after table in §1 is on identical notes and isolates the pipeline's
contribution only.

---

## 8. Style references were silently given Classical data

`PhraseBank` and `TransitionBank` each carried a byte-identical
`_load_transition_matrix`, and both fell back to
`pattern_library/transitions/by_genre/**classical**.json` for every composer —
while genre matrices for baroque, romantic, late-romantic, impressionist,
modern, minimalist, nationalistic and film-score sat unread beside them. So a
Bach piece with no composer matrix, and every `style__<name>` reference, was
handed Classical texture-transition odds. In the one place whose entire job is
style fidelity.

Both now delegate to a single `style_registry.load_transition_matrix`, which
resolves the composer's real genre. Verified: `style__romantic` loads the
romantic matrix (4,639 transitions), `style__baroque` the baroque one (5,250);
both previously loaded classical (13,317).

**Liszt was missing from `_STYLE_MEMBERS` entirely** while being one of only
twelve *armed* composers — so "compose in a romantic style" drew on Chopin,
Schubert and Weber and quietly ignored the whole Liszt corpus. Eleven other
composers with compiled packs were likewise unclassified. All added, and a test
now fails if any compiled pack has no style.

## 9. Guards for the failure mode that caused all of this

The most expensive defect in this pass was not a wrong line of code. It was two
finished, well-tested, thoroughly documented modules that nothing called — and
a green test suite that said nothing, because every unit test built its objects
in memory.

`test_no_dead_modules.py` closes that: if `CLAUDE.md` lists a module, either
something imports it (Python, or a `.claude` skill/agent/workflow), or its entry
says plainly that nothing does. `performance_bank.py` and `transition_bank.py`
are called by nothing and now say so; `performance_renderer.py`'s docstring
claimed a `PerformanceBank` dependency it does not have, which is corrected.
`test_score_realism_calibration.py` additionally fails if any single detector is
defined but never run by `realism_report` — the same failure at one-detector
granularity, quieter and just as real.

## 10. Smaller fixes

- The panel judge picked a winner from an **unengraved** preview — no
  articulation, no phrasing, no pedal — and only the winner was engraved on
  promotion. Candidates are now engraved too, so the judge compares what ships.
- `self_evaluate`'s hint for `texture_change_pct` told the critic that real
  music "changes texture between ~40-70% of consecutive bars" — the very band
  the comment three lines above records as having rejected 20 of 24 real
  movements. Corrected to the calibrated 4.5-58.5%, and it now reads
  differently for "too low" and "too high".
- The craft reference's §6b sat between §4b and §5, covering §6's subject;
  merged into §6. Tests guard section ordering, uniqueness, and that every `§N`
  cross-reference in every file resolves to a section that exists.

---

## Verification

451 unit tests and 15 calibration tests pass. The calibration set is the one
that matters here: it parses the reference corpus and fails if any detector
fires on canonical music beyond its documented rate, if the commit gate rejects
real corpus bars, or if a guidance file quotes a corpus size the harness does
not have.

The before/after in §1 is measured on **identical notes** — the same nine
committed phrases, re-engraved and re-assembled — so it isolates the pipeline's
contribution and claims nothing about composition. Whether the composed output
improves is a question for the next agent run, which now has actionable
register targets, five measured instructions it did not have, and an audit that
can see the four defects it used to miss.

---

# Second pass — the doctrine and the corpus behind it

The first pass fixed the machinery. This one went after the *content* it runs
on: the 460 markdown files under `.claude/context/` that are read into every
brief, and the compiled packs and corpus artifacts derived from them.

## 11. Doctrine that contradicted the corpus it described

A number in a doctrine file is an instruction. Seven were measurably wrong, and
two were wrong **in the direction that causes the defects the audit reports**.

| Claim | Where | Measured |
|---|---|---|
| "Beethoven changes texture **58%** of the time between consecutive bars" | `human-sounding-music.md` | **25.5%** over his whole 17,757-bar corpus. Generalised from one movement, and it told the composer to change texture twice as often as Beethoven does — the "different idiom every bar" failure. It also contradicted the calibrated `texture_change_pct` band in `scales.py` outright. |
| "melodies are roughly **70-80% stepwise**" | `melody-craft.md` | **40-79%, median 64.5%** over 26 movements. Aiming at the top of the range is an instruction to write scales — and `scalar_overuse` fires on the last piece at 39% of melody bars against a real median of 2%. |
| "Parallel 3rds and 6ths … up to ~4 consecutive" | `counterpoint-essentials.md` | 43 runs longer than 4 across 15 movements; the longest is **25**. A passage in parallel thirds is a standard device, not a ration. |
| "Every bar should have AT LEAST 2 different bass notes" | Chopin guide | Real Chopin breaks it in **one bar in five**; the sparsest movement satisfies it 20% of the time. |
| "Every 4-bar phrase should contain at least 2 leaps of P5 or wider" | Chopin guide | Satisfied by **68%** of real 4-bar groups (min 42%). |
| "**NEVER** write the LH as single-note arpeggiation only" | Chopin guide | A median **7%** of real mazurka bars are exactly that, and one whole movement runs at 87%. |
| "Minimum 1 dynamic marking per 8 bars" / "at least 1 appoggiatura per 8-bar phrase" / "Plan a voice-count arc: 2→3→4→6→8→6→4→2→1" | `human-sounding-music.md` | Quotas and schedules — the failure mode the same file warns about three sections earlier. |

One claim I expected to be wrong was not: "no more than 4 consecutive notes in
the same direction" sits inside a **species counterpoint** section, where it is
pedagogically correct, and the file already frames species rules as exercises.
Measuring free composition against it was my error, not the file's.

`test_doctrine_matches_corpus.py` now re-derives these from disk, so doctrine
and corpus cannot drift apart silently again.

## 12. Five composers had no cadence doctrine at all

Composer profiles *delegate* shared vocabulary — Bach's `harmonic-language.md`
opens "For shared Baroque harmonic vocabulary (figured bass, **cadence types**,
sequences, voice-leading conventions), see baroque-harmony.md" — and the
compiler never followed the pointer. It read only the composer's own file, so
five of the twelve armed composers compiled to an **empty
`cadence_scripts.json`**, in the one place that addresses the single most
reliable tell that a machine wrote the piece.

Then the lookup that reads them matched labels with a plain substring test:
`"HC" in "HALF CADENCE"` is False. A composer profile writes `HC (->V)`, the
genre files write `Half cadence`, the Renaissance file writes `Clausula vera` —
so even where scripts existed, only Mozart's matched.

| | cadence scripts before | after |
|---|---|---|
| bach | 0 | 7 |
| corelli | 0 | 7 |
| weber | 0 | 6 |
| palestrina / monteverdi | 0 | 13 |
| mozart | 5 | 22 |
| beethoven | 4 | 21 |
| haydn | 3 | 20 |
| chopin | 6 | 12 (and harmonic devices 0 → 7) |
| liszt | 6 | 12 |
| schubert | 4 | 10 |
| handel | 2 | 9 |

Every armed composer now resolves a cadence script for every common cadence
type. Palestrina correctly resolves none for a *deceptive* cadence, which is
right: the Renaissance does not have one.

## 13. A whole period was missing

`style_registry` declared a `renaissance` style with two **armed** composers,
`compiled_packs/style__renaissance/` held their corpus profiles, and there was
no `.claude/context/renaissance/` directory at all. Every genre fallback
therefore handed Renaissance polyphony *Classical* data. Written:
`renaissance-harmony.md` — cadence types (clausula vera, Phrygian, Landini),
dissonance treatment, the modes with their finals and reciting tones, musica
ficta, texture devices, and what not to do in the idiom.

## 14. Genre texture-transition matrices were stale or synthetic

Built once by a migration script and never again. Six of the nine were still
**synthetic** — the Classical matrix with hand-picked multipliers ("baroque:
alberti ×0.3, pedal_point ×1.5") — and the two real ones were each wrong:

- `baroque.json` was sourced from bach + handel + corelli **plus palestrina and
  monteverdi**, folding Renaissance polyphony into Baroque odds.
- `romantic.json` was chopin alone, while schubert, liszt and weber are armed.
- There was no `renaissance.json`, so Palestrina fell through to Classical.

`build_corpus_indexes.py` now derives them from whichever members are actually
armed, and runs after the per-composer matrices it depends on. Result:
renaissance created (63,195 transitions), baroque decontaminated, classical
13,317 → 25,615, romantic 4,639 → 5,555. The six styles with nothing armed are
**skipped honestly** rather than synthesised, and where synthetic data is still
the only option the brief now says so in the text rather than passing it off as
corpus evidence.

Three separate places also hard-coded `by_genre/classical.json` as *the* genre
fallback for every composer — `PhraseBank`, `TransitionBank` (byte-identical
copies of the same loader) and `context_compiler`. All three now resolve the
composer's real genre through one shared `style_registry.load_transition_matrix`.

## 15. The brief overstated its own evidence

Composing "as Corelli" from **19 bars** is a different act from composing as
Mozart from 7,022, and the brief said so only obliquely, through scattered "no
corpus stats for texture X" warnings the agent had to add up for itself.
`composer_coverage_tier` had always known the answer; nothing put it in front of
the composer. Every brief now opens with a `CORPUS COVERAGE` line — tier, bar
count, and what that means for how much weight the exemplars deserve.

A stale `corpus_profile.json` is now ignored rather than trusted, detected from
its metric vocabulary: `self_evaluate` narrows its discriminator bands to
`mean ± 2σ` from those numbers, so a profile written by an older build silently
becomes the standard a section is judged against.

## 16. Multi-voice exemplars bypassed the malformed-bar filter

`_shorthand_beats` had no case for `//`, so the token failed the note regex, the
function returned `None`, and both callers read `None` as "unparseable, don't
judge it". Every multi-voice exemplar therefore skipped the overflow and
underfill guards — which is most exemplars for exactly the composers where it
matters most (a Bach sample averages four voices a bar). Measured across the
armed corpus, 5.0% of the voices handed to the composer did not fill their bar;
after the fix, 2.8%, and all but ~0.5% of the remainder turned out to be my
audit's own arithmetic.

## 17. A discriminator band that rejected Bach

`texture_change_pct` was calibrated on Mozart, Beethoven and Chopin, before Bach
was armed. Bach's corpus mean is **0.622**, above the band's 0.585 ceiling — so
every Bach section would have been reported "texture change high", the
discriminator telling the critic that Bach's actual behaviour is a defect. Per
composer the measured means now span 0.144 (Chopin) to 0.622 (Bach); the band
covers that range.

## What I got wrong in this pass

Worth recording, because the method only works if the misses are counted too.

- I "fixed" `detect_bar_length_errors` to measure the largest `offset + duration`
  instead of `measure.duration.quarterLength`, and wrote a confident docstring
  about the false positive it removed. `Stream.duration` **is** `highestTime`;
  the change was a no-op. The docstring now says so. The two blocking errors on
  canonical music turned out to be Humdrum *import* artifacts (Beethoven Op.2
  No.2/i bar 54 parses as 465 beats in a 2/4 bar), which no measurement of the
  parsed stream can distinguish from a real export bug — recorded as a stated
  limit of the only detector family that can block.
- I reported 31 malformed exemplars before noticing my checker summed both
  voices of a `//` bar, and 4 more before noticing it counted grace notes as
  metrical time.
- I flagged "no more than 4 consecutive notes in one direction" as rejecting real
  music, having measured free composition against a species-counterpoint
  exercise rule that the file already framed correctly.

Each of those took a second look at the actual data to catch, and each would
have shipped as a confident wrong claim.
