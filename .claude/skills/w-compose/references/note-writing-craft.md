# Note-Writing Craft — for the agent that authors every pitch

A router and distillation, not a textbook. Each section gives the
load-bearing rule and points into `.claude/context/general/` for depth.
Artistic guidance here is guidance — "typically", "consider" — only
physical constraints (ranges, spans, meter) are strict.

This file is the single source of truth for the shorthand grammar (§8),
the gate loop (§9), the adapt toolkit (§7), and the canonical tool-call
snippets (§10). Skills and agents point here instead of restating.

## §1 Study first, then compose freely

**Read the brief before you write a note — then write what the music needs.**
Those are two rules, and they used to be one contradictory one ("never write
notes you have not earned from the brief", followed a paragraph later by
"invent freely"). Here is the actual policy:

- **Studying is required.** `get_composition_brief(piece_id, phrase_id)` before
  composing, and read the exemplar bars as music. This is enforced: a commit
  without a brief receipt is rejected (`brief_not_fetched`). Composing with no
  idea what the real repertoire does is the single biggest cause of mechanical
  output.
- **What you then write is yours.** Quote, adapt, develop, or invent — your
  choice, moment by moment. A surface resembling none of the exemplars earns an
  advisory `composed_blind` note and nothing more. No statistic blocks a commit;
  only physical impossibility does (§9).

The brief is the whole corpus distilled for this phrase. Use every section:

- **CREATIVE INTENT** — what this passage must FEEL like. Start here.
- **MOTIFS THIS PHRASE CARRIES** — the piece's designed idea (character, contour,
  rhythm cell, recognition anchor) and the transform this phrase should apply to
  it. A piece is memorable because one idea keeps coming back changed. If a motif
  is listed, it is the material — state it, or transform it as asked, and make the
  recognition anchor audible.
- **PRINCIPAL THEME** — the piece's own theme, already composed. When a section
  calls for a return, transformation or fragment, this is the material; do not
  invent a second theme where the first one belongs.
- **CHORD FRAME** — the chord tones under each bar (and each beat, where the
  harmony moves inside the bar), spelled ready to write. Voicing against them
  is what keeps the vertical clean; departing from them is a decision you may
  make, not an accident to fall into.
- **COMPOSER FINGERPRINTS** — the traits that make this voice recognizable.
- **STYLE DOCTRINE** — cadence script, ornament intent, breathing, harmonic
  colour, melodic contour that apply *here*.
- **PHRASE SHAPE / CADENCE PATTERN / TEXTURE TRANSITIONS / LH VOCABULARY** —
  corpus patterns above the single bar.
- **STYLE TARGETS** — this composer's measured ranges. A reality check on what
  you wrote, never a specification to write toward (§2).
- **EXEMPLARS** — up to eight real corpus bars, transposed to this phrase's key
  and rendered in the shorthand you write in. Adapt them (§7); never copy one
  verbatim.
- **NAMED GESTURES** — this composer's own idioms with the notes and the
  expression already on them ("The Appoggiatura and Sigh" is E5 *espressivo*,
  D5, C5 held). Not statistics: material.
- **CORPUS GESTURES** — real shapes from the scores, selected for what this
  phrase is DOING (a presentation gets pickups and insists; a coda gets
  cadential releases). Rhythm and contour, not pitches — the pitches are yours.
- **WHAT THIS CORPUS ACTUALLY IS** / **CORPUS COVERAGE** — which repertoire the
  numbers below were measured on. When a statistic describes piano sonatas and
  you are writing a quartet, trust what you know of the genre.
- **RHYTHMIC FINGERPRINT** — the note values this composer actually writes.
- **AVOID (AI tells)**, ledger items, and the continuity state.

