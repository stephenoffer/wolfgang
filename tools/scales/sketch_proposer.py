"""
SketchProposer — generates K sketch candidates per phrase.

Uses the PhraseSlot (function, cadence, harmony, motif obligations),
StyleDNA (texture priors, harmonic language), and corpus retrieval
to propose multiple abstract sketches.

Claude may also write sketches directly via /w-compose; this module
generates the "engine-side" candidates that Claude adjudicates.
"""

from __future__ import annotations

import random
from fractions import Fraction

from .cadence_bank import CadenceBank
from .enums import (
    AccompType,
    CadenceTarget,
    HarmonicFunction,
    PhraseFunction,
    TextureType,
)
from .gesture_bank import GestureBank
from .models import (
    Anchor,
    BreathPoint,
    CadenceApproach,
    DynamicEvent,
    EntryExitState,
    GestureQuery,
    GestureResult,
    HarmonyEvent,
    MotifPlacement,
    PhraseQuery,
    PhraseResult,
    PhraseSlot,
    SketchIR,
    StyleDNA,
    TextureIntent,
)
from .phrase_bank import PhraseBank


class SketchProposer:
    """Generates K sketch candidates from a PhraseSlot + StyleDNA.

    Each sketch variant explores a different approach to the same
    phrase requirements — different contour shapes, texture choices,
    harmonic surprises, and breath placements.
    """

    def __init__(
        self, phrase_bank: PhraseBank, gesture_bank: GestureBank, cadence_bank: CadenceBank
    ):
        self.phrase_bank = phrase_bank
        self.gesture_bank = gesture_bank
        self.cadence_bank = cadence_bank

    def propose(self, slot: PhraseSlot, style_dna: StyleDNA, k: int = 3) -> list[SketchIR]:
        """Generate K sketch candidates for a phrase slot."""
        # Retrieve a phrase prototype to bias variant 0
        phrase_prototype = self._retrieve_phrase_prototype(slot)

        sketches = []
        for variant_idx in range(k):
            # Plan gesture sequence for this variant
            gesture_sequence = self._plan_gesture_sequence(slot, variant_idx)

            sketch = self._generate_variant(
                slot,
                style_dna,
                variant_idx,
                phrase_prototype=phrase_prototype if variant_idx == 0 else None,
                gesture_sequence=gesture_sequence,
            )
            sketches.append(sketch)
        return sketches

    def _generate_variant(
        self,
        slot: PhraseSlot,
        style_dna: StyleDNA,
        variant_idx: int,
        phrase_prototype: PhraseResult | None = None,
        gesture_sequence: list[GestureResult] | None = None,
    ) -> SketchIR:
        """Generate one sketch variant."""
        sketch = SketchIR(phrase_id=slot.phrase_id)

        # 1. Harmonic rhythm from slot's harmony plan
        sketch.harmonic_rhythm = self._build_harmonic_rhythm(slot)

        # 2. Melody anchors based on function and variant
        #    If a phrase prototype was retrieved, use its density_curve and
        #    register_curve to bias the contour for variant 0.
        sketch.melody_anchors = self._build_melody_anchors(
            slot,
            style_dna,
            variant_idx,
            phrase_prototype=phrase_prototype,
        )

        # 3. Bass anchors from harmony
        sketch.bass_anchors = self._build_bass_anchors(slot)

        # 4. Texture plan (varies by variant)
        sketch.texture_plan = self._build_texture_plan(slot, style_dna, variant_idx)

        # 5. Dynamic shape
        sketch.dynamic_shape = self._build_dynamic_shape(slot, variant_idx)

        # 6. Motif placements from obligations
        sketch.motif_placements = self._build_motif_placements(slot)

        # 7. Breath points
        sketch.breath_points = self._build_breath_points(slot, variant_idx)

        # 8. Cadence approach
        sketch.cadence = self._build_cadence(slot)

        # 9. Entry/exit signatures
        sketch.entry_signature = self._build_entry_signature(slot)
        sketch.exit_signature = self._build_exit_signature(slot)

        return sketch

    # ─── Harmonic Rhythm ──────────────────────────────────────────────────

    def _build_harmonic_rhythm(self, slot: PhraseSlot) -> list[HarmonyEvent]:
        """Build harmonic rhythm from the slot's harmony plan."""
        events = []
        for i, roman in enumerate(slot.harmony_plan):
            bar = slot.bar_start + i
            function = _classify_harmonic_function(roman)
            events.append(
                HarmonyEvent(
                    bar=bar,
                    beat=1.0,
                    roman=roman,
                    key=slot.key,
                    function=function,
                )
            )
        return events

    # ─── Melody Anchors ───────────────────────────────────────────────────

    def _build_melody_anchors(
        self,
        slot: PhraseSlot,
        style_dna: StyleDNA,
        variant_idx: int,
        phrase_prototype: PhraseResult | None = None,
    ) -> list[Anchor]:
        """Build melody anchors — structural pitches at key moments.

        Generates anchors on every bar (beat 1 and often beat 3) to ensure
        a dense, singable melodic line with clear contour.

        If a phrase_prototype is provided (variant 0), its density_curve
        and register_curve bias the contour shape — the prototype acts as
        a corpus-grounded starting point rather than a pure heuristic.
        """
        anchors = []
        bar_count = slot.bar_count

        # Variant strategies for contour shape
        # 0 = arch contour (peak at 2/3)
        # 1 = descending from high start
        # 2 = ascending with late peak
        peak_position = {
            0: int(bar_count * 0.67),
            1: 1,
            2: bar_count - 1,
        }.get(variant_idx % 3, int(bar_count * 0.67))

        # If we have a phrase prototype, use its register_curve to derive
        # a better peak position (the bar with highest register value).
        if phrase_prototype and phrase_prototype.register_curve:
            reg = phrase_prototype.register_curve
            if len(reg) >= 2:
                # Find the bar index with the highest register value
                max_reg_idx = reg.index(max(reg))
                # Scale to our bar_count
                scaled_peak = int(max_reg_idx * bar_count / max(len(reg) - 1, 1))
                peak_position = max(1, min(bar_count - 1, scaled_peak))

        # Build per-bar melody contour using scale degrees
        # This creates a smooth melodic arc across the phrase
        contour_degrees = self._build_contour(
            bar_count, peak_position, variant_idx, slot.cadence_target
        )

        # If prototype has a density_curve, use it to bias anchor weights:
        # denser bars get higher-weight anchors (more structurally important).
        prototype_density = None
        if phrase_prototype and phrase_prototype.density_curve:
            dc = phrase_prototype.density_curve
            # Interpolate density_curve to match bar_count
            if len(dc) >= 2:
                prototype_density = []
                for i in range(bar_count):
                    idx_f = i * (len(dc) - 1) / max(bar_count - 1, 1)
                    lo = int(idx_f)
                    hi = min(lo + 1, len(dc) - 1)
                    frac = idx_f - lo
                    prototype_density.append(dc[lo] * (1 - frac) + dc[hi] * frac)

        for i, degree in enumerate(contour_degrees):
            bar = slot.bar_start + i
            base_weight = 0.9 if i == 0 or i == bar_count - 1 else 0.7
            # Bias weight from prototype density (higher density → higher weight)
            if prototype_density and i < len(prototype_density):
                # density values are typically 0-20+; normalize to 0-1 boost
                density_boost = min(prototype_density[i] / 20.0, 1.0) * 0.15
                weight = min(1.0, base_weight + density_boost)
            else:
                weight = base_weight

            # Beat 1 anchor (structural)
            role = (
                "entry"
                if i == 0
                else "cadence"
                if i == bar_count - 1
                else "peak"
                if i == peak_position - 1
                else "structural"
            )
            anchors.append(
                Anchor(
                    bar=bar,
                    beat=1.0,
                    pitch_or_degree=degree,
                    weight=weight,
                    role=role,
                )
            )

            # Beat 3 anchor for inner-bar motion (creates stepwise melody)
            if i < bar_count - 1:
                next_degree = contour_degrees[i + 1]
                mid_degree = self._interpolate_degree(degree, next_degree, variant_idx)
                anchors.append(
                    Anchor(
                        bar=bar,
                        beat=_mid_bar_beat(slot.meter),
                        pitch_or_degree=mid_degree,
                        weight=0.5,
                        role="passing",
                    )
                )

        return anchors

    def _build_contour(self, bar_count: int, peak_pos: int, variant_idx: int, cadence: str) -> list:
        """Build a scale-degree contour for the full phrase.

        Two things were wrong here, and together they flattened every melody
        this proposer wrote.

        The templates were fixed lists of degrees 1-7 — ONE OCTAVE, by
        construction. A melody cannot use register structurally if its
        vocabulary stops at the seventh, and the `register_stasis` audit was
        measuring exactly that ceiling: 19 semitones across a whole piece,
        against a median of 33 over 336 real keyboard movements.

        And `peak_pos` — the climax position the caller computes per variant —
        was accepted and never read. The peak fell wherever the template
        happened to put it after interpolation, so an arch asked to peak at
        two-thirds peaked at the middle, and the one asked to peak late peaked
        early. The phrase's high point was decided by list arithmetic.

        Now the arc is built from its three structural points — where it opens,
        where it turns, where it closes — and the turn happens where the caller
        asked. Degrees run past the octave because that is how a climax is
        written: `^12` is the twelfth above the tonic, not a wrapped `^5`.
        """
        # (opening degree, turning degree, closing degree)
        profiles = [
            (1, 12, 1),  # arch — rise a twelfth to the climax and fall back
            (10, 3, 1),  # descent from a high opening
            (1, 10, 1),  # late peak
        ]
        open_deg, turn_deg, close_deg = profiles[variant_idx % 3]

        if bar_count <= 1:
            degrees = [f"^{turn_deg}"]
        else:
            turn_idx = min(max(int(peak_pos), 1), bar_count - 1)
            degrees = []
            for i in range(bar_count):
                if i <= turn_idx:
                    t = i / turn_idx
                    raw = open_deg + (turn_deg - open_deg) * t
                else:
                    t = (i - turn_idx) / (bar_count - 1 - turn_idx)
                    raw = turn_deg + (close_deg - turn_deg) * t
                degrees.append(f"^{max(1, min(14, round(raw)))}")

        # Force cadence soprano
        if cadence and cadence != "none":
            degrees[-1] = _cadence_soprano_degree(cadence)

        return degrees

    def _interpolate_degree(self, deg_a: str, deg_b: str, variant_idx: int) -> str:
        """Find a passing degree between two scale degrees."""
        a = int(deg_a[1:]) if deg_a.startswith("^") else 3
        b = int(deg_b[1:]) if deg_b.startswith("^") else 3
        mid = (a + b) // 2
        if mid == a:
            mid = a + (1 if variant_idx % 2 == 0 else -1)
        # Clamped to 7, which pulled every mid-bar anchor back inside one
        # octave even when the anchors it sits between were a tenth apart.
        mid = max(1, min(14, mid))
        return f"^{mid}"

    # ─── Bass Anchors ─────────────────────────────────────────────────────

    def _build_bass_anchors(self, slot: PhraseSlot) -> list[Anchor]:
        """Build bass anchors from the harmony plan."""
        anchors = []
        for i, roman in enumerate(slot.harmony_plan):
            bar = slot.bar_start + i
            bass_degree = _roman_to_bass_degree(roman)
            anchors.append(
                Anchor(
                    bar=bar,
                    beat=1.0,
                    pitch_or_degree=bass_degree,
                    weight=0.8,
                    role="structural",
                )
            )
        return anchors

    # ─── Texture Plan ─────────────────────────────────────────────────────

    def _build_texture_plan(
        self, slot: PhraseSlot, style_dna: StyleDNA, variant_idx: int
    ) -> list[TextureIntent]:
        """Build per-bar texture intent."""
        plan = []

        # Use slot's texture plan if provided
        if slot.texture_plan:
            for i, bar_tex in enumerate(slot.texture_plan):
                plan.append(
                    TextureIntent(
                        bar=slot.bar_start + i,
                        rh_type=bar_tex.rh_texture,
                        lh_type=bar_tex.lh_texture,
                        density_target=bar_tex.rh_density_target,
                        gesture_family=bar_tex.gesture_family,
                    )
                )
            return plan

        # Generate from style priors with variation per variant
        rh_options = list(style_dna.rh_distribution.keys()) or [TextureType.SINGING_MELODY.value]
        lh_options = list(style_dna.lh_distribution.keys()) or [AccompType.ALBERTI.value]

        # Weight-based selection with variant offset
        for i in range(slot.bar_count):
            bar = slot.bar_start + i

            # Vary texture every 2-4 bars
            if i == 0 or (i % (2 + variant_idx % 3) == 0):
                rh = _weighted_choice(style_dna.rh_distribution, rh_options[0])
                lh = _weighted_choice(style_dna.lh_distribution, lh_options[0])
            # Keep previous texture

            density = 8 + variant_idx * 2  # slight density variation
            plan.append(
                TextureIntent(
                    bar=bar,
                    rh_type=rh,
                    lh_type=lh,
                    density_target=density,
                )
            )

        return plan

    # ─── Dynamic Shape ────────────────────────────────────────────────────

    def _build_dynamic_shape(self, slot: PhraseSlot, variant_idx: int) -> list[DynamicEvent]:
        """Build dynamic events."""
        events = []
        curves = slot.curves.energy or [0.5] * slot.bar_count

        for i, energy in enumerate(curves):
            bar = slot.bar_start + i
            level = _energy_to_dynamic(energy)
            hairpin = None
            if i < len(curves) - 1:
                if curves[i + 1] > energy + 0.15:
                    hairpin = "cresc"
                elif curves[i + 1] < energy - 0.15:
                    hairpin = "decresc"
            events.append(
                DynamicEvent(
                    bar=bar,
                    beat=1.0,
                    level=level,
                    hairpin=hairpin,
                )
            )

        return events

    # ─── Motif Placements ─────────────────────────────────────────────────

    def _build_motif_placements(self, slot: PhraseSlot) -> list[MotifPlacement]:
        """Build motif placements from obligations."""
        placements = []
        for mt in slot.motif_transforms:
            placements.append(
                MotifPlacement(
                    bar=slot.bar_start,
                    beat=1.0,
                    motif_id=mt.params.get("motif_id", ""),
                    transform=mt.operation,
                    voice="melody",
                    params=mt.params,
                )
            )
        return placements

    # ─── Breath Points ────────────────────────────────────────────────────

    def _build_breath_points(self, slot: PhraseSlot, variant_idx: int) -> list[BreathPoint]:
        """Place breath/rest points."""
        points = []
        # Breath at phrase midpoint
        mid = slot.bar_start + slot.bar_count // 2
        points.append(
            BreathPoint(
                bar=mid,
                beat=_breath_beat(slot.meter, variant_idx),
                type="breath",
            )
        )
        return points

    # ─── Cadence ──────────────────────────────────────────────────────────

    def _build_cadence(self, slot: PhraseSlot) -> CadenceApproach:
        """Build cadence approach from slot targets."""
        arrival_bar = slot.cadence_bar or (slot.bar_start + slot.bar_count - 1)
        approach_bar = max(arrival_bar - 1, slot.bar_start)
        # A slot whose plan says "none" is asking for NO cadence. Unguarded, the
        # tables below handed it the PAC's answers — soprano ^1 over V-I — so a
        # phrase explicitly planned not to close was given the strongest close
        # available. `_cadence_soprano_degree`'s caller already guards this; this
        # one did not.
        target = (slot.cadence_target or "").strip()
        if not target or target == CadenceTarget.NONE.value:
            return CadenceApproach(
                type=target,
                approach_bar=approach_bar,
                arrival_bar=arrival_bar,
                soprano_arrival_degree=0,
                bass_motion="",
            )
        return CadenceApproach(
            type=slot.cadence_target,
            approach_bar=approach_bar,
            arrival_bar=arrival_bar,
            soprano_arrival_degree=_cadence_soprano_int(slot.cadence_target),
            bass_motion=_cadence_bass_motion(slot.cadence_target),
        )

    # ─── Entry/Exit ───────────────────────────────────────────────────────

    def _build_entry_signature(self, slot: PhraseSlot) -> EntryExitState:
        return EntryExitState(
            pitch=slot.continuation.last_soprano_pitch,
            texture_rh=slot.continuation.last_rh_texture,
            texture_lh=slot.continuation.last_lh_texture,
            dynamic=slot.continuation.last_dynamic,
            last_chord=slot.continuation.last_chord,
        )

    def _build_exit_signature(self, slot: PhraseSlot) -> EntryExitState:
        return EntryExitState()

    # ─── Retrieval Helpers ───────────────────────────────────────────────

    def _retrieve_phrase_prototype(self, slot: PhraseSlot) -> PhraseResult | None:
        """Retrieve a phrase prototype from PhraseBank to ground variant 0.

        Builds a PhraseQuery from the PhraseSlot's structural properties
        and returns the best match, or None if the bank is empty or lookup fails.
        """
        try:
            key_mode = "minor" if slot.key.endswith("m") else "major"
            # The same three dimensions the brief now fills — 0.20 of the
            # ranking that was a flat 0.5 for every candidate. See
            # `composition_brief._slot_contour_class`.
            from .composition_brief import _slot_contour_class, _slot_entry_texture

            query = PhraseQuery(
                formal_function=slot.function,
                cadence_type=slot.cadence_target if slot.cadence_target != "none" else None,
                length_range=(max(1, slot.bar_count - 1), slot.bar_count + 1),
                key_mode=key_mode,
                cadence_distance=slot.bar_count,
                contour_class=_slot_contour_class(slot),
                entry_texture=_slot_entry_texture(slot),
                n=1,
            )
            results = self.phrase_bank.retrieve(query)
            if results:
                return results[0]
        except Exception:
            pass
        return None

    def _plan_gesture_sequence(self, slot: PhraseSlot, variant_idx: int) -> list[GestureResult]:
        """Plan a sequence of gestures for a phrase based on its function.

        Maps phrase function to an ordered sequence of gesture functions,
        queries GestureBank for each, and returns up to 3 results.
        """
        # Map phrase function → ordered gesture function sequence
        _FUNCTION_TO_GESTURES = {
            PhraseFunction.PRESENTATION.value: ["pickup", "answer"],
            PhraseFunction.CONTINUATION.value: ["sequence_step", "cadential_push"],
            PhraseFunction.CADENTIAL.value: ["arrival"],
            PhraseFunction.CLOSING.value: ["cadential_release", "sustain"],
            PhraseFunction.TRANSITION.value: ["sequence_step", "lean_in"],
            PhraseFunction.SEQUENCE.value: ["sequence_step", "sequence_step"],
            PhraseFunction.FRAGMENTATION.value: ["insist", "cadential_push"],
            PhraseFunction.RETRANSITION.value: ["lean_in", "arrival"],
            PhraseFunction.INTRODUCTION.value: ["pickup"],
            PhraseFunction.CODETTA.value: ["cadential_release"],
            PhraseFunction.CODA.value: ["sustain", "cadential_release"],
            # Eleven of the enum's members were listed and the rest fell through
            # to the PRESENTATION gestures, so a phrase that RETURNS the theme —
            # the recapitulation, the payoff — was given "pickup, answer", the
            # gestures of a beginning. Measured over 426 slots in `workspace/`,
            # 31% took that fallback, led by `contrasting_theme` (56) and
            # `return` (49), both of which ARE enum members.
            PhraseFunction.CONTRASTING_THEME.value: ["pickup", "answer"],
            PhraseFunction.RETURN.value: ["arrival", "answer"],
            PhraseFunction.RETURN_VARIED.value: ["arrival", "answer"],
            PhraseFunction.LIQUIDATION.value: ["cadential_release"],
            PhraseFunction.EPISODE.value: ["sequence_step", "answer"],
            # ...and the vocabulary the planner writes that the enum does not
            # contain at all. Names are drawn from the four gesture families
            # (`_same_gesture_family`): initiate, drive, resolve, answer.
            "development": ["sequence_step", "insist"],
            "extension": ["sequence_step", "cadential_push"],
            "climactic": ["insist", "arrival"],
            "climax": ["insist", "arrival"],
            "standing_on_dominant": ["insist", "lean_in"],
            "resolution": ["cadential_release", "sustain"],
            "recapitulation": ["arrival", "answer"],
            "false_recap": ["arrival", "answer"],
            "varied_return": ["arrival", "answer"],
            "contrasting": ["pickup", "answer"],
        }

        gesture_functions = _FUNCTION_TO_GESTURES.get(
            (slot.function or "").strip(), ["pickup", "answer"]
        )

        results: list[GestureResult] = []
        try:
            for gfn in gesture_functions:
                if len(results) >= 3:
                    break
                query = GestureQuery(function=gfn, n=1)
                hits = self.gesture_bank.retrieve(query)
                if hits:
                    results.append(hits[0])
        except Exception:
            pass
        return results


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _classify_harmonic_function(roman: str) -> str:
    """Classify a Roman numeral chord as tonic/predominant/dominant/chromatic.

    Delegates to `harmony_analysis`, which owns Roman-numeral parsing. This was
    an exact-match table over eleven spellings with a fallback of
    ``return TONIC`` — so every numeral it did not literally list came back
    TONIC, and the ones it did not list are the inversions and sevenths that
    make up most of real music:

        ii65 IV6 iv6   -> tonic, should be predominant
        V65 V43 V42    -> tonic, should be DOMINANT
        viio6 viio7 vii07 -> tonic, should be DOMINANT

    Nine of twenty-two common numerals wrong, six of them dominants read as
    tonic — which inverts the tension of every cadence built on one. The
    canonical `parse_roman` + `classify_function` path gets all twenty-two
    right, and it is the same pair that already round-trips 9,216 combinations
    of degree, quality and inversion.
    """
    from .harmony_analysis import classify_function, parse_roman

    parsed = parse_roman((roman or "").strip(), "major")
    if not parsed:
        return HarmonicFunction.CHROMATIC.value
    return classify_function(parsed["degree"] % 12, parsed["quality"], 0, "major")


