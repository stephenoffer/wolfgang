"""Unit tests for convergence.py. Run: python3 tools/scales/tests/test_convergence.py"""

from scales import convergence as C


def test_errors_dominate():
    # candidate with an error can NEVER beat a clean one, even with great corpus/critic
    dirty = {"error_count": 1, "warn_count": 0, "corpus_distance": 0.0, "critic_quality": 5.0}
    clean = {"error_count": 0, "warn_count": 9, "corpus_distance": 9.0, "critic_quality": 0.0}
    assert C.dominates(clean, dirty)
    assert not C.dominates(dirty, clean)


def test_keep_best_no_regression():
    best = {"error_count": 0, "warn_count": 2, "corpus_distance": 1.0, "critic_quality": 4.0}
    worse = {"error_count": 0, "warn_count": 3, "corpus_distance": 1.0, "critic_quality": 4.0}
    better = {"error_count": 0, "warn_count": 1, "corpus_distance": 1.0, "critic_quality": 4.0}
    assert not C.dominates(worse, best)  # do not replace with a regression
    assert C.dominates(better, best)  # replace with a strict improvement


def test_corpus_distance_only_penalizes_out_of_band():
    div = {"metrics": {"a": {"z": 1.5}, "b": {"z": 3.0}, "c": {"z": -4.0}}}
    # |1.5|<2 → 0 ; |3|-2=1 ; |4|-2=2  → total 3.0
    assert C.corpus_distance(div) == 3.0


def test_pareto_improves():
    before = {"vertical_clash": 1, "monotony": 2}
    fixed = {"vertical_clash": 0, "monotony": 2}  # one better, none worse
    assert C.pareto_improves(fixed, before)
    assert not C.pareto_improves(before, before)  # no improvement


def test_pareto_rejects_trading_one_real_defect_for_another():
    before = {"monotony": 2, "no_breathing": 0}
    traded = {"monotony": 1, "no_breathing": 2}  # de-monotonized by removing the breath
    assert not C.pareto_improves(traded, before)


def test_pareto_tolerates_movement_in_advisory_detectors():
    """A real musical revision jostles the idiom-level detectors — an added
    appoggiatura registers as a clash. Requiring that literally nothing move up
    rejected every genuine improvement and stalled the loop on attempt one."""
    before = {"monotony": 3, "vertical_clash": 0}
    revised = {"monotony": 1, "vertical_clash": 2}
    assert C.pareto_improves(revised, before)


def test_advisory_warnings_do_not_decide_the_ranking():
    """Counting idiom warnings in the ordering made the loop prefer the blandest
    candidate: a cross-relation the detector itself calls idiomatic cost as much
    as a real defect."""
    bland = {"error_count": 0, "warn_count": 0, "critic_quality": 3.0, "detector_counts": {}}
    rich = {
        "error_count": 0,
        "warn_count": 5,
        "critic_quality": 4.5,
        "detector_counts": {"vertical_clash": 5},
    }
    assert C.composite_score(rich) > C.composite_score(bland)


def test_converged():
    base = dict(error_count=0, critic_quality=4.2, section_gate_passed=True, critic_approved=True)
    assert C.converged(**base)
    assert not C.converged(**{**base, "error_count": 1})  # a hard error blocks
    assert not C.converged(**{**base, "critic_quality": 3.0})  # below quality bar
    assert not C.converged(**{**base, "critic_approved": False})  # critic's ears rule
    assert not C.converged(**{**base, "section_gate_passed": False})
    # corpus divergence is ADVISORY — an out-of-band z must NOT block (real
    # Chopin/Beethoven sit outside a MIDI corpus's narrow bands).
    assert C.converged(**{**base, "corpus_divergence": {"metrics": {"a": {"z": 9.0}}}})


if __name__ == "__main__":
    import sys

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ok  {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
