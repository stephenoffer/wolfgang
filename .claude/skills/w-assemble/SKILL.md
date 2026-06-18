---
name: w-assemble
description: "Assemble all composed sections into complete movements and convert to MusicXML. Final output generation."
argument-hint: "<piece-id> [scope: 'full' | 'movement-N' | 'section-ID']"
---

# w-assemble — Final Assembly

Assemble all realized sections into complete movements and produce MusicXML + optional audio preview.

## Prerequisites

Before assembly, verify all sections have realized phrases.

## Assembly

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.piece_graph import PieceGraph
from scales.assembler import assemble
graph = PieceGraph.load('workspace/<piece-id>/piece_graph.json')
path = assemble(graph, scope='full')
print(f'MusicXML written to: {path}')
"
```

## MIDI Preview

```bash
python3 -c "
import sys; sys.path.insert(0, 'tools')
from scales.piece_graph import PieceGraph
from scales.midi_renderer import render_midi
graph = PieceGraph.load('workspace/<piece-id>/piece_graph.json')
path = render_midi(graph)
print(f'MIDI written to: {path}')
"
```

## Output

Report to user:
- Path to MusicXML file (importable into MuseScore)
- Path to MIDI file (for playback preview)
- Summary: movements, total bars, sections, key scheme
