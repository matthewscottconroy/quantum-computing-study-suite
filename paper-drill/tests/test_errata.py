""""Report a problem with this item" on the feedback screen.

The repository is public now.  A generated question that is wrong, ambiguous or
unanswerable from the paper had no path from "this is wrong" to a fix except
remembering it later, and nobody remembers it later.  One control on the
feedback screen — where the question, the grade and the model answer are all on
screen — turns that into a prefilled GitHub issue.

Four properties, all driven headlessly with the browser call stubbed:

* the URL is prefilled with the item id, the question text and the comment,
  in the fields ``.github/ISSUE_TEMPLATE/content_error.yml`` declares;
* the control is keyboard reachable and named for a screen reader;
* nothing blocks the drill — Next Question stays live, no network call is
  made, and the report is never a precondition for anything;
* with no browser (``QDesktopServices.openUrl`` returns False) the URL is shown
  instead of being lost.
"""
from __future__ import annotations

import time
from urllib.parse import parse_qs, urlsplit

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QMessageBox, QPushButton

import persistence
from common import errata
from core.models import Evaluation, Question, QuestionAttempt, Verdict

TITLE = "Surface Code Paper"
QUESTIONS = [
    Question(1, "QUESTION-1: what is the code distance of the patch?", "factual"),
    Question(2, "QUESTION-2: why does the threshold theorem matter here?", "conceptual"),
]
ERRATA_TEXT = "⚑ Report a problem with this item"


# ---------------------------------------------------------------------------
# Helpers (mirrors tests/test_screens.py so the files stay independent)
# ---------------------------------------------------------------------------

def _button(widget, text: str) -> QPushButton:
    for btn in widget.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    have = [b.text() for b in widget.findChildren(QPushButton)]
    raise AssertionError(f"no button {text!r}; have {have}")


def _pump(qapp, predicate, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        time.sleep(0.005)
    qapp.processEvents()
    return bool(predicate())


def _pages():
    from ui import main_window as mw
    return mw


@pytest.fixture
def fake_ai(monkeypatch):
    import ai.generator
    import ai.grader

    state = {"questions": list(QUESTIONS), "scores": []}

    def generate(paper_text, count):
        return list(state["questions"])

    def grade(paper_text, question, answer):
        score = state["scores"].pop(0) if state["scores"] else 8
        verdict = (Verdict.CORRECT if score >= 7 else
                   Verdict.PARTIAL if score >= 4 else Verdict.INCORRECT)
        return Evaluation(score=score, verdict=verdict,
                          feedback=f"graded:{question}", model_answer="distance 5")

    monkeypatch.setattr(ai.generator, "generate_questions", generate)
    monkeypatch.setattr(ai.grader, "grade_answer", grade)
    return state


@pytest.fixture
def window(qapp, data_dir, no_api_key):
    from ui.main_window import MainWindow

    win = MainWindow()
    win.show()
    qapp.processEvents()
    yield win
    for name in ("_gen_worker", "_grade_worker"):
        worker = getattr(win, name, None)
        if worker is not None:
            worker.wait(3000)
    win.close()
    win.deleteLater()
    qapp.processEvents()


@pytest.fixture
def opened(monkeypatch):
    """Record every URL handed to the browser instead of launching one."""
    urls: list[str] = []

    def fake_open(url):
        urls.append(url.toString())
        return True

    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(fake_open))
    return urls


@pytest.fixture
def no_browser(monkeypatch):
    """A machine with no browser: openUrl reports failure."""
    monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(lambda url: False))


def _fill_and_accept(monkeypatch, why: str, fix: str = "", severity: str = "wrong"):
    """Drive the modal dialog without showing it: fill it in, accept it."""
    from common.ui import errata_dialog

    original = errata_dialog.ErrataDialog

    def driven(*args, **kwargs):
        dialog = original(*args, **kwargs)
        dialog._why.setPlainText(why)
        dialog._fix.setPlainText(fix)
        index = dialog._severity.findData(severity)
        if index >= 0:
            dialog._severity.setCurrentIndex(index)
        # exec() would spin a nested event loop; accept straight away instead.
        dialog.exec = lambda: (dialog._on_accept(), QDialog.DialogCode.Accepted)[1]
        driven.last = dialog
        return dialog

    driven.last = None
    monkeypatch.setattr(errata_dialog, "ErrataDialog", driven)
    return driven


def _cancel_the_dialog(monkeypatch):
    from common.ui import errata_dialog

    original = errata_dialog.ErrataDialog

    def driven(*args, **kwargs):
        dialog = original(*args, **kwargs)
        dialog.exec = lambda: QDialog.DialogCode.Rejected
        return dialog

    monkeypatch.setattr(errata_dialog, "ErrataDialog", driven)


def _submit(qapp, win, text: str) -> None:
    mw = _pages()
    q = win._question
    q._answer_edit.setPlainText(text)
    qapp.processEvents()
    _button(q, "Submit Answer").click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_FEEDBACK)


