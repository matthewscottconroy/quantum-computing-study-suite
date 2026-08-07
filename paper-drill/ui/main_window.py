"""Main application window for paper-drill."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from core.models import SessionStats, QuestionAttempt
from ui.screens.paper_input_screen import PaperInputScreen
from ui.screens.question_screen import QuestionScreen
from ui.screens.feedback_screen import FeedbackScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.library_screen import LibraryScreen
from ui.widgets.loading_overlay import LoadingOverlay
from persistence import save_session
from workers.generation_worker import GenerationWorker
from workers.grading_worker import GradingWorker

PAGE_INPUT    = 0
PAGE_QUESTION = 1
PAGE_FEEDBACK = 2
PAGE_SUMMARY  = 3
PAGE_HISTORY  = 4
PAGE_LIBRARY  = 5


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(1000, 720)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._input    = PaperInputScreen()
        self._question = QuestionScreen()
        self._feedback = FeedbackScreen()
        self._summary  = SummaryScreen()
        self._history  = HistoryScreen()
        self._library  = LibraryScreen()
        self._overlay  = LoadingOverlay(self)

        for w in (self._input, self._question, self._feedback, self._summary,
                  self._history, self._library):
            self._stack.addWidget(w)

        self._input.drill_requested.connect(self._on_drill_requested)
        self._input.history_requested.connect(self._on_history)
        self._input.library_requested.connect(self._on_library)
        self._question.answer_submitted.connect(self._on_answer_submitted)
        self._question.session_cancelled.connect(self._go_input)
        self._feedback.next_requested.connect(self._go_next_question)
        self._feedback.done_requested.connect(self._on_done)
        self._summary.drill_again.connect(self._drill_again)
        self._summary.back_requested.connect(self._go_input)
        self._history.back_requested.connect(self._go_input)
        self._library.back_requested.connect(self._go_input)
        self._library.drill_requested.connect(self._on_drill_requested)

        self._config = None
        self._questions = []
        self._attempts: list[QuestionAttempt] = []
        self._current_attempt: QuestionAttempt | None = None
        self._stats = SessionStats()

    def _on_drill_requested(self, config) -> None:
        self._config = config
        self._attempts = []
        self._overlay.show_with_message("Generating questions from paper…")
        self._gen_worker = GenerationWorker(config, self)
        self._gen_worker.questions_ready.connect(self._on_questions_ready)
        self._gen_worker.failed.connect(self._on_gen_failed)
        self._gen_worker.start()

    def _on_questions_ready(self, questions) -> None:
        self._overlay.hide()
        self._questions = questions
        self._stats = SessionStats(title=self._config.paper_title)
        self._question.start(questions, self._config.paper_text)
        self._stack.setCurrentIndex(PAGE_QUESTION)

    def _on_gen_failed(self, err: str) -> None:
        self._overlay.hide()
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Generation Failed", f"Could not generate questions:\n{err}")

    def _on_answer_submitted(self, attempt: QuestionAttempt) -> None:
        self._current_attempt = attempt
        self._question.show_grading()
        self._grade_worker = GradingWorker(
            self._config.paper_text,
            attempt.question.text,
            attempt.answer_text,
            self,
        )
        self._grade_worker.graded.connect(self._on_graded)
        self._grade_worker.failed.connect(self._on_grade_failed)
        self._grade_worker.start()

    def _on_graded(self, evaluation) -> None:
        self._question.hide_grading()
        self._current_attempt.evaluation = evaluation
        self._attempts.append(self._current_attempt)
        self._stats.total += 1
        self._stats.scores.append(evaluation.score)

        is_last = len(self._attempts) >= len(self._questions)
        self._feedback.show_attempt(self._current_attempt, is_last)
        self._stack.setCurrentIndex(PAGE_FEEDBACK)

    def _on_grade_failed(self, err: str) -> None:
        self._question.hide_grading()
        from PyQt6.QtWidgets import QMessageBox
        from core.models import Evaluation, Verdict
        btn = QMessageBox.question(
            self, "Grading Failed",
            f"Could not grade answer:\n{err}\n\nSkip this question and continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn == QMessageBox.StandardButton.Yes:
            self._current_attempt.evaluation = Evaluation(
                score=0, verdict=Verdict.INCORRECT,
                feedback=f"Grading failed: {err}", model_answer="",
            )
            self._attempts.append(self._current_attempt)
            self._stats.total += 1
            self._stats.scores.append(0)
            is_last = len(self._attempts) >= len(self._questions)
            self._feedback.show_attempt(self._current_attempt, is_last)
            self._stack.setCurrentIndex(PAGE_FEEDBACK)

    def _go_next_question(self) -> None:
        self._question.show_current()
        self._stack.setCurrentIndex(PAGE_QUESTION)

    def _on_done(self) -> None:
        save_session(self._stats)
        self._summary.show_stats(self._stats)
        self._stack.setCurrentIndex(PAGE_SUMMARY)

    def _drill_again(self) -> None:
        if self._config:
            self._on_drill_requested(self._config)

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_library(self) -> None:
        self._library.refresh()
        self._stack.setCurrentIndex(PAGE_LIBRARY)

    def _go_input(self) -> None:
        self._stack.setCurrentIndex(PAGE_INPUT)

    def resizeEvent(self, event) -> None:
        self._overlay.resize(self.size())
        super().resizeEvent(event)
