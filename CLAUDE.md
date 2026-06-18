# Wolfgang — Classical Music Generation Agent

## Project Overview
Wolfgang is a multi-skill Claude Code agent system that generates full orchestral scores from natural language descriptions, images, or references to existing works. Output is MusicXML (.musicxml/.mxl) importable into MuseScore.

## Architecture (v6 — corpus-armed agent composition)
- **7 Claude Code skills** in `.claude/skills/` + **3 subagents** in `.claude/agents/` (phrase-composer, music-critic, candidate-composer) — all read/write one PieceGraph
- **SCALES algorithm** — Sketch-Conditioned Alternating Ledger-guided Expansion Search
- **Single source of truth** — `PieceGraph` in `workspace/<piece-id>/piece_graph.json`
- **Python engine** in `tools/scales/` — brief provider, validator, commit gate, fallback realizer, assembler
- **Claude composes, corpus-armed** — by default Claude writes every note per phrase from a **composition brief** (real corpus exemplar bars + density/ornament targets + continuity), committed via `commit_agent_phrase_*` through a **blocking quality gate**. Engine realization is the fallback for unauthored phrases.
- **Unified modes** — compose, variation, style transfer, reduction, orchestration all use one algorithm

### Core Philosophy
**Music is art, not a template.** All artistic guidance is flexible. Only physical constraints (instrument ranges, hand spans, meter) are strict. The emotional story drives the notes. Gate overrides exist for honest artistic reasons and are logged, never hidden.

**Never compose blind.** Before writing notes for a phrase, Claude reads its brief (`get_composition_brief`): real corpus bars in shorthand, corpus density/ornament statistics, open ledger items, and the previous phrase's committed tail. **Adapt the exemplars — never copy verbatim, never ignore.**

**Sketch before detailing.** Claude writes SketchIR (anchors, harmonic rhythm, texture intent) from the brief, then composes the surface itself.

**Gates catch the mechanical; ears catch the dead.** The commit gate blocks skeletal density and photocopied accompaniment per phrase (corpus-derived thresholds); the fresh-ears `music-critic` subagent reviews each section it did NOT compose, armed with the `self_evaluate` discriminator report (texture_change_pct etc.).

**Carry expectations across time.** The ExpectationLedger tracks musical promises, debts, cooldowns, and locks — the system's working memory of unfinished musical business.

### Pipeline
```
User Request → /wolfgang (orchestrator: plans, dispatches, holds summaries only)
  → /w-plan → PieceContract + StyleDNA + NarrativeArc + FormGraph + MotifBank
  → per section:
      /w-compose per phrase  (phrase-composer subagent: brief mandatory →
                              SketchIR → adapt exemplars → gated commit;
                              max 3 attempts; candidate panel on theme
                              statements/climaxes)
      /w-review              (music-critic subagent, fresh ears +
                              self_evaluate discriminator report)
  → orchestration phase      (concertos/symphonies: piano-core → orchestrate_section)
  → /w-assemble → MusicXML + MIDI preview
```

### Composition Modes (all one algorithm, different contracts)
| Mode | Description | Lock Policy |
|------|-------------|-------------|
| `compose_from_text` | Fresh composition from description | No locks |
| `variation` | Vary an existing piece | High theme/form locks |
| `style_transfer` | Restyle a piece | Medium melody, high structure locks |
| `reduce_to_piano` | Orchestral → piano (SABRE engine) | High coverage locks |
| `orchestrate` | Piano → orchestra expansion | High identity locks |
| `continue_piece` | Continue an existing piece | Ledger carries forward |

