"""The ear's bar-record detectors, measured against real music.

CLAUDE.md's standing rule: "Falsify every rule against real scores. Before any
check is allowed to block or even warn at scale, ask whether it would reject
canonical music, and test it." A detector that fires on most of the repertoire is
noise the critic has to triage away, which is worse than no detector.

These bounds are what the detectors measure TODAY on the rebuilt corpus. They are
deliberately loose — the point is to catch a regression that makes a detector
start rejecting real music, not to pin an exact number.

**Both halves, because a false-positive bound on its own rewards blindness.** A
detector that never fires passes every specificity test trivially. Three
detectors in this project failed the other way in the same week — one reported
"the theme appears in 1 place" on every piece regardless of the notes, one found
`pending_resolution` on 49% of real phrase endings, and `unresolved_nct` rejected
83% of canonical Mozart. Asking "would this reject real music?" catches the third
and is blind to the first two. So the sensitivity tests below hand each detector
a case that is unambiguously the defect and require it to fire.

Marked `calibration` because it reads the corpus; run with `pytest -m calibration`.
"""

import collections

import pytest

from scales import musical_ear as ME
from scales.composition_brief import _iter_corpus_bars

pytestmark = pytest.mark.calibration

_COMPOSERS = ("mozart", "beethoven", "chopin", "bach", "haydn")

# detector -> the most real movements it may fire on, as a fraction.
# unresolved_nct began at 0.83 (10 of 12 real Mozart movements, every case a
# secondary dominant's leading tone inside an arpeggio) before three conditions
# were added; see its docstring.
_MAX_FALSE_POSITIVE_RATE = {
    "unresolved_nct": 0.20,
    "no_breathing": 0.35,
    "monotony": 0.35,
    "arpeggiated_melody": 0.45,
    "static_bass": 0.45,
}


def _movements(composer, minimum=16, cap=12):
    by = collections.defaultdict(list)
    for bar in _iter_corpus_bars(composer):
        by[bar.get("source")].append(bar)
    out = [sorted(v, key=lambda b: b.get("bar_num", 0)) for v in by.values() if len(v) >= minimum]
    return out[:cap]


@pytest.mark.parametrize("name,rate", sorted(_MAX_FALSE_POSITIVE_RATE.items()))
def test_a_detector_may_not_fire_on_most_of_the_repertoire(name, rate):
    fn = getattr(ME, f"detect_{name}")
    fired = total = 0
    for composer in _COMPOSERS:
        movements = _movements(composer)
        if not movements:
            continue
        total += len(movements)
        fired += sum(1 for m in movements if fn(m))
    if not total:
        pytest.skip("no corpus available")
    observed = fired / total
    assert observed <= rate, (
        f"detect_{name} fires on {fired}/{total} = {observed:.0%} of real movements "
        f"(bound {rate:.0%}). A check that rejects canonical music is broken, not strict."
    )


def test_no_bar_record_detector_reports_an_error_on_real_music():
    """Only PHYSICAL defects may be errors, and real scores have none."""
    offenders = []
    for composer in _COMPOSERS:
        for movement in _movements(composer):
            for name in _MAX_FALSE_POSITIVE_RATE:
                for finding in getattr(ME, f"detect_{name}")(movement):
                    if finding.get("severity") == "error":
                        offenders.append(f"{name} on {movement[0].get('source')}")
    assert not offenders, "error-severity findings on real music: " + "; ".join(offenders[:5])


# ── Sensitivity: does the detector find what is definitely there? ─────────────


def _notes(pitches, dur=0.5):
    import music21

    return [
        {"type": "note", "pitch": p, "midi": music21.pitch.Pitch(p).midi, "dur": dur}
        for p in pitches
    ]


def _bar(n, melody, **overrides):
    bar = {
        "bar_num": n,
        "key": "C",
        "key_mode": "major",
        "roman": "I",
        "time_sig": [4, 4],
        "phrase_position": "middle",
        "melody_line": melody,
        "rh_display": [{"type": "note", "pitch": e.get("pitch"), "dur": e["dur"]} for e in melody],
        "lh_display": [],
        "melody_density": len(melody),
        "accomp_density": 4,
    }
    bar.update(overrides)
    return bar


