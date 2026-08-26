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
