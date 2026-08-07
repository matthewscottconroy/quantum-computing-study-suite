"""QThread: grade a FREE_FORM answer asynchronously via Claude."""

from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal

from core.models import Problem, Attempt
from grading.claude_grader import grade_free_form, GradingError


class EvaluationWorker(QThread):
    evaluation_ready = pyqtSignal(object)   # Attempt
    error = pyqtSignal(str)

    def __init__(self, problem: Problem, answer: str, parent=None) -> None:
        super().__init__(parent)
        self._problem = problem
        self._answer = answer

    def run(self) -> None:
        try:
            attempt = grade_free_form(self._problem, self._answer)
            self.evaluation_ready.emit(attempt)
        except GradingError as exc:
            self.error.emit(str(exc))
        except Exception as exc:
            self.error.emit(f"Unexpected evaluation error: {exc}")
