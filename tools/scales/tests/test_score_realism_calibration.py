"""Calibration harness for `score_realism`: no detector may fire on real music.

`score_realism.py`'s module docstring promises that "every threshold in this
file was set by running the detector over the real Mozart/Beethoven/Chopin
corpus under ``tools/reference_scores/`` (see
``tools/tests/test_score_realism_calibration.py``) and choosing a bound the real
music clears. A detector that fires on canonical music is a broken detector."

That file did not exist, and the promise was false. Run against 26 canonical
movements, the shipped detectors fired like this:

    dynamic_terracing            26/26      ← measured the file format
    repeated_bars                20/26      ← verbatim repetition is normal
    rhythm_vocabulary_poverty     9/26
    closing_gesture_absent        8/26      ← empty trailing barline measures
    voicing_poverty               3/26
    tie_absent                    2/26
    articulation_absent           1/26

This is that harness. It is marked `calibration` because it parses ~26 Humdrum
scores and is too slow for the default run; the fast unit test below it guards
the same invariant on the recorded numbers so a regression cannot ship silently.

Run it with:  pytest -m calibration tools/scales/tests/test_score_realism_calibration.py -s
"""

from __future__ import annotations

import warnings
from collections import Counter
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
_REF = _REPO / "tools" / "reference_scores"

# Detectors allowed a nonzero false-positive rate on canonical music, with the
# measured rate and the reason. Anything not listed here must fire on ZERO of
# the reference movements. Both entries are `info` severity, so neither can
# drive a revision on its own.
_TOLERATED = {
    # Mozart K.279/iii and Chopin Op.30 No.2 genuinely contain no tied notes.
    "tie_absent": 2,
    # Four movements end on a short, thin bar whose rhythm occurs earlier —
    # a curt ending is a real compositional choice.
    "closing_gesture_absent": 4,
}


def _reference_scores(limit_per_set: int = 14):
    sets = [
        ("mozart-piano-sonatas", "sonata0*-*.krn", limit_per_set),
        ("chopin-mazurkas", "mazurka3*.krn", 6),
        ("beethoven-piano-sonatas", "*.krn", 6),
    ]
    out = []
    for folder, pattern, n in sets:
        d = _REF / folder / "kern"
        if d.is_dir():
            out.extend(sorted(d.glob(pattern))[:n])
    return out


@pytest.mark.calibration
def test_no_detector_fires_on_canonical_music():
    """The falsification pass. A bound real music cannot clear is a bug."""
    warnings.filterwarnings("ignore")
    from scales.score_realism import realism_report

    files = _reference_scores()
    if len(files) < 10:
        pytest.skip(f"reference corpus not available ({len(files)} scores found)")

    fired: Counter = Counter()
    where: dict = {}
    for f in files:
        rep = realism_report(str(f))
        for det in rep["summary"]["by_detector"]:
            fired[det] += 1
            where.setdefault(det, []).append(f.name)

    print(f"\n{len(files)} canonical movements audited")
    for det, n in fired.most_common():
        print(f"  {det:34} {n:2}/{len(files)}  {where[det][:4]}")

    over = {det: n for det, n in fired.items() if n > _TOLERATED.get(det, 0)}
    assert not over, (
        "detector(s) fire on canonical music beyond the tolerated rate: "
        + ", ".join(
            f"{d} on {n}/{len(files)} (tolerated {_TOLERATED.get(d, 0)})" for d, n in over.items()
        )
        + " — a detector that flags what real composers write does not measure "
        "the music, it measures the threshold."
    )


@pytest.mark.calibration
def test_detectors_still_catch_the_baseline_defects():
    """The other half: a bound loose enough to pass everything is also useless.

    Synthesises the baseline score's signature defects and asserts the audit
    still names them.
    """
    warnings.filterwarnings("ignore")
    import music21

    from scales.score_realism import (
        _bar_table,
        detect_articulation_absence,
        detect_dynamic_poverty,
        detect_notation_spam,
    )

    s = music21.stream.Score()
    p = music21.stream.Part()
    for bar in range(1, 41):
        m = music21.stream.Measure(number=bar)
        if bar % 2:
            m.insert(0.0, music21.expressions.TextExpression("rit."))
        else:
            m.insert(0.0, music21.expressions.TextExpression("a tempo"))
        for beat in range(4):
            m.insert(float(beat), music21.note.Note("C4", quarterLength=1.0))
        p.append(m)
    s.insert(0, p)
    bars = _bar_table(s)

    assert detect_articulation_absence(bars), "zero articulations in 40 bars must be flagged"
    assert detect_dynamic_poverty(bars, 0), "zero dynamics in 40 bars must be flagged"
    spam = detect_notation_spam(bars)
    assert spam, "a tempo direction on every other bar must be flagged"
    assert any("rit" in f["problem"] for f in spam)