### Key Design Principles
1. **Claude composes from corpus evidence; the engine provides, gates, and falls back.** Briefs put real notes in front of Claude before it writes any.
2. **Layer-based piano IR, not SATB.** principal_line, bass_foundation, response_layer, counter_reply, ornamental_surface.
3. **Every note carries a role.** structural, passing, neighbor, appoggiatura, suspension, arpeggiated_fill, pedal_support, ornamental.
4. **Blocking commit gate, calibrated on the corpus.** Brief-receipt requirement (a phrase cannot commit unless its brief was fetched; an empty-exemplar brief blocks as `brief_insufficient`), density floors (½ corpus median per texture; a hard generic floor when the composer has no stats), photocopied-accompaniment detection, and `composed_blind` corpus-alignment (a surface that resembles no briefed exemplar is blocked). Waivable with a logged reason (≥20 chars, ≤1 blocking check per commit); no `skip_gate`. A real corpus bar passes its own composer's gate.
5. **ExpectationLedger enforces long-range coherence.** Promises, debts, cooldowns, prohibitions, identity locks.
6. **Expression survives to the score.** Slurs, ties, ornaments, hairpins, dynamics flow shorthand → LayerIR → EventIR → MusicXML spanners.
7. **Context isolation for scale.** Orchestrator holds plans/summaries; phrase-composer subagents hold note-level work; music-critic reviews with fresh ears (no rationale leakage). Symphonies iterate movement → section → phrase with per-commit checkpoints.

## Key Entry Point
- `/wolfgang <description>` — the master orchestrator skill

## Skills (7 total)
| Skill | Purpose |
|-------|---------|
| `/wolfgang` | Master orchestrator — parses request, determines mode, runs pipeline |
| `/w-plan` | Unified planning: contract, style, narrative, form, motifs |
| `/w-compose` | Per-phrase composition end-to-end: brief mandatory → SketchIR → Claude composes every note → gated commit; engine realization = fallback |
| `/w-review` | Fresh-ears review (music-critic) of what gates can't hear; RevisionScripts |
| `/w-assemble` | Assembly → MusicXML + audio preview |
| `/w-interpret` | Translate images/concepts/references → musical parameters |
| `/w-research` | Web search for unknown composers, build temporary profiles |

Shared craft rules (shorthand grammar, gate loop, adapt toolkit, canonical
tool-call snippets) live in `.claude/skills/w-compose/references/note-writing-craft.md`
— skills and agents point there, never restate.

## Python Package: `tools/scales/`

**Packaging.** The source root is `tools/`; `scales` (and the corpus-build
`scripts`) are installable top-level packages declared in the repo-root
`pyproject.toml`. Install once with `.venv/bin/python -m pip install -e ".[dev]"`
(pulls in `music21`, `lxml`, plus `ruff` + `pytest`). After that, `from scales....`
imports and `python -m scripts.<name>` work from anywhere — no `sys.path` shims.
Lint/format with `ruff check tools/` and `ruff format tools/`; run the unit suite
with `pytest` (the corpus-dependent calibration harness is deselected by default —
run it explicitly with `pytest -m calibration`).

### Core Data Models (`models.py`)
| Model | Purpose |
|-------|---------|
| `PieceContract` | Immutable intent document — mode, style, locks, constraints |
| `StyleDNA` | Compiled style profile — NOT prose, all numeric/structural |
| `PieceGraph` | Single source of truth — all state in one graph |
| `ExpectationLedger` | Musical promises, debts, cooldowns, locks |
| `SketchIR` | What Claude writes — structural content, not final notes |
| `LayerIR` | Role-based layers replacing SATB — every note has a role tag |
| `EventIR` | Final merged event stream for engraving |
| `PerformanceIR` | Separate interpretation layer (microtiming, rubato, pedal) |
| `CandidateNode` | One candidate in beam search with multi-dimensional scores |
| `RevisionScript` | Structured edit operations Claude writes instead of re-composing |