**TRANSITION IN** carries four things a phrase composed in isolation cannot
otherwise know: how every earlier phrase closed (so this one closes
differently), how long the current accompaniment idiom has run, where the
melody has been sitting, and **what the previous phrase left hanging** — a
seventh above the bass, or a dominant, is a debt this phrase owes. It also says
how this composer typically joins a phrase like this one to a phrase like that,
measured over the real joints in the corpus.

A phrase that ignores the fingerprints and the doctrine is generic even when
every number lands in range.

## §2 Density — a reality check, not a target

The brief prints this composer's real events-per-bar for each texture. It is a
diagnostic: it tells you when you have written a *sketch* instead of a
realization. It is not a quota, and composing to hit it produces exactly the
mechanical evenness it was meant to detect. (This section used to say "meet
them" in its first line and "not a total to hit" in its last.)

Generic ranges when the brief has no stats for a texture (from
`human-sounding-music.md`, corpus-derived):

| Texture | events/bar (typ.) | notes |
|---|---|---|
| RH singing_melody | 4-7 | single line + occasional doubled third/sixth |
| RH passage_work / scalar_run | 9-13 | continuous sixteenths |
| LH alberti / broken_chord | 8-12 | continuous eighths or sixteenths |
| LH walking / bass_melody | 4-8 | real line, not roots |
| LH block_chord_sparse | 2-4 | only where the music is chordal by intent |
| whole bar, both hands | 10-12 (6-18 range) | below 6 is usually a sketch |

The failure this catches is real: three quarter-note LH bars under a figurated
style is a sketch. Romantic figuration runs 6+ flowing LH notes per bar, often
spanning a tenth in arpeggiation. But a bar that is deliberately bare — a
cadence coming to rest, a silence before an entry — is music, and the gate only
ever warns (§9).

**Two different numbers are called "events per bar" in a brief.** The
per-texture medians count ONE hand. The `events_per_bar` under STYLE TARGETS
counts both hands together. They are not comparable; the brief now says so
where it prints them.

## §3 Left-hand character

The LH is a musician, not a metronome. Every composer's accompaniment
vocabulary is different — read the brief's LH VOCABULARY and TARGET STATS for
*this* composer rather than carrying one composer's habits everywhere.
Typically:

- The figure **tracks the harmony**: when the chord changes, the figure
  moves to the new chord's position, it doesn't restart on autopilot.
- The figure **responds inversely to the melody**: simplify under the
  melodic peak or fastest melody notes; fill and converse during melody
  rests and long notes.
- Change figure at **phrase boundaries**, not on a fixed rotation —
  and a figure may legitimately persist a whole section if that's the
  point (Raindrop prelude); make persistence a choice, vary its inner
  voicing.
- Consider pedal points under harmonic motion, a counter-melody in the
  tenor, octave reinforcement at climaxes.

Depth: `figuration-patterns.md`, `human-sounding-music.md` (LH tables).

## §4 Melody that sings

- **Hum test**: could the first four notes belong to any piece? Give the
  line a hook — a rhythmic cell, a signature interval, a contour shape.
- Mostly **stepwise (typically 35-50%+ of intervals)** with strategic
  leaps at expressive moments; after a leap, gap-fill stepwise the other
  way (Narmour).
- **Non-chord tones on strong beats** — appoggiaturas, suspensions —
  are where melody stops being arpeggiated accompaniment. C-E-G-C is a
  chord, not a tune.
- Contour breathes in waves: typically 1-2 direction changes per bar;
  one clear peak per phrase, placed asymmetrically.
- Vary the metric entry point; not every phrase starts on beat 1.
- **A scale is not a melody.** Measured against 26 canonical movements, plain
  unbroken stepwise runs occupy 0-15% of melody bars (median 2%). The last
  piece this system generated ran 39%: bar after bar of even eighths walking
  straight up or straight down an octave. A run is a *connector* between two
  ideas, not the idea. If a bar's melody is one direction and all steps, it is
  filling time — break it with a leap and a gap-fill, turn it back on itself,
  or give it a rhythmic profile instead of even values.
- **Repeated notes are melodic.** Real melodies restate a pitch 2-30% of the
  time (median 9%) — insistence, declamation, a drum-beat under a rising line.
  Generated melodies tend to sit far below that, and a line that never stays
  put reads as restless noodling.

Depth: `melody-craft.md`, `melodic-construction.md`.

## §4b Cadences — vary how the music arrives

This is the loudest tell there is, and the characteristic result of composing
phrases in isolation: **every phrase ending using the identical cadential
rhythm** (a half note plus a quarter rest, with the same root-chord-rest
underneath). Every phrase closes
the same way, so the form had no punctuation — just a repeating full stop.

Real music varies the arrival at least as much as the departure. Some ways:

| Device | What it does |
|---|---|
| Feminine ending | Resolve on a weak beat, not the downbeat |
| Elision | The cadence lands *on* the next phrase's first bar — no gap |
| Tie over the barline | The final note leans into the next phrase |
| Escape tone / appoggiatura | Decorate the arrival instead of stating it plainly |
| Deceptive turn | Go to vi where V-I was promised, then close later |
| Truncation | Cut the phrase a bar short and start the next early |
| Extension | Repeat the cadential bar with fuller voicing before closing |
| Register change | Take the close an octave lower than the phrase sat |
| Silence | Rest on the downbeat and let the ear supply the resolution |

Keep the strongest, plainest cadence for the moment that needs it most — the
end of the section and the end of the piece. If two adjacent phrases close
identically, one of them should not.

**Ending the piece.** The final bar must sound like a last bar: a fuller final
chord (add the octave below, the third above), a held value, a fermata where
the style takes one, a rolled chord (`:arp`). A last bar indistinguishable
from any other phrase-ending bar reads as the generator stopping rather than
the music ending.

Check the last chord by reading it, not by assuming it. The previous generated
piece ended on a **first-inversion tonic** — the final sounding sonority was
A-C-F in F major, with A in the bass, after a bare two-note dominant lasting an
eighth. Write the ending deliberately:

- The tonic in the **bass**, root position, unless you have a reason. (Four in
  five canonical movements end that way; the exceptions are mostly slow
  movements running attacca into the next, which is a deliberate open ending,
  not an accident.)
- A dominant that is actually **heard** before it — a real chord with weight,
  not two notes on an off-beat eighth.
- Make sure the bass note is still **sounding** at the end. A root struck on
  beat 1 and released before the final chord leaves an inversion behind.

## §5 Ornament with intent

Every ornament expresses something the bare note doesn't: a grace where
the music leans in, a turn where it yearns at a peak, a trill at the
cadential arrival. Ornaments at regular intervals are wallpaper — the
classic AI tell. The brief gives this composer's measured ornament densities per texture;
read them there rather than from a number written down here, which goes stale
the moment the corpus is rebuilt. Depth: `ornament-intent.md`.

## §6 Texture variety — the biggest human/AI separator

AI output typically holds one texture for 8-20 bars; real music does not.
But the opposite failure is just as mechanical, and this system used to
*plan* it — a different accompaniment idiom in every bar. The brief's
`texture_change_pct` band is the composer's own measured rate (Beethoven sits
near 0.26, i.e. roughly one change every four bars); read it there rather than
from a number in this file.

