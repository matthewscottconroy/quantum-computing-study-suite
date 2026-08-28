"""QThread worker for the optional Claude code review."""
from __future__ import annotations
from PyQt6.QtCore import QThread, pyqtSignal
from core.models import Kata


class ReviewWorker(QThread):
    reviewed = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, kata: Kata, user_code: str, parent=None) -> None:
        super().__init__(parent)
        self._kata = kata
        self._user_code = user_code

    def run(self) -> None:
        try:
            from grading.claude_review import review_code
            feedback = review_code(self._kata, self._user_code)
            self.reviewed.emit(feedback)
        except Exception as e:
            self.failed.emit(str(e))
