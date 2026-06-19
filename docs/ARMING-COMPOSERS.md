# Arming Composers and Contributing

Wolfgang composes from real bars. A composer is only as good as the corpus behind them, so the most useful thing you can contribute is a newly **armed** composer — one with genuine bar-level data, not just a profile shell. This guide covers arming a composer, rebuilding the corpus data, ingesting your own scores, and the day-to-day developer workflow.

All commands assume you've installed the project (`./.venv/bin/python -m pip install -e ".[dev]"`) and run from the repo root. Use `.venv/bin/python` for anything that parses or assembles scores, since that's where music21 lives.

## What "armed" means

Eleven composers ship armed: Bach, Beethoven, Chopin, Corelli, Handel, Haydn, Monteverdi, Mozart, Palestrina, Schubert, and Weber. Armed means there's bar-level data in `tools/reference_index/<composer>/` and compiled statistics in `tools/compiled_packs/<composer>/`. That's what lets a composition brief show real exemplar bars and real density numbers.

Around three dozen other composers have a profile scaffold in `tools/compiled_packs/` but no corpus bars. They're recognized names with stylistic notes, but they can't yet supply exemplars — which is why a request for one of them reports a lower support tier instead of composing blind. Arming them turns the scaffold into the real thing.

Check any composer's status:

```bash
python3 -m scripts.acquire_composer --status mozart
```

That prints the tier, whether they're armed, the bar count, and whether the density stats and corpus profile exist.

## Arming a composer

One command does the whole job — it finds scores, extracts bars, and builds the indexes, profiles, and density stats:

```bash
python3 -m scripts.acquire_composer haydn
```

It looks first in music21's built-in corpus (local, no network) and then, if needed, falls back to an allowlisted set of public-domain sources (KernScores / HumdrumOrg), validating what it pulls. Useful options:

- `--no-web` — use only the local music21 corpus; never touch the network.
- `--max-files N` — cap how many score files to ingest (default 60).
- `--status` — just report the tier and exit, without acquiring anything.

```bash
python3 -m scripts.acquire_composer clementi --max-files 40
python3 -m scripts.acquire_composer haydn --no-web
```

After this finishes, that composer can be briefed against real bars, and `/wolfgang ... in the style of <composer>` will use them.

## Rebuilding corpus artifacts

Everything downstream of the raw bars derives from those bars, so you can always rebuild the index and statistics layers without re-downloading anything. The canonical order is indexes, then per-composer profiles, then style profiles:

```bash
python3 -m scripts.build_corpus_indexes        # phrase / gesture / window indexes + transition matrices
python3 -m scripts.build_corpus_profiles       # per-composer metric distributions (corpus_profile.json)
python3 -m scripts.build_style_profiles        # aggregated profiles + density stats per style
```

What each one produces:

- **`build_corpus_indexes`** — the retrieval layer: phrase catalogs, gesture banks, window indexes, and per-composer left-hand transition matrices. Pass specific composer names to limit it (`build_corpus_indexes mozart bach`), or `--force` to rebuild composers that already have indexes.
- **`build_corpus_profiles`** — the statistical distributions (mean, spread, percentiles per metric) that let the system compare a generated piece to the composer's real spread with z-scores. Writes `corpus_profile.json` into each composer's compiled pack.
- **`build_style_profiles`** — pools the bars of every member of a style (classical, baroque, romantic, renaissance) into aggregate distributions under `compiled_packs/style__<name>/`, which is what powers composing *in a style* rather than as one person.

## Ingesting your own scores

If you have scores you want folded into the corpus — and you want the context layer updated too, not just the indexes — use the feedback-loop ingestion path:

```bash
python3 tools/scripts/ingest_with_feedback.py path/to/score.musicxml mozart
python3 tools/scripts/ingest_with_feedback.py --batch path/to/folder mozart
```

This extracts musical evidence, matches it against the registry of measurable claims about that composer, promotes recurring evidence into overlay deltas, and flags contradictions — extending both the retrieval indexes and the evidence overlays in one pass.

## The three-layer context stack

When you contribute, it helps to know which layer you're touching, because the rules differ:

1. **Canonical doctrine** (`.claude/context/`) — human-curated, stable music knowledge. Never modified by code. Edit by hand, thoughtfully.
2. **Evidence overlays** (`tools/context_overlays/<composer>/`) — machine-generated deltas from the corpus feedback loop, auto-loaded at composition time. Don't hand-edit these, and never write to the canonical markdown from code — that's what the overlay layer is for.
3. **Live memory** (`tools/reference_index/`, `tools/pattern_library/`) — rebuilt on every corpus ingestion.

The one rule to internalize: machine-discovered facts go into overlays, not into the canonical doctrine. The canonical layer stays a clean, human-owned source of truth.

## Developer workflow

The engine is the `scales` package under `tools/`, with corpus-build tooling in `scripts`. Standard loop:

```bash
ruff check tools/        # lint
ruff format tools/       # format
pytest                   # unit tests
```

The test suite covers the parts that have a measurable contract: the commit gate's enforcement, the discriminator metrics, the anti-blind detector, shorthand parsing, the expectation ledger, narrative curves, performance rendering, and style resolution.

One suite is deselected by default — the corpus calibration harness, which checks that real corpus bars pass their own composer's gate (the target is around 89%). It's slow and depends on the corpus being present, so run it explicitly when you've touched the gate or the corpus:

```bash
pytest -m calibration
```

## Where to read more

[CLAUDE.md](../CLAUDE.md) is the full module map — every file in `scales`, the data models, the corpus layout, and how the pieces fit together. It's the reference to keep open while working on the engine.
