# How It Works

This is the honest explanation of what happens when you ask Wolfgang for a piece — the algorithm, the evidence it composes from, the checks it runs, and how a long work stays coherent. If you want the exhaustive module-by-module reference, that's in [CLAUDE.md](../CLAUDE.md); this is the readable version.

## The core idea: compose from evidence, check the result

The thing that makes machine-composed music sound machine-composed is usually one of two failures. Either the system assembles pre-made fragments and the seams show, or it samples from a model that has no notion of *this* phrase's job in *this* piece and produces something locally plausible but globally dead.

Wolfgang's answer is to do what a student composer does: study real examples of the thing you're trying to write, then write your own version, then have someone listen to it critically. Concretely:

1. **Claude writes the notes** — not a fragment library, not a sampler. The model composes every note of every phrase.
2. **But never blind.** Before writing a phrase, Claude is handed a *composition brief* full of real bars from the corpus and the statistics of how the target composer actually writes.
3. **And never unchecked.** A quality gate blocks the phrase at commit time if it's skeletal, photocopied, or unlike anything in the brief. A separate critic then listens to whole sections with fresh ears.

The engine's job is to *provide, gate, and fall back* — it builds the briefs, enforces the gate, and can realize a phrase itself if Claude doesn't. Claude's job is to compose well from what the engine provides.

## SCALES, in plain language

The algorithm is called SCALES — Sketch-Conditioned Alternating Ledger-guided Expansion Search. Unpacked, it's a sequence of sensible ideas:

- **Sketch-conditioned.** Claude doesn't jump straight to final notes. It first writes a sketch of the phrase — the structural pitches, where the harmony moves, what texture it intends, where the music breathes — and *then* composes the surface against that sketch. Plan before detail.
- **Ledger-guided.** A running ledger tracks the musical promises the piece has made and not yet kept, so later phrases answer earlier ones instead of wandering. (More on this below.)
- **Expansion search.** For the structurally important phrases — a theme's first statement, a climax, a final cadence — Wolfgang can compose several candidate versions through different interpretive lenses and let the critic pick the best, rather than accepting the first attempt.

For ordinary phrases it's mostly a clean forward pass: brief, sketch, compose, gate, commit. The search machinery comes out for the moments that carry the piece.

## The composition brief

This is the heart of "never compose blind." Before any notes are written for a phrase, the engine assembles a brief scoped to exactly that phrase's job. It contains:

- **Real exemplar bars** — up to a handful of actual bars from the corpus, transposed into the phrase's key and shown in a compact shorthand. These are the models to adapt.
- **Density and ornament statistics** — how many notes per bar this composer typically writes in this texture, how often they ornament, how the left hand moves. Drawn from thousands of real bars, not guessed.
- **Fingerprints** — the handful of habits that make this composer recognizable.
- **Doctrine** — phrase-scoped guidance: how cadences are typically scripted, when ornaments are intended, how the harmony is colored.
- **Continuity** — what the previous phrase left hanging: its final melody note, register, and dynamic, so this phrase can connect rather than restart.

The instruction to Claude is blunt: *adapt the exemplars — never copy them verbatim, never ignore them.* A phrase can't even be committed unless its brief was actually fetched first; that's enforced, not encouraged.

## The commit gate

When Claude commits a phrase, it passes through a blocking gate calibrated on the real corpus. The gate doesn't judge taste — a separate critic does that. It catches the mechanical failures that have a measurable signature:

- **Brief not fetched / brief insufficient** — you can't commit a phrase whose brief was never pulled, and a brief with no real exemplars (an unarmed composer) blocks rather than letting the system improvise from nothing.
- **Density floors** — a phrase that's skeletal relative to how this composer actually writes, in the texture it claims to be, gets blocked. The check is per-bar against each bar's own texture and only fires when a clear majority of bars are thin, so a phrase that legitimately thins out at a cadence still passes.
- **Composed blind** — if the committed surface resembles none of the briefed exemplars in its rhythm and intervals, it's blocked. This is the enforcement behind "adapt, don't ignore."
- **Photocopied accompaniment** — left-hand figuration mechanically repeated bar after bar gets flagged.