What matters is that texture change is **motivated** — by harmony arriving
somewhere, by the melody's register, by phrase rhetoric — never by a schedule
in either direction. Plan the voice-count arc across a section (2 voices
opening → fuller at climax → thinning to close). And **silence is a texture**:
rests typically 5-10% of the surface; let cadences ring. Depth:
`human-sounding-music.md`, `texture-classification.md`,
`dramatic-pacing-silence.md`.

### §6a Density was never the problem — variance was

Measured against 22 real Mozart movements, generated music is often *not* thin
by the numbers — around 1.13 notes per right-hand attack against a real median
of 1.15, with a texture-change rate inside the real 0.37-0.67 range. Density is
rarely the problem.

What was missing was **variance**: simultaneity CV 0.19 against a Mozart floor
of 0.22. The texture never thickened into a climax and never thinned into a
cadence — it stayed the same weight from the first bar to the last. So the fix
is not "add more notes"; it is to make the weight *move*. Thin to a single line
where the music withdraws, thicken to full chords at the arrival, and let the
cadence come to rest with less than what preceded it.

## §7 The adapt toolkit

How to earn notes from an exemplar (in roughly increasing freedom):

| Move | When | How |
|---|---|---|
| Transpose | Exemplar already fits the moment | Brief exemplars arrive pre-transposed; lift the rhythm+contour, adjust to your harmony |
| Reharmonize | Right figure, wrong chord | Keep the rhythmic skeleton; move pitches to your chord tones, keep NCT placement |
| Re-contour | Right energy, wrong shape | Keep durations; bend the pitch curve to your sketch anchors (peak where YOUR phrase peaks) |
| Splice | RH of one + LH of another | Combine; reconcile the seam (register, harmony) |
| Vary density | Right idea, wrong fullness | Split long notes into figuration or merge — keep the gesture's identity |
| Fresh in idiom | No exemplar fits | Write new material that obeys the exemplars' observed grammar (their rhythm vocabulary, NCT habits, register behavior) |

