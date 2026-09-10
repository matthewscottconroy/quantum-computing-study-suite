"""Shared fixtures for quantum-quiz tests.

* Puts the app root on sys.path so bare imports (``from core.topics import TOPICS``)
  work exactly as they do when the app runs.
* Points QUANTUM_STUDY_DATA_DIR at a throwaway session directory *before* any
  app module is imported (apps that honour the variable never see real data),
  and then, per test, relocates every module-level path constant that points
  into either the real ``~/.local/share/quantum-study`` or that session
  directory into a fresh ``tmp_path`` (autouse, so it also covers the
  MainWindow smoke test and gives each test an empty history).
* Forces the offscreen Qt platform so the suite runs headless.
"""
from __future__ import annotations

import importlib
import os
import pathlib
import shutil
import sys
import tempfile

import pytest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Always override (never inherit) so a developer's own QUANTUM_STUDY_DATA_DIR is
# never touched either.  Must happen before any app import.
_SESSION_DATA_DIR = pathlib.Path(tempfile.mkdtemp(prefix="quantum-quiz-tests-"))
os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_SESSION_DATA_DIR)

REAL_DATA_DIR = pathlib.Path.home() / ".local" / "share" / "quantum-study"
_DATA_ROOTS = (REAL_DATA_DIR, _SESSION_DATA_DIR)

# Every module that defines a Path constant pointing into the data dir.
_PATH_MODULES = ("persistence",)


def _relocate(path: pathlib.PurePath, target: pathlib.Path) -> pathlib.Path | None:
    for root in _DATA_ROOTS:
        try:
            return target / path.relative_to(root)
        except ValueError:
            continue
    return None


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_SESSION_DATA_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def data_dir(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> pathlib.Path:
    """Per-test data directory; all persistence path constants are pointed at it."""
    target = tmp_path / "quantum-study"
    for mod_name in _PATH_MODULES:
        mod = importlib.import_module(mod_name)
        for name, value in list(vars(mod).items()):
            if isinstance(value, pathlib.PurePath):
                relocated = _relocate(value, target)
                if relocated is not None:
                    monkeypatch.setattr(mod, name, relocated)
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    return target


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole session."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app
