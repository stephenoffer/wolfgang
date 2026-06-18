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

## Step 1: Discriminator report (evidence, not verdict)

```bash
python3 -c "
import sys, json; sys.path.insert(0, 'tools')
from scales.scales import self_evaluate
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
  its briefed exemplars). A blind phrase ignored the corpus that was put in
  front of it — treat it as a prime revision target.
- **`section_gate`** — a hard pass/fail verdict (`passed` + `hard_failures`)
  derived from the egregious cases (mechanically static texture, composed-blind
  phrases, many traits far outside the corpus). A failed section_gate must be
  resolved or explicitly justified before the section is accepted — it is not
  advisory.

The numeric style gate (`run_style_review_section`) also runs these
targets and can emit a machine RevisionScript for engine-realized
phrases; it never auto-targets agent-authored phrases.

## Step 2: Dispatch the critic, then check the ledger

After the critic's verdict, check the ExpectationLedger yourself: are
musical promises kept — motif returns due in this section, pending
resolutions, climax delivery, texture-variety debts?

## Step 3: RevisionScript (if revising)

Structured ops, not prose. Target the SMALLEST change that fixes the
problem; never wholesale re-realize an agent-authored phrase — propose
bar-level edits instead.

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

## Step 4: Bounded corpus-divergence loop (auto-revision)

After the ears review, close the loop against the corpus distribution.
This catches statistical drift the critic may not name — a section that
sounds fine bar-to-bar but, as a whole, sits outside the composer's real
spread (too flat, too dense, monotone texture).

Run up to **2 passes**:

1. `compare_to_corpus(piece_id, section_id)` → read `flags` (`|z|>2`),
   `texture_divergence.over`, and `authoring.composed_blind_phrases`.
2. If nothing is flagged, stop — the section is corpus-faithful.
3. Otherwise, translate each flag into a targeted revision and dispatch the
   `music-critic` with the divergence flags (it returns bar-level
   `revision_ops`). Map the drift to where it lives:
   - `texture_change_pct` / `lh_texture_change_pct` **low** → the most
     monotonous phrases (identical density bar-to-bar); vary the
     accompaniment, change figure at phrase boundaries.
   - `events_per_bar` **low** → skeletal phrases; raise figuration to the
     density target. **high** → overstuffed; thin under the melody.
   - `density_cv` **low** → flat dynamics of activity; add ebb and flow.
   - `composed_blind` phrases → re-compose adapting the briefed exemplars
     (re-read the brief first).
4. `apply_revision(...)`, then re-run `compare_to_corpus` to confirm.

Stop after 2 passes regardless. **Log the residual** — never hide an
unresolved drift: report which metrics are still `|z|>2` and which phrases
were recomposed, so the final state is honest. Targeted bar edits only;
never wholesale re-realize an agent-authored phrase.
