"""The brief must not overstate the evidence behind it.

Composing "as Corelli" from **19 bars** is a different act from composing as
Mozart from 7,022, and the brief said so only obliquely — through scattered
"no corpus stats for texture X" warnings the agent had to add up for itself.
`composer_coverage_tier` had always known the answer; nothing put it in front
of the composer.

The same principle covers the texture-transition matrices: six of the nine
by-genre matrices have no armed member and are still **synthetic** — the
Classical matrix with hand-picked multipliers — so composing "in an
impressionist style" against them means composing against Mozart's texture
habits with a fudge factor applied. Passing that off as corpus evidence is how
a piece ends up in the wrong idiom with numbers that look supportive.
"""

from __future__ import annotations

import pytest

from scales.composition_brief import _coverage_note, composer_coverage_tier


def test_a_thin_corpus_is_declared_in_the_brief():
    note = _coverage_note("corelli")
    if not note.get("tier"):
        pytest.skip("corelli not present")
    assert note["tier"] in ("C", "D")
    assert "THIN" in note["advice"].upper() or "UNARMED" in note["advice"].upper()
    assert note["bars"] < 400


def test_a_rich_corpus_says_so_too():
    note = _coverage_note("mozart")
    if not note.get("tier"):
        pytest.skip("mozart not present")
    assert note["tier"] == "A"
    assert note["bars"] > 1500
    assert "THIN" not in note["advice"].upper()


def test_coverage_is_rendered_where_the_composer_will_read_it(function_source):
    """Near the top, not buried in the warnings block at the bottom."""

    from scales import composition_brief

    src = function_source(composition_brief, "render_text")
    assert "CORPUS COVERAGE" in src
    header = src.index("COMPOSITION BRIEF")
    coverage = src.index("CORPUS COVERAGE")
    exemplars = src.find("EXEMPLARS")
    assert coverage > header
    if exemplars != -1:
        assert coverage < exemplars, "coverage must be stated before the exemplars it qualifies"


def test_an_unknown_composer_does_not_crash_the_coverage_note():
    note = _coverage_note("someone-nobody-has-armed")
    assert isinstance(note, dict)
    assert note.get("tier") in (None, "D")


def test_the_tier_thresholds_match_what_the_docstring_claims():
    """Tier A ≥1500 bars, B ≥400, C = some bars, D = none."""
    doc = composer_coverage_tier.__doc__ or ""
    assert "1500" in doc and "400" in doc
    for composer, expect in (("mozart", "A"), ("corelli", "C")):
        rep = composer_coverage_tier(composer)
        if not rep.get("bars"):
            continue
        assert rep["tier"] == expect, f"{composer} reported tier {rep['tier']}"


def test_synthetic_transition_data_is_declared_in_the_brief(function_source):

    from scales import composition_brief

    src = function_source(composition_brief, "_transition_patterns")
    assert "synthetic" in src.lower()
    assert "provenance" in src
    rendered = function_source(composition_brief, "render_text")
    assert "provenance" in rendered, "the synthetic-data warning is computed but never printed"


# ─── Cadence doctrine must reach every armed composer ────────────────────────


def test_a_cadence_script_is_found_whatever_the_source_calls_it():
    """The lookup was a plain substring test on the label.

    A composer profile writes "HC (->V)"; the shared genre harmony files write
    "Half cadence"; the Renaissance file writes "Clausula vera". `"HC" in
    "HALF CADENCE"` is False, so five of the twelve armed composers got **no
    cadence script at all** — in the one place that addresses the single most
    reliable tell that a machine wrote the piece.
    """
    from scales.composition_brief import _cadence_matches

    assert _cadence_matches("HC", "HC (->V)")
    assert _cadence_matches("HC", "Half cadence")
    assert _cadence_matches("PAC", "Authentic (PAC)")
    assert _cadence_matches("PAC", "Authentic (perfect)")
    assert _cadence_matches("PAC", "Clausula vera")
    assert _cadence_matches("DC", "Deceptive")
    assert _cadence_matches("plagal", "Plagal")
    # and it must still discriminate
    assert not _cadence_matches("PAC", "Half cadence")
    assert not _cadence_matches("HC", "Plagal")
    assert not _cadence_matches("", "Half cadence")
    assert not _cadence_matches("HC", "")