Verbatim copying produces a patchwork that won't cohere with your
phrase; ignoring exemplars produces a machine. Adaptation is the craft.
(The Python `corpus_adapter` offers these as functions — transpose_bar,
density_adjust, combine_hands, register_shift — but you can apply the
transforms directly when writing shorthand.)

## §8 The shorthand grammar — expression is part of the note

One dict per bar; `bars` length must equal the slot's `bar_count`.
Each bar dict: `{'rh': '<tokens>', 'lh': '<tokens>', 'dyn': 'p', 'art': 'stacc',
'text': 'dolce', 'ped': True}` — everything but `rh`/`lh` is optional.
`dyn` prints **once** (not once per staff); `art` applies to every sounding
note in the bar unless a note carries its own mark; `text` prints as italic
character text; `ped` puts a pedal-down at the bar's first left-hand note.

| Token | Meaning |
|---|---|
| `C5q` | note: pitch + octave + duration |
| `rest_q` | rest |
| `[C5,E5,G5]q` | chord (one rhythm) |
| `voiceA // voiceB` | **two independent voices in ONE hand** — sustained melody over a moving inner line, e.g. `Ab5h. Gb5q // Db5e Eb5e F5e Gb5e`. Each voice parses from beat 1; voice 1 sings on top, voice 2 is the inner line. Use instead of collapsing real polyphony into block chords. |
| `~` | tie (suffix) |
| `( ... )` | slur over the enclosed notes |
| `<` / `>` | crescendo / diminuendo start |
| `!` | hairpin stop |

Stackable `:xxx` suffixes:

| Group | Suffixes |
|---|---|
| Ornaments | `:tr` trill · `:mord` mordent · `:imord`/`:prall` inverted mordent · `:turn` · `:iturn` · `:schl` slide · `:ferm` fermata |
| Grace notes | `:grace` plain · `:acci` acciaccatura (slashed, crushed) · `:appo` appoggiatura (unslashed, takes time) |
| Articulations | `:stacc` · `:stacciss` wedge · `:port` portato · `:spicc` · `:acc` · `:ten` · `:marc` · `:breath` · `:caes` caesura |
| Techniques | `:arp` rolled chord · `:arpu`/`:arpd` rolled up/down · `:trem` · `:gliss`…`:glissend` · `:8va` / `:8vb` / `:loco` |
| Dynamics | `:ppp :pp :p :mp :mf :f :ff :fff :sf :sfz :fp :fz :rfz` |
| Pedal | `:ped` down · `:pedup` up · `:pedch` change |
| Character | `:dolce :cantabile :espressivo :leggiero :grazioso :sotto_voce :agitato :appassionato :tranquillo :morendo :risoluto :semplice :maestoso :scherzando :calando` … (prints as italic text) |
| Fingering | `:fin3`, or bare `:3` |

