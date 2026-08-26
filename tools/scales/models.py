"""
Core data models for the SCALES system.

Every object in the system is defined here. The PieceGraph is the single
source of truth; all other models are nodes, edges, or payloads within it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .enums import (
    AccompType,
    CadenceTarget,
    CompositionMode,
    ExpectationDomain,
    ExpectationStatus,
    ExpectationType,
    HarmonicFunction,
    MotifTransformOp,
    NoteRole,
    PhraseFunction,
    PhraseStatus,
    SalienceLevel,
    SupportTier,
    TextureType,
    WorkScale,
)

# ─── Source & Target Specs ───────────────────────────────────────────────────


@dataclass
class SourceReference:
    """Reference to an input score for score-to-score modes."""

    path: str = ""
    format: str = "musicxml"  # musicxml | midi | abc
    movements: Optional[List[int]] = None  # which movements to use; None = all


@dataclass
class LockPolicy:
    """What to preserve from the source in score-to-score modes.

    Each value is 0.0 (completely overwrite) to 1.0 (preserve exactly).
    """

    principal_melody: float = 0.0
    bass_foundation: float = 0.0
    cadence_hits: float = 0.0
    counterline: float = 0.0
    color_events: float = 0.0
    phrase_count: float = 0.0
    key_scheme: float = 0.0
    form_layout: float = 0.0


@dataclass
class PhysicalConstraints:
    """Hard physical constraints that are never violated."""

    max_hand_span_semitones: int = 16
    max_notes_per_hand: int = 5
    min_tempo_bpm: int = 40
    max_tempo_bpm: int = 200
    # Voice ranges (MIDI): extended piano range
    piano_low: int = 21  # A0
    piano_high: int = 108  # C8


@dataclass
class TargetSpec:
    """What the output should be."""

    instrumentation: str = "solo_piano"
    difficulty: str = "advanced"  # beginner | intermediate | advanced | virtuoso
    movements: int = 1
    reduction_mode: Optional[str] = None  # study | playable | concert


@dataclass
class StyleBlendSpec:
    """How the output should sound stylistically."""

    type: str = "single"  # single | blend | transfer
    axes: Dict[str, Dict[str, float]] = field(default_factory=dict)
    # Example: {"pianism": {"Liszt": 0.85}, "harmony": {"source_preserve": 0.7}}
    primary_composer: str = ""
    era: str = ""
    genre: str = ""


# ─── PieceContract ───────────────────────────────────────────────────────────


@dataclass
class PieceContract:
    """The immutable intent document. First Claude output for any request."""

    piece_id: str = ""
    mode: str = CompositionMode.COMPOSE_FROM_TEXT.value
    description: str = ""
    source: Optional[SourceReference] = None
    target: TargetSpec = field(default_factory=TargetSpec)
    style: StyleBlendSpec = field(default_factory=StyleBlendSpec)
    locks: LockPolicy = field(default_factory=LockPolicy)
    constraints: PhysicalConstraints = field(default_factory=PhysicalConstraints)


# ─── StyleDNA ────────────────────────────────────────────────────────────────


@dataclass
class FingerprintRule:
    """A style fingerprint extracted from composition-guide.md."""

    id: str = ""
    name: str = ""
    description: str = ""
    texture_affinities: List[str] = field(default_factory=list)
    texture_exclusions: List[str] = field(default_factory=list)
    density_range: Optional[Tuple[float, float]] = None
    register_implication: Optional[str] = None
    frequency: str = "per_section"  # per_section | per_phrase | occasional
    detection_heuristic: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FingerprintRuleSet:
    """Collection of fingerprint rules with a required count."""

    required_count: int = 3
    items: List[FingerprintRule] = field(default_factory=list)


@dataclass
class CadenceRule:
    """A cadence pattern from the harmonic vocabulary."""

    name: str = ""
    type: str = ""  # PAC, HC, DC, etc.
    chords: List[str] = field(default_factory=list)
    soprano_rule: str = ""
    bass_rule: str = ""
    strength: int = 1  # 1-5
    frequency_weight: float = 0.5


@dataclass
class ChromaticTechnique:
    """A chromatic technique from harmonic-language.md."""

    name: str = ""
    frequency_weight: float = 0.5
    context: str = ""
    harmonic_function: str = ""


@dataclass
class ProgressionEdge:
    """A weighted edge in the harmonic progression graph."""

    target: str = ""
    weight: float = 0.5
    context: str = ""


@dataclass
class DensityTarget:
    """Density targets for a tempo class."""

    rh_mean: float = 8.0
    lh_mean: float = 6.0
    rh_range: Tuple[float, float] = (4.0, 16.0)
    lh_range: Tuple[float, float] = (2.0, 16.0)


@dataclass
class FormTemplate:
    """A form template for one form type."""

    sections: List[Dict[str, Any]] = field(default_factory=list)
    key_scheme: Dict[str, Any] = field(default_factory=dict)
    coda_behavior: str = "brief"


@dataclass
class PhraseStructureRules:
    """Default phrase structure rules."""

    default_period_length: int = 8
    antecedent_cadence: str = "HC"
    consequent_cadence: str = "PAC"
    extension_frequency: float = 0.2


@dataclass
class InstrumentRole:
    """Orchestration role for an instrument."""

    name: str = ""
    role: str = ""
    characteristic_usage: str = ""
    register_range: Tuple[int, int] = (60, 84)
    doubling_partners: List[str] = field(default_factory=list)
    solo_frequency: str = "occasional"


@dataclass
class PeriodOverlay:
    """Modifications for a specific composer period (early/middle/late)."""

    id: str = ""
    years: str = ""
    stat_modifiers: Dict[str, float] = field(default_factory=dict)
    rule_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StyleDNA:
    """Compiled style profile. NOT prose — all numeric/structural."""

    composer_id: str = ""
    tier: str = SupportTier.TIER_D.value

    # Fingerprints
    fingerprints: FingerprintRuleSet = field(default_factory=FingerprintRuleSet)

    # Distribution priors
    lh_distribution: Dict[str, float] = field(default_factory=dict)
    rh_distribution: Dict[str, float] = field(default_factory=dict)
    combo_distribution: Dict[str, float] = field(default_factory=dict)
    transition_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Density targets by tempo class
    density_targets: Dict[str, DensityTarget] = field(default_factory=dict)

    # Harmonic language
    cadence_vocabulary: List[CadenceRule] = field(default_factory=list)
    chromatic_techniques: List[ChromaticTechnique] = field(default_factory=list)
    progression_graph: Dict[str, List[ProgressionEdge]] = field(default_factory=dict)

    # Formal grammar
    form_templates: Dict[str, FormTemplate] = field(default_factory=dict)
    phrase_structure: PhraseStructureRules = field(default_factory=PhraseStructureRules)

    # Orchestration
    orchestration_roles: Dict[str, InstrumentRole] = field(default_factory=dict)

    # Period overlay
    active_period: Optional[PeriodOverlay] = None

    # Blend metadata
    axis_ownership: Optional[Dict[str, str]] = None
    blend_weights: Optional[Dict[str, float]] = None


# ─── MotifObject ─────────────────────────────────────────────────────────────


@dataclass
class MotifTransform:
    """A specific transform applied to a motif."""

    operation: str = MotifTransformOp.STATE.value
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MotifObject:
    """A musical character with identity, transforms, and appearances."""

    motif_id: str = ""
    character: str = ""  # narrative description
    scale_degree_contour: List[int] = field(default_factory=list)
    interval_contour: List[int] = field(default_factory=list)
    rhythm_cell: List[str] = field(default_factory=list)
    accent_profile: List[float] = field(default_factory=list)

    recognition_anchor: Dict[str, Any] = field(default_factory=dict)
    phrase_functions: List[str] = field(default_factory=list)
    harmonic_contexts: List[str] = field(default_factory=list)
    accompaniment_hints: List[str] = field(default_factory=list)
    typical_registers: List[Tuple[int, int]] = field(default_factory=list)

    allowed_transforms: List[str] = field(default_factory=list)
    appearances: List[Dict[str, Any]] = field(default_factory=list)


# ─── Narrative Arc ───────────────────────────────────────────────────────────


@dataclass
class NarrativeSection:
    """One section in the emotional narrative."""

    id: str = ""
    label: str = ""
    bar_start: int = 1
    bar_end: int = 8
    energy_curve: List[float] = field(default_factory=list)
    tension_curve: List[float] = field(default_factory=list)
    density_curve: List[float] = field(default_factory=list)
    brightness_curve: List[float] = field(default_factory=list)
    climax_type: Optional[str] = None  # primary | secondary | anti-climax
    # Authored prose intent — the dramatic EVENT this section enacts, written by
    # the agent at plan time (e.g. "the storm finally breaks, after three failed
    # attempts to rise"). This, not the curve-averaged adjectives, is what drives
    # the notes. Mirrors MotifObject.character.
    character: str = ""
    gesture: str = ""  # optional: the physical/gestural shape (e.g. "a long exhale")


@dataclass
class NarrativeArc:
    """Full emotional trajectory of the piece."""

    sections: List[NarrativeSection] = field(default_factory=list)
    primary_climax_section: str = ""
    overall_character: str = ""


# ─── Form Graph ──────────────────────────────────────────────────────────────


@dataclass
class MovementSpec:
    """One movement in the piece."""

    id: str = ""
    form: str = ""  # sonata | ternary | rondo | theme_variations | fugue | free
    key: str = "C"
    tempo_bpm: int = 120
    meter: Tuple[int, int] = (4, 4)
    tempo_marking: str = ""
    sections: List[str] = field(default_factory=list)  # section_ids


@dataclass
class SectionSpec:
    """One section in a movement."""

    id: str = ""
    movement_id: str = ""
    role: str = ""  # exposition | development | recapitulation | coda | A | B | etc.
    key: str = "C"
    bar_start: int = 1
    bar_end: int = 8
    phrase_ids: List[str] = field(default_factory=list)


@dataclass
class FormGraph:
    """The full formal structure of the piece."""

    movements: List[MovementSpec] = field(default_factory=list)
    sections: Dict[str, SectionSpec] = field(default_factory=dict)


# ─── PhraseSlot (planning IR) ───────────────────────────────────────────────


@dataclass
class BarTexturePlan:
    """Texture plan for a single bar."""

    rh_texture: str = TextureType.SINGING_MELODY.value
    lh_texture: str = AccompType.ALBERTI.value
    rh_density_target: int = 8
    lh_density_target: int = 6
    gesture_family: str = ""


@dataclass
class PhraseCurves:
    """0-1 normalized control curves, one value per bar."""

    energy: List[float] = field(default_factory=list)
    tension: List[float] = field(default_factory=list)
    density: List[float] = field(default_factory=list)
    register: List[float] = field(default_factory=list)
    brightness: List[float] = field(default_factory=list)
    articulation: List[float] = field(default_factory=list)


@dataclass
class ContinuationContext:
    """DEAD REPRESENTATION — do not write to this, and do not read it.

    The live continuity path is ``composition_brief._derive_continuation``, which
    reads these same facts off the previous phrase's REALIZED notes and returns
    them as the ``continuation`` dict inside ``_transition_context`` /
    ``get_phrase_continuity``. That is what the brief renders.

    This dataclass declares thirteen fields and **no code outside this module has
    ever written one of them**. It sits on every PhraseSlot and is serialized on
    every save, so it survives here only so that existing graphs still load; a
    future reader would otherwise reasonably assume the declared representation
    is the real one. Two representations of one idea, with one of them dead, is
    the hazard this project keeps getting bitten by — see
    `docs/AUDIT-CORPUS-2026-08-26.md`.
    """

    last_soprano_pitch: Optional[str] = None
    last_bass_pitch: Optional[str] = None
    last_soprano_contour: Optional[str] = None
    last_chord: Optional[str] = None
    last_key: Optional[str] = None
    pending_resolution: Optional[str] = None
    last_rh_density: Optional[float] = None
    last_lh_density: Optional[float] = None
    last_rh_texture: Optional[str] = None
    last_lh_texture: Optional[str] = None
    last_dynamic: Optional[str] = None
    motifs_stated: List[str] = field(default_factory=list)
    motifs_developed: List[str] = field(default_factory=list)


@dataclass
class PhraseSlot:
    """What a phrase IS — its role, constraints, and targets."""

    phrase_id: str = ""
    section_id: str = ""
    bar_start: int = 1
    bar_count: int = 4
    function: str = PhraseFunction.PRESENTATION.value
    cadence_target: str = CadenceTarget.NONE.value
    cadence_bar: Optional[int] = None
    # Beats of anacrusis before the phrase's first full bar (0 = downbeat start).
    pickup_beats: float = 0.0
    key: str = "C"
    meter: Tuple[int, int] = (4, 4)
    tempo_bpm: int = 120
    harmony_plan: List[str] = field(default_factory=list)
    # Per bar, the harmonies the bar moves THROUGH (empty = holds one chord).
    # Additive alongside harmony_plan, which stays one-roman-per-bar so every
    # existing consumer is unaffected.
    harmony_detail: List[List[str]] = field(default_factory=list)
    motif_transforms: List[MotifTransform] = field(default_factory=list)
    texture_plan: List[BarTexturePlan] = field(default_factory=list)
    curves: PhraseCurves = field(default_factory=PhraseCurves)
    continuation: ContinuationContext = field(default_factory=ContinuationContext)
    forward_context: Optional[str] = None  # what the next phrase is
    # ─── What this phrase is FOR (dramatic_plan.py) ───────────────────────
    # A phrase used to know its cadence and its bar count and nothing about why
    # it exists, so every one came out locally optimal and the piece had no arc.
    dramatic_role: str = ""  # establish|extend|depart|intensify|crisis|
    # retreat|return|confirm|close
    climax_distance: int = 0  # phrases from the piece's peak (0 = it IS)
    return_strategy: str = ""  # how a RETURN must differ from the statement
    return_strategy_detail: str = ""
    key_motion: str = ""  # prolong | depart | arrive
    pivot_hint: str = ""  # tones common to the old and new key
    section_techniques: List[str] = field(default_factory=list)  # from SectionContract
    # Free-text character note from the form spec (e.g. "variation 2 — minore").
    # Surfaced in the brief so a variation set actually varies in character.
    notes: str = ""
    # "" | "downbeat" | "anacrusis" — whether this phrase enters on the downbeat
    # or with an upbeat. Measured over the corpus, 46% of Mozart's movements and
    # 57% of Beethoven's open with a pickup bar; NONE of the twelve pieces in
    # workspace/ ever has. The shorthand and the engraver have supported an
    # anacrusis for some time — nothing ever asked for one.
    metric_entry: str = ""


# ─── SketchIR (what Claude writes) ──────────────────────────────────────────


@dataclass
class Anchor:
    """A structural pitch event — melody or bass anchor."""

    bar: int = 1
    beat: float = 1.0
    pitch_or_degree: str = ""  # "C5" or "^5" (scale degree)
    weight: float = 1.0
    role: str = "structural"  # structural | peak | cadence | motif | entry | exit


@dataclass
class HarmonyEvent:
    """A chord change in the harmonic rhythm."""

    bar: int = 1
    beat: float = 1.0
    roman: str = "I"
    key: str = "C"
    function: str = HarmonicFunction.TONIC.value


@dataclass
class TextureIntent:
    """Texture plan for a single bar in the sketch."""

    bar: int = 1
    rh_type: str = TextureType.SINGING_MELODY.value
    lh_type: str = AccompType.ALBERTI.value
    density_target: int = 8
    gesture_family: str = ""


@dataclass
class DynamicEvent:
    """A dynamic marking."""

    bar: int = 1
    beat: float = 1.0
    level: str = "mf"
    hairpin: Optional[str] = None  # cresc | decresc | None


@dataclass
class ExpressionMark:
    """An expression marking."""

    bar: int = 1
    beat: float = 1.0
    mark: str = ""  # cantabile | dolce | espressivo | etc.


@dataclass
class MotifPlacement:
    """Where a motif appears in the sketch."""

    bar: int = 1
    beat: float = 1.0
    motif_id: str = ""
    transform: str = MotifTransformOp.STATE.value
    voice: str = "melody"  # melody | bass | inner
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BreathPoint:
    """A planned silence or breath."""

    bar: int = 1
    beat: float = 1.0
    type: str = "rest"  # rest | breath | caesura


@dataclass
class CadenceApproach:
    """How the cadence is approached and arrived at."""

    type: str = CadenceTarget.PAC.value
    approach_bar: int = 7
    arrival_bar: int = 8
    soprano_arrival_degree: int = 1
    bass_motion: str = "V-I"


@dataclass
class EntryExitState:
    """Boundary state for transition continuity."""

    pitch: Optional[str] = None
    register_center: Optional[int] = None
    density: Optional[int] = None
    texture_rh: Optional[str] = None
    texture_lh: Optional[str] = None
    dynamic: Optional[str] = None
    last_chord: Optional[str] = None


@dataclass
class SketchIR:
    """What Claude composes: structural content, NOT final notes."""

    phrase_id: str = ""
    melody_anchors: List[Anchor] = field(default_factory=list)
    bass_anchors: List[Anchor] = field(default_factory=list)
    harmonic_rhythm: List[HarmonyEvent] = field(default_factory=list)
    texture_plan: List[TextureIntent] = field(default_factory=list)
    dynamic_shape: List[DynamicEvent] = field(default_factory=list)
    expression_marks: List[ExpressionMark] = field(default_factory=list)
    motif_placements: List[MotifPlacement] = field(default_factory=list)
    breath_points: List[BreathPoint] = field(default_factory=list)
    cadence: CadenceApproach = field(default_factory=CadenceApproach)
    entry_signature: EntryExitState = field(default_factory=EntryExitState)
    exit_signature: EntryExitState = field(default_factory=EntryExitState)


# ─── LayerIR (role-based writing) ────────────────────────────────────────────


@dataclass
class LayerEvent:
    """A single note event in a layer, with its musical role."""

    bar: int = 1
    beat: float = 1.0
    pitch: str = "C4"  # "C5" | "rest" | ["E4","G4","C5"]
    duration: str = "q"
    role: str = NoteRole.STRUCTURAL.value

    dynamic: Optional[str] = None
    articulation: Optional[str] = None
    ornament: Optional[str] = None
    tie: Optional[str] = None
    slur: Optional[str] = None
    hairpin: Optional[str] = None  # "cresc_start" | "dim_start" | "stop"
    expression: Optional[str] = None
    source_layer: Optional[str] = None

    # Playing technique that is neither an articulation nor an ornament:
    # "arpeggio" / "arpeggio_up" / "arpeggio_down" (a rolled chord — ubiquitous
    # in real piano writing and previously inexpressible), "tremolo",
    # "gliss_start" / "gliss_stop", "8va" / "8vb" / "octave_stop".
    technique: Optional[str] = None
    # Sustain pedal as a NOTATED mark: "down" | "up" | "change".
    pedal: Optional[str] = None
    # Fingering digit(s) for piano — engraved above/below the note.
    fingering: Optional[str] = None


@dataclass
class LayerIR:
    """Role-based musical layers. Replaces SATB as the native writing format."""

    phrase_id: str = ""
    instrumentation: str = "solo_piano"

    # Piano layers (always present for piano)
    principal_line: List[LayerEvent] = field(default_factory=list)
    bass_foundation: List[LayerEvent] = field(default_factory=list)
    response_layer: List[LayerEvent] = field(default_factory=list)
    counter_reply: List[LayerEvent] = field(default_factory=list)
    ornamental_surface: List[LayerEvent] = field(default_factory=list)

    # Orchestra layers (present when instrumentation != solo_piano)
    foreground: Optional[List[LayerEvent]] = None
    countermelody: Optional[List[LayerEvent]] = None
    harmonic_mass: Optional[List[LayerEvent]] = None
    rhythmic_motor: Optional[List[LayerEvent]] = None
    color_layer: Optional[List[LayerEvent]] = None
    punctuation: Optional[List[LayerEvent]] = None

    # Additional independent voices beyond the two a hand's main layers carry,
    # keyed "treble3", "treble4", "bass3"... Three- and four-voice writing was
    # simply unavailable in the shorthand: '//' gave two voices per hand and a
    # fugue or a chorale needs more, so real counterpoint required hand-written
    # LayerIR JSON and therefore never happened.
    inner_voices: Dict[str, List[LayerEvent]] = field(default_factory=dict)

    # Metadata
    key: str = "C"
    meter: Tuple[int, int] = (4, 4)
    bar_count: int = 4
    # Beats in an opening ANACRUSIS (pickup). 0 = the phrase starts on the
    # downbeat. Without this every phrase in every piece had to begin on beat 1
    # of a full bar, which rules out a large share of the classical repertoire's
    # melodies before a note is written.
    pickup_beats: float = 0.0


# ─── EventIR (final merged stream) ──────────────────────────────────────────


@dataclass
class EventIR:
    """Final symbolic event for engraving. Retains provenance."""

    staff: str = "treble"
    bar: int = 1
    beat: float = 1.0
    pitch: str = "C4"
    duration: str = "q"
    voice: int = 1
    role: str = NoteRole.STRUCTURAL.value
    source_layer: str = ""

    dynamic: Optional[str] = None
    articulation: Optional[str] = None
    ornament: Optional[str] = None
    tie: Optional[str] = None
    slur: Optional[str] = None
    hairpin: Optional[str] = None  # "cresc_start" | "dim_start" | "stop"
    expression: Optional[str] = None

    # Mirrors of the LayerEvent notation fields — see LayerEvent. These have to
    # be carried through to EventIR or the mark is silently lost at engraving.
    technique: Optional[str] = None
    pedal: Optional[str] = None
    fingering: Optional[str] = None


# ─── PerformanceIR ───────────────────────────────────────────────────────────


@dataclass
class TimingOffset:
    bar: int = 1
    beat: float = 1.0
    offset_ms: float = 0.0
    # Which line this offset applies to. Keyed by (bar, beat) alone, this model
    # could not express "the melody is struck 12ms ahead of the bass on this
    # beat" — which is what melodic lead IS, and the most documented cue in
    # human performance. Two offsets at one instant collided on the same key and
    # whichever was recorded first won, so melody and bass moved together:
    # silently the opposite of the intent.
    #
    # None means "every voice at this instant", which is what a breath or an
    # agogic stretch means and keeps every existing offset working unchanged.
    voice: Optional[str] = None


@dataclass
class RubatoWindow:
    bar_start: int = 1
    bar_end: int = 4
    curve: List[float] = field(default_factory=list)


@dataclass
class DynamicPoint:
    bar: int = 1
    beat: float = 1.0
    velocity: int = 80  # 0-127


@dataclass
class PedalEvent:
    bar: int = 1
    beat: float = 1.0
    type: str = "sustain"  # sustain | sostenuto | una_corda
    action: str = "down"  # down | up | half


@dataclass
class VoicingEmphasis:
    bar: int = 1
    beat: float = 1.0
    voice: str = "melody"
    boost: float = 0.1  # velocity boost ratio


@dataclass
class PerformanceIR:
    """Separate interpretation layer. Applied AFTER EventIR is finalized."""

    phrase_id: str = ""
    microtiming: List[TimingOffset] = field(default_factory=list)
    rubato_windows: List[RubatoWindow] = field(default_factory=list)
    dynamic_curve: List[DynamicPoint] = field(default_factory=list)
    pedal_events: List[PedalEvent] = field(default_factory=list)
    voicing_emphasis: List[VoicingEmphasis] = field(default_factory=list)


# ─── Candidate Scoring ──────────────────────────────────────────────────────


@dataclass
class CandidateScores:
    """Multi-dimensional scoring for a single candidate."""

    style_fidelity: float = 0.0
    sketch_fidelity: float = 0.0
    expectation_score: float = 0.0
    novelty_score: float = 0.0
    continuity_score: float = 0.0
    lock_compliance: float = 0.0

    # v6: context-awareness dimensions
    context_fidelity: float = (
        0.0  # did this candidate use context? (corpus patterns, gestures, etc.)
    )
    anti_pattern_risk: float = 0.0  # 0 = clean, higher = more AI tells detected

    # Hard constraint pass (meter, range, playability)
    hard_pass: bool = True

    _MODE_WEIGHTS = {
        CompositionMode.COMPOSE_FROM_TEXT.value: {
            "style": 0.20,
            "sketch": 0.18,
            "expect": 0.12,
            "novel": 0.12,
            "contin": 0.12,
            "lock": 0.08,
            "context": 0.10,
            "anti": 0.08,
        },
        CompositionMode.VARIATION.value: {
            "style": 0.12,
            "sketch": 0.12,
            "expect": 0.12,
            "novel": 0.08,
            "contin": 0.12,
            "lock": 0.26,
            "context": 0.10,
            "anti": 0.08,
        },
        CompositionMode.STYLE_TRANSFER.value: {
            "style": 0.25,
            "sketch": 0.12,
            "expect": 0.08,
            "novel": 0.08,
            "contin": 0.12,
            "lock": 0.17,
            "context": 0.10,
            "anti": 0.08,
        },
        CompositionMode.REDUCE_TO_PIANO.value: {
            "style": 0.08,
            "sketch": 0.08,
            "expect": 0.08,
            "novel": 0.04,
            "contin": 0.12,
            "lock": 0.44,
            "context": 0.08,
            "anti": 0.08,
        },
        CompositionMode.ORCHESTRATE.value: {
            "style": 0.17,
            "sketch": 0.12,
            "expect": 0.12,
            "novel": 0.08,
            "contin": 0.12,
            "lock": 0.21,
            "context": 0.10,
            "anti": 0.08,
        },
        CompositionMode.CONTINUE_PIECE.value: {
            "style": 0.17,
            "sketch": 0.17,
            "expect": 0.17,
            "novel": 0.08,
            "contin": 0.17,
            "lock": 0.08,
            "context": 0.08,
            "anti": 0.08,
        },
    }

    def total(self, mode: str) -> float:
        if not self.hard_pass:
            return 0.0
        w = self._MODE_WEIGHTS.get(
            mode, self._MODE_WEIGHTS[CompositionMode.COMPOSE_FROM_TEXT.value]
        )
        return (
            w["style"] * self.style_fidelity
            + w["sketch"] * self.sketch_fidelity
            + w["expect"] * self.expectation_score
            + w["novel"] * self.novelty_score
            + w["contin"] * self.continuity_score
            + w["lock"] * self.lock_compliance
            + w.get("context", 0) * self.context_fidelity
            + w.get("anti", 0) * (1.0 - self.anti_pattern_risk)
        )


@dataclass
class CandidateNode:
    """One candidate in the beam search."""

    phrase_id: str = ""
    sketch_idx: int = 0
    realization_idx: int = 0
    sketch: Optional[SketchIR] = None
    surface: Optional[LayerIR] = None
    reduced: Optional[SketchIR] = None
    scores: CandidateScores = field(default_factory=CandidateScores)


@dataclass
class SectionPath:
    """Optimal path through a section's phrase candidates."""

    section_id: str = ""
    nodes: List[CandidateNode] = field(default_factory=list)
    total_score: float = 0.0
    transition_scores: List[float] = field(default_factory=list)


