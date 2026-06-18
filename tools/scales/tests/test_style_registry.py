"""Unit tests for style_registry.py. Run: python3 -m scales.tests.test_style_registry"""

from scales import style_registry as SR


def test_normalize_and_synonyms():
    assert SR.normalize_style("classical") == "classical"
    assert SR.normalize_style("Galant") == "classical"
    assert SR.normalize_style("baroque-era") == "baroque"
    assert SR.normalize_style("nonsense-xyz") is None


def test_style_id_helpers():
    sid = SR.make_style_id("classical")
    assert sid == "style__classical"
    assert SR.is_style_id(sid)
    assert not SR.is_style_id("mozart")
    assert SR.style_name(sid) == "classical"
    assert SR.style_name("mozart") == "mozart"  # non-style passthrough


def test_members_armed_filtering():
    # classical members are armed (corpus present in this repo)
    members = SR.style_members("classical")
    assert "mozart" in members and "haydn" in members
    # superset includes composers that may not be armed
    assert set(SR.all_style_members("classical")) >= set(members)


def test_resolve_composer_vs_style_vs_unknown():
    assert SR.resolve_reference("mozart")["kind"] == "composer"
    r_style = SR.resolve_reference("classical")
    assert r_style["kind"] == "style" and r_style["id"] == "style__classical"
    assert r_style["armed"] and r_style["members"]
    r_unknown = SR.resolve_reference("rachmaninoff")
    assert r_unknown["kind"] == "unknown" and not r_unknown["armed"]


def test_unknown_style_with_no_armed_members():
    # impressionist is a known style but has no armed composers in this repo
    r = SR.resolve_reference("impressionist")
    assert r["kind"] == "style"
    assert r["armed"] is False
    assert r["members"] == []


def test_styles_for_composer():
    styles = SR.styles_for_composer("mozart")
    assert "classical" in styles


def test_available_styles_nonempty():
    avail = {s["style"] for s in SR.available_styles()}
    # at least the armed period styles in this repo
    assert {"classical", "baroque", "romantic"} <= avail


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"ok {fn.__name__}")
    print(f"\n{len(fns)} tests passed")