Three of these are worth calling out because nothing generated by this system
has ever used them, and their absence is audible:

- **`:arp` — the rolled chord.** The most characteristic piano notation there
  is. Roll the arrival chord, roll a wide left-hand stretch, roll the final
  chord of the piece.
- **Ties across the barline.** Write `C5h~` at the end of one bar and `C5h` at
  the start of the next. The assembler also splits a note that overruns its bar
  into tied fragments automatically, but writing the tie yourself is clearer.
  A score with no ties anywhere has every bar sealed off from the next.

  Measured over 103 real keyboard scores, ties run a **median 0.35 per bar**
  (p25 0.06, max 3.94). Everything this system has composed so far runs
  **0.008 per bar across 5,848 bars** — a fortieth of the median. Zero is a
  legitimate choice (19 of those 103 scores have none, mostly strict
  counterpoint where every voice is its own line), so this is not a rule. It is
  a tendency worth knowing you have: a held note across a barline is how one bar
  becomes a phrase instead of a unit, and the default here has been to seal
  every bar shut. The engraver's pass cannot fix it either — it only fills
  fields left blank and never changes a duration, so a tie is yours to write.
- **`:acci` vs `:appo` — and why `:grace` is the wrong default.** A crushed
  grace and an accented appoggiatura are different ornaments: `:appo` leans ON
  the beat, takes half the principal's written value away from it, and is the
  louder of the two; `:acci` is crushed in before the beat and steals no time.
  In Baroque and Classical writing an unmarked small note is normally read as
  the **long appoggiatura** — the leaning dissonance is where the expression
  lives in a slow movement — so reach for `:appo` first and `:acci` when you
  specifically want the flick. `:grace` is the *unspecified* mark and it sounds
  literally, as the short note you wrote: correct when that is what you mean,
  flat when you meant a lean. (28 of the first 30 grace marks written in this
  system were bare `:grace`, which is what prompted this note.)

Durations:
- plain: `w h q e s t x` — whole, half, quarter, eighth, 16th, 32nd, 64th
- longer than a whole: `br` breve (8 quarters), `dbr` dotted breve, `lo` longa.
  A note longer than its bar engraves as tied fragments across the barline; the
  meter check still asks each bar to fill, so in a bar shorter than the value
  write the tie yourself (`C5w~` then `C5w`).
- dotted: `dw dh dq de ds dt`; double-dotted: `ddh ddq dde`
- **tuplets**: `trip_q trip_e trip_s trip_t` (three in the space of two — three
  `trip_e` fill one beat exactly), plus `quint_e quint_s sext_s sept_s`. Rests
  take the same codes: `rest_trip_e`. Tuplets engrave with real brackets; use
  them, a rhythm with no triplets anywhere is a tell.

**Pickup bars (anacrusis).** Mark the phrase's first bar dict `'pickup': True`
and write only the upbeat's notes in it — they right-align to the barline
automatically (a one-beat pickup in 4/4 lands on beat 4) and the bar is exported
as a real partial measure. The pickup **occupies** the phrase's first bar, so
`bars` still has exactly `bar_count` dicts — don't add an extra one. Not every
melody starts on a downbeat; until recently none of them could.

```python
bars = [
  {'rh': 'G4q',            'lh': 'rest_q', 'pickup': True},   # upbeat
  {'rh': 'C5q. D5e E5q F5q','lh': 'C3e G3e E3e G3e C3e G3e E3e G3e'},
]
```

Two grammar rules worth knowing:
- `~` ties to the **immediately following** note, which must be the same pitch.
  A tie with a different next pitch is dropped (it cannot be notated).