# ─── Revision ────────────────────────────────────────────────────────────────


@dataclass
class RevisionOp:
    """A single revision operation."""

    target_phrase: str = ""
    target_layer: Optional[str] = None
    target_bars: Optional[Tuple[int, int]] = None
    operation: str = ""  # re_sketch | re_realize | transpose_region | change_texture | etc.
    params: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class RevisionScript:
    """What Claude writes instead of notes to fix problems."""

    section_id: str = ""
    ops: List[RevisionOp] = field(default_factory=list)
    priority: str = "important"  # critical | important | minor
    max_iterations: int = 3


# ─── Phrase State ────────────────────────────────────────────────────────────


@dataclass
class ReviewResult:
    """Result of reviewing a phrase."""

    passed: bool = False
    mechanical_issues: List[str] = field(default_factory=list)
    musical_issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    revision_script: Optional[RevisionScript] = None
    iteration: int = 0


@dataclass
class PhraseState:
    """Complete state for a single phrase through the pipeline."""

    slot: PhraseSlot = field(default_factory=PhraseSlot)
    control: Optional[Any] = None  # PhraseControlIR (forward ref to avoid circular)
    sketch: Optional[SketchIR] = None
    sketch_candidates: List[SketchIR] = field(default_factory=list)
    onset_bundles: Optional[List[Any]] = None  # List[OnsetBundle]
    candidates: List[CandidateNode] = field(default_factory=list)
    realized: Optional[LayerIR] = None
    review: Optional[ReviewResult] = None
    craft_check: Optional[Any] = None  # PhraseCraftCheck
    context_trace: Optional[Any] = None  # ContextTrace
    status: str = PhraseStatus.PLANNED.value
    salience: str = SalienceLevel.NORMAL.value
    agent_authored: bool = False  # True when final LayerIR was written by Claude, not the engine


