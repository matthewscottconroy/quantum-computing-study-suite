"""Main application window for qec-trainer."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from core.models import GradeMode, SessionStats
from problems import build_problem_set
from ui.screens.setup_screen import SetupScreen
from ui.screens.problem_screen import ProblemScreen
from ui.screens.result_screen import ResultScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.reference_screen import ReferenceScreen
from persistence import save_session, toggle_flag, load_flagged
from workers.grading_worker import GradingWorker
from grading.auto_grader import grade_mc

PAGE_SETUP      = 0
PAGE_PROBLEM    = 1
PAGE_RESULT     = 2
PAGE_SUMMARY    = 3
PAGE_HISTORY    = 4
PAGE_REFERENCE  = 5


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(960, 700)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup     = SetupScreen()
        self._problem   = ProblemScreen()
        self._result    = ResultScreen()
        self._summary   = SummaryScreen()
        self._history   = HistoryScreen()
        self._reference = ReferenceScreen()

        for w in (self._setup, self._problem, self._result,
                  self._summary, self._history, self._reference):
            self._stack.addWidget(w)

        self._setup.session_started.connect(self._on_session_started)
        self._setup.history_requested.connect(self._on_history)
        self._setup.reference_requested.connect(self._on_reference)
        self._problem.answer_submitted.connect(self._on_answer_submitted)
        self._problem.session_ended.connect(self._finish_session)
        self._result.next_requested.connect(self._advance)
        self._result.flag_requested.connect(self._on_flag)
        self._summary.session_again.connect(self._go_setup)
        self._summary.back_requested.connect(self._go_setup)
        self._summary.review_mistakes.connect(self._on_review_mistakes)
        self._history.back_requested.connect(self._go_setup)
        self._reference.back_requested.connect(self._go_setup)

        self._problems: list = []
        self._idx: int = 0
        self._stats = SessionStats()
        self._streak: int = 0

    def _on_session_started(self, config) -> None:
        self._problems = build_problem_set(config)
        if not self._problems:
            QMessageBox.warning(self, "No Problems", "No problems match your selection.")
            return
        self._idx    = 0
        self._stats  = SessionStats()
        self._streak = 0
        self._show_current_problem()

    def _show_current_problem(self) -> None:
        if self._idx >= len(self._problems):
            self._finish_session()
            return
        p = self._problems[self._idx]
        self._problem.show_problem(p, self._idx + 1, len(self._problems), self._streak)
        self._stack.setCurrentIndex(PAGE_PROBLEM)

    def _on_answer_submitted(self, problem, answer: str, hints_used: int, elapsed_secs: int) -> None:
        if problem.grade_mode == GradeMode.AUTO and problem.choices:
            attempt = grade_mc(problem, answer)
            attempt.hints_used = hints_used
            attempt.elapsed_secs = elapsed_secs
            self._record_attempt(attempt)
        else:
            self._problem.show_grading()
            self._grade_worker = GradingWorker(problem, answer, hints_used, elapsed_secs, self)
            self._grade_worker.graded.connect(self._on_graded)
            self._grade_worker.failed.connect(self._on_grade_failed)
            self._grade_worker.start()

    def _on_graded(self, attempt) -> None:
        self._problem.hide_grading()
        self._record_attempt(attempt)

    def _on_grade_failed(self, err: str, answer: str, hints_used: int, elapsed_secs: int) -> None:
        self._problem.hide_grading()
        btn = QMessageBox.question(
            self, "Grading Failed",
            f"Could not grade answer:\n{err}\n\nSkip this problem and continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn == QMessageBox.StandardButton.Yes:
            problem = self._problems[self._idx]
            from core.models import Attempt, Verdict
            self._record_attempt(Attempt(
                problem=problem, answer=answer,
                score=0, verdict=Verdict.INCORRECT,
                feedback=f"Grading failed: {err}",
                hints_used=hints_used, elapsed_secs=elapsed_secs,
            ))

    def _record_attempt(self, attempt) -> None:
        self._stats.total += 1
        if attempt.score >= 7:
            self._stats.correct += 1
            self._streak += 1
        else:
            self._streak = 0
        self._stats.attempts.append(attempt)

        is_last = self._idx + 1 >= len(self._problems)
        self._result.show_attempt(attempt, is_last)

        # Update flag button state
        try:
            flagged = attempt.problem.id in load_flagged()
        except Exception:
            flagged = False
        self._result.set_flagged(flagged)

        self._stack.setCurrentIndex(PAGE_RESULT)

    def _on_flag(self) -> None:
        if not self._problems or self._idx >= len(self._problems):
            return
        problem_id = self._problems[self._idx].id
        try:
            new_state = toggle_flag(problem_id)
        except Exception:
            new_state = True
        self._result.set_flagged(new_state)

    def _advance(self) -> None:
        self._idx += 1
        if self._idx >= len(self._problems):
            self._finish_session()
        else:
            self._show_current_problem()

    def _finish_session(self) -> None:
        if self._stats.total > 0:
            save_session(self._stats)
        self._summary.show_stats(self._stats)
        self._stack.setCurrentIndex(PAGE_SUMMARY)

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_reference(self) -> None:
        self._reference.load_all()
        self._stack.setCurrentIndex(PAGE_REFERENCE)

    def _on_review_mistakes(self) -> None:
        mistakes = [a.problem for a in self._stats.attempts if a.score < 7]
        if not mistakes:
            return
        self._problems = mistakes
        self._idx = 0
        self._stats = SessionStats()
        self._streak = 0
        self._show_current_problem()

    def _go_setup(self) -> None:
        self._stack.setCurrentIndex(PAGE_SETUP)
