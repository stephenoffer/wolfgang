# Note-Writing Craft — for the agent that authors every pitch

A router and distillation, not a textbook. Each section gives the
load-bearing rule and points into `.claude/context/general/` for depth.
Artistic guidance here is guidance — "typically", "consider" — only
physical constraints (ranges, spans, meter) are strict.

This file is the single source of truth for the shorthand grammar (§8),
the gate loop (§9), the adapt toolkit (§7), and the canonical tool-call
snippets (§10). Skills and agents point here instead of restating.

## §1 The one rule

**Never write notes you have not earned from the brief.** Get
`get_composition_brief(piece_id, phrase_id)` before composing; read the
exemplar bars as music, not as a formality. If you catch yourself
inventing an accompaniment pattern from scratch, stop — go read an
exemplar. Composing blind is the single biggest cause of mechanical
output. Then: **adapt, don't copy, don't ignore** (§7).

**The brief is the whole corpus distilled for this phrase — use every
section, not just the exemplars.** It now carries, in addition to the
EXEMPLARS:
- **COMPOSER FINGERPRINTS** — the traits that make this voice recognizable;
  the phrase should exhibit one or two, not just avoid wrong notes.
- **STYLE DOCTRINE (this phrase)** — cadence script, ornament intent,
  breathing, harmonic color, melody priors that apply *here*.
- **PHRASE SHAPE** — the corpus density/register arc to follow (where the
  peak lands), so the phrase has a trajectory, not flat bars.
- **CADENCE PATTERN** — the real chord/soprano/bass formula for your cadence.
- **TEXTURE TRANSITIONS** — how the corpus moves between textures (so the
  accompaniment varies idiomatically instead of photocopying).
- **LH VOCABULARY** — canonical real left-hand figures to start from.
- **Corpus targets** — this composer's actual discriminator bands.
- **AVOID (AI tells)** — the mechanical patterns to stay clear of.
A phrase that ignores the fingerprints and doctrine is generic even if its
density is right. Surfacing this material cost real work; skipping it wastes
it. Fetching the brief is enforced (a receipt is required at commit:
`brief_not_fetched` otherwise), and the gate **blocks** a surface that
resembles none of the briefed exemplars (`composed_blind`) — so read them
and adapt them in earnest.

## §2 Density by texture — honesty about how many notes

The brief gives composer-and-texture-specific targets; meet them.
Generic corpus ranges when the brief lacks a texture
(from `human-sounding-music.md`, corpus-derived):

| Texture | events/bar (typ.) | notes |
|---|---|---|
| RH singing_melody | 4-7 | single line + occasional doubled third/sixth |
| RH passage_work / scalar_run | 9-13 | continuous sixteenths |
| LH alberti / broken_chord | 8-12 | continuous eighths or sixteenths |
| LH walking / bass_melody | 4-8 | real line, not roots |
| LH block_chord_sparse | 2-4 | only where the music is chordal by intent |
| whole bar, both hands | 10-12 (6-18 range) | below 6 = skeletal writing |

Three quarter-note LH bars under a figurated style is a sketch, not a
realization — Romantic figuration (Chopin) runs 6+ flowing LH notes per
bar, often spanning a tenth-plus in arpeggiation. The commit gate blocks
density below half the corpus median; don't write toward the gate, write
toward the median.

## §3 Left-hand character

The LH is a musician, not a metronome. From the corpus: the most common
LH rhythm is **three quarters (17%)**, then Alberti sixteenths (14%),
then held notes — variety is the norm. Typically:

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

Depth: `melody-craft.md`, `melodic-construction.md`.

## §5 Ornament with intent

Every ornament expresses something the bare note doesn't: a grace where
the music leans in, a turn where it yearns at a peak, a trill at the
cadential arrival. Ornaments at regular intervals are wallpaper — the
classic AI tell. The brief gives corpus ornament densities (e.g. Mozart
singing_melody ≈ 0.18 grace notes/bar); use them as a reality check,
not a quota. Depth: `ornament-intent.md`.

## §6 Texture variety — the biggest human/AI separator

Corpus Beethoven changes bar-to-bar texture **~58% of the time** (most
common run: 1 bar); AI output typically holds one texture 8-20 bars.
Texture change is motivated — by harmony arriving somewhere, by the
melody's register, by phrase rhetoric — never by a schedule. Plan the
voice-count arc across a section (2 voices opening → fuller at climax →
thinning to close). And **silence is a texture**: rests typically 5-10%
of the surface; let cadences ring. Depth: `human-sounding-music.md`,
`texture-classification.md`, `dramatic-pacing-silence.md`.

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
Each bar dict: `{'rh': '<tokens>', 'lh': '<tokens>', 'dyn': 'p'}`
(`dyn` optional — or mark dynamics inline on notes).