# ─── Revision History ────────────────────────────────────────────────────────


@dataclass
class RevisionEntry:
    """An entry in the audit trail."""

    timestamp: str = ""
    skill: str = ""
    path: str = ""
    operation: str = ""
    reason: str = ""


# ─── Retrieval Types ─────────────────────────────────────────────────────────


@dataclass
class PhraseQuery:
    """Query for phrase-level retrieval from corpus."""

    formal_function: Optional[str] = None
    cadence_type: Optional[str] = None
    length_range: Tuple[int, int] = (2, 16)
    cadence_distance: Optional[int] = None
    harmony_path_class: Optional[str] = None
    key_mode: Optional[str] = None
    contour_class: Optional[str] = None
    density_curve: Optional[List[float]] = None
    density_tolerance: float = 0.3
    rh_texture_family: Optional[str] = None
    lh_texture_family: Optional[str] = None
    register_center_range: Optional[Tuple[int, int]] = None
    interaction_type: Optional[str] = None
    entry_texture: Optional[str] = None
    exit_texture: Optional[str] = None
    n: int = 10
    deduplicate_by_source: bool = True


@dataclass
class PhraseResult:
    """A retrieved phrase from corpus."""

    phrase_id: str = ""
    source: str = ""
    bar_range: Tuple[int, int] = (1, 4)
    length: int = 4
    role: str = ""
    cadence_type: str = ""
    key: str = ""
    key_mode: str = ""
    density_curve: List[float] = field(default_factory=list)
    register_curve: List[float] = field(default_factory=list)
    rh_textures: List[str] = field(default_factory=list)
    lh_textures: List[str] = field(default_factory=list)
    match_score: float = 0.0
    match_breakdown: Dict[str, float] = field(default_factory=dict)
    entry_state: Dict[str, Any] = field(default_factory=dict)
    exit_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransitionQuery:
    """Query for phrase-to-phrase transitions."""

    exit_density: int = 8
    exit_register_center: int = 72
    exit_texture_rh: str = ""
    exit_texture_lh: str = ""
    exit_dynamic: Optional[str] = None
    exit_cadence_type: Optional[str] = None
    target_function: Optional[str] = None
    target_key_mode: Optional[str] = None
    target_density_direction: Optional[str] = None
    texture_contrast_preference: float = 0.5
    n: int = 10


