"""The four detectors the calibration harness could never fire.

`test_score_realism_calibration` audits reference scores by calling
`realism_report(path)` with no PieceGraph. Without one, `phrase_boundaries`
returns empty lists, and FOUR detectors take their input from it:

    detect_cadence_formula_reuse       bounds["ends"]
    detect_uniform_phrase_lengths      bounds["lengths"]
    detect_identical_phrase_openings   bounds["starts"]
    detect_texture_stasis_across_sections   bounds["sections"]
    detect_no_recurring_material       bounds["starts"] + bounds["ends"]

Each of them returns immediately on an empty sequence. So their clean record in
that harness says nothing about whether they clear real music — they never ran
on it. A check reporting nothing may be unable to report anything, and the
promise in `score_realism`'s docstring that "every threshold was set by running
the detector over the real corpus" was not true of these.

`detect_no_recurring_material` was added afterwards and this file's structural
test is what caught it joining the set — which is the gap not coming back.

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


def _as_rec(bar, staff="rh_display"):
    """A corpus bar record in the shape `_rhythm_sig` / `_contour_sig` read."""
    ev = [e for e in bar.get(staff, []) if e.get("type") != "rest"]
    return {
        "onsets": [round(float(e.get("beat", e.get("offset", 0)) or 0), 4) for e in ev],
        "durations": [round(float(e.get("dur", 0) or 0), 4) for e in ev],
        "tops": [e["midi"] for e in ev if e.get("midi") is not None],
    }


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


@pytest.mark.calibration
def test_identical_phrase_openings_clears_real_music():
    """A returning head-motif is the point of a theme, so this bound has to
    allow real music to reuse an opening figure and still catch a piece where
    even the contrasting phrases open the same way."""
    from scales.score_realism import _contour_sig, _rhythm_sig

    shares = []
    for composer in _COMPOSERS:
        from scripts.build_corpus_indexes import group_by_source, load_bars

        for _src, mvt in group_by_source(load_bars(composer)).items():
            opens = [b for b in mvt if str(b.get("phrase_position", "")).lower() == "opening"]
            recs = [b for b in opens if b.get("rh_display")]
            if len(recs) < 4:
                continue
            counts = Counter((_rhythm_sig(_as_rec(b)), _contour_sig(_as_rec(b))) for b in recs)
            shares.append(counts.most_common(1)[0][1] / len(recs))
    if len(shares) < 50:
        pytest.skip("corpus bar records not available")
    shares.sort()
    rate = sum(1 for v in shares if v >= 0.75) / len(shares)
    print(
        f"\n  identical_phrase_openings: n={len(shares)} "
        f"median={statistics.median(shares):.2f} p90={shares[int(0.9 * len(shares))]:.2f} "
        f"bound=0.75 flagged={rate:.0%}"
    )
    assert rate <= _MAX_FALSE_POSITIVE_RATE, f"fires on {rate:.0%} of real movements"


def test_the_melody_staff_is_resolved_not_assumed():
    """`detect_identical_phrase_openings` read staff index 0.

    That is the melody on a piano grand staff and whichever part happens to be
    first on anything else. `realism_report` already resolves the melody staff
    from the score; the detector ignored it.
    """
    import inspect

    from scales.score_realism import detect_identical_phrase_openings

    src = inspect.getsource(detect_identical_phrase_openings)
    assert "for staff in (0,)" not in src, "the melody staff is hardcoded again"
    assert "melody_staff" in src


@pytest.mark.calibration
def test_no_recurring_material_clears_real_music():
    """The FLAGS half for a detector that mostly FINDS.

    "Nothing in this piece comes back" must not be said of real music. Measured
    as the share of movements whose most common phrase opening (or cadential
    rhythm) appears exactly once.
    """
    from scripts.build_corpus_indexes import group_by_source, load_bars

    from scales.score_realism import _RECURRENCE_MIN_PHRASES, _contour_sig, _rhythm_sig

    stats = {}
    for position, key in (
        ("opening", lambda r: (_rhythm_sig(r), _contour_sig(r))),
        ("cadential", _rhythm_sig),
    ):
        total = flagged = 0
        for composer in (*_COMPOSERS, "schubert", "bach"):
            for _src, mvt in group_by_source(load_bars(composer)).items():
                marked = [
                    b
                    for b in mvt
                    if str(b.get("phrase_position", "")).lower() == position and b.get("rh_display")
                ]
                if len(marked) < _RECURRENCE_MIN_PHRASES:
                    continue
                total += 1
                if Counter(key(_as_rec(b)) for b in marked).most_common(1)[0][1] <= 1:
                    flagged += 1
        stats[position] = (flagged, total)

    if stats["opening"][1] < 50:
        pytest.skip("corpus bar records not available")

    over = {}
    for position, (flagged, total) in sorted(stats.items()):
        rate = flagged / total
        print(f"\n  no_recurring_material ({position}): {flagged}/{total} = {rate:.1%}")
        if rate > _MAX_FALSE_POSITIVE_RATE:
            over[position] = rate
    assert not over, (
        "no_recurring_material says 'nothing comes back' about real movements at "
        + ", ".join(f"{p} {r:.0%}" for p, r in over.items())
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
        # Added after this guard existed, and the guard is what said so — the
        # mirror of the two above, for a piece where nothing comes back.
        "detect_no_recurring_material",
    }
    assert users == expected, (
        f"the set of detectors fed from `phrase_boundaries` changed: {sorted(users)}.\n"
        "These cannot fire in the reference-score calibration harness, which "
        "passes no PieceGraph — so a new one would inherit a clean record it "
        "never earned. Calibrate it here, against corpus bar records."
    )


# ─── A composer's own band needs a composer's worth of movements ─────────────


@pytest.mark.calibration
def test_a_thin_corpus_does_not_get_a_narrow_band_of_its_own():
    """The sample-size guard counted staff-views, and two staves of one
    movement are not independent samples of a composer.

    Liszt cleared a threshold of 8 with 8 views drawn from FOUR pieces, giving
    him a 95th-percentile dominant-value share of 0.714 — narrower than any
    well-armed composer's. A generated Liszt then tripped
    `rhythm_vocabulary_poverty` at 73% and 97%, while real CHOPIN left hands
    exceed 97% in a quarter of his movements and reach 100%. The band was a fact
    about the sample, not about Liszt.

    Four composers were affected: debussy and liszt at 4 movements,
    rimsky-korsakov and vivaldi at 5. They fall back to the wide cross-composer
    band, which errs toward silence — the right failure for a thin corpus.
    """
    import collections

    from scales.composition_brief import _iter_corpus_bars
    from scales.score_realism import _rhythm_vocabulary_bounds

    checked = 0
    for composer in ("liszt", "mozart", "chopin", "haydn"):
        per = collections.defaultdict(int)
        try:
            for bar in _iter_corpus_bars(composer):
                for hand in ("rh_display", "lh_display"):
                    for event in bar.get(hand) or []:
                        if isinstance(event, dict) and event.get("type") != "rest":
                            per[(bar.get("source"), hand)] += 1
        except Exception:
            continue
        movements = {src for (src, _hand), n in per.items() if n >= 40}
        if not movements:
            continue
        checked += 1
        bounds = _rhythm_vocabulary_bounds(composer)
        if len(movements) < 8:
            assert bounds is None, (
                f"{composer} has {len(movements)} movements and still gets a band "
                f"of its own: {bounds}"
            )
        else:
            assert bounds is not None, f"{composer} has {len(movements)} movements and no band"
    if checked < 2:
        pytest.skip("corpus not available")


def test_the_detector_still_catches_a_staff_of_one_value():
    """The other falsification question. A band wide enough to say nothing
    about anything would pass the test above and be useless.
    """
    from scales.score_realism import detect_rhythm_vocabulary_poverty

    one_value = [{"staff": 0, "bar": i + 1, "durations": [1.0]} for i in range(60)]
    for composer in ("liszt", "mozart", ""):
        assert detect_rhythm_vocabulary_poverty(one_value, composer=composer), composer

    varied = [
        {"staff": 0, "bar": i + 1, "durations": [[0.25, 0.5, 1.0, 1.5, 2.0][i % 5]]}
        for i in range(60)
    ]
    for composer in ("liszt", "mozart"):
        assert not detect_rhythm_vocabulary_poverty(varied, composer=composer), composer
