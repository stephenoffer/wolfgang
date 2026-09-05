"""A bassoon was doubling the soprano melody.

`plan_orchestration`'s last pass gives any still-silent instrument a part —
"better a real part than a tacet stave in a score that names it" — and it gave
every one of them the MELODY.

In a concerto tutti, where the piano core is octaves over a bass and there is
little inner material, that left flute, oboe, clarinet, bassoon AND violin 1 all
on the tune, five instruments at 95-100% the same pitch classes, while violin 2
had 4 notes and the cello 8 across eight bars. A bassoon doubling a soprano
melody is not a thin part, it is a wrong one.

A low instrument now doubles the BASS, which is exactly what the pass above it
already does for the viola and calls "the oldest filler in the orchestra".
"""

from __future__ import annotations

from scales.models import LayerEvent, LayerIR
from scales.orchestration_planner import plan_orchestration, practical_range
from scales.pitch import pitch_to_midi

ENSEMBLE = [
    "flute", "oboe", "clarinet", "bassoon", "horn",
    "violin_1", "violin_2", "viola", "cello", "contrabass",
]


def _octave_tutti() -> LayerIR:
    """The shape that exposed it: a melody in octaves over a bare bass, with
    nothing in the middle for the inner passes to hand out."""
    layer = LayerIR(key="A minor", meter=(4, 4))
    layer.principal_line = [
        LayerEvent(bar=1 + i // 4, beat=1.0 + (i % 4), pitch=p, duration="q",
                   role="structural", source_layer="principal_line")
        for i, p in enumerate(["A5", "C6", "E6", "C6", "B5", "A5", "G#5", "A5"])
    ]
    layer.bass_foundation = [
        LayerEvent(bar=1 + i // 4, beat=1.0 + (i % 4), pitch=p, duration="q",
                   role="structural", source_layer="bass_foundation")
        for i, p in enumerate(["A2", "A2", "E2", "E2", "A2", "F2", "E2", "A2"])
    ]
    return layer


def _tops(parts, name):
    out = []
    for event in parts.get(name) or []:
        pitches = event["pitch"] if isinstance(event["pitch"], list) else [event["pitch"]]
        got = [pitch_to_midi(p) for p in pitches if p and p != "rest"]
        if got:
            out.append(max(g for g in got if g is not None))
    return out


def test_a_low_instrument_does_not_take_the_soprano_line():
    parts = plan_orchestration(_octave_tutti(), ENSEMBLE, key="A minor")
    melody = _tops(parts, "violin_1") or _tops(parts, "flute")
    assert melody
    melody_centre = sum(melody) / len(melody)
    for low in ("bassoon", "cello", "contrabass"):
        line = _tops(parts, low)
        if not line:
            continue
        assert sum(line) / len(line) < melody_centre - 7, (
            f"{low} sits at the melody's height — it is doubling the tune"
        )


def test_a_high_instrument_may_still_double_the_tune():
    """Doubling the melody in the flute is idiomatic for a tutti; the fix must
    not silence the winds, only stop the wrong ones."""
    parts = plan_orchestration(_octave_tutti(), ENSEMBLE, key="A minor")
    assert _tops(parts, "flute"), "the flute should have a part"


def test_no_instrument_is_left_tacet():
    """The original intent stands: a named stave gets notes."""
    parts = plan_orchestration(_octave_tutti(), ENSEMBLE, key="A minor")
    silent = [name for name in ENSEMBLE if not (parts.get(name) or [])]
    assert not silent, f"tacet staves in a score that names them: {silent}"


def test_every_part_stays_inside_its_instrument():
    parts = plan_orchestration(_octave_tutti(), ENSEMBLE, key="A minor")
    for name in ENSEMBLE:
        line = _tops(parts, name)
        if not line:
            continue
        low, high = practical_range(name)
        assert low <= min(line) and max(line) <= high, f"{name} {min(line)}-{max(line)}"


def test_a_concerto_soloist_is_one_instrument_on_two_staves(tmp_path, monkeypatch):
    """The soloist is emitted as two PARTS — the ensemble path gives each part a
    single staff, and a soloist crammed onto one had its hands overlapping and 42
    events trimmed by the repair pass. But the lower part was then named from its
    staff id, so the score listed **"Piano"** and **"Piano Lh"** as if two
    players were at two pianos.

    An engraved concerto names the instrument once, at the top of a brace.
    """
    import music21

    from scales import scales as S

    monkeypatch.setattr(S, "_WORKSPACE", tmp_path)
    pid = "concerto-brace-probe"
    S.init_workspace(pid, "compose_from_text", description="probe",
                     params={"instrumentation": "concerto"})
    S.compile_style(pid, "beethoven")
    S.build_form_graph(pid, "binary", "A minor", tempo_bpm=100, meter=(4, 4))

    graph = S._load_graph(pid)
    first = sorted(graph.phrases)[0]
    bars = [
        {"rh": "A5q C6q E6q C6q", "lh": "A2q E3q A2q E3q"},
        {"rh": "B5q A5q G#5q A5q", "lh": "E2q B2q E2q E3q"},
        {"rh": "C6q B5q A5q G#5q", "lh": "A2q E3q A2q E3q"},
        {"rh": "A5w", "lh": "A2w"},
    ]
    S.get_composition_brief(pid, first, composer="beethoven")
    committed = S.commit_agent_phrase_direct_bars(pid, first, bars, composer="beethoven")
    if not committed.get("ok"):
        import pytest

        pytest.skip(f"probe phrase did not commit: {committed}")

    section = graph.phrases[first].slot.section_id
    S.orchestrate_section(pid, section, soloist="piano")
    result = S.assemble_orchestration(pid, section)
    score = music21.converter.parse(str(result["path"]))

    names = [p.partName for p in score.parts]
    assert not any(str(n).lower().endswith(" lh") for n in names), names
    assert names.count("Piano") == 2, names

    braces = [
        g for g in score.recurse().getElementsByClass("StaffGroup")
        if g.symbol == "brace" and len(g.getSpannedElements()) == 2
    ]
    assert braces, "the soloist's two staves are not braced together"