def test_every_armed_composer_has_cadence_doctrine_for_the_common_cadences():
    """Five composers compiled to an empty `cadence_scripts.json` because the
    compiler never read the genre harmony file their profile delegates to."""
    import os
    from pathlib import Path

    from scales.composition_brief import _doctrine_slices
    from scales.models import PhraseSlot

    idx = Path("tools") / "reference_index"
    if not idx.is_dir():
        pytest.skip("corpus not present")
    armed = sorted(d for d in os.listdir(idx) if (idx / d).is_dir())

    missing = []
    for composer in armed:
        for cad in ("HC", "PAC"):
            slot = PhraseSlot(
                phrase_id="p",
                section_id="s",
                bar_start=1,
                bar_count=4,
                key="C major",
                meter=(4, 4),
                cadence_target=cad,
            )
            if not _doctrine_slices(composer, slot, "opening").get("cadence_script"):
                missing.append(f"{composer}/{cad}")
    assert not missing, (
        f"armed composer(s) with no cadence doctrine for a common cadence: {missing}"
    )


def test_every_armed_composer_has_real_fingerprints():
    """ "COMPOSER FINGERPRINTS — the defining traits of this composer's voice"
    is the brief section the phrase-composer is told to make the phrase
    *exhibit*. Four armed composers — Corelli, Monteverdi, Palestrina and Weber
    — had no written profile at all, so the brief printed "no composer
    fingerprints for 'corelli'" and the phrase had nothing to be recognisably
    anyone's.
    """
    import json
    import os
    from pathlib import Path

    idx = Path("tools") / "reference_index"
    packs = Path("tools") / "compiled_packs"
    if not idx.is_dir() or not packs.is_dir():
        pytest.skip("corpus not present")

    thin = []
    for composer in sorted(d for d in os.listdir(idx) if (idx / d).is_dir()):
        path = packs / composer / "fingerprint_rules.json"
        if not path.exists():
            thin.append(f"{composer}: no fingerprint_rules.json")
            continue
        data = json.loads(path.read_text())
        items = data.get("items") if isinstance(data, dict) else data
        if len(items or []) < 3:
            thin.append(f"{composer}: {len(items or [])} fingerprints")
    assert not thin, (
        "armed composer(s) without enough fingerprints to make a phrase "
        f"recognisably theirs: {thin}"
    )


def test_melody_doctrine_is_composer_specific():
    """`melody_priors.json` came out **byte-identical for every composer**.

    `_pass_melody_priors` read only the general `melodic-construction.md` and
    `melody-craft.md`; the `melodic-style.md` describing each composer's actual
    melodic voice sat unread in **44 profile directories**. Melody is the most
    audible thing in the output, and the brief's melody doctrine said the same
    thing whether it was building a Bach fugue subject or a Chopin nocturne.
    """
    import json
    import os
    from pathlib import Path

    idx = Path("tools") / "reference_index"
    packs = Path("tools") / "compiled_packs"
    if not idx.is_dir() or not packs.is_dir():
        pytest.skip("corpus not present")

    armed = sorted(d for d in os.listdir(idx) if (idx / d).is_dir())
    generic = []
    for composer in armed:
        path = packs / composer / "melody_priors.json"
        if not path.exists():
            generic.append(f"{composer}: no melody_priors.json")
            continue
        priors = json.loads(path.read_text())
        own = [p for p in priors if p.get("category") == "composer_melodic_voice"]
        if len(own) < 3:
            generic.append(f"{composer}: {len(own)} composer-specific priors")
    assert not generic, f"armed composer(s) whose melody doctrine is generic boilerplate: {generic}"


