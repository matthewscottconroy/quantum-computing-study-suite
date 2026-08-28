"""QThread worker for grading one problem part with Claude."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import Problem, Part


class PartGradingWorker(QThread):
    graded = pyqtSignal(str, object)     # part_id, GradeResult
    failed = pyqtSignal(str, str)        # part_id, error message

    def __init__(self, problem: Problem, part: Part, answer: str,
                 tries: int = 1, parent=None) -> None:
        super().__init__(parent)
        self._problem = problem
        self._part    = part
        self._answer  = answer
        self._tries   = tries

    def run(self) -> None:
        try:
            from ai.grader import grade_part
            result = grade_part(self._problem, self._part, self._answer, self._tries)
            self.graded.emit(self._part.part_id, result)
        except Exception as e:
            self.failed.emit(self._part.part_id, str(e))
