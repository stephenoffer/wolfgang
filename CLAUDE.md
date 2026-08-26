# Wolfgang — Classical Music Generation Agent

## Project Overview
Wolfgang is a multi-skill Claude Code agent system that generates full orchestral scores from natural language descriptions, images, or references to existing works. Output is MusicXML (.musicxml/.mxl) importable into MuseScore.

## Architecture (v6 — corpus-armed agent composition)
- **7 Claude Code skills** in `.claude/skills/` + **3 subagents** in `.claude/agents/` (phrase-composer, music-critic, candidate-composer) — all read/write one PieceGraph
- **SCALES algorithm** — Sketch-Conditioned Alternating Ledger-guided Expansion Search
- **Single source of truth** — `PieceGraph` in `workspace/<piece-id>/piece_graph.json`
- **Python engine** in `tools/scales/` — brief provider, validator, commit gate, fallback realizer, assembler
- **Claude composes, corpus-armed** — by default Claude writes every note per phrase from a **composition brief** (real corpus exemplar bars + density/ornament targets + continuity) and from its **own whole-score study** (see `reference_study.py`), committed via `commit_agent_phrase_*`. The commit gate blocks **only physical violations** (meter/range/span); corpus-alignment is advisory. Engine realization is the fallback for unauthored phrases.
- **Unified modes** — compose, variation, style transfer, reduction, orchestration all use one algorithm

### Core Philosophy
**Music is art, not a template.** All artistic guidance is flexible. Only physical constraints (instrument ranges, hand spans, meter) are strict. The emotional story drives the notes. Gate overrides exist for honest artistic reasons and are logged, never hidden.

**Study scores like a human, then compose freely.** At plan time Claude reads **whole reference scores** (`list_reference_scores` / `get_reference_score`) and writes its **own analysis** (`save_reference_study`) — form, themes, harmonic language, what makes them work. That understanding feeds every phrase brief (`get_composition_brief`: real corpus bars in shorthand, density/ornament stats, ledger, continuity, and the "WHAT YOU LEARNED FROM THE SCORES" section). From there Claude has **creative liberty**: invent freely or adapt the exemplars — never copy verbatim. The agent chooses its own harmony; the corpus only informs.

**Sketch before detailing.** Claude writes SketchIR (anchors, harmonic rhythm, texture intent) from the brief, then composes the surface itself.

**Only physics is strict; ears judge the rest.** The commit gate blocks only physical violations (meter/range/span, plus same-voice overlap). Skeletal density, photocopied accompaniment, and `composed_blind` are **advisory** signals, never auto-blocks — the agent may invent away from the corpus. At section level, `_section_gate` fails only on the musical_ear's `error`-severity findings — a bar holding more beats than its meter, a note outside the instrument's range — read back off the **assembled score**. Those are not artistic judgements, and every detector was falsified against real sonatas and mazurkas (zero errors on nine of them) before being allowed to block. The fresh-ears `music-critic` subagent reviews each section it did NOT compose, armed with the `self_evaluate` discriminator report, and is the sole driver of *artistic* revision. Corpus z-scores are a diagnostic the critic may read, never a revision target ("metric whack-a-mole" is rejected).

