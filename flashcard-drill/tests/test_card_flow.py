"""Drive CardScreen / MainWindow offscreen: start, reveal, rate, keyboard focus,
empty decks, timer wiring, session persistence.

Regression coverage for the review findings: the empty flagged-only session
that poisoned History (ZeroDivisionError -> qFatal), Space activating the
'End Session' button, and the first-card ``time_up.disconnect()`` TypeError.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

import persistence.storage as storage
from cards import all_cards
from core.deck import all_categories
from core.models import DrillConfig


def _cat() -> str:
    return all_categories()[0]


@pytest.fixture
def card_screen(qapp):
    from ui.screens.card_screen import CardScreen

    screen = CardScreen()
    screen.resize(900, 650)
    screen.show()
    qapp.processEvents()
    yield screen
    screen.close()
    screen.deleteLater()
    qapp.processEvents()


@pytest.fixture
def window(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    win.show()
    qapp.processEvents()
    yield win
    win.close()
    win.deleteLater()
    qapp.processEvents()


def _start(screen, n=3, timer=0, cat=None):
    assert screen.start(DrillConfig(categories=[cat or _cat()], card_count=n, timer_secs=timer))
    return screen


# ---------------------------------------------------------------------------
# CardScreen on its own
# ---------------------------------------------------------------------------

def test_start_reveal_rate_emits_stats(qapp, card_screen):
    got = []
    card_screen.session_complete.connect(got.append)
    _start(card_screen, n=3)
    assert card_screen._progress_lbl.text() == "Card 1 of 3"
    assert not card_screen.is_revealed

    for rate in (card_screen._got_btn, card_screen._unsure_btn, card_screen._missed_btn):
        card_screen._reveal_btn.click(); qapp.processEvents()
        assert card_screen.is_revealed
        rate.click(); qapp.processEvents()

    assert len(got) == 1
    stats = got[0]
    assert (stats.total, stats.got_it, stats.unsure, stats.missed) == (3, 1, 1, 1)
    assert [r.rating for r in stats.results] == ["got_it", "unsure", "missed"]
    assert all(r.elapsed_secs is not None and r.elapsed_secs >= 0 for r in stats.results)


def test_empty_deck_start_returns_false_and_emits_nothing(qapp, card_screen):
    completed, backs = [], []
    card_screen.session_complete.connect(completed.append)
    card_screen.back_requested.connect(lambda: backs.append(True))
    assert card_screen.start(DrillConfig(categories=[], card_count=5, flagged_only=True)) is False
    qapp.processEvents()
    assert completed == [] and backs == []
    assert card_screen.start_deck([], 0) is False


def test_space_reveals_and_focus_stays_on_screen(qapp, card_screen):
    """Regression: focus used to land on 'End Session', so Space ended the session."""
    backs, completed = [], []
    card_screen.back_requested.connect(lambda: backs.append(True))
    card_screen.session_complete.connect(completed.append)
    _start(card_screen, n=3)
    qapp.processEvents()

    assert qapp.focusWidget() is card_screen
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
    assert card_screen.is_revealed
    assert backs == [] and completed == []

    # Mouse-rate, then Space again on the next card (focus must come back).
    card_screen._got_btn.click(); qapp.processEvents()
    assert qapp.focusWidget() is card_screen
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
    assert card_screen.is_revealed and card_screen._idx == 1

    # Space / Return while revealed is a no-op (must never trigger a button).
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space)
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Return); qapp.processEvents()
    assert card_screen._stats.total == 1 and backs == [] and completed == []

    # Digits rate; Return reveals.
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_2); qapp.processEvents()
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Return); qapp.processEvents()
    QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_3); qapp.processEvents()
    assert len(completed) == 1
    s = completed[0]
    assert (s.total, s.got_it, s.unsure, s.missed) == (3, 1, 1, 1)


def test_no_button_on_card_screen_can_take_focus(card_screen):
    from PyQt6.QtWidgets import QPushButton

    focusable = [b.text() for b in card_screen.findChildren(QPushButton)
                 if b.focusPolicy() != Qt.FocusPolicy.NoFocus]
    assert focusable == []
    assert card_screen.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_timer_auto_reveals_once_per_card(qapp, card_screen):
    """First card: time_up.disconnect() on a never-connected signal must not raise;
    later cards: exactly one receiver, so one emission -> one reveal."""
    reveals = []
    orig = card_screen._reveal

    def counting():
        reveals.append(card_screen._idx)
        orig()
    card_screen._reveal = counting

    _start(card_screen, n=3, timer=10)                # would raise pre-fix on card 1
    assert card_screen._timer_widget.text() == "⏱ 10s"
    card_screen._timer_widget.time_up.emit(); qapp.processEvents()
    assert reveals == [0] and card_screen.is_revealed

    card_screen._got_btn.click(); qapp.processEvents()
    assert card_screen._timer_widget.text() == "⏱ 10s"
    card_screen._timer_widget.time_up.emit(); qapp.processEvents()
    assert reveals == [0, 1]                         # not [0, 1, 1]

    # A second emission on an already revealed card is ignored.
    card_screen._timer_widget.time_up.emit(); qapp.processEvents()
    assert reveals == [0, 1, 1] and card_screen._stats.total == 1


def test_end_session_with_nothing_rated_goes_back_without_stats(qapp, card_screen):
    backs, completed = [], []
    card_screen.back_requested.connect(lambda: backs.append(True))
    card_screen.session_complete.connect(completed.append)
    _start(card_screen, n=3)
    card_screen._end_btn.click(); qapp.processEvents()
    assert len(backs) == 1 and completed == []


def test_flag_button_toggles_and_writes_contract_entries(qapp, card_screen, data_dir):
    _start(card_screen, n=2)
    card_screen._reveal_btn.click(); qapp.processEvents()
    cid = card_screen.current_card.id
    toggled = []
    card_screen.flag_toggled.connect(lambda c, s: toggled.append((c, s)))

    card_screen._flag_btn.click(); qapp.processEvents()
    assert toggled == [(cid, True)]
    assert "unflag" in card_screen._flag_btn.text()
    entries = json.loads(storage._FLAGGED_FILE.read_text())
    assert len(entries) == 1
    assert set(entries[0]) == {"id", "label", "category", "app", "timestamp"}
    assert entries[0]["id"] == cid and entries[0]["app"] == "flashcard-drill"
    assert entries[0]["label"] == card_screen.current_card.front

    card_screen._flag_btn.click(); qapp.processEvents()
    assert toggled[-1] == (cid, False)
    assert storage.load_flagged() == set()
    assert card_screen._flag_btn.text() == "⚑ Flag for Review"


def test_flag_button_stays_truthful_when_persistence_fails(qapp, card_screen, monkeypatch):
    _start(card_screen, n=2)
    card_screen._reveal_btn.click(); qapp.processEvents()

    def boom(_cid):
        raise OSError("read-only data dir")
    monkeypatch.setattr(storage, "toggle_flag", boom)
    toggled = []
    card_screen.flag_toggled.connect(lambda c, s: toggled.append((c, s)))

    card_screen._flag_btn.click(); qapp.processEvents()
    assert toggled == []                                     # nothing was persisted
    assert card_screen._flag_btn.text() == "⚑ Flag for Review"
    assert "read-only" in card_screen._flag_btn.toolTip()


# ---------------------------------------------------------------------------
# MainWindow orchestration
# ---------------------------------------------------------------------------

def test_flagged_only_with_no_flags_never_writes_history(qapp, window, data_dir):
    from ui.main_window import PAGE_SETUP, PAGE_HISTORY

    setup = window._setup
    setup._flagged_cb.setChecked(True); qapp.processEvents()
    assert not setup._start_btn.isEnabled()
    assert setup._start_btn.toolTip()

    # Even if Start fires anyway (flags removed between validate and click) …
    setup._start_btn.setEnabled(True)
    setup._start_btn.click(); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_SETUP
    assert setup.notice_text()
    assert not storage.HISTORY_FILE.exists()

    # … or a drill is started programmatically with an empty deck.
    window._on_drill_started(DrillConfig(categories=[], card_count=5, flagged_only=True))
    qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_SETUP
    assert not storage.HISTORY_FILE.exists()

    # History must still open cleanly afterwards.
    window._on_history(); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_HISTORY


def test_flagged_only_start_enables_once_a_card_is_flagged(qapp, window):
    setup = window._setup
    setup._flagged_cb.setChecked(True); qapp.processEvents()
    assert not setup._start_btn.isEnabled()
    storage.toggle_flag(all_cards()[0].id)
    setup._validate()
    assert setup._start_btn.isEnabled()
    setup._flagged_cb.setChecked(False); qapp.processEvents()
    assert setup._start_btn.isEnabled()


def test_full_session_via_keyboard_is_saved_and_summarised(qapp, window, data_dir):
    from ui.main_window import PAGE_CARDS, PAGE_SUMMARY, PAGE_SETUP

    window._setup._count_spin.setValue(5)
    window._setup._start_btn.click(); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_CARDS
    assert qapp.focusWidget() is window._cards

    for key in (Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_1, Qt.Key.Key_1):
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
        QTest.keyClick(qapp.focusWidget(), key); qapp.processEvents()

    assert window._stack.currentIndex() == PAGE_SUMMARY
    assert window._summary._score_lbl.text() == "60%"
    sessions = json.loads(storage.HISTORY_FILE.read_text())
    assert len(sessions) == 1
    s = sessions[0]
    assert (s["total"], s["got_it"], s["unsure"], s["missed"]) == (5, 3, 1, 1)
    assert all(set(r) == {"card_id", "category", "rating", "elapsed_secs"} for r in s["results"])

    # Review Missed drills exactly the missed card, on the card page with focus.
    window._summary.review_missed.emit(); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_CARDS
    assert [c.id for c in window._cards.deck] == [r["card_id"] for r in s["results"] if r["rating"] == "missed"]
    assert qapp.focusWidget() is window._cards

    # End with nothing rated: back to Setup, nothing new written.
    window._cards._end_btn.click(); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_SETUP
    assert len(storage._load_raw()) == 1
    # Now that elapsed data exists the setup screen shows a session estimate.
    assert window._setup._estimate_lbl.text() != ""


def test_session_complete_with_zero_total_is_not_saved(qapp, window, data_dir):
    from core.models import SessionStats
    from ui.main_window import PAGE_SETUP

    window._cards.session_complete.emit(SessionStats()); qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_SETUP
    assert not storage.HISTORY_FILE.exists()
