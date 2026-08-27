"""The revision path — how a critic's finding becomes different music.

Everything upstream of this is diagnosis. If a revision op cannot express the
change the critic asked for, or applies it to the wrong bars, the analysis is
decorative.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from scales.direct_compose import compose_phrase
from scales.models import PhraseSlot, PhraseState, RevisionOp
from scales.patch_engine import PatchEngine


@pytest.fixture()
def phrase():
    state = PhraseState(
        slot=PhraseSlot(
            phrase_id="p",
            section_id="s",
            bar_start=1,
            bar_count=2,
            key="Db major",
            meter=(4, 4),
            tempo_bpm=90,
        )
    )
    state.realized = compose_phrase(
        [
            {"rh": "C5q D5q [E5,G5]q F5q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e"},
            {"rh": "G5q A5q B5q C6q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e"},
        ],
        key="Db major",
        bar_start=1,
        phrase_id="p",
        meter=(4, 4),
    )
    return state


def _op(operation, **kw):
    return RevisionOp(target_phrase="p", operation=operation, **kw)


def test_transpose_moves_every_layer_not_just_two(phrase):
    """Transposing only principal_line and bass_foundation left the inner
    voices, the figuration and the ornamental surface in the old key — an
    instant dissonance dressed up as a revision."""
    PatchEngine().apply_revision_op(
        _op("transpose_region", params={"interval": 2}, target_bars=(1, 1)), phrase
    )
    rh = [e for e in phrase.realized.principal_line if e.bar == 1]
    lh = [e for e in phrase.realized.bass_foundation if e.bar == 1]
    assert rh[0].pitch != "C5" and lh[0].pitch != "C3", "both hands must move together"


def test_transpose_moves_chords_too(phrase):
    """Chords were skipped, so the melody moved and the harmony under it did not."""
    PatchEngine().apply_revision_op(
        _op("transpose_region", params={"interval": 1}, target_bars=(1, 1)), phrase
    )
    chords = [e for e in phrase.realized.principal_line if isinstance(e.pitch, list)]
    assert chords, "the fixture has a chord"
    assert chords[0].pitch != ["E5", "G5"], "the chord did not transpose"


def test_transpose_spells_in_the_phrases_own_key(phrase):
    """Spelling every transposition in C turned a move into D-flat major into a
    page of sharps."""
    PatchEngine().apply_revision_op(
        _op("transpose_region", params={"interval": 1}, target_bars=(1, 1)), phrase
    )
    names = [e.pitch for e in phrase.realized.principal_line if e.bar == 1 and e.pitch != "rest"]
    flat_spellings = [n for n in names if isinstance(n, str) and "b" in n[1:]]
    assert flat_spellings, f"a Db-major phrase should be spelled in flats, got {names}"


def test_transpose_leaves_bars_outside_the_target_alone(phrase):
    before = [e.pitch for e in phrase.realized.principal_line if e.bar == 2]
    PatchEngine().apply_revision_op(
        _op("transpose_region", params={"interval": 5}, target_bars=(1, 1)), phrase
    )
    after = [e.pitch for e in phrase.realized.principal_line if e.bar == 2]
    assert before == after


def test_change_texture_respects_the_target_bars(phrase):
    """`if target_bars is None or True` ignored the target entirely, so an op
    asking to change two bars rewrote every bar of the phrase."""
    from scales.models import BarTexturePlan

    # BarTexturePlan is POSITIONAL — entry i is the phrase's bar_start + i.
    phrase.slot.texture_plan = [
        BarTexturePlan(lh_texture="alberti"),
        BarTexturePlan(lh_texture="alberti"),
    ]
    PatchEngine().apply_revision_op(
        _op("change_texture", params={"lh_texture": "block_chord_sparse"}, target_bars=(2, 2)),
        phrase,
    )
    textures = [bp.lh_texture for bp in phrase.slot.texture_plan]
    assert textures == ["alberti", "block_chord_sparse"], textures


def test_set_articulation_is_reachable_without_recomposing(phrase):
    """The critic's commonest finding is an unarticulated page; the only way to
    act on it was `re_realize`, which throws away the notes to add a dot."""
    PatchEngine().apply_revision_op(
        _op("set_articulation", params={"articulation": "staccato"}, target_bars=(2, 2)), phrase
    )
    by_bar = {}
    for e in phrase.realized.principal_line:
        by_bar.setdefault(e.bar, set()).add(e.articulation)
    assert by_bar[2] == {"staccato"}
    assert by_bar[1] == {None}, "bar 1 was not in the target range"
    assert phrase.realized.principal_line, "the notes must survive"


def test_set_hairpin_shapes_a_span(phrase):
    PatchEngine().apply_revision_op(
        _op("set_hairpin", params={"kind": "cresc"}, target_bars=(1, 2)), phrase
    )
    marks = [(e.bar, e.hairpin) for e in phrase.realized.principal_line if e.hairpin]
    assert marks[0][1] == "cresc_start" and marks[-1][1] == "stop"
    assert len(marks) == 2, "exactly one start and one stop"


def test_thin_texture_removes_offbeats_and_keeps_the_harmony(phrase):
    before = len(phrase.realized.bass_foundation)
    PatchEngine().apply_revision_op(_op("thin_texture", target_bars=(1, 1)), phrase)
    after = phrase.realized.bass_foundation
    assert len(after) < before, "nothing was thinned"
    assert [e for e in after if e.bar == 1], "bar 1 must not be emptied"
    assert all(abs(e.beat - round(e.beat)) < 0.01 for e in after if e.bar == 1)
    assert len([e for e in after if e.bar == 2]) == 8, "bar 2 was outside the target"


def test_an_unknown_operation_does_not_destroy_the_phrase(phrase):
    notes = list(phrase.realized.principal_line)
    PatchEngine().apply_revision_op(_op("no_such_operation"), phrase)
    assert phrase.realized.principal_line == notes


# ── The engine fallback, which committed without any validation ─────────────


def test_engine_surfaces_are_repaired_before_they_are_committed():
    """`run_scales_section` committed straight to the graph with NO physical
    validation, while the agent path has enforced meter, range and same-voice
    overlap at commit for months. A probe of one three-phrase section found 65
    meter errors going silently to the score."""
    from scales.models import LayerEvent, LayerIR
    from scales.scales import _POSITION_GRID, _repair_engine_surface
    from scales.validator import validate_meter

    layer = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=1)
    layer.principal_line = [
        # A beat position on no notatable grid — what a float cursor rounded to
        # two decimals produces.
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="q"),
        LayerEvent(bar=1, beat=1.56, pitch="D5", duration="q"),
        # Same voice re-attacking while the previous note still sounds.
        LayerEvent(bar=1, beat=2.0, pitch="E5", duration="h"),
        LayerEvent(bar=1, beat=2.5, pitch="F5", duration="q"),
        # Past the barline: beats are 1-BASED, so beat 5.5 of a 4/4 bar is
        # offset 4.5 — outside a bar that holds 4 beats.
        LayerEvent(bar=1, beat=5.5, pitch="G5", duration="q"),
    ]
    counts = _repair_engine_surface(layer, (4, 4))

    assert counts, "a malformed surface must report what was repaired"
    assert counts.get("snapped", 0) >= 1
    errors = [i for i in validate_meter(layer.principal_line, (4, 4)) if i.severity == "error"]
    assert not errors, [i.message for i in errors]
    assert counts.get("overflow_dropped", 0) >= 1, "the out-of-bar note was kept"
    for e in layer.principal_line:
        # Every surviving onset sits on the notatable grid (compared at the
        # precision the IR stores, since beats are JSON floats).
        offset = Fraction(e.beat).limit_denominator(10**6) - 1
        assert (offset * _POSITION_GRID).denominator == 1, f"beat {e.beat} is off the grid"
        assert e.beat >= 1.0, "a beat below 1 is not a position in any bar"
        assert e.beat < 5.0, "a surviving note starts outside its own bar"


def test_repair_leaves_a_well_formed_surface_alone():
    """A repair that rewrites correct music is worse than no repair."""
    from scales.scales import _repair_engine_surface

    layer = compose_phrase(
        [{"rh": "C5q D5q E5q F5q", "lh": "C3e G3e C3e G3e C3e G3e C3e G3e"}],
        key="C",
        bar_start=1,
        phrase_id="p",
        meter=(4, 4),
    )
    before = [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line]
    assert not _repair_engine_surface(layer, (4, 4)), "nothing needed repairing"
    assert [(e.bar, e.beat, e.pitch, e.duration) for e in layer.principal_line] == before


def test_repair_keeps_triplets_and_32nds_on_the_grid():
    """The grid must not be a 16th grid: snapping a triplet onto one destroys it."""
    from scales.scales import _repair_engine_surface

    layer = compose_phrase(
        [{"rh": "C5trip_e D5trip_e E5trip_e F5t G5t A5t B5t C6q", "lh": "C3w"}],
        key="C",
        bar_start=1,
        phrase_id="p",
        meter=(4, 4),
    )
    beats = [e.beat for e in layer.principal_line]
    _repair_engine_surface(layer, (4, 4))
    assert [e.beat for e in layer.principal_line] == beats, "a legal rhythm was altered"


def test_the_repair_grid_can_express_every_notatable_duration():
    """The one-line invariant that would have caught a grid of 48.

    48 covers triplets, sextuplets, 32nds and 64ths — and silently rounds every
    quintuplet and septuplet, because 5 and 7 do not divide it. That is the same
    failure as the 16th-note grid that once destroyed every triplet in this
    system, so it is asserted rather than trusted.
    """
    from scales.duration import DURATION_VALUES
    from scales.scales import _POSITION_GRID

    step = Fraction(1, _POSITION_GRID)
    off_grid = {code: v for code, v in DURATION_VALUES.items() if v % step != 0}
    assert not off_grid, f"these durations cannot land on the repair grid: {off_grid}"


@pytest.mark.parametrize("code", ["quint_s", "quint_e", "sept_s", "trip_s", "sext_s", "x"])
def test_repair_does_not_move_a_legal_tuplet(code):
    """A repair that corrupts a legal rhythm is worse than the drift it fixes."""
    from scales.duration import DURATION_VALUES
    from scales.models import LayerEvent, LayerIR
    from scales.scales import _repair_engine_surface

    value = DURATION_VALUES[code]
    count = int(Fraction(1) / value) if value <= 1 else 2
    layer = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=1)
    beat = Fraction(1)
    for _ in range(count):
        layer.principal_line.append(
            LayerEvent(bar=1, beat=round(float(beat), 6), pitch="C5", duration=code)
        )
        beat += value
    before = [e.beat for e in layer.principal_line]
    _repair_engine_surface(layer, (4, 4))
    assert [e.beat for e in layer.principal_line] == before, f"{code} run was moved"


def test_every_subdivision_divides_the_repair_grid():
    """A subdivision that does not divide the grid produces a position no
    engraver can bracket."""
    from scales.scales import _POSITION_GRID, _SUBDIVISIONS

    assert all(_POSITION_GRID % d == 0 for d in _SUBDIVISIONS)
    assert list(_SUBDIVISIONS) == sorted(_SUBDIVISIONS), (
        "coarsest first: a 48th is within tolerance of a septuplet and would "
        "swallow it if the fine binary grids came first"
    )


@pytest.mark.parametrize(
    "drifted,duration,expected",
    [
        (1.56, "t", 1.5625),
        (2.06, "t", 2.0625),
        # A POSITION AND ITS DURATION SHARE A GRID. A triplet position is only
        # read as one when the note's own length comes from that family — a
        # 32nd at 4/3 is a drifted binary onset that happened to land near a
        # third, and reading it as a genuine triplet leaves a bar that cannot
        # tile. These cases originally passed a binary "t" and expected the
        # tuplet position, which is the incoherent combination the rule exists
        # to reject; they carry a tuplet duration now.
        (1.3333, "trip_e", 4 / 3),
        (1.1667, "trip_s", 7 / 6),
        (0.06, "t", 1.0),
    ],
)
def test_repair_recovers_a_smeared_onset(drifted, duration, expected):
    """The positions a float cursor rounded to two decimals actually produced."""
    from scales.models import LayerEvent, LayerIR
    from scales.scales import _repair_engine_surface

    layer = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=1)
    layer.principal_line = [LayerEvent(bar=1, beat=drifted, pitch="C5", duration=duration)]
    _repair_engine_surface(layer, (4, 4))
    assert layer.principal_line[0].beat == pytest.approx(expected, abs=1e-4)


@pytest.mark.parametrize("drifted", [1.3333, 1.1667])
def test_a_binary_note_near_a_triplet_position_is_drift_not_a_tuplet(drifted):
    """The other half of the same rule, stated as its own claim.

    A 32nd sitting within a 256th of a third is a smeared binary onset. Read as
    a genuine triplet it leaves a remainder no notatable value fills — a 3/8 bar
    exported holding 85/56, with a MusicXML warning as the only witness.
    """
    from fractions import Fraction

    from scales.models import LayerEvent, LayerIR
    from scales.scales import _repair_engine_surface

    layer = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=1)
    layer.principal_line = [LayerEvent(bar=1, beat=drifted, pitch="C5", duration="t")]
    _repair_engine_surface(layer, (4, 4))
    resolved = Fraction(str(layer.principal_line[0].beat)).limit_denominator(1680)
    assert (resolved - 1).denominator % 3 != 0, (
        f"{drifted} with a binary duration resolved to the tuplet position {resolved}"
    )


def test_repair_never_deletes_a_grace_note():
    """A grace note SHARES its principal's beat by definition — it is played
    before it and takes no metric time. Reading that as a same-voice overlap
    deleted every appoggiatura and acciaccatura the composer wrote, silently,
    in exactly the paths this repair was added to protect."""
    from scales.direct_compose import compose_phrase
    from scales.scales import _repair_engine_surface

    layer = compose_phrase(
        [{"rh": "A5e:appo G5q Bb5dq A5e", "lh": "F3h."}],
        key="F major",
        bar_start=1,
        phrase_id="p",
        meter=(3, 4),
    )
    before = [(e.beat, e.pitch, e.ornament) for e in layer.principal_line]
    counts = _repair_engine_surface(layer, (3, 4))
    after = [(e.beat, e.pitch, e.ornament) for e in layer.principal_line]

    assert after == before, "a legal bar with a grace note was altered"
    assert not counts, f"nothing needed repairing: {counts}"
    assert any(orn for _, _, orn in after), "the appoggiatura was deleted"


def test_repair_still_trims_a_real_overlap_beside_a_grace_note():
    """The grace-note exemption must not disable the overlap check around it."""
    from scales.models import LayerEvent, LayerIR
    from scales.scales import _repair_engine_surface

    layer = LayerIR(phrase_id="p", key="C", meter=(4, 4), bar_count=1)
    layer.principal_line = [
        LayerEvent(bar=1, beat=1.0, pitch="B4", duration="e", ornament="acciaccatura"),
        LayerEvent(bar=1, beat=1.0, pitch="C5", duration="h"),  # still sounding at 2.0
        LayerEvent(bar=1, beat=2.0, pitch="D5", duration="h"),
    ]
    counts = _repair_engine_surface(layer, (4, 4))
    assert counts.get("overlaps_trimmed") == 1, "the real overlap was missed"
    assert len(layer.principal_line) == 3, "nothing should be deleted"
    assert layer.principal_line[0].ornament == "acciaccatura"


def test_the_documented_revision_params_are_the_ones_the_engine_reads():
    """Each handler reads ONE key with `op.params.get(...)`, and most supply a
    default — so an op carrying the wrong name applies cleanly, changes nothing
    (or changes the wrong thing), and still reports `ops_applied`.

    `transpose_region` defaults `interval` to 0, so a script saying `semitones`
    transposes by nothing. `set_hairpin` defaults `kind` to "cresc", so a script
    asking for a diminuendo gets a crescendo — which is how the first version of
    the guard table got this entry wrong: probing it "worked" because the
    default fired.

    Derived from the source so the table and the handlers cannot drift.
    """
    import re
    from pathlib import Path

    from scales.scales import _REVISION_OP_PARAMS, _REVISION_OPS

    src = (Path(__file__).resolve().parents[1] / "patch_engine.py").read_text()
    blocks = re.split(r'(?:elif|if) operation == "([a-z_]+)":', src)
    actual = {}
    for i in range(1, len(blocks), 2):
        name, body = blocks[i], blocks[i + 1]
        keys = re.findall(r'op\.params\.get\(\s*"([a-z_]+)"', body)
        # `key` is a fallback lookup in transpose_region, not its subject.
        keys = [k for k in keys if k != "key"]
        if keys:
            actual[name] = keys[0]

    assert actual, "no revision handlers found — did the dispatch shape change?"
    for operation, primary in actual.items():
        if operation not in _REVISION_OPS:
            continue
        declared = _REVISION_OP_PARAMS.get(operation)
        assert declared, f"{operation} reads {primary!r} but the guard declares no parameter"
        assert primary in declared, (
            f"{operation} reads {primary!r}; the guard declares {declared}. "
            "A script using the declared name would be a silent no-op."
        )
    # And nothing is declared for an operation that reads no parameter at all.
    for operation in _REVISION_OP_PARAMS:
        assert operation in actual, f"{operation} is declared but reads no parameter"


def test_the_critic_guidance_documents_the_real_parameter_names():
    """The agent writing a RevisionScript has no way to know the key but to be
    told, and the table in `music-critic.md` is where it is told."""
    import re
    from pathlib import Path

    from scales.scales import _REVISION_OP_PARAMS

    doc = Path(__file__).resolve().parents[3] / ".claude" / "agents" / "music-critic.md"
    if not doc.exists():
        return
    text = doc.read_text()
    for operation, keys in _REVISION_OP_PARAMS.items():
        row = re.search(rf"\|\s*`{operation}`\s*\|(.*?)\|", text)
        if not row:
            continue
        assert any(f'"{k}"' in row.group(1) for k in keys), (
            f"music-critic.md documents {operation} as {row.group(1).strip()!r}, "
            f"but the engine reads {' or '.join(keys)}"
        )
