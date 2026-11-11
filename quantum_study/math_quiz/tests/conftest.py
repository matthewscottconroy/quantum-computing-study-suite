"""Fixtures for the math-quiz tests.

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
    """Per-test data directory.  Everything resolves through the env var."""
    target = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    # common.schema backs a file up once per process and common.journal
    # remembers the last refused write; each test gets a clean slate so a
    # backup is taken (and asserted on) in the test that wants one, and a
    # refusal never leaks into the next test.
    from quantum_study.common import journal, schema
    schema.reset_session()
    journal.clear_write_error()
    yield target
    schema.reset_session()
    journal.clear_write_error()
