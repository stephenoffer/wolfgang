# Human-likeness / authenticity fix pass — 2026-08-25

Baseline read of `workspace/mozart-andante-fmaj-20260825` (41 bars, F major
andante, solo piano), read back bar-by-bar off the assembled MusicXML. The
`musical_ear` reported **0 errors, 0 warnings** on a score that is visibly,
audibly formulaic. That gap — the measurement layer cannot see the defects that
make output sound machine-made — is the thesis of this pass.

## What the score actually looked like

| Observed | Count | Why it reads as machine-made |
|---|---|---|
| `rit.` / `a tempo` alternating almost every bar | 9 + 9 | No engraved score does this. Marked at each phrase's *first* bar. |
| Cadence bar written as `<note>/half + quarter rest` | 7 of 41 bars | One cadence formula, reused verbatim at every phrase end. |
| LH bar = broken-chord triplet arpeggio | 12 of 41 bars | Single accompaniment idiom for the whole piece. |
| Articulation marks in the whole score | **0** | Real Classical piano writing is dense with slurs + staccato. |
| Ties in the whole score | **0** | Nothing is held over a barline; every bar is a sealed box. |
| Hairpins | 2 | Dynamics change only in steps at section starts. |
| Tempo marks | 1 | No tempo character text at all, one metronome mark. |
| Whole bars repeated verbatim | m1=m5=m28, m24=m26, m12=m35 | Copy-paste, not variation. |
| Bar-level dynamics printed twice | every one | Emitted on both staves independently. |

## The core finding

`musical_ear.ear_report` returned **0 errors, 0 warnings** on that score. Every
gate in the system passed it. The measurement layer could not see any of the
defects above, because none of them is an *error* — a bar with one cadence
formula in it is perfectly legal music.

Two separate things had to be fixed:

1. **The notation layer could not express what human music needs.** No rolled
   chords, no ties across barlines, five articulation names, no character text,
   no pedal marks, no fingering. A note that ran past its barline was silently
   truncated. The composer could not have written an articulated score.
2. **Nothing measured whether the output read as engraved music.** Added
   `score_realism.py`.

## Verification

Two 16-bar settings of the same harmony, one written the way the system used to
write and one using the notation layer as it now stands:

| | old | new | real movements |
|---|---|---|---|
| notation marks / bar | 0.00 | 4.38 | 0.11-5.71, median 1.58 |
| realism findings | 9 | 2 | — |

The nine findings on the old setting were: cadence formula (both staves),
accompaniment monoculture, rhythm-vocabulary poverty (both staves), uniform
phrase lengths, identical phrase openings, scalar overuse, texture stasis. The
two remaining on the new setting are true of the test data (four 4-bar phrases,
two similar sections), not artifacts.

## Calibration discipline

Every realism detector was run over 60 canonical Mozart / Beethoven / Chopin
movements before being allowed to warn. The first draft fired on **130%** of
them (multiple findings per movement); it now fires on ≤8%, and every detector
that still fires on real music is `info` severity with its false-positive rate
stated in its own docstring.

This falsification overturned two of the defects diagnosed by eye:

- **Verbatim bar repetition is not a defect.** Real movements repeat their
  most-repeated bar a median of 4 times (max 16), and 38% of a staff's bars
  being verbatim repeats is the median. The `repeated_bars` detector was
  recalibrated above the real maximum and demoted to `info`.
- **Accompaniment "monoculture" was measured wrong.** With an exact-contour
  signature the generated piece scored 0.12 against a real-corpus median of
  0.08 — it was *less* uniform than real music by that measure. The signature
  was coarsened to rhythm-plus-contour-direction so it catches the same figure
  transposed, which is what the eye actually saw.

Structural statistics mostly showed the generated piece **inside** the real
distribution (leap share, step share, rest placement, onset independence,
attack-count variance, register span all sit mid-range). The defects that
genuinely separated it were notational and phrase-boundary-relative, not
statistical — which is consistent with the standing lesson that chasing corpus
z-scores is a dead end.

## Applying it to the output

