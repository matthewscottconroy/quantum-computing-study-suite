"""End-to-end headless drives of both session flows through MainWindow, using the
real ProblemWorker QThreads (problem 2 is exactly the path that used to segfault)."""
from __future__ import annotations

import pytest
from PyQt6.QtCore import QCoreApplication, QElapsedTimer, QEventLoop

import persistence
from core.models import ProblemCategory, TrainerConfig


def _wait_until(pred, timeout_ms: int = 90000, what: str = "condition") -> None:
    clock = QElapsedTimer()
    clock.start()
    while not pred():
        QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 50)
        if clock.elapsed() > timeout_ms:
            raise TimeoutError(f"timed out waiting for {what}")


@pytest.fixture
def window(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    yield win
    win._sprint.stop_timers()
    win._problem._tick_timer.stop()
    win.close()


def test_training_session_answer_flag_next_skip_summary_review(window, isolated_data_dir):
    from ui.main_window import PAGE_PROBLEM, PAGE_SETUP, PAGE_SUMMARY

    win = window
    win._setup.session_started.emit(TrainerConfig(
        categories=[ProblemCategory.SINGLE_GATE_OUTPUT, ProblemCategory.NOISE_CHANNEL],
        difficulty="beginner", problem_count=3))
    _wait_until(lambda: win._stack.currentIndex() == PAGE_PROBLEM
                and win._current_problem is not None, what="problem 1")
    p1 = win._current_problem
    assert win._problem._progress_lbl.text() == "Problem 1 of 3"
    assert win._problem._flag_btn.isHidden()
    assert not win._problem._next_btn.isEnabled()

    # Problem 1: click the keyed choice -> correct, result view shown.
    win._problem._choice_btns[int(p1.correct_answer)].click()
    assert win._session.stats.correct == 1
    assert not win._problem._flag_btn.isHidden()
    assert win._problem._next_btn.isEnabled()
    assert not win._problem._skip_btn.isEnabled()
    assert win._problem._choice_btns[int(p1.correct_answer)].objectName() == "choice_correct"

    # Flag toggle round-trips through trainer_flagged.json.
    win._problem._flag_btn.click()
    assert win._problem.is_flagged()
    assert [e["id"] for e in persistence.load_flagged()] == [persistence.flag_id_for(p1)]
    assert persistence.load_flagged()[0]["app"] == "circuit-trainer"
    win._problem._flag_btn.click()
    assert not win._problem.is_flagged() and persistence.load_flagged() == []

    # Next -> problem 2 is generated on a SECOND worker thread (old crash path).
    win._problem._next_btn.click()
    _wait_until(lambda: win._current_problem is not p1
                and win._stack.currentIndex() == PAGE_PROBLEM, what="problem 2")
    p2 = win._current_problem
    assert win._problem._progress_lbl.text() == "Problem 2 of 3"
    wrong = (int(p2.correct_answer) + 1) % len(p2.choices)
    win._problem._choice_btns[wrong].click()
    assert win._session.stats.wrong == 1
    assert win._problem._choice_btns[wrong].objectName() == "choice_wrong"

    # Problem 3 (third worker thread) is skipped -> summary, session saved.
    win._problem._next_btn.click()
    _wait_until(lambda: win._current_problem not in (p1, p2), what="problem 3")
    assert win._problem._progress_lbl.text() == "Problem 3 of 3"
    win._problem._skip_btn.click()
    assert win._stack.currentIndex() == PAGE_SUMMARY
    stats = win._session.stats
    assert (stats.total, stats.correct, stats.wrong, len(stats.attempts)) == (3, 1, 1, 2)
    raw = persistence._load_raw()
    assert len(raw) == 1 and raw[0]["total"] == 3 and raw[0]["correct"] == 1
    assert "sprint" not in raw[0]
    assert raw[0]["attempts"][0]["category"] == p1.category.value

    # Review mistakes re-serves the missed problem without a worker.
    win._summary.review_mistakes.emit()
    assert win._stack.currentIndex() == PAGE_PROBLEM and win._current_problem is p2
    win._problem._choice_btns[int(p2.correct_answer)].click()
    assert win._session.stats.correct == 1
    win._problem._next_btn.click()
    assert win._stack.currentIndex() == PAGE_SUMMARY

    win._summary.restart_requested.emit()
    assert win._stack.currentIndex() == PAGE_SETUP and win._session is None


def test_sprint_flow_answer_timeout_summary(window, isolated_data_dir):
    from ui.main_window import PAGE_SETUP, PAGE_SPRINT, PAGE_SPRINT_SUMMARY
    from ui.screens.setup_screen import SPRINT_CATEGORIES

    win = window
    win._setup.session_started.emit(TrainerConfig(
        categories=list(SPRINT_CATEGORIES), difficulty="beginner",
        problem_count=2, sprint=True))
    _wait_until(lambda: win._stack.currentIndex() == PAGE_SPRINT
                and win._current_problem is not None, what="sprint question 1")
    q1 = win._current_problem
    assert q1.category in SPRINT_CATEGORIES
    assert win._sprint._progress_lbl.text() == "Question 1 of 2"
    assert win._sprint._countdown.isActive()
    assert win._sprint._timer_lbl.text() == "1:00"

    # Question 1: correct click -> flash, countdown stopped, auto-advance.
    win._sprint._choice_btns[int(q1.correct_answer)].click()
    assert win._session.stats.correct == 1
    assert not win._sprint._countdown.isActive()
    assert win._sprint._flash_lbl.text() == "✓ Correct"
    _wait_until(lambda: win._current_problem is not q1
                and win._stack.currentIndex() == PAGE_SPRINT, what="sprint question 2")
    q2 = win._current_problem
    assert q2.category in SPRINT_CATEGORIES
    assert win._sprint._progress_lbl.text() == "Question 2 of 2"
    assert win._sprint._countdown.isActive()

    # Question 2: forced timeout counts as wrong, then the summary.
    win._sprint.timed_out.emit(60)
    last = win._session.stats.attempts[-1]
    assert last.feedback == "Time expired — counted as wrong."
    assert last.score == 0 and not last.is_correct and last.elapsed_secs == 60
    assert win._sprint._flash_lbl.text() == "⏱ Time's up!"
    _wait_until(lambda: win._stack.currentIndex() == PAGE_SPRINT_SUMMARY, what="sprint summary")
    stats = win._session.stats
    assert (stats.total, stats.correct) == (2, 1)

    raw = persistence._load_raw()
    assert len(raw) == 1 and raw[0].get("sprint") is True and raw[0]["total"] == 2
    assert {a["category"] for a in raw[0]["attempts"]} <= {c.value for c in SPRINT_CATEGORIES}

    win._sprint_summary.restart_requested.emit()
    assert win._stack.currentIndex() == PAGE_SETUP
    assert not win._sprint._countdown.isActive()