def test_tolerated_false_positives_are_advisory_only():
    """Fast guard: anything allowed to fire on real music must be `info`.

    A detector with a known false-positive rate must never be able to drive a
    revision, whatever the reference corpus is doing on this machine.
    """
    import inspect

    from scales import score_realism

    for name in _TOLERATED:
        fn = getattr(score_realism, f"detect_{name}", None) or getattr(
            score_realism, f"detect_{name.replace('_absent', '_absence')}", None
        )
        assert fn is not None, f"no detector function found for {name}"
        src = inspect.getsource(fn)
        assert "_WARN" not in src, (
            f"{fn.__name__} fires on canonical music but can emit a warning; "
            "detectors with a known false-positive rate must be _INFO only"
        )


def test_no_detector_emits_an_error_severity():
    """`score_realism` is advisory by construction — nothing here may block.

    Checked on the parse tree, not the source text: the severity argument of
    every ``_finding(...)`` call must be one of the two advisory constants.
    `_section_gate` blocks on ``error``-severity findings, so a detector here
    that ever produced one would turn a calibration miss into a hard failure.
    """
    import ast
    import inspect

    from scales import score_realism

    tree = ast.parse(inspect.getsource(score_realism))
    checked = 0
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "_finding"):
            continue
        # _finding(detector, bar, severity, problem, fix_hint, **evidence)
        assert len(node.args) >= 3, "unexpected _finding() signature"
        sev = node.args[2]
        name = getattr(sev, "id", None)
        assert name in ("_WARN", "_INFO"), (
            f"_finding() called with severity {ast.dump(sev)[:60]} at line "
            f"{node.lineno}; score_realism is advisory by construction and "
            "must only ever emit _WARN or _INFO"
        )
        checked += 1
    assert checked >= 12, f"only {checked} _finding() calls found — did the module shrink?"


def test_realism_report_is_wired_into_self_evaluate():
    """The whole module was dead code once. This is what noticed."""
    import inspect

    from scales import scales

    src = inspect.getsource(scales.self_evaluate)
    assert "realism_report" in src, (
        "self_evaluate must run the realism audit — score_realism shipped "
        "complete, tested by nothing and called by nothing, and every score "
        "the system produced carried the defects it was written to catch"
    )


# ─── Calibration claims must match the calibration ───────────────────────────


def test_the_documented_corpus_size_matches_the_harness():
    """Numbers quoted in guidance must be numbers something actually measured.

    Every guidance surface quotes the reference corpus at the composer — the
    brief's "WRITE THE MARKS WITH THE NOTES" block, the craft reference's
    realism table, `score_realism`'s own docstrings. Those numbers are the whole
    argument for each instruction, so a stale one is not cosmetic: it is the
    system asserting a measurement it never made.

    Two surfaces claimed "60 canonical movements" while this harness measures
    26, and `score_realism`'s docstrings claimed calibration ranges that were
    never run at all (`articulation_absent` said real movements carry 0.4-2.1
    marks per bar; the measured minimum is 0.041, which is why its bound fired
    on real music).
    """
    import re

    n = len(_reference_scores())
    if n < 10:
        pytest.skip(f"reference corpus not available ({n} scores found)")

    sources = (
        [
            _REPO / "tools" / "scales" / "composition_brief.py",
            _REPO / "tools" / "scales" / "score_realism.py",
        ]
        + sorted((_REPO / ".claude" / "skills").rglob("*.md"))
        + sorted((_REPO / ".claude" / "agents").glob("*.md"))
    )
    wrong = []
    # "canonical" is this harness's word for its corpus. Other measurements in
    # the same files legitimately use a different one — §6b of the craft
    # reference quotes 22 *real Mozart* movements from a separate texture study
    # — so the guard is scoped to the claims this harness is the source for.
    pattern = re.compile(r"(\d+)[\s-]+canonical\b[^.\n]{0,60}?movements")
    for src in sources:
        if not src.exists():
            continue
        for claimed in pattern.findall(src.read_text()):
            if int(claimed) != n:
                wrong.append(f"{src.name} claims {claimed} movements; the harness measures {n}")
    assert not wrong, "stale corpus-size claim(s):\n  " + "\n  ".join(wrong)