def _roman_to_bass_degree(roman: str) -> str:
    """The scale degree in the BASS for a Roman numeral, as `^n`.

    This was a hand-written dict of about twenty spellings ending in
    `return "^1"`, so every numeral it did not list put the TONIC in the bass:

        bVI -> ^1    V/V -> ^1    viio7 -> ^1    #ivo -> ^1

    A chromatic chord over a tonic bass is not that chord. Same shape as the
    harmonic-function table in Addendum 73 — an exact-match table whose fallback
    is the most stable answer available, which is the most damaging one to be
    wrong with.

    Derived instead from `harmony_analysis`: parse the numeral, take the chord's
    template, pick the member the inversion puts in the bass, and name the scale
    degree closest to it. Falls back to `^1` only when the numeral does not parse
    at all.
    """
    from .harmony_analysis import roman_bass_offset

    bass_pc = roman_bass_offset(roman)
    if bass_pc is None:
        return "^1"
    # Name it as a major-scale degree; chromatic bass notes take the nearest
    # degree below with an accidental, which is how they are written.
    major = (0, 2, 4, 5, 7, 9, 11)
    if bass_pc in major:
        return f"^{major.index(bass_pc) + 1}"
    below = max(i for i, pc in enumerate(major) if pc < bass_pc)
    return f"^#{below + 1}"

