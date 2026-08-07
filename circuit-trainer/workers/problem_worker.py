"""QThread: generate the next problem from the session config."""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.session import TrainerSession
from core.models import Problem
from problems import generate


class ProblemWorker(QThread):
    problem_ready = pyqtSignal(object)   # Problem
    error = pyqtSignal(str)

    def __init__(self, session: TrainerSession, parent=None) -> None:
        super().__init__(parent)
        self._session = session

    def run(self) -> None:
        try:
            category = self._session.next_category()
            difficulty = self._session.next_difficulty()
            problem: Problem = generate(category, difficulty)
            self.problem_ready.emit(problem)
        except Exception as exc:
            self.error.emit(f"Problem generation failed: {exc}")
