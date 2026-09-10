"""Main application window for problem-trainer."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from core.models import (
    SessionStats, AttemptRecord, problem_score, derivation_score,
)
from ui.screens.setup_screen import SetupScreen, MODE_PROBLEMS
from ui.screens.problem_screen import ProblemScreen
from ui.screens.derivation_screen import DerivationScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.reference_screen import ReferenceScreen
from persistence import save_session
import persistence
from workers.grading_worker import PartGradingWorker
from workers.step_worker import StepCheckWorker

PAGE_SETUP      = 0
PAGE_PROBLEM    = 1
PAGE_DERIVATION = 2
PAGE_SUMMARY    = 3
PAGE_HISTORY    = 4
PAGE_REFERENCE  = 5

DERIVATION_CATEGORY = "derivation"      # flag-entry category for guided derivations


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(1020, 760)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup      = SetupScreen()
        self._problem    = ProblemScreen()
        self._derivation = DerivationScreen()
        self._summary    = SummaryScreen()
        self._history    = HistoryScreen()
        self._reference  = ReferenceScreen()
        for w in (self._setup, self._problem, self._derivation,
                  self._summary, self._history, self._reference):
            self._stack.addWidget(w)

        self._setup.session_started.connect(self._on_session_started)
        self._setup.history_requested.connect(self._on_history)
        self._setup.reference_requested.connect(lambda: self._open_reference())
        self._problem.part_submitted.connect(self._on_part_submitted)
        self._problem.problem_finished.connect(self._on_problem_finished)
        self._problem.session_ended.connect(self._finish_session)
        self._problem.flag_requested.connect(self._on_flag)
        self._problem.reference_requested.connect(self._open_reference_for_topic)
        self._derivation.step_submitted.connect(self._on_step_submitted)
        self._derivation.derivation_finished.connect(self._on_derivation_finished)
        self._derivation.session_ended.connect(self._finish_session)
        self._derivation.flag_requested.connect(self._on_flag)
        self._derivation.reference_requested.connect(self._open_reference_for_derivation)
        self._summary.session_again.connect(self._go_setup)
        self._summary.back_requested.connect(self._go_setup)
        self._history.back_requested.connect(self._go_setup)
        self._reference.back_requested.connect(self._close_reference)

        self._mode: str = MODE_PROBLEMS
        self._items: list = []
        self._idx: int = 0
        self._stats = SessionStats()
        self._workers: list = []
        self._reference_return: int = PAGE_SETUP

    # -- session flow ---------------------------------------------------

    def _on_session_started(self, mode: str, items: list) -> None:
        if not items:
            QMessageBox.warning(self, "No Items", "Nothing matches your selection.")
            return
        self._mode = mode
        self._items = items
        self._idx = 0
        self._stats = SessionStats()
        self._show_current()

    def _show_current(self) -> None:
        if self._idx >= len(self._items):
            self._finish_session()
            return
        item = self._items[self._idx]
        flagged = self._is_flagged(item.id)
        if self._mode == MODE_PROBLEMS:
            self._problem.show_problem(item, self._idx + 1, len(self._items))
            self._problem.set_flagged(flagged)
            self._stack.setCurrentIndex(PAGE_PROBLEM)
        else:
            self._derivation.show_derivation(item, self._idx + 1, len(self._items))
            self._derivation.set_flagged(flagged)
            self._stack.setCurrentIndex(PAGE_DERIVATION)

    def _advance(self) -> None:
        self._idx += 1
        self._show_current()

    def _finish_session(self) -> None:
        if self._stats.total > 0:
            try:
                save_session(self._stats)
            except Exception:
                pass
            self._summary.show_stats(self._stats)
            self._stack.setCurrentIndex(PAGE_SUMMARY)
        else:
            self._go_setup()

    # -- mode 1: problem parts ------------------------------------------

    def _on_part_submitted(self, problem, part, answer: str, tries: int) -> None:
        worker = PartGradingWorker(problem, part, answer, tries, self)
        worker.graded.connect(self._problem.on_part_graded)
        worker.failed.connect(self._problem.on_part_failed)
        worker.finished.connect(lambda w=worker: self._reap(w))
        self._workers.append(worker)
        worker.start()

    def _on_problem_finished(self, problem, states: list) -> None:
        score = problem_score(states)
        self._stats.attempts.append(AttemptRecord(
            problem_id=problem.id, kind="problem", score=score, title=problem.title,
            category=problem.topic))
        self._advance()

    # -- mode 2: derivation steps ---------------------------------------

    def _on_step_submitted(self, derivation, step, answer: str,
                           accepted_steps: list, tries: int) -> None:
        worker = StepCheckWorker(derivation, step, answer, accepted_steps, tries, self)
        worker.checked.connect(self._derivation.on_step_checked)
        worker.failed.connect(self._derivation.on_step_failed)
        worker.finished.connect(lambda w=worker: self._reap(w))
        self._workers.append(worker)
        worker.start()

    def _on_derivation_finished(self, derivation, states: list) -> None:
        score = derivation_score(states)
        self._stats.attempts.append(AttemptRecord(
            problem_id=derivation.id, kind="derivation", score=score,
            title=derivation.title, category=DERIVATION_CATEGORY))
        self._advance()

    # -- flag for review ------------------------------------------------

    @staticmethod
    def _is_flagged(item_id: str) -> bool:
        try:
            return persistence.is_flagged(item_id)
        except Exception:
            return False

    def _current_item(self):
        if 0 <= self._idx < len(self._items):
            return self._items[self._idx]
        return None

    def _on_flag(self) -> None:
        """Toggle the review flag on the problem/derivation currently shown."""
        item = self._current_item()
        if item is None:
            return
        is_problem = self._mode == MODE_PROBLEMS
        category = item.topic if is_problem else DERIVATION_CATEGORY
        try:
            new_state = persistence.toggle_flag(item.id, item.title, category)
        except Exception:
            new_state = self._is_flagged(item.id)
        screen = self._problem if is_problem else self._derivation
        screen.set_flagged(new_state)

    # -- reference (in-app docs) ----------------------------------------

    def _open_reference(self, chapter_selector=None) -> None:
        """Show the docs browser; Back returns to whichever page was open.

        Without a ``chapter_selector`` (the Setup button) the browser is reset
        to every chapter with no title filter, so a jump made earlier from a
        problem or derivation does not linger.
        """
        current = self._stack.currentIndex()
        if current != PAGE_REFERENCE:
            self._reference_return = current
        if chapter_selector is None:
            self._reference.show_all()
        else:
            chapter_selector()
        self._stack.setCurrentIndex(PAGE_REFERENCE)

    def _open_reference_for_topic(self, topic: str) -> None:
        self._open_reference(lambda: self._reference.select_topic(topic))

    def _open_reference_for_derivation(self, derivation_id: str) -> None:
        self._open_reference(lambda: self._reference.select_derivation(derivation_id))

    def _close_reference(self) -> None:
        target = self._reference_return
        if target in (PAGE_REFERENCE, PAGE_SETUP) or target >= self._stack.count():
            self._go_setup()
        else:
            self._stack.setCurrentIndex(target)

    # -- misc -----------------------------------------------------------

    def _reap(self, worker) -> None:
        try:
            self._workers.remove(worker)
        except ValueError:
            pass
        worker.deleteLater()

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _go_setup(self) -> None:
        self._setup.refresh_flag_filter()
        self._stack.setCurrentIndex(PAGE_SETUP)
