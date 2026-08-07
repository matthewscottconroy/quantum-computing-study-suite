"""QThread worker for answer grading."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import Evaluation


class GradingWorker(QThread):
    graded = pyqtSignal(object)   # Evaluation
    failed = pyqtSignal(str)

    def __init__(self, paper_text: str, question: str, answer: str, parent=None) -> None:
        super().__init__(parent)
        self._paper    = paper_text
        self._question = question
        self._answer   = answer

    def run(self) -> None:
        try:
            from ai.grader import grade_answer
            evaluation = grade_answer(self._paper, self._question, self._answer)
            self.graded.emit(evaluation)
        except Exception as e:
            self.failed.emit(str(e))
