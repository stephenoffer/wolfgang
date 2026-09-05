"""Mutopia packages scores as ZIPs, and the crawler could not open one.

`acquire_composer`'s Mutopia fallback exists for composers KernScores lacks. It
accepted only loose `.mid`/`.krn`/`.xml` files — but Mutopia publishes a piece's
MIDI as `<piece>-mids.zip` beside the loose files, and for many pieces the ZIP
is the only copy. Corelli's entire holding is one zipped quartet, so the crawler
walked his whole folder, found nothing, and returned "no files" rather than "I
skipped an archive I could not read".

Measured across six composer folders, loose-only vs. with archives:

    CorelliA     0 ->  1        AlbenizIMF   1 ->  1
    VivaldiA     5 -> 11        SchubertF    0 ->  0
    ClementiM    0 ->  2        HandelGF     1 ->  2

Four of six gain and three go from nothing to something. Corelli went from 38
bars to 143 on the strength of it.

These tests are OFFLINE by construction — they build the archives they read.
A network test would be a test of Mutopia's uptime, and the two web sources had
already 503'd once during this work.
"""

import io
import zipfile
from pathlib import Path

import pytest
from scripts.acquire_composer import (
    _ARCHIVE_MAX_MEMBERS,
    _extract_score_archive,
    _is_score_archive,
)


def _zip(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, payload in members.items():
            zf.writestr(name, payload)
    return buf.getvalue()


# ─── Which archives are worth a download ─────────────────────────────────────


@pytest.mark.parametrize(
    "name", ["nr8-quartet-mids.zip", "sonata-xml.zip", "fugue-krn.zip", "PIECE-MIDS.ZIP"]
)
def test_a_score_bundle_is_recognised(name):
    assert _is_score_archive(name)


@pytest.mark.parametrize(
    "name",
    [
        "nr8-quartet-a4-pdfs.zip",  # engraved PDFs
        "nr8-quartet-let-pss.zip",  # PostScript
        "nr8-quartet-lys.zip",  # LilyPond source, not playable
        "nr8-quartet.mid",  # a loose file, handled by the other branch
        "notes.txt",
    ],
)
def test_an_archive_of_something_else_is_not_downloaded(name):
    """The name is the filter: rejecting these after downloading would cost a
    request each, and a Mutopia leaf carries four PDF archives per piece."""
    assert not _is_score_archive(name)


# ─── Unpacking ───────────────────────────────────────────────────────────────


def test_the_playable_members_are_written_out(tmp_path: Path):
    data = _zip({"soundch.mid": b"MThd\x00", "soundch-1.mid": b"MThd\x01", "readme.txt": b"hi"})
    written = _extract_score_archive(data, tmp_path, "nr8-quartet")
    assert len(written) == 2
    assert all(Path(w).name.startswith("nr8-quartet__") for w in written), (
        "leaf folders reuse basenames, so members must stay disambiguated by piece"
    )
    assert all(Path(w).suffix == ".mid" for w in written)
    assert (tmp_path / "nr8-quartet__soundch.mid").read_bytes() == b"MThd\x00"


def test_nested_paths_are_flattened_not_reproduced(tmp_path: Path):
    """A member named `../x.mid` must not write outside the destination."""
    written = _extract_score_archive(_zip({"a/b/piece.mid": b"MThd"}), tmp_path, "p")
    assert len(written) == 1
    assert Path(written[0]).parent == tmp_path


# ─── A bad archive costs one source, never the acquisition ───────────────────


def test_a_corrupt_archive_is_skipped_quietly(tmp_path: Path):
    assert _extract_score_archive(b"not a zip at all", tmp_path, "p") == []


def test_an_empty_archive_yields_nothing(tmp_path: Path):
    assert _extract_score_archive(_zip({}), tmp_path, "p") == []


def test_an_archive_of_only_unplayable_members_yields_nothing(tmp_path: Path):
    assert _extract_score_archive(_zip({"a.pdf": b"%PDF", "b.ly": b"\\score"}), tmp_path, "p") == []


def test_an_implausible_member_count_is_refused(tmp_path: Path):
    """A MIDI bundle for one piece is a handful of files, not a thousand."""
    many = {f"p{i}.mid": b"MThd" for i in range(_ARCHIVE_MAX_MEMBERS + 5)}
    assert _extract_score_archive(_zip(many), tmp_path, "p") == []
    assert not list(tmp_path.iterdir()), "nothing may be written before the refusal"


def test_an_implausibly_large_archive_is_refused(tmp_path: Path):
    """Guards against a decompression bomb without trusting the header alone."""
    assert (
        _extract_score_archive(_zip({"big.mid": b"\x00" * (33 * 1024 * 1024)}), tmp_path, "p") == []
    )
