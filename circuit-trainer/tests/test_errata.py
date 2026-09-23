"""Errata reporting: "⚠ Report a problem with this item" on the result view.

The repository is public, so a wrong problem needs a path from "this is wrong"
to a fix.  The control is a ``common.ui.errata_dialog.ErrataButton``; these
tests drive it headlessly with the browser stubbed out, because nothing here
may ever open a real browser or touch the network.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QDialog

import persistence
from core.models import AnswerFormat, Attempt, Problem, ProblemCategory


def _problem(text="Apply H to |0⟩. What is the output state?",
             cat=ProblemCategory.SINGLE_GATE_OUTPUT,
             fmt=AnswerFormat.MULTIPLE_CHOICE, correct="1") -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text=text,
        answer_format=fmt, correct_answer=correct,
        choices=None if fmt is AnswerFormat.FREE_FORM else ["|0⟩", "|+⟩", "|1⟩", "|−⟩"],
        circuit_png=None, aux_circuit_png=None, matrix_str=None,
        state_str="|ψ⟩ = |0⟩", solution_steps=["H|0⟩ = |+⟩"],
        key_concepts=["Hadamard"],
    )


class _Opened:
    """Stands in for QDesktopServices: records, never opens.

    ``QUrl.toString()`` re-encodes, so the recorded string is not character for
    character the one the app built -- that one arrives on the ``reported``
    signal.  This records the fully-encoded form, which is what a browser would
    actually be handed.
    """

    def __init__(self, succeed: bool = True) -> None:
        self.urls: list[str] = []
        self._succeed = succeed

    def openUrl(self, url) -> bool:                      # noqa: N802 (Qt name)
        self.urls.append(url.toString(QUrl.ComponentFormattingOption.FullyEncoded))
        return self._succeed


@pytest.fixture
def opened(monkeypatch):
    """Stub the browser hand-off inside common.ui.errata_dialog."""
    from common.ui import errata_dialog

    stub = _Opened()
    monkeypatch.setattr(errata_dialog, "QDesktopServices", stub)
    return stub


@pytest.fixture
def screen(qapp):
    from ui.screens.problem_screen import ProblemScreen

    s = ProblemScreen()
    yield s
    s._tick_timer.stop()
    s.deleteLater()


def _accept_with(comment: str, fix: str = "", severity: str | None = None):
    """A stand-in ``ErrataDialog.exec`` that types *comment* and accepts."""
    def fake_exec(self) -> QDialog.DialogCode:
        self._why.setPlainText(comment)
        if fix:
            self._fix.setPlainText(fix)
        if severity is not None:
            self._severity.setCurrentIndex(self._severity.findData(severity))
        self._on_accept()
        return QDialog.DialogCode.Accepted
    return fake_exec


def _show(screen, problem, *, correct=True):
    screen.load_problem(problem, number=1, total=4)
    screen.show_result(Attempt(problem, problem.correct_answer, correct,
                               10 if correct else 0, "fb"))


# ── The control itself ────────────────────────────────────────────────────────

def test_the_control_appears_only_once_an_item_is_on_screen(screen):
    p = _problem()
    screen.load_problem(p, number=1, total=4)
    assert screen._errata_btn.isHidden(), "nothing to report before the answer"
    screen.show_result(Attempt(p, "1", True, 10, "fb"))
    assert not screen._errata_btn.isHidden()
    assert screen._errata_btn.text() == "⚠ Report a problem with this item"

    # ...and it is put away again with the next problem.
    screen.load_problem(_problem("another"), number=2, total=4)
    assert screen._errata_btn.isHidden()
    assert screen._errata_status.isHidden()


def test_the_control_is_keyboard_reachable_and_named(screen):
    p = _problem()
    _show(screen, p)
    btn = screen._errata_btn
    assert btn.focusPolicy().value & Qt.FocusPolicy.TabFocus.value
    assert btn.accessibleName() == "Report a problem with this item"
    assert btn.accessibleDescription()
    assert btn.toolTip()
    btn.setFocus()
    # Space/Enter on a focused QPushButton is Qt's own activation path; the
    # click signal is what both are wired to.
    assert btn.isEnabled()


def test_it_is_a_separate_control_from_flag_for_review(screen):
    """Flagging is "come back to this"; errata is "this is wrong for everyone"."""
    p = _problem()
    _show(screen, p)
    assert screen._errata_btn is not screen._flag_btn
    assert not screen._flag_btn.isHidden() and not screen._errata_btn.isHidden()


# ── What the report carries ───────────────────────────────────────────────────

def test_reporting_opens_a_prefilled_github_issue(screen, opened, monkeypatch):
    from common import errata
    from common.ui import errata_dialog

    p = _problem()
    _show(screen, p, correct=False)
    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        _accept_with("Both |+⟩ and |−⟩ are defensible here.",
                                     fix="Key |+⟩ only.", severity="misleading"))
    seen: list[str] = []
    screen.errata_reported.connect(seen.append)

    screen._errata_btn.click()

    assert len(opened.urls) == 1, "exactly one browser hand-off"
    assert len(seen) == 1
    url = seen[0]                       # the URL as the app built it
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"

    q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    assert q["template"] == "content_error.yml"
    assert q["title"] == f"[content] circuit-trainer: {persistence.flag_id_for(p)}"
    assert q["severity"] == errata.SEVERITIES["misleading"]
    assert "circuit-trainer/problems/" in q["file"]
    assert persistence.flag_id_for(p) in q["file"]
    assert "Apply H to |0⟩" in q["quote"]
    assert "Both |+⟩ and |−⟩" in q["why_wrong"]
    assert q["correction"] == "Key |+⟩ only."


def test_the_quote_carries_what_the_learner_actually_saw(screen):
    from ui.screens.problem_screen import errata_text

    p = _problem()
    text = errata_text(p)
    assert "Apply H to |0⟩" in text
    assert "State: |ψ⟩ = |0⟩" in text
    for i, choice in enumerate(p.choices):
        assert f"{chr(65 + i)}. {choice}" in text
    assert "Keyed answer: B" in text             # correct_answer "1" -> B


def test_a_free_form_item_reports_without_choices(screen):
    from ui.screens.problem_screen import errata_text

    p = _problem("Explain this circuit.", ProblemCategory.CIRCUIT_EXPLANATION,
                 AnswerFormat.FREE_FORM, correct="")
    text = errata_text(p)
    assert "Explain this circuit." in text and "Choices:" not in text


def test_the_url_stays_inside_the_length_cap(screen, opened, monkeypatch):
    from common import errata
    from common.ui import errata_dialog

    p = _problem("Consider the following circuit. " + ("blah " * 4000))
    _show(screen, p, correct=False)
    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        _accept_with("wrong " * 3000))
    screen._errata_btn.click()
    assert len(opened.urls[0]) <= errata.MAX_URL
    assert persistence.flag_id_for(p) in opened.urls[0]   # the short fields survive


def test_the_preview_is_pure_and_opens_nothing(screen, opened):
    p = _problem()
    _show(screen, p)
    url = screen.errata_url_preview()
    assert url.startswith("https://github.com/") and opened.urls == []


# ── Cancelling, and no browser ────────────────────────────────────────────────

def test_cancelling_the_dialog_reports_nothing(screen, opened, monkeypatch):
    from common.ui import errata_dialog

    _show(screen, _problem())
    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        lambda self: QDialog.DialogCode.Rejected)
    seen: list[str] = []
    screen.errata_reported.connect(seen.append)

    screen._errata_btn.click()
    assert opened.urls == [] and seen == []
    assert screen._errata_status.isHidden()


def test_with_no_browser_the_link_is_still_recoverable(screen, monkeypatch):
    """QDesktopServices is fire-and-forget; the report must not vanish with it."""
    from common.ui import errata_dialog

    stub = _Opened(succeed=False)
    monkeypatch.setattr(errata_dialog, "QDesktopServices", stub)
    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        _accept_with("The keyed answer is wrong."))
    _show(screen, _problem(), correct=False)
    seen: list[str] = []
    screen.errata_reported.connect(seen.append)
    screen._errata_btn.click()

    assert stub.urls, "the URL was still handed to QDesktopServices"
    assert not screen._errata_status.isHidden()
    url = seen[0]
    assert screen._errata_status.toolTip() == url
    # Selectable, so it can be read off the screen even with nothing on the
    # clipboard and nothing registered for https.
    assert (screen._errata_status.textInteractionFlags()
            & Qt.TextInteractionFlag.TextSelectableByMouse)
    text = screen._errata_status.text()
    assert "clipboard" in text or url in text


def test_an_unusable_clipboard_does_not_break_the_report(screen, opened, monkeypatch):
    from common.ui import errata_dialog
    from ui.screens import problem_screen

    class _NoClipboard:
        @staticmethod
        def clipboard():
            raise RuntimeError("no clipboard on this display")

    monkeypatch.setattr(problem_screen, "QGuiApplication", _NoClipboard)
    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        _accept_with("Wrong probability."))
    _show(screen, _problem(), correct=False)
    seen: list[str] = []
    screen.errata_reported.connect(seen.append)
    screen._errata_btn.click()                       # must not raise
    assert opened.urls and not screen._errata_status.isHidden()
    # No clipboard, so the status line has to carry the link itself.
    assert seen[0] in screen._errata_status.text()


# ── The dialog ────────────────────────────────────────────────────────────────

def test_the_dialog_will_not_submit_an_empty_report(qapp):
    from common.ui.errata_dialog import ErrataDialog

    dialog = ErrataDialog(app="circuit-trainer", item_id="gs:H-X-H:0",
                          item_text="Apply H then X then H.")
    try:
        assert not dialog._open_btn.isEnabled()
        dialog._why.setPlainText("The keyed answer is the identity, not X.")
        assert dialog._open_btn.isEnabled()
        url = dialog.build_url()
        assert "gs%3AH-X-H%3A0" in url or "gs:H-X-H:0" in url
    finally:
        dialog.deleteLater()


def test_the_whole_report_path_writes_nothing_to_the_data_dir(screen, opened,
                                                              monkeypatch,
                                                              isolated_data_dir):
    from common.ui import errata_dialog

    monkeypatch.setattr(errata_dialog.ErrataDialog, "exec",
                        _accept_with("This is wrong."))
    _show(screen, _problem(), correct=False)
    screen._errata_btn.click()
    assert not isolated_data_dir.exists() or list(isolated_data_dir.iterdir()) == []
