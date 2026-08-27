"""
SCALES — Top-level orchestrator.

Sketch-Conditioned Alternating Ledger-guided Expansion Search.

This module provides the Python tool surface that Claude's skills call.
All functions operate on the PieceGraph as the single source of truth.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import fields
from dataclasses import fields as _dataclass_fields
from datetime import datetime, timezone
from fractions import Fraction as _F
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .anti_pattern_detector import run_all_detectors
from .cadence_bank import CadenceBank
from .candidate_scorer import CandidateScorer
from .context_compiler import ContextCompiler
from .context_router import ContextRouter
from .context_utilization import compute_utilization
from .craft_checker import CraftChecker
from .cross_scale_ledger import CrossScaleLedger
from .donor_strategy import DonorStrategy
from .duration import bar_duration
from .enums import (
    AccompType,
    CadenceTarget,
    ExpectationDomain,
    ExpectationType,
    PhraseFunction,
    PipelinePhase,
    TextureType,
)
from .expectation_ledger import ExpectationLedger
from .gesture_bank import GestureBank
from .harmonic_solver import HarmonicSolver
from .models import (
    BarTexturePlan,
    CandidateNode,
    ContextTrace,
    FormGraph,
    HarmonicCell,
    LayerIR,
    MotifObject,
    MotifSlot,
    MovementContract,
    MovementSpec,
    NarrativeArc,
    NarrativeSection,
    PhraseControlIR,
    PhraseCurves,
    PhraseSlot,
    SectionContract,
    SectionSpec,
    SketchIR,
    StyleDNA,
    WorkGraph,
)

# v6 imports
from .pattern_retriever import PatternRetriever
from .phrase_bank import PhraseBank
from .piece_graph import PieceGraph, load_layer_ir_from_dict
from .realizer import Realizer
from .reducer import Reducer
from .section_search import SectionSearch
from .sketch_proposer import SketchProposer
from .style_resolver import StyleResolver
from .surface_composer import SurfaceComposer

_WORKSPACE = Path("workspace")
_LOG = logging.getLogger(__name__)


# Every revision operation the patch engine implements. An op the engine does
# not recognise is logged and skipped, so a typo in a critic's revision script
# came back as a successful revision that changed nothing.
_REVISION_OPS = frozenset(
    {
        "re_sketch",
        "re_realize",
        "transpose_region",
        "change_texture",
        "change_dynamic",
        "set_articulation",
        "set_hairpin",
        "set_expression",
        "thin_texture",
    }
)


#: The parameter key each operation actually READS. Every handler uses
#: `op.params.get(<key>)` and does nothing when it is absent, so an op carrying
#: the wrong name is a silent no-op that still counts as applied.
_REVISION_OP_PARAMS = {
    "transpose_region": ("interval",),
    "change_texture": ("lh_texture",),
    "change_dynamic": ("dynamic",),
    "set_articulation": ("articulation",),
    "set_hairpin": ("kind",),
    "set_expression": ("text",),
    # re_sketch, re_realize and thin_texture take no parameters.
}


def _piece_instrumentation(graph) -> str:
    """What the piece is scored for, from its contract.

    Every LayerIR was constructed claiming `solo_piano`, so every check that
    asks "is this a keyboard?" answered yes for a motet — the hand-span limit
    among them, which is meaningless for two singers.
    """
    contract = getattr(graph, "contract", None)
    target = getattr(contract, "target", None) if contract is not None else None
    if isinstance(target, dict):
        return str(target.get("instrumentation") or "solo_piano")
    return str(getattr(target, "instrumentation", "") or "solo_piano")


class _MissingPiece(Exception):
    """A tool was asked about a piece that does not exist.

    Carries the structured result the tool should return. Raised rather than
    returned so `_load_graph` can be a one-line call at the top of a tool
    without every caller needing a two-value unpack.
    """

    def __init__(self, piece_id: str):
        self.result = {
            "error": f"No workspace for '{piece_id}'",
            "hint": (
                f"Nothing at workspace/{piece_id}/piece_graph.json. Check the piece id "
                f"(get_status() lists what exists), or create it with "
                f"init_workspace('{piece_id}', mode=..., description=...)."
            ),
        }
        super().__init__(self.result["error"])


def _load_graph(piece_id: str) -> "PieceGraph":
    """The piece's graph, or a structured error explaining that it isn't there.

    Every tool here is called by an agent writing a Python snippet, so what a
    failure LOOKS like is part of the interface. Ten tools raised a bare
    FileNotFoundError — a traceback with a path in it and no indication that the
    piece id was the problem — and eight others silently succeeded on a piece
    that does not exist, which is worse: `load_workspace` returned a plausible
    dict for nothing, and `save_reference_study` returned `{"saved": True}`
    after writing state for a piece nobody had created.
    """
    path = _WORKSPACE / piece_id / "piece_graph.json"
    if not path.exists():
        raise _MissingPiece(piece_id)
    return PieceGraph.load(str(path))


class _ToolRefusal(Exception):
    """A tool was asked to do something that cannot mean what it says.

    Same mechanism as `_MissingPiece` — raised so a guard stays one line at the
    top of a tool — but the message is the guard's rather than a fixed one.
    """

    def __init__(self, result: Dict):
        self.result = result


def _require_source_loaded(graph, piece_id: str, tool: str) -> None:
    """A mode that transforms an existing score needs that score.

    Every mode in `_MODE_LOCKS` — variation, style_transfer, continue_piece,
    orchestrate, reduce_to_piano — is defined by what it PRESERVES from a
    source. `load_source_score` is what reads that source in and what applies
    the lock policy; the orchestrator skill says so plainly ("Without it the
    mode has no material: the path alone is not the music").

    Nothing enforced it. Planning a `variation` with no source loaded returned
    ten phrase slots, `contract.source` empty and `contract.locks` **entirely
    unset** — so the piece composed an original work, called it a variation,
    and the lock policy that is the mode's whole definition never applied. The
    same held for style_transfer, reduce_to_piano and continue_piece. Passing
    `source_path` to `init_workspace` does not help: it records a path, and a
    path is not a score.
    """
    mode = str(getattr(graph, "mode", "") or "")
    if mode not in _MODE_LOCKS:
        return
    phrases = getattr(graph, "phrases", None) or {}
    if any(getattr(p, "salience", "") == "source" for p in phrases.values()):
        return
    path = getattr(getattr(graph.contract, "source", None), "path", "")
    raise _ToolRefusal(
        {
            "error": (
                f"'{piece_id}': mode is '{mode}', which transforms an existing "
                f"score, but no source has been loaded — so there is nothing to "
                f"{'vary' if mode == 'variation' else 'transform'}."
            ),
            "hint": (
                f"Call load_source_score('{piece_id}') before {tool}(). It reads "
                f"the score in as phrases marked salience='source' AND applies "
                f"the mode's lock policy ({', '.join(sorted(_MODE_LOCKS[mode]))}), "
                f"which is what makes this mode different from compose_from_text."
            ),
            "source_path_recorded": path or None,
            "next": f"load_source_score('{piece_id}'"
            + (f", path='{path}')" if path else ", path='<score.musicxml>')"),
        }
    )


def _tool(fn):
    """Turn a missing piece into the tool's normal error result."""
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (_MissingPiece, _ToolRefusal) as exc:
            return exc.result

    return wrapper


def _as_list(value, what: str):
    """Normalise a tool argument that must be a list, or say why it cannot be.

    Every function in this module is called by an agent writing a Python
    snippet, so the arguments arrive hand-typed. A bare string is a sequence of
    **characters**, and Python will iterate it happily: `compile_style(...,
    composers="mozart")` compiled six one-letter "composers" (a, m, o, r, t, z —
    the letters of the name), left `tools/compiled_packs/m/` on disk, and then
    resolved the whole piece's style against "m": tier D, zero fingerprints,
    zero cadences, zero left-hand textures. The piece still generated. It simply
    had no style, and nothing anywhere said so.

    So: coerce the two unambiguous single-item cases (a lone string, a lone
    dict) and refuse anything else loudly, because a silent misread here costs
    a whole piece.
    """
    if value is None:
        return []
    if isinstance(value, (str, bytes)):
        return [value]
    if isinstance(value, dict):
        return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    raise TypeError(
        f"{what} must be a list (or a single item), got {type(value).__name__}: {value!r}"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# Reading the forces out of a request. Three word classes, because two was not
# enough — see `_infer_instrumentation`.

#: Words that name SINGERS. These are people, and they always win.
#:
#: Matched on WORD BOUNDARIES, not as substrings. "chorale" contains "choral",
#: so a substring test turned "a chorale prelude for organ" — a solo organ work
#: — into a choir. Single voice-part names (soprano, alto, tenor, bass) are
#: deliberately absent: "double bass", "bass line" and "soprano recorder" are
#: all instruments, and "SATB"/"for four voices" already cover the real cases.
_VOCAL_FORCES = (
    "voice",
    "voices",
    "choir",
    "choirs",
    "chorus",
    "choral",
    "satb",
    "singers",
    "cappella",
    "acappella",
)
#: Words that name repertoire which is USUALLY vocal but has a keyboard
#: literature — an organ mass, a chorale prelude, a keyboard transcription.
#: These mean singers only when no instrument is named.
_VOCAL_GENRES = (
    "motet",
    "madrigal",
    "mass",
    "masses",
    "chorale",
    "chorales",
    "anthem",
    "cantata",
    "requiem",
    "magnificat",
    "psalm",
)
_ENSEMBLE_WORDS = (
    "quartet",
    "quintet",
    "trio",
    "orchestra",
    "orchestral",
    "symphony",
    "symphonic",
    "concerto",
    "ensemble",
    "octet",
    "sextet",
    "band",
    "consort",
)
_KEYBOARD_WORDS = (
    "keyboard",
    "piano",
    "harpsichord",
    "organ",
    "clavichord",
    "fortepiano",
    "pianoforte",
    "clavier",
)
#: Singers named by VOICE TYPE. "A sacred piece for soprano, alto, tenor and
#: bass" named four people and resolved to `solo_piano`, because the singer
#: words this module knew were "voice"/"voices"/"choir" and none of them appear
#: in it — so four singers got a grand staff and the pianist's hand-span limit,
#: which is the motet failure described below wearing different words.
#:
#: The names are shared with instruments, so a bare word list cannot be used:
#: "bass clarinet", "alto saxophone", "tenor trombone" and "double bass" all
#: name a voice type and none of them is a person. Hence the two guard sets and
#: the position-aware scan in `_singer_voice_types`.
_VOICE_TYPE_FAMILY = {
    "soprano": "soprano",
    "sopranos": "soprano",
    "soprani": "soprano",
    "superius": "soprano",
    "cantus": "soprano",
    "treble": "soprano",
    "trebles": "soprano",
    "descant": "soprano",
    "mezzo": "mezzo",
    "alto": "alto",
    "altos": "alto",
    "alti": "alto",
    "altus": "alto",
    "contralto": "alto",
    "tenor": "tenor",
    "tenors": "tenor",
    "tenori": "tenor",
    "tenore": "tenor",
    "countertenor": "countertenor",
    "baritone": "baritone",
    "baritones": "baritone",
    "bass": "bass",
    "basses": "bass",
    "basso": "bass",
    "bassi": "bass",
    "bassus": "bass",
}
_VOICE_TYPES = frozenset(_VOICE_TYPE_FAMILY)
#: A voice type FOLLOWED by one of these is an instrument or a position in the
#: texture, not a singer — "bass clarinet", "alto flute", "tenor line".
_INSTRUMENT_AFTER_VOICE_TYPE = frozenset(
    {
        "clarinet",
        "clarinets",
        "saxophone",
        "saxophones",
        "sax",
        "saxes",
        "trombone",
        "trombones",
        "flute",
        "flutes",
        "recorder",
        "recorders",
        "oboe",
        "oboes",
        "horn",
        "horns",
        "tuba",
        "tubas",
        "trumpet",
        "trumpets",
        "cornet",
        "cornets",
        "bassoon",
        "bassoons",
        "viol",
        "viols",
        "viola",
        "violin",
        "guitar",
        "guitars",
        "drum",
        "drums",
        "lute",
        "gamba",
        "shawm",
        "sackbut",
        "crumhorn",
        "harp",
        "marimba",
        "xylophone",
        "banjo",
        "mandolin",
        "pipe",
        "pipes",
        "string",
        "strings",
        "continuo",
        "line",
        "lines",
        "clef",
        "register",
        "staff",
        "stave",
        "entry",
        "entries",
    }
)
#: A voice type PRECEDED by one of these is an instrument or a figured-bass
#: idiom — "double bass", "figured bass", "walking bass".
_INSTRUMENT_BEFORE_VOICE_TYPE = frozenset(
    {
        "double",
        "contra",
        "contrabass",
        "string",
        "figured",
        "ground",
        "walking",
        "thorough",
        "thoroughbass",
        "electric",
        "upright",
        "acoustic",
    }
)
#: Repertoire for ONE singer. Lets a single named voice type beside a keyboard
#: read as a song rather than as a keyboard piece whose tenor register is being
#: described ("a chorale prelude for organ with the cantus in the tenor").
#: Voice types that ALSO name a register or a line in keyboard writing — "the
#: cantus in the tenor", "the bass of the fugue". Beside a named keyboard these
#: are not evidence of a singer. The rest ("soprano", "contralto", "baritone",
#: "mezzo", "countertenor") name people and nothing else.
_REGISTER_AMBIGUOUS_TYPES = frozenset(
    {
        "alto",
        "altos",
        "alti",
        "altus",
        "tenor",
        "tenors",
        "tenori",
        "tenore",
        "bass",
        "basses",
        "basso",
        "bassi",
        "bassus",
        "treble",
        "trebles",
        "cantus",
        "superius",
        "descant",
    }
)
_SOLO_SONG_GENRES = frozenset(
    {
        "song",
        "songs",
        "lied",
        "lieder",
        "aria",
        "arias",
        "arietta",
    }
)

#: "two-voice", "four-part" — a COUNT OF CONTRAPUNTAL LINES, not a count of
#: people. It is the standard way to describe keyboard counterpoint.
_TEXTURE_COUNT = re.compile(
    r"\b(?:two|three|four|five|six|2|3|4|5|6)[\s\-]?(?:voice|voices|part|parts)\b"
)


def _words_of(text: str) -> frozenset:
    return frozenset(re.findall(r"[a-z]+", text))


def _names_any(text: str, words) -> bool:
    present = _words_of(text)
    return any(w in present for w in words)


def _singer_voice_types(text: str) -> set:
    """The voice-type WORDS in `text` that name PEOPLE, not instruments.

    Position-aware on purpose: the word alone cannot tell a singer from a
    "bass clarinet". Words are returned rather than families because the caller
    needs both how many distinct voices were named (via `_VOICE_TYPE_FAMILY`,
    so "sopranos" and "soprano" count once) and whether any of them was one of
    the unambiguous ones.
    """
    tokens = re.findall(r"[a-z]+", text)
    found = set()
    for i, tok in enumerate(tokens):
        if tok not in _VOICE_TYPES:
            continue
        after = tokens[i + 1] if i + 1 < len(tokens) else ""
        before = tokens[i - 1] if i else ""
        if after in _INSTRUMENT_AFTER_VOICE_TYPE:
            continue
        if before in _INSTRUMENT_BEFORE_VOICE_TYPE:
            continue
        found.add(tok)
    return found


#: Modes whose TARGET forces are fixed by the mode itself, whatever the request
#: says. Both of these name their source in the description — see the note in
#: `init_workspace`.
_MODE_TARGET_INSTRUMENTATION = {
    "reduce_to_piano": "solo_piano",
    "orchestrate": "ensemble",
}


def _infer_instrumentation(description: str) -> Optional[str]:
    """Read the forces out of the request.

    Nothing did. "A short sacred motet for FOUR VOICES in the Dorian mode" was
    recorded as `solo_piano`, and the pianist's hand-span limit was applied to
    Tenor and Bassus as one hand — the motet failed its commit with "lh span 19
    semitones exceeds max 16", true of a hand and meaningless for two singers.

    The first fix then over-corrected in the other direction, and that error was
    worse. "A two-voice invention in D minor FOR KEYBOARD" came back `choir`,
    because "N-voice" is the standard way to describe keyboard counterpoint and
    the named instrument in the same sentence was never consulted. The piece
    routed down the ensemble path and exported with the **left hand as a
    cello** — two instruments instead of a grand staff, no brace, LH on its own
    MIDI channel — and that path is the documented cause of the voice-overlap
    bar overflow that desyncs the hands.

    So three classes rather than two:

      * a word naming SINGERS always wins ("a cantata for choir and orchestra"
        is choral, not orchestral);
      * a word naming vocal REPERTOIRE means singers only when no instrument is
        named, so "a chorale prelude for organ" and "an organ mass" stay
        keyboard works while a bare "a mass" is still choral;
      * "N-voice"/"N-part" is discounted as a texture only when an instrument
        is actually named, so an unqualified "for four voices" still means four
        people.

    A fourth class, added after "a sacred piece for soprano, alto, tenor and
    bass" came back `solo_piano`: singers named by VOICE TYPE. Those names are
    shared with instruments, so they are read in context — a type followed by
    an instrument ("bass clarinet") or preceded by a qualifier ("double bass")
    is not a person. A type that survives that scan means singers when two
    distinct types appear, when no instrument is named at all, or when the
    request names solo-song repertoire; a LONE type beside a named keyboard is
    left undecided, because "a chorale prelude for organ with the cantus in the
    tenor" is describing a register, not hiring a singer.

    Vocal is tested before ensemble and keyboard is not a shortcut, or "a piano
    trio" resolves to a keyboard piece.
    """
    d = (description or "").lower()
    names_keyboard = _names_any(d, _KEYBOARD_WORDS)
    scanned = _TEXTURE_COUNT.sub(" ", d) if names_keyboard else d
    if _names_any(scanned, _VOCAL_FORCES):
        return "choir"
    voiced = _singer_voice_types(scanned)
    families = {_VOICE_TYPE_FAMILY[t] for t in voiced}
    if voiced and (
        # a word that names a person and nothing else
        any(t not in _REGISTER_AMBIGUOUS_TYPES for t in voiced)
        or _names_any(scanned, _SOLO_SONG_GENRES)
        # register words mean singers when no instrument is competing for them
        or (not names_keyboard and (len(families) > 1 or not _names_any(scanned, _ENSEMBLE_WORDS)))
    ):
        return "choir"
    if _names_any(scanned, _ENSEMBLE_WORDS):
        return "ensemble"
    if not names_keyboard and _names_any(scanned, _VOCAL_GENRES):
        return "choir"
    return None


def _physical_constraints(graph):
    """Constraints for THIS piece — hand limits only where there are hands."""
    from .models import PhysicalConstraints

    inst = ""
    try:
        inst = (getattr(graph.contract.target, "instrumentation", "") or "").lower()
    except Exception:
        inst = ""
    # A whitelist of spellings, and the graphs on disk carry four: "solo_piano"
    # (54 pieces), "piano" (2), "piano_solo" (2) and "solo piano" (1). The last
    # two missed, so `keyboard` came out False for a solo piano work and the
    # validator skipped hand span and notes-per-hand entirely — a STRICT
    # physical constraint switched off by a space. `is_keyboard` normalizes
    # spacing and hyphens and is the one decider.
    from .models import is_keyboard

    return PhysicalConstraints(keyboard=is_keyboard(inst))


# ─── Workspace Management ────────────────────────────────────────────────────


@_tool
def init_workspace(
    piece_id: str, mode: str, description: str = "", params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a new workspace and initialize PieceGraph.

    Returns summary dict for Claude.
    """
    workspace = _WORKSPACE / piece_id
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "cache").mkdir(exist_ok=True)
    (workspace / "output").mkdir(exist_ok=True)
    (workspace / "logs").mkdir(exist_ok=True)

    graph = PieceGraph.create(piece_id, mode, description)

    if params:
        if "source_path" in params:
            from .models import SourceReference

            graph.contract.source = SourceReference(path=params["source_path"])
        if "instrumentation" in params:
            graph.contract.target.instrumentation = params["instrumentation"]
        if "difficulty" in params:
            graph.contract.target.difficulty = params["difficulty"]

    # Read the forces out of the request when the caller did not name them.
    #
    # THE MODE WINS where it names the target. `reduce_to_piano` and
    # `orchestrate` describe a transformation, so their descriptions name the
    # SOURCE — "reduce this symphony to piano", "orchestrate this piano piece" —
    # and inferring from the words set the target to exactly the wrong thing in
    # both: the reduction was recorded as an ensemble and the orchestration as
    # solo piano.
    #
    # That inversion matters most where it is least visible: the piano
    # playability check (hand span) runs only for keyboard targets, so a
    # reduction — whose entire purpose is to fit two hands — was the one output
    # never checked for it, while an orchestration was checked against a span
    # no orchestra has.
    if not (params or {}).get("instrumentation"):
        forced = _MODE_TARGET_INSTRUMENTATION.get(mode)
        inferred = forced or _infer_instrumentation(description)
        if inferred:
            graph.contract.target.instrumentation = inferred

    graph.phase = PipelinePhase.INIT.value
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "piece_id": piece_id,
        "workspace": str(workspace),
        "piece_graph_path": str(workspace / "piece_graph.json"),
        "mode": mode,
    }


@_tool
def load_workspace(piece_id: str) -> Dict[str, Any]:
    """Load existing workspace and return status summary."""
    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"

    if not graph_path.exists():
        return {"error": f"Workspace not found: {piece_id}"}

    graph = PieceGraph.load(str(graph_path))
    return graph.get_status_summary()


@_tool
def get_status(piece_id: str) -> Dict[str, Any]:
    """Quick status check."""
    return load_workspace(piece_id)


@_tool
def list_sections(piece_id: str) -> Dict[str, Any]:
    """Ordered sections with a compact per-phrase summary — the deterministic
    work-list for the compose pipeline (used by the wolfgang-compose workflow
    and the orchestrator). Each phrase carries status + agent_authored so a
    resume skips already-composed phrases. Phrases are listed in their
    committed order (composition within a section is sequential)."""
    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"
    if not graph_path.exists():
        return {"error": f"Workspace not found: {piece_id}"}
    graph = PieceGraph.load(str(graph_path))
    sections = []
    for sid in graph.form.sections:  # insertion order = movement→section build order
        phrases = []
        for pid in graph.get_section_phrases(sid):
            st = graph.phrases.get(pid)
            phrases.append(
                {
                    "phrase_id": pid,
                    "status": getattr(st, "status", "missing") if st else "missing",
                    "agent_authored": bool(getattr(st, "agent_authored", False)) if st else False,
                }
            )
        sections.append({"section_id": sid, "phrases": phrases})
    return {
        "piece_id": piece_id,
        "sections": sections,
        "section_count": len(sections),
        "phrase_count": sum(len(s["phrases"]) for s in sections),
    }


# ─── Planning Tools ──────────────────────────────────────────────────────────


@_tool
def compile_style(
    piece_id: str,
    composers: List[str],
    blend_weights: Optional[Dict[str, float]] = None,
    era: str = "",
    genre: str = "",
) -> Dict[str, Any]:
    """Compile StyleDNA and StyleProgram for the piece.

    Runs the context compiler (passes 1-12) and style resolver.
    For Tier C/D composers, applies donor strategy.
    """
    # A bare string is a sequence of CHARACTERS. Passing composers="mozart" — the
    # obvious call, and the one a reader of the signature makes — compiled seven
    # bogus one-letter "composers" and then resolved the whole piece's style
    # against "m": tier D, zero fingerprints, zero cadences, zero LH textures.
    # The piece still generated; it just had no style at all, and nothing said so.
    if isinstance(composers, str):
        composers = [composers]
    composers = [c for c in (composers or []) if c]
    if not composers:
        raise ValueError("compile_style needs at least one composer or style name")

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    # Compile packs for each composer (all 12 passes).
    #
    # NOT for a style. A style pack is an AGGREGATE, built by
    # `scripts/build_style_profiles.py` from its members; the compiler builds a
    # pack from `.claude/context/<genre>/composer-profiles/<name>/`, and a style
    # has no such directory. Running it on one therefore writes EMPTY passes over
    # the aggregate: compiling "classical" left `style__classical` with zero
    # instruments, zero textures and zero worked prototypes, and the damage is to
    # the shared pack — every later piece in that style inherits it. Observed by
    # doing exactly this and having `test_style_packs_carry_doctrine` catch it.
    from .style_registry import is_style_id, normalize_style

    compiler = ContextCompiler()
    skipped_styles: List[str] = []
    for composer in composers:
        if is_style_id(composer) or normalize_style(composer):
            skipped_styles.append(composer)
            continue
        compiler.compile(composer, genre)

    # Resolve style
    resolver = StyleResolver()
    if blend_weights and len(composers) > 1:
        program = resolver.resolve_blend_program(blend_weights, era)
    else:
        program = resolver.resolve_program(composers[0], era)

    # Handle donor strategy for sparse-corpus composers
    if program.dna.tier in ("C", "D"):
        ds = DonorStrategy()
        donor_plan = ds.resolve_donors(composers[0], program.dna.tier, genre)
        if donor_plan.donors:
            program = ds.augment_program(program, donor_plan)

    graph.style_dna = program.dna  # backward compat
    graph.style_program = program  # v6
    graph.save(str(workspace / "piece_graph.json"))

    result = {
        "composer_id": program.dna.composer_id,
        "tier": program.dna.tier,
        "fingerprints": len(program.dna.fingerprints.items),
        "lh_textures": len(program.dna.lh_distribution),
        "cadences": len(program.dna.cadence_vocabulary),
        "gesture_templates": len(program.gesture_templates),
        "anti_patterns": len(program.anti_patterns),
        "harmonic_devices": len(program.harmonic_devices),
        "breathing_rules": len(program.breathing_rules),
        "ornament_intents": len(program.ornament_intents),
        "donor_plan": bool(program.donor_plan and program.donor_plan.donors),
        "axis_ownership": program.dna.axis_ownership,
    }
    # Say it out loud when the style compiled to nothing. A tier-D profile with
    # no fingerprints and no cadence vocabulary means every brief downstream will
    # be generic, and that is worth a warning rather than a silent pass.
    if not result["fingerprints"] and not result["cadences"]:
        result["warning"] = (
            f"style '{composers[0]}' compiled with no fingerprints and no cadence "
            f"vocabulary (tier {result['tier']}) — briefs will be generic. Check "
            f"the composer name, or arm it with scripts/acquire_composer.py."
        )
    return result


def _movement_of_phrase(graph, phrase_id: str, slot) -> str:
    """Which movement a slot belongs to — the field if set, else `m<N>_`."""
    mv = str(getattr(slot, "movement_id", "") or "")
    if mv:
        return mv
    sid = str(getattr(slot, "section_id", "") or phrase_id or "")
    m = re.match(r"^(m\d+)_", sid)
    return m.group(1) if m else "m1"


def _movement_ordinal(movement_id: str) -> int:
    m = re.match(r"^m(\d+)$", str(movement_id or ""))
    return int(m.group(1)) if m else 1


def _bars_before_movement(graph, movement_id: str) -> Tuple[int, Dict[str, int]]:
    """(last bar of the movements BEFORE this one, {later movement: its first bar}).

    Ordered by movement number rather than by "everything else already in the
    graph", so REBUILDING a middle movement puts it back where it was instead of
    appending it after the finale. The two rules agree while movements are built
    in order and disagree exactly when one is revised, which is when it matters.

    A rebuild that changes a movement's LENGTH leaves the movements after it in
    the wrong place, and nothing downstream can tell — so they are named here
    and the caller reports them. Silently overlapping bars is how three
    movements ended up stacked on one another in the first place.
    """
    mid = str(movement_id or "m1")
    ordinal = _movement_ordinal(mid)
    before = 0
    after: Dict[str, int] = {}
    for pid, ps in getattr(graph, "phrases", {}).items():
        slot = getattr(ps, "slot", None)
        if slot is None:
            continue
        other = _movement_of_phrase(graph, pid, slot)
        if other == mid:
            continue
        end = int(slot.bar_start or 1) + int(slot.bar_count or 0) - 1
        start = int(slot.bar_start or 1)
        if _movement_ordinal(other) < ordinal:
            before = max(before, end)
        else:
            after[other] = min(after.get(other, start), start)
    return before, after


@_tool
def build_form_graph(
    piece_id: str,
    form: str,
    key: str,
    tempo_bpm: int = 120,
    meter: Tuple[int, int] = (4, 4),
    sections: Optional[List[Dict]] = None,
    motif_ids: Optional[List[str]] = None,
    movement_id: str = "m1",
) -> List[Dict]:
    """Build a form graph with PhraseSlots.

    Returns list of PhraseSlot summaries for Claude to review.

    ``sections`` and ``motif_ids`` are NOT IMPLEMENTED. They were accepted,
    normalised by `_as_list`, and then never read — so a caller handing over a
    custom section layout got the canned form for `form` and no indication that
    their layout had been discarded. Nothing in the repo passes either, and the
    documented call in `/w-plan` omits both, but the signature advertised them
    and a silent no-op on a public tool is worse than an unimplemented one.
    Supplying either now logs a warning; the shape a real implementation should
    take is `_build_from_spec`, which already materialises a section spec.
    """
    sections = _as_list(sections, "sections")
    motif_ids = _as_list(motif_ids, "motif_ids")
    for name, given in (("sections", sections), ("motif_ids", motif_ids)):
        if given:
            _LOG.warning(
                "build_form_graph(%s=...) is not implemented and was ignored — the "
                "form was built from form=%r alone. Nothing was silently applied.",
                name,
                form,
            )
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    # Planning is the first step that commits to a form, and for a mode whose
    # form is supposed to COME FROM the source, planning without one is where
    # the mode quietly turns into compose_from_text.
    _require_source_loaded(graph, piece_id, "build_form_graph")

    # Build sections and phrases based on form
    # Build ON the existing form graph when this is an additional movement.
    # A fresh FormGraph() replaced the registry every call, so `form.sections`
    # held only the LAST movement built — `get_section_phrases` returned []
    # for every earlier one, which silently blocked the engine fallback, the
    # section gate and the review path for all but one movement of a work.
    form_graph = graph.form if (movement_id != "m1" and graph.form) else FormGraph()
    phrase_summaries = []
    form_substituted = ""

    # This movement begins after every bar already spoken for by ANOTHER
    # movement — its own earlier phrases are excluded so rebuilding a movement
    # replaces it in place instead of pushing it further down the score each
    # time. Bars are the assembler's layout coordinate and must be unique
    # across the whole work; see `_build_from_spec`.
    bar_offset, later_movements = _bars_before_movement(graph, movement_id)
    prior_phrase_ids = {
        pid
        for pid, ps in graph.phrases.items()
        if getattr(ps, "slot", None) is not None
        and _movement_of_phrase(graph, pid, ps.slot) == movement_id
    }
    if bar_offset:
        _LOG.info("%s: movement %r starts at bar %d", piece_id, movement_id, bar_offset + 1)

    if form == "ternary":
        phrases = _build_ternary(key, tempo_bpm, meter, graph.style_dna, movement_id, bar_offset)
    elif form == "sonata":
        phrases = _build_sonata(key, tempo_bpm, meter, graph.style_dna, movement_id, bar_offset)
    elif form == "theme_variations":
        phrases = _build_theme_variations(
            key, tempo_bpm, meter, graph.style_dna, movement_id, bar_offset
        )
    elif form in ("binary", "rounded_binary"):
        phrases = _build_binary(
            key,
            tempo_bpm,
            meter,
            graph.style_dna,
            movement_id,
            rounded=form == "rounded_binary",
            bar_offset=bar_offset,
        )
    else:
        # SAY SO. `_build_simple` is a reasonable default for a form this system
        # has no spec for, but it was silent: asking for a `rondo` returned a
        # four-phrase A-B-A' with no refrain returns, a `minuet_trio` came back
        # with no trio, and a `fugue` and a `binary` were the same song form
        # under a different name. Nothing in the result said the form asked for
        # was not the form built.
        phrases = _build_simple(
            key, tempo_bpm, meter, form, graph.style_dna, movement_id, bar_offset
        )
        form_substituted = form

    # Create movement
    movement = MovementSpec(
        id=movement_id,
        form=form,
        key=key,
        tempo_bpm=tempo_bpm,
        meter=meter,
        sections=[],
    )

    # Group phrases into sections and add to graph
    current_section_id = ""
    for slot in phrases:
        # Wire the planned emotional arc into per-bar slot curves (keystone:
        # drives dynamics, density targets, register, and the tempo arc).
        _apply_narrative_curves(slot, graph.narrative)
        if slot.section_id != current_section_id:
            current_section_id = slot.section_id
            section = SectionSpec(
                id=current_section_id,
                movement_id=movement_id,
                key=slot.key,
                phrase_ids=[],
            )
            form_graph.sections[current_section_id] = section
            movement.sections.append(current_section_id)

        form_graph.sections[current_section_id].phrase_ids.append(slot.phrase_id)
        graph.add_phrase(slot.phrase_id, slot)

        phrase_summaries.append(
            {
                "phrase_id": slot.phrase_id,
                "section": slot.section_id,
                "bars": f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}",
                "function": slot.function,
                "cadence": slot.cadence_target,
                "key": slot.key,
            }
        )

    # REPLACE a movement of the same id rather than appending a second copy.
    # Rebuilding a movement appended a duplicate MovementSpec, so `form.movements`
    # grew each replan and every consumer that iterates it — the assembler's
    # movement headings among them — saw the movement twice.
    _existing = [
        i for i, m in enumerate(form_graph.movements) if getattr(m, "id", "") == movement_id
    ]
    if _existing:
        form_graph.movements[_existing[0]] = movement
        for _dup in reversed(_existing[1:]):
            del form_graph.movements[_dup]
    else:
        form_graph.movements.append(movement)
    graph.form = form_graph

    # The dramatic plan: what each phrase is FOR. Without this, planning produced
    # a form skeleton with an energy ramp and nothing else — no climax, no tension
    # arc, no register plan, no strategy for how a return differs from the
    # statement, and no phrase knowing what it leads into.
    from . import dramatic_plan

    plan_info = dramatic_plan.build([graph.phrases[p.phrase_id].slot for p in phrases])
    graph.narrative = _narrative_from_slots(
        [graph.phrases[p.phrase_id].slot for p in phrases], plan_info
    )

    # Build SectionContracts from the form graph sections
    for sec_id, sec_spec in form_graph.sections.items():
        # Determine section role from phrase functions
        section_phrases = [
            graph.phrases[pid].slot for pid in sec_spec.phrase_ids if pid in graph.phrases
        ]
        cadence_path = [s.cadence_target for s in section_phrases]
        energy_envelope = []
        for s in section_phrases:
            energy_envelope.extend(s.curves.energy if s.curves.energy else [0.5] * s.bar_count)

        from .dramatic_plan import section_rhetoric

        _roles = [getattr(sl, "dramatic_role", "") for sl in section_phrases]
        _goals, _techs = section_rhetoric([r for r in _roles if r])
        graph.section_contracts[sec_id] = SectionContract(
            id=sec_id,
            movement_id=sec_spec.movement_id or "m1",
            role=sec_spec.role or _infer_section_role(sec_id),
            key=sec_spec.key,
            bar_start=section_phrases[0].bar_start if section_phrases else 1,
            bar_end=(section_phrases[-1].bar_start + section_phrases[-1].bar_count - 1)
            if section_phrases
            else 8,
            phrase_ids=sec_spec.phrase_ids,
            cadence_path=cadence_path,
            energy_envelope=energy_envelope,
            rhetorical_goals=_goals,
            development_techniques=_techs,
            texture_family=(
                section_phrases[0].texture_plan[0].lh_texture
                if section_phrases and section_phrases[0].texture_plan
                else ""
            ),
        )
        for _sl in section_phrases:
            _sl.section_techniques = list(_techs)
            _sl.section_goals = list(_goals)

    # ─── Populate expectations from form structure ─────────────────────
    #
    # This block wrote nothing, for any piece, for the entire life of the
    # project. Not because it raised — the `except Exception: pass` that used to
    # wrap it never fired — but because every write was guarded by
    # `if _cross_ledger is not None` / `elif _ledger is not None`, and a fresh
    # PieceGraph has `cross_scale_ledger = None` and no `expectation_ledger`
    # attribute at all. Both guards were False every time, so the loop ran to
    # completion and recorded nothing, and the swallow-everything handler hid
    # the cause. `ensure_ledger` creates or restores one, so there is now
    # something to populate.
    from .cross_scale_ledger import ensure_ledger, persist_ledger

    _cross_ledger = ensure_ledger(graph)
    _ledger = None

    for sec_id, sec_contract in graph.section_contracts.items():
        role = sec_contract.role

        # Development sections promise theme recapitulation
        if role == "development":
            if _cross_ledger is not None:
                _cross_ledger.add_movement_expectation(
                    exp_type=ExpectationType.PROMISE.value,
                    domain=ExpectationDomain.MOTIF_THEME.value,
                    object_ref=f"theme_recap_after_{sec_id}",
                    introduced_at=sec_id,
                    expected_form="theme recapitulation",
                    urgency=0.7,
                    details={"source_section": sec_id, "role": role},
                )
            elif _ledger is not None:
                _ledger.add_promise(
                    object_ref=f"theme_recap_after_{sec_id}",
                    introduced_at=sec_id,
                    expected_form="theme recapitulation",
                    urgency=0.7,
                    details={"source_section": sec_id, "role": role},
                )

        # Sections with cadence paths create a debt for cadence resolution
        if sec_contract.cadence_path:
            if _cross_ledger is not None:
                _cross_ledger.add_section_expectation(
                    exp_type=ExpectationType.DEBT.value,
                    domain=ExpectationDomain.CADENCE.value,
                    object_ref=f"cadence_resolution_{sec_id}",
                    introduced_at=sec_id,
                    must_resolve_by=sec_contract.phrase_ids[-1]
                    if sec_contract.phrase_ids
                    else None,
                    urgency=0.6,
                    details={
                        "cadence_path": [str(c) for c in sec_contract.cadence_path],
                        "section": sec_id,
                    },
                )
            elif _ledger is not None:
                _ledger.add_debt(
                    object_ref=f"cadence_resolution_{sec_id}",
                    opened_at=sec_id,
                    must_resolve_by=sec_contract.phrase_ids[-1]
                    if sec_contract.phrase_ids
                    else None,
                    urgency=0.6,
                    details={
                        "cadence_path": [str(c) for c in sec_contract.cadence_path],
                        "section": sec_id,
                    },
                )
    # Serialize before saving: `PieceGraph.cross_scale_ledger` is typed as the
    # SERIALIZED form, so leaving the live object on it breaks `save` and every
    # promise recorded here would be gone before composition ever read it.
    persist_ledger(graph, _cross_ledger)

    graph.phase = PipelinePhase.PLANNING.value
    # Decide the piece's METRIC ENTRY at the composer's own rate. A piece that
    # always begins squarely on beat 1 of bar 1 sounds squared-off, and none of
    # the twelve pieces in workspace/ has ever begun any other way — while 46% of
    # Mozart's movements and 69% of Bach's open with a pickup. The shorthand and
    # the engraver have both supported an anacrusis all along; nothing asked.
    _plan_metric_entry(graph)

    # Elect ONE principal theme and state it at every section opening
    # (transformed at the recap) — a memorable, recurring through-line instead of
    # locally-optimized, independent phrases. Runs AFTER the slots exist, and is
    # idempotent, so `resolve_motifs` can do the same work if it comes second.
    themed = _place_principal_theme(graph)

    graph.save(str(workspace / "piece_graph.json"))

    if form_substituted:
        _LOG.warning(
            "form %r has no spec in this system; built the default song form "
            "(A-B-A', %d phrases) instead. Known forms: %s.",
            form_substituted,
            len(phrase_summaries),
            ", ".join(_KNOWN_FORMS),
        )
        phrase_summaries.append(
            {
                "warning": "form_substituted",
                "requested": form_substituted,
                "built": "simple song form (A-B-A')",
                "known_forms": list(_KNOWN_FORMS),
                "note": (
                    "A rondo built this way has no refrain returns and a "
                    "minuet_trio has no trio. Use a known form, or lay the "
                    "sections out explicitly with the `sections` argument."
                ),
            }
        )
    # NO THEME IS A SILENT OUTCOME, and it is the one that matters most.
    #
    # `_place_principal_theme` needs `graph.motif_bank`, which only
    # `resolve_motifs` fills. Called without it — which is what happens if the
    # planning order in `/w-plan` is not followed, or a caller goes straight to
    # the form — it plants nothing and returns 0, and every phrase is then
    # composed with no recurring idea. Measured on a piece built that way: 19
    # phrases, 19 different openings, where real movements reuse one in about a
    # third. Nothing anywhere said so.
    if not themed:
        reason = (
            "no motifs are defined for this piece"
            if not graph.motif_bank
            else "no section opening was free to carry it"
        )
        phrase_summaries.append(
            {
                "warning": "no_principal_theme_planted",
                "movement": movement_id,
                "why": reason,
                "note": (
                    "every phrase will be composed with no recurring idea, and a "
                    "piece with nothing to recognise has nothing to develop or "
                    "resolve. Call resolve_motifs BEFORE build_form_graph (the "
                    "order in /w-plan), then rebuild the form."
                ),
            }
        )

    # A REBUILD leaves the old layout's debris behind, and nothing downstream
    # can tell the difference between a phrase this form asked for and one the
    # previous form did. Rebuilding a ternary movement as a sonata keeps the
    # ternary's `_retr` and `_coda` phrases — realized, in scope, and assembled
    # into the score alongside the sonata. They are named rather than deleted:
    # some of them may hold composed music, and dropping that uninvited is not
    # this function's call to make.
    built_ids = {p.phrase_id for p in phrases}
    orphans = sorted(prior_phrase_ids - built_ids)
    if orphans:
        phrase_summaries.append(
            {
                "warning": "stale_phrases_from_previous_layout",
                "movement": movement_id,
                "phrase_ids": orphans,
                "note": (
                    "these phrases belong to this movement's PREVIOUS form and are "
                    "still in the graph — they will be assembled into the score. "
                    "Remove them if the rebuild was intentional."
                ),
            }
        )

    # A rebuild that changed this movement's LENGTH moves its last bar into the
    # movement after it. The bars would silently overlap, which is the same
    # failure as the one `bar_offset` exists to prevent, arriving from the other
    # direction.
    if later_movements and phrases:
        movement_end = max(p.bar_start + p.bar_count - 1 for p in phrases)
        clash = sorted(mv for mv, start in later_movements.items() if start <= movement_end)
        if clash:
            phrase_summaries.append(
                {
                    "warning": "later_movements_now_overlap",
                    "movement": movement_id,
                    "ends_at_bar": movement_end,
                    "overlapping": clash,
                    "note": (
                        "this movement changed length and now runs into the "
                        "movement(s) after it — rebuild them so their bars follow."
                    ),
                }
            )

    return phrase_summaries


def _narrative_from_slots(slots, plan_info) -> "NarrativeArc":
    """Build a NarrativeArc from the planned slots' dramatic roles.

    ``narrative.sections`` was empty after planning and ``primary_climax_section``
    was blank, so every downstream consumer of the narrative (the brief's CREATIVE
    INTENT, the per-bar curve interpolation, the critic's arc judgement) had
    nothing to read.
    """
    from .dramatic_plan import ROLE_INTENT

    arc = NarrativeArc()
    by_section: Dict[str, List] = {}
    for slot in slots:
        by_section.setdefault(slot.section_id, []).append(slot)
    climax_phrase = plan_info.get("climax_phrase")
    for section_id, group in by_section.items():
        roles = [getattr(s, "dramatic_role", "") for s in group]
        is_climax = any(s.phrase_id == climax_phrase for s in group)
        arc.sections.append(
            NarrativeSection(
                id=section_id,
                label=section_id,
                bar_start=group[0].bar_start,
                bar_end=group[-1].bar_start + group[-1].bar_count - 1,
                energy_curve=[v for s in group for v in (s.curves.energy or [])],
                tension_curve=[v for s in group for v in (s.curves.tension or [])],
                density_curve=[v for s in group for v in (s.curves.density or [])],
                brightness_curve=[v for s in group for v in (s.curves.brightness or [])],
                climax_type="primary" if is_climax else "",
                character="; ".join(dict.fromkeys(ROLE_INTENT.get(r, "") for r in roles if r)),
                gesture=" then ".join(dict.fromkeys(r for r in roles if r)),
            )
        )
        if is_climax:
            arc.primary_climax_section = section_id
    return arc


@_tool
def resolve_motifs(piece_id: str, motif_definitions: List[Dict]) -> Dict[str, Any]:
    """Validate and store motif definitions."""
    motif_definitions = _as_list(motif_definitions, "motif_definitions")
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    # "Validate and store" validated nothing. A definition with no `motif_id`
    # was stored under the empty string, and an empty id can never be elected
    # (`elect_principal_theme` returns it, `if not graph.principal_theme_id`
    # rejects it) nor referenced by any transform. If it is the only motif, the
    # theme system goes inert and says nothing — the caller sees
    # `sections_given_a_theme_statement: 0` with no reason. The commonest way to
    # produce one is writing `"id"` instead of `"motif_id"`.
    nameless = [
        i for i, m in enumerate(motif_definitions) if not str(m.get("motif_id", "")).strip()
    ]
    if nameless:
        return {
            "error": f"motif definition(s) at index {nameless} have no 'motif_id'",
            "hint": (
                "Every motif needs a `motif_id` — it is the key the bank is stored "
                "under and the id a MotifTransform refers to. A motif without one "
                "cannot be elected as the principal theme or placed on any phrase. "
                "(The field is `motif_id`, not `id`.)"
            ),
        }

    for mdef in motif_definitions:
        motif = MotifObject(
            motif_id=mdef.get("motif_id", ""),
            character=mdef.get("character", ""),
            scale_degree_contour=mdef.get("scale_degree_contour", []),
            interval_contour=mdef.get("interval_contour", []),
            rhythm_cell=mdef.get("rhythm_cell", []),
            accent_profile=mdef.get("accent_profile", []),
            recognition_anchor=mdef.get("recognition_anchor", {}),
            allowed_transforms=mdef.get("allowed_transforms", []),
        )
        graph.motif_bank[motif.motif_id] = motif

    # Back-fill theme placements onto slots that already exist.
    #
    # `build_form_graph` writes `slot.motif_transforms` only if
    # `graph.principal_theme_id` is already set, which requires the motif bank to
    # exist at that moment. The documented plan order is motifs (step 4) then
    # form (step 5), but in practice the form is built first — and then nothing
    # ever revisits it. Measured over the twelve pieces in `workspace/`: five have
    # a populated motif bank (3, 5, 6, 3 and 3 motifs) and NOT ONE has an elected
    # principal theme or a single placement on any of its 113 phrases. The theme
    # system — the thing that makes a piece memorable rather than a run of
    # individually plausible phrases — has never been active in a real run.
    #
    # Making the two steps order-independent is the fix; the election logic
    # itself works on every one of those banks.
    placed = _place_principal_theme(graph)

    graph.save(str(workspace / "piece_graph.json"))
    return {
        "motifs_stored": len(graph.motif_bank),
        "motif_ids": list(graph.motif_bank.keys()),
        "principal_theme_id": graph.principal_theme_id,
        "sections_given_a_theme_statement": placed,
    }


def _plan_metric_entry(graph) -> None:
    """Mark the opening phrase as an anacrusis when this composer usually does.

    Deterministic, not random: the decision is seeded by the piece id, so the
    same piece always plans the same way and a rebuild does not silently change
    the music.
    """
    # Read the slots OFF THE GRAPH, not from a caller's list. The graph holds its
    # own PhraseState objects, so mutating a local list of slots changes nothing
    # that gets saved — which is how this field was set correctly in memory and
    # came back empty on the very next load.
    slots = [st.slot for st in graph.phrases.values() if getattr(st, "slot", None)]
    if not slots:
        return
    from .composition_brief import anacrusis_rate, resolve_composer

    warnings: List[str] = []
    composer = resolve_composer(graph, None, warnings)
    try:
        rate = anacrusis_rate(composer)
    except Exception:
        return
    if rate <= 0:
        return
    opening = min(slots, key=lambda s: s.bar_start)
    if opening.metric_entry:
        return  # already decided (a replan, or the planner said so explicitly)
    seed = sum(ord(c) for c in (graph.piece_id or "")) % 1000 / 1000.0
    opening.metric_entry = "anacrusis" if seed < rate else "downbeat"


def _place_principal_theme(graph) -> int:
    """Elect the principal theme and place it at each section opening.

    Idempotent: a section that already carries a placement is left alone, so this
    is safe to call from both `build_form_graph` and `resolve_motifs` regardless
    of which ran first.
    """
    from .theme_planner import elect_principal_theme, plan_section_opening_placements

    if not graph.motif_bank:
        return 0
    if not graph.principal_theme_id:
        graph.principal_theme_id = elect_principal_theme(graph.motif_bank) or ""
    if not graph.principal_theme_id:
        return 0

    by_section: Dict[str, List] = {}
    for state in graph.phrases.values():
        slot = getattr(state, "slot", None)
        if slot is not None:
            by_section.setdefault(slot.section_id, []).append(slot)

    placed = 0
    for section_id, slots in by_section.items():
        slots.sort(key=lambda s: s.bar_start)
        if any(s.motif_transforms for s in slots):
            continue  # this section already has its statement planned
        slots[0].motif_transforms.extend(
            plan_section_opening_placements(
                _infer_section_role(section_id), graph.principal_theme_id
            )
        )
        placed += 1
    return placed


@_tool
def save_narrative(
    piece_id: str,
    sections: List[Dict[str, Any]],
    overall_character: str = "",
    primary_climax_section: str = "",
) -> Dict[str, Any]:
    """Persist the emotional NarrativeArc the agent authored at plan time.

    Each section dict drives composition of every phrase it covers. The
    ``character`` field is the dramatic EVENT in prose (e.g. "the storm finally
    breaks, after three failed attempts to rise") — this is what the
    composition brief surfaces as CREATIVE INTENT and what should drive the
    notes, not the curve-averaged adjectives. Curves (energy/tension/
    brightness/density, 0-1) remain optional shaping cues.

    section dict keys: id, label, bar_start, bar_end, character (prose),
    gesture (optional prose), energy_curve, tension_curve, brightness_curve,
    density_curve (lists of 0-1), climax_type ("primary"|"secondary"|"anti").
    """
    sections = _as_list(sections, "sections")
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    # Bar numbers restart per movement, so in a multi-movement work a section
    # needs to say which movement it belongs to or a phrase at bar 1 of the
    # second movement matches a section covering bars 1-8 of the first.
    n_movements = len(getattr(getattr(graph, "work_graph", None), "movements", None) or [])

    sec_fields = {f.name for f in fields(NarrativeSection)}
    arc = NarrativeArc(
        overall_character=overall_character,
        primary_climax_section=primary_climax_section,
    )
    missing_character = []
    bad_span = []
    unattributed = []
    for sd in sections:
        if not isinstance(sd, dict):
            continue
        sec = NarrativeSection(**{k: v for k, v in sd.items() if k in sec_fields})
        if not (sec.character or "").strip():
            missing_character.append(sec.id or sec.label or f"bars {sec.bar_start}-{sec.bar_end}")
        # A section is matched to phrases by `bar_start <= bar <= bar_end`
        # (see `_creative_intent`), so a span that is inverted or was never
        # given covers NO phrase and the narrative is silently inert there.
        # Missing keys fall through to the dataclass defaults, which is how a
        # section with no bar range at all comes back as a confident 1-8.
        given = "bar_start" in sd and "bar_end" in sd
        if not given or sec.bar_end < sec.bar_start:
            bad_span.append(
                {
                    "section": sec.id or sec.label or "?",
                    "bar_start": sec.bar_start,
                    "bar_end": sec.bar_end,
                    "why": "no bar range given" if not given else "bar_end is before bar_start",
                }
            )
        if n_movements >= 2 and not (getattr(sec, "movement_id", "") or "").strip():
            unattributed.append(sec.id or sec.label or f"bars {sec.bar_start}-{sec.bar_end}")
        arc.sections.append(sec)
    if not primary_climax_section:
        primary = next((s.id for s in arc.sections if s.climax_type == "primary"), "")
        arc.primary_climax_section = primary
    graph.narrative = arc
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "sections_stored": len(arc.sections),
        "overall_character": arc.overall_character,
        "primary_climax_section": arc.primary_climax_section,
        # The agent should author prose intent for every section; warn (don't
        # block) so this stays a planning discipline, not a hard gate.
        "sections_missing_character": missing_character,
        "sections_with_an_unusable_bar_range": bad_span,
        "sections_with_no_movement_id": unattributed,
        "warning": "; ".join(
            w
            for w in (
                (
                    f"{len(missing_character)} section(s) have no authored character prose — "
                    "the brief will fall back to generic curve-adjectives there"
                    if missing_character
                    else ""
                ),
                (
                    f"{len(bad_span)} section(s) cover no bars — a section is matched to "
                    "phrases by bar_start <= bar <= bar_end, so these reach no phrase at all"
                    if bad_span
                    else ""
                ),
                (
                    f"{len(unattributed)} section(s) name no movement_id in a "
                    f"{n_movements}-movement work — bar numbers restart per "
                    "movement, so these may attach to the wrong one"
                    if unattributed
                    else ""
                ),
            )
            if w
        ),
    }


# ─── SCALES Core ─────────────────────────────────────────────────────────────


def planning_gaps(graph) -> List[Dict[str, str]]:
    """Planning inputs that were never supplied, and what each costs the music.

    Every one of these has a silent fallback, so a piece composed without them
    comes out plausible-looking and quietly worse. A peer session measured
    texture, ties, cadences and register all session on pieces with NO thematic
    material, because its harness went `build_form_graph` → `run_scales_section`
    and skipped planning entirely — a legal call sequence that nothing objected
    to. The numbers were valid for what they measured; they were never measuring
    the whole system.

    Reported, never blocking. Composing an unplanned piece deliberately is a
    reasonable thing to do while testing something else; doing it by accident
    and believing the result is not.
    """
    gaps: List[Dict[str, str]] = []
    dna = getattr(graph, "style_dna", None)
    if dna is None or not (getattr(dna, "composer_id", "") or "").strip():
        gaps.append(
            {
                "missing": "style",
                "costs": (
                    "no composer fingerprints, no corpus exemplars in any brief, "
                    "and generic density bands in place of this composer's own"
                ),
                "fix": "compile_style(piece_id, composers=[...])",
            }
        )
    if not getattr(graph, "motif_bank", None):
        gaps.append(
            {
                "missing": "motifs",
                "costs": (
                    "no principal theme, so nothing recurs and the piece has "
                    "nothing to recognise, develop or resolve"
                ),
                "fix": "resolve_motifs(piece_id, [...]) BEFORE build_form_graph",
            }
        )
    # AUTHORED prose, not merely present prose. `_narrative_from_slots` fills
    # `character` for every section by joining entries from `ROLE_INTENT`, a
    # nine-entry table keyed by dramatic role — so a check for "is character
    # non-empty" is satisfied on every piece ever built and can never fire.
    # A gap that cannot fire is worse than no gap: it reports readiness it never
    # tested. Derived prose is drawn from that closed vocabulary, which is what
    # makes this decidable without a new field.
    from .dramatic_plan import ROLE_INTENT

    # Whole entries, subtracted as SUBSTRINGS. Splitting the character text on
    # ";" and comparing the parts does not work: the table's own entries contain
    # semicolons ("state the idea plainly and let it be heard; nothing here needs
    # to prove anything"), so splitting shreds them and every derived section
    # then looks authored — the check passing for the wrong reason, which reads
    # exactly like the feature working.
    derived = sorted(
        (t.strip() for t in ROLE_INTENT.values() if t and t.strip()), key=len, reverse=True
    )

    def _is_authored(text: str) -> bool:
        rest = str(text)
        for entry in derived:
            rest = rest.replace(entry, "")
        return bool(rest.strip(" ;,.\t\n"))

    narrative = getattr(graph, "narrative", None)
    sections = list(getattr(narrative, "sections", None) or []) if narrative else []
    authored = [
        sec
        for sec in sections
        if (getattr(sec, "character", "") or "").strip() and _is_authored(sec.character)
    ]
    if not authored:
        gaps.append(
            {
                "missing": "narrative",
                "costs": (
                    "no section has authored character prose — every one is the "
                    "role table's own words, so the brief's CREATIVE INTENT says "
                    "the same thing for every piece with the same form"
                ),
                "fix": "save_narrative(piece_id, sections=[...]) with `character` prose",
            }
        )
    if not getattr(graph, "reference_studies", None):
        gaps.append(
            {
                "missing": "reference_study",
                "costs": (
                    "briefs carry corpus bars but not the agent's own reading of "
                    "whole scores — the 'WHAT YOU LEARNED FROM THE SCORES' section "
                    "of every brief is empty"
                ),
                "fix": "list_reference_scores / get_reference_score / save_reference_study",
            }
        )
    return gaps


#: Transforms that present the theme so a listener is meant to RECOGNISE it.
#: `fragment`, `sequence`, `diminish` and `liquidate` are development — the
#: theme is being worked, not stated, and a bar of it does not have to be whole.
_THEME_STATEMENT_OPS = frozenset({"state", "augment", "invert", "retrograde", "reharmonize"})


def _theme_statement_bars(graph, slot) -> frozenset:
    """Bars where a theme is STATED, and so must keep their downbeat.

    A `MotifTransform` records the operation and the motif id and no position,
    so where the statement sits has to be reconstructed: a placement is made on
    a section's opening phrase, and the motif's own `rhythm_cell` says how many
    bars it spans. Protecting the whole phrase instead is measurably too much —
    it silenced `_rest_the_downbeat` on every planned piece.
    """
    if slot is None:
        return frozenset()
    ops = {
        str(getattr(t, "operation", "") or "").lower()
        for t in (getattr(slot, "motif_transforms", None) or [])
    }
    if not (ops & _THEME_STATEMENT_OPS):
        return frozenset()

    from .duration import bar_duration, dur_to_beats

    span = 0.0
    for transform in getattr(slot, "motif_transforms", None) or []:
        motif_id = (getattr(transform, "params", None) or {}).get("motif_id", "")
        motif = (graph.motif_bank or {}).get(motif_id)
        cell = list(getattr(motif, "rhythm_cell", None) or []) if motif else []
        span = max(span, sum(float(dur_to_beats(d) or 0) for d in cell))
    per_bar = float(bar_duration(tuple(slot.meter))) or 4.0
    # A motif whose length cannot be read still gets its first bar; a placement
    # that protects nothing would be the same defect one level down.
    bars = max(1, int(-(-span // per_bar))) if span > 0 else 1
    bars = min(bars, int(slot.bar_count or 1))
    return frozenset(range(slot.bar_start, slot.bar_start + bars))


@_tool
def run_scales_section(
    piece_id: str,
    section_id: str,
    k_sketches: int = 3,
    n_realizations: int = 4,
    beam_width: int = 5,
    use_v6_pipeline: bool = True,
    run_style_gate: bool = False,
) -> Dict[str, Any]:
    """Run the full SCALES algorithm on one section.

    This is the main engine entry point. When use_v6_pipeline=True,
    uses the context-aware surface composer with onset bundles.
    Falls back to the original realizer when v6 components are unavailable.

    When run_style_gate=True, after committing the best path, runs
    ``run_style_review_section`` and attaches results under ``style_review``.
    """
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    composer_id = graph.style_dna.composer_id
    if "+" in composer_id:
        composer_id = composer_id.split("+")[0].replace("blend:", "")

    # Set up classic components
    pb = PhraseBank(composer_id)
    gb = GestureBank(composer_id)
    cb = CadenceBank(composer_id)

    proposer = SketchProposer(pb, gb, cb)
    realizer = Realizer(gb, cb, motif_bank=graph.motif_bank)
    reducer = Reducer()
    scorer = CandidateScorer(reducer)
    search = SectionSearch()

    phrase_order = graph.get_section_phrases(section_id)

    if not phrase_order:
        return {"error": f"No phrases found for section {section_id}"}

    # Set up v6 components if available
    pr = None
    cr = None
    hs = None
    sc = None
    cc = None
    cbr = None
    _kept_authored: List[str] = []
    cross_ledger = None
    section_contract = graph.section_contracts.get(section_id)
    style_program = graph.style_program

    if use_v6_pipeline and style_program:
        pr = PatternRetriever()
        # Corpus bars: tier A/B use target composer; C/D use donor corpus when available
        from .corpus_bar_retriever import CorpusBarRetriever

        tier = style_program.dna.tier if style_program.dna else "D"
        cbr = None
        if tier in ("A", "B"):
            cbr = CorpusBarRetriever(composer_id)
        elif tier in ("C", "D") and style_program.donor_plan and style_program.donor_plan.donors:
            donors_sorted = sorted(
                style_program.donor_plan.donors,
                key=lambda x: -x[1],
            )
            for donor_composer, _w in donors_sorted:
                try:
                    cand = CorpusBarRetriever(donor_composer)
                    if cand.bar_count > 0:
                        cbr = cand
                        break
                except Exception:
                    continue
        cr = ContextRouter(pr, corpus_bar_retriever=cbr)
        hs = HarmonicSolver()
        # Set up phrase-level composer with all retrieval banks
        sc = SurfaceComposer(
            pattern_retriever=pr,
            phrase_bank=pb,
            gesture_bank=gb,
            corpus_bar_retriever=cbr,
            cadence_bank=cb,
            motif_bank=graph.motif_bank,
        )
        cc = CraftChecker()
        # Use CrossScaleLedger instead of bare ExpectationLedger —
        # restored from the graph so promises/debts survive across runs
        # and movements (defensive load: a bad payload yields a fresh one)
        saved_ledger = getattr(graph, "cross_scale_ledger", None)
        if saved_ledger:
            try:
                cross_ledger = CrossScaleLedger.from_dict(saved_ledger)
            except Exception:
                cross_ledger = CrossScaleLedger()
        else:
            cross_ledger = CrossScaleLedger()

    # Use cross-scale ledger's phrase delegate, or standalone for classic
    ledger = cross_ledger.phrase_ledger if cross_ledger else ExpectationLedger()

    # For each phrase: sketch → realize → reduce → score
    all_candidates: Dict[str, List[CandidateNode]] = {}
    all_traces: Dict[str, ContextTrace] = {}
    prev_surface = None

    for pi, phrase_id in enumerate(phrase_order):
        phrase_state = graph.phrases.get(phrase_id)
        if not phrase_state:
            continue
        slot = phrase_state.slot

        # Agent-authored LayerIR: Claude wrote final notes — do not run engine
        if getattr(phrase_state, "agent_authored", False) and phrase_state.realized is not None:
            _kept_authored.append(phrase_id)
            sketch_for_score = phrase_state.sketch
            if sketch_for_score is None:
                prop = proposer.propose(slot, graph.style_dna, k=1)
                sketch_for_score = prop[0] if prop else SketchIR(phrase_id=phrase_id)
            surface = phrase_state.realized
            reduced = reducer.reduce(surface)
            agent_node = CandidateNode(
                phrase_id=phrase_id,
                sketch_idx=0,
                realization_idx=0,
                sketch=sketch_for_score,
                surface=surface,
                reduced=reduced,
            )
            candidates = [agent_node]
            if phrase_id not in all_traces:
                all_traces[phrase_id] = ContextTrace(
                    phrase_id=phrase_id,
                    total_bar_count=slot.bar_count,
                    gestures_applied=["agent_authored:layer_ir"],
                )
            scorer_kwargs_ag: Dict[str, Any] = {}
            if style_program:
                scorer_kwargs_ag["context_traces"] = {0: all_traces[phrase_id]}
                scorer_kwargs_ag["anti_patterns"] = style_program.anti_patterns
                scorer_kwargs_ag["tier"] = style_program.dna.tier
            scorer.score_all(
                candidates,
                slot,
                graph.style_dna,
                ledger,
                phrase_order,
                prev_surface,
                graph.contract.locks,
                graph.mode,
                **scorer_kwargs_ag,
            )
            all_candidates[phrase_id] = candidates
            if candidates:
                prev_surface = candidates[0].surface
            continue

        # Phase 1: Use Claude-authored sketch if available, else propose K candidates
        if phrase_state.sketch is not None:
            # Claude wrote this sketch — use it as the sole candidate
            sketches = [phrase_state.sketch]
        else:
            sketches = proposer.propose(slot, graph.style_dna, k=k_sketches)

        # Phase 2: Realize N candidates per sketch
        candidates = []
        for si, sketch in enumerate(sketches):
            if sc and cr and hs and style_program:
                # ─── v6 pipeline: context-aware onset bundle composition ───
                # Resolve context for this phrase
                phrase_ctx = cr.resolve(
                    style_program,
                    slot,
                    section_contract=section_contract,
                    phrase_index=pi,
                    total_phrases=len(phrase_order),
                )

                # Build harmonic cells from sketch's harmonic rhythm
                h_cells = [
                    HarmonicCell(bar=h.bar, beat=h.beat, roman=h.roman, key=h.key or slot.key)
                    for h in sketch.harmonic_rhythm
                ]

                # Solve harmonic voicings
                voicings = hs.solve(h_cells, slot.key, slot.meter)

                # Build PhraseControlIR from sketch + slot
                control = PhraseControlIR(
                    phrase_id=phrase_id,
                    section_id=slot.section_id,
                    phrase_function=slot.function,
                    bars=slot.bar_count,
                    bar_start=slot.bar_start,
                    meter=slot.meter,
                    tempo_bpm=slot.tempo_bpm,
                    local_key=slot.key,
                    cadence_target=slot.cadence_target,
                    cadence_bar=slot.cadence_bar,
                    harmonic_cells=h_cells,
                    melody_anchors=sketch.melody_anchors,
                    bass_anchors=sketch.bass_anchors,
                    dynamic_shape=sketch.dynamic_shape,
                    expression_marks=sketch.expression_marks,
                    cadence=sketch.cadence,
                    # Context hooks — prove context shaped this phrase
                    fingerprint_contract=[fp.id for fp in phrase_ctx.fingerprint_targets],
                    anti_pattern_set=[ap.id for ap in phrase_ctx.active_anti_patterns],
                    gesture_plan=[g.id for g in phrase_ctx.active_gestures],
                )
                # Copy texture program from slot
                from .models import TextureProgram

                control.texture_program = TextureProgram(bars=slot.texture_plan)
                control.motif_slots = [
                    MotifSlot(
                        bar=mp.bar,
                        beat=mp.beat,
                        motif_id=mp.motif_id,
                        transform=mp.transform,
                        voice=mp.voice or "melody",
                        params=dict(mp.params or {}),
                    )
                    for mp in (sketch.motif_placements or [])
                ]

                for variant in range(n_realizations):
                    # Compose onset bundles
                    bundles, trace = sc.compose(
                        control,
                        phrase_ctx,
                        voicings,
                        style_program,
                        variant=variant,
                    )

                    # Convert to LayerIR for compatibility
                    surface = sc.bundles_to_layer_ir(
                        bundles,
                        phrase_id,
                        slot.key,
                        slot.meter,
                        slot.bar_count,
                        instrumentation=_contract_instrumentation(graph),
                    )

                    # Self-reduction
                    reduced = reducer.reduce(surface)

                    node = CandidateNode(
                        phrase_id=phrase_id,
                        sketch_idx=si,
                        realization_idx=variant,
                        sketch=sketch,
                        surface=surface,
                        reduced=reduced,
                    )
                    candidates.append(node)

                    # Store trace for first variant
                    if variant == 0:
                        all_traces[phrase_id] = trace

            else:
                # ─── Classic pipeline: hardcoded realizer ───
                realizations = realizer.realize(
                    sketch,
                    slot,
                    graph.style_dna,
                    n=n_realizations,
                    motif_bank=graph.motif_bank,
                )

                for ri, surface in enumerate(realizations):
                    reduced = reducer.reduce(surface)
                    node = CandidateNode(
                        phrase_id=phrase_id,
                        sketch_idx=si,
                        realization_idx=ri,
                        sketch=sketch,
                        surface=surface,
                        reduced=reduced,
                    )
                    candidates.append(node)

        # Phase 4: Score all candidates (with v6 context if available)
        scorer_kwargs: Dict[str, Any] = {}
        if style_program:
            # Build per-candidate context traces for scoring
            cand_traces: Dict[int, ContextTrace] = {}
            if phrase_id in all_traces:
                for ci in range(len(candidates)):
                    cand_traces[ci] = all_traces[phrase_id]
            scorer_kwargs["context_traces"] = cand_traces
            scorer_kwargs["anti_patterns"] = style_program.anti_patterns
            scorer_kwargs["tier"] = style_program.dna.tier

        scorer.score_all(
            candidates,
            slot,
            graph.style_dna,
            ledger,
            phrase_order,
            prev_surface,
            graph.contract.locks,
            graph.mode,
            **scorer_kwargs,
        )

        all_candidates[phrase_id] = candidates

        # Track best for continuity
        if candidates:
            prev_surface = candidates[0].surface

    # Phase 5: Section-level beam search
    best_path = search.beam_search(
        all_candidates,
        phrase_order,
        mode=graph.mode,
        beam_width=beam_width,
    )

    # Phase 6: Commit best path
    engine_repairs: Dict[str, Dict[str, int]] = {}
    engine_engraving: Dict[str, Dict[str, Any]] = {}
    # WHAT EACH SURFACE PASS ACTUALLY DID.
    #
    # A pass that never fired and a pass that correctly found nothing to do are
    # indistinguishable in every log we have: both return 0 and say nothing.
    # `_rest_the_downbeat` was inert on every planned piece — a motif placement
    # protects a whole phrase and planning puts one on most of them — and
    # reported exactly what it would have reported if it had been working. The
    # `planning_gaps` report says which INPUTS were missing; this says which
    # passes actually reached the notes.
    # The last report from each pass, carrying its decline reasons. A section
    # runs a pass once per phrase, so this is the final phrase's detail — enough
    # to say WHICH rule is declining, which a bare count cannot.
    _pass_reports: Dict[str, Dict[str, Any]] = {}
    _passes: Dict[str, int] = {
        "melody_thickened": 0,
        "bass_thickened": 0,
        "cadences_shaped": 0,
        "barline_ties": 0,
        "downbeat_rests": 0,
    }
    for node in best_path.nodes:
        if node.surface:
            # The engine path committed straight to the graph with NO physical
            # validation, while the agent path has enforced meter, range and
            # same-voice overlap at commit for months. A probe of one
            # three-phrase section found 65 meter errors going silently to the
            # score: bars holding 4.875 beats of a 4/4, notes starting while the
            # same voice was still sounding, and beat positions like 1.56 that
            # are not on any notatable grid. Repair what is mechanically
            # repairable, and report the rest.
            repairs = _repair_engine_surface(
                node.surface, tuple(slot_meter_for(graph, node.phrase_id))
            )
            if repairs:
                engine_repairs[node.phrase_id] = repairs
            # Give the melody weight at its arrivals. AFTER the repair, because
            # a doubling shares its principal's onset and the repair measures
            # each note's room against the next later one — thickening first
            # made it re-measure spans it had already settled.
            from .surface_composer import (
                _clamp_to_period_register,
                _hold_over_barline,
                _rest_the_downbeat,
                _shape_the_cadence,
                _thicken_bass_foundation,
                _thicken_principal_line,
            )

            # NEVER on a phrase the agent wrote. The engine is the fallback;
            # adding so much as a doubling to the agent's own notes breaks the
            # one guarantee this path makes.
            _existing = graph.phrases.get(node.phrase_id)
            if not getattr(_existing, "agent_authored", False):
                _passes["melody_thickened"] += _thicken_principal_line(
                    node.surface,
                    node.surface.key
                    or getattr(getattr(_existing, "slot", None), "key", "")
                    or "C major",
                    report=_pass_reports.setdefault("melody_thickened", {}),
                )
                _passes["bass_thickened"] += _thicken_bass_foundation(
                    node.surface,
                    node.surface.key
                    or getattr(getattr(_existing, "slot", None), "key", "")
                    or "C major",
                    report=_pass_reports.setdefault("bass_thickened", {}),
                    composer=composer_id,
                )
                # Before the tie pass, which must not find a note it is about
                # to bind already rewritten underneath it.
                _slot = getattr(_existing, "slot", None)
                if _slot is not None:
                    _passes["cadences_shaped"] += int(
                        _shape_the_cadence(
                            node.surface,
                            tuple(slot_meter_for(graph, node.phrase_id)),
                            getattr(_slot, "cadence_target", "none"),
                            _slot.bar_start + _slot.bar_count - 1,
                        )
                    )
                _passes["barline_ties"] += _hold_over_barline(
                    node.surface,
                    tuple(slot_meter_for(graph, node.phrase_id)),
                    composer=composer_id,
                    protect_bars=_theme_statement_bars(graph, _slot),
                    report=_pass_reports.setdefault("barline_ties", {}),
                )
                # The OTHER way a bar avoids a fresh downbeat: it opens with a
                # rest. `_hold_over_barline` ties into the bar; nothing let the
                # melody simply be silent there, and this engine wrote ZERO
                # leading rests in any layer across two complete pieces where
                # real melodies rest on 3-9% of downbeats. After the tie pass,
                # which must not find a note it is about to bind already turned
                # into a rest.
                _passes["downbeat_rests"] += _rest_the_downbeat(
                    node.surface,
                    tuple(slot_meter_for(graph, node.phrase_id)),
                    composer=composer_id,
                    bar_start=getattr(_slot, "bar_start", 1) if _slot is not None else 1,
                    # The theme is the one thing that must be heard — but
                    # protecting the WHOLE phrase carrying it makes this pass
                    # inert on the path the pipeline actually runs.
                    # `build_form_graph` puts a placement on every section's
                    # opening phrase, which is 5 of 9 phrases in a ternary and 9
                    # of 17 in a sonata, and the measured rate came out at 2.4%
                    # against Haydn's real 7.5%. (My own verification run had
                    # missed it, on a piece with no motifs — which is what
                    # `planning_gaps` exists to catch, and it caught its author
                    # one turn after I wrote it.)
                    #
                    # A MotifTransform carries no bar, so the bars it occupies
                    # are not recorded — but the motif's own rhythm says how
                    # long it is, and a placement lands at the phrase's opening.
                    # So the statement's bars are protected instead of the
                    # phrase's, and only for the transforms that present the
                    # theme WHOLE. A fragment or a liquidation is development;
                    # it is not the bar a listener needs intact.
                    protect_bars=_theme_statement_bars(graph, _slot),
                )
                # LAST of the surface passes: the widened melody range is the
                # union across every composer, and Bach's harpsichord stops a
                # major third below its ceiling. Bring anything the instrument
                # did not have back by octaves.
                _clamp_to_period_register(node.surface, composer_id)
                # REPAIR AGAIN. Thickening and holding both rewrite the surface
                # the repair had just settled, and nothing re-checked it before
                # `commit_phrase` — so a phrase reached the graph with onsets
                # the repair would have fixed had it seen them. The committed
                # LayerIR of a 3/8 section carried a 64th at 67/48 of a beat,
                # which no binary note can sit on, and the bar could then not
                # tile: music21 filled the gap and the measure exported over its
                # meter. One bar per piece, in the bass staff, every time.
                #
                # The repair is idempotent by construction — every pass either
                # leaves an event alone or moves it onto the grid — so running
                # it after the passes that disturb it costs a second walk and
                # nothing else.
                second = _repair_engine_surface(
                    node.surface, tuple(slot_meter_for(graph, node.phrase_id))
                )
                for key, count in (second or {}).items():
                    engine_repairs.setdefault(node.phrase_id, {})
                    engine_repairs[node.phrase_id][key] = (
                        engine_repairs[node.phrase_id].get(key, 0) + count
                    )
            # The engraver's pass runs on the agent path (`_gated_commit`) and
            # did not run here, so every phrase the ENGINE realized reached the
            # page unengraved. Measured on a fresh three-phrase section: 229
            # events carrying 0 slurs, 0 articulations, 0 hairpins, 0 ornaments
            # and 0 pedal marks — dynamics only, straight from the realizer.
            # That is what a score with 0.00 marks per bar looks like, and the
            # fallback is exactly the path used for anything the agent did not
            # author. `enrich_layer_ir` only fills fields left None, so it
            # cannot overwrite the engine's own decisions.
            engraved = _engrave_phrase(graph, node.phrase_id, node.surface, composer_id)
            if engraved and engraved.get("ok") is not False:
                engine_engraving[node.phrase_id] = {
                    k: v for k, v in engraved.items() if isinstance(v, (int, float)) and v
                }
            graph.commit_phrase(node.phrase_id, node.surface)
            # Both of these run on the agent path at commit and ran on neither
            # here. Their absence is silent and compounding:
            #   * the PRINCIPAL THEME is captured from the phrase that first
            #     states it. When the engine realizes the opening section — the
            #     usual case for a fallback — nothing captured it, so
            #     `principal_theme_phrase()` returned "" and there was no theme
            #     to bring back, develop, or recognise. A piece cannot have a
            #     memorable theme if nothing ever recorded what the theme was.
            #   * expectations are DISCHARGED on commit. Recording promises at
            #     plan time and never closing them leaves every debt open for
            #     the whole piece, which is the same bug `_settle_expectations`
            #     was written to fix on the other path.
            _capture_theme_if_first_statement(graph, node.phrase_id)
            _settle_expectations(graph, node.phrase_id)

    # Phase 6b: Populate expectations from committed phrases
    try:
        for node in best_path.nodes:
            trace = all_traces.get(node.phrase_id)
            if not trace:
                continue

            # Chromatic devices used → add DEBT for tonal resolution
            if trace.devices_used:
                if cross_ledger is not None:
                    cross_ledger.add_section_expectation(
                        exp_type=ExpectationType.DEBT.value,
                        domain=ExpectationDomain.HARMONY_TONAL.value,
                        object_ref=f"tonal_resolution_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        urgency=0.6,
                        details={
                            "chromatic_devices": trace.devices_used,
                            "section": section_id,
                        },
                    )
                elif ledger is not None:
                    ledger.add_debt(
                        object_ref=f"tonal_resolution_{node.phrase_id}",
                        opened_at=node.phrase_id,
                        urgency=0.6,
                        details={
                            "chromatic_devices": trace.devices_used,
                            "section": section_id,
                        },
                    )

            # Motif/fingerprint placement → add PROMISE for motif development
            if trace.fingerprints_expressed:
                if cross_ledger is not None:
                    cross_ledger.add_section_expectation(
                        exp_type=ExpectationType.PROMISE.value,
                        domain=ExpectationDomain.MOTIF_THEME.value,
                        object_ref=f"motif_development_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        expected_form="motif development or return",
                        urgency=0.5,
                        details={
                            "fingerprints": trace.fingerprints_expressed,
                            "section": section_id,
                        },
                    )
                elif ledger is not None:
                    ledger.add_promise(
                        object_ref=f"motif_development_{node.phrase_id}",
                        introduced_at=node.phrase_id,
                        expected_form="motif development or return",
                        urgency=0.5,
                        details={
                            "fingerprints": trace.fingerprints_expressed,
                            "section": section_id,
                        },
                    )
    except Exception:
        pass  # Ledger not available — skip gracefully

    # Phase 7 (v6): Compute context utilization + enforce minimum context
    cu_report = None
    anti_results: List[Dict] = []
    context_violations: List[str] = []
    if style_program and all_traces:
        tier = style_program.dna.tier if style_program.dna else "D"

        # Run anti-pattern detection on committed surfaces
        prev_layer = None
        for node in best_path.nodes:
            if node.surface:
                results = run_all_detectors(node.surface, style_program.anti_patterns, prev_layer)
                anti_results.extend(results)
                prev_layer = node.surface

        cu_report = compute_utilization(
            all_traces,
            style_program.fingerprint_contract,
            anti_results,
            tier,
        )
        graph.context_traces = all_traces
        graph.context_utilization = cu_report

        # Enforce minimum context package per phrase (informational)
        fallback_budgets = {"A": 0.10, "B": 0.20, "C": 0.35, "D": 1.0}
        budget = fallback_budgets.get(tier, 1.0)
        for pid, trace in all_traces.items():
            fallback_ratio = trace.fallback_bar_count / max(trace.total_bar_count, 1)
            if fallback_ratio > budget:
                context_violations.append(
                    f"{pid}: fallback ratio {fallback_ratio:.0%} exceeds budget {budget:.0%}"
                )
            if (
                not trace.corpus_patterns_used
                and not trace.corpus_bars_used
                and not trace.gestures_applied
            ):
                context_violations.append(f"{pid}: no corpus reference (pattern, bar, or gesture)")

        # Run craft checks on committed surfaces
        if cc:
            for node in best_path.nodes:
                if node.surface:
                    ps = graph.phrases.get(node.phrase_id)
                    if ps:
                        ps.craft_check = cc.check(node.surface)

    graph.phase = PipelinePhase.REALIZING.value

    # Persist the cross-scale ledger so musical promises/debts carry
    # forward to later sections and movements
    if cross_ledger is not None:
        try:
            graph.cross_scale_ledger = cross_ledger.to_dict()
        except Exception:
            pass

    graph.save(str(workspace / "piece_graph.json"))

    result: Dict[str, Any] = {
        "section_id": section_id,
        # What the ENGINE actually wrote. This reported the whole path length,
        # so running the fallback over a section Claude had already composed
        # said "3 phrases realized" while correctly leaving all three alone —
        # an orchestrator reading that would believe work had been done.
        "phrases_realized": len(best_path.nodes) - len(_kept_authored),
        "phrases_kept_agent_authored": len(_kept_authored),
        "phrases_in_path": len(best_path.nodes),
        "path_score": best_path.total_score,
        "transition_scores": best_path.transition_scores,
        "pipeline": "v6" if (sc and style_program) else "classic",
    }
    # What planning never supplied. Each has a silent fallback, so a piece
    # composed without them looks fine and is quietly worse.
    gaps = planning_gaps(graph)
    if gaps:
        result["planning_gaps"] = gaps
        _LOG.warning(
            "%s composed with no %s — see `planning_gaps` in the result",
            section_id,
            ", ".join(g["missing"] for g in gaps),
        )
    if engine_repairs:
        # Never silent. A repaired surface means the generator produced
        # something that could not be engraved, and the caller should see it.
        result["engine_repairs"] = engine_repairs
    # Reported ALWAYS, including the zeroes — a zero is the informative case.
    result["surface_passes"] = dict(_passes)
    if _pass_reports:
        result["surface_pass_detail"] = {k: v for k, v in _pass_reports.items() if v}
    idle = sorted(name for name, count in _passes.items() if not count)
    if idle:
        result["surface_passes_idle"] = idle
        _LOG.warning("engine surface repairs in %s: %s", section_id, engine_repairs)

    if engine_engraving:
        # What the ENGRAVER added, separate from what the engine composed — so a
        # reviewer can tell one from the other, which is the whole reason the
        # enricher reports at all.
        result["engraving"] = engine_engraving

    if cu_report:
        result["context_utilization"] = {
            "corpus_coverage": cu_report.corpus_coverage,
            "fallback_ratio": cu_report.fallback_ratio,
            "fingerprint_coverage": cu_report.fingerprint_coverage,
            "anti_patterns_detected": cu_report.anti_patterns_detected,
            "gestures_applied": cu_report.gestures_applied,
            "breathing_rules_applied": cu_report.breathing_rules_applied,
        }
        # The corpus-utilization floor is a GATE, not a footnote: a section
        # that exceeds its tier's fallback budget or contains phrases with no
        # corpus reference at all has not met the corpus-armed bar and must be
        # re-armed / re-composed before it is treated as done.
        result["context_gate"] = {
            "passed": not context_violations,
            "tier": tier,
            "violations": context_violations,
        }
        if context_violations:
            result["needs_attention"] = (
                f"context_gate FAILED for tier {tier}: {len(context_violations)} "
                f"phrase(s) under-used the corpus (see context_gate.violations). "
                f"Arm the composer (acquire_composer.py) or re-compose the "
                f"flagged phrases — do not treat this section as complete."
            )

    if run_style_gate:
        try:
            result["style_review"] = run_style_review_section(
                piece_id,
                section_id,
                threshold=0.35,
                persist=True,
            )
        except Exception as exc:
            result["style_review"] = {"error": str(exc)}

    return result


# ─── Form Builders ───────────────────────────────────────────────────────────


# ─── Form specifications ─────────────────────────────────────────────────────
#
# A form is DATA: an ordered list of phrase specs. Every form used to be built
# from identical 8-bar phrases (ternary = 8+8 | 8+8 | 8+8; theme-and-variations
# = 8+8 per variation), which puts a cadence in every eighth bar for the whole
# piece. Uniform phrase rhythm is one of the strongest machine tells there is —
# real classical phrases run 4, 5, 6, 8, 10 bars, extend, elide, and are
# answered by asymmetric consequents. These specs give each form its own phrase
# rhythm, and the key roles are resolved through the interval helpers so any
# key spelling works.
#
# Each entry: (section, bars, function, cadence, key_role)
#   key_role ∈ tonic | relative | dominant | subdominant | parallel

_PF = PhraseFunction
_CT = CadenceTarget

# A cadence at the end of every phrase is a cadence every four to six bars for
# the whole piece, which is a metronome at the structural level. Real phrases run
# INTO one another: a continuation that is spinning the idea out does not stop to
# cadence, it evades or simply carries on (CT.NONE), and only the structural
# arrivals — the end of a section, the confirmation, the close — actually land.
_TERNARY_SPEC = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.NONE.value, "tonic"),  # runs on
    ("m1_a", 6, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "relative"),
    ("m1_b", 5, _PF.CONTINUATION.value, _CT.IAC.value, "relative"),
    ("m1_retr", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_a2", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),  # elides into the drive
    ("m1_a2", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ("m1_coda", 4, _PF.CODA.value, _CT.PLAGAL.value, "tonic"),
]

# ── Binary and rounded binary ────────────────────────────────────────────────
#
# The two commonest forms in the repertoire this project is armed for, and
# neither had a spec: every Baroque dance (allemande, courante, sarabande,
# gigue), every Scarlatti sonata, and — as rounded binary — the minuet, the trio
# and most Classical dance movements. Asking for a `binary` gigue silently built
# a four-phrase A-B-A' song form, which is not a gigue in any respect that
# matters: no modulation to the dominant, no double bar, no return.
#
# SIMPLE BINARY ‖: A :‖: B :‖ — A leaves the tonic and cadences in the new key
# (the dominant from a major tonic, the relative major from a minor one, which
# is why the second half of `_binary_spec` is chosen from the mode rather than
# fixed); B works back and closes in the tonic. The two halves balance; B is
# usually the longer, because getting home takes more room than leaving.
#: The forms `build_form_graph` dispatches. One list, so the warning message,
#: the result field and the tests cannot disagree about what exists — a
#: hardcoded copy in the test broke on every form ADDED to the system.
_KNOWN_FORMS = ("binary", "rounded_binary", "ternary", "sonata", "theme_variations")

_BINARY_SPEC_MAJOR = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.NONE.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "dominant"),
    ("m1_b", 4, _PF.CONTINUATION.value, _CT.EVADED.value, "dominant"),
    ("m1_b", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_b", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
]
_BINARY_SPEC_MINOR = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.NONE.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "relative"),
    ("m1_b", 4, _PF.CONTINUATION.value, _CT.EVADED.value, "relative"),
    ("m1_b", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_b", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
]

# ROUNDED BINARY ‖: A :‖: B A' :‖ — the same departure, then the opening
# material RETURNS in the tonic. The difference from ternary is that A' is a
# reprise inside the second half rather than a third section, so B is short: a
# digression, not a contrasting theme.
_ROUNDED_BINARY_SPEC_MAJOR = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.NONE.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "dominant"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "dominant"),
    ("m1_b", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_a2", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),
    ("m1_a2", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
]
_ROUNDED_BINARY_SPEC_MINOR = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.NONE.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "relative"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "relative"),
    ("m1_b", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_a2", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),
    ("m1_a2", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
]


# A complete sonata movement: exposition, development, recapitulation, coda.
# Building only the exposition (as before) meant asking for sonata form got a
# fragment that stops after the closing theme, in the wrong key, with the
# development's promised recapitulation never arriving.
_SONATA_SPEC = [
    ("m1_pt", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_pt", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_tr", 6, _PF.TRANSITION.value, _CT.EVADED.value, "dominant"),
    ("m1_st", 4, _PF.CONTRASTING_THEME.value, _CT.HC.value, "dominant"),
    ("m1_st", 4, _PF.CONTINUATION.value, _CT.NONE.value, "dominant"),
    ("m1_st", 5, _PF.CADENTIAL.value, _CT.PAC.value, "dominant"),
    ("m1_cl", 4, _PF.CLOSING.value, _CT.PAC.value, "dominant"),
    ("m1_dev", 6, _PF.FRAGMENTATION.value, _CT.NONE.value, "relative"),
    ("m1_dev", 8, _PF.SEQUENCE.value, _CT.NONE.value, "subdominant"),
    ("m1_dev", 6, _PF.LIQUIDATION.value, _CT.NONE.value, "parallel"),
    ("m1_dev", 4, _PF.RETRANSITION.value, _CT.HC.value, "tonic"),
    ("m1_rec_pt", 4, _PF.RETURN.value, _CT.NONE.value, "tonic"),
    ("m1_rec_pt", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_rec_tr", 4, _PF.TRANSITION.value, _CT.EVADED.value, "tonic"),
    ("m1_rec_st", 4, _PF.RETURN_VARIED.value, _CT.NONE.value, "tonic"),
    ("m1_rec_st", 6, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ("m1_coda", 6, _PF.CODA.value, _CT.PAC.value, "tonic"),
]

_SIMPLE_SPEC = [
    ("m1_a", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
    ("m1_a", 4, _PF.CONTINUATION.value, _CT.PAC.value, "tonic"),
    ("m1_b", 4, _PF.CONTRASTING_THEME.value, _CT.EVADED.value, "relative"),
    ("m1_a2", 6, _PF.RETURN.value, _CT.PAC.value, "tonic"),
]

# Each variation gets its own character: a key role, a phrase rhythm, and a
# tempo scaling. Giving every variation the same key, meter, length and cadence
# plan (as before) makes a set of variations that vary nothing structural.
_VARIATION_CHARACTERS = [
    {"key_role": "tonic", "bars": (4, 4), "tempo_scale": 1.0, "label": "figural"},
    {"key_role": "parallel", "bars": (4, 6), "tempo_scale": 0.75, "label": "minore"},
    {"key_role": "tonic", "bars": (4, 5), "tempo_scale": 1.25, "label": "brillante"},
    {"key_role": "subdominant", "bars": (6, 6), "tempo_scale": 0.85, "label": "cantabile"},
]


def _key_for_role(key: str, role: str) -> str:
    """Resolve a form spec's key role against the piece's tonic."""
    fns = {
        "tonic": lambda k: k,
        "relative": _relative_key,
        "dominant": _dominant_key,
        "subdominant": _subdominant_key,
        "parallel": _parallel_key,
    }
    return fns.get(role, lambda k: k)(key)


def _build_from_spec(
    spec, key, tempo, meter, style, movement_id: str = "m1", bar_offset: int = 0
) -> List[PhraseSlot]:
    """Materialize a form spec into PhraseSlots with running bar numbers.

    ``bar_offset`` places this movement AFTER the ones already built. The cursor
    started at 1 for every movement, so a three-movement work laid all three on
    top of each other: the assembler collects events by absolute bar, and bar 1
    held movement I's, II's and III's opening bars at once. In a real run that
    was 34 of 41 bars overfull — a 2/4 bar carrying 8 beats — with the metre
    flip-flopping 2/4, 3/4, 4/4, 2/4 down the page and three final barlines
    inside the score. The movement-heading and movement-barline machinery was
    written assuming bar numbers are globally unique, which they were, right up
    until a second movement existed.

    Every form spec hardcodes an ``m1_`` prefix, so a second movement built into
    the same piece produced phrase ids that COLLIDED with the first and silently
    replaced them — a sonata's ``m1_a_p1`` overwritten by a ternary's. The
    documented ``m2_a`` convention was unreachable. The prefix is rewritten here
    so each movement gets its own namespace.
    """
    phrases: List[PhraseSlot] = []
    bar = 1 + max(0, int(bar_offset or 0))
    counters: Dict[str, int] = {}
    from .dramatic_plan import role_for

    mid = str(movement_id or "m1")
    for section_id, bars, fn, cad, key_role in spec:
        section_id = re.sub(r"^m\d+_", f"{mid}_", section_id) if mid != "m1" else section_id
        counters[section_id] = counters.get(section_id, 0) + 1
        slot_key = _key_for_role(key, key_role)
        # Resolve the dramatic role BEFORE the harmony is sampled: an opening
        # statement and a crisis should not be handed the same palette, and the
        # sampler cannot know which it is unless it is told.
        drole = role_for(section_id, counters[section_id] - 1)
        phrases.append(
            _make_slot(
                f"{section_id}_p{counters[section_id]}",
                section_id,
                bar,
                bars,
                fn,
                cad,
                slot_key,
                meter,
                tempo,
                style,
                dramatic_role=drole,
            )
        )
        bar += bars
    return phrases


def _build_ternary(
    key: str,
    tempo: int,
    meter: Tuple[int, int],
    style: StyleDNA,
    movement_id: str = "m1",
    bar_offset: int = 0,
) -> List[PhraseSlot]:
    """ABA' ternary with a retransition and a coda, and asymmetric phrases."""
    return _build_from_spec(_TERNARY_SPEC, key, tempo, meter, style, movement_id, bar_offset)


def _build_sonata(
    key: str,
    tempo: int,
    meter: Tuple[int, int],
    style: StyleDNA,
    movement_id: str = "m1",
    bar_offset: int = 0,
) -> List[PhraseSlot]:
    """A complete sonata-allegro: exposition, development, recapitulation, coda."""
    return _build_from_spec(_SONATA_SPEC, key, tempo, meter, style, movement_id, bar_offset)


def _build_binary(
    key: str,
    tempo: int,
    meter: Tuple[int, int],
    style: StyleDNA,
    movement_id: str = "m1",
    rounded: bool = False,
    bar_offset: int = 0,
) -> List[PhraseSlot]:
    """Binary or rounded binary, with the second key area chosen by mode.

    A major-key first half goes to the DOMINANT; a minor-key one goes to the
    RELATIVE MAJOR. That is not a stylistic preference — a minor-key dance that
    cadences in the minor dominant is the rarer choice, and getting it wrong
    puts the whole first half in the wrong key.
    """
    from .pitch import is_minor_key

    minor = is_minor_key(key)
    if rounded:
        spec = _ROUNDED_BINARY_SPEC_MINOR if minor else _ROUNDED_BINARY_SPEC_MAJOR
    else:
        spec = _BINARY_SPEC_MINOR if minor else _BINARY_SPEC_MAJOR
    return _build_from_spec(spec, key, tempo, meter, style, movement_id, bar_offset)


def _build_theme_variations(
    key: str,
    tempo: int,
    meter: Tuple[int, int],
    style: StyleDNA,
    movement_id: str = "m1",
    bar_offset: int = 0,
) -> List[PhraseSlot]:
    """Theme + four variations, each with its own key role, phrase rhythm and tempo.

    This alone among the builders never passed ``movement_id`` down, so a
    variations movement placed second in a work built ``m1_theme`` / ``m1_var1``
    section ids — colliding with movement I's namespace, which is the exact
    collision `_build_from_spec`'s prefix rewrite exists to prevent.
    """
    mid = str(movement_id or "m1")
    spec = [
        ("m1_theme", 4, _PF.PRESENTATION.value, _CT.HC.value, "tonic"),
        ("m1_theme", 4, _PF.CADENTIAL.value, _CT.PAC.value, "tonic"),
    ]
    phrases = _build_from_spec(spec, key, tempo, meter, style, mid, bar_offset)
    bar = max((p.bar_start + p.bar_count for p in phrases), default=1 + bar_offset)
    for i, character in enumerate(_VARIATION_CHARACTERS, start=1):
        section = f"{mid}_var{i}"
        var_key = _key_for_role(key, character["key_role"])
        var_tempo = max(30, int(round(tempo * character["tempo_scale"])))
        for j, (bars, fn, cad) in enumerate(
            (
                (character["bars"][0], _PF.RETURN_VARIED.value, _CT.HC.value),
                (character["bars"][1], _PF.CADENTIAL.value, _CT.PAC.value),
            ),
            start=1,
        ):
            slot = _make_slot(
                f"{section}_p{j}", section, bar, bars, fn, cad, var_key, meter, var_tempo, style
            )
            slot.notes = f"variation {i} — {character['label']}"
            phrases.append(slot)
            bar += bars
    return phrases


def _build_simple(
    key: str,
    tempo: int,
    meter: Tuple[int, int],
    form: str,
    style: StyleDNA,
    movement_id: str = "m1",
    bar_offset: int = 0,
) -> List[PhraseSlot]:
    """A short song-form default for unrecognized form names."""
    return _build_from_spec(_SIMPLE_SPEC, key, tempo, meter, style, movement_id, bar_offset)


def _make_slot(
    phrase_id: str,
    section_id: str,
    bar_start: int,
    bar_count: int,
    function: str,
    cadence: str,
    key: str,
    meter: Tuple[int, int],
    tempo: int,
    style: StyleDNA,
    dramatic_role: str = "",
) -> PhraseSlot:
    """Create a PhraseSlot with SUGGESTED harmony and texture plans.

    The harmony plan is a corpus-typical *default*, not a mandate: the agent
    chooses the actual harmony from what it learned studying the reference
    scores (the brief presents this plan as advisory). It also serves as the
    chord-frame for clash-avoidance and as input to the engine fallback when a
    phrase is left unauthored.
    """
    from .progression_model import corpus_harmony_plan

    composer_id = getattr(style, "composer_id", "") or ""
    target = getattr(style, "target", None)
    style_name = ""
    if isinstance(target, dict):
        style_name = target.get("genre") or target.get("era") or ""
    else:
        style_name = getattr(target, "genre", "") or getattr(style, "era", "") or ""
    from .pitch import is_minor_key
    from .progression_model import within_bar_detail

    harmony = corpus_harmony_plan(
        composer_id,
        style_name,
        cadence,
        bar_count,
        key,
        seed=bar_start,
        role=dramatic_role,
    ) or _default_harmony_plan(function, cadence, bar_count, minor=is_minor_key(key))

    # Where the harmony moves INSIDE each bar, from the composer's own within-bar
    # patterns. Without this the plan could only ever say one chord per bar.
    harmony_detail = within_bar_detail(
        composer_id,
        style_name,
        harmony,
        key,
        cadence,
        beats=int(bar_duration(meter)) if meter else 4,
        seed=bar_start,
    )

    texture_plan = _default_texture_plan(style, function, cadence, bar_count, meter, seed=bar_start)

    # Energy curve
    energy = _default_energy_curve(function, bar_count)

    return PhraseSlot(
        dramatic_role=dramatic_role,
        phrase_id=phrase_id,
        section_id=section_id,
        bar_start=bar_start,
        bar_count=bar_count,
        function=function,
        cadence_target=cadence,
        # A phrase that does not cadence has no cadence bar. Setting one anyway
        # made the density/texture plan thin at the end of EVERY phrase, which
        # put an audible comma in the music every four to six bars.
        cadence_bar=(
            bar_start + bar_count - 1 if cadence and cadence != CadenceTarget.NONE.value else None
        ),
        key=key,
        meter=meter,
        tempo_bpm=tempo,
        harmony_plan=harmony,
        harmony_detail=harmony_detail,
        texture_plan=texture_plan,
        curves=PhraseCurves(energy=energy),
    )


# How often the accompaniment changes character is a MEASURED property of the
# composer, not a policy. Two wrong answers have been shipped here: a round-robin
# (`options[i % len(options)]`) that planned a different idiom in every bar for no
# reason, and then a flat "hold one idiom for the whole phrase", which is just as
# wrong in the other direction — Mozart's own corpus changes left-hand texture on
# **62%** of bar transitions (measured over 402 bars of his 3/4 andantes), and his
# profile records lh_texture_change_pct ≈ 0.54. Holding one figure for six bars is
# the single most audible way generated music announces itself.
#
# So: take the rate from the composer's corpus profile, and take the SUCCESSOR
# from the corpus transition matrix — what that composer actually moves to next.
# Not accompaniment idioms a plan can schedule: silence is the absence of one,
# and "unclassified" is the extractor's junk bucket.
_UNSCHEDULABLE_LH = {"silence", "unclassified", ""}

_CADENCE_LH = {
    "alberti": "block_chord_sparse",
    "broken_chord_wave": "block_chord_sparse",
    "walking_bass": "block_chord_sparse",
    "block_chord_offbeat": "block_chord_sparse",
}


def _lh_change_rate(style) -> float:
    """The composer's own measured LH texture-change rate, or a neutral default."""
    from .composition_brief import corpus_profile

    composer = (getattr(style, "composer_id", "") or "").lower()
    prof = corpus_profile(composer) if composer else {}
    stat = (prof or {}).get("metrics", {}).get("lh_texture_change_pct") or {}
    mean = stat.get("mean")
    return float(mean) if isinstance(mean, (int, float)) and 0 < mean < 1 else 0.45


def _next_lh_texture(style, current: str, options: List[str], seed: int) -> str:
    """What this composer actually moves to after ``current``.

    This read ``trans["next"]`` — a key ``_transition_patterns`` has never
    returned. It returns ``after_previous.follow``. So the lookup was dead: the
    corpus transition matrix, built specifically to say what follows what, was
    never consulted, and the accompaniment simply cycled through the style's
    ranked textures by index.
    """
    from .composition_brief import _transition_patterns

    try:
        trans = _transition_patterns(getattr(style, "composer_id", "") or "", None, current)
        follow = ((trans or {}).get("after_previous") or {}).get("follow") or []
        ranked = [t for t, _w in follow if t != current and t not in _UNSCHEDULABLE_LH]
        if ranked:
            return ranked[seed % min(3, len(ranked))]
    except Exception:
        pass
    alt = [t for t in options if t != current and t not in _UNSCHEDULABLE_LH]
    return alt[seed % len(alt)] if alt else current


def _rh_change_rate(style) -> float:
    """The composer's own measured RH texture-change rate."""
    from .composition_brief import corpus_profile

    composer = (getattr(style, "composer_id", "") or "").lower()
    prof = corpus_profile(composer) if composer else {}
    stat = (prof or {}).get("metrics", {}).get("texture_change_pct") or {}
    mean = stat.get("mean")
    return float(mean) if isinstance(mean, (int, float)) and 0 < mean < 1 else 0.35


def _default_texture_plan(
    style, function: str, cadence: str, bar_count: int, meter, seed: int = 0
) -> List:
    """Plan the accompaniment's character bar by bar at the composer's own rate.

    Density targets scale with the bar's real beat count and the chosen texture
    rather than being the same hard-coded 8-RH / 6-LH for every bar of every
    piece in every meter.
    """

    def _ranked(dist, fallback, min_share: float = 0.05):
        """Textures this composer actually uses often, commonest first.

        The tail is dropped: rotating through the WHOLE ranked list reached
        idioms a composer uses in 1% of bars, so a tender andante's second phrase
        was planned as passage-work. Variety should stay inside the composer's
        mainstream vocabulary, not sample its extremes.
        """
        if not dist:
            return [fallback]
        ranked = sorted(dist.items(), key=lambda kv: -kv[1])
        total = sum(v for _, v in ranked) or 1.0
        keep = [k for k, v in ranked if (v / total) >= min_share]
        return keep or [ranked[0][0]] or [fallback]

    rh_opts = _ranked(getattr(style, "rh_distribution", None), TextureType.SINGING_MELODY.value)
    lh_opts = _ranked(getattr(style, "lh_distribution", None), AccompType.ALBERTI.value)
    # "silence" is a real corpus label (the staff rests for a bar) but it is not
    # something to PLAN as a phrase's accompaniment idiom — a phrase whose plan
    # opens on silence has no accompaniment at all. It was filtered out of the
    # successor choice and not out of the initial pick.
    rh_opts = [t for t in rh_opts if t not in _UNSCHEDULABLE_LH] or [
        TextureType.SINGING_MELODY.value
    ]
    lh_opts = [t for t in lh_opts if t not in _UNSCHEDULABLE_LH] or [AccompType.ALBERTI.value]
    # Every phrase used to START on the style's single most common texture and
    # accrue its changes from zero, so phrase 1 and phrase 9 of the same piece
    # were planned identically: alberti, alberti, then a change at the same bar
    # index, over and over. That IS the "same accompaniment throughout" tell the
    # brief warns about, planned in. Offsetting both the starting texture and the
    # accrual phase by where the phrase sits in the piece makes each phrase begin
    # somewhere the previous one did not, while still following the composer's
    # own distribution and change rate.
    offset = max(0, int(seed))
    # The opening states the norm — a piece should not begin on its composer's
    # fourth-commonest texture — and a RETURN should recall how the material
    # first sounded rather than arriving in a texture the listener has never
    # associated with it.
    anchored = offset <= 1 or (function or "").lower() in ("return", "recapitulation", "coda")
    step = 0 if anchored else (offset // 4)
    rh = rh_opts[step % len(rh_opts)]
    lh = lh_opts[step % len(lh_opts)]
    rate = _lh_change_rate(style)
    rh_rate_of_change = _rh_change_rate(style)

    beats = float(bar_duration(meter)) if meter else 4.0
    rh_rate = {
        "held_note": 0.35,
        "singing_melody": 1.2,
        "chordal": 1.0,
        "block_chord_sparse": 0.6,
        "scalar_run": 3.0,
        "zigzag_figuration": 3.0,
        "passage_work": 3.0,
        "dotted_pairs": 1.5,
        "dialogue": 1.2,
        "ornamental_cascade": 3.5,
    }
    lh_rate = {
        "silence": 0.0,
        "pedal_point": 0.4,
        "block_chord_sparse": 0.7,
        "block_chord_offbeat": 1.2,
        "bass_melody": 1.0,
        "walking_bass": 1.2,
        "alberti": 2.0,
        "broken_chord_wave": 2.0,
        "broken_chord_asc": 2.0,
        "broken_chord_desc": 2.0,
        "interlocking": 2.0,
        "block_chord_tremolo": 3.0,
        "sparse_punctuation": 0.6,
    }
    cadence_bar = bar_count - 1 if cadence and cadence != CadenceTarget.NONE.value else -1

    plan = []
    accrued = 0.0 if anchored else (offset * 0.37) % 1.0
    rh_accrued = 0.0 if anchored else (offset * 0.61) % 1.0
    for i in range(bar_count):
        is_cadence = i == cadence_bar
        if i and not is_cadence:
            # Deterministic pacing: change once the accumulated rate crosses 1,
            # which lands the phrase's change COUNT on the composer's own rate.
            accrued += rate
            if accrued >= 1.0:
                accrued -= 1.0
                lh = _next_lh_texture(style, lh, lh_opts, i + offset)
            # The UPPER staff was pinned to one texture for the whole phrase —
            # so every bar retrieved the same exemplars and got the same density
            # target, while the brief printed the composer's real
            # texture_change_pct right underneath as a target to hit. A phrase
            # cannot change texture 40% of the time if the plan says it never
            # changes at all.
            rh_accrued += rh_rate_of_change
            if rh_accrued >= 1.0 and len(rh_opts) > 1:
                rh_accrued -= 1.0
                alt = [t for t in rh_opts if t != rh]
                rh = alt[(i + offset) % len(alt)]
        bar_lh = _CADENCE_LH.get(lh, lh) if is_cadence else lh
        # Not every cadence is a held note. Alternating the two idiomatic
        # cadential upper-staff gestures stops every phrase in every piece from
        # ending the same way.
        bar_rh = rh
        if is_cadence and rh not in ("held_note", "chordal"):
            bar_rh = "chordal" if (bar_count % 2 == 0) else "held_note"
        plan.append(
            BarTexturePlan(
                rh_texture=bar_rh,
                lh_texture=bar_lh,
                rh_density_target=max(
                    1, round(beats * (0.4 if is_cadence else rh_rate.get(bar_rh, 1.2)))
                ),
                lh_density_target=max(
                    1, round(beats * (0.5 if is_cadence else lh_rate.get(bar_lh, 1.5)))
                ),
            )
        )
    return plan


def _default_harmony_plan(
    function: str, cadence: str, bar_count: int, minor: bool = False
) -> List[str]:
    """Fallback harmony plan when the corpus model has nothing for this composer.

    Built as opening + middle + CADENCE rather than by slicing a fixed 8-bar
    template: slicing dropped the dominant out of any phrase that was not
    exactly eight bars, so a six-bar phrase asked for a perfect cadence and got
    tonic-tonic. Mode-aware too — the old version handed a phrase in A minor an
    A MAJOR tonic and a major supertonic.
    """
    if bar_count <= 0:
        return []
    tonic = "i" if minor else "I"
    sub = "iv" if minor else "IV"
    supertonic = "iio6" if minor else "ii6"
    submediant = "VI" if minor else "vi"

    dom7 = "V" if minor else "V7"
    # EVADED and ELIDED had no entry, so they fell through to an empty tail and
    # the phrase ended wherever the functional walk happened to be — no dominant,
    # no arrival, nothing to evade.
    tails = {
        CadenceTarget.PAC.value: [dom7, tonic],
        CadenceTarget.IAC.value: ["V", tonic + "6"],
        CadenceTarget.HC.value: [supertonic, "V"],
        CadenceTarget.DC.value: [dom7, submediant],
        CadenceTarget.PLAGAL.value: [sub, tonic],
        CadenceTarget.EVADED.value: [dom7, tonic + "6"],
        CadenceTarget.ELIDED.value: [supertonic, tonic + "6"],
    }
    tail = tails.get(cadence, [])
    if bar_count <= len(tail):
        return tail[-bar_count:]

    # Middle: a functional walk out from the tonic and back to the predominant,
    # long enough to fill whatever is left once the cadence is reserved.
    walk = [tonic, submediant, sub, supertonic, tonic, sub]
    body = [tonic]
    i = 0
    while len(body) < bar_count - len(tail):
        body.append(walk[i % len(walk)])
        i += 1
    return body + tail


def _default_energy_curve(function: str, bar_count: int) -> List[float]:
    """Generate a default energy curve."""
    if function in (PhraseFunction.PRESENTATION.value, PhraseFunction.RETURN.value):
        # Gentle arch
        return [0.4 + 0.3 * (i / bar_count) for i in range(bar_count)]
    if function == PhraseFunction.CADENTIAL.value:
        # Build to peak then resolve
        peak = bar_count * 2 // 3
        return [
            0.5 + 0.3 * (i / peak) if i <= peak else 0.8 - 0.3 * ((i - peak) / (bar_count - peak))
            for i in range(bar_count)
        ]
    if function == PhraseFunction.CONTRASTING_THEME.value:
        # Gentle, lower energy
        return [0.3 + 0.2 * (i / bar_count) for i in range(bar_count)]
    return [0.5] * bar_count


def _sample_curve(curve: List[float], frac: float) -> Optional[float]:
    """Linear-sample a per-section curve list at fractional position frac∈[0,1]."""
    if not curve:
        return None
    if len(curve) == 1:
        return float(curve[0])
    frac = max(0.0, min(1.0, frac))
    x = frac * (len(curve) - 1)
    lo = int(x)
    hi = min(lo + 1, len(curve) - 1)
    t = x - lo
    return float(curve[lo] * (1 - t) + curve[hi] * t)


def _apply_narrative_curves(slot: PhraseSlot, narrative) -> bool:
    """Interpolate the covering NarrativeSection's curves into the slot's
    PhraseCurves, one value per bar — the keystone wiring that lets the planned
    emotional arc actually drive dynamics, density targets, and the tempo arc.

    Falls back silently (keeps the function-default energy curve) when no
    narrative exists or no section covers the slot. Returns True if it applied.
    """
    if narrative is None or not getattr(narrative, "sections", None):
        return False
    from .models import narrative_section_is_in_movement

    sections = narrative.sections
    _mid = (getattr(slot, "section_id", "") or "").split("_", 1)[0]
    energy, tension, density, brightness = [], [], [], []
    covered = False
    for i in range(slot.bar_count):
        gbar = slot.bar_start + i
        # Movement-aware: bar numbers restart per movement, so a bar range alone
        # matched the WRONG movement's section and mapped its energy, tension,
        # density and brightness onto this slot — the curves that drive dynamics,
        # density targets and the tempo arc.
        sec = next(
            (
                s
                for s in sections
                if s.bar_start <= gbar <= s.bar_end and narrative_section_is_in_movement(s, _mid)
            ),
            None,
        )
        prev_e = slot.curves.energy[i] if i < len(slot.curves.energy) else 0.5
        if sec is None:
            energy.append(prev_e)
            tension.append(0.5)
            density.append(0.5)
            brightness.append(0.5)
            continue
        covered = True
        span = max(1, sec.bar_end - sec.bar_start)
        frac = (gbar - sec.bar_start) / span
        e = _sample_curve(sec.energy_curve, frac)
        energy.append(e if e is not None else prev_e)
        tension.append(_sample_curve(sec.tension_curve, frac) or 0.5)
        density.append(_sample_curve(sec.density_curve, frac) or 0.5)
        brightness.append(_sample_curve(sec.brightness_curve, frac) or 0.5)
    if not covered:
        return False
    # Only override the default energy when the narrative actually supplied it.
    if any(s.energy_curve for s in sections):
        slot.curves.energy = energy
    slot.curves.tension = tension
    slot.curves.density = density
    slot.curves.brightness = brightness

    # Drive note density per bar from the narrative density curve (not just
    # dynamics) — low density → sparser/sustained texture, high → fuller/running.
    for i, bt in enumerate(getattr(slot, "texture_plan", []) or []):
        d = density[i] if i < len(density) else 0.5
        bt.rh_density_target = int(round(4 + 12 * d))
        bt.lh_density_target = int(round(3 + 7 * d))
    return True


def _parse_key_str(key: str):
    """Delegates to the single canonical parser (pitch.parse_key)."""
    from .pitch import parse_key

    return parse_key(key)


def _key_name(key_obj) -> str:
    """Render a music21 Key back to the project's canonical "<Tonic> <mode>" form."""
    tonic = key_obj.tonic.name.replace("-", "b")
    return f"{tonic} {key_obj.mode}"


def _transpose_key(key: str, interval_name: str, mode: Optional[str] = None) -> str:
    """Transpose a key by a NAMED interval, optionally switching mode.

    Replaces two hard-coded lookup tables that silently returned "C"/"Am"/"G"
    for any key spelling they did not contain — which was ALL of them once the
    planner started writing "a minor" instead of "Am", so every ternary B
    section and every sonata secondary theme landed in the wrong key.

    The interval is named ("P5", "m3") rather than a semitone count so the
    spelling stays diatonic: the dominant of D-flat is A-flat, not G-sharp.
    """
    import music21

    k = _parse_key_str(key)
    new_tonic = k.tonic.transpose(music21.interval.Interval(interval_name))
    return _key_name(music21.key.Key(new_tonic.name, mode or k.mode))


def _relative_key(key: str) -> str:
    """The relative major of a minor key, or the relative minor of a major key."""
    k = _parse_key_str(key)
    if k.mode == "minor":
        return _transpose_key(key, "m3", "major")
    return _transpose_key(key, "-m3", "minor")


def _dominant_key(key: str) -> str:
    """The key a sonata exposition's secondary theme goes to.

    Major: the dominant. Minor: the RELATIVE MAJOR — a minor-mode exposition
    that modulates to the minor dominant is the exception, not the rule, and the
    old table did exactly that for every minor key.
    """
    k = _parse_key_str(key)
    if k.mode == "minor":
        return _relative_key(key)
    return _transpose_key(key, "P5")


def _subdominant_key(key: str) -> str:
    return _transpose_key(key, "P4")


def _parallel_key(key: str) -> str:
    k = _parse_key_str(key)
    return _transpose_key(key, "P1", "major" if k.mode == "minor" else "minor")


def _infer_section_role(section_id: str) -> str:
    """Infer section role from its ID naming convention."""
    sid = section_id.lower()
    if "pt" in sid or "expo" in sid:
        return "exposition"
    if "dev" in sid:
        return "development"
    if "recap" in sid:
        return "recapitulation"
    if "coda" in sid:
        return "coda"
    if "_a" in sid and "_a2" not in sid:
        return "A"
    if "_b" in sid:
        return "B"
    if "_a2" in sid or "return" in sid:
        return "A_return"
    if "tr" in sid:
        return "transition"
    if "st" in sid:
        return "secondary_theme"
    if "cl" in sid:
        return "closing"
    return "A"


# ─── Work-Level Planning (multi-movement) ──────────────────────────────────


@_tool
def init_work(
    piece_id: str,
    movement_count: int,
    description: str = "",
    emotional_narrative: str = "",
    finale_payoff: str = "",
) -> Dict[str, Any]:
    """Create a WorkGraph for multi-movement works.

    This is WHERE Wolfgang decides the symphony's dramatic destiny.

    ``description`` is NOT STORED: `WorkGraph` has no such field, so it was
    accepted and dropped. The piece's description belongs to `init_workspace`,
    which puts it on the contract — and `_creative_intent` reads it from there
    when no narrative prose was authored. Supplying it here now says so rather
    than swallowing it.

    ``movement_count`` is declared `int` and was never checked. Calling this the
    way every other tool here is called — `init_work(pid, "compose_from_text")`,
    with the MODE in the second position, which is what `init_workspace` takes —
    stored the string "compose_from_text" as the movement count and reported it
    back in the result without complaint. A count is a number or the caller has
    made a mistake worth naming.
    """
    try:
        movement_count = int(movement_count)
    except (TypeError, ValueError):
        return {
            "error": (
                f"'{piece_id}': movement_count must be a number, got "
                f"{movement_count!r}. init_work(piece_id, movement_count, ...) — "
                f"note the second argument is the COUNT, not the mode; the mode "
                f"belongs to init_workspace(piece_id, mode, ...)."
            )
        }
    if movement_count < 1:
        return {"error": f"'{piece_id}': movement_count must be at least 1, got {movement_count}"}
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    if (description or "").strip():
        _LOG.warning(
            "init_work(description=...) is not stored — WorkGraph has no description "
            "field. The piece description belongs on init_workspace(description=...), "
            "which is where the brief reads it from. Nothing was lost silently; "
            "the work's dramatic material goes in emotional_narrative/finale_payoff."
        )

    from .models import TonalItinerary

    # Handle contract possibly being a dict (from JSON deserialization)
    # The home key of a multi-movement work came from
    # `target.instrumentation` — the wrong attribute entirely, so a piano work's
    # tonal itinerary recorded a home key of "solo_piano". Take it from the
    # music: the key of the first phrase that exists, and only then a default.
    home_key = "C"
    slots = sorted(
        (ps.slot for ps in graph.phrases.values() if getattr(ps, "slot", None)),
        key=lambda sl: getattr(sl, "bar_start", 0),
    )
    for slot in slots:
        if getattr(slot, "key", None):
            home_key = slot.key
            break
    work = WorkGraph(
        work_id=piece_id,
        movement_count=movement_count,
        emotional_narrative=emotional_narrative,
        finale_payoff=finale_payoff,
        tonal_itinerary=TonalItinerary(home_key=home_key),
    )
    graph.work_graph = work
    graph.save(str(workspace / "piece_graph.json"))

    # What a WorkGraph DECLARES and what anything actually fills are different
    # lists, and the docstring above ("where Wolfgang decides the symphony's
    # dramatic destiny") reads like the first. Nothing in the codebase writes
    # `theme_families`, `climax_reservations`, `cross_movement_recalls`,
    # `orchestral_macro_arc` or `cyclic_obligations` — five declared structures,
    # 24 fields, never populated by any path. Saying so is not a fix; letting the
    # data model imply a capability it does not have is the same defect as a
    # parameter that is accepted and discarded.
    unplanned = [
        name
        for name in (
            "theme_families",
            "climax_reservations",
            "cross_movement_recalls",
            "orchestral_macro_arc",
            "cyclic_obligations",
        )
        if not getattr(work, name, None)
    ]
    return {
        "work_id": piece_id,
        "movement_count": movement_count,
        "emotional_narrative": emotional_narrative,
        # Empty because nothing fills them yet — not because this work has none.
        "declared_but_not_planned": unplanned,
        "note": (
            "Cross-movement structure is DECLARED on WorkGraph and not yet "
            "populated by any tool: " + ", ".join(unplanned) + ". Plan recalls and "
            "theme families in the movement narratives until these are implemented."
            if unplanned
            else ""
        ),
    }


@_tool
def plan_movement(
    piece_id: str,
    movement_id: str,
    form: str,
    key: str,
    tempo_bpm: int = 120,
    meter: Tuple[int, int] = (4, 4),
    character: str = "",
    role_in_work: str = "",
    tempo_marking: str = "",
) -> Dict[str, Any]:
    """Add a MovementContract to the WorkGraph."""
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    if not graph.work_graph:
        return {"error": "No WorkGraph found — call init_work first"}

    movement = MovementContract(
        id=movement_id,
        form=form,
        key=key,
        tempo_bpm=tempo_bpm,
        meter=meter,
        tempo_marking=tempo_marking,
        character=character,
        role_in_work=role_in_work,
    )
    # REPLACE, never append. Planning a movement twice — which is what revising
    # one looks like, and what happens the moment a call is corrected and rerun —
    # used to leave two contracts with the same id. The work then reported
    # `['m1', 'm2', 'm1']`, and every brief in the piece opened with
    # "MOVEMENT 1 of 3" for a two-movement sonatina, because the count is the
    # length of that list.
    existing = next(
        (i for i, m in enumerate(graph.work_graph.movements) if m.id == movement_id), None
    )
    if existing is None:
        graph.work_graph.movements.append(movement)
    else:
        graph.work_graph.movements[existing] = movement
    # Heal a list that was already duplicated by an earlier run: keep the FIRST
    # position of each id (score order) and the LAST contract written for it.
    # Without this the fix only stops new duplicates and every existing work
    # keeps counting its movements wrong.
    seen: Dict[str, int] = {}
    deduped: List[Any] = []
    for m in graph.work_graph.movements:
        if m.id in seen:
            deduped[seen[m.id]] = m
        else:
            seen[m.id] = len(deduped)
            deduped.append(m)
    graph.work_graph.movements = deduped
    graph.work_graph.tonal_itinerary.movement_keys[movement_id] = key
    # The work's home key is the FIRST movement's key. `init_work` runs before
    # any movement or phrase exists, so it can only default — a three-movement
    # sonatina in G major recorded a home key of "C", and every later question
    # about where the work lives got the wrong answer.
    if len(graph.work_graph.movements) == 1 and key:
        graph.work_graph.tonal_itinerary.home_key = key
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "movement_id": movement_id,
        "form": form,
        "key": key,
        "character": character,
        # This registers the movement's CONTRACT and creates no phrases, even
        # though it takes `form`, `key`, `tempo_bpm` and `meter` — every argument
        # `build_form_graph` needs. A caller who stops here has a work with two
        # planned movements and nothing to compose, and the old return said
        # nothing about it. Same shape as `init_work(description=...)` above:
        # a tool that quietly does less than its arguments imply.
        "phrases_created": 0,
        "next": (
            f"build_form_graph(piece_id, {form!r}, {key!r}, "
            f"tempo_bpm={tempo_bpm}, meter={tuple(meter)}, "
            f"movement_id={movement_id!r}) — this call only records the contract"
        ),
    }


# ─── Revision Support ──────────────────────────────────────────────────────


@_tool
def apply_revision(piece_id: str, section_id: str, revision_ops: List[Dict]) -> Dict[str, Any]:
    """Apply a RevisionScript to a section using the PatchEngine.

    Each op is a dict with: target_phrase, operation, params, reason.
    """
    revision_ops = _as_list(revision_ops, "revision_ops")
    from .models import RevisionOp, RevisionScript
    from .patch_engine import PatchEngine

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)

    ops = [
        RevisionOp(
            target_phrase=op.get("target_phrase", ""),
            target_layer=op.get("target_layer"),
            target_bars=tuple(op["target_bars"]) if op.get("target_bars") else None,
            operation=op.get("operation", ""),
            params=op.get("params", {}),
            reason=op.get("reason", ""),
        )
        for op in revision_ops
    ]
    script = RevisionScript(section_id=section_id, ops=ops)

    engine = PatchEngine()
    phrase_order = graph.get_section_phrases(section_id)
    # A revision that silently applies to nothing looks exactly like one that
    # worked: the result carried an empty `affected_phrases` and no error, so a
    # mistyped section or phrase id read as "the critic's fix landed". Every op
    # names a target and every target has to exist.
    if not phrase_order:
        return {
            "error": f"Unknown section '{section_id}' in '{piece_id}'",
            "sections": sorted({ps.slot.section_id for ps in graph.phrases.values() if ps.slot}),
        }
    unknown = sorted(
        {
            op.target_phrase
            for op in ops
            if op.target_phrase and op.target_phrase not in graph.phrases
        }
    )
    if unknown:
        return {
            "error": f"Unknown target phrase(s): {', '.join(unknown)}",
            "phrases_in_section": phrase_order,
        }
    unknown_ops = sorted({op.operation for op in ops if op.operation not in _REVISION_OPS})
    if unknown_ops:
        return {
            "error": f"Unknown revision operation(s): {', '.join(unknown_ops)}",
            "operations": sorted(_REVISION_OPS),
        }
    # Each operation reads ONE specific param key, and reads it with `.get`. A
    # script that says `semitones` where the engine reads `interval`, or
    # `texture` where it reads `lh_texture`, therefore applies cleanly, changes
    # nothing, and reports ops_applied. The reviewer is told its revision landed
    # and the music is identical. Names it is, then — a critic writing one of
    # these has no way to know the key but to be told.
    bad_params = []
    for op in ops:
        required = _REVISION_OP_PARAMS.get(op.operation)
        if required and not any(k in (op.params or {}) for k in required):
            got = sorted(op.params or {}) or ["nothing"]
            bad_params.append(
                f"{op.operation} on {op.target_phrase or '?'} needs "
                f"{' or '.join(required)}, got {', '.join(got)}"
            )
    if bad_params:
        return {
            "error": "revision operation(s) missing the parameter they read: "
            + "; ".join(bad_params),
            "op_parameters": {k: sorted(v) for k, v in _REVISION_OP_PARAMS.items()},
        }

    affected = engine.identify_affected_phrases(script, phrase_order)
    applied = 0
    for op in ops:
        if op.target_phrase and op.target_phrase in graph.phrases:
            graph.phrases[op.target_phrase] = engine.apply_revision_op(
                op, graph.phrases[op.target_phrase]
            )
            applied += 1

    warnings = engine.validate_edit_coherence(affected, phrase_order)
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "ops_applied": applied,
        "affected_phrases": affected,
        "warnings": warnings,
        "needs_recomposition": [
            pid
            for pid in affected
            if graph.phrases.get(pid) and graph.phrases[pid].status in ("planned", "sketched")
        ],
    }


# ─── Engraver's pass ─────────────────────────────────────────────────────────


def _engrave_phrase(graph, phrase_id: str, layer: LayerIR, composer: Optional[str]):
    """Run the engraver's pass over a phrase the agent just wrote.

    `expression_enricher` existed, was fully tested, and was called by nothing.
    Every score the system produced therefore came out with **zero
    articulations and zero ties** where a real Mozart sonata movement carries
    0.27-1.74 articulations and up to 0.89 ties per bar (measured over the nine
    first movements in `reference_scores/mozart-piano-sonatas`). An
    unarticulated score sounds like a MIDI file because it is one.

    The pass is strictly non-destructive: it writes only fields the composer
    left blank, so the agent stays the author and this is the engraver who
    follows it. The report is stored on the phrase so a reviewer can tell the
    two apart.
    """
    from .expression_enricher import enrich_layer_ir, expression_density

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None

    style_name = composer or getattr(graph.style_dna, "composer_id", "") or ""
    curves = getattr(slot, "curves", None) if slot else None
    energy = list(getattr(curves, "energy", []) or []) if curves else None
    harmony = list(getattr(slot, "harmony_plan", []) or []) if slot else None
    cadence_bar = getattr(slot, "cadence_bar", None) if slot else None
    character = (getattr(slot, "notes", "") or "") if slot else ""
    # The dynamic the previous phrase ended on, so the engraver does not restate
    # a level the music is already at. This read `slot.continuation.last_dynamic`
    # — a field of a dataclass nothing has ever written — so it was always None.
    base_dyn = None
    try:
        from .composition_brief import _transition_context

        base_dyn = ((_transition_context(graph, phrase_id) or {}).get("continuation") or {}).get(
            "last_dynamic"
        )
    except Exception:
        base_dyn = None

    try:
        report = enrich_layer_ir(
            layer,
            style=style_name,
            energy_curve=energy,
            harmony_plan=harmony,
            cadence_bar=cadence_bar,
            base_dynamic=base_dyn,
            character=character,
            is_final_phrase=_is_final_phrase(graph, phrase_id),
        )
    except Exception as exc:  # never let the engraver block a good commit
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    out = report.as_dict()
    out["density_after"] = expression_density(layer)
    return out


def _is_final_phrase(graph, phrase_id: str) -> bool:
    """True when no later phrase exists anywhere in the piece."""
    order = list(graph.phrases.keys())
    try:
        return order.index(phrase_id) == len(order) - 1
    except ValueError:
        return False


def _gated_commit(
    graph,
    workspace: Path,
    phrase_id: str,
    layer: LayerIR,
    allow: Optional[List[Dict[str, str]]],
    composer: Optional[str],
) -> Dict[str, Any]:
    """Shared gate + commit path for both agent commit entry points.

    Enforces (in order): the brief receipt (a phrase cannot be committed unless
    its brief was fetched), then the blocking quality gate (density, figuration,
    corpus alignment). Both are hard — there is no gate-bypass flag."""
    from .commit_gate import run_commit_gate
    from .models import RevisionEntry

    # 1. Brief receipt requirement — never compose blind without a brief.
    state = graph.phrases.get(phrase_id)
    trace = getattr(state, "context_trace", None) if state else None
    trace = trace if isinstance(trace, dict) else {}
    waived = {
        str(w.get("check", "")).strip()
        for w in (allow or [])
        if str(w.get("check", "")).strip() and str(w.get("reason", "")).strip()
    }
    if not trace.get("brief_fetched"):
        return {
            "ok": False,
            "error": "brief_not_fetched",
            "hint": (
                "Call get_composition_brief(piece_id, phrase_id) for this "
                "phrase BEFORE composing. The brief's real corpus exemplars "
                "are mandatory — the commit gate will not accept a surface "
                "composed without one."
            ),
        }
    if trace.get("brief_insufficient") and "brief_insufficient" not in waived:
        return {
            "ok": False,
            "error": "brief_insufficient",
            "hint": (
                "The corpus yielded NO exemplars for this phrase, so the "
                "brief cannot anchor the writing. Arm the composer with "
                "real scores (tools/scripts/acquire_composer.py <composer>) "
                "and re-fetch the brief, or — if composing without corpus "
                "support is a deliberate choice — recommit with "
                "allow=[{'check': 'brief_insufficient', 'reason': '...'}]."
            ),
        }

    # 2a. The tempo has to be a speed a player can take. `min_tempo_bpm` and
    #     `max_tempo_bpm` have sat on PhysicalConstraints unread since the model
    #     was written.
    tempo_notes: List[str] = []
    try:
        from .validator import validate_tempo

        slot_for_tempo = getattr(state, "slot", None)
        if slot_for_tempo is not None:
            tempo_notes = [
                i.message
                for i in validate_tempo(
                    getattr(slot_for_tempo, "tempo_bpm", None),
                    getattr(graph.contract, "constraints", None),
                )
            ]
    except Exception:
        tempo_notes = []

    # 2. Blocking quality gate (density, figuration, corpus alignment, meter).
    gate = run_commit_gate(graph, phrase_id, layer, allow=allow, composer=composer)
    if not gate.passed:
        return {
            "ok": False,
            "error": "quality_gate_blocked",
            "blocking": [d.to_dict() for d in gate.blocking],
            "warnings": [d.to_dict() for d in gate.warnings],
            "rejected_waivers": gate.rejected_waivers,
            "hint": (
                "Revise the flagged bars and recommit, or — if the "
                "choice is genuinely intentional — recommit with "
                "allow=[{'check': '<name>', 'reason': '<musical "
                "justification>'}]. Physical constraints cannot "
                "be waived."
            ),
        }

    # 3. Engraver's pass — fill in the marks the composer left blank.
    #    Non-destructive; only blank fields are written.
    engraving = _engrave_phrase(graph, phrase_id, layer, composer)

    graph.commit_agent_phrase(phrase_id, layer)

    # 4. Craft checklist. This ran only inside `run_scales_section` — the ENGINE
    #    FALLBACK path — so it never saw a single agent-authored phrase, which
    #    is the path every piece actually takes. The checks ask the questions a
    #    composer asks of their own bar (does the melody make a claim, does the
    #    rhythm have an identity, does the bass have a purpose, does the phrase
    #    breathe, is there one detail worth remembering) and they are advisory:
    #    a phrase may fail one deliberately.
    craft = _craft_check_phrase(graph, phrase_id, layer)

    # 5. Hand the next phrase what it needs to continue from this one.
    _record_continuation(graph, phrase_id)

    # Capture the piece's principal theme from the first phrase whose dramatic
    # role is to state it. The theme machinery was entirely inert on the default
    # path: `motif_bank` is empty at plan time so no theme was ever elected, and
    # `capture_theme_surface` was called only by one optional workflow — so every
    # later phrase's brief had no theme to develop and a piece came out as N
    # independently-composed phrases with nothing binding them.
    _capture_theme_if_first_statement(graph, phrase_id)
    _settle_expectations(graph, phrase_id)

    # Overrides are auditable: every waived check lands in the history
    for ov in gate.overrides:
        graph.revision_history.append(
            RevisionEntry(
                timestamp=_now_iso(),
                skill="commit_gate",
                path=f"phrases.{phrase_id}",
                operation=f"override:{ov['check']}",
                reason=ov.get("reason", ""),
            )
        )

    graph.save(str(workspace / "piece_graph.json"))
    out: Dict[str, Any] = {"ok": True, "phrase_id": phrase_id, "agent_authored": True}
    out["gate"] = {
        "warnings": [d.to_dict() for d in gate.warnings],
        "overrides": gate.overrides,
        "rejected_waivers": gate.rejected_waivers,
    }
    out["engraving"] = engraving
    if craft:
        out["craft"] = craft
    if tempo_notes:
        out["tempo"] = tempo_notes
    return out


def _settle_expectations(graph, phrase_id: str) -> None:
    """Close the obligations this phrase discharges, on commit.

    The ledger had a ``satisfy`` method on both implementations and NOTHING in
    the project ever called it. Expectations were recorded at plan time and never
    resolved, so every debt stayed open for the whole piece and the brief's
    ledger section only ever grew — which is not a working memory, it is a list
    that gets longer. A composer told to resolve a cadence it already resolved
    four phrases ago learns to ignore the section.

    A section's cadence debt is discharged by the LAST phrase of that section
    (that is where its cadence lands); a theme-return promise by the first
    committed phrase of a section whose role is a return.
    """
    from .cross_scale_ledger import ensure_ledger, persist_ledger

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    if slot is None:
        return
    section_id = slot.section_id or ""
    order = graph.get_section_phrases(section_id) or []
    is_last_of_section = bool(order) and order[-1] == phrase_id
    role = _infer_section_role(section_id).lower()
    is_return = any(k in role for k in ("recap", "rec_", "a2", "return", "reprise"))

    try:
        ledger = ensure_ledger(graph)
    except Exception:
        return
    settled = False
    for exp in list(getattr(ledger, "expectations", []) or []):
        if getattr(exp, "status", "") != "open":
            continue
        ref = str(getattr(exp, "object_ref", "") or "")
        if is_last_of_section and ref == f"cadence_resolution_{section_id}":
            settled |= bool(ledger.satisfy(exp.id, phrase_id))
        elif is_return and ref.startswith("theme_recap_after_"):
            settled |= bool(ledger.satisfy(exp.id, phrase_id))
    if settled:
        persist_ledger(graph, ledger)


def _record_continuation(graph, phrase_id: str) -> None:
    """Hand the NEXT phrase what it needs to continue from this one.

    `ContinuationContext` declares thirteen fields and **nothing anywhere in the
    system ever set one**, so every phrase slot carried the default and every
    consumer of the model field — the engraver's opening dynamic among them —
    read None.

    The facts themselves come from `composition_brief._derive_continuation`,
    which is the one implementation: the brief derives the same thing on read
    (robust for graphs written before this existed), and a second copy here
    would be a second answer to the same question, which is how this project
    ends up with two of everything.
    """
    from .composition_brief import _derive_continuation
    from .models import ContinuationContext

    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    if slot is None or getattr(state, "realized", None) is None:
        return
    here = slot.bar_start or 0
    following = [
        (ps.slot.bar_start, ps)
        for ps in graph.phrases.values()
        if ps.slot and (ps.slot.bar_start or 0) > here
    ]
    if not following:
        return
    nxt = min(following, key=lambda t: t[0])[1]

    facts = _derive_continuation(graph, phrase_id) or {}
    if not facts:
        return
    known = {f.name for f in _dataclass_fields(ContinuationContext)}
    nxt.slot.continuation = ContinuationContext(**{k: v for k, v in facts.items() if k in known})


def _craft_check_phrase(graph, phrase_id: str, layer: LayerIR) -> Optional[Dict[str, Any]]:
    """Run the craft checklist over a just-committed agent surface.

    Returns the failed checks with what each one is asking, or None when the
    phrase satisfies all of them. Advisory: a phrase may fail one on purpose
    (a deliberately static bass under a moving melody, a phrase with no rest
    because it elides into the next).
    """
    from .craft_checker import CraftChecker

    state = graph.phrases.get(phrase_id)
    if state is None:
        return None
    try:
        result = CraftChecker().check(
            layer,
            control=getattr(state, "control", None),
            bundles=getattr(state, "onset_bundles", None),
        )
    except Exception as exc:  # a checklist must never block a good commit
        return {"error": f"{type(exc).__name__}: {exc}"}
    state.craft_check = result

    asks = {
        "melodic_claim_clear": "the melody makes a claim rather than filling time",
        "rhythm_has_identity": "the rhythm is a shape, not an even stream",
        "bass_has_purpose": "the bass is a line, not a series of roots",
        "harmony_is_voiced": "the harmony is voiced, not implied",
        "has_breath_point": "the phrase breathes somewhere",
        "accompaniment_responds_to_melody": "the accompaniment answers the melody",
        "entry_exit_earned": "the phrase's entry and exit are prepared",
        "has_memorable_detail": "one detail is worth remembering",
        "all_notes_justified": "every note has a reason",
    }
    failed = [
        {"check": name, "asks": text}
        for name, text in asks.items()
        if getattr(result, name, True) is False
    ]
    return (
        {"failed": failed, "passed": len(asks) - len(failed), "of": len(asks)} if failed else None
    )


def slot_meter_for(graph, phrase_id: str) -> Tuple[int, int]:
    """The meter a phrase is written in (4/4 when the slot does not say)."""
    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    meter = getattr(slot, "meter", None) if slot else None
    return tuple(meter) if meter else (4, 4)


# The finest grid every notatable duration lands on exactly. The denominators in
# DURATION_VALUES are 1,2,3,4,5,6,7,8,12,16 and their LCM is 1680, so a position
# snapped here can always be bracketed.
#
# This started at 48, which covers triplets (16/48), sextuplets (8/48), 32nds
# (6/48) and 64ths (3/48) — and silently rounds every QUINTUPLET and SEPTUPLET,
# because 5 and 7 do not divide 48. A five-note quintuplet came out drifting by
# up to a 120th of a beat per note and no longer summed to its own beat. That is
# the same failure as the 16th-note grid that once destroyed every triplet in
# this system, so the invariant is asserted rather than trusted.
_POSITION_GRID = 1680

# Subdivisions of the beat, coarsest first, restricted to divisors of
# _POSITION_GRID so every result is exactly notatable. A position is explained
# by the SIMPLEST subdivision it lands on, which is why the order is by size:
# 1/7 is reached before any fine binary grid (a 48th is within tolerance of a
# septuplet and would otherwise swallow it), while a drifted 0.56 passes every
# coarse candidate and resolves at a sixteenth.
_SUBDIVISIONS = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 16, 20, 21, 24, 28, 30, 35, 40, 42, 48)
# How far a stored onset may sit from a subdivision and still be read as it.
# A 256th of a beat is far below anything anyone writes and far above float
# noise or a value rounded to four decimals.
_GRID_TOLERANCE = _F(1, 256)


def _contract_instrumentation(graph) -> str:
    """The piece's own forces, for code that builds a LayerIR from scratch.

    Six sites hardcoded `"solo_piano"`, so the forces could be inferred
    perfectly from the request and still never reach the checks that consult
    them. Every reader was correct and all of them were wrong, because the value
    was never set at the source.
    """
    target = getattr(getattr(graph, "contract", None), "target", None)
    if isinstance(target, dict):
        return str(target.get("instrumentation") or "solo_piano")
    return str(getattr(target, "instrumentation", "") or "solo_piano")


def _repair_engine_surface(
    layer, meter: Tuple[int, int], allow_chords: bool = True
) -> Dict[str, int]:
    """Make an engine-realized surface notatable and meter-legal.

    Three mechanical repairs, in order, each counted so the caller can report
    what was wrong rather than hiding it:

    1. **Snap every onset to the notatable grid.** A float beat cursor that
       accumulated float durations and was then rounded produced positions like
       1.56 and 2.06, which are on no grid and which the engraver has to guess at.
    2. **Truncate a note that is still sounding when its own voice re-attacks.**
       One voice cannot play two notes at once; the earlier note ends where the
       next begins.
    3. **Deal with what runs past the barline.** A bar holding 4.875 beats of a
       4/4 cannot be engraved; the overflow is the engine's error, not music. A
       note STARTING past the barline is dropped (`overflow_dropped`); one that
       merely runs over the end is shortened to fit (`overflow_clamped`). Those
       are different reports — the first loses music, the second does not — and
       reporting both as "dropped" said three notes had been lost from a phrase
       where none had.

    This is a repair, not a rescue: it makes a malformed surface legal, and the
    counts it returns are the signal that the generator upstream needs fixing.
    """
    from fractions import Fraction

    from .duration import bar_duration, dur_to_beats, is_grace

    capacity = bar_duration(meter)
    counts = {
        "snapped": 0,
        "duplicates_removed": 0,
        # FIVE different things used to report as `overlaps_trimmed`, and the
        # reader could not tell a harmless discard from a lost note. A rest
        # sharing a note's onset is generator noise the repair absorbs
        # completely; two simultaneous notes in one orchestral part means a note
        # the composer wrote is GONE. "overlaps_trimmed: 1" was the report for
        # both. Same shape as the `duplicates_removed` split above it: a counter
        # that merges opposite diagnoses hides the one that matters.
        "overlaps_trimmed": 0,
        "rest_over_note_dropped": 0,
        "simultaneous_notes_dropped": 0,
        "second_chord_dropped": 0,
        "chord_note_length_unified": 0,
        "overflow_clamped": 0,
        "overflow_dropped": 0,
    }

    def _binary_at_most(beats) -> str:
        """The longest DOTTED-OR-PLAIN binary value no longer than `beats`."""
        from .duration import DURATION_VALUES

        want = Fraction(beats)
        best_code, best = "x", Fraction(0)
        for code, value in DURATION_VALUES.items():
            value = Fraction(value)
            if _tuplet_family(value):
                continue
            if best < value <= want:
                best_code, best = code, value
        return best_code

    def _tuplet_family(value: Fraction) -> frozenset:
        """The odd primes in a denominator — the tuplet family it belongs to.

        A binary value is `frozenset()`; a triplet is `{3}`; a quintuplet `{5}`;
        a septuplet `{7}`.
        """
        d = value.denominator
        out = set()
        for prime in (3, 5, 7):
            while d % prime == 0:
                out.add(prime)
                d //= prime
        return frozenset(out)

    def _on_grid(beat, duration=None) -> Fraction:
        """The SIMPLEST subdivision that explains this position.

        Two failures to avoid at once. A coarse grid (1/48) repairs float drift
        but silently rounds every quintuplet and septuplet, because 5 and 7 do
        not divide 48. A fine grid (1/1680, the LCM of every denominator in the
        duration table) preserves those exactly — and stops repairing drift,
        because 1.56 is already on it, so a smeared onset stays smeared.

        So: walk the subdivisions in order of musical plausibility (binary,
        then ternary, then quintuplet and septuplet) and take the first that
        explains the position to within a 256th of a beat. 1.56 resolves to
        1.5625 at a sixteenth; a quintuplet's 1.2 is nowhere near any binary or
        ternary position and resolves exactly at a fifth. Nothing plausible ⇒
        fall back to the finest grid, which is exact for anything notatable.

        A POSITION AND ITS DURATION MUST SHARE A GRID. A 64th note sitting on a
        septuplet position is not a septuplet — it is a drifted onset that
        happened to land within a 256th of one, and the subdivision walk was
        explaining it as genuine. The bar could then never tile: a note at
        39/28 lasting 1/16 leaves a remainder no notatable value fills, music21
        padded it with rests of 3/80 and 1/56, and the exported measure held
        85/56 of a 3/8 bar. Four bars in every 3/8 piece, and the only witness
        was a MusicXML warning during read-back.

        So a tuplet subdivision is only allowed to explain a position when the
        note's own duration comes from that tuplet family, and a binary note
        that explains nowhere falls back to a binary grid rather than to
        1/1680, which is itself divisible by 3, 5 and 7.
        """
        offset = Fraction(beat) - 1
        allowed = None
        if duration is not None:
            try:
                allowed = _tuplet_family(Fraction(dur_to_beats(duration)))
            except (TypeError, ValueError, ZeroDivisionError):
                allowed = None
        for denom in _SUBDIVISIONS:
            if allowed is not None and not _tuplet_family(Fraction(1, denom)) <= allowed:
                continue
            candidate = Fraction(round(offset * denom), denom)
            if abs(candidate - offset) <= _GRID_TOLERANCE:
                return max(Fraction(1), candidate + 1)
        grid = 16 if allowed is not None and not allowed else _POSITION_GRID
        return max(Fraction(1), Fraction(round(offset * grid), grid) + 1)

    for events in _all_event_lists(layer):
        for e in events:
            exact = _on_grid(e.beat, e.duration)
            # Count a snap only when the note actually MOVED. Comparing the
            # resolved fraction to `Fraction(e.beat)` compares it to the exact
            # binary expansion of a float, which for any tuplet is never equal:
            # 7/6 cannot be written as a float, so every triplet onset counted
            # as drift repaired. That reported `snapped: 6` on a phrase whose
            # onsets were all already exact to within 1e-6 — a clean surface
            # described as needing six repairs.
            if abs(float(exact) - float(e.beat)) > 1e-6:
                counts["snapped"] += 1
            e.beat = round(float(exact), 6)

            # AN ISOLATED TUPLET CANNOT TILE A BAR.
            #
            # A quintuplet quarter (2/5) starting on a sixteenth ends at 37/80,
            # which is a position no notatable value reaches — music21 padded
            # the hole with a 3/80 rest and the bar exported over its meter. A
            # tuplet is only ever written as a complete group, so its first note
            # sits on that tuplet's own grid: 0, 1/5, 2/5 for a quintuplet. An
            # onset that does not is a tuplet value handed to a note that was
            # never part of a group, and the honest repair is to give it the
            # nearest binary duration instead.
            #
            # A genuine group survives untouched: a triplet beginning on a beat
            # starts at 0, which lies on every grid, and its later notes at 1/6
            # and 1/3 lie on the ternary one.
            family = _tuplet_family(Fraction(dur_to_beats(e.duration)))
            if family:
                offset = Fraction(exact) - 1
                for prime in family:
                    if (offset * prime).denominator != 1 and (offset * prime * 2).denominator != 1:
                        e.duration = _binary_at_most(dur_to_beats(e.duration))
                        counts["isolated_tuplet_rewritten"] = (
                            counts.get("isolated_tuplet_rewritten", 0) + 1
                        )
                        break

        events.sort(key=lambda x: (x.bar, x.beat))

        # EXACT duplicates first, and separately from overlaps.
        #
        # Two notes on one beat in one layer are a CHORD — the ordinary way a
        # melody takes weight at an arrival — so the overlap rule below must not
        # touch them. But the same note written twice is not a chord, and used
        # to be removed only as a side effect of that rule. Removing it here
        # keeps both facts true at once: a doubled accompaniment is still
        # de-duplicated (39 of one section's 67 "overlaps" were exactly that),
        # and a chord still reaches the score.
        seen_exact: set = set()
        deduped = []
        for e in events:
            signature = (e.bar, round(float(_on_grid(e.beat)), 6), str(e.pitch), e.duration)
            if not is_grace(e.ornament) and signature in seen_exact:
                counts["duplicates_removed"] += 1
                continue
            seen_exact.add(signature)
            deduped.append(e)
        events[:] = deduped

        # A REST NEVER SHORTENS A NOTE.
        #
        # A rest carries no sound, so a rest sitting inside a note's span is the
        # generator saying two contradictory things about one instant and only
        # one of them is audible. The overlap rule below did not know that: it
        # read the rest as the next onset, found the note ran past it, and
        # CLAMPED THE NOTE. A half note with a pattern rest under its second
        # beat came out a quarter, reported as `overlaps_trimmed: 1`, which
        # reads as housekeeping.
        #
        # The rests come from the corpus, legitimately: a retrieved left-hand
        # pattern contains them, `pitch_to_midi("rest")` returns None so the
        # chord-tone snap falls through and the rest passes into the layer
        # unchanged, where a bass note is already sounding. Given a choice
        # between losing a rest and truncating a note, always lose the rest.
        #
        # This subsumes the same-onset case handled in the group pass below —
        # kept there because the group pass must know a rest is not a chord tone
        # before it decides what kind of group it is looking at.
        sounding_spans = [
            (e.bar, float(_on_grid(e.beat)), float(dur_to_beats(e.duration) or 0))
            for e in events
            if e.pitch != "rest" and not is_grace(e.ornament)
        ]
        if sounding_spans:
            covered = []
            for e in events:
                if e.pitch != "rest":
                    continue
                at = float(_on_grid(e.beat))
                if any(
                    bar == e.bar and start <= at + 1e-9 < start + span
                    for bar, start, span in sounding_spans
                ):
                    covered.append(id(e))
                    counts["rest_over_note_dropped"] += 1
            if covered:
                events[:] = [e for e in events if id(e) not in covered]

        # A chord is simultaneous notes of the SAME LENGTH. Notes sharing an
        # onset with different lengths are not a chord and not playable by one
        # voice — a 64th and a quarter struck together leave the quarter still
        # sounding when the next note arrives, which the meter check reports as
        # a bar holding more beats than it has. Keep the length most of the
        # group agrees on; that IS the chord, and the odd spans are the defect.
        from collections import Counter as _Counter

        by_onset: Dict[Tuple[int, float], List] = {}
        for e in events:
            if is_grace(e.ornament):
                continue
            by_onset.setdefault((e.bar, round(float(_on_grid(e.beat)), 6)), []).append(e)
        drop: set = set()
        for group in by_onset.values():
            if len(group) < 2:
                continue
            # A REST is not a chord tone. A rest sharing a note's onset is the
            # generator saying two contradictory things about one instant, and
            # treating the pair as a chord kept both: the assembler placed the
            # note and then laid the rest out sequentially, where it landed
            # PAST THE BARLINE. That is the trailing rest on the barline that
            # made one bass bar per piece export over its meter.
            sounding = [x for x in group if x.pitch != "rest"]
            if sounding and len(sounding) != len(group):
                for x in group:
                    if x.pitch == "rest":
                        drop.add(id(x))
                        counts["rest_over_note_dropped"] += 1
                group = sounding
                if len(group) < 2:
                    continue
            # Two events that are ALREADY chords are two chords, not one. A
            # viola handed `[F5,A5,C6]` and `[F3,A3,C4]` on the same beat cannot
            # play both — that is the orchestration planner writing an inner
            # line and a pad into one part's single voice — and laid out
            # sequentially they gave a 3/4 bar 5 beats. Keep the first; the
            # caller reports the loss (`notes_planned` vs `notes_written`).
            if not allow_chords:
                # An ORCHESTRAL part is one player: notes sharing an onset are
                # not a chord it can take, and this path has no voice splitter
                # to separate them into two lines. Keep the first and let the
                # caller report the loss — see `notes_planned` vs
                # `notes_written` in `assemble_orchestration`.
                for x in group[1:]:
                    drop.add(id(x))
                    counts["simultaneous_notes_dropped"] += 1
                continue
            chords = [x for x in group if isinstance(x.pitch, list)]
            if len(chords) > 1:
                for x in chords[1:]:
                    drop.add(id(x))
                    counts["second_chord_dropped"] += 1
                continue
            lengths = _Counter(x.duration for x in group)
            if len(lengths) < 2:
                continue  # a genuine chord
            keep_len = max(lengths, key=lambda d: (lengths[d], dur_to_beats(d)))
            for x in group:
                if x.duration != keep_len:
                    drop.add(id(x))
                    counts["chord_note_length_unified"] += 1
        if drop:
            events[:] = [e for e in events if id(e) not in drop]

        keep = []
        for i, e in enumerate(events):
            # A grace note SHARES its principal's beat by definition — it is
            # played before it and takes no metric time. Reading that as a
            # same-voice overlap deleted every appoggiatura and acciaccatura the
            # composer wrote, silently, in exactly the paths this repair was
            # added to protect.
            if is_grace(e.ornament):
                keep.append(e)
                continue
            start = _on_grid(e.beat) - 1
            length = dur_to_beats(e.duration)
            if start >= capacity:
                counts["overflow_dropped"] += 1
                continue
            # The next event at a LATER onset — not merely the next in the bar.
            #
            # Two notes starting on the same beat in the same layer are a
            # CHORD, which is the ordinary way a melody takes weight at an
            # arrival. This took the next event in the bar whatever its beat,
            # so a simultaneous note gave `room = 0` and was deleted as an
            # overlap: the engine could not represent a thickened melody note
            # at all, and every melody it wrote came out 100% single notes.
            # A chord is playable; an overlap is two DIFFERENT spans in one
            # voice, which is what this still catches.
            nxt = next(
                (
                    x
                    for x in events[i + 1 :]
                    if x.bar == e.bar
                    and not is_grace(x.ornament)
                    # OFFSETS on both sides. `start` is `_on_grid(e.beat) - 1`,
                    # zero-based, and `_on_grid(x.beat)` is one-based — so at
                    # beat 1 this read `1 > 0` and selected the very same-beat
                    # event it was written to skip. The guard excluded nothing,
                    # at any beat, and chords were still deleted.
                    and _on_grid(x.beat) - 1 > start
                ),
                None,
            )
            room = capacity - start
            if nxt is not None:
                room = min(room, _on_grid(nxt.beat) - 1 - start)
            if room <= 0:
                # An EXACT DUPLICATE is a different diagnosis from an overlap,
                # and counting them together hides which. A generator writing
                # the same note twice is noise the repair absorbs completely; a
                # generator writing two DIFFERENT notes into one voice has
                # written something a player cannot play, and one of them is
                # about to be lost. Both looked like "overlaps_trimmed: 67",
                # which reads as 67 notes shortened when it was mostly a
                # doubled accompaniment being de-duplicated.
                same = nxt is not None and nxt.pitch == e.pitch and nxt.duration == e.duration
                counts["duplicates_removed" if same else "overlaps_trimmed"] += 1
                continue
            if length > room:
                from .duration import largest_dur_at_most

                # NOT beats_to_dur: the nearest notatable value to the room left
                # can be LONGER than the room (1.4375 -> a dotted quarter at
                # 1.5), so the clamp rounded straight back past the barline.
                e.duration = largest_dur_at_most(room)
                # SHORTENED to fit, not removed. Counting that as
                # `overflow_dropped` said three notes had been lost from a
                # phrase where none had — they were clamped by a sixteenth,
                # because a drifted onset at beat 4.56 snapped to 4.5625 and a
                # 4/4 bar has no room for an eighth there. "Dropped" and
                # "clamped" are not the same report and the first is alarming.
                counts["overlaps_trimmed" if nxt is not None else "overflow_clamped"] += 1
            keep.append(e)
        events[:] = keep

    return {k: v for k, v in counts.items() if v}


def _all_event_lists(layer) -> List[List]:
    """Every event list on a LayerIR, including the numbered inner voices."""
    names = (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    )
    out = [getattr(layer, n, None) or [] for n in names]
    out.extend((getattr(layer, "inner_voices", None) or {}).values())
    return [e for e in out if e]


def _capture_theme_if_first_statement(graph, phrase_id: str) -> None:
    """Store (or refresh) the principal theme when its own phrase is committed.

    Two bugs lived in the "capture once" guard this replaces.

    It returned early whenever a theme surface already existed, so **recomposing
    the theme's own phrase left the old theme on the graph forever**. Every
    later brief then developed material that was no longer in the piece, and the
    theme-recurrence check reported the theme appearing in *zero* places —
    correctly, because the stored theme really had stopped matching anything.

    And it set the surface without setting `principal_theme_id`, so a piece
    could carry a populated theme whose id was the empty string; anything keyed
    on the id was silently working with no theme at all. A graph in that state
    is repaired here rather than left broken.
    """
    state = graph.phrases.get(phrase_id)
    slot = getattr(state, "slot", None) if state else None
    if slot is None:
        return
    role = getattr(slot, "dramatic_role", "")
    # The opening statement, or (for a piece planned without a dramatic role) the
    # phrase that starts at bar 1.
    is_theme_phrase = role == "establish" or slot.bar_start == 1
    have = getattr(graph, "principal_theme_surface", None)
    if have and not is_theme_phrase:
        return  # nothing to do: this is not the phrase the theme comes from
    from .theme_planner import principal_theme_phrase

    source = principal_theme_phrase(graph)
    if have and source and source != phrase_id:
        return  # the theme came from a different phrase; that capture stands
    # Either there is no theme yet, or this IS the phrase it came from and has
    # just been recomposed — re-capture so the stored theme is never stale.
    if not is_theme_phrase:
        return
    try:
        from .theme_planner import capture_theme_surface

        capture_theme_surface(graph, phrase_id, n_bars=min(4, slot.bar_count))
    except Exception:
        pass  # a missing theme must never block a commit


@_tool
def commit_agent_phrase_layer_ir(
    piece_id: str,
    phrase_id: str,
    layer_ir: Dict[str, Any],
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate, gate, and store agent-written LayerIR (full note-level IR).

    Call this when Claude (not the Python realizer) authored every
    ``LayerEvent`` for the phrase. Sets ``agent_authored`` so
    ``run_scales_section`` preserves this surface.

    Physical validation is strict. The commit gate then checks for
    mechanical output (skeletal density, photocopied accompaniment) with
    corpus-derived thresholds; artistic checks can be waived via
    ``allow=[{"check": ..., "reason": ...}]`` (logged to revision history).
    """
    allow = _as_list(allow, "allow")
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}

    layer = load_layer_ir_from_dict(layer_ir)
    layer.phrase_id = phrase_id
    slot = graph.phrases[phrase_id].slot
    if slot:
        # The SLOT is authoritative for key and meter. Testing `if not
        # layer.meter` never fired, because LayerIR defaults to a truthy (4, 4) —
        # so a 3/4 phrase committed as raw LayerIR kept 4/4, the meter check then
        # allowed four beats in a three-beat bar, and the score came out mis-barred.
        # An explicit meter that disagrees with the slot is reported, not silently
        # honored: the plan and the notes must agree on the bar length.
        supplied_meter = tuple(layer.meter) if layer.meter else None
        slot_meter = tuple(slot.meter) if slot.meter else (4, 4)
        if supplied_meter and supplied_meter != slot_meter and layer_ir.get("meter"):
            return {
                "ok": False,
                "error": "meter_mismatch",
                "hint": (
                    f"LayerIR declares meter {supplied_meter} but phrase slot "
                    f"{phrase_id} is {slot_meter}. Write the phrase in the "
                    f"planned meter, or change the plan first."
                ),
            }
        layer.meter = slot_meter
        # Same trap for key: the dataclass default "C" is truthy, so an unset key
        # used to stick as C major no matter what the slot planned.
        if not layer.key or not layer_ir.get("key"):
            layer.key = slot.key

    report = validate_layer_ir(layer, _physical_constraints(graph))
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    return _gated_commit(graph, workspace, phrase_id, layer, allow, composer)


@_tool
def commit_agent_phrase_direct_bars(
    piece_id: str,
    phrase_id: str,
    bars: List[Dict[str, Any]],
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert Claude's per-bar RH/LH shorthand to LayerIR and commit (gated).

    ``bars`` format matches ``direct_compose.compose_phrase``. Shorthand
    supports chords ``[C5,E5,G5]q``, ties ``~``, slurs ``( )``, ornaments
    ``:tr :mord :turn :grace``, articulations ``:stacc :acc :ten``,
    dynamics ``:p :f``, and hairpins ``< > !``.

    The commit gate blocks unambiguously mechanical output; waive a named
    artistic check with ``allow=[{"check": ..., "reason": ...}]``.
    """
    bars = _as_list(bars, "bars")
    allow = _as_list(allow, "allow")
    from .direct_compose import compose_phrase, parse_issues
    from .validator import validate_layer_ir

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    slot = graph.phrases[phrase_id].slot
    if not slot:
        return {"error": "Phrase has no slot"}

    if len(bars) != slot.bar_count:
        return {
            "error": "bar_count_mismatch",
            "expected_bars": slot.bar_count,
            "got": len(bars),
            "hint": (
                f"Write exactly {slot.bar_count} bar dicts (bars "
                f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}). A pickup "
                f"bar OCCUPIES the phrase's first bar — mark that first dict "
                f"{{'pickup': True}} and write only the upbeat in it; do not add an "
                f"extra dict for it, or the phrase would run into the next one's bars."
            ),
        }

    # Anything in the shorthand that will not survive to the page. The parser
    # used to fail SILENTLY in both directions: a pitch it could not read was
    # passed through and then dropped without a word by the engraver, and a
    # pitch it half-read came back as a different note ('C12q' -> 'C1', eleven
    # octaves down). Neither is a musical judgement — a token that cannot be
    # engraved is a typo, and only the composer can fix it.
    typos = parse_issues(bars, tuple(slot.meter) if slot.meter else (4, 4))
    if typos:
        return {
            "error": "unwritable_tokens",
            "tokens": typos[:12],
            "hint": (
                "These would have been silently dropped or read as a different note. "
                "A pitch is a letter A-G, an optional accidental (#, b, ##, bb) and an "
                "octave digit; a duration is one of the codes in craft §8. Fix the "
                "tokens and recommit."
            ),
        }

    layer = compose_phrase(
        bars,
        key=slot.key,
        bar_start=slot.bar_start,
        phrase_id=phrase_id,
        meter=slot.meter,
        instrumentation=_piece_instrumentation(graph),
    )
    report = validate_layer_ir(layer, _physical_constraints(graph))
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    return _gated_commit(graph, workspace, phrase_id, layer, allow, composer)


@_tool
def run_style_review_section(
    piece_id: str,
    section_id: str,
    threshold: float = 0.35,
    persist: bool = True,
) -> Dict[str, Any]:
    """Compare assembled section MusicXML to StyleDNA-derived targets; optional RevisionScript."""
    from .review_style_gate import run_style_review_section as _gate

    return _gate(piece_id, section_id, threshold=threshold, persist=persist)


# ─── Agent Composition Support (briefs, continuity, self-evaluation) ─────────


@_tool
def commit_phrase_sketch(piece_id: str, phrase_id: str, sketch: Dict[str, Any]) -> Dict[str, Any]:
    """Record the structural plan for a phrase BEFORE its notes are written.

    ``/w-compose`` step 2 and the phrase-composer agent both describe writing
    SketchIR — anchors, harmonic rhythm, texture intent, dynamic shape, breath
    points, cadence approach — as a required step, with a seven-question
    checklist. There was no way to do it: ``state.sketch`` was written only
    inside ``run_scales_section``, the engine fallback the default flow never
    takes. So on 164 real phrases the field holds a value 10 times, all of them
    engine-realized, and the brief's SKETCH section — which is how phrase N+1
    sees what phrase N planned — was empty for everything the agent wrote.

    Accepts a plain dict, so the agent can send exactly the structure it thought
    in. Unknown keys are ignored rather than rejected; a sketch is a plan, not a
    contract, and refusing one over a stray key would just push the step back
    into being skipped.
    """
    from .models import SketchIR
    from .piece_graph import _dataclass_from_dict

    workspace = _WORKSPACE / piece_id
    path = workspace / "piece_graph.json"
    if not path.exists():
        return {"error": f"no workspace for '{piece_id}'"}
    graph = PieceGraph.load(str(path))
    state = graph.phrases.get(phrase_id)
    if state is None:
        return {"error": f"unknown phrase_id: {phrase_id} (known: {sorted(graph.phrases)[:8]})"}
    if not isinstance(sketch, dict):
        return {"error": "sketch must be a dict of SketchIR fields"}

    data = dict(sketch)
    data.setdefault("phrase_id", phrase_id)
    state.sketch = _dataclass_from_dict(SketchIR, data)
    graph.save(str(path))

    from .composition_brief import _summarize_sketch

    summary = _summarize_sketch(state.sketch)
    return {
        "ok": True,
        "phrase_id": phrase_id,
        "recorded": sorted(k for k in summary),
        "ignored_keys": sorted(
            set(data) - {f.name for f in __import__("dataclasses").fields(SketchIR)}
        ),
    }


@_tool
def get_composition_brief(
    piece_id: str,
    phrase_id: str,
    n_exemplars: int = 8,
    composer: Optional[str] = None,
    fmt: str = "text",
) -> Any:
    """Build the composition brief for one phrase.

    The brief contains real corpus exemplar bars (in direct_compose
    shorthand), density/ornament target stats, ledger state, and the
    continuity context from the previous phrase. Claude must read this
    BEFORE writing any notes for the phrase.

    fmt="text" returns a compact string; fmt="json" returns a dict.
    """
    from dataclasses import asdict

    from .composition_brief import build_brief, render_text

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    if phrase_id not in graph.phrases:
        # `build_brief` raises a KeyError with a good message inside it, but a
        # traceback is not a result. Every other tool returns one.
        return {
            "error": f"Unknown phrase '{phrase_id}' in '{piece_id}'",
            "phrases": sorted(graph.phrases)[:20],
            "hint": "get_section_status(piece_id, section_id) lists a section's phrases.",
        }
    brief = build_brief(graph, phrase_id, n_exemplars=n_exemplars, composer=composer)
    if _persist_brief_receipt(graph, phrase_id, brief):
        graph.save(str(workspace / "piece_graph.json"))
    # The composing agent reads the brief and nothing else, so this is where a
    # missing planning step has to appear or it appears nowhere. A brief built
    # on an uncompiled style still renders — with generic bands and no
    # fingerprints — and reads exactly like one that was armed.
    gaps = planning_gaps(graph)
    if fmt == "json":
        out = asdict(brief)
        if gaps:
            out["planning_gaps"] = gaps
        return out
    text = render_text(brief, graph)
    if gaps:
        lines = [
            "",
            "!! PLANNING NEVER SUPPLIED: " + ", ".join(g["missing"] for g in gaps),
            "   Each has a silent fallback, so this brief looks complete and is not.",
        ]
        for gap in gaps:
            lines.append(f"   - no {gap['missing']}: {gap['costs']}")
            lines.append(f"     fix: {gap['fix']}")
        text = "\n".join(lines) + "\n\n" + text
    return text


def _persist_brief_receipt(graph, phrase_id: str, brief) -> bool:
    """Record a brief receipt on the phrase trace. The commit gate REQUIRES
    this receipt — a phrase cannot be committed unless its brief was fetched
    (``brief_fetched``), and a brief that yielded no corpus exemplars is marked
    ``brief_insufficient`` so the commit is blocked unless explicitly waived.
    Also persists the exemplar shorthands so the gate can check the surface
    actually adapted them (anti-skip). Returns True if anything was written."""
    state = graph.phrases.get(phrase_id)
    if state is None:
        return False
    if getattr(state, "context_trace", None) is None:
        state.context_trace = {}
    if not isinstance(state.context_trace, dict):
        return False
    rhs = [ex.rh for ex in getattr(brief, "exemplars", []) if getattr(ex, "rh", "")]
    lhs = [ex.lh for ex in getattr(brief, "exemplars", []) if getattr(ex, "lh", "")]
    state.context_trace["brief_fetched"] = True
    state.context_trace["briefed_exemplars"] = rhs
    state.context_trace["briefed_exemplar_lhs"] = lhs
    state.context_trace["brief_insufficient"] = not rhs
    composer = getattr(brief, "composer", "")
    if composer:
        state.context_trace["brief_composer"] = composer
    return True


# ─── Whole-score reference study ─────────────────────────────────────────────


def list_reference_scores(composer: str) -> Any:
    """List the complete reference pieces available to study for a composer.

    Returns one entry per source piece/movement (bar count, key, meter, dominant
    textures) so the agent can pick 2-4 representative scores to read in full
    BEFORE composing — the way a human composer studies real scores. Pass a
    composer name or a ``style__<name>`` id (aggregates over armed members).
    """
    from .reference_study import list_reference_scores as _list

    return _list(composer)


def get_reference_score(
    composer: str,
    source: str,
    target_key: Optional[str] = None,
    max_bars: Optional[int] = None,
) -> Any:
    """Read one COMPLETE reference piece in readable shorthand.

    Reconstructs the full piece from the corpus (ordered by bar), rendered in the
    same direct_compose shorthand the brief uses, with each bar's roman/function
    and RH/LH texture so the agent sees the harmonic and textural arc — not just
    disconnected notes. Pass ``target_key`` to transpose into the key you'll
    compose in. The agent reads this and writes its OWN analysis via
    ``save_reference_study``.
    """
    from .reference_study import reconstruct_score

    return reconstruct_score(composer, source, target_key=target_key, max_bars=max_bars)


@_tool
def save_reference_study(
    piece_id: str,
    composer: str,
    source: str,
    analysis: str,
    observations: Optional[Dict[str, Any]] = None,
) -> Any:
    """Persist the agent's OWN analysis of a reference piece to the PieceGraph.

    ``analysis`` is the agent's prose: form, themes, harmonic language, texture
    and dynamic arc, "what makes it work". ``observations`` is optional structured
    notes (e.g. cadence points, recurring gestures). Stored under
    ``reference_studies["<composer>/<source>"]`` and fed forward into every phrase
    brief, so the agent composes from its own understanding of real scores.
    """
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    key = f"{composer}/{source}"
    graph.patch(
        path=f"reference_studies.{key}",
        operation="set",
        value={
            "composer": composer,
            "source": source,
            "analysis": analysis,
            "observations": observations or {},
        },
        skill="w-plan",
        reason=f"Whole-score study of {key}",
    )
    graph.save(str(workspace / "piece_graph.json"))
    return {"saved": True, "key": key, "studies": sorted(graph.reference_studies.keys())}


@_tool
def run_agent_section_briefs(
    piece_id: str,
    section_id: str,
    n_exemplars: int = 6,
    composer: Optional[str] = None,
    fmt: str = "text",
) -> Any:
    """Build briefs for every phrase in a section with ONE corpus load.

    Prefer this over per-phrase get_composition_brief for large works —
    corpus shards (20-90MB per composer) are loaded once per process.
    """
    from dataclasses import asdict

    from .composition_brief import build_brief, render_text

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        return {"error": f"No phrases found for section '{section_id}'"}

    out = {}
    dirty = False
    for pid in phrase_ids:
        try:
            brief = build_brief(graph, pid, n_exemplars=n_exemplars, composer=composer)
            dirty = _persist_brief_receipt(graph, pid, brief) or dirty
            out[pid] = asdict(brief) if fmt == "json" else render_text(brief, graph)
        except KeyError as exc:
            out[pid] = {"error": str(exc)}
    if dirty:
        graph.save(str(workspace / "piece_graph.json"))
    if fmt == "text":
        return "\n\n".join(v if isinstance(v, str) else json.dumps(v) for v in out.values())
    return out


@_tool
def plan_readiness(piece_id: str) -> Dict[str, Any]:
    """Is this piece's plan actually complete enough to compose against?

    Every part of the plan is optional at the type level, so a piece can reach
    the phrase composers with an empty narrative, no motifs and no reference
    study, and nothing anywhere says so — the briefs simply omit those sections
    and the agent cannot tell "the planner skipped this" from "this composer has
    none".

    Measured over the twelve pieces in ``workspace/``: five have a populated
    motif bank and NOT ONE had an elected principal theme or a single placement,
    and only one of twelve carried a saved reference study. Both systems are
    documented as load-bearing. This is the check that would have caught either
    on the first run.

    Returns ``ready`` (nothing missing that changes the notes), plus ``missing``
    and ``thin`` lists naming what to go back and do.
    """
    workspace = _WORKSPACE / piece_id
    path = workspace / "piece_graph.json"
    if not path.exists():
        return {"ready": False, "missing": [f"no workspace for '{piece_id}'"], "thin": []}
    graph = PieceGraph.load(str(path))

    missing: List[str] = []
    thin: List[str] = []

    if not graph.phrases:
        missing.append("form graph — no phrase slots exist (run build_form_graph)")

    dna = getattr(graph, "style_dna", None)
    composer_id = (getattr(dna, "composer_id", "") or "").strip()
    if not composer_id or len(composer_id) < 2:
        missing.append(
            f"style — composer_id is {composer_id!r} (run compile_style with a real "
            f"composer or style name; passing a bare string where a list is "
            f"expected resolves it to a single letter)"
        )
    elif getattr(dna, "tier", "") in ("C", "D"):
        thin.append(f"style tier {dna.tier} for '{composer_id}' — briefs will be generic")

    sections = getattr(getattr(graph, "narrative", None), "sections", None) or []
    if not sections:
        missing.append(
            "narrative — no sections (run save_narrative). Without it every phrase's "
            "CREATIVE INTENT falls back to its bare function label"
        )
    elif not any((getattr(s, "character", "") or "").strip() for s in sections):
        thin.append("narrative sections have no authored `character` prose")
    else:
        # An EMPTY character is caught above; a character the planner wrote for
        # itself is not. `build_form_graph` fills the field with
        # `"; ".join(ROLE_INTENT[r] for r in roles)`, so a piece can pass the
        # check above with five sections of text that are identical to every
        # other piece of the same form — measured byte-for-byte across a Chopin
        # nocturne and a Mozart andante. The readiness report said the narrative
        # was present; what was present was the form's shape, not the piece's.
        from .composition_brief import _character_is_role_derived

        default_only = [
            getattr(s, "label", "") or "?"
            for s in sections
            if _character_is_role_derived(
                getattr(s, "character", "") or "", getattr(s, "gesture", "") or ""
            )
        ]
        if len(default_only) == len(sections):
            thin.append(
                "narrative `character` is the planner's own role text on every "
                "section — generic to the form, identical for any piece with this "
                "shape. Run save_narrative with prose about THIS piece"
            )
        elif default_only:
            thin.append(
                f"narrative `character` is still the planner's default on "
                f"{len(default_only)} of {len(sections)} sections "
                f"({', '.join(default_only[:4])})"
            )

    if not graph.motif_bank:
        missing.append(
            "motifs — the motif bank is empty (run resolve_motifs). A piece is "
            "memorable because ONE idea recurs transformed; with no motif the "
            "brief has no material to name"
        )
    else:
        placed = sum(
            1 for st in graph.phrases.values() if getattr(st.slot, "motif_transforms", None)
        )
        if not graph.principal_theme_id:
            missing.append("motifs — no principal theme elected")
        elif not placed:
            missing.append("motifs — principal theme is placed in no phrase")

    movements = getattr(getattr(graph, "form", None), "movements", None) or []
    if len(movements) > 1 and not getattr(graph, "work_graph", None):
        missing.append(
            f"work plan — {len(movements)} movements and no WorkGraph (run init_work + "
            f"plan_movement). Without it nothing decides what each movement is FOR, "
            f"how it contrasts with the last, or what the finale pays off"
        )

    if not getattr(graph, "reference_studies", None):
        missing.append(
            "reference study — none saved (run save_reference_study after reading "
            "whole scores). Every brief's 'WHAT YOU LEARNED FROM THE SCORES' "
            "section is empty without it"
        )

    return {
        "piece_id": piece_id,
        "ready": not missing,
        "missing": missing,
        "thin": thin,
        "phrases": len(graph.phrases),
        "motifs": len(graph.motif_bank or {}),
        "narrative_sections": len(sections),
        "reference_studies": len(getattr(graph, "reference_studies", None) or {}),
    }


@_tool
def get_section_status(piece_id: str, section_id: str) -> Dict[str, Any]:
    """Compact, section-scoped status — use this instead of dumping the graph.

    Returns ordered phrases with status/agent_authored/bar range and, for
    committed phrases, the realized tail (what the next phrase connects to).
    """
    from .composition_brief import _last_events_summary

    graph = _load_graph(piece_id)
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        known = sorted(graph.form.sections)
        return {"error": f"Unknown section '{section_id}'", "known_sections": known}

    phrases = []
    committed = 0
    for pid in phrase_ids:
        state = graph.phrases.get(pid)
        if state is None:
            phrases.append({"phrase_id": pid, "status": "missing"})
            continue
        slot = state.slot
        entry: Dict[str, Any] = {
            "phrase_id": pid,
            "status": state.status,
            "agent_authored": bool(getattr(state, "agent_authored", False)),
            "bars": f"{slot.bar_start}-{slot.bar_start + slot.bar_count - 1}",
            "function": slot.function,
            "cadence": slot.cadence_target,
        }
        if state.realized is not None:
            committed += 1
            tail = _last_events_summary(state.realized)
            if tail:
                entry["exit"] = tail
        phrases.append(entry)

    return {
        "piece_id": piece_id,
        "section_id": section_id,
        "committed": committed,
        "total": len(phrase_ids),
        "phrases": phrases,
    }


@_tool
def get_phrase_continuity(piece_id: str, phrase_id: str) -> Dict[str, Any]:
    """Continuity context for one phrase, read from committed state on disk.

    Disk is the source of truth — never trust a subagent's self-reported
    exit state over what was actually committed.
    """
    from .composition_brief import _summarize_slot, _transition_context

    graph = _load_graph(piece_id)
    state = graph.phrases.get(phrase_id)
    if state is None:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    return {
        "phrase_id": phrase_id,
        "slot": _summarize_slot(state.slot),
        "transition_in": _transition_context(graph, phrase_id),
    }


# Discriminator target bands — corpus-derived human-vs-AI tells
# (see .claude/context/general/human-sounding-music.md)
# Generic human-vs-AI bands, keyed by the metric name on the EvidenceBundle
# (i.e. what style_analyzer measures). Keep these names in sync with
# EvidenceBundle's fields — a band whose key is not a bundle attribute is
# silently skipped and the metric simply disappears from the report.
_DISCRIMINATOR_BANDS = {
    # CALIBRATED against 36 real movements by Mozart, Beethoven and Chopin
    # (5th-95th percentile, widened 10%). Every one of these was previously a
    # hand-written guess, and every one of them rejected real music — the worst,
    # texture_change_pct at (0.35, 0.70), rejected **20 of 24** real movements.
    # A band that flags what real composers actually write does not measure the
    # music; it measures the band, and it pushes the critic toward the
    # non-idiomatic. test_discriminator_bands_do_not_reject_real_music keeps
    # them honest.
    #
    # texture_change_pct was widened again once Bach was armed: the calibration
    # set was Mozart/Beethoven/Chopin only, and Bach's corpus mean is **0.622**,
    # above the old 0.585 ceiling. Every Bach section would have been reported
    # "texture change high" — the discriminator telling the critic that Bach's
    # actual texture behaviour is a defect. Per-composer means now measured over
    # the whole armed corpus span 0.144 (Chopin) to 0.622 (Bach); the band
    # covers that range with a margin. A composer with a corpus_profile is
    # judged against its own mean ± 2σ instead (see _PROFILE_OVERRIDABLE), so
    # this generic band only applies to unarmed references.
    "texture_change_pct": (0.045, 0.85),
    # A COUNT of contour reversals per bar, not a fraction (see
    # _PROFILE_OVERRIDABLE below for why that distinction matters). Real
    # movements run 0.9 to 3.6; the old (1.0, 2.0) rejected half of them,
    # including 5 of 12 Mozart sonata movements.
    "direction_changes_per_bar": (0.9, 3.6),
    "density_cv": (0.198, None),
    "rest_ratio": (0.039, 0.265),
    "stepwise_pct": (0.312, 0.831),
    "events_per_bar": (5.67, 21.23),
    "rhythmic_variety": (4.5, None),
    "dynamic_markings_per_bar": (0.072, None),
}

# Bands a composer's corpus_profile may narrow to that composer's own spread.
# This is an ALLOW-LIST on purpose. Overriding by name alone silently swapped
# units: corpus_profile's old "direction_changes_per_bar" was a FRACTION of bars
# whose direction label changes (mean 0.56), and it was overriding a band applied
# to style_analyzer's per-bar reversal COUNT (1-3 for real music). Every section
# with a healthy melodic contour was therefore reported "high" with the hint
# "melodic contour is monotonic or jittery" — the discriminator was telling the
# critic that good melody writing was a defect. Two quantities, one name.
_PROFILE_OVERRIDABLE = frozenset({"texture_change_pct", "density_cv", "events_per_bar"})


# The four surface facts that most decide whether a phrase sounds like a person
# playing an instrument or a program filling bars, paired with the plain-English
# sentence to say when the piece is far from the composer on one.
_GAP_METRICS = {
    "rest_bar_ratio": (
        "bars containing a rest",
        "the music never stops sounding — the clearest single tell of a machine",
        "the line is so broken up it cannot sustain a phrase",
    ),
    "dotted_ratio": (
        "bars carrying a dotted rhythm",
        "the rhythm is running even, with no long-short spring in it",
        "the dotted figure has hardened into a mannerism",
    ),
    "lh_texture_change_pct": (
        "barlines where the left hand changes character",
        "one accompaniment idiom is being held all the way through",
        "the accompaniment is restless, changing character faster than the music does",
    ),
    "third_ratio": (
        "melodic intervals that are thirds",
        "the melody is all steps — it never leaps into a chord",
        "the melody is noodling in broken chords",
    ),
}


def _rhythmic_gap(divergence: Dict[str, Any], composer: str) -> Dict[str, Any]:
    """Restate the biggest corpus divergences as sentences instead of z-scores.

    Everything here is already in ``corpus_divergence``. A B-flat andante was
    reported at ``rest_bar_ratio z=-2.32`` and the number was read, understood
    as diagnostic, and left alone; the same fact as "your piece rests in 22% of
    its bars, Mozart rests in 60%" is one a composer acts on. This is advisory
    exactly like the rest of the corpus comparison — it names a distance, never
    a target, and metric-chasing remains the wrong response.
    """
    out: List[Dict[str, Any]] = []
    metrics = (divergence or {}).get("metrics") or {}
    for key, (what, why_low, why_high) in _GAP_METRICS.items():
        m = metrics.get(key)
        if not isinstance(m, dict) or m.get("z") is None:
            continue
        try:
            z = float(m["z"])
            mine = float(m["value"])
            theirs = float(m.get("corpus_mean", 0.0))
        except (TypeError, ValueError):
            continue
        if abs(z) < 1.5:
            continue
        # The reading depends on WHICH SIDE the piece falls on. A first version
        # carried only the below-case sentence and reported a piece resting in
        # 79% of its bars as "the music never stops sounding".
        direction = "far below" if z < 0 else "far above"
        why = why_low if z < 0 else why_high
        out.append(
            {
                "metric": key,
                "z": round(z, 2),
                "note": (
                    f"{mine:.0%} of your {what} vs {composer}'s {theirs:.0%} — "
                    f"{direction} him. Heard as: {why}."
                ),
            }
        )
    out.sort(key=lambda d: -abs(d["z"]))
    return {"composer": composer, "gaps": out}


@_tool
def self_evaluate(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Assemble a section (or the full piece) and compare its measured
    statistics to corpus norms — the discriminator report.

    This is what the fresh-ears reviewer reads: generated-vs-corpus on the
    metrics that most separate human music from AI output (texture change
    rate above all). Section-level by design — these metrics are
    meaningless on a single 4-bar phrase.
    """
    from .assembler import assemble
    from .composition_brief import resolve_composer
    from .feedback.evidence_extractor import extract_from_file

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    warnings: List[str] = []
    resolved = resolve_composer(graph, composer, warnings)

    scope = f"section-{section_id}" if section_id else "full"
    try:
        path = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
    except ValueError as exc:
        return {"error": str(exc)}

    bundle = extract_from_file(path, resolved)
    if bundle is None:
        return {"error": f"Could not analyze assembled score at {path}"}

    report: Dict[str, Any] = {
        "piece_id": piece_id,
        "scope": scope,
        "composer_reference": resolved,
        "bar_count": bundle.bar_count,
        "metrics": {},
        "flags": [],
        "warnings": warnings,
    }

    # style_analyzer reports these as PERCENTAGES (0-100) while the bands here are
    # fractions, so they are converted unconditionally. The old rule was "divide
    # if the value exceeds 1.5", which silently inverted any piece with under 1.5%
    # rests: 0.8% was read as the fraction 0.8 and reported as far ABOVE a
    # 0.03-0.15 band — a score with almost no breathing room was told it had too
    # much. Guessing units from magnitude is not a contract.
    _PCT_METRICS = {"texture_change_pct", "rest_ratio", "stepwise_pct"}

    # Composer-aware bands: when the resolved composer has a corpus_profile,
    # judge each metric against THAT composer's own spread (mean ± 2σ) instead
    # of the generic human-vs-AI band. Otherwise the generic band can fight the
    # composer — e.g. it demands texture_change ≥0.35 while real Beethoven/Liszt
    # sit at ~0.26-0.31, penalising idiomatic figural persistence as "monotony".
    from .composition_brief import corpus_profile as _corpus_profile

    bands = dict(_DISCRIMINATOR_BANDS)
    _prof_metrics = (_corpus_profile(resolved) or {}).get("metrics", {})
    for _m, _stat in _prof_metrics.items():
        if _m not in bands or _m not in _PROFILE_OVERRIDABLE:
            continue  # same name != same quantity; see _PROFILE_OVERRIDABLE
        _mean, _sd = _stat.get("mean"), _stat.get("stdev")
        if _mean is None or not _sd or _sd <= 0:
            continue  # degenerate (e.g. grace_ratio=0 in MIDI corpus) → keep generic
        bands[_m] = (max(0.0, _mean - 2 * _sd), _mean + 2 * _sd)

    for metric, (lo, hi) in bands.items():
        value = getattr(bundle, metric, None)
        if value is None:
            value = (bundle.raw_metrics or {}).get(metric)
        if value is None:
            continue
        if metric in _PCT_METRICS:
            value = value / 100.0
        status = "ok"
        if lo is not None and value < lo:
            status = "low"
        elif hi is not None and value > hi:
            status = "high"
        report["metrics"][metric] = {
            "value": round(float(value), 3),
            "target": [lo, hi],
            "status": status,
        }
        if status != "ok":
            hints = {
                "texture_change_pct": (
                    "texture is static — real movements change texture between "
                    "4.5% and 58.5% of consecutive bars"
                    if status == "low"
                    else "texture changes more often than any real movement in the corpus"
                ),
                "direction_changes_per_bar": (
                    "the melodic line barely changes direction (monotonic) or "
                    "reverses far more often than any real movement in the corpus"
                ),
                "density_cv": "density is flat — no ebb and flow",
                "rest_ratio": ("no breathing room" if status == "low" else "too sparse"),
                "stepwise_pct": (
                    "melody is leap-heavy/fragmented"
                    if status == "low"
                    else "melody never leaps — no peaks"
                ),
                "events_per_bar": ("skeletal writing" if status == "low" else "overstuffed"),
                "rhythmic_variety": "too few distinct durations",
                "dynamic_markings_per_bar": "dynamics are flat",
            }
            report["flags"].append(
                {
                    "metric": metric,
                    "status": status,
                    "value": report["metrics"][metric]["value"],
                    "hint": hints.get(metric, ""),
                }
            )

    # Extra context the critic can use
    report["texture_distribution"] = {
        "rh": dict(
            sorted((bundle.rh_texture_distribution or {}).items(), key=lambda kv: -kv[1])[:6]
        ),
        "lh": dict(
            sorted((bundle.lh_texture_distribution or {}).items(), key=lambda kv: -kv[1])[:6]
        ),
    }
    report["assembled_path"] = path

    # Composer-specific distribution comparison (z-scores vs this composer's
    # own corpus), reusing the already-assembled score.
    divergence = _corpus_divergence_from_path(path, resolved, scope)
    if "error" not in divergence:
        # Every z-score here is measured against a corpus that is one genre:
        # Bach's is 100% four-part chorales, Haydn's 100% string quartets. A
        # keyboard piece judged "far from Bach" may simply be far from a
        # chorale. Say so beside the numbers rather than letting them pass as
        # facts about the composer.
        try:
            from .composition_brief import corpus_scope

            sc = corpus_scope(resolved)
            if sc.get("narrow"):
                divergence["corpus_scope"] = (
                    f"{sc['dominant_share']:.0%} of the {resolved} corpus behind these "
                    f"z-scores is {sc['dominant']}. Divergence from it is divergence "
                    f"from that genre, not from {resolved}."
                )
        except Exception:
            pass
        report["corpus_divergence"] = divergence
        report["rhythmic_gap"] = _rhythmic_gap(divergence, resolved)

    # Anti-skip: how much of the scope Claude actually authored, and any
    # phrases flagged as composed-blind (resembling no briefed exemplar).
    report["authoring"] = _authoring_summary(graph, section_id)
    # An unfinished piece must SAY it is unfinished. A score assembled from 3 of
    # 9 phrases is simply shorter, with nothing in any report explaining why:
    # `warnings` came back EMPTY for exactly that piece, while `authoring` called
    # its six empty phrases "engine_realized". Everything else in this report
    # describes only the phrases that exist, which is misleading unsaid.
    _unrealized = report["authoring"].get("unrealized") or 0
    if _unrealized:
        _named = ", ".join(report["authoring"].get("unrealized_phrases", [])[:8])
        warnings.append(
            f"INCOMPLETE: {_unrealized} of {report['authoring'].get('phrases', 0)} "
            f"phrases have no notes at all ({_named}). Every measurement in this "
            f"report describes only the phrases that exist."
        )

    # The craft checklist runs on every commit and is stored on the phrase —
    # and the reviewer, whose whole input is this report, never saw it. Advisory
    # by construction; measured over 200 real corpus phrases from five composers
    # the individual checks fire on 1.5%-13.5% of them, which is the same band
    # the realism detectors run in, so they are hints and not verdicts.
    try:
        from .craft_checker import craft_findings

        craft: List[Dict[str, Any]] = []
        for pid, ps in graph.phrases.items():
            if section_id and not (ps.slot and ps.slot.section_id == section_id):
                continue
            cc = getattr(ps, "craft_check", None)
            if cc is None:
                continue
            for line in craft_findings(cc) or []:
                craft.append({"phrase": pid, "note": str(line)})
        if craft:
            report["craft"] = {
                "findings": craft[:20],
                "count": len(craft),
                "note": (
                    "Advisory. Measured on 200 real corpus phrases these checks fire "
                    "on 1.5%-13.5% of real music each — a phrase may fail one on "
                    "purpose (no rest because it elides into the next, a deliberately "
                    "static bass, two-voice counterpoint that has no inner voice)."
                ),
            }
    except Exception as exc:
        report["craft"] = {"error": f"{type(exc).__name__}: {exc}"}

    # Which briefed evidence the commits actually used. CLAUDE.md documents this
    # as "embedded in self_evaluate" and it was wired only into
    # `run_scales_section` — so the reviewer, whose whole input is this report,
    # could not tell a phrase built from the corpus exemplars from one invented
    # beside them.
    try:
        from .composition_brief import composer_coverage_tier
        from .context_utilization import compute_section_coverage, compute_utilization

        # `context_trace` round-trips through JSON as a plain dict, and
        # `compute_utilization` reads dataclass attributes — so on any graph
        # loaded from disk (which is every graph a reviewer sees) the report
        # could not be computed at all.
        from .models import ContextTrace
        from .piece_graph import _dataclass_from_dict

        def _as_trace(t, pid):
            if isinstance(t, ContextTrace):
                return t
            if isinstance(t, dict):
                try:
                    return _dataclass_from_dict(ContextTrace, {"phrase_id": pid, **t})
                except Exception:
                    return None
            return None

        traces = {}
        for pid, ps in graph.phrases.items():
            if section_id and not (ps.slot and ps.slot.section_id == section_id):
                continue
            tr = _as_trace(getattr(ps, "context_trace", None), pid)
            if tr is not None:
                traces[pid] = tr
        if traces:
            tier = (composer_coverage_tier(resolved) or {}).get("tier", "D")
            if section_id:
                util = compute_section_coverage(section_id, traces, tier=tier)
            else:
                u = compute_utilization(traces, tier=tier)
                util = u.as_dict() if hasattr(u, "as_dict") else vars(u)

            # The engine populates these counters; an AGENT-authored commit does
            # not, so on the default path every field is 0. Reported raw, that
            # reads as "this piece used no corpus evidence at all" — a number
            # that looks like evidence and is not, which is the exact failure
            # this report is elsewhere used to catch. What IS recorded for an
            # agent commit is the brief receipt, so report that instead.
            raw = [
                ps.context_trace or {}
                for ps in graph.phrases.values()
                if not section_id or (ps.slot and ps.slot.section_id == section_id)
            ]
            briefed = [t for t in raw if t.get("brief_fetched")]
            if briefed and not any(v for k, v in util.items() if isinstance(v, (int, float)) and v):
                report["context_utilization"] = {
                    "path": "agent_authored",
                    "note": (
                        "The engine's utilization counters do not apply to phrases "
                        "the agent wrote; what is recorded is the brief receipt."
                    ),
                    "phrases_briefed": len(briefed),
                    "phrases_total": len(raw),
                    # `briefed_exemplars` is persisted as a COUNT by one writer
                    # and as the LIST of exemplars by another; accept both.
                    "exemplars_shown": sum(
                        len(v) if isinstance(v, list) else int(v or 0)
                        for v in (t.get("briefed_exemplars") for t in briefed)
                    ),
                    "composed_blind": sum(1 for t in raw if t.get("composed_blind")),
                }
            else:
                report["context_utilization"] = util
    except Exception as exc:
        report["context_utilization"] = {"error": f"{type(exc).__name__}: {exc}"}

    # Transparency (C4): the band-based flags above use GENERIC human-vs-AI
    # discriminator bands; the composer-specific comparison lives in
    # corpus_divergence. Say so, and flag when only the generic bands were
    # available (no corpus_profile for this composer).
    report["bands_source"] = (
        "generic human-vs-AI discriminator bands; composer-specific z-scores "
        "are in corpus_divergence"
    )
    if "corpus_divergence" not in report:
        report["warnings"].append(
            f"no composer-specific corpus_profile for '{resolved}' — only "
            f"generic discriminator bands were applied (run "
            f"scripts/build_corpus_profiles.py or arm the composer)"
        )

    # Musical ear: bar/beat-level structural defects (vertical clash, buried
    # melody, unresolved NCT, no breathing, monotony) — the feedback signal the
    # actor-critic loop revises against. Reuses the already-assembled score.
    try:
        from .musical_ear import ear_report

        report["ear"] = ear_report(
            path, _extract_generated_bars(path, resolved, scope), graph=graph
        )
    except Exception as exc:  # never let the ear crash a review
        report["ear"] = {
            "findings": [],
            "summary": {"error_count": 0, "warn_count": 0},
            "undetectable": [],
            "error": str(exc),
        }

    # Score realism: formula, uniformity and notational poverty — the defects
    # that are not *wrong* but are obviously not written by a person. The ear
    # answers "is anything broken here"; this answers "does this read as
    # engraved music". It reported nothing on a score that used one cadence
    # formula in seven of its 41 bars and carried no articulation at all,
    # because none of that is an error. Every finding is advisory: this is
    # material for the fresh-ears critic to weigh, never an auto-block.
    try:
        from .score_realism import realism_report

        report["realism"] = realism_report(path, graph=graph, scope=scope, composer=resolved)
    except Exception as exc:  # never let the audit crash a review
        report["realism"] = {
            "findings": [],
            "summary": {"by_detector": {}, "warn_count": 0, "info_count": 0},
            "notation_census": {},
            "error": f"{type(exc).__name__}: {exc}",
        }

    # Voicing and cadence analysis over the PieceGraph. These read the phrases
    # as musical objects rather than as an engraved file, so they see what the
    # score-side audit cannot: whether the texture's weight actually MOVES
    # (simultaneity_cv — the measurement that showed the previous piece was not
    # thin, it was unvarying), and whether each cadence the notes describe is
    # the cadence the plan asked for, which nothing had ever checked.
    try:
        from .cadence_analysis import analyze_cadences
        from .voicing import analyze_voicing, texture_runs

        in_scope = [
            ps
            for ps in graph.phrases.values()
            if ps.realized and (not section_id or (ps.slot and ps.slot.section_id == section_id))
        ]
        in_scope.sort(key=lambda ps: ps.slot.bar_start if ps.slot else 0)
        merged = None
        if in_scope:
            from .direct_compose import merge_phrases

            merged = merge_phrases(
                [ps.realized for ps in in_scope],
                key=(in_scope[0].slot.key if in_scope[0].slot else "C"),
                meter=(tuple(in_scope[0].slot.meter) if in_scope[0].slot else (4, 4)),
                piece_id=piece_id,
            )
        if merged is not None:
            # Part-writing reaches the reviewer. `analyze_counterpoint` finds
            # parallel fifths and octaves, hidden octaves into cadences, doubled
            # leading tones, unresolved sevenths and voice independence — and it
            # lived only in `musical_report`, while the music-critic is given
            # "only the score and the self_evaluate report". A three-voice fugue
            # with 5 parallel fifths and 2 parallel octaves passed review with
            # nothing to see. In the contrapuntal styles this system is armed for
            # — Bach, Palestrina, Monteverdi — those are the cardinal errors.
            try:
                from .counterpoint import analyze_counterpoint, summarize_for_critic

                cp = analyze_counterpoint(
                    merged, key=(in_scope[0].slot.key if in_scope[0].slot else "C")
                )
                report["part_writing"] = {
                    "errors": cp.error_count,
                    "warnings": cp.warn_count,
                    "independence": round(cp.independence, 3),
                    "by_kind": cp.by_kind(),
                    "lines": summarize_for_critic(cp, limit=12),
                }
                # `muddy_low_interval` is the loudest finding this analyser
                # produces (392 of them across the workspace) and it arrives with
                # no scale attached, so a reviewer cannot tell a real problem from
                # normal practice. Real composers write low thirds at very
                # different rates — Liszt 0.094 per bar, Beethoven 0.023,
                # Mozart 0.0077, Haydn 0.0007, and Palestrina exactly 0.0000 in
                # 60,677 bars. Judged against the piece's OWN composer, a Mozart
                # andante at 0.171 is 22x his practice while a Liszt piece at the
                # same figure is unremarkable.
                muddy = cp.by_kind().get("muddy_low_interval", 0)
                if muddy:
                    from .composition_brief import muddy_low_interval_rate

                    own = muddy_low_interval_rate(resolved)
                    n_bars = sum((ps.slot.bar_count or 0) for ps in in_scope if ps.slot) or 1
                    rate = muddy / n_bars
                    report["part_writing"]["muddy_low_intervals"] = {
                        "per_bar": round(rate, 3),
                        "composer_per_bar": round(own, 4) if own is not None else None,
                        "times_own_practice": (round(rate / own, 1) if own else None),
                    }
            except Exception as exc:  # never let an analyser break the report
                report["part_writing"] = {"error": f"{type(exc).__name__}: {exc}"}

            v = analyze_voicing(merged, style=resolved)
            report["voicing"] = {
                k: getattr(v, k)
                for k in (
                    "mean_simultaneity",
                    "simultaneity_cv",
                    "rh_notes_per_attack",
                    "lh_notes_per_attack",
                    "single_line_rh_pct",
                    "register_span",
                    "widest_hand_span",
                    "unplayable_spans",
                    "thirds_sixths_pct",
                    "observations",
                    "suggestions",
                )
            }
            report["voicing"]["texture_runs"] = [
                {"idiom": lbl, "from_bar": b0, "to_bar": b1} for lbl, b0, b1 in texture_runs(merged)
            ]
            c = analyze_cadences(
                [
                    (
                        ps.realized,
                        ((ps.slot.bar_start or 1) + (ps.slot.bar_count or 1) - 1)
                        if ps.slot
                        else None,
                        (ps.slot.key if ps.slot else None),
                        (ps.slot.cadence_target if ps.slot else None),
                    )
                    for ps in in_scope
                ]
            )
            report["cadences"] = {
                "realized": [
                    (c_.__dict__ if hasattr(c_, "__dict__") else c_) for c_ in (c.cadences or [])
                ],
                "matches_plan": c.matches_plan,
                "variety": c.variety,
                "repeated_formulas": c.repeated_formulas,
                "observations": c.observations,
                "suggestions": c.suggestions,
            }
    except Exception as exc:  # never let an analyzer crash a review
        report["voicing"] = {"error": f"{type(exc).__name__}: {exc}"}

    # Section gate (C3): the discriminator report is no longer purely advisory.
    # Egregious failures (mechanical static texture, composed-blind phrases,
    # many traits far outside the corpus spread, audible harmonic clashes or a
    # buried melody) constitute a HARD failure the pipeline must act on.
    report["section_gate"] = _section_gate(report)
    return report


@_tool
def review_context(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Everything the fresh-ears critic needs, in one call.

    The critic was assembling its own context out of `self_evaluate` plus a hand
    written music21 snippet, which meant each reviewer saw a slightly different
    slice and the prose analyzers (theme recurrence, part-writing, the engraved
    page) reached it only if the reviewer happened to know they existed.

    Returns the assembled paths, the discriminator report, and `musical_prose` —
    the same findings phrased as musical sentences rather than metrics. That
    phrasing is deliberate: a critic handed z-scores revises toward the z-score,
    which is the "metric whack-a-mole" this system explicitly rejects.

    Deliberately does NOT include the composer's rationale, sketch or brief.
    Fresh ears means the reviewer cannot rationalise what it is hearing.
    """
    report = self_evaluate(piece_id, section_id, composer)
    if "error" in report:
        return report
    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    scope = f"section-{section_id}" if section_id else "full"

    out: Dict[str, Any] = {
        "piece_id": piece_id,
        "section_id": section_id,
        "scope": scope,
        "evaluation": report,
    }
    # The composer's own review rubric. `review_rubric.json` exists in 50 of the
    # 51 compiled packs — the fingerprints this voice must exhibit and the
    # anti-patterns that mark a pastiche of it — and **nothing had ever loaded
    # it**, so every review judged style generically no matter whose style it
    # was. "Mozart's music breathes; four instruments all forte simultaneously
    # is Beethoven" is not something a generic rubric can say.
    try:
        from .composition_brief import _load_pack

        rubric = _load_pack(report.get("composer_reference", ""), "review_rubric") or {}
        checks = rubric.get("checks") if isinstance(rubric, dict) else None
        if checks:
            out["style_rubric"] = [
                {
                    "category": c.get("category"),
                    "severity": c.get("severity"),
                    "check": re.sub(r"\*\*", "", str(c.get("description", "") or "")).strip(),
                }
                for c in checks
                if isinstance(c, dict) and c.get("description")
            ]
    except Exception:
        pass

    try:
        from .musical_report import build_report, concerns_only, render_text

        mr = build_report(graph, style=report.get("composer_reference"), scope=scope)
        out["musical_prose"] = render_text(mr)
        out["concerns"] = concerns_only(mr)
    except Exception as exc:  # a prose failure must not cost the critic its data
        out["musical_prose"] = ""
        out["concerns"] = []
        out["prose_error"] = f"{type(exc).__name__}: {exc}"

    try:
        from .assembler import assemble
        from .midi_renderer import render_midi

        out["musicxml"] = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
        out["midi"] = render_midi(graph, scope=scope, output_dir=str(workspace / "cache"))
    except Exception as exc:
        out["render_error"] = f"{type(exc).__name__}: {exc}"
    return out


def _section_gate(report: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a pass/fail verdict from a self_evaluate report.

    Falsified against real scores (2026-06-20): statistical hard-fails
    (static-texture, |z|>3, musical_ear clash/buried) REJECTED real Chopin,
    Beethoven, and Bach, so no ARTISTIC check may block. Composing away from the
    briefed exemplars is a creative choice, not a defect, so ``composed_blind``
    stays advisory too. The critic's ear judges whether a section works.

    What DOES block is a physically broken score. The ear's ``error``-severity
    findings — a bar that holds more beats than its meter, a note outside the
    instrument's range — are not artistic judgements: they cannot be engraved or
    played, and every one of them has been shipped silently by this system at
    some point because nothing read the assembled file back. Those detectors
    were falsified against nine real sonatas and mazurkas first and produce zero
    errors on them (see musical_ear).
    """
    authoring = report.get("authoring", {})
    blind = authoring.get("composed_blind", 0)
    advisory: List[str] = []
    if blind:
        advisory.append(
            f"{blind} phrase(s) composed away from the briefed exemplars: "
            f"{authoring.get('composed_blind_phrases', [])} — fine if deliberate "
            f"invention; the critic judges by ear"
        )

    hard_failures: List[str] = []
    for finding in (report.get("ear", {}) or {}).get("findings", []):
        if finding.get("severity") != "error":
            continue
        hard_failures.append(f"{finding.get('detector')}: {finding.get('problem')}")
    if len(hard_failures) > 8:
        hard_failures = hard_failures[:8] + [f"... and {len(hard_failures) - 8} more"]

    # Realism findings are ADVISORY without exception — every one of them was
    # falsified against the reference corpus and several fire on canonical
    # movements (each detector's docstring states its false-positive rate). They
    # are surfaced here because they were previously computed and then read by
    # nobody, which is how a score with one cadence formula in seven of its bars
    # and no articulation at all passed every gate the system had.
    for finding in (report.get("realism", {}) or {}).get("findings", []):
        advisory.append(f"{finding.get('detector')}: {finding.get('problem')}")
    census = (report.get("realism", {}) or {}).get("notation_census") or {}
    if census:
        advisory.append(
            "notation census — "
            + ", ".join(
                f"{k}={census[k]}"
                for k in ("articulations", "slur", "hairpin", "ties", "ornaments", "dynamics")
                if k in census
            )
            + f" over {census.get('bars', '?')} bars "
            f"({census.get('marks_per_bar', '?')} marks/bar; real Mozart/Beethoven/Chopin "
            f"movements run 0.11-5.71, median 1.58)"
        )

    return {
        "passed": not hard_failures,
        "hard_failures": hard_failures,
        "advisory": advisory,
    }


# ─── Piece-vs-corpus distribution comparison (B3) ────────────────────────────


def _extract_generated_bars(path: str, composer: str, source_name: str):
    """Re-extract bar records from an assembled score, exactly as the corpus
    was extracted — so generated metrics are comparable to the corpus profile.
    """
    import music21
    from scripts.build_full_corpus import analyze_score_bars

    score = music21.converter.parse(path)
    return analyze_score_bars(score, composer, source_name)


# Above this, a z-score is reporting a degenerate corpus distribution rather
# than anything about the music. See the note in _corpus_divergence_from_path.
_Z_DEGENERATE = 8.0

#: Metrics computed over the piece's CHORD events alone — every one is a ratio
#: or a mean whose denominator is the chord count, so a mostly single-line
#: texture makes them meaningless rather than extreme.
_CHORD_SAMPLE_METRICS = frozenset(
    {
        "avg_chord_size",
        "maj_chord_ratio",
        "min_chord_ratio",
        "dim_aug_chord_ratio",
        "seventh_chord_ratio",
    }
)
#: Below this many chord events, those five are reported but not scored.
_MIN_CHORD_SAMPLE = 8


def _corpus_divergence_from_path(path: str, composer: str, scope: str) -> Dict[str, Any]:
    """Compare an assembled score's bar metrics to the composer's corpus
    distribution (corpus_profile.json) via per-metric z-scores.

    Same yardstick on both sides: ``corpus_metrics.bar_metrics`` over bar
    records. ``|z| > 2`` means the generated music sits outside the spread of
    real movements for that trait.
    """
    from .composition_brief import corpus_profile
    from .corpus_metrics import (
        bar_metrics,
        l1_distance,
        sonority_metrics,
        texture_distribution,
        zscore,
    )
    from .style_dimensions import style_fingerprint

    profile = corpus_profile(composer)
    pm = profile.get("metrics", {}) if isinstance(profile, dict) else {}
    if not pm:
        return {
            "error": f"no corpus_profile for '{composer}' — run scripts/build_corpus_profiles.py"
        }

    try:
        bars = _extract_generated_bars(path, composer, scope)
    except Exception as exc:  # parse/extract failure must not crash review
        return {"error": f"could not extract generated bars: {exc}"}
    if not bars:
        return {"error": "no bars extracted from assembled score"}

    # Score on EVERY profiled dimension — texture/rhythm (bar_metrics), plus
    # harmony/melody/rhythm-value (style_fingerprint), plus how many notes sound
    # together (sonority_metrics).
    #
    # `build_corpus_profiles` merges all THREE for the corpus side; this merged
    # only two. `chorded_attack_pct` and `mean_sonority` were therefore compared
    # against a real distribution and never computed for the piece, so
    # `gen.get(name, 0.0)` below handed them 0.0 every time. A nocturne whose
    # attacks are 100% chorded and whose mean sonority is 3.06 was reported as
    #
    #     chorded_attack_pct  value 0.0  z -15.78
    #     mean_sonority       value 0.0  z  -5.10
    #
    # the two largest deviations in the report, in every report, fabricated. The
    # module docstring calls bar_metrics "the shared yardstick run on BOTH corpus
    # bars and a generated piece"; it was shared for 37 of the 39 metrics.
    gen = {**bar_metrics(bars), **style_fingerprint(bars), **sonority_metrics(bars)}
    # How many CHORD events the piece actually has. Five of the profiled metrics
    # are computed over these alone; see `_CHORD_SAMPLE_METRICS`.
    chord_events = sum(
        1
        for bar in bars
        for hand in ("rh_display", "lh_display", "rh_inner_display", "lh_inner_display")
        for event in (bar.get(hand) or [])
        if isinstance(event, dict) and event.get("type") == "chord"
    )
    metrics: Dict[str, Any] = {}
    flags: List[Dict[str, Any]] = []
    uncomputed: List[str] = []
    for name in pm:
        stat = pm.get(name)
        if not stat:
            continue
        # Skip degenerate corpus stats (zero variance) — e.g. grace_ratio is
        # always 0 in a MIDI-derived corpus because MIDI cannot encode grace
        # notes. A z-score against sd=0 is a meaningless sentinel, not evidence
        # the generated music diverges, so it must not count toward the gate.
        if not stat.get("stdev") or stat["stdev"] <= 0:
            continue
        if name not in gen:
            # NEVER default to 0.0. A metric the corpus profile carries and the
            # piece side cannot compute is not "the piece scores zero" — it is a
            # measurement that did not happen, and scoring it produced the two
            # largest deviations in every report (chorded_attack_pct z=-15.78 on
            # a piece whose attacks are 100% chorded). Skip it and SAY so, so a
            # stale profile or a renamed metric surfaces as a gap rather than as
            # evidence about the music.
            uncomputed.append(name)
            continue
        value = gen[name]
        z = zscore(value, stat["mean"], stat["stdev"])
        # A |z| this large cannot come from a well-sampled distribution over a
        # bounded metric; it means the corpus barely varies on this measure and
        # the division is amplifying noise. A two-part invention reported
        # `min_chord_ratio z = +142.8` — it has exactly two chord events in 18
        # bars, one of them minor, so the ratio is 1/2 against a corpus mean of
        # 0.0002 and sd 0.0035. Nothing about that number is evidence, and left
        # unmarked it reads as the single worst thing about the piece.
        status = "ok" if abs(z) <= 2 else ("low" if z < 0 else "high")
        if abs(z) > _Z_DEGENERATE:
            status = "unreliable"
        elif name in _CHORD_SAMPLE_METRICS and chord_events < _MIN_CHORD_SAMPLE:
            # These five are computed over the piece's CHORD events alone, and a
            # mean or a ratio over a handful of them is not evidence. The
            # `_Z_DEGENERATE` guard above catches only the extremes: a baroque
            # piece with **two** chord events in 388 notes reported
            # `avg_chord_size z=+3.48, status "high"` and it reached the flags —
            # "your chords are too big", from two chords. Marked the same way as
            # a degenerate corpus stat, and for the same reason.
            status = "unreliable"
        metrics[name] = {
            "value": value,
            "z": z,
            "corpus_mean": stat["mean"],
            "corpus_sd": stat["stdev"],
            "status": status,
        }
        if status == "unreliable":
            if name in _CHORD_SAMPLE_METRICS and chord_events < _MIN_CHORD_SAMPLE:
                metrics[name]["note"] = (
                    f"computed over the piece's {chord_events} chord event(s) — too few "
                    f"to support a ratio or a mean, so this is not evidence about the "
                    f"piece. A mostly single-line texture is a texture, not a fault."
                )
                metrics[name]["chord_events"] = chord_events
            else:
                metrics[name]["note"] = (
                    f"corpus sd is {stat['stdev']:.4g} against mean {stat['mean']:.4g} — "
                    "this composer's corpus barely varies on this measure, so the "
                    "comparison is not evidence about the piece."
                )
        if status not in ("ok", "unreliable"):
            flags.append(
                {
                    "metric": name,
                    "z": z,
                    "value": value,
                    "corpus_mean": stat["mean"],
                    "status": status,
                }
            )

    gen_lh = texture_distribution(bars, "lh")
    corpus_lh = profile.get("lh_texture_distribution", {})
    lh_l1 = l1_distance(gen_lh, corpus_lh)
    gen_rh = texture_distribution(bars, "rh")
    corpus_rh = profile.get("rh_texture_distribution", {})
    rh_l1 = l1_distance(gen_rh, corpus_rh)
    # Judge L1 against real per-movement spread, not against 0: a single
    # movement legitimately uses a texture subset, so L1≈1 is normal.
    base = profile.get("lh_l1_baseline", {})
    lh_threshold = round(base.get("mean", 0.6) + 2 * base.get("stdev", 0.0), 3) if base else 0.6
    lh_over = lh_l1 > lh_threshold
    rh_over = bool(corpus_rh) and rh_l1 > lh_threshold  # share the calibrated band

    n_metrics = len(metrics)
    n_ok = n_metrics - len(flags)
    return {
        "composer": composer,
        "bar_count": len(bars),
        "corpus_movements": profile.get("movements_used"),
        "metrics": metrics,
        "flags": flags,
        # Metrics the profile carries that this piece could not be measured on —
        # a stale profile key or a renamed metric. Reported so the gap is
        # visible; previously each became a 0.0 and a large fabricated z.
        "uncomputed_metrics": sorted(uncomputed),
        "texture_divergence": {
            "lh_l1": lh_l1,
            "rh_l1": rh_l1,
            "threshold": lh_threshold,
            "over": lh_over or rh_over,
            "lh_over": lh_over,
            "rh_over": rh_over,
            "corpus_movement_mean": base.get("mean"),
        },
        "corpus_likeness": (
            f"{n_ok}/{n_metrics} metrics within 2σ of {composer}; "
            f"texture L1 lh={lh_l1}/rh={rh_l1} (corpus ≤{lh_threshold})"
        ),
    }


def _authoring_summary(graph, section_id: Optional[str]) -> Dict[str, Any]:
    """How much of the scope was agent-authored vs engine-realized, plus any
    composed-blind flags recorded at commit time."""
    if section_id:
        pids = graph.get_section_phrases(section_id)
    else:
        pids = list(graph.phrases.keys())
    authored = blind = engine = unrealized = 0
    blind_phrases: List[str] = []
    unrealized_phrases: List[str] = []

    def _has_notes(state) -> bool:
        layer = getattr(state, "realized", None)
        if layer is None:
            return False
        for name in (
            "principal_line",
            "bass_foundation",
            "counter_reply",
            "response_layer",
            "ornamental_surface",
            "foreground",
            "harmonic_mass",
            "rhythmic_motor",
            "color_layer",
            "punctuation",
            "countermelody",
        ):
            if getattr(layer, name, None):
                return True
        return bool(getattr(layer, "inner_voices", None))

    for pid in pids:
        st = graph.phrases.get(pid)
        if st is None:
            continue
        if getattr(st, "agent_authored", False):
            authored += 1
        elif _has_notes(st):
            engine += 1
        else:
            # NOT engine-realized: never composed at all. `else: engine += 1`
            # counted an empty phrase as one the engine had written, so a piece
            # with 3 of 9 phrases composed reported "9 phrases: 3 agent, 6
            # engine" — which reads as finished. Nothing else anywhere says a
            # section is missing, and the assembled score is simply shorter with
            # no indication of why.
            unrealized += 1
            unrealized_phrases.append(pid)
        trace = getattr(st, "context_trace", None) or {}
        if isinstance(trace, dict) and trace.get("composed_blind"):
            blind += 1
            blind_phrases.append(pid)
    return {
        "phrases": len(pids),
        "agent_authored": authored,
        "engine_realized": engine,
        "unrealized": unrealized,
        "unrealized_phrases": unrealized_phrases,
        "composed_blind": blind,
        "composed_blind_phrases": blind_phrases,
    }


@_tool
def compare_to_corpus(
    piece_id: str, section_id: Optional[str] = None, composer: Optional[str] = None
) -> Dict[str, Any]:
    """Assemble a section (or whole piece) and score it against the composer's
    real-corpus metric distribution — the post-generation divergence report.

    Returns per-metric z-scores (flagging |z|>2), LH-texture L1 divergence, and
    a one-line corpus-likeness summary. This is a DIAGNOSTIC the critic may read
    to understand where the section sits relative to the composer's real spread —
    NOT a revision driver. Out-of-band does not mean bad (real Chopin/Beethoven
    sit outside MIDI-derived bands); chasing z-scores back into band is the
    "metric whack-a-mole" the agent-creative direction rejects. Composer-specific
    (vs the generic human-sounding bands in ``self_evaluate``).
    """
    from .assembler import assemble
    from .composition_brief import resolve_composer

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    warnings: List[str] = []
    resolved = resolve_composer(graph, composer, warnings)
    scope = f"section-{section_id}" if section_id else "full"
    try:
        path = assemble(graph, scope=scope, output_dir=str(workspace / "cache"))
    except ValueError as exc:
        return {"error": str(exc)}

    report = _corpus_divergence_from_path(path, resolved, scope)
    report["piece_id"] = piece_id
    report["scope"] = scope
    report["assembled_path"] = path
    report["warnings"] = warnings
    report["authoring"] = _authoring_summary(graph, section_id)
    # An unfinished piece must SAY it is unfinished. A score assembled from 3 of
    # 9 phrases is simply shorter, with nothing in any report explaining why —
    # `warnings` came back EMPTY for exactly that piece, while `authoring` called
    # the six empty phrases "engine_realized". Everything measured below is a
    # description of the part that exists, which is misleading on its own.
    unrealized = report["authoring"].get("unrealized") or 0
    if unrealized:
        total = report["authoring"].get("phrases") or 0
        named = ", ".join(report["authoring"].get("unrealized_phrases", [])[:8])
        warnings.append(
            f"INCOMPLETE: {unrealized} of {total} phrases have no notes at all "
            f"({named}). Every measurement in this report describes only the "
            f"phrases that exist."
        )
    return report


# ─── Candidate Panel Support ─────────────────────────────────────────────────
#
# Structurally load-bearing phrases (theme statements, climaxes,
# recapitulation entries, final cadences) can be composed by 2-3
# candidate-composer subagents through different lenses. Candidates are
# stored OUTSIDE graph.phrases (so they never assemble into the score),
# previewed as standalone MusicXML for the judge, and the winner is
# promoted to the canonical phrase.


def _candidates_dir(piece_id: str) -> Path:
    d = _WORKSPACE / piece_id / "candidates"
    d.mkdir(parents=True, exist_ok=True)
    return d


@_tool
def commit_candidate_phrase(
    piece_id: str,
    phrase_id: str,
    lens: str,
    bars: Optional[List[Dict[str, Any]]] = None,
    layer_ir: Optional[Dict[str, Any]] = None,
    allow: Optional[List[Dict[str, str]]] = None,
    composer: Optional[str] = None,
) -> Dict[str, Any]:
    """Commit one PANEL CANDIDATE for a phrase, under a lens label.

    Validates and runs the same quality gate as a real commit, but stores
    the result in workspace/<piece>/candidates/ (never in graph.phrases),
    with a standalone MusicXML preview for the judge. Promote the winner
    with ``promote_candidate``.
    """
    bars = _as_list(bars, "bars")
    allow = _as_list(allow, "allow")
    from .commit_gate import run_commit_gate
    from .direct_compose import compose_phrase
    from .piece_graph import _deep_serialize
    from .validator import validate_layer_ir

    graph = _load_graph(piece_id)
    if phrase_id not in graph.phrases:
        return {"error": f"Unknown phrase_id: {phrase_id}"}
    slot = graph.phrases[phrase_id].slot
    if not slot:
        return {"error": "Phrase has no slot"}

    if bars:
        if len(bars) != slot.bar_count:
            return {
                "error": "bar_count_mismatch",
                "expected_bars": slot.bar_count,
                "got": len(bars),
                "hint": (
                    f"Write exactly {slot.bar_count} bar dicts. A pickup bar occupies "
                    f"the phrase's first bar; mark it {{'pickup': True}} rather than "
                    f"adding an extra dict."
                ),
            }
        layer = compose_phrase(
            bars,
            key=slot.key,
            bar_start=slot.bar_start,
            phrase_id=phrase_id,
            meter=slot.meter,
            instrumentation=_piece_instrumentation(graph),
        )
    elif layer_ir is not None:
        layer = load_layer_ir_from_dict(layer_ir)
        layer.phrase_id = phrase_id
        if not layer.key:
            layer.key = slot.key
    else:
        return {"error": "Provide bars or layer_ir"}

    report = validate_layer_ir(layer, _physical_constraints(graph))
    if not report.passed:
        return {
            "ok": False,
            "error": "validation_failed",
            "issues": [f"{i.severity}: {i.message}" for i in report.issues[:20]],
        }

    gate = run_commit_gate(graph, phrase_id, layer, allow=allow, composer=composer)
    if not gate.passed:
        return {
            "ok": False,
            "error": "quality_gate_blocked",
            "blocking": [d.to_dict() for d in gate.blocking],
            "warnings": [d.to_dict() for d in gate.warnings],
            "hint": "Same gate rules as a real commit — revise the "
            "flagged bars (max 3 attempts) or waive with "
            "allow=[{'check':..,'reason':..}].",
        }

    # Engrave the candidate too, so the judge compares what will actually ship.
    # The panel judge picks a winner from a rendered preview; an unengraved
    # preview has no articulation, no phrasing and no pedal in it, so the judge
    # was choosing between three MIDI dumps and only the winner was then
    # engraved on promotion. The pass is non-destructive and idempotent — it
    # runs again on promotion and finds nothing left blank.
    engraving = _engrave_phrase(graph, phrase_id, layer, composer)

    cand_id = f"{phrase_id}__cand_{lens}"
    cand_path = _candidates_dir(piece_id) / f"{cand_id}.json"
    record = {
        "phrase_id": phrase_id,
        "lens": lens,
        "layer_ir": _deep_serialize(layer),
        "gate": {"warnings": [d.to_dict() for d in gate.warnings], "overrides": gate.overrides},
        "engraving": engraving,
        "created_at": _now_iso(),
    }
    with open(cand_path, "w") as f:
        json.dump(record, f, indent=1)

    preview_path = ""
    try:
        preview_path = _render_layer_preview(
            layer, _candidates_dir(piece_id) / f"{cand_id}.musicxml", tempo_bpm=slot.tempo_bpm
        )
    except Exception as exc:  # preview is best-effort
        preview_path = f"(preview failed: {exc})"

    return {
        "ok": True,
        "candidate_id": cand_id,
        "lens": lens,
        "path": str(cand_path),
        "preview": preview_path,
        "gate": record["gate"],
    }


def _render_layer_preview(layer: LayerIR, out_path: Path, tempo_bpm: int = 120) -> str:
    """Render a single LayerIR as a standalone MusicXML preview."""
    import music21

    from .assembler import _build_ensemble_score, _build_piano_score
    from .models import is_keyboard
    from .music_io import layer_ir_to_event_ir

    events = layer_ir_to_event_ir(layer)
    # Re-base bars so the preview starts at bar 1
    if events:
        shift = min(e.bar for e in events) - 1
        for e in events:
            e.bar -= shift
    score = music21.stream.Score()
    # A candidate for a MOTET was previewed as a piano grand staff: this called
    # `_build_piano_score` whatever the piece was scored for. The judge compares
    # candidates against each other, so a shared wrong instrument does not bias
    # the comparison — but it is still the wrong score, and a reviewer reading
    # one cannot see the forces the phrase was written for.
    if is_keyboard(layer.instrumentation):
        score = _build_piano_score(score, events, layer.key, layer.meter, tempo_bpm)
    else:
        score = _build_ensemble_score(
            score,
            events,
            layer.key,
            layer.meter,
            tempo_bpm,
            instrumentation=layer.instrumentation,
        )
    score.write("musicxml", fp=str(out_path))
    return str(out_path)


@_tool
def list_phrase_candidates(piece_id: str, phrase_id: str) -> Dict[str, Any]:
    """All committed panel candidates for a phrase, with previews.

    An empty list means "this phrase has no candidates yet", which is a normal
    answer. It must not also mean "this piece does not exist" — the two are
    indistinguishable to a caller and the second is a typo worth reporting.
    """
    graph = _load_graph(piece_id)  # raises _MissingPiece; @_tool returns it
    if phrase_id not in graph.phrases:
        return {
            "error": f"Unknown phrase '{phrase_id}' in '{piece_id}'",
            "phrases": sorted(graph.phrases)[:20],
        }
    out: Dict[str, Any] = {"phrase_id": phrase_id, "candidates": []}
    for path in sorted(_candidates_dir(piece_id).glob(f"{phrase_id}__cand_*.json")):
        try:
            with open(path) as f:
                record = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        preview = path.with_suffix(".musicxml")
        out["candidates"].append(
            {
                "candidate_id": path.stem,
                "lens": record.get("lens"),
                "path": str(path),
                "preview": str(preview) if preview.exists() else None,
                "gate_warnings": [
                    w.get("check") for w in record.get("gate", {}).get("warnings", [])
                ],
            }
        )
    return out


@_tool
def promote_candidate(piece_id: str, phrase_id: str, lens: str) -> Dict[str, Any]:
    """Promote the winning panel candidate to the canonical phrase.

    Re-runs the gate (cheap; the candidate already passed it) and commits
    as agent-authored. Loser files stay on disk for the audit trail.
    """
    cand_path = _candidates_dir(piece_id) / f"{phrase_id}__cand_{lens}.json"
    if not cand_path.exists():
        listing = list_phrase_candidates(piece_id, phrase_id)
        if "error" in listing:
            # The listing failed for its own reason (usually: no such piece).
            # Reaching into its "candidates" key raised a bare KeyError on top
            # of a perfectly good error message.
            return listing
        return {
            "error": f"No candidate '{lens}' for {phrase_id}",
            "available": [c["lens"] for c in listing.get("candidates", [])],
        }
    with open(cand_path) as f:
        record = json.load(f)

    result = commit_agent_phrase_layer_ir(
        piece_id,
        phrase_id,
        record["layer_ir"],
        allow=[
            {**ov, "reason": ov.get("reason", "panel candidate override")}
            for ov in record.get("gate", {}).get("overrides", [])
        ]
        or None,
    )
    if result.get("ok"):
        result["promoted_from"] = f"{phrase_id}__cand_{lens}"
        workspace = _WORKSPACE / piece_id
        graph = _load_graph(piece_id)
        from .models import RevisionEntry

        graph.revision_history.append(
            RevisionEntry(
                timestamp=_now_iso(),
                skill="candidate_panel",
                path=f"phrases.{phrase_id}",
                operation=f"promote:{lens}",
                reason=f"judge selected '{lens}' lens candidate",
            )
        )
        graph.save(str(workspace / "piece_graph.json"))
    return result


# Default lock policy per score-to-score mode — what "keep the source's X" means
# for each. A LockPolicy of all zeros says "preserve nothing", which for a
# variation set or a style transfer is the one thing it cannot mean.
_MODE_LOCKS = {
    "variation": {
        "principal_melody": 0.8,
        "form_layout": 0.9,
        "phrase_count": 0.9,
        "cadence_hits": 0.7,
        "key_scheme": 0.8,
    },
    "style_transfer": {
        "principal_melody": 0.6,
        "form_layout": 0.9,
        "phrase_count": 0.9,
        "cadence_hits": 0.5,
        "key_scheme": 0.7,
    },
    "continue_piece": {
        "principal_melody": 0.3,
        "form_layout": 0.2,
        "key_scheme": 0.6,
    },
    "orchestrate": {
        "principal_melody": 0.95,
        "bass_foundation": 0.9,
        "cadence_hits": 0.9,
        "form_layout": 1.0,
        "phrase_count": 1.0,
        "key_scheme": 1.0,
    },
    "reduce_to_piano": {
        "principal_melody": 0.9,
        "bass_foundation": 0.8,
        "cadence_hits": 0.8,
        "form_layout": 1.0,
        "phrase_count": 1.0,
        "key_scheme": 1.0,
    },
}


@_tool
def load_source_score(
    piece_id: str,
    source_path: Optional[str] = None,
    segment_bars: int = 4,
) -> Dict[str, Any]:
    """Read a source score into the PieceGraph as phrases.

    `variation`, `style_transfer` and `continue_piece` are three of the six
    composition modes this system documents, and **none of them could read its
    source**. `init_workspace` stored the path on the contract, the mode was
    recorded on the graph, and nothing anywhere parsed the score — so a
    variation set had no theme, a style transfer had nothing to restyle, and a
    continuation had nothing to continue from. The lock policy sat at all
    zeros, which for those modes means "preserve nothing" — the one thing they
    cannot mean.

    Segments the source into phrases of ``segment_bars`` bars. That is a plain
    division, not phrase detection: it gives the modes real material to work
    from and honest bar numbers, and where the source's own phrasing matters,
    /w-plan can re-slice it. Phrases are marked `agent_authored=False` and
    `salience="source"` so nothing downstream mistakes them for composed music.
    """
    from .models import LayerEvent, PhraseState
    from .music_io import parse_musicxml_to_events

    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"
    if not graph_path.exists():
        return {"error": f"No workspace for '{piece_id}' — run init_workspace first"}
    graph = PieceGraph.load(str(graph_path))

    path = source_path or getattr(getattr(graph.contract, "source", None), "path", "")
    if not path:
        return {
            "error": "No source score",
            "hint": (
                "Pass source_path, or set it at init_workspace time with "
                "params={'source_path': '<file>'}."
            ),
        }
    src = Path(path)
    if not src.exists():
        return {"error": f"Source score not found: {path}"}

    try:
        events, instruments = parse_musicxml_to_events(str(src))
    except Exception as exc:
        return {"error": f"Could not read {path}: {type(exc).__name__}: {exc}"}
    if not events:
        return {"error": f"No notes in {path}"}

    key = _source_key(src) or "C"
    meter = _source_meter(src) or (4, 4)
    tempo = _source_tempo(src) or 100

    # The lowest-sounding part is the bass, everything else the upper texture —
    # the same split the piano path uses, applied to whatever the source has.
    def _low(ev) -> int:
        from .pitch import pitch_to_midi

        pitches = ev["pitch"] if isinstance(ev["pitch"], list) else [ev["pitch"]]
        vals = []
        for pitch in pitches:
            try:
                vals.append(pitch_to_midi(pitch))
            except (ValueError, KeyError, TypeError):
                pass
        return min(vals) if vals else 60

    sounding = [e for e in events if e["pitch"] != "rest"]
    if not sounding:
        return {"error": f"No sounding notes in {path}"}
    # Which part is the bass, by where it actually sits — not by its name. A
    # piano grand staff is two parts both called "Piano", and a source whose
    # hands both land in `principal_line` has no bass line at all for anything
    # downstream to lock, vary or reduce.
    by_inst: Dict[str, int] = {}
    for e in sounding:
        pitch_low = _low(e)
        inst = e["instrument"]
        by_inst[inst] = min(by_inst.get(inst, pitch_low), pitch_low)
    bass_inst = min(by_inst, key=by_inst.get) if len(by_inst) > 1 else None
    if bass_inst is None and sounding:
        # A single part carrying both hands: split at the median pitch.
        pitches = sorted(_low(e) for e in sounding)
        split_at = pitches[len(pitches) // 2]
        bass_inst = None  # handled per-event below
    else:
        split_at = None

    bars = sorted({e["bar"] for e in events if e.get("bar")})
    first_bar, last_bar = bars[0], bars[-1]
    n_phrases = 0
    for start in range(first_bar, last_bar + 1, max(1, segment_bars)):
        end = min(start + segment_bars - 1, last_bar)
        chunk = [e for e in events if start <= e.get("bar", 0) <= end]
        if not any(e["pitch"] != "rest" for e in chunk):
            continue
        layer = LayerIR(
            phrase_id=f"src_p{n_phrases + 1}",
            instrumentation="solo_piano",
            key=key,
            meter=meter,
            bar_count=end - start + 1,
        )
        for e in chunk:
            if bass_inst is not None:
                is_bass = e["instrument"] == bass_inst
            else:
                is_bass = split_at is not None and e["pitch"] != "rest" and _low(e) < split_at
            target = layer.bass_foundation if is_bass else layer.principal_line
            target.append(
                LayerEvent(
                    bar=e["bar"],
                    beat=e["beat"],
                    pitch=e["pitch"],
                    duration=e["duration"],
                    dynamic=e.get("dynamic"),
                    source_layer="source",
                )
            )
        _repair_engine_surface(layer, meter)
        n_phrases += 1
        pid = layer.phrase_id
        graph.phrases[pid] = PhraseState(
            slot=PhraseSlot(
                phrase_id=pid,
                section_id="m1_source",
                bar_start=start,
                bar_count=end - start + 1,
                key=key,
                meter=meter,
                tempo_bpm=tempo,
            ),
            realized=layer,
            agent_authored=False,
            salience="source",
        )

    # A mode that preserves nothing is not that mode.
    defaults = _MODE_LOCKS.get(getattr(graph, "mode", "") or "", {})
    applied = {}
    if defaults and not any(vars(graph.contract.locks).values()):
        for field_name, value in defaults.items():
            if hasattr(graph.contract.locks, field_name):
                setattr(graph.contract.locks, field_name, value)
                applied[field_name] = value

    if not getattr(getattr(graph.contract, "source", None), "path", ""):
        from .models import SourceReference

        graph.contract.source = SourceReference(path=str(src))
    # `continue_piece` is documented as the mode where "the ledger carries
    # forward" — the promises and debts the earlier music left open. It carried
    # nothing: `load_source_score` reads a SCORE FILE, which has no ledger, so
    # the mode's whole differentiator did not happen. When the source is another
    # workspace's output — which is what continuing a piece means — that piece's
    # graph is right there beside it.
    if str(getattr(graph, "mode", "")) == "continue_piece":
        carried = 0
        try:
            src_graph = Path(path).resolve().parent.parent / "piece_graph.json"
            if src_graph.exists():
                prior = PieceGraph.load(str(src_graph))
                led = getattr(prior, "cross_scale_ledger", None)
                if isinstance(led, dict) and led:
                    graph.cross_scale_ledger = led
                    exps = led.get("expectations")
                    carried = len(exps) if isinstance(exps, list) else 0
        except Exception:
            carried = 0
        result_extra = {"ledger_expectations_carried": carried}
    else:
        result_extra = {}

    graph.save(str(graph_path))

    return {
        "ok": True,
        "source": str(src),
        "mode": graph.mode,
        "instruments": instruments,
        "bars": last_bar - first_bar + 1,
        "phrases_loaded": n_phrases,
        "key": key,
        "meter": list(meter),
        "tempo_bpm": tempo,
        "locks_applied": applied,
        **result_extra,
        "hint": (
            "Source phrases are marked salience='source' and agent_authored=False. "
            "Plan over them with /w-plan, then compose against them — the lock "
            "policy says how much of each must survive."
        ),
    }


def _thin_carried_dynamics(layer) -> int:
    """Collapse a dynamic repeated on consecutive events of one layer.

    Returns how many marks were removed. Only an UNBROKEN run collapses: real
    scores restate a dynamic 36.1% of the time, and a reminder after a gap is
    correct engraving, not spam.
    """
    removed = 0
    for name in (
        "principal_line",
        "bass_foundation",
        "response_layer",
        "counter_reply",
        "ornamental_surface",
        "inner_voices",
    ):
        events = getattr(layer, name, None) or []
        last = None
        for e in sorted(events, key=lambda x: (x.bar, x.beat)):
            dyn = getattr(e, "dynamic", None)
            if dyn is None:
                continue
            if dyn == last:
                e.dynamic = None
                removed += 1
            else:
                last = dyn
    return removed


@_tool
def reduce_to_piano(
    piece_id: str,
    source_path: str,
    mode: str = "playable_reduction",
    key: Optional[str] = None,
    meter: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """Reduce an orchestral score to a playable piano texture (SABRE).

    `reduce_to_piano` is one of the six composition modes this system
    documents, and it had **no entry point**: `SABRE.reduce_to_piano` existed,
    the orchestrator skill described the mode, and no tool exposed it, so the
    mode was unreachable from any skill.

    Everything a generator produces is repaired against the same physical rules
    before it is committed — one hand cannot play two notes at once, a bar
    cannot hold more beats than its meter — and the repairs are reported rather
    than absorbed. SABRE's own output needs it: reducing a 14-bar 3/4 section
    produced 32 meter violations, because the reducer builds its LayerIR at a
    hard-coded 4/4 and takes no meter argument.
    """
    from .music_io import parse_musicxml_to_events
    from .sabre import SABRE

    workspace = _WORKSPACE / piece_id
    graph_path = workspace / "piece_graph.json"
    if not graph_path.exists():
        return {"error": f"No workspace for '{piece_id}' — run init_workspace first"}
    graph = PieceGraph.load(str(graph_path))

    src = Path(source_path)
    if not src.exists():
        return {"error": f"Source score not found: {source_path}"}
    try:
        events, instruments = parse_musicxml_to_events(str(src))
    except Exception as exc:
        return {"error": f"Could not read {source_path}: {type(exc).__name__}: {exc}"}
    if not events:
        return {"error": f"No events in {source_path}"}

    # The source's own key and meter, unless the caller overrides. Reducing a
    # 3/4 score into a 4/4 container mis-bars every bar of it.
    resolved_key = key or _source_key(src) or "C"
    resolved_meter = tuple(meter) if meter else (_source_meter(src) or (4, 4))

    # The reducer takes the meter now, so the LayerIR is built in the source's
    # own meter rather than assembled at 4/4 and corrected afterwards.
    layer = SABRE().reduce_to_piano(
        events,
        instruments=instruments,
        mode=mode,
        key=resolved_key,
        meter=resolved_meter,
    )
    layer.key = resolved_key
    layer.meter = resolved_meter
    layer.instrumentation = "solo_piano"

    repairs = _repair_engine_surface(layer, resolved_meter)
    if repairs:
        _LOG.warning("reduction repairs for %s: %s", piece_id, repairs)

    bars = sorted({e.bar for e in (layer.principal_line or []) + (layer.bass_foundation or [])})
    if not bars:
        return {"error": "Reduction produced no notes"}
    layer.bar_count = bars[-1] - bars[0] + 1

    phrase_id = f"reduction_{src.stem}"[:64]
    slot = PhraseSlot(
        phrase_id=phrase_id,
        section_id="m1_reduction",
        bar_start=bars[0],
        bar_count=layer.bar_count,
        key=resolved_key,
        meter=resolved_meter,
        tempo_bpm=_source_tempo(src) or 100,
    )
    from .models import PhraseState

    # A reduction inherits the source's dynamic on EVERY note it carries down,
    # so a Clara Schumann polonaise holding 7 written dynamics came out with 313
    # of them — 296 printed, 3.70 per bar, against a real per-part range of
    # 0.03-0.85 (median 0.24) measured over 212 parts. That is 4.4x the loudest
    # real part, and it is the reduction shouting a marking at the player on
    # every beat.
    #
    # Thinned to CHANGES, which is where a dynamic is written. Note what this
    # deliberately does not do: 36.1% of real dynamics restate the level already
    # in force (a reminder after a long gap is normal engraving), so this only
    # collapses an unbroken run within one layer, never a restatement after
    # something else intervened.
    _thin_carried_dynamics(layer)
    graph.phrases[phrase_id] = PhraseState(slot=slot, realized=layer, agent_authored=False)
    graph.save(str(graph_path))

    return {
        "ok": True,
        "phrase_id": phrase_id,
        "source": str(src),
        "instruments_reduced": len(instruments),
        "key": resolved_key,
        "meter": list(resolved_meter),
        "bars": layer.bar_count,
        "notes": len(layer.principal_line or []) + len(layer.bass_foundation or []),
        "repairs": repairs,
        "hint": (
            "Review for playability, then assemble. A reduction is a first draft: "
            "the reducer packs what fits, it does not decide what matters."
        ),
    }


def _source_key(path: Path) -> Optional[str]:
    """The key a score is written in, from its own key signature."""
    try:
        import music21

        score = music21.converter.parse(str(path))
        ks = next(iter(score.recurse().getElementsByClass("KeySignature")), None)
        if ks is None:
            return None
        tonic = ks.asKey()
        return f"{tonic.tonic.name} {tonic.mode}"
    except Exception:
        return None


def _source_meter(path: Path) -> Optional[Tuple[int, int]]:
    """The meter a score is written in — NOT an assumed 4/4."""
    try:
        import music21

        score = music21.converter.parse(str(path))
        ts = next(iter(score.recurse().getElementsByClass("TimeSignature")), None)
        return (int(ts.numerator), int(ts.denominator)) if ts is not None else None
    except Exception:
        return None


def _source_tempo(path: Path) -> Optional[int]:
    try:
        import music21

        score = music21.converter.parse(str(path))
        mm = next(iter(score.recurse().getElementsByClass("MetronomeMark")), None)
        return int(mm.number) if mm is not None and mm.number else None
    except Exception:
        return None


#: Words in a profile's role description that name what the part DOES.
_MELODY_WORDS = ("melod", "leader", "soprano", "principal", "tune", "sings", "lead ")
_BASS_WORDS = ("bass", "root", "foundation", "anchor", "lowest", "pedal")


def _style_role_assignments(roles, ensemble) -> Dict[str, str]:
    """Which INSTRUMENT this style gives the melody and the bass.

    `plan_orchestration` reads `style_roles["melody"]` and `style_roles["bass"]`
    and expects an instrument NAME. The packs hold the opposite shape —
    instrument name -> role description — so handing the raw dict over produced
    `None` for melody and, for Chopin, an `InstrumentRole` OBJECT for bass,
    which then failed an `in ensemble` test and fell back. It never raised and
    never assigned anything: the style's own scoring preferences reached the
    planner as silence.

    Only an instrument actually in the ensemble is proposed; anything else is
    left to the planner's own choice.
    """
    available = {str(name).lower() for name in (ensemble or [])}
    out: Dict[str, str] = {}
    for name, role in (roles or {}).items():
        # What the style says this instrument DOES — never what it is CALLED.
        # The instrument's own name used to be part of the matched text, and
        # `_BASS_WORDS` contains "bass", which is a substring of **bassoon**. So
        # any ensemble with a bassoon in it got `{"bass": "bassoon"}`, the cello
        # was left with nothing, and the planner's last pass ("anything still
        # silent doubles the melody") handed the cello the TUNE. Measured on a
        # real orchestration off this system: cello 63-74 against viola 48-60 —
        # the cello playing entirely above the viola for the whole movement.
        # `bass_clarinet` and `bass_trombone` collide the same way.
        described = " ".join(
            str(v).lower()
            for v in (
                getattr(role, "role", ""),
                getattr(role, "characteristic_usage", ""),
            )
            if v
        )
        key = str(getattr(role, "name", name) or name).lower().replace(" ", "_")
        if key not in available:
            continue
        if "melody" not in out and any(w in described for w in _MELODY_WORDS):
            out["melody"] = key
        elif "bass" not in out and any(w in described for w in _BASS_WORDS):
            out["bass"] = key
    return out


@_tool
def orchestrate_section(
    piece_id: str,
    section_id: str,
    target_ensemble: Optional[List[str]] = None,
    planner: str = "idiomatic",
    soloist: str = "",
) -> Dict[str, Any]:
    """Expand a section's committed piano-core LayerIR into orchestral parts.

    Piano-core-first workflow for concertos/symphonies: compose and review
    the musical substance at the keyboard, then expand by role.

    planner="idiomatic" (default) uses orchestration_planner — register-
    aware assignment with climax doublings, divided inner voices, wind
    pads, range clamping. planner="sabre" falls back to the simple 3-role
    expansion. Parts go to workspace/<piece>/orchestration/<section>.json;
    render to score with ``assemble_orchestration``.
    """
    target_ensemble = _as_list(target_ensemble, "target_ensemble")
    from .direct_compose import merge_phrases

    workspace = _WORKSPACE / piece_id
    graph = _load_graph(piece_id)
    phrase_ids = graph.get_section_phrases(section_id)
    if not phrase_ids:
        return {"error": f"Unknown section '{section_id}'"}

    realized = [
        graph.phrases[pid].realized
        for pid in phrase_ids
        if pid in graph.phrases and graph.phrases[pid].realized
    ]
    if not realized:
        return {"error": f"No realized phrases in section '{section_id}'"}

    first_slot = graph.phrases[phrase_ids[0]].slot
    key = first_slot.key if first_slot else "C"
    meter = first_slot.meter if first_slot else (4, 4)

    if not target_ensemble:
        target = getattr(graph.contract, "target", None)
        instrumentation = getattr(target, "instrumentation", "orchestra")
        default_ensembles = {
            "orchestra": [
                "flute",
                "oboe",
                "clarinet",
                "bassoon",
                "horn",
                "violin_1",
                "violin_2",
                "viola",
                "cello",
                "contrabass",
            ],
            "string_quartet": ["violin_1", "violin_2", "viola", "cello"],
            "string_orchestra": ["violin_1", "violin_2", "viola", "cello", "contrabass"],
            # A choir was not in this table at all, so a choral piece was
            # orchestrated onto flute, oboe, clarinet, bassoon and horn.
            "choir": ["soprano", "alto", "tenor", "bass"],
            "string_quintet": ["violin_1", "violin_2", "viola", "cello", "contrabass"],
            "string_trio": ["violin_1", "viola", "cello"],
        }
        # The keys are `string_quartet`; a contract carries "string quartet",
        # with a space, and this fell through to the ORCHESTRA roster — the same
        # two-spelling miss as the pedal and hand-span whitelists, with a
        # plausible-looking result that is simply the wrong ensemble.
        from .models import is_string_ensemble, is_vocal

        normalized = str(instrumentation or "").strip().lower().replace("-", "_").replace(" ", "_")
        if normalized not in default_ensembles:
            if is_vocal(normalized):
                normalized = "choir"
            elif is_string_ensemble(normalized):
                normalized = "string_quartet" if "quartet" in normalized else "string_orchestra"
        target_ensemble = default_ensembles.get(normalized, default_ensembles["orchestra"])

    merged = merge_phrases(realized, key=key, meter=meter, piece_id=f"{piece_id}:{section_id}")
    merged.meter = meter

    if planner == "sabre":
        from .sabre import SABRE

        parts = SABRE().orchestrate_from_piano(merged, target_ensemble, key=key)
    else:
        from .orchestration_planner import plan_orchestration

        # `orchestration_roles` is a field of StyleDNA, which StyleProgram
        # WRAPS — so `getattr(program, "orchestration_roles", None)` read it off
        # the wrong object and returned None every time, and the planner's
        # generic fallback took over with nothing to say it had. Try the DNA the
        # program carries, then the graph's own.
        style_roles = None
        for holder in (
            getattr(getattr(graph, "style_program", None), "dna", None),
            getattr(graph, "style_dna", None),
        ):
            roles = getattr(holder, "orchestration_roles", None)
            if roles:
                style_roles = _style_role_assignments(roles, target_ensemble)
                break
        parts = plan_orchestration(merged, target_ensemble, key=key, style_roles=style_roles)

    # A CONCERTO keeps its soloist. `orchestrate_section` is documented as the
    # concerto workflow — "piano-core first, then orchestrate_section" — but the
    # planner is a role distributor with no notion of a solo part, so naming
    # `piano` in the ensemble got it the melody line alone: 42 notes between G5
    # and C7, one staff, no left hand. That is a flute part on a piano staff.
    #
    # With a soloist named, that part keeps the piano core entire — both hands,
    # every event — and the orchestra is planned around it.
    if soloist:
        solo_events = []
        for name in (
            "principal_line",
            "counter_reply",
            "ornamental_surface",
            "bass_foundation",
            "response_layer",
        ):
            for e in getattr(merged, name, []) or []:
                if getattr(e, "pitch", None) == "rest":
                    continue
                solo_events.append(
                    {
                        "bar": e.bar,
                        "beat": float(e.beat),
                        "pitch": e.pitch,
                        "duration": e.duration,
                        "role": getattr(e, "role", ""),
                        "staff": "treble"
                        if name in ("principal_line", "counter_reply", "ornamental_surface")
                        else "bass",
                    }
                )
        solo_events.sort(key=lambda d: (d["bar"], d["beat"]))
        # TWO STAVES. The ensemble assembler gives each part one staff, so a
        # soloist emitted as a single part had its hands overlapping in time and
        # the repair pass trimmed 42 events — bar 1 came out as the left hand
        # alone. A concerto soloist is notated on two staves; emit it that way.
        upper = [e for e in solo_events if e["staff"] == "treble"]
        lower = [e for e in solo_events if e["staff"] == "bass"]
        parts[soloist] = upper
        added = [soloist]
        if lower:
            parts[f"{soloist}_lh"] = lower
            added.append(f"{soloist}_lh")
        target_ensemble = [n for n in added if n not in target_ensemble] + [
            n for n in target_ensemble if n not in added
        ]

    out_dir = workspace / "orchestration"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{section_id}.json"
    with open(out_path, "w") as f:
        json.dump(
            {
                "section_id": section_id,
                "ensemble": target_ensemble,
                "key": key,
                "meter": list(meter),
                "planner": planner,
                "parts": parts,
            },
            f,
            indent=1,
        )

    graph.output_paths[f"orchestration:{section_id}"] = str(out_path)
    graph.save(str(workspace / "piece_graph.json"))

    return {
        "ok": True,
        "section_id": section_id,
        "ensemble": target_ensemble,
        "planner": planner,
        "part_event_counts": {k: len(v) for k, v in parts.items()},
        "path": str(out_path),
    }


@_tool
def assemble_orchestration(piece_id: str, section_id: str) -> Dict[str, Any]:
    """Render orchestrated parts (from orchestrate_section) to MusicXML."""
    import music21

    from .assembler import _build_ensemble_score
    from .models import EventIR

    # Check the PIECE before the orchestration. Reporting "run
    # orchestrate_section first" for a piece that does not exist points at the
    # wrong problem: the id is a typo, and no amount of orchestrating will help.
    _load_graph(piece_id)
    workspace = _WORKSPACE / piece_id
    parts_path = workspace / "orchestration" / f"{section_id}.json"
    if not parts_path.exists():
        return {"error": f"No orchestration for '{section_id}' — run orchestrate_section first"}
    with open(parts_path) as f:
        data = json.load(f)

    # Read EVERY field the writer stored, driven off EventIR rather than a
    # hand-listed seven. Naming the fields here is how the orchestral path lost
    # `ornament`: an appoggiatura arrived as a plain eighth note, took real time,
    # collided with the note it decorates and left the bar summing to 3.5 beats
    # of a 3/4. A field the writer starts emitting is now picked up for free.
    known = {f.name for f in _dataclass_fields(EventIR)}
    events: List[EventIR] = []
    for inst, inst_events in data.get("parts", {}).items():
        for ev in inst_events:
            if not isinstance(ev, dict) or "pitch" not in ev:
                continue
            fields_present = {k: v for k, v in ev.items() if k in known}
            fields_present["staff"] = inst
            events.append(EventIR(**fields_present))
    if not events:
        return {"error": "Orchestration has no events"}

    # Repair defensively, per instrument. The planner is a separate generator
    # and the same physical rules apply to it: one instrument cannot play two
    # notes at once, and a bar cannot hold more beats than its meter. Reported,
    # never absorbed — a repair here means the planner produced something
    # unplayable and that is worth seeing.
    orch_repairs: Dict[str, Dict[str, int]] = {}
    _orch_meter = tuple(data.get("meter") or (4, 4))
    for inst in sorted({e.staff for e in events}):
        part_events = [e for e in events if e.staff == inst]
        holder = LayerIR(phrase_id=inst, key=data.get("key", "C"), meter=_orch_meter)
        holder.principal_line = part_events
        fixed = _repair_engine_surface(holder, _orch_meter, allow_chords=False)
        if fixed:
            orch_repairs[inst] = fixed
        events = [e for e in events if e.staff != inst] + list(holder.principal_line)
    if orch_repairs:
        _LOG.warning("orchestration repairs in %s: %s", section_id, orch_repairs)
    # How many pitches the plan asked for, counted BEFORE the repair, so the
    # return value can say whether any were lost. A trimmed overlap can trim a
    # note to nothing, and this reported only into the log — an agent reading
    # the tool result saw a clean `ok: True` for a part the planner had made
    # unplayable. The viola of a real orchestrated section arrived with an inner
    # line and a wind pad written into the same voice, and two of its pitches
    # went silently.
    planned_pitches = 0
    for part_events in (data.get("parts") or {}).values():
        for ev in part_events:
            pitch = ev.get("pitch")
            planned_pitches += len(pitch) if isinstance(pitch, list) else 1

    # Re-base bars so the score starts at bar 1
    shift = min(e.bar for e in events) - 1
    if shift:
        for e in events:
            e.bar -= shift
    events.sort(key=lambda e: (e.bar, e.beat, e.staff, e.voice))

    meter = tuple(data.get("meter", [4, 4]))
    score = music21.stream.Score()
    # The full ensemble, so an instrument that is tacet in this section still
    # gets its staff and its rests.
    score = _build_ensemble_score(
        score,
        events,
        data.get("key", "C"),
        meter,
        120,
        ensemble=[str(x) for x in (data.get("ensemble") or [])],
    )
    out_path = workspace / "output" / f"{piece_id}_{section_id}_orch.musicxml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(out_path))
    # Report the parts in the order they are IN THE FILE. Sorting them here made
    # the tool answer "bassoon, cello, clarinet, contrabass, flute…" about a
    # score whose parts are correctly flute, oboe, clarinet, bassoon, horn,
    # strings — so an agent checking its own output reads an alphabetical list
    # and concludes the score order is broken when it is not.
    written_pitches = sum(len(n.pitches) for n in score.recurse().notes)
    result = {
        "ok": True,
        "path": str(out_path),
        "parts": [p.partName or p.id for p in score.parts],
        "notes_planned": planned_pitches,
        "notes_written": written_pitches,
    }
    if orch_repairs:
        result["repairs"] = orch_repairs
    if written_pitches < planned_pitches:
        result["warning"] = (
            f"{planned_pitches - written_pitches} planned pitch(es) did not reach "
            f"the score — the planner wrote overlapping notes into one part's "
            f"single voice and the repair trimmed them away. See `repairs`."
        )
    return result