def test_two_composers_do_not_get_identical_melody_doctrine():
    """The direct symptom: Bach and Chopin used to receive the same file."""
    import json
    from pathlib import Path

    packs = Path("tools") / "compiled_packs"
    a = packs / "bach" / "melody_priors.json"
    b = packs / "chopin" / "melody_priors.json"
    if not (a.exists() and b.exists()):
        pytest.skip("packs not present")
    assert json.loads(a.read_text()) != json.loads(b.read_text())


def test_the_composers_own_voice_leads_the_melody_slice():
    """Generic contour advice must not crowd out the composer's own voice."""
    from scales.composition_brief import _doctrine_slices
    from scales.models import PhraseSlot

    slot = PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=1,
        bar_count=4,
        key="F major",
        meter=(4, 4),
        cadence_target="HC",
    )
    priors = _doctrine_slices("bach", slot, "opening").get("melody_priors") or []
    if not priors:
        pytest.skip("bach pack not present")
    assert len(priors) > 2, "the slice still carries only the two generic priors"
    assert "Fortspinnung" in priors[0], f"composer voice does not lead: {priors[0]!r}"


def test_ornament_doctrine_is_composer_specific_where_the_profile_provides_it():
    """`ornament_intents.json` was identical for all twelve armed composers.

    Ornament choice is one of the most composer-specific things in the idiom —
    Mozart's appoggiatura sigh, Bach's structural mordent, Chopin's chromatic
    cascade that continues the line rather than decorating it — and every brief
    recommended the same ornament in the same place, while the table saying what
    each composer actually does sat uncompiled in their profile.
    """
    from scales.composition_brief import _doctrine_slices
    from scales.models import PhraseSlot

    slot = PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=1,
        bar_count=4,
        key="F major",
        meter=(4, 4),
        cadence_target="PAC",
    )
    seen = {}
    for composer in ("mozart", "bach", "chopin"):
        got = _doctrine_slices(composer, slot, "closing").get("ornament_intent") or []
        if not got:
            pytest.skip(f"{composer} pack not present")
        seen[composer] = got[0]
    assert len(set(seen.values())) == len(seen), (
        f"composers share an identical leading ornament intent: {seen}"
    )
    assert "ppoggiatura" in seen["mozart"], seen["mozart"]
    assert "rill" in seen["bach"] or "ordent" in seen["bach"], seen["bach"]


def test_the_composers_own_lh_catalogue_reaches_the_brief():
    """`mozart-lh-vocabulary.md` was opened by nothing.

    It was written against the failure it names in its own first sentence — "a
    static bass note held under perpetual figuration, the same idiom every bar"
    — catalogues ten alternatives in this system's own shorthand, and never
    compiled. The brief's LH VOCABULARY comes from the corpus pattern library
    instead, which supplies real figures but not the *when*.
    """
    from scales.composition_brief import _doctrine_slices
    from scales.models import BarTexturePlan, PhraseSlot

    slot = PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=1,
        bar_count=4,
        key="D minor",
        meter=(4, 4),
        cadence_target="HC",
    )
    slot.texture_plan = [BarTexturePlan(lh_texture="alberti")]
    figs = _doctrine_slices("mozart", slot, "opening").get("figuration") or []
    if not figs:
        pytest.skip("mozart pack not present")
    assert any(f.startswith("LH idiom") for f in figs), (
        f"the composer's own LH catalogue is not reaching the brief: {figs}"
    )
    # and it must carry the shorthand, which is what makes it usable
    assert any("`" in f for f in figs if f.startswith("LH idiom"))


def test_a_composer_without_an_lh_catalogue_still_gets_generic_figuration():
    """The new source is additive; nothing regresses for the other eleven."""
    from scales.composition_brief import _doctrine_slices
    from scales.models import BarTexturePlan, PhraseSlot

    slot = PhraseSlot(
        phrase_id="p",
        section_id="s",
        bar_start=1,
        bar_count=4,
        key="D minor",
        meter=(4, 4),
        cadence_target="HC",
    )
    slot.texture_plan = [BarTexturePlan(lh_texture="alberti")]
    figs = _doctrine_slices("bach", slot, "opening").get("figuration") or []
    if not figs:
        pytest.skip("bach pack not present")
    assert figs, "generic figuration doctrine disappeared"


