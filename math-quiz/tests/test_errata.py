"""\"Report a problem with this item\": the control on the feedback screen, the
URL it builds, and what happens on a machine with no browser.

Nothing here touches the network — ``common.errata`` only builds a URL string
and ``QDesktopServices`` is stubbed throughout.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QApplication, QDialog

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui import errata_dialog as ed

import ui.screens.feedback_screen as fs
from core.models import Evaluation, Question, QuizConfig


def _question(text="State the spectral theorem for Hermitian operators.",
              subject="Linear Algebra", topic="spectral theorem") -> Question:
    return Question(subject=subject, topic=topic, difficulty="beginner",
                    question_type="conceptual", text=text, hints=["h1"])


def _evaluation(score: int) -> Evaluation:
    return Evaluation(score=score, verdict="Incorrect" if score < 4 else "Correct",
                      feedback="feedback text", model_answer="the model answer")


@pytest.fixture
def accepting_dialog(monkeypatch):
    """Drive the modal dialog headlessly: type a reason and accept it."""
    typed = {"why": "The spectral theorem needs the operator to be normal.",
             "fix": "Say 'normal', not 'Hermitian'.", "severity": None}

    def fake_exec(self):
        self._why.setPlainText(typed["why"])
        self._fix.setPlainText(typed["fix"])
        if typed["severity"] is not None:
            self._severity.setCurrentIndex(
                self._severity.findData(typed["severity"]))
        self._on_accept()
        return QDialog.DialogCode.Accepted

    monkeypatch.setattr(ed.ErrataDialog, "exec", fake_exec)
    return typed


@pytest.fixture
def browser(monkeypatch):
    """Stub QDesktopServices.openUrl; ``browser["ok"]`` decides the outcome."""
    state = {"ok": True, "urls": []}

    def fake_open(url):
        state["urls"].append(url.toString())
        return state["ok"]

    monkeypatch.setattr(fs.QDesktopServices, "openUrl", fake_open)
    return state


# ── The control itself ────────────────────────────────────────────────────────

def test_errata_button_is_present_labelled_and_keyboard_reachable(qapp):
    fb = fs.FeedbackScreen()
    btn = fb._errata_btn
    assert "Report a problem" in btn.text()
    assert btn.accessibleName()
    assert btn.toolTip()
    assert btn.focusPolicy() & Qt.FocusPolicy.TabFocus      # Tab reaches it
    assert btn.isEnabled()
    # It is always available — a wrong answer is not a precondition for
    # noticing that the question itself is broken.
    fb.load_evaluation(_evaluation(10))
    assert btn.isEnabled() and not btn.isHidden()
    fb.deleteLater()


def test_set_item_points_the_report_at_the_question_on_screen(qapp):
    fb = fs.FeedbackScreen()
    assert fb.errata_item() == ("", "")
    fb.set_item("abc123", "What is the trace of a projector?")
    assert fb.errata_item() == ("abc123", "What is the trace of a projector?")
    fb.set_item(None, None)                                # never raises
    assert fb.errata_item() == ("", "")
    fb.deleteLater()


def test_reporting_builds_a_prefilled_issue_url_and_opens_it(
        qapp, accepting_dialog, browser):
    fb = fs.FeedbackScreen()
    fb.set_item("abc123", "State the spectral theorem for Hermitian operators.")
    seen: list[tuple[str, bool]] = []
    fb.errata_reported.connect(lambda url, ok: seen.append((url, ok)))

    fb._errata_btn.click()

    assert len(seen) == 1
    url, opened = seen[0]
    assert opened is True
    # QUrl.toString() pretty-decodes %20 etc., so compare through QUrl.
    assert browser["urls"] == [QUrl(url).toString()]

    parsed = urlparse(url)
    assert parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"
    q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    assert q["template"] == "content_error.yml"
    assert q["title"] == "[content] math-quiz: abc123"
    assert "abc123" in q["file"] and "math-quiz" in q["file"]
    assert q["quote"] == "State the spectral theorem for Hermitian operators."
    assert q["why_wrong"] == accepting_dialog["why"]
    assert q["correction"] == accepting_dialog["fix"]
    assert q["severity"] == errata.SEVERITIES["wrong"]
    fb.deleteLater()


def test_cancelling_the_dialog_reports_nothing(qapp, browser, monkeypatch):
    monkeypatch.setattr(ed.ErrataDialog, "exec",
                        lambda self: QDialog.DialogCode.Rejected)
    fb = fs.FeedbackScreen()
    fb.set_item("abc123", "text")
    seen = []
    fb.errata_reported.connect(lambda url, ok: seen.append(url))
    fb._errata_btn.click()
    assert seen == [] and browser["urls"] == []
    fb.deleteLater()


def test_a_report_with_no_description_cannot_be_submitted(qapp):
    """The dialog's accept button stays off until there is something to read."""
    dlg = ed.ErrataDialog(app="math-quiz", item_id="abc123", item_text="q")
    try:
        assert dlg._open_btn.isEnabled() is False
        dlg._why.setPlainText("   ")
        assert dlg._open_btn.isEnabled() is False
        dlg._why.setPlainText("The stated eigenvalue is wrong.")
        assert dlg._open_btn.isEnabled() is True
        query = parse_qs(urlparse(dlg.build_url()).query)
        assert query["why_wrong"] == ["The stated eigenvalue is wrong."]
        assert query["quote"] == ["q"]
    finally:
        dlg.deleteLater()


