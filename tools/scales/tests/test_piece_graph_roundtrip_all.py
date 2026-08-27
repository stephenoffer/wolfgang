"""Every model must survive a PieceGraph save/load with nothing lost.

Hand-enumerated loaders are this project's single largest source of silent
bugs. Each one is written by naming the fields that mattered at the time, and
every field added afterwards is dropped on the next read with no error
anywhere. The tally when this test was written: StyleDNA read back **7 of its
18 fields**, so the composer FINGERPRINTS, the cadence vocabulary, the
chromatic techniques, the progression graph, the form templates and the
orchestration roles were all destroyed on load; `FormGraph.movements` was not
read at all, so a multi-movement work lost its movement structure; PhraseState
named five of thirteen, losing `craft_check` and the critic's own `review`;
LayerIR lost `inner_voices` and `pickup_beats`; SketchIR lost five fields;
PieceContract returned every nested spec as a raw dict.

This test exists so that the next field added to any model cannot repeat it.
It fills every field of every model with a distinctive value, round-trips the
graph through JSON, and walks both trees comparing everything.
"""

from __future__ import annotations

import dataclasses
import typing

import pytest

from scales import models as M
from scales.craft_checker import CraftChecker
from scales.direct_compose import compose_phrase
from scales.piece_graph import PieceGraph

_PROBE_STR = "probe-value"
_PROBE_INT = 4242
_PROBE_FLOAT = 42.5


def _populate(cls, depth: int = 0):
    """An instance of ``cls`` with every field set to a recognisable value."""
    if depth > 3 or not dataclasses.is_dataclass(cls):
        return None
    hints = typing.get_type_hints(cls)
    kwargs = {}
    for f in dataclasses.fields(cls):
        hint = hints.get(f.name)
        origin, args = typing.get_origin(hint), typing.get_args(hint)
        if origin is typing.Union:  # Optional[X]
            inner = [a for a in args if a is not type(None)]
            hint = inner[0] if inner else str
            origin, args = typing.get_origin(hint), typing.get_args(hint)
        if dataclasses.is_dataclass(hint):
            value = _populate(hint, depth + 1)
        elif origin is list:
            item = args[0] if args else str
            if dataclasses.is_dataclass(item):
                value = [_populate(item, depth + 1)]
            elif typing.get_origin(item) is tuple:
                # e.g. List[Tuple[int, int]] — feeding a string here would only
                # test the probe, not the loader.
                value = [tuple(7 for _ in typing.get_args(item)) or (7, 8)]
            elif item is int:
                value = [_PROBE_INT]
            elif item is float:
                value = [_PROBE_FLOAT]
            else:
                value = [_PROBE_STR]
        elif origin is dict:
            value = {"probe_key": _PROBE_STR}
        elif origin is tuple:
            value = (7, 8)
        elif hint is bool:
            value = True
        elif hint is int:
            value = _PROBE_INT
        elif hint is float:
            value = _PROBE_FLOAT
        else:
            value = _PROBE_STR
        kwargs[f.name] = value
    try:
        return cls(**kwargs)
    except Exception:
        return cls()