# ── Inferred textures must be corpus-real, and the composer's own ────────────


def test_inferred_textures_are_labels_the_corpus_actually_produces():
    """`passage_work` came from an older label vocabulary the corpus no longer
    produces, so every lookup keyed by it missed: exemplar retrieval, density
    targets, ornament stats. The same dead label is documented on the cache
    side in `_density_cache_is_current`.
    """
    from scales.composition_brief import _iter_corpus_bars, _texture_modes

    real_rh, real_lh = set(), set()
    for bar in _iter_corpus_bars("mozart"):
        if bar.get("rh_texture"):
            real_rh.add(bar["rh_texture"])
        if bar.get("lh_texture"):
            real_lh.add(bar["lh_texture"])
    assert "passage_work" not in real_rh, "corpus vocabulary changed; update the inference"
    for rh, lh in _texture_modes("mozart"):
        assert rh in real_rh, f"{rh} is not a texture the corpus produces"
        assert lh in real_lh, f"{lh} is not a texture the corpus produces"


def test_inference_gives_each_composer_their_own_idiom():
    """`alberti` for every composer above the low density band was Mozart's
    habit written into a function every composer goes through. It is not the
    modal LH texture at any density band across the armed corpus.
    """
    from scales.composition_brief import _texture_modes

    dense_lh = {c: _texture_modes(c)[2][1] for c in ("mozart", "chopin", "bach", "monteverdi")}
    assert dense_lh["mozart"] == "alberti"  # his really is
    assert len(set(dense_lh.values())) >= 3, dense_lh


def test_an_unknown_composer_infers_from_the_whole_corpus():
    """No corpus to measure must not mean no textures — and must not mean
    Mozart's."""
    from scales.composition_brief import _texture_modes

    modes = _texture_modes("no-such-composer")
    assert len(modes) == 3
    assert all(rh and lh for rh, lh in modes)


# ── Metre relaxation: a corpus in 4/2 can still teach a 4/4 phrase ───────────


def test_palestrina_can_produce_a_brief_at_all():
    """He has 60,677 bars, tier A, and 58,038 of them are in 4/2 — not one in
    4/4. The retriever filtered metre exactly at every level of its texture
    relaxation, so a 4/4 request matched nothing and the brief came back EMPTY:
    the largest corpus in the project, unusable, failing commits with
    `brief_insufficient`.
    """
    from scales.composition_brief import _retrieve_exemplars, _shorthand_beats
    from scales.models import PhraseSlot

    slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(4, 4))
    warnings: list = []
    exemplars = _retrieve_exemplars("palestrina", slot, 6, warnings)
    assert exemplars, "palestrina still yields no exemplars for a 4/4 phrase"
    # Renotated, not merely relabelled: every voice must fill the target bar.
    for exemplar in exemplars:
        for shorthand in (exemplar.rh, exemplar.lh):
            for voice in shorthand.split("//"):
                beats = _shorthand_beats(voice.strip())
                if beats is not None:
                    assert abs(beats - 4.0) < 0.01, f"{exemplar.source}: {beats} beats"
    # And it says so — borrowing across notation levels is not silent.
    assert any("renotated" in w for w in warnings), warnings


def test_metre_equivalence_borrows_only_a_real_equivalent():
    """A 4/2 bar is a 4/4 bar at another notation level. A 2/4 bar is not, and
    neither is 6/8 — pretending otherwise teaches the wrong rhythm."""
    from scales.composition_brief import _equivalent_meters

    available = [(4, 2), (2, 2), (3, 4), (2, 4), (6, 8), (3, 2)]
    equivalent = _equivalent_meters((4, 4), available)
    assert (4, 2) in equivalent  # same count, another level
    assert (2, 2) in equivalent  # same total length (alla breve)
    for wrong in ((3, 4), (2, 4), (6, 8), (3, 2)):
        assert wrong not in equivalent, wrong
    # The closest notation level comes first.
    assert equivalent[0] == (4, 2)
    # Nothing to borrow is an empty list, not a wrong answer.
    assert _equivalent_meters((4, 4), [(4, 4)]) == []
    # A malformed metre defaults to 4/4, matching `duration.bar_duration`, so
    # the two cannot disagree about what (0, 0) means.
    assert _equivalent_meters((0, 0), available) == _equivalent_meters((4, 4), available)


