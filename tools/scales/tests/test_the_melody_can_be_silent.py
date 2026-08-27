"""A bar can lack a fresh downbeat two ways, and only one was covered.

`_hold_over_barline` ties the previous note into the bar. Nothing let the melody
simply be SILENT at the top of a bar — and measured on this engine's own output,
across two complete pieces:

    leading rests in the committed LayerIR:  0 of 83 bars, in every layer

Not a low rate. None. The 8-10% of leading rests visible in the exported left
hand were the assembler PADDING bars where the accompaniment had no downbeat
note — a statistic that looked healthy in the score and did not exist in the
music. Real melodies rest on 5-12% of downbeats:

    schubert 11.6%  beethoven 11.1%  chopin 8.9%  mozart 8.3%
    haydn     7.5%  bach       5.3%
"""

from __future__ import annotations

from scales.models import LayerEvent, LayerIR
from scales.surface_composer import _rest_the_downbeat


def _piece(bars=24, notes=4, with_bass=True):
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=bars, key="C major")
    ir.principal_line = [
        LayerEvent(
            bar=b,
            beat=1.0 + i,
            # An arch, so the downbeat is never the bar's peak.
            pitch=["C5", "E5", "G5", "D5"][i % 4],
            duration="q",
            role="structural",
            source_layer="principal_line",
        )
        for b in range(1, bars + 1)
        for i in range(notes)
    ]
    if with_bass:
        ir.bass_foundation = [
            LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", source_layer="bass_foundation")
            for b in range(1, bars + 1)
        ]
    return ir


def _leading_rests(ir):
    by_bar = {}
    for e in ir.principal_line:
        by_bar.setdefault(e.bar, []).append(e)
    return sum(
        1
        for events in by_bar.values()
        if sorted(events, key=lambda x: float(x.beat))[0].pitch == "rest"
    )


def test_the_melody_now_rests_on_some_downbeats():
    ir = _piece()
    assert _rest_the_downbeat(ir, (4, 4), share=0.12) > 0
    assert _leading_rests(ir) > 0


def test_the_rate_is_the_composers_own_not_a_fixed_one():
    """Bach rests half as often as Beethoven; one number is right for neither."""
    counts = {}
    for share in (0.05, 0.12):
        ir = _piece(bars=48)
        _rest_the_downbeat(ir, (4, 4), share=share)
        counts[share] = _leading_rests(ir)
    assert counts[0.12] > counts[0.05], counts


def test_it_is_inert_at_a_share_of_zero():
    """The sibling passes each shipped without this once."""
    ir = _piece()
    assert _rest_the_downbeat(ir, (4, 4), share=0.0) == 0
    assert _leading_rests(ir) == 0


def test_applying_it_twice_adds_nothing():
    """A revision loop runs these again; a pass that counts its own output drifts."""
    ir = _piece()
    first = _rest_the_downbeat(ir, (4, 4), share=0.12)
    after_first = _leading_rests(ir)
    assert _rest_the_downbeat(ir, (4, 4), share=0.12) == 0, "the pass re-fired on its own output"
    assert _leading_rests(ir) == after_first == first


def test_a_four_bar_phrase_does_not_get_one_rest_per_phrase():
    """Both ways to get the quota wrong, stated as a test.

    `round(len(phrase_bars) * share)` is 0 for a four-bar phrase at any real
    rate (4 x 0.083 rounds to 0) and can never produce the rate at all;
    `max(1, ...)` is its mirror and puts one rest in every phrase whatever the
    composer's rate. The quota is the difference between the running totals at
    the phrase's last and first ABSOLUTE bars, so it sums correctly over the
    piece however the phrases are cut.
    """
    total = 0
    for start in range(1, 41, 4):  # ten consecutive four-bar phrases
        ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=4, key="C major")
        ir.principal_line = [
            LayerEvent(
                bar=b,
                beat=1.0 + i,
                pitch=["C5", "E5", "G5", "D5"][i % 4],
                duration="q",
                role="structural",
                source_layer="principal_line",
            )
            for b in range(start, start + 4)
            for i in range(4)
        ]
        ir.bass_foundation = [
            LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", source_layer="bass_foundation")
            for b in range(start, start + 4)
        ]
        total += _rest_the_downbeat(ir, (4, 4), share=0.083)  # Mozart's own rate
    # 40 bars at 8.3% is between three and four rests. One per phrase is ten —
    # the `max(1, ...)` failure. Zero is the `round(4 * 0.083)` failure. A first
    # version of this test used share=0.25, where ten rests over forty bars is
    # simply the CORRECT rate, so it could not tell the two apart.
    assert total != 10, "one rest per phrase regardless of rate — the max(1, ...) failure"
    assert total > 0, "no rest at any phrase — the per-phrase round-to-zero failure"
    assert 2 <= total <= 5, f"{total} rests across 40 bars at 8.3% (expected 3-4)"