def _unambiguous_cases():
    """One case per detector that is, by construction, the defect it names."""
    return {
        # A chromatic note leapt to AND from, inside an otherwise stepwise line.
        "unresolved_nct": [_bar(1, _notes(["C5", "D5", "E5", "Ab5", "D5", "E5", "F5", "G5"]))],
        # A cadential bar of unbroken eighths: the line never comes to rest.
        "no_breathing": [
            _bar(
                1,
                _notes(["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]),
                phrase_position="cadential",
            )
        ],
        # Five bars of identical rhythm and identical contour.
        "monotony": [_bar(i, _notes(["C5", "D5", "E5", "F5"])) for i in range(1, 6)],
        # Five bars of pure chord tones reached by leap — accompaniment on the
        # top staff, which is what "the melody does not sing" looks like.
        "arpeggiated_melody": [
            _bar(i, _notes(["C5", "E5", "G5", "C6", "G5", "E5"])) for i in range(1, 6)
        ],
        # One unchanging bass note under a moving melody, harmony static too.
        "static_bass": [
            _bar(
                i,
                _notes(["C5", "D5", "E5", "F5"]),
                lh_display=[{"type": "note", "pitch": "C2", "dur": 4.0}],
            )
            for i in range(1, 7)
        ],
    }


@pytest.mark.parametrize("name", sorted(_MAX_FALSE_POSITIVE_RATE))
def test_a_detector_must_find_the_defect_it_names(name):
    fn = getattr(ME, f"detect_{name}")
    findings = fn(_unambiguous_cases()[name])
    assert findings, (
        f"detect_{name} found nothing in a case constructed to BE that defect. "
        f"A detector that never fires passes every false-positive bound trivially; "
        f"specificity without sensitivity is not a working check."
    )


def test_the_chromatic_check_is_not_blinded_by_its_own_texture_guard():
    """The leap-texture guard must not swallow a wrong note in a long lyrical line.

    It skips bars whose melody is majority leaps, because in a broken-chord
    figure every note is leapt to. A ten-note stepwise line with one chromatic
    leap is the opposite case and must still be caught.
    """
    # Ten intervals, two of them leaps: the C#6 is leapt to AND from inside a
    # line that is otherwise stepwise, which is the shape a wrong note takes.
    line = ["C5", "D5", "E5", "F5", "G5", "C#6", "G5", "A5", "B5", "C6", "D6"]
    findings = ME.detect_unresolved_nct([_bar(1, _notes(line))])
    assert findings, "a chromatic leap inside a stepwise line must still be caught"
    # Named the way the KEY writes it — C major spells that pitch class D-flat —
    # so assert the pitch, not one enharmonic spelling of it.
    assert any(x in findings[0]["problem"] for x in ("Db6", "C#6")), findings[0]["problem"]


# ── The anti-pattern detectors, both halves ──────────────────────────────────
#
# Four of the ten never fired on their own defect. `flat_dynamics` returned
# "insufficient dynamics data" when a phrase had NO dynamic at all — the extreme
# case of the thing it names, and the state 91.3% of every note this project has
# ever committed is in. `ornament_wallpaper` read `layer.ornamental_surface`, a
# layer the shorthand path never populates (an ornament written `C5q:tr` is a
# FIELD on a note in `principal_line`), so it searched an empty drawer.


def _ev(bar, beat, pitch, dur="q", **kw):
    from scales.models import LayerEvent

    return LayerEvent(bar=bar, beat=beat, pitch=pitch, duration=dur, **kw)


def _layer(melody, bass=None, response=None, bars=8):
    from scales.models import LayerIR

    ir = LayerIR(key="C major", meter=(4, 4), bar_count=bars)
    ir.principal_line = melody
    ir.bass_foundation = bass or []
    ir.response_layer = response or []
    return ir


def _anti_pattern_positives():
    flat = [_ev(b, i + 1.0, "C5") for b in range(1, 9) for i in range(4)]
    prev = _layer(
        [_ev(b, i + 1.0, p) for b in range(1, 5) for i, p in enumerate(["C5", "D5", "E5", "F5"])],
        bars=4,
    )
    return {
        "flat_dynamics": (_layer(flat),),
        "same_accompaniment": (
            _layer(
                flat,
                response=[
                    _ev(b, i + 1.0, p, "e")
                    for b in range(1, 9)
                    for i, p in enumerate(["C4", "E4", "G4", "C5"])
                ],
            ),
        ),
        "register_monotony": (_layer(flat),),
        "missing_silence": (_layer(flat),),
        "ornament_wallpaper": (_layer([_ev(b, 1.0, "C5", ornament="trill") for b in range(1, 9)]),),
        "metronomic_rhythm": (_layer(flat),),
        "root_position_bias": (_layer(flat, bass=[_ev(b, 1.0, "C2", "w") for b in range(1, 9)]),),
        "scalar_fill": (
            _layer(
                [
                    _ev(1, 1 + i * 0.5, p, "e")
                    for i, p in enumerate(["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"])
                ]
            ),
        ),
        "safe_harmony": (
            _layer(flat, bass=[_ev(b, 1.0, p, "w") for b, p in zip(range(1, 9), ["C2", "G2"] * 4)]),
        ),
        "identical_restatement": (prev, prev),
    }


@pytest.mark.parametrize("name", sorted(_anti_pattern_positives()))
def test_an_anti_pattern_detector_must_find_its_own_defect(name):
    from scales import anti_pattern_detector as AP

    fired, _severity, message = getattr(AP, f"detect_{name}")(*_anti_pattern_positives()[name])
    assert fired, (
        f"detect_{name} found nothing in a case constructed to BE that defect "
        f"(said: {message!r}). Specificity without sensitivity is not a check."
    )


def test_no_anti_pattern_detector_fires_on_real_looking_writing():
    """Shaped dynamics, varied rhythm, ornaments where the music leans, a rest."""
    from scales import anti_pattern_detector as AP
    from scales.direct_compose import compose_phrase

    bars = [
        {"rh": "(F5dq A5e G5e F5e)", "lh": "F2e C3e A2e C3e F2e C3e", "dyn": "p"},
        {"rh": "(<Bb5q A5e F5e D5q!)", "lh": "D3e Bb3e F3e Bb3e D3e Bb3e"},
        {"rh": "(A5e C6e E6q:turn D6e C6e)", "lh": "A2q Bb2q C3e E3e"},
        {"rh": "[E5,G5,Bb5]dq rest_e [C5,E5,G5]q", "lh": "[C2,C3]dq [C2,G2]dq", "dyn": "mf"},
        {"rh": "(C6q Bb5e A5e G5q)", "lh": "F2e C3e A2e C3e F2e C3e"},
        {"rh": "(F5h:tr E5e D5e)", "lh": "Bb2e F3e D3e F3e Bb2e F3e", "dyn": "mp"},
        {"rh": "(G5e F5e E5e D5e C5q)", "lh": "C3q G3q E3e G3e"},
        {"rh": "F5dh:ferm rest_e", "lh": "[F2,F3]dh rest_e", "dyn": "pp"},
    ]
    layer = compose_phrase(bars, key="F major", meter=(3, 4), bar_start=1)
    fired = []
    for name, fn in AP._DETECTORS.items():
        try:
            result = fn(layer)
        except TypeError:
            continue  # needs a previous phrase
        if result[0]:
            fired.append(f"{name}: {result[2]}")
    assert not fired, "fired on real-looking writing:\n  " + "\n  ".join(fired)


# ── composed_blind: a presence check, with real ground truth ─────────────────


def _real_bar_shorthands(composer="mozart", n=600, seed=11):
    import random

    from scales.composition_brief import _adapted_to_shorthand, _iter_corpus_bars
    from scales.corpus_adapter import AdaptedBar

    rng = random.Random(seed)
    pool = [
        b
        for b in _iter_corpus_bars(composer)
        if (b.get("rh_display") or []) and not b.get("truncated")
    ]
    if not pool:
        return []
    pool = rng.sample(pool, min(n, len(pool)))
    out = []
    for bar in pool:
        adapted = AdaptedBar(
            rh_events=bar.get("rh_display") or [],
            lh_events=[],
            target_key=bar.get("key", "C"),
            target_bar_num=1,
        )
        rh = _adapted_to_shorthand(adapted)[0]
        if rh and len(rh.split()) >= 3:
            out.append(rh)
    return out


def test_composed_blind_does_not_flag_real_music_against_real_exemplars():
    """Real Mozart, judged against other real Mozart, must almost never read blind."""
    import random

    from scales.anti_skip import BLIND_FLOOR, resemblance, signature_from_shorthand

    shorthands = _real_bar_shorthands()
    if len(shorthands) < 60:
        pytest.skip("no corpus available")
    sigs = [signature_from_shorthand(s) for s in shorthands]
    rng = random.Random(11)
    flagged = total = 0
    for i in range(0, min(600, len(sigs)), 6):
        exemplars = [sigs[j] for j in rng.sample(range(len(sigs)), 8)]
        total += 1
        if max(resemblance(sigs[i], e) for e in exemplars) < BLIND_FLOOR:
            flagged += 1
    rate = flagged / total
    assert rate <= 0.10, (
        f"composed_blind flags {rate:.0%} of real Mozart bars against real Mozart "
        f"exemplars. Combining rhythm and interval similarity with `min` instead of "
        f"the mean measures 19% here — a permissive operating point is deliberate."
    )


def test_composed_blind_recognises_a_surface_that_is_the_exemplar():
    """Sensitivity floor: the exemplar itself, and a transposition of it."""
    from scales.anti_skip import BLIND_FLOOR, resemblance, signature_from_shorthand

    exemplar = "A4h C5s Bb4s A4s Bb4s"
    ref = signature_from_shorthand(exemplar)
    for label, surface in (
        ("verbatim", exemplar),
        ("transposed", "D5h F5s Eb5s D5s Eb5s"),
        ("same rhythm, new pitches", "G4h B4s A4s G4s A4s"),
    ):
        score = resemblance(signature_from_shorthand(surface), ref)
        assert score >= BLIND_FLOOR, f"{label} scored {score} against its own exemplar"
