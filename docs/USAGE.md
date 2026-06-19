# Usage Guide

This walks you through installing Wolfgang, composing your first piece, writing prompts that work, and getting the most out of the system. If you just want the elevator pitch, start with the [README](../README.md).

## Install and verify

You need Python 3.10 or newer and [Claude Code](https://claude.com/claude-code). From the repo root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

This installs the engine (the `scales` and `scripts` packages) along with music21, lxml, and the dev tools (ruff, pytest). Confirm the install:

```bash
.venv/bin/python -c "from scales import composition_brief; print('OK')"
```

If that prints `OK`, you're ready. The corpus ships in the repo, so there's nothing to download — eleven composers are armed and waiting.

To view what Wolfgang produces, install [MuseScore](https://musescore.org). It's free and opens the `.musicxml` files directly. The `.mid` previews will play in almost anything.

## Your first piece

Open the project in Claude Code and ask for something:

```
/wolfgang a tender nocturne in D-flat major in the style of Chopin
```

Here's what happens, and what you'll see at each stage.

**Planning.** Wolfgang works out the architecture before writing any notes: the key scheme, the form (a nocturne's ABA with a coda, say), the emotional arc and where the climax sits, and the handful of motifs the piece will be built from. It shows you this plan — the form graph, the themes, a short style summary — so you can see the shape before it commits.

**Composing, section by section.** For each section, Wolfgang composes one phrase at a time. Each phrase starts from a brief of real Chopin bars and statistics, gets sketched, then written note by note, then checked at commit by the quality gate. You see short summaries as sections complete — character, key gestures, anything notable — not raw note lists. The notes are on disk.

**Review.** After a section is composed, a separate critic listens to it fresh — without ever seeing why it was written the way it was — and returns a verdict: approve, or revise with specific bar-level fixes. You see the verdict and the one moment the critic found most memorable.

**Assembly.** When everything is composed and reviewed, Wolfgang assembles the sections into the final score and writes it out.

When it finishes, look in `output/` for the `.musicxml` (open it in MuseScore) and a `.mid` preview. The full working state — every phrase, every revision, the running ledger of musical promises — lives in `workspace/<piece-id>/`.

## Writing prompts that work

Wolfgang reads a plain-language description and figures out the mode, style, key, form, instrumentation, and mood. The more of those you name, the closer the result lands to what you imagined. You don't have to specify everything — it fills gaps with sensible choices — but specifics help.

Things you can name, with examples:

- **A composer or style:** *"in the style of Beethoven"*, *"a baroque trio sonata"*, *"romantic and Lisztian"*. Naming an armed composer (see the roster below) gives the richest result.
- **A key and a form:** *"a piano sonata in G minor"*, *"a theme and variations in A major"*, *"a string quartet, first movement, sonata form"*.
- **A mood or a program:** *"a winter forest at dusk, sparse and cold, warming as it goes"*. Wolfgang maps imagery and emotion onto register, density, dynamics, and texture.
- **A blend:** *"a mix of Chopin's lyricism and Rachmaninoff's weight"*. Style packs and blending make this real rather than a label.

Some prompts that have produced real pieces in this repo:

```
/wolfgang a three-movement piano sonata in G minor in the style of Mozart
/wolfgang a nocturne — a moonlit forest at dusk, then a flowing river, then stillness
/wolfgang a stormy sonata-form movement in D minor
```

### Composing from an image or a concept

If your idea is visual or abstract rather than musical, Wolfgang can translate it first. Point it at an image or describe a scene, and the `/w-interpret` step turns color, texture, movement, and mood into musical parameters — key, tempo, density, register, dynamics — before planning begins. You can let `/wolfgang` invoke this automatically, or run `/w-interpret` yourself to see the parameters it extracts.

### Referencing an existing work

You can anchor a request to a known piece — *"something with the gravity of the Moonlight Sonata's first movement"* — and Wolfgang pulls out the key, tempo, texture, and mood to inform a new piece. Note this informs a *new* composition; to actually transform a specific score you load, use one of the transformation modes below.

## The six modes

Every mode runs the same composition algorithm. They differ in what's locked in place — a variation keeps the themes, an orchestration keeps the identity of the original.

**Compose from text** *(default)* — a fresh piece from your description. This is what you get unless you ask for something else.

**Variation** — vary an existing piece while keeping its themes and form intact.
> *"variations on the theme from this piece: path/to/score.musicxml"*

**Style transfer** — re-cast an existing piece in a different idiom, keeping its structure but changing its surface.
> *"restyle this Mozart sonata as if Chopin wrote it: path/to/score.musicxml"*

**Reduce to piano** — condense an orchestral score into a playable two-hand piano version. Wolfgang's reduction engine works out what to keep and how to fit it under ten fingers.
> *"reduce this orchestral score to solo piano: path/to/score.musicxml"*

**Orchestrate** — expand a piano piece into an orchestral one, assigning material to instruments by register and role.
> *"orchestrate this piano piece for full orchestra: path/to/score.musicxml"*

**Continue** — extend an existing piece from where it stops, carrying its musical commitments forward.
> *"continue this piece for another minute: path/to/score.musicxml"*

## Working with composers

Eleven composers ship fully armed — real bars, real statistics — and these give the best results:

> Bach · Beethoven · Chopin · Corelli · Handel · Haydn · Monteverdi · Mozart · Palestrina · Schubert · Weber

You can also compose **in a style** rather than as one person. Four style packs — **classical**, **baroque**, **romantic**, **renaissance** — aggregate across their member composers, so *"in the classical style"* draws on Mozart, Haydn, and Beethoven together rather than imitating one. This is often the better choice when you want an idiom, not a specific voice.

If you ask for a composer who isn't armed — Rachmaninoff, Debussy, Brahms, and many others have profile scaffolding but no corpus bars — Wolfgang won't quietly pretend. It tells you the support tier honestly:

- **Tier A** — large corpus and a full profile. The armed eleven.
- **Tier B** — a good corpus in a closely related style.
- **Tier C** — sparse data, but a profile exists.
- **Tier D** — unknown; only era and genre inference.

To turn a scaffolded composer into a Tier-A one, arm them from public-domain sources. That's a one-time setup step, covered in **[Arming Composers](ARMING-COMPOSERS.md)**.

## Understanding the output and the workspace

Two directories matter, and they have different jobs.

**`output/`** holds finished scores — the `.musicxml` (and sometimes compressed `.mxl`) files you open in MuseScore, plus `.mid` previews. This is the deliverable.

**`workspace/<piece-id>/`** holds everything about a piece in progress: the plan, the narrative arc, the themes, the per-section composition state, the research notes, and the running ledger of musical promises and debts. The single source of truth here is the **PieceGraph** — one structured file the whole pipeline reads from and writes to. Piece IDs look like `mozart-piano-sonata-gm-20260331`: a descriptive slug, the key, and the date.

Because all state lives on disk, **a piece can be interrupted and resumed.** If a long work stops partway, Wolfgang reads the PieceGraph back and picks up where it left off — already-composed phrases are skipped, not redone. Both `output/` and `workspace/` are gitignored, so your generated work stays local.

## Tips and troubleshooting

**`brief_insufficient` means the composer isn't armed.** This isn't a bug to work around — it's Wolfgang refusing to compose blind. The fix is to arm the composer (see [Arming Composers](ARMING-COMPOSERS.md)) or pick an armed one, not to bypass the check.

**Large works are a commitment.** A symphony is hundreds of separate phrase compositions. Wolfgang tells you the scale up front and checkpoints at movement boundaries. Start small to get a feel for it before asking for an hour of orchestral music.

**Gate overrides are honest, not hidden.** Sometimes a phrase is meant to be sparse — a held cadence, a moment of stillness — and the gate would otherwise flag it. When Wolfgang overrides a check, it records a real reason in the piece's revision history. If something sounds thin, that history tells you whether it was a choice or a slip.

**Trust the files, not the chat.** If you're unsure what state a piece is in, the workspace on disk is authoritative. The conversation is a summary; the PieceGraph is the truth.