### Agent Composition Layer (the default path)
| Module | Purpose |
|--------|---------|
| `composition_brief.py` | Build per-phrase briefs — ALL levels of corpus material, scoped to the phrase: up to 8 exemplar bars (transposed shorthand), per-texture density stats, composer **fingerprints**, phrase-scoped **doctrine** (cadence script, ornament intent, breathing, harmonic color, melody priors), **multi-level patterns** (phrase-shape arc, cadence pattern, texture transitions, LH vocabulary), composer-specific discriminator bands from `corpus_profile.json`, ledger + continuity |
| `corpus_metrics.py` | Discriminator metrics (texture_change_pct, density_cv, events_per_bar, …) over the **bar-record format** — the shared yardstick run on BOTH corpus bars and a generated piece (assembled → analyze_score_bars), so piece-vs-corpus z-scores are apples-to-apples |
| `anti_skip.py` | `composed_blind` detector — committed melody's rhythm+interval signature vs briefed exemplars; fires if it resembles none. Wired into the commit gate as a **blocking** check (waivable). Briefed exemplars + a brief receipt persisted on the phrase at brief time |
| `commit_gate.py` | Blocking quality gate at commit: brief-receipt requirement (`brief_not_fetched`/`brief_insufficient`), density floors — **per-bar against each bar's own texture**, blocking only when a majority (≥60%) of bars are skeletal so real phrases that mix textures / thin at a cadence pass (hard generic floor when corpus stats absent), figuration_flat, **composed_blind** (corpus alignment), anti-pattern + musicality warns; waivers require a real reason (≥20 chars) and at most one blocking check per commit; overrides logged to revision history. There is **no `skip_gate`** |
| `style_registry.py` | Compose **in a style, not as one composer** — maps styles/genres → member composers (armed-only), synonyms, `style__<name>` ids, `resolve_reference()` (composer / style / unknown). The corpus primitives in composition_brief detect `style__` and aggregate over members (exemplars interleaved across composers, fingerprints unioned, profile/density aggregated). Unknown composers resolve honestly (no silent substitution) and point at `acquire_composer.py` or the closest armed style |
| `musicality.py` | Symbolic metrics over LayerIR: rhythmic variety, interval profile, figuration richness, contour, rest ratio |
| `performance_renderer.py` | Populate PerformanceIR per phrase (dynamic curves, cadential rubato, pedal, voicing emphasis, agogic microtiming) — deterministic, derived on the fly |
| `orchestration_planner.py` | Idiomatic piano-core → orchestra: register-aware assignment, climax doublings (flute 8va at f+), divided inner voices, wind pads, range clamping |
| `surface_composer.py` | Phrase-level, context-driven composition — retrieves phrase prototypes + gesture families, plans gesture slots between anchors, co-composes melody + accompaniment per slot, integrates cadences and motif realization. The v6 engine-realization path (richer than the bar-by-bar fallback) |
| `context_router.py` | Routes a phrase's context query to the right retrieval banks (phrase / gesture / cadence / pattern), assembling a `PhraseContext` |
| `context_utilization.py` | Computes the corpus-utilization report (which briefed evidence the commit actually used) — embedded in `self_evaluate` |
| `craft_checker.py` | Validates note-writing craft rules (slur/tie grammar, articulation validity) as part of the commit path |
| `review_style_gate.py` | Post-realization style gate — assembles a section, compares metrics to StyleDNA-derived targets (via `style_analyzer` + `style_comparator`), builds a RevisionScript; exposed as `run_style_review_section` |
| `corpus_bar_retriever.py` | General-purpose lazy-loaded access to corpus bar records, indexed by texture/key/density |
| `pattern_retriever.py` | Accesses the 24,615 canonical LH patterns from `pattern_library/` |
| `corpus_adapter.py` | Adapts retrieved corpus bars to the phrase (transposition, re-harmonization, density adjustment) for briefs |
| `harmonic_solver.py` | Solves chord-tone / voice-leading constraints for the surface composer |
| `donor_strategy.py` | Selects donor measures for harmonic/melodic material during phrase realization |
| `motif_realization.py` | Realizes motif placements into note events (transform ops, scale-degree mapping) |
| `style_analyzer.py` | Quantitative style fingerprints from a score (≈25 metrics) — guardrail for gross statistical failures; used by `review_style_gate` and the feedback loop |
| `style_comparator.py` | Compares a composed section's metrics against StyleDNA targets — per-metric divergence, pass/fail, fix suggestions |
| `.claude/agents/` | phrase-composer (sonnet, workhorse), music-critic (opus, fresh ears + judge), candidate-composer (panel lens via `commit_candidate_phrase` → `promote_candidate`) |

