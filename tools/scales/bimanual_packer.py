"""
BimanualPacker — optimize bimanual RH/LH packing for piano reduction.

Takes a RoleGraph and produces an optimized LayerIR where events are
assigned to piano hands with playability constraints.
"""

from __future__ import annotations

from dataclasses import replace as _replace

from .enums import NoteRole, OrchestraRole, ReductionMode
from .models import LayerEvent, LayerIR, PhysicalConstraints
from .pitch import midi_to_pitch, pitch_to_midi
from .role_decomposer import RoleEvent, RoleGraph


def _merge_simultaneous(events: list[LayerEvent]) -> list[LayerEvent]:
    """Collapse events sharing an onset into one chord event.

    Duration is the SHORTEST of the merged notes. Taking the longest would push
    the chord over the next onset and re-create the overflow this exists to
    remove; a pianist reading a reduction re-strikes rather than holds, and the
    bar arithmetic has to be exact because meter is a strict constraint.
    """
    from collections import OrderedDict

    from .duration import dur_to_beats

    groups: "OrderedDict[tuple, list[LayerEvent]]" = OrderedDict()
    for event in sorted(events, key=lambda e: (e.bar, float(e.beat))):
        groups.setdefault((event.bar, round(float(event.beat), 4)), []).append(event)

    out: list[LayerEvent] = []
    for group in groups.values():
        if len(group) == 1:
            out.append(group[0])
            continue
        pitches: list[str] = []
        for event in group:
            for pitch in event.pitch if isinstance(event.pitch, list) else [event.pitch]:
                if pitch and pitch != "rest" and pitch not in pitches:
                    pitches.append(pitch)
        if not pitches:
            out.append(group[0])
            continue
        shortest = min(
            group,
            key=lambda e: (
                float(dur_to_beats(e.duration)) if e.duration else float("inf")
            ),
        )
        merged = _replace(
            shortest,
            pitch=pitches[0] if len(pitches) == 1 else pitches,
        )
        out.append(merged)
    return _clip_to_next_onset(out)


def _clip_to_next_onset(events: list[LayerEvent]) -> list[LayerEvent]:
    """Shorten any note that outlasts the next onset in its own bar.

    Merging simultaneous onsets fixed most of it, but a held note can still be
    overlapped by a LATER, shorter one — "A4h at beat 3 while F#4q starts at
    beat 3" is two notes in one voice just as surely. A hand plays one thing at
    a time, so the earlier note ends where the next begins.

    Only within a bar: a note tied across a barline is legitimate and this must
    not shorten it.
    """
    from .duration import beats_to_dur, dur_to_beats

    out: list[LayerEvent] = []
    ordered = sorted(events, key=lambda e: (e.bar, float(e.beat)))
    for index, event in enumerate(ordered):
        nxt = ordered[index + 1] if index + 1 < len(ordered) else None
        if nxt is None or nxt.bar != event.bar:
            out.append(event)
            continue
        try:
            span = float(dur_to_beats(event.duration))
        except (ValueError, KeyError, TypeError):
            out.append(event)
            continue
        room = float(nxt.beat) - float(event.beat)
        if room <= 0 or span <= room + 1e-9:
            out.append(event)
            continue
        try:
            clipped = beats_to_dur(room)
        except (ValueError, KeyError, TypeError):
            # Not a writable duration (an odd remainder). Leave it: a wrong
            # duration is worse than a long one, and the gate will say so.
            out.append(event)
            continue
        out.append(_replace(event, duration=clipped))
    return out


