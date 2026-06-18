"""
SectionSearch — beam search / Viterbi-style path optimization across a section.

Finds the best combination of phrase candidates such that the whole
section works together, not just individual phrases.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .models import CandidateNode, SectionPath


class SectionSearch:
    """Beam search over phrase candidates to find optimal section path."""

    def beam_search(
        self,
        candidates_by_phrase: Dict[str, List[CandidateNode]],
        phrase_order: List[str],
        mode: str = "compose_from_text",
        beam_width: int = 5,
        transition_scorer: Optional[Callable] = None,
        ledger_scorer: Optional[Callable] = None,
    ) -> SectionPath:
        """Find the best path through phrase candidates.

        Args:
            candidates_by_phrase: phrase_id -> list of scored CandidateNodes
            phrase_order: ordered phrase IDs in the section
            mode: composition mode for weight selection
            beam_width: how many paths to keep at each step
            transition_scorer: callable(prev_surface, curr_surface) -> float
            ledger_scorer: callable(phrase_id) -> float
        """
        if not phrase_order:
            return SectionPath()

        # Filter to only phrases that have candidates
        active_phrases = [
            p for p in phrase_order if p in candidates_by_phrase and candidates_by_phrase[p]
        ]
        if not active_phrases:
            return SectionPath()

        # Initialize beam with first phrase candidates
        first_phrase = active_phrases[0]
        beam: List[SectionPath] = []
        for cand in candidates_by_phrase[first_phrase]:
            path = SectionPath(
                section_id="",
                nodes=[cand],
                total_score=cand.scores.total(mode),
                transition_scores=[],
            )
            beam.append(path)

        # Sort and prune
        beam = _prune_beam(beam, beam_width)

        # Extend beam phrase by phrase
        for phrase_id in active_phrases[1:]:
            new_beam: List[SectionPath] = []
            phrase_candidates = candidates_by_phrase[phrase_id]

            for path in beam:
                for cand in phrase_candidates:
                    # Compute transition score
                    transition_score = 0.5  # default
                    if transition_scorer and path.nodes:
                        prev_surface = path.nodes[-1].surface
                        curr_surface = cand.surface
                        if prev_surface and curr_surface:
                            transition_score = transition_scorer(prev_surface, curr_surface)

                    # Compute ledger score
                    ledger_score = 1.0
                    if ledger_scorer:
                        ledger_score = ledger_scorer(phrase_id)

                    # Combined score
                    node_score = cand.scores.total(mode)
                    extended_score = (
                        path.total_score
                        + node_score
                        + 0.3 * transition_score  # transition weight
                        + 0.2 * ledger_score  # ledger weight
                    )

                    new_path = SectionPath(
                        section_id=path.section_id,
                        nodes=path.nodes + [cand],
                        total_score=extended_score,
                        transition_scores=path.transition_scores + [transition_score],
                    )
                    new_beam.append(new_path)

            beam = _prune_beam(new_beam, beam_width)

        # Return best path
        if beam:
            best = beam[0]
            # Normalize score by path length
            if len(best.nodes) > 0:
                best.total_score /= len(best.nodes)
            return best
        return SectionPath()

    def greedy_search(
        self,
        candidates_by_phrase: Dict[str, List[CandidateNode]],
        phrase_order: List[str],
        mode: str = "compose_from_text",
    ) -> SectionPath:
        """Simple greedy selection: pick best candidate per phrase.

        Faster but no transition optimization. Useful for single phrases
        or when beam search is overkill.
        """
        nodes = []
        total_score = 0.0

        for phrase_id in phrase_order:
            cands = candidates_by_phrase.get(phrase_id, [])
            if not cands:
                continue
            # Pick the one with highest individual score
            best = max(cands, key=lambda c: c.scores.total(mode))
            nodes.append(best)
            total_score += best.scores.total(mode)

        if nodes:
            total_score /= len(nodes)

        return SectionPath(
            nodes=nodes,
            total_score=total_score,
        )


def _prune_beam(beam: List[SectionPath], width: int) -> List[SectionPath]:
    """Sort by score descending and keep top `width` paths."""
    beam.sort(key=lambda p: p.total_score, reverse=True)
    return beam[:width]
