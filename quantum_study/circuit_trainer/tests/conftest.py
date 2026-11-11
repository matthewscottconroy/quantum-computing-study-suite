"""Fixtures for the circuit-trainer tests.

The repository's root ``conftest.py`` provides ``qapp``, headless Qt and a
process-wide throwaway data directory.  This file narrows the data directory
to a fresh ``tmp_path`` per test and adds what only this app needs.
"""
from __future__ import annotations

import os
import pathlib
import sys

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point every persistence path at a throwaway directory.

    Since the migration to ``common.datadir`` the location is resolved on every
    call rather than frozen into a module constant at import time, so setting
    the environment variable is the whole fixture — there are no private names
    left to patch.  (The subprocesses some tests spawn inherit it too.)

    ``common.schema`` keeps a process-wide "already backed up this file" set so
    a drill that logs two hundred rows makes one backup; it is cleared here so
    each test starts a fresh backup session.
    """
    from quantum_study.common import journal, schema

    data_dir = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(data_dir))
    schema.reset_session()
    journal.clear_write_error()
    yield data_dir
    schema.reset_session()
    journal.clear_write_error()