@dataclass
class TransitionResult:
    """A retrieved transition between phrases."""

    from_phrase_id: str = ""
    to_phrase_id: str = ""
    register_continuity: float = 0.0
    harmonic_plausibility: float = 0.0
    dynamic_continuity: float = 0.0
    texture_contrast: float = 0.0
    motivic_logic: float = 0.0
    composite_score: float = 0.0
    entry_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GestureQuery:
    """Query for idiomatic gesture retrieval."""

    function: Optional[str] = None
    target_role: Optional[str] = None
    texture_rh: Optional[str] = None
    texture_lh: Optional[str] = None
    density_range: Optional[Tuple[int, int]] = None
    register_range: Optional[Tuple[int, int]] = None
    contour: Optional[str] = None
    entry_state: Optional[str] = None
    exit_state: Optional[str] = None
    interaction_role: Optional[str] = None
    min_span_beats: Optional[float] = None
    max_span_beats: Optional[float] = None
    key_mode: Optional[str] = None
    n: int = 8


@dataclass
class GestureResult:
    """A retrieved gesture from corpus."""

    cell_id: str = ""
    function: str = ""
    span_beats: float = 4.0
    accent_profile: List[str] = field(default_factory=list)
    dur_profile: List[str] = field(default_factory=list)
    contour: str = ""
    interaction_role: str = ""
    harmony_binding: str = ""
    entry_state: str = ""
    exit_state: str = ""
    transform_ops: List[str] = field(default_factory=list)
    source: str = ""
    rh_texture: str = ""
    lh_texture: str = ""
    melody_density: int = 8
    match_score: float = 0.0


