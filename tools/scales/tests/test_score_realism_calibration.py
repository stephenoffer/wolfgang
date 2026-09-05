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


def test_tolerated_false_positives_are_advisory_only(function_source):
    """Fast guard: anything allowed to fire on real music must be `info`.

    A detector with a known false-positive rate must never be able to drive a
    revision, whatever the reference corpus is doing on this machine.
    """

    from scales import score_realism

    for name in _TOLERATED:
        fn = getattr(score_realism, f"detect_{name}", None) or getattr(
            score_realism, f"detect_{name.replace('_absent', '_absence')}", None
        )
        assert fn is not None, f"no detector function found for {name}"
        src = function_source(score_realism, fn.__name__)
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


def test_realism_report_is_wired_into_self_evaluate(function_source):
    """The whole module was dead code once. This is what noticed."""

    from scales import scales

    src = function_source(scales, "self_evaluate")
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
    # A claim MAY cite a corpus other than this harness's — a wider re-measure
    # against several repertoires is exactly the right way to falsify a bound
    # that a Classical-only corpus made look safe. But then it has to SHOW ITS
    # WORK: an itemised breakdown, immediately below, whose denominators sum to
    # the number claimed. That keeps the guard's whole purpose (no asserting a
    # measurement nobody made) while letting a real wider measurement through,
    # instead of forcing it to be reworded until the regex stops noticing.
    breakdown = re.compile(r"/(\d+)\b")
    for src in sources:
        if not src.exists():
            continue
        text = src.read_text()
        for match in pattern.finditer(text):
            claimed = int(match.group(1))
            if claimed == n:
                continue
            following = text[match.end() : match.end() + 1200]
            itemised = [int(d) for d in breakdown.findall(following)]
            # A breakdown may or may not carry a TOTAL row ("0/82  all"). Accept
            # either shape: the parts sum to the claim, or a total row states it
            # outright. Counting the total as one more part is how this first
            # read 16+16+16+16+18+82 and called a correct table unsubstantiated.
            parts = [d for d in itemised if d != claimed]
            if claimed in itemised or (parts and sum(parts) == claimed):
                continue  # cites its own corpus and adds up
            wrong.append(
                f"{src.name} claims {claimed} movements; the harness measures {n} "
                f"(and no itemised breakdown below it sums to {claimed})"
            )
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


def test_every_detector_defined_is_actually_run(function_source):
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
    report_src = function_source(score_realism, "realism_report")
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

    Two known false positives are tolerated, both with the same cause:
    music21's Humdrum importer collapses a span of source into one measure, so
    Mozart K.281/iii bar 43 parses as 16 beats inside a 2/2 bar, and Beethoven
    Op.2 No.2/i bar 54 parses as **465**. The music is fine; the parse is not.
    No measurement of the parsed stream can tell "the importer merged some bars"
    apart from "our exporter overflowed one", so the detector is trustworthy on
    the MusicXML this system writes and should not be pointed at freshly
    imported Humdrum without checking.

    Note the offenders are keyed by their path under `reference_scores/`, not by
    filename: the Mozart and Beethoven directories both contain a
    `sonata02-1.krn`, and keying by name alone silently conflated them.
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
            key = str(f.relative_to(_REF))
            offenders[key] = sorted({x.get("detector") for x in errs})

    # Humdrum import artifacts — see `detect_bar_length_errors`. This allowlist
    # was TWO filenames, and it held only because the sample above draws 14
    # Mozart files, 6 Chopin and 6 Beethoven. Measured over all 224 files in
    # `reference_scores/`, 36 of them (16%) raise a blocking error: 26% of the
    # Beethoven sonatas, 10% of the Mozart, 4% of the mazurkas. Every one is
    # music21's Humdrum importer merging bars — extents run as high as 465 beats
    # inside a 2/4 measure — and the ratio does not separate them from a real
    # overflow, so there is nothing to detect our way out of. Naming the files
    # was hiding the rate behind a sample; the rate is asserted instead.
    known = {
        "mozart-piano-sonatas/kern/sonata03-3.krn",
        "beethoven-piano-sonatas/kern/sonata02-1.krn",
    }
    unexpected = {k: v for k, v in offenders.items() if k not in known}
    non_bar_length = {
        k: v for k, v in unexpected.items() if any(d != "bar_length" for d in v)
    }
    print(f"\n{len(files)} canonical movements; ear errors on {sorted(offenders)}")
    assert not non_bar_length, (
        "musical_ear raises BLOCKING errors on canonical music for something "
        "other than the documented Humdrum import artifact: "
        + ", ".join(f"{k} {v}" for k, v in non_bar_length.items())
    )
    rate = len(offenders) / len(files)
    assert rate <= 0.25, (
        f"bar_length blocks {rate:.0%} of this sample, above the 16% measured "
        f"across all of reference_scores/ — the importer artifact has grown or a "
        f"real regression is hiding in it"
    )