def test_the_theme_is_never_silenced():
    """The one thing in the piece that must be heard."""
    ir = _piece(bars=24)
    protected = frozenset(range(1, 25))
    assert _rest_the_downbeat(ir, (4, 4), share=0.5, protect_bars=protected) == 0


def test_a_bar_whose_accompaniment_is_also_silent_is_left_alone():
    """The harmony has to be stated by something. If the melody rests and the
    bass is not there either, the bar says nothing at all."""
    ir = _piece(with_bass=False)
    assert _rest_the_downbeat(ir, (4, 4), share=0.5) == 0


def test_the_phrases_climax_is_never_the_note_removed():
    """Silencing the note the whole phrase is shaped toward removes the phrase.

    The first version of this rule protected each BAR's highest note, which
    sounds careful and excludes every descending bar — a melody that falls from
    its downbeat has its peak there by construction. It became the single
    largest decline reason in the sweep. A bar-local high point is ordinary; the
    phrase's climax is not.
    """
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=24, key="C major")
    ir.principal_line = [
        LayerEvent(
            bar=b,
            beat=1.0 + i,
            # Bar 1 beat 1 is the highest note in the whole phrase.
            pitch=("C7" if (b, i) == (1, 0) else ["C5", "E5", "G5", "D5"][i % 4]),
            duration="q",
            role="structural",
            source_layer="principal_line",
        )
        for b in range(1, 25)
        for i in range(4)
    ]
    ir.bass_foundation = [
        LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", source_layer="bass_foundation")
        for b in range(1, 25)
    ]
    report = {}
    _rest_the_downbeat(ir, (4, 4), share=0.9, report=report)
    first = sorted([e for e in ir.principal_line if e.bar == 1], key=lambda x: float(x.beat))
    assert first[0].pitch == "C7", "the phrase's climax was silenced"
    assert report["declined"]["the downbeat is the phrase's climax"] == 1


def test_a_bar_that_merely_falls_from_its_downbeat_is_still_eligible():
    """The converse, asserted because a rule with only one side stated is the
    one that gets half-reverted later. Every bar here descends, so under the old
    rule every downbeat was a local peak and nothing was ever eligible."""
    ir = LayerIR(phrase_id="p", meter=(4, 4), bar_count=24, key="C major")
    # Every bar FALLS from its downbeat — so under the old rule every downbeat
    # was a local peak. Only bar 12 reaches the phrase's actual high point, so
    # the climax rule excludes one bar and not twenty-four. (A first version of
    # this fixture started every bar on the same G5, which made every downbeat
    # the phrase peak too, and it failed for the fixture's reason rather than
    # the code's.)
    tops = ["G5", "A5", "F5", "E5", "G5", "A5", "F5", "E5", "G5", "A5", "F5", "C6"]
    ir.principal_line = [
        LayerEvent(
            bar=b,
            beat=1.0 + i,
            pitch=[tops[(b - 1) % len(tops)], "D5", "C5", "B4"][i % 4],
            duration="q",
            role="structural",
            source_layer="principal_line",
        )
        for b in range(1, 25)
        for i in range(4)
    ]
    ir.bass_foundation = [
        LayerEvent(bar=b, beat=1.0, pitch="C3", duration="w", source_layer="bass_foundation")
        for b in range(1, 25)
    ]
    assert _rest_the_downbeat(ir, (4, 4), share=0.12) > 0, (
        "every bar descends, so under a bar-local peak rule nothing is ever eligible"
    )


def test_the_rest_is_written_explicitly_and_fills_the_gap_it_opens():
    """An implicit gap is something the assembler fills and nobody chose."""
    from scales.duration import dur_to_beats

    ir = _piece()
    _rest_the_downbeat(ir, (4, 4), share=0.5)
    by_bar = {}
    for e in ir.principal_line:
        by_bar.setdefault(e.bar, []).append(e)
    silenced = [
        sorted(v, key=lambda x: float(x.beat))
        for v in by_bar.values()
        if sorted(v, key=lambda x: float(x.beat))[0].pitch == "rest"
    ]
    assert silenced, "nothing was silenced"
    for events in silenced:
        rest, nxt = events[0], events[1]
        assert float(rest.beat) == 1.0
        assert abs(float(rest.beat) + dur_to_beats(rest.duration) - float(nxt.beat)) < 1e-6


def test_the_pass_says_why_it_declined_not_only_how_often_it_acted():
    """A pass that does nothing and a pass that correctly declines both return 0.

    So does one whose quota rounded to nothing, one that found no eligible bar,
    and one switched off by a zero rate — four states, one integer, and "0"
    reads as "correctly decided there was nothing to do" in every log there is.
    That is the generator-side form of a check reporting nothing because it
    cannot report anything, and it is what hid this pass being inert on every
    planned piece: the theme guard was eating whole phrases and the only signal
    was a 0 that looked deliberate.
    """
    report = {}
    ir = _piece(with_bass=False)
    assert _rest_the_downbeat(ir, (4, 4), share=0.5, report=report) == 0
    assert report["pass"] == "downbeat_rests"
    assert report["reason"] == "no bar could take a rest"
    assert report["considered"] == 24
    assert report["eligible"] == 0
    assert report["declined"]["no accompaniment on the downbeat"] > 0

    report = {}
    assert _rest_the_downbeat(_piece(), (4, 4), share=0.0, report=report) == 0
    assert report["reason"] == "share is zero", report

    report = {}
    ir = _piece()
    assert _rest_the_downbeat(ir, (4, 4), share=0.12, report=report) > 0
    assert report["applied"] == report["allowance"] > 0
    assert not report.get("reason"), report


