"""The melody's register arc — the fixes behind `register_stasis`.

Three separate defects kept every engine-realized melody inside one octave:
the contour templates only named degrees 1-7, the anchor resolver could not
express a degree above the octave, and the climax position the caller computed
was accepted and discarded.
"""

from scales.models import Anchor
from scales.realizer import Realizer
from scales.sketch_proposer import SketchProposer


def _resolve(degree: str, key: str) -> int:
    realizer = Realizer.__new__(Realizer)
    return realizer._resolve_anchor_pitch(
        Anchor(bar=1, beat=1.0, pitch_or_degree=degree), key, []
    )


def test_a_degree_above_the_octave_resolves_an_octave_up():
    """`intervals.get(degree, 0)` returned the TONIC for anything past 7, so a
    melody asking to rise an octave stayed exactly where it was."""
    tonic = _resolve("^1", "C major")
    assert _resolve("^8", "C major") == tonic + 12
    assert _resolve("^15", "C major") == tonic + 24
    assert _resolve("^10", "C major") == _resolve("^3", "C major") + 12
    assert _resolve("^12", "C major") == _resolve("^5", "C major") + 12


def test_the_octave_degrees_follow_the_mode():
    """A tenth in minor is a minor tenth."""
    assert _resolve("^10", "C minor") == _resolve("^3", "C minor") + 12
    assert _resolve("^3", "C minor") == _resolve("^1", "C minor") + 3
    assert _resolve("^3", "C major") == _resolve("^1", "C major") + 4


def test_the_contour_reaches_past_the_octave():
    """The templates were fixed lists of degrees 1-7, so no melody this
    proposer wrote could span more than a seventh's worth of anchors."""
    proposer = SketchProposer.__new__(SketchProposer)
    degrees = proposer._build_contour(bar_count=8, peak_pos=5, variant_idx=0, cadence="none")
    numbers = [int(d.lstrip("^")) for d in degrees]
    assert max(numbers) > 7, f"contour never leaves the octave: {degrees}"


def test_the_climax_lands_where_the_caller_asked():
    """`peak_pos` was a parameter the function accepted and never read."""
    proposer = SketchProposer.__new__(SketchProposer)
    for peak in (2, 5, 9):
        degrees = proposer._build_contour(
            bar_count=12, peak_pos=peak, variant_idx=0, cadence="none"
        )
        numbers = [int(d.lstrip("^")) for d in degrees]
        assert numbers.index(max(numbers)) == peak, (
            f"asked for a peak at bar {peak}, got it at {numbers.index(max(numbers))}: {degrees}"
        )


def test_the_contour_still_ends_on_the_cadence_soprano():
    proposer = SketchProposer.__new__(SketchProposer)
    plain = proposer._build_contour(bar_count=8, peak_pos=5, variant_idx=0, cadence="none")
    cadenced = proposer._build_contour(bar_count=8, peak_pos=5, variant_idx=0, cadence="PAC")
    assert cadenced[:-1] == plain[:-1]
    assert cadenced[-1].startswith("^")


def test_every_contour_degree_is_writable():
    proposer = SketchProposer.__new__(SketchProposer)
    for variant in range(3):
        for bars in (1, 2, 4, 8, 16):
            for peak in range(bars):
                degrees = proposer._build_contour(
                    bar_count=bars, peak_pos=peak, variant_idx=variant, cadence="none"
                )
                assert len(degrees) == bars
                for d in degrees:
                    n = int(d.lstrip("^"))
                    assert 1 <= n <= 14, f"{d} out of range"
                    assert _resolve(d, "D minor") is not None


def test_a_mid_bar_anchor_between_wide_anchors_is_not_pulled_into_one_octave():
    """`_interpolate_degree` clamped to 7, so a passing note between a `^5` and
    a `^12` came out below both of them."""
    proposer = SketchProposer.__new__(SketchProposer)
    mid = int(proposer._interpolate_degree("^5", "^12", 0).lstrip("^"))
    assert 5 <= mid <= 12, f"mid-bar anchor {mid} fell outside its neighbours"


# ─── the bass reads the same notation ────────────────────────────────────────


def _bass(degree: str, key_root: int = 0, mode: str = "major") -> int:
    from scales.surface_composer import SurfaceComposer

    composer = SurfaceComposer.__new__(SurfaceComposer)
    return composer._resolve_bass_pitch(
        Anchor(bar=1, beat=1.0, pitch_or_degree=degree), None, "C major", mode, key_root
    )


def test_a_chromatic_bass_degree_does_not_crash():
    """`int(p[1:])` raised `invalid literal for int() with base 10: '#2'` on the
    ordinary way to write a raised second, and took the whole section with it."""
    assert _bass("^#2") == _bass("^2") + 1
    assert _bass("^b7") == _bass("^7") - 1
    assert _bass("^b3") == _bass("^3") - 1


def test_a_bass_degree_above_the_octave_goes_up_an_octave():
    """It wrapped with `% len(intervals)`, so `^9` was the second in the SAME
    octave — the same octave-blindness the melody anchors had."""
    assert _bass("^9") == _bass("^2") + 12
    assert _bass("^8") == _bass("^1") + 12


def test_an_unreadable_bass_degree_falls_back_rather_than_raising():
    assert isinstance(_bass("^nonsense"), int)


def test_the_bass_degree_follows_the_mode():
    assert _bass("^3", mode="minor") == _bass("^1", mode="minor") + 3
    assert _bass("^3", mode="major") == _bass("^1", mode="major") + 4
