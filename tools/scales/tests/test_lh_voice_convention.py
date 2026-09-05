"""A plain single-stream left hand is ONE voice.

`direct_compose` settled this and recorded why: filing note[0] as
`bass_foundation` and everything after it as `response_layer` gives every piece a
bass of exactly one short note per bar — a bass that plays once and stops —
while the actual moving bass sits in a second voice that does not exist.

`surface_composer` invented a second convention (`voice = "bass" if beat <= 1.01
else "accomp"`) in three separate builders, so the ENGINE path had the artifact
`direct_compose` had already removed. The craft checklist duly reported "the
bass does not sound in most bars" about real corpus patterns — 7 of 14 bass bars
sounding for under half a beat.

The sound is unaffected either way; every note is present. What changes is every
per-layer reading: the voice-leading check reads `bass_foundation` as the lower
voice, and so do the craft checklist and the density statistics.
"""

from scales.surface_composer import _lh_voice_for


class _E:
    def __init__(self, duration, beat=1.0):
        self.duration = duration
        self.beat = beat


def test_a_single_stream_left_hand_is_all_bass():
    evs = [_E("e", 1.0), _E("e", 1.5), _E("e", 2.0), _E("e", 2.5)]
    assert [_lh_voice_for(evs, i, (4, 4)) for i in range(4)] == ["bass"] * 4


def test_a_real_pedal_under_figuration_keeps_the_split():
    """A first event lasting the whole bar IS a second voice."""
    evs = [_E("w", 1.0), _E("e", 1.5), _E("e", 2.0), _E("e", 2.5)]
    got = [_lh_voice_for(evs, i, (4, 4)) for i in range(4)]
    assert got == ["bass", "accomp", "accomp", "accomp"], got


def test_the_pedal_test_respects_the_meter():
    """A dotted half fills a 3/4 bar but not a 4/4 one."""
    evs = [_E("h.", 1.0), _E("e", 2.0)]
    assert _lh_voice_for(evs, 1, (3, 4)) == "accomp"
    assert _lh_voice_for(evs, 1, (4, 4)) == "bass"


def test_an_empty_hand_is_harmless():
    assert _lh_voice_for([], 0, (4, 4)) == "bass"


def test_a_malformed_meter_does_not_raise():
    evs = [_E("e", 1.0), _E("e", 1.5)]
    for meter in (None, (0, 0), "nonsense"):
        assert _lh_voice_for(evs, 1, meter) in ("bass", "accomp")


def test_both_engine_builders_use_the_shared_rule():
    """Three builders had their own copy of the split; a convention that lives
    in three places is three conventions."""
    import inspect

    from scales import surface_composer as SC

    src = inspect.getsource(SC)
    assert 'voice="bass" if evt.beat <= 1.01 else "accomp"' not in src
    assert src.count("_lh_voice_for(") >= 3  # helper + two call sites
