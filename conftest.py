"""Repository-wide pytest configuration: applies to ``tests/`` and to every
``quantum_study/<app>/tests/``.

The helpers and the reasons for them are in ``quantum_study/common/testing.py``.
"""
from __future__ import annotations

import os

import pytest

from quantum_study.common import testing

# Before anything imports an app: headless Qt, and a study-data directory that
# is never the developer's real one.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLBACKEND", "Agg")
testing.isolate_data_dir()


@pytest.fixture(scope="session")
def qapp():
    """The one offscreen QApplication for the whole test process."""
    pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not installed")
    return testing.qapplication()


@pytest.fixture(autouse=True)
def _settle_qt_after_each_qt_test(request):
    """Autouse, so it is set up first and torn down last - after the test's own
    fixtures have closed their windows."""
    yield
    if "qapp" in request.fixturenames:
        testing.settle_qt()
