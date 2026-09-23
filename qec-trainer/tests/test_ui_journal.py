"""Headless drives of the new UI: confidence strip and mistake journal.

Every assertion goes through the real widgets (no shortcuts into persistence)
so the wiring itself is under test, against a temp data dir.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QPushButton

import persistence
from core.models import GradeMode, Problem


@pytest.fixture
def win(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    w = MainWindow()
    try:
        yield w
    finally:
        w.close()


def _mc(pid: str = "rep_distance") -> Problem:
    return Problem(
        id=pid, category="Repetition Code", difficulty="beginner",
        question="What is the distance of the 3-qubit repetition code?",
        choices=["1", "2", "3", "4"], correct_index=2,
        explanation="It corrects one bit flip, so d = 3.",
        grade_mode=GradeMode.AUTO)


def _start(win, problem):
    win._problems = [problem]
    win._idx = 0
    from core.models import SessionStats
    win._stats = SessionStats()
    win._streak = 0
    win._show_current_problem()


def _answer(win, letter: str, confidence: int | None = None):
    screen = win._problem
    idx = "ABCD".index(letter)
    screen._radio_btns[idx].setChecked(True)
    screen._validate_mc()
    if confidence is not None:
        screen._confidence.set_rating(confidence)
    screen._on_submit()


# ── 1-4: wrong answer → journal → cause → confidence → resolve ────────────────

def test_wrong_answer_logs_a_mistake_with_a_cause_then_resolves(win, isolated_data_dir):
    p = _mc()
    _start(win, p)

    # (3) confidence strip is visible and usable BEFORE the answer is submitted
    strip = win._problem._confidence
    assert strip.isVisibleTo(win._problem)
    assert strip.rating() is None
    _answer(win, "B", confidence=4)          # wrong, and "certain" — the danger zone

    # the result screen is showing and the mistake row appeared
    from ui.main_window import PAGE_RESULT
    assert win._stack.currentIndex() == PAGE_RESULT
    assert win._result._mistake_card.isVisibleTo(win._result)
    assert "✗" in win._result._verdict_lbl.text()       # glyph, not colour alone

    # (2) entry schema field-for-field, in the temp data dir
    raw = json.loads((isolated_data_dir / "mistakes.json").read_text())
    assert len(raw) == 1
    row = raw[0]
    assert row == {
        "id": "rep_distance",
        "app": "qec-trainer",
        "category": "Repetition Code",
        "question": "What is the distance of the 3-qubit repetition code?",
        "your_answer": "B",
        "correct_answer": "C. 3",
        "cause": None,
        "note": "",
        "timestamp": row["timestamp"],
        "resolved": False,
    }
    assert isinstance(row["timestamp"], float) and row["timestamp"] > 0

    # (1) choose a cause through the widget
    win._result.mistake_row.choose("knew_but_slipped")
    win._result.mistake_row.set_note("read the question twice")
    stored = persistence.load_mistakes()[0]
    assert stored["cause"] == "knew_but_slipped"
    assert stored["note"] == "read the question twice"
    assert stored["resolved"] is False

    # (3) the confidence pairing row
    conf = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert conf == [{
        "id": "rep_distance", "app": "qec-trainer", "category": "Repetition Code",
        "confidence": 4, "correct": False, "timestamp": conf[0]["timestamp"],
    }]
    assert persistence.calibration_summary() == {4: {"total": 1, "correct": 0}}

    # (4) re-answer correctly -> resolved True, mistake row gone
    _start(win, p)
    _answer(win, "C", confidence=3)
    assert not win._result._mistake_card.isVisibleTo(win._result)
    assert "✓" in win._result._verdict_lbl.text()
    rows = persistence.load_mistakes()
    assert len(rows) == 1 and rows[0]["resolved"] is True
    assert rows[0]["cause"] == "knew_but_slipped"       # the analysis survives
    assert persistence.open_mistakes() == []
    assert persistence.calibration_summary() == {3: {"total": 1, "correct": 1},
                                                 4: {"total": 1, "correct": 0}}


def test_skipping_both_prompts_still_logs_the_mistake_and_nothing_else(win, isolated_data_dir):
    _start(win, _mc())
    _answer(win, "A")                       # no confidence, no cause
    rows = persistence.load_mistakes()
    assert len(rows) == 1 and rows[0]["cause"] is None and rows[0]["your_answer"] == "A"
    assert persistence.load_confidence() == []
    assert not (isolated_data_dir / "confidence.json").exists()


def test_a_correct_answer_logs_no_mistake(win):
    _start(win, _mc())
    _answer(win, "C", confidence=2)
    assert persistence.load_mistakes() == []
    assert persistence.load_confidence()[0]["correct"] is True


def test_confidence_is_not_carried_over_between_problems(win):
    _start(win, _mc("a"))
    _answer(win, "C", confidence=4)
    _start(win, _mc("b"))
    assert win._problem._confidence.rating() is None
    _answer(win, "C")
    assert [r["id"] for r in persistence.load_confidence()] == ["a"]


def test_the_strip_locks_once_the_answer_is_in(win):
    _start(win, _mc())
    strip = win._problem._confidence
    _answer(win, "A", confidence=1)
    assert all(not b.isEnabled() for b in strip._buttons.values())
    win._problem.show_problem(_mc("b"), 1, 1)
    assert all(b.isEnabled() for b in strip._buttons.values())


# ── Opt-out ───────────────────────────────────────────────────────────────────

def test_opt_out_hides_the_strip_and_is_remembered(win, isolated_data_dir):
    _start(win, _mc())
    strip = win._problem._confidence
    strip._optout_btn.click()
    assert strip.isHidden()
    assert persistence.confidence_prompt_enabled() is False

    _start(win, _mc("b"))                    # a fresh problem must not re-ask
    assert strip.isHidden()
    _answer(win, "A")
    assert persistence.load_confidence() == []

    persistence.set_confidence_prompt_enabled(True)
    _start(win, _mc("c"))
    assert strip.isVisibleTo(win._problem)


# ── Accessibility of the new controls ─────────────────────────────────────────

def _new_buttons(widget):
    return [b for b in widget.findChildren(QPushButton) if b.objectName() == "pill"]


def test_new_controls_are_keyboard_reachable_and_named(win):
    _start(win, _mc())
    _answer(win, "A", confidence=1)
    pills = _new_buttons(win._problem._confidence) + _new_buttons(win._result.mistake_row)
    assert len(pills) == 4 + len(persistence.MISTAKE_CAUSES)
    for b in pills:
        assert b.focusPolicy() in (Qt.FocusPolicy.StrongFocus, Qt.FocusPolicy.WheelFocus)
        assert b.accessibleName(), b.text()
        assert b.isCheckable()
    note = win._result.mistake_row._note_edit
    assert note.accessibleName() and note.focusPolicy() != Qt.FocusPolicy.NoFocus
    optout = win._problem._confidence._optout_btn
    assert optout.accessibleName() and optout.focusPolicy() != Qt.FocusPolicy.NoFocus


def test_state_is_never_colour_alone(win):
    _start(win, _mc())
    _answer(win, "A", confidence=2)
    strip = win._problem._confidence
    assert strip._buttons[2].text().startswith("✓")
    assert not strip._buttons[3].text().startswith("✓")
    assert "Unsure" in strip._status_lbl.text()

    row = win._result.mistake_row
    assert row._status_lbl.text() == "Logged — uncategorised"
    row.choose("misread")
    assert row._buttons["misread"].text().startswith("✓")
    assert "Misread" in row._status_lbl.text()


def test_the_theme_gives_every_new_control_a_focus_ring():
    from ui import theme
    for rule in ("QPushButton#pill:focus", "QPushButton:focus",
                 "QPushButton#flat:focus", "QLineEdit:focus"):
        assert rule in theme.QSS, rule


# ── Decoder game ──────────────────────────────────────────────────────────────

def _force_round(screen, level: str):
    from core.decoder_game import generate_round
    import random

    screen._plan = [level]
    screen._round_idx = 0
    screen._score = screen._streak = screen._best_streak = 0
    screen._results = []
    screen._pages.setCurrentIndex(0)
    screen._show_round()
    assert screen._round is not None
    return screen._round


def test_decoder_round_journals_a_failure_with_code_and_round_type(win, isolated_data_dir):
    from core.decoder_game import pauli_label, pauli_xor

    dec = win._decoder
    r = _force_round(dec, "rep3")
    dec._confidence.set_rating(4)
    # deliberately pick a wrong choice
    wrong = next(i for i in range(len(r.choices)) if i != r.correct_index)
    dec._radio_btns[wrong].setChecked(True)
    dec._on_submit()

    assert dec._mistake_row.isVisibleTo(dec)
    rows = persistence.load_mistakes()
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == "decoder_rep3"                 # code + round type
    assert row["app"] == "qec-trainer"
    assert row["category"] == "Decoder Game"
    assert "3-qubit" in row["question"].lower() or "repetition" in row["question"].lower()
    assert row["your_answer"] == pauli_label(r.choices[wrong][1], r.code.n)
    assert row["correct_answer"] == pauli_label(r.error, r.code.n)
    assert row["cause"] is None and row["resolved"] is False

    dec._mistake_row.choose("out_of_time")
    assert persistence.load_mistakes()[0]["cause"] == "out_of_time"
    assert persistence.load_confidence()[0] == {
        "id": "decoder_rep3", "app": "qec-trainer", "category": "Decoder Game",
        "confidence": 4, "correct": False,
        "timestamp": persistence.load_confidence()[0]["timestamp"]}

    # decode the next round correctly -> the open entry resolves
    r2 = _force_round(dec, "rep3")
    dec._radio_btns[r2.correct_index].setChecked(True)
    dec._on_submit()
    assert not dec._mistake_row.isVisibleTo(dec)
    assert persistence.load_mistakes()[0]["resolved"] is True


def test_decoder_grid_round_journals_and_keeps_history_schema(win, isolated_data_dir):
    dec = win._decoder
    r = _force_round(dec, "surface1")
    # place a correction that is off by a logical operator -> guaranteed failure
    from core.decoder_game import pauli_xor
    bad = pauli_xor(r.error, r.code.logical_x)
    dec._surface_grid._states = [
        (1 if (bad[0] >> q & 1) else 0) + (2 if (bad[1] >> q & 1) else 0)
        for q in range(9)]
    dec._on_submit()
    assert dec._mistake_row.isVisibleTo(dec)
    assert persistence.load_mistakes()[0]["id"] == "decoder_surface1"

    dec._finish()
    sessions = json.loads((isolated_data_dir / "qec_history.json").read_text())
    assert sessions[0]["attempts"][0]["problem_id"] == "decoder_surface1"
    assert set(sessions[0]["attempts"][0]) == {
        "problem_id", "category", "difficulty", "score", "verdict",
        "hints_used", "elapsed_secs"}


def test_surface_check_squares_pair_colour_with_a_sign(win):
    dec = win._decoder
    grid = dec._surface_grid
    grid.load_syndrome((1, 0, 0, 0, 0, 0, 0, 0))
    assert grid._check_lbls[0].text() == "X−"
    assert "fired" in grid._check_lbls[0].accessibleName()
    assert grid._check_lbls[1].text() == "X+"
    assert "quiet" in grid._check_lbls[1].accessibleName()
    for q, btn in enumerate(grid._qubit_btns):
        assert btn.accessibleName() == f"Data qubit {q + 1} — no correction"
    grid._on_qubit_clicked(0)
    assert grid._qubit_btns[0].accessibleName().endswith("X correction")


def test_main_window_still_constructs_with_no_api_key(win):
    assert win.centralWidget() is not None
    assert win.windowTitle()