def test_rescaling_maps_bar_length_not_denominator():
    """4/2 is eight quarters against 4/4's four, so it halves; 2/2 is already
    four and must not be touched.

    The denominator form got the first right and quietly halved the second to a
    two-beat bar, which the overflow guard dropped — so Mussorgsky and Bruckner
    (whose corpora are entirely 2/2) still came back empty while the warning
    claimed their bars had been renotated.
    """
    from scales.composition_brief import _retrieve_exemplars, _shorthand_beats
    from scales.models import PhraseSlot

    for composer in ("mussorgsky", "bruckner"):
        slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(4, 4))
        exemplars = _retrieve_exemplars(composer, slot, 4, [])
        assert exemplars, f"{composer} yields nothing for 4/4"
        for exemplar in exemplars:
            for voice in exemplar.rh.split("//"):
                beats = _shorthand_beats(voice.strip())
                if beats is not None:
                    assert abs(beats - 4.0) < 0.01, f"{composer} {exemplar.source}: {beats}"


def test_simple_and_compound_metres_never_borrow_from_each_other():
    """3/4 and 6/8 are both three quarters long, so a length test alone calls
    them equivalent.

    They are not: 6/8 is two dotted beats subdividing in threes, 3/4 is three
    plain ones, and renotating either as the other by a duration factor teaches
    exactly the wrong rhythm. This is the same objection that keeps 2/4 away
    from 4/4 — it just survives the arithmetic, which is what made it easy to
    miss when writing the length rule.
    """
    from scales.composition_brief import _equivalent_meters

    available = [(4, 4), (3, 4), (6, 8), (2, 4), (4, 2), (2, 2), (9, 8), (12, 8), (3, 8), (6, 4)]

    assert (6, 8) not in _equivalent_meters((3, 4), available)
    assert (3, 4) not in _equivalent_meters((6, 8), available)
    assert (6, 4) not in _equivalent_meters((12, 8), available)  # compound vs simple

    # Within a class, another notation level is still fine.
    assert (3, 8) in _equivalent_meters((3, 4), available)
    assert (4, 2) in _equivalent_meters((4, 4), available)


def test_a_composer_with_no_compound_metre_teaches_none():
    """Bach's corpus is chorales — 4/4, 3/4, 3/2 and no 6/8 at all. Yielding
    nothing for a 6/8 phrase is the honest answer; borrowing his 3/4 bars and
    presenting them as compound is not.
    """
    from scales.composition_brief import _corpus_meters, _retrieve_exemplars
    from scales.models import PhraseSlot

    assert not any(m == (6, 8) for m in _corpus_meters("bach"))
    slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(6, 8))
    assert _retrieve_exemplars("bach", slot, 4, []) == []
    # And a composer who DID write compound metre still teaches it.
    slot_c = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(6, 8))
    assert _retrieve_exemplars("chopin", slot_c, 4, [])


def test_an_empty_exemplar_result_says_why():
    """Every filter in the per-bar loop is a `continue`, so a spec whose
    candidates ALL fail returns nothing and, without this, says nothing — which
    reads as "this composer has no material" when it really means "every bar we
    found was unusable".

    Written against handel and schubert, whose records underfilled their metre.
    Both have since been re-acquired and now return exemplars, so the original
    `if exemplars: continue` guard skipped every case and this test executed
    **zero assertions** — it had stopped checking the behaviour entirely while
    still passing. The empty case is now CONSTRUCTED rather than waited for.
    """
    from scales.composition_brief import _retrieve_exemplars
    from scales.models import PhraseSlot

    cases = {
        "an unarmed composer": ("nobody_by_this_name", (4, 4)),
        "a metre the corpus has never seen": ("mozart", (23, 16)),
        "no composer at all": ("", (4, 4)),
    }
    for label, (composer, meter) in cases.items():
        warnings: list = []
        slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=meter)
        exemplars = _retrieve_exemplars(composer, slot, 4, warnings)
        assert not exemplars, f"{label}: expected no exemplars, got {len(exemplars)}"
        assert warnings, f"{label}: returned nothing and said nothing"


