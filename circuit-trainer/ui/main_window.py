"""MainWindow — owns all screens, routes signals, keeps the session alive."""

from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from core.models import TrainerConfig, Problem, Attempt, AnswerFormat
from core.session import TrainerSession
from grading.auto_grader import grade
from workers.problem_worker import ProblemWorker
from workers.evaluation_worker import EvaluationWorker
from ui.screens.setup_screen import SetupScreen
from ui.screens.problem_screen import ProblemScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.widgets.loading_overlay import LoadingOverlay
from config import APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT

PAGE_SETUP   = 0
PAGE_PROBLEM = 1
PAGE_SUMMARY = 2
PAGE_HISTORY = 3


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1200, 800)

        self._session: TrainerSession | None = None
        self._current_problem: Problem | None = None
        self._problem_worker: ProblemWorker | None = None
        self._eval_worker: EvaluationWorker | None = None
        self._pending_elapsed_secs: int = 0
        self._review_queue: list[Problem] = []

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup   = SetupScreen()
        self._problem = ProblemScreen()
        self._summary = SummaryScreen()
        self._history = HistoryScreen()

        self._stack.addWidget(self._setup)    # 0
        self._stack.addWidget(self._problem)  # 1
        self._stack.addWidget(self._summary)  # 2
        self._stack.addWidget(self._history)  # 3

        self._overlay = LoadingOverlay(self)

        self._setup.session_started.connect(self._on_session_started)
        self._setup.history_requested.connect(self._on_history)
        self._problem.answer_submitted.connect(self._on_mc_answer)
        self._problem.free_form_submitted.connect(self._on_free_form_submitted)
        self._problem.next_requested.connect(self._on_next)
        self._problem.skip_requested.connect(self._on_skip)
        self._summary.restart_requested.connect(self._on_restart)
        self._summary.review_mistakes.connect(self._on_review_mistakes)
        self._history.back_requested.connect(self._on_history_back)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.resize(self.size())

    # ── Flow ──────────────────────────────────────────────────────────────────

    def _on_session_started(self, config: TrainerConfig) -> None:
        self._session = TrainerSession(config)
        self._review_queue = []
        self._fetch_next()

    def _fetch_next(self) -> None:
        self._overlay.show_message("Generating problem…")
        self._problem_worker = ProblemWorker(self._session, self)
        self._problem_worker.problem_ready.connect(self._on_problem_ready)
        self._problem_worker.error.connect(self._on_gen_error)
        self._problem_worker.start()

    def _on_problem_ready(self, problem: Problem) -> None:
        self._current_problem = problem
        self._overlay.hide_overlay()
        self._problem.load_problem(
            problem,
            number=self._session.problem_number(),
            total=self._session.config.problem_count,
        )
        self._stack.setCurrentIndex(PAGE_PROBLEM)

    # ── Answer handling ───────────────────────────────────────────────────────

    def _on_mc_answer(self, choice_idx: int, elapsed_secs: int) -> None:
        if self._current_problem is None:
            return
        attempt = grade(self._current_problem, str(choice_idx))
        attempt.elapsed_secs = elapsed_secs
        self._session.record(attempt)
        self._problem.show_result(attempt)

    def _on_free_form_submitted(self, answer: str, elapsed_secs: int) -> None:
        if self._current_problem is None:
            return
        self._pending_elapsed_secs = elapsed_secs
        self._overlay.show_message("Grading with Claude…")
        self._eval_worker = EvaluationWorker(self._current_problem, answer, self)
        self._eval_worker.evaluation_ready.connect(self._on_eval_ready)
        self._eval_worker.error.connect(self._on_eval_error)
        self._eval_worker.start()

    def _on_eval_ready(self, attempt: Attempt) -> None:
        self._overlay.hide_overlay()
        attempt.elapsed_secs = self._pending_elapsed_secs
        self._pending_elapsed_secs = 0
        self._session.record(attempt)
        self._problem.show_result(attempt)

    def _on_eval_error(self, msg: str) -> None:
        self._overlay.hide_overlay()
        reply = QMessageBox.question(
            self, "Grading failed",
            f"{msg}\n\nSkip this problem and continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._session.record_skip()
            self._advance()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _on_skip(self) -> None:
        self._session.record_skip()
        self._advance()

    def _on_next(self) -> None:
        self._advance()

    def _advance(self) -> None:
        if self._session.is_complete():
            self._summary.load_stats(self._session.stats)
            self._stack.setCurrentIndex(PAGE_SUMMARY)
        elif self._review_queue:
            self._serve_review_problem()
        else:
            self._fetch_next()

    def _on_review_mistakes(self) -> None:
        """Requeue problems answered incorrectly and start a review session."""
        if self._session is None:
            return
        wrong_problems = [
            a.problem for a in self._session.stats.attempts if not a.is_correct
        ]
        if not wrong_problems:
            return
        # Build a minimal config that mirrors the current session settings.
        review_config = TrainerConfig(
            categories=self._session.config.categories,
            difficulty=self._session.config.difficulty,
            problem_count=len(wrong_problems),
        )
        self._session = TrainerSession(review_config)
        # Directly enqueue the wrong problems without generating new ones.
        self._session._category_queue = [p.category for p in wrong_problems]
        self._review_queue = list(wrong_problems)
        self._serve_review_problem()

    def _serve_review_problem(self) -> None:
        if not self._review_queue:
            self._summary.load_stats(self._session.stats)
            self._stack.setCurrentIndex(PAGE_SUMMARY)
            return
        problem = self._review_queue.pop(0)
        self._current_problem = problem
        self._problem.load_problem(
            problem,
            number=self._session.problem_number(),
            total=self._session.config.problem_count,
        )
        self._stack.setCurrentIndex(PAGE_PROBLEM)

    def _on_restart(self) -> None:
        self._session = None
        self._current_problem = None
        self._review_queue = []
        self._stack.setCurrentIndex(PAGE_SETUP)

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_history_back(self) -> None:
        self._stack.setCurrentIndex(PAGE_SETUP)

    def _on_gen_error(self, msg: str) -> None:
        self._overlay.hide_overlay()
        reply = QMessageBox.question(
            self, "Problem generation failed",
            f"{msg}\n\nRetry?",
            QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Retry:
            self._fetch_next()
        else:
            self._stack.setCurrentIndex(PAGE_SETUP)
