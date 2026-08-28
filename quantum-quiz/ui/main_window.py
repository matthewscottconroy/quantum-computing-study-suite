"""
MainWindow — owns the QStackedWidget and routes signals between screens.
Never calls Claude or Qiskit directly; all async work goes through workers.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import Qt

from core.models import QuizConfig, Question, Evaluation
from core.session import QuizSession
from qiskit_contexts import QiskitContext
from workers.question_worker import QuestionWorker
from workers.evaluation_worker import EvaluationWorker
from workers.viva_worker import VivaWorker
from ui.screens.setup_screen import SetupScreen
from ui.screens.question_screen import QuestionScreen
from ui.screens.feedback_screen import FeedbackScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.widgets.loading_overlay import LoadingOverlay
from config import APP_NAME, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT


PAGE_SETUP    = 0
PAGE_QUESTION = 1
PAGE_FEEDBACK = 2
PAGE_SUMMARY  = 3
PAGE_HISTORY  = 4


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(1100, 760)

        self._session: QuizSession | None = None
        self._current_question: Question | None = None
        self._pending_elapsed: int = 0
        self._q_worker: QuestionWorker | None = None
        self._ev_worker: EvaluationWorker | None = None
        self._viva_worker: VivaWorker | None = None

        # Viva mode state: (base_question, answer, evaluation) queued for a probe.
        # Cap is one follow-up per base question, and follow-ups never spawn
        # follow-ups — enforced by _current_is_followup below.
        self._viva_pending: tuple[Question, str, Evaluation] | None = None
        self._current_is_followup: bool = False

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup_screen   = SetupScreen()
        self._question_screen = QuestionScreen()
        self._feedback_screen = FeedbackScreen()
        self._summary_screen  = SummaryScreen()
        self._history_screen  = HistoryScreen()

        self._stack.addWidget(self._setup_screen)    # 0
        self._stack.addWidget(self._question_screen) # 1
        self._stack.addWidget(self._feedback_screen) # 2
        self._stack.addWidget(self._summary_screen)  # 3
        self._stack.addWidget(self._history_screen)  # 4

        self._overlay = LoadingOverlay(self)

        self._setup_screen.quiz_started.connect(self._on_quiz_started)
        self._setup_screen.history_requested.connect(self._on_history)
        self._question_screen.answer_submitted.connect(self._on_answer_submitted)
        self._question_screen.skip_requested.connect(self._on_skip)
        self._feedback_screen.next_question_requested.connect(self._on_next_question)
        self._summary_screen.restart_requested.connect(self._on_restart)
        self._summary_screen.review_mistakes.connect(self._on_review_mistakes)
        self._history_screen.back_requested.connect(self._on_history_back)

        self._check_for_draft()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._overlay.resize(self.size())

    def _show_page(self, index: int) -> None:
        self._stack.setCurrentIndex(index)

    # ── Quiz flow ─────────────────────────────────────────────────────────────

    def _on_quiz_started(self, config: QuizConfig) -> None:
        self._session = QuizSession(config)
        self._viva_pending = None
        self._current_is_followup = False
        self._fetch_next_question()

    def _fetch_next_question(self) -> None:
        self._overlay.show_with_message(
            "Generating question",
            "Building Qiskit context and calling Claude…",
        )
        self._q_worker = QuestionWorker(self._session, self)
        self._q_worker.question_ready.connect(self._on_question_ready)
        self._q_worker.error.connect(self._on_generation_error)
        self._q_worker.start()

    def _on_question_ready(self, question: Question, context: QiskitContext) -> None:
        self._current_question = question
        self._current_is_followup = False
        self._overlay.hide_overlay()
        self._question_screen.load_question(
            question=question,
            context=context,
            number=self._session.question_number(),
            total=self._session.config.question_count,
        )
        self._show_page(PAGE_QUESTION)

    def _on_answer_submitted(self, answer: str, elapsed: int) -> None:
        if self._current_question is None:
            return
        self._pending_elapsed = elapsed
        self._overlay.show_with_message("Evaluating answer", "Claude is grading your response…")
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
            is_followup=self._current_is_followup,
        )
        # Queue a viva probe: base questions only (follow-ups never spawn
        # follow-ups), and only when the answer had enough substance (score ≥ 4).
        if (
            self._session.config.viva_mode
            and not self._current_is_followup
            and evaluation.score >= 4
        ):
            self._viva_pending = (self._current_question, answer, evaluation)
        else:
            self._viva_pending = None
        try:
            from persistence import save_draft
            save_draft(self._session.stats)
        except Exception:
            pass
        self._feedback_screen.load_evaluation(evaluation)
        self._show_page(PAGE_FEEDBACK)

    def _on_skip(self) -> None:
        if self._current_is_followup:
            # Skipping a viva follow-up: it was an extra question, so it must
            # not consume a slot in the configured count.
            self._current_is_followup = False
            self._advance_or_finish()
            return
        self._viva_pending = None
        self._session.record_skip()
        self._advance_or_finish()

    def _on_next_question(self) -> None:
        if self._viva_pending is not None:
            self._fetch_viva_followup()
            return
        self._current_is_followup = False
        self._advance_or_finish()

    # ── Viva mode ─────────────────────────────────────────────────────────────

    def _fetch_viva_followup(self) -> None:
        base_question, answer, evaluation = self._viva_pending
        self._viva_pending = None
        self._overlay.show_with_message(
            "Generating follow-up",
            "Claude is probing your answer one level deeper…",
        )
        self._viva_worker = VivaWorker(
            self._session, base_question, answer, evaluation, self
        )
        self._viva_worker.question_ready.connect(self._on_viva_ready)
        self._viva_worker.error.connect(self._on_viva_error)
        self._viva_worker.start()

    def _on_viva_ready(self, question: Question, context: QiskitContext) -> None:
        self._current_question = question
        self._current_is_followup = True
        self._overlay.hide_overlay()
        self._question_screen.load_question(
            question=question,
            context=context,
            # The follow-up belongs to the base question just answered.
            number=max(1, self._session.question_number() - 1),
            total=self._session.config.question_count,
            is_followup=True,
        )
        self._show_page(PAGE_QUESTION)

    def _on_viva_error(self, message: str) -> None:
        # Follow-ups are a bonus — on failure, continue the session normally.
        self._overlay.hide_overlay()
        self._current_is_followup = False
        self._advance_or_finish()

    def _advance_or_finish(self) -> None:
        if self._session.is_complete():
            self._summary_screen.load_stats(self._session.stats)
            self._show_page(PAGE_SUMMARY)
        else:
            self._fetch_next_question()

    def _on_restart(self) -> None:
        self._session = None
        self._current_question = None
        self._viva_pending = None
        self._current_is_followup = False
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
        from core.session import QuizSession
        review_config = QuizConfig(
            subjects=self._session.config.subjects,
            difficulty=self._session.config.difficulty,
            question_types=self._session.config.question_types,
            question_count=len(failed),
        )
        new_session = QuizSession(review_config)
        new_session._pending_questions = list(failed)
        self._session = new_session
        self._viva_pending = None
        self._current_is_followup = False
        self._fetch_next_question()

    # ── History ───────────────────────────────────────────────────────────────

    def _on_history(self) -> None:
        self._history_screen.refresh()
        self._show_page(PAGE_HISTORY)

    def _on_history_back(self) -> None:
        self._show_page(PAGE_SETUP)

    # ── Draft recovery ────────────────────────────────────────────────────────

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
                    "quantum-quiz-recovered.json", "JSON (*.json)"
                )
                if path:
                    import shutil
                    shutil.copy2(str(_DRAFT_FILE), path)
            clear_draft()
        except Exception:
            pass

    # ── Error handling ────────────────────────────────────────────────────────

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
            if self._current_is_followup:
                # Follow-ups are extras — dropping one must not consume a slot.
                self._current_is_followup = False
            else:
                self._session.record_skip()
            self._advance_or_finish()
