---
name: w-review
description: "Fresh-ears musical review of composed sections — judges what the commit gate can't hear (singing line, narrative arc, memorable moments, cross-section continuity). Writes structured RevisionScripts."
argument-hint: "<piece-id> <section-id>"
---

# w-review — Listening Review

With blocking commit gates catching density, anti-patterns, and
playability per phrase, review focuses on what gates cannot hear. A
section that passed every commit gate can still fail review for being
correct-but-dead. That is the point of this phase. You are listening as
a musician, not auditing metrics — count nothing; ask why.

## Run it fresh-ears

Run the review through the `music-critic` subagent (Agent tool) so the
reviewer has NOT seen the composition rationale. Give it ONLY:
`piece_id`, `section_id`, the assembled paths, and the discriminator
report below. Never paste briefs, sketch reasoning, or composer
summaries into its prompt — that destroys the fresh-ears value.

The review criteria (does the melody sing · does the arc land · one
memorable moment · do phrases connect · person-or-machine · sounds-like-
THIS-composer) live in `.claude/agents/music-critic.md`. The fresh-ears
subagent is the **default and the norm** — dispatch it. Inline review (the
main conversation judging its own work) defeats the purpose and is a
last resort only when the subagent is genuinely unavailable; if you must,
read that file, apply its criteria, and **say in your report that review
was done inline (not fresh-ears)** so the loss of independence is visible.

## Step 1: Review context (evidence, not verdict)

One call gives the critic everything — the assembled score and MIDI, the
discriminator report, and the same findings phrased as musical sentences:

```bash
.venv/bin/python -c "
import json; from scales.scales import review_context
r = review_context('<piece-id>', '<section-id>')
print(r['musical_prose'])          # what to read first
print(json.dumps(r['evaluation'], indent=1))
"
```

`musical_prose` is deliberately prose, not metrics. A critic handed z-scores
revises toward the z-score, which is the metric whack-a-mole this system
rejects. It answers the questions that decide whether a piece is any good:

- **Does the theme come back?** A theme stated once and never returned is an
  opening, not a theme.
- **Do the cadences differ, and is each one the cadence that was planned?**
  Nothing checked a realized cadence against its plan until recently — the
  previous piece closed seven of its nine phrases identically, and two of its
  structural cadences had no dominant at all.
- **Does the texture's weight move?** Not "is it thick enough" — the last piece
  measured normal density and a simultaneity CV *below* anything real Mozart
  does, meaning it never thickened at a climax or thinned into a cadence.
- **Does the page read as engraved music?** Articulation, ties, slurs,
  hairpins per bar against the real-corpus range.
- **Is the part-writing clean?** Parallels, hidden octaves, spacing, hand span.

Take `r['concerns']` as the short list of what the analyzers actually flagged.
Then read the score yourself — the prose tells you where to look, it does not
tell you whether the music is good.

The raw report is still there if you want the numbers:

```bash
.venv/bin/python -c "
import sys, json; from scales.scales import self_evaluate
print(json.dumps(self_evaluate('<piece-id>', '<section-id>'), indent=1))
"
```

Compares the assembled section against corpus norms on the metrics that
most separate human music from AI output — texture_change_pct above all
(corpus ≈ 0.4-0.7; AI tends to ≈ 0.1), direction changes, density
variation, rest ratio, stepwise mix. Flags are evidence for ears, not a
checklist.

`self_evaluate` now also embeds two things the critic should weigh:
- **`corpus_divergence`** — the section scored against THIS composer's own
  per-movement distribution (z-scores; `|z|>2` = outside the spread of real
  movements for that trait). Run it standalone for the whole piece with
  `compare_to_corpus(piece_id, section_id)`. This is composer-specific, unlike
  the generic bands above.
- **`authoring`** — how many phrases were agent-authored vs engine-realized,
  and any `composed_blind` phrases (a committed surface that resembled none of
  its briefed exemplars). This is **advisory**: composing away from the briefed
  exemplars is a legitimate creative choice. Listen — if a blind phrase sings,
  it stays; if it drifted by accident, that's a revision target. Your ear, not
  the flag, decides.
- **`section_gate`** — its `hard_failures` are **physical only**, but they are
  real: they are read back off the ASSEMBLED score, so they catch what the commit
  gate could not see (a bar holding more beats than its meter after export, a
  note outside the instrument's range). Fix those. It never hard-fails on
  anything artistic; composed-blind phrases and the notation census come through
  as `advisory`. The fresh-ears critic, not this gate, judges whether the section
  works.

The numeric style gate (`run_style_review_section`) also runs these
targets and can emit a machine RevisionScript for engine-realized
phrases; it never auto-targets agent-authored phrases.

## Step 2: Dispatch the critic, then check the ledger

After the critic's verdict, check the ExpectationLedger yourself: are
musical promises kept — motif returns due in this section, pending
resolutions, climax delivery, texture-variety debts?

## Step 3: RevisionScript (if revising)

Structured ops, not prose. Match the fix to the problem: a **local defect**
(clash, buried note, one weak bar) gets the smallest bar-level edit; a
**structural weakness** (the line doesn't sing, a flat climax, phrases that
don't connect) gets a re-heard, recomposed passage — a contiguous run of bars,
or the phrase — because patching one bar won't fix a line. Drive revision by
what you hear, never to push a metric back into band.

```json
{
  "section_id": "m1_a",
  "ops": [
    {
      "target_phrase": "m1_a_p1",
      "target_layer": "principal_line",
      "target_bars": [5, 6],
      "operation": "re_sketch",
      "params": {"reason": "melody too predictable"},
      "reason": "Needs chromatic surprise before cadence"
    }
  ],
  "priority": "important",
  "max_iterations": 3
}
```

Apply via `apply_revision(piece_id, section_id, ops)`. Max 3 review
iterations per section — after that, accept or escalate to the user with
your honest assessment.

## Step 4: Corpus divergence is a DIAGNOSTIC, not a revision driver

`compare_to_corpus(piece_id, section_id)` z-scores tell you where a section sits
relative to the composer's real spread. **Read it to understand, never to
chase.** Falsification against real scores showed an out-of-band z-score does not
mean bad music — real Chopin and Beethoven sit outside a MIDI-derived corpus's
narrow bands. Optimizing one metric back into band reliably breaks another
("metric whack-a-mole"), and that is exactly the mechanical-sounding output this
system rejects.

So there is **no auto-revision loop here**. Revision targets come from the
fresh-ears critic and the `musical_ear` (audible defects: clashes, buried melody,
no breathing, monotony) — Steps 2-3. If a z-score flag *coincides* with something
the critic actually heard ("this section is monotonous"), fix what the critic
heard; the z-score was just a corroborating hint. If the critic is happy and a
z-score is out of band, **leave it** — the music is the judge of the metric, not
the other way around. Always report residual divergence honestly in your summary,
but do not revise to satisfy it.
