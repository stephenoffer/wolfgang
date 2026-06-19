<div align="center">
<pre>
╦ ╦╔═╗╦  ╔═╗╔═╗╔═╗╔╗╔╔═╗
║║║║ ║║  ╠╣ ║ ╦╠═╣║║║║ ╦
╚╩╝╚═╝╩═╝╚  ╚═╝╩ ╩╝╚╝╚═╝
</pre>
</div>

Wolfgang is a music-composition agent that runs inside [Claude Code](https://claude.com/claude-code). You describe a piece in plain language — *"a moonlit nocturne in the style of Chopin"*, *"a three-movement piano sonata in G minor"* — and it writes a full score, note by note, and hands you a MusicXML file you can open in MuseScore.

It is not a loop generator and not a black-box neural model. Every phrase is composed against real bars from a corpus of actual scores, then checked by a quality gate and a second listener before it stays in the piece.

## What makes it different

Most automatic music tools either stitch together pre-made fragments or sample from a model that has swallowed everything and explains nothing. Wolfgang takes a slower, more transparent path. Before it writes a single note for a phrase, it pulls a **composition brief**: real bars from the target composer's corpus, the statistical shape of their writing (how dense, how ornamented, how the left hand moves), and what the previous phrase left hanging. Claude composes the phrase by adapting that evidence — never copying it, never ignoring it.

Then the work gets checked. A **commit gate** blocks the usual failure modes of machine music: skeletal textures, photocopied accompaniment, surfaces that resemble none of the briefed examples. Anything it lets through still has to pass a **fresh-ears critic** — a separate reviewer that hears the assembled section without ever seeing why it was written that way, and judges the things a gate can't measure: whether the melody sings, whether the climax lands, whether it sounds like a person wrote it.

The whole piece lives in one file on disk (the PieceGraph) that every step reads from and writes to. That means a long work can be interrupted and resumed, and every decision — including every time the gate was overridden, and the honest reason why — is recorded rather than hidden.

Open the `.musicxml` files in [MuseScore](https://musescore.org) (free) to read and play them. The `.mid` files are quick playback previews.

## Quick start

You need Python 3.10+ and Claude Code. From the repo root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

That installs the engine and its dependencies (music21, lxml) plus the dev tools. Verify it worked:

```bash
.venv/bin/python -c "from scales import composition_brief; print('OK')"
```

Then open the project in Claude Code and ask for a piece:

```
/wolfgang a moonlit nocturne in the style of Chopin
```

Wolfgang plans the piece, shows you the form and the main themes, composes it section by section with a review pass on each, and assembles the result. The finished MusicXML and a MIDI preview land in `output/`; the working state for the piece lives in `workspace/<piece-id>/`.

For the full walkthrough — writing good prompts, the composition modes, resuming a piece — see the **[Usage Guide](docs/USAGE.md)**.

## What it can compose

You can ask for a fresh piece, or point it at existing music and transform that. All of these run through the same underlying algorithm; they differ in what gets locked in place.

| Mode | What it does |
|------|--------------|
| Compose from text | Write a new piece from a description (the default). |
| Variation | Vary an existing piece, keeping its themes and form. |
| Style transfer | Re-style an existing piece in a different idiom. |
| Reduce to piano | Condense an orchestral score to a playable piano version. |
| Orchestrate | Expand a piano piece into an orchestral one. |
| Continue | Extend an existing piece from where it stops. |

Pieces range from solo piano and string quartet up to multi-movement sonatas and orchestral works.

## The corpus

Wolfgang composes from evidence, so the corpus is the heart of it. Eleven composers ship **fully armed** — real bar-level data extracted from their scores, ready to brief a composition against:

| Composer | Bars | | Composer | Bars |
|----------|-----:|-|----------|-----:|
| Beethoven | 16,812 | | Monteverdi | 3,885 |
| Palestrina | 8,302 | | Haydn | 1,013 |
| Mozart | 6,987 | | Corelli | — |
| Bach | 4,893 | | Handel | — |
| Chopin | 4,691 | | Schubert | — |
| | | | Weber | — |

On top of the per-composer data, four **style packs** — classical, baroque, romantic, and renaissance — let you compose *in a style* rather than as one specific person, blending across the members of that style.

Around three dozen further composers (Rachmaninoff, Debussy, Brahms, Liszt, and more) ship with profile scaffolding but no corpus bars yet. Wolfgang is honest about this: ask for one and it tells you the support tier rather than quietly substituting someone else. You can arm any of them yourself from public-domain sources — see **[Arming Composers](docs/ARMING-COMPOSERS.md)**.

Backing all of this is a library of 24,615 canonical left-hand accompaniment patterns extracted from the corpus.

## How it works, briefly

```
/wolfgang "describe your piece"
        │
        ▼
   plan  ──►  form, themes, narrative arc, key scheme
        │
        ▼
   for each section:
        compose each phrase   (brief → sketch → write notes → quality gate)
        review the section     (fresh-ears critic, no rationale leaked)
        │
        ▼
   (concertos/symphonies) orchestrate
        │
        ▼
   assemble  ──►  MusicXML + MIDI in output/
```

The planning step decides the architecture; composition fills it in one phrase at a time, each phrase grounded in real corpus bars and checked at commit; review listens to whole sections and asks for targeted revisions. For the real explanation — the SCALES algorithm, what's in a brief, what the gate blocks and why — read **[How It Works](docs/HOW-IT-WORKS.md)**.

## Requirements and honest limitations

- **It runs inside Claude Code.** The Python engine and corpus ship in this repo, but the composing itself is done by Claude through the skills in `.claude/`. This is not a standalone command-line app or a web service.
- **Python 3.10 or newer.** Tested on 3.14.
- **MuseScore is optional** but recommended — it's how you view and play the `.musicxml` output.
- **Large works cost real time and tokens.** A four-movement symphony is hundreds of individual phrase compositions, each its own reasoning pass. Wolfgang tells you the scale before it starts. Short pieces are quick; big ones are a commitment.
- **Quality varies by corpus depth.** A Mozart or Beethoven request draws on thousands of real bars. An unarmed composer falls back to thinner inference, and the docs will tell you so.

## Documentation

- **[Usage Guide](docs/USAGE.md)** — install, your first piece, prompts, modes, output, troubleshooting.
- **[How It Works](docs/HOW-IT-WORKS.md)** — the algorithm, the brief, the gate, the critic.
- **[Arming Composers](docs/ARMING-COMPOSERS.md)** — add a composer, rebuild corpus data, contribute.
- **[CLAUDE.md](CLAUDE.md)** — the full engine and module reference (written for the agent; useful if you want every detail).

## License

<!-- TODO: no LICENSE file exists in the repo yet. Add one before publishing and update this section. -->

A license has not been chosen yet. Until one is added, all rights are reserved by the author.
