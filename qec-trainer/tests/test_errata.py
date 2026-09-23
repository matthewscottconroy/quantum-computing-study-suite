"""Errata: "Report a problem with this item" -> a prefilled GitHub issue.

Every assertion drives the real control on the real result screen.  The only
thing stubbed is the two things a test must not do: open a modal dialog and
open a browser.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import QDialog

import common_path  # noqa: F401  (puts the repo root on sys.path)
from common import errata
from common.ui import errata_dialog as ed

from core.models import Attempt, GradeMode, Problem, Verdict


def _attempt(pid: str = "surf_mwpm") -> Attempt:
    problem = Problem(
        id=pid, category="Surface Code", difficulty="intermediate",
        question="Which decoder is standard for the surface code?",
        choices=["Union-Find", "MWPM", "Belief propagation", "Lookup table"],
        correct_index=1,
        explanation="Minimum-weight perfect matching pairs the fired checks.",
        grade_mode=GradeMode.AUTO)
    return Attempt(problem, "A", 0, Verdict.INCORRECT, "Not quite.")


@pytest.fixture
def result(qapp):
    from ui.screens.result_screen import ResultScreen

    screen = ResultScreen()
    screen.show_attempt(_attempt(), is_last=False)
    yield screen
    screen.close()


class _Browser:
    """Stand-in for QDesktopServices: records the URL, reports success or not."""

    def __init__(self, succeeds: bool = True, raises: bool = False) -> None:
        self.succeeds = succeeds
        self.raises = raises
        self.urls: list[QUrl] = []

    def openUrl(self, url: QUrl) -> bool:    # noqa: N802 (Qt naming)
        if self.raises:
            raise RuntimeError("no desktop integration here")
        self.urls.append(url)
        return self.succeeds

    def opened(self) -> list[str]:
        """The URLs as handed over, compared through QUrl so the percent
        encoding QUrl normalises does not make a true match look false."""
        return [u.toString() for u in self.urls]


@pytest.fixture
def browser(monkeypatch):
    from ui.screens import result_screen

    fake = _Browser()
    monkeypatch.setattr(result_screen, "QDesktopServices", fake)
    return fake


def _fill_and_accept(monkeypatch, why="B is also defensible.",
                     fix="Say 'MWPM or Union-Find'.", severity="misleading"):
    """Make ErrataDialog.exec() fill itself in and accept, without a modal loop."""
    seen: dict = {}

    def fake_exec(self):
        seen["dialog"] = self
        seen["enabled_before"] = self._open_btn.isEnabled()
        self._why.setPlainText(why)
        seen["enabled_after"] = self._open_btn.isEnabled()
        self._fix.setPlainText(fix)
        index = self._severity.findData(severity)
        assert index >= 0, severity
        self._severity.setCurrentIndex(index)
        self._on_accept()
        return int(QDialog.DialogCode.Accepted)

    monkeypatch.setattr(ed.ErrataDialog, "exec", fake_exec)
    return seen


# ── the control ───────────────────────────────────────────────────────────────

def test_the_result_screen_offers_an_errata_control(result):
    btn = result.errata_button
    assert isinstance(btn, ed.ErrataButton)
    assert btn.isVisibleTo(result)
    assert btn.isEnabled()
    assert "Report a problem" in btn.text()
    assert btn.accessibleName()
    assert btn.toolTip()


def test_the_control_is_keyboard_reachable(result):
    """Tab must reach it: a mouse-only escape hatch is no escape hatch."""
    btn = result.errata_button
    assert btn.focusPolicy() in (Qt.FocusPolicy.StrongFocus,
                                 Qt.FocusPolicy.WheelFocus)
    chain, node = [], result.nextInFocusChain()
    for _ in range(400):
        chain.append(node)
        node = node.nextInFocusChain()
        if node is result:
            break
    assert btn in chain


def test_it_follows_the_item_on_screen(result):
    btn = result.errata_button
    assert btn._item_id == "surf_mwpm"
    assert "Which decoder" in btn._item_text

    result.show_attempt(_attempt("steane_distance"), is_last=True)
    assert btn._item_id == "steane_distance"


# ── the URL ───────────────────────────────────────────────────────────────────

def test_reporting_builds_a_prefilled_issue_for_this_item(result, browser, monkeypatch):
    seen = _fill_and_accept(monkeypatch)
    url = result.errata_button.report()

    assert url and browser.opened() == [QUrl(url).toString()]
    parsed = urlparse(url)
    assert parsed.scheme == "https" and parsed.netloc == "github.com"
    assert parsed.path == f"/{errata.REPO}/issues/new"

    fields = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    assert fields["template"] == "content_error.yml"
    assert fields["title"] == "[content] qec-trainer: surf_mwpm"
    assert "qec-trainer/problems/" in fields["file"]
    assert "surf_mwpm" in fields["file"]
    assert "Which decoder is standard" in fields["quote"]
    assert "Bank answer: B. MWPM" in fields["quote"]     # what a fixer needs
    assert fields["why_wrong"] == "B is also defensible."
    assert fields["correction"] == "Say 'MWPM or Union-Find'."
    assert fields["severity"] == errata.SEVERITIES["misleading"]


def test_an_empty_report_cannot_be_submitted(result, browser, monkeypatch):
    seen = _fill_and_accept(monkeypatch, why="something is wrong")
    result.errata_button.report()
    assert seen["enabled_before"] is False    # nothing typed yet
    assert seen["enabled_after"] is True


def test_cancelling_reports_nothing(result, browser, monkeypatch):
    monkeypatch.setattr(ed.ErrataDialog, "exec",
                        lambda self: int(QDialog.DialogCode.Rejected))
    assert result.errata_button.report() is None
    assert browser.urls == []
    assert result._errata_lbl.isHidden()


# ── degrading gracefully ──────────────────────────────────────────────────────

def test_a_successful_open_says_nothing_was_sent_yet(result, browser, monkeypatch):
    _fill_and_accept(monkeypatch)
    result.errata_button.report()
    assert not result._errata_lbl.isHidden()
    assert "nothing is sent" in result._errata_lbl.text().lower()


def test_no_browser_falls_back_to_the_clipboard(result, browser, monkeypatch, qapp):
    browser.succeeds = False
    _fill_and_accept(monkeypatch)
    url = result.errata_button.report()

    assert url                                  # the report was still built
    assert not result._errata_lbl.isHidden()
    assert "clipboard" in result._errata_lbl.text().lower()
    clipboard = qapp.clipboard()
    if clipboard is not None:                   # absent on some headless setups
        assert clipboard.text() == url


def test_a_desktop_that_raises_shows_the_link_instead_of_crashing(
        result, browser, monkeypatch):
    browser.raises = True
    monkeypatch.setattr(type(result), "_copy_to_clipboard",
                        staticmethod(lambda text: False))
    _fill_and_accept(monkeypatch)
    url = result.errata_button.report()

    assert url
    assert url in result._errata_lbl.text()
    assert result._errata_lbl.textInteractionFlags() & \
        Qt.TextInteractionFlag.TextSelectableByMouse


def test_reporting_is_offline_and_leaves_no_trace_in_the_data_dir(
        result, browser, monkeypatch, isolated_data_dir):
    """The URL is built by pure string work — no network, no files, no blocking."""
    _fill_and_accept(monkeypatch)
    result.errata_button.report()
    assert not isolated_data_dir.exists()


def test_showing_the_next_item_clears_the_last_report_message(
        result, browser, monkeypatch):
    _fill_and_accept(monkeypatch)
    result.errata_button.report()
    assert not result._errata_lbl.isHidden()
    result.show_attempt(_attempt("rep_distance"), is_last=False)
    assert result._errata_lbl.isHidden()
    assert result._errata_lbl.text() == ""


def test_a_very_long_item_is_truncated_rather_than_dropped(result, browser, monkeypatch):
    long_attempt = _attempt("long_one")
    long_attempt.problem.explanation = "x" * 20_000
    result.show_attempt(long_attempt, is_last=False)
    _fill_and_accept(monkeypatch)
    url = result.errata_button.report()

    assert url and len(url) <= errata.MAX_URL
    fields = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    assert fields["title"] == "[content] qec-trainer: long_one"   # never trimmed
    assert fields["why_wrong"] == "B is also defensible."


# ── the whole flow, through the main window ───────────────────────────────────

def test_reporting_from_a_live_session_does_not_disturb_the_drill(
        qapp, browser, monkeypatch, isolated_data_dir):
    from ui.main_window import MainWindow, PAGE_RESULT

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    win = MainWindow()
    try:
        win._problems = [_attempt().problem]
        win._idx = 0
        win._show_current_problem()
        win._problem._radio_btns[0].setChecked(True)
        win._problem._validate_mc()
        win._problem._on_submit()
        assert win._stack.currentIndex() == PAGE_RESULT

        _fill_and_accept(monkeypatch)
        url = win._result.errata_button.report()

        assert url and browser.opened() == [QUrl(url).toString()]
        assert win._stack.currentIndex() == PAGE_RESULT      # still on the item
        assert win._result._next_btn.isEnabled()             # Next never blocked
        assert win._result._mistake_card.isVisibleTo(win._result)
    finally:
        win.close()
