"""The root suite must run on ONE QApplication, and leave no widget behind.

CI segfaulted inside Qt's window-activation delivery once three modules each
had their own module-scoped ``qapp`` fixture: the application was destroyed
and rebuilt between modules, and widgets from the earlier ones were still
waiting to be deleted.  See the note above ``qapp`` in conftest.py.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import conftest

TESTS = Path(__file__).resolve().parent


def test_only_conftest_builds_a_qapplication():
    offenders = sorted(
        p.name for p in TESTS.glob("*.py")
        if p.name not in {"conftest.py", Path(__file__).name}
        and "QApplication(" in p.read_text(encoding="utf-8"))
    assert not offenders, (
        "use the session-wide `qapp` fixture from conftest.py instead of "
        f"constructing a QApplication in {offenders}")


def test_the_application_is_kept_alive_by_conftest(qapp):
    from PyQt6.QtWidgets import QApplication

    assert conftest._QAPP is qapp
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
    conftest.settle_qt()
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
    conftest.settle_qt()
    assert ref() is None
    assert destroyed == [True], "the C++ widget must go with its wrapper"
