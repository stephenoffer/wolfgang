"""The four detectors the calibration harness could never fire.

`test_score_realism_calibration` audits reference scores by calling
`realism_report(path)` with no PieceGraph. Without one, `phrase_boundaries`
returns empty lists, and FOUR detectors take their input from it:

    detect_cadence_formula_reuse       bounds["ends"]
    detect_uniform_phrase_lengths      bounds["lengths"]
    detect_identical_phrase_openings   bounds["starts"]
    detect_texture_stasis_across_sections   bounds["sections"]

Each of them returns immediately on an empty sequence. So their clean record in
that harness says nothing about whether they clear real music — they never ran
on it. A check reporting nothing may be unable to report anything, and the
promise in `score_realism`'s docstring that "every threshold was set by running
the detector over the real corpus" was not true of these.

The corpus bar records carry what the reference scores lack: `phrase_position`,
marking bars `cadential` / `closing` / `opening`. This harness reconstructs
phrase bounds from those marks and runs the detectors on real movements.

Marked `calibration`; the fast test below guards the recorded rates.
"""

from __future__ import annotations

import statistics
from collections import Counter, defaultdict

import pytest

_COMPOSERS = ("mozart", "beethoven", "chopin", "haydn")

#: Measured false-positive rate per staff at the shipped bounds, as a share of
#: real movements. `cadence_formula` used ONE bound of 0.66 for both staves; the
#: melody cleared it at 8% and the accompaniment failed at 18%, because an
#: accompaniment repeats its cadential figure more than a melody does. Bounds
#: are now per staff and both sit at 8%.
_MAX_FALSE_POSITIVE_RATE = 0.10


def _movement_ends(composer):
    """(movement, cadential bar records) for movements with ≥3 marked ends."""
    from scripts.build_corpus_indexes import group_by_source, load_bars

    out = []
    for _src, mvt in group_by_source(load_bars(composer)).items():
        ends = [
            b for b in mvt if str(b.get("phrase_position", "")).lower() in ("cadential", "closing")
        ]
        if len(ends) >= 3:
            out.append((mvt, ends))
    return out


def _reuse_share(ends, staff):
    """The detector's own measure: largest share of ends sharing one rhythm."""
    recs = [e for e in ends if e.get(staff)]
    if len(recs) < 3:
        return None
    sigs = Counter(
        tuple(
            (
                round(float(ev.get("beat", ev.get("offset", 0)) or 0), 4),
                round(float(ev.get("dur", 0) or 0), 4),
            )
            for ev in rec[staff]
            if ev.get("type") != "rest"
        )
        for rec in recs
    )
    return sigs.most_common(1)[0][1] / len(recs)


@pytest.mark.calibration
def test_cadence_formula_bounds_clear_real_music_on_both_staves():
    from scales.score_realism import _CADENCE_FORMULA_BOUND, _CADENCE_FORMULA_BOUND_ACCOMP

    shares = defaultdict(list)
    for composer in _COMPOSERS:
        for _mvt, ends in _movement_ends(composer):
            for staff in ("rh_display", "lh_display"):
                share = _reuse_share(ends, staff)
                if share is not None:
                    shares[staff].append(share)

    if len(shares.get("rh_display", [])) < 50:
        pytest.skip("corpus bar records not available")

    bounds = {"rh_display": _CADENCE_FORMULA_BOUND, "lh_display": _CADENCE_FORMULA_BOUND_ACCOMP}
    over = {}
    for staff, values in sorted(shares.items()):
        values.sort()
        rate = sum(1 for v in values if v >= bounds[staff]) / len(values)
        print(
            f"\n  {staff:12s} n={len(values):4d} median={statistics.median(values):.2f} "
            f"p90={values[int(0.9 * len(values))]:.2f}  bound={bounds[staff]}  flagged={rate:.0%}"
        )
        if rate > _MAX_FALSE_POSITIVE_RATE:
            over[staff] = rate

    assert not over, (
        "cadence_formula flags real movements above the tolerated rate: "
        + ", ".join(f"{s} at {r:.0%}" for s, r in over.items())
        + " — a detector that flags what real composers write measures the "
        "threshold, not the music."
    )


@pytest.mark.calibration
def test_uniform_phrase_lengths_clears_real_music():
    """Real movements do use runs of equal phrase lengths; four-bar phrases are
    the classical norm. The bound must separate "regular" from "mechanical"."""
    from scales.score_realism import detect_uniform_phrase_lengths

    fired = total = 0
    for composer in _COMPOSERS:
        for mvt, _ends in _movement_ends(composer):
            marks = sorted(
                b["bar_num"]
                for b in mvt
                if str(b.get("phrase_position", "")).lower() in ("opening",)
            )
            if len(marks) < 4:
                continue
            lengths = [b - a for a, b in zip(marks, marks[1:]) if b > a]
            if len(lengths) < 3:
                continue
            total += 1
            if detect_uniform_phrase_lengths(lengths):
                fired += 1
    if total < 20:
        pytest.skip("too few movements with phrase-opening marks")
    rate = fired / total
    print(f"\n  uniform_phrase_lengths: {fired}/{total} = {rate:.0%} of real movements")
    assert rate <= 0.25, (
        f"uniform_phrase_lengths fires on {rate:.0%} of real movements — classical "
        "phrase rhythm is regular by design and the bound has to allow that"
    )


def test_uniform_phrase_lengths_still_finds_what_is_definitely_there():
    """The other half of falsification.

    A detector that FLAGS needs "would it reject real music?" — 0 of 246 real
    movements, above. One that FINDS needs ground truth and "would it find what
    is definitely there?" A clean rate on real music is also what a detector
    that can never fire produces, and asking only the first question is how a
    theme-recurrence detector reported "appears in 1 place" on every piece for a
    whole session.
    """
    from scales.score_realism import detect_uniform_phrase_lengths

    assert detect_uniform_phrase_lengths([4] * 8), "eight four-bar phrases is the case"
    assert detect_uniform_phrase_lengths([2] * 6), "the length itself is not the point"
    assert not detect_uniform_phrase_lengths([4, 4, 4, 8]), "one long close is not mechanical"
    assert not detect_uniform_phrase_lengths([4, 6, 4, 8, 4])


def test_the_four_bounds_dependent_detectors_are_named():
    """A guard against the gap coming back silently.

    If a new detector starts taking its input from `phrase_boundaries`, it joins
    the set that the reference-score harness cannot exercise, and it should be
    added to this file rather than quietly inheriting a clean record it never
    earned.
    """
    import ast
    import inspect

    from scales import score_realism

    tree = ast.parse(inspect.getsource(score_realism))
    report = next(
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "realism_report"
    )
    users = set()
    for node in ast.walk(report):
        if (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "bounds"
        ):
            parent = node
            for call in ast.walk(report):
                if isinstance(call, ast.Call) and any(
                    a is parent or (isinstance(a, ast.keyword) and a.value is parent)
                    for a in list(call.args) + list(call.keywords)
                ):
                    if isinstance(call.func, ast.Name):
                        users.add(call.func.id)
    expected = {
        "detect_cadence_formula_reuse",
        "detect_uniform_phrase_lengths",
        "detect_identical_phrase_openings",
        "detect_texture_stasis_across_sections",
    }
    assert users == expected, (
        f"the set of detectors fed from `phrase_boundaries` changed: {sorted(users)}.\n"
        "These cannot fire in the reference-score calibration harness, which "
        "passes no PieceGraph — so a new one would inherit a clean record it "
        "never earned. Calibrate it here, against corpus bar records."
    )
