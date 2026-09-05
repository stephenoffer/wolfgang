"""A corpus attributed to the wrong composer is worse than no corpus.

Mutopia folder codes are `<Surname><Initials>` and several surnames carry more
than one composer. The resolver matched on surname PREFIX and returned whichever
sorted first, so `bach` resolved to **BachCPE** — Carl Philipp Emanuel. The tool
downloaded a CPE rondo into `_fetch_bach/` intending it as J.S. Bach, and one
successful parse would have merged it into his corpus.

`haydn` is FJ/JM (Joseph and his brother Michael), `strauss` is F/JJ,
`williams` is R/RH — none of them the Richard Strauss or John Williams this
project's profiles describe.
"""

from scripts.acquire_composer import _split_mutopia_code


def test_a_folder_code_splits_into_surname_and_initials():
    assert _split_mutopia_code("BachCPE") == ("Bach", "CPE")
    assert _split_mutopia_code("BachJS") == ("Bach", "JS")
    assert _split_mutopia_code("LisztF") == ("Liszt", "F")
    assert _split_mutopia_code("HaydnFJ") == ("Haydn", "FJ")
    assert _split_mutopia_code("RimskyKorsakovN")[1] == "N"


def _resolve(monkeypatch, name, folders):
    from scripts import acquire_composer as AC

    html = "".join(f'<a href="{f}/">{f}</a>' for f in folders).encode()
    monkeypatch.setattr(AC, "_http_get", lambda url, **k: html)
    return AC._mutopia_composer_code(name)


BACHES = ["BachCPE", "BachJS", "BachJC"]


def test_a_shared_surname_resolves_to_the_intended_composer(monkeypatch):
    """`bach` must be Johann Sebastian, not whichever sorts first."""
    assert _resolve(monkeypatch, "bach", BACHES) == "BachJS"


def test_initials_select_a_specific_composer_in_either_order(monkeypatch):
    assert _resolve(monkeypatch, "bach cpe", BACHES) == "BachCPE"
    assert _resolve(monkeypatch, "cpe bach", BACHES) == "BachCPE"
    assert _resolve(monkeypatch, "js bach", BACHES) == "BachJS"


def test_an_unresolvable_ambiguity_is_refused_not_guessed(monkeypatch):
    """No entry in the intended-composer table and no initials from the caller:
    returning either folder would silently attribute one composer's music to
    another."""
    assert _resolve(monkeypatch, "smith", ["SmithA", "SmithB"]) is None


def test_a_surname_is_matched_exactly_not_by_prefix(monkeypatch):
    """`williams` must not match `WilliamsonX`, and a prefix match is what put
    Vaughan Williams in reach of a request for John Williams."""
    assert _resolve(monkeypatch, "wills", ["WilliamsR", "WillisRS"]) is None
    assert _resolve(monkeypatch, "willis", ["WilliamsR", "WillisRS"]) == "WillisRS"


def test_an_unambiguous_surname_still_resolves(monkeypatch):
    assert _resolve(monkeypatch, "liszt", ["LisztF", "BachJS"]) == "LisztF"
    assert _resolve(monkeypatch, "franz liszt", ["LisztF", "BachJS"]) == "LisztF"


def test_the_intended_composers_are_the_ones_this_project_names():
    """The table must point at the composer whose PROFILE exists here."""
    from scripts.acquire_composer import _MUTOPIA_INITIALS

    assert _MUTOPIA_INITIALS["bach"] == "JS"
    assert _MUTOPIA_INITIALS["haydn"] == "FJ"