@pytest.mark.calibration
def test_an_inaudible_overfull_bar_does_not_block():
    """A bar can run past its barline because a voice's trailing REST is long.
    Nothing sounds late, and real engraving does it constantly: of the overfull
    bars found in real scores, 56/56 Monteverdi and 11/11 Haydn were rests-only.
    They were raising BLOCKING errors — 56% of real Haydn quartets and 12% of
    real Monteverdi madrigals could not have passed a section gate — and this
    system's own engraver writes them too (69 across three workspace pieces).

    A note sounding past the barline stays an error: that is the shape every
    notation bug here has actually had (7.5 beats in 4/4 from a pedal figure
    parsed sequentially).
    """
    warnings.filterwarnings("ignore")
    from music21 import corpus

    from scales.musical_ear import ear_report

    for composer, limit in (("haydn", 12), ("monteverdi", 25), ("palestrina", 25)):
        try:
            paths = [str(p) for p in corpus.getComposer(composer)[:limit]]
        except Exception:  # pragma: no cover - corpus not installed
            pytest.skip(f"music21 corpus has no {composer}")
        blocked, scored = [], 0
        for path in paths:
            try:
                rep = ear_report(path, [], graph=None)
            except Exception:
                continue
            scored += 1
            if any(f.get("severity") == "error" for f in rep.get("findings", [])):
                blocked.append(path.split("/")[-1])
        if scored < 8:
            pytest.skip(f"only {scored} {composer} movements parsed")
        print(f"\n{composer}: {len(blocked)}/{scored} blocked")
        assert not blocked, (
            f"musical_ear BLOCKS real {composer}: {blocked} — an overfull bar made "
            f"only of rests is inaudible and must not fail a section gate"
        )


@pytest.mark.calibration
def test_detectors_do_not_reject_ensemble_music():
    """The harness above reads only `reference_scores/`, which is Mozart,
    Beethoven and Chopin — so every threshold in `score_realism` was falsified
    against Classical and Romantic piano music and against nothing else. Two
    detectors turned out to be describing that repertoire rather than music:

        syncopation_absent          fired on 40/40 real Palestrina, 17/30 Monteverdi
        rhythm_vocabulary_poverty   fired on 10/40 Palestrina, 11/30 Monteverdi

    Renaissance vocal polyphony puts nearly every attack on a beat — its
    characteristic displacement, the suspension, is a whole beat long — and it
    draws on a deliberately narrow set of note values. Neither is a defect, and
    a warning that is wrong that often teaches the critic to discount the ones
    that are right.

    This test reads music21's own corpus rather than `reference_scores/`, which
    holds no early music at all.
    """
    warnings.filterwarnings("ignore")
    from music21 import corpus

    from scales.score_realism import realism_report

    # Measured after the fix; a little headroom so one odd parse cannot fail CI.
    # Every entry here was above 0 before the fix, several far above: the shipped
    # bounds were measured on a 2-staff piano corpus and several of them turned
    # out to describe the grand staff rather than music. Rates before -> after:
    #
    #   voicing_poverty        mozart 50% haydn 78% palestrina 76% monteverdi 40% -> 0
    #   register_stasis        palestrina 100% monteverdi 68% haydn 11%           -> 0
    #   syncopation_absent     palestrina 100% monteverdi 57%                     -> 0
    #   rhythm_vocab_poverty   monteverdi 36% palestrina 29% haydn 22% bach 15%   -> <=16%
    #   melody_vocab_poverty   mozart 29% palestrina 24% monteverdi 24%           -> 0
    #   scalar_overuse         haydn 22% palestrina 16%                           -> 0
    _ENSEMBLE = {
        "syncopation_absent": 0.05,
        "voicing_poverty": 0.05,
        "register_stasis": 0.05,
        "scalar_overuse": 0.10,
        "melody_vocabulary_poverty": 0.10,
        "accompaniment_vocabulary_poverty": 0.10,
    }
    ceilings = {
        "palestrina": {**_ENSEMBLE, "rhythm_vocabulary_poverty": 0.15},
        "monteverdi": {**_ENSEMBLE, "rhythm_vocabulary_poverty": 0.25},
        "haydn": {**_ENSEMBLE, "rhythm_vocabulary_poverty": 0.15},
        "mozart": {**_ENSEMBLE, "rhythm_vocabulary_poverty": 0.15},
    }
    for composer, limits in ceilings.items():
        try:
            paths = [str(p) for p in corpus.getComposer(composer)[:30]]
        except Exception:  # pragma: no cover - corpus not installed
            pytest.skip(f"music21 corpus has no {composer}")
        fires: Counter = Counter()
        scored = 0
        for path in paths:
            try:
                rep = realism_report(path, composer=composer)
            except Exception:
                continue
            scored += 1
            for name in {f.get("detector") for f in rep.get("findings") or []}:
                fires[name] += 1
        if scored < 8:
            pytest.skip(f"only {scored} {composer} movements parsed")
        for detector, ceiling in limits.items():
            rate = fires[detector] / scored
            print(f"\n{composer}: {detector} fires on {fires[detector]}/{scored} ({rate:.0%})")
            assert rate <= ceiling, (
                f"{detector} fires on {rate:.0%} of real {composer} "
                f"(ceiling {ceiling:.0%}) — it is rejecting canonical music"
            )
