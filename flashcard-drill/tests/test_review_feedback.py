"""Drive the confidence strip and the mistake journal offscreen.

Covers the whole user-visible contract: a wrong answer logged and categorised, a
confidence rating paired with its grade, "Got it" later resolving the entry, the
opt-out, keyboard reach and accessible names — and, crucially, that none of it
disturbs the SM-2 schedule or the existing history schemas.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QPushButton

import persistence.review_store as rs
import persistence.storage as storage
from core.models import Flashcard

MISTAKE_FIELDS = {"id", "app", "category", "question", "your_answer",
                  "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}

CARD_A = Flashcard(id="pauli_xyx", category="Pauli Matrices",
                   front="XYX = ?", back="-Y")
CARD_B = Flashcard(id="pauli_xzx", category="Pauli Matrices",
                   front="XZX = ?", back="-Z")


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


@pytest.fixture
def window(qapp, monkeypatch):
    """MainWindow offscreen with no API key anywhere (this app never needs one)."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    win.show()
    qapp.processEvents()
    yield win
    win.close()
    win.deleteLater()
    qapp.processEvents()


def _miss(qapp, screen):
    """Reveal the current card and rate it Missed."""
    screen._reveal_btn.click(); qapp.processEvents()
    screen._missed_btn.click(); qapp.processEvents()


# ---------------------------------------------------------------------------
# 1 + 2 — a wrong answer becomes a categorised journal entry
# ---------------------------------------------------------------------------

def test_a_missed_card_is_journalled_with_the_exact_contract_schema(qapp, screen, data_dir):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)

    # Logged immediately, before any cause is picked: nothing can be lost.
    assert rs.mistakes_path() == data_dir / "mistakes.json"
    entries = json.loads(rs.mistakes_path().read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) == MISTAKE_FIELDS
    assert entry["id"] == "pauli_xyx"
    assert entry["app"] == "flashcard-drill"
    assert entry["category"] == "Pauli Matrices"
    assert entry["question"] == "XYX = ?"
    assert entry["correct_answer"] == "-Y"
    assert "Missed" in entry["your_answer"]
    assert entry["cause"] is None
    assert entry["note"] == ""
    assert isinstance(entry["timestamp"], float) and entry["timestamp"] > 0
    assert entry["resolved"] is False
    assert all(len(entry[f]) <= 200
               for f in ("question", "your_answer", "correct_answer", "note"))

    # The cause row is up, showing the question *and* the answer, over card 2.
    assert screen.cause_row_visible
    assert "XYX = ?" in screen._cause_question_lbl.text()
    assert "Missed" in screen._cause_question_lbl.text()
    assert screen._cause_answer_lbl.text() == "Answer: -Y"
    assert screen.current_card is CARD_B          # the drill was never held up
    assert screen._progress_lbl.text() == "Card 2 of 2"

    # Categorising updates that same entry in place.
    screen._cause_note.setText("little-endian slip again")
    screen._cause_btns["knew_but_slipped"].click(); qapp.processEvents()

    entries = json.loads(rs.mistakes_path().read_text())
    assert len(entries) == 1
    assert entries[0]["cause"] == "knew_but_slipped"
    assert entries[0]["note"] == "little-endian slip again"
    assert entries[0]["timestamp"] == entry["timestamp"]
    assert set(entries[0]) == MISTAKE_FIELDS


