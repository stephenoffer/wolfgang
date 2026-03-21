# Wolfgang v2 — Classical Music Generation Agent

## Project Overview
Wolfgang is a multi-skill Claude Code agent system that generates full orchestral scores from natural language descriptions, images, or references to existing works. Output is MusicXML (.musicxml/.mxl) importable into MuseScore.

## Architecture
- **16 Claude Code skills** in `.claude/skills/` — each handles one aspect of composition
- **File-mediated state machine** — all state in `workspace/<piece-id>/` as JSON + ABC files
- **Musical Continuity Document (MCD)** — `continuity.json` tracks all musical decisions for long-form coherence
- **ABC notation** as intermediate format, converted to MusicXML via `music21` Python library

## Key Entry Point
- `/wolfgang <description>` — the master orchestrator skill that parses requests and chains all sub-skills

## Skills (invoke with `/skill-name`)
| Skill | Purpose |
|-------|---------|
| `/wolfgang` | Master orchestrator — parses request, manages pipeline, user checkpoints |
| `/w-interpret` | Translates images, abstract concepts, piece references → musical parameters |
| `/w-research` | Web search for unknown composers/styles, builds temporary profiles |
| `/w-narrative` | Designs emotional arc from story/program |
| `/w-structure` | Plans form, sections, key areas, timing |
| `/w-themes` | Creates themes as ABC + transformations + usage plan |
| `/w-novelty` | Checks themes against known melodies for originality |
| `/w-harmony` | Designs chord progressions per section |
| `/w-rhythm` | Plans rhythmic patterns per section |
| `/w-orchestration` | Assigns instruments, dynamics, texture per section |
| `/w-compose` | Writes ABC notation for one section |
| `/w-review` | Section-level quality check (up to 3 iterations) |
| `/w-holistic` | Full-piece/movement-level coherence review |
| `/w-reduce` | Arrangement/reduction between instrumentations |
| `/w-assemble` | Final assembly + MusicXML conversion |

## Context System
- `.claude/context/general/` — shared music theory (scales, counterpoint, form)
- `.claude/context/<genre>/` — genre-specific harmony, orchestration, forms
- `.claude/context/<genre>/composer-profiles/` — individual composer style guides
- Genre periods: baroque, classical, romantic, late-romantic, nationalistic, impressionist, modern, minimalist, film-score

## Python Tools (`tools/`)
- `abc_to_musicxml.py` — ABC → MusicXML via music21
- `validate_abc.py` — pre-conversion syntax validation
- `validate_musicxml.py` — post-conversion schema validation
- `assemble_score.py` — merge section ABCs into movements
- `range_checker.py` — verify notes within instrument ranges
- `theme_extractor.py` — extract/verify theme patterns in ABC
- `novelty_checker.py` — compare themes against known melody database
- `continuity_tracker.py` — update Musical Continuity Document

## Conventions
- All context files: dense tables + ABC examples, not prose. Target ~200-400 lines, <4000 tokens
- Workspace files: JSON for structured data, ABC for music notation
- Section IDs: `m<movement>_<section_name>` (e.g., `m1_expo_pt`, `m2_a`)
- Piece IDs: `<descriptive-slug>-<key>-<date>` (e.g., `winter-concerto-dm-20260321`)
- Python: use music21 for all music parsing/conversion, lxml for XML validation
