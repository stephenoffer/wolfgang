"""
RoleDecomposer — decompose a multi-instrument score into role graph.

Labels every event with its musical role (principal melody, secondary melody,
bass foundation, harmonic pad, rhythmic motor, color, cue) and computes
salience scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import OrchestraRole
from .pitch import pitch_to_midi


@dataclass
class RoleEvent:
    """A source event annotated with role and salience."""

    instrument: str = ""
    bar: int = 1
    beat: float = 1.0
    pitch: str = ""
    duration: str = "q"
    dynamic: str | None = None
    # What the source note was MARKED with. A reduction that cannot see the
    # original's phrasing cannot preserve it, and this carried only `dynamic`:
    # a polonaise with 27 slurs reduced to a piano part with none.
    slur: str | None = None
    articulation: str | None = None
    ornament: str | None = None
    tie: str | None = None
    role: str = OrchestraRole.HARMONIC_PAD.value
    salience: float = 0.5

    # Decomposition factors
    structural_importance: float = 0.0
    melodic_prominence: float = 0.0
    dynamic_weight: float = 0.0
    cadence_weight: float = 0.0


@dataclass
class RoleGraph:
    """Complete role-annotated score."""

    events: list[RoleEvent] = field(default_factory=list)
    bars: int = 0
    instruments: list[str] = field(default_factory=list)

    def get_by_role(self, role: str) -> list[RoleEvent]:
        return [e for e in self.events if e.role == role]

    def get_by_instrument(self, instrument: str) -> list[RoleEvent]:
        return [e for e in self.events if e.instrument == instrument]

    def get_top_salience(self, n: int = 10) -> list[RoleEvent]:
        return sorted(self.events, key=lambda e: e.salience, reverse=True)[:n]


class RoleDecomposer:
    """Decomposes a parsed score into a RoleGraph.

    Uses heuristics based on register, rhythm, dynamics, and
    instrument identity to assign roles.
    """

    # Instrument role priors
    _ROLE_PRIORS = {
        # Strings
        "violin_1": OrchestraRole.PRINCIPAL_MELODY.value,
        "violin_2": OrchestraRole.SECONDARY_MELODY.value,
        # An undivided violin part carries the tune: a score that writes plain
        # "Violin" is not writing a second violin.
        "violin": OrchestraRole.PRINCIPAL_MELODY.value,
        # Voices. A chorale or a mass reduced to piano has no strings in it at
        # all, and every one of these used to resolve to a harmonic pad.
        "soprano": OrchestraRole.PRINCIPAL_MELODY.value,
        "mezzo_soprano": OrchestraRole.SECONDARY_MELODY.value,
        "alto": OrchestraRole.SECONDARY_MELODY.value,
        "tenor": OrchestraRole.SECONDARY_MELODY.value,
        "baritone": OrchestraRole.BASS_FOUNDATION.value,
        "bass": OrchestraRole.BASS_FOUNDATION.value,
        "viola": OrchestraRole.HARMONIC_PAD.value,
        "cello": OrchestraRole.BASS_FOUNDATION.value,
        "contrabass": OrchestraRole.BASS_FOUNDATION.value,
        "double_bass": OrchestraRole.BASS_FOUNDATION.value,
        # Woodwinds
        "flute": OrchestraRole.PRINCIPAL_MELODY.value,
        "oboe": OrchestraRole.PRINCIPAL_MELODY.value,
        "clarinet": OrchestraRole.PRINCIPAL_MELODY.value,
        "bassoon": OrchestraRole.BASS_FOUNDATION.value,
        # Brass
        "horn": OrchestraRole.HARMONIC_PAD.value,
        "trumpet": OrchestraRole.COLOR_PUNCTUATION.value,
        "trombone": OrchestraRole.HARMONIC_PAD.value,
        "tuba": OrchestraRole.BASS_FOUNDATION.value,
        # Percussion
        "timpani": OrchestraRole.RHYTHMIC_MOTOR.value,
        # Present in `INSTRUMENT_RANGES` and absent here, so a score with any of
        # them reduced that part as an unnamed harmonic pad.
        "piccolo": OrchestraRole.PRINCIPAL_MELODY.value,
        "english_horn": OrchestraRole.SECONDARY_MELODY.value,
        "bass_clarinet": OrchestraRole.BASS_FOUNDATION.value,
        "contrabassoon": OrchestraRole.BASS_FOUNDATION.value,
        "bass_trombone": OrchestraRole.BASS_FOUNDATION.value,
        "harp": OrchestraRole.COLOR_PUNCTUATION.value,
        "celesta": OrchestraRole.COLOR_PUNCTUATION.value,
        "glockenspiel": OrchestraRole.COLOR_PUNCTUATION.value,
        # Piano
        "piano_rh": OrchestraRole.PRINCIPAL_MELODY.value,
        "piano_lh": OrchestraRole.BASS_FOUNDATION.value,
    }

    def decompose(
        self, events: list[dict[str, Any]], instruments: list[str] | None = None
    ) -> RoleGraph:
        """Decompose raw events into a role graph.

        Args:
            events: List of dicts with keys: instrument, bar, beat, pitch, duration, dynamic
            instruments: List of instrument names in the score
        """
        graph = RoleGraph(instruments=instruments or [])

        for event_data in events:
            role_event = RoleEvent(
                instrument=event_data.get("instrument", ""),
                bar=event_data.get("bar", 1),
                beat=event_data.get("beat", 1.0),
                pitch=event_data.get("pitch", ""),
                duration=event_data.get("duration", "q"),
                dynamic=event_data.get("dynamic"),
                slur=event_data.get("slur"),
                articulation=event_data.get("articulation"),
                ornament=event_data.get("ornament"),
                tie=event_data.get("tie"),
            )

            # Assign role
            role_event.role = self._assign_role(role_event)

            # Compute salience
            role_event.salience = self._compute_salience(role_event)

            graph.events.append(role_event)
            graph.bars = max(graph.bars, role_event.bar)

        return graph

    def _assign_role(self, event: RoleEvent) -> str:
        """Assign orchestral role to an event.

        The lookup was `event.instrument.lower().replace(" ", "_")` against a
        table keyed `violin_1`, `cello`, `flute`. Measured against the part names
        in real scores, **11 of 15 missed** — every violin spelling ("Violin",
        "Violin I", "1st Violin"), "Violoncello", and all four voice names — and
        a miss returns HARMONIC_PAD. So in `reduce_to_piano` the first violin,
        which is carrying the tune, was filed as filler in every real orchestral
        score, and the reduction had no principal melody to preserve.
        """
        from .models import canonical_instrument

        key, division = canonical_instrument(event.instrument)
        # "Violin I" and "Violin II" are different roles; "Flute 1" and "Flute 2"
        # are not, so a division only counts where the table names it.
        divided = f"{key}_{division}" if division else ""
        instrument = divided if divided in self._ROLE_PRIORS else key

        # Start with instrument prior
        role = self._ROLE_PRIORS.get(instrument, OrchestraRole.HARMONIC_PAD.value)

        # Adjust based on register
        midi = pitch_to_midi(event.pitch)
        if midi is not None:
            if midi >= 72 and role == OrchestraRole.HARMONIC_PAD.value:
                role = OrchestraRole.SECONDARY_MELODY.value
            elif midi <= 48:
                role = OrchestraRole.BASS_FOUNDATION.value

        # Adjust based on dynamics
        dyn = (event.dynamic or "").lower()
        if dyn in ("ff", "fff", "sfz") and role == OrchestraRole.HARMONIC_PAD.value:
            role = OrchestraRole.CLIMACTIC_HIT.value

        return role

    def _compute_salience(self, event: RoleEvent) -> float:
        """Compute salience score (0-1) for a role event."""
        score = 0.0

        # Structural importance by role
        role_weights = {
            OrchestraRole.PRINCIPAL_MELODY.value: 1.0,
            OrchestraRole.SECONDARY_MELODY.value: 0.7,
            OrchestraRole.BASS_FOUNDATION.value: 0.8,
            OrchestraRole.HARMONIC_PAD.value: 0.3,
            OrchestraRole.RHYTHMIC_MOTOR.value: 0.4,
            OrchestraRole.COLOR_PUNCTUATION.value: 0.5,
            OrchestraRole.CUE_NOTES.value: 0.2,
            OrchestraRole.CLIMACTIC_HIT.value: 0.9,
        }
        event.structural_importance = role_weights.get(event.role, 0.3)
        score += 0.4 * event.structural_importance

        # Melodic prominence (higher register = more prominent)
        midi = pitch_to_midi(event.pitch)
        if midi is not None:
            event.melodic_prominence = min(1.0, max(0.0, (midi - 48) / 48))
            score += 0.2 * event.melodic_prominence

        # Dynamic weight
        dyn_map = {
            "ppp": 0.1,
            "pp": 0.2,
            "p": 0.3,
            "mp": 0.4,
            "mf": 0.5,
            "f": 0.7,
            "ff": 0.9,
            "fff": 1.0,
            "sfz": 1.0,
        }
        event.dynamic_weight = dyn_map.get((event.dynamic or "").lower(), 0.5)
        score += 0.2 * event.dynamic_weight

        # Beat position (downbeats more salient)
        if abs(event.beat - 1.0) < 0.01:
            score += 0.2
        elif abs(event.beat - 3.0) < 0.01:
            score += 0.1

        return min(1.0, score)
