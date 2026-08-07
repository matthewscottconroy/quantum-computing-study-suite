"""QThread worker for Claude grading of open-ended QEC questions."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import Problem, Attempt


class GradingWorker(QThread):
    graded = pyqtSignal(object)   # Attempt
    failed = pyqtSignal(str, str, int, int)  # err, answer, hints_used, elapsed_secs

    def __init__(self, problem: Problem, answer: str, hints_used: int = 0,
                 elapsed_secs: int = 0, parent=None) -> None:
        super().__init__(parent)
        self._problem      = problem
        self._answer       = answer
        self._hints_used   = hints_used
        self._elapsed_secs = elapsed_secs

    def run(self) -> None:
        try:
            from grading.claude_grader import grade_open
            attempt = grade_open(self._problem, self._answer)
            attempt.hints_used   = self._hints_used
            attempt.elapsed_secs = self._elapsed_secs
            self.graded.emit(attempt)
        except Exception as e:
            self.failed.emit(str(e), self._answer, self._hints_used, self._elapsed_secs)
