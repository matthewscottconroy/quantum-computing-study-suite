"""The root suite must run on ONE QApplication, and leave no widget behind.

CI segfaulted inside Qt's window-activation delivery once three modules each
had their own module-scoped ``qapp`` fixture: the application was destroyed
and rebuilt between modules, and widgets from the earlier ones were still
waiting to be deleted.  See ``quantum_study/common/testing.py``.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from quantum_study.common import testing

TESTS = Path(__file__).resolve().parent


def _builds_a_qapplication(path: Path) -> bool:
    """True if the file *calls* QApplication(...) in its own code.  A child
    process that a test starts from a code string has to build one, and a
    string is not a call."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name == "QApplication":
                return True
    return False


def test_no_test_builds_its_own_qapplication():
    """Every suite in the repository, not just this one."""
    repo = TESTS.parent
    files = list(TESTS.glob("*.py")) + list((repo / "quantum_study").glob("*/tests/*.py"))
    offenders = sorted(str(p.relative_to(repo)) for p in files if _builds_a_qapplication(p))
    assert not offenders, (
        "use the session-wide `qapp` fixture from the root conftest.py instead "
        f"of constructing a QApplication in {offenders}")


def test_the_application_is_kept_alive_for_the_whole_run(qapp):
    from PyQt6.QtWidgets import QApplication

    assert testing._QAPP is qapp
    assert QApplication.instance() is qapp


def test_settle_qt_destroys_a_widget_marked_for_deletion(qapp):
    """deleteLater() + processEvents() alone does NOT delete outside an event
    loop; settle_qt() must, or dead widgets pile up until the collector runs."""
    from PyQt6 import sip
    from PyQt6.QtWidgets import QWidget

    w = QWidget()
    w.show()
    w.close()
    w.deleteLater()
    qapp.processEvents()
    assert not sip.isdeleted(w), "premise: a bare processEvents() leaves it alive"
    testing.settle_qt()
    assert sip.isdeleted(w)


def test_settle_qt_collects_a_widget_stuck_in_a_reference_cycle(qapp):
    import weakref

    from PyQt6.QtWidgets import QPushButton, QWidget

    destroyed = []

    def build():
        w = QWidget()
        btn = QPushButton("x", w)
        btn.clicked.connect(lambda: w.close())      # w -> btn -> lambda -> w
        w.destroyed.connect(lambda: destroyed.append(True))
        return weakref.ref(w)

    ref = build()
    assert ref() is not None, "premise: reference counting alone cannot free it"
    testing.settle_qt()
    assert ref() is None
    assert destroyed == [True], "the C++ widget must go with its wrapper"
