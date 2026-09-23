""""Report a problem with this item" on the card back, driven offscreen.

The repository is public and the card bank is 550 hand-written cards: when one
of them is wrong, the path from "this is wrong" to a fix used to be
"remember it later", and nobody remembers it later.  The control tested here
turns a reveal into a prefilled GitHub issue.

Three properties are load-bearing and are each pinned below: it is **keyboard
reachable** (the drill's own buttons deliberately are not, so this one has to
be reached by Tab and activated by Space), it **never blocks** the drill (the
dialog is opened, not ``exec()``'d, so the countdown keeps running), and it
**degrades** when there is no browser to open (the URL goes to the clipboard
and the button says so) instead of the click doing nothing.

Nothing here touches the network: ``QDesktopServices.openUrl`` is stubbed, and
even in real use it only hands a URL to the system browser — the issue is not
filed until the user submits it on GitHub.
"""
from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import errata
from core.models import Flashcard
from ui.widgets import errata_button as errata_widget

CARD_A = Flashcard(id="pauli_xyx", category="Pauli Matrices",
                   front="XYX = ?", back="-Y")
CARD_B = Flashcard(id="pauli_xzx", category="Pauli Matrices",
                   front="XZX = ?", back="-Z")


class _Browser:
    """Stand-in for QDesktopServices: records the URLs, opens nothing."""

    def __init__(self, works: bool = True) -> None:
        self.works = works
        self.opened: list[str] = []

    def openUrl(self, url) -> bool:          # noqa: N802 (Qt naming)
        self.opened.append(url.toString())
        return self.works


@pytest.fixture
def browser(monkeypatch):
    fake = _Browser()
    monkeypatch.setattr(errata_widget, "QDesktopServices", fake)
    return fake


@pytest.fixture
def screen(qapp):
    from ui.screens.card_screen import CardScreen

    widget = CardScreen()
    widget.resize(900, 700)
    widget.show()
    qapp.processEvents()
    yield widget
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def _reveal(qapp, screen):
    screen._reveal_btn.click()
    qapp.processEvents()


def _fill_and_accept(qapp, dialog, why="The answer should be +Y.", fix="",
                     severity=None):
    dialog._why.setPlainText(why)
    if fix:
        dialog._fix.setPlainText(fix)
    if severity is not None:
        dialog._severity.setCurrentIndex(
            dialog._severity.findData(severity))
    qapp.processEvents()
    assert dialog._open_btn.isEnabled()
    dialog._open_btn.click()
    qapp.processEvents()


# ---------------------------------------------------------------------------
# Where it is, and what it knows
# ---------------------------------------------------------------------------

def test_it_appears_with_the_answer_and_never_before_it(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    assert not screen._errata_btn.isVisible()     # the front alone is not enough
    _reveal(qapp, screen)
    assert screen._errata_btn.isVisible()
    assert screen._errata_btn.text() == "⚠ Report a problem with this item"


def test_it_points_at_the_card_currently_on_screen(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)
    assert screen._errata_btn._item_id == "pauli_xyx"
    assert "XYX = ?" in screen._errata_btn._item_text
    assert "-Y" in screen._errata_btn._item_text

    screen._got_btn.click(); qapp.processEvents()
    _reveal(qapp, screen)
    assert screen._errata_btn._item_id == "pauli_xzx"
    assert "XZX = ?" in screen._errata_btn._item_text


def test_it_is_keyboard_reachable_and_named(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)
    btn = screen._errata_btn
    assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert btn.accessibleName() and btn.accessibleDescription()
    assert btn.toolTip()

    btn.setFocus(); qapp.processEvents()
    assert qapp.focusWidget() is btn
    QTest.keyClick(btn, Qt.Key.Key_Space); qapp.processEvents()
    assert btn.dialog is not None and btn.dialog.isVisible()
    btn.dialog.reject(); qapp.processEvents()


# ---------------------------------------------------------------------------
# It never blocks, and it hands the drill back
# ---------------------------------------------------------------------------

def test_the_dialog_is_opened_not_exec_d_so_the_drill_keeps_running(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)

    screen._errata_btn.click()            # returns immediately: no nested loop
    qapp.processEvents()
    dialog = screen._errata_btn.dialog
    assert dialog is not None and dialog.isVisible() and dialog.isModal()

    # The drill is still live underneath it: the timer ticks, the card is there.
    assert screen.current_card is CARD_A
    screen._timer_widget.reset(5)
    screen._timer_widget.start()
    assert screen.is_revealed

    # A second click does not stack a second dialog.
    screen._errata_btn.click(); qapp.processEvents()
    assert screen._errata_btn.dialog is dialog

    dialog.reject(); qapp.processEvents()
    assert screen._errata_btn.dialog is None
    # Keyboard focus is back on the drill (offscreen has no active window, so
    # this is the screen's own focus, not the application's).
    assert screen.focusWidget() is screen


def test_dismissing_the_dialog_reports_nothing(qapp, screen, browser):
    reported: list[str] = []
    screen._errata_btn.reported.connect(reported.append)
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)

    screen._errata_btn.click(); qapp.processEvents()
    screen._errata_btn.dialog._why.setPlainText("typed, then thought better")
    screen._errata_btn.dialog.reject(); qapp.processEvents()
    assert reported == [] and browser.opened == []


# ---------------------------------------------------------------------------
# The report itself
# ---------------------------------------------------------------------------

