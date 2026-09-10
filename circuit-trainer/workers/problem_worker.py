"""QThread: generate the next problem from the session config."""

from __future__ import annotations

# qiskit's native extension (qiskit._accelerate) must be initialised on the
# MAIN thread.  problems/__init__.py imports the generator modules lazily, so
# without this line qiskit would be first-imported inside the first
# ProblemWorker thread; once that short-lived thread exits, the next
# QuantumCircuit() built on a fresh worker thread segfaults
# (Python 3.14 + qiskit 2.5, reproduced with QThread and threading.Thread).
# Importing at module level here runs on whichever thread imports the worker
# -- always the GUI thread (ui.main_window imports it) -- so every later
# worker is safe.  Do not move this into ProblemWorker.run().
import qiskit  # noqa: F401

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