def _cadence_soprano_degree(cadence_type: str) -> str:
    """Target soprano degree for a cadence type."""
    mapping = {
        CadenceTarget.PAC.value: "^1",
        CadenceTarget.IAC.value: "^3",
        CadenceTarget.HC.value: "^2",
        CadenceTarget.DC.value: "^1",
        CadenceTarget.PLAGAL.value: "^1",
        # An EVADED cadence is defined by the resolution NOT arriving — the
        # soprano avoids the tonic and the bass goes somewhere other than I.
        # It was falling through to the PAC default and being handed ^1 over
        # V-I, which is the exact opposite of the gesture.
        CadenceTarget.EVADED.value: "^2",
    }
    return mapping.get(cadence_type, "^1")


def _cadence_soprano_int(cadence_type: str) -> int:
    mapping = {
        CadenceTarget.PAC.value: 1,
        CadenceTarget.IAC.value: 3,
        CadenceTarget.HC.value: 2,
        CadenceTarget.DC.value: 1,
        CadenceTarget.PLAGAL.value: 1,
        CadenceTarget.EVADED.value: 2,
    }
    return mapping.get(cadence_type, 1)


def _cadence_bass_motion(cadence_type: str) -> str:
    mapping = {
        CadenceTarget.PAC.value: "V-I",
        CadenceTarget.HC.value: "?-V",
        CadenceTarget.DC.value: "V-vi",
        CadenceTarget.PLAGAL.value: "IV-I",
        CadenceTarget.IAC.value: "V-I",
        # The dominant arrives and its resolution is withheld.
        CadenceTarget.EVADED.value: "V-?",
    }
    return mapping.get(cadence_type, "V-I")