def test_accepting_opens_a_prefilled_github_issue_for_this_card(qapp, screen, browser):
    reported: list[str] = []
    screen._errata_btn.reported.connect(reported.append)
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)

    screen._errata_btn.click(); qapp.processEvents()
    _fill_and_accept(qapp, screen._errata_btn.dialog,
                     why="XYX is -Y only up to a phase convention.",
                     fix="Say which convention.", severity="misleading")

    # One report, one browser hand-off.  (Qt normalises the percent-encoding
    # on its way through QUrl, so the two strings are equal as URLs, not as
    # bytes — compare what they mean.)
    assert len(reported) == 1 and len(browser.opened) == 1
    assert parse_qs(urlparse(browser.opened[0]).query) == \
        parse_qs(urlparse(reported[0]).query)
    url = urlparse(reported[0])
    assert url.netloc == "github.com"
    assert url.path == f"/{errata.REPO}/issues/new"

    fields = {k: v[0] for k, v in parse_qs(url.query).items()}
    assert fields["template"] == "content_error.yml"
    assert fields["title"] == "[content] flashcard-drill: pauli_xyx"
    assert "flashcard-drill/cards/" in fields["file"]
    assert "pauli_xyx" in fields["file"]
    assert "XYX = ?" in fields["quote"] and "-Y" in fields["quote"]
    assert fields["why_wrong"].startswith("XYX is -Y only up to")
    assert fields["correction"] == "Say which convention."
    assert fields["severity"] == errata.SEVERITIES["misleading"]

    assert screen._errata_btn.dialog is None
    assert screen.focusWidget() is screen


def test_a_report_with_nothing_written_in_it_cannot_be_sent(qapp, screen):
    assert screen.start_deck([CARD_A], 0)
    _reveal(qapp, screen)
    screen._errata_btn.click(); qapp.processEvents()
    dialog = screen._errata_btn.dialog

    assert not dialog._open_btn.isEnabled()          # nothing to read yet
    dialog._why.setPlainText("   ")
    qapp.processEvents()
    assert not dialog._open_btn.isEnabled()
    dialog._why.setPlainText("wrong sign")
    qapp.processEvents()
    assert dialog._open_btn.isEnabled()
    dialog.reject(); qapp.processEvents()


def test_reporting_never_touches_the_drill_or_any_data_file(qapp, screen, browser, data_dir):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)
    screen._errata_btn.click(); qapp.processEvents()
    _fill_and_accept(qapp, screen._errata_btn.dialog)

    assert screen.current_card is CARD_A             # not rated, not advanced
    assert screen._stats.total == 0
    assert not data_dir.exists() or list(data_dir.iterdir()) == []


# ---------------------------------------------------------------------------
# No browser: the report is still recoverable
# ---------------------------------------------------------------------------

def test_with_no_browser_the_url_goes_to_the_clipboard_and_says_so(qapp, screen,
                                                                   monkeypatch):
    from PyQt6.QtGui import QGuiApplication

    fake = _Browser(works=False)
    monkeypatch.setattr(errata_widget, "QDesktopServices", fake)
    failed: list[str] = []
    reported: list[str] = []
    screen._errata_btn.open_failed.connect(failed.append)
    screen._errata_btn.reported.connect(reported.append)

    assert screen.start_deck([CARD_A, CARD_B], 0)
    _reveal(qapp, screen)
    screen._errata_btn.click(); qapp.processEvents()
    _fill_and_accept(qapp, screen._errata_btn.dialog)

    assert len(failed) == 1 and failed == reported   # still reported, not lost
    assert QGuiApplication.clipboard().text() == failed[0]
    assert screen._errata_btn.text() == errata_widget.NO_BROWSER_TEXT
    assert "clipboard" in screen._errata_btn.toolTip()
    assert failed[0] in screen._errata_btn.toolTip()

    # The notice is about that one attempt: the next card starts clean.
    screen._got_btn.click(); qapp.processEvents()
    _reveal(qapp, screen)
    assert screen._errata_btn.text() == errata_widget.BUTTON_TEXT


def test_the_button_can_be_told_not_to_open_anything(qapp, browser):
    """``open_browser=False`` is how a headless caller drives it."""
    btn = errata_widget.CardErrataButton(app="flashcard-drill",
                                         item_id="pauli_xyx",
                                         item_text="XYX = ?",
                                         open_browser=False)
    try:
        reported: list[str] = []
        btn.reported.connect(reported.append)
        btn.report()
        qapp.processEvents()
        _fill_and_accept(qapp, btn.dialog)
        assert len(reported) == 1 and browser.opened == []
        assert "pauli_xyx" in reported[0]
    finally:
        btn.deleteLater()
        qapp.processEvents()


def test_a_very_long_card_still_produces_a_usable_url(qapp, screen, browser):
    """Fields are truncated longest-first, so the file and the id always fit."""
    monster = Flashcard(id="long_card", category="Algorithms",
                        front="Q " + "x" * 9000, back="A " + "y" * 9000)
    assert screen.start_deck([monster], 0)
    _reveal(qapp, screen)
    screen._errata_btn.click(); qapp.processEvents()
    _fill_and_accept(qapp, screen._errata_btn.dialog, why="z" * 4000)

    url = browser.opened[0]
    assert len(url) <= errata.MAX_URL
    fields = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
    assert fields["title"] == "[content] flashcard-drill: long_card"
    assert "long_card" in fields["file"]


def test_the_dialog_class_is_the_shared_one(qapp):
    from common.ui.errata_dialog import ErrataButton, ErrataDialog

    assert issubclass(errata_widget.CardErrataButton, ErrataButton)
    btn = errata_widget.CardErrataButton(app="flashcard-drill")
    try:
        btn.report()
        qapp.processEvents()
        assert isinstance(btn.dialog, ErrataDialog)
        assert isinstance(btn.dialog, QDialog)
        btn.dialog.reject()
        qapp.processEvents()
    finally:
        btn.deleteLater()
        qapp.processEvents()