def _diff(a, b, path: str, out: list) -> None:
    if dataclasses.is_dataclass(a) and dataclasses.is_dataclass(b):
        for f in dataclasses.fields(a):
            _diff(getattr(a, f.name, None), getattr(b, f.name, None), f"{path}.{f.name}", out)
    elif dataclasses.is_dataclass(a) and isinstance(b, dict):
        out.append(f"{path}: came back as a raw dict, not {type(a).__name__}")
    elif isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if k not in b:
                out.append(f"{path}[{k}]: dropped")
            else:
                _diff(a[k], b[k], f"{path}[{k}]", out)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            out.append(f"{path}: {len(a)} entries became {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                _diff(x, y, f"{path}[{i}]", out)
    elif a != b:
        out.append(f"{path}: {a!r} -> {b!r}")


@pytest.fixture()
def round_tripped(tmp_path):
    graph = PieceGraph()
    graph.piece_id = "roundtrip-probe"
    graph.contract = _populate(M.PieceContract)
    graph.style_dna = _populate(M.StyleDNA)
    graph.narrative = _populate(M.NarrativeArc)

    # FormGraph by hand: the probe cannot invent a well-formed section map.
    graph.form = M.FormGraph()
    graph.form.sections["s1"] = _populate(M.SectionSpec)
    graph.form.movements.append(_populate(M.MovementContract))

    graph.motif_bank = {"mA": _populate(M.MotifObject)}
    graph.section_contracts = {"s1": _populate(M.SectionContract)}

    state = M.PhraseState()
    state.slot = _populate(M.PhraseSlot)
    state.slot.meter = (3, 4)
    state.sketch = _populate(M.SketchIR)
    state.realized = compose_phrase(
        [{"rh": "C5h. // G4h. // E4h.", "lh": "C3h."}],
        key="C",
        bar_start=1,
        phrase_id="p1",
        meter=(3, 4),
    )
    state.realized.pickup_beats = 1.0
    state.realized.principal_line[0].technique = "arpeggio"
    state.craft_check = CraftChecker().check(state.realized)
    state.review = _populate(M.ReviewResult)
    state.agent_authored = True
    graph.phrases = {"p1": state}

    path = tmp_path / "piece_graph.json"
    graph.save(str(path))
    return graph, PieceGraph.load(str(path))


@pytest.mark.parametrize(
    "field",
    ["contract", "style_dna", "narrative", "form", "motif_bank", "section_contracts", "phrases"],
)
def test_no_field_is_lost_on_a_save_load(round_tripped, field):
    original, reloaded = round_tripped
    lost: list = []
    _diff(getattr(original, field), getattr(reloaded, field), field, lost)
    assert not lost, "fields lost on round trip:\n  " + "\n  ".join(lost[:20])


def test_the_specific_fields_that_were_being_dropped(round_tripped):
    """Named individually so a regression says WHICH one came back."""
    _, back = round_tripped

    assert back.style_dna.fingerprints.items, "composer fingerprints"
    assert back.style_dna.cadence_vocabulary, "cadence vocabulary"
    assert back.style_dna.chromatic_techniques, "chromatic techniques"
    assert back.style_dna.progression_graph, "progression graph"
    assert back.style_dna.form_templates, "form templates"
    assert back.style_dna.orchestration_roles, "orchestration roles"
    assert back.form.movements, "FormGraph.movements"

    assert isinstance(back.contract.target, M.TargetSpec), "nested contract specs stay typed"
    assert isinstance(back.contract.locks, M.LockPolicy)

    phrase = back.phrases["p1"]
    assert phrase.realized.inner_voices, "LayerIR.inner_voices"
    assert phrase.realized.pickup_beats == 1.0, "LayerIR.pickup_beats"
    assert phrase.realized.principal_line[0].technique == "arpeggio", "LayerEvent.technique"
    assert phrase.craft_check is not None and phrase.craft_check.has_breath_point is not None
    assert isinstance(back.phrases["p1"].review, M.ReviewResult), "the critic's verdict stays typed"
    assert phrase.sketch.texture_plan, "SketchIR.texture_plan"


def test_a_save_never_leaves_a_partial_graph():
    """`open(path, "w")` truncates before it writes, so the graph — the SINGLE
    SOURCE OF TRUTH for a whole composition — was empty for as long as the write
    took.

    Anything interrupting it left an empty file where hours of work had been: a
    crash, a Ctrl-C, a full disk. A concurrent reader saw the same, which is how
    it surfaced — a fixture reading a graph mid-save raised
    `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, which is what
    decoding an empty string looks like.
    """
    import os
    import tempfile
    from pathlib import Path

    from scales.piece_graph import PieceGraph

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "piece_graph.json"
        graph = PieceGraph()
        graph.piece_id = "atomic-probe"
        graph.save(str(path))
        good = path.read_text()
        assert good.strip(), "the first save wrote nothing"

        class _Unserializable:
            def __repr__(self):
                raise RuntimeError("boom")

        graph.output_paths = {"score": _Unserializable()}
        with pytest.raises(Exception):
            graph.save(str(path))

        # The previous good file survives, byte for byte.
        assert path.read_text() == good, "a failed save destroyed the last good graph"
        # And no scratch file is left in the workspace.
        assert os.listdir(tmp) == ["piece_graph.json"], os.listdir(tmp)


def test_a_concurrent_reader_never_sees_a_half_written_graph():
    """The mechanism, demonstrated rather than argued.

    Truncate-then-write leaves the file empty for the duration of the write, so
    a reader hitting that window decodes an empty string. Measured against the
    old implementation: 5,155 corrupt reads out of 27,540. Atomic: zero.

    Asserts ZERO, not "few" — `os.replace` makes a partial read impossible, so
    any corruption at all means the atomicity has been lost.
    """
    import json
    import tempfile
    import threading
    import time
    from pathlib import Path

    from scales.piece_graph import PieceGraph

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "piece_graph.json"
        graph = PieceGraph()
        graph.piece_id = "race-probe"
        graph.save(str(path))

        stop = threading.Event()
        corrupt = []

        def writer():
            while not stop.is_set():
                graph.save(str(path))

        def reader():
            while not stop.is_set():
                try:
                    json.loads(path.read_text())
                except FileNotFoundError:
                    pass
                except ValueError:
                    corrupt.append(1)

        threads = [threading.Thread(target=writer), threading.Thread(target=reader)]
        for t in threads:
            t.start()
        time.sleep(0.4)
        stop.set()
        for t in threads:
            t.join()

        assert not corrupt, f"{len(corrupt)} partial reads — the save is not atomic"