| Token | Meaning |
|---|---|
| `C5q` | note: pitch + octave + duration |
| `rest_q` | rest |
| `[C5,E5,G5]q` | chord |
| `~` | tie (suffix) |
| `( ... )` | slur over the enclosed notes |
| `:tr :mord :turn :grace` | ornaments |
| `:stacc :acc :ten :marc` | articulations |
| `:pp :p :mp :mf :f :ff` | dynamics |
| `<` / `>` | crescendo / diminuendo start |
| `!` | hairpin stop |

Durations: `w h q e s t`; dotted: `dh dq de ds`.

Slurs, hairpins, dynamics, and articulation are not post-production —
write them with the pitches. A phrase with zero expression marks will
warn at the gate for ornament-rich styles. Shape every phrase
dynamically: where does it lean, where does it withdraw?

For genuinely multi-voice writing (independent inner voices,
counter-melodies) that shorthand can't express, build full LayerIR JSON
and commit with `commit_agent_phrase_layer_ir` instead (§10).

## §9 Reading gate diagnostics

| Diagnostic | Meaning | Typical fix |
|---|---|---|
| `brief_not_fetched` (blocks, pre-gate) | Committing a phrase whose brief you never fetched | Call `get_composition_brief(piece_id, phrase_id)` first — the corpus exemplars are mandatory |
| `brief_insufficient` (blocks, pre-gate) | Corpus yielded no exemplars for this phrase | Arm the composer (`acquire_composer.py <composer>`) and re-fetch, or waive only if composing without corpus is intended |
| `density_low_rh/lh` (blocks) | Skeletal writing vs corpus median (a hard generic floor applies even with no corpus stats) | Add real figuration — flowing arpeggiation, passing tones, inner motion — or waive with a reason if sparseness IS the idea |
| `figuration_flat` (blocks) | ≥90% of bars share one LH pattern (now fires on 2+ bar phrases too) | Vary inner voicing, invert contour mid-phrase, follow the harmony into new positions |
| `composed_blind` (blocks) | Surface resembles NONE of the briefed exemplars | Borrow the exemplars' rhythmic cells + interval shapes; or waive if composing away from the corpus is intended |
| `same_accompaniment` (warns) | >60% repeated pattern | Often fine if intentional — check it is |
| `register_monotony` (warns) | Melody within one octave | Widen at the peak; use register as drama |
| `missing_silence` (warns) | Zero rests | Add breath at phrase boundaries |
| `expression_zero` (warns) | No slurs/ornaments/hairpins | See §8 |
| `direction_changes_per_bar` (warns) | Monotonic contour | See §4 |
| `interval_distribution` (warns) | Leap-dominated line | Gap-fill; the line reads as broken chords |

Respond to the diagnostic surgically — revise the flagged bars, don't
re-roll the phrase. Max 3 commit attempts; then override with an honest
reason or hand the phrase back. Waivers are constrained on purpose: a
reason must be a real musical justification (**≥20 chars**), and **at most
one blocking check may be waived per commit** — waiving the whole blocking
set is rejected as "make the gate go away". Physical checks (`meter`,
range, span) are never waivable.

## §10 Canonical tool calls

All functions live in `scales.scales`; run from the repo root.

Fetch a brief (one phrase, or a whole section in one corpus load):

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import get_composition_brief
print(get_composition_brief('<piece-id>', '<phrase-id>'))
"
```

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.scales import run_agent_section_briefs
print(run_agent_section_briefs('<piece-id>', '<section-id>'))
"
```

Commit shorthand bars through the gate (`allow=[{'check': ..., 'reason': ...}]`
to waive a named artistic check, logged):

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
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
python3 -c "
import sys, json; sys.path.insert(0, 'tools')
from scales.scales import commit_agent_phrase_layer_ir
r = commit_agent_phrase_layer_ir('<piece-id>', '<phrase-id>', json.loads(open('layer.json').read()))
print(r)
"
```

Panel candidates (candidate-composer agents only): same payloads via
`commit_candidate_phrase(piece_id, phrase_id, lens, bars=...)` — stored
under `workspace/<piece>/candidates/` with a MusicXML preview, never in
the graph. The orchestrator promotes the judge's winner with
`promote_candidate(piece_id, phrase_id, lens)`.
