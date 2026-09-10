"""
MainWindow — owns the QStackedWidget and routes signals between screens.
"""

from __future__ import annotations
import os
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QFileDialog

from core.models import QuizConfig, Question, Evaluation
from core.session import MathSession
from workers.question_worker import QuestionWorker
from workers.evaluation_worker import EvaluationWorker
from ui.screens.setup_screen import SetupScreen
from ui.screens.question_screen import QuestionScreen
from ui.screens.feedback_screen import FeedbackScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.reference_screen import ReferenceScreen
from ui.widgets.loading_overlay import LoadingOverlay
from config import APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT

PAGE_SETUP    = 0
PAGE_QUESTION = 1
PAGE_FEEDBACK = 2
PAGE_SUMMARY  = 3
PAGE_HISTORY  = 4
PAGE_REFERENCE = 5


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1100, 760)

        self._session: MathSession | None = None
        self._current_question: Question | None = None
        self._pending_elapsed: int = 0
        self._q_worker: QuestionWorker | None = None
        self._ev_worker: EvaluationWorker | None = None

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup    = SetupScreen()
        self._question = QuestionScreen()
        self._feedback = FeedbackScreen()
        self._summary  = SummaryScreen()
        self._history  = HistoryScreen()
        self._reference = ReferenceScreen()

        self._stack.addWidget(self._setup)     # 0
        self._stack.addWidget(self._question)  # 1
        self._stack.addWidget(self._feedback)  # 2
        self._stack.addWidget(self._summary)   # 3
        self._stack.addWidget(self._history)   # 4
        self._stack.addWidget(self._reference) # 5

        self._overlay = LoadingOverlay(self)

        self._setup.quiz_started.connect(self._on_quiz_started)
        self._setup.history_requested.connect(self._on_history)
        self._setup.reference_requested.connect(self._on_reference)
        self._reference.back_requested.connect(self._on_reference_back)
        self._question.answer_submitted.connect(self._on_answer_submitted)
        self._question.skip_requested.connect(self._on_skip)
        self._feedback.next_question_requested.connect(self._on_next_question)
        self._feedback.flag_requested.connect(self._on_flag)
        self._summary.restart_requested.connect(self._on_restart)
        self._summary.review_mistakes.connect(self._on_review_mistakes)
        self._history.back_requested.connect(self._on_history_back)

        self._check_for_draft()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.resize(self.size())

    def _show_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)

    def _on_quiz_started(self, config: QuizConfig) -> None:
        self._session = MathSession(config)
        self._fetch_next_question()

    def _fetch_next_question(self) -> None:
        self._overlay.show_with_message(
            "Generating question",
            "Calling Claude…",
        )
        self._q_worker = QuestionWorker(self._session, self)
        self._q_worker.question_ready.connect(self._on_question_ready)
        self._q_worker.error.connect(self._on_generation_error)
        self._q_worker.start()

    def _on_question_ready(self, question: Question) -> None:
        self._current_question = question
        self._overlay.hide_overlay()
        self._question.load_question(
            question=question,
            number=self._session.question_number(),
            total=self._session.config.question_count,
        )
        self._show_page(PAGE_QUESTION)

    def _on_answer_submitted(self, answer: str, elapsed: int) -> None:
        if self._current_question is None:
            return
        self._pending_elapsed = elapsed
        self._overlay.show_with_message(
            "Evaluating answer",
            "Claude is grading your response…",
        )
        self._ev_worker = EvaluationWorker(self._current_question, answer, self)
        self._ev_worker.evaluation_ready.connect(
            lambda ev: self._on_evaluation_ready(answer, ev)
        )
        self._ev_worker.error.connect(self._on_evaluation_error)
        self._ev_worker.start()

    def _on_evaluation_ready(self, answer: str, evaluation: Evaluation) -> None:
        self._overlay.hide_overlay()
        self._session.record_answer(
            self._current_question, answer, evaluation,
            elapsed_seconds=self._pending_elapsed,
        )
        try:
            from persistence import save_draft
            save_draft(self._session.stats)
        except Exception:
            pass
        self._feedback.load_evaluation(evaluation)
        self._feedback.set_flagged(self._question_is_flagged(self._current_question))
        self._show_page(PAGE_FEEDBACK)

    # ── Flag for review ───────────────────────────────────────────────────────

    @staticmethod
    def _question_is_flagged(question: Question | None) -> bool:
        if question is None:
            return False
        try:
            from persistence import is_flagged
            return is_flagged(question)
        except Exception:
            return False

    def _on_flag(self) -> None:
        """Toggle the current question in math_flagged.json."""
        if self._current_question is None:
            return
        try:
            from persistence import toggle_flag
            new_state = toggle_flag(self._current_question)
        except Exception as exc:
            # Keep the last known state and tell the user why, rather than
            # silently looking as though the click did nothing.
            new_state = self._feedback.is_flagged()
            self.statusBar().showMessage(f"Could not update flag: {exc}", 5000)
        self._feedback.set_flagged(new_state)

    def _on_skip(self) -> None:
        self._session.record_skip()
        self._advance_or_finish()

    def _on_next_question(self) -> None:
        self._advance_or_finish()

    def _advance_or_finish(self) -> None:
        if self._session.is_complete():
            self._summary.load_stats(self._session.stats)
            self._show_page(PAGE_SUMMARY)
        else:
            self._fetch_next_question()

    def _on_restart(self) -> None:
        self._session = None
        self._current_question = None
        self._show_page(PAGE_SETUP)

    def _on_review_mistakes(self) -> None:
        """Requeue questions that scored below 7 as a new mini-session."""
        if self._session is None:
            return
        failed = [
            r.question for r in self._session.stats.history
            if r.evaluation.score < 7
        ]
        if not failed:
            return
        from core.models import QuizConfig
        from core.session import MathSession
        review_config = QuizConfig(
            subjects=self._session.config.subjects,
            difficulty=self._session.config.difficulty,
            question_types=self._session.config.question_types,
            question_count=len(failed),
        )
        new_session = MathSession(review_config)
        new_session._pending_questions = list(failed)
        self._session = new_session
        self._fetch_next_question()

    def _on_history(self) -> None:
        self._history.refresh()
        self._show_page(PAGE_HISTORY)

    def _on_history_back(self) -> None:
        self._show_page(PAGE_SETUP)

    def _on_reference(self) -> None:
        self._reference.load_all()
        self._show_page(PAGE_REFERENCE)

    def _on_reference_back(self) -> None:
        self._show_page(PAGE_SETUP)

    def _check_for_draft(self) -> None:
        try:
            from persistence import has_draft, clear_draft, _DRAFT_FILE
            if not has_draft():
                return
            reply = QMessageBox.question(
                self,
                "Unsaved session found",
                "A previous session was interrupted before it completed.\n"
                "Would you like to export it as JSON before starting fresh?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Discard,
            )
            if reply == QMessageBox.StandardButton.Yes:
                path, _ = QFileDialog.getSaveFileName(
                    self, "Export interrupted session",
                    "math-quiz-recovered.json", "JSON (*.json)"
                )
                if path:
                    import shutil
                    shutil.copy2(str(_DRAFT_FILE), path)
            clear_draft()
        except Exception:
            pass

    def _on_generation_error(self, message: str) -> None:
        self._overlay.hide_overlay()
        reply = QMessageBox.question(
            self,
            "Question generation failed",
            f"{message}\n\nRetry?",
            QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Retry:
            self._fetch_next_question()
        else:
            self._show_page(PAGE_SETUP)

    def _on_evaluation_error(self, message: str) -> None:
        self._overlay.hide_overlay()
        reply = QMessageBox.question(
            self,
            "Evaluation failed",
            f"{message}\n\nSkip this question and continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._session.record_skip()
            self._advance_or_finish()