@dataclass
class CadenceQuery:
    """Query for cadential realization retrieval."""

    cadence_type: str = CadenceTarget.PAC.value
    key: str = "C"
    mode: str = "major"
    texture_family: Optional[str] = None
    dynamic_profile: Optional[str] = None
    soprano_arrival_degree: Optional[int] = None
    approach_length_bars: int = 2
    n: int = 5


@dataclass
class CadenceResult:
    """A retrieved cadential realization."""

    cadence_id: str = ""
    cadence_type: str = ""
    source: str = ""
    chord_sequence: List[str] = field(default_factory=list)
    soprano_arrival: str = ""
    bass_motion: str = ""
    texture_at_cadence: str = ""
    density_at_cadence: int = 8
    dynamic_at_cadence: str = ""
    approach_bars: Optional[List[Dict]] = None
    strength: int = 3
    match_score: float = 0.0


@dataclass
class PerformanceQuery:
    """Query for expressive performance patterns."""

    phrase_type: str = ""
    texture: Optional[str] = None
    dynamic_context: Optional[str] = None
    n: int = 5


@dataclass
class PerformanceResult:
    """A retrieved performance pattern."""

    pattern_id: str = ""
    phrase_type: str = ""
    tempo_modification: Optional[str] = None
    dynamic_curve: List[float] = field(default_factory=list)
    pedal_pattern: Optional[str] = None
    source: str = ""
    match_score: float = 0.0


# ═══════════════════════════════════════════════════════════════════════════
# v6 — Recursive, Context-Governed, Symphony-Capable Architecture
# ═══════════════════════════════════════════════════════════════════════════


# ─── WorkGraph (multi-movement top level) ──────────────────────────────────


@dataclass
class ThemeFamily:
    """A thematic family that can span movements."""

    family_id: str = ""
    character: str = ""
    primary_motif_ids: List[str] = field(default_factory=list)
    movements_present: List[str] = field(default_factory=list)
    transformation_arc: List[str] = field(default_factory=list)


@dataclass
class TonalItinerary:
    """Global key plan across the whole work."""

    home_key: str = "C"
    movement_keys: Dict[str, str] = field(default_factory=dict)
    key_relationships: List[str] = field(default_factory=list)
    progressive_tonality: bool = False


@dataclass
class ClimaxReservation:
    """A reserved climax point in the work."""

    movement_id: str = ""
    section_id: str = ""
    climax_type: str = ""
    energy_level: float = 1.0
    is_true_apex: bool = False
    reserved_devices: List[str] = field(default_factory=list)


@dataclass
class CrossMovementRecall:
    """A planned thematic recall across movements."""

    source_movement: str = ""
    source_theme: str = ""
    target_movement: str = ""
    target_section: str = ""
    transform: str = ""
    purpose: str = ""


@dataclass
class MovementContract:
    """What a movement IS within the larger work."""

    id: str = ""
    form: str = ""
    key: str = "C"
    tempo_bpm: int = 120
    meter: Tuple[int, int] = (4, 4)
    tempo_marking: str = ""
    character: str = ""
    role_in_work: str = ""
    sections: List[str] = field(default_factory=list)
    theme_families_active: List[str] = field(default_factory=list)
    orchestration_zones: List[Dict] = field(default_factory=list)
    contrast_with_previous: str = ""
    development_strategies: List[str] = field(default_factory=list)
    recap_logic: str = ""
    coda_logic: str = ""


