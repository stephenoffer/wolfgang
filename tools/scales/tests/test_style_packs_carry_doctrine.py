"""A style pack shipped with none of the composer-profile doctrine.

Composing "in the classical style" rather than "as Mozart" is a first-class mode
in this system — `style_registry` resolves `style__classical` to Mozart, Haydn
and Beethoven, and the corpus primitives in `composition_brief` already
aggregate exemplars, fingerprints and density over those members.

The COMPILER did not. Every profile-derived pass takes one directory, and a
style id has none, so `compile("style__classical")` produced:

                     orchestration   influences   prototypes
    mozart                      40           15            8
    chopin                      64           17           14
    style__classical             0            0            0
    style__baroque               0            0            0
    style__romantic              0            0            0

Only the passes fed by the SHARED general documents — figuration templates,
cadence scripts, harmonic devices — survived, which is exactly why the style
packs looked populated and nobody noticed. A style request lost every device
catalogue, every LH vocabulary, every worked procedure and every orchestration
role its members had.

After aggregating each pass over the member profiles:

    style__classical            79           46           11
    style__baroque             222           45            9
    style__romantic            204          118           22
    style__renaissance          66            0*           4     (*honest: neither
                                                                  member has a
                                                                  cross-references.md)
"""

import json
import os

import pytest

_STYLES = ("style__classical", "style__baroque", "style__romantic", "style__renaissance")


def _pack(style, name):
    path = f"tools/compiled_packs/{style}/{name}.json"
    if not os.path.exists(path):
        pytest.skip(f"{style} not compiled")
    return json.load(open(path))


@pytest.mark.parametrize("style", _STYLES)
def test_a_style_carries_orchestration_roles(style):
    data = _pack(style, "orchestration_roles")
    # 15, not 20: Palestrina and Monteverdi between them describe 19 voice
    # roles, which is everything a two-member Renaissance style has. The
    # threshold exists to catch a return to ZERO, not to demand a number the
    # smallest style cannot reach.
    assert len(data.get("instruments", {})) + len(data.get("textures", [])) >= 15


@pytest.mark.parametrize("style", _STYLES)
def test_a_style_carries_its_members_forms(style):
    assert len(_pack(style, "formal_graphs").get("forms", {})) >= 5


@pytest.mark.parametrize("style", _STYLES)
def test_a_style_carries_worked_prototypes(style):
    data = _pack(style, "phrase_prototypes")
    protos = data.get("prototypes", []) if isinstance(data, dict) else data
    assert len(protos) >= 3, f"{style} has no worked composing procedure from any member"


def test_a_style_is_richer_than_any_one_member():
    """The point of aggregating: the classical style should know more than
    Mozart alone, because it is also Haydn and Beethoven."""
    style = _pack("style__classical", "orchestration_roles")
    mozart = _pack("mozart", "orchestration_roles")
    n_style = len(style.get("instruments", {})) + len(style.get("textures", []))
    n_mozart = len(mozart.get("instruments", {})) + len(mozart.get("textures", []))
    assert n_style > n_mozart


def test_the_renaissance_influence_gap_is_honest_not_a_parse_failure():
    """`style__renaissance` has no influences because neither Palestrina nor
    Monteverdi has a `cross-references.md` at all. An empty field whose source
    does not exist is correct; the test records WHY so it is not "fixed" by
    inventing one."""
    import glob

    for member in ("palestrina", "monteverdi"):
        assert not glob.glob(f".claude/context/*/composer-profiles/{member}/cross-references.md"), (
            f"{member} now has a cross-references.md — the style should inherit it"
        )


def test_merging_deduplicates_by_id():
    """Two members sharing a device must not yield it twice."""
    from scales.context_compiler import _merge_pass_result

    merged = _merge_pass_result(
        [{"id": "a", "n": 1}, {"id": "b", "n": 2}],
        [{"id": "b", "n": 2}, {"id": "c", "n": 3}],
    )
    assert [e["id"] for e in merged] == ["a", "b", "c"]


def test_merging_nested_dicts_keeps_both_sides():
    from scales.context_compiler import _merge_pass_result

    merged = _merge_pass_result(
        {"forms": {"sonata": {"sections": []}}},
        {"forms": {"fugue": {"sections": []}}},
    )
    assert set(merged["forms"]) == {"sonata", "fugue"}


def test_a_plain_composer_is_unaffected_by_the_style_branch():
    """Mozart must compile exactly as before."""
    data = _pack("mozart", "orchestration_roles")
    assert len(data.get("instruments", {})) + len(data.get("textures", [])) >= 20