@pytest.mark.calibration
def test_period_register_clears_each_composers_own_repertoire():
    """A detector for "notes the composer's instrument did not have" must not
    fire on that composer's own music. The first ceilings clipped a real Chopin
    mazurka by one semitone."""
    import glob
    import random

    import music21

    from scales.score_realism import _bar_table, detect_out_of_period_register

    cases = [
        ("mozart", "tools/reference_scores/mozart-piano-sonatas/kern/*.krn"),
        ("beethoven", "tools/reference_scores/beethoven-piano-sonatas/kern/*.krn"),
        ("chopin", "tools/reference_scores/chopin-mazurkas/kern/*.krn"),
    ]
    rng = random.Random(7)
    for composer, pattern in cases:
        files = sorted(glob.glob(pattern))
        if not files:
            pytest.skip(f"no reference scores for {composer}")
        fired = []
        for path in rng.sample(files, min(12, len(files))):
            try:
                bars = _bar_table(music21.converter.parse(path))
            except Exception:
                continue
            if detect_out_of_period_register(bars, composer):
                fired.append(Path(path).name)
        assert not fired, f"{composer}'s own keyboard range rejects {composer}'s own music: {fired}"


def test_period_register_catches_an_anachronistic_climax():
    """The concrete case: a "Mozart" pastiche whose climax reaches E-flat 7,
    a fourth above the top of Mozart's fortepiano."""
    from scales.score_realism import detect_out_of_period_register

    bars = [
        {"bar": 35, "staff": 0, "midis": [98, 99, 86]},
        {"bar": 36, "staff": 0, "midis": [98, 74]},
    ]
    found = detect_out_of_period_register(bars, "mozart")
    assert found and found[0]["detector"] == "out_of_period_register"
    assert found[0]["severity"] == "warn", "never blocks — a modern piano plays them"
    # Liszt's Erard had that register; the same notes must not fire for him.
    assert not detect_out_of_period_register(bars, "liszt")
    # An unknown composer has no data, so no claim is made.
    assert not detect_out_of_period_register(bars, "someone-unarmed")


def test_every_detector_defined_is_actually_run():
    """A detector that `realism_report` does not call is dead code.

    This whole module was dead once, and the cost was three months of scores
    with no articulation in them. The same thing at one-detector granularity is
    quieter and just as real: the function exists, its unit test passes, and it
    never sees a note of generated music.
    """
    import ast
    import inspect

    from scales import score_realism

    tree = ast.parse(inspect.getsource(score_realism))
    defined = {
        n.name
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name.startswith("detect_")
    }
    report_src = inspect.getsource(score_realism.realism_report)
    unwired = sorted(name for name in defined if name not in report_src)
    assert not unwired, f"detector(s) defined but never run by realism_report: {unwired}"
    assert len(defined) >= 15, f"only {len(defined)} detectors found — did the module shrink?"


# ─── The blocking family gets its own falsification ──────────────────────────


@pytest.mark.calibration
def test_musical_ear_errors_do_not_fire_on_canonical_music():
    """`musical_ear` is the only family whose findings BLOCK a section.

    `_section_gate` hard-fails on any `error`-severity ear finding, so a false
    error here is the most expensive kind of bug in the system: it rejects music
    that is fine, and the composer has no way to argue.

    One known false positive is tolerated, with its cause: music21's Humdrum
    importer lays out bar 43 of Mozart's K.281 third movement with offsets
    running 0 to 16 inside a 2/2 measure. The music is fine; the parse is not.
    No measurement of the parsed stream can tell "the importer merged some bars"
    apart from "our exporter overflowed one", so the detector is trustworthy on
    the MusicXML this system writes and should not be pointed at freshly
    imported Humdrum without checking.
    """
    warnings.filterwarnings("ignore")
    from scales.musical_ear import ear_report

    files = _reference_scores()
    if len(files) < 10:
        pytest.skip(f"reference corpus not available ({len(files)} scores found)")

    offenders: dict = {}
    for f in files:
        try:
            rep = ear_report(str(f), [], graph=None)
        except Exception:
            continue
        errs = [x for x in rep.get("findings", []) if x.get("severity") == "error"]
        if errs:
            offenders[f.name] = sorted({x.get("detector") for x in errs})

    known = {"sonata03-3.krn"}  # the K.281/iii Humdrum import artifact above
    unexpected = {k: v for k, v in offenders.items() if k not in known}
    print(f"\n{len(files)} canonical movements; ear errors on {sorted(offenders)}")
    assert not unexpected, "musical_ear raises BLOCKING errors on canonical music: " + ", ".join(
        f"{k} {v}" for k, v in unexpected.items()
    )