**Falsify every rule against real scores.** Before any check is allowed to block or even warn at scale, ask whether it would reject canonical music, and test it. This has caught: a same-octave cross-relation "error" that fires 45 times across nine real sonatas; an underfull-bar "error" that real engraved scores trip 22 times (repeat structures, written-out partial bars); a flat-density warning that fires on 27% of real Palestrina, whose Renaissance polyphony is *defined* by even motion.

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
4. **Commit gate blocks only physical constraints; corpus checks are advisory.** Meter (and range/span in the validator) are strict and non-waivable. Brief-receipt is still enforced (studying references is required: `brief_not_fetched`/`brief_insufficient`), but density floors, photocopied-accompaniment, and `composed_blind` corpus-alignment now **warn** rather than block — the agent has creative liberty to invent away from the corpus, and the fresh-ears critic judges the result by ear. No `skip_gate`. A real corpus bar passes its own composer's gate.
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
| `anti_skip.py` | `composed_blind` detector — committed melody's rhythm+interval signature vs briefed exemplars; fires if it resembles none. Wired into the commit gate as an **advisory** check (warns; the critic judges invention by ear). Briefed exemplars + a brief receipt persisted on the phrase at brief time |
| `reference_study.py` | Whole-score study — `list_reference_scores` (enumerate complete reference pieces per composer/style) + `reconstruct_score` (one full piece in readable shorthand with per-bar roman/function/texture). Lets the agent read real scores end-to-end at plan time and write its own analysis (`save_reference_study` → `PieceGraph.reference_studies`), fed forward into every phrase brief |
| `commit_gate.py` | Commit gate: blocks **only physical** violations (`meter`; range/span in validator). Brief-receipt requirement (`brief_not_fetched`/`brief_insufficient`) still enforced. Density floors, figuration_flat, **composed_blind**, and anti-pattern/musicality checks are all **advisory warnings** the fresh-ears critic weighs — never auto-blocks. The agent has creative liberty to invent away from the corpus. There is **no `skip_gate`** |
| `style_registry.py` | Compose **in a style, not as one composer** — maps styles/genres → member composers (armed-only), synonyms, `style__<name>` ids, `resolve_reference()` (composer / style / unknown). The corpus primitives in composition_brief detect `style__` and aggregate over members (exemplars interleaved across composers, fingerprints unioned, profile/density aggregated). Unknown composers resolve honestly (no silent substitution) and point at `acquire_composer.py` or the closest armed style |
| `musicality.py` | Symbolic metrics over LayerIR: rhythmic variety, interval profile, figuration richness, contour, rest ratio |
| `performance_renderer.py` | Populate PerformanceIR per phrase (dynamic curves, cadential rubato, pedal, voicing emphasis, agogic microtiming) — deterministic, derived on the fly |
| `orchestration_planner.py` | Idiomatic piano-core → orchestra: register-aware assignment, climax doublings (flute 8va at f+), divided inner voices, wind pads, range clamping |
| `surface_composer.py` | Phrase-level, context-driven composition — retrieves phrase prototypes + gesture families, plans gesture slots between anchors, co-composes melody + accompaniment per slot, integrates cadences and motif realization. The v6 engine-realization path (richer than the bar-by-bar fallback) |
| `context_router.py` | Routes a phrase's context query to the right retrieval banks (phrase / gesture / cadence / pattern), assembling a `PhraseContext` |
| `context_utilization.py` | Computes the corpus-utilization report (which briefed evidence the commit actually used) — embedded in `self_evaluate` |
| `score_realism.py` | **The read-back audit for "this reads as machine-made".** 17 detectors over the ASSEMBLED score — cadence-formula reuse, scalar melody, accompaniment monoculture, notation spam, articulation/tie/dynamic/voicing poverty, uniform phrase lengths, identical phrase openings, texture stasis, out-of-period register — plus a notation census (marks per bar vs the real-corpus 0.11-5.71, median 1.58). **Advisory without exception**: every threshold was set by measuring 60 canonical Mozart/Beethoven/Chopin movements and each detector's docstring states its false-positive rate. Wired into `self_evaluate.realism` and surfaced as `_section_gate` advisories |
| `expression_enricher.py` | Non-destructive engraver's pass over a committed LayerIR — fills only notation fields the composer left `None` (never a pitch or a duration), period-gated (no pedal for Bach, no dynamics for Palestrina). Called from `_engrave_phrase` after the gate passes; its report is stored on the phrase so a reviewer can tell the engraver's marks from the composer's |
| `ornament_realization.py` | Ornaments made AUDIBLE in the preview — trills take their speed from the tempo and start on the upper note for baroque/classical, turns and mordents get real neighbours from the key, appoggiatura and acciaccatura sound different. They were engraved and then silent: a `tr` played one plain note |
| `counterpoint.py` | Parallel 5ths/8ves in the real texture, hidden octaves into cadences, doubled leading tone, unresolved 7ths, voice crossing, spacing, voice independence |
| `voicing.py` | Spacing / register / hand-span / thin-texture analysis, plus `texture_runs()` — the accompaniment idiom's actual run lengths |
| `cadence_analysis.py` | Reads each cadence from the NOTES and compares it to the planned `slot.cadence_target` — which nothing checked before |
| `craft_checker.py` | Validates note-writing craft rules (slur/tie grammar, articulation validity) as part of the commit path |
| `expression_enricher.py` | **The engraver's pass**, run on every agent commit inside `_gated_commit`. Fills in slurs, articulation, hairpins, dynamics, pedal and closing marks the composer left blank — and *only* what was left blank, so the agent stays the author. Period-aware (`ENGRAVING_STYLES`); reports exactly what it added so a reviewer can separate engraver from composer. It never changes a pitch or a duration, which is why it does not add ties |
| `score_realism.py` | **The read-back audit** for "this sounds machine-made", run inside `self_evaluate` off the assembled score. 16 detectors for formula, uniformity and notational poverty — cadence-formula reuse, register stasis, accompaniment monoculture, scalar overuse, notation spam, articulation/tie absence. `musical_ear` answers "is anything broken"; this answers "does this read as engraved music". **Advisory without exception**: every threshold was set from the measured distribution over 26 canonical movements, and `tests/test_score_realism_calibration.py` fails if any detector exceeds its documented false-positive rate on them |
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
The note generators below (`sketch_proposer`, `realizer`, `surface_composer`) are **fallback-only** — they run inside `run_scales_section` for phrases Claude did not author, and never overwrite an `agent_authored` phrase. The default flow always routes note-writing through the agent.

