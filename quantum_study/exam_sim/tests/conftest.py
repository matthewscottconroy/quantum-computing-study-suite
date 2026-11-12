"""Fixtures for the exam-sim tests.

The repository's root ``conftest.py`` provides ``qapp``, headless Qt and a
process-wide throwaway data directory.  This file narrows the data directory
to a fresh ``tmp_path`` per test and adds what only this app needs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the suite data directory at a temp dir for one test."""
    from quantum_study.exam_sim import persistence
    from quantum_study.common import schema

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))
    # The "one backup per file per process" memo is global; without this the
    # second test in a process would skip its backup because the first test
    # already backed up a file of the same name in a different temp dir.
    schema.reset_session()
    persistence.clear_write_error()
    assert persistence.DATA_DIR == root, "config/persistence ignored the override"
    yield root
    schema.reset_session()
    persistence.clear_write_error()


@pytest.fixture(scope="session")
def questions():
    from quantum_study.exam_sim.bank import all_questions
    return all_questions()
