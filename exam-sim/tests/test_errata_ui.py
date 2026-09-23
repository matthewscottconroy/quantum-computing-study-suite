""""Report a problem with this item" — the in-app errata path, driven headless.

The URL builder and the dialog are shared (``common.errata`` /
``common.ui.errata_dialog``) and unit-tested in the root suite.  What is
tested here is exam-sim's side of it: what the report *says* about a bank
question, that the control is reachable by keyboard, that it opens the browser
exactly once and only when the learner accepts, that a machine with no browser
still gets the URL, and that the button is on the two screens where a question
is shown after it has been graded — and on neither the timed exam runner nor
anywhere it could leak an answer early.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QMessageBox

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from common.ui.errata_dialog import ErrataDialog
from core.models import Question
from ui.errata import BUTTON_TEXT, ReportButton, item_text_for

WHY = "Option B is also correct: Sampler V2 returns a BitArray too."


def _q(qid: str = "sa_int_counts", section: str = "Sampler",
       correct: int = 2) -> Question:
    return Question(id=qid, section=section, question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"],
                    correct_index=correct, explanation="because",
                    difficulty="easy")


def _field(url: str, name: str) -> str:
    """One query field of an issue URL, decoded."""
    return parse_qs(urlparse(url).query)[name][0]


def _was_opened(browser, url: str) -> bool:
    """QUrl.toString() decodes some escapes, so compare the normalised forms."""
    return browser.opened == [QUrl(url).toString()]


def _close(widget, qapp):
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


@pytest.fixture
def accepted(monkeypatch):
    """Make ``ErrataDialog.exec()`` fill in a description and accept."""
    def fake_exec(self):
        self._why.setPlainText(WHY)
        self._on_accept()
        return QDialog.DialogCode.Accepted
    monkeypatch.setattr(ErrataDialog, "exec", fake_exec)


@pytest.fixture
def cancelled(monkeypatch):
    monkeypatch.setattr(ErrataDialog, "exec",
                        lambda self: QDialog.DialogCode.Rejected)


@pytest.fixture
def browser(monkeypatch):
    """Stub QDesktopServices.openUrl; ``browser.ok`` decides whether it works."""
    class Stub:
        ok = True
        opened: list[str] = []

    stub = Stub()
    stub.opened = []

    def fake_open(url):
        stub.opened.append(url.toString())
        return stub.ok

    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(fake_open))
    return stub


# ── what the report says ─────────────────────────────────────────────────────

def test_item_text_quotes_the_question_as_the_learner_saw_it():
    text = item_text_for(_q(), chosen_index=1)
    assert text.startswith("Question sa_int_counts?")
    assert "A. opt-a" in text
    assert "B. opt-b   <- your answer" in text
    assert "C. opt-c   <- keyed correct" in text
    assert "Explanation shown: because" in text
    # with no answer picked (the results screen for an unanswered question)
    assert "your answer" not in item_text_for(_q())


def test_the_url_is_a_prefilled_content_error_issue():
    url = errata.issue_url("exam-sim", "sa_int_counts",
                           item_text_for(_q(), 1), WHY)
    parts = urlparse(url)
    assert parts.netloc == "github.com"
    assert parts.path.endswith("/issues/new")
    fields = {k: v[0] for k, v in parse_qs(parts.query).items()}
    assert fields["template"] == "content_error.yml"
    assert fields["title"] == "[content] exam-sim: sa_int_counts"
    assert "exam-sim/bank/" in fields["file"] and "sa_int_counts" in fields["file"]
    assert "opt-b   <- your answer" in fields["quote"]
    assert fields["why_wrong"] == WHY
    assert len(url) <= errata.MAX_URL


# ── the control ──────────────────────────────────────────────────────────────

def test_the_button_is_keyboard_reachable_and_named(qapp):
    btn = ReportButton()
    try:
        assert btn.text() == BUTTON_TEXT
        assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert btn.accessibleName() and btn.toolTip()
        btn.setFocus()
        assert btn.objectName() == "flat"      # the theme's focus-ring rule
    finally:
        _close(btn, qapp)


def test_accepting_the_dialog_opens_the_browser_once(qapp, accepted, browser):
    btn = ReportButton()
    seen: list[str] = []
    btn.reported.connect(seen.append)
    try:
        btn.set_question(_q(), chosen_index=1)
        url = btn.report()
        assert url and url.startswith("https://github.com/")
        assert seen == [url]
        assert _was_opened(browser, url)
        assert "sa_int_counts" in url
    finally:
        _close(btn, qapp)


def test_cancelling_reports_nothing_and_opens_nothing(qapp, cancelled, browser):
    btn = ReportButton()
    seen: list[str] = []
    btn.reported.connect(seen.append)
    try:
        btn.set_question(_q())
        assert btn.report() is None
        assert seen == [] and browser.opened == []
    finally:
        _close(btn, qapp)


def test_clicking_the_button_is_the_same_path(qapp, accepted, browser):
    btn = ReportButton()
    try:
        btn.set_question(_q())
        btn.click()
        assert len(browser.opened) == 1
    finally:
        _close(btn, qapp)


def test_no_browser_degrades_to_the_clipboard_without_blocking(qapp, accepted,
                                                               browser):
    browser.ok = False
    btn = ReportButton()
    try:
        btn.set_question(_q())
        url = btn.report()                     # returns; nothing blocks
        assert url and _was_opened(browser, url)
        clipboard = qapp.clipboard()
        assert clipboard is not None and clipboard.text() == url
        boxes = [w for w in qapp.topLevelWidgets() if isinstance(w, QMessageBox)]
        assert boxes, "no fallback was shown"
        box = boxes[-1]
        assert not box.isModal(), "the fallback must not block the drill"
        assert url in box.detailedText()
        box.close()
        qapp.processEvents()
    finally:
        _close(btn, qapp)


def test_the_dialog_will_not_file_an_empty_report(qapp):
    dialog = ErrataDialog(app="exam-sim", item_id="sa_int_counts",
                          item_text=item_text_for(_q()))
    try:
        assert dialog._open_btn.isEnabled() is False
        dialog._why.setPlainText("   ")
        assert dialog._open_btn.isEnabled() is False
        dialog._why.setPlainText(WHY)
        assert dialog._open_btn.isEnabled() is True
        assert _field(dialog.build_url(), "why_wrong") == WHY
    finally:
        _close(dialog, qapp)


# ── where it appears ─────────────────────────────────────────────────────────

def test_results_screen_offers_one_report_per_missed_question(qapp, data_dir,
                                                              accepted, browser):
    from core.models import ExamAttempt, ExamResult
    from ui.screens.results_screen import ResultsScreen

    miss, hit = _q("s2", correct=0), _q("s1", correct=1)
    result = ExamResult(mode="sprint", attempts=[
        ExamAttempt(miss, chosen_index=2), ExamAttempt(hit, chosen_index=1)])
    screen = ResultsScreen()
    try:
        screen.show_result(result)
        assert len(screen._report_btns) == 1            # only the miss
        btn = screen._report_btns[0]
        assert btn.isEnabled() and btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        url = btn.report()
        assert "s2" in url and _was_opened(browser, url)
        assert "opt-c   <- your answer" in _field(url, "quote")
    finally:
        _close(screen, qapp)


def test_review_screen_shows_the_report_only_after_the_answer_is_checked(
        qapp, data_dir, questions, accepted, browser):
    import persistence
    from ui.screens.review_screen import ReviewScreen

    q = questions[0]
    wrong = (q.correct_index + 1) % len(q.options)
    persistence.record_miss(q, wrong)

    screen = ReviewScreen()
    try:
        assert screen.start() is True
        assert not screen._report_btn.isVisibleTo(screen)
        screen._radio_btns[wrong].click()
        screen._submit_btn.click()
        assert screen._report_btn.isVisibleTo(screen)
        url = screen._report_btn.report()
        assert q.id in url
        assert q.options[wrong] in _field(url, "quote")
        # moving on hides it again until the next answer is checked
        screen._show_current()
        assert not screen._report_btn.isVisibleTo(screen)
    finally:
        _close(screen, qapp)


def test_the_timed_exam_runner_has_no_report_button(qapp, data_dir):
    """Nothing may open a dialog or a browser while the exam clock runs."""
    from ui.screens.exam_screen import ExamScreen

    screen = ExamScreen()
    try:
        screen.start_session([_q("a"), _q("b")], 10, "sprint")
        assert screen.findChildren(ReportButton) == []
    finally:
        screen.abort()
        _close(screen, qapp)
