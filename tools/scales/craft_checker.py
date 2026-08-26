"""
CraftChecker — enforces the phrase sanctity checklist.

Every phrase must pass before acceptance:
- melodic claim is clear
- rhythm has identity
- bass has purpose
- harmony is voiced, not just labeled
- there is a breath point
- accompaniment responds to melody
- entry and exit feel earned
- at least one memorable detail (encouraged, not blocking)
"""

from __future__ import annotations

from typing import List, Optional

from .models import (
    LayerIR,
    OnsetBundle,
    PhraseControlIR,
    PhraseCraftCheck,
)
from .pitch import pitch_to_midi


class CraftChecker:
    """Enforces the phrase sanctity checklist."""

    def check(
        self,
        layer_ir: LayerIR,
        control: Optional[PhraseControlIR] = None,
        bundles: Optional[List[OnsetBundle]] = None,
    ) -> PhraseCraftCheck:
        """Run all craft checks on a realized phrase."""
        return PhraseCraftCheck(
            melodic_claim_clear=self._check_melodic_claim(layer_ir),
            rhythm_has_identity=self._check_rhythmic_identity(layer_ir),
            bass_has_purpose=self._check_bass_purpose(layer_ir),
            harmony_is_voiced=self._check_harmony_voiced(layer_ir),
            has_breath_point=self._check_breathing(layer_ir),
            accompaniment_responds_to_melody=self._check_accomp_response(layer_ir),
            entry_exit_earned=self._check_entry_exit(layer_ir, control),
            has_memorable_detail=self._check_memorable_detail(layer_ir),
            all_notes_justified=self._check_justifications(bundles),
        )

    def _check_melodic_claim(self, layer: LayerIR) -> bool:
        """Melody exists and has directional movement."""
        melody = layer.principal_line
        if len(melody) < 3:
            return False

        midis = []
        for evt in melody:
            if evt.pitch != "rest" and not isinstance(evt.pitch, list):
                try:
                    midis.append(pitch_to_midi(evt.pitch))
                except (ValueError, KeyError):
                    pass

        if len(midis) < 3:
            return False

        # Check that melody has directional movement (not all same pitch)
        pitch_range = max(midis) - min(midis)
        return pitch_range >= 3  # at least a minor third

    def _check_rhythmic_identity(self, layer: LayerIR) -> bool:
        """Rhythm has variety — not all same duration."""
        all_events = layer.principal_line + layer.response_layer
        if len(all_events) < 4:
            return False

        durations = [evt.duration for evt in all_events if evt.pitch != "rest"]
        unique = set(durations)
        return len(unique) >= 2

    def _check_bass_purpose(self, layer: LayerIR) -> bool:
        """Bass exists and provides harmonic foundation."""
        bass = layer.bass_foundation
        if len(bass) < 2:
            return False

        # Bass should have at least one note per 2 bars
        bars_with_bass = set(evt.bar for evt in bass if evt.pitch != "rest")
        expected_bars = max(1, layer.bar_count // 2)
        return len(bars_with_bass) >= expected_bars

    def _check_harmony_voiced(self, layer: LayerIR) -> bool:
        """Harmony is not just melody-over-bass-root: something fills the middle.

        This used to count events in ``response_layer`` and ``counter_reply``.
        Those layers are only populated when the shorthand writes an explicit
        second voice in a hand, so a perfectly well-voiced phrase whose chords
        live in ``bass_foundation`` — which is most of them, since a plain
        single-stream left hand goes there whole — scored as unvoiced. Measured
        on 126 real 8-bar phrases, the old check passed **56%** of canonical
        music.

        The question is about the SOUND: at some point in the phrase, are three
        or more notes sounding together?
        """
        from .counterpoint import attack_times, extract_voices, sounding_at

        spans = extract_voices(layer)
        if not spans:
            return False
        for t in attack_times(spans):
            if len(sounding_at(spans, t)) >= 3:
                return True
        return False

    def _check_breathing(self, layer: LayerIR) -> bool:
        """Has at least one rest or breath point."""
        all_events = layer.principal_line + layer.bass_foundation + layer.response_layer
        rests = sum(1 for evt in all_events if evt.pitch == "rest")
        return rests >= 1 or layer.bar_count <= 2

    def _check_accomp_response(self, layer: LayerIR) -> bool:
        """There is an accompaniment, and it is not the same in every bar.

        The old check was ``len(response_layer) >= 4`` — a layer that is empty
        for any phrase written with a single-stream left hand, so it passed only
        **31%** of 126 real phrases. It was measuring which layer the notes were
        filed under, not whether an accompaniment exists or does anything.

        "Responds" is deliberately weak here: an accompaniment that holds one
        figure for a phrase is normal writing (real music reuses its figures far
        more than intuition suggests). What this rules out is no accompaniment
        at all, or one note per bar and nothing else.
        """
        accomp = [
            e
            for e in (layer.bass_foundation + layer.response_layer)
            if e.pitch != "rest"
        ]
        if len(accomp) < 3:
            return False
        bars = {e.bar for e in accomp}
        return len(accomp) >= max(3, len(bars) + 1)

    def _check_entry_exit(self, layer: LayerIR, control: Optional[PhraseControlIR]) -> bool:
        """The phrase begins and ends with sound, not with a hole.

        Two faults in the old version. It indexed ``principal_line`` in LIST
        order rather than in TIME order, so for any material not stored sorted
        it tested two arbitrary events. And it required the very last event to
        be a note — but a phrase that ends with a rest after its final note has
        ended perfectly well, and lifting into a rest is how a phrase breathes.
        It passed **75%** of 126 real phrases.

        What matters is that the phrase *sounds* at its start and reaches a
        sounding note at its end.
        """
        melody = sorted(
            (e for e in layer.principal_line), key=lambda e: (e.bar, e.beat)
        )
        sounding = [e for e in melody if e.pitch != "rest"]
        if not sounding:
            return False
        # An anacrusis legitimately starts with a rest before the upbeat, so the
        # test is that sound arrives early in the phrase, not on the first event.
        first_sounding = melody.index(sounding[0])
        return first_sounding <= 2

    def _check_memorable_detail(self, layer: LayerIR) -> bool:
        """Something in this phrase is worth remembering.

        The old version looked for events in ``ornamental_surface`` (a layer
        nothing populates), more than one distinct dynamic in the melody, or any
        articulation on the melody. It passed **0 of 126** real 8-bar phrases —
        a check that no canonical music can satisfy is measuring the wrong
        thing entirely.

        A detail is memorable if it is *distinctive*, and a phrase can be
        distinctive in pitch or in rhythm as well as in notation: an expressive
        leap, a note markedly longer than its neighbours, a silence, a written
        ornament or articulation anywhere in the texture, a dynamic that moves.
        """
        from .duration import dur_to_beats

        events = (
            layer.principal_line
            + layer.counter_reply
            + layer.bass_foundation
            + layer.response_layer
            + layer.ornamental_surface
        )
        if not events:
            return False

        # Notated detail, anywhere in the texture — not only in the melody.
        if any(
            e.ornament or e.articulation or getattr(e, "technique", None) for e in events
        ):
            return True
        if len({e.dynamic for e in events if e.dynamic}) > 1:
            return True
        if any(e.hairpin for e in events):
            return True

        melody = [e for e in layer.principal_line if e.pitch != "rest"]
        if len(melody) >= 3:
            midis = [m for m in (self._top_midi(e) for e in melody) if m is not None]
            # An expressive leap: a sixth or wider is a gesture, not a step.
            if any(abs(b - a) >= 9 for a, b in zip(midis, midis[1:])):
                return True
            durs = [float(dur_to_beats(e.duration)) for e in melody]
            if durs:
                longest, typical = max(durs), sorted(durs)[len(durs) // 2]
                # A note twice the phrase's usual value is an arrival.
                if typical > 0 and longest >= typical * 2:
                    return True
        # A written silence inside the phrase is itself a detail.
        interior = [e for e in layer.principal_line[1:-1] if e.pitch == "rest"]
        return bool(interior)

    @staticmethod
    def _top_midi(event) -> Optional[int]:
        """Top sounding MIDI of an event, or None."""
        pitch = getattr(event, "pitch", None)
        if not pitch or pitch == "rest":
            return None
        names = pitch if isinstance(pitch, list) else [pitch]
        vals = []
        for n in names:
            try:
                vals.append(pitch_to_midi(n))
            except (ValueError, KeyError, TypeError):
                continue
        vals = [v for v in vals if v is not None]
        return max(vals) if vals else None

    def _check_justifications(self, bundles: Optional[List[OnsetBundle]]) -> bool:
        """Every note has at least one structural + one local reason."""
        if not bundles:
            return True  # skip if no bundles (backward compat)

        for bundle in bundles:
            for onset in bundle.events:
                if onset.pitch == "rest":
                    continue
                j = onset.justification
                if not j.structural_reasons or not j.local_reasons:
                    return False
        return True
