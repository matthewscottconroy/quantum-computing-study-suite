"""Offscreen MainWindow tests: constructs with no API key/data, screen routing,
and the flag-for-review round trip through the controller."""
from __future__ import annotations

import json

import pytest
from PyQt6.QtWidgets import QMessageBox, QPushButton

from core.models import Question

FLAG_KEYS = {"id", "label", "category", "app", "timestamp"}


def _button(widget, text: str) -> QPushButton:
    for b in widget.findChildren(QPushButton):
        if b.text() == text:
            return b
    raise AssertionError(f"no button {text!r}; have {[b.text() for b in widget.findChildren(QPushButton)]}")


def _question(text: str = "Derive the Bloch-sphere coordinates of |+>.") -> Question:
    return Question(subject="Quantum Mechanics", topic="the Bloch sphere representation of a qubit",
                    difficulty="beginner", question_type="conceptual explanation", text=text)


@pytest.fixture
def win(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    w = MainWindow()
    w.show()
    qapp.processEvents()
    yield w
    w.close()
    w.deleteLater()


def test_main_window_constructs_on_setup_page(win):
    from ui.main_window import PAGE_SETUP
    assert win.windowTitle()
    assert win.centralWidget() is not None
    assert win._stack.currentIndex() == PAGE_SETUP
    assert win._stack.count() == 6


def test_reference_button_opens_docs_browser_and_back_returns(win, qapp):
    from ui.main_window import PAGE_REFERENCE, PAGE_SETUP

    _button(win._setup_screen, "Reference").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_REFERENCE
    assert win._reference_screen._list.count() >= 59
    assert win._reference_screen.current_doc_path() is not None

    _button(win._reference_screen, "← Back").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_SETUP


def test_history_button_opens_history_and_back_returns(win, qapp):
    from ui.main_window import PAGE_HISTORY, PAGE_SETUP

    _button(win._setup_screen, "View History").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_HISTORY
    _button(win._history_screen, "← Back to Setup").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_SETUP


def test_flag_toggle_writes_a_question_specific_entry(win, data_dir):
    import persistence

    q1 = _question()
    win._current_question = q1
    assert win._current_question_flagged() is False

    win._on_flag_toggled()
    entries = json.loads(persistence._FLAGGED_FILE.read_text())
    assert len(entries) == 1
    e = entries[0]
    assert set(e) == FLAG_KEYS
    assert e["id"] == persistence.question_flag_id(q1.subject, q1.topic, q1.text)
    assert e["id"].startswith(f"{q1.subject}::{q1.topic}::")
    assert e["category"] == q1.subject and e["app"] == "quantum-quiz"
    assert e["label"] == q1.text and isinstance(e["timestamp"], float)
    assert win._current_question_flagged() is True
    fb = win._feedback_screen
    assert fb.is_flagged() and fb._flag_btn.text() == "⚑ Flagged — click to unflag"

    # A different question on the same subject/topic gets its own entry …
    q2 = _question("State the Bloch vector of |0>.")
    win._current_question = q2
    assert win._current_question_flagged() is False
    win._on_flag_toggled()
    ids = [x["id"] for x in json.loads(persistence._FLAGGED_FILE.read_text())]
    assert len(ids) == 2 and ids[0] != ids[1]

    # … and toggling the first again removes only the first.
    win._current_question = q1
    win._on_flag_toggled()
    assert [x["id"] for x in json.loads(persistence._FLAGGED_FILE.read_text())] == [ids[1]]
    assert not fb.is_flagged() and fb._flag_btn.text() == "⚑ Flag for review"

    # The feedback screen's own button drives the same path.
    fb._flag_btn.click()
    assert win._current_question_flagged() is True and fb.is_flagged()


def test_flag_write_failure_is_surfaced_not_swallowed(win, monkeypatch):
    import persistence

    warnings: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox, "warning",
        staticmethod(lambda parent, title, text, *a, **k: warnings.append((title, text))
                     or QMessageBox.StandardButton.Ok),
    )

    def boom(*_a, **_k):
        raise PermissionError("read-only data directory")

    monkeypatch.setattr(persistence, "toggle_flag", boom)
    win._current_question = _question()
    win._on_flag_toggled()
    assert len(warnings) == 1
    title, text = warnings[0]
    assert "flag" in title.lower()
    assert "quiz_flagged.json" in text and "read-only data directory" in text
    assert not win._feedback_screen.is_flagged()


def test_flag_toggle_without_a_question_is_a_noop(win, data_dir):
    import persistence

    win._current_question = None
    win._on_flag_toggled()
    assert not persistence._FLAGGED_FILE.exists()
    assert win._current_question_flagged() is False