def test_a_phrase_may_begin_with_a_rest():
    """The exclusion that looked obviously right and was backwards.

    "The entry has to land" cost more than any other condition — on a 2/4
    ternary it declined 18 of 41 bars, because a four-bar phrase spends half its
    bars on an entry or a cadence. Measured by phrase position, an OPENING bar
    is where real melodies rest MOST: Mozart 14.6% against 8.3% in the middle,
    Schubert 14.3%, Beethoven 12.2%. A phrase that begins with a rest is an
    upbeat entry.
    """
    ir = _piece(bars=8)
    _rest_the_downbeat(ir, (4, 4), share=0.9)
    first = sorted([e for e in ir.principal_line if e.bar == 1], key=lambda x: float(x.beat))
    assert first[0].pitch == "rest", "the phrase's opening bar is still excluded"


def test_the_cadence_bar_keeps_its_downbeat():
    """It is the arrival, and the position where the classical composers rest
    least — Mozart 4.7%, Bach 3.4%."""
    ir = _piece(bars=8)
    _rest_the_downbeat(ir, (4, 4), share=0.9)
    last = sorted([e for e in ir.principal_line if e.bar == 8], key=lambda x: float(x.beat))
    assert last[0].pitch != "rest"


def test_every_early_exit_publishes_its_reason():
    """`stop()` writes the report itself so the two cannot happen out of order.

    A first version left the write to the caller and every early return
    published a report with `reason` missing — which is exactly the field the
    early returns exist to carry. A report that omits the reason on the paths
    that have one is the same defect as no report at all, arriving quietly.
    """
    from scales.surface_composer import PassReport

    report = {}
    made = PassReport("probe")
    assert made.stop(report, "nothing to do") == 0
    assert report["reason"] == "nothing to do"
    assert report["pass"] == "probe"
    assert report["ran"] is True
    assert made.idle


def test_a_pass_that_acted_carries_no_reason():
    """`reason` present means the pass gave up; absent means it worked."""
    report = {}
    ir = _piece()
    assert _rest_the_downbeat(ir, (4, 4), share=0.12, report=report) > 0
    assert "reason" not in report, report
    assert report["applied"] > 0


def test_a_zero_is_never_bare():
    """The invariant the report exists to hold: `applied == 0` implies a reason
    or a declined candidate.

    A peer session found `applied: 0` with an empty `declined` and no `reason` —
    the one shape this class was built to make impossible. The cause was a
    `continue` in the apply loop that recorded nothing when a gap turned out not
    to be a notatable rest. Rather than trust that every future path remembers,
    the report SAYS SO when it happens: a reader who sees that sentence knows to
    look at the pass rather than at the music.
    """
    from scales.surface_composer import PassReport

    bare = PassReport("probe")
    bare.applied = 0
    assert "unaccounted path" in bare.as_dict()["reason"]

    acted = PassReport("probe")
    acted.applied = 3
    assert "reason" not in acted.as_dict()

    declined = PassReport("probe")
    declined.decline("nothing eligible")
    assert "reason" not in declined.as_dict()
    assert declined.as_dict()["declined"] == {"nothing eligible": 1}


def test_every_zero_this_pass_can_return_is_explained():
    """Walked across the conditions rather than asserted once."""
    cases = [
        ("share zero", dict(share=0.0), _piece()),
        ("no accompaniment", dict(share=0.5), _piece(with_bass=False)),
        ("all protected", dict(share=0.5, protect_bars=frozenset(range(1, 25))), _piece()),
        ("too short", dict(share=0.5), _piece(bars=1, notes=2)),
    ]
    for label, kwargs, ir in cases:
        report = {}
        applied = _rest_the_downbeat(ir, (4, 4), report=report, **kwargs)
        assert applied == 0, label
        assert report.get("reason") or report.get("declined"), f"{label}: bare zero -> {report}"
        assert "unaccounted path" not in report.get("reason", ""), f"{label}: {report}"


def test_a_short_phrase_is_not_refused_for_being_short():
    """The floor was eight notes, set when the pass was new.

    The rate comes from the composer's corpus and the quota from absolute bar
    numbers, so neither depends on how much material is in front of this call.
    All an eight-note floor did was refuse every short phrase — the identical
    floor, set the same way, was making the tie pass idle on three composers.
    """
    ir = _piece(bars=3, notes=2)
    report = {}
    _rest_the_downbeat(ir, (4, 4), share=0.5, report=report)
    assert "too short" not in report.get("reason", ""), report