def _start_session(qapp, win, title: str = TITLE):
    mw = _pages()
    inp = win._input
    inp._title_edit.setText(title)
    inp._text_edit.setPlainText("We present a distance-5 surface code patch.")
    inp._count_spin.setValue(len(QUESTIONS))
    inp._save_chk.setChecked(False)
    qapp.processEvents()
    _button(inp, "Generate Questions").click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_QUESTION)
    return win._question


# ---------------------------------------------------------------------------
# The control itself
# ---------------------------------------------------------------------------

class TestErrataControl:
    def test_it_is_on_the_feedback_screen_and_keyboard_reachable(self, qapp):
        from ui.screens.feedback_screen import FeedbackScreen

        fb = FeedbackScreen()
        btn = _button(fb, ERRATA_TEXT)
        assert btn.focusPolicy() in (Qt.FocusPolicy.StrongFocus,
                                     Qt.FocusPolicy.WheelFocus)
        assert btn.accessibleName() == "Report a problem with this question"
        assert btn.accessibleDescription().strip()
        assert btn.toolTip().strip()
        assert btn.isEnabled()
        # The shared base sheet this app installs draws a visible ring on any
        # focused button, so the control is findable without a mouse.
        from ui import theme
        assert "QPushButton:focus" in theme.QSS_APP
        fb.deleteLater()

    def test_show_attempt_points_it_at_the_question_on_screen(self, qapp):
        from ui.screens.feedback_screen import FeedbackScreen

        fb = FeedbackScreen()
        attempt = QuestionAttempt(
            question=QUESTIONS[0], answer_text="three",
            evaluation=Evaluation(score=2, verdict=Verdict.INCORRECT,
                                  feedback="no", model_answer="five"))
        fb.show_attempt(attempt, is_last=False)
        assert fb._errata_btn._item_text == QUESTIONS[0].text
        fb.set_errata_item("paper-abc", QUESTIONS[0].text)
        assert fb._errata_btn._item_id == "paper-abc"
        fb.deleteLater()


# ---------------------------------------------------------------------------
# The URL
# ---------------------------------------------------------------------------

class TestReportedUrl:
    def test_it_is_prefilled_with_the_item_the_learner_was_looking_at(
            self, qapp, window, fake_ai, opened, monkeypatch):
        _fill_and_accept(monkeypatch, "The paper never states the distance.",
                         fix="Ask about the stabiliser weight instead.")
        fake_ai["scores"] = [2]
        _start_session(qapp, window)
        _submit(qapp, window, "three")

        seen: list[str] = []
        window._feedback.errata_reported.connect(seen.append)
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()

        # ``seen`` is the URL as built; ``opened`` is what QUrl handed the
        # browser (same URL, some characters re-encoded on the round trip).
        assert len(seen) == 1 and len(opened) == 1
        assert window._last_errata_url == seen[0]

        parts = urlsplit(seen[0])
        assert parts.scheme == "https" and parts.netloc == "github.com"
        assert parts.path == f"/{errata.REPO}/issues/new"
        q = {k: v[0] for k, v in parse_qs(parts.query).items()}
        assert q["template"] == "content_error.yml"
        item_id = persistence.make_flag_id(TITLE, QUESTIONS[0].text)
        assert q["title"] == f"[content] paper-drill: {item_id}"
        assert item_id in q["file"] and "paper-drill" in q["file"]
        assert q["quote"] == QUESTIONS[0].text
        assert q["why_wrong"] == "The paper never states the distance."
        assert q["correction"] == "Ask about the stabiliser weight instead."
        assert q["severity"] == errata.SEVERITIES["wrong"]

    def test_the_id_is_the_same_one_the_flag_and_the_journal_use(
            self, qapp, window, fake_ai, opened, monkeypatch):
        """A report a maintainer cannot match to a logged mistake is half a
        report, so the errata id is the flag id is the journal id."""
        _fill_and_accept(monkeypatch, "ambiguous")
        fake_ai["scores"] = [1]
        _start_session(qapp, window)
        _submit(qapp, window, "no idea")
        window._feedback._flag_btn.click()
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()

        q = {k: v[0] for k, v in parse_qs(urlsplit(opened[0]).query).items()}
        item_id = persistence.make_flag_id(TITLE, QUESTIONS[0].text)
        flagged = persistence.load_flagged()
        logged = persistence.load_mistakes()
        assert [e["id"] for e in flagged] == [item_id]
        assert [e["id"] for e in logged] == [item_id]
        assert item_id in q["file"]

    def test_severity_comes_from_the_dropdown(self, qapp, window, fake_ai,
                                              opened, monkeypatch):
        _fill_and_accept(monkeypatch, "a stray comma", severity="typo")
        _start_session(qapp, window)
        _submit(qapp, window, "an answer")
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()
        q = {k: v[0] for k, v in parse_qs(urlsplit(opened[0]).query).items()}
        assert q["severity"] == errata.SEVERITIES["typo"]

    def test_cancelling_reports_nothing(self, qapp, window, fake_ai, opened,
                                        monkeypatch):
        _cancel_the_dialog(monkeypatch)
        seen: list[str] = []
        _start_session(qapp, window)
        _submit(qapp, window, "an answer")
        window._feedback.errata_reported.connect(seen.append)
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()
        assert opened == [] and seen == []
        assert window._last_errata_url is None


