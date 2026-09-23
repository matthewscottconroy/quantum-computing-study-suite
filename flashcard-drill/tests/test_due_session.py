"""Drive the SM-2 daily pull offscreen: due counts, "Due today" mode, summary.

Everything here goes through the real widgets and the real (temp) data dir, so
it also covers the wiring between card_screen -> schedule_store -> setup/summary.
"""
from __future__ import annotations

import json
from datetime import date, timedelta

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtTest import QTest

import persistence.schedule_store as store
import persistence.storage as storage
from cards import all_cards
from core.deck import all_categories
from core.models import DrillConfig
from core.scheduler import CardState
from ui.screens.setup_screen import MODE_DUE, MODE_FREE

TODAY = date.today()


@pytest.fixture
def make_window(qapp, monkeypatch):
    """Build MainWindow *after* the test has seeded the data dir."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    windows = []

    def factory():
        from ui.main_window import MainWindow
        win = MainWindow()
        win.show()
        qapp.processEvents()
        windows.append(win)
        return win

    yield factory
    for win in windows:
        win.close()
        win.deleteLater()
    qapp.processEvents()


def _seed(offsets: dict[str, int], **kw) -> dict[str, CardState]:
    """Write a schedule where ``card_id -> due = today + offset`` days."""
    states = {
        cid: CardState(cid, n=kw.get("n", 2), ef=kw.get("ef", 2.5),
                       interval_days=kw.get("interval_days", 6),
                       due=TODAY + timedelta(days=off),
                       last_seen=TODAY + timedelta(days=off - 6))
        for cid, off in offsets.items()
    }
    store.save_states(states)
    return states


def _smallest_category() -> str:
    counts: dict[str, int] = {}
    for c in all_cards():
        counts[c.category] = counts.get(c.category, 0) + 1
    return min(counts, key=lambda k: counts[k])


def _select_only(setup, category: str) -> None:
    for cat, cb in setup._cbs.items():
        cb.setChecked(cat == category)


# ---------------------------------------------------------------------------
# Setup screen: the daily pull
# ---------------------------------------------------------------------------

def test_fresh_install_has_no_schedule_and_defaults_to_free_drill(make_window, data_dir):
    setup = make_window()._setup
    assert not store.schedule_exists()
    assert setup.mode == MODE_FREE
    assert setup.due_summary.due == 0
    assert setup.due_summary.new == setup.due_summary.total == len(all_cards())
    assert "No review schedule yet" in setup._due_lbl.text()
    assert setup._start_btn.isEnabled()
    assert setup._due_btn.isHidden()


def test_due_count_is_shown_and_due_mode_becomes_the_default(qapp, make_window, data_dir):
    ids = [c.id for c in all_cards()[:23]]
    _seed({cid: -1 for cid in ids})
    setup = make_window()._setup

    assert setup.due_summary.due == 23
    assert setup._due_lbl.text() == "23 cards due today"
    sub = setup._due_sub_lbl.text()
    assert "23 overdue" in sub and "23 scheduled" in sub
    assert f"{len(all_cards()) - 23} new" in sub
    assert setup.mode == MODE_DUE           # auto-selected: there is a pull today
    assert not setup._due_btn.isHidden()
    assert setup._start_btn.isEnabled()


def test_singular_wording_and_next_review_line(qapp, make_window, data_dir):
    card_id = all_cards()[0].id
    _seed({card_id: 0})
    setup = make_window()._setup
    assert setup._due_lbl.text() == "1 card due today"

    _seed({card_id: 3})
    setup._refresh_due()
    assert setup._due_lbl.text() == "Nothing due today"
    assert "next review in 3 days" in setup._due_sub_lbl.text()
    assert setup._due_btn.isHidden()


def test_user_mode_choice_is_not_overridden_by_a_refresh(qapp, make_window, data_dir):
    _seed({c.id: -1 for c in all_cards()[:5]})
    setup = make_window()._setup
    assert setup.mode == MODE_DUE

    setup._mode_combo.setCurrentIndex(setup._mode_combo.findData(MODE_FREE))
    setup._on_mode_picked(setup._mode_combo.currentIndex())
    setup.showEvent(QShowEvent())          # coming back from a session
    qapp.processEvents()
    assert setup.mode == MODE_FREE          # the refresh must respect the choice


def test_flagged_only_disables_the_schedule_mode(qapp, make_window, data_dir):
    _seed({c.id: -1 for c in all_cards()[:4]})
    setup = make_window()._setup
    setup._flagged_cb.setChecked(True)
    qapp.processEvents()
    assert not setup._mode_combo.isEnabled()
    assert setup._due_btn.isHidden()
    setup._flagged_cb.setChecked(False)
    qapp.processEvents()
    assert setup._mode_combo.isEnabled()


# ---------------------------------------------------------------------------
# A "Due today" session end to end
# ---------------------------------------------------------------------------

def test_due_session_draws_due_cards_oldest_first_then_new(qapp, make_window, data_dir):
    pool = all_cards()
    oldest, middle, today_card, future = pool[0].id, pool[1].id, pool[2].id, pool[3].id
    _seed({oldest: -9, middle: -4, today_card: 0, future: 6})

    window = make_window()
    setup = window._setup
    assert setup.mode == MODE_DUE
    setup._count_spin.setValue(6)
    setup._start_btn.click()
    qapp.processEvents()

    from ui.main_window import PAGE_CARDS
    assert window._stack.currentIndex() == PAGE_CARDS
    deck = [c.id for c in window._cards.deck]
    assert deck[:3] == [oldest, middle, today_card]      # oldest due first
    assert len(deck) == 6                                # topped up with new cards
    assert future not in deck                            # not due yet
    assert len(set(deck)) == 6


def test_review_due_cards_button_starts_the_pull(qapp, make_window, data_dir):
    due_ids = [c.id for c in all_cards()[:2]]
    _seed({cid: -1 for cid in due_ids})
    window = make_window()
    window._setup._mode_combo.setCurrentIndex(window._setup._mode_combo.findData(MODE_FREE))
    window._setup._on_mode_picked(1)
    window._setup._count_spin.setValue(5)

    window._setup._due_btn.click()
    qapp.processEvents()
    from ui.main_window import PAGE_CARDS
    assert window._stack.currentIndex() == PAGE_CARDS
    assert window._setup.mode == MODE_DUE
    assert [c.id for c in window._cards.deck][:2] == due_ids


def test_rating_a_due_session_advances_the_schedule_and_the_summary(qapp, make_window, data_dir):
    from ui.main_window import PAGE_SUMMARY

    pool = all_cards()
    graduating = pool[0].id          # 6-day card answered "Got it" -> 15 days
    lapsing = pool[1].id             # 6-day card answered "Missed" -> 1 day, lapse
    _seed({graduating: -1, lapsing: -1})

    window = make_window()
    window._setup._count_spin.setValue(5)          # 5 is the minimum the spin allows
    window._setup._start_btn.click()
    qapp.processEvents()
    deck = [c.id for c in window._cards.deck]
    assert len(deck) == 5
    assert deck[:2] == [graduating, lapsing]

    # got it / missed / unsure / got it / got it
    for key in (Qt.Key.Key_1, Qt.Key.Key_3, Qt.Key.Key_2, Qt.Key.Key_1, Qt.Key.Key_1):
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
        QTest.keyClick(qapp.focusWidget(), key); qapp.processEvents()

    assert window._stack.currentIndex() == PAGE_SUMMARY

    states = store.load_states()
    assert states[graduating].interval_days == 15
    assert states[graduating].due == TODAY + timedelta(days=15)
    assert states[lapsing].interval_days == 1 and states[lapsing].lapses == 1
    assert states[lapsing].ef == pytest.approx(2.3)
    assert states[deck[2]].n == 1 and states[deck[2]].interval_days == 1   # new, "unsure"

    stats = window._last_stats
    # 6->15 plus the three new cards that earned their first 1-day interval.
    assert (stats.graduated, stats.lapsed) == (4, 1)
    line = window._summary._schedule_lbl.text()
    assert not window._summary._schedule_lbl.isHidden()
    assert "4 graduated to a longer interval" in line
    assert "1 lapsed back to 1 day" in line
    assert "longest interval now 15 days" in line
    assert "next review tomorrow (4 cards)" in line

    # History keeps its own schema, untouched by the scheduler.
    sessions = json.loads(storage.history_path().read_text())
    assert len(sessions) == 1 and sessions[0]["total"] == 5
    assert all(set(r) == {"card_id", "category", "rating", "elapsed_secs"}
               for r in sessions[0]["results"])

    # Back on Setup the pull is empty again — the habit loop closed for today.
    window._summary.back_requested.emit()
    qapp.processEvents()
    assert window._setup.due_summary.due == 0
    assert window._setup._due_lbl.text() == "Nothing due today"
    assert "next review tomorrow" in window._setup._due_sub_lbl.text()


def test_free_drill_also_updates_the_schedule(qapp, make_window, data_dir):
    window = make_window()
    assert window._setup.mode == MODE_FREE
    window._setup._count_spin.setValue(5)
    window._setup._start_btn.click()
    qapp.processEvents()
    for _ in range(5):
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_1); qapp.processEvents()

    states = store.load_states()
    assert len(states) == 5
    assert all(s.interval_days == 1 and s.n == 1 for s in states.values())


def test_nothing_due_and_nothing_new_disables_start_and_explains_when_to_return(
        qapp, make_window, data_dir):
    category = _smallest_category()
    ids = [c.id for c in all_cards() if c.category == category]
    _seed({cid: 4 for cid in ids})

    window = make_window()
    setup = window._setup
    _select_only(setup, category)
    setup._mode_combo.setCurrentIndex(setup._mode_combo.findData(MODE_DUE))
    setup._on_mode_picked(setup._mode_combo.currentIndex())
    qapp.processEvents()

    assert setup.due_summary.available == 0
    assert not setup._start_btn.isEnabled()
    assert "in 4 days" in setup._start_btn.toolTip()

    # Forcing the drill anyway lands back on Setup with a mode-aware notice.
    from ui.main_window import PAGE_SETUP
    window._on_drill_started(DrillConfig(categories=[category], card_count=5, due_only=True))
    qapp.processEvents()
    assert window._stack.currentIndex() == PAGE_SETUP
    assert "in 4 days" in setup.notice_text()
    assert "Free drill" in setup.notice_text()
    assert not storage.history_path().exists()


def test_no_category_selected_says_so_instead_of_claiming_no_schedule(qapp, make_window,
                                                                     data_dir):
    _seed({c.id: -1 for c in all_cards()[:3]})
    setup = make_window()._setup
    assert setup._due_lbl.text() == "3 cards due today"

    for cb in setup._cbs.values():
        cb.setChecked(False)
    qapp.processEvents()
    assert setup._due_lbl.text() == "No categories selected"
    assert setup.due_summary.total == 0
    assert not setup._start_btn.isEnabled()
    assert setup._due_btn.isHidden()


def test_due_mode_respects_the_category_selection(qapp, make_window, data_dir):
    category = _smallest_category()
    other = next(c for c in all_categories() if c != category)
    in_scope = [c.id for c in all_cards() if c.category == category][:3]
    out_of_scope = [c.id for c in all_cards() if c.category == other][:3]
    _seed({cid: -2 for cid in in_scope + out_of_scope})

    window = make_window()
    setup = window._setup
    _select_only(setup, category)
    qapp.processEvents()
    assert setup.due_summary.due == 3

    setup._mode_combo.setCurrentIndex(setup._mode_combo.findData(MODE_DUE))
    setup._count_spin.setValue(5)
    setup._start_btn.click()
    qapp.processEvents()
    deck = [c.id for c in window._cards.deck]
    assert set(deck[:3]) == set(in_scope)
    assert not set(deck) & set(out_of_scope)


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------

def test_existing_history_with_no_schedule_bootstraps_on_first_launch(
        qapp, make_window, data_dir):
    from core.models import CardResult, Rating, SessionStats

    pool = all_cards()[:12]
    stats = SessionStats(total=len(pool), got_it=len(pool))
    for card in pool:
        stats.results.append(CardResult(card_id=card.id, category=card.category,
                                        rating=Rating.GOT_IT.value))
    storage.save_session(stats)
    before = storage.history_path().read_bytes()
    assert not store.schedule_exists()

    setup = make_window()._setup

    assert store.schedule_exists()                       # migrated on first read
    assert storage.history_path().read_bytes() == before   # and history is untouched
    states = store.load_states()
    assert set(states) == {c.id for c in pool}
    assert all(s.n == 1 and s.interval_days == 1 for s in states.values())
    # Rated today, so they come back tomorrow: nothing due yet, free drill stays.
    assert setup.due_summary.due == 0
    assert setup.due_summary.scheduled == 12
    assert setup.mode == MODE_FREE
    assert "next review tomorrow" in setup._due_sub_lbl.text()


# ---------------------------------------------------------------------------
# Failure modes reaching the UI
# ---------------------------------------------------------------------------

def test_an_unwritable_data_dir_degrades_instead_of_aborting(qapp, make_window, data_dir,
                                                             monkeypatch):
    """Read-only storage: the drill runs, the summary appears, nothing raises."""
    import ui.main_window as main_window

    ids = [c.id for c in all_cards()[:2]]
    _seed({cid: -1 for cid in ids})
    window = make_window()

    def boom(_stats):
        raise PermissionError("read-only data dir")

    monkeypatch.setattr(main_window, "save_session", boom)
    monkeypatch.setattr(store, "save_states", boom)

    window._setup._count_spin.setValue(5)
    window._setup._start_btn.click()
    qapp.processEvents()
    for _ in range(5):
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_Space); qapp.processEvents()
        QTest.keyClick(qapp.focusWidget(), Qt.Key.Key_1); qapp.processEvents()

    from ui.main_window import PAGE_SUMMARY
    assert window._stack.currentIndex() == PAGE_SUMMARY
    assert window._summary._score_lbl.text() == "100%"
    assert "could not be saved" in window._summary.warning_text()
    assert window._last_stats.schedule == []        # nothing was persisted, nothing claimed
    assert window._summary._schedule_lbl.isHidden()


def test_a_corrupt_schedule_file_is_treated_as_no_schedule(qapp, make_window, data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    store.schedule_path().write_text('{"junk": [1, 2, 3], "bad": {"ef": "x"}')
    setup = make_window()._setup
    assert setup.due_summary.due == 0
    assert setup.mode == MODE_FREE
    assert setup._start_btn.isEnabled()
