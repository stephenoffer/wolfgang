"""A form must be CLAIMED by a profile, not merely mentioned in it.

`_pass_formal_grammar` asked `if "sonata" in text.lower()`. Palestrina's
formal-approach.md opens "There is no sonata, no rondo, no ternary reprise" —
and the compiler handed a 16th-century vocal polyphonist a sonata graph with
exposition keys I and V and a tonic recapitulation rule. Thirteen profiles
phrase a form by denying it.
"""

from scales.context_compiler import _form_is_asserted


def test_a_denied_form_is_not_claimed():
    text = "There is no sonata, no rondo, no ternary reprise — asking where the B section is mistakes the genre."
    assert not _form_is_asserted(text, "sonata")
    assert not _form_is_asserted(text, "rondo")
    assert not _form_is_asserted(text, "ternary")


def test_an_asserted_form_is_claimed():
    assert _form_is_asserted("The first movement is in sonata form.", "sonata")
    assert _form_is_asserted("## Sonata Form — Haydn's Game", "sonata")
    assert _form_is_asserted("| Sonata form | Monothematic variant |", "sonata")


def test_negation_is_read_per_clause():
    """ "It is a rondo, not a sonata" claims one form and denies the other."""
    t = "The finale is a rondo, not a sonata."
    assert _form_is_asserted(t, "rondo")
    assert not _form_is_asserted(t, "sonata")


def test_contrastive_phrasings_do_not_claim_the_contrasted_form():
    for t in (
        "Unlike sonata form, this unfolds continuously.",
        "He writes variations rather than sonata movements.",
        "This is nothing like a rondo.",
        "Instead of a ternary reprise the text simply ends.",
    ):
        form = "sonata" if "sonata" in t else ("rondo" if "rondo" in t else "ternary")
        assert not _form_is_asserted(t, form), t


def test_the_renaissance_composers_claim_no_sonata():
    """The specific absurdity that prompted this."""
    import json
    import os

    for c in ("palestrina", "monteverdi"):
        p = f"tools/compiled_packs/{c}/formal_graphs.json"
        if not os.path.exists(p):
            continue
        forms = json.load(open(p)).get("forms") or {}
        assert "sonata" not in forms, f"{c} claims sonata form"


def test_a_minor_key_exposition_does_not_go_to_the_dominant():
    """The key scheme was hardcoded to I-V for every sonata. A minor-key
    exposition goes to the relative major."""
    import json
    import os

    p = "tools/compiled_packs/mozart/formal_graphs.json"
    if not os.path.exists(p):
        return
    ks = ((json.load(open(p)).get("forms") or {}).get("sonata") or {}).get("key_scheme") or {}
    assert ks.get("exposition_keys_minor") == ["i", "III"], ks
    assert ks.get("exposition_keys_major") == ["I", "V"], ks