def test_skipping_the_cause_row_still_leaves_the_mistake_logged(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_dismiss_btn.click(); qapp.processEvents()

    assert not screen.cause_row_visible
    logged = rs.load_mistakes()
    assert len(logged) == 1 and logged[0]["cause"] is None
    assert logged[0]["resolved"] is False


def test_escape_dismisses_the_cause_row_and_the_next_rating_closes_it(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    assert screen.cause_row_visible
    QTest.keyClick(screen, Qt.Key.Key_Escape); qapp.processEvents()
    assert not screen.cause_row_visible

    # …and rating the following card closes it when it was left open.
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    assert screen.cause_row_visible
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()
    assert not screen.cause_row_visible


def test_a_note_typed_without_a_cause_is_still_saved(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_note.setText("check the Y sign convention")
    screen._cause_note.editingFinished.emit(); qapp.processEvents()

    logged = rs.load_mistakes()[0]
    assert logged["note"] == "check the Y sign convention" and logged["cause"] is None


def test_a_note_is_flushed_when_the_row_closes_on_the_next_rating(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_note.setText("sign convention")      # typed, never confirmed
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()      # closes the row
    assert not screen.cause_row_visible
    assert rs.load_mistakes()[0]["note"] == "sign convention"


def test_clicking_the_chosen_cause_again_clears_it(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_btns["misread"].click(); qapp.processEvents()
    assert rs.load_mistakes()[0]["cause"] == "misread"
    screen._cause_btns["misread"].click(); qapp.processEvents()
    assert rs.load_mistakes()[0]["cause"] is None


def test_each_miss_is_its_own_event_and_the_row_follows_the_latest(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B, CARD_A], 0)
    _miss(qapp, screen)
    screen._cause_btns["misread"].click(); qapp.processEvents()
    _miss(qapp, screen)                                   # card B
    assert "XZX = ?" in screen._cause_question_lbl.text()
    screen._cause_btns["out_of_time"].click(); qapp.processEvents()

    assert [(e["id"], e["cause"]) for e in rs.load_mistakes()] == [
        ("pauli_xyx", "misread"), ("pauli_xzx", "out_of_time")]
    assert rs.cause_counts() == {"misread": 1, "out_of_time": 1}


def test_a_miss_on_the_final_card_is_logged_even_though_no_row_can_be_shown(qapp, screen):
    done = []
    screen.session_complete.connect(done.append)
    assert screen.start_deck([CARD_A], 0)
    _miss(qapp, screen)
    assert len(done) == 1                                 # the session still ended
    assert not screen.cause_row_visible
    assert [e["id"] for e in rs.load_mistakes()] == ["pauli_xyx"]


# ---------------------------------------------------------------------------
# 3 — confidence pairing
# ---------------------------------------------------------------------------

def test_confidence_is_taken_before_the_reveal_and_paired_with_the_grade(qapp, screen, data_dir):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    assert not screen._confidence_container.isHidden()    # shown with the FRONT
    assert not screen.is_revealed

    screen._confidence_btns[4].click(); qapp.processEvents()
    assert screen._confidence == 4
    assert screen._confidence_btns[4].isChecked()
    assert screen._confidence_btns[4].text().startswith("●")   # glyph, not colour
    assert screen._confidence_btns[1].text().startswith("○")
    assert not rs.confidence_path().exists()              # nothing until it is graded

    screen._reveal_btn.click(); qapp.processEvents()
    assert screen._confidence_container.isHidden()        # cannot be hindsight
    screen._missed_btn.click(); qapp.processEvents()

    assert rs.confidence_path() == data_dir / "confidence.json"
    rows = json.loads(rs.confidence_path().read_text())
    assert len(rows) == 1
    assert set(rows[0]) == CONFIDENCE_FIELDS
    assert rows[0] == {
        "id": "pauli_xyx", "app": "flashcard-drill", "category": "Pauli Matrices",
        "confidence": 4, "correct": False, "timestamp": rows[0]["timestamp"],
    }
    assert isinstance(rows[0]["timestamp"], float) and rows[0]["timestamp"] > 0
    assert [e["id"] for e in rs.confidently_wrong()] == ["pauli_xyx"]

    # A fresh card starts with no rating, and "Got it" records correct=True.
    assert screen._confidence is None
    assert all(b.text().startswith("○") for b in screen._confidence_btns.values())
    screen._confidence_btns[2].click(); qapp.processEvents()
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()
    assert [(r["confidence"], r["correct"]) for r in rs.load_confidence()] == [
        (4, False), (2, True)]
    assert rs.calibration_summary() == {2: {"total": 1, "correct": 1},
                                        4: {"total": 1, "correct": 0}}


def test_confidence_is_optional_and_toggles_off(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    screen._confidence_btns[3].click(); qapp.processEvents()
    screen._confidence_btns[3].click(); qapp.processEvents()   # same button clears it
    assert screen._confidence is None
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()
    assert rs.load_confidence() == []                     # skipped, nothing recorded


def test_digits_set_confidence_before_the_reveal_and_rate_after_it(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    screen.setFocus(); qapp.processEvents()
    QTest.keyClick(screen, Qt.Key.Key_3); qapp.processEvents()
    assert screen._confidence == 3 and not screen.is_revealed and screen._stats.total == 0

    QTest.keyClick(screen, Qt.Key.Key_Space); qapp.processEvents()
    QTest.keyClick(screen, Qt.Key.Key_1); qapp.processEvents()     # now it rates
    assert screen._stats.got_it == 1
    assert [(r["confidence"], r["correct"]) for r in rs.load_confidence()] == [(3, True)]


def test_dont_ask_hides_the_strip_for_good_and_setup_can_undo_it(qapp, window):
    from ui.main_window import PAGE_CARDS, PAGE_SETUP

    cards, setup = window._cards, window._setup
    window._stack.setCurrentIndex(PAGE_CARDS); qapp.processEvents()
    assert cards.start_deck([CARD_A, CARD_B], 0)
    assert not cards._confidence_container.isHidden()
    cards._confidence_off_btn.click(); qapp.processEvents()
    assert cards._confidence_container.isHidden()
    assert rs.confidence_enabled() is False

    assert cards.start_deck([CARD_A, CARD_B], 0)          # still hidden next session
    assert cards._confidence_container.isHidden()
    cards._reveal_btn.click(); qapp.processEvents()
    cards._got_btn.click(); qapp.processEvents()
    assert rs.load_confidence() == []

    window._stack.setCurrentIndex(PAGE_SETUP); qapp.processEvents()
    assert setup._confidence_cb.isChecked() is False   # showEvent re-reads the file
    setup._confidence_cb.setChecked(True); qapp.processEvents()
    assert rs.confidence_enabled() is True
    assert cards.start_deck([CARD_A, CARD_B], 0)
    assert not cards._confidence_container.isHidden()


# ---------------------------------------------------------------------------
# 4 — a later correct answer resolves the entry
# ---------------------------------------------------------------------------

def test_getting_the_card_right_later_resolves_the_journal_entry(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_btns["didnt_know"].click(); qapp.processEvents()
    assert rs.load_mistakes()[0]["resolved"] is False

    assert screen.start_deck([CARD_A, CARD_B], 0)
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()

    entries = rs.load_mistakes()
    assert len(entries) == 1                              # resolved, not duplicated
    assert entries[0]["resolved"] is True
    assert entries[0]["cause"] == "didnt_know"            # the analysis survives


def test_unsure_does_not_resolve_a_mistake(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    assert screen.start_deck([CARD_A, CARD_B], 0)
    screen._reveal_btn.click(); qapp.processEvents()
    screen._unsure_btn.click(); qapp.processEvents()
    assert rs.load_mistakes()[0]["resolved"] is False


# ---------------------------------------------------------------------------
# The drill itself is unchanged
# ---------------------------------------------------------------------------

def test_journalling_never_double_counts_as_an_sm2_lapse(qapp, screen, data_dir):
    """A logged mistake is analysis; the schedule update stays exactly as before."""
    from persistence.schedule_store import load_states

    assert screen.start_deck([CARD_A, CARD_B], 0)         # learn card A first
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()
    assert load_states()["pauli_xyx"].lapses == 0

    assert screen.start_deck([CARD_A, CARD_B], 0)
    _miss(qapp, screen)
    screen._cause_btns["confused"].click(); qapp.processEvents()
    screen._cause_note.setText("note"); screen._cause_note.editingFinished.emit()
    qapp.processEvents()

    state = load_states()["pauli_xyx"]
    assert state.lapses == 1                              # exactly one, not two
    assert state.interval_days == 1 and state.n == 0
    assert state.ef == pytest.approx(2.3)


def test_history_and_flag_files_keep_their_frozen_schemas(qapp, window, data_dir):
    """The new files are additive: nothing else on disk changes shape."""
    cards = window._cards
    assert cards.start_deck([CARD_A, CARD_B], 0)
    for btn in (cards._missed_btn, cards._got_btn):      # confidence left unset
        cards._reveal_btn.click(); qapp.processEvents()
        btn.click(); qapp.processEvents()
    qapp.processEvents()

    sessions = json.loads(storage.history_path().read_text())
    assert len(sessions) == 1
    assert set(sessions[0]) == {"total", "got_it", "unsure", "missed",
                                "timestamp", "results"}
    assert all(set(r) == {"card_id", "category", "rating", "elapsed_secs"}
               for r in sessions[0]["results"])
    # Three data files, each with the version sidecar common.schema stamps
    # beside it, plus the lock common.locking flocks for the duration of a
    # read-modify-write (empty, never read, and what stops a second app
    # clobbering rows we just appended).  No backups: every file here was
    # created by this session, so there was no earlier state to keep.
    assert sorted(p.name for p in data_dir.iterdir()) == [
        "flashcard_history.json", "flashcard_history.json.schema.json",
        "flashcard_schedule.json", "flashcard_schedule.json.schema.json",
        "mistakes.json", "mistakes.json.lock", "mistakes.json.schema.json"]
    assert (data_dir / "mistakes.json.lock").read_bytes() == b""

    # The sidecar is what makes the next format change survivable: it says what
    # the file is and which version wrote it, and it is invisible to every
    # reader (coach.py / dashboard.py open one exact file name).
    marker = json.loads((data_dir / "mistakes.json.schema.json").read_text())
    assert marker["file"] == "mistakes.json" and marker["kind"] == "mistakes"
    assert marker["schema"] == 1 and marker["written_by"].startswith("common/")


# ---------------------------------------------------------------------------
# Accessibility
# ---------------------------------------------------------------------------

def test_every_new_control_is_keyboard_reachable_and_named(qapp, screen):
    assert screen.start_deck([CARD_A, CARD_B], 0)
    new_buttons = (list(screen._confidence_btns.values())
                   + list(screen._cause_btns.values())
                   + [screen._confidence_off_btn, screen._cause_dismiss_btn])
    for btn in new_buttons:
        assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus, btn.text()
        assert btn.accessibleName(), btn.text()
    assert screen._cause_note.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert screen._cause_note.accessibleName()

    # Meaning is never colour-only: selected state carries a glyph.
    assert all(b.text()[0] in "○●" for b in new_buttons if b.isCheckable())

    # Focusing a new control and activating it hands focus back to the screen.
    screen._confidence_btns[2].setFocus(); qapp.processEvents()
    assert qapp.focusWidget() is screen._confidence_btns[2]
    QTest.keyClick(screen._confidence_btns[2], Qt.Key.Key_Space); qapp.processEvents()
    assert screen._confidence == 2
    assert qapp.focusWidget() is screen

    # "W" jumps into the cause row once it is up.
    _miss(qapp, screen)
    screen.setFocus(); qapp.processEvents()
    QTest.keyClick(screen, Qt.Key.Key_W); qapp.processEvents()
    assert qapp.focusWidget() in set(screen._cause_btns.values())


def test_the_drill_buttons_still_refuse_focus(qapp, screen):
    drill = (screen._end_btn, screen._reveal_btn, screen._got_btn,
             screen._unsure_btn, screen._missed_btn, screen._flag_btn)
    assert all(b.focusPolicy() == Qt.FocusPolicy.NoFocus for b in drill)
    assert screen.start_deck([CARD_A, CARD_B], 0)
    assert qapp.focusWidget() is screen
    QTest.keyClick(screen, Qt.Key.Key_Space); qapp.processEvents()
    assert screen.is_revealed and qapp.focusWidget() is screen


# ---------------------------------------------------------------------------
# Failure tolerance in the UI
# ---------------------------------------------------------------------------

def test_a_broken_journal_never_interrupts_the_drill(qapp, screen, monkeypatch):
    def boom(*a, **k):
        raise OSError("read-only data dir")
    monkeypatch.setattr(rs, "log_mistake", boom)
    monkeypatch.setattr(rs, "log_confidence", boom)
    monkeypatch.setattr(rs, "resolve_mistakes", boom)

    assert screen.start_deck([CARD_A, CARD_B], 0)
    screen._confidence_btns[3].click(); qapp.processEvents()
    _miss(qapp, screen)
    assert not screen.cause_row_visible                   # nothing to categorise
    screen._reveal_btn.click(); qapp.processEvents()
    screen._got_btn.click(); qapp.processEvents()
    assert (screen._stats.total, screen._stats.missed, screen._stats.got_it) == (2, 1, 1)


def test_mainwindow_builds_and_drills_with_no_api_key(qapp, window):
    from ui.main_window import PAGE_CARDS

    assert window._cards.start_deck([CARD_A, CARD_B], 0)
    window._stack.setCurrentIndex(PAGE_CARDS); qapp.processEvents()
    assert isinstance(window._cards._confidence_off_btn, QPushButton)
    assert window._setup._confidence_cb.isChecked() is True
