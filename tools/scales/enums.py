"""
All enumerations for the SCALES system.
"""

from enum import Enum

# ─── Composition Mode ────────────────────────────────────────────────────────


class CompositionMode(str, Enum):
    COMPOSE_FROM_TEXT = "compose_from_text"
    VARIATION = "variation"
    STYLE_TRANSFER = "style_transfer"
    REDUCE_TO_PIANO = "reduce_to_piano"
    ORCHESTRATE = "orchestrate"
    CONTINUE_PIECE = "continue_piece"


# ─── Note Role (every note carries one) ─────────────────────────────────────


class NoteRole(str, Enum):
    STRUCTURAL = "structural"
    PASSING = "passing"
    NEIGHBOR = "neighbor"
    APPOGGIATURA = "appoggiatura"
    SUSPENSION = "suspension"
    ANTICIPATION = "anticipation"
    ARPEGGIATED_FILL = "arpeggiated_fill"
    PEDAL_SUPPORT = "pedal_support"
    PUNCTUATION = "punctuation"
    CUE = "cue"
    ORNAMENTAL = "ornamental"


# ─── Phrase Function ─────────────────────────────────────────────────────────


class PhraseFunction(str, Enum):
    PRESENTATION = "presentation"
    CONTINUATION = "continuation"
    CADENTIAL = "cadential"
    CLOSING = "closing"
    SEQUENCE = "sequence"
    FRAGMENTATION = "fragmentation"
    LIQUIDATION = "liquidation"
    RETRANSITION = "retransition"
    RETURN = "return"
    RETURN_VARIED = "return_varied"
    TRANSITION = "transition"
    INTRODUCTION = "introduction"
    CODETTA = "codetta"
    CODA = "coda"
    CONTRASTING_THEME = "contrasting_theme"
    EPISODE = "episode"


# ─── Texture Types (RH) ─────────────────────────────────────────────────────


class TextureType(str, Enum):
    SINGING_MELODY = "singing_melody"
    SCALAR_RUN = "scalar_run"
    ZIGZAG_FIGURATION = "zigzag_figuration"
    CHORDAL = "chordal"
    PASSAGE_WORK = "passage_work"
    DOTTED_PAIRS = "dotted_pairs"
    DIALOGUE = "dialogue"
    STAMMER_REPEAT = "stammer_repeat"
    ORNAMENTAL_CASCADE = "ornamental_cascade"
    SILENCE = "silence"


# ─── Accompaniment Types (LH) ───────────────────────────────────────────────


class AccompType(str, Enum):
    ALBERTI = "alberti"
    BASS_MELODY = "bass_melody"
    BLOCK_CHORD_SPARSE = "block_chord_sparse"
    BROKEN_CHORD_DESC = "broken_chord_desc"
    BROKEN_CHORD_WAVE = "broken_chord_wave"
    WALKING_BASS = "walking_bass"
    BLOCK_CHORD_OFFBEAT = "block_chord_offbeat"
    PEDAL_POINT = "pedal_point"
    SPARSE_PUNCTUATION = "sparse_punctuation"
    BLOCK_CHORD_TREMOLO = "block_chord_tremolo"
    BROKEN_CHORD_ASC = "broken_chord_asc"
    SILENCE = "silence"
    INTERLOCKING = "interlocking"


# ─── Cadence Targets ─────────────────────────────────────────────────────────


class CadenceTarget(str, Enum):
    PAC = "PAC"
    IAC = "IAC"
    HC = "HC"
    DC = "DC"
    PLAGAL = "plagal"
    EVADED = "evaded"
    ELIDED = "elided"
    NONE = "none"


# ─── Gesture Types (unified both-hands) ─────────────────────────────────────


class GestureType(str, Enum):
    CHORD_THEN_FIGURATION = "chord_then_figuration"
    HELD_MELODY_OVER_BASS = "held_melody_over_bass"
    SINGING_OVER_ALBERTI = "singing_over_alberti"
    ARPEGGIO_AS_MELODY = "arpeggio_as_melody"
    GRACE_CLUSTER_LAUNCH = "grace_cluster_launch"
    SCALAR_OVER_SPARSE = "scalar_over_sparse"
    PARALLEL_HANDS = "parallel_hands"
    STAMMER_REPEAT = "stammer_repeat"
    SEQUENCE_STEP = "sequence_step"
    CHORDAL_DIALOGUE = "chordal_dialogue"
    ALBERTI_SIXTEENTHS = "alberti_sixteenths"
    BROKEN_CHORD_WAVE = "broken_chord_wave"
    BASS_MELODY_CONTRAPUNTAL = "bass_melody_contrapuntal"
    WALKING_BASS = "walking_bass"
    BLOCK_CHORD_PUNCTUATION = "block_chord_punctuation"
    SILENCE_BOTH = "silence_both"
    SILENCE_LH_ONLY = "silence_lh_only"
    SPARSE_HELD = "sparse_held"
    TREMOLO_BUILD = "tremolo_build"
    PEDAL_OVER_MELODY = "pedal_over_melody"


# ─── Hand Relationship ───────────────────────────────────────────────────────


class HandRelationship(str, Enum):
    MELODY_OVER_PATTERN = "melody_over_pattern"
    PATTERN_OVER_BASS = "pattern_over_bass"
    PARALLEL = "parallel"
    DIALOGUE = "dialogue"
    HOMOPHONIC = "homophonic"
    SOLO_RH = "solo_rh"
    SOLO_LH = "solo_lh"
    INTERLOCKING = "interlocking"