### SCALES Algorithm (engine fallback)
| Module | Purpose |
|--------|---------|
| `scales.py` | Top-level tool surface — init_workspace, compile_style, build_form_graph, get_composition_brief, run_agent_section_briefs, commit_agent_phrase_*, commit_candidate_phrase / list_phrase_candidates / promote_candidate (panel), get_section_status, get_phrase_continuity, self_evaluate (now embeds `corpus_divergence` + `authoring`), `compare_to_corpus` (post-gen z-scores vs the composer's own distribution; drives the bounded auto-revision loop), orchestrate_section + assemble_orchestration, run_scales_section (persists CrossScaleLedger across runs/movements) |
| `sketch_proposer.py` | Generate K sketch candidates from PhraseSlot + StyleDNA + corpus |
| `realizer.py` | Style-conditioned realization: SketchIR → LayerIR |
| `reducer.py` | Reduce surface back to skeleton for round-trip comparison |
| `candidate_scorer.py` | Multi-dimensional scoring (style, sketch, expectations, novelty, continuity, locks) |
| `section_search.py` | Beam search / Viterbi over section phrase paths |
| `cross_scale_ledger.py` | Persists the CrossScaleLedger (promises/debts/locks) across `run_scales_section` runs and movement boundaries |

### Retrieval Banks
| Module | Purpose |
|--------|---------|
| `phrase_bank.py` | Phrase-level retrieval (2-16 bars) from corpus |
| `gesture_bank.py` | Idiomatic gesture retrieval by function/texture/density |
| `cadence_bank.py` | Cadential realization retrieval |
| `transition_bank.py` | Phrase-to-phrase transition scoring |
| `performance_bank.py` | Expressive rendering patterns |

### SABRE (Reduction Engine)
| Module | Purpose |
|--------|---------|
| `sabre.py` | Salience-Aware Bimanual Reduction Engine |
| `role_decomposer.py` | Decompose orchestral score into role graph |
| `bimanual_packer.py` | Optimize RH/LH packing with playability constraints |

### Style & Context
| Module | Purpose |
|--------|---------|
| `context_compiler.py` | 19-pass offline compilation: markdown → ComposerPack |
| `style_resolver.py` | Blend/merge StyleDNA with axis ownership + overlay loading |

### Corpus Feedback Loop (`feedback/`)
| Module | Purpose |
|--------|---------|
| `evidence_extractor.py` | Extract EvidenceBundle from scores (wraps style_analyzer + build_full_corpus) |
| `claim_registry.py` | Registry of measurable claims bootstrapped from compiled packs |
| `claim_matcher.py` | Match evidence against claims, update support/contradiction counts |
| `overlay_builder.py` | Promote recurring evidence into overlay delta JSONs |
| `conflict_resolver.py` | Detect contradictions, generate conflict reports |

### Assembly & Utilities
| Module | Purpose |
|--------|---------|
| `direct_compose.py` | Claude shorthand → LayerIR (full grammar: note-writing-craft.md §8) |
| `assembler.py` | LayerIR → MusicXML via music21 — dynamics, articulations, ornaments, ties, text expressions, (spanner pass) slurs + hairpins, plus notational performance marks (rit. / a tempo / con pedale) |
| `midi_renderer.py` | Humanized MIDI preview — interpolated velocity curves, melody voicing emphasis, cadential rubato (real tempo marks), agogic microtiming, audible sustain; this is what the music-critic hears |
| `music_io.py` | MusicXML/MIDI parsing helpers |
| `piece_graph.py` | PieceGraph CRUD + patch operations |
| `patch_engine.py` | Applies structured RevisionScript edit operations to the PieceGraph |
| `expectation_ledger.py` | Musical promise/debt/cooldown tracking |
| `validator.py` | Physical constraints (range, span, meter, voice leading) — consolidates the former standalone range/voice-leading checkers |
| `pitch.py` | Pitch/interval/key/chord utilities |
| `duration.py` | Duration/meter utilities |

### Three-Layer Context Stack
| Layer | Location | Update Cadence |
|-------|----------|----------------|
| **1. Canonical Doctrine** | `.claude/context/` | Human-curated, stable — never machine-modified |
| **2. Evidence Overlays** | `tools/context_overlays/{composer}/` | Machine-updated from corpus feedback |
| **3. Live Memory** | `tools/reference_index/`, `tools/pattern_library/` | Updates on every corpus ingestion |

### Corpus Data
| Location | Content |
|----------|---------|
| `tools/reference_index/` | Bar indexes, window indexes, gesture banks, phrase catalogs per composer (all 11 — rebuild the index layer from bars with `scripts/build_corpus_indexes.py`) |
| `tools/pattern_library/` | 24,615 canonical LH patterns + per-composer LH-texture transition matrices |
| `tools/texture_templates/` | Per-composer texture analysis |
| `tools/compiled_packs/` | Compiled ComposerPacks (context_compiler) + `density_stats.json` + `corpus_profile.json` (per-composer metric **distributions** for piece-vs-corpus comparison — built by `scripts/build_corpus_profiles.py`) |
| `tools/context_overlays/` | Evidence-backed overlay deltas (auto-loaded by style_resolver) |
| `tools/context_evidence/` | Claim registries, support stats, conflict reports per composer |

**Rebuilding corpus artifacts** (all derive from bar records — no raw scores needed): `python3 -m scripts.build_corpus_indexes` (phrase/gesture/window indexes + transition matrices, all 11 composers) then `python3 -m scripts.build_corpus_profiles` (per-composer corpus_profile distributions) then `python3 -m scripts.build_style_profiles` (aggregated profiles + density stats per **style**, written under `compiled_packs/style__<name>/`). Arm a missing composer with `python3 -m scripts.acquire_composer <name>` (music21 local + allowlisted KernScores web). Use `.venv/bin/python` for anything that assembles/parses scores (music21).

### Context Files
| Location | Content |
|----------|---------|
| `.claude/context/general/` | Shared music theory |
| `.claude/context/<genre>/` | Genre-specific harmony, orchestration, forms |
| `.claude/context/<genre>/composer-profiles/` | 9-file composer directories |

## Conventions
- **Artistic guidance, not rigid rules**: Use "typically", "aim for", "consider" for artistic choices
- **Music is ONE fabric**: Never compose texture, melody, harmony, rhythm as separate layers
- **PieceGraph is the single source of truth**: All skills read/write `workspace/<piece-id>/piece_graph.json`
- **Default path**: For each phrase, Claude reads the **composition brief** (`get_composition_brief` — real corpus exemplars + density/ornament targets + continuity), writes **SketchIR**, then **composes every final note** by adapting the exemplars and commits via `commit_agent_phrase_*`. The **commit gate** blocks skeletal density and photocopied accompaniment; waive a named artistic check with `allow=[{"check": ..., "reason": ...}]` (logged).
- **Engine fallback**: Phrases Claude doesn't author are realized by `run_scales_section`, which **never overwrites** `agent_authored` phrases.
- **Delegation**: In orchestrated runs, phrase composition happens in `phrase-composer` subagents and section review in the fresh-ears `music-critic` (give it only paths + the `self_evaluate` report — never the rationale). Use `get_section_status`/`get_phrase_continuity` for state, not whole-graph dumps.
- **Large works**: movement → section → phrase loops; per-commit checkpoints; piano-core first, then `orchestrate_section` for concertos/symphonies.
- **Section IDs**: `m<movement>_<section_name>` (e.g., `m1_expo_pt`, `m2_a`)
- **Phrase IDs**: `<section_id>_p<number>` (e.g., `m1_a_p1`)
- **Piece IDs**: `<descriptive-slug>-<key>-<date>` (e.g., `winter-concerto-dm-20260321`)
- **Python**: use music21 for all music parsing/conversion
- **Composer profiles**: Load via `compile_style()`, not raw markdown
- **Corpus data**: Accessed via retrieval banks (PhraseBank, GestureBank, etc.), not raw JSON
- **Corpus feedback**: New scores should be ingested via `tools/scripts/ingest_with_feedback.py` to update both retrieval indexes and context overlays
- **Evidence-backed overlays**: Machine-generated deltas in `tools/context_overlays/` are auto-loaded by style_resolver — never edit canonical markdown from code