def test_real_composers_still_return_exemplars():
    """The other half: the check above must not be passing because retrieval is
    broken for everyone."""
    from scales.composition_brief import _retrieve_exemplars
    from scales.models import PhraseSlot

    for composer in ("mozart", "handel", "schubert"):
        slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(4, 4))
        assert _retrieve_exemplars(composer, slot, 4, []), composer


def test_a_metre_dead_end_blames_the_metre_not_the_texture():
    """Bach has thousands of singing_melody bars and never wrote 6/8. Reporting
    "no corpus exemplars for singing_melody/broken_chord_wave" sends the next
    reader after a texture problem that does not exist."""
    from scales.composition_brief import _retrieve_exemplars
    from scales.models import PhraseSlot

    warnings: list = []
    slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(6, 8))
    _retrieve_exemplars("bach", slot, 4, warnings)
    assert any("no 6/8 bars" in w for w in warnings), warnings
    assert any("metre, not the texture" in w for w in warnings), warnings


def test_old_format_records_are_not_shown_as_exemplars():
    """Corelli, Weber, Handel and Schubert are still on the pre-rewrite record
    format — no `rh_display`, no `time_sig`, no harmony.

    What reached the brief from one was HALF a bar: an empty right hand and a
    "left hand" playing at E5, which is Corelli's melody filed as accompaniment.
    That teaches something false — the melody is silent and the accompaniment
    sits in the treble — so it is worse than showing nothing. All four are
    already flagged `needs_reacquire`.
    """
    from scales.composition_brief import _iter_corpus_bars, _retrieve_exemplars
    from scales.models import PhraseSlot

    for composer in ("corelli", "weber", "handel", "schubert"):
        first = next(iter(_iter_corpus_bars(composer)), None)
        if first is None or "rh_display" in first:
            continue  # re-acquired since
        warnings: list = []
        slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(4, 4))
        assert _retrieve_exemplars(composer, slot, 3, warnings) == []
        assert any("old record format" in w for w in warnings), warnings

    # Composers on the rich format are unaffected.
    for composer in ("bach", "mozart", "palestrina"):
        slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=(4, 4))
        assert _retrieve_exemplars(composer, slot, 3, [])


def test_no_exemplar_shows_an_empty_voice():
    """`//` means "these two voices sound together".

    When the corpus bar had an empty main voice and a populated inner one, the
    renderer still joined them, so a hand reached the brief reading
    " // B3q rest_e Bb3s A3s" — a silent upper voice over an inner line, which
    is not what the bar does and not something to imitate. 6.2% of multi-voice
    exemplar hands read that way. One voice sounding is written as one voice.
    """
    import glob
    import os

    from scales.composition_brief import _retrieve_exemplars
    from scales.models import PhraseSlot

    composers = [
        os.path.basename(p.rstrip("/")) for p in sorted(glob.glob("tools/reference_index/*/"))
    ]
    assert composers, "no corpus on disk"
    checked = 0
    for composer in composers:
        for meter in ((4, 4), (3, 4)):
            slot = PhraseSlot(phrase_id="p", bar_start=1, bar_count=4, key="C", meter=meter)
            for exemplar in _retrieve_exemplars(composer, slot, 6, []):
                for shorthand in (exemplar.rh, exemplar.lh):
                    if "//" not in shorthand:
                        continue
                    checked += 1
                    voices = [v.strip() for v in shorthand.split("//")]
                    assert all(voices), f"{composer}: empty voice in {shorthand!r}"
    assert checked, "no multi-voice exemplars were examined"


# ── Form specs ───────────────────────────────────────────────────────────────


