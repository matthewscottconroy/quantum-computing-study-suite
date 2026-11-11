"""Fixtures for the flashcard-drill tests.

The repository's root ``conftest.py`` provides ``qapp``, headless Qt and a
process-wide throwaway data directory.  This file narrows the data directory
to a fresh ``tmp_path`` per test and adds what only this app needs.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile

import pytest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


REAL_DATA_DIR = pathlib.Path.home() / ".local" / "share" / "quantum-study"


@pytest.fixture(autouse=True)
def data_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Per-test data directory: one environment variable, resolved at call time."""
    from quantum_study.common import journal, schema

    target = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    # Per-process state that would otherwise leak between tests: "this file has
    # already been backed up once" and "the last write was refused".
    schema.reset_session()
    journal.clear_write_error()
    assert target != REAL_DATA_DIR        # belt and braces: never the real one
    return target