- `( ... )` needs at least two notes. `(C5q)` alone is not a slur and is
  ignored.

Slurs, hairpins, dynamics, and articulation are not post-production —
write them with the pitches. A phrase with zero expression marks will
warn at the gate for ornament-rich styles. Shape every phrase
dynamically: where does it lean, where does it withdraw?

`//` takes **as many voices as you need**, not just two. Three in one hand, or
two in each for a four-voice chorale — each `//` section is an independent voice
that parses from beat 1 and engraves as its own staff voice, and each must fill
the bar on its own (the meter check now verifies every one of them separately).

```python
# four-voice writing: S+A in the right hand, T+B in the left
{'rh': 'C5h B4h // G4h G4h', 'lh': 'E3h D3h // C3h G2h'}
# three voices in one hand
{'rh': 'C5h B4h // G4h G4h // E4h D4h', 'lh': 'C3w'}
```

This is worth knowing because until recently it was capped at two voices per
hand, so genuine counterpoint required hand-written LayerIR JSON and therefore
never got written. If the music wants an independent inner line, write one.

## §8b One rule about durations, for anyone touching this code

`beats_to_dur` returns the **nearest** notatable value. That is right when you
are *describing* a duration and wrong whenever you are *fitting* one into a
space:

```python
remaining = capacity - offset      # 1.4375 beats left in the bar
dur = beats_to_dur(remaining)      # -> 'dq', a dotted quarter: 1.5 beats
```

The clamp is a no-op precisely when it matters. A clean remainder converts
fine; only an awkward one — which is the whole reason the note is being
clamped — lands on a longer neighbour and runs past the barline again. This
shipped in three separate places, including the tie-splitter, where a note
split to *fix* an overflow re-created one and compounded it across every
barline it crossed.

Use `duration.largest_dur_at_most(x)` for anything that must fit.

## §9 Reading gate diagnostics

