"""The rhythmic fingerprint — the facts a composer can hold in mind while writing.

A B-flat andante passed the commit gate, the musical ear and the realism audit
while resting in 22% of its bars against Mozart's 62%, carrying a dotted rhythm
in 4.9% against his 21%, and holding nothing faster than a sixteenth against his
12%. Every one of those numbers was derivable from the corpus the whole time.
The brief carried them only as per-note ratios — the same truth in a unit nobody
reasons in — so they were never read.
"""

import pytest

from scales.composition_brief import (
    render_rhythmic_fingerprint,
    rhythmic_fingerprint,
)

_ARMED = ["mozart", "bach", "beethoven", "chopin"]


def _fp(c):
    fp = rhythmic_fingerprint(c)
    if not fp.get("bars"):
        pytest.skip(f"{c} corpus not present")
    return fp


@pytest.mark.parametrize("composer", _ARMED)
def test_every_armed_composer_has_a_measurable_fingerprint(composer):
    fp = _fp(composer)
    for k in ("rest_bar_pct", "dotted_bar_pct", "fast_note_pct", "lh_texture_change_pct"):
        assert 0.0 <= fp[k] <= 1.0, f"{composer}.{k} = {fp[k]}"
    assert fp["top_note_values"]


def test_the_fingerprint_separates_composers():
    """If every composer's fingerprint were the same it would carry no
    information and be worse than nothing — it would read as authority."""
    seen = {c: _fp(c)["rest_bar_pct"] for c in _ARMED}
    assert len(set(round(v, 2) for v in seen.values())) > 1, seen


def test_mozart_rests_far_more_than_the_machine_default():
    """The specific fact the andante missed."""
    assert _fp("mozart")["rest_bar_pct"] > 0.5


def test_a_thin_corpus_is_not_presented_as_a_fact_about_the_composer():
    """Liszt's corpus is 437 bars from the four lyrical works that are public
    domain and contains nothing faster than a sixteenth. Rendering that as "0%
    of HIS melody notes are a 32nd or faster" states a falsehood about Liszt and
    would push a composer away from the filigree that is his signature."""
    fp = rhythmic_fingerprint("liszt")
    if not fp.get("bars"):
        pytest.skip("liszt corpus not present")
    text = " ".join(render_rhythmic_fingerprint("liszt"))
    assert "THIS IS THE SAMPLE, NOT THE COMPOSER" in text
    assert "FACTS ABOUT HIM" not in text


def test_a_narrow_corpus_never_gets_the_unqualified_wording():
    """The heading must track `corpus_scope().narrow`, not a hardcoded list of
    composers — a first version asserted Mozart earned the plain "FACTS ABOUT
    HIM" wording, and broadening two corpora then falsified it for others."""
    from scales.composition_brief import available_corpus_composers, corpus_scope

    for c in available_corpus_composers():
        if not corpus_scope(c).get("narrow"):
            continue
        text = " ".join(render_rhythmic_fingerprint(c))
        assert "THIS IS THE SAMPLE, NOT THE COMPOSER" in text, c
        assert "FACTS ABOUT HIM" not in text, c


def test_the_fingerprint_reaches_the_brief():
    """Two complete, well-tested modules once sat in this repo that nothing
    imported. A fingerprint the brief does not carry is decoration."""
    import inspect

    from scales import composition_brief as cb

    src = inspect.getsource(cb)
    assert "render_rhythmic_fingerprint(brief.composer)" in src


# ─── The evaluation side: z-scores restated as sentences ────────────────────


def test_a_gap_reads_correctly_on_BOTH_sides():
    """The first version of this carried one sentence per metric, written for
    the below-case, and reported a piece resting in 79% of its bars as "the
    music never stops sounding"."""
    from scales.scales import _rhythmic_gap

    def gap(value, mean, sd):
        return _rhythmic_gap(
            {"metrics": {"rest_bar_ratio": {"value": value, "corpus_mean": mean, "corpus_sd": sd,
                                            "z": (value - mean) / sd}}},
            "beethoven",
        )["gaps"]

    too_few = gap(0.10, 0.48, 0.17)[0]["note"]
    too_many = gap(0.79, 0.48, 0.17)[0]["note"]
    assert "far below" in too_few and "never stops sounding" in too_few
    assert "far above" in too_many and "never stops sounding" not in too_many
    assert "broken up" in too_many


def test_only_real_distances_are_reported():
    """A piece sitting inside the composer's distribution should be told
    nothing — a report that always fires is noise."""
    from scales.scales import _rhythmic_gap

    inside = _rhythmic_gap(
        {"metrics": {"rest_bar_ratio": {"value": 0.50, "corpus_mean": 0.48,
                                        "corpus_sd": 0.17, "z": 0.12}}},
        "beethoven",
    )
    assert inside["gaps"] == []


def test_the_gap_report_names_a_distance_not_a_target():
    """Corpus comparison is diagnostic in this project; metric-chasing was
    tried and rejected. The wording must not read as an instruction."""
    from scales.scales import _rhythmic_gap

    note = _rhythmic_gap(
        {"metrics": {"rest_bar_ratio": {"value": 0.10, "corpus_mean": 0.48,
                                        "corpus_sd": 0.17, "z": -2.2}}},
        "mozart",
    )["gaps"][0]["note"]
    for word in ("must", "should", "target", "increase to", "aim for"):
        assert word not in note.lower(), f"'{word}' reads as a quota: {note}"
