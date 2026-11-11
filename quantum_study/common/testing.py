"""Test support shared by every suite in the repository.

Nothing in the apps imports this module; the repository's root ``conftest.py``
does, and exposes what is here as fixtures to every test.  It has no pytest
import of its own, so it is safe to import anywhere.

Two things used to go wrong, both silently:

* **A test wrote into the developer's own study journal.**  A missing or blank
  ``QUANTUM_STUDY_DATA_DIR`` means "use the real ``~/.local/share/quantum-study``",
  and the per-test fixtures that redirect it are opt-in.  :func:`isolate_data_dir`
  sets a throwaway default for the whole process before any app is imported.

* **Qt objects were destroyed at arbitrary moments.**  Several test modules
  each built their own ``QApplication`` and left closed widgets for Python's
  garbage collector, which then freed them in the middle of some later test's
  event delivery; CI segfaulted inside Qt.  :func:`qapplication` creates the
  application once and keeps it, and :func:`settle_qt` destroys whatever a
  test left behind at a point where Qt is idle.
"""
from __future__ import annotations

import atexit
import gc
import os
import shutil
import tempfile
from pathlib import Path

__all__ = ["isolate_data_dir", "qapplication", "settle_qt"]

_QAPP = None
_DATA_DIR: Path | None = None


def isolate_data_dir() -> Path:
    """Point ``QUANTUM_STUDY_DATA_DIR`` at a temp directory for this process.

    Always overrides - a developer's own setting must not be touched either -
    and is idempotent.  The directory is removed at interpreter exit.
    """
    global _DATA_DIR
    if _DATA_DIR is None:
        _DATA_DIR = Path(tempfile.mkdtemp(prefix="quantum-study-tests-"))
        atexit.register(shutil.rmtree, _DATA_DIR, ignore_errors=True)
    os.environ["QUANTUM_STUDY_DATA_DIR"] = str(_DATA_DIR)
    return _DATA_DIR


def qapplication():
    """The one offscreen ``QApplication`` for the whole test process."""
    global _QAPP
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PyQt6.QtWidgets import QApplication

    if _QAPP is None:
        _QAPP = QApplication.instance() or QApplication([])
    return _QAPP


def settle_qt() -> None:
    """Destroy every widget that is no longer wanted, now.

    Delivers pending events, acts on every ``deleteLater()`` (a bare
    ``processEvents()`` outside an event loop does not), then collects Python
    garbage so a wrapper stuck in a reference cycle takes its C++ object with
    it here rather than inside a later test's event handler.
    """
    if _QAPP is None:
        return
    from PyQt6.QtCore import QCoreApplication, QEvent

    _QAPP.processEvents()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    gc.collect()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    _QAPP.processEvents()
