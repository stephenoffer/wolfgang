"""There is one field-driven reconstructor, and everything uses it.

`piece_graph._dataclass_from_dict` exists because "hand-enumerated loaders are
how this project keeps losing state" — the PhraseSlot loader listed ten fields
and silently dropped `curves`, `motif_transforms`, `harmony_detail`,
`pickup_beats`, `continuation` and `notes` on the first save/load round-trip.

Two more copies of the same idea were living in `feedback/`:

    known = {f.name for f in cls.__dataclass_fields__.values()}
    filtered = {k: v for k, v in data.items() if k in known}
    return cls(**filtered)

byte-identical in `claim_registry.MeasurableClaim.from_dict` and
`evidence_extractor.EvidenceBundle.from_dict`, and neither recursed into nested
dataclasses the way the canonical one does. Both now delegate.
"""

import ast
import pathlib

from scales.feedback.claim_registry import MeasurableClaim
from scales.feedback.evidence_extractor import EvidenceBundle
from scales.piece_graph import _dataclass_from_dict


def test_a_claim_round_trips():
    claim = MeasurableClaim.from_dict({"claim_id": "c1", "category": "harmony"})
    assert claim.claim_id == "c1"
    assert claim.category == "harmony"


def test_a_bundle_round_trips():
    bundle = EvidenceBundle.from_dict({"composer": "mozart", "bar_count": 41})
    assert bundle.composer == "mozart"
    assert bundle.bar_count == 41


def test_an_unknown_key_is_ignored_not_raised():
    """The property both copies existed to provide."""
    assert MeasurableClaim.from_dict({"claim_id": "c1", "bogus": 123}).claim_id == "c1"
    assert EvidenceBundle.from_dict({"composer": "m", "bogus": 1}).composer == "m"


def test_both_delegate_rather_than_reimplement():
    root = pathlib.Path(__file__).resolve().parents[1]
    for module in ("feedback/claim_registry.py", "feedback/evidence_extractor.py"):
        src = (root / module).read_text()
        tree = ast.parse(src)
        fn = next(
            n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "from_dict"
        )
        body = ast.unparse(fn)
        assert "_dataclass_from_dict" in body, module
        assert "__dataclass_fields__" not in body, f"{module} still filters fields itself"


def test_no_third_copy_appears():
    """The guard. A new module that needs this must import it."""
    root = pathlib.Path(__file__).resolve().parents[1]
    offenders = []
    for path in root.rglob("*.py"):
        if "test" in str(path) or path.name == "piece_graph.py":
            continue
        src = path.read_text()
        if "__dataclass_fields__" in src and "k in known" in src:
            offenders.append(path.name)
    assert not offenders, f"re-implemented field filtering: {offenders}"


def test_the_canonical_one_recurses_into_nested_dataclasses():
    """What the copies did NOT do, and why delegating is an improvement rather
    than a tidy-up."""
    from scales.models import NarrativeArc

    arc = _dataclass_from_dict(
        NarrativeArc, {"sections": [{"id": "a", "bar_start": 3, "character": "x"}]}
    )
    assert arc.sections and arc.sections[0].id == "a"
    assert arc.sections[0].bar_start == 3


# ─── One pitch parser, too ───────────────────────────────────────────────────


def test_the_note_parser_delegates(function_source):
    """`style_dimensions._note_to_midi` was a second implementation of
    `pitch.pitch_to_midi` — accidentals walked by hand. The two agreed on every
    spelling tested, which is exactly how the four key parsers
    (`project_one_parser_one_loader`) started before three of them drifted."""
    from scales import style_dimensions

    src = function_source(style_dimensions, "_note_to_midi")
    assert "pitch_to_midi" in src
    assert "_PC_BASE" not in src, "still walks accidentals by hand"


def test_the_note_parser_still_handles_music21_spellings():
    """Delegation must not lose the cases the local copy existed for: music21
    writes flats as '-', and double accidentals occur in real scores."""
    from scales.pitch import pitch_to_midi
    from scales.style_dimensions import _note_to_midi

    for name in ("C4", "Db4", "D-4", "F#5", "F##5", "Ab-1", "A-3", "B--4", "E-4", "Cb4"):
        assert _note_to_midi(name) == pitch_to_midi(name), name


def test_the_note_parser_returns_none_for_junk_rather_than_raising():
    """Its callers treat None as "not a note"; an exception would take out a
    corpus pass."""
    from scales.style_dimensions import _note_to_midi

    for junk in ("", "bogus", "H4", "4"):
        assert _note_to_midi(junk) is None


def test_the_key_parsers_are_delegates_not_copies():
    """Three functions match `parse_key` by name; two are one-line delegates to
    `pitch.parse_key`, which is correct — an alias is not a duplicate."""
    import ast
    import pathlib

    # Located by NAME through the AST, not by `inspect.getsource`. That reads the
    # file at line numbers recorded when the module was imported, so if anything
    # edits the file during the run it returns the text of a DIFFERENT function —
    # this test failed intermittently for exactly that reason while another
    # session was editing `scales.py`, and passed in isolation every time.
    for filename, funcname in (
        ("assembler.py", "_parse_key"),
        ("scales.py", "_parse_key_str"),
    ):
        tree = ast.parse((pathlib.Path("tools/scales") / filename).read_text())
        node = next(
            (
                n
                for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.name == funcname
            ),
            None,
        )
        assert node is not None, f"{filename} has no {funcname}"
        src = ast.unparse(node)
        assert "parse_key" in src
        assert "music21" not in src, f"{funcname} re-implements parsing instead of delegating"