def test_binary_and_rounded_binary_are_real_forms_not_the_song_default():
    """Every Baroque dance and every Scarlatti sonata is binary, and the minuet
    is rounded binary — and neither had a spec, so both silently built a
    four-phrase A-B-A' song form. That is not a gigue in any respect that
    matters: no modulation to the dominant, no return.
    """
    from scales.models import StyleDNA
    from scales.scales import _build_binary

    def shape(key, rounded):
        slots = _build_binary(key, 100, (4, 4), StyleDNA(), "m1", rounded=rounded)
        return [(s.section_id, s.key, s.cadence_target) for s in slots]

    simple = shape("G major", False)
    # Two halves, and the first one LEAVES the tonic and cadences there.
    assert simple[0][0] == "m1_a" and simple[0][1] == "G major"
    assert simple[1][1] == "D major" and simple[1][2] == "PAC"
    assert simple[-1][1] == "G major" and simple[-1][2] == "PAC"
    assert {sec for sec, _, _ in simple} == {"m1_a", "m1_b"}, "simple binary has no reprise"

    # A minor-key first half goes to the RELATIVE MAJOR, not the minor dominant.
    assert shape("d minor", False)[1][1] == "F major"

    # Rounded binary brings the opening back, inside the second half.
    rounded = shape("G major", True)
    assert "m1_a2" in {sec for sec, _, _ in rounded}, "rounded binary must return"
    assert rounded[-1][1] == "G major" and rounded[-1][2] == "PAC"


def test_the_planning_guidance_lists_the_forms_that_exist(function_source):
    """An agent choosing a form has no way to know which are real but to be
    told, and an unknown name silently builds a song form."""
    from pathlib import Path

    from scales import scales

    doc = Path(__file__).resolve().parents[3] / ".claude" / "skills" / "w-plan" / "SKILL.md"
    if not doc.exists():
        return
    text = doc.read_text()
    for form in ("binary", "rounded_binary", "ternary", "sonata", "theme_variations"):
        assert f"`{form}`" in text, f"w-plan does not document the {form} form"
    # And the code's own list agrees.
    src = function_source(scales, "build_form_graph")
    for form in ("binary", "rounded_binary", "ternary", "sonata", "theme_variations"):
        assert form in src, f"{form} is documented but not dispatched"


def test_an_unreadable_corpus_shard_is_not_skipped_in_silence():
    """A corrupt or half-written shard was `continue`d without a word, so a
    composer quietly lost several thousand bars and every statistic downstream —
    density targets, fingerprints, the corpus profile the gate compares against
    — was computed over less corpus than it reported.

    Measured: truncating one of Mozart's four shards drops 2,000 of his 7,022
    bars. An interrupted rebuild is the ordinary way to get one, and nothing
    anywhere said which file to rebuild.
    """
    import shutil
    import tempfile
    from pathlib import Path

    import scales.composition_brief as brief

    source = Path("tools/reference_index/mozart")
    if not source.is_dir() or not list(source.glob("bars_*.json")):
        pytest.skip("no sharded corpus on disk")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        shutil.copytree(source, root / "mozart")
        shard = sorted((root / "mozart").glob("bars_*.json"))[0]
        shard.write_text("")  # what an interrupted write leaves behind

        original = brief._REFERENCE_INDEX
        try:
            brief._REFERENCE_INDEX = root
            with _capture_warnings() as logged:
                bars = sum(1 for _ in brief._iter_corpus_bars("mozart"))
        finally:
            brief._REFERENCE_INDEX = original

        assert bars > 0, "the other shards must still load"
        assert logged, "an unreadable shard must be reported, not skipped silently"
        assert any(str(shard.name) in line for line in logged), logged


class _capture_warnings:
    """Collect WARNING records from the module's logger."""

    def __enter__(self):
        import logging

        self._records: list = []
        self._handler = logging.Handler()
        self._handler.emit = lambda record: self._records.append(record.getMessage())
        self._logger = logging.getLogger("scales.composition_brief")
        self._logger.addHandler(self._handler)
        self._prev = self._logger.level
        self._logger.setLevel(logging.WARNING)
        return self._records

    def __exit__(self, *exc):
        self._logger.removeHandler(self._handler)
        self._logger.setLevel(self._prev)
        return False
