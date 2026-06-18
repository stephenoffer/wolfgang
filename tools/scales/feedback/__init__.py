"""
Corpus feedback loop for Wolfgang v2.

Closes the loop between new reference scores and the context doctrine system.
New scores → evidence extraction → claim matching → overlay building → recompilation.

Three-layer context stack:
  Layer 1: Canonical doctrine (.claude/context/) — human-curated, stable
  Layer 2: Evidence-backed overlays (tools/context_overlays/) — machine-updated
  Layer 3: Live memory (tools/reference_index/, pattern_library/) — updates fastest
"""