@dataclass
class WorkGraph:
    """The top-level plan for a multi-movement work.

    Decides the symphony's dramatic and tonal destiny: whether the finale
    redeems, intensifies, or reframes the opening; which themes recur across
    movements; where the true apex sits; whether the slow movement is a
    refuge, wound, memory, or foreshadowing.
    """

    work_id: str = ""
    movement_count: int = 1
    movements: List[MovementContract] = field(default_factory=list)
    tonal_itinerary: TonalItinerary = field(default_factory=TonalItinerary)
    theme_families: Dict[str, ThemeFamily] = field(default_factory=dict)
    climax_reservations: List[ClimaxReservation] = field(default_factory=list)
    cross_movement_recalls: List[CrossMovementRecall] = field(default_factory=list)
    orchestral_macro_arc: List[Dict] = field(default_factory=list)
    emotional_narrative: str = ""
    cyclic_obligations: List[str] = field(default_factory=list)
    finale_payoff: str = ""


# ─── SectionContract (richer than SectionSpec) ─────────────────────────────


@dataclass
class SectionContract:
    """What a section IS — richer than SectionSpec.

    Adds thematic material, cadence path, energy envelope, texture family,
    orchestration, transition debts, and rhetorical goals.
    """

    id: str = ""
    movement_id: str = ""
    role: str = ""
    key: str = "C"
    bar_start: int = 1
    bar_end: int = 8
    phrase_ids: List[str] = field(default_factory=list)
    theme_families_active: List[str] = field(default_factory=list)
    cadence_path: List[str] = field(default_factory=list)
    energy_envelope: List[float] = field(default_factory=list)
    texture_family: str = ""
    orchestration_role_map: Dict[str, str] = field(default_factory=dict)
    transition_debt_in: str = ""
    transition_debt_out: str = ""
    rhetorical_goals: List[str] = field(default_factory=list)
    salience: str = SalienceLevel.NORMAL.value
    development_techniques: List[str] = field(default_factory=list)


# ─── PhraseControlIR (the rich bridge into note writing) ───────────────────


@dataclass
class HarmonicCell:
    """Beat-level or half-bar-level harmonic specification."""

    bar: int = 1
    beat: float = 1.0
    roman: str = "I"
    key: str = "C"
    function: str = HarmonicFunction.TONIC.value
    inversion: int = 0
    quality: str = "major"
    bass_degree: Optional[str] = None
    voice_leading_hint: Optional[str] = None


@dataclass
class MotifSlot:
    """Where and how a motif should appear in this phrase."""

    bar: int = 1
    beat: float = 1.0
    motif_id: str = ""
    transform: str = MotifTransformOp.STATE.value
    voice: str = "melody"
    params: Dict[str, Any] = field(default_factory=dict)
    is_recognition_moment: bool = False


@dataclass
class RhythmPlan:
    """Rhythmic blueprint for the phrase."""

    pulse_level: str = "quarter"
    subdivision_level: str = "eighth"
    rhythmic_topic: str = ""
    syncopation_budget: float = 0.0
    hemiola: bool = False
    accelerando_bars: Optional[Tuple[int, int]] = None
    ritardando_bars: Optional[Tuple[int, int]] = None


@dataclass
class TextureProgram:
    """Texture plan richer than List[BarTexturePlan]."""

    bars: List[BarTexturePlan] = field(default_factory=list)
    dominant_gesture_type: str = ""
    hand_relationship: str = ""
    texture_changes: List[int] = field(default_factory=list)
    density_arc: str = ""


@dataclass
class RegisterPlan:
    """Register usage for the phrase."""

    soprano_range: Tuple[int, int] = (60, 84)
    bass_range: Tuple[int, int] = (36, 60)
    register_trajectory: str = ""
    registral_climax_bar: Optional[int] = None


@dataclass
class ArticulationPlan:
    """Articulation intent for the phrase."""

    dominant_articulation: str = "legato"
    articulation_changes: List[Dict] = field(default_factory=list)


@dataclass
class BreathingPlan:
    """Breathing and silence plan for the phrase."""

    breath_points: List[Dict] = field(default_factory=list)
    rest_budget: float = 0.1
    longest_continuous_sound: int = 4


@dataclass
class OrnamentPolicyPhrase:
    """Ornament policy resolved for this specific phrase."""

    density_arc: str = "bare_adorned_bare"
    allowed_ornaments: List[str] = field(default_factory=list)
    forbidden_ornaments: List[str] = field(default_factory=list)
    ornament_positions: List[Dict] = field(default_factory=list)


@dataclass
class RetrievalQuery:
    """What to retrieve from corpus for this phrase."""

    phrase_query: Optional[PhraseQuery] = None
    gesture_queries: List[GestureQuery] = field(default_factory=list)
    cadence_query: Optional[CadenceQuery] = None
    pattern_textures: List[str] = field(default_factory=list)


@dataclass
class PhraseBoundaryState:
    """State at phrase entry or exit for cross-phrase continuity."""

    pitch: Optional[str] = None
    register_center: Optional[int] = None
    density: Optional[int] = None
    texture_rh: Optional[str] = None
    texture_lh: Optional[str] = None
    dynamic: Optional[str] = None
    last_chord: Optional[str] = None
    last_key: Optional[str] = None
    articulation: Optional[str] = None
    pending_resolution: Optional[str] = None
    motifs_stated: List[str] = field(default_factory=list)


@dataclass
class PhraseControlIR:
    """The main bridge between macro-plan and note writing.

    The smallest unit that still feels musically intentional. Richer than
    SketchIR — specifies harmonic cells at beat level, rhythm plan,
    register path, articulation, breathing, ornament policy.

    PhraseControlIR is what the Surface Composer receives.
    SketchIR is what Claude writes as a lighter-weight creative act.
    PhraseControlIR = SketchIR + resolved context + retrieval results.
    """

    phrase_id: str = ""
    section_id: str = ""
    phrase_function: str = PhraseFunction.PRESENTATION.value
    bars: int = 8
    bar_start: int = 1
    meter: Tuple[int, int] = (4, 4)
    tempo_bpm: int = 120
    local_key: str = "C"
    cadence_target: str = CadenceTarget.NONE.value
    cadence_bar: Optional[int] = None

    harmonic_cells: List[HarmonicCell] = field(default_factory=list)
    motif_slots: List[MotifSlot] = field(default_factory=list)

    melody_anchors: List[Anchor] = field(default_factory=list)
    bass_anchors: List[Anchor] = field(default_factory=list)
    dynamic_shape: List[DynamicEvent] = field(default_factory=list)
    expression_marks: List[ExpressionMark] = field(default_factory=list)
    cadence: CadenceApproach = field(default_factory=CadenceApproach)

    rhythm_plan: RhythmPlan = field(default_factory=RhythmPlan)
    texture_program: TextureProgram = field(default_factory=TextureProgram)
    register_plan: RegisterPlan = field(default_factory=RegisterPlan)
    articulation_plan: ArticulationPlan = field(default_factory=ArticulationPlan)
    breathing_plan: BreathingPlan = field(default_factory=BreathingPlan)
    ornament_policy: OrnamentPolicyPhrase = field(default_factory=OrnamentPolicyPhrase)

    entry_state: PhraseBoundaryState = field(default_factory=PhraseBoundaryState)
    exit_state: PhraseBoundaryState = field(default_factory=PhraseBoundaryState)

    retrieval_query: RetrievalQuery = field(default_factory=RetrievalQuery)
    salience: str = SalienceLevel.NORMAL.value
    performance_intent: Optional[Dict] = None

    # Context hooks — prove context shaped this phrase
    fingerprint_contract: List[str] = field(default_factory=list)
    anti_pattern_set: List[str] = field(default_factory=list)
    gesture_plan: List[str] = field(default_factory=list)
    phrase_prototype_id: Optional[str] = None
    donor_plan_id: Optional[str] = None