class BimanualPacker:
    """Optimizes assignment of orchestral events to piano hands.

    Objective:
      maximize coverage + thematic_integrity + bass_continuity + pianistic_flow
      - hand_span_cost - leap_cost - density_cost - register_mud_cost

    Subject to:
      - max_notes_per_hand (default 5)
      - max_hand_span_semitones (default 16)
      - playability at tempo
    """

    def __init__(self, constraints: PhysicalConstraints | None = None):
        self.constraints = constraints or PhysicalConstraints()

    def pack(
        self,
        role_graph: RoleGraph,
        mode: str = ReductionMode.PLAYABLE.value,
        key: str = "C",
        meter: tuple[int, int] = (4, 4),
    ) -> LayerIR:
        """Pack a role graph into a piano LayerIR.

        Args:
            role_graph: Annotated orchestral score
            mode: study_reduction | playable_reduction | concert_transcription
            key: Target key for pitch spelling
            meter: The SOURCE's time signature. Omitting it left the LayerIR at
                its `(4, 4)` default, so reducing a 3/4 orchestral section
                mis-barred every bar of it — 32 meter violations in one section,
                and the reduction of a minuet came out in common time.
        """
        layer = LayerIR(
            phrase_id="reduction",
            # Correct, not an oversight: the OUTPUT of a reduction is a piano
            # whatever the source was. This is the one hardcode in the family
            # that should stay — and the playability check it enables is exactly
            # what a reduction needs most.
            instrumentation="solo_piano",
            key=key,
            meter=meter,
            bar_count=role_graph.bars,
        )

        # Group events by bar
        bars: dict[int, list[RoleEvent]] = {}
        for event in role_graph.events:
            bars.setdefault(event.bar, []).append(event)

        for bar_num in sorted(bars.keys()):
            bar_events = bars[bar_num]
            rh_events, lh_events = self._pack_bar(bar_events, mode, key)

            # Assign to layers, MERGING anything that sounds at the same
            # instant. Each layer is ONE voice, and the packer emitted a
            # separate event per source part — so a four-part chorale reduced
            # to a right hand whose 4/4 bars held 5, 6 and 9 beats, and whose
            # own validator said "G4q starts at beat 1 while D4q is still
            # sounding — one voice cannot play both". Every reduction failed the
            # strict meter gate, which is the one constraint that cannot be
            # waived. A pianist plays those notes as a chord; so does this.
            for event in _merge_simultaneous(rh_events):
                layer.principal_line.append(event)
            for event in _merge_simultaneous(lh_events):
                layer.bass_foundation.append(event)

        return layer

    def _pack_bar(
        self, events: list[RoleEvent], mode: str, key: str
    ) -> tuple[list[LayerEvent], list[LayerEvent]]:
        """Pack one bar of events into RH and LH."""
        rh: list[LayerEvent] = []
        lh: list[LayerEvent] = []

        # Sort by salience (most important first)
        events_sorted = sorted(events, key=lambda e: e.salience, reverse=True)

        # Salience threshold by mode
        threshold = {
            ReductionMode.STUDY.value: 0.2,
            ReductionMode.PLAYABLE.value: 0.3,
            ReductionMode.CONCERT.value: 0.15,
        }.get(mode, 0.3)

        # Max events per hand per beat
        max_per_hand = {
            ReductionMode.STUDY.value: 4,
            ReductionMode.PLAYABLE.value: 3,
            ReductionMode.CONCERT.value: 5,
        }.get(mode, 3)

        # Group by beat
        by_beat: dict[float, list[RoleEvent]] = {}
        for event in events_sorted:
            if event.salience >= threshold:
                by_beat.setdefault(event.beat, []).append(event)

        for _beat, beat_events in sorted(by_beat.items()):
            rh_beat: list[RoleEvent] = []
            lh_beat: list[RoleEvent] = []

            for event in beat_events:
                midi = pitch_to_midi(event.pitch)
                if midi is None:
                    continue

                # Assignment heuristic
                if event.role in (
                    OrchestraRole.PRINCIPAL_MELODY.value,
                    OrchestraRole.SECONDARY_MELODY.value,
                    OrchestraRole.COLOR_PUNCTUATION.value,
                ):
                    if len(rh_beat) < max_per_hand:
                        rh_beat.append(event)
                elif event.role == OrchestraRole.BASS_FOUNDATION.value:
                    if len(lh_beat) < max_per_hand:
                        lh_beat.append(event)
                elif event.role in (
                    OrchestraRole.HARMONIC_PAD.value,
                    OrchestraRole.RHYTHMIC_MOTOR.value,
                ):
                    # Assign to less busy hand
                    if midi >= 60 and len(rh_beat) < max_per_hand:
                        rh_beat.append(event)
                    elif len(lh_beat) < max_per_hand:
                        lh_beat.append(event)
                else:
                    if midi >= 60 and len(rh_beat) < max_per_hand:
                        rh_beat.append(event)
                    elif len(lh_beat) < max_per_hand:
                        lh_beat.append(event)

            # Check hand span constraints
            rh_beat = self._enforce_span(rh_beat)
            lh_beat = self._enforce_span(lh_beat)

            # Convert to LayerEvents
            for event in rh_beat:
                rh.append(
                    LayerEvent(
                        bar=event.bar,
                        beat=event.beat,
                        pitch=midi_to_pitch(pitch_to_midi(event.pitch), key),
                        duration=event.duration,
                        role=self._map_role(event.role),
                        dynamic=event.dynamic,
                        # The marks the source note carried. Dropping them here
                        # is why a reduction lost every slur the original had.
                        slur=event.slur,
                        articulation=event.articulation,
                        ornament=event.ornament,
                        tie=event.tie,
                        source_layer="principal_line",
                    )
                )

            for event in lh_beat:
                lh.append(
                    LayerEvent(
                        bar=event.bar,
                        beat=event.beat,
                        pitch=midi_to_pitch(pitch_to_midi(event.pitch), key),
                        duration=event.duration,
                        role=self._map_role(event.role),
                        dynamic=event.dynamic,
                        # The marks the source note carried. Dropping them here
                        # is why a reduction lost every slur the original had.
                        slur=event.slur,
                        articulation=event.articulation,
                        ornament=event.ornament,
                        tie=event.tie,
                        source_layer="bass_foundation",
                    )
                )

        return rh, lh

    def _enforce_span(self, events: list[RoleEvent]) -> list[RoleEvent]:
        """Remove events that exceed hand span."""
        if len(events) <= 1:
            return events

        midis = [(pitch_to_midi(e.pitch), e) for e in events if pitch_to_midi(e.pitch) is not None]
        if not midis:
            return events

        midis.sort(key=lambda x: x[0])

        # If span exceeds max, remove least salient events from extremes
        while len(midis) >= 2:
            span = midis[-1][0] - midis[0][0]
            if span <= self.constraints.max_hand_span_semitones:
                break
            # Remove the least salient extreme
            if midis[0][1].salience <= midis[-1][1].salience:
                midis.pop(0)
            else:
                midis.pop()

        return [e for _, e in midis]

    def _map_role(self, orchestra_role: str) -> str:
        """Map orchestral role to note role."""
        mapping = {
            OrchestraRole.PRINCIPAL_MELODY.value: NoteRole.STRUCTURAL.value,
            OrchestraRole.SECONDARY_MELODY.value: NoteRole.STRUCTURAL.value,
            OrchestraRole.BASS_FOUNDATION.value: NoteRole.STRUCTURAL.value,
            OrchestraRole.HARMONIC_PAD.value: NoteRole.ARPEGGIATED_FILL.value,
            OrchestraRole.RHYTHMIC_MOTOR.value: NoteRole.PUNCTUATION.value,
            OrchestraRole.COLOR_PUNCTUATION.value: NoteRole.ORNAMENTAL.value,
            OrchestraRole.CUE_NOTES.value: NoteRole.CUE.value,
            OrchestraRole.CLIMACTIC_HIT.value: NoteRole.STRUCTURAL.value,
        }
        return mapping.get(orchestra_role, NoteRole.STRUCTURAL.value)
