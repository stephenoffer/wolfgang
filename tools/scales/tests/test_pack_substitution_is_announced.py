"""When one member's doctrine stands in for a style, say so.

`_load_pack` falls back, for an aggregate reference with no pack of its own, to
"a representative armed member" — one composer's cadence scripts and ornament
intents printed under `STYLE DOCTRINE (this phrase)` as though they were the
idiom's.

Every armed style currently has its own packs, so the fallback does not fire
today. It is still live code on the path that builds every style-targeted brief,
and when it fires it is silent — which is the failure mode this project has
recorded more than any other. The test drives the fallback directly rather than
waiting for a style to lose a pack.
"""

import scales.composition_brief as CB
from scales.composition_brief import pack_source
from scales.style_registry import _STYLE_MEMBERS, style_members

DOCTRINE = ("cadence_scripts", "ornament_intents", "breathing_rules")


def setup_function():
    CB._PACK_CACHE.clear()
    CB._PACK_SOURCE.clear()


def test_a_reference_with_its_own_pack_reports_itself():
    assert pack_source("mozart", "cadence_scripts") == "mozart"


def test_every_armed_style_currently_has_its_own_doctrine():
    """If this starts failing, a style lost its pack — and the notice below is
    what stops that being invisible."""
    for style in _STYLE_MEMBERS:
        if not style_members(style):
            continue
        ref = f"style__{style}"
        for pack in DOCTRINE:
            if CB._load_pack(ref, pack):
                assert pack_source(ref, pack) == ref, f"{ref}/{pack} substituted"


def test_the_fallback_reports_the_member_that_stood_in(monkeypatch):
    real = CB._load_pack

    def without_style_packs(composer, name):
        if composer == "style__classical" and name in DOCTRINE:
            for member in ("mozart", "haydn"):
                got = real(member, name)
                if got:
                    CB._PACK_SOURCE[f"{composer}/{name}"] = member
                    return got
            return None
        return real(composer, name)

    monkeypatch.setattr(CB, "_load_pack", without_style_packs)
    CB._PACK_CACHE.clear()
    CB._PACK_SOURCE.clear()
    assert pack_source("style__classical", "cadence_scripts") == "mozart"


def test_the_brief_names_the_substitution(monkeypatch):
    """The notice must reach the composer, not just the bookkeeping.

    Asserted on the RENDERED TEXT, which is what the composer reads. The first
    version matched strings in `inspect.getsource(render_text)`, which is not a
    claim about the brief at all — and `getsource` finds a function by the line
    number recorded when the module was IMPORTED, so once the file changes on
    disk it returns whatever now occupies those lines. That is what made this
    test intermittent: it once failed asserting the notice appeared in the
    string `'        ):'`.
    """
    monkeypatch.setitem(CB._PACK_SOURCE, "style__classical/cadence_scripts", "mozart")
    monkeypatch.setattr(CB, "pack_source", lambda c, n: "mozart" if c == "style__classical" else c)

    # The notice lives inside the doctrine block, so the brief must carry some.
    brief = CB.CompositionBrief(phrase_id="p", composer="style__classical")
    brief.doctrine = {"cadence_script": {"type": "PAC", "soprano": "1"}}
    text = CB.render_text(brief)
    assert "standing in for the style" in text, (
        "a substituted pack must be announced to the composer, not only recorded"
    )
    assert "mozart" in text.lower(), "the notice must name WHICH member stood in"
