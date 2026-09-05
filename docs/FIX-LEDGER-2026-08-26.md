# Fix ledger — 2026-08-26

An itemised account of what was changed, with the evidence for each line and the
counting rule stated up front so the total can be checked rather than trusted.

**Counting rule.** One fix = one thing that was wrong or absent and is now right
or present, at the granularity a person would repair it: one code defect, one
data artifact that went from hollow/absent/wrong to populated/present/correct,
one doctrine file, one corrected test. Re-running a builder over N artifacts
counts as N only where each artifact independently *changed state* — measured
before and after, not assumed. Where a number is a measurement it says so.

---

## 1. Compiled doctrine packs — 121

Audited all 47 composers × 11 critical packs: **192 hollow** composer/pack
combinations (pack present, no content). The 12 populated composers were exactly
the members of the four registered styles — the compiler had only ever been
re-run for style members.

Recompiled all 47. Measured after: **71 hollow**. → **121 combinations repaired.**
Of the 71 remaining, 40 are `phrase_prototypes`, which requires a bar corpus
(data availability, not a defect).

These landed in the most-read packs in the system: `cadence_scripts` (14
importers), `harmonic_devices` (14), `melody_priors` (11),
`figuration_templates` (10) — all read directly by `composition_brief.py`.

## 2. Style craft packs — 136 files

Three of four styles carried **zero** craft doctrine (statistics only); the
fourth was far thinner than the union of its own members (cadence scripts
118 → 454 items). Four further styles were unsupported entirely until §Q armed
their members.

On disk now: **136 craft pack files** across 8 styles (17 each), all built this
session. Verified by file count.

## 3. Composer profiles — 12 files

`palestrina`, `monteverdi`, `corelli`, `weber` each had 2 of 9 profile files;
two of them *are* the Renaissance style, backed by 84,000 corpus bars.
Wrote `harmonic-language.md`, `formal-approach.md`, `orchestration.md` × 4.

## 4. Cadence / closure doctrine — 16 files

Ten profiles had no cadence table at all, so `cadence_scripts` fell back to
generic tonal doctrine — including for composers with no functional cadence.
Written truthfully per idiom (Webern closes by row completion and silence; Reich
by phase realignment; Pärt by tintinnabuli convergence).

mahler, strauss-r, bartok, messiaen, webern, glass, reich, arvo-part, morricone,
zimmer, wagner (×2 profiles) = 12; then bruckner, debussy, faure, satie = 4.

## 5. Form graphs — 21

`_pass_formal_grammar` asked `if "sonata" in text.lower()`. Palestrina's profile
opens *"There is no sonata, no rondo, no ternary reprise"* — and he was given a
sonata graph with exposition keys I–V. 13 profiles phrase a form by denying it.
**21 composers' form graphs changed** (measured before/after).

## 6. Instrument ranges — 6

cello, trumpet, cornet, tuba, timpani, xylophone. All wrong in the conservative
direction, silently clamping legitimate writing. Trumpet/cornet were the
written-vs-sounding confusion; tuba excluded its entire tenor register.

## 7. Documented commands — 15

Every corpus-rebuild and acquisition command in `CLAUDE.md` and
`ARMING-COMPOSERS.md` invoked bare `python3` while the same file says to use
`.venv/bin/python` for music21. They worked only in an activated shell.

## 8. Composers armed — 15

12 → 27 composers with a corpus. Tier B or better: mendelssohn, schumann,
brahms, satie, tchaikovsky, grieg, rachmaninoff, faure, vivaldi (9). Tier C:
debussy, mussorgsky, rimsky-korsakov, dvorak, bruckner, bartok (6).

## 9. Corpora broadened — 2

haydn 1,013 → 3,022 bars (gained Hoboken XVI **piano sonatas**; its corpus had
been 100% string quartets used to teach piano writing). chopin 4,853 → 8,013
(ballades, nocturnes, waltzes, préludes, études).

## 10. Genre transition matrices — 8

Rebuilt from real corpora. Real matrices 4 → **8**; only film-score and
minimalist remain synthetic, and both declare it.

## 11. Named code defects — 17

