"""
SABRE — Salience-Aware Bimanual Reduction Engine.

Orchestral → piano reduction and piano → orchestral expansion.
Handles three reduction modes:
  - study_reduction: preserve structure and voice-leading, moderate difficulty
  - playable_reduction: stronger omission, optimize for human playability
  - concert_transcription: can add figuration, redistribute, amplify
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .bimanual_packer import BimanualPacker
from .enums import ReductionMode
from .models import LayerIR, PhysicalConstraints
from .role_decomposer import RoleDecomposer


class SABRE:
    """Salience-Aware Bimanual Reduction Engine.

    Usage:
        sabre = SABRE()
        layer_ir = sabre.reduce_to_piano(events, instruments, mode="playable_reduction")
    """

    def __init__(self, constraints: Optional[PhysicalConstraints] = None):
        self.decomposer = RoleDecomposer()
        self.packer = BimanualPacker(constraints)

    def reduce_to_piano(
        self,
        events: List[Dict[str, Any]],
        instruments: Optional[List[str]] = None,
        mode: str = ReductionMode.PLAYABLE.value,
        key: str = "C",
    ) -> LayerIR:
        """Full reduction pipeline: decompose → pack → LayerIR.

        Args:
            events: Raw score events [{instrument, bar, beat, pitch, duration, dynamic}]
            instruments: List of instruments in the score
            mode: Reduction mode
            key: Target key for pitch spelling
        """
        # Step 1: Decompose into role graph
        role_graph = self.decomposer.decompose(events, instruments)

        # Step 2: Pack into piano hands
        layer_ir = self.packer.pack(role_graph, mode, key)

        return layer_ir

    def orchestrate_from_piano(
        self, layer_ir: LayerIR, target_ensemble: List[str], key: str = "C"
    ) -> Dict[str, List[Dict]]:
        """Expand piano LayerIR into orchestral parts.

        This is the inverse of reduction: assign piano layers to
        orchestral instruments by role.
        """
        parts: Dict[str, List[Dict]] = {inst: [] for inst in target_ensemble}

        # Simple role-based assignment
        role_to_instruments = self._plan_orchestration(target_ensemble)

        # Assign principal line to melody instruments
        melody_inst = role_to_instruments.get(
            "melody", target_ensemble[0] if target_ensemble else "violin_1"
        )
        for event in layer_ir.principal_line:
            parts.setdefault(melody_inst, []).append(
                {
                    "bar": event.bar,
                    "beat": event.beat,
                    "pitch": event.pitch,
                    "duration": event.duration,
                    "dynamic": event.dynamic,
                }
            )

        # Assign bass foundation to bass instruments
        bass_inst = role_to_instruments.get(
            "bass", target_ensemble[-1] if target_ensemble else "cello"
        )
        for event in layer_ir.bass_foundation:
            parts.setdefault(bass_inst, []).append(
                {
                    "bar": event.bar,
                    "beat": event.beat,
                    "pitch": event.pitch,
                    "duration": event.duration,
                    "dynamic": event.dynamic,
                }
            )

        # Assign response layer to inner instruments
        inner_inst = role_to_instruments.get("inner", None)
        if inner_inst:
            for event in layer_ir.response_layer:
                parts.setdefault(inner_inst, []).append(
                    {
                        "bar": event.bar,
                        "beat": event.beat,
                        "pitch": event.pitch,
                        "duration": event.duration,
                        "dynamic": event.dynamic,
                    }
                )

        return parts

    def _plan_orchestration(self, instruments: List[str]) -> Dict[str, str]:
        """Plan which instruments get which roles."""
        plan = {}

        # Heuristic assignment
        melody_candidates = ["violin_1", "flute", "oboe", "clarinet"]
        bass_candidates = ["cello", "contrabass", "double_bass", "bassoon", "tuba"]
        inner_candidates = ["violin_2", "viola", "horn", "clarinet"]

        for inst in instruments:
            inst_lower = inst.lower().replace(" ", "_")
            if inst_lower in melody_candidates and "melody" not in plan:
                plan["melody"] = inst
            elif inst_lower in bass_candidates and "bass" not in plan:
                plan["bass"] = inst
            elif inst_lower in inner_candidates and "inner" not in plan:
                plan["inner"] = inst

        # Defaults
        if "melody" not in plan and instruments:
            plan["melody"] = instruments[0]
        if "bass" not in plan and len(instruments) > 1:
            plan["bass"] = instruments[-1]
        if "inner" not in plan and len(instruments) > 2:
            plan["inner"] = instruments[1]

        return plan
