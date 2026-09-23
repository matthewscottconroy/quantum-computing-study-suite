"""Errata: "report a problem with this item" on the feedback screen.

The repository is public and quantum-quiz's questions are generated, so a
wrong or ambiguous question has no route to a fix except this button.  It must
be keyboard reachable, must never block a session, and must still do something
useful on a machine with no browser.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox

import common_path  # noqa: F401  (puts the repo root on sys.path)
from common import errata
from common.ui import errata_dialog as ed

import persistence
from core.models import Evaluation, Question, QuizConfig
from core.session import QuizSession
from qiskit_contexts import EMPTY_CONTEXT

QUESTION_TEXT = "Which qubit is the most significant bit in Qiskit's ordering?"


def _question(text: str = QUESTION_TEXT, subject: str = "Qiskit") -> Question:
    return Question(subject=subject, topic="little-endian ordering",
                    difficulty="beginner", question_type="conceptual explanation",
                    text=text)


def _evaluation(score: int = 2) -> Evaluation:
    return Evaluation(score=score, verdict="Incorrect", feedback="See the model answer.",
                      model_answer="Qiskit is little-endian: qubit 0 is the rightmost bit.")


@pytest.fixture
def win(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    w = MainWindow()
    w._session = QuizSession(QuizConfig(
        subjects=["Qiskit"], difficulty="beginner",
        question_types=["conceptual explanation"], question_count=5,
    ))
    w.show()
    qapp.processEvents()
    yield w
    w.close()
    w.deleteLater()


def _ask_and_grade(win, question: Question | None = None, score: int = 2) -> Question:
    question = question or _question()
    win._current_question = question
    win._question_screen.load_question(question, EMPTY_CONTEXT, number=1, total=5)
    win._on_evaluation_ready("qubit 0 is the leftmost bit", _evaluation(score))
    return question


def _auto_accept(monkeypatch, why="Qubit 0 is the LEAST significant bit.",
                 fix="", severity=None):
    """Drive ErrataDialog headlessly: fill it in and accept it."""
    seen: list[ed.ErrataDialog] = []

    def fake_exec(self):
        seen.append(self)
        self._why.setPlainText(why)
        if fix:
            self._fix.setPlainText(fix)
        if severity:
            self._severity.setCurrentIndex(self._severity.findData(severity))
        self._on_accept()
        return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(ed.ErrataDialog, "exec", fake_exec)
    return seen


def _stub_browser(monkeypatch, ok: bool = True) -> list[str]:
    """Record what would be opened.  QUrl round-trips, so compare canonically."""
    opened: list[str] = []
    monkeypatch.setattr(
        QDesktopServices, "openUrl",
        staticmethod(lambda url: (opened.append(url.toString()), ok)[1]))
    return opened


def _same_url(recorded: str, returned: str) -> bool:
    return QUrl(recorded) == QUrl(returned)


# ── the control ───────────────────────────────────────────────────────────────

def test_the_button_is_on_the_feedback_screen_and_keyboard_reachable(win, qapp):
    fb = win._feedback_screen
    btn = fb._errata_btn
    assert "Report a problem" in btn.text()
    assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert btn.accessibleName() and btn.accessibleDescription()
    assert btn.toolTip()
    btn.setEnabled(True)
    btn.setFocus()
    qapp.processEvents()
    assert btn.hasFocus()


def test_the_button_is_armed_by_the_controller_and_disarmed_between_questions(win, qapp):
    fb = win._feedback_screen
    assert fb._errata_btn.isEnabled() is False        # nothing on screen yet

    q = _ask_and_grade(win)
    qapp.processEvents()
    assert fb._errata_btn.isEnabled() is True
    assert fb._errata_btn._item_id == persistence.mistake_item_id(q.subject, q.text)
    assert fb._errata_btn._item_text == q.text

    fb.load_evaluation(_evaluation(9))                # next question, not yet armed
    assert fb._errata_btn.isEnabled() is False
    assert fb.errata_status() == ""


# ── the issue URL ─────────────────────────────────────────────────────────────

def test_reporting_opens_a_prefilled_issue_for_this_question(win, qapp, monkeypatch):
    _auto_accept(monkeypatch, why="Qubit 0 is the LEAST significant bit.",
                 fix="Say: qubit 0 is the least significant bit.",
                 severity="wrong")
    opened = _stub_browser(monkeypatch)
    q = _ask_and_grade(win)
    qapp.processEvents()

    url = win._feedback_screen._errata_btn.report()
    assert url and len(opened) == 1 and _same_url(opened[0], url)

    parsed = urlparse(url)
    assert parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"
    fields = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    assert fields["template"] == "content_error.yml"          # lands in the form
    assert fields["title"].startswith("[content] quantum-quiz: ")
    assert persistence.mistake_item_id(q.subject, q.text) in fields["title"]
    assert "quantum-quiz" in fields["file"]
    assert fields["quote"] == q.text                          # the exact wording
    assert "LEAST significant" in fields["why_wrong"]
    assert "least significant bit" in fields["correction"]
    assert fields["severity"] == errata.SEVERITIES["wrong"]
    assert len(url) <= errata.MAX_URL
    assert win._feedback_screen.errata_status().startswith("✓")


def test_cancelling_the_dialog_reports_nothing(win, qapp, monkeypatch):
    monkeypatch.setattr(ed.ErrataDialog, "exec",
                        lambda self: int(QDialog.DialogCode.Rejected))
    opened = _stub_browser(monkeypatch)
    _ask_and_grade(win)
    assert win._feedback_screen._errata_btn.report() is None
    assert opened == []
    assert win._feedback_screen.errata_status() == ""


def test_the_dialog_names_the_item_and_needs_a_description(qapp):
    """The "Open the issue" button stays off until there is something to read."""
    dialog = ed.ErrataDialog(None, app=persistence.APP_ID,
                             item_id="abc123", item_text=QUESTION_TEXT)
    try:
        assert dialog._open_btn.isEnabled() is False
        labels = [w.text() for w in dialog.findChildren(QLabel)]
        assert any("abc123" in text for text in labels)      # the item is named
        assert any("quantum-quiz" in text for text in labels)

        dialog._why.setPlainText("Qubit 0 is the least significant bit.")
        qapp.processEvents()
        assert dialog._open_btn.isEnabled() is True

        url = dialog.build_url()
        assert "abc123" in url and url.startswith("https://github.com/")
        dialog._why.setPlainText("   ")
        qapp.processEvents()
        assert dialog._open_btn.isEnabled() is False
    finally:
        dialog.deleteLater()


# ── degradation ───────────────────────────────────────────────────────────────

def test_no_browser_puts_the_link_on_the_clipboard_and_says_so(win, qapp, monkeypatch):
    _auto_accept(monkeypatch)
    opened = _stub_browser(monkeypatch, ok=False)     # openUrl fails
    dialogs: list = []
    for name in ("warning", "question", "information", "critical"):
        monkeypatch.setattr(QMessageBox, name,
                            staticmethod(lambda *a, **k: dialogs.append(a)
                                         or QMessageBox.StandardButton.Ok))
    _ask_and_grade(win)
    url = win._feedback_screen._errata_btn.report()

    assert url and len(opened) == 1 and _same_url(opened[0], url)   # tried, failed
    assert dialogs == []                              # never a modal error box
    status = win._feedback_screen.errata_status()
    assert status.startswith("✓") and "clipboard" in status
    from PyQt6.QtGui import QGuiApplication
    assert QGuiApplication.clipboard().text() == url
    assert win._feedback_screen._errata_status.toolTip() == url


def test_a_broken_browser_integration_never_reaches_the_session(win, qapp, monkeypatch):
    _auto_accept(monkeypatch)

    def boom(_url):
        raise RuntimeError("no desktop portal")

    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(boom))
    _ask_and_grade(win)
    url = win._feedback_screen._errata_btn.report()   # must not raise
    assert url
    assert "No browser" in win._feedback_screen.errata_status()
    # the session is untouched: the feedback screen is still the current page
    from ui.main_window import PAGE_FEEDBACK
    assert win._stack.currentIndex() == PAGE_FEEDBACK


def test_a_very_long_question_still_produces_a_usable_url(win, qapp, monkeypatch):
    _auto_accept(monkeypatch, why="x" * 9000)
    _stub_browser(monkeypatch)
    _ask_and_grade(win, _question("Q " + "y" * 9000))
    url = win._feedback_screen._errata_btn.report()
    assert url and len(url) <= errata.MAX_URL
    fields = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    assert fields["template"] == "content_error.yml"          # never trimmed
    assert fields["title"].startswith("[content] quantum-quiz: ")


def test_reporting_needs_no_api_key_and_no_network(win, qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    _auto_accept(monkeypatch)
    _stub_browser(monkeypatch)
    _ask_and_grade(win)
    # errata.issue_url is pure: proving it here means the button cannot stall
    assert errata.issue_url("quantum-quiz", "abc", "q", "wrong").startswith("https://")
    assert win._feedback_screen._errata_btn.report()