# ─── CrossScale Ledger Types ───────────────────────────────────────────────


@dataclass
class CrossScaleExpectation:
    """An expectation that exists at a specific compositional scale."""

    id: str = ""
    scale: str = WorkScale.PHRASE.value
    type: str = ExpectationType.PROMISE.value
    domain: str = ExpectationDomain.MOTIF_THEME.value
    object_ref: str = ""
    introduced_at: str = ""
    must_resolve_by: Optional[str] = None
    expected_form: Optional[str] = None
    urgency: float = 0.5
    status: str = ExpectationStatus.OPEN.value
    resolved_at: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThemeGenealogy:
    """Tracks the life of a theme across the work."""

    theme_id: str = ""
    original_statement: str = ""
    appearances: List[Dict] = field(default_factory=list)
    recognition_score: float = 1.0


@dataclass
class OrchestrationMemory:
    """Tracks orchestral color usage across the work."""

    color_episodes: List[Dict] = field(default_factory=list)
    instrument_rest_tracker: Dict[str, int] = field(default_factory=dict)


# ─── Onset Bundle and Note Justification ───────────────────────────────────


@dataclass
class OnsetJustification:
    """Why this note exists. Every note must have ≥1 structural + ≥1 local."""

    structural_reasons: List[str] = field(default_factory=list)
    local_reasons: List[str] = field(default_factory=list)
    context_trace: str = ""


@dataclass
class OnsetEvent:
    """A single note event in an onset bundle with full justification."""

    voice: str = ""
    pitch: str = "C4"
    duration: str = "q"
    role: str = NoteRole.STRUCTURAL.value
    justification: OnsetJustification = field(default_factory=OnsetJustification)
    dynamic: Optional[str] = None
    articulation: Optional[str] = None
    ornament: Optional[str] = None
    tie: Optional[str] = None
    expression: Optional[str] = None


@dataclass
class OnsetBundle:
    """A coordinated set of events at one time cursor.

    The Surface Composer writes onset bundles, not isolated lines.
    Every onset is decided with awareness of all simultaneous events.
    """

    bar: int = 1
    beat: float = 1.0
    events: List[OnsetEvent] = field(default_factory=list)
    harmonic_cell: Optional[HarmonicCell] = None
    active_motif: Optional[str] = None
    pedal_state: Optional[str] = None


@dataclass
class PhraseCraftCheck:
    """The phrase sanctity checklist. Every phrase must pass before acceptance."""

    melodic_claim_clear: bool = False
    rhythm_has_identity: bool = False
    bass_has_purpose: bool = False
    harmony_is_voiced: bool = False
    has_breath_point: bool = False
    accompaniment_responds_to_melody: bool = False
    entry_exit_earned: bool = False
    has_memorable_detail: bool = False
    all_notes_justified: bool = False

    @property
    def passed(self) -> bool:
        return all(
            [
                self.melodic_claim_clear,
                self.rhythm_has_identity,
                self.bass_has_purpose,
                self.harmony_is_voiced,
                self.has_breath_point,
                self.accompaniment_responds_to_melody,
                self.entry_exit_earned,
            ]
        )


# ─── Executable Context Objects (from compiler passes 8-12) ───────────────


@dataclass
class ExecutableGesture:
    """A note-level gesture template parsed from phrase-construction.md
    or composer composition-guide.md. Contains actual pitch/duration events.
    """

    id: str = ""
    name: str = ""
    situation: str = ""
    voice_events: Dict[str, List[Dict]] = field(default_factory=dict)
    harmonic_context: str = ""
    phrase_functions: List[str] = field(default_factory=list)
    composer_affinities: List[str] = field(default_factory=list)
    source_file: str = ""
    source_heading: str = ""


@dataclass
class AntiPatternRule:
    """An executable anti-pattern check."""

    id: str = ""
    name: str = ""
    description: str = ""
    detector: str = ""
    severity: str = "warning"
    params: Dict[str, Any] = field(default_factory=dict)
    style_scope: str = ""
    source_file: str = ""


@dataclass
class HarmonicDevice:
    """An executable harmonic device from harmonic-language.md."""

    id: str = ""
    name: str = ""
    chord_sequence: List[str] = field(default_factory=list)
    voice_leading_hints: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)
    frequency_weight: float = 0.3
    emotional_color: str = ""
    source_file: str = ""


@dataclass
class CadenceScript:
    """A cadential realization recipe."""

    id: str = ""
    type: str = ""
    approach_chords: List[str] = field(default_factory=list)
    soprano_line: List[str] = field(default_factory=list)
    bass_motion: str = ""
    inner_voice_rules: List[str] = field(default_factory=list)
    strength: int = 3
    typical_texture: str = ""
    preparation_bars: int = 2


@dataclass
class BreathingRule:
    """Silence/rest doctrine from dramatic-pacing-silence.md."""

    type: str = ""
    placement: str = ""
    duration_beats_min: float = 1.0
    duration_beats_max: float = 4.0
    effect: str = ""
    technique: str = ""
    source_file: str = ""


@dataclass
class OrnamentIntent:
    """Ornament intent rule from ornament-intent.md decision framework."""

    context: str = ""
    what_moment_needs: str = ""
    common_choice: str = ""
    why: str = ""
    density_arc: str = ""


@dataclass
class PerformanceIntentProfile:
    """Performance nuance directives."""

    rubato_contexts: List[str] = field(default_factory=list)
    pedal_rules: List[Dict[str, str]] = field(default_factory=list)
    voicing_priorities: List[str] = field(default_factory=list)


# ─── Executable Context Objects (from compiler passes 13-18) ──────────────


@dataclass
class PromptSemantic:
    """Maps an emotional/descriptive word to musical parameters.

    Compiled from emotional-vocabulary.md, character-theme-design.md,
    musical-semiotics.md, philosophy-to-music.md.
    """

    word: str = ""
    synonyms: List[str] = field(default_factory=list)
    tempo_range: Optional[Tuple[int, int]] = None
    mode_scale: List[str] = field(default_factory=list)
    dynamics: str = ""
    texture: str = ""
    register: str = ""
    articulation: str = ""
    rhythm_type: str = ""
    harmonic_language: str = ""
    interval_preferences: List[str] = field(default_factory=list)
    density_range: Optional[Tuple[float, float]] = None
    orchestration_color: str = ""
    contour: str = ""
    grounding: str = "interpretive"
    source_files: List[str] = field(default_factory=list)


@dataclass
class MelodyPrior:
    """Interval language, breath-span, hook placement, peak timing,
    motif continuation rule.

    Compiled from melodic-construction.md and melody-craft.md.
    """

    id: str = ""
    category: str = ""  # interval_language | breath_span | hook_placement | peak_timing | motif_continuation | contour | phrase_structure
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    grounding: str = "interpretive"
    source_file: str = ""


@dataclass
class FigurationTemplate:
    """Texture-family proposal template from figuration-patterns.md."""

    id: str = ""
    name: str = ""
    pattern_keyword: str = ""
    period_style: List[str] = field(default_factory=list)
    tempo_range: Optional[Tuple[int, int]] = None
    character: str = ""
    when_to_use: List[str] = field(default_factory=list)
    variation_operators: List[str] = field(default_factory=list)
    density_suggestion: Optional[Tuple[int, int]] = None
    register_suggestion: str = ""
    grounding: str = "interpretive"
    source_file: str = ""


