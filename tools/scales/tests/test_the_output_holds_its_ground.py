"""Every dimension this session closed, re-measured on one generated piece.

Written because a dimension that gets fixed stops being measured. Chopin's
melodic direction changes were brought to 3.0 per bar — matching him exactly —
and drifted to 2.0 over several rounds of unrelated work on tuplets. Every one
of those changes WAS verified, against texture agreement, silent tails and
duration vocabulary: the dimensions being watched for that change. Contour was
not among them precisely because it had already been closed.

The piece is one artefact and everything moves everything, so the guard has to
be the whole set of closed findings rather than the ones relevant to today's
edit. Each bound below carries the measurement that motivated it and the real
figure it is judged against.

Marked `calibration` because it generates a piece and parses the corpus: about
two minutes. Run it with:

    pytest -m calibration tools/scales/tests/test_the_output_holds_its_ground.py -s
"""

import contextlib
import io
import shutil
import sys
import warnings
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

pytestmark = pytest.mark.calibration


def _compose(composer: str, key: str = "D minor", meter=(4, 4)):
    """Generate one ternary piece and return its analysed bars, with the plan."""
    import music21
    from scripts.build_full_corpus import analyze_score_bars

    from scales import scales as S

    piece = f"_guard_{composer}_{meter[0]}{meter[1]}"
    shutil.rmtree(S._WORKSPACE / piece, ignore_errors=True)
    try:
        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            S.init_workspace(piece, mode="compose_from_text", description="guard")
            S.compile_style(piece, composers=[composer])
            S.build_form_graph(
                piece, form="ternary", key=key, tempo_bpm=92, meter=meter
            )
            graph = S._load_graph(piece)
            planned = {}
            for phrase in graph.phrases.values():
                slot = phrase.slot
                for offset, plan in enumerate(getattr(slot, "texture_plan", None) or []):
                    planned[slot.bar_start + offset] = plan.rh_texture
            for section in sorted(
                {p.slot.section_id for p in graph.phrases.values() if p.slot}
            ):
                S.run_scales_section(piece, section_id=section)
            context = S.review_context(piece)
            assert context.get("musicxml"), context.get("error")
            score = music21.converter.parse(context["musicxml"])
            bars = analyze_score_bars(score, composer, "guard")
    finally:
        shutil.rmtree(S._WORKSPACE / piece, ignore_errors=True)
    return bars, planned


def _tops(bar, field="rh_display"):
    from scales.pitch import pitch_to_midi

    out = []
    for event in bar.get(field) or []:
        if event.get("type") == "rest":
            continue
        midis = []
        for name in event.get("pitches") or (
            [event.get("pitch")] if event.get("pitch") else []
        ):
            try:
                midis.append(pitch_to_midi(name))
            except Exception:
                pass
        if midis:
            out.append(max(midis))
    return out


@pytest.fixture(scope="module")
def chopin():
    return _compose("chopin")


def test_the_written_bar_is_the_texture_that_was_planned(chopin):
    """Was 73% before the density-and-contour work, 93% after.

    The residual is `chordal -> held_note` at phrase ends, which the corpus
    shows is ordinary — real cadential chordal bars are all-single-note 10% of
    the time.
    """
    bars, planned = chopin
    written = {b.get("bar_num"): b.get("rh_texture") for b in bars}
    pairs = [
        (want, written.get(bar))
        for bar, want in planned.items()
        if want and written.get(bar)
    ]
    agree = sum(1 for want, got in pairs if want == got) / max(len(pairs), 1)
    assert agree >= 0.85, f"{agree:.0%} of bars match the texture planned"


def test_the_melody_does_not_stand_still(chopin):
    """Repeated pitches were 19.9% of adjacent pairs against a real 8.2%.

    None of them was chosen: the arch rounds scale indices and lands twice on
    one degree. A line sitting on one note is among the plainest tells there is.
    """
    bars, _ = chopin
    repeats = moves = 0
    for bar in bars:
        tops = _tops(bar)
        for first, second in zip(tops, tops[1:]):
            moves += 1
            if first == second:
                repeats += 1
    share = repeats / max(moves, 1)
    assert share <= 0.12, f"{share:.1%} of adjacent pairs repeat (real 8.2%)"


def test_the_melody_still_turns(chopin):
    """Direction changes per bar: real Chopin 3.0.

    This is the dimension that drifted. It was brought to 3.0 exactly and fell
    to 2.0 during later work on tuplets, unnoticed because nothing was watching
    it any more. The bound is deliberately loose — what matters is catching a
    line that stops turning at all.
    """
    import statistics

    bars, _ = chopin
    turns = []
    for bar in bars:
        tops = _tops(bar)
        signs = [
            1 if second > first else -1
            for first, second in zip(tops, tops[1:])
            if second != first
        ]
        if signs:
            turns.append(sum(1 for a, b in zip(signs, signs[1:]) if a != b))
    assert turns, "no bar had two melody notes"
    assert statistics.median(turns) >= 1.5, (
        f"median {statistics.median(turns)} direction changes per bar (real 3.0)"
    )


def test_the_score_holds_no_duration_nobody_wrote(chopin):
    """A seventh of written notes were once a triplet-16th absent from the IR.

    music21 completes an incomplete tuplet group by SPLITTING it, so fragments
    reach the page as durations no one composed. Real Mozart writes a
    triplet-16th in 0.3% of his notes; ours reached 14%.
    """
    bars, _ = chopin
    counts = {}
    total = 0
    for bar in bars:
        for field in ("rh_display", "lh_display"):
            for event in bar.get(field) or []:
                if event.get("type") == "rest":
                    continue
                value = round(float(event.get("dur") or 0), 4)
                if value > 0:
                    counts[value] = counts.get(value, 0) + 1
                    total += 1
    assert total, "the piece has no notes"
    # 1/6 and 5/24 are the split artefacts; both were absent from the IR.
    for artefact in (0.1667, 0.2083):
        share = counts.get(artefact, 0) / total
        assert share <= 0.02, f"{share:.1%} of notes are {artefact}, a split artefact"
    assert len(counts) <= 14, (
        f"{len(counts)} distinct note values; no real Mozart movement exceeds 14"
    )


def test_the_accompaniment_reaches_the_barline(chopin):
    """The left hand fell silent before the barline in 79-100% of bars.

    A pattern is stored at the length of the bar it came from, and nothing
    checked that against the bar it was poured into. Real Chopin leaves the tail
    silent in 3-25% depending on idiom, so this is a rate and not a rule.
    """
    silent = counted = 0
    bars, _ = chopin
    for bar in bars:
        events = bar.get("lh_display") or []
        if not events:
            continue
        position = last_sound = 0.0
        for event in events:
            length = float(event.get("dur") or 0)
            if event.get("type") != "rest":
                last_sound = position + length
            position += length
        if position <= 0:
            continue
        counted += 1
        if last_sound < position - 0.01:
            silent += 1
    assert counted, "the piece has no left hand"
    share = silent / counted
    assert share <= 0.35, f"the left hand stops early in {share:.0%} of bars"