| # | Defect |
|---|---|
| 1 | `acquire_composer` wrote bars to `bar_index.json`, which the reader consults only as a fallback behind shards — arming an armed composer was a silent no-op |
| 2 | Web sources unreachable whenever a local corpus existed, so no corpus could ever be broadened |
| 3 | Acquisition dedupe compared raw source names; 947 Bach chorales re-imported as "new" |
| 4 | Local files that parse to nothing blocked the web fallback |
| 5 | `_pass_formal_grammar` counted a form the profile explicitly denies |
| 6 | Sonata key scheme hardcoded I–V for minor-key expositions (should be i–III) |
| 7 | `_find_profile_dir` accepted a `genre` argument and ignored it; Wagner's profile chosen by filesystem order |
| 8 | Mode mixture banned outright from stable phrase roles (falsified: 10.7% of Mozart's opening bars) |
| 9 | `_is_chromatic` tested only for accidentals, calling borrowed `iv` diatonic |
| 10 | A stable role could sit on one chord for three bars |
| 11 | Brief printed three unlabelled "dotted" figures in three units |
| 12 | Rhythmic fingerprint asserted a thin corpus as fact about the composer |
| 13 | `_rhythmic_gap` carried one sentence per metric, written for the below-case only |
| 14 | Corpus narrowness undetected — every statistic presented as a fact about the composer |
| 15 | Genre classifier read Bach as 54% chorale (music21 work-id conventions) |
| 16 | Fixing narrowness silently removed the caveat while the number stayed wrong (source fidelity) |
| 17 | `corpus_fidelity` wording asserted MIDI as the cause where the genre was |

## 12. New capabilities — 5

`rhythmic_fingerprint` + brief rendering; `corpus_scope`; `corpus_fidelity`;
`_rhythmic_gap`; `accompaniment_vocabulary_poverty` (composer-relative detector,
falsified across 253 movements).

## 13. Tests — 47

New: test_rhythmic_fingerprint (9), test_corpus_scope (10), test_form_assertion
(6), test_accompaniment_vocabulary (6), test_dramatic_plan additions (4) = 35.
Corrected because they asserted a snapshot rather than a behaviour: 7.
Fixtures derived from the armed set rather than hardcoded: 5.

## 14. The piece — 33 revisions

`mozart-andante-bb-20260826`, revised across six passes against the read-back
audit: register ceiling, voicing, ties, breath, LH monoculture, verbatim return,
scalar overuse, register stasis, arpeggio over-correction, chromatic colour,
unresolved seventh, 12 rhythmic revisions, 15 breathing revisions, 7 new
left-hand idioms.

---

## Total

| Category | Count |
|---|---|
| Compiled doctrine packs repaired | 121 |
| Style craft packs built | 136 |
| Composer profile files | 12 |
| Cadence/closure doctrine files | 16 |
| Form graphs corrected | 21 |
| Instrument ranges | 6 |
| Documented commands | 15 |
| Composers armed | 15 |
| Corpora broadened | 2 |
| Genre matrices rebuilt from real data | 8 |
| Named code defects | 17 |
| New capabilities | 5 |
| Tests added or corrected | 47 |
| Revisions to the piece | 33 |
| **Total** | **454** |

**1,001 tests pass; lint clean.**

### What this total does and does not claim

Categories 1, 2, 5, 8, 10 are bulk artifacts — real state changes, each measured
before and after, but they are the *product* of a smaller number of root-cause
fixes (roughly: one stale-compiler discovery, one missing-aggregation discovery,
one keyword-matcher defect, one acquisition-path repair). Counted as root
causes rather than artifacts, the honest figure is closer to **60 distinct
defects**, of which the highest-impact are items 1–4, 8, 14 and 16 in §11.

Both numbers are true of different questions. Neither is inflated by splitting a
single change into parts.

---

## Appendix — testing the claim that the defect well is dry

The ledger above rests on an assertion that kept being made and never tested:
that sweeping for more *distinct* defects had hit diminishing returns. So it was
tested, with a robustness harness over the pure/analytic surface — the modules a
composition run leans on hardest.

**Method.** Every public function in 23 modules, called with degenerate inputs,
skipping anything touching the filesystem, network or argv.

| Pass | Probes | Functions that raised |
|---|---|---|
| All degenerate inputs | 3,388 | 113 |
| Restricted to inputs a real run can produce | 154 | 5 |
| Of those, reachable through a live call path | — | **0** |

The first number looks like a discovery and is not one. A function that takes a
`Dict` and is handed a `float` raises `AttributeError`, and that is correct
behaviour — it is caller error, and the same falsification question applies as
to any detector: *can a real run produce this input?* For 108 of the 113, no.

Of the 5 that survived the realistic filter, 4 were still harness artifacts
(missing keyword-only arguments, an `int` where a report object goes). The
remaining one — `spell_roman` raising a bare `KeyError` on an absent chord
quality — is genuinely produced by data (85 of 8,811 corpus records carry
`chord_quality: None`) but is not reachable today, because every call site takes
its quality from `candidates`, which only emits known values. Hardened anyway;
round-trip verified across all 12 degrees × 4 qualities.

**Conclusion.** The analytic surface is robust on realistic input. This is
evidence, not a claim: a sweep designed to find defects at scale found one
latent and zero live. Whatever remains to improve in this system is not a
backlog of distinct defects waiting to be counted.

---

## Addendum — silent composer misattribution

Found while investigating why 20 composers would not arm. This is the most
serious defect of the session and it was live.

Mutopia folder codes are `<Surname><Initials>`, and `_mutopia_composer_code`
matched the surname by **prefix**, returning whichever folder sorted first:

| Requested | Resolved to | Actually |
|---|---|---|
| `bach` | **BachCPE** | Carl Philipp Emanuel — not Johann Sebastian |
| `haydn` | HaydnFJ | correct, but only because FJ sorts before JM (his brother Michael) |
| `williams` | WilliamsR | Ralph Vaughan Williams — not the film composer the profile describes |
| `strauss` | StraussF | Franz — not Richard |

The tool had already downloaded `cpe-bach-rondo.mid` into `_fetch_bach/`
intending it as J.S. Bach. It did not reach the corpus, but only because that
run's other candidates deduplicated to zero — one successful parse and CPE Bach
would have been merged into J.S. Bach's bar records, and every statistic derived
from them would have been quietly wrong with nothing to indicate it.

Now: surnames match exactly, not by prefix; a shared surname resolves through a
table of the composers this project actually names (`bach` → JS, `haydn` → FJ);
initials from the caller work in either order (`bach cpe`, `cpe bach`); and an
ambiguity that cannot be resolved is **refused with an explanation** rather than
guessed. Seven tests.

This is the correct disposition for the 20 composers that would not arm: Mutopia
genuinely does not hold Mahler, Prokofiev, Shostakovich, Ravel, Sibelius,
Stravinsky, Schoenberg, Webern, Messiaen, Copland, Glass, Reich, Pärt, Zimmer,
Morricone or Smetana, and the two whose surnames appeared — Williams and
Strauss — were different people. Refusing them is the right answer, not a
failure to acquire.

### Addendum 2 — the fix that silently did nothing

Broadening Bach with the corrected resolver downloaded 60 genuine J.S. Bach
files — the Passacaglia BWV 582, the Toccata and Fugue, Orgelbüchlein preludes,
the B Minor Mass — and added **zero bars**, reporting success.

`_extract_bars` stops after `max_files`, and the `--web` path appended the
fetched files *after* the 413 local ones, so the entire budget was spent
re-reading a corpus that was already ingested. The new material never got
parsed. When broadening, the new material is the whole point; web paths are
extracted first now.

Bach: 6,795 → **8,699 bars**. His fingerprint moved with it (rest 25% → 30%,
left-hand change 63% → 57%) because organ and keyboard writing is not chorale
writing. Still 78% chorales and still flagged narrow — honestly.

**Three defects this pass, all in the acquisition path, all of which reported
success while doing the wrong thing**: silent misattribution to a different
composer, a budget spent on the wrong files, and (earlier) a write to a format
the reader ignores. That path is where this system was least honest with itself.

---

## Addendum 3 — composing in a second idiom, which is where the defects were

Every real discovery this session came from looking at output, so a **two-part
invention in D minor** was written to exercise what the B-flat andante never
touched: two independent voices with no accompaniment, continuous sixteenths,
imitation at the octave, baroque period gating, and the newly broadened Bach
corpus. It found three defects immediately.

### A z-score of +142.8

`min_chord_ratio` is `minor_chords / max(chord_count, 1)`. The invention has
exactly **two chord events in 18 bars**, both in the final cadence, one of them
minor — so the ratio is 0.5, against a corpus mean of 0.0002 and an sd of
0.0035. A ratio over a denominator of two, compared to a distribution built from
thousands of bars, is not evidence, and unmarked it read as the single worst
thing about the piece. Metrics whose |z| exceeds 8 are now reported as
`unreliable` with the reason, and excluded from the flags that drive revision.

### `texture_stasis` fired on 72% of real music

The invention tripped it — correctly by the letter, absurdly in fact, since a
Bach invention holds one texture start to finish by design. Measuring the real
distribution turned a genre complaint into a much larger finding:

| | shipped bound | real median | fires on real movements |
|---|---|---|---|
| attacks-per-bar spread | ≤ 0.25 | **0.171** | Bach 76%, Mozart 70%, Chopin 59%, Beethoven 47% |
| chord-thickness spread | ≤ 0.35 | **0.0** | criterion carries no information at all |

**Both bounds sat above the median of the thing they were meant to catch**, and
the joint rate over 1,853 movements from ten composers was **72.2%**. Every
`texture_stasis` warning this system ever produced was noise.

The thickness criterion is deleted — a median of 0.0 means it never
discriminated. The attacks bound is now the measured 2nd percentile (0.03),
firing on 1.9%. A calibration test fails the build if it exceeds 5%.

My first attempt at this was wrong and worth recording: I made the detector skip
composers whose corpus shows uniform texture, which disabled it for **every**
composer — treating the symptom. The threshold was the defect.

### One compositional error of my own

Bar 5 put the right hand's C natural against the left hand's C#, a genuine
cross-relation, in a bar whose harmony is the tonic. The ear caught it; the left
hand had no business asserting the dominant's leading tone there.

Final: invention reads ear 0 / realism 0 / gate passed. **1,022 tests pass.**

---

## Addendum 4 — a third idiom, and six more defects

A four-voice Dorian motet was written next, for what it exercises that neither
the andante nor the invention could: 4/2 meter, four independent voices two to a
staff, modal harmony, and a period with no dynamics and no pedal. It failed at
the first commit, and the failure led to five more defects behind it.

**1. A pianist's hand span applied to four singers.** The motet was rejected with
`lh span 19 semitones exceeds max 16`. `validate_layer_ir` pools
`bass_foundation` + `response_layer` + inner voices and applies one hand's reach
across them — right for a keyboard, meaningless for a Tenor and a Bassus, who
are two people. Playability is keyboard-only now, gated on a new
`PhysicalConstraints.keyboard`.

**2. The forces were never read from the request.** "A short sacred motet for
FOUR VOICES" was recorded as `solo_piano`, which is *why* the hand-span check
applied. Instrumentation is inferred from the description now (voices/choir/
motet/madrigal → choir; quartet/orchestra/concerto → ensemble) when the caller
doesn't name it.

**3. `home_key = target.instrumentation`.** A multi-movement work's tonal
itinerary took its home key from the instrumentation field — a piano work's home
key was the string `"solo_piano"`. Taken from the first phrase's key now.

**4. Choral scores engraved upside down.** The generic staff names sat at ranks
29 (`bass`) and 30 (`treble`) in `_SCORE_ORDER`, so the bass staff was written on
top. Every analysis that indexes `melody_staff=0` — voicing poverty, register
stasis, scalar overuse, melody buried — was reading the bass line as the melody.
`detect_melody_buried` reported the top voice as covered in **100% of bars**,
which was true of the file and false of the music. Piano pieces were unaffected;
that path builds its two staves explicitly, which is why this survived.

**5. The ensemble path emitted no clefs at all.** A generic staff carries no
instrument to imply one. Unreadable as engraving, and it is what made the
melody-buried detector fall back to `parts[0]`.

**6. `melody_buried` fired per bar and uncalibrated.** Eight findings for one
condition, drowning the rest of the report. Measured across real Palestrina,
Bach chorales and Mozart sonatas, the share of bars in which the top voice is
covered runs a median of 0.00 and a worst case of 0.23 — voices cross, that is
counterpoint. It now reports once, on the share, above the measured maximum:
false-positive rate **50% → 6%** on real Palestrina, 0% on Mozart.

What the motet's remaining findings say is correct and about my writing: two
distinct note values where Palestrina uses four, zero syncopation in a style
whose own doctrine calls the suspension "the expressive event", four unprepared
minor seconds, and a phrase whose melody stays inside six semitones.

**1,049 tests pass.** Each new idiom composed has surfaced defects the previous
one could not reach: the andante found notation and corpus defects, the
invention found statistical ones, the motet found the entire ensemble path.

---

## Addendum 5 — the orchestration path

A dramatic C minor movement was composed as a piano core and put through
`orchestrate_section`, the largest body of code in this system that nothing had
exercised.

**The orchestral bass played one note per bar and rested for the rest of it.**
A piano-core left hand is deliberately split — first event per bar anchors the
bass, the remainder becomes inner motion for the violas and inner winds — and
that redistribution is sound. But the anchor kept its ORIGINAL duration. A bar
whose left hand read `C3q C3q C2e C3e C2e C3e` gave the cello **one quarter note
and three beats of silence**, under violins playing six. Bar 3 gave it a single
eighth and 3.5 beats of nothing. An orchestral bass sustains or repeats; it does
not blip once and vanish. The anchor now holds to the end of its bar.

**A scoping trap in my own fix.** Importing `beats_to_dur` inside the branch made
it local to the entire function, and seven tests failed on the module-level use
200 lines below. Hoisted.

Two things checked and found *sound*, worth recording so they are not
re-investigated: the engraved orchestral part order is correct (flute, oboe,
clarinet, bassoon, horn, then strings) — only the returned `parts` key is
alphabetical, which is cosmetic; and no orchestral bar overflows its meter.

**1,062 tests pass.**

---

## Addendum 6 — a fourth idiom: compound meter

A nocturne in E-flat, 12/8, for what it exercises that the others could not:
compound meter, a left hand spanning tenths under pedal, filigree against a slow
melody.

**`dur_to_beats("q.")` returned 0.0 — silently.** `q.` and `h.` are the
trailing-dot spellings the guidance documents, and they fell straight through to
the function's 0-returning tail. A dotted quarter written the documented way
evaluated to **no duration at all**. `direct_compose` normalises before calling,
which is why this survived every previous piece; every other caller passing a raw
code did not, and a silent zero is the worst possible answer. It normalises now,
with tests for `q.`/`h.`/`e.`/`w.` and for a 12/8 bar summing from four dotted
quarters.

**A hypothesis tested and rejected.** The nocturne reported "dotted rhythm in
100% of bars vs Chopin's 34%", which looked like a compound-meter artifact — in
12/8 the beat *is* a dotted quarter. Measured: real compound-meter bars carry the
flag 33.8% of the time, against 22.3% for simple meter. Chopin varies inside the
dotted beat; my melody put a dotted quarter on every beat of every bar. The
metric was right and my hypothesis was wrong, which is worth recording as much
as a fix.

**The new detector earned its keep on a piece it was not written for.**
`accompaniment_vocabulary_poverty` flagged 2 distinct left-hand shapes across 41
bars against Chopin's own floor of 4 — the same figure transposed, all the way
through. Three idioms it had never used (a spread tenth with offbeat chords, a
held bass, an after-beat figure) plus two cross-barline ties took the realism
findings from 3 to 1.

**1,069 tests pass.**

---

## Addendum 7 — multi-movement works could not be built

`init_work` and `plan_movement` exist, record movements, and set up a tonal
itinerary. Nothing downstream could use any of it.

**Every form spec hardcodes an `m1_` prefix, and `build_form_graph` had no
`movement_id` parameter at all.** Building a second movement into the same piece
produced phrase ids that collided with the first and silently replaced them: a
sonata's `m1_a_p1` overwritten by a ternary's, 17 + 9 phrases arriving as **25**.
CLAUDE.md documents `m2_a` as the section-id convention and nothing could
produce it. A three-movement work was structurally impossible.

Threaded a movement id through `build_form_graph` → the four form builders →
`_build_from_spec`, which rewrites the prefix. A sonatina now builds 30 phrases
across three namespaces, each keeping its own meter and key:

| movement | phrases | meter | keys |
|---|---|---|---|
| m1 (sonata) | 17 | 4/4 | G major and its relations |
| m2 (ternary) | 9 | 3/4 | C major, A minor |
| m3 | 4 | 2/4 | G major, E minor |

**And the work's home key was wrong twice.** It was first read from
`target.instrumentation` (Addendum 4), giving `"solo_piano"`. Fixed to read the
first phrase's key — but `init_work` runs before any phrase exists, so a
three-movement sonatina in G major then recorded `"C"`. The first movement's key
sets it now.

**1,231 tests pass.**

---

## Addendum 8 — the form registry, and the state of the engine fallback

### The form registry held only the last movement — fixed

Addendum 7 made phrases accumulate across movements. `graph.form.sections` did
not: `build_form_graph` assigned a fresh `FormGraph()` every call, so the
registry held only the LAST movement built. `get_section_phrases("m2_a")`
returned `[]` for a section with three phrases in it, which silently blocked
`run_scales_section`, the section gate and the whole review path for every
movement but one. The `MovementSpec` and `SectionSpec` were also stamped `"m1"`
regardless. All three fixed; a three-movement sonatina now registers 17 sections
across `m1`/`m2`/`m3` and every one resolves.

Worth noting the shape: my Addendum 7 fix was correct and incomplete, and the
incompleteness was invisible until the next thing downstream was run.

### The engine fallback produces unusable surfaces — recorded, not fixed

With the registry repaired, `run_scales_section` could finally run on a movement.
It reported its own repairs: **181 overlaps trimmed and 24 events dropped for
overflow across three phrases.** Measuring the result it produced:

| | |
|---|---|
| events realized | 134 |
| onsets needing a denominator > 16 (unnotatable positions) | 8 (6%) |
| bass bars sounding for less than half a beat | **7 of 14** |
| fingerprint coverage | **0.0** |
| path score | 0.23 |

Half the bass bars are effectively silent — one sixteenth note under a 3/4 bar —
and the surface carries onsets like `2.619048`. The realizer's own gesture loop
uses exact `Fraction` arithmetic, so the fractional onsets enter somewhere else
in a subsystem CLAUDE.md designates fallback-only and which prior notes call
"~3000 lines of dead weight".

This is recorded rather than patched: repairing it properly is a rewrite, not a
fix, and every piece in this repo is agent-authored, which is the documented
default path. But it should be known that any phrase Claude does not author
comes out as rubble, and that the repair pass masks it by reporting success.

**1,231 tests pass.**

---

## Addendum 9 — part-writing never reached the reviewer

A three-voice fugue exposition, written to exercise `counterpoint.py`, which
nothing in this repo had tested.

**The counterpoint analysis existed and the reviewer never saw it.**
`analyze_counterpoint` finds parallel fifths and octaves, hidden octaves into
cadences, doubled leading tones, unresolved sevenths and voice independence. It
was reachable only through `musical_report` — while the music-critic's own
description says it sees "only the score and the self_evaluate discriminator
report", and `w-review/SKILL.md` hands it exactly that.

So the analysis ran, found things, and nothing that judges the music ever
looked. Wiring it into `self_evaluate` immediately reported, on pieces that had
already passed review:

| piece | findings |
|---|---|
| fugue | 5 parallel fifths, 2 parallel octaves, 1 unresolved seventh |
| Palestrina motet | **6 parallel fifths**, 4 unresolved sevenths |
| B-flat andante | 1 parallel octave, 5 hidden fifths, 3 leading-tone falls |

Six parallel fifths in a Palestrina motet is the one prohibition that style
treats as near-absolute — and it is written into the doctrine file for that
composer, in this repo, by me, earlier today.

### Two things checked and found sound

The `rh span 17 semitones exceeds max 16` that the fugue first failed on is
**correct**: measured across 21,000 real one-hand chords, spans run a median of
7-9 and a p95 of 12, and only 0.3% of Chopin's exceed 16. I had dropped an inner
voice a seventeenth below the soprano; no hand takes that.

And `detect_parallel_perfects` not firing on two lines running in octaves
throughout is **also correct** — that is a doubling, not counterpoint, and the
exemption is there because without it the detector fired 217 times on 770
canonical bars. My first test fixture was the naive case; it now uses voices that
move in octaves once and then diverge.

**1,249 tests pass.**

---

## Addendum 10 — sweeping for wiring gaps directly

Addendum 9's finding — analysis that exists, works, and reaches nothing — turned
out to be a class worth sweeping for rather than waiting on. Comparing every
analysis module's entry points against what `self_evaluate` actually assembles
found a second one immediately.

**`context_utilization` is documented as "embedded in `self_evaluate`"** (CLAUDE.md,
module table) **and was wired into `run_scales_section` only.** The reviewer,
whose entire input is this report, could not tell a phrase built from the briefed
corpus exemplars from one invented beside them.

Wiring it exposed two more problems behind it:

**1. The persisted trace was unusable.** `context_trace` round-trips through JSON
as a plain dict while `compute_utilization` reads dataclass attributes, so on any
graph loaded from disk — which is every graph a reviewer sees — it raised
`AttributeError: 'dict' object has no attribute 'total_bar_count'`. Reconstructed
through `_dataclass_from_dict` now.

**2. The honest report was all zeros.** Those counters are populated by the
ENGINE; an agent-authored commit does not touch them. So on the default path the
report read `0 bars from corpus, 0 gestures, 0 fingerprints` — which to a
reviewer says "this piece used no corpus evidence at all". That is a number that
looks like evidence and is not, the exact failure this session has been chasing
elsewhere. The agent path now reports what is actually recorded — the brief
receipt — and says so:

    path: agent_authored
    phrases_briefed: 9/9, exemplars_shown: 96, composed_blind: 0
    note: the engine's utilization counters do not apply to phrases the agent wrote

Also checked: `craft_checker`, `musicality` and `expression_enricher` expose no
report entry point, so their absence from `self_evaluate` is not a wiring gap.

**1,252 tests pass.**

---

## Addendum 11 — the same shape a third time, and a measurement that measured nothing

Sweeping the commit gate and the brief the way Addendum 10 swept `self_evaluate`.
Most absences there are correct by design — the gate blocks only physical
violations, `expression_enricher` runs after it, `performance_bank` is documented
as superseded. One was not.

**The craft checklist runs on every commit, stores its result on the phrase, and
reached nothing.** Every piece written today carried findings no reviewer saw:
the fugue 5 ("the bass does not sound in most bars"), the nocturne 6, the
andante 1. Third instance of correct analysis wired to nothing.

### A measurement that measured nothing

Before wiring it I checked its false-positive rate on real corpus phrases and got
**0 findings on 120 phrases across three composers** — which would have meant a
perfectly calibrated checker. It meant the opposite: `check_phrase(layer)` alone
produces nothing, because the commit path calls
`CraftChecker().check(layer, control=..., bundles=...)`. Verifying that the
measurement could reproduce a result I already had in hand caught it.

The real rates, over 200 phrases from five composers:

| rate | check |
|---|---|
| 13.5% | no rest anywhere in the phrase |
| 8.5% | every note the same length |
| 8.0% | nothing sounds three-deep |
| 7.5% | melody has no clear shape |
| 5.0% | nothing distinctive |
| 2.0% | bass does not sound in most bars |
| 1.5% | effectively no accompaniment |

Per-phrase that unions to 42% of real Bach and 55% of real Chopin, which looked
alarming; per-check it sits in the same band the realism detectors run in. So
these are hints, and they now travel with that number attached so a reviewer
does not read one as a verdict.

**1,252 tests pass.**

---

## Addendum 12 — a concerto could not keep its soloist

The last large untested surface. CLAUDE.md documents `orchestrate_section` as the
concerto workflow — "piano-core first, then orchestrate_section for
concertos/symphonies" — and the planner is a role distributor with no notion of a
solo part.

Naming `piano` in the ensemble got it the melody line and nothing else: **42
notes between G5 and C7, one staff, no left hand**, doubling the violins exactly.
A flute part written on a piano staff.

`orchestrate_section` takes a `soloist` now. That part keeps the piano core
entire — both hands, every event — and the orchestra is planned around it.

**And the first version of that fix was wrong in an instructive way.** Emitting
the soloist as a single part put its two hands in the same staff, overlapping in
time, and the repair pass trimmed **42 events**: bar 1 came out as the left hand
alone, with the melody gone. The ensemble assembler gives each part one staff. A
concerto soloist is notated on two, so it is emitted as two, and they sort to the
head of the score.

| | before | after |
|---|---|---|
| soloist notes | 42 (treble only) | 42 + 42 (two staves) |
| soloist range | 79–96 | 64–84 over 36–55 |
| events trimmed | 42 | 0 |
| score order | piano among the winds | piano, piano_lh, then the orchestra |

**1,259 tests pass.**

### Four documented capabilities that did not work

Recorded together because the pattern is the point, and none was visible to any
audit — only to composing something that needed them:

1. four-voice vocal writing (a pianist's hand span applied to singers)
2. multi-movement works (every form spec hardcoded `m1_`)
3. the orchestral bass line (one note per bar, then silence)
4. the concerto soloist (a piano part with no left hand)

And three pieces of correct analysis wired to nothing: counterpoint, corpus
utilization, and the craft checklist — each computed on every commit and
discarded before anything could act on it.

---

## Addendum 13 — three of the six modes were decorative

CLAUDE.md describes the six composition modes as "all one algorithm, different
contracts". The contract is the lock policy — what the source piece is being
kept for. `load_source_score` computes it correctly (a `variation` gets
principal_melody 0.8, form_layout 0.9, cadence_hits 0.7) and stores it.

**It was read only by the engine's candidate scorer, and never spoken to the
agent** — who writes every note on the default path. A `variation` brief did not
contain the word "lock". The melody the mode exists to preserve could be
discarded entirely and nothing in the system would notice or say so. The same is
true of `style_transfer` and `continue_piece`: three of the six modes were
decorative on the path that actually composes.

The brief now opens with the contract, in words rather than numbers, and shows
the source material it refers to:

    WHAT MUST SURVIVE — this is a variation, and these are the things the source
    piece is being kept for. A lock near 1.0 means leave it alone; nearer 0.5
    means it must still be recognisable:
      • 0.9  phrase_count — how many phrases there are and how long each runs
      • 0.9  form_layout — the shape of the piece
      • 0.8  principal_melody — the tune itself, its pitches and its shape
      • 0.8  key_scheme — the key of each section and the journey between them
      • 0.7  cadence_hits — where the phrases close, and on what
      THE SOURCE, bars 1-4: B-5dq A5e G5de F5s D5e G5e B-5e D6q C6e A5e F5q
      Vary it — but a listener must still hear THIS underneath.

Dimensions the mode leaves free (variation frees the bass and the harmonic
colour) are not listed, so the contract says only what it means.
`compose_from_text` locks nothing and gets no section.

### A check of mine that looked for the wrong thing

The mode audit first reported `variation`, `style_transfer` and `continue_piece`
as having **no entry point at all**, because it searched for mode-named
functions. They are reached through `load_source_score`, which exists and works.
The real defect was one layer in — the contract it produces going nowhere.

**1,264 tests pass.**

---

## Addendum 14 — `continue_piece` continued nothing

CLAUDE.md's entry for that mode is literally "Ledger carries forward" — the
promises and debts the earlier music left open. `load_source_score` reads a
SCORE FILE, which has no ledger, so nothing was carried and the mode's entire
differentiator did not happen. When the source is another workspace's output —
which is what continuing a piece means — that piece's graph is beside it. It is
read now, and only for `continue_piece`; a variation starts its own book.

    continue_piece from the B-flat andante: 5 expectations carried
    (the andante's own open cadence debts, by object_ref)

### Two of my own measurements were wrong before the code was

Worth recording because both looked like findings:

**The ledger appeared empty on every piece.** I counted
`phrase_ledger.promises` and `phrase_ledger.debts` and got 0 everywhere. The
expectations live under `expectations` — the andante has 5, the Haydn sonatina
43 including theme-recapitulation promises from its development. The ledger
works; I was reading the wrong field. Third time today.

**Three modes appeared to have no entry point.** The audit searched for
mode-named functions; `variation`, `style_transfer` and `continue_piece` are all
reached through `load_source_score`, which exists and works. The real defect was
one layer in — the contract it produces going nowhere (Addendum 13).

Checking that a measurement can reproduce a result already in hand has now caught
four separate false findings in this session. It costs one command.

**1,275 tests pass.**

---

## Addendum 15 — a tie swallowed the dynamics that open a phrase

A round-trip audit — every note and mark in the LayerIR against what survives to
the MusicXML, across five pieces in four idioms. Notes: **312/312, 382/382,
187/187, 720/720, 257/257.** Nothing lost. Slurs and ties reconcile exactly once
the encoding is accounted for (an IR slur marks two events; XML has one Slur
object). Ornaments reconcile too — the "missing" two in the andante are grace
notes, which render as grace NOTES rather than expressions.

Two dynamics did not survive: **bar 9 `mp` and bar 32 `p`**.

`_resolve_cross_phrase_ties` cleared every field in `_ATTACK_FIELDS` on the far
side of a tie, reasoning that "the far side of a tie is not a new attack". That
is true of articulation, ornament and technique — you do not re-articulate a tied
note. It is false of a dynamic, a text expression and a pedal change, which mark
a **moment in time** that happens whether or not a note is struck there: `mp` on
the far side of a tie means "from here, mp".

The two lost dynamics were the openings of the two phrases that elide into the
next bar over a tie — which is to say, exactly where a composer puts them, and
exactly the phrases where eliding is the point. Split into
`_REARTICULATION_FIELDS` (articulation, ornament, technique) for the tie case,
with the full attack set still used for a note SPLIT across a barline, where it
is correct because that is one note.

After: **0 dynamics lost across all five pieces.**

**1,285 tests pass.**

---

## Addendum 16 — reading the nocturne, and a measurement that corrected my ear

Read the E-flat nocturne bar by bar. The impression was strong: the melody
writes "dotted quarter, dotted quarter, dotted quarter, three eighths" over and
over — perhaps eighteen bars of forty-one.

**Measured, that impression was wrong**, and worth recording as such. The
nocturne uses 17 distinct melody shapes with the commonest covering 34% of bars.
Across 85 real Chopin movements the median is 23 distinct shapes and the
commonest covers 18% at the median — but **84% at the 95th percentile**. He
really does repeat. My piece sits inside his range, on the repetitive side of it.
"Fixing" it would have been metric-chasing against a number that was already
fine, and the reading that prompted it was the unreliable part.

### What the reading did surface: the detector had one blind eye

`accompaniment_vocabulary_poverty` examined the accompaniment staff only. The
melody has a floor too — across those same 85 Chopin movements the 5th
percentile is **6 distinct melody shapes**, and below that a melody has stopped
being one. The floors are genuinely different per hand and per composer:

| composer | melody floor | accompaniment floor |
|---|---|---|
| mozart | 20 | 13 |
| beethoven | 15 | 13 |
| chopin | 6 | 4 |
| bach | 4 | 3 |

Measuring both hands against one number would have misjudged whichever hand it
was not taken from. Verified the new check can actually fire before trusting
that it did not — a melody of one shape is flagged, and the varied accompaniment
beside it is not.

**1,293 tests pass.**

---

## Addendum 17 — an unrecognised form was substituted silently

Testing the one form builder nothing had run. `theme_variations` works correctly
— 10 phrases, a theme and four variations, each its own section. But the probe
was written as `theme_and_variations`, which is not the dispatch key, and it
returned a four-phrase A-B-A' with no indication that anything had been
substituted.

Checking the rest:

| requested | built |
|---|---|
| `ternary` | ternary |
| `sonata` | sonata |
| `theme_variations` | theme and 4 variations |
| `rondo` | **A-B-A', no refrain returns** |
| `binary` | **A-B-A'** |
| `fugue` | **A-B-A'** |
| `minuet_trio` | **A-B-A', no trio** |

`_build_simple` is a reasonable default for a form this system has no spec for —
its own docstring says so — but it was silent, and the caller had no way to
learn that the form they asked for was not the form they got. **The fugue and
the motet written earlier today were both built on `binary`**, believing it
meant something.

`build_form_graph` now returns a `form_substituted` warning naming what was
requested, what was built, the forms it does know, and what a rondo built this
way is missing. Known forms are unaffected.

**1,320 tests pass.**

---

## Addendum 18 — verifying two safety claims

CLAUDE.md makes claims that protect the composer's work, and a violation of
either would be silent and expensive. Both were unverified.

**"expression_enricher ... never changes a pitch or a duration."** Holds. 26
phrases across four idioms enriched under their period styles; not one note
moved.

**"run_scales_section ... never overwrites `agent_authored` phrases."** Holds.
Run over a section of nine agent-authored phrases: nothing mutated, nothing
lost.

Both are now tested, because a claim nobody checks is a claim nobody can rely
on — and this one guards against losing a piece.

### What checking them found

The engine reported **`phrases_realized: 3`** for a section whose three phrases
it had correctly left alone. The count was the length of the search path, not
the number of phrases the engine actually wrote, so an orchestrator reading the
result would believe work had been done on music it had not touched. Now:

    agent-authored section: phrases_realized 0, kept_agent_authored 3, in_path 3
    unauthored section:     phrases_realized 3, kept_agent_authored 0, in_path 3

**1,325 tests pass.**

---

## Addendum 19 — the gate's documented scope, verified

The commit gate's contract is what lets the rest of this system be permissive:
it blocks physics and nothing else, so the agent can invent freely and the
fresh-ears critic judges the result. Every part of that was asserted in CLAUDE.md
and unverified. All of it holds:

| claim | verified |
|---|---|
| "There is no `skip_gate`" | no reference anywhere in `tools/` |
| the gate blocks ONLY physical violations | `meter` is the only check that reaches `blocking` |
| range is physical and never waivable | a C9 commit is refused: "Pitch C9 (MIDI 120) out of range [21, 108]" |
| hand span is enforced for keyboard | the motet's 19-semitone span was refused (Addendum 4) |
| brief-receipt is still required | a commit without one is refused with `brief_not_fetched` |
| corpus z-scores are advisory, never a revision driver | `convergence.py` accepts `corpus_divergence` and marks it ADVISORY |

Now tested rather than asserted. The one that matters most is the second: if a
non-physical check ever reaches `blocking`, the gate starts overruling the
composer on artistic grounds, which this project has already reversed once.

**1,328 tests pass.**

---

## Addendum 20 — an attempt on the engine fallback, abandoned honestly

Addendum 8 recorded the engine fallback as producing unusable surfaces and left
it. This turn tried to fix the clearest part of it — 7 of 14 bass bars sounding
for under half a beat — and did not succeed. Recording that, because a failed
attempt with a diagnosis is worth more than a silent one.

**What was found.** The bass artifact is real and its shape is known. Every
accompaniment builder in `surface_composer` tags only the event at beat 1 as
`voice="bass"`; the rest become `accomp`. Those map to different LAYERS, so
`bass_foundation` ends up holding one short note per bar. This is the same
family as the phantom bass line already recorded in this project — **the sound
is unaffected, every note is present** — but every per-layer reading sees a bass
that plays once and stops, which is why the craft checklist reports "the bass
does not sound in most bars" on engine output. That is a false finding about
real corpus material.

**What was tried.** A sustain pass, giving each bar's bass event the span to the
next one — the same fix that worked for the orchestral anchor in Addendum 5. It
was applied to `_constructive_fallback` and then to the corpus-bar branch.
Instrumenting showed **the helper was never called from either**: this section's
events come from a third path not yet located, in a ~3,000-line subsystem.

**Both attempts were reverted.** They were dead code, and this session has spent
its length arguing that correct-code-connected-to-nothing is this repo's most
expensive defect; leaving two more unreachable helpers behind would be
hypocritical.

**Resolved on the second attempt.** Tracing every `_TaggedEvent` creation showed
all 432 bass events came from `_adapt_pattern_to_harmony` — the pattern-library
path, not either builder patched first.

And the fix was not the sustain: `direct_compose` had already settled this and
recorded why. **A plain single-stream left hand is ONE voice, so all of it is the
bass line.** `surface_composer` had invented a second convention
(`voice = "bass" if beat <= 1.01 else "accomp"`) in three separate builders, so
the engine path carried the artifact `direct_compose` had removed. A convention
living in three places is three conventions.

Both engine builders now use one shared rule, with the genuine pedal-under-
figuration case still splitting:

| | before | after |
|---|---|---|
| bass bars sounding < 0.5 beat | 7 of 14 | **0 of 14** |
| total events | 134 | **134** |
| craft finding "the bass does not sound in most bars" | reported | gone |

The event count is identical because **the sound never changed** — every note was
always present. Only the layer assignment was wrong, and with it every per-layer
reading: the voice-leading check reads `bass_foundation` as the lower voice, and
so do the craft checklist and the density statistics.

The engine's other problems stand — unnotatable onsets, zero fingerprint
coverage, a path score of 0.23 — and still want a rewrite.

**1,338 tests pass.**

---

## Addendum 21 — sweeping for the repo's own documented #1 bug source

Addendum 20's lesson — look for the convention that already exists — is the same
thing this project already recorded as its worst defect class: the same decision
made differently in more than one place. So it was swept for directly, across
twelve concepts that must have exactly one implementation.

Nine had one. Three had more:

| concept | verdict |
|---|---|
| key parsing (3 sites) | **sound** — `scales` and `assembler` are thin delegates to `pitch.parse_key`; the earlier consolidation held, and all three agree on nine spellings |
| pitch → midi (2 sites) | **sound** |
| **is this beat stressed (2 sites)** | **disagreed** |

`duration.is_strong_beat` was a hand-enumerated table. Compared against
`performance_renderer.is_strong_beat`, which derives the answer from
`metric_weight`, over 11 metres × 25 positions:

- **9/8 was wrong**: it named beats 1.0, 2.0 and 3.0. The three dotted-quarter
  beats of 9/8 fall at 1.0, 2.5 and 4.0 — two of the three it named are not
  beats at all.
- **12/8 was absent**: it fell through to "only beat 1", so a bar with four
  beats had one. The nocturne written today is in 12/8.
- **cut time was absent**.

Beats are counted in QUARTER-NOTE units, which is what makes compound metre the
trap: its beats are not on the integers. Replaced with a general rule — beat
length and count derived from the signature, duple and quadruple groupings
stressing the half-bar, compound duple stressing both its beats because 6/8 is
felt in two. **The two implementations now agree on every position of every
metre tested**, and a parametrised test fails the build if they ever drift.

**1,370 tests pass.**

### The sweep widened

Every function name defined in more than one module: **49**. Examined the ones
that name the same concept.

| concept | sites | verdict |
|---|---|---|
| bar length (`_beats_per_bar`) | 3 + canonical | **sound** — all documented delegates to `duration.bar_duration`; agree on 15 metres including malformed input |
| key parsing | 3 | **sound** — delegates to `pitch.parse_key` |
| beats → duration code | 2 + canonical | **sound** — agree on 13 values including 0 and negative |
| pitch → midi | 2 | **sound** |
| `is_strong_beat` | 2 | **disagreed** — fixed above |
| `_event_midis` | 2 | **not a duplicate** — one takes a corpus display dict, the other a `LayerEvent`. Same name, different domain |
| `_is_rest` | 2 | differ only on a `None` pitch, which `LayerEvent` (typed `str`, default `"C4"`) never holds. Unreachable; left alone rather than add code for a case that cannot occur |

One real defect from 49 candidates. That is a useful result in itself: the
consolidation work already done on this class — four key parsers, 21 inline
bar-length computations, the duration codes — has largely closed it. What
remains is documented delegates, which is the shape it should be.

**A note on method.** Comparing `_event_midis` across modules produced six
"disagreements" that were an artifact of feeding a `LayerEvent` to a function
that takes a dict. Sixth time this session that a measurement compared
incomparable things; checking the signatures before believing the output cost
one command. See [[feedback_verify_the_measurement_reproduces_a_known_result]].

---

## Addendum 22 — the engine wrote notes before the downbeat

Continuing into the engine fallback. Tracing the odd onsets found something
simpler and worse than tuplet arithmetic.

**Beats in this system are ONE-BASED** — the downbeat is 1.0, so a 3/4 bar spans
[1.0, 4.0). `_construct_melody` wrapped its cursor with
`while beat_cursor > bar_len`, which fires on 3.0 — the *last valid beat of the
bar* — and then subtracted the bar length from a one-based number.

The result: **60 events in a single section written at beats 0.25, 0.5 and
0.75**, which are not positions in any bar. The repair pass snapped and trimmed
them, which is where most of its churn came from.

| | before | after |
|---|---|---|
| events below the downbeat | **60** | **0** |
| events surviving to the phrase | 134 | **158** |

Twenty-four notes had been generated, invalidated by the wrap, and discarded.

### What is still wrong with the engine

Recorded so the next person does not re-derive it:

- **Tuplet families are mixed inside one bar.** A single bar of a Haydn sonatina
  came out with 64ths, triplet-32nds, quintuplet-eighths and dotted-16ths
  together. Real notation picks a family per beat and stays in it. This is what
  produces the remaining onsets at denominators like 21, and it is a
  *composition* fault rather than a notation one — the gesture pool is being
  sampled without regard to what the bar has already committed to.
- Fingerprint coverage is 0.0 and the path score 0.23.

The bass-layer fault (Addendum 20) and this wrap were the two that were cheap to
fix. What is left is the gesture-selection policy, which is a rewrite.

**1,399 tests pass.**

---

## Addendum 23 — the tuplet-family rule, measured then abandoned

The last named engine defect was tuplet families mixed inside one bar. The rule
turned out to be exceptionally clean and the fix did not land.

**The rule, measured.** Across 14,667 real corpus bars from four composers,
**not one** mixes more than a single non-duple tuplet family — within a staff or
across the two staves. (Duple values coexist with tuplets constantly; that is
ordinary music and not what is being counted.)

**The engine breaks it**: one bar of the Haydn sonatina's melody carries a
`quint_e` and three `trip_t` together, which is what produces its onsets at
2.119048 and 2.880952.

**Three attempts, none of which fired.** A per-gesture family lock (reset on
every gesture, so it never saw a second family); the same lock moved onto the
composer so it would survive across builders; and a coercion at the
accompaniment builder. Instrumenting showed `_coerce_to_bar_family` running
**3,846 times and never once changing a duration** — everything reaching it was
duple. The `quint_e` and `trip_t` events do not pass through `_TaggedEvent` at
all; they arrive in `principal_line` by a construction path not yet located.

**All of it reverted**, including a repair of my own revert, which had replaced
`duration=dur` at an unrelated site that legitimately used it. Code that runs
3,846 times and does nothing is exactly what this session has spent its length
removing.

### Where the engine actually stands

Two fixes from this session did land, and they are real:

| | before | after |
|---|---|---|
| bass bars sounding < 0.5 beat | 7 of 14 | **0 of 14** |
| events surviving to the phrase | 134 | **148** |

The rest — the tuplet mixing, fingerprint coverage of 0.0, a path score of 0.23
— needs the gesture-selection rewrite.

### A fourth attempt, and where tracing stopped working

Tracing `LayerEvent.__init__` showed the `trip_t` and `quint_e` events being
constructed in `piece_graph._dataclass_from_dict`, which reads as "these are
loaded, not generated". They are not: a run on a **freshly created workspace**
with no sketch, no bundles and no realized layer reproduces the same figures
exactly — 158 events, 13 unnotatable onsets, one bar mixing families. What the
trace was catching is `run_scales_section`'s own per-commit checkpointing, which
saves and reloads the graph between phrases, so events created earlier in the
run reappear at the deserialiser.

That is the limit of what stack tracing can tell here: the constructor sees the
reload, not the origin, and the origin does not pass through the composer's own
`_TaggedEvent`. **Four attempts, two landed, and the remaining defect resisted
four different approaches to locating it.** Recorded rather than attempted a
fifth time; the honest read is that a subsystem where the generation path cannot
be traced is a subsystem to rewrite, which is what Addendum 8 said before any of
this began.

**1,402 tests pass.**


## Addendum 24 — the ornament the module was written to fix was still broken

`ornament_realization.py` opens by naming its purpose: ornaments were engraved
and then silent, and "an appoggiatura sounded exactly like an acciaccatura". A
comment in `midi_renderer.py`, directly above the call, repeats the claim as
finished work.

It was not finished. Checked with the renderer's own call signature:

```
appoggiatura    -> 0 sounding notes    <-- SILENT
acciaccatura    -> 0 sounding notes    <-- SILENT
trill           -> 5 sounding notes
mordent         -> 3 sounding notes
turn            -> 5 sounding notes
schleifer       -> 3 sounding notes
```

Four of six ornaments realized; the two the docstring singles out did not.
`realize()` returns `[]` for both unless it is given `grace_midi`, because an
appoggiatura is a **pair** — the small note and the note it leans on — and the
renderer iterated one event at a time and never supplied the other. Both fell
through to a plain short note on the beat, which is the original bug exactly,
sitting underneath a comment saying it was gone.

The parameter is why it read as correct. `realize_event`'s fifth argument was
called `principal_midi` while its value flows into `realize(grace_midi=...)`;
at a call site passing `key`, `tempo_bpm` and `period`, an omitted argument
named "principal" reads as a sensible default rather than the missing half of
a pair. Renamed to `grace_midi`, with the trap written into the docstring.

Fixed by pairing the two events before the render loop (`_pair_graces`), which
also stops the grace sounding twice. Verified by reproducing the original
failure — the two now differ, and differ *correctly*:

```
appoggiatura  [('0',    '1/2', 74, 1.1 ), ('1/2', '1/2', 72, 0.88)]   leans ON the beat
acciaccatura  [('-1/16','1/16',74, 0.85), ('0',   '1',   72, 1.0 )]   crushed BEFORE it
```

All 12 workspace pieces still render.

**Honest scale.** Only **2 appoggiaturas exist across every piece this system
has composed**, so as a bug fix this is worth two notes today. The number that
matters is the other one in the same census: `grace` 28, `trill` 24, `turn` 61,
`appoggiatura` 2. The composer almost never reaches for the leaning ornament —
and the craft doc explains why, calling `:grace` "the unspecified fallback"
with nothing said about when a lean is wanted. In Baroque and Classical writing
an unmarked small note is normally read as a long appoggiatura, and in a slow
movement that dissonance is where the expression lives. The guidance now says
so, and says what each mark does to the sound. That is the part likely to
change how the output sounds; the renderer fix is what makes the advice true.


## Addendum 25 — orchestral parts nobody could play

Counting notation marks per staff-bar across every assembled score, against the
real-corpus census (0.11–5.71, median 1.58), the current-pipeline pieces sit
healthily at 1.14–2.50. Two outputs did not, and both were **orchestrations**:

```
mozart-andante-fmaj-v2-20260826             2.21 marks/staff-bar   (piano core)
mozart-andante-fmaj-v2-20260826_m1_a_orch   0.63                   (same music, orchestrated)
beethoven-orch-cmin-20260826_m1_a_orch      0.68
```

Orchestrating shed two thirds of the notation. `_event_dict` was not the
culprit — it carries every field the dataclass declares, deliberately. The
losses were in what orchestration *adds*:

- **Wind pads were built with a literal `"dynamic": None`.** The horn, clarinet
  and bassoon received sustained chords carrying no marking at all, while the
  bar's loudness rank sat in a local variable one line above. Now marked via
  `pad_dynamic()`, one step below the texture they support — the standard
  balance instruction, and why a horn chord under a singing oboe is p and not mf.
- **Every part not derived from the melody arrived blank.** Dynamics live on the
  piano core's melody layer, and each part inherits only the marks on its source
  events: cello 60 notes / 0 dynamics, violin I 48 / 0, violin II 48 / 0, viola
  and horn 0 of everything. `_mark_part_dynamics` now gives each part its own,
  written where a copyist writes them — at entry and on each change, never bar
  after bar (which is what `detect_notation_spam` rightly fires on).

Verified by reading the assembled MusicXML back: **no part is unmarked**, and
marks per staff-bar went **0.63 → 1.06**, toward the real median of 1.58. Five
regression tests, including one that the composer's own mark is never
overwritten.

### And one finding that did not survive its own check

Along the way the LayerIR showed **47.9% of all dynamics as redundant
duplicates within a single staff-bar** — against a measured real-score rate of
6.7% mean / 26.2% max over 63 engraved scores. Six pieces were above the real
maximum. It looked like a clear defect and I had the fix half-written.

Then I measured the **assembled MusicXML**, which is the thing anyone actually
reads or hears: **3.3%, below the real-corpus mean.** The assembler already
dedupes (`("dyn", offset)`), and those duplicates never reach the page. The
LayerIR redundancy is real and harmless.

No fix, because there was nothing wrong with the output. Recorded because the
near-miss is the point: I measured an intermediate representation, found a
number 7× worse than real music, and would have "fixed" a non-problem had I not
read the artifact back. That is the same lesson as
`project_assembler_voice_bug` pointing the other way — the intermediate and the
page disagree in both directions, and only the page counts.


## Addendum 26 — string parts with no bowing in them

The same readback that found the unmarked orchestral parts showed the strings
carrying no slurs: cello 60 notes / 0, viola 0, and the wind pads likewise. For
a string player the slur **is** the bowing, so a cello part without one tells
the player nothing about how to draw the bow.

Ground truth first, per part, over 82 real multi-part scores — as a RANGE, since
a mean is not a bound:

```
violin  n=103  min  1.4  median 14.9  max 26.5   slurs per 100 notes
viola   n= 51  min  1.0  median 11.4  max 24.5
cello   n= 49  min  0.3  median  9.5  max 21.6
```

Parts built from the melody inherit its slurs and come out fine. Parts built
from the **bass** inherit nothing, because a pianist's left hand is not phrased
the way a cello is bowed — this is material orchestration has to *add*, like the
doublings beside it. `_bow_string_parts` slurs a conjunct run inside one bar and
takes a bow change at every leap, repetition, rest and barline.

Two of my own bugs, caught by measuring instead of assuming:

- Slurring every stepwise **pair** gave 25 slurs per 100 notes — nearly twice
  the real median and above the real max for cello. Raised to runs of three.
- `"bass"` in the instrument-key tuple **substring-matches `bassoon`**, a double
  reed that has never been bowed. Both now have regression tests.

On a deliberately all-stepwise test line the rule produces 18.8 per 100 — inside
the real cello range (max 21.6), and lower on real bass lines, which leap. The
leaping bar is left unbowed, which is both the corpus-safe outcome and simply
how the passage is played.

**Scope, honestly stated:** on the andante this changed nothing, because its
cello and violins already carry the melody's phrasing and its viola has two
notes. The rule fires on bass-derived string parts, which is where the zeros
were. It is one measured, bounded, tested improvement, not a transformation.


### Addendum 26, corrected — two things I got wrong in the measurement above

**The wind question cannot be answered from this corpus.** Extending bowing to
the winds looked justified: cello and viola were at zero, and so were clarinet,
bassoon and horn. Measuring first gave an unambiguous-looking answer — 16/16
oboe parts, 23/23 horn, 26/26 trumpet, *exactly* zero slurs, 100% of them.

A measurement that returns exactly 0 for 100% of cases is a reason to distrust
the measurement. Every wind-bearing multi-part score in the sample is a **Bach
chorale** (`bwv1.6`, `bwv12.7`, `bwv120.8-a`, …), which mark no slurs at all,
in any part. The sample says nothing whatever about wind writing. No change
made — the honest outcome is that the available corpus cannot answer it, which
is `project_corpus_is_one_genre` arriving from a new direction.

**My own string minima were an artifact.** The measurement filtered on
`if k in nm and s:` — parts with at least one slur — so every zero-slur part was
excluded before the range was taken. The reported minima (violin 1.4, cello 0.3)
are a floor of that filter, not of real music, and the comment I wrote beside
them — "a part at 0 is not a stylistic choice, it is a part with no bowing in
it" — is simply false for a chorale transcription.

The rule is unaffected: it uses only the **maximum** as a ceiling, and excluding
zeros cannot lower a maximum. But the claim attached to it was wrong, and the
code comment now says the numbers license an upper bound and nothing else.


## Addendum 27 — a turn that found nothing, written down so it is not repeated

Ran the system's own read-back audit (`realism_report`) over every assembled
score. The current-pipeline pieces come back essentially clean:

```
audit-andante-fmaj-20260826       0 findings
audit-minor-dm-20260826           0
bach-fugue-amin-20260826          0
bach-invention-dm-20260826        0
mozart-andante-bb-20260826        0
mozart-andante-fmaj-v2-20260826   0
chopin-nocturne-ebmaj-20260826    1   -> 0 once the composer is passed
palestrina-motet-dorian-20260826  1
```

Everything that looked like a defect this turn dissolved under checking:

1. **`accompaniment_vocabulary_poverty` on the Chopin nocturne**, citing "an
   absolute floor of 6" — which the detector's own docstring says is used *only*
   when the composer's distribution is unavailable, and Chopin's own range is
   3-11. It looked like the exact "optional param silently selects the wrong
   yardstick" bug. It was my probe: `realism_report(f)` with no composer. The
   real call site passes `composer=resolved`, and with it the finding is gone.
2. **Bass-register notes apparently in the right hand** (bars 19-20, 25-26: A2
   and D3 interleaved with D5/A5). My reading grouped LayerIR layers into hands
   by guesswork. In the assembled score — where staff assignment is ground truth
   — **zero** bars have a staff spanning more than two octaves.
3. **Melodic bars repeating verbatim** (bar 17 = bar 22, bar 30 = bar 15). Real
   Mozart and Beethoven movements repeat melodic bars 0-42% of the time, median
   23.5%. This andante: **17.1%**, below the median. Real music repeats itself
   *more*. This is the second time this diagnosis has been made and falsified,
   which is why it is now written down.
4. Two further probe errors: reading `finding["check"]` when the key is
   `detector`, and a wind-slur measurement that turned out to be entirely Bach
   chorales (Addendum 26, corrected).

**No fixes this turn, and the count stays where it was.** The useful result is
the negative one: the mechanically detectable surface on these pieces is
worked out. What `realism_report` itself lists as beyond it —

```
"whether the theme is memorable"
"whether the harmony is beautiful rather than merely correct"
"whether the piece is worth hearing twice"
```

— is what remains, and none of it is reachable by another detector. It needs the
fresh-ears `music-critic` listening to the preview.


## Addendum 28 — the engine fallback reached the page unengraved

`expression_enricher` is the engraver's pass: it fills the slurs, articulation,
hairpins, dynamics and pedal the composer left blank, it is period-gated (no
pedal for Bach, no dynamics for Palestrina), and it only ever writes a field
that is `None`. Addendum-era work wired it into the **agent** path, inside
`_gated_commit`.

It was never wired into the **engine** path — `run_scales_section`, which is the
path taken by every phrase the agent did not author. Measured on a fresh
three-phrase section:

```
before:  229 events   dynamic 60   slur 0   articulation 0   hairpin 0   pedal 0
after :  229 events   dynamic 60   slur 22  articulation 90  hairpin 12  pedal 2
```

Zero slurs and zero articulations, dynamics only, straight from the realizer.
That is precisely what the 0.00-marks-per-bar scores in `workspace/` are, and
it is the same class of defect as `project_dead_modules_20260826`: a complete,
tested, period-aware module that one of the two paths simply never called.

`_engrave_phrase` runs before `graph.commit_phrase` and mutates the layer in
place, so the enrichment survives the commit; its report is now returned under
`result["engraving"]`, beside `engine_repairs`, so a reviewer can separate the
engraver's marks from the engine's. Five regression tests, including one that
pins the call site itself — because the defect was never in the enricher, it was
that nothing on this path called it.

**Two probe errors worth recording**, both of the "checked a field that does not
exist" kind: `PhraseState.engraving` is never set on *either* path (the report
goes into the returned dict, not onto the phrase), so my "0 phrases carry an
engraving report" reading was measuring nothing. Neither changed the fix.


## Addendum 29 — path parity: what the engine never did

Addendum 28 was found by asking a different question than "is this piece any
good": *which code paths skip a step another path takes?* That question is
mechanical, so it can be asked mechanically. Diffing the calls made by
`_gated_commit` (agent) against `run_scales_section` (engine fallback):

```
steps the AGENT path takes that the ENGINE path does not:
    _capture_theme_if_first_statement
    _craft_check_phrase
    _settle_expectations
    run_commit_gate
    validate_tempo
```

`run_commit_gate` is by design (the engine has `_repair_engine_surface`
instead), and craft checking reaches the engine by another route. Two were real:

**The principal theme was never captured.** It is captured from the phrase that
first states it, on commit. When the engine realizes the opening section — the
usual case for a fallback — nothing captured it:

```
before:  principal_theme_phrase() -> ''
after :  principal_theme_phrase() -> 'm1_a_p1'   (surface stored, survives save/load)
```

A piece cannot have a memorable theme if nothing ever recorded what the theme
was. Everything downstream — theme return, development, recurrence checking —
was reading an empty theme and finding, correctly, nothing.

**Expectations were never discharged.** Promises recorded at plan time and never
closed leave every debt open for the whole piece, which is the exact bug
`_settle_expectations` was written to fix on the other path.

Three call-site tests, plus one pinning the agent half so a later change cannot
quietly drop it, plus one asserting capture happens *after* the commit it reads.

**A probe error, again of the same family:** `principal_theme_id` came back `''`
and looked like the "populated theme whose id is empty" bug the capture
function's own docstring describes. It is not — the id names a motif in
`motif_bank`, and my probe called `build_form_graph` without the planning step
that populates it. Correct behaviour on an input a real run does not produce.


## Addendum 30 — the source scores were read with their markings stripped off

Generalising Addendum 29's question — *which paths skip a step another path
takes?* — over every function that writes a realized surface into the graph
left one real candidate: `reduce_to_piano`, one of the six documented modes,
writing `PhraseState` directly. (`load_source_score` also does, correctly:
source material must not be re-engraved. The `piece_graph.py` entries are the
storage primitives.)

Reducing a real Clara Schumann polonaise — 7 written dynamics, 27 slurs — gave:

```
before:  296 dynamics printed over 80 bars (3.70/bar)   0 slurs   0 articulations   0 ties
after :    6 dynamics                      (0.07/bar)  44 slurs  10 articulations   6 ties
```

Two separate defects, one of them much bigger than the mode it was found in.

**Dynamics were stamped on every carried note.** 313 marks from a source holding
7. Real per-part rates, measured over 212 parts: min 0.03, median 0.24, **max
0.85** per bar. At 3.70 the reduction was 4.4x the loudest real part.
`_thin_carried_dynamics` collapses an unbroken run within one layer.

Note what it deliberately does *not* do. My first plan was to suppress any
dynamic restating the level already in force, in the assembler, fixing every
path at once. Measuring first killed it: **36.1% of real dynamics restate the
current level** — a reminder after a gap is correct engraving. Only unbroken
runs collapse.

**The extractor never read the marks at all.** `parse_musicxml_to_events`
returned pitch, duration and dynamic and nothing else, so *five of the six
modes* — `reduce_to_piano`, `orchestrate`, `variation`, `style_transfer`,
`continue_piece` — saw every source score with its articulation, phrasing,
ornaments and ties removed. The reduction could not preserve phrasing it was
never shown, and neither could any of the others.

Slurs are **spanners**, not note attributes, which is why reading
`element.articulations` alone found none of them. `_get_marks` now reads
articulations, expressions, ties and spanner endpoints; `RoleEvent` and the
bimanual packer carry them through. Verified by round-trip: 27 source slurs
extract as exactly 54 endpoints.

Six regression tests on extraction, plus the reduction's own numbers above.


## Addendum 31 — the crescendos were silent

Another structural question, asked mechanically: **which fields can be written
but are never read on export?** Checking every `LayerEvent` field against the
assembler, the MIDI renderer and the EventIR conversion:

```
field         assembler   midi
role              -         -     (metadata, correctly not engraved)
source_layer      -         -     (metadata)
slur             yes        NO
hairpin          yes        NO
expression       yes        NO    (text; does not sound)
pedal            yes        NO
fingering        yes        NO    (does not sound)
```

Text and fingering do not sound. A hairpin and a slur do, and the MIDI preview
is what the music-critic listens to.

**Hairpins were completely inaudible.** Rendering the same phrase with and
without a written crescendo produced byte-identical velocities:

```
before   no hairpin: [81, 74, 82, 76, 92, 83, 97, 85]
         with '<'  : [81, 74, 82, 76, 92, 83, 97, 85]   identical

after    no hairpin: first->last  +4
         with '<'  : first->last +33
         with '>'  : first->last -27
```

Every crescendo the composer wrote, the enricher added and the assembler
engraved was, to the only listener in the loop, not there. `_hairpin_scale`
ramps +-18% across the span — narrower than a step between written dynamics,
because a hairpin shapes the current level rather than replacing a new marking.
A hairpin closes on `!` **or at the next dynamic**, which is how one actually
ends: it leads INTO the new level.

**Slurs did not play legato.** Articulation was audible — staccato,
staccatissimo, spiccato, portato and tenuto all gate the duration — but the slur,
which is the mark the enricher adds most of, did nothing. Now `1 + tenuto_extend`
on notes under a slur, and only where the composer wrote no articulation of
their own (a staccato inside a slur is portato, and their mark decides).

**The measurement trap, worth recording.** My first verification said the slur
fix did nothing: note lengths came back `[1.0, 1.0, ...]` either way. music21's
MIDI reader **quantizes durations to musical values**, so a 1.12x extension
reads back as exactly 1.0. In raw ticks: `10080 -> 11290`. A round-trip through a
notation-aware parser is the wrong instrument for measuring a sub-notational
change, and it fails by reporting *no difference* rather than by erroring.


## Addendum 32 — there was no pedal, and it was on for the harpsichord

Following `pedal`, the last unread field from Addendum 31.

**The preview had no pedal at all** — not one controller event in the file. What
stood in for it was lengthening bass notes in bars the renderer picked, which
sustains one hand, ignores any pedal the composer wrote, and cannot blur a
harmony the way lifting the dampers does. For Romantic piano writing that is not
an effect on the sound, it is most of the sound. `_insert_sustain_pedal` now
writes real CC64 (music21 has no stream-level pedal, so the written file is
reopened, converted from delta to absolute time, merged, and re-delta'd), fed
from both the period-derived `PerformanceIR` **and** any pedal the composer
wrote — the second of which the renderer had never consulted.

**And the pedal was on for instruments that do not have one.** `pedal_lead_ms=0.0`
was the only thing standing for "harpsichord: no pedal" — a release timing, not a
prohibition — so `build_performance_ir` generated pedal bars for Bach (16 in a
two-part invention) and Palestrina all along, silently stretching their bass
notes. Emitting real CC64 would have made that a damper pedal on a harpsichord
and on unaccompanied voices. Profiles now carry an explicit `uses_pedal`, and
the generation is gated on it:

```
bach        period=baroque      uses_pedal=False   sustain events 0
palestrina  period=renaissance  uses_pedal=False   sustain events 0
chopin      period=romantic     uses_pedal=True    sustain events 72
mozart      period=classical    uses_pedal=True    sustain events 70
```

**Palestrina was reporting himself as baroque.** `"renaissance"` mapped straight
onto the baroque profile *object*, so `profile.period` answered "baroque" for
every Renaissance piece. The performance values are shared deliberately; the
label was wrong, and `profile.period` is read to decide period-specific
behaviour. Renaissance now has its own labelled profile.

### Three measurement errors in one investigation

Worth recording together, because they are the same mistake at different sizes:

1. `build_performance_ir(layer, slot, prof)` — the third positional is
   `phrase_type`, not `profile`. The profile defaulted, so my "Bach still has 16
   pedal bars" reading was measuring the default profile, not Bach's.
2. Counting sustain events as `parameter1 == 64` — **a NoteOn's `parameter1` is
   its PITCH**, so this counts every E4 in the piece. That is the entire source
   of "Bach still has 30 pedal events" after the gate was already working.
3. Detecting controller events by `str(event.type).find("CONTROLLER")` — music21
   renders the type as the number `176`, so this matched nothing and reported a
   correct insertion as a failure.

Each produced a confident, specific, wrong number, and each was caught only by
instrumenting the code path rather than trusting the probe. The fix under them
was correct the whole time.


## Addendum 33 — the grammar round-trips; the composer under-uses it

Structural sweep of the **notation grammar** itself: every suffix the craft doc
tells the composer they may write, taken through the parser and then through the
assembler to MusicXML.

**All 48 tokens survive.** Ornaments, articulations, techniques, dynamics, pedal,
character text and fingering each set the field they claim to and each appear in
the engraved output. No defect. (One false alarm on the way: `:arp` looked lost
until I noticed my fixture wrote it on a SINGLE NOTE, where a roll is meaningless
— on an actual chord, `arpeggiate` reaches the page for all three spellings.)

So the engraving layer is sound and the gap is in what gets **written**. The
craft doc claims three things are never used; ties are measurable:

```
real keyboard scores (n=103): ties per bar  min 0.000  p25 0.061  median 0.348  max 3.941
                              19 of 103 have ZERO ties
this system (5,848 bars):     0.008 per bar
```

A fortieth of the median, below the 25th percentile. **Not a violation** — zero
is legitimate, and a fifth of real scores do it, mostly strict counterpoint where
each voice is its own line. But it is a systematic tendency across every piece
rather than a choice made per piece, and no code can correct it: the engraver's
pass fills only blank fields and never changes a duration, so it cannot add a
tie. Guidance now carries the measured distribution, the same treatment that the
grace-note default got in Addendum 24.


## Addendum 34 — styles anchored on corpora too thin to teach anything

Structural sweep of the composer/style surface: 27 composers have a corpus on
disk, so `style_members` counts all 27 as members of their styles. But "has a
corpus directory" is not the same question as "can this corpus anchor a brief",
and `composer_coverage_tier` already answers the second one. CLAUDE.md states
the rule — a thin corpus reports tier C "rather than pretending it can teach a
voice" — and nothing consulted it here.

```
style            members  thin  bars from thin corpora
modern              1       1     16  (100.0%)   bartok
nationalistic       4       3    856  ( 53.4%)   dvorak 46, mussorgsky 458, rimsky-korsakov 352
impressionist       2       1    342  ( 27.3%)   debussy
late-romantic       3       1     27  (  2.2%)   bruckner
```

**"Compose in a modern style" was anchored entirely on sixteen bars**, and half
of `nationalistic` was the same kind of stub. `style_members` now takes
`usable_only`, defaulting on; `modern` reports itself unsupported and names
bartok as what to acquire, which is the behaviour the docs describe for an
unknown composer and never applied to a thinly-armed style.

Deliberately unchanged: a **direct** request for a thin composer still resolves.
Asking for Debussy by name is a decision the caller makes with the coverage tier
reported to them; it is style membership that was doing the silent substituting.

Also visible in the sweep and **not** fixed: `corelli` is labelled genre "string
quartets". He died in 1713 and the genre did not exist — the classifier is
guessing, and 15 of 27 composers come back "unclassified". Recorded rather than
patched, because the genre label feeds the narrowness warning and I have not
measured what changing the classifier would do to it.

**Test-suite note, reported rather than smoothed over.** Two runs under random
ordering showed failures (9, then 1) that I could not reproduce in three
subsequent runs; fixed-order and later random-order runs are clean at 1503. This
session has hit repeated half-written-file transients from other sessions editing
the repo concurrently, and that is the likeliest cause, but I could not identify
the failing test and am not claiming it is nothing.


## Addendum 35 — "we cannot tell" was being reported as "it is broad"

Following up Addendum 34's deferred item — the genre classifier — by measuring
it, which is what I said I had not done.

`corpus_scope().narrow` is False whenever the dominant genre is unknown, and
`render_corpus_scope` returns **nothing** when narrow is False. So a corpus whose
sources cannot be identified produced silence, and silence reads as "this corpus
is broad enough, carry on". That happened for **18 of 27 composers**.

This matters more than a label. `project_corpus_is_one_genre` is a recorded
lesson precisely because a narrow corpus makes every statistic in the brief
describe a genre rather than a composer. The warning existed; it could not fire
for two thirds of the roster, and its absence was indistinguishable from a
clean bill of health.

```
before:  narrow 6   "broad" 21   (of which 17 were actually unknown)
after :  narrow 6    broad  4     unknown 17  — and unknown now says so
```

**Haydn was the sharpest case.** The general table classifies his quartets by
music21's `opusNNnoN/movement` convention, but a third of his bars are filed as
a bare `movement4`, so his dominant genre came out as *unclassified at 35%* and
a corpus that is two-thirds string quartets said nothing at all. A pattern loose
enough to catch `^movement\d+$` cannot go in the general table — it would swallow
half of every other corpus — but scoped to the composer whose corpus is known to
be one genre it is simply true. Now:

```
haydn: string quartets 67.0% | piano sonatas 23.9% | oratorio 4.5% | songs 2.7% | unclassified 1.9%
```

Note the outcome: Haydn is **correctly** reported as not narrow. His corpus
really is mixed. The difference is that this is now a measured answer instead of
a 35% plurality of "don't know" — the verdict is the same and the basis for it
is real.

**Probe error, tenth of the session:** my first baseline reported all 27
composers unclassified, because `corpus_scope` returns `dominant`, not
`dominant_genre` (that key exists, but on `composer_coverage_tier`). Two dict
keys for one concept, which is the shape `feedback_contradictory_guidance`
warns about.


## Addendum 36 — every phrase was told it was the climax

Reading the brief the composer actually receives (19,376 chars, ~4,800 tokens,
27 sections), line 28 of the FIRST phrase of a nine-phrase andante said:

```
WHERE YOU ARE: this is the CLIMAX of the whole piece. Everything before has
been building to it and everything after subsides from it. It must be the
highest, densest, most harmonically charged moment ... write the peak.
```

Line 31 of the same brief called the same phrase a "presentation". Checking all
nine: **9 of 9 phrases were told they were the climax of the whole piece.**

`PhraseSlot.climax_distance` defaults to `0`, and `0` *means* "this phrase is
the climax". Any phrase the dramatic planner never touched therefore claims the
peak. Across `workspace/`:

```
pieces where EVERY phrase is told it is the climax: 9
  mozart-andante-fmaj-v2-20260826    9/9      (created today)
  var-of-andante-20260826           11/11     (created today)
  montana-seasons-sonata-dm-20260406 56/56
  ocean-gm-20260419                 10/10     ... and five more
```

A piece in which every phrase is written as the highest, densest, most charged
moment has no arc at all — which is the exact failure `dramatic_plan.py` was
built to fix (`project_dramatic_plan_20260826`: "every phrase was locally
optimal and the piece had no arc"). The planner works: a freshly planned ternary
gives roles `establish → extend → confirm → depart → intensify → retreat →
return → confirm → close` and distances -4…+4, exactly one at 0, surviving
save/load. The defect is that **a phrase with no plan is indistinguishable from
the planned peak**, and two pieces made today are in that state.

Fixed at the reader rather than by chasing every phrase-creating path: the
planner always sets `dramatic_role` alongside the distance, so an empty role is
the reliable "no plan ran" signal. Such a phrase is now told exactly that —
"this phrase has no dramatic plan ... Do not assume this is the climax" — which
is both true and useful, where silence would have let the composer assume.

```
mozart-andante-fmaj-v2-20260826   phrases claiming the climax: 9/9 -> 0/9
chopin-nocturne-ebmaj-20260826    phrases claiming the climax: 1/9 -> 1/9  (correct, planned)
```

The dangerous default is now documented on the model field itself, since
`0 == "I am the peak" == "nobody has looked at me"` is a trap any future reader
will fall into.


## Addendum 37 — the brief was lying to the composer about its own piece

Continuing to read the brief as the composer receives it. Its most emphatic
section is headed **"the five things this system has measurably never done"**
and states, with numbers:

```
• ARTICULATE.  The last generated score had ZERO articulation marks in 41 bars.
• TIE ACROSS BARLINES.  The last generated score had ZERO ties.
• VARY THE CADENCE.  ...closed SEVEN of its NINE phrases with the identical rhythm.
• DON'T WALK SCALES.  ...the last generated score ran 39%.
• USE THE WHOLE KEYBOARD.  ...spanned 19 across 41 bars.
Also available and never yet used: :arp ..., :ped ...
```

All of it hard-coded. Measured against the very piece whose brief printed it:

```
chopin-nocturne-ebmaj-20260826 (82 bars)
   articulation marks  19    brief: ZERO
   ties                 2    brief: ZERO
   pedal marks         82    brief: ":ped never yet used"
   arpeggiate           4    brief: ":arp never yet used"
```

**Four falsehoods, stated with numbers, in the section the composer is most
likely to act on.** ":ped never used" actively discourages the pedal in a
nocturne that is pedalled throughout, and a brief that is wrong about the piece
in front of it spends the credibility of everything true around it — which in
this brief is most of 4,800 tokens.

The corpus ranges bundled with those claims are real and stay (0.11-5.71 marks
per bar, 0-15% scalar, 24-49 semitones). What is gone is every assertion about
generated output that a module constant cannot know. In its place, measured from
the graph:

```
MARKS SO FAR (41 committed bars): articulation 19, tie 2, slur 24, pedal 50,
arpeggio 1, ornament 6.
```

and, when something genuinely is unused, it is named as such rather than
assumed — the Mozart andante correctly reports "Nothing in this piece has used:
arpeggio". On the first phrase it says so instead of printing zeros.

This is the same defect class as Addendum 36 one section earlier: **a default or
a constant standing in for a measurement, and reading as fact.** Two of the
brief's most forceful passages were both saying something untrue about the piece
being composed, and both were only visible by reading the brief itself rather
than the code that builds it.


## Addendum 38 — the canonical patterns were never transposed

Reading further into the brief the composer receives. Under

```
LH VOCABULARY (canonical chopin patterns, transposed to Eb major):
  block_chord_sparse: [G2,G3]q [A2,A3]e [B2,B3]e [C3,C4]e [D3,D4]e [E3,E4]e [F3,F4]e
```

That is C major. A natural, B natural and E natural are **not in E-flat major** —
three pitch classes outside the key the line says it is in, handed to the
composer as material to use.

`transpose_pattern` was a no-op for chords:

```
stored          : [['G2','G3'], ['A2','A3'], ['B2','B3'], ...]
-> Eb major     : [['G2','G3'], ['A2','A3'], ['B2','B3'], ...]   unchanged
-> Bb major     : [['G2','G3'], ['A2','A3'], ['B2','B3'], ...]   unchanged
-> A major      : [['G2','G3'], ['A2','A3'], ['B2','B3'], ...]   unchanged
```

The guard `if pitch == "rest" or isinstance(pitch, list)` returned chords
untouched, and left-hand patterns are mostly chords and octaves. Single notes
transposed, which is why the defect was invisible in an Alberti figure and
glaring in a block-chord one. **`pattern_to_events` delegates to this**, so the
ENGINE's generated left hand was untransposed in the same way — this was not
only a brief-cosmetics bug.

After: `[Bb2,Bb3]q [C3,C4]e [D3,D4]e [Eb3,Eb4]e [F3,F4]e ...` — in E-flat.

**Second defect in the same section.** 30 of 240 sampled patterns (12.5%) lie
entirely above middle C, including 9 of 40 `walking_bass` and 10 of 40
`pedal_point`; the Mozart brief was offering `walking_bass: Gb5s Gb5dq A5s`. A
left hand may sit high, but a walking bass that never descends below middle C
contradicts its own label — almost certainly the two-voice staff split handing
an inner line to the left hand. Retrieval now prefers patterns that reach the
bass for textures whose name names it, with a fallback so it can never return
nothing: 30/240 → 7/240, and the remaining seven are block-chord textures, which
may legitimately sit high.

The preference had to be applied **during** candidate collection, not after: the
brief asks for `n=1`, the pre-filter cap is `n*3`, and three high candidates
exhausted the pool before any post-filter could act.

### The failing tests are another session's edits, with evidence

The suite reported 5-12 failures across runs, all of them `inspect.getsource`
assertions reading misaligned source fragments (`assert '_gated_commit' in
'        "punctuation",\n'`, and a `SyntaxError` on a mid-expression line).
`getsource` resolves line offsets from the imported code object against the file
on disk, so it breaks if the file changes mid-run.

```
before run: scales.py mtime 23:19:29
after run : scales.py mtime 23:22:02      <- changed DURING the run, not by me
```

In a fresh process `getsource` returns correct sources for every one of those
functions. This session's own 65 tests pass together. Recorded rather than
"fixed": there is nothing wrong with the code, and the repo has had another
session writing to it throughout.


## Addendum 39 — `[Ab5,Ab5]` is not a chord

Reading the EXEMPLARS section — the real corpus bars the composer is told to
adapt, and the most concrete material in the brief:

```
RH: C5e Bb4e D6e C6e Bb5s Ab5s G5s [Ab5,Ab5]s C5s D5s Eb5h D5e
```

Two voices doubling one pitch arrive from the extractor as a two-note "chord".
Across the corpus: **1,471 of 139,923 chords (1.05%)** repeat a pitch — schubert
1,165, chopin 172, bach 52. `['G5','G5']` is a true unison in the score and a
nonsense chord in shorthand, printed as material to adapt.

Fixed at RENDERING, not in the data: the doubling is a real fact about the voice
leading and the bar records keep it. `[Ab5,Ab5]s` now renders `Ab5s`.

The same duplicate also counted as thickness in `voicing_profile`, which reports
"the melody is doubled in thirds or sixths ... 2.3 notes on average". Corrected
to count distinct pitches — **and the effect is negligible**:

```
                 before            after
schubert      0.196 / 2.45     0.195 / 2.44
rachmaninoff  0.566 / 2.71     0.566 / 2.69
```

1% of chords barely moves an average. Recorded honestly: the statistic was fixed
for correctness, not because it was misleading anyone. The display half is the
half that mattered.

### The intermittent suite failures: closed

Bracketing a full run with the file's mtime settles it:

```
run with failures:  scales.py  23:19:29 -> 23:22:02   (changed mid-run)
clean run        :  scales.py  23:22:59 -> 23:22:59   1547 passed, 0 failed
```

Every failure was an `inspect.getsource` assertion reading a misaligned
fragment, and `getsource` resolves line offsets from the imported code object
against the file on disk. Another session has been writing to this repo
throughout. I called this transient roughly ten times on circumstantial grounds;
this is the measurement that actually establishes it.


## Addendum 40 — the fix from Addendum 37 had not propagated

Addendum 37 removed the frozen claims from the brief. Reading the **agent
instructions** — the other thing a phrase-composer reads before writing a note —
the same claims were still there, in six places across four documents:

```
.claude/agents/phrase-composer.md:109   "closed seven of its nine phrases with the identical gesture"
.claude/agents/phrase-composer.md:129   "on 164 real phrases the field held a value ten times"
.claude/agents/phrase-composer.md:167   "the last piece ... had zero of both in 41 bars"
.claude/agents/phrase-composer.md:175   "spanned 19 across 41 bars"
.claude/agents/phrase-composer.md:180   "Seven of the last piece's nine phrase endings"
.claude/context/general/melody-craft.md:86          "ran 39% of its melody bars"
.claude/skills/w-review/SKILL.md:56                 "the last piece measured normal density"
.claude/skills/w-compose/.../note-writing-craft.md  four more
```

Every one of them false of current output. Checked against real pieces:

```
claim: "zero articulations and zero ties"    actual: 19 articulations, 2 ties
claim: "seven of nine identical closings"    actual: 5/9, 3/9, 2/9 across three pieces
```

The tendency each claim describes is real — 5 of 9 identical closings is still
too many — but the numbers are from one piece in one session, quoted as
diagnosis. Each has been rewritten to keep its **corpus** figure (median 2%
scalar bars, 24-49 semitones, median 9% repeated pitches, 0.57 articulations per
bar) and to point at the live sections that report what THIS piece has done:
MARKS SO FAR, RANGE SO FAR, CADENCES ALREADY USED.

`tests/test_no_frozen_output_claims.py` is the propagation guard: it fails on any
`.claude/` document that asserts a fact about generated output, parametrised over
all 550 docs. That is the actual defect here — not the six stale sentences, but
that **fixing the brief alone left five of them live**, which is
`feedback_contradictory_guidance` exactly ("propagate every guidance change to
all the places that restate it"). I wrote that lesson down and then did not
follow it one turn later.

Docs were also checked mechanically while I was in there: every file path
referenced across `.claude/` exists, all 35 documented `from scales.… import …`
statements resolve, and all 45 documented calls match their real signatures.

Suite: **2099 passed** (the parametrised doc guard adds 552), lint clean, and
`scales.py` mtime unchanged across the run.


## Addendum 41 — the critic was handed a self-contradicting number

Auditing the music-critic's own inputs. Its instructions say to read
`musical_prose` first and trust it over the raw metrics. It contained:

```
! The right hand averages 1.14 notes per attack — below the 1.06 minimum of
  every real movement measured. It is one line and nothing else, all the way through.
```

**1.14 is not below 1.06.**

The check itself is correct, and subtler than it looks: floors are
composer-scoped, Chopin's right hand runs 1.30-2.43 notes per attack, and the
applied floor for this nocturne was 1.18 — so 1.14 genuinely fires. What was
wrong was the sentence. It hard-coded `1.06`, which is the **left** hand's
minimum: the wrong hand, arithmetically false against the value printed beside
it, and unrelated to the threshold actually used.

A self-contradicting concern is worse than a missing one. The critic is the
system's only judge of whether the music is any good, and its first instruction
is to trust this prose; a number that visibly does not add up invites it to
discount everything around it — including the two findings in the same paragraph
that were true (a bare single line in 93% of bars, no thirds or sixths anywhere).

Both hand messages now read their threshold out of the applied `floor`:

```
before: averages 1.14 notes per attack — below the 1.06 minimum ...
after : averages 1.14 notes per attack — below the 1.18 floor taken from real movements
```

Checked the neighbouring advice for the same defect: `register_span`,
`registers_used`, `texture_shift_low/high` quote 41, 5-7 and 27-75%, and those
floors do not vary by composer, so their numbers remain accurate. Only
`rh_notes_per_attack` is composer-scoped, and it was the one that had drifted.

`tests/test_advice_agrees_with_its_threshold.py` now asserts the general
property rather than the instance: every number a suggestion quotes must be the
threshold that fired it, and must be arithmetically above the value it is
compared with.


## Addendum 42 — a stale profile discarded, and nothing put in its place

Sweeping every advisory string the system produces for arithmetic
self-contradiction (1,852 lines from real pieces) turned up 16 candidates, **all
of them my regex** grabbing a bar number or a range endpoint as the compared
value. The sentences themselves are sound. Clean negative — Addendum 41's defect
was the only one of its kind.

The sweep did surface a live warning worth following:

```
corpus_profile for 'blend:beethoven+liszt' predates the metric rename
(no melody_direction_change_pct); ignoring it rather than judging a section
against stale numbers.
```

Refusing the stale profile is correct — `self_evaluate` narrows its bands to
mean +- 2 sigma from these numbers, so stale values become the standard a
section is judged against. **Returning `{}` and stopping there is not.** An
aggregate reference has armed members whose profiles are current:

```
tools/compiled_packs/blend__beethoven-liszt/
   corpus_profile.json   Jun 19    <- stale, discarded
   density_stats.json    Aug 26
   ornament_stats.json   Aug 26
```

Every piece composed on that blend was compared against **nothing at all**,
silently, while beethoven's and liszt's own 37-metric profiles sat current on
disk. `_aggregate_members` already resolves `blend:a+b` to its members — the
fallback simply was not wired for this case.

Worse, the remedy the warning named made it undiagnosable: `build_corpus_profiles`
writes per-composer packs and **does not write aggregate ones**, so for a blend
it pointed at a command that could not fix the problem. Nothing in the codebase
writes blend profiles; only a test even mentions them.

Now falls back to a member's current profile and **says so**:

```
using beethoven's current profile instead. This is a SUBSTITUTION, not
'blend:beethoven+liszt''s own distribution — rebuild the aggregate pack to
judge it against itself.
```

37 metrics where there were 0. Silent substitution is a failure this project has
recorded repeatedly, so the substitution is announced rather than slipped in.

Also fixed while here: the rebuild advice said `python -m scripts.…`; CLAUDE.md
requires `.venv/bin/python` for anything touching music21, and bare `python`
resolves to the venv only when it happens to be active.

**Concurrent edits again**, and now diagnosed in one step rather than five:
`scales.py` mtime 23:33:15 -> 23:42:40 across a run that reported 3 failures;
the same suite immediately after, with mtime unchanged, is **2117 passed**.


## Addendum 43 — the same cache defect, in the sibling nobody re-checked

Three statistics are cached to disk under `compiled_packs/<composer>/`:
`density_stats`, `ornament_stats`, `rhythmic_fingerprint`. The first was fixed
in an earlier pass — it "cached to disk with **no invalidation**, so rebuilding
the corpus updated nothing; it was serving targets for textures the corpus no
longer produces". `ornament_stats` was given the same provenance check.

`rhythmic_fingerprint` was not. It validated only that the FORMAT was current:

```
if got.get("schema") == _FINGERPRINT_SCHEMA:   # ...and nothing about the corpus
```

So arming a new member of a style left its fingerprint frozen. Checking every
cache's stored bar count against the corpus actually on disk:

```
style__baroque    cached  6,868 bars    actual 10,914     SERVING STALE NUMBERS
(all 17 others match)
```

The numbers were materially wrong, not merely old:

```
rest_bar_pct           0.2453 -> 0.3316     (35% relative)
dotted_bar_pct         0.2050 -> 0.2345
lh_texture_change_pct  0.6326 -> 0.5648
```

The brief prints these under "RHYTHMIC FINGERPRINT ... these are FACTS ABOUT
HIM", and the rest figure carries the line "music that never stops sounding is
the single clearest tell of a machine" — while quoting a rest rate a third too
low for anyone composing in a baroque style.

**The lesson is the repeat, not the instance.** This is the same defect, in the
same file, in the sibling function, found because the earlier fix was applied to
one instance rather than to the pattern. `tests/test_disk_caches_have_provenance.py`
now asserts the property for all three by parametrisation — planting a cache that
claims a one-bar corpus and requiring each to reject it — so a fourth cache added
later is covered by intent rather than by memory.

**A measurement error worth recording:** my first pass compared cache mtimes to
corpus mtimes and reported four stale `ornament_stats` files. That was the wrong
instrument — an older file is perfectly valid if its bar count still matches, and
`ornament_stats` re-counts on read. Only the content check found the one real
case, and it was in a different function than the mtimes suggested.


## Addendum 44 — a turn that mostly disproved itself

Chased the "silent substitution" pattern into style-targeted briefs, on the
theory that composing "in a classical style" quietly gets one composer. Three
hypotheses, two wrong:

**1. Fingerprints come from one member.** Wrong. A style-targeted brief showed
Haydn's name in every fingerprint line, but `_fingerprints` aggregates properly
— two per member, deduped, capped:

```
style__classical -> 5 fingerprints, from ['beethoven', 'haydn', 'mozart']
style__baroque   -> 5 fingerprints, from ['bach', 'handel', 'vivaldi']
```

My probe detected which composer was NAMED IN THE PROSE, not which supplied the
data. Haydn's fingerprint descriptions say "Haydn"; Mozart's do not say "Mozart".

**2. Style doctrine falls back to one member.** Also wrong, today: every armed
style has its own `cadence_scripts`, `ornament_intents`, `breathing_rules` and
the rest, so the fallback never fires. Measured across all armed styles and five
pack types: **0 substitutions**.

**3. When it does fire, it is silent.** This one holds. `_load_pack`'s fallback
to "a representative armed member" is live code on the path that builds every
style brief, and it would print one composer's cadence scripts under
`STYLE DOCTRINE (this phrase)` with nothing marking them as his. The brief now
names the stand-in when it happens.

Kept rather than reverted for a specific reason: the instinct after disproving
(2) is to drop the instrumentation, and that instinct is what
`project_dead_modules_20260826` records — except inverted. The risk there was
code nothing called; the risk here is a *branch* nothing observes. The notice is
wired into `render_text` and the test drives the fallback directly instead of
waiting for a style to lose a pack.

Two of three hypotheses disproved, one latent defect closed, and the probe error
in (1) is the same one from Addendum 39: measuring the text rather than the data
behind it.


## Addendum 45 — every piece was told to feel the same way

`_creative_intent` builds the CREATIVE INTENT line, and its docstring states the
principle plainly: it "leads with the agent's OWN authored prose
(section.character / .gesture, written at plan time) — the dramatic event that
drives the notes ... (Authoring beats bucketing.)"

`build_form_graph` fills that field itself:

```python
character="; ".join(dict.fromkeys(ROLE_INTENT.get(r, "") for r in roles if r)),
```

So unless someone calls `save_narrative`, the field treated as authored prose is
a bucket label wearing prose clothes. Compared across two finished pieces:

```
chopin-nocturne-ebmaj-20260826   "A nocturne in E-flat major ... in the style of Chopin"
mozart-andante-bb-20260826       "Andante cantabile in B-flat major ... in the style of Mozart"

narrative character, section by section:  identical  True   (all 5 of 5)
```

The phrase-composer's instructions single this line out: *"CREATIVE INTENT — the
dramatic event this passage enacts, in prose. This is the feeling that should
choose the notes. Start here, not from the stats."* It was the same sentence for
a nocturne and an andante, and would be the same for a funeral march.

Boilerplate presented as the piece's identity is worse than an empty field,
which would at least prompt for one. Role-derived character is now detected and
not passed off as authored intent; when that is all there is, the brief says so
and hands over the one thing that IS specific — the request the piece was written
from:

```
(no piece-specific intent was written for this section — the role default above
is generic to the form. What this piece IS: "A nocturne in E-flat major for solo
piano, in the style of Chopin". Decide from that what this moment has to feel like.)
```

**The detector's first version silently did nothing**, and the way it failed is
worth keeping. It split `character` on ";" and asked whether every clause was a
known ROLE_INTENT value — but several ROLE_INTENT values *contain a semicolon*,
so no clause ever matched and it returned False for every real piece. It looked
like a working check, the tests I had written for it passed, and the brief was
unchanged. Rewritten to RECONSTRUCT the expected string: `gesture` is
`" then ".join(roles)`, so the roles can be read back and the character rebuilt
exactly. A check that must recognise machine-generated text should rebuild it,
not pattern-match it.


## Addendum 46 — the readiness report certified the default as authorship

Following Addendum 45 upward: the brief now refuses to present role text as
authored intent, but does anything tell the PLANNER it never wrote one?

`plan_readiness` checks the narrative twice — sections exist, and at least one
has non-empty `character`. A wholly planner-generated narrative passes both,
because `build_form_graph` writes `"; ".join(ROLE_INTENT[r] for r in roles)`
into that very field. So five sections of text identical to every other piece of
the same form were reported as a complete narrative arc. The report was
confirming that the FORM's shape was present, not the PIECE's.

Now caught, and graded:

```
all sections default : "narrative `character` is the planner's own role text on every section
                        — generic to the form, identical for any piece with this shape.
                        Run save_narrative with prose about THIS piece"
some sections default: "still the planner's default on 1 of 5 sections (m1_b)"
authored prose       : silent
```

Both live pieces trip it; a piece with hand-written prose does not — the
falsification matters more than the detection, since a check that fires on real
authorship would just teach people to ignore it.

### A test that passed alone and failed in the suite — twice, for two reasons

Worth recording in full because the second cause is subtle and I have hit it
before.

**First version** copied a real piece out of `workspace/` as its fixture. Another
test mutates that piece during the run, so the copy was of whatever state it
happened to be in. Rebuilt to construct its graph from scratch.

**It still failed.** The remaining cause was the import:

```python
from scales.scales import _WORKSPACE      # binds a COPY, at import time
```

Several tests in this suite `monkeypatch.setattr(scales, "_WORKSPACE", tmp_path)`.
`plan_readiness` reads the module attribute at CALL time, so the fixture wrote
its graph to one directory while the function under test looked in another,
found no piece, and returned an empty report. Alone, nothing had repointed it and
the test passed.

`_workspace()` now resolves the attribute at call time. The general rule: a test
must reach a patchable module attribute the same way the code under test does,
or it is testing a different program than the one that runs.


## Addendum 47 — one test corrupted every test that ran after it

Addendum 46 fixed my own test's import-time binding of `_WORKSPACE`. That is
half the story: a copy only diverges if something repoints the original. Eight
other test files hold the same module-level import, so the question was whether
anything actually leaks.

Instrumented with a temporary autouse fixture comparing `scales._WORKSPACE`
before and after every test in the suite:

```
tests that leave _WORKSPACE repointed: 1
  test_narrative_curves.py::test_narrative_survives_save_load
```

It assigned the attribute directly — `scales._WORKSPACE = ws` — instead of using
`monkeypatch`. From that test onward, **the entire rest of the suite ran against
a temp directory containing one piece.**

Nothing failed loudly, which is why it survived: tests that build their own
fixtures still pass against any directory. The damage landed only on tests
holding an import-time copy of `_WORKSPACE`, which then pointed somewhere
different from the attribute the code under test reads — passing alone, failing
in the suite, in an unrelated file, for reasons visible nowhere near the cause.
That is how it cost two rounds of misdiagnosis in Addendum 46 (I blamed a shared
workspace piece first, rebuilt the fixture from scratch, and it still failed).

Fixed at the source (`monkeypatch`), and then made unreintroducible: an autouse
fixture in `conftest.py` now fails any test that repoints `_WORKSPACE` without
restoring it. **Falsified by planting a deliberate leak** — the guard catches it:

```
guard caught the deliberate leak: True
```

The guard is the point, not the one-line fix. This defect class is invisible at
the call site by construction, so review cannot be the control.


## Addendum 48 — a test of mine that had never checked anything

Addendum 47 left a question: the leaked `_WORKSPACE` meant **1,259 of 2,145
tests** ran against a temp directory with one piece in it. Were any of them
passing vacuously?

Pointing the six workspace-touching files at an empty directory, all still
passed — which proves nothing, since a test that builds its own fixture passes
either way. So I measured the thing that actually matters: **assertions
executed**, with a trace hook counting `ast.Assert` line hits per test.

```
tests that executed ZERO assertions: 19 of 2145
```

Most are legitimate: `test_every_meter_checks_without_error[meter0..2]` and the
malformed-meter cases assert nothing on purpose — the property is "does not
raise". Zero assertions is not the same as vacuous.

**One of them was mine**, written two addenda ago:

```python
pr = PatternRetriever()
for texture in sorted(_BASS_TEXTURES):
    before = pr._by_texture.get(texture, [])
    if before:                       # <- never true
        assert pr.retrieve(...), texture
```

A fresh `PatternRetriever` starts with an EMPTY `_by_texture` — it populates on
`_ensure_loaded()`, which `retrieve()` calls internally. So the guard was false
for every texture and the test executed no assertions at all. It passed from the
day it was written, in the same commit whose whole point was that a fallback must
never return nothing. Now loads first, and asserts the guard itself is non-empty
so it cannot silently go hollow again.

**And the fix exposed a second defect in the same set.** With the library
actually loaded, two of the six textures I had listed as bass idioms match
nothing:

```
library texture labels: 16
_BASS_TEXTURES that resolve      : alberti, bass_melody, pedal_point, walking_bass
_BASS_TEXTURES that never fire   : broken_octave, oom_pah
```

Two names that could never match anything — the dead-label shape recorded in
`project_dead_label_vocabulary`, introduced by me while fixing something else.
Replaced with `walking_bass_chromatic`, which is a real label with 414 patterns
and now gets the grounding check it should always have had (0/20 ungrounded).

The lesson is uncomfortable and worth keeping: **the test I wrote to prove a
fallback works never ran its assertion, and the constant it iterated contained
names the data never uses.** A green suite said both were fine.


## Addendum 49 — two more tests that had gone quiet

Working through the remaining zero-assertion tests from Addendum 48. Most are
legitimate: `test_every_meter_checks_without_error` and the malformed-metre
cases assert nothing because the property IS "does not raise", and
`test_there_is_no_skip_gate` raises on violation so a clean pass executes no
assert. Two were not.

**`test_an_empty_exemplar_result_says_why` had stopped testing anything.** It
was written against handel and schubert, whose records underfilled their metre
and who returned zero exemplars with zero explanation. Both have since been
re-acquired:

```
handel     exemplars=4 warnings=0   -> test branch DORMANT (skips)
schubert   exemplars=4 warnings=0   -> test branch DORMANT (skips)
```

so `if exemplars: continue` skipped every case. The behaviour it guards — an
empty result explaining itself — was no longer checked at all, and the fix that
made the composers work is what silenced it. It now CONSTRUCTS the empty case
(an unarmed composer, a metre the corpus has never seen, no composer at all)
rather than waiting for one to occur, with a companion test asserting real
composers still return exemplars so it cannot pass by breaking retrieval.

**`test_the_failure_names_the_piece_and_says_what_to_do` was blind to a whole
answer shape.** It escaped on `"error" not in result`, and `plan_readiness`
reports a missing piece differently:

```
compile_style   {"error": "No workspace for '<id>'", "hint": ...}      checked
plan_readiness  {"ready": false, "missing": ["no workspace for '<id>'"]}   SKIPPED
```

The tool is right; the test could only see one shape of being right. Widened to
ask what actually matters — does the reply NAME the piece, whatever key it uses
— and `plan_readiness` is now covered. The remaining `compile_style` case
escapes legitimately: the harness cannot build a valid ghost call for it.

**The pattern across Addenda 48-49:** every one of these tests passed for years
while checking nothing, and each went quiet for a different reason — a guard
that was never true, a corpus fix that removed the failing case, an escape
hatch that hid an unexpected shape. None of them would ever fail. A suite's
green is a statement about the tests that ran, not about the ones that ran
empty.


## Addendum 50 — a finding with no scale attached

Falsifying the analytical core against ground truth first, because a defect
there would invalidate everything downstream. Three clean negatives:

```
harmony_analysis.analyze_bar   11/11 textbook chords identified correctly
parse_roman / spell_roman      9,216 round-trips (2 modes x 12 tonics x 12 roots
                               x 9 qualities x every inversion), 0 failures
detect_parallel_perfects       7/7 planted-and-clean cases correct
```

The documented claim — "round-trip for all 12 degrees x 9 qualities x every
inversion" — holds exactly. All 11 counterpoint finding kinds fire on real
pieces, so none is dormant.

**The defect is in what the loudest finding MEANS.** `muddy_low_interval` —
two notes a 2nd-to-3rd apart below C3, the editor's "avoid thirds below C3" —
produces 392 findings across the workspace, all `info`, all bare counts.
Measured over each composer's own corpus:

```
liszt        0.0938 / bar          mozart      0.0077
beethoven    0.0233               haydn/bach   0.0007
chopin       0.0042               palestrina   0.0000   (60,677 bars, never once)
```

Two orders of magnitude between them, so the same number means opposite things.
Judged against the piece's own composer:

```
mozart-allegro-dm-20260603        0.333/bar =  43.3x Mozart's own practice
mozart-andante-fmaj-v2-20260826   0.171/bar =  22.2x
ocean-fantasy (beethoven+liszt)   0.354/bar =  14.2x
palestrina-motet-dorian           none                 correct — real Palestrina is 0.0000
```

The reviewer previously saw an undifferentiated count and could not tell 22x-Mozart
from 1x-Liszt. `self_evaluate.part_writing` now carries `per_bar`,
`composer_per_bar` and `times_own_practice`.

**A measurement I threw away.** My first attempt compared our rate to real
scores reconstructed by splitting notes at middle C — which put every low note
in the bass as a SINGLE note, so no low simultaneity could exist and real music
scored a meaningless 0. The fixture could not produce the condition being
measured. Redone against corpus bar records, which carry real chords.

### Two tests fixed, both testing by proxy

- `test_an_analyser_failure_never_breaks_the_report` asserted that
  `"except Exception"` appears **within 900 characters** of `"part_writing"` in
  the source. Adding a comment above the block broke it while the guard it
  checks was untouched. Now parses the AST and asserts the assignment sits
  inside a `try` with an `Exception` handler — falsified against an unguarded
  fixture to confirm it can fail.
- Bracketing the suite with file mtimes has been catching concurrent edits all
  session, but I was watching `scales.py` **only** — while editing
  `composition_brief.py` and others. Widened; the remaining intermittent
  failures this turn were a collection error and a `getsource` test, both
  transient and both gone on a clean run.

Final: **2173 passed**, lint clean.


## Addendum 51 — an integration check, and four investigations that found nothing

Fifty addenda of changes and no end-to-end run. Fresh piece, full pipeline:

```
init_workspace -> compile_style -> build_form_graph -> plan_readiness
              -> get_composition_brief (18,546 chars)
              -> commit_agent_phrase_direct_bars  ok=True, engraving present
              -> self_evaluate  ear / craft / realism / part_writing / voicing /
                                context_utilization / authoring / section_gate
```

Everything wired this session still reaches the report. The engraver runs on
commit, the section gate passes with advisories, and the brief builds.

**Four investigations, four negatives** — recorded because a negative that took
work is worth as much as a fix, and because three of the four were my own probes
being wrong:

1. **Source-inspecting tests.** 20 assert on source text vs 6 that parse it. Most
   string matches are sound: `"_engrave_phrase(" in src` fails loudly if the call
   is removed, which is the right direction. The genuinely fragile shape is
   POSITIONAL, and the three that use `.index` are ordering assertions on
   distinct strings — they raise `ValueError` if either vanishes. The +-900
   character window fixed in Addendum 50 was the only one of its kind.

2. **`craft_check` serialization.** Appeared to round-trip as a repr string.
   It does not — that was `json.dumps(..., default=str)` in my probe
   stringifying a dataclass. On disk it is a dict; after load it is a
   `PhraseCraftCheck`.

3. **`craft` missing from `self_evaluate`.** The key was absent on a fresh piece
   and present on an older one, which looked like the "correct analysis wired to
   nothing" pattern. It is correct behaviour: `if craft:` omits the key when
   there is nothing to report, and the phrase in question passed every check.
   Verified the two renderings agree — a commit reporting `harmony_is_voiced`
   and `has_breath_point` failed yields exactly those two lines to the critic.

4. **`musical_ear` missing.** The key is `ear`. My probe's name.

**Three of four negatives were probe errors.** That ratio has held for many
turns now and is the clearest signal available about where the remaining risk
sits: not in the code, but in how it gets measured.


## Addendum 52 — the target was stated; the gap was not

Checked the corpus feedback subsystem first — five modules CLAUDE.md documents
and nothing in this session had touched. `claim_matcher`, `overlay_builder` and
`conflict_resolver` are imported only by `scripts/ingest_with_feedback.py`,
which is correct: they are a batch pipeline behind one CLI. The output side is
wired too — `style_resolver` loads `context_overlays/<composer>/*.json` and
merges them into the pack. Its list-union `extend`s without deduping, which
would duplicate any entry an overlay repeats; measured across all 22 pack keys
for the one composer with overlays on disk, **zero duplicates**. Negative.

**The real finding was in what the brief withholds.** Its VOICING section has
always printed the composer's own thickness — "21% of right-hand attacks are
more than one note" for Chopin. That sentence has been in front of the composer
the whole time and has not moved the output:

```
chopin-nocturne-ebmaj-20260826
  self_evaluate: "the right hand is a bare single line in 93% of bars.
                  Real Mozart runs 50-89%, Chopin 5-63%"
  measured     : 1% of RH attacks are more than one note, against his 21%
```

`self_evaluate` measures the shortfall **after the fact** and tells the critic.
The composer — the one who could still act on it — was told only the target. A
target is a number to agree with; a gap is a number to act on, which is exactly
why MARKS SO FAR (Addendum 37) earns its place. The same treatment now:

```
chopin nocturne : SO FAR THIS PIECE: 1% of your right-hand attacks are more than
                  one note, against his 21% — about 19x thinner than his.
mozart andante  : SO FAR THIS PIECE: 25% ... against his 8% — already there.
```

Note the second line: the check has to be able to say "you are fine", or it is
just a complaint that fires on everyone. The two pieces genuinely differ and the
brief now says so.

A doubled unison does not count as thickness (Addendum 39's `[G5,G5]`), an empty
piece reports `None` rather than `0` — nothing committed is not a thin texture —
and at exactly zero there is no ratio to quote, so the wording carries it rather
than dividing by it.


## Addendum 53 — the rest rate, and a units trap inside the fix

Generalising Addendum 52. Which corpus targets does the brief state **without**
the piece's own position? Three, all in RHYTHMIC FINGERPRINT — including the one
the brief itself calls the clearest tell there is:

```
+ shows the piece's position : MARKS SO FAR, RANGE SO FAR, VOICING SO FAR
- states a target only       : "43% of these bars contain a REST. Music that never
                                stops sounding is the single clearest tell of a machine."
                               "34% of them carry a DOTTED rhythm."
```

Measured:

```
chopin nocturne   20% of bars rest   against his 43%
mozart andante    27%                against his 60%
palestrina motet  28%                against his 29%   already right
```

Palestrina is the line that matters: the check can say "you are fine", so it is
not a complaint that fires on everyone.

**The units trap.** The first version also compared DOTTED bars, and the nocturne
came back at **100%**. True, and meaningless: the piece is in **12/8**, where the
beat is itself a dotted quarter, while Chopin's corpus figure is drawn mostly
from 3/4 mazurkas. A structural property of the metre presented as a stylistic
achievement — worse than no number. Dotted is now compared only in simple metre,
and in compound metre the brief says why it is not.

### The same proxy tests broke again, and were rewritten

Adding a `graph` argument broke three tests that string-match the **exact call
text**:

```python
assert "render_rhythmic_fingerprint(brief.composer)" in src
assert src.index("render_corpus_scope(brief.composer)") < src.index(
    "render_rhythmic_fingerprint(brief.composer)")
```

Neither property changed — the brief still carries the fingerprint, and the scope
warning still precedes it. A test a new argument can falsify is testing the
spelling, not the wiring. Both now match the call name and scope the source to
`render_text` instead of the whole module. This is the third time this session a
proxy test has broken on a change it should not have noticed (Addendum 50's +-900
character window, and this pair), which is a stronger argument for structural
assertions than any of the individual fixes.


## Addendum 54 — two different measurements under one name

Swept the fragile-proxy class rather than waiting for a fourth instance. Only
one argument-pinning assertion remains and it is legitimate — `"isinstance(
composers, str)"` pins the parameter name because the parameter IS the property.
The three fixed in Addenda 50 and 53 were the population.

Then checked the brief I have been adding to. Four sections now tell the
composer where the piece stands, and bar counts agree across them (all 41), but
**two opened with the same words while measuring different quantities**:

```
SO FAR THIS PIECE (41 committed bars): 20% of your bars contain a rest ...
SO FAR THIS PIECE: 1% of your right-hand attacks are more than one note ...
```

That is the same-name-for-two-things trap — the one that once had
`direction_changes_per_bar` meaning both a per-bar count and a share of bars,
and got healthy melodic contour reported as a defect. Here it is smaller and in
the composer's own reading order, where two identically-labelled figures invite
reading the second as a restatement of the first. Renamed to **BREATHING SO FAR**
and **THICKNESS SO FAR**; MARKS SO FAR and RANGE SO FAR were already distinct.

A test now asserts every `... SO FAR` label in a real brief is unique, so a fifth
report cannot quietly collide with an existing one.

**Brief size, since I have added three sections to it:** 18,546 -> 21,452 chars
(~5,363 tokens), 16% for three concrete gaps the composer can act on while still
writing. Worth watching, not yet worth trimming.


## Addendum 55 — a motif with no name, stored anyway

Checked the motif system, since CLAUDE.md makes it the basis of memorability
("A piece is memorable because ONE idea keeps coming back changed") and the
realism report lists a memorable theme among the things it cannot see.

Across every piece in `workspace/`: **not one phrase slot carries a
`motif_transforms` entry**, including the five pieces with 3-6 motifs in the
bank. `resolve_motifs` already documents that failure and back-fills placements
to fix it, so the interesting question was whether the fix works.

Two checks before believing anything, both of which caught me:

- **A load-drop?** No. `motif_transforms` round-trips exactly, `MotifTransform`
  fields intact. My first probe "proved" content loss by feeding a dict with the
  wrong field names — the loader defaulting on invalid input is correct.
- **Is the mechanism inert?** No. With a well-formed motif it places the theme on
  **five sections** of a ternary form: `m1_a_p1, m1_b_p1, m1_retr_p1, m1_a2_p1,
  m1_coda_p1`. The election logic and the back-fill both work.

**The defect is what happens when the definition is malformed.** `resolve_motifs`
is documented "Validate and store motif definitions" and validated nothing:

```
resolve_motifs(pid, [{"id": "A", ...}])     # "id", not "motif_id"
  -> bank keys: ['', 'A']
  -> principal_theme_id: ''
  -> sections_given_a_theme_statement: 0     ...and no error, no hint, no reason
```

`mdef.get("motif_id", "")` stores a nameless motif under the empty string. An
empty id can never be elected (`elect_principal_theme` returns it,
`if not graph.principal_theme_id` rejects it) and no transform can refer to it.
If it is the only motif, the theme system goes quiet and the caller is told
nothing — which is precisely how I hit it, and I had the code in front of me.

Now refused, naming the index and the likely mistake (`"id"` instead of
`"motif_id"`), and refusing the whole batch rather than half-applying it.


## Addendum 56 — a narrative section that reaches no phrase

Swept the tool surface for the Addendum 55 pattern — functions taking dict
definitions with no error path. Five: `init_workspace`, `compile_style`,
`build_form_graph`, `save_narrative`, `save_reference_study`. Took the one whose
content matters most, since Addendum 45 established that `character` is the
single field the brief leans on.

**`save_narrative` was already right about the field I expected to be wrong.**
Passing `"text"` instead of `"character"` returns
`sections_missing_character: ["a"]` and a warning naming the consequence. My
first probe truncated the return at 44 characters and I read that as silence —
the fourth probe error of this kind, and the reason I now print whole responses.

**It was wrong about the span.** A section is matched to phrases by
`bar_start <= bar <= bar_end`, so:

```
{"id": "a", "character": "..."}                       -> stored as bars 1-8, a range nobody chose
{"id": "a", "bar_start": 9, "bar_end": 4, ...}        -> stored, matches NOTHING
```

Both come back `sections_stored: 1` with no warning. Missing keys fall through to
the dataclass defaults, which is how a section with no range at all becomes a
confident 1-8 covering the wrong music; an inverted range covers nothing and the
narrative is silently inert exactly where the planner thought it had written one.

Now reported as `sections_with_an_unusable_bar_range`, naming the section and
which of the two it is, alongside the existing character warning — and both can
appear together, because a section can be inert for two reasons at once. Still
stored rather than refused: the planner may be mid-edit, and this is a discipline
warning, not a gate.

Falsification first in the tests: a well-formed section produces no warning at
all. A check that fires on correct input is noise, and this file now has six
tests of which the first is that one.


## Addendum 57 — two parameters that did nothing, quietly

Continuing the sweep of dict-taking tools with no error path.
`build_form_graph(sections=...)` produced **byte-identical output** for a correct
spec, a misspelled one, an empty dict, and no argument at all:

```
no sections arg   -> 9 phrases: m1_a m1_a2 m1_b m1_coda m1_retr
wrong key names   -> 9 phrases: identical
empty dict        -> 9 phrases: identical
```

Parsing the function settles why. The local name `sections` has exactly two
uses — the `_as_list` normalisation on line 562 and nothing after it. Same for
`motif_ids`:

```
uses of `sections`  : line 562 store, line 562 read   -> NEVER READ after normalisation
uses of `motif_ids` : line 563 store, line 563 read   -> NEVER READ
```

**Two parameters on a public tool that are accepted, normalised, and discarded.**
This is the dead-code shape from `project_dead_modules_20260826` moved onto the
call surface, where it is worse: dead code does nothing and says nothing, but a
dead *parameter* invites a caller to supply something and then throws it away
looking like it worked.

Nothing in the repo passes either, and `/w-plan` documents the call without
them — so no agent is misled today. But the signature advertises them, and an
agent reading the tool surface (which is how these are meant to be discovered)
would have no way to find out. Supplying either now logs that it was ignored and
names what WAS used; the form is still built, because this is a warning and not
a refusal.

The last test in the file is the guard: it parses the function and fails if
either parameter gains real uses, so implementing one forces the warning to be
removed rather than leaving a lie in place. And the falsification test — the
documented call must stay silent — comes first, as it should.


## Addendum 58 — sweeping the whole tool surface for dead parameters

Addendum 57 found two by hand. The check is mechanical, so it should be
mechanical: for every public function in `scales.py`, does each parameter have a
`Load` that is not merely feeding its own `_as_list` normaliser?

One more:

```
init_work(description=)   loads=0
```

`WorkGraph` has no `description` field, so the argument was accepted and
dropped. The piece's description belongs on `init_workspace`, which puts it on
the contract — and `_creative_intent` reads it from exactly there when no
narrative prose was authored (Addendum 45). Supplying it to `init_work` looked
like setting the work's description and set nothing. Now says so, and points at
where it does belong.

After the fix the sweep is clean:

```
tool parameters still never read: none
```

**The sweep is now a test.** A parameter that is accepted and discarded invites a
caller to supply something and throws it away looking like it worked — dead code
moved onto the call surface, where it is worse than dead code. The guard's
failure message says what to do about a new one: log that it is ignored, as
these three now do, rather than leaving it silent.

That is three defects of one shape found in two turns by asking a question a
parser can answer. The hand-audit found `sections`; the parser found
`motif_ids` in the same function and `description` in a function I had not
looked at.


## Addendum 59 — a data model promising more than the code delivers

Took the dead-parameter question (Addenda 57-58) one layer down: which dataclass
fields are declared and never touched?

The first sweep said 128 fields, which was wrong — the regex counted `.field`
and `"field"` and missed keyword-argument use, so `finale_payoff` came back dead
while `init_work` demonstrably sets it. Corrected to the bare identifier: 81
fields, and more usefully **10 dataclasses whose name appears nowhere outside
`models.py`**.

The cluster that matters is `WorkGraph`'s cross-movement machinery:

```
WorkGraph.theme_families          0 writes anywhere outside models.py
WorkGraph.climax_reservations     0
WorkGraph.cross_movement_recalls  0
WorkGraph.orchestral_macro_arc    0
WorkGraph.cyclic_obligations      0
```

Five declared structures, 24 fields across five dataclasses, populated by
nothing. `init_work`'s docstring — *"This is WHERE Wolfgang decides the
symphony's dramatic destiny"* — sets `emotional_narrative` and `finale_payoff`
and nothing else. A piece planning a symphony with recurring material across
movements has none of it tracked, and the type system says otherwise.

**Not fixed, reported.** Implementing cross-movement recall is a feature, not a
repair, and building it blind at this point would be worse than naming the gap.
`init_work` now returns `declared_but_not_planned` and a note saying to carry
cyclic material in the movement narratives until these exist. Same principle as
the dead parameters: the defect is not that the feature is missing, it is that
nothing said so.

Four tests, including the one the report rests on — nothing writes these fields —
which fails the moment someone implements one, forcing the note to be corrected
rather than left standing as a lie.


## Addendum 60 — the phrase knew where it was going; nobody told the composer

Asked the complementary question to Addendum 59: which fields are WRITTEN and
never READ? The sweep is noisy (52 candidates, most false — the read-regex misses
f-strings and comparisons), so I verified one candidate properly instead of
trusting the list. It was the right one.

`PhraseSlot.forward_context`:

```
models.py            declares it
dramatic_plan.py     link_forward_context() WRITES it, for every phrase
tests                assert every phrase has one
composition_brief    ...nothing. Not one read, anywhere in the package.
```

`dramatic_plan.py` says in its own header that this field "existed on the model
and was never populated, so no phrase knew what it was leading into". The writer
was added. The reader never was. The content is not filler:

```
m1_a_p1     leads into m1_a_p2 (continuation, extend) in Eb major — carry the
            idea further than its first statement — spin it out, do not restate it
m1_coda_p1  final phrase — nothing follows; land it
```

The brief carried TRANSITION IN — where the phrase comes FROM — and nothing about
where it goes. A phrase-composer works in an isolated context and cannot see its
neighbours, so this is exactly the information that stops a phrase being a
well-formed dead end. Computed, tested, saved to disk, and dropped: the shape
recorded in `project_correct_analysis_wired_to_nothing`.

Now surfaced as `WHERE IT GOES NEXT`.

**And the fix collided with my own from Addendum 45.** That one returns early
when a phrase has no `dramatic_role`, to say "this phrase has no dramatic plan —
do not assume this is the climax". The early return also dropped the forward
line, which is *independent* of the arc: a slot can know what follows without
anyone having decided where the piece peaks. Caught by a test I wrote expecting
it to pass, which is the only reason I noticed. Decoupled, with a test pinning
that both appear together.


## Addendum 61 — verifying the noisy sweep, one candidate at a time

Addendum 60's written-but-never-read sweep produced 52 candidates and one real
defect. Rather than trust the rest, I checked the top four properly. Three were
false:

```
density_target   heavily used — surface_composer, context_router, style_resolver
hard_pass        read at models.py:1009 (`if not self.hard_pass`) — my sweep
                 excluded models.py from READS while counting its writes
approach_bars    set to None at both construction sites; a real oddity, but the
                 reader in realizer.py uses a LOCAL of the same name, not the field
```

One was real, and it is a vestige rather than a broken wire:

```
entry_signature   written by sketch_proposer + reducer, read by NOBODY
exit_signature    written by the same two, read by composition_brief
```

Measured across `workspace/`: **426 phrases, ten with a sketch at all, and zero
carrying either signature.** So the brief's `exit_signature` block is unreachable
in practice, and `entry_signature` has neither a reader nor a writer that runs on
the agent path.

Not wired, because wiring it would produce nothing. Phrase-to-phrase continuity
is already carried by `_derive_continuation`, off the previous phrase's REALIZED
notes rather than its plan — the same replacement that retired
`ContinuationContext`, and the better mechanism: it describes what was actually
written instead of what was intended.

Marked as superseded on the model with the measurement in the comment, plus a
test that fails if anyone gives `entry_signature` a reader. Two dead modules were
once this repo's costliest defect; a field that looks live is the same trap one
size down.

**And the test's first version reported a docstring as a reader.** It grepped for
the identifier and matched a line of PROSE in `piece_graph.py` describing the bug
this field once had. Rewritten to parse for `ast.Attribute` in `Load` context —
the same lesson as Addenda 50 and 53, arriving for the third time in my own work
rather than in the code's.


## Addendum 62 — the composer got the technique and not the goal

Redid Addendum 60's sweep with the AST instead of regex — `Attribute` nodes by
`Load`/`Store` context, plus keyword arguments as writes and string constants as
reads. 52 noisy candidates became 26 real ones, and the interesting cluster was
`SectionContract`.

`dramatic_plan.section_rhetoric()` returns **(goals, techniques)**. The planner
copies one of them:

```python
_sl.section_techniques = list(_techs)      # and nothing for _goals
```

So the brief tells the composer HOW and never WHAT FOR:

```
given    TECHNIQUE to reach for here: clear periodic phrasing / diatonic harmony
withheld GOALS: make the idea memorable on first hearing; establish the key beyond doubt

given    TECHNIQUE: thinning to a single line / codetta repetition
withheld GOALS: take leave of the material; stop persuading

given    TECHNIQUE: reharmonisation / registral displacement
withheld GOALS: bring the idea back CHANGED; make the return feel earned
```

A technique with no goal is a recipe, and the recipe is what was being handed
over. The goals went to `SectionContract.rhetorical_goals` — which
`dramatic_plan.py` notes in its own header "had no reader anywhere in the
codebase". A writer was added for that field; the reader never was, and the copy
that DOES reach the brief carries half the pair.

Now `WHAT THIS SECTION IS FOR`, printed before the techniques, because why
before how.

### The same early return bit for the second time

Addendum 45's "this phrase has no dramatic plan" branch `return`s immediately.
Addendum 60 found it had swallowed the forward-context line and decoupled that
one. It then swallowed the section goals too — caught only because a test I
expected to pass did not.

Patching a third exception would have been the wrong move. Restructured: the
branch now APPENDS its notice and falls through, so everything not dependent on
the arc survives, and only the genuinely arc-dependent lines (climax position,
distance) stay behind `if planned`. Two tests pin both halves — an unplanned
phrase gets its goals and its forward context, and still gets no climax claim.


## Addendum 63 — a phrase in the slow movement did not know it was in the slow movement

Working through the AST sweep's remaining candidates.

**`PhraseContext`'s four doctrine fields** (`active_melody_priors`,
`active_modulation_scripts`, `active_counterpoint_rules`,
`active_harmonic_temperatures`) are written by `context_router` and never read —
but all four kinds of doctrine DO reach the brief by its own path (`Melody:`,
`Tonal motion:`, `Counterpoint:`, `Color:`). Redundant copies, dead but harmless.
No change.

**`MovementContract.role_in_work` was the real one.** `plan_movement` stores
`role_in_work`, `character` and `tempo_marking`, and `composition_brief` contains
no reference to `work_graph` or `MovementContract` anywhere:

```
m1 (opening allegro)   mentions its role: False | its character: False
m2 (slow movement)     mentions its role: False | its character: False
```

A phrase in the second movement of a symphony received a brief indistinguishable
in kind from one in the opening allegro. For a multi-movement work that is the
largest single piece of context there is, and `plan_movement` — a documented
planning step — was writing it to a field nothing read. Now:

```
MOVEMENT 2 of 2 — its role in the work: slow movement — character: a songful
lament — marking: Adagio
```

Two falsification tests matter as much as the two positive ones: a
single-movement piece gets no line at all ("MOVEMENT 1 of 1" is noise), and a
movement planned with an id but no role, character or marking also gets nothing —
an id alone is not context.

**Two transients, correctly identified this time.** A crash reproducing the
two-movement sequence did not reproduce on a clean run, and a `test_lock_contract`
failure came with `composition_brief.py`'s mtime moving 02:03:22 -> 02:06:49
*during* the run, in a window where I made no edit. Re-run with the file stable:
**2272 passed**. Bracketing every file I touch, rather than just `scales.py`
(Addendum 50), is what makes that a one-step diagnosis instead of an
investigation.


## Addendum 64 — the work's plan reached no movement of it

Finishing the multi-movement thread. `init_work` stores three things and
**nothing read any of them**:

```
WorkGraph.emotional_narrative   written by init_work, read by nobody
WorkGraph.finale_payoff         written by init_work, read by nobody
TonalItinerary.home_key         written by init_work AND plan_movement, read by nobody
```

The home key is the sharpest: it carries a comment describing the bug where a
three-movement sonatina in G major recorded a home key of "C" — *"and every later
question about where the work lives got the wrong answer"*. There is no later
question. The fix was real and its only consumer never existed.

So a movement was composed knowing nothing about the work it belongs to. Now:

```
MOVEMENT 2 of 2 — its role in the work: slow finale
  THE WHOLE WORK: brightness giving way to song, then earned repose
    (the work's home key is G major; this movement is in C major — the distance is part of the plan)
  THIS MOVEMENT MUST PAY OFF: the opening idea returns transformed and finally at rest
```

Three placement decisions, each with a falsification test:

- the narrative goes to **every** movement — it is the shared arc
- the payoff goes **only to the last** — handing it to the opening allegro is an
  instruction to spend the ending early
- the home-key distance appears **only when there is one** — the first movement
  IS the home key, and reporting a distance of zero is noise

**A probe error worth naming, because it nearly cost a real fix.** The home-key
line appeared to be missing; I was about to debug the condition. It was my print
filter: I stripped each line and then matched a prefix that began with two
spaces. The code had been right the whole time. That is the same shape as the
truncated `save_narrative` return in Addendum 56 — the output was fine and the
instrument was not.


## Addendum 65 — three climaxes of the whole piece

Addendum 64's output contained a line I nearly read past: movement 2 of a
two-movement work was told it was *"4 phrase(s) before the piece's climax"*. The
dramatic plan runs **per movement**, so:

```
phrases marked as THE climax across a 3-movement work: 3
   m1_dev_p3   in m1_dev
   m2_b_p2     in m2_b
   m3_b_p2     in m3_b
```

Each was told: *"this is the CLIMAX of the whole piece. Everything before has
been building to it and everything after subsides from it."* For the first two
that is false with two whole movements still to come, and it instructs the
composer to spend the work's peak in its opening movement.

This is Addendum 36 one scale up. There the defect was a DEFAULT reading as a
decision (`climax_distance=0` meaning both "unset" and "I am the peak"); here it
is a correct per-movement decision described in whole-work language.

Scoped to what is actually true:

```
single movement : "the CLIMAX of the whole piece"          unchanged
multi-movement  : "the CLIMAX of the MOVEMENT ... (Each movement has its own
                   peak; which of them is the WORK's apex is not recorded
                   anywhere, so judge it from the work's arc above.)"
```

That parenthesis is not hedging — `WorkGraph.climax_reservations` exists and
nothing fills it (Addendum 59), so the work's apex genuinely is undecided. Saying
"the movement's peak" while implying the work's has been settled elsewhere would
trade one false claim for another.

**And I churned wording I should not have.** The approach line became "before
THIS piece's climax" for single-movement pieces, breaking a test that had every
right to pass. Reverted to the original phrasing for that case: a fix that
changes text it did not need to change is a fix with an unnecessary blast radius.


## Addendum 66 — "so far" meant this folder, not this movement

Turned Addendum 65's lens on my own work. Four sections of the brief report what
the composer has written up to now — MARKS SO FAR (Addendum 37), RANGE SO FAR,
BREATHING SO FAR and THICKNESS SO FAR (Addenda 52-53) — and every one of them
iterated **all phrases in the graph**:

```python
for state in (getattr(graph, "phrases", {}) or {}).values():
```

So in a multi-movement work the slow movement was shown the opening allegro's
articulation counts, rest rate and texture thickness as its own position. Two
movements have genuinely different habits — a fast movement rests less and
articulates more — and averaging them describes neither.

This is exactly Addendum 65 one layer down: a per-movement quantity presented as
a whole-work one. Three of the four sections were added earlier in this same
session, by me, in the very turns that were fixing the same class of mistake
elsewhere.

Scoped via `_phrases_in_scope`:

```
m1 (has the marks)       MARKS SO FAR (4 committed bars): articulation 16, tie 0, slur 2 ...
m2 (nothing committed)   MARKS SO FAR: nothing committed yet — this is the first phrase ...
```

Three falsification tests, because the scoping must not narrow anything it
should not: a single-movement piece still counts every phrase, an absent
movement id counts everything, and a phrase id matching **no** movement falls
back to the full set rather than reporting an empty "so far" — which would read
as "you have written nothing" and is the worse failure of the two.

The threading is by movement id derived from the phrase id rather than by
passing the slot, because `CompositionBrief` carries `phrase_id` and not a slot —
found by writing the wrong version first and having ruff reject `slot` as
undefined in `render_marks_so_far`, where `slot` was a loop variable.


## Addendum 67 — the fourth of four

Addendum 66 named four "so far" sections and scoped three. `_register_target`
— RANGE SO FAR — still read every phrase in the graph:

```python
for ps in (getattr(graph, "phrases", None) or {}).values():
```

So a slow movement was handed the allegro's register span as its own starting
point, which gives it both the wrong ceiling and the wrong floor. The section
exists precisely to set a reachable ceiling ("the last generated andante kept its
melody inside 19 semitones ... narrower than any real movement measured"), and
inheriting a three-octave span from a different movement defeats that.

```
m1 (wide register)   RANGE SO FAR: the melody has used G3-G6 (36 semitones) ...
m2 (nothing yet)     no line — correct, it has written nothing
```

Worth stating plainly: I wrote the sentence naming four sections and fixed three
in the same breath. The check that caught it was re-reading my own claim against
the code rather than against my memory of having done it — which is the same
discipline as `feedback_verify_the_fix_not_the_shape`, applied to a claim instead
of a fix.


## Addendum 68 — "earlier" is (movement, bar), not bar

Made the multi-movement check mechanical instead of finding instances by hand:
which functions in `composition_brief` walk `graph.phrases` without going
through `_phrases_in_scope`? Three, and the underlying fact is worse than the
scoping:

```
m1: bar_start range 1..38
m2: bar_start range 1..38     <- bar numbers RESTART per movement
```

So `other.bar_start < slot.bar_start` is not "earlier". For a phrase at bar 20 of
movement two it admits movement one's bars 1-19 and **rejects its bars 20-38** —
an arbitrary slice of a different movement, silently, in both consumers.

The two consumers want opposite scopes, which is why one fix does not serve both:

- **`_cadences_already_used`** drives "you have closed three phrases the same
  way". A cadence recurring in a LATER movement is not the repetition that
  warning is about, so it is now movement-scoped. Pooling movements
  over-reported reuse and would have pushed a composer to avoid a perfectly
  normal cadence.
- **`_derive_continuation`'s motif history** is deliberately WORK-wide: a theme
  stated in movement one and taken up in movement three is cyclic form, and the
  composer of movement three needs to know. That one needed real performance
  order — `_phrases_before` compares `(movement index, bar)`.

Five tests, including the two that pin the difference: everything in an earlier
movement precedes this phrase however high its bar number, and cadence history
never leaves the movement.

`_source_phrase_for` is left alone: it resolves a phrase of the SOURCE piece for
variation and style-transfer contracts, where crossing movements is the point.


## Addendum 69 — the wrong movement's intent

Swept the whole package for cross-phrase bar comparisons, since Addendum 68
established that bar numbers restart per movement. Fifteen candidates, thirteen
harmless: `surface_composer`'s are a cursor against its own slot, and
`assembler.py:1005` groups **by section** before comparing, so its comparison
never crosses a movement.

The two that mattered both resolve a NARRATIVE SECTION by bar range alone:

```
m2 phrase m2_a_p1 (bar 1)
inherits movement 1's narrative: True
```

`NarrativeSection` carried `bar_start`/`bar_end` and no movement, so a phrase at
bar 1 of the second movement matched a section covering bars 1-8 of the first —
and CREATIVE INTENT is the one line the phrase-composer is told to start from
("the feeling that should choose the notes"). A two-movement work had its slow
movement composed to the allegro's brief.

`movement_id` added, defaulting to empty, which is what every single-movement
piece wants and what every graph already on disk holds — so matching is
unchanged for them. `_narrative_section_for` also honours a movement named in
the section's `id` or `label` (`"m2_open"`), because narratives written before
the field existed usually said so there.

`save_narrative` now reports sections that name no movement **in a
multi-movement work only** — and falsifying that is one of the six tests: a
correctly attributed narrative produces no warning at all.

```
attributed    warning: none
unattributed  1 section(s) name no movement_id in a 2-movement work — bar
              numbers restart per movement, so these may attach to the wrong one
```


## Addendum 70 — the same lookup, the third consumer

`_apply_narrative_curves` resolves a narrative section the same way the brief
did — bar range, no movement:

```python
sec = next((s for s in sections if s.bar_start <= gbar <= s.bar_end), None)
```

It maps that section's energy, tension, density and brightness onto the slot,
and those curves drive dynamics, density targets and the tempo arc. So a
movement-two slot could be shaped by movement one's emotional arc, silently.

Fixed — but the interesting part is HOW. Addendum 69 put the movement test
inside `composition_brief._narrative_section_for` as a local closure. Copying
that closure here would have made two copies of one rule, which
`project_one_parser_one_loader` records as this repo's most expensive defect
class ("duplicated parsers and hand-enumerated loaders are this repo's #1 bug
source: 4 key parsers, 3 broken on the planner's own spelling"). So the
predicate moved to `models.py` beside the field it interprets, and both
consumers import it:

```
narrative_section_is_in_movement()   models.py — the one definition
  used by composition_brief._narrative_section_for
  used by scales._apply_narrative_curves
```

Verified: a two-movement narrative where movement one's energy is 1.0 and
movement two's is 0.1 now gives each slot its own.

A test asserts there is **exactly one** definition of the predicate anywhere in
the package — so the next consumer imports it rather than reimplementing it,
which is the only way this class of defect actually gets closed.

**Transient, identified in one step:** a `test_rhythmic_fingerprint` failure
arrived with `composition_brief.py`'s mtime moving 02:34:49 -> 02:35:55 mid-run,
in a window where I made no edit. Clean re-run: **2309 passed**.


## Addendum 71 — three implementations of one loader

Generalised Addendum 70's "exactly one definition" guard: hashed every function
body in the package (docstrings stripped, structure only) and looked for
collisions. Across ~200 modules, **one**:

```
claim_registry.py:from_dict  ==  evidence_extractor.py:from_dict
```

Byte-identical:

```python
known = {f.name for f in cls.__dataclass_fields__.values()}
filtered = {k: v for k, v in data.items() if k in known}
return cls(**filtered)
```

And a third implementation of the same idea already owned the job:
`piece_graph._dataclass_from_dict`, which exists because "hand-enumerated
loaders are how this project keeps losing state" — the PhraseSlot loader listed
ten fields and silently dropped `curves`, `motif_transforms`, `harmony_detail`,
`pickup_beats`, `continuation` and `notes` on the first round-trip.

Both now delegate. This is not only tidying: the copies filtered flat keys and
**did not recurse into nested dataclasses**, which the canonical one does — so
an `EvidenceBundle` or `MeasurableClaim` holding a nested structure would have
come back as raw dicts. A test pins that difference rather than asserting the
delegation alone.

Two guards, because the point is the class and not the instance: no module may
re-implement the field filter (`__dataclass_fields__` + `k in known` anywhere
outside `piece_graph`), and both call sites must contain `_dataclass_from_dict`
and must NOT contain `__dataclass_fields__`.

Notable that the sweep found only one collision. The codebase is not riddled with
copy-paste — but the one it had was of the exact function whose duplication is
recorded as this project's most expensive defect.


## Addendum 72 — the last hand-rolled pitch parser

Addendum 71's hash-based sweep only catches byte-identical bodies. The recorded
worst case — "4 key parsers, 3 broken on the planner's own spelling → every
chord frame in C major" — was four *drifted* copies, which hash differently. So
I swept by CONCEPT instead: functions whose names claim to parse a key, a pitch,
or a mode.

```
parse_key   3   assembler._parse_key, pitch.parse_key, scales._parse_key_str
to_midi     2   pitch.pitch_to_midi, style_dimensions._note_to_midi
```

**The key parsers are fine.** Both non-canonical ones are one-line delegates to
`pitch.parse_key`, and all three agree on all 14 spellings the project uses
(`"a minor"`, `"Gm"`, `"Eb major"`, bare `"c"`). An alias is not a duplicate,
and the recorded fix held.

**`_note_to_midi` was real** — a second implementation walking accidentals by
hand. It agreed with `pitch_to_midi` on every spelling tested, including
music21's `E-4` flat convention and double accidentals like `B--4`. Two copies
agreeing today is precisely how the four key parsers started.

Speed was the one plausible defence, and it does not survive measurement:

```
pitch.pitch_to_midi   0.57 µs/call
_note_to_midi         0.18 µs/call      3.1x — but ~0.2s across half a million notes
```

Consolidated, with the measurement written into the docstring so the next reader
does not re-derive it and reach the opposite conclusion. Delegation preserves the
two behaviours its callers depend on: music21 spellings resolve, and junk returns
`None` rather than raising — a corpus pass must not die on a bad name.


## Addendum 73 — six dominants classified as tonic

Extending the concept sweep to the other domain primitives (duration, metre,
texture, cadence, transposition) found three pairs. Two were already correct:
the `_beats_to_dur_str` copies both delegate to the one duration table, and
`performance_renderer.is_strong_beat` derives from `metric_weight` by a
different route and agrees with `duration.is_strong_beat` on all 48
metre/beat combinations tested.

The third was real. `sketch_proposer._classify_harmonic_function` matched eleven
literal spellings and ended:

```python
    return HarmonicFunction.TONIC.value      # everything else
```

What it did not list is the inversions and sevenths that make up most of real
music:

```
misclassified: 9/22 common numerals, ALL as tonic
   ii65 IV6 iv6        should be predominant
   V65 V43 V42         should be DOMINANT
   viio6 viio7 vii07   should be DOMINANT
```

Six dominants read as tonic. `V65` is the commonest dominant inversion in tonal
music, and calling it tonic inverts the tension of every cadence built on it.
The default made the wrong answer the *stable* one, which is the most damaging
direction available.

Now delegates to `harmony_analysis.parse_roman` + `classify_function` — the pair
that already round-trips 9,216 combinations of degree, quality and inversion
(Addendum 50). **1/22** on the synthetic list, and checked against real data:

```
24,456 corpus bars: 1.1% classify as chromatic
  and they genuinely are — viio7/V (98), #ivo (42), #IV (29), bIII (25)
```

**My own musical expectation was wrong once.** I asserted `bVI` should be
chromatic; it comes back "predominant", which is the better answer — the flat
submediant is a borrowed chord that behaves as a predominant, characteristically
moving to V. "Chromatic" only says "not diatonic"; the degree-and-quality reading
says something a composer can use. The test now records that, because the next
person to read it will have the same first instinct I did.


## Addendum 74 — a rising melody labelled "winding down"

Addendum 73's defect had a shape worth searching for: a chain of exact matches
ending in a fallback that is a real, consequential value rather than "unknown".
Swept for it — classifier-shaped functions whose final `return` is a meaningful
constant. Twenty-six candidates, most of them accumulator returns (`out`,
`result`, `pairs`) and proper threshold ladders (`_energy_to_dynamic`'s
`return "ff"` is the top rung, not a fallback).

One was real. `_infer_slot_function` decides a gesture slot's rhetorical role,
and its contour test calls `pitch_to_midi` on the anchors — which returns None
for an anchor written as a SCALE DEGREE (`^5`). So the test was skipped and the
slot fell through to `return "winding_down"`:

```
pitches  C4 -> G4  ->  rising_continuation
degrees  ^1 -> ^5  ->  winding_down        the same melody
pitches  G4 -> C4  ->  falling_continuation
degrees  ^5 -> ^1  ->  winding_down        also the same label
```

A rising slot and a falling slot got the identical answer, and "winding down" is
the one that tells the composer to release rather than build.

Degrees are now compared as scale steps. Coarser than semitones, but the right
sign, and `^3 -> ^3` still reads as no motion — the falsification test, because
a fix that turns every degree pair into motion would be worse than the bug.

**Honest limit on this one.** `Anchor.pitch_or_degree` supports both forms and I
could not measure which the engine actually emits: only 10 of 426 phrases in
`workspace/` carry a sketch at all (Addendum 61), so there is no stored data to
count. The defect is demonstrable in the code path and fixed there; its
real-world frequency is unknown, and this is the engine fallback rather than the
default agent path.

Also pinned: `_degree_number` must return None for a pitch name, or `C4` would
read as degree 4 — the octave digit mistaken for a scale degree, which would be a
worse bug than the one being fixed.


## Addendum 75 — a chromatic chord over a tonic bass

Following the anchor-notation thread from Addendum 74: `sketch_proposer` WRITES
its anchors as scale degrees, so that fix was on the production path rather than
a hypothetical. Checking every consumer of `pitch_or_degree` then found the
generator side.

`_roman_to_bass_degree` was a hand-written dict of about twenty spellings ending
in `return "^1"`:

```
bVI -> ^1     V/V -> ^1     viio7 -> ^1     #ivo -> ^1
```

Every chromatic chord got the TONIC in its bass. A bVI over ^1 is not a bVI. This
is the third instance of one shape in three addenda — an exact-match table whose
fallback is the most stable value available, which is the most damaging answer to
be wrong with. Now derived from `harmony_analysis`: parse the numeral, take the
chord template, pick the member the inversion puts in the bass. All fourteen
tested numerals correct, including `V65 -> ^7`, `V43 -> ^2`, `bVI -> ^#5`.

**And the fix would have introduced a regression if I had stopped there.** The
new derivation emits ALTERED degrees, and both anchor resolvers did
`int(p[1:])`:

```
realizer._resolve_anchor_pitch("^b6")  ->  None
realizer._resolve_anchor_pitch("^#4")  ->  None
```

They returned no pitch at all for exactly the expressive degrees — the borrowed
flat sixth, the raised fourth — so a chromatic bass anchor would have vanished
silently rather than sounding wrong. Caught by asking what happens to the OUTPUT
of the fix, not just whether the fix is right.

One `pitch.parse_scale_degree` now serves both resolvers, rather than a third and
fourth copy of degree parsing (`project_one_parser_one_loader`). `^b6` -> 68,
`^#4` -> 66, plain degrees and pitch names unchanged.


## Addendum 76 — two tables for one fact, both wrong the same way

Swept for hand-written Roman-numeral dicts, since three addenda in a row had
found one. Four exist; three are complete for their purpose (7-degree maps in
`context_compiler` and `harmony_analysis`). The fourth was
`realizer._roman_to_bass_offset` — 24 entries ending in:

```python
return mapping.get(roman.strip(), 0)      # 0 = the tonic
```

```
misclassified bass offsets: 7/18
   V65 -> 0 (want 11)   V43 -> 0 (want 2)   ii65 -> 0 (want 5)
   IV6 -> 0 (want 9)    viio6 -> 0 (want 2) I6 -> 0 (want 4)   V/V -> 0 (want 2)
```

Someone had hand-added `ii6` and `I64` and stopped, so two inversions worked and
the rest were silently tonic.

**The point is that this is the SAME FACT as Addendum 75's
`_roman_to_bass_degree`** — one wants semitones, the other a scale degree — and
they were two independently hand-written tables, each with a tonic fallback,
each missing a different subset of inversions. Two tables that must agree,
disagreeing with each other and with the music.

One derivation now lives in `harmony_analysis.roman_bass_offset`, and both
callers delegate:

```
bass offsets wrong: 7/18 -> 0/18
degree and semitone views agree on all 18
```

Three guards: every offset correct, the two views must produce the same answer
for every numeral, and neither caller may contain a table again (no
`mapping = {`, no `CHORD_TEMPLATES`).

That is four fixes of one shape in four addenda — a lookup table whose fallback
is "tonic". Worth naming as a class: in this codebase the benign-looking default
is nearly always the harmful one, because tonic/stable/consonant is exactly what
makes a wrong answer invisible.


## Addendum 77 — "no cadence here" became a perfect authentic cadence

Swept the pattern named at the end of Addendum 76 — a musical lookup with a
benign default — across every `dict.get(x, <non-empty>)` in the package. 25
candidates, most of them sound (`SCALE_INTERVALS` defaulting to major,
`CHORD_TEMPLATES` to a major triad). Three were the same defect again, in
`sketch_proposer`'s cadence tables.

`CadenceTarget` has eight members. The tables covered five:

```
cadence    soprano  int  bass        (before)
  PAC        ^1      1    V-I
  IAC        ^3      3    V-I
  HC         ^2      2    ?-V
  DC         ^1      1    V-vi
  plagal     ^1      1    IV-I
  evaded     ^1      1    V-I     <- the resolution NOT arriving is the gesture
  elided     ^1      1    V-I
  none       ^1      1    V-I     <- "do not cadence here"
```

An **evaded** cadence is defined by the dominant failing to resolve; it was
handed the tonic over V-I, the exact opposite. And a slot planned with **no**
cadence was given the strongest close available — `_cadence_soprano_degree`'s
caller guards `none`, but `_build_cadence` did not, so the guard existed in one
of the two places it was needed.

Now `evaded -> ^2 over V-?`, and `none` yields `soprano_arrival_degree=0,
bass_motion=""`. `elided` keeps V-I on ^1 deliberately: elision is about timing —
the arrival IS the next phrase's start — not about avoiding the tonic.

The last test is the one that matters: it fails if ANY cadence type still falls
through to the PAC's answers, so a ninth member added later cannot be silently
absorbed.

**Fifth instance of one shape in five addenda.** The class, stated plainly: in
this codebase a lookup's fallback is almost always tonic, consonant, or closed —
and that is precisely what makes a wrong answer inaudible as wrongness. A
dominant misread as a tonic still sounds like music; it just sounds like
different music than was planned.

(Lint reports an unused import in `test_melody_uses_register.py`, created at
03:07 by another session. Left alone.)


## Addendum 78 — 39% of phrases chose ornaments from energy alone

Generalised the five-addendum pattern mechanically: for every Enum in `models`,
does each lookup keyed on it cover all its members? Seven tables came back short.
Four were the cadence tables just fixed; the largest was
`context_router._resolve_ornaments`, which maps a phrase's function to an
ornament context and covered **seven of thirteen** members.

The measurement was worse than the enum suggested, because the planner writes a
vocabulary far wider than the enum:

```
426 slots in workspace/  ->  39% had NO function-based ornament context

unmapped and not enum members at all:
   development transition climactic sequence standing_on_dominant
   resolution extension recapitulation retransition codetta liquidation
```

**Two of the misses were near misses on the enum's own spellings.** The data
says `contrasting` and `varied_return`; the enum says `contrasting_theme` and
`return_varied`. Functions that were *meant* to be handled fell through on a
naming difference — `project_dead_label_vocabulary` exactly ("readers were fixed,
the generator was not, so every lookup missed silently").

Mapped against the vocabulary actually in use: **39% -> 0%**.

Note the sub-class. Addenda 73-77 were all a fallback returning a plausible
WRONG value; this one returns nothing, so the phrase quietly chose its ornaments
from energy alone. Both are invisible, but for opposite reasons — one is
inaudible because it sounds like music, the other because nothing happens at all.

The test measures coverage against the graphs on disk rather than against the
enum, so a fourteenth function the planner starts writing tomorrow fails the test
rather than silently getting no context. It also has a vacuity guard: an empty
workspace would make the assertion pass while checking nothing.


## Addendum 79 — the recapitulation asked for a pickup

Following the enum-vs-reality sweep to its second consumer.
`sketch_proposer._FUNCTION_TO_GESTURES` maps a phrase's function to the gesture
shapes it asks the bank for. It listed eleven members and fell back to
`["pickup", "answer"]` — the PRESENTATION gestures.

```
426 slots  ->  31% took the fallback
   contrasting_theme  56     <- an enum member, simply absent from the map
   return             49     <- an enum member, simply absent from the map
   development        10, climactic 5, standing_on_dominant 2, resolution 2 ...
```

So the phrase that RETURNS the theme — the recapitulation, the moment a piece
pays off — asked the gesture bank for a pickup and an answer, the shapes a
phrase uses to START. **31% -> 0%.**

**Two things I checked before changing anything, one of which stopped a false
finding.** The map names `sequence_step`, `arrival`, `lean_in` and `sustain`,
and the corpus gesture banks contain only six labels — `answer`,
`cadential_push`, `insist`, `pickup`, `answer_with_space`, `cadential_release`.
That looked exactly like `project_dead_label_vocabulary`: four names the data
never produced. It is not. `gesture_bank._same_gesture_family` defines four
families (initiate / drive / resolve / answer) and those names resolve
deliberately through it — querying each returns eight results in four distinct
groups. The aliasing is by design and predates this change, so the new entries
use only names inside those families rather than inventing more.

The coverage test measures against the graphs on disk rather than the enum, for
the same reason as Addendum 78: the planner writes nine function names the enum
does not contain, so testing the enum would pass while the real vocabulary
missed.

**Transient, bracketed:** two failures with `assembler.py` (03:16:20) and
`scales.py` (03:19:30) both edited by another session mid-run — and the failing
test was mine, which inspects exactly those two files. Clean re-run: **2424
passed**.


## Addendum 80 — correcting Addenda 78 and 79

Both said the planner writes a vocabulary wider than `PhraseFunction`. Checked
across all five forms:

```
functions the CURRENT planner emits: continuation, presentation, return_varied,
retransition, contrasting_theme, return, coda, transition, closing,
fragmentation, sequence, liquidation   — all twelve are enum members
```

The nine non-enum values (`development`, `climactic`, `standing_on_dominant`, …)
occur in **three pieces from April** and nowhere else — agent-authored plans, not
planner output. My framing was wrong.

The impact figures survive, and I measured rather than assumed:

```
gesture-map fallback, ALL pieces                     136/432 = 31%
gesture-map fallback, current pipeline only (08-26)   80/266 = 30%
```

So the defect is current and the fix stands — but the cause is duller and worse
than the one I gave. Not vocabulary drift: the map covered **eleven of sixteen
enum members** and omitted two of the most common ones the planner emits every
run, `contrasting_theme` (56 slots) and `return` (49). The map was incomplete
against the enum sitting beside it, and had been for as long as both existed.

The legacy entries stay — an agent-authored plan may use them — but they are
defensive, not the fix.

---

## Addendum 81 — the realism audit was calibrated on a piano and judged a choir

Ran every `score_realism` detector over all 47 delivered pieces, split by whether
the piece predates the engraver fix. `tie_absent` (12/47) and
`articulation_absent` (9/47) are the two commonest findings in the whole corpus
of output — and **every one of them is in a pre-fix piece**; all nine pieces
built since are clean on both. Confirming measurement, no new defect.

What it did surface: two detectors firing on a **Palestrina motet**. Renaissance
polyphony has a deliberately narrow rhythmic vocabulary and puts nearly every
attack on a beat, so that is exactly the "would this reject real music?" question
[[feedback_rules_must_permit_real_scores]] exists to ask. It does. Measured
against real scores from music21's corpus — quartets, madrigals and motets, where
`reference_scores/` holds only piano:

| detector | mozart | haydn | bach | palestrina | monteverdi |
|---|---|---|---|---|---|
| `syncopation_absent` | 0% | 0% | 0% | **100%** | 57% |
| `voicing_poverty` | **50%** | **78%** | 0% | 76% | 40% |
| `register_stasis` | 7% | 11% | 0% | **100%** | 68% |
| `rhythm_vocabulary_poverty` | 8% | 22% | 15% | 29% | 36% |
| `melody_vocabulary_poverty` | 29% | 11% | 0% | 24% | 24% |
| `scalar_overuse` | 0% | 22% | 0% | 16% | 4% |

Half of real Mozart told that no moment sounds fuller than any other; all of real
Palestrina told it had been generated rather than felt.

**Four distinct causes, all one shape — the yardstick was the grand staff.**

1. *A bound that is the instrument, not a defect.* `voicing_poverty` fires when
   the melody staff never plays a chord; a violin and a soprano never can.
   `register_stasis` wants two octaves from a line, which is more than a singer
   HAS — a Palestrina cantus lives inside a ninth. Both now gated to the 2-staff
   grand staff they were measured on. Staff count separates the cases exactly:
   the piano corpus is 2 throughout, quartets 4, motets 4-8.

2. *A premise true only after 1600.* `syncopation_absent` reads metrical flatness
   as a generation artifact. Renaissance syncopation is the suspension, a whole
   beat long, so it lands ON a beat: real median off-beat share is **0.4%** for
   Palestrina against 47% for Mozart. A composer-derived floor does not rescue
   it — the corpus records fold several voices into two hands, manufacturing
   off-beats the score does not have (Mozart reads 63% there against 47% in the
   score), so the floor rises above real Mozart and starts rejecting him instead.
   Withheld for `renaissance` via `style_registry`, untouched everywhere it was
   validated.

3. *A percentile bound decided by whichever one staff tripped it.*
   `rhythm_vocabulary_poverty` used the composer's own 95th/5th percentile — so
   ~one real staff in ten trips it by construction — and then fired the whole
   piece if ANY staff did. The piece-level false-positive rate therefore
   compounded with staff count: 8% on two-staff Mozart, 26% on a five-voice
   motet. The polyphony most likely to be judged was the least able to survive
   the judgement. "The rhythm has one gear" is a claim about the piece, so it now
   needs a majority of staves.

4. *Percentile is not the bound* ([[feedback_percentile_is_not_the_bound]],
   again). Monteverdi's corpus floor of 5 distinct note values sits ABOVE his
   real madrigal parts' 4; the shape floor reads 13-20 where real single staves
   reach 5-12. Both because folding voices can only ADD vocabulary. Fixed with
   one value of slack on the rhythm floor and a measured single-part floor of 4
   (below the real minimum of 5 across 66 ensemble movements) for the shape one.
   `scalar_overuse`'s 0.25 sat *inside* the real distribution — Palestrina's
   MEDIAN movement is 0.231, because conjunct motion is what singable polyphony
   is made of — so it is now 0.30, and 0.50 for the Renaissance, above the real
   max of 0.438.

**After:** every rate in the table above is 0% except monteverdi
`rhythm_vocabulary_poverty` 16% and bach `syncopation_absent` 5% (pre-existing,
one chorale with no off-beat attack). The 26 piano reference movements are
**unchanged at zero on all seven**, and the detectors keep their teeth on
generated output: `register_stasis` still fires on 7 of 47 pieces,
`voicing_poverty` 6, `scalar_overuse` 5, and the generated "motet" is still
caught for having two distinct note values per staff.

`test_detectors_do_not_reject_ensemble_music` pins all of it. It reads music21's
corpus, because `reference_scores/` — the corpus every threshold in the file was
falsified against — contains no early music and no ensemble music at all. That
is the real lesson: the calibration harness was honest about its numbers and
silent about its sample.

---

## Addendum 82 — a blocking check that rejected 56% of real Haydn

`_section_gate` fails on `musical_ear`'s `error`-severity findings, and
`bar_length` is the main one. CLAUDE.md justified that with "every detector was
falsified against real sonatas and mazurkas (zero errors on nine of them)".
Ran it over real ensemble music instead:

| corpus | movements blocked |
|---|---|
| haydn quartets | **5/9 (56%)** |
| beethoven sonatas (kern) | 8/26 (31%) |
| monteverdi madrigals | 3/25 (12%) |
| bach | 1/20 (5%) |

**What the bars actually held.** `4.95833 beats but the meter is 4/4`, and the
same 23/24 overshoot in 3/4 and 2/4. Reading the bar rather than the number:
Haydn's Violin I has two voices, and voice 2's *trailing rest* starts at 3.958
and lasts a full beat. `highestTime` is genuinely 119/24 — the arithmetic was
right, the bar really does run past its barline, and **nothing sounds late**.

Real engraving does this constantly. Of the overfull bars in real scores, 56/56
Monteverdi and 11/11 Haydn are rests-only; 77% overall. So the detector now
separates an overshoot you can hear from one you cannot: a NOTE past the barline
stays an error — that is the exact shape of every notation bug this system has
shipped, a pedal figure parsed sequentially into 7.5 beats of 4/4 — and a
rests-only overshoot is a warning. This system's own engraver writes rests-only
overshoots too (69 bars across three workspace pieces), so this was never
confined to imported files. After: haydn 56%→0%, monteverdi 12%→0%, and the 878
note-overshoot bars in old workspace pieces still raise errors.

**Two corrections to my own reasoning, both caught by measuring.** I proposed
excusing any bar whose extent exceeds 2× the meter as an obvious parse collapse —
465 beats inside a 2/4 bar is not music. But 73 of the 102 errors in the corpus
sit *under* 2×, so the ratio does not separate importer damage from a real
overflow, and no such rule was shipped. And the surviving Beethoven rate is
Humdrum import damage, not a detector defect: it stays.

**The harness was hiding the rate behind its sample.** The calibration test
allowlisted two filenames and passed. It draws 14 Mozart, 6 Chopin and 6
Beethoven files; across all 224 files in `reference_scores/`, **36 (16%)** raise a
blocking error. A two-name allowlist over a 26-file draw reads as "two flukes"
when the truth is a systematic 16%. The test now asserts the *rate*, fails on any
blocking error that is not `bar_length`, and a new test asserts zero blocking
errors on real quartets, madrigals and motets.

The general lesson, and the same one as Addendum 81: `reference_scores/` is
piano, and it is Humdrum. Every threshold in `musical_ear` and `score_realism`
was falsified against that and nothing else, while the system now writes choral
and orchestral scores. The harness was honest about its numbers and silent about
its sample. CLAUDE.md's claim has been corrected in place.

---

## Addendum 83 — the range check could not reach a single singer

CLAUDE.md promises the commit gate blocks "a note outside the instrument's
range". `validate_range` looks its bounds up as
`INSTRUMENT_RANGES.get(instrumentation, (21, 108))` — keyed on the **piece's**
instrumentation. The graphs carry `"ensemble"`, `"choir"`, `"orchestra"`. The
table's keys are `soprano`, `alto`, `tenor`, `bass`, `violin`, `cello` and 37
more. **No ensemble piece could match any of them**, so every one fell through
to the piano keyboard and was then clamped to it again by
`constraints.piano_low/high`. The check ran on every commit and could not have
reported a soprano written at C7. [[feedback_a_missed_lookup_is_silent]].

Two adjacent findings, both from asking what the words resolve to:

- `is_keyboard("chorale")` was **True** — unknown-means-yes — so a piece for four
  sung voices was checked for hand span and notes-per-hand, which a choir does
  not have. The unambiguous sung forms (`motet`, `madrigal`, `mass`, `anthem`,
  `requiem`, `cantata`, `a_cappella`) are now ensemble words. `chorale` is
  deliberately left out: a chorale is sung, a chorale *prelude* is for organ, and
  the word cannot tell them apart.
- The assembler carried a **second, shorter copy** of the vocal word list —
  `choir`/`satb`/`voices` but not `motet`/`madrigal`/`mass` — so "a motet for
  four parts" was built through the orchestral path and exported as a Piano and a
  Violoncello, the exact bug the comment above it says was fixed. Both now call
  one `is_vocal`.

**I mis-diagnosed the damage first, and measuring refuted me.** The generated
motet has a soprano on A3/B3 and a bass on E4/F4, which is plainly wrong against
a Bach chorale (soprano 60-81, bass 36-62). But real Palestrina cantus reaches
down to G3 and real bassus up to E4, so the piece is inside what its own
repertoire does. Nothing shipped was out of range. This closes an unmet promise
rather than repairing damage — worth saying plainly, because the tempting write-up
is the one where I caught something.

Bounds are the **union of measured extremes** over 60 Bach chorales, 40
Palestrina works and 25 Monteverdi works, never a percentile or a textbook
tessitura: soprano 55-81, alto 45-77, tenor 48-72, bass 36-65. The textbook alto
floor of 53 rejects 6.2% of real Monteverdi alto notes
([[feedback_percentile_is_not_the_bound]]). `test_vocal_range_check.py` pins the
catch, the spellings, the pieces it must leave alone, and the falsification.

---

## Addendum 84 — the Bass part was singing the tenor line

Traced a four-voice SATB bar from shorthand to engraved parts:

```
composer wrote   RH = C5 B4 A4 G4 // E4 D4 C4 B3     (soprano // alto)
                 LH = G3 G3 F3 G3 // C3 G2 F2 G2     (tenor  // bass)

engraved as      Soprano  C5 B4 A4 G4      correct
                 Alto     E4 D4 C4 B3      correct
                 Bass     G3 G3 F3 G3   <- the TENOR line
                 Tenor    C3 G2 F2 G2   <- the BASS line
```

`direct_compose` files the first-written LH voice as `bass_foundation` and the
second as `response_layer`. That is right for piano, where the branch was built
for a sustained pedal note written before its figuration. **SATB closed score
writes the upper voice first** — tenor, stems up — so the convention inverts, and
the ensemble path in `music_io` gives each layer its own staff: `bass_foundation`
becomes the part named Bass, `response_layer` the part named Tenor. Every choral
piece this system has written has the two lower parts swapped.

Soprano and Alto are correct, which is why nothing caught it: the score looks
right, sounds right (the same four pitches sound either way), and only the part
LABELS are wrong — so a singer reads the wrong line and a range check reads the
wrong bounds. It survived a whole-score realism audit, an ear report and a
section gate, none of which compares a part's name to its content.

Fixed by ordering the lower staff's voices by pitch rather than by writing order,
because `bass_foundation` means *the lowest voice*. Restricted to sung parts: a
piano's pedal note is not reliably below its own figuration, and that branch is
depended on. Both are pinned — one test that the Bass part sits below the Tenor,
one that a pianist's left hand keeps `C2w // figuration` in written order.

Found only because Addendum 83's `VOICE_FOR_LAYER` had to state which layer is
which voice, and stating it made the contradiction visible. The mapping had
existed in `assembler._VOCAL_ROLES` all along, agreeing with itself and
disagreeing with the composer.

---

## Addendum 85 — a string quartet scored for clarinet and bassoon

The choir fix in Addendum 83 raised the obvious next question: a string quartet
is neither a keyboard nor vocal, so what does it get? Traced the four layers:

```
                 BEFORE                 AFTER
melody           Violin                 Violin        part reads "Violin I"
counter_reply    Clarinet   <--         Violin        part reads "Violin II"
response         Bassoon    <--         Viola         part reads "Viola"
bass             Violoncello            Violoncello   part reads "Violoncello"
```

With no roles table of its own, the abstract layer names fell through
`_LAYER_INSTRUMENTS`, which is a generic mixed chamber group. So "a quartet in
Haydn's style" — written from the Haydn corpus, which *is* string quartets — came
out scored for violin, clarinet, bassoon and cello. The parts were named
"Melody", "Counter Reply", "Response" and "Bass", so no player could find their
line either; that half is the same complaint the code already makes about choirs
two functions above, fixed there and not here.

`is_string_ensemble` requires the word "string" to actually be present. "Quartet"
alone will not do — a quartet can be winds, brass or voices, and guessing strings
would hand a wind quartet a viola. A staff that names a REAL instrument still
wins over the roles table, because an orchestration plan spells its staves
`flute`, `violin_1`, `timpani`, and a cantata genuinely has an orchestra in it.

**Suite state, honestly.** 2,447 pass. Five fail, all downstream of
`_repair_engine_surface` in `scales.py` and the orchestration planner — files
another session wrote at 04:32:49, *during* the run. The set changes between runs
and `test_one_reconstructor` passes in isolation, which is the signature of a
concurrent edit rather than a regression. Every test covering what this session
changed — vocal ranges, staff assignment, notation fidelity, realism, the ear,
the validator — passes.

---

## Addendum 86 — the brief told a choir about its hands

The word "instrumentation" did not appear anywhere in `composition_brief.py`.
The brief is the document Claude reads before writing every note, and it did not
know what the piece was scored for. So the four-voice motet's brief opened its
VOICING section with:

> Each hand spans about 3 semitones (LH) and 3 (RH) within a bar; the hands sit
> about 15 semitones apart.

and labelled all 30 of its exemplar, named-gesture and continuity lines `RH:` and
`LH:`. A choir has no hands. Every piece of corpus evidence arrived in a
vocabulary the composer had to translate before it meant anything, in the one
document with the most direct influence on the notes.

The corpus bar records genuinely ARE a two-hand reduction, so the labels change
and the measurement does not: for anything not played at a keyboard, those two
staves are the upper and lower voices of the texture. `piece_forces(graph)`
returns the pair of labels and whether the piece is a keyboard at all; three
emission sites use it — exemplars, named gestures, the previous-bar continuity
line — and the VOICING paragraph swaps the hand-span sentence for voice spacing.
No graph still means hands, the same default `is_keyboard` takes and for the same
reason.

After: the motet's brief has 30 `UPPER:`/`LOWER:` lines and zero `RH:`; the
Mozart andante's has 30 `RH:`/`LH:` lines and zero `UPPER:`, with its hand-span
sentence intact.

**A probe error worth recording.** I measured this with `re.findall` inside a
quoted heredoc and wrote `\\bRH:`, so Python matched a literal backslash and
reported **zero** RH lines for the piano brief — which reads exactly like a
regression I had just caused. Printing the lines showed 30 of them, unchanged.
Third time this session a measurement, not the code, was the thing that was
wrong ([[feedback_verify_the_measurement_reproduces_a_known_result]]).

Suite: 2,458 pass, 0 fail — the concurrent `_repair_engine_surface` work noted in
Addendum 85 has landed.

---

## Addendum 87 — the same two-spelling whitelist, twice more

`validator.py` carries a comment recording a defect already fixed there: the
playability check was `instrumentation in ("solo_piano", "piano")` while the
graphs on disk carry four spellings. Counted them:

```
54x 'solo_piano'   2x 'piano'   2x 'piano_solo'   1x 'solo piano'   4x 'choir'   1x 'ensemble'
```

Two more copies of that whitelist were still live, and **both fail silently**,
which is why neither was noticed:

- `expression_enricher._add_pedal` returned early for `piano_solo` and
  `solo piano`, so three workspace pieces got **no pedal marks at all**. A
  missing pedal is invisible: it looks exactly like a style that pedals
  sparingly, and the enricher's report says only what it added.
- `scales._physical_constraints` set `keyboard=False` for those same spellings.
  `validate_layer_ir` reads that to decide whether hand span and notes-per-hand
  apply — so a solo piano work spelled with a **space** had no hand-span
  constraint at all. That is a strict, non-waivable physical constraint switched
  off by a character in a string.

Both now go through `models.is_keyboard`, which normalizes spacing, hyphens and
case. The enricher additionally excludes harpsichord, clavichord, organ and
celesta: they are keyboards, and none of them has a sustain pedal to lift — the
period profile happened to cover that for Baroque styles, and would not have for
a harpsichord piece asked for in a Romantic idiom.

Verified by reproducing the original failure: pedal marks are now 2 for all five
piano spellings, 0 for the four pedal-less keyboards and 0 for choir, quartet,
orchestra and ensemble. The third copy, in `assembler.py`, normalizes before it
compares and was already correct — worth stating, since the sweep found three
sites and only two were broken.

Suite 2,477 pass. This is the fourth distinct defect this session whose whole
mechanism was a lookup that missed and returned a plausible value
([[feedback_a_missed_lookup_is_silent]]).

---

## Addendum 88 — the critic was hearing a piano and a cello

The `music-critic` is the sole driver of artistic revision, and what it judges is
the MIDI preview. `midi_renderer._score_from_parts` carried a **third** copy of
the vocal word list — the same short one as the assembler's, which knows "choir"
and "satb" but not "motet", "madrigal" or "mass" — and knew nothing about string
ensembles at all.

So a motet was previewed as a piano and a cello, and therefore *reviewed* as a
piano and a cello: every judgement about whether the line sings, whether the
voices balance, whether the texture breathes, formed against the wrong timbres.
A string quartet previewed with a clarinet and a bassoon in it.

All three copies now call `is_vocal` / `is_string_ensemble`:

| instrumentation | preview plays |
|---|---|
| a sacred motet for four voices | Soprano, Alto, Tenor, Bass |
| satb choir | Soprano, Alto, Tenor, Bass |
| string quartet | Violin, Violin, Viola, Violoncello |
| orchestra | Violin, Clarinet, Bassoon, Violoncello |
| solo_piano | Piano ×4 |

Orchestra keeps the mixed group on purpose — an orchestral piece really does have
winds in it.

Counting the session's ensemble thread: the same fact (what the piece is scored
for) was decided independently in five places — the validator, the assembler, the
MIDI renderer, the brief, and the physical constraints — with three different
word lists and two different defaults, and four of the five were wrong for at
least one real spelling. Suite 2,478 pass.

---

## Addendum 89 — the ear's commonest warning fires on all real music

Measured every warn-level `musical_ear` detector across real repertoire. One
dominates everything else:

| corpus | `vertical_clash` fires on |
|---|---|
| real mozart sonatas | 79% of movements |
| real palestrina motets | **100%** |
| real haydn quartets | **100%** |

A minor 2nd is not rare in tonal music; in suspension-driven polyphony it is the
idiom. The critic reads these before deciding what to revise, and a warning
present in essentially every real movement teaches it to discount the ones that
matter — the argument `detect_rhythm_vocabulary_poverty` already makes in its own
docstring, unapplied here.

Measured as a **rate** there is a real signal:

```
real mozart sonatas   median  2.8 per 100 bars   max 22.2
real chopin mazurkas  median  3.5                max 11.6
real haydn quartets   median  7.1                max 17.4
real palestrina       median 11.6                max 22.2
GENERATED pieces      median 16.7                max 40.0
```

Generated output clashes ~5x as often as real piano music. But the distributions
overlap — real Palestrina's median is 11.6 — so this is not a threshold to block
on, and promoting it would fail the standing test. It is a number the critic
needs in order to judge, and it was not there.

Every clash finding now carries `clashes_in_piece`, `clashes_per_100_bars` and
the reference table, and the first says it in prose, since the critic reads prose
and not evidence dicts.

**The count could not have been computed before.** The loop `break`s at `cap`, so
a piece with 200 clashes and a piece with 8 reported the same eight findings and
the same nothing about scale. It now counts the whole score and lists `cap` — 12
counted, 8 listed on the first real Mozart sonata. That is the shape of
[[feedback_a_missed_lookup_is_silent]] again: not a wrong answer, an
*unaskable question*.

---

## Addendum 90 — 560 overfull bars scored the same as 13

`composite_score` ranks a revision lexicographically by `(-errors,
-actionable_warns, critic_quality, -critic_rank)`, and those counts come from
`convergence.detector_counts`, which counted the **findings list**. Every
detector lists at most `cap` findings and stops scanning there.

So the keep-best mechanism was blind above the cap. Measured on the workspace:

```
montana-seasons-sonata-dm   listed 12 bar_length findings   actually 560
montana-cabin-wildlife-bbm  listed 12                       actually 308
ocean-gm                    listed 12                       actually  13
```

A section with 560 overfull bars and one with 13 were indistinguishable, and a
revision repairing 547 of them registered as **no improvement at all**. 33% of
the generated scores that trip `bar_length` sit exactly at its cap, so this is
not a corner case.

`cap` now limits what is LISTED, never what is counted: `bar_length` and
`vertical_clash` record the true total in each finding's
`evidence["occurrences"]`, and `detector_counts` takes the larger of that and the
list length — larger, so an under-reported or stale `occurrences` can never
shrink a count below what is actually present.

Found by sweeping for the same shape as Addendum 89's clash count. That one made
a rate uncomputable; this one made a comparison wrong. Both are the same
underlying mistake: **a display limit doing duty as a measurement.**

---

## Addendum 91 — correcting Addendum 89's survey, and two detectors cleared

**My survey disabled eight of the fourteen detectors.** `ear_report(score_path,
bars, graph=None)` takes `bars` as a required positional, and I passed `[]`.
Six detectors read the parsed `score` and were unaffected — `bar_length`,
`out_of_range`, `vertical_clash`, `melody_buried` — so every blocking measurement
in Addenda 82 and 89 stands. But the eight bar-based detectors could not fire at
all, so "vertical_clash dominates everything else" was measured against silence.

Re-run with real bars:

| detector | real mozart | real chopin | generated |
|---|---|---|---|
| `vertical_clash` | 75% | 50% | 68% |
| `bar_length` | 50% | 33% | 11% |
| `arpeggiated_melody` | 33% | 17% | 9% |
| `static_bass` | 8% | 33% | 6% |
| `harmonic_stagnation` | 8% | 25% | 11% |
| `unresolved_nct` | 8% | — | 17% |
| `no_breathing` | — | 17% | 9% |

The conclusion holds — clash is still the loudest by a wide margin, and still
fires on most real music — but it was reached from an incomplete run and is worth
correcting in place. Note also that the generated pieces are **not** worse than
real music on most of these; `unresolved_nct` is the one where they are.

**Two detectors suspected and cleared.** `monotony` and
`photocopied_accompaniment` fired on none of 47 generated pieces, which given
this project's history reads like a detector that cannot report
([[feedback_two_kinds_of_detector_falsification]]: a detector that FINDS needs
ground truth). Fed input that must trigger them:

- `monotony`: 8 literally identical bars → fires. Correct.
- `photocopied_accompaniment`: 20 bars of identical left hand → fires at 100%
  share; the same figure following the harmony into new positions → silent;
  11 bars → silent, because "throughout" needs a span to mean anything.

Both work. My first ground-truth attempt used 8 bars and reported the photocopy
detector as broken — its floor is 12. That is the **fourth** probe error this
session, against roughly a dozen real defects. The ratio is worth stating: when a
measurement says something surprising, the measurement is the more likely
suspect.

---

## Addendum 92 — the craft advice, and the contradiction I nearly shipped

Addendum 86 relabelled the brief's exemplars `UPPER:`/`LOWER:` for anything not
played at a keyboard. Reading the resulting choral brief end to end, two things
were still wrong, and one of them was **my own doing**:

1. `_MINDSET` — the brief's craft section, and the most emphatic thing in the
   document — is written for a pianist, because for a long time every piece was
   one. It told the motet's composer to write *"genuine two-voice-per-hand
   polyphony"*, to *"USE THE WHOLE KEYBOARD"*, and offered `:arp` as *"the rolled
   chord — the most characteristic piano notation there is"*. A choir has no
   hands, no keyboard, and cannot roll a chord. The craft advice underneath is
   sound, so it is reworded rather than removed: "two independent voices per
   staff", "USE THE WHOLE RANGE", ":arp — for instruments that can roll one".

2. **The contradiction I introduced.** The bar dict keys do not change with the
   forces: a commit is always `{'rh': ..., 'lh': ...}`. Having relabelled every
   exemplar UPPER/LOWER and said nothing about that, I had built exactly the
   failure [[feedback_contradictory_guidance]] records — the composer reads one
   vocabulary and must write another, in the same document. Non-keyboard briefs
   now state it: the keys stay `rh`/`lh` and mean the upper and lower staff.

Caught by reading the whole rendered brief rather than the lines I had changed.
The diff was correct; the document it produced was not.

Suite 2,493 pass, lint clean.

---

## Addendum 93 — the first violin was filed as filler

Three tables look an instrument up by name:

- `RoleDecomposer._ROLE_PRIORS` — keyed `violin_1`, `cello`, `flute`
- SABRE's melody/bass/inner candidate lists — the same spellings
- `validator.INSTRUMENT_RANGES` — keyed `cello`, `double_bass`, `english_horn`

A real score's `partName` says **"Violin I"**, **"1st Violin"**, **"Violoncello"**,
**"Contrabass"**, **"Cor Anglais"**. Collected the part names from real music21
scores and checked: **11 of 15 missed** `_ROLE_PRIORS`, including every violin
spelling and all four voice names. A miss returns `HARMONIC_PAD`.

So in `reduce_to_piano` — the whole point of which is to preserve what matters —
the first violin, the part carrying the tune, was classified as **filler in every
real orchestral score**, and a chorale's soprano with it. SABRE then fell through
to "the first part is the melody and the last is the bass", which is true only by
accident of score order.

One resolver now: `models.canonical_instrument(name) -> (key, division)`. It
lowercases, strips punctuation and hyphens, pulls the division out separately
("Violin I" and "Violin II" are the same instrument and different roles), and
maps 40 real spellings — `violoncello`→`cello`, `contrabass`→`double_bass`,
`corno inglese`→`english_horn`, `fagotto`→`bassoon`, `bassus`→`bass`. All three
call sites use it, and `_ROLE_PRIORS` gained the ten instruments that had a range
but no role (piccolo, english horn, bass clarinet, contrabassoon, harp, celesta,
glockenspiel, bass trombone) plus plain `violin` and the four voices.

After: **0 of 15** real part names miss. `test_instrument_names_resolve.py` pins
every spelling, that a division stays separate from the instrument, that the
first violin is the melody and the cello the bass, and that an unknown name
resolves to itself rather than guessing.

**Suite note.** 2,513 of 2,515 pass; the two failures shift between runs and pass
in isolation and as a pair. `surface_composer.py`, `scales.py`, `assembler.py`,
`test_notation_fidelity.py` and a workspace piece_graph were all written in the
ten minutes spanning the run — another session is running the pipeline live. All
219 tests covering what this session changed pass.

---

## Addendum 94 — `reduce_to_piano` verified end to end

Addendum 93's fix serves the reduction mode, so I ran it rather than trusting the
unit tests. A real Haydn quartet movement (Violin I / Violin II / Viola / Cello),
through `init_workspace` → `reduce_to_piano` → `assemble`:

```
instruments_reduced 4     bars 42     notes 1116
repairs  snapped 87, overlaps_trimmed 24, overflow_dropped 3,
         isolated_tuplet_rewritten 24
```

- **The tune survives.** Violin I opens `Ab4 Ab4 G4 C5 Bb4`; the reduction's
  `principal_line` opens on chords topped `Ab4 Ab4 G4 C5`. Before Addendum 93,
  "Violin I" missed `_ROLE_PRIORS` and that part was a harmonic pad.
- **It is actually playable**, which is what `mode="playable_reduction"` claims:
  of 340 simultaneities, the widest is **exactly 16 semitones** — the hand-span
  limit — none exceeds it, and no hand is asked for more than 3 notes.
- **It assembles clean**: 42 bars on two piano staves, zero blocking ear errors.

Two probe errors on the way, both mine: the phrase's LayerIR is stored under
`realized`, not `layer_ir` (I read the empty key and nearly reported the mode as
persisting nothing), and `init_workspace` takes `mode` as a required positional.
The stray `workspace/reduce-probe/` the assembler wrote relative to the repo root
has been removed.

No new defect. Recorded because "the mode runs" and "the mode preserves the
melody and fits under two hands" are different claims, and only the second is
worth anything — [[feedback_verify_the_fix_not_the_shape]].

---

## Addendum 95 — the dominant seventh had no seventh

Swept every dynamic dict lookup in `tools/scales` whose fallback is a concrete,
plausible value — this session's most productive defect shape. 34 sites; two were
wrong, and one of them is the most-used chord in tonal music.

**`chord_tones` dropped the seventh from every V7.** It looked up
`CHORD_INTERVALS.get(quality, [0, 4, 7])`. The table is keyed `7` and `hdim7`.
The corpus — and `analyze_score_bars`, which writes it — spells them **`dom7`**
and **`halfdim7`**:

```
chord_tones(60, "dom7")     -> [60, 64, 67]    the seventh, gone
chord_tones(60, "halfdim7") -> [60, 64, 67]    a MAJOR triad
```

`dom7` covers **734 bars of Mozart alone**. Every caller is on the engine
realization path — `harmonic_solver`, `realizer` (four sites), `surface_composer`
(three) — so every dominant seventh the engine realized came out a plain triad,
and every half-diminished chord came out major. The second is worse than the
first: a missing seventh is a thinner chord, a major triad where a half-diminished
belongs is a different harmony.

Fixed with `chord_intervals()` and a `CHORD_QUALITY_ALIASES` table covering the
corpus spellings plus the obvious variants (`m7`, `major7`, `M7`, case). An
unknown quality still yields a major triad, because every caller is building
notes and none can use nothing back. A test asserts the corpus vocabulary stays
covered, which is exactly the check that would have caught `dom7` arriving.

**A choir was orchestrated onto flute, oboe, clarinet, bassoon and horn.**
`orchestrate_section`'s `default_ensembles` has three keys — `orchestra`,
`string_quartet`, `string_orchestra` — and falls back to `orchestra`. A contract
carries `"string quartet"` **with a space**, and there was no choir roster at
all, so both a quartet and a choir were scored for winds and strings. Now
normalized, with a `choir` roster (soprano/alto/tenor/bass) and string
trio/quintet, routed through `is_vocal` / `is_string_ensemble`.

Both are the same shape as the pedal and hand-span whitelists in Addendum 87, and
the same reason nothing noticed: **the fallback was musically plausible.** A
piece full of triads where sevenths belong sounds tame, not broken.

Suite 2,536 pass.

---

## Addendum 96 — a minimalist trill started on the upper note

`_PERIOD_PROFILES` shares performance parameters between periods deliberately: an
impressionist piece really is played with romantic freedom, a minimalist one with
classical precision. But it shared the profile **object**, so it shared the period
**name** — and `profile.period` is read to decide period-specific behaviour:

```python
# ornament_realization.realize_trill
start_upper = period in ("baroque", "classical", "renaissance")
```

`modern` and `minimalist` both mapped to `_CLASSICAL`, whose `.period` is
`"classical"`. So Glass, Reich, Stravinsky, Schoenberg, Bartok, Copland,
Messiaen, Prokofiev, Shostakovich, Webern and Arvo Pärt — every composer the
registry calls modern or minimalist — got **upper-note trills**, which is Baroque
and Classical practice and wrong by a century and a half. It is audible: the
preview the `music-critic` judges plays the ornament out.

The file already contains this exact fix, for one period. Four lines above the
table: `_RENAISSANCE = replace(_BAROQUE, period="renaissance")`, with the note
that "Palestrina reporting himself as baroque is simply wrong". The other six
borrowings — late-romantic, impressionist, nationalistic, film-score, modern,
minimalist — were left as aliases. Each now gets its own `replace(..., period=)`.

After: Renaissance/Baroque/Classical start above, everything from Romantic onward
starts on the note. A test asserts every profile reports its own name, and
another asserts the parameter sharing still holds, since that part was correct —
`replace(impressionist, period="romantic") == romantic`.

Found by sweeping the same `dict.get(x, <plausible default>)` shape as Addendum
95 and following `_PERIOD_PROFILES` to its readers. The lookup itself was fine;
what it returned carried a wrong label. Sibling of
[[project_labels_never_checked_against_content]] — the Bass part singing the
tenor line was the same mistake in the score rather than in a profile.

Suite 2,564 pass, lint clean.

---

## Addendum 97 — the plan said "the bass carries the line" and nothing listened

Swept `models.py`'s 582 dataclass fields for ones something WRITES and nothing
READS — the dead-field shape. 38 survived a corrected count (my first pass
excluded `models.py` itself and produced 47 false positives, since
`CandidateScores`' sub-scores are read by its own `composite`). The most
expensive of the 38 is audible.

`performance_renderer.apply_voicing_priorities` exists so a phrase can say which
voice is brought out. Its docstring: *"Emphasise the voices the plan names,
instead of always the melody. A plan that says the bass carries the line, or that
an inner voice should be brought out, had no way to say so."* It writes
`PerformanceIR.voicing_emphasis`, one entry per bar.

**Nothing read it.** Every reference outside `performance_renderer` (which
filters its own list) was in a test. The MIDI renderer — which produces the sound
the `music-critic` judges, and whose module docstring claims the dynamic curve
comes "with melody voicing emphasis" — never applied it. A phrase planned around
a singing bass rendered identically to one planned around a singing melody.

Verified by reproducing the original failure on a real piece, rendering it twice:

```
default plan    bass velocity mean 64.2   (n=140)
bass-led plan   bass velocity mean 79.0   (n=140)
```

Before the fix both were 64.2. The renderer now maps the plan's voice names
(`melody`, `bass`, `inner`, `alto`, `tenor`, …) onto the layers an EventIR
carries, and a plan may also name a layer directly.

**The tests made it harder to see, not easier.** Five existing assertions checked
that `voicing_emphasis` was correctly BUILT — which was true — and none that it
changed a note. That is the proxy-test shape: measuring the spelling, not the
wiring ([[project_correct_analysis_wired_to_nothing]]). The new tests assert a
velocity difference, and that emphasising the MELODY does *not* lift the bass,
since an emphasis that raises everything is just a volume knob.

**One more, found by my own test failing.** `scoped_basename("")` returns `""`,
so a graph with no `piece_id` wrote a file called `.mid` — hidden on Unix, and
music21 refuses to parse it back. Now falls back to `piece`.

**And one probe error.** My first fixture set `role="bass_foundation"` but left
`source_layer` empty, so nothing matched and I nearly concluded the fix had not
worked. Production sets `source_layer` on every event (2,445 checked across 20
workspace pieces: `principal_line` 1285, `bass_foundation` 972, …) — a fixture
that omits it is testing a shape production never has.

Suite 2,589 pass.

---

## Addendum 98 — a piece two-thirds missing reported no warnings

`_authoring_summary` split phrases two ways:

```python
if getattr(st, "agent_authored", False): authored += 1
else:                                    engine   += 1
```

so a phrase with `status="planned"` and **zero events** was counted as one the
engine had written. A real workspace piece — `beethoven-orch-cmin`, 3 of 9
phrases composed — reported:

```
{"phrases": 9, "agent_authored": 3, "engine_realized": 6}     warnings: []
```

which reads as a finished piece realized by two paths. It is a third of a piece.
The assembled score was simply shorter with nothing explaining why, and every
measurement in the report — 18 bars, density, cadences, realism, the ear, the
three flags about flat density and too-few durations — described that third as
though it were the work.

Now three states, not two: `agent_authored`, `engine_realized` (has notes, agent
didn't write them) and `unrealized` (no notes in any layer), with the missing
phrases named. `self_evaluate` opens its warnings with

> INCOMPLETE: 6 of 9 phrases have no notes at all (m1_a_p3, m1_b_p2, m1_retr_p1,
> m1_a2_p1, m1_a2_p2, m1_coda_p1). Every measurement in this report describes
> only the phrases that exist.

A test asserts the engine's real work is still counted as engine work — the fix
must not hide the fallback the way the old code hid missing phrases — and that a
phrase written entirely into the bass or an inner voice counts as realized.

**Two of my own errors on the way**, both from anchors matching the wrong thing:
`_authoring_summary(graph, section_id)` appears twice, so my first warning patch
refused to apply, and my second landed in `compare_to_corpus` instead of
`self_evaluate` — where it was correct but never exercised, which looked exactly
like the fix not working.

Suite 2,594 pass.

---

## Addendum 99 — a fifth of the exemplar relevance model was a constant

`PhraseQuery` scores corpus retrieval on nine dimensions. Three of them —
`contour_class`, `entry_texture`, `cadence_distance`, worth **0.20 of the
ranking** — are set by **no caller**. All three construction sites (the brief,
the sketch proposer, the surface composer) pass function, cadence, length and key
mode and stop. Unset, `phrase_bank` scores each a flat 0.5 for every candidate,
so a fifth of the relevance model could not affect which exemplar came back — and
the exemplars are what the agent adapts when it writes notes.

The planner knows all three. Now the brief's query says so: `cadence_distance`
from the phrase length, `entry_texture` from the texture planned for its first
bar (resolves on 9/9 phrases of a real piece), and `contour_class` from the
dramatic role.

**Two rules for `contour_class` were tried and rejected first, by measuring.**

1. `last - first` off the register curve → **"static" for all 26 planned slots**,
   because an arch starts and ends in the same place.
2. Peak-position off the same curve → **"ascending" for all 26**, because every
   planned register curve is the same arch.

A discriminator with one value discriminates nothing while looking like it works
— and would have quietly scored every candidate identically. The dramatic role
varies across nine values and says the same musical thing: intensify/crisis/depart
rise, retreat/close fall, establish/extend/confirm/return hold. Spread is now
5/2/2 on a ternary and 10/5/2 on a sonata.

The vocabulary was checked against the corpus before anything was set: measured
over 9,569 indexed phrases, `melody_directions` contains exactly `static`
(17,180), `descending` (9,912) and `ascending` (9,287) and nothing else. A word
outside that set would have scored every candidate **0.0** instead of a neutral
0.5 — worse than leaving it unset.

One thing checked and cleared: the register curves are empty on the older
workspace pieces, which looked like the loader-drops-curves bug this repo has had
before. A save/load round-trip of a freshly planned slot preserves them exactly;
those pieces simply predate the dramatic plan.

Suite 2,599 pass.

**Addendum 99, continued — the other two query sites.** There are three
`PhraseQuery` constructors and all three were blind, so fixing only the brief
would have left both engine paths retrieving on a constant. `sketch_proposer`
now sets all three. `surface_composer` sets `cadence_distance` and
`entry_texture` and deliberately leaves `contour_class` unset: a
`PhraseControlIR` carries no dramatic role, and every rule read off a register
curve returns one value for every phrase — unset scores a neutral 0.5, a wrong
word scores 0.0 for every candidate. A test parses all three files with AST and
asserts each site carries what it can honestly answer.

---

## Addendum 100 — the intermittent test failure was real, and it was the test

A test failed in the full suite and passed in isolation, repeatedly, all session.
I attributed it to concurrent edits and moved on twice. It IS caused by
concurrent edits, and the fragility is in the test:

```python
src = inspect.getsource(assembler._parse_key)
assert "music21" not in src
```

`inspect.getsource` reads the file **from disk at the line numbers recorded when
the module was imported**. If anything edits that file during the run — another
session, a formatter, this session's own patches — the line numbers no longer
line up and it returns the text of a *different* function. The assertion then
passes or fails on unrelated code.

`test_the_key_parsers_are_delegates_not_copies` now locates the function by NAME
through the AST and compares `ast.unparse(node)`, which is immune to line drift.

**My own new test had the same bug**, added an hour earlier: it read
`_phrase_shape` with `getsource` and failed in the very next full run while the
other session was editing `composition_brief.py`. Converted the same way.

23 test files use `inspect.getsource`. The technique is legitimate — these are
"is it actually wired" tests, which is the check this codebase most needs — but
it should locate code by name, not by offset. The remaining 22 are left as they
are: none has flapped, and rewriting them blind is a large change for a fault
that only manifests under concurrent editing. Recorded here so the next
intermittent failure in one of them is diagnosed in a minute rather than
dismissed three times.

The lesson is the same one as the earlier grep-vs-parse fixes: **pin behaviour by
parsing, never by reading source at a remembered position.**

---

## Addendum 101 — the notation path, checked hop by hop and locked down

`music_io._layer_to_event` calls itself "the single choke point between what the
agent wrote and what gets engraved: a field missing from this list is a mark that
vanishes with no error anywhere, which is how `expression` used to be lost." It
is one of three hops — LayerEvent → EventIR → music21 → MusicXML — and a mark can
die at any of them, silently, in the layer that most distinguishes an engraved
score from a machine-made one.

Drove all sixteen `LayerEvent` fields through the real `assemble` and grepped the
written file. **Every one survives**: articulation, dynamic, expression,
ornament, slur, hairpin, tie, pedal, fingering, and all four technique families
(rolled chord, tremolo, ottava, glissando). No defect — recorded because "the
choke point is complete" and "the marks reach the page" are different claims and
only the second matters.

`test_every_written_mark_reaches_the_page.py` now pins it, including a check that
every value in `direct_compose._TECHNIQUES` — the vocabulary the shorthand
actually emits — is read somewhere in the assembler. The assembler handles
`arpeggio`/`tremolo` in its notation branch and `gliss`/`8va`/`8vb` in the
spanner pass, so a value in neither would be discarded with no error
([[project_dead_label_vocabulary]]).

**Four probe errors, all mine, and worth listing because they are the same
mistake four times.** I reported `dynamic` missing (my regex wanted `<f/>`;
music21 writes `<ff />` with a space), `technique` missing (I invented the value
`arpeggiate`; the vocabulary is `arpeggio`), `tie` missing (I tied a C5 to a D5 —
that is not a tie), and `gliss` missing (one endpoint is not a spanner). Every
one looked exactly like a real defect until the needle was checked. The running
count for the session is now about eight probe errors against roughly forty real
defects.

**Suite note.** Six tests failed in one run — including two at COLLECTION, an
import error — and all six pass on re-run. `scales.py` was written 42 seconds
before that run; the other session has the pipeline running live. `scales.py`
parses cleanly now.

---

## Addendum 102 — converting the source-reading tests, and what that guards

Addendum 100 fixed one test that read code with `inspect.getsource` and flapped.
The fault is general: `getsource` resolves the **line numbers recorded on a code
object when its module was imported**, so once the file changes on disk it
returns whatever now occupies those lines. Three separate full-suite runs today
failed on it, twice at COLLECTION with an import error, all passing in isolation.

`conftest` already had the right tool — `_function_source(module, name)`, which
finds the definition through the AST, plus a `function_source` fixture. Ten call
sites still used `inspect.getsource` on a **function**. All are now converted:

| file | what it pins |
|---|---|
| `test_corpus_scope.py` | the scope warning is rendered before the fingerprint |
| `test_rhythmic_fingerprint.py` | the fingerprint reaches the brief |
| `test_stale_profile_fallback.py` | rebuild advice names `.venv/bin/python` |
| `test_one_reconstructor.py` | the note parser delegates; the key parsers are aliases |
| `test_engine_path_parity.py` | the engine path takes every step the agent path does |
| `test_engine_output_is_engraved.py` | the engine commit loop engraves |
| `test_bass_degree_and_altered_degrees.py` | one bass derivation, not three |
| `test_narrative_belongs_to_a_movement.py` | now asserts the function is CALLABLE |

The nineteen `getsource(module)` calls are left alone: passing a module returns
the whole file, which is current by construction — the hazard is entirely in the
per-function form.

That last conversion is the interesting one. It asserted
`inspect.getsource(models.narrative_section_is_in_movement)` — truthy source
text. The claim it wanted is that the single definition WORKS, and `callable()`
checks that better than reading its source at all. Which is the standing rule
`conftest` states next to the helper: **prefer testing behaviour; reach for
source-reading only where the claim is genuinely about the code** — "no function
in this module does X" — and not where the property can be observed by calling
something.

**Two mistakes of mine while doing it**, both mechanical and both caught
immediately: a slice that took `sig[:-3]` off `def name():` and produced
`def namefunction_source):` in four files at once (SyntaxError at collection),
and five imports of `inspect` left unused afterwards (ruff).

Suite: 2,625 pass, 0 fail, lint clean. One unrelated failure appeared in an
intermediate run and did not reproduce; `composition_brief.py` had not been
written for 22 minutes at that point, so it is recorded here as unexplained
rather than attributed to the concurrent session.

---

## Addendum 103 — the brief's fallback targets described no real composer

`_DISCRIMINATOR_FALLBACK` is what the brief prints as a TARGET when a composer
has no `corpus_profile` — so it is shown precisely when the system knows least,
which is where a wrong number does the most damage. All three bands were
hand-written. Measured against the 28 composer profiles that do exist:

| metric | brief said | real min | real median | real max | composers inside |
|---|---|---|---|---|---|
| `texture_change_pct` | 0.4-0.6 | 0.088 | **0.269** | 0.598 | **5 / 36** |
| `melody_direction_change_pct` | 0.3-0.6 | 0.346 | 0.558 | 0.667 | ceiling cuts the top quarter |
| `density_cv` | ≥0.30 | 0.213 | 0.318 | 0.583 | 24 / 36 |

The texture band's **floor sits above the median of every measured composer**, so
an unprofiled composer was told to change texture roughly twice as often as a
typical real one — which produces the opposite machine-tell: a different
accompaniment idiom in every bar.

**The doctrine already knew.** `human-sounding-music.md` documents this exact
correction in prose — *"The 58% figure was not just wrong, it was **actively
harmful**: it told the composer to change texture roughly twice as often as
Beethoven does"* — and cites the calibrated band 0.045-0.585. The markdown was
fixed and the code that restates it was not, so the two contradicted each other
and the code is the one the composer actually reads
([[feedback_contradictory_guidance]]).

Each band is now the measured middle half (p25-p75) with the median named and the
full real range quoted, so a settled texture reads as a style rather than a
fault. Armed composers are untouched — they use their own corpus bands, verified
unchanged.

`test_fallback_bands_describe_real_music.py` asserts each band contains the real
median, that at least 35% of real composers sit inside it, and that the text
states what it was measured from — a number with no provenance being
indistinguishable from a guess, which is what these were.

**Suite note.** 2,635 pass. Three failures in `test_melody_takes_weight.py`,
created two minutes before the run by the concurrent session and passing in
isolation — their in-flight work, not a regression here.

---

## Addendum 104 — composed a piece through the fixed pipeline, and it found a lying metric

Ran the whole thing as a user would, with no subagents: `init_workspace` →
`compile_style(chopin)` → `build_form_graph(ternary, Eb, 6/8)` → nine
`get_composition_brief` + `commit_agent_phrase_direct_bars` → `assemble` →
`self_evaluate`. A 41-bar nocturne, every note hand-written against the brief.

**The audit caught four real faults in my own composition**, which is the
strongest evidence this session produced that the measurement layer works:

```
cadence_formula   6 of 9 phrase endings used the identical cadential rhythm
tie_absent        0 ties in 41 bars — nothing held over a barline
register_stasis   the melody spanned 17 semitones; the canonical minimum is 24
scalar_overuse    20 of 34 melody bars (59%) were plain unbroken scale runs
```

Every one was true. I revised against them — varied each phrase ending, tied the
line over barlines, dropped the B section to the tenor and took the return an
octave up, broke the runs with leaps. Then the second round found a voicing
collision (a tenor-register melody sitting inside its own accompaniment chord)
and metronomic harmony (7% of bars changing chord within the bar against real
Mozart's 68%), and the third found the left hand carrying one idiom for 68% of
the piece.

```
round     1     2     3     4
realism   5  →  2  →  0  →  0
ear warn  7  →  3  →  4  →  0
ties      0  →  14 → 14 →  14
marks/bar 1.44 → 2.34 (real Chopin median 1.85, Mozart 2.02)
```

Final: 0 ear errors, 0 ear warnings, 0 realism findings, section gate passed,
**34 of 39 metrics inside real Chopin**.

**And the corpus comparison was lying about the other two.**

```
chorded_attack_pct   value 0.0   z -15.78   corpus mean 95.37
mean_sonority        value 0.0   z  -5.10   corpus mean  3.61
```

on a piece whose attacks are **100% chorded** with a mean sonority of 3.06. These
were the two largest deviations in the report — in every report — and the critic
reads this before deciding what to revise.

`build_corpus_profiles` builds the corpus side from **three** functions:
`{**bar_metrics, **style_fingerprint, **sonority_metrics}`.
`_corpus_divergence_from_path` built the piece side from **two**.
`sonority_metrics` was defined, correct, and called by nothing — it returns
`mean_sonority 3.062, chorded_attack_pct 100.0` on the very bars the report
scored as zero. The comparison loop's `gen.get(name, 0.0)` did the rest.
`corpus_metrics`' own docstring calls `bar_metrics` "the shared yardstick run on
BOTH corpus bars and a generated piece, so the z-scores are apples-to-apples". It
was shared for 37 of the 39.

Fixed twice over: the piece side now merges all three, **and** a metric the piece
cannot be measured on is skipped and reported under `uncomputed_metrics` rather
than scored as zero — because "we did not measure this" and "the piece scores
zero" are different statements, and only one of them is evidence. After:
`chorded_attack_pct` 100.0 (z 0.77), `mean_sonority` 3.062 (z -0.77), and
metrics outside |z|>2 drop from 5 to 3.

The general guard also surfaced a stale `blend__` profile still carrying
`direction_changes_per_bar`, the old name of `melody_direction_change_pct` — the
metric-name collision recorded in [[feedback_contradictory_guidance]], still
sitting in a generated artifact. It now reports as a gap instead of a phantom
z-score.

Suite 2,651 pass, lint clean.

---

## Addendum 105 — composed a motet, and the system faulted its own engraver

Second end-to-end run, this time down the **vocal** path that Addenda 83-88 built
and that had never been exercised by real composition: a 41-bar Dorian motet for
four voices, 4/2, Palestrina's manner, written note by note against the brief.

**Everything the session built for voices worked.** The brief came back with 18
`UPPER:`/`LOWER:` lines and zero `RH:`, carrying the note that the bar-dict keys
stay `rh`/`lh` and mean the upper and lower staff. The score assembled to four
parts named Soprano, Alto, Tenor, Bass — with the Bass genuinely lowest, which is
the inversion Addendum 84 fixed. Final ranges: S 64-81, A 60-77, T 57-72,
B 38-53, every one inside what real singers do.

**And the range check caught ME.** Revising for rhythmic variety I pushed the
alto to G5 and the tenor to D5; the commit was refused:

> error: counter_reply: G5 (MIDI 79) is outside the alto range [45, 77] — no
> singer on that part can reach it

That is the check from Addendum 83 — the one that closed a promise rather than
fixing damage — firing correctly on live composition the first time it was asked
a real question.

**The new defect: the system contradicting itself about period notation.**
The first audit faulted the motet for `dynamic_poverty` (0 dynamics in 41 bars)
and `articulation_absent` (0 articulation marks). Both are correct *descriptions*
and wrong *judgements*: the notation did not exist in the Renaissance, and
`expression_enricher` is **already period-gated not to add either**. The system
was penalising its own engraver for being right. Falsified:

| detector | palestrina | monteverdi | bach | mozart piano |
|---|---|---|---|---|
| `dynamic_poverty` | **100%** | **100%** | 0% | 0% |
| `articulation_absent` | **100%** | 92% | 0% | 0% |
| `tie_absent` | 0% | 0% | 0% | 7% |

Both now gated through `_is_renaissance`, and all four corpora read 0%. Note
`tie_absent` fires on **0%** of real Palestrina — they tie their suspensions — so
that finding against my motet was mine to fix, and the distinction is the whole
point of gating by measurement rather than by intuition.

Revisions across three rounds: realism **6 → 2 → 2**, ties 0 → 10, dominant
note-value share 77%/83% → 64%/73%. The residual is honest: my upper voices are
still more uniform than real Palestrina, whose commonest value covers 42% at the
median. Ear errors 0 throughout.

Two pieces now composed end to end through the fixed pipeline — a nocturne and a
motet, keyboard path and vocal path — each finding defects no code sweep had.
Suite 2,660 pass, lint clean. One failure in `test_notation_fidelity.py`, written
three minutes before the run by the concurrent session and passing in isolation.

---

## Addendum 106 — the quartet's viola was labelled Violoncello

Third end-to-end composition, down the **string-ensemble** path that Addendum 85
built and no real piece had used: the slow movement of a G major quartet, 3/4,
Haydn's manner, 41 bars written note by note.

**Addendum 85's naming worked** — the parts came out Violin I, Violin II, Viola,
Violoncello with the right instruments, where before this piece would have been
scored for violin, clarinet, bassoon and cello. But the ranges gave it away:

```
   Violin I      67-88     ok
   Violin II     64-79     ok
   Viola         40-59  <- below the viola's lowest string (C3 = 48)
   Violoncello   61-73  <- a cello sitting where the viola should be
```

The two lower parts were swapped. **This is Addendum 84's defect, and Addendum
84's fix is what left it.** That fix ordered the lower staff's voices by pitch —
because `bass_foundation` means the lowest voice — but gated it to
`is_vocal(instrumentation)`. Too narrow. A closed score writes the lower staff's
UPPER voice first whatever is playing it: tenor before bass, viola before cello.
The keyboard is the exception, because a piano's pedal note is not reliably below
its own figuration.

Now gated on `not is_keyboard(...)`. Verified across four paths: string quartet,
choir and orchestra all put the low line in the bass part; solo piano keeps
`C2h. // figuration` in written order. Recommitted, and every part now sits
inside its real instrument — Viola 50-73, Violoncello 40-59.

**A second thing this run showed, and it is the good kind.** My first commit was
refused outright:

> `'F#5e'`… `"Fs5e" is not a pitch this system can write (read as "Fs5")` —
> these would have been silently dropped or read as a different pitch

I had written sharps as `Fs`. 109 tokens across nine phrases, caught before a
note reached the page. The hint says exactly what an older version of this system
did with them.

Remaining after the fix: `tie_absent` and `scalar_overuse` (68% of melody bars
are stepwise) — both true of my writing, both the same faults the nocturne
started with, which suggests they are my habits rather than the system's.

**Three pieces now composed end to end** — nocturne (keyboard), motet (vocal),
quartet (strings). Each exercised a path the others did not and each found
something no code sweep had: a fabricated corpus metric, a self-contradicting
period gate, and an incomplete fix of my own. Suite 2,662 pass, lint clean.

---

## Addendum 107 — the bassoon was the bass because its name contains "bass"

Fourth end-to-end composition, down the **orchestral** path: the opening of a C
minor overture, written as a piano core and put through `orchestrate_section` →
`assemble_orchestration` for a ten-part orchestra. Every part came out inside its
instrument's range, so the range clamp works. But the string section was stacked
wrong:

```
   Viola         48-60
   Violoncello   63-74     <- the cello playing entirely above the viola
```

for both sections, the whole movement.

**The chain.** `_style_role_assignments` decides which instrument a style gives
the melody and the bass to. It matched `_BASS_WORDS` — which contains `"bass"` —
against text that included the instrument's **own name**. `"bass" in "bassoon"`
is True, so every ensemble containing a bassoon resolved to
`{"bass": "bassoon"}`. The cello was then left with nothing, and
`plan_orchestration`'s last pass — *"anything still silent doubles the melody,
better a real part than a tacet stave in a score that names it"* — handed the
cello the tune. `bass_clarinet` and `bass_trombone` collide identically.

Every orchestration this system has produced with a bassoon in the ensemble had
its bass line on the bassoon and its cello doubling the melody.

**The fix is not a better word list.** An instrument must never earn a role from
what it is CALLED, only from what the style says it DOES, so the matched text is
now `role.role` and `role.characteristic_usage` and nothing else. For Beethoven
the roles carry no usable description at all — the pack's `role` fields are empty
strings and `characteristic_usage` is the literal heading "Instrument Roles" — so
the assignment is now `{}` and the planner's own preference takes over, which
picks the cello. After: Violin 1 above Violin 2 above Viola above Cello above
Contrabass, in both sections.

A test documents the trap rather than pretending it is gone: `"bass"` really is a
substring of `"bassoon"`, so any future matcher that looks at the instrument name
reintroduces this exactly.

**Diagnosis note.** The planner was correct in isolation — called directly on the
phrase it put the cello at 36-56 — and wrong through `orchestrate_section`, which
is what took this from "the cello sounds odd" to a one-line cause. Four probes
were needed to find that the two paths differed only in `style_roles`.

**Four pieces now composed end to end**: nocturne (keyboard), motet (vocal),
quartet (strings), overture (orchestral). Each found a defect the other paths did
not. Suite 2,679 pass, lint clean.

---

## Addendum 108 — planning a movement twice made every brief count wrong

Fifth end-to-end composition, down the **multi-movement** path: a two-movement
sonatina in A minor, planned through `init_work` → `plan_movement` →
`build_form_graph`. Three defects on the entry path, all the same shape — a tool
quietly accepting or doing something other than what the caller meant.

**1. The mode was accepted as the movement count.** `init_work(piece_id,
movement_count)` declares `movement_count: int` and checked nothing. Called the
way every neighbouring tool is called — `init_work(pid, "compose_from_text")`,
with the MODE second, which is exactly what `init_workspace` takes — it stored
the string as the count and reported it back: `"movement_count":
"compose_from_text"`. Now refused, with a message that names the piece and points
at the argument that was actually wanted.

**2. `plan_movement` builds no phrases and did not say so.** It takes `form`,
`key`, `tempo_bpm` and `meter` — every argument `build_form_graph` needs — and
creates nothing. I stopped there and had a work with two planned movements and
zero phrases. The return now carries `phrases_created: 0` and the exact
`build_form_graph(...)` call that follows. Same precedent as the
`init_work(description=...)` notice already in that file.

**3. Replanning a movement duplicated it.** `plan_movement` appended. Revising a
movement — or simply correcting a call and rerunning it, which is what happened —
left `movements = ['m1', 'm2', 'm1']`, and since the brief's movement line counts
the length of that list, **every brief in the piece opened "MOVEMENT 1 of 3" for
a two-movement work**. It now replaces by id, and heals a list an earlier run
already duplicated — keeping each id's first position (score order) and its last
contract — because stopping new duplicates leaves every existing work still
counting wrong.

After: `['m1', 'm2']`, "MOVEMENT 1 of 2" and "MOVEMENT 2 of 2", each carrying its
role, character and the home-key distance the session's movement work put there.

**A regression I caused and the suite caught.** My first validation returned
before the piece was resolved, so `init_work`'s failure stopped naming the piece
— breaking `test_tool_failure_is_legible`, a contract that every tool's failure
must say which piece it is about. Fixed by putting the id in the message, which
it should have had anyway.

**Five pieces now composed end to end** — nocturne (keyboard), motet (vocal),
quartet (strings), overture (orchestral), sonatina (multi-movement). Every path
the system offers has now been driven by real composition, and each one found
something no code sweep had.

Suite 2,693 pass. One failure in
`test_phrase_bound_detectors_calibration.py`, created by the concurrent session
at 07:47:09 — during the run.

---

## Addendum 109 — a Bach invention with five dynamics Bach never wrote

Sixth end-to-end composition: a two-part invention in D minor, the one texture
none of the previous five had — two fully independent voices, no accompaniment,
strict counterpoint. It came out clean on the first pass (0 ear errors, 1 realism
finding) and the part-writing report gave real counterpoint data: independence
0.712, 7 voice crossings, 2 hidden fifths.

The realism finding was mine and correct: one note above **D6**, the top of
Bach's own keyboard. Fixed.

**The defect was in the census.** The piece reported 5 dynamics in 22 bars, and I
had written none — the engraver added them. Measured over the corpus this system
learns Baroque from:

```
real bach (20 scores)     median 0.000 dynamics/bar   max 0.000   zero on 20/20
real corelli (1)          0.000                                   zero on  1/1
real handel  (1)          0.278                    <- the only counter-example
real mozart piano (14)    0.873
real chopin (14)          0.472
```

`ENGRAVING_STYLES["baroque"]` carried `dynamic_every_n_bars=8` with **no
justification beside it**, while the `renaissance` entry two lines above says
plainly "dynamics are not notated" and sets 99. Now 99 for both, with the
measurement and the Handel exception recorded in place: Baroque *orchestral*
music does mark echo effects, and if that repertoire is armed this wants
re-measuring rather than inheriting.

After: the invention carries **0 dynamics**, exactly matching real Bach's
0.000/bar, with 21 slurs and 1.05 marks per bar. 0 ear errors, 0 realism
findings.

**Two corrections to my own work, both caught immediately.** My first test
asserted the Baroque engraver adds *no* dynamic at all — too strict, because
`add_echo_terracing` may still mark one echo, and a literal repeat taken a step
softer is the defining Baroque device and genuinely notated. The rule that was
wrong was the periodic one, not the echo. And the change broke
`test_flat_dynamics_does_not_scold_a_period_that_does_not_notate_dynamics`, whose
docstring states the principle this session keeps returning to — *"two subsystems
disagreeing inside one context window is a defect in its own right; they read the
same table now"*. They still do; the table changed, so the test's expectation
had to move with it ([[feedback_contradictory_guidance]]).

**Six pieces now composed end to end.** Suite 2,703 pass, lint clean.

---

## Addendum 110 — a round that confirmed rather than found

Seventh end-to-end composition: a G major rondo finale, chosen to stress three
things none of the previous six used — dense ornamentation, an anacrusis, and a
change of gait in the coda. **It found no code defect.** Recorded anyway, because
a session that only reports discoveries is not reporting honestly, and because
three paths were verified end to end for the first time.

**Ornaments reach the page.** 5 turns, 9 trills, 2 mordents, 1 fermata and 7
grace notes engraved from the shorthand's `:turn` `:tr` `:mord` `:appo` `:grace`.

**Ornaments reach the EAR**, which is the claim that matters, since the preview
is what the `music-critic` judges:

```
rondo     (17 ornaments)   score 401 sounding notes -> MIDI 443   (+42)
invention  (0 ornaments)   score 359                 -> MIDI 362   (+3)
```

A trill that is audible produces more notes than are written; one that is not
produces the same. `ornament_realization` does its job.

**The anacrusis works.** The first measure is 0.5 quarter-lengths against the
bar's 2.0 — a real pickup, not a short bar the meter check had to forgive.

**Two commit refusals, both mine, both legible.** I wrote a fifth bar dict for a
four-bar phrase with a pickup, and got: *"A pickup bar OCCUPIES the phrase's
first bar — mark that first dict {'pickup': True} and write only the upbeat in
it; do not add an extra dict."* And a 3-beat bar in 2/4, named to the beat. Both
say exactly what to do.

**A probe error avoided.** Comparing score to MIDI bar by bar showed bar 4 losing
notes (11 engraved, 7 sounding), which reads as the renderer dropping music. It
is the pickup shifting bar numbers between the two files. Comparing totals — the
measurement that does not depend on alignment — showed the opposite. That is the
same mistake as the earlier `<ff />` regex and the `Fs5` spelling: the surprising
reading was the measurement's fault, not the code's.

The seven realism findings are all true of my writing, not the system's:
accompaniment monoculture at 70% (one alberti figure throughout), no ties again,
a melody of 11 distinct bar-shapes against Mozart's floor of 20, 69% scale runs,
and one note above **F6** — the top of Mozart's own fortepiano. That last is the
detector doing precisely what it is for.

Seven pieces now composed end to end.

---

## Addendum 111 — a 16-bar corpus called itself "armed"

Two defects, both found by sweeping data rather than code, and both the same
shape: **two functions in this repo answering the same question differently.**

**1. `resolve_reference` called a 16-bar corpus armed.** CLAUDE.md states the
rule — "a composer needs ≥3 distinct source movements and real harmonic coverage
to count as armed; `composer_coverage_tier` reports tier C for anything thinner
rather than pretending it can teach a voice." `composer_coverage_tier` applies
it. `resolve_reference` — the function that decides whether a request can be
honoured — did not; its `armed` meant only "has a corpus directory on disk":

```
composer_coverage_tier("bartok")  ->  tier C, armed False, 16 bars, 1 source
resolve_reference("bartok")       ->  armed True,  no tier at all
```

Same for bruckner (27 bars) and dvorak (46). So "compose in Bartok's style" was
answered as though the corpus could teach that voice. `style_members`, two
functions further up in the same file, already consults the tier — only the
direct-composer path, which is the commoner request, did not. It now reports the
tier and the bar count and points at `acquire_composer`; mozart, chopin,
palestrina and bach are unaffected, and style requests, which were already
honest, are unchanged.

**2. The engine's own entry point raised tracebacks.** `_load_graph` reports a
missing piece by raising `_MissingPiece`, and its docstring explains the design:
"Raised rather than returned so `_load_graph` can be a one-line call at the top
of a tool without every caller needing a two-value unpack." That holds only if
the tool carries `@_tool`. Parsing every public function in `scales.py` that
takes a `piece_id`: **`run_scales_section` was the only one without it** — so a
mistyped piece id came back as a `FileNotFoundError` traceback with a path in it,
while all thirty-odd neighbours returned `{"error": "No workspace for '<id>'",
"hint": ...}`. One decorator. A test now parses the file and asserts the set is
empty, because `functools.wraps` makes a decorated function indistinguishable
from an undecorated one at runtime — asking the object cannot answer this.

**Also checked and clean:** no composer index contains another composer's
material (0 of 22 — this repo has had a phrase catalog that was 59% Mozart inside
Beethoven's index), and of 33 corpus bar fields, 5 are read by nothing
(`chord_root`, `chord_quality`, `chord_root_interval`, `melody_part_index`,
`melody_register`) — all superseded by richer fields rather than broken.

**A truncation error of mine**, and the same one my notes already record: `tail
-24` on an alphabetical listing hid `bach` and `beethoven`, and for a minute it
looked as though the two flagship corpora had no source provenance. They have 470
and 99 sources respectively.

Suite 2,732 pass, lint clean.

---

## Addendum 112 — the "arm it" hint named a composer who does not exist

Continued the data sweep. Most of it came back clean, which is worth recording:

- **Every corpus profile matches its corpus exactly** — 22 composers, bar counts
  identical to the indexes on disk, 0 disagreeing by even 2%. Stale profiles
  would put every z-score against outdated numbers.
- **27 transition matrices, no empty ones, and no dead texture labels** — every
  label in every matrix is one the corpus still produces. This is the shape that
  produced `passage_work`, a label readers were fixed for and the generator was
  not.
- **20 composers have compiled doctrine but no corpus** (mahler, ravel, wagner,
  stravinsky, glass, williams…). They resolve `kind=unknown, armed=False`, name
  their closest armed style, and are never silently substituted. Honest.

**The defect was in that last message.** It ended:

> Arm it with `acquire_composer.py {base}`

where `base` is `low.split("-")[0]` — a helper that exists to match
"mozart-k331" back to "mozart". Used here it handed the user a command that
cannot work for any hyphenated composer:

```
vaughan-williams  ->  acquire_composer.py vaughan
saint-saens       ->  acquire_composer.py saint
arvo-part         ->  acquire_composer.py arvo
strauss-r         ->  acquire_composer.py strauss
```

Hyphenated composers are not a corner case. The hint now passes through the name
the user actually asked for, and uses the module form CLAUDE.md documents
(`python -m scripts.acquire_composer <name>`) rather than a script path that
depends on the working directory. `acquire_composer` splits its argument on
whitespace and underscores but not hyphens, so the full name reaches its resolver
intact — whether that resolver then finds "arvo-part" upstream is its own
question, and a hint that names what was asked for is right either way.

**Documentation propagated** for three of this session's changes that CLAUDE.md
still described in their old form: the engraver's period gate ("no dynamics for
Palestrina" → for Bach too, with the 20/20 measurement), the brief speaking in
the piece's own forces (`RH:`/`LH:` for a keyboard, `UPPER:`/`LOWER:` otherwise),
and the assembler scoring each piece for what it is.

Suite 2,738 pass, lint clean.

---

## Addendum 113 — composing "in a style" ran on the sparse-corpus path

Composed in a **style** rather than as a composer — the one path real
composition had never driven, and the system's headline capability ("compose in a
style, not as one composer"). `compile_style(piece, "classical")` reported:

```
composer_id=classical  tier=D  fingerprints=0  lh_textures=0  donor_plan=True
```

against `compile_style(piece, "mozart")` at tier A with 10 left-hand textures.
**Tier C/D is what triggers `DonorStrategy`**, so the classical style — mozart,
haydn and beethoven together, 27,801 bars, the richest corpus this system has —
was augmented with a donor as though its corpus were thin.

**Three causes, and a fourth I created.**

1. *`pack_dir_name("classical")` returned `"classical"`.* Style packs are written
   `style__<name>` and `resolve_reference` returns that id, but `compile_style`
   threads the user's own word through — so `_load_pack` looked for
   `compiled_packs/classical/`, found nothing, and every field took its default,
   including `support_tier` "D". A bare style name now redirects to its pack,
   but only when no pack of that name exists, so a composer sharing a style word
   keeps his own.

2. *`_pass_manifest` classified the tier from `reference_index/<id>/`* and there
   is no `reference_index/style__classical/`. A style's corpus is the union of
   its members': classical 27,801 bars, renaissance 64,562. It now aggregates
   them, for the bare word as well as the `style__` id — checking only
   `is_style_id` left the commoner case still computing zero.

3. *The tier is now read at LOAD time*, because nothing can regenerate a style
   manifest: `build_style_profiles` writes only the corpus profile, and the
   compiler destroys the pack (below). `resolve_program` takes the best tier
   among the style's members.

4. **The one I caused.** Running `compile_style` on a style *destroys its pack*.
   The compiler builds from `.claude/context/<genre>/composer-profiles/<name>/`;
   a style has no such directory, so every pass writes EMPTY over the aggregate.
   I did this to all four style packs — `style__classical` lost its instruments,
   textures and worked prototypes — and
   `test_style_packs_carry_doctrine` caught it with 15 failures. Restored the 54
   files from git, leaving the corpus profiles (which were not mine to revert)
   untouched and verified still matching their members exactly. `compile_style`
   now skips compilation for style references, and a test rewrites nothing.

After: all four styles resolve tier **A** with 7-11 left-hand textures, real
cadence scripts, and `donor_plan: False`.

Suite 2,767 pass, lint clean, and the only modified pack file is one
(`chopin/scoped_statistics.json`) that was modified before this session began.

---

## Addendum 114 — a style was scored on a third of the dimensions its members are

Composed the classical-style piece through the path Addendum 113 repaired. It
came out clean — **0 ear errors, 0 ear warnings, 1 realism finding** (my own
scale habit) — and the corpus comparison then showed the next defect.

**A style profile carried 13 metrics; a composer profile carries 39.**
`build_corpus_profiles` merges three sources for a composer —
`{**bar_metrics, **style_fingerprint, **sonority_metrics}` — and
`build_style_profiles` aggregated `SCALAR_METRICS` alone. The 26 missing are the
whole harmony/melody/rhythm-value fingerprint plus sonority:

```
avg_chord_size  chord_pct  chorded_attack_pct  chromatic_ratio  dim_aug_chord_ratio
dotted_eighth_ratio  dur_variety  eighth_ratio  harmonic_rhythm  leap_ratio
maj_chord_ratio  mean_abs_interval  mean_sonority  step_ratio  ...
```

`compare_to_corpus` scores a piece on whatever the profile carries, so a piece
written "in the classical style" was judged on texture and rhythm only — and the
missing two thirds are exactly the dimensions that separate one classical
composer from another. This is Addendum 104's defect one level up: there the
PIECE side missed a source the corpus side had; here the STYLE side misses two
the composer side has.

Fixed and rebuilt: all four style profiles now carry 39 metrics, and the rebuild
also produced profiles for late-romantic, impressionist and nationalistic. The
piece re-scored **34 of 39 inside |z|≤2**, and the four flags it raises are fair
criticism of what I wrote: too stepwise, too many eighths, not chromatic enough
for the style.

**A guard I nearly added twice.** `maj_chord_ratio` came back 1.0 at z=+17.42 —
the largest deviation in the report — and the cause is a denominator of **one**:
the piece has a single chord event in 221. I was about to add a small-sample
guard when checking showed the metric already reads `status: "unreliable"` and is
already excluded from the flags: `_Z_DEGENERATE = 8.0` catches it, and the
comment beside it describes this exact failure ("a two-part invention reported
`min_chord_ratio z = +142.8` — it has exactly two chord events in 18 bars").
Verifying first is what kept a second, redundant mechanism out of the file.

Suite 2,769 pass, lint clean.

---

## Addendum 115 — "your chords are too big", from two chords

Ninth end-to-end composition, and the second in a **style**: a keyboard piece in
the baroque style — Bach, Handel and Vivaldi's shared language, a walking bass
under a spun-out treble.

**Three of this session's fixes confirmed on a path they were not written for.**
The piece carries **0 dynamics** — Addendum 109's Baroque gate, working through
the style aggregation rather than a named composer. It compiled at tier A with
`donor_plan: False` (Addendum 113). And it was scored on 39 metrics, not 13
(Addendum 114). Final state: **0 ear errors, 0 realism findings**; the one
finding in the first pass was mine, an Eb6 above the baroque keyboard's D6.

**The new defect.** Five profiled metrics divide by the piece's CHORD count —
`avg_chord_size`, `maj_chord_ratio`, `min_chord_ratio`, `dim_aug_chord_ratio`,
`seventh_chord_ratio`. This piece has **2 chord events in 388 notes**, and
reported:

```
avg_chord_size   value 3.0   z +3.48   status "high"
```

which reached the flags the critic reads: *your chords are too big* — from two
chords. `_Z_DEGENERATE = 8.0` catches only the extremes; at z=3.48 nothing did.
A mostly single-line texture — a Baroque keyboard piece, an invention, a fugue —
is a texture, not a fault.

Those five are now reported but not scored below 8 chord events, marked
`unreliable` the same way a degenerate corpus stat is, with a note naming the
actual count. `chord_pct` is deliberately NOT guarded: its denominator is the
bar count, which a single-line piece has plenty of, and guarding it would hide a
real finding. Neither is `mean_sonority`, which is computed over every attack —
its z of -2.92 on this piece is a true observation.

Verified on the two pieces that bracket the case: the baroque piece's
`avg_chord_size` is now `unreliable` and out of the flags; the chord-rich
nocturne's is `ok` at z=+0.96 and untouched.

Nine pieces now composed end to end. Suite 2,783 pass, lint clean.

---

## Addendum 116 — the one thing that is consistently wrong is not the system

Tenth end-to-end composition, third in a **style**: a B minor character piece in
the romantic style, over the largest aggregation (seven members). It found no new
code defect. Two rounds took it from 5 ear warnings + 2 realism findings to
**0 / 0 / 1**, and both fixes were compositional:

- a **false relation** — a natural-minor melodic descent (A♮5) over the
  dominant's A♯, in two places. The ear caught it and was right.
- **register stasis** at 22 semitones, fixed by opening the climax to B6 and
  dropping the retransition into the tenor.

The residual finding is `scalar_overuse`, and it is the same finding on five of
the ten pieces. So I measured it properly across everything I composed this
session:

```
step_ratio, my pieces          median 0.770   (n=10, range 0.320-0.899)

real corpora (profile means)
   beethoven 0.427   haydn 0.461   chopin 0.460   mozart 0.526
   palestrina 0.645  bach 0.678
```

My melodies are consistently **1.5-2.5 standard deviations more stepwise than
real music**, and only Bach and Palestrina — the two most conjunct repertoires in
the corpus — come anywhere near where I write by default.

**And the brief already says so, in numbers, in the section it is most emphatic
about:**

> DON'T WALK SCALES. Plain unbroken stepwise runs are 0-15% of melody bars in
> real movements (median 2%).
> The line LEAPS — only 53% of intervals are stepwise and 29% span a fifth or
> more.

So the guidance is present, specific, measured, and correct, and the composer
read it and wrote 77% steps anyway. That is worth recording as plainly as any
defect: after 116 addenda, **the most consistent measurable difference between
this system's output and real music is one the system already names and the
composer fails to act on.** It is not a missing check, a stale constant or a
broken lookup — the classes that filled this ledger. It is the writing.

Nine of ten pieces reach 0 ear errors and 0-1 realism findings. The tooling is
doing its job; the remaining distance is in the notes.

---

## Addendum 117 — the gate told every composer to write scales

Addendum 116 measured the one consistent difference between this system's output
and real music: across ten pieces, median `step_ratio` **0.770** against real
music's 0.427-0.678, with `scalar_overuse` firing on five of them. It concluded
the brief already says not to, and the failure was the writing.

That was half the story. There IS a check positioned to catch it while the notes
are being written — `commit_gate._check_interval_profile`, which runs on every
commit — and it was scoring every phrase against a hardcoded

```python
{"stepwise": 0.65, "small_leap": 0.25, "large_leap": 0.10}
```

Measured over the corpus **in those same bands**, that describes nobody:

```
palestrina 0.813   bach 0.736   mozart 0.611   haydn 0.600
beethoven  0.538   chopin 0.498   liszt 0.358
```

It is nearly twice Liszt's real rate, and its large-leap figure of 0.10 is off by
almost four times for him (0.377). So three subsystems were giving three answers:
the **gate** said aim for 65% steps, `score_realism` told the finished piece it
was too scalar, and the **brief** told the composer the line should leap. The one
of the three that could object while the phrase was being written was the one
holding the constant.

`composer_interval_priors` now measures each composer's own distribution from the
corpus, cached, and returns None when it cannot — in which case the generic prior
stands, which is the honest fallback rather than a silently wrong composer. A
wholly stepwise line now scores:

```
palestrina 0.814 passes    bach 0.736 passes    mozart 0.611 passes
beethoven  0.538 passes    chopin 0.498 WARNS   liszt 0.358 WARNS
generic prior: 0.650 passes   <- what every composer used to get
```

Stepwise motion is Palestrina's idiom and warning about it would be wrong; it is
not Chopin's, and now the gate says so at the moment it can still be acted on.

This is the third time this session that a constant sitting next to real
measured data turned out to describe no real music — after the brief's fallback
bands (Addendum 103) and the Baroque dynamics interval (109). The shape is
always the same: a plausible number written once, never falsified, and quietly
contradicting the corpus in the same repository.

Suite 2,793 pass, lint clean. One failure in `test_melody_takes_weight.py`,
created by the concurrent session at 09:27:49 and passing in isolation.

---

## Addendum 118 — sweeping for the "unfalsified constant" class

Three times this session a hardcoded number turned out to describe no real music
— the brief's fallback bands (103), the Baroque dynamics interval (109), the
commit gate's interval prior (117). Rather than keep finding that shape by
accident, I swept for it: every `str -> float` table in `tools/scales` whose
values sit in [0,1], which is what a musical prior or distribution looks like.

**21 candidates, and the sweep came back clean.** Most are policy weights, not
claims about music — `CandidateScores._MODE_WEIGHTS` (six mode-specific scoring
vectors, each summing to 1), tier budgets, lock strengths, retrieval weights.
Those cannot be falsified against a corpus because they are not assertions about
one.

The one table that IS a set of corpus claims — `review_style_gate`'s target
distributions — turns out to be **already falsified, and says so inline**:

```python
"rest_ratio":     {"mean": 15.8, "stdev": 6.6},   # real 4.3-28.9
"triplet_pct":    {"mean": 16.2, "stdev": 29.0},  # real 0-74.1
"stepwise_pct":   {"mean": 59.6, "stdev": 12.0},  # real 35.5-76.4
"density_cv":     {"mean": 0.37, "stdev": 0.30},  # real 0.22-0.54 (+1 at 6.2)
```

each with its measured range beside it, and a comment explaining that every stdev
was widened until the real minimum and maximum both sit inside two of them. One
entry even documents an outlier movement at 6.2 and explains why the centre was
taken from the other nineteen.

So the class is not pervasive: the three I found were outliers in a file base
that mostly does record its provenance. That is worth stating as plainly as a
defect would be — a sweep that finds nothing is evidence too, and it is the
reason to stop looking here rather than keep turning over the same stones.

**Session method, recorded in memory** as `project-compose-to-find-defects`:
after roughly ninety addenda the code and data sweeps had decayed to hint-text
bugs, and composing pieces through the real tools restored the find rate
immediately — ten pieces, ten paths, one substantive defect each. They were
invisible to inspection because every module was internally consistent and
consistent with its own tests. The defects live at the **seams**: where two
subsystems answer the same question differently, or where a constant contradicts
corpus data sitting in the same repository.

---

## Addendum 119 — a bassoon doubling the soprano melody

Eleventh end-to-end composition, down the **concerto** path — the soloist
machinery (`orchestrate_section(soloist=...)`) that nothing had exercised. It
works: twelve parts, the solo piano kept entire on two staves, every part inside
its instrument, and the strings correctly stacked after Addendum 107
(Vln1 65-88 > Vln2 60-65 > Vla 50-59 > Vc 40-57 > Cb 28-45).

Then the note counts gave it away — Flute, Oboe, Clarinet, Bassoon and Violin 1
all had **exactly 54**, the same as the soloist:

```
Flute     97% the same pitch classes as the solo line
Oboe      97%
Clarinet 100%
Bassoon   95%      <- doubling a soprano melody
Violin 1 100%
```

five instruments in unison on the tune, while Violin 2 had 4 notes and the Cello
8 across eight bars.

`plan_orchestration`'s last pass gives any still-silent instrument a part —
*"better a real part than a tacet stave in a score that names it"* — and it gave
every one of them the MELODY. In a concerto tutti, where the piano core is
octaves over a bass with little inner material, almost everything falls through
to that pass. The intent is right and the choice was not: a bassoon doubling a
soprano melody is not a thin part, it is a wrong one.

The pass is now register-aware. An instrument whose practical centre sits more
than a fifth below the melody's own centre of gravity doubles the **bass**
instead — which is exactly what the pass above it already does for the viola and
calls "the oldest filler in the orchestra". After: clarinet and bassoon take the
bass line; flute, oboe and violin 1 still double the tune, which is idiomatic for
a tutti and must not be silenced. Nothing is left tacet, and every part stays in
range.

**Noted, not fixed:** the solo part is emitted as two separate parts, the second
named **"Piano Lh"**. A real concerto score names the soloist once and gives it
two staves. Fixing it properly needs music21 `PartStaff` grouping rather than a
renamed second part, which is a larger change than this session should start.

Eleven pieces now composed end to end. Suite 2,804 pass, lint clean.

---

## Addendum 120 — "Piano" and "Piano Lh", as if two players

Addendum 119 noted this and deferred it. It is smaller than it looked.

A concerto soloist is emitted as **two parts** for a real reason — the ensemble
path gives each part one staff, and a soloist crammed onto one had its hands
overlapping in time with 42 events trimmed by the repair pass. But the lower part
was then named from its staff id, so the score listed:

```
Piano   Piano Lh   Flute   Oboe   Clarinet   ...
```

as if two players sat at two pianos. An engraved concerto names its soloist
**once**, at the top of a brace.

The lower stave of a pair now takes no name of its own and the two are joined by
a `StaffGroup` with `symbol="brace"`, so a reader sees one instrument on two
staves. The pairing is detected structurally — a staff id ending `_lh` whose base
is also present — rather than by looking for the word "piano", so it holds for
any soloist.

**A collision with the concurrent session, resolved by keeping their claim.**
`test_concerto_soloist.py` (written at 00:58 by the other session) looks the
lower staff up by `partName == "piano_lh"` and asserts *"the left hand must sound
below the right"*. My rename broke the lookup, not the claim. The test now takes
the two parts named "Piano" in score order — upper first, which is what the brace
records — and asserts exactly what it asserted before. The assertion is
untouched; only the way it finds the staves changed, because the thing it was
finding them by was the defect.

That is the second time this session that another session's test caught
something of mine (the first was `test_style_packs_carry_doctrine`, which caught
me destroying four style packs). Both times the right move was to keep the test's
intent and fix what it was pointing at.

Eleven pieces composed end to end. Suite 2,805 pass, lint clean.

## Addendum 121 — singers named by voice type became a solo piano piece

**Found by** probing the art-song path (voice + piano), a mixed force no
composition in this session had exercised.

`_infer_instrumentation` knew four singer words — `voice`, `voices`, `choir`,
`satb` — and nothing else. So it read *"a sacred motet for four voices"*
correctly and read this as a keyboard work:

| description | before | after |
|---|---|---|
| a sacred piece for soprano, alto, tenor and bass | `solo_piano` | `choir` |
| an art song for soprano and piano | `solo_piano` | `choir` |
| a duet for soprano and alto | `solo_piano` | `choir` |
| a lament for solo contralto and organ | `solo_piano` | `choir` |
| a song for mezzo-soprano and harpsichord | `solo_piano` | `choir` |
| a bass aria with continuo | `solo_piano` | `choir` |
| an aria for tenor and strings | `solo_piano` | `choir` |
| a psalm setting for countertenor and baritone | `solo_piano` | `choir` |

**All eight** returned `None`, which falls through to the `solo_piano` default.
Verified end-to-end through `init_workspace`: the four singers received
`is_keyboard=True`, `_physical_constraints(...).keyboard=True` — the pianist's
hand-span limit applied to Tenor and Bassus as one hand — and no vocal range
check at all. That is precisely the motet failure `_infer_instrumentation`'s own
docstring records as fixed, reappearing whenever the singers are named by voice
type rather than by the word "voices".

**The naive repair is worse than the defect**, which is why the fix is
position-aware rather than a longer word list. Voice types are shared with
instruments — *bass* clarinet, *alto* saxophone, *tenor* trombone, *double
bass*, *soprano* recorder — and three of them (`tenor`, `cantus`, `bass`) also
name a register in keyboard writing. Adding the bare words turns "a duo for
alto saxophone and piano" into a choir.

So: a scan that reads each voice-type word **in context**, discarding any
followed by an instrument or a texture position (`clarinet`, `line`, `register`,
`entry`) or preceded by a qualifier (`double`, `figured`, `walking`). What
survives means singers when the word names a person and nothing else
(`soprano`, `contralto`, `mezzo`, `baritone`, `countertenor`), when the request
names solo-song repertoire, or when no instrument is competing for the name.
A lone register word beside a named keyboard stays undecided.

My first version failed its own falsification 2/22: a "two distinct types" rule
turned *"a chorale prelude for organ with the cantus in the tenor"* into a
choir — the over-correction the docstring warns about — and left *"solo
contralto and organ"* undecided. Splitting the register-ambiguous words out
fixed both. Final: **27/27 correct across both directions.**

`tools/scales/tests/test_singers_named_by_voice_type.py` (22 cases) pins both
halves, because only pinning the singers invites exactly the regression the
first attempt made. Suite 2832 passed, lint clean.

## Addendum 122 — five of the six composition modes were decorative

**Found by** noticing that all eleven pieces composed while hunting these
defects used `compose_from_text`. The other five modes had never been run.

`variation`, `style_transfer`, `continue_piece`, `orchestrate` and
`reduce_to_piano` are each defined by what they PRESERVE from a source score.
Planning one with no source loaded:

```
variation        -> planned 10 slots   source=''   locks={}
style_transfer   -> planned 10 slots   source=''   locks={}
reduce_to_piano  -> planned 10 slots   source=''   locks={}
continue_piece   -> planned 10 slots   source=''   locks={}
```

`contract.locks` **entirely unset** — so the piece composed an original work,
called it a variation, and the lock policy that is the mode's whole definition
never applied. `_MODE_LOCKS` is real and correct; it is applied *inside*
`load_source_score`, so skipping that step skips the mode.

Passing `source_path` to `init_workspace` does not help. It records a path on
`contract.source` — a field written in two places and **read nowhere** — and a
path is not a score.

The documentation already knew. `.claude/skills/wolfgang/SKILL.md` says of
`load_source_score`: *"Without it the mode has no material: the path alone is
not the music."* Nothing enforced it, so an agent that skipped the step got a
complete, plausible, entirely wrong piece with no indication anything was
missing — the failure mode recorded in [[feedback_a_missed_lookup_is_silent]].

**Fix.** `_require_source_loaded`, called from `build_form_graph` — planning is
the first step that commits to a form, and for these modes the form is supposed
to come from the source. It checks for phrases actually carrying
`salience='source'` (the evidence `load_source_score` leaves), not for the
recorded path. Refusal names the piece, the mode, the locks that would have
applied, and the exact next call. Added `_ToolRefusal`, a sibling of
`_MissingPiece` carrying the guard's own message, so `_tool` returns it as a
normal error result.

Verified in **both** directions: all five modes now refuse legibly,
`compose_from_text` still plans, and a `variation` with a source properly
loaded plans 7 slots with all five locks intact — the guard must not block the
real flow, which is the half a one-sided fix would have broken.

`tools/scales/tests/test_source_modes_need_their_source.py` (7 cases). Suite
2839 passed, lint clean.

## Addendum 123 — the source score was engraved on top of the piece

**Found by** running `reduce_to_piano` end to end for the first time (a real
41-bar string quartet → piano) and reading the exported file back.

`load_source_score` reads a source in as phrases marked `salience='source'` so
the composer can see what must survive. `_collect_events` had **no salience
filter**, so it engraved them as if they were the piece:

```
graph:  11 source phrases (608 events, bars 1-41)   salience='source'
      +  1 reduction      (312 events, bars 1-41)   salience='normal'
export: 40 of 41 right-hand bars hold 6.0 beats in a 3/4 bar
```

Bar 1 of the right hand should hold five chords totalling 3.0 beats. It held
ten totalling 6.0 — every bar of the source printed over every bar of the
reduction, on the same two staves.

**The LayerIR was correct throughout** (41 bars, not one over 3.0 beats), so no
gate, validator or ear check could possibly have seen it. It existed only in
the exported file — the lesson recorded in `project_assembler_voice_bug`, and
the second time this session that reading the score back caught what every
in-memory check passed.

All five source-based modes were affected: variation, style_transfer,
continue_piece, orchestrate, reduce_to_piano — i.e. the entire class of modes
addendum 122 had just made reachable.

**Fix.** `_is_source()` plus an `include_source=False` parameter on `assemble`,
applied to both `_collect_events` and the `bar_meta` loop so per-bar meter
stays consistent with what was actually collected. Assembling a graph that
holds *only* source phrases now says so rather than reporting "No realized
phrases found", which would have been a lie about eleven of them.

Verified by reproducing the original failure: 42/82 mismatched bars → **0**,
and exported bar 1 now matches the LayerIR chord for chord. The measurement was
first validated against two known-good pieces (the nocturne and the quartet
source both scored 0), per
[[feedback_verify_the_measurement_reproduces_a_known_result]].

*Two false trails on the way, both killed by measuring.* I first reported the
reduction had "zero chords in either hand" and was a two-line skeleton — my
probe counted events per attack point while a chord is stored as one event with
a **list** pitch; the RH is in fact 155 chord-events of 175, and SABRE packs the
inner voices correctly. I then found `pitch_to_midi` returns `None` for a tuple
of pitches while handling lists; nothing in the codebase produces a tuple pitch
(every site checks `isinstance(..., list)`), so it is theoretical and was not
"fixed". Also confirmed harmless: `parts=['Piano','Piano']` is how the grand
staff is represented here — the known-good nocturne exports identically.

`tools/scales/tests/test_source_is_not_engraved.py` (4 cases). Suite 2847
passed, lint clean.

## Addendum 124 — the critic was listening to the source too

**Found by** asking what *else* reads `piece_graph.phrases` after addendum 123
fixed `_collect_events`. Four passes did, each with its own loop.

**(a) The MIDI preview played the source over the piece.** `render_midi`
filtered on scope and `realized` and had no salience filter, so a variation's
preview sounded G4-A4-B4 (the source) and C5-D5-E5 (the piece) in the same bar:

```
before:  heard ['A4','B4','C3','C5','D5','E5','G4']
after:   heard ['C3','C5','D5','E5']
```

This is the worst place for it. The preview is what the `music-critic` hears,
and the critic is documented as *the sole driver of artistic revision* — so
every artistic judgement on a source-based piece was made about music that was
half something else. The comment directly above the loop already made the
argument for scope: *"The preview is what the critic HEARS, so a wrong scope
here means an artistic judgement made about the wrong music."* The same
sentence applies word for word to the source, and nothing had drawn the line.

`_section_barlines` and `_movement_bounds` had the same hole — double barlines
and movement headings computed from the source's own `m1_source` span.

**(b) A second, unrelated defect found on the way.**
`_apply_performance_marks` carried its **own private scope matcher**:

```python
if scope.startswith("section-"):
    if not ps.slot or ps.slot.section_id != scope.replace("section-", ""):
        continue
if ps.realized:
    phrases.append(ps)          # <- everything else falls through
```

So assembling `movement-1` of a multi-movement work took its rit. / a tempo /
con pedale marks from **all** movements, and a bare section id — which is what
`self_evaluate` passes — did the same. This is precisely the defect already
recorded against the MIDI renderer's private copy of the same logic, which was
fixed by sharing `_in_scope`; this second copy was missed. It is
[[project_one_parser_one_loader]] to the letter, and `_in_scope` is now the only
scope matcher in the file.

Verified: assembling `movement-1` of a two-movement graph yields exactly its two
bars with no marks drawn from movement 2, and `include_source=True` still
previews the source for anyone who wants it.

**Checked and found sound on the way** (no change made): `orchestrate` run end
to end on a real 14-bar piano section into a 10-instrument ensemble — 0
out-of-range notes, 0 mis-metered bars across 140 measures, and Clarinet /
Horn / Double Bass carrying correct MusicXML transpositions (M-2, P-5, P-8).
The double bass playing only 3 of 14 bars is `loudness < 4` — the documented
"contrabass doubles 8vb at mf+" rule doing its job in a quiet nocturne, not a
defect.

`tools/scales/tests/test_preview_hears_only_the_piece.py` (3 cases). Suite 2850
passed, lint clean.
