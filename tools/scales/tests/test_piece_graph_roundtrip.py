"""Save/load round-trip: no model may lose a field on the way to disk.

Hand-enumerated loaders are this project's most productive bug source, and the
failure is always silent. The loader names the fields it knows about; a field
added to the model later is simply absent from the reconstructed object, so the
feature works on the commit that writes it and has vanished by the time the
graph is read back. Shipped instances of exactly this:

  * `PhraseSlot` listed ten fields — `curves` (the narrative energy arc),
    `motif_transforms` (the theme placements), `harmony_detail`, `pickup_beats`,
    `continuation` and `notes` all round-tripped to their defaults.
  * `LayerIR` dropped `inner_voices`, so three- and four-voice counterpoint
    survived the commit and disappeared on the assemble that followed, and
    `pickup_beats`, so every anacrusis was silently squared up to a full bar.
  * `SketchIR` named six of eleven fields, dropping `texture_plan`,
    `expression_marks`, `motif_placements`, `entry_signature` and
    `exit_signature`.
  * `PieceGraph.style_dna` and `context_trace` each had their own variant.

None of these were caught by a unit test, because every unit test built its
objects in memory. This file is the general guard: it fills a model with
non-default values, sends it through a real save/load, and asserts nothing came
back different. Adding a field to any model is then automatically covered.
"""

from __future__ import annotations

import dataclasses
import typing

import pytest

from scales import models
from scales.piece_graph import PieceGraph

# ─── Synthesising a distinctively non-default instance ───────────────────────


def _sentinel(hint, depth=0):
    """A value that is valid for `hint` and never equal to the field default."""
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)

    if origin is typing.Union:  # Optional[X]
        inner = [a for a in args if a is not type(None)]
        return _sentinel(inner[0], depth) if inner else "x"
    if origin is list:
        if depth > 2:
            return []
        return [_sentinel(args[0], depth + 1)] if args else ["x"]
    if origin is dict:
        if depth > 2:
            return {}
        return {"k": _sentinel(args[1], depth + 1)} if len(args) == 2 else {"k": "v"}
    if origin is tuple:
        return (7, 8)
    if dataclasses.is_dataclass(hint):
        return _populate(hint, depth + 1)
    if hint is bool:
        return True
    if hint is int:
        return 7
    if hint is float:
        return 0.625
    if hint is str:
        return "sentinel"
    return "sentinel"


def _populate(cls, depth=0):
    """Build an instance of `cls` with every field set to a sentinel."""
    if depth > 3:
        return cls()
    kwargs = {}
    try:
        hints = typing.get_type_hints(cls)
    except Exception:
        hints = {}
    for f in dataclasses.fields(cls):
        hint = hints.get(f.name, str)
        try:
            kwargs[f.name] = _sentinel(hint, depth)
        except Exception:
            continue
    try:
        return cls(**kwargs)
    except Exception:
        return cls()