def _energy_to_dynamic(energy: float) -> str:
    """Convert 0-1 energy to dynamic marking."""
    if energy < 0.2:
        return "pp"
    if energy < 0.35:
        return "p"
    if energy < 0.5:
        return "mp"
    if energy < 0.65:
        return "mf"
    if energy < 0.8:
        return "f"
    return "ff"


def _beat_positions(meter: tuple[int, int]) -> list[float]:
    """The ONE-BASED positions of a bar's metrical beats.

    Beats are one-based here, so a bar of length `d` spans `[1.0, 1.0 + d)`
    and `float(num)` is not a position in any metre but n/4. In 6/8 it named
    beat 6.0, a full two quarters past a bar that ends at 4.0.

    A compound metre is counted in dotted beats — 6/8 has two, not six — which
    is what makes 2.5 (the second dotted beat) the mid-bar position rather than
    an offbeat.
    """
    num, denom = meter
    if num > 3 and num % 3 == 0:
        unit = Fraction(4, denom) * 3
        count = num // 3
    else:
        unit = Fraction(4, denom)
        count = num
    return [float(1 + unit * i) for i in range(max(1, count))]


def _mid_bar_beat(meter: tuple[int, int]) -> float:
    """The strong interior beat a mid-bar anchor belongs on.

    This was hardcoded to 3.0 — the midpoint of a 4/4 bar and of nothing else.
    In 2/4 it is the barline exactly, so every mid-bar anchor in the phrase was
    written outside its bar and dropped by the repair pass. 4/4 still resolves
    to 3.0, so the common case is unchanged.
    """
    positions = _beat_positions(meter)
    return positions[len(positions) // 2] if len(positions) > 1 else positions[0]


def _breath_beat(meter: tuple[int, int], variant_idx: int) -> float:
    """Choose a beat position for a breath — late in the bar."""
    num, denom = meter
    if num == 4 and denom == 4:
        return [4.0, 3.0, 4.5][variant_idx % 3]
    if num == 3 and denom == 4:
        return [3.0, 2.0][variant_idx % 2]
    positions = _beat_positions(meter)
    tail = positions[-2:]
    return tail[(len(tail) - 1 - variant_idx) % len(tail)]


def _weighted_choice(distribution: dict[str, float], default: str) -> str:
    """Choose from a weighted distribution."""
    if not distribution:
        return default
    items = list(distribution.items())
    total = sum(v for _, v in items)
    if total <= 0:
        return default
    r = random.random() * total
    cumulative = 0.0
    for key, weight in items:
        cumulative += weight
        if r <= cumulative:
            return key
    return items[-1][0]
