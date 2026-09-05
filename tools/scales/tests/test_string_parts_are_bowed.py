"""String parts must be bowed, because for a string player the slur IS the bowing.

Parts built from the piano core's melody inherit its slurs. Parts built from the
BASS inherit nothing — a pianist's left hand is not phrased the way a cello is
bowed — so they arrived with no slur in them at all: measured on a real
orchestration off this system, cello 60 notes / 0 slurs, viola 0.

Slurs per 100 notes over 82 real multi-part scores, as a RANGE rather than a
mean, since a mean is not a bound:

    violin  n=103  min 1.4  median 14.9  max 26.5
    viola   n= 51  min 1.0  median 11.4  max 24.5
    cello   n= 49  min 0.3  median  9.5  max 21.6
"""

from scales.orchestration_planner import _REAL_STRING_SLUR_RANGE, _bow_string_parts


def _line(runs):
    return [
        {"bar": b, "beat": float(i + 1), "pitch": p, "duration": "q"}
        for b, run in enumerate(runs, start=1)
        for i, p in enumerate(run)
    ]


CONJUNCT = [
    ["C3", "D3", "E3", "F3"],
    ["G3", "F3", "E3", "D3"],
    ["C3", "G3", "C4", "G3"],
    ["E3", "F3", "G3", "A3"],
]


def test_a_bass_derived_string_part_gets_bowing():
    parts = {"cello": _line(CONJUNCT)}
    _bow_string_parts(parts)
    assert any(e.get("slur") == "start" for e in parts["cello"])


def test_the_bowing_rate_stays_inside_what_real_cellos_do():
    parts = {"cello": _line(CONJUNCT)}
    _bow_string_parts(parts)
    ev = parts["cello"]
    rate = 100 * sum(1 for e in ev if e.get("slur") == "start") / len(ev)
    lo, hi = _REAL_STRING_SLUR_RANGE["cello"]
    assert rate <= hi, f"{rate:.1f} per 100 is more bowed than any real cello part"


def test_a_leap_takes_a_bow_change():
    """Bar 3 is C3-G3-C4-G3 — all leaps. Slurring across them is not phrasing,
    it is an unplayable bowing."""
    parts = {"cello": _line(CONJUNCT)}
    _bow_string_parts(parts)
    bar3 = [e for e in parts["cello"] if e["bar"] == 3]
    assert not any(e.get("slur") for e in bar3)


def test_a_slur_never_crosses_a_barline_it_was_not_asked_to():
    parts = {"cello": _line(CONJUNCT)}
    _bow_string_parts(parts)
    for e in parts["cello"]:
        if e.get("slur") == "start":
            stop = next(
                x
                for x in parts["cello"]
                if x["bar"] >= e["bar"]
                and x.get("slur") == "stop"
                and (x["bar"], x["beat"]) >= (e["bar"], e["beat"])
            )
            assert stop["bar"] == e["bar"]


def test_a_bassoon_is_never_bowed():
    """`"bass"` as a substring matches `bassoon`, a double reed that has never
    been bowed. This is the bug that catch exists for."""
    parts = {"bassoon": _line(CONJUNCT)}
    _bow_string_parts(parts)
    assert not any(e.get("slur") for e in parts["bassoon"])


def test_a_part_that_already_carries_phrasing_is_left_alone():
    ev = _line(CONJUNCT)
    ev[0]["slur"] = "start"
    ev[1]["slur"] = "stop"
    parts = {"violin_i": ev}
    _bow_string_parts(parts)
    assert sum(1 for e in ev if e.get("slur") == "start") == 1
