"""Headless drive of the confidence strip and the mistake-journal row."""
from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt

import persistence
from core.models import GradeMode, Problem

PAGE_PROBLEM, PAGE_RESULT = 1, 2


def _problem(pid: str = "qaoa_mixer_role") -> Problem:
    return Problem(
        id=pid, category="QAOA", difficulty="beginner",
        question="Which operator does QAOA apply first in each layer?",
        choices=["The cost operator U_C", "The mixer U_B", "A Hadamard", "A measurement"],
        correct_index=0, explanation="U_C then U_B.", grade_mode=GradeMode.MC,
    )


@pytest.fixture
def win(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import ui.main_window as mw

    monkeypatch.setattr(mw, "build_problem_set", lambda cfg: [_problem()])
    window = mw.MainWindow()
    try:
        yield window
    finally:
        window.close()


def _start(win) -> None:
    win._setup._start_btn.click()
    assert win._stack.currentIndex() == PAGE_PROBLEM


def _answer(win, letter: str) -> None:
    idx = "ABCD".index(letter)
    win._problem._radio_btns[idx].setChecked(True)
    win._problem._validate_mc()
    assert win._problem._submit_btn.isEnabled()
    win._problem._submit_btn.click()
    assert win._stack.currentIndex() == PAGE_RESULT


def test_wrong_answer_journals_a_mistake_and_a_cause(win, isolated_data_dir):
    _start(win)
    _answer(win, "B")                       # wrong: correct_index is 0

    rows = persistence.load_mistakes()
    assert len(rows) == 1
    entry = rows[0]
    assert set(entry) == {"id", "app", "category", "question", "your_answer",
                          "correct_answer", "cause", "note", "timestamp", "resolved"}
    assert entry["id"] == "qaoa_mixer_role"
    assert entry["app"] == "vqa-trainer"
    assert entry["category"] == "QAOA"
    assert entry["question"].startswith("Which operator does QAOA apply first")
    assert entry["your_answer"] == "B. The mixer U_B"
    assert entry["correct_answer"] == "A. The cost operator U_C"
    assert entry["cause"] is None and entry["note"] == ""
    assert entry["resolved"] is False
    assert isinstance(entry["timestamp"], float)
    assert all(len(entry[f]) <= 200 for f in
               ("question", "your_answer", "correct_answer", "note"))

    # the row is on screen, inline, and skippable
    assert win._result.journal_visible()
    row = win._result._mistake_row
    row._note.setText("U_C is the cost layer")
    row.button_for("knew_but_slipped").click()

    entry = persistence.load_mistakes()[0]
    assert entry["cause"] == "knew_but_slipped"
    assert entry["note"] == "U_C is the cost layer"


def test_skipping_the_cause_still_keeps_the_mistake(win):
    _start(win)
    _answer(win, "C")
    win._result._next_btn.click()           # straight past the row
    row = persistence.load_mistakes()[0]
    assert row["cause"] is None and row["resolved"] is False


def test_a_note_typed_but_never_committed_is_flushed_on_next(win):
    _start(win)
    _answer(win, "D")
    win._result._mistake_row._note.setText("little-endian again")
    win._result._next_btn.click()
    assert persistence.load_mistakes()[0]["note"] == "little-endian again"


def test_confidence_pairs_with_the_grade(win):
    _start(win)
    strip = win._problem._confidence
    assert strip.isVisibleTo(win._problem), "shown before the answer is submitted"
    assert strip.value() is None
    strip.button_for(4).click()
    assert strip.value() == 4
    _answer(win, "B")                       # confidently wrong

    rows = persistence.load_confidence()
    assert len(rows) == 1
    assert rows[0] == {
        "id": "qaoa_mixer_role", "app": "vqa-trainer", "category": "QAOA",
        "confidence": 4, "correct": False, "timestamp": rows[0]["timestamp"],
    }
    assert isinstance(rows[0]["timestamp"], float)
    assert persistence.confidence_breakdown() == {4: (0, 1)}


def test_skipping_the_confidence_strip_logs_nothing(win):
    _start(win)
    _answer(win, "A")
    assert persistence.load_confidence() == []


def test_correct_answer_resolves_an_earlier_mistake(win):
    _start(win)
    _answer(win, "B")
    assert persistence.load_mistakes()[0]["resolved"] is False
    assert win._result.journal_visible()

    win._result._next_btn.click()           # session of one -> summary
    win._summary.session_again.emit()
    _start(win)
    win._problem._confidence.button_for(3).click()
    _answer(win, "A")                       # now correct

    rows = persistence.load_mistakes()
    assert len(rows) == 1 and rows[0]["resolved"] is True
    assert not win._result.journal_visible(), "no journal row on a correct answer"
    assert persistence.load_confidence()[0] == {
        "id": "qaoa_mixer_role", "app": "vqa-trainer", "category": "QAOA",
        "confidence": 3, "correct": True,
        "timestamp": persistence.load_confidence()[0]["timestamp"],
    }


def test_opt_out_hides_the_strip_for_good(win, qapp, monkeypatch):
    _start(win)
    strip = win._problem._confidence
    strip.button_for(2).click()
    strip._opt_out_btn.click()
    assert strip.isHidden() and strip.value() is None
    assert persistence.confidence_prompt_enabled() is False
    _answer(win, "B")
    assert persistence.load_confidence() == [], "an opted-out user logs nothing"

    # and a brand-new window never asks again
    import ui.main_window as mw
    monkeypatch.setattr(mw, "build_problem_set", lambda cfg: [_problem()])
    second = mw.MainWindow()
    try:
        second._setup._start_btn.click()
        assert second._problem._confidence.isHidden()
        assert second._problem.confidence() is None
    finally:
        second.close()


def test_new_controls_are_keyboard_reachable_and_named(win):
    _start(win)
    strip = win._problem._confidence
    for level in (1, 2, 3, 4):
        btn = strip.button_for(level)
        assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert btn.accessibleName() and btn.accessibleDescription()
        assert str(level) in btn.text(), "the level is in the label, not just a colour"
        assert btn.objectName() == "chip"     # carries the :focus ring in theme.QSS
    assert strip._opt_out_btn.accessibleName()
    assert strip._opt_out_btn.focusPolicy() == Qt.FocusPolicy.StrongFocus

    _answer(win, "B")
    row = win._result._mistake_row
    for cause in persistence.MISTAKE_CAUSES:
        btn = row.button_for(cause)
        assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert btn.accessibleName() and btn.text()
        assert btn.objectName() == "chip"
    assert row._note.accessibleName() and row._note.objectName() == "note"
    assert row._note.focusPolicy() == Qt.FocusPolicy.StrongFocus

    # the verdict is spelled out and glyphed, never colour alone
    assert "Incorrect" in win._result._verdict_lbl.text()
    assert "✗" in win._result._verdict_lbl.text()
    assert win._result._verdict_lbl.accessibleName() == "Verdict: Incorrect"
    assert win._result._score_lbl.accessibleName() == "Score 0 out of 10"


def test_focus_ring_styles_exist_for_every_new_control():
    from ui import theme

    for rule in ("QPushButton#chip:focus", "QPushButton#chip:checked:focus",
                 "QPushButton#linkbtn:focus", "QLineEdit#note:focus"):
        assert rule in theme.QSS, rule


def test_a_persistence_failure_never_blocks_the_session(win, monkeypatch):
    def boom(*a, **k):
        raise OSError("disk full")

    import ui.main_window as mw
    monkeypatch.setattr(mw, "log_mistake", boom)
    monkeypatch.setattr(mw, "log_confidence", boom)
    monkeypatch.setattr(mw, "resolve_mistakes", boom)

    _start(win)
    win._problem._confidence.button_for(1).click()
    _answer(win, "B")                       # still reaches the result screen
    win._result._mistake_row.button_for("other").click()   # no journal row to update
    win._result._next_btn.click()
