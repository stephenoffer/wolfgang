"""Shared pytest setup for the SCALES test suite.

Makes the top-level ``scales`` package importable when the suite is run without
an editable install (``pip install -e .``) — pytest auto-loads this file before
collecting tests, so individual test modules need no ``sys.path`` manipulation.
"""

import sys
from pathlib import Path

import pytest

_TOOLS = Path(__file__).resolve().parents[2]  # repo's tools/ directory
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))


@pytest.fixture
def tmp_workspace(tmp_path, monkeypatch):
    """Isolated workspace dir with ``scales._WORKSPACE`` pointed at it.

    Mirrors the manual setup in each gate test's ``__main__`` runner so the same
    test functions work under both ``pytest`` and direct execution.
    """
    from scales import scales

    monkeypatch.setattr(scales, "_WORKSPACE", tmp_path)
    return tmp_path
