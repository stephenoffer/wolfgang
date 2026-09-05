"""
HarmonicSolver — resolves harmonic cells into concrete voicings with
voice leading.

Replaces the realizer's _harmony_to_bass() which just puts root-position
bass. The solver produces beat-level voicings with smooth voice leading,
using HarmonicDevice templates, CadenceScripts, and the pitch utilities.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

# Roman numeral → scale degree offset (from root, in semitones)
# Roman numeral -> (degree, quality) is parsed, not looked up. The two tables
# that used to live here were hand-maintained and full of holes: "viio7" was
# listed but "V7" was not, so every dominant seventh in every progression model
# and every chord frame silently degraded to a plain triad; "I6" was listed but
# "I64" was not, so second-inversion chords came out in root position. A parser
# covers the whole grammar by construction — see
# ``scales.harmony_analysis.parse_roman``, which round-trips against
# ``spell_roman`` for all 12 degrees, 9 qualities and every inversion.
from .harmony_analysis import parse_roman as _parse_roman
from .models import (
    CadenceScript,
    HarmonicCell,
    HarmonicDevice,
    RegisterPlan,
)
from .pitch import (
    build_scale,
    chord_tones,
    is_minor_key,
    key_to_root_midi,
    midi_to_pitch,
)


def _roman_degree(roman: str, mode: str = "major") -> int:
    parsed = _parse_roman(roman, mode)
    return int(parsed["degree"]) if parsed else 0


def _roman_quality(roman: str, mode: str = "major") -> str:
    parsed = _parse_roman(roman, mode)
    return str(parsed["quality"]) if parsed else "major"


def _roman_inversion(roman: str, mode: str = "major") -> int:
    parsed = _parse_roman(roman, mode)
    return int(parsed["inversion"]) if parsed else 0


class HarmonicSolver:
    """Resolves HarmonicCells into concrete voicings with voice leading.

    Uses:
    - HarmonicDevice templates for chromatic devices
    - CadenceScript templates for cadence bars
    - Voice-leading cost minimization from pitch.py
    """

    def solve(
        self,
        cells: List[HarmonicCell],
        key: str,
        meter: Tuple[int, int],
        devices: Optional[List[HarmonicDevice]] = None,
        cadence_scripts: Optional[List[CadenceScript]] = None,
        register_plan: Optional[RegisterPlan] = None,
    ) -> List[Dict]:
        """Produce beat-level voicings with smooth voice leading.

        Returns list of dicts:
        {bar, beat, soprano, alto, tenor, bass, quality, inversion, roman}
        """
        if not cells:
            return []

        root_midi = key_to_root_midi(key)
        mode = "minor" if is_minor_key(key) else "major"
        scale = build_scale(root_midi + 60, mode)

        # Register defaults
        sop_range = (60, 84)
        bass_range = (36, 60)
        if register_plan:
            sop_range = register_plan.soprano_range
            bass_range = register_plan.bass_range

        voicings: List[Dict] = []
        prev_voicing: Optional[Dict] = None

        for cell in cells:
            voicing = self._voice_cell(
                cell,
                key,
                root_midi,
                mode,
                scale,
                sop_range,
                bass_range,
                prev_voicing,
                devices,
                cadence_scripts,
            )
            voicings.append(voicing)
            prev_voicing = voicing

        return voicings

    def _voice_cell(
        self,
        cell: HarmonicCell,
        key: str,
        root_midi: int,
        mode: str,
        scale: List[int],
        sop_range: Tuple[int, int],
        bass_range: Tuple[int, int],
        prev: Optional[Dict],
        devices: Optional[List[HarmonicDevice]],
        cadence_scripts: Optional[List[CadenceScript]],
    ) -> Dict:
        """Voice a single harmonic cell.

        Consults HarmonicDevice templates when available for
        voice-leading hints and emotional color guidance.
        """
        roman = cell.roman
        # The ROMAN decides the quality when there is one.
        #
        # This read `cell.quality or _roman_quality(roman, mode)`, and
        # `HarmonicCell.quality` defaults to `"major"` — a non-empty default, so
        # the `or` never fell through and the parsed quality was never consulted
        # for any cell built without an explicit one. Which is all of them on
        # the v6 path.
        #
        # Every minor chord was therefore voiced MAJOR: `i` in D minor came out
        # D-F#-A and `iv` came out G-B-D. Measured on a planned piece, **5 of 16
        # bars carried a pitch class outside their own chord**, every one of
        # them that F#, sounding against a melody correctly playing F natural.
        #
        # `i` IS minor — the numeral says so, and `parse_roman` reads it
        # correctly. The `quality` field is redundant beside a roman and only
        # meaningful without one.
        quality = _roman_quality(roman, mode) if roman else (cell.quality or "major")
        degree_offset = _roman_degree(roman, mode)

        # Compute root MIDI
        cell_root = root_midi + degree_offset

        # Get chord tones
        tones = chord_tones(cell_root, quality)

        # Check for matching HarmonicDevice
        device_hint = None
        if devices:
            matching = self._find_matching_device(cell, devices)
            if matching and matching.voice_leading_hints:
                device_hint = matching.voice_leading_hints[0]

        # Apply inversion. A figured symbol ("V65", "I64") carries its own
        # inversion; ignoring it and reading only ``cell.inversion`` put every
        # chord the corpus spells in inversion back into root position, which is
        # exactly the stepwise-bass writing that inversions exist to produce.
        inversion = cell.inversion or _roman_inversion(roman, mode)
        bass_midi = tones[inversion % len(tones)] if tones else cell_root

        # If device provides bass guidance, apply as soft influence
        if device_hint and prev and "bass_midi" in prev:
            bass_midi = self._apply_device_bass_hint(
                device_hint, prev["bass_midi"], bass_midi, tones
            )

        # Place bass in register
        bass_midi = self._place_in_range(bass_midi, bass_range)

        # Place soprano — use device hint or voice-leading hint
        soprano_hint = device_hint or cell.voice_leading_hint
        soprano_midi = self._choose_soprano(tones, sop_range, prev, soprano_hint, bass=bass_midi)

        # Fill inner voices
        alto_midi, tenor_midi = self._fill_inner(tones, soprano_midi, bass_midi)

        return {
            "bar": cell.bar,
            "beat": cell.beat,
            "soprano": midi_to_pitch(soprano_midi, key),
            "alto": midi_to_pitch(alto_midi, key),
            "tenor": midi_to_pitch(tenor_midi, key),
            "bass": midi_to_pitch(bass_midi, key),
            "soprano_midi": soprano_midi,
            "alto_midi": alto_midi,
            "tenor_midi": tenor_midi,
            "bass_midi": bass_midi,
            "quality": quality,
            "inversion": inversion,
            "roman": roman,
            "key": cell.key or key,
        }

    def _place_in_range(self, midi: int, range_: Tuple[int, int]) -> int:
        """Place a pitch class within a register range."""
        pc = midi % 12
        low, high = range_
        best = low + pc
        while best < low:
            best += 12
        while best > high:
            best -= 12
        return max(low, min(high, best))

    def _choose_soprano(
        self,
        tones: List[int],
        sop_range: Tuple[int, int],
        prev: Optional[Dict],
        hint: Optional[str],
        bass: Optional[int] = None,
    ) -> int:
        """Choose soprano pitch with voice-leading optimization."""
        from .pitch import parallel_perfect

        candidates = []
        for tone in tones:
            placed = self._place_in_range(tone, sop_range)
            candidates.append(placed)

        if not candidates:
            return (sop_range[0] + sop_range[1]) // 2

        if prev and "soprano_midi" in prev:
            prev_sop = prev["soprano_midi"]
            # Hard-avoid outer-voice parallel 5ths/8ves against the chosen bass.
            if bass is not None and "bass_midi" in prev:
                safe = [
                    c
                    for c in candidates
                    if not parallel_perfect(prev_sop, prev["bass_midi"], c, bass)
                ]
                if safe:
                    candidates = safe
            # Choose candidate closest to previous soprano
            candidates.sort(key=lambda c: abs(c - prev_sop))
            # Apply hint if present
            if hint:
                hint_lower = hint.lower()
                if "descend" in hint_lower:
                    desc = [c for c in candidates if c <= prev_sop]
                    if desc:
                        return desc[0]
                elif "ascend" in hint_lower:
                    asc = [c for c in candidates if c >= prev_sop]
                    if asc:
                        return asc[0]
                elif "hold" in hint_lower or "sustain" in hint_lower:
                    closest = min(candidates, key=lambda c: abs(c - prev_sop))
                    return closest
            return candidates[0]

        # No previous — choose middle of range
        mid = (sop_range[0] + sop_range[1]) // 2
        candidates.sort(key=lambda c: abs(c - mid))
        return candidates[0]

    def _fill_inner(self, tones: List[int], soprano: int, bass: int) -> Tuple[int, int]:
        """Fill alto and tenor from remaining chord tones."""
        # Place remaining chord tones between bass and soprano
        inner_candidates = []
        for tone in tones:
            pc = tone % 12
            # Try all octaves between bass and soprano
            placed = bass + pc - (bass % 12)
            while placed < bass:
                placed += 12
            while placed <= soprano:
                if placed > bass and placed < soprano:
                    inner_candidates.append(placed)
                placed += 12

        if len(inner_candidates) >= 2:
            inner_candidates.sort()
            # THE INNER VOICES COMPLETE THE CHORD.
            #
            # Taking the lowest and highest candidate picks by REGISTER, and a
            # seventh chord has four notes for four voices: with the bass on the
            # root and the soprano on the fifth, the extremes can easily be two
            # octaves of the third, and the seventh — the note that makes it a
            # seventh chord — is never sounded.
            #
            # Measured on the assembled score: the plan asks for sevenths in
            # 19.5% of Mozart's chords and 9.8% of Chopin's, and the written
            # score analyses at 5.1% and 6.0% against their real 14.1% and
            # 17.8%. The harmony was planned correctly and thinned on the way
            # to the notes.
            #
            # So prefer pitch classes the outer voices do not already carry,
            # lowest and highest among those, and fall back to the register
            # extremes when the chord is a triad already fully covered.
            # ...and they must carry DIFFERENT pitch classes. Taking the
            # lowest and highest of the missing notes picks two octaves of the
            # same one where a chord has several placements — B2 and B4 for a
            # G7 whose bass is G and soprano D — which leaves the seventh out
            # just as surely as picking by register did.
            outer = {bass % 12, soprano % 12}
            missing = [c for c in inner_candidates if c % 12 not in outer]
            if len(missing) >= 2:
                tenor = missing[0]
                higher = [c for c in missing if c % 12 != tenor % 12]
                alto = higher[-1] if higher else missing[-1]
                if alto < tenor:
                    tenor, alto = alto, tenor
            elif len(missing) == 1:
                # One note still missing: give it a voice, and let the other
                # take whichever extreme is not its own pitch class.
                tenor = missing[0]
                others = [c for c in inner_candidates if c % 12 != tenor % 12]
                alto = others[-1] if others else inner_candidates[-1]
                if alto < tenor:
                    tenor, alto = alto, tenor
            else:
                tenor = inner_candidates[0]
                alto = inner_candidates[-1]
        elif len(inner_candidates) == 1:
            tenor = inner_candidates[0]
            alto = (tenor + soprano) // 2
            # Snap alto to nearest chord tone
            alto = self._place_in_range(tones[0], (tenor, soprano))
        else:
            # No inner tones fit — just split the range
            gap = soprano - bass
            tenor = bass + gap // 3
            alto = bass + 2 * gap // 3

        return alto, tenor

    def _apply_device_bass_hint(
        self, hint: str, prev_bass: int, default_bass: int, tones: List[int]
    ) -> int:
        """Apply a device voice-leading hint to bass note selection.

        This is a soft influence: if the hint suggests stepwise motion,
        try to find a chord tone close to the previous bass pitch. If no
        good option exists, fall back to the default bass.
        """
        hint_lower = hint.lower()
        if "step" in hint_lower or "descend" in hint_lower:
            # Try to find a chord tone that descends stepwise from prev
            candidates = [t for t in tones if 0 < prev_bass - t <= 3]
            if candidates:
                return max(candidates)  # closest descending step
        elif "ascend" in hint_lower:
            candidates = [t for t in tones if 0 < t - prev_bass <= 3]
            if candidates:
                return min(candidates)  # closest ascending step
        elif "hold" in hint_lower or "sustain" in hint_lower:
            if tones:
                return min(tones, key=lambda t: abs(t - prev_bass))
        return default_bass

    def _find_matching_device(
        self, cell: HarmonicCell, devices: List[HarmonicDevice]
    ) -> Optional[HarmonicDevice]:
        """Find a HarmonicDevice matching this cell's context."""
        function = cell.function or ""
        roman = cell.roman.lower() if cell.roman else ""

        for device in devices:
            if not device.contexts:
                continue
            for ctx in device.contexts:
                ctx_lower = ctx.lower()
                # Match by harmonic function
                if function and function.lower() in ctx_lower:
                    return device
                # Match by chord name
                if roman and roman in ctx_lower:
                    return device
                # Match by general context keywords
                if "cadent" in ctx_lower and "V" in cell.roman:
                    return device
                if "chromatic" in ctx_lower and cell.roman.startswith("b"):
                    return device
        return None