The shipped `mozart-andante-fmaj-20260825` was regenerated as
`mozart-andante-fmaj-v2-20260826` through the real pipeline
(`get_composition_brief` → `commit_agent_phrase_direct_bars` → gate → engraver's
pass → assemble), with the same form, key scheme and phrase layout.

| | shipped 2026-08-25 | regenerated 2026-08-26 |
|---|---|---|
| notation marks / bar | 0.95 | **2.54** (real median 1.58) |
| articulations | 0 | 38 |
| slurs / hairpins | 18 / 2 | 37 / 12 |
| ties | 0 | 2 (a real elision, bar 8→9) |
| `rit.` marks | 9 | 3, at the three section ends |
| distinct cadences (of 9 phrases) | 3 shapes, one used 4× | 9 distinct, variety 0.78 |
| scalar melody bars | 39% (real max 15%) | below threshold |
| melodic register span | 20 semitones | 53 |
| simultaneity CV | 0.19 (Mozart floor 0.22) | **0.29** |
| longest single-texture run | — | 8 bars (was 16 before revision) |
| realism findings | 4 | **0** |
| musical_ear findings | 0 | 0 |

Three defects were found in the *regenerated* piece by the newly-wired
analyzers and fixed, which is the loop working:

1. **`out_of_period_register`** — the climax reached E♭7, a fourth above the top
   of Mozart's fortepiano. Fixed by taking the peak down and finding the range
   at the bottom instead (the retransition now sinks to C4). This detector was
   added because the defect was mine.
2. **`cadence_analysis`** — two of the three structural cadences had **no
   dominant** (IV–I and vi–I where a PAC was planned). This is the same defect
   the original piece had, reproduced by hand; nothing had ever checked a
   realized cadence against its plan.
3. **A rootless dominant.** With the fix in place the cadences still read as
   `viio–I`: the bass struck C on beat 1 and left, so the sonority at the moment
   of resolution was E–G–B♭. Holding the dominant's root under the whole
   cadence bar turned them into real `V7–I`, and the structural arrival at bar
   37 needed the tonic in the *soprano* to be a perfect rather than imperfect
   cadence.

## Second pass — subsystems that were never running

The notation work above made the output expressible. Probing for the *shape* of
that first set of bugs — a value computed and read by nobody — found that
several of the system's advertised subsystems had never produced anything.

| Subsystem | State found | Now |
|---|---|---|
| ExpectationLedger | **Never held an entry in any piece.** Every write guarded by `if ledger is not None`; a fresh graph has none. And the brief read only the PHRASE scale — the one scale nothing is ever filed at. | A sonata plans 10 open expectations; every phrase's brief sees them |
| Style composition | `normalize_style` replaced `_` with `-` *before* stripping `style__`, so the system's own id matched nothing. All four styles had **zero members**, so no progression model, so hard-coded I-IV-V. | classical 21,029 transitions, renaissance 53,928, romantic 4,099, baroque 3,670 |
| `ContinuationContext` | Thirteen fields; **nothing ever wrote one**. | Recorded at commit and rendered, including the resolution a phrase owes |
| Craft checklist | Ran only in the engine-fallback path, never on the agent path every piece takes | Runs at commit, advisory |
| Engine fallback | Committed with **no physical validation**: 65 meter errors in one section | 0, with repairs reported not absorbed |
| Model round-trip | 26 fields lost on save/load; StyleDNA read back 7 of 18 | 0, pinned by a probe test |

## Two rules worth keeping

**`beats_to_dur` is right when you are describing a duration and wrong whenever
you are fitting one into a space.** Nearest-value conversion is a no-op exactly
when the clamp matters. Three sites had it.

**A detector's own author is the worst-placed person to spot its false
positives.** Running it over the repertoire is the only thing that reliably
does. Between the two sessions this reversed conclusions we were each confident
about: verbatim bar repetition (not a defect — real movements median 4), LH
"monoculture" (the generated piece was *less* uniform than real music), hand
spans (211 false "unplayable" stretches across 1,027 real bars — the ordinary
pedal-point idiom), and a hanging-dissonance check that fired on 49% of real
phrase endings.
