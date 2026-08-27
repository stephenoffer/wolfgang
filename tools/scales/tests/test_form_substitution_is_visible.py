"""Asking for a form this system has no spec for must say so.

`_build_simple` is a reasonable default — but it was silent. `rondo` returned a
four-phrase A-B-A' with no refrain returns; `minuet_trio` came back with no
trio; `fugue` and `binary` were the same song form under different names.
Nothing in the result said the form asked for was not the form built, and two
pieces in this repo were composed on `binary` believing it meant something.
"""

import shutil

import pytest

from scales.scales import _WORKSPACE, build_form_graph, compile_style, init_workspace


def _known_forms():
    """The forms the builder actually dispatches, read from the system.

    Hardcoding this list meant every form ADDED to the system broke the test —
    the same brittleness as encoding which composers happen to be armed. What
    the test is for is that a known form builds silently and an unknown one
    reports, and neither claim needs a literal.
    """
    from scales.scales import _KNOWN_FORMS

    return tuple(_KNOWN_FORMS)


KNOWN = _known_forms()


def _build(form):
    pid = f"_test_form_{form}"
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    init_workspace(pid, mode="compose_from_text", description="x")
    compile_style(pid, composers=["haydn"])
    out = build_form_graph(pid, form=form, key="C major", tempo_bpm=96, meter=(2, 4))
    shutil.rmtree(_WORKSPACE / pid, ignore_errors=True)
    return out


def _warning(out):
    return next(
        (x for x in out if isinstance(x, dict) and x.get("warning") == "form_substituted"), None
    )


@pytest.mark.parametrize("form", KNOWN)
def test_a_known_form_is_built_without_complaint(form):
    assert _warning(_build(form)) is None


@pytest.mark.parametrize("form", ["rondo", "fugue", "minuet_trio", "nonsense"])
def test_an_unknown_form_is_reported(form):
    w = _warning(_build(form))
    assert w is not None, f"{form} was substituted silently"
    assert w["requested"] == form
    assert "song form" in w["built"]
    assert set(w["known_forms"]) == set(KNOWN)


def test_theme_variations_really_builds_variations():
    """It is a known form and must not be the ternary default: a theme plus
    several variations, each its own section."""
    out = _build("theme_variations")
    secs = {x["section"] for x in out if isinstance(x, dict) and "section" in x}
    assert any("theme" in s for s in secs), secs
    assert sum(1 for s in secs if "var" in s) >= 3, secs


def test_the_warning_says_what_is_missing():
    """A number is not actionable; the composer needs to know what a rondo built
    this way does not have."""
    w = _warning(_build("rondo"))
    assert "refrain" in w["note"] or "trio" in w["note"]