@dataclass
class ModulationScript:
    """Executable modulation procedure from modulation-techniques.md."""

    id: str = ""
    type: str = ""  # pivot_chord | direct | chromatic | enharmonic | common_tone | sequential
    from_key_class: str = ""
    to_key_relationship: str = ""
    mechanism: str = ""
    smoothness: str = ""  # very_smooth | smooth | dramatic | expressive | mystical | natural
    best_for: List[str] = field(default_factory=list)
    chord_sequence: List[str] = field(default_factory=list)
    voice_leading_hints: List[str] = field(default_factory=list)
    pivot_chord_in_old: str = ""
    pivot_chord_in_new: str = ""
    grounding: str = "interpretive"
    source_file: str = ""


@dataclass
class CounterpointRule:
    """Contrapuntal rule family from counterpoint-essentials.md."""

    id: str = ""
    category: str = ""  # motion_balance | dissonance_handling | parallel_prohibition | voice_independence | voice_leading | voice_spacing
    description: str = ""
    severity: str = "warning"  # error | warning | suggestion
    style_permissions: Dict[str, bool] = field(default_factory=dict)
    repair_recipe: str = ""
    detection_heuristic: Dict[str, Any] = field(default_factory=dict)
    grounding: str = "hard_corroborated"
    source_file: str = ""


@dataclass
class HarmonicTemperature:
    """Tension curve and harmonic temperature mapping from harmonic-expression.md."""

    id: str = ""
    category: str = ""  # tension_curve | temperature_mapping | emotional_to_harmonic | prolongation | harmonic_rhythm | cadence_punctuation
    emotional_context: str = ""
    tonal_move: str = ""
    narrative_meaning: str = ""
    tension_level: Optional[float] = None
    harmonic_parameters: Dict[str, Any] = field(default_factory=dict)
    when_to_use: List[str] = field(default_factory=list)
    grounding: str = "interpretive"
    source_file: str = ""


@dataclass
class DonorPlan:
    """Donor strategy for sparse-corpus composers (Tier C/D)."""

    donors: List[Tuple[str, float]] = field(default_factory=list)
    max_donor_weight: float = 0.6
    fingerprint_filter: bool = True
    leakage_budget: float = 0.2


@dataclass
class FingerprintContract:
    """Required fingerprints for a piece — enforceable, not aspirational."""

    style_claim: str = ""
    period: str = ""
    required_fingerprints: List[str] = field(default_factory=list)
    minimum_audible_count: int = 3


@dataclass
class ContextTrace:
    """Provenance record for one phrase — what context shaped its notes."""

    phrase_id: str = ""
    corpus_patterns_used: List[str] = field(default_factory=list)
    corpus_bars_used: List[str] = field(default_factory=list)
    gestures_applied: List[str] = field(default_factory=list)
    devices_used: List[str] = field(default_factory=list)
    fingerprints_expressed: List[str] = field(default_factory=list)
    breathing_rules_applied: List[str] = field(default_factory=list)
    ornament_intents_applied: List[str] = field(default_factory=list)
    fallback_bar_count: int = 0
    donor_bar_count: int = 0
    total_bar_count: int = 0


@dataclass
class ContextUtilizationReport:
    """Per-piece/section proof that context was actually used."""

    total_bars: int = 0
    bars_from_corpus_patterns: int = 0
    bars_from_corpus_bars: int = 0
    bars_from_hardcoded_fallback: int = 0
    bars_from_donor: int = 0
    gestures_applied: int = 0
    breathing_rules_applied: int = 0
    ornament_intents_applied: int = 0
    harmonic_devices_used: int = 0
    fingerprints_satisfied: int = 0
    fingerprints_required: int = 0
    anti_patterns_detected: int = 0
    anti_patterns_checked: int = 0
    phrase_traces: Dict[str, ContextTrace] = field(default_factory=dict)

    @property
    def corpus_coverage(self) -> float:
        total = self.bars_from_corpus_patterns + self.bars_from_corpus_bars
        return total / max(self.total_bars, 1)

    @property
    def fallback_ratio(self) -> float:
        return self.bars_from_hardcoded_fallback / max(self.total_bars, 1)

    @property
    def fingerprint_coverage(self) -> float:
        return self.fingerprints_satisfied / max(self.fingerprints_required, 1)


@dataclass
class PhraseContext:
    """The resolved context for one phrase — what the realizer and scorer see.

    Produced by ContextRouter.resolve(). Contains only the context items
    active for this specific phrase given its function, position, harmonic
    state, and style claim.
    """

    active_gestures: List[ExecutableGesture] = field(default_factory=list)
    active_patterns: Dict[str, List[Any]] = field(default_factory=dict)
    breathing_plan: List[BreathingRule] = field(default_factory=list)
    ornament_intents: List[OrnamentIntent] = field(default_factory=list)
    available_devices: List[HarmonicDevice] = field(default_factory=list)
    cadence_scripts: List[CadenceScript] = field(default_factory=list)
    active_anti_patterns: List[AntiPatternRule] = field(default_factory=list)
    fingerprint_targets: List[FingerprintRule] = field(default_factory=list)
    is_donor_phrase: bool = False

    # Context assets from compiler passes 13-18
    active_melody_priors: List[MelodyPrior] = field(default_factory=list)
    active_figuration_templates: List[FigurationTemplate] = field(default_factory=list)
    active_modulation_scripts: List[ModulationScript] = field(default_factory=list)
    active_counterpoint_rules: List[CounterpointRule] = field(default_factory=list)
    active_harmonic_temperatures: List[HarmonicTemperature] = field(default_factory=list)
    prompt_parameters: Optional[Dict[str, Any]] = None


@dataclass
class StyleProgram:
    """The master executable style object. Wraps StyleDNA with all
    runtime-actionable data.

    StyleDNA remains the compiled statistical profile (distributions,
    transitions, densities). StyleProgram adds executable rules, patterns,
    and constraints that directly affect note-level decisions.
    """

    dna: StyleDNA = field(default_factory=StyleDNA)
    gesture_templates: List[ExecutableGesture] = field(default_factory=list)
    anti_patterns: List[AntiPatternRule] = field(default_factory=list)
    harmonic_devices: List[HarmonicDevice] = field(default_factory=list)
    cadence_scripts: List[CadenceScript] = field(default_factory=list)
    breathing_rules: List[BreathingRule] = field(default_factory=list)
    ornament_intents: List[OrnamentIntent] = field(default_factory=list)
    performance_intents: PerformanceIntentProfile = field(default_factory=PerformanceIntentProfile)
    review_rubric: List[Dict] = field(default_factory=list)
    donor_plan: Optional[DonorPlan] = None
    fingerprint_contract: Optional[FingerprintContract] = None

    # Context assets from compiler passes 13-18
    prompt_semantics: List[PromptSemantic] = field(default_factory=list)
    melody_priors: List[MelodyPrior] = field(default_factory=list)
    figuration_templates: List[FigurationTemplate] = field(default_factory=list)
    modulation_scripts: List[ModulationScript] = field(default_factory=list)
    counterpoint_rules: List[CounterpointRule] = field(default_factory=list)
    harmonic_temperatures: List[HarmonicTemperature] = field(default_factory=list)
