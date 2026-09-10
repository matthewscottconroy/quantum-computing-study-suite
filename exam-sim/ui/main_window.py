"""Main application window for exam-sim."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from config import (
    WINDOW_TITLE, WINDOW_MIN_SIZE,
    EXAM_QUESTION_COUNT, EXAM_MINUTES,
    SPRINT_QUESTION_COUNT, SPRINT_MINUTES,
)
from bank import build_exam_set, build_sprint_set
from persistence import save_result, record_misses
from ui.screens.home_screen import HomeScreen
from ui.screens.exam_screen import ExamScreen
from ui.screens.results_screen import ResultsScreen
from ui.screens.review_screen import ReviewScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.reference_screen import ReferenceScreen

PAGE_HOME      = 0
PAGE_EXAM      = 1
PAGE_RESULTS   = 2
PAGE_REVIEW    = 3
PAGE_HISTORY   = 4
PAGE_REFERENCE = 5


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(1120, 760)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._home    = HomeScreen()
        self._exam    = ExamScreen()
        self._results = ResultsScreen()
        self._review  = ReviewScreen()
        self._history   = HistoryScreen()
        self._reference = ReferenceScreen()
        for w in (self._home, self._exam, self._results, self._review,
                  self._history, self._reference):
            self._stack.addWidget(w)

        self._home.full_exam_requested.connect(self._on_full_exam)
        self._home.sprint_requested.connect(self._on_sprint)
        self._home.review_requested.connect(self._on_review)
        self._home.history_requested.connect(self._on_history)
        self._home.reference_requested.connect(self._on_reference)
        self._exam.session_finished.connect(self._on_exam_finished)
        self._results.home_requested.connect(self._go_home)
        self._review.home_requested.connect(self._go_home)
        self._history.back_requested.connect(self._go_home)
        self._reference.back_requested.connect(self._go_home)

    def _on_full_exam(self) -> None:
        questions = build_exam_set(EXAM_QUESTION_COUNT)
        if len(questions) < EXAM_QUESTION_COUNT:
            QMessageBox.warning(
                self, "Bank too small",
                f"Only {len(questions)} questions available in the bank.")
            if not questions:
                return
        self._exam.start_session(questions, EXAM_MINUTES, "full")
        self._stack.setCurrentIndex(PAGE_EXAM)

    def _on_sprint(self, section: str) -> None:
        questions = build_sprint_set(section, SPRINT_QUESTION_COUNT)
        if not questions:
            QMessageBox.warning(self, "No questions",
                                f"No questions found for section: {section}")
            return
        self._exam.start_session(questions, SPRINT_MINUTES, "sprint")
        self._stack.setCurrentIndex(PAGE_EXAM)

    def _on_exam_finished(self, result) -> None:
        try:
            save_result(result)
            record_misses(result)
        except Exception as exc:
            QMessageBox.warning(self, "Persistence",
                                f"Could not save session: {exc}")
        self._results.show_result(result)
        self._stack.setCurrentIndex(PAGE_RESULTS)

    def _on_review(self) -> None:
        if not self._review.start():
            QMessageBox.information(
                self, "Nothing to review",
                "No previously missed questions on file.")
            return
        self._stack.setCurrentIndex(PAGE_REVIEW)

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_reference(self) -> None:
        self._reference.load_all()
        self._stack.setCurrentIndex(PAGE_REFERENCE)

    def _go_home(self) -> None:
        self._home.refresh()
        self._stack.setCurrentIndex(PAGE_HOME)