**Only physical constraints block.** `meter` (bar capacity), range, and span
are strict and non-waivable. Everything else is **advisory** — a warning the
fresh-ears critic weighs, never an auto-block. You have creative liberty to
invent away from the corpus; your ear (and the critic's) is the judge, not a
statistical floor.

| Diagnostic | Meaning | How to read it |
|---|---|---|
| `meter` (**blocks** — physical) | An event overflows its bar's capacity | Real fix required: make each voice sum to the meter (a pedal under figuration = full-bar first LH event) |
| `unwritable_tokens` (**blocks** — physical) | A token in the shorthand cannot be engraved | A typo, not a judgement. `H5q` is not a pitch; `C12q` reads as `C1`, eleven octaves down; an unclosed chord vanishes entirely. The message names each one. Fix and recommit |
| `brief_not_fetched` (blocks, pre-gate) | Committing a phrase whose brief you never fetched | Call `get_composition_brief(piece_id, phrase_id)` first — studying the references is required |
| `brief_insufficient` (blocks, pre-gate) | Corpus yielded no exemplars for this phrase | Arm the composer (`acquire_composer.py <composer>`) and re-fetch, or waive only if composing without corpus is intended |
| `density_low_rh/lh` (advisory) | Skeletal vs corpus median | If you want more motion, add figuration; if the sparseness is intentional, leave it |
| `figuration_flat` (advisory) | Most bars share one LH pattern | Often fine for a persistent figure; vary it if it feels mechanical |
| `composed_blind` (advisory) | Surface resembles NONE of the briefed exemplars | Fine if it's deliberate invention; if it drifted by accident, anchor in the exemplars' cells/shapes |
| `same_accompaniment` (advisory) | >60% repeated pattern | Often fine if intentional — check it is |
| `register_monotony` (advisory) | Melody within one octave | Widen at the peak; use register as drama |
| `missing_silence` (advisory) | Zero rests | Add breath at phrase boundaries |
| `expression_zero` (advisory) | No slurs/ornaments/hairpins | See §8 |
| `direction_changes_per_bar` (advisory) | Monotonic contour | See §4 |
| `interval_distribution` (advisory) | Leap-dominated line | Gap-fill; the line reads as broken chords |
| `density_variance` (advisory) | Identical event count bar after bar | Let density ebb and flow; thin at cadences, thicken on the build |
| `flat_dynamics` (advisory) | One dynamic for the whole phrase | Shape it — where does it lean, where does it withdraw? |
| `ornament_wallpaper` (advisory) | Ornaments at regular intervals | Place them where the music leans, not on a schedule |
| `identical_restatement` (advisory) | A repeat that changes nothing | A return must be changed by what happened in between |
| `metronomic_rhythm` (advisory) | One note value throughout | Vary it — dotted figures, ties, agogic long notes |
| `root_position_bias` (advisory) | Every chord in root position | Inversions are what make a bass line step instead of leap |
| `scalar_fill` (advisory) | Runs used as filler | A scale is a gesture, not a way to reach the next bar |
| `safe_harmony` (advisory) | I-IV-V and nothing else | The corpus model offers this composer's real vocabulary; use it |

Treat advisory warnings as a second pair of eyes, not a checklist: respond to the
ones that name something you actually hear, surgically (revise the flagged bars,
don't re-roll the phrase), and consciously keep the rest if they're intentional.
Only a `meter` overflow (or a physical range/span breach) forces a fix.

### The realism audit (section level, in `self_evaluate.realism`)

The gate above judges one phrase. `self_evaluate` additionally reads the
**assembled section back off disk** and runs a second family of detectors, for
the defects that are not *wrong* but are obviously not written by a person.
These caught nothing for a long time because they did not exist: the previous
generated piece passed every gate the system had while using one cadence
formula in seven of its nine phrase endings and carrying no articulation at all.

Every one of these is advisory, and each was falsified against **26 canonical
movements** (14 Mozart sonata movements, 6 Chopin mazurkas, 6 Beethoven sonata
movements) by `tests/test_score_realism_calibration.py` — the thresholds sit
outside what real music does, and each detector's docstring states its measured
false-positive rate. Detectors that fire on canonical music are not warnings:
`tie_absent` and `closing_gesture_absent` fire on real movements and are
therefore `info` only.

When the audit first ran against that corpus, **seven of its detectors fired on
real music** — `dynamic_terracing` on 26 of 26, `repeated_bars` on 20 of 26.
They have been recalibrated or replaced. This is why a threshold here is never
a target to optimise toward: it marks the edge of what real music does, and
most real music sits nowhere near it.

| Finding | What it measured | Real-corpus range |
|---|---|---|
| `cadence_formula` | Two-thirds+ of phrase endings share one rhythm | See §4b |
| `register_stasis` | The melody never leaves one narrow band | **24-49 semitones, median 32.5** |
| `scalar_overuse` | Melody bars that are plain unbroken scale runs | 0-15%, median 2% |
| `articulation_absent` | Zero articulation marks in the whole section | median 0.57/bar |
| `tie_absent` | Nothing held over any barline | median 0.18/bar |
| `notation_spam` | One direction (`rit.`, `a tempo`) printed over and over | — |
| `accompaniment_monoculture` | One left-hand figure carries the whole piece | up to 0.85 |
| `identical_phrase_openings` | Even the contrasting phrases start the same | — |
| `uniform_phrase_lengths` | Every phrase exactly N bars, nothing ever stretches | 2-3 distinct lengths |
| `texture_stasis` | Sections indistinguishable in density and thickness | — |
| `dynamic_poverty` / `voicing_poverty` / `rhythm_vocabulary_poverty` | One dynamic level, single notes only, one note value | — |
| `closing_gesture_absent` | The last bar looks like any other bar | fires on 4/26 real — `info` |
| `repeated_bars` | Verbatim bar repetition at an extreme rate | **median 38% of bars, max 91%** — repetition is normal, `info` |

The report also carries a **notation census** — articulations, slurs, hairpins,
ties, ornaments, dynamics per bar. Real Mozart/Beethoven/Chopin movements run
0.11-5.71 marks per bar, median 1.58. A section well under that is under-marked
whatever else is true of it.

**Two of these deserve singling out, because they are the ones the system keeps
failing and neither is a notation problem — both are compositional.**

- **`register_stasis`.** Measured across the 26 reference movements, the melody
  staff spans **24 to 49 semitones (median 32.5)**; the narrowest canonical
  movement is a Chopin mazurka at exactly two octaves. A generated piece that
  stays inside that is narrower than anything real.
  Register is the cheapest structural device there is: open below where you
  intend to peak, take the return an octave up, drop to the tenor for the
  darkest phrase. A melody that lives inside one octave sounds like it is being
  played through a keyhole, however good the notes are.
- **`cadence_formula`.** Seven of that piece's nine phrase endings were the
  identical rhythm. A cadence is a piece of rhetoric, and rhetoric that repeats
  verbatim stops persuading: vary the approach, the rhythm of the arrival, and
  whether the line falls to the tonic or rises to the third. Note that
  *verbatim bar repetition elsewhere* is a different thing and is entirely
  normal — real movements repeat bars constantly (median 38% of a staff's
  bars). Repeating a bar is fine; ending every phrase the same way is not.

## §10 Canonical tool calls

All functions live in `scales.scales`; run from the repo root.

Fetch a brief (one phrase, or a whole section in one corpus load):

```bash
.venv/bin/python -c "
from scales.scales import get_composition_brief
print(get_composition_brief('<piece-id>', '<phrase-id>'))
"
```

```bash
.venv/bin/python -c "
from scales.scales import run_agent_section_briefs
print(run_agent_section_briefs('<piece-id>', '<section-id>'))
"
```

Record the phrase's structural plan (it becomes the SKETCH section of the next
phrase's brief — unknown keys are ignored):

```bash
.venv/bin/python -c "
from scales.scales import commit_phrase_sketch
print(commit_phrase_sketch('<piece-id>', '<phrase-id>', {
  'melody_anchors': [{'bar': 1, 'beat': 1.0, 'pitch_or_degree': 'F5', 'role': 'entry'}],
  'harmonic_rhythm': [{'bar': 1, 'beat': 1.0, 'roman': 'I'}],
  'breath_points': [{'bar': 2, 'beat': 3.0, 'type': 'rest'}],
}))
"
```

Commit shorthand bars through the gate (`allow=[{'check': ..., 'reason': ...}]`
to waive a named artistic check, logged):

```bash
.venv/bin/python -c "
from scales.scales import commit_agent_phrase_direct_bars
bars = [
  {'rh': '(D5q E5e F5e G5q:tr A5q)', 'lh': 'D3e A3e F3e A3e D3e A3e F3e A3e', 'dyn': 'p'},
  # ... one dict per bar, exactly bar_count bars
]
r = commit_agent_phrase_direct_bars('<piece-id>', '<phrase-id>', bars)
print(r)
"
```

Commit full LayerIR JSON (multi-voice writing):

```bash
.venv/bin/python -c "
import sys, json; from scales.scales import commit_agent_phrase_layer_ir
r = commit_agent_phrase_layer_ir('<piece-id>', '<phrase-id>', json.loads(open('layer.json').read()))
print(r)
"
```

Panel candidates (candidate-composer agents only): same payloads via
`commit_candidate_phrase(piece_id, phrase_id, lens, bars=...)` — stored
under `workspace/<piece>/candidates/` with a MusicXML preview, never in
the graph. The orchestrator promotes the judge's winner with
`promote_candidate(piece_id, phrase_id, lens)`.