# ─── Gesture Function ────────────────────────────────────────────────────────


class GestureFunction(str, Enum):
    PICKUP = "pickup"
    ANSWER = "answer"
    ANSWER_WITH_SPACE = "answer_with_space"
    INSIST = "insist"
    SEQUENCE_STEP = "sequence_step"
    ARRIVAL = "arrival"
    CADENTIAL_PUSH = "cadential_push"
    CADENTIAL_RELEASE = "cadential_release"
    SUSTAIN = "sustain"
    ECHO = "echo"
    BREATHE = "breathe"
    SILENCE = "silence"
    LEAN_IN = "lean_in"


# ─── Expectation Types ───────────────────────────────────────────────────────


class ExpectationType(str, Enum):
    PROMISE = "promise"
    DEBT = "debt"
    COOLDOWN = "cooldown"
    PROHIBITION = "prohibition"
    IDENTITY_LOCK = "identity_lock"


class ExpectationStatus(str, Enum):
    OPEN = "open"
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    EXPIRED = "expired"


# ─── Motif Transforms ────────────────────────────────────────────────────────


class MotifTransformOp(str, Enum):
    STATE = "state"
    SEQUENCE = "sequence"
    FRAGMENT = "fragment"
    INVERT = "invert"
    AUGMENT = "augment"
    DIMINISH = "diminish"
    LIQUIDATE = "liquidate"
    RETROGRADE = "retrograde"
    REHARMONIZE = "reharmonize"


# ─── Support Tiers ───────────────────────────────────────────────────────────


class SupportTier(str, Enum):
    TIER_A = "A"
    TIER_B = "B"
    TIER_C = "C"
    TIER_D = "D"


# ─── Reduction Modes ─────────────────────────────────────────────────────────


class ReductionMode(str, Enum):
    STUDY = "study_reduction"
    PLAYABLE = "playable_reduction"
    CONCERT = "concert_transcription"


# ─── Phrase Status ────────────────────────────────────────────────────────────


class PhraseStatus(str, Enum):
    PLANNED = "planned"
    SKETCHED = "sketched"
    REALIZED = "realized"
    REVIEWED = "reviewed"
    APPROVED = "approved"


# ─── Pipeline Phase ──────────────────────────────────────────────────────────


class PipelinePhase(str, Enum):
    INIT = "init"
    PLANNING = "planning"
    SKETCHING = "sketching"
    REALIZING = "realizing"
    REVIEWING = "reviewing"
    ASSEMBLING = "assembling"
    COMPLETE = "complete"


# ─── Harmonic Function ───────────────────────────────────────────────────────


class HarmonicFunction(str, Enum):
    TONIC = "tonic"
    PREDOMINANT = "predominant"
    DOMINANT = "dominant"
    CHROMATIC = "chromatic"
    APPLIED = "applied"
    NEAPOLITAN = "neapolitan"
    AUGMENTED_SIXTH = "augmented_sixth"


# ─── Orchestral Roles ────────────────────────────────────────────────────────


class OrchestraRole(str, Enum):
    PRINCIPAL_MELODY = "principal_melody"
    SECONDARY_MELODY = "secondary_melody"
    BASS_FOUNDATION = "bass_foundation"
    HARMONIC_PAD = "harmonic_pad"
    RHYTHMIC_MOTOR = "rhythmic_motor"
    COLOR_PUNCTUATION = "color_punctuation"
    CUE_NOTES = "cue_notes"
    CLIMACTIC_HIT = "climactic_hit"


# ─── Composition Scale (recursive hierarchy) ───────────────────────────────


class WorkScale(str, Enum):
    WORK = "work"
    MOVEMENT = "movement"
    SECTION = "section"
    PHRASE = "phrase"
    GESTURE = "gesture"
    ONSET = "onset"


# ─── Salience Level (compute budget allocation) ────────────────────────────


class SalienceLevel(str, Enum):
    CRITICAL = "critical"  # main themes, climaxes, exposed solos, finale payoffs
    HIGH = "high"  # cadential turns, transitions into major arrivals
    NORMAL = "normal"  # standard phrases
    LOW = "low"  # connective tissue (still must pass phrase checklist)


# ─── Note Justification (every note must have ≥1 structural + ≥1 local) ───


class NoteJustification(str, Enum):
    # Structural reasons
    MOTIF = "motif"
    HARMONY = "harmony"
    CADENCE = "cadence"
    FORM = "form"
    ORCHESTRATION_ROLE = "orchestration_role"
    LEDGER_OBLIGATION = "ledger_obligation"
    # Local reasons
    VOICE_LEADING = "voice_leading"
    RHYTHMIC_COUNTERPOINT = "rhythmic_counterpoint"
    EXPRESSIVE_ACCENT = "expressive_accent"
    ARTICULATION = "articulation"
    ORNAMENT_INTENT = "ornament_intent"
    REGISTER_SHAPING = "register_shaping"
    COLOR = "color"


# ─── Expectation Domain (for CrossScale Ledger) ────────────────────────────


class ExpectationDomain(str, Enum):
    MOTIF_THEME = "motif_theme"
    HARMONY_TONAL = "harmony_tonal"
    CADENCE = "cadence"
    ORCHESTRATION = "orchestration"
    RHYTHM = "rhythm"
    ENERGY_CLIMAX = "energy_climax"
    FORM = "form"
    RECALL = "recall"