| Module | Purpose |
|--------|---------|
| `scales.py` | Top-level tool surface — init_workspace, compile_style, `list_reference_scores` / `get_reference_score` / `save_reference_study` (whole-score study), build_form_graph, get_composition_brief, run_agent_section_briefs, commit_agent_phrase_*, commit_candidate_phrase / list_phrase_candidates / promote_candidate (panel), get_section_status, get_phrase_continuity, self_evaluate (embeds `corpus_divergence` + `authoring`), `compare_to_corpus` (post-gen z-scores vs the composer's own distribution — a **diagnostic** the critic may read, never a revision driver), orchestrate_section + assemble_orchestration, run_scales_section (persists CrossScaleLedger across runs/movements) |
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
| `transition_bank.py` | Phrase-to-phrase transition scoring. **Currently called by nothing** — the brief reaches the same corpus data through `PhraseBank`. Its texture-transition loader is shared (`style_registry.load_transition_matrix`) |
| `performance_bank.py` | Hand-written expressive-rendering templates. **Currently called by nothing** — superseded by `performance_renderer`, which derives the same shapes from the period profile |

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
| `direct_compose.py` | Claude shorthand → LayerIR (full grammar: note-writing-craft.md §8) — tuplets (`trip_e`…), 64ths, trailing-dot durations (`h.`), pickup bars (`'pickup': True`), `//` two-voice-per-hand, and melodic-context note roles |
| `assembler.py` | LayerIR → MusicXML via music21 — dynamics, articulations, ornaments, ties, text expressions, (spanner pass) slurs + hairpins, plus notational performance marks (rit. / a tempo / con pedale) |
| `midi_renderer.py` | Humanized MIDI preview — interpolated velocity curves, melody voicing emphasis, cadential rubato (real tempo marks), agogic microtiming, audible sustain; this is what the music-critic hears |
| `music_io.py` | MusicXML/MIDI parsing helpers |
| `piece_graph.py` | PieceGraph CRUD + patch operations |
| `patch_engine.py` | Applies structured RevisionScript edit operations to the PieceGraph |
| `expectation_ledger.py` | Musical promise/debt/cooldown tracking |
| `validator.py` | Physical constraints (range, span, meter, voice leading) — consolidates the former standalone range/voice-leading checkers |
| `harmony_analysis.py` | **The one harmonic analyzer and Roman-numeral parser.** Duration- and metrically-weighted chord fitting with quality/diatonic priors and a Viterbi pass for harmonic inertia (`analyze_bar` — one entry per distinct harmony); `parse_roman` / `spell_roman` round-trip for all 12 degrees × 9 qualities × every inversion, so nothing hand-maintains a symbol table. Replaced pitch-set collection, which read three beats of plain C major as `I7` and labelled 42.6% of the corpus "chromatic" |
| `pitch.py` | Pitch/interval/key/chord utilities |
| `duration.py` | Duration/meter utilities — exact `Fraction` values so triplets and 32nds survive to MusicXML |

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

**Rebuilding corpus artifacts.** Two layers, in order.

*Bar records* (needs raw scores; only when the extractor changes):
`.venv/bin/python -m scripts.build_full_corpus --reference` (mozart/beethoven/chopin from
`reference_scores/`), `--music21 bach haydn palestrina monteverdi`, and
`--local <composer> <dir>` for web-acquired sources cached under
`reference_scores/_fetch_<composer>/`.

*Derived layers* (from bar records alone): `.venv/bin/python -m scripts.build_corpus_indexes`
(phrase/gesture/window indexes + transition matrices) then
`.venv/bin/python -m scripts.build_corpus_profiles` (per-composer distributions) then
`.venv/bin/python -m scripts.build_style_profiles` (per-**style** aggregates under
`compiled_packs/style__<name>/`) then `.venv/bin/python -m scripts.build_progression_model`.
Pass `--force` to `build_corpus_indexes` to overwrite existing per-artifact files;
without it, only missing artifacts are written (the flagship composers are no
longer skipped outright — that let a stale, cross-contaminated phrase catalog
survive corpus rebuilds).

Arm a missing composer with `.venv/bin/python -m scripts.acquire_composer <name>` (music21
local + allowlisted KernScores/Mutopia web). A composer needs **≥3 distinct source
movements and real harmonic coverage** to count as armed; `composer_coverage_tier`
reports tier C for anything thinner rather than pretending it can teach a voice.
Use `.venv/bin/python` for anything that assembles/parses scores (music21).

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
- **Default path**: For each phrase, Claude reads the **composition brief** (`get_composition_brief` — motifs, creative intent, chord frame, real corpus exemplars, density/ornament targets, continuity), writes **SketchIR**, then **composes every final note** and commits via `commit_agent_phrase_*`. The **commit gate blocks only physical violations** (see above); skeletal density and photocopied accompaniment are advisory warnings the fresh-ears critic weighs. Waive a named check with `allow=[{"check": ..., "reason": ...}]` (logged).
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