Crucially, the gate is overridable — but honestly. Sometimes the music genuinely wants to be sparse. To waive a check you must give a real, recorded reason (at least a sentence), and you can waive at most one blocking check per commit. Every override goes into the piece's revision history. There is no silent "skip the gate" switch; if the music breaks a rule, the file says so and says why. A real bar from the corpus passes its own composer's gate — the thresholds are calibrated against the genuine article.

## The fresh-ears critic

Gates catch the mechanical. They can't hear whether a melody sings. So after a section is composed, a separate reviewer — the music critic — listens to it.

The critical detail is what the critic *doesn't* get: it never sees the briefs, the sketches, or any rationale for why the music was written the way it was. It hears the assembled score and a MIDI rendering, plus a discriminator report of how the section's statistics compare to the composer's real distribution. Then it judges the things that matter and can't be measured:

- Does the melody sing across the section, or is it just correct notes?
- Does the narrative arc land — is there a real climax, built from register and harmony and texture and dynamics together?
- Is there one genuinely memorable moment?
- Do the phrases connect into one fabric, or merely follow one another?
- Does it sound like a person wrote it, or a machine?

The critic returns a verdict — approve, or revise — and when it asks for changes, it writes them as specific, smallest-possible edits tied to bar numbers, not "redo this." Withholding the rationale is deliberate: a reviewer who's been told the intent tends to hear the intent instead of the result.

## The ExpectationLedger: coherence over time

A piece is not a list of good phrases; it's a structure of promises and payoffs. A theme stated early demands recapitulation. A harmonic tension opened must resolve. A gesture overused needs a rest before it returns.

The ExpectationLedger is the system's working memory for exactly this. It tracks promises (things set up that need following through), debts (things owed), cooldowns (gestures that need a break), and locks (identity that must be preserved — essential in variation and orchestration modes, where the original's themes or structure are fixed). As composition moves phrase to phrase, section to section, and movement to movement, the ledger carries forward, so the piece answers itself across its whole length instead of forgetting what it just did.

## The pipeline and the cast

```
/wolfgang "describe your piece"
        │
   ┌────┴─────────────────────────────────────────┐
   │ (optional) interpret images/concepts          │
   │ (optional) research an unknown composer        │
   └────┬─────────────────────────────────────────┘
        ▼
   plan ──────►  contract, style, narrative arc, form, motifs
        │
        ▼
   for each section:
        ┌──────────────────────────────────────────┐
        │ for each phrase:                          │
        │   brief → sketch → compose → gate → commit │  (≤3 attempts)
        └──────────────────────────────────────────┘
        review the whole section  (fresh-ears critic)
        apply targeted revisions   (≤2 passes)
        │
        ▼
   (concertos/symphonies) orchestrate the piano core
        │
        ▼
   assemble ──►  MusicXML + MIDI in output/
```

The work is split across a few specialized roles so that each holds only what it needs:

| Skill | Job |
|-------|-----|
| `/wolfgang` | Orchestrator — parses the request, picks the mode, runs the pipeline, holds only summaries. |
| `/w-plan` | Builds the whole architecture before any notes: contract, style, narrative, form, motifs. |
| `/w-compose` | Composes one phrase end to end: brief → sketch → notes → gated commit. |
| `/w-review` | Fresh-ears review of a section; writes structured revision requests. |
| `/w-assemble` | Assembles sections into the final MusicXML and MIDI. |
| `/w-interpret` | Turns images and concepts into musical parameters. |
| `/w-research` | Researches an unknown composer and builds a temporary profile. |

| Subagent | Job |
|----------|-----|
| phrase-composer | The workhorse — composes routine phrases in an isolated context. |
| candidate-composer | Composes one interpretation (lyrical, dramatic, or contrapuntal) of an important phrase, for the panel. |
| music-critic | The fresh-ears reviewer and the judge that compares candidate phrases. |

This separation isn't bureaucracy — it's what lets a symphony stay coherent. The orchestrator never drowns in note-level detail, the phrase composers never see the whole graph, and the critic never sees the rationale. Each does one job well with exactly the context it should have.

## Going deeper

[CLAUDE.md](../CLAUDE.md) is the complete reference: every module in the `scales` package, the data models (PieceContract, StyleDNA, PieceGraph, the various IRs), the corpus build scripts, and the three-layer context stack. It's written as instructions for the agent, but it's the authoritative map if you want to read the code.