# ---------------------------------------------------------------------------
# It must not get in the way
# ---------------------------------------------------------------------------

class TestItNeverBlocks:
    def test_the_drill_carries_on_around_it(self, qapp, window, fake_ai,
                                            opened, monkeypatch):
        mw = _pages()
        _fill_and_accept(monkeypatch, "wrong units")
        fake_ai["scores"] = [2, 9]
        _start_session(qapp, window)
        _submit(qapp, window, "three")
        fb = window._feedback

        _button(fb, ERRATA_TEXT).click()
        qapp.processEvents()
        assert len(opened) == 1

        # Everything else on the screen is still live and unchanged.
        assert fb.mistake_prompt_visible()
        assert fb._score_lbl.text() == "2/10"
        _button(fb, "Next Question").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_QUESTION
        _submit(qapp, window, "because errors are suppressed")
        assert fb._score_lbl.text() == "9/10"

    def test_it_writes_nothing_to_the_data_directory(self, qapp, window, fake_ai,
                                                     data_dir, opened, monkeypatch):
        _fill_and_accept(monkeypatch, "wrong")
        _start_session(qapp, window)
        _submit(qapp, window, "an answer")
        before = sorted(p.name for p in data_dir.iterdir()) if data_dir.exists() else []
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()
        after = sorted(p.name for p in data_dir.iterdir()) if data_dir.exists() else []
        assert after == before

    def test_an_exploding_browser_does_not_reach_the_drill(
            self, qapp, window, fake_ai, monkeypatch):
        """openUrl is a platform call; if it throws, the drill still stands."""
        def boom(url):
            raise RuntimeError("no display")

        monkeypatch.setattr(QDesktopServices, "openUrl", staticmethod(boom))
        shown: list[QMessageBox] = []
        monkeypatch.setattr(QMessageBox, "show", lambda self: shown.append(self))
        _fill_and_accept(monkeypatch, "wrong")
        _start_session(qapp, window)
        _submit(qapp, window, "an answer")
        _button(window._feedback, ERRATA_TEXT).click()      # must not raise
        qapp.processEvents()
        assert len(shown) == 1


# ---------------------------------------------------------------------------
# Degrading with no browser
# ---------------------------------------------------------------------------

class TestNoBrowser:
    def test_the_url_is_shown_instead_of_lost(self, qapp, window, fake_ai,
                                              no_browser, monkeypatch):
        shown: list[QMessageBox] = []
        monkeypatch.setattr(QMessageBox, "show", lambda self: shown.append(self))
        _fill_and_accept(monkeypatch, "the model answer contradicts the paper")
        _start_session(qapp, window)
        _submit(qapp, window, "an answer")

        seen: list[str] = []
        window._feedback.errata_reported.connect(seen.append)
        _button(window._feedback, ERRATA_TEXT).click()
        qapp.processEvents()

        assert len(seen) == 1                       # the report still happened
        assert len(shown) == 1
        box = shown[0]
        assert seen[0] in box.informativeText()     # copyable, not lost
        assert box.textInteractionFlags() & Qt.TextInteractionFlag.TextSelectableByMouse
        assert not box.isModal()                    # never blocks the drill


# ---------------------------------------------------------------------------
# The dialog (from common.ui.errata_dialog, driven through this app's button)
# ---------------------------------------------------------------------------

class TestDialog:
    def test_it_refuses_an_empty_report_and_accepts_a_filled_one(self, qapp):
        from common.ui.errata_dialog import ErrataDialog

        dialog = ErrataDialog(app="paper-drill", item_id="paper-1",
                              item_text=QUESTIONS[0].text)
        assert not dialog._open_btn.isEnabled()     # nothing to read yet
        dialog._why.setPlainText("the distance is 3, not 5")
        qapp.processEvents()
        assert dialog._open_btn.isEnabled()

        url = dialog.build_url()
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        assert q["why_wrong"] == "the distance is 3, not 5"
        assert q["quote"] == QUESTIONS[0].text
        assert dialog.issue_url is None             # not until it is accepted
        dialog._on_accept()
        assert dialog.issue_url == url
        dialog.deleteLater()

    def test_a_very_long_question_is_truncated_not_dropped(self, qapp):
        from common.ui.errata_dialog import ErrataDialog

        dialog = ErrataDialog(app="paper-drill", item_id="paper-1",
                              item_text="q" * 40_000)
        dialog._why.setPlainText("w" * 40_000)
        url = dialog.build_url()
        assert len(url) <= errata.MAX_URL
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        assert q["title"].startswith("[content] paper-drill:")   # never trimmed
        assert "paper-drill" in q["file"]
        dialog.deleteLater()