# ── Degrading with no browser ─────────────────────────────────────────────────

def test_with_no_browser_the_url_goes_to_the_clipboard_and_says_so(
        qapp, accepting_dialog, browser):
    browser["ok"] = False
    fb = fs.FeedbackScreen()
    fb.set_item("abc123", "text")
    seen: list[tuple[str, bool]] = []
    fb.errata_reported.connect(lambda url, ok: seen.append((url, ok)))

    fb._errata_btn.click()

    assert len(seen) == 1
    url, opened = seen[0]
    assert opened is False
    clipboard = QApplication.clipboard()
    assert clipboard is not None and clipboard.text() == url
    fb.deleteLater()


def test_an_exploding_openurl_is_reported_not_raised(qapp, accepting_dialog,
                                                     monkeypatch):
    def boom(_url):
        raise RuntimeError("no desktop services here")

    monkeypatch.setattr(fs.QDesktopServices, "openUrl", boom)
    fb = fs.FeedbackScreen()
    fb.set_item("abc123", "text")
    seen = []
    fb.errata_reported.connect(lambda url, ok: seen.append(ok))
    fb._errata_btn.click()                                 # must not raise
    assert seen == [False]
    fb.deleteLater()


def test_reporting_never_blocks_the_drill(qapp, accepting_dialog, browser):
    """Nothing about the report gates moving on to the next question."""
    fb = fs.FeedbackScreen()
    fb.load_evaluation(_evaluation(2))
    fb.set_item("abc123", "text")
    advanced = []
    fb.next_question_requested.connect(lambda: advanced.append(True))
    fb._errata_btn.click()
    assert fb.isEnabled() and fb._errata_btn.isEnabled()
    fb.next_question_requested.emit()
    assert advanced == [True]
    fb.deleteLater()


# ── Wired into the window ─────────────────────────────────────────────────────

def test_the_window_points_the_report_at_the_graded_question_and_confirms_it(
        qapp, monkeypatch, accepting_dialog, browser):
    """Headless drive: answer a question, then report it from the feedback screen."""
    from PyQt6.QtCore import QObject, pyqtSignal

    import persistence
    import ui.main_window as mw

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    q = _question()

    class FakeQuestionWorker(QObject):
        question_ready = pyqtSignal(object)
        error = pyqtSignal(str)

        def __init__(self, session, parent=None):
            super().__init__(parent)
            self._session = session

        def start(self):
            self._session.record_generated(q)
            self.question_ready.emit(q)

    class FakeEvaluationWorker(QObject):
        evaluation_ready = pyqtSignal(object)
        error = pyqtSignal(str)

        def __init__(self, question, answer, parent=None):
            super().__init__(parent)

        def start(self):
            self.evaluation_ready.emit(_evaluation(2))

    monkeypatch.setattr(mw, "QuestionWorker", FakeQuestionWorker)
    monkeypatch.setattr(mw, "EvaluationWorker", FakeEvaluationWorker)

    win = mw.MainWindow()
    try:
        win._on_quiz_started(QuizConfig(subjects=["Linear Algebra"],
                                        difficulty="beginner",
                                        question_types=["conceptual"],
                                        question_count=1))
        qapp.processEvents()
        win._question._answer_edit.setPlainText("an answer")
        win._question._submit_btn.click()
        qapp.processEvents()

        assert win._stack.currentIndex() == mw.PAGE_FEEDBACK
        assert win._feedback.errata_item() == (persistence.mistake_id_for(q), q.text)

        win._feedback._errata_btn.click()
        qapp.processEvents()
        assert len(browser["urls"]) == 1
        assert persistence.mistake_id_for(q) in browser["urls"][0]
        assert "browser" in win.statusBar().currentMessage()

        # No browser: the message changes, the report is not lost.
        browser["ok"] = False
        win._feedback._errata_btn.click()
        qapp.processEvents()
        assert "clipboard" in win.statusBar().currentMessage()
    finally:
        win.close()
        win.deleteLater()