def _diff(a, b, path=""):
    """Field paths where `a` and `b` differ, ignoring container ordering."""
    out = []
    if dataclasses.is_dataclass(a) and dataclasses.is_dataclass(b):
        for f in dataclasses.fields(a):
            out += _diff(getattr(a, f.name), getattr(b, f.name), f"{path}.{f.name}")
        return out
    if isinstance(a, tuple) and isinstance(b, list):
        b = tuple(b)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: len {len(a)} -> {len(b)}"]
        for i, (x, y) in enumerate(zip(a, b)):
            out += _diff(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return [f"{path}: keys {sorted(a)} -> {sorted(b)}"]
        for k in a:
            out += _diff(a[k], b[k], f"{path}[{k!r}]")
        return out
    if a != b:
        out.append(f"{path}: {a!r} -> {b!r}")
    return out


# ─── The models that go through the graph ────────────────────────────────────

_PHRASE_MODELS = ["PhraseSlot", "SketchIR", "LayerIR"]


@pytest.mark.parametrize("model_name", _PHRASE_MODELS)
def test_phrase_model_survives_a_save_load_round_trip(model_name, tmp_path):
    cls = getattr(models, model_name)
    original = _populate(cls)

    g = PieceGraph()
    g.piece_id = "roundtrip"
    slot = original if model_name == "PhraseSlot" else models.PhraseSlot(phrase_id="p1")
    g.add_phrase("p1", slot)
    if model_name == "SketchIR":
        g.phrases["p1"].sketch = original
    elif model_name == "LayerIR":
        g.phrases["p1"].realized = original

    path = str(tmp_path / "piece_graph.json")
    g.save(path)
    loaded = PieceGraph.load(path)

    got = {
        "PhraseSlot": lambda: loaded.phrases["p1"].slot,
        "SketchIR": lambda: loaded.phrases["p1"].sketch,
        "LayerIR": lambda: loaded.phrases["p1"].realized,
    }[model_name]()

    assert got is not None, f"{model_name} came back as None"
    diffs = _diff(original, got)
    assert not diffs, (
        f"{model_name} lost or changed {len(diffs)} field(s) on a save/load "
        f"round-trip — a hand-enumerated loader is dropping them:\n  " + "\n  ".join(diffs[:20])
    )


def test_layer_event_notation_fields_survive():
    """Every notation field on a note, specifically.

    These are the fields the engraver's pass writes. A loader that drops
    `articulation` or `tie` produces exactly the unmarked, MIDI-like score this
    system used to ship, and nothing else in the pipeline would notice.
    """
    from scales.piece_graph import _reconstruct_layer_event

    ev = models.LayerEvent(
        bar=3,
        beat=2.5,
        pitch="F#5",
        duration="e",
        role="appoggiatura",
        dynamic="mf",
        articulation="tenuto",
        ornament="trill",
        tie="start",
        slur="start",
        hairpin="cresc_start",
        expression="dolce",
        source_layer="principal_line",
        technique="arpeggio_up",
        pedal="down",
        fingering="3",
    )
    back = _reconstruct_layer_event(dataclasses.asdict(ev))
    diffs = _diff(ev, back)
    assert not diffs, f"LayerEvent lost notation on reload: {diffs}"


def test_optional_orchestra_layers_stay_none_when_absent():
    """`None` and `[]` are not interchangeable here.

    The assembler branches on `is None` to decide whether an instrument exists
    at all, so a loader that normalises absent orchestra layers to empty lists
    engraves a silent staff for every instrument the piece does not use.
    """
    from scales.piece_graph import _reconstruct_layer_ir

    layer = _reconstruct_layer_ir({"phrase_id": "p1", "principal_line": []})
    for name in (
        "foreground",
        "countermelody",
        "harmonic_mass",
        "rhythmic_motor",
        "color_layer",
        "punctuation",
    ):
        assert getattr(layer, name) is None, f"{name} should be None, got {getattr(layer, name)!r}"


def test_every_reconstructor_is_field_driven():
    """No loader in piece_graph.py may re-enumerate a model's field list.

    A guard on the *shape* of the code, because the round-trip tests above can
    only cover models that are reachable through the graph. If a new
    `X(a=..., b=...)` reconstruction appears, it is a load-drop bug waiting for
    the next field to be added.
    """
    import ast
    import inspect

    from scales import piece_graph

    tree = ast.parse(inspect.getsource(piece_graph))
    offenders = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        if not fn.name.startswith(("_reconstruct", "_slot_from_dict", "load_")):
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", "") or getattr(node.func, "attr", "")
            if not name or not name[0].isupper():
                continue
            if not dataclasses.is_dataclass(getattr(models, name, None)):
                continue
            if len(node.keywords) >= 4:
                offenders.append(f"{fn.name} builds {name} from {len(node.keywords)} named fields")
    assert not offenders, (
        "field-enumerating reconstruction(s) found; use _dataclass_from_dict "
        "so adding a model field cannot silently drop it:\n  " + "\n  ".join(offenders)
    )


# ─── The models that live on the graph itself ────────────────────────────────

_GRAPH_MODELS = {
    "SectionContract": ("section_contracts", "s1"),
    "ContextTrace": ("context_traces", "p1"),
}


@pytest.mark.parametrize("model_name", sorted(_GRAPH_MODELS))
def test_graph_level_model_survives_a_save_load_round_trip(model_name, tmp_path):
    cls = getattr(models, model_name)
    original = _populate(cls)
    attr, key = _GRAPH_MODELS[model_name]

    g = PieceGraph()
    g.piece_id = "roundtrip"
    getattr(g, attr)[key] = original

    path = str(tmp_path / "piece_graph.json")
    g.save(path)
    loaded = PieceGraph.load(path)

    got = getattr(loaded, attr).get(key)
    assert got is not None, f"{model_name} came back as None"
    # The loader backfills the dict key onto the id field when it is blank;
    # the sentinel is never blank, so nothing legitimate is masked here.
    diffs = [d for d in _diff(original, got) if not d.startswith((".id:", ".phrase_id:"))]
    assert not diffs, (
        f"{model_name} lost or changed {len(diffs)} field(s) on a save/load "
        f"round-trip:\n  " + "\n  ".join(diffs[:20])
    )


def test_work_graph_movements_survive_a_round_trip(tmp_path):
    """A movement contract is most of a symphony's plan.

    `MovementContract` was reconstructed from eight named fields and has
    fifteen, so `sections`, `theme_families_active`, `development_strategies`,
    `recap_logic`, `coda_logic`, `contrast_with_previous` and
    `orchestration_zones` were dropped on every load.
    """
    wg = _populate(models.WorkGraph)
    wg.movements = [_populate(models.MovementContract)]

    g = PieceGraph()
    g.piece_id = "roundtrip"
    g.work_graph = wg
    path = str(tmp_path / "piece_graph.json")
    g.save(path)
    loaded = PieceGraph.load(path)

    assert loaded.work_graph is not None
    assert len(loaded.work_graph.movements) == 1
    diffs = _diff(wg, loaded.work_graph)
    assert not diffs, f"WorkGraph lost {len(diffs)} field(s):\n  " + "\n  ".join(diffs[:20])


def test_piece_graph_load_is_field_driven():
    """The same shape guard, for the loaders inlined into `PieceGraph.load`.

    `test_every_reconstructor_is_field_driven` only walks the module-level
    `_reconstruct_*` helpers; the ContextTrace, SectionContract, WorkGraph,
    MovementContract and TonalItinerary loaders were written inline in
    `PieceGraph.load` and so slipped past it while dropping fields.
    """
    import ast
    import inspect

    from scales import piece_graph

    tree = ast.parse(inspect.getsource(piece_graph))
    # Every function or method whose job is to turn stored data back into
    # objects, wherever it is defined.
    loaders = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef)
        and (
            n.name.startswith(("_reconstruct", "load", "_from_data")) or n.name == "_slot_from_dict"
        )
    ]
    assert loaders, "no loader functions found — did piece_graph.py move?"

    offenders = []
    for fn in loaders:
        for node in ast.walk(fn):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", "") or getattr(node.func, "attr", "")
            if not name or not name[0].isupper():
                continue
            if not dataclasses.is_dataclass(getattr(models, name, None)):
                continue
            if len(node.keywords) >= 4:
                offenders.append(
                    f"{fn.name}() builds {name} from {len(node.keywords)} named "
                    f"fields (line {node.lineno})"
                )
    assert not offenders, (
        "field-enumerating reconstruction(s) found; use _dataclass_from_dict so "
        "adding a model field cannot silently drop it:\n  " + "\n  ".join(offenders)
    )
