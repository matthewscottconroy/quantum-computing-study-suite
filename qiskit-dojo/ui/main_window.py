"""Main application window for qiskit-dojo."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from core.models import SessionStats
from katas import build_kata_set
from ui.screens.setup_screen import SetupScreen
from ui.screens.kata_screen import KataScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from persistence import save_session

PAGE_SETUP   = 0
PAGE_KATA    = 1
PAGE_SUMMARY = 2
PAGE_HISTORY = 3


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(1180, 760)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup   = SetupScreen()
        self._kata    = KataScreen()
        self._summary = SummaryScreen()
        self._history = HistoryScreen()

        for w in (self._setup, self._kata, self._summary, self._history):
            self._stack.addWidget(w)

        self._setup.session_started.connect(self._on_session_started)
        self._setup.history_requested.connect(self._on_history)
        self._kata.kata_completed.connect(self._on_kata_completed)
        self._kata.session_ended.connect(self._finish_session)
        self._summary.session_again.connect(self._go_setup)
        self._summary.back_requested.connect(self._go_setup)
        self._history.back_requested.connect(self._go_setup)

        self._katas: list = []
        self._idx: int = 0
        self._stats = SessionStats()

    def _on_session_started(self, config) -> None:
        self._katas = build_kata_set(config)
        if not self._katas:
            QMessageBox.warning(self, "No Katas", "No katas match your selection.")
            return
        self._idx = 0
        self._stats = SessionStats()
        self._show_current()

    def _show_current(self) -> None:
        if self._idx >= len(self._katas):
            self._finish_session()
            return
        k = self._katas[self._idx]
        self._kata.show_kata(k, self._idx + 1, len(self._katas))
        self._stack.setCurrentIndex(PAGE_KATA)

    def _on_kata_completed(self, attempt) -> None:
        self._stats.attempts.append(attempt)
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

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _go_setup(self) -> None:
        self._stack.setCurrentIndex(PAGE_SETUP)
